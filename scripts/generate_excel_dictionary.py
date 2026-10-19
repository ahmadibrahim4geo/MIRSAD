# -*- coding: utf-8 -*-
"""
Script to build and format the comprehensive Fields_AR_EN_Units.xlsx
workbook for the NASA POWER Climate Atlas Generator.
"""
from __future__ import print_function
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

FIELDS_DATA = [
    # --- 1. الحقول الإدارية والوصفية (Administrative & Metadata Fields) ---
    {
        "short_name": "OBJECTID",
        "full_name": "OBJECTID",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"المعرف الرقمي التسلسلي الفريد للظاهرة في قاعدة البيانات الجغرافية (Geodatabase OID).",
        "unit": "-",
        "map_title": u"-"
    },
    {
        "short_name": "Source_ID",
        "full_name": "Source_ID",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"المعرف الفريد لمحطة الرصد أو النقطة المناخية المصدرية المدخلة في المعالجة.",
        "unit": "-",
        "map_title": u"-"
    },
    {
        "short_name": "Point_Lat",
        "full_name": "Point_Lat",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"دائرة العرض الجغرافية للنقطة بالنظام الإحداثي العالمي WGS 1984 بالدرجات العشرية.",
        "unit": u"درجة (°)",
        "map_title": u"خريطة توزيع دوائر العرض للمحطات"
    },
    {
        "short_name": "Point_Lon",
        "full_name": "Point_Lon",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"خط الطول الجغرافي للنقطة بالنظام الإحداثي العالمي WGS 1984 بالدرجات العشرية.",
        "unit": u"درجة (°)",
        "map_title": u"خريطة توزيع خطوط الطول للمحطات"
    },
    {
        "short_name": "Data_Start",
        "full_name": "Data_Start",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"سنة أو تاريخ بداية السلسلة الزمنية المناخية المسحوبة من وكالة ناسا POWER.",
        "unit": u"سنة / تاريخ",
        "map_title": u"-"
    },
    {
        "short_name": "Data_End",
        "full_name": "Data_End",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"سنة أو تاريخ نهاية السلسلة الزمنية المناخية المسحوبة من وكالة ناسا POWER.",
        "unit": u"سنة / تاريخ",
        "map_title": u"-"
    },
    {
        "short_name": "Temporal",
        "full_name": "Temporal",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"الدقة الزمنية للبيانات المدخلة في المعالجة (Daily يومي / Monthly شهري / Precalc محسوب مسبقاً).",
        "unit": u"نص",
        "map_title": u"-"
    },
    {
        "short_name": "Intrp_Meth",
        "full_name": "Interp_Meth",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"خوارزمية الاستيفاء المكاني المستخدمة في توليد أسطح الراستر (IDW / Kriging / Spline).",
        "unit": u"نص",
        "map_title": u"-"
    },
    {
        "short_name": "Cell_Size",
        "full_name": "Cell_Size",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"حجم ودقة خلية الراستر الناتجة عن الاستيفاء المكاني بوحدات الإسقاط المعتمد.",
        "unit": u"متر / درجات",
        "map_title": u"-"
    },
    {
        "short_name": "Wind_Cell",
        "full_name": "Wind_Cell",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"المسافة التباعدية بين خلايا شبكة متجهات وأسهم اتجاه وسرعة الرياح.",
        "unit": u"متر / درجات",
        "map_title": u"-"
    },
    {
        "short_name": "Status",
        "full_name": "Status",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"حالة إتمام المعالجة الحسابية المناخية للنقطة بنجاح (OK أو FAILED).",
        "unit": u"نص",
        "map_title": u"-"
    },
    {
        "short_name": "Error_Msg",
        "full_name": "Error_Msg",
        "module_code": "00_Admin",
        "module_name": "Admin / بيانات إدارية",
        "desc_ar": u"نص رسالة الخطأ أو التشخيص التحذيري في حال تعثر معالجة بيانات النقطة.",
        "unit": u"نص",
        "map_title": u"-"
    },

    # --- 2. درجات الحرارة (01_Temperature) ---
    {
        "short_name": "T_AnnMean",
        "full_name": "T_Annual_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي السنوي لدرجة حرارة الهواء عند ارتفاع 2 متر لجميع شهور السنة.",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي لدرجة الحرارة (°C)"
    },
    {
        "short_name": "T_MonMean",
        "full_name": "T_Month_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الشهري لدرجة حرارة الهواء عند ارتفاع 2 متر (متوسط الـ 12 شهراً المناخي).",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط الشهري لدرجة الحرارة (°C)"
    },
    {
        "short_name": "T_WinMean",
        "full_name": "T_Winter_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"متوسط درجة حرارة الهواء لفصل الشتاء الأرصادي (شهور ديسمبر، يناير، فبراير - DJF).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة خلال فصل الشتاء (°C)"
    },
    {
        "short_name": "T_SprMean",
        "full_name": "T_Spring_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"متوسط درجة حرارة الهواء لفصل الربيع الأرصادي (شهور مارس، أبريل، مايو - MAM).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة خلال فصل الربيع (°C)"
    },
    {
        "short_name": "T_SumMean",
        "full_name": "T_Summer_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"متوسط درجة حرارة الهواء لفصل الصيف الأرصادي (شهور يونيو، يوليو، أغسطس - JJA).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة خلال فصل الصيف (°C)"
    },
    {
        "short_name": "T_AutMean",
        "full_name": "T_Autumn_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"متوسط درجة حرارة الهواء لفصل الخريف الأرصادي (شهور سبتمبر، أكتوبر، نوفمبر - SON).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة خلال فصل الخريف (°C)"
    },
    {
        "short_name": "T_AnnRng",
        "full_name": "T_Annual_Range",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المدى الحراري السنوي (الفارق بين متوسط أدفأ شهور السنة ومتوسط أبرد شهور السنة).",
        "unit": u"°C",
        "map_title": u"خريطة المدى الحراري السنوي لدرجات الحرارة (°C)"
    },
    {
        "short_name": "T_SeaRng",
        "full_name": "T_Seasonal_Range",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجات الحرارة)",
        "desc_ar": u"المدى الفصلي لدرجة الحرارة (الفارق بين أدفأ فصول السنة وأبردها).",
        "unit": u"°C",
        "map_title": u"خريطة المدى الفصلي لدرجة الحرارة (°C)"
    },
    {
        "short_name": "T_MaxSumMo",
        "full_name": "T_Max_Summer_Month_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"متوسط درجة الحرارة لأدفأ شهور فصل الصيف (أعلى متوسط شهري مسجل في الصيف).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط أدفأ شهور فصل الصيف (°C)"
    },
    {
        "short_name": "T_MinWinMo",
        "full_name": "T_Min_Winter_Month_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"متوسط درجة الحرارة لأبرد شهور فصل الشتاء (أدنى متوسط شهري مسجل في الشتاء).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط أبرد شهور فصل الشتاء (°C)"
    },
    {
        "short_name": "T_MaxMean",
        "full_name": "T_Annual_Max_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط السنوي للنهايات العظمى اليومية لدرجة حرارة الهواء (T2M_MAX).",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي للنهايات العظمى لدرجة الحرارة (°C)"
    },
    {
        "short_name": "T_MinMean",
        "full_name": "T_Annual_Min_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط السنوي للنهايات الصغرى اليومية لدرجة حرارة الهواء (T2M_MIN).",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي للنهايات الصغرى لدرجة الحرارة (°C)"
    },
    {
        "short_name": "T_JanMean",
        "full_name": "T_January_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر يناير عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر يناير (°C)"
    },
    {
        "short_name": "T_FebMean",
        "full_name": "T_February_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر فبراير عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر فبراير (°C)"
    },
    {
        "short_name": "T_MarMean",
        "full_name": "T_March_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر مارس عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر مارس (°C)"
    },
    {
        "short_name": "T_AprMean",
        "full_name": "T_April_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر أبريل عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر أبريل (°C)"
    },
    {
        "short_name": "T_MayMean",
        "full_name": "T_May_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر مايو عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر مايو (°C)"
    },
    {
        "short_name": "T_JunMean",
        "full_name": "T_June_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر يونيو عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر يونيو (°C)"
    },
    {
        "short_name": "T_JulMean",
        "full_name": "T_July_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر يوليو عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر يوليو (°C)"
    },
    {
        "short_name": "T_AugMean",
        "full_name": "T_August_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر أغسطس عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر أغسطس (°C)"
    },
    {
        "short_name": "T_SepMean",
        "full_name": "T_September_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر سبتمبر عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر سبتمبر (°C)"
    },
    {
        "short_name": "T_OctMean",
        "full_name": "T_October_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر أكتوبر عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر أكتوبر (°C)"
    },
    {
        "short_name": "T_NovMean",
        "full_name": "T_November_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر نوفمبر عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر نوفمبر (°C)"
    },
    {
        "short_name": "T_DecMean",
        "full_name": "T_December_Mean",
        "module_code": "01_Temperature",
        "module_name": "01_Temperature (درجة الحرارة)",
        "desc_ar": u"المتوسط الحسابي لدرجة حرارة الهواء عند ارتفاع 2 متر لشهر ديسمبر عبر فترة الرصد 1996–2025.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة لشهر ديسمبر (°C)"
    },

    # --- 3. مؤشر الحرارة والراحة البيومناخية (11_Heat_Index) ---
    {
        "short_name": "HI_AnnMean",
        "full_name": "HI_Annual_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"المتوسط السنوي لمؤشر الحرارة المحسوسة المحسوب بمعادلة روتفوش وستيدمان للحرارة والرطوبة.",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي لمؤشر الحرارة المحسوسة (°C)"
    },
    {
        "short_name": "HI_SumMean",
        "full_name": "HI_Summer_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة خلال فصل الصيف (مقياس الإجهاد الحراري الفعلي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة خلال فصل الصيف (°C)"
    },
    {
        "short_name": "HI_SprMean",
        "full_name": "HI_Spring_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة خلال فصل الربيع (موسم الخماسين والتحول الحراري).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة خلال فصل الربيع (°C)"
    },
    {
        "short_name": "HI_AutMean",
        "full_name": "HI_Autumn_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة خلال فصل الخريف (الاحترار المتأخر في سبتمبر).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة خلال فصل الخريف (°C)"
    },
    {
        "short_name": "HI_WinMean",
        "full_name": "HI_Winter_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة الظاهرية/الهيوميدكس خلال فصل الشتاء في الأجواء الباردة والرطبة.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة الحرارة المحسوسة خلال فصل الشتاء (°C)"
    },
    {
        "short_name": "HI_AnRng",
        "full_name": "HI_Annual_Range",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"المدى السنوي لمؤشر الحرارة المحسوسة (الفارق بين أعلى شهر إجهاد حراري وأدنى شهر).",
        "unit": u"°C",
        "map_title": u"خريطة المدى السنوي لمؤشر الحرارة المحسوسة (°C)"
    },
    {
        "short_name": "HI_SeaRng",
        "full_name": "HI_Seasonal_Range",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"المدى الفصلي لمؤشر الحرارة المحسوسة (الفارق بين أعلى متوسط فصلي وأدناه).",
        "unit": u"°C",
        "map_title": u"خريطة المدى الفصلي لمؤشر الحرارة المحسوسة (°C)"
    },
    {
        "short_name": "WBGT_SuMn",
        "full_name": "WBGT_Summer_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط درجة حرارة البصيلة الرطبة الكروية الصيفي في الظل (معيار ISO 7243 للإجهاد المهني والرياضي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الإجهاد الحراري الصيفي (WBGT) (°C)"
    },
    {
        "short_name": "HI_JanMean",
        "full_name": "HI_January_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر يناير (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر يناير (°C)"
    },
    {
        "short_name": "HI_FebMean",
        "full_name": "HI_February_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر فبراير (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر فبراير (°C)"
    },
    {
        "short_name": "HI_MarMean",
        "full_name": "HI_March_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر مارس (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر مارس (°C)"
    },
    {
        "short_name": "HI_AprMean",
        "full_name": "HI_April_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر أبريل (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر أبريل (°C)"
    },
    {
        "short_name": "HI_MayMean",
        "full_name": "HI_May_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر مايو (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر مايو (°C)"
    },
    {
        "short_name": "HI_JunMean",
        "full_name": "HI_June_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر يونيو (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر يونيو (°C)"
    },
    {
        "short_name": "HI_JulMean",
        "full_name": "HI_July_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر يوليو (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر يوليو (°C)"
    },
    {
        "short_name": "HI_AugMean",
        "full_name": "HI_August_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر أغسطس (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر أغسطس (°C)"
    },
    {
        "short_name": "HI_SepMean",
        "full_name": "HI_September_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر سبتمبر (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر سبتمبر (°C)"
    },
    {
        "short_name": "HI_OctMean",
        "full_name": "HI_October_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر أكتوبر (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر أكتوبر (°C)"
    },
    {
        "short_name": "HI_NovMean",
        "full_name": "HI_November_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر نوفمبر (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر نوفمبر (°C)"
    },
    {
        "short_name": "HI_DecMean",
        "full_name": "HI_December_Mean",
        "module_code": "11_Heat_Index",
        "module_name": "11_Heat_Index (مؤشر الحرارة)",
        "desc_ar": u"متوسط مؤشر الحرارة المحسوسة (روثفوز) لشهر ديسمبر (خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مؤشر الحرارة المحسوسة لشهر ديسمبر (°C)"
    },

    # --- 4. نقطة الندى (07_Dew_Point) ---
    {
        "short_name": "Td_AnnMean",
        "full_name": "Td_Annual_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"المتوسط الحسابي السنوي لدرجة حرارة نقطة الندى عند ارتفاع 2 متر.",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي لدرجة حرارة نقطة الندى (°C)"
    },
    {
        "short_name": "Td_MonMean",
        "full_name": "Td_Month_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (درجة حرارة نقطة الندى)",
        "desc_ar": u"المتوسط الشهري لدرجة حرارة نقطة الندى عند ارتفاع 2 متر (متوسط الـ 12 شهراً).",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط الشهري لنقطة الندى (°C)"
    },
    {
        "short_name": "Td_WinMean",
        "full_name": "Td_Winter_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى خلال فصل الشتاء الأرصادي (DJF).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى خلال فصل الشتاء (°C)"
    },
    {
        "short_name": "Td_SprMean",
        "full_name": "Td_Spring_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى خلال فصل الربيع الأرصادي (MAM).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى خلال فصل الربيع (°C)"
    },
    {
        "short_name": "Td_SumMean",
        "full_name": "Td_Summer_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى خلال فصل الصيف الأرصادي (JJA - مؤشر مباشر للرطوبة الخانقة والكتمة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى خلال فصل الصيف (°C)"
    },
    {
        "short_name": "Td_AutMean",
        "full_name": "Td_Autumn_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى خلال فصل الخريف الأرصادي (SON).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى خلال فصل الخريف (°C)"
    },
    {
        "short_name": "Td_AnnRng",
        "full_name": "Td_Annual_Range",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"المدى السنوي لدرجة حرارة نقطة الندى (الفارق بين أعلى وأدنى متوسط شهري لنقطة الندى).",
        "unit": u"°C",
        "map_title": u"خريطة المدى السنوي لدرجة حرارة نقطة الندى (°C)"
    },
    {
        "short_name": "Td_SeaRng",
        "full_name": "Td_Seasonal_Range",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"المدى الفصلي لنقطة الندى (الفارق بين أعلى وأدنى فصول السنة).",
        "unit": u"°C",
        "map_title": u"خريطة المدى الفصلي لنقطة الندى (°C)"
    },
    {
        "short_name": "Td_JanMean",
        "full_name": "Td_January_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر يناير.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر يناير (°C)"
    },
    {
        "short_name": "Td_FebMean",
        "full_name": "Td_February_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر فبراير.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر فبراير (°C)"
    },
    {
        "short_name": "Td_MarMean",
        "full_name": "Td_March_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر مارس.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر مارس (°C)"
    },
    {
        "short_name": "Td_AprMean",
        "full_name": "Td_April_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر أبريل.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر أبريل (°C)"
    },
    {
        "short_name": "Td_MayMean",
        "full_name": "Td_May_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر مايو.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر مايو (°C)"
    },
    {
        "short_name": "Td_JunMean",
        "full_name": "Td_June_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر يونيو.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر يونيو (°C)"
    },
    {
        "short_name": "Td_JulMean",
        "full_name": "Td_July_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر يوليو.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر يوليو (°C)"
    },
    {
        "short_name": "Td_AugMean",
        "full_name": "Td_August_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر أغسطس.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر أغسطس (°C)"
    },
    {
        "short_name": "Td_SepMean",
        "full_name": "Td_September_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر سبتمبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر سبتمبر (°C)"
    },
    {
        "short_name": "Td_OctMean",
        "full_name": "Td_October_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر أكتوبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر أكتوبر (°C)"
    },
    {
        "short_name": "Td_NovMean",
        "full_name": "Td_November_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر نوفمبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر نوفمبر (°C)"
    },
    {
        "short_name": "Td_DecMean",
        "full_name": "Td_December_Mean",
        "module_code": "07_Dew_Point",
        "module_name": "07_Dew_Point (نقطة الندى)",
        "desc_ar": u"متوسط درجة حرارة نقطة الندى عند ارتفاع 2 متر لشهر ديسمبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة نقطة الندى لشهر ديسمبر (°C)"
    },

    # --- 5. التساقط والأمطار (02_Precipitation) ---
    {
        "short_name": "R_AnnMean",
        "full_name": "R_Annual_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"المتوسط السنوي لتساقط الأمطار (متوسط مجاميع السنين على مدار فترة الرصد 1996–2025).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة المتوسط السنوي لتساقط الأمطار (ملم)"
    },
    {
        "short_name": "R_MonMean",
        "full_name": "R_Month_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"المتوسط الشهري لتساقط الأمطار (المتوسط السنوي مقسوماً على 12 شهراً).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة المتوسط الشهري لتساقط الأمطار (ملم)"
    },
    {
        "short_name": "R_AnnRng",
        "full_name": "R_Annual_Range",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"المدى السنوي لتساقط الأمطار (الفارق بين أعلى شهر مطراً وأقل شهر مطراً في السنة).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة المدى السنوي لتساقط الأمطار (ملم)"
    },
    {
        "short_name": "R_SeaRng",
        "full_name": "R_Seasonal_Range",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"المدى الفصلي لتساقط الأمطار (الفارق بين مجموع أعلى فصول السنة مطراً ومجموع أقلها مطراً).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة المدى الفصلي لتساقط الأمطار (ملم)"
    },
    {
        "short_name": "R_WinMean",
        "full_name": "R_Winter_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط هطول الأمطار خلال فصل الشتاء (شهور ديسمبر، يناير، فبراير - DJF).",
        "unit": u"مم/فصل (mm/season)",
        "map_title": u"خريطة متوسط هطول الأمطار خلال فصل الشتاء (مم/فصل)"
    },
    {
        "short_name": "R_SprMean",
        "full_name": "R_Spring_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط هطول الأمطار خلال فصل الربيع (شهور مارس، أبريل، مايو - MAM).",
        "unit": u"مم/فصل (mm/season)",
        "map_title": u"خريطة متوسط هطول الأمطار خلال فصل الربيع (مم/فصل)"
    },
    {
        "short_name": "R_SumMean",
        "full_name": "R_Summer_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط هطول الأمطار خلال فصل الصيف (شهور يونيو، يوليو، أغسطس - JJA).",
        "unit": u"مم/فصل (mm/season)",
        "map_title": u"خريطة متوسط هطول الأمطار خلال فصل الصيف (مم/فصل)"
    },
    {
        "short_name": "R_AutMean",
        "full_name": "R_Autumn_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط هطول الأمطار خلال فصل الخريف (شهور سبتمبر، أكتوبر، نوفمبر - SON).",
        "unit": u"مم/فصل (mm/season)",
        "map_title": u"خريطة متوسط هطول الأمطار خلال فصل الخريف (مم/فصل)"
    },
    {
        "short_name": "R_AutTot",
        "full_name": "R_Autumn_Total",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"إجمالي كميات الأمطار التراكمية لفصل الخريف الأرصادي عبر سنوات فترة الرصد (SON).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة إجمالي كميات أمطار فصل الخريف (ملم)"
    },
    {
        "short_name": "R_JanMean",
        "full_name": "R_January_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر يناير عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر يناير (ملم/شهر)"
    },
    {
        "short_name": "R_FebMean",
        "full_name": "R_February_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر فبراير عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر فبراير (ملم/شهر)"
    },
    {
        "short_name": "R_MarMean",
        "full_name": "R_March_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر مارس عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر مارس (ملم/شهر)"
    },
    {
        "short_name": "R_AprMean",
        "full_name": "R_April_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر أبريل عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر أبريل (ملم/شهر)"
    },
    {
        "short_name": "R_MayMean",
        "full_name": "R_May_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر مايو عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر مايو (ملم/شهر)"
    },
    {
        "short_name": "R_JunMean",
        "full_name": "R_June_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر يونيو عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر يونيو (ملم/شهر)"
    },
    {
        "short_name": "R_JulMean",
        "full_name": "R_July_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر يوليو عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر يوليو (ملم/شهر)"
    },
    {
        "short_name": "R_AugMean",
        "full_name": "R_August_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر أغسطس عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر أغسطس (ملم/شهر)"
    },
    {
        "short_name": "R_SepMean",
        "full_name": "R_September_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر سبتمبر عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر سبتمبر (ملم/شهر)"
    },
    {
        "short_name": "R_OctMean",
        "full_name": "R_October_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر أكتوبر عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر أكتوبر (ملم/شهر)"
    },
    {
        "short_name": "R_NovMean",
        "full_name": "R_November_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر نوفمبر عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر نوفمبر (ملم/شهر)"
    },
    {
        "short_name": "R_DecMean",
        "full_name": "R_December_Mean",
        "module_code": "02_Precipitation",
        "module_name": "02_Precipitation (الأمطار)",
        "desc_ar": u"متوسط مجموع كميات الأمطار التراكمية لشهر ديسمبر عبر سنوات فترة الرصد 1996–2025.",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط مجموع أمطار شهر ديسمبر (ملم/شهر)"
    },

    # --- 6. ضغط مستوى سطح البحر (03_Sea_Level_Pressure) ---
    {
        "short_name": "PSL_AnMean",
        "full_name": "PSL_Annual_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي السنوي المصحح عند مستوى سطح البحر القياسي (Sea Level Pressure).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط الجوي عند مستوى سطح البحر (hPa)"
    },
    {
        "short_name": "PSL_MonMea",
        "full_name": "PSL_Month_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"المتوسط الشهري للضغط الجوي المصحح عند مستوى سطح البحر القياسي (متوسط الـ 12 شهراً).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة المتوسط الشهري لضغط مستوى سطح البحر (hPa)"
    },
    {
        "short_name": "PSL_WnMean",
        "full_name": "PSL_Winter_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي عند مستوى سطح البحر لفصل الشتاء الأرصادي (DJF).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر خلال فصل الشتاء (hPa)"
    },
    {
        "short_name": "PSL_SpMean",
        "full_name": "PSL_Spring_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي عند مستوى سطح البحر لفصل الربيع الأرصادي (MAM).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر خلال فصل الربيع (hPa)"
    },
    {
        "short_name": "PSL_SuMean",
        "full_name": "PSL_Summer_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي عند مستوى سطح البحر لفصل الصيف الأرصادي (JJA).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر خلال فصل الصيف (hPa)"
    },
    {
        "short_name": "PSL_AuMean",
        "full_name": "PSL_Autumn_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي عند مستوى سطح البحر لفصل الخريف الأرصادي (SON).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر خلال فصل الخريف (hPa)"
    },
    {
        "short_name": "PSL_AnRng",
        "full_name": "PSL_Annual_Range",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"المدى البارومتري السنوي لضغط مستوى البحر (الفارق بين أعلى وأدنى متوسط شهري للضغط).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة المدى السنوي لضغط مستوى سطح البحر (hPa)"
    },
    {
        "short_name": "PSL_SeaRng",
        "full_name": "PSL_Seasonal_Range",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"المدى الفصلي لضغط مستوى البحر (الفارق بين أعلى وأدنى فصول السنة ضغطاً).",
        "unit": u"hPa",
        "map_title": u"خريطة المدى الفصلي لضغط مستوى البحر (hPa)"
    },
    {
        "short_name": "PSL_JanMn",
        "full_name": "PSL_January_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر يناير (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر يناير (hPa)"
    },
    {
        "short_name": "PSL_FebMn",
        "full_name": "PSL_February_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر فبراير (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر فبراير (hPa)"
    },
    {
        "short_name": "PSL_MarMn",
        "full_name": "PSL_March_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر مارس (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر مارس (hPa)"
    },
    {
        "short_name": "PSL_AprMn",
        "full_name": "PSL_April_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر أبريل (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر أبريل (hPa)"
    },
    {
        "short_name": "PSL_MayMn",
        "full_name": "PSL_May_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر مايو (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر مايو (hPa)"
    },
    {
        "short_name": "PSL_JunMn",
        "full_name": "PSL_June_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر يونيو (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر يونيو (hPa)"
    },
    {
        "short_name": "PSL_JulMn",
        "full_name": "PSL_July_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر يوليو (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر يوليو (hPa)"
    },
    {
        "short_name": "PSL_AugMn",
        "full_name": "PSL_August_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر أغسطس (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر أغسطس (hPa)"
    },
    {
        "short_name": "PSL_SepMn",
        "full_name": "PSL_September_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر سبتمبر (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر سبتمبر (hPa)"
    },
    {
        "short_name": "PSL_OctMn",
        "full_name": "PSL_October_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر أكتوبر (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر أكتوبر (hPa)"
    },
    {
        "short_name": "PSL_NovMn",
        "full_name": "PSL_November_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر نوفمبر (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر نوفمبر (hPa)"
    },
    {
        "short_name": "PSL_DecMn",
        "full_name": "PSL_December_Mean",
        "module_code": "03_Sea_Level_Pressure",
        "module_name": "03_Sea_Level_Pressure (ضغط مستوى البحر)",
        "desc_ar": u"متوسط الضغط الجوي المصحح لمستوى سطح البحر القياسي لشهر ديسمبر (SLP).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط ضغط مستوى سطح البحر لشهر ديسمبر (hPa)"
    },

    # --- 7. الضغط الجوي السطحي الفعلي (04_Surface_Pressure) ---
    {
        "short_name": "PS_AnnMean",
        "full_name": "PS_Annual_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"المتوسط السنوي للضغط الجوي السطحي الفعلي الحقيقي عند منسوب تضاريس المحطة.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة المتوسط السنوي للضغط الجوي السطحي (hPa)"
    },
    {
        "short_name": "PS_MonMean",
        "full_name": "PS_Month_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"المتوسط الشهري للضغط الجوي السطحي الفعلي للمحطة (متوسط الـ 12 شهراً).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة المتوسط الشهري للضغط الجوي السطحي (hPa)"
    },
    {
        "short_name": "PS_WinMean",
        "full_name": "PS_Winter_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي لفصل الشتاء الأرصادي (DJF).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي خلال فصل الشتاء (hPa)"
    },
    {
        "short_name": "PS_SprMean",
        "full_name": "PS_Spring_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي لفصل الربيع الأرصادي (MAM).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي خلال فصل الربيع (hPa)"
    },
    {
        "short_name": "PS_SumMean",
        "full_name": "PS_Summer_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي لفصل الصيف الأرصادي (JJA).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي خلال فصل الصيف (hPa)"
    },
    {
        "short_name": "PS_AutMean",
        "full_name": "PS_Autumn_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي لفصل الخريف الأرصادي (SON).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي خلال فصل الخريف (hPa)"
    },
    {
        "short_name": "PS_AnnRng",
        "full_name": "PS_Annual_Range",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"المدى البارومتري السنوي للضغط السطحي (الفارق بين أعلى وأدنى متوسط شهري للضغط السطحي).",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة المدى السنوي للضغط الجوي السطحي (hPa)"
    },
    {
        "short_name": "PS_SeaRng",
        "full_name": "PS_Seasonal_Range",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"المدى الفصلي للضغط السطحي (الفارق بين فصول السنة).",
        "unit": u"hPa",
        "map_title": u"خريطة المدى الفصلي للضغط السطحي (hPa)"
    },
    {
        "short_name": "PS_JanMean",
        "full_name": "PS_January_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر يناير.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر يناير (hPa)"
    },
    {
        "short_name": "PS_FebMean",
        "full_name": "PS_February_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر فبراير.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر فبراير (hPa)"
    },
    {
        "short_name": "PS_MarMean",
        "full_name": "PS_March_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر مارس.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر مارس (hPa)"
    },
    {
        "short_name": "PS_AprMean",
        "full_name": "PS_April_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر أبريل.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر أبريل (hPa)"
    },
    {
        "short_name": "PS_MayMean",
        "full_name": "PS_May_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر مايو.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر مايو (hPa)"
    },
    {
        "short_name": "PS_JunMean",
        "full_name": "PS_June_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر يونيو.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر يونيو (hPa)"
    },
    {
        "short_name": "PS_JulMean",
        "full_name": "PS_July_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر يوليو.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر يوليو (hPa)"
    },
    {
        "short_name": "PS_AugMean",
        "full_name": "PS_August_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر أغسطس.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر أغسطس (hPa)"
    },
    {
        "short_name": "PS_SepMean",
        "full_name": "PS_September_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر سبتمبر.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر سبتمبر (hPa)"
    },
    {
        "short_name": "PS_OctMean",
        "full_name": "PS_October_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر أكتوبر.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر أكتوبر (hPa)"
    },
    {
        "short_name": "PS_NovMean",
        "full_name": "PS_November_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر نوفمبر.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر نوفمبر (hPa)"
    },
    {
        "short_name": "PS_DecMean",
        "full_name": "PS_December_Mean",
        "module_code": "04_Surface_Pressure",
        "module_name": "04_Surface_Pressure (الضغط السطحي)",
        "desc_ar": u"متوسط الضغط الجوي السطحي الفعلي الحقيقي عند منسوب المحطة لشهر ديسمبر.",
        "unit": u"hPa / mbar",
        "map_title": u"خريطة متوسط الضغط السطحي الفعلي لشهر ديسمبر (hPa)"
    },

    # --- 8. سرعة واتجاه الرياح (05_Wind) ---
    {
        "short_name": "WSp_AnMean",
        "full_name": "W_Spd_Annual_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"المتوسط السنوي لسرعة الرياح عند ارتفاع 10 أمتار فوق سطح الأرض.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة المتوسط السنوي لسرعة الرياح (م/ث)"
    },
    {
        "short_name": "WSp_MonMea",
        "full_name": "W_Spd_Month_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح السطحية)",
        "desc_ar": u"المتوسط الشهري لسرعة الرياح على ارتفاع 10 أمتار (متوسط الـ 12 شهراً).",
        "unit": u"m/s",
        "map_title": u"خريطة المتوسط الشهري لسرعة الرياح (m/s)"
    },
    {
        "short_name": "WSp_WnMean",
        "full_name": "W_Spd_Winter_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح لفصل الشتاء الأرصادي عند ارتفاع 10 أمتار (DJF).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح خلال فصل الشتاء (م/ث)"
    },
    {
        "short_name": "WSp_SpMean",
        "full_name": "W_Spd_Spring_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح لفصل الربيع الأرصادي عند ارتفاع 10 أمتار (MAM).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح خلال فصل الربيع (م/ث)"
    },
    {
        "short_name": "WSp_SuMean",
        "full_name": "W_Spd_Summer_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح لفصل الصيف الأرصادي عند ارتفاع 10 أمتار (JJA).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح خلال فصل الصيف (م/ث)"
    },
    {
        "short_name": "WSp_AuMean",
        "full_name": "W_Spd_Autumn_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح لفصل الخريف الأرصادي عند ارتفاع 10 أمتار (SON).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح خلال فصل الخريف (م/ث)"
    },
    {
        "short_name": "WSp_MaxMo",
        "full_name": "W_Spd_Annual_Max_Month",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"أقصى متوسط شهري مسجل لسرعة الرياح في السنة (ذروة النشاط الريحي).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة أقصى متوسط شهري لسرعة الرياح (م/ث)"
    },
    {
        "short_name": "WSp_MinMo",
        "full_name": "W_Spd_Annual_Min_Month",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"أدنى متوسط شهري مسجل لسرعة الرياح في السنة (فترة الهدوء الريحي).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة أدنى متوسط شهري لسرعة الرياح (م/ث)"
    },
    {
        "short_name": "WSp_AnRng",
        "full_name": "W_Spd_Annual_Range",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"المدى السنوي لسرعة الرياح (الفارق بين أشد شهور السنة رياحاً وأهدأها سرعة).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة المدى السنوي لسرعة الرياح (م/ث)"
    },
    {
        "short_name": "WSp_SeaRng",
        "full_name": "W_Spd_Seasonal_Range",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"المدى الفصلي لسرعة الرياح (الفارق بين أشد فصول السنة ريحاً وأهدأها).",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة المدى الفصلي لسرعة الرياح (م/ث)"
    },
    {
        "short_name": "WDr_AnMean",
        "full_name": "W_Dir_Annual_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"الاتجاه السائد السنوي للرياح بالدرجات الزاوية (محسوب بالمتوسط الدائري للمتجهات الدائرية atan2).",
        "unit": u"درجة (°)",
        "map_title": u"خريطة الاتجاه السائد السنوي للرياح (درجات)"
    },
    {
        "short_name": "WDr_MonMea",
        "full_name": "W_Dir_Month_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح السطحية)",
        "desc_ar": u"المتوسط الشهري لاتجاه الرياح السائدة (المتوسط الدائري للشهور الـ 12).",
        "unit": u"°",
        "map_title": u"خريطة المتوسط الشهري لاتجاه الرياح السائدة (°)"
    },
    {
        "short_name": "WDr_WnMean",
        "full_name": "W_Dir_Winter_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"اتجاه الرياح السائد خلال فصل الشتاء الأرصادي بالدرجات الزاوية (DJF).",
        "unit": u"درجة (°)",
        "map_title": u"خريطة اتجاه الرياح السائد خلال فصل الشتاء (درجات)"
    },
    {
        "short_name": "WDr_SpMean",
        "full_name": "W_Dir_Spring_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"اتجاه الرياح السائد خلال فصل الربيع الأرصادي بالدرجات الزاوية (MAM).",
        "unit": u"درجة (°)",
        "map_title": u"خريطة اتجاه الرياح السائد خلال فصل الربيع (درجات)"
    },
    {
        "short_name": "WDr_SuMean",
        "full_name": "W_Dir_Summer_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"اتجاه الرياح السائد خلال فصل الصيف الأرصادي بالدرجات الزاوية (JJA).",
        "unit": u"درجة (°)",
        "map_title": u"خريطة اتجاه الرياح السائد خلال فصل الصيف (درجات)"
    },
    {
        "short_name": "WDr_AuMean",
        "full_name": "W_Dir_Autumn_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"اتجاه الرياح السائد خلال فصل الخريف الأرصادي بالدرجات الزاوية (SON).",
        "unit": u"درجة (°)",
        "map_title": u"خريطة اتجاه الرياح السائد خلال فصل الخريف (درجات)"
    },
    {
        "short_name": "WSp_JanMn",
        "full_name": "W_Spd_January_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر يناير عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر يناير (م/ث)"
    },
    {
        "short_name": "WSp_FebMn",
        "full_name": "W_Spd_February_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر فبراير عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر فبراير (م/ث)"
    },
    {
        "short_name": "WSp_MarMn",
        "full_name": "W_Spd_March_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر مارس عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر مارس (م/ث)"
    },
    {
        "short_name": "WSp_AprMn",
        "full_name": "W_Spd_April_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر أبريل عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر أبريل (م/ث)"
    },
    {
        "short_name": "WSp_MayMn",
        "full_name": "W_Spd_May_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر مايو عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر مايو (م/ث)"
    },
    {
        "short_name": "WSp_JunMn",
        "full_name": "W_Spd_June_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر يونيو عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر يونيو (م/ث)"
    },
    {
        "short_name": "WSp_JulMn",
        "full_name": "W_Spd_July_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر يوليو عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر يوليو (م/ث)"
    },
    {
        "short_name": "WSp_AugMn",
        "full_name": "W_Spd_August_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر أغسطس عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر أغسطس (م/ث)"
    },
    {
        "short_name": "WSp_SepMn",
        "full_name": "W_Spd_September_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر سبتمبر عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر سبتمبر (م/ث)"
    },
    {
        "short_name": "WSp_OctMn",
        "full_name": "W_Spd_October_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر أكتوبر عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر أكتوبر (م/ث)"
    },
    {
        "short_name": "WSp_NovMn",
        "full_name": "W_Spd_November_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر نوفمبر عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر نوفمبر (م/ث)"
    },
    {
        "short_name": "WSp_DecMn",
        "full_name": "W_Spd_December_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط سرعة الرياح على ارتفاع 10 أمتار لشهر ديسمبر عبر فترة الرصد.",
        "unit": u"م/ث (m/s)",
        "map_title": u"خريطة متوسط سرعة الرياح لشهر ديسمبر (م/ث)"
    },
    {
        "short_name": "WDr_JanMn",
        "full_name": "W_Dir_January_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر يناير محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر يناير (°)"
    },
    {
        "short_name": "WDr_FebMn",
        "full_name": "W_Dir_February_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر فبراير محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر فبراير (°)"
    },
    {
        "short_name": "WDr_MarMn",
        "full_name": "W_Dir_March_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر مارس محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر مارس (°)"
    },
    {
        "short_name": "WDr_AprMn",
        "full_name": "W_Dir_April_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر أبريل محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر أبريل (°)"
    },
    {
        "short_name": "WDr_MayMn",
        "full_name": "W_Dir_May_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر مايو محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر مايو (°)"
    },
    {
        "short_name": "WDr_JunMn",
        "full_name": "W_Dir_June_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر يونيو محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر يونيو (°)"
    },
    {
        "short_name": "WDr_JulMn",
        "full_name": "W_Dir_July_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر يوليو محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر يوليو (°)"
    },
    {
        "short_name": "WDr_AugMn",
        "full_name": "W_Dir_August_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر أغسطس محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر أغسطس (°)"
    },
    {
        "short_name": "WDr_SepMn",
        "full_name": "W_Dir_September_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر سبتمبر محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر سبتمبر (°)"
    },
    {
        "short_name": "WDr_OctMn",
        "full_name": "W_Dir_October_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر أكتوبر محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر أكتوبر (°)"
    },
    {
        "short_name": "WDr_NovMn",
        "full_name": "W_Dir_November_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر نوفمبر محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر نوفمبر (°)"
    },
    {
        "short_name": "WDr_DecMn",
        "full_name": "W_Dir_December_Mean",
        "module_code": "05_Wind",
        "module_name": "05_Wind (الرياح)",
        "desc_ar": u"متوسط اتجاه الرياح السائد لشهر ديسمبر محسوب بالمتوسط الدائري المتجهي (atan2).",
        "unit": u"درجة (°) / Degree",
        "map_title": u"خريطة اتجاه الرياح السائد لشهر ديسمبر (°)"
    },

    # --- 9. الرطوبة النسبية (06_Relative_Humidity) ---
    {
        "short_name": "RH_AnMean",
        "full_name": "RH_Annual_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"المتوسط الحسابي السنوي للرطوبة النسبية للهواء عند ارتفاع 2 متر كنسبة مئوية.",
        "unit": u"%",
        "map_title": u"خريطة المتوسط السنوي للرطوبة النسبية (%)"
    },
    {
        "short_name": "RH_MonMean",
        "full_name": "RH_Month_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"المتوسط الشهري للرطوبة النسبية عند ارتفاع 2 متر (متوسط الـ 12 شهراً).",
        "unit": u"%",
        "map_title": u"خريطة المتوسط الشهري للرطوبة النسبية (%)"
    },
    {
        "short_name": "RH_WnMean",
        "full_name": "RH_Winter_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية لفصل الشتاء الأرصادي (DJF).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية خلال فصل الشتاء (%)"
    },
    {
        "short_name": "RH_SpMean",
        "full_name": "RH_Spring_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية لفصل الربيع الأرصادي (MAM).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية خلال فصل الربيع (%)"
    },
    {
        "short_name": "RH_SuMean",
        "full_name": "RH_Summer_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية لفصل الصيف الأرصادي (JJA).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية خلال فصل الصيف (%)"
    },
    {
        "short_name": "RH_AuMean",
        "full_name": "RH_Autumn_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية لفصل الخريف الأرصادي (SON).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية خلال فصل الخريف (%)"
    },
    {
        "short_name": "RH_AnRng",
        "full_name": "RH_Annual_Range",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"المدى السنوي للرطوبة النسبية (الفارق بين أعلى شهر رطوبة وأدنى شهر رطوبة).",
        "unit": u"%",
        "map_title": u"خريطة المدى السنوي للرطوبة النسبية (%)"
    },
    {
        "short_name": "RH_SeaRng",
        "full_name": "RH_Seasonal_Range",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"المدى الفصلي للرطوبة النسبية (الفارق بين أكثر فصول السنة رطوبة وأجفها).",
        "unit": u"%",
        "map_title": u"خريطة المدى الفصلي للرطوبة النسبية (%)"
    },
    {
        "short_name": "RH_JanMean",
        "full_name": "RH_January_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر يناير عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر يناير (%)"
    },
    {
        "short_name": "RH_FebMean",
        "full_name": "RH_February_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر فبراير عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر فبراير (%)"
    },
    {
        "short_name": "RH_MarMean",
        "full_name": "RH_March_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر مارس عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر مارس (%)"
    },
    {
        "short_name": "RH_AprMean",
        "full_name": "RH_April_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر أبريل عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر أبريل (%)"
    },
    {
        "short_name": "RH_MayMean",
        "full_name": "RH_May_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر مايو عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر مايو (%)"
    },
    {
        "short_name": "RH_JunMean",
        "full_name": "RH_June_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر يونيو عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر يونيو (%)"
    },
    {
        "short_name": "RH_JulMean",
        "full_name": "RH_July_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر يوليو عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر يوليو (%)"
    },
    {
        "short_name": "RH_AugMean",
        "full_name": "RH_August_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر أغسطس عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر أغسطس (%)"
    },
    {
        "short_name": "RH_SepMean",
        "full_name": "RH_September_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر سبتمبر عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر سبتمبر (%)"
    },
    {
        "short_name": "RH_OctMean",
        "full_name": "RH_October_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر أكتوبر عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر أكتوبر (%)"
    },
    {
        "short_name": "RH_NovMean",
        "full_name": "RH_November_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر نوفمبر عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر نوفمبر (%)"
    },
    {
        "short_name": "RH_DecMean",
        "full_name": "RH_December_Mean",
        "module_code": "06_Relative_Humidity",
        "module_name": "06_Relative_Humidity (الرطوبة النسبية)",
        "desc_ar": u"متوسط الرطوبة النسبية عند ارتفاع 2 متر لشهر ديسمبر عبر فترة الرصد.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الرطوبة النسبية لشهر ديسمبر (%)"
    },

    # --- 10. الإشعاع الشمسي (08_Solar_Radiation) ---
    {
        "short_name": "Sol_AnMean",
        "full_name": "Sol_Annual_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المتوسط اليومي السنوي للإشعاع الشمسي الكلي السطحي الواصل لسطح الأرض في كافة ظروف السماء.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المتوسط اليومي السنوي للإشعاع الشمسي (kWh/m²/day)"
    },
    {
        "short_name": "Sol_MonMea",
        "full_name": "Sol_Month_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المتوسط الشهري للإشعاع الشمسي اليومي الساقط على السطح الأفقي (متوسط الـ 12 شهراً).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المتوسط الشهري للإشعاع الشمسي اليومي (kWh/m²/day)"
    },
    {
        "short_name": "Sol_AnTot",
        "full_name": "Sol_Annual_Total",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"إجمالي الطاقة الشمسية السنوية التراكمية الساقطة على المتر المربع في السنة كاملة.",
        "unit": u"kWh/m²/year",
        "map_title": u"خريطة إجمالي الطاقة الشمسية السنوية التراكمية (kWh/m²/year)"
    },
    {
        "short_name": "Sol_WnMean",
        "full_name": "Sol_Winter_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"متوسط الإشعاع الشمسي اليومي لفصل الشتاء الأرصادي (DJF).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة متوسط الإشعاع الشمسي خلال فصل الشتاء (kWh/m²/day)"
    },
    {
        "short_name": "Sol_SpMean",
        "full_name": "Sol_Spring_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"متوسط الإشعاع الشمسي اليومي لفصل الربيع الأرصادي (MAM).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة متوسط الإشعاع الشمسي خلال فصل الربيع (kWh/m²/day)"
    },
    {
        "short_name": "Sol_SuMean",
        "full_name": "Sol_Summer_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"متوسط الإشعاع الشمسي اليومي لفصل الصيف الأرصادي (JJA).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة متوسط الإشعاع الشمسي خلال فصل الصيف (kWh/m²/day)"
    },
    {
        "short_name": "Sol_AuMean",
        "full_name": "Sol_Autumn_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"متوسط الإشعاع الشمسي اليومي لفصل الخريف الأرصادي (SON).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة متوسط الإشعاع الشمسي خلال فصل الخريف (kWh/m²/day)"
    },
    {
        "short_name": "Sol_AnRng",
        "full_name": "Sol_Annual_Range",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المدى السنوي للإشعاع الشمسي (الفارق بين ذروة الإشعاع في الصيف وأدناه في الشتاء).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المدى السنوي للإشعاع الشمسي (kWh/m²/day)"
    },
    {
        "short_name": "Sol_SeaRng",
        "full_name": "Sol_Seasonal_Range",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المدى الفصلي للإشعاع الشمسي اليومي (الفارق بين فصول السنة).",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المدى الفصلي للإشعاع الشمسي (kWh/m²/day)"
    },
    {
        "short_name": "Sol_JanMn",
        "full_name": "Sol_January_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر يناير.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر يناير (kWh/m²/day)"
    },
    {
        "short_name": "Sol_FebMn",
        "full_name": "Sol_February_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر فبراير.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر فبراير (kWh/m²/day)"
    },
    {
        "short_name": "Sol_MarMn",
        "full_name": "Sol_March_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر مارس.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر مارس (kWh/m²/day)"
    },
    {
        "short_name": "Sol_AprMn",
        "full_name": "Sol_April_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر أبريل.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر أبريل (kWh/m²/day)"
    },
    {
        "short_name": "Sol_MayMn",
        "full_name": "Sol_May_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر مايو.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر مايو (kWh/m²/day)"
    },
    {
        "short_name": "Sol_JunMn",
        "full_name": "Sol_June_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر يونيو.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر يونيو (kWh/m²/day)"
    },
    {
        "short_name": "Sol_JulMn",
        "full_name": "Sol_July_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر يوليو.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر يوليو (kWh/m²/day)"
    },
    {
        "short_name": "Sol_AugMn",
        "full_name": "Sol_August_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر أغسطس.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر أغسطس (kWh/m²/day)"
    },
    {
        "short_name": "Sol_SepMn",
        "full_name": "Sol_September_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر سبتمبر.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر سبتمبر (kWh/m²/day)"
    },
    {
        "short_name": "Sol_OctMn",
        "full_name": "Sol_October_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر أكتوبر.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر أكتوبر (kWh/m²/day)"
    },
    {
        "short_name": "Sol_NovMn",
        "full_name": "Sol_November_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر نوفمبر.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر نوفمبر (kWh/m²/day)"
    },
    {
        "short_name": "Sol_DecMn",
        "full_name": "Sol_December_Mean",
        "module_code": "08_Solar_Radiation",
        "module_name": "08_Solar_Radiation (الإشعاع الشمسي)",
        "desc_ar": u"المعدل اليومي للإشعاع الشمسي الكلي الساقط على السطح الأفقي لشهر ديسمبر.",
        "unit": u"kWh/m²/day",
        "map_title": u"خريطة المعدل اليومي للإشعاع الشمسي لشهر ديسمبر (kWh/m²/day)"
    },

    # --- 11. مؤشر الأشعة فوق البنفسجية (09_UV_Index) ---
    {
        "short_name": "UV_AnMean",
        "full_name": "UV_Annual_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"المتوسط السنوي لمؤشر الأشعة فوق البنفسجية عند الظهيرة وفق منظومة منظمة الصحة العالمية.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة المتوسط السنوي لمؤشر الأشعة فوق البنفسجية (UV)"
    },
    {
        "short_name": "UV_MonMean",
        "full_name": "UV_Month_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (مؤشر الأشعة فوق البنفسجية)",
        "desc_ar": u"المتوسط الشهري لمؤشر الأشعة فوق البنفسجية في سماء صافية (متوسط الـ 12 شهراً).",
        "unit": u"Index",
        "map_title": u"خريطة المتوسط الشهري لمؤشر الأشعة فوق البنفسجية"
    },
    {
        "short_name": "UV_WnMean",
        "full_name": "UV_Winter_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية لفصل الشتاء الأرصادي (DJF).",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية خلال فصل الشتاء"
    },
    {
        "short_name": "UV_SpMean",
        "full_name": "UV_Spring_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية لفصل الربيع الأرصادي (MAM).",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية خلال فصل الربيع"
    },
    {
        "short_name": "UV_SuMean",
        "full_name": "UV_Summer_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية لفصل الصيف الأرصادي (JJA - ذروة مخاطر الحروق الشمسية).",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية خلال فصل الصيف"
    },
    {
        "short_name": "UV_AuMean",
        "full_name": "UV_Autumn_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية لفصل الخريف الأرصادي (SON).",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية خلال فصل الخريف"
    },
    {
        "short_name": "UV_AnRng",
        "full_name": "UV_Annual_Range",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"المدى السنوي لمؤشر الأشعة فوق البنفسجية (الفارق بين ذروة الصيف وأدنى مستويات الشتاء).",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة المدى السنوي لمؤشر الأشعة فوق البنفسجية"
    },
    {
        "short_name": "UV_SeaRng",
        "full_name": "UV_Seasonal_Range",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"المدى الفصلي لمؤشر الأشعة فوق البنفسجية (الفارق بين فصول السنة).",
        "unit": u"مؤشر (Index)",
        "map_title": u"خريطة المدى الفصلي لمؤشر الأشعة فوق البنفسجية"
    },
    {
        "short_name": "UV_JanMean",
        "full_name": "UV_January_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر يناير وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر يناير"
    },
    {
        "short_name": "UV_FebMean",
        "full_name": "UV_February_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر فبراير وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر فبراير"
    },
    {
        "short_name": "UV_MarMean",
        "full_name": "UV_March_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر مارس وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر مارس"
    },
    {
        "short_name": "UV_AprMean",
        "full_name": "UV_April_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر أبريل وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر أبريل"
    },
    {
        "short_name": "UV_MayMean",
        "full_name": "UV_May_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر مايو وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر مايو"
    },
    {
        "short_name": "UV_JunMean",
        "full_name": "UV_June_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر يونيو وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر يونيو"
    },
    {
        "short_name": "UV_JulMean",
        "full_name": "UV_July_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر يوليو وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر يوليو"
    },
    {
        "short_name": "UV_AugMean",
        "full_name": "UV_August_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر أغسطس وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر أغسطس"
    },
    {
        "short_name": "UV_SepMean",
        "full_name": "UV_September_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر سبتمبر وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر سبتمبر"
    },
    {
        "short_name": "UV_OctMean",
        "full_name": "UV_October_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر أكتوبر وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر أكتوبر"
    },
    {
        "short_name": "UV_NovMean",
        "full_name": "UV_November_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر نوفمبر وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر نوفمبر"
    },
    {
        "short_name": "UV_DecMean",
        "full_name": "UV_December_Mean",
        "module_code": "09_UV_Index",
        "module_name": "09_UV_Index (الأشعة فوق البنفسجية)",
        "desc_ar": u"متوسط مؤشر الأشعة فوق البنفسجية القصوى لشهر ديسمبر وفق معيار WHO.",
        "unit": u"مؤشر (0-16+)",
        "map_title": u"خريطة متوسط مؤشر الأشعة فوق البنفسجية لشهر ديسمبر"
    },

    # --- 12. الغطاء السحابي (10_Cloud_Cover) ---
    {
        "short_name": "Cld_AnMean",
        "full_name": "Cld_Annual_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"المتوسط السنوي لنسبة تغطية السماء بالغيوم والسحب كنسبة مئوية.",
        "unit": u"%",
        "map_title": u"خريطة المتوسط السنوي لنسبة الغطاء السحابي (%)"
    },
    {
        "short_name": "Cld_MonMea",
        "full_name": "Cld_Month_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"المتوسط الشهري لكمية الغطاء السحابي الكلي (متوسط الـ 12 شهراً).",
        "unit": u"%",
        "map_title": u"خريطة المتوسط الشهري للغطاء السحابي (%)"
    },
    {
        "short_name": "Cld_WnMean",
        "full_name": "Cld_Winter_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة تغطية السحب لفصل الشتاء الأرصادي (DJF).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي خلال فصل الشتاء (%)"
    },
    {
        "short_name": "Cld_SpMean",
        "full_name": "Cld_Spring_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة تغطية السحب لفصل الربيع الأرصادي (MAM).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي خلال فصل الربيع (%)"
    },
    {
        "short_name": "Cld_SuMean",
        "full_name": "Cld_Summer_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة تغطية السحب لفصل الصيف الأرصادي (JJA).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي خلال فصل الصيف (%)"
    },
    {
        "short_name": "Cld_AuMean",
        "full_name": "Cld_Autumn_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة تغطية السحب لفصل الخريف الأرصادي (SON).",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي خلال فصل الخريف (%)"
    },
    {
        "short_name": "Cld_AnRng",
        "full_name": "Cld_Annual_Range",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"المدى السنوي لتغطية السحب (الفارق بين أكثر شهور السنة غيوماً وأكثرها صفاءً).",
        "unit": u"%",
        "map_title": u"خريطة المدى السنوي لنسبة الغطاء السحابي (%)"
    },
    {
        "short_name": "Cld_SeaRng",
        "full_name": "Cld_Seasonal_Range",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"المدى الفصلي للغطاء السحابي (الفارق بين أعلى فصول السنة غيوماً وأصفاها).",
        "unit": u"%",
        "map_title": u"خريطة المدى الفصلي للغطاء السحابي (%)"
    },
    {
        "short_name": "Cld_JanMn",
        "full_name": "Cld_January_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر يناير.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر يناير (%)"
    },
    {
        "short_name": "Cld_FebMn",
        "full_name": "Cld_February_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر فبراير.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر فبراير (%)"
    },
    {
        "short_name": "Cld_MarMn",
        "full_name": "Cld_March_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر مارس.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر مارس (%)"
    },
    {
        "short_name": "Cld_AprMn",
        "full_name": "Cld_April_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر أبريل.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر أبريل (%)"
    },
    {
        "short_name": "Cld_MayMn",
        "full_name": "Cld_May_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر مايو.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر مايو (%)"
    },
    {
        "short_name": "Cld_JunMn",
        "full_name": "Cld_June_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر يونيو.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر يونيو (%)"
    },
    {
        "short_name": "Cld_JulMn",
        "full_name": "Cld_July_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر يوليو.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر يوليو (%)"
    },
    {
        "short_name": "Cld_AugMn",
        "full_name": "Cld_August_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر أغسطس.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر أغسطس (%)"
    },
    {
        "short_name": "Cld_SepMn",
        "full_name": "Cld_September_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر سبتمبر.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر سبتمبر (%)"
    },
    {
        "short_name": "Cld_OctMn",
        "full_name": "Cld_October_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر أكتوبر.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر أكتوبر (%)"
    },
    {
        "short_name": "Cld_NovMn",
        "full_name": "Cld_November_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر نوفمبر.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر نوفمبر (%)"
    },
    {
        "short_name": "Cld_DecMn",
        "full_name": "Cld_December_Mean",
        "module_code": "10_Cloud_Cover",
        "module_name": "10_Cloud_Cover (الغطاء السحابي)",
        "desc_ar": u"متوسط نسبة الغطاء السحابي الكلي للسماء لشهر ديسمبر.",
        "unit": u"%",
        "map_title": u"خريطة متوسط الغطاء السحابي لشهر ديسمبر (%)"
    },

    # --- 13. مؤشر البرودة الريحية (12_Wind_Chill) ---
    {
        "short_name": "WC_WinMean",
        "full_name": "WC_Winter_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط درجة البرودة الريحية لفصل الشتاء المحسوبة بمعادلة NWS لخفض الحرارة بفعل سرعة الرياح.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح خلال فصل الشتاء (°C)"
    },
    {
        "short_name": "WC_SprMean",
        "full_name": "WC_Spring_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح خلال فصل الربيع (خيار إضافي للمناطق الباردة صيفاً/ربيعاً).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح خلال فصل الربيع (°C)"
    },
    {
        "short_name": "WC_SumMean",
        "full_name": "WC_Summer_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح خلال فصل الصيف (خيار إضافي للمناطق الباردة صيفاً).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح خلال فصل الصيف (°C)"
    },
    {
        "short_name": "WC_AutMean",
        "full_name": "WC_Autumn_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح خلال فصل الخريف (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح خلال فصل الخريف (°C)"
    },
    {
        "short_name": "WC_JanMean",
        "full_name": "WC_January_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر يناير (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر يناير (°C)"
    },
    {
        "short_name": "WC_FebMean",
        "full_name": "WC_February_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر فبراير (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر فبراير (°C)"
    },
    {
        "short_name": "WC_MarMean",
        "full_name": "WC_March_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر مارس (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر مارس (°C)"
    },
    {
        "short_name": "WC_AprMean",
        "full_name": "WC_April_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر أبريل (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر أبريل (°C)"
    },
    {
        "short_name": "WC_MayMean",
        "full_name": "WC_May_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر مايو (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر مايو (°C)"
    },
    {
        "short_name": "WC_JunMean",
        "full_name": "WC_June_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر يونيو (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر يونيو (°C)"
    },
    {
        "short_name": "WC_JulMean",
        "full_name": "WC_July_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر يوليو (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر يوليو (°C)"
    },
    {
        "short_name": "WC_AugMean",
        "full_name": "WC_August_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر أغسطس (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر أغسطس (°C)"
    },
    {
        "short_name": "WC_SepMean",
        "full_name": "WC_September_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر سبتمبر (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر سبتمبر (°C)"
    },
    {
        "short_name": "WC_OctMean",
        "full_name": "WC_October_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر أكتوبر (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر أكتوبر (°C)"
    },
    {
        "short_name": "WC_NovMean",
        "full_name": "WC_November_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر نوفمبر (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر نوفمبر (°C)"
    },
    {
        "short_name": "WC_DecMean",
        "full_name": "WC_December_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"متوسط مبرد الرياح لشهر ديسمبر (خيار إضافي للمناطق الباردة).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط مبرد الرياح لشهر ديسمبر (°C)"
    },
    {
        "short_name": "WC_AnRng",
        "full_name": "WC_Annual_Range",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"المدى السنوي لمبرد الرياح (الفارق بين أعلى شهر وأدناه، خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة المدى السنوي لمبرد الرياح (°C)"
    },
    {
        "short_name": "WC_SeaRng",
        "full_name": "WC_Seasonal_Range",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"المدى الفصلي لمبرد الرياح (الفارق بين أعلى فصل وأدناه، خيار إضافي).",
        "unit": u"°C",
        "map_title": u"خريطة المدى الفصلي لمبرد الرياح (°C)"
    },
    {
        "short_name": "WC_AnnMean",
        "full_name": "WC_Annual_Mean",
        "module_code": "12_Wind_Chill",
        "module_name": "12_Wind_Chill (مبرد الرياح)",
        "desc_ar": u"المتوسط الحسابي السنوي لتأثير البرودة الريحية على حرارة الهواء المحسوسة.",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي لمبرد الرياح (°C)"
    },

    # --- 14. مؤشر دي مارتون للقحولة (13_De_Martonne_Aridity) ---
    {
        "short_name": "DM_AridAnn",
        "full_name": "DM_Aridity_Annual",
        "module_code": "13_De_Martonne_Aridity",
        "module_name": "13_De_Martonne_Aridity (دليل دي مارتون)",
        "desc_ar": u"دليل القحولة والجفاف السنوي لدي مارتون I = P / (T + 10) لتصنيف الأقاليم من القاحل فائق الجفاف إلى الرطب.",
        "unit": u"مؤشر (Index)",
        "map_title": u"خريطة دليل دي مارتون السنوي للقحولة والجفاف"
    },

    # --- 15. البخر والنتح (14_Evapotranspiration) ---
    {
        "short_name": "ET_AnnMean",
        "full_name": "ET_Annual_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط مجموع البخر والنتح السنوي (متوسط السنة الواحدة من التراكمات بهارجريفز-ساماني FAO-56، يقابل R_Annual_Mean للمطر).",
        "unit": u"ملم/سنة (mm/year)",
        "map_title": u"خريطة المتوسط السنوي للبخر والنتح (ملم/سنة)"
    },
    {
        "short_name": "ET_MonMean",
        "full_name": "ET_Month_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر-نتح المرجعي)",
        "desc_ar": u"المعدل الشهري للبخر-نتح المرجعي المحسوب بطريقة هارجريفز (متوسط الشهور = المجموع السنوي / 12).",
        "unit": u"mm/month",
        "map_title": u"خريطة المتوسط الشهري للبخر والنتح المرجعي (mm/month)"
    },
    {
        "short_name": "ET_AnnRng",
        "full_name": "ET_Annual_Range",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"المدى السنوي للبخر والنتح (الفارق بين أعلى شهور السنة فقداً للماء بالبخر والنتح وأدناها).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة المدى السنوي للبخر والنتح (ملم)"
    },
    {
        "short_name": "ET_SeaRng",
        "full_name": "ET_Seasonal_Range",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"المدى الفصلي للبخر والنتح (الفارق بين مجموع أعلى فصول السنة في البخر والنتح ومجموع أقلها).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة المدى الفصلي للبخر والنتح (ملم)"
    },
    {
        "short_name": "ET_WinMean",
        "full_name": "ET_Winter_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لفصل الشتاء (متوسط مجموع ديسمبر، يناير، فبراير - DJF).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة متوسط البخر والنتح خلال فصل الشتاء (ملم)"
    },
    {
        "short_name": "ET_SprMean",
        "full_name": "ET_Spring_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لفصل الربيع (متوسط مجموع مارس، أبريل، مايو - MAM).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة متوسط البخر والنتح خلال فصل الربيع (ملم)"
    },
    {
        "short_name": "ET_SumMean",
        "full_name": "ET_Summer_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لفصل الصيف (متوسط مجموع يونيو، يوليو، أغسطس - JJA).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة متوسط البخر والنتح خلال فصل الصيف (ملم)"
    },
    {
        "short_name": "ET_AutMean",
        "full_name": "ET_Autumn_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لفصل الخريف (متوسط مجموع سبتمبر، أكتوبر، نوفمبر - SON).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة متوسط البخر والنتح خلال فصل الخريف (ملم)"
    },
    {
        "short_name": "PET_HarAnn",
        "full_name": "PET_Hargreaves_Annual",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"التبخر-نتح الكامن السنوي بهارجريفز (حقل رديف مطابق تماماً لـ ET_Annual_Mean للتوافقية العكسية).",
        "unit": u"ملم/سنة (mm/year)",
        "map_title": u"خريطة التبخر والنتح الكامن السنوي بهارجريفز (ملم/سنة)"
    },
    {
        "short_name": "ET_JanMean",
        "full_name": "ET_January_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر يناير بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر يناير (ملم/شهر)"
    },
    {
        "short_name": "ET_FebMean",
        "full_name": "ET_February_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر فبراير بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر فبراير (ملم/شهر)"
    },
    {
        "short_name": "ET_MarMean",
        "full_name": "ET_March_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر مارس بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر مارس (ملم/شهر)"
    },
    {
        "short_name": "ET_AprMean",
        "full_name": "ET_April_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر أبريل بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر أبريل (ملم/شهر)"
    },
    {
        "short_name": "ET_MayMean",
        "full_name": "ET_May_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر مايو بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر مايو (ملم/شهر)"
    },
    {
        "short_name": "ET_JunMean",
        "full_name": "ET_June_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر يونيو بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر يونيو (ملم/شهر)"
    },
    {
        "short_name": "ET_JulMean",
        "full_name": "ET_July_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر يوليو بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر يوليو (ملم/شهر)"
    },
    {
        "short_name": "ET_AugMean",
        "full_name": "ET_August_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر أغسطس بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر أغسطس (ملم/شهر)"
    },
    {
        "short_name": "ET_SepMean",
        "full_name": "ET_September_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر سبتمبر بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر سبتمبر (ملم/شهر)"
    },
    {
        "short_name": "ET_OctMean",
        "full_name": "ET_October_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر أكتوبر بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر أكتوبر (ملم/شهر)"
    },
    {
        "short_name": "ET_NovMean",
        "full_name": "ET_November_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر نوفمبر بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر نوفمبر (ملم/شهر)"
    },
    {
        "short_name": "ET_DecMean",
        "full_name": "ET_December_Mean",
        "module_code": "14_Evapotranspiration",
        "module_name": "14_Evapotranspiration (البخر والنتح)",
        "desc_ar": u"متوسط البخر والنتح لشهر ديسمبر بطريقة هارجريفز-ساماني (ملم/شهر).",
        "unit": u"ملم/شهر (mm/month)",
        "map_title": u"خريطة متوسط البخر والنتح لشهر ديسمبر (ملم/شهر)"
    },

    # --- 16. مؤشر القحولة العالمي (15_UNEP_Aridity) ---
    {
        "short_name": "UNEP_Arid",
        "full_name": "UNEP_Aridity_Annual",
        "module_code": "15_UNEP_Aridity",
        "module_name": "15_UNEP_Aridity (مؤشر UNEP)",
        "desc_ar": u"مؤشر القحولة العالمي لبرنامج الأمم المتحدة للبيئة AI = P / ET_ann لتحديد المناطق القاحلة وشبه القاحلة.",
        "unit": u"نسبة (Ratio)",
        "map_title": u"خريطة مؤشر القحولة العالمي لبرنامج الأمم المتحدة للبيئة"
    },

    # --- 17. الموازنة والعجز المائي المناخي (16_Water_Deficit) ---
    {
        "short_name": "WatDefAnn",
        "full_name": "Water_Deficit_Annual",
        "module_code": "16_Water_Deficit",
        "module_name": "16_Water_Deficit (العجز المائي)",
        "desc_ar": u"الموازنة المائية المناخية السنوية الصافية WD = P - ET_ann (القيم السالبة تعبر عن عجز مائي والموجبة فائض مائي).",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة الموازنة والعجز المائي المناخي السنوي (ملم)"
    },

    # --- 18. الأشهر الجافة بيولوجياً (17_Dry_Months) ---
    {
        "short_name": "Dry_Months",
        "full_name": "Dry_Months_Count",
        "module_code": "17_Dry_Months",
        "module_name": "17_Dry_Months (الأشهر الجافة)",
        "desc_ar": u"عدد أشهر السنة الجافة بيولوجياً ومناخياً وفق معيار والتر-ليث البيومناخي الشهير (P < 2T).",
        "unit": u"شهر (0-12)",
        "map_title": u"خريطة عدد الأشهر الجافة بيولوجياً في السنة"
    },

    # --- 19. الاتجاهات والشذوذ المناخي (18_Trends_And_Anomalies) ---
    {
        "short_name": "T_AnnTrDec",
        "full_name": "T_Annual_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه درجة الحرارة لكل عقد زمني (10 سنوات) باستخدام انحدار المربعات الصغرى الخطي.",
        "unit": u"°C/decade",
        "map_title": u"خريطة اتجاه تغير درجة الحرارة في العقد الزمني (°C/decade)"
    },
    {
        "short_name": "R_AnnTrDec",
        "full_name": "R_Annual_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه تساقط الأمطار لكل عقد زمني (10 سنوات) باستخدام انحدار المربعات الصغرى الخطي.",
        "unit": u"mm/decade",
        "map_title": u"خريطة اتجاه تغير تساقط الأمطار في العقد الزمني (mm/decade)"
    },
    {
        "short_name": "T_AnnAnom",
        "full_name": "T_Annual_Anom",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"الشذوذ الحراري السنوي لدرجة الحرارة مقارنة بخط الأساس المناخي العالمي 1991–2020.",
        "unit": u"°C",
        "map_title": u"خريطة الشذوذ الحراري السنوي مقارنة بخط أساس 1991–2020 (°C)"
    },
    {
        "short_name": "T_AnomWin",
        "full_name": "T_Anom_Winter",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"الشذوذ الحراري لفصل الشتاء مقارنة بمتوسط شهور الشتاء لخط الأساس المناخي 1991–2020.",
        "unit": u"°C",
        "map_title": u"خريطة الشذوذ الحراري لفصل الشتاء مقارنة بخط أساس 1991–2020 (°C)"
    },
    {
        "short_name": "T_AnomSum",
        "full_name": "T_Anom_Summer",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"الشذوذ الحراري لفصل الصيف مقارنة بمتوسط شهور الصيف لخط الأساس المناخي 1991–2020.",
        "unit": u"°C",
        "map_title": u"خريطة الشذوذ الحراري لفصل الصيف مقارنة بخط أساس 1991–2020 (°C)"
    },
    {
        "short_name": "R_AnnAnom",
        "full_name": "R_Annual_Anom",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ الأمطار السنوي المطلق مقارنة بمتوسط الأمطار لخط الأساس المناخي 1991–2020.",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة شذوذ تساقط الأمطار السنوي مقارنة بخط أساس 1991–2020 (ملم)"
    },
    {
        "short_name": "R_AnnAnPct",
        "full_name": "R_Annual_Anom_Pct",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ الأمطار السنوي كنسبة مئوية من خط الأساس المناخي 1991–2020 (فرق نسبي مئوي).",
        "unit": u"%",
        "map_title": u"خريطة الشذوذ النسبي المئوي للأمطار مقارنة بخط أساس 1991–2020 (%)"
    },
    {
        "short_name": "R_AnomWin",
        "full_name": "R_Anom_Winter",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الشتاء المطلق مقارنة بأمطار شتاء خط الأساس المناخي 1991–2020.",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة شذوذ أمطار الشتاء مقارنة بخط أساس 1991–2020 (ملم)"
    },
    {
        "short_name": "R_AnomWPct",
        "full_name": "R_Anom_Winter_Pct",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الشتاء كنسبة مئوية مقارنة بأمطار شتاء خط الأساس المناخي 1991–2020.",
        "unit": u"%",
        "map_title": u"خريطة الشذوذ النسبي المئوي لأمطار الشتاء مقارنة بخط أساس 1991–2020 (%)"
    },
    {
        "short_name": "T_WinTrDec",
        "full_name": "T_Winter_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه درجة حرارة فصل الشتاء لكل عقد زمني (10 سنوات) باستخدام انحدار المربعات الصغرى.",
        "unit": u"°C/decade",
        "map_title": u"خريطة اتجاه تغير حرارة فصل الشتاء في العقد الزمني (°C/decade)"
    },
    {
        "short_name": "T_SprTrDec",
        "full_name": "T_Spring_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه درجة حرارة فصل الربيع لكل عقد زمني (10 سنوات) باستخدام انحدار المربعات الصغرى.",
        "unit": u"°C/decade",
        "map_title": u"خريطة اتجاه تغير حرارة فصل الربيع في العقد الزمني (°C/decade)"
    },
    {
        "short_name": "T_SumTrDec",
        "full_name": "T_Summer_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه درجة حرارة فصل الصيف لكل عقد زمني (10 سنوات) باستخدام انحدار المربعات الصغرى.",
        "unit": u"°C/decade",
        "map_title": u"خريطة اتجاه تغير حرارة فصل الصيف في العقد الزمني (°C/decade)"
    },
    {
        "short_name": "T_AutTrDec",
        "full_name": "T_Autumn_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه درجة حرارة فصل الخريف لكل عقد زمني (10 سنوات) باستخدام انحدار المربعات الصغرى.",
        "unit": u"°C/decade",
        "map_title": u"خريطة اتجاه تغير حرارة فصل الخريف في العقد الزمني (°C/decade)"
    },
    {
        "short_name": "T_AnomSpr",
        "full_name": "T_Anom_Spring",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"الشذوذ الحراري لفصل الربيع مقارنة بمتوسط شهور الربيع لخط الأساس المناخي 1991–2020.",
        "unit": u"°C",
        "map_title": u"خريطة الشذوذ الحراري لفصل الربيع مقارنة بخط أساس 1991–2020 (°C)"
    },
    {
        "short_name": "T_AnomAut",
        "full_name": "T_Anom_Autumn",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"الشذوذ الحراري لفصل الخريف مقارنة بمتوسط شهور الخريف لخط الأساس المناخي 1991–2020.",
        "unit": u"°C",
        "map_title": u"خريطة الشذوذ الحراري لفصل الخريف مقارنة بخط أساس 1991–2020 (°C)"
    },
    {
        "short_name": "R_WinTrDec",
        "full_name": "R_Winter_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه تساقط أمطار فصل الشتاء لكل عقد زمني (10 سنوات) بانحدار المربعات الصغرى.",
        "unit": u"mm/decade",
        "map_title": u"خريطة اتجاه تغير أمطار فصل الشتاء في العقد الزمني (mm/decade)"
    },
    {
        "short_name": "R_SprTrDec",
        "full_name": "R_Spring_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه تساقط أمطار فصل الربيع لكل عقد زمني (10 سنوات) بانحدار المربعات الصغرى.",
        "unit": u"mm/decade",
        "map_title": u"خريطة اتجاه تغير أمطار فصل الربيع في العقد الزمني (mm/decade)"
    },
    {
        "short_name": "R_SumTrDec",
        "full_name": "R_Summer_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه تساقط أمطار فصل الصيف لكل عقد زمني (10 سنوات) بانحدار المربعات الصغرى.",
        "unit": u"mm/decade",
        "map_title": u"خريطة اتجاه تغير أمطار فصل الصيف في العقد الزمني (mm/decade)"
    },
    {
        "short_name": "R_AutTrDec",
        "full_name": "R_Autumn_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه تساقط أمطار فصل الخريف لكل عقد زمني (10 سنوات) بانحدار المربعات الصغرى.",
        "unit": u"mm/decade",
        "map_title": u"خريطة اتجاه تغير أمطار فصل الخريف في العقد الزمني (mm/decade)"
    },
    {
        "short_name": "R_AnomSpr",
        "full_name": "R_Anom_Spring",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الربيع المطلق مقارنة بأمطار ربيع خط الأساس المناخي 1991–2020.",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة شذوذ أمطار فصل الربيع مقارنة بخط أساس 1991–2020 (ملم)"
    },
    {
        "short_name": "R_AnSpPct",
        "full_name": "R_Anom_Spring_Pct",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الربيع كنسبة مئوية مقارنة بأمطار ربيع خط الأساس المناخي 1991–2020.",
        "unit": u"%",
        "map_title": u"خريطة الشذوذ النسبي المئوي لأمطار الربيع مقارنة بخط أساس 1991–2020 (%)"
    },
    {
        "short_name": "R_AnomSum",
        "full_name": "R_Anom_Summer",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الصيف المطلق مقارنة بأمطار صيف خط الأساس المناخي 1991–2020.",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة شذوذ أمطار فصل الصيف مقارنة بخط أساس 1991–2020 (ملم)"
    },
    {
        "short_name": "R_AnSuPct",
        "full_name": "R_Anom_Summer_Pct",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الصيف كنسبة مئوية مقارنة بأمطار صيف خط الأساس المناخي 1991–2020.",
        "unit": u"%",
        "map_title": u"خريطة الشذوذ النسبي المئوي لأمطار الصيف مقارنة بخط أساس 1991–2020 (%)"
    },
    {
        "short_name": "R_AnomAut",
        "full_name": "R_Anom_Autumn",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الخريف المطلق مقارنة بأمطار خريف خط الأساس المناخي 1991–2020.",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة شذوذ أمطار فصل الخريف مقارنة بخط أساس 1991–2020 (ملم)"
    },
    {
        "short_name": "R_AnAuPct",
        "full_name": "R_Anom_Autumn_Pct",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ أمطار فصل الخريف كنسبة مئوية مقارنة بأمطار خريف خط الأساس المناخي 1991–2020.",
        "unit": u"%",
        "map_title": u"خريطة الشذوذ النسبي المئوي لأمطار الخريف مقارنة بخط أساس 1991–2020 (%)"
    },
    {
        "short_name": "T_MonTrDec",
        "full_name": "T_Month_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه درجة الحرارة الشهرية العامة لكل عقد زمني (10 سنوات).",
        "unit": u"°C/decade",
        "map_title": u"خريطة اتجاه تغير درجات الحرارة الشهرية في العقد الزمني (°C/decade)"
    },
    {
        "short_name": "T_AnomMon",
        "full_name": "T_Anom_Month",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"الشذوذ الحراري الشهري العام لدرجة الحرارة مقارنة بمتوسط الشهور لخط الأساس المناخي 1991–2020.",
        "unit": u"°C",
        "map_title": u"خريطة الشذوذ الحراري الشهري العام مقارنة بخط أساس 1991–2020 (°C)"
    },
    {
        "short_name": "R_MonTrDec",
        "full_name": "R_Month_Trend_Decade",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"معدل تغير واتجاه تساقط الأمطار الشهرية العامة لكل عقد زمني (10 سنوات).",
        "unit": u"mm/decade",
        "map_title": u"خريطة اتجاه تغير تساقط الأمطار الشهرية في العقد الزمني (mm/decade)"
    },
    {
        "short_name": "R_AnomMon",
        "full_name": "R_Anom_Month",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ الأمطار الشهري العام المطلق مقارنة بمتوسط الشهور لخط الأساس المناخي 1991–2020.",
        "unit": u"ملم (mm)",
        "map_title": u"خريطة شذوذ الأمطار الشهري العام مقارنة بخط أساس 1991–2020 (ملم)"
    },
    {
        "short_name": "R_AnMonPct",
        "full_name": "R_Anom_Month_Pct",
        "module_code": "18_Trends_And_Anomalies",
        "module_name": "18_Trends_And_Anomalies (الاتجاهات والشذوذ)",
        "desc_ar": u"شذوذ الأمطار الشهري العام كنسبة مئوية من متوسط الشهور لخط الأساس المناخي 1991–2020.",
        "unit": u"%",
        "map_title": u"خريطة الشذوذ النسبي المئوي للأمطار الشهرية العامة مقارنة بخط أساس 1991–2020 (%)"
    },
    {
        "short_name": "LST_AnMean",
        "full_name": "LST_Annual_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"المتوسط السنوي لدرجة حرارة سطح الأرض (LST) عبر سنوات السلسلة المناخية (1996–2025).",
        "unit": u"°C",
        "map_title": u"خريطة المتوسط السنوي لدرجة حرارة سطح الأرض (°C)"
    },
    {
        "short_name": "LST_MonMn",
        "full_name": "LST_Month_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط الشهور السنوي لدرجة حرارة سطح الأرض (عمود جدول إحصائي فقط مطابق للسنوي).",
        "unit": u"°C",
        "map_title": u"متوسط الشهور لدرجة حرارة سطح الأرض (°C)"
    },
    {
        "short_name": "LST_WinMn",
        "full_name": "LST_Winter_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لفصل الشتاء (ديسمبر، يناير، فبراير).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة سطح الأرض شتاءً (°C)"
    },
    {
        "short_name": "LST_SprMn",
        "full_name": "LST_Spring_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لفصل الربيع (مارس، أبريل، مايو).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة سطح الأرض ربيعاً (°C)"
    },
    {
        "short_name": "LST_SumMn",
        "full_name": "LST_Summer_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لفصل الصيف (يونيو، يوليو، أغسطس).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة سطح الأرض صيفاً (°C)"
    },
    {
        "short_name": "LST_AutMn",
        "full_name": "LST_Autumn_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لفصل الخريف (سبتمبر، أكتوبر، نوفمبر).",
        "unit": u"°C",
        "map_title": u"خريطة متوسط درجة حرارة سطح الأرض خريفاً (°C)"
    },
    {
        "short_name": "LST_AnRng",
        "full_name": "LST_Annual_Range",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"المدى السنوي لدرجة حرارة سطح الأرض (الفرق بين أعلى وأدنى متوسط شهري).",
        "unit": u"°C",
        "map_title": u"خريطة المدى السنوي لدرجة حرارة سطح الأرض (°C)"
    },
    {
        "short_name": "LST_SeaRng",
        "full_name": "LST_Seasonal_Range",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"المدى الفصلي لدرجة حرارة سطح الأرض (الفرق بين أدفأ فصل وأبرد فصل).",
        "unit": u"°C",
        "map_title": u"خريطة المدى الفصلي لدرجة حرارة سطح الأرض (°C)"
    },
    {
        "short_name": "LST_mT_Ann",
        "full_name": "LST_minus_T_Annual",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"الفارق السنوي بين حرارة السطح وحرارة الهواء عند 2 م (LST_Annual_Mean - T_Annual_Mean).",
        "unit": u"°C",
        "map_title": u"خريطة الفارق السنوي بين حرارة السطح وحرارة الهواء (°C)"
    },
    {
        "short_name": "LST_mT_Wi",
        "full_name": "LST_minus_T_Winter",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق الشتاء بين حرارة السطح وحرارة الهواء عند 2 م (LST_Winter_Mean - T_Winter_Mean).",
        "unit": u"°C",
        "map_title": u"خريطة فارق الشتاء بين حرارة السطح وحرارة الهواء (°C)"
    },
    {
        "short_name": "LST_mT_Sp",
        "full_name": "LST_minus_T_Spring",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق الربيع بين حرارة السطح وحرارة الهواء عند 2 م (LST_Spring_Mean - T_Spring_Mean).",
        "unit": u"°C",
        "map_title": u"خريطة فارق الربيع بين حرارة السطح وحرارة الهواء (°C)"
    },
    {
        "short_name": "LST_mT_Sum",
        "full_name": "LST_minus_T_Summer",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق الصيف بين حرارة السطح وحرارة الهواء عند 2 م (LST_Summer_Mean - T_Summer_Mean).",
        "unit": u"°C",
        "map_title": u"خريطة فارق الصيف بين حرارة السطح وحرارة الهواء (°C)"
    },
    {
        "short_name": "LST_mT_Au",
        "full_name": "LST_minus_T_Autumn",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق الخريف بين حرارة السطح وحرارة الهواء عند 2 م (LST_Autumn_Mean - T_Autumn_Mean).",
        "unit": u"°C",
        "map_title": u"خريطة فارق الخريف بين حرارة السطح وحرارة الهواء (°C)"
    },
    {
        "short_name": "LST_JanMn",
        "full_name": "LST_January_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر يناير.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر يناير (°C)"
    },
    {
        "short_name": "LST_FebMn",
        "full_name": "LST_February_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر فبراير.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر فبراير (°C)"
    },
    {
        "short_name": "LST_MarMn",
        "full_name": "LST_March_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر مارس.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر مارس (°C)"
    },
    {
        "short_name": "LST_AprMn",
        "full_name": "LST_April_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر أبريل.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر أبريل (°C)"
    },
    {
        "short_name": "LST_MayMn",
        "full_name": "LST_May_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر مايو.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر مايو (°C)"
    },
    {
        "short_name": "LST_JunMn",
        "full_name": "LST_June_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر يونيو.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر يونيو (°C)"
    },
    {
        "short_name": "LST_JulMn",
        "full_name": "LST_July_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر يوليو.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر يوليو (°C)"
    },
    {
        "short_name": "LST_AugMn",
        "full_name": "LST_August_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر أغسطس.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر أغسطس (°C)"
    },
    {
        "short_name": "LST_SepMn",
        "full_name": "LST_September_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر سبتمبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر سبتمبر (°C)"
    },
    {
        "short_name": "LST_OctMn",
        "full_name": "LST_October_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر أكتوبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر أكتوبر (°C)"
    },
    {
        "short_name": "LST_NovMn",
        "full_name": "LST_November_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر نوفمبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر نوفمبر (°C)"
    },
    {
        "short_name": "LST_DecMn",
        "full_name": "LST_December_Mean",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"متوسط درجة حرارة سطح الأرض لشهر ديسمبر.",
        "unit": u"°C",
        "map_title": u"خريطة متوسط حرارة سطح الأرض لشهر ديسمبر (°C)"
    },
    {
        "short_name": "LST_mT_Jan",
        "full_name": "LST_minus_T_January",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر يناير بين حرارة السطح وحرارة الهواء عند 2 م (LST_January_Mean - T_January_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Feb",
        "full_name": "LST_minus_T_February",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر فبراير بين حرارة السطح وحرارة الهواء عند 2 م (LST_February_Mean - T_February_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Mar",
        "full_name": "LST_minus_T_March",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر مارس بين حرارة السطح وحرارة الهواء عند 2 م (LST_March_Mean - T_March_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Apr",
        "full_name": "LST_minus_T_April",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر أبريل بين حرارة السطح وحرارة الهواء عند 2 م (LST_April_Mean - T_April_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_May",
        "full_name": "LST_minus_T_May",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر مايو بين حرارة السطح وحرارة الهواء عند 2 م (LST_May_Mean - T_May_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Jun",
        "full_name": "LST_minus_T_June",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر يونيو بين حرارة السطح وحرارة الهواء عند 2 م (LST_June_Mean - T_June_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Jul",
        "full_name": "LST_minus_T_July",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر يوليو بين حرارة السطح وحرارة الهواء عند 2 م (LST_July_Mean - T_July_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Aug",
        "full_name": "LST_minus_T_August",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر أغسطس بين حرارة السطح وحرارة الهواء عند 2 م (LST_August_Mean - T_August_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Sep",
        "full_name": "LST_minus_T_September",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر سبتمبر بين حرارة السطح وحرارة الهواء عند 2 م (LST_September_Mean - T_September_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Oct",
        "full_name": "LST_minus_T_October",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر أكتوبر بين حرارة السطح وحرارة الهواء عند 2 م (LST_October_Mean - T_October_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Nov",
        "full_name": "LST_minus_T_November",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر نوفمبر بين حرارة السطح وحرارة الهواء عند 2 م (LST_November_Mean - T_November_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    },
    {
        "short_name": "LST_mT_Dec",
        "full_name": "LST_minus_T_December",
        "module_code": "19_Land_Surface_Temperature",
        "module_name": "19_Land_Surface_Temperature (حرارة سطح الأرض)",
        "desc_ar": u"فارق شهر ديسمبر بين حرارة السطح وحرارة الهواء عند 2 م (LST_December_Mean - T_December_Mean).",
        "unit": u"°C",
        "map_title": u"-"
    }
]

REMOVED_REDUNDANT_FIELDS = {
    "T_Month_Mean", "T_Seasonal_Range",
    "HI_Seasonal_Range",
    "Td_Month_Mean", "Td_Seasonal_Range",
    "R_Month_Mean", "R_Seasonal_Range",
    "PSL_Month_Mean", "PSL_Seasonal_Range",
    "PS_Month_Mean", "PS_Seasonal_Range",
    "W_Spd_Month_Mean", "W_Spd_Seasonal_Range", "W_Dir_Month_Mean",
    "RH_Month_Mean", "RH_Seasonal_Range",
    "Sol_Month_Mean", "Sol_Seasonal_Range",
    "UV_Month_Mean", "UV_Seasonal_Range",
    "Cld_Month_Mean", "Cld_Seasonal_Range",
    "WC_Seasonal_Range",
    "ET_Month_Mean", "ET_Seasonal_Range",
    "LST_Month_Mean", "LST_Seasonal_Range",
}
FIELDS_DATA = [f for f in FIELDS_DATA if f["full_name"] not in REMOVED_REDUNDANT_FIELDS]

MODULES_SUMMARY = [
    {
        "num": "01",
        "name_en": "01_Temperature",
        "name_ar": u"درجة الحرارة",
        "folder": "01_Temperature",
        "fc": "01_Temperature",
        "count": 22,
        "unit": u"°C",
        "method": u"NASA POWER T2M, T2M_MAX, T2M_MIN / WMO Climatological Normals"
    },
    {
        "num": "02",
        "name_en": "02_Land_Surface_Temperature",
        "name_ar": u"درجة حرارة سطح الأرض",
        "folder": "02_Land_Surface_Temperature",
        "fc": "02_Land_Surface_Temperature",
        "count": 35,
        "unit": u"°C",
        "method": u"NASA POWER TS (MERRA-2) / Climatological Skin Temperature & Differences"
    },
    {
        "num": "03",
        "name_en": "03_Precipitation",
        "name_ar": u"الأمطار والتساقط",
        "folder": "03_Precipitation",
        "fc": "03_Precipitation",
        "count": 19,
        "unit": u"mm",
        "method": u"NASA POWER PRECTOTCORR / Annual, Seasonal Totals & Ranges"
    },
    {
        "num": "04",
        "name_en": "04_Sea_Level_Pressure",
        "name_ar": u"ضغط مستوى سطح البحر",
        "folder": "04_Sea_Level_Pressure",
        "fc": "04_Sea_Level_Pressure",
        "count": 18,
        "unit": u"hPa / mbar",
        "method": u"NASA POWER SLP / Reduced to Standard Mean Sea Level"
    },
    {
        "num": "05",
        "name_en": "05_Surface_Pressure",
        "name_ar": u"الضغط السطحي الفعلي",
        "folder": "05_Surface_Pressure",
        "fc": "05_Surface_Pressure",
        "count": 18,
        "unit": u"hPa / mbar",
        "method": u"NASA POWER PS / Actual Local Topographic Station Pressure"
    },
    {
        "num": "06",
        "name_en": "06_Wind",
        "name_ar": u"الرياح السطحية (سرعة واتجاه)",
        "folder": "06_Wind",
        "fc": "06_Wind",
        "count": 37,
        "unit": u"m/s, °",
        "method": u"NASA POWER WS10M, WD10M / Circular Mean Vector atan2"
    },
    {
        "num": "07",
        "name_en": "07_Relative_Humidity",
        "name_ar": u"الرطوبة النسبية",
        "folder": "07_Relative_Humidity",
        "fc": "07_Relative_Humidity",
        "count": 18,
        "unit": u"%",
        "method": u"NASA POWER RH2M / Climatological Relative Humidity at 2m"
    },
    {
        "num": "08",
        "name_en": "08_Dew_Point",
        "name_ar": u"نقطة الندى",
        "folder": "08_Dew_Point",
        "fc": "08_Dew_Point",
        "count": 18,
        "unit": u"°C",
        "method": u"NASA POWER T2MDEW / Dew Point Temperature at 2m"
    },
    {
        "num": "09",
        "name_en": "09_Solar_Radiation",
        "name_ar": u"الإشعاع الشمسي والطاقة",
        "folder": "09_Solar_Radiation",
        "fc": "09_Solar_Radiation",
        "count": 19,
        "unit": u"kWh/m²/day",
        "method": u"NASA POWER ALLSKY_SFC_SW_DWN / Daily Mean & Cumulative Annual"
    },
    {
        "num": "10",
        "name_en": "10_UV_Index",
        "name_ar": u"مؤشر الأشعة فوق البنفسجية",
        "folder": "10_UV_Index",
        "fc": "10_UV_Index",
        "count": 18,
        "unit": u"Index (0–16+)",
        "method": u"WHO / WMO Global Solar UV Index Standard"
    },
    {
        "num": "11",
        "name_en": "11_Cloud_Cover",
        "name_ar": u"الغطاء السحابي",
        "folder": "11_Cloud_Cover",
        "fc": "11_Cloud_Cover",
        "count": 18,
        "unit": u"%",
        "method": u"NASA POWER CLOUD_AMT / Total Sky Cloud Fraction"
    },
    {
        "num": "12",
        "name_en": "12_Heat_Index",
        "name_ar": u"مؤشر الحرارة والإجهاد الحراري",
        "folder": "12_Heat_Index",
        "fc": "12_Heat_Index",
        "count": 19,
        "unit": u"°C",
        "method": u"Steadman-Rothfusz NWS Formula + Humidex + ISO 7243 WBGT"
    },
    {
        "num": "13",
        "name_en": "13_Wind_Chill",
        "name_ar": u"مبرد الرياح",
        "folder": "13_Wind_Chill",
        "fc": "13_Wind_Chill",
        "count": 18,
        "unit": u"°C",
        "method": u"US National Weather Service (NWS) Wind Chill Equivalent"
    },
    {
        "num": "14",
        "name_en": "14_De_Martonne_Aridity",
        "name_ar": u"دليل الجفاف لدي مارتون",
        "folder": "14_De_Martonne_Aridity",
        "fc": "14_De_Martonne_Aridity",
        "count": 1,
        "unit": u"Index",
        "method": u"De Martonne (1926) Aridity Index: I = P / (T + 10)"
    },
    {
        "num": "15",
        "name_en": "15_Evapotranspiration",
        "name_ar": u"البخر والنتح المرجعي (ET)",
        "folder": "15_Evapotranspiration",
        "fc": "15_Evapotranspiration",
        "count": 19,
        "unit": u"mm",
        "method": u"FAO-56 Hargreaves-Samani (1985) Extraterrestrial Radiation Ra"
    },
    {
        "num": "16",
        "name_en": "16_UNEP_Aridity",
        "name_ar": u"مؤشر القحولة UNEP",
        "folder": "16_UNEP_Aridity",
        "fc": "16_UNEP_Aridity",
        "count": 1,
        "unit": u"Ratio",
        "method": u"UNEP Global Aridity Index: AI = P / ETo"
    },
    {
        "num": "17",
        "name_en": "17_Water_Deficit",
        "name_ar": u"الموازنة والعجز المائي",
        "folder": "17_Water_Deficit",
        "fc": "17_Water_Deficit",
        "count": 1,
        "unit": u"mm",
        "method": u"Climatic Water Balance: WD = P - ETo (Negative = Deficit)"
    },
    {
        "num": "18",
        "name_en": "18_Dry_Months",
        "name_ar": u"عدد الأشهر الجافة بيولوجياً",
        "folder": "18_Dry_Months",
        "fc": "18_Dry_Months",
        "count": 1,
        "unit": u"Months (0–12)",
        "method": u"Walter-Lieth Bioclimatic Standard: P < 2 * T"
    },
    {
        "num": "19",
        "name_en": "19_Trends_And_Anomalies",
        "name_ar": u"الاتجاهات والشذوذ المناخي",
        "folder": "19_Trends_And_Anomalies",
        "fc": "19_Trends_And_Anomalies",
        "count": 30,
        "unit": u"°C, mm, %",
        "method": u"OLS Linear Regression Trends & WMO 1991–2020 Baseline Anomalies"
    }
]


def build_excel(output_path):
    wb = openpyxl.Workbook()
    
    # ----------------------------------------------------
    # Styles
    # ----------------------------------------------------
    navy_dark = "1F4E79"
    navy_med = "2F5597"
    header_fill = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
    summary_fill = PatternFill(start_color=navy_med, end_color=navy_med, fill_type="solid")
    zebra_even = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    zebra_odd = PatternFill(start_color="F2F6FA", end_color="F2F6FA", fill_type="solid")
    admin_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    
    font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_title = Font(name="Segoe UI", size=14, bold=True, color="1F4E79")
    font_bold = Font(name="Segoe UI", size=10, bold=True, color="000000")
    font_regular = Font(name="Segoe UI", size=10, color="000000")
    font_code = Font(name="Consolas", size=10, bold=True, color="1F4E79")
    font_map_title = Font(name="Segoe UI", size=10, bold=True, color="165B33")
    font_unit = Font(name="Segoe UI", size=10, bold=True, color="7F3F98")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    
    section_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    font_section = Font(name="Segoe UI", size=11, bold=True, color="1F4E79")
    font_banner = Font(name="Segoe UI", size=14, bold=True, color="FFFFFF")

    # ----------------------------------------------------
    # Sheet 1: 01_عن_القاموس_About_Dictionary
    # ----------------------------------------------------
    ws0 = wb.active
    ws0.title = "01_عن_القاموس_About_Dictionary"
    ws0.views.sheetView[0].showGridLines = True

    # Title Banner (Row 1)
    ws0.merge_cells("A1:G1")
    tcell = ws0.cell(1, 1, u"القاموس المرجعي الشامل لحقول ومؤشرات أطلس المناخ الرقمي\nComprehensive Data Dictionary — NASA POWER Climate Atlas Engine")
    tcell.font = font_banner
    tcell.fill = header_fill
    tcell.alignment = align_center
    ws0.row_dimensions[1].height = 45

    # Section 1: Engine Profile (Row 3)
    ws0.merge_cells("A3:G3")
    s1 = ws0.cell(3, 1, u"1. بطاقة الهوية الفنية ومصدر البيانات المناخية (Technical Engine & Data Source Profile)")
    s1.font = font_section
    s1.fill = section_fill
    s1.alignment = align_right
    ws0.row_dimensions[3].height = 24

    engine_meta = [
        (u"اسم الأداة والمنصة البرمجية (Software Platform)", u"NASA POWER Climate Atlas Generator (ArcGIS 10.8 & Pro)", u"أداة المعالجة الكارتوجرافية والتحليل المناخي الآلي لمنظومة ArcGIS"),
        (u"مزود ونماذج البيانات المناخية (Data Source & Models)", u"NASA POWER API (CERES & MERRA-2 Gridded Reanalysis)", u"نماذج الاستشعار الفضائي وإعادة التحليل المناخي المعتمدة لوكالة ناسا"),
        (u"الفترة الزمنية المناخية القياسية (Climate Normal Period)", u"1996 – 2025 (سلسلة 30 عاماً تشمل المتوسطات الشهرية والفصلية والسنوية)", u"تطابق المعيار الدولي للمعدلات المناخية القياسية (WMO 30-Year Normal)"),
        (u"المعايير العلمية والمرجعيات الدولية (Scientific Standards)", u"WMO-No. 1203 / FAO-56 Irrigation / Steadman & ISO 7243", u"المنهجيات المعتمدة عالمياً لحساب الراحة الحرارية والقحولة والتبخر"),
        (u"التغطية الجغرافية ونظام الإحداثيات (Spatial Scope & Coordinate System)", u"Global Coverage (WGS 1984 / EPSG:4326)", u"تغطية عالمية شاملة بدقة شبكية منتظمة وقابلة للقص على أي دولة أو إقليم"),
        (u"إجمالي الحقول الموصوفة في القاموس (Total Defined Fields)", u"%d حقلاً معيارياً (%d مؤشراً مناخياً + 12 حقلاً إدارياً)" % (len(FIELDS_DATA), len(FIELDS_DATA) - 12), u"تشمل الحقول الإدارية والفيزيائية والفصلية ومتجهات الرياح والموديلات"),
        (u"عدد الحزم والعناصر المناخية (Climate Modules)", u"19 حزمة موديولية متكاملة (19 Complete Modules)", u"مجلدات راسترات وطبقات معالم بقاعدة البيانات الجغرافية متطابقة 1:1"),
    ]

    for idx, (prop, val, note) in enumerate(engine_meta, 4):
        ws0.row_dimensions[idx].height = 22
        r_fill = zebra_odd if idx % 2 == 0 else zebra_even
        c1 = ws0.cell(idx, 1, idx - 3)
        c1.alignment = align_center
        c1.font = font_bold
        c1.fill = r_fill
        c1.border = thin_border
        
        c2 = ws0.cell(idx, 2, prop)
        c2.alignment = align_right
        c2.font = font_bold
        c2.fill = r_fill
        c2.border = thin_border
        
        ws0.merge_cells(start_row=idx, start_column=3, end_row=idx, end_column=4)
        c3 = ws0.cell(idx, 3, val)
        c3.alignment = align_center
        c3.font = font_code
        c3.fill = r_fill
        c3.border = thin_border
        ws0.cell(idx, 4).border = thin_border
        ws0.cell(idx, 4).fill = r_fill
        
        ws0.merge_cells(start_row=idx, start_column=5, end_row=idx, end_column=7)
        c5 = ws0.cell(idx, 5, note)
        c5.alignment = align_right
        c5.font = font_regular
        c5.fill = r_fill
        c5.border = thin_border
        for c_i in (6, 7):
            ws0.cell(idx, c_i).border = thin_border
            ws0.cell(idx, c_i).fill = r_fill

    # Section 2: 19 Modules Summary Table (Row 12)
    ws0.merge_cells("A12:G12")
    s2 = ws0.cell(12, 1, u"2. هيكل حزم البيانات والموديلات الـ 19 المتطابقة 1:1 (The 19 Climate Modules Architecture)")
    s2.font = font_section
    s2.fill = section_fill
    s2.alignment = align_right
    ws0.row_dimensions[12].height = 24

    headers_sec2 = [
        u"م",
        u"كود الموديول في الأداة\nModule Code",
        u"الاسم باللغة العربية\nArabic Module Name",
        u"الاسم بالإنجليزية\nEnglish Module Name",
        u"المؤشرات\nIndicators",
        u"الوحدة الرئيسية\nMain Unit",
        u"المنهجية والمعيار العلمي المعتمد\nScientific Methodology & Standards"
    ]
    ws0.row_dimensions[13].height = 28
    for col_idx, h_text in enumerate(headers_sec2, 1):
        c = ws0.cell(row=13, column=col_idx, value=h_text)
        c.font = font_header
        c.fill = summary_fill
        c.alignment = align_center
        c.border = thin_border

    for idx, mod in enumerate(MODULES_SUMMARY, 14):
        ws0.row_dimensions[idx].height = 22
        r_fill = zebra_odd if idx % 2 == 0 else zebra_even
        
        c1 = ws0.cell(idx, 1, mod["num"])
        c1.alignment = align_center
        c1.font = font_bold
        c1.fill = r_fill
        c1.border = thin_border
        
        c2 = ws0.cell(idx, 2, mod["folder"])
        c2.alignment = align_left
        c2.font = font_code
        c2.fill = r_fill
        c2.border = thin_border
        
        c3 = ws0.cell(idx, 3, mod["name_ar"])
        c3.alignment = align_right
        c3.font = font_bold
        c3.fill = r_fill
        c3.border = thin_border
        
        c4 = ws0.cell(idx, 4, mod["name_en"])
        c4.alignment = align_left
        c4.font = font_regular
        c4.fill = r_fill
        c4.border = thin_border
        
        c5 = ws0.cell(idx, 5, mod["count"])
        c5.alignment = align_center
        c5.font = font_bold
        c5.fill = r_fill
        c5.border = thin_border
        
        c6 = ws0.cell(idx, 6, mod["unit"])
        c6.alignment = align_center
        c6.font = font_unit
        c6.fill = r_fill
        c6.border = thin_border
        
        c7 = ws0.cell(idx, 7, mod["method"])
        c7.alignment = align_left
        c7.font = font_regular
        c7.fill = r_fill
        c7.border = thin_border

    # Section 3: Columns Guide (Row 33)
    ws0.merge_cells("A33:G33")
    s3 = ws0.cell(33, 1, u"3. دليل قراءة أعمدة القاموس المرجعي واستخدامها في نظم المعلومات الجغرافية (Field Dictionary Columns Guide)")
    s3.font = font_section
    s3.fill = section_fill
    s3.alignment = align_right
    ws0.row_dimensions[33].height = 24

    cols_meta = [
        (u"اسم الحقل المختصر (Short Field Name)", u"صيغة Shapefile / DBF (حتى 10 أحرف)", u"متوافق 100% مع طبقات الشيب فايل لمنع اقتطاع الأسماء وتشوهها عند التصدير."),
        (u"اسم الحقل الكامل (Full Field Name)", u"صيغة Geodatabase و NASA POWER API", u"الاسم المعياري الشامل المعتمد في قواعد البيانات الجغرافية (GDB) وبرمجية الأداة."),
        (u"الموديول / العنصر المناخي (Climate Module)", u"الحزمة المناخية (1 من 18 موديول)", u"يتطابق بنسبة 1:1 مع اسم مجلد الراستر واسم طبقة المعالم في قاعدة البيانات."),
        (u"الشرح والتوصيف العلمي (Scientific Description)", u"البيان الفيزيائي والمعادلة الرياضية", u"التوصيف الرياضي والفيزيائي الدقيق لكيفية حساب المؤشر وفترته الزمنية المعتمدة."),
        (u"وحدة القياس القياسية (Measurement Unit)", u"الوحدات الدولية المعتمدة (SI Units)", u"درجات مئوية (°C)، ملم، هيكتوباسكال (hPa)، م/ث، ميجاجول/م²، نسب مئوية (%)."),
        (u"اسم الخريطة المقترح (Suggested Map Title)", u"الصياغة الكارتوجرافية الاحترافية", u"العنوان الكارتوجرافي الرسمي المعتمد لوضعه في عنوان الخريطة ومفتاح المصطلحات (Legend)."),
    ]

    for idx, (prop, val, note) in enumerate(cols_meta, 34):
        ws0.row_dimensions[idx].height = 22
        r_fill = zebra_odd if idx % 2 == 0 else zebra_even
        c1 = ws0.cell(idx, 1, idx - 33)
        c1.alignment = align_center
        c1.font = font_bold
        c1.fill = r_fill
        c1.border = thin_border
        
        c2 = ws0.cell(idx, 2, prop)
        c2.alignment = align_right
        c2.font = font_bold
        c2.fill = r_fill
        c2.border = thin_border
        
        ws0.merge_cells(start_row=idx, start_column=3, end_row=idx, end_column=4)
        c3 = ws0.cell(idx, 3, val)
        c3.alignment = align_center
        c3.font = font_code
        c3.fill = r_fill
        c3.border = thin_border
        ws0.cell(idx, 4).border = thin_border
        ws0.cell(idx, 4).fill = r_fill
        
        ws0.merge_cells(start_row=idx, start_column=5, end_row=idx, end_column=7)
        c5 = ws0.cell(idx, 5, note)
        c5.alignment = align_right
        c5.font = font_regular
        c5.fill = r_fill
        c5.border = thin_border
        for c_i in (6, 7):
            ws0.cell(idx, c_i).border = thin_border
            ws0.cell(idx, c_i).fill = r_fill

    # Set column widths for Sheet 1
    col_widths_0 = {
        1: 6,   # م
        2: 32,  # Module / Property
        3: 28,  # Value / Code
        4: 28,  # Sub-value / English
        5: 14,  # Count
        6: 18,  # Unit
        7: 48   # Note / Method
    }
    for col_idx, width in col_widths_0.items():
        ws0.column_dimensions[get_column_letter(col_idx)].width = width

    # ----------------------------------------------------
    # Sheet 2: Climate Fields
    # ----------------------------------------------------
    ws1 = wb.create_sheet(title="Climate_Fields")
    
    headers_ws1 = [
        u"م",
        u"اسم الحقل المختصر (Shapefile)\nShort Field Name",
        u"اسم الحقل الكامل (Geodatabase / API)\nFull Field Name (EN)",
        u"الموديول / العنصر المناخي\nClimate Module",
        u"الشرح والتوصيف العلمي باللغة العربية\nScientific Description (AR)",
        u"وحدة القياس\nUnit",
        u"اسم الخريطة المقترح\nSuggested Map Title (AR)"
    ]
    
    ws1.row_dimensions[1].height = 36
    for col_idx, h_text in enumerate(headers_ws1, 1):
        cell = ws1.cell(row=1, column=col_idx, value=h_text)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
    
    for row_idx, item in enumerate(FIELDS_DATA, 2):
        ws1.row_dimensions[row_idx].height = 24
        is_admin = item["module_code"].startswith("00")
        row_fill = admin_fill if is_admin else (zebra_even if row_idx % 2 == 0 else zebra_odd)
        
        # Col 1: Serial
        c1 = ws1.cell(row=row_idx, column=1, value=row_idx - 1)
        c1.font = font_bold
        c1.alignment = align_center
        c1.fill = row_fill
        c1.border = thin_border
        
        # Col 2: Short Name
        c2 = ws1.cell(row=row_idx, column=2, value=item["short_name"])
        c2.font = font_code
        c2.alignment = align_center
        c2.fill = row_fill
        c2.border = thin_border
        
        # Col 3: Full Name
        c3 = ws1.cell(row=row_idx, column=3, value=item["full_name"])
        c3.font = font_bold
        c3.alignment = align_left
        c3.fill = row_fill
        c3.border = thin_border
        
        # Col 4: Module Name
        c4 = ws1.cell(row=row_idx, column=4, value=item["module_name"])
        c4.font = font_regular
        c4.alignment = align_left
        c4.fill = row_fill
        c4.border = thin_border
        
        # Col 5: Description AR
        c5 = ws1.cell(row=row_idx, column=5, value=item["desc_ar"])
        c5.font = font_regular
        c5.alignment = align_right
        c5.fill = row_fill
        c5.border = thin_border
        
        # Col 6: Unit
        c6 = ws1.cell(row=row_idx, column=6, value=item["unit"])
        c6.font = font_unit
        c6.alignment = align_center
        c6.fill = row_fill
        c6.border = thin_border
        
        # Col 7: Suggested Map Title AR
        c7 = ws1.cell(row=row_idx, column=7, value=item["map_title"])
        c7.font = font_map_title if item["map_title"] != "-" else font_regular
        c7.alignment = align_right if item["map_title"] != "-" else align_center
        c7.fill = row_fill
        c7.border = thin_border

    # Freeze panes on Header
    ws1.freeze_panes = "A2"
    
    # Auto-filter
    ws1.auto_filter.ref = "A1:G{}".format(len(FIELDS_DATA) + 1)
    
    # Column widths for Sheet 1
    col_widths_1 = {
        1: 6,   # م
        2: 24,  # Short Name
        3: 28,  # Full Name
        4: 30,  # Module Name
        5: 65,  # Description AR
        6: 18,  # Unit
        7: 48   # Map Title AR
    }
    for col_idx, width in col_widths_1.items():
        ws1.column_dimensions[get_column_letter(col_idx)].width = width

    # ----------------------------------------------------
    # Sheet 2: Modules Summary
    # ----------------------------------------------------
    ws2 = wb.create_sheet(title="Modules_19_Summary")
    
    headers_ws2 = [
        u"الرقم\nNo.",
        u"اسم العنصر في الأداة\nTool Parameter & Layer",
        u"الاسم باللغة العربية\nModule Arabic Name",
        u"مجلد الراستر (1:1)\nOutput Raster Folder",
        u"طبقة المعالم (1:1)\nFeature Class Name",
        u"عدد المؤشرات\nIndicators",
        u"الوحدة الرئيسية\nMain Unit",
        u"المنهجية والمعادلة العلمية\nScientific Method & Standards"
    ]
    
    ws2.row_dimensions[1].height = 36
    for col_idx, h_text in enumerate(headers_ws2, 1):
        cell = ws2.cell(row=1, column=col_idx, value=h_text)
        cell.font = font_header
        cell.fill = summary_fill
        cell.alignment = align_center
        cell.border = thin_border
        
    for row_idx, item in enumerate(MODULES_SUMMARY, 2):
        ws2.row_dimensions[row_idx].height = 24
        row_fill = zebra_even if row_idx % 2 == 0 else zebra_odd
        
        c1 = ws2.cell(row=row_idx, column=1, value=item["num"])
        c1.font = font_bold
        c1.alignment = align_center
        c1.fill = row_fill
        c1.border = thin_border
        
        c2 = ws2.cell(row=row_idx, column=2, value=item["name_en"])
        c2.font = font_code
        c2.alignment = align_left
        c2.fill = row_fill
        c2.border = thin_border
        
        c3 = ws2.cell(row=row_idx, column=3, value=item["name_ar"])
        c3.font = font_bold
        c3.alignment = align_right
        c3.fill = row_fill
        c3.border = thin_border
        
        c4 = ws2.cell(row=row_idx, column=4, value=item["folder"])
        c4.font = font_code
        c4.alignment = align_left
        c4.fill = row_fill
        c4.border = thin_border
        
        c5 = ws2.cell(row=row_idx, column=5, value=item["fc"])
        c5.font = font_code
        c5.alignment = align_left
        c5.fill = row_fill
        c5.border = thin_border
        
        c6 = ws2.cell(row=row_idx, column=6, value=item["count"])
        c6.font = font_bold
        c6.alignment = align_center
        c6.fill = row_fill
        c6.border = thin_border
        
        c7 = ws2.cell(row=row_idx, column=7, value=item["unit"])
        c7.font = font_unit
        c7.alignment = align_center
        c7.fill = row_fill
        c7.border = thin_border
        
        c8 = ws2.cell(row=row_idx, column=8, value=item["method"])
        c8.font = font_regular
        c8.alignment = align_left
        c8.fill = row_fill
        c8.border = thin_border

    # Row 20: Total Summary
    total_row = len(MODULES_SUMMARY) + 2
    ws2.row_dimensions[total_row].height = 26
    c_tot_label = ws2.cell(row=total_row, column=3, value=u"الإجمالي العام للمؤشرات المناخية:")
    c_tot_label.font = Font(name="Segoe UI", size=11, bold=True, color="1F4E79")
    c_tot_label.alignment = align_right
    
    total_indicators = sum(m["count"] for m in MODULES_SUMMARY)
    c_tot_val = ws2.cell(row=total_row, column=6, value=total_indicators)
    c_tot_val.font = Font(name="Segoe UI", size=11, bold=True, color="1F4E79")
    c_tot_val.alignment = align_center
    
    ws2.freeze_panes = "A2"
    ws2.auto_filter.ref = "A1:H{}".format(len(MODULES_SUMMARY) + 1)
    
    col_widths_2 = {
        1: 8,   # No.
        2: 26,  # Name EN
        3: 26,  # Name AR
        4: 26,  # Folder
        5: 26,  # FC
        6: 15,  # Count
        7: 16,  # Unit
        8: 55   # Method
    }
    for col_idx, width in col_widths_2.items():
        ws2.column_dimensions[get_column_letter(col_idx)].width = width

    # Save
    wb.save(output_path)
    print("Successfully built Excel dictionary at:", output_path)
    print("Sheet 1 'Climate_Fields' total rows:", len(FIELDS_DATA) + 1)
    print("Sheet 2 'Modules_19_Summary' total rows:", len(MODULES_SUMMARY) + 1)


if __name__ == "__main__":
    import os
    cur_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(cur_dir, "Documents", "03_Excel_Dictionaries")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    out_file = os.path.join(docs_dir, "Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx")
    build_excel(out_file)
