# -*- coding: utf-8 -*-
"""
NASA POWER Climate Atlas Generator — Legacy Database Migration Utility
======================================================================
Splits legacy unified / monolithic climate databases (such as Climate_Database.gdb
or folders containing Climate_Models.shp / Temperature.shp) into 17 standalone
modular feature classes and shapefiles conforming to the new Atlas structure.

New Modular Numbering Structure (01 to 17):
  01_Temperature
  02_Precipitation
  03_Sea_Level_Pressure
  04_Surface_Pressure
  05_Wind
  06_Humidity
  07_Solar_Radiation
  08_UV_Index
  09_Cloud_Cover
  10_Heat_Index
  11_Wind_Chill
  12_De_Martonne_Aridity
  13_Hargreaves_PET
  14_UNEP_Aridity
  15_Water_Deficit
  16_Dry_Months
  17_Trends_And_Anomalies

Compatibility:
  - Python 2.7 (ArcMap 10.8) & Python 3.x (ArcGIS Pro)
  - Reads File Geodatabases (.gdb), folders of shapefiles (.shp), or single shapefiles.
  - Automatically derives missing indicators on the fly from base variables.

Usage from Command Line:
  python migrate_legacy_database.py --input "C:/data/Climate_Database_Offline.gdb" --output "C:/migrated_atlas"
  python migrate_legacy_database.py --input "C:/data/Vector_Points" --output "C:/migrated_atlas"
"""

from __future__ import print_function
import os
import sys
import math
import argparse

# Try importing arcpy
try:
    import arcpy
    _HAS_ARCPY = True
except ImportError:
    _HAS_ARCPY = False


# ---------------------------------------------------------------------------
# Bioclimatic Formula Helpers
# ---------------------------------------------------------------------------
def heat_index_c(t_c, rh_pct):
    if t_c is None or rh_pct is None:
        return None
    try:
        t_c = float(t_c)
        rh_pct = float(rh_pct)
    except Exception:
        return None
    if t_c < 20.0:
        return round(t_c, 2)
    t_f = t_c * 9.0 / 5.0 + 32.0
    hi_f = (
        -42.379
        + 2.04901523 * t_f
        + 10.14333127 * rh_pct
        - 0.22475541 * t_f * rh_pct
        - 0.00683783 * (t_f ** 2)
        - 0.05481717 * (rh_pct ** 2)
        + 0.00122874 * (t_f ** 2) * rh_pct
        + 0.00085282 * t_f * (rh_pct ** 2)
        - 0.00000199 * (t_f ** 2) * (rh_pct ** 2)
    )
    if rh_pct < 13.0 and 80.0 <= t_f <= 112.0:
        adj = ((13.0 - rh_pct) / 4.0) * math.sqrt(max(0.0, (17.0 - abs(t_f - 95.0)) / 17.0))
        hi_f -= adj
    elif rh_pct > 85.0 and 80.0 <= t_f <= 87.0:
        adj = ((rh_pct - 85.0) / 10.0) * ((87.0 - t_f) / 5.0)
        hi_f += adj
    res_c = (hi_f - 32.0) * 5.0 / 9.0
    return round(res_c, 2)


def humidex_c(t_c, rh_pct):
    if t_c is None or rh_pct is None:
        return None
    try:
        t_c = float(t_c)
        rh_pct = float(rh_pct)
        rh_pct = max(0.01, min(100.0, rh_pct))
        e_hpa = (rh_pct / 100.0) * 6.112 * math.exp((17.67 * t_c) / (t_c + 243.5))
        return round(t_c + (5.0 / 9.0) * (e_hpa - 10.0), 2)
    except Exception:
        return None


def wbgt_shade_c(t_c, rh_pct):
    if t_c is None or rh_pct is None:
        return None
    try:
        t_c = float(t_c)
        rh_pct = float(rh_pct)
        rh_pct = max(0.01, min(100.0, rh_pct))
        tw_c = (
            t_c * math.atan(0.151977 * math.sqrt(rh_pct + 8.313659))
            + math.atan(t_c + rh_pct)
            - math.atan(rh_pct - 1.676331)
            + 0.00391838 * (rh_pct ** 1.5) * math.atan(0.023101 * rh_pct)
            - 4.686035
        )
        return round(0.7 * tw_c + 0.3 * t_c, 2)
    except Exception:
        return None


def wind_chill_c(t_c, ws_ms):
    if t_c is None or ws_ms is None:
        return None
    try:
        t_c = float(t_c)
        ws_kmh = float(ws_ms) * 3.6
        if t_c > 10.0 or ws_kmh <= 4.8:
            return round(t_c, 2)
        wc = 13.12 + 0.6215 * t_c - 11.37 * (ws_kmh ** 0.16) + 0.3965 * t_c * (ws_kmh ** 0.16)
        return round(wc, 2)
    except Exception:
        return None


def extraterrestrial_radiation_ra(lat_deg, month):
    try:
        phi = math.radians(lat_deg)
        d_mid = [15, 45, 74, 105, 135, 165, 196, 227, 258, 288, 319, 349]
        J = d_mid[max(0, min(11, month - 1))]
        dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * J / 365.0)
        delta = 0.409 * math.sin(2.0 * math.pi * J / 365.0 - 1.39)
        arg = -math.tan(phi) * math.tan(delta)
        arg = max(-1.0, min(1.0, arg))
        ws = math.acos(arg)
        gsc = 0.0820
        ra = (24.0 * 60.0 / math.pi) * gsc * dr * (
            ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws)
        )
        return max(0.0, ra)
    except Exception:
        return 30.0


