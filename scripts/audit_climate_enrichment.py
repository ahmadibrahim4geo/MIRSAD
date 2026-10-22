"""Capture/check the pre-enrichment contracts without ArcGIS or network access.

The reference is a regression baseline, not independent scientific validation.
Capture is explicit, refuses replacement, and requires unchanged runtime sources.
"""
import argparse
import copy
import datetime as dt
import hashlib
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "MIRSAD Desktop"
REFERENCE = ROOT / "tests/fixtures/climate_enrichment_baseline.json"
REPORTS = DESKTOP / "docs/reports/climate-enrichment"
sys.path[:0] = [str(ROOT), str(DESKTOP / "src")]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def load_toolbox():
    path = ROOT / "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt"
    loader = importlib.machinery.SourceFileLoader("mirsad_enrichment_reference", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def monthly_fixture():
    base = dict(T2M=20., T2M_MAX=27., T2M_MIN=13., PRECTOTCORR=30., TS=28.,
                RH2M=60., T2MDEW=12., PS=100., SLP=101.3, WS10M=3., WD10M=350.,
                ALLSKY_SFC_SW_DWN=15., ALLSKY_SFC_UV_INDEX=5., CLOUD_AMT=40.)
    return {p: {(y, m): v + (y - 2023) + m / 10.
                for y in (2023, 2024) for m in range(1, 13)} for p, v in base.items()}


def point_fixture():
    return dict(station_key="USER:baseline", usaf="000001", wban="", name="Baseline / مرجع",
                country="USER", source_country="", latitude=30., longitude=31., elevation=None,
                qa_status="user_supplied", point_type="User point", input_source="Deterministic fixture")


def desktop_fixture(missing=False):
    start, end = dt.date(2023, 1, 1), dt.date(2024, 12, 31)
    monthly = monthly_fixture()
    raw = {p: {start + dt.timedelta(days=i): values[((start + dt.timedelta(days=i)).year,
                                                  (start + dt.timedelta(days=i)).month)]
               for i in range((end - start).days + 1)} for p, values in monthly.items()}
    if missing:
        raw["PRECTOTCORR"].pop(dt.date(2024, 2, 29))
        raw["RH2M"].pop(dt.date(2024, 7, 1))
    return [dict(station=point_fixture(), series=raw, status="OK", error="",
                 source_summary="NASA POWER", provenance={})], start, end


def current_contracts():
    from mirsad_desktop import science, climate
    from mirsad_desktop.registry import MODULES, module_fields
    from mirsad_desktop.exports import element_sheets
    from mirsad_desktop.climate_products import PRODUCTS, REGIONAL
    from mirsad_desktop.tools import TOOLS, fresh_draft
    core = load_toolbox()
    calculations = {}
    for label in ("complete", "missing_months"):
        monthly = monthly_fixture()
        if label == "missing_months":
            monthly["PRECTOTCORR"].pop((2024, 2))
            monthly["RH2M"].pop((2023, 7))
        calculations[label] = {}
        for module in MODULES:
            opts = dict(precip_totals=True, gap_method="none", lat=30., monthly_ranges=True)
            legacy = module_fields(module.name, core.compute_point_fields(
                copy.deepcopy(monthly), [2023, 2024], [module.name], "Daily", **opts))
            desktop = module_fields(module.name, science.compute_point_fields(
                copy.deepcopy(monthly), [2023, 2024], [module.name], "Daily", **opts))
            if legacy != desktop:
                raise AssertionError("Scientific host mismatch: " + module.name + "/" + label)
            calculations[label][module.name] = dict(fields=list(legacy), values=legacy)
    outputs = {}
    for missing in (False, True):
        records, start, end = desktop_fixture(missing)
        layers, daily = climate.prepare_outputs(records, [m.name for m in MODULES], start, end,
                                               "NASA POWER", monthly_ranges=True)
        case = {}
        for name, values in layers.items():
            sheets = element_sheets(values, "NASA POWER", {"catalogue_version": "fixture"},
                                    "fixed-regression-run", daily[name])
            case[name] = dict(properties=list(values[0]["properties"]), values=values[0]["properties"],
                              daily_header=daily[name][0], daily_rows=len(daily[name][1]),
                              daily_sha256=hashlib.sha256(canonical(list(daily[name][1]))).hexdigest(),
                              sheets=[dict(name=n, headers=h, rows=len(r)) for n, h, r in sheets])
        outputs["missing_days" if missing else "complete"] = case
    return dict(calculations=calculations, desktop_outputs=outputs,
                module_fields={m.name: core.MODULE_FIELDS[m.name] for m in MODULES},
                module_folders={m.name: core.MODULE_FOLDER[m.name] for m in MODULES},
                desktop_files={m.name: m.name + ".xlsx" for m in MODULES},
                module_dependencies={m.name: list(m.params) for m in MODULES},
                drafts={tool.key: {k: v for k, v in fresh_draft(tool).items()
                                  if k in ("provider", "daily", "yearly", "ranges", "scopes", "units", "modules")}
                        for tool in TOOLS},
                product_capabilities=PRODUCTS, regional_products=list(REGIONAL))


def capture():
    if REFERENCE.exists():
        raise SystemExit("Refusing to replace the accepted baseline. Review changes explicitly.")
    runtime = ["Toolboxes", "mirsad_core", "MIRSAD Desktop/src"]
    changes = subprocess.check_output(["git", "diff", "HEAD", "--name-only", "--", *runtime], cwd=ROOT,
                                      encoding="utf-8").splitlines()
    changes = [p for p in changes if not p.endswith(".xml")]
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "--", *runtime],
                                        cwd=ROOT, encoding="utf-8").splitlines()
    changes += [p for p in untracked if not p.endswith(".xml")]
    if changes:
        raise SystemExit("Runtime differs from HEAD; cannot capture a pre-change baseline: " + str(changes))
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, encoding="ascii").strip()
    contracts = current_contracts()
    result = dict(source_revision=revision, scope="Deterministic regression baseline; not native/live acceptance",
                  contracts_sha256=hashlib.sha256(canonical(contracts)).hexdigest(), contracts=contracts)
    REFERENCE.parent.mkdir(parents=True, exist_ok=True)
    with REFERENCE.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print("Captured baseline:", revision, result["contracts_sha256"])


