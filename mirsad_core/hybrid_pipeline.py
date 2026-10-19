# -*- coding: utf-8 -*-
"""Source-wide Hybrid download barriers, shared by ArcMap, Pro and Desktop.

Python 2.7/3 compatible. All adapters return daily canonical values, never
statistically imputed values. Monthly Gap Fill belongs after this pipeline.
"""
from __future__ import unicode_literals
import calendar
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import tempfile
import time
from .climate_sources import reanalysis_plan,variable_resolution

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, HTTPError

POLICY = "hybrid-source-barriers-v1"
SOURCES = ("NOAA GSOD", "Open-Meteo", "NASA POWER")
OM_DAILY = {"T2M":"temperature_2m_mean", "T2M_MAX":"temperature_2m_max",
            "T2M_MIN":"temperature_2m_min", "PRECTOTCORR":"precipitation_sum",
            "ALLSKY_SFC_SW_DWN":"shortwave_radiation_sum"}
OM_HOURLY = {"RH2M":"relative_humidity_2m", "T2MDEW":"dew_point_2m", "PS":"surface_pressure",
             "SLP":"pressure_msl", "WS10M":"wind_speed_10m", "WD10M":"wind_direction_10m",
             "CLOUD_AMT":"cloud_cover"}
NOAA_FIELDS = {"TEMP":("T2M",9999.9,lambda v:(v-32)*5/9),
               "MAX":("T2M_MAX",9999.9,lambda v:(v-32)*5/9),
               "MIN":("T2M_MIN",9999.9,lambda v:(v-32)*5/9),
               "DEWP":("T2MDEW",9999.9,lambda v:(v-32)*5/9),
               "SLP":("SLP",9999.9,lambda v:v/10), "STP":("PS",9999.9,lambda v:v/10),
               "WDSP":("WS10M",999.9,lambda v:v*0.5144444444444445),
               "PRCP":("PRECTOTCORR",99.99,lambda v:v*25.4)}
FILLABLE = ("T2M", "T2M_MAX", "T2M_MIN", "RH2M", "T2MDEW", "ALLSKY_SFC_SW_DWN",
            "ALLSKY_SFC_UV_INDEX", "CLOUD_AMT", "SLP", "PS", "WS10M", "TS")


class Cancelled(Exception):
    pass


def valid(value):
    try:
        v = float(value)
        return not math.isnan(v) and not math.isinf(v) and v > -900
    except (TypeError, ValueError):
        return False


def date(value):
    return dt.datetime.strptime(str(value), "%Y-%m-%d").date()


def days(start, end):
    current = start
    while current <= end:
        yield current.isoformat()
        current += dt.timedelta(days=1)


