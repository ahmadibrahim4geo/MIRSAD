# -*- coding: utf-8 -*-
"""
Test Suite: Multi-Level Smart Variable, Season, and Field Filtering System
Target: POWER_Climate_Atlas_Generator_10_8.pyt
Environment: ArcGIS Desktop 10.8 (Python 2.7)
"""
import os
import sys

_test_dir = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(_test_dir)
PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(PYT):
    PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt"))

mod = type(sys)("mfilter")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = ("PASS " if cond else "FAIL ") + name
    if detail != "":
        line += " | " + str(detail)
    print(line)

print("=== 1. Candidate Fields Generation (get_candidate_fields) ===")
# All candidates for Temperature & Dew Point
c_temp = mod.get_candidate_fields(["Temperature"])
check("Temperature has 10 candidate fields", len(c_temp) == 10, len(c_temp))
check("Temperature excludes Td_Winter_Mean", "Td_Winter_Mean" not in [c[0] for c in c_temp])

c_dp = mod.get_candidate_fields(["Dew Point"])
check("Dew Point has 6 candidate fields", len(c_dp) == 6, len(c_dp))
check("Dew Point contains Td_Winter_Mean", "Td_Winter_Mean" in [c[0] for c in c_dp])

# Summer only for Temperature & Dew Point
c_sum = mod.get_candidate_fields(["Temperature"], ["Seasonal Summaries"], ["Summer (JJA)"])
sum_names = [c[0] for c in c_sum]
check("Summer only has 2 temperature fields", len(sum_names) == 2, sum_names)
check("Summer contains T_Summer_Mean", "T_Summer_Mean" in sum_names)
check("Summer contains T_Max_Summer_Month_Mean", "T_Max_Summer_Month_Mean" in sum_names)
check("Summer excludes T_Winter_Mean", "T_Winter_Mean" not in sum_names)
check("Summer excludes Td_Summer_Mean", "Td_Summer_Mean" not in sum_names)

c_sum_dp = mod.get_candidate_fields(["Dew Point"], ["Seasonal Summaries"], ["Summer (JJA)"])
sum_dp_names = [c[0] for c in c_sum_dp]
check("Summer Dew Point contains Td_Summer_Mean", "Td_Summer_Mean" in sum_dp_names)

# Winter only for Temperature & Dew Point
c_win_t = mod.get_candidate_fields(["Temperature"], ["Seasonal Summaries"], ["Winter (DJF)"])
win_t_names = [c[0] for c in c_win_t]
check("Winter temperature has 2 fields", len(win_t_names) == 2, win_t_names)
check("Winter excludes Td_Winter_Mean", "Td_Winter_Mean" not in win_t_names)

c_win_dp = mod.get_candidate_fields(["Dew Point"], ["Seasonal Summaries"], ["Winter (DJF)"])
win_dp_names = [c[0] for c in c_win_dp]
check("Winter Dew Point contains Td_Winter_Mean", "Td_Winter_Mean" in win_dp_names)

# Winter only for Precipitation
c_win_p = mod.get_candidate_fields(["Precipitation"], ["Seasonal Summaries"], ["Winter (DJF)"])
win_p_names = [c[0] for c in c_win_p]
check("Winter precip only has R_Winter_Mean", win_p_names == ["R_Winter_Mean"], win_p_names)

# Annual only for Precipitation
c_ann_p = mod.get_candidate_fields(["Precipitation"], ["Annual Summaries"], [])
ann_p_names = [c[0] for c in c_ann_p]
check("Annual precip has R_Annual_Mean and R_Annual_Range",
      "R_Annual_Mean" in ann_p_names and "R_Annual_Range" in ann_p_names and "R_Month_Mean" not in ann_p_names, ann_p_names)

print("=== 2. Field Resolution Engine (resolve_filtered_fields) ===")
# Mode: Full Suite
res_full = mod.resolve_filtered_fields(["Temperature", "Precipitation", "Dew Point"],
                                       "All Variables & Fields (Full Suite) [Recommended]")
