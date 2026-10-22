"""Opt-in public service probes; never enable an application capability automatically.

Small historical fixture at 30N/31E, UTC, spanning leap day. No credentials.
Responses are kept in ignored test scratch, with a compact reproducible report.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/.output/climate-enrichment-live"


def probe(case):
    model, variable, hourly = case
    query = dict(latitude=30., longitude=31., start_date="2024-02-28", end_date="2024-03-01",
                 models=model, timezone="UTC", daily=variable)
    if hourly:
        query["hourly"] = hourly
    url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode(query)
    result = dict(model=model, daily_variable=variable, hourly_variable=hourly, url=url,
                  retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                  acceptance="single public sample only; not production adapter acceptance")
    try:
        with urlopen(Request(url, headers={"User-Agent": "MIRSAD-source-capability-audit/1"}), timeout=20) as response:
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise ValueError("Probe response exceeds 1 MB")
            payload = json.loads(data)
            result.update(http_status=response.status, response_sha256=hashlib.sha256(data).hexdigest())
        filename = model + "-" + variable + ".json"
        (OUTPUT / filename).write_bytes(data)
        values = payload.get("daily", {}).get(variable, [])
        dates = payload.get("daily", {}).get("time", [])
        finite = lambda v: isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v)
        result.update(response_file=filename, dates=dates, values=values,
                      units=payload.get("daily_units", {}).get(variable),
                      usable=dates == ["2024-02-28", "2024-02-29", "2024-03-01"]
                      and len(values) == 3 and all(finite(v) for v in values))
        if hourly:
            grouped = {}
            for stamp, value in zip(payload.get("hourly", {}).get("time", []), payload.get("hourly", {}).get(hourly, [])):
                if finite(value):
                    grouped.setdefault(stamp[:10], {})[stamp] = value
            operation = max if variable.endswith("_max") else min
            result["hourly_valid_counts"] = {d: len(grouped.get(d, {})) for d in dates}
            result["recomputed_daily"] = [operation(grouped[d].values()) if len(grouped.get(d, {})) == 24 else None for d in dates]
            result["matches_hourly_within_0_11"] = result["usable"] and all(
                finite(w) and abs(v - w) <= .11 for v, w in zip(values, result["recomputed_daily"]))
    except Exception as error:
        result.update(usable=False, error=str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Make four small public archive requests")
    args = parser.parse_args()
    if not args.live:
        parser.error("Live network access requires --live")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cases = [("era5_land", "relative_humidity_2m_max", "relative_humidity_2m"),
             ("era5_land", "relative_humidity_2m_min", "relative_humidity_2m"),
             ("era5", "sunshine_duration", None),
             ("era5", "vapour_pressure_deficit_max", "vapour_pressure_deficit")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(probe, cases))
    result = dict(point=dict(latitude=30., longitude=31.), timezone="UTC",
                  start="2024-02-28", end="2024-03-01", results=rows)
    (OUTPUT / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps(row, ensure_ascii=True))
    return 0 if all(row["usable"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
