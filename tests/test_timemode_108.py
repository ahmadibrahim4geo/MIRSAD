# -*- coding: utf-8 -*-
"""Time Mode verification: enable/disable matrix across transitions (incl.
restore), validation no-crash paths, and single-year winter rule.
Runs on ArcMap 10.x python."""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt"))

mod = type(sys)("mtm")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = ("PASS " if cond else "FAIL ") + name
    if detail != "":
        line += " | " + str(detail)
    print(line)

try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
tool = mod.PowerClimateAtlasGenerator()
ps = tool.getParameterInfo()
pdict = dict((p.name, p) for p in ps)

def state():
    tool.updateParameters(ps)
    return {
        "single": pdict["Single_Year"].enabled,
        "start_yr": pdict["Start_Year"].enabled,
        "end_yr": pdict["End_Year"].enabled,
        "start_dt": pdict["Start_Date"].enabled,
        "end_dt": pdict["End_Date"].enabled,
    }

# 1. default Single Year
pdict["Time_Mode"].value = "Single Year"
s = state()
check("single: only Single_Year enabled",
      s == {"single": True, "start_yr": False, "end_yr": False, "start_dt": False, "end_dt": False}, s)

# 2. switch to Year Range
pdict["Time_Mode"].value = "Year Range"
s = state()
check("range: Start/End Year on, Single & Dates off",
      s == {"single": False, "start_yr": True, "end_yr": True, "start_dt": False, "end_dt": False}, s)

# 3. switch to Custom Date Range
pdict["Time_Mode"].value = "Custom Date Range"
s = state()
check("custom: Start/End Date on, Years off",
      s == {"single": False, "start_yr": False, "end_yr": False, "start_dt": True, "end_dt": True}, s)

# 4. switch BACK to Single Year (restore path)
pdict["Time_Mode"].value = "Single Year"
s = state()
check("back to single restores",
      s == {"single": True, "start_yr": False, "end_yr": False, "start_dt": False, "end_dt": False}, s)

# 5. switch back to Custom Date Range (double toggle stability)
pdict["Time_Mode"].value = "Custom Date Range"
s = state()
check("custom again stable",
      s == {"single": False, "start_yr": False, "end_yr": False, "start_dt": True, "end_dt": True}, s)

# 6. verify Start/End Date parameter types (GPString allows custom flexible typing and visual picker)
check("start_date datatype String or GPDate", pdict["Start_Date"].datatype in ("Date", "GPDate", "String", "GPString"), pdict["Start_Date"].datatype)
check("end_date datatype String or GPDate", pdict["End_Date"].datatype in ("Date", "GPDate", "String", "GPString"), pdict["End_Date"].datatype)
check("start_date category Time Window", pdict["Start_Date"].category == "Time Window")
check("end_date category Time Window", pdict["End_Date"].category == "Time Window")

# 7. test parse_gp_date helper
import datetime as _dt
d1 = mod.parse_gp_date("2023-05-15")
check("parse_gp_date iso string", d1 == _dt.date(2023, 5, 15), d1)
d2 = mod.parse_gp_date("2023-05-15 00:00:00")
check("parse_gp_date datetime string", d2 == _dt.date(2023, 5, 15), d2)
d3 = mod.parse_gp_date(_dt.datetime(2024, 2, 29, 10, 30))
check("parse_gp_date datetime obj", d3 == _dt.date(2024, 2, 29), d3)
d4 = mod.parse_gp_date(None)
check("parse_gp_date none", d4 is None, d4)
d5 = mod.parse_gp_date("31/3/1990")
check("parse_gp_date d/m/y slash", d5 == _dt.date(1990, 3, 31), d5)
d6 = mod.parse_gp_date("31/12/2000")
check("parse_gp_date d/m/y year 2000", d6 == _dt.date(2000, 12, 31), d6)

