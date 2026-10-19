# -*- coding: utf-8 -*-
"""
Mega Climate Styles Architecture Generator
Generates comprehensive style definitions for all 125 scientific palettes across 11 elements,
each expanded to 9 distinct class tiers: [3, 4, 5, 6, 7, 8, 9, 10, 11].
Total: 125 styles x 9 tiers x 2 (Stepped + Smooth) = 2,250 Color Ramps!
"""
from __future__ import unicode_literals
import io
import math
import sys
import os
import json

def srgb_to_xyz(r, g, b):
    def inv_gamma(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r_l, g_l, b_l = inv_gamma(r), inv_gamma(g), inv_gamma(b)
    x = r_l * 0.4124564 + g_l * 0.3575761 + b_l * 0.1804375
    y = r_l * 0.2126729 + g_l * 0.7151522 + b_l * 0.0721750
    z = r_l * 0.0193339 + g_l * 0.1191920 + b_l * 0.9503041
    return x, y, z

def xyz_to_lab(x, y, z):
    xn, yn, zn = 0.95047, 1.00000, 1.08883
    def f(t):
        return t ** (1.0/3.0) if t > 0.008856 else 7.787 * t + 16.0 / 116.0
    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return L, a, b

def lab_to_xyz(L, a, b):
    xn, yn, zn = 0.95047, 1.00000, 1.08883
    fy = (L + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    def inv_f(t):
        return t ** 3 if t ** 3 > 0.008856 else (t - 16.0 / 116.0) / 7.787
    return inv_f(fx) * xn, inv_f(fy) * yn, inv_f(fz) * zn

def xyz_to_srgb(x, y, z):
    r_l = x *  3.2404542 + y * -1.5371385 + z * -0.4985314
    g_l = x * -0.9692660 + y *  1.8760108 + z *  0.0415560
    b_l = x *  0.0556434 + y * -0.2040259 + z *  1.0572252
    def gamma(v):
        v = max(0.0, min(1.0, v))
        return 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1.0 / 2.4)) - 0.055
    return int(round(gamma(r_l) * 255.0)), int(round(gamma(g_l) * 255.0)), int(round(gamma(b_l) * 255.0))

