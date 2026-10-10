# NASA POWER Agroclimatology & Solar Energy Reanalysis

## General Information
- **Source Identifier:** `NASA POWER API (Agroclimatology / MERRA-2)`
- **Lead Organization:** National Aeronautics and Space Administration (NASA)
- **Facility:** NASA Langley Research Center (LaRC), Hampton, VA, USA
- **Modeling Center:** NASA Global Modeling and Assimilation Office (GMAO)
- **Primary Numerical Models:**
  - GMAO MERRA-2 (Modern-Era Retrospective analysis for Research and Applications, Version 2)
  - GEOS 5.12.4 FP-IT (Forward Processing for Instrument Teams)
  - CERES FLASHFlux (Clouds and the Earth's Radiant Energy System)

---

## Temporal Coverage Window
| Product / Stream | Start Date | End Date | Notes |
| :--- | :--- | :--- | :--- |
| **Daily & Monthly Meteorology** | **1981-01-01** | **Present** | Full 45+ year continuous reanalysis stream |
| **Surface Solar Radiation** | **1984-01-01** | **Present** | CERES satellite radiometry integrated from 2000 |
| **Hourly Meteorology** | **2001-01-01** | **Present** | High-temporal resolution stream |
| **Climatological Normals** | 1991–2020 | Static Baseline | WMO standard 30-year climatological normal |
| **Data Latency** | — | **2 to 4 Days** | Processing delay for satellite ingest and QC |

---

## What This Source CAN Provide (Capabilities & Strengths)
1. **Solar Energy & Radiation (Global Gold Standard):**
   - `ALLSKY_SFC_SW_DWN`: All-Sky Surface Shortwave Downward Irradiance ($MJ/m^2/\text{day}$ or $kWh/m^2/\text{day}$).
   - `CLRSKY_SFC_SW_DWN`: Clear-Sky Surface Shortwave Irradiance.
   - `ALLSKY_SFC_UVA_DWN` & `ALLSKY_SFC_UVB_DWN`: Direct UV surface exposure and Erythemal UV Index.
2. **Continuous Global Gridded Coverage (Zero Voids):**
   - 100% complete global grid cells ($0.5^\circ \times 0.625^\circ$, ~50 × 60 km), including open oceans and remote deserts without any missing pixels.
3. **Air Temperature & Thermal Dynamics:**
   - Air Temperature at 2m ($T2M$, $T2M_{max}$, $T2M_{min}$, Diurnal Range).
   - Earth Skin Surface Temperature ($TS$ / Land Surface Temperature - LST).
4. **Atmospheric Moisture & Wind Field:**
   - Dew Point ($T2MDEW$) and Relative Humidity ($RH2M$) at 2m.
   - Surface Atmospheric Pressure ($PS$).
   - Wind Speed at multiple mast heights ($2\text{ m}$, $10\text{ m}$, and $50\text{ m}$) and 10m Wind Direction.
5. **Precipitation & Cloud Cover:**
   - Bias-corrected daily precipitation rate ($PRECTOTCORR$, $mm/\text{day}$).
   - Total Cloud Area Fraction ($CLDTOT$, %).

---

## What This Source CANNOT Provide (Limitations & Boundary Constraints)
1. **Cannot Provide Historical Data Prior to 1981:**
   - Daily/monthly records strictly begin on **January 1, 1981**; earlier decades (1901–1980) are unavailable.
2. **Cannot Provide Instantaneous Peak Wind Gusts:**
   - Only provides hourly/daily mean wind velocities; instantaneous anemometer gust spikes ($W_{gst}$) are not cataloged.
3. **Cannot Provide Sea Level Pressure ($PSL$) Directly:**
   - Provides Surface Pressure ($PS$) at model terrain height; does not output hypsometrically reduced Sea Level Pressure (which must be calculated).
4. **Cannot Provide Subsurface Soil Moisture or Soil Temperature Profiles:**
   - Vertical multi-layer soil hydrology ($0\text{--}255\text{ cm}$) is not included in the standard POWER agroclimatology feed.
5. **Cannot Resolve Fine Microtopography in Complex Valleys:**
   - Because grid spacing is ~50 km × 60 km, local microclimatic elevation lapse variations (e.g. sharp mountain ravines or narrow coastal strips) are smoothed out.
6. **Cannot Provide Real-Time Same-Day Operations:**
   - Trailing operational latency of 2 to 4 days behind current real-time.

---

## Directory Contents
- `Data_Source_Profile.txt`: English machine-readable technical profile.
- `Data_Source_Profile_AR.txt`: Arabic machine-readable technical profile.
- `README.md`: This comprehensive English reference manual.
- `README_AR.md`: Complete Arabic technical reference manual.
