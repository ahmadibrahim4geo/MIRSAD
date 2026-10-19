"""Live Hybrid barrier, raw-data and export checks; use the independent runtime."""
import datetime as dt
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.catalogue import Catalogue
from mirsad_desktop import climate
from mirsad_desktop.services import run_climate_project

target=ROOT/".test-output/hybrid-live"
target.mkdir(exist_ok=True)
catalogue=Catalogue()
stations=[s for s in catalogue.stations("EG") if s["usaf"] in ("623660","623180") and s["wban"]=="99999"][:2]
assert len(stations)==2
events=[]
def progress(value):
    if isinstance(value,dict):
        events.append(value)
    print(str(value)[:180],flush=True)

records,errors,urls=climate.download(stations,dt.date(2024,1,1),dt.date(2024,1,31),"Hybrid",
    ["Temperature","Precipitation","UV Index"],target/"cache",progress,lambda:False,om_model="era5")
order=[e["stage"] for e in events]
assert order==sorted(order,key=("NOAA GSOD","Open-Meteo","NASA POWER").index)
assert not errors,errors
assert all(rec["provenance"].get("T2M") for rec in records)
assert any(any("NOAA" in source for values in rec["provenance"].values() for source in values.values()) for rec in records)
name="Desktop_"+str(time.time_ns())
output,manifest=run_climate_project(stations,target,name,catalogue.metadata(),dt.date(2024,1,1),dt.date(2024,1,31),
    "Hybrid",["Temperature","Precipitation","UV Index"],gap_method="climatological",progress=progress)
assert (output/"Project.gdb").exists()
assert (output/"Project.gpkg").exists()
assert list((output/"Raw_Data").glob("*-monthly-estimates.json"))
assert list((output/"Raw_Data").glob("*-summary.json"))
report=dict(passed=manifest["status"]=="complete",events=events,output=str(output),status=manifest["status"],errors=manifest["errors"],
    sources=[dict(station_key=r["station"]["station_key"],source_summary=r["source_summary"],missing_counts=r["missing_counts"],
                  source_events=r["source_events"],warnings=r["warnings"]) for r in records])
(target/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("LIVE REPORT",report["passed"],flush=True)
raise SystemExit(0 if report["passed"] else 1)
