# NOAA ISD / GHCN Direct Station Ground Observations Archive

## General Information
- **Source Identifier:** `NOAA ISD / GHCN Direct Station Ground Observations Archive`
- **Lead Organization:** National Oceanic and Atmospheric Administration (NOAA)
- **Data Center:** National Centers for Environmental Information (NCEI), Asheville, NC, USA
- **Cooperating Agency:** World Meteorological Organization (WMO)
- **Primary Data Type:** Direct physical instrumental measurements recorded at terrestrial and marine surface observing stations.

---

## Temporal Coverage Window
| Parameter | Value |
| :--- | :--- |
| **Start Year** | **1901** (Standardized global synoptic archive; selected stations from 1850s) |
| **End Year** | **Present** (Updated continuously in Near-Real-Time via GTS/METAR) |
| **Historical Archive Depth** | Over 125 continuous years of climatological ground truth |
| **Update Latency** | 1 to 3 hours for sub-hourly METAR/SYNOP; Daily at 11:00 UTC for GHCN |

---

## What This Source CAN Provide (Capabilities & Strengths)
1. **100% Pure Physical Ground Truth:**
   - Raw, unmodeled instrument records directly from thermometers, barometers, hygrometers, anemometers, and rain gauges.
2. **Air Temperature & Moisture:**
   - Dry bulb air temperature ($T$, $T_{max}$, $T_{min}$) at standard 2m screen height.
   - Dew point temperature ($T_d$) and psychrometric relative humidity ($RH$).
3. **Barometric Pressure Suite:**
   - Station Pressure ($PS$) measured directly by barometer at ground elevation.
   - Mean Sea Level Pressure ($PSL$) hypsometrically reduced for synoptic isobar analysis.
4. **Wind Field Dynamics:**
   - Wind speed ($W_{spd}$) at 10m mast, compass wind direction ($W_{dir}$ $0^\circ\text{--}360^\circ$), and peak instantaneous wind gusts ($W_{gst}$).
5. **Liquid Precipitation:**
   - Physical tipping-bucket and manual rain gauge accumulation ($mm$), rain day frequencies, and extreme 24-hour storm events.
6. **Cloud State & Weather Phenomena:**
   - Total cloud amount in Oktas ($0\text{--}8$), cloud ceiling base height (ceilometer), and WMO present weather codes (fog, haze, dust storm, thunderstorms, precipitation types).
7. **Official Legal & Forensic Validity:**
   - Certified evidentiary ground truth suitable for formal government records, legal compliance, and forensic climatology audits.

---

## What This Source CANNOT Provide (Limitations & Boundary Constraints)
1. **Cannot Provide Surface Solar Radiation Flux ($W/m^2$):**
   - Standard synoptic weather stations lack pyranometers; Solar irradiance ($GHI$, $DNI$, diffuse) is unavailable except at sparse specialized BSRN/SURFRAD networks.
2. **Cannot Provide Satellite UV Erythemal Index:**
   - UV spectrometers are not part of routine synoptic weather station packages.
3. **Cannot Provide Land Surface Skin Temperature ($LST$):**
   - Ground thermometers measure ambient air temperature at 2m height; they cannot measure the radiometrically emitted skin temperature of the land surface (which requires satellite sensors).
4. **Cannot Provide Subsurface Soil Moisture/Temperature Profiles:**
   - Airport and general synoptic towers do not install vertical soil probes ($0\text{--}255\text{ cm}$).
5. **Cannot Guarantee 100% Unbroken Temporal Continuity:**
   - Physical stations are vulnerable to sensor maintenance downtime, power outages, and communication line breaks, resulting in NoData timestamps (`-999`).
6. **Cannot Provide Continuous Spatial Grid Across Data Voids:**
   - Data exists strictly where physical towers are installed; no data is available across remote deserts, open oceans, or uninstrumented mountain ranges without interpolation.

---

## Directory Contents
- `Data_Source_Profile.txt`: English machine-readable technical profile.
- `Data_Source_Profile_AR.txt`: Arabic machine-readable technical profile.
- `README.md`: This comprehensive English reference manual.
- `README_AR.md`: Complete Arabic technical reference manual.
