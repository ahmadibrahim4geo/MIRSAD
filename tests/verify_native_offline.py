# -*- coding: utf-8 -*-
r"""Opt-in native ArcGIS smoke test; creates a fresh isolated workspace.

Run explicitly with ArcGIS Python, e.g.:
    C:\Python27\ArcGIS10.8\python.exe -B -u tests\verify_native_offline.py
No network requests, existing datasets, or CURRENT map are used.
"""
from __future__ import print_function
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class Messages(object):
    def addMessage(self, text):
        print(text)
        sys.stdout.flush()

    addWarning = addMessage
    addWarningMessage = addMessage
    addErrorMessage = addMessage


def main():
    print("STAGE 1: import ArcPy")
    sys.stdout.flush()
    import arcpy
    print("STAGE 2: initialize native geoprocessor (%s)" % sys.version.split()[0])
    sys.stdout.flush()
    arcpy.Exists(ROOT)
    print("STAGE 3: create isolated test data")
    sys.stdout.flush()
    base = os.path.join(ROOT, "tests", "logs")
    if not os.path.isdir(base):
        os.makedirs(base)
    run = tempfile.mkdtemp(prefix="native_offline_", dir=base)
    if not os.path.abspath(run).startswith(os.path.abspath(base) + os.sep):
        raise RuntimeError("Test output escaped the intended workspace")
    print("TEST WORKSPACE: " + run)
    sr = arcpy.SpatialReference(3857)
    gdb = os.path.join(run, "inputs.gdb")
    arcpy.CreateFileGDB_management(run, "inputs.gdb")
    points = os.path.join(gdb, "01_Temperature")
    arcpy.CreateFeatureclass_management(gdb, "01_Temperature", "POINT", spatial_reference=sr)
    arcpy.AddField_management(points, "T_Annual_Mean", "DOUBLE")
    arcpy.AddField_management(points, "Data_Start", "TEXT", field_length=30)
    arcpy.AddField_management(points, "Data_End", "TEXT", field_length=30)
    with arcpy.da.InsertCursor(points, ["SHAPE@XY", "T_Annual_Mean", "Data_Start", "Data_End"]) as cursor:
        for xy, value in [((1000, 1000), 20.0), ((9000, 1000), 22.0),
                          ((1000, 9000), 24.0), ((9000, 9000), 26.0)]:
            cursor.insertRow([xy, value, "1996", "2025"])
    mask = os.path.join(gdb, "mask")
    arcpy.CreateFeatureclass_management(gdb, "mask", "POLYGON", spatial_reference=sr)
    ring = arcpy.Array([arcpy.Point(x, y) for x, y in
                        [(0, 0), (10000, 0), (10000, 10000), (0, 10000), (0, 0)]])
    with arcpy.da.InsertCursor(mask, ["SHAPE@"]) as cursor:
        cursor.insertRow([arcpy.Polygon(ring, sr)])
    if sys.version_info[0] >= 3:
        from importlib.machinery import SourceFileLoader
        core = SourceFileLoader("native_test_core", os.path.join(ROOT, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")).load_module()
    else:
        import imp
        core = imp.load_source("native_test_core", os.path.join(ROOT, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt"))
    import raster_atlas_generator as raster
    cases = [(core.PowerClimateAtlasGenerator(), "points",
              {"Study_Area_Mask": mask, "Base_Cell_Size": "1000 Meters",
               "Field_Filter_Scope": "Custom Field Selection", "Selected_Fields": "T_Annual_Mean",
               "Add_To_Map": False}),
             (raster.RasterDataClimateAtlasGenerator(), "raster",
              {"Final_Clip_Layer": mask, "Output_Cell_Size": 1000})]
    arcpy.env.mask = mask
    arcpy.env.cellSize = 777
    for tool, label, extra in cases:
        print("STAGE 4: execute " + label)
        sys.stdout.flush()
        params = tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)
        settings = {"Operation_Mode": "Interpolate & Map Existing Data (Offline Mode - No Internet)",
                    "Precalculated_Point_Layers": points, "Climate_Modules": "Temperature",
                    "Output_Workspace": os.path.join(run, label), "Output_Spatial_Reference": sr,
                    "Temporal_Scope": "Annual", "Study_Area_Name": "Native_Regression"}
        settings.update(extra)
        for name, value in settings.items():
            pdict[name].value = value
        tool.execute(params, Messages())
        result = os.path.join(settings["Output_Workspace"], "01_Temperature", "T_Annual_Mean.tif")
        if not arcpy.Exists(result):
            raise AssertionError("Missing output raster: " + result)
        low = float(arcpy.GetRasterProperties_management(result, "MINIMUM").getOutput(0))
        high = float(arcpy.GetRasterProperties_management(result, "MAXIMUM").getOutput(0))
        if not (20.0 <= low <= high <= 26.0):
            raise AssertionError("Unexpected interpolated values: %r" % ((low, high),))
        desc = arcpy.Describe(result)
        if desc.extent.XMin < -1000 or desc.extent.XMax > 11000:
            raise AssertionError("Raster escaped the study mask")
        if abs(float(arcpy.env.cellSize) - 777.0) > 1e-9 or str(arcpy.env.mask) != mask:
            raise AssertionError("Tool changed caller environment")
        print("PASS: %s raster, mask, values and environment" % label)
    print("NATIVE OFFLINE VERIFICATION PASSED: " + run)


if __name__ == "__main__":
    main()
