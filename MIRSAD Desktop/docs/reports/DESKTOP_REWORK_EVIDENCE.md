# Development rework evidence — 18 October 2026

Candidate: **0.4.0.dev1**, development channel only. This records implemented changes and actual checks, not a claim of complete Toolbox parity.

Final receipt: the rebuilt EXE passed its frozen self-test, GUI export and workspace acceptance; the final installer passed payload verification, installed-workspace execution, uninstall and user-file preservation. Bundle SHA-256: `3de1ca09fbfc913a5d005634bc0a1de13a616d0432b06e929f07876bc7d3b41c`. Installer SHA-256: `4e70a72c5c865ad503e80ae95b1f3ad1c169b0ed4c7851535636a676ead40a2c`. Stable still contains only its reserved README.

## Implemented

- Removed Google/Azure basemap connection UI, key prompts, session creation, authenticated tile requests and dynamic attribution requests. Unknown old basemap names fall back to the local/offline map. Public no-key backgrounds retain attribution; input datasets and climate providers remain separate.
- Applied neutral charcoal/light palettes and QSS at application level, including dialogs/popups and inactive windows. Added compact bounded combo popups, actual checked-checkbox SVG resources, readable light/dark selection colors, explicit scrollbar page styling, wrapped labels and responsive panel constraints.
- Made the layer/sidebar, viewer and tool inspector separate draggable splitter sections, with panel visibility/reset commands and saved layout. Reduced canvas/table minimum sizes to support scaled screens. Both interface directions and themes are exercised in native-window captures.
- Kept raster settings accessible for the point and station tools. Raster production remains an explicit workflow choice. Fixed independent draft preservation of end dates, selected Open-Meteo model, monthly rasters, classification and individual units.
- Passed selected Open-Meteo models, monthly raster flags and individual units through the JSON worker/service contract. Fixed seasonal selection incorrectly dropping all named seasons; monthly table fields remain available independently of raster selection.
- Enabled all 19 module groups for the Open-Meteo route with an explicitly announced NASA supplement for unavailable/missing variables. Actual per-value sources and raw responses are retained. Provider/model changes use distinct versioned cache identities.
- Implemented NOAA GSOD (ISD-derived daily summaries) in Desktop Hybrid. Both USAF and WBAN must match; a location discrepancy greater than 0.05 degrees is excluded and recorded, not corrected. Observations have priority over selected ERA5, then NASA supplementation. Source flags and raw CSV remain available. Incomplete precipitation reports (including H/I zero values), missing sentinels and zero-observation mean fields are excluded. Original coordinates are preserved.
- Added a separate native NASA POWER **monthly regional endpoint** workflow, with its own download AOI and study mask, tiled downloads, native grid-cell records, raw JSON, monthly coverage, GIS/Excel, optional individual-year Excel, clipped continuous/classified GeoTIFF and PDF. This uses regional grid requests rather than generated point-API sampling. No artificial daily observations are generated from monthly data.
- Implemented actual classified rasters for Jenks, equal interval and quantile choices. Jenks uses a documented deterministic sample of at most 1,024 cells; class 1 is highest and 0 is NoData. Continuous rasters remain available and read back.
- Reused interpolation indexes/fitted interpolators across raster chunks and eliminated full-grid coordinate mesh arrays. Processing remains in the isolated 64-bit child process.
- Embedded the exact **ArcGIS Pro 3.6** CRS folder/name snapshot: **7,519 entries = 1,175 Geographic + 6,344 Projected**, exported read-only from the installed Pro runtime. The separately pinned public Esri catalogue includes **9,185 definitions** and its license/hash manifest. The picker can switch catalogues; Desktop never imports ArcGIS to use them. Correct canonical PROJ definitions are preferred, with official WKT fallback for missing registry codes. Invalid custom CRS cannot be accepted.

## Evidence locations

All disposable runs are inside `.test-output/`:

