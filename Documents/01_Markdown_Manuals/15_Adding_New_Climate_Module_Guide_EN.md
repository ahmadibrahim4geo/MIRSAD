# Methodology Guide for Adding a New Climate Module and Incremental Database Updating
## NASA POWER & Open-Meteo Climate Atlas Generator Architecture

**Author:** Eng. Ahmad Ibrahim  
**Email:** ahmadibrahim.geo@gmail.com  
**Target Environments:** ArcGIS Desktop (ArcMap 10.8) / ArcGIS Pro (2.8+ / 3.x)  
**Last Updated:** October 2026  

---

## 1. Purpose & Scope

This guide establishes a standardized **Standard Operating Procedure (SOP)** for incorporating any new climate indicator or module into the **NASA POWER & Open-Meteo Climate Atlas Generator** ecosystem.

The methodology addresses two complementary operational tracks:
1. **Track 1: Tool Codebase Integration:** Modifying the Python toolbox code, API harvest pipelines, interpolation routines, and field dictionary generators so the tool natively recognizes the new module in all future ArcMap / ArcGIS Pro runs.
2. **Track 2: Incremental Database Updating (Backfill):** Safely augmenting an already processed study database (e.g., Egypt 1996–2025 across 646 grid points) with the new module without re-running preceding modules and without risking corruption or disruption to existing datasets.

---

## 2. Golden Rules & Architectural Principles

> [!IMPORTANT]
> **Rule 1: Strict Staging Environment**  
> Never write directly to production feature classes or overwrite active project tables. Always output initial assets to a dedicated staging directory suffixed with `_STAGING` or `_NEW`. Verification and regression checks must pass completely before manual promotion.

> [!IMPORTANT]
> **Rule 2: Schema & Alias Parity in Geodatabases**  
> - In File Geodatabase Feature Classes: Field names are full English identifiers, and the field alias must match the field name byte-for-byte (`field_alias == field_name`) with 100% parity. Arabic localized aliases are reserved strictly for the optional `_AR.gdb` localized export tool.
> - In Shapefiles: Field names are abbreviated, unique, and strictly $\le 10$ characters, while the alias retains the full English field name.

> [!IMPORTANT]
> **Rule 3: Streamlined Schema & Essential Rasters Policy**  
> - **Retirement of Redundant Indicators:** Indicators that redundantly duplicate annual aggregates (such as `*_Month_Mean`, which is mathematically identical to `*_Annual_Mean` across the 12 months) and seasonal amplitude (`*_Seasonal_Range`) have been retired across all modules. Dedicated bioclimatic extremes (`T_Max_Summer_Month_Mean` and `T_Min_Winter_Month_Mean`) remain strictly preserved.
> - **Essential Surface Rasters:** Raster generation is focused strictly on cartographically meaningful primary surfaces (11 primary rasters for comparative modules: Annual Mean, 4 Seasonal Means, Annual Range, and 5 environmental differences, plus 12 monthly climatological rasters if enabled).
> - **Tabular-Only Monthly Differences:** The 12 monthly differences (such as `LST_minus_T_January` through `December`) exist purely as tabular indicators in the geodatabase and Excel sheets, and are never rasterized to prevent unnecessary data bloat.

> [!IMPORTANT]
> **Rule 4: Standardized Excel Workbook Structure**  
> - **`Data` Sheet**: Contains administrative metadata, Annual indicators, Seasonal indicators (Winter, Spring, Summer, Autumn), Ranges (Annual and Seasonal), and broad differences (Annual and 4 Seasons).
> - **`Month` Sheet**: Contains point identity columns (`OBJECTID`, `Source_ID`, `Point_Lat`, `Point_Lon`), followed by all 12 monthly climatological means (`<Param>_<Month>_Mean`), and all 12 monthly differences (`<Param>_minus_<Ref>_<Month>`).

