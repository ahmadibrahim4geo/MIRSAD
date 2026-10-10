# 16. Climate Data Sources: Temporal Coverage, Parameters & Archival Specifications

## 1. Executive Overview / نظرة عامة
The **MIRSAD Climate Atlas Generator** supports five distinct, certified climatological data sources across both spatial points and raster grids. This document details the exact temporal coverage (start year to end year), spatial properties, measured physical parameters, and operational capabilities of each data provider.

---

## 2. Master Temporal & Spatial Matrix

| Source Provider | Start Date | End Date | Update Latency | Spatial Nature | Grid / Spatial Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hybrid Climate Engine** *(Default)* | **1901** | **Present** | 2–5 days | Station Points | Ground Instrument + 9 km Fusion |
| **NOAA ISD / GHCN Ground Stations** | **1901** *(1850s)* | **Present** | Real-Time | Station Points | True Station Instrument Mast |
| **NASA POWER Agroclimatology** | **1981-01-01** | **Present** | 2–4 days | Gridded World | $0.5^\circ \times 0.625^\circ$ (~50 × 60 km) |
| **Copernicus Climate Data Store (CDS)** | **1940-01-01** | **Present** | 2–5 days | Gridded World | **$0.10^\circ$ (~9 km to 11 km)** |
| **Open-Meteo ERA5 / ERA5-Land** | **1940-01-01** | **Present** | 2–5 days | Gridded World | **$0.10^\circ$ (~9 km to 11 km)** |

---

## 3. Parameter Availability Comparison Across Sources

| Climatological Indicator | Hybrid Engine (Default) | NOAA ISD Ground | NASA POWER API | Copernicus CDS | Open-Meteo ERA5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Air Temperature (Mean, Max, Min)** | ✅ Observed + Gap-Fill | ✅ True Ground | ✅ MERRA-2 Grid | ✅ ERA5-Land Grid | ✅ ERA5-Land Grid |
| **Dew Point & Relative Humidity** | ✅ Observed + Gap-Fill | ✅ True Ground | ✅ MERRA-2 Grid | ✅ ERA5-Land Grid | ✅ ERA5-Land Grid |
| **Sea Level Pressure (PSL / Isobars)** | ✅ Observed + Gap-Fill | ✅ True Ground | ✅ Modeled PS | ✅ ERA5-Land Grid | ✅ ERA5-Land Grid |
| **Wind Speed (Mean, Max) & Direction** | ✅ Observed + Gap-Fill | ✅ True Ground | ✅ MERRA-2 Grid | ✅ ERA5-Land Grid | ✅ ERA5-Land Grid |
| **Precipitation (Daily, Monthly, Total)** | ✅ Observed + Gap-Fill | ✅ True Ground | ✅ MERRA-2 Corrected | ✅ ERA5-Land Grid | ✅ ERA5-Land Grid |
| **Cloud Cover (Okta / Total Fraction %)** | ✅ Observed + Gap-Fill | ✅ True Ground | ✅ MERRA-2 Grid | ✅ ERA5-Land Grid | ✅ ERA5-Land Grid |
| **Solar Radiation Flux (GHI / DNI)** | ✅ Satellite Synthesis | ❌ Sparse BSRN only | ✅ CERES Gold Standard | ✅ Radiative Model | ✅ Radiative Model |
| **UV Index (Erythemal Exposure)** | ✅ Satellite Synthesis | ❌ Rare | ✅ CERES FLASHFlux | ❌ Model Estimate | ❌ Model Estimate |
| **Land Surface Skin Temp (LST)** | ✅ Satellite Synthesis | ❌ Satellite-only | ✅ MERRA-2 Skin TS | ✅ ERA5 Skin Temp | ✅ ERA5 Skin Temp |
| **Soil Temperature & Moisture (4 Depths)** | Optional | ❌ Not available | ❌ Not available | ✅ 0–255 cm Depths | ✅ 0–255 cm Depths |
| **Reference Evapotranspiration (ET0)** | ✅ Hargreaves & FAO | ✅ Hargreaves Calc | ✅ Hargreaves Calc | ✅ FAO-56 Penman | ✅ FAO-56 Penman |
| **Heat Index & Wind Chill** | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation |
| **Aridity Indices (De Martonne & UNEP)** | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation |
| **Water Deficit & Walter-Lieth Dry Months** | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation | ✅ Physical Equation |
| **Zero-NoData Surface Guarantee** | ✅ **100% Guaranteed** | ⚠️ Subject to gaps | ✅ 100% Gridded | ✅ 100% Gridded | ✅ 100% Gridded |

---

## 4. Source Profiles & Use-Case Guidelines

### 4.1 Hybrid Engine (NOAA Ground + NASA / ERA5 Gap-Filling) [Default]
- **Operational Philosophy:** Uses certified ground station observations as the primary ground truth, while automatically filling any operational missing days from ERA5-Land / NASA POWER, and synthesizing radiative sensors (Solar, UV) seamlessly.
- **When to Use:** Standard production mapping, academic thesis work, master atlas compilation, and any analysis where missing pixels or NoData gaps cannot be tolerated.

### 4.2 NOAA ISD / GHCN Direct Station Ground Observations
- **Operational Philosophy:** 100% pure physical sensor records without numerical model intervention.
- **When to Use:** Formal audits, calibration/validation of satellite algorithms, official meteorological court reports, and long historical studies starting in the early 20th century.

### 4.3 NASA POWER Agroclimatology (MERRA-2 / CERES)
- **Operational Philosophy:** Specialized agro-meteorological reanalysis with world-leading satellite-derived solar irradiance.
- **When to Use:** Solar photovoltaic farm siting, agricultural water demand modeling, crop yield forecasting, and regions lacking ground stations.

### 4.4 Copernicus Climate Data Store (CDS / ERA5 / AgERA5)
- **Operational Philosophy:** Official European C3S / ECMWF reference archive with state-of-the-art 4D-Var data assimilation downscaled to 0.10° (~9 km). Supports optional personal API tokens with seamless zero-auth fallback.
- **When to Use:** Official European/WMO climatological standards, agricultural water modeling, national atlases, and high-resolution environmental assessments from 1940 to present.

### 4.5 Open-Meteo Historical API (ECMWF ERA5 & ERA5-Land)
- **Operational Philosophy:** High-resolution numerical reanalysis with topography-adjusted digital elevation model downscaling.
- **When to Use:** Mountainous regions, steep valleys, microclimatic gradient mapping, soil hydrology, and long historical series from 1940 to 1980.