def check():
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    expected = reference["contracts"]
    assert hashlib.sha256(canonical(expected)).hexdigest() == reference["contracts_sha256"], "Reference digest changed"
    actual = current_contracts()
    changed = [key for key in expected if actual.get(key) != expected[key]]
    if changed:
        raise AssertionError("Pre-enrichment contract changed: " + ", ".join(changed))
    print("Climate baseline passed: 19 modules; complete/missing months and leap-day missingness;")
    print("legacy/Desktop calculation values, field order, Daily records, sheet layouts and legacy paths unchanged.")


def capabilities():
    """Inventory implemented adapters separately from external service candidates."""
    from mirsad_core import hybrid_pipeline as h, climate_products as products
    from mirsad_desktop.registry import MODULES
    targets = [
        ("Tmax", "T2M_MAX", "Temperature", "deg_C"),
        ("Tmin", "T2M_MIN", "Temperature", "deg_C"),
        ("Tmean", "T2M", "Temperature", "deg_C"),
        ("Trange", None, "Temperature", "deg_C difference"),
        ("RHmax", "RH2M_MAX", "Relative Humidity", "percent"),
        ("RHmin", "RH2M_MIN", "Relative Humidity", "percent"),
        ("RHmean", "RH2M", "Relative Humidity", "percent"),
        ("Tdew", "T2MDEW", "Dew Point", "deg_C"),
        ("ea", None, "Relative Humidity", "kPa"),
        ("es", None, "Relative Humidity", "kPa"),
        ("VPD_Source", "VPD_SOURCE", "Relative Humidity", "kPa; daily operation must be explicit"),
        ("VPD_FAO56", None, "Relative Humidity", "kPa"),
        ("Rs", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "MJ/m2/day kernel input"),
        ("Rn_Source", "RN_SOURCE", "Solar Radiation", "MJ/m2/day; surface definition required"),
        ("Rn_FAO56", None, "Solar Radiation", "MJ/m2/day reference surface"),
        ("n", "SUNSHINE_DURATION", "Solar Radiation", "hours/day"),
        ("Ra", None, "Solar Radiation", "MJ/m2/day"),
        ("U2", None, "Wind", "m/s at 2m"),
        ("P", "PS", "Surface Pressure", "kPa kernel input"),
        ("DOY", None, "Site metadata", "day number"),
        ("X", None, "Site metadata", "output CRS unit"),
        ("Y", None, "Site metadata", "output CRS unit"),
        ("Z_Elev_m", None, "Site metadata", "m; original station elevation is separate"),
        ("ET0_HG", None, "Evapotranspiration", "legacy period totals retained"),
        ("ET0_PM", None, "Evapotranspiration", "mm/day then declared period aggregation"),
    ]
    power_variables = sorted({p for m in MODULES for p in m.params})
    providers = [
        dict(provider="NOAA GSOD", product="GSOD", variables=sorted({v[0] for v in h.NOAA_FIELDS.values()}),
             temporal="Daily summaries", region="Matching USAF/WBAN/location only", start="Station/file-specific",
             end="Latest available station/year file", modes=["station"], auth=None),
        dict(provider="Open-Meteo", product="ERA5 / ERA5-Land", variables=sorted(set(h.OM_DAILY) | set(h.OM_HOURLY)),
             temporal="Daily or complete hourly-to-daily UTC", region="Model/cell-specific; Land has land constraints",
             start="ERA5 1940; ERA5-Land 1950; per-variable suitability", end="Latest published archive dates",
             modes=["point", "station"], auth=None),
        dict(provider="NASA POWER", product="POWER meteorology / radiation", variables=power_variables,
             temporal="Daily point; separate monthly regional protocol", region="Product/variable-specific grid",
             start="Variable-specific; not inferred from API family", end="Latest published variable dates",
             modes=["point", "station", "regional_monthly"], auth=None),
    ]
    providers += [dict(provider=name, product=spec["id"], variables=spec["variables"], temporal=spec["temporal"],
                       region=spec["region"], start=spec["start"], end=spec["end"], auth=spec["auth"],
                       modes=(["station"] if name == products.GHCN else ["point", "station"]) +
                             (["regional_native"] if name in products.REGIONAL else []))
                  for name, spec in sorted(products.PRODUCTS.items())]
    rows = []
    for logical, raw_key, module, unit in targets:
        for provider in providers:
            available = bool(raw_key and raw_key in provider["variables"])
            for mode in ("point", "station", "regional_native", "regional_monthly"):
                adapter = available and mode in provider["modes"]
                rows.append(dict(variable=logical, raw_key=raw_key, module=module, unit=unit,
                                 provider=provider["provider"], product=provider["product"], temporal=provider["temporal"],
                                 region=provider["region"], start=provider["start"], end=provider["end"], output_mode=mode,
                                 adapter_available=adapter,
                                 status="implemented protocol; baseline/static inventory" if adapter else
                                        "derived/site contract pending" if raw_key is None else "not implemented in this adapter/mode",
                                 live_acceptance="not established by this static matrix", auth=provider["auth"]))
    result = dict(source_revision=json.loads(REFERENCE.read_text(encoding="utf-8"))["source_revision"],
                  scope="Pre-enrichment implementation inventory; service capability does not imply adapter support",
                  notes=["No new raw keys above are enabled merely by being listed here.",
                         "HG exists through legacy calculations; no separate daily HG/PM product interface yet.",
                         "Ra exists inside legacy HG calculations; a standalone daily Ra export is pending.",
                         "X/Y are represented by geometry/Point_Lon/Point_Lat; explicit output-CRS attribute contract is pending.",
                         "NOAA WDSP is mapped to WS10M, which does not prove measurement height.",
                         "Native monthly/composite inputs must never create daily observations.",
                         "CDS/IMERG authentication acceptance is pending, as recorded in the existing backlog."],
                  rows=rows)
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / "CAPABILITY_MATRIX.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", len(rows), "variable/provider/product/temporal/region/period/mode contracts to", path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", action="store_true", help="Capture once before changing runtime source")
    parser.add_argument("--capabilities", action="store_true", help="Generate the implemented capability inventory")
    args = parser.parse_args()
    if args.capture and args.capabilities:
        parser.error("Capture and capability generation are separate operations")
    if args.capture:
        capture()
    elif args.capabilities:
        capabilities()
    else:
        check()
