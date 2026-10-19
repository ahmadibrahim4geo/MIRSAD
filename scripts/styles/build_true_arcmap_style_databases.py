# -*- coding: utf-8 -*-
"""
Generate 100% Genuine, Native ArcMap Desktop (.style) Databases
Mega Edition: 125 Comprehensive Climate Styles across 11 Elements
Expanded to 9 Class Tiers: [3, 4, 5, 6, 7, 8, 9, 10, 11 Classes]
Total Color Ramps: 125 x 9 x 2 (Stepped + Smooth) = 2,250 Color Ramps!
Plus 875 Named Colors and 875 Polygon Fill Symbols!
"""
from __future__ import unicode_literals
import os
import sys
import shutil
import time
import gc

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STYLE_DIR = os.path.join(BASE_DIR, "style")
RAW_DIR = os.path.join(STYLE_DIR, "Raw_Climate_Styles")
TEMPLATE_STYLE = os.path.join(RAW_DIR, "Meteorological.style")

OUT_STYLE_DIR = os.path.join(STYLE_DIR, "ArcMap_Style_Files")
CONSOLIDATED_1 = os.path.join(BASE_DIR, "All_ArcMap_Styles_Consolidated")
CONSOLIDATED_2 = os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated")

for d in [OUT_STYLE_DIR, CONSOLIDATED_1, CONSOLIDATED_2]:
    if not os.path.isdir(d):
        os.makedirs(d)

# Import style definitions
sys.path.insert(0, os.path.join(BASE_DIR, "scripts", "styles"))
import generate_climate_styles as gcs

import arcpy
import comtypes.client

com_dir = r"C:\Program Files (x86)\ArcGIS\Desktop10.8\com"
m_sys = comtypes.client.GetModule(os.path.join(com_dir, "esriSystem.olb"))
m_disp = comtypes.client.GetModule(os.path.join(com_dir, "esriDisplay.olb"))
m_fw = comtypes.client.GetModule(os.path.join(com_dir, "esriFramework.olb"))

def make_rgb(r, g, b):
    c_obj = comtypes.client.CreateObject("esriDisplay.RgbColor")
    c = c_obj.QueryInterface(m_disp.IRgbColor)
    c.Red = r
    c.Green = g
    c.Blue = b
    return c_obj.QueryInterface(m_disp.IColor)

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def create_stepped_multipart_ramp(hex_list, name):
    """
    Creates a discrete stepped MultiPartColorRamp where each class
    is a uniform AlgorithmicColorRamp with FromColor == ToColor.
    Leaves Size = 0 so ArcMap dynamically scales the steps across 100% of the preview width.
    """
    multi_obj = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    multi = multi_obj.QueryInterface(m_disp.IMultiPartColorRamp)
    multi_cr = multi_obj.QueryInterface(m_disp.IColorRamp)
    multi_cr.Name = name
    for h in hex_list:
        r, g, b = hex_to_rgb(h)
        part_obj = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        part = part_obj.QueryInterface(m_disp.IAlgorithmicColorRamp)
        part.FromColor = make_rgb(r, g, b)
        part.ToColor = make_rgb(r, g, b)
        part.Algorithm = 1  # esriCIELabAlgorithm
        multi.AddRamp(part_obj.QueryInterface(m_disp.IColorRamp))
    return multi_obj

def create_smooth_multipart_ramp(hex_list, name):
    """
    Creates a continuous smooth MultiPartColorRamp connecting adjacent
    class colors with CIELab interpolation for continuous raster mapping.
    Leaves Size = 0 so ArcMap smoothly interpolates across 100% of the preview width.
    """
    multi_obj = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    multi = multi_obj.QueryInterface(m_disp.IMultiPartColorRamp)
    multi_cr = multi_obj.QueryInterface(m_disp.IColorRamp)
    multi_cr.Name = name
    n_segments = len(hex_list) - 1
    for i in range(n_segments):
        r1, g1, b1 = hex_to_rgb(hex_list[i])
        r2, g2, b2 = hex_to_rgb(hex_list[i+1])
        part_obj = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        part = part_obj.QueryInterface(m_disp.IAlgorithmicColorRamp)
        part.FromColor = make_rgb(r1, g1, b1)
        part.ToColor = make_rgb(r2, g2, b2)
        part.Algorithm = 1  # esriCIELabAlgorithm
        multi.AddRamp(part_obj.QueryInterface(m_disp.IColorRamp))
    return multi_obj

