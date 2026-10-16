# -*- coding: utf-8 -*-
"""NOAA / WMO Ground Weather Stations Climate Atlas Generator.
Native Dual Compatibility for ArcGIS Pro (Python 3) & ArcMap 10.8 (Python 2.7).

Author: Ahmad Ibrahim
Email: ahmadibrahim.geo@gmail.com
Version: 2.1 (October 2026) - Enterprise Edition with English & Arabic Tool Suite
"""
import os
import sys
import math
import json
import csv
import io
import datetime
import time
import traceback

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
    def get_country_info(code, lat=None, lon=None):
        return (code, code, "Other", False)


class Toolbox(object):
    def __init__(self):
        self.label = "MIRSAD - Ground Weather Stations Atlas Generator"
        self.alias = "MirsadStationsAtlas"
        self.description = (
            "Enterprise Geoprocessing Toolbox for Automated Ground Weather "
            "Stations Ingestion, Climatological Processing, and Spatial Interpolation "
            "using certified NOAA ISD and WMO Global Networks under the MIRSAD platform."
        )
        self.tools = [WeatherStationsAtlasGenerator, WeatherStationsAtlasGeneratorAR]


class _ParamProxy(object):
    """Immutable parameter proxy that forwards values to core engine without altering host COM parameters."""
    def __init__(self, name, value, value_as_text=None):
        self.name = name
        self.value = value
        self.valueAsText = value_as_text if value_as_text is not None else (str(value) if value is not None else "")

    def __repr__(self):
        return "_ParamProxy(%s, %r)" % (self.name, self.value)