check("Full Suite includes all Temperature fields",
      len(res_full["Temperature"]) == len(mod.MODULE_FIELDS["Temperature"]))
check("Full Suite includes all Precipitation fields",
      len(res_full["Precipitation"]) == len(mod.MODULE_FIELDS["Precipitation"]))
check("Full Suite includes all Dew Point fields",
      len(res_full["Dew Point"]) == len(mod.MODULE_FIELDS["Dew Point"]))

# Mode: Filter by Seasons - Summer only across Temperature, Precipitation, Dew Point
res_sum = mod.resolve_filtered_fields(
    ["Temperature", "Precipitation", "Dew Point"],
    "Filter by Seasons & Aggregations",
    aggregations=["Seasonal Summaries"],
    seasons=["Summer (JJA)"]
)
check("Seasons filter: Temperature has summer fields",
      res_sum["Temperature"] == ["T_Summer_Mean", "T_Max_Summer_Month_Mean"],
      res_sum["Temperature"])
check("Seasons filter: Dew Point has summer dew point",
      res_sum["Dew Point"] == ["Td_Summer_Mean"],
      res_sum["Dew Point"])
check("Seasons filter: Precipitation has summer mean",
      res_sum["Precipitation"] == ["R_Summer_Mean"],
      res_sum["Precipitation"])

# Mode: Custom Field Checklist
custom_selection = [
    "T_Summer_Mean - Summer Mean Air Temperature",
    "R_Winter_Mean - Winter Mean Precipitation"
]
res_custom = mod.resolve_filtered_fields(
    ["Temperature", "Precipitation"],
    "Custom Field Checklist",
    custom_fields=custom_selection
)
check("Custom Checklist: Temperature has T_Summer_Mean only",
      res_custom["Temperature"] == ["T_Summer_Mean"], res_custom["Temperature"])
check("Custom Checklist: Precipitation has R_Winter_Mean only",
      res_custom["Precipitation"] == ["R_Winter_Mean"], res_custom["Precipitation"])

print("=== 2.5 Measurement Units Conversion & Mapping ===")
sample_f = {
    "T_Annual_Mean": 20.0, "T_Annual_Range": 10.0, "T_Annual_Anom": 0.5,
    "T_Max_Summer_Month_Mean": 35.0, "T_Min_Winter_Month_Mean": 10.0,
    "R_Annual_Mean": 100.0, "R_Annual_Anom_Pct": 15.0,
    "PS_Annual_Mean": 1013.25,
    "W_Spd_Annual_Mean": 5.0, "W_Dir_Annual_Mean": 350.0,
    "Sol_Annual_Mean": 5.5
}
f_conv = mod.convert_fields_to_user_units(
    sample_f,
    unit_temp="Fahrenheit",
    unit_precip="Inches",
    unit_press="inHg",
    unit_wind="mph",
    unit_solar="MJ"
)
check("Temperature mean converts to Fahrenheit", f_conv["T_Annual_Mean"] == 68.0, f_conv["T_Annual_Mean"])
check("Temperature range converts delta (1.8x)", f_conv["T_Annual_Range"] == 18.0, f_conv["T_Annual_Range"])
check("Temperature anomaly converts delta", f_conv["T_Annual_Anom"] == 0.9, f_conv["T_Annual_Anom"])
check("T Max Summer converts to Fahrenheit", f_conv["T_Max_Summer_Month_Mean"] == 95.0, f_conv["T_Max_Summer_Month_Mean"])
check("T Min Winter converts to Fahrenheit", f_conv["T_Min_Winter_Month_Mean"] == 50.0, f_conv["T_Min_Winter_Month_Mean"])
check("Precipitation converts to Inches", f_conv["R_Annual_Mean"] == 3.94, f_conv["R_Annual_Mean"])
check("Precipitation percentage anomaly unaffected", f_conv["R_Annual_Anom_Pct"] == 15.0, f_conv["R_Annual_Anom_Pct"])
check("Pressure converts to inHg", f_conv["PS_Annual_Mean"] == 29.92, f_conv["PS_Annual_Mean"])
check("Wind speed converts to mph", f_conv["W_Spd_Annual_Mean"] == 11.18, f_conv["W_Spd_Annual_Mean"])
check("Wind direction angle unaffected", f_conv["W_Dir_Annual_Mean"] == 350.0, f_conv["W_Dir_Annual_Mean"])
check("Solar radiation converts to MJ/m2/day", f_conv["Sol_Annual_Mean"] == 19.8, f_conv["Sol_Annual_Mean"])

