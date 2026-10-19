"""One public Cairo point, one month, all provider-supported module groups."""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.catalogue import Catalogue
from mirsad_desktop.registry import MODULES,unavailable
from mirsad_desktop.services import run_climate_project

parser=argparse.ArgumentParser();parser.add_argument("--provider",choices=["NASA POWER","Open-Meteo ERA5"],required=True);args=parser.parse_args()
catalogue=Catalogue();station=next(s for s in catalogue.stations("EG") if s["usaf"]=="623660")
modules=[m.name for m in MODULES if not unavailable(args.provider,m.name)]
name="Live_Expanded_"+args.provider.split()[0]
output,manifest=run_climate_project([station],ROOT/".test-output",name,catalogue.metadata(),dt.date(2024,1,1),dt.date(2024,1,31),args.provider,modules,
    progress=lambda m:print(m.get("message","") if isinstance(m,dict) else m,flush=True),crs="EPSG:32636")
if len(manifest["outputs"].get("Project.gdb",[]))!=len(modules)+1:raise RuntimeError("Incomplete FileGDB layer export")
if any(error.get("output") for error in manifest["errors"]):raise RuntimeError(json.dumps(manifest["errors"]))
from openpyxl import load_workbook
book=load_workbook(output/"Temperature.xlsx",read_only=True,data_only=True)
rows=list(book["Daily"].values)[1:];book.close()
if not rows or not all(row[-1] is not None for row in rows):raise RuntimeError("Temperature daily values missing")
print("PASS:",args.provider,"module groups",len(modules),"scientific status",manifest["status"],"flags",len(manifest["errors"]))
print(output)
