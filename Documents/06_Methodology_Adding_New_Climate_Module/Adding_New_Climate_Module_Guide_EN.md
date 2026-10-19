# 06. Methodology Guide for Adding a New Climate Module and Incremental Database Updating

> **Development update — 17 October 2026:** This legacy toolbox guide includes historical counts and assumptions. Read the [MIRSAD Desktop methodology review](../../MIRSAD%20Desktop/docs/reports/METHODOLOGY_REVIEW.md) before new development. Verify parameter counts from code; direct Hybrid/NOAA downloads are not implemented, and Excel is the normal tabular export. ArcPy examples remain references for the legacy workflow.
## MIRSAD (مِرصاد) — Climate Atlas & Meteorological Database Platform
### Multi-source Integrated Reanalysis & Surface Atlas Database — SOP Architecture Manual

**Platform:** **MIRSAD (مِرصاد)**  
**Author:** Eng. Ahmad Ibrahim — GIS & Climatology Specialist  
**Email:** ahmadibrahim.geo@gmail.com  
**Target Environments:** ArcGIS Desktop (ArcMap 10.8, Python 2.7) / ArcGIS Pro (2.8+ / 3.x, Python 3)  
**Last Updated:** October 2026 (Unified Enterprise Edition 2.0)  

---

## 1. Purpose & Scope

This guide establishes an enterprise-grade **Standard Operating Procedure (SOP)** for incorporating any new climate indicator or biophysical module into the **MIRSAD (مِرصاد)** — *Multi-source Integrated Reanalysis & Surface Atlas Database* ecosystem.

The **MIRSAD** platform operates on a multi-tier climatological data architecture integrating four authoritative data tiers:
1. **Certified In-Situ Ground Weather Stations:** 28,095 observational stations worldwide from NOAA ISD and WMO networks.
2. **High-Resolution Numerical Reanalysis:** ECMWF ERA5-Land (~9 km native resolution via Open-Meteo API).
3. **Global Satellite & Atmospheric Reanalyses:** NASA POWER MERRA-2 (~50 km) and CERES SYN1deg solar radiation (~100 km).
4. **Intelligent Hybrid Engine:** Observational ground-truth harmonized with automated spaceborne and numerical reanalysis gap-filling.

The methodology addresses two complementary operational tracks:
* **Track 1: Tool Codebase Integration:** Modifying the Python toolboxes, API harvest pipelines, interpolation routines, field dictionary generators, and the `Source Data` provenance engine so the tool natively recognizes the new module in all future ArcMap / ArcGIS Pro runs.
* **Track 2: Incremental Database Updating (Backfill):** Safely augmenting an already processed study database (e.g., Egypt 1996–2025 across 646 grid points, or Arab League national station networks) with the new module without re-running preceding modules and without risking corruption or disruption to existing datasets.

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
> - **`Data` Sheet**: Contains administrative metadata, Annual indicators, Seasonal indicators (Winter, Spring, Summer, Autumn), Annual Range, and broad environmental differences (Annual and 4 Seasons).
> - **`Month` Sheet**: Contains point identity columns (`OBJECTID`, `Source_ID`, `Point_Lat`, `Point_Lon`), followed by all 12 monthly climatological means (`<Param>_<Month>_Mean`), and all 12 monthly differences (`<Param>_minus_<Ref>_<Month>`).
> - **`Source_Data` Sheet**: Documents the meteorological origin, host provider, satellite/reanalysis numerical model, spatial resolution, and temporal coverage.

> [!IMPORTANT]
> **Rule 5: Strict Parameter Count Invariance**  
> The main Python toolbox (`Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt`) must strictly maintain exactly **65 parameters**, and the raster engine (`Toolboxes/raster_atlas_generator.py`) must strictly maintain exactly **33 parameters**. Never alter parameter indices or counts in `ArcToolbox`.

