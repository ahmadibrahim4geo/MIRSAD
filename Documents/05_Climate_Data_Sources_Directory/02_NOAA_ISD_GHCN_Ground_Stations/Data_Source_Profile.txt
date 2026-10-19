# MIRSAD climate source profile

2026-10-18 · Implemented development source contract

## NOAA GSOD

General archive 1929; station/element-specific → Station/year-specific

Station observations | Daily summaries

Exact catalogue station | stations

T2M, T2M_MAX, T2M_MIN, T2MDEW, PRECTOTCORR, PS, SLP, WS10M

USAF, WBAN and location are required together. This is not hourly ISD or GHCN. Hybrid finishes NOAA, then ERA5, then NASA, then optional monthly Gap Fill.

https://www.ncei.noaa.gov/data/global-summary-of-the-day/

## NOAA GHCN-Daily (Station Observations Only)

Station/element-specific → Station/element-specific

Station location | Daily

Catalogue stations only | stations

T2M, T2M_MAX, T2M_MIN, PRECTOTCORR

Requires an explicit 11-character GHCN_ID and matching coordinates. No USAF/WBAN conversion or nearest-station substitution. Nonblank QFLAG values are excluded; absent TAVG is not invented.

https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

[All sources](../SOURCES_EN.md)

No source guarantees complete coverage. Missing values stay NULL.