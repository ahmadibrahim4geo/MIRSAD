# -*- coding: utf-8 -*-
"""Explicit user-account adapters. Credentials are never included in returned data.

CDS ARCO is already de-accumulated hourly; do not de-accumulate it again.
NASA IMERG Daily reports mm/day, not mm/hour. No source substitution is made.
"""
from __future__ import unicode_literals
import datetime as dt
import io
import json
import math
import re
import time
import zipfile
try:
    from urllib.parse import urlparse,urljoin
except ImportError:
    from urlparse import urlparse,urljoin
from . import hybrid_pipeline as h

CDS="Copernicus CDS ERA5-Land (Need Sign In)"
IMERG="NASA IMERG V07 Daily Final (Need Sign In)"
CDS_URL="https://cds.climate.copernicus.eu/api/retrieve/v1/"
LAND_MAPPING={"T2M":"2m_temperature","T2M_MAX":"2m_temperature","T2M_MIN":"2m_temperature",
              "T2MDEW":"2m_dewpoint_temperature","RH2M":"2m_dewpoint_temperature","TS":"skin_temperature",
              "PS":"surface_pressure","WS10M":"10m_u_component_of_wind","WD10M":"10m_u_component_of_wind",
              "PRECTOTCORR":"total_precipitation","ALLSKY_SFC_SW_DWN":"surface_solar_radiation_downwards"}
CDS_COLUMNS={"2m_temperature":("t2m","2m_temperature"),"2m_dewpoint_temperature":("d2m","2m_dewpoint_temperature"),
    "skin_temperature":("skt","skin_temperature"),"surface_pressure":("sp","surface_pressure"),
    "10m_u_component_of_wind":("u10","10m_u_component_of_wind"),"10m_v_component_of_wind":("v10","10m_v_component_of_wind"),
    "total_precipitation":("tp","total_precipitation"),"surface_solar_radiation_downwards":("ssrd","surface_solar_radiation_downwards")}


def read_bounded(response,limit=64*1024*1024):
    if int(response.headers.get("Content-Length",0))>limit:raise ValueError("Source response exceeds 64 MB; reduce the request")
    chunks=[];size=0
    try:
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>limit:raise ValueError("Source response exceeds 64 MB")
            chunks.append(chunk)
    finally:response.close()
    return b"".join(chunks)


def cds_payload(variable,station):
    lat,lon=station["latitude"],station["longitude"]
    return dict(inputs=dict(variable=[variable],data_format="csv",area=[lat,lon,lat,lon]))


def cds_download(variable,station,token,cancelled,session):
    if not token:raise ValueError("Need Sign In: enter your CDS personal API token and accept the dataset terms on CDS")
    headers={"PRIVATE-TOKEN":token,"User-Agent":"MIRSAD climate research"}
    endpoint=CDS_URL+"processes/reanalysis-era5-land-timeseries/execution"
    response=session.post(endpoint,json=cds_payload(variable,station),headers=headers,timeout=(15,60),allow_redirects=False)
    if response.status_code in (401,403):raise ValueError("CDS sign-in/terms required; check your personal token and dataset licence acceptance")
    if response.status_code not in (200,201,202):raise ValueError("CDS request rejected (HTTP %s)"%response.status_code)
    info=response.json();job=info.get("jobID") or info.get("job_id")
    if not job or not re.match(r"^[A-Za-z0-9-]{1,128}$",str(job)):raise ValueError("CDS returned no valid job identifier")
    url=CDS_URL+"jobs/"+str(job)
    for unused in range(360):
        if cancelled():raise h.Cancelled("Cancelled")
        response=session.get(url,headers=headers,timeout=(15,60),allow_redirects=False)
        if response.status_code!=200:raise ValueError("CDS job status unavailable (HTTP %s)"%response.status_code)
        status=response.json().get("status")
        if status in ("failed","dismissed"):raise ValueError("CDS job failed or was dismissed; inspect your CDS request dashboard")
        if status=="successful":break
        for tick in range(25):
            if cancelled():raise h.Cancelled("Cancelled")
            time.sleep(.2)
    else:raise ValueError("CDS queue did not complete within 30 minutes; retry later")
    response=session.get(url+"/results",headers=headers,timeout=(15,60),allow_redirects=False)
    if response.status_code!=200:raise ValueError("CDS result listing unavailable")
    result=response.json();assets=result.get("asset",{})
    href=assets.get("value",{}).get("href") or assets.get("href")
    if not href:
        href=next((v.get("href") for v in result.values() if isinstance(v,dict) and v.get("href")),None)
    if not href or urlparse(href).scheme!="https":raise ValueError("CDS did not return a secure download asset")
    # Do not forward the CDS token to the separate object-storage download host.
    response=session.get(href,timeout=(15,60),stream=True)
    if response.status_code!=200:raise ValueError("CDS download unavailable; retry the request")
    data=read_bounded(response)
    if data.startswith(b"PK"):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members=[m for m in archive.infolist() if m.filename.lower().endswith(".csv")]
            if len(members)!=1 or members[0].file_size>64*1024*1024:raise ValueError("Unexpected CDS CSV archive")
            data=archive.read(members[0])
    return data.decode("utf-8-sig"),dict(dataset="reanalysis-era5-land-timeseries",variable=variable,job_id=job,
                                      request=cds_payload(variable,station),url=endpoint)