> [!IMPORTANT]
> **Rule 5: Strict Parameter Count Invariance**  
> The main Python toolbox (`Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt`) must strictly maintain exactly **65 parameters**, and the raster engine (`Toolboxes/raster_atlas_generator.py`) must strictly maintain exactly **33 parameters**. Never alter parameter indices or counts in `ArcToolbox`.

---

## 3. Track 1: Tool Codebase Integration

Adding a new module requires coordinated updates across four core codebase files:

```
NASA POWER Climate Atlas Generator Codebase
├── Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt   (Main toolbox: harvesting, computation, export)
├── Toolboxes/raster_atlas_generator.py                (Raster interpolation & masking engine)
├── generate_excel_dictionary.py             (Field dictionary generator)
└── generate_master_atlas_excel.py           (Classification guide builder)
```

### Step 1.1: Physical Parameter Selection & Meteorological Provenance
Prior to writing code, establish:
1. **Module Name:** e.g., `Land Surface Temperature`.
2. **Folder Index:** Sequential numbering (e.g., Module 19: `19_Land_Surface_Temperature`).
3. **Prefix:** Unique short code (e.g., `LST`).
4. **NASA POWER Parameter:** e.g., `TS` (Earth Skin Temperature, MERRA-2, 0.5° resolution).
5. **Open-Meteo Equivalent:** e.g., `skin_temperature` (ERA5).
6. **Unit & Valid Physical Range:** e.g., `°C` and range `[-30, 75]` for QA gating.

---

### Step 1.2: Main Toolbox Updates (`Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt`)

#### 1. Register Module Dictionaries:
```python
PRIMARY_MODULES_ALL = [
    "Temperature", "Precipitation", ..., "Land Surface Temperature"
]

MODULE_PARAMS = {
    ...
    "Land Surface Temperature": ["TS"],
}

MODULE_FOLDER = {
    ...
    "Land Surface Temperature": "19_Land_Surface_Temperature",
}

MODULE_SHORT = {
    ...
    "Land Surface Temperature": "LST",
}

DEFAULT_UNIT_BY_MODULE = {
    ...
    "Land Surface Temperature": "deg_c",
}

COLOR_RAMPS = {
    ...
    "Land Surface Temperature": "Temperature",
}
```

#### 2. Open-Meteo ERA5 Canonical Mapping:
```python
OM_HOURLY_BY_MODULE = {
    ...
    "Land Surface Temperature": ["skin_temperature"],
}
OM_CANON = {
    ...
    "skin_temperature": "TS",
}
```

#### 3. Define Field Specifications (`_LST_DEFS`):
Define all 37 indicators as tuples:
`(Field_Name, Alias, Type, Width, Precision, Scale, Period, Statistic, Unit, Formula, Description)`:
```python
_LST_DEFS = [
    # 1. Annual Mean
    ("LST_Annual_Mean", "Annual Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Annual", "Mean", "deg_c", "MEAN(TS_monthly)", "Mean annual land surface temperature"),
    # 2-5. 4 Astronomical Seasons
    ("LST_Winter_Mean", "Winter Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Winter", "Mean", "deg_c", "MEAN(TS_Dec, Jan, Feb)", "Mean winter land surface temperature"),
    ("LST_Spring_Mean", "Spring Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Spring", "Mean", "deg_c", "MEAN(TS_Mar, Apr, May)", "Mean spring land surface temperature"),
    ("LST_Summer_Mean", "Summer Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Summer", "Mean", "deg_c", "MEAN(TS_Jun, Jul, Aug)", "Mean summer land surface temperature"),
    ("LST_Autumn_Mean", "Autumn Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Autumn", "Mean", "deg_c", "MEAN(TS_Sep, Oct, Nov)", "Mean autumn land surface temperature"),
    # 6. Thermal Range
    ("LST_Annual_Range", "Annual Range Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Annual", "Range", "deg_c", "MAX(TS_m) - MIN(TS_m)", "Annual range of monthly LST"),
    # 7-11. Surface-to-Air Differences (Annual and 4 Seasons)
    ("LST_minus_T_Annual", "Annual Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Annual", "Mean", "deg_c", "LST_Annual_Mean - T_Annual_Mean", "Surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Winter", "Winter Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Winter", "Mean", "deg_c", "LST_Winter_Mean - T_Winter_Mean", "Winter surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Spring", "Spring Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Spring", "Mean", "deg_c", "LST_Spring_Mean - T_Spring_Mean", "Spring surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Summer", "Summer Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Summer", "Mean", "deg_c", "LST_Summer_Mean - T_Summer_Mean", "Summer surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Autumn", "Autumn Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Autumn", "Mean", "deg_c", "LST_Autumn_Mean - T_Autumn_Mean", "Autumn surface skin temperature minus 2m air temperature"),
    # 12-23. 12 Monthly Climatological Means
    ("LST_January_Mean", "January Mean Land Surface Temperature", "DOUBLE", 8, 8, 2, "January", "Mean", "deg_c", "MEAN(TS_Jan)", "January mean LST"),
    # ... through December ...
    # 24-35. 12 Monthly Surface-to-Air Differences (Tabular in GDB and Excel only)
    ("LST_minus_T_January", "January Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2, "January", "Difference", "deg_c", "LST_Jan - T_Jan", "January surface minus air temperature"),
    # ... through December ...
]

FIELD_DEFS.extend(_LST_DEFS)
MODULE_FIELDS["Land Surface Temperature"] = [f[0] for f in _LST_DEFS]
```

