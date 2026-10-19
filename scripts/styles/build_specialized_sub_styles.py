# -*- coding: utf-8 -*-
"""
Generate Specialized Seasonal and Thematic Sub-Style ArcMap Databases (.style)
Creates tailored sub-style databases directly beside the master styles in each element folder,
as well as inside the consolidated directories, with FULLY UPDATED internal classifications
for Color Ramps, Colors, and Fill Symbols.
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

def build_style_db(target_path, style_list, element_label, ramp_cat=None, color_cat=None, fill_cat=None):
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

    safe_ramp_cat = unicode(ramp_cat or safe_elem_label)
    safe_color_cat = unicode(color_cat or (safe_elem_label + " Colors"))
    safe_fill_cat = unicode(fill_cat or (safe_elem_label + " Zones"))

    for s in style_list:
        s_id = s.get("id", "")
        s_name_en = s.get("name_en") or s_id
        s_cat = s.get("category") or safe_elem_label
        is_diverging = (s_cat.lower() == "diverging")

        classes_map = s.get("classes", {})
        sorted_tier_keys = sorted([int(k) for k in classes_map.keys()])

        theme_tag = safe_elem_label.split(" and ")[0].strip() if " and " in safe_elem_label else safe_elem_label.strip()

        for nclass in sorted_tier_keys:
            hex_list = classes_map.get(nclass) or classes_map.get(unicode(nclass)) or classes_map.get(str(nclass))
            if not hex_list:
                continue

            stepped_name = u"[%s] %s - Stepped (%d Classes)" % (theme_tag, s_name_en, nclass)
            r_stepped = create_stepped_multipart_ramp(hex_list, stepped_name)
            item_s = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            it_s = item_s.QueryInterface(m_disp.IStyleGalleryItem)
            it_s.Name = stepped_name
            it_s.Category = u"Default Ramps"
            it_s.Item = r_stepped
            sg.AddItem(it_s)
            ramp_count += 1

            smooth_name = u"[%s] %s - Smooth (%d Classes)" % (theme_tag, s_name_en, nclass)
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

                rgb_obj = make_rgb(r, g, b)
                it_col = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                it_c_i = it_col.QueryInterface(m_disp.IStyleGalleryItem)
                it_c_i.Name = c_label
                it_c_i.Category = safe_color_cat
                it_c_i.Item = rgb_obj
                sg.AddItem(it_c_i)
                color_count += 1

                fill_obj = create_fill_symbol(hex_c)
                it_f = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                it_f_i = it_f.QueryInterface(m_disp.IStyleGalleryItem)
                it_f_i.Name = f_label
                it_f_i.Category = safe_fill_cat
                it_f_i.Item = fill_obj
                sg.AddItem(it_f_i)
                fill_count += 1

    sg.SaveStyle(target_path, "Color Ramps", "")
    sg.SaveStyle(target_path, "Colors", "")
    sg.SaveStyle(target_path, "Fill Symbols", "")
    del sg, sg_storage, sg_obj
    gc.collect()
    time.sleep(0.05)
    return ramp_count, color_count, fill_count

def main():
    print("=================================================================")
    print("BUILDING SPECIALIZED SUB-STYLES WITH UPDATED INTERNAL CATEGORIES")
    print("=================================================================")

    # Build lookup
    all_elements = [{"folder": "01_Temperature", "name_en": "Temperature", "name_ar": "درجات الحرارة", "styles": gcs.TEMPERATURE_STYLES}] + gcs.OTHER_ELEMENTS
    style_by_id = {}
    for el in all_elements:
        for s in el["styles"]:
            style_by_id[s["id"]] = s

    substyles_spec = [
        # --- 01_Temperature ---
        {
            "folder": "01_Temperature",
            "file": "01_Temp_Annual_Mean.style",
            "label": "Annual Temperature Mean",
            "ramp_cat": "Annual Temperature Ramps",
            "color_cat": "Annual Temperature Colors",
            "fill_cat": "Annual Temperature Zones",
            "ids": ["Temp_Div_RdYlBu_Brewer", "Temp_Multi_Thermal_Crameri", "Temp_Multi_SpectralMuted", "Temp_Div_RdBu_IPCC"]
        },
        {
            "folder": "01_Temperature",
            "file": "01_Temp_Summer_Max.style",
            "label": "Summer and Extreme Maximum Temperature",
            "ramp_cat": "Summer Max Temperature Ramps",
            "color_cat": "Summer Max Colors",
            "fill_cat": "Summer Heat Zones",
            "ids": ["Temp_Seq_WarmRed", "Temp_Seq_AmberOrange", "Temp_Multi_HeatwaveRisk", "Temp_Seq_TropicalNights", "Temp_Multi_NASA_LST"]
        },
        {
            "folder": "01_Temperature",
            "file": "01_Temp_Winter_Min.style",
            "label": "Winter and Minimum Temperature / Frost",
            "ramp_cat": "Winter Min Temperature Ramps",
            "color_cat": "Winter Cold & Frost Colors",
            "fill_cat": "Winter Cold Zones",
            "ids": ["Temp_Seq_CoolBlue", "Temp_Seq_FrostThreshold", "Temp_Div_Nuuk_Cryo", "Temp_Seq_DeepPurple"]
        },
        {
            "folder": "01_Temperature",
            "file": "01_Temp_Spring_Autumn.style",
            "label": "Transitional Seasons Spring and Autumn",
            "ramp_cat": "Transitional Temperature Ramps",
            "color_cat": "Spring & Autumn Colors",
            "fill_cat": "Transitional Temperature Zones",
            "ids": ["Temp_Multi_SpectralMuted", "Temp_Div_TealCoral", "Temp_Div_PuOr", "Temp_Multi_WMO_Standard"]
        },
        {
            "folder": "01_Temperature",
            "file": "01_Temp_Unified_All_Seasons.style",
            "label": "Unified Multi-Panel Seasons Comparison",
            "ramp_cat": "Unified Multi-Panel Ramps",
            "color_cat": "Unified Climatological Colors",
            "fill_cat": "Unified Climatological Zones",
            "ids": ["Temp_Multi_Thermal_Crameri", "Temp_Div_RdYlBu_Brewer", "Temp_Multi_NOAA_NWS", "Temp_Multi_ERA5_Thermal"]
        },
        {
            "folder": "01_Temperature",
            "file": "01_Temp_Heat_Index.style",
            "label": "Perceived Temperature and Heat Index",
            "ramp_cat": "Heat Index Ramps",
            "color_cat": "Perceived Temperature Colors",
            "fill_cat": "Heat Stress Zones",
            "ids": ["Temp_Multi_SteadmanApparent", "Temp_Multi_HeatwaveRisk"]
        },

        # --- 02_Precipitation ---
        {
            "folder": "02_Precipitation",
            "file": "02_Precip_Annual_Total.style",
            "label": "Annual Total Precipitation",
            "ramp_cat": "Annual Precipitation Ramps",
            "color_cat": "Annual Rainfall Colors",
            "fill_cat": "Annual Precipitation Zones",
            "ids": ["Precip_Seq_YlGnBu", "Precip_Seq_Blues", "Precip_Seq_CHIRPS_Rain", "Precip_Multi_ERA5_Total"]
        },
        {
            "folder": "02_Precipitation",
            "file": "02_Precip_Winter_Rain.style",
            "label": "Winter Precipitation and Flash Floods",
            "ramp_cat": "Winter Rain & Snow Ramps",
            "color_cat": "Winter Rain & Flood Colors",
            "fill_cat": "Winter Flood Zones",
            "ids": ["Precip_Seq_Blues", "Precip_Multi_FlashFlood", "Precip_Multi_SnowIce", "Precip_Seq_SWE_Snowpack"]
        },
        {
            "folder": "02_Precipitation",
            "file": "02_Precip_Summer_Monsoon.style",
            "label": "Summer Rain and Tropical Monsoon",
            "ramp_cat": "Summer Monsoon Ramps",
            "color_cat": "Monsoon Rainfall Colors",
            "fill_cat": "Monsoon Precipitation Zones",
            "ids": ["Precip_Seq_BuPu", "Precip_Div_MonsoonAnomaly", "Precip_Multi_NASA_GPM"]
        },
        {
            "folder": "02_Precipitation",
            "file": "02_Precip_Spring_Autumn_Storms.style",
            "label": "Transitional Storms and Radar Reflectivity",
            "ramp_cat": "Transitional Storm Ramps",
            "color_cat": "Radar Reflectivity Colors",
            "fill_cat": "Convective Storm Zones",
            "ids": ["Precip_Multi_DopplerRadar", "Precip_Multi_ConvectiveStorm", "Precip_Seq_Intensity_WMO"]
        },
        {
            "folder": "02_Precipitation",
            "file": "02_Precip_Drought_Anomaly_SPI.style",
            "label": "Precipitation Anomaly and Drought SPI",
            "ramp_cat": "Precipitation Anomaly Ramps",
            "color_cat": "Drought & Surplus Colors",
            "fill_cat": "SPI Drought Zones",
            "ids": ["Precip_Div_BrBG", "Precip_Div_SPI", "Precip_Div_SPEI_Multi"]
        },

        # --- 03_Sea_Level_Pressure ---
        {
            "folder": "03_Sea_Level_Pressure",
            "file": "03_Pres_Annual_MSL_Standard.style",
            "label": "Standard Mean Sea Level Pressure",
            "ramp_cat": "Standard MSL Pressure Ramps",
            "color_cat": "Standard Pressure Colors",
            "fill_cat": "Isobaric Pressure Zones",
            "ids": ["Pres_Div_WMO_MSLP", "Pres_Synoptic_HighLow", "Pres_Multi_MicrobarIsobars"]
        },
        {
            "folder": "03_Sea_Level_Pressure",
            "file": "03_Pres_Winter_Siberian_High.style",
            "label": "Winter Siberian Anticyclone and Mediterranean Lows",
            "ramp_cat": "Winter Anticyclone Ramps",
            "color_cat": "Winter Anticyclone Colors",
            "fill_cat": "Winter Pressure Zones",
            "ids": ["Pres_Div_SiberianAnticyclone", "Pres_Div_SevereCyclone"]
        },
        {
            "folder": "03_Sea_Level_Pressure",
            "file": "03_Pres_Summer_Subtropical_Low.style",
            "label": "Summer Subtropical High and Thermal Lows",
            "ramp_cat": "Summer Subtropical Low Ramps",
            "color_cat": "Summer Low Pressure Colors",
            "fill_cat": "Summer Pressure Zones",
            "ids": ["Pres_Synoptic_Subtropical", "Pres_Multi_Cyclones", "Pres_Seq_Density"]
        },

        # --- 04_Surface_Pressure ---
        {
            "folder": "04_Surface_Pressure",
            "file": "04_SPres_Hypsometric_Terrain.style",
            "label": "Hypsometric Surface Pressure and Complex Terrain",
            "ramp_cat": "Hypsometric Surface Pressure Ramps",
            "color_cat": "Hypsometric Pressure Colors",
            "fill_cat": "Hypsometric Pressure Zones",
            "ids": ["SPres_Seq_Hypsometric", "SPres_Multi_Terrain", "SPres_Multi_MicroRelief"]
        },
        {
            "folder": "04_Surface_Pressure",
            "file": "04_SPres_Basin_Plateau_Extreme.style",
            "label": "Plateau and Deep Basin Surface Pressure",
            "ramp_cat": "Basin & Plateau Pressure Ramps",
            "color_cat": "Plateau & Basin Colors",
            "fill_cat": "Plateau & Basin Zones",
            "ids": ["SPres_Seq_ValleyBasin", "SPres_Multi_PlateauHigh", "SPres_Div_Anomaly"]
        },

        # --- 05_Wind ---
        {
            "folder": "05_Wind",
            "file": "05_Wind_Annual_Beaufort.style",
            "label": "Annual Wind Speed Beaufort Scale",
            "ramp_cat": "Beaufort Wind Speed Ramps",
            "color_cat": "Beaufort Scale Colors",
            "fill_cat": "Beaufort Wind Zones",
            "ids": ["Wind_Seq_Beaufort", "Wind_Seq_PowerDensity"]
        },
        {
            "folder": "05_Wind",
            "file": "05_Wind_Winter_Gales_Chill.style",
            "label": "Winter Marine Gales and Wind Chill",
            "ramp_cat": "Winter Marine Gale Ramps",
            "color_cat": "Winter Gale Colors",
            "fill_cat": "Winter Gale Zones",
            "ids": ["Wind_Seq_MarineGale", "Wind_Multi_WindChill", "Wind_Multi_SeaState"]
        },
        {
            "folder": "05_Wind",
            "file": "05_Wind_Spring_Khamsin_Dust.style",
            "label": "Spring Khamsin Dust Storms and Severe Gales",
            "ramp_cat": "Spring Khamsin Dust Ramps",
            "color_cat": "Khamsin Dust Colors",
            "fill_cat": "Khamsin Dust Zones",
            "ids": ["Wind_Multi_KhamsinDust", "Wind_Multi_EF_Tornado"]
        },
        {
            "folder": "05_Wind",
            "file": "05_Wind_Summer_Thermal_Breeze.style",
            "label": "Summer Coastal Sea Breeze and Jet Stream",
            "ramp_cat": "Coastal Thermal Breeze Ramps",
            "color_cat": "Coastal Breeze Colors",
            "fill_cat": "Coastal Breeze Zones",
            "ids": ["Wind_Seq_ThermalBreeze", "Wind_Multi_DopplerVelocity", "Wind_Multi_JetStream"]
        },

        # --- 06_Relative_Humidity ---
        {
            "folder": "06_Relative_Humidity",
            "file": "06_Humidity_Annual_Mean.style",
            "label": "Annual Relative and Specific Humidity",
            "ramp_cat": "Annual Relative Humidity Ramps",
            "color_cat": "Relative Humidity Colors",
            "fill_cat": "Relative Humidity Zones",
            "ids": ["RH_Seq_YlGnBu", "RH_Seq_SpecificHumidity", "RH_Multi_PWAT_AtmRiver"]
        },
        {
            "folder": "06_Relative_Humidity",
            "file": "06_Humidity_Summer_Stress_WBGT.style",
            "label": "Summer Humidity Heat Stress and Vapor Deficit",
            "ramp_cat": "Summer Humidity Stress Ramps",
            "color_cat": "Heat Stress Humidity Colors",
            "fill_cat": "Heat Stress Humidity Zones",
            "ids": ["RH_Multi_WBGT_Stress", "RH_Seq_VPD_Agricultural", "RH_Multi_SatWaterVapor"]
        },
        {
            "folder": "06_Relative_Humidity",
            "file": "06_Humidity_Winter_Fog_Saturation.style",
            "label": "Winter Dense Fog and Dew Point Saturation",
            "ramp_cat": "Winter Fog & Saturation Ramps",
            "color_cat": "Winter Fog Colors",
            "fill_cat": "Winter Fog Zones",
            "ids": ["RH_Seq_FogSaturation", "RH_Multi_DewPointTemp"]
        },
        {
            "folder": "06_Relative_Humidity",
            "file": "06_Humidity_Transitional_Depression.style",
            "label": "Transitional Dew Point Depression and Flux",
            "ramp_cat": "Dew Point Depression Ramps",
            "color_cat": "Dew Point Depression Colors",
            "fill_cat": "Dew Point Depression Zones",
            "ids": ["RH_Div_DewPointDepression", "RH_Div_MoistureFlux"]
        },

        # --- 07_Solar_Radiation ---
        {
            "folder": "07_Solar_Radiation",
            "file": "07_Solar_Annual_GHI_ESMAP.style",
            "label": "Annual Global Horizontal Irradiation (GHI / PVOUT)",
            "ramp_cat": "Annual Solar Radiation (GHI) Ramps",
            "color_cat": "Solar Radiation Colors",
            "fill_cat": "Solar Radiation Zones",
            "ids": ["Solar_Seq_YlOrRd", "Solar_Seq_ESMAP_GHI", "Solar_Seq_PVOUT"]
        },
        {
            "folder": "07_Solar_Radiation",
            "file": "07_Solar_Summer_DNI_Thermal.style",
            "label": "Summer Peak Direct Normal Irradiation DNI",
            "ramp_cat": "Summer Peak Solar DNI Ramps",
            "color_cat": "Direct Solar Colors",
            "fill_cat": "Direct Solar Zones",
            "ids": ["Solar_Seq_DNI_Thermal", "Solar_Seq_GTI_Tilted", "Solar_Seq_ClearnessIndex"]
        },
        {
            "folder": "07_Solar_Radiation",
            "file": "07_Solar_Winter_Diffuse_Sunshine.style",
            "label": "Winter Sunshine Duration and Diffuse Radiation",
            "ramp_cat": "Winter Diffuse & Sunshine Ramps",
            "color_cat": "Diffuse Solar Colors",
            "fill_cat": "Diffuse Solar Zones",
            "ids": ["Solar_Seq_SunshineDuration", "Solar_Seq_DHI_Diffuse", "Solar_Multi_SolarAlbedo"]
        },
        {
            "folder": "07_Solar_Radiation",
            "file": "07_Solar_Spring_Autumn_Agronomy.style",
            "label": "Agronomy Photosynthetically Active Radiation PAR",
            "ramp_cat": "Agronomy PAR Radiation Ramps",
            "color_cat": "Agronomy PAR Colors",
            "fill_cat": "Agronomy PAR Zones",
            "ids": ["Solar_Seq_PAR_Agronomy", "Solar_Seq_YlOrRd"]
        },

        # --- 08_UV_Index ---
        {
            "folder": "08_UV_Index",
            "file": "08_UV_Annual_WHO_Standard.style",
            "label": "Mandatory WHO Standard UV Protection",
            "ramp_cat": "WHO Standard UV Index Ramps",
            "color_cat": "WHO UV Index Colors",
            "fill_cat": "WHO UV Health Zones",
            "ids": ["UV_Standard_WHO", "UV_EPA_HealthRisk"]
        },
        {
            "folder": "08_UV_Index",
            "file": "08_UV_Summer_Peak_Extreme.style",
            "label": "Summer Noon Extreme UV Index Peak",
            "ramp_cat": "Summer Extreme UV Peak Ramps",
            "color_cat": "Summer UV Risk Colors",
            "fill_cat": "Extreme UV Risk Zones",
            "ids": ["UV_SummerPeak", "UV_ErythemalDose", "UV_Multi_Fitzpatrick"]
        },
        {
            "folder": "08_UV_Index",
            "file": "08_UV_Winter_Safe_Synthesis.style",
            "label": "Winter Safe UV and Vitamin D Synthesis",
            "ramp_cat": "Winter Safe UV Ramps",
            "color_cat": "Safe Vitamin D Colors",
            "fill_cat": "Safe UV Synthesis Zones",
            "ids": ["UV_Seq_VitaminDSynthesis", "UV_Multi_HighAltitude", "UV_Div_OzoneDepletion"]
        },

        # --- 09_Cloud_Cover ---
        {
            "folder": "09_Cloud_Cover",
            "file": "09_Cloud_Annual_Okta_Fraction.style",
            "label": "Annual Cloud Amount Okta Scale and Fraction",
            "ramp_cat": "Okta Scale Cloud Cover Ramps",
            "color_cat": "Cloud Okta Colors",
            "fill_cat": "Cloud Fraction Zones",
            "ids": ["Cloud_Seq_Okta", "Cloud_Seq_Fraction"]
        },
        {
            "folder": "09_Cloud_Cover",
            "file": "09_Cloud_Winter_Low_Fog.style",
            "label": "Winter Low Cloud Ceiling Fog and Optical Depth",
            "ramp_cat": "Winter Low Cloud & Fog Ramps",
            "color_cat": "Low Ceiling Cloud Colors",
            "fill_cat": "Aviation Fog Zones",
            "ids": ["Cloud_Seq_LowCloudFog", "Cloud_Seq_OpticalDepth", "Cloud_Seq_CirrusIce"]
        },
        {
            "folder": "09_Cloud_Cover",
            "file": "09_Cloud_Summer_Convective_Aerosol.style",
            "label": "Summer Convective Cloud Tops and Aerosol Dust",
            "ramp_cat": "Summer Convective Cloud Ramps",
            "color_cat": "Convective Cloud Colors",
            "fill_cat": "Convective Storm Zones",
            "ids": ["Cloud_Multi_ConvectiveTops", "Cloud_Multi_AOD_Aerosol", "Cloud_Multi_IR_CloudTop"]
        },

        # --- 10_Drought_And_Aridity ---
        {
            "folder": "10_Drought_And_Aridity",
            "file": "10_Aridity_Annual_UNEP_DeMartonne.style",
            "label": "Annual Aridity UNEP and De Martonne",
            "ramp_cat": "UNEP & De Martonne Aridity Ramps",
            "color_cat": "Aridity Index Colors",
            "fill_cat": "Aridity Climate Zones",
            "ids": ["Aridity_UNEP_World", "Aridity_SoilMoistureDeficit"]
        },
        {
            "folder": "10_Drought_And_Aridity",
            "file": "10_Drought_Summer_PET_Hargreaves.style",
            "label": "Summer Evapotranspiration PET Hargreaves",
            "ramp_cat": "Summer Evapotranspiration PET Ramps",
            "color_cat": "Evapotranspiration Colors",
            "fill_cat": "Evaporative Demand Zones",
            "ids": ["Drought_ETo_Hargreaves", "Drought_EDDI_Evaporative", "Drought_ETa_ActualDeficit"]
        },
        {
            "folder": "10_Drought_And_Aridity",
            "file": "10_Drought_Water_Balance_SPEI.style",
            "label": "Climatic Water Balance SPEI and Crop Moisture",
            "ramp_cat": "Water Balance & Deficit (SPEI) Ramps",
            "color_cat": "Climatic Water Deficit Colors",
            "fill_cat": "Water Balance Zones",
            "ids": ["Drought_SPEI_Index", "Drought_PDSI_Palmer", "Drought_CMI_CropMoisture", "Drought_NDWI_WaterIndex"]
        },
        {
            "folder": "10_Drought_And_Aridity",
            "file": "10_Drought_Desert_Encroachment.style",
            "label": "Desert Encroachment and Oasis Degradation",
            "ramp_cat": "Desert Encroachment Ramps",
            "color_cat": "Desertification Colors",
            "fill_cat": "Desertification Zones",
            "ids": ["Drought_Multi_DesertBoundaries", "Aridity_UNEP_World"]
        },

        # --- 11_Climate_Models ---
        {
            "folder": "11_Climate_Models",
            "file": "11_Model_Temp_Warming_Stripes.style",
            "label": "Warming Stripes and Temperature Anomalies",
            "ramp_cat": "Warming Stripes & Anomaly Ramps",
            "color_cat": "Warming Stripes Colors",
            "fill_cat": "Warming Anomaly Zones",
            "ids": ["Model_Div_WarmingStripes", "Model_Div_TempAnomaly", "Model_Seq_TropicalNightsTR20"]
        },
        {
            "folder": "11_Climate_Models",
            "file": "11_Model_Precip_Change_Extremes.style",
            "label": "Precipitation Change and Extreme Indices",
            "ramp_cat": "Precipitation Change & Extremes Ramps",
            "color_cat": "Precipitation Change Colors",
            "fill_cat": "Extreme Climate Zones",
            "ids": ["Model_Div_PrecipChange", "Model_Div_ExtremePrecipR95p", "Model_Seq_ConsecutiveDryDays", "Model_Multi_ExtremesIndex"]
        },
        {
            "folder": "11_Climate_Models",
            "file": "11_Model_SSP_Scenarios_Multi.style",
            "label": "IPCC Shared Socioeconomic SSPs and Sea Level Rise",
            "ramp_cat": "Shared Socioeconomic SSP Ramps",
            "color_cat": "SSP Scenario Colors",
            "fill_cat": "Socioeconomic Scenario Zones",
            "ids": ["Model_Multi_SSPSenarios", "Model_Multi_SeaLevelRise", "Model_Seq_DegreeDays"]
        }
    ]

    total_substyles = len(substyles_spec)
    built_count = 0

    for idx, spec in enumerate(substyles_spec):
        folder = spec["folder"]
        fname = spec["file"]
        label = spec["label"]
        ramp_cat = spec.get("ramp_cat", label)
        color_cat = spec.get("color_cat", label + " Colors")
        fill_cat = spec.get("fill_cat", label + " Zones")
        style_ids = spec["ids"]

        selected = []
        for sid in style_ids:
            if sid in style_by_id:
                selected.append(style_by_id[sid])
            else:
                print("WARNING: Missing ID: %s" % sid)

        if not selected:
            print("ERROR: No styles found for %s" % fname)
            continue

        # Target 1: Inside the element's dedicated folder (beside original .style)
        elem_dir = os.path.join(STYLE_DIR, folder)
        target_local = os.path.join(elem_dir, fname)

        # Build style database with custom categories
        ramps, colors, fills = build_style_db(target_local, selected, label, ramp_cat, color_cat, fill_cat)
        built_count += 1
        print("[%2d/%2d] BUILT: %s/%s -> %d Ramps (%s) | %d Colors (%s) | %d Fills (%s)" % (
            idx + 1, total_substyles, folder, fname, ramps, ramp_cat, colors, color_cat, fills, fill_cat
        ))

        # Copy to consolidated and output directories
        shutil.copyfile(target_local, os.path.join(OUT_STYLE_DIR, fname))
        shutil.copyfile(target_local, os.path.join(CONSOLIDATED_1, fname))
        shutil.copyfile(target_local, os.path.join(CONSOLIDATED_2, fname))

    print("\nSUCCESS! All %d specialized seasonal and thematic sub-styles generated with updated internal categories!" % built_count)

if __name__ == "__main__":
    main()
