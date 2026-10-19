# -*- coding: utf-8 -*-
"""Public climate product contracts and adapters shared by ArcMap/Pro/Desktop.

Native monthly/composite products never become fabricated daily observations.
All product values, scale metadata, requests and quality decisions are retained.
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
import re
import sys
import xml.etree.ElementTree as ET
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from . import hybrid_pipeline as h
from .remote_grid import RangeGrid,InterruptedErrorCompat
from .protected_sources import CDS,IMERG

CHIRPS="CHIRPS v3 (Monthly Rainfall)"
TERRA="TerraClimate v1.1 (Monthly Climate)"
CHELSA="CHELSA v2.1 (Monthly Climate)"
MODIS_DAY="MODIS MOD11A2 (Daytime Surface Temperature)"
MODIS_NIGHT="MODIS MOD11A2 (Nighttime Surface Temperature)"
GHCN="NOAA GHCN-Daily (Station Observations Only)"
PRODUCTS={
    CDS:dict(id="cds_era5_land_arco",variables=["T2M","T2M_MAX","T2M_MIN","T2MDEW","RH2M","TS","PS","WS10M","WD10M","PRECTOTCORR","ALLSKY_SFC_SW_DWN"],resolution="0.1 degree API grid",temporal="Daily",start="1950-01",end="Latest published CDS ARCO data",region="Global land",url="https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries",auth="cds_token"),
    IMERG:dict(id="imerg07_final",variables=["PRECTOTCORR"],resolution="0.1 degree",temporal="Daily",start="File-specific GES DISC catalogue",end="Latest Final run (delayed)",region="Global grid; missing cells retained",url="https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary",auth="earthdata"),
    CHIRPS:dict(id="chirps3",variables=["PRECTOTCORR"],resolution="0.05 degree",temporal="Monthly",start="1981-01",end="Latest final month",region="Land 60S to 60N",url="https://www.chc.ucsb.edu/data/chirps3",auth=None),
    TERRA:dict(id="terraclimate11",variables=["T2M","T2M_MAX","T2M_MIN","PRECTOTCORR","WS10M","ALLSKY_SFC_SW_DWN"],resolution="1/24 degree (~4 km)",temporal="Monthly",start="1950-01",end="Latest published month; inspected from time axis",region="Global land",url="https://www.climatologylab.org/terraclimate.html",auth=None),
    CHELSA:dict(id="chelsa21",variables=["T2M","T2M_MAX","T2M_MIN","PRECTOTCORR","WS10M","RH2M","CLOUD_AMT"],resolution="30 arcsec (~1 km)",temporal="Monthly",start="1979/1980; variable-specific catalogue",end="2018/2021; variable-specific catalogue",region="Global land",url="https://www.chelsa-climate.org/datasets/chelsa_monthly",auth=None),
    MODIS_DAY:dict(id="mod11a2_day",variables=["TS"],resolution="Nominal 1 km",temporal="8-day clear-sky composites; explicit monthly aggregation",start="2000-02",end="Available site dates from API",region="Global land",url="https://modis.ornl.gov/data/modis_webservice.html",auth=None),
    MODIS_NIGHT:dict(id="mod11a2_night",variables=["TS"],resolution="Nominal 1 km",temporal="8-day clear-sky composites; explicit monthly aggregation",start="2000-02",end="Available site dates from API",region="Global land",url="https://modis.ornl.gov/data/modis_webservice.html",auth=None),
    GHCN:dict(id="ghcnd",variables=["T2M","T2M_MAX","T2M_MIN","PRECTOTCORR"],resolution="Station location",temporal="Daily",start="Station/element-specific",end="Station/element-specific",region="Catalogue stations only",url="https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily",auth=None),
}
ENABLED=(CHIRPS,TERRA,MODIS_DAY,MODIS_NIGHT,GHCN,CDS,IMERG,CHELSA)
REGIONAL=(CHIRPS,CHELSA)


def grid_url(provider,parameter,period):
    year,month=map(int,period.split("-"))
    if provider==CHIRPS:
        return "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/chirps-v3.0.%04d.%02d.cog"%(year,month)
    variable={"T2M":"tas","T2M_MAX":"tasmax","T2M_MIN":"tasmin","PRECTOTCORR":"pr","WS10M":"sfcWind","RH2M":"hurs","CLOUD_AMT":"clt"}[parameter]
    return "https://os.unil.cloud.switch.ch/chelsa02/chelsa/global/monthly/%s/%04d/CHELSA_%s_%02d_%04d_V.2.1.tif"%(variable,year,variable,month,year)


def native_grid_cells(provider,bounds,start,end,required,folder,cancelled,contains=None,limit=20000):
    """Enumerate original native cell centres; never oversample a point service."""
    if provider not in REGIONAL:raise ValueError("Product has no regional native-grid implementation")
    west,south,east,north=map(float,bounds)
    if not all(not math.isnan(v) and not math.isinf(v) for v in bounds) or not(-180<=west<east<=180 and -90<=south<north<=90):raise ValueError("Use a non-wrapping WGS84 study extent")
    selected=[p for p in required if p in PRODUCTS[provider]["variables"]]
    periods=list(months(start,end))
    if not selected or not periods:raise ValueError("Select supported variables and complete calendar months")
    grid=None;errors=[]
    for period in periods:
        for parameter in selected:
            try:
                grid=RangeGrid(grid_url(provider,parameter,period),folder,cancelled);break
            except InterruptedErrorCompat:raise h.Cancelled("Cancelled")
            except Exception as exc:errors.append(str(exc))
        if grid:break
    if not grid:raise ValueError("No native source grid available: "+"; ".join(errors[:3]))
    c0=max(0,int(math.ceil((west-grid.west)/grid.dx-.5)))
    c1=min(grid.width-1,int(math.floor((east-grid.west)/grid.dx-.5)))
    r0=max(0,int(math.ceil((grid.north-north)/grid.dy-.5)))
    r1=min(grid.height-1,int(math.floor((grid.north-south)/grid.dy-.5)))
    if max(0,c1-c0+1)*max(0,r1-r0+1)>2000000:raise ValueError("Study extent exceeds bounded native-grid enumeration; process smaller areas")
    cells=[]
    for row in range(r0,r1+1):
        if cancelled():raise h.Cancelled("Cancelled")
        lat=grid.north-(row+.5)*grid.dy
        for column in range(c0,c1+1):
            lon=grid.west+(column+.5)*grid.dx
            if contains and not contains(lon,lat):continue
            cells.append(dict(station_key=PRODUCTS[provider]["id"]+"|%d|%d"%(row,column),
                name=PRODUCTS[provider]["id"]+" native cell",latitude=lat,longitude=lon,row=row,column=column))
            if len(cells)>limit:raise ValueError("Study area exceeds %d native cells; process smaller areas"%limit)
    if not cells:raise ValueError("Study area contains no native cell centres; enlarge it or use the point tool")
    return cells


def choices(stations=False):
    return [name for name in ENABLED if stations or name!=GHCN]


def descriptor(provider):
    return PRODUCTS.get(provider)


def months(start,end):
    for year in range(start.year,end.year+1):
        for month in range(1,13):
            first=dt.date(year,month,1);last=dt.date(year,month,calendar.monthrange(year,month)[1])
            if start<=first and last<=end:yield "%04d-%02d"%(year,month)


def csv_rows(text):
    return csv.DictReader(io.BytesIO(text.encode("utf-8")) if sys.version_info[0]==2 else io.StringIO(text))


def unpack_cf(value,attributes):
    """NCSS CSV returns packed values even when its header displays CF units."""
    raw=float(value)
    sentinels=[float(attributes[k]) for k in ("_FillValue","missing_value") if k in attributes]
    if math.isnan(raw) or math.isinf(raw) or raw in sentinels:return None
    return raw*float(attributes.get("scale_factor",1))+float(attributes.get("add_offset",0))


def parse_ghcn(text,identifier,start,end,required):
    mapping={"TAVG":"T2M","TMAX":"T2M_MAX","TMIN":"T2M_MIN","PRCP":"PRECTOTCORR"}
    series={};rejected=0
    for line in text.splitlines():
        if len(line)<269:continue
        if line[:11]!=identifier:raise ValueError("GHCN station identity mismatch")
        year,month=int(line[11:15]),int(line[15:17]);parameter=mapping.get(line[17:21])
        if parameter not in required:continue
        for day in range(1,calendar.monthrange(year,month)[1]+1):
            when=dt.date(year,month,day)
            if not start<=when<=end:continue
            segment=line[21+(day-1)*8:29+(day-1)*8];raw=int(segment[:5])
            if raw==-9999:continue
            if segment[6]!=" ":rejected+=1;continue
            series.setdefault(parameter,{})[str(when)]=raw/10.
    return series,rejected


def run(provider,stations,start,end,required,folder,progress,cancelled,session=None,credentials=None):
    spec=descriptor(provider)
    if not spec:raise ValueError("Unknown climate product")
    if not os.path.isdir(folder):os.makedirs(folder)
    records=[dict(station=s,series={},native_monthly={},provenance={},resolution_by_variable={},
                  raw_paths=[],urls=[],warnings=[],status="FAILED",error="",source_summary=provider,
                  source_policy=[provider],native_monthly_coverage={}) for s in stations]
    periods=list(months(start,end));allowed=[p for p in required if p in spec["variables"]]
    text_cache={}
    def read(url,rec):
        if cancelled():raise h.Cancelled("Cancelled")
        token=hashlib.sha256(("products-v1|"+url).encode("utf-8")).hexdigest()
        path=os.path.join(folder,token+".response.json")
        if url in text_cache:text=text_cache[url]
        elif os.path.isfile(path):
            with io.open(path,encoding="utf-8") as stream:saved=json.load(stream)
            if saved["url"]!=url:raise ValueError("Source checkpoint identity mismatch")
            text=saved["text"];text_cache[url]=text
        else:
            text=h._read(url,session,cancelled)
            if text is None:raise ValueError("Product not available (HTTP 404): "+url)
            h.atomic_json(path,dict(url=url,text=text));text_cache[url]=text
        if path not in rec["raw_paths"]:rec["raw_paths"].append(path)
        if url not in rec["urls"]:rec["urls"].append(url)
        return text
    def annotate(rec,p):
        rec["resolution_by_variable"][p]={provider:dict(product=spec["id"],spatial=spec["resolution"],temporal=spec["temporal"])}
    def put(rec,p,period,value,coverage=1.):
        if value is not None:
            rec["native_monthly"].setdefault(p,{})[period]=float(value)
            rec["native_monthly_coverage"].setdefault(p,{})[period]=coverage
            rec["provenance"].setdefault(p,{})[period]=provider;annotate(rec,p)
    for rec in records:
        if not allowed:rec["warnings"].append("Selected product has no requested dependencies; no download was made.")
        unsupported=set(required)-set(allowed)
        if unsupported:rec["warnings"].append("Unsupported variables remain NULL: "+", ".join(sorted(unsupported)))
    if spec.get("auth"):
        from .protected_sources import protected_fetch
        for rec in records:
            token=hashlib.sha256((spec["id"]+rec["station"]["station_key"]+str(start)+str(end)+",".join(sorted(allowed))).encode("utf-8")).hexdigest()
            path=os.path.join(folder,token+"-protected-response.json")
            try:
                if not allowed:continue
                progress(dict(stage="download",completed=records.index(rec),total=len(records),message=provider+": submitting selected product request"))
                if os.path.isfile(path):
                    with io.open(path,encoding="utf-8") as f:response=json.load(f)
                else:
                    response=protected_fetch(provider,rec["station"],start,end,allowed,credentials or {},cancelled)
                    h.atomic_json(path,response)
                rec["series"]=response["series"];rec["urls"].extend(response["urls"]);rec["warnings"].extend(response["warnings"])
                rec["raw_paths"].append(path)
                for p,values in rec["series"].items():
                    rec["provenance"][p]={day:provider for day in values};annotate(rec,p)
            except h.Cancelled:raise
            except Exception as exc:
                error=str(exc)
                for secret in (credentials or {}).values():
                    if secret:error=error.replace(secret,"[redacted]")
                rec["warnings"].append(error)
    elif provider==TERRA:
        mapping={"T2M_MAX":"tmax","T2M_MIN":"tmin","PRECTOTCORR":"ppt","WS10M":"ws","ALLSKY_SFC_SW_DWN":"srad"}
        needed=set(allowed)
        if "T2M" in needed:needed.update(("T2M_MAX","T2M_MIN"))
        for parameter in sorted(needed):
            variable=mapping.get(parameter)
            if not variable:continue
            base="https://thredds.northwestknowledge.net/thredds/ncss/agg_terraclimate_%s_1950_CurrentYear_GLOBE.nc"%variable
            for rec in records:
                try:
                    xml=read(base+"/dataset.xml",rec)
                    if "<!DOCTYPE" in xml:raise ValueError("Unexpected XML document type")
                    grid=next(g for g in ET.fromstring(xml).iter("grid") if g.get("name")==variable)
                    attributes={a.get("name"):a.get("value") for a in grid.findall("attribute")}
                    expected={"tmax":"degC","tmin":"degC","ppt":"mm","ws":"m/s","srad":"W/m2"}[variable]
                    if attributes.get("units","").replace("^","")!=expected:raise ValueError("Unexpected native units for "+variable+": "+str(attributes.get("units")))
                    query=dict(var=variable,latitude=rec["station"]["latitude"],longitude=rec["station"]["longitude"],
                        time_start=str(start)+"T00:00:00Z",time_end=str(end)+"T23:59:59Z",timeStride=1,accept="csv")
                    rows=csv_rows(read(base+"?"+urlencode(query),rec))
                    column=next(k for k in rows.fieldnames if k.startswith(variable+"["))
                    for row in rows:
                        period=row["time"][:7]
                        if period not in periods:continue
                        value=unpack_cf(row[column],attributes)
                        if parameter=="ALLSKY_SFC_SW_DWN" and value is not None:value*=.0864 # W/m2 -> MJ/m2/day
                        put(rec,parameter,period,value)
                    rec.setdefault("cf_metadata",{})[variable]=attributes
                except h.Cancelled:raise
                except Exception as exc:rec["warnings"].append(parameter+": "+str(exc))
        if "T2M" in allowed:
            for rec in records:
                for period in periods:
                    hi=rec["native_monthly"].get("T2M_MAX",{}).get(period);lo=rec["native_monthly"].get("T2M_MIN",{}).get(period)
                    if hi is not None and lo is not None:put(rec,"T2M",period,(hi+lo)/2)
                rec["warnings"].append("T2M is derived as (monthly tmax+tmin)/2, not an independent observed mean temperature.")
    elif provider in (CHIRPS,CHELSA):
        mapping={"T2M":"tas","T2M_MAX":"tasmax","T2M_MIN":"tasmin","PRECTOTCORR":"pr","WS10M":"sfcWind","RH2M":"hurs","CLOUD_AMT":"clt","ALLSKY_SFC_SW_DWN":"rsds"}
        for period in periods:
            year,month=map(int,period.split("-"))
            for parameter in allowed:
                url=grid_url(provider,parameter,period)
                variable=mapping[parameter]
                try:
                    grid=RangeGrid(url,folder,cancelled,session)
                    for rec in records:
                        value=grid.sample(rec["station"]["longitude"],rec["station"]["latitude"])
                        if provider==CHELSA:
                            meta=grid.gdal_metadata
                            expected_unit={"T2M":"K","T2M_MAX":"K","T2M_MIN":"K","PRECTOTCORR":"kg m-2 month-1","WS10M":"m s-1","RH2M":"%","CLOUD_AMT":"%","ALLSKY_SFC_SW_DWN":"MJ m-2 d-1"}[parameter]
                            actual_unit=meta.get("variable_unit","").replace("**"," ").replace("^","")
                            units=("%","percent") if parameter in ("RH2M","CLOUD_AMT") else (expected_unit,)
                            if meta.get("version")!="2.1" or meta.get("variable")!=variable or actual_unit not in units:raise ValueError("Unexpected CHELSA version/variable/unit: "+actual_unit+"; no values inferred")
                            if meta.get("datetime","")[:7]!=period or meta.get("frequency")!="month":raise ValueError("CHELSA metadata period mismatch")
                            if not(0<grid.scale<100) or math.isnan(grid.scale) or math.isinf(grid.scale):raise ValueError("Invalid CHELSA scale")
                            if value is not None:value=value*grid.scale+grid.offset
                            if value is not None and parameter in ("T2M","T2M_MAX","T2M_MIN"):value-=273.15
                            rec.setdefault("grid_metadata",{})[url]=dict(scale=grid.scale,offset=grid.offset,metadata=grid.gdal_metadata)
                        if value is not None and parameter in ("PRECTOTCORR","WS10M","RH2M","CLOUD_AMT","ALLSKY_SFC_SW_DWN") and value<0:value=None
                        put(rec,parameter,period,value)
                        rec["urls"].append(url)
                    for rec in records:rec["raw_paths"].extend(p for p in grid.raw_paths if p not in rec["raw_paths"])
                except (h.Cancelled,InterruptedErrorCompat):raise h.Cancelled("Cancelled")
                except Exception as exc:
                    for rec in records:rec["warnings"].append(period+" "+parameter+": "+str(exc))
    elif provider==GHCN:
        catalogue_url="https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
        for rec in records:
            try:
                station=rec["station"];attrs=station.get("attributes",{})
                identifier=station.get("ghcn_id") or attrs.get("GHCN_ID") or attrs.get("ghcn_id")
                if not identifier:raise ValueError("An explicit GHCN_ID and matching location are required; no nearest station was substituted")
                identifier=str(identifier).strip()
                if not re.match(r"^[A-Za-z0-9]{11}$",identifier):raise ValueError("GHCN_ID must be the exact 11-character archive identifier")
                row=next((line for line in read(catalogue_url,rec).splitlines() if line[:11]==identifier),None)
                if not row:raise ValueError("GHCN_ID absent from the source catalogue")
                if abs(float(row[12:20])-station["latitude"])>.01 or abs(float(row[21:30])-station["longitude"])>.01:raise ValueError("GHCN catalogue coordinates differ by >0.01 degree; no correction applied")
                series,rejected=parse_ghcn(read("https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/"+identifier+".dly",rec),identifier,start,end,allowed)
                rec["series"]=series;rec["observation_identity"]=identifier
                rec["warnings"].append("GHCN quality-flagged values excluded: %d"%rejected)
                for p,values in series.items():
                    rec["provenance"][p]={day:provider for day in values};annotate(rec,p)
            except h.Cancelled:raise
            except Exception as exc:rec["warnings"].append(str(exc))
    elif provider in (MODIS_DAY,MODIS_NIGHT):
        for rec in records:
            try:
                if "TS" not in allowed:continue
                query=dict(latitude=rec["station"]["latitude"],longitude=rec["station"]["longitude"])
                base="https://modis.ornl.gov/rst/api/v1/MOD11A2/"
                dates=json.loads(read(base+"dates?"+urlencode(query),rec))["dates"]
                # Include the preceding composite for overlaps with month boundaries.
                selected=[d for d in dates if str(start-dt.timedelta(days=7))<=d["calendar_date"]<=str(end)]
                daytime=provider==MODIS_DAY;band="LST_Day_1km" if daytime else "LST_Night_1km"
                qc="QC_Day" if daytime else "QC_Night";sky="Clear_sky_days" if daytime else "Clear_sky_nights"
                weighted={};counts={};rec["composites"]=[]
                for offset in range(0,len(selected),10):
                    batch=selected[offset:offset+10];q=dict(query,startDate=batch[0]["modis_date"],endDate=batch[-1]["modis_date"],kmAboveBelow=0,kmLeftRight=0)
                    data=json.loads(read(base+"subset?"+urlencode(q),rec));grouped={}
                    if data["nrows"]!=1 or data["ncols"]!=1:raise ValueError("Expected one native MODIS cell")
                    for entry in data["subset"]:grouped.setdefault(entry["calendar_date"],{})[entry["band"]]=entry["data"][0]
                    for day,values in grouped.items():
                        raw=float(values.get(band,0));flags=int(values.get(qc,255));mask=int(values.get(sky,0))
                        accepted=7500<=raw<=65535 and (flags&3)<=1 and ((flags>>2)&3)==0 and ((flags>>6)&3)<=1
                        value=raw*.02-273.15 if accepted else None
                        rec["composites"].append(dict(date=day,band=band,raw=raw,qc=flags,clear_sky_mask=mask,accepted=accepted,value_degC=value))
                        first=h.date(day)
                        for index in range(min(8,(dt.date(first.year+1,1,1)-first).days)):
                            when=first+dt.timedelta(days=index);period=str(when)[:7]
                            if accepted and mask&(1<<index) and start<=when<=end and period in periods:
                                weighted[period]=weighted.get(period,0)+value;counts[period]=counts.get(period,0)+1
                for period,total in weighted.items():
                    year,month=map(int,period.split("-"));put(rec,"TS",period,total/counts[period],counts[period]/float(calendar.monthrange(year,month)[1]))
                rec["warnings"].append("Monthly clear-sky composite-weighted LST estimate; not a 24h air/surface mean. Daily rows are not fabricated. Coverage counts quality-accepted clear-sky days.")
            except h.Cancelled:raise
            except Exception as exc:rec["warnings"].append(str(exc))
    for index,rec in enumerate(records):
        if cancelled():raise h.Cancelled("Cancelled")
        available=any(values for values in rec["series"].values()) or any(values for values in rec["native_monthly"].values())
        rec["status"]="OK" if available else "FAILED"
        rec["error"]="" if available else "No usable selected-product values; inspect source warnings"
        if spec["temporal"]!="Daily" and not periods:rec["warnings"].append("This product requires complete calendar months for monthly outputs")
        token=hashlib.sha256((spec["id"]+rec["station"]["station_key"]+str(start)+str(end)+",".join(sorted(required))).encode("utf-8")).hexdigest()
        rec["raw_path"]=os.path.join(folder,token+"-product-summary.json")
        h.atomic_json(rec["raw_path"],rec)
        progress(dict(stage="download",completed=index+1,total=len(records),message=provider+" product stage complete"))
    return records
