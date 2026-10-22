# دليل مصادر مرصاد — الحالة المنفذة

مراجعة 2026-10-21. نهاية الأرشيف متغيرة؛ لا تعني بداية المنتج وجود كل عنصر في كل موقع. بيانات المصدر ومؤشرات التغطية هي المرجع لكل تشغيل.

## NASA POWER

Meteorology 1981; radiation 1984; UV 2001 → Latest published data, variable-dependent | 0.5 x 0.625 degree meteorology; 1 x 1 degree radiation/cloud | Daily points; monthly regional

Global | points, stations, regional

**Variables:** T2M, T2M_MAX, T2M_MIN, T2MDEW, TS, PRECTOTCORR, RH2M, CLOUD_AMT, PS, SLP, WS10M, WD10M, ALLSKY_SFC_SW_DWN, ALLSKY_SFC_UV_INDEX

شبكات ثابتة حسب المتغير؛ تصغير بكسل الإخراج لا يزيد دقة معلومات المصدر.

[Official reference](https://power.larc.nasa.gov/docs/)

## Open-Meteo ERA5 / ERA5-Land

ERA5 1940; Land 1950 → Latest archive, typically delayed | Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval | Daily

Global; Land variables require valid land cells | points, stations

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, SUNSHINE_DURATION, RH2M, T2MDEW, PS, SLP, WS10M, WD10M, CLOUD_AMT, RH2M_MAX, RH2M_MIN, VPD_SOURCE, WS10M_CONFIRMED

Auto يستخدم Land للحرارة والرطوبة والندى، وERA5 لبقية المتغيرات المدعومة. للفترة التي تبدأ قبل 1950 يستخدم ERA5 كاملًا. الوضع المستقل لا يستكمل NASA؛ المسار القديم والهجين لهما سياسة معلنة منفصلة. إضافات RHmax/RHmin وVPD وساعات السطوع والرياح ذات ارتفاع القياس المؤكد مدمجة في Desktop وأداتَي Point وStation بالمسار اليومي؛ لا تشمل الشبكة الإقليمية. ملخصات الساعات تشترط 24 ساعة UTC صحيحة؛ counts وعمليات الاشتقاق محفوظة في Excel.

[Official reference](https://open-meteo.com/en/docs/historical-weather-api)

## NOAA GSOD

General archive 1929; station/element-specific → Station/year-specific | Station observations | Daily summaries

Exact catalogue station | stations

**Variables:** T2M, T2M_MAX, T2M_MIN, T2MDEW, PRECTOTCORR, PS, SLP, WS10M

USAF وWBAN والموقع معًا؛ ليس ISD الساعي ولا GHCN. الهجين ينهي NOAA ثم ERA5 ثم NASA ثم Gap Fill الشهري.

[Official reference](https://www.ncei.noaa.gov/data/global-summary-of-the-day/)

## Copernicus CDS ERA5-Land (Need Sign In)

1950-01 → Latest published CDS ARCO data | 0.1 degree API grid | Daily

Global land | points, stations

**Variables:** T2M, T2M_MAX, T2M_MIN, T2MDEW, RH2M, TS, PS, WS10M, WD10M, PRECTOTCORR, ALLSKY_SFC_SW_DWN

Need Sign In: رمز CDS الشخصي وقبول شروط المنتج. ARCO ساعي منزوع التراكم بالفعل؛ اليوم يتطلب 24 ساعة UTC. العظمى والصغرى من العينات الساعية، والرطوبة مشتقة من الحرارة والندى. الخدمة ترجع كامل الأرشيف لكل متغير ثم تُرشح الفترة محليًا بحد 64MB. المسار منفذ واختُبر بروتوكوله وتحويلاته؛ لم يُختبر بحساب حقيقي.

[Official reference](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries)

## NASA IMERG V07 Daily Final (Need Sign In)

File-specific GES DISC catalogue → Latest Final run (delayed) | 0.1 degree | Daily

Global grid; missing cells retained | points, stations

**Variables:** PRECTOTCORR

Need Sign In: حساب NASA Earthdata وإجازة GES DISC. أمطار Final اليومية بوحدة mm/day؛ لا ضرب ثانٍ في 24. المسار منفذ؛ التنزيل بحساب حقيقي لم يُختبر بعد.

[Official reference](https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary)

## CHIRPS v3 (Monthly Rainfall)

1981-01 → Latest final month | 0.05 degree | Monthly

Land 60S to 60N | points, stations, regional

**Variables:** PRECTOTCORR

أمطار شهرية نهائية؛ لم يُنفذ تنزيل CHIRPS اليومي. الصفر صحيح والمفقود NULL.

[Official reference](https://www.chc.ucsb.edu/data/chirps3)

## TerraClimate v1.1 (Monthly Climate)

1950-01 → Latest published month; inspected from time axis | 1/24 degree (~4 km) | Monthly

Global land | points, stations

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, WS10M, ALLSKY_SFC_SW_DWN

الإصدار 1.1 مستقل عن 1.0. قراءة CF scale/offset من كل متغير. متوسط الحرارة مشتق من (العظمى+الصغرى)/2. المطر مجموع شهري.

[Official reference](https://www.climatologylab.org/terraclimate.html)

## CHELSA v2.1 (Monthly Climate)

1979/1980; variable-specific catalogue → 2018/2021; variable-specific catalogue | 30 arcsec (~1 km) | Monthly

Global land | points, stations, regional

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, WS10M, RH2M, CLOUD_AMT

تُقرأ الوحدات والتحويل من الملف نفسه؛ مدى التواريخ يختلف حسب المتغير. الإشعاع الشمسي مستبعد حتى حل تعارض بيانات وحدته. الملف غير المتاح يبقى NULL.

[Official reference](https://www.chelsa-climate.org/datasets/chelsa_monthly)

## MODIS MOD11A2 (Daytime Surface Temperature)

2000-02 → Available site dates from API | Nominal 1 km | 8-day clear-sky composites; explicit monthly aggregation

Global land | points, stations

**Variables:** TS

حرارة سطح نهارية، وليست حرارة هواء. تجميع شهري موزون بأيام السماء الصافية المقبولة بالجودة. لا أيام رصد مصطنعة ولا فرق سطح/هواء دون حرارة هواء.

[Official reference](https://modis.ornl.gov/data/modis_webservice.html)

## MODIS MOD11A2 (Nighttime Surface Temperature)

2000-02 → Available site dates from API | Nominal 1 km | 8-day clear-sky composites; explicit monthly aggregation

Global land | points, stations

**Variables:** TS

حرارة سطح ليلية منفصلة عن النهارية، بنفس فحص الجودة والسحب. نسبة التغطية تعكس الأيام الصافية المقبولة.

[Official reference](https://modis.ornl.gov/data/modis_webservice.html)

## NOAA GHCN-Daily (Station Observations Only)

Station/element-specific → Station/element-specific | Station location | Daily

Catalogue stations only | stations

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR

يلزم حقل GHCN_ID صريح من 11 حرفًا وإحداثيات مطابقة. لا تحويل تلقائي من USAF/WBAN ولا أقرب محطة. قيم QFLAG غير الفارغة تستبعد؛ TAVG غير الموجود لا يُخترع.

[Official reference](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)
