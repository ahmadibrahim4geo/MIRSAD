# 03. Processing Pipeline & Geoprocessing Workflow
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. End-to-End Processing Architecture

The processing pipeline executes through a sequence of 13 deterministic, audited stages implemented across `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` and `Toolboxes/raster_atlas_generator.py`:

```
 [Stage 1: User Parameter Ingestion & Spatial Extent Validation]
                          |
                          v
 [Stage 2: Geodetic Fishnet Sampling Point Generation]
                          |
                          v
 [Stage 3: Multi-Point REST API Acquisition & Local Cache Intercept]
                          |
                          v
 [Stage 4: Payload Ingestion & Sentinel Value Scrubbing (-999.0)]
                          |
                          v
 [Stage 5: Primary Temporal Aggregation (Daily to Monthly)]
                          |
                          v
 [Stage 6: Multi-Year Climatological Aggregation (30-Year Normals)]
                          |
                          v
 [Stage 7: Seasonal & Annual Temporal Synthesis (DJF, MAM, JJA, SON)]
                          |
                          v
 [Stage 8: Biometeorological & Agroclimatic Indicator Modeling]
                          |
                          v
 [Stage 9: Long-Term Decadal Trend (OLS) & Baseline Anomaly Analysis]
                          |
                          v
 [Stage 10: Vector Schema Building (FGDB & Shapefile 115 Fields)]
                          |
                          v
 [Stage 11: Geostatistical Surface Interpolation (IDW / Spline / Kriging)]
                          |
                          v
 [Stage 12: Raster Masking, Snapping, and 18-Folder Tree Organization]
                          |
                          v
 [Stage 13: Layer Symbology Application & Excel Dictionary Export]
```

---

## 2. Detailed Technical Breakdown of Pipeline Stages

### Stage 1: User Parameter Ingestion & Spatial Extent Validation
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`getParameterInfo` lines 3800–3950, `execute` lines 4070–4150).
- **Functionality**: Reads target boundary feature class/shapefile, temporal start year (default 1991), end year (default 2020), data provider selection (`NASA POWER` or `Open-Meteo`), interpolation method (`IDW`, `Spline`, `Kriging`), output cell size, and target File Geodatabase workspace.
- **Validation**: Enforces coordinate reference system verification, spatial boundary clipping limits, and date range validity ($End\_Year \ge Start\_Year$).

### Stage 2: Geodetic Fishnet Sampling Point Generation
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (lines 4155–4220).
- **Functionality**: Computes the bounding envelope of the study area in WGS84 (EPSG:4326). Generates a uniform point grid based on the chosen spatial resolution (e.g. $0.1^\circ$, $0.25^\circ$, or $0.5^\circ$). Each point receives a persistent `Source_ID`, geodetic latitude (`Point_Lat`), and longitude (`Point_Lon`).

### Stage 3: Multi-Point REST API Acquisition & Local Cache Intercept
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (lines 4230–4350).
- **Functionality**: Constructs parameterized HTTP GET requests. Incorporates exponential backoff retry logic (up to 5 attempts with delay multipliers: 2s, 4s, 8s, 16s) to handle server-side rate limiting or network timeouts.
- **Cache Intercept**: If an offline cache directory or local GDB point cache is provided, the tool skips the HTTP request and reads cached payloads directly, enabling complete offline execution.

### Stage 4: Payload Ingestion & Sentinel Value Scrubbing
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`is_missing` line 612).
- **Functionality**: Replaces sentinel missing values (`-999.0`, `-99.0`, `-9999.0`, `NaN`, `None`, and `inf`) with null tokens. Enforces physical validity filters (e.g. $RH \in [0, 100]\%$, $Sol \ge 0\text{ kWh/m}^2$, $WS \ge 0\text{ m/s}$, $PS \ge 300\text{ hPa}$).

### Stage 5: Primary Temporal Aggregation (Daily to Monthly)
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`monthly_precip_total_from_rate` line 749, `safe_sum` line 642).
- **Functionality**:
  - For rate parameters (e.g. precipitation $PRECTOTCORR$ in mm/day): Multiplied by calendar days in each specific month ($28, 29, 30, \text{ or } 31$) to yield total monthly rainfall depth in mm.
  - For state variables ($T, RH, PS, PSL, WS$): Computes daily means and accumulates monthly means.
  - For solar radiation: Converts native MJ/m²/day to kWh/m²/day by dividing by 3.6 (`solar_mj_to_kwh` line 755).

