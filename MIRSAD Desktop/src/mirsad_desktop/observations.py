"""NOAA GSOD daily observations derived from ISD; raw flags remain in the response.

Reference: NCEI global-summary-of-the-day/doc/readme.txt. Incomplete rainfall
reports, including H/I (zero without a complete report), are never treated as zero.
"""
import csv
import datetime as dt
import io
import math

REFERENCE="https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt"
BASE="https://www.ncei.noaa.gov/data/global-summary-of-the-day/access"
FIELDS={"TEMP":("T2M",9999.9,lambda v:(v-32)*5/9),
        "MAX":("T2M_MAX",9999.9,lambda v:(v-32)*5/9),
        "MIN":("T2M_MIN",9999.9,lambda v:(v-32)*5/9),
        "DEWP":("T2MDEW",9999.9,lambda v:(v-32)*5/9),
        "SLP":("SLP",9999.9,lambda v:v/10),
        "STP":("PS",9999.9,lambda v:v/10),
        "WDSP":("WS10M",999.9,lambda v:v*0.5144444444444445),
        "PRCP":("PRECTOTCORR",99.99,lambda v:v*25.4)}


def station_id(station):
    usaf,wban=str(station.get("usaf","")),str(station.get("wban",""))
    if station.get("point_type") in ("User point","Grid point"):return None
    return usaf+wban if len(usaf)==6 and usaf.isdigit() and len(wban)==5 and wban.isdigit() else None


def parse_gsod(text,station,start,end,required):
    identifier=station_id(station)
    result={p:{} for p in required if p in {v[0] for v in FIELDS.values()}}
    rejected=0;seen=set()
    for row in csv.DictReader(io.StringIO(text)):
        if row.get("STATION","").strip()!=identifier:raise ValueError("NOAA station identifier mismatch")
        day=dt.date.fromisoformat(row["DATE"])
        if not start<=day<=end:continue
        if day in seen:raise ValueError("Duplicate NOAA station/day")
        seen.add(day)
        lat,lon=float(row["LATITUDE"]),float(row["LONGITUDE"])
        if not math.isfinite(lat+lon) or abs(lat-station["latitude"])>.05 or abs(lon-station["longitude"])>.05:
            rejected+=1;continue
        for source,(target,sentinel,convert) in FIELDS.items():
            if target not in result:continue
            count=row.get(source+"_ATTRIBUTES")
            if source in ("TEMP","DEWP","SLP","STP","WDSP") and count is not None:
                try:
                    if int(count.strip())<=0:continue
                except ValueError:continue
            try:value=float(row.get(source,""))
            except (TypeError,ValueError):continue
            if not math.isfinite(value) or value==sentinel:continue
            if source=="PRCP" and (value<0 or row.get("PRCP_ATTRIBUTES","").strip() not in ("D","F","G")):continue
            result[target][day]=convert(value)
    return result,rejected


def fetch_observations(session,station,start,end,required,cancelled):
    identifier=station_id(station)
    result={};raw={};urls=[];warnings=[]
    if not identifier:return result,raw,urls,["No catalogue USAF/WBAN observation identity; reanalysis/satellite data only."]
    for year in range(start.year,end.year+1):
        if cancelled():raise InterruptedError("Cancelled")
        url=f"{BASE}/{year}/{identifier}.csv"
        try:
            with session.get(url,timeout=(15,60),stream=True) as response:
                if response.status_code==404:
                    warnings.append(f"NOAA GSOD has no {year} file for {identifier}.");continue
                response.raise_for_status();data=bytearray()
                for chunk in response.iter_content(65536):
                    if cancelled():raise InterruptedError("Cancelled")
                    data.extend(chunk)
                    if len(data)>4*1024*1024:raise ValueError("NOAA station/year response exceeds 4 MB")
            text=data.decode("utf-8-sig")
            parsed,rejected=parse_gsod(text,station,start,end,required)
            raw[str(year)]=text;urls.append(url)
            for p,values in parsed.items():result.setdefault(p,{}).update(values)
            if rejected:warnings.append(f"NOAA {year}: {rejected} records excluded because coordinates differ from selected catalogue location by more than 0.05 degrees; no coordinate correction applied.")
        except InterruptedError:raise
        except Exception as exc:warnings.append(f"NOAA {year}: {exc}")
    return result,raw,urls,warnings
