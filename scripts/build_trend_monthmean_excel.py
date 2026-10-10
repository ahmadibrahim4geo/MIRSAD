# -*- coding: utf-8 -*-
"""Append the 5 general-monthly columns to the Data sheet of Trends_And_Anomalies.xls."""
import os
from importlib.machinery import SourceFileLoader

import geopandas as gpd
import xlrd

ROOT = r"D:\My Software\NASA POWER Climate Atlas Generator"
BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
TABLES = os.path.join(BASE, "00_Tables_And_Reports")
XLS = os.path.join(TABLES, "Trends_And_Anomalies.xls")

F = ["T_Anom_Month", "R_Anom_Month", "R_Anom_Month_Pct",
     "T_Month_Trend_Decade", "R_Month_Trend_Decade"]

pyt = SourceFileLoader(
    "pytmod", os.path.join(ROOT, "POWER_Climate_Atlas_Generator_10_8.pyt")).load_module()

wb = xlrd.open_workbook(XLS)
parts = []
for s in wb.sheet_names():
    sh = wb.sheet_by_name(s)
    parts.append((s, [sh.cell_value(0, c) for c in range(sh.ncols)],
                  [[sh.cell_value(r, c) for c in range(sh.ncols)]
                   for r in range(1, sh.nrows)]))

lyr = gpd.read_file(os.path.join(BASE, "Climate_Database_From_1996_To_2025.gdb"),
                    layer="Trends_And_Anomalies")
gdb = {int(r["Source_ID"]): r for _, r in lyr.iterrows()}


def gval(rec, f):
    v = rec[f]
    if v is None or v != v:
        return None
    return float(v)


sheets = []
for s, h, rr in parts:
    if s == "Data":
        isi = h.index("Source_ID")
        nh = h + [f for f in F if f not in h]
        nr = []
        for r in rr:
            rec = gdb.get(int(r[isi]))
            nr.append(list(r) + [gval(rec, f) for f in F if f not in h])
        sheets.append((s, nh, nr, False))
    else:
        sheets.append((s, h, rr, False))

pyt.write_master_excel_workbook(XLS, sheets)
print("OK:", [(s, len(h)) for s, h, rr, _ in sheets])
