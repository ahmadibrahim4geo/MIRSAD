# -*- coding: utf-8 -*-
"""Inject the 5 general-monthly fields into Trends_And_Anomalies GDB layer.

Fields (DOUBLE, alias = field name, same pattern as the rest):
  T_Anom_Month, R_Anom_Month, R_Anom_Month_Pct, T_Month_Trend_Decade, R_Month_Trend_Decade
Values computed from Egypt_Monthly_Raw_1996_2025.json with the tool's own
compute_trend_anomaly_fields. NO raster is produced (tables only).
"""
import csv
import json
import os
import sys
import tempfile
import shutil
from importlib.machinery import SourceFileLoader

import arcpy

ROOT = r"D:\My Software\NASA POWER Climate Atlas Generator"
BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
TABLES = os.path.join(BASE, "00_Tables_And_Reports")
GDB = os.path.join(BASE, "Climate_Database_From_1996_To_2025.gdb")
FC = os.path.join(GDB, "Trends_And_Anomalies")

FIELDS = ["T_Anom_Month", "R_Anom_Month", "R_Anom_Month_Pct",
          "T_Month_Trend_Decade", "R_Month_Trend_Decade"]

pyt = SourceFileLoader(
    "pytmod", os.path.join(ROOT, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")).load_module()

raw = json.load(open(os.path.join(TABLES, "Egypt_Monthly_Raw_1996_2025.json"),
                     "r", encoding="utf-8-sig"))
tmp = os.path.join(tempfile.gettempdir(), "opencode_oid2.xlsx")
shutil.copy(os.path.join(TABLES, "Temperature.xls"), tmp)
import openpyxl
wb = openpyxl.load_workbook(tmp, read_only=True, data_only=True)
sh = wb["Data"]
rows = list(sh.iter_rows(values_only=True))
hdr = rows[0]
o2s = {int(r[hdr.index("OBJECTID")]): int(r[hdr.index("Source_ID")])
       for r in rows[1:] if r[hdr.index("OBJECTID")] is not None}

table = {}
for pid, series in raw.items():
    try:
        sid = o2s[int(float(pid))]
    except Exception:
        continue
    mt = {}
    for k, v in series.get("T2M", {}).items():
        try:
            m = int(k[4:])
        except Exception:
            continue
        if 1 <= m <= 12:
            mt[(int(k[:4]), m)] = v
    mp = {}
    for k, v in series.get("PRECTOTCORR", {}).items():
        try:
            m = int(k[4:])
        except Exception:
            continue
        if 1 <= m <= 12:
            mp[(int(k[:4]), m)] = pyt.monthly_precip_total_from_rate(v, int(k[:4]), m)
    out = pyt.compute_trend_anomaly_fields(mt, mp)
    table[sid] = {f: out.get(f) for f in FIELDS}

have = set(f.name for f in arcpy.ListFields(FC))
for fld in FIELDS:
    if fld not in have:
        arcpy.management.AddField(FC, fld, "DOUBLE", field_alias=fld)
        print("added %s" % fld)
        sys.stdout.flush()

n_fill = 0
with arcpy.da.UpdateCursor(FC, ["Source_ID"] + FIELDS) as cur:
    for row in cur:
        try:
            sid = int(row[0])
        except Exception:
            continue
        rec = table.get(sid)
        if not rec:
            continue
        dirty = False
        for i, fld in enumerate(FIELDS, 1):
            if row[i] is None and rec.get(fld) is not None:
                row[i] = float(rec[fld])
                dirty = True
        if dirty:
            cur.updateRow(row)
            n_fill += 1
print("filled %d rows." % n_fill)
