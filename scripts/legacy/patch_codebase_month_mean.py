# -*- coding: utf-8 -*-
"""
Patches Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt and Toolboxes/raster_atlas_generator.py
to fully integrate *_Month_Mean fields, descriptive Arabic aliases, and shapefile mappings.
"""

import sys
import os

PYT_FILE = r"d:\My Software\NASA POWER Climate Atlas Generator\Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt"
RAG_FILE = r"d:\My Software\NASA POWER Climate Atlas Generator\Toolboxes/raster_atlas_generator.py"

# --- 1. PATCH Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt ---
print("Patching Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt...")
with open(PYT_FILE, "r", encoding="utf-8") as f:
    pyt_content = f.read()

# Add FIELD_DEFS entries
field_defs_insert = '''    ("T_Month_Mean", "Mean Monthly Air Temperature", u"المتوسط الشهري لدرجة الحرارة", "T2M", "Temperature", "Annual", "Mean", "C", u"المتوسط الشهري لدرجة الحرارة (متوسط الـ 12 شهراً)", "Mean of 12 climatological monthly means", "Mean of valid monthly T2M values"),
    ("PSL_Month_Mean", "Mean Monthly Sea Level Pressure", u"المتوسط الشهري لضغط مستوى سطح البحر", "SLP", "Sea Level Pressure", "Annual", "Mean", "mbar/hPa", u"المتوسط الشهري لضغط مستوى سطح البحر", "Mean monthly sea-level pressure", "Mean of valid values"),
    ("PS_Month_Mean", "Mean Monthly Surface Pressure", u"المتوسط الشهري للضغط الجوي السطحي", "PS", "Surface Pressure", "Annual", "Mean", "mbar/hPa", u"المتوسط الشهري للضغط السطحي الفعلي", "Mean monthly surface pressure", "Mean of valid values"),
    ("W_Spd_Month_Mean", "Mean Monthly Wind Speed", u"المتوسط الشهري لسرعة الرياح", "WS10M", "Wind", "Annual", "Mean", "m/s", u"المتوسط الشهري لسرعة الرياح", "Mean monthly 10-m wind speed", "Mean of valid values"),
    ("W_Dir_Month_Mean", "Mean Monthly Wind Direction", u"المتوسط الشهري لاتجاه الرياح السائدة", "WD10M", "Wind", "Annual", "Circular Mean", "degree", u"المتوسط الشهري لاتجاه الرياح", "Mean monthly wind direction", "atan2(mean sin, mean cos)"),
    ("RH_Month_Mean", "Mean Monthly Relative Humidity", u"المتوسط الشهري للرطوبة النسبية", "RH2M", "Relative Humidity", "Annual", "Mean", "%", u"المتوسط الشهري للرطوبة النسبية", "Mean monthly 2-m relative humidity", "Mean of valid values"),
    ("Td_Month_Mean", "Mean Monthly Dew Point Temperature", u"المتوسط الشهري لدرجة حرارة نقطة الندى", "T2MDEW", "Dew Point", "Annual", "Mean", "C", u"المتوسط الشهري لنقطة الندى", "Mean monthly dew point temperature", "Mean of valid monthly T2MDEW values"),
    ("Sol_Month_Mean", "Mean Monthly Daily Solar Radiation", u"المتوسط الشهري للإشعاع الشمسي اليومي", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Annual", "Mean", "kWh/m2/day", u"المتوسط الشهري لمعدل الإشعاع اليومي", "Mean monthly daily solar radiation", "Mean of MJ/3.6"),
    ("UV_Month_Mean", "Mean Monthly UV Index", u"المتوسط الشهري لمؤشر الأشعة فوق البنفسجية", "ALLSKY_SFC_UV_INDEX", "UV Index", "Annual", "Mean", "Index", u"المتوسط الشهري لمؤشر الأشعة فوق البنفسجية", "Mean monthly UV index", "Mean of valid values"),
    ("Cld_Month_Mean", "Mean Monthly Cloud Cover", u"المتوسط الشهري للغطاء السحابي", "CLOUD_AMT", "Cloud Cover", "Annual", "Mean", "%", u"المتوسط الشهري لكمية السحب", "Mean monthly cloud amount", "Mean of valid values"),
    ("ET_Month_Mean", "Mean Monthly Evapotranspiration", u"المتوسط الشهري للبخر والنتح", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Annual", "Mean", "mm/month", u"المتوسط الشهري للبخر والنتح المحسوب بطريقة هارجريفز", "Mean monthly potential evapotranspiration", "ET_Annual_Total / 12"),
'''

