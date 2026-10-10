# Comprehensive Scientific and Technical Guide
# NASA POWER & Open-Meteo Climate Atlas Generator
## Native Dual Compatibility for ArcGIS Pro (Python 3) & ArcMap 10.8 (Python 2.7)

[![Developer](https://img.shields.io/badge/Developer-Ahmad%20Ibrahim-1F4E79.svg?style=for-the-badge&logo=github)](https://github.com/ahmadibrahim4geo)
[![Email](https://img.shields.io/badge/Email-ahmadibrahim.geo%40gmail.com-red.svg)](mailto:ahmadibrahim.geo@gmail.com)
[![Platform](https://img.shields.io/badge/Platform-ArcGIS%20Pro%20%7C%20ArcMap%2010.8-0079c1.svg)](https://www.esri.com/)
[![Repository](https://img.shields.io/badge/Repository-NASA--POWER--Climate--Atlas--Generator-blue.svg)](https://github.com/ahmadibrahim4geo/MIRSAD)

---

## Table of Contents
1. [Overview & Engineering Goals](#1-overview--engineering-goals)
2. [Dual Architecture: ArcGIS Pro & ArcMap 10.8](#2-dual-architecture-arcgis-pro--arcmap-108)
3. [The Dual-Tool Workflow Architecture](#3-the-dual-tool-workflow-architecture)
4. [The 18 Modular Climate Layers & 1:1 Standardized Architecture](#4-the-18-modular-climate-layers--11-standardized-architecture)
5. [Dual Operation Modes & Smart Skip Execution](#5-dual-operation-modes--smart-skip-execution)
   - [A. Online Pipeline (Download & Generate Atlas)](#a-online-pipeline-download--generate-atlas)
   - [B. Offline Pipeline (Interpolate & Map Existing Data)](#b-offline-pipeline-interpolate--map-existing-data)
6. [Spatial Masking Rules & Non-Destructive Principles](#6-spatial-masking-rules--non-destructive-principles)
   - [Station Points Invariance Rule](#station-points-invariance-rule)
   - [Products Strictly Subject to Mask Clipping](#products-strictly-subject-to-mask-clipping)
7. [High-Efficiency Lossless LZW Block Tiling Compression](#7-high-efficiency-lossless-lzw-block-tiling-compression)
8. [Wind Vector Fields & Directional Flow Dynamics](#8-wind-vector-fields--directional-flow-dynamics)
9. [WMO 30-Year Climatological Normals Standards](#9-wmo-30-year-climatological-normals-standards)
10. [Global Bioclimatic & Aridity Models](#10-global-bioclimatic--aridity-models)
11. [Data Quality Control & Gap-Filling Protocols](#11-data-quality-control--gap-filling-protocols)
12. [Data Interoperability & Schema Standards](#12-data-interoperability--schema-standards)
13. [Measurement Units & Active Mathematical Conversions](#13-measurement-units--active-mathematical-conversions)
14. [User Interface Customization & Default Parameters](#14-user-interface-customization--default-parameters)

---

## 1. Overview & Engineering Goals

The **NASA POWER & Open-Meteo Climate Atlas Generator** is an enterprise-grade geoprocessing platform engineered to automate the ingestion, quality assurance, climatological calculations, spatial interpolation, cartographic symbology, and multi-format dissemination of multi-decadal meteorological data.

### Primary Objectives:
1. Eliminate manual barriers to acquiring global historical reanalysis and projection datasets from **NASA POWER** (MERRA-2, CERES) and **Open-Meteo** (ERA5-Land ~9 km).
2. Automate mathematically sound spatial interpolation and climatological normal calculations following **World Meteorological Organization (WMO)** standards.
3. Deliver a robust, modular schema comprising **17 discrete thematic feature classes**.
4. Optimize raster generation pipelines using high-performance, **lossless block-tiled LZW compression** without scientific precision degradation.

---

## 2. Dual Architecture: ArcGIS Pro & ArcMap 10.8

The codebase features a cross-compatible hybrid engine providing seamless operation across both major Esri software generations:

- **ArcGIS Pro (2.x / 3.x) with Python 3.x**:
  - Full Python 3 unicode compliance, avoiding legacy `unicode()` or `str.decode()` exceptions.
  - Safe evaluation of dictionary views (`list(dict.values())`) and modern iterables.
  - Mitigation of intermediate scratch deletion routines (`arcpy.management.Delete`), guaranteeing user layers in the Contents pane / Table of Contents (TOC) remain permanently visible during and after execution.
- **ArcMap 10.8 with Python 2.7**:
  - Full 32-bit ArcObjects / COM backward compatibility.
  - Built-in interactive Tkinter visual calendar modal (`calendar_dialog.py`).
  - Professional Excel reporting (`.xls`) with explicit UTF-8 BOM encoding for uncorrupted Arabic script support.

---

## 3. The Dual-Tool Workflow Architecture

The platform operates via two complementary tools:
1. **`POWER_Climate_Atlas_Generator_10_8.pyt` (Feature Atlas Generator)**:
   - Primary user-facing Geoprocessing Toolbox.
   - Handles API communications, rate-limiting, quality control, calendar GUI interactions, and 96 climatological indicators.
   - Generates the authoritative `Climate_Database.gdb` with 18 structured feature classes.
2. **`raster_atlas_generator.py` (Raster Surface Engine)**:
   - Core backend spatial processing engine.
   - Executes spatial surface interpolation (IDW with smooth power profiles, Ordinary Kriging, Spline with Tension, Natural Neighbor).
   - Manages focal smoothing filters, polygon boundary clipping, isobar contouring, wind vector arrow grids, and lossless LZW compression.

---

## 4. The 18 Modular Climate Layers & 1:1 Standardized Architecture

Outputs are organized via a strict **1:1 unified naming mapping** across UI parameter selection, geodatabase feature classes, and output raster folders:

| # | Feature Class Name | Raster Output Folder | Scientific Description | Indicators | Units |
|:---:|---|---|---|:---:|:---:|
| **01** | `01_Temperature` | `01_Temperature` | Annual/seasonal means (DJF, MAM, JJA, SON), thermal range, summer/winter extremes, diurnal max/min. | 10 | °C |
| **02** | `02_Precipitation` | `02_Precipitation` | Annual total, monthly mean rate, seasonal accumulated sums, annual range, seasonal range. | 8 | mm |
| **03** | `03_Sea_Level_Pressure` | `03_Sea_Level_Pressure` | Atmospheric pressure reduced to mean sea level (MSLP) annual/seasonal means and range. | 6 | hPa / mbar |
| **04** | `04_Surface_Pressure` | `04_Surface_Pressure` | True atmospheric pressure at actual station topographic elevation annual/seasonal means and range. | 6 | hPa / mbar |
| **05** | `05_Wind` | `05_Wind` | 10-meter wind speed means/ranges, circular mean vector wind directions (annual & seasonal). | 13 | m/s, degrees (°) |
| **06** | `06_Relative_Humidity` | `06_Relative_Humidity` | 2-meter relative humidity annual/seasonal means and annual psychrometric range. | 6 | % |
| **07** | `07_Dew_Point` | `07_Dew_Point` | Standalone dew point temperature annual/seasonal means and annual range. | 6 | °C |
| **08** | `08_Solar_Radiation` | `08_Solar_Radiation` | All-sky shortwave downward solar irradiance daily means and accumulated annual totals. | 7 | kWh/m²/day, kWh/m²/year |
| **09** | `09_UV_Index` | `09_UV_Index` | Solar noon all-sky UV radiation index adhering to World Health Organization (WHO) risk scales. | 6 | index (0–15+) |
| **10** | `10_Cloud_Cover` | `10_Cloud_Cover` | Annual and seasonal all-sky cloud fractions and sunshine duration dynamics. | 6 | % |
| **11** | `11_Heat_Index` | `11_Heat_Index` | Steadman-Rothfusz apparent temperature (Heat Index), winter Humidex, and summer shade WBGT. | 5 | °C |
| **12** | `12_Wind_Chill` | `12_Wind_Chill` | Osczevski-Bluestein equivalent wind chill temperature index (winter & annual). | 2 | °C |
| **13** | `13_De_Martonne_Aridity` | `13_De_Martonne_Aridity` | De Martonne aridity index ($I_{DM} = P / (T + 10)$) and bioclimatic classifications. | 1 | dimensionless index |
| **14** | `14_Evapotranspiration` | `14_Evapotranspiration` | FAO-56 Hargreaves-Samani potential evapotranspiration ($ET_o$) with 8 seasonal and annual indicators. | 8 | mm/year, mm/month, mm |
| **15** | `15_UNEP_Aridity` | `15_UNEP_Aridity` | United Nations Environment Programme aridity ratio ($AI = P / ET$) for dryland classification. | 1 | ratio |
| **16** | `16_Water_Deficit` | `16_Water_Deficit` | Annual net climatic water balance ($WD = P - ET$). | 1 | mm/year |
| **17** | `17_Dry_Months` | `17_Dry_Months` | Walter-Lieth biologically dry months count ($P < 2T$). | 1 | months (0–12) |
| **18** | `18_Trends_And_Anomalies` | `18_Trends_And_Anomalies` | Decadal linear climate trends and annual/seasonal anomalies relative to the 1991–2020 normal. | 9 | °C/decade, mm/decade, % |

---

## 5. Dual Operation Modes & Smart Skip Execution

### A. Online Pipeline (`Download & Generate Atlas`)
- Ingests raw station coordinates or point features.
- Connects to NASA POWER or Open-Meteo ERA5-Land APIs.
- Applies QA/QC, gap-fills missing dates, computes all 92 indicators, and creates `Climate_Database.gdb`.

### B. Offline Pipeline (`Interpolate & Map Existing Data`)
- 100% offline workflow without internet dependency.
- **Smart Skip Logic**: If `Climate_Database.gdb` or previously downloaded outputs exist in the project directory, the tool automatically reuses them rather than rebuilding or overwriting from scratch.
- **TOC Integrity**: Eliminates intermediate layer drops, guaranteeing that user layers remain visible in the Table of Contents / Contents pane.
- **Auto-Field Discovery**: Automatically detects present variables and pre-activates corresponding module checklists upon selecting the precalculated layer.

---

## 6. Spatial Masking Rules & Non-Destructive Principles

### Station Points Invariance Rule
- **Point features are NEVER clipped by the study area polygon**.
- Preserving the full input point set maintains geographical context, allows boundary spatial interpolation without edge distortion, and keeps the station database intact for reuse in broader or adjacent studies.

### Products Strictly Subject to Mask Clipping
Polygon mask clipping (`Study_Area_Mask`) is applied exclusively to derived spatial products:
1. **Continuous raster surfaces (GeoTIFFs)**.
2. **Atmospheric pressure isobars (Contours)**.
3. **Directional wind vector arrow grids**.

---

## 7. High-Efficiency Lossless LZW Block Tiling Compression

- Utilizes `arcpy.management.CopyRaster` configured with **LZW compression** and **`128x128` block tiling** (`tileSize="128 128"`).
- Suppresses intermediate pyramid computation overhead (`arcpy.env.pyramid = "NONE"`).
- **Verified Benchmark Results**:
  - **34.8% reduction in raster file size** on disk.
  - **100% Bit-for-Bit Lossless Precision**: Evaluated using numerical matrix differentiation via NumPy; absolute maximum cell divergence is identically zero (`max_diff = 0.000000000000000`). All floating-point decimal precision is completely conserved.

---

## 8. Wind Vector Fields & Directional Flow Dynamics

- Produces continuous wind speed surfaces alongside circular vector mean wind direction surfaces (0–360° azimuth).
- Generates a regularized point grid whose spatial density is controlled via `Wind_Factor_Cell_Size`.
- Samples speed and azimuth values onto grid points, clips the grid to the study mask, and configures directional arrow symbology to depict airflow patterns.
- Vector periods are Annual, Winter, Spring, Summer, Autumn, and Month — all sampled from the annual/seasonal/`Month_Mean` rasters and clipped to the mask. The 12 detailed monthly surfaces (`Month/` folder) are never used as vector sources.
- PSL/PS isobar contours are likewise derived from the Annual/Seasonal/`Month_Mean` pressure rasters and clipped to the mask.

---

## 8b. Seasonal Range and Monthly Climatology Rasters

- Every mean-type element carries `*_Seasonal_Range` (max seasonal mean minus min seasonal mean), computed, stored and interpolated exactly like the annual indicators.
- **Generate Monthly Climatology Rasters (Jan–Dec)** (`GPBoolean`, default OFF, after Temporal Scope): adds the 12 `*_January_Mean … *_December_Mean` fields (Wind: 24) to points/tables/Excel and interpolates one raster per month into each element's `Month/` subfolder with the same method, cell size and mask. Requires a period of ≥ 2 years; all 12 rasters of one element share a unified color stretch.
- **Monthly Ranges - Interannual Variability per Month** (`GPBoolean`, default OFF, independent toggle): adds `<Prefix>_<Month>_Range` fields (e.g. `ET_December_Range`) measuring max−min of each calendar month across years for the mean-type modules. Carried by the Month sheet and `Month/` rasters like the monthly means, even when monthly-means rasters are off.
- **Heat Index Monthly Means (Opt-in Suite)** (`GPBoolean`, default OFF, independent toggle): publishes the 12 monthly Rothfusz heat-index means (`HI_January_Mean` … `HI_December_Mean`) alongside the 8 base Heat Index fields. Winter caveat: monthly values use Rothfusz year-round (= air T below 26.7 °C); only the seasonal `HI_Winter_Mean` uses Humidex. Carried by the Month sheet and `Month/` rasters like the other monthly means.
- **Save Daily Time Series (Daily sheet)** (`GPBoolean`, default OFF): when Temporal is Daily, adds a third `Daily` sheet (OBJECTID, Source_ID, Date, values) to each element workbook; the Month sheet is always kept. Opt-in for short periods / few points; beyond ~60000 rows a `<Element>_daily.csv` is written instead (`.xls` capacity).
- **Wind Chill Full Suite for Cold Regions** (`GPBoolean`, default OFF): publishes `WC_Spring/Summer/Autumn_Mean`, `WC_Annual/Seasonal_Range` and the 12 monthly WC means in addition to `WC_Winter_Mean`/`WC_Annual_Mean`. Needed only where months fall below the 10 °C threshold (Patagonia, Iceland, high mountains, Canada); warm regions keep the clean 2-field schema. Same NWS equation/threshold.
- Field aliases in the main GDB equal the field names; no raster is ever written inside the GDB.

---

## 9. WMO 30-Year Climatological Normals Standards

- The tool aligns with **WMO-No. 1203** standards specifying 30-year consecutive averaging periods to eliminate decadal climate noise.
- Current global baseline: **1991–2020**.
- Meteorological seasons:
  - **Winter (DJF)**: December, January, February
  - **Spring (MAM)**: March, April, May
  - **Summer (JJA)**: June, July, August
  - **Autumn (SON)**: September, October, November

---

## 10. Global Bioclimatic & Aridity Models

- **De Martonne Aridity Index**: $I_{DM} = P / (T + 10)$
- **FAO-56 Hargreaves-Samani PET**: $PET = 0.0023 \cdot R_a \cdot (T_{mean} + 17.8) \cdot \sqrt{T_{max} - T_{min}}$
- **UNEP Aridity Ratio**: $AI = P / PET$
- **Climatic Water Deficit**: $WD = P - PET$
- **Biologically Dry Months (Walter-Lieth)**: $P_{month} < 2 \cdot T_{month}$

---

## 11. Data Quality Control & Gap-Filling Protocols

- Translates NASA `-999.0` missing values to `None / Null`.
- Imputation methods: Climatological month mean, linear boundary interpolation, and spatial nearest neighbor fallback.

---

## 12. Data Interoperability & Schema Standards

- **Geodatabase (`Climate_Database.gdb`)**: 17 clean feature classes with sequential, gap-free `OBJECTID` indexing and zero orphaned export fields.
- **Shapefiles (`.shp`)**: Optional clean export with 10-character field truncation.
- **Arabic Database (`Climate_Database_AR.gdb`)**: Features Arabic field aliases while preserving English physical names for offline pipeline reusability.
- **Excel Master Workbook**: Professionally styled workbooks with UTF-8 BOM encoding.
- **Authoritative Data Dictionary**: Referenced in `Fields_AR_EN_Units.xlsx`.

---

## 13. Measurement Units & Active Mathematical Conversions

The platform incorporates comprehensive measurement unit options across physical domains, converting data values directly at calculation time:

| Domain | Supported Measurement Units | Conversion Multiplier / Formula | Default Standard |
|---|---|---|---|
| **Temperature** | Celsius (`°C`), Fahrenheit (`°F`), Kelvin (`K`) | Absolute: $T_F = T_C \times 1.8 + 32$, $T_K = T_C + 273.15$<br>Deltas/Ranges: $\Delta T_F = \Delta T_C \times 1.8$, $\Delta T_K = \Delta T_C$ | `Celsius (°C) [Default]` |
| **Precipitation** | Millimeters (`mm`), Inches (`in`) | $P_{in} = P_{mm} / 25.4$<br>*(Percentage anomalies & count of dry months preserved)* | `Millimeters (mm) [Default]` |
| **Pressure** | Hectopascals (`hPa`), Millibars (`mbar`), Inches of Mercury (`inHg`), Kilopascals (`kPa`) | $P_{inHg} = P_{hPa} \times 0.029530$, $P_{kPa} = P_{hPa} / 10.0$ | `Hectopascals (hPa) [Default]` |
| **Wind Speed** | Meters per second (`m/s`), Kilometers per hour (`km/h`), Knots (`kt`), Miles per hour (`mph`) | $W_{km/h} = W_{m/s} \times 3.6$, $W_{kt} = W_{m/s} \times 1.94384$, $W_{mph} = W_{m/s} \times 2.23694$<br>*(Vector direction azimuth degrees 0–360° preserved)* | `Meters per second (m/s) [Default]` |
| **Solar Radiation** | Kilowatt-hours per square meter per day (`kWh/m²/day`), Megajoules per square meter per day (`MJ/m²/day`), Watt-hours per square meter per day (`Wh/m²/day`), Calories per square centimeter per day (`cal/cm²/day` / Langley) | $S_{MJ} = S_{kWh} \times 3.6$, $S_{Wh} = S_{kWh} \times 1000.0$, $S_{cal} = S_{kWh} \times 85.9845$ | `Kilowatt-hours per square meter per day (kWh/m2/day) [Default]` |

> [!IMPORTANT]
> **Active Mathematical Conversion Across All Products:**  
> The user-selected measurement units are actively evaluated during statistical calculation and strictly reflected across all output products: Feature Class attribute tables in `Climate_Database.gdb`, Shapefile `.dbf` exports, Excel Master workbooks (`.xls`), and continuous spatial interpolation raster surfaces (`.tif`).

---

## 14. User Interface Customization & Default Parameters

To ensure a seamless, user-centric GIS experience:
- **No Premature Dialog Errors on Open:** All required parameters natively use standard green asterisks without displaying premature red "X" error badges on dialog launch before the user interacts with the tool.
- **Dynamic Study Area Naming:** The `Study Area Name` parameter is left blank (`None`) by default. Users freely input their region name; if omitted, the tool dynamically defaults to the boundary mask polygon layer name or `Study_Area`.
- **Unconstrained Module Selection:** The `Climate Modules & Models` and `Variables Selection (Checklist)` parameters default to unselected (`None`), granting users complete autonomy to select the exact parameters and models desired.
- **100% Pure English Interface:** All parameter titles, categories, tool descriptions, and dropdown selection menus strictly follow standard English nomenclature, completely eliminating mixed-language strings in the tool interface.

