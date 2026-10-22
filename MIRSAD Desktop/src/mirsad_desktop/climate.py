"""Climate adapters; Hybrid uses network-wide source barriers and checkpoints."""
import calendar
import datetime as dt
from collections import defaultdict

from .exports import station_properties
from .registry import BY_NAME,parameters,OM_DAILY,OM_HOURLY,module_fields,unavailable
from .climate_sources import pipeline_sources,uses_reanalysis,model_code,GRID_HYBRID
RAW_UNITS={"T2M":"deg_C","T2M_MAX":"deg_C","T2M_MIN":"deg_C","TS":"deg_C","PRECTOTCORR":"mm/day",
           "PS":"kPa","SLP":"kPa","WS10M":"m/s","WD10M":"degree","RH2M":"percent","T2MDEW":"deg_C",
           "ALLSKY_SFC_SW_DWN":"MJ/m2/day","ALLSKY_SFC_UV_INDEX":"24h mean (NASA); daily max (ERA5)","CLOUD_AMT":"percent"}

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")
SEASONS = {"Winter": (12, 1, 2), "Spring": (3, 4, 5), "Summer": (6, 7, 8), "Autumn": (9, 10, 11)}


def number(value):
    import math
    try:
        result = float(value)
        return result if math.isfinite(result) and result > -900 else None
    except (ValueError, TypeError):
        return None

def request_json(session,url,query,cancelled):
    """Bound network input before JSON parsing, with normal TLS verification."""
    import json
    limit=64*1024*1024
    with session.get(url,params=query,timeout=(15,60),stream=True) as response:
        response.raise_for_status()
        if int(response.headers.get("Content-Length",0))>limit:raise ValueError("Climate response exceeds 64 MB; split the time interval.")
        data=bytearray()
        for chunk in response.iter_content(65536):
            if cancelled():raise InterruptedError("Cancelled")
            data.extend(chunk)
            if len(data)>limit:raise ValueError("Climate response exceeds 64 MB; split the time interval.")
        return json.loads(data),response.url


def summarize(series, start, end, module):
    """Daily input -> conservative full-month and full-year climate summaries."""
    by_month = defaultdict(list)
    for date, value in series.items():
        if start <= date <= end and number(value) is not None:
            by_month[(date.year, date.month)].append(float(value))
    monthly = {}
    for (year, month), values in by_month.items():
        days = calendar.monthrange(year, month)[1]
        if len(values) == days:
            monthly[(year, month)] = sum(values) if module == "Precipitation" else sum(values) / len(values)
    climatology = {}
    for month in range(1, 13):
        values = [v for (y, m), v in monthly.items() if m == month]
        climatology[month] = sum(values) / len(values) if values else None
    prefix = "T" if module == "Temperature" else "R"
    fields = {prefix + "_" + name + "_Mean": climatology[index] for index, name in enumerate(MONTHS, 1)}
    annual = []
    seasonal = defaultdict(list)
    for year in range(start.year, end.year + 1):
        if all((year, month) in monthly for month in range(1, 13)):
            values = [monthly[(year, month)] for month in range(1, 13)]
            annual.append(sum(values) if module == "Precipitation" else sum(values) / 12)
        for season, months in SEASONS.items():
            if all((year, month) in monthly for month in months):
                values = [monthly[(year, month)] for month in months]
                seasonal[season].append(sum(values) if module == "Precipitation" else sum(values) / len(values))
    fields[prefix + "_Annual_Mean"] = sum(annual) / len(annual) if annual else None
    for season in SEASONS:
        values = seasonal[season]
        fields[prefix + "_" + season + "_Mean"] = sum(values) / len(values) if values else None
    clim_values = [v for v in climatology.values() if v is not None]
    fields[prefix + "_Annual_Range"] = max(clim_values)-min(clim_values) if len(clim_values) == 12 else None
    valid = [float(value) for date, value in series.items() if start <= date <= end and number(value) is not None]
    expected = (end-start).days + 1
    fields["Valid_Days"] = len(valid)
    fields["Expected_Days"] = expected
    fields["Coverage_Fraction"] = len(valid)/expected
    if module == "Temperature":
        fields["T_Period_Mean"] = sum(valid)/len(valid) if valid else None
    else:
        fields["R_Period_Total"] = sum(valid) if len(valid) == expected else None
    return fields