if '("T_Month_Mean"' not in pyt_content:
    pyt_content = pyt_content.replace(
        'FIELD_DEFS = [\n',
        'FIELD_DEFS = [\n' + field_defs_insert
    )
    print("  Inserted FIELD_DEFS in pyt")

# Add SHP_FIELD_MAP entries
shp_map_insert = '''    "T_Month_Mean": "T_MonMean",
    "PSL_Month_Mean": "PSL_MonMea",
    "PS_Month_Mean": "PS_MonMean",
    "W_Spd_Month_Mean": "WSp_MonMea",
    "W_Dir_Month_Mean": "WDr_MonMea",
    "RH_Month_Mean": "RH_MonMean",
    "Td_Month_Mean": "Td_MonMean",
    "Sol_Month_Mean": "Sol_MonMea",
    "UV_Month_Mean": "UV_MonMean",
    "Cld_Month_Mean": "Cld_MonMea",
    "ET_Month_Mean": "ET_MonMean",
'''

if '"T_Month_Mean": "T_MonMean"' not in pyt_content:
    pyt_content = pyt_content.replace(
        'SHP_FIELD_MAP = {\n',
        'SHP_FIELD_MAP = {\n' + shp_map_insert
    )
    print("  Inserted SHP_FIELD_MAP in pyt")

# Update compute functions in pyt:
# 1. compute_temperature_fields
if '"T_Month_Mean": s_mean["Annual"]' not in pyt_content:
    pyt_content = pyt_content.replace(
        '"T_Annual_Mean": s_mean["Annual"],',
        '"T_Annual_Mean": s_mean["Annual"],\n        "T_Month_Mean": s_mean["Annual"],'
    )
    print("  Added T_Month_Mean to compute_temperature_fields")

# 2. compute_wind_fields
if '"W_Spd_Month_Mean": s_spd["Annual"]' not in pyt_content:
    pyt_content = pyt_content.replace(
        '"W_Spd_Annual_Mean": s_spd["Annual"],',
        '"W_Spd_Annual_Mean": s_spd["Annual"],\n        "W_Spd_Month_Mean": s_spd["Annual"],'
    )
    pyt_content = pyt_content.replace(
        'out["W_Dir_Annual_Mean"] = circular_mean_deg(allv)',
        'out["W_Dir_Annual_Mean"] = circular_mean_deg(allv)\n    out["W_Dir_Month_Mean"] = circular_mean_deg(allv)'
    )
    print("  Added W_Spd_Month_Mean and W_Dir_Month_Mean to compute_wind_fields")

# 3. compute_solar_fields
if '"Sol_Month_Mean": s["Annual"]' not in pyt_content:
    pyt_content = pyt_content.replace(
        '"Sol_Annual_Mean": s["Annual"],',
        '"Sol_Annual_Mean": s["Annual"],\n        "Sol_Month_Mean": s["Annual"],'
    )
    print("  Added Sol_Month_Mean to compute_solar_fields")

# 4. compute_drought_fields
if '"ET_Month_Mean": round(pet_mean, 1)' not in pyt_content:
    pyt_content = pyt_content.replace(
        '"ET_Annual_Mean": round(pet_mean, 1),',
        '"ET_Annual_Mean": round(pet_mean, 1),\n        "ET_Month_Mean": round(pet_mean, 1),'
    )
    print("  Added ET_Month_Mean to compute_drought_fields")

