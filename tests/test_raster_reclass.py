# -*- coding: utf-8 -*-
"""Unit tests for raster reclassification and color interpolation in POWER Climate Atlas Generator."""
import os
import sys
import unittest
import numpy as np

# Load the toolbox module (2/3 compatible: imp was removed in 3.12,
# and spec_from_file_location() returns None for the .pyt extension)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import importlib.machinery as _ilm

    def _load_source(_name, _path):
        return _ilm.SourceFileLoader(_name, _path).load_module()
except ImportError:  # Python 2.7 fallback
    import imp as _imp
    _load_source = _imp.load_source
_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pyt_path = os.path.join(_base, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(pyt_path):
    pyt_path = os.path.join(_base, "POWER_Climate_Atlas_Generator_10_8.pyt")
mod = _load_source("power_atlas_108", pyt_path)

passed = 0
failed = 0

def check(title, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print("PASS %s %s" % (title, ("| " + str(detail)) if detail else ""))
    else:
        failed += 1
        print("FAIL %s %s" % (title, ("| " + str(detail)) if detail else ""))

print("=== 1. Color Ramp Interpolation (interpolate_colors) ===")
base7 = ["#4575B4", "#74ADD1", "#ABD9E9", "#FFFFBF", "#FDAE61", "#F46D43", "#D73027"]

c5 = mod.interpolate_colors(base7, 5)
check("5 colors length", len(c5) == 5, len(c5))
check("5 colors starts with first color", c5[0].upper() == base7[0].upper(), c5[0])
check("5 colors ends with last color", c5[-1].upper() == base7[-1].upper(), c5[-1])

c7 = mod.interpolate_colors(base7, 7)
check("7 colors identical to base", [c.upper() for c in c7] == [b.upper() for b in base7])

c10 = mod.interpolate_colors(base7, 10)
check("10 colors length", len(c10) == 10, len(c10))
check("10 colors starts with first color", c10[0].upper() == base7[0].upper(), c10[0])
check("10 colors ends with last color", c10[-1].upper() == base7[-1].upper(), c10[-1])

print("\n=== 2. Reclassification Methods in ArcPy Spatial Analyst ===")
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.CheckOutExtension("Spatial")

tool = mod.PowerClimateAtlasGenerator()
tmp_dir = os.path.join(os.path.dirname(__file__), "_test_reclass_tmp")
mod.makedirs_ok(tmp_dir)
ras_dir = os.path.join(tmp_dir, "Rasters")
lyr_dir = os.path.join(tmp_dir, "Layers")
mod.makedirs_ok(ras_dir)
mod.makedirs_ok(lyr_dir)

# Create a sample continuous raster (e.g. 10x10 with values 5.0 to 95.0)
arr = np.linspace(5.0, 95.0, 100).reshape((10, 10))
rp = os.path.join(ras_dir, "Sample_Temp.tif")
if arcpy.Exists(rp):
    arcpy.management.Delete(rp)
r_obj = arcpy.NumPyArrayToRaster(arr)
r_obj.save(rp)
arcpy.management.CalculateStatistics(rp)

methods = [
    "Natural Breaks (Jenks)",
    "Equal Interval",
    "Equal Area (Quantile)",
    "Geometric Interval",
    "Standard Deviation"
]

dummy_msg = lambda t: None
dummy_warn = lambda t: None

for meth in methods:
    n_classes = 6
    colors = mod.interpolate_colors(base7, n_classes)
    cls_rp, clr_path, breaks = tool._build_display(
        rp, "Sample_Temp", "Temperature", colors, n_classes, meth, dummy_msg, dummy_warn, purge=True)
    
    check("Method '%s': cls_rp created" % meth, cls_rp and arcpy.Exists(cls_rp), cls_rp)
    check("Method '%s': clr_path created" % meth, clr_path and os.path.exists(clr_path), clr_path)
    if clr_path and os.path.exists(clr_path):
        with open(clr_path, "r") as fh:
            lines = [l.strip() for l in fh if l.strip()]
        check("Method '%s': clr lines == %d" % (meth, n_classes), len(lines) == n_classes, len(lines))
    if breaks:
        check("Method '%s': breaks count == %d" % (meth, n_classes + 1), len(breaks) == n_classes + 1, len(breaks))
        check("Method '%s': breaks ascending" % meth, breaks[0] < breaks[-1], "%f -> %f" % (breaks[0], breaks[-1]))

print("\n=== 3. Layer File Generation (_make_lyr) ===")
# Test layer with classified display
lp_cls = os.path.join(lyr_dir, "Sample_Temp_Classified.lyr")
tool._make_lyr(cls_rp, lp_cls, "Sample_Temp", "Temperature", colors, n_classes, "Natural Breaks (Jenks)",
               dummy_msg, dummy_warn, breaks=breaks, src_continuous=rp, is_classified=True)
check("Classified .lyr exists", arcpy.Exists(lp_cls))
check("Classified .lyr.json exists", os.path.exists(lp_cls + ".json"))

# Test layer with continuous (reclass disabled)
lp_cont = os.path.join(lyr_dir, "Sample_Temp_Continuous.lyr")
tool._make_lyr(rp, lp_cont, "Sample_Temp", "Temperature", base7, 7, "IDW",
               dummy_msg, dummy_warn, breaks=[5.0, 95.0], src_continuous=rp, is_classified=False)
check("Continuous .lyr exists", arcpy.Exists(lp_cont))
check("Continuous .lyr.json exists", os.path.exists(lp_cont + ".json"))
if os.path.exists(lp_cont + ".json"):
    import json
    with open(lp_cont + ".json", "r") as fh:
        meta_c = json.load(fh)
    check("Continuous JSON classification is 'Continuous'", meta_c.get("classification") == "Continuous")
    check("Continuous JSON display_raster is Sample_Temp.tif", meta_c.get("display_raster") == "Sample_Temp.tif")

# Clean up test temp files
try:
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
except Exception:
    pass

print("\n" + "-" * 45)
print("TEST SUMMARY: %d PASS, %d FAIL" % (passed, failed))
print("-" * 45)
if failed > 0:
    sys.exit(1)
sys.exit(0)
