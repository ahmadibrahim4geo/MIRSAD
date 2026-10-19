---
name: desktop-gis-architecture
description: >-
  Architect, implement, and optimize standalone Desktop GIS applications in Python (PySide6/PyQt)
  and spatial libraries (GDAL/OGR, GeoPandas, Shapely, PyProj, Rasterio). Use whenever developing
  desktop GIS software, building interactive map canvases, implementing Table of Contents (TOC),
  Catalog trees, Geodatabase (.gdb) / GeoPackage (.gpkg) I/O, or geoprocessing engines.
---

# Desktop GIS Architecture & Engineering Guide

This skill provides foundational engineering patterns, software architecture blueprints, and implementation standards for developing high-performance, standalone Desktop GIS applications using **Python (PySide6 / PyQt6)** and native open-source geospatial engines (**GDAL/OGR**, **GeoPandas**, **Shapely**, **PyProj**, **Rasterio**).

Inspired by industry-leading desktop GIS platforms:
- **QGIS Architecture** (`qgis/QGIS`): MapCanvas, LayerTree, Processing Framework, TaskManager.
- **RustGIS Architecture** (`opengeos/RustGIS`): Ribbon-based tools, high-speed tile caching, immediate UI.
- **ArcGIS Pro**: Geoprocessing toolboxes, Geodatabase (.gdb) browsing, environmental parameters.

---

## 1. Core Architectural Layers

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Desktop GIS UI Layer                            │
│  - Ribbon Toolbar (QToolBar / QTabBar)                                 │
│  - Table of Contents / TOC (QTreeView + Custom LayerTreeModel)        │
│  - Interactive Map Canvas (QGraphicsView / QOpenGLWidget)             │
│  - Tabular Data Views (QTableView + Virtualized Model)                 │
│  - Geoprocessing Toolbox (ArcToolbox Accordion / Tree)                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Qt Signals & Slots
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Geospatial Application Core                         │
│  - Layer Registry & Symbology Engine (Vector / Raster styling)         │
│  - Coordinate Transformation Pipeline (PyProj / SpatialReference)     │
│  - Spatial Indexing & View Frustum Culling (RTree / STRtree)           │
│  - Task & Geoprocessing Worker Pool (QThreadPool / QRunnable)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Low-Level Data I/O
┌───────────────────────────────────▼────────────────────────────────────┐
│                    Data Storage & Providers Engine                     │
│  - File Geodatabase (.gdb) [GDAL/OGR OpenFileGDB Driver]              │
│  - GeoPackage (.gpkg) [SQLite3 / OGR GPKG Driver]                      │
│  - Shapefiles (.shp) & GeoJSON (.geojson)                              │
│  - Cloud-Optimized GeoTIFF & Rasters [Rasterio / GDAL]                 │
│  - Web Map Tile Providers (XYZ / TMS / CartoDB / OSM / Esri)          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Interactive Map Canvas Implementation

### Viewport Transformation (Geographic to Pixel):
Never render whole global datasets without spatial indexing:
1. **Bounding Box Calculation**: Determine the current view bounding box (`min_x, min_y, max_x, max_y`) in Project CRS.
2. **Spatial Query (STRtree)**: Query memory-resident R-Tree to fetch only features intersecting the view frustum.
3. **Affine Transformation**: Map coordinates $(X, Y) \to (ScreenX, ScreenY)$:
   $$ScreenX = \frac{X - min\_x}{max\_x - min\_x} \times ViewWidth$$
   $$ScreenY = \frac{max\_y - Y}{max\_y - min\_y} \times ViewHeight$$
4. **Tile Cache**: Web basemap tiles (XYZ) must be cached locally in an LRU SQLite or directory cache to ensure instant, offline-capable panning.

---

## 3. Geodatabase (.gdb) & GeoPackage (.gpkg) Browser (Add Data Engine)

### Inspection without Full Ingestion:
When browsing databases in the Add Data dialog, never load entire tables into memory. Inspect metadata using OGR:

```python
from osgeo import ogr

def inspect_geodatabase(gdb_path):
    """Inspects feature classes and tables inside a .gdb or .gpkg without full read."""
    driver = ogr.GetDriverByName("OpenFileGDB") if gdb_path.endswith(".gdb") else ogr.GetDriverByName("GPKG")
    ds = driver.Open(gdb_path, 0) # 0 = Read-Only
    if not ds:
        raise IOError(f"Cannot open spatial database: {gdb_path}")

    layers = []
    for i in range(ds.GetLayerCount()):
        layer = ds.GetLayerByIndex(i)
        geom_type_code = layer.GetGeomType()
        geom_type = ogr.GeometryTypeToName(geom_type_code)
        spatial_ref = layer.GetSpatialRef()
        crs_auth = f"{spatial_ref.GetAuthorityName(None)}:{spatial_ref.GetAuthorityCode(None)}" if spatial_ref else "Unknown"
        extent = layer.GetExtent() # (minX, maxX, minY, maxY)
        count = layer.GetFeatureCount()

        layers.append({
            "name": layer.GetName(),
            "geometry": geom_type,
            "count": count,
            "crs": crs_auth,
            "extent": extent
        })
    return layers
```

---

## 4. Non-Blocking Geoprocessing Engine (ArcToolbox Pattern)

### Golden Rules:
1. **Never block the UI Thread**: Long-running calculations (downloads, raster interpolations, contouring) MUST execute inside `QRunnable` or `QThread`.
2. **Thread-Safe Telemetry**: Send progress percentages, log messages, and error traces back to the UI via Qt Signals (`pyqtSignal(int, str)`).
3. **Cancellation Token**: Every geoprocessing job must support cooperative cancellation (`self.is_cancelled`).
4. **Output Auto-Registration**: Upon successful execution, the tool must emit a `finished(results_dict)` signal so the main window automatically registers:
   - Generated Feature Classes into the TOC.
   - Generated Excel workbooks into the **Results & Outputs Section**.

```python
from PySide6.QtCore import QRunnable, QObject, Signal, Slot

class GeoprocessingWorkerSignals(QObject):
    progress = Signal(int, str) # (percent, log_message)
    finished = Signal(dict)     # output artifacts
    error = Signal(str)

class GeoprocessingWorker(QRunnable):
    def __init__(self, tool_func, params):
        super().__init__()
        self.tool_func = tool_func
        self.params = params
        self.signals = GeoprocessingWorkerSignals()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    @Slot()
    def run(self):
        try:
            results = self.tool_func(self.params, self.progress_callback, self.is_cancelled_check)
            self.signals.finished.emit(results)
        except Exception as e:
            self.signals.error.emit(str(e))

    def progress_callback(self, pct, msg):
        self.signals.progress.emit(pct, msg)

    def is_cancelled_check(self):
        return self._is_cancelled
```

---

## 5. Verification & Testing Checklist

When modifying or generating desktop GIS code:
1. **CRS Handling**: Ensure on-the-fly CRS transformations do not mutate raw geometries.
2. **Memory Management**: Verify feature iterators close datasets properly (`ds = None` or context managers) to avoid file lock issues on Windows FileGDBs.
3. **Fail-Soft Isolation**: If a FileGDB export fails due to ArcPy / license limits, the GeoPackage and Excel exports must succeed and be reported cleanly.
4. **Coordinate Precision**: Always preserve 4 to 6 decimal places for coordinates, and retain USAF/WBAN keys as strings with leading zeros.
