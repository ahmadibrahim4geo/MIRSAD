# Open-Meteo Historical Weather API (ECMWF ERA5 & ERA5-Land Reanalysis)

## General Information
- **Source Identifier:** `Open-Meteo Historical API (ERA5 Reanalysis - High-Resolution)`
- **Lead Organization:** Open-Meteo Weather API
- **Foundational Modeling Agency:** European Centre for Medium-Range Weather Forecasts (ECMWF)
- **European Programme:** Copernicus Climate Change Service (C3S)
- **Primary Numerical Models:**
  - ECMWF ERA5 Global Fifth Generation Atmospheric Reanalysis
  - ECMWF ERA5-Land High-Resolution Terrestrial Surface Reanalysis (H-TESSEL Land Surface Scheme)

---

## Temporal Coverage Window
| Reanalysis Model | Start Date | End Date | Notes |
| :--- | :--- | :--- | :--- |
| **ERA5 Global Atmospheric** | **1940-01-01** | **Present** | Over 85 continuous years of atmospheric history |
| **ERA5-Land Terrestrial Surface** | **1950-01-01** | **Present** | High-resolution land reanalysis stream |
| **Data Latency** | — | **2 to 5 Days** | Finalized ERA5 data stream delay (provisional ERA5T in 5 days) |

---

## What This Source CAN Provide (Capabilities & Strengths)
1. **Exceptional Spatial Resolution (0.10° ~ 9 to 11 km):**
   - The finest publicly accessible multi-decade global terrestrial reanalysis (ERA5-Land).
   - Features precise lapse-rate elevation correction downscaled to digital elevation models (DEM), capturing mountain microclimates.
2. **Deep Continuous Historical Archive (1940–Present):**
   - Spans over 85 continuous years without temporal gaps, covering key mid-20th century decades.
3. **Comprehensive Thermal & Wind Fields:**
   - 2m Air Temperature ($T$, $T_{max}$, $T_{min}$) and Apparent / Feels-Like Temperature.
   - Wind speed at 10m and 100m (wind turbine hub height), 10m wind direction, and 10m wind gusts ($W_{gst}$).
4. **Moisture & Hypsometric Pressure:**
   - 2m Dew Point and Relative Humidity.
   - Surface Atmospheric Pressure and Mean Sea Level Pressure ($PSL$).
5. **Multi-Layer Soil Hydrology (Unique Capability):**
   - Volumetric Soil Moisture at 4 depths ($0\text{--}7\text{ cm}$, $7\text{--}28\text{ cm}$, $28\text{--}100\text{ cm}$, $100\text{--}255\text{ cm}$).
   - Soil Temperature at the same 4 vertical depth layers.
   - Standard Reference Evapotranspiration ($ET_0$ according to FAO-56 Penman-Monteith).
6. **Precipitation & Cloud Layers:**
   - Total liquid equivalent precipitation, rain, snowfall, and snow depth.
   - Multi-layer cloud cover (Low, Mid, High, and Total Cloud fractions).

---

## What This Source CANNOT Provide (Limitations & Boundary Constraints)
1. **Cannot Provide Historical Data Prior to 1940:**
   - ERA5 begins on **January 1, 1940** (and ERA5-Land begins on January 1, 1950); the early 20th century (1901–1939) is unavailable.
2. **Cannot Provide Direct Satellite UV Index (Erythemal Exposure):**
   - Does not carry dedicated satellite spectrophotometer UV instruments (such as NASA CERES FLASHFlux); UV is modeled or estimated.
3. **Cannot Replace Direct In-Situ Instrumental Ground Truth:**
   - It is a numerical model assimilation product; it reflects mathematical reanalysis physics rather than an unadjusted glass thermometer or tipping-bucket gauge on the ground.
4. **Cannot Provide Real-Time Same-Day Weather:**
   - Trailing operational latency of 2 to 5 days for data quality consolidation.

---

## Directory Contents
- `Data_Source_Profile.txt`: English machine-readable technical profile.
- `Data_Source_Profile_AR.txt`: Arabic machine-readable technical profile.
- `README.md`: This comprehensive English reference manual.
- `README_AR.md`: Complete Arabic technical reference manual.
