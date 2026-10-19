# Development 0.4.0.dev7 source integration

Reviewed 18 October 2026. This delivery implements the shared source cycle; it does not close the separate full legacy output/raster-option parity milestone.

## Implemented behavior

- Three distinct EN/AR toolboxes: Point, Weather Stations, and Grid Raster. The point toolbox keeps its filename/alias and its own optional raster generation, without registering the regional tool twice.
- Shared Python 2.7/3 adapters are copied byte-for-byte into Desktop at build time. Desktop never imports a parent toolbox at runtime.
- Auto selects ERA5-Land for supported temperature/RH/dewpoint variables from 1950 and ERA5 for other supported variables. Whole intervals beginning before 1950 use ERA5. Manual overrides remain separate per tool. POWER and other fixed products retain their actual native grids.
- Station Hybrid retains NOAA → ERA5 → NASA source-wide barriers, then optional monthly estimation. Any-point Hybrid starts at ERA5. Independent providers never acquire an undocumented NASA supplement. Failure of one Auto request group preserves other groups and remains retryable.
- CHIRPS v3 monthly final, TerraClimate v1.1 monthly, CHELSA v2.1 monthly, MODIS MOD11A2 daytime/nighttime, and explicit-ID GHCN-Daily are implemented. Native CHIRPS/CHELSA regional cell extraction is implemented in both Desktop and the regional toolbox.
- Direct CDS ERA5-Land ARCO and daily Final IMERG V07 adapters are implemented with **Need Sign In**, using the user's personal token/account. CDS/IMERG live authenticated end-to-end verification remains pending.
- Desktop credentials pass through a bounded stdin pipe, including the windowed frozen EXE. They are absent from saved requests, manifests, job logs, CLI arguments and environment variables. Password/token fields are masked. Public products do not show account fields.
- Native monthly/composite records never fabricate daily observations. MODIS primary LST coverage reflects accepted clear-sky days; optional surface-air differences stay NULL without air temperature. Unsupported module dependencies produce module-specific quality results.
- Monthly/composite products constrain the toolbox temporal control to Monthly and disable Daily export. Direct execution also enforces this contract, including calls that bypass ArcPy's parameter-update cycle.
- ArcGIS interpolation materializes the identical non-NULL point selection in an owned scratch FileGDB, then passes its full path to Spatial Analyst. This resolves error 010819 from named FeatureLayers backed by paths containing spaces. Temporary workspaces are restored, and raster failures now fail an explicit QA check and produce a completed-with-warnings outcome instead of unqualified success.
- Desktop Excel adds Source_Resolution, with actual product/resolution per station and variable. Existing Data/Month climate columns are retained. Both spatial formats read back from the same calculated records; export failures remain explicit.

## Numerical and runtime evidence

All test/live artifacts below are disposable files under `.test-output/`, not distributable project data.

| Check | Actual result |
|---|---|
| Desktop suite | 46 tests passed, including real Excel/GPKG/FileGDB NULL and zero readback, source credentials, per-tool drafts, map controls and CRS |
| Shared source barriers | 12 tests passed, including partial Auto product failure/retry and actual per-variable provenance |
| Legacy control-flow/validation/data quality | 22 + 12 + 16 isolated tests passed; control-flow and validation also passed on Python 2.7. ArcPy doubles are not native verification |
| Product unit/protocol fixtures on Python 2.7 | 7 passed: CF packing, rainfall totals, MODIS quality, GHCN flags, CDS 24h conversions, token transport/redaction |
| Bounded GeoTIFF fixtures on Python 2.7 | 4 passed: zero/nodata/edges, strips, HTTP ranges, cache, cancellation, native-centre AOI limits |
| TerraClimate Pro 3.6 | Cairo January 2024 rainfall **2.5 mm** read back from native FileGDB; `.test-output/terra-native.json` |
| Auto ERA5 Pro 3.6 | January 2024 temperature/rainfall exported; unsupported UV stays a module-quality issue without rejecting valid earlier modules; `.test-output/era5-native.json` |
| CHIRPS regional Desktop versus Pro 3.6 | Same four original Amazon cells: **328.07, 331.81, 326.27, 329.32 mm**; both native workflows/readback passed |
| CHIRPS annual native raster | Pro 3.6 generated **6/6** annual/range/seasonal GeoTIFFs in the space-containing workspace; independent GDAL readback verified EPSG:32719, 5,000 m output cells and finite nonnegative data. Output cell size is interpolation resolution, not an increase in CHIRPS native resolution |
| CHIRPS annual arithmetic | Independent sum of 12 retained raw monthly values matches each annual point value to 1e-6 mm: 2154.8974113464355, 2208.8127212524414, 2193.521774291992, 2271.794219970703. The existing monthly export rounds to two decimals; it was checked separately |
| Remote grid versus GDAL | CHIRPS samples match GDAL exactly, including 328.0668640136719 and 73.09212493896484 mm; CHELSA raw pixel matches checked |
| CHELSA current archive | Cairo January 2021 T=15.65°C, rainfall=1 mm, cloud=15.43%; January 2018 Tmax/Tmin/RH/wind metadata and values also verified |
| TerraClimate solar | Cairo January 2024 **13.65984 MJ/m²/day**, using actual CF scale/offset and W/m² conversion |
| GHCN-Daily | Explicit USW00094728, matching New York coordinates, January 2024 TMAX/TMIN/PRCP; absent TAVG remains absent |
| MODIS | Cairo January 2024 daytime LST 20.234°C with **10/31** quality-accepted clear-sky day coverage |