### Stage 6: Multi-Year Climatological Aggregation (30-Year Normals)
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`climat_monthly_means` line 700).
- **Functionality**: Computes the 30-year climatological normal for each of the 12 calendar months:
  $$\overline{X}_m = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} X_{y, m} \quad \text{for } m \in \{1, 2, \dots, 12\}$$
  Requires at least 75% valid years (`min_frac=0.75`, e.g. at least 23 years out of 30) for each calendar month.

### Stage 7: Seasonal & Annual Temporal Synthesis
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`seasonal_means_from_monthly` line 709, `seasonal_totals_from_monthly_totals` line 721).
- **Functionality**: Aggregates monthly climatological normals into standard meteorological seasons:
  - Winter (DJF: December, January, February)
  - Spring (MAM: March, April, May)
  - Summer (JJA: June, July, August)
  - Autumn (SON: September, October, November)
  - Circular vector aggregation for wind direction via `circular_mean_deg` (line 663).

### Stage 8: Biometeorological & Agroclimatic Indicator Modeling
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`heat_index_c` line 797, `wetbulb_stull_c` line 840, `wbgt_shade_c` line 858, `windchill_c` line 872, `extraterrestrial_radiation_ra` line 1350, `compute_drought_fields` line 1373).
- **Functionality**: Evaluates complex derived physical models:
  - Rothfusz 9-parameter Heat Index polynomial and Canadian Humidex.
  - Stull (2011) Wet-Bulb Temperature and ISO 7243 Shade WBGT ($0.7 T_w + 0.3 T_a$).
  - Environment Canada / US NWS Wind Chill.
  - De Martonne Aridity Index ($P / (T + 10)$).
  - Hargreaves-Samani (1985) Reference Crop Evapotranspiration ($PET$).
  - UNEP Aridity Index ($P / PET$).
  - Net Climatic Water Deficit ($P - PET$).
  - Bagnouls-Gaussen Dry Months count ($P_m < 2 T_m$).

### Stage 9: Long-Term Decadal Trend & Baseline Anomaly Analysis
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (`_lin_trend_per_decade` line 1185, `_recent_minus_baseline` line 1201).
- **Functionality**: Fits Ordinary Least Squares (OLS) linear regression lines over annual time series to calculate warming rates per decade ($T_{Trend\_Decade}$) and precipitation trends ($R_{Trend\_Decade}$). Computes shifts between the recent decade (2011–2020) and the 30-year WMO normal (1991–2020).

### Stage 10: Vector Schema Building (FGDB & Shapefile)
- **Module**: `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt` (lines 4380–4500).
- **Functionality**: Creates the output File Geodatabase feature classes and/or Shapefiles. Adds up to 270 attribute fields (12 Admin + 258 Climate Indicators including 144 monthly indicators). Applies `SHP_FIELD_MAP` to truncate field names to 10 characters for DBF compatibility while preserving full names and descriptive aliases in the FGDB.

### Stage 11: Geostatistical Surface Interpolation
- **Module**: `Toolboxes/raster_atlas_generator.py` (lines 1736–2650).
- **Functionality**: Reads the vector points and executes spatial interpolation using ArcGIS Spatial Analyst:
  - **IDW (Inverse Distance Weighting)**: Power parameter $p=2$, variable neighborhood.
  - **Spline**: Regularized or Tension spline with weight 0.1.
  - **Ordinary Kriging**: Spherical or Gaussian semivariogram model.

### Stage 12: Raster Masking, Snapping, and 18-Folder Tree Organization
- **Module**: `Toolboxes/raster_atlas_generator.py` (lines 1800–2650).
- **Functionality**: Clips all interpolated surfaces to the study area boundary mask. Snaps cell geometry to a common origin to guarantee identical cell alignment across all 114 annual, seasonal, and monthly mean rasters. Organizes the outputs into 18 standardized directory trees (e.g. `01_Temperature`, `02_Precipitation`, etc.).

### Stage 13: Layer Symbology Application & Dual-Sheet Excel Workbook Export
- **Module**: `Toolboxes/raster_atlas_generator.py` (lines 2660–2750), `generate_excel_dictionary.py`, `generate_master_atlas_excel.py`.
- **Functionality**: Applies pre-authored ArcGIS layer files (`.lyr`) and color ramps (e.g. blue-to-red for temperature, greens-to-blues for rainfall, orange-to-purple for heat stress). Exports dual-sheet element Excel workbooks (`Data` & `Month` sheets) and comprehensive classification guide `Climate_Atlas_Classification_Guide.xlsx` and `Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx`.