def fetch_series(session, station, start, end, provider, cancelled, modules=None, om_model="auto", required_params=None, allow_supplement=True):
    if cancelled():
        raise InterruptedError("Cancelled")
    modules=modules or ["Temperature","Precipitation"]
    required=parameters(modules) if required_params is None else required_params
    if "Open-Meteo" in provider and not pipeline_sources(provider) and model_code(om_model)=="auto":
        provider=GRID_HYBRID
    if provider in ("NASA POWER", "NASA POWER API"):
        url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        query = dict(latitude=station["latitude"], longitude=station["longitude"],
                     start=start.strftime("%Y%m%d"), end=end.strftime("%Y%m%d"),
                     parameters=",".join(required), community="RE", format="JSON", **{"time-standard": "UTC"})
        payload,source_url=request_json(session,url,query,cancelled)
        if "properties" not in payload or "parameter" not in payload["properties"]:
            raise ValueError("NASA POWER response has no climate parameter data")
        result = {}
        for variable in required:
            result[variable] = {dt.datetime.strptime(key, "%Y%m%d").date(): number(value)
                              for key, value in payload["properties"]["parameter"].get(variable, {}).items()}
        # POWER's RE community reports solar daily energy in kWh/m²/day;
        # the shared scientific kernel's input contract is MJ/m²/day.
        unit=payload.get("parameters",{}).get("ALLSKY_SFC_SW_DWN",{}).get("units","").lower()
        if "kw" in unit:
            result["ALLSKY_SFC_SW_DWN"]={d:v*3.6 if v is not None else None for d,v in result.get("ALLSKY_SFC_SW_DWN",{}).items()}
    elif "Open-Meteo" in provider and not pipeline_sources(provider):
        url = "https://archive-api.open-meteo.com/v1/archive"
        query = dict(latitude=station["latitude"], longitude=station["longitude"], start_date=start.isoformat(),
                     end_date=end.isoformat(),models=model_code(om_model),timezone="UTC",wind_speed_unit="ms")
        daily_vars=[OM_DAILY[p] for p in required if p in OM_DAILY]
        hourly_vars=[OM_HOURLY[p] for p in required if p in OM_HOURLY]
        if daily_vars:query["daily"]=",".join(daily_vars)
        if hourly_vars:query["hourly"]=",".join(hourly_vars)
        if daily_vars or hourly_vars:
            payload,source_url=request_json(session,url,query,cancelled)
            if "daily" not in payload and "hourly" not in payload:
                raise ValueError(payload.get("reason", "Open-Meteo response has no climate data"))
        else:payload,source_url={},""
        times=[dt.date.fromisoformat(v) for v in payload.get("daily",{}).get("time",[])]
        result={p:dict(zip(times,[number(v) for v in payload.get("daily",{}).get(OM_DAILY[p],[])])) for p in required if p in OM_DAILY}
        for p in required:
            if p not in OM_HOURLY:continue
            grouped=defaultdict(list)
            hourly=payload.get("hourly",{})
            for timestamp,value in zip(hourly.get("time",[]),hourly.get(OM_HOURLY[p],[])):
                if number(value) is not None:grouped[dt.date.fromisoformat(timestamp[:10])].append(number(value))
            from .science import circular_mean_deg
            result[p]={day:(circular_mean_deg(values) if p=="WD10M" else sum(values)/24) for day,values in grouped.items() if len(values)==24}
            if p in ("SLP","PS"):
                result[p]={day:value/10 for day,value in result[p].items()} # hPa -> kernel kPa
        if allow_supplement:
            original_payload=payload
            provenance={p:{str(day):"Open-Meteo "+model_code(om_model) for day,value in values.items() if number(value) is not None}
                        for p,values in result.items()}
            payload={"Open-Meteo":original_payload,"provenance":provenance,"warnings":[]}
            days=[start+dt.timedelta(days=i) for i in range((end-start).days+1)]
            missing=[p for p in required if any(number(result.get(p,{}).get(d)) is None for d in days)]
            if missing:
                try:
                    supplement,url,raw=fetch_series(session,station,start,end,"NASA POWER",cancelled,modules,om_model,missing,False)
                    payload["NASA POWER"]=raw
                    for p,values in supplement.items():
                        for day,value in values.items():
                            if number(value) is not None and number(result.setdefault(p,{}).get(day)) is None:
                                result[p][day]=value;provenance.setdefault(p,{})[str(day)]="NASA POWER (declared supplement)"
                    source_url=(source_url+" ; " if source_url else "")+url
                except InterruptedError:raise
                except Exception as exc:payload["warnings"].append("NASA supplement: "+str(exc))
    elif pipeline_sources(provider):
        from .hybrid_pipeline import run, Cancelled
        selected=dict(station)
        selected.setdefault("station_key","%s|%s|%.8f|%.8f" % (station.get("usaf",""),station.get("wban",""),station["latitude"],station["longitude"]))
        try:
            record=run([selected],start,end,required,None,lambda value:None,cancelled,
                       model=model_code(om_model) if uses_reanalysis(provider) else "native",session=session,sources=pipeline_sources(provider))[0]
        except Cancelled as exc:
            raise InterruptedError(str(exc)) from exc
        if record["status"]=="FAILED":
            raise ValueError(record["error"]+": "+"; ".join(record["warnings"]))
        result={p:{dt.date.fromisoformat(day):v for day,v in values.items()} for p,values in record["series"].items()}
        source_url=" ; ".join(record["urls"])
        payload=record
    else:
        raise ValueError("Provider is not implemented: " + provider)
    if cancelled():
        raise InterruptedError("Cancelled")
    return result, source_url, payload