Relevant logs: `products-live`, `products-current-live`, `chelsa-extended`, `grid-acceptance`, `chirps-regional-desktop`, `chirps-regional-pro`, `chirps-regional-pro-annual`, `native-annual-independent`, `era5-auto-native`, `products-final-suite`, `build-dev7-final`. The annual fixture and independent readback are in `.test-output/regional-products/run-1792345646146/`. The native annual raster run verifies the interpolation repair; the final temporal-control guard is covered separately by the isolated validation tests.

## Explicit verification limits

- ArcMap's native Python process did not return from `import arcpy` after more than 10 minutes. Only that test process was stopped. Python 2.7 adapter fixtures passed, but a native ArcMap end-to-end run is **not confirmed**.
- No personal CDS/NASA account was supplied or requested in chat. Live authenticated downloads, terms acceptance and account authorization require a separate verification session. Protocol/conversion tests do not establish valid-account access.
- CHELSA solar radiation remains excluded because current file scaling/unit metadata and older specifications disagree. Missing dates/files remain NULL; no guessed conversion is used. Other CHELSA variables have variable-specific coverage, not a universal 2021 end.
- GHCN requires an imported supporting station/point layer with GHCN_ID. The NOAA USAF/WBAN catalogue is not silently converted into GHCN identifiers.
- TerraClimate and MODIS are currently point/site adapters. Native regional source extraction is enabled only for NASA POWER, CHIRPS and CHELSA.
- Full equality of legacy and Desktop Excel metadata columns, filenames, Daily layout and advanced raster controls remains open. Scientific kernels and download adapters are shared, but that alone does not prove complete UI/export parity. See DESKTOP_PARITY_REWORK_PLAN.md.
- [The static output contract audit](OUTPUT_CONTRACT_AUDIT.md) confirms the declared scientific field names for all 19 groups on a complete two-year fixture with monthly ranges enabled. Five legacy metadata fields, identifier/type/order mappings, input attribute retention, file layout and advanced parameters still need explicit parity work; a static field-name match is not end-to-end export equality.
- Broad historical root `unittest discover` is not green: it mixes native-only imports and independent ArcPy doubles, and retains old parameter-count/provider expectations. Current relevant suites were run in isolated processes; the broad attempt is retained in `.test-output/root-products-suite.log` rather than reported as passing.

## Documentation and package gates

`scripts/build_climate_source_catalogue.py` generates the shared JSON snapshot, matching embedded snapshot, EN/AR source profiles and bilingual `climate-sources.html`. The Desktop offline guide consumes that snapshot. Source manuals, website translations and the comparison Word document were updated; obsolete completeness/no-login claims were removed from current source profiles. Word was exported with installed Microsoft Word because LibreOffice is absent, then all seven PDF pages were rendered and visually inspected. QA PDF/images remain scratch files.

The development build must pass scientific/GIS/raster/PDF diagnostics, GUI export and actual frozen workspace tests from outside the repository with a clean PATH. The frozen workspace test verifies the credential pipe without logging its fixture secret. Installer acceptance uses a separate QA AppId and disposable `.build/` installation, verifies payload hashes and preserves user-created files during uninstall. Stable is unpromoted.

Final dev7 gates **passed**: all 46 Desktop tests, frozen diagnostics/GUI/workspace, independent annual raster readback, and QA installer installation/readback/uninstallation with user files preserved. Static comparison verifies all 16 reviewed runtime modules and their current source documentation, including the scientific source hash. PE machine `0x8664` confirms the delivered EXE is 64-bit. The build now regenerates the catalogue after resolving its Python runner and fails explicitly if generation fails.

| Candidate artifact | SHA256 |
|---|---|
| `runtime/development/MIRSAD.exe` | `d65377c5ea9d485b60e57ea2c7ca55d33c9039ab4f9764efbada880b650a2928` |
| Complete development bundle | `ab9b03a17aa80ecb111c31c08ca8169756c7d57d653c4896e82f511fd183e5d9` |
| `runtime/installers/development/MIRSAD-Setup.exe` | `47cdf617ba7b88121f1f583fe68be6ba1c81381f33366a7e317cdcde2c9d491f` |

Final evidence: `.test-output/dev7-delivery.json`, `packaged_source_equivalence.json`, `installer_acceptance.json`, `packaged_workspace.json`, and `source-docx-acceptance.json`. Source catalogue and all five vendored source adapters were checked byte-for-byte against their shared copies. No stable binary was created and no production installation or external website was changed.
