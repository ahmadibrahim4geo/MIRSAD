# -*- coding: utf-8 -*-
"""Smoke TAIL: wind vectors + isobars + QA on existing smoke outputs
(registry rebuilt by scanning element folders for .tif files; element layers
read from Climate_Database.gdb)."""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "SmokeTest_108_Output")

mod = type(sys)("mtail")
exec(compile(open((os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt")), "rb").read(),
             "tail", "exec"), mod.__dict__)
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True

msgs = []
tool = mod.PowerClimateAtlasGenerator()
modules = ["Temperature", "Wind", "Precipitation", "Sea Level Pressure"]


def _log(t):
    print(t)
gdb = os.path.join(OUT, "Climate_Database.gdb")
mask = os.path.join(BASE, "Egypt Climate Data", "Egpyt_Climate.gdb", "Egypt")
out_sr = arcpy.SpatialReference(4326)
paths = {"gdb": gdb, "vec": os.path.join(OUT, "00_Tables_And_Reports")}

reg = []
for m in modules:
    folder = os.path.join(OUT, mod.MODULE_FOLDER[m])
    subdirs = [os.path.join(folder, s) for s in ("Speed", "Direction")] if m == "Wind" else [folder]
    for dp in subdirs:
        if not os.path.isdir(dp):
            continue
        for f in sorted(os.listdir(dp)):
            if not f.lower().endswith(".tif"):
                continue
            field = os.path.splitext(f)[0]
            if field.endswith("_cls"):
                continue
            module = tool._module_of_field(field)
            reg.append((field, os.path.join(dp, f), None, module,
                        tool._colors_for(module, field),
                        5 if module == "UV Index" else 7))
print("registry rebuilt: %d" % len(reg))
assert len(reg) == 36, len(reg)
els = {}
for m in modules:
    fc = os.path.join(gdb, mod.MODULE_SHORT.get(m, m))
    assert arcpy.Exists(fc), fc
    els[m] = fc
print("element layers: %d" % len(els))

arcpy.CheckOutExtension("Spatial")
try:
    wv = tool._build_wind_vectors(gdb, paths, reg, els.get("Wind"), mask, out_sr, 2.0,
                                  msgs.append, msgs.append)
    print("wind fcs: %d" % len(wv))
    assert len(wv) == 5, wv
    tool._build_isobars(gdb, reg, msgs.append, msgs.append)
    for n in ("Isobars_PSL_Winter_Mean", "Isobars_PSL_Spring_Mean",
              "Isobars_PSL_Summer_Mean", "Isobars_PSL_Autumn_Mean"):
        assert arcpy.Exists(os.path.join(gdb, n)), n
    print("isobars ok")
finally:
    arcpy.CheckInExtension("Spatial")

results = [{"oid": 1, "status": "OK", "fields": {"T_Annual_Mean": 1.0}, "error": ""}]
qa = tool._run_qa(els, paths, modules, reg, results, msgs.append, msgs.append)
fails = [q for q in qa if not q[1]]
print("QA fails: %s" % fails)
assert not fails, fails
print("TAIL OK")