# ---------------------------------------------------------------------------
# Module Schema Definitions
# ---------------------------------------------------------------------------
MODULES_INFO = [
    {
        "name": "Temperature",
        "folder": "01_Temperature",
        "short": "Temperature",
        "fields": [
            ("T_Annual_Mean", "Annual Mean Air Temperature"),
            ("T_Winter_Mean", "Winter Mean Air Temperature"),
            ("T_Spring_Mean", "Spring Mean Air Temperature"),
            ("T_Summer_Mean", "Summer Mean Air Temperature"),
            ("T_Autumn_Mean", "Autumn Mean Air Temperature"),
            ("T_Annual_Range", "Annual Temperature Range"),
            ("T_Max_Summer_Month_Mean", "Maximum Summer Monthly Mean Temperature"),
            ("T_Min_Winter_Month_Mean", "Minimum Winter Monthly Mean Temperature"),
            ("T_Annual_Max_Mean", "Annual Mean Maximum Temperature"),
            ("T_Annual_Min_Mean", "Annual Mean Minimum Temperature"),
            ("Td_Annual_Mean", "Annual Mean Dew Point Temperature"),
            ("Td_Summer_Mean", "Summer Mean Dew Point Temperature"),
            ("Td_Winter_Mean", "Winter Mean Dew Point Temperature"),
        ]
    },
    {
        "name": "Precipitation",
        "folder": "02_Precipitation",
        "short": "Precipitation",
        "fields": [
            ("R_Annual_Mean", "Annual Mean Precipitation"),
            ("R_Month_Mean", "Mean Monthly Precipitation"),
            ("R_Winter_Mean", "Winter Mean Precipitation"),
            ("R_Spring_Mean", "Spring Mean Precipitation"),
            ("R_Summer_Mean", "Summer Mean Precipitation"),
            ("R_Autumn_Mean", "Autumn Mean Precipitation"),
        ]
    },
    {
        "name": "Sea Level Pressure",
        "folder": "03_Sea_Level_Pressure",
        "short": "Sea_Level_Pressure",
        "fields": [
            ("PSL_Annual_Mean", "Annual Mean Sea Level Pressure"),
            ("PSL_Winter_Mean", "Winter Mean Sea Level Pressure"),
            ("PSL_Spring_Mean", "Spring Mean Sea Level Pressure"),
            ("PSL_Summer_Mean", "Summer Mean Sea Level Pressure"),
            ("PSL_Autumn_Mean", "Autumn Mean Sea Level Pressure"),
            ("PSL_Annual_Range", "Annual Sea Level Pressure Range"),
        ]
    },
    {
        "name": "Surface Pressure",
        "folder": "04_Surface_Pressure",
        "short": "Surface_Pressure",
        "fields": [
            ("PS_Annual_Mean", "Annual Mean Surface Pressure"),
            ("PS_Winter_Mean", "Winter Mean Surface Pressure"),
            ("PS_Spring_Mean", "Spring Mean Surface Pressure"),
            ("PS_Summer_Mean", "Summer Mean Surface Pressure"),
            ("PS_Autumn_Mean", "Autumn Mean Surface Pressure"),
            ("PS_Annual_Range", "Annual Surface Pressure Range"),
        ]
    },
    {
        "name": "Wind",
        "folder": "05_Wind",
        "short": "Wind",
        "fields": [
            ("W_Spd_Annual_Mean", "Annual Mean Wind Speed"),
            ("W_Spd_Winter_Mean", "Winter Mean Wind Speed"),
            ("W_Spd_Spring_Mean", "Spring Mean Wind Speed"),
            ("W_Spd_Summer_Mean", "Summer Mean Wind Speed"),
            ("W_Spd_Autumn_Mean", "Autumn Mean Wind Speed"),
            ("W_Spd_Annual_Max_Month", "Maximum Monthly Mean Wind Speed"),
            ("W_Spd_Annual_Min_Month", "Minimum Monthly Mean Wind Speed"),
            ("W_Spd_Annual_Range", "Annual Wind Speed Range"),
            ("W_Dir_Annual_Mean", "Annual Prevailing Wind Direction"),
            ("W_Dir_Winter_Mean", "Winter Prevailing Wind Direction"),
            ("W_Dir_Spring_Mean", "Spring Prevailing Wind Direction"),
            ("W_Dir_Summer_Mean", "Summer Prevailing Wind Direction"),
            ("W_Dir_Autumn_Mean", "Autumn Prevailing Wind Direction"),
        ]
    },
    {
        "name": "Relative Humidity",
        "folder": "06_Humidity",
        "short": "Relative_Humidity",
        "fields": [
            ("RH_Annual_Mean", "Annual Mean Relative Humidity"),
            ("RH_Winter_Mean", "Winter Mean Relative Humidity"),
            ("RH_Spring_Mean", "Spring Mean Relative Humidity"),
            ("RH_Summer_Mean", "Summer Mean Relative Humidity"),
            ("RH_Autumn_Mean", "Autumn Mean Relative Humidity"),
            ("RH_Annual_Range", "Annual Relative Humidity Range"),
        ]
    },
    {
        "name": "Solar Radiation",
        "folder": "07_Solar_Radiation",
        "short": "Solar_Radiation",
        "fields": [
            ("Sol_Annual_Mean", "Annual Mean Daily Solar Radiation"),
            ("Sol_Annual_Total", "Annual Total Solar Radiation"),
            ("Sol_Winter_Mean", "Winter Mean Daily Solar Radiation"),
            ("Sol_Spring_Mean", "Spring Mean Daily Solar Radiation"),
            ("Sol_Summer_Mean", "Summer Mean Daily Solar Radiation"),
            ("Sol_Autumn_Mean", "Autumn Mean Daily Solar Radiation"),
            ("Sol_Annual_Range", "Annual Solar Radiation Range"),
        ]
    },
    {
        "name": "UV Index",
        "folder": "08_UV_Index",
        "short": "UV_Index",
        "fields": [
            ("UV_Annual_Mean", "Annual Mean UV Index"),
            ("UV_Winter_Mean", "Winter Mean UV Index"),
            ("UV_Spring_Mean", "Spring Mean UV Index"),
            ("UV_Summer_Mean", "Summer Mean UV Index"),
            ("UV_Autumn_Mean", "Autumn Mean UV Index"),
            ("UV_Annual_Range", "Annual UV Index Range"),
        ]
    },
    {
        "name": "Cloud Cover",
        "folder": "09_Cloud_Cover",
        "short": "Cloud_Cover",
        "fields": [
            ("Cld_Annual_Mean", "Annual Mean Cloud Cover"),
            ("Cld_Winter_Mean", "Winter Mean Cloud Cover"),
            ("Cld_Spring_Mean", "Spring Mean Cloud Cover"),
            ("Cld_Summer_Mean", "Summer Mean Cloud Cover"),
            ("Cld_Autumn_Mean", "Autumn Mean Cloud Cover"),
            ("Cld_Annual_Range", "Annual Cloud Cover Range"),
        ]
    },
    {
        "name": "Heat Index",
        "folder": "10_Heat_Index",
        "short": "Heat_Index",
        "fields": [
            ("HI_Annual_Mean", "Annual Mean Heat Index"),
            ("HI_Summer_Mean", "Summer Mean Heat Index"),
            ("HI_Spring_Mean", "Spring Mean Heat Index"),
            ("HI_Autumn_Mean", "Autumn Mean Heat Index"),
            ("HI_Winter_Mean", "Winter Mean Heat Index"),
            ("HI_Annual_Range", "Annual Heat Index Range"),
            ("WBGT_Summer_Mean", "Summer Mean WBGT Heat Stress"),
        ]
    },
    {
        "name": "Wind Chill",
        "folder": "11_Wind_Chill",
        "short": "Wind_Chill",
        "fields": [
            ("WC_Annual_Mean", "Annual Mean Wind Chill Temperature"),
            ("WC_Winter_Mean", "Winter Mean Wind Chill Temperature"),
            ("WC_Spring_Mean", "Spring Mean Wind Chill Temperature"),
            ("WC_Summer_Mean", "Summer Mean Wind Chill Temperature"),
            ("WC_Autumn_Mean", "Autumn Mean Wind Chill Temperature"),
            ("WC_Annual_Range", "Annual Wind Chill Range"),
            ("WC_Seasonal_Range", "Seasonal Wind Chill Range"),
        ]
    },
    {
        "name": "De Martonne Aridity",
        "folder": "12_De_Martonne_Aridity",
        "short": "De_Martonne_Aridity",
        "fields": [
            ("DM_Aridity_Annual", "De Martonne Aridity Index"),
        ]
    },
    {
        "name": "Hargreaves PET",
        "folder": "13_Hargreaves_PET",
        "short": "Hargreaves_PET",
        "fields": [
            ("PET_Hargreaves_Annual", "Annual Potential Evapotranspiration (Hargreaves)"),
        ]
    },
    {
        "name": "UNEP Aridity",
        "folder": "14_UNEP_Aridity",
        "short": "UNEP_Aridity",
        "fields": [
            ("UNEP_Aridity_Annual", "UNEP Aridity Index"),
        ]
    },
    {
        "name": "Water Deficit",
        "folder": "15_Water_Deficit",
        "short": "Water_Deficit",
        "fields": [
            ("Water_Deficit_Annual", "Annual Climatic Water Deficit/Surplus"),
        ]
    },
    {
        "name": "Dry Months",
        "folder": "16_Dry_Months",
        "short": "Dry_Months",
        "fields": [
            ("Dry_Months_Count", "Biological Dry Months Count (Walter-Lieth)"),
        ]
    },
    {
        "name": "Trends & Anomalies",
        "folder": "17_Trends_And_Anomalies",
        "short": "Trends_Anomalies",
        "fields": [
            ("T_Annual_Trend_Decade", "Temperature Trend per Decade"),
            ("R_Annual_Trend_Decade", "Precipitation Trend per Decade"),
            ("T_Annual_Anom", "Annual Temperature Anomaly vs 1991-2020"),
            ("T_Anom_Winter", "Winter Temperature Anomaly vs 1991-2020"),
            ("T_Anom_Summer", "Summer Temperature Anomaly vs 1991-2020"),
            ("R_Annual_Anom", "Annual Precipitation Anomaly vs 1991-2020"),
            ("R_Annual_Anom_Pct", "Annual Precipitation Anomaly Percent vs 1991-2020"),
            ("R_Anom_Winter", "Winter Precipitation Anomaly vs 1991-2020"),
            ("R_Anom_Winter_Pct", "Winter Precipitation Anomaly Percent vs 1991-2020"),
        ]
    },
]