> [!IMPORTANT]
> **Rule 6: Mandatory Source Data Provenance Tracking**  
> Every new module must be registered in `get_element_source_metadata(element_name, provider)` across both tool engines. This ensures automatic compilation of the `Source Data/` folder, `Climate_Data_Sources_Provenance.xls`, `.csv`, and bilingual README documents.

> [!IMPORTANT]
> **Rule 7: Sovereign & Geopolitical Standardization**  
> When dealing with ground weather stations or national administrative layers, all stations located in historical Palestine must be strictly grouped under Country Code `PS`, with country names `Palestine` and `دولة فلسطين`, and fully integrated into the Arab League regional aggregate filter (22 sovereign nations).

---

## 3. Track 1: Tool Codebase Integration

Adding a new module requires coordinated updates across the core MIRSAD codebase files:

```
MIRSAD Platform Codebase
├── Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt   (Primary toolbox: harvesting, computation, GDB/Excel export)
├── Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt (Ground stations: harvesting, filtering, atlas generation)
├── Toolboxes/raster_atlas_generator.py                (Raster engine: IDW/Kriging/Spline interpolation, clipping)
├── generate_excel_dictionary.py             (Master field dictionary generator)
└── generate_master_atlas_excel.py           (Classification guide builder & raster symbology)
```

### Step 1.1: Physical Parameter Selection & Meteorological Provenance
Prior to writing code, establish:
1. **Module Name:** e.g., `Land Surface Temperature`.
2. **Folder Index:** Sequential numbering (e.g., Module 19: `19_Land_Surface_Temperature`).
3. **Prefix:** Unique short code (e.g., `LST`).
4. **NASA POWER Parameter:** e.g., `TS` (Earth Skin Temperature, MERRA-2, 0.5° resolution).
5. **Open-Meteo Equivalent:** e.g., `skin_temperature` (ERA5-Land, ~9 km resolution).
6. **Ground Observation Equivalent:** NOAA ISD / WMO variable mapping (if surface sensor observations exist).
7. **Hybrid Hierarchy:** Priority chain for multi-source resolution (In-Situ ground truth -> ERA5-Land -> MERRA-2).
8. **Unit & Valid Physical Range:** e.g., `°C` and range `[-30, 75]` for QA gating.

---

### Step 1.2: Main Toolbox Updates (`Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt`)

#### 1. Register Module Dictionaries:
```python
PRIMARY_MODULES_ALL = [
    "Temperature", "Precipitation", "Sea Level Pressure", "Surface Pressure",
    "Wind", "Relative Humidity", "Dew Point", "Solar Radiation",
    "UV Index", "Cloud Cover", "Land Surface Temperature"
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
    "Land Surface Temperature": "Temperature",  # Or customized color ramp
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

#### 3. Register Source Provenance Metadata in `get_element_source_metadata`:
```python
def get_element_source_metadata(element_name, provider=None):
    ...
    meta_db["Land Surface Temperature"] = {
        "source_name": "NASA POWER / Open-Meteo ERA5-Land",
        "primary_source": "NASA Langley Research Center & ECMWF",
        "models": "MERRA-2 Skin Temp & ECMWF ERA5-Land (Skin Temperature)",
        "spatial_res": "0.5° x 0.5° (NASA) / 0.1° (~9 km, ERA5)",
        "temporal_range": "1981-Present (NASA) / 1950-Present (ERA5)",
        "temporal_coverage_ar": "من 1981 حتى الوقت الحاضر (NASA) / من 1950 حتى الحاضر (ERA5)",
        "description": "Land surface skin temperature derived from thermal infrared satellite sensors and high-resolution assimilation."
    }