def atomic_json(path, data):
    """Commit a checkpoint only when its entire response has been persisted."""
    handle, temporary = tempfile.mkstemp(prefix=".pending-", dir=os.path.dirname(path))
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        if hasattr(os, "replace"):
            os.replace(temporary, path)
        elif os.name == "nt":  # Python 2.7 on Windows
            import ctypes
            if not ctypes.windll.kernel32.MoveFileExW(type(u"")(temporary), type(u"")(path), 9):
                raise OSError("Could not commit Hybrid checkpoint")
        else:
            os.rename(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def observation_id(station):
    usaf, wban = str(station.get("usaf", "")), str(station.get("wban", ""))
    return usaf+wban if len(usaf)==6 and usaf.isdigit() and len(wban)==5 and wban.isdigit() else None


def parse_noaa(text, station, start, end, required):
    identifier = observation_id(station)
    # Python 2's csv module requires bytes; station names are retained in raw CSV.
    import sys
    stream = io.BytesIO(text.encode("utf-8")) if sys.version_info[0] == 2 else io.StringIO(text)
    result, seen, rejected = {}, set(), 0
    for row in csv.DictReader(stream):
        if row.get("STATION", "").strip() != identifier:
            raise ValueError("NOAA station identifier mismatch")
        day = date(row["DATE"])
        if not start <= day <= end:
            continue
        if day in seen:
            raise ValueError("Duplicate NOAA station/day")
        seen.add(day)
        lat, lon = float(row["LATITUDE"]), float(row["LONGITUDE"])
        if (math.isnan(lat+lon) or math.isinf(lat+lon) or
                abs(lat-station["latitude"]) > .05 or abs(lon-station["longitude"]) > .05):
            rejected += 1
            continue
        for source, (target, sentinel, convert) in NOAA_FIELDS.items():
            if target not in required:
                continue
            count = row.get(source+"_ATTRIBUTES")
            if source in ("TEMP", "DEWP", "SLP", "STP", "WDSP") and count is not None:
                try:
                    if int(count.strip()) <= 0:
                        continue
                except ValueError:
                    continue
            try:
                value = float(row.get(source, ""))
            except (TypeError, ValueError):
                continue
            if not valid(value) or value == sentinel:
                continue
            if source == "PRCP" and (value < 0 or row.get("PRCP_ATTRIBUTES", "").strip() not in ("D", "F", "G")):
                continue
            result.setdefault(target, {})[day.isoformat()] = convert(value)
    return result, rejected


def _read(url, session, cancelled):
    """Bound responses and retries; a 404 is a terminal absence, not a timeout."""
    for attempt in range(3):
        if cancelled():
            raise Cancelled("Cancelled")
        response = None
        try:
            if session is not None:
                response = session.get(url, timeout=(15,60), stream=True)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                chunks = response.iter_content(65536)
            else:
                response = urlopen(url, timeout=60)
                chunks = iter(lambda: response.read(65536), b"")
            data = bytearray()
            for chunk in chunks:
                if cancelled():
                    raise Cancelled("Cancelled")
                data.extend(chunk)
                if len(data) > 64*1024*1024:
                    raise ValueError("Hybrid source response exceeds 64 MB; narrow the request")
            return data.decode("utf-8-sig")
        except HTTPError as exc:
            if exc.code == 404:
                return None
            if attempt == 2:
                raise
        except Cancelled:
            raise
        except Exception:
            if attempt == 2:
                raise
        finally:
            if response is not None:
                response.close()
        for unused in range(2**attempt * 5):
            if cancelled():
                raise Cancelled("Cancelled")
            time.sleep(.2)


def fetch_source(source, station, start, end, required, model, session, cancelled):
    if source=="Open-Meteo" and model in ("auto","auto_era5_1940"):
        plan=reanalysis_plan(required,"era5" if model=="auto_era5_1940" else "auto",start)
        combined=dict(series={},raw=[],urls=[],warnings=[],state="COMPLETE",models_by_variable={})
        for selected,variables in plan:
            try:part=fetch_source(source,station,start,end,variables,selected,session,cancelled)
            except Cancelled:raise
            except Exception as exc:
                # Preserve other product groups if one service request fails.
                # Partial responses remain auditable but are retried on rerun.
                combined["state"]="PARTIAL_FAILURE"
                combined["warnings"].append("Open-Meteo "+selected+": request failed; other variable groups continue: "+str(exc))
                combined["raw"].append(dict(model=selected,error=str(exc)))
                continue
            combined["series"].update(part["series"])
            combined["raw"].append(dict(model=selected,response=part["raw"]))
            for key in ("urls","warnings"):combined[key].extend(part.get(key,[]))
            combined["models_by_variable"].update({p:selected for p in variables})
        return combined
    query = dict(latitude=station["latitude"], longitude=station["longitude"])
    warnings = []
    if source == "NOAA GSOD":
        url = "https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/%d/%s.csv" % (start.year, observation_id(station))
    elif source == "Open-Meteo":
        query.update(start_date=start.isoformat(), end_date=end.isoformat(), models=model, timezone="UTC", wind_speed_unit="ms")
        daily = [OM_DAILY[p] for p in required if p in OM_DAILY]
        hourly = [OM_HOURLY[p] for p in required if p in OM_HOURLY]
        if daily:
            query["daily"] = ",".join(daily)
        if hourly:
            query["hourly"] = ",".join(hourly)
        url = "https://archive-api.open-meteo.com/v1/archive?"+urlencode(query)
    else:
        query.update(start=start.strftime("%Y%m%d"), end=end.strftime("%Y%m%d"),
                     parameters=",".join(required), community="RE", format="JSON")
        query["time-standard"] = "UTC"
        url = "https://power.larc.nasa.gov/api/temporal/daily/point?"+urlencode(query)
    text = _read(url, session, cancelled)
    if text is None:
        return dict(series={}, raw=None, urls=[url], warnings=[source+": no file/response (HTTP 404)"], state="NOT_AVAILABLE")
    if source == "NOAA GSOD":
        series, rejected = parse_noaa(text, station, start, end, required)
        if rejected:
            warnings.append("NOAA: %d daily records excluded: coordinates differ by >0.05 degrees; no correction applied." % rejected)
        raw = text
    else:
        raw = json.loads(text)
        series = {}
        if source == "NASA POWER":
            parameters = raw.get("properties", {}).get("parameter")
            if parameters is None:
                raise ValueError("NASA response has no climate parameter data")
            for p in required:
                series[p] = {dt.datetime.strptime(k, "%Y%m%d").date().isoformat():float(v)
                             for k,v in parameters.get(p, {}).items() if valid(v)}
            unit = raw.get("parameters", {}).get("ALLSKY_SFC_SW_DWN", {}).get("units", "").lower()
            if "kw" in unit:
                series["ALLSKY_SFC_SW_DWN"] = {k:v*3.6 for k,v in series.get("ALLSKY_SFC_SW_DWN", {}).items()}
        else:
            if "daily" not in raw and "hourly" not in raw:
                raise ValueError(raw.get("reason", "Open-Meteo response has no climate data"))
            daily, hourly = raw.get("daily", {}), raw.get("hourly", {})
            for p in required:
                if p in OM_DAILY:
                    series[p] = {day:float(v) for day,v in zip(daily.get("time", []), daily.get(OM_DAILY[p], [])) if valid(v)}
                elif p in OM_HOURLY:
                    grouped = {}
                    for timestamp,v in zip(hourly.get("time", []), hourly.get(OM_HOURLY[p], [])):
                        if valid(v):
                            grouped.setdefault(timestamp[:10], {})[timestamp] = float(v)
                    series[p] = {}
                    for day, hours in grouped.items():
                        if len(hours) != 24:
                            continue
                        values = list(hours.values())
                        if p == "WD10M":
                            x = sum(math.cos(math.radians(v)) for v in values)
                            y = sum(math.sin(math.radians(v)) for v in values)
                            if math.hypot(x,y) < 1e-10:
                                continue
                            value = math.degrees(math.atan2(y,x)) % 360
                        else:
                            value = sum(values)/24
                            if p in ("PS", "SLP"):
                                value /= 10
                        series[p][day] = value
    absent=[p for p in required if not series.get(p)]
    if absent:
        warnings.append(source+(" "+model if source=="Open-Meteo" else "")+
                        ": no usable values for "+", ".join(sorted(absent))+" in this request; missing values remain NULL.")
    return dict(series=series, raw=raw, urls=[url], warnings=warnings, state="COMPLETE")


def run(stations, start, end, required, cache_folder, progress, cancelled,
        model="auto", session=None, fetch=None, sources=None):
    """Finish one source for the entire network before starting the next one.

    Successful and 404 request checkpoints survive cancellation. Failed requests
    are recorded but retried on the next run. Only empty cells can be merged.
    Requests are bounded to a calendar year and the enclosing missing interval;
    a provider may return extra days, which never replace higher-priority data.
    """
    fetch = fetch or fetch_source
    sources=tuple(SOURCES if sources is None else sources)
    if model=="auto" and start.year<1950:model="auto_era5_1940"
    if not sources or len(set(sources))!=len(sources) or any(s not in SOURCES for s in sources):
        raise ValueError("Unknown or duplicate source in provider policy")
    if cache_folder is not None and not os.path.isdir(cache_folder):
        os.makedirs(cache_folder)
    keys = [station["station_key"] for station in stations]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate station identity in Hybrid request")
    records = [dict(station=s, series={p:{} for p in required}, provenance={}, warnings=[], source_events=[], raw_paths=[], urls=[],source_policy=list(sources)) for s in stations]
    noaa_params = set(v[0] for v in NOAA_FIELDS.values())
    for source in sources:
        for index, rec in enumerate(records):
            if cancelled():
                raise Cancelled("Cancelled")
            progress(dict(stage=source, completed=index, total=len(records), message="%s %d/%d" % (source,index+1,len(records))))
            station = rec["station"]
            supported = [p for p in required if source != "NOAA GSOD" or p in noaa_params]
            if source == "Open-Meteo":
                supported = [p for p in supported if p in OM_DAILY or p in OM_HOURLY]
            if source == "NOAA GSOD" and not observation_id(station):
                rec["source_events"].append(dict(source=source, state="NO_OBSERVATION_ID"))
                rec["warnings"].append("No valid USAF/WBAN observation identity. NOAA is station-only; no nearest station was substituted.")
                continue
            for year in range(start.year, end.year+1):
                first, last = max(start,dt.date(year,1,1)), min(end,dt.date(year,12,31))
                missing = {p:[d for d in days(first,last) if not valid(rec["series"].get(p,{}).get(d))] for p in supported}
                missing = {p:v for p,v in missing.items() if v}
                if not missing:
                    continue
                gap_days = [d for values in missing.values() for d in values]
                first, last, needed = date(min(gap_days)), date(max(gap_days)), sorted(missing)
                identity = dict(policy=POLICY, source=source, station=station, start=str(first), end=str(last), required=needed, model=model)
                token = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
                path = os.path.join(cache_folder, token+".json") if cache_folder is not None else None
                try:
                    response = None
                    if path is not None and os.path.isfile(path):
                        try:
                            with io.open(path, encoding="utf-8") as stream:
                                saved = json.load(stream)
                            if saved.get("identity") == identity and saved.get("response",{}).get("state")!="PARTIAL_FAILURE":
                                response = saved["response"]
                        except (ValueError, KeyError):
                            pass  # Interrupted/corrupt old cache is never trusted.
                    if response is None:
                        response = fetch(source,station,first,last,needed,model,session,cancelled)
                        if path is not None:
                            atomic_json(path, dict(identity=identity, response=response, retrieved_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())))
                    if path is not None:
                        rec["raw_paths"].append(path)
                    else:
                        rec.setdefault("raw_responses",[]).append(dict(source=source,response=response))
                    rec["urls"].extend(response.get("urls", []))
                    event = dict(source=source, start=str(first), end=str(last), state=response.get("state", "COMPLETE"))
                    rec["source_events"].append(event)
                    rec["warnings"].extend(response.get("warnings", []))
                    for p, values in response["series"].items():
                        if p not in needed:
                            continue
                        target, provenance = rec["series"].setdefault(p,{}), rec["provenance"].setdefault(p,{})
                        actual_model=response.get("models_by_variable",{}).get(p,model)
                        label = "Open-Meteo "+actual_model if source == "Open-Meteo" else source
                        for day,v in values.items():
                            if str(start)<=day<=str(end) and valid(v) and not valid(target.get(day)):
                                target[day], provenance[day] = float(v), label
                                rec.setdefault("resolution_by_variable",{}).setdefault(p,{})[label]=variable_resolution(source,p,actual_model)
                except Cancelled:
                    raise
                except Exception as exc:
                    if cancelled():
                        raise Cancelled("Cancelled")
                    rec["warnings"].append(source+": "+str(exc))
                    rec["source_events"].append(dict(source=source, start=str(first), end=str(last), state="FAILED", error=str(exc)))
        progress(dict(stage=source, completed=len(records), total=len(records), message=source+" stage complete"))
    for rec in records:
        rec["missing_counts"] = {p:sum(1 for d in days(start,end) if not valid(rec["series"].get(p,{}).get(d))) for p in required}
        rec["status"] = "OK" if any(valid(v) for values in rec["series"].values() for v in values.values()) else "FAILED"
        rec["error"] = "" if rec["status"] == "OK" else "No usable data from selected sources: "+", ".join(sources)
        rec["source_summary"] = " + ".join(sorted(set(s for values in rec["provenance"].values() for s in values.values())))
        summary_token = hashlib.sha256((POLICY+rec["station"]["station_key"]+str(start)+str(end)+model+",".join(sorted(required))+"|"+",".join(sources)).encode("utf-8")).hexdigest()
        if cache_folder is not None:
            rec["raw_path"] = os.path.join(cache_folder, summary_token+"-summary.json")
            atomic_json(rec["raw_path"], rec)
    return records