def cds_csv(text,variable,start,end):
    from .climate_products import csv_rows
    reader=csv_rows(text)
    columns=reader.fieldnames or []
    time_column=next((k for k in ("time","valid_time","date") if k in columns),None)
    data_column=next((k for k in CDS_COLUMNS[variable] if k in columns),None)
    if not time_column or not data_column:raise ValueError("Unrecognized CDS CSV columns; no values were inferred")
    values={}
    for row in reader:
        timestamp=row[time_column].replace(" ","T")[:19]
        if not (str(start)<=timestamp[:10]<=str(end)):continue
        try:value=float(row[data_column])
        except (ValueError,TypeError):continue
        if not h.valid(value):continue
        if timestamp in values:raise ValueError("Duplicate CDS hourly timestamp")
        values[timestamp]=value
    return values


def daily_from_cds(hourly,required):
    """UTC 24-hour coverage; scalar means, circular directions, totals in SI."""
    result={};dates=sorted(set(t[:10] for values in hourly.values() for t in values))
    for day in dates:
        stamps=[day+"T%02d:00:00"%hour for hour in range(24)]
        for p in required:
            variable=LAND_MAPPING.get(p)
            if not variable:continue
            dependencies=[variable]
            if p=="RH2M":dependencies.append("2m_temperature")
            if p in ("WS10M","WD10M"):dependencies.append("10m_v_component_of_wind")
            if any(any(t not in hourly.get(v,{}) for t in stamps) for v in dependencies):continue
            values=[hourly[variable][t] for t in stamps]
            if p in ("T2M","T2M_MAX","T2M_MIN","T2MDEW","TS"):
                operation=max if p=="T2M_MAX" else min if p=="T2M_MIN" else lambda a:sum(a)/24.
                value=operation(values)-273.15
            elif p=="PS":value=sum(values)/24./1000. # Pa -> kPa
            elif p=="PRECTOTCORR":
                if any(v<0 for v in values):continue
                value=sum(values)*1000. # ARCO de-accumulated metres -> mm/day
            elif p=="ALLSKY_SFC_SW_DWN":value=sum(values)/1e6 # ARCO hourly J/m2 -> daily MJ/m2
            elif p in ("WS10M","WD10M"):
                vector=[(hourly["10m_u_component_of_wind"][t],hourly["10m_v_component_of_wind"][t]) for t in stamps]
                if p=="WS10M":value=sum(math.hypot(u,v) for u,v in vector)/24.
                else:
                    bearings=[math.atan2(-u,-v) for u,v in vector if math.hypot(u,v)>1e-10]
                    if len(bearings)!=24:continue
                    x=sum(math.cos(a) for a in bearings);y=sum(math.sin(a) for a in bearings)
                    if math.hypot(x,y)<1e-10:continue
                    value=math.degrees(math.atan2(y,x))%360.
            elif p=="RH2M":
                rh=[]
                for t in stamps:
                    dew=hourly[variable][t]-273.15;temp=hourly["2m_temperature"][t]-273.15
                    rh.append(min(100.,max(0.,100.*math.exp(17.625*dew/(243.04+dew)-17.625*temp/(243.04+temp)))))
                value=sum(rh)/24.
            else:continue
            result.setdefault(p,{})[day]=value
    return result


