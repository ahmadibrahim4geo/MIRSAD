# -*- coding: utf-8 -*-
"""Tests for per-element workflow: merge folding, element point layers
(admin + own module fields only, row counts), and raster sourcing from the
element layer. Runs on ArcMap 10.x python."""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt"))
OUT = os.path.join(BASE, "tests", ".output", "elements")
if not os.path.isdir(os.path.dirname(OUT)):
    os.makedirs(os.path.dirname(OUT))

mod = type(sys)("mel")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = ("PASS " if cond else "FAIL ") + name
    if detail != "":
        line += " | " + str(detail)
    print(line)

# ---------------- 1. bare element names ----------------
check("short names cover all", set(mod.MODULES_ALL).issubset(set(mod.MODULE_SHORT))
      and all(mod.MODULE_SHORT[m].replace("_", " ") for m in mod.MODULES_ALL))
check("short names GDB-safe", all(" " not in v and len(v) <= 40 for v in mod.MODULE_SHORT.values()))

# ---------------- 2. element layers built from input + results ----------------
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True
tool = mod.PowerClimateAtlasGenerator()
msgs, warns = [], []
if os.path.isdir(OUT):
    shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
gdb = os.path.join(OUT, "e.gdb")
arcpy.management.CreateFileGDB(OUT, "e.gdb")
sp = arcpy.SpatialReference(4326)
arcpy.management.CreateFeatureclass(gdb, "inp", "POINT", spatial_reference=sp)
inp = os.path.join(gdb, "inp")
arcpy.management.AddField(inp, "Source_ID", "LONG")
with arcpy.da.InsertCursor(inp, ["SHAPE@XY", "Source_ID"]) as cur:
    for i, (x, y) in enumerate([(30.0, 30.0), (31.0, 30.5), (32.0, 31.0)]):
        cur.insertRow([(x, y), i + 1])
tfields = mod.MODULE_FIELDS["Temperature"]
rfields = mod.MODULE_FIELDS["Precipitation"]
results = []
for i in (1, 2, 3):
    results.append({"oid": i, "lat": 30.0, "lon": 31.0, "status": "OK", "error": "",
                    "fields": dict([("T_Annual_Mean", 20.0)] + [(f, 20.0) for f in tfields[1:]]
                                   + [("R_Annual_Total", 100.0)] + [(f, 100.0) for f in rfields[1:]])})
els = tool._build_element_layers(inp, gdb, sp, results, ["Temperature", "Precipitation"],
                                 {"y0": 2025, "y1": 2025, "temporal": "Monthly",
                                  "interp": "IDW", "base_cell": 0.5, "wind_cell": 2.0},
                                 msgs.append, warns.append)
check("two element FCs", set(els) == set(["Temperature", "Precipitation"]), els.keys())
for m, fc in els.items():
    check("element exists " + m, arcpy.Exists(fc))
    check("element rows " + m, int(arcpy.GetCount_management(fc)[0]) == 3)
    names = set(f.name for f in arcpy.ListFields(fc))
    want = set(["Source_ID", "Status", "Point_Lat", "Data_Start"] + mod.MODULE_FIELDS[m])
    check("element fields " + m, want <= names, sorted(names - want)[:3])
    other = (set(tfields + rfields) - set(mod.MODULE_FIELDS[m])) & names
    check("no foreign climate fields " + m, not other, list(other)[:3])
    check("bare name, no prefix", os.path.basename(fc) == mod.MODULE_SHORT[m],
          os.path.basename(fc))

# ---------------- 3. rasters sourced from the element layer ----------------
arcpy.CheckOutExtension("Spatial")
_gdb2, _paths = tool._build_layout(OUT, ["Temperature"])
reg = tool._interpolate_all(None, ["Temperature"], _paths,
                            cell=0.5, method="IDW", mask=None,
                            msg=msgs.append, warn=warns.append,
                            source_by_module={"Temperature": els["Temperature"]})
check("registry from element src", len(reg) == len(tfields), len(reg))
check("rasters exist", all(os.path.isfile(r[1]) for r in reg))
arcpy.CheckInExtension("Spatial")
shutil.rmtree(OUT, ignore_errors=True)

print("")
print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
