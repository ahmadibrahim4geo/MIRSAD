# MIRSAD climate sources — implemented state

Reviewed 2026-10-18. Archive ends change; a product start does not guarantee every variable at every location. Inspect per-run provenance and coverage.

## NASA POWER

Meteorology 1981; radiation 1984; UV 2001 → Latest published data, variable-dependent | 0.5 x 0.625 degree meteorology; 1 x 1 degree radiation/cloud | Daily points; monthly regional

Global | points, stations, regional

**Variables:** T2M, T2M_MAX, T2M_MIN, T2MDEW, TS, PRECTOTCORR, RH2M, CLOUD_AMT, PS, SLP, WS10M, WD10M, ALLSKY_SFC_SW_DWN, ALLSKY_SFC_UV_INDEX

Fixed variable-specific grids; smaller output pixels do not increase source information resolution.

[Official reference](https://power.larc.nasa.gov/docs/)

## Open-Meteo ERA5 / ERA5-Land

ERA5 1940; Land 1950 → Latest archive, typically delayed | Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval | Daily

Global; Land variables require valid land cells | points, stations

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, RH2M, T2MDEW, PS, SLP, WS10M, WD10M, CLOUD_AMT

Auto uses Land for temperature, RH and dewpoint and ERA5 for other supported variables. An interval beginning before 1950 uses ERA5 throughout. Standalone never supplements NASA; legacy and Hybrid retain explicitly separate policies.

[Official reference](https://open-meteo.com/en/docs/historical-weather-api)

## NOAA GSOD

General archive 1929; station/element-specific → Station/year-specific | Station observations | Daily summaries

Exact catalogue station | stations

**Variables:** T2M, T2M_MAX, T2M_MIN, T2MDEW, PRECTOTCORR, PS, SLP, WS10M

USAF, WBAN and location are required together. This is not hourly ISD or GHCN. Hybrid finishes NOAA, then ERA5, then NASA, then optional monthly Gap Fill.

[Official reference](https://www.ncei.noaa.gov/data/global-summary-of-the-day/)

## Copernicus CDS ERA5-Land (Need Sign In)

1950-01 → Latest published CDS ARCO data | 0.1 degree API grid | Daily

Global land | points, stations

**Variables:** T2M, T2M_MAX, T2M_MIN, T2MDEW, RH2M, TS, PS, WS10M, WD10M, PRECTOTCORR, ALLSKY_SFC_SW_DWN

Need Sign In: personal CDS token and accepted dataset terms. ARCO is already hourly de-accumulated; a day requires 24 UTC hours. Max/min use hourly samples; RH is derived from temperature/dewpoint. The service returns the full archive per variable, filtered locally with a 64 MB limit. Protocol/conversion tests pass; authenticated end-to-end access remains unverified.

[Official reference](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries)

## NASA IMERG V07 Daily Final (Need Sign In)

File-specific GES DISC catalogue → Latest Final run (delayed) | 0.1 degree | Daily

Global grid; missing cells retained | points, stations

**Variables:** PRECTOTCORR

Need Sign In: NASA Earthdata account with GES DISC authorization. Final daily precipitation is mm/day, with no second multiplication by 24. Adapter implemented; live authenticated download remains unverified.

[Official reference](https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary)

## CHIRPS v3 (Monthly Rainfall)

1981-01 → Latest final month | 0.05 degree | Monthly

Land 60S to 60N | points, stations, regional

**Variables:** PRECTOTCORR

Final monthly rainfall only; daily CHIRPS ingestion is not implemented. Zero is valid; missing stays NULL.

[Official reference](https://www.chc.ucsb.edu/data/chirps3)

## TerraClimate v1.1 (Monthly Climate)

1950-01 → Latest published month; inspected from time axis | 1/24 degree (~4 km) | Monthly

Global land | points, stations

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, WS10M, ALLSKY_SFC_SW_DWN

v1.1 is separate from v1.0. CF scale/offset are read per variable. Mean temperature is (tmax+tmin)/2. Rainfall is a monthly total.

[Official reference](https://www.climatologylab.org/terraclimate.html)

## CHELSA v2.1 (Monthly Climate)

1979/1980; variable-specific catalogue → 2018/2021; variable-specific catalogue | 30 arcsec (~1 km) | Monthly

Global land | points, stations, regional

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, WS10M, RH2M, CLOUD_AMT

Units/scaling are validated from each file; dates vary by variable. Solar radiation is excluded pending conflicting unit metadata. Unavailable files stay NULL.

[Official reference](https://www.chelsa-climate.org/datasets/chelsa_monthly)

## MODIS MOD11A2 (Daytime Surface Temperature)

2000-02 → Available site dates from API | Nominal 1 km | 8-day clear-sky composites; explicit monthly aggregation

Global land | points, stations

**Variables:** TS

Daytime surface temperature, not air temperature. Monthly estimates weight quality-accepted clear-sky days. No synthetic daily observations or surface-air differences without air data.

[Official reference](https://modis.ornl.gov/data/modis_webservice.html)

## MODIS MOD11A2 (Nighttime Surface Temperature)

2000-02 → Available site dates from API | Nominal 1 km | 8-day clear-sky composites; explicit monthly aggregation

Global land | points, stations

**Variables:** TS

Nighttime surface temperature stays separate from daytime, with the same quality/cloud screening. Coverage reflects accepted clear-sky days.

[Official reference](https://modis.ornl.gov/data/modis_webservice.html)

## NOAA GHCN-Daily (Station Observations Only)

Station/element-specific → Station/element-specific | Station location | Daily

Catalogue stations only | stations

**Variables:** T2M, T2M_MAX, T2M_MIN, PRECTOTCORR

Requires an explicit 11-character GHCN_ID and matching coordinates. No USAF/WBAN conversion or nearest-station substitution. Nonblank QFLAG values are excluded; absent TAVG is not invented.

[Official reference](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)
