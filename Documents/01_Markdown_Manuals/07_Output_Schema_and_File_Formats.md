# 07. Output Schema and File Formats
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Storage Architecture Overview

The Climate Atlas Generator produces multi-tiered geospatial deliverables to support diverse analytical environments:

1. **ESRI File Geodatabase (FGDB)**: Primary repository containing feature classes supporting up to 342 attribute fields (330 Climate Indicators + 12 Admin across 19 modules, or 307 fields in the 18 core modules), full descriptive aliases, and 64-bit floating point precision.
2. **ESRI Shapefile (.shp)**: Legacy vector interoperability layer with 10-character DBF field name truncation enforced via `SHP_FIELD_MAP`.
3. **Floating-Point GeoTIFF / ESRI GRID Rasters**: 114 interpolated continuous surfaces covering annual, seasonal, and monthly mean climatological horizons organized across 18 modular directories.
4. **Excel Data Dictionaries & Master Metadata Tables**: Dual-sheet workbooks (`Data` & `Month`) and human-readable spreadsheets with Arabic/English bilingual documentation.
5. **NetCDF / Spatial Metadata**: CF-1.8 compliant metadata mappings for scientific exchange.

---

## 2. File Geodatabase (FGDB) Schema Specifications

- **Workspace Path**: `.../Climate_Atlas.gdb`
- **Primary Feature Class**: `Climate_Atlas_Points` (and modular element feature classes: `01_Temperature`, `02_Precipitation`, etc.)
- **Geometry Type**: Point (`esriGeometryPoint`)
- **Spatial Reference**: GCS_WGS_1984 (EPSG:4326) or user-specified Projected Coordinate System.
- **Precision**: Double (`esriFieldTypeDouble`, 8-byte IEEE 754 floating point) for all climate indicators.
- **Field Alias Policy**: In the main GDB every field's alias equals the field name itself (English, e.g. alias of `T_Annual_Mean` is `T_Annual_Mean`), so offline reuse and joins never break. Arabic descriptive aliases live only in the companion `<base>_AR.gdb` copy.
- **Rasters are NEVER stored inside the GDB**: all `.tif` surfaces are written to the dedicated element folders on disk (see §4). The GDB holds point feature classes, wind-vector and isobar contour feature classes only.

---

## 3. Shapefile 10-Character Truncation Mapping (`SHP_FIELD_MAP`)

Because the dBASE IV format underlying Shapefiles strictly limits field names to **10 ASCII characters**, the platform implements an immutable, deterministic mapping dictionary:

```python
# Implemented in Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt and Toolboxes/raster_atlas_generator.py
SHP_FIELD_MAP = {
    # Temperature
    "T_Annual_Mean": "T_AnnMean",
    "T_Winter_Mean": "T_WinMean",
    "T_Spring_Mean": "T_SprMean",
    "T_Summer_Mean": "T_SumMean",
    "T_Autumn_Mean": "T_AutMean",
    "T_Annual_Range": "T_AnnRng",
    "T_Max_Summer_Month_Mean": "T_MaxSumMo",
    "T_Min_Winter_Month_Mean": "T_MinWinMo",
    "T_Annual_Max_Mean": "T_MaxMean",
    "T_Annual_Min_Mean": "T_MinMean",
    
    # Precipitation (Standardized)
    "R_Annual_Mean": "R_AnnMean",
    "R_Annual_Range": "R_AnnRng",
    "R_Winter_Mean": "R_WinMean",
    "R_Spring_Mean": "R_SprMean",
    "R_Summer_Mean": "R_SumMean",
    "R_Autumn_Mean": "R_AutMean",
    # Legacy Precipitation Aliases
    "R_Annual_Total": "R_AnnTot",
    "R_Winter_Total": "R_WinTot",
    "R_Spring_Total": "R_SprTot",
    "R_Summer_Total": "R_SumTot",
    "R_Autumn_Total": "R_AutTot",
    
    # Wind
    "W_Spd_Annual_Mean": "WSp_AnMean",
    "W_Dir_Annual_Mean": "WDr_AnMean",
    
    # Agroclimatic & Drought
    "DM_Aridity_Annual": "DM_AridAnn",
    "PET_Hargreaves_Annual": "PET_HarAnn",
    "UNEP_Aridity_Annual": "UNEP_Arid",
    "Water_Deficit_Annual": "WatDefAnn",
    "Dry_Months_Count": "Dry_Months",
    
    # Trends & Anomalies
    "T_Annual_Trend_Decade": "T_AnnTrDec",
    "R_Annual_Trend_Decade": "R_AnnTrDec",
    "T_Annual_Anom": "T_AnnAnom",
    "R_Annual_Anom": "R_AnnAnom",
    "R_Annual_Anom_Pct": "R_AnnAnPct"
}
```

---

## 4. Raster Directory Architecture

The 103 climate rasters are systematically written to 18 subdirectories located in the output folder:

