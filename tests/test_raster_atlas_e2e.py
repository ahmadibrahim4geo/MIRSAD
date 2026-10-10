# -*- coding: utf-8 -*-
"""
End-to-End Test for RasterDataClimateAtlasGenerator
Uses local REC as Layer 1 (download extent) and Egypt as Layer 2 (final clip mask).
"""
import os
import sys
try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)

# Ensure workspace in path
proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)

from raster_atlas_generator import RasterDataClimateAtlasGenerator

def run_test():
    print("=" * 60)
    print("Testing RasterDataClimateAtlasGenerator End-to-End...")
    print("=" * 60)

    gdb_input = os.path.join(proj_dir, "Egypt Climate Data", "Egpyt_Climate.gdb")
    layer1_rec = os.path.join(gdb_input, "REC")
    layer2_egypt = os.path.join(gdb_input, "Egypt")

    out_test_dir = os.path.join(proj_dir, "test_raster_output")
    if os.path.isdir(out_test_dir):
        try:
            shutil.rmtree(out_test_dir)
        except Exception:
            pass
    if not os.path.isdir(out_test_dir):
        os.makedirs(out_test_dir)

    tool = RasterDataClimateAtlasGenerator()
    params = tool.getParameterInfo()
    pdict = dict((p.name, p) for p in params)

    pdict["Download_Extent_Layer"].value = layer1_rec
    pdict["Final_Clip_Layer"].value = layer2_egypt
    pdict["Climate_Data_Source"].value = "NASA POWER Regional Grid"
    pdict["Time_Mode"].value = "Year Range"
    pdict["Start_Year"].value = 2020
    pdict["End_Year"].value = 2020
    pdict["Included_Aggregations"].value = "Annual Summaries;Seasonal Summaries (DJF, MAM, JJA, SON)"
    pdict["Climate_Modules"].value = "Temperature"
    pdict["Interpolation_Method"].value = "Inverse Distance Weighted (IDW)"
    pdict["Output_Cell_Size"].value = 0.05
    pdict["Export_Individual_Shapefiles"].value = True
    pdict["Output_Workspace"].value = out_test_dir

    print("Executing tool...")
    tool.execute(params, None)

    print("\n--- Verifying Outputs ---")
    gdb_out = os.path.join(out_test_dir, "Project_Data.gdb")
    temp_fc = os.path.join(gdb_out, "Temperature")
    assert arcpy.Exists(temp_fc), "Temperature FC missing in GDB!"
    count = int(arcpy.GetCount_management(temp_fc).getOutput(0))
    print("[PASS] Temperature FC in GDB with %d points" % count)

    flds = [f.name for f in arcpy.ListFields(temp_fc)]
    print("Fields present:", flds)
    for req_f in ["T_Annual_Mean", "T_Winter_Mean", "T_Summer_Mean", "T_Spring_Mean", "T_Autumn_Mean", "Data_Start", "Data_End"]:
        assert req_f in flds, "Missing required field: %s" % req_f
    print("[PASS] All seasonal, annual, and date metadata fields exist in master GDB table.")

    # Check Rasters
    mod_dir = os.path.join(out_test_dir, "01_Temperature")
    tif_annual = os.path.join(mod_dir, "T_Annual_Mean.tif")
    assert os.path.isfile(tif_annual), "T_Annual_Mean.tif missing!"
    desc_ras = arcpy.Describe(tif_annual)
    print("[PASS] Raster exists: %s | Format: %s | PixelType: %s" % (
        os.path.basename(tif_annual), desc_ras.format, desc_ras.pixelType))

    # Check Shp & Tables
    vec_dir = os.path.join(out_test_dir, "00_Tables_And_Reports")
    shp_file = os.path.join(vec_dir, "01_Temperature_Grid_Points.shp")
    assert os.path.isfile(shp_file), "Shapefile missing: %s" % shp_file
    print("[PASS] Shapefile exists: %s" % os.path.basename(shp_file))

    # Check Log
    log_file = os.path.join(out_test_dir, "Processing_Log.txt")
    assert os.path.isfile(log_file), "Processing_Log.txt missing!"
    print("[PASS] Processing_Log.txt exists.")

    print("\nALL CHECKS PASSED! Tool executed and produced 100% compliant atlas package.")

if __name__ == "__main__":
    run_test()