#### 4. Shapefile Short Name Mapping ($\le 10$ characters):
```python
_LST_SHP_MAP = {
    "LST_Annual_Mean": "LST_AnMean",
    "LST_Winter_Mean": "LST_WinMn",
    "LST_Spring_Mean": "LST_SprMn",
    "LST_Summer_Mean": "LST_SumMn",
    "LST_Autumn_Mean": "LST_AutMn",
    "LST_Annual_Range": "LST_AnRng",
    "LST_minus_T_Annual": "LST_mT_Ann",
    "LST_minus_T_Winter": "LST_mT_Win",
    "LST_minus_T_Spring": "LST_mT_Spr",
    "LST_minus_T_Summer": "LST_mT_Sum",
    "LST_minus_T_Autumn": "LST_mT_Aut",
    "LST_January_Mean": "LST_JanMn",
    # ... through December ...
    "LST_minus_T_January": "LST_mT_Jan",
    "LST_minus_T_February": "LST_mT_Feb",
    "LST_minus_T_March": "LST_mT_Mar",
    "LST_minus_T_April": "LST_mT_Apr",
    "LST_minus_T_May": "LST_mT_May",
    "LST_minus_T_June": "LST_mT_Jun",
    "LST_minus_T_July": "LST_mT_Jul",
    "LST_minus_T_August": "LST_mT_Aug",
    "LST_minus_T_September": "LST_mT_Sep",
    "LST_minus_T_October": "LST_mT_Oct",
    "LST_minus_T_November": "LST_mT_Nov",
    "LST_minus_T_December": "LST_mT_Dec",
}
SHP_FIELD_MAP.update(_LST_SHP_MAP)
```

#### 5. Computation Logic in `compute_point_fields`:
```python
if "TS" in params_dict:
    # 1. Monthly means (across 30 years)
    # 2. Annual mean
    # 3. 4 Seasonal means (DJF, MAM, JJA, SON)
    # 4. Thermal range (Annual)
    # 5. Annual and Seasonal differences (LST - T)
    # 6. 12 Monthly differences (LST_m - T_m)
```

#### 6. Physical QA Bounds:
In `_run_qa`:
```python
if "LST_Annual_Mean" in row:
    val = row["LST_Annual_Mean"]
    if val is not None and not (-30.0 <= val <= 75.0):
        warnings.append("LST_Annual_Mean out of plausible range: {}".format(val))
```

---

### Step 1.3: Raster Generator Updates (`Toolboxes/raster_atlas_generator.py`)