def download(stations, start, end, provider, modules, cache_folder, progress, cancelled, om_model="auto",credentials=None,extra_variables=None,et_methods=None):
    import hashlib
    import json
    import requests
    from pathlib import Path
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    if end < start or end >= dt.date.today():
        raise ValueError("Choose a valid past date interval.")
    if not modules or any(module not in BY_NAME for module in modules):
        raise ValueError("Choose one or more climate modules.")
    for module in modules:
        if unavailable(provider,module):raise ValueError(module+": "+unavailable(provider,module))
    cache = Path(cache_folder)
    cache.mkdir(parents=True, exist_ok=True)
    from .climate_products import descriptor,run as download_product
    required=parameters(modules)
    order=pipeline_sources(provider)
    from .daily_climate import selected_dependencies,validate_et_methods,PM_DEPENDENCIES
    methods=validate_et_methods(et_methods,modules)
    if extra_variables or "PM" in methods:
        required=sorted(set(required+selected_dependencies(extra_variables or [],modules)+list(PM_DEPENDENCIES if "PM" in methods else ())))
        if descriptor(provider):
            raise ValueError("Supplementary daily variables are not integrated with this product yet; choose an ERA5/POWER/GSOD point source.")
        if order is None:
            order=("Open-Meteo","NASA POWER") if "Open-Meteo" in provider else ("NASA POWER",)
    if descriptor(provider):
        from .hybrid_pipeline import Cancelled
        try:records=download_product(provider,stations,start,end,parameters(modules),str(cache),progress,cancelled,credentials=credentials)
        except Cancelled as exc:raise InterruptedError(str(exc)) from exc
        for rec in records:
            rec["series"]={p:{dt.date.fromisoformat(day):v for day,v in values.items()} for p,values in rec["series"].items()}
            if descriptor(provider)["temporal"]!="Daily":
                rec["monthly"]={p:{tuple(map(int,period.split("-"))):v for period,v in values.items()} for p,values in rec["native_monthly"].items()}
        return records,[dict(station_key=r["station"]["station_key"],error=r["error"]) for r in records if r["status"]=="FAILED"],sorted({url for r in records for url in r["urls"]})
    results, errors, source_urls = [], [], []
    with requests.Session() as session:
        session.headers["User-Agent"] = "MIRSAD-Desktop/0.1.0 (climate research)"
        retry = Retry(total=2, backoff_factor=1.0, status_forcelist=[429, 500, 502, 503, 504], respect_retry_after_header=True)
        session.mount("https://", HTTPAdapter(max_retries=retry))
        if order:
            from .hybrid_pipeline import run, Cancelled
            # The shared pipeline owns bounded retries, without nested HTTP retries.
            session.mount("https://", HTTPAdapter(max_retries=0))
            try:
                records=run(stations,start,end,required,str(cache),progress,cancelled,
                            model=model_code(om_model) if uses_reanalysis(provider) else "native",session=session,sources=order)
            except Cancelled as exc:
                raise InterruptedError(str(exc)) from exc
            for rec in records:
                rec["series"]={p:{dt.date.fromisoformat(day):v for day,v in values.items()} for p,values in rec["series"].items()}
            errors=[dict(station_key=rec["station"]["station_key"],error=rec["error"]) for rec in records if rec["status"]=="FAILED"]
            return records,errors,sorted({url for rec in records for url in rec["urls"]})
        for index, station in enumerate(stations, 1):
            if cancelled():
                raise InterruptedError("Cancelled")
            progress({"stage":"download","completed":index-1,"total":len(stations),"message":"%d/%d — %s"%(index,len(stations),station["name"])})
            token = hashlib.sha256(("v5"+station["station_key"]+provider+(model_code(om_model) if uses_reanalysis(provider) else "native")+start.isoformat()+end.isoformat()+",".join(parameters(modules))).encode()).hexdigest()
            raw_path = cache / (token + ".json")
            try:
                if raw_path.exists():
                    cached = json.loads(raw_path.read_text(encoding="utf-8"))
                    series = {module: {dt.date.fromisoformat(k): value for k, value in values.items()}
                              for module, values in cached["series"].items()}
                    source_url = cached["url"]
                else:
                    series, source_url, payload = fetch_series(session, station, start, end, provider, cancelled,modules,om_model)
                    cached = {"series": {m: {d.isoformat(): v for d, v in values.items()} for m, values in series.items()},
                              "url": source_url, "raw_response": payload, "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
                    raw_path.write_text(json.dumps(cached, ensure_ascii=False), encoding="utf-8")
                provenance=cached.get("raw_response",{}).get("provenance",{})
                actual=sorted({src for values in provenance.values() for src in values.values()})
                source_urls.append(source_url)
                results.append(dict(station=station,series=series,status="OK",error="",raw_path=str(raw_path),
                                    source_summary=" + ".join(actual) if actual else provider,
                                    provenance=provenance,resolution_by_variable=cached.get("raw_response",{}).get("resolution_by_variable",{}),warnings=cached.get("raw_response",{}).get("warnings",[])))
            except InterruptedError:
                raise
            except Exception as exc:
                errors.append({"station_key": station["station_key"], "error": str(exc)})
                results.append(dict(station=station, series={}, status="FAILED", error=str(exc)))
                progress("Failed: " + station["name"] + " — " + str(exc))
            progress({"stage":"download","completed":index,"total":len(stations),"message":"Downloaded %d/%d · failed %d"%(index,len(stations),len(errors))})
    return results, errors, source_urls


def prepare_outputs(results, modules, start, end, provider, gap_method="none",scopes=None,monthly_ranges=False,units="Metric",unit_options=None):
    layers, daily = {}, {}
    hybrid=bool(pipeline_sources(provider))
    if hybrid:
        from .hybrid_pipeline import prepare_monthly
        from .science import fill_interior_gaps
        adapted=[dict(rec,series={p:{str(day):v for day,v in values.items()} for p,values in rec["series"].items()}) for rec in results]
        prepare_monthly(adapted,start,end,gap_method,fill_interior_gaps)
        for rec,prepared in zip(results,adapted):
            for key in ("monthly","monthly_prepared","monthly_gap_provenance"):
                rec[key]=prepared[key]
    for module in modules:
        from .tabular import RowBuffer
        records, daily_rows = [], RowBuffer()
        for result in results:
            station = result["station"]
            raw=result["series"]
            # Compatibility with old cached/test fixtures; new downloads retain
            # every actual source variable instead of one column per module.
            raw=dict(raw)
            if "Temperature" in raw:raw["T2M"]=raw["Temperature"]
            if "Precipitation" in raw:raw["PRECTOTCORR"]=raw["Precipitation"]
            required=BY_NAME[module].params
            series=raw.get(required[0],{})
            props = station_properties(station)
            props.update(Data_Start=start.isoformat(), Data_End=end.isoformat(), Source=result.get("source_summary",provider),
                         Measurement_Unit=BY_NAME[module].unit, Status=result["status"],
                         Error_Msg=result["error"])
            from .science import compute_point_fields,circular_mean_deg
            monthly={p:{period:v for period,v in values.items() if start<=dt.date(*period,1)<=end}
                     for p,values in result.get("monthly",{}).items()}
            for variable,values in ([] if hybrid else raw.items()):
                groups=defaultdict(list)
                for date,value in values.items():
                    if start<=date<=end and number(value) is not None:groups[(date.year,date.month)].append(float(value))
                monthly[variable]={}
                for (year,month),values in groups.items():
                    if len(values)!=calendar.monthrange(year,month)[1]:continue
                    monthly[variable][(year,month)]=(sum(values) if variable=="PRECTOTCORR" else circular_mean_deg(values) if variable=="WD10M" else sum(values)/len(values))
            calculated=compute_point_fields(monthly,list(range(start.year,end.year+1)),[module],"Daily",precip_totals=True,
                gap_method="none" if hybrid else gap_method,lat=station["latitude"],uv_source="nasa",monthly_ranges=monthly_ranges)
            fields=module_fields(module,calculated)
            complete_years=[year for year in range(start.year,end.year+1) if all(number(monthly.get(p,{}).get((year,m))) is not None for p in required for m in range(1,13))]
            if not complete_years and module!="Trends & Anomalies":
                fields={key:None if "Annual" in key else value for key,value in fields.items()}
            if "monthly" in result and not hybrid:
                months=[(y,m) for y in range(start.year,end.year+1) for m in range(1,13) if start<=dt.date(y,m,1)<=end]
                coverage=result.get("native_monthly_coverage",{})
                # MODIS supplies the primary LST measurement only. The optional
                # surface-air difference remains NULL without an air temperature.
                coverage_variables=("TS",) if module=="Land Surface Temperature" and provider.startswith("MODIS MOD11A2") else required
                fractions=[min((coverage.get(p,{}).get("%04d-%02d"%period,1.) if number(monthly.get(p,{}).get(period)) is not None else 0.) for p in coverage_variables) for period in months]
                valid=sum(f>=1. for f in fractions)
                fields.update(Valid_Days=None,Expected_Days=None,Valid_Months=valid,Expected_Months=len(months),Coverage_Fraction=sum(fractions)/max(1,len(months)))
                if coverage:props["Source_Temporal_Resolution"]="Native monthly / documented composite aggregation"
            elif module in ("Temperature","Precipitation"):
                summary=summarize(series,start,end,module)
                if hybrid:
                    summary={k:v for k,v in summary.items() if k in ("Valid_Days","Expected_Days","Coverage_Fraction","T_Period_Mean","R_Period_Total")}
                fields.update(summary)
            else:
                valid=sum(1 for offset in range((end-start).days+1) if all(number(raw.get(p,{}).get(start+dt.timedelta(days=offset))) is not None for p in required))
                fields.update(Valid_Days=valid,Expected_Days=(end-start).days+1,Coverage_Fraction=valid/((end-start).days+1))
            if units=="Imperial" or unit_options:
                from .science import convert_fields_to_user_units
                original=dict(fields)
                options=dict(unit_temp="Fahrenheit",unit_precip="Inches",unit_press="inHg",unit_wind="mph") if units=="Imperial" else {}
                options.update({k:v for k,v in (unit_options or {}).items() if v})
                if set(options)-{"unit_temp","unit_precip","unit_press","unit_wind","unit_solar"}:raise ValueError("Unknown output unit setting")
                fields=convert_fields_to_user_units(fields,**options)
                for key,value in original.items():
                    if key.startswith("LST_minus_T") and value is not None:fields[key]=round(value*(1.8 if "Fahrenheit" in options.get("unit_temp","") else 1),2)
                props["Measurement_Unit"]={"deg_C":"deg_F","mm":"inches","hPa":"inHg","m/s; degree":"mph; degree","mixed":"deg_F; inches; percent"}.get(BY_NAME[module].unit,BY_NAME[module].unit)
                key={"deg_C":"unit_temp","mm":"unit_precip","hPa":"unit_press","m/s; degree":"unit_wind","kWh/m2/day":"unit_solar"}.get(BY_NAME[module].unit)
                if key and options.get(key):props["Measurement_Unit"]=options[key]+("; degree" if key=="unit_wind" else "")
                elif units!="Imperial":props["Measurement_Unit"]=BY_NAME[module].unit
            if scopes is not None:
                months=tuple("_"+m+"_" for m in MONTHS)
                fields={k:v for k,v in fields.items()
                    if not(any("_"+s+"_" in k and s not in scopes for s in SEASONS) and "Seasonal" not in scopes)
                    and not("Annual" in k and "Annual" not in scopes)}
            props.update(fields)
            if hybrid:
                props["Gap_Fill_Method"]=gap_method
                props["Gap_Filled_Months"]=sum(1 for p in required for period in result.get("monthly_gap_provenance",{}).get(p,{}) if start<=dt.date.fromisoformat(period+"-01")<=end)
            if module=="Trends & Anomalies" and not any(value is not None for value in calculated.values()):
                props["Status"]="INSUFFICIENT_HISTORY"
                props["Error_Msg"]="Trend requires >=8 complete years; anomalies require >=20 baseline years (1991–2020) and >=5 recent years."
            if result["status"] == "OK" and props["Coverage_Fraction"] < 1:
                any_data=any(number(v) is not None for p in required for v in monthly.get(p,{}).values()) if "monthly" in result and not hybrid else any(number(v) is not None for p in required for d,v in raw.get(p,{}).items() if start<=d<=end)
                props["Status"] = "NO_DATA" if not any_data else "PARTIAL"
                props["Error_Msg"] = ("%d of %d months have full dependency/quality coverage; coverage fraction %.3f."%(props["Valid_Months"],props["Expected_Months"],props["Coverage_Fraction"])) if "monthly" in result and not hybrid else "%d of %d requested daily values are available." % (props["Valid_Days"],props["Expected_Days"])
            records.append(dict(latitude=station["latitude"], longitude=station["longitude"], properties=props))
            dates=sorted({d for p in required for d in raw.get(p,{})})
            for date in dates:
                if start <= date <= end:
                    for variable in required:
                        if date in raw.get(variable,{}):
                            daily_rows.append([station["station_key"],station["usaf"],station["name"],date.isoformat(),variable,RAW_UNITS.get(variable,"source unit"),raw[variable][date]])
        layers[module] = records
        daily[module] = (["Station_Key", "Station_ID", "Station_Name", "Date", "Variable", "Unit", "Value"], daily_rows)
    return layers, daily