# 5. compute_point_fields modules
if '"PSL_Month_Mean": s["Annual"]' not in pyt_content:
    pyt_content = pyt_content.replace(
        '"PSL_Annual_Mean": s["Annual"],',
        '"PSL_Annual_Mean": s["Annual"], "PSL_Month_Mean": s["Annual"],'
    )
    pyt_content = pyt_content.replace(
        '"PS_Annual_Mean": s["Annual"],',
        '"PS_Annual_Mean": s["Annual"], "PS_Month_Mean": s["Annual"],'
    )
    pyt_content = pyt_content.replace(
        '"RH_Annual_Mean": s["Annual"],',
        '"RH_Annual_Mean": s["Annual"], "RH_Month_Mean": s["Annual"],'
    )
    pyt_content = pyt_content.replace(
        '"Td_Annual_Mean": s_td["Annual"],',
        '"Td_Annual_Mean": s_td["Annual"], "Td_Month_Mean": s_td["Annual"],'
    )
    pyt_content = pyt_content.replace(
        '"UV_Annual_Mean": s["Annual"],',
        '"UV_Annual_Mean": s["Annual"], "UV_Month_Mean": s["Annual"],'
    )
    pyt_content = pyt_content.replace(
        '"Cld_Annual_Mean": s["Annual"],',
        '"Cld_Annual_Mean": s["Annual"], "Cld_Month_Mean": s["Annual"],'
    )
    print("  Added Month_Mean to compute_point_fields modules")

# 6. Set descriptive Arabic aliases on AddField in pyt
if 'FIELD_ALIAS_AR =' not in pyt_content:
    pyt_content = pyt_content.replace(
        'FIELD_BY_NAME = dict((r[0], r) for r in FIELD_DEFS)\n',
        'FIELD_BY_NAME = dict((r[0], r) for r in FIELD_DEFS)\nFIELD_ALIAS_AR = dict((r[0], r[2]) for r in FIELD_DEFS)\n'
    )

# Update AddField calls to use FIELD_ALIAS_AR
old_code_1 = '''                for name, typ, _alias in ADMIN_FIELDS:
                    if name not in existing:
                        if typ == "TEXT":
                            arcpy.management.AddField(fc, name, typ, field_length=255, field_alias=name)
                        else:
                            arcpy.management.AddField(fc, name, typ, field_alias=name)
                wanted = wanted_fields_by_module.get(m, MODULE_FIELDS.get(m, []))
                for wf in wanted:
                    if wf not in existing:
                        field_type = "LONG" if wf == "Dry_Months_Count" else "DOUBLE"
                        arcpy.management.AddField(fc, wf, field_type, field_alias=wf)'''

new_code_1 = '''                for name, typ, _alias in ADMIN_FIELDS:
                    if name not in existing:
                        ar_alias = ADMIN_AR.get(name, name)
                        if typ == "TEXT":
                            arcpy.management.AddField(fc, name, typ, field_length=255, field_alias=ar_alias)
                        else:
                            arcpy.management.AddField(fc, name, typ, field_alias=ar_alias)
                wanted = wanted_fields_by_module.get(m, MODULE_FIELDS.get(m, []))
                for wf in wanted:
                    if wf not in existing:
                        field_type = "LONG" if wf == "Dry_Months_Count" else "DOUBLE"
                        ar_alias = FIELD_ALIAS_AR.get(wf, wf)
                        arcpy.management.AddField(fc, wf, field_type, field_alias=ar_alias)'''

if old_code_1 in pyt_content:
    pyt_content = pyt_content.replace(old_code_1, new_code_1)
    print("  Updated AddField in _build_element_layers with Arabic aliases")

old_code_2 = '''            for name, typ, _alias in ADMIN_FIELDS:
                if name not in existing:
                    if typ == "TEXT":
                        arcpy.management.AddField(fc, name, typ, field_length=255, field_alias=name)
                    else:
                        arcpy.management.AddField(fc, name, typ, field_alias=name)
            if wanted_fields is not None:
                wanted = wanted_fields
            else:
                wanted = MODULE_FIELDS.get(m, [])
            for f in wanted:
                if f not in existing:
                    field_type = "LONG" if f == "Dry_Months_Count" else "DOUBLE"
                    arcpy.management.AddField(fc, f, field_type, field_alias=f)'''

