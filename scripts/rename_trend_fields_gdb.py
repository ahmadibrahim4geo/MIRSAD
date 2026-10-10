# -*- coding: utf-8 -*-
"""Rename annual/seasonal/monthly TREND fields in the GDB layer (values kept).

Old -> new (anomaly names untouched):
  T_Trend_Decade/R_Trend_Decade -> T/R_Annual_Trend_Decade
  T/R_Trend_<Season>            -> T/R_<Season>_Trend_Decade
  T/R_Trend_<Month>             -> T/R_<Month>_Trend_Decade
  T/R_Trend_Month               -> T/R_Month_Trend_Decade
Alias of every renamed field = the new field name (Latin).
"""
import arcpy

BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
FC = BASE + r"\Climate_Database_From_1996_To_2025.gdb\Trends_And_Anomalies"

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

have = set(f.name for f in arcpy.ListFields(FC))
for old, new in pairs:
    if old not in have:
        print("SKIP (absent): %s" % old)
        continue
    if new in have:
        print("SKIP (target exists): %s" % new)
        continue
    arcpy.management.AlterField(FC, old, new, new)
    print("renamed %s -> %s" % (old, new))
print("done")
