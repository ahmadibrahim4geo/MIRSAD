# MIRSAD Desktop — Legacy Audit & Technical Inventory
Date: 2026-10-17  
Author: Lead Desktop GIS Engineer  
Target: MIRSAD Desktop Standalone Application

---

## 1. Executive Summary
This document fulfills Phase 0 of the [original design requirements](../design/reference/REQUIREMENTS.md). It provides a comprehensive audit of the repository, existing toolboxes, runtime architecture, data contracts, and migration readiness.

The legacy toolset comprises two major ArcGIS Python Toolboxes (`.pyt`):
1. `Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt` (supporting ArcMap / Python 2.7 and ArcGIS Pro / Python 3).
2. `Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt` (climate calculation engine and raster atlas generator).

The standalone application (`MIRSAD Desktop/`) operates completely independently from ArcGIS, ArcPy, and any sibling directory. All legacy computational methods are extracted and vendored into pure Python functions through deterministic development-time scripts (`scripts/vendor_science.py`).

---

## 2. Technical Architecture & Component Inventory

| Dimension | Legacy Toolboxes | Standalone Desktop (MIRSAD Desktop) |
|---|---|---|
| **Runtime Environment** | ArcMap (Python 2.7) / ArcGIS Pro (Python 3.x) | Python 3.12 64-bit (Packaged via PyInstaller) |
| **GIS Engine** | Esri `arcpy` geoprocessing engine | GDAL / OGR / PyOGRIO / Shapely / PyProj / Rasterio |
| **GUI Framework** | Esri Geoprocessing Tool Dialogs | PySide6 (Qt 6.x Widgets) with Child Process Isolation |
| **Vector Storage** | Esri File Geodatabase (`.gdb`) | GeoPackage (`.gpkg`) and File Geodatabase (`.gdb`) via `OpenFileGDB` |
| **Tabular Storage** | Excel (`.xlsx`) via openpyxl/xlwt | Excel (`.xlsx`) via openpyxl with exact sheet/column parity |
| **Raster Processing** | ArcPy Spatial Analyst (IDW, Spline, Kriging) | SciPy / NumPy / Rasterio with pure leave-one-out validation |
| **Station Database** | Shapefile / DBF (`assets/stations.dbf`) | SQLite embedded snapshot (`assets/stations.sqlite`, 28,066 stations) |
| **Execution Isolation** | In-process ArcMap / Background geoprocessing | Dedicated `ProcessWorker` running `launcher.py --run-job <json>` |

---

## 3. Data & Contract Preservation Matrix

### 3.1 Station Database Integrity
- **Total Stations**: 28,066 global WMO weather stations audited against NOAA ISD history.
- **Station Keys**: USAF and WBAN are strictly treated as text with leading zeros preserved (e.g. `USAF: '623660'`, `WBAN: '99999'`).
- **QA Status**: 28,064 records verified with exact reference match; 2 coordinate review flags quarantined without destructive editing.
- **Local Persistence**: Bundled as a read-only SQLite database with deterministic SHA-256 validation.

### 3.2 Excel Export Contract
Legacy toolboxes produce Excel workbooks structured as follows:
1. `Data` sheet: Base attributes (`Station_ID`, `Station_Name`, `Lat`, `Lon`, `Elev`, `Country`, non-monthly indices).
2. `Month` sheet: 12 monthly columns per climate variable (`<Var>_Jan`, `<Var>_Feb`, ..., `<Var>_Dec`).
3. `Source_Data` sheet: Metadata, time window, gap-filling method, and provider provenance.

`MIRSAD Desktop` exports adhere 100% to this structure, maintaining identical sheet names, column headers, casing, and precision.

### 3.3 Geodatabase & GeoPackage Contracts
- **Feature Class Names**: `Stations` (working points), `Input_Climate` (processed stations), `Study_Area` (boundary polygon).
- **Coordinate Precision**: All coordinates stored with full 64-bit IEEE floating-point precision. Output coordinates are reprojected using `pyproj` with `always_xy=True`.

---

## 4. UI / UX Redesign Gaps Identified in Existing UI
From auditing `01_current_mirsad_ui.png` against the target requirements:
1. **Language Mixing**: UI currently displays dual labels (e.g., `المخرجات / Outputs`, `نقاطي / My points`). Target requires unmixed language catalogs: pure English by default (`en-US`), and pure Arabic when switched (`ar-EG`).
2. **Tab Layout**: PDF tab was occupying central view by default. Target requires the Map Canvas to be the central primary tab.
3. **Workspace Organization**: Layout needs clear separation matching `02_arcgis_pro_workspace.png`:
   - Left: Contents (TOC) with drawing order, layer visibility, and context menus.
   - Center: Main Map View / Attribute Table / Excel View.
   - Right: Tools / Geoprocessing pane with categorized collapsible parameter groups.
4. **Phantom Layers**: TOC previously pre-populated dummy "Working points" and "Study boundary" items. Target requires Contents to reflect only actual loaded project layers.
5. **Add Data Experience**: Must match `03_arcgis_pro_add_data.png`, allowing deep inspection inside `.gdb` and `.gpkg` containers, layer selection, and role assignment.

---

## 5. Security & Safety Controls
- **Process Worker Boundary**: Native GIS crashes (e.g. GDAL/C++ memory violations) are isolated in child `QProcess` workers; the UI never terminates unexpectedly.
- **Path and File Protection**: Original input files are opened in read-only mode (`r` / `OpenFileGDB`). Overwrite actions require explicit confirmation.
- **No Hardcoded API Keys**: Basemaps rely on free public tiles (OpenStreetMap) with attribution; no paywalled services are enabled without explicit user configuration.
