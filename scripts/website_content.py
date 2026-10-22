"""Presentation translations only; source capability/units stay in the runtime registry."""

SOURCE_AR = {
    'power': dict(label='NASA POWER — الأرصاد والإشعاع', start='الأرصاد: 1981؛ الإشعاع: 1984؛ الأشعة فوق البنفسجية: 2001', end='أحدث بيانات منشورة، حسب المتغير', resolution='الأرصاد: ‎0.5 × 0.625 درجة؛ الإشعاع والسحب: ‎1 × 1 درجة', temporal='يومية للنقاط والمحطات؛ شهرية للشبكة الإقليمية', region='تغطية عالمية'),
    'openmeteo': dict(label='Open-Meteo — إعادة التحليل ERA5 وERA5-Land', start='ERA5: سنة 1940؛ ERA5-Land: سنة 1950', end='أحدث بيانات الأرشيف، مع تأخر النشر', resolution='اختيار تلقائي لكل متغير وللفترة كاملة: ‎0.1 درجة لليابسة أو ‎0.25 درجة لـERA5', temporal='يومية', region='عالمية؛ متغيرات ERA5-Land تحتاج خلية يابسة صالحة'),
    'gsod': dict(label='NOAA GSOD — ملخصات الرصد اليومي للمحطات', start='يبدأ الأرشيف العام سنة 1929؛ البداية الفعلية حسب المحطة والعنصر', end='حسب المحطة والسنة وتوافر الرصد', resolution='رصد في موقع المحطة؛ ليست شبكة بكسلات', temporal='ملخصات يومية', region='المحطة المحددة في الدليل، بمعرفها وموقعها'),
    'cds_era5_land_arco': dict(label='Copernicus CDS — السلسلة الزمنية ERA5-Land', start='يناير 1950', end='أحدث بيانات ARCO المنشورة لدى CDS', resolution='شبكة واجهة الخدمة: ‎0.1 درجة', temporal='يومية، مجمعة من الساعات المكتملة', region='اليابسة عالميًا'),
    'imerg07_final': dict(label='NASA IMERG V07 — الأمطار اليومية النهائية', start='حسب الملفات المتاحة في دليل GES DISC', end='أحدث تشغيل نهائي منشور، مع تأخر النشر', resolution='‎0.1 درجة', temporal='يومية', region='شبكة عالمية؛ الخلايا المفقودة تظل مفقودة'),
    'chirps3': dict(label='CHIRPS v3 — الأمطار الشهرية', start='يناير 1981', end='أحدث شهر نهائي منشور', resolution='‎0.05 درجة', temporal='شهرية', region='اليابسة بين دائرتي عرض ‎60° جنوبًا و‎60° شمالًا'),
    'terraclimate11': dict(label='TerraClimate v1.1 — المناخ الشهري', start='يناير 1950', end='أحدث شهر منشور؛ يُقرأ من المحور الزمني للملف', resolution='‎1/24 درجة، نحو 4 كم', temporal='شهرية', region='اليابسة عالميًا'),
    'chelsa21': dict(label='CHELSA v2.1 — المناخ الشهري', start='1979 أو 1980، حسب دليل المتغير', end='2018 أو 2021، حسب دليل المتغير', resolution='30 ثانية قوسية، نحو 1 كم', temporal='شهرية', region='اليابسة عالميًا'),
    'mod11a2_day': dict(label='MODIS MOD11A2 — حرارة السطح نهارًا', start='فبراير 2000', end='التواريخ المتاحة للموقع في واجهة الخدمة', resolution='دقة اسمية: 1 كم', temporal='مركبات لثمانية أيام صافية؛ تجميع شهري صريح', region='اليابسة عالميًا'),
    'mod11a2_night': dict(label='MODIS MOD11A2 — حرارة السطح ليلًا', start='فبراير 2000', end='التواريخ المتاحة للموقع في واجهة الخدمة', resolution='دقة اسمية: 1 كم', temporal='مركبات لثمانية أيام صافية؛ تجميع شهري صريح', region='اليابسة عالميًا'),
    'ghcnd': dict(label='NOAA GHCN-Daily — الرصد اليومي للمحطات', start='حسب المحطة والعنصر المناخي', end='حسب المحطة والعنصر المناخي', resolution='رصد في موقع المحطة؛ ليست شبكة بكسلات', temporal='يومية', region='محطات الدليل فقط، بمعرف GHCN صريح'),
}

