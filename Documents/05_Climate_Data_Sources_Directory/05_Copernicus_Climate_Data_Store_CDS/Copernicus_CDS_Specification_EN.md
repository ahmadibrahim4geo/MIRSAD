# MIRSAD climate source profile

2026-10-18 · Implemented development source contract

## Copernicus CDS ERA5-Land (Need Sign In)

1950-01 → Latest published CDS ARCO data

0.1 degree API grid | Daily

Global land | points, stations

T2M, T2M_MAX, T2M_MIN, T2MDEW, RH2M, TS, PS, WS10M, WD10M, PRECTOTCORR, ALLSKY_SFC_SW_DWN

Need Sign In: personal CDS token and accepted dataset terms. ARCO is already hourly de-accumulated; a day requires 24 UTC hours. Max/min use hourly samples; RH is derived from temperature/dewpoint. The service returns the full archive per variable, filtered locally with a 64 MB limit. Protocol/conversion tests pass; authenticated end-to-end access remains unverified.

https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries

[All sources](../SOURCES_EN.md)

No source guarantees complete coverage. Missing values stay NULL.

ARCO daily conversions: complete 24-hour UTC days; Kelvin to Celsius; Pa to kPa; sum already de-accumulated hourly precipitation metres × 1000; sum hourly solar joules ÷ 1e6. Hourly-sample maxima/minima; RH from the documented Magnus formula. Unsupported sea-level pressure, cloud and UV remain NULL.