```

#### 4. Define Field Specifications (`_LST_DEFS`):
Define all 35 indicators as tuples:
`(Field_Name, Alias, Type, Width, Precision, Scale, Period, Statistic, Unit, Formula, Description)`:
```python
_LST_DEFS = [
    # 1. Annual Mean
    ("LST_Annual_Mean", "Annual Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Annual", "Mean", "deg_c", "MEAN(TS_monthly)", "Mean annual land surface temperature"),
    # 2-5. Four Seasons
    ("LST_Winter_Mean", "Winter Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Winter", "Mean", "deg_c", "MEAN(TS_Dec, Jan, Feb)", "Mean winter land surface temperature"),
    ("LST_Spring_Mean", "Spring Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Spring", "Mean", "deg_c", "MEAN(TS_Mar, Apr, May)", "Mean spring land surface temperature"),
    ("LST_Summer_Mean", "Summer Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Summer", "Mean", "deg_c", "MEAN(TS_Jun, Jul, Aug)", "Mean summer land surface temperature"),
    ("LST_Autumn_Mean", "Autumn Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Autumn", "Mean", "deg_c", "MEAN(TS_Sep, Oct, Nov)", "Mean autumn land surface temperature"),
    # 6. Annual Range
    ("LST_Annual_Range", "Annual Range Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Annual", "Range", "deg_c", "MAX(TS_m) - MIN(TS_m)", "Annual range of monthly LST"),
    # 7-11. Environmental Differences (Annual & 4 Seasons)
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
    # 12-23. Twelve Monthly Climatological Means
    ("LST_January_Mean", "January Mean Land Surface Temperature", "DOUBLE", 8, 8, 2, "January", "Mean", "deg_c", "MEAN(TS_Jan)", "January mean LST"),
    # ... through December ...
    # 24-35. Twelve Monthly Differences (Tabular-only in GDB and Excel)
    ("LST_minus_T_January", "January Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2, "January", "Difference", "deg_c", "LST_Jan - T_Jan", "January surface minus air temperature"),
    # ... through December ...
]

FIELD_DEFS.extend(_LST_DEFS)
MODULE_FIELDS["Land Surface Temperature"] = [f[0] for f in _LST_DEFS]
```

#### 5. Shapefile Column Map Definition ($\le 10$ Characters):
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

#### 6. Calculation Logic in `compute_point_fields`:
```python
if "TS" in params_dict:
    # 1. 12 Monthly climatological means across all years (LST_m)
    # 2. Arithmetic Annual Mean
    # 3. Four climatological seasons (DJF, MAM, JJA, SON)
    # 4. Annual thermal range
    # 5. Annual and seasonal environmental air-surface temperature offsets (LST - T)
    # 6. 12 monthly air-surface temperature differences (LST_m - T_m)
```

#### 7. Scientific Quality Assurance Gating:
In `_run_qa`:
```python
if "LST_Annual_Mean" in row:
    val = row["LST_Annual_Mean"]
    if val is not None and not (-30.0 <= val <= 75.0):
        warnings.append("LST_Annual_Mean out of plausible range: {}".format(val))
```

---

### Step 1.3: Raster Engine Updates (`Toolboxes/raster_atlas_generator.py`)

1. Register module in core registries (`PRIMARY_MODULES_ALL`, `MODULE_FOLDER`, `MODULE_SHORT`, `POWER_PRIMARY_PARAM`, `COLOR_RAMPS`).
2. Add module entry to `get_element_source_metadata`.
3. Register shapefile field aliases in `SHP_FIELD_MAP`.
4. **Register Essential Surfaces Only:** Configure `MODULE_INDICATOR_FIELDS` with the 11 essential rasters only (strictly excluding monthly differences):
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
5. Register monthly climatology labels:
```python
_MONTHLY_LABEL_BASE["Land Surface Temperature"] = ("LST", "Mean Land Surface Temperature")
```

---

### Step 1.4: Dictionary & Classification Guide Updates

1. **`generate_excel_dictionary.py`:**
   - Add 35 fields to `FIELDS_DATA`.
   - Add module to `MODULES_SUMMARY` (35 fields).
   - Update master counters: 330 climate indicators + 12 administrative fields = **342 total fields** across **19 modules**.
   - Execute script to regenerate `docs/03_Excel_Dictionaries/Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx`.

2. **`generate_master_atlas_excel.py`:**
   - Add module to `MODULE_FOLDER_MAP` and `MODULES_METADATA`:
     ```python
     "19_Land_Surface_Temperature": {
         "ar_title": "درجة حرارة سطح الأرض",
         "en_title": "Land Surface Temperature",
         "unit": "°C",
         "scale_type": "standard",
     }
     ```

---

### Step 1.5: Verification & Automated Regression Testing
Run the complete automated test suite to confirm 100% clean execution:
```powershell
python -m py_compile Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt Toolboxes/raster_atlas_generator.py
python tests/test_power_atlas_108_offline.py
python tests/test_weather_stations_atlas.py
python tests/test_excel_export_108.py
python tests/test_field_filters_108.py
python tests/test_provider_interp_108.py
```
All tests must report **100% PASS (0 failures)**.

---

## 4. Track 2: Incremental Database Updating (Backfill)

> **Real-World Case Study:**  
> A complete project workspace exists for `Egypt Climate Data 1996-2025`:
> - Geodatabase `Climate_Database_From_1996_To_2025.gdb` (with point layers 01 through 18).
> - Raster folders `01_Temperature` through `18_Trends_And_Anomalies`.
> - Directory `00_Tables_And_Reports` with master Excel workbooks and `Source Data/` provenance assets.
> 
> **Objective:** Add Module 19 (`19_Land_Surface_Temperature`) matching exact project standards without re-running previous modules, incorporating all 35 indicators into the GDB and Excel workbooks, updating `Source Data/`, while generating the 11 essential rasters only.

---

### Step 2.1: Establish Staging Directory
Create a dedicated staging folder:
```
C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature_STAGING\
```

---

### Step 2.2: Acquire Raw Data & Cache JSON Locally
Extract coordinates from the primary point layer (646 points). Query parameter `TS` from 1996 through 2025 via the API and cache locally into `00_Tables_And_Reports\Egypt_TS_Raw_Monthly_1996_2025.json`:

```python
url = (
    "https://power.larc.nasa.gov/api/temporal/monthly/point"
    "?parameters=TS&community=AG&longitude={:.4f}&latitude={:.4f}&start=1996&end=2025&format=JSON"
).format(lon, lat)
```

---

### Step 2.3: Calculate Indicators & Build Staging Assets
Compute all 35 indicators for every point:
1. **12 Monthly Means:** `LST_January_Mean` through `LST_December_Mean`.
2. **Annual Mean:** `LST_Annual_Mean`.
3. **Four Seasons:** Winter (DJF), Spring (MAM), Summer (JJA), Autumn (SON).
4. **Annual Range:** `LST_Annual_Range` = Peak Month - Minimum Month.
5. **Annual & Seasonal Differences:** `LST_minus_T_Annual` and `LST_minus_T_<Season>`.
6. **12 Monthly Differences:** `LST_minus_T_<Month>` (Tabular only).

Export the following assets to staging:
* **CSV File:** `19_Land_Surface_Temperature.csv` (UTF-8 encoding).
* **Excel Workbook:** `19_Land_Surface_Temperature.xls`:
  - **`Data` Sheet** (23 cols): 12 administrative + 1 Annual + 4 Seasonal + 1 Range + 5 Environmental differences.
  - **`Month` Sheet** (28 cols): 4 identity cols + 12 monthly means + 12 monthly differences.
  - **`Source_Data` Sheet**: Full provenance documentation (NASA POWER MERRA-2 Skin Temp, 0.5° resolution).
* **Update Master `Source Data` Directory:**
  - Append Module 19 provenance entry to `Source Data/Climate_Data_Sources_Provenance.xls` (including RTL Arabic sheet `ملخص_مصادر_البيانات` and `Source_Data` sheet).
* **Shapefile:** `19_Land_Surface_Temperature_Grid_Points.shp` with compliant $\le 10$ char column names.

---

### Step 2.4: Populate Geodatabase Feature Class (ArcPy da)
Using ArcGIS Python:

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

2. Add 12 administrative fields and 35 indicator fields as `DOUBLE` with **strict 1:1 alias parity** (`field_alias == field_name`).
3. Insert all point rows using `arcpy.da.InsertCursor`.
4. Run verification assertion:
```python
count = int(arcpy.GetCount_management(target_fc)[0])
assert count == 646, "Point count mismatch!"
for f in arcpy.ListFields(target_fc):
    if f.type not in ("OID", "Geometry"):
        assert f.name == f.aliasName, "Alias mismatch on: " + f.name
```

---

### Step 2.5: Generate Continuous Surface Rasters (Spline)
Create production raster directory:
`C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature\`

Interpolate the 11 essential rasters using ArcPy Spatial Analyst:
```python
import os
import arcpy
from arcpy.sa import Spline, ExtractByMask

arcpy.CheckOutExtension("Spatial")

ref_raster = r"C:\...\Egypt Climate Data 1996-2025\01_Temperature\T_Annual_Mean.tif"
mask_poly = r"C:\...\Egypt Climate Data 1996-2025\Climate_Database_From_1996_To_2025.gdb\Egypt"

arcpy.env.snapRaster = ref_raster
arcpy.env.cellSize = 250.0  # 250m
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

---

### Step 2.6: Generate Classification Guide Sheet
Run the master classification builder to compute natural breaks and standard deviation scales:
```powershell
python generate_master_atlas_excel.py --base_dir "C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025" --study_area "Egypt"
```
The script reads raster statistics and creates the `19_Land_Surface_Temperature` sheet in `Climate_Atlas_Classification_Guide.xlsx` with standard 3, 5, 7, and 9 classification breaks.

---

## 5. Quality Assurance Checklist (QA/QC)

| # | Inspection Item | Acceptance Criteria | Verification Method |
|:---:|:---|:---|:---|
| **1** | Primary Toolbox Parameter Count | Exactly 65 parameters | ArcMap GP Tool Properties |
| **2** | Raster Engine Parameter Count | Exactly 33 parameters | `Toolboxes/raster_atlas_generator.py` inspect |
| **3** | Feature Class Record Count | Exactly matches input points (e.g. 646) | `arcpy.GetCount_management` |
| **4** | Feature Class Total Field Count | Exactly 47 fields (12 admin + 35 indicators) | `arcpy.ListFields` |
| **5** | Field Name & Alias Parity | `name == aliasName` (100% identical) | ArcPy validation loop |
| **6** | Shapefile Field Name Lengths | Strictly $\le 10$ characters, no duplicates | DBF inspection |
| **7** | Essential Rasters Count | Exactly 11 `.tif` files in module folder | Folder scan |
| **8** | Unwanted Raster Suppression | Zero redundant or monthly difference rasters | Folder scan |
| **9** | Raster Alignment & Geometry | Snap = T_Annual_Mean, Cell = 250m, Mask = Study Area, Comp = LZW | ArcMap Layer Properties |
| **10** | Excel Workbook Sheets | `Data` (23 cols), `Month` (28 cols), `Source_Data` (8 cols) | `xlrd` / Excel inspect |
| **11** | Source Data Provenance Directory | `Source Data/Climate_Data_Sources_Provenance.xls` updated | Workspace inspect |
| **12** | Classification Guide Sheet | Sheet `19_Land_Surface_Temperature` populated (3, 5, 7, 9 breaks) | Excel check |
| **13** | Field Dictionary Coverage | 342 total fields across 19 modules | `Climate_Atlas_Fields_Dictionary` |
| **14** | Automated Test Regression | 100% PASS rate across all suites | `unittest` runner |

---

## 6. Conclusion

By adhering strictly to this SOP:
1. The **MIRSAD** platform maintains infinite extensibility to support any future biophysical parameter (e.g., Soil Moisture, Actual Evapotranspiration, SPEI Drought Index, Boundary Layer Height).
2. Existing project databases can be augmented and backfilled seamlessly without risking existing deliverables, preserving total mathematical integrity, cartographic consistency, and rigorous provenance documentation.
