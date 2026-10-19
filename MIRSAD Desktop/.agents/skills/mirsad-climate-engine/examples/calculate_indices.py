# -*- coding: utf-8 -*-
"""
Python implementation of Core Climatological & Bioclimatic Indices.
Includes:
- De Martonne Aridity Index
- Lang Regenfaktor
- Growing Degree Days (GDD)
- NOAA Heat Index (Rothfusz equation)
"""

import math

def de_martonne_aridity_index(annual_precip_mm, annual_mean_temp_c):
    """
    Calculates De Martonne Aridity Index: I = P / (T + 10)
    Returns: (index_value, class_ar, class_en)
    """
    if annual_mean_temp_c + 10.0 <= 0:
        return 0.0, "شديد البرودة / متجمد", "Glacial / Tundra"
    idx = annual_precip_mm / (annual_mean_temp_c + 10.0)
    if idx < 5.0:
        cat_ar = "شديد الجفاف (صحراوي خالي)"
        cat_en = "Hyper-Arid"
    elif idx < 10.0:
        cat_ar = "جاف (صحراوي)"
        cat_en = "Arid"
    elif idx < 20.0:
        cat_ar = "شبه جاف (استبس / حشائش)"
        cat_en = "Semi-Arid"
    elif idx < 30.0:
        cat_ar = "شبه رطب (متوسطي)"
        cat_en = "Mediterranean / Sub-Humid"
    elif idx < 55.0:
        cat_ar = "رطب"
        cat_en = "Humid"
    else:
        cat_ar = "شديد الرطوبة"
        cat_en = "Per-Humid"
    return round(idx, 2), cat_ar, cat_en


def lang_regenfaktor(annual_precip_mm, annual_mean_temp_c):
    """Calculates Lang's Rain Factor: R_L = P / T"""
    if annual_mean_temp_c <= 0:
        return 0.0
    return round(annual_precip_mm / annual_mean_temp_c, 2)


def growing_degree_days(daily_mean_temps, base_temp=10.0):
    """
    Calculates GDD = Sum(max(0, T_mean - T_base)) over growing season.
    """
    gdd = 0.0
    for t in daily_mean_temps:
        if t is not None and t > base_temp:
            gdd += (t - base_temp)
    return round(gdd, 1)


def noaa_heat_index(temp_c, relative_humidity_pct):
    """
    Calculates NOAA Heat Index in Celsius using the full Rothfusz regression.
    """
    # Convert C to F
    T = (temp_c * 9.0 / 5.0) + 32.0
    RH = relative_humidity_pct

    # Simple equation first
    HI_simple = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094))
    if HI_simple < 80.0:
        HI_F = HI_simple
    else:
        # Full Rothfusz equation
        HI_F = (-42.379 + 2.04901523 * T + 10.14333127 * RH
                - 0.22475541 * T * RH - 0.00683783 * T * T
                - 0.05481717 * RH * RH + 0.00122874 * T * T * RH
                + 0.00085282 * T * RH * RH - 0.00000199 * T * T * RH * RH)

    # Convert back to Celsius
    HI_C = (HI_F - 32.0) * 5.0 / 9.0
    return round(HI_C, 1)
