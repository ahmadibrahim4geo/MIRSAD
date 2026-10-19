# -*- coding: utf-8 -*-
"""
Build 12-month climatology tables from Egypt_Monthly_Raw_1996_2025.json.

Uses the atlas tool's OWN formulas (compute_point_fields from
Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt) so values are bit-consistent with
the published GDB/rasters (verified: OBJECTID=1 reproduces the xls exactly).

Outputs (under 00_Tables_And_Reports):
  Monthly_Climatology/<Element>.csv  (OBJECTID, Source_ID, 12 monthly fields)
and appends the 12 monthly columns to each element's .xls table in place.

Pure-Python: runs anywhere, no arcpy. GDB + Month/ rasters are handled by
scripts/build_monthly_backfill_arcmap.py inside ArcMap.
"""

import os
import sys
import csv
import json
import shutil
import tempfile

from importlib.machinery import SourceFileLoader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
TABLES = os.path.join(BASE, "00_Tables_And_Reports")
RAW_JSON = os.path.join(TABLES, "Egypt_Monthly_Raw_1996_2025.json")
OUT_DIR = os.path.join(TABLES, "Monthly_Climatology")
YEARS = list(range(1996, 2026))
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

ELEMENTS = {
    "Temperature": ("Temperature.xls", ["Temperature"]),
    "Precipitation": ("Precipitation.xls", ["Precipitation"]),
    "Sea Level Pressure": ("Sea_Level_Pressure.xls", ["Sea Level Pressure"]),
    "Surface Pressure": ("Surface_Pressure.xls", ["Surface Pressure"]),
    "Wind": ("Wind.xls", ["Wind"]),
    "Relative Humidity": ("Relative_Humidity.xls", ["Relative Humidity"]),
    "Dew Point": ("Dew_Point.xls", ["Dew Point"]),
    "Solar Radiation": ("Solar_Radiation.xls", ["Solar Radiation"]),
    "UV Index": ("UV_Index.xls", ["UV Index"]),
    "Cloud Cover": ("Cloud_Cover.xls", ["Cloud Cover"]),
    "Evapotranspiration": ("Evapotranspiration.xls", ["Evapotranspiration"]),
}
ALL_MODULES = ["Temperature", "Precipitation", "Sea Level Pressure",
               "Surface Pressure", "Wind", "Relative Humidity", "Dew Point",
               "Solar Radiation", "UV Index", "Cloud Cover",
               "Evapotranspiration"]


def load_tool():
    return SourceFileLoader(
        "pytmod", os.path.join(ROOT, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")).load_module()


def read_coords_from_temperature_xlsx():
    """OBJECTID -> (Source_ID, lat). Temperature.xls is xlsx content."""
    import openpyxl
    tmp = os.path.join(tempfile.gettempdir(), "opencode_tcoords.xlsx")
    shutil.copy(os.path.join(TABLES, "Temperature.xls"), tmp)
    wb = openpyxl.load_workbook(tmp, read_only=True, data_only=True)
    sh = wb["Data"]
    rows = list(sh.iter_rows(values_only=True))
    hdr = rows[0]
    i_oid = hdr.index("OBJECTID")
    i_sid = hdr.index("Source_ID")
    i_lat = hdr.index("Point_Lat")
    out = {}
    for r in rows[1:]:
        if r[i_oid] is None:
            continue
        out[str(int(r[i_oid]))] = (int(r[i_sid]), float(r[i_lat]))
    return out


def main():
    pyt = load_tool()
    # monthly field list per element, in Jan..Dec order
    monthly_of_element = {}
    for mod in ALL_MODULES:
        # FIELD_DEFS order is already Jan..Dec within each prefix group
        # (Wind: 12 speed then 12 direction) - keep it untouched.
        flds = [f for f in pyt.MODULE_FIELDS.get(mod, []) if pyt.is_monthly_field(f)]
        monthly_of_element[mod] = flds
        print("%s: %d monthly fields" % (mod, len(flds)))

    raw = json.load(open(RAW_JSON, "r", encoding="utf-8-sig"))
    coords = read_coords_from_temperature_xlsx()
    print("points in raw: %d, coords: %d" % (len(raw), len(coords)))

    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    # per-point computation (single call, all modules)
    table = {}  # pid -> {field: value}
    for pid, series in raw.items():
        monthly = {}
        for param, s in series.items():
            monthly[param] = {}
            for k, v in s.items():
                try:
                    m = int(k[4:])
                except Exception:
                    continue
                if 1 <= m <= 12:
                    monthly[param][(int(k[:4]), m)] = v
        _sid, lat = coords.get(pid, (int(pid), 25.0))
        res = pyt.compute_point_fields(monthly, YEARS, ALL_MODULES, "Monthly", lat=lat)
        table[pid] = res

    # CSV per element (join key for ArcMap: Source_ID)
    for mod, (xls_name, _m) in ELEMENTS.items():
        flds = monthly_of_element[mod]
        # Wind: speed first then direction (matches FIELD_DEFS order anyway)
        csv_path = os.path.join(OUT_DIR, "%s.csv" % xls_name[:-4])
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["OBJECTID", "Source_ID"] + flds)
            for pid in sorted(table.keys(), key=int):
                sid, _lat = coords.get(pid, (int(pid), 0.0))
                w.writerow([pid, sid] + [table[pid].get(f) for f in flds])
        print("CSV: %s (%d rows)" % (csv_path, len(table)))

    # Element workbooks: monthly values live ONLY in the Month sheet, never
    # in Data (single implementation in repair_excel_month_sheets).
    sys.path.insert(0, HERE)
    import repair_excel_month_sheets as rep
    for mod, (xls_name, _m) in ELEMENTS.items():
        flds = monthly_of_element[mod]
        if xls_name == "Precipitation.xls":
            rep.repair_precipitation(pyt, table)
        else:
            rep.repair_xlsx_element(os.path.join(TABLES, xls_name), mod, flds, table)

    print("DONE.")


if __name__ == "__main__":
    main()
