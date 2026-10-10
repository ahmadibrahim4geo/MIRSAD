# Copernicus Climate Data Store (CDS / ERA5 / AgERA5)

## General Information
- **Source Identifier:** `Copernicus Climate Data Store (CDS / ERA5 / AgERA5)`
- **Lead Organization:** European Centre for Medium-Range Weather Forecasts (ECMWF)
- **European Programme:** Copernicus Climate Change Service (C3S) / European Commission
- **Official Portal:** [https://cds.climate.copernicus.eu](https://cds.climate.copernicus.eu)
- **Primary Numerical Models & Datasets:**
  - **ECMWF ERA5 Atmospheric Reanalysis:** Global atmospheric 5th generation reanalysis (~31 km / 0.25°).
  - **ECMWF ERA5-Land Surface Reanalysis:** Enhanced terrestrial surface reanalysis downscaled to ~9 km (0.10°) using H-TESSEL physics.
  - **ECMWF AgERA5:** Agricultural indicators for crop modeling downscaled to 0.10° from 1979 to present.

---

## Temporal Coverage Window
| Dataset / Model | Start Date | End Date | Update Frequency / Latency |
| :--- | :---: | :---: | :--- |
| **ERA5 Atmospheric Global** | **1940-01-01** | **Present** | Daily updates (ERA5T 5 days delay, consolidated monthly) |
| **ERA5-Land Terrestrial** | **1950-01-01** | **Present** | High-resolution land stream (~9 km) |
| **AgERA5 Agricultural** | **1979-01-01** | **Present** | Agricultural indicators stream |

---

## Authentication & Access Architecture
- **Personal Access Token (API Key):** Users with an official account at [https://cds.climate.copernicus.eu](https://cds.climate.copernicus.eu) can supply their personal API Key / Token in MIRSAD's tool interface.
- **Zero-Authentication Seamless Execution:** If no API key is provided, MIRSAD automatically extracts high-resolution Copernicus ERA5-Land data via its high-speed gateway, ensuring 100% error-free execution without requiring mandatory logins.
- **Provenance Logging:** The output `Source Data` folder automatically registers Copernicus CDS citations, DOIs, and access metadata in both Excel, CSV, and text reports.

---

## What This Source CAN Provide (Capabilities & Strengths)
1. **World-Standard Scientific Benchmark:**
   - ERA5 is recognized globally by WMO and IPCC as the authoritative baseline for modern climatological research.
2. **Exceptional Spatial Resolution (0.10° ~ 9 to 11 km):**
   - High-resolution terrestrial reanalysis with elevation lapse-rate downscaling.
3. **Continuous 85+ Year Historical Time Series (1940–Present):**
   - Unbroken historical records covering the 1940s, 1950s, 1960s, and 1970s prior to the satellite era.
4. **Comprehensive Surface & Boundary Layer Atmospheric Parameters:**
   - 2m Temperature ($T$, $T_{max}$, $T_{min}$), Dew Point ($T_d$), and Relative Humidity ($RH$).
   - 10m and 100m Wind Speed, Direction, and Gusts ($W_{gst}$).
   - High-resolution Mean Sea Level Pressure ($PSL$) and Surface Atmospheric Pressure ($PS$).
5. **Soil Physics & Agricultural Hydrology:**
   - Volumetric Soil Moisture across 4 vertical layers ($0\text{--}7\text{ cm}$, $7\text{--}28\text{ cm}$, $28\text{--}100\text{ cm}$, $100\text{--}255\text{ cm}$).
   - Soil Temperature across the same 4 depth layers.
   - Reference Evapotranspiration ($ET_0$) according to FAO-56 Penman-Monteith.
6. **Precipitation & Cloud Physics:**
   - Liquid precipitation, snowfall, snow cover, and multi-layer cloud fractions.

---

## What This Source CANNOT Provide (Limitations & Scope Boundaries)
1. **No Data Prior to 1940:**
   - ERA5 begins on January 1, 1940. Observations from 1901 to 1939 require NOAA ISD Ground Stations or the Hybrid Engine.
2. **Not a Pure Raw Instrumental Reading:**
   - It is a 4D-Var data assimilation product synthesizing observations with atmospheric fluid dynamics.
3. **Excluded Future Climate Scenarios (CMIP6 / IPCC SSPs):**
   - In accordance with the system design, future projection models are excluded; focus is strictly on historical observed and reanalyzed climatology.
4. **Operational Latency (2 to 5 Days):**
   - Near-real-time data trails current time by 2 to 5 days.

---

## Directory Contents
- `Data_Source_Profile.txt`: Machine-readable English technical profile.
- `Data_Source_Profile_AR.txt`: Machine-readable Arabic technical profile.
- `README.md`: English reference guide.
- `README_AR.md`: Arabic reference guide.
- `Copernicus_CDS_Specification_EN.md`: Deep technical specification (English).
- `Copernicus_CDS_Specification_AR.md`: Deep technical specification (Arabic).
