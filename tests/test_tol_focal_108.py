# -*- coding: utf-8 -*-
"""Tests for Point Tolerance (unit parsing + thinning) and Focal Statistics
(real SA execution + dynamic enabling). Runs on ArcMap 10.x python."""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt"))
TMP = os.path.join(BASE, "tests", ".output", "tolerance")
if not os.path.isdir(os.path.dirname(TMP)):
    os.makedirs(os.path.dirname(TMP))

mod = type(sys)("mtf")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = ("PASS " if cond else "FAIL ") + name
    if detail != "":
        line += " | " + str(detail)
    print(line)

# ---------------- 1. tolerance unit parsing ----------------
check("meters", mod.tolerance_meters("1000 Meters") == 1000.0)
check("kilometers", mod.tolerance_meters("2 Kilometers") == 2000.0)
check("feet", abs(mod.tolerance_meters("100 Feet") - 30.48) < 1e-9)
check("miles", abs(mod.tolerance_meters("1 Mile") - 1609.34) < 1e-9)
check("decimal degrees", abs(mod.tolerance_meters("0.5 DecimalDegrees") - 55660.0) < 1e-9)
check("zero off", mod.tolerance_meters("0 Meters") == 0.0)
check("none off", mod.tolerance_meters(None) == 0.0)
check("blank off", mod.tolerance_meters("") == 0.0)

# ---------------- 2. thinning logic ----------------
pts = [{"oid": 1, "lat": 30.0, "lon": 31.0},
       {"oid": 2, "lat": 30.0, "lon": 31.001},   # ~96m east -> merged at 200m
       {"oid": 3, "lat": 31.0, "lon": 32.0},     # far -> kept
       {"oid": 4, "lat": 30.0, "lon": 31.0}]     # exact duplicate -> merged
kept, dropped = mod.thin_points_tolerance(pts, 200.0)
check("thin keeps first + far", [p["oid"] for p in kept] == [1, 3],
      [p["oid"] for p in kept])
check("thin drops near+dup", dropped == [2, 4], dropped)
kept0, dropped0 = mod.thin_points_tolerance(pts, 0.0)
check("tol 0 keeps all", len(kept0) == 4 and dropped0 == [])
kept1, _ = mod.thin_points_tolerance([pts[0]], 200.0)
check("single point kept", len(kept1) == 1)

# ---------------- 3. params + dynamic focal enabling ----------------
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True
tool = mod.PowerClimateAtlasGenerator()
ps = tool.getParameterInfo()
check("69 point parameters", len(ps) == 69, len(ps))
pdict = dict((p.name, p) for p in ps)
check("tol default 0 Meters", "0" in str(pdict["Point_Tolerance"].value), pdict["Point_Tolerance"].value)
check("focal defaults", pdict["Focal_Smoothing"].value is False and pdict["Focal_Statistic"].value == "MEAN"
      and pdict["Focal_Neighborhood"].value == 3, (pdict["Focal_Smoothing"].value, pdict["Focal_Statistic"].value, pdict["Focal_Neighborhood"].value))
pdict["Focal_Smoothing"].value = False
tool.updateParameters(ps)
check("focal off disables", pdict["Focal_Statistic"].enabled is False and pdict["Focal_Neighborhood"].enabled is False)
pdict["Focal_Smoothing"].value = True
tool.updateParameters(ps)
check("focal on enables", pdict["Focal_Statistic"].enabled is True and pdict["Focal_Neighborhood"].enabled is True)

# ---------------- 4. real focal execution ----------------
arcpy.CheckOutExtension("Spatial")
if os.path.isdir(TMP):
    shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
sp = arcpy.SpatialReference(4326)
arcpy.management.CreateFeatureclass("in_memory", "tfx", "POINT", spatial_reference=sp)
arcpy.management.AddField("in_memory/tfx", "ZV", "DOUBLE")
with arcpy.da.InsertCursor("in_memory/tfx", ["SHAPE@XY", "ZV"]) as cur:
    for i, (x, y) in enumerate([(30.0, 30.0), (32.0, 30.0), (31.0, 32.0),
                                (30.5, 30.5), (31.5, 31.5), (31.0, 30.5)]):
        cur.insertRow([(x, y), 10.0 + i * 5.0 + (30.0 if i == 2 else 0.0)])  # spike at #3
arcpy.management.MakeFeatureLayer("in_memory/tfx", "pwr_tfx_lyr")
from arcpy.sa import FocalStatistics, NbrRectangle
base = os.path.join(TMP, "base.tif")
tool._interp_surface("pwr_tfx_lyr", "ZV", 0.2, "IDW").save(base)
spike_before = float(arcpy.GetRasterProperties_management(base, "MAXIMUM")[0])
sm = os.path.join(TMP, "smooth.tif")
FocalStatistics(arcpy.Raster(base), NbrRectangle(3, 3, "CELL"), "MEAN").save(sm)
spike_after = float(arcpy.GetRasterProperties_management(sm, "MAXIMUM")[0])
check("focal dampens spike", spike_after < spike_before, (spike_before, spike_after))
check("focal keeps extent", arcpy.Describe(sm).extent.XMin == arcpy.Describe(base).extent.XMin)
arcpy.CheckInExtension("Spatial")
shutil.rmtree(TMP, ignore_errors=True)

print("")
print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