VARIABLES = {
    'T2M': ('متوسط حرارة الهواء عند مترين', 'Mean air temperature at 2 m'),
    'T2M_MAX': ('العظمى لحرارة الهواء عند مترين', 'Maximum air temperature at 2 m'),
    'T2M_MIN': ('الصغرى لحرارة الهواء عند مترين', 'Minimum air temperature at 2 m'),
    'T2MDEW': ('درجة حرارة نقطة الندى عند مترين', 'Dew-point temperature at 2 m'),
    'TS': ('درجة حرارة سطح الأرض', 'Land surface temperature'),
    'PRECTOTCORR': ('هطول الأمطار', 'Precipitation'),
    'RH2M': ('الرطوبة النسبية عند مترين', 'Relative humidity at 2 m'),
    'RH2M_MAX': ('أقصى رطوبة يومية مشتقة من ساعات مكتملة — إضافة اختيارية للنقاط والمحطات', 'Daily maximum RH from complete hours — optional point/station output'),
    'RH2M_MIN': ('أدنى رطوبة يومية مشتقة من ساعات مكتملة — إضافة اختيارية للنقاط والمحطات', 'Daily minimum RH from complete hours — optional point/station output'),
    'VPD_SOURCE': ('أقصى عجز يومي لضغط البخار من المصدر — إضافة اختيارية للنقاط والمحطات', 'Source daily maximum vapour pressure deficit — optional point/station output'),
    'SUNSHINE_DURATION': ('مدة السطوع اليومية بالثواني — إضافة اختيارية للنقاط والمحطات', 'Daily sunshine duration in seconds — optional point/station output'),
    'WS10M_CONFIRMED': ('سرعة رياح بارتفاع مؤكد 10 أمتار للحسابات الإضافية', 'Confirmed 10 m wind for optional calculations'),
    'CLOUD_AMT': ('نسبة الغطاء السحابي', 'Cloud-cover fraction'),
    'PS': ('الضغط الجوي عند السطح', 'Surface pressure'),
    'SLP': ('الضغط الجوي المختزل إلى مستوى البحر', 'Sea-level pressure'),
    'WS10M': ('سرعة الرياح عند 10 أمتار', 'Wind speed at 10 m'),
    'WD10M': ('اتجاه الرياح عند 10 أمتار', 'Wind direction at 10 m'),
    'ALLSKY_SFC_SW_DWN': ('طاقة الإشعاع الشمسي قصير الموجة الهابط عند السطح', 'Surface downwelling shortwave solar energy'),
    'ALLSKY_SFC_UV_INDEX': ('مؤشر الأشعة فوق البنفسجية', 'Ultraviolet index'),
}

TOOLS = {'points': ('النقاط', 'Points'), 'stations': ('المحطات', 'Stations'), 'regional': ('الشبكة الإقليمية', 'Regional grid')}

MODULE_DESCRIPTIONS = {
    'Temperature': ('متوسط الحرارة والعظمى والصغرى والمدى الحراري.', 'Mean, maximum and minimum air temperature and temperature range.'),
    'Land Surface Temperature': ('حرارة السطح والفرق عن حرارة الهواء؛ ليست رصدًا إضافيًا لحرارة الهواء.', 'Surface temperature and its difference from air temperature; not another air observation.'),
    'Precipitation': ('مجاميع الفترات المكتملة ومتوسطاتها المناخية؛ المفقود ليس صفرًا.', 'Complete-period totals and their climatological means; missing is not zero.'),
    'Sea Level Pressure': ('الضغط المختزل إلى مستوى سطح البحر.', 'Pressure reduced to sea level.'),
    'Surface Pressure': ('الضغط عند ارتفاع السطح، منفصلًا عن ضغط مستوى البحر.', 'Pressure at the surface elevation, distinct from sea-level pressure.'),
    'Wind': ('سرعة الرياح عند 10 أمتار والاتجاه بمتوسط دائري.', '10 m wind speed and circular-mean wind direction.'),
    'Relative Humidity': ('ملخصات الرطوبة النسبية بالنسبة المئوية.', 'Relative humidity summaries in percent.'),
    'Dew Point': ('ملخصات درجة حرارة نقطة الندى.', 'Dew-point temperature summaries.'),
    'Solar Radiation': ('متوسط الطاقة اليومية للإشعاع الشمسي وملخصاتها.', 'Mean daily solar energy and its summaries.'),
    'UV Index': ('مؤشر الأشعة فوق البنفسجية، مع توضيح تقريب الظهر الموروث لبيانات NASA.', 'UV index with the inherited NASA noon approximation documented.'),
    'Cloud Cover': ('متوسط نسبة الغطاء السحابي.', 'Mean cloud-cover fraction.'),
    'Heat Index': ('تقدير الإجهاد من الحرارة والرطوبة؛ نواتج WBGT تقريبية وليست قياس جهاز.', 'Heat/humidity stress estimates; WBGT outputs are approximate, not instrument readings.'),
    'Wind Chill': ('برودة الرياح ضمن مجال تطبيق المعادلة.', 'Wind chill within the formula’s domain.'),
    'De Martonne Aridity': ('مؤشر دي مارتون من المطر وحرارة الهواء.', 'De Martonne aridity from rainfall and air temperature.'),
    'Evapotranspiration': ('Hargreaves هو الافتراضي من الحرارة ودائرة العرض. المصدر الحالي يتيح أيضًا Penman–Monteith يوميًا عند اكتمال مدخلاته، كحساب مستقل في Desktop والنقاط والمحطات.', 'Hargreaves is the default, from temperature and latitude. Current source also offers independent daily Penman–Monteith in Desktop and point/station tools when its inputs are complete.'),
    'UNEP Aridity': ('نسبة المطر إلى البخر والنتح المحتمل، عند اكتمال المدخلات.', 'Precipitation / potential evapotranspiration when inputs are valid.'),
    'Water Deficit': ('العجز المائي وفق المطر والبخر والنتح في المحرك.', 'Water deficit from the kernel’s rainfall/PET calculations.'),
    'Dry Months': ('عدد الأشهر الجافة وفق مقارنة المطر بالحرارة.', 'Dry-month count from precipitation and temperature.'),
    'Trends & Anomalies': ('اتجاهات الحرارة والمطر والشذوذ عن خط الأساس، عند كفاية السنوات.', 'Temperature/rainfall trends and baseline anomalies when enough years are available.'),
}
