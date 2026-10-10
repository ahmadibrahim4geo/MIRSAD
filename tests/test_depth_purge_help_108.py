# -*- coding: utf-8 -*-
"""Tests for classified display rasters (.lyr with real colors), purge-cache
behavior, add-to-map skip outside ArcMap, and embedded Tool Help.
Runs on ArcMap 10.x python."""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt"))
TMP = os.path.join(BASE, "DepthTest_TMP")

mod = type(sys)("mdepth")
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
arcpy.env.overwriteOutput = True
tool = mod.PowerClimateAtlasGenerator()
msgs, warns = [], []

# ---------------- 1. embedded help + params ----------------
check("tool help docstring", len((mod.PowerClimateAtlasGenerator.__doc__ or "")) > 800,
      len(mod.PowerClimateAtlasGenerator.__doc__ or ""))
for key in ["DATA SOURCES", "OUTPUT LAYOUT", "PERFORMANCE", "SCIENTIFIC NOTES"]:
    check("help has " + key, key in (mod.PowerClimateAtlasGenerator.__doc__ or ""))
ps = tool.getParameterInfo()
check("46 params", len(ps) == 46, len(ps))
check("all params documented", all((p.description or "").strip() for p in ps),
      [p.name for p in ps if not (p.description or "").strip()])
pdict = dict((p.name, p) for p in ps)
check("purge default True", pdict["Purge_Cache"].value is True, pdict["Purge_Cache"].value)
check("add-to-map default True", pdict["Add_To_Map"].value is True
      and (pdict["Add_To_Map"].description or "").strip() != "", pdict["Add_To_Map"].value)
check("download-only default False", pdict["Download_Only"].value is False
      and (pdict["Download_Only"].description or "").strip() != "", pdict["Download_Only"].value)
pdict["Download_Only"].value = True
tool.updateParameters(ps)
raster_param_names = [
    "Interpolation_Method", "IDW_Curve_Profile", "IDW_Power", "IDW_Search_Type",
    "IDW_Num_Points", "IDW_Max_Distance", "Krig_Model", "Krig_Type", "Krig_Num_Points",
    "Spline_Type", "Spline_Weight", "Spline_Num_Points", "Base_Cell_Size",
    "Wind_Factor_Cell_Size", "Create_Isobars", "Pressure_Interval_Scheme",
    "Custom_Pressure_Step", "Focal_Smoothing", "Focal_Statistic", "Focal_Neighborhood",
    "Add_To_Map", "Map_Add_Modules"
]
check("download-only disables rasters", all(pdict[n].enabled is False for n in raster_param_names)
      and pdict["Climate_Data_Source"].enabled is True and pdict["Point_Tolerance"].enabled is True)
pdict["Download_Only"].value = False
tool.updateParameters(ps)

# ---------------- 2. classified display builder ----------------
arcpy.CheckOutExtension("Spatial")
if os.path.isdir(TMP):
    shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
sp = arcpy.SpatialReference(4326)
fc = "in_memory/dpx_a"
for o in (fc, "pwr_dpx_lyr"):
    try:
        arcpy.management.Delete(o)
    except Exception:
        pass
arcpy.management.CreateFeatureclass("in_memory", "dpx_a", "POINT", spatial_reference=sp)
arcpy.management.AddField(fc, "ZV", "DOUBLE")
with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "ZV"]) as cur:
    for i, (x, y) in enumerate([(30.0, 30.0), (32.0, 30.0), (31.0, 32.0),
                                (30.5, 30.5), (31.5, 31.5)]):
        cur.insertRow([(x, y), 10.0 + i * 5.0])
arcpy.management.MakeFeatureLayer(fc, "pwr_dpx_lyr")
rd = os.path.join(TMP, "Rasters")
ld = os.path.join(TMP, "Layers")
os.makedirs(rd)
os.makedirs(ld)
rp = os.path.join(rd, "T_Annual_Mean.tif")
tool._interp_surface("pwr_dpx_lyr", "ZV", 0.5, "IDW").save(rp)
colors = mod.COLOR_RAMPS["Temperature"]
cls_rp, clr_path = tool._build_display(rp, "T_Annual_Mean", "Temperature", colors, 7,
                                       msgs.append, warns.append)
check("display raster built", cls_rp and os.path.isfile(cls_rp), cls_rp)
check("clr sidecar 7 classes", clr_path and os.path.isfile(clr_path), clr_path)
if clr_path and os.path.isfile(clr_path):
    lines = open(clr_path).read().strip().splitlines()
    okclr = len(lines) == 7 and all(len(ln.split()) == 4 for ln in lines) \
        and lines[0].startswith("1 ") and lines[-1].startswith("7 ")
    check("clr content valid", okclr, lines[0] if lines else "")
