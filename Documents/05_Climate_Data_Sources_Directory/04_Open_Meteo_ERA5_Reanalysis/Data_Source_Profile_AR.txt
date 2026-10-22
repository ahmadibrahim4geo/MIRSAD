# MIRSAD climate source profile

2026-10-21 · Implemented development source contract

## Open-Meteo ERA5 / ERA5-Land

ERA5 1940; Land 1950 → Latest archive, typically delayed

Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval | Daily

Global; Land variables require valid land cells | points, stations

T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, SUNSHINE_DURATION, RH2M, T2MDEW, PS, SLP, WS10M, WD10M, CLOUD_AMT, RH2M_MAX, RH2M_MIN, VPD_SOURCE, WS10M_CONFIRMED

Auto يستخدم Land للحرارة والرطوبة والندى، وERA5 لبقية المتغيرات المدعومة. للفترة التي تبدأ قبل 1950 يستخدم ERA5 كاملًا. الوضع المستقل لا يستكمل NASA؛ المسار القديم والهجين لهما سياسة معلنة منفصلة. إضافات RHmax/RHmin وVPD وساعات السطوع والرياح ذات ارتفاع القياس المؤكد مدمجة في Desktop وأداتَي Point وStation بالمسار اليومي؛ لا تشمل الشبكة الإقليمية. ملخصات الساعات تشترط 24 ساعة UTC صحيحة؛ counts وعمليات الاشتقاق محفوظة في Excel.

https://open-meteo.com/en/docs/historical-weather-api

[All sources](../SOURCES_AR.md)

No source guarantees complete coverage. Missing values stay NULL.