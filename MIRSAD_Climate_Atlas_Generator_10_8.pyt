# -*- coding: utf-8 -*-
"""
POWER Climate Atlas Generator — ArcMap Desktop 10.x edition (tested 10.8)
ArcGIS Desktop Python Toolbox (.pyt) — Python 2.7 compatible.

Developed by: Ahmad Ibrahim (@ahmadibrahim4geo)
إعداد وتطوير: أحمد إبراهيم
Email / البريد الإلكتروني: ahmadibrahim.geo@gmail.com

Data source: NASA POWER API (https://power.larc.nasa.gov/)
             & Open-Meteo Climate API (https://open-meteo.com/)

Tool: POWER Climate Atlas Generator
- Reads an input point layer + optional study-area mask polygon.
- Queries NASA POWER (Monthly/Daily) per point with retries + parallelism.
- Computes annual/seasonal indicators with correct units.
- Builds per-element point layers (GDB + SHP + CSV each), interpolated clipped rasters
  (GeoTIFF, written directly inside each element folder), wind vector layers,
  optional PSL isobars, bilingual data dictionaries and a processing log.

Field/raster names, folder layout, seasons, color ramps and units follow the
project technical specification exactly. Rasters open directly in ArcMap with
standard stretched symbology (no intermediate layer files are produced).

Only libraries available in a stock ArcGIS Desktop 10.x Python are used:
arcpy, requests (with urllib2 fallback), json, os, math, datetime, calendar,
csv, io.
"""

import os
import sys
import json
import math
import csv
import io
import time
import calendar
import gc
import traceback
import datetime as _dt

PY27 = sys.version_info[0] == 2

# Python 2/3 compat aliases (RHS only evaluated in the taken branch, so no NameError).
if PY27:
    _text_type = unicode  # noqa: F821 - Python 2 only
    _binary_type = str
else:
    _text_type = str
    _binary_type = bytes


def _excel_text(v):
    """Return text suitable for xlwt on both Python 2 (unicode) and 3 (str)."""
    if v is None:
        return ""
    if PY27:
        try:
            if isinstance(v, _text_type):
                return v
            if isinstance(v, _binary_type):
                try:
                    return v.decode("utf-8")
                except Exception:
                    return v
            return _text_type(v)
        except Exception:
            try:
                return str(v)
            except Exception:
                return ""
    else:
        if isinstance(v, str):
            return v
        if isinstance(v, bytes):
            try:
                return v.decode("utf-8")
            except Exception:
                return v.decode("utf-8", errors="replace")
        try:
            return str(v)
        except Exception:
            return ""

try:
    import arcpy
    _HAS_ARCPY = True
except Exception:
    arcpy = None
    _HAS_ARCPY = False

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    requests = None
    _HAS_REQUESTS = False

_this_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

try:
    from raster_atlas_generator import RasterDataClimateAtlasGenerator
except Exception:
    RasterDataClimateAtlasGenerator = None

TOOL_VERSION = "1.1-arcmap10"
# CONSISTENCY_MARKER_ZZ9
NASA_BASE = "https://power.larc.nasa.gov/api/temporal"
NASA_COMMUNITY = "AG"
MISSING_SENTINELS = (-999.0, -999, -99.0, -99)

SEASONS = {
    # Climatological approximation: December of the SAME calendar year.
    # Strict WMO DJF uses Dec of the previous year + Jan/Feb of the current
    # year; for multi-year climatological means the difference is negligible,
    # for single years it can be noticeable (documented, test-verified).
    "Winter": (1, 2, 12),
    "Spring": (3, 4, 5),
    "Summer": (6, 7, 8),
    "Autumn": (9, 10, 11),
}
SEASON_SUFFIX = {"Winter": "Win", "Spring": "Spr", "Summer": "Sum", "Autumn": "Aut"}

PRIMARY_MODULES_ALL = [
    "Temperature",
    "Land Surface Temperature",
    "Precipitation",
    "Sea Level Pressure",
    "Surface Pressure",
    "Wind",
    "Relative Humidity",
    "Dew Point",
    "Solar Radiation",
    "UV Index",
    "Cloud Cover",
]

SUBMODELS_ALL = [
    "Heat Index / Thermal Stress [Requires: Temperature, Relative Humidity]",
    "Wind Chill / Cold Stress [Requires: Temperature, Wind]",
    "De Martonne Aridity Index [Requires: Temperature, Precipitation]",
    "Evapotranspiration (ET) [Requires: Temperature]",
    "UNEP Aridity Index [Requires: Temperature, Precipitation]",
    "Water Deficit Annual [Requires: Temperature, Precipitation]",
    "Walter-Lieth Dry Months Count [Requires: Temperature, Precipitation]",
    "Trends & Baseline Anomalies [Requires: Temperature, Precipitation]",
]

DERIVED_MODULES_ALL = [
    "Heat Index",
    "Wind Chill",
    "De Martonne Aridity",
    "Evapotranspiration",
    "UNEP Aridity",
    "Water Deficit",
    "Dry Months",
    "Trends & Anomalies",
]

CANONICAL_DERIVED_MAP = {
    "Heat Index / Thermal Stress [Requires: Temperature, Relative Humidity]": "Heat Index",
    "Wind Chill / Cold Stress [Requires: Temperature, Wind]": "Wind Chill",
    "De Martonne Aridity Index [Requires: Temperature, Precipitation]": "De Martonne Aridity",
    "Evapotranspiration (ET) [Requires: Temperature]": "Evapotranspiration",
    "FAO-56 Hargreaves PET [Requires: Temperature]": "Evapotranspiration",
    "Hargreaves PET": "Evapotranspiration",
    "Hargreaves_PET": "Evapotranspiration",
    "ET": "Evapotranspiration",
    "UNEP Aridity Index [Requires: Temperature, Precipitation]": "UNEP Aridity",
    "Water Deficit Annual [Requires: Temperature, Precipitation]": "Water Deficit",
    "Walter-Lieth Dry Months Count [Requires: Temperature, Precipitation]": "Dry Months",
    "Trends & Baseline Anomalies [Requires: Temperature, Precipitation]": "Trends & Anomalies",
}

DERIVED_TO_SUBMODEL_KEY = dict((CANONICAL_DERIVED_MAP[s], s) for s in SUBMODELS_ALL)

MODULES_ALL = PRIMARY_MODULES_ALL + SUBMODELS_ALL
ALL_CANONICAL_MODULES = PRIMARY_MODULES_ALL + DERIVED_MODULES_ALL

SUBMODEL_DEPS = {
    "Heat Index / Thermal Stress [Requires: Temperature, Relative Humidity]": {
        "short": "Heat_Index",
        "canonical": "Heat Index",
        "field": "HI_Summer_Mean",
        "fields": ["HI_Annual_Mean", "HI_Summer_Mean", "HI_Spring_Mean", "HI_Autumn_Mean", "HI_Winter_Mean", "HI_Annual_Range", "WBGT_Summer_Mean"],
        "modules": ["Temperature", "Relative Humidity"],
        "params": ["T2M", "T2M_MAX", "RH2M"]
    },
    "Wind Chill / Cold Stress [Requires: Temperature, Wind]": {
        "short": "Wind_Chill",
        "canonical": "Wind Chill",
        "field": "WC_Winter_Mean",
        "fields": ["WC_Winter_Mean", "WC_Annual_Mean"],
        "modules": ["Temperature", "Wind"],
        "params": ["T2M", "WS10M"]
    },
    "De Martonne Aridity Index [Requires: Temperature, Precipitation]": {
        "short": "De_Martonne_Aridity",
        "canonical": "De Martonne Aridity",
        "field": "DM_Aridity_Annual",
        "fields": ["DM_Aridity_Annual"],
        "modules": ["Temperature", "Precipitation"],
        "params": ["T2M", "PRECTOTCORR"]
    },
    "Evapotranspiration (ET) [Requires: Temperature]": {
        "short": "Evapotranspiration",
        "canonical": "Evapotranspiration",
        "field": "ET_Annual_Mean",
        "fields": ["ET_Annual_Mean", "ET_Annual_Range",
                   "ET_Winter_Mean", "ET_Spring_Mean", "ET_Summer_Mean", "ET_Autumn_Mean"],
        "modules": ["Temperature"],
        "params": ["T2M", "T2M_MAX", "T2M_MIN"]
    },
    "UNEP Aridity Index [Requires: Temperature, Precipitation]": {
        "short": "UNEP_Aridity",
        "canonical": "UNEP Aridity",
        "field": "UNEP_Aridity_Annual",
        "fields": ["UNEP_Aridity_Annual"],
        "modules": ["Temperature", "Precipitation"],
        "params": ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR"]
    },
    "Water Deficit Annual [Requires: Temperature, Precipitation]": {
        "short": "Water_Deficit",
        "canonical": "Water Deficit",
        "field": "Water_Deficit_Annual",
        "fields": ["Water_Deficit_Annual"],
        "modules": ["Temperature", "Precipitation"],
        "params": ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR"]
    },
    "Walter-Lieth Dry Months Count [Requires: Temperature, Precipitation]": {
        "short": "Dry_Months",
        "canonical": "Dry Months",
        "field": "Dry_Months_Count",
        "fields": ["Dry_Months_Count"],
        "modules": ["Temperature", "Precipitation"],
        "params": ["T2M", "PRECTOTCORR"]
    },
    "Trends & Baseline Anomalies [Requires: Temperature, Precipitation]": {
        "short": "Trends_And_Anomalies",
        "canonical": "Trends & Anomalies",
        "field": "T_Annual_Trend_Decade",
        "fields": ["T_Annual_Trend_Decade", "R_Annual_Trend_Decade", "T_Annual_Anom",
                   "T_Anom_Winter", "T_Anom_Summer", "R_Annual_Anom",
                   "R_Annual_Anom_Pct", "R_Anom_Winter", "R_Anom_Winter_Pct"],
        "modules": ["Temperature", "Precipitation"],
        "params": ["T2M", "PRECTOTCORR"]
    }
}

# Monthly trend/anomaly fields follow the *_<Month> naming pattern of the
# monthly means (T_Anom_January ... R_December_Trend_Decade). Alias == English name.
_TREND_MONTHS = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
_TREND_SUB_KEY = "Trends & Baseline Anomalies [Requires: Temperature, Precipitation]"
for _mn in _TREND_MONTHS:
    SUBMODEL_DEPS[_TREND_SUB_KEY]["fields"] += [
        "T_Anom_%s" % _mn, "R_Anom_%s" % _mn, "R_Anom_%s_Pct" % _mn,
        "T_%s_Trend_Decade" % _mn, "R_%s_Trend_Decade" % _mn,
    ]
# Seasonal complements (anomaly + per-season trend for the missing seasons).
SUBMODEL_DEPS[_TREND_SUB_KEY]["fields"] += [
    "T_Anom_Spring", "T_Anom_Autumn",
    "R_Anom_Spring", "R_Anom_Spring_Pct",
    "R_Anom_Summer", "R_Anom_Summer_Pct",
    "R_Anom_Autumn", "R_Anom_Autumn_Pct",
    "T_Winter_Trend_Decade", "T_Spring_Trend_Decade", "T_Summer_Trend_Decade", "T_Autumn_Trend_Decade",
    "R_Winter_Trend_Decade", "R_Spring_Trend_Decade", "R_Summer_Trend_Decade", "R_Autumn_Trend_Decade",
]
# General-monthly aggregates (same *_Month_Mean pattern as the means).
SUBMODEL_DEPS[_TREND_SUB_KEY]["fields"] += [
    "T_Anom_Month", "R_Anom_Month", "R_Anom_Month_Pct",
    "T_Month_Trend_Decade", "R_Month_Trend_Decade",
]

# Fail-safe alias population for SUBMODEL_DEPS
for _can, _sub_k in DERIVED_TO_SUBMODEL_KEY.items():
    if _sub_k in SUBMODEL_DEPS and _can not in SUBMODEL_DEPS:
        SUBMODEL_DEPS[_can] = SUBMODEL_DEPS[_sub_k]

if "Evapotranspiration (ET) [Requires: Temperature]" in SUBMODEL_DEPS:
    _et_info = SUBMODEL_DEPS["Evapotranspiration (ET) [Requires: Temperature]"]
    SUBMODEL_DEPS["ET"] = _et_info
    SUBMODEL_DEPS["Hargreaves PET"] = _et_info
    SUBMODEL_DEPS["Hargreaves_PET"] = _et_info

def resolve_module_canonical(name):
    """Maps any module name (full UI string, canonical, or short) to its canonical name."""
    if not name:
        return None
    name_str = name.strip().strip("'\"")
    def _norm(s):
        return str(s).strip().strip("'\"").lower().replace("_", " ").replace("-", " ")
    n_input = _norm(name_str)
    # Legacy and alias fast lookup
    _DIRECT_ALIASES = {
        "et": "Evapotranspiration",
        "evaporation": "Evapotranspiration",
        "evapotranspiration": "Evapotranspiration",
        "hargreaves pet": "Evapotranspiration",
        "hargreaves_pet": "Evapotranspiration",
        "humidity": "Relative Humidity",
        "relative humidity": "Relative Humidity",
        "relative_humidity": "Relative Humidity",
        "trends anomalies": "Trends & Anomalies",
        "trends_anomalies": "Trends & Anomalies",
        "trends and anomalies": "Trends & Anomalies",
        "trends_and_anomalies": "Trends & Anomalies",
        "dew point": "Dew Point",
        "dew_point": "Dew Point",
    }
    if n_input in _DIRECT_ALIASES:
        return _DIRECT_ALIASES[n_input]
    for cm in ALL_CANONICAL_MODULES:
        if n_input == _norm(cm) or name_str.lower() == cm.lower():
            return cm
    if name_str in CANONICAL_DERIVED_MAP:
        return CANONICAL_DERIVED_MAP[name_str]
    clean = name_str.split(" [")[0].strip().lower()
    clean_norm = _norm(clean)
    if clean_norm in _DIRECT_ALIASES:
        return _DIRECT_ALIASES[clean_norm]
    for sub_key, can_name in CANONICAL_DERIVED_MAP.items():
        k_clean = _norm(sub_key.split(" [")[0])
        if clean_norm == k_clean or k_clean.startswith(clean_norm) or clean_norm == _norm(can_name):
            return can_name
    for info in SUBMODEL_DEPS.values():
        if clean_norm == _norm(info.get("short", "")) or clean_norm == _norm(info.get("canonical", "")):
            return info["canonical"]
    try:
        for can_name, folder_name in MODULE_FOLDER.items():
            if n_input == _norm(folder_name):
                return can_name
        for leg_folder, can_name in LEGACY_MODULE_FOLDERS.items():
            if n_input == _norm(leg_folder):
                return can_name
        for can_name, short_code in MODULE_SHORT.items():
            if n_input == _norm(short_code):
                return can_name
    except Exception:
        pass
    return None

def resolve_submodel_name(name):
    """Legacy helper returning full submodel key if name represents a derived module."""
    if not name:
        return None
    name_str = str(name).strip().strip("'\"")
    if name_str in SUBMODELS_ALL:
        return name_str
    can = resolve_module_canonical(name_str)
    if can and can in DERIVED_TO_SUBMODEL_KEY:
        return DERIVED_TO_SUBMODEL_KEY[can]
    if name_str in SUBMODEL_DEPS:
        sub_k = SUBMODEL_DEPS[name_str].get("canonical")
        if sub_k and sub_k in DERIVED_TO_SUBMODEL_KEY:
            return DERIVED_TO_SUBMODEL_KEY[sub_k]
        return name_str
    return None

MODULE_PARAMS = {
    "Temperature": ["T2M", "T2M_MAX", "T2M_MIN", "RH2M", "T2MDEW"],
    "Precipitation": ["PRECTOTCORR"],
    "Sea Level Pressure": ["SLP"],
    "Surface Pressure": ["PS"],
    "Wind": ["WS10M", "WD10M"],
    "Relative Humidity": ["RH2M"],
    "Dew Point": ["T2MDEW"],
    "Solar Radiation": ["ALLSKY_SFC_SW_DWN"],
    "UV Index": ["ALLSKY_SFC_UV_INDEX"],
    "Cloud Cover": ["CLOUD_AMT"],
    "Heat Index": ["T2M", "T2M_MAX", "RH2M"],
    "Wind Chill": ["T2M", "WS10M"],
    "De Martonne Aridity": ["T2M", "PRECTOTCORR"],
    "Evapotranspiration": ["T2M", "T2M_MAX", "T2M_MIN"],
    "Hargreaves PET": ["T2M", "T2M_MAX", "T2M_MIN"],
    "UNEP Aridity": ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR"],
    "Water Deficit": ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR"],
    "Dry Months": ["T2M", "PRECTOTCORR"],
    "Trends & Anomalies": ["T2M", "PRECTOTCORR"],
    "Climate_Models": ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS10M"],
    "Drought & Aridity": ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN"],
    "Land Surface Temperature": ["TS", "T2M"],
}

MODULE_FOLDER = {
    "Temperature": "01_Temperature",
    "Land Surface Temperature": "02_Land_Surface_Temperature",
    "Precipitation": "03_Precipitation",
    "Sea Level Pressure": "04_Sea_Level_Pressure",
    "Surface Pressure": "05_Surface_Pressure",
    "Wind": "06_Wind",
    "Relative Humidity": "07_Relative_Humidity",
    "Dew Point": "08_Dew_Point",
    "Solar Radiation": "09_Solar_Radiation",
    "UV Index": "10_UV_Index",
    "Cloud Cover": "11_Cloud_Cover",
    "Heat Index": "12_Heat_Index",
    "Wind Chill": "13_Wind_Chill",
    "De Martonne Aridity": "14_De_Martonne_Aridity",
    "Evapotranspiration": "15_Evapotranspiration",
    "Hargreaves PET": "15_Evapotranspiration",
    "UNEP Aridity": "16_UNEP_Aridity",
    "Water Deficit": "17_Water_Deficit",
    "Dry Months": "18_Dry_Months",
    "Trends & Anomalies": "19_Trends_And_Anomalies",
    "Climate_Models": "12_Climate_Models",
}

LEGACY_MODULE_FOLDERS = {
    "19_Land_Surface_Temperature": "Land Surface Temperature",
    "02_Precipitation": "Precipitation",
    "03_Sea_Level_Pressure": "Sea Level Pressure",
    "04_Surface_Pressure": "Surface Pressure",
    "05_Wind": "Wind",
    "06_Relative_Humidity": "Relative Humidity",
    "07_Dew_Point": "Dew Point",
    "08_Solar_Radiation": "Solar Radiation",
    "09_UV_Index": "UV Index",
    "10_Cloud_Cover": "Cloud Cover",
    "11_Heat_Index": "Heat Index",
    "12_Wind_Chill": "Wind Chill",
    "13_De_Martonne_Aridity": "De Martonne Aridity",
    "14_Evapotranspiration": "Evapotranspiration",
    "15_UNEP_Aridity": "UNEP Aridity",
    "16_Water_Deficit": "Water Deficit",
    "17_Dry_Months": "Dry Months",
    "18_Trends_And_Anomalies": "Trends & Anomalies",
}

COLOR_RAMPS = {
    "Temperature": ["#4575B4", "#74ADD1", "#ABD9E9", "#FFFFBF", "#FDAE61", "#F46D43", "#D73027"],
    "Precipitation": ["#8C510A", "#D8B365", "#F6E8C3", "#C7EAE5", "#80CDC1", "#35978F", "#01665E"],
    "Sea Level Pressure": ["#762A83", "#9970AB", "#C2A5CF", "#F7F7F7", "#A6DBA0", "#5AAE61", "#1B7837"],
    "Surface Pressure": ["#762A83", "#9970AB", "#C2A5CF", "#F7F7F7", "#A6DBA0", "#5AAE61", "#1B7837"],
    "Wind_Speed": ["#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C"],
    "Wind_Direction": ["#F7F7F7", "#D9D9D9", "#BDBDBD", "#969696", "#737373", "#525252", "#252525"],
    "Relative Humidity": ["#FFFFCC", "#C7E9B4", "#7FCDBB", "#41B6C4", "#1D91C0", "#225EA8", "#0C2C84"],
    "Dew Point": ["#FFFFCC", "#C7E9B4", "#7FCDBB", "#41B6C4", "#1D91C0", "#225EA8", "#0C2C84"],
    "Solar Radiation": ["#FFFFCC", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#BD0026"],
    "UV Index": ["#299500", "#F7E400", "#F85900", "#D8001D", "#6B499D"],
    "Cloud Cover": ["#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#4292C6", "#2171B5", "#084594"],
    "Heat Index": ["#FFFFD4", "#FEE391", "#FEC44F", "#FE9929", "#EC7014", "#CC4C02", "#8C2D04"],
    "Wind Chill": ["#08306B", "#08519C", "#2171B5", "#4292C6", "#6BAED6", "#9ECAE1", "#C6DBEF"],
    "De Martonne Aridity": ["#8C510A", "#D8B365", "#F6E8C3", "#E0E0E0", "#80CDC1", "#35978F", "#01665E"],
    "Evapotranspiration": ["#FFFFCC", "#D9F0A3", "#ADDD8E", "#78C679", "#41AB5D", "#238443", "#005A32"],
    "Hargreaves PET": ["#FFFFCC", "#D9F0A3", "#ADDD8E", "#78C679", "#41AB5D", "#238443", "#005A32"],
    "UNEP Aridity": ["#D73027", "#FC8D59", "#FEE08B", "#FFFFBF", "#D9EF8B", "#91CF60", "#1A9850"],
    "Water Deficit": ["#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#D1E5F0", "#92C5DE", "#4393C3"],
    "Dry Months": ["#2166AC", "#4393C3", "#92C5DE", "#D1E5F0", "#FDDBC7", "#F4A582", "#D6604D"],
    "Trends & Anomalies": ["#2166AC", "#67A9CF", "#D1E5F0", "#F7F7F7", "#FDDBC7", "#EF8A62", "#B2182B"],
    "Land Surface Temperature": ["#4575B4", "#74ADD1", "#ABD9E9", "#FFFFBF", "#FDAE61", "#F46D43", "#D73027"],
    "Climate_Models": ["#8C510A", "#D8B365", "#F6E8C3", "#E0E0E0", "#80CDC1", "#35978F", "#01665E"],
}


# ---------------------------------------------------------------------------
# Small portability helpers (py2/py3 + Desktop/Pro)
# ---------------------------------------------------------------------------

def now_str():
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds):
    if seconds is None:
        return "0s"
    s = int(round(seconds))
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    if hrs > 0:
        return "%dh %02dm %02ds" % (hrs, mins, secs)
    elif mins > 0:
        return "%dm %02ds" % (mins, secs)
    else:
        return "%.1fs" % seconds


def makedirs_ok(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise


def open_utf8(path, mode="w"):
    # io.open supports encoding + newline on both 2.7 and 3.x
    if "b" in mode:
        return open(path, mode)
    return io.open(path, mode, encoding="utf-8-sig" if "w" in mode else "utf-8",
                   newline="" if not PY27 else None)


def _enc(cell):
    # csv on py2.7 needs byte strings
    if cell is None:
        return ""
    if PY27 and isinstance(cell, unicode):
        return cell.encode("utf-8")
    if PY27 and isinstance(cell, float) and (cell != cell):
        return ""
    return cell


def write_csv(path, header, rows):
    if PY27:
        fh = open(path, "wb")
        fh.write(u"\ufeff".encode("utf-8"))
        w = csv.writer(fh)
        w.writerow([_enc(h) for h in header])
        for r in rows:
            w.writerow([_enc(c) for c in r])
        fh.close()
    else:
        with io.open(path, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            for r in rows:
                w.writerow(["" if c is None else c for c in r])


def write_excel_file(path, header, rows, sheet_name="Data", rtl=False):
    """Writes a styled Microsoft Excel .xls workbook using xlwt."""
    try:
        import xlwt
    except ImportError:
        return False

    wb = xlwt.Workbook(encoding="utf-8")
    safe_sheet = (sheet_name or "Data")[:31]
    ws = wb.add_sheet(safe_sheet)
    if rtl:
        try:
            ws.cols_right_to_left = True
        except Exception:
            pass

    header_style = xlwt.easyxf(
        "font: bold on, color white, height 220; "
        "pattern: pattern solid, fore_colour dark_blue; "
        "align: horiz center, vert center; "
        "borders: left thin, right thin, top thin, bottom thin;"
    )
    zebra_style = xlwt.easyxf(
        "pattern: pattern solid, fore_colour 0x1F; "
        "borders: left thin, right thin, top thin, bottom thin; "
        "align: vert center;"
    )
    data_style = xlwt.easyxf(
        "borders: left thin, right thin, top thin, bottom thin; "
        "align: vert center;"
    )

    col_widths = {}
    for col_idx, h in enumerate(header):
        h_str = _excel_text(h)
        ws.write(0, col_idx, h_str, header_style)
        col_widths[col_idx] = len(h_str)

    for row_idx, r in enumerate(rows):
        cur_style = zebra_style if (row_idx % 2 == 1) else data_style
        for col_idx, cell in enumerate(r):
            val = cell
            if cell is None:
                val = ""
            elif isinstance(cell, _binary_type):
                try:
                    val = cell.decode("utf-8")
                except Exception:
                    pass
            elif isinstance(cell, float):
                if math.isnan(cell) or abs(cell - (-999.0)) < 1e-5:
                    val = ""
                else:
                    val = round(cell, 3)

            ws.write(row_idx + 1, col_idx, val, cur_style)
            val_len = len(_excel_text(val)) if val != "" else 0
            if val_len > col_widths.get(col_idx, 0):
                col_widths[col_idx] = val_len

    for col_idx, width in col_widths.items():
        ws.col(col_idx).width = min(256 * 60, max(256 * 12, 256 * (width + 5)))

    wb.save(path)
    return True


def write_master_excel_workbook(path, sheets_list):
    """
    Writes a multi-sheet styled Microsoft Excel .xls workbook.
    sheets_list: list of (sheet_name, header, rows, rtl)
    """
    try:
        import xlwt
    except ImportError:
        return False

    wb = xlwt.Workbook(encoding="utf-8")
    header_style = xlwt.easyxf(
        "font: bold on, color white, height 220; "
        "pattern: pattern solid, fore_colour dark_blue; "
        "align: horiz center, vert center; "
        "borders: left thin, right thin, top thin, bottom thin;"
    )
    zebra_style = xlwt.easyxf(
        "pattern: pattern solid, fore_colour 0x1F; "
        "borders: left thin, right thin, top thin, bottom thin; "
        "align: vert center;"
    )
    data_style = xlwt.easyxf(
        "borders: left thin, right thin, top thin, bottom thin; "
        "align: vert center;"
    )

    for item in sheets_list:
        sheet_name, header, rows, rtl = item[0], item[1], item[2], item[3]
        safe_sheet = (sheet_name or "Sheet")[:31]
        ws = wb.add_sheet(safe_sheet)
        if rtl:
            try:
                ws.cols_right_to_left = True
            except Exception:
                pass

        col_widths = {}
        for col_idx, h in enumerate(header):
            h_str = _excel_text(h)
            ws.write(0, col_idx, h_str, header_style)
            col_widths[col_idx] = len(h_str)

        for row_idx, r in enumerate(rows):
            cur_style = zebra_style if (row_idx % 2 == 1) else data_style
            for col_idx, cell in enumerate(r):
                val = cell
                if cell is None:
                    val = ""
                elif isinstance(cell, _binary_type):
                    try:
                        val = cell.decode("utf-8")
                    except Exception:
                        pass
                elif isinstance(cell, float):
                    if math.isnan(cell) or abs(cell - (-999.0)) < 1e-5:
                        val = ""
                    else:
                        val = round(cell, 3)

                ws.write(row_idx + 1, col_idx, val, cur_style)
                val_len = len(_excel_text(val)) if val != "" else 0
                if val_len > col_widths.get(col_idx, 0):
                    col_widths[col_idx] = val_len

        for col_idx, width in col_widths.items():
            ws.col(col_idx).width = min(256 * 60, max(256 * 12, 256 * (width + 5)))

    wb.save(path)
    return True


# ---------------------------------------------------------------------------
# Data Source & Model Provenance Metadata Core
# ---------------------------------------------------------------------------

def get_element_source_metadata(module, provider, om_model=None, gap_method="climatological", y0=1996, y1=2025):
    """
    Returns accurate scientific provenance metadata for a climate element
    and provider combination.
    """
    p = str(provider or "").lower()
    m = str(module or "")
    om_m = str(om_model or "ERA5-Land")

    if "hybrid" in p:
        p_src = "NOAA ISD / GHCN Certified Ground Station Network"
        model = "In-Situ Synoptic Ground Tower (Observed Ground-Truth) + ECMWF ERA5-Land (~9 km) / MERRA-2"
        url = "https://www.ncei.noaa.gov | https://open-meteo.com | https://power.larc.nasa.gov"
        gap_m = "Automated Hybrid Satellite & Reanalysis Numerical Imputation"
        gap_s = "ECMWF ERA5-Land (~9 km) / NASA POWER MERRA-2 (~50 km)"
        cov = "1940-Present (Ground-Truth Unified)"
        res = "In-Situ Ground Point + 0.1 deg (~9 km) Gap-Filling"
        qual = "Hybrid Multi-Tier Validated (100% Complete Record)"
        citation = "NOAA NCEI ISD Ground Observations & ECMWF ERA5-Land Reanalysis (Hersbach et al., 2020)"
    elif "noaa" in p:
        p_src = "NOAA NCEI Integrated Surface Database (ISD / GHCN)"
        model = "In-Situ Synoptic Meteorological Tower (WMO Standard Instruments)"
        url = "https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database"
        gap_m = "None (Pure Ground Observation)" if gap_method == "none" else "Climatological Station Imputation"
        gap_s = "None" if gap_method == "none" else "Station Multi-Year Climatology Baseline"
        cov = "1901-Present (Historical & Active Network)"
        res = "Point Ground Station Observation Tower"
        qual = "NOAA NCEI Level 2 Certified Ground Observation"
        citation = "Smith, A., et al. (2011). The Integrated Surface Database: Recent Improvements. BAMS."
    elif "copernicus" in p or "cds" in p:
        p_src = "Copernicus Climate Data Store (CDS) - European Union / ECMWF"
        if "land" in om_m.lower():
            model = "ECMWF ERA5-Land Surface Reanalysis (~9 km / 0.1 deg)"
            res = "0.1 deg x 0.1 deg (~9 km)"
        else:
            model = "ECMWF ERA5 Atmospheric Reanalysis (~31 km / 0.25 deg)"
            res = "0.25 deg x 0.25 deg (~31 km)"
        url = "https://cds.climate.copernicus.eu"
        gap_m = "ECMWF 4D-Var Data Assimilation & Multi-Source Synthesis"
        gap_s = "Copernicus Climate Change Service (C3S) Core Archive"
        cov = "1940-Present (Continuous Real-Time)"
        qual = "WMO / ECMWF Scientific Certified Climate Standard"
        citation = "Hersbach, H., et al. (2020). The ERA5 global reanalysis. Q.J.R. Meteorol. Soc."
    elif "open-meteo" in p or "era5" in p:
        p_src = "Open-Meteo Historical Weather API"
        if "land" in om_m.lower():
            model = "ECMWF ERA5-Land High-Resolution Reanalysis (~9 km / 0.1 deg)"
            res = "0.1 deg x 0.1 deg (~9 km)"
        elif "seamless" in om_m.lower():
            model = "ECMWF ERA5-Seamless Multi-Scale Reanalysis (9-25 km)"
            res = "0.1 - 0.25 deg (9-25 km)"
        else:
            model = "ECMWF ERA5 Atmospheric Reanalysis (~25 km / 0.25 deg)"
            res = "0.25 deg x 0.25 deg (~25 km)"
        url = "https://open-meteo.com/en/docs/historical-weather-api"
        gap_m = "ECMWF Continuous 4D-Var Data Assimilation"
        gap_s = "ECMWF IFS Cy41r2 Model Assimilation"
        cov = "1940-Present (Daily & Hourly)"
        qual = "ECMWF Operational Quality Controlled Reanalysis"
        citation = "Muñoz-Sabater, J., et al. (2021). ERA5-Land: A state-of-the-art global reanalysis dataset. ESSD."
    else:
        # Default NASA POWER API
        p_src = "NASA POWER API (LaRC Agroclimatology / MERRA-2)"
        if m in ("Solar Radiation", "UV Index", "Cloud Cover"):
            model = "NASA CERES FLASHFlux & CERES SYN1deg (~100 km / 1.0 deg)"
            res = "1.0 deg x 1.0 deg (~100 km)"
            citation = "Wielicki, B. A., et al. (1996). Clouds and the Earth's Radiant Energy System (CERES). BAMS."
        elif m == "Precipitation":
            model = "NASA MERRA-2 & GPCP Precipitation (~50 km / 0.5 deg)"
            res = "0.5 deg x 0.5 deg (~50 km)"
            citation = "Gelaro, R., et al. (2017). The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2). J. Climate."
        elif m == "Land Surface Temperature":
            model = "NASA MERRA-2 Skin Temp & MODIS LST (~50 km / 0.5 deg)"
            res = "0.5 deg x 0.5 deg (~50 km)"
            citation = "Wan, Z. (2014). New refinements and validation of the collection-6 MODIS LST product. RSE."
        else:
            model = "NASA GEOS-5 FP-IT / MERRA-2 Atmospheric Reanalysis (~50 km / 0.5 deg)"
            res = "0.5 deg x 0.5 deg (~50 km)"
            citation = "Gelaro, R., et al. (2017). The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2). J. Climate."
        url = "https://power.larc.nasa.gov"
        gap_m = "None (Pure Record)" if gap_method == "none" else "NASA Climatological Imputation"
        gap_s = "None" if gap_method == "none" else "NASA POWER Climatology Baseline"
        cov = "1981-Present (Active Real-Time)"
        qual = "Satellite & Reanalysis Assimilated (MERRA-2)"

    return {
        "primary_source": p_src,
        "model_used": model,
        "provider_url": url,
        "gap_fill_method": gap_m,
        "gap_fill_source": gap_s,
        "temporal_coverage": cov,
        "spatial_resolution": res,
        "quality_status": qual,
        "scientific_citation": citation
    }


def build_source_data_provenance_table(pts_or_results, modules, provider, om_model=None,
                                       gap_method="climatological", y0=1996, y1=2025,
                                       temporal="Monthly"):
    """
    Constructs full multi-sheet provenance data structures for export:
    Returns (prov_sheet, summary_sheet, ar_summary_sheet)
    """
    prov_header = [
        "Point_OID", "Station_ID", "Station_Name", "Country",
        "Latitude", "Longitude", "Elevation_m",
        "Climate_Module", "Primary_Data_Source", "Atmospheric_Model_Sensor",
        "Provider_URL", "Gap_Fill_Method_Applied", "Gap_Fill_Source",
        "Temporal_Coverage", "Spatial_Resolution", "Data_Quality_Status"
    ]

    prov_rows = []
    summary_rows = []
    ar_summary_rows = []

    ar_mod_names = {
        "Temperature": u"درجة الحرارة",
        "Land Surface Temperature": u"حرارة سطح الأرض",
        "Precipitation": u"التساقط والأمطار",
        "Sea Level Pressure": u"الضغط الجوي عند مستوى البحر",
        "Surface Pressure": u"الضغط الجوي السطحي",
        "Wind": u"الرياح (السرعة والاتجاه)",
        "Relative Humidity": u"الرطوبة النسبية",
        "Dew Point": u"نقطة الندى",
        "Solar Radiation": u"الإشعاع الشمسي",
        "UV Index": u"مؤشر الأشعة فوق البنفسجية",
        "Cloud Cover": u"الغطاء السحابي",
        "Thermal Comfort": u"الراحة الحرارية ومؤشر الحرارة",
        "Heat Index": u"مؤشر الحرارة",
        "Wind Chill": u"برودة الرياح",
        "Drought & Aridity": u"الجفاف والقحولة",
        "De Martonne Aridity": u"قرينة دي مارتون للجفاف",
        "UNEP Aridity": u"مؤشر برنامج الأمم المتحدة للجفاف",
        "Water Deficit": u"العجز المائي",
        "Dry Months": u"الشهور الجافة",
        "Trends & Anomalies": u"الاتجاهات والشذوذ المناخي",
        "Climate_Models": u"النماذج والتغيرات المناخية",
        "Evapotranspiration": u"البخر-نتح المحتمل"
    }

    sum_header = [
        "Module_ID", "Climate_Module", "Primary_Data_Source", "Core_Atmospheric_Model",
        "Provider_Website", "Effective_Coverage", "Spatial_Resolution",
        "Gap_Filling_Strategy", "Scientific_Citation"
    ]
    ar_sum_header = [
        u"رقم العنصر", u"العنصر المناخي", u"المصدر الرئيسي للبيانات", u"النموذج الجوي والمستشعر",
        u"موقع المصدر", u"الفترة الزمنية المغطاة", u"الدقة المكانية",
        u"طريقة ومصدر سد الفجوات", u"التوثيق والاعتماد العلمي"
    ]

    eff_modules = list(modules) if modules else ["Temperature"]
    for m_idx, m in enumerate(eff_modules):
        meta = get_element_source_metadata(m, provider, om_model, gap_method, y0, y1)
        sum_rows_item = [
            m_idx + 1, m, meta["primary_source"], meta["model_used"],
            meta["provider_url"], meta["temporal_coverage"], meta["spatial_resolution"],
            meta["gap_fill_method"] + " (" + meta["gap_fill_source"] + ")",
            meta["scientific_citation"]
        ]
        summary_rows.append(sum_rows_item)

        ar_name = ar_mod_names.get(m, m)
        ar_sum_item = [
            m_idx + 1, ar_name, meta["primary_source"], meta["model_used"],
            meta["provider_url"], meta["temporal_coverage"], meta["spatial_resolution"],
            meta["gap_fill_method"] + " (" + meta["gap_fill_source"] + ")",
            meta["scientific_citation"]
        ]
        ar_summary_rows.append(ar_sum_item)

    pts = pts_or_results or []
    for p_idx, p in enumerate(pts):
        oid = p.get("oid", p_idx + 1)
        sid = p.get("station_id") or p.get("Station_ID") or p.get("Source_ID") or ("PNT_%04d" % oid)
        sname = p.get("station_name") or p.get("Name") or p.get("Station_Nm") or ("Station %s" % sid)
        ctry = p.get("country") or p.get("Country") or p.get("Country_Nm") or "Regional"
        lat = round(float(p.get("lat", 0.0)), 4) if p.get("lat") is not None else 0.0
        lon = round(float(p.get("lon", 0.0)), 4) if p.get("lon") is not None else 0.0
        elev = round(float(p.get("elevation", p.get("Elev_m", 0.0))), 1) if (p.get("elevation") or p.get("Elev_m")) else 0.0

        for m in eff_modules:
            meta = get_element_source_metadata(m, provider, om_model, gap_method, y0, y1)
            prov_rows.append([
                oid, sid, sname, ctry,
                lat, lon, elev,
                m, meta["primary_source"], meta["model_used"],
                meta["provider_url"], meta["gap_fill_method"], meta["gap_fill_source"],
                meta["temporal_coverage"], meta["spatial_resolution"], meta["quality_status"]
            ])

    prov_sheet = ("Source_Data", prov_header, prov_rows, False)
    sum_sheet = ("Sources_Summary", sum_header, summary_rows, False)
    ar_sum_sheet = (u"ملخص_مصادر_البيانات", ar_sum_header, ar_summary_rows, True)

    return prov_sheet, sum_sheet, ar_sum_sheet


def export_source_data_folder(out_ws, pts_or_results, modules, provider, om_model=None,
                              gap_method="climatological", y0=1996, y1=2025,
                              temporal="Monthly", msg=None, warn=None):
    """
    Creates the dedicated 'Source Data' folder in the output workspace
    and populates it with:
    1. Climate_Data_Sources_Provenance.xls (Multi-sheet Excel workbook)
    2. Climate_Data_Sources_Provenance.csv (UTF-8 BOM CSV)
    3. README_Sources_Provenance.txt (English technical guide)
    4. README_مصادر_البيانات_والنماذج.txt (Arabic technical guide)
    """
    if not out_ws:
        return
    source_dir = os.path.join(out_ws, "Source Data")
    makedirs_ok(source_dir)

    prov_sheet, sum_sheet, ar_sum_sheet = build_source_data_provenance_table(
        pts_or_results, modules, provider, om_model, gap_method, y0, y1, temporal
    )

    # 1. Multi-sheet Excel workbook
    xls_path = os.path.join(source_dir, "Climate_Data_Sources_Provenance.xls")
    try:
        write_master_excel_workbook(xls_path, [prov_sheet, sum_sheet, ar_sum_sheet])
        if msg:
            msg("Source Data Excel: %s" % xls_path)
    except Exception as ex:
        if warn:
            warn("Source Data Excel export warning: %s" % ex)

    # 2. Universal UTF-8 BOM CSV
    csv_path = os.path.join(source_dir, "Climate_Data_Sources_Provenance.csv")
    try:
        write_csv(csv_path, prov_sheet[1], prov_sheet[2])
        if msg:
            msg("Source Data CSV: %s" % csv_path)
    except Exception as ex:
        if warn:
            warn("Source Data CSV export warning: %s" % ex)

    # 3. English Technical Guide
    txt_en_path = os.path.join(source_dir, "README_Sources_Provenance.txt")
    try:
        with io.open(txt_en_path, "w", encoding="utf-8") as fh:
            fh.write(u"=" * 80 + u"\n")
            fh.write(u"CLIMATE ATLAS DATA SOURCES & MODEL PROVENANCE SPECIFICATION\n")
            fh.write(u"=" * 80 + u"\n\n")
            fh.write(u"Primary Provider Selected: %s\n" % _excel_text(provider))
            fh.write(u"Atmospheric / Numerical Model: %s\n" % _excel_text(om_model or "Standard Native"))
            fh.write(u"Gap-Filling Methodology: %s\n" % _excel_text(gap_method))
            fh.write(u"Analysis Period: %s - %s (Temporal: %s)\n\n" % (y0, y1, temporal))
            fh.write(u"-" * 80 + u"\n")
            fh.write(u"ELEMENT-BY-ELEMENT SOURCES SUMMARY:\n")
            fh.write(u"-" * 80 + u"\n")
            for row in sum_sheet[2]:
                fh.write(u"[%02d] Element: %s\n" % (row[0], row[1]))
                fh.write(u"     • Primary Source    : %s\n" % row[2])
                fh.write(u"     • Atmospheric Model : %s\n" % row[3])
                fh.write(u"     • Official Website  : %s\n" % row[4])
                fh.write(u"     • Temporal Coverage : %s\n" % row[5])
                fh.write(u"     • Spatial Resolution: %s\n" % row[6])
                fh.write(u"     • Gap-Filling       : %s\n" % row[7])
                fh.write(u"     • Citation / Auth   : %s\n\n" % row[8])
            fh.write(u"=" * 80 + u"\n")
            fh.write(u"Developed by Ahmad Ibrahim (@ahmadibrahim4geo)\n")
    except Exception as ex_txt:
        if warn:
            warn("Source Data README EN warning: %s" % ex_txt)

    # 4. Arabic Technical Guide
    txt_ar_path = os.path.join(source_dir, u"README_مصادر_البيانات_والنماذج.txt")
    try:
        with io.open(txt_ar_path, "w", encoding="utf-8") as fh:
            fh.write(u"=" * 80 + u"\n")
            fh.write(u"توثيق مصادر البيانات والنماذج الجوية لأطلس المناخ الجغرافي\n")
            fh.write(u"=" * 80 + u"\n\n")
            fh.write(u"مصدر البيانات المختار: %s\n" % _excel_text(provider))
            fh.write(u"النموذج الجوي / العددي: %s\n" % _excel_text(om_model or "النموذج القياسي المعتمد"))
            fh.write(u"خوارزمية سد الفجوات: %s\n" % _excel_text(gap_method))
            fh.write(u"فترة الدراسة والتحليل: من %s إلى %s (التردد الزمني: %s)\n\n" % (y0, y1, temporal))
            fh.write(u"-" * 80 + u"\n")
            fh.write(u"ملخص المصادر والنماذج لكل عنصر مناخي:\n")
            fh.write(u"-" * 80 + u"\n")
            for row in ar_sum_sheet[2]:
                fh.write(u"[%02d] العنصر المناخي: %s\n" % (row[0], row[1]))
                fh.write(u"     • المصدر الرئيسي       : %s\n" % row[2])
                fh.write(u"     • النموذج الجوي / المستشعر: %s\n" % row[3])
                fh.write(u"     • البوابة الرسمية للمصدر  : %s\n" % row[4])
                fh.write(u"     • فترة التغطية الزمنية   : %s\n" % row[5])
                fh.write(u"     • الدقة المكانية         : %s\n" % row[6])
                fh.write(u"     • معالجة وسد الفجوات     : %s\n" % row[7])
                fh.write(u"     • التوثيق والاعتماد العلمي : %s\n\n" % row[8])
            fh.write(u"=" * 80 + u"\n")
            fh.write(u"إعداد وتطوير: م. أحمد إبراهيم (@ahmadibrahim4geo)\n")
    except Exception as ex_ar:
        if warn:
            warn("Source Data README AR warning: %s" % ex_ar)


# ---------------------------------------------------------------------------
# Pure-python climate core (no arcpy) — testable offline
# ---------------------------------------------------------------------------


def is_missing(v):
    """True if value is a NASA missing sentinel, None or NaN."""
    if v is None:
        return True
    try:
        f = float(v)
    except Exception:
        return True
    try:
        if math.isnan(f):
            return True
    except Exception:
        pass
    for s in MISSING_SENTINELS:
        if abs(f - s) < 1e-9:
            return True
    return False


def month_days(year, month):
    return calendar.monthrange(year, month)[1]


def safe_mean(values):
    vals = [float(v) for v in values if not is_missing(v)]
    if not vals:
        return None
    return sum(vals) / len(vals)


def safe_sum(values, expected=None, min_frac=0.75):
    """Sum of valid values, or None.

    expected: how many values a complete period should hold (e.g. days in
        month for daily->monthly precipitation sums). When given, returns
        None unless at least min_frac of them are valid -- otherwise a
        partial sum would silently under-report the total (a missing rainy
        month/day shrinks the annual total with no warning). Without
        expected, keeps the legacy behavior (sum of whatever is valid)."""
    vals = [float(v) for v in values if not is_missing(v)]
    if not vals:
        return None
    if expected:
        try:
            if len(vals) < float(expected) * float(min_frac):
                return None
        except Exception:
            pass
    return sum(vals)


def circular_mean_deg(angles):
    """Prevailing direction via vector mean. Returns 0-360 or None."""
    sins, coss = [], []
    for a in angles:
        if is_missing(a):
            continue
        try:
            r = math.radians(float(a) % 360.0)
        except Exception:
            continue
        sins.append(math.sin(r))
        coss.append(math.cos(r))
    if not sins:
        return None
    ms = sum(sins) / len(sins)
    mc = sum(coss) / len(coss)
    if abs(ms) < 1e-12 and abs(mc) < 1e-12:
        return None
    return math.degrees(math.atan2(ms, mc)) % 360.0


def group_monthly_by_calendar_month(monthly):
    """monthly: {(y,m): v} or {m: v} -> {m: [values]} valid only."""
    out = dict((m, []) for m in range(1, 13))
    for ym, v in monthly.items():
        if isinstance(ym, (tuple, list)):
            m = int(ym[1])
        else:
            m = int(ym)
        if 1 <= m <= 12 and not is_missing(v):
            try:
                out[m].append(float(v))
            except Exception:
                pass
    return out


def climat_monthly_means(monthly):
    """Mean of each calendar month across years -> {m: mean}."""
    g = group_monthly_by_calendar_month(monthly)
    res = {}
    for m, v in g.items():
        res[m] = sum(v) / len(v) if v else None
    return res


def seasonal_means_from_monthly(monthly):
    """Mean-type aggregation. Returns dict Annual/Winter/Spring/Summer/Autumn."""
    clim = climat_monthly_means(monthly)
    res = {}
    ann = [v for v in clim.values() if v is not None]
    res["Annual"] = sum(ann) / len(ann) if ann else None
    for season, months in SEASONS.items():
        vals = [clim[m] for m in months if clim.get(m) is not None]
        res[season] = sum(vals) / len(vals) if vals else None
    return res


def seasonal_totals_from_monthly_totals(monthly_totals, years):
    """Sum-type aggregation (precipitation)."""
    per_year_annual = []
    per_year_season = dict((s, []) for s in SEASONS)
    for y in years:
        avals = [monthly_totals.get((y, m)) for m in range(1, 13)]
        avals = [float(v) for v in avals if not is_missing(v)]
        if avals:
            per_year_annual.append(sum(avals))
        for season, months in SEASONS.items():
            svals = [monthly_totals.get((y, m)) for m in months]
            svals = [float(v) for v in svals if not is_missing(v)]
            if svals:
                per_year_season[season].append(sum(svals))

    def _m(x):
        return sum(x) / len(x) if x else None

    return {
        "Annual_Mean": _m(per_year_annual),
        "Annual_Grand": sum(per_year_annual) if per_year_annual else None,
        "Winter": _m(per_year_season["Winter"]),
        "Spring": _m(per_year_season["Spring"]),
        "Summer": _m(per_year_season["Summer"]),
        "Autumn": _m(per_year_season["Autumn"]),
    }


def monthly_precip_total_from_rate(rate_mm_day, year, month):
    if is_missing(rate_mm_day):
        return None
    return float(rate_mm_day) * month_days(year, month)


def solar_mj_to_kwh(mj):
    if is_missing(mj):
        return None
    return float(mj) / 3.6


def pressure_kpa_to_mbar(v, source_unit="auto"):
    """Convert pressure to mbar/hPa.

    source_unit: "kPa" forces x10, "hPa"/"mbar"/"mb" keeps as-is,
        "auto" (default, backward compatible): POWER PS/SLP are typically
        kPa (~80-105), so |v|<200 is treated as kPa. Prefer an explicit
        unit whenever the provider documents it."""
    if is_missing(v):
        return None
    f = float(v)
    if source_unit == "kPa":
        return f * 10.0
    if source_unit in ("hPa", "mbar", "mb"):
        return f
    if abs(f) < 200.0:
        return f * 10.0
    return f


def annual_temp_range(monthly_tmean):
    clim = climat_monthly_means(monthly_tmean)
    vals = [v for v in clim.values() if v is not None]
    if len(vals) < 2:
        return None
    return max(vals) - min(vals)


def daylength_hours(lat_deg, month):
    """Astronomical daylength (hours) for mid-month day at given latitude.

    Used only to convert NASA POWER 24h-mean UV to WHO noon-max estimate.
    Polar night -> 0.0, polar day -> 24.0."""
    try:
        _mid_doy = [15, 45, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]
        m = max(1, min(12, int(month)))
        _n = _mid_doy[m - 1]
        _decl = math.radians(-23.44 * math.cos(2.0 * math.pi * (_n + 10) / 365.0))
        _lat = math.radians(float(lat_deg))
        _cos_om = -math.tan(_lat) * math.tan(_decl)
        if _cos_om <= -1.0:
            return 24.0
        if _cos_om >= 1.0:
            return 0.0
        _omega_deg = math.degrees(math.acos(_cos_om))
        return 2.0 * _omega_deg / 15.0
    except Exception:
        return 12.0


def uv_mean24_to_noonmax(mean24, lat_deg, month, k_shape=0.435):
    """Convert NASA POWER 24h-mean UV to WHO noon-max estimate.

    NASA daily/monthly ALLSKY_SFC_UV_INDEX is the mean of 24 hourly values
    including night zeros (verified Cairo: noon 10.5 -> daily 2.66), while
    WHO UVI is the solar-noon maximum. mean24 = max * daylight * k / 24,
    with empirical clear-sky shape factor k~0.435 (Cairo Jul/Jan within ~6%).
    Returns None for missing input, 0.0 for polar night. Uncertainty ~10-15%.
    Open-Meteo uv_index_max (already a daily max) must NOT pass here."""
    if is_missing(mean24):
        return None
    try:
        f = float(mean24)
    except Exception:
        return None
    if f <= 0.0:
        return 0.0
    dl = daylength_hours(lat_deg, month)
    if dl is None or dl < 0.5:
        return 0.0
    if dl > 24.0:
        dl = 24.0
    try:
        return float(f) * 24.0 / (dl * float(k_shape))
    except Exception:
        return None


def monthly_range(monthly):
    """max - min of climatological monthly means (or None)."""
    clim = climat_monthly_means(monthly)
    vals = [v for v in clim.values() if v is not None]
    if len(vals) < 2:
        return None
    return max(vals) - min(vals)


def monthly_interannual_ranges(mdict):
    """Per-calendar-month max-min across years: {1..12: range or None}.

    Measures interannual variability inside one month (e.g. warmest vs coldest
    January on record). Needs >= 2 valid years for that month; opt-in only."""
    out = {}
    if not mdict:
        return dict((m, None) for m in range(1, 13))
    for m in range(1, 13):
        vals = []
        for ym, v in mdict.items():
            try:
                mm = ym[1] if isinstance(ym, (tuple, list)) else int(ym)
            except Exception:
                continue
            if int(mm) != m or is_missing(v):
                continue
            try:
                vals.append(float(v))
            except Exception:
                pass
        out[m] = (max(vals) - min(vals)) if len(vals) >= 2 else None
    return out


def heat_index_c(t_c, rh):
    """Rothfusz (NOAA) heat index in C from air temp C + RH %.

    Applied to climatological monthly means; below 26.7C (80F) the index
    equals air temperature. Returns None when inputs are missing."""
    if t_c is None or rh is None or is_missing(t_c) or is_missing(rh):
        return None
    t_c, rh = float(t_c), float(rh)
    if rh < 0.0:
        rh = 0.0
    if rh > 100.0:
        rh = 100.0
    t_f = t_c * 9.0 / 5.0 + 32.0
    if t_f < 80.0:
        return t_c
    hi = (-42.379 + 2.04901523 * t_f + 10.14333127 * rh - 0.22475541 * t_f * rh
          - 0.00683783 * t_f * t_f - 0.05481717 * rh * rh + 0.00122874 * t_f * t_f * rh
          + 0.00085282 * t_f * rh * rh - 0.00000199 * t_f * t_f * rh * rh)
    if rh < 13.0 and 80.0 <= t_f <= 112.0:
        hi -= ((13.0 - rh) / 4.0) * math.sqrt((17.0 - abs(t_f - 95.0)) / 17.0)
    elif rh > 85.0 and 80.0 <= t_f <= 87.0:
        hi += ((rh - 85.0) / 10.0) * ((87.0 - t_f) / 5.0)
    return (hi - 32.0) * 5.0 / 9.0


def humidex_c(t_c, rh):
    """Canadian Humidex (IH) in C from air temp C + RH %.

    Formula:
      e = 6.112 * (10.0 ** ((7.5 * t_c) / (237.7 + t_c))) * (rh / 100.0)
      humidex = t_c + (5.0 / 9.0) * (e - 10.0)
    Returns None when inputs are missing."""
    if t_c is None or rh is None or is_missing(t_c) or is_missing(rh):
        return None
    t_c, rh = float(t_c), float(rh)
    if rh < 0.0:
        rh = 0.0
    if rh > 100.0:
        rh = 100.0
    e = 6.112 * (10.0 ** ((7.5 * t_c) / (237.7 + t_c))) * (rh / 100.0)
    return t_c + (5.0 / 9.0) * (e - 10.0)


def wetbulb_stull_c(t_c, rh):
    """Psychrometric wet-bulb temperature in C (Stull 2011) from air temp C + RH %.

    Closed-form empirical fit, valid roughly for -20..50 C and RH 5..99%.
    Returns None when inputs are missing."""
    if t_c is None or rh is None or is_missing(t_c) or is_missing(rh):
        return None
    t_c, rh = float(t_c), float(rh)
    if rh < 0.0:
        rh = 0.0
    if rh > 100.0:
        rh = 100.0
    return (t_c * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(t_c + rh) - math.atan(rh - 1.676331)
            + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
            - 4.686035)


def wbgt_shade_c(t_c, rh):
    """Simplified outdoor-shade WBGT in C (ISO 7243, no solar load).

    WBGT = 0.7 * Tnwb + 0.3 * Ta with natural wet-bulb via Stull (2011).
    Needs only air temp C + RH %; wind/solar corrections (Liljegren) not applied.
    Returns None when inputs are missing."""
    if t_c is None or rh is None or is_missing(t_c) or is_missing(rh):
        return None
    tw = wetbulb_stull_c(t_c, rh)
    if tw is None:
        return None
    return 0.7 * tw + 0.3 * float(t_c)


def windchill_c(t_c, ws_ms):
    """Wind chill (felt cold) in C, Environment Canada / US NWS (2001) revision.

    WC = 13.12 + 0.6215*T - 11.37*V^0.16 + 0.3965*T*V^0.16
    with T in C and V (10-m wind) in km/h; ws_ms is given in m/s (WS10M
    native unit) and converted inside (x3.6).

    Valid per observation only when T <= 10C and V >= 4.8 km/h; otherwise
    returns air temperature itself (same convention as heat_index_c below
    its 26.7C threshold). Applied here to climatological monthly means as
    a screening signal -- desert night extremes are smoothed inside the
    monthly mean, so this understates peak cold stress (documented).
    Returns None when inputs are missing."""
    if t_c is None or ws_ms is None or is_missing(t_c) or is_missing(ws_ms):
        return None
    t_c = float(t_c)
    v_kmh = max(0.0, float(ws_ms)) * 3.6
    if t_c > 10.0 or v_kmh < 4.8:
        return t_c
    v_pow = v_kmh ** 0.16
    return 13.12 + 0.6215 * t_c - 11.37 * v_pow + 0.3965 * t_c * v_pow


def equal_interval_breaks(vmin, vmax, n=7):
    if vmin is None or vmax is None:
        return None
    if abs(vmax - vmin) < 1e-12:
        eps = abs(vmax) * 0.01 if vmax != 0 else 0.01
        vmin, vmax = vmin - eps, vmax + eps
    w = (vmax - vmin) / float(n)
    return [vmin + w * i for i in range(n + 1)]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def interpolate_colors(hex_list, n):
    """Interpolate a list of hex color codes to exactly n hex colors."""
    if not hex_list:
        return []
    if n <= 1:
        return [hex_list[0]]
    if n == len(hex_list):
        return list(hex_list)
    rgb_list = [hex_to_rgb(h) for h in hex_list]
    m = len(rgb_list)
    result = []
    for i in range(n):
        t = float(i) / float(n - 1) * float(m - 1)
        idx = int(t)
        frac = t - idx
        if idx >= m - 1:
            r, g, b = rgb_list[-1]
        else:
            r1, g1, b1 = rgb_list[idx]
            r2, g2, b2 = rgb_list[idx + 1]
            r = int(round(r1 + (r2 - r1) * frac))
            g = int(round(g1 + (g2 - g1) * frac))
            b = int(round(b1 + (b2 - b1) * frac))
        result.append("#%02X%02X%02X" % (r, g, b))
    return result


def tolerance_meters(value_text):
    """Parse a GPLinearUnit text like '1000 Meters' into metres (float).

    Unknown/empty/zero values return 0.0 (= tolerance OFF)."""
    if value_text is None:
        return 0.0
    parts = str(value_text).strip().split()
    if not parts:
        return 0.0
    try:
        v = float(parts[0])
    except Exception:
        return 0.0
    unit = " ".join(parts[1:]).strip().lower() if len(parts) > 1 else "meters"
    factors = {"meter": 1.0, "meters": 1.0, "metre": 1.0, "metres": 1.0, "m": 1.0,
               "kilometer": 1000.0, "kilometers": 1000.0, "kilometre": 1000.0,
               "kilometres": 1000.0, "km": 1000.0,
               "foot": 0.3048, "feet": 0.3048, "ft": 0.3048,
               "mile": 1609.34, "miles": 1609.34, "mi": 1609.34,
               "decimaldegree": 111320.0, "decimaldegrees": 111320.0,
               "degree": 111320.0, "degrees": 111320.0, "dd": 111320.0}
    return v * factors.get(unit, 1.0)


def parse_gp_date(val):
    """Parse a date parameter value or date string into a datetime.date object.

    Handles datetime.datetime, datetime.date, and various string formats
    including DD/MM/YYYY, D/M/YYYY, YYYY-MM-DD, YYYY/MM/DD, etc."""
    if val is None:
        return None
    if hasattr(val, "year") and hasattr(val, "month") and hasattr(val, "day"):
        return _dt.date(val.year, val.month, val.day)
    s = str(val).strip()
    if not s:
        return None
    s_date = s.split()[0] if " " in s else s
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y", "%Y%m%d"):
        try:
            return _dt.datetime.strptime(s_date, fmt).date()
        except Exception:
            pass
    parts = s_date.replace("-", "/").replace(".", "/").split("/")
    if len(parts) == 3:
        try:
            p1, p2, p3 = int(parts[0]), int(parts[1]), int(parts[2])
            if p3 > 1000:
                return _dt.date(p3, p2, p1)
            elif p1 > 1000:
                return _dt.date(p1, p2, p3)
        except Exception:
            pass
    return None


def launch_calendar_picker(initial_start=None, initial_end=None):
    """Launch the smooth visual calendar dialog, with subprocess or in-process fallback."""
    import subprocess
    script_path = os.path.join(_this_dir, "utils", "calendar_dialog.py")
    if os.path.isfile(script_path):
        try:
            py_exe = sys.executable or "python.exe"
            cmd = [py_exe, script_path, "--start", str(initial_start or "01/01/2024"), "--end", str(initial_end or "31/12/2024")]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            if isinstance(out, bytes):
                try:
                    out = out.decode("utf-8", errors="replace")
                except Exception:
                    out = ""
            if out and "{" in out:
                data = json.loads(out[out.find("{"):out.rfind("}") + 1])
                return data
        except Exception:
            pass
    try:
        from utils.calendar_dialog import open_calendar_picker
        return open_calendar_picker(initial_start, initial_end)
    except Exception:
        return {"applied": False}


def safe_project_fc(in_fc, out_sr, work_gdb, tag, warn):
    """Project in_fc into work_gdb/tmp_<tag> and return the new path.

    ArcMap 10.8 cannot Project into the in_memory workspace (ERROR 000944),
    so projection always targets a real Feature Class. On failure the input
    is returned unchanged (caller keeps the input SR)."""
    out_fc = os.path.join(work_gdb, "tmp_" + tag)
    try:
        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)
    except Exception:
        pass
    try:
        arcpy.management.Project(in_fc, out_fc, out_sr)
        return out_fc
    except Exception as ex:
        try:
            warn("Projection to output SR failed (%s); keeping input SR." % ex)
        except Exception:
            pass
        return in_fc


def ensure_mask_fc(mask, mask_orig, maskp, out_sr, msg, warn):
    """Returns a usable mask feature path, rebuilding it if necessary.

    The reprojected mask (maskp.shp inside _scratch) is reused by every
    element plus wind vectors. If it went missing (e.g. deleted by a scratch
    purge), it is rebuilt from the original mask path. Returns None when no
    mask was requested or when rebuild is impossible (caller must then skip
    raster work instead of publishing unclipped surfaces)."""
    try:
        if mask and arcpy.Exists(mask):
            return mask
    except Exception:
        pass
    try:
        if mask_orig and arcpy.Exists(mask_orig) and maskp:
            try:
                if arcpy.Exists(maskp):
                    arcpy.management.Delete(maskp)
            except Exception:
                pass
            arcpy.management.Project(mask_orig, maskp, out_sr)
            msg("Mask restored to output SR.")
            return maskp
    except Exception as ex:
        warn("Mask restore failed (%s)." % ex)
    return None


def thin_points_tolerance(pts, tol_m):
    """Greedy order-preserving thinning: keep the first point of each cluster.

    pts: [{"oid":..,"lat":..,"lon":..}]. Distances use an equirectangular
    approximation (metres) adequate for a thinning threshold. Returns
    (kept_list, dropped_oid_list)."""
    if tol_m is None or tol_m <= 0 or len(pts) < 2:
        return list(pts), []
    kept, dropped = [], []
    tol2 = tol_m * tol_m
    for p in pts:
        dup = False
        for q in kept:
            mlat = math.radians((p["lat"] + q["lat"]) / 2.0)
            dx = (p["lon"] - q["lon"]) * 111320.0 * math.cos(mlat)
            dy = (p["lat"] - q["lat"]) * 111320.0
            if dx * dx + dy * dy < tol2:
                dup = True
                break
        if dup:
            dropped.append(p["oid"])
        else:
            kept.append(p)
    return kept, dropped


def compute_thermal_stress_fields(c_t, c_rh):
    """Shared Heat Index / Humidex / WBGT aggregation (single source of truth).

    c_t / c_rh: climatological monthly means {1..12: value} (T in C, RH in %).
    Used by both compute_temperature_fields (Temperature module) and the
    Climate_Models branch of compute_point_fields (previously copy-pasted).
    Returns HI_Annual/Summer/Winter_Mean, HI_Annual_Range, WBGT_Summer_Mean.
    The 12 HI_<Month>_Mean values use Rothfusz year-round (documented
    winter caveat: the seasonal HI_Winter_Mean uses Humidex instead); they
    are always computed but only published when the opt-in 'extended HI
    months' toggle is enabled (mirrors compute_winter_chill_fields)."""
    c_t = c_t or {}
    c_rh = c_rh or {}
    hi_m = dict((m, heat_index_c(c_t.get(m), c_rh.get(m))) for m in range(1, 13))
    hi_vals = [v for v in hi_m.values() if v is not None]
    hi_sum = [hi_m[m] for m in SEASONS["Summer"] if hi_m.get(m) is not None]
    hi_spr = [hi_m[m] for m in SEASONS["Spring"] if hi_m.get(m) is not None]
    hi_aut = [hi_m[m] for m in SEASONS["Autumn"] if hi_m.get(m) is not None]
    hi_win = [humidex_c(c_t.get(m), c_rh.get(m)) for m in SEASONS["Winter"]
              if c_t.get(m) is not None and c_rh.get(m) is not None]
    hi_win_vals = [v for v in hi_win if v is not None]
    wb_m = dict((m, wbgt_shade_c(c_t.get(m), c_rh.get(m))) for m in range(1, 13))
    wb_sum = [wb_m[m] for m in SEASONS["Summer"] if wb_m.get(m) is not None]
    _seas = []
    for _s in (hi_spr, hi_sum, hi_aut, hi_win_vals):
        if _s:
            _seas.append(sum(_s) / len(_s))
    return {
        "HI_Annual_Mean": sum(hi_vals) / len(hi_vals) if hi_vals else None,
        "HI_Summer_Mean": sum(hi_sum) / len(hi_sum) if hi_sum else None,
        "HI_Spring_Mean": sum(hi_spr) / len(hi_spr) if hi_spr else None,
        "HI_Autumn_Mean": sum(hi_aut) / len(hi_aut) if hi_aut else None,
        "HI_Winter_Mean": sum(hi_win_vals) / len(hi_win_vals) if hi_win_vals else None,
        "HI_January_Mean": round(hi_m.get(1), 2) if hi_m.get(1) is not None else None,
        "HI_February_Mean": round(hi_m.get(2), 2) if hi_m.get(2) is not None else None,
        "HI_March_Mean": round(hi_m.get(3), 2) if hi_m.get(3) is not None else None,
        "HI_April_Mean": round(hi_m.get(4), 2) if hi_m.get(4) is not None else None,
        "HI_May_Mean": round(hi_m.get(5), 2) if hi_m.get(5) is not None else None,
        "HI_June_Mean": round(hi_m.get(6), 2) if hi_m.get(6) is not None else None,
        "HI_July_Mean": round(hi_m.get(7), 2) if hi_m.get(7) is not None else None,
        "HI_August_Mean": round(hi_m.get(8), 2) if hi_m.get(8) is not None else None,
        "HI_September_Mean": round(hi_m.get(9), 2) if hi_m.get(9) is not None else None,
        "HI_October_Mean": round(hi_m.get(10), 2) if hi_m.get(10) is not None else None,
        "HI_November_Mean": round(hi_m.get(11), 2) if hi_m.get(11) is not None else None,
        "HI_December_Mean": round(hi_m.get(12), 2) if hi_m.get(12) is not None else None,
        "HI_Annual_Range": (max(hi_vals) - min(hi_vals)) if len(hi_vals) >= 2 else None,
        "WBGT_Summer_Mean": sum(wb_sum) / len(wb_sum) if wb_sum else None,
    }


def compute_winter_chill_fields(c_t, c_ws):
    """Shared Wind Chill aggregation (single source of truth).

    c_t / c_ws: climatological monthly means {1..12: value} (T in C,
    10-m wind speed in m/s). Monthly WC via windchill_c(); winter = DJF
    mean, annual = 12-month mean; spring/summer/autumn means are also
    returned (same equation) but only published when the opt-in
    'extended WC seasons' toggle is enabled (cold-summer regions).
    Months missing T or wind are skipped; None when no valid month. Used
    by the Climate_Models branch of compute_point_fields (mirrors
    compute_thermal_stress_fields)."""
    c_t = c_t or {}
    c_ws = c_ws or {}
    wc_m = dict((m, windchill_c(c_t.get(m), c_ws.get(m))) for m in range(1, 13))
    wc_vals = [v for v in wc_m.values() if v is not None]
    wc_win = [wc_m[m] for m in SEASONS["Winter"] if wc_m.get(m) is not None]
    wc_spr = [wc_m[m] for m in SEASONS["Spring"] if wc_m.get(m) is not None]
    wc_sum = [wc_m[m] for m in SEASONS["Summer"] if wc_m.get(m) is not None]
    wc_aut = [wc_m[m] for m in SEASONS["Autumn"] if wc_m.get(m) is not None]
    _wseas = []
    for _s in (wc_spr, wc_sum, wc_aut, wc_win):
        if _s:
            _wseas.append(sum(_s) / len(_s))
    _months_en = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
    out = {
        "WC_Winter_Mean": sum(wc_win) / len(wc_win) if wc_win else None,
        "WC_Spring_Mean": sum(wc_spr) / len(wc_spr) if wc_spr else None,
        "WC_Summer_Mean": sum(wc_sum) / len(wc_sum) if wc_sum else None,
        "WC_Autumn_Mean": sum(wc_aut) / len(wc_aut) if wc_aut else None,
        "WC_Annual_Mean": sum(wc_vals) / len(wc_vals) if wc_vals else None,
        "WC_Annual_Range": (max(wc_vals) - min(wc_vals)) if len(wc_vals) >= 2 else None,
    }
    for _mi, _mn in enumerate(_months_en, 1):
        out["WC_%s_Mean" % _mn] = round(wc_m.get(_mi), 2) if wc_m.get(_mi) is not None else None
    return out


# WMO climate normal used as the anomaly baseline (fixed, documented).
BASELINE_YEARS = list(range(1991, 2021))
BASELINE_MIN_YEARS = 20   # baseline usable when >=20 of the 30 normal years are complete
RECENT_WINDOW = 10        # anomaly "recent" = last 10 complete years
RECENT_MIN_YEARS = 5
TREND_MIN_YEARS = 8       # least-squares trend needs >=8 complete annual values


def _complete_annual_values(monthly, kind="mean"):
    """Per-year annual value over complete years only (12/12 valid months).

    kind "mean" -> annual mean (temperature-like); "sum" -> annual total
    (precipitation-like). Partial edge years are skipped, never infilled.
    Returns {year: value}."""
    out = {}
    if not monthly:
        return out
    years = sorted(set(ym[0] for ym in monthly))
    for y in years:
        vals = [monthly.get((y, m)) for m in range(1, 13)]
        vals = [float(v) for v in vals if not is_missing(v)]
        if len(vals) < 12:
            continue
        out[y] = sum(vals) / 12.0 if kind == "mean" else sum(vals)
    return out


def _complete_season_values(monthly, season, kind="mean"):
    """Per-year seasonal value over complete seasons only (3/3 valid months,
    same-year-December DJF convention as the rest of the atlas)."""
    out = {}
    if not monthly:
        return out
    months = SEASONS[season]
    years = sorted(set(ym[0] for ym in monthly))
    for y in years:
        vals = [monthly.get((y, m)) for m in months]
        vals = [float(v) for v in vals if not is_missing(v)]
        if len(vals) < 3:
            continue
        out[y] = sum(vals) / 3.0 if kind == "mean" else sum(vals)
    return out


def _complete_month_values(monthly, month):
    """Per-year values of a single calendar month (1-12) over valid years.

    Returns {year: value} skipping years where that month is missing.
    Used for monthly anomaly (recent vs WMO baseline) and monthly OLS trend."""
    out = {}
    if not monthly:
        return out
    for (y, m), v in monthly.items():
        if m == month and not is_missing(v):
            out[y] = float(v)
    return out


def _lin_trend_per_decade(year_vals, min_n=TREND_MIN_YEARS):
    """Least-squares slope of annual values vs year, x10 = change per decade.
    Returns None when fewer than min_n complete years exist."""
    ys = sorted(year_vals)
    if len(ys) < min_n:
        return None
    xs = [float(y) for y in ys]
    vs = [float(year_vals[y]) for y in ys]
    mx = sum(xs) / len(xs)
    mv = sum(vs) / len(vs)
    den = sum((x - mx) ** 2 for x in xs)
    if den < 1e-12:
        return None
    return 10.0 * sum((x - mx) * (v - mv) for x, v in zip(xs, vs)) / den


def _recent_minus_baseline(year_vals):
    """(recent_mean, baseline_mean) of annual values, or (None, None).

    Baseline = WMO normal 1991-2020 (needs >=20 complete years);
    recent = last 10 complete years (needs >=5). Overlap between the two
    windows is allowed and documented (short records)."""
    base = [y for y in BASELINE_YEARS if y in year_vals]
    if len(base) < BASELINE_MIN_YEARS:
        return None, None
    recent_ys = sorted(year_vals)[-RECENT_WINDOW:]
    if len(recent_ys) < RECENT_MIN_YEARS:
        return None, None
    b = sum(float(year_vals[y]) for y in base) / len(base)
    r = sum(float(year_vals[y]) for y in recent_ys) / len(recent_ys)
    return r, b


def compute_trend_anomaly_fields(m_tmean, m_precip_totals):
    """Climate change signals from multi-year monthly series (no extra fetch).

    m_tmean: {(y,m): C}; m_precip_totals: {(y,m): mm/month total}.
    Returns 9 core fields (None-filled when data coverage is insufficient):
    - T_Annual_Trend_Decade / R_Annual_Trend_Decade: least-squares change per decade.
    - T_Annual_Anom/Winter/Summer (C) and R_Annual_Anom/Winter (mm + %):
      recent (last 10 complete years) minus WMO 1991-2020 baseline.
      Percent anomalies are None when the baseline mean is <5 mm
      (hyper-arid division guard).
    - Seasonal complements: T_Anom_Spring/Autumn, R_Anom_Spring/Summer/Autumn
      (+Pct), per-season OLS trends T_<Season>_Trend_Decade/R_<Season>_Trend_Decade.
    Plus monthly fields following the *_January_Mean naming pattern:
    - T_Anom_<Month> (C), R_Anom_<Month> (mm), R_Anom_<Month>_Pct (%),
      T_<Month>_Trend_Decade (C/decade), R_<Month>_Trend_Decade (mm/decade)."""
    t_ann = _complete_annual_values(m_tmean, "mean")
    p_ann = _complete_annual_values(m_precip_totals, "sum")
    t_win = _complete_season_values(m_tmean, "Winter", "mean")
    t_spr = _complete_season_values(m_tmean, "Spring", "mean")
    t_sum = _complete_season_values(m_tmean, "Summer", "mean")
    t_aut = _complete_season_values(m_tmean, "Autumn", "mean")
    p_win = _complete_season_values(m_precip_totals, "Winter", "sum")
    p_spr = _complete_season_values(m_precip_totals, "Spring", "sum")
    p_sum = _complete_season_values(m_precip_totals, "Summer", "sum")
    p_aut = _complete_season_values(m_precip_totals, "Autumn", "sum")

    t_trend = _lin_trend_per_decade(t_ann)
    r_trend = _lin_trend_per_decade(p_ann)

    r_t_ann, b_t_ann = _recent_minus_baseline(t_ann)
    r_t_win, b_t_win = _recent_minus_baseline(t_win)
    r_t_spr, b_t_spr = _recent_minus_baseline(t_spr)
    r_t_sum, b_t_sum = _recent_minus_baseline(t_sum)
    r_t_aut, b_t_aut = _recent_minus_baseline(t_aut)
    r_p_ann, b_p_ann = _recent_minus_baseline(p_ann)
    r_p_win, b_p_win = _recent_minus_baseline(p_win)
    r_p_spr, b_p_spr = _recent_minus_baseline(p_spr)
    r_p_sum, b_p_sum = _recent_minus_baseline(p_sum)
    r_p_aut, b_p_aut = _recent_minus_baseline(p_aut)

    def _pct(r, b):
        if r is None or b is None or abs(b) < 5.0:
            return None
        return (r - b) / abs(b) * 100.0

    out = {
        "T_Annual_Trend_Decade": round(t_trend, 3) if t_trend is not None else None,
        "R_Annual_Trend_Decade": round(r_trend, 2) if r_trend is not None else None,
        "T_Annual_Anom": round(r_t_ann - b_t_ann, 2) if r_t_ann is not None else None,
        "T_Anom_Winter": round(r_t_win - b_t_win, 2) if r_t_win is not None else None,
        "T_Anom_Spring": round(r_t_spr - b_t_spr, 2) if r_t_spr is not None else None,
        "T_Anom_Summer": round(r_t_sum - b_t_sum, 2) if r_t_sum is not None else None,
        "T_Anom_Autumn": round(r_t_aut - b_t_aut, 2) if r_t_aut is not None else None,
        "R_Annual_Anom": round(r_p_ann - b_p_ann, 1) if r_p_ann is not None else None,
        "R_Annual_Anom_Pct": round(_pct(r_p_ann, b_p_ann), 1) if _pct(r_p_ann, b_p_ann) is not None else None,
        "R_Anom_Winter": round(r_p_win - b_p_win, 1) if r_p_win is not None else None,
        "R_Anom_Winter_Pct": round(_pct(r_p_win, b_p_win), 1) if _pct(r_p_win, b_p_win) is not None else None,
        "R_Anom_Spring": round(r_p_spr - b_p_spr, 1) if r_p_spr is not None else None,
        "R_Anom_Spring_Pct": round(_pct(r_p_spr, b_p_spr), 1) if _pct(r_p_spr, b_p_spr) is not None else None,
        "R_Anom_Summer": round(r_p_sum - b_p_sum, 1) if r_p_sum is not None else None,
        "R_Anom_Summer_Pct": round(_pct(r_p_sum, b_p_sum), 1) if _pct(r_p_sum, b_p_sum) is not None else None,
        "R_Anom_Autumn": round(r_p_aut - b_p_aut, 1) if r_p_aut is not None else None,
        "R_Anom_Autumn_Pct": round(_pct(r_p_aut, b_p_aut), 1) if _pct(r_p_aut, b_p_aut) is not None else None,
    }
    # --- Per-season OLS trends (same seasons as the seasonal means) ---
    for _se, _ts, _ps in (("Winter", t_win, p_win), ("Spring", t_spr, p_spr),
                          ("Summer", t_sum, p_sum), ("Autumn", t_aut, p_aut)):
        _ttr = _lin_trend_per_decade(_ts)
        _ptr = _lin_trend_per_decade(_ps)
        out["T_%s_Trend_Decade" % _se] = round(_ttr, 3) if _ttr is not None else None
        out["R_%s_Trend_Decade" % _se] = round(_ptr, 2) if _ptr is not None else None
    # --- Monthly anomaly & trend (same *_<Month> naming pattern as means) ---
    for _mi, _mn in enumerate(MONTH_NAMES_EN, 1):
        _tm = _complete_month_values(m_tmean, _mi)
        _pm = _complete_month_values(m_precip_totals, _mi)
        _t_tr = _lin_trend_per_decade(_tm)
        _p_tr = _lin_trend_per_decade(_pm)
        _rt, _bt = _recent_minus_baseline(_tm)
        _rp, _bp = _recent_minus_baseline(_pm)
        out["T_Anom_%s" % _mn] = round(_rt - _bt, 2) if _rt is not None else None
        out["R_Anom_%s" % _mn] = round(_rp - _bp, 1) if _rp is not None else None
        _pp = _pct(_rp, _bp)
        out["R_Anom_%s_Pct" % _mn] = round(_pp, 1) if _pp is not None else None
        out["T_%s_Trend_Decade" % _mn] = round(_t_tr, 3) if _t_tr is not None else None
        out["R_%s_Trend_Decade" % _mn] = round(_p_tr, 2) if _p_tr is not None else None
    # --- General-monthly aggregates (same *_Month_Mean pattern as the means):
    # mean of the 12 valid monthly anomaly/trend values. Linearity makes
    # T_Anom_Month == T_Annual_Anom and R_Anom_Month == R_Annual_Anom / 12
    # when coverage is complete; the mean-of-valid form stays robust otherwise.
    def _mmean(vals):
        _v = [float(x) for x in vals if x is not None]
        return sum(_v) / len(_v) if _v else None
    _a = _mmean([out.get("T_Anom_%s" % _mn) for _mn in MONTH_NAMES_EN])
    out["T_Anom_Month"] = round(_a, 2) if _a is not None else None
    _a = _mmean([out.get("R_Anom_%s" % _mn) for _mn in MONTH_NAMES_EN])
    out["R_Anom_Month"] = round(_a, 1) if _a is not None else None
    _a = _mmean([out.get("R_Anom_%s_Pct" % _mn) for _mn in MONTH_NAMES_EN])
    out["R_Anom_Month_Pct"] = round(_a, 1) if _a is not None else None
    _a = _mmean([out.get("T_%s_Trend_Decade" % _mn) for _mn in MONTH_NAMES_EN])
    out["T_Month_Trend_Decade"] = round(_a, 3) if _a is not None else None
    _a = _mmean([out.get("R_%s_Trend_Decade" % _mn) for _mn in MONTH_NAMES_EN])
    out["R_Month_Trend_Decade"] = round(_a, 2) if _a is not None else None
    return out


def compute_temperature_fields(m_tmean, m_tmax, m_tmin, m_rh=None, m_td=None):
    """m_*: {(y,m): value C (RH in %)}. Returns dict of new T_*/HI_*/Td_* fields."""
    s_mean = seasonal_means_from_monthly(m_tmean)
    clim = climat_monthly_means(m_tmean)
    s_max = seasonal_means_from_monthly(m_tmax)
    s_min = seasonal_means_from_monthly(m_tmin)
    sum_max = [clim.get(m) for m in SEASONS["Summer"] if clim.get(m) is not None]
    win_min = [clim.get(m) for m in SEASONS["Winter"] if clim.get(m) is not None]
    clim_rh = climat_monthly_means(m_rh or {})
    _ts = compute_thermal_stress_fields(clim, clim_rh)
    s_td = seasonal_means_from_monthly(m_td or {})
    out = {
        "T_Annual_Mean": s_mean["Annual"],
        "T_Winter_Mean": s_mean["Winter"],
        "T_Spring_Mean": s_mean["Spring"],
        "T_Summer_Mean": s_mean["Summer"],
        "T_Autumn_Mean": s_mean["Autumn"],
        "T_Annual_Range": annual_temp_range(m_tmean),
        "T_Max_Summer_Month_Mean": max(sum_max) if sum_max else None,
        "T_Min_Winter_Month_Mean": min(win_min) if win_min else None,
        "T_Annual_Max_Mean": s_max["Annual"],
        "T_Annual_Min_Mean": s_min["Annual"],
        "HI_Annual_Mean": _ts["HI_Annual_Mean"],
        "HI_Summer_Mean": _ts["HI_Summer_Mean"],
        "HI_Spring_Mean": _ts["HI_Spring_Mean"],
        "HI_Autumn_Mean": _ts["HI_Autumn_Mean"],
        "HI_Winter_Mean": _ts["HI_Winter_Mean"],
        "HI_Annual_Range": _ts["HI_Annual_Range"],
        "WBGT_Summer_Mean": _ts["WBGT_Summer_Mean"],
        "Td_Annual_Mean": s_td["Annual"],
        "Td_Summer_Mean": s_td["Summer"],
        "Td_Winter_Mean": s_td["Winter"],
    }
    _months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for m_idx, m_name in enumerate(_months_en, 1):
        out["T_%s_Mean" % m_name] = round(clim.get(m_idx), 2) if clim.get(m_idx) is not None else None
    return out


def compute_wind_fields(m_spd, m_dir):
    """Circular means for direction, arithmetic for speed."""
    s_spd = seasonal_means_from_monthly(m_spd)
    clim_spd = climat_monthly_means(m_spd)
    spd_vals = [v for v in clim_spd.values() if v is not None]
    out = {
        "W_Spd_Annual_Mean": s_spd["Annual"],
        "W_Spd_Winter_Mean": s_spd["Winter"],
        "W_Spd_Spring_Mean": s_spd["Spring"],
        "W_Spd_Summer_Mean": s_spd["Summer"],
        "W_Spd_Autumn_Mean": s_spd["Autumn"],
        "W_Spd_Annual_Max_Month": max(spd_vals) if spd_vals else None,
        "W_Spd_Annual_Min_Month": min(spd_vals) if spd_vals else None,
        "W_Spd_Annual_Range": (max(spd_vals) - min(spd_vals)) if len(spd_vals) >= 2 else None,
    }
    _suffix = {"Winter": "Winter", "Spring": "Spring", "Summer": "Summer", "Autumn": "Autumn"}
    for season in SEASONS:
        months = SEASONS[season]
        vals = [v for ym, v in m_dir.items() if ym[1] in months and not is_missing(v)]
        out["W_Dir_" + _suffix[season] + "_Mean"] = circular_mean_deg(vals)
    allv = [v for v in m_dir.values() if not is_missing(v)]
    out["W_Dir_Annual_Mean"] = circular_mean_deg(allv)
    _months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for m_idx, m_name in enumerate(_months_en, 1):
        out["W_Spd_%s_Mean" % m_name] = round(clim_spd.get(m_idx), 2) if clim_spd.get(m_idx) is not None else None
        m_vals = [v for ym, v in m_dir.items() if ym[1] == m_idx and not is_missing(v)]
        out["W_Dir_%s_Mean" % m_name] = circular_mean_deg(m_vals)
    return out


def compute_solar_fields(m_sol_mj, years):
    """m_sol: {(y,m): MJ/m2/day monthly rate}. Returns kWh fields."""
    daily_kwh = {}
    for ym, v in m_sol_mj.items():
        k = solar_mj_to_kwh(v)
        if k is not None:
            daily_kwh[ym] = k
    s = seasonal_means_from_monthly(daily_kwh)
    per_year = []
    for y in years:
        tot = 0.0
        ok = False
        for m in range(1, 13):
            v = daily_kwh.get((y, m))
            if v is not None:
                tot += float(v) * month_days(y, m)
                ok = True
        if ok:
            per_year.append(tot)
    total = sum(per_year) / len(per_year) if per_year else None
    out = {
        "Sol_Annual_Mean": s["Annual"],
        "Sol_Annual_Total": total,
        "Sol_Winter_Mean": s["Winter"],
        "Sol_Spring_Mean": s["Spring"],
        "Sol_Summer_Mean": s["Summer"],
        "Sol_Autumn_Mean": s["Autumn"],
        "Sol_Annual_Range": monthly_range(daily_kwh),
    }
    _months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for m_idx, m_name in enumerate(_months_en, 1):
        m_vals = [v for ym, v in daily_kwh.items() if ym[1] == m_idx and v is not None]
        out["Sol_%s_Mean" % m_name] = round(sum(m_vals) / len(m_vals), 2) if m_vals else None
    return out


def extraterrestrial_radiation_ra(lat_deg, month):
    """Computes extraterrestrial solar radiation Ra in mm/day equivalent for a given month (FAO-56 standard)."""
    mid_days = [15, 45, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]
    m_idx = max(1, min(12, int(month)))
    J = mid_days[m_idx - 1]
    phi = math.radians(float(lat_deg))
    delta = 0.409 * math.sin((2.0 * math.pi * J / 365.0) - 1.39)
    dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * J / 365.0)
    tan_val = -math.tan(phi) * math.tan(delta)
    if tan_val >= 1.0:
        omega_s = 0.0
    elif tan_val <= -1.0:
        omega_s = math.pi
    else:
        omega_s = math.acos(tan_val)
    Gsc = 0.0820
    ra_mj = ((24.0 * 60.0) / math.pi) * Gsc * dr * (
        omega_s * math.sin(phi) * math.sin(delta) +
        math.cos(phi) * math.cos(delta) * math.sin(omega_s)
    )
    return max(0.0, 0.408 * ra_mj)


def compute_drought_fields(m_tmean, m_tmax, m_tmin, m_precip, lat=0.0):
    """Computes annual drought and aridity indicators:
    - DM_Aridity_Annual: De Martonne Aridity Index = P / (T + 10)
    - PET_Hargreaves_Annual: Annual Potential Evapotranspiration (Hargreaves-Samani, mm/year)
    - UNEP_Aridity_Annual: UNEP Aridity Index = P / PET
    - Water_Deficit_Annual: Annual Climatic Water Balance = P - PET (mm/year)
    - Dry_Months_Count: Count of biologically dry months where P_month < 2 * T_month"""
    c_tmean = climat_monthly_means(m_tmean)
    c_tmax = climat_monthly_means(m_tmax)
    c_tmin = climat_monthly_means(m_tmin)
    c_precip = climat_monthly_means(m_precip)

    # No single year exists at climatological scale, so February uses the
    # long-term average month length (28.25 days) instead of a fixed 28 --
    # otherwise every leap-day's PET is silently dropped.
    days_in_m = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly_pet = []
    monthly_p = []
    monthly_t = []
    dry_count = 0

    # Total input absence must NOT yield plausible-looking numbers from the
    # per-month fallbacks below (t=20C, p=0 would fake a hyper-arid site).
    _has_any_input = any(
        c_tmean.get(m) is not None or c_tmax.get(m) is not None
        or c_tmin.get(m) is not None or c_precip.get(m) is not None
        for m in range(1, 13)
    )
    if not _has_any_input:
        return {
            "DM_Aridity_Annual": None,
            "PET_Hargreaves_Annual": None,
            "UNEP_Aridity_Annual": None,
            "Water_Deficit_Annual": None,
            "Dry_Months_Count": None,
        }

    for m in range(1, 13):
        t = c_tmean.get(m)
        tx = c_tmax.get(m)
        tn = c_tmin.get(m)
        p = c_precip.get(m)

        if t is None:
            t = 20.0
        if tx is None:
            tx = t + 5.0
        if tn is None:
            tn = t - 5.0
        if p is None:
            p = 0.0

        p = max(0.0, float(p))
        t = float(t)
        tx = float(tx)
        tn = float(tn)

        monthly_p.append(p)
        monthly_t.append(t)

        ra = extraterrestrial_radiation_ra(lat, m)
        tdiff = max(0.0, tx - tn)
        pet_daily = 0.0023 * ra * (t + 17.8) * math.sqrt(tdiff)
        pet_month = max(0.0, pet_daily * days_in_m[m - 1])
        monthly_pet.append(pet_month)

        if p < (2.0 * t):
            dry_count += 1

    p_annual = sum(monthly_p)
    t_annual = (sum(monthly_t) / 12.0) if monthly_t else 20.0
    pet_annual = sum(monthly_pet)
    pet_mean = pet_annual / 12.0
    pet_range = (max(monthly_pet) - min(monthly_pet)) if monthly_pet else 0.0

    # Seasonal ET totals (DJF, MAM, JJA, SON)
    # monthly_pet indices: 0=Jan, 1=Feb, ... 11=Dec
    et_win = monthly_pet[11] + monthly_pet[0] + monthly_pet[1]
    et_spr = monthly_pet[2] + monthly_pet[3] + monthly_pet[4]
    et_sum = monthly_pet[5] + monthly_pet[6] + monthly_pet[7]
    et_aut = monthly_pet[8] + monthly_pet[9] + monthly_pet[10]
    et_seasons = [et_win, et_spr, et_sum, et_aut]
    et_sea_range = max(et_seasons) - min(et_seasons)

    denom_dm = t_annual + 10.0
    # De Martonne is undefined for denom <= 0 (polar edge t_annual <= -10C):
    # None (not applicable) instead of 0.0 (which would misread as hyper-arid).
    dm_aridity = (p_annual / denom_dm) if denom_dm > 0.01 else None
    unep_aridity = (p_annual / pet_annual) if pet_annual > 0.01 else 0.0
    water_deficit = p_annual - pet_annual

    out_d = {
        "DM_Aridity_Annual": round(dm_aridity, 2) if dm_aridity is not None else None,
        "ET_Annual_Mean": round(pet_annual, 1),
        "ET_Annual_Range": round(pet_range, 1),
        "ET_Winter_Mean": round(et_win, 1),
        "ET_Spring_Mean": round(et_spr, 1),
        "ET_Summer_Mean": round(et_sum, 1),
        "ET_Autumn_Mean": round(et_aut, 1),
        "PET_Hargreaves_Annual": round(pet_annual, 1),
        "UNEP_Aridity_Annual": round(unep_aridity, 3),
        "Water_Deficit_Annual": round(water_deficit, 1),
        "Dry_Months_Count": int(dry_count),
    }
    _months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for m_idx, m_name in enumerate(_months_en, 1):
        out_d["ET_%s_Mean" % m_name] = round(monthly_pet[m_idx - 1], 1) if (monthly_pet and len(monthly_pet) >= m_idx) else None
    return out_d


# ---------------------------------------------------------------------------
# Field dictionary (spec sections 5-13 + 16-17). Single source of truth.
# ---------------------------------------------------------------------------
FIELD_DEFS = [
    ("T_Annual_Mean", "Annual Mean Air Temperature", u"المتوسط السنوي لدرجة الحرارة", "T2M", "Temperature", "Annual", "Mean", "C", u"متوسط قيم درجة الحرارة الشهرية خلال السنة", "Mean of monthly T2M over the period", "Mean of valid monthly T2M values"),
    ("T_Winter_Mean", "Winter Mean Air Temperature", u"متوسط درجة الحرارة في الشتاء", "T2M", "Temperature", "Winter", "Mean", "C", u"متوسط أشهر 1 و2 و12", "Mean of Dec/Jan/Feb monthly means", "Mean of climatological months 12,1,2"),
    ("T_Spring_Mean", "Spring Mean Air Temperature", u"متوسط درجة الحرارة في الربيع", "T2M", "Temperature", "Spring", "Mean", "C", u"متوسط أشهر 3 و4 و5", "Mean of Mar/Apr/May monthly means", "Mean of climatological months 3,4,5"),
    ("T_Summer_Mean", "Summer Mean Air Temperature", u"متوسط درجة الحرارة في الصيف", "T2M", "Temperature", "Summer", "Mean", "C", u"متوسط أشهر 6 و7 و8", "Mean of Jun/Jul/Aug monthly means", "Mean of climatological months 6,7,8"),
    ("T_Autumn_Mean", "Autumn Mean Air Temperature", u"متوسط درجة الحرارة في الخريف", "T2M", "Temperature", "Autumn", "Mean", "C", u"متوسط أشهر 9 و10 و11", "Mean of Sep/Oct/Nov monthly means", "Mean of climatological months 9,10,11"),
    ("T_Annual_Range", "Annual Temperature Range", u"المدى الحراري السنوي العام", "T2M", "Temperature", "Annual", "Range", "C", u"أعلى متوسط شهري ناقص أدنى متوسط شهري", "Highest monthly mean minus lowest monthly mean", "max(clim monthly) - min(clim monthly)"),
    ("T_Max_Summer_Month_Mean", "Maximum Summer Monthly Mean Temperature", u"أقصى متوسط شهري لدرجة الحرارة في الصيف", "T2M", "Temperature", "Summer", "Max", "C", u"أعلى متوسط شهري صيفي", "Max of climatological T2M for months 6,7,8", "max of monthly means 6,7,8"),
    ("T_Min_Winter_Month_Mean", "Minimum Winter Monthly Mean Temperature", u"أدنى متوسط شهري لدرجة الحرارة في الشتاء", "T2M", "Temperature", "Winter", "Min", "C", u"أدنى متوسط شهري شتوي", "Min of climatological T2M for months 12,1,2", "min of monthly means 12,1,2"),
    ("T_Annual_Max_Mean", "Annual Mean Maximum Temperature", u"المتوسط السنوي لدرجات الحرارة العظمى", "T2M_MAX", "Temperature", "Annual", "Mean", "C", u"متوسط القيم العظمى الشهرية خلال السنة", "Annual mean of monthly T2M_MAX", "Mean of valid monthly T2M_MAX values"),
    ("T_Annual_Min_Mean", "Annual Mean Minimum Temperature", u"المتوسط السنوي لدرجات الحرارة الصغرى", "T2M_MIN", "Temperature", "Annual", "Mean", "C", u"متوسط القيم الصغرى الشهرية خلال السنة", "Annual mean of monthly T2M_MIN", "Mean of valid monthly T2M_MIN values"),
    ("HI_Annual_Mean", "Annual Mean Heat Index", u"المتوسط السنوي لمؤشر الحرارة المحسوسة", "T2M+RH2M", "Heat Index", "Annual", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة الشهرية", "Annual mean Rothfusz heat index from T2M and RH2M", "Mean of monthly HI; equals T below 26.7C; needs humidity"),
    ("HI_Summer_Mean", "Summer Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة في فصل الصيف", "T2M+RH2M", "Heat Index", "Summer", "Mean", "C", u"متوسط المؤشر صيفاً", "Summer mean heat index", "Mean of monthly HI for months 6,7,8"),
    ("HI_Spring_Mean", "Spring Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة في فصل الربيع", "T2M+RH2M", "Heat Index", "Spring", "Mean", "C", u"متوسط المؤشر ربيعاً", "Spring mean heat index", "Mean of monthly HI for months 3,4,5"),
    ("HI_Autumn_Mean", "Autumn Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة في فصل الخريف", "T2M+RH2M", "Heat Index", "Autumn", "Mean", "C", u"متوسط المؤشر خريفاً", "Autumn mean heat index", "Mean of monthly HI for months 9,10,11"),
    ("HI_Winter_Mean", "Winter Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة في فصل الشتاء", "T2M+RH2M", "Heat Index", "Winter", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة (الهيوميدكس IH) شتاءً", "Winter mean perceived temperature (Humidex/IH)", "Mean of monthly Humidex IH for months 12,1,2"),
    ("HI_Annual_Range", "Annual Heat Index Range", u"المدى السنوي لمؤشر الحرارة المحسوسة (الإجهاد الحراري)", "T2M+RH2M", "Heat Index", "Annual", "Range", "C", u"أعلى مؤشر شهري بروثفوز ناقص أدناه", "Highest monthly Rothfusz heat index minus lowest monthly heat index", "max(monthly Rothfusz HI) - min(monthly Rothfusz HI)"),
    ("WBGT_Summer_Mean", "Summer Mean WBGT Heat Stress", u"متوسط الإجهاد الحراري صيفاً (WBGT)", "T2M+RH2M", "Heat Index", "Summer", "Mean", "C", u"متوسط مؤشر WBGT الظلي صيفاً من الحرارة والرطوبة", "Summer mean shade WBGT from T2M and RH2M (Stull + ISO 7243)", "Mean of monthly shade WBGT for months 6,7,8"),
    ("HI_January_Mean", "January Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر يناير (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر يناير (روثفوز)", "Mean Rothfusz heat index for January; opt-in monthly HI suite", "Mean of January HI values; equals T below 26.7C"),
    ("HI_February_Mean", "February Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر فبراير (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر فبراير (روثفوز)", "Mean Rothfusz heat index for February; opt-in monthly HI suite", "Mean of February HI values; equals T below 26.7C"),
    ("HI_March_Mean", "March Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر مارس (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر مارس (روثفوز)", "Mean Rothfusz heat index for March; opt-in monthly HI suite", "Mean of March HI values; equals T below 26.7C"),
    ("HI_April_Mean", "April Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر أبريل (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر أبريل (روثفوز)", "Mean Rothfusz heat index for April; opt-in monthly HI suite", "Mean of April HI values; equals T below 26.7C"),
    ("HI_May_Mean", "May Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر مايو (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر مايو (روثفوز)", "Mean Rothfusz heat index for May; opt-in monthly HI suite", "Mean of May HI values; equals T below 26.7C"),
    ("HI_June_Mean", "June Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر يونيو (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر يونيو (روثفوز)", "Mean Rothfusz heat index for June; opt-in monthly HI suite", "Mean of June HI values; equals T below 26.7C"),
    ("HI_July_Mean", "July Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر يوليو (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر يوليو (روثفوز)", "Mean Rothfusz heat index for July; opt-in monthly HI suite", "Mean of July HI values; equals T below 26.7C"),
    ("HI_August_Mean", "August Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر أغسطس (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر أغسطس (روثفوز)", "Mean Rothfusz heat index for August; opt-in monthly HI suite", "Mean of August HI values; equals T below 26.7C"),
    ("HI_September_Mean", "September Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر سبتمبر (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر سبتمبر (روثفوز)", "Mean Rothfusz heat index for September; opt-in monthly HI suite", "Mean of September HI values; equals T below 26.7C"),
    ("HI_October_Mean", "October Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر أكتوبر (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر أكتوبر (روثفوز)", "Mean Rothfusz heat index for October; opt-in monthly HI suite", "Mean of October HI values; equals T below 26.7C"),
    ("HI_November_Mean", "November Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر نوفمبر (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر نوفمبر (روثفوز)", "Mean Rothfusz heat index for November; opt-in monthly HI suite", "Mean of November HI values; equals T below 26.7C"),
    ("HI_December_Mean", "December Mean Heat Index", u"متوسط مؤشر الحرارة المحسوسة لشهر ديسمبر (خيار إضافي)", "T2M+RH2M", "Heat Index", "Monthly", "Mean", "C", u"متوسط مؤشر الحرارة المحسوسة لشهر ديسمبر (روثفوز)", "Mean Rothfusz heat index for December; opt-in monthly HI suite", "Mean of December HI values; equals T below 26.7C"),
    ("R_Annual_Mean", "Annual Mean Precipitation", u"المتوسط السنوي لتساقط الأمطار", "PRECTOTCORR", "Precipitation", "Annual", "Mean", "mm/year", u"متوسط مجاميع كميات المطر السنوية", "Mean annual total across years (single year: yearly sum)", "Mean of per-year annual sums"),
    ("R_Annual_Range", "Annual Precipitation Range", u"المدى السنوي للأمطار", "PRECTOTCORR", "Precipitation", "Annual", "Range", "mm", u"أعلى متوسط شهري للأمطار ناقص أدنى متوسط شهري", "Highest monthly precipitation minus lowest monthly precipitation", "max(clim monthly) - min(clim monthly)"),
    ("R_Winter_Mean", "Winter Mean Precipitation", u"متوسط هطول الأمطار خلال فصل الشتاء", "PRECTOTCORR", "Precipitation", "Winter", "Mean", "mm/season", u"متوسط هطول الأمطار خلال فصل الشتاء (مم/فصل)", "Mean winter precipitation across years", "Mean of per-year Dec+Jan+Feb totals"),
    ("R_Spring_Mean", "Spring Mean Precipitation", u"متوسط هطول الأمطار خلال فصل الربيع", "PRECTOTCORR", "Precipitation", "Spring", "Mean", "mm/season", u"متوسط هطول الأمطار خلال فصل الربيع (مم/فصل)", "Mean spring precipitation across years", "Mean of per-year Mar+Apr+May totals"),
    ("R_Summer_Mean", "Summer Mean Precipitation", u"متوسط هطول الأمطار خلال فصل الصيف", "PRECTOTCORR", "Precipitation", "Summer", "Mean", "mm/season", u"متوسط هطول الأمطار خلال فصل الصيف (مم/فصل)", "Mean summer precipitation across years", "Mean of per-year Jun+Jul+Aug totals"),
    ("R_Autumn_Mean", "Autumn Mean Precipitation", u"متوسط هطول الأمطار خلال فصل الخريف", "PRECTOTCORR", "Precipitation", "Autumn", "Mean", "mm/season", u"متوسط هطول الأمطار خلال فصل الخريف (مم/فصل)", "Mean autumn precipitation across years", "Mean of per-year Sep+Oct+Nov totals"),
    ("PSL_Annual_Mean", "Annual Mean Sea Level Pressure", u"المتوسط السنوي لضغط مستوى سطح البحر", "SLP", "Sea Level Pressure", "Annual", "Mean", "mbar/hPa", u"متوسط الضغط المصحح إلى مستوى سطح البحر", "Mean sea-level pressure", "Mean of valid values; kPa*10 if needed"),
    ("PSL_Winter_Mean", "Winter Mean Sea Level Pressure", u"متوسط ضغط مستوى سطح البحر في الشتاء", "SLP", "Sea Level Pressure", "Winter", "Mean", "mbar/hPa", u"متوسط الشتاء", "Winter mean", "Mean of months 12,1,2"),
    ("PSL_Spring_Mean", "Spring Mean Sea Level Pressure", u"متوسط ضغط مستوى سطح البحر في الربيع", "SLP", "Sea Level Pressure", "Spring", "Mean", "mbar/hPa", u"متوسط الربيع", "Spring mean", "Mean of months 3,4,5"),
    ("PSL_Summer_Mean", "Summer Mean Sea Level Pressure", u"متوسط ضغط مستوى سطح البحر في الصيف", "SLP", "Sea Level Pressure", "Summer", "Mean", "mbar/hPa", u"متوسط الصيف", "Summer mean", "Mean of months 6,7,8"),
    ("PSL_Autumn_Mean", "Autumn Mean Sea Level Pressure", u"متوسط ضغط مستوى سطح البحر في الخريف", "SLP", "Sea Level Pressure", "Autumn", "Mean", "mbar/hPa", u"متوسط الخريف", "Autumn mean", "Mean of months 9,10,11"),
    ("PSL_Annual_Range", "Annual Sea Level Pressure Range", u"المدى السنوي لضغط مستوى سطح البحر", "SLP", "Sea Level Pressure", "Annual", "Range", "mbar/hPa", u"max-min climatological monthly means", "max-min of monthly means", "max(clim) - min(clim)"),
    ("PS_Annual_Mean", "Annual Mean Surface Pressure", u"المتوسط السنوي للضغط الجوي عند السطح الفعلي", "PS", "Surface Pressure", "Annual", "Mean", "mbar/hPa", u"متوسط الضغط الفعلي عند سطح الأرض", "Mean surface pressure", "Mean of valid values; kPa*10 if needed"),
    ("PS_Winter_Mean", "Winter Mean Surface Pressure", u"متوسط الضغط السطحي في الشتاء", "PS", "Surface Pressure", "Winter", "Mean", "mbar/hPa", u"متوسط الشتاء", "Winter mean", "Mean of months 12,1,2"),
    ("PS_Spring_Mean", "Spring Mean Surface Pressure", u"متوسط الضغط السطحي في الربيع", "PS", "Surface Pressure", "Spring", "Mean", "mbar/hPa", u"متوسط الربيع", "Spring mean", "Mean of months 3,4,5"),
    ("PS_Summer_Mean", "Summer Mean Surface Pressure", u"متوسط الضغط السطحي في الصيف", "PS", "Surface Pressure", "Summer", "Mean", "mbar/hPa", u"متوسط الصيف", "Summer mean", "Mean of months 6,7,8"),
    ("PS_Autumn_Mean", "Autumn Mean Surface Pressure", u"متوسط الضغط السطحي في الخريف", "PS", "Surface Pressure", "Autumn", "Mean", "mbar/hPa", u"متوسط الخريف", "Autumn mean", "Mean of months 9,10,11"),
    ("PS_Annual_Range", "Annual Surface Pressure Range", u"المدى السنوي للضغط السطحي الفعلي", "PS", "Surface Pressure", "Annual", "Range", "mbar/hPa", u"max-min climatological monthly means", "max-min of monthly means", "max(clim) - min(clim)"),
    ("W_Spd_Annual_Mean", "Annual Mean Wind Speed", u"المتوسط السنوي لسرعة الرياح", "WS10M", "Wind", "Annual", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار", "Mean 10-m wind speed", "Mean of valid values"),
    ("W_Spd_Winter_Mean", "Winter Mean Wind Speed", u"متوسط سرعة الرياح في الشتاء", "WS10M", "Wind", "Winter", "Mean", "m/s", u"متوسط الشتاء", "Winter mean", "Mean of months 12,1,2"),
    ("W_Spd_Spring_Mean", "Spring Mean Wind Speed", u"متوسط سرعة الرياح ربيعاً", "WS10M", "Wind", "Spring", "Mean", "m/s", u"متوسط الربيع", "Spring mean", "Mean of months 3,4,5"),
    ("W_Spd_Summer_Mean", "Summer Mean Wind Speed", u"متوسط سرعة الرياح صيفاً", "WS10M", "Wind", "Summer", "Mean", "m/s", u"متوسط الصيف", "Summer mean", "Mean of months 6,7,8"),
    ("W_Spd_Autumn_Mean", "Autumn Mean Wind Speed", u"متوسط سرعة الرياح خريفاً", "WS10M", "Wind", "Autumn", "Mean", "m/s", u"متوسط الخريف", "Autumn mean", "Mean of months 9,10,11"),
    ("W_Spd_Annual_Max_Month", "Maximum Monthly Mean Wind Speed", u"أقصى متوسط سرعة رياح شهري مسجل خلال العام", "WS10M", "Wind", "Annual", "Max", "m/s", u"max climatological monthly mean", "max of monthly means", "max(clim monthly)"),
    ("W_Spd_Annual_Min_Month", "Minimum Monthly Mean Wind Speed", u"أدنى متوسط سرعة رياح شهري مسجل خلال العام", "WS10M", "Wind", "Annual", "Min", "m/s", u"min climatological monthly mean", "min of monthly means", "min(clim monthly)"),
    ("W_Spd_Annual_Range", "Annual Wind Speed Range", u"المدى السنوي لسرعة الرياح الشهرية", "WS10M", "Wind", "Annual", "Range", "m/s", u"max-min monthly means", "max-min of monthly means", "max(clim) - min(clim)"),
    ("W_Dir_Annual_Mean", "Annual Prevailing Wind Direction", u"المتوسط السنوي لاتجاه الرياح السائد", "WD10M", "Wind", "Annual", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح", "Vector-mean wind direction", "atan2(mean sin, mean cos)"),
    ("W_Dir_Winter_Mean", "Winter Prevailing Wind Direction", u"متوسط اتجاه الرياح في الشتاء", "WD10M", "Wind", "Winter", "Circular Mean", "degree", u"متوسط دائري شتاءً", "Winter vector mean", "months 12,1,2"),
    ("W_Dir_Spring_Mean", "Spring Prevailing Wind Direction", u"متوسط اتجاه الرياح في الربيع", "WD10M", "Wind", "Spring", "Circular Mean", "degree", u"متوسط دائري ربيعاً", "Spring vector mean", "months 3,4,5"),
    ("W_Dir_Summer_Mean", "Summer Prevailing Wind Direction", u"متوسط اتجاه الرياح في الصيف", "WD10M", "Wind", "Summer", "Circular Mean", "degree", u"متوسط دائري صيفاً", "Summer vector mean", "months 6,7,8"),
    ("W_Dir_Autumn_Mean", "Autumn Prevailing Wind Direction", u"متوسط اتجاه الرياح في الخريف", "WD10M", "Wind", "Autumn", "Circular Mean", "degree", u"متوسط دائري خريفاً", "Autumn vector mean", "months 9,10,11"),
    ("RH_Annual_Mean", "Annual Mean Relative Humidity", u"المتوسط السنوي للرطوبة النسبية", "RH2M", "Relative Humidity", "Annual", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع مترين", "Mean 2-m relative humidity", "Mean of valid values"),
    ("RH_Winter_Mean", "Winter Mean Relative Humidity", u"متوسط الرطوبة النسبية شتاءً", "RH2M", "Relative Humidity", "Winter", "Mean", "%", u"متوسط الشتاء", "Winter mean", "months 12,1,2"),
    ("RH_Spring_Mean", "Spring Mean Relative Humidity", u"متوسط الرطوبة النسبية ربيعاً", "RH2M", "Relative Humidity", "Spring", "Mean", "%", u"متوسط الربيع", "Spring mean", "months 3,4,5"),
    ("RH_Summer_Mean", "Summer Mean Relative Humidity", u"متوسط الرطوبة النسبية صيفاً", "RH2M", "Relative Humidity", "Summer", "Mean", "%", u"متوسط الصيف", "Summer mean", "months 6,7,8"),
    ("RH_Autumn_Mean", "Autumn Mean Relative Humidity", u"متوسط الرطوبة النسبية خريفاً", "RH2M", "Relative Humidity", "Autumn", "Mean", "%", u"متوسط الخريف", "Autumn mean", "months 9,10,11"),
    ("RH_Annual_Range", "Annual Relative Humidity Range", u"المدى السنوي للرطوبة النسبية", "RH2M", "Relative Humidity", "Annual", "Range", "%", u"أعلى متوسط شهري ناقص أدنى متوسط شهري", "Highest monthly mean minus lowest monthly mean", "max(clim monthly) - min(clim monthly)"),
    ("Td_Annual_Mean", "Annual Mean Dew Point Temperature", u"المتوسط السنوي لدرجة حرارة نقطة الندى", "T2MDEW", "Dew Point", "Annual", "Mean", "C", u"متوسط درجة حرارة نقطة الندى الشهرية خلال السنة", "Annual mean dew point temperature (absolute humidity signal)", "Mean of valid monthly T2MDEW values"),
    ("Td_Winter_Mean", "Winter Mean Dew Point Temperature", u"متوسط نقطة الندى في الشتاء", "T2MDEW", "Dew Point", "Winter", "Mean", "C", u"متوسط نقطة الندى شتاءً", "Winter mean dew point temperature", "Mean of monthly T2MDEW for months 12,1,2"),
    ("Td_Spring_Mean", "Spring Mean Dew Point Temperature", u"متوسط نقطة الندى في الربيع", "T2MDEW", "Dew Point", "Spring", "Mean", "C", u"متوسط نقطة الندى ربيعاً", "Spring mean dew point temperature", "Mean of monthly T2MDEW for months 3,4,5"),
    ("Td_Summer_Mean", "Summer Mean Dew Point Temperature", u"متوسط نقطة الندى في الصيف", "T2MDEW", "Dew Point", "Summer", "Mean", "C", u"متوسط نقطة الندى صيفاً (مؤشر الخنقة والرطوبة الساحلية)", "Summer mean dew point (mugginess / coastal humidity)", "Mean of monthly T2MDEW for months 6,7,8"),
    ("Td_Autumn_Mean", "Autumn Mean Dew Point Temperature", u"متوسط نقطة الندى في الخريف", "T2MDEW", "Dew Point", "Autumn", "Mean", "C", u"متوسط نقطة الندى خريفاً", "Autumn mean dew point temperature", "Mean of monthly T2MDEW for months 9,10,11"),
    ("Td_Annual_Range", "Annual Dew Point Range", u"المدى السنوي لدرجة حرارة نقطة الندى", "T2MDEW", "Dew Point", "Annual", "Range", "C", u"أعلى متوسط شهري لنقطة الندى ناقص أدنى متوسط شهري", "Highest monthly dew point minus lowest monthly dew point", "max(clim monthly) - min(clim monthly)"),
    ("Sol_Annual_Mean", "Annual Mean Daily Solar Radiation", u"المتوسط اليومي السنوي للإشعاع الشمسي", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Annual", "Mean", "kWh/m2/day", u"معدل الإشعاع اليومي المعتاد", "Mean daily solar radiation", "Mean of MJ/3.6"),
    ("Sol_Annual_Total", "Annual Total Solar Radiation", u"إجمالي الإشعاع الشمسي السنوي التراكمي", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Annual", "Sum", "kWh/m2/year", u"إجمالي الطاقة الشمسية المتراكمة خلال السنة", "Annual accumulated solar energy", "Per-year sum(daily*days), averaged"),
    ("Sol_Winter_Mean", "Winter Mean Daily Solar Radiation", u"متوسط الإشعاع الشمسي شتاءً", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Winter", "Mean", "kWh/m2/day", u"متوسط الشتاء", "Winter mean", "months 12,1,2 (kWh)"),
    ("Sol_Spring_Mean", "Spring Mean Daily Solar Radiation", u"متوسط الإشعاع الشمسي ربيعاً", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Spring", "Mean", "kWh/m2/day", u"متوسط الربيع", "Spring mean", "months 3,4,5"),
    ("Sol_Summer_Mean", "Summer Mean Daily Solar Radiation", u"متوسط الإشعاع الشمسي صيفاً", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Summer", "Mean", "kWh/m2/day", u"متوسط الصيف", "Summer mean", "months 6,7,8"),
    ("Sol_Autumn_Mean", "Autumn Mean Daily Solar Radiation", u"متوسط الإشعاع الشمسي خريفاً", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Autumn", "Mean", "kWh/m2/day", u"متوسط الخريف", "Autumn mean", "months 9,10,11"),
    ("Sol_Annual_Range", "Annual Solar Radiation Range", u"المدى السنوي للإشعاع الشمسي", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Annual", "Range", "kWh/m2/day", u"أعلى متوسط شهري ناقص أدنى متوسط شهري", "Highest monthly mean minus lowest monthly mean", "max(clim monthly) - min(clim monthly)"),
    ("UV_Annual_Mean", "Annual Mean UV Index", u"المتوسط السنوي لمؤشر الأشعة فوق البنفسجية", "ALLSKY_SFC_UV_INDEX", "UV Index", "Annual", "Mean", "Index", u"متوسط مؤشر UV", "Mean UV index", "Mean of valid values"),
    ("UV_Winter_Mean", "Winter Mean UV Index", u"متوسط مؤشر UV شتاءً", "ALLSKY_SFC_UV_INDEX", "UV Index", "Winter", "Mean", "Index", u"متوسط الشتاء", "Winter mean", "months 12,1,2"),
    ("UV_Spring_Mean", "Spring Mean UV Index", u"متوسط مؤشر UV ربيعاً", "ALLSKY_SFC_UV_INDEX", "UV Index", "Spring", "Mean", "Index", u"متوسط الربيع", "Spring mean", "months 3,4,5"),
    ("UV_Summer_Mean", "Summer Mean UV Index", u"متوسط مؤشر UV صيفاً", "ALLSKY_SFC_UV_INDEX", "UV Index", "Summer", "Mean", "Index", u"متوسط الصيف", "Summer mean", "months 6,7,8"),
    ("UV_Autumn_Mean", "Autumn Mean UV Index", u"متوسط مؤشر UV خريفاً", "ALLSKY_SFC_UV_INDEX", "UV Index", "Autumn", "Mean", "Index", u"متوسط الخريف", "Autumn mean", "months 9,10,11"),
    ("UV_Annual_Range", "Annual UV Index Range", u"المدى السنوي لمؤشر الأشعة فوق البنفسجية", "ALLSKY_SFC_UV_INDEX", "UV Index", "Annual", "Range", "Index", u"أعلى متوسط شهري ناقص أدنى متوسط شهري", "Highest monthly mean minus lowest monthly mean", "max(clim monthly) - min(clim monthly)"),
    ("Cld_Annual_Mean", "Annual Mean Cloud Cover", u"المتوسط السنوي للغطاء السحابي", "CLOUD_AMT", "Cloud Cover", "Annual", "Mean", "%", u"متوسط الغطاء السحابي", "Mean cloud amount", "Mean of valid values"),
    ("Cld_Winter_Mean", "Winter Mean Cloud Cover", u"متوسط الغطاء السحابي شتاءً", "CLOUD_AMT", "Cloud Cover", "Winter", "Mean", "%", u"متوسط الشتاء", "Winter mean", "months 12,1,2"),
    ("Cld_Spring_Mean", "Spring Mean Cloud Cover", u"متوسط الغطاء السحابي ربيعاً", "CLOUD_AMT", "Cloud Cover", "Spring", "Mean", "%", u"متوسط الربيع", "Spring mean", "months 3,4,5"),
    ("Cld_Summer_Mean", "Summer Mean Cloud Cover", u"متوسط الغطاء السحابي صيفاً", "CLOUD_AMT", "Cloud Cover", "Summer", "Mean", "%", u"متوسط الصيف", "Summer mean", "months 6,7,8"),
    ("Cld_Autumn_Mean", "Autumn Mean Cloud Cover", u"متوسط الغطاء السحابي خريفاً", "CLOUD_AMT", "Cloud Cover", "Autumn", "Mean", "%", u"متوسط الخريف", "Autumn mean", "months 9,10,11"),
    ("Cld_Annual_Range", "Annual Cloud Cover Range", u"المدى السنوي للغطاء السحابي", "CLOUD_AMT", "Cloud Cover", "Annual", "Range", "%", u"أعلى متوسط شهري ناقص أدنى متوسط شهري", "Highest monthly mean minus lowest monthly mean", "max(clim monthly) - min(clim monthly)"),
    ("DM_Aridity_Annual", "De Martonne Aridity Index", u"مؤشر دي مارتون للجفاف والقحولة", "PRECTOTCORR+T2M", "De Martonne Aridity", "Annual", "Index", "Index", u"مؤشر دي مارتون السنوي للقحولة والجفاف = P / (T + 10)", "Annual De Martonne aridity index P / (T + 10)", "P_ann / (T_ann + 10)"),
    ("ET_Annual_Mean", "Annual Mean Evapotranspiration", u"المتوسط السنوي للبخر والنتح (مجموع السنة النمطية)", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Annual", "Mean", "mm/year", u"متوسط مجموع البخر والنتح السنوي = متوسط السنة الواحدة من التراكمات (يقابل R_Annual_Mean للمطر)", "Mean annual total potential evapotranspiration (Hargreaves-Samani FAO-56)", "Mean of per-year annual sums"),
    ("ET_Annual_Range", "Annual Evapotranspiration Range", u"المدى السنوي للبخر والنتح", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Annual", "Range", "mm/month", u"أعلى قيمة شهرية للبخر والنتح ناقص أدنى قيمة شهرية", "Highest monthly ET minus lowest monthly ET", "max(monthly ET) - min(monthly ET)"),
    ("ET_Winter_Mean", "Winter Mean Evapotranspiration", u"متوسط بخر ونتح الشتاء", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Winter", "Mean", "mm", u"متوسط البخر والنتح لفصل الشتاء (ديسمبر، يناير، فبراير)", "Winter mean potential evapotranspiration (DJF)", "Mean of Dec+Jan+Feb ET totals"),
    ("ET_Spring_Mean", "Spring Mean Evapotranspiration", u"متوسط بخر ونتح الربيع", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Spring", "Mean", "mm", u"متوسط البخر والنتح لفصل الربيع (مارس، أبريل، مايو)", "Spring mean potential evapotranspiration (MAM)", "Mean of Mar+Apr+May ET totals"),
    ("ET_Summer_Mean", "Summer Mean Evapotranspiration", u"متوسط بخر ونتح الصيف", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Summer", "Mean", "mm", u"متوسط البخر والنتح لفصل الصيف (يونيو، يوليو، أغسطس)", "Summer mean potential evapotranspiration (JJA)", "Mean of Jun+Jul+Aug ET totals"),
    ("ET_Autumn_Mean", "Autumn Mean Evapotranspiration", u"متوسط بخر ونتح الخريف", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Autumn", "Mean", "mm", u"متوسط البخر والنتح لفصل الخريف (سبتمبر، أكتوبر، نوفمبر)", "Autumn mean potential evapotranspiration (SON)", "Mean of Sep+Oct+Nov ET totals"),
    ("PET_Hargreaves_Annual", "Annual Potential Evapotranspiration (Hargreaves)", u"التبخر-نتح الكامن السنوي بهارجريفز", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Annual", "Sum", "mm/year", u"التبخر-نتح الكامن السنوي المحسوب بطريقة هارجريفز-ساماني (رديف)", "Annual potential evapotranspiration (Hargreaves-Samani alias)", "Sum of monthly Hargreaves ETo"),
    ("UNEP_Aridity_Annual", "UNEP Aridity Index", u"مؤشر القحولة العالمي (برنامج الأمم المتحدة للبيئة)", "PRECTOTCORR+PET", "UNEP Aridity", "Annual", "Index", "Index", u"مؤشر القحولة العالمي المعتمد من UNEP = P / PET", "UNEP Aridity Index P / PET", "P_ann / PET_ann"),
    ("Water_Deficit_Annual", "Annual Climatic Water Deficit/Surplus", u"العجز/الفائض المائي المناخي السنوي", "PRECTOTCORR-PET", "Water Deficit", "Annual", "Sum", "mm/year", u"الفارق السنوي بين الأمطار والتبخر الكامن = P - PET", "Annual climatic water balance (P - PET)", "P_ann - PET_ann"),
    ("Dry_Months_Count", "Biological Dry Months Count (Walter-Lieth)", u"عدد الأشهر الجافة بيولوجياً (والتر-ليث)", "PRECTOTCORR+T2M", "Dry Months", "Annual", "Count", "months", u"عدد أشهر السنة التي تقل فيها كمية الأمطار عن ضعف درجة الحرارة P < 2T", "Annual count of biologically dry months where P_month < 2*T_month", "Count of months where P < 2*T"),
    ("WC_Winter_Mean", "Winter Mean Wind Chill Temperature", u"متوسط الإحساس بالبرودة شتاءً (تبريد الرياح)", "T2M+WS10M", "Wind Chill", "Winter", "Mean", "C", u"متوسط الإحساس بالبرودة شتاءً من الحرارة والرياح (صقيع الليالي الصحراوية)", "Winter mean wind chill from T2M and WS10M (EC/NWS 2001)", "Mean of monthly WC for months 12,1,2; =T when T>10C or calm"),
    ("WC_Spring_Mean", "Spring Mean Wind Chill Temperature", u"متوسط الإحساس بالبرودة ربيعاً (تبريد الرياح)", "T2M+WS10M", "Wind Chill", "Spring", "Mean", "C", u"متوسط الإحساس بالبرودة ربيعاً (للمناطق الباردة صيفاً/ربيعاً فقط؛ خيار إضافي)", "Spring mean wind chill from T2M and WS10M (EC/NWS 2001); opt-in extended seasons", "Mean of monthly WC for months 3,4,5; =T when T>10C or calm"),
    ("WC_Summer_Mean", "Summer Mean Wind Chill Temperature", u"متوسط الإحساس بالبرودة صيفاً (تبريد الرياح)", "T2M+WS10M", "Wind Chill", "Summer", "Mean", "C", u"متوسط الإحساس بالبرودة صيفاً (للمناطق الباردة صيفاً فقط؛ خيار إضافي)", "Summer mean wind chill from T2M and WS10M (EC/NWS 2001); opt-in extended seasons", "Mean of monthly WC for months 6,7,8; =T when T>10C or calm"),
    ("WC_Autumn_Mean", "Autumn Mean Wind Chill Temperature", u"متوسط الإحساس بالبرودة خريفاً (تبريد الرياح)", "T2M+WS10M", "Wind Chill", "Autumn", "Mean", "C", u"متوسط الإحساس بالبرودة خريفاً (للمناطق الباردة فقط؛ خيار إضافي)", "Autumn mean wind chill from T2M and WS10M (EC/NWS 2001); opt-in extended seasons", "Mean of monthly WC for months 9,10,11; =T when T>10C or calm"),
    ("WC_Annual_Range", "Annual Wind Chill Range", u"المدى السنوي للإحساس بالبرودة (تبريد الرياح)", "T2M+WS10M", "Wind Chill", "Annual", "Range", "C", u"أعلى شهري ناقص أدناه (للمناطق الباردة فقط؛ خيار إضافي)", "Highest monthly WC minus lowest monthly WC (EC/NWS 2001); opt-in extended seasons", "max(monthly WC) - min(monthly WC)"),
    ("WC_January_Mean", "January Mean Wind Chill", u"متوسط مبرد الرياح لشهر يناير (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر يناير", "Mean WC for January; opt-in extended seasons", "Mean of valid January WC values"),
    ("WC_February_Mean", "February Mean Wind Chill", u"متوسط مبرد الرياح لشهر فبراير (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر فبراير", "Mean WC for February; opt-in extended seasons", "Mean of valid February WC values"),
    ("WC_March_Mean", "March Mean Wind Chill", u"متوسط مبرد الرياح لشهر مارس (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر مارس", "Mean WC for March; opt-in extended seasons", "Mean of valid March WC values"),
    ("WC_April_Mean", "April Mean Wind Chill", u"متوسط مبرد الرياح لشهر أبريل (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر أبريل", "Mean WC for April; opt-in extended seasons", "Mean of valid April WC values"),
    ("WC_May_Mean", "May Mean Wind Chill", u"متوسط مبرد الرياح لشهر مايو (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر مايو", "Mean WC for May; opt-in extended seasons", "Mean of valid May WC values"),
    ("WC_June_Mean", "June Mean Wind Chill", u"متوسط مبرد الرياح لشهر يونيو (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر يونيو", "Mean WC for June; opt-in extended seasons", "Mean of valid June WC values"),
    ("WC_July_Mean", "July Mean Wind Chill", u"متوسط مبرد الرياح لشهر يوليو (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر يوليو", "Mean WC for July; opt-in extended seasons", "Mean of valid July WC values"),
    ("WC_August_Mean", "August Mean Wind Chill", u"متوسط مبرد الرياح لشهر أغسطس (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر أغسطس", "Mean WC for August; opt-in extended seasons", "Mean of valid August WC values"),
    ("WC_September_Mean", "September Mean Wind Chill", u"متوسط مبرد الرياح لشهر سبتمبر (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر سبتمبر", "Mean WC for September; opt-in extended seasons", "Mean of valid September WC values"),
    ("WC_October_Mean", "October Mean Wind Chill", u"متوسط مبرد الرياح لشهر أكتوبر (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر أكتوبر", "Mean WC for October; opt-in extended seasons", "Mean of valid October WC values"),
    ("WC_November_Mean", "November Mean Wind Chill", u"متوسط مبرد الرياح لشهر نوفمبر (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر نوفمبر", "Mean WC for November; opt-in extended seasons", "Mean of valid November WC values"),
    ("WC_December_Mean", "December Mean Wind Chill", u"متوسط مبرد الرياح لشهر ديسمبر (خيار إضافي للمناطق الباردة)", "T2M+WS10M", "Wind Chill", "Monthly", "Mean", "C", u"متوسط مبرد الرياح لشهر ديسمبر", "Mean WC for December; opt-in extended seasons", "Mean of valid December WC values"),    ("WC_Annual_Mean", "Annual Mean Wind Chill Temperature", u"المتوسط السنوي للإحساس بالبرودة (تبريد الرياح)", "T2M+WS10M", "Wind Chill", "Annual", "Mean", "C", u"متوسط الإحساس بالبرودة السنوي من الحرارة والرياح", "Annual mean wind chill from T2M and WS10M (EC/NWS 2001)", "Mean of 12 monthly WC values"),
    ("T_Annual_Trend_Decade", "Temperature Trend per Decade", u"اتجاه الحرارة في العقد (الميل المناخي)", "T2M", "Trends & Anomalies", "Annual", "Trend", "C/decade", u"ميل المربعات الصغرى للمتوسطات السنوية × 10 (موجب = احترار)", "Least-squares slope of annual T2M means x10", "10 * slope(annual means vs year); >=8 complete years"),
    ("R_Annual_Trend_Decade", "Precipitation Trend per Decade", u"اتجاه الأمطار في العقد (الميل المناخي)", "PRECTOTCORR", "Trends & Anomalies", "Annual", "Trend", "mm/decade", u"ميل المربعات الصغرى للإجماليات السنوية × 10", "Least-squares slope of annual PRECTOTCORR totals x10", "10 * slope(annual totals vs year); >=8 complete years"),
    ("T_Annual_Anom", "Annual Temperature Anomaly vs 1991-2020", u"شذوذ الحرارة السنوي عن معيار 1991-2020", "T2M", "Trends & Anomalies", "Annual", "Anomaly", "C", u"متوسط آخر 10 سنوات كاملة ناقص معيار WMO ‏1991-2020", "Recent (last 10 complete years) minus WMO 1991-2020 normal", "Recent annual mean - baseline annual mean"),
    ("T_Anom_Winter", "Winter Temperature Anomaly vs 1991-2020", u"شذوذ حرارة الشتاء عن معيار 1991-2020", "T2M", "Trends & Anomalies", "Winter", "Anomaly", "C", u"شذوذ متوسط الشتاء عن المعيار", "Recent winter mean minus baseline winter mean", "Recent DJF mean - baseline DJF mean"),
    ("T_Anom_Summer", "Summer Temperature Anomaly vs 1991-2020", u"شذوذ حرارة الصيف عن معيار 1991-2020", "T2M", "Trends & Anomalies", "Summer", "Anomaly", "C", u"شذوذ متوسط الصيف عن المعيار", "Recent summer mean minus baseline summer mean", "Recent JJA mean - baseline JJA mean"),
    ("R_Annual_Anom", "Annual Precipitation Anomaly vs 1991-2020", u"شذوذ الأمطار السنوي عن معيار 1991-2020", "PRECTOTCORR", "Trends & Anomalies", "Annual", "Anomaly", "mm/year", u"فرق الإجمالي السنوي الحديث عن المعيار بالمم", "Recent annual total minus baseline annual total", "Recent - baseline (mm)"),
    ("R_Annual_Anom_Pct", "Annual Precipitation Anomaly Percent vs 1991-2020", u"شذوذ الأمطار السنوي بالنسبة المئوية", "PRECTOTCORR", "Trends & Anomalies", "Annual", "Anomaly", "%", u"الشذوذ السنوي نسبة مئوية (None إذا كان الأساس <5 مم)", "Relative anomaly in percent; None when baseline <5 mm", "(Recent - baseline) / baseline * 100"),
    ("R_Anom_Winter", "Winter Precipitation Anomaly vs 1991-2020", u"شذوذ أمطار الشتاء عن معيار 1991-2020", "PRECTOTCORR", "Trends & Anomalies", "Winter", "Anomaly", "mm", u"فرق إجمالي الشتاء الحديث عن المعيار (تراجع الساحلي)", "Recent winter total minus baseline winter total", "Recent DJF total - baseline DJF total"),
    ("R_Anom_Winter_Pct", "Winter Precipitation Anomaly Percent vs 1991-2020", u"شذوذ أمطار الشتاء بالنسبة المئوية", "PRECTOTCORR", "Trends & Anomalies", "Winter", "Anomaly", "%", u"الشذوذ الشتوي نسبة مئوية (None إذا كان الأساس <5 مم)", "Relative winter anomaly in percent; None when baseline <5 mm", "(Recent - baseline) / baseline * 100"),
    # --- Climatological Monthly Fields (12 Months per Element) ---
    ("T_January_Mean", "January Mean Air Temperature", u"متوسط درجة الحرارة لشهر يناير", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر يناير خلال الفترة (2 م)", "Mean of monthly T2M for January across years", "Mean of January T2M values"),
    ("T_February_Mean", "February Mean Air Temperature", u"متوسط درجة الحرارة لشهر فبراير", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر فبراير خلال الفترة (2 م)", "Mean of monthly T2M for February across years", "Mean of February T2M values"),
    ("T_March_Mean", "March Mean Air Temperature", u"متوسط درجة الحرارة لشهر مارس", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر مارس خلال الفترة (2 م)", "Mean of monthly T2M for March across years", "Mean of March T2M values"),
    ("T_April_Mean", "April Mean Air Temperature", u"متوسط درجة الحرارة لشهر أبريل", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر أبريل خلال الفترة (2 م)", "Mean of monthly T2M for April across years", "Mean of April T2M values"),
    ("T_May_Mean", "May Mean Air Temperature", u"متوسط درجة الحرارة لشهر مايو", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر مايو خلال الفترة (2 م)", "Mean of monthly T2M for May across years", "Mean of May T2M values"),
    ("T_June_Mean", "June Mean Air Temperature", u"متوسط درجة الحرارة لشهر يونيو", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر يونيو خلال الفترة (2 م)", "Mean of monthly T2M for June across years", "Mean of June T2M values"),
    ("T_July_Mean", "July Mean Air Temperature", u"متوسط درجة الحرارة لشهر يوليو", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر يوليو خلال الفترة (2 م)", "Mean of monthly T2M for July across years", "Mean of July T2M values"),
    ("T_August_Mean", "August Mean Air Temperature", u"متوسط درجة الحرارة لشهر أغسطس", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر أغسطس خلال الفترة (2 م)", "Mean of monthly T2M for August across years", "Mean of August T2M values"),
    ("T_September_Mean", "September Mean Air Temperature", u"متوسط درجة الحرارة لشهر سبتمبر", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر سبتمبر خلال الفترة (2 م)", "Mean of monthly T2M for September across years", "Mean of September T2M values"),
    ("T_October_Mean", "October Mean Air Temperature", u"متوسط درجة الحرارة لشهر أكتوبر", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر أكتوبر خلال الفترة (2 م)", "Mean of monthly T2M for October across years", "Mean of October T2M values"),
    ("T_November_Mean", "November Mean Air Temperature", u"متوسط درجة الحرارة لشهر نوفمبر", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر نوفمبر خلال الفترة (2 م)", "Mean of monthly T2M for November across years", "Mean of November T2M values"),
    ("T_December_Mean", "December Mean Air Temperature", u"متوسط درجة الحرارة لشهر ديسمبر", "T2M", "Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة الهواء لشهر ديسمبر خلال الفترة (2 م)", "Mean of monthly T2M for December across years", "Mean of December T2M values"),
    ("R_January_Mean", "January Mean Precipitation", u"متوسط تراكم أمطار شهر يناير", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر يناير عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for January", "Mean of per-year January totals (mm/month)"),
    ("R_February_Mean", "February Mean Precipitation", u"متوسط تراكم أمطار شهر فبراير", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر فبراير عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for February", "Mean of per-year February totals (mm/month)"),
    ("R_March_Mean", "March Mean Precipitation", u"متوسط تراكم أمطار شهر مارس", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر مارس عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for March", "Mean of per-year March totals (mm/month)"),
    ("R_April_Mean", "April Mean Precipitation", u"متوسط تراكم أمطار شهر أبريل", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر أبريل عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for April", "Mean of per-year April totals (mm/month)"),
    ("R_May_Mean", "May Mean Precipitation", u"متوسط تراكم أمطار شهر مايو", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر مايو عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for May", "Mean of per-year May totals (mm/month)"),
    ("R_June_Mean", "June Mean Precipitation", u"متوسط تراكم أمطار شهر يونيو", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر يونيو عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for June", "Mean of per-year June totals (mm/month)"),
    ("R_July_Mean", "July Mean Precipitation", u"متوسط تراكم أمطار شهر يوليو", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر يوليو عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for July", "Mean of per-year July totals (mm/month)"),
    ("R_August_Mean", "August Mean Precipitation", u"متوسط تراكم أمطار شهر أغسطس", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر أغسطس عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for August", "Mean of per-year August totals (mm/month)"),
    ("R_September_Mean", "September Mean Precipitation", u"متوسط تراكم أمطار شهر سبتمبر", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر سبتمبر عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for September", "Mean of per-year September totals (mm/month)"),
    ("R_October_Mean", "October Mean Precipitation", u"متوسط تراكم أمطار شهر أكتوبر", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر أكتوبر عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for October", "Mean of per-year October totals (mm/month)"),
    ("R_November_Mean", "November Mean Precipitation", u"متوسط تراكم أمطار شهر نوفمبر", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر نوفمبر عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for November", "Mean of per-year November totals (mm/month)"),
    ("R_December_Mean", "December Mean Precipitation", u"متوسط تراكم أمطار شهر ديسمبر", "PRECTOTCORR", "Precipitation", "Monthly", "Sum", "mm/month", u"متوسط تراكم كميات أمطار شهر ديسمبر عبر السنوات (ملم/شهر)", "Mean of monthly precipitation totals for December", "Mean of per-year December totals (mm/month)"),
    ("PSL_January_Mean", "January Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر يناير", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر يناير", "Mean sea-level pressure for January", "Mean of valid January SLP values"),
    ("PSL_February_Mean", "February Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر فبراير", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر فبراير", "Mean sea-level pressure for February", "Mean of valid February SLP values"),
    ("PSL_March_Mean", "March Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر مارس", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر مارس", "Mean sea-level pressure for March", "Mean of valid March SLP values"),
    ("PSL_April_Mean", "April Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر أبريل", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر أبريل", "Mean sea-level pressure for April", "Mean of valid April SLP values"),
    ("PSL_May_Mean", "May Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر مايو", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر مايو", "Mean sea-level pressure for May", "Mean of valid May SLP values"),
    ("PSL_June_Mean", "June Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر يونيو", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر يونيو", "Mean sea-level pressure for June", "Mean of valid June SLP values"),
    ("PSL_July_Mean", "July Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر يوليو", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر يوليو", "Mean sea-level pressure for July", "Mean of valid July SLP values"),
    ("PSL_August_Mean", "August Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر أغسطس", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر أغسطس", "Mean sea-level pressure for August", "Mean of valid August SLP values"),
    ("PSL_September_Mean", "September Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر سبتمبر", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر سبتمبر", "Mean sea-level pressure for September", "Mean of valid September SLP values"),
    ("PSL_October_Mean", "October Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر أكتوبر", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر أكتوبر", "Mean sea-level pressure for October", "Mean of valid October SLP values"),
    ("PSL_November_Mean", "November Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر نوفمبر", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر نوفمبر", "Mean sea-level pressure for November", "Mean of valid November SLP values"),
    ("PSL_December_Mean", "December Mean Sea Level Pressure", u"متوسط ضغط مستوى البحر لشهر ديسمبر", "SLP", "Sea Level Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي المصحح لمستوى سطح البحر لشهر ديسمبر", "Mean sea-level pressure for December", "Mean of valid December SLP values"),
    ("PS_January_Mean", "January Mean Surface Pressure", u"متوسط الضغط السطحي لشهر يناير", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر يناير", "Mean surface pressure for January", "Mean of valid January PS values"),
    ("PS_February_Mean", "February Mean Surface Pressure", u"متوسط الضغط السطحي لشهر فبراير", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر فبراير", "Mean surface pressure for February", "Mean of valid February PS values"),
    ("PS_March_Mean", "March Mean Surface Pressure", u"متوسط الضغط السطحي لشهر مارس", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر مارس", "Mean surface pressure for March", "Mean of valid March PS values"),
    ("PS_April_Mean", "April Mean Surface Pressure", u"متوسط الضغط السطحي لشهر أبريل", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر أبريل", "Mean surface pressure for April", "Mean of valid April PS values"),
    ("PS_May_Mean", "May Mean Surface Pressure", u"متوسط الضغط السطحي لشهر مايو", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر مايو", "Mean surface pressure for May", "Mean of valid May PS values"),
    ("PS_June_Mean", "June Mean Surface Pressure", u"متوسط الضغط السطحي لشهر يونيو", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر يونيو", "Mean surface pressure for June", "Mean of valid June PS values"),
    ("PS_July_Mean", "July Mean Surface Pressure", u"متوسط الضغط السطحي لشهر يوليو", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر يوليو", "Mean surface pressure for July", "Mean of valid July PS values"),
    ("PS_August_Mean", "August Mean Surface Pressure", u"متوسط الضغط السطحي لشهر أغسطس", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر أغسطس", "Mean surface pressure for August", "Mean of valid August PS values"),
    ("PS_September_Mean", "September Mean Surface Pressure", u"متوسط الضغط السطحي لشهر سبتمبر", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر سبتمبر", "Mean surface pressure for September", "Mean of valid September PS values"),
    ("PS_October_Mean", "October Mean Surface Pressure", u"متوسط الضغط السطحي لشهر أكتوبر", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر أكتوبر", "Mean surface pressure for October", "Mean of valid October PS values"),
    ("PS_November_Mean", "November Mean Surface Pressure", u"متوسط الضغط السطحي لشهر نوفمبر", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر نوفمبر", "Mean surface pressure for November", "Mean of valid November PS values"),
    ("PS_December_Mean", "December Mean Surface Pressure", u"متوسط الضغط السطحي لشهر ديسمبر", "PS", "Surface Pressure", "Monthly", "Mean", "mbar/hPa", u"متوسط الضغط الجوي عند السطح الفعلي لشهر ديسمبر", "Mean surface pressure for December", "Mean of valid December PS values"),
    ("W_Spd_January_Mean", "January Mean Wind Speed", u"متوسط سرعة الرياح لشهر يناير", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر يناير", "Mean 10-m wind speed for January", "Mean of valid January WS10M values"),
    ("W_Spd_February_Mean", "February Mean Wind Speed", u"متوسط سرعة الرياح لشهر فبراير", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر فبراير", "Mean 10-m wind speed for February", "Mean of valid February WS10M values"),
    ("W_Spd_March_Mean", "March Mean Wind Speed", u"متوسط سرعة الرياح لشهر مارس", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر مارس", "Mean 10-m wind speed for March", "Mean of valid March WS10M values"),
    ("W_Spd_April_Mean", "April Mean Wind Speed", u"متوسط سرعة الرياح لشهر أبريل", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر أبريل", "Mean 10-m wind speed for April", "Mean of valid April WS10M values"),
    ("W_Spd_May_Mean", "May Mean Wind Speed", u"متوسط سرعة الرياح لشهر مايو", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر مايو", "Mean 10-m wind speed for May", "Mean of valid May WS10M values"),
    ("W_Spd_June_Mean", "June Mean Wind Speed", u"متوسط سرعة الرياح لشهر يونيو", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر يونيو", "Mean 10-m wind speed for June", "Mean of valid June WS10M values"),
    ("W_Spd_July_Mean", "July Mean Wind Speed", u"متوسط سرعة الرياح لشهر يوليو", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر يوليو", "Mean 10-m wind speed for July", "Mean of valid July WS10M values"),
    ("W_Spd_August_Mean", "August Mean Wind Speed", u"متوسط سرعة الرياح لشهر أغسطس", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر أغسطس", "Mean 10-m wind speed for August", "Mean of valid August WS10M values"),
    ("W_Spd_September_Mean", "September Mean Wind Speed", u"متوسط سرعة الرياح لشهر سبتمبر", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر سبتمبر", "Mean 10-m wind speed for September", "Mean of valid September WS10M values"),
    ("W_Spd_October_Mean", "October Mean Wind Speed", u"متوسط سرعة الرياح لشهر أكتوبر", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر أكتوبر", "Mean 10-m wind speed for October", "Mean of valid October WS10M values"),
    ("W_Spd_November_Mean", "November Mean Wind Speed", u"متوسط سرعة الرياح لشهر نوفمبر", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر نوفمبر", "Mean 10-m wind speed for November", "Mean of valid November WS10M values"),
    ("W_Spd_December_Mean", "December Mean Wind Speed", u"متوسط سرعة الرياح لشهر ديسمبر", "WS10M", "Wind", "Monthly", "Mean", "m/s", u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر ديسمبر", "Mean 10-m wind speed for December", "Mean of valid December WS10M values"),
    ("W_Dir_January_Mean", "January Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر يناير", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر يناير (متجهي)", "Vector-mean wind direction for January", "atan2(mean sin, mean cos) for January"),
    ("W_Dir_February_Mean", "February Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر فبراير", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر فبراير (متجهي)", "Vector-mean wind direction for February", "atan2(mean sin, mean cos) for February"),
    ("W_Dir_March_Mean", "March Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر مارس", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر مارس (متجهي)", "Vector-mean wind direction for March", "atan2(mean sin, mean cos) for March"),
    ("W_Dir_April_Mean", "April Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر أبريل", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر أبريل (متجهي)", "Vector-mean wind direction for April", "atan2(mean sin, mean cos) for April"),
    ("W_Dir_May_Mean", "May Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر مايو", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر مايو (متجهي)", "Vector-mean wind direction for May", "atan2(mean sin, mean cos) for May"),
    ("W_Dir_June_Mean", "June Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر يونيو", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر يونيو (متجهي)", "Vector-mean wind direction for June", "atan2(mean sin, mean cos) for June"),
    ("W_Dir_July_Mean", "July Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر يوليو", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر يوليو (متجهي)", "Vector-mean wind direction for July", "atan2(mean sin, mean cos) for July"),
    ("W_Dir_August_Mean", "August Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر أغسطس", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر أغسطس (متجهي)", "Vector-mean wind direction for August", "atan2(mean sin, mean cos) for August"),
    ("W_Dir_September_Mean", "September Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر سبتمبر", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر سبتمبر (متجهي)", "Vector-mean wind direction for September", "atan2(mean sin, mean cos) for September"),
    ("W_Dir_October_Mean", "October Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر أكتوبر", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر أكتوبر (متجهي)", "Vector-mean wind direction for October", "atan2(mean sin, mean cos) for October"),
    ("W_Dir_November_Mean", "November Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر نوفمبر", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر نوفمبر (متجهي)", "Vector-mean wind direction for November", "atan2(mean sin, mean cos) for November"),
    ("W_Dir_December_Mean", "December Prevailing Wind Direction", u"متوسط اتجاه الرياح السائد لشهر ديسمبر", "WD10M", "Wind", "Monthly", "Circular Mean", "degree", u"متوسط دائري لاتجاهات الرياح لشهر ديسمبر (متجهي)", "Vector-mean wind direction for December", "atan2(mean sin, mean cos) for December"),
    ("RH_January_Mean", "January Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر يناير", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر يناير", "Mean 2-m relative humidity for January", "Mean of valid January RH2M values"),
    ("RH_February_Mean", "February Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر فبراير", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر فبراير", "Mean 2-m relative humidity for February", "Mean of valid February RH2M values"),
    ("RH_March_Mean", "March Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر مارس", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر مارس", "Mean 2-m relative humidity for March", "Mean of valid March RH2M values"),
    ("RH_April_Mean", "April Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر أبريل", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر أبريل", "Mean 2-m relative humidity for April", "Mean of valid April RH2M values"),
    ("RH_May_Mean", "May Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر مايو", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر مايو", "Mean 2-m relative humidity for May", "Mean of valid May RH2M values"),
    ("RH_June_Mean", "June Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر يونيو", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر يونيو", "Mean 2-m relative humidity for June", "Mean of valid June RH2M values"),
    ("RH_July_Mean", "July Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر يوليو", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر يوليو", "Mean 2-m relative humidity for July", "Mean of valid July RH2M values"),
    ("RH_August_Mean", "August Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر أغسطس", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر أغسطس", "Mean 2-m relative humidity for August", "Mean of valid August RH2M values"),
    ("RH_September_Mean", "September Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر سبتمبر", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر سبتمبر", "Mean 2-m relative humidity for September", "Mean of valid September RH2M values"),
    ("RH_October_Mean", "October Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر أكتوبر", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر أكتوبر", "Mean 2-m relative humidity for October", "Mean of valid October RH2M values"),
    ("RH_November_Mean", "November Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر نوفمبر", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر نوفمبر", "Mean 2-m relative humidity for November", "Mean of valid November RH2M values"),
    ("RH_December_Mean", "December Mean Relative Humidity", u"متوسط الرطوبة النسبية لشهر ديسمبر", "RH2M", "Relative Humidity", "Monthly", "Mean", "%", u"متوسط الرطوبة النسبية على ارتفاع 2 متر لشهر ديسمبر", "Mean 2-m relative humidity for December", "Mean of valid December RH2M values"),
    ("Td_January_Mean", "January Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر يناير", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر يناير", "Mean dew point temperature for January", "Mean of valid January T2MDEW values"),
    ("Td_February_Mean", "February Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر فبراير", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر فبراير", "Mean dew point temperature for February", "Mean of valid February T2MDEW values"),
    ("Td_March_Mean", "March Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر مارس", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر مارس", "Mean dew point temperature for March", "Mean of valid March T2MDEW values"),
    ("Td_April_Mean", "April Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر أبريل", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر أبريل", "Mean dew point temperature for April", "Mean of valid April T2MDEW values"),
    ("Td_May_Mean", "May Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر مايو", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر مايو", "Mean dew point temperature for May", "Mean of valid May T2MDEW values"),
    ("Td_June_Mean", "June Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر يونيو", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر يونيو", "Mean dew point temperature for June", "Mean of valid June T2MDEW values"),
    ("Td_July_Mean", "July Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر يوليو", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر يوليو", "Mean dew point temperature for July", "Mean of valid July T2MDEW values"),
    ("Td_August_Mean", "August Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر أغسطس", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر أغسطس", "Mean dew point temperature for August", "Mean of valid August T2MDEW values"),
    ("Td_September_Mean", "September Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر سبتمبر", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر سبتمبر", "Mean dew point temperature for September", "Mean of valid September T2MDEW values"),
    ("Td_October_Mean", "October Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر أكتوبر", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر أكتوبر", "Mean dew point temperature for October", "Mean of valid October T2MDEW values"),
    ("Td_November_Mean", "November Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر نوفمبر", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر نوفمبر", "Mean dew point temperature for November", "Mean of valid November T2MDEW values"),
    ("Td_December_Mean", "December Mean Dew Point Temperature", u"متوسط نقطة الندى لشهر ديسمبر", "T2MDEW", "Dew Point", "Monthly", "Mean", "C", u"متوسط درجة حرارة نقطة الندى لشهر ديسمبر", "Mean dew point temperature for December", "Mean of valid December T2MDEW values"),
    ("Sol_January_Mean", "January Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر يناير", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر يناير (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for January", "Mean of January MJ/3.6 across years"),
    ("Sol_February_Mean", "February Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر فبراير", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر فبراير (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for February", "Mean of February MJ/3.6 across years"),
    ("Sol_March_Mean", "March Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر مارس", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر مارس (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for March", "Mean of March MJ/3.6 across years"),
    ("Sol_April_Mean", "April Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر أبريل", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر أبريل (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for April", "Mean of April MJ/3.6 across years"),
    ("Sol_May_Mean", "May Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر مايو", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر مايو (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for May", "Mean of May MJ/3.6 across years"),
    ("Sol_June_Mean", "June Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر يونيو", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر يونيو (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for June", "Mean of June MJ/3.6 across years"),
    ("Sol_July_Mean", "July Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر يوليو", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر يوليو (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for July", "Mean of July MJ/3.6 across years"),
    ("Sol_August_Mean", "August Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر أغسطس", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر أغسطس (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for August", "Mean of August MJ/3.6 across years"),
    ("Sol_September_Mean", "September Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر سبتمبر", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر سبتمبر (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for September", "Mean of September MJ/3.6 across years"),
    ("Sol_October_Mean", "October Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر أكتوبر", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر أكتوبر (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for October", "Mean of October MJ/3.6 across years"),
    ("Sol_November_Mean", "November Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر نوفمبر", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر نوفمبر (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for November", "Mean of November MJ/3.6 across years"),
    ("Sol_December_Mean", "December Mean Daily Solar Radiation", u"المتوسط اليومي للإشعاع الشمسي لشهر ديسمبر", "ALLSKY_SFC_SW_DWN", "Solar Radiation", "Monthly", "Mean", "kWh/m2/day", u"معدل الإشعاع الشمسي اليومي لشهر ديسمبر (كيلوواط.س/م2/يوم)", "Mean daily solar radiation for December", "Mean of December MJ/3.6 across years"),
    ("UV_January_Mean", "January Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يناير", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يناير", "Mean UV index for January", "Mean of valid January UV values"),
    ("UV_February_Mean", "February Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر فبراير", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر فبراير", "Mean UV index for February", "Mean of valid February UV values"),
    ("UV_March_Mean", "March Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر مارس", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر مارس", "Mean UV index for March", "Mean of valid March UV values"),
    ("UV_April_Mean", "April Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أبريل", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أبريل", "Mean UV index for April", "Mean of valid April UV values"),
    ("UV_May_Mean", "May Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر مايو", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر مايو", "Mean UV index for May", "Mean of valid May UV values"),
    ("UV_June_Mean", "June Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يونيو", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يونيو", "Mean UV index for June", "Mean of valid June UV values"),
    ("UV_July_Mean", "July Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يوليو", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يوليو", "Mean UV index for July", "Mean of valid July UV values"),
    ("UV_August_Mean", "August Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أغسطس", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أغسطس", "Mean UV index for August", "Mean of valid August UV values"),
    ("UV_September_Mean", "September Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر سبتمبر", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر سبتمبر", "Mean UV index for September", "Mean of valid September UV values"),
    ("UV_October_Mean", "October Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أكتوبر", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أكتوبر", "Mean UV index for October", "Mean of valid October UV values"),
    ("UV_November_Mean", "November Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر نوفمبر", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر نوفمبر", "Mean UV index for November", "Mean of valid November UV values"),
    ("UV_December_Mean", "December Mean UV Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر ديسمبر", "ALLSKY_SFC_UV_INDEX", "UV Index", "Monthly", "Mean", "Index", u"متوسط مؤشر الأشعة فوق البنفسجية لشهر ديسمبر", "Mean UV index for December", "Mean of valid December UV values"),
    ("Cld_January_Mean", "January Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر يناير", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر يناير", "Mean cloud cover for January", "Mean of valid January CLOUD_AMT values"),
    ("Cld_February_Mean", "February Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر فبراير", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر فبراير", "Mean cloud cover for February", "Mean of valid February CLOUD_AMT values"),
    ("Cld_March_Mean", "March Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر مارس", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر مارس", "Mean cloud cover for March", "Mean of valid March CLOUD_AMT values"),
    ("Cld_April_Mean", "April Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر أبريل", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر أبريل", "Mean cloud cover for April", "Mean of valid April CLOUD_AMT values"),
    ("Cld_May_Mean", "May Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر مايو", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر مايو", "Mean cloud cover for May", "Mean of valid May CLOUD_AMT values"),
    ("Cld_June_Mean", "June Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر يونيو", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر يونيو", "Mean cloud cover for June", "Mean of valid June CLOUD_AMT values"),
    ("Cld_July_Mean", "July Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر يوليو", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر يوليو", "Mean cloud cover for July", "Mean of valid July CLOUD_AMT values"),
    ("Cld_August_Mean", "August Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر أغسطس", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر أغسطس", "Mean cloud cover for August", "Mean of valid August CLOUD_AMT values"),
    ("Cld_September_Mean", "September Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر سبتمبر", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر سبتمبر", "Mean cloud cover for September", "Mean of valid September CLOUD_AMT values"),
    ("Cld_October_Mean", "October Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر أكتوبر", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر أكتوبر", "Mean cloud cover for October", "Mean of valid October CLOUD_AMT values"),
    ("Cld_November_Mean", "November Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر نوفمبر", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر نوفمبر", "Mean cloud cover for November", "Mean of valid November CLOUD_AMT values"),
    ("Cld_December_Mean", "December Mean Cloud Cover", u"متوسط الغطاء السحابي لشهر ديسمبر", "CLOUD_AMT", "Cloud Cover", "Monthly", "Mean", "%", u"متوسط نسبة الغطاء السحابي لشهر ديسمبر", "Mean cloud cover for December", "Mean of valid December CLOUD_AMT values"),
    ("ET_January_Mean", "January Mean Evapotranspiration", u"متوسط البخر والنتح لشهر يناير", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر يناير بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for January (FAO-56)", "Monthly FAO-56 Hargreaves ETo for January"),
    ("ET_February_Mean", "February Mean Evapotranspiration", u"متوسط البخر والنتح لشهر فبراير", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر فبراير بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for February (FAO-56)", "Monthly FAO-56 Hargreaves ETo for February"),
    ("ET_March_Mean", "March Mean Evapotranspiration", u"متوسط البخر والنتح لشهر مارس", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر مارس بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for March (FAO-56)", "Monthly FAO-56 Hargreaves ETo for March"),
    ("ET_April_Mean", "April Mean Evapotranspiration", u"متوسط البخر والنتح لشهر أبريل", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر أبريل بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for April (FAO-56)", "Monthly FAO-56 Hargreaves ETo for April"),
    ("ET_May_Mean", "May Mean Evapotranspiration", u"متوسط البخر والنتح لشهر مايو", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر مايو بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for May (FAO-56)", "Monthly FAO-56 Hargreaves ETo for May"),
    ("ET_June_Mean", "June Mean Evapotranspiration", u"متوسط البخر والنتح لشهر يونيو", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر يونيو بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for June (FAO-56)", "Monthly FAO-56 Hargreaves ETo for June"),
    ("ET_July_Mean", "July Mean Evapotranspiration", u"متوسط البخر والنتح لشهر يوليو", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر يوليو بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for July (FAO-56)", "Monthly FAO-56 Hargreaves ETo for July"),
    ("ET_August_Mean", "August Mean Evapotranspiration", u"متوسط البخر والنتح لشهر أغسطس", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر أغسطس بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for August (FAO-56)", "Monthly FAO-56 Hargreaves ETo for August"),
    ("ET_September_Mean", "September Mean Evapotranspiration", u"متوسط البخر والنتح لشهر سبتمبر", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر سبتمبر بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for September (FAO-56)", "Monthly FAO-56 Hargreaves ETo for September"),
    ("ET_October_Mean", "October Mean Evapotranspiration", u"متوسط البخر والنتح لشهر أكتوبر", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر أكتوبر بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for October (FAO-56)", "Monthly FAO-56 Hargreaves ETo for October"),
    ("ET_November_Mean", "November Mean Evapotranspiration", u"متوسط البخر والنتح لشهر نوفمبر", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر نوفمبر بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for November (FAO-56)", "Monthly FAO-56 Hargreaves ETo for November"),
    ("ET_December_Mean", "December Mean Evapotranspiration", u"متوسط البخر والنتح لشهر ديسمبر", "T2M+T2M_MAX+T2M_MIN", "Evapotranspiration", "Monthly", "Mean", "mm/month", u"متوسط مجموع البخر والنتح لشهر ديسمبر بطريقة هارجريفز-ساماني (ملم/شهر)", "Mean total potential evapotranspiration for December (FAO-56)", "Monthly FAO-56 Hargreaves ETo for December"),
]

MONTH_NAMES_EN = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]

FIELD_BY_NAME = dict((r[0], r) for r in FIELD_DEFS)
FIELD_ALIAS_AR = dict((r[0], r[2]) for r in FIELD_DEFS)

# Interannual monthly ranges (opt-in): max-min of each calendar month across
# years, e.g. ET_December_Range. Generated (not hand-listed) to keep the 11
# mean-type modules x 12 months in sync; published only when the monthly-ranges
# toggle is enabled (default OFF).
MONTHLY_RANGE_MODULES = [
    ("T", "Temperature", "Temperature", "T2M", "C", u"درجة الحرارة"),
    ("R", "Precipitation", "Precipitation", "PRECTOTCORR", "mm", u"الأمطار"),
    ("PSL", "Sea Level Pressure", "Sea Level Pressure", "SLP", "mbar/hPa", u"ضغط مستوى البحر"),
    ("PS", "Surface Pressure", "Surface Pressure", "PS", "mbar/hPa", u"الضغط السطحي"),
    ("W_Spd", "Wind", "Wind Speed", "WS10M", "m/s", u"سرعة الرياح"),
    ("RH", "Relative Humidity", "Relative Humidity", "RH2M", "%", u"الرطوبة النسبية"),
    ("Td", "Dew Point", "Dew Point", "T2MDEW", "C", u"نقطة الندى"),
    ("Sol", "Solar Radiation", "Solar Radiation", "ALLSKY_SFC_SW_DWN", "kWh/m2/day", u"الإشعاع الشمسي"),
    ("UV", "UV Index", "UV Index", "ALLSKY_SFC_UV_INDEX", "Index", u"الأشعة فوق البنفسجية"),
    ("Cld", "Cloud Cover", "Cloud Cover", "CLOUD_AMT", "%", u"الغطاء السحابي"),
    ("ET", "Evapotranspiration", "Evapotranspiration", "T2M+T2M_MAX+T2M_MIN", "mm/month", u"البخر والنتح"),
]
for _pfx, _mod, _word, _code, _unit, _ar in MONTHLY_RANGE_MODULES:
    for _mn in MONTH_NAMES_EN:
        FIELD_DEFS.append(
            ("%s_%s_Range" % (_pfx, _mn), "%s %s Monthly Range" % (_mn, _word),
             u"المدى الشهري لـ %s (%s، تباين السنوات)" % (_ar, _mn),
             _code, _mod, "Monthly", "Range", _unit,
             u"المدى بين أعلى وأدنى قيمة لشهر %s عبر السنوات" % _mn,
             "Interannual range of %s %s across years (opt-in)" % (_pfx, _mn),
             "max(yearly %s) - min(yearly %s)" % (_mn, _mn)))
FIELD_BY_NAME = dict((r[0], r) for r in FIELD_DEFS)
FIELD_ALIAS_AR = dict((r[0], r[2]) for r in FIELD_DEFS)

# Monthly trend/anomaly fields (Trends & Anomalies module): same *_<Month>
# naming pattern as the monthly means (T_Anom_January ... R_December_Trend_Decade).
# Alias == English field name (project convention: separate Arabic output command).
for _mn in MONTH_NAMES_EN:
    FIELD_DEFS.append(
        ("T_Anom_%s" % _mn, "%s Temperature Anomaly vs 1991-2020" % _mn,
         "%s Temperature Anomaly vs 1991-2020" % _mn,
         "T2M", "Trends & Anomalies", "Monthly", "Anomaly", "C",
         u"Monthly temperature anomaly (recent vs WMO 1991-2020 baseline)",
         "Recent %s mean minus baseline %s mean" % (_mn, _mn),
         "Recent monthly mean - baseline monthly mean"))
    FIELD_DEFS.append(
        ("R_Anom_%s" % _mn, "%s Precipitation Anomaly vs 1991-2020" % _mn,
         "%s Precipitation Anomaly vs 1991-2020" % _mn,
         "PRECTOTCORR", "Trends & Anomalies", "Monthly", "Anomaly", "mm",
         u"Monthly precipitation anomaly (recent vs WMO 1991-2020 baseline)",
         "Recent %s total minus baseline %s total" % (_mn, _mn),
         "Recent monthly total - baseline monthly total"))
    FIELD_DEFS.append(
        ("R_Anom_%s_Pct" % _mn, "%s Precipitation Anomaly Percent vs 1991-2020" % _mn,
         "%s Precipitation Anomaly Percent vs 1991-2020" % _mn,
         "PRECTOTCORR", "Trends & Anomalies", "Monthly", "Anomaly", "%",
         u"Monthly precipitation anomaly percent (None when baseline <5 mm)",
         "Relative monthly anomaly in percent; None when baseline <5 mm",
         "(Recent - baseline) / baseline * 100"))
    FIELD_DEFS.append(
        ("T_%s_Trend_Decade" % _mn, "%s Temperature Trend per Decade" % _mn,
         "%s Temperature Trend per Decade" % _mn,
         "T2M", "Trends & Anomalies", "Monthly", "Trend", "C/decade",
         u"OLS monthly temperature trend x10 (alias = English field name)",
         "Least-squares slope of %s means x10" % _mn,
         "10 * slope(monthly values vs year); >=8 complete years"))
    FIELD_DEFS.append(
        ("R_%s_Trend_Decade" % _mn, "%s Precipitation Trend per Decade" % _mn,
         "%s Precipitation Trend per Decade" % _mn,
         "PRECTOTCORR", "Trends & Anomalies", "Monthly", "Trend", "mm/decade",
         u"OLS monthly precipitation trend x10 (alias = English field name)",
         "Least-squares slope of %s totals x10" % _mn,
         "10 * slope(monthly totals vs year); >=8 complete years"))
FIELD_BY_NAME = dict((r[0], r) for r in FIELD_DEFS)
FIELD_ALIAS_AR = dict((r[0], r[2]) for r in FIELD_DEFS)
MODULE_FIELDS = {}
for _r in FIELD_DEFS:
    MODULE_FIELDS.setdefault(_r[4], []).append(_r[0])

# Seasonal trend/anomaly complements (Trends & Anomalies module).
# Alias == English field name (project convention: separate Arabic output command).
_TREND_SEASON_DEFS = [
    ("T_Anom_Spring", "Spring Temperature Anomaly vs 1991-2020", "T2M", "Spring", "C",
     "Recent spring mean minus baseline spring mean", "Recent MAM mean - baseline MAM mean"),
    ("T_Anom_Autumn", "Autumn Temperature Anomaly vs 1991-2020", "T2M", "Autumn", "C",
     "Recent autumn mean minus baseline autumn mean", "Recent SON mean - baseline SON mean"),
    ("R_Anom_Spring", "Spring Precipitation Anomaly vs 1991-2020", "PRECTOTCORR", "Spring", "mm",
     "Recent spring total minus baseline spring total", "Recent MAM total - baseline MAM total"),
    ("R_Anom_Spring_Pct", "Spring Precipitation Anomaly Percent vs 1991-2020", "PRECTOTCORR", "Spring", "%",
     "Relative spring anomaly in percent; None when baseline <5 mm", "(Recent - baseline) / baseline * 100"),
    ("R_Anom_Summer", "Summer Precipitation Anomaly vs 1991-2020", "PRECTOTCORR", "Summer", "mm",
     "Recent summer total minus baseline summer total", "Recent JJA total - baseline JJA total"),
    ("R_Anom_Summer_Pct", "Summer Precipitation Anomaly Percent vs 1991-2020", "PRECTOTCORR", "Summer", "%",
     "Relative summer anomaly in percent; None when baseline <5 mm", "(Recent - baseline) / baseline * 100"),
    ("R_Anom_Autumn", "Autumn Precipitation Anomaly vs 1991-2020", "PRECTOTCORR", "Autumn", "mm",
     "Recent autumn total minus baseline autumn total", "Recent SON total - baseline SON total"),
    ("R_Anom_Autumn_Pct", "Autumn Precipitation Anomaly Percent vs 1991-2020", "PRECTOTCORR", "Autumn", "%",
     "Relative autumn anomaly in percent; None when baseline <5 mm", "(Recent - baseline) / baseline * 100"),
    ("T_Winter_Trend_Decade", "Winter Temperature Trend per Decade", "T2M", "Winter", "C/decade",
     "Least-squares slope of winter means x10", "10 * slope(seasonal means vs year); >=8 complete years"),
    ("T_Spring_Trend_Decade", "Spring Temperature Trend per Decade", "T2M", "Spring", "C/decade",
     "Least-squares slope of spring means x10", "10 * slope(seasonal means vs year); >=8 complete years"),
    ("T_Summer_Trend_Decade", "Summer Temperature Trend per Decade", "T2M", "Summer", "C/decade",
     "Least-squares slope of summer means x10", "10 * slope(seasonal means vs year); >=8 complete years"),
    ("T_Autumn_Trend_Decade", "Autumn Temperature Trend per Decade", "T2M", "Autumn", "C/decade",
     "Least-squares slope of autumn means x10", "10 * slope(seasonal means vs year); >=8 complete years"),
    ("R_Winter_Trend_Decade", "Winter Precipitation Trend per Decade", "PRECTOTCORR", "Winter", "mm/decade",
     "Least-squares slope of winter totals x10", "10 * slope(seasonal totals vs year); >=8 complete years"),
    ("R_Spring_Trend_Decade", "Spring Precipitation Trend per Decade", "PRECTOTCORR", "Spring", "mm/decade",
     "Least-squares slope of spring totals x10", "10 * slope(seasonal totals vs year); >=8 complete years"),
    ("R_Summer_Trend_Decade", "Summer Precipitation Trend per Decade", "PRECTOTCORR", "Summer", "mm/decade",
     "Least-squares slope of summer totals x10", "10 * slope(seasonal totals vs year); >=8 complete years"),
    ("R_Autumn_Trend_Decade", "Autumn Precipitation Trend per Decade", "PRECTOTCORR", "Autumn", "mm/decade",
     "Least-squares slope of autumn totals x10", "10 * slope(seasonal totals vs year); >=8 complete years"),
]
for _fld, _en, _code, _period, _unit, _calc_en, _calc in _TREND_SEASON_DEFS:
    _stat = "Trend" if _fld.startswith(("T_Trend", "R_Trend")) else "Anomaly"
    FIELD_DEFS.append((_fld, _en, _en, _code, "Trends & Anomalies", "Seasonal",
                       _stat, _unit, _en, _calc_en, _calc))
    MODULE_FIELDS.setdefault("Trends & Anomalies", []).append(_fld)
# General-monthly aggregates: same *_Month_Mean pattern as the means
# (Period Annual, so they live in the Data sheet, not Month).
_TREND_MONTHMEAN_DEFS = [
    ("T_Anom_Month", "Mean Monthly Temperature Anomaly vs 1991-2020", "T2M", "C",
     "Mean of the 12 valid monthly temperature anomalies", "Mean of valid T_Anom_<Month>"),
    ("R_Anom_Month", "Mean Monthly Precipitation Anomaly vs 1991-2020", "PRECTOTCORR", "mm",
     "Mean of the 12 valid monthly precipitation anomalies", "Mean of valid R_Anom_<Month>"),
    ("R_Anom_Month_Pct", "Mean Monthly Precipitation Anomaly Percent vs 1991-2020", "PRECTOTCORR", "%",
     "Mean of the valid monthly precipitation anomaly percents", "Mean of valid R_Anom_<Month>_Pct"),
    ("T_Month_Trend_Decade", "Mean Monthly Temperature Trend per Decade", "T2M", "C/decade",
     "Mean of the 12 valid monthly temperature trends", "Mean of valid T_<Month>_Trend_Decade"),
    ("R_Month_Trend_Decade", "Mean Monthly Precipitation Trend per Decade", "PRECTOTCORR", "mm/decade",
     "Mean of the 12 valid monthly precipitation trends", "Mean of valid R_<Month>_Trend_Decade"),
]
for _fld, _en, _code, _unit, _calc_en, _calc in _TREND_MONTHMEAN_DEFS:
    _stat = "Trend" if "Trend" in _fld else "Anomaly"
    FIELD_DEFS.append((_fld, _en, _en, _code, "Trends & Anomalies", "Annual",
                       _stat, _unit, _en, _calc_en, _calc))
    MODULE_FIELDS.setdefault("Trends & Anomalies", []).append(_fld)

_LST_DEFS = [
    ("LST_Annual_Mean", "Annual Mean Land Surface Temperature", u"المتوسط السنوي لدرجة حرارة سطح الأرض", "TS", "Land Surface Temperature", "Annual", "Mean", "C", u"المتوسط السنوي لدرجة حرارة سطح الأرض من مسبار ناسا ميررا-2", "Mean of monthly TS over the period", "Mean of valid monthly TS values"),
    ("LST_Winter_Mean", "Winter Mean Land Surface Temperature", u"متوسط درجة حرارة سطح الأرض شتاءً", "TS", "Land Surface Temperature", "Winter", "Mean", "C", u"متوسط أشهر الشتاء (ديسمبر، يناير، فبراير)", "Mean of Dec/Jan/Feb monthly TS means", "Mean of climatological months 12,1,2"),
    ("LST_Spring_Mean", "Spring Mean Land Surface Temperature", u"متوسط درجة حرارة سطح الأرض ربيعاً", "TS", "Land Surface Temperature", "Spring", "Mean", "C", u"متوسط أشهر الربيع (مارس، أبريل، مايو)", "Mean of Mar/Apr/May monthly TS means", "Mean of climatological months 3,4,5"),
    ("LST_Summer_Mean", "Summer Mean Land Surface Temperature", u"متوسط درجة حرارة سطح الأرض صيفاً", "TS", "Land Surface Temperature", "Summer", "Mean", "C", u"متوسط أشهر الصيف (يونيو، يوليو، أغسطس)", "Mean of Jun/Jul/Aug monthly TS means", "Mean of climatological months 6,7,8"),
    ("LST_Autumn_Mean", "Autumn Mean Land Surface Temperature", u"متوسط درجة حرارة سطح الأرض خريفاً", "TS", "Land Surface Temperature", "Autumn", "Mean", "C", u"متوسط أشهر الخريف (سبتمبر، أكتوبر، نوفمبر)", "Mean of Sep/Oct/Nov monthly TS means", "Mean of climatological months 9,10,11"),
    ("LST_Annual_Range", "Annual Land Surface Temperature Range", u"المدى السنوي لدرجة حرارة سطح الأرض", "TS", "Land Surface Temperature", "Annual", "Range", "C", u"أعلى متوسط شهري ناقص أدنى متوسط شهري", "Highest monthly TS mean minus lowest monthly TS mean", "max(clim monthly) - min(clim monthly)"),
    ("LST_minus_T_Annual", "Annual Surface-to-Air Temperature Difference", u"الفارق السنوي بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Annual", "Difference", "C", u"الفرق بين المتوسط السنوي لحرارة السطح وحرارة الهواء عند 2 م = LST - T2M", "Annual difference between skin and air temperature (LST - T2M)", "LST_Annual_Mean - T_Annual_Mean"),
    ("LST_minus_T_Winter", "Winter Surface-to-Air Temperature Difference", u"فارق الشتاء بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Winter", "Difference", "C", u"الفرق الشتوي بين حرارة السطح وحرارة الهواء = LST_Winter - T_Winter", "Winter difference between skin and air temperature (LST - T2M)", "LST_Winter_Mean - T_Winter_Mean"),
    ("LST_minus_T_Spring", "Spring Surface-to-Air Temperature Difference", u"فارق الربيع بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Spring", "Difference", "C", u"الفرق الربيعي بين حرارة السطح وحرارة الهواء = LST_Spring - T_Spring", "Spring difference between skin and air temperature (LST - T2M)", "LST_Spring_Mean - T_Spring_Mean"),
    ("LST_minus_T_Summer", "Summer Surface-to-Air Temperature Difference", u"فارق الصيف بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Summer", "Difference", "C", u"الفرق الصيفي بين حرارة السطح وحرارة الهواء = LST_Summer - T_Summer", "Summer difference between skin and air temperature (LST - T2M)", "LST_Summer_Mean - T_Summer_Mean"),
    ("LST_minus_T_Autumn", "Autumn Surface-to-Air Temperature Difference", u"فارق الخريف بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Autumn", "Difference", "C", u"الفرق الخريفي بين حرارة السطح وحرارة الهواء = LST_Autumn - T_Autumn", "Autumn difference between skin and air temperature (LST - T2M)", "LST_Autumn_Mean - T_Autumn_Mean"),
    ("LST_January_Mean", "January Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر يناير", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر يناير", "Mean of monthly TS for January across years", "Mean of January TS values"),
    ("LST_February_Mean", "February Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر فبراير", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر فبراير", "Mean of monthly TS for February across years", "Mean of February TS values"),
    ("LST_March_Mean", "March Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر مارس", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر مارس", "Mean of monthly TS for March across years", "Mean of March TS values"),
    ("LST_April_Mean", "April Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر أبريل", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر أبريل", "Mean of monthly TS for April across years", "Mean of April TS values"),
    ("LST_May_Mean", "May Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر مايو", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر مايو", "Mean of monthly TS for May across years", "Mean of May TS values"),
    ("LST_June_Mean", "June Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر يونيو", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر يونيو", "Mean of monthly TS for June across years", "Mean of June TS values"),
    ("LST_July_Mean", "July Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر يوليو", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر يوليو", "Mean of monthly TS for July across years", "Mean of July TS values"),
    ("LST_August_Mean", "August Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر أغسطس", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر أغسطس", "Mean of monthly TS for August across years", "Mean of August TS values"),
    ("LST_September_Mean", "September Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر سبتمبر", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر سبتمبر", "Mean of monthly TS for September across years", "Mean of September TS values"),
    ("LST_October_Mean", "October Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر أكتوبر", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر أكتوبر", "Mean of monthly TS for October across years", "Mean of October TS values"),
    ("LST_November_Mean", "November Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر نوفمبر", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر نوفمبر", "Mean of monthly TS for November across years", "Mean of November TS values"),
    ("LST_December_Mean", "December Mean Land Surface Temperature", u"متوسط حرارة سطح الأرض لشهر ديسمبر", "TS", "Land Surface Temperature", "Monthly", "Mean", "C", u"متوسط درجة حرارة سطح الأرض لشهر ديسمبر", "Mean of monthly TS for December across years", "Mean of December TS values"),
    ("LST_minus_T_January", "January Surface-to-Air Temperature Difference", u"فارق يناير بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر يناير = LST_Jan - T_Jan", "January difference between skin and air temperature (LST - T2M)", "LST_January_Mean - T_January_Mean"),
    ("LST_minus_T_February", "February Surface-to-Air Temperature Difference", u"فارق فبراير بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر فبراير = LST_Feb - T_Feb", "February difference between skin and air temperature (LST - T2M)", "LST_February_Mean - T_February_Mean"),
    ("LST_minus_T_March", "March Surface-to-Air Temperature Difference", u"فارق مارس بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر مارس = LST_Mar - T_Mar", "March difference between skin and air temperature (LST - T2M)", "LST_March_Mean - T_March_Mean"),
    ("LST_minus_T_April", "April Surface-to-Air Temperature Difference", u"فارق أبريل بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر أبريل = LST_Apr - T_Apr", "April difference between skin and air temperature (LST - T2M)", "LST_April_Mean - T_April_Mean"),
    ("LST_minus_T_May", "May Surface-to-Air Temperature Difference", u"فارق مايو بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر مايو = LST_May - T_May", "May difference between skin and air temperature (LST - T2M)", "LST_May_Mean - T_May_Mean"),
    ("LST_minus_T_June", "June Surface-to-Air Temperature Difference", u"فارق يونيو بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر يونيو = LST_Jun - T_Jun", "June difference between skin and air temperature (LST - T2M)", "LST_June_Mean - T_June_Mean"),
    ("LST_minus_T_July", "July Surface-to-Air Temperature Difference", u"فارق يوليو بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر يوليو = LST_Jul - T_Jul", "July difference between skin and air temperature (LST - T2M)", "LST_July_Mean - T_July_Mean"),
    ("LST_minus_T_August", "August Surface-to-Air Temperature Difference", u"فارق أغسطس بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر أغسطس = LST_Aug - T_Aug", "August difference between skin and air temperature (LST - T2M)", "LST_August_Mean - T_August_Mean"),
    ("LST_minus_T_September", "September Surface-to-Air Temperature Difference", u"فارق سبتمبر بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر سبتمبر = LST_Sep - T_Sep", "September difference between skin and air temperature (LST - T2M)", "LST_September_Mean - T_September_Mean"),
    ("LST_minus_T_October", "October Surface-to-Air Temperature Difference", u"فارق أكتوبر بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر أكتوبر = LST_Oct - T_Oct", "October difference between skin and air temperature (LST - T2M)", "LST_October_Mean - T_October_Mean"),
    ("LST_minus_T_November", "November Surface-to-Air Temperature Difference", u"فارق نوفمبر بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر نوفمبر = LST_Nov - T_Nov", "November difference between skin and air temperature (LST - T2M)", "LST_November_Mean - T_November_Mean"),
    ("LST_minus_T_December", "December Surface-to-Air Temperature Difference", u"فارق ديسمبر بين حرارة السطح وحرارة الهواء", "TS-T2M", "Land Surface Temperature", "Monthly", "Difference", "C", u"الفرق بين حرارة السطح وحرارة الهواء لشهر ديسمبر = LST_Dec - T_Dec", "December difference between skin and air temperature (LST - T2M)", "LST_December_Mean - T_December_Mean"),
]
for _def in _LST_DEFS:
    FIELD_DEFS.append(_def)
    MODULE_FIELDS.setdefault("Land Surface Temperature", []).append(_def[0])

FIELD_BY_NAME = dict((r[0], r) for r in FIELD_DEFS)
FIELD_ALIAS_AR = dict((r[0], r[2]) for r in FIELD_DEFS)

# Backward compatibility aliases:
MODULE_FIELDS["Climate_Models"] = [f for sm in DERIVED_MODULES_ALL for f in MODULE_FIELDS.get(sm, [])]
MODULE_FIELDS["Drought & Aridity"] = [
    "DM_Aridity_Annual", "PET_Hargreaves_Annual", "UNEP_Aridity_Annual",
    "Water_Deficit_Annual", "Dry_Months_Count"
]

# Monthly-climatology helpers: FIELD_DEFS index 5 holds the temporal period
# ("Monthly" for *_January_Mean ... *_December_Mean / ET_*_Total fields).
FIELD_PERIOD = {}
for _r in FIELD_DEFS:
    FIELD_PERIOD[_r[0]] = _r[5]


def is_monthly_field(fname):
    """True for 12-month climatology fields (*_January_Mean ... *_December_Mean,
    ET_*_Total, *_<Month>_Range). Used to route their rasters into the Month/ subfolder and to
    apply the unified monthly color stretch."""
    if not fname:
        return False
    if FIELD_PERIOD.get(fname) == "Monthly":
        return True
    for _mn in MONTH_NAMES_EN:
        if fname.endswith("_%s_Mean" % _mn) or fname.endswith("_%s_Total" % _mn):
            return True
        if fname.endswith("_%s_Range" % _mn):
            return True
        if fname in ("T_Anom_%s" % _mn, "R_Anom_%s" % _mn,
                     "R_Anom_%s_Pct" % _mn, "T_%s_Trend_Decade" % _mn,
                     "R_%s_Trend_Decade" % _mn):
            return True
    return False


def monthly_group_key(module, field):
    """Grouping key for the unified monthly stretch: one global min/max per
    element, with Wind speed and direction kept separate (different units).
    Trends & Anomalies monthly fields are split by variable group so that
    C, mm, mm/decade, C/decade and % never share one stretch."""
    if module == "Wind":
        return (module, "Spd" if field.startswith("W_Spd") else "Dir")
    if module == "Trends & Anomalies":
        if field.startswith(("T_Anom", "T_Annual_An")):
            return (module, "T_Anom")
        if field.startswith(("R_Anom", "R_Annual_An")) and field.endswith("_Pct"):
            return (module, "R_Anom_Pct")
        if field.startswith(("R_Anom", "R_Annual_An")):
            return (module, "R_Anom")
        if "Trend" in field:
            return (module, "T_Trend" if field.startswith("T_") else "R_Trend")
    return (module, "")

MODULE_SHORT = {
    "Temperature": "Temperature",
    "Precipitation": "Precipitation",
    "Sea Level Pressure": "Sea_Level_Pressure",
    "Surface Pressure": "Surface_Pressure",
    "Wind": "Wind",
    "Relative Humidity": "Relative_Humidity",
    "Dew Point": "Dew_Point",
    "Solar Radiation": "Solar_Radiation",
    "UV Index": "UV_Index",
    "Cloud Cover": "Cloud_Cover",
    "Heat Index": "Heat_Index",
    "Wind Chill": "Wind_Chill",
    "De Martonne Aridity": "De_Martonne_Aridity",
    "Evapotranspiration": "Evapotranspiration",
    "Hargreaves PET": "Evapotranspiration",
    "UNEP Aridity": "UNEP_Aridity",
    "Water Deficit": "Water_Deficit",
    "Dry Months": "Dry_Months",
    "Trends & Anomalies": "Trends_And_Anomalies",
    "Land Surface Temperature": "Land_Surface_Temperature",
    "Drought & Aridity": "Drought_Aridity",
    "Climate_Models": "Climate_Models",
}

for _sub_k, _can in CANONICAL_DERIVED_MAP.items():
    if _can in MODULE_SHORT and _sub_k not in MODULE_SHORT:
        MODULE_SHORT[_sub_k] = MODULE_SHORT[_can]

SHORT_TO_MODULE = dict((v, k) for k, v in MODULE_SHORT.items())


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
    "HI_January_Mean": "HI_JanMean",
    "HI_February_Mean": "HI_FebMean",
    "HI_March_Mean": "HI_MarMean",
    "HI_April_Mean": "HI_AprMean",
    "HI_May_Mean": "HI_MayMean",
    "HI_June_Mean": "HI_JunMean",
    "HI_July_Mean": "HI_JulMean",
    "HI_August_Mean": "HI_AugMean",
    "HI_September_Mean": "HI_SepMean",
    "HI_October_Mean": "HI_OctMean",
    "HI_November_Mean": "HI_NovMean",
    "HI_December_Mean": "HI_DecMean",
    "WBGT_Summer_Mean": "WBGT_SuMn",
    "HI_Summer_Mean": "HI_SumMean",
    "HI_Spring_Mean": "HI_SprMean",
    "HI_Autumn_Mean": "HI_AutMean",
    "HI_Winter_Mean": "HI_WinMean",
    "Interp_Meth": "Intrp_Meth",
    "Measurement_Unit": "Meas_Unit",
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
    "R_Annual_Range": "R_AnnRng",
    "R_Annual_Total": "R_AnnTot",
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
    "Td_Annual_Range": "Td_AnnRng",
    "Td_Autumn_Mean": "Td_AutMean",
    "Td_Spring_Mean": "Td_SprMean",
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
    "ET_Annual_Mean": "ET_AnnMean",
    "ET_Annual_Range": "ET_AnnRng",
    "ET_Winter_Mean": "ET_WinMean",
    "ET_Spring_Mean": "ET_SprMean",
    "ET_Summer_Mean": "ET_SumMean",
    "ET_Autumn_Mean": "ET_AutMean",
    "PET_Hargreaves_Annual": "PET_HarAnn",
    "UNEP_Aridity_Annual": "UNEP_Arid",
    "Water_Deficit_Annual": "WatDefAnn",
    "WC_Winter_Mean": "WC_WinMean",
    "WC_Spring_Mean": "WC_SprMean",
    "WC_Summer_Mean": "WC_SumMean",
    "WC_Autumn_Mean": "WC_AutMean",
    "WC_Annual_Mean": "WC_AnnMean",
    "WC_Annual_Range": "WC_AnRng",
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
    # --- Monthly Field Abbreviations ---
    "Cld_April_Mean": "Cld_AprMn",
    "Cld_August_Mean": "Cld_AugMn",
    "Cld_December_Mean": "Cld_DecMn",
    "Cld_February_Mean": "Cld_FebMn",
    "Cld_January_Mean": "Cld_JanMn",
    "Cld_July_Mean": "Cld_JulMn",
    "Cld_June_Mean": "Cld_JunMn",
    "Cld_March_Mean": "Cld_MarMn",
    "Cld_May_Mean": "Cld_MayMn",
    "Cld_November_Mean": "Cld_NovMn",
    "Cld_October_Mean": "Cld_OctMn",
    "Cld_September_Mean": "Cld_SepMn",
    "ET_April_Mean": "ET_AprMean",
    "ET_August_Mean": "ET_AugMean",
    "ET_December_Mean": "ET_DecMean",
    "ET_February_Mean": "ET_FebMean",
    "ET_January_Mean": "ET_JanMean",
    "ET_July_Mean": "ET_JulMean",
    "ET_June_Mean": "ET_JunMean",
    "ET_March_Mean": "ET_MarMean",
    "ET_May_Mean": "ET_MayMean",
    "ET_November_Mean": "ET_NovMean",
    "ET_October_Mean": "ET_OctMean",
    "ET_September_Mean": "ET_SepMean",
    "PSL_April_Mean": "PSL_AprMn",
    "PSL_August_Mean": "PSL_AugMn",
    "PSL_December_Mean": "PSL_DecMn",
    "PSL_February_Mean": "PSL_FebMn",
    "PSL_January_Mean": "PSL_JanMn",
    "PSL_July_Mean": "PSL_JulMn",
    "PSL_June_Mean": "PSL_JunMn",
    "PSL_March_Mean": "PSL_MarMn",
    "PSL_May_Mean": "PSL_MayMn",
    "PSL_November_Mean": "PSL_NovMn",
    "PSL_October_Mean": "PSL_OctMn",
    "PSL_September_Mean": "PSL_SepMn",
    "PS_April_Mean": "PS_AprMean",
    "PS_August_Mean": "PS_AugMean",
    "PS_December_Mean": "PS_DecMean",
    "PS_February_Mean": "PS_FebMean",
    "PS_January_Mean": "PS_JanMean",
    "PS_July_Mean": "PS_JulMean",
    "PS_June_Mean": "PS_JunMean",
    "PS_March_Mean": "PS_MarMean",
    "PS_May_Mean": "PS_MayMean",
    "PS_November_Mean": "PS_NovMean",
    "PS_October_Mean": "PS_OctMean",
    "PS_September_Mean": "PS_SepMean",
    "RH_April_Mean": "RH_AprMean",
    "RH_August_Mean": "RH_AugMean",
    "RH_December_Mean": "RH_DecMean",
    "RH_February_Mean": "RH_FebMean",
    "RH_January_Mean": "RH_JanMean",
    "RH_July_Mean": "RH_JulMean",
    "RH_June_Mean": "RH_JunMean",
    "RH_March_Mean": "RH_MarMean",
    "RH_May_Mean": "RH_MayMean",
    "RH_November_Mean": "RH_NovMean",
    "RH_October_Mean": "RH_OctMean",
    "RH_September_Mean": "RH_SepMean",
    "R_April_Mean": "R_AprMean",
    "R_August_Mean": "R_AugMean",
    "R_December_Mean": "R_DecMean",
    "R_February_Mean": "R_FebMean",
    "R_January_Mean": "R_JanMean",
    "R_July_Mean": "R_JulMean",
    "R_June_Mean": "R_JunMean",
    "R_March_Mean": "R_MarMean",
    "R_May_Mean": "R_MayMean",
    "R_November_Mean": "R_NovMean",
    "R_October_Mean": "R_OctMean",
    "R_September_Mean": "R_SepMean",
    "Sol_April_Mean": "Sol_AprMn",
    "Sol_August_Mean": "Sol_AugMn",
    "Sol_December_Mean": "Sol_DecMn",
    "Sol_February_Mean": "Sol_FebMn",
    "Sol_January_Mean": "Sol_JanMn",
    "Sol_July_Mean": "Sol_JulMn",
    "Sol_June_Mean": "Sol_JunMn",
    "Sol_March_Mean": "Sol_MarMn",
    "Sol_May_Mean": "Sol_MayMn",
    "Sol_November_Mean": "Sol_NovMn",
    "Sol_October_Mean": "Sol_OctMn",
    "Sol_September_Mean": "Sol_SepMn",
    "T_April_Mean": "T_AprMean",
    "T_August_Mean": "T_AugMean",
    "T_December_Mean": "T_DecMean",
    "T_February_Mean": "T_FebMean",
    "T_January_Mean": "T_JanMean",
    "T_July_Mean": "T_JulMean",
    "T_June_Mean": "T_JunMean",
    "T_March_Mean": "T_MarMean",
    "T_May_Mean": "T_MayMean",
    "T_November_Mean": "T_NovMean",
    "T_October_Mean": "T_OctMean",
    "T_September_Mean": "T_SepMean",
    "Td_April_Mean": "Td_AprMean",
    "Td_August_Mean": "Td_AugMean",
    "Td_December_Mean": "Td_DecMean",
    "Td_February_Mean": "Td_FebMean",
    "Td_January_Mean": "Td_JanMean",
    "Td_July_Mean": "Td_JulMean",
    "Td_June_Mean": "Td_JunMean",
    "Td_March_Mean": "Td_MarMean",
    "Td_May_Mean": "Td_MayMean",
    "Td_November_Mean": "Td_NovMean",
    "Td_October_Mean": "Td_OctMean",
    "Td_September_Mean": "Td_SepMean",
    "UV_April_Mean": "UV_AprMean",
    "UV_August_Mean": "UV_AugMean",
    "UV_December_Mean": "UV_DecMean",
    "UV_February_Mean": "UV_FebMean",
    "UV_January_Mean": "UV_JanMean",
    "UV_July_Mean": "UV_JulMean",
    "UV_June_Mean": "UV_JunMean",
    "UV_March_Mean": "UV_MarMean",
    "UV_May_Mean": "UV_MayMean",
    "UV_November_Mean": "UV_NovMean",
    "UV_October_Mean": "UV_OctMean",
    "UV_September_Mean": "UV_SepMean",
    "W_Dir_April_Mean": "WDr_AprMn",
    "W_Dir_August_Mean": "WDr_AugMn",
    "W_Dir_December_Mean": "WDr_DecMn",
    "W_Dir_February_Mean": "WDr_FebMn",
    "W_Dir_January_Mean": "WDr_JanMn",
    "W_Dir_July_Mean": "WDr_JulMn",
    "W_Dir_June_Mean": "WDr_JunMn",
    "W_Dir_March_Mean": "WDr_MarMn",
    "W_Dir_May_Mean": "WDr_MayMn",
    "W_Dir_November_Mean": "WDr_NovMn",
    "W_Dir_October_Mean": "WDr_OctMn",
    "W_Dir_September_Mean": "WDr_SepMn",
    "W_Spd_April_Mean": "WSp_AprMn",
    "W_Spd_August_Mean": "WSp_AugMn",
    "W_Spd_December_Mean": "WSp_DecMn",
    "W_Spd_February_Mean": "WSp_FebMn",
    "W_Spd_January_Mean": "WSp_JanMn",
    "W_Spd_July_Mean": "WSp_JulMn",
    "W_Spd_June_Mean": "WSp_JunMn",
    "W_Spd_March_Mean": "WSp_MarMn",
    "W_Spd_May_Mean": "WSp_MayMn",
    "W_Spd_November_Mean": "WSp_NovMn",
    "W_Spd_October_Mean": "WSp_OctMn",
    "W_Spd_September_Mean": "WSp_SepMn",
    "T_January_Range": "T_JanRng",
    "T_February_Range": "T_FebRng",
    "T_March_Range": "T_MarRng",
    "T_April_Range": "T_AprRng",
    "T_May_Range": "T_MayRng",
    "T_June_Range": "T_JunRng",
    "T_July_Range": "T_JulRng",
    "T_August_Range": "T_AugRng",
    "T_September_Range": "T_SepRng",
    "T_October_Range": "T_OctRng",
    "T_November_Range": "T_NovRng",
    "T_December_Range": "T_DecRng",
    "R_January_Range": "R_JanRng",
    "R_February_Range": "R_FebRng",
    "R_March_Range": "R_MarRng",
    "R_April_Range": "R_AprRng",
    "R_May_Range": "R_MayRng",
    "R_June_Range": "R_JunRng",
    "R_July_Range": "R_JulRng",
    "R_August_Range": "R_AugRng",
    "R_September_Range": "R_SepRng",
    "R_October_Range": "R_OctRng",
    "R_November_Range": "R_NovRng",
    "R_December_Range": "R_DecRng",
    "PSL_January_Range": "PSL_JanRg",
    "PSL_February_Range": "PSL_FebRg",
    "PSL_March_Range": "PSL_MarRg",
    "PSL_April_Range": "PSL_AprRg",
    "PSL_May_Range": "PSL_MayRg",
    "PSL_June_Range": "PSL_JunRg",
    "PSL_July_Range": "PSL_JulRg",
    "PSL_August_Range": "PSL_AugRg",
    "PSL_September_Range": "PSL_SepRg",
    "PSL_October_Range": "PSL_OctRg",
    "PSL_November_Range": "PSL_NovRg",
    "PSL_December_Range": "PSL_DecRg",
    "PS_January_Range": "PS_JanRng",
    "PS_February_Range": "PS_FebRng",
    "PS_March_Range": "PS_MarRng",
    "PS_April_Range": "PS_AprRng",
    "PS_May_Range": "PS_MayRng",
    "PS_June_Range": "PS_JunRng",
    "PS_July_Range": "PS_JulRng",
    "PS_August_Range": "PS_AugRng",
    "PS_September_Range": "PS_SepRng",
    "PS_October_Range": "PS_OctRng",
    "PS_November_Range": "PS_NovRng",
    "PS_December_Range": "PS_DecRng",
    "W_Spd_January_Range": "WSp_JanRg",
    "W_Spd_February_Range": "WSp_FebRg",
    "W_Spd_March_Range": "WSp_MarRg",
    "W_Spd_April_Range": "WSp_AprRg",
    "W_Spd_May_Range": "WSp_MayRg",
    "W_Spd_June_Range": "WSp_JunRg",
    "W_Spd_July_Range": "WSp_JulRg",
    "W_Spd_August_Range": "WSp_AugRg",
    "W_Spd_September_Range": "WSp_SepRg",
    "W_Spd_October_Range": "WSp_OctRg",
    "W_Spd_November_Range": "WSp_NovRg",
    "W_Spd_December_Range": "WSp_DecRg",
    "RH_January_Range": "RH_JanRng",
    "RH_February_Range": "RH_FebRng",
    "RH_March_Range": "RH_MarRng",
    "RH_April_Range": "RH_AprRng",
    "RH_May_Range": "RH_MayRng",
    "RH_June_Range": "RH_JunRng",
    "RH_July_Range": "RH_JulRng",
    "RH_August_Range": "RH_AugRng",
    "RH_September_Range": "RH_SepRng",
    "RH_October_Range": "RH_OctRng",
    "RH_November_Range": "RH_NovRng",
    "RH_December_Range": "RH_DecRng",
    "Td_January_Range": "Td_JanRng",
    "Td_February_Range": "Td_FebRng",
    "Td_March_Range": "Td_MarRng",
    "Td_April_Range": "Td_AprRng",
    "Td_May_Range": "Td_MayRng",
    "Td_June_Range": "Td_JunRng",
    "Td_July_Range": "Td_JulRng",
    "Td_August_Range": "Td_AugRng",
    "Td_September_Range": "Td_SepRng",
    "Td_October_Range": "Td_OctRng",
    "Td_November_Range": "Td_NovRng",
    "Td_December_Range": "Td_DecRng",
    "Sol_January_Range": "Sol_JanRg",
    "Sol_February_Range": "Sol_FebRg",
    "Sol_March_Range": "Sol_MarRg",
    "Sol_April_Range": "Sol_AprRg",
    "Sol_May_Range": "Sol_MayRg",
    "Sol_June_Range": "Sol_JunRg",
    "Sol_July_Range": "Sol_JulRg",
    "Sol_August_Range": "Sol_AugRg",
    "Sol_September_Range": "Sol_SepRg",
    "Sol_October_Range": "Sol_OctRg",
    "Sol_November_Range": "Sol_NovRg",
    "Sol_December_Range": "Sol_DecRg",
    "UV_January_Range": "UV_JanRng",
    "UV_February_Range": "UV_FebRng",
    "UV_March_Range": "UV_MarRng",
    "UV_April_Range": "UV_AprRng",
    "UV_May_Range": "UV_MayRng",
    "UV_June_Range": "UV_JunRng",
    "UV_July_Range": "UV_JulRng",
    "UV_August_Range": "UV_AugRng",
    "UV_September_Range": "UV_SepRng",
    "UV_October_Range": "UV_OctRng",
    "UV_November_Range": "UV_NovRng",
    "UV_December_Range": "UV_DecRng",
    "Cld_January_Range": "Cld_JanRg",
    "Cld_February_Range": "Cld_FebRg",
    "Cld_March_Range": "Cld_MarRg",
    "Cld_April_Range": "Cld_AprRg",
    "Cld_May_Range": "Cld_MayRg",
    "Cld_June_Range": "Cld_JunRg",
    "Cld_July_Range": "Cld_JulRg",
    "Cld_August_Range": "Cld_AugRg",
    "Cld_September_Range": "Cld_SepRg",
    "Cld_October_Range": "Cld_OctRg",
    "Cld_November_Range": "Cld_NovRg",
    "Cld_December_Range": "Cld_DecRg",
    "ET_January_Range": "ET_JanRng",
    "ET_February_Range": "ET_FebRng",
    "ET_March_Range": "ET_MarRng",
    "ET_April_Range": "ET_AprRng",
    "ET_May_Range": "ET_MayRng",
    "ET_June_Range": "ET_JunRng",
    "ET_July_Range": "ET_JulRng",
    "ET_August_Range": "ET_AugRng",
    "ET_September_Range": "ET_SepRng",
    "ET_October_Range": "ET_OctRng",
    "ET_November_Range": "ET_NovRng",
    "ET_December_Range": "ET_DecRng",
}

# Monthly trend/anomaly short names (<=10 chars, same *_<Mon3> pattern).
_TREND_SHP_ABBR = {"January": "Jan", "February": "Feb", "March": "Mar",
                   "April": "Apr", "May": "May", "June": "Jun", "July": "Jul",
                   "August": "Aug", "September": "Sep", "October": "Oct",
                   "November": "Nov", "December": "Dec"}
for _mn, _ab in _TREND_SHP_ABBR.items():
    SHP_FIELD_MAP.setdefault("T_Anom_%s" % _mn, "T_Anom%s" % _ab)
    SHP_FIELD_MAP.setdefault("R_Anom_%s" % _mn, "R_Anom%s" % _ab)
    SHP_FIELD_MAP.setdefault("R_Anom_%s_Pct" % _mn, "R_An%sPct" % _ab)
    SHP_FIELD_MAP.setdefault("T_%s_Trend_Decade" % _mn, "T_%sTrDec" % _ab)
    SHP_FIELD_MAP.setdefault("R_%s_Trend_Decade" % _mn, "R_%sTrDec" % _ab)
# Seasonal complements short names (<=10 chars).
for _fld, _shp in (("T_Anom_Spring", "T_AnomSpr"), ("T_Anom_Autumn", "T_AnomAut"),
                   ("R_Anom_Spring", "R_AnomSpr"), ("R_Anom_Spring_Pct", "R_AnSpPct"),
                   ("R_Anom_Summer", "R_AnomSum"), ("R_Anom_Summer_Pct", "R_AnSuPct"),
                   ("R_Anom_Autumn", "R_AnomAut"), ("R_Anom_Autumn_Pct", "R_AnAuPct"),
                   ("T_Winter_Trend_Decade", "T_WinTrDec"), ("T_Spring_Trend_Decade", "T_SprTrDec"),
                   ("T_Summer_Trend_Decade", "T_SumTrDec"), ("T_Autumn_Trend_Decade", "T_AutTrDec"),
                   ("R_Winter_Trend_Decade", "R_WinTrDec"), ("R_Spring_Trend_Decade", "R_SprTrDec"),
                   ("R_Summer_Trend_Decade", "R_SumTrDec"), ("R_Autumn_Trend_Decade", "R_AutTrDec")):
    SHP_FIELD_MAP.setdefault(_fld, _shp)
# General-monthly aggregates short names (<=10 chars).
for _fld, _shp in (("T_Anom_Month", "T_AnomMon"), ("R_Anom_Month", "R_AnomMon"),
                   ("R_Anom_Month_Pct", "R_AnMonPct"),
                   ("T_Month_Trend_Decade", "T_MonTrDec"), ("R_Month_Trend_Decade", "R_MonTrDec")):
    SHP_FIELD_MAP.setdefault(_fld, _shp)

# Land Surface Temperature short names (<=10 chars).
_LST_SHP_MAP = {
    "LST_Annual_Mean": "LST_AnMean",
    "LST_Winter_Mean": "LST_WinMn",
    "LST_Spring_Mean": "LST_SprMn",
    "LST_Summer_Mean": "LST_SumMn",
    "LST_Autumn_Mean": "LST_AutMn",
    "LST_Annual_Range": "LST_AnRng",
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
for _fld, _shp in _LST_SHP_MAP.items():
    SHP_FIELD_MAP.setdefault(_fld, _shp)

REV_SHP_MAP = dict((v, k) for k, v in SHP_FIELD_MAP.items())


def field_display_label(r):
    """Clean label for ArcMap GPString checklist (no semicolons!)."""
    return "%s - %s" % (r[0], r[1])


def parse_season_name(s_text):
    """Normalize 'Winter (DJF)' -> 'Winter'"""
    for s in ("Winter", "Spring", "Summer", "Autumn"):
        if s.lower() in s_text.lower():
            return s
    return s_text


def parse_temporal_scope(t_scope):
    """Normalize list or semicolon string of scopes to set of temporal scopes.
    Defaults to all standard scopes if None or empty."""
    if not t_scope:
        return {"Annual", "Winter", "Spring", "Summer", "Autumn"}
    if isinstance(t_scope, (list, tuple)):
        raw = t_scope
    else:
        raw = str(t_scope).split(";")
    res = set()
    for item in raw:
        s = str(item).strip().strip("'\"")
        for norm in ("Annual", "Winter", "Spring", "Summer", "Autumn"):
            if norm.lower() in s.lower():
                res.add(norm)
    return res if res else {"Annual", "Winter", "Spring", "Summer", "Autumn"}


def get_field_temporal_scope(fname):
    """Returns 'Annual', 'Winter', 'Spring', 'Summer', 'Autumn', or 'Monthly' for any field name."""
    f = fname.upper()
    for _m in ("JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
               "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"):
        if _m in f:
            return "Monthly"
    if ("WINTER" in f or "_WIN" in f or "_WN" in f or "WNMEAN" in f or "WINMEAN" in f or "MIN_WINTER" in f) and not fname.endswith("_Range"):
        return "Winter"
    if ("SPRING" in f or "_SPR" in f or "SPMEAN" in f or "SPRMEAN" in f) and not fname.endswith("_Range"):
        return "Spring"
    if ("SUMMER" in f or "_SUM" in f or "SUMEAN" in f or "SUMMEAN" in f or "MAX_SUMMER" in f or "WBGT_SUMMER" in f or "SUMN" in f) and not fname.endswith("_Range"):
        return "Summer"
    if ("AUTUMN" in f or "_AUT" in f or "AUMEAN" in f or "AUTMEAN" in f) and not fname.endswith("_Range"):
        return "Autumn"
    if fname in ("T_Anom_Month", "R_Anom_Month", "R_Anom_Month_Pct", "T_Month_Trend_Decade", "R_Month_Trend_Decade"):
        return "Monthly"
    fdef = FIELD_BY_NAME.get(fname)
    if fdef and len(fdef) > 5:
        s_val = fdef[5]
        if s_val == "Monthly" or s_val in MONTH_NAMES_EN:
            return "Monthly"
        if s_val in ("Annual", "Winter", "Spring", "Summer", "Autumn"):
            return s_val
    return "Annual"


def get_candidate_fields(modules, aggregations=None, seasons=None, temporal_scope=None):
    """Returns list of (field_name, display_label, module) for active criteria."""
    t_set = parse_temporal_scope(temporal_scope) if temporal_scope else None
    if aggregations is None:
        aggregations = [
            "Annual Summaries",
            "Seasonal Summaries",
            "Extreme & Bioclimatic Indices"
        ]
    if seasons is None:
        seasons = ["Winter", "Spring", "Summer", "Autumn"]
    else:
        seasons = [parse_season_name(s) for s in seasons]

    want_ann = any("Annual" in a for a in aggregations)
    want_sea = any("Seasonal" in a for a in aggregations)
    want_mon = any("Monthly Climatology" in a or "الشهريات" in a for a in aggregations)
    want_ext = any("Extreme" in a or "Indices" in a for a in aggregations)

    candidates = []
    for r in FIELD_DEFS:
        fname, en_label, _ar, _raw, mod, s_type, stat, _u = r[:8]
        if mod not in modules:
            continue

        f_scope = get_field_temporal_scope(fname)
        if t_set is not None and f_scope in ("Winter", "Spring", "Summer", "Autumn") and f_scope not in t_set:
            continue

        is_season = (f_scope in ("Winter", "Spring", "Summer", "Autumn"))
        is_monthly = (f_scope == "Monthly")
        is_extreme = (stat in ("Range", "Max", "Min", "Count") or fname.startswith("HI_") or fname.startswith("WC_"))

        match = False
        if is_season:
            if want_sea and (f_scope in seasons):
                match = True
        elif is_monthly:
            if want_mon:
                match = True
        else:
            if is_extreme:
                if want_ext or want_ann:
                    match = True
            else:
                if want_ann:
                    match = True

        if match:
            candidates.append((fname, field_display_label(r), mod))
    return candidates


def resolve_filtered_fields(modules, scope, aggregations=None, seasons=None, custom_fields=None, temporal_scope=None):
    """Returns {module: [field_names]} based on user filtering configuration and temporal scope."""
    out = dict((m, []) for m in modules)
    t_set = parse_temporal_scope(temporal_scope) if temporal_scope else None

    # Dedicated Period Execution Scopes
    if scope and ("Annual Only" in scope or "Annual Summaries" in scope or "سنوي فقط" in scope):
        for m in modules:
            for f in MODULE_FIELDS.get(m, []):
                if get_field_temporal_scope(f) == "Annual":
                    out[m].append(f)
        return out

    if scope and ("Seasonal Only" in scope or "Seasonal Summaries" in scope or "فصلي فقط" in scope):
        for m in modules:
            for f in MODULE_FIELDS.get(m, []):
                if get_field_temporal_scope(f) in ("Winter", "Spring", "Summer", "Autumn"):
                    out[m].append(f)
        return out

    if scope and ("Monthly Climatology Only" in scope or "شهري تفصيلي" in scope or ("Monthly Only" in scope and "Overall" not in scope)):
        for m in modules:
            for f in MODULE_FIELDS.get(m, []):
                if get_field_temporal_scope(f) == "Monthly":
                    out[m].append(f)
        return out

    if not scope or scope.startswith("All Variables") or "Full Suite" in scope:
        for m in modules:
            for f in MODULE_FIELDS.get(m, []):
                f_scope = get_field_temporal_scope(f)
                if t_set is None or f_scope in t_set or (f_scope == "Monthly" and len(t_set) == 5):
                    out[m].append(f)
        return out

    if scope.startswith("Custom Field"):
        selected_raw = []
        if custom_fields:
            if isinstance(custom_fields, (list, tuple)):
                selected_raw = list(custom_fields)
            else:
                selected_raw = [x.strip() for x in str(custom_fields).split(";") if x.strip()]

        chosen_names = set()
        for item in selected_raw:
            cleaned = item.strip("'\"")
            fname = cleaned.split(" - ")[0].strip()
            if fname in FIELD_BY_NAME:
                chosen_names.add(fname)

        for m in modules:
            for f in MODULE_FIELDS.get(m, []):
                if f in chosen_names:
                    f_scope = get_field_temporal_scope(f)
                    if t_set is None or f_scope in t_set or (f_scope == "Monthly" and len(t_set) == 5):
                        out[m].append(f)
        return out

    # "Filter by Seasons & Aggregations"
    candidates = get_candidate_fields(modules, aggregations, seasons, temporal_scope=temporal_scope)
    for fname, _lbl, mod in candidates:
        if mod in out and fname not in out[mod]:
            out[mod].append(fname)
    return out


def metadata_rows_for_modules(modules, wanted_fields_by_module=None):
    rows = []
    wanted_all = set()
    if wanted_fields_by_module:
        for m_name in modules:
            for f_name in wanted_fields_by_module.get(m_name, []):
                wanted_all.add(f_name)
    for r in FIELD_DEFS:
        is_in_mod = (r[4] in modules)
        if is_in_mod:
            if wanted_fields_by_module is not None and r[0] not in wanted_all:
                continue
            rows.append({
                "Field_Name": r[0], "Full_Name_EN": r[1], "Name_AR": r[2],
                "NASA_Code": r[3], "Module": r[4],
                "Period": r[5], "Statistic": r[6], "Unit": r[7], "Description_AR": r[8],
                "Description_EN": r[9], "Calculation": r[10],
                "Source": "NASA POWER", "Notes": "",
            })
    return rows


# ---------------------------------------------------------------------------
# NASA POWER client (requests preferred, urllib2 fallback for old installs)
# ---------------------------------------------------------------------------

def nasa_url(temporal, lat, lon, start_year, end_year, params, start_date=None, end_date=None):
    t = "monthly" if temporal == "Monthly" else "daily"
    if temporal == "Monthly":
        start, end = str(start_year), str(end_year)
    else:
        if start_date and end_date:
            start = str(start_date).replace("-", "")
            end = str(end_date).replace("-", "")
        else:
            start, end = "%d0101" % start_year, "%d1231" % end_year
    return (
        "%s/%s/point?parameters=%s&community=%s&longitude=%s&latitude=%s"
        "&start=%s&end=%s&format=JSON"
        % (NASA_BASE, t, ",".join(params), NASA_COMMUNITY,
           repr(float(lon)), repr(float(lat)), start, end)
    )


def _http_get_json(url, timeout, session=None):
    if _HAS_REQUESTS:
        get = (session.get if session is not None else requests.get)
        resp = get(url, timeout=timeout,
                   headers={"User-Agent": "POWER-Climate-Atlas-Generator/1.0-arcmap10"})
        if resp.status_code != 200:
            raise RuntimeError("HTTP %s: %s" % (resp.status_code, resp.text[:300]))
        return resp.json()
    # fallback for environments without requests
    if PY27:
        import urllib2
    else:
        import urllib.request as urllib2
    req = urllib2.Request(url, headers={"User-Agent": "POWER-Climate-Atlas-Generator/1.0-arcmap10"})
    resp = urllib2.urlopen(req, timeout=timeout)
    return json.load(resp)


def fetch_nasa_point(lat, lon, start_year, end_year, params, temporal="Monthly",
                     timeout=60, retries=3, session=None, start_date=None, end_date=None):
    """Returns properties.parameter dict. Raises RuntimeError after retries."""
    url = nasa_url(temporal, lat, lon, start_year, end_year, params,
                   start_date=start_date, end_date=end_date)
    last_err = None
    for attempt in range(retries):
        try:
            data = _http_get_json(url, timeout, session)
            try:
                return data["properties"]["parameter"]
            except KeyError:
                raise RuntimeError("Unexpected NASA response: %s" % str(data)[:300])
        except Exception as ex:
            last_err = ex
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("NASA request failed (%s): %s" % (url, last_err))


def parse_monthly_series(raw_dict):
    """raw: {YYYYMM: value} -> {(y,m): value}. Skips non-month keys (e.g. ANN='YYYY13')."""
    out = {}
    if not raw_dict:
        return out
    for k, v in raw_dict.items():
        try:
            ks = str(k)
            y, m = int(ks[:4]), int(ks[4:6])
            if 1 <= m <= 12:
                out[(y, m)] = float(v)
        except Exception:
            continue
    return out


def parse_daily_series(raw_dict):
    """raw: {YYYYMMDD: value} -> {(y,m,d): value}."""
    out = {}
    if not raw_dict:
        return out
    for k, v in raw_dict.items():
        try:
            ks = str(k)
            out[(int(ks[:4]), int(ks[4:6]), int(ks[6:8]))] = float(v)
        except Exception:
            continue
    return out


def build_monthly_from_daily(parameter_dict, mean_params, sum_params, years):
    """Convert daily NASA response to monthly {(y,m): v} per param."""
    monthly = {}
    for p in set(mean_params) | set(sum_params):
        daily = parse_daily_series(parameter_dict.get(p, {}))
        by_month = {}
        for ymd, v in daily.items():
            by_month.setdefault((ymd[0], ymd[1]), []).append(v)
        m = {}
        for ym, vals in by_month.items():
            if p in sum_params:
                try:
                    _exp = calendar.monthrange(int(ym[0]), int(ym[1]))[1]
                except Exception:
                    _exp = None
                m[ym] = safe_sum(vals, expected=_exp)
            else:
                m[ym] = safe_mean(vals)
        monthly[p] = m
    return monthly


def fill_interior_gaps(monthly, method="climatological"):
    """Fill missing months.

    method:
      'climatological' (recommended): fill with the mean of the same calendar
          month across all available years. If single-year or month missing across
          all years, fallback to overall station mean.
      'linear': linear interpolation between nearest valid neighbours in
          chronological order, with boundary fill for leading/trailing months.
      'none': no filling -- skip missing values.

    Returns a new dict with gaps filled; original is not mutated."""
    if method == "none" or not monthly:
        return dict(monthly)
    out = dict(monthly)
    if method == "climatological":
        # Mean of same calendar month across years
        by_cal = {}  # m -> [values]
        for (y, m), v in monthly.items():
            if not is_missing(v):
                by_cal.setdefault(m, []).append(float(v))
        cal_mean = {}
        for m, vals in by_cal.items():
            if vals:
                cal_mean[m] = sum(vals) / len(vals)
        all_vals = [float(v) for v in monthly.values() if not is_missing(v)]
        overall_mean = (sum(all_vals) / len(all_vals)) if all_vals else None

        for (y, m), v in list(out.items()):
            if is_missing(v):
                if m in cal_mean:
                    out[(y, m)] = cal_mean[m]
                elif overall_mean is not None:
                    out[(y, m)] = overall_mean
        # Also fill completely missing (y,m) keys if that year has any data
        years_present = set(y for (y, _m) in monthly)
        for y in years_present:
            has_any = any(not is_missing(monthly.get((y, mm)))
                          for mm in range(1, 13))
            if has_any:
                for mm in range(1, 13):
                    if (y, mm) not in out or is_missing(out.get((y, mm))):
                        if mm in cal_mean:
                            out[(y, mm)] = cal_mean[mm]
                        elif overall_mean is not None:
                            out[(y, mm)] = overall_mean
    elif method in ("linear", "linear_boundary"):
        keys = sorted(out.keys())
        if not keys:
            return out
        valid_indices = [i for i, k in enumerate(keys) if not is_missing(out[k])]
        if not valid_indices:
            return out
        first_valid_i = valid_indices[0]
        last_valid_i = valid_indices[-1]
        first_valid_v = float(out[keys[first_valid_i]])
        last_valid_v = float(out[keys[last_valid_i]])

        # 1. Leading boundary fill (e.g. Jan before first valid)
        for i in range(first_valid_i):
            out[keys[i]] = first_valid_v

        # 2. Interior linear interpolation
        for i in range(first_valid_i + 1, last_valid_i):
            if not is_missing(out[keys[i]]):
                continue
            prev_i, prev_v = None, None
            for j in range(i - 1, -1, -1):
                if not is_missing(out[keys[j]]):
                    prev_i, prev_v = j, float(out[keys[j]])
                    break
            next_i, next_v = None, None
            for j in range(i + 1, len(keys)):
                if not is_missing(out[keys[j]]):
                    next_i, next_v = j, float(out[keys[j]])
                    break
            if prev_v is not None and next_v is not None:
                span = next_i - prev_i
                frac = float(i - prev_i) / span
                out[keys[i]] = prev_v + frac * (next_v - prev_v)

        # 3. Trailing boundary fill (e.g. Dec after last valid)
        for i in range(last_valid_i + 1, len(keys)):
            out[keys[i]] = last_valid_v
    return out


def spatial_impute_missing(results, modules):
    """Fill missing field values in results using Inverse Distance Weighting of
    the nearest valid stations, ensuring no point row is left blank or failed."""
    count = 0
    for m in modules:
        fields = MODULE_FIELDS.get(m, [])
        for f in fields:
            valid_pts = []
            for r in results:
                v = r.get("fields", {}).get(f)
                if v is not None and not is_missing(v):
                    valid_pts.append((float(r["lat"]), float(r["lon"]), float(v)))
            if not valid_pts:
                continue
            for r in results:
                v = r.get("fields", {}).get(f)
                if v is None or is_missing(v):
                    rlat, rlon = float(r["lat"]), float(r["lon"])
                    dists = []
                    for vlat, vlon, val in valid_pts:
                        # Equirectangular metres (same as thin_points_tolerance):
                        # plain degree hypot() overweights E-W gaps at high latitudes.
                        mlat = math.radians((rlat + vlat) / 2.0)
                        dx = (rlon - vlon) * 111320.0 * math.cos(mlat)
                        dy = (rlat - vlat) * 111320.0
                        d = math.sqrt(dx * dx + dy * dy)
                        dists.append((d, val))
                    dists.sort(key=lambda x: x[0])
                    top = dists[:min(3, len(dists))]
                    if top[0][0] < 1.0:
                        imputed = top[0][1]
                    else:
                        w_sum = sum(1.0 / max(d[0], 1e-6) for d in top)
                        imputed = sum((1.0 / max(d[0], 1e-6)) * d[1] for d in top) / w_sum
                    r.setdefault("fields", {})[f] = round(imputed, 3)
                    if r.get("status") != "OK":
                        r["status"] = "OK (Gap-Filled)"
                    count += 1
    return count


# ---------------------------------------------------------------------------
# Open-Meteo Historical API (ERA5 reanalysis) client — pure python + requests
# Daily aggregates where the archive provides them, hourly aggregates (averaged
# to monthly by us) where it does not. Output feeds the SAME monthly structure
# and compute_point_fields as NASA, so the field table never changes.
# ---------------------------------------------------------------------------
ADMIN_FIELDS = [
    ("Source_ID", "LONG", "Original point ID"),
    ("Point_Lat", "DOUBLE", "Point latitude WGS84"),
    ("Point_Lon", "DOUBLE", "Point longitude WGS84"),
    ("Data_Start", "TEXT", "Time series start date or year"),
    ("Data_End", "TEXT", "Time series end date or year"),
    ("Temporal", "TEXT", "Temporal frequency (Monthly)"),
    ("Interp_Meth", "TEXT", "Spatial interpolation algorithm"),
    ("Cell_Size", "DOUBLE", "Base raster cell size in meters"),
    ("Wind_Cell", "DOUBLE", "Wind grid cell size in meters"),
    ("Measurement_Unit", "TEXT", "Measurement_Unit"),
    ("Status", "TEXT", "Point processing status (OK / Error)"),
    ("Error_Msg", "TEXT", "Error message if any"),
]

# Arabic display aliases for ADMIN_FIELDS (used only by the optional Arabic-DB copy).
# Field NAMES never change, so the copy stays reusable as offline input.
ADMIN_AR = {
    "Source_ID": u"المعرف الأصلي للنقطة",
    "Point_Lat": u"دائرة العرض WGS84",
    "Point_Lon": u"خط الطول WGS84",
    "Data_Start": u"بداية السلسلة الزمنية",
    "Data_End": u"نهاية السلسلة الزمنية",
    "Temporal": u"الدقة الزمنية",
    "Interp_Meth": u"خوارزمية الاستيفاء",
    "Cell_Size": u"حجم خلية الراستر",
    "Wind_Cell": u"حجم خلية الرياح",
    "Measurement_Unit": u"وحدة القياس",
    "Unit": u"وحدة القياس",
    "Status": u"حالة المعالجة",
    "Error_Msg": u"رسالة الخطأ",
}

def get_units_mapping(unit_sys=None, unit_temp=None, unit_precip=None, unit_press=None, unit_wind=None, unit_solar=None):
    if unit_temp and "Fahrenheit" in unit_temp:
        t_unit = u"°F"
    elif unit_temp and ("Kelvin" in unit_temp or unit_temp.strip() == "K"):
        t_unit = "K"
    else:
        t_unit = u"°C"

    p_unit = "in" if (unit_precip and "Inches" in unit_precip) else "mm"

    if unit_press and "mbar" in unit_press:
        pr_unit = "mbar"
    elif unit_press and "inHg" in unit_press:
        pr_unit = "inHg"
    elif unit_press and "kPa" in unit_press:
        pr_unit = "kPa"
    else:
        pr_unit = "hPa"

    if unit_wind and "km/h" in unit_wind:
        w_unit = "km/h"
    elif unit_wind and ("kt" in unit_wind or "Knots" in unit_wind):
        w_unit = "kt"
    elif unit_wind and "mph" in unit_wind:
        w_unit = "mph"
    else:
        w_unit = "m/s"

    if unit_solar and "MJ" in unit_solar:
        sol_unit = "MJ/m²/day"
    elif unit_solar and ("kWh" in unit_solar or "kW-hr" in unit_solar or "Kilowatt" in unit_solar):
        sol_unit = "kWh/m²/day"
    elif unit_solar and ("Wh" in unit_solar or "Watt" in unit_solar):
        sol_unit = "Wh/m²/day"
    elif unit_solar and ("cal" in unit_solar or "Langley" in unit_solar):
        sol_unit = "cal/cm²/day"
    else:
        sol_unit = "kWh/m²/day"

    return {
        "Temperature": t_unit,
        "Heat Index": t_unit,
        "Heat_Index": t_unit,
        "Wind Chill": t_unit,
        "Wind_Chill": t_unit,
        "Dew Point": t_unit,
        "Dew_Point": t_unit,
        "Precipitation": p_unit,
        "Water Deficit": p_unit,
        "Water_Deficit": p_unit,
        "Evapotranspiration": p_unit,
        "Sea Level Pressure": pr_unit,
        "Sea_Level_Pressure": pr_unit,
        "Surface Pressure": pr_unit,
        "Surface_Pressure": pr_unit,
        "Isobars": pr_unit,
        "Wind": w_unit,
        "Wind Speed": w_unit,
        "Wind_Speed": w_unit,
        "Wind Vector": w_unit,
        "Wind_Vector": w_unit,
        "Relative Humidity": "%",
        "Relative_Humidity": "%",
        "Cloud Cover": "%",
        "Cloud_Cover": "%",
        "Solar Radiation": sol_unit,
        "Solar_Radiation": sol_unit,
        "UV Index": "Index",
        "UV_Index": "Index",
        "De Martonne Aridity": "Index",
        "De_Martonne_Aridity": "Index",
        "UNEP Aridity": "Ratio",
        "UNEP_Aridity": "Ratio",
        "Dry Months": "Months",
        "Dry_Months": "Months",
        "Trends & Anomalies": u"%s/dec" % t_unit,
        "Trends_And_Anomalies": u"%s/dec" % t_unit,
        "Land Surface Temperature": u"%s" % t_unit,
        "Land_Surface_Temperature": u"%s" % t_unit,
        "Climate_Models": "Composite",
        "Drought & Aridity": "Composite",
    }


REQUIRED_COLUMNS = [
    "OBJECTID", "Source_ID", "Point_Lat", "Point_Lon", "Data_Start", "Data_End",
    "Temporal", "Interp_Meth", "Cell_Size", "Wind_Cell", "Measurement_Unit", "Status", "Error_Msg",
] + [r[0] for r in FIELD_DEFS]


OM_BASE = "https://archive-api.open-meteo.com/v1/archive"

OM_DAILY_BY_MODULE = {
    "Temperature": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min"],
    "Precipitation": ["precipitation_sum"],
    "Wind": ["wind_direction_10m_dominant"],
    "Solar Radiation": ["shortwave_radiation_sum"],
    "UV Index": ["uv_index_max"],
    "Heat Index": ["temperature_2m_mean", "temperature_2m_max"],
    "Wind Chill": ["temperature_2m_mean"],
    "De Martonne Aridity": ["temperature_2m_mean", "precipitation_sum"],
    "Evapotranspiration": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min"],
    "Hargreaves PET": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min"],
    "UNEP Aridity": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "Water Deficit": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "Dry Months": ["temperature_2m_mean", "precipitation_sum"],
    "Trends & Anomalies": ["temperature_2m_mean", "precipitation_sum"],
    "Land Surface Temperature": ["temperature_2m_mean"],
    "Climate_Models": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "Drought & Aridity": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
}
OM_HOURLY_BY_MODULE = {
    "Sea Level Pressure": ["pressure_msl"],
    "Surface Pressure": ["surface_pressure"],
    "Temperature": ["dew_point_2m"],
    "Wind": ["wind_speed_10m"],
    "Relative Humidity": ["relative_humidity_2m"],
    "Dew Point": ["dew_point_2m"],
    "Cloud Cover": ["cloud_cover"],
    "Heat Index": ["relative_humidity_2m"],
    "Wind Chill": ["wind_speed_10m"],
    "Land Surface Temperature": ["skin_temperature"],
    "Climate_Models": ["relative_humidity_2m", "dew_point_2m", "wind_speed_10m"],
}
# canonical monthly keys produced for each module (mirrors NASA parameter names)
OM_CANON = {
    "temperature_2m_mean": "T2M", "temperature_2m_max": "T2M_MAX",
    "temperature_2m_min": "T2M_MIN", "precipitation_sum": "PRECTOTCORR",
    "wind_speed_10m": "WS10M", "wind_direction_10m_dominant": "WD10M",
    "pressure_msl": "SLP", "surface_pressure": "PS",
    "relative_humidity_2m": "RH2M", "dew_point_2m": "T2MDEW",
    "shortwave_radiation_sum": "ALLSKY_SFC_SW_DWN",
    "uv_index_max": "ALLSKY_SFC_UV_INDEX", "cloud_cover": "CLOUD_AMT",
    "skin_temperature": "TS",
}
OM_SUM_VARS = ("precipitation_sum",)


def om_var_sets(modules):
    """Daily + hourly Open-Meteo variable lists for the selected modules."""
    daily, hourly = [], []
    for m in modules:
        for v in OM_DAILY_BY_MODULE.get(m, []):
            if v not in daily:
                daily.append(v)
        for v in OM_HOURLY_BY_MODULE.get(m, []):
            if v not in hourly:
                hourly.append(v)
    return daily, hourly


def om_model_slug(model_text):
    s = str(model_text or "").lower()
    if "land" in s:
        return "era5_land"
    elif "seamless" in s:
        return "era5_seamless"
    elif "era5" in s:
        return "era5"
    return "era5_land"


def om_url(lat, lon, y0, y1, daily_vars, hourly_vars, model="era5_land", start_date=None, end_date=None):
    if not start_date:
        start_date = "%d-01-01" % y0
    if not end_date:
        end_date = "%d-12-31" % y1
    q = ("latitude=%s&longitude=%s&start_date=%s&end_date=%s&timezone=UTC"
         % (repr(float(lat)), repr(float(lon)), str(start_date), str(end_date)))
    if daily_vars:
        q += "&daily=" + ",".join(daily_vars)
    if hourly_vars:
        q += "&hourly=" + ",".join(hourly_vars)
    if model:
        q += "&models=" + om_model_slug(model)
    return OM_BASE + "?" + q


def om_group_daily(dates, values, mode="mean"):
    """dates: [YYYY-MM-DD], values: [...] -> {(y,m): aggregated} skipping nulls."""
    by_month = {}
    for d, v in zip(dates or [], values or []):
        if v is None:
            continue
        try:
            f = float(v)
        except Exception:
            continue
        if f != f:  # NaN
            continue
        try:
            ym = (int(d[0:4]), int(d[5:7]))
        except Exception:
            continue
        by_month.setdefault(ym, []).append(f)
    out = {}
    for ym, vals in by_month.items():
        if not vals:
            continue
        out[ym] = sum(vals) if mode == "sum" else sum(vals) / len(vals)
    return out


def om_group_hourly(times, values):
    """times: [YYYY-MM-DDTHH:MM], values -> {(y,m): mean} skipping nulls."""
    by_month = {}
    for t, v in zip(times or [], values or []):
        if v is None:
            continue
        try:
            f = float(v)
        except Exception:
            continue
        if f != f:
            continue
        try:
            ym = (int(t[0:4]), int(t[5:7]))
        except Exception:
            continue
        by_month.setdefault(ym, []).append(f)
    out = {}
    for ym, vals in by_month.items():
        if vals:
            out[ym] = sum(vals) / len(vals)
    return out


def probe_server(provider, lat, lon, year, n_pts, timeout=30, model="era5_land",
                 start_date=None, end_date=None):
    """Fail-fast connectivity check: one minimal request before the full loop.

    Raises RuntimeError with a clear cause so the run aborts in seconds instead
    of downloading for an hour into empty outputs."""
    try:
        if provider.startswith("Open-Meteo") or "ERA5" in provider or "Hybrid" in provider or "Copernicus" in provider or "CDS" in provider:
            fetch_openmeteo_point(lat, lon, year, year, ["Temperature"],
                                  timeout=timeout, retries=1, model=model,
                                  start_date=start_date, end_date=end_date)
        else:
            fetch_nasa_point(lat, lon, year, year, ["T2M"], temporal="Monthly",
                             timeout=timeout, retries=1,
                             start_date=start_date, end_date=end_date)
    except Exception as ex:
        raise RuntimeError(
            "Server connectivity check failed (%s): %s. Check the internet "
            "connection, firewall/proxy settings, and that the service is online, "
            "then re-run for the %d points." % (provider, ex, n_pts))


def om_drop_vars_from_reason(reason, daily_vars, hourly_vars):
    """Remove variables named in an API error; returns (daily, hourly, dropped)."""
    r = str(reason or "")
    dropped = []
    daily = [v for v in daily_vars if v not in r or not _mark_dropped(v, dropped)]
    hourly = [v for v in hourly_vars if v not in r or not _mark_dropped(v, dropped)]
    return daily, hourly, dropped


def _mark_dropped(v, dropped):
    dropped.append(v)
    return True


def om_parse_response(data, daily_vars, hourly_vars):
    """Map an Open-Meteo response to canonical monthly dicts + complete daily series."""
    monthly, daily_raw = {}, {}
    daily = data.get("daily", {}) or {}
    hourly = data.get("hourly", {}) or {}
    dates = daily.get("time", []) or []

    # 1. Process daily variables
    for v in daily_vars:
        canon = OM_CANON.get(v, v)
        mode = "sum" if v in OM_SUM_VARS else "mean"
        vals = daily.get(v, []) or []
        monthly[canon] = om_group_daily(dates, vals, mode)
        # Parse complete daily time series for this variable
        draw = {}
        for d, val in zip(dates, vals):
            if val is None:
                continue
            try:
                f = float(val)
            except Exception:
                continue
            if f == f:  # not NaN
                try:
                    draw[(int(d[0:4]), int(d[5:7]), int(d[8:10]))] = f
                except Exception:
                    pass
        if draw:
            daily_raw[canon] = draw
            if canon != v:
                daily_raw[v] = draw

    # 2. Process hourly variables and aggregate to daily when missing
    htimes = hourly.get("time", []) or []
    for v in hourly_vars:
        canon = OM_CANON.get(v, v)
        hvals = hourly.get(v, []) or []
        monthly[canon] = om_group_hourly(htimes, hvals)
        if canon not in daily_raw and htimes and hvals:
            day_accum = {}
            for t_str, val in zip(htimes, hvals):
                if val is None:
                    continue
                try:
                    fv = float(val)
                except Exception:
                    continue
                if fv == fv:
                    try:
                        ymd = (int(t_str[0:4]), int(t_str[5:7]), int(t_str[8:10]))
                        day_accum.setdefault(ymd, []).append(fv)
                    except Exception:
                        pass
            if day_accum:
                mode = "sum" if v in OM_SUM_VARS else "mean"
                draw = {}
                for ymd, vlist in day_accum.items():
                    if vlist:
                        draw[ymd] = sum(vlist) if mode == "sum" else (sum(vlist) / float(len(vlist)))
                if draw:
                    daily_raw[canon] = draw
                    if canon != v:
                        daily_raw[v] = draw

    return monthly, daily_raw



def fetch_openmeteo_point(lat, lon, y0, y1, modules, timeout=60, retries=3,
                          daily_vars=None, hourly_vars=None, model="era5_land",
                          start_date=None, end_date=None):
    """Returns (monthly, daily_raw, dropped_vars). Raises RuntimeError after retries."""
    if daily_vars is None or hourly_vars is None:
        daily_vars, hourly_vars = om_var_sets(modules)
    url = om_url(lat, lon, y0, y1, daily_vars, hourly_vars, model=model,
                 start_date=start_date, end_date=end_date)
    last_err = None
    for attempt in range(retries):
        try:
            data = _http_get_json(url, timeout)
            if isinstance(data, dict) and data.get("error"):
                raise RuntimeError("Open-Meteo: %s" % data.get("reason", data))
            _m, _d = om_parse_response(data, daily_vars, hourly_vars)
            return _m, _d, []
        except Exception as ex:
            last_err = ex
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError("Open-Meteo request failed: %s" % last_err)


def om_probe_vars(modules, timeout=30, model="era5_land", start_date=None, end_date=None):
    """One tiny request to verify variable availability; drops rejected vars.

    Returns (daily_vars, hourly_vars, dropped, note). Never raises."""
    daily_vars, hourly_vars = om_var_sets(modules)
    if not daily_vars and not hourly_vars:
        return daily_vars, hourly_vars, [], ""
    url = om_url(30.0, 31.0, 2020, 2020, daily_vars, hourly_vars, model=model,
                 start_date=(start_date if start_date else "2020-01-01"),
                 end_date=(end_date if end_date else "2020-01-10"))
    try:
        data = _http_get_json(url, timeout)
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(str(data.get("reason", data)))
        return daily_vars, hourly_vars, [], ""
    except Exception as ex:
        daily2, hourly2, dropped = om_drop_vars_from_reason(ex, daily_vars, hourly_vars)
        # last resort: core daily set only
        if not daily2 and not hourly2:
            daily2 = [v for v in daily_vars
                      if v in ("temperature_2m_mean", "temperature_2m_max",
                               "temperature_2m_min", "precipitation_sum",
                               "shortwave_radiation_sum", "wind_direction_10m_dominant")]
            dropped = [v for v in daily_vars + hourly_vars if v not in daily2]
        note = "Open-Meteo rejected variables %s (%s); affected fields will be NoData." % (
            dropped or ["?"], ex)
        return daily2, hourly2, dropped, note


def convert_fields_to_user_units(fields, unit_temp=None, unit_precip=None, unit_press=None, unit_wind=None, unit_solar=None):
    """Converts computed numeric indicator fields from standard baseline units
    (°C, mm, hPa, m/s, kWh/m2/day) to the user's selected units.
    Operates on a dictionary of {field_name: value} and returns a converted copy."""
    if not fields:
        return {}
    out = dict(fields)

    is_f = bool(unit_temp and "Fahrenheit" in unit_temp)
    is_k = bool(unit_temp and ("Kelvin" in unit_temp or unit_temp.strip() == "K"))

    is_in = bool(unit_precip and "Inches" in unit_precip)

    is_inhg = bool(unit_press and "inHg" in unit_press)
    is_kpa = bool(unit_press and "kPa" in unit_press)

    is_kmh = bool(unit_wind and "km/h" in unit_wind)
    is_kt = bool(unit_wind and ("kt" in unit_wind or "Knots" in unit_wind))
    is_mph = bool(unit_wind and "mph" in unit_wind)

    is_kwh = bool(unit_solar and ("kWh" in unit_solar or "kW-hr" in unit_solar or "Kilowatt" in unit_solar))
    is_mj = bool(unit_solar and "MJ" in unit_solar)
    is_wh = bool(unit_solar and ("Wh" in unit_solar or "Watt" in unit_solar) and not is_kwh)
    is_cal = bool(unit_solar and ("cal" in unit_solar or "Langley" in unit_solar))

    temp_prefixes = ("T_", "Td_", "HI_", "WC_", "WBGT_", "LST_")

    for k, v in list(out.items()):
        if v is None:
            continue
        try:
            val = float(v)
        except (ValueError, TypeError):
            continue

        if any(k.startswith(pfx) for pfx in temp_prefixes):
            is_delta = any(x in k for x in ("Range", "Trend", "Anom", "Diff"))
            if is_f:
                out[k] = round(val * 1.8, 2) if is_delta else round(val * 1.8 + 32.0, 2)
            elif is_k:
                out[k] = round(val, 2) if is_delta else round(val + 273.15, 2)

        elif k.startswith("R_") or k.startswith("ET_") or k.startswith("PET_") or k.startswith("Water_Deficit"):
            if "Pct" not in k and "Count" not in k and "Days" not in k:
                if is_in:
                    out[k] = round(val / 25.4, 2)

        elif k.startswith("PS_") or k.startswith("PSL_"):
            if is_inhg:
                out[k] = round(val * 0.029530, 2)
            elif is_kpa:
                out[k] = round(val / 10.0, 2)

        elif k.startswith("W_Spd_") or k == "W_Spd":
            if is_kmh:
                out[k] = round(val * 3.6, 2)
            elif is_kt:
                out[k] = round(val * 1.943844, 2)
            elif is_mph:
                out[k] = round(val * 2.236936, 2)

        elif k.startswith("Sol_"):
            if is_mj:
                out[k] = round(val * 3.6, 2)
            elif is_wh:
                out[k] = round(val * 1000.0, 2)
            elif is_cal:
                out[k] = round(val * 85.9845, 2)

    return out


def compute_point_fields(monthly, years, modules, temporal, daily_raw=None,
                         precip_totals=False, gap_method="climatological", lat=0.0,
                         uv_source=None, monthly_ranges=False,
                         unit_temp=None, unit_precip=None, unit_press=None,
                         unit_wind=None, unit_solar=None):
    """Core per-point computation. monthly: {param: {(y,m): v}}.
    precip_totals=True when monthly PRECTOTCORR values are already totals
    (NASA daily mode, Open-Meteo); False only for NASA monthly rates (mm/day).
    gap_method: 'climatological' | 'linear' | 'none' for interior missing
    months of mean-type variables (never precipitation sums, never wind
    direction).
    uv_source: 'nasa' | 'om' | None. None infers from precip_totals
    (OM=True -> no conversion, NASA=False -> convert 24h-mean to noon-max).
    NASA ALLSKY_SFC_UV_INDEX daily/monthly is a 24h mean incl. night zeros,
    converted per (y,m) to WHO noon-max via daylength; OM uv_index_max is
    already a daily max and is averaged directly.
    monthly_ranges: when True, also emit per-calendar-month interannual ranges
    (<Prefix>_<Month>_Range, e.g. ET_December_Range) for the mean-type modules.
    Opt-in only (independent toggle, default OFF)."""
    _FILLABLE = ("T2M", "T2M_MAX", "T2M_MIN", "RH2M", "T2MDEW", "ALLSKY_SFC_SW_DWN",
                  "ALLSKY_SFC_UV_INDEX", "CLOUD_AMT", "SLP", "PS", "WS10M", "TS")
    if gap_method != "none":
        monthly = dict((k, fill_interior_gaps(v, gap_method) if k in _FILLABLE else v)
                       for k, v in monthly.items())
    res = {}
    if "Temperature" in modules:
        res.update(compute_temperature_fields(
            monthly.get("T2M", {}), monthly.get("T2M_MAX", {}),
            monthly.get("T2M_MIN", {}), monthly.get("RH2M", {}),
            monthly.get("T2MDEW", {})))
    if "Precipitation" in modules:
        raw = monthly.get("PRECTOTCORR", {})
        if temporal == "Monthly" and not precip_totals:
            totals = {}
            for ym, v in raw.items():
                totals[ym] = monthly_precip_total_from_rate(v, ym[0], ym[1])
        else:
            totals = dict(raw)  # already summed per month
        agg = seasonal_totals_from_monthly_totals(totals, years)
        clim_m = climat_monthly_means(totals)
        clim_vals = [v for v in clim_m.values() if v is not None]
        res["R_Annual_Mean"] = agg["Annual_Mean"]
        res["R_Annual_Range"] = (max(clim_vals) - min(clim_vals)) if len(clim_vals) >= 2 else None
        res["R_Winter_Mean"] = agg["Winter"]
        res["R_Spring_Mean"] = agg["Spring"]
        res["R_Summer_Mean"] = agg["Summer"]
        res["R_Autumn_Mean"] = agg["Autumn"]
        _months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        for m_idx, m_name in enumerate(_months_en, 1):
            res["R_%s_Mean" % m_name] = round(clim_m.get(m_idx), 2) if clim_m.get(m_idx) is not None else 0.0
    has_drought_mod = any(m in modules for m in [
        "De Martonne Aridity", "Evapotranspiration", "Hargreaves PET", "UNEP Aridity", "Water Deficit", "Dry Months",
        "Drought & Aridity", "Climate_Models"
    ])
    if has_drought_mod:
        raw_p = monthly.get("PRECTOTCORR", {})
        if temporal == "Monthly" and not precip_totals:
            totals_p = {}
            for ym, v in raw_p.items():
                totals_p[ym] = monthly_precip_total_from_rate(v, ym[0], ym[1])
        else:
            totals_p = dict(raw_p)
        res.update(compute_drought_fields(
            monthly.get("T2M", {}), monthly.get("T2M_MAX", {}),
            monthly.get("T2M_MIN", {}), totals_p, lat=lat))

    if "Heat Index" in modules or "Climate_Models" in modules:
        c_t = climat_monthly_means(monthly.get("T2M", {}))
        c_rh = climat_monthly_means(monthly.get("RH2M", {}))
        res.update(compute_thermal_stress_fields(c_t, c_rh))

    if "Wind Chill" in modules or "Climate_Models" in modules:
        c_t = climat_monthly_means(monthly.get("T2M", {}))
        c_ws = climat_monthly_means(monthly.get("WS10M", {}))
        res.update(compute_winter_chill_fields(c_t, c_ws))

    if "Trends & Anomalies" in modules or "Climate_Models" in modules:
        raw_p = monthly.get("PRECTOTCORR", {})
        if temporal == "Monthly" and not precip_totals:
            totals_p = {}
            for ym, v in raw_p.items():
                totals_p[ym] = monthly_precip_total_from_rate(v, ym[0], ym[1])
        else:
            totals_p = dict(raw_p)
        res.update(compute_trend_anomaly_fields(
            monthly.get("T2M", {}), totals_p))
    _months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    if "Sea Level Pressure" in modules:
        conv = dict((ym, pressure_kpa_to_mbar(v)) for ym, v in monthly.get("SLP", {}).items())
        s = seasonal_means_from_monthly(conv)
        c_slp = climat_monthly_means(conv)
        res.update({"PSL_Annual_Mean": s["Annual"], "PSL_Winter_Mean": s["Winter"],
                    "PSL_Spring_Mean": s["Spring"], "PSL_Summer_Mean": s["Summer"],
                    "PSL_Autumn_Mean": s["Autumn"],
                    "PSL_Annual_Range": monthly_range(conv)})
        for m_idx, m_name in enumerate(_months_en, 1):
            res["PSL_%s_Mean" % m_name] = round(c_slp.get(m_idx), 2) if c_slp.get(m_idx) is not None else None
    if "Surface Pressure" in modules:
        conv = dict((ym, pressure_kpa_to_mbar(v)) for ym, v in monthly.get("PS", {}).items())
        s = seasonal_means_from_monthly(conv)
        c_ps = climat_monthly_means(conv)
        res.update({"PS_Annual_Mean": s["Annual"], "PS_Winter_Mean": s["Winter"],
                    "PS_Spring_Mean": s["Spring"], "PS_Summer_Mean": s["Summer"],
                    "PS_Autumn_Mean": s["Autumn"],
                    "PS_Annual_Range": monthly_range(conv)})
        for m_idx, m_name in enumerate(_months_en, 1):
            res["PS_%s_Mean" % m_name] = round(c_ps.get(m_idx), 2) if c_ps.get(m_idx) is not None else None
    if "Wind" in modules:
        res.update(compute_wind_fields(monthly.get("WS10M", {}), monthly.get("WD10M", {})))
    if "Relative Humidity" in modules:
        _rh_monthly = monthly.get("RH2M", {})
        s = seasonal_means_from_monthly(_rh_monthly)
        c_rh = climat_monthly_means(_rh_monthly)
        res.update({"RH_Annual_Mean": s["Annual"], "RH_Winter_Mean": s["Winter"],
                    "RH_Spring_Mean": s["Spring"], "RH_Summer_Mean": s["Summer"],
                    "RH_Autumn_Mean": s["Autumn"],
                    "RH_Annual_Range": monthly_range(_rh_monthly)})
        for m_idx, m_name in enumerate(_months_en, 1):
            res["RH_%s_Mean" % m_name] = round(c_rh.get(m_idx), 2) if c_rh.get(m_idx) is not None else None
    if "Dew Point" in modules:
        _td_monthly = monthly.get("T2MDEW", {})
        s_td = seasonal_means_from_monthly(_td_monthly)
        c_td = climat_monthly_means(_td_monthly)
        res.update({"Td_Annual_Mean": s_td["Annual"], "Td_Winter_Mean": s_td["Winter"],
                    "Td_Spring_Mean": s_td["Spring"], "Td_Summer_Mean": s_td["Summer"],
                    "Td_Autumn_Mean": s_td["Autumn"],
                    "Td_Annual_Range": monthly_range(_td_monthly)})
        for m_idx, m_name in enumerate(_months_en, 1):
            res["Td_%s_Mean" % m_name] = round(c_td.get(m_idx), 2) if c_td.get(m_idx) is not None else None
    if "Solar Radiation" in modules:
        res.update(compute_solar_fields(monthly.get("ALLSKY_SFC_SW_DWN", {}), years))
    if "UV Index" in modules:
        _uv_monthly = monthly.get("ALLSKY_SFC_UV_INDEX", {})
        # NASA = 24h mean -> WHO noon-max per (y,m); OM = already daily max.
        _uv_is_nasa = (uv_source == "nasa") if uv_source in ("nasa", "om") else (not precip_totals)
        # Backward compat: scripts calling without uv_source on raw NASA monthly
        # JSON default to NASA conversion (precip_totals=False). OM callers pass
        # precip_totals=True so no conversion is applied.
        if _uv_is_nasa:
            try:
                _lat_f = float(lat) if lat is not None else 0.0
            except Exception:
                _lat_f = 0.0
            _uv_noon = {}
            for _ym, _v in _uv_monthly.items():
                try:
                    _m = _ym[1]
                except Exception:
                    continue
                _c = uv_mean24_to_noonmax(_v, _lat_f, _m)
                if _c is not None:
                    _uv_noon[_ym] = _c
            _uv_work = _uv_noon if _uv_noon else _uv_monthly
        else:
            _uv_work = _uv_monthly
        s = seasonal_means_from_monthly(_uv_work)
        c_uv = climat_monthly_means(_uv_work)
        res.update({"UV_Annual_Mean": s["Annual"], "UV_Winter_Mean": s["Winter"],
                    "UV_Spring_Mean": s["Spring"], "UV_Summer_Mean": s["Summer"],
                    "UV_Autumn_Mean": s["Autumn"],
                    "UV_Annual_Range": monthly_range(_uv_work)})
        for m_idx, m_name in enumerate(_months_en, 1):
            res["UV_%s_Mean" % m_name] = round(c_uv.get(m_idx), 2) if c_uv.get(m_idx) is not None else None
    if "Cloud Cover" in modules:
        _cld_monthly = monthly.get("CLOUD_AMT", {})
        s = seasonal_means_from_monthly(_cld_monthly)
        c_cld = climat_monthly_means(_cld_monthly)
        res.update({"Cld_Annual_Mean": s["Annual"], "Cld_Winter_Mean": s["Winter"],
                    "Cld_Spring_Mean": s["Spring"], "Cld_Summer_Mean": s["Summer"],
                    "Cld_Autumn_Mean": s["Autumn"],
                    "Cld_Annual_Range": monthly_range(_cld_monthly)})
        for m_idx, m_name in enumerate(_months_en, 1):
            res["Cld_%s_Mean" % m_name] = round(c_cld.get(m_idx), 2) if c_cld.get(m_idx) is not None else None
    if "Land Surface Temperature" in modules:
        _ts_monthly = monthly.get("TS", {})
        s_ts = seasonal_means_from_monthly(_ts_monthly)
        c_ts = climat_monthly_means(_ts_monthly)
        _t_ann = res.get("T_Annual_Mean")
        _t_win = res.get("T_Winter_Mean")
        _t_spr = res.get("T_Spring_Mean")
        _t_sum = res.get("T_Summer_Mean")
        _t_aut = res.get("T_Autumn_Mean")
        if any(v is None for v in (_t_ann, _t_win, _t_spr, _t_sum, _t_aut)):
            s_t = seasonal_means_from_monthly(monthly.get("T2M", {}))
            if _t_ann is None:
                _t_ann = s_t.get("Annual")
            if _t_win is None:
                _t_win = s_t.get("Winter")
            if _t_spr is None:
                _t_spr = s_t.get("Spring")
            if _t_sum is None:
                _t_sum = s_t.get("Summer")
            if _t_aut is None:
                _t_aut = s_t.get("Autumn")
        _diff_ann = (round(s_ts["Annual"] - _t_ann, 2)
                     if (s_ts["Annual"] is not None and _t_ann is not None) else None)
        _diff_win = (round(s_ts["Winter"] - _t_win, 2)
                     if (s_ts["Winter"] is not None and _t_win is not None) else None)
        _diff_spr = (round(s_ts["Spring"] - _t_spr, 2)
                     if (s_ts["Spring"] is not None and _t_spr is not None) else None)
        _diff_sum = (round(s_ts["Summer"] - _t_sum, 2)
                     if (s_ts["Summer"] is not None and _t_sum is not None) else None)
        _diff_aut = (round(s_ts["Autumn"] - _t_aut, 2)
                     if (s_ts["Autumn"] is not None and _t_aut is not None) else None)
        res.update({"LST_Annual_Mean": s_ts["Annual"],
                    "LST_Winter_Mean": s_ts["Winter"], "LST_Spring_Mean": s_ts["Spring"],
                    "LST_Summer_Mean": s_ts["Summer"], "LST_Autumn_Mean": s_ts["Autumn"],
                    "LST_Annual_Range": monthly_range(_ts_monthly),
                    "LST_minus_T_Annual": _diff_ann,
                    "LST_minus_T_Winter": _diff_win,
                    "LST_minus_T_Spring": _diff_spr,
                    "LST_minus_T_Summer": _diff_sum,
                    "LST_minus_T_Autumn": _diff_aut})
        for m_idx, m_name in enumerate(_months_en, 1):
            _lst_m = round(c_ts.get(m_idx), 2) if c_ts.get(m_idx) is not None else None
            res["LST_%s_Mean" % m_name] = _lst_m
            _t_m = res.get("T_%s_Mean" % m_name)
            if _t_m is None and "T2M" in monthly:
                c_t = climat_monthly_means(monthly.get("T2M", {}))
                _t_m = round(c_t.get(m_idx), 2) if c_t.get(m_idx) is not None else None
            _diff_m = round(_lst_m - _t_m, 2) if (_lst_m is not None and _t_m is not None) else None
            res["LST_minus_T_%s" % m_name] = _diff_m
    if monthly_ranges:
        # Opt-in interannual monthly ranges (<Prefix>_<Month>_Range), computed
        # on the same transformed series as the means (pressure in mbar/hPa,
        # solar in kWh, UV as WHO noon-max, precipitation as totals, ET via
        # Hargreaves). Wind direction excluded (circular).
        _m_en = ["January", "February", "March", "April", "May", "June", "July",
                 "August", "September", "October", "November", "December"]

        def _put(pfx, rng):
            for _mi, _mn in enumerate(_m_en, 1):
                _v = rng.get(_mi)
                res["%s_%s_Range" % (pfx, _mn)] = round(_v, 2) if _v is not None else None

        if "Temperature" in modules:
            _put("T", monthly_interannual_ranges(monthly.get("T2M", {})))
        if "Precipitation" in modules:
            _praw = monthly.get("PRECTOTCORR", {})
            if temporal == "Monthly" and not precip_totals:
                _ptot = {}
                for _ym, _v in _praw.items():
                    _ptot[_ym] = monthly_precip_total_from_rate(_v, _ym[0], _ym[1])
            else:
                _ptot = dict(_praw)
            _put("R", monthly_interannual_ranges(_ptot))
        if "Sea Level Pressure" in modules:
            _put("PSL", monthly_interannual_ranges(dict(
                (ym, pressure_kpa_to_mbar(v)) for ym, v in monthly.get("SLP", {}).items())))
        if "Surface Pressure" in modules:
            _put("PS", monthly_interannual_ranges(dict(
                (ym, pressure_kpa_to_mbar(v)) for ym, v in monthly.get("PS", {}).items())))
        if "Wind" in modules:
            _put("W_Spd", monthly_interannual_ranges(monthly.get("WS10M", {})))
        if "Relative Humidity" in modules:
            _put("RH", monthly_interannual_ranges(monthly.get("RH2M", {})))
        if "Dew Point" in modules:
            _put("Td", monthly_interannual_ranges(monthly.get("T2MDEW", {})))
        if "Solar Radiation" in modules:
            _put("Sol", monthly_interannual_ranges(dict(
                (ym, v) for ym, v in
                ((k, solar_mj_to_kwh(x)) for k, x in monthly.get("ALLSKY_SFC_SW_DWN", {}).items())
                if v is not None)))
        if "UV Index" in modules:
            _urm = monthly.get("ALLSKY_SFC_UV_INDEX", {})
            _uis_nasa = (uv_source == "nasa") if uv_source in ("nasa", "om") else (not precip_totals)
            try:
                _ulat = float(lat) if lat is not None else 0.0
            except Exception:
                _ulat = 0.0
            if _uis_nasa:
                _unoon = {}
                for _ym, _v in _urm.items():
                    try:
                        _mm = _ym[1]
                    except Exception:
                        continue
                    _cc = uv_mean24_to_noonmax(_v, _ulat, _mm)
                    if _cc is not None:
                        _unoon[_ym] = _cc
                _uwork = _unoon if _unoon else _urm
            else:
                _uwork = _urm
            _put("UV", monthly_interannual_ranges(_uwork))
        if "Cloud Cover" in modules:
            _put("Cld", monthly_interannual_ranges(monthly.get("CLOUD_AMT", {})))
        if "Evapotranspiration" in modules:
            try:
                _elat = float(lat) if lat is not None else 0.0
            except Exception:
                _elat = 0.0
            _etm = {}
            for _ym, _t in monthly.get("T2M", {}).items():
                try:
                    _yy, _mm = int(_ym[0]), int(_ym[1])
                except Exception:
                    continue
                _tx = monthly.get("T2M_MAX", {}).get(_ym)
                _tn = monthly.get("T2M_MIN", {}).get(_ym)
                if is_missing(_t) or is_missing(_tx) or is_missing(_tn):
                    continue
                try:
                    _ra = extraterrestrial_radiation_ra(_elat, _mm)
                    _td = max(0.0, float(_tx) - float(_tn))
                    _pet = 0.0023 * _ra * (float(_t) + 17.8) * math.sqrt(_td)
                    _etm[_ym] = max(0.0, _pet * month_days(_yy, _mm))
                except Exception:
                    continue
            _put("ET", monthly_interannual_ranges(_etm))
    if any([unit_temp, unit_precip, unit_press, unit_wind, unit_solar]):
        res = convert_fields_to_user_units(res, unit_temp, unit_precip, unit_press, unit_wind, unit_solar)
    return res


# ---------------------------------------------------------------------------
# Toolbox definition (ArcMap 10.x Python toolbox API)
# ---------------------------------------------------------------------------

class Toolbox(object):
    """POWER Climate Atlas Generator (ArcMap 10.x & ArcGIS Pro compatible).

    Professional climate-atlas toolbox: downloads gridded climate data for user
    point features (NASA POWER API or Open-Meteo ERA5 reanalysis), computes
    annual/seasonal indicators with correct units, and packages everything as a
    documented atlas (points, clipped rasters, layer files, dictionaries, log).
    """

    def __init__(self):
        self.label = "MIRSAD - Climate Atlas & Meteorological Database Generator"
        self.alias = "mirsadAtlas"
        self.tools = [PowerClimateAtlasGenerator]
        if RasterDataClimateAtlasGenerator:
            self.tools.append(RasterDataClimateAtlasGenerator)


class PowerClimateAtlasGenerator(object):
    """MIRSAD: Spatial Climate Atlas Generator — builds a documented climate atlas package.

    WHAT IT DOES (3 stages, sequential and memory-safe on 32-bit ArcMap):
      1. FETCH: queries the selected Climate Data Source for every input point
         (WGS 84 coordinates extracted internally) with retries and an in-run
         cache; failed points are logged, never aborting the run.
      2. COMPUTE: annual/seasonal indicators per module with correct physics:
         temperature means and annual range (max-min monthly mean), precipitation
         accumulated totals (rate x days-in-month for NASA monthly), pressure
         converted to mbar/hPa, wind direction by circular (vector) mean, solar
         MJ/m2/day converted to kWh (mean vs annual total distinguished), UV and
         cloud means. Missing sentinels (-999) are excluded everywhere.
       3. BUILD: per-element point layers (GDB + shapefile + CSV each), interpolated and
          study-area-clipped raw float rasters (GeoTIFF, LZW, directly inside each
          element folder), thinned wind arrow layers, optional PSL isobars, bilingual
          (Arabic/English) data dictionaries and a full processing log with QA.

    DATA SOURCES: 'NASA POWER API' (gridded POWER climatology, ~0.5 deg native),
    'Open-Meteo Historical API (ERA5 Reanalysis)' (ERA5-Land, ~9 km native), or
    'Hybrid (Ground Truth + Satellite Gap-filling)'.

    OUTPUT LAYOUT (fixed, per-module folders 01..18 plus 00_Tables_And_Reports,
    Export_SHP and Project_Data.gdb): see the Processing_Log.txt written
    next to every run for the exact file list, warnings and QA results.
    """

    def __init__(self):
        self.label = "MIRSAD: Spatial Climate Atlas Generator"
        self.category = ""
        self.description = (
            "MIRSAD Platform: Fetch multi-source climate data (NASA POWER, Open-Meteo ERA5, "
            "or Hybrid) for point features, compute annual/seasonal indicators with correct units, "
            "and build an organized atlas package: per-element point layers (GDB/SHP/CSV each), "
            "interpolated clipped rasters (GeoTIFF), wind vector layers, optional PSL isobars, "
            "bilingual data dictionaries and a processing log.")
        self.canRunInBackground = True
        self._last_subs = []

    # ---------------- parameters ----------------
    def getParameterInfo(self):
        p_op_mode = arcpy.Parameter(
            displayName="Operation Mode",
            name="Operation_Mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p_op_mode.filter.type = "ValueList"
        p_op_mode.filter.list = [
            "Download & Generate Atlas (Full Pipeline) [Default]",
            "Interpolate & Map Existing Data (Offline Mode - No Internet)"
        ]
        p_op_mode.value = "Download & Generate Atlas (Full Pipeline) [Default]"
        p_op_mode.description = (
            "REQUIRED. Choose operation mode:\n"
            "'Download & Generate Atlas (Full Pipeline)': Online mode. Queries climate data for input points, "
            "computes indicators, builds feature classes, and interpolates rasters.\n"
            "'Interpolate & Map Existing Data (Offline Mode)': Offline mode. No internet queries. Takes a precalculated "
            "point layer already containing climate fields and directly performs spatial interpolation, masking, "
            "and atlas map generation."
        )

        p_wf_mode = arcpy.Parameter(
            displayName="Execution Workflow Mode",
            name="Execution_Workflow_Mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p_wf_mode.filter.type = "ValueList"
        p_wf_mode.filter.list = [
            "Batch Mode: Download All Then Process [Recommended]",
            "Sequential Mode: Element by Element"
        ]
        p_wf_mode.value = "Batch Mode: Download All Then Process [Recommended]"
        p_wf_mode.description = (
            "DOWNLOAD MODE ONLY. Choose workflow execution architecture:\n"
            "'Batch Mode: Download All Then Process' (recommended): Queries and saves data for all "
            "requested climate modules and submodels into the Geodatabase first, ensuring total data "
            "safety against network interruptions, then interpolates all surfaces in a second pass.\n"
            "'Sequential Mode: Element by Element': Queries, computes, and interpolates surfaces for "
            "each climate module one by one, providing immediate visual progress in the map layout."
        )

        p0 = arcpy.Parameter(
            displayName="Input Point Features",
            name="Input_Point_Features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        p0.filter.list = ["Point"]
        p0.description = ("REQUIRED for Download mode. Point layer (shapefile or geodatabase feature class). "
                          "Each point is queried against the data source using its WGS 84 "
                          "(EPSG:4326) longitude/latitude.")

        p_precalc = arcpy.Parameter(
            displayName="Precalculated Point Layer(s) (Offline Mode)",
            name="Precalculated_Point_Layers",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input")
        p_precalc.multiValue = True
        p_precalc.filter.list = ["Point", "Multipoint"]
        p_precalc.description = (
            "REQUIRED for Offline mode. One or more existing point layers (from GDB or Shapefile) containing "
            "pre-calculated climate attributes. The tool automatically merges them by coordinates/Source_ID."
        )

        p1 = arcpy.Parameter(
            displayName="Study Area Mask (optional polygon)",
            name="Study_Area_Mask",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Input")
        p1.filter.list = ["Polygon"]
        p1.description = ("OPTIONAL but recommended. Polygon used to set processing extent/mask, "
                          "clip final rasters, and generate wind vectors/isobars.")

        p_study_name = arcpy.Parameter(
            displayName="Study Area Name (Optional)",
            name="Study_Area_Name",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_study_name.value = None
        p_study_name.description = ("OPTIONAL. Name of the study area (e.g. 'Egypt', 'Sinai', 'Aswan', 'Nile Basin'). "
                                    "Used to title the atlas, name the boundary layer archived in GDB, and generate the Classification Workbook.")


        p12 = arcpy.Parameter(
            displayName="Output Folder Workspace",
            name="Output_Workspace",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        p12.description = ("REQUIRED. Output folder workspace. A File Geodatabase "
                           "'Climate_Database.gdb' is created inside automatically. "
                           "Per-element point layers (Temperature, Precipitation, etc.) "
                           "are stored in the GDB. Existing outputs are overwritten.")

        p2 = arcpy.Parameter(
            displayName="Output Spatial Reference",
            name="Output_Spatial_Reference",
            datatype="GPSpatialReference",
            parameterType="Optional",
            direction="Input")
        p2.description = ("OPTIONAL. Target coordinate system for all outputs. "
                          "DEFAULT: same as input points.")

        # ═══ Measurement Units & Standards ═══
        p_unit_sys = arcpy.Parameter(
            displayName="Measurement Units System",
            name="Measurement_Units_System",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_unit_sys.filter.type = "ValueList"
        p_unit_sys.filter.list = [
            "Metric (Celsius °C, mm, hPa, m/s, kWh/m2/day) [Default]",
            "Imperial (Fahrenheit °F, Inches in, inHg, mph, MJ/m2/day)",
            "Custom Units"
        ]
        p_unit_sys.value = "Metric (Celsius °C, mm, hPa, m/s, kWh/m2/day) [Default]"
        p_unit_sys.category = "Measurement Units & Standards"
        p_unit_sys.description = (
            "Select the measurement units system for atlas outputs.\n"
            "• Metric (Default): Celsius (°C), Millimeters (mm), Hectopascals (hPa), Meters/second (m/s), kWh/m2/day conforming to WMO and Egyptian standards.\n"
            "• Imperial: Fahrenheit (°F), Inches (in), Inches of Mercury (inHg), Miles/hour (mph), MJ/m2/day.\n"
            "• Custom Units: Manually customize units for each climate variable below.\n"
        )

        p_unit_temp = arcpy.Parameter(
            displayName="Temperature Unit",
            name="Temperature_Unit",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_unit_temp.filter.type = "ValueList"
        p_unit_temp.filter.list = ["Celsius (°C) [Default]", "Fahrenheit (°F)", "Kelvin (K)"]
        p_unit_temp.value = "Celsius (°C) [Default]"
        p_unit_temp.category = "Measurement Units & Standards"
        p_unit_temp.description = (
            "Measurement unit for temperature variables: Celsius (°C, default), Fahrenheit (°F), or Kelvin (K)."
        )

        p_unit_precip = arcpy.Parameter(
            displayName="Precipitation Unit",
            name="Precipitation_Unit",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_unit_precip.filter.type = "ValueList"
        p_unit_precip.filter.list = ["Millimeters (mm) [Default]", "Inches (in)"]
        p_unit_precip.value = "Millimeters (mm) [Default]"
        p_unit_precip.category = "Measurement Units & Standards"
        p_unit_precip.description = (
            "Measurement unit for precipitation and rainfall: Millimeters (mm, default) or Inches (in)."
        )

        p_unit_press = arcpy.Parameter(
            displayName="Pressure Unit",
            name="Pressure_Unit",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_unit_press.filter.type = "ValueList"
        p_unit_press.filter.list = [
            "Hectopascals (hPa) [Default]",
            "Millibars (mbar)",
            "Inches of Mercury (inHg)",
            "Kilopascals (kPa)"
        ]
        p_unit_press.value = "Hectopascals (hPa) [Default]"
        p_unit_press.category = "Measurement Units & Standards"
        p_unit_press.description = (
            "Measurement unit for atmospheric and sea level pressure: Hectopascals (hPa, default), Millibars (mbar), Inches of Mercury (inHg), or Kilopascals (kPa)."
        )

        p_unit_wind = arcpy.Parameter(
            displayName="Wind Speed Unit",
            name="Wind_Speed_Unit",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_unit_wind.filter.type = "ValueList"
        p_unit_wind.filter.list = ["Meters per second (m/s) [Default]", "Kilometers per hour (km/h)", "Knots (kt)", "Miles per hour (mph)"]
        p_unit_wind.value = "Meters per second (m/s) [Default]"
        p_unit_wind.category = "Measurement Units & Standards"
        p_unit_wind.description = (
            "Measurement unit for surface wind speed: Meters/second (m/s, default), km/h, kt, or mph."
        )

        p_unit_solar = arcpy.Parameter(
            displayName="Solar Radiation Unit",
            name="Solar_Radiation_Unit",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_unit_solar.filter.type = "ValueList"
        p_unit_solar.filter.list = [
            "Kilowatt-hours per square meter per day (kWh/m2/day) [Default]",
            "Megajoules per square meter per day (MJ/m2/day)",
            "Watt-hours per square meter per day (Wh/m2/day)",
            "Calories per square centimeter per day (cal/cm2/day, Langley)"
        ]
        p_unit_solar.value = "Kilowatt-hours per square meter per day (kWh/m2/day) [Default]"
        p_unit_solar.category = "Measurement Units & Standards"
        p_unit_solar.description = (
            "Measurement unit for surface solar radiation: Kilowatt-hours/m2/day (kWh/m2/day, default in Egypt & WMO), "
            "Megajoules/m2/day (MJ/m2/day), Watt-hours/m2/day (Wh/m2/day), or Calories/cm2/day (cal/cm2/day, Langley)."
        )

        p_exp_shp = arcpy.Parameter(
            displayName="Export Shapefiles (Optional)",
            name="Export_Shapefiles",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_exp_shp.value = False
        p_exp_shp.category = "Output Options"
        p_exp_shp.description = ("OPTIONAL (default OFF). When checked, exports per-element "
                                 "shapefiles to the Export_SHP folder and wind vector shapefiles. "
                                 "When unchecked, only the File Geodatabase, rasters and tables are produced.")

        p_ar_db = arcpy.Parameter(
            displayName="Create Arabic-Alias Database Copy (Optional)",
            name="Create_Arabic_Database",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_ar_db.value = False
        p_ar_db.category = "Output Options"
        p_ar_db.description = ("OPTIONAL (default OFF). Creates a second GDB copy "
                               "(<name>_AR.gdb) with Arabic field aliases only - field names stay "
                               "English so the copy remains reusable as offline input. "
                               "For Arabic users to read and understand the columns.")

        p14 = arcpy.Parameter(
            displayName="Climate Data Source",
            name="Climate_Data_Source",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p14.filter.type = "ValueList"
        p14.filter.list = [
            "NASA POWER API",
            "Copernicus Climate Data Store (CDS / ERA5 / AgERA5)",
            "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling",
            "Open-Meteo Historical API (ERA5 Reanalysis)",
            "NOAA ISD / GHCN Direct Station Ground Observations Archive"
        ]
        p14.value = "NASA POWER API"
        p14.category = "Data Source"
        p14.description = ("REQUIRED. Data provider for all climate queries.\n"
                           "• 'NASA POWER API' [Default]: Gridded global agroclimatology & solar radiation (1981-Present).\n"
                           "• 'Copernicus Climate Data Store (CDS / ERA5 / AgERA5)': Official ECMWF C3S reanalysis (~9 km, 1940-Present).\n"
                           "• 'Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling': Ground observations with automated satellite and reanalysis gap-filling.\n"
                           "• 'Open-Meteo Historical API (ERA5 Reanalysis)': High-resolution numerical atmospheric reanalysis (~9 km, 1940-Present).\n"
                           "• 'NOAA ISD / GHCN Direct Station Ground Observations Archive': Official ground station observational archive.")

        p_om_model = arcpy.Parameter(
            displayName="Open-Meteo Reanalysis Model",
            name="OpenMeteo_Model",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_om_model.filter.type = "ValueList"
        p_om_model.filter.list = [
            "ERA5-Land (Highest Resolution ~9 km / 0.1 deg) [Recommended]",
            "ERA5-Seamless (Combined 9-25 km / 0.1-0.25 deg)",
            "ERA5 (Standard Reanalysis ~25 km / 0.25 deg)"
        ]
        p_om_model.value = "ERA5-Land (Highest Resolution ~9 km / 0.1 deg) [Recommended]"
        p_om_model.category = "Data Source"
        p_om_model.description = ("ATMOSPHERIC REANALYSIS MODEL. "
                                  "'ERA5-Land' (default, recommended): highest spatial resolution (~9 km / 0.1 deg). "
                                  "'ERA5-Seamless': combined high-resolution model. "
                                  "'ERA5': standard global reanalysis (~25 km / 0.25 deg).")

        p_cds_key = arcpy.Parameter(
            displayName="Copernicus CDS API Key / Personal Token",
            name="CDS_API_Key",
            datatype="GPStringHidden",
            parameterType="Optional",
            direction="Input")
        p_cds_key.category = "Data Source"
        p_cds_key.description = ("COPERNICUS CDS ONLY. Optional Personal Access Token (API Key) from https://cds.climate.copernicus.eu. "
                                 "If omitted, ERA5 data streams seamlessly via the high-speed gateway.")

        # ═══ Time Window ═══
        p3 = arcpy.Parameter(
            displayName="Time Mode",
            name="Time_Mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p3.filter.type = "ValueList"
        p3.filter.list = ["Single Year", "Year Range", "Custom Date Range"]
        p3.value = "Single Year"
        p3.category = "Time Window"
        p3.description = ("REQUIRED. 'Single Year' queries January-December of one year. "
                          "'Year Range' computes multi-year climatological normals. "
                          "'Custom Date Range' queries specific start/end dates via calendar or text.")

        p4 = arcpy.Parameter(
            displayName="Single Year (type any year)",
            name="Single_Year",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p4.value = 2024
        p4.category = "Time Window"
        p4.description = "Type any year you need (free entry, no list)."

        p5 = arcpy.Parameter(
            displayName="Start Year (type any year)",
            name="Start_Year",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p5.value = 2015
        p5.category = "Time Window"
        p5.description = "Type the first year of the period (free entry, no list)."

        p6 = arcpy.Parameter(
            displayName="End Year (type any year)",
            name="End_Year",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p6.value = 2024
        p6.category = "Time Window"
        p6.description = "Type the last year of the period (free entry, no list)."

        p_start_date = arcpy.Parameter(
            displayName="Start Date",
            name="Start_Date",
            datatype="GPDate",
            parameterType="Optional",
            direction="Input")
        p_start_date.value = "01/01/2024"
        p_start_date.category = "Time Window"
        p_start_date.description = ("CUSTOM DATE RANGE ONLY. Pick from the built-in calendar "
                                    "(any past or future year) or type the date directly.")

        p_end_date = arcpy.Parameter(
            displayName="End Date",
            name="End_Date",
            datatype="GPDate",
            parameterType="Optional",
            direction="Input")
        p_end_date.value = "31/12/2024"
        p_end_date.category = "Time Window"
        p_end_date.description = ("CUSTOM DATE RANGE ONLY. Pick from the built-in calendar "
                                  "(any past or future year) or type the date directly.")

        p7 = arcpy.Parameter(
            displayName="Temporal Resolution",
            name="Temporal_Resolution",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p7.filter.type = "ValueList"
        p7.filter.list = ["Monthly", "Daily"]
        p7.value = "Monthly"
        p7.category = "Time Window"
        p7.description = ("REQUIRED. Monthly (recommended): faster, uses monthly means/rates. "
                          "Daily: detailed, required for max daily rainfall / extremes.")

        p_gf = arcpy.Parameter(
            displayName="Gap Fill Method",
            name="Gap_Fill_Method",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_gf.filter.type = "ValueList"
        p_gf.filter.list = [
            "Climatological Month Mean (Recommended)",
            "Linear + Boundary Interpolation",
            "Spatial Nearest Neighbor Fallback",
            "No Fill (skip missing)"
        ]
        p_gf.value = "Climatological Month Mean (Recommended)"
        p_gf.category = "Time Window"
        p_gf.description = ("OPTIONAL. How to handle missing months or stations (NoData/-999). "
                            "'Climatological Month Mean' (recommended): fills gaps with the average "
                            "of the same calendar month across years, with station mean fallback. "
                            "'Linear + Boundary Interpolation': fills interior gaps linearly and "
                            "endpoints using boundary fill. 'Spatial Nearest Neighbor Fallback': "
                            "estimates missing fields from nearest valid spatial stations. "
                            "'No Fill': ignores missing values.")

        p_dl = arcpy.Parameter(
            displayName="Download & Save Point Data Only (Skip Rasters & Atlas)",
            name="Download_Only",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_dl.value = False
        p_dl.category = ""
        p_dl.description = ("OPTIONAL (default OFF). When checked, the tool downloads climate data and saves "
                            "complete point feature classes (GDB, SHP, CSV) for each element, but skips "
                            "surface interpolation, raster creation, contours, and layer styling.")

        p8 = arcpy.Parameter(
            displayName="Climate Modules & Models",
            name="Climate_Modules",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p8.multiValue = True
        p8.filter.type = "ValueList"
        p8.filter.list = MODULES_ALL
        p8.value = None
        p8.category = "Climate Modules & Models"
        p8.description = (
            "Select primary climate modules and applied bioclimatic models to compute and export. "
            "Submodels (De Martonne, Evapotranspiration, UNEP, Water Deficit, Walter-Lieth, Heat Index) "
            "are located at the bottom of the list and can be selected directly; prerequisite variables "
            "are retrieved automatically if not selected."
        )

        # ═══ Variable & Field Selection ═══
        p_temporal_scope = arcpy.Parameter(
            displayName="Temporal Scope / Seasons",
            name="Temporal_Scope",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_temporal_scope.multiValue = True
        p_temporal_scope.filter.type = "ValueList"
        p_temporal_scope.filter.list = ["Annual", "Winter", "Spring", "Summer", "Autumn"]
        p_temporal_scope.value = "Annual;Winter;Spring;Summer;Autumn"
        p_temporal_scope.category = "Variable & Field Selection"
        p_temporal_scope.description = (
            "TEMPORAL MATRIX SCOPE. Select which temporal scopes and seasons to compute and map "
            "(Annual, Winter, Spring, Summer, Autumn). Uncheck any seasons not needed (e.g. keep only "
            "Annual for fast regional atlas, or Summer only for heat waves). The tool computes only the "
            "Cartesian product of selected Climate Modules and selected Temporal Scope."
        )

        p_monthly_rasters = arcpy.Parameter(
            displayName="Generate Monthly Climatology Rasters (Jan-Dec)",
            name="Generate_Monthly_Rasters",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_monthly_rasters.value = False
        p_monthly_rasters.category = "Variable & Field Selection"
        p_monthly_rasters.description = (
            "GENERATE 12 INDIVIDUAL MONTHLY RASTERS (Jan-Dec). When checked, interpolates independent "
            "climatological surface rasters for all 12 calendar months into a dedicated 'Month' subfolder "
            "for each selected element (same interpolation method, cell size and clip mask; LZW, 128x128 "
            "blocks). Requires a multi-year period (>= 2 years); single years are skipped with a warning. "
            "Wind produces 24 surfaces (12 speed W_Spd_* + 12 direction W_Dir_*)."
        )

        p_daily_sheet = arcpy.Parameter(
            displayName="Save Daily Time Series (Daily sheet)",
            name="Save_Daily_Series",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_daily_sheet.value = False
        p_daily_sheet.category = "Variable & Field Selection"
        p_daily_sheet.description = (
            "SAVE DAILY TIME SERIES INSIDE EACH ELEMENT WORKBOOK. When checked (and Temporal is Daily), "
            "adds a third 'Daily' sheet (OBJECTID, Source_ID, Date, daily values) to each element .xls; "
            "the Month sheet is always kept (computed from daily). Opt-in because daily volumes grow fast "
            "(points x days); recommended for short periods / few points. Monthly (default) ignores it. "
            "If rows exceed .xls capacity (~60000), a <Element>_daily.csv is written instead with a warning."
        )

        p_wc_ext = arcpy.Parameter(
            displayName="Wind Chill Full Suite for Cold Regions (Seasons+Ranges+Monthly)",
            name="Extended_WC_Seasons",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_wc_ext.value = False
        p_wc_ext.category = "Variable & Field Selection"
        p_wc_ext.description = (
            "OPT-IN FOR COLD REGIONS ONLY (e.g. Patagonia, Iceland, high mountains, Canada): publishes "
            "WC_Spring/Summer/Autumn_Mean, WC_Annual_Range and the 12 monthly WC means in addition "
            "to WC_Winter_Mean and WC_Annual_Mean. OFF by default: warm regions (e.g. Egypt) keep the clean "
            "2-field schema, where extra fields would merely repeat air temperature (passthrough). Same NWS "
            "equation/threshold."
        )

        p_mrng = arcpy.Parameter(
            displayName="Monthly Ranges - Interannual Variability per Month",
            name="Monthly_Ranges",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_mrng.value = False
        p_mrng.category = "Variable & Field Selection"
        p_mrng.description = (
            "OPT-IN, independent toggle (default OFF): adds per-calendar-month interannual ranges "
            "(<Prefix>_<Month>_Range, e.g. ET_December_Range = wettest December minus driest December "
            "across years) for the mean-type modules (T, R, PSL, PS, Wind speed, RH, Td, Solar, UV, "
            "Cloud, ET). Wind direction excluded. Month sheet and Month/ rasters carry them like the "
            "monthly means. Needs >= 2 valid years per month; gap-filled months yield 0."
        )

        p_hi_mon = arcpy.Parameter(
            displayName="Heat Index Monthly Means (Opt-in Suite)",
            name="Extended_HI_Months",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_hi_mon.value = False
        p_hi_mon.category = "Variable & Field Selection"
        p_hi_mon.description = (
            "OPT-IN, independent toggle (default OFF): publishes the 12 monthly Rothfusz heat-index "
            "means (HI_January_Mean ... HI_December_Mean) in addition to the 8 base Heat Index fields. "
            "Documented winter caveat: monthly values use Rothfusz year-round (= air T below 26.7C), "
            "while the seasonal HI_Winter_Mean uses Humidex. Month sheet and Month/ rasters carry "
            "them like the other monthly means."
        )

        # NOTE: Field Filter Scope comes FIRST: it drives the enabled state of
        # the two filter boxes below it (Included Summary Periods / Seasons)
        # and of the Variables checklist at the end of this group.
        p_filter_scope = arcpy.Parameter(
            displayName="Field Filter Scope",
            name="Field_Filter_Scope",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p_filter_scope.filter.type = "ValueList"
        p_filter_scope.filter.list = [
            "Full Suite (Annual + Seasonal + Monthly) [Recommended]",
            "Annual Summaries Only",
            "Seasonal Summaries Only",
            "Monthly Climatology Only (Jan - Dec)",
            "Filter by Specific Seasons & Aggregations",
            "Custom Field Checklist"
        ]
        p_filter_scope.value = "Full Suite (Annual + Seasonal + Monthly) [Recommended]"
        p_filter_scope.category = "Variable & Field Selection"
        p_filter_scope.description = (
            "REQUIRED. Controls which variables, seasons, and indicators are computed and exported. "
            "'Full Suite (Annual + Seasonal + Monthly)' (default): calculates and maps all annual, seasonal, monthly and extreme fields. "
            "'Annual Summaries Only': restricts processing strictly to annual summaries, means and totals. "
            "'Seasonal Summaries Only': restricts processing strictly to seasonal summaries (Winter, Spring, Summer, Autumn). "
            "'Monthly Climatology Only (Jan - Dec)': restricts processing strictly to the 12 individual calendar months (Jan-Dec). "
            "'Filter by Specific Seasons & Aggregations': quickly filter by specific season or summary level. "
            "'Custom Field Checklist': interactive checklist table at the end of this group to select/unselect exact fields by name."
        )

        p_sel_fields = arcpy.Parameter(
            displayName="Variables Selection (Checklist)",
            name="Selected_Fields",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_sel_fields.multiValue = True
        p_sel_fields.filter.type = "ValueList"
        p_sel_fields.filter.list = []
        p_sel_fields.value = None
        p_sel_fields.category = "Variable & Field Selection"
        p_sel_fields.description = (
            "VARIABLES SELECTION. Interactive checklist of climate variables and indicators to compute. "
            "All fields for the selected Climate Modules are included by default. "
            "Check or uncheck individual variables as needed, or use the Filter Scope above to filter by seasons/periods."
        )

        p_inc_aggs = arcpy.Parameter(
            displayName="Included Summary Periods",
            name="Included_Aggregations",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_inc_aggs.multiValue = True
        p_inc_aggs.filter.type = "ValueList"
        p_inc_aggs.filter.list = [
            "Annual Summaries",
            "Seasonal Summaries",
            "Detailed Monthly Climatology (Jan-Dec)",
            "Extreme & Bioclimatic Indices"
        ]
        p_inc_aggs.value = "Annual Summaries;Seasonal Summaries;Extreme & Bioclimatic Indices"
        p_inc_aggs.category = "Variable & Field Selection"
        p_inc_aggs.description = (
            "PERIOD FILTER ONLY. Choose summary levels to generate. "
            "'Annual Summaries': annual means and totals. "
            "'Seasonal Summaries': seasonal means and totals (Winter, Spring, Summer, Autumn). "
            "'Detailed Monthly Climatology': 12 individual monthly climatologies (Jan-Dec). "
            "'Extreme & Bioclimatic Indices': heat index, ranges, extreme months, rain days."
        )

        p_inc_seasons = arcpy.Parameter(
            displayName="Included Seasons",
            name="Included_Seasons",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_inc_seasons.multiValue = True
        p_inc_seasons.filter.type = "ValueList"
        p_inc_seasons.filter.list = [
            "Winter (DJF)",
            "Spring (MAM)",
            "Summer (JJA)",
            "Autumn (SON)"
        ]
        p_inc_seasons.value = "Winter (DJF);Spring (MAM);Summer (JJA);Autumn (SON)"
        p_inc_seasons.category = "Variable & Field Selection"
        p_inc_seasons.description = (
            "SEASONS FILTER ONLY. Select which seasons to generate. "
            "Uncheck any season you do not need (e.g. keep only Summer or only Winter)."
        )

        # ═══ Interpolation Parameters ═══
        p11 = arcpy.Parameter(
            displayName="Interpolation Method",
            name="Interpolation_Method",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        p11.filter.type = "ValueList"
        p11.filter.list = ["IDW", "Ordinary Kriging", "Spline", "Natural Neighbor"]
        p11.value = "IDW"
        p11.category = "Interpolation Parameters"
        p11.description = ("REQUIRED. IDW (default) | Ordinary Kriging | Spline | Natural Neighbor. "
                           "Requires Spatial Analyst.")

        p_idw_prof = arcpy.Parameter(
            displayName="IDW Curve Profile",
            name="IDW_Curve_Profile",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_idw_prof.filter.type = "ValueList"
        p_idw_prof.filter.list = [
            "Gentle / Smooth (Power 1.2)",
            "Standard Quadratic (Power 2.0)",
            "Regional Broad (Power 0.7)",
            "Custom Power"
        ]
        p_idw_prof.value = "Gentle / Smooth (Power 1.2)"
        p_idw_prof.category = "Interpolation Parameters"
        p_idw_prof.description = ("IDW ONLY. Distance decay curve profile. 'Gentle / Smooth' (power 1.2) "
                                  "eliminates concentric island/bullseye artifacts. 'Standard' (power 2.0) "
                                  "is the classical steep quadratic decay. 'Regional Broad' (power 0.7) "
                                  "gives extended regional smoothing. 'Custom Power' allows typing an arbitrary power.")

        p15 = arcpy.Parameter(
            displayName="IDW Power",
            name="IDW_Power",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        p15.value = 1.2
        p15.category = "Interpolation Parameters"
        p15.description = "IDW ONLY. Power parameter. DEFAULT 1.2 for smooth, seamless climate surfaces without artificial bullseyes."

        p16 = arcpy.Parameter(
            displayName="IDW Search Radius Type",
            name="IDW_Search_Type",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p16.filter.type = "ValueList"
        p16.filter.list = ["Variable", "Fixed"]
        p16.value = "Variable"
        p16.category = "Interpolation Parameters"
        p16.description = "IDW ONLY. 'Variable' (default): expand search. 'Fixed': fixed radius."

        p17 = arcpy.Parameter(
            displayName="IDW Number of Points",
            name="IDW_Num_Points",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p17.value = 12
        p17.category = "Interpolation Parameters"
        p17.description = "IDW ONLY. Number of neighbouring points. DEFAULT 12."

        p18 = arcpy.Parameter(
            displayName="IDW Maximum Distance (metres, optional)",
            name="IDW_Max_Distance",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        p18.category = "Interpolation Parameters"
        p18.description = "IDW ONLY, OPTIONAL. Caps the search neighbourhood in metres."

        p19 = arcpy.Parameter(
            displayName="Kriging Semivariogram Model",
            name="Krig_Model",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p19.filter.type = "ValueList"
        p19.filter.list = ["Spherical", "Circular", "Exponential", "Gaussian"]
        p19.value = "Spherical"
        p19.category = "Interpolation Parameters"
        p19.description = "KRIGING ONLY. DEFAULT Spherical."

        p20 = arcpy.Parameter(
            displayName="Kriging Type",
            name="Krig_Type",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p20.filter.type = "ValueList"
        p20.filter.list = ["Ordinary", "Universal"]
        p20.value = "Ordinary"
        p20.category = "Interpolation Parameters"
        p20.description = "KRIGING ONLY. 'Ordinary' (default) or 'Universal'."

        p21 = arcpy.Parameter(
            displayName="Kriging Number of Points",
            name="Krig_Num_Points",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p21.value = 12
        p21.category = "Interpolation Parameters"
        p21.description = "KRIGING ONLY. DEFAULT 12."

        p_sp_type = arcpy.Parameter(
            displayName="Spline Type",
            name="Spline_Type",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_sp_type.filter.type = "ValueList"
        p_sp_type.filter.list = ["Tension", "Regularized"]
        p_sp_type.value = "Tension"
        p_sp_type.category = "Interpolation Parameters"
        p_sp_type.description = ("SPLINE ONLY. 'Tension' (recommended for climate): produces taut, smooth "
                                 "surfaces that honor exact point values without overshoots. 'Regularized': "
                                 "smooth surface that may overshoot local extremes.")

        p_sp_weight = arcpy.Parameter(
            displayName="Spline Weight",
            name="Spline_Weight",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        p_sp_weight.value = 5.0
        p_sp_weight.category = "Interpolation Parameters"
        p_sp_weight.description = ("SPLINE ONLY. Weight parameter. For Tension Spline, higher weights (e.g. 5.0-10.0) "
                                   "produce stiffer, less smoothed surfaces closely matching points; smaller weights "
                                   "produce smoother surfaces. DEFAULT 5.0.")

        p_sp_pts = arcpy.Parameter(
            displayName="Spline Number of Points",
            name="Spline_Num_Points",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p_sp_pts.value = 12
        p_sp_pts.category = "Interpolation Parameters"
        p_sp_pts.description = "SPLINE ONLY. Number of neighbouring points used for interpolation. DEFAULT 12."

        p9 = arcpy.Parameter(
            displayName="Base Cell Size (Meters) [Default: 500 Meters]",
            name="Base_Cell_Size",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        p9.value = "500 Meters"
        p9.category = "Interpolation Parameters"
        p9.description = ("REQUIRED. Cell size for all rasters in Meters or Kilometers. "
                          "Default: 500 Meters. NOTE: fine cells improve appearance only; "
                          "native NASA POWER resolution stays coarse (~0.5 deg).")

        p10 = arcpy.Parameter(
            displayName="Wind Vector Spacing / Cell Size (Meters)",
            name="Wind_Factor_Cell_Size",
            datatype="GPLinearUnit",
            parameterType="Optional",
            direction="Input")
        p10.value = "25000 Meters"
        p10.category = "Interpolation Parameters"
        p10.description = ("OPTIONAL. Independent coarser spacing for wind arrow points "
                           "in Meters or Kilometers. Default: 25000 Meters. "
                           "Enabled only when Wind module is selected.")

        # ═══ Raster Reclassification ═══
        p_reclass_en = arcpy.Parameter(
            displayName="Enable Raster Reclassification",
            name="Enable_Raster_Reclass",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p_reclass_en.value = False
        p_reclass_en.category = "Raster Reclassification"
        p_reclass_en.description = (
            "OPTIONAL (default OFF). When checked, generates classified rasters (_cls.tif) "
            "with discrete thematic classes and embedded colormaps alongside the continuous rasters. "
            "When unchecked, outputs only raw continuous floating-point rasters.")

        p_reclass_cnt = arcpy.Parameter(
            displayName="Number of Classes",
            name="Reclass_Classes_Count",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p_reclass_cnt.value = 7
        p_reclass_cnt.category = "Raster Reclassification"
        p_reclass_cnt.description = (
            "RECLASS ONLY. Number of classification bins/classes (2 to 32). Default: 7.")

        p_reclass_meth = arcpy.Parameter(
            displayName="Classification Method",
            name="Reclass_Method",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p_reclass_meth.filter.type = "ValueList"
        p_reclass_meth.filter.list = [
            "Natural Breaks (Jenks)",
            "Equal Interval",
            "Equal Area (Quantile)",
            "Geometric Interval",
            "Standard Deviation"
        ]
        p_reclass_meth.value = "Natural Breaks (Jenks)"
        p_reclass_meth.category = "Raster Reclassification"
        p_reclass_meth.description = (
            "RECLASS ONLY. Statistical classification method to partition raster continuous values.")

        # ═══ Pressure Contour ═══
        p13 = arcpy.Parameter(
            displayName="Create PSL Isobar Contour (Optional)",
            name="Create_Isobars",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p13.value = False
        p13.category = "Pressure Contour"
        p13.description = ("OPTIONAL. Creates isobar polylines from pressure rasters "
                           "when a pressure module is selected.")

        p31 = arcpy.Parameter(
            displayName="Pressure Contour Scheme (Optional)",
            name="Pressure_Interval_Scheme",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p31.filter.type = "ValueList"
        p31.filter.list = ["Global Standard (4 mbar)", "Local Detailed (2 mbar)",
                           "Custom Interval"]
        p31.value = "Global Standard (4 mbar)"
        p31.category = "Pressure Contour"
        p31.description = "ISOBARS ONLY. Contour interval preset."

        p32 = arcpy.Parameter(
            displayName="Custom Pressure Step (mbar) (Optional)",
            name="Custom_Pressure_Step",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        p32.value = 4.0
        p32.category = "Pressure Contour"
        p32.description = "ISOBARS ONLY, CUSTOM SCHEME ONLY. Step in mbar/hPa. Must be > 0."

        # ═══ Post-Processing ═══
        p25 = arcpy.Parameter(
            displayName="Apply Focal Smoothing",
            name="Focal_Smoothing",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p25.value = False
        p25.category = "Post-Processing"
        p25.description = "OPTIONAL. Smooths interpolated rasters with Focal Statistics."

        p26 = arcpy.Parameter(
            displayName="Focal Statistic",
            name="Focal_Statistic",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p26.filter.type = "ValueList"
        p26.filter.list = ["MEAN", "MEDIAN", "MINIMUM", "MAXIMUM", "STD"]
        p26.value = "MEAN"
        p26.category = "Post-Processing"
        p26.description = "FOCAL ONLY. DEFAULT MEAN."

        p27 = arcpy.Parameter(
            displayName="Focal Neighborhood (cells)",
            name="Focal_Neighborhood",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        p27.value = 3
        p27.category = "Post-Processing"
        p27.description = "FOCAL ONLY. Square neighbourhood in cells (3 = 3x3). DEFAULT 3."

        p24 = arcpy.Parameter(
            displayName="Point Tolerance (0 = off)",
            name="Point_Tolerance",
            datatype="GPLinearUnit",
            parameterType="Optional",
            direction="Input")
        p24.value = "0 Meters"
        p24.category = "Pre-Processing"
        p24.description = ("OPTIONAL (default 0 = OFF). Merges points closer than this distance "
                           "before download to reduce interpolation artifacts.")

        # ═══ Map Options ═══
        p23 = arcpy.Parameter(
            displayName="Add Results To Current Map",
            name="Add_To_Map",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p23.value = False
        p23.category = "Map Options"
        p23.description = "OPTIONAL (default OFF). Safely adds final layers to the current map sequentially."

        p28 = arcpy.Parameter(
            displayName="Map Add Modules (elements to add)",
            name="Map_Add_Modules",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        p28.multiValue = True
        p28.filter.type = "ValueList"
        p28.filter.list = []
        p28.value = None
        p28.category = "Map Options"
        p28.description = "ADD-TO-MAP ONLY. Choose which elements to add to the map."

        # ═══ Maintenance & Cache ═══
        p22 = arcpy.Parameter(
            displayName="Purge Intermediate Cache",
            name="Purge_Cache",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        p22.value = True
        p22.category = "Maintenance & Cache"
        p22.description = ("OPTIONAL (default ON). Deletes intermediate products after use.")

        return [p_op_mode, p_wf_mode, p_dl, p0, p_precalc, p1, p_study_name, p12, p2,
                p_unit_sys, p_unit_temp, p_unit_precip, p_unit_press, p_unit_wind, p_unit_solar,
                p_exp_shp, p_ar_db, p14, p_om_model, p_cds_key,
                p3, p4, p5, p6, p_start_date, p_end_date, p7, p_gf,
                p24,
                p8, p_temporal_scope, p_monthly_rasters, p_daily_sheet, p_wc_ext, p_mrng, p_hi_mon, p_filter_scope, p_inc_aggs, p_inc_seasons, p_sel_fields,
                p11, p9, p10, p_idw_prof, p15, p16, p17, p18, p19, p20, p21,
                p_sp_type, p_sp_weight, p_sp_pts,
                p_reclass_en, p_reclass_cnt, p_reclass_meth,
                p13, p31, p32,
                p25, p26, p27,
                p23, p28,
                p22]

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        pdict = dict((p.name, p) for p in parameters)
        p_op = pdict.get("Operation_Mode")
        op_text = p_op.valueAsText if p_op else "Download & Generate Atlas (Full Pipeline) [Default]"
        is_offline = bool(op_text and ("Offline" in op_text or "Existing" in op_text or op_text.startswith("Interpolate & Map Existing Data")))

        # --- Measurement Units synchronization ---
        p_usys = pdict.get("Measurement_Units_System")
        usys_val = p_usys.valueAsText if p_usys else "Metric"
        is_custom_units = bool(usys_val and "Custom" in usys_val)
        is_imperial = bool(usys_val and "Imperial" in usys_val)

        p_ut = pdict.get("Temperature_Unit")
        p_up = pdict.get("Precipitation_Unit")
        p_upr = pdict.get("Pressure_Unit")
        p_uw = pdict.get("Wind_Speed_Unit")
        p_usol = pdict.get("Solar_Radiation_Unit")

        if p_ut:
            p_ut.enabled = is_custom_units
            if not is_custom_units:
                p_ut.value = "Fahrenheit (°F)" if is_imperial else "Celsius (°C) [Default]"
        if p_up:
            p_up.enabled = is_custom_units
            if not is_custom_units:
                p_up.value = "Inches (in)" if is_imperial else "Millimeters (mm) [Default]"
        if p_upr:
            p_upr.enabled = is_custom_units
            if not is_custom_units:
                p_upr.value = "Inches of Mercury (inHg)" if is_imperial else "Hectopascals (hPa) [Default]"
        if p_uw:
            p_uw.enabled = is_custom_units
            if not is_custom_units:
                p_uw.value = "Miles per hour (mph)" if is_imperial else "Meters per second (m/s) [Default]"
        if p_usol:
            p_usol.enabled = is_custom_units
            if not is_custom_units:
                p_usol.value = "Megajoules per square meter per day (MJ/m2/day)" if is_imperial else "Kilowatt-hours per square meter per day (kWh/m2/day) [Default]"

        p_in = pdict.get("Input_Point_Features") or pdict.get("Input_Points")
        p_pre = pdict.get("Precalculated_Point_Layers") or pdict.get("Precalculated_Point_Layer")
        if p_in:
            p_in.enabled = not is_offline
            p_in.parameterType = "Required" if not is_offline else "Optional"
        if p_pre:
            p_pre.enabled = is_offline
            p_pre.parameterType = "Required" if is_offline else "Optional"

        p_wf = pdict.get("Execution_Workflow_Mode")
        if p_wf:
            p_wf.enabled = not is_offline

        p_dl = pdict.get("Download_Only")
        dl = bool(p_dl.value) if (p_dl and p_dl.value is not None and not is_offline) else False
        if p_dl:
            p_dl.enabled = not is_offline

        # --- Climate Data Source & Model sync ---
        p_src = pdict.get("Climate_Data_Source")
        if p_src:
            p_src.enabled = not is_offline
        src_text = p_src.valueAsText if p_src else "NASA POWER API"
        use_om = bool(src_text and src_text.startswith("Open-Meteo"))
        use_cds = bool(src_text and ("Copernicus" in src_text or "CDS" in src_text))
        if "OpenMeteo_Model" in pdict:
            pdict["OpenMeteo_Model"].enabled = (not is_offline) and (use_om or use_cds)
        if "CDS_API_Key" in pdict:
            pdict["CDS_API_Key"].enabled = (not is_offline) and use_cds

        # --- Time Mode & Date controls ---
        p_mode = pdict.get("Time_Mode") or pdict.get("Time_Range_Mode")
        if p_mode:
            p_mode.enabled = not is_offline
        mode = p_mode.valueAsText if p_mode else "Single Year"
        single = bool(mode and mode.startswith("Single Year"))
        yr_range = bool(mode and mode.startswith("Year Range"))
        custom_range = bool(mode and "Custom Date" in mode)

        if "Single_Year" in pdict:
            pdict["Single_Year"].enabled = (not is_offline) and single
        if "Start_Year" in pdict:
            pdict["Start_Year"].enabled = (not is_offline) and yr_range
        if "End_Year" in pdict:
            pdict["End_Year"].enabled = (not is_offline) and yr_range
        if "Start_Date" in pdict:
            pdict["Start_Date"].enabled = (not is_offline) and custom_range
        if "End_Date" in pdict:
            pdict["End_Date"].enabled = (not is_offline) and custom_range
        if "Temporal_Resolution" in pdict:
            pdict["Temporal_Resolution"].enabled = not is_offline
        if "Gap_Fill_Method" in pdict:
            pdict["Gap_Fill_Method"].enabled = not is_offline

        p_mods = pdict.get("Climate_Modules")

        # --- Precalculated Layer(s) Field Discovery (Offline Mode) ---
        if is_offline and p_pre and p_pre.value:
            try:
                precalc_val = p_pre.valueAsText
                last_precalc = getattr(self, "_last_precalc_layer", None)
                if precalc_val != last_precalc:
                    lyr_paths = [lp.strip().strip("'\"") for lp in (precalc_val or "").split(";") if lp.strip().strip("'\"")]
                    layer_fnames = set()
                    for lp in lyr_paths:
                        try:
                            fld_objs = arcpy.ListFields(lp)
                            for f in fld_objs:
                                layer_fnames.add(f.name)
                                if f.name in REV_SHP_MAP:
                                    layer_fnames.add(REV_SHP_MAP[f.name])
                        except Exception:
                            pass

                    detected_mods = []
                    for m in PRIMARY_MODULES_ALL:
                        m_flds = MODULE_FIELDS.get(m, [])
                        shp_flds = [SHP_FIELD_MAP.get(f, f[:10]) for f in m_flds]
                        if any(f in layer_fnames or sf in layer_fnames for f, sf in zip(m_flds, shp_flds)):
                            detected_mods.append(m)

                    for sub_name in SUBMODELS_ALL:
                        sinfo = SUBMODEL_DEPS.get(sub_name)
                        if not sinfo:
                            continue
                        req_flds = sinfo.get("fields", [sinfo["field"]])
                        has_out = any(f in layer_fnames for f in req_flds)
                        has_inp = False
                        if "Temperature" in sinfo["modules"] and "Precipitation" in sinfo["modules"]:
                            has_inp = any(f in layer_fnames for f in ("T_Annual_Mean", "T_AnMean", "T2M")) and \
                                      any(f in layer_fnames for f in ("R_Annual_Mean", "R_AnnMean", "R_Annual_Total", "R_AnnTot", "PRECTOTCORR"))
                        elif "Temperature" in sinfo["modules"] and "Relative Humidity" in sinfo["modules"]:
                            has_inp = any(f in layer_fnames for f in ("T_Summer_Mean", "T_SumMean", "T_Annual_Mean", "T_AnMean", "T2M")) and \
                                      any(f in layer_fnames for f in ("RH_Summer_Mean", "RH_SuMean", "RH_Annual_Mean", "RH_AnMean", "RH2M"))
                        elif "Temperature" in sinfo["modules"]:
                            has_inp = any(f in layer_fnames for f in ("T_Annual_Mean", "T_AnMean", "T2M"))
                        if has_out or has_inp:
                            if sub_name not in detected_mods:
                                detected_mods.append(sub_name)

                    if detected_mods and p_mods and not p_mods.altered:
                        p_mods.value = ";".join(detected_mods)

                    self._last_precalc_layer = precalc_val
            except Exception:
                pass

        # --- Dynamic sync between Climate Modules / Submodels and Map Add Modules ---
        p_map_mods = pdict.get("Map_Add_Modules")
        p_add_map = pdict.get("Add_To_Map")
        mods_text = p_mods.valueAsText if p_mods else ""
        raw_mods = [m.strip().strip("'\"") for m in (mods_text.split(";") if mods_text else []) if m.strip().strip("'\"")]
        map_choices = []
        active_mods = []
        for m in raw_mods:
            can = resolve_module_canonical(m)
            target = can if can else m
            if target not in map_choices:
                map_choices.append(target)
            if target not in active_mods:
                active_mods.append(target)
        if not raw_mods:
            map_choices = []

        if p_map_mods:
            p_map_mods.filter.list = map_choices if map_choices else list(ALL_CANONICAL_MODULES)
            last_choices = getattr(self, "_last_map_choices", None)
            if map_choices != last_choices or not p_map_mods.altered:
                p_map_mods.value = ";".join(map_choices) if map_choices else None
                self._last_map_choices = list(map_choices) if map_choices else []

        # --- Field Filter Scope & Variable/Season controls ---
        p_scope = pdict.get("Field_Filter_Scope")
        scope = p_scope.valueAsText if p_scope else "Full Suite (Annual + Seasonal + Monthly) [Recommended]"
        is_seasons_filter = bool(scope and (scope.startswith("Filter by Specific Seasons") or scope.startswith("Filter by Seasons")))
        is_custom_checklist = bool(scope and scope.startswith("Custom Field"))
        is_seasonal_only = bool(scope and (("Seasonal" in scope and "Only" in scope) or "فصلي فقط" in scope))
        is_monthly_only = bool(scope and (("Monthly" in scope and "Only" in scope) or "شهري تفصيلي" in scope))

        p_aggs = pdict.get("Included_Aggregations")
        p_seas = pdict.get("Included_Seasons")
        p_flds = pdict.get("Selected_Fields")

        if p_aggs:
            p_aggs.enabled = is_seasons_filter or is_custom_checklist

        aggs_val = p_aggs.valueAsText if p_aggs else ""
        has_seasonal = ("Seasonal" in aggs_val) if aggs_val else True

        if p_seas:
            p_seas.enabled = is_seasonal_only or ((is_seasons_filter or is_custom_checklist) and has_seasonal)

        p_tscope = pdict.get("Temporal_Scope")
        tscope_val = p_tscope.valueAsText if p_tscope else None

        seas_val = p_seas.valueAsText if p_seas else ""
        active_seasons = [s.strip().strip("'\"") for s in seas_val.split(";") if s.strip().strip("'\"")] if seas_val else None
        active_aggs = [a.strip().strip("'\"") for a in aggs_val.split(";") if a.strip().strip("'\"")] if aggs_val else None

        if p_flds:
            p_flds.enabled = is_custom_checklist
            if is_custom_checklist:
                candidates = get_candidate_fields(active_mods, active_aggs, active_seasons, temporal_scope=tscope_val)
                cand_labels = [c[1] for c in candidates]
                p_flds.filter.list = cand_labels
                last_cand_set = getattr(self, "_last_cand_set", None)
                curr_cand_set = tuple(sorted(cand_labels))
                if curr_cand_set != last_cand_set:
                    if p_flds.valueAsText:
                        old_items = [x.strip().strip("'\"") for x in p_flds.valueAsText.split(";") if x.strip().strip("'\"")]
                        retained = [x for x in old_items if x in cand_labels]
                        if retained:
                            p_flds.value = ";".join(retained)
                        else:
                            p_flds.value = ";".join(cand_labels) if cand_labels else None
                    else:
                        p_flds.value = ";".join(cand_labels) if cand_labels else None
                    self._last_cand_set = curr_cand_set
            elif is_seasons_filter:
                candidates = get_candidate_fields(active_mods, active_aggs, active_seasons, temporal_scope=tscope_val)
                cand_labels = [c[1] for c in candidates]
                p_flds.filter.list = cand_labels
                p_flds.value = ";".join(cand_labels) if cand_labels else None
            else:
                candidates = get_candidate_fields(active_mods, temporal_scope=tscope_val)
                cand_labels = [c[1] for c in candidates]
                p_flds.filter.list = cand_labels
                last_mods_all = getattr(self, "_last_mods_all", None)
                curr_mods_all = (tuple(sorted(active_mods)), tscope_val)
                if curr_mods_all != last_mods_all:
                    p_flds.value = ";".join(cand_labels) if cand_labels else None
                    self._last_mods_all = curr_mods_all

        # --- Dynamic interpolation panel ---
        p_meth = pdict.get("Interpolation_Method")
        meth = p_meth.valueAsText if p_meth else "IDW"
        is_idw = (meth == "IDW")
        is_krig = (meth == "Ordinary Kriging")
        is_spline = (meth == "Spline")

        # Sync IDW Curve Profile with IDW Power
        p_prof = pdict.get("IDW_Curve_Profile")
        p_pow = pdict.get("IDW_Power")
        if p_prof and p_pow:
            prof_val = p_prof.valueAsText or "Gentle / Smooth (Power 1.2)"
            last_prof = getattr(self, "_last_prof", None)
            if prof_val != last_prof:
                if "1.2" in prof_val:
                    p_pow.value = 1.2
                elif "2.0" in prof_val:
                    p_pow.value = 2.0
                elif "0.7" in prof_val:
                    p_pow.value = 0.7
                self._last_prof = prof_val

        for k in ("IDW_Curve_Profile", "IDW_Search_Type", "IDW_Num_Points", "IDW_Max_Distance"):
            if k in pdict:
                pdict[k].enabled = is_idw and not dl
        if "IDW_Power" in pdict:
            is_custom = prof_val.startswith("Custom") if prof_val else False
            pdict["IDW_Power"].enabled = is_idw and (not dl) and is_custom
        for k in ("Krig_Model", "Krig_Type", "Krig_Num_Points"):
            if k in pdict:
                pdict[k].enabled = is_krig and not dl
        for k in ("Spline_Type", "Spline_Weight", "Spline_Num_Points"):
            if k in pdict:
                pdict[k].enabled = is_spline and not dl
        for k in ("Interpolation_Method", "Base_Cell_Size", "Create_Isobars"):
            if k in pdict:
                pdict[k].enabled = not dl

        has_wind = ("Wind" in active_mods) or any(m.strip().lower() == "wind" for m in raw_mods)
        if "Wind_Factor_Cell_Size" in pdict:
            pdict["Wind_Factor_Cell_Size"].enabled = (not dl) and has_wind

        # Raster Reclassification options
        p_rc_en = pdict.get("Enable_Raster_Reclass")
        rc_on = bool(p_rc_en.value) if p_rc_en and p_rc_en.value is not None else False
        if p_rc_en:
            p_rc_en.enabled = not dl
        if "Reclass_Classes_Count" in pdict:
            pdict["Reclass_Classes_Count"].enabled = rc_on and not dl
        if "Reclass_Method" in pdict:
            pdict["Reclass_Method"].enabled = rc_on and not dl

        # Focal options
        p_focal = pdict.get("Focal_Smoothing")
        focal_on = bool(p_focal.value) if p_focal and p_focal.value is not None else False
        if "Focal_Smoothing" in pdict:
            pdict["Focal_Smoothing"].enabled = not dl
        if "Focal_Statistic" in pdict:
            pdict["Focal_Statistic"].enabled = focal_on and not dl
        if "Focal_Neighborhood" in pdict:
            pdict["Focal_Neighborhood"].enabled = focal_on and not dl

        # Map Options
        if p_add_map:
            p_add_map.enabled = not dl
        if p_map_mods:
            p_map_mods.enabled = bool(p_add_map.value if p_add_map else False) and not dl

        # Isobars
        p_iso = pdict.get("Create_Isobars")
        iso_on = bool(p_iso.value) if p_iso and p_iso.value is not None else False
        has_p = ("Sea Level Pressure" in active_mods) or ("Surface Pressure" in active_mods)
        show_iso = bool(iso_on and has_p)
        if "Pressure_Interval_Scheme" in pdict:
            pdict["Pressure_Interval_Scheme"].enabled = show_iso
        p_scheme = pdict.get("Pressure_Interval_Scheme")
        scheme = p_scheme.valueAsText if p_scheme else "Global Standard (4 mbar)"
        if "Custom_Pressure_Step" in pdict:
            if show_iso and scheme == "Custom Interval":
                pdict["Custom_Pressure_Step"].enabled = True
            else:
                if show_iso and scheme.startswith("Global"):
                    pdict["Custom_Pressure_Step"].value = 4.0
                elif show_iso:
                    pdict["Custom_Pressure_Step"].value = 2.0
        # Daily time series persistence control
        p_temp = pdict.get("Temporal_Resolution")
        p_dly = pdict.get("Save_Daily_Series")
        if p_temp and p_dly:
            t_val = p_temp.valueAsText or "Monthly"
            is_daily = bool(t_val and ("Daily" in t_val or "يومي" in t_val))
            p_dly.enabled = is_daily
            if is_daily:
                if not p_dly.altered:
                    p_dly.value = True
            else:
                p_dly.value = False

        return


    def updateMessages(self, parameters):
        try:
            for p in parameters:
                try:
                    p.clearMessage()
                except Exception:
                    pass
            pdict = dict((p.name, p) for p in parameters)
            p_op = pdict.get("Operation_Mode")
            op_text = p_op.valueAsText if p_op else "Download & Generate Atlas (Full Pipeline) [Default]"
            is_offline = bool(op_text and op_text.startswith("Interpolate & Map Existing Data"))

            p_dl = pdict.get("Download_Only")
            dl_only = bool(p_dl.value) if (p_dl and p_dl.value is not None and not is_offline) else False

            if not is_offline:
                p_in = pdict.get("Input_Point_Features") or pdict.get("Input_Points")
                if p_in and p_in.value:
                    try:
                        desc = arcpy.Describe(p_in.value)
                        if desc.shapeType != "Point":
                            p_in.setErrorMessage("Input must be a Point layer.")
                    except Exception:
                        pass
            else:
                p_pre = pdict.get("Precalculated_Point_Layers") or pdict.get("Precalculated_Point_Layer")
                if p_pre and p_pre.value:
                    try:
                        lyr_list = [l.strip().strip("'\"") for l in (p_pre.valueAsText or "").split(";") if l.strip().strip("'\"")]
                        for lyr in lyr_list:
                            desc = arcpy.Describe(lyr)
                            if desc.shapeType not in ("Point", "Multipoint"):
                                p_pre.setErrorMessage("Precalculated layer '%s' must be a Point or Multipoint layer." % os.path.basename(lyr))
                                break
                    except Exception:
                        pass

            if not is_offline:
                p_mode = pdict.get("Time_Mode") or pdict.get("Time_Range_Mode")
                mode = p_mode.valueAsText if p_mode else "Single Year"
                if mode == "Single Year":
                    p_sy = pdict.get("Single_Year")
                    y = p_sy.value if p_sy else None
                    if y is None:
                        if p_sy:
                            p_sy.setErrorMessage("Type the year you need (free entry).")
                    else:
                        try:
                            yi = int(y)
                        except Exception:
                            if p_sy:
                                p_sy.setErrorMessage("Type the year as a number (e.g. 2025).")
                        else:
                            if yi < 1981 and p_sy:
                                p_sy.setWarningMessage("Years before 1981 have no NASA POWER data.")
                elif mode == "Year Range":
                    p_s = pdict.get("Start_Year")
                    p_e = pdict.get("End_Year")
                    s = p_s.value if p_s else None
                    e = p_e.value if p_e else None
                    if s is None or e is None:
                        if p_s:
                            p_s.setErrorMessage("Type Start and End years (free entry).")
                    else:
                        try:
                            si, ei = int(s), int(e)
                        except Exception:
                            if p_s:
                                p_s.setErrorMessage("Type years as numbers (e.g. 1990 and 2026).")
                        else:
                            if si > ei and p_e:
                                p_e.setErrorMessage("End Year must be >= Start Year.")
                            if (si < 1981 or ei < 1981) and p_s:
                                p_s.setWarningMessage("NASA POWER coverage starts 1981.")
                elif mode == "Custom Date Range":
                    p_sd = pdict.get("Start_Date")
                    p_ed = pdict.get("End_Date")
                    d_start = parse_gp_date(p_sd.value if p_sd else None)
                    d_end = parse_gp_date(p_ed.value if p_ed else None)
                    if not d_start and p_sd:
                        p_sd.setErrorMessage("Pick or type the Start Date (any year).")
                    if not d_end and p_ed:
                        p_ed.setErrorMessage("Pick or type the End Date (any year).")
                    if d_start and d_end:
                        if d_start > d_end and p_ed:
                            p_ed.setErrorMessage("End Date must be on or after Start Date.")

            p_mods = pdict.get("Climate_Modules")
            mods = p_mods.valueAsText if p_mods else ""
            if mods:
                raw_items = [m.strip().strip("'\"") for m in mods.split(";") if m.strip().strip("'\"")]
                curr_can_mods = [resolve_module_canonical(m) for m in raw_items if resolve_module_canonical(m)]
                for item in raw_items:
                    res_s = resolve_submodel_name(item)
                    if res_s:
                        req_m = SUBMODEL_DEPS[res_s].get("modules", [])
                        unsel = [rm for rm in req_m if rm not in curr_can_mods]
                        if unsel:
                            p_mods.setWarningMessage(
                                "Module '%s' requires %s. "
                                "Prerequisite data will be queried automatically as temporary intermediate data."
                                % (SUBMODEL_DEPS[res_s]["canonical"], ", ".join(unsel))
                            )

            p_scope = pdict.get("Field_Filter_Scope")
            scope = p_scope.valueAsText if p_scope else "Full Suite (Annual + Seasonal + Monthly) [Recommended]"
            if scope and not (scope.startswith("All Variables") or "Full Suite" in scope):
                p_aggs = pdict.get("Included_Aggregations")
                p_seas = pdict.get("Included_Seasons")
                p_flds = pdict.get("Selected_Fields")
                active_mods_list = []
                for m in (mods.split(";") if mods else []):
                    m_clean = m.strip().strip("'\"")
                    if m_clean:
                        can = resolve_module_canonical(m_clean)
                        target = can if can else m_clean
                        if target not in active_mods_list:
                            active_mods_list.append(target)
                aggs_txt = p_aggs.valueAsText if p_aggs else ""
                aggs_list = [a.strip().strip("'\"") for a in aggs_txt.split(";") if a.strip().strip("'\"")] if aggs_txt else []
                seas_txt = p_seas.valueAsText if p_seas else ""
                seas_list = [s.strip().strip("'\"") for s in seas_txt.split(";") if s.strip().strip("'\"")] if seas_txt else []
                flds_txt = p_flds.valueAsText if p_flds else ""

                filtered = resolve_filtered_fields(active_mods_list, scope, aggs_list, seas_list, flds_txt)
                total_f = sum(len(flist) for flist in filtered.values())
                if total_f == 0:
                    if scope.startswith("Custom Field") and p_flds:
                        p_flds.setErrorMessage("At least one custom field must be selected.")
                    elif p_scope:
                        p_scope.setErrorMessage("No climate indicators match the selected filter criteria.")

            if not dl_only:
                for k in ("Base_Cell_Size", "Wind_Factor_Cell_Size"):
                    p_c = pdict.get(k)
                    v = (p_c.valueAsText if p_c else "") or ""
                    if not v.strip() and p_c:
                        p_c.setErrorMessage("Cell size is required (e.g. 5000 Meters).")

            p_meth = pdict.get("Interpolation_Method")
            meth = p_meth.valueAsText if p_meth else "IDW"
            if meth == "IDW" and not dl_only:
                p_pow = pdict.get("IDW_Power")
                if p_pow and (p_pow.value is None or float(p_pow.value) <= 0):
                    p_pow.setErrorMessage("IDW Power must be > 0 (default 1.2).")
                p_pts = pdict.get("IDW_Num_Points")
                if p_pts and (p_pts.value is None or int(p_pts.value) < 1):
                    p_pts.setErrorMessage("IDW Number of Points must be >= 1 (default 12).")
                p_st = pdict.get("IDW_Search_Type")
                if p_st and (p_st.valueAsText or "Variable") == "Fixed":
                    p_md = pdict.get("IDW_Max_Distance")
                    if p_md and (p_md.value is None or float(p_md.value) <= 0):
                        p_md.setErrorMessage("Fixed search requires Maximum Distance > 0 (metres).")
            elif meth == "Ordinary Kriging" and not dl_only:
                p_kpts = pdict.get("Krig_Num_Points")
                if p_kpts and (p_kpts.value is None or int(p_kpts.value) < 1):
                    p_kpts.setErrorMessage("Kriging Number of Points must be >= 1 (default 12).")
            elif meth == "Spline" and not dl_only:
                p_sw = pdict.get("Spline_Weight")
                if p_sw and (p_sw.value is None or float(p_sw.value) < 0):
                    p_sw.setErrorMessage("Spline Weight must be >= 0 (default 5.0).")
                p_spts = pdict.get("Spline_Num_Points")
                if p_spts and (p_spts.value is None or int(p_spts.value) < 1):
                    p_spts.setErrorMessage("Spline Number of Points must be >= 1 (default 12).")

            p_rc_en = pdict.get("Enable_Raster_Reclass")
            if p_rc_en and bool(p_rc_en.value) and not dl_only:
                p_rc_cnt = pdict.get("Reclass_Classes_Count")
                if p_rc_cnt:
                    val = p_rc_cnt.value
                    if val is None or int(val) < 2 or int(val) > 32:
                        p_rc_cnt.setErrorMessage("Number of classes must be between 2 and 32 (default: 7).")

            p_foc = pdict.get("Focal_Smoothing")
            if p_foc and bool(p_foc.value) and not dl_only:
                p_fn = pdict.get("Focal_Neighborhood")
                if p_fn and (p_fn.value is None or int(p_fn.value) < 1):
                    p_fn.setErrorMessage("Focal Neighborhood must be >= 1 cell (default 3 = 3x3).")

            p_am = pdict.get("Add_To_Map")
            if p_am and bool(p_am.value) and not dl_only:
                p_mm = pdict.get("Map_Add_Modules")
                if p_mm and not (p_mm.valueAsText or "").strip():
                    p_mm.setErrorMessage("Add to map is ON: choose at least one element.")

            p_sch = pdict.get("Pressure_Interval_Scheme")
            _sch = p_sch.valueAsText if p_sch else ""
            if _sch == "Custom Interval":
                p_cs = pdict.get("Custom_Pressure_Step")
                _st = p_cs.value if p_cs else None
                if _st is None or float(_st) <= 0:
                    if p_cs:
                        p_cs.setErrorMessage("Custom Interval needs a step > 0 mbar (e.g. 1.0).")

            p_out = pdict.get("Output_Workspace")
            out = p_out.valueAsText if p_out else ""
            if out and not os.path.isdir(out):
                try:
                    makedirs_ok(out)
                except Exception:
                    if p_out:
                        p_out.setErrorMessage("Cannot create output folder.")
        except Exception:
            pass
        return

    # ---------------- execute ----------------
    def execute(self, parameters, messages):
        if not _HAS_ARCPY:
            raise RuntimeError("This tool must run inside ArcMap (arcpy).")
        arcpy.env.overwriteOutput = True
        log_lines = []
        warnings = []

        def msg(t):
            messages.addMessage(t)
            log_lines.append("[%s] %s" % (now_str(), t))

        def warn(t):
            warnings.append(t)
            log_lines.append("[WARN] " + t)
            if hasattr(messages, "addWarningMessage"):
                messages.addWarningMessage(t)
            elif hasattr(messages, "addWarning"):
                messages.addWarning(t)
            elif hasattr(messages, "addMessage"):
                messages.addMessage("[WARNING] " + str(t))

        t_start = time.time()
        try:
            pdict = dict((p.name, p) for p in parameters)
            p_op = pdict.get("Operation_Mode")
            op_text = p_op.valueAsText if p_op else "Download & Generate Atlas (Full Pipeline) [Default]"
            is_offline = bool(op_text and op_text.startswith("Interpolate & Map Existing Data"))

            p_dl0 = pdict.get("Download_Only")
            download_only = False if (is_offline or p_dl0 is None or p_dl0.value is None) else bool(p_dl0.value)
            if is_offline:
                p_pre_in = pdict.get("Precalculated_Point_Layers") or pdict.get("Precalculated_Point_Layer") or pdict.get("Input_Point_Features")
                in_points = p_pre_in.valueAsText if p_pre_in else None
            else:
                p_std_in = pdict.get("Input_Point_Features") or pdict.get("Input_Points")
                in_points = p_std_in.valueAsText if p_std_in else None
            mask = pdict["Study_Area_Mask"].valueAsText if (pdict.get("Study_Area_Mask") and pdict["Study_Area_Mask"].valueAsText) else None
            p_sname = pdict.get("Study_Area_Name")
            study_area_name = p_sname.valueAsText if (p_sname and p_sname.valueAsText) else ""
            out_sr_p = pdict.get("Output_Spatial_Reference") or pdict.get("Output_Coordinate_System")
            out_sr_text = out_sr_p.valueAsText if out_sr_p else None
            time_mode = (pdict.get("Time_Mode") or pdict.get("Time_Range_Mode")).valueAsText or "Single Year"
            p_sy = pdict.get("Single_Year")
            single_year = int(p_sy.value) if (p_sy and p_sy.value is not None) else 2025
            p_s = pdict.get("Start_Year")
            start_year = int(p_s.value) if (p_s and p_s.value is not None) else 2015
            p_e = pdict.get("End_Year")
            end_year = int(p_e.value) if (p_e and p_e.value is not None) else 2025
            p_sd = pdict.get("Start_Date")
            p_ed = pdict.get("End_Date")
            d_start = parse_gp_date(p_sd.value if p_sd else None)
            d_end = parse_gp_date(p_ed.value if p_ed else None)
            p_temp = pdict.get("Temporal_Resolution")
            temporal = p_temp.valueAsText if (p_temp and p_temp.valueAsText) else "Monthly"
            p_cmods = pdict.get("Climate_Modules")
            mods_text = p_cmods.valueAsText if (p_cmods and p_cmods.valueAsText) else ""
            raw_items = [m.strip().strip("'\"") for m in mods_text.split(";") if m.strip().strip("'\"")]
            modules = []
            active_submodels = []
            for item in raw_items:
                res_sub = resolve_submodel_name(item)
                if res_sub:
                    if res_sub not in active_submodels:
                        active_submodels.append(res_sub)
                    can_mod = resolve_module_canonical(item)
                    if can_mod and can_mod not in modules:
                        modules.append(can_mod)
                else:
                    can_mod = resolve_module_canonical(item) or item
                    if can_mod not in modules:
                        modules.append(can_mod)

            active_export_modules = list(modules)

            if not active_export_modules:
                raise RuntimeError("Select at least one climate module or applied model.")
            p_bc = pdict.get("Base_Cell_Size")
            base_cell = tolerance_meters(p_bc.valueAsText if (p_bc and p_bc.value) else "5000 Meters")
            if base_cell <= 0:
                base_cell = 5000.0
            p_wc = pdict.get("Wind_Factor_Cell_Size")
            wind_cell = tolerance_meters(p_wc.valueAsText if (p_wc and p_wc.value) else "25000 Meters")
            if wind_cell <= 0:
                wind_cell = 25000.0
            interp = pdict.get("Interpolation_Method").valueAsText if pdict.get("Interpolation_Method") else "IDW"
            p_ows = pdict.get("Output_Workspace")
            out_ws = p_ows.valueAsText if (p_ows and p_ows.valueAsText) else ""
            p_iso = pdict.get("Create_Isobars")
            create_isobars = bool(p_iso.value) if (p_iso and p_iso.value is not None) else False
            p_gmr = pdict.get("Generate_Monthly_Rasters")
            generate_monthly_rasters = bool(p_gmr.value) if (p_gmr and p_gmr.value is not None) else False
            p_dly = pdict.get("Save_Daily_Series")
            save_daily = bool(p_dly.value) if (p_dly and p_dly.value is not None) else False
            p_wcx = pdict.get("Extended_WC_Seasons")
            wc_extended = bool(p_wcx.value) if (p_wcx and p_wcx.value is not None) else False
            p_mr = pdict.get("Monthly_Ranges")
            monthly_ranges_on = bool(p_mr.value) if (p_mr and p_mr.value is not None) else False
            p_him = pdict.get("Extended_HI_Months")
            hi_monthly = bool(p_him.value) if (p_him and p_him.value is not None) else False
            p_pv = pdict.get("Purge_Cache")
            purge = True if (p_pv is None or p_pv.value is None) else bool(p_pv.value)
            p_am = pdict.get("Add_To_Map")
            add_to_map = False if (p_am is None or p_am.value is None) else bool(p_am.value)
            p_exp = pdict.get("Export_Shapefiles")
            export_shp = bool(p_exp.value) if (p_exp and p_exp.value is not None) else False
            p_ardb = pdict.get("Create_Arabic_Database")
            arabic_db = bool(p_ardb.value) if (p_ardb and p_ardb.value is not None) else False

            # --- Measurement Units extraction ---
            p_usys = pdict.get("Measurement_Units_System")
            unit_sys_text = p_usys.valueAsText if (p_usys and p_usys.valueAsText) else "Metric"
            p_utemp = pdict.get("Temperature_Unit")
            unit_temp_text = p_utemp.valueAsText if (p_utemp and p_utemp.valueAsText) else "Celsius (°C)"
            p_uprecip = pdict.get("Precipitation_Unit")
            unit_precip_text = p_uprecip.valueAsText if (p_uprecip and p_uprecip.valueAsText) else "Millimeters (mm)"
            p_upress = pdict.get("Pressure_Unit")
            unit_press_text = p_upress.valueAsText if (p_upress and p_upress.valueAsText) else "Hectopascals (hPa)"
            p_uwind = pdict.get("Wind_Speed_Unit")
            unit_wind_text = p_uwind.valueAsText if (p_uwind and p_uwind.valueAsText) else "Meters per second (m/s)"
            p_usol = pdict.get("Solar_Radiation_Unit")
            unit_solar_text = p_usol.valueAsText if (p_usol and p_usol.valueAsText) else "Kilowatt-hours per square meter per day (kWh/m2/day) [Default]"
            units_by_module = get_units_mapping(unit_sys_text, unit_temp_text, unit_precip_text, unit_press_text, unit_wind_text, unit_solar_text)

            p_tol = pdict.get("Point_Tolerance")
            tol_m = tolerance_meters(p_tol.valueAsText if (p_tol and p_tol.value) else None)
            p_foc = pdict.get("Focal_Smoothing")
            focal_on = bool(p_foc.value) if (p_foc and p_foc.value is not None) else False
            p_fstat = pdict.get("Focal_Statistic")
            focal_stat = p_fstat.valueAsText if (p_fstat and p_fstat.valueAsText) else "MEAN"
            p_fn = pdict.get("Focal_Neighborhood")
            focal_n = int(p_fn.value) if (p_fn and p_fn.value is not None) else 3
            focal = {"apply": focal_on, "stat": focal_stat, "size": max(1, focal_n)}
            p_rc_en = pdict.get("Enable_Raster_Reclass")
            reclass_enabled = bool(p_rc_en.value) if (p_rc_en and p_rc_en.value is not None) else False
            p_rc_cnt = pdict.get("Reclass_Classes_Count")
            reclass_nclass = int(p_rc_cnt.value) if (p_rc_cnt and p_rc_cnt.value is not None) else 7
            p_rc_meth = pdict.get("Reclass_Method")
            reclass_method = p_rc_meth.valueAsText if (p_rc_meth and p_rc_meth.valueAsText) else "Natural Breaks (Jenks)"
            reclass_opts = {
                "enable": reclass_enabled,
                "nclass": max(2, min(32, reclass_nclass)),
                "method": reclass_method
            }
            provider = pdict.get("Climate_Data_Source").valueAsText if pdict.get("Climate_Data_Source") else "NASA POWER API"
            use_om = bool(provider.startswith("Open-Meteo") or "ERA5" in provider or "Hybrid" in provider or "Copernicus" in provider or "CDS" in provider)
            p_cds_k = pdict.get("CDS_API_Key")
            cds_key = p_cds_k.valueAsText if (p_cds_k and p_cds_k.valueAsText) else None
            p_om_m = pdict.get("OpenMeteo_Model")
            om_model = p_om_m.valueAsText if (p_om_m and p_om_m.valueAsText) else "ERA5-Land (Highest Resolution ~9 km / 0.1 deg) [Recommended]"
            om_slug = om_model_slug(om_model)
            p_gf = pdict.get("Gap_Fill_Method")
            _gap_txt = p_gf.valueAsText if (p_gf and p_gf.valueAsText) else "Climatological Month Mean (Recommended)"
            if _gap_txt.startswith("Linear"):
                gap_method = "linear"
            elif _gap_txt.startswith("No Fill"):
                gap_method = "none"
            elif _gap_txt.startswith("Spatial"):
                gap_method = "spatial"
            else:
                gap_method = "climatological"

            # --- Field Filtering Setup ---
            p_scope = pdict.get("Field_Filter_Scope")
            filter_scope = p_scope.valueAsText if p_scope else "All Variables & Fields (Full Suite) [Recommended]"
            p_aggs = pdict.get("Included_Aggregations")
            aggs_txt = p_aggs.valueAsText if p_aggs else ""
            filter_aggs = [a.strip().strip("'\"") for a in aggs_txt.split(";") if a.strip().strip("'\"")] if aggs_txt else None
            p_seas = pdict.get("Included_Seasons")
            seas_txt = p_seas.valueAsText if p_seas else ""
            filter_seasons = [s.strip().strip("'\"") for s in seas_txt.split(";") if s.strip().strip("'\"")] if seas_txt else None
            p_flds = pdict.get("Selected_Fields")
            filter_custom_flds = p_flds.valueAsText if p_flds else None
            p_tscope = pdict.get("Temporal_Scope")
            filter_tscope = p_tscope.valueAsText if p_tscope else None
            t_scope_set = parse_temporal_scope(filter_tscope)

            p_wf_p = pdict.get("Execution_Workflow_Mode")
            wf_mode_text = p_wf_p.valueAsText if p_wf_p else "Batch Mode: Download All Then Process [Recommended]"
            is_sequential = bool(wf_mode_text and "Sequential" in wf_mode_text)
            is_batch = not is_sequential

            wanted_fields_by_module = resolve_filtered_fields(
                active_export_modules, filter_scope, filter_aggs, filter_seasons, filter_custom_flds, temporal_scope=filter_tscope
            )
            # Opt-in extended WC seasons: default OFF keeps the clean 2-field
            # schema (Winter + Annual). Stripped here so GDB fields, Excel,
            # rasters and dictionaries all stay byte-identical to legacy runs.
            WC_EXTENDED_FIELDS = ("WC_Spring_Mean", "WC_Summer_Mean", "WC_Autumn_Mean",
                                    "WC_Annual_Range",
                                    "WC_January_Mean", "WC_February_Mean", "WC_March_Mean",
                                    "WC_April_Mean", "WC_May_Mean", "WC_June_Mean",
                                    "WC_July_Mean", "WC_August_Mean", "WC_September_Mean",
                                    "WC_October_Mean", "WC_November_Mean", "WC_December_Mean")
            if not wc_extended:
                for _m, _fl in list(wanted_fields_by_module.items()):
                    wanted_fields_by_module[_m] = [f for f in _fl if f not in WC_EXTENDED_FIELDS]
            else:
                msg("Extended Wind Chill full suite ENABLED (cold regions): seasonal/range/monthly means will be published.")
            # Opt-in interannual monthly ranges (independent toggle, default OFF).
            # Stripped here so default runs stay byte-identical across GDB/Excel/rasters.
            if not monthly_ranges_on:
                for _m, _fl in list(wanted_fields_by_module.items()):
                    wanted_fields_by_module[_m] = [
                        f for f in _fl
                        if not (len(f) > 7 and f.endswith("_Range") and any(
                            f.endswith("_%s_Range" % _mn) for _mn in MONTH_NAMES_EN))]
            else:
                msg("Monthly Ranges ENABLED: interannual per-month ranges will be published.")
            # Opt-in monthly Heat Index suite (independent toggle, default OFF).
            # Stripped here so default runs stay byte-identical across GDB/Excel/rasters.
            HI_MONTHLY_FIELDS = ("HI_January_Mean", "HI_February_Mean", "HI_March_Mean",
                                 "HI_April_Mean", "HI_May_Mean", "HI_June_Mean",
                                 "HI_July_Mean", "HI_August_Mean", "HI_September_Mean",
                                 "HI_October_Mean", "HI_November_Mean", "HI_December_Mean")
            if not hi_monthly:
                for _m, _fl in list(wanted_fields_by_module.items()):
                    wanted_fields_by_module[_m] = [f for f in _fl if f not in HI_MONTHLY_FIELDS]
            else:
                msg("Extended Heat Index monthly suite ENABLED: 12 monthly Rothfusz means will be published.")

            total_wanted_fields = sum(len(flist) for flist in wanted_fields_by_module.values())
            msg("Workflow Pipeline Mode: %s" % ("SEQUENTIAL (Element by Element)" if is_sequential else "BATCH (Download All Then Process)"))
            msg("Field Filtering: Scope='%s' | Temporal Scope=%s | Total Active Indicators=%d." % (
                filter_scope, ", ".join(sorted(t_scope_set)), total_wanted_fields))
            for m in active_export_modules:
                msg("  Module '%s': %d indicators (%s)" % (
                    m, len(wanted_fields_by_module.get(m, [])),
                    ", ".join(wanted_fields_by_module.get(m, []))
                ))
            if total_wanted_fields == 0:
                raise RuntimeError("No climate fields match the selected filter criteria.")

            # --- interpolation advanced options (active algorithm only) ---
            p_pow = pdict.get("IDW_Power")
            p_st = pdict.get("IDW_Search_Type")
            p_npts = pdict.get("IDW_Num_Points")
            p_md = pdict.get("IDW_Max_Distance")
            p_sp_type = pdict.get("Spline_Type")
            p_sp_weight = pdict.get("Spline_Weight")
            p_sp_pts = pdict.get("Spline_Num_Points")
            iopts = {
                "power": float(p_pow.value) if (p_pow and p_pow.value is not None) else 1.2,
                "search": p_st.valueAsText if (p_st and p_st.valueAsText) else "Variable",
                "npoints": int(p_npts.value) if (p_npts and p_npts.value is not None) else 12,
                "maxdist": (float(p_md.value) if (p_md and p_md.value is not None) else None),
                "spline_type": (p_sp_type.valueAsText if p_sp_type and p_sp_type.valueAsText else "Tension"),
                "spline_weight": (float(p_sp_weight.value) if p_sp_weight and p_sp_weight.value is not None else 5.0),
                "spline_npoints": (int(p_sp_pts.value) if p_sp_pts and p_sp_pts.value is not None else 12),
            }
            p_km = pdict.get("Krig_Model")
            p_kt = pdict.get("Krig_Type")
            p_kp = pdict.get("Krig_Num_Points")
            kopts = {
                "model": (p_km.valueAsText if p_km and p_km.valueAsText else "Spherical"),
                "ktype": (p_kt.valueAsText if p_kt and p_kt.valueAsText else "Ordinary"),
                "npoints": (int(p_kp.value) if p_kp and p_kp.value is not None else 12),
            }

            col_data_start = "2024"
            col_data_end = "2024"

            if is_offline:
                years = [2024]
                y0, y1 = 2000, 2024
                start_date_str, end_date_str = None, None
                time_tag = "Offline"
                period_label = "Precalculated Data (Offline Mode)"
                col_data_start = "Precalculated"
                col_data_end = "Precalculated"
                try:
                    l_paths = [lp.strip().strip("'\"") for lp in (in_points or "").split(";") if lp.strip().strip("'\"")]
                    found_dates = False
                    for test_lyr in l_paths:
                        try:
                            f_names = [f.name for f in arcpy.ListFields(test_lyr)]
                            if "Data_Start" in f_names and "Data_End" in f_names:
                                with arcpy.da.SearchCursor(test_lyr, ["Data_Start", "Data_End"]) as cur:
                                    for row in cur:
                                        if row[0] is not None and row[1] is not None and str(row[0]).strip() and str(row[1]).strip():
                                            col_data_start = str(row[0]).strip()
                                            col_data_end = str(row[1]).strip()
                                            import re
                                            m0 = re.search(r'\b(19\d\d|20\d\d)\b', col_data_start)
                                            m1 = re.search(r'\b(19\d\d|20\d\d)\b', col_data_end)
                                            if m0 and m1:
                                                y0, y1 = int(m0.group(1)), int(m1.group(1))
                                                years = list(range(min(y0, y1), max(y0, y1) + 1))
                                                if y0 == y1:
                                                    time_tag = "%d" % y0
                                                    period_label = "%d (Precalculated)" % y0
                                                else:
                                                    time_tag = "From_%d_To_%d" % (min(y0, y1), max(y0, y1))
                                                    period_label = "%d-%d (Precalculated)" % (min(y0, y1), max(y0, y1))
                                            else:
                                                time_tag = "Offline"
                                                period_label = "%s-%s (Precalculated)" % (col_data_start, col_data_end)
                                            found_dates = True
                                            break
                            if found_dates:
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
            elif time_mode == "Single Year":
                years = [single_year]
                y0, y1 = single_year, single_year
                start_date_str = "%04d-01-01" % single_year
                end_date_str = "%04d-12-31" % single_year
                time_tag = "%d" % single_year
                period_label = "%d (Single Year)" % single_year
                col_data_start = str(single_year)
                col_data_end = str(single_year)
            elif time_mode == "Year Range":
                years = list(range(start_year, end_year + 1))
                y0, y1 = years[0], years[-1]
                start_date_str = "%04d-01-01" % start_year
                end_date_str = "%04d-12-31" % end_year
                time_tag = "From_%d_To_%d" % (start_year, end_year)
                period_label = "%d-%d (%d yrs)" % (start_year, end_year, len(years))
                col_data_start = str(start_year)
                col_data_end = str(end_year)
            else:
                if not d_start:
                    d_start = _dt.date(2024, 1, 1)
                if not d_end:
                    d_end = _dt.date(2024, 12, 31)
                if d_start > d_end:
                    d_start, d_end = d_end, d_start
                y0, y1 = d_start.year, d_end.year
                years = list(range(y0, y1 + 1))
                start_date_str = "%04d-%02d-%02d" % (d_start.year, d_start.month, d_start.day)
                end_date_str = "%04d-%02d-%02d" % (d_end.year, d_end.month, d_end.day)
                time_tag = "From_%04d%02d%02d_To_%04d%02d%02d" % (
                    d_start.year, d_start.month, d_start.day,
                    d_end.year, d_end.month, d_end.day)
                s_txt = p_sd.valueAsText if (p_sd and p_sd.value) else ("%02d/%02d/%04d" % (d_start.day, d_start.month, d_start.year))
                e_txt = p_ed.valueAsText if (p_ed and p_ed.value) else ("%02d/%02d/%04d" % (d_end.day, d_end.month, d_end.year))
                period_label = "%s to %s (Custom Date Range)" % (s_txt, e_txt)
                col_data_start = str(s_txt)
                col_data_end = str(e_txt)

            # --- Monthly climatology gate: 12-month means are climatologically
            # meaningful only for multi-year spans (>= 2 years). A single year
            # (or < 2 years) keeps the flag OFF with a warning.
            try:
                _span_yrs = int(y1) - int(y0) + 1
            except Exception:
                _span_yrs = 1
            monthly_enabled = bool(generate_monthly_rasters) and _span_yrs >= 2
            if generate_monthly_rasters and not monthly_enabled:
                warn("Monthly climatology rasters skipped: the selected period spans %d year(s); "
                     "at least 2 years are required for monthly means (Jan-Dec)." % _span_yrs)
            elif monthly_enabled:
                msg("Monthly climatology rasters: ENABLED (12 Month/ surfaces per element, unified stretch).")

            msg("=" * 70)
            msg("MIRSAD: Spatial Climate Atlas Generator v%s (منظومة مِرصاد)" % TOOL_VERSION)
            msg("Multi-source Integrated Reanalysis & Surface Atlas Database Platform")
            msg("=" * 70)
            if download_only:
                msg("Mode: DOWNLOAD & SAVE POINT DATA ONLY (points + tables, skipping rasters and atlas).")
            msg("Data source: %s" % provider)
            if use_om:
                msg("Atmospheric Model: %s [API code: %s]" % (om_model, om_slug))
            else:
                msg("NASA POWER Model: MERRA-2 (~50 km / 0.5 deg) & CERES SYN1deg (~100 km / 1.0 deg) via AG community")
            msg("Modules: %s%s | Period: %s | Temporal: %s | Interp: %s"
                % (", ".join(modules) if modules else "None",
                   (" | Submodels: " + ", ".join(SUBMODEL_DEPS[s]["short"] for s in active_submodels)) if active_submodels else "",
                   period_label, temporal, interp))
            if interp == "IDW":
                msg("IDW settings: power=%.2f, search=%s, points=%d%s" % (
                    iopts["power"], iopts["search"], iopts["npoints"],
                    (", maxdist=%.0fm" % iopts["maxdist"]) if iopts["maxdist"] else ""))
            elif interp == "Ordinary Kriging":
                msg("Kriging settings: model=%s, type=%s, points=%d" % (
                    kopts["model"], kopts["ktype"], kopts["npoints"]))
            elif interp == "Spline":
                msg("Spline settings: type=%s, weight=%.2f, points=%d" % (
                    iopts["spline_type"], iopts["spline_weight"], iopts["spline_npoints"]))

            in_point_list = [lp.strip().strip("'\"") for lp in (in_points or "").split(";") if lp.strip().strip("'\"")]
            if not in_point_list:
                raise RuntimeError("No input point features or precalculated point layers were specified.")
            primary_in_point = in_point_list[0]
            in_desc = arcpy.Describe(primary_in_point)
            if out_sr_text:
                try:
                    out_sr = arcpy.SpatialReference()
                    out_sr.loadFromString(out_sr_text)
                except Exception:
                    try:
                        p_sr = pdict.get("Output_Spatial_Reference")
                        out_sr = arcpy.Describe(p_sr.value).spatialReference if p_sr else in_desc.spatialReference
                    except Exception:
                        out_sr = in_desc.spatialReference
            else:
                out_sr = in_desc.spatialReference
            is_geo = getattr(out_sr, "type", "") == "Geographic"
            eff_base = base_cell / 111320.0 if (is_geo and base_cell > 1.0) else base_cell
            eff_wind = wind_cell / 111320.0 if (is_geo and wind_cell > 1.0) else wind_cell
            if is_geo and (base_cell > 1.0 or wind_cell > 1.0):
                warn("Geographic output SR: cell sizes treated as metres and converted to degrees "
                     "(base=%.5f deg, wind=%.5f deg)." % (eff_base, eff_wind))
            msg("Output SR: %s (%s)" % (out_sr.name, getattr(out_sr, "type", "?")))

            if is_offline:
                gdb_name = "Climate_Atlas_Offline_%s.gdb" % time_tag
            else:
                gdb_name = "Climate_Database_%s.gdb" % time_tag
            gdb_path, paths = self._build_layout(out_ws, active_export_modules, gdb_name=gdb_name, export_shp=export_shp)
            msg("Workspace: %s (GDB: %s)" % (out_ws, gdb_name))

            # -------------------------------------------------------------
            # Archive Study Area Mask Boundary & Grid Points into Project GDB
            # -------------------------------------------------------------
            s_name = (study_area_name or "").strip()
            if not s_name and mask:
                try:
                    s_name = os.path.splitext(os.path.basename(mask))[0]
                except Exception:
                    s_name = "Study_Area"
            if not s_name:
                s_name = "Study_Area"

            import re
            clean_sname = re.sub(r'[^a-zA-Z0-9_]', '_', s_name).strip('_')
            if not clean_sname:
                clean_sname = "Study_Area"

            # 1. Archive Mask Boundary Layer inside GDB
            if mask and arcpy.Exists(mask):
                bnd_fc_name = arcpy.ValidateTableName("%s_Boundary" % clean_sname, gdb_path)
                bnd_out_path = os.path.join(gdb_path, bnd_fc_name)
                try:
                    m_abs = os.path.abspath(str(mask)).lower()
                    b_abs = os.path.abspath(str(bnd_out_path)).lower()
                    if m_abs != b_abs:
                        if not arcpy.Exists(bnd_out_path):
                            arcpy.management.CopyFeatures(mask, bnd_out_path)
                            msg("Archived Study Area Mask boundary into GDB: %s" % bnd_fc_name)
                        else:
                            msg("Study Area Mask boundary already exists in GDB: %s" % bnd_fc_name)
                    else:
                        msg("Study Area Mask boundary already resides in GDB: %s" % bnd_fc_name)
                except Exception as ex_bnd:
                    warn("Could not archive Study Area Mask boundary into GDB: %s" % ex_bnd)

            # 2. Archive Primary Input Sampling Grid Points inside GDB
            if primary_in_point and arcpy.Exists(primary_in_point):
                pts_fc_name = arcpy.ValidateTableName("%s_Grid_Points" % clean_sname, gdb_path)
                pts_out_path = os.path.join(gdb_path, pts_fc_name)
                try:
                    p_abs = os.path.abspath(str(primary_in_point)).lower()
                    pt_abs = os.path.abspath(str(pts_out_path)).lower()
                    if p_abs != pt_abs:
                        if not arcpy.Exists(pts_out_path):
                            arcpy.management.CopyFeatures(primary_in_point, pts_out_path)
                            msg("Archived Input Sampling Grid Points into GDB: %s" % pts_fc_name)
                        else:
                            msg("Input Sampling Grid Points already exist in GDB: %s" % pts_fc_name)
                    else:
                        msg("Input Sampling Grid Points already reside in GDB: %s" % pts_fc_name)
                except Exception as ex_pts:
                    warn("Could not archive Input Sampling Grid Points into GDB: %s" % ex_pts)

            wgs = arcpy.SpatialReference(4326)
            scratch_dir = os.path.join(out_ws, "_scratch")
            makedirs_ok(scratch_dir)
            # Keep the original mask path: per-element scratch purges must never
            # delete the reprojected mask, and if it ever goes missing it is
            # rebuilt from the original via ensure_mask_fc().
            mask_orig = mask
            maskp = None
            mask_required = bool(mask_orig)
            if mask:
                # Reproject the mask once into the output SR so mask, extent,
                # snap and cell size all share one unit system.
                try:
                    maskp = os.path.join(scratch_dir, "maskp.shp")
                    try:
                        if arcpy.Exists(maskp):
                            arcpy.management.Delete(maskp)
                    except Exception:
                        pass
                    arcpy.management.Project(mask, maskp, out_sr)
                    mask = maskp
                    msg("Mask reprojected to output SR.")
                except Exception as ex:
                    warn("Mask reprojection failed (%s); using mask as-is." % ex)

            # NOTE: DO NOT set arcpy.env.mask = mask here!
            # Doing so would prematurely clip input points and restrict intermediate tools.
            # Masking must be applied ONLY after surface interpolation via ExtractByMask.
            arcpy.ClearEnvironment("mask")
            arcpy.ClearEnvironment("extent")
            arcpy.env.outputCoordinateSystem = out_sr

            # --- PRE-RASTERIZE MASK: raster-on-raster ExtractByMask is 10-50x faster ---
            raster_mask = None
            if mask and arcpy.Exists(mask):
                try:
                    _rmask_path = os.path.join(scratch_dir, "mask_raster.tif")
                    if arcpy.Exists(_rmask_path):
                        try:
                            arcpy.management.Delete(_rmask_path)
                        except Exception:
                            pass
                    # Rasterize: polygon -> 1/NoData raster at target cell size
                    arcpy.env.extent = mask
                    arcpy.env.cellSize = eff_base
                    arcpy.conversion.PolygonToRaster(
                        mask, arcpy.Describe(mask).OIDFieldName,
                        _rmask_path, "CELL_CENTER", "NONE", eff_base)
                    if arcpy.Exists(_rmask_path):
                        raster_mask = _rmask_path
                        msg("Vector mask pre-rasterized to %s (fast raster masking enabled)." % _rmask_path)
                    else:
                        msg("Pre-rasterization did not produce output; will use vector mask (slower).")
                except Exception as ex_rmask:
                    warn("Mask pre-rasterization failed (%s); will use vector mask (slower)." % ex_rmask)
                finally:
                    arcpy.ClearEnvironment("extent")
            arcpy.env.cellSize = eff_base
            # --- guard: refuse rasters that would exhaust 32-bit ArcMap ---
            try:
                _desc_target = arcpy.Describe(mask) if (mask and arcpy.Exists(mask)) else arcpy.Describe(in_points)
                _ext = _desc_target.extent
                _w = float(_ext.XMax - _ext.XMin)
                _h = float(_ext.YMax - _ext.YMin)
                if _w > 0 and _h > 0 and eff_base > 0:
                    _cells = (_w / eff_base) * (_h / eff_base)
                    if _cells > 50000000:
                        _unit_lbl = "degrees" if is_geo else "metres"
                        _err_msg = (
                            "Cell size %.4g %s produces approximately %.1f million cells (safety limit: 50 million). "
                            "This would exhaust system memory and cause an unrecoverable freeze. "
                            "Please increase the Base Cell Size parameter and re-run." % (
                                base_cell, _unit_lbl, _cells / 1000000.0))
                        arcpy.AddError(_err_msg)
                        raise RuntimeError(_err_msg)
            except RuntimeError:
                raise
            except Exception:
                pass
            # --- ArcMap 10.x & CopyRaster deadlock guard: explicitly disable parallel processing ---
            # In 32-bit ArcMap, parallelProcessingFactor != 0 causes CopyRaster and Spatial Analyst
            # tools to deadlock indefinitely (BUG-000129060). Setting "0" enforces single-process.
            try:
                arcpy.env.parallelProcessingFactor = "0"
            except Exception:
                pass
            # --- mandatory maximum LZW block compression on all output rasters + dedicated scratch ---
            try:
                arcpy.env.compression = "LZW"
                arcpy.env.tileSize = "128 128"
                arcpy.env.pyramid = "NONE"
                arcpy.env.rasterStatistics = "STATISTICS 1 1"
            except Exception:
                pass
            try:
                arcpy.env.scratchWorkspace = scratch_dir
            except Exception:
                pass
            msg("Maximum LZW block compression (128x128 tiles, no internal pyramid overhead) enforced | purge cache: %s" % purge)

            if interp == "IDW":
                interp_label = "IDW(p=%.2f,%s,n=%d%s)" % (
                    iopts["power"], iopts["search"], iopts["npoints"],
                    (",d=%.0f" % iopts["maxdist"]) if iopts["maxdist"] else "")
            elif interp == "Ordinary Kriging":
                interp_label = "Kriging(%s,%s,n=%d)" % (
                    kopts["model"], kopts["ktype"], kopts["npoints"])
            elif interp == "Spline":
                interp_label = "Spline(%s,w=%.2f,n=%d)" % (
                    iopts["spline_type"], iopts["spline_weight"], iopts["spline_npoints"])
            else:
                interp_label = interp
            if focal["apply"]:
                interp_label += "+Focal(%s,%dx%d)" % (focal["stat"], focal["size"], focal["size"])
                msg("Focal smoothing: %s %dx%d (smoothed raster replaces output)."
                    % (focal["stat"], focal["size"], focal["size"]))

            # Determine ordered modules to enforce foundational hierarchy:
            HIERARCHY = list(ALL_CANONICAL_MODULES)
            ordered_modules = [m for m in HIERARCHY if m in active_export_modules]
            for m in active_export_modules:
                if m not in ordered_modules:
                    ordered_modules.append(m)

            admin_meta = {
                "y0": y0, "y1": y1, "temporal": temporal, "interp": interp_label,
                "base_cell": base_cell, "wind_cell": wind_cell,
                "data_start": col_data_start, "data_end": col_data_end,
                "units_by_module": units_by_module,
                "unit_sys": unit_sys_text, "unit_temp": unit_temp_text,
                "unit_precip": unit_precip_text, "unit_press": unit_press_text,
                "unit_wind": unit_wind_text, "unit_solar": unit_solar_text,
                "provider": provider, "om_model": om_model, "om_slug": om_slug,
                "gap_method": gap_method, "gap_txt": _gap_txt
            }
            self._admin_meta = admin_meta
            element_fcs = {}
            raster_registry = []
            sa_avail = False
            if not download_only:
                try:
                    if not hasattr(arcpy, "mp"):
                        arcpy.CheckOutExtension("Spatial")
                    sa_avail = True
                except Exception:
                    sa_avail = False
                    warn("Spatial Analyst unavailable: raster interpolation skipped.")


            if is_offline:
                msg("Offline Mode: merging precalculated point layer(s) ...")
                results = []
                element_fcs = self._merge_offline_layers(
                    in_points, gdb_path, out_sr, modules, active_submodels,
                    wanted_fields_by_module, msg, warn, admin_meta=admin_meta)
                if not element_fcs:
                    raise RuntimeError("No element point layers were built from precalculated inputs.")

                for mi, m in enumerate(ordered_modules):
                    fc = element_fcs.get(m)
                    if not fc or not arcpy.Exists(fc):
                        continue
                    short = MODULE_SHORT.get(m, m)
                    if export_shp:
                        self._export_shapefile(fc, os.path.join(paths["shp"], short + ".shp"), msg, warn)
                    self._export_excel(fc, os.path.join(paths["vec"], short + ".xls"), msg, warn, module_name=m)
                    if not download_only and sa_avail:
                        if mask_required:
                            mask = ensure_mask_fc(mask, mask_orig, maskp, out_sr, msg, warn)
                            if not mask:
                                warn("Element '%s': mask unavailable, rasters skipped "
                                     "(no unclipped output published)." % m)
                                msg(">>> Element [%d/%d] %s: Layer & exports ready (rasters skipped). <<<\n"
                                    % (mi + 1, len(ordered_modules), m))
                                continue
                        elem_rasters = self._interpolate_all(
                            None, [m], paths, eff_base, interp, mask, msg, warn,
                            iopts, kopts, is_geo, purge, scratch_dir, focal,
                            {m: fc}, wanted_fields_by_module=wanted_fields_by_module,
                            reclass_opts=reclass_opts,
                            raster_mask=raster_mask,
                            monthly_enabled=monthly_enabled,
                            monthly_ranges_on=monthly_ranges_on)
                        raster_registry.extend(elem_rasters)
                        if purge and os.path.exists(scratch_dir):
                            for sf in os.listdir(scratch_dir):
                                sfp = os.path.join(scratch_dir, sf)
                                try:
                                    # NEVER delete the reprojected mask: it is
                                    # reused by every element + wind vectors.
                                    if os.path.isfile(sfp) and not sf.lower().startswith(("maskp.", "mask_raster")):
                                        os.remove(sfp)
                                except Exception:
                                    pass
                        gc.collect()
                    msg(">>> Element [%d/%d] %s: Layer, exports & rasters ready. <<<\n" % (mi + 1, len(ordered_modules), m))
            else:
                msg("Extracting WGS84 coordinates ...")
                pts = self._extract_points(in_points, wgs, messages)
                msg("Input points: %d" % len(pts))
                if not pts:
                    raise RuntimeError(
                        "No points found in '%s' (empty layer, empty selection, or "
                        "definition query filtering everything out)." % in_points)
                if tol_m > 0:
                    if not is_geo and tol_m > eff_base:
                        warn("Point Tolerance (%.0f m) exceeds Base Cell Size (%.0f m): "
                             "thinning may leave gaps; consider a smaller tolerance."
                             % (tol_m, eff_base))
                    if is_geo and tol_m / 111320.0 > eff_base:
                        warn("Point Tolerance exceeds Base Cell Size: "
                             "thinning may leave gaps; consider a smaller tolerance.")
                    kept, dropped = thin_points_tolerance(pts, tol_m)
                    msg("Tolerance %.0f m: %d kept, %d merged %s" % (
                        tol_m, len(kept), len(dropped),
                        ("(OIDs %s)" % dropped[:20]) if dropped else ""))
                    pts = kept
                    if not pts:
                        raise RuntimeError("Tolerance removed all points.")

                msg("Checking server connectivity (one probe request) ...")
                try:
                    probe_server(provider, pts[0]["lat"], pts[0]["lon"], y0, len(pts),
                                 model=om_slug, start_date=start_date_str, end_date=end_date_str)
                    msg("Server connectivity OK (%s)." % provider)
                except RuntimeError as ex:
                    messages.addErrorMessage(str(ex))
                    raise

                # Project base points once for all elements
                tmp_base = safe_project_fc(in_points, out_sr, gdb_path, "baseproj", warn)
                tmp_base_is_temp = (tmp_base != in_points)

                results = [dict(p, parameter={}, monthly={}, daily_raw={}, fields={}, status="PENDING", error="") for p in pts]
                nasa_cache = {}
                sess = None
                if _HAS_REQUESTS:
                    try:
                        sess = requests.Session()
                    except Exception:
                        sess = None

                if use_om:
                    om_daily_all, om_hourly_all, _om_drop, _om_note = om_probe_vars(
                        ordered_modules, model=om_slug, start_date=start_date_str, end_date=end_date_str)
                    if _om_note:
                        warn(_om_note)

                module_timings = {}
                raster_timings = {}
                overall_start_dt = now_str()

                try:
                    for mi, m in enumerate(ordered_modules):
                        t_mod_start = time.time()
                        mod_start_clock = now_str().split(" ")[1]
                        msg("\n" + "=" * 65)
                        msg(">>> ELEMENT [%d/%d]: %s <<<" % (mi + 1, len(ordered_modules), m))
                        msg("  -> Module Processing Started: %s" % mod_start_clock)
                        msg("=" * 65)

                        # Determine raw parameters needed for this element
                        if m == "Climate_Models":
                            needed_m = []
                            for s in active_submodels:
                                for p in SUBMODEL_DEPS[s].get("params", []):
                                    if p not in needed_m:
                                        needed_m.append(p)
                        else:
                            needed_m = list(MODULE_PARAMS.get(m, []))

                        t_dl_start = time.time()

                        # Check if any station needs querying
                        if use_om:
                            # For Open-Meteo, get required variables for this module
                            m_d_vars, m_h_vars = om_var_sets([m])
                            m_d_vars = [v for v in m_d_vars if v in om_daily_all]
                            m_h_vars = [v for v in m_h_vars if v in om_hourly_all]

                            pts_to_fetch = []
                            for idx, p in enumerate(pts):
                                curr_m = results[idx].get("monthly", {})
                                missing = any(v not in curr_m for v in m_d_vars) or any(v not in curr_m for v in m_h_vars)
                                if missing:
                                    pts_to_fetch.append((idx, p))

                            if pts_to_fetch:
                                prov_title = "Copernicus CDS / ERA5" if ("Copernicus" in provider or "CDS" in provider) else "Open-Meteo"
                                msg("Element [%d/%d] %s: Querying %s (%s) sequentially (%d station(s)) ..."
                                    % (mi + 1, len(ordered_modules), m, prov_title, om_slug, len(pts_to_fetch)))
                                arcpy.SetProgressor("step", "Querying %s for %s..." % (prov_title, m), 0, len(pts_to_fetch), 1)
                                for step_i, (idx, p) in enumerate(pts_to_fetch):
                                    pct = float(step_i + 1) / float(len(pts_to_fetch)) * 100.0
                                    msg("  [%s] Station %d/%d (%.0f%%) [OID %s | Lat: %.4f, Lon: %.4f] - Fetching..." %
                                        (m, step_i + 1, len(pts_to_fetch), pct, p.get("oid", idx + 1), p["lat"], p["lon"]))
                                    try:
                                        monthly, daily_raw, _drop = fetch_openmeteo_point(
                                            p["lat"], p["lon"], y0, y1, [m],
                                            daily_vars=m_d_vars, hourly_vars=m_h_vars,
                                            model=om_slug, start_date=start_date_str, end_date=end_date_str)
                                        results[idx].setdefault("monthly", {}).update(monthly)
                                        if temporal == "Daily":
                                            results[idx].setdefault("daily_raw", {}).update(daily_raw)
                                        results[idx]["status"] = "OK"
                                    except Exception as ex:
                                        results[idx]["error"] = str(ex)[:500]
                                        results[idx]["status"] = "FAILED"
                                    arcpy.SetProgressorPosition(step_i + 1)
                                arcpy.ResetProgressor()

                                # --- Automatic Rescue Pass for Open-Meteo ---
                                failed_om = [idx for (idx, p) in pts_to_fetch if results[idx].get("status") == "FAILED"]
                                if failed_om:
                                    msg("  [RESCUE PASS] Retrying %d transiently failed station(s) for %s with extended timeout..."
                                        % (len(failed_om), m))
                                    time.sleep(3.0)
                                    for r_i, idx in enumerate(failed_om):
                                        p = pts[idx]
                                        try:
                                            monthly, daily_raw, _drop = fetch_openmeteo_point(
                                                p["lat"], p["lon"], y0, y1, [m],
                                                daily_vars=m_d_vars, hourly_vars=m_h_vars,
                                                model=om_slug, timeout=90, retries=4,
                                                start_date=start_date_str, end_date=end_date_str)
                                            results[idx].setdefault("monthly", {}).update(monthly)
                                            if temporal == "Daily":
                                                results[idx].setdefault("daily_raw", {}).update(daily_raw)
                                            results[idx]["status"] = "OK"
                                            results[idx]["error"] = ""
                                            msg("    -> [RESCUED %d/%d] Station OID %s recovered successfully!"
                                                % (r_i + 1, len(failed_om), p.get("oid", idx + 1)))
                                        except Exception as ex_r:
                                            results[idx]["error"] = str(ex_r)[:500]
                                            results[idx]["status"] = "FAILED"
                                            warn("    -> [STILL FAILED] Station OID %s: %s"
                                                 % (p.get("oid", idx + 1), str(ex_r)[:150]))
                            else:
                                msg("Element [%d/%d] %s: All required variables already cached in memory. Reusing with 0 queries."
                                    % (mi + 1, len(ordered_modules), m))

                        else:
                            # NASA POWER: check if missing any params
                            pts_to_fetch = []
                            for idx, p in enumerate(pts):
                                curr_par = results[idx].get("parameter", {})
                                missing_p = [pname for pname in needed_m if pname not in curr_par]
                                if missing_p:
                                    pts_to_fetch.append((idx, p, missing_p))

                            if pts_to_fetch:
                                msg("Element [%d/%d] %s: Querying NASA POWER sequentially (%d station(s), params: %s) ..."
                                    % (mi + 1, len(ordered_modules), m, len(pts_to_fetch), ", ".join(needed_m)))
                                arcpy.SetProgressor("step", "Querying NASA POWER for %s..." % m, 0, len(pts_to_fetch), 1)
                                for step_i, (idx, p, missing_p) in enumerate(pts_to_fetch):
                                    pct = float(step_i + 1) / float(len(pts_to_fetch)) * 100.0
                                    msg("  [%s] Station %d/%d (%.0f%%) [OID %s | Lat: %.4f, Lon: %.4f] - Querying %s..." %
                                        (m, step_i + 1, len(pts_to_fetch), pct, p.get("oid", idx + 1), p["lat"], p["lon"], ",".join(missing_p)))
                                    key = (round(p["lat"], 4), round(p["lon"], 4), y0, y1, temporal, start_date_str, end_date_str, tuple(sorted(missing_p)))
                                    if key in nasa_cache:
                                        results[idx].setdefault("parameter", {}).update(nasa_cache[key])
                                        results[idx]["status"] = "OK"
                                    else:
                                        try:
                                            par = fetch_nasa_point(
                                                p["lat"], p["lon"], y0, y1, missing_p,
                                                temporal=temporal, session=sess,
                                                start_date=start_date_str, end_date=end_date_str)
                                            nasa_cache[key] = par
                                            results[idx].setdefault("parameter", {}).update(par)
                                            results[idx]["status"] = "OK"
                                        except Exception as ex:
                                            results[idx]["error"] = str(ex)[:500]
                                            results[idx]["status"] = "FAILED"
                                    arcpy.SetProgressorPosition(step_i + 1)
                                arcpy.ResetProgressor()

                                # --- Automatic Rescue Pass for NASA POWER ---
                                failed_nasa = []
                                for (idx, p, missing_p) in pts_to_fetch:
                                    curr_par = results[idx].get("parameter", {})
                                    unresolved = [pname for pname in missing_p if pname not in curr_par]
                                    if unresolved or results[idx].get("status") == "FAILED":
                                        failed_nasa.append((idx, p, unresolved if unresolved else missing_p))

                                if failed_nasa:
                                    msg("  [RESCUE PASS] Retrying %d transiently failed station(s) for %s with extended timeout..."
                                        % (len(failed_nasa), m))
                                    time.sleep(3.0)
                                    for r_i, (idx, p, missing_p) in enumerate(failed_nasa):
                                        try:
                                            par = fetch_nasa_point(
                                                p["lat"], p["lon"], y0, y1, missing_p,
                                                temporal=temporal, session=sess,
                                                timeout=90, retries=4,
                                                start_date=start_date_str, end_date=end_date_str)
                                            key = (round(p["lat"], 4), round(p["lon"], 4), y0, y1, temporal, start_date_str, end_date_str, tuple(sorted(missing_p)))
                                            nasa_cache[key] = par
                                            results[idx].setdefault("parameter", {}).update(par)
                                            results[idx]["status"] = "OK"
                                            results[idx]["error"] = ""
                                            msg("    -> [RESCUED %d/%d] Station OID %s recovered successfully!"
                                                % (r_i + 1, len(failed_nasa), p.get("oid", idx + 1)))
                                        except Exception as ex_r:
                                            results[idx]["error"] = str(ex_r)[:500]
                                            results[idx]["status"] = "FAILED"
                                            warn("    -> [STILL FAILED] Station OID %s: %s"
                                                 % (p.get("oid", idx + 1), str(ex_r)[:150]))
                            else:
                                msg("Element [%d/%d] %s: All required variables (%s) already cached in memory. Reusing with 0 queries."
                                    % (mi + 1, len(ordered_modules), m, ", ".join(needed_m)))

                        t_dl_dur = time.time() - t_dl_start
                        n_q = len(pts_to_fetch)
                        avg_dl_s = (t_dl_dur / max(1, n_q)) if n_q else 0.0
                        msg("  [TIMING] Element [%d/%d] %s: Data retrieved in %s (Avg: %.2fs/station, %d queried, %d cached)."
                            % (mi + 1, len(ordered_modules), m, format_duration(t_dl_dur), avg_dl_s, n_q, len(pts) - n_q))

                        # Compute indicators for this element
                        msg("Element [%d/%d] %s: Computing indicators ..." % (mi + 1, len(ordered_modules), m))
                        for idx, rec in enumerate(results):
                            try:
                                if use_om:
                                    monthly = rec.get("monthly", {})
                                    daily_raw = rec.get("daily_raw", {})
                                    precip_totals = True
                                else:
                                    avail_p = list(rec.get("parameter", {}).keys())
                                    monthly, daily_raw = self._monthly_from_response(
                                        rec.get("parameter", {}), temporal, avail_p, years)
                                    precip_totals = False
                                    rec["monthly"] = monthly
                                    rec["daily_raw"] = daily_raw

                                if time_mode == "Custom Date Range" and d_start and d_end:
                                    start_ym = (d_start.year, d_start.month)
                                    end_ym = (d_end.year, d_end.month)
                                    for var, ym_dict in list(monthly.items()):
                                        if isinstance(ym_dict, dict):
                                            monthly[var] = dict((ym, v) for ym, v in ym_dict.items()
                                                                if start_ym <= ym <= end_ym)

                                f = compute_point_fields(monthly, years, [m], temporal,
                                                         daily_raw, precip_totals, gap_method,
                                                         lat=rec.get("lat", 0.0),
                                                         uv_source=("om" if use_om else "nasa"),
                                                         monthly_ranges=monthly_ranges_on,
                                                         unit_temp=unit_temp_text,
                                                         unit_precip=unit_precip_text,
                                                         unit_press=unit_press_text,
                                                         unit_wind=unit_wind_text,
                                                         unit_solar=unit_solar_text)
                                rec.setdefault("fields", {}).update(f)
                            except Exception as ex:
                                warn("Element '%s' failed at point %s: %s"
                                     % (m, rec.get("oid"), str(ex)[:200]))

                        if gap_method != "none":
                            spatial_impute_missing(results, [m])

                        if m == "UV Index" and not use_om and years and min(years) < 2001:
                            warn("UV Index: NASA CERES UV starts 2001; requested %d-%d so "
                                 "1996-2000 are climatology-filled and the effective UV "
                                 "coverage is 2001-%d (recorded per-point as Data_Start=2001)."
                                 % (min(years), max(years), max(years)))

                        for rec in results:
                            vals = rec.get("fields", {})
                            n_valid = sum(1 for v in vals.values() if v is not None)
                            if not rec.get("status") or rec["status"] == "PENDING":
                                rec["status"] = "OK" if n_valid > 0 else "FAILED"
                            if n_valid == 0 and rec.get("status") == "FAILED":
                                rec["error"] = "No valid values from " + provider

                        # Immediate GDB Layer Commit for this element
                        w_fields = wanted_fields_by_module.get(m, []) if wanted_fields_by_module else None
                        fc = self._build_single_element_layer(
                            tmp_base, gdb_path, results, m, admin_meta, msg, warn, wanted_fields=w_fields)
                        if fc and arcpy.Exists(fc):
                            element_fcs[m] = fc

                        # Immediate Export of Shapefile, Excel
                        short = MODULE_SHORT.get(m, m)
                        if export_shp:
                            self._export_shapefile(fc, os.path.join(paths["shp"], short + ".shp"), msg, warn)
                        daily_pkg = None
                        if save_daily and temporal == "Daily":
                            try:
                                daily_pkg = self._build_daily_table(results, list(MODULE_PARAMS.get(m, [])))
                            except Exception as ex_d:
                                warn("Daily table skipped for '%s': %s" % (m, str(ex_d)[:150]))
                        self._export_excel(fc, os.path.join(paths["vec"], short + ".xls"), msg, warn,
                                           daily=daily_pkg, module_name=m)
                        if daily_pkg:
                            try:
                                self._export_daily_gdb_table(gdb_path, short, daily_pkg, msg, warn)
                            except Exception as ex_gt:
                                warn("Daily GDB table skipped for '%s': %s" % (m, ex_gt))


                        elem_rasters = []
                        t_mod_interp_elapsed = 0.0
                        if is_sequential:
                            # Immediate Raster Interpolation (Sequential Mode)
                            if not download_only and sa_avail:
                                if mask_required:
                                    mask = ensure_mask_fc(mask, mask_orig, maskp, out_sr, msg, warn)
                                    if not mask:
                                        warn("Element '%s': mask unavailable, rasters skipped "
                                             "(no unclipped output published)." % m)
                                        msg(">>> Element [%d/%d] %s completed: Point layer, Shapefile, CSV, Excel (rasters skipped). <<<\n"
                                            % (mi + 1, len(ordered_modules), m))
                                        continue
                                t_interp_start = time.time()
                                elem_rasters = self._interpolate_all(
                                    None, [m], paths, eff_base, interp, mask, msg, warn,
                                    iopts, kopts, is_geo, purge, scratch_dir, focal,
                                    {m: fc}, wanted_fields_by_module=wanted_fields_by_module,
                                    reclass_opts=reclass_opts,
                                    raster_mask=raster_mask,
                                    raster_timings=raster_timings,
                                    monthly_enabled=monthly_enabled,
                                    monthly_ranges_on=monthly_ranges_on)
                                t_mod_interp_elapsed = time.time() - t_interp_start
                                raster_registry.extend(elem_rasters)
                                if purge and os.path.exists(scratch_dir):
                                    for sf in os.listdir(scratch_dir):
                                        sfp = os.path.join(scratch_dir, sf)
                                        try:
                                            # NEVER delete the reprojected mask: it is
                                            # reused by every element + wind vectors.
                                            if os.path.isfile(sfp) and not sf.lower().startswith(("maskp.", "mask_raster")):
                                                os.remove(sfp)
                                        except Exception:
                                            pass
                                gc.collect()

                            t_mod_dur = time.time() - t_mod_start
                            mod_end_clock = now_str().split(" ")[1]
                            module_timings[m] = {
                                "start_time": mod_start_clock,
                                "end_time": mod_end_clock,
                                "dl_dur": t_dl_dur,
                                "interp_dur": t_mod_interp_elapsed,
                                "n_pts": len(pts),
                                "n_queried": n_q,
                                "n_rasters": len(elem_rasters),
                                "total_dur": t_mod_dur,
                                "status": "OK" if any(r.get("status") == "OK" for r in results) else "FAILED"
                            }
                            msg(">>> Element [%d/%d] %s completed in %s (Download: %s | Rasters [%d]: %s). <<<\n"
                                % (mi + 1, len(ordered_modules), m, format_duration(t_mod_dur),
                                   format_duration(t_dl_dur), len(elem_rasters), format_duration(t_mod_interp_elapsed)))
                        else:
                            t_mod_dur = time.time() - t_mod_start
                            mod_end_clock = now_str().split(" ")[1]
                            module_timings[m] = {
                                "start_time": mod_start_clock,
                                "end_time": mod_end_clock,
                                "dl_dur": t_dl_dur,
                                "interp_dur": 0.0,
                                "n_pts": len(pts),
                                "n_queried": n_q,
                                "n_rasters": 0,
                                "total_dur": t_mod_dur,
                                "status": "OK" if any(r.get("status") == "OK" for r in results) else "FAILED"
                            }
                            msg(">>> [BATCH DATA COMMITTED] Element [%d/%d] %s: Point layer & vector exports committed to GDB (%s). <<<\n"
                                % (mi + 1, len(ordered_modules), m, format_duration(t_mod_dur)))

                    # Batch Mode Phase 2: Spatial Interpolation for all committed layers
                    if is_batch and not download_only and sa_avail:
                        msg("\n" + "=" * 65)
                        msg(">>> [BATCH MODE PHASE 2] All Data Committed to GDB. Starting Spatial Interpolation for All Modules <<<")
                        msg("=" * 65)
                        for mi, m in enumerate(ordered_modules):
                            fc = element_fcs.get(m)
                            if not fc or not arcpy.Exists(fc):
                                continue
                            if mask_required:
                                mask = ensure_mask_fc(mask, mask_orig, maskp, out_sr, msg, warn)
                                if not mask:
                                    warn("Element '%s': mask unavailable, rasters skipped." % m)
                                    continue
                            t_b_start = time.time()
                            elem_rasters = self._interpolate_all(
                                None, [m], paths, eff_base, interp, mask, msg, warn,
                                iopts, kopts, is_geo, purge, scratch_dir, focal,
                                {m: fc}, wanted_fields_by_module=wanted_fields_by_module,
                                reclass_opts=reclass_opts,
                                raster_mask=raster_mask,
                                raster_timings=raster_timings,
                                monthly_ranges_on=monthly_ranges_on)
                            t_b_dur = time.time() - t_b_start
                            raster_registry.extend(elem_rasters)
                            if m in module_timings:
                                module_timings[m]["interp_dur"] = t_b_dur
                                module_timings[m]["n_rasters"] = len(elem_rasters)
                                module_timings[m]["total_dur"] += t_b_dur
                            if purge and os.path.exists(scratch_dir):
                                for sf in os.listdir(scratch_dir):
                                    sfp = os.path.join(scratch_dir, sf)
                                    try:
                                        if os.path.isfile(sfp) and not sf.lower().startswith(("maskp.", "mask_raster")):
                                            os.remove(sfp)
                                    except Exception:
                                        pass
                            gc.collect()
                            msg(">>> Element [%d/%d] %s: Rasters interpolated & clipped in %s (Generated %d rasters). <<<\n"
                                % (mi + 1, len(ordered_modules), m, format_duration(t_b_dur), len(elem_rasters)))

                finally:
                    if tmp_base_is_temp:
                        try:
                            arcpy.management.Delete(tmp_base)
                        except Exception:
                            pass

                n_data = sum(1 for r in results if r.get("status") == "OK")
                n_empty = len(results) - n_data
                ok_count = n_data
                fail = [(r["oid"], r.get("error", "")) for r in results
                        if r.get("status") != "OK"]
                msg("Data retrieved for %d/%d points%s." % (
                    n_data, len(results),
                    (" (%d without valid values)" % n_empty) if n_empty else ""))
                if results and n_data == 0:
                    raise RuntimeError(
                        "No point received valid values from %s. Check the failure reasons "
                        "above (network, server limits, or period outside coverage %d-%d); "
                        "fix and re-run instead of building an empty atlas."
                        % (provider, y0, y1))

            # Ensure points are available for provenance documentation even in offline mode
            if not results and element_fcs:
                try:
                    first_m = ordered_modules[0] if ordered_modules else None
                    first_fc = element_fcs.get(first_m) if first_m else None
                    if first_fc and arcpy.Exists(first_fc):
                        wgs = arcpy.SpatialReference(4326)
                        results = self._extract_points(first_fc, wgs, messages)
                except Exception:
                    pass

            # Master Excel Workbook (.xls) containing all active modules
            try:
                master_sheets = []
                prov_sheet, sum_sheet, ar_sum_sheet = build_source_data_provenance_table(
                    results, ordered_modules, provider, om_model, gap_method, y0, y1, temporal)
                if prov_sheet and prov_sheet[2]:
                    master_sheets.append(prov_sheet)
                if sum_sheet and sum_sheet[2]:
                    master_sheets.append(sum_sheet)

                for m in ordered_modules:
                    short = MODULE_SHORT.get(m, m)
                    fc = element_fcs.get(m)
                    if fc and arcpy.Exists(fc):
                        f_names = [f.name for f in arcpy.ListFields(fc)
                                   if f.type not in ("Geometry", "Raster", "Blob")]
                        f_rows = []
                        with arcpy.da.SearchCursor(fc, f_names) as cur:
                            for r in cur:
                                f_rows.append(list(r))
                        master_sheets.append((short, f_names, f_rows, False))
                if master_sheets:
                    master_xls = os.path.join(paths["vec"], "Climate_Atlas_Master_Workbook.xls")
                    write_master_excel_workbook(master_xls, master_sheets)
                    msg("Master Excel Workbook: %s (%d sheets)" % (master_xls, len(master_sheets)))
            except Exception as ex:
                warn("Master Excel export warning: %s" % ex)

            # Dedicated Source Data Folder with Provenance Workbooks and Documentation
            try:
                export_source_data_folder(
                    out_ws, results, ordered_modules, provider, om_model, gap_method,
                    y0, y1, temporal, msg, warn)
            except Exception as ex_sd:
                warn("Source Data folder export warning: %s" % ex_sd)

            wind_fcs = []
            iso_scheme, iso_step = "", None
            if download_only:
                msg("Download-only mode: skipping rasters, wind vectors and isobars.")
            else:

                if "Wind" in modules and sa_avail:
                    wind_w = wanted_fields_by_module.get("Wind", [])
                    has_spd = any("W_Spd" in f for f in wind_w)
                    has_dir = any("W_Dir" in f for f in wind_w)
                    if has_spd and has_dir:
                        if mask_required:
                            mask = ensure_mask_fc(mask, mask_orig, maskp, out_sr, msg, warn)
                        if mask_required and not mask:
                            warn("Wind vectors skipped: mask unavailable.")
                        else:
                            try:
                                wind_fcs = self._build_wind_vectors(
                                    gdb_path, paths, raster_registry, element_fcs.get("Wind"),
                                    mask, out_sr, eff_wind, msg, warn, export_shp)
                            except Exception as ex:
                                warn("Wind vectors failed: %s" % ex)

            iso_mods = [m for m in ("Sea Level Pressure", "Surface Pressure")
                        if m in modules]
            has_iso_r = any(r[3] in iso_mods for r in raster_registry)
            if create_isobars and iso_mods and sa_avail and has_iso_r:
                p_isch = pdict.get("Pressure_Interval_Scheme")
                _scheme = p_isch.valueAsText if (p_isch and p_isch.valueAsText) else "Global Standard (4 mbar)"
                p_istep = pdict.get("Custom_Pressure_Step")
                _stepv = p_istep.value if (p_istep and p_istep.value is not None) else 4.0
                if _scheme == "Custom Interval":
                    iso_step = float(_stepv) if _stepv is not None else 4.0
                elif _scheme.startswith("Local"):
                    iso_step = 2.0
                else:
                    iso_step = 4.0
                iso_scheme = _scheme
                if iso_step <= 0:
                    warn("Isobar step must be > 0; using 4.0 mbar.")
                    iso_step = 4.0
                msg("Isobars (%s, step %.2f mbar) for: %s."
                    % (_scheme, iso_step, ", ".join(iso_mods)))
                try:
                    try:
                        iso_mask = ensure_mask_fc(mask, mask_orig, maskp, out_sr, msg, warn)
                    except Exception:
                        iso_mask = None
                    self._build_isobars(gdb_path, raster_registry, msg, warn, iso_step, iso_mask)
                except Exception as ex:
                    warn("Isobars failed: %s" % ex)
            elif create_isobars and not iso_mods:
                warn("Create_Isobars checked but no pressure module selected: skipped.")

            self._write_dictionaries(paths["vec"], active_export_modules, msg, provider,
                                     wanted_fields_by_module=wanted_fields_by_module)
            qa = self._run_qa(element_fcs, paths, active_export_modules, raster_registry, results, msg, warn,
                              wanted_fields_by_module=wanted_fields_by_module)

            ar_gdb_path = None
            if arabic_db and element_fcs:
                try:
                    ar_gdb_path = self._build_arabic_db(gdb_path, element_fcs, msg, warn)
                except Exception as ex:
                    warn("Arabic DB failed: %s" % ex)
                    ar_gdb_path = None

            if is_offline:
                _first_fc = list(element_fcs.values())[0] if element_fcs else None
                _n_pts = int(arcpy.GetCount_management(_first_fc)[0]) if (_first_fc and arcpy.Exists(_first_fc)) else 0
                _n_ok = _n_pts
                _fail = []
            else:
                _n_pts = len(pts)
                _n_ok = ok_count
                _fail = fail

            t_total_elapsed = time.time() - t_start
            self._write_log(paths["vec"], {
                "tool_version": TOOL_VERSION, "modules": active_export_modules,
                "submodels": active_submodels, "years": (y0, y1, len(years)),
                "temporal": temporal, "interp": interp_label, "provider": provider,
                "interp_detail": {"idw": iopts, "krig": kopts},
                "base_cell": base_cell,
                "wind_cell": wind_cell, "n_points": _n_pts, "n_ok": _n_ok,
                "n_fail": len(_fail), "failed": _fail[:50], "rasters": raster_registry,
                "wind": wind_fcs, "warnings": warnings, "qa": qa,
                "elapsed": t_total_elapsed,
                "start_time": overall_start_dt,
                "end_time": now_str(),
                "module_timings": module_timings,
                "raster_timings": raster_timings,
                "purge": purge, "add_to_map": add_to_map,
                "tol_m": tol_m, "focal": focal, "dl_only": download_only,
                "element_layers": element_fcs,
                "iso": (iso_scheme, iso_step),
                "export_shp": export_shp, "arabic_db": ar_gdb_path,
            })
            if add_to_map and not download_only:
                p_map_mods = pdict.get("Map_Add_Modules")
                _mtxt = p_map_mods.valueAsText if (p_map_mods and p_map_mods.valueAsText) else ""
                map_modules = [m.strip().strip("'\"") for m in _mtxt.split(";")
                               if m.strip().strip("'\"")]
                map_modules = [m for m in map_modules if m in active_export_modules]
                if not map_modules:
                    warn("Add to map: no selected element was computed; nothing added.")
                else:
                    self._add_to_map(raster_registry, wind_fcs, map_modules,
                                     msg, warn)
            self._cleanup(msg, scratch_dir, purge)
            # Generate Master Climate Atlas Classification & Specification Guide
            try:
                tool_dir = os.path.dirname(os.path.abspath(__file__))
                if tool_dir not in sys.path:
                    sys.path.insert(0, tool_dir)
                import generate_master_atlas_excel
                guide_path = os.path.join(paths["vec"], "Climate_Atlas_Classification_Guide.xlsx")
                sp_info = {
                    "name": clean_sname,
                    "display_name": study_area_name or clean_sname
                }
                if mask and arcpy.Exists(mask):
                    try:
                        tot_sqkm = 0.0
                        tot_perim = 0.0
                        with arcpy.da.SearchCursor(mask, ["SHAPE@"]) as s_cur:
                            for s_row in s_cur:
                                geom = s_row[0]
                                if geom:
                                    try:
                                        tot_sqkm += geom.getArea("GEODESIC", "SQUAREKILOMETERS")
                                        tot_perim += geom.getLength("GEODESIC", "KILOMETERS")
                                    except Exception:
                                        tot_sqkm += (geom.area / 1e6)
                                        tot_perim += (geom.length / 1e3)
                        if tot_sqkm > 0:
                            sp_info["total_sqkm"] = tot_sqkm
                            sp_info["area"] = "{:,.2f} كم² ({:,.2f} مليون هكتار)".format(tot_sqkm, tot_sqkm / 10000.0) if tot_sqkm >= 10000 else "{:,.2f} كم² ({:,.2f} هكتار)".format(tot_sqkm, tot_sqkm * 100)
                        if tot_perim > 0:
                            sp_info["perimeter"] = "{:,.2f} كم".format(tot_perim)
                        
                        desc_m = arcpy.Describe(mask)
                        ext_m = desc_m.extent
                        sr_m = desc_m.spatialReference
                        if sr_m and sr_m.factoryCode == 4326:
                            sp_info["extent"] = "{:.4f}°N إلى {:.4f}°N | {:.4f}°E إلى {:.4f}°E".format(
                                ext_m.YMin, ext_m.YMax, ext_m.XMin, ext_m.XMax
                            )
                        else:
                            sr_wgs = arcpy.SpatialReference(4326)
                            p_min = arcpy.PointGeometry(arcpy.Point(ext_m.XMin, ext_m.YMin), sr_m).projectAs(sr_wgs)
                            p_max = arcpy.PointGeometry(arcpy.Point(ext_m.XMax, ext_m.YMax), sr_m).projectAs(sr_wgs)
                            sp_info["extent"] = "{:.4f}°N إلى {:.4f}°N | {:.4f}°E إلى {:.4f}°E".format(
                                p_min.firstPoint.Y, p_max.firstPoint.Y, p_min.firstPoint.X, p_max.firstPoint.X
                            )
                    except Exception as ex_sp:
                        warn("Could not calculate spatial geometry metrics: %s" % ex_sp)

                pts_for_count = primary_in_point if (primary_in_point and arcpy.Exists(primary_in_point)) else None
                if not pts_for_count:
                    pts_fc_check = os.path.join(gdb_path, "%s_Grid_Points" % clean_sname)
                    if arcpy.Exists(pts_fc_check):
                        pts_for_count = pts_fc_check
                if pts_for_count:
                    try:
                        cnt = int(arcpy.management.GetCount(pts_for_count)[0])
                        sp_info["points"] = "{:,} محطة رصد مناخية".format(cnt)
                    except Exception:
                        pass

                generate_master_atlas_excel.build_master_classification_workbook(
                    base_dir=out_ws,
                    study_area_name=clean_sname,
                    target_excel=guide_path,
                    spatial_info=sp_info,
                    tech_info={
                        "cell_size": "%.1f متر (%.1f Meters)" % (eff_base if is_geo else base_cell, base_cell),
                        "wind_cell": "%.1f متر (%.1f Meters)" % (eff_wind if is_geo else wind_cell, wind_cell),
                        "isobar_step": "4.0 mbar (Global Standard)",
                        "interp": interp,
                        "period": period_label,
                        "source": provider
                    }
                )
                msg("Generated Master Climate Atlas Classification Guide: %s" % guide_path)
                root_guide_path = os.path.join(out_ws, "Climate_Atlas_Classification_Guide.xlsx")
                try:
                    import shutil
                    shutil.copy2(guide_path, root_guide_path)
                    msg("Saved root workspace copy of Classification Guide: %s" % root_guide_path)
                except Exception as ex_copy:
                    warn("Could not copy Classification Guide to root: %s" % ex_copy)
            except Exception as ex_guide:
                warn("Could not generate Climate Atlas Classification Guide: %s" % ex_guide)

            msg("\n" + "=" * 70)
            msg("  [DONE] NASA POWER Climate Atlas Generated Successfully!")
            msg("  Execution Started : %s" % overall_start_dt)
            msg("  Execution Finished: %s" % now_str())
            msg("  Total Duration    : %s (%.1f seconds)" % (format_duration(t_total_elapsed), t_total_elapsed))
            msg("  Project Directory : %s" % out_ws)
            msg("  Tables & Reports  : %s" % paths["vec"])
            msg("=" * 70 + "\n")
        except Exception as ex:
            tb = traceback.format_exc()
            messages.addErrorMessage("FAILED: %s\n%s" % (ex, tb))
            raise
        finally:
            try:
                # In ArcGIS Pro, checking in extension inside background geoprocessing causes
                # IAoInitialize / CheckInLicenseExtension null pointer dereference (0xC0000005 in ucrtbase.dll!strcpy).
                # Only check in extension in desktop ArcMap (10.x).
                if not hasattr(arcpy, "mp"):
                    arcpy.CheckInExtension("Spatial")
            except Exception:
                pass


    def _add_to_map(self, registry, wind_fcs, map_modules, msg, warn):
        """Add chosen elements to the CURRENT ArcMap data frame, one group layer
        per element. Element rasters (.tif) go to the bottom of each group.

        Group strategy (best effort, never fails the run):
          1. a group with the element name already exists -> add inside it,
          2. else create the group via ArcObjects automation (needs running ArcMap),
          3. else add the element layers flat with a warning.
        Outside ArcMap (no CURRENT document) it logs a warning and returns."""

        def _find_group(mxd, df, name):
            try:
                for l in arcpy.mapping.ListLayers(mxd, "", df):
                    if getattr(l, "isGroupLayer", False) and l.name == name:
                        return l
            except Exception:
                pass
            return None

        def _create_group(mxd, df, name):
            found = _find_group(mxd, df, name)
            if found is not None:
                return found
            try:
                from comtypes.client import GetActiveObject, CreateObject
                app = GetActiveObject("esriArcMap.Application")
                focus_map = app.Document.FocusMap
                grp = CreateObject("esriCarto.GroupLayer")
                grp.Name = name
                focus_map.AddLayer(grp)
                try:
                    app.Document.UpdateContents()
                    app.Document.ActiveView.Refresh()
                except Exception:
                    pass
                return _find_group(mxd, df, name)
            except Exception as ex:
                warn("Group '%s' could not be created (%s); layers added flat."
                     % (name, str(ex)[:120]))
                return None

        # Check if running inside ArcGIS Pro (arcpy.mp)
        if hasattr(arcpy, "mp"):
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                m = getattr(aprx, "activeMap", None)
                if not m:
                    maps = aprx.listMaps()
                    if maps:
                        m = maps[0]
                if not m:
                    warn("Add to map skipped: no active map in ArcGIS Pro project.")
                    return
                by_module = {}
                for (_f, _r, _lp, _m, _c, _n) in registry:
                    by_module.setdefault(_m, []).append(_r)
                
                # Gather all valid layers to add sequentially
                items_to_add = []
                for module in map_modules:
                    lps = by_module.get(module, [])
                    extras = []
                    if module == "Wind":
                        extras = [w for w in (wind_fcs or []) if arcpy.Exists(w)]
                    for lp in lps + extras:
                        if lp and arcpy.Exists(lp):
                            items_to_add.append((module, lp))

                total_items = len(items_to_add)
                if total_items == 0:
                    warn("Add to map: no valid layers found to add.")
                    return

                msg("\n>>> Safely adding %d layer(s) to current ArcGIS Pro map sequentially... <<<" % total_items)
                added = 0
                for idx, (module, lp) in enumerate(items_to_add, 1):
                    try:
                        bname = os.path.basename(lp)
                        msg("  -> [%d/%d] Adding to map: %s (%s)..." % (idx, total_items, bname, module))
                        new_layer = m.addDataFromPath(lp)
                        # Safeguard: Keep the first layer visible for immediate preview,
                        # hide subsequent layers to prevent GPU/DirectX rendering storm and memory crash
                        try:
                            if new_layer:
                                lyrs = new_layer if isinstance(new_layer, (list, tuple)) else [new_layer]
                                for lyr in lyrs:
                                    if added > 0:
                                        lyr.visible = False
                        except Exception:
                            pass
                        added += 1
                        time.sleep(0.05)  # Yield for ArcGIS Pro UI event loop
                    except Exception as ex:
                        warn("Could not add %s to Pro map: %s" % (lp, ex))
                msg("Successfully added %d layer(s) to ArcGIS Pro map (background layers initially hidden to protect performance)." % added)
                return
            except Exception as ex:
                warn("Add to ArcGIS Pro map skipped: %s" % ex)
                return

        try:
            mxd = arcpy.mapping.MapDocument("CURRENT")
        except Exception as ex:
            warn("Add to map skipped (not running inside ArcMap or ArcGIS Pro): %s" % ex)
            return
        try:
            dfs = arcpy.mapping.ListDataFrames(mxd)
            if not dfs:
                warn("Add to map skipped (no data frame in current map).")
                return
            df = dfs[0]
            by_module = {}
            for (_f, _r, _lp, _m, _c, _n) in registry:
                by_module.setdefault(_m, []).append(_r)
            
            # Gather all valid layers for ArcMap
            items_to_add = []
            for module in map_modules:
                lps = by_module.get(module, [])
                extras = []
                if module == "Wind":
                    extras = [w for w in (wind_fcs or []) if arcpy.Exists(w)]
                for lp in lps + extras:
                    if lp and arcpy.Exists(lp):
                        items_to_add.append((module, lp))

            total_items = len(items_to_add)
            if total_items == 0:
                warn("Add to map: no valid layers found to add.")
                return

            msg("\n>>> Safely adding %d layer(s) to current ArcMap data frame sequentially... <<<" % total_items)
            added = 0
            groups = {}
            for idx, (module, lp) in enumerate(items_to_add, 1):
                try:
                    bname = os.path.basename(lp)
                    msg("  -> [%d/%d] Adding to ArcMap: %s (%s)..." % (idx, total_items, bname, module))
                    gname = MODULE_FOLDER.get(module, module)
                    if gname not in groups:
                        groups[gname] = _create_group(mxd, df, gname)
                    grp = groups.get(gname)

                    layer = arcpy.mapping.Layer(lp)
                    if added > 0:
                        layer.visible = False
                    if grp is not None:
                        arcpy.mapping.AddLayerToGroup(df, grp, layer, "BOTTOM")
                    else:
                        arcpy.mapping.AddLayer(df, layer, "BOTTOM")
                    added += 1
                    time.sleep(0.02)
                except Exception as ex:
                    warn("Could not add %s to map: %s" % (lp, ex))
            try:
                arcpy.RefreshActiveView()
                arcpy.RefreshTOC()
            except Exception:
                pass
            msg("Successfully added %d layer(s) to ArcMap (background layers initially hidden)." % added)
        except Exception as ex:
            warn("Add to map failed: %s" % ex)

    # ================= helpers (arcpy) =================
    def _build_layout(self, out_ws, modules, gdb_name=None, export_shp=False):
        makedirs_ok(out_ws)
        if not gdb_name:
            gdb_name = "Climate_Database.gdb"
        if not gdb_name.lower().endswith(".gdb"):
            gdb_name += ".gdb"
        gdb_path = os.path.join(out_ws, gdb_name)
        if not arcpy.Exists(gdb_path):
            arcpy.management.CreateFileGDB(out_ws, gdb_name)
        paths = {"gdb": gdb_path, "vec": os.path.join(out_ws, "00_Tables_And_Reports"),
                 "shp": os.path.join(out_ws, "Export_SHP"),
                 "source_data": os.path.join(out_ws, "Source Data")}
        makedirs_ok(paths["vec"])
        makedirs_ok(paths["source_data"])
        if export_shp:
            makedirs_ok(paths["shp"])
        for m in modules:
            folder = os.path.join(out_ws, MODULE_FOLDER[m])
            if m == "Wind":
                for sub in ["Speed", "Direction"]:
                    makedirs_ok(os.path.join(folder, sub))
            else:
                makedirs_ok(folder)
        return gdb_path, paths

    def _extract_points(self, in_points, wgs, messages):
        d = arcpy.Describe(in_points)
        oid_field = d.OIDFieldName
        in_sr = d.spatialReference
        fields_in = [f.name for f in arcpy.ListFields(in_points)]

        st_id_field = next((f for f in ["Station_ID", "STATION_ID", "station_id", "Source_ID"] if f in fields_in), None)
        st_nm_field = next((f for f in ["Name", "Station_Nm", "STATION_NM", "NAME", "station_name"] if f in fields_in), None)
        st_ctry_field = next((f for f in ["Country", "Country_Nm", "Country_Cd", "COUNTRY", "country"] if f in fields_in), None)
        st_elev_field = next((f for f in ["Elev_m", "Elev_Meters", "ELEV_M", "Elevation", "elevation"] if f in fields_in), None)

        search_fields = [oid_field, "SHAPE@XY"]
        f_map = {}
        if st_id_field:
            f_map["st_id"] = len(search_fields)
            search_fields.append(st_id_field)
        if st_nm_field:
            f_map["st_nm"] = len(search_fields)
            search_fields.append(st_nm_field)
        if st_ctry_field:
            f_map["st_ctry"] = len(search_fields)
            search_fields.append(st_ctry_field)
        if st_elev_field:
            f_map["st_elev"] = len(search_fields)
            search_fields.append(st_elev_field)

        pts = []
        with arcpy.da.SearchCursor(in_points, search_fields) as cur:
            for row in cur:
                try:
                    x, y = row[1][0], row[1][1]
                    try:
                        need_reproj = (in_sr.factoryCode != 4326)
                    except Exception:
                        need_reproj = (in_sr.name != wgs.name)
                    if need_reproj:
                        pt = arcpy.PointGeometry(arcpy.Point(x, y), in_sr).projectAs(wgs)
                        lon, lat = pt.centroid.X, pt.centroid.Y
                    else:
                        lon, lat = x, y

                    p_info = {"oid": row[0], "lat": float(lat), "lon": float(lon)}
                    if "st_id" in f_map and row[f_map["st_id"]] is not None:
                        p_info["station_id"] = str(row[f_map["st_id"]])
                    else:
                        p_info["station_id"] = "PNT_%04d" % row[0]
                    if "st_nm" in f_map and row[f_map["st_nm"]]:
                        p_info["station_name"] = str(row[f_map["st_nm"]])
                    else:
                        p_info["station_name"] = "Point %d" % row[0]
                    if "st_ctry" in f_map and row[f_map["st_ctry"]]:
                        p_info["country"] = str(row[f_map["st_ctry"]])
                    else:
                        p_info["country"] = "Regional"
                    if "st_elev" in f_map and row[f_map["st_elev"]] is not None:
                        try:
                            p_info["elevation"] = float(row[f_map["st_elev"]])
                        except Exception:
                            p_info["elevation"] = 0.0
                    else:
                        p_info["elevation"] = 0.0

                    pts.append(p_info)
                except Exception:
                    continue
        return pts

    def _query_all(self, pts, y0, y1, params, temporal, messages, msg, warn, tag="",
                   start_date=None, end_date=None):
        # Sequential in-order queries (one point at a time). On 32-bit ArcMap this
        # keeps peak memory minimal (each response is processed and released before
        # the next), avoids NASA API rate-limiting from parallel bursts, and gives
        # a steady, predictable progress bar. A single reused HTTP session plus an
        # in-run cache for duplicate coordinates keeps it efficient.
        cache = {}
        sess = None
        if _HAS_REQUESTS:
            try:
                sess = requests.Session()
            except Exception:
                sess = None
        msg("Querying NASA POWER sequentially%s (timeout 60s, 3 retries per point) ..."
            % ((" [%s]" % tag) if tag else ""))
        results = []
        arcpy.SetProgressor("step", "Querying NASA POWER ...", 0, len(pts), 1)
        for idx, p in enumerate(pts):
            key = (round(p["lat"], 4), round(p["lon"], 4), y0, y1, temporal, start_date, end_date)
            if key in cache:
                results.append(dict(p, parameter=cache[key], status="OK", error=""))
            else:
                try:
                    par = fetch_nasa_point(p["lat"], p["lon"], y0, y1, params,
                                           temporal=temporal, session=sess,
                                           start_date=start_date, end_date=end_date)
                    cache[key] = par
                    results.append(dict(p, parameter=par, status="OK", error=""))
                except Exception as ex:
                    results.append(dict(p, parameter={}, status="FAILED", error=str(ex)[:500]))
            if (idx + 1) % 10 == 0 or (idx + 1) == len(pts):
                arcpy.SetProgressorPosition(idx + 1)
                msg("  NASA %d/%d ..." % (idx + 1, len(pts)))
        arcpy.ResetProgressor()
        ok = 0
        fail = []
        for r in results:
            if r["status"] == "OK":
                ok += 1
            else:
                fail.append((r["oid"], r.get("error", "")))
        if fail:
            warn("%d NASA queries failed (kept as FAILED, process continues). e.g. %s"
                 % (len(fail), fail[:3]))
        return results, ok, fail

    def _monthly_from_response(self, parameter, temporal, needed, years):
        monthly, daily_raw = {}, {}
        if temporal == "Monthly":
            for p in needed:
                monthly[p] = parse_monthly_series(parameter.get(p, {}))
        else:
            mean_ps = [p for p in needed if p != "PRECTOTCORR"]
            m = build_monthly_from_daily(parameter, mean_ps, ["PRECTOTCORR"], years)
            monthly.update(m)
            for p in needed:
                daily_raw[p] = parse_daily_series(parameter.get(p, {}))
        return monthly, daily_raw

    def _query_all_om(self, pts, y0, y1, modules, temporal, messages, msg, warn, tag="",
                      model="era5_land", start_date=None, end_date=None):
        """Sequential Open-Meteo queries with a one-time variable probe."""
        msg("Probing Open-Meteo variable availability ...")
        daily_vars, hourly_vars, dropped, note = om_probe_vars(
            modules, model=model, start_date=start_date, end_date=end_date)
        if note:
            warn(note)
        if not daily_vars and not hourly_vars:
            return ([dict(p, monthly={}, daily_raw={}, status="FAILED",
                          error="Open-Meteo: no usable variables") for p in pts],
                    0, [(p["oid"], "no usable variables") for p in pts])
        msg("Querying Open-Meteo archive (%s) sequentially%s ..."
            % (model, (" [%s]" % tag) if tag else ""))
        results = []
        arcpy.SetProgressor("step", "Querying Open-Meteo ...", 0, len(pts), 1)
        for idx, p in enumerate(pts):
            try:
                monthly, daily_raw, _drop = fetch_openmeteo_point(
                    p["lat"], p["lon"], y0, y1, modules,
                    daily_vars=daily_vars, hourly_vars=hourly_vars,
                    model=model, start_date=start_date, end_date=end_date)
                if temporal != "Daily":
                    # Daily raw series not needed when temporal != 'Daily'
                    results.append(dict(p, monthly=monthly, daily_raw={},
                                        status="OK", error=""))
                else:
                    results.append(dict(p, monthly=monthly, daily_raw=daily_raw,
                                        status="OK", error=""))
            except Exception as ex:
                results.append(dict(p, monthly={}, daily_raw={}, status="FAILED",
                                    error=str(ex)[:500]))
            if (idx + 1) % 10 == 0 or (idx + 1) == len(pts):
                arcpy.SetProgressorPosition(idx + 1)
                msg("  Open-Meteo %d/%d ..." % (idx + 1, len(pts)))
        arcpy.ResetProgressor()
        ok = 0
        fail = []
        for r in results:
            if r["status"] == "OK":
                ok += 1
            else:
                fail.append((r["oid"], r.get("error", "")))
        if fail:
            warn("%d Open-Meteo queries failed (kept as FAILED, process continues). e.g. %s"
                 % (len(fail), fail[:3]))
        return results, ok, fail

    def _export_shapefile(self, fc, shp_path, msg, warn):
        """Export one feature class to an exact .shp path (+ sidecars).

        Long (>10 char) field names are truncated on a temp copy via
        SHP_FIELD_MAP; the GDB keeps full names. The shapefile field NAME is
        the short (<=10 char) form but its ALIAS keeps the full English field
        name (Arabic aliases live only in the opt-in _AR.gdb)."""
        tmp_copy = "in_memory/shp_tmp"
        export_fc = fc
        try:
            try:
                arcpy.management.Delete(tmp_copy)
            except Exception:
                pass
            current = set(f.name for f in arcpy.ListFields(fc))
            long_names = [n for n in SHP_FIELD_MAP if n in current]
            if long_names:
                arcpy.management.CopyFeatures(fc, tmp_copy)
                for n in long_names:
                    try:
                        arcpy.management.AlterField(tmp_copy, n, SHP_FIELD_MAP[n], n)
                    except Exception as ex:
                        warn("Shapefile field rename %s->%s failed: %s" % (n, SHP_FIELD_MAP[n], ex))
                export_fc = tmp_copy
        except Exception as ex:
            warn("Shapefile prep failed, exporting as-is: %s" % ex)
        try:
            makedirs_ok(os.path.dirname(shp_path))
            try:
                if arcpy.Exists(shp_path):
                    arcpy.management.Delete(shp_path)
            except Exception:
                pass
            arcpy.conversion.FeatureClassToShapefile([export_fc], os.path.dirname(shp_path))
            got = os.path.join(os.path.dirname(shp_path),
                               arcpy.Describe(export_fc).baseName + ".shp")
            if os.path.abspath(got) != os.path.abspath(shp_path) and os.path.isfile(got):
                stem_got = os.path.splitext(got)[0]
                stem_want = os.path.splitext(shp_path)[0]
                for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg", ".sbn", ".sbx", ".xml", ".shp.xml"]:
                    src, dst = stem_got + ext, stem_want + ext
                    if os.path.isfile(src):
                        try:
                            if os.path.isfile(dst):
                                os.remove(dst)
                            os.rename(src, dst)
                        except Exception:
                            pass
            msg("Shapefile: %s" % shp_path)
            if export_fc != fc:
                warn("Shapefile truncations applied (GDB keeps full names): %s"
                     % ", ".join("%s->%s" % (k, SHP_FIELD_MAP[k]) for k in SHP_FIELD_MAP))
        except Exception as ex:
            warn("Shapefile export failed: %s" % ex)
        finally:
            try:
                if tmp_copy and arcpy.Exists(tmp_copy):
                    arcpy.management.Delete(tmp_copy)
            except Exception:
                pass

    def _build_daily_table(self, results, params):
        """Long-format daily series for the Daily sheet: {"params": [...], "header": [...], "rows": [...]}.

        Rows: [oid, sid, st_id, st_nm, ctry, lat, lon, YYYY-MM-DD, v1, ...] sorted by oid then date.
        Missing daily values are left blank (never -999-filled). Returns None
        when no daily data is present."""
        if not results:
            return None

        # Discover all available variables across results
        available_keys = set()
        for rec in results:
            draw = rec.get("daily_raw", {}) or {}
            for k, v in draw.items():
                if isinstance(v, dict) and v:
                    available_keys.add(k)

        if not available_keys:
            return None

        # Identify matching parameters: canonical NASA param, Open-Meteo param, or any available
        have = []
        for p in (params or []):
            if p in available_keys and p not in have:
                have.append(p)
            else:
                for k in available_keys:
                    if OM_CANON.get(k) == p and k not in have:
                        have.append(k)
        if not have:
            have = sorted(list(available_keys))
        if not have:
            return None

        out_rows = []
        for rec in results:
            draw = rec.get("daily_raw", {}) or {}
            if not any(isinstance(draw.get(p), dict) and draw[p] for p in have):
                continue
            oid = rec.get("oid")
            sid = rec.get("Source_ID", rec.get("source_id", oid))
            st_id = rec.get("Station_ID", rec.get("station_id", sid))
            st_nm = rec.get("Station_Nm", rec.get("station_name", rec.get("Name", "")))
            ctry = rec.get("Country_Cd", rec.get("country", rec.get("Country", "")))
            lat = rec.get("lat")
            lon = rec.get("lon")
            by_date = {}
            for p in have:
                for ymd, v in (draw.get(p) or {}).items():
                    try:
                        ds = "%04d-%02d-%02d" % (int(ymd[0]), int(ymd[1]), int(ymd[2]))
                    except Exception:
                        continue
                    if v is None:
                        continue
                    try:
                        fv = float(v)
                    except Exception:
                        continue
                    if fv != fv:
                        continue
                    by_date.setdefault(ds, {})[p] = round(fv, 3)
            for ds in sorted(by_date):
                out_rows.append([oid, sid, st_id, st_nm, ctry, lat, lon, ds] + [by_date[ds].get(p) for p in have])
        if not out_rows:
            return None
        header = ["OBJECTID", "Source_ID", "Station_ID", "Station_Name", "Country", "Latitude", "Longitude", "Date"] + have
        return {"params": have, "header": header, "rows": out_rows}


    def _export_excel(self, fc, xls_path, msg, warn, daily=None, module_name=None):
        try:
            fields = [f.name for f in arcpy.ListFields(fc)
                      if f.type not in ("Geometry", "Raster", "Blob")]
            rows = []
            with arcpy.da.SearchCursor(fc, fields) as cur:
                for r in cur:
                    rows.append(list(r))
            
            month_keywords = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            m_fnames = [fn for fn in fields if any(mk in fn for mk in month_keywords)]
            base_fnames = [fn for fn in fields if fn in ("OBJECTID", "Source_ID", "Point_Lat", "Point_Lon")]
            # Data sheet carries annual/seasonal/overall-monthly indicators ONLY;
            # the 12 detailed monthly fields live exclusively in the Month sheet.
            data_fields = [fn for fn in fields if fn not in m_fnames]
            data_rows = [[r[fields.index(c)] for c in data_fields] for r in rows]
            sheets_to_write = [("Data", data_fields, data_rows, False)]
            if m_fnames:
                month_cols = base_fnames + m_fnames
                month_indices = [fields.index(c) for c in month_cols if c in fields]
                month_rows = [[r[idx] for idx in month_indices] for r in rows]
                sheets_to_write.append(("Month", month_cols, month_rows, False))
            # Optional third sheet: daily time series (opt-in, Daily temporal only).
            # Month sheet is always kept; daily never replaces it.
            if daily and daily.get("rows"):
                d_header = daily.get("header") or (["OBJECTID", "Source_ID", "Date"] + list(daily.get("params", [])))
                d_rows = daily["rows"]
                if len(d_rows) <= 60000:
                    sheets_to_write.append(("Daily", d_header, d_rows, False))
                else:
                    msg("Daily sheet in Excel skipped (rows=%d exceed .xls 65k limit); full CSV and GDB tables saved instead." % len(d_rows))

                # ALWAYS export complete daily timeseries CSV so data is completely retained regardless of row limits
                csv_path = os.path.splitext(xls_path)[0] + "_daily.csv"
                try:
                    import csv as _csv
                    with open(csv_path, "w", newline="", encoding="utf-8-sig") as _fh:
                        _w = _csv.writer(_fh)
                        _w.writerow(d_header)
                        _w.writerows(d_rows)
                    msg("Saved Daily Timeseries CSV: %s (%d records)" % (csv_path, len(d_rows)))
                except Exception as ex_csv:
                    warn("Daily CSV export failed: %s" % ex_csv)


            # Dedicated Source Data Provenance sheet for this element
            try:
                mod_name = module_name
                if not mod_name:
                    base_name = os.path.splitext(os.path.basename(xls_path))[0]
                    mod_name = SHORT_TO_MODULE.get(base_name, base_name)

                admin_m = getattr(self, "_admin_meta", {}) or {}
                prov_meta = get_element_source_metadata(
                    mod_name,
                    admin_m.get("provider", "NASA POWER API"),
                    admin_m.get("om_model"),
                    admin_m.get("gap_method", "climatological"),
                    admin_m.get("y0", 1996),
                    admin_m.get("y1", 2025)
                )

                elem_prov_hdr = [
                    "Point_OID", "Station_ID", "Station_Name", "Country",
                    "Latitude", "Longitude", "Elevation_m",
                    "Climate_Element", "Primary_Data_Source", "Atmospheric_Model_Sensor",
                    "Provider_URL", "Gap_Fill_Method_Applied", "Gap_Fill_Source",
                    "Temporal_Coverage", "Spatial_Resolution", "Data_Quality_Status"
                ]
                elem_prov_rows = []
                for idx, r in enumerate(rows):
                    oid = r[fields.index("OBJECTID")] if "OBJECTID" in fields else (idx + 1)
                    sid = r[fields.index("Station_ID")] if "Station_ID" in fields else (
                          r[fields.index("Source_ID")] if "Source_ID" in fields else ("PNT_%04d" % oid))
                    sname = r[fields.index("Station_Nm")] if "Station_Nm" in fields else (
                            r[fields.index("Name")] if "Name" in fields else ("Station %s" % sid))
                    ctry = r[fields.index("Country_Cd")] if "Country_Cd" in fields else (
                           r[fields.index("Country")] if "Country" in fields else "Regional")
                    lat = r[fields.index("Point_Lat")] if "Point_Lat" in fields else 0.0
                    lon = r[fields.index("Point_Lon")] if "Point_Lon" in fields else 0.0
                    elev = r[fields.index("Elev_Meters")] if "Elev_Meters" in fields else (
                           r[fields.index("Elev_m")] if "Elev_m" in fields else 0.0)

                    elem_prov_rows.append([
                        oid, sid, sname, ctry,
                        lat, lon, elev,
                        mod_name, prov_meta["primary_source"], prov_meta["model_used"],
                        prov_meta["provider_url"], prov_meta["gap_fill_method"], prov_meta["gap_fill_source"],
                        prov_meta["temporal_coverage"], prov_meta["spatial_resolution"], prov_meta["quality_status"]
                    ])

                sheets_to_write.append(("Source_Data", elem_prov_hdr, elem_prov_rows, False))
            except Exception as ex_p:
                pass
            
            write_master_excel_workbook(xls_path, sheets_to_write)
            msg("Excel: %s (sheets: %s)" % (xls_path, ", ".join(s[0] for s in sheets_to_write)))
        except Exception as ex:
            warn("Excel export failed: %s" % ex)

    def _export_csv(self, fc, csv_path, msg, warn, module_name=None):
        xls_path = os.path.splitext(csv_path)[0] + ".xls"
        return self._export_excel(fc, xls_path, msg, warn, module_name=module_name)

    def _export_daily_gdb_table(self, gdb_path, short, daily_pkg, msg, warn):
        """Exports daily time series records into a standalone File Geodatabase Table."""
        if not HAS_ARCPY or not daily_pkg or not daily_pkg.get("rows"):
            return
        tbl_name = "%s_Daily" % short
        tbl_path = os.path.join(gdb_path, tbl_name)
        try:
            if arcpy.Exists(tbl_path):
                try:
                    arcpy.management.Delete(tbl_path)
                except Exception:
                    pass
            arcpy.management.CreateTable(gdb_path, tbl_name)

            arcpy.management.AddField(tbl_path, "Source_ID", "LONG")
            arcpy.management.AddField(tbl_path, "Station_ID", "TEXT", field_length=30)
            arcpy.management.AddField(tbl_path, "Station_Name", "TEXT", field_length=120)
            arcpy.management.AddField(tbl_path, "Country", "TEXT", field_length=20)
            arcpy.management.AddField(tbl_path, "Point_Lat", "DOUBLE")
            arcpy.management.AddField(tbl_path, "Point_Lon", "DOUBLE")
            arcpy.management.AddField(tbl_path, "Obs_Date", "TEXT", field_length=15)

            params = daily_pkg.get("params", [])
            for p in params:
                arcpy.management.AddField(tbl_path, p, "DOUBLE", field_alias=p)

            cur_fields = ["Source_ID", "Station_ID", "Station_Name", "Country", "Point_Lat", "Point_Lon", "Obs_Date"] + params
            with arcpy.da.InsertCursor(tbl_path, cur_fields) as cur:
                for r in daily_pkg["rows"]:
                    # r: [oid, sid, st_id, st_nm, ctry, lat, lon, ds] + [vals]
                    row_data = [r[1], str(r[2] or ""), str(r[3] or ""), str(r[4] or ""), r[5], r[6], str(r[7] or "")] + list(r[8:])
                    cur.insertRow(row_data)
            cnt = int(arcpy.management.GetCount(tbl_path)[0])
            msg("Saved Geodatabase Daily Table: %s (%d records)" % (tbl_name, cnt))
        except Exception as ex:
            warn("Could not export daily table to GDB: %s" % ex)


    def _interp_surface(self, in_points, field, cell, method, iopts=None, kopts=None):
        iopts = iopts or {"power": 1.2, "search": "Variable", "npoints": 12, "maxdist": None,
                          "spline_type": "Tension", "spline_weight": 5.0, "spline_npoints": 12}
        kopts = kopts or {"model": "Spherical", "ktype": "Ordinary", "npoints": 12}
        if method == "IDW":
            from arcpy.sa import Idw, RadiusVariable, RadiusFixed
            power = float(iopts.get("power", 1.2))
            npts = max(1, int(iopts.get("npoints", 12)))
            maxdist = iopts.get("maxdist")
            if (iopts.get("search") or "Variable") == "Fixed":
                rr = RadiusFixed(float(maxdist), npts)
            elif maxdist:
                rr = RadiusVariable(npts, float(maxdist))
            else:
                rr = RadiusVariable(npts)
            return Idw(in_points, field, cell, power, rr)
        if method == "Ordinary Kriging":
            from arcpy.sa import Kriging, RadiusVariable
            model = kopts.get("model", "Spherical")
            npts = max(1, int(kopts.get("npoints", 12)))
            clsname = "KrigingModel" + ("Universal" if kopts.get("ktype") == "Universal"
                                        else "Ordinary")
            try:
                krmodel = getattr(arcpy.sa, clsname)(model)
            except Exception:
                krmodel = model  # string form (Ordinary) as fallback
            return Kriging(in_points, field, krmodel, cell, RadiusVariable(npts))
        if method == "Spline" or str(method).startswith("Spline"):
            from arcpy.sa import Spline
            stype = str(iopts.get("spline_type", "Tension")).upper() if iopts else "TENSION"
            weight = float(iopts.get("spline_weight", 5.0)) if iopts else 5.0
            npts = max(1, int(iopts.get("spline_npoints", 12))) if iopts else 12
            return Spline(in_points, field, cell, stype, weight, npts)
        from arcpy.sa import NaturalNeighbor
        return NaturalNeighbor(in_points, field, cell)

    def _interp_direction_uv(self, src_fc, dir_field, cell, method, iopts=None, kopts=None, warn=None):
        """Circular (U/V) interpolation for wind direction fields.

        Interpolating degrees linearly (e.g. mean of 350 and 10 = 180) is
        mathematically wrong. Instead interpolates sin(dir) and cos(dir)
        separately then reconstructs with atan2(sin, cos) -> 0-360.
        Returns an arcpy.sa Raster object or raises on failure (caller falls
        back to linear with a warning).
        Python 2.7 / ArcMap 10.8 compatible, no numpy.
        """
        import math
        tmp_fc = "in_memory/dir_uv_pts"
        lyr_sin = "pwr_atlas_dir_sin"
        lyr_cos = "pwr_atlas_dir_cos"
        for o in (tmp_fc, lyr_sin, lyr_cos):
            try:
                arcpy.management.Delete(o)
            except Exception:
                pass
        try:
            arcpy.management.CopyFeatures(src_fc, tmp_fc)
        except Exception as ex:
            raise RuntimeError("dir copy failed: %s" % ex)
        for _fn in ("TMP_SIN", "TMP_COS"):
            try:
                arcpy.management.AddField(tmp_fc, _fn, "DOUBLE")
            except Exception:
                pass
        n_valid = 0
        try:
            with arcpy.da.UpdateCursor(tmp_fc, [dir_field, "TMP_SIN", "TMP_COS"]) as cur:
                for row in cur:
                    try:
                        wd = row[0]
                        if wd is None:
                            row[1], row[2] = None, None
                        else:
                            a = float(wd) % 360.0
                            r = math.radians(a)
                            row[1] = math.sin(r)
                            row[2] = math.cos(r)
                            n_valid += 1
                    except Exception:
                        row[1], row[2] = None, None
                    cur.updateRow(row)
        except Exception as ex:
            raise RuntimeError("dir sin/cos calc failed: %s" % ex)
        if n_valid < 3:
            raise RuntimeError("only %d valid direction points" % n_valid)
        for o in (lyr_sin, lyr_cos):
            try:
                arcpy.management.Delete(o)
            except Exception:
                pass
        arcpy.management.MakeFeatureLayer(
            tmp_fc, lyr_sin, "%s IS NOT NULL" % arcpy.AddFieldDelimiters(tmp_fc, "TMP_SIN"))
        arcpy.management.MakeFeatureLayer(
            tmp_fc, lyr_cos, "%s IS NOT NULL" % arcpy.AddFieldDelimiters(tmp_fc, "TMP_COS"))
        sin_r = self._interp_surface(lyr_sin, "TMP_SIN", cell, method, iopts, kopts)
        cos_r = self._interp_surface(lyr_cos, "TMP_COS", cell, method, iopts, kopts)
        try:
            from arcpy.sa import ATan2, Con
            rad = ATan2(sin_r, cos_r)
            deg = rad * 57.29577951308232
            circular = Con(deg < 0, deg + 360.0, deg)
        except Exception:
            # Fallback if ATan2 unavailable: quadrant-corrected ATan
            from arcpy.sa import ATan, Con, Cos, Sin, Abs
            try:
                ratio = sin_r / (Abs(cos_r) + 1e-9)
                base = ATan(Abs(ratio)) * 57.29577951308232
                # quadrant logic: atan2(sin,cos)
                q1 = Con((sin_r >= 0) & (cos_r > 0), base)
                q2 = Con((sin_r >= 0) & (cos_r <= 0), 180.0 - base, q1)
                q3 = Con((sin_r < 0) & (cos_r <= 0), 180.0 + base, q2)
                circular = Con((sin_r < 0) & (cos_r > 0), 360.0 - base, q3)
            except Exception as ex2:
                raise RuntimeError("atan2 fallback failed: %s" % ex2)
        finally:
            for o in (lyr_sin, lyr_cos, tmp_fc):
                try:
                    arcpy.management.Delete(o)
                except Exception:
                    pass
        return circular

    def _raster_paths(self, out_ws, module, field):
        # Rasters are written directly inside the element folder (no Rasters/
        # subfolder, no Layers/ subfolder, no .lyr files). Monthly climatology
        # rasters (*_January_Mean ... *_December_Mean) go into a dedicated
        # Month/ subfolder so they never mix with annual/seasonal surfaces.
        # The second return value is kept (None) so existing unpacking call
        # sites keep working.
        folder = MODULE_FOLDER[module]
        if module == "Wind":
            sub = "Speed" if field.startswith("W_Spd") else "Direction"
            rdir = os.path.join(out_ws, folder, sub)
        else:
            rdir = os.path.join(out_ws, folder)
        if is_monthly_field(field):
            rdir = os.path.join(rdir, "Month")
        makedirs_ok(rdir)
        return os.path.join(rdir, field + ".tif"), None

    def _module_of_field(self, field):
        for m, fs in MODULE_FIELDS.items():
            if field in fs:
                return m
        return None

    def _colors_for(self, module, field):
        if module == "Wind":
            if field.startswith("W_Spd"):
                return COLOR_RAMPS["Wind_Speed"]
            return COLOR_RAMPS["Wind_Direction"]
        if module == "UV Index":
            return COLOR_RAMPS["UV Index"]
        if field.startswith("HI_"):
            return COLOR_RAMPS["Temperature"]
        return COLOR_RAMPS.get(module, COLOR_RAMPS["Temperature"])
    def _build_display(self, rp, field, module, colors, nclass, method_name, msg, warn,
                   purge=True, fixed_breaks=None):
        """Classified display raster for real on-open colors in ArcMap.

        Slice according to method_name -> integer zones -> VAT -> .clr colormap applied
        with AddColormap (all core-license tools). Zones are REMAPPED so zone 1
        is the HIGHEST interval (descending legend) with colors matched (hottest
        color on the highest zone). Returns (cls_path, clr_path, breaks) or (None, None, None)
        on failure (caller falls back to the continuous raster).

        fixed_breaks: optional list of nclass+1 global class edges (unified
        monthly stretch). When given, zones come from Reclassify with these
        exact edges instead of per-raster Slice, so all 12 Month/ rasters of
        one element share identical classes.
        """
        from arcpy.sa import Slice
        rdir = os.path.dirname(rp)
        ldir = rdir
        cls_rp = os.path.join(rdir, field + "_cls.tif")
        clr_path = os.path.join(ldir, field + ".clr")
        ztmp = os.path.join(rdir, field + "_z.tif")
        try:
            for _f in (cls_rp, ztmp):
                try:
                    if arcpy.Exists(_f):
                        arcpy.management.Delete(_f)
                except Exception:
                    pass
            try:
                if fixed_breaks and len(fixed_breaks) == nclass + 1:
                    # Unified monthly stretch: identical global classes for all
                    # 12 Month/ rasters (open-ended outer classes keep extremes).
                    from arcpy.sa import Reclassify, RemapRange
                    _rr = [[-1e30, fixed_breaks[1], 1]]
                    for _k in range(1, nclass - 1):
                        _rr.append([fixed_breaks[_k], fixed_breaks[_k + 1], _k + 1])
                    _rr.append([fixed_breaks[nclass - 1], 1e30, nclass])
                    Reclassify(rp, "Value", RemapRange(_rr)).save(ztmp)
                    msg("Display for %s: unified monthly classes (global stretch)." % field)
                    breaks = list(fixed_breaks)
                else:
                    meth_str = str(method_name or "Natural Breaks (Jenks)").lower()
                    if "natural" in meth_str:
                        Slice(rp, nclass, "NATURAL_BREAKS").save(ztmp)
                    elif "area" in meth_str or "quantile" in meth_str:
                        Slice(rp, nclass, "EQUAL_AREA").save(ztmp)
                    elif "geometric" in meth_str:
                        try:
                            _mn = float(arcpy.GetRasterProperties_management(rp, "MINIMUM")[0])
                        except Exception:
                            _mn = 0.0
                        shift = (1.0 - _mn) if _mn <= 0 else 0.0
                        r_pos = (arcpy.Raster(rp) + shift) if shift > 0 else arcpy.Raster(rp)
                        Slice(arcpy.sa.Ln(r_pos), nclass, "EQUAL_INTERVAL").save(ztmp)
                    elif "standard" in meth_str or "deviation" in meth_str:
                        try:
                            _mean = float(arcpy.GetRasterProperties_management(rp, "MEAN")[0])
                            _std = float(arcpy.GetRasterProperties_management(rp, "STD")[0])
                        except Exception:
                            _mean, _std = 0.0, 1.0
                        r_z = ((arcpy.Raster(rp) - _mean) / _std) if _std > 1e-9 else arcpy.Raster(rp)
                        Slice(r_z, nclass, "EQUAL_INTERVAL").save(ztmp)
                    else:
                        # Default: Equal Interval
                        Slice(rp, nclass, "EQUAL_INTERVAL").save(ztmp)

                # descending remap: zone 1 = highest interval
                (nclass + 1 - arcpy.Raster(ztmp)).save(cls_rp)
                if purge:
                    try:
                        arcpy.management.Delete(ztmp)
                    except Exception:
                        pass
                zone_colors = [hex_to_rgb(colors[nclass - k]) for k in range(1, nclass + 1)]
            except Exception:
                # constant raster: Slice cannot build intervals -> single zone
                try:
                    _mn = float(arcpy.GetRasterProperties_management(rp, "MINIMUM")[0])
                    _mx = float(arcpy.GetRasterProperties_management(rp, "MAXIMUM")[0])
                except Exception:
                    _mn, _mx = None, None
                if _mn is None or abs(_mx - _mn) > 1e-9:
                    raise
                (arcpy.Raster(rp) * 0 + 1).save(cls_rp)
                mid = colors[len(colors) // 2]
                zone_colors = [hex_to_rgb(mid)]
                msg("Display for %s: constant raster, single zone." % field)
            try:
                arcpy.management.BuildRasterAttributeTable(cls_rp)
            except Exception as ex:
                warn("VAT build for %s display skipped: %s" % (field, ex))
            with open(clr_path, "w") as fh:
                for i, rgb in enumerate(zone_colors):
                    fh.write("%d %d %d %d\n" % (i + 1, rgb[0], rgb[1], rgb[2]))
            try:
                arcpy.management.AddColormap(cls_rp, "#", clr_path)
            except Exception as ex:
                warn("Colormap for %s display skipped: %s" % (field, ex))

            # Compute actual zone breaks from continuous raster using ZonalStatisticsAsTable
            breaks = None
            try:
                scratch_dir = arcpy.env.scratchWorkspace or os.path.dirname(rp)
                ztbl = os.path.join(scratch_dir, "zst_%s" % field[:8])
                if arcpy.Exists(ztbl):
                    try:
                        arcpy.management.Delete(ztbl)
                    except Exception:
                        pass
                arcpy.sa.ZonalStatisticsAsTable(cls_rp, "Value", rp, ztbl, "DATA", "MIN_MAX")
                zone_ranges = {}
                with arcpy.da.SearchCursor(ztbl, ["Value", "MIN", "MAX"]) as cur:
                    for row in cur:
                        zone_ranges[int(row[0])] = (float(row[1]), float(row[2]))
                if purge:
                    try:
                        arcpy.management.Delete(ztbl)
                    except Exception:
                        pass
                if len(zone_ranges) == nclass:
                    b_list = [zone_ranges[nclass][0]]
                    for z in range(nclass, 0, -1):
                        b_list.append(zone_ranges[z][1])
                    breaks = b_list
            except Exception:
                breaks = None

            return cls_rp, clr_path, breaks
        except Exception as ex:
            warn("Classified display for %s failed (%s); layer will use the raw raster."
                 % (field, ex))
            return None, None, None
    def _merge_offline_layers(self, in_layers_text, gdb_path, out_sr, modules,
                              active_submodels, wanted_fields_by_module, msg, warn,
                              admin_meta=None):
        """Merges one or more precalculated point layers (multi-value) offline by coordinates/Source_ID.
        Computes requested applied submodels on the fly, builds primary element layers,
        and creates a dedicated 'Climate_Models' feature class in the GDB.
        Returns dict {module: fc_path}."""
        element_fcs = {}
        layer_paths = [lp.strip().strip("'\"") for lp in (in_layers_text or "").split(";") if lp.strip().strip("'\"")]
        if not layer_paths:
            raise RuntimeError("No precalculated point layers provided for offline mode.")

        msg("Offline multi-layer processing: inspecting %d input layer(s) ..." % len(layer_paths))

        # 1. Direct Layer Mapping: If user provides precalculated modular layers (from TOC, GDB, or SHP)
        direct_layer_map = {}
        for lyr in layer_paths:
            try:
                base_n = os.path.basename(str(lyr)).replace(".shp", "")
                canon = resolve_module_canonical(base_n)
                if not canon:
                    clean = re.sub(r'^\d+[_ ]*', '', base_n)
                    canon = resolve_module_canonical(clean)
                if canon:
                    f_set = set(f.name for f in arcpy.ListFields(lyr))
                    ind_cand = wanted_fields_by_module.get(canon, MODULE_FIELDS.get(canon, []))
                    if any(f in f_set or SHP_FIELD_MAP.get(f) in f_set for f in ind_cand):
                        direct_layer_map[canon] = lyr
            except Exception:
                pass

        for m in list(direct_layer_map.keys()):
            if m in modules:
                element_fcs[m] = direct_layer_map[m]
                msg("  Direct mapping: [%s] -> '%s' (active in TOC, no recreation or deletion needed)."
                    % (m, os.path.basename(str(direct_layer_map[m]))))

        remaining_modules = [m for m in modules if m not in direct_layer_map]
        if not remaining_modules:
            msg("  All %d requested module(s) mapped directly to input layers. Skipping table rebuilding." % len(modules))
            return element_fcs

        wgs_sr = arcpy.SpatialReference(4326)

        # 1. Base layer for geometry and projection
        base_layer = layer_paths[0]
        tmp_base = safe_project_fc(base_layer, out_sr, gdb_path, "offbase", warn)
        tmp_is_temp = (tmp_base != base_layer)

        try:
            # 2. Extract geometries and coordinates from base layer
            point_records = []
            coord_to_idx = {}
            oid_to_idx = {}
            base_desc = arcpy.Describe(tmp_base)
            oid_field = base_desc.OIDFieldName

            with arcpy.da.SearchCursor(tmp_base, [oid_field, "SHAPE@"]) as cur:
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

            msg("  Base geometry layer: %s (%d points)" % (os.path.basename(base_layer), len(point_records)))

            # 3. Read attributes from all input layers and merge by coordinates / OID
            for lyr in layer_paths:
                lyr_desc = arcpy.Describe(lyr)
                lyr_oid = lyr_desc.OIDFieldName
                all_fields = [f.name for f in arcpy.ListFields(lyr)
                              if f.type not in ("Geometry", "Raster", "Blob")]
                val_fields = [f for f in all_fields if f != lyr_oid]

                with arcpy.da.SearchCursor(lyr, [lyr_oid, "SHAPE@"] + val_fields) as cur:
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
                                canonical = REV_SHP_MAP.get(fname, fname)
                                if val is not None and not is_missing(val):
                                    if canonical not in target_fields or target_fields[canonical] is None:
                                        target_fields[canonical] = val
                                    target_fields[fname] = val
                                    shp_sh = SHP_FIELD_MAP.get(canonical)
                                    if shp_sh:
                                        target_fields[shp_sh] = val

            # 4. On-the-fly computation of active applied submodels if missing
            if active_submodels:
                msg("Computing applied submodels for offline points ...")
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
                    t_win_val = (f.get("T_Winter_Mean") if f.get("T_Winter_Mean") is not None else
                                 (f.get("T_WinMean") if f.get("T_WinMean") is not None else None))
                    t_spr_val = (f.get("T_Spring_Mean") if f.get("T_Spring_Mean") is not None else
                                 (f.get("T_SpMean") if f.get("T_SpMean") is not None else t_val))
                    rh_spr_val = (f.get("RH_Spring_Mean") if f.get("RH_Spring_Mean") is not None else
                                  (f.get("RH_SpMean") if f.get("RH_SpMean") is not None else rh_val))
                    t_aut_val = (f.get("T_Autumn_Mean") if f.get("T_Autumn_Mean") is not None else
                                 (f.get("T_AuMean") if f.get("T_AuMean") is not None else t_val))
                    rh_aut_val = (f.get("RH_Autumn_Mean") if f.get("RH_Autumn_Mean") is not None else
                                  (f.get("RH_AuMean") if f.get("RH_AuMean") is not None else rh_val))
                    ws_win_val = (f.get("W_Spd_Winter_Mean") if f.get("W_Spd_Winter_Mean") is not None else
                                  (f.get("WSp_WnMean") if f.get("WSp_WnMean") is not None else
                                   (f.get("W_Spd_Annual_Mean") if f.get("W_Spd_Annual_Mean") is not None else
                                    (f.get("WSp_AnMean") if f.get("WSp_AnMean") is not None else f.get("WS10M")))))
                    ws_ann_val = (f.get("W_Spd_Annual_Mean") if f.get("W_Spd_Annual_Mean") is not None else
                                  (f.get("WSp_AnMean") if f.get("WSp_AnMean") is not None else f.get("WS10M")))

                    # De Martonne
                    if any("De Martonne" in s for s in modules) or any("De Martonne" in s for s in active_submodels):
                        if f.get("DM_Aridity_Annual") is None and t_val is not None and p_val is not None:
                            t_f, p_f = float(t_val), float(p_val)
                            f["DM_Aridity_Annual"] = round(p_f / (t_f + 10.0), 2) if (t_f + 10.0) > 0.01 else 0.0

                    # Evapotranspiration (Hargreaves ET)
                    if any(m in ("Evapotranspiration", "Hargreaves PET", "UNEP Aridity", "Water Deficit") for m in modules) or any("Evapotranspiration" in s or "Hargreaves" in s or "UNEP" in s or "Water Deficit" in s for s in active_submodels):
                        if (f.get("ET_Annual_Mean") is None or f.get("PET_Hargreaves_Annual") is None) and t_val is not None and tx_val is not None and tn_val is not None:
                            t_f, tx_f, tn_f = float(t_val), float(tx_val), float(tn_val)
                            days_in_m = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                            tdiff = max(0.0, tx_f - tn_f)
                            m_pets = []
                            for m_idx in range(1, 13):
                                ra_m = extraterrestrial_radiation_ra(pt_lat, m_idx)
                                m_pets.append(0.0023 * ra_m * (t_f + 17.8) * math.sqrt(tdiff) * days_in_m[m_idx - 1])
                            pet_ann = sum(m_pets)
                            pet_mean = pet_ann / 12.0
                            pet_range = max(m_pets) - min(m_pets)
                            et_win = m_pets[11] + m_pets[0] + m_pets[1]
                            et_spr = m_pets[2] + m_pets[3] + m_pets[4]
                            et_sum = m_pets[5] + m_pets[6] + m_pets[7]
                            et_aut = m_pets[8] + m_pets[9] + m_pets[10]
                            et_seasons = [et_win, et_spr, et_sum, et_aut]
                            et_sea_range = max(et_seasons) - min(et_seasons)
                            f["ET_Annual_Mean"] = round(max(0.0, pet_ann), 1)
                            f["ET_Annual_Range"] = round(max(0.0, pet_range), 1)
                            f["ET_Winter_Mean"] = round(max(0.0, et_win), 1)
                            f["ET_Spring_Mean"] = round(max(0.0, et_spr), 1)
                            f["ET_Summer_Mean"] = round(max(0.0, et_sum), 1)
                            f["ET_Autumn_Mean"] = round(max(0.0, et_aut), 1)
                            f["PET_Hargreaves_Annual"] = round(max(0.0, pet_ann), 1)

                    # UNEP Aridity
                    if any("UNEP" in s for s in modules) or any("UNEP" in s for s in active_submodels):
                        pet_val = f.get("ET_Annual_Mean") if f.get("ET_Annual_Mean") is not None else f.get("PET_Hargreaves_Annual")
                        if f.get("UNEP_Aridity_Annual") is None and p_val is not None and pet_val is not None:
                            pet_f = float(pet_val)
                            f["UNEP_Aridity_Annual"] = round(float(p_val) / pet_f, 3) if pet_f > 0.01 else 0.0

                    # Water Deficit
                    if any("Water Deficit" in s for s in modules) or any("Water Deficit" in s for s in active_submodels):
                        pet_val = f.get("ET_Annual_Mean") if f.get("ET_Annual_Mean") is not None else f.get("PET_Hargreaves_Annual")
                        if f.get("Water_Deficit_Annual") is None and p_val is not None and pet_val is not None:
                            f["Water_Deficit_Annual"] = round(float(p_val) - float(pet_val), 1)

                    # Walter-Lieth Dry Months
                    if any(m in ("Dry Months", "Walter-Lieth") for m in modules) or any("Walter-Lieth" in s or "Dry Months" in s for s in active_submodels):
                        if f.get("Dry_Months_Count") is None and p_val is not None and t_val is not None:
                            p_f, t_f = float(p_val), float(t_val)
                            if p_f < 2.0 * t_f * 12.0:
                                f["Dry_Months_Count"] = int(min(12, max(1, 12.0 * (1.0 - (p_f / max(1.0, 24.0 * t_f))))))
                            else:
                                f["Dry_Months_Count"] = 0

                    # Heat Index
                    if any("Heat Index" in s for s in modules) or any("Heat Index" in s for s in active_submodels):
                        if f.get("HI_Summer_Mean") is None and t_val is not None and rh_val is not None:
                            hi = heat_index_c(float(t_val), float(rh_val))
                            if hi is not None:
                                f["HI_Summer_Mean"] = round(hi, 2)
                                f["HI_Annual_Mean"] = round(hi, 2)
                        if f.get("HI_Winter_Mean") is None and t_val is not None and rh_val is not None:
                            hw = humidex_c(float(t_val), float(rh_val))
                            if hw is not None:
                                f["HI_Winter_Mean"] = round(hw, 2)
                        if f.get("HI_Spring_Mean") is None and t_spr_val is not None and rh_spr_val is not None:
                            hs = heat_index_c(float(t_spr_val), float(rh_spr_val))
                            if hs is not None:
                                f["HI_Spring_Mean"] = round(hs, 2)
                        if f.get("HI_Autumn_Mean") is None and t_aut_val is not None and rh_aut_val is not None:
                            ha = heat_index_c(float(t_aut_val), float(rh_aut_val))
                            if ha is not None:
                                f["HI_Autumn_Mean"] = round(ha, 2)
                        if f.get("WBGT_Summer_Mean") is None and t_val is not None and rh_val is not None:
                            wb = wbgt_shade_c(float(t_val), float(rh_val))
                            if wb is not None:
                                f["WBGT_Summer_Mean"] = round(wb, 2)
                        # Opt-in monthly HI (proxies mirror the online monthly Rothfusz means)
                        for _mi, _mn in enumerate(("January", "February", "March", "April", "May", "June",
                                                  "July", "August", "September", "October", "November",
                                                  "December"), 1):
                            _hf = "HI_%s_Mean" % _mn
                            if f.get(_hf) is None:
                                _tv = f.get("T_%s_Mean" % _mn)
                                _rv = f.get("RH_%s_Mean" % _mn)
                                if _tv is not None and _rv is not None:
                                    _hi = heat_index_c(float(_tv), float(_rv))
                                    if _hi is not None:
                                        f[_hf] = round(_hi, 2)

                    # Wind Chill (offline: seasonal means stand in for monthly series)
                    if any("Wind Chill" in s for s in modules) or any("Wind Chill" in s for s in active_submodels):
                        if f.get("WC_Winter_Mean") is None and t_win_val is not None and ws_win_val is not None:
                            wc = windchill_c(float(t_win_val), float(ws_win_val))
                            if wc is not None:
                                f["WC_Winter_Mean"] = round(wc, 2)
                        if f.get("WC_Annual_Mean") is None and t_val is not None and ws_ann_val is not None:
                            wc = windchill_c(float(t_val), float(ws_ann_val))
                            if wc is not None:
                                f["WC_Annual_Mean"] = round(wc, 2)
                        # Opt-in extended seasons (proxies mirror the online seasonal means)
                        for _fld, _tseas, _wseas in (
                                ("WC_Spring_Mean", ("T_Spring_Mean", "T_SpMean"), ("W_Spd_Spring_Mean", "WSp_SpMean")),
                                ("WC_Summer_Mean", ("T_Summer_Mean", "T_SuMean"), ("W_Spd_Summer_Mean", "WSp_SuMean")),
                                ("WC_Autumn_Mean", ("T_Autumn_Mean", "T_AuMean"), ("W_Spd_Autumn_Mean", "WSp_AuMean"))):
                            if f.get(_fld) is None:
                                _tv = f.get(_tseas[0]) if f.get(_tseas[0]) is not None else f.get(_tseas[1], t_val)
                                _wv = f.get(_wseas[0]) if f.get(_wseas[0]) is not None else f.get(_wseas[1], ws_ann_val)
                                if _tv is not None and _wv is not None:
                                    _wc = windchill_c(float(_tv), float(_wv))
                                    if _wc is not None:
                                        f[_fld] = round(_wc, 2)
                        if f.get("WC_Annual_Range") is None and f.get("WC_Summer_Mean") is not None and f.get("WC_Winter_Mean") is not None:
                            f["WC_Annual_Range"] = round(abs(float(f["WC_Summer_Mean"]) - float(f["WC_Winter_Mean"])), 2)

            # 5. Create primary element feature classes in GDB for remaining modules
            admin_names = [a[0] for a in ADMIN_FIELDS]
            for mi, m in enumerate(remaining_modules):
                try:
                    arcpy.SetProgressorLabel("Offline Merge: processing module %s [%d/%d]..." % (m, mi + 1, len(remaining_modules)))
                except Exception:
                    pass
                msg("  Offline Merge: assembling module [%d/%d] '%s'..." % (mi + 1, len(remaining_modules), m))
                short = MODULE_SHORT.get(m, m)
                fc = os.path.join(gdb_path, short)
                for _inp in layer_paths:
                    try:
                        if os.path.normcase(os.path.abspath(fc)) == os.path.normcase(os.path.abspath(_inp)):
                            fc = os.path.join(gdb_path, short + "_Atlas")
                            break
                    except Exception:
                        pass
                if not arcpy.Exists(fc):
                    arcpy.management.CopyFeatures(tmp_base, fc)
                existing = set(f.name for f in arcpy.ListFields(fc))
                for name, typ, _alias in ADMIN_FIELDS:
                    if name not in existing:
                        # Main GDB: alias = field name (Latin). Arabic aliases live in the _AR copy.
                        if typ == "TEXT":
                            arcpy.management.AddField(fc, name, typ, field_length=255, field_alias=name)
                        else:
                            arcpy.management.AddField(fc, name, typ, field_alias=name)
                wanted = wanted_fields_by_module.get(m, MODULE_FIELDS.get(m, []))
                for wf in wanted:
                    if wf not in existing:
                        field_type = "LONG" if wf == "Dry_Months_Count" else "DOUBLE"
                        arcpy.management.AddField(fc, wf, field_type, field_alias=wf)
                oid_name = arcpy.Describe(fc).OIDFieldName
                with arcpy.da.UpdateCursor(fc, [oid_name, "SHAPE@"] + admin_names + wanted) as ucur:
                    for row in ucur:
                        pt_g = row[1]
                        lat_v, lon_v = None, None
                        try:
                            if pt_g:
                                p_wgs = pt_g.projectAs(wgs_sr)
                                lat_v, lon_v = float(p_wgs.centroid.Y), float(p_wgs.centroid.X)
                        except Exception:
                            pass
                        ck = (round(lat_v, 4), round(lon_v, 4)) if (lat_v is not None and lon_v is not None) else None
                        p_idx = coord_to_idx.get(ck)
                        if p_idx is None and lat_v is not None and lon_v is not None:
                            p_idx = coord_to_idx.get((round(lat_v, 3), round(lon_v, 3)))
                        if p_idx is None:
                            p_idx = oid_to_idx.get(row[0])
                        rec_f = point_records[p_idx]["fields"] if (p_idx is not None and p_idx < len(point_records)) else {}
                        d_start_v = rec_f.get("Data_Start") or (admin_meta.get("data_start") if admin_meta else 0)
                        d_end_v = rec_f.get("Data_End") or (admin_meta.get("data_end") if admin_meta else 0)
                        unit_val = rec_f.get("Measurement_Unit") or rec_f.get("Unit") or (admin_meta.get("units_by_module", {}).get(m, "") if admin_meta else "")
                        admin_vals = [
                            rec_f.get("Source_ID", row[0]),
                            lat_v,
                            lon_v,
                            d_start_v,
                            d_end_v,
                            rec_f.get("Temporal", (admin_meta.get("temporal", "Precalculated") if admin_meta else "Precalculated")),
                            rec_f.get("Interp_Meth", "Offline"),
                            rec_f.get("Cell_Size", (admin_meta.get("base_cell", 0.0) if admin_meta else 0.0)),
                            rec_f.get("Wind_Cell", (admin_meta.get("wind_cell", 0.0) if admin_meta else 0.0)),
                            unit_val,
                            rec_f.get("Status", "OK"),
                            (rec_f.get("Error_Msg", "") or "")[:255]
                        ]
                        for ai, aval in enumerate(admin_vals):
                            row[2 + ai] = aval
                        for wi, wf in enumerate(wanted):
                            val = rec_f.get(wf)
                            if val is None and wf in SHP_FIELD_MAP:
                                val = rec_f.get(SHP_FIELD_MAP[wf])
                            if val is None and wf in REV_SHP_MAP:
                                val = rec_f.get(REV_SHP_MAP[wf])
                            row[2 + len(admin_names) + wi] = val
                        ucur.updateRow(row)

                # Clean any unwanted/extraneous fields (e.g. Feat_ID, Feat_Name, old base fields)
                keep_fields = set(["OBJECTID", "Shape", "SHAPE", oid_name] + admin_names + wanted)
                to_delete = [f.name for f in arcpy.ListFields(fc) if f.name not in keep_fields and f.type not in ("OID", "Geometry")]
                if to_delete:
                    try:
                        arcpy.management.DeleteField(fc, to_delete)
                    except Exception:
                        pass

                element_fcs[m] = fc
                msg("Element layer '%s': %s" % (m, fc))



        finally:
            if tmp_is_temp:
                try:
                    arcpy.management.Delete(tmp_base)
                except Exception:
                    pass

        return element_fcs

    def _build_single_element_layer(self, tmp_projected, gdb_path, results, m,
                                    admin_meta, msg, warn, wanted_fields=None):
        """Builds one point Feature Class in GDB for a single climate element."""
        fc = os.path.join(gdb_path, MODULE_SHORT.get(m, m))
        try:
            if arcpy.Exists(fc):
                arcpy.management.Delete(fc)
            arcpy.management.CopyFeatures(tmp_projected, fc)
            existing = set(f.name for f in arcpy.ListFields(fc))
            for name, typ, _alias in ADMIN_FIELDS:
                if name not in existing:
                    # Main GDB: alias = field name (Latin). Arabic aliases live in the _AR copy.
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
                    arcpy.management.AddField(fc, f, field_type, field_alias=f)

            by_oid = dict((r.get("oid"), r) for r in results if r.get("oid") is not None)
            by_coord = {}
            for r in results:
                if r.get("lat") is not None and r.get("lon") is not None:
                    by_coord[(round(float(r["lat"]), 4), round(float(r["lon"]), 4))] = r
            results_list = list(results)
            wgs = arcpy.SpatialReference(4326)
            y0, y1, temporal = admin_meta["y0"], admin_meta["y1"], admin_meta["temporal"]
            interp, base_cell = admin_meta["interp"], admin_meta["base_cell"]
            wind_cell = admin_meta["wind_cell"]
            admin_names = [a[0] for a in ADMIN_FIELDS]

            oid_name = arcpy.Describe(fc).OIDFieldName
            with arcpy.da.UpdateCursor(fc, [oid_name, "SHAPE@"] + admin_names + wanted) as ucur:
                row_idx = 0
                for row in ucur:
                    r = None
                    try:
                        pt_geom = row[1]
                        if pt_geom:
                            pt_wgs = pt_geom.projectAs(wgs)
                            ckey = (round(pt_wgs.centroid.Y, 4), round(pt_wgs.centroid.X, 4))
                            r = by_coord.get(ckey)
                    except Exception:
                        r = None
                    if r is None:
                        r = by_oid.get(row[0])
                    if r is None and row_idx < len(results_list):
                        r = results_list[row_idx]
                    row_idx += 1

                    if r is None:
                        r = {"oid": row[0], "lat": None, "lon": None,
                             "status": "FAILED", "error": "No result",
                             "fields": {}}
                    vals = r.get("fields", {})
                    ds_val = str(admin_meta.get("data_start", str(y0)))
                    de_val = str(admin_meta.get("data_end", str(y1)))
                    unit_val = admin_meta.get("units_by_module", {}).get(m, "") if admin_meta else ""
                    admin = [r.get("oid", row[0]), r.get("lat"), r.get("lon"), ds_val, de_val, temporal,
                             interp, base_cell, wind_cell, unit_val, r.get("status", "FAILED"),
                             (r.get("error", "") or "")[:255]]
                    for i in range(len(admin)):
                        row[2 + i] = admin[i]
                    for i, f in enumerate(wanted):
                        row[2 + len(admin) + i] = vals.get(f)
                    ucur.updateRow(row)
            n = int(arcpy.GetCount_management(fc)[0])
            msg("Element layer '%s': %s (%d rows)." % (m, fc, n))
            return fc
        except Exception as ex:
            warn("Element layer '%s' failed: %s" % (m, ex))
            return None

    def _build_element_layers(self, in_points, gdb_path, out_sr, results, modules,
                              admin_meta, msg, warn, wanted_fields_by_module=None):
        """One point Feature Class per climate element, named after the element.

        Projects the input once, then per element copies it and stores admin
        fields plus that element's computed climate fields (from results).
        Returns {module: fc_path}."""
        out = {}
        # NOTE: ArcMap 10.8 cannot Project into in_memory -> use a real temp FC.
        tmp = safe_project_fc(in_points, out_sr, gdb_path, "elemproj", warn)
        tmp_is_temp = (tmp != in_points)
        try:
            for m in modules:
                wf = wanted_fields_by_module.get(m, []) if wanted_fields_by_module else None
                fc = self._build_single_element_layer(tmp, gdb_path, results, m,
                                                      admin_meta, msg, warn, wanted_fields=wf)
                if fc:
                    out[m] = fc
        finally:
            if tmp_is_temp:
                try:
                    arcpy.management.Delete(tmp)
                except Exception:
                    pass
        return out

    def _interpolate_all(self, master_fc, modules, paths, cell, method, mask, msg, warn,
                         iopts=None, kopts=None, is_geo=False,
                         purge=True, scratch=None, focal=None, source_by_module=None,
                          wanted_fields_by_module=None, reclass_opts=None,
                          raster_mask=None, raster_timings=None, monthly_enabled=False,
                          monthly_ranges_on=False):
        from arcpy.sa import ExtractByMask
        out_ws = os.path.dirname(paths["vec"])
        if scratch is None:
            scratch = os.path.join(out_ws, "_scratch")
        makedirs_ok(scratch)
        try:
            arcpy.env.scratchWorkspace = scratch
        except Exception:
            pass
        focal = focal or {"apply": False, "stat": "MEAN", "size": 3}
        if reclass_opts is None:
            reclass_opts = {"enable": False, "nclass": 7, "method": "Natural Breaks (Jenks)"}
        reclass_on = bool(reclass_opts.get("enable", False))
        reclass_nclass = int(reclass_opts.get("nclass", 7))
        reclass_method = str(reclass_opts.get("method", "Natural Breaks (Jenks)"))
        msg("Raw float rasters | LZW: enforced | purge temps: %s | focal: %s | reclass: %s" % (
            purge,
            ("OFF" if not focal["apply"] else "%s %dx%d" % (focal["stat"], focal["size"], focal["size"])),
            ("%s (%d classes)" % (reclass_method, reclass_nclass)) if reclass_on else "OFF"))
        registry = []
        todo = []
        for m in modules:
            if wanted_fields_by_module is not None:
                flist = wanted_fields_by_module.get(m, [])
            else:
                flist = MODULE_FIELDS.get(m, [])
            for f in flist:
                # Monthly climatology surfaces are interpolated only when the
                # monthly option is enabled (multi-year span, >= 2 years).
                # Monthly *ranges* additionally pass with the independent
                # Monthly Ranges toggle (opt-in, default OFF).
                if is_monthly_field(f) and not monthly_enabled:
                    _is_mrange = f.endswith("_Range") and any(
                        f.endswith("_%s_Range" % _mn) for _mn in MONTH_NAMES_EN)
                    if not (_is_mrange and monthly_ranges_on):
                        continue
                todo.append((m, f))
        # IDW max distance is entered in metres: convert for geographic output
        if iopts and iopts.get("maxdist") and is_geo and float(iopts["maxdist"]) > 1.0:
            iopts = dict(iopts, maxdist=float(iopts["maxdist"]) / 111320.0)
            warn("IDW Maximum Distance converted to degrees: %.5f." % iopts["maxdist"])
        arcpy.SetProgressor("step", "Interpolating rasters ...", 0, len(todo), 1)
        # --- valid-value counts: one scan per source point layer ---
        # The same scan also collects the global min/max of the 12 monthly
        # fields per element, so all Month/ rasters of one element share one
        # unified color stretch (true visual comparison across months).
        msg("Counting valid values ...")
        counts = {}
        _src_of = source_by_module or {}
        _mod_of_field = {}
        for _m, _f in todo:
            _mod_of_field.setdefault(_f, _m)
        monthly_minmax = {}
        try:
            _by_src = {}
            for _m, _f in todo:
                _by_src.setdefault(_src_of.get(_m, master_fc), []).append(_f)
            for _s, _fs in _by_src.items():
                if _s is None or not arcpy.Exists(_s):
                    continue
                with arcpy.da.SearchCursor(_s, _fs) as _cur:
                    for _row in _cur:
                        for _f, _v in zip(_fs, _row):
                            if _v is not None:
                                counts[_f] = counts.get(_f, 0) + 1
                                if is_monthly_field(_f):
                                    try:
                                        _fv = float(_v)
                                    except Exception:
                                        continue
                                    _grp = monthly_group_key(_mod_of_field.get(_f), _f)
                                    _mm = monthly_minmax.get(_grp)
                                    if _mm is None:
                                        monthly_minmax[_grp] = [_fv, _fv]
                                    else:
                                        if _fv < _mm[0]:
                                            _mm[0] = _fv
                                        if _fv > _mm[1]:
                                            _mm[1] = _fv
            for _grp, (_gmin, _gmax) in monthly_minmax.items():
                _glabel = _grp[0] + ("/" + _grp[1] if _grp[1] else "")
                msg("Monthly unified stretch [%s]: global %.4g .. %.4g over 12 months." % (_glabel, _gmin, _gmax))
        except Exception as ex:
            warn("Fast counting failed, falling back to per-field counts: %s" % ex)
            counts = {}
        i = 0
        for module, field in todo:
            i += 1
            arcpy.SetProgressorPosition(i)
            arcpy.SetProgressorLabel("Interpolating raster [%d/%d]: %s (%s)..." % (i, len(todo), field, module))
            t_fld_start = time.time()
            msg("  -> [%d/%d] Processing column: %s (%s)..." % (i, len(todo), field, module))
            try:
                # NOTE: each element interpolates from its own point layer
                src_fc = (source_by_module or {}).get(module, master_fc)
                if src_fc is None or not arcpy.Exists(src_fc):
                    warn("Skipping raster %s: no source point layer." % field)
                    continue
                available_fields = [f.name for f in arcpy.ListFields(src_fc)]
                actual_field = field
                if actual_field not in available_fields:
                    shp_alias = SHP_FIELD_MAP.get(field)
                    if shp_alias and shp_alias in available_fields:
                        actual_field = shp_alias
                    else:
                        warn("Skipping raster %s: field not found in point layer." % field)
                        continue
                if actual_field in counts:
                    n_valid = counts[actual_field]
                elif field in counts:
                    n_valid = counts[field]
                else:
                    n_valid = 0
                    with arcpy.da.SearchCursor(src_fc, [actual_field]) as cur:
                        for row in cur:
                            if row[0] is not None:
                                n_valid += 1
                if n_valid < 3:
                    warn("Skipping raster %s: only %d valid points." % (field, n_valid))
                    continue
                lyr = "pwr_atlas_interp"
                try:
                    arcpy.management.Delete(lyr)
                except Exception:
                    pass
                arcpy.management.MakeFeatureLayer(
                    src_fc, lyr, "%s IS NOT NULL" % arcpy.AddFieldDelimiters(src_fc, actual_field))
                try:
                    arcpy.ClearEnvironment("mask")
                    if mask and arcpy.Exists(mask):
                        arcpy.env.extent = mask
                    else:
                        arcpy.ClearEnvironment("extent")
                    arcpy.env.parallelProcessingFactor = "0"
                except Exception:
                    pass
                # Circular directions must NOT be interpolated linearly
                # (mean of 350+10=180 instead of 0). Use sin/cos U/V method.
                is_dir = field.startswith("W_Dir")
                if is_dir:
                    try:
                        try:
                            arcpy.management.Delete(lyr)
                        except Exception:
                            pass
                        surf = self._interp_direction_uv(
                            src_fc, actual_field, cell, method, iopts, kopts, warn)
                        msg("Raster %s: circular U/V (sin/cos + atan2) interpolation." % field)
                    except Exception as ex_uv:
                        warn("Direction U/V failed for %s (%s); falling back to linear." % (field, ex_uv))
                        try:
                            arcpy.management.Delete(lyr)
                        except Exception:
                            pass
                        arcpy.management.MakeFeatureLayer(
                            src_fc, lyr, "%s IS NOT NULL" % arcpy.AddFieldDelimiters(src_fc, actual_field))
                        surf = self._interp_surface(lyr, actual_field, cell, method, iopts, kopts)
                else:
                    surf = self._interp_surface(lyr, actual_field, cell, method, iopts, kopts)
                rp, lp = self._raster_paths(out_ws, module, field)
                # --- clip to final extent in memory ---
                # Prefer pre-rasterized mask (10-50x faster than vector mask)
                effective_mask = raster_mask if (raster_mask and arcpy.Exists(raster_mask)) else mask
                if effective_mask:
                    try:
                        clipped = ExtractByMask(surf, effective_mask)
                    except Exception:
                        # Fallback 1: try vector mask if raster mask failed
                        if effective_mask != mask and mask:
                            try:
                                clipped = ExtractByMask(surf, mask)
                            except Exception:
                                clipped = surf
                        else:
                            # Fallback 2: save to scratch then mask
                            tmpu = os.path.join(scratch, "u_" + field + ".tif")
                            try:
                                surf.save(tmpu)
                                clipped = ExtractByMask(tmpu, effective_mask)
                            except Exception:
                                clipped = surf
                            finally:
                                try:
                                    if arcpy.Exists(tmpu):
                                        arcpy.management.Delete(tmpu)
                                except Exception:
                                    pass
                else:
                    clipped = surf

                # --- focal smoothing if requested ---
                if focal["apply"]:
                    from arcpy.sa import FocalStatistics, NbrRectangle
                    src_raster = FocalStatistics(clipped,
                                    NbrRectangle(focal["size"], focal["size"], "CELL"),
                                    focal["stat"])
                else:
                    src_raster = clipped

                # --- raw float save with maximum LZW block compression ---
                makedirs_ok(os.path.dirname(rp))
                try:
                    arcpy.env.parallelProcessingFactor = "0"
                except Exception:
                    pass
                try:
                    arcpy.management.CopyRaster(src_raster, rp, nodata_value="-3.4028235e+38")
                except Exception:
                    try:
                        arcpy.Raster(src_raster).save(rp)
                    except Exception:
                        src_raster.save(rp)

                try:
                    arcpy.management.CalculateStatistics(rp)
                except Exception:
                    pass

                t_fld_dur = time.time() - t_fld_start
                msg("     [OK] Successfully saved: %s (in %.1f seconds)" % (os.path.basename(rp), t_fld_dur))
                if raster_timings is not None:
                    raster_timings[field] = (module, os.path.basename(rp), t_fld_dur)

                # Immediately release raster memory and dataset locks before next iteration
                try:
                    del surf
                except Exception:
                    pass
                try:
                    del clipped
                except Exception:
                    pass
                try:
                    del src_raster
                except Exception:
                    pass
                try:
                    arcpy.management.Delete(lyr)
                except Exception:
                    pass
                try:
                    import gc
                    gc.collect()
                except Exception:
                    pass

                colors = self._colors_for(module, field)

                if reclass_on:
                    nclass = 5 if (module == "UV Index" and reclass_nclass == 7) else reclass_nclass
                    interp_colors = interpolate_colors(colors, nclass)
                    fixed_breaks = None
                    if is_monthly_field(field):
                        _grp = monthly_group_key(module, field)
                        if _grp in monthly_minmax:
                            _gmin, _gmax = monthly_minmax[_grp]
                            try:
                                fixed_breaks = equal_interval_breaks(_gmin, _gmax, nclass)
                                msg("Raster %s: unified monthly stretch (global %.4g..%.4g)." % (field, _gmin, _gmax))
                            except Exception:
                                fixed_breaks = None
                    cls_rp, clr_path, breaks = self._build_display(
                        rp, field, module, interp_colors, nclass, reclass_method, msg, warn, purge=purge,
                        fixed_breaks=fixed_breaks)
                    # No .lyr output: registry keeps the raster path only.
                    registry.append((field, rp, None, module, interp_colors, nclass))
                    msg("Raster: %s [raw float, LZW] + %s [%d classes, %s]" % (
                        rp, os.path.basename(cls_rp) if cls_rp else "", nclass, reclass_method))
                else:
                    nclass = len(colors)
                    registry.append((field, rp, None, module, colors, nclass))
                    msg("Raster: %s [raw float, LZW, continuous]" % rp)
            except Exception as ex:
                warn("Raster %s failed: %s" % (field, ex))
        arcpy.ResetProgressor()
        return registry

    def _make_lyr(self, raster_path, lyr_path, field, module, colors, nclass, method, msg, warn,
                  breaks=None, src_continuous=None, is_classified=True):
        """Create ArcMap .lyr pointing at the raster.
        When is_classified is True: points to classified display raster (<field>_cls.tif) with embedded colormap.
        When is_classified is False: points directly to the continuous float GeoTIFF (<field>.tif).
        """
        info = FIELD_BY_NAME.get(field, (field, field, "", "", module, "", "", "", "", "", ""))
        try:
            if arcpy.Exists(lyr_path):
                arcpy.management.Delete(lyr_path)
        except Exception:
            pass
        lyr_name = field  # layer name = raster/field name in the TOC
        try:
            arcpy.management.Delete(lyr_name)
        except Exception:
            pass
        try:
            arcpy.management.MakeRasterLayer(raster_path, lyr_name)
        except Exception as ex:
            warn("MakeRasterLayer failed for %s: %s" % (field, ex))
            return

        if is_classified:
            if not breaks:
                try:
                    _mn = float(arcpy.GetRasterProperties_management(raster_path, "MINIMUM")[0])
                    _mx = float(arcpy.GetRasterProperties_management(raster_path, "MAXIMUM")[0])
                except Exception:
                    _mn, _mx = 0.0, 1.0
                breaks = equal_interval_breaks(_mn, _mx, nclass) or [_mn, _mx]
            disp_note = ("Display: classified %d-class raster (%s, descending, zone 1 = highest) "
                          "with embedded colormap (raw float: %s). "
                          % (nclass, method, os.path.basename(src_continuous or raster_path)))
            class_lines = []
            for k in range(1, nclass + 1):
                _lo, _hi = breaks[nclass - k], breaks[nclass - k + 1]
                _ci = nclass - k if (nclass - k) < len(colors) else len(colors) - 1
                class_lines.append("Class %d: %.4g - %.4g  color %s" % (k, _lo, _hi, colors[_ci]))
            desc_text = ("%s | %s | Unit: %s | Period: %s | Statistic: %s | "
                         "Method: %s (%d classes) | Source: NASA POWER. %s"
                         % (info[1], info[2], info[7], info[5], info[6],
                            method, nclass, disp_note))
            credits_text = ("NASA POWER (power.larc.nasa.gov), %s. Gridded/modelled estimates, "
                            "not station measurements. Created %s. Classification (%s): %s"
                            % (TOOL_VERSION, now_str(), method, " ; ".join(class_lines)))
            class_field = method
        else:
            disp_note = ("Display: continuous floating-point surface raster (%s). "
                         % os.path.basename(raster_path))
            class_lines = []
            if breaks and len(breaks) >= 2:
                class_lines.append("Range: %.4g to %.4g %s" % (breaks[0], breaks[-1], info[7]))
            desc_text = ("%s | %s | Unit: %s | Period: %s | Statistic: %s | "
                         "Method: %s (Continuous Float) | Source: NASA POWER. %s"
                         % (info[1], info[2], info[7], info[5], info[6],
                            method, disp_note))
            credits_text = ("NASA POWER (power.larc.nasa.gov), %s. Gridded/modelled estimates, "
                            "not station measurements. Created %s. Continuous floating-point surface."
                            % (TOOL_VERSION, now_str()))
            class_field = "Continuous"

        try:
            arcpy.management.SaveToLayerFile(lyr_name, lyr_path)
            try:
                lyr = arcpy.mapping.Layer(lyr_path)
                lyr.description = desc_text
                lyr.credits = credits_text
                lyr.save()
            except Exception as ex:
                warn("Layer metadata for %s not fully embedded: %s" % (field, ex))
            try:
                _lyr2 = arcpy.mapping.Layer(lyr_path)
                _lyr2.replaceDataSource(
                    os.path.dirname(raster_path), "RASTER_WORKSPACE",
                    os.path.basename(raster_path))
                _lyr2.save()
            except Exception as ex:
                warn("Layer datasource relink for %s skipped: %s" % (field, ex))
            try:
                meta = {
                    "variable_EN": info[1], "variable_AR": info[2], "unit": info[7],
                    "period": info[5], "statistic": info[6], "method": method,
                    "classification": class_field, "classes": (nclass if is_classified else None),
                    "breaks": breaks, "colors": (colors if is_classified else None),
                    "class_labels": class_lines,
                    "display_raster": os.path.basename(raster_path),
                    "source_raster": os.path.basename(src_continuous or raster_path),
                    "data_min": (breaks[0] if breaks else None),
                    "data_max": (breaks[-1] if breaks else None),
                    "source": "NASA POWER", "created": now_str(),
                    "raster": os.path.basename(raster_path),
                    "arcmap_note": ("Opens with embedded colormap colors. Raw float values stay in the source_raster GeoTIFF."
                                    if is_classified else "Continuous floating-point surface raster."),
                }
                _s = json.dumps(meta, ensure_ascii=False, indent=2)
                if not isinstance(_s, bytes):
                    _s = _s.encode("utf-8")
                with open(lyr_path + ".json", "wb") as fh:
                    fh.write(_s)
            except Exception as ex:
                warn("Sidecar json for %s failed: %s" % (field, ex))
            msg("Layer: %s" % lyr_path)
        except Exception as ex:
            warn("Layer file for %s failed: %s" % (field, ex))
        finally:
            try:
                arcpy.management.Delete(lyr_name)
            except Exception:
                pass

    def _build_wind_vectors(self, gdb_path, paths, registry, extent_fc, mask, out_sr,
                            wind_cell, msg, warn, export_shp=True):
        """Thinned fishnet points sampling speed+direction rasters -> 5 vector FCs."""
        spd = {}
        drc = {}
        for item in registry:
            f, rp = item[0], item[1]
            if f.startswith("W_Spd"):
                spd[f] = rp
            elif f.startswith("W_Dir"):
                drc[f] = rp
        if not spd or not drc:
            warn("Wind vectors skipped: speed/direction rasters missing.")
            return []
        if mask:
            ext = arcpy.Describe(mask).extent
        elif extent_fc is not None and arcpy.Exists(extent_fc):
            ext = arcpy.Describe(extent_fc).extent
        else:
            warn("Wind vectors skipped: no mask and no Wind point layer for extent.")
            return []
        out_ws = os.path.dirname(paths["vec"])
        fish = "in_memory/wind_fishnet"
        for o in (fish, fish + "_label", "in_memory/wind_clip", "in_memory/wind_proj"):
            try:
                arcpy.management.Delete(o)
            except Exception:
                pass
        origin = "%s %s" % (ext.XMin, ext.YMin)
        yaxis = "%s %s" % (ext.XMin, ext.YMin + 10)
        corner = "%s %s" % (ext.XMax, ext.YMax)
        arcpy.management.CreateFishnet(fish, origin, yaxis, float(wind_cell), float(wind_cell),
                                       "", "", corner, "LABELS", None, "POLYGON")
        fish_pts = fish + "_label"
        if mask:
            try:
                arcpy.analysis.Clip(fish_pts, mask, "in_memory/wind_clip")
                fish_pts = "in_memory/wind_clip"
            except Exception as ex:
                warn("Wind fishnet clip failed: %s" % ex)
        try:
            proj = safe_project_fc(fish_pts, out_sr, gdb_path, "windproj", warn)
            if proj != fish_pts:
                fish_pts = proj
        except Exception:
            pass
        periods = [("Annual", "W_Spd_Annual_Mean", "W_Dir_Annual_Mean"),
                   ("Winter", "W_Spd_Winter_Mean", "W_Dir_Winter_Mean"),
                   ("Spring", "W_Spd_Spring_Mean", "W_Dir_Spring_Mean"),
                   ("Summer", "W_Spd_Summer_Mean", "W_Dir_Summer_Mean"),
                   ("Autumn", "W_Spd_Autumn_Mean", "W_Dir_Autumn_Mean")]
        created = []
        vdir = os.path.join(out_ws, "05_Wind", "Direction", "Vector_Points")
        if export_shp:
            makedirs_ok(vdir)
        for suffix, fs, fd in periods:
            if fs not in spd or fd not in drc:
                continue
            fc = os.path.join(gdb_path, "Wind_Vector_%s" % suffix)
            try:
                if arcpy.Exists(fc):
                    arcpy.management.Delete(fc)
                arcpy.management.CopyFeatures(fish_pts, fc)
                arcpy.sa.ExtractMultiValuesToPoints(fc, [[spd[fs], "Wind_Speed"], [drc[fd], "Wind_Dir"]])
                for fn, typ in [("Arrow_Angle", "DOUBLE"), ("Arrow_Size", "DOUBLE"), ("Period", "TEXT")]:
                    try:
                        if typ == "TEXT":
                            arcpy.management.AddField(fc, fn, typ, field_length=20)
                        else:
                            arcpy.management.AddField(fc, fn, typ)
                    except Exception:
                        pass
                with arcpy.da.UpdateCursor(fc, ["Wind_Dir", "Wind_Speed", "Arrow_Angle", "Arrow_Size", "Period"]) as cur:
                    for row in cur:
                        wd, ws = row[0], row[1]
                        try:
                            row[2] = (float(wd) + 180.0) % 360.0 if wd is not None else None
                        except Exception:
                            row[2] = None
                        try:
                            row[3] = float(ws) if ws is not None else None
                        except Exception:
                            row[3] = None
                        row[4] = suffix
                        cur.updateRow(row)
                try:
                    if export_shp:
                        shp = os.path.join(vdir, "Wind_Vector_%s.shp" % suffix)
                        if arcpy.Exists(shp):
                            arcpy.management.Delete(shp)
                        arcpy.conversion.FeatureClassToShapefile([fc], vdir)
                except Exception as ex:
                    warn("Wind shapefile %s failed: %s" % (suffix, ex))
                created.append(fc)
                msg("Wind vectors: %s" % fc)
            except Exception as ex:
                warn("Wind vectors %s failed: %s" % (suffix, ex))
        for o in (fish, fish + "_label", "in_memory/wind_clip",
                  os.path.join(gdb_path, "tmp_windproj")):
            try:
                arcpy.management.Delete(o)
            except Exception:
                pass
        return created

    def _build_isobars(self, gdb_path, registry, msg, warn, step=None, mask=None):
        from arcpy.sa import Contour
        mapping = {"PSL_Annual_Mean": "Isobars_PSL_Annual_Mean",
                   "PS_Annual_Mean": "Isobars_PS_Annual_Mean",
                   "PSL_Winter_Mean": "Isobars_PSL_Winter_Mean",
                   "PSL_Spring_Mean": "Isobars_PSL_Spring_Mean",
                   "PSL_Summer_Mean": "Isobars_PSL_Summer_Mean",
                   "PSL_Autumn_Mean": "Isobars_PSL_Autumn_Mean",
                   "PS_Winter_Mean": "Isobars_PS_Winter_Mean",
                   "PS_Spring_Mean": "Isobars_PS_Spring_Mean",
                   "PS_Summer_Mean": "Isobars_PS_Summer_Mean",
                   "PS_Autumn_Mean": "Isobars_PS_Autumn_Mean"}
        lut = dict((item[0], item[1]) for item in registry)
        use_mask = mask if (mask and arcpy.Exists(mask)) else None
        for field, fcname in mapping.items():
            if field not in lut:
                continue
            try:
                if step:
                    interval = float(step)
                else:
                    rmin = float(arcpy.GetRasterProperties_management(lut[field], "MINIMUM")[0])
                    rmax = float(arcpy.GetRasterProperties_management(lut[field], "MAXIMUM")[0])
                    interval = max((rmax - rmin) / 10.0, 0.5)
                out = os.path.join(gdb_path, fcname)
                if arcpy.Exists(out):
                    arcpy.management.Delete(out)
                Contour(lut[field], out, interval)
                msg("Isobars: %s (interval %.2f hPa)" % (out, interval))
                if use_mask:
                    raw = out + "_raw"
                    try:
                        if arcpy.Exists(raw):
                            arcpy.management.Delete(raw)
                        arcpy.management.Rename(out, os.path.basename(raw))
                        arcpy.Clip_analysis(raw, use_mask, out)
                        arcpy.management.Delete(raw)
                        msg("Isobars clipped to mask: %s" % fcname)
                    except Exception as cex:
                        warn("Isobar clip %s failed (%s); keeping unclipped." % (field, cex))
                        try:
                            if not arcpy.Exists(out) and arcpy.Exists(raw):
                                arcpy.management.Rename(raw, os.path.basename(out))
                        except Exception:
                            pass
            except Exception as ex:
                warn("Isobar %s failed: %s" % (field, ex))

    def _build_arabic_db(self, gdb_path, element_fcs, msg, warn):
        """Copies element point layers into <base>_AR.gdb with Arabic field aliases.

        Field NAMES stay English (identical to the main GDB) so the copy remains
        reusable as offline input - only aliases are Arabic, letting Arabic users
        read and understand the columns. Returns the AR gdb path (or None)."""
        try:
            base = os.path.basename(gdb_path)
            if base.lower().endswith(".gdb"):
                ar_name = base[:-4] + "_AR.gdb"
            else:
                ar_name = base + "_AR.gdb"
            ar_gdb = os.path.join(os.path.dirname(gdb_path), ar_name)
            if not arcpy.Exists(ar_gdb):
                arcpy.CreateFileGDB_management(os.path.dirname(gdb_path), ar_name)
                msg("Arabic DB: created %s" % ar_name)
            ar_map = dict((r[0], r[2]) for r in FIELD_DEFS)
            ar_map.update(ADMIN_AR)
            n_fc, n_alias = 0, 0
            for _m, fc in (element_fcs or {}).items():
                if not fc or not arcpy.Exists(fc):
                    continue
                out_fc = os.path.join(ar_gdb, os.path.basename(fc))
                try:
                    if arcpy.Exists(out_fc):
                        arcpy.management.Delete(out_fc)
                    arcpy.CopyFeatures_management(fc, out_fc)
                    n_fc += 1
                    for f in arcpy.ListFields(out_fc):
                        if f.type in ("OID", "Geometry"):
                            continue
                        alias = ar_map.get(f.name, f.name)
                        try:
                            arcpy.management.AlterField_management(
                                out_fc, f.name, new_field_alias=alias)
                            n_alias += 1
                        except Exception:
                            pass
                except Exception as fex:
                    warn("Arabic DB layer %s failed: %s" % (os.path.basename(fc), fex))
            msg("Arabic DB: %d layers, %d Arabic aliases -> %s" % (n_fc, n_alias, ar_gdb))
            return ar_gdb
        except Exception as ex:
            warn("Arabic DB failed: %s" % ex)
            return None

    def _write_dictionaries(self, vec_dir, modules, msg, provider="NASA POWER API", wanted_fields_by_module=None):
        rows = metadata_rows_for_modules(modules, wanted_fields_by_module=wanted_fields_by_module)
        for r in rows:
            if r["Field_Name"] == "R_Annual_Mean":
                r["Notes"] = "Climatological annual mean (mean of per-year sums)"
            if r["Field_Name"] == "R_Annual_Range":
                r["Notes"] = "Difference between wettest and driest climatological months"
            if r["Field_Name"] == "Td_Annual_Range":
                r["Notes"] = "Difference between highest and lowest monthly dew point"
            if r["Field_Name"].startswith("HI_"):
                r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                    "Needs humidity (RH2M); NoData when unavailable"
            if r["Field_Name"] in ("WC_Winter_Mean", "WC_Annual_Mean", "WC_Spring_Mean", "WC_Summer_Mean", "WC_Autumn_Mean", "WC_Annual_Range"):
                r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                    "Needs 10-m wind (WS10M); equals air T when T>10C or calm"
            if r["Field_Name"] in ("T_Annual_Trend_Decade", "R_Annual_Trend_Decade"):
                r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                    "Least-squares/decade; NoData when <8 complete years"
            if "_Anom" in r["Field_Name"]:
                r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                    "Recent (last 10 complete yrs) minus WMO 1991-2020 normal"
            if r["Field_Name"].startswith("W_Dir"):
                r["Notes"] = "Circular (vector) mean, not arithmetic mean of angles"
            if r["Field_Name"] == "Sol_Annual_Total":
                r["Notes"] = "Mean annual accumulated energy (kWh/m2/year)"
            if provider.startswith("Open-Meteo") or "ERA5" in provider:
                r["Source"] = "Open-Meteo ERA5"
            elif provider.startswith("Hybrid"):
                r["Source"] = "Hybrid: NOAA ISD Ground Stations + NASA/ERA5 Gap-Filling"
            elif provider.startswith("NOAA"):
                r["Source"] = "NOAA ISD / GHCN Direct Station Ground Archive"
            else:
                r["Source"] = "NASA POWER"
        if provider.startswith("Open-Meteo") or "ERA5" in provider:
            # provider-specific statistic documentation (same table, adapted notes)
            for r in rows:
                if r["Field_Name"].startswith("UV_"):
                    r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                        "Open-Meteo: mean of daily maximum (uv_index_max, ERA5)"
                if r["Field_Name"].startswith("W_Spd"):
                    r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                        "Open-Meteo: mean of hourly wind_speed_10m (ERA5)"
                if r["Field_Name"].startswith(("PSL_", "PS_", "RH_", "Cld_")):
                    r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                        "Open-Meteo: mean of hourly aggregates (ERA5)"
                if r["Field_Name"].startswith("R_"):
                    r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                        "Open-Meteo: precipitation_sum daily totals (mm, ERA5)"
        elif provider.startswith("Hybrid"):
            for r in rows:
                r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                    "Hybrid: Ground observation with satellite/reanalysis gap-filling"
        elif provider.startswith("NOAA"):
            for r in rows:
                r["Notes"] = ((r["Notes"] + "; ") if r["Notes"] else "") + \
                    "NOAA NCEI ISD Ground station in-situ observation record"
        cols = ["Field_Name", "Full_Name_EN", "Name_AR", "NASA_Code", "Module", "Period",
                "Statistic", "Unit", "Description_AR", "Description_EN", "Calculation",
                "Source", "Notes"]
        p1_xls = os.path.join(vec_dir, "Metadata_Dictionary.xls")
        write_excel_file(p1_xls, cols, [[r[c] for c in cols] for r in rows], sheet_name="Metadata", rtl=False)
        p1_csv = os.path.join(vec_dir, "Metadata_Dictionary.csv")
        write_csv(p1_csv, cols, [[r[c] for c in cols] for r in rows])
        msg("Dictionary Excel & CSV: %s (%d fields)" % (p1_xls, len(rows)))

        ar_cols = ["Field_Name", "Name_AR", "Unit", "Description_AR", "Module", "Period"]
        p2_xls = os.path.join(vec_dir, "Field_Dictionary_Arabic.xls")
        write_excel_file(p2_xls, ar_cols,
                         [[r["Field_Name"], r["Name_AR"], r["Unit"],
                           r["Description_AR"], r["Module"], r["Period"]] for r in rows], sheet_name="Arabic_Dictionary", rtl=True)
        p2_csv = os.path.join(vec_dir, "Field_Dictionary_Arabic.csv")
        write_csv(p2_csv, ar_cols,
                  [[r["Field_Name"], r["Name_AR"], r["Unit"],
                    r["Description_AR"], r["Module"], r["Period"]] for r in rows])
        msg("Dictionary Excel & CSV (RTL): %s" % p2_xls)

    def _run_qa(self, element_fcs, paths, modules, registry, results, msg, warn, wanted_fields_by_module=None):
        checks = []

        def _add(name, ok, detail=""):
            checks.append((name, bool(ok), detail))
            if ok:
                msg("QA PASS: %s %s" % (name, detail))
            else:
                warn("QA FAIL: %s %s" % (name, detail))

        def _elfc(m):
            fc = (element_fcs or {}).get(m)
            if fc and arcpy.Exists(fc):
                return fc
            return None

        try:
            _counts = {}
            for m in modules:
                _fc = _elfc(m)
                _counts[m] = int(arcpy.GetCount_management(_fc)[0]) if _fc else -1
            _ok = all(v >= 0 for v in _counts.values()) and len(set(_counts.values())) == 1
            _add("element layers", _ok, "counts=%s" % _counts)
        except Exception as ex:
            _add("element layers", False, str(ex))
        try:
            _admin = [a[0] for a in ADMIN_FIELDS]
            _miss, _total = [], 0
            for m in modules:
                _fc = _elfc(m)
                if _fc is None:
                    _miss.append(m + ":layer")
                    continue
                _names = set(f.name for f in arcpy.ListFields(_fc))
                m_wanted = (wanted_fields_by_module or {}).get(m, MODULE_FIELDS.get(m, []))
                for n in _admin + m_wanted:
                    _total += 1
                    if n not in _names:
                        _miss.append(n)
            _add("field names present", not _miss, "(%d/%d, missing=%s)"
                 % (_total - len(_miss), _total, _miss[:8]))
            _allw = [f for m in modules for f in (wanted_fields_by_module or {}).get(m, MODULE_FIELDS.get(m, []))]
            _add("shapefile name length<=10 (or mapped)",
                 all(len(n) <= 10 or n in SHP_FIELD_MAP for n in _allw),
                 "mapped=%d fields" % len(SHP_FIELD_MAP))
        except Exception as ex:
            _add("field names present", False, str(ex))
        try:
            _req = [c for c in REQUIRED_COLUMNS if c != "OBJECTID"]
            _miss = []
            for m in modules:
                _fc = _elfc(m)
                if _fc is None:
                    _miss.append(m + ":layer")
                    continue
                _have = set(f.name for f in arcpy.ListFields(_fc))
                m_wanted = (wanted_fields_by_module or {}).get(m, MODULE_FIELDS.get(m, []))
                for c in _req:
                    if c in [a[0] for a in ADMIN_FIELDS] or c in m_wanted:
                        if c not in _have:
                            _miss.append(c)
            _add("required columns present", not _miss, "missing=%s" % _miss[:8])
        except Exception as ex:
            _add("required columns present", False, str(ex))
        try:
            bad = 0
            for m in modules:
                _fc = _elfc(m)
                if _fc is None:
                    continue
                m_wanted = (wanted_fields_by_module or {}).get(m, MODULE_FIELDS.get(m, []))
                if not m_wanted:
                    continue
                with arcpy.da.SearchCursor(_fc, m_wanted) as cur:
                    for row in cur:
                        for v in row:
                            if v is not None and abs(float(v) + 999.0) < 1e-9:
                                bad += 1
            _add("no -999 sentinel values", bad == 0, "(bad=%d)" % bad)
        except Exception as ex:
            _add("no -999 sentinel values", False, str(ex))
        _add("Metadata_Dictionary.xls",
             os.path.isfile(os.path.join(paths["vec"], "Metadata_Dictionary.xls")))
        _add("Field_Dictionary_Arabic.xls",
             os.path.isfile(os.path.join(paths["vec"], "Field_Dictionary_Arabic.xls")))
        missing = [item[0] for item in registry if not os.path.isfile(item[1])]
        _add("tif per raster", len(missing) == 0,
             "(%d/%d, missing=%s)" % (len(registry) - len(missing), len(registry), missing[:5]))
        mods_with_r = set(item[3] for item in registry)
        _add("outputs match selected modules", not (mods_with_r - set(modules)),
             "raster modules=%s" % sorted(mods_with_r))
        try:
            ranges = [("Temperature", "T_Annual_Mean", (-30, 45)),
                      ("Temperature", "HI_Annual_Mean", (-30, 60)),
                      ("Temperature", "HI_Winter_Mean", (-30, 60)),
                      ("Temperature", "HI_Spring_Mean", (-30, 60)),
                      ("Temperature", "HI_Autumn_Mean", (-30, 60)),
                      ("Heat Index", "HI_July_Mean", (-30, 60)),
                      ("Temperature", "Td_Summer_Mean", (-30, 40)),
                      ("Climate_Models", "WC_Winter_Mean", (-50, 15)),
                      ("Climate_Models", "WC_Spring_Mean", (-50, 30)),
                      ("Climate_Models", "WC_Summer_Mean", (-50, 40)),
                      ("Climate_Models", "WC_Autumn_Mean", (-50, 30)),
                      ("Climate_Models", "WC_Annual_Range", (0, 60)),
                      ("Temperature", "WBGT_Summer_Mean", (-30, 60)),
                      ("Relative Humidity", "RH_Annual_Mean", (0, 100)),
                      ("Cloud Cover", "Cld_Annual_Mean", (0, 100)),
                      ("Sea Level Pressure", "PSL_Annual_Mean", (870, 1050)),
                      ("Surface Pressure", "PS_Annual_Mean", (870, 1050)),
                      ("Land Surface Temperature", "LST_Annual_Mean", (-30, 75)),
                      ("Land Surface Temperature", "LST_minus_T_Annual", (-20, 30)),
                      ("Land Surface Temperature", "LST_minus_T_Winter", (-20, 30)),
                      ("Land Surface Temperature", "LST_minus_T_Spring", (-20, 30)),
                      ("Land Surface Temperature", "LST_minus_T_Summer", (-20, 30)),
                      ("Land Surface Temperature", "LST_minus_T_Autumn", (-20, 30))]
            for _mname in ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"):
                ranges.append(("Land Surface Temperature", "LST_minus_T_%s" % _mname, (-20, 30)))
            notes = []
            ok_all = True
            for _m, fld, lim in ranges:
                if _m not in modules:
                    continue
                _fc = _elfc(_m)
                if _fc is None:
                    continue
                if fld not in set(f.name for f in arcpy.ListFields(_fc)):
                    continue
                with arcpy.da.SearchCursor(_fc, [fld]) as cur:
                    vals = [r[0] for r in cur if r[0] is not None]
                if vals:
                    badv = [v for v in vals if not (lim[0] <= v <= lim[1])]
                    if badv:
                        ok_all = False
                        notes.append("%s %d out of range" % (fld, len(badv)))
            _add("value ranges sane", ok_all, "; ".join(notes))
        except Exception as ex:
            _add("value ranges sane", False, str(ex))
        return checks

    def _write_log(self, vec_dir, info):
        p = os.path.join(vec_dir, "Processing_Log.txt")
        with open_utf8(p, "w") as fh:
            fh.write(u"POWER Climate Atlas Generator v%s — Processing Log (ArcMap 10.x)\n" % info["tool_version"])
            fh.write(u"Created: %s\n\n" % now_str())
            fh.write(u"Modules: %s\n" % ", ".join(info["modules"]))
            fh.write(u"Period: %d-%d (%d years)\n" % info["years"])
            fh.write(u"Data source: %s\n" % info.get("provider", "NASA POWER API"))
            if info.get("dl_only"):
                fh.write(u"Mode: DOWNLOAD ONLY (points + tables, no rasters).\n")
            fh.write(u"Temporal: %s | Interp: %s | Base cell: %s | Wind cell: %s\n"
                     % (info["temporal"], info["interp"], info["base_cell"], info["wind_cell"]))
            fh.write(u"Raw float rasters (32-bit, true values) | LZW: enforced | purge cache: %s\n"
                     % (info.get("purge", "?")))
            fh.write(u"Tolerance: %.0f m | Focal: %s\n" % (
                info.get("tol_m", 0),
                ("OFF" if not (info.get("focal") or {}).get("apply") else "%s %dx%d" % (
                    info["focal"]["stat"], info["focal"]["size"], info["focal"]["size"]))))
            if info.get("interp_detail"):
                fh.write(u"Interp detail: %s\n" % info["interp_detail"])
            if info.get("iso", ("", None))[0]:
                fh.write(u"Isobars: %s, step %.2f mbar.\n" % info["iso"])
            fh.write(u"Points: %d | Queries OK: %d | Queries failed: %d\n"
                     % (info["n_points"], info["n_ok"], info["n_fail"]))
            if info["failed"]:
                fh.write(u"Failed points (oid, err):\n")
                for oid, err in info["failed"]:
                    fh.write(u"  %s: %s\n" % (oid, err))
            fh.write(u"\nRasters:\n")
            for item in info["rasters"]:
                fh.write(u"  [%s] %s\n" % (item[3], item[1]))
            if info.get("element_layers"):
                fh.write(u"\nElement point layers:\n")
                for _m in sorted(info["element_layers"]):
                    fh.write(u"  [%s] %s\n" % (_m, info["element_layers"][_m]))
            if info["wind"]:
                fh.write(u"\nWind vectors:\n")
                for w in info["wind"]:
                    fh.write(u"  %s\n" % w)
            fh.write(u"\nScientific notes:\n")
            _is_om = str(info.get("provider", "")).startswith("Open-Meteo")
            _src = (u"Open-Meteo ERA5 reanalysis (~0.25 deg native)" if _is_om
                    else u"NASA POWER (~0.5 deg native)")
            for n in [
                (_is_om and u"Open-Meteo ERA5 are gridded/modelled estimates, not in-situ measurements."
                 or u"NASA POWER are gridded/modelled estimates, not in-situ measurements."),
                u"Interpolated cell size is cartographic; native resolution is coarse (%s)." % _src,
                u"Wind direction uses circular (vector) mean.",
                u"Precipitation is accumulated (sum), not averaged like temperature.",
                u"PSL (sea-level) and PS (surface) are different products.",
                u"Sol_Annual_Mean (kWh/m2/day) differs from Sol_Annual_Total (kWh/m2/year).",
                u"Winter = months 12,1,2 of the same year(s); -999 excluded; NoData where insufficient valid values.",
                u"Wind chill is a monthly-mean screening signal (valid per month only at T<=10C and wind>=4.8 km/h, else equals air T).",
                u"Trends need >=8 complete years; anomalies = last 10 complete years minus the WMO 1991-2020 normal (>=20 baseline years).",
                u"Rasters are raw float GeoTIFFs clipped to the study area, written "
                u"directly inside each element folder; classified display rasters "
                u"(<field>_cls.tif) are written alongside only when enabled.",
            ]:
                fh.write(u"  - %s\n" % n)
            if info["warnings"]:
                fh.write(u"\nWarnings (%d):\n" % len(info["warnings"]))
                for w in info["warnings"]:
                    fh.write(u"  ! %s\n" % w)
            fh.write(u"\nQA:\n")
            for name, ok, detail in info["qa"]:
                fh.write(u"  [%s] %s %s\n" % ("PASS" if ok else "FAIL", name, detail))

            # --- EXECUTION TIMELINE & PERFORMANCE BENCHMARKS ---
            fh.write(u"\n" + u"=" * 78 + u"\n")
            fh.write(u"EXECUTION TIMELINE & PERFORMANCE BENCHMARKS\n")
            fh.write(u"=" * 78 + u"\n")
            fh.write(u"Overall Started  : %s\n" % info.get("start_time", "-"))
            fh.write(u"Overall Completed: %s\n" % info.get("end_time", "-"))
            fh.write(u"Total Duration   : %s (%.1f seconds)\n" % (
                format_duration(info.get("elapsed", 0)), info.get("elapsed", 0)))

            mod_timings = info.get("module_timings") or {}
            if mod_timings:
                fh.write(u"\n--- Element Performance Breakdown ---\n")
                fh.write(u"%-22s | %-8s | %-8s | %-12s | %-7s | %-12s | %-6s\n" %
                         ("Element", "Start", "End", "Download Dur", "Rasters", "Interp Dur", "Status"))
                fh.write(u"%s\n" % ("-" * 86))
                for m, mdata in mod_timings.items():
                    fh.write(u"%-22s | %-8s | %-8s | %-12s | %-7d | %-12s | %-6s\n" % (
                        m[:22],
                        mdata.get("start_time", "-"),
                        mdata.get("end_time", "-"),
                        format_duration(mdata.get("dl_dur", 0)),
                        mdata.get("n_rasters", 0),
                        format_duration(mdata.get("interp_dur", 0)),
                        mdata.get("status", "-")
                    ))

            r_timings = info.get("raster_timings") or {}
            if r_timings:
                fh.write(u"\n--- Detailed Raster Generation Durations ---\n")
                fh.write(u"%-22s | %-36s | %-12s\n" % ("Element", "Raster File", "Duration"))
                fh.write(u"%s\n" % ("-" * 76))
                for fld, rinfo in sorted(r_timings.items(), key=lambda x: (x[1][0] if len(x[1]) > 0 else "", x[0])):
                    _mod = rinfo[0] if len(rinfo) > 0 else "-"
                    _fname = rinfo[1] if len(rinfo) > 1 else fld
                    _dur = rinfo[2] if len(rinfo) > 2 else 0.0
                    fh.write(u"%-22s | %-36s | %-12s\n" % (
                        _mod[:22],
                        _fname[:36],
                        format_duration(_dur)
                    ))
            fh.write(u"=" * 78 + u"\n")

    def _cleanup(self, msg, scratch=None, purge=True):
        for o in ["in_memory/input_proj", "in_memory/raw_ras",
                  "in_memory/u_raw", "in_memory/u_clip",
                  "in_memory/wind_fishnet", "in_memory/wind_fishnet_label",
                  "in_memory/wind_clip", "in_memory/shp_tmp",
                  "pwr_atlas_interp"]:
            try:
                if arcpy.Exists(o):
                    arcpy.management.Delete(o)
            except Exception:
                pass
        try:
            arcpy.ClearEnvironment("mask")
            arcpy.ClearEnvironment("extent")
            arcpy.ClearEnvironment("cellSize")
            arcpy.ClearEnvironment("outputCoordinateSystem")
            arcpy.ClearEnvironment("parallelProcessingFactor")
            arcpy.ClearEnvironment("compression")
            arcpy.ClearEnvironment("tileSize")
            arcpy.ClearEnvironment("pyramid")
            arcpy.ClearEnvironment("rasterStatistics")
            arcpy.ClearEnvironment("scratchWorkspace")
        except Exception:
            pass
        if scratch and purge:
            try:
                import shutil
                if os.path.isdir(scratch):
                    shutil.rmtree(scratch, ignore_errors=True)
                msg("Scratch cache purged: %s" % scratch)
            except Exception as ex:
                msg("Scratch purge skipped: %s" % ex)
        elif scratch:
            msg("Scratch kept for inspection (purge OFF): %s" % scratch)
        msg("Intermediate data cleaned (in_memory, masks reset). Inputs and final outputs untouched.")