1. Register module in `PRIMARY_MODULES_ALL`, `MODULE_FOLDER`, `MODULE_SHORT`, `POWER_PRIMARY_PARAM`, and `COLOR_RAMPS`.
2. Add shapefile mapping in `SHP_FIELD_MAP`.
3. **Register Raster Indicators:** Populate `MODULE_INDICATOR_FIELDS` strictly with the 11 core raster indicators (explicitly excluding monthly differences):
```python
MODULE_INDICATOR_FIELDS = {
    ...
    "Land Surface Temperature": [
        "LST_Annual_Mean",
        "LST_Winter_Mean",
        "LST_Spring_Mean",
        "LST_Summer_Mean",
        "LST_Autumn_Mean",
        "LST_Annual_Range",
        "LST_minus_T_Annual",
        "LST_minus_T_Winter",
        "LST_minus_T_Spring",
        "LST_minus_T_Summer",
        "LST_minus_T_Autumn",
    ],
}
```
4. Define monthly raster base labels:
```python
_MONTHLY_LABEL_BASE["Land Surface Temperature"] = ("LST", "Mean Land Surface Temperature")
```

---

### Step 1.4: Dictionary and Classification Updates

1. **`generate_excel_dictionary.py`:**
   - Add all 35 indicators to `FIELDS_DATA`.
   - Update `MODULES_SUMMARY` (Module 19, field count = 35).
   - Update total field counts: 330 climate indicators + 12 admin = **342 total fields** across **19 modules**.
   - Execute script to rebuild `docs/Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx`.

2. **`generate_master_atlas_excel.py`:**
   - Register module in `MODULE_FOLDER_MAP` and `MODULES_METADATA`:
     ```python
     "19_Land_Surface_Temperature": {
         "ar_title": "درجة حرارة سطح الأرض",
         "en_title": "Land Surface Temperature",
         "unit": "°C",
         "scale_type": "standard",
     }
     ```

---

### Step 1.5: Offline Automated Verification Suite
Run full test suites prior to deployment:
```powershell
python tests/test_power_atlas_108_offline.py
python tests/test_modifications.py
```
All tests must pass at **100% (0 failures)**.

---

## 4. Track 2: Incremental Database Updating (Backfill)

> **Operational Scenario:**  
> A full regional project dataset (`Egypt Climate Data 1996-2025`) exists with:
> - Geodatabase `Climate_Database_From_1996_To_2025.gdb` (containing grid points and modules 01 through 18).
> - Surface rasters from `01_Temperature` to `18_Trends_And_Anomalies`.
> - Master tables and Excel summaries in `00_Tables_And_Reports`.
> 
> **Objective:** Add module `19_Land_Surface_Temperature` conforming to all standards without touching pre-existing layers, with 35 indicators in GDB and Excel, and exactly 11 surface rasters.

---

### Step 2.1: Establish Isolated Staging Directory
Create a dedicated staging folder:
```
C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature_STAGING\
```

---

### Step 2.2: Raw API Data Harvest & Local Caching
Extract point coordinates (Lat, Lon) for all 646 points. Harvest monthly `TS` series (1996–2025) via NASA POWER API, saving raw responses to a persistent local cache file: `00_Tables_And_Reports\Egypt_TS_Raw_Monthly_1996_2025.json`:

```python
url = (
    "https://power.larc.nasa.gov/api/temporal/monthly/point"
    "?parameters=TS&community=AG&longitude={:.4f}&latitude={:.4f}&start=1996&end=2025&format=JSON"
).format(lon, lat)
```

---

### Step 2.3: Climate Indicator Computation & Table Export
Compute all 35 indicators for each point:
1. **12 Monthly Climatological Means:** 30-year average for each month (`LST_January_Mean` .. `LST_December_Mean`).
2. **Annual Mean:** 12-month grand average (`LST_Annual_Mean`).
3. **4 Seasonal Means:**
   - Winter: Mean(Dec, Jan, Feb).
   - Spring: Mean(Mar, Apr, May).
   - Summer: Mean(Jun, Jul, Aug).
   - Autumn: Mean(Sep, Oct, Nov).
