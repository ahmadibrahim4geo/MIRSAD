# MIRSAD climate source profile

2026-10-21 · Implemented development source contract

## NOAA GSOD

General archive 1929; station/element-specific → Station/year-specific

Station observations | Daily summaries

Exact catalogue station | stations

T2M, T2M_MAX, T2M_MIN, T2MDEW, PRECTOTCORR, PS, SLP, WS10M

USAF وWBAN والموقع معًا؛ ليس ISD الساعي ولا GHCN. الهجين ينهي NOAA ثم ERA5 ثم NASA ثم Gap Fill الشهري.

https://www.ncei.noaa.gov/data/global-summary-of-the-day/

## NOAA GHCN-Daily (Station Observations Only)

Station/element-specific → Station/element-specific

Station location | Daily

Catalogue stations only | stations

T2M, T2M_MAX, T2M_MIN, PRECTOTCORR

يلزم حقل GHCN_ID صريح من 11 حرفًا وإحداثيات مطابقة. لا تحويل تلقائي من USAF/WBAN ولا أقرب محطة. قيم QFLAG غير الفارغة تستبعد؛ TAVG غير الموجود لا يُخترع.

https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

[All sources](../SOURCES_AR.md)

No source guarantees complete coverage. Missing values stay NULL.