"""Live provider/model and native regional-download acceptance; disposable output."""
import datetime as dt
import json
from pathlib import Path
import sys
import time
import shutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.catalogue import Catalogue
from mirsad_desktop.climate import fetch_series
from mirsad_desktop.registry import MODULES
from mirsad_desktop.regional import run_regional_project
import requests

target=ROOT/".test-output/rework-live"
target.mkdir(exist_ok=True)
catalogue=Catalogue()
station=next(s for s in catalogue.stations("EG") if s["usaf"]=="623660" and s["wban"]=="99999")
checks=[]
with requests.Session() as session:
    for provider,model,modules in [("Open-Meteo ERA5",m,[item.name for item in MODULES]) for m in ("era5","era5_land","era5_seamless")]+[
            ("NASA POWER","era5",[m.name for m in MODULES]),("Hybrid","era5_land",["Temperature","Precipitation","UV Index"])]:
        started=time.perf_counter()
        try:
            series,url,raw=fetch_series(session,station,dt.date(2024,1,1),dt.date(2024,1,3),provider,lambda:False,modules,model)
            counts={p:sum(v is not None for v in values.values()) for p,values in series.items()}
            assert any(counts.values()),"No usable values"
            name=provider.replace(" ","_")+"_"+model
            (target/(name+".json")).write_text(json.dumps(raw),encoding="utf-8")
            checks.append(dict(provider=provider,model=model,valid_values=counts,url=url,seconds=time.perf_counter()-started,passed=True))
        except Exception as exc:checks.append(dict(provider=provider,model=model,passed=False,error=str(exc)))
        print(json.dumps(checks[-1]),flush=True)
from shapely.geometry import box,mapping
try:
    name="Regional_Live"
    # Preserve previous successful evidence instead of overwriting a project.
    if not (target/name).exists():
        output,manifest=run_regional_project(target,name,catalogue.metadata(),mapping(box(30.5,29.5,31.5,30.5)),mapping(box(30.7,29.7,31.3,30.3)),
            dt.date(2024,1,1),dt.date(2024,1,31),["Temperature"],raster_options=dict(crs="EPSG:32636",cell_size=10000,pdf=True,fields=["T_January_Mean"],reclass_enabled=True),
            monthly_rasters=True,progress=lambda v:print(str(v)[:150],flush=True))
        checks.append(dict(provider="NASA POWER Regional Grid",passed=manifest["status"]=="complete",errors=manifest["errors"],output=str(output)))
    else:checks.append(dict(provider="NASA POWER Regional Grid",passed=json.loads((target/name/"manifest.json").read_text())["status"]=="complete",output=str(target/name)))
except Exception as exc:checks.append(dict(provider="NASA POWER Regional Grid",passed=False,error=str(exc)))
report=dict(checks=checks,passed=all(c["passed"] for c in checks))
(target/"network_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("PASSED",report["passed"],flush=True)
sys.exit(0 if report["passed"] else 1)
