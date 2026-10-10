# -*- coding: utf-8 -*-
"""Targeted regression: _interpolate_all with the NEW signature (no depth)
on tiny data, UV module (5 fast rasters incl. classified display, no .lyr)."""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "SigTest_TMP")

mod = type(sys)("msig")
exec(compile(open((os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt")), "rb").read(),
             "sig", "exec"), mod.__dict__)
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True
tool = mod.PowerClimateAtlasGenerator()
msgs = []

if os.path.isdir(OUT):
    shutil.rmtree(OUT, ignore_errors=True)
gdb_path, paths = tool._build_layout(OUT, ["UV Index"])
sp = arcpy.SpatialReference(4326)
arcpy.management.CreateFeatureclass(gdb_path, "mini", "POINT", spatial_reference=sp)
mini = os.path.join(gdb_path, "mini")
for f in ["UV_Annual_Mean", "UV_Winter_Mean", "UV_Spring_Mean", "UV_Summer_Mean", "UV_Autumn_Mean"]:
    arcpy.management.AddField(mini, f, "DOUBLE")
with arcpy.da.InsertCursor(mini, ["SHAPE@XY", "UV_Annual_Mean", "UV_Winter_Mean", "UV_Spring_Mean", "UV_Summer_Mean", "UV_Autumn_Mean"]) as cur:
    for i, (x, y) in enumerate([(30.0, 30.0), (32.0, 30.0), (31.0, 32.0),
                                (30.5, 30.5), (31.5, 31.5), (31.0, 30.5)]):
        cur.insertRow([(x, y), 5.0 + i, 3.0 + i * 0.5, 5.0 + i, 8.0 + i, 4.0 + i])

arcpy.CheckOutExtension("Spatial")
try:
    reg = tool._interpolate_all(mini, ["UV Index"], paths, 0.5, "IDW", None,
                                msgs.append, msgs.append,
                                reclass_opts={"enable": True, "nclass": 5,
                                              "method": "Natural Breaks (Jenks)"})
    print("registry: %d" % len(reg))
    assert len(reg) == 5, len(reg)
    for (f, rp, lp, m, c, n) in reg:
        assert os.path.isfile(rp), rp
        assert lp is None, lp
        assert os.path.isfile(os.path.join(os.path.dirname(rp), f + "_cls.tif")), f
        assert os.path.isfile(os.path.join(os.path.dirname(rp), f + ".clr")), f
    print("ALL RASTERS+DISPLAY OK (no .lyr)")
finally:
    arcpy.CheckInExtension("Spatial")
shutil.rmtree(OUT, ignore_errors=True)
print("SIG TEST OK")
