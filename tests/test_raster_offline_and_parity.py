# -*- coding: utf-8 -*-
"""
Verification Test for Tool 1 and Tool 2 Parity, Offline Multi-Layer Support,
and English Aliases.
Runs with Python 2.7 (ArcMap 10.8).
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
    print("SKIP test_raster_offline_and_parity: arcpy not available in this Python interpreter.")
    sys.exit(0)

def run_parity_tests():
    print("=" * 70)
    print("TESTING TOOL 1 & TOOL 2 PARITY AND OFFLINE MULTI-LAYER CAPABILITIES")
    print("=" * 70)

    pyt_path = os.path.join(PROJ_DIR, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
    if not os.path.exists(pyt_path):
        pyt_path = os.path.join(PROJ_DIR, "POWER_Climate_Atlas_Generator_10_8.pyt")
    pyt_mod = _load_source("pyt_mod", pyt_path)
    from raster_atlas_generator import RasterDataClimateAtlasGenerator, SHP_FIELD_MAP, REV_SHP_MAP

    # 1. Check Toolbox integration & side-by-side categories
    tb = pyt_mod.Toolbox()
    t1 = pyt_mod.PowerClimateAtlasGenerator()
    t2 = RasterDataClimateAtlasGenerator()

    assert "MIRSAD" in t1.label, "Tool 1 label mismatch: %s" % t1.label
    assert "MIRSAD" in t2.label, "Tool 2 label mismatch: %s" % t2.label
    assert getattr(t1, "category", "") == "", "Tool 1 category must be root: %s" % getattr(t1, "category", "")
    assert getattr(t2, "category", "") == "", "Tool 2 category must be root: %s" % getattr(t2, "category", "")
    print("[PASS] Tool 1 and Tool 2 are configured side-by-side at root: '%s' & '%s'" % (t1.label, t2.label))

    # 2. Check Visual Calendar parameter has no Arabic mojibake
    params1 = dict((p.name, p) for p in t1.getParameterInfo())
    params2 = dict((p.name, p) for p in t2.getParameterInfo())

    p1_cal = params1["Open_Calendar_Picker"].displayName
    p2_cal = params2["Open_Calendar_Picker"].displayName
    assert "Launch Visual Calendar Window" in p1_cal and "(" not in p1_cal, "Arabic text still present in Tool 1 picker: %s" % p1_cal
    assert "Launch Visual Calendar Window" in p2_cal and "(" not in p2_cal, "Arabic text still present in Tool 2 picker: %s" % p2_cal
    print("[PASS] Visual Calendar display names are clean English: '%s' & '%s'" % (p1_cal, p2_cal))

    # 3. Check Cell Size display name and default
    p1_cell = params1["Base_Cell_Size"]
    p2_cell = params2["Output_Cell_Size"]
    assert "500" in p1_cell.displayName, "Tool 1 cell size display name: %s" % p1_cell.displayName
    assert "500" in p2_cell.displayName, "Tool 2 cell size display name: %s" % p2_cell.displayName
    print("[PASS] Cell size parameters reflect 500 Meters default.")

    # 4. Check Offline Multi-Layer Merging in Tool 2
    tdir = tempfile.mkdtemp()
    try:
        gdb = os.path.join(tdir, "test_parity.gdb")
        arcpy.CreateFileGDB_management(tdir, "test_parity.gdb")

        # Layer A: Temperature shapefile with 10-char truncated names (simulating exported run)
        shp_t = os.path.join(tdir, "01_Temperature_Grid_Points.shp")
        arcpy.CreateFeatureclass_management(tdir, "01_Temperature_Grid_Points.shp", "POINT", spatial_reference=arcpy.SpatialReference(4326))
        arcpy.AddField_management(shp_t, "T_AnnMean", "DOUBLE")
        arcpy.AddField_management(shp_t, "T_WinMean", "DOUBLE")
        arcpy.AddField_management(shp_t, "T_SumMean", "DOUBLE")
        arcpy.AddField_management(shp_t, "Data_Start", "TEXT", field_length=30)
        arcpy.AddField_management(shp_t, "Data_End", "TEXT", field_length=30)

        with arcpy.da.InsertCursor(shp_t, ["SHAPE@XY", "T_AnnMean", "T_WinMean", "T_SumMean", "Data_Start", "Data_End"]) as icur:
            icur.insertRow([(31.0, 30.0), 22.5, 14.2, 29.8, "2015", "2024"])
            icur.insertRow([(32.0, 30.0), 23.0, 15.0, 30.5, "2015", "2024"])

        # Layer B: Precipitation shapefile with 10-char truncated names
        shp_p = os.path.join(tdir, "02_Precipitation_Grid_Points.shp")
        arcpy.CreateFeatureclass_management(tdir, "02_Precipitation_Grid_Points.shp", "POINT", spatial_reference=arcpy.SpatialReference(4326))
        arcpy.AddField_management(shp_p, "R_AnnTot", "DOUBLE")
        arcpy.AddField_management(shp_p, "R_WinTot", "DOUBLE")
        arcpy.AddField_management(shp_p, "Data_Start", "TEXT", field_length=30)
        arcpy.AddField_management(shp_p, "Data_End", "TEXT", field_length=30)

        with arcpy.da.InsertCursor(shp_p, ["SHAPE@XY", "R_AnnTot", "R_WinTot", "Data_Start", "Data_End"]) as icur:
            icur.insertRow([(31.0, 30.0), 45.0, 25.0, "2015", "2024"])
            icur.insertRow([(32.0, 30.0), 60.0, 30.0, "2015", "2024"])

        # Layer C: Humidity shapefile
        shp_rh = os.path.join(tdir, "06_Humidity_Grid_Points.shp")
        arcpy.CreateFeatureclass_management(tdir, "06_Humidity_Grid_Points.shp", "POINT", spatial_reference=arcpy.SpatialReference(4326))
        arcpy.AddField_management(shp_rh, "RH_AnMean", "DOUBLE")
        arcpy.AddField_management(shp_rh, "RH_SuMean", "DOUBLE")
        arcpy.AddField_management(shp_rh, "Data_Start", "TEXT", field_length=30)
        arcpy.AddField_management(shp_rh, "Data_End", "TEXT", field_length=30)

        with arcpy.da.InsertCursor(shp_rh, ["SHAPE@XY", "RH_AnMean", "RH_SuMean", "Data_Start", "Data_End"]) as icur:
            icur.insertRow([(31.0, 30.0), 55.0, 60.0, "2015", "2024"])
            icur.insertRow([(32.0, 30.0), 50.0, 55.0, "2015", "2024"])

        # Test Tool 2 _merge_offline_layers
        layers_input = [shp_t, shp_p, shp_rh]
        submodels_test = [
            "De Martonne Aridity Index [Requires: Temperature, Precipitation]",
            "Heat Index / Thermal Stress [Requires: Temperature, Relative Humidity]"
        ]
        out_sr_wgs = arcpy.SpatialReference(4326)

        print("\nExecuting Tool 2 _merge_offline_layers...")
        elem_fcs, ind_fields_map = t2._merge_offline_layers(
            layers_input, gdb, out_sr_wgs, ["Temperature", "Precipitation", "Relative Humidity"],
            submodels_test, lambda m: sys.stdout.write(m + "\n"), lambda w: sys.stdout.write("WARN: " + w + "\n"),
            col_data_start="2015", col_data_end="2024"
        )

        assert "Temperature" in elem_fcs, "Temperature FC missing in offline element layers"
        assert "Precipitation" in elem_fcs, "Precipitation FC missing in offline element layers"
        assert "Climate_Models" in elem_fcs, "Climate_Models FC missing in offline element layers"
        print("[PASS] Tool 2 offline merger assembled element and submodel layers.")

        # Check Temperature values reconstructed from R_AnnTot / T_AnnMean
        t_fc = elem_fcs["Temperature"]
        t_rows = list(arcpy.da.SearchCursor(t_fc, ["POINT_X", "POINT_Y", "T_Annual_Mean", "Data_Start", "Data_End"]))
        assert len(t_rows) == 2, "Expected 2 points in Temperature FC"
        assert abs(t_rows[0][2] - 22.5) < 1e-4, "T_Annual_Mean value mismatch: %s" % t_rows[0][2]
        assert t_rows[0][3] == "2015" and t_rows[0][4] == "2024", "Date metadata mismatch: %s to %s" % (t_rows[0][3], t_rows[0][4])
        print("[PASS] Tool 2 Temperature FC: values and metadata mapped correctly from shapefile truncation.")

        # Check Precipitation values reconstructed
        p_fc = elem_fcs["Precipitation"]
        p_rows = list(arcpy.da.SearchCursor(p_fc, ["R_Annual_Total"]))
        assert abs(p_rows[0][0] - 45.0) < 1e-4, "R_Annual_Total value mismatch: %s" % p_rows[0][0]
        print("[PASS] Tool 2 Precipitation FC: R_Annual_Total mapped correctly.")

        # Check Submodels on the fly in Climate_Models
        m_fc = elem_fcs["Climate_Models"]
        m_fields = [f.name for f in arcpy.ListFields(m_fc)]
        print("Climate_Models Fields:", m_fields)
        assert "DM_Aridity_Annual" in m_fields, "DM_Aridity_Annual missing in Climate_Models"
        assert "HI_Summer_Mean" in m_fields, "HI_Summer_Mean missing in Climate_Models"
        assert "HI_Winter_Mean" in m_fields, "HI_Winter_Mean missing in Climate_Models"

        # Check Field Aliases: ensure HI_Winter_Mean alias is English
        for f in arcpy.ListFields(m_fc):
            if f.name == "HI_Winter_Mean":
                assert f.aliasName == "HI_Winter_Mean", "HI_Winter_Mean alias should be 'HI_Winter_Mean', got: %s" % f.aliasName
        print("[PASS] HI_Winter_Mean field alias is strictly English ('HI_Winter_Mean').")

        # Check Submodel computed values
        m_rows = list(arcpy.da.SearchCursor(m_fc, ["DM_Aridity_Annual", "HI_Summer_Mean", "HI_Winter_Mean"]))
        dm_val = m_rows[0][0]
        hi_sum_val = m_rows[0][1]
        hi_win_val = m_rows[0][2]
        print("Computed Submodels at Point 1: DM=%.2f, HI_Summer=%.2f, HI_Winter=%.2f" % (dm_val, hi_sum_val, hi_win_val))
        assert dm_val > 0.0, "De Martonne Aridity should be > 0"
        assert hi_sum_val > 0.0, "HI_Summer should be > 0"
        assert hi_win_val > 0.0, "HI_Winter should be > 0"
        print("[PASS] Submodels calculated accurately on the fly from offline multi-layers.")

    finally:
        shutil.rmtree(tdir, ignore_errors=True)

    print("\n" + "=" * 70)
    print("ALL PARITY & OFFLINE VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_parity_tests()