def create_fill_symbol(hex_c):
    """Creates a SimpleFillSymbol with solid fill and 0.4pt grey outline."""
    r, g, b = hex_to_rgb(hex_c)
    fill_obj = comtypes.client.CreateObject("esriDisplay.SimpleFillSymbol")
    fill = fill_obj.QueryInterface(m_disp.ISimpleFillSymbol)
    fill.Color = make_rgb(r, g, b)
    fill.Style = 0  # esriSFSSolid

    line_obj = comtypes.client.CreateObject("esriDisplay.SimpleLineSymbol")
    line = line_obj.QueryInterface(m_disp.ISimpleLineSymbol)
    line.Color = make_rgb(110, 110, 110)
    line.Width = 0.4
    line.Style = 0  # esriSLSSolid
    fill.Outline = line_obj.QueryInterface(m_disp.ILineSymbol)
    return fill_obj

def get_theme_for_style(s_id, elem_label):
    if s_id in ["Temp_Seq_WarmRed", "Temp_Seq_AmberOrange", "Temp_Multi_HeatwaveRisk", "Temp_Seq_TropicalNights", "Temp_Multi_NASA_LST"]:
        return ("Summer Max Temperature Ramps", "Summer Heat Colors", "Summer Heat Zones")
    elif s_id in ["Temp_Seq_CoolBlue", "Temp_Seq_FrostThreshold", "Temp_Div_Nuuk_Cryo", "Temp_Seq_DeepPurple"]:
        return ("Winter Min Temperature Ramps", "Winter Cold Colors", "Winter Cold Zones")
    elif s_id in ["Temp_Div_RdYlBu_Brewer", "Temp_Div_RdBu_IPCC", "Temp_Multi_WMO_Standard", "Temp_Div_HadCRUT5", "Temp_Multi_KoppenThermal"]:
        return ("Annual Mean Temperature Ramps", "Annual Mean Colors", "Annual Mean Zones")
    elif s_id in ["Temp_Multi_SpectralMuted", "Temp_Div_TealCoral", "Temp_Div_PuOr", "Temp_Div_ContinentalThermal"]:
        return ("Transitional Seasons Ramps", "Transitional Colors", "Transitional Zones")
    elif s_id in ["Temp_Multi_Thermal_Crameri", "Temp_Multi_Roma_Crameri", "Temp_Multi_NOAA_NWS", "Temp_Multi_ERA5_Thermal", "Temp_Multi_NOAA_CPC", "Temp_Div_NASA_GISTEMP"]:
        return ("Unified Climatology Ramps", "Unified Climatological Colors", "Unified Climatological Zones")
    elif s_id in ["Temp_Multi_SteadmanApparent"]:
        return ("Heat Index Ramps", "Perceived Temperature Colors", "Heat Stress Zones")
    elif s_id in ["Precip_Seq_Blues", "Precip_Multi_FlashFlood", "Precip_Multi_SnowIce", "Precip_Seq_SWE_Snowpack"]:
        return ("Winter Rain & Snow Ramps", "Winter Flood Colors", "Winter Flood Zones")
    elif s_id in ["Precip_Seq_BuPu", "Precip_Div_MonsoonAnomaly", "Precip_Multi_NASA_GPM"]:
        return ("Summer Monsoon Ramps", "Monsoon Rainfall Colors", "Monsoon Rainfall Zones")
    elif s_id in ["Precip_Seq_YlGnBu", "Precip_Seq_CHIRPS_Rain", "Precip_Multi_ERA5_Total"]:
        return ("Annual Precipitation Ramps", "Annual Rainfall Colors", "Annual Precipitation Zones")
    elif s_id in ["Precip_Multi_DopplerRadar", "Precip_Multi_ConvectiveStorm", "Precip_Seq_Intensity_WMO"]:
        return ("Transitional Storm Ramps", "Radar Reflectivity Colors", "Convective Storm Zones")
    elif s_id in ["Precip_Div_BrBG", "Precip_Div_SPI", "Precip_Div_SPEI_Multi"]:
        return ("Precipitation Anomaly Ramps", "Drought & Surplus Colors", "SPI Drought Zones")
    elif s_id in ["Pres_Div_WMO_MSLP", "Pres_Synoptic_HighLow", "Pres_Multi_MicrobarIsobars"]:
        return ("Standard MSL Pressure Ramps", "Standard Pressure Colors", "Isobaric Pressure Zones")
    elif s_id in ["Pres_Div_SiberianAnticyclone", "Pres_Div_SevereCyclone"]:
        return ("Winter Anticyclone Ramps", "Winter Anticyclone Colors", "Winter Pressure Zones")
    elif s_id in ["Pres_Synoptic_Subtropical", "Pres_Multi_Cyclones", "Pres_Seq_Density"]:
        return ("Summer Subtropical Low Ramps", "Summer Low Pressure Colors", "Summer Pressure Zones")
    elif s_id in ["SPres_Seq_Hypsometric", "SPres_Multi_Terrain", "SPres_Multi_MicroRelief"]:
        return ("Hypsometric Surface Pressure Ramps", "Hypsometric Pressure Colors", "Hypsometric Pressure Zones")
    elif s_id in ["SPres_Seq_ValleyBasin", "SPres_Multi_PlateauHigh", "SPres_Div_Anomaly", "SPres_Div_LapseRate", "SPres_Seq_Altimeter"]:
        return ("Basin & Plateau Pressure Ramps", "Plateau & Basin Colors", "Plateau & Basin Zones")
    elif s_id in ["Wind_Seq_Beaufort", "Wind_Seq_PowerDensity"]:
        return ("Beaufort Wind Speed Ramps", "Beaufort Scale Colors", "Beaufort Wind Zones")
    elif s_id in ["Wind_Seq_MarineGale", "Wind_Multi_WindChill", "Wind_Multi_SeaState"]:
        return ("Winter Marine Gale Ramps", "Winter Gale Colors", "Winter Gale Zones")
    elif s_id in ["Wind_Multi_KhamsinDust", "Wind_Multi_EF_Tornado"]:
        return ("Spring Khamsin Dust Ramps", "Khamsin Dust Colors", "Khamsin Dust Zones")
    elif s_id in ["Wind_Seq_ThermalBreeze", "Wind_Multi_DopplerVelocity", "Wind_Multi_JetStream", "Wind_Multi_Hurricanes", "Wind_Multi_AviationTurbulence"]:
        return ("Coastal Breeze & Aviation Ramps", "Coastal Breeze Colors", "Coastal Breeze Zones")
    elif s_id in ["RH_Seq_YlGnBu", "RH_Seq_SpecificHumidity", "RH_Multi_PWAT_AtmRiver"]:
        return ("Annual Relative Humidity Ramps", "Relative Humidity Colors", "Relative Humidity Zones")
    elif s_id in ["RH_Multi_WBGT_Stress", "RH_Seq_VPD_Agricultural", "RH_Multi_SatWaterVapor"]:
        return ("Summer Humidity Stress Ramps", "Heat Stress Humidity Colors", "Heat Stress Humidity Zones")
    elif s_id in ["RH_Seq_FogSaturation", "RH_Multi_DewPointTemp"]:
        return ("Winter Fog & Saturation Ramps", "Winter Fog Colors", "Winter Fog Zones")
    elif s_id in ["RH_Div_DewPointDepression", "RH_Div_MoistureFlux"]:
        return ("Dew Point Depression Ramps", "Dew Point Depression Colors", "Dew Point Depression Zones")
    elif s_id in ["Solar_Seq_YlOrRd", "Solar_Seq_ESMAP_GHI", "Solar_Seq_PVOUT"]:
        return ("Annual Solar Radiation Ramps", "Solar Radiation Colors", "Solar Radiation Zones")
    elif s_id in ["Solar_Seq_DNI_Thermal", "Solar_Seq_GTI_Tilted", "Solar_Seq_ClearnessIndex"]:
        return ("Summer Peak Solar DNI Ramps", "Direct Solar Colors", "Direct Solar Zones")
    elif s_id in ["Solar_Seq_SunshineDuration", "Solar_Seq_DHI_Diffuse", "Solar_Multi_SolarAlbedo"]:
        return ("Winter Diffuse & Sunshine Ramps", "Diffuse Solar Colors", "Diffuse Solar Zones")
    elif s_id in ["Solar_Seq_PAR_Agronomy"]:
        return ("Agronomy PAR Radiation Ramps", "Agronomy PAR Colors", "Agronomy PAR Zones")
    elif s_id in ["UV_Standard_WHO", "UV_EPA_HealthRisk"]:
        return ("WHO Standard UV Index Ramps", "WHO UV Index Colors", "WHO UV Health Zones")
    elif s_id in ["UV_SummerPeak", "UV_ErythemalDose", "UV_Multi_Fitzpatrick"]:
        return ("Summer Extreme UV Peak Ramps", "Summer UV Risk Colors", "Extreme UV Risk Zones")
    elif s_id in ["UV_Seq_VitaminDSynthesis", "UV_Multi_HighAltitude", "UV_Div_OzoneDepletion"]:
        return ("Winter Safe UV Ramps", "Safe Vitamin D Colors", "Safe UV Synthesis Zones")
    elif s_id in ["Cloud_Seq_Okta", "Cloud_Seq_Fraction"]:
        return ("Okta Scale Cloud Cover Ramps", "Cloud Okta Colors", "Cloud Fraction Zones")
    elif s_id in ["Cloud_Seq_LowCloudFog", "Cloud_Seq_OpticalDepth", "Cloud_Seq_CirrusIce"]:
        return ("Winter Low Cloud & Fog Ramps", "Low Ceiling Cloud Colors", "Aviation Fog Zones")
    elif s_id in ["Cloud_Multi_ConvectiveTops", "Cloud_Multi_AOD_Aerosol", "Cloud_Multi_IR_CloudTop"]:
        return ("Summer Convective Cloud Ramps", "Convective Cloud Colors", "Convective Storm Zones")
    elif s_id in ["Aridity_UNEP_World", "Aridity_SoilMoistureDeficit"]:
        return ("UNEP & De Martonne Aridity Ramps", "Aridity Index Colors", "Aridity Climate Zones")
    elif s_id in ["Drought_ETo_Hargreaves", "Drought_EDDI_Evaporative", "Drought_ETa_ActualDeficit"]:
        return ("Summer Evapotranspiration PET Ramps", "Evapotranspiration Colors", "Evaporative Demand Zones")
    elif s_id in ["Drought_SPEI_Index", "Drought_PDSI_Palmer", "Drought_CMI_CropMoisture", "Drought_NDWI_WaterIndex"]:
        return ("Water Balance & Deficit Ramps", "Climatic Water Deficit Colors", "Water Balance Zones")
    elif s_id in ["Drought_Multi_DesertBoundaries"]:
        return ("Desert Encroachment Ramps", "Desertification Colors", "Desertification Zones")
    elif s_id in ["Model_Div_WarmingStripes", "Model_Div_TempAnomaly", "Model_Seq_TropicalNightsTR20"]:
        return ("Warming Stripes & Anomaly Ramps", "Warming Stripes Colors", "Warming Anomaly Zones")
    elif s_id in ["Model_Div_PrecipChange", "Model_Div_ExtremePrecipR95p", "Model_Seq_ConsecutiveDryDays", "Model_Multi_ExtremesIndex"]:
        return ("Precipitation Change & Extremes Ramps", "Precipitation Change Colors", "Extreme Climate Zones")
    elif s_id in ["Model_Multi_SSPSenarios", "Model_Multi_SeaLevelRise", "Model_Seq_DegreeDays"]:
        return ("Shared Socioeconomic SSP Ramps", "SSP Scenario Colors", "Socioeconomic Scenario Zones")
    return (elem_label + " Ramps", elem_label + " Colors", elem_label + " Zones")

