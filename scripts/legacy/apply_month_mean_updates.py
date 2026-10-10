# -*- coding: utf-8 -*-
"""
Apply Month Mean fields, descriptive Arabic aliases, rasters, and Excel updates
across Desktop and D: drive datasets for NASA POWER Climate Atlas.
"""

import os
import shutil
import arcpy
import pandas as pd

# Target Roots
DESKTOP_DIR = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
D_DRIVE_DIR = r"D:\MY DATA & FILE\Spatial Data\Egypt Climate Data 1996-2025"

# Comprehensive Arabic Aliases Map
ARABIC_ALIASES = {
    # System / Spatial / Admin fields
    "Point_ID": u"معرف النقطة",
    "Source_ID": u"معرف المحطة",
    "Point_Lat": u"دائرة العرض (شمالاً)",
    "Point_Lon": u"خط الطول (شرقاً)",
    "POINT_X": u"الإحداثي السيني X",
    "POINT_Y": u"الإحداثي الصادي Y",
    "Data_Start": u"بداية فترة الرصد",
    "Data_End": u"نهاية فترة الرصد",
    "Temporal": u"النطاق الزمني",
    "Interp_Meth": u"طريقة الاستيفاء المكاني",
    "Cell_Size": u"حجم الخلية (متر)",
    "Wind_Cell": u"حجم خلية الرياح (متر)",
    "Status": u"حالة المعالجة",
    "Error_Msg": u"رسالة الخطأ",
    "Measurement_Unit": u"وحدة القياس",

    # Temperature
    "T_Annual_Mean": u"المتوسط السنوي لدرجة الحرارة",
    "T_Month_Mean": u"المتوسط الشهري لدرجة الحرارة",
    "T_Winter_Mean": u"متوسط درجة الحرارة لفصل الشتاء",
    "T_Spring_Mean": u"متوسط درجة الحرارة لفصل الربيع",
    "T_Summer_Mean": u"متوسط درجة الحرارة لفصل الصيف",
    "T_Autumn_Mean": u"متوسط درجة الحرارة لفصل الخريف",
    "T_Annual_Range": u"المدى الحراري السنوي لدرجات الحرارة",
    "T_Max_Summer_Month_Mean": u"متوسط أدفأ شهور فصل الصيف",
    "T_Min_Winter_Month_Mean": u"متوسط أبرد شهور فصل الشتاء",
    "T_Annual_Max_Mean": u"المتوسط السنوي لدرجة الحرارة العظمى",
    "T_Annual_Min_Mean": u"المتوسط السنوي لدرجة الحرارة الصغرى",
    "T_January_Mean": u"متوسط درجة الحرارة لشهر يناير",
    "T_February_Mean": u"متوسط درجة الحرارة لشهر فبراير",
    "T_March_Mean": u"متوسط درجة الحرارة لشهر مارس",
    "T_April_Mean": u"متوسط درجة الحرارة لشهر أبريل",
    "T_May_Mean": u"متوسط درجة الحرارة لشهر مايو",
    "T_June_Mean": u"متوسط درجة الحرارة لشهر يونيو",
    "T_July_Mean": u"متوسط درجة الحرارة لشهر يوليو",
    "T_August_Mean": u"متوسط درجة الحرارة لشهر أغسطس",
    "T_September_Mean": u"متوسط درجة الحرارة لشهر سبتمبر",
    "T_October_Mean": u"متوسط درجة الحرارة لشهر أكتوبر",
    "T_November_Mean": u"متوسط درجة الحرارة لشهر نوفمبر",
    "T_December_Mean": u"متوسط درجة الحرارة لشهر ديسمبر",

    # Precipitation
    "R_Annual_Mean": u"المجموع السنوي لتساقط الأمطار",
    "R_Month_Mean": u"المتوسط الشهري لتساقط الأمطار",
    "R_Annual_Range": u"المدى السنوي لتساقط الأمطار",
    "R_Seasonal_Range": u"المدى الفصلي لتساقط الأمطار",
    "R_Winter_Mean": u"متوسط هطول الأمطار لفصل الشتاء",
    "R_Spring_Mean": u"متوسط هطول الأمطار لفصل الربيع",
    "R_Summer_Mean": u"متوسط هطول الأمطار لفصل الصيف",
    "R_Autumn_Mean": u"متوسط هطول الأمطار لفصل الخريف",
    "R_Winter_Total": u"المجموع التراكمي لهطول الأمطار شتاءً",
    "R_Spring_Total": u"المجموع التراكمي لهطول الأمطار ربيعاً",
    "R_Summer_Total": u"المجموع التراكمي لهطول الأمطار صيفاً",
    "R_Autumn_Total": u"المجموع التراكمي لهطول الأمطار خريفاً",
    "R_January_Mean": u"متوسط هطول الأمطار لشهر يناير",
    "R_February_Mean": u"متوسط هطول الأمطار لشهر فبراير",
    "R_March_Mean": u"متوسط هطول الأمطار لشهر مارس",
    "R_April_Mean": u"متوسط هطول الأمطار لشهر أبريل",
    "R_May_Mean": u"متوسط هطول الأمطار لشهر مايو",
    "R_June_Mean": u"متوسط هطول الأمطار لشهر يونيو",
    "R_July_Mean": u"متوسط هطول الأمطار لشهر يوليو",
    "R_August_Mean": u"متوسط هطول الأمطار لشهر أغسطس",
    "R_September_Mean": u"متوسط هطول الأمطار لشهر سبتمبر",
    "R_October_Mean": u"متوسط هطول الأمطار لشهر أكتوبر",
    "R_November_Mean": u"متوسط هطول الأمطار لشهر نوفمبر",
    "R_December_Mean": u"متوسط هطول الأمطار لشهر ديسمبر",

    # Sea Level Pressure
    "PSL_Annual_Mean": u"المتوسط السنوي للضغط الجوي عند مستوى سطح البحر",
    "PSL_Month_Mean": u"المتوسط الشهري للضغط الجوي عند مستوى سطح البحر",
    "PSL_Winter_Mean": u"متوسط الضغط الجوي عند مستوى البحر شتاءً",
    "PSL_Spring_Mean": u"متوسط الضغط الجوي عند مستوى البحر ربيعاً",
    "PSL_Summer_Mean": u"متوسط الضغط الجوي عند مستوى البحر صيفاً",
    "PSL_Autumn_Mean": u"متوسط الضغط الجوي عند مستوى البحر خريفاً",
    "PSL_Annual_Range": u"المدى السنوي للضغط الجوي عند مستوى البحر",
    "PSL_January_Mean": u"متوسط الضغط عند مستوى البحر لشهر يناير",
    "PSL_February_Mean": u"متوسط الضغط عند مستوى البحر لشهر فبراير",
    "PSL_March_Mean": u"متوسط الضغط عند مستوى البحر لشهر مارس",
    "PSL_April_Mean": u"متوسط الضغط عند مستوى البحر لشهر أبريل",
    "PSL_May_Mean": u"متوسط الضغط عند مستوى البحر لشهر مايو",
    "PSL_June_Mean": u"متوسط الضغط عند مستوى البحر لشهر يونيو",
    "PSL_July_Mean": u"متوسط الضغط عند مستوى البحر لشهر يوليو",
    "PSL_August_Mean": u"متوسط الضغط عند مستوى البحر لشهر أغسطس",
    "PSL_September_Mean": u"متوسط الضغط عند مستوى البحر لشهر سبتمبر",
    "PSL_October_Mean": u"متوسط الضغط عند مستوى البحر لشهر أكتوبر",
    "PSL_November_Mean": u"متوسط الضغط عند مستوى البحر لشهر نوفمبر",
    "PSL_December_Mean": u"متوسط الضغط عند مستوى البحر لشهر ديسمبر",

    # Surface Pressure
    "PS_Annual_Mean": u"المتوسط السنوي للضغط الجوي السطحي",
    "PS_Month_Mean": u"المتوسط الشهري للضغط الجوي السطحي",
    "PS_Winter_Mean": u"متوسط الضغط الجوي السطحي شتاءً",
    "PS_Spring_Mean": u"متوسط الضغط الجوي السطحي ربيعاً",
    "PS_Summer_Mean": u"متوسط الضغط الجوي السطحي صيفاً",
    "PS_Autumn_Mean": u"متوسط الضغط الجوي السطحي خريفاً",
    "PS_Annual_Range": u"المدى السنوي للضغط الجوي السطحي",
    "PS_January_Mean": u"متوسط الضغط الجوي السطحي لشهر يناير",
    "PS_February_Mean": u"متوسط الضغط الجوي السطحي لشهر فبراير",
    "PS_March_Mean": u"متوسط الضغط الجوي السطحي لشهر مارس",
    "PS_April_Mean": u"متوسط الضغط الجوي السطحي لشهر أبريل",
    "PS_May_Mean": u"متوسط الضغط الجوي السطحي لشهر مايو",
    "PS_June_Mean": u"متوسط الضغط الجوي السطحي لشهر يونيو",
    "PS_July_Mean": u"متوسط الضغط الجوي السطحي لشهر يوليو",
    "PS_August_Mean": u"متوسط الضغط الجوي السطحي لشهر أغسطس",
    "PS_September_Mean": u"متوسط الضغط الجوي السطحي لشهر سبتمبر",
    "PS_October_Mean": u"متوسط الضغط الجوي السطحي لشهر أكتوبر",
    "PS_November_Mean": u"متوسط الضغط الجوي السطحي لشهر نوفمبر",
    "PS_December_Mean": u"متوسط الضغط الجوي السطحي لشهر ديسمبر",

    # Wind Speed & Direction
    "W_Spd_Annual_Mean": u"المتوسط السنوي لسرعة الرياح",
    "W_Spd_Month_Mean": u"المتوسط الشهري لسرعة الرياح",
    "W_Spd_Winter_Mean": u"متوسط سرعة الرياح لفصل الشتاء",
    "W_Spd_Spring_Mean": u"متوسط سرعة الرياح لفصل الربيع",
    "W_Spd_Summer_Mean": u"متوسط سرعة الرياح لفصل الصيف",
    "W_Spd_Autumn_Mean": u"متوسط سرعة الرياح لفصل الخريف",
    "W_Spd_Annual_Max_Month": u"أعلى متوسط شهري لسرعة الرياح",
    "W_Spd_Annual_Min_Month": u"أدنى متوسط شهري لسرعة الرياح",
    "W_Spd_Annual_Range": u"المدى السنوي لسرعة الرياح",
    "W_Dir_Annual_Mean": u"المتوسط السنوي لاتجاه الرياح السائدة",
    "W_Dir_Month_Mean": u"المتوسط الشهري لاتجاه الرياح السائدة",
    "W_Dir_Winter_Mean": u"اتجاه الرياح السائدة لفصل الشتاء",
    "W_Dir_Spring_Mean": u"اتجاه الرياح السائدة لفصل الربيع",
    "W_Dir_Summer_Mean": u"اتجاه الرياح السائدة لفصل الصيف",
    "W_Dir_Autumn_Mean": u"اتجاه الرياح السائدة لفصل الخريف",
    "W_Spd_January_Mean": u"متوسط سرعة الرياح لشهر يناير",
    "W_Spd_February_Mean": u"متوسط سرعة الرياح لشهر فبراير",
    "W_Spd_March_Mean": u"متوسط سرعة الرياح لشهر مارس",
    "W_Spd_April_Mean": u"متوسط سرعة الرياح لشهر أبريل",
    "W_Spd_May_Mean": u"متوسط سرعة الرياح لشهر مايو",
    "W_Spd_June_Mean": u"متوسط سرعة الرياح لشهر يونيو",
    "W_Spd_July_Mean": u"متوسط سرعة الرياح لشهر يوليو",
    "W_Spd_August_Mean": u"متوسط سرعة الرياح لشهر أغسطس",
    "W_Spd_September_Mean": u"متوسط سرعة الرياح لشهر سبتمبر",
    "W_Spd_October_Mean": u"متوسط سرعة الرياح لشهر أكتوبر",
    "W_Spd_November_Mean": u"متوسط سرعة الرياح لشهر نوفمبر",
    "W_Spd_December_Mean": u"متوسط سرعة الرياح لشهر ديسمبر",
    "W_Dir_January_Mean": u"اتجاه الرياح السائدة لشهر يناير",
    "W_Dir_February_Mean": u"اتجاه الرياح السائدة لشهر فبراير",
    "W_Dir_March_Mean": u"اتجاه الرياح السائدة لشهر مارس",
    "W_Dir_April_Mean": u"اتجاه الرياح السائدة لشهر أبريل",
    "W_Dir_May_Mean": u"اتجاه الرياح السائدة لشهر مايو",
    "W_Dir_June_Mean": u"اتجاه الرياح السائدة لشهر يونيو",
    "W_Dir_July_Mean": u"اتجاه الرياح السائدة لشهر يوليو",
    "W_Dir_August_Mean": u"اتجاه الرياح السائدة لشهر أغسطس",
    "W_Dir_September_Mean": u"اتجاه الرياح السائدة لشهر سبتمبر",
    "W_Dir_October_Mean": u"اتجاه الرياح السائدة لشهر أكتوبر",
    "W_Dir_November_Mean": u"اتجاه الرياح السائدة لشهر نوفمبر",
    "W_Dir_December_Mean": u"اتجاه الرياح السائدة لشهر ديسمبر",

    # Relative Humidity
    "RH_Annual_Mean": u"المتوسط السنوي للرطوبة النسبية",
    "RH_Month_Mean": u"المتوسط الشهري للرطوبة النسبية",
    "RH_Winter_Mean": u"متوسط الرطوبة النسبية لفصل الشتاء",
    "RH_Spring_Mean": u"متوسط الرطوبة النسبية لفصل الربيع",
    "RH_Summer_Mean": u"متوسط الرطوبة النسبية لفصل الصيف",
    "RH_Autumn_Mean": u"متوسط الرطوبة النسبية لفصل الخريف",
    "RH_Annual_Range": u"المدى السنوي للرطوبة النسبية",
    "RH_January_Mean": u"متوسط الرطوبة النسبية لشهر يناير",
    "RH_February_Mean": u"متوسط الرطوبة النسبية لشهر فبراير",
    "RH_March_Mean": u"متوسط الرطوبة النسبية لشهر مارس",
    "RH_April_Mean": u"متوسط الرطوبة النسبية لشهر أبريل",
    "RH_May_Mean": u"متوسط الرطوبة النسبية لشهر مايو",
    "RH_June_Mean": u"متوسط الرطوبة النسبية لشهر يونيو",
    "RH_July_Mean": u"متوسط الرطوبة النسبية لشهر يوليو",
    "RH_August_Mean": u"متوسط الرطوبة النسبية لشهر أغسطس",
    "RH_September_Mean": u"متوسط الرطوبة النسبية لشهر سبتمبر",
    "RH_October_Mean": u"متوسط الرطوبة النسبية لشهر أكتوبر",
    "RH_November_Mean": u"متوسط الرطوبة النسبية لشهر نوفمبر",
    "RH_December_Mean": u"متوسط الرطوبة النسبية لشهر ديسمبر",

    # Dew Point
    "Td_Annual_Mean": u"المتوسط السنوي لدرجة حرارة نقطة الندى",
    "Td_Month_Mean": u"المتوسط الشهري لدرجة حرارة نقطة الندى",
    "Td_Winter_Mean": u"متوسط حرارة نقطة الندى لفصل الشتاء",
    "Td_Spring_Mean": u"متوسط حرارة نقطة الندى لفصل الربيع",
    "Td_Summer_Mean": u"متوسط حرارة نقطة الندى لفصل الصيف",
    "Td_Autumn_Mean": u"متوسط حرارة نقطة الندى لفصل الخريف",
    "Td_Annual_Range": u"المدى السنوي لدرجة حرارة نقطة الندى",
    "Td_January_Mean": u"متوسط حرارة نقطة الندى لشهر يناير",
    "Td_February_Mean": u"متوسط حرارة نقطة الندى لشهر فبراير",
    "Td_March_Mean": u"متوسط حرارة نقطة الندى لشهر مارس",
    "Td_April_Mean": u"متوسط حرارة نقطة الندى لشهر أبريل",
    "Td_May_Mean": u"متوسط حرارة نقطة الندى لشهر مايو",
    "Td_June_Mean": u"متوسط حرارة نقطة الندى لشهر يونيو",
    "Td_July_Mean": u"متوسط حرارة نقطة الندى لشهر يوليو",
    "Td_August_Mean": u"متوسط حرارة نقطة الندى لشهر أغسطس",
    "Td_September_Mean": u"متوسط حرارة نقطة الندى لشهر سبتمبر",
    "Td_October_Mean": u"متوسط حرارة نقطة الندى لشهر أكتوبر",
    "Td_November_Mean": u"متوسط حرارة نقطة الندى لشهر نوفمبر",
    "Td_December_Mean": u"متوسط حرارة نقطة الندى لشهر ديسمبر",

    # Solar Radiation
    "Sol_Annual_Mean": u"المتوسط السنوي للإشعاع الشمسي اليومي",
    "Sol_Month_Mean": u"المتوسط الشهري للإشعاع الشمسي اليومي",
    "Sol_Annual_Total": u"المجموع السنوي للإشعاع الشمسي",
    "Sol_Winter_Mean": u"متوسط الإشعاع الشمسي اليومي شتاءً",
    "Sol_Spring_Mean": u"متوسط الإشعاع الشمسي اليومي ربيعاً",
    "Sol_Summer_Mean": u"متوسط الإشعاع الشمسي اليومي صيفاً",
    "Sol_Autumn_Mean": u"متوسط الإشعاع الشمسي اليومي خريفاً",
    "Sol_Annual_Range": u"المدى السنوي للإشعاع الشمسي اليومي",
    "Sol_January_Mean": u"متوسط الإشعاع الشمسي لشهر يناير",
    "Sol_February_Mean": u"متوسط الإشعاع الشمسي لشهر فبراير",
    "Sol_March_Mean": u"متوسط الإشعاع الشمسي لشهر مارس",
    "Sol_April_Mean": u"متوسط الإشعاع الشمسي لشهر أبريل",
    "Sol_May_Mean": u"متوسط الإشعاع الشمسي لشهر مايو",
    "Sol_June_Mean": u"متوسط الإشعاع الشمسي لشهر يونيو",
    "Sol_July_Mean": u"متوسط الإشعاع الشمسي لشهر يوليو",
    "Sol_August_Mean": u"متوسط الإشعاع الشمسي لشهر أغسطس",
    "Sol_September_Mean": u"متوسط الإشعاع الشمسي لشهر سبتمبر",
    "Sol_October_Mean": u"متوسط الإشعاع الشمسي لشهر أكتوبر",
    "Sol_November_Mean": u"متوسط الإشعاع الشمسي لشهر نوفمبر",
    "Sol_December_Mean": u"متوسط الإشعاع الشمسي لشهر ديسمبر",

    # UV Index
    "UV_Annual_Mean": u"المتوسط السنوي لمؤشر الأشعة فوق البنفسجية",
    "UV_Month_Mean": u"المتوسط الشهري لمؤشر الأشعة فوق البنفسجية",
    "UV_Winter_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية شتاءً",
    "UV_Spring_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية ربيعاً",
    "UV_Summer_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية صيفاً",
    "UV_Autumn_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية خريفاً",
    "UV_Annual_Range": u"المدى السنوي لمؤشر الأشعة فوق البنفسجية",
    "UV_January_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يناير",
    "UV_February_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر فبراير",
    "UV_March_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر مارس",
    "UV_April_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أبريل",
    "UV_May_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر مايو",
    "UV_June_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يونيو",
    "UV_July_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر يوليو",
    "UV_August_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أغسطس",
    "UV_September_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر سبتمبر",
    "UV_October_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر أكتوبر",
    "UV_November_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر نوفمبر",
    "UV_December_Mean": u"متوسط مؤشر الأشعة فوق البنفسجية لشهر ديسمبر",

    # Cloud Cover
    "Cld_Annual_Mean": u"المتوسط السنوي للغطاء السحابي",
    "Cld_Month_Mean": u"المتوسط الشهري للغطاء السحابي",
    "Cld_Winter_Mean": u"متوسط كمية السحب لفصل الشتاء",
    "Cld_Spring_Mean": u"متوسط كمية السحب لفصل الربيع",
    "Cld_Summer_Mean": u"متوسط كمية السحب لفصل الصيف",
    "Cld_Autumn_Mean": u"متوسط كمية السحب لفصل الخريف",
    "Cld_Annual_Range": u"المدى السنوي للغطاء السحابي",
    "Cld_January_Mean": u"متوسط كمية السحب لشهر يناير",
    "Cld_February_Mean": u"متوسط كمية السحب لشهر فبراير",
    "Cld_March_Mean": u"متوسط كمية السحب لشهر مارس",
    "Cld_April_Mean": u"متوسط كمية السحب لشهر أبريل",
    "Cld_May_Mean": u"متوسط كمية السحب لشهر مايو",
    "Cld_June_Mean": u"متوسط كمية السحب لشهر يونيو",
    "Cld_July_Mean": u"متوسط كمية السحب لشهر يوليو",
    "Cld_August_Mean": u"متوسط كمية السحب لشهر أغسطس",
    "Cld_September_Mean": u"متوسط كمية السحب لشهر سبتمبر",
    "Cld_October_Mean": u"متوسط كمية السحب لشهر أكتوبر",
    "Cld_November_Mean": u"متوسط كمية السحب لشهر نوفمبر",
    "Cld_December_Mean": u"متوسط كمية السحب لشهر ديسمبر",

    # Heat Index
    "HI_Annual_Mean": u"المتوسط السنوي للحرارة المحسوسة",
    "HI_Summer_Mean": u"متوسط مؤشر الحرارة المحسوسة صيفاً",
    "HI_Winter_Mean": u"متوسط مؤشر الحرارة المحسوسة شتاءً",
    "HI_Annual_Range": u"المدى السنوي لمؤشر الحرارة المحسوسة",
    "WBGT_Summer_Mean": u"متوسط الإجهاد الحراري الرطب صيفاً",

    # Wind Chill
    "WC_Annual_Mean": u"المتوسط السنوي للإحساس ببرودة الرياح",
    "WC_Winter_Mean": u"متوسط تبريد الرياح شتاءً",

    # Aridity
    "DM_Aridity_Annual": u"معامل الجفاف لدي مارتون",
    "UNEP_Aridity_Annual": u"دليل الجفاف لبرنامج الأمم المتحدة للبيئة",
    "Water_Deficit_Annual": u"العجز المائي المناخي السنوي",
    "Dry_Months_Count": u"عدد الشهور الجافة المناخية",

    # Evapotranspiration
    "ET_Annual_Total": u"المجموع السنوي للبخر-نتح المرجعي",
    "ET_Annual_Mean": u"المتوسط الشهري للبخر والنتح",
    "ET_Month_Mean": u"المتوسط الشهري للبخر والنتح المرجعي",
    "ET_Annual_Range": u"المدى الشهري للبخر والنتح",
    "ET_Seasonal_Range": u"المدى الفصلي للبخر والنتح",
    "ET_Winter_Total": u"مجموع البخر والنتح لفصل الشتاء",
    "ET_Spring_Total": u"مجموع البخر والنتح لفصل الربيع",
    "ET_Summer_Total": u"مجموع البخر والنتح لفصل الصيف",
    "ET_Autumn_Total": u"مجموع البخر والنتح لفصل الخريف",
    "PET_Hargreaves_Annual": u"البخر-نتح الممكن بهارجريفز",

    # Trends & Anomalies
    "T_Annual_Trend_Decade": u"معدل تغير الحرارة لكل عقد",
    "R_Annual_Trend_Decade": u"معدل تغير الأمطار لكل عقد",
    "T_Annual_Anom": u"شذوذ درجة الحرارة السنوي",
    "T_Anom_Winter": u"شذوذ حرارة الشتاء",
    "T_Anom_Summer": u"شذوذ حرارة الصيف",
    "R_Annual_Anom": u"شذوذ الأمطار السنوي",
    "R_Annual_Anom_Pct": u"النسبة المئوية لشذوذ الأمطار السنوي",
    "R_Anom_Winter": u"شذوذ أمطار الشتاء",
    "R_Anom_Winter_Pct": u"النسبة المئوية لشذوذ أمطار الشتاء",
}