```text
Output_Rasters/
├── 01_Temperature/          (10 GeoTIFFs: T_Annual_Mean.tif, T_Annual_Range.tif, T_Max_Summer_Month_Mean.tif, ...)
├── 02_Precipitation/        (6 GeoTIFFs: R_Annual_Mean.tif, R_Annual_Range.tif, R_Winter_Mean.tif, ...)
├── 03_Sea_Level_Pressure/   (6 GeoTIFFs: PSL_Annual_Mean.tif, PSL_Annual_Range.tif, ...)
├── 04_Surface_Pressure/     (6 GeoTIFFs: PS_Annual_Mean.tif, PS_Annual_Range.tif, ...)
├── 05_Wind/                 (13 GeoTIFFs: W_Spd_Annual_Mean.tif, W_Dir_Annual_Mean.tif, ...)
├── 06_Relative_Humidity/    (6 GeoTIFFs: RH_Annual_Mean.tif, RH_Annual_Range.tif, ...)
├── 07_Dew_Point/            (6 GeoTIFFs: Td_Annual_Mean.tif, Td_Annual_Range.tif, ...)
├── 08_Solar_Radiation/      (7 GeoTIFFs: Sol_Annual_Mean.tif, Sol_Annual_Total.tif, ...)
├── 09_UV_Index/             (7 GeoTIFFs: UV_Annual_Mean.tif, UV_Annual_Range.tif, ...)
├── 10_Cloud_Cover/          (6 GeoTIFFs: Cld_Annual_Mean.tif, Cld_Annual_Range.tif, ...)
├── 11_Heat_Index/           (7 GeoTIFFs: HI_Annual_Mean.tif, HI_Summer_Mean.tif, WBGT_Summer_Mean.tif, ...)
├── 12_Wind_Chill/           (2 GeoTIFFs by default: WC_Winter_Mean.tif, WC_Annual_Mean.tif; +17 with cold-regions opt-in)
├── 13_De_Martonne_Aridity/  (1 GeoTIFF: DM_Aridity_Annual.tif)
├── 14_Evapotranspiration/   (7 GeoTIFFs: PET_Hargreaves_Annual.tif, ET_Annual_Mean.tif, ET_Annual_Range.tif, ...)
├── 15_UNEP_Aridity/         (1 GeoTIFF: UNEP_Aridity_Annual.tif)
├── 16_Water_Deficit/        (1 GeoTIFF: Water_Deficit_Annual.tif)
├── 17_Dry_Months/           (1 GeoTIFF: Dry_Months_Count.tif)
├── 18_Trends_And_Anomalies/ (9 GeoTIFFs: T_Annual_Trend_Decade.tif, R_Annual_Trend_Decade.tif, ...)
└── 19_Land_Surface_Temp/    (11 GeoTIFFs: LST_Annual_Mean.tif, LST_Annual_Range.tif, differences, ...)
```

- **Format**: 32-bit Floating Point GeoTIFF (`.tif`).
- **Compression**: LZW lossless compression.
- **NoData Sentinel**: `-3.4028234663852886e+38` (IEEE 754 32-bit float minimum) or ESRI Grid NoData.
- **Pyramid Layers**: Bilinear interpolation resampling for continuous variables; Nearest Neighbor for integer counts (`Dry_Months_Count`).

### 4.1 Monthly Climatology Subfolder (`Month/`)
When the **Generate Monthly Climatology Rasters (Jan–Dec)** option is enabled (default OFF, requires a multi-year period of ≥ 2 years), each element receives 12 independent monthly surfaces (Wind: 24 — 12 speed `W_Spd_*` + 12 direction `W_Dir_*`) inside a dedicated subfolder so they never mix with annual/seasonal rasters:
```text
01_Temperature/Month/   (T_January_Mean.tif ... T_December_Mean.tif)
05_Wind/Speed/Month/    (W_Spd_January_Mean.tif ... W_Spd_December_Mean.tif)
05_Wind/Direction/Month/(W_Dir_January_Mean.tif ... W_Dir_December_Mean.tif)
```
All 12 rasters of one element share a single unified color stretch (global min/max over the 12 months) for true visual month-to-month comparison. Wind direction uses circular U/V (sin/cos + atan2) interpolation, never linear degrees.

---

## 5. Dual-Sheet Excel Workbooks & Raw Time-Series Archive

### 5.1 Element Workbook Structure (`00_Tables_And_Reports/*.xls`)
Every exported element workbook is generated with two comprehensive worksheets:
1. **Sheet `Data`**: Preserves station identifiers (`Source_ID`, `Point_Lat`, `Point_Lon`), run parameters (`Data_Start`, `Data_End`, `Temporal`, `Interp_Meth`, `Cell_Size`), annual indicators, seasonal indicators (DJF, MAM, JJA, SON), and annual ranges/differences. It NEVER carries the 12 detailed monthly fields (`*_January_Mean` … `*_December_Mean`).
2. **Sheet `Month`**: Contains station identifiers plus all 12 individual climatological monthly indicators (Jan–Dec) — the exclusive home of the detailed monthly means.

### 5.2 Local Raw Time-Series Archive (`Egypt_Monthly_Raw_1996_2025.json`)
The complete 30-year monthly raw time-series downloaded from NASA POWER is preserved as a permanent structured JSON document in `00_Tables_And_Reports\Egypt_Monthly_Raw_1996_2025.json`. This provides:
- Instant offline recalculations without API latency.
- Full provenance and verifiable auditability back to raw CERES and MERRA-2 records.
- Re-usable inputs for downstream hydrological and agroclimatic models.

