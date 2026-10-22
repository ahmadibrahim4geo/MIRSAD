# -*- coding: utf-8 -*-
"""Python 2/3 provider policies and real native resolution choices."""
from __future__ import unicode_literals

STATION_HYBRID = "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling"
GRID_HYBRID = "Hybrid: ERA5 + NASA POWER (Any Point)"
NOAA_ONLY = "NOAA GSOD (Station Observations Only)"
ERA5_ONLY = "Open-Meteo ERA5 (Standalone - No NASA Supplement)"
LEGACY_OM = "Open-Meteo ERA5"
ERA5_MODELS = (
    "Auto: Finest suitable model per variable [Default]",
    "ERA5-Land (0.1 deg ~11 km API grid) [Manual]",
    "ERA5-Seamless (0.1-0.25 deg; variable-dependent)",
    "ERA5 (0.25 deg ~25 km API grid)",
)
NOAA_RESOLUTION = "Station observations (native point; no selectable grid resolution)"
POWER_RESOLUTION = "Native POWER grids (meteo 0.5 x 0.625 deg; solar 1 x 1 deg)"


def pipeline_sources(provider):
    text=provider or ""
    if "Hybrid" in text or "هجين" in text:
        if "NOAA" not in text and "ERA5" in text and "NASA" in text:
            return ("Open-Meteo","NASA POWER")
        return ("NOAA GSOD","Open-Meteo","NASA POWER")
    if "NOAA GSOD" in text:return ("NOAA GSOD",)
    if "Open-Meteo" in text and "Standalone" in text:return ("Open-Meteo",)
    return None


def uses_reanalysis(provider):
    order=pipeline_sources(provider)
    return "Open-Meteo" in order if order else "Open-Meteo" in (provider or "")


def resolution_options(provider):
    if uses_reanalysis(provider):return ERA5_MODELS
    from .climate_products import descriptor
    spec=descriptor(provider)
    if spec:return ("Auto: native "+spec["resolution"]+" | "+spec["temporal"],)
    return (NOAA_RESOLUTION,) if "NOAA GSOD" in (provider or "") else (POWER_RESOLUTION,)


def canonical_resolution(value):
    text=(value or "").lower()
    if "auto" in text:return ERA5_MODELS[0]
    if "seamless" in text:return ERA5_MODELS[2]
    if "land" in text:return ERA5_MODELS[1]
    if "era5" in text:return ERA5_MODELS[3]
    return ERA5_MODELS[0]


LAND_VARIABLES=("T2M","T2M_MAX","T2M_MIN","RH2M","T2MDEW")
ENRICHMENT_LAND_VARIABLES=("RH2M_MAX","RH2M_MIN")


def model_code(value):
    text=(value or "auto").lower()
    if "auto" in text:return "auto"
    if "seamless" in text:return "era5_seamless"
    if "land" in text:return "era5_land"
    if "era5" in text:return "era5"
    raise ValueError("Unknown ERA5 selection: "+str(value))


def reanalysis_plan(required,selection,start):
    """Finest supported product for the entire requested period, never per year."""
    selected=model_code(selection)
    if selected!="auto":return [(selected,list(required))]
    if start.year<1950:return [("era5",list(required))]
    land=[p for p in required if p in LAND_VARIABLES+ENRICHMENT_LAND_VARIABLES]
    atmospheric=[p for p in required if p not in LAND_VARIABLES+ENRICHMENT_LAND_VARIABLES]
    return [(code,params) for code,params in (("era5_land",land),("era5",atmospheric)) if params]


def variable_resolution(source,variable,model=None):
    if source=="NOAA GSOD":return dict(product="GSOD",spatial="Station location",temporal="Daily")
    if source=="NASA POWER":
        solar=variable in ("ALLSKY_SFC_SW_DWN","ALLSKY_SFC_UV_INDEX","CLOUD_AMT")
        return dict(product="NASA POWER radiation/cloud" if solar else "NASA POWER meteorology",spatial="1 x 1 degree" if solar else "0.5 x 0.625 degree",temporal="Daily")
    land=model=="era5_land" or (model=="era5_seamless" and variable in LAND_VARIABLES)
    return dict(product="ERA5-Land" if land else "ERA5",spatial="0.1 degree" if land else "0.25 degree",temporal="Daily from hourly")


def point_providers(stations=False):
    from .climate_products import choices
    if stations:return [STATION_HYBRID,NOAA_ONLY,ERA5_ONLY,GRID_HYBRID,LEGACY_OM,"NASA POWER"]+choices(True)
    return [GRID_HYBRID,ERA5_ONLY,LEGACY_OM,"NASA POWER"]+choices()
