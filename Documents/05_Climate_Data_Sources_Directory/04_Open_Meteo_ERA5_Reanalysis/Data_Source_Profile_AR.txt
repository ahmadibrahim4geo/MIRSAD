# MIRSAD climate source profile

2026-10-18 · Implemented development source contract

## Open-Meteo ERA5 / ERA5-Land

ERA5 1940; Land 1950 → Latest archive, typically delayed

Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval | Daily

Global; Land variables require valid land cells | points, stations

T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, RH2M, T2MDEW, PS, SLP, WS10M, WD10M, CLOUD_AMT

Auto يستخدم Land للحرارة والرطوبة والندى، وERA5 لبقية المتغيرات المدعومة. للفترة التي تبدأ قبل 1950 يستخدم ERA5 كاملًا. الوضع المستقل لا يستكمل NASA؛ المسار القديم والهجين لهما سياسة معلنة منفصلة.

https://open-meteo.com/en/docs/historical-weather-api

[All sources](../SOURCES_AR.md)

No source guarantees complete coverage. Missing values stay NULL.