check("display VAT exists", os.path.isfile(cls_rp + ".vat.dbf"),
      os.path.isfile(cls_rp + ".vat.dbf"))
lp = os.path.join(ld, "T_Annual_Mean.lyr")
brks = mod.equal_interval_breaks(10.0, 35.0, 7)
tool._make_lyr(cls_rp, lp, "T_Annual_Mean", "Temperature", colors, 7, "IDW",
               msgs.append, warns.append, brks, rp)
import json as _json
meta = _json.loads(open(lp + ".json", "rb").read().decode("utf-8"))
check("lyr on display + sidecar", os.path.isfile(lp)
      and meta.get("display_raster") == "T_Annual_Mean_cls.tif"
      and meta.get("source_raster") == "T_Annual_Mean.tif"
      and len(meta.get("breaks", [])) == 8, meta.get("display_raster"))
lyr = arcpy.mapping.Layer(lp)
check("display lyr loads unbroken", lyr.isBroken is False
      and os.path.isfile(lyr.dataSource), lyr.dataSource)
check("lyr named as raster", lyr.name == "T_Annual_Mean", lyr.name)
# descending: first clr row = hottest ramp color, last row = coldest
hot = mod.hex_to_rgb(colors[-1])
cold = mod.hex_to_rgb(colors[0])
check("clr descending colors", lines[0] == "1 %d %d %d" % hot
      and lines[-1] == "7 %d %d %d" % cold, (lines[0], lines[-1]))
# descending labels: Class 1 = highest interval, Class 7 = lowest
cl = meta.get("class_labels", [])
check("labels descending", len(cl) == 7 and cl[0].startswith("Class 1:")
      and cl[-1].startswith("Class 7:")
      and ("%.4g" % brks[-1]) in cl[0] and ("%.4g" % brks[0]) in cl[-1],
      (cl[0] if cl else "", cl[-1] if cl else ""))
# display zones remapped 1(high)..7(low): min 1, max 7
_dmn = float(arcpy.GetRasterProperties_management(cls_rp, "MINIMUM")[0])
_dmx = float(arcpy.GetRasterProperties_management(cls_rp, "MAXIMUM")[0])
check("display zones 1..7", _dmn == 1.0 and _dmx == 7.0, (_dmn, _dmx))
# pdict dynamic sync between Climate_Modules and Map_Add_Modules
_vals = [v.strip().strip("'\"") for v in str(pdict["Map_Add_Modules"].value).split(";") if v.strip()]
check("map modules syncs active module", _vals == ["Temperature"], _vals)
pdict["Climate_Modules"].values = mod.MODULES_ALL
tool.updateParameters(ps)
_vals_all = [v.strip().strip("'\"") for v in str(pdict["Map_Add_Modules"].value).split(";") if v.strip()]
check("map modules syncs all when all chosen", set(_vals_all) == set(mod.MODULES_ALL), _vals_all)
pdict["Add_To_Map"].value = False
tool.updateParameters(ps)
check("map modules hidden when addmap off", pdict["Map_Add_Modules"].enabled is False)
pdict["Add_To_Map"].value = True
tool.updateParameters(ps)
check("map modules shown when addmap on", pdict["Map_Add_Modules"].enabled is True)
arcpy.CheckInExtension("Spatial")

# ---------------- 3. add-to-map skips gracefully outside ArcMap ----------------
warns[:] = []
try:
    tool._add_to_map([], [], ["Temperature"], msgs.append, warns.append)
    skipped = any("not running inside ArcMap" in w for w in warns)
    check("add-to-map headless skip", skipped, warns[-1][:80] if warns else "no warn")
except Exception as ex:
    check("add-to-map headless skip", False, str(ex)[:120])

# ---------------- 4. purge behavior ----------------
sdir = os.path.join(TMP, "_scratch")
os.makedirs(sdir)
open(os.path.join(sdir, "junk.tif"), "wb").write("x")
tool._cleanup(msgs.append, sdir, True)
check("purge removes scratch", not os.path.isdir(sdir))
os.makedirs(sdir)
open(os.path.join(sdir, "junk.tif"), "wb").write("x")
tool._cleanup(msgs.append, sdir, False)
check("no-purge keeps scratch", os.path.isfile(os.path.join(sdir, "junk.tif")))
shutil.rmtree(TMP, ignore_errors=True)

print("")
print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