new_code_2 = '''            for name, typ, _alias in ADMIN_FIELDS:
                if name not in existing:
                    ar_alias = ADMIN_AR.get(name, name)
                    if typ == "TEXT":
                        arcpy.management.AddField(fc, name, typ, field_length=255, field_alias=ar_alias)
                    else:
                        arcpy.management.AddField(fc, name, typ, field_alias=ar_alias)
            if wanted_fields is not None:
                wanted = wanted_fields
            else:
                wanted = MODULE_FIELDS.get(m, [])
            for f in wanted:
                if f not in existing:
                    field_type = "LONG" if f == "Dry_Months_Count" else "DOUBLE"
                    ar_alias = FIELD_ALIAS_AR.get(f, f)
                    arcpy.management.AddField(fc, f, field_type, field_alias=ar_alias)'''

if old_code_2 in pyt_content:
    pyt_content = pyt_content.replace(old_code_2, new_code_2)
    print("  Updated AddField in _build_single_element_layer with Arabic aliases")

with open(PYT_FILE, "w", encoding="utf-8") as f:
    f.write(pyt_content)
print("Finished patching Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt\n")


# --- 2. PATCH Toolboxes/raster_atlas_generator.py ---
print("Patching Toolboxes/raster_atlas_generator.py...")
with open(RAG_FILE, "r", encoding="utf-8") as f:
    rag_content = f.read()

# Add SHP_FIELD_MAP entries
if '"T_Month_Mean": "T_MonMean"' not in rag_content:
    rag_content = rag_content.replace(
        'SHP_FIELD_MAP = {\n',
        'SHP_FIELD_MAP = {\n' + shp_map_insert
    )
    print("  Inserted SHP_FIELD_MAP in rag")

# Update MODULE_INDICATOR_FIELDS
if '("T_Month_Mean"' not in rag_content:
    rag_content = rag_content.replace(
        '("T_Annual_Mean", "Annual Mean Air Temperature"),\n',
        '("T_Annual_Mean", "Annual Mean Air Temperature"),\n        ("T_Month_Mean", "Mean Monthly Air Temperature"),\n'
    )
    rag_content = rag_content.replace(
        '("PSL_Annual_Mean", "Annual Mean Sea Level Pressure"),\n',
        '("PSL_Annual_Mean", "Annual Mean Sea Level Pressure"),\n        ("PSL_Month_Mean", "Mean Monthly Sea Level Pressure"),\n'
    )
    rag_content = rag_content.replace(
        '("PS_Annual_Mean", "Annual Mean Surface Pressure"),\n',
        '("PS_Annual_Mean", "Annual Mean Surface Pressure"),\n        ("PS_Month_Mean", "Mean Monthly Surface Pressure"),\n'
    )
    rag_content = rag_content.replace(
        '("W_Spd_Annual_Mean", "Annual Mean Wind Speed"),\n',
        '("W_Spd_Annual_Mean", "Annual Mean Wind Speed"),\n        ("W_Spd_Month_Mean", "Mean Monthly Wind Speed"),\n'
    )
    rag_content = rag_content.replace(
        '("W_Dir_Annual_Mean", "Annual Prevailing Wind Direction"),\n',
        '("W_Dir_Annual_Mean", "Annual Prevailing Wind Direction"),\n        ("W_Dir_Month_Mean", "Mean Monthly Wind Direction"),\n'
    )
    rag_content = rag_content.replace(
        '("RH_Annual_Mean", "Annual Mean Relative Humidity"),\n',
        '("RH_Annual_Mean", "Annual Mean Relative Humidity"),\n        ("RH_Month_Mean", "Mean Monthly Relative Humidity"),\n'
    )
    rag_content = rag_content.replace(
        '("Td_Annual_Mean", "Annual Mean Dew Point Temperature"),\n',
        '("Td_Annual_Mean", "Annual Mean Dew Point Temperature"),\n        ("Td_Month_Mean", "Mean Monthly Dew Point Temperature"),\n'
    )
    rag_content = rag_content.replace(
        '("Sol_Annual_Mean", "Annual Mean Daily Solar Radiation"),\n',
        '("Sol_Annual_Mean", "Annual Mean Daily Solar Radiation"),\n        ("Sol_Month_Mean", "Mean Monthly Daily Solar Radiation"),\n'
    )
    rag_content = rag_content.replace(
        '("UV_Annual_Mean", "Annual Mean UV Index"),\n',
        '("UV_Annual_Mean", "Annual Mean UV Index"),\n        ("UV_Month_Mean", "Mean Monthly UV Index"),\n'
    )
    rag_content = rag_content.replace(
        '("Cld_Annual_Mean", "Annual Mean Cloud Cover"),\n',
        '("Cld_Annual_Mean", "Annual Mean Cloud Cover"),\n        ("Cld_Month_Mean", "Mean Monthly Cloud Cover"),\n'
    )
    rag_content = rag_content.replace(
        '("ET_Annual_Mean", "Annual Mean Monthly Evapotranspiration"),\n',
        '("ET_Annual_Mean", "Annual Mean Monthly Evapotranspiration"),\n        ("ET_Month_Mean", "Mean Monthly Evapotranspiration"),\n'
    )
    print("  Added Month_Mean to MODULE_INDICATOR_FIELDS in rag")