u_map = mod.get_units_mapping(unit_solar="Kilowatt-hours per square meter per day (kWh/m2/day) [Default]")
check("Solar Radiation default unit is kWh/m2/day", u_map["Solar Radiation"] == "kWh/m²/day", u_map["Solar Radiation"])
u_map_mj = mod.get_units_mapping(unit_solar="Megajoules per square meter per day (MJ/m2/day)")
check("Solar Radiation unit MJ/m2/day", u_map_mj["Solar Radiation"] == "MJ/m²/day", u_map_mj["Solar Radiation"])

print("=== 3. Toolbox Parameters & Dynamic GUI Synchronization ===")
try:
    import arcpy
except ImportError:
    print("SKIP Section 3: arcpy not available")
    print("\n==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
    sys.exit(0 if not FAIL else 1)
tool = mod.PowerClimateAtlasGenerator()
ps = tool.getParameterInfo()
check("Total parameters is 60", len(ps) == 60, len(ps))

pdict = dict((p.name, p) for p in ps)
check("Field_Filter_Scope exists", "Field_Filter_Scope" in pdict)
check("Included_Aggregations exists", "Included_Aggregations" in pdict)
check("Included_Seasons exists", "Included_Seasons" in pdict)
check("Selected_Fields exists", "Selected_Fields" in pdict)
check("Enable_Raster_Reclass exists", "Enable_Raster_Reclass" in pdict)
check("Reclass_Classes_Count exists", "Reclass_Classes_Count" in pdict)
check("Reclass_Method exists", "Reclass_Method" in pdict)
check("Measurement_Units_System exists", "Measurement_Units_System" in pdict)
check("Temperature_Unit exists", "Temperature_Unit" in pdict)
check("Precipitation_Unit exists", "Precipitation_Unit" in pdict)
check("Pressure_Unit exists", "Pressure_Unit" in pdict)
check("Wind_Speed_Unit exists", "Wind_Speed_Unit" in pdict)
check("Solar_Radiation_Unit exists", "Solar_Radiation_Unit" in pdict)
check("Study_Area_Name defaults to None", pdict["Study_Area_Name"].value is None)
check("Climate_Modules defaults to None", pdict["Climate_Modules"].value is None)
check("Input_Point_Features is Required", pdict["Input_Point_Features"].parameterType == "Required")
check("Enable_Raster_Reclass default False", pdict["Enable_Raster_Reclass"].value == False)

# Check positions and display names
names = [p.name for p in ps]
cm_idx = names.index("Climate_Modules")
scope_idx = names.index("Field_Filter_Scope")
check("Climate_Modules exists in parameters", cm_idx >= 0)
check("Field_Filter_Scope exists and follows module selection", scope_idx > cm_idx)
check("Included_Aggregations follows scope", names[scope_idx + 1] == "Included_Aggregations")
check("Included_Seasons follows at index + 2", names[scope_idx + 2] == "Included_Seasons")
check("Selected_Fields checklist is at index + 3", names[scope_idx + 3] == "Selected_Fields")
check("Selected_Fields displayName contains Variables",
      "Variables" in pdict["Selected_Fields"].displayName)
check("Field_Filter_Scope category is Variable & Field Selection",
      pdict["Field_Filter_Scope"].category == "Variable & Field Selection")

# Test dynamic state in updateParameters:
# Default: Full Suite -> sub-filters disabled
tool.updateParameters(ps)
check("Default Full Suite disables Included_Aggregations", not pdict["Included_Aggregations"].enabled)
check("Default Full Suite disables Included_Seasons", not pdict["Included_Seasons"].enabled)
check("Default Full Suite disables Selected_Fields", not pdict["Selected_Fields"].enabled)
check("Default disables Reclass_Classes_Count", not pdict["Reclass_Classes_Count"].enabled)
check("Default disables Reclass_Method", not pdict["Reclass_Method"].enabled)

# Test dynamic toggle of reclass options
pdict["Enable_Raster_Reclass"].value = True
tool.updateParameters(ps)
check("Enabling reclass enables Reclass_Classes_Count", pdict["Reclass_Classes_Count"].enabled)
check("Enabling reclass enables Reclass_Method", pdict["Reclass_Method"].enabled)
pdict["Enable_Raster_Reclass"].value = False
tool.updateParameters(ps)

# Switch to Filter by Seasons & Aggregations
pdict["Field_Filter_Scope"].value = "Filter by Seasons & Aggregations"
pdict["Included_Aggregations"].value = "Seasonal Summaries"
tool.updateParameters(ps)
check("Seasons mode enables Included_Aggregations", pdict["Included_Aggregations"].enabled)
check("Seasons mode enables Included_Seasons when Seasonal in aggs", pdict["Included_Seasons"].enabled)
check("Seasons mode keeps Selected_Fields disabled", not pdict["Selected_Fields"].enabled)

# Switch to Custom Field Checklist
pdict["Field_Filter_Scope"].value = "Custom Field Checklist"
pdict["Climate_Modules"].value = "Precipitation"
pdict["Included_Aggregations"].value = "Annual Summaries;Seasonal Summaries;Extreme & Bioclimatic Indices"
tool.updateParameters(ps)
check("Custom Checklist enables Selected_Fields", pdict["Selected_Fields"].enabled)
check("Selected_Fields checklist updated for Precipitation",
      any("R_Annual_Total" in item for item in pdict["Selected_Fields"].filter.list),
      pdict["Selected_Fields"].filter.list)

# Switch back to All Variables
pdict["Field_Filter_Scope"].value = "All Variables & Fields (Full Suite) [Recommended]"
tool.updateParameters(ps)
check("Full Suite disables sub-filters again",
      not pdict["Included_Aggregations"].enabled and not pdict["Selected_Fields"].enabled)

print("=== 4. Validation & updateMessages ===")
tool.updateMessages(ps)
check("No error on default settings", not pdict["Field_Filter_Scope"].hasError())

# Switch to Custom Checklist with empty selection
pdict["Field_Filter_Scope"].value = "Custom Field Checklist"
pdict["Selected_Fields"].value = ""
tool.updateMessages(ps)
check("Empty custom selection sets error", pdict["Selected_Fields"].hasError())

# Reset
pdict["Selected_Fields"].value = "R_Winter_Mean - Winter Mean Precipitation"
tool.updateMessages(ps)
check("Valid selection clears error", not pdict["Selected_Fields"].hasError())

print("=== 5. Metadata Dictionaries and QA Integration ===")
rows = mod.metadata_rows_for_modules(["Temperature"], {"Temperature": ["T_Summer_Mean"]})
check("Metadata rows filtered to 1", len(rows) == 1 and rows[0]["Field_Name"] == "T_Summer_Mean",
      [r["Field_Name"] for r in rows])

print("\n-----------------------------------------")
print("TEST SUMMARY: %d PASS, %d FAIL" % (len(PASS), len(FAIL)))
print("-----------------------------------------")
if FAIL:
    sys.exit(1)
