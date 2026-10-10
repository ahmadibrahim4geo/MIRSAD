# -*- coding: utf-8 -*-
import os
import sys
import json
import arcpy

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

BASE_DIR = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
GDB_PATH = os.path.join(BASE_DIR, "Climate_Database_From_1996_To_2025.gdb")
MASK_FC = os.path.join(GDB_PATH, "Egypt")
REF_RASTER = os.path.join(BASE_DIR, "01_Temperature", "T_Annual_Mean.tif")
STAGING_DIR = os.path.join(BASE_DIR, "19_Land_Surface_Temperature_STAGING")
RASTER_DIR = os.path.join(BASE_DIR, "19_Land_Surface_Temperature")
CALC_JSON = os.path.join(BASE_DIR, "00_Tables_And_Reports", "egypt_lst_calculated_646.json")

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

LST_INDICATOR_FIELDS = [
    "LST_Annual_Mean", "LST_Month_Mean", "LST_Winter_Mean", "LST_Spring_Mean",
    "LST_Summer_Mean", "LST_Autumn_Mean", "LST_Annual_Range", "LST_Seasonal_Range",
    "LST_minus_T_Annual", "LST_minus_T_Winter", "LST_minus_T_Spring",
    "LST_minus_T_Summer", "LST_minus_T_Autumn"
] + ["LST_%s_Mean" % m for m in MONTH_NAMES] + ["LST_minus_T_%s" % m for m in MONTH_NAMES]

SHP_MAP = {
    "LST_Annual_Mean": "LST_AnMean",
    "LST_Month_Mean": "LST_MonMn",
    "LST_Winter_Mean": "LST_WinMn",
    "LST_Spring_Mean": "LST_SprMn",
    "LST_Summer_Mean": "LST_SumMn",
    "LST_Autumn_Mean": "LST_AutMn",
    "LST_Annual_Range": "LST_AnRng",
    "LST_Seasonal_Range": "LST_SeaRng",
    "LST_minus_T_Annual": "LST_mT_Ann",
    "LST_minus_T_Winter": "LST_mT_Win",
    "LST_minus_T_Spring": "LST_mT_Spr",
    "LST_minus_T_Summer": "LST_mT_Sum",
    "LST_minus_T_Autumn": "LST_mT_Aut",
    "LST_January_Mean": "LST_JanMn",
    "LST_February_Mean": "LST_FebMn",
    "LST_March_Mean": "LST_MarMn",
    "LST_April_Mean": "LST_AprMn",
    "LST_May_Mean": "LST_MayMn",
    "LST_June_Mean": "LST_JunMn",
    "LST_July_Mean": "LST_JulMn",
    "LST_August_Mean": "LST_AugMn",
    "LST_September_Mean": "LST_SepMn",
    "LST_October_Mean": "LST_OctMn",
    "LST_November_Mean": "LST_NovMn",
    "LST_December_Mean": "LST_DecMn",
    "LST_minus_T_January": "LST_mT_Jan",
    "LST_minus_T_February": "LST_mT_Feb",
    "LST_minus_T_March": "LST_mT_Mar",
    "LST_minus_T_April": "LST_mT_Apr",
    "LST_minus_T_May": "LST_mT_May",
    "LST_minus_T_June": "LST_mT_Jun",
    "LST_minus_T_July": "LST_mT_Jul",
    "LST_minus_T_August": "LST_mT_Aug",
    "LST_minus_T_September": "LST_mT_Sep",
    "LST_minus_T_October": "LST_mT_Oct",
    "LST_minus_T_November": "LST_mT_Nov",
    "LST_minus_T_December": "LST_mT_Dec",
}

RASTERS_TO_BUILD = [
    "LST_Annual_Mean",
    "LST_Winter_Mean",
    "LST_Spring_Mean",
    "LST_Summer_Mean",
    "LST_Autumn_Mean",
    "LST_Annual_Range",
    "LST_Seasonal_Range",
    "LST_minus_T_Annual",
    "LST_minus_T_Winter",
    "LST_minus_T_Spring",
    "LST_minus_T_Summer",
    "LST_minus_T_Autumn",
]


