r"""
Update Egypt Climate Database with Measurement Units column for all feature classes.
Target: C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025\Climate_Database_From_1996_To_2025.gdb
"""
import os
import arcpy

GDB_PATH = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025\Climate_Database_From_1996_To_2025.gdb"

MODULE_UNITS = {
    "Temperature": "°C",
    "Precipitation": "mm",
    "Sea_Level_Pressure": "hPa",
    "Surface_Pressure": "hPa",
    "Wind": "m/s",
    "Relative_Humidity": "%",
    "Dew_Point": "°C",
    "Solar_Radiation": "MJ/m²/day",
    "UV_Index": "Index",
    "Cloud_Cover": "%",
    "Heat_Index": "°C",
    "Wind_Chill": "°C",
    "De_Martonne_Aridity": "Index",
    "Evapotranspiration": "mm",
    "UNEP_Aridity": "Index",
    "Water_Deficit": "mm",
    "Dry_Months": "Months",
    "Trends_And_Anomalies": "°C/dec",
    "Wind_Vector_Annual": "m/s, °",
    "Wind_Vector_Winter": "m/s, °",
    "Wind_Vector_Spring": "m/s, °",
    "Wind_Vector_Summer": "m/s, °",
    "Wind_Vector_Autumn": "m/s, °",
}

def update_database_units():
    print(f"Connecting to Geodatabase: {GDB_PATH}")
    arcpy.env.workspace = GDB_PATH
    fcs = arcpy.ListFeatureClasses()
    print(f"Found {len(fcs)} feature classes.")

    updated_count = 0
    for fc in fcs:
        unit_val = None
        for mod_key, u in MODULE_UNITS.items():
            if fc.lower() == mod_key.lower():
                unit_val = u
                break
        if not unit_val:
            if "isobars" in fc.lower():
                unit_val = "hPa"
            elif "vector" in fc.lower():
                unit_val = "m/s, °"
            else:
                continue

        fc_path = os.path.join(GDB_PATH, fc)
        fields = [f.name for f in arcpy.ListFields(fc_path)]
        if "Measurement_Unit" not in fields:
            arcpy.management.AddField(fc_path, "Measurement_Unit", "TEXT", field_length=25, field_alias="Measurement_Unit")
            print(f"  Added 'Measurement_Unit' field to {fc}")

        with arcpy.da.UpdateCursor(fc_path, ["Measurement_Unit"]) as cur:
            for row in cur:
                row[0] = unit_val
                cur.updateRow(row)

        # Delete old 'Unit' field if present to keep geodatabase 100% clean
        if "Unit" in fields:
            try:
                arcpy.management.DeleteField(fc_path, "Unit")
                print(f"  Deleted old 'Unit' field from {fc}")
            except Exception as e:
                print(f"  Note on deleting Unit from {fc}: {e}")

        row_count = int(arcpy.GetCount_management(fc_path)[0])
        print(f"  [OK] {fc}: populated {row_count} rows with Measurement_Unit = '{unit_val}'")
        updated_count += 1

    print(f"\nSuccessfully updated {updated_count} feature classes with Measurement_Unit!")

if __name__ == "__main__":
    update_database_units()