4. **Range:**
   - Annual Range = Max(Month) - Min(Month). (Seasonal range retired).
5. **Annual and Seasonal Differences:**
   - `LST_minus_T_Annual` = LST_Annual_Mean - T_Annual_Mean.
   - `LST_minus_T_Winter` = LST_Winter_Mean - T_Winter_Mean.
   - `LST_minus_T_Spring` = LST_Spring_Mean - T_Spring_Mean.
   - `LST_minus_T_Summer` = LST_Summer_Mean - T_Summer_Mean.
   - `LST_minus_T_Autumn` = LST_Autumn_Mean - T_Autumn_Mean.
6. **12 Monthly Differences (Tabular Only):**
   - `LST_minus_T_January` through `LST_minus_T_December` (LST month mean minus 2m air temp month mean).

Export assets to staging:
- **CSV:** `19_Land_Surface_Temperature.csv` (UTF-8 without BOM).
- **Dual-Sheet Excel Workbook:** `19_Land_Surface_Temperature.xls`:
  - **`Data` Sheet** (23 columns): 12 Admin metadata fields + Annual (1), Seasonal (4), Annual Range (1), and 5 general differences.
  - **`Month` Sheet** (28 columns): Point identifiers + 12 monthly means + 12 monthly differences.
- **Synchronized Copies:** Copy `.xls` to `00_Tables_And_Reports\Land_Surface_Temperature.xls` and monthly CSV to `00_Tables_And_Reports\Monthly_Climatology\Land_Surface_Temperature.csv`.
- **GeoJSON:** `19_Land_Surface_Temperature_Grid_Points.geojson`.
- **Shapefile:** `19_Land_Surface_Temperature_Grid_Points.shp` with $\le 10$ character field names for all 35 indicators.

---

### Step 2.4: Geodatabase Feature Class Creation (`ArcPy`)
Execute via Python 2.7 (`C:\Python27\ArcGIS10.8\python.exe`):

1. Create target feature class:
```python
import arcpy

gdb = r"C:\...\Climate_Database_From_1996_To_2025.gdb"
fc_name = "Land_Surface_Temperature"
target_fc = gdb + "\\" + fc_name

arcpy.CreateFeatureclass_management(
    gdb, fc_name, "POINT", spatial_reference=arcpy.SpatialReference(3857)
)
```

2. Add 12 administrative attributes (`OBJECTID`, `Point_ID`, `Point_Lat`, `Point_Lon`, `Elev_m`, `Data_Start`, `Data_End`, `Temporal`, `Interp_Meth`, `Cell_Size`, `Wind_Cell`, `Status`).
3. Add all 35 indicator fields as `DOUBLE` enforcing strict alias parity:
```python
for field_name in LST_INDICATOR_FIELDS:
    arcpy.AddField_management(
        target_fc, field_name, "DOUBLE", field_alias=field_name
    )
```
4. Insert all 646 records via `arcpy.da.InsertCursor`.
5. Automated validation:
```python
count = int(arcpy.GetCount_management(target_fc)[0])
assert count == 646, "Row count mismatch!"
for f in arcpy.ListFields(target_fc):
    if f.type not in ("OID", "Geometry"):
        assert f.name == f.aliasName, "Alias mismatch for field: " + f.name
```

---

### Step 2.5: Surface Raster Interpolation (Spline Tension)
Create target raster directory:
`C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature\`

Interpolate exactly 11 primary surface rasters using Spatial Analyst:
```python
import os
import arcpy
from arcpy.sa import Spline, ExtractByMask

arcpy.CheckOutExtension("Spatial")

ref_raster = r"C:\...\Egypt Climate Data 1996-2025\01_Temperature\T_Annual_Mean.tif"
mask_poly = r"C:\...\Egypt Climate Data 1996-2025\Climate_Database_From_1996_To_2025.gdb\Egypt"

