# 12. Operational User Workflows (Online, Open-Meteo, Offline)
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Workflow 1: Live Online Execution via NASA POWER API

### 1.1 Prerequisites
- Active Internet connection with HTTP/HTTPS access to `power.larc.nasa.gov`.
- Target boundary feature class (Polygon) projected in any valid coordinate system.

### 1.2 Execution Steps
1. Launch **ArcMap 10.8** or **ArcGIS Pro**.
2. Open ArcToolbox $
ightarrow$ `NASA POWER Climate Atlas Generator.pyt` $
ightarrow$ Open `Climate Atlas Generator`.
3. Configure Tool Parameters:
   - **Study Area Boundary**: Select boundary shapefile or feature class.
   - **Data Provider**: Select `NASA POWER`.
   - **Temporal Scope**: Enter Start Year (`1991`) and End Year (`2020`).
   - **Point Grid Spacing**: Enter desired sampling resolution (e.g. `0.25` degrees).
   - **Interpolation Method**: Select `IDW`, `Spline`, or `Kriging`.
   - **Output Geodatabase**: Choose target `.gdb` workspace.
   - **Output Raster Folder**: Choose destination folder on disk.
4. Click **OK** to execute. The geoprocessing console displays real-time progress:
   - Point grid generation
   - Ingestion from NASA POWER API
   - Quality assurance filtering
   - Vector synthesis and surface raster interpolation across all 18 folders.

---

## 2. Workflow 2: High-Resolution Execution via Open-Meteo Archive API

### 2.1 Use Case
Ideal for mountainous regions, complex coastlines, or local municipal studies requiring the higher spatial fidelity of ECMWF ERA5-Land ($0.1^\circ \approx 9\text{ km}$).

### 2.2 Execution Steps
1. In the tool dialog, set **Data Provider** to `Open-Meteo`.
2. Set **Point Grid Spacing** to `0.1` degrees.
3. Open-Meteo queries execute via non-blocking parallel batches, retrieving hourly and daily archives for rapid synthesis.

---

## 3. Workflow 3: Complete Offline Execution via Local Point Cache

### 3.1 Use Case
Operating in air-gapped secure facilities, remote field laptops without internet connectivity, or re-running rasters with different interpolation settings without re-downloading data.

### 3.2 Execution Steps
1. Copy previous session cache or populated `Climate_Atlas_Points` feature class to the local machine.
2. Open `Raster Data Climate Atlas Generator` standalone tool (`raster_atlas_generator.py`).
3. Point **Input Feature Class** to the local points table.
4. Select target **Modules to Interpolate** (e.g. `All`, `Temperature`, or `Precipitation`).
5. Choose **Interpolation Method** and **Cell Size**.
6. Click **Execute**. All 103 rasters are generated entirely locally from the existing attribute table in under 5 minutes.

---

## 4. Workflow 4: Monthly Climatology Rasters (Jan–Dec)

Both tools expose **Generate Monthly Climatology Rasters (Jan–Dec) / توليد راستر مناخي مستقل لكل شهر** (`GPBoolean`, default OFF) right after the Temporal Scope parameter:
1. Select a **multi-year period (≥ 2 years)** — single years are skipped with a warning because a one-year "climatology" is meaningless.
2. Check the monthly option and execute. Each element gains a `Month/` subfolder with 12 rasters (Wind: 24) plus unified-stretch metadata; point tables and Excel workbooks gain the 12 `*_January_Mean … *_December_Mean` fields and a `Month` sheet.
3. **Online tool** computes the 12 fields from the downloaded time series during the run.
4. **Offline tool** reads the 12 fields straight from the input point layers (no download); absent fields are skipped.
5. **Backfill without re-downloading**: `scripts/build_monthly_tables.py` (pure Python, anywhere) derives the 12 fields from `Egypt_Monthly_Raw_1996_2025.json` into `Monthly_Climatology/*.csv` and appends them to the `.xls` tables; `scripts/build_monthly_backfill_arcmap.py` (inside ArcMap) injects them into the GDB (alias = field name) and interpolates the `Month/` rasters, `Wind_Vector_Month` and the PSL/PS month isobars.