def monthly(series, start, end):
    """Full calendar month coverage, canonical units, no synthetic daily values."""
    output = {}
    for p, values in series.items():
        periods = {}
        for year in range(start.year,end.year+1):
            for month in range(1,13):
                first = dt.date(year,month,1)
                last = dt.date(year,month,calendar.monthrange(year,month)[1])
                if first < start or last > end:
                    continue
                v = [values.get(day) for day in days(first,last)]
                if not all(valid(value) for value in v):
                    periods[(year,month)] = None
                elif p == "PRECTOTCORR":
                    periods[(year,month)] = sum(v)
                elif p == "WD10M":
                    x, y = sum(math.cos(math.radians(n)) for n in v), sum(math.sin(math.radians(n)) for n in v)
                    periods[(year,month)] = math.degrees(math.atan2(y,x))%360 if math.hypot(x,y)>1e-10 else None
                else:
                    periods[(year,month)] = sum(v)/len(v)
        output[p] = periods
    return output


def prepare_monthly(records, start, end, method, fill_function):
    """One explicit monthly estimation pass after all online sources finish.

    Temporal filling retains the reviewed legacy mean-variable rules (rainfall
    and bearings excluded). Explicit spatial mode estimates individual monthly
    cells with inverse-distance weights from at most 3 original donor stations;
    it never estimates final indices or feeds estimated donors back into itself.
    """
    pending = []
    for index, rec in enumerate(records):
        prepared = rec.get("monthly_prepared")
        if prepared and prepared["method"] == method and prepared["start"] <= str(start) and prepared["end"] >= str(end):
            continue
        pending.append(index)
        rec["monthly"] = monthly(rec["series"], start, end)
        for p,values in rec.get("native_monthly",{}).items():
            rec["monthly"][p]={tuple(map(int,period.split("-"))):v for period,v in values.items()
                               if str(start)[:7]<=period<=str(end)[:7]}
        rec["monthly_gap_provenance"] = {}
        rec["monthly_prepared"] = dict(start=str(start), end=str(end), method=method)
    # Snapshot valid source cells before any estimate is made.
    originals = [{p:dict(values) for p,values in rec["monthly"].items()} for rec in records]
    for index, rec in enumerate(records):
        if index not in pending:
            continue
        if method not in ("climatological", "linear", "spatial"):
            continue
        for p, values in rec["monthly"].items():
            if p not in FILLABLE and not (method == "spatial" and p == "PRECTOTCORR"):
                continue
            filled = fill_function(originals[index].get(p,{}), method) if method != "spatial" else {}
            for period, value in list(values.items()):
                if valid(value):
                    continue
                donors = []
                estimate = filled.get(period)
                if method == "spatial":
                    lat, lon = rec["station"]["latitude"], rec["station"]["longitude"]
                    for other_index, other in enumerate(records):
                        v = originals[other_index].get(p,{}).get(period)
                        if other_index == index or not valid(v):
                            continue
                        other_lat, other_lon = other["station"]["latitude"], other["station"]["longitude"]
                        dlat, dlon = math.radians(other_lat-lat), math.radians(other_lon-lon)
                        a = math.sin(dlat/2)**2+math.cos(math.radians(lat))*math.cos(math.radians(other_lat))*math.sin(dlon/2)**2
                        distance = 6371008.8*2*math.asin(math.sqrt(max(0,min(1,a))))
                        donors.append((distance,other["station"]["station_key"],v))
                    donors.sort()
                    donors = donors[:3]
                    if donors:
                        estimate = donors[0][2] if donors[0][0]<1 else sum(v/max(d,1e-6) for d,k,v in donors)/sum(1/max(d,1e-6) for d,k,v in donors)
                if valid(estimate):
                    values[period] = float(estimate)
                    rec["monthly_gap_provenance"].setdefault(p,{})["%04d-%02d" % period] = dict(
                        value=float(estimate), method=method,
                        donors=[dict(station_key=k,distance_m=d) for d,k,v in donors])
    return records
