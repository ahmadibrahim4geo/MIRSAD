"""Explicit, tiny live API check. Not part of offline unit tests."""
import argparse
import datetime as dt
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.catalogue import Catalogue
from mirsad_desktop.services import run_climate_project

parser = argparse.ArgumentParser()
parser.add_argument("--provider",choices=["NASA POWER","Open-Meteo ERA5"],required=True)
args = parser.parse_args()
catalogue = Catalogue()
station = next(row for row in catalogue.stations("EG") if row["usaf"]=="623660")
with tempfile.TemporaryDirectory(prefix="network_",dir=ROOT/".test-output") as folder:
    output,manifest = run_climate_project([station],folder,"Live_Check",catalogue.metadata(),dt.date(2024,1,1),dt.date(2024,1,2),
                                          args.provider,["Temperature","Precipitation"],progress=print)
    (ROOT/".test-output"/("network_"+args.provider.split()[0]+".json")).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    if manifest["status"] != "complete": raise SystemExit(json.dumps(manifest["errors"]))
    from openpyxl import load_workbook
    for module in ("Temperature","Precipitation"):
        book = load_workbook(output/(module+".xlsx"),read_only=True,data_only=True)
        all_rows=list(book["Daily"].values)
        variable="T2M" if module=="Temperature" else "PRECTOTCORR"
        rows=[row for row in all_rows[1:] if row[all_rows[0].index("Variable")]==variable]
        if len(rows) != 2 or any(row[-1] is None for row in rows):
            raise RuntimeError("Live API did not return two valid daily values: "+module)
        book.close()
    print("Live network and dual-export check passed:",args.provider)
