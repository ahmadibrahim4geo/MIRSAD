# Architecture Decision Record: ADR-001 — Map Engine Selection

**Status**: Accepted  
**Date**: 2026-10-17  
**Context**: MIRSAD Desktop requires an interactive, high-performance, and dependable Map Canvas capable of panning, zooming, selecting points, displaying raster surfaces, and overlaying vector boundaries without requiring ArcGIS or ArcPy.

---

## 1. Options Considered

### Option A: Native Qt Slippy Map Canvas (PySide6 + SlippyMap + QPainter)
- **Architecture**: Native PySide6 widget with Web Mercator tile fetching, tile disk caching via `QNetworkDiskCache`, vector geometry rendering with `QPainter`, Warped VRT raster overlays via `rasterio`, coordinate picking, and live reprojection with `pyproj`.
- **Pros**:
  - 100% self-contained in PySide6 with zero external GIS desktop dependencies.
  - Very fast startup (< 1.5 seconds) and tiny distribution footprint (< 25 MB executable bundle).
  - No licensing complications (LGPL compatible).
  - Clean separation of UI events and background processing.
  - Full support for both online slippy tiles (OpenStreetMap, Esri) and complete offline operation (`Offline / None`).
- **Cons**:
  - Advanced cartographic symbology (e.g. dynamic arrow vectors, complex rule-based styles) must be drawn custom.

### Option B: PyQGIS Canvas (`qgis.gui.QgsMapCanvas`)
- **Architecture**: Embedding the QGIS C++ runtime into the Python application.
- **Pros**:
  - Full GIS symbology, labeling engine, `.qml` styles.
- **Cons**:
  - Heavy runtime footprint (+1.5 GB of DLLs, plugins, and resources).
  - Severe binary conflicts on Windows: QGIS is compiled against specific PyQt5/PyQt6 builds and older Qt versions, creating critical DLL loading collisions with PySide6.
  - Strict GPL v2/v3 copyleft licensing contagion.
  - Packaging and deployment complexity on clean Windows environments.

---

## 2. Decision
**We select Option A: Native Qt Slippy Map Canvas**.

### Rationale:
1. **Application Independence**: MIRSAD Desktop's core mission is to be an independent, lightweight, self-sufficient Windows GIS application that runs cleanly without third-party GIS runtime installations.
2. **Binary Stability**: Eliminates DLL conflicts, version mismatches, and C++ ABI breakage.
3. **Packaging Simplicity**: Builds smoothly via PyInstaller with zero GPL compliance risks.
4. **Offline Capability**: Features full offline rendering and solid-color backgrounds for environments without internet access.

---

## 3. Basemap Policy
- **Primary Default**: **OpenStreetMap** with mandatory visible attribution (`© OpenStreetMap contributors`).
- **Optional Imagery / Topo**: Esri World Imagery and Topographic tiles (accessible for standard evaluation).
- **Offline Mode**: `Offline / None` providing a neutral canvas with WGS84 coordinate display and EPSG:3857 map projection.
- **Paywalled Services**: Removed from default menus; only activated if the user explicitly enters an API key in-memory.
