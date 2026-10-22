# MIRSAD climate source profile

2026-10-21 · Implemented development source contract

## Open-Meteo ERA5 / ERA5-Land

ERA5 1940; Land 1950 → Latest archive, typically delayed

Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval | Daily

Global; Land variables require valid land cells | points, stations

T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, SUNSHINE_DURATION, RH2M, T2MDEW, PS, SLP, WS10M, WD10M, CLOUD_AMT, RH2M_MAX, RH2M_MIN, VPD_SOURCE, WS10M_CONFIRMED

Auto uses Land for temperature, RH and dewpoint and ERA5 for other supported variables. An interval beginning before 1950 uses ERA5 throughout. Standalone never supplements NASA; legacy and Hybrid retain explicitly separate policies. New RH extrema, VPD, sunshine and confirmed-height wind options are integrated in Desktop and the Daily Point/Station tools; regional activation is not included. Hourly aggregation requires 24 valid UTC hours; sample counts and operations are exported in Excel.

https://open-meteo.com/en/docs/historical-weather-api

[All sources](../SOURCES_EN.md)

No source guarantees complete coverage. Missing values stay NULL.