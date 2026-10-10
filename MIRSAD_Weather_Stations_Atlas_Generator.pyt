# -*- coding: utf-8 -*-
"""NOAA / WMO Ground Weather Stations Climate Atlas Generator.
Native Dual Compatibility for ArcGIS Pro (Python 3) & ArcMap 10.8 (Python 2.7).

Author: Ahmad Ibrahim (أحمد إبراهيم)
Email: ahmadibrahim.geo@gmail.com
Version: 2.0 (October 2026) - Enterprise Carbon-Copy Edition
"""
import os
import sys
import math
import json
import csv
import io
import datetime
import time

TOOLBOX_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(TOOLBOX_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

HUB_DIR = os.path.join(TOOLBOX_DIR, "Weather_Stations_Hub")
SHP_HUB_GLOBAL = os.path.join(HUB_DIR, "Shapefiles", "Global_Weather_Stations.shp")
SHP_HUB_EGYPT = os.path.join(HUB_DIR, "Shapefiles", "Egypt_Weather_Stations.shp")
GDB_HUB = os.path.join(HUB_DIR, "Geodatabase", "Weather_Stations_Directory.gdb")

try:
    import arcpy
    HAS_ARCPY = hasattr(arcpy, "da") and hasattr(arcpy, "Parameter")
except ImportError:
    HAS_ARCPY = False



def _load_core_module():
    """Dynamically loads the core climate atlas engine."""
    pyt_path = os.path.join(TOOLBOX_DIR, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
    if not os.path.exists(pyt_path):
        pyt_path = os.path.join(TOOLBOX_DIR, "POWER_Climate_Atlas_Generator_10_8.pyt")
    if not os.path.exists(pyt_path):
        raise RuntimeError("Core module not found at: %s" % pyt_path)
    if sys.version_info[0] >= 3:
        from importlib.machinery import SourceFileLoader
        loader = SourceFileLoader("power_atlas_core", pyt_path)
        return loader.load_module("power_atlas_core")
    else:
        import imp
        return imp.load_source("power_atlas_core", pyt_path)


_core = _load_core_module()

try:
    from country_continent_registry import COUNTRY_REGISTRY, get_country_info
except Exception:
    COUNTRY_REGISTRY = {}
    def get_country_info(code):
        return (code, "", "Other", False)


class Toolbox(object):
    def __init__(self):
        self.label = "MIRSAD - Ground Weather Stations Atlas Generator"
        self.alias = "MirsadStationsAtlas"
        self.description = (
            "Enterprise Geoprocessing Toolbox for Automated Ground Weather "
            "Stations Ingestion, Climatological Processing, and Spatial Interpolation "
            "using certified NOAA ISD and WMO Global Networks under the MIRSAD platform."
        )
        self.tools = [WeatherStationsAtlasGenerator]


class WeatherStationsAtlasGenerator(_core.PowerClimateAtlasGenerator):
    def __init__(self):
        super(WeatherStationsAtlasGenerator, self).__init__() if hasattr(super(WeatherStationsAtlasGenerator, self), '__init__') else _core.PowerClimateAtlasGenerator.__init__(self)
        self.label = "MIRSAD: Ground Weather Stations Climate Atlas Generator"
        self.description = (
            "Harvests certified NOAA & WMO ground weather stations, downloads historical "
            "climate time series from NASA POWER, Open-Meteo ERA5, or NOAA ISD direct ground observations, "
            "computes climatological normals and bioclimatic indicators, builds geodatabase feature classes, "
            "exports Excel workbooks, and generates lossless continuous raster surfaces."
        )
        self.canRunInBackground = False

    def getParameterInfo(self):
        core_params = _core.PowerClimateAtlasGenerator.getParameterInfo(self)
        core_pdict = dict((p.name, p) for p in core_params)

        # ------------------------------------------------------------------
        # Category 1: Station Selection & Study Area (Top Inputs)
        # ------------------------------------------------------------------
        p_st_mode = arcpy.Parameter(
            displayName="Station Selection Mode",
            name="Station_Selection_Mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        p_st_mode.filter.type = "ValueList"
        p_st_mode.filter.list = [
            "Select by Country (National Network)",
            "Spatial Intersect by Study Area Boundary (Polygon Clip)",
            "Custom Station IDs (Manual Entry / From Explorer)",
            "Global Network (Worldwide - Caution: High Station Count)",
            "Local Saved Station Layer (Shapefile / Geodatabase)"
        ]
        p_st_mode.value = "Select by Country (National Network)"
        p_st_mode.category = "Station Selection & Study Area"
        p_st_mode.description = (
            "Choose how weather stations are chosen:\n"
            "• 'Select by Country (National Network)': filters certified NOAA/WMO stations by country or region.\n"
            "• 'Spatial Intersect by Study Area Boundary': clips stations falling within your polygon boundary (+ optional buffer).\n"
            "• 'Custom Station IDs': specify USAF/WMO station IDs directly.\n"
            "• 'Global Network': process all global stations worldwide.\n"
            "• 'Local Saved Station Layer': load a pre-saved station feature layer from disk."
        )

        p_st_region = arcpy.Parameter(
            displayName="Geographic Region / Continent Filter",
            name="Region_Filter",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )
        p_st_region.filter.type = "ValueList"
        p_st_region.filter.list = [
            "Arab League Countries (22 Nations)",
            "All Countries Worldwide (Global Open Dataset)",
            "Africa",
            "Asia",
            "Europe",
            "North America",
            "South America",
            "Oceania",
            "Antarctica"
        ]
        p_st_region.value = "Arab League Countries (22 Nations)"
        p_st_region.category = "Station Selection & Study Area"
        p_st_region.description = "First-tier spatial filter to narrow down country list."

        p_st_country = arcpy.Parameter(
            displayName="Select Country / Scope",
            name="Select_Country",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )
        p_st_country.filter.type = "ValueList"
        p_st_country.filter.list = [
            "[All Arab League Countries (ARAB)]",
            "Palestine (PS)",
            "Egypt (EG)",
            "Saudi Arabia (SA)",
            "Algeria (AG)",
            "Morocco (MO)",
            "Iraq (IZ)",
            "Sudan (SU)",
            "Oman (MU)",
            "Libya (LY)",
            "Tunisia (TS)",
            "Kuwait (KU)",
            "Syria (SY)",
            "Somalia (SO)",
            "Jordan (JO)",
            "United Arab Emirates (AE)",
            "Qatar (QA)",
            "Yemen (YM)",
            "Mauritania (MR)",
            "Comoros (CN)",
            "Bahrain (BA)",
            "Lebanon (LE)",
            "Djibouti (DJ)"
        ]
        p_st_country.value = "[All Arab League Countries (ARAB)]"
        p_st_country.category = "Station Selection & Study Area"
        p_st_country.description = "Second-tier national network filter or aggregate scope (e.g. All Arab League, All Asian)."

        p_st_poly = arcpy.Parameter(
            displayName="Study Area Boundary Polygon (Optional Mask / Clip)",
            name="Study_Area_Polygon",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input"
        )
        p_st_poly.filter.list = ["Polygon"]
        p_st_poly.category = "Station Selection & Study Area"
        p_st_poly.description = (
            "OPTIONAL polygon feature layer. Used to spatially clip weather stations, "
            "define the processing extent/mask, and clip output rasters."
        )

        p_st_buffer = arcpy.Parameter(
            displayName="Include Neighboring Buffer Stations (30 km Halo for Interpolation)",
            name="Include_Buffer_Stations",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        p_st_buffer.value = True
        p_st_buffer.category = "Station Selection & Study Area"
        p_st_buffer.description = (
            "When polygon clipping is active, includes stations within a 30 km halo outside the boundary "
            "to prevent edge degradation and distortion during spatial interpolation."
        )

        p_st_custom = arcpy.Parameter(
            displayName="Custom Station IDs (Semicolon-Separated USAF Codes)",
            name="Custom_Station_IDs",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )
        p_st_custom.category = "Station Selection & Study Area"
        p_st_custom.description = "OPTIONAL. Enter semicolon-separated USAF station codes (e.g. 623660;624140;623180)."

        p_st_local = arcpy.Parameter(
            displayName="Local Station Layer (Optional Point Layer)",
            name="Local_Station_Features",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input"
        )
        p_st_local.filter.list = ["Point", "Multipoint"]
        p_st_local.category = "Station Selection & Study Area"
        p_st_local.description = "OPTIONAL. Load a pre-existing weather stations shapefile or GDB feature class."

        # ------------------------------------------------------------------
        # Category 2: Climate Data Source (Expanded Provider Suite)
        # ------------------------------------------------------------------
        p_csrc = core_pdict.get("Climate_Data_Source")
        if p_csrc:
            p_csrc.filter.list = [
                "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling",
                "NOAA ISD / GHCN Direct Station Ground Observations Archive",
                "NASA POWER API (Agroclimatology / MERRA-2)",
                "Open-Meteo Historical API (ERA5 Reanalysis - High-Resolution)"
            ]
            p_csrc.value = "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling"
            p_csrc.description = (
                "Select meteorological data provider for the weather stations:\n"
                "• 'Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling' [Default]: Uses certified ground station observations with automatic satellite and reanalysis gap-filling for 100% data completeness.\n"
                "• 'NOAA ISD / GHCN Direct Station Ground Observations Archive': Direct official observational records from NOAA NCEI ground instruments.\n"
                "• 'NASA POWER API': Gridded global agroclimatology (solar radiation, temperature, precipitation, 1981-Present).\n"
                "• 'Open-Meteo Historical API': High-resolution ERA5-Land reanalysis (~9 km resolution, 1940-Present)."
            )

        # Hide manual Input_Point_Features in favor of Station Selectors
        if "Input_Point_Features" in core_pdict:
            core_pdict["Input_Point_Features"].parameterType = "Optional"
            core_pdict["Input_Point_Features"].enabled = False

        # Hide legacy Study_Area_Mask in favor of Study_Area_Polygon
        if "Study_Area_Mask" in core_pdict:
            core_pdict["Study_Area_Mask"].parameterType = "Optional"
            core_pdict["Study_Area_Mask"].enabled = False

        station_params = [
            p_st_mode, p_st_region, p_st_country,
            p_st_poly, p_st_buffer, p_st_custom, p_st_local
        ]

        filtered_core = [
            p for p in core_params
            if p.name not in ("Input_Point_Features", "Study_Area_Mask")
        ]

        hidden_core = [
            core_pdict["Input_Point_Features"],
            core_pdict["Study_Area_Mask"]
        ]

        return station_params + filtered_core + hidden_core

    def updateParameters(self, parameters):
        pdict = dict((p.name, p) for p in parameters)

        # 1. Station selection UI controls
        st_mode = pdict.get("Station_Selection_Mode")
        mode_val = st_mode.valueAsText if st_mode else "Select by Country (National Network)"

        p_reg = pdict.get("Region_Filter")
        p_ctry = pdict.get("Select_Country")
        p_custom = pdict.get("Custom_Station_IDs")
        p_local = pdict.get("Local_Station_Features")
        p_poly = pdict.get("Study_Area_Polygon")
        p_buf = pdict.get("Include_Buffer_Stations")

        if mode_val == "Select by Country (National Network)":
            if p_reg: p_reg.enabled = True
            if p_ctry: p_ctry.enabled = True
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = False
        elif mode_val == "Spatial Intersect by Study Area Boundary (Polygon Clip)":
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = True
        elif mode_val == "Custom Station IDs (Manual Entry / From Explorer)":
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = True
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = False
        elif mode_val == "Local Saved Station Layer (Shapefile / Geodatabase)":
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = True
            if p_buf: p_buf.enabled = False
        elif mode_val == "Global Network (Worldwide - Caution: High Station Count)":
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = False

        # Dynamic population of Country Filter based on Region_Filter
        if p_reg and p_ctry:
            reg_val = p_reg.valueAsText or "Arab League Countries"
            if "Arab" in reg_val:
                p_ctry.filter.list = [
                    "[All Arab League Countries (ARAB)]",
                    "Palestine (PS)", "Egypt (EG)", "Saudi Arabia (SA)", "Algeria (AG)", "Morocco (MO)",
                    "Iraq (IZ)", "Sudan (SU)", "Oman (MU)", "Libya (LY)", "Tunisia (TS)",
                    "Kuwait (KU)", "Syria (SY)", "Somalia (SO)", "Jordan (JO)",
                    "United Arab Emirates (AE)", "Qatar (QA)", "Yemen (YM)",
                    "Mauritania (MR)", "Comoros (CN)", "Bahrain (BA)",
                    "Lebanon (LE)", "Djibouti (DJ)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "[All Arab League Countries (ARAB)]"
            elif "Africa" in reg_val:
                p_ctry.filter.list = [
                    "[All African Countries (AFRICA)]",
                    "Angola (AO)", "Benin (BN)", "Botswana (BC)", "Burkina Faso (UV)",
                    "Burundi (BY)", "Cameroon (CM)", "Cape Verde (CV)", "Chad (CD)",
                    "Congo (CF)", "DR Congo (CG)", "Equatorial Guinea (EK)",
                    "Eritrea (ER)", "Eswatini (WZ)", "Ethiopia (ET)", "Gabon (GB)",
                    "Gambia (GA)", "Ghana (GH)", "Guinea (GV)", "Guinea-Bissau (PU)",
                    "Ivory Coast (IV)", "Kenya (KE)", "Lesotho (LT)", "Liberia (LI)",
                    "Madagascar (MA)", "Malawi (MI)", "Mali (ML)", "Mauritius (MP)",
                    "Mozambique (MZ)", "Namibia (WA)", "Niger (NG)", "Nigeria (NI)",
                    "Rwanda (RW)", "Senegal (SG)", "Seychelles (SE)", "Sierra Leone (SL)",
                    "South Africa (SF)", "South Sudan (OD)", "Tanzania (TZ)",
                    "Togo (TO)", "Uganda (UG)", "Zambia (ZA)", "Zimbabwe (ZI)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "[All African Countries (AFRICA)]"
            elif "Asia" in reg_val:
                p_ctry.filter.list = [
                    "[All Asian Countries (ASIA)]",
                    "Palestine (PS)",
                    "Afghanistan (AF)", "Armenia (AM)", "Azerbaijan (AJ)", "Bangladesh (BG)",
                    "Bhutan (BT)", "Brunei (BX)", "Cambodia (CB)", "China (CH)",
                    "Georgia (GG)", "India (IN)", "Indonesia (ID)", "Iran (IR)",
                    "Japan (JA)", "Kazakhstan (KZ)", "Kyrgyzstan (KG)", "Laos (LA)",
                    "Malaysia (MY)", "Maldives (MV)", "Mongolia (MG)", "Myanmar (BM)",
                    "Nepal (NP)", "North Korea (KN)", "Pakistan (PK)", "Philippines (RP)",
                    "Singapore (SN)", "South Korea (KS)", "Sri Lanka (CE)", "Taiwan (TW)",
                    "Tajikistan (TI)", "Thailand (TH)", "Timor-Leste (TP)", "Turkey (TU)",
                    "Turkmenistan (TM)", "Uzbekistan (UZ)", "Vietnam (VM)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "[All Asian Countries (ASIA)]"
            elif "Europe" in reg_val:
                p_ctry.filter.list = [
                    "[All European Countries (EUROPE)]",
                    "Albania (AL)", "Austria (AU)", "Belarus (BO)", "Belgium (BE)",
                    "Bosnia and Herzegovina (BK)", "Bulgaria (BU)", "Croatia (HR)",
                    "Cyprus (CY)", "Czech Republic (EZ)", "Denmark (DA)", "Estonia (EN)",
                    "Finland (FI)", "France (FR)", "Germany (GM)", "Greece (GR)",
                    "Hungary (HU)", "Iceland (IC)", "Ireland (EI)", "Italy (IT)",
                    "Latvia (LG)", "Lithuania (LH)", "Luxembourg (LU)", "Moldova (MD)",
                    "Montenegro (MJ)", "Netherlands (NL)", "North Macedonia (MK)",
                    "Norway (NO)", "Poland (PL)", "Portugal (PO)", "Romania (RO)",
                    "Russia (RS)", "Serbia (RI)", "Slovakia (LO)", "Slovenia (SI)",
                    "Spain (SP)", "Sweden (SW)", "Switzerland (SZ)", "Ukraine (UP)",
                    "United Kingdom (UK)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "[All European Countries (EUROPE)]"
            elif "North America" in reg_val:
                p_ctry.filter.list = [
                    "[All North American Countries (NORTH AMERICA)]",
                    "Canada (CA)", "United States (US)", "Mexico (MX)", "Guatemala (GT)",
                    "Belize (BH)", "Honduras (HO)", "El Salvador (ES)", "Nicaragua (NU)",
                    "Costa Rica (CS)", "Panama (PM)", "Cuba (CU)", "Jamaica (JM)",
                    "Haiti (HA)", "Dominican Republic (DR)", "Bahamas (BF)", "Trinidad and Tobago (TD)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "United States (US)"
            elif "South America" in reg_val:
                p_ctry.filter.list = [
                    "[All South American Countries (SOUTH AMERICA)]",
                    "Argentina (AR)", "Bolivia (BL)", "Brazil (BR)", "Chile (CI)",
                    "Colombia (CO)", "Ecuador (EC)", "Guyana (GY)", "Paraguay (PA)",
                    "Peru (PE)", "Suriname (NS)", "Uruguay (UY)", "Venezuela (VE)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "Brazil (BR)"
            elif "Oceania" in reg_val:
                p_ctry.filter.list = [
                    "[All Oceania Countries (OCEANIA)]",
                    "Australia (AS)", "New Zealand (NZ)", "Fiji (FJ)", "Papua New Guinea (PP)",
                    "Solomon Islands (BP)", "Vanuatu (NH)", "Samoa (WS)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "Australia (AS)"
            elif "All" in reg_val:
                p_ctry.filter.list = ["[All Countries Worldwide (WORLD)]"]
                p_ctry.value = "[All Countries Worldwide (WORLD)]"

        # Sync Study_Area_Mask with Study_Area_Polygon
        p_mask = pdict.get("Study_Area_Mask")
        if p_mask and p_poly:
            p_mask.value = p_poly.value

        # Open-Meteo Model enable/disable sync with Climate_Data_Source
        p_src = pdict.get("Climate_Data_Source")
        p_om_m = pdict.get("OpenMeteo_Model")
        if p_src and p_om_m:
            src_text = p_src.valueAsText or ""
            p_om_m.enabled = ("Open-Meteo" in src_text or "Hybrid" in src_text)

        # Call core updateParameters for units, temporal filters, interpolation, etc.
        _core.PowerClimateAtlasGenerator.updateParameters(self, parameters)

    def _parse_target_country(self, ctry_str, reg_str):
        if not ctry_str:
            return "ARAB" if ("Arab" in (reg_str or "")) else "WORLD"
        c_up = ctry_str.upper()
        if "ARAB" in c_up:
            return "ARAB"
        if "WORLD" in c_up or "ALL COUNTRIES" in c_up:
            return "WORLD"
        if "AFRICA" in c_up:
            return "AFRICA"
        if "ASIA" in c_up:
            return "ASIA"
        if "EUROPE" in c_up:
            return "EUROPE"
        if "NORTH AMERICA" in c_up:
            return "NORTH AMERICA"
        if "SOUTH AMERICA" in c_up:
            return "SOUTH AMERICA"
        if "OCEANIA" in c_up:
            return "OCEANIA"
        if "PALESTINE" in c_up or "(PS)" in c_up:
            return "PS"
        if "(" in ctry_str and ")" in ctry_str:
            code = ctry_str.split("(")[1].split(")")[0].strip().upper()
            if code in ("IS", "IL", "GZ", "WE", "PS"):
                return "PS"
            return code
        return ctry_str.strip().upper()

    def _load_all_stations(self, local_layer=None):
        stations = []
        if local_layer and HAS_ARCPY:
            try:
                fields = ["Station_ID", "Name", "Country", "Country_Nm", "Continent", "Is_Arab", "Lat", "Lon", "Elev_m"]
                actual_fields = [f.name for f in arcpy.ListFields(local_layer)]
                valid_fields = [f for f in fields if f in actual_fields]
                with arcpy.da.SearchCursor(local_layer, valid_fields + ["SHAPE@XY"]) as cur:
                    for row in cur:
                        rdict = dict(zip(valid_fields, row[:-1]))
                        xy = row[-1]
                        lat = float(xy[1]) if xy else float(rdict.get("Lat", 0.0))
                        lon = float(xy[0]) if xy else float(rdict.get("Lon", 0.0))
                        name_val = str(rdict.get("Name", "Station"))
                        ctry = str(rdict.get("Country", "")).strip().upper()
                        if ctry in ("IS", "IL", "GZ", "WE") or (ctry == "PS" and not (lat < 15.0 and lon > 100.0)):
                            ctry = "PS"
                            c_nm = "Palestine"
                            cont = "Asia"
                            is_ar = True
                        else:
                            c_nm = str(rdict.get("Country_Nm", ctry))
                            cont = str(rdict.get("Continent", "Other"))
                            is_ar = bool(rdict.get("Is_Arab", False))
                        stations.append({
                            "Station_ID": str(rdict.get("Station_ID", "")),
                            "Name": name_val,
                            "Country": ctry,
                            "Country_Nm": c_nm,
                            "Continent": cont,
                            "Is_Arab": is_ar,
                            "Lat": lat,
                            "Lon": lon,
                            "Elev_m": float(rdict.get("Elev_m", 0.0))
                        })
                if stations:
                    return stations
            except Exception:
                pass

        # Load from HUB Directory
        shp_target = SHP_HUB_GLOBAL if os.path.exists(SHP_HUB_GLOBAL) else SHP_HUB_EGYPT
        if os.path.exists(shp_target):
            if HAS_ARCPY:
                fields = ["Station_ID", "Name", "Country", "Country_Nm", "Continent", "Is_Arab", "Lat", "Lon", "Elev_m", "SHAPE@XY"]
                with arcpy.da.SearchCursor(shp_target, fields) as cur:
                    for r in cur:
                        name_val = str(r[1])
                        lat = float(r[6])
                        lon = float(r[7])
                        ctry = str(r[2]).strip().upper()
                        if ctry in ("IS", "IL", "GZ", "WE") or (ctry == "PS" and not (lat < 15.0 and lon > 100.0)):
                            ctry = "PS"
                            c_nm = "Palestine"
                            cont = "Asia"
                            is_ar = True
                        else:
                            c_nm = str(r[3])
                            cont = str(r[4])
                            is_ar = bool(r[5])
                        stations.append({
                            "Station_ID": str(r[0]),
                            "Name": name_val,
                            "Country": ctry,
                            "Country_Nm": c_nm,
                            "Continent": cont,
                            "Is_Arab": is_ar,
                            "Lat": lat,
                            "Lon": lon,
                            "Elev_m": float(r[8])
                        })
            else:
                # Standalone fallback (geopandas or pyogrio)
                try:
                    import geopandas as gpd
                    df = gpd.read_file(shp_target)
                    for _, r in df.iterrows():
                        name_val = str(r["Name"])
                        lat = float(r["Lat"])
                        lon = float(r["Lon"])
                        ctry = str(r["Country"]).strip().upper()
                        if ctry in ("IS", "IL", "GZ", "WE") or (ctry == "PS" and not (lat < 15.0 and lon > 100.0)):
                            ctry = "PS"
                            c_nm = "Palestine"
                            cont = "Asia"
                            is_ar = True
                        else:
                            c_nm = str(r.get("Country_Nm", ctry))
                            cont = str(r.get("Continent", "Other"))
                            is_ar = bool(r.get("Is_Arab", False))
                        stations.append({
                            "Station_ID": str(r["Station_ID"]),
                            "Name": name_val,
                            "Country": ctry,
                            "Country_Nm": c_nm,
                            "Continent": cont,
                            "Is_Arab": is_ar,
                            "Lat": lat,
                            "Lon": lon,
                            "Elev_m": float(r["Elev_m"])
                        })
                except Exception:
                    try:
                        import pyogrio
                        df = pyogrio.read_dataframe(shp_target)
                        for _, r in df.iterrows():
                            name_val = str(r["Name"])
                            lat = float(r["Lat"])
                            lon = float(r["Lon"])
                            ctry = str(r["Country"]).strip().upper()
                            if ctry in ("IS", "IL", "GZ", "WE") or (ctry == "PS" and not (lat < 15.0 and lon > 100.0)):
                                ctry = "PS"
                                c_nm = "Palestine"
                                cont = "Asia"
                                is_ar = True
                            else:
                                c_nm = str(r.get("Country_Nm", ctry))
                                cont = str(r.get("Continent", "Other"))
                                is_ar = bool(r.get("Is_Arab", False))
                            stations.append({
                                "Station_ID": str(r["Station_ID"]),
                                "Name": name_val,
                                "Country": ctry,
                                "Country_Nm": c_nm,
                                "Continent": cont,
                                "Is_Arab": is_ar,
                                "Lat": lat,
                                "Lon": lon,
                                "Elev_m": float(r["Elev_m"])
                            })
                    except Exception:
                        pass

        return stations

    def _resolve_stations(self, mode, target_country, study_poly, inc_buf, custom_ids, local_layer=None):
        all_stations = self._load_all_stations(local_layer)
        if not all_stations:
            return []

        if mode == "Select by Country (National Network)":
            if target_country == "ARAB":
                return [s for s in all_stations if s.get("Is_Arab")]
            elif target_country in ("WORLD", "ALL"):
                return all_stations
            elif target_country in ("AFRICA", "ASIA", "EUROPE", "NORTH AMERICA", "SOUTH AMERICA", "OCEANIA", "ANTARCTICA"):
                return [s for s in all_stations if s.get("Continent", "").upper() == target_country]
            elif target_country == "PS":
                return [s for s in all_stations if s.get("Country") == "PS"]
            else:
                return [s for s in all_stations if s.get("Country") == target_country]

        elif mode == "Spatial Intersect by Study Area Boundary (Polygon Clip)":
            if not study_poly:
                return all_stations
            return self._intersect_stations(all_stations, study_poly, inc_buf)

        elif mode == "Custom Station IDs (Manual Entry / From Explorer)":
            ids = [x.strip() for x in (custom_ids or "").replace(",", ";").split(";") if x.strip()]
            return [s for s in all_stations if s.get("Station_ID") in ids]

        elif mode == "Global Network (Worldwide - Caution: High Station Count)":
            return all_stations

        elif mode == "Local Saved Station Layer (Shapefile / Geodatabase)":
            return all_stations

        return all_stations

    def _intersect_stations(self, stations, study_poly, inc_buf):
        if not HAS_ARCPY:
            return stations
        try:
            desc = arcpy.Describe(study_poly)
            poly_sr = desc.spatialReference
            wgs = arcpy.SpatialReference(4326)

            # Build union geometry of mask polygon
            poly_geom = None
            with arcpy.da.SearchCursor(study_poly, ["SHAPE@"]) as cur:
                for row in cur:
                    g = row[0]
                    if poly_sr.factoryCode != 4326:
                        g = g.projectAs(wgs)
                    if poly_geom is None:
                        poly_geom = g
                    else:
                        poly_geom = poly_geom.union(g)

            if not poly_geom:
                return stations

            # Buffer geometry if requested (30 km halo in degrees ~ 0.27 deg)
            search_geom = poly_geom.buffer(0.27) if inc_buf else poly_geom

            selected = []
            for s in stations:
                pt = arcpy.PointGeometry(arcpy.Point(s["Lon"], s["Lat"]), wgs)
                if search_geom.contains(pt) or search_geom.touches(pt):
                    selected.append(s)
            return selected
        except Exception:
            return stations

    def _write_stations_shapefile(self, stations, out_shp):
        if HAS_ARCPY:
            out_dir = os.path.dirname(out_shp)
            shp_name = os.path.basename(out_shp)
            if arcpy.Exists(out_shp):
                arcpy.Delete_management(out_shp)
            wgs = arcpy.SpatialReference(4326)
            arcpy.CreateFeatureclass_management(out_dir, shp_name, "POINT", spatial_reference=wgs)
            arcpy.AddField_management(out_shp, "Station_ID", "TEXT", field_length=20)
            arcpy.AddField_management(out_shp, "Name", "TEXT", field_length=100)
            arcpy.AddField_management(out_shp, "Country", "TEXT", field_length=10)
            arcpy.AddField_management(out_shp, "Elev_m", "DOUBLE")
            arcpy.AddField_management(out_shp, "Source_ID", "LONG")

            fields = ["SHAPE@XY", "Station_ID", "Name", "Country", "Elev_m", "Source_ID"]
            with arcpy.da.InsertCursor(out_shp, fields) as cur:
                for idx, s in enumerate(stations):
                    xy = (s["Lon"], s["Lat"])
                    cur.insertRow([xy, s["Station_ID"], s["Name"][:100], s["Country"], s["Elev_m"], idx + 1])
        else:
            # Standalone fallback using pyogrio
            import pyogrio
            from shapely.geometry import Point
            import geopandas as gpd
            data = []
            for idx, s in enumerate(stations):
                data.append({
                    "Station_ID": s["Station_ID"],
                    "Name": s["Name"],
                    "Country": s["Country"],
                    "Elev_m": s["Elev_m"],
                    "Source_ID": idx + 1,
                    "geometry": Point(s["Lon"], s["Lat"])
                })
            gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
            gdf.to_file(out_shp, driver="ESRI Shapefile", encoding="utf-8")

    def _enrich_station_metadata(self, out_ws, stations):
        if not HAS_ARCPY:
            return
        gdb_path = os.path.join(out_ws, "Climate_Database.gdb")
        if not arcpy.Exists(gdb_path):
            return

        station_lookup = dict((idx + 1, s) for idx, s in enumerate(stations))
        try:
            arcpy.env.workspace = gdb_path
            fcs = arcpy.ListFeatureClasses() or []
            for fc in fcs:
                existing_fields = [f.name for f in arcpy.ListFields(fc)]
                if "Source_ID" not in existing_fields:
                    continue

                if "Station_ID" not in existing_fields:
                    arcpy.AddField_management(fc, "Station_ID", "TEXT", field_length=20)
                if "Station_Nm" not in existing_fields:
                    arcpy.AddField_management(fc, "Station_Nm", "TEXT", field_length=100)
                if "Country_Cd" not in existing_fields:
                    arcpy.AddField_management(fc, "Country_Cd", "TEXT", field_length=10)
                if "Elev_Meters" not in existing_fields:
                    arcpy.AddField_management(fc, "Elev_Meters", "DOUBLE")

                update_fields = ["Source_ID", "Station_ID", "Station_Nm", "Country_Cd", "Elev_Meters"]
                with arcpy.da.UpdateCursor(fc, update_fields) as cur:
                    for row in cur:
                        sid = row[0]
                        sdata = station_lookup.get(sid)
                        if sdata:
                            row[1] = sdata.get("Station_ID", "")
                            row[2] = sdata.get("Name", "")[:100]
                            row[3] = sdata.get("Country", "")
                            row[4] = float(sdata.get("Elev_m", 0.0))
                            cur.updateRow(row)
        except Exception:
            pass

    def execute(self, parameters, messages):
        pdict = dict((p.name, p) for p in parameters)

        # 1. Resolve Weather Stations
        st_mode = pdict["Station_Selection_Mode"].valueAsText
        st_reg = pdict.get("Region_Filter").valueAsText if pdict.get("Region_Filter") else "Arab League Countries (22 Nations)"
        st_ctry = pdict.get("Select_Country").valueAsText if pdict.get("Select_Country") else "Egypt (EG)"
        study_poly = pdict.get("Study_Area_Polygon").valueAsText if (pdict.get("Study_Area_Polygon") and pdict["Study_Area_Polygon"].valueAsText) else None
        inc_buf = bool(pdict.get("Include_Buffer_Stations").value) if (pdict.get("Include_Buffer_Stations") and pdict["Include_Buffer_Stations"].value is not None) else True
        custom_ids = pdict.get("Custom_Station_IDs").valueAsText if pdict.get("Custom_Station_IDs") else ""
        local_layer = pdict.get("Local_Station_Features").valueAsText if (pdict.get("Local_Station_Features") and pdict["Local_Station_Features"].valueAsText) else None

        target_country = self._parse_target_country(st_ctry, st_reg)

        messages.addMessage("================================================================================")
        messages.addMessage("MIRSAD (مِرصاد) - NOAA / WMO GROUND WEATHER STATIONS CLIMATE ATLAS GENERATOR")
        messages.addMessage("Multi-source Integrated Reanalysis & Surface Atlas Database Platform")
        messages.addMessage("================================================================================")
        messages.addMessage("[1/5] Resolving Weather Station Network (Mode: %s) ..." % st_mode)
        resolved_stations = self._resolve_stations(st_mode, target_country, study_poly, inc_buf, custom_ids, local_layer)

        if not resolved_stations:
            raise RuntimeError("No weather stations matched the selected scope/boundary. Please check your filter or polygon.")

        messages.addMessage("      -> Successfully resolved %d certified ground stations." % len(resolved_stations))

        # 2. Build Scratch Feature Class for Stations
        out_ws = pdict["Output_Workspace"].valueAsText
        if not os.path.exists(out_ws):
            os.makedirs(out_ws)
        scratch_dir = os.path.join(out_ws, "scratch")
        if not os.path.exists(scratch_dir):
            os.makedirs(scratch_dir)

        station_shp = os.path.join(scratch_dir, "Target_Weather_Stations.shp")
        self._write_stations_shapefile(resolved_stations, station_shp)

        # Map to Input_Point_Features & Study_Area_Mask
        pdict["Input_Point_Features"].value = station_shp
        if study_poly:
            pdict["Study_Area_Mask"].value = study_poly

        # 3. Handle Climate_Data_Source mapping for the core engine
        p_csrc = pdict.get("Climate_Data_Source")
        csrc_val = p_csrc.valueAsText if p_csrc else "NASA POWER API (Agroclimatology / MERRA-2)"
        orig_source_name = csrc_val

        if "Hybrid" in csrc_val:
            p_csrc.value = "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling"
        elif "NOAA" in csrc_val:
            p_csrc.value = "NOAA ISD / GHCN Direct Station Ground Observations Archive"
        elif "Open-Meteo" in csrc_val:
            p_csrc.value = "Open-Meteo Historical API (ERA5 Reanalysis)"
        else:
            p_csrc.value = "NASA POWER API"

        messages.addMessage("[2/5] Initializing Climate Engine with Data Source: %s" % orig_source_name)

        # 4. Invoke Core Calculation & Mapping Engine
        _core.PowerClimateAtlasGenerator.execute(self, parameters, messages)

        # 5. Enrich Resulting GDB Feature Classes with Station Metadata
        messages.addMessage("[5/5] Finalizing Ground Station Metadata & Master Directory ...")
        self._enrich_station_metadata(out_ws, resolved_stations)
        messages.addMessage("All ground weather station atlas operations completed successfully!")
