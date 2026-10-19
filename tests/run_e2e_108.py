# -*- coding: utf-8 -*-
"""End-to-end execute() on 9 spread points x Temperature+Precipitation, live NASA.
Validates the per-element fetch loop, element layers, rasters-from-elements,
dicts, QA and log through the REAL tool entry point."""
import os
import shutil
import sys
import traceback

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt"))
OUT = os.path.join(BASE, "E2E_108_Output")
GDBIN = os.path.join(BASE, "Egypt Climate Data", "Egpyt_Climate.gdb")
PTSIN = os.path.join(GDBIN, "Point_Sample_Climate")
MASK = os.path.join(GDBIN, "Egypt")

mod = type(sys)("me2e")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True

LOG = open(os.path.join(BASE, "e2e_progress.log"), "w")

def log(*a):
    t = " ".join(str(x) for x in a)
    LOG.write(t + "\n")
    LOG.flush()

class Msg(object):
    def addMessage(self, t):
        log("[MSG] " + str(t))
    def addWarningMessage(self, t):
        log("[WARN] " + str(t))
    def addErrorMessage(self, t):
        log("[ERR] " + str(t))

if os.path.isdir(OUT):
    shutil.rmtree(OUT, ignore_errors=True)

# 9 spread points into a scratch input
arcpy.management.MakeFeatureLayer(PTSIN, "e2e_lyr")
oid_f = arcpy.Describe("e2e_lyr").OIDFieldName
oids = sorted([r[0] for r in arcpy.da.SearchCursor("e2e_lyr", ["OID@"])])
pick = [oids[i * len(oids) // 9] for i in range(9)]
arcpy.management.MakeFeatureLayer(PTSIN, "e2e_sub", '%s IN (%s)' % (arcpy.AddFieldDelimiters(PTSIN, oid_f), ",".join(map(str, pick))))
sub = os.path.join(OUT + "_IN.gdb", "pts9")
if arcpy.Exists(OUT + "_IN.gdb"):
    arcpy.management.Delete(OUT + "_IN.gdb")
arcpy.management.CreateFileGDB(os.path.dirname(OUT + "_IN.gdb"), os.path.basename(OUT + "_IN.gdb"))
arcpy.management.CopyFeatures("e2e_sub", sub)
arcpy.management.Delete("e2e_lyr")
arcpy.management.Delete("e2e_sub")

tool = mod.PowerClimateAtlasGenerator()
ps = tool.getParameterInfo()
pdict = dict((p.name, p) for p in ps)
vals = {
    "Input_Point_Features": sub,
    "Output_Workspace": OUT,
    "Output_Spatial_Reference": None,
    "Study_Area_Mask": MASK,
    "Climate_Data_Source": "NASA POWER API",
    "Climate_Modules": ["Temperature", "Precipitation"],
    "Time_Mode": "Single Year",
    "Single_Year": 2025,
    "Start_Year": 2015,
    "End_Year": 2025,
    "Temporal_Aggregation": "Monthly",
    "Gap_Fill_Method": "No Fill (skip missing)",
    "Download_Only": False,
    "Interpolation_Method": "IDW",
    "IDW_Curve_Profile": "Gentle / Smooth (Power 1.2)",
    "IDW_Power": 1.2,
    "IDW_Search_Type": "Variable",
    "IDW_Num_Points": 12,
    "IDW_Max_Distance": None,
    "Krig_Model": "Spherical",
    "Krig_Type": "Ordinary",
    "Krig_Num_Points": 12,
    "Spline_Type": "Tension",
    "Spline_Weight": 5.0,
    "Spline_Num_Points": 12,
    "Base_Cell_Size": "50000 Meters",
    "Wind_Factor_Cell_Size": "200000 Meters",
    "Create_Isobars": False,
    "Pressure_Interval_Scheme": "Global Standard (4 mbar)",
    "Custom_Pressure_Step": 4.0,
    "Focal_Smoothing": False,
    "Focal_Statistic": "MEAN",
    "Focal_Neighborhood": 3,
    "Point_Tolerance": "0 Meters",
    "Add_To_Map": False,
    "Map_Add_Modules": ["Temperature", "Precipitation"],
    "Purge_Cache": True
}
for k, v in vals.items():
    if k in pdict and v is not None:
        try:
            if pdict[k].multiValue and isinstance(v, list):
                pdict[k].values = v
            else:
                pdict[k].value = v
        except Exception as ex:
            log("set %s failed: %s" % (k, ex))
tool.updateParameters(ps)
try:
    tool.execute(ps, Msg())
    gdb_expected = os.path.join(OUT, "Climate_Database_2025.gdb")
    assert os.path.isdir(gdb_expected), "Expected GDB missing: %s" % gdb_expected
    log("E2E EXECUTE OK (GDB: %s)" % os.path.basename(gdb_expected))
except Exception:
    log("E2E EXECUTE FAILED")
    traceback.print_exc(file=LOG)
    LOG.flush()
    sys.exit(1)
finally:
    LOG.close()
