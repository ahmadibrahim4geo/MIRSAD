# -*- coding: utf-8 -*-
"""Append Month sheet (60 monthly trend/anomaly fields) to Trends_And_Anomalies.xls."""
import csv
import os
from importlib.machinery import SourceFileLoader

import xlrd

BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
TABLES = os.path.join(BASE, "00_Tables_And_Reports")
XLS = os.path.join(TABLES, "Trends_And_Anomalies.xls")
CSV_PATH = os.path.join(TABLES, "Monthly_Climatology", "Trends_Monthly.csv")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MFIELDS = []
for _mn in MONTHS:
    MFIELDS += ["T_Anom_%s" % _mn, "R_Anom_%s" % _mn,
                "R_Anom_%s_Pct" % _mn, "T_Trend_%s" % _mn,
                "R_Trend_%s" % _mn]

pyt = SourceFileLoader(
    "pytmod", os.path.join(ROOT, "POWER_Climate_Atlas_Generator_10_8.pyt")).load_module()

wb = xlrd.open_workbook(XLS)
sh = wb.sheet_by_name("Data")
data_hdr = [sh.cell_value(0, c) for c in range(sh.ncols)]
data_rows = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(1, sh.nrows)]
i_oid = data_hdr.index("OBJECTID")
i_sid = data_hdr.index("Source_ID")
i_lat = data_hdr.index("Point_Lat")
i_lon = data_hdr.index("Point_Lon")

tab = {}
with open(CSV_PATH, "r", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        try:
            tab[int(float(row["Source_ID"]))] = row
        except Exception:
            pass

m_hdr = ["OBJECTID", "Source_ID", "Point_Lat", "Point_Lon"] + MFIELDS
m_rows = []
for r in data_rows:
    if r[i_oid] == "":
        continue
    sid = int(r[i_sid])
    rec = tab.get(sid, {})
    vals = []
    for f in MFIELDS:
        v = rec.get(f)
        vals.append(float(v) if v not in (None, "") else None)
    m_rows.append([r[i_oid], r[i_sid], r[i_lat], r[i_lon]] + vals)

pyt.write_master_excel_workbook(
    XLS, [("Data", data_hdr, data_rows, False), ("Month", m_hdr, m_rows, False)])
print("OK: Data %d cols x %d rows | Month %d cols x %d rows"
      % (len(data_hdr), len(data_rows), len(m_hdr), len(m_rows)))