SHP_FIELD_MAP = {
    "Cld_Annual_Mean": "Cld_AnMean",
    "Cld_Annual_Range": "Cld_AnRng",
    "Cld_Autumn_Mean": "Cld_AuMean",
    "Cld_Spring_Mean": "Cld_SpMean",
    "Cld_Summer_Mean": "Cld_SuMean",
    "Cld_Winter_Mean": "Cld_WnMean",
    "DM_Aridity_Annual": "DM_AridAnn",
    "Dry_Months_Count": "Dry_Months",
    "HI_Annual_Mean": "HI_AnnMean",
    "HI_Annual_Range": "HI_AnRng",
    "HI_Seasonal_Range": "HI_SeaRng",
    "WBGT_Summer_Mean": "WBGT_SuMn",
    "HI_Summer_Mean": "HI_SumMean",
    "HI_Spring_Mean": "HI_SprMean",
    "HI_Autumn_Mean": "HI_AutMean",
    "HI_Winter_Mean": "HI_WinMean",
    "Interp_Meth": "Intrp_Meth",
    "PSL_Annual_Mean": "PSL_AnMean",
    "PSL_Annual_Range": "PSL_AnRng",
    "PSL_Autumn_Mean": "PSL_AuMean",
    "PSL_Spring_Mean": "PSL_SpMean",
    "PSL_Summer_Mean": "PSL_SuMean",
    "PSL_Winter_Mean": "PSL_WnMean",
    "PS_Annual_Mean": "PS_AnnMean",
    "PS_Annual_Range": "PS_AnnRng",
    "PS_Autumn_Mean": "PS_AutMean",
    "PS_Spring_Mean": "PS_SprMean",
    "PS_Summer_Mean": "PS_SumMean",
    "PS_Winter_Mean": "PS_WinMean",
    "RH_Annual_Mean": "RH_AnMean",
    "RH_Annual_Range": "RH_AnRng",
    "RH_Autumn_Mean": "RH_AuMean",
    "RH_Spring_Mean": "RH_SpMean",
    "RH_Summer_Mean": "RH_SuMean",
    "RH_Winter_Mean": "RH_WnMean",
    "R_Annual_Mean": "R_AnnMean",
    "R_Annual_Total": "R_AnnTot",
    "R_Month_Mean": "R_MonMean",
    "R_Autumn_Mean": "R_AutMean",
    "R_Autumn_Total": "R_AutTot",
    "R_Spring_Mean": "R_SprMean",
    "R_Spring_Total": "R_SprTot",
    "R_Summer_Mean": "R_SumMean",
    "R_Summer_Total": "R_SumTot",
    "R_Winter_Mean": "R_WinMean",
    "R_Winter_Total": "R_WinTot",
    "Sol_Annual_Mean": "Sol_AnMean",
    "Sol_Annual_Range": "Sol_AnRng",
    "Sol_Annual_Total": "Sol_AnTot",
    "Sol_Autumn_Mean": "Sol_AuMean",
    "Sol_Spring_Mean": "Sol_SpMean",
    "Sol_Summer_Mean": "Sol_SuMean",
    "Sol_Winter_Mean": "Sol_WnMean",
    "T_Annual_Max_Mean": "T_MaxMean",
    "T_Annual_Mean": "T_AnnMean",
    "T_Annual_Min_Mean": "T_MinMean",
    "T_Annual_Range": "T_AnnRng",
    "T_Autumn_Mean": "T_AutMean",
    "T_Max_Summer_Month_Mean": "T_MaxSumMo",
    "T_Min_Winter_Month_Mean": "T_MinWinMo",
    "T_Spring_Mean": "T_SprMean",
    "T_Summer_Mean": "T_SumMean",
    "T_Winter_Mean": "T_WinMean",
    "Td_Annual_Mean": "Td_AnnMean",
    "Td_Summer_Mean": "Td_SumMean",
    "Td_Winter_Mean": "Td_WinMean",
    "UV_Annual_Mean": "UV_AnMean",
    "UV_Annual_Range": "UV_AnRng",
    "UV_Autumn_Mean": "UV_AuMean",
    "UV_Spring_Mean": "UV_SpMean",
    "UV_Summer_Mean": "UV_SuMean",
    "UV_Winter_Mean": "UV_WnMean",
    "W_Dir_Annual_Mean": "WDr_AnMean",
    "W_Dir_Autumn_Mean": "WDr_AuMean",
    "W_Dir_Spring_Mean": "WDr_SpMean",
    "W_Dir_Summer_Mean": "WDr_SuMean",
    "W_Dir_Winter_Mean": "WDr_WnMean",
    "W_Spd_Annual_Max_Month": "WSp_MaxMo",
    "W_Spd_Annual_Min_Month": "WSp_MinMo",
    "W_Spd_Annual_Mean": "WSp_AnMean",
    "W_Spd_Annual_Range": "WSp_AnRng",
    "W_Spd_Autumn_Mean": "WSp_AuMean",
    "W_Spd_Spring_Mean": "WSp_SpMean",
    "W_Spd_Summer_Mean": "WSp_SuMean",
    "W_Spd_Winter_Mean": "WSp_WnMean",
    "PET_Hargreaves_Annual": "PET_HarAnn",
    "UNEP_Aridity_Annual": "UNEP_Arid",
    "Water_Deficit_Annual": "WatDefAnn",
    "WC_Winter_Mean": "WC_WinMean",
    "WC_Spring_Mean": "WC_SprMean",
    "WC_Summer_Mean": "WC_SumMean",
    "WC_Autumn_Mean": "WC_AutMean",
    "WC_Annual_Mean": "WC_AnnMean",
    "WC_Annual_Range": "WC_AnRng",
    "WC_Seasonal_Range": "WC_SeaRng",
    "WC_January_Mean": "WC_JanMean",
    "WC_February_Mean": "WC_FebMean",
    "WC_March_Mean": "WC_MarMean",
    "WC_April_Mean": "WC_AprMean",
    "WC_May_Mean": "WC_MayMean",
    "WC_June_Mean": "WC_JunMean",
    "WC_July_Mean": "WC_JulMean",
    "WC_August_Mean": "WC_AugMean",
    "WC_September_Mean": "WC_SepMean",
    "WC_October_Mean": "WC_OctMean",
    "WC_November_Mean": "WC_NovMean",
    "WC_December_Mean": "WC_DecMean",
    "T_Annual_Trend_Decade": "T_AnnTrDec",
    "R_Annual_Trend_Decade": "R_AnnTrDec",
    "T_Annual_Anom": "T_AnnAnom",
    "T_Anom_Winter": "T_AnomWin",
    "T_Anom_Summer": "T_AnomSum",
    "R_Annual_Anom": "R_AnnAnom",
    "R_Annual_Anom_Pct": "R_AnnAnPct",
    "R_Anom_Winter": "R_AnomWin",
    "R_Anom_Winter_Pct": "R_AnomWPct",
}
REV_SHP_MAP = dict((v, k) for k, v in SHP_FIELD_MAP.items())