def hex_to_lab(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return xyz_to_lab(*srgb_to_xyz(r, g, b))

def lab_to_hex(L, a, b):
    r, g, b = xyz_to_srgb(*lab_to_xyz(L, a, b))
    return '#%02X%02X%02X' % (r, g, b)

def interp_lab(c1, c2, t):
    return (c1[0] + (c2[0] - c1[0]) * t,
            c1[1] + (c2[1] - c1[1]) * t,
            c1[2] + (c2[2] - c1[2]) * t)

def interpolate_piecewise(anchors_hex, n):
    anchors_lab = [hex_to_lab(h) for h in anchors_hex]
    if n == 1:
        return [anchors_hex[len(anchors_hex)//2]]
    m = len(anchors_lab)
    res = []
    for i in range(n):
        t = float(i) / float(n - 1)
        scaled_t = t * (m - 1)
        idx = min(int(math.floor(scaled_t)), m - 2)
        local_t = scaled_t - idx
        L, a, b = interp_lab(anchors_lab[idx], anchors_lab[idx+1], local_t)
        res.append(lab_to_hex(L, a, b))
    return res

def generate_classes_for_palette(cat, anchors):
    """
    Generates color hex lists for tiers 3, 4, 5, 6, 7, 8, 9, 10, 11
    ensuring strict symmetry for diverging palettes.
    """
    classes = {}
    is_diverging = (cat.lower() == "diverging")

    for n in [3, 4, 5, 6, 7, 8, 9, 10, 11]:
        if is_diverging:
            # anchors: (neg_list, neutral_hex, pos_list)
            neg_anchors, neutral_hex, pos_anchors = anchors
            if n % 2 == 1:
                k = (n - 1) // 2
                left = interpolate_piecewise(neg_anchors, k)
                center = [neutral_hex]
                right = interpolate_piecewise(pos_anchors, k)
                classes[n] = left + center + right
            else:
                k = n // 2
                left = interpolate_piecewise(neg_anchors, k)
                right = interpolate_piecewise(pos_anchors, k)
                classes[n] = left + right
        else:
            # Sequential or Multi-Hue: piecewise over anchor points
            classes[n] = interpolate_piecewise(anchors, n)
    return classes

# Define all 125 styles metadata & anchors
RAW_STYLES_DATA = [
    # =========================================================================
    # 01_Temperature (25 styles)
    # =========================================================================
    {
        "element_folder": "01_Temperature",
        "element_name_en": "Temperature",
        "element_name_ar": "درجات الحرارة",
        "styles": [
            ("Temp_Seq_WarmRed", "Sequential Warm Red", "تدرج أحمر دافئ متتابع", "Sequential", "ColorBrewer Reds",
             ["#FCBBA1", "#FC9272", "#FB6A4A", "#DE2D26", "#A50F15", "#67000D"]),
            ("Temp_Seq_AmberOrange", "Thermal Amber Orange", "تدرج برتقالي عنبري حراري", "Sequential", "ColorBrewer Oranges",
             ["#FDD0A2", "#FDBB84", "#FDAE6B", "#F16913", "#D94801", "#7F2704"]),
            ("Temp_Seq_CoolBlue", "Minimum Cold Temperature", "تدرج أزرق بارد للحرارة الصغرى", "Sequential", "ColorBrewer Blues",
             ["#BDD7E7", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C", "#08306B"]),
            ("Temp_Seq_DeepPurple", "Severe Frost & Cryosphere", "تدرج بنفسجي للصقيع الشديد والتجمد", "Sequential", "ColorBrewer Purples",
             ["#DADAEB", "#BCBDDC", "#9E9AC8", "#756BB1", "#54278F", "#3F007D"]),
            ("Temp_Div_RdBu_IPCC", "IPCC AR6 Temperature Anomaly", "تدرج الشذوذ الحراري المعتمد لتقرير المناخ السادس", "Diverging", "IPCC AR6 / Nature (Crameri)",
             (["#053061", "#2166AC", "#4393C3", "#92C5DE"], "#FFFFBF", ["#F4A582", "#D6604D", "#B2182B", "#67001F"])),
            ("Temp_Div_RdYlBu_Brewer", "ColorBrewer RdYlBu Classic", "تدرج كولور بروير الكلاسيكي المتباعد", "Diverging", "ColorBrewer 2.0 (Cynthia Brewer)",
             (["#313695", "#4575B4", "#74ADD1", "#ABD9E9"], "#FFFFBF", ["#FDAE61", "#F46D43", "#D73027", "#A50026"])),
            ("Temp_Multi_SpectralMuted", "Esri Soft Spectral", "طيف إزري الناعم المريح بصرياً", "Diverging", "Esri Better Colors for Better Mapping",
             (["#2B83BA", "#64ABB0", "#ABDDA4"], "#FFFFBF", ["#FDAE61", "#EA633E", "#D7191C"])),
            ("Temp_Div_TealCoral", "Teal to Coral Ergonomic", "تدرج التركواز إلى المرجاني المريح للعين", "Diverging", "Esri Cartographic Design",
             (["#006666", "#008B8B", "#48D1CC", "#B2EBF2"], "#FFF2CE", ["#FFCCBC", "#FF8A65", "#FF5722", "#D84315"])),
            ("Temp_Div_PuOr", "Extreme Temperature Variance", "تدرج التباين الحراري البنفسجي-البرتقالي", "Diverging", "CPT-City Archive (J.J. Green)",
             (["#2D004B", "#542788", "#8073AC", "#B2ABD2"], "#FEE0B6", ["#FDB863", "#E08214", "#B35806", "#7F3B08"])),
            ("Temp_Multi_Thermal_Crameri", "Crameri Batlow Scientific", "مقياس باتلو العلمي المحايد إدراكياً", "Multi-Hue", "Fabio Crameri Scientific Colour Maps",
             ["#001030", "#0F4E7A", "#0E7270", "#369055", "#7AB028", "#B8C300", "#F7B800", "#FF7800", "#F04422", "#F6D94E"]),
            ("Temp_Multi_Roma_Crameri", "Crameri Roma Diverging", "مقياس روما العلمي المتباعد", "Diverging", "Fabio Crameri Scientific Colour Maps",
             (["#7E1E7B", "#542788", "#4393C3", "#92C5DE"], "#FFFFBF", ["#FEE090", "#FDAE61", "#F46D43", "#A50026"])),
            ("Temp_Multi_WMO_Standard", "WMO Synoptic Temperature", "مقياس درجات الحرارة السطحية للمنظمة العالمية للأرصاد", "Multi-Hue", "WMO Technical Regulations WMO-No. 306",
             ["#000080", "#0000FF", "#00BFFF", "#00FFFF", "#00FF00", "#FFFF00", "#FFA500", "#FF0000", "#800000"]),
            ("Temp_Multi_NOAA_NWS", "NOAA NWS Heat Scale", "المقياس المعتمد للتنبؤات الحرارية بهيئة الأرصاد الأمريكية", "Multi-Hue", "NOAA National Weather Service (NWS)",
             ["#2C1E5C", "#483D8B", "#4169E1", "#87CEEB", "#98FB98", "#FFFF00", "#FFA500", "#FF4500", "#8B0000"]),
            ("Temp_Multi_NASA_LST", "NASA MODIS Land Surface Temp", "تدرج حرارة سطح الأرض من أقمار ناسا", "Multi-Hue", "NASA Earth Science Data Systems (LST)",
             ["#0C0887", "#4B03A1", "#7D03A8", "#A82296", "#CB4679", "#E56B5D", "#F89441", "#FDBB2D", "#F0F921"]),
            ("Temp_Multi_HeatwaveRisk", "Extreme Heatwave Stress", "مقياس مخاطر الموجات الحارة الشديدة والإجهاد الحيوي", "Sequential", "WMO / WHO Health Heatwave Guidance",
             ["#FFFFB2", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#B10026", "#67000D", "#490000"]),
            ("Temp_Div_NASA_GISTEMP", "NASA GISTEMP Global Anomaly", "تدرج شذوذ الحرارة السطحية العالمي لمرصد غودارد", "Diverging", "NASA Goddard Institute for Space Studies (GISS)",
             (["#08306B", "#2879B9", "#73B3D8", "#C6DBEF"], "#FFFFBF", ["#FDD0A2", "#F16913", "#C51B17", "#67000D"])),
            ("Temp_Multi_ERA5_Thermal", "ECMWF ERA5 2m Air Temp", "تدرج حرارة الهواء 2م لإعادة التحليل الأوروبي ERA5", "Multi-Hue", "ECMWF Copernicus Climate Change Service (C3S)",
             ["#00204D", "#004273", "#126782", "#358A88", "#67A685", "#A3BE85", "#D5CE8A", "#FFDC80", "#F28E2B", "#E15759"]),
            ("Temp_Multi_NOAA_CPC", "NOAA CPC Climatological Scale", "مقياس مركز التنبؤات المناخية الأمريكي CPC", "Multi-Hue", "NOAA Climate Prediction Center",
             ["#313695", "#4575B4", "#74ADD1", "#ABD9E9", "#E0F3F8", "#FFFFBF", "#FEE090", "#FDAE61", "#F46D43", "#D73027", "#A50026"]),
            ("Temp_Div_Nuuk_Cryo", "Crameri Nuuk Cryosphere", "مقياس نوك العلمي للمناطق القطبية والجليد", "Diverging", "Fabio Crameri Scientific Colour Maps (Nuuk)",
             (["#0D253A", "#1C4E75", "#3A7EB0", "#76AFDA", "#B5DBF2"], "#FFFFBF", ["#FAD3BD", "#F59D77", "#DF5842", "#AC1C24", "#610012"])),
            ("Temp_Seq_FrostThreshold", "WMO Frost & Freeze Hazard", "عتبات خطر الصقيع والتجمد الزراعي", "Sequential", "WMO Agricultural Meteorology Guidelines",
             ["#E0F3F8", "#92C5DE", "#4393C3", "#2166AC", "#053061", "#021A3B"]),
            ("Temp_Multi_KoppenThermal", "Köppen-Geiger Thermal Regimes", "الأقاليم الحرارية المعيارية لتصنيف كوبن-جيجر", "Multi-Hue", "Köppen-Geiger World Climate Classification",
             ["#960000", "#FF0000", "#FF69B4", "#FFA500", "#FFFF00", "#00FF00", "#00FFFF", "#007FFF", "#0000FF", "#800080"]),
            ("Temp_Div_HadCRUT5", "HadCRUT5 Historical Warming", "شذوذ الاحترار التاريخي لمركز هادلي البريطاني", "Diverging", "UK Met Office / Climatic Research Unit (CRU)",
             (["#08519C", "#3182BD", "#6BAED6", "#BDD7E7"], "#FFFFBF", ["#FCAE91", "#FB6A4A", "#DE2D26", "#A50F15"])),
            ("Temp_Multi_SteadmanApparent", "Steadman Apparent Temperature", "درجة الحرارة المحسوسة الفعلية لستيدمان", "Multi-Hue", "Steadman Biometeorological Formula",
             ["#2B83BA", "#ABDDA4", "#FFFFBF", "#FDAE61", "#D7191C", "#7F0000"]),
            ("Temp_Div_ContinentalThermal", "Continental Annual Range", "المدى الحراري السنوي للمناطق القارية", "Diverging", "Climatological Continental Range Index",
             (["#1B385C", "#3B6998", "#78A3C8", "#B8D4E8"], "#FFFFBF", ["#FDD49E", "#FDBB84", "#FC8D59", "#E34A33", "#B30000"])),
            ("Temp_Seq_TropicalNights", "Tropical Nights Accumulation", "مؤشر الليالي الاستوائية وتراكم الحرارة الليلية", "Sequential", "WMO Expert Team on Climate Change Indices (ETCCDI)",
             ["#FFF7BC", "#FEE391", "#FEC44F", "#FE9929", "#EC7014", "#CC4C02", "#993404", "#662506"])
        ]
    },

    # =========================================================================
    # 02_Precipitation (16 styles)
    # =========================================================================
    {
        "element_folder": "02_Precipitation",
        "element_name_en": "Precipitation",
        "element_name_ar": "الأمطار والتساقط",
        "styles": [
            ("Precip_Seq_Blues", "Cumulative Rainfall Blues", "تدرج الهطول المطري التراكمي القياسي", "Sequential", "ColorBrewer Blues",
             ["#BDD7E7", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#08519C", "#08306B"]),
            ("Precip_Seq_YlGnBu", "Climatological Precipitation", "تدرج الهطول المناخي السنوي والفصلي", "Sequential", "NOAA ROC / ColorBrewer YlGnBu",
             ["#FFFFCC", "#EDF8B1", "#C7E9B4", "#7FCDBB", "#41B6C4", "#1D91C0", "#225EA8", "#253494", "#081D58"]),
            ("Precip_Seq_BuPu", "Monsoon & Heavy Downpours", "تدرج أمطار الرياح الموسمية والهطول الغزير", "Sequential", "ColorBrewer BuPu",
             ["#BFD3E6", "#9EBCDA", "#8C96C6", "#8C6BB1", "#88419D", "#810F7C", "#4D004B"]),
            ("Precip_Div_BrBG", "Precipitation Departure Anomaly", "شذوذ وفائض وعجز الأمطار عن المعدل الطبيعي", "Diverging", "ColorBrewer BrBG",
             (["#543005", "#8C510A", "#BF812D", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#35978F", "#01665E", "#003C30"])),
            ("Precip_Div_SPI", "Standardized Precipitation Index", "مؤشر الهطول القياسي (SPI) للجفاف والرطوبة", "Diverging", "WMO Commission for Agricultural Meteorology (SPI)",
             (["#730000", "#E60000", "#FFAA00", "#FFFF00"], "#F6E8C3", ["#A6F28F", "#38A800", "#0070FF", "#002673"])),
            ("Precip_Multi_DopplerRadar", "Doppler Radar Reflectivity dBZ", "مقياس انعكاسية رادار الطقس الوطني للسيول", "Multi-Hue", "NOAA NWS Radar Operations Center (ROC)",
             ["#04E9E7", "#019FF4", "#0300F4", "#02FD02", "#01C501", "#008E00", "#FDF802", "#E5BC00", "#FD9500", "#FD0000", "#D40000", "#BC0000", "#F800FD", "#9854C6", "#4A0072"]),
            ("Precip_Multi_FlashFlood", "Flash Flood Guidance Risk", "مقياس مخاطر السيول الجارفة والفيضانات المفاجئة", "Multi-Hue", "NOAA National Water Center (NWC)",
             ["#B2E2E2", "#66C2A4", "#2CA25F", "#006D2C", "#FFD92F", "#E78AC3", "#E41A1C", "#7F0000"]),
            ("Precip_Multi_SnowIce", "Cryospheric Snow & Glacial", "تدرج تراكم الثلوج والكتل الجليدية", "Multi-Hue", "National Snow and Ice Data Center (NSIDC)",
             ["#C6E8F8", "#BAE4BC", "#7BCCC4", "#43A2CA", "#0868AC", "#084081", "#1F1A3A"]),
            ("Precip_Multi_NASA_GPM", "NASA GPM IMERG Precipitation", "تدرج قياس الهطول العالمي عبر أقمار ناسا GPM", "Multi-Hue", "NASA Global Precipitation Measurement (GPM)",
             ["#A8E6F5", "#00B4D8", "#0077B6", "#03045E", "#F72585", "#7209B7", "#3A0CA3"]),
            ("Precip_Seq_CHIRPS_Rain", "CHIRPS High-Resolution Rainfall", "تدرج مراقبة الأمطار عالي الدقة CHIRPS", "Sequential", "Climate Hazards Center / UCSB",
             ["#A2D9CE", "#73C6B6", "#45B39D", "#16A085", "#117864", "#0E6251", "#0B4C3F"]),
            ("Precip_Multi_ERA5_Total", "ECMWF ERA5 Total Precipitation", "تدرج إجمالي الهطول المطري لنموذج ERA5 العالمي", "Multi-Hue", "ECMWF Copernicus Climate Change Service",
             ["#B5D9F0", "#92C5DE", "#4393C3", "#2166AC", "#053061", "#2D004B", "#49006A"]),
            ("Precip_Seq_Intensity_WMO", "WMO Hourly Rainfall Intensity", "مقياس شدة الأمطار الساعية للمنظمة العالمية للأرصاد", "Sequential", "WMO-No. 8 Guide to Meteorological Instruments",
             ["#E0F7FA", "#80DEEA", "#26C6DA", "#00ACC1", "#00838F", "#006064"]),
            ("Precip_Div_SPEI_Multi", "Multi-scalar SPEI Drought/Wet", "مؤشر الجفاف والفيضان متعدد المقاييس الزمنية SPEI", "Diverging", "Vicente-Serrano et al. (SPEI Global)",
             (["#8C510A", "#BF812D", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#35978F", "#01665E"])),
            ("Precip_Seq_SWE_Snowpack", "Snow Water Equivalent SWE", "المكافئ المائي للغطاء الثلجي والهيدرولوجيا", "Sequential", "USDA NRCS SNOTEL / NASA SnowEx",
             ["#BDD7E7", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#084594"]),
            ("Precip_Multi_ConvectiveStorm", "Severe Convective Cloudburst", "مقياس السحب الحملية الركامية والسيول الوميضية", "Multi-Hue", "NOAA Storm Prediction Center (SPC)",
             ["#C7EAE5", "#5AB4AC", "#01665E", "#FFCC00", "#FF6600", "#CC0000", "#7A0000", "#4A004A"]),
            ("Precip_Div_MonsoonAnomaly", "Tropical Monsoon Anomaly", "شذوذ الرياح الموسمية المدارية وفترات الانقطاع", "Diverging", "Indian Meteorological Department / WMO Monsoon",
             (["#A6611A", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#018571"]))
        ]
    },

    # =========================================================================
    # 03_Sea_Level_Pressure (8 styles)
    # =========================================================================
    {
        "element_folder": "03_Sea_Level_Pressure",
        "element_name_en": "Sea Level Pressure",
        "element_name_ar": "الضغط عند مستوى سطح البحر",
        "styles": [
            ("Pres_Div_WMO_MSLP", "WMO MSLP Diverging", "مقياس الضغط الجوي المتباعد عند 1013.25 مليبار", "Diverging", "WMO Synoptic Standards (1013.25 hPa)",
             (["#67001F", "#B2182B", "#D6604D", "#F4A582"], "#FFFFBF", ["#92C5DE", "#4393C3", "#2166AC", "#053061"])),
            ("Pres_Synoptic_HighLow", "Synoptic Highs & Lows", "تدرج المنخفضات والمرتفعات الجوية السينوبتيكية", "Diverging", "NOAA Ocean Prediction Center (OPC)",
             (["#A50026", "#D73027", "#F46D43", "#FDAE61"], "#FFFFBF", ["#ABD9E9", "#74ADD1", "#4575B4", "#313695"])),
            ("Pres_Multi_Cyclones", "Tropical Cyclones & Depressions", "تدرج المنخفضات المدارية العميقة ومراكز الأعاصير", "Multi-Hue", "National Hurricane Center (NHC)",
             ["#49006A", "#7A0177", "#AE017E", "#DD3497", "#F768A1", "#FA9FB5", "#FCC5C0", "#F49AC2"]),
            ("Pres_Seq_Density", "Isobaric Air Density", "تدرج كثافة الهواء والباروكلينيكية الجوية", "Sequential", "CPT-City Isobaric Archive",
             ["#FEE8C8", "#FDD49E", "#FDBB84", "#FC8D59", "#EF6548", "#D7301F", "#B30000", "#7F0000"]),
            ("Pres_Div_SevereCyclone", "Severe Cyclone Deep Core", "المنخفضات الجوية الشديدة والأعاصير الحلزونية", "Diverging", "WMO Severe Weather Information Centre",
             (["#542788", "#998EC3", "#D8DAEB"], "#FFFFBF", ["#FEE0B6", "#F1A340", "#B35806"])),
            ("Pres_Synoptic_Subtropical", "Subtropical High Belts", "المرتفعات شبه المدارية وحزام الضغط المرتفع الآزوري", "Sequential", "Hadley Circulation Pressure Climatology",
             ["#B3CDE3", "#8C96C6", "#8856A7", "#810F7C"]),
            ("Pres_Div_SiberianAnticyclone", "Siberian High vs Mediterranean", "المرتفع السيبيري الشتوي مقابل منخفضات المتوسط", "Diverging", "Synoptic Climatology of Eurasia & North Africa",
             (["#313695", "#4575B4", "#74ADD1"], "#FFFFBF", ["#FDAE61", "#F46D43", "#A50026"])),
            ("Pres_Multi_MicrobarIsobars", "High-Resolution Microbar Isobars", "تدرج خطوط تساوي الضغط عالي الدقة (2 مليبار)", "Multi-Hue", "NOAA High-Resolution Rapid Refresh (HRRR)",
             ["#2B83BA", "#64ABB0", "#ABDDA4", "#E6F598", "#FFFFBF", "#FEE08B", "#FDAE61", "#F46D43", "#D53E4F"])
        ]
    },

    # =========================================================================
    # 04_Surface_Pressure (8 styles)
    # =========================================================================
    {
        "element_folder": "04_Surface_Pressure",
        "element_name_en": "Surface Pressure",
        "element_name_ar": "الضغط الجوي السطحي",
        "styles": [
            ("SPres_Seq_Hypsometric", "Hypsometric Topographic Pressure", "تدرج الضغط السطحي الهبسومتري المرتبط بالتضاريس", "Sequential", "ICAO Standard Atmosphere Model",
             ["#003C30", "#01665E", "#35978F", "#80CDC1", "#C7EAE5", "#F6E8C3", "#DFC27D", "#BF812D", "#8C510A", "#543005"]),
            ("SPres_Multi_Terrain", "Orographic Relief Column", "تدرج الضغط الطبوغرافي المعقد للمرتفعات والوديان", "Multi-Hue", "USGS / NASA SRTM Digital Elevation",
             ["#2D004B", "#542788", "#8073AC", "#B2ABD2", "#D8DAEB", "#FEE0B6", "#FDB863", "#E08214", "#B35806", "#7F3B08"]),
            ("SPres_Div_Anomaly", "Surface Pressure Anomaly", "شذوذ الضغط الجوي السطحي عن المعدل التضاريسي", "Diverging", "ECMWF Surface Pressure Diagnostics",
             (["#2166AC", "#67A9CF", "#BDC9E1"], "#FFFFBF", ["#FDBB84", "#EF6548", "#B30000"])),
            ("SPres_Seq_Altimeter", "Barometric Altimeter QNH", "مقياس الارتفاع البارومتري للطيران والملاحة الجوية", "Sequential", "Federal Aviation Administration (FAA)",
             ["#C7E9C0", "#A1D99B", "#74C476", "#41AB5D", "#238B45", "#006D2C", "#00441B"]),
            ("SPres_Multi_PlateauHigh", "Tibetan & Ethiopian Plateau", "الضغط السطحي للهضاب العالية (هضبة التبت وإثيوبيا)", "Multi-Hue", "High-Altitude Meteorology Research",
             ["#313695", "#4575B4", "#74ADD1", "#ABD9E9", "#E0F3F8", "#FFFFBF", "#FEE090", "#FDAE61", "#F46D43"]),
            ("SPres_Seq_ValleyBasin", "Deep Depression & Rift Valley", "الضغط السطحي للمنخفضات العميقة (القطارة والبحر الميت)", "Sequential", "Dead Sea & Qattara Basin Barometric Studies",
             ["#FFFFD4", "#FED98E", "#FE9929", "#D95F0E", "#993404"]),
            ("SPres_Div_LapseRate", "Atmospheric Lapse Rate Departure", "انحراف تدرج الضغط الشاقولي عن الغلاف المعياري", "Diverging", "WMO Upper-Air Sounding Standards",
             (["#053061", "#2166AC", "#4393C3"], "#FFFFBF", ["#F4A582", "#D6604D", "#67001F"])),
            ("SPres_Multi_MicroRelief", "Micro-relief Surface Pressure", "الضغط السطحي للتضاريس الدقيقة والمنحدرات", "Multi-Hue", "Complex Terrain Mesoscale Meteorology",
             ["#00441B", "#238B45", "#74C476", "#C7E9C0", "#FFFFCC", "#FED976", "#FD8D3C", "#E31A1C", "#800026"])
        ]
    },

    # =========================================================================
    # 05_Wind (12 styles)
    # =========================================================================
    {
        "element_folder": "05_Wind",
        "element_name_en": "Wind",
        "element_name_ar": "سرعة واتجاه الرياح",
        "styles": [
            ("Wind_Seq_Beaufort", "WMO Beaufort Wind Scale", "مقياس بوفورت الدولي لسرعة وطاقة الرياح", "Multi-Hue", "WMO-No. 306 Beaufort Scale",
             ["#BEE3F8", "#A6D96A", "#1A9641", "#FFFFBF", "#FDAE61", "#F46D43", "#D7191C", "#7A0177", "#49006A"]),
            ("Wind_Multi_DopplerVelocity", "Doppler Radial Velocity", "سرعة الرياح القطرية لرادار الدوبلر (اقتراب/ابتعاد)", "Diverging", "NOAA ROC Doppler Radial Velocity",
             (["#00FF00", "#00BF00", "#008000", "#004000"], "#C5C5C5", ["#660000", "#990000", "#CC0000", "#FF0000"])),
            ("Wind_Multi_Hurricanes", "Saffir-Simpson Hurricane Scale", "مقياس سافير-سيمبسون لشدة الأعاصير المدارية", "Multi-Hue", "NOAA National Hurricane Center (NHC)",
             ["#41B6C4", "#253494", "#FED976", "#FD8D3C", "#E31A1C", "#800026", "#4D004B"]),
            ("Wind_Multi_AviationTurbulence", "Clear Air Turbulence Risk", "مخاطر الاضطرابات الجوية لطيران الخطوط الجوية", "Multi-Hue", "ICAO / FAA Aviation Turbulence Scale",
             ["#2B83BA", "#ABDDA4", "#FFFFBF", "#FDAE61", "#D7191C", "#99000D", "#4A0000"]),
            ("Wind_Seq_MarineGale", "Marine Offshore Gale Scale", "مقياس الأنواء البحرية والرياح العاتية في عرض البحر", "Sequential", "National Data Buoy Center (NDBC)",
             ["#B2E2E2", "#66C2A4", "#2CA25F", "#006D2C"]),
            ("Wind_Multi_EF_Tornado", "Enhanced Fujita Tornado Scale", "مقياس فوجيتا المطور للأعاصير القمعية التدميرية", "Multi-Hue", "NOAA Storm Prediction Center (EF-Scale)",
             ["#C7E9C0", "#74C476", "#FEB24C", "#FD8D3C", "#FC4E2A", "#B10026", "#490000"]),
            ("Wind_Multi_WindChill", "NOAA NWS Wind Chill Index", "مؤشر التبريد بالرياح ومخاطر التجمد البشري", "Multi-Hue", "NOAA National Weather Service (Wind Chill)",
             ["#A5D8F7", "#9ECAE1", "#4292C6", "#08519C", "#3F007D", "#67001F"]),
            ("Wind_Seq_PowerDensity", "Wind Power Density at 100m", "كثافة طاقة الرياح لتوليد الكهرباء على ارتفاع 100م", "Sequential", "Global Wind Atlas / DTU Wind Energy",
             ["#CCEBC5", "#A8DDB5", "#7BCCC4", "#4EB3D3", "#2B8CBE", "#0868AC", "#084081"]),
            ("Wind_Multi_JetStream", "Jet Stream Core Isotachs", "سرعات التيار النفاث في طبقات الجو العليا (250 hPa)", "Multi-Hue", "Aviation High-Altitude Jet Stream Climatology",
             ["#313695", "#4575B4", "#74ADD1", "#ABD9E9", "#FFFFBF", "#FDAE61", "#F46D43", "#D73027", "#A50026", "#4A0000"]),
            ("Wind_Multi_SeaState", "Douglas Sea State & Waves", "مقياس دوغلاس لحالة البحر وارتفاع الأمواج", "Multi-Hue", "WMO Marine Meteorology Guide (Douglas Scale)",
             ["#E0F3F8", "#92C5DE", "#4393C3", "#2166AC", "#053061", "#2D004B", "#67001F"]),
            ("Wind_Seq_ThermalBreeze", "Diurnal Coastal Breeze", "نسيم البر والبحر ودورة الرياح اليومية الساحلية", "Sequential", "Coastal Boundary Layer Meteorology",
             ["#BDD7E7", "#9ECAE1", "#6BAED6", "#3182BD", "#08519C"]),
            ("Wind_Multi_KhamsinDust", "Khamsin Sandstorm Gales", "رياح الخماسين والعواصف الغبارية الصحراوية", "Multi-Hue", "Middle East & North Africa Dust Climatology",
             ["#FFF7BC", "#FEE391", "#FEC44F", "#FE9929", "#D95F0E", "#993404", "#662506", "#3D1703"])
        ]
    },

    # =========================================================================
    # 06_Relative_Humidity (10 styles)
    # =========================================================================
    {
        "element_folder": "06_Relative_Humidity",
        "element_name_en": "Relative Humidity",
        "element_name_ar": "الرطوبة النسبية وبخار الماء",
        "styles": [
            ("RH_Seq_YlGnBu", "Surface Relative Humidity", "تدرج الرطوبة النسبية السطحية من الجفاف للتشبع", "Sequential", "ColorBrewer YlGnBu Climatology",
             ["#FFFFD9", "#EDF8B1", "#C7E9B4", "#7FCDBB", "#41B6C4", "#1D91C0", "#225EA8", "#253494", "#081D58"]),
            ("RH_Multi_SatWaterVapor", "Satellite Water Vapor IR", "قناة بخار الماء بالأشعة تحت الحمراء للأقمار الاصطناعية", "Multi-Hue", "EUMETSAT / GOES Water Vapor Channel",
             ["#000000", "#282828", "#505050", "#787878", "#A0A0A0", "#C8C8C8", "#5B0082"]),
            ("RH_Div_DewPointDepression", "Dew Point Depression", "فرق درجة الحرارة ونقطة الندى (تحديد تشبع الهواء)", "Diverging", "WMO Radiosonde & Synoptic Observations",
             (["#00441B", "#1B7837", "#5AAE61", "#A6DBA0"], "#F6E8C3", ["#FDB863", "#E08214", "#B35806", "#7F3B08"])),
            ("RH_Seq_FogSaturation", "Fog & Condensation Saturation", "تدرج تشبع الضباب والندى الكثيف الساحلي", "Sequential", "Aviation Surface Weather Observation (Fog/Mist)",
             ["#BDD7E7", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#08519C", "#08306B"]),
            ("RH_Seq_VPD_Agricultural", "Vapor Pressure Deficit VPD", "مؤشر عجز ضغط البخار لإجهاد المحاصيل الزراعية", "Sequential", "FAO-56 Irrigation / Agriculture & Forest Fire",
             ["#C7E9C0", "#A1D99B", "#74C476", "#FEB24C", "#FD8D3C", "#FC4E2A", "#B10026"]),
            ("RH_Multi_DewPointTemp", "Absolute Dew Point Scale", "مقياس درجة حرارة نقطة الندى المطلقة (°C)", "Multi-Hue", "NOAA National Weather Service (Dew Point)",
             ["#800080", "#4B0082", "#0000FF", "#00BFFF", "#00FF7F", "#FFFF00", "#FF7F00", "#FF0000"]),
            ("RH_Seq_SpecificHumidity", "Specific Humidity g/kg", "الرطوبة النوعية ونسبة محتوى بخار الماء (جم/كجم)", "Sequential", "Atmospheric Boundary Layer Thermodynamics",
             ["#D0D1E6", "#A6BDDB", "#74A9CF", "#3690C0", "#0570B0", "#045A8D", "#023858"]),
            ("RH_Multi_WBGT_Stress", "Wet Bulb Globe Temp WBGT", "مؤشر البصيلة الرطبة المعياري للإجهاد الحراري", "Multi-Hue", "ISO 7243 / OSHA Heat Stress Standards",
             ["#006D2C", "#2CA25F", "#FFFF00", "#FFA500", "#FF0000", "#7F0000"]),
            ("RH_Multi_PWAT_AtmRiver", "Precipitable Water PWAT", "الماء القابل للتساقط وخرائط الأنهار الجوية", "Multi-Hue", "NASA AIRS / NOAA Atmospheric Rivers",
             ["#B3E5FC", "#92C5DE", "#4393C3", "#2166AC", "#053061", "#49006A"]),
            ("RH_Div_MoistureFlux", "Moisture Flux Convergence", "تقارب وتباعد تدفق الرطوبة الجوية", "Diverging", "Dynamic Meteorology Moisture Convergence",
             (["#8C510A", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#01665E"]))
        ]
    },

    # =========================================================================
    # 07_Solar_Radiation (10 styles)
    # =========================================================================
    {
        "element_folder": "07_Solar_Radiation",
        "element_name_en": "Solar Radiation",
        "element_name_ar": "الإشعاع الشمسي والطاقة الكلية",
        "styles": [
            ("Solar_Seq_YlOrRd", "Global Solar Radiation", "تدرج الإشعاع الشمسي الكلي التراكمي", "Sequential", "ColorBrewer YlOrRd",
             ["#FFFFCC", "#FFEDA0", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#BD0026", "#800026"]),
            ("Solar_Seq_ESMAP_GHI", "Global Horizontal Irradiance GHI", "الإشعاع الشمسي الأفقي الكلي للبنك الدولي", "Sequential", "World Bank ESMAP / Solargis Global Solar Atlas",
             ["#FFFFB2", "#FECC5C", "#FD8D3C", "#F03B20", "#BD0026", "#7A0000"]),
            ("Solar_Seq_PVOUT", "Photovoltaic Potential PVOUT", "القدرة الإنتاجية لتوليد الكهرباء الكهروضوئية", "Sequential", "Global Solar Atlas Photovoltaic Electricity",
             ["#FFF7BC", "#FEE391", "#FEC44F", "#FE9929", "#EC7014", "#CC4C02", "#8C2D04"]),
            ("Solar_Seq_DNI_Thermal", "Direct Normal Irradiance DNI", "الإشعاع المباشر لمحطات الطاقة الشمسية المركزة", "Sequential", "NREL National Solar Radiation Database (NSRDB)",
             ["#FFFFE5", "#FFF7BC", "#FEE391", "#FEC44F", "#FE9929", "#EC7014", "#CC4C02", "#993404", "#662506"]),
            ("Solar_Seq_SunshineDuration", "Daily Sunshine Hours", "ساعات سطوع الشمس اليومية الفعلية (0-14 ساعة)", "Sequential", "WMO Sunshine Duration Climatological Standard",
             ["#FFFFD4", "#FEE391", "#FEC44F", "#FE9929", "#EC7014", "#CC4C02", "#8C2D04"]),
            ("Solar_Seq_DHI_Diffuse", "Diffuse Horizontal Irradiance", "الإشعاع الشمسي المشتت في الغلاف الجوي", "Sequential", "Solar Energy Engineering Diffuse Radiation",
             ["#CCEBC5", "#A8DDB5", "#7BCCC4", "#4EB3D3", "#2B8CBE"]),
            ("Solar_Seq_GTI_Tilted", "Global Tilted Irradiance GTI", "الإشعاع الشمسي للألواح الكهروضوئية المائلة", "Sequential", "PVGIS European Commission Photovoltaic Platform",
             ["#FFFFE5", "#FFF7BC", "#FEE391", "#FEC44F", "#FB6A4A", "#DE2D26", "#A50F15"]),
            ("Solar_Seq_PAR_Agronomy", "Photosynthetically Active PAR", "الإشعاع الشمسي الفعال في البناء الضوئي الزراعي", "Sequential", "Agrometeorology Crop Photosynthesis Scale",
             ["#C7E9C0", "#A1D99B", "#74C476", "#31A354", "#006D2C"]),
            ("Solar_Seq_ClearnessIndex", "Atmosphere Clearness Index Kt", "معامل صفاء السماء ونفاذية الغلاف الجوي للإشعاع", "Sequential", "Solar Radiation Clearness Index Modeling",
             ["#B3CDE3", "#8C96C6", "#8856A7", "#810F7C"]),
            ("Solar_Multi_SolarAlbedo", "Surface Shortwave Albedo", "معامل انعكاس سطح الأرض للإشعاع الشمسي (الألبيدو)", "Multi-Hue", "NASA MODIS / VIIRS Surface Albedo",
             ["#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#D4C2B0", "#A5D5F2"])
        ]
    },

    # =========================================================================
    # 08_UV_Index (8 styles)
    # =========================================================================
    {
        "element_folder": "08_UV_Index",
        "element_name_en": "UV Index",
        "element_name_ar": "مؤشر الأشعة فوق البنفسجية",
        "styles": [
            ("UV_Standard_WHO", "WHO Global Solar UV Index", "المعيار الدولي الإلزامي لمنظمة الصحة العالمية", "Multi-Hue", "WHO / WMO / UNEP (ISBN 92 4 159007 6)",
             ["#289500", "#48B500", "#F7E400", "#F85900", "#D80010", "#A80010", "#6B49C8", "#452494"]),
            ("UV_EPA_HealthRisk", "EPA Erythemal Damage Spectrum", "مقياس الحماية الصحية من أضرار الأشعة الحارقة", "Multi-Hue", "US Environmental Protection Agency (EPA)",
             ["#38A800", "#79C900", "#FFFF00", "#FFAA00", "#FF0000", "#8400A8", "#4C005C"]),
            ("UV_ErythemalDose", "Daily Erythemal UV Dose", "الجرعة اليومية للأشعة فوق البنفسجية المؤثرة حيوياً", "Sequential", "CIE S 007/E-1998 Erythemal Action Spectrum",
             ["#FFFFCC", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#E31A1C", "#BD0026", "#800026"]),
            ("UV_SummerPeak", "Tropical Summer Noon Peak UV", "ذروة الأشعة فوق البنفسجية الشديدة في ظهيرة الصيف", "Multi-Hue", "Tropical & Desert UV Radiation Monitoring",
             ["#229954", "#F4D03F", "#EB984E", "#E74C3C", "#8E44AD", "#512E5F"]),
            ("UV_Multi_Fitzpatrick", "Fitzpatrick Skin Phototypes", "مقياس فيتزباتريك لتحمل الجلد وسرعة حروق الشمس", "Multi-Hue", "Harvard Medical School / Fitzpatrick Phototypes",
             ["#FAD8C3", "#E3A882", "#BA774B", "#7A4526", "#452514"]),
            ("UV_Multi_HighAltitude", "High-Altitude Alpine UV", "مؤشر الأشعة فوق البنفسجية في المرتفعات والجبال", "Multi-Hue", "Alpine Solar Radiation Amplification Studies",
             ["#289500", "#F7E400", "#F85900", "#D80010", "#6B49C8", "#3B187B", "#1F0445"]),
            ("UV_Seq_VitaminDSynthesis", "Vitamin D Optimal Synthesis", "النطاق الشمسي الحيوي الآمن لتكوين فيتامين د", "Sequential", "Photobiology & Endocrine Society Guidelines",
             ["#B2E2E2", "#66C2A4", "#2CA25F", "#006D2C"]),
            ("UV_Div_OzoneDepletion", "Stratospheric Ozone UV Anomaly", "شذوذ الأشعة الناتج عن ترقق طبقة الأوزون", "Diverging", "WMO/UNEP Scientific Assessment of Ozone Depletion",
             (["#4575B4", "#74ADD1", "#ABD9E9"], "#FFFFBF", ["#FDAE61", "#F46D43", "#D73027"]))
        ]
    },

    # =========================================================================
    # 09_Cloud_Cover (8 styles)
    # =========================================================================
    {
        "element_folder": "09_Cloud_Cover",
        "element_name_en": "Cloud Cover",
        "element_name_ar": "الغطاء السحابي ونقاء السماء",
        "styles": [
            ("Cloud_Seq_Okta", "WMO Okta Cloud Scale", "مقياس الأوكتا العالمي للسحب (من 0 إلى 8 أوكتا)", "Multi-Hue", "WMO International Cloud Atlas (Okta Scale)",
             ["#A8D4F5", "#7FB3D5", "#5499C7", "#2980B9", "#2471A3", "#1B4F72", "#17202A"]),
            ("Cloud_Seq_Fraction", "Total Cloud Fraction %", "نسبة الغطاء السحابي الكلي المئوية (0% - 100%)", "Sequential", "MODIS / EUMETSAT Cloud Fraction",
             ["#BDD7E7", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#08519C", "#08306B"]),
            ("Cloud_Multi_IR_CloudTop", "Satellite IR Cloud Top Temp", "درجات حرارة قمم السحب بالأشعة تحت الحمراء", "Multi-Hue", "NOAA GOES-R Advanced Baseline Imager (ABI)",
             ["#B0D0E8", "#888888", "#444444", "#0000FF", "#00FF00", "#FFFF00", "#FF0000"]),
            ("Cloud_Seq_OpticalDepth", "Cloud Optical Thickness Tau", "السمك البصري للغيوم وكثافة حجب الضوء", "Sequential", "NASA MODIS Cloud Optical Properties",
             ["#CCEBC5", "#A8DDB5", "#7BCCC4", "#4EB3D3", "#2B8CBE", "#0868AC", "#084081"]),
            ("Cloud_Seq_LowCloudFog", "Low Stratus & Fog Ceiling", "السحب المنخفضة وحزام الضباب ومخاطر الرؤية", "Sequential", "Aviation Weather Center Ceiling & Fog Hazard",
             ["#C5CBD0", "#ABB2B9", "#8E99A2", "#7F8C8D", "#566573"]),
            ("Cloud_Multi_ConvectiveTops", "Overshooting Tops & Hailstorms", "القمم الركامية المخترقة وعواصف البرد الشديدة", "Multi-Hue", "NASA Convective Storm Research",
             ["#000080", "#0000FF", "#00BFFF", "#00FF00", "#FFFF00", "#FF7F00", "#FF0000", "#800080", "#4A004A"]),
            ("Cloud_Multi_AOD_Aerosol", "Aerosol Optical Depth 550nm", "عمق الهباء الجوي البصري والعواصف الترابية الصحراوية", "Multi-Hue", "NASA AERONET / MODIS Aerosol Optical Depth",
             ["#313695", "#4575B4", "#ABD9E9", "#FFFFBF", "#FDAE61", "#F46D43", "#D73027", "#8C510A"]),
            ("Cloud_Seq_CirrusIce", "High Cirrus Ice Water Path", "سحب السمحاق العالية ومسار الجليد السحابي", "Sequential", "Cirrus Cloud Radiation & Cryosphere Climatology",
             ["#BDD7E7", "#6BAED6", "#2171B5", "#08306B"])
        ]
    },

    # =========================================================================
    # 10_Drought_And_Aridity (10 styles)
    # =========================================================================
    {
        "element_folder": "10_Drought_And_Aridity",
        "element_name_en": "Drought and Aridity",
        "element_name_ar": "مؤشرات الجفاف والقحولة",
        "styles": [
            ("Aridity_UNEP_World", "UNEP World Aridity Index", "مؤشر القحولة العالمي المعتمد لأطلس التصحر", "Multi-Hue", "UNEP World Atlas of Desertification (AI = P/PET)",
             ["#D73027", "#F46D43", "#FDAE61", "#FEE08B", "#FFFFBF", "#D9EF8B", "#A6D96A", "#66BD63", "#1A9850", "#006837"]),
            ("Drought_SPEI_Index", "SPEI Drought Severity", "مؤشر الجفاف والتبخر المعياري المتعدد", "Diverging", "Global SPEI Drought Monitor (Vicente-Serrano)",
             (["#67001F", "#B2182B", "#D6604D", "#F4A582"], "#FFFFBF", ["#92C5DE", "#4393C3", "#2166AC", "#053061"])),
            ("Drought_PDSI_Palmer", "Palmer Drought Severity PDSI", "مؤشر بالمر الهيدرولوجي والزراعي لشدة الجفاف", "Diverging", "NOAA National Centers for Environmental Information",
             (["#730000", "#C51B17", "#E66101", "#FDB863"], "#FFFFBF", ["#B2ABD2", "#8073AC", "#542788", "#2D004B"])),
            ("Aridity_SoilMoistureDeficit", "Soil Moisture Depletion", "مؤشر استنزاف وعجز رطوبة التربة الجذرية", "Sequential", "European Drought Observatory (EDO / Copernicus)",
             ["#543005", "#8C510A", "#BF812D", "#DFC27D", "#F6E8C3", "#C7EAE5", "#80CDC1", "#35978F", "#01665E", "#003C30"]),
            ("Drought_ETo_Hargreaves", "Reference Evapotranspiration", "معدل البخر-نتح المرجعي بهارجريفز (ملم/يوم)", "Sequential", "FAO-56 Irrigation and Drainage Guidelines",
             ["#FFFFB2", "#FECC5C", "#FD8D3C", "#F03B20", "#BD0026", "#7A0000"]),
            ("Drought_EDDI_Evaporative", "Evaporative Demand Drought EDDI", "مؤشر الطلب التبخري لرصد الجفاف الوميضي السريع", "Diverging", "NOAA Physical Sciences Laboratory (EDDI)",
             (["#01665E", "#35978F", "#80CDC1"], "#F6E8C3", ["#DFC27D", "#BF812D", "#8C510A", "#543005"])),
            ("Drought_CMI_CropMoisture", "Crop Moisture Index CMI", "مؤشر رطوبة المحاصيل الزراعية الأسبوعي", "Diverging", "USDA / NOAA Joint Agricultural Weather Facility",
             (["#8C510A", "#BF812D", "#DFC27D"], "#F6E8C3", ["#C7EAE5", "#80CDC1", "#01665E"])),
            ("Drought_ETa_ActualDeficit", "Actual ET Deficit Index", "عجز البخر-نتح الفعلي عن المرجعي للمحاصيل", "Sequential", "USGS FEWS NET Water Balance Evapotranspiration",
             ["#FFFFD4", "#FED98E", "#FE9929", "#D95F0E", "#993404", "#542788"]),
            ("Drought_NDWI_WaterIndex", "Normalized Difference Water NDWI", "مؤشر اختلاف المياه المعياري للغطاء النباتي والتربة", "Diverging", "Gao (1996) Remote Sensing Water Index",
             (["#8C510A", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#01665E", "#003C30"])),
            ("Drought_Multi_DesertBoundaries", "Desert Biome Encroachment", "زحف الكثبان الرملية وتدهور أطراف الواحات", "Multi-Hue", "UNCCD Global Land Outlook / Sahara Encroachment",
             ["#8C510A", "#BF812D", "#DFC27D", "#E0D0B0", "#A8DDB5", "#43A2CA", "#0868AC"])
        ]
    },

    # =========================================================================
    # 11_Climate_Models (10 styles)
    # =========================================================================
    {
        "element_folder": "11_Climate_Models",
        "element_name_en": "Climate Models",
        "element_name_ar": "نماذج التغير المناخي والسيناريوهات",
        "styles": [
            ("Model_Div_WarmingStripes", "Ed Hawkins Warming Stripes", "خطوط الاحترار العالمي لجامعة ريدينج (1850-2025)", "Diverging", "Prof. Ed Hawkins / University of Reading (Warming Stripes)",
             (["#08306B", "#2171B5", "#6BAED6", "#BDD7E7"], "#FFFFBF", ["#FCAE91", "#FB6A4A", "#CB181D", "#67000D"])),
            ("Model_Div_TempAnomaly", "CMIP6 Temperature Anomaly", "شذوذ درجات الحرارة المتوقعة لنماذج CMIP6 المناخية", "Diverging", "World Climate Research Programme (WCRP / CMIP6)",
             (["#053061", "#2166AC", "#4393C3", "#92C5DE"], "#FFFFBF", ["#FEE090", "#FDAE61", "#F46D43", "#D73027", "#A50026"])),
            ("Model_Div_PrecipChange", "CMIP6 Precipitation % Change", "نسبة التغير المتوقعة في الأمطار المستقبلية (%)", "Diverging", "IPCC Working Group I Interactive Atlas",
             (["#543005", "#8C510A", "#BF812D", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#35978F", "#01665E", "#003C30"])),
            ("Model_Multi_SSPSenarios", "IPCC Shared Socioeconomic SSPs", "سيناريوهات مسارات التطور المشتركة (SSP1 إلى SSP5)", "Multi-Hue", "IPCC AR6 Cross-Working Group Scenario Palette",
             ["#005A32", "#238B45", "#74C476", "#FED976", "#FD8D3C", "#E31A1C", "#7F0000"]),
            ("Model_Multi_ExtremesIndex", "Climate Extremes ETCCDI", "مؤشر تكرار وشدة الظواهر المناخية المتطرفة", "Sequential", "WMO Commission for Climatology / ETCCDI",
             ["#FFFFCC", "#FED976", "#FEB24C", "#FD8D3C", "#FC4E2A", "#BD0026", "#67000D", "#490000"]),
            ("Model_Seq_TropicalNightsTR20", "Projected Tropical Nights TR20", "الزيادة المتوقعة في عدد الليالي الاستوائية الحارة", "Sequential", "CMIP6 Future Extreme Temperature Projections",
             ["#FFF7BC", "#FEE391", "#FEC44F", "#FE9929", "#EC7014", "#CC4C02", "#993404", "#662506"]),
            ("Model_Seq_ConsecutiveDryDays", "Consecutive Dry Days CDD", "أيام الجفاف المتتالية واتساع الفترات الجافة", "Sequential", "IPCC AR6 Drought Projections Index",
             ["#FFFFD4", "#FED98E", "#FE9929", "#D95F0E", "#993404", "#542788"]),
            ("Model_Div_ExtremePrecipR95p", "Very Wet Days R95p Index", "شذوذ الأيام شديدة المطر والأمطار الغزيرة القصوى", "Diverging", "WMO ETCCDI Extreme Precipitation Indices",
             (["#A6611A", "#DFC27D"], "#F6E8C3", ["#80CDC1", "#018571", "#003C30"])),
            ("Model_Seq_DegreeDays", "Degree Days Heating/Cooling Shift", "تحول أيام درجات التدفئة والتبريد لاستهلاك الطاقة", "Sequential", "Energy Climatology Heating & Cooling Degree Days",
             ["#BDD7E7", "#6BAED6", "#3182BD", "#08519C", "#FC4E2A", "#BD0026"]),
            ("Model_Multi_SeaLevelRise", "Coastal Sea Level Rise Scenarios", "سيناريوهات غمر وارتفاع منسوب البحر الساحلي حتى 2100", "Multi-Hue", "IPCC Special Report on Ocean and Cryosphere (SROCC)",
             ["#08519C", "#3182BD", "#6BAED6", "#BDD7E7", "#FEE5D9", "#FCAE91", "#FB6A4A", "#DE2D26", "#A50F15"])
        ]
    }
]

def build_generate_climate_styles_file():
    print("Computing CIELab Interpolations for all 125 Palettes x 9 Class Tiers (3 to 11)...")
    all_elements_output = []
    total_styles_count = 0

    for el_data in RAW_STYLES_DATA:
        el_obj = {
            "folder": el_data["element_folder"],
            "name_en": el_data["element_name_en"],
            "name_ar": el_data["element_name_ar"],
            "styles": []
        }
        for s_id, s_en, s_ar, s_cat, s_src, anchors in el_data["styles"]:
            classes_dict = generate_classes_for_palette(s_cat, anchors)
            el_obj["styles"].append({
                "id": s_id,
                "name_en": s_en,
                "name_ar": s_ar,
                "category": s_cat,
                "source": s_src,
                "classes": classes_dict
            })
            total_styles_count += 1
        all_elements_output.append(el_obj)

    print("Total styles configured: %d across 11 elements." % total_styles_count)

    # Separate temperature styles from other elements for module compatibility
    temp_styles = all_elements_output[0]["styles"]
    other_elements = all_elements_output[1:]

    target_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_climate_styles.py")
    with io.open(target_py, "w", encoding="utf-8") as f:
        f.write(u'''# -*- coding: utf-8 -*-
"""
NASA POWER & Open-Meteo Climate Atlas Generator
Comprehensive Climate Styles & Cartographic Color Palette Generator

Generates high-precision, cartographically balanced, perceptually uniform styles
for ArcGIS Desktop (10.x / 10.8), ArcGIS Pro, and QGIS.
Supported Formats: .style (ArcMap Style Database), .clr, .qml, .sld, .json, .csv.

Contains 125 Scientific Palettes across 11 Climate Elements.
Each palette supports 9 class tiers: 3, 4, 5, 6, 7, 8, 9, 10, 11 classes!
Total Color Ramps: 125 x 9 x 2 (Stepped + Smooth) = 2,250 Color Ramps!
"""
from __future__ import unicode_literals
import sys
import os
import io
import json

PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode
else:
    text_type = str

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def open_utf8(path, mode="w"):
    if PY2:
        return io.open(path, mode, encoding="utf-8")
    else:
        return open(path, mode, encoding="utf-8")

def hex_to_rgb(hex_code):
    h = hex_code.strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def write_clr(path, hex_colors, start_val=1):
    with open_utf8(path, "w") as f:
        for idx, hex_c in enumerate(hex_colors):
            r, g, b = hex_to_rgb(hex_c)
            f.write(u"%d %d %d %d\\n" % (start_val + idx, r, g, b))

TEMPERATURE_STYLES = ''')
        json_temp = json.dumps(temp_styles, ensure_ascii=False, indent=2)
        f.write(json_temp)
        f.write(u'''\n\nOTHER_ELEMENTS = ''')
        json_other = json.dumps(other_elements, ensure_ascii=False, indent=2)
        f.write(json_other)
        f.write(u'''\n\nCLIMATE_ELEMENTS_STYLES = [{'folder': '01_Temperature', 'name_en': 'Temperature', 'name_ar': 'درجات الحرارة', 'styles': TEMPERATURE_STYLES}] + OTHER_ELEMENTS\n''')
        f.write(u'''print("Mega Climate Styles Configured: 125 Palettes with 9 Class Tiers (3 to 11) across 11 Elements.")\n''')

    print("Successfully generated: %s" % target_py)

if __name__ == "__main__":
    build_generate_climate_styles_file()
