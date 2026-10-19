# -*- coding: utf-8 -*-
"""
patch_codebase_seasonal_and_monthly.py
--------------------------------------
Applies all code modifications to:
1. generate_excel_dictionary.py
2. generate_master_atlas_excel.py
3. Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt
4. Toolboxes/raster_atlas_generator.py
"""
import io
import os
import re

BASE_DIR = r"D:\My Software\NASA POWER Climate Atlas Generator"

# -------------------------------------------------------------
# 1. Update generate_excel_dictionary.py
# -------------------------------------------------------------
dict_path = os.path.join(BASE_DIR, "generate_excel_dictionary.py")
with io.open(dict_path, "r", encoding="utf-8") as f:
    dict_content = f.read()

# Add 9 Seasonal Range indicators if not present
if '"full_name": "T_Seasonal_Range"' not in dict_content:
    print("Patching generate_excel_dictionary.py...")
    # Add T_Seasonal_Range right after T_Annual_Range
    t_target = '        "full_name": "T_Annual_Range",\n        "module_code": "01_Temperature",\n        "module_name": "01_Temperature (درجات الحرارة)",\n        "desc_ar": u"المدى الحراري السنوي (الفارق بين أدفأ وأبرد شهور السنة).",\n        "unit": u"°C",\n        "map_title": u"خريطة المدى الحراري السنوي لدرجة الحرارة (°C)"\n    },'
    t_repl = t_target + '\n    {\n        "short_name": "T_SeaRng",\n        "full_name": "T_Seasonal_Range",\n        "module_code": "01_Temperature",\n        "module_name": "01_Temperature (درجات الحرارة)",\n        "desc_ar": u"المدى الفصلي لدرجة الحرارة (الفارق بين أدفأ فصول السنة وأبردها).",\n        "unit": u"°C",\n        "map_title": u"خريطة المدى الفصلي لدرجة الحرارة (°C)"\n    },'
    dict_content = dict_content.replace(t_target, t_repl)

    # PSL_Seasonal_Range after PSL_Annual_Range
    psl_target = '        "full_name": "PSL_Annual_Range",\n        "module_code": "03_Sea_Level_Pressure",\n        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",\n        "desc_ar": u"المدى السنوي لضغط مستوى البحر (الفارق بين أعلى وأدنى شهور السنة).",\n        "unit": u"hPa",\n        "map_title": u"خريطة المدى السنوي لضغط مستوى البحر (hPa)"\n    },'
    psl_repl = psl_target + '\n    {\n        "short_name": "PSL_SeaRng",\n        "full_name": "PSL_Seasonal_Range",\n        "module_code": "03_Sea_Level_Pressure",\n        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",\n        "desc_ar": u"المدى الفصلي لضغط مستوى البحر (الفارق بين أعلى وأدنى فصول السنة).",\n        "unit": u"hPa",\n        "map_title": u"خريطة المدى الفصلي لضغط مستوى البحر (hPa)"\n    },'
    dict_content = dict_content.replace(psl_target, psl_repl)

    # PS_Seasonal_Range after PS_Annual_Range
    ps_target = '        "full_name": "PS_Annual_Range",\n        "module_code": "04_Surface_Pressure",\n        "module_name": "04_Surface_Pressure (الضغط السطحي)",\n        "desc_ar": u"المدى السنوي للضغط السطحي (الفارق بين أعلى وأدنى شهور السنة).",\n        "unit": u"hPa",\n        "map_title": u"خريطة المدى السنوي للضغط السطحي (hPa)"\n    },'
    ps_repl = ps_target + '\n    {\n        "short_name": "PS_SeaRng",\n        "full_name": "PS_Seasonal_Range",\n        "module_code": "04_Surface_Pressure",\n        "module_name": "04_Surface_Pressure (الضغط السطحي)",\n        "desc_ar": u"المدى الفصلي للضغط السطحي (الفارق بين فصول السنة).",\n        "unit": u"hPa",\n        "map_title": u"خريطة المدى الفصلي للضغط السطحي (hPa)"\n    },'
    dict_content = dict_content.replace(ps_target, ps_repl)

    # W_Spd_Seasonal_Range after W_Spd_Annual_Range
    w_target = '        "full_name": "W_Spd_Annual_Range",\n        "module_code": "05_Wind",\n        "module_name": "05_Wind (الرياح)",\n        "desc_ar": u"المدى السنوي لسرعة الرياح (الفارق بين أشد وأهدأ شهور السنة).",\n        "unit": u"م/ث (m/s)",\n        "map_title": u"خريطة المدى السنوي لسرعة الرياح (م/ث)"\n    },'
    w_repl = w_target + '\n    {\n        "short_name": "WSp_SeaRng",\n        "full_name": "W_Spd_Seasonal_Range",\n        "module_code": "05_Wind",\n        "module_name": "05_Wind (الرياح)",\n        "desc_ar": u"المدى الفصلي لسرعة الرياح (الفارق بين أشد فصول السنة ريحاً وأهدأها).",\n        "unit": u"م/ث (m/s)",\n        "map_title": u"خريطة المدى الفصلي لسرعة الرياح (م/ث)"\n    },'
    dict_content = dict_content.replace(w_target, w_repl)

    # RH_Seasonal_Range after RH_Annual_Range
    rh_target = '        "full_name": "RH_Annual_Range",\n        "module_code": "06_Relative_Humidity",\n        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",\n        "desc_ar": u"المدى السنوي للرطوبة النسبية (الفارق بين أكثر شهور السنة رطوبة وأجفها).",\n        "unit": u"%",\n        "map_title": u"خريطة المدى السنوي للرطوبة النسبية (%)"\n    },'
    rh_repl = rh_target + '\n    {\n        "short_name": "RH_SeaRng",\n        "full_name": "RH_Seasonal_Range",\n        "module_code": "06_Relative_Humidity",\n        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",\n        "desc_ar": u"المدى الفصلي للرطوبة النسبية (الفارق بين أكثر فصول السنة رطوبة وأجفها).",\n        "unit": u"%",\n        "map_title": u"خريطة المدى الفصلي للرطوبة النسبية (%)"\n    },'
    dict_content = dict_content.replace(rh_target, rh_repl)

    # Td_Seasonal_Range after Td_Annual_Range
    td_target = '        "full_name": "Td_Annual_Range",\n        "module_code": "07_Dew_Point",\n        "module_name": "07_Dew_Point (نقطة الندى)",\n        "desc_ar": u"المدى السنوي لنقطة الندى (الفارق بين أعلى وأدنى شهور السنة).",\n        "unit": u"°C",\n        "map_title": u"خريطة المدى السنوي لنقطة الندى (°C)"\n    },'
    td_repl = td_target + '\n    {\n        "short_name": "Td_SeaRng",\n        "full_name": "Td_Seasonal_Range",\n        "module_code": "07_Dew_Point",\n        "module_name": "07_Dew_Point (نقطة الندى)",\n        "desc_ar": u"المدى الفصلي لنقطة الندى (الفارق بين أعلى وأدنى فصول السنة).",\n        "unit": u"°C",\n        "map_title": u"خريطة المدى الفصلي لنقطة الندى (°C)"\n    },'
    dict_content = dict_content.replace(td_target, td_repl)

    # Sol_Seasonal_Range after Sol_Annual_Range
    sol_target = '        "full_name": "Sol_Annual_Range",\n        "module_code": "08_Solar_Radiation",\n        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",\n        "desc_ar": u"المدى السنوي للإشعاع الشمسي اليومي (الفارق بين أعلى وأدنى شهور السنة).",\n        "unit": u"kWh/m²/day",\n        "map_title": u"خريطة المدى السنوي للإشعاع الشمسي اليومي (kWh/m²/day)"\n    },'
    sol_repl = sol_target + '\n    {\n        "short_name": "Sol_SeaRng",\n        "full_name": "Sol_Seasonal_Range",\n        "module_code": "08_Solar_Radiation",\n        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",\n        "desc_ar": u"المدى الفصلي للإشعاع الشمسي اليومي (الفارق بين فصول السنة).",\n        "unit": u"kWh/m²/day",\n        "map_title": u"خريطة المدى الفصلي للإشعاع الشمسي اليومي (kWh/m²/day)"\n    },'
    dict_content = dict_content.replace(sol_target, sol_repl)

    # UV_Seasonal_Range after UV_Annual_Range
    uv_target = '        "full_name": "UV_Annual_Range",\n        "module_code": "09_UV_Index",\n        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",\n        "desc_ar": u"المدى السنوي لمؤشر الأشعة فوق البنفسجية (الفارق بين أعلى وأدنى شهور السنة).",\n        "unit": u"مؤشر (Index)",\n        "map_title": u"خريطة المدى السنوي لمؤشر الأشعة فوق البنفسجية"\n    },'
    uv_repl = uv_target + '\n    {\n        "short_name": "UV_SeaRng",\n        "full_name": "UV_Seasonal_Range",\n        "module_code": "09_UV_Index",\n        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",\n        "desc_ar": u"المدى الفصلي لمؤشر الأشعة فوق البنفسجية (الفارق بين فصول السنة).",\n        "unit": u"مؤشر (Index)",\n        "map_title": u"خريطة المدى الفصلي لمؤشر الأشعة فوق البنفسجية"\n    },'
    dict_content = dict_content.replace(uv_target, uv_repl)

    # Cld_Seasonal_Range after Cld_Annual_Range
    cld_target = '        "full_name": "Cld_Annual_Range",\n        "module_code": "10_Cloud_Cover",\n        "module_name": "10_Cloud_Cover (الغطاء السحابي)",\n        "desc_ar": u"المدى السنوي للغطاء السحابي (الفارق بين أعلى شهور السنة غيوماً وأصفاها).",\n        "unit": u"%",\n        "map_title": u"خريطة المدى السنوي للغطاء السحابي (%)"\n    },'
    cld_repl = cld_target + '\n    {\n        "short_name": "Cld_SeaRng",\n        "full_name": "Cld_Seasonal_Range",\n        "module_code": "10_Cloud_Cover",\n        "module_name": "10_Cloud_Cover (الغطاء السحابي)",\n        "desc_ar": u"المدى الفصلي للغطاء السحابي (الفارق بين أعلى فصول السنة غيوماً وأصفاها).",\n        "unit": u"%",\n        "map_title": u"خريطة المدى الفصلي للغطاء السحابي (%)"\n    },'
    dict_content = dict_content.replace(cld_target, cld_repl)

    with io.open(dict_path, "w", encoding="utf-8") as f:
        f.write(dict_content)
    print("generate_excel_dictionary.py updated successfully.")

