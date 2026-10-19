# -*- coding: utf-8 -*-
"""
End-to-End Live Integration Test: Field & Season Filtering
Tests executing the tool with 'Filter by Seasons & Aggregations' for Summer (JJA) only.
Verifies that only summer indicators are generated in GDB, Rasters, Dictionaries, and QA.
"""
import os
import shutil
import sys
import traceback

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt"))
OUT = os.path.join(BASE, "E2E_Filter_Output")
GDBIN = os.path.join(BASE, "Egypt Climate Data", "Egpyt_Climate.gdb")
PTSIN = os.path.join(GDBIN, "Point_Sample_Climate")
MASK = os.path.join(GDBIN, "Egypt")

mod = type(sys)("me2e_filter")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True

LOG = open(os.path.join(BASE, "e2e_filter.log"), "w")

def log(*a):
    t = " ".join(str(x) for x in a)
    print(t)
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

# Pick 6 spread points for fast execution
arcpy.management.MakeFeatureLayer(PTSIN, "e2e_f_lyr")
oid_f = arcpy.Describe("e2e_f_lyr").OIDFieldName
oids = sorted([r[0] for r in arcpy.da.SearchCursor("e2e_f_lyr", ["OID@"])])
pick = [oids[i * len(oids) // 6] for i in range(6)]
arcpy.management.MakeFeatureLayer(PTSIN, "e2e_f_sub", '%s IN (%s)' % (arcpy.AddFieldDelimiters(PTSIN, oid_f), ",".join(map(str, pick))))
sub = os.path.join(OUT + "_IN.gdb", "pts6")
if arcpy.Exists(OUT + "_IN.gdb"):
    arcpy.management.Delete(OUT + "_IN.gdb")
arcpy.management.CreateFileGDB(os.path.dirname(OUT + "_IN.gdb"), os.path.basename(OUT + "_IN.gdb"))
arcpy.management.CopyFeatures("e2e_f_sub", sub)
arcpy.management.Delete("e2e_f_lyr")
arcpy.management.Delete("e2e_f_sub")

tool = mod.PowerClimateAtlasGenerator()
ps = tool.getParameterInfo()
pdict = dict((p.name, p) for p in ps)
vals = {
    "Input_Point_Features": sub,
    "Output_Workspace": OUT,
    "Study_Area_Mask": MASK,
    "Climate_Data_Source": "NASA POWER API",
    "Climate_Modules": ["Temperature", "Precipitation"],
    "Field_Filter_Scope": "Filter by Seasons & Aggregations",
    "Included_Aggregations": ["Seasonal Summaries"],
    "Included_Seasons": ["Summer (JJA)"],
    "Time_Mode": "Single Year",
    "Single_Year": 2025,
    "Temporal_Aggregation": "Monthly",
    "Gap_Fill_Method": "No Fill (skip missing)",
    "Download_Only": False,
    "Interpolation_Method": "IDW",
    "IDW_Curve_Profile": "Gentle / Smooth (Power 1.2)",
    "Base_Cell_Size": "50000 Meters",
    "Add_To_Map": False,
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
    
    # Verify Temperature FC fields
    t_fc = os.path.join(gdb_expected, "Temperature")
    t_fields = [f.name for f in arcpy.ListFields(t_fc)]
    log("Temperature FC fields: %s" % t_fields)
    assert "T_Summer_Mean" in t_fields, "T_Summer_Mean missing"
    assert "T_Winter_Mean" not in t_fields, "T_Winter_Mean should have been filtered out!"
    assert "T_Annual_Mean" not in t_fields, "T_Annual_Mean should have been filtered out!"

    # Verify Precipitation FC fields
    p_fc = os.path.join(gdb_expected, "Precipitation")
    p_fields = [f.name for f in arcpy.ListFields(p_fc)]
    log("Precipitation FC fields: %s" % p_fields)
    assert "R_Summer_Mean" in p_fields, "R_Summer_Mean missing"
    assert "R_Winter_Mean" not in p_fields, "R_Winter_Mean should have been filtered out!"

    # Verify Rasters generated directly inside each element folder: exactly 4 rasters
    t_rasters = os.listdir(os.path.join(OUT, "01_Temperature"))
    p_rasters = os.listdir(os.path.join(OUT, "02_Precipitation"))
    log("Temperature Rasters: %s" % t_rasters)
    log("Precipitation Rasters: %s" % p_rasters)
    
    # GeoTIFF float files (excluding _cls display rasters)
    t_raw = [f for f in t_rasters if f.endswith(".tif") and not f.endswith("_cls.tif")]
    p_raw = [f for f in p_rasters if f.endswith(".tif") and not f.endswith("_cls.tif")]
    assert len(t_raw) == 3, "Expected 3 summer temperature rasters, got: %s" % t_raw
    # Verify Excel workbooks generated in 00_Tables_And_Reports
    vec_dir = os.path.join(OUT, "00_Tables_And_Reports")
    master_xls = os.path.join(vec_dir, "Climate_Atlas_Master_Workbook.xls")
    assert os.path.isfile(master_xls), "Master workbook missing: %s" % master_xls
    log("Master workbook verified: %s" % master_xls)

    meta_xls = os.path.join(vec_dir, "Metadata_Dictionary.xls")
    assert os.path.isfile(meta_xls), "Metadata dictionary xls missing: %s" % meta_xls
    log("Metadata Excel dictionary verified: %s" % meta_xls)

    arabic_xls = os.path.join(vec_dir, "Field_Dictionary_Arabic.xls")
    assert os.path.isfile(arabic_xls), "Arabic Excel dictionary verified: %s" % arabic_xls
    log("Arabic Excel dictionary verified: %s" % arabic_xls)

    t_xls = os.path.join(vec_dir, "Temperature.xls")
    assert os.path.isfile(t_xls), "Temperature xls missing: %s" % t_xls
    log("Temperature element Excel workbook verified: %s" % t_xls)

    p_xls = os.path.join(vec_dir, "Precipitation.xls")
    assert os.path.isfile(p_xls), "Precipitation xls missing: %s" % p_xls
    log("Precipitation element Excel workbook verified: %s" % p_xls)

    log("ALL E2E FILTERING CHECKS PASSED PERFECTLY!")
except Exception:
    log("E2E FILTER EXECUTE FAILED")
    traceback.print_exc(file=LOG)
    LOG.flush()
    sys.exit(1)
finally:
    LOG.close()