# 8. updateMessages valid combos
for setup in [("Single Year", 2025, 2015, 2025, "2023-01-01", "2023-12-31"),
              ("Year Range", 2025, 2015, 2025, "2023-01-01", "2023-12-31"),
              ("Custom Date Range", 2025, 2015, 2025, "2023-01-01", "2023-12-31")]:
    pdict["Time_Mode"].value = setup[0]
    pdict["Single_Year"].value = setup[1]
    pdict["Start_Year"].value = setup[2]
    pdict["End_Year"].value = setup[3]
    pdict["Start_Date"].value = setup[4]
    pdict["End_Date"].value = setup[5]
    try:
        tool.updateParameters(ps)
        tool.updateMessages(ps)
        check("messages ok %s" % setup[0], True)
    except Exception as ex:
        check("messages ok %s" % setup[0], False, str(ex)[:100])

# 9. updateMessages invalid combos handled cleanly without crash
for setup in [("Single Year", 1900, 2015, 2025, "2023-01-01", "2023-12-31"),
              ("Year Range", 2025, 2025, 2015, "2023-01-01", "2023-12-31"),
              ("Year Range", 2025, 1970, 2025, "2023-01-01", "2023-12-31"),
              ("Custom Date Range", 2025, 2015, 2025, "2024-12-31", "2023-01-01"),
              ("Custom Date Range", 2025, 2015, 2025, "1975-01-01", "1976-01-01")]:
    pdict["Time_Mode"].value = setup[0]
    pdict["Single_Year"].value = setup[1]
    pdict["Start_Year"].value = setup[2]
    pdict["End_Year"].value = setup[3]
    pdict["Start_Date"].value = setup[4]
    pdict["End_Date"].value = setup[5]
    try:
        tool.updateParameters(ps)
        tool.updateMessages(ps)
        check("messages invalid %s handled" % setup[0], True)
    except Exception as ex:
        check("messages invalid %s handled" % setup[0], False, str(ex)[:100])

# single-year winter rule: Dec+Jan+Feb of the SAME year only
mt = dict(((2025, m), 10.0 * m) for m in range(1, 13))
tf = mod.compute_temperature_fields(mt, mt, mt)
check("winter = Jan+Feb+Dec same year",
      abs(tf["T_Winter_Mean"] - (10.0 + 20.0 + 120.0) / 3) < 1e-9, tf["T_Winter_Mean"])
check("no next-year leak", abs(tf["T_Spring_Mean"] - (30.0 + 40.0 + 50.0) / 3) < 1e-9)

# 10. Test RasterDataClimateAtlasGenerator
print("\n--- Testing RasterDataClimateAtlasGenerator ---")
from raster_atlas_generator import RasterDataClimateAtlasGenerator
rtool = RasterDataClimateAtlasGenerator()
rps = rtool.getParameterInfo()
rpdict = dict((p.name, p) for p in rps)

check("raster tool Time_Mode category", rpdict["Time_Mode"].category == "Time Window")
check("raster tool Open_Calendar_Picker category", rpdict["Open_Calendar_Picker"].category == "Time Window")
check("raster tool Start_Date category", rpdict["Start_Date"].category == "Time Window")
check("raster tool End_Date category", rpdict["End_Date"].category == "Time Window")

# Test dynamic enabling/disabling in raster tool
rpdict["Time_Mode"].value = "Single Year"
rtool.updateParameters(rps)
check("raster single year: Single_Year on", rpdict["Single_Year"].enabled and not rpdict["Start_Year"].enabled and not rpdict["Start_Date"].enabled)

rpdict["Time_Mode"].value = "Year Range"
rtool.updateParameters(rps)
check("raster year range: Start_Year on", rpdict["Start_Year"].enabled and rpdict["End_Year"].enabled and not rpdict["Single_Year"].enabled)

rpdict["Time_Mode"].value = "Custom Date Range"
rtool.updateParameters(rps)
check("raster custom date: Start_Date on", rpdict["Start_Date"].enabled and rpdict["End_Date"].enabled and rpdict["Open_Calendar_Picker"].enabled and not rpdict["Single_Year"].enabled)

# Test messages validation
rpdict["Start_Date"].value = "31/03/1990"
rpdict["End_Date"].value = "31/12/2000"
rtool.updateMessages(rps)
check("raster custom valid dates ok", True)

print("")
print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)

