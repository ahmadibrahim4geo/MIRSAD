---
name: mirsad-climate-engine
description: >-
  Core scientific geoprocessing rules, climate indices calculations, and data pipeline contracts
  for the MIRSAD Climate Atlas Generator platform. Use whenever implementing or debugging climate
  modules, NASA POWER / Open-Meteo / NOAA ISD ingestion, ETCCDI climate extremes, aridity indices,
  spatial interpolation, or dual ArcMap/Desktop runtimes.
---

# MIRSAD Climate Atlas Engine & Scientific Standards

This skill defines the mathematical definitions, data integrity standards, API contracts, and geoprocessing workflows powering the MIRSAD Climate Atlas platform.

---

## 1. Station Data & Coordinate Integrity Rules

1. **Station Identifiers**:
   - `USAF` (6 digits) alone is NOT unique. A station key must combine `USAF` + `WBAN` + `Location`:
     $$\text{Station Key} = \text{USAF} \mid \text{WBAN} \mid \text{Latitude} \mid \text{Longitude}$$
   - Always preserve identifiers as **strings** with leading zeros intact (e.g. `"062366"`).
2. **Missing Precipitation Rule**:
   - Missing precipitation values MUST NEVER be treated as zero (`0.0`). Missing data must be recorded as null/NaN with coverage percentages tracked.
3. **Coordinates & Datum**:
   - Raw station coordinates are stored in **WGS 84 (EPSG:4326)**.
   - For spatial interpolation (IDW, Kriging), project on-the-fly to a suitable conformal or equal-area projected coordinate system (e.g., UTM Zone or Lambert Conformal Conic).

---

## 2. The 19 Climate Modules & Mathematical Formulas

MIRSAD calculates 19 standard climatological, bioclimatic, and agroclimatic indices:

### Thermal Indices:
- **T_MEAN**: Monthly and Annual Mean Temperature ($^\circ\text{C}$).
- **T_MAX / T_MIN**: Mean Daily Maximum and Minimum Temperatures.
- **DTR (Diurnal Temperature Range)**:
  $$DTR = T_{MAX} - T_{MIN}$$

### Moisture & Precipitation Indices:
- **P_ANNUAL**: Annual Total Precipitation ($\text{mm}$).
- **P_MONTHLY**: Monthly Precipitation Climatological Normals ($1991 - 2020$).

### Bioclimatic & Aridity Indices:
- **De Martonne Aridity Index ($I_{DM}$)**:
  $$I_{DM} = \frac{P}{T + 10}$$
  *Classification*:
  - $I_{DM} < 5$: Hyper-Arid (صحراوي خالي)
  - $5 \le I_{DM} < 10$: Arid (جاف)
  - $10 \le I_{DM} < 20$: Semi-Arid (شبه جاف)
  - $20 \le I_{DM} < 30$: Mediterranean / Sub-Humid (شبه رطب)
  - $I_{DM} \ge 30$: Humid / Per-Humid (رطب إلى رطب جداً)

- **Lang Regenfaktor ($R_L$)**:
  $$R_L = \frac{P}{T}$$

- **Thornthwaite Potential Evapotranspiration (PET) & Moisture Index**:
  Based on monthly heat index ($I$) and empirical temperature functions.

- **Bagnouls-Gaussen Xerothermic Index ($BGI$)**:
  Identifies dry months where $P < 2T$.

### Agroclimatic & Extreme Indices (ETCCDI):
- **GDD (Growing Degree Days)**:
  $$GDD = \sum \max(0, T_{mean} - T_{base}), \quad \text{where } T_{base} = 10^\circ\text{C}$$
- **NOAA Heat Index ($HI$)**:
  Rothfusz multiple regression based on temperature and relative humidity.
- **R10mm / R20mm**: Count of days where daily precipitation $\ge 10\text{mm}$ or $\ge 20\text{mm}$.
- **RX1day / RX5day**: Maximum 1-day and consecutive 5-day precipitation amount ($\text{mm}$).
- **CDD (Consecutive Dry Days)**: Maximum length of dry spell ($P < 1\text{mm}$).

---

## 3. Data Providers Ingestion Pipeline

MIRSAD supports 3 verified data sources:
1. **NASA POWER API (Satellite & Reanalysis)**:
   - Global coverage ($0.5^\circ \times 0.5^\circ$), daily solar radiation, humidity, wind, and temperatures.
   - Endpoint: `https://power.larc.nasa.gov/api/temporal/daily/point`.
2. **Open-Meteo ERA5 Reanalysis**:
   - High-resolution atmospheric reanalysis ($0.1^\circ$ to $0.25^\circ$).
   - Endpoint: `https://archive-api.open-meteo.com/v1/archive`.
3. **NOAA ISD (Integrated Surface Database)**:
   - Direct ground station historical observations.

---

## 4. Multi-Format Output Contract

When geoprocessing completes, outputs must be generated simultaneously:
1. **Excel Workbook (`.xlsx`)**: Formatted multi-sheet workbook with metadata, monthly averages, and QA logs.
2. **GeoPackage (`.gpkg`)**: Open spatial layer with table schema, geometries, and attribute fields.
3. **File Geodatabase (`.gdb`)**: Esri-compatible feature class.
*Rule*: If FileGDB export fails due to environment/license constraints, the GeoPackage and Excel files must be preserved and reported as successful. Never hide a failed FileGDB or fail the whole job prematurely.