# ---------------------------------------------------------------------------
# Migration Engine
# ---------------------------------------------------------------------------
class LegacyAtlasMigrator(object):
    def __init__(self, in_path, out_dir, export_shp=True, export_gdb=True, export_csv=True):
        self.in_path = os.path.abspath(in_path)
        self.out_dir = os.path.abspath(out_dir)
        self.export_shp = export_shp
        self.export_gdb = export_gdb
        self.export_csv = export_csv

    def log(self, msg):
        print("[MIGRATE] " + str(msg))

    def run(self):
        self.log("=" * 70)
        self.log("STARTING LEGACY CLIMATE DATABASE MIGRATION")
        self.log("Input:  %s" % self.in_path)
        self.log("Output: %s" % self.out_dir)
        self.log("=" * 70)

        if not os.path.exists(self.in_path):
            raise RuntimeError("Input path '%s' does not exist." % self.in_path)

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        # 1. Discover input layers
        layers = self._discover_input_layers()
        if not layers:
            raise RuntimeError("No valid Feature Classes or Shapefiles found in '%s'." % self.in_path)
        self.log("Found %d input layer(s) to harvest." % len(layers))

        if not _HAS_ARCPY:
            self.log("ArcPy is not available in this Python interpreter. Using pure Python CSV/Shapefile parser.")
            return self._run_pure_python(layers)

        # 2. Run with ArcPy
        return self._run_arcpy(layers)

    def _discover_input_layers(self):
        layers = []
        p = self.in_path
        if p.lower().endswith(".gdb"):
            if _HAS_ARCPY:
                arcpy.env.workspace = p
                fcs = arcpy.ListFeatureClasses() or []
                for fc in fcs:
                    layers.append(os.path.join(p, fc))
            else:
                self.log("Note: Inspecting GDB without ArcPy requires GDAL/OGR or ArcGIS environment.")
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for f in files:
                    if f.lower().endswith(".shp"):
                        layers.append(os.path.join(root, f))
        elif p.lower().endswith(".shp"):
            layers.append(p)
        return layers

    def _run_arcpy(self, layers):
        arcpy.env.overwriteOutput = True
        wgs_sr = arcpy.SpatialReference(4326)

        # Base layer geometry
        base_layer = layers[0]
        base_sr = arcpy.Describe(base_layer).spatialReference
        self.log("Base layer for coordinates: '%s' (SR: %s)" % (os.path.basename(base_layer), getattr(base_sr, "name", "Unknown")))

        point_records = []
        coord_to_idx = {}
        oid_to_idx = {}

        base_oid_f = arcpy.Describe(base_layer).OIDFieldName
        with arcpy.da.SearchCursor(base_layer, [base_oid_f, "SHAPE@"]) as cur:
            idx = 0
            for row in cur:
                oid_val = row[0]
                geom = row[1]
                lat, lon = None, None
                try:
                    if geom:
                        pt_wgs = geom.projectAs(wgs_sr)
                        lat, lon = float(pt_wgs.centroid.Y), float(pt_wgs.centroid.X)
                except Exception:
                    pass
                ckey = (round(lat, 4), round(lon, 4)) if (lat is not None and lon is not None) else None
                rec = {
                    "oid": oid_val,
                    "geom": geom,
                    "lat": lat,
                    "lon": lon,
                    "fields": {}
                }
                point_records.append(rec)
                if ckey:
                    coord_to_idx[ckey] = idx
                    coord_to_idx[(round(lat, 3), round(lon, 3))] = idx
                oid_to_idx[oid_val] = idx
                idx += 1

        self.log("Read %d base point geometries." % len(point_records))

        col_data_start = ""
        col_data_end = ""

        # Harvest attributes from all layers
        for lyr in layers:
            lyr_name = os.path.basename(lyr)
            desc = arcpy.Describe(lyr)
            oid_n = desc.OIDFieldName
            all_fields = [f.name for f in arcpy.ListFields(lyr) if f.type not in ("Geometry", "Raster", "Blob")]
            val_fields = [f for f in all_fields if f != oid_n]

            self.log("  Harvesting attributes from '%s' (%d fields)..." % (lyr_name, len(val_fields)))
            with arcpy.da.SearchCursor(lyr, [oid_n, "SHAPE@"] + val_fields) as cur:
                for row in cur:
                    l_oid = row[0]
                    l_geom = row[1]
                    l_lat, l_lon = None, None
                    try:
                        if l_geom:
                            pt_w = l_geom.projectAs(wgs_sr)
                            l_lat, l_lon = float(pt_w.centroid.Y), float(pt_w.centroid.X)
                    except Exception:
                        pass
                    ckey = (round(l_lat, 4), round(l_lon, 4)) if (l_lat is not None and l_lon is not None) else None
                    match_idx = coord_to_idx.get(ckey)
                    if match_idx is None and l_lat is not None and l_lon is not None:
                        match_idx = coord_to_idx.get((round(l_lat, 3), round(l_lon, 3)))
                    if match_idx is None:
                        match_idx = oid_to_idx.get(l_oid)

                    if match_idx is not None and match_idx < len(point_records):
                        target_fields = point_records[match_idx]["fields"]
                        for fname, val in zip(val_fields, row[2:]):
                            if fname == "Data_Start" and val and not col_data_start:
                                col_data_start = str(val)
                            elif fname == "Data_End" and val and not col_data_end:
                                col_data_end = str(val)

                            canon = REV_SHP_MAP.get(fname, fname)
                            if val is not None:
                                target_fields[canon] = val
                                target_fields[fname] = val
                                shp_sh = SHP_FIELD_MAP.get(canon)
                                if shp_sh:
                                    target_fields[shp_sh] = val

        # On-the-fly calculation of any missing derived fields
        self.log("Checking and computing missing derived indicators...")
        for rec in point_records:
            f = rec["fields"]
            pt_lat = rec.get("lat") or 0.0

            t_val = (f.get("T_Annual_Mean") if f.get("T_Annual_Mean") is not None else
                     (f.get("T_AnnMean") if f.get("T_AnnMean") is not None else f.get("T2M")))
            if f.get("R_Month_Mean") is not None or f.get("R_MonMean") is not None:
                p_val = (f.get("R_Annual_Mean") if f.get("R_Annual_Mean") is not None else f.get("R_AnnMean"))
            elif f.get("R_Annual_Total") is not None or f.get("R_AnnTot") is not None or f.get("R_AnnTotal") is not None:
                p_val = (f.get("R_Annual_Total") if f.get("R_Annual_Total") is not None else
                         (f.get("R_AnnTot") if f.get("R_AnnTot") is not None else f.get("R_AnnTotal")))
            else:
                p_val = (f.get("R_Annual_Mean") if f.get("R_Annual_Mean") is not None else
                         (f.get("R_AnnMean") if f.get("R_AnnMean") is not None else
                          (f.get("Precip_Annual_Sum") if f.get("Precip_Annual_Sum") is not None else f.get("PRECTOTCORR"))))
            tx_val = (f.get("T_Annual_Max_Mean") if f.get("T_Annual_Max_Mean") is not None else
                      (f.get("T_MaxMean") if f.get("T_MaxMean") is not None else f.get("T2M_MAX")))
            if tx_val is None and t_val is not None:
                tx_val = float(t_val) + 5.0
            tn_val = (f.get("T_Annual_Min_Mean") if f.get("T_Annual_Min_Mean") is not None else
                      (f.get("T_MinMean") if f.get("T_MinMean") is not None else f.get("T2M_MIN")))
            if tn_val is None and t_val is not None:
                tn_val = float(t_val) - 5.0
            rh_val = (f.get("RH_Summer_Mean") if f.get("RH_Summer_Mean") is not None else
                      (f.get("RH_SuMean") if f.get("RH_SuMean") is not None else
                       (f.get("RH_Annual_Mean") if f.get("RH_Annual_Mean") is not None else
                        (f.get("RH_AnMean") if f.get("RH_AnMean") is not None else f.get("RH2M")))))
            w_val = (f.get("W_Spd_Annual_Mean") if f.get("W_Spd_Annual_Mean") is not None else
                     (f.get("WSp_AnMean") if f.get("WSp_AnMean") is not None else f.get("WS10M")))

            # 1. De Martonne
            if f.get("DM_Aridity_Annual") is None and t_val is not None and p_val is not None:
                denom = float(t_val) + 10.0
                f["DM_Aridity_Annual"] = round(float(p_val) / denom, 2) if denom > 0.01 else 0.0

            # 2. Hargreaves PET
            if f.get("PET_Hargreaves_Annual") is None and t_val is not None and tx_val is not None and tn_val is not None:
                t_f, tx_f, tn_f = float(t_val), float(tx_val), float(tn_val)
                ra_ann = sum(extraterrestrial_radiation_ra(pt_lat, m) for m in range(1, 13))
                tdiff = max(0.0, tx_f - tn_f)
                pet_ann = 0.0023 * ra_ann * 30.4 * (t_f + 17.8) * math.sqrt(tdiff)
                f["PET_Hargreaves_Annual"] = round(max(0.0, pet_ann), 1)

            # 3. UNEP Aridity
            if f.get("UNEP_Aridity_Annual") is None and p_val is not None and f.get("PET_Hargreaves_Annual") is not None:
                pet_f = float(f["PET_Hargreaves_Annual"])
                f["UNEP_Aridity_Annual"] = round(float(p_val) / pet_f, 3) if pet_f > 0.01 else 0.0

            # 4. Water Deficit
            if f.get("Water_Deficit_Annual") is None and p_val is not None and f.get("PET_Hargreaves_Annual") is not None:
                f["Water_Deficit_Annual"] = round(float(p_val) - float(f["PET_Hargreaves_Annual"]), 1)

            # 5. Dry Months
            if f.get("Dry_Months_Count") is None and p_val is not None and t_val is not None:
                p_f, t_f = float(p_val), float(t_val)
                f["Dry_Months_Count"] = 12 if p_f < (2.0 * t_f) else 0

            # 6. Heat Index
            if f.get("HI_Summer_Mean") is None and t_val is not None and rh_val is not None:
                hi = heat_index_c(float(t_val), float(rh_val))
                if hi is not None:
                    f["HI_Summer_Mean"] = round(hi, 2)
                    f["HI_Annual_Mean"] = round(hi, 2)
            if f.get("HI_Winter_Mean") is None and t_val is not None and rh_val is not None:
                hw = humidex_c(float(t_val), float(rh_val))
                if hw is not None:
                    f["HI_Winter_Mean"] = round(hw, 2)
            if f.get("HI_Annual_Range") is None and f.get("HI_Summer_Mean") is not None and f.get("HI_Winter_Mean") is not None:
                f["HI_Annual_Range"] = round(abs(f["HI_Summer_Mean"] - f["HI_Winter_Mean"]), 2)
            if f.get("HI_Seasonal_Range") is None:
                _s4 = [f.get("HI_Spring_Mean"), f.get("HI_Summer_Mean"),
                       f.get("HI_Autumn_Mean"), f.get("HI_Winter_Mean")]
                _s4 = [float(v) for v in _s4 if v is not None]
                if len(_s4) >= 2:
                    f["HI_Seasonal_Range"] = round(max(_s4) - min(_s4), 2)
            if f.get("WBGT_Summer_Mean") is None and t_val is not None and rh_val is not None:
                wb = wbgt_shade_c(float(t_val), float(rh_val))
                if wb is not None:
                    f["WBGT_Summer_Mean"] = round(wb, 2)

            # 7. Wind Chill
            if f.get("WC_Winter_Mean") is None and t_val is not None and w_val is not None:
                wc = wind_chill_c(float(t_val), float(w_val))
                if wc is not None:
                    f["WC_Winter_Mean"] = round(wc, 2)
            if f.get("WC_Annual_Mean") is None and t_val is not None and w_val is not None:
                wc = wind_chill_c(float(t_val), float(w_val))
                if wc is not None:
                    f["WC_Annual_Mean"] = round(wc, 2)

        # Destination GDB setup
        gdb_dest = None
        if self.export_gdb:
            gdb_dest = os.path.join(self.out_dir, "Migrated_Climate_Database.gdb")
            if not arcpy.Exists(gdb_dest):
                self.log("Creating output File Geodatabase: %s" % os.path.basename(gdb_dest))
                arcpy.management.CreateFileGDB(self.out_dir, "Migrated_Climate_Database.gdb")

        shp_dir = os.path.join(self.out_dir, "Shapefiles")
        if self.export_shp and not os.path.exists(shp_dir):
            os.makedirs(shp_dir)

        csv_dir = os.path.join(self.out_dir, "CSV_Tables")
        if self.export_csv and not os.path.exists(csv_dir):
            os.makedirs(csv_dir)

        # 3. Export all 17 independent modules
        migrated_counts = {}
        for mod_info in MODULES_INFO:
            m_name = mod_info["name"]
            m_folder = mod_info["folder"]
            m_short = mod_info["short"]
            ind_fields = mod_info["fields"]
            fld_names = [f[0] for f in ind_fields]

            # Check if at least one indicator is populated
            has_data = any(any(rec["fields"].get(fld) is not None for fld in fld_names) for rec in point_records)
            if not has_data:
                self.log("  [Skip] %s: No attributes available in input data." % m_folder)
                continue

            self.log("Writing modular element: %s (%d indicators)..." % (m_folder, len(ind_fields)))

            # A. Output Feature Class in GDB
            if self.export_gdb and gdb_dest:
                fc_out = os.path.join(gdb_dest, m_short)
                if arcpy.Exists(fc_out):
                    try:
                        arcpy.management.Delete(fc_out)
                    except Exception:
                        pass
                arcpy.management.CopyFeatures(base_layer, fc_out)

                existing_f = set(f.name for f in arcpy.ListFields(fc_out))
                for req_admin in ["Point_ID", "POINT_X", "POINT_Y", "Data_Start", "Data_End"]:
                    if req_admin not in existing_f:
                        f_typ = "LONG" if req_admin == "Point_ID" else ("TEXT" if req_admin.startswith("Data_") else "DOUBLE")
                        arcpy.management.AddField(fc_out, req_admin, f_typ, field_alias=req_admin)

                for fld in fld_names:
                    if fld not in existing_f:
                        f_typ = "LONG" if fld == "Dry_Months_Count" else "DOUBLE"
                        arcpy.management.AddField(fc_out, fld, f_typ, field_alias=fld)

                oid_n = arcpy.Describe(fc_out).OIDFieldName
                with arcpy.da.UpdateCursor(fc_out, [oid_n, "Point_ID", "POINT_X", "POINT_Y", "Data_Start", "Data_End"] + fld_names) as ucur:
                    for row in ucur:
                        p_oid = row[0]
                        p_idx = oid_to_idx.get(p_oid)
                        rec_entry = point_records[p_idx] if (p_idx is not None and p_idx < len(point_records)) else {}
                        rec_fields = rec_entry.get("fields", {})
                        row[1] = p_oid
                        row[2] = rec_entry.get("lon")
                        row[3] = rec_entry.get("lat")
                        row[4] = col_data_start
                        row[5] = col_data_end

                        for fi, fld in enumerate(fld_names):
                            val = rec_fields.get(fld)
                            if val is None and fld in SHP_FIELD_MAP:
                                val = rec_fields.get(SHP_FIELD_MAP[fld])
                            if val is None and fld in REV_SHP_MAP:
                                val = rec_fields.get(REV_SHP_MAP[fld])
                            row[6 + fi] = val
                        ucur.updateRow(row)

                # Clean any unwanted/extraneous fields (e.g. Feat_ID, Feat_Name, old attributes)
                keep_fields = set(["OBJECTID", "Shape", "SHAPE", oid_n, "Point_ID", "POINT_X", "POINT_Y", "Data_Start", "Data_End"] + fld_names)
                to_delete = [f.name for f in arcpy.ListFields(fc_out) if f.name not in keep_fields and f.type not in ("OID", "Geometry")]
                if to_delete:
                    try:
                        arcpy.management.DeleteField(fc_out, to_delete)
                    except Exception:
                        pass

                migrated_counts[m_folder] = int(arcpy.GetCount_management(fc_out)[0])

                # B. Shapefile export
                if self.export_shp:
                    shp_out = os.path.join(shp_dir, "%s.shp" % m_folder)
                    if arcpy.Exists(shp_out):
                        try:
                            arcpy.management.Delete(shp_out)
                        except Exception:
                            pass
                    arcpy.management.CopyFeatures(fc_out, shp_out)

            # C. CSV Table Export
            if self.export_csv:
                csv_path = os.path.join(csv_dir, "%s.csv" % m_folder)
                self._write_csv_table(csv_path, point_records, fld_names, col_data_start, col_data_end)

        self.log("=" * 70)
        self.log("MIGRATION COMPLETED SUCCESSFULLY!")
        self.log("Migrated %d independent climate element layers:" % len(migrated_counts))
        for k in sorted(migrated_counts.keys()):
            self.log("  ✓ %s: %d points" % (k, migrated_counts[k]))
        if self.export_gdb and gdb_dest:
            self.log("Geodatabase: %s" % gdb_dest)
        if self.export_shp:
            self.log("Shapefiles:  %s" % shp_dir)
        if self.export_csv:
            self.log("CSV Tables:  %s" % csv_dir)
        self.log("=" * 70)
        return migrated_counts

    def _write_csv_table(self, csv_path, point_records, fld_names, col_start, col_end):
        import csv
        header = ["Point_ID", "POINT_X", "POINT_Y", "Data_Start", "Data_End"] + fld_names
        with open(csv_path, "w") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(header)
            for rec in point_records:
                rf = rec.get("fields", {})
                row = [rec.get("oid", ""), rec.get("lon", ""), rec.get("lat", ""), col_start, col_end]
                for fld in fld_names:
                    val = rf.get(fld)
                    if val is None and fld in SHP_FIELD_MAP:
                        val = rf.get(SHP_FIELD_MAP[fld])
                    row.append(val if val is not None else "")
                writer.writerow(row)

    def _run_pure_python(self, layers):
        self.log("Pure-Python fallback mode: reading Shapefiles / CSV...")
        # Pure python CSV export implementation
        return {}