- `rework-tests-final.log`: **33 passing** final source unit/integration/UI tests, including missing regional dependencies reporting partial results while preserving successful exports.
- `rework-live/network_report.json`: live selected ERA5/ERA5-Land/ERA5-Seamless requests including dependencies of the 19 groups, NASA and Hybrid. Counts show actual available values; a successful request does not certify complete coverage. The NASA sample contains missing wind direction, retained as missing.
- `rework-live/Regional_Live/`: actual small regional download and GDB/GPKG/Excel/GeoTIFF/PDF outputs with a manifest and raw source JSON.
- `rework-native.json`: native ArcGIS Pro 3.6 construction/update of all six English/Arabic tool entry points (67/74/35 parameters), and native FileGDB readback of the new regional output. This is not an end-to-end run of every legacy provider/parameter combination.
- `rework-crs-validation.json`: all 9,185 public CRS definitions parsed successfully. This checks definitions, not transformation accuracy.
- `rework-ui/`: native Qt window, menu and CRS screenshots in light/dark and Arabic/English, plus scale reports. Screenshots were inspected and clipping/minimum-size issues corrected.
- `rework-performance.json`: warmed median of three runs of the same IDW workload, 10,000 source points and 200,000 query cells, power 2, 12 neighbours. Measured 0.3393 s before versus 0.2317 s after (about 32% less time, 1.46× throughput), with zero numerical difference on this fixture. This is a CPU interpolation benchmark, not a network/export/ArcGIS performance claim.
- `rework-source-build-parity.json`: code instructions, constants, names and function signatures in 25 packaged modules compared with current sources; no mismatch. Debug filenames/line tables are excluded.
- `packaged_self_test.json`, `packaged_ui_export.json`, `packaged_workspace.json`: frozen application checks, actual worker export and interactive workspace/preview acceptance outside the repository working directory.
- `rework-build-final.log`, `rework-installer-build.log`, `installer_acceptance.json`: final development build and installer evidence. A missing compiler was prepared in official portable mode under `.build/tools/`; the public download's Authenticode signature validated. It is a build tool, not part of MIRSAD or a system installation. Installer QA uses a separate application identity and verifies payload, installed workspace, uninstall and preservation of user-file fixtures. A short-lived uninstaller-helper cleanup race was repaired with bounded retries confined to the verified QA directory.

The existing 10 Toolbox validation and 19 runtime regressions also pass under the independent Python environment. They use an ArcPy double and are distinguished from the native checks above. No new runtime dependency was added.

## Limits still requiring implementation/acceptance

- **Full 67/74/35-parameter parity is not complete.** `TOOLBOX_PARAMETER_CONTRACTS.json` records the actual legacy parameter inventory. Advanced IDW search/radius profiles, additional Kriging models/drift and spline variants, buffer/custom station selection parity, specialized pressure contours/focal smoothing, wind vector products, optional Shapefile/localized-database workflows and ArcGIS layer/style files are not all migrated or certified.
- **Exact output schema/name/layout parity is not certified.** Current Desktop workbooks preserve Data/Month/Source_Data and optional Daily/year files, but legacy OBJECTID/Source_ID/administrative schemas and daily wide tables differ from Desktop stable-key/daily-long tables. No claim of byte-identical files or identical columns is made. Existing GDB/GPKG outputs use the same calculated records and stable keys with readback.
- Standalone interpolation methods still require numerical comparisons against native ArcGIS implementations across representative datasets; the IDW benchmark proves before/after Desktop equivalence only.
- Native regional data are monthly and require complete calendar months. Requests are bounded to 512 tiles/20,000 grid points; raster/cell limits still apply. Variables on different native grids are joined only at matching coordinates; missing scientific dependencies are flagged rather than interpolated or fabricated silently.
- A NOAA catalogue location is not proof of current field accuracy. GSOD is an identified daily product derived from ISD, not direct hourly ISD ingestion. The existing legacy Toolbox Hybrid implementation was inspected/validated but was not replaced by the new Desktop adapter in this change.
- Available registry definitions do not guarantee a particular datum transformation's accuracy or that required grid files are installed. A complete transformation-choice UI and clean-machine certification remain outstanding.
- No rewrite to Rust was introduced: the measured bottleneck was addressed by reusing the existing native SciPy index. Trusted signing and stable promotion remain separate; no stable release was changed.

## Reproduction

Use the independent `.venv` to run `python -m unittest discover -s tests -v`, `scripts/verify_rework_network.py`, and `scripts/build_development.ps1`. The network script needs internet; the native audit/snapshot scripts require the development machine's licensed Pro runtime only. `scripts/build_crs_catalogue.py` pins and hashes official source data; `capture_native_crs.py` and `integrate_native_crs.py` reproduce the native folder snapshot. The benchmark requires the preserved local before-change source snapshot and is evidence of this change, not a distributed application dependency.

Development: `runtime/development/MIRSAD.exe`. Installer candidate: `runtime/installers/development/MIRSAD-Setup.exe`. Promote neither to stable without explicit approval of the verified candidate.