# ==============================================================================
# TOOL 1: ENGLISH PRIMARY TOOL (Pure English Interface)
# ==============================================================================
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
        self.canRunInBackground = True

    def getParameterInfo(self):
        core_params = _core.PowerClimateAtlasGenerator.getParameterInfo(self)
        core_pdict = dict((p.name, p) for p in core_params)

        # ------------------------------------------------------------------
        # Top Inputs: Station Selection & Supplementary Points (Open / Visible)
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
        p_st_country.description = "Second-tier national network filter or aggregate scope (e.g. All Arab League, All Asian)."

        p_st_poly = arcpy.Parameter(
            displayName="Study Area Boundary Polygon (Optional Mask / Clip)",
            name="Study_Area_Polygon",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input"
        )
        p_st_poly.filter.list = ["Polygon"]
        p_st_poly.description = (
            "OPTIONAL polygon feature layer. Used to spatially clip weather stations, "
            "define the processing extent/mask, and clip output rasters."
        )

        p_st_supp = arcpy.Parameter(
            displayName="Supplementary Survey Points (Optional - To Densify Data-Sparse Areas)",
            name="Supplementary_Points",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input"
        )
        p_st_supp.filter.list = ["Point", "Multipoint"]
        p_st_supp.description = (
            "OPTIONAL point feature layer (shapefile or geodatabase feature class). Custom sampling points "
            "(e.g., in unmonitored desert regions or project sites) will be automatically merged with the "
            "selected certified weather stations to enhance spatial interpolation coverage."
        )

        p_st_buffer = arcpy.Parameter(
            displayName="Include Neighboring Buffer Stations (30 km Halo for Interpolation)",
            name="Include_Buffer_Stations",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"
        )
        p_st_buffer.value = True
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
        p_st_custom.description = "OPTIONAL. Enter semicolon-separated USAF station codes (e.g. 623660;624140;623180)."

        p_st_local = arcpy.Parameter(
            displayName="Local Station Layer (Optional Point Layer)",
            name="Local_Station_Features",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input"
        )
        p_st_local.filter.list = ["Point", "Multipoint"]
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

        station_params = [
            p_st_mode, p_st_region, p_st_country,
            p_st_poly, p_st_supp, p_st_buffer, p_st_custom, p_st_local
        ]

        # Completely exclude Input_Point_Features and Study_Area_Mask from GUI
        filtered_core = [
            p for p in core_params
            if p.name not in ("Input_Point_Features", "Study_Area_Mask", "Precalculated_Point_Layers")
        ]

        return station_params + filtered_core

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
                        
                        en_name, ar_name, cont, is_arab = get_country_info(ctry, lat, lon)
                        stations.append({
                            "Station_ID": str(rdict.get("Station_ID", "")),
                            "Name": name_val,
                            "Country": ctry,
                            "Country_Nm": en_name,
                            "Continent": cont,
                            "Is_Arab": is_arab,
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
                try:
                    import geopandas as gpd
                    df = gpd.read_file(shp_target)
                    for _, r in df.iterrows():
                        stations.append({
                            "Station_ID": str(r["Station_ID"]),
                            "Name": str(r["Name"]),
                            "Country": str(r["Country"]).strip().upper(),
                            "Country_Nm": str(r.get("Country_Nm", "")),
                            "Continent": str(r.get("Continent", "Other")),
                            "Is_Arab": bool(r.get("Is_Arab", False)),
                            "Lat": float(r["Lat"]),
                            "Lon": float(r["Lon"]),
                            "Elev_m": float(r.get("Elev_m", 0.0))
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
                # Strict Arab League spatial bounding envelope:
                # Comoros (~ -12.13) to Syria/Tunisia (~ 37.5), Mauritania (~ -17.1) to Oman (~ 60.0)
                return [
                    s for s in all_stations
                    if s.get("Is_Arab") and (-15.0 <= s.get("Lat", 0.0) <= 38.5) and (-18.0 <= s.get("Lon", 0.0) <= 61.0)
                ]
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
                try:
                    arcpy.management.Delete(out_shp)
                except Exception:
                    pass
            wgs = arcpy.SpatialReference(4326)
            arcpy.management.CreateFeatureclass(out_dir, shp_name, "POINT", spatial_reference=wgs)
            arcpy.management.AddField(out_shp, "Station_ID", "TEXT", field_length=20)
            arcpy.management.AddField(out_shp, "Station_Nm", "TEXT", field_length=100)
            arcpy.management.AddField(out_shp, "Country_Cd", "TEXT", field_length=10)
            arcpy.management.AddField(out_shp, "Elev_m", "DOUBLE")
            arcpy.management.AddField(out_shp, "Source_ID", "LONG")
            arcpy.management.AddField(out_shp, "Point_Type", "TEXT", field_length=30)

            fields = ["SHAPE@XY", "Station_ID", "Station_Nm", "Country_Cd", "Elev_m", "Source_ID", "Point_Type"]
            with arcpy.da.InsertCursor(out_shp, fields) as cur:
                for idx, s in enumerate(stations):
                    xy = (s["Lon"], s["Lat"])
                    pt_type = "Supplementary Point" if s.get("Is_Supplementary") else "Ground Station"
                    st_name = (s.get("Name") or s.get("Station_Nm") or "")[:100]
                    st_ctry = (s.get("Country") or s.get("Country_Cd") or "")[:10]
                    cur.insertRow([xy, s["Station_ID"], st_name, st_ctry, float(s.get("Elev_m", 0.0)), idx + 1, pt_type])
        else:
            import pyogrio
            from shapely.geometry import Point
            import geopandas as gpd
            data = []
            for idx, s in enumerate(stations):
                data.append({
                    "Station_ID": s["Station_ID"],
                    "Station_Nm": (s.get("Name") or s.get("Station_Nm") or "")[:100],
                    "Country_Cd": (s.get("Country") or s.get("Country_Cd") or "")[:10],
                    "Elev_m": float(s.get("Elev_m", 0.0)),
                    "Source_ID": idx + 1,
                    "Point_Type": "Supplementary Point" if s.get("Is_Supplementary") else "Ground Station",
                    "geometry": Point(s["Lon"], s["Lat"])
                })
            gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
            gdf.to_file(out_shp, driver="ESRI Shapefile", encoding="utf-8")

    def _enrich_station_metadata(self, out_ws, stations):
        if not HAS_ARCPY:
            return
        gdb_target = None
        if os.path.exists(out_ws):
            for item in os.listdir(out_ws):
                if item.startswith("Climate_Database") and item.endswith(".gdb"):
                    gdb_target = os.path.join(out_ws, item)
                    break
        if not gdb_target or not arcpy.Exists(gdb_target):
            return

        station_lookup = dict((idx + 1, s) for idx, s in enumerate(stations))
        saved_ws = arcpy.env.workspace
        try:
            arcpy.env.workspace = gdb_target
            fcs = arcpy.ListFeatureClasses() or []
            for fc in fcs:
                existing_fields = [f.name for f in arcpy.ListFields(fc)]
                if "Source_ID" not in existing_fields:
                    continue
                # If Station_Nm is already present from shapefile creation, skip schema modifications
                if "Station_Nm" in existing_fields and "Station_ID" in existing_fields:
                    continue

                if "Station_ID" not in existing_fields:
                    arcpy.management.AddField(fc, "Station_ID", "TEXT", field_length=20)
                if "Station_Nm" not in existing_fields:
                    arcpy.management.AddField(fc, "Station_Nm", "TEXT", field_length=100)
                if "Country_Cd" not in existing_fields:
                    arcpy.management.AddField(fc, "Country_Cd", "TEXT", field_length=10)
                if "Elev_Meters" not in existing_fields:
                    arcpy.management.AddField(fc, "Elev_Meters", "DOUBLE")
                if "Point_Type" not in existing_fields:
                    arcpy.management.AddField(fc, "Point_Type", "TEXT", field_length=30)

                update_fields = ["Source_ID", "Station_ID", "Station_Nm", "Country_Cd", "Elev_Meters", "Point_Type"]
                cur = None
                try:
                    cur = arcpy.da.UpdateCursor(fc, update_fields)
                    for row in cur:
                        sid = row[0]
                        sdata = station_lookup.get(sid)
                        if sdata:
                            row[1] = sdata.get("Station_ID", "")
                            row[2] = (sdata.get("Name") or sdata.get("Station_Nm") or "")[:100]
                            row[3] = (sdata.get("Country") or sdata.get("Country_Cd") or "")[:10]
                            row[4] = float(sdata.get("Elev_m", 0.0))
                            row[5] = "Supplementary Point" if sdata.get("Is_Supplementary") else "Ground Station"
                            cur.updateRow(row)
                finally:
                    if cur:
                        del cur
        except Exception:
            pass
        finally:
            arcpy.env.workspace = saved_ws

    def execute(self, parameters, messages):
        pdict = dict((p.name, p) for p in parameters)

        try:
            # 1. Resolve Weather Stations
            raw_mode = pdict["Station_Selection_Mode"].valueAsText or ""
            if "استقطاع" in raw_mode or "Spatial" in raw_mode:
                st_mode = "Spatial Intersect by Study Area Boundary (Polygon Clip)"
            elif "أكواد" in raw_mode or "Custom" in raw_mode:
                st_mode = "Custom Station IDs (Manual Entry / From Explorer)"
            elif "محلية" in raw_mode or "Local" in raw_mode:
                st_mode = "Local Saved Station Layer (Shapefile / Geodatabase)"
            elif "العالمية" in raw_mode or "Global" in raw_mode:
                st_mode = "Global Network (Worldwide - Caution: High Station Count)"
            else:
                st_mode = "Select by Country (National Network)"

            st_reg = pdict.get("Region_Filter").valueAsText if pdict.get("Region_Filter") else "Arab League Countries (22 Nations)"
            st_ctry = pdict.get("Select_Country").valueAsText if pdict.get("Select_Country") else "Egypt (EG)"
            study_poly = pdict.get("Study_Area_Polygon").valueAsText if (pdict.get("Study_Area_Polygon") and pdict["Study_Area_Polygon"].valueAsText) else None
            supp_layer = pdict.get("Supplementary_Points").valueAsText if (pdict.get("Supplementary_Points") and pdict["Supplementary_Points"].valueAsText) else None
            inc_buf = bool(pdict.get("Include_Buffer_Stations").value) if (pdict.get("Include_Buffer_Stations") and pdict["Include_Buffer_Stations"].value is not None) else True
            custom_ids = pdict.get("Custom_Station_IDs").valueAsText if pdict.get("Custom_Station_IDs") else ""
            local_layer = pdict.get("Local_Station_Features").valueAsText if (pdict.get("Local_Station_Features") and pdict["Local_Station_Features"].valueAsText) else None

            target_country = self._parse_target_country(st_ctry, st_reg)

            messages.addMessage("================================================================================")
            messages.addMessage("MIRSAD - NOAA / WMO GROUND WEATHER STATIONS CLIMATE ATLAS GENERATOR")
            messages.addMessage("Multi-source Integrated Reanalysis & Surface Atlas Database Platform")
            messages.addMessage("================================================================================")
            messages.addMessage("[1/5] Resolving Weather Station Network (Mode: %s) ..." % st_mode)
            resolved_stations = self._resolve_stations(st_mode, target_country, study_poly, inc_buf, custom_ids, local_layer)

            # Ingest Optional Supplementary Points
            supp_stations = []
            if supp_layer and arcpy.Exists(supp_layer):
                messages.addMessage("      -> Ingesting Supplementary Survey Points to densify sampling network ...")
                try:
                    desc_supp = arcpy.Describe(supp_layer)
                    supp_sr = desc_supp.spatialReference
                    wgs = arcpy.SpatialReference(4326)
                    with arcpy.da.SearchCursor(supp_layer, ["SHAPE@XY", "OID@"]) as cur:
                        for idx, row in enumerate(cur):
                            xy = row[0]
                            oid = row[1]
                            if supp_sr.factoryCode != 4326:
                                pt_geom = arcpy.PointGeometry(arcpy.Point(xy[0], xy[1]), supp_sr).projectAs(wgs)
                                pt_lon = pt_geom.firstPoint.X
                                pt_lat = pt_geom.firstPoint.Y
                            else:
                                pt_lon = xy[0]
                                pt_lat = xy[1]

                            supp_stations.append({
                                "Station_ID": "SUPP_%04d" % (idx + 1),
                                "Name": "Auxiliary Point %d (OID %s)" % (idx + 1, oid),
                                "Country": target_country if target_country not in ("ARAB", "WORLD") else "SUPP",
                                "Country_Nm": "Supplementary Survey",
                                "Continent": "Other",
                                "Is_Arab": True,
                                "Lat": float(pt_lat),
                                "Lon": float(pt_lon),
                                "Elev_m": 0.0,
                                "Is_Supplementary": True
                            })
                    messages.addMessage("      -> Successfully added %d supplementary sampling points." % len(supp_stations))
                except Exception as ex_supp:
                    messages.addWarning("Could not ingest supplementary points: %s" % ex_supp)

            all_target_points = resolved_stations + supp_stations

            if not all_target_points:
                raise RuntimeError("No weather stations or supplementary points matched the selected scope/boundary. Please check your filter or polygon.")

            messages.addMessage("      -> Successfully verified %d certified ground stations and %d auxiliary points (Total: %d locations)."
                                % (len(resolved_stations), len(supp_stations), len(all_target_points)))

            # 2. Build Scratch Feature Class for Stations
            out_ws = pdict["Output_Workspace"].valueAsText
            if not os.path.exists(out_ws):
                os.makedirs(out_ws)
            scratch_dir = os.path.join(out_ws, "scratch")
            if not os.path.exists(scratch_dir):
                os.makedirs(scratch_dir)

            station_shp = os.path.join(scratch_dir, "Target_Weather_Stations.shp")
            self._write_stations_shapefile(all_target_points, station_shp)

            # 3. Construct Core Execution Parameters using pure-python proxies
            # This completely avoids mutating ArcGIS Pro's live C++ COM parameters,
            # preventing Access Violation (0xC0000005) crashes when tools finish in both English and Arabic.
            core_parameters = []
            for p in parameters:
                if p.name in ("Input_Point_Features", "Study_Area_Mask", "Supplementary_Points"):
                    continue
                p_name = p.name
                val = p.value
                val_text = p.valueAsText or ""

                # Canonicalize Data Source for core engine
                if p_name == "Climate_Data_Source":
                    if "Hybrid" in val_text or "هجين" in val_text:
                        val = val_text = "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling"
                    elif "NOAA" in val_text or "أرشيف" in val_text:
                        val = val_text = "NOAA ISD / GHCN Direct Station Ground Observations Archive"
                    elif "Open-Meteo" in val_text or "أوبن" in val_text:
                        val = val_text = "Open-Meteo Historical API (ERA5 Reanalysis - High-Resolution)"
                    else:
                        val = val_text = "NASA POWER API (Agroclimatology / MERRA-2)"

                # Canonicalize Operation Mode for core engine
                elif p_name == "Operation_Mode":
                    if "Interpolate" in val_text or "استيفاء" in val_text or "Offline" in val_text:
                        val = val_text = "Interpolate & Map Existing Data (Offline Mode - No Internet)"
                    else:
                        val = val_text = "Download & Generate Atlas (Full Pipeline) [Default]"

                core_parameters.append(_ParamProxy(p_name, val, val_text))

            # Add injected feature layers as proxies
            core_parameters.append(_ParamProxy("Input_Point_Features", station_shp, station_shp))
            if study_poly:
                core_parameters.append(_ParamProxy("Study_Area_Mask", study_poly, study_poly))

            p_csrc_raw = pdict.get("Climate_Data_Source").valueAsText if pdict.get("Climate_Data_Source") else ""
            messages.addMessage("[2/5] Initializing Climate Engine with Data Source: %s" % p_csrc_raw)

            # 4. Invoke Core Calculation & Mapping Engine
            _core.PowerClimateAtlasGenerator.execute(self, core_parameters, messages)

            # 6. Enrich Resulting GDB Feature Classes with Station Metadata
            messages.addMessage("[5/5] Finalizing Ground Station Metadata & Master Directory ...")
            self._enrich_station_metadata(out_ws, all_target_points)
            messages.addMessage("All ground weather station atlas operations completed successfully!")

        except Exception as ex:
            messages.addErrorMessage("MIRSAD EXECUTION ERROR: %s" % str(ex))
            messages.addErrorMessage(traceback.format_exc())
            raise
        finally:
            try:
                arcpy.env.workspace = None
            except Exception:
                pass


# ==============================================================================
# TOOL 2: ARABIC COMPANION TOOL (النسخة العربية الكاملة)
# ==============================================================================
class WeatherStationsAtlasGeneratorAR(WeatherStationsAtlasGenerator):
    def __init__(self):
        super(WeatherStationsAtlasGeneratorAR, self).__init__() if hasattr(super(WeatherStationsAtlasGeneratorAR, self), '__init__') else WeatherStationsAtlasGenerator.__init__(self)
        self.label = "MIRSAD: Ground Weather Stations Climate Atlas Generator (AR)"
        self.description = (
            "أداة مِرصاد الجغرافية لاستخلاص محطات الأرصاد الجوية السطحية المعتمدة عالمياً (NOAA ISD & WMO)، "
            "وتنزيل السلاسل الزمنية المناخية من وكالة ناسا (NASA POWER) أو المركز الأوروبي (Open-Meteo ERA5) أو الأرصاد المباشرة، "
            "وحساب المعدلات المناخية والمؤشرات الحيوية، وبناء قواعد البيانات الجغرافية وجداول إكسل، وإنتاج أسطح الراستر المستمرة فائقة الدقة."
        )
        self.canRunInBackground = True

    def getParameterInfo(self):
        params = WeatherStationsAtlasGenerator.getParameterInfo(self)
        pdict = dict((p.name, p) for p in params)

        # 1. Station_Selection_Mode
        p_mode = pdict.get("Station_Selection_Mode")
        if p_mode:
            p_mode.displayName = "نمط اختيار محطات الأرصاد الجوية"
            p_mode.filter.list = [
                "اختيار بالدولة (الشبكة الوطنية المعتمدة)",
                "استقطاع مكاني بمضلع حدود منطقة الدراسة",
                "أكواد محطات مخصصة (إدخال يدوي / من المستكشف)",
                "الشبكة العالمية الموحدة (حول العالم - تنبيه: عدد كبير)",
                "طبقة محطات محلية محفوظة (شيب فايل / قاعدة بيانات)"
            ]
            p_mode.value = "اختيار بالدولة (الشبكة الوطنية المعتمدة)"
            p_mode.description = (
                "اختر طريقة تحديد محطات الرصد الجوي:\n"
                "• 'اختيار بالدولة (الشبكة الوطنية)': تصفية المحطات المعتمدة حسب الدولة أو الإقليم.\n"
                "• 'استقطاع مكاني بمضلع الحدود': اقتطاع المحطات الواقعة داخل مضلع دراستك (+ نطاق عازل اختياري).\n"
                "• 'أكواد محطات مخصصة': إدخال أكواد USAF/WMO لمحطات محددة مباشرة.\n"
                "• 'الشبكة العالمية الموحدة': معالجة المحطات حول العالم.\n"
                "• 'طبقة محطات محلية محفوظة': استدعاء طبقة محطات محفوظة مسبقاً من جهازك."
            )

        # 2. Region_Filter
        p_reg = pdict.get("Region_Filter")
        if p_reg:
            p_reg.displayName = "نطاق الإقليم الجغرافي / القارة"
            p_reg.filter.list = [
                "دول الوطن العربي (22 دولة)",
                "جميع دول العالم (قاعدة البيانات المفتوحة)",
                "أفريقيا",
                "آسيا",
                "أوروبا",
                "أمريكا الشمالية",
                "أمريكا الجنوبية",
                "أوقيانوسيا",
                "القارة القطبية الجنوبية"
            ]
            p_reg.value = "دول الوطن العربي (22 دولة)"
            p_reg.description = "مرشح مكاني للمستوى الأول لتضييق نطاق قائمة الدول."

        # 3. Select_Country
        p_ctry = pdict.get("Select_Country")
        if p_ctry:
            p_ctry.displayName = "اختيار الدولة / النطاق الوطني"
            p_ctry.filter.list = [
                "[جميع دول الوطن العربي (ARAB)]",
                "فلسطين (PS)",
                "مصر (EG)",
                "المملكة العربية السعودية (SA)",
                "الجزائر (AG)",
                "المغرب (MO)",
                "العراق (IZ)",
                "السودان (SU)",
                "سلطنة عُمان (MU)",
                "ليبيا (LY)",
                "تونس (TS)",
                "الكويت (KU)",
                "سوريا (SY)",
                "الصومال (SO)",
                "الأردن (JO)",
                "الإمارات العربية المتحدة (AE)",
                "قطر (QA)",
                "اليمن (YM)",
                "موريتانيا (MR)",
                "جزر القمر (CN)",
                "البحرين (BA)",
                "لبنان (LE)",
                "جيبوتي (DJ)"
            ]
            p_ctry.value = "[جميع دول الوطن العربي (ARAB)]"
            p_ctry.description = "مرشح الشبكة الوطنية للمستوى الثاني أو النطاق الإقليمي الشامل."

        # 4. Study_Area_Polygon
        p_poly = pdict.get("Study_Area_Polygon")
        if p_poly:
            p_poly.displayName = "مضلع حدود منطقة الدراسة (قناع / استقطاع اختياري)"
            p_poly.description = "طبقة مضلعات اختيارية. تُستخدم لقص محطات الأرصاد وتحديد قناع الامتداد وقص أسطح الراستر النهائية."

        # 5. Supplementary_Points
        p_supp = pdict.get("Supplementary_Points")
        if p_supp:
            p_supp.displayName = "نقاط رفع إضافية داعمة (اختيارية - لتكثيف المناطق الفارغة)"
            p_supp.description = "طبقة نقاط اختيارية (شيب فايل أو قاعدة بيانات). تُستخدم لإضافة مواقع رفع خاصة (مثل المناطق الصحراوية أو مواقع المشاريع الخالية من المحطات) لدمجها تلقائياً مع محطات الأرصاد ورفع دقة الاستيفاء."

        # 6. Include_Buffer_Stations
        p_buf = pdict.get("Include_Buffer_Stations")
        if p_buf:
            p_buf.displayName = "تضمين محطات النطاق العازل المجاورة (حرم 30 كم لدقة الاستيفاء)"
            p_buf.description = "عند تفعيل القص بالمضلع، يتم تضمين المحطات الواقعة ضمن مسافة 30 كم خارج الحدود لمنع تشوه الحواف أثناء الاستيفاء المكاني."

        # 7. Custom_Station_IDs
        p_cust = pdict.get("Custom_Station_IDs")
        if p_cust:
            p_cust.displayName = "أكواد المحطات المخصصة (أكواد USAF مفصولة بفاصلة منقوطة)"
            p_cust.description = "اختياري. أدخل أكواد محطات USAF مفصولة بفاصلة منقوطة (مثال: 623660;624140;623180)."

        # 8. Local_Station_Features
        p_loc = pdict.get("Local_Station_Features")
        if p_loc:
            p_loc.displayName = "طبقة محطات محلية محفوظة (شيب فايل أو فيتشر كلاس)"
            p_loc.description = "اختياري. استدعاء طبقة محطات محفوظة مسبقاً بصيغة Shapefile أو File Geodatabase."

        # 9. Climate_Data_Source
        p_csrc = pdict.get("Climate_Data_Source")
        if p_csrc:
            p_csrc.displayName = "مصدر البيانات المناخية ومحرك المعالجة"
            p_csrc.filter.list = [
                "نظام هجين: أرصاد محطات NOAA + سد فجوات NASA/ERA5 (Hybrid) [موصى به]",
                "أرشيف الأرصاد السطحية المباشرة من محطات NOAA ISD / GHCN",
                "واجهة ناسا باور المناخية الزراعية (NASA POWER API / MERRA-2)",
                "واجهة أوبن-ميتيو لبيانات ERA5 عالية الدقة (Open-Meteo ERA5 Reanalysis)"
            ]
            p_csrc.value = "نظام هجين: أرصاد محطات NOAA + سد فجوات NASA/ERA5 (Hybrid) [موصى به]"
            p_csrc.description = "اختر مزود البيانات المناخية لمحطات الرصد الجوي."

        # 10. Operation_Mode
        p_op = pdict.get("Operation_Mode")
        if p_op:
            p_op.displayName = "نمط سير العمل والتشغيل"
            p_op.filter.list = [
                "تنزيل البيانات وإنتاج الأطلس كاملاً (المسار الشامل) [الافتراضي]",
                "استيفاء ورسم الخرائط لبيانات موجودة مسبقاً (وضع أوفلاين)"
            ]
            p_op.value = "تنزيل البيانات وإنتاج الأطلس كاملاً (المسار الشامل) [الافتراضي]"

        # 11. Execution_Workflow_Mode
        p_wf = pdict.get("Execution_Workflow_Mode")
        if p_wf:
            p_wf.displayName = "نمط تنفيذ المعالجة وتدفق المهام"
            p_wf.filter.list = [
                "نمط الدفعات: تنزيل كافة البيانات أولاً ثم المعالجة [موصى به]",
                "نمط تتابعي: معالجة عنصر بعنصر"
            ]
            p_wf.value = "نمط الدفعات: تنزيل كافة البيانات أولاً ثم المعالجة [موصى به]"

        # 12. Download_Only
        p_dl = pdict.get("Download_Only")
        if p_dl:
            p_dl.displayName = "تنزيل وحفظ بيانات النقاط فقط (تخطي الراسترات والأطلس)"

        # 13. Study_Area_Name
        p_sname = pdict.get("Study_Area_Name")
        if p_sname:
            p_sname.displayName = "اسم منطقة الدراسة (اختياري - لتسمية الطبقات)"

        # 14. Output_Workspace
        p_ows = pdict.get("Output_Workspace")
        if p_ows:
            p_ows.displayName = "مجلد مساحة عمل المخرجات الرئيسي"

        # 15. Output_Spatial_Reference
        p_osr = pdict.get("Output_Spatial_Reference")
        if p_osr:
            p_osr.displayName = "نظام الإسناد المكاني للمخرجات (Spatial Reference)"

        # 16. Units
        p_unit = pdict.get("Measurement_Units_System")
        if p_unit:
            p_unit.displayName = "نظام وحدات القياس (متري Metric / إمبراطوري Imperial)"

        # 17. Interpolation_Method
        p_interp = pdict.get("Interpolation_Method")
        if p_interp:
            p_interp.displayName = "طريقة الاستيفاء المكاني للراستر"

        # 18. Base_Cell_Size
        p_bcell = pdict.get("Base_Cell_Size")
        if p_bcell:
            p_bcell.displayName = "حجم الخلية الأساسي لأسطح الراستر (بالأمتار)"

        return params

    def updateParameters(self, parameters):
        pdict = dict((p.name, p) for p in parameters)

        st_mode = pdict.get("Station_Selection_Mode")
        mode_val = st_mode.valueAsText if st_mode else ""

        p_reg = pdict.get("Region_Filter")
        p_ctry = pdict.get("Select_Country")
        p_custom = pdict.get("Custom_Station_IDs")
        p_local = pdict.get("Local_Station_Features")
        p_buf = pdict.get("Include_Buffer_Stations")

        if "الدولة" in mode_val or "Country" in mode_val:
            if p_reg: p_reg.enabled = True
            if p_ctry: p_ctry.enabled = True
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = False
        elif "استقطاع" in mode_val or "Intersect" in mode_val:
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = True
        elif "أكواد" in mode_val or "Custom" in mode_val:
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = True
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = False
        elif "محلية" in mode_val or "Local" in mode_val:
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = True
            if p_buf: p_buf.enabled = False
        elif "العالمية" in mode_val or "Global" in mode_val:
            if p_reg: p_reg.enabled = False
            if p_ctry: p_ctry.enabled = False
            if p_custom: p_custom.enabled = False
            if p_local: p_local.enabled = False
            if p_buf: p_buf.enabled = False

        # Populate countries in Arabic
        if p_reg and p_ctry:
            reg_val = p_reg.valueAsText or ""
            if "العربي" in reg_val or "Arab" in reg_val:
                p_ctry.filter.list = [
                    "[جميع دول الوطن العربي (ARAB)]",
                    "فلسطين (PS)", "مصر (EG)", "المملكة العربية السعودية (SA)", "الجزائر (AG)", "المغرب (MO)",
                    "العراق (IZ)", "السودان (SU)", "سلطنة عُمان (MU)", "ليبيا (LY)", "تونس (TS)",
                    "الكويت (KU)", "سوريا (SY)", "الصومال (SO)", "الأردن (JO)",
                    "الإمارات العربية المتحدة (AE)", "قطر (QA)", "اليمن (YM)",
                    "موريتانيا (MR)", "جزر القمر (CN)", "البحرين (BA)",
                    "لبنان (LE)", "جيبوتي (DJ)"
                ]
                if not p_ctry.valueAsText or p_ctry.valueAsText not in p_ctry.filter.list:
                    p_ctry.value = "[جميع دول الوطن العربي (ARAB)]"

        _core.PowerClimateAtlasGenerator.updateParameters(self, parameters)

    def execute(self, parameters, messages):
        # Delegate execution directly to master engine without mutating any host parameters
        WeatherStationsAtlasGenerator.execute(self, parameters, messages)