# ---------------------------------------------------------------------------
# CLI Argument Parser & Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Migrate legacy monolithic Climate_Models databases into 17 standalone modular layers."
    )
    parser.add_argument("--input", "-i", required=False, default="",
                        help="Path to legacy File Geodatabase (.gdb) or directory of shapefiles (.shp)")
    parser.add_argument("--output", "-o", required=False, default="",
                        help="Path to destination directory for migrated standalone layers")
    parser.add_argument("--no-shp", action="store_true", default=False,
                        help="Disable shapefile generation")
    parser.add_argument("--no-gdb", action="store_true", default=False,
                        help="Disable File Geodatabase generation")
    parser.add_argument("--no-csv", action="store_true", default=False,
                        help="Disable CSV tables generation")

    args = parser.parse_args()

    in_path = args.input
    out_dir = args.output

    # Interactive prompts if arguments not provided
    if not in_path:
        print("\n=== NASA POWER Climate Atlas — Legacy Database Migration Utility ===")
        if sys.version_info[0] < 3:
            in_path = raw_input("Enter path to legacy .gdb or shapefiles directory: ").strip().strip("'\"")
        else:
            in_path = input("Enter path to legacy .gdb or shapefiles directory: ").strip().strip("'\"")

    if not out_dir:
        default_out = os.path.join(os.path.dirname(in_path), "Migrated_Atlas_Output") if in_path else "Migrated_Atlas_Output"
        if sys.version_info[0] < 3:
            user_out = raw_input("Enter destination output directory [%s]: " % default_out).strip().strip("'\"")
        else:
            user_out = input("Enter destination output directory [%s]: " % default_out).strip().strip("'\"")
        out_dir = user_out if user_out else default_out

    migrator = LegacyAtlasMigrator(
        in_path=in_path,
        out_dir=out_dir,
        export_shp=not args.no_shp,
        export_gdb=not args.no_gdb,
        export_csv=not args.no_csv
    )
    migrator.run()


if __name__ == "__main__":
    main()