def protected_fetch(provider,station,start,end,required,credentials,cancelled):
    import requests
    if provider==CDS:
        token=credentials.get("token","");variables=set(LAND_MAPPING[p] for p in required if p in LAND_MAPPING)
        if "RH2M" in required:variables.add("2m_temperature")
        if any(p in required for p in ("WS10M","WD10M")):variables.add("10m_v_component_of_wind")
        hourly={};raw=[];urls=[]
        with requests.Session() as session:
            for variable in sorted(variables):
                try:text,metadata=cds_download(variable,station,token,cancelled,session)
                except h.Cancelled:raise
                except requests.RequestException:raise ValueError("CDS connection failed; retry or inspect the CDS request dashboard")
                hourly[variable]=cds_csv(text,variable,start,end)
                raw.append(dict(metadata=metadata,hourly_selected=hourly[variable]));urls.append(metadata["url"])
        return dict(series=daily_from_cds(hourly,required),raw=raw,urls=urls,warnings=["CDS ARCO accumulations are already hourly de-accumulated. Only complete UTC days are aggregated."])
    if provider!=IMERG:raise ValueError("Unknown protected source")
    username,password=credentials.get("username",""),credentials.get("password","")
    if not username or not password:raise ValueError("Need Sign In: enter your NASA Earthdata username/password; authorize NASA GES DISC in Earthdata")
    class EarthdataSession(requests.Session):
        def rebuild_auth(self,prepared_request,response):
            hosts=("gpm1.gesdisc.eosdis.nasa.gov","urs.earthdata.nasa.gov")
            if urlparse(prepared_request.url).scheme=="https" and urlparse(prepared_request.url).hostname in hosts and urlparse(response.request.url).hostname in hosts:
                prepared_request.prepare_auth((username,password))
            else:super(EarthdataSession,self).rebuild_auth(prepared_request,response)
    series={};raw=[];urls=[]
    with EarthdataSession() as session:
        session.auth=(username,password)
        for day in h.days(start,end):
            if cancelled():raise h.Cancelled("Cancelled")
            when=h.date(day);ordinal=when.timetuple().tm_yday
            base="https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDF.07/%04d/%03d/3B-DAY.MS.MRG.3IMERG.%s-S000000-E235959.V07B.nc4"%(when.year,ordinal,when.strftime("%Y%m%d"))
            x=min(3599,int(math.floor((station["longitude"]+180)*10)));y=min(1799,int(math.floor((station["latitude"]+90)*10)))
            if not(0<=x<=3599 and 0<=y<=1799):raise ValueError("Invalid IMERG cell")
            if "PRECTOTCORR" not in required:break
            try:
                response=session.get(base+".das",timeout=(15,60),stream=True)
                if response.status_code in (401,403):raise ValueError("NASA sign-in/authorization required; check the account and GES DISC authorization")
                if response.status_code==404:continue
                if response.status_code!=200:raise ValueError("IMERG metadata unavailable (HTTP %s)"%response.status_code)
                metadata=read_bounded(response).decode("utf-8")
                block=re.search(r"\bprecipitation\s*\{(.*?)\}",metadata,re.S)
                if not block or not re.search(r'"mm\s*/\s*day"',block.group(1)):raise ValueError("Unexpected IMERG precipitation units; no conversion was inferred")
                url=base+".ascii?precipitation[0][%d][%d]"%(x,y)
                response=session.get(url,timeout=(15,60),stream=True)
                if response.status_code!=200:raise ValueError("IMERG point response unavailable (HTTP %s)"%response.status_code)
                text=read_bounded(response).decode("utf-8")
                match=re.search(r"precipitation\[[^\n]+\n\s*(?:\[[0-9\]\[, ]+\]\s*,?\s*)?([-+0-9.eE]+)",text)
                if not match:raise ValueError("Unrecognized IMERG scalar response")
                value=float(match.group(1));raw.append(dict(url=url,das=metadata,response=text))
                if value>=0 and not math.isnan(value) and not math.isinf(value):series.setdefault("PRECTOTCORR",{})[day]=value
                urls.append(url)
            except requests.RequestException:raise ValueError("NASA connection failed; retry the selected IMERG request")
    return dict(series=series,raw=raw,urls=urls,warnings=[])