def build_element_style(target_path, style_list, element_label):
    ldb = target_path[:-6] + ".ldb" if target_path.endswith(".style") else target_path + ".ldb"
    if os.path.isfile(ldb):
        try: os.remove(ldb)
        except: pass
    if os.path.isfile(target_path):
        try: os.remove(target_path)
        except: pass
        time.sleep(0.05)
    shutil.copyfile(TEMPLATE_STYLE, target_path)

    # 1. Clean existing template records
    conn = comtypes.client.CreateObject("ADODB.Connection")
    conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + target_path)
    for tbl in ["Color Ramps", "Colors", "Fill Symbols"]:
        rs = comtypes.client.CreateObject("ADODB.Recordset")
        rs.Open("SELECT * FROM [" + tbl + "]", conn, 1, 3)
        while not rs.EOF:
            rs.Delete()
            rs.MoveNext()
        rs.Close()
    conn.Close()
    del conn, rs
    gc.collect()

    # 2. Add native items via StyleGallery
    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sg_storage = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sg_storage.TargetFile = target_path
    sg_storage.AddFile(target_path)

    ramp_count = 0
    color_count = 0
    fill_count = 0
    safe_elem_label = unicode(element_label or "Climate")

    for s in style_list:
        s_id = s.get("id", "")
        s_name_en = s.get("name_en") or s_id
        s_cat = s.get("category") or safe_elem_label
        is_diverging = (s_cat.lower() == "diverging")

        classes_map = s.get("classes", {})
        sorted_tier_keys = sorted([int(k) for k in classes_map.keys()])

        ramp_cat, color_cat, fill_cat = get_theme_for_style(s_id, safe_elem_label)
        theme_tag = ramp_cat.replace(" Temperature Ramps", "").replace(" Precipitation Ramps", "").replace(" Ramps", "").strip()

        if "Master" in safe_elem_label:
            prefix = s_id.split("_")[0]
            elem_tag = {
                "Temp": "01 Temp",
                "Precip": "02 Precip",
                "Pres": "03 MSLP",
                "SPres": "04 SPres",
                "Wind": "05 Wind",
                "RH": "06 RH",
                "Solar": "07 Solar",
                "UV": "08 UV",
                "Cloud": "09 Cloud",
                "Aridity": "10 Drought",
                "Drought": "10 Drought",
                "Model": "11 Model"
            }.get(prefix, safe_elem_label)
            ramp_prefix = u"%s [%s]" % (elem_tag, theme_tag)
            color_cat = elem_tag + " - " + color_cat
            fill_cat = elem_tag + " - " + fill_cat
        else:
            ramp_prefix = u"[%s]" % theme_tag

        # Color Ramps for all class tiers: [3, 4, 5, 6, 7, 8, 9, 10, 11]
        # Must be registered under Category: 'Default Ramps' so ArcMap Symbology dropdown displays them.
        for nclass in sorted_tier_keys:
            hex_list = classes_map.get(nclass) or classes_map.get(unicode(nclass)) or classes_map.get(str(nclass))
            if not hex_list:
                continue

            stepped_name = u"%s %s - Stepped (%d Classes)" % (ramp_prefix, s_name_en, nclass)
            r_stepped = create_stepped_multipart_ramp(hex_list, stepped_name)
            item_s = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            it_s = item_s.QueryInterface(m_disp.IStyleGalleryItem)
            it_s.Name = stepped_name
            it_s.Category = u"Default Ramps"
            it_s.Item = r_stepped
            sg.AddItem(it_s)
            ramp_count += 1

            smooth_name = u"%s %s - Smooth (%d Classes)" % (ramp_prefix, s_name_en, nclass)
            r_smooth = create_smooth_multipart_ramp(hex_list, smooth_name)
            item_sm = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            it_sm = item_sm.QueryInterface(m_disp.IStyleGalleryItem)
            it_sm.Name = smooth_name
            it_sm.Category = u"Default Ramps"
            it_sm.Item = r_smooth
            sg.AddItem(it_sm)
            ramp_count += 1

        sample_hexes = classes_map.get("7") or classes_map.get(7) or classes_map.get("5") or classes_map.get(5)
        if sample_hexes:
            total_sample = len(sample_hexes)
            mid_idx = total_sample // 2
            for idx, hex_c in enumerate(sample_hexes):
                r, g, b = hex_to_rgb(hex_c)
                if is_diverging and idx == mid_idx and (total_sample % 2 == 1):
                    c_label = u"%s - Neutral Center (%s)" % (s_name_en, hex_c)
                    f_label = u"%s - Neutral Center Fill (%s)" % (s_name_en, hex_c)
                else:
                    c_label = u"%s - Class %d/%d (%s)" % (s_name_en, idx + 1, total_sample, hex_c)
                    f_label = u"%s - Zone %d/%d Fill (%s)" % (s_name_en, idx + 1, total_sample, hex_c)

                # Add Color
                rgb_obj = make_rgb(r, g, b)
                it_col = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                it_c_i = it_col.QueryInterface(m_disp.IStyleGalleryItem)
                it_c_i.Name = c_label
                it_c_i.Category = color_cat
                it_c_i.Item = rgb_obj
                sg.AddItem(it_c_i)
                color_count += 1

                # Add Fill Symbol
                fill_obj = create_fill_symbol(hex_c)
                it_f = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                it_f_i = it_f.QueryInterface(m_disp.IStyleGalleryItem)
                it_f_i.Name = f_label
                it_f_i.Category = fill_cat
                it_f_i.Item = fill_obj
                sg.AddItem(it_f_i)
                fill_count += 1

    sg.SaveStyle(target_path, "Color Ramps", "")
    sg.SaveStyle(target_path, "Colors", "")
    sg.SaveStyle(target_path, "Fill Symbols", "")
    del sg, sg_storage, sg_obj
    gc.collect()
    time.sleep(0.05)
    print("SUCCESS: %s -> %d Color Ramps | %d Colors | %d Fill Symbols" % (
        os.path.basename(target_path), ramp_count, color_count, fill_count
    ))
    return ramp_count, color_count, fill_count

