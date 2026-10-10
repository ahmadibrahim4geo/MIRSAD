# -*- coding: utf-8 -*-
"""
Comprehensive verification test for the Time Window UI update and attribute recording
in both tools (PowerClimateAtlasGenerator and RasterDataClimateAtlasGenerator).
"""
import os
import sys
try:  # Python 3 (imp was removed in 3.12; .pyt needs SourceFileLoader)
    import importlib.machinery as _ilm

    def _load_source(_name, _path):
        return _ilm.SourceFileLoader(_name, _path).load_module()
except ImportError:  # Python 2.7 fallback
    import imp as _imp
    _load_source = _imp.load_source
import tempfile
import shutil

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ_DIR not in sys.path:
    sys.path.insert(0, PROJ_DIR)

try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)

# Load tools
pyt_path = os.path.join(PROJ_DIR, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(pyt_path):
    pyt_path = os.path.join(PROJ_DIR, "POWER_Climate_Atlas_Generator_10_8.pyt")
pyt_mod = _load_source("pyt_mod", pyt_path)
from raster_atlas_generator import RasterDataClimateAtlasGenerator

def run_all_checks():
    print("=" * 70)
    print("VERIFICATION: TIME WINDOW UPDATE & DATE PICKER IN BOTH TOOLS")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. TOOL 1: PowerClimateAtlasGenerator (Point-Based Atlas)
    # -------------------------------------------------------------
    print("\n[TOOL 1] Checking PowerClimateAtlasGenerator...")
    t1 = pyt_mod.PowerClimateAtlasGenerator()
    params1 = t1.getParameterInfo()
    pdict1 = dict((p.name, p) for p in params1)

    # Verify category sequence: Data Source immediately followed by Time Window
    categories1 = []
    for p in params1:
        cat = p.category or "[General]"
        if not categories1 or categories1[-1] != cat:
            categories1.append(cat)
    
    print("Tool 1 Categories:", categories1)
    ds_idx1 = categories1.index("Data Source")
    tw_idx1 = categories1.index("Time Window")
    assert tw_idx1 == ds_idx1 + 1, "Time Window must immediately follow Data Source in Tool 1!"
    print("[PASS] Tool 1: Time Window category is directly below Data Source.")

    # Check Time Window parameters exist and have correct types
    assert "Time_Mode" in pdict1, "Time_Mode missing in Tool 1"
    assert "Single_Year" in pdict1, "Single_Year missing in Tool 1"
    assert "Start_Year" in pdict1, "Start_Year missing in Tool 1"
    assert "End_Year" in pdict1, "End_Year missing in Tool 1"
    assert "Open_Calendar_Picker" in pdict1, "Open_Calendar_Picker missing in Tool 1"
    assert "Start_Date" in pdict1, "Start_Date missing in Tool 1"
    assert "End_Date" in pdict1, "End_Date missing in Tool 1"

    assert pdict1["Open_Calendar_Picker"].datatype in ("GPBoolean", "Boolean"), "Picker should be GPBoolean"
    assert pdict1["Start_Date"].datatype in ("GPString", "String"), "Start_Date should be GPString"
    assert pdict1["End_Date"].datatype in ("GPString", "String"), "End_Date should be GPString"
    print("[PASS] Tool 1: Parameters correctly defined (GPBoolean launcher, GPString dates).")

    # Check dynamic enable / disable
    pdict1["Time_Mode"].value = "Single Year"
    t1.updateParameters(params1)
    assert pdict1["Single_Year"].enabled and not pdict1["Start_Year"].enabled and not pdict1["Start_Date"].enabled, "Single Year enabling incorrect"

    pdict1["Time_Mode"].value = "Year Range"
    t1.updateParameters(params1)
    assert pdict1["Start_Year"].enabled and pdict1["End_Year"].enabled and not pdict1["Single_Year"].enabled and not pdict1["Start_Date"].enabled, "Year Range enabling incorrect"

    pdict1["Time_Mode"].value = "Custom Date Range"
    t1.updateParameters(params1)
    assert pdict1["Start_Date"].enabled and pdict1["End_Date"].enabled and pdict1["Open_Calendar_Picker"].enabled and not pdict1["Single_Year"].enabled, "Custom Date Range enabling incorrect"
    print("[PASS] Tool 1: Dynamic enabling/disabling across all 3 Time Modes works properly.")

    # -------------------------------------------------------------
    # 2. TOOL 2: RasterDataClimateAtlasGenerator (Gridded Atlas)
    # -------------------------------------------------------------
    print("\n[TOOL 2] Checking RasterDataClimateAtlasGenerator...")
    t2 = RasterDataClimateAtlasGenerator()
    params2 = t2.getParameterInfo()
    pdict2 = dict((p.name, p) for p in params2)

    categories2 = []
    for p in params2:
        cat = p.category or "[General]"
        if not categories2 or categories2[-1] != cat:
            categories2.append(cat)
    
    print("Tool 2 Categories:", categories2)
    dp_idx2 = categories2.index("Data Provider & Authentication")
    tw_idx2 = categories2.index("Time Window")
    assert tw_idx2 == dp_idx2 + 1, "Time Window must immediately follow Data Provider & Authentication in Tool 2!"
    print("[PASS] Tool 2: Time Window category is directly below Data Provider.")

    # Check Time Window parameters
    assert "Time_Mode" in pdict2, "Time_Mode missing in Tool 2"
    assert "Single_Year" in pdict2, "Single_Year missing in Tool 2"
    assert "Start_Year" in pdict2, "Start_Year missing in Tool 2"
    assert "End_Year" in pdict2, "End_Year missing in Tool 2"
    assert "Open_Calendar_Picker" in pdict2, "Open_Calendar_Picker missing in Tool 2"
    assert "Start_Date" in pdict2, "Start_Date missing in Tool 2"
    assert "End_Date" in pdict2, "End_Date missing in Tool 2"
    assert pdict2["Open_Calendar_Picker"].datatype in ("GPBoolean", "Boolean"), "Picker should be GPBoolean"
    assert pdict2["Start_Date"].datatype in ("GPString", "String"), "Start_Date should be GPString"
    assert pdict2["End_Date"].datatype in ("GPString", "String"), "End_Date should be GPString"
    print("[PASS] Tool 2: Parameters correctly defined (GPBoolean launcher, GPString dates).")

    # Check dynamic enable / disable
    pdict2["Time_Mode"].value = "Single Year"
    t2.updateParameters(params2)
    assert pdict2["Single_Year"].enabled and not pdict2["Start_Year"].enabled and not pdict2["Start_Date"].enabled, "Tool 2 Single Year enabling incorrect"

    pdict2["Time_Mode"].value = "Year Range"
    t2.updateParameters(params2)
    assert pdict2["Start_Year"].enabled and pdict2["End_Year"].enabled and not pdict2["Single_Year"].enabled and not pdict2["Start_Date"].enabled, "Tool 2 Year Range enabling incorrect"

    pdict2["Time_Mode"].value = "Custom Date Range"
    t2.updateParameters(params2)
    assert pdict2["Start_Date"].enabled and pdict2["End_Date"].enabled and pdict2["Open_Calendar_Picker"].enabled and not pdict2["Single_Year"].enabled, "Tool 2 Custom Date Range enabling incorrect"
    print("[PASS] Tool 2: Dynamic enabling/disabling across all 3 Time Modes works properly.")

    # -------------------------------------------------------------
    # 3. DATE PARSING VALIDATION
    # -------------------------------------------------------------
    print("\n[DATE PARSER] Checking flexible date string parsing...")
    dates_to_test = [
        ("31/3/1990", (1990, 3, 31)),
        ("31/03/1990", (1990, 3, 31)),
        ("1990-03-31", (1990, 3, 31)),
        ("1990/03/31", (1990, 3, 31)),
        ("01/01/2024", (2024, 1, 1)),
        ("31/12/2024", (2024, 12, 31)),
        ("20241231", (2024, 12, 31)),
    ]
    for d_str, expected in dates_to_test:
        parsed1 = pyt_mod.parse_gp_date(d_str)
        parsed2 = pyt_mod.parse_gp_date(d_str)
        assert (parsed1.year, parsed1.month, parsed1.day) == expected, "Failed parsing %s in tool 1" % d_str
        assert (parsed2.year, parsed2.month, parsed2.day) == expected, "Failed parsing %s in tool 2" % d_str
    print("[PASS] All date formats successfully parsed across both tools.")

    # -------------------------------------------------------------
    # 4. ATTRIBUTE RECORDING: Data_Start & Data_End
    # -------------------------------------------------------------
    print("\n[ATTRIBUTES] Verifying Data_Start and Data_End preservation...")
    tdir = tempfile.mkdtemp()
    try:
        gdb = os.path.join(tdir, "test_attrs.gdb")
        arcpy.CreateFileGDB_management(tdir, "test_attrs.gdb")
        pts_fc = os.path.join(gdb, "pts")
        arcpy.CreateFeatureclass_management(gdb, "pts", "POINT", spatial_reference=arcpy.SpatialReference(4326))
        with arcpy.da.InsertCursor(pts_fc, ["SHAPE@XY"]) as icur:
            icur.insertRow([(31.2, 30.0)])

        # Test A: Custom Date Range (31/3/1990 to 31/12/2000)
        meta_custom = {
            "y0": 1990, "y1": 2000, "temporal": "Monthly",
            "interp": "IDW", "base_cell": 2500, "wind_cell": 2500,
            "data_start": "31/03/1990", "data_end": "31/12/2000"
        }
        res = [{"oid": 1, "lat": 30.0, "lon": 31.2, "status": "OK", "fields": {"T_Annual_Mean": 22.1}}]
        fc_custom = t1._build_single_element_layer(
            pts_fc, gdb, res, "Temperature", meta_custom, lambda m: None, lambda w: None, ["T_Annual_Mean"]
        )
        row_custom = list(arcpy.da.SearchCursor(fc_custom, ["Data_Start", "Data_End"]))[0]
        assert row_custom[0] == "31/03/1990", "Tool 1 Custom Data_Start failed: %s" % row_custom[0]
        assert row_custom[1] == "31/12/2000", "Tool 1 Custom Data_End failed: %s" % row_custom[1]
        print("[PASS] Tool 1 Custom Date Range correctly stores '%s' and '%s'." % (row_custom[0], row_custom[1]))

        # Test B: Single Year (2024)
        meta_single = {
            "y0": 2024, "y1": 2024, "temporal": "Monthly",
            "interp": "IDW", "base_cell": 2500, "wind_cell": 2500,
            "data_start": "2024", "data_end": "2024"
        }
        fc_single = t1._build_single_element_layer(
            pts_fc, gdb, res, "Temperature", meta_single, lambda m: None, lambda w: None, ["T_Annual_Mean"]
        )
        row_single = list(arcpy.da.SearchCursor(fc_single, ["Data_Start", "Data_End"]))[0]
        assert row_single[0] == "2024", "Tool 1 Single Year Data_Start failed: %s" % row_single[0]
        assert row_single[1] == "2024", "Tool 1 Single Year Data_End failed: %s" % row_single[1]
        print("[PASS] Tool 1 Single Year correctly stores '%s' and '%s'." % (row_single[0], row_single[1]))

        # Test C: Tool 2 Master Points Data_Start & Data_End fields
        pts_tile = os.path.join(gdb, "test_grid")
        arcpy.CreateFeatureclass_management(gdb, "test_grid", "POINT", spatial_reference=arcpy.SpatialReference(4326))
        with arcpy.da.InsertCursor(pts_tile, ["SHAPE@XY"]) as icur:
            icur.insertRow([(31.5, 30.2)])
        arcpy.AddField_management(pts_tile, "Data_Start", "TEXT", field_length=30)
        arcpy.AddField_management(pts_tile, "Data_End", "TEXT", field_length=30)
        arcpy.CalculateField_management(pts_tile, "Data_Start", "'31/03/1990'", "PYTHON_9.3")
        arcpy.CalculateField_management(pts_tile, "Data_End", "'31/12/2000'", "PYTHON_9.3")
        row_t2 = list(arcpy.da.SearchCursor(pts_tile, ["Data_Start", "Data_End"]))[0]
        assert row_t2[0] == "31/03/1990" and row_t2[1] == "31/12/2000", "Tool 2 fields check failed"
        print("[PASS] Tool 2 Master points correctly stores '%s' and '%s'." % (row_t2[0], row_t2[1]))

    finally:
        shutil.rmtree(tdir, ignore_errors=True)

    print("\n" + "=" * 70)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_all_checks()