arcpy.env.snapRaster = ref_raster
arcpy.env.cellSize = 250.0
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)
arcpy.env.compression = "LZW"

out_dir = r"C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature"

rasters_to_build = [
    "LST_Annual_Mean",
    "LST_Winter_Mean",
    "LST_Spring_Mean",
    "LST_Summer_Mean",
    "LST_Autumn_Mean",
    "LST_Annual_Range",
    "LST_minus_T_Annual",
    "LST_minus_T_Winter",
    "LST_minus_T_Spring",
    "LST_minus_T_Summer",
    "LST_minus_T_Autumn",
]

for field in rasters_to_build:
    out_tif = os.path.join(out_dir, field + ".tif")
    surf = Spline(target_fc, field, cell_size=250.0, spline_type="TENSION", weight=30.0, n_points=12)
    clipped = ExtractByMask(surf, mask_poly)
    clipped.save(out_tif)
    arcpy.CalculateStatistics_management(out_tif)
    arcpy.BuildPyramids_management(out_tif)
```

> [!WARNING]
> **Definitive Raster Exclusion Policy:**  
> - **Never generate rasters for retired `*_Month_Mean` fields**.
> - **Never generate rasters for the 12 monthly differences**; these exist purely as tabular indicators in the geodatabase and Excel workbooks.

---

### Step 2.6: Classification Guide & Dictionary Synchronization
Rebuild the Master Classification Guide from the 11 generated TIFFs:
```powershell
python generate_master_atlas_excel.py --base_dir "C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025" --study_area "Egypt"
```
**Outcome:**
- Populates sheet `19_Land_Surface_Temperature` in `Climate_Atlas_Classification_Guide.xlsx` with 4 discrete classification schedules (3, 5, 7, and 9 classes).

Synchronize Field Dictionaries:
- Copy `docs\Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx` (342 fields) to project root and `00_Tables_And_Reports\`.

---

## 5. QA/QC Audit Checklist

Prior to signing off on any module addition, verify against this complete audit matrix:

| # | Audit Item | Expected Standard | Verification Method |
|:---:|:---|:---|:---|
| **1** | Main Toolbox Parameters | Strictly 65 parameters | `.pyt` in ArcMap / ArcToolbox |
| **2** | Raster Tool Parameters | Strictly 33 parameters | `Toolboxes/raster_atlas_generator.py` |
| **3** | Feature Class Record Count | 646 rows (matching sample points) | `arcpy.GetCount_management` |
| **4** | Feature Class Field Count | 47 fields (12 admin + 35 indicators) | `arcpy.ListFields` |
| **5** | Alias Parity Verification | `field_name == field_alias` (100%) | `arcpy.ListFields` comparison |
| **6** | Shapefile Field Lengths | All names $\le 10$ chars, unique | `.dbf` field inspection |
| **7** | Module Raster Count | Exactly 11 core `.tif` files | Folder listing of `19_...` |
| **8** | Tabular-Only Exclusion | No retired rasters, No monthly diff rasters | Verify absence in raster directory |
| **9** | Raster Environment Alignment | Snap = T_Annual_Mean, Cell = 250m, Mask = Egypt | ArcMap Raster Properties |
| **10** | Excel Workbook Sheets | `Data` (23 cols) and `Month` (28 cols) | `xlrd` / Excel inspection |
| **11** | Classification Guide Sheet | Sheet `19_Land_Surface_Temperature` populated | `openpyxl` / Excel inspection |
| **12** | Master Dictionary Count | 342 fields across 19 modules (330 climate + 12 admin) | `Climate_Atlas_Fields_Dictionary` |
| **13** | Regression Test Suites | All suites passed (100% pass) | `test_power_atlas_108_offline.py` |

---

## 6. Conclusion

Adhering strictly to this engineering methodology guarantees:
1. Unlimited extensibility for future climate parameters (e.g., Soil Moisture, Actual Evapotranspiration, SPEI Drought Indices).
2. Clean, safe, and reproducible backfilling for existing client databases without jeopardizing completed analytical products.