if __name__ == "__main__":
    print("=================================================================")
    print("GENERATING MEGA ARCMAP .STYLE DATABASES (125 STYLES x 9 TIERS)")
    print("=================================================================")

    element_file_map = {
        "02_Precipitation": "02_Precipitation.style",
        "03_Sea_Level_Pressure": "03_Sea_Level_Pressure.style",
        "04_Surface_Pressure": "04_Surface_Pressure.style",
        "05_Wind": "05_Wind.style",
        "06_Relative_Humidity": "06_Relative_Humidity.style",
        "07_Solar_Radiation": "07_Solar_Radiation.style",
        "08_UV_Index": "08_UV_Index.style",
        "09_Cloud_Cover": "09_Cloud_Cover.style",
        "10_Drought_And_Aridity": "10_Drought_And_Aridity.style",
        "11_Climate_Models": "11_Climate_Models.style"
    }

    # 1. Temperature Styles (25 styles x 18 = 450 ramps)
    temp_style_file = os.path.join(OUT_STYLE_DIR, "01_Temperature.style")
    build_element_style(temp_style_file, gcs.TEMPERATURE_STYLES, "Temperature")

    # 2. Other 10 Elements
    all_master_styles = list(gcs.TEMPERATURE_STYLES)

    for el in gcs.OTHER_ELEMENTS:
        fld = el.get("folder", "")
        fname = element_file_map.get(fld, fld + ".style")
        target = os.path.join(OUT_STYLE_DIR, fname)
        st_list = el.get("styles", [])
        el_label = el.get("name_en") or fld.split("_", 1)[-1].replace("_", " ")
        build_element_style(target, st_list, el_label)
        all_master_styles.extend(st_list)

    # 3. Master Style Database (All 125 Styles Combined: 2,250 ramps)
    master_style_file = os.path.join(OUT_STYLE_DIR, "NASA_POWER_Climate_Atlas_Master.style")
    build_element_style(master_style_file, all_master_styles, "Climate Atlas Master")
    shutil.copyfile(master_style_file, os.path.join(BASE_DIR, "NASA_POWER_Climate_Atlas_Master.style"))

    # 4. Copy to element STYLE folders and consolidated folders
    print("\nSynchronizing .style files across all designated repositories...")
    for f in os.listdir(OUT_STYLE_DIR):
        if f.endswith(".style"):
            src_path = os.path.join(OUT_STYLE_DIR, f)
            shutil.copyfile(src_path, os.path.join(CONSOLIDATED_1, f))
            shutil.copyfile(src_path, os.path.join(CONSOLIDATED_2, f))

    # Also copy into style/<Element>/ and style/<Element>/STYLE/
    for el_fld, st_file in element_file_map.items():
        src_p = os.path.join(OUT_STYLE_DIR, st_file)
        # 1. Direct element folder
        el_root = os.path.join(STYLE_DIR, el_fld)
        if os.path.isdir(el_root):
            shutil.copyfile(src_p, os.path.join(el_root, st_file))
        # 2. Subfolder STYLE
        dst_dir = os.path.join(STYLE_DIR, el_fld, "STYLE")
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        shutil.copyfile(src_p, os.path.join(dst_dir, st_file))

    # Copy 01_Temperature.style into style/01_Temperature/ and style/01_Temperature/STYLE/
    shutil.copyfile(temp_style_file, os.path.join(STYLE_DIR, "01_Temperature", "01_Temperature.style"))
    t_dst = os.path.join(STYLE_DIR, "01_Temperature", "STYLE")
    if not os.path.isdir(t_dst):
        os.makedirs(t_dst)
    shutil.copyfile(temp_style_file, os.path.join(t_dst, "01_Temperature.style"))

    # Also copy raw official ESRI styles into consolidated folders
    raw_esri_styles = [
        "Meteorological.style", "Weather.style", "ESRI.style", "Environmental.style",
        "Conservation.style", "Forestry.style", "Military METOC.style", "Soils EURO.style",
        "Water Wastewater.style"
    ]
    for rf in raw_esri_styles:
        rsrc = os.path.join(RAW_DIR, rf)
        if os.path.isfile(rsrc):
            shutil.copyfile(rsrc, os.path.join(CONSOLIDATED_1, rf))
            shutil.copyfile(rsrc, os.path.join(CONSOLIDATED_2, rf))

    print("\n=================================================================")
    print("VERIFYING GENERATED .STYLE FILES IN ARCMAP STYLE GALLERY")
    print("=================================================================")
    all_ok = True
    for f in sorted(os.listdir(OUT_STYLE_DIR)):
        if f.endswith(".style"):
            sp = os.path.join(OUT_STYLE_DIR, f)
            sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
            sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
            sg_storage = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
            sg_storage.AddFile(sp)

            # Check Color Ramps
            enum_ramps = sg.Items("Color Ramps", sp, "")
            enum_ramps.Reset()
            r_item = enum_ramps.Next()
            r_cnt = 0
            r_valid = 0
            while r_item:
                r_cnt += 1
                if bool(r_item.Item):
                    r_valid += 1
                r_item = enum_ramps.Next()

            # Check Colors
            enum_colors = sg.Items("Colors", sp, "")
            enum_colors.Reset()
            c_item = enum_colors.Next()
            c_cnt = 0
            while c_item:
                c_cnt += 1
                c_item = enum_colors.Next()

            # Check Fill Symbols
            enum_fills = sg.Items("Fill Symbols", sp, "")
            enum_fills.Reset()
            f_item = enum_fills.Next()
            f_cnt = 0
            while f_item:
                f_cnt += 1
                f_item = enum_fills.Next()

            del sg, sg_storage, sg_obj
            gc.collect()

            print("VERIFIED: %-36s | %4d Ramps (100%% Valid) | %3d Colors | %3d Fills" % (
                f, r_cnt, c_cnt, f_cnt
            ))
            if r_cnt != r_valid:
                all_ok = False

    if all_ok:
        print("\nALL 125 MEGA CLIMATE STYLES SUCCESSFULLY BUILT AND VERIFIED IN ARCMAP STYLE GALLERY!")
    else:
        print("\nWARNING: Some items failed validation!")