# -------------------------------------------------------------
# 2. Update Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt
# -------------------------------------------------------------
pyt_path = os.path.join(BASE_DIR, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")
with io.open(pyt_path, "r", encoding="utf-8") as f:
    pyt_content = f.read()

print("Patching Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt...")

# 2A. Update point computation functions to calculate *_Seasonal_Range
# Temperature
old_t = '"T_Annual_Range": annual_temp_range(m_tmean),'
new_t = '''"T_Annual_Range": annual_temp_range(m_tmean),
        "T_Seasonal_Range": (max([s_mean["Winter"], s_mean["Spring"], s_mean["Summer"], s_mean["Autumn"]]) - min([s_mean["Winter"], s_mean["Spring"], s_mean["Summer"], s_mean["Autumn"]])) if all(s_mean.get(k) is not None for k in ["Winter", "Spring", "Summer", "Autumn"]) else None,'''
if '"T_Seasonal_Range":' not in pyt_content:
    pyt_content = pyt_content.replace(old_t, new_t, 1)

# Wind
old_w = '"W_Spd_Annual_Range": wind_range,'
new_w = '''"W_Spd_Annual_Range": wind_range,
        "W_Spd_Seasonal_Range": (max([s_spd["Winter"], s_spd["Spring"], s_spd["Summer"], s_spd["Autumn"]]) - min([s_spd["Winter"], s_spd["Spring"], s_spd["Summer"], s_spd["Autumn"]])) if all(s_spd.get(k) is not None for k in ["Winter", "Spring", "Summer", "Autumn"]) else None,'''
if '"W_Spd_Seasonal_Range":' not in pyt_content:
    pyt_content = pyt_content.replace(old_w, new_w, 1)

# Solar
old_sol = '"Sol_Annual_Range": sol_range,'
new_sol = '''"Sol_Annual_Range": sol_range,
        "Sol_Seasonal_Range": (max([s_sol["Winter"], s_sol["Spring"], s_sol["Summer"], s_sol["Autumn"]]) - min([s_sol["Winter"], s_sol["Spring"], s_sol["Summer"], s_sol["Autumn"]])) if all(s_sol.get(k) is not None for k in ["Winter", "Spring", "Summer", "Autumn"]) else None,'''
if '"Sol_Seasonal_Range":' not in pyt_content:
    pyt_content = pyt_content.replace(old_sol, new_sol, 1)

# In compute_point_fields (PSL, PS, RH, Td, UV, Cld):
# When calculating m_means and seasonal ranges
old_psl_block = 'f["PSL_Annual_Range"] = monthly_range(m_psl)'
new_psl_block = '''f["PSL_Annual_Range"] = monthly_range(m_psl)
            s_psl_vals = [s_psl.get("Winter"), s_psl.get("Spring"), s_psl.get("Summer"), s_psl.get("Autumn")]
            f["PSL_Seasonal_Range"] = (max(s_psl_vals) - min(s_psl_vals)) if all(v is not None for v in s_psl_vals) else None'''
if 'f["PSL_Seasonal_Range"]' not in pyt_content:
    pyt_content = pyt_content.replace(old_psl_block, new_psl_block, 1)

old_ps_block = 'f["PS_Annual_Range"] = monthly_range(m_ps)'
new_ps_block = '''f["PS_Annual_Range"] = monthly_range(m_ps)
            s_ps_vals = [s_ps.get("Winter"), s_ps.get("Spring"), s_ps.get("Summer"), s_ps.get("Autumn")]
            f["PS_Seasonal_Range"] = (max(s_ps_vals) - min(s_ps_vals)) if all(v is not None for v in s_ps_vals) else None'''
if 'f["PS_Seasonal_Range"]' not in pyt_content:
    pyt_content = pyt_content.replace(old_ps_block, new_ps_block, 1)

old_rh_block = 'f["RH_Annual_Range"] = monthly_range(m_rh)'
new_rh_block = '''f["RH_Annual_Range"] = monthly_range(m_rh)
            s_rh_vals = [s_rh.get("Winter"), s_rh.get("Spring"), s_rh.get("Summer"), s_rh.get("Autumn")]
            f["RH_Seasonal_Range"] = (max(s_rh_vals) - min(s_rh_vals)) if all(v is not None for v in s_rh_vals) else None'''
if 'f["RH_Seasonal_Range"]' not in pyt_content:
    pyt_content = pyt_content.replace(old_rh_block, new_rh_block, 1)

old_td_block = 'f["Td_Annual_Range"] = monthly_range(m_td)'
new_td_block = '''f["Td_Annual_Range"] = monthly_range(m_td)
            s_td_vals = [s_td.get("Winter"), s_td.get("Spring"), s_td.get("Summer"), s_td.get("Autumn")]
            f["Td_Seasonal_Range"] = (max(s_td_vals) - min(s_td_vals)) if all(v is not None for v in s_td_vals) else None'''
if 'f["Td_Seasonal_Range"]' not in pyt_content:
    pyt_content = pyt_content.replace(old_td_block, new_td_block, 1)

old_uv_block = 'f["UV_Annual_Range"] = monthly_range(m_uv)'
new_uv_block = '''f["UV_Annual_Range"] = monthly_range(m_uv)
            s_uv_vals = [s_uv.get("Winter"), s_uv.get("Spring"), s_uv.get("Summer"), s_uv.get("Autumn")]
            f["UV_Seasonal_Range"] = (max(s_uv_vals) - min(s_uv_vals)) if all(v is not None for v in s_uv_vals) else None'''
if 'f["UV_Seasonal_Range"]' not in pyt_content:
    pyt_content = pyt_content.replace(old_uv_block, new_uv_block, 1)

old_cld_block = 'f["Cld_Annual_Range"] = monthly_range(m_cld)'
new_cld_block = '''f["Cld_Annual_Range"] = monthly_range(m_cld)
            s_cld_vals = [s_cld.get("Winter"), s_cld.get("Spring"), s_cld.get("Summer"), s_cld.get("Autumn")]
            f["Cld_Seasonal_Range"] = (max(s_cld_vals) - min(s_cld_vals)) if all(v is not None for v in s_cld_vals) else None'''
if 'f["Cld_Seasonal_Range"]' not in pyt_content:
    pyt_content = pyt_content.replace(old_cld_block, new_cld_block, 1)

# 2B. Add FIELD_DEFS for 9 Seasonal Range indicators
seasonal_field_defs = '''    ("T_Seasonal_Range", "Seasonal Temperature Range", u"المدى الفصلي لدرجة الحرارة", "T2M", "Temperature", "Annual", "Range", "C", u"المدى الفصلي لدرجة الحرارة", "Warmest seasonal mean minus coldest seasonal mean", "max(seasons) - min(seasons)"),
    ("PSL_Seasonal_Range", "Seasonal Sea Level Pressure Range", u"المدى الفصلي لضغط مستوى البحر", "PSL", "Sea Level Pressure", "Annual", "Range", "hPa", u"المدى الفصلي لضغط مستوى سطح البحر", "Highest seasonal PSL minus lowest seasonal PSL", "max(seasons) - min(seasons)"),
    ("PS_Seasonal_Range", "Seasonal Surface Pressure Range", u"المدى الفصلي للضغط السطحي", "PS", "Surface Pressure", "Annual", "Range", "hPa", u"المدى الفصلي للضغط السطحي", "Highest seasonal PS minus lowest seasonal PS", "max(seasons) - min(seasons)"),
    ("W_Spd_Seasonal_Range", "Seasonal Wind Speed Range", u"المدى الفصلي لسرعة الرياح", "WS10M", "Wind", "Annual", "Range", "m/s", u"المدى الفصلي لسرعة الرياح", "Windiest seasonal mean minus calmest seasonal mean", "max(seasons) - min(seasons)"),
    ("RH_Seasonal_Range", "Seasonal Relative Humidity Range", u"المدى الفصلي للرطوبة النسبية", "RH2M", "Relative Humidity", "Annual", "Range", "%", u"المدى الفصلي للرطوبة النسبية", "Humidest seasonal mean minus driest seasonal mean", "max(seasons) - min(seasons)"),
    ("Td_Seasonal_Range", "Seasonal Dew Point Range", u"المدى الفصلي لنقطة الندى", "T2MDEW", "Dew Point", "Annual", "Range", "C", u"المدى الفصلي لنقطة الندى", "Highest seasonal Td minus lowest seasonal Td", "max(seasons) - min(seasons)"),
    ("Sol_Seasonal_Range", "Seasonal Solar Radiation Range", u"المدى الفصلي للإشعاع الشمسي", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Annual", "Range", "kWh/m2/day", u"المدى الفصلي للإشعاع الشمسي", "Highest seasonal daily mean minus lowest seasonal daily mean", "max(seasons) - min(seasons)"),
    ("UV_Seasonal_Range", "Seasonal UV Index Range", u"المدى الفصلي للأشعة فوق البنفسجية", "ALLSKY_SFC_UV_INDEX", "UV Index", "Annual", "Range", "Index", u"المدى الفصلي لمؤشر الأشعة فوق البنفسجية", "Highest seasonal UV index minus lowest seasonal UV index", "max(seasons) - min(seasons)"),
    ("Cld_Seasonal_Range", "Seasonal Cloud Cover Range", u"المدى الفصلي للغطاء السحابي", "CLOUD_AMT", "Cloud Cover", "Annual", "Range", "%", u"المدى الفصلي للغطاء السحابي", "Highest seasonal cloud cover minus lowest seasonal cloud cover", "max(seasons) - min(seasons)"),
'''
if '"T_Seasonal_Range", "Seasonal Temperature Range"' not in pyt_content:
    pyt_content = pyt_content.replace('    ("T_Annual_Range",', seasonal_field_defs + '    ("T_Annual_Range",', 1)

# 2C. Update SHP_FIELD_MAP in pyt
shp_ranges = '''    "T_Seasonal_Range": "T_SeaRng",
    "PSL_Seasonal_Range": "PSL_SeaRng",
    "PS_Seasonal_Range": "PS_SeaRng",
    "W_Spd_Seasonal_Range": "WSp_SeaRng",
    "RH_Seasonal_Range": "RH_SeaRng",
    "Td_Seasonal_Range": "Td_SeaRng",
    "Sol_Seasonal_Range": "Sol_SeaRng",
    "UV_Seasonal_Range": "UV_SeaRng",
    "Cld_Seasonal_Range": "Cld_SeaRng",
'''
if '"T_Seasonal_Range": "T_SeaRng"' not in pyt_content:
    pyt_content = pyt_content.replace('    "T_Month_Mean": "T_MonMean",\n', '    "T_Month_Mean": "T_MonMean",\n' + shp_ranges, 1)

# 2D. Add parameter Generate_Monthly_Rasters to getParameterInfo()
param_target = '''        p_temporal_scope.category = "Variable & Field Selection"
        p_temporal_scope.description = (
            "TEMPORAL MATRIX SCOPE. Select which temporal scopes and seasons to compute and map "
            "(Annual, Winter, Spring, Summer, Autumn). Uncheck any seasons not needed (e.g. keep only "
            "Annual for fast regional atlas, or Summer only for heat waves). The tool computes only the "
            "Cartesian product of selected Climate Modules and selected Temporal Scope."
        )'''

param_addition = '''

        p_monthly_rasters = arcpy.Parameter(
            displayName="Generate Monthly Climatology Rasters (Jan–Dec) / توليد راستر مناخي مستقل لكل شهر من أشهر السنة",
            name="Generate_Monthly_Rasters",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_monthly_rasters.value = False
        p_monthly_rasters.category = "Variable & Field Selection"
        p_monthly_rasters.description = (
            "GENERATE 12 INDIVIDUAL MONTHLY RASTERS (Jan-Dec). When checked, interpolates independent "
            "climatological surface rasters for all 12 calendar months into a dedicated 'Month' subfolder "
            "for each selected element."
        )'''

if 'p_monthly_rasters = arcpy.Parameter(' not in pyt_content:
    pyt_content = pyt_content.replace(param_target, param_target + param_addition, 1)
    pyt_content = pyt_content.replace('p8, p_temporal_scope, p_filter_scope,', 'p8, p_temporal_scope, p_monthly_rasters, p_filter_scope,', 1)

# 2E. Update execute to read Generate_Monthly_Rasters
exec_target = '''            p_iso = pdict.get("Create_Isobars")
            create_isobars = bool(p_iso.value) if (p_iso and p_iso.value is not None) else False'''

exec_addition = '''            p_gmr = pdict.get("Generate_Monthly_Rasters")
            generate_monthly_rasters = bool(p_gmr.value) if (p_gmr and p_gmr.value is not None) else False'''

if 'generate_monthly_rasters = bool(p_gmr.value)' not in pyt_content:
    pyt_content = pyt_content.replace(exec_target, exec_target + "\n" + exec_addition, 1)

# 2F. Update _build_wind_vectors in pyt
wv_target = '''        periods = [
            ("Annual", "W_Spd_Annual_Mean", "W_Dir_Annual_Mean"),'''
wv_repl = '''        periods = [
            ("Annual", "W_Spd_Annual_Mean", "W_Dir_Annual_Mean"),
            ("Month", "W_Spd_Month_Mean", "W_Dir_Month_Mean"),'''
if '("Month", "W_Spd_Month_Mean", "W_Dir_Month_Mean")' not in pyt_content:
    pyt_content = pyt_content.replace(wv_target, wv_repl, 1)

# 2G. Update _build_isobars in pyt
iso_target = '''        mapping = {"PSL_Winter_Mean": "Isobars_PSL_Winter_Mean",'''
iso_repl = '''        mapping = {"PSL_Annual_Mean": "Isobars_PSL_Annual_Mean",
                   "PSL_Month_Mean": "Isobars_PSL_Month_Mean",
                   "PS_Annual_Mean": "Isobars_PS_Annual_Mean",
                   "PS_Month_Mean": "Isobars_PS_Month_Mean",
                   "PSL_Winter_Mean": "Isobars_PSL_Winter_Mean",'''
if '"PSL_Month_Mean": "Isobars_PSL_Month_Mean"' not in pyt_content:
    pyt_content = pyt_content.replace(iso_target, iso_repl, 1)

with io.open(pyt_path, "w", encoding="utf-8") as f:
    f.write(pyt_content)
print("Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt updated successfully.")

# -------------------------------------------------------------
# 3. Update Toolboxes/raster_atlas_generator.py
# -------------------------------------------------------------
rag_path = os.path.join(BASE_DIR, "Toolboxes/raster_atlas_generator.py")
with io.open(rag_path, "r", encoding="utf-8") as f:
    rag_content = f.read()

print("Patching Toolboxes/raster_atlas_generator.py...")

# Add Seasonal Range fields to MODULE_INDICATOR_FIELDS
rag_mod_updates = [
    ('("T_Annual_Range", "Annual Temperature Range"),', '("T_Annual_Range", "Annual Temperature Range"),\n        ("T_Seasonal_Range", "Seasonal Temperature Range"),'),
    ('("PSL_Annual_Range", "Annual Sea Level Pressure Range"),', '("PSL_Annual_Range", "Annual Sea Level Pressure Range"),\n        ("PSL_Seasonal_Range", "Seasonal Sea Level Pressure Range"),'),
    ('("PS_Annual_Range", "Annual Surface Pressure Range"),', '("PS_Annual_Range", "Annual Surface Pressure Range"),\n        ("PS_Seasonal_Range", "Seasonal Surface Pressure Range"),'),
    ('("W_Spd_Annual_Range", "Annual Wind Speed Range"),', '("W_Spd_Annual_Range", "Annual Wind Speed Range"),\n        ("W_Spd_Seasonal_Range", "Seasonal Wind Speed Range"),'),
    ('("RH_Annual_Range", "Annual Relative Humidity Range"),', '("RH_Annual_Range", "Annual Relative Humidity Range"),\n        ("RH_Seasonal_Range", "Seasonal Relative Humidity Range"),'),
    ('("Td_Annual_Range", "Annual Dew Point Range"),', '("Td_Annual_Range", "Annual Dew Point Range"),\n        ("Td_Seasonal_Range", "Seasonal Dew Point Range"),'),
    ('("Sol_Annual_Range", "Annual Solar Radiation Range"),', '("Sol_Annual_Range", "Annual Solar Radiation Range"),\n        ("Sol_Seasonal_Range", "Seasonal Solar Radiation Range"),'),
    ('("UV_Annual_Range", "Annual UV Index Range"),', '("UV_Annual_Range", "Annual UV Index Range"),\n        ("UV_Seasonal_Range", "Seasonal UV Index Range"),'),
    ('("Cld_Annual_Range", "Annual Cloud Cover Range"),', '("Cld_Annual_Range", "Annual Cloud Cover Range"),\n        ("Cld_Seasonal_Range", "Seasonal Cloud Cover Range"),'),
]

for old_s, new_s in rag_mod_updates:
    if new_s not in rag_content and old_s in rag_content:
        rag_content = rag_content.replace(old_s, new_s, 1)

# Add to SHP_FIELD_MAP in Toolboxes/raster_atlas_generator.py
if '"T_Seasonal_Range": "T_SeaRng"' not in rag_content:
    rag_content = rag_content.replace('    "T_Month_Mean": "T_MonMean",\n', '    "T_Month_Mean": "T_MonMean",\n' + shp_ranges, 1)

# Add Generate_Monthly_Rasters parameter to getParameterInfo() in Toolboxes/raster_atlas_generator.py
rag_param_target = '''        p_tscope.category = "Time Window"
        p_tscope.description = (
            "TEMPORAL MATRIX SCOPE. Select which temporal scopes and seasons to compute and map "
            "(Annual, Winter, Spring, Summer, Autumn). Uncheck any seasons not needed (e.g. keep only "
            "Annual for fast regional atlas, or Summer only for heat waves). The tool computes only the "
            "Cartesian product of selected Climate Modules and selected Temporal Scope."
        )'''

rag_param_addition = '''

        p_monthly_rasters = arcpy.Parameter(
            displayName="Generate Monthly Climatology Rasters (Jan–Dec) / توليد راستر مناخي مستقل لكل شهر من أشهر السنة",
            name="Generate_Monthly_Rasters",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        p_monthly_rasters.value = False
        p_monthly_rasters.category = "Time Window"
        p_monthly_rasters.description = (
            "GENERATE 12 INDIVIDUAL MONTHLY RASTERS (Jan-Dec). When checked, interpolates independent "
            "climatological surface rasters for all 12 calendar months into a dedicated 'Month' subfolder "
            "for each selected element."
        )'''

if 'p_monthly_rasters = arcpy.Parameter(' not in rag_content:
    rag_content = rag_content.replace(rag_param_target, rag_param_target + rag_param_addition, 1)
    rag_content = rag_content.replace('p_tscope, p_filter_scope,', 'p_tscope, p_monthly_rasters, p_filter_scope,', 1)

# In _build_wind_vectors in Toolboxes/raster_atlas_generator.py
rag_wv_target = '''        periods = [
            ("Annual", "W_Spd_Annual_Mean", "W_Dir_Annual_Mean"),'''
rag_wv_repl = '''        periods = [
            ("Annual", "W_Spd_Annual_Mean", "W_Dir_Annual_Mean"),
            ("Month", "W_Spd_Month_Mean", "W_Dir_Month_Mean"),'''
if '("Month", "W_Spd_Month_Mean", "W_Dir_Month_Mean")' not in rag_content:
    rag_content = rag_content.replace(rag_wv_target, rag_wv_repl, 1)

with io.open(rag_path, "w", encoding="utf-8") as f:
    f.write(rag_content)
print("Toolboxes/raster_atlas_generator.py updated successfully.")
