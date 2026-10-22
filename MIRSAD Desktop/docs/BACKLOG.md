# Remaining work and acceptance

Updated: 22 October 2026. Completed delivery details live in
[STATUS](STATUS.md), [CHANGELOG](CHANGELOG.md) and [reports/](reports/).
Retired help/readiness and parity execution plans are recoverable in Git history;
their outstanding requirements are retained here.

| Area | Remaining evidence or implementation |
|---|---|
| Climate enrichment plan | Desktop implements 11 optional variables, hourly audit, local/web DEM, separate HG/PM and streaming/split XLSX. Point/Station Toolbox integrates the 11 variables, separate HG/PM methods, yearly XLSX and per-day/hourly audit; native Pro method fixtures passed. See [variables](reports/climate-enrichment/TOOLBOX_ACCEPTANCE.md) and [PM evidence](reports/climate-enrichment/TOOLBOX_PM_ACCEPTANCE.md). Remaining: Toolbox DEM and full native raster acceptance, supported regional/product additions, optional Arabic aliases in Desktop, full per-field help dictionary, 1000-point/30-year pipeline benchmark and DPI. Earlier frozen/installer gates cover the 21 October Desktop candidate; they do not package later source/help changes. See [Desktop acceptance](reports/climate-enrichment/DESKTOP_SOURCE_ACCEPTANCE.md) and [tracker](reports/climate-enrichment/IMPLEMENTATION_TRACKER.md). |
| Toolbox/Desktop parity | Match all advanced inputs, order, activation rules, optional defaults, climate and raster controls against the three tools. Compare the same dataset/provider/period/units across hosts. Resolve differences in filenames, metadata, Excel columns/order, Daily long/wide layout, per-year exports and advanced raster products. Retain actual raw/source provenance. |
| Native ArcMap | Verify actual loading/processing/exports in licensed ArcMap/Python 2.7. Compatibility checks and ArcPy doubles are not native acceptance. |
| Authenticated sources | Live end-to-end CDS and NASA IMERG access with an authorized user's free account/accepted terms. Never use or request the developer's credentials in chat. Retain implemented secret-in-memory policy. |
| Temperature differences | Resolve the documented legacy LST-minus-air Fahrenheit/Kelvin offset defect through an explicit cross-host scientific change with independent expected values; not an organizational fix. |
| Coverage and parity | Compare conservative daily summaries, native monthly/composite paths, Hybrid and kernel aggregation with real missingness. Confirm identical records underpin GIS and Excel outputs, and expose individual FileGDB/GPKG failures. |
| Spatial outputs | Finish the full interpolation/raster/atlas contract, units, masking, class labels, maps and optional surfaces against native reference runs. Measure memory/time on representative small/large projects and cancellation/restart. |
| Desktop navigation | Complete remaining Add Data/catalog requirements, geometry/type validation, input reuse, Contents/table/raster integration, read-only result workflows and state preservation against the retained product requirements. Do not enable unimplemented commands. |
| CRS | The embedded ArcGIS/Esri catalogues are implemented. Continue checking real transformations, unavailable datum grids and layer CRS interpretation; catalogue size alone does not prove transformation accuracy. |
| Native help | Visually verify F1/per-tool XML help in ArcMap and Pro. CHM/Qt/browser display/search do not establish ArcGIS-native summary rendering. |
| Accessibility and themes | Complete 100/125/150/200% DPI, small/large displays, keyboard/screen-reader acceptance and consistent popup/dialog/print contrast in both languages. |
| Packaging | Repeat a full frozen build from a fresh checkout when accepting a release; earlier clean-checkout checks were not a second complete PyInstaller build. Authentic signing needs a real certificate. |
| Release | Stable promotion, production install and public binary Release require explicit approval of the tested candidate. |

Retain Qt/Python for the current implementation. Consider Rust only for a measured
bottleneck with equivalent numerical results, compatibility and packaging evidence.
No language migration is part of the repository reorganization.

For detailed original requirements and unaccepted scenarios, consult
[product requirements](architecture/PRODUCT_REQUIREMENTS.md) and
[design requirements/reference images](design/reference/REQUIREMENTS.md).
These are historical requirements, not declarations that every item is complete.
