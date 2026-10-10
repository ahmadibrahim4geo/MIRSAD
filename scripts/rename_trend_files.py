# -*- coding: utf-8 -*-
"""Rename trend/anomaly headers in Trends_And_Anomalies.xls (Data+Month),
dictionaries, CSVs, and raster filenames (with XML sidecar patching)."""
import csv
import os

BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
TABLES = os.path.join(BASE, "00_Tables_And_Reports")
TRENDS = os.path.join(BASE, "18_Trends_And_Anomalies")

pairs = [("T_Trend_Decade", "T_Annual_Trend_Decade"),
         ("R_Trend_Decade", "R_Annual_Trend_Decade"),
         ("T_Anom_Annual", "T_Annual_Anom"),
         ("R_Anom_Annual", "R_Annual_Anom"),
         ("R_Anom_Annual_Pct", "R_Annual_Anom_Pct")]
for _s in ("Winter", "Spring", "Summer", "Autumn"):
    pairs.append(("T_Trend_%s" % _s, "T_%s_Trend_Decade" % _s))
    pairs.append(("R_Trend_%s" % _s, "R_%s_Trend_Decade" % _s))
for _m in ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"):
    pairs.append(("T_Trend_%s" % _m, "T_%s_Trend_Decade" % _m))
    pairs.append(("R_Trend_%s" % _m, "R_%s_Trend_Decade" % _m))
pairs.append(("T_Trend_Month", "T_Month_Trend_Decade"))
pairs.append(("R_Trend_Month", "R_Month_Trend_Decade"))
# longest-first so R_Anom_Annual_Pct is replaced before R_Anom_Annual
pairs.sort(key=lambda p: -len(p[0]))


def rep(t):
    for a, b in pairs:
        t = t.replace(a, b)
    return t


# --- 1. CSV headers ---
for fn in ("Trends_Monthly.csv", "Trends_Seasonal.csv"):
    p = os.path.join(TABLES, "Monthly_Climatology", fn)
    if not os.path.exists(p):
        print("skip csv", fn)
        continue
    rows = list(csv.reader(open(p, encoding="utf-8")))
    rows[0] = [rep(h) for h in rows[0]]
    with open(p, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rows)
    print("csv header renamed:", fn)

# --- 2. Trends_And_Anomalies.xls Data+Month headers (BIFF via tool writer) ---
from importlib.machinery import SourceFileLoader
import xlrd
pyt = SourceFileLoader(
    "pytmod",
    r"D:\My Software\NASA POWER Climate Atlas Generator\POWER_Climate_Atlas_Generator_10_8.pyt").load_module()
xls = os.path.join(TABLES, "Trends_And_Anomalies.xls")
wb = xlrd.open_workbook(xls)
sheets = []
for s in wb.sheet_names():
    sh = wb.sheet_by_name(s)
    h = [rep(sh.cell_value(0, c)) for c in range(sh.ncols)]
    rws = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(1, sh.nrows)]
    sheets.append((s, h, rws, False))
pyt.write_master_excel_workbook(xls, sheets)
print("xls headers renamed:", xls)

# --- 3. dictionaries (Field_Name column only) ---
for fn in ("Metadata_Dictionary.xls", "Field_Dictionary_Arabic.xls"):
    p = os.path.join(TABLES, fn)
    if not os.path.exists(p):
        print("skip dict", fn)
        continue
    try:
        wb = xlrd.open_workbook(p)
    except Exception as ex:
        print("skip dict (read):", fn, ex)
        continue
    out = []
    for s in wb.sheet_names():
        sh = wb.sheet_by_name(s)
        h = [sh.cell_value(0, c) for c in range(sh.ncols)]
        try:
            fi = h.index("Field_Name")
        except ValueError:
            try:
                fi = h.index("اسم_الحقل")
            except ValueError:
                fi = None
        rws = []
        for r in range(1, sh.nrows):
            row = [sh.cell_value(r, c) for c in range(sh.ncols)]
            if fi is not None and isinstance(row[fi], str):
                row[fi] = rep(row[fi])
            rws.append(row)
        out.append((s, h, rws, "Arabic" in s))
    pyt.write_master_excel_workbook(p, out)
    print("dict renamed:", fn)

# --- 4. raster filenames + XML sidecar contents ---
import glob
renamed = 0
for a, b in pairs:
    for pat in (a + ".tif", a + ".tfw", a + ".tif.aux.xml", a + ".tif.xml",
                a + ".tif.ovr"):
        for src in glob.glob(os.path.join(TRENDS, pat)):
            dst = os.path.join(TRENDS, os.path.basename(src).replace(a, b, 1))
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
            renamed += 1
            if dst.endswith((".xml",)):
                t = open(dst, encoding="utf-8", errors="replace").read()
                t2 = rep(t)
                if t2 != t:
                    open(dst, "w", encoding="utf-8").write(t2)
print("raster files renamed:", renamed)
print("DONE")