# Update DICTIONARY_ROWS_AR in rag
dict_ar_insert = '''            [u"درجة الحرارة", u"T_Month_Mean", u"المتوسط الشهري لدرجة الحرارة", u"مئوية", u"بيانات شبكية"],
            [u"ضغط مستوى سطح البحر", u"PSL_Month_Mean", u"المتوسط الشهري لضغط مستوى سطح البحر", u"هيكتوباسكال", u"بيانات شبكية"],
            [u"الضغط الجوي السطحي", u"PS_Month_Mean", u"المتوسط الشهري للضغط السطحي", u"هيكتوباسكال", u"بيانات شبكية"],
            [u"الرياح", u"W_Spd_Month_Mean", u"المتوسط الشهري لسرعة الرياح", u"م/ث", u"بيانات شبكية"],
            [u"الرياح", u"W_Dir_Month_Mean", u"المتوسط الشهري لاتجاه الرياح", u"درجة", u"بيانات شبكية"],
            [u"الرطوبة النسبية", u"RH_Month_Mean", u"المتوسط الشهري للرطوبة النسبية", u"%", u"بيانات شبكية"],
            [u"نقطة الندى", u"Td_Month_Mean", u"المتوسط الشهري لدرجة حرارة نقطة الندى", u"مئوية", u"بيانات شبكية"],
            [u"الإشعاع الشمسي", u"Sol_Month_Mean", u"المتوسط الشهري للإشعاع الشمسي", u"ميجاجول/م2/يوم", u"بيانات شبكية"],
            [u"مؤشر الأشعة فوق البنفسجية", u"UV_Month_Mean", u"المتوسط الشهري لمؤشر UV", u"مؤشر", u"بيانات شبكية"],
            [u"الغطاء السحابي", u"Cld_Month_Mean", u"المتوسط الشهري لكمية السحب", u"%", u"بيانات شبكية"],
            [u"البخر والنتح", u"ET_Month_Mean", u"المتوسط الشهري للبخر والنتح", u"ملم/شهر", u"مشتق من بيانات شبكية"],
'''

if 'u"T_Month_Mean"' not in rag_content:
    rag_content = rag_content.replace(
        'rows_ar = [\n',
        'rows_ar = [\n' + dict_ar_insert
    )
    print("  Added Month_Mean to DICTIONARY_ROWS_AR in rag")

with open(RAG_FILE, "w", encoding="utf-8") as f:
    f.write(rag_content)
print("Finished patching Toolboxes/raster_atlas_generator.py\n")
print("ALL CODEBASE INTEGRATION COMPLETE!")
