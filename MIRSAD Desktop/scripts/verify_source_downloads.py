"""Small real provider requests; preserve evidence, no user datasets modified."""
import datetime as dt
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent))
from mirsad_core import hybrid_pipeline as h
from mirsad_core.station_catalogue import load_shared_catalogue

row=next(s for s in load_shared_catalogue(str(ROOT.parent/"data/stations.sqlite"))["EG"]
         if s["Station_ID"]=="623660" and s["WBAN"]=="99999")
station=dict(station_key=row["Station_Key"],usaf=row["Station_ID"],wban=row["WBAN"],latitude=row["Lat"],longitude=row["Lon"])
report=[]
for source,model in [("NOAA GSOD","native"),("Open-Meteo","era5_land"),("Open-Meteo","era5_seamless"),("Open-Meteo","era5")]:
    try:
        r=h.fetch_source(source,station,dt.date(2024,1,1),dt.date(2024,1,2),list(h.OM_DAILY)+list(h.OM_HOURLY),model,None,lambda:False)
        item=dict(source=source,model=model,counts={k:len(v) for k,v in r["series"].items()},urls=r["urls"],warnings=r["warnings"])
        assert item["counts"].get("T2M")==2,item
    except Exception as exc:
        item=dict(source=source,model=model,error=str(exc))
    print(json.dumps(item),flush=True)
    report.append(item)
(ROOT/".test-output/standalone-live.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
if any("error" in r for r in report):sys.exit(1)
