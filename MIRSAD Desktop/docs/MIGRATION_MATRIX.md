# Toolbox migration status — development 0.3

The standalone executable has one source tree and no runtime ArcGIS dependency. This matrix distinguishes migrated workflows from exact legacy parity.

| Legacy workflow | Standalone implementation | Evidence / remaining limits |
|---|---|---|
| Ground station catalogue and country/region selection | Embedded identified catalogue, filters, stable multiple selection | 28,066 location records; shared version/hash; two coordinate review flags preserved |
| Point climate tool | Own SHP/GDB/GPKG/Excel/CSV points, coordinate entry/picking, CRS mapping, all 19 module groups | 38 pure legacy scientific functions vendored reproducibly; independent numerical fixtures |
| Providers | NASA POWER daily and Open-Meteo ERA5 daily/hourly normalization | Live 19/17 group requests pass; LST/UV disabled for this ERA5 route; no direct NOAA/Hybrid claim |
| Monthly, seasonal, annual and individual years | Scientific summaries, optional monthly ranges and yearly Excel, source/daily units and coverage | Partial-year totals are not promoted to complete annual totals; insufficient trend history remains NULL and flagged |
| Regional raster workflow | Generate grid inside local boundary; sample supported point APIs; interpolate/clip | This is explicit point-grid sampling, not a claimed native NASA regional raster adapter |
| Existing climate point layers | Import numeric fields and process without another download | Local GIS/Excel exports, clipped GeoTIFF, PDF and leave-one-out scores tested |
| Interpolation | IDW, nearest, linear TIN, thin-plate spline, local ordinary exponential kriging | Independent implementations; ArcGIS parameter/variogram parity is not yet certified |
| Spatial database outputs | Real FileGDB and GPKG feature classes, user-selected output CRS | Coordinate/attribute/NULL readback; ArcGIS Pro reads 20 EPSG:32636 feature classes |
| Data browser | Add Data for point/polygon/line/table/raster datasets, layer selection, CRS assignment, bounded previews | GIS parsing in child processes; original datasets are preserved |
| Map display | Native pan/zoom, Esri and OSM, user overlays, licensed Google/Azure connection | Esri live rendering verified; licensed keys not available for a live acceptance test |
| Specialized cartography | PDF map pages and continuous scalar rasters | Legacy isobars, dedicated wind-arrow feature classes, full classification/style suites and `.lyr/.lyrx` export remain outstanding |
| Independent tools | Fixed map/viewers/inputs/climate/raster/output positions; separate station, own-point and point-field-raster drafts | Cross-tool selection, source/period, modules and raster option isolation tested; drafts are session-only |
| Result previews | Paginated Excel sheets / GIS attributes; explicit Use as input; map overlays; PDF pages rendered in a child process | Original workbook bytes preserved; preview is not full Excel formatting or formula evaluation |
| Application lifecycle | Two fixed distribution channels, worker recovery/journals, embedded Help, version metadata; per-user Inno installer and separate-QA install/uninstall verification scripts | Project reopen/editor, trusted Authenticode signature and clean-machine certification remain outstanding; installer test evidence is recorded separately |

Primary scientific source: `MIRSAD_Climate_Atlas_Generator_10_8.pyt::compute_point_fields` and its pure dependency closure. Extraction is development-time only via `scripts/vendor_science.py`; the distributed application never locates the parent toolbox.