def step1_create_gdb_feature_class(data):
    fc_name = "Land_Surface_Temperature"
    fc_path = os.path.join(GDB_PATH, fc_name)
    if arcpy.Exists(fc_path):
        print("Feature Class %s already exists, deleting for clean recreate..." % fc_name)
        arcpy.Delete_management(fc_path)

    sr = arcpy.SpatialReference(3857)
    arcpy.CreateFeatureclass_management(GDB_PATH, fc_name, "POINT", spatial_reference=sr)
    print("Created Feature Class: %s" % fc_path)

    admin_fields = [
        ("Source_ID", "LONG", "Source_ID"),
        ("Point_Lat", "DOUBLE", "Point_Lat"),
        ("Point_Lon", "DOUBLE", "Point_Lon"),
        ("Data_Start", "TEXT", "Data_Start", 10),
        ("Data_End", "TEXT", "Data_End", 10),
        ("Temporal", "TEXT", "Temporal", 20),
        ("Interp_Meth", "TEXT", "Interp_Meth", 50),
        ("Cell_Size", "DOUBLE", "Cell_Size"),
        ("Wind_Cell", "DOUBLE", "Wind_Cell"),
        ("Status", "TEXT", "Status", 20),
        ("Error_Msg", "TEXT", "Error_Msg", 50),
    ]

    for f_info in admin_fields:
        fname, ftype, falias = f_info[:3]
        flen = f_info[3] if len(f_info) > 3 else None
        arcpy.AddField_management(fc_path, fname, ftype, field_length=flen, field_alias=falias)

    for fld in LST_INDICATOR_FIELDS:
        arcpy.AddField_management(fc_path, fld, "DOUBLE", field_alias=fld)

    print("Added all admin and indicator fields to %s" % fc_name)

    # Insert rows
    cursor_fields = ["SHAPE@XY", "Source_ID", "Point_Lat", "Point_Lon", "Data_Start", "Data_End",
                     "Temporal", "Interp_Meth", "Cell_Size", "Wind_Cell", "Status", "Error_Msg"] + LST_INDICATOR_FIELDS

    with arcpy.da.InsertCursor(fc_path, cursor_fields) as cur:
        for r in data:
            row_vals = [
                (float(r["X_3857"]), float(r["Y_3857"])),
                int(r["Source_ID"]),
                float(r["Point_Lat"]),
                float(r["Point_Lon"]),
                str(r["Data_Start"]),
                str(r["Data_End"]),
                str(r["Temporal"]),
                str(r["Interp_Meth"]),
                float(r["Cell_Size"]),
                float(r["Wind_Cell"]),
                str(r["Status"]),
                str(r["Error_Msg"]),
            ]
            for fld in LST_INDICATOR_FIELDS:
                row_vals.append(float(r[fld]) if r.get(fld) is not None else None)
            cur.insertRow(row_vals)

    count = int(arcpy.GetCount_management(fc_path)[0])
    print("Inserted %d rows into %s." % (count, fc_path))
    return fc_path


def step2_export_shapefile(fc_path):
    shp_name = "19_Land_Surface_Temperature_Grid_Points.shp"
    shp_path = os.path.join(STAGING_DIR, shp_name)
    if arcpy.Exists(shp_path):
        arcpy.Delete_management(shp_path)

    # Use FeatureClassToFeatureClass with field mappings for <=10 char names
    fms = arcpy.FieldMappings()
    fms.addTable(fc_path)

    # Remap long field names to short <= 10 char names
    for long_fld, short_fld in SHP_MAP.items():
        f_idx = fms.findFieldMapIndex(long_fld)
        if f_idx >= 0:
            fm = fms.getFieldMap(f_idx)
            out_fld = fm.outputField
            out_fld.name = short_fld
            out_fld.aliasName = long_fld
            fm.outputField = out_fld
            fms.replaceFieldMap(f_idx, fm)

    arcpy.FeatureClassToFeatureClass_conversion(fc_path, STAGING_DIR, shp_name, field_mapping=fms)
    print("Exported Shapefile with <=10 char fields: %s" % shp_path)


def step3_interpolate_rasters(fc_path):
    if not os.path.exists(RASTER_DIR):
        os.makedirs(RASTER_DIR)

    from arcpy.sa import Spline, ExtractByMask

    # Setup environment
    arcpy.env.snapRaster = REF_RASTER
    arcpy.env.cellSize = 250.0
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)
    arcpy.env.compression = "LZW"
    arcpy.ClearEnvironment("mask")
    arcpy.ClearEnvironment("extent")

    print("\n--- Starting Spline Interpolation for 9 Rasters ---")
    for fld in RASTERS_TO_BUILD:
        out_tif = os.path.join(RASTER_DIR, "%s.tif" % fld)
        print("Interpolating %s -> %s" % (fld, out_tif))
        # Spline: in_point_features, z_field, cell_size, spline_type, weight, number_points
        surf = Spline(fc_path, fld, 250.0, "TENSION", 30.0, 12)
        # Mask by Egypt boundary
        clipped = ExtractByMask(surf, MASK_FC)
        clipped.save(out_tif)

        # Build pyramids & compute stats
        arcpy.CalculateStatistics_management(out_tif)
        arcpy.BuildPyramids_management(out_tif)
        print("  -> Saved & calculated stats for %s.tif" % fld)

    print("\nAll 9 rasters successfully generated in %s" % RASTER_DIR)


def main():
    with open(CALC_JSON, "r") as f:
        data = json.load(f)

    fc_path = step1_create_gdb_feature_class(data)
    step2_export_shapefile(fc_path)
    # Note: Rasters are NOT generated per user constraint:
    # "لا تقوم بعمل الراستر لان انا لا احتاجه في شغلي حاليا"
    # The 12 existing rasters remain intact.
    # step3_interpolate_rasters(fc_path)
    print("\nArcGIS Feature Class and Shapefile successfully updated with all 37 fields!")


if __name__ == "__main__":
    main()
