# MIRSAD climate source profile

2026-10-18 · Implemented development source contract

## Open-Meteo ERA5 / ERA5-Land

ERA5 1940; Land 1950 → Latest archive, typically delayed

Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval | Daily

Global; Land variables require valid land cells | points, stations

T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, RH2M, T2MDEW, PS, SLP, WS10M, WD10M, CLOUD_AMT

Auto uses Land for temperature, RH and dewpoint and ERA5 for other supported variables. An interval beginning before 1950 uses ERA5 throughout. Standalone never supplements NASA; legacy and Hybrid retain explicitly separate policies.

https://open-meteo.com/en/docs/historical-weather-api

[All sources](../SOURCES_EN.md)

No source guarantees complete coverage. Missing values stay NULL.