# Elements that need Month_Mean field added to GDB: (FC_name, source_fld, target_fld)
MONTH_MEAN_MAPPINGS = [
    ("Temperature", "T_Annual_Mean", "T_Month_Mean"),
    ("Sea_Level_Pressure", "PSL_Annual_Mean", "PSL_Month_Mean"),
    ("Surface_Pressure", "PS_Annual_Mean", "PS_Month_Mean"),
    ("Wind", "W_Spd_Annual_Mean", "W_Spd_Month_Mean"),
    ("Wind", "W_Dir_Annual_Mean", "W_Dir_Month_Mean"),
    ("Relative_Humidity", "RH_Annual_Mean", "RH_Month_Mean"),
    ("Dew_Point", "Td_Annual_Mean", "Td_Month_Mean"),
    ("Solar_Radiation", "Sol_Annual_Mean", "Sol_Month_Mean"),
    ("UV_Index", "UV_Annual_Mean", "UV_Month_Mean"),
    ("Cloud_Cover", "Cld_Annual_Mean", "Cld_Month_Mean"),
    ("Evapotranspiration", "ET_Annual_Mean", "ET_Month_Mean"),
]

# Rasters to replicate: (source_rel_path, target_rel_path)
RASTER_MAPPINGS = [
    (r"01_Temperature\T_Annual_Mean.tif", r"01_Temperature\T_Month_Mean.tif"),
    (r"03_Sea_Level_Pressure\PSL_Annual_Mean.tif", r"03_Sea_Level_Pressure\PSL_Month_Mean.tif"),
    (r"04_Surface_Pressure\PS_Annual_Mean.tif", r"04_Surface_Pressure\PS_Month_Mean.tif"),
    (r"05_Wind\Speed\W_Spd_Annual_Mean.tif", r"05_Wind\Speed\W_Spd_Month_Mean.tif"),
    (r"05_Wind\Direction\W_Dir_Annual_Mean.tif", r"05_Wind\Direction\W_Dir_Month_Mean.tif"),
    (r"06_Relative_Humidity\RH_Annual_Mean.tif", r"06_Relative_Humidity\RH_Month_Mean.tif"),
    (r"07_Dew_Point\Td_Annual_Mean.tif", r"07_Dew_Point\Td_Month_Mean.tif"),
    (r"08_Solar_Radiation\Sol_Annual_Mean.tif", r"08_Solar_Radiation\Sol_Month_Mean.tif"),
    (r"09_UV_Index\UV_Annual_Mean.tif", r"09_UV_Index\UV_Month_Mean.tif"),
    (r"10_Cloud_Cover\Cld_Annual_Mean.tif", r"10_Cloud_Cover\Cld_Month_Mean.tif"),
    (r"14_Evapotranspiration\ET_Annual_Mean.tif", r"14_Evapotranspiration\ET_Month_Mean.tif"),
]

# Excel files to update: (excel_name, source_col, target_col)
EXCEL_MAPPINGS = [
    ("Temperature.xls", "T_Annual_Mean", "T_Month_Mean"),
    ("Sea_Level_Pressure.xls", "PSL_Annual_Mean", "PSL_Month_Mean"),
    ("Surface_Pressure.xls", "PS_Annual_Mean", "PS_Month_Mean"),
    ("Wind.xls", "W_Spd_Annual_Mean", "W_Spd_Month_Mean"),
    ("Wind.xls", "W_Dir_Annual_Mean", "W_Dir_Month_Mean"),
    ("Relative_Humidity.xls", "RH_Annual_Mean", "RH_Month_Mean"),
    ("Dew_Point.xls", "Td_Annual_Mean", "Td_Month_Mean"),
    ("Solar_Radiation.xls", "Sol_Annual_Mean", "Sol_Month_Mean"),
    ("UV_Index.xls", "UV_Annual_Mean", "UV_Month_Mean"),
    ("Cloud_Cover.xls", "Cld_Annual_Mean", "Cld_Month_Mean"),
    ("Evapotranspiration.xls", "ET_Annual_Mean", "ET_Month_Mean"),
]


def update_geodatabase(gdb_path):
    print(">>> Updating Geodatabase: %s" % gdb_path)
    if not arcpy.Exists(gdb_path):
        print("  [ERROR] GDB does not exist: %s" % gdb_path)
        return

    arcpy.env.workspace = gdb_path
    fcs = arcpy.ListFeatureClasses()

    # 1. Add Month_Mean fields and populate them
    for fc_name, src_fld, tgt_fld in MONTH_MEAN_MAPPINGS:
        if fc_name in fcs:
            fc_path = os.path.join(gdb_path, fc_name)
            existing_fields = [f.name for f in arcpy.ListFields(fc_path)]
            alias = ARABIC_ALIASES.get(tgt_fld, tgt_fld)

            if tgt_fld not in existing_fields:
                print("  Adding field %s to %s (alias: %s)..." % (tgt_fld, fc_name, alias))
                arcpy.AddField_management(fc_path, tgt_fld, "DOUBLE", field_alias=alias)
            else:
                # Update alias
                try:
                    arcpy.management.AlterField(fc_path, tgt_fld, new_field_alias=alias)
                except Exception as e:
                    pass

            # Populate target field from source field
            if src_fld in existing_fields:
                print("  Populating %s = %s in %s..." % (tgt_fld, src_fld, fc_name))
                with arcpy.da.UpdateCursor(fc_path, [src_fld, tgt_fld]) as cur:
                    for row in cur:
                        row[1] = row[0]
                        cur.updateRow(row)

    # 2. Update Arabic Aliases for ALL fields in ALL feature classes
    print("  Updating descriptive Arabic aliases for all fields in all feature classes...")
    for fc in fcs:
        fc_path = os.path.join(gdb_path, fc)
        for f in arcpy.ListFields(fc_path):
            if f.name in ARABIC_ALIASES:
                ar_alias = ARABIC_ALIASES[f.name]
                if f.aliasName != ar_alias:
                    try:
                        arcpy.management.AlterField(fc_path, f.name, new_field_alias=ar_alias)
                    except Exception as e:
                        # Some system fields like OID/Shape cannot have alias altered
                        pass


def update_rasters(root_dir):
    print(">>> Updating Rasters in: %s" % root_dir)
    for src_rel, tgt_rel in RASTER_MAPPINGS:
        src_path = os.path.join(root_dir, src_rel)
        tgt_path = os.path.join(root_dir, tgt_rel)

        if os.path.exists(src_path):
            src_dir = os.path.dirname(src_path)
            tgt_dir = os.path.dirname(tgt_path)
            if not os.path.exists(tgt_dir):
                os.makedirs(tgt_dir)

            src_base = os.path.splitext(os.path.basename(src_path))[0]
            tgt_base = os.path.splitext(os.path.basename(tgt_path))[0]

            # Copy tif and all associated files (.tfw, .aux.xml, .ovr, .xml)
            for fname in os.listdir(src_dir):
                if fname.startswith(src_base):
                    ext_part = fname[len(src_base):]
                    src_file = os.path.join(src_dir, fname)
                    tgt_file = os.path.join(tgt_dir, tgt_base + ext_part)
                    shutil.copy2(src_file, tgt_file)
            print("  Created raster: %s (from %s)" % (tgt_rel, src_rel))
        else:
            print("  [WARN] Source raster not found: %s" % src_path)


def update_excel_workbooks(root_dir):
    print(">>> Updating Excel Workbooks in: %s" % root_dir)
    tables_dir = os.path.join(root_dir, "00_Tables_And_Reports")
    if not os.path.exists(tables_dir):
        print("  [WARN] Tables directory not found: %s" % tables_dir)
        return

    for xls_name, src_col, tgt_col in EXCEL_MAPPINGS:
        xls_path = os.path.join(tables_dir, xls_name)
        if not os.path.exists(xls_path):
            print("  [WARN] File not found: %s" % xls_path)
            continue

        try:
            # Read both sheets
            sheets = pd.read_excel(xls_path, sheet_name=None)
            if "Data" in sheets:
                df_data = sheets["Data"]
                if src_col in df_data.columns and tgt_col not in df_data.columns:
                    # Insert tgt_col right after src_col
                    idx = df_data.columns.get_loc(src_col) + 1
                    df_data.insert(idx, tgt_col, df_data[src_col])
                    sheets["Data"] = df_data

                    # Write back workbook with both sheets
                    with pd.ExcelWriter(xls_path, engine="openpyxl") as writer:
                        for s_name, s_df in sheets.items():
                            s_df.to_excel(writer, sheet_name=s_name, index=False)
                    print("  Updated %s: added %s" % (xls_name, tgt_col))
                else:
                    print("  %s already contains %s or missing %s" % (xls_name, tgt_col, src_col))
        except Exception as e:
            print("  [ERROR] Updating %s: %s" % (xls_name, e))


def main():
    print("=== STARTING CLIMATE ATLAS MONTH MEAN & ARABIC ALIASES UPDATE ===")
    
    # 1. Update Desktop
    if os.path.exists(DESKTOP_DIR):
        print("\n--- PROCESSING DESKTOP DATASET ---")
        gdb_desktop = os.path.join(DESKTOP_DIR, "Climate_Database_From_1996_To_2025.gdb")
        update_geodatabase(gdb_desktop)
        update_rasters(DESKTOP_DIR)
        update_excel_workbooks(DESKTOP_DIR)

    # 2. Update D Drive
    if os.path.exists(D_DRIVE_DIR):
        print("\n--- PROCESSING D: DRIVE DATASET ---")
        gdb_d = os.path.join(D_DRIVE_DIR, "Climate_Database_From_1996_To_2025.gdb")
        update_geodatabase(gdb_d)
        update_rasters(D_DRIVE_DIR)
        update_excel_workbooks(D_DRIVE_DIR)

    print("\n=== CLIMATE ATLAS MONTH MEAN & ARABIC ALIASES UPDATE COMPLETE ===")


if __name__ == "__main__":
    main()
