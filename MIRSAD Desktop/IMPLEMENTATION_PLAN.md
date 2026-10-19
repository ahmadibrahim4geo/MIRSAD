# MIRSAD Desktop — execution plan

Updated: 2026-10-18. Master specification: `MIRSAD_DESKTOP_MASTER_PLAN.md`.

## Current requested work — 18 October 2026

New planning request: [Help centre and repository contribution readiness](../Documents/HELP_AND_REPOSITORY_READINESS_PLAN.md). Extend the existing bilingual Qt manual into a topic tree, result search, bookmarks, navigation and printing; generate independent offline toolbox help from the same content. Audit cleanup/test failures and prepare clean-clone contributor workflows before repository updates. Stages H0–H6 are planned, not implemented by this planning turn; the dev7 executable, installer and stable channel remain unchanged.

The shared source cycle is implemented in dev7. [The shared development roadmap](../Documents/DEVELOPMENT_ROADMAP.md) records decisions and stage status; [dev7 acceptance evidence](docs/DEV7_SOURCE_ACCEPTANCE.md) separates implemented adapters, verified public/native runs and remaining authenticated/ArcMap/full-output-parity limits.

The user's complete toolbox-parity and desktop UI rework scope is recorded in [DESKTOP_PARITY_REWORK_PLAN.md](docs/DESKTOP_PARITY_REWORK_PLAN.md). This is planned work, not a completed delivery. It includes removing Google/Microsoft and other API-key-dependent basemap connections, improving native resizing and compact menus, complete consistent light/dark themes, tool/provider/raster/output parity, an audited CRS catalogue, and measured performance improvements. Retain Qt initially; evaluate Rust for demonstrated computation bottlenecks, with numerical parity and packaging evidence before adoption. The historical licensed-basemap implementation recorded below is superseded by the removal requirement. Stable remains subject to explicit candidate approval.

## Fixed product locations

Map UI follow-up (0.4.0.dev3): replaced the full-width basemap combo with a compact native icon/gallery, moved navigation into floating map controls, added local scalable outline icons and viewer-tab styling, localized accessible tooltips and canvas-scoped keyboard shortcuts. See [MAP_CONTROLS_REWORK.md](docs/MAP_CONTROLS_REWORK.md) for visual and interaction acceptance. Stable remains unchanged.


Hybrid follow-up (0.4.0.dev2): implemented source-wide NOAA → selected ERA5 → NASA barriers shared with the Python 2/3 toolbox, request checkpoints/resumption, late monthly estimation and per-cell audits. See [HYBRID_PIPELINE.md](docs/HYBRID_PIPELINE.md) for scientific rules, actual live/native evidence and limits. Stable remains unchanged.

- Development executable: `runtime/development/MIRSAD.exe`.
- Approved executable: `runtime/stable/MIRSAD.exe` (created only after approval).
- One source tree, one build command, one promotion command. Build and test scratch directories are not additional applications.

## Development 0.4 rework — 18 October 2026

Implemented removal of API-key basemaps, application-wide neutral light/dark themes, compact popup controls, resizable/persisted panels, always-accessible raster settings, per-tool model/date/monthly/classification/unit drafts, selected-model worker routing, actual NOAA GSOD Hybrid ingestion with per-value provenance, declared NASA supplements for Open-Meteo dependencies, native NASA monthly regional downloads with separate AOI/mask, monthly/classified rasters, and reusable interpolation indexes. Embedded the exact 7,519-entry ArcGIS Pro 3.6 CRS taxonomy plus the separate 9,185-definition official Esri catalogue.

See [DESKTOP_REWORK_EVIDENCE.md](docs/DESKTOP_REWORK_EVIDENCE.md) for tests, real live/native evidence and outstanding requirements. Full advanced-parameter and exact Excel/GIS schema parity remain unfinished; the rework plan is not marked complete. Stable is unchanged.

## First usable delivery

### Development 0.4.0.dev7 — per-variable products and user accounts

- Implemented default Auto per variable and full interval, real manual overrides, previewed product/grid decisions and actual resolution provenance. Shared request groups survive another group's failure and retry incomplete checkpoints.
- Added CHIRPS monthly final, TerraClimate v1.1, CHELSA v2.1, separate MODIS LST day/night and explicit-ID GHCN. CDS ARCO/IMERG account adapters have Need Sign In and masked own-account fields; secrets use a bounded worker pipe and are excluded from persisted jobs/logs.
- Added CHIRPS/CHELSA original-cell regional extraction to both runtimes; four-cell CHIRPS Desktop/Pro values match. Kept native monthly/composite coverage and NULLs through real dual spatial/Excel readback. Added Source_Resolution Excel sheet without renaming existing climate columns.
- Repaired native ArcGIS 010819 interpolation failures on space-containing paths using a materialized NULL selection in the owned scratch FileGDB; actual annual CHIRPS produced six GeoTIFFs, checked independently with GDAL and raw-month arithmetic. Failed rasters now fail QA and cannot produce an unqualified success summary. Monthly product controls and direct execution prevent Daily exports.
- Rebuilt bilingual offline/source guides, website source status and comparison Word document from the reviewed source snapshot. Corrected old completeness/no-login claims and clarified date/variable/product limits.
- 46 Desktop tests, isolated shared/legacy tests and native Pro runs passed. Frozen EXE acceptance verifies GUI/worker/rasters/PDF/CRS and secret transport. Final build/installer gate evidence is retained under .test-output. Stable remains unpromoted.
- ArcMap native import stalled before tool execution; Python 2.7 source fixtures passed. CDS/IMERG live account access and complete legacy metadata/file/raster-option parity remain explicitly open. See docs/DEV7_SOURCE_ACCEPTANCE.md.

### Development 0.4.0.dev6 — independent sources and native resolution

- Added standalone NOAA GSOD for real station identities, standalone selected ERA5 and ERA5→NASA any-point Hybrid in the shared Python 2/3 and vendored Desktop ingestion paths. No nearest-station substitution or hidden standalone provider fallback.
- Added real source-resolution choices, highest supported ERA5-Land grid initially selected, fixed NOAA/POWER information and per-tool remembered ERA5 profiles. Live tests exposed unsupported ERA5-Land variables; UI, retained warnings and bilingual guides explain NULLs and the Seamless/ERA5 alternatives.
- Shared tests pass on Python 2.7. Native Pro 3.6 NOAA-only and ERA5-only runs produced January 2024 station GIS/Excel outputs with source-policy assertions. All three reanalysis profiles and NOAA annual CSV were requested live. See `docs/CLIMATE_SOURCES_AND_RESOLUTION.md` for source research and explicit verification limits.
- Advanced legacy schema/raster-option parity remains outstanding. Researched CHIRPS, TerraClimate, CHELSA, gridMET and CDS are future adapters; no unimplemented provider is enabled. Stable is unpromoted.
- The fixed development EXE and installer now contain dev6. All 42 Desktop build tests, 38 root checks, Python 2.7 shared checks, frozen GUI/worker/export diagnostics and QA installer installation/uninstallation passed. The latest compact UI also passed its 11-test suite and visual review in Arabic dark/English light. Stable remains unchanged.

### Development 0.4.0.dev5 — Esri coordinate-system browser

- Kept the versioned Pro 3.6 taxonomy in every catalogue mode: exact geographic continent and projected-family folders, full UTM subgroups and WGS hemisphere levels. The public PE catalogue's area-of-use grouping no longer replaces the native tree. Its 1,760 additional definitions have explicit separate branches.
- Added persistent Favorites, source-CRS groups under Layers, an initially collapsed native-tree overview, selected-system summary, optional details, path-aware search with expansion restoration and Show selected.
- Propagated original CRS metadata from point import, polygon import and spatial preview workers into layer records. Coordinate calculations, source data and climate/export contracts are unchanged.
- Updated both user guides. Acceptance evidence, verified native paths and development package results are in `docs/CRS_BROWSER_REWORK.md`. Stable remains unpromoted.
- After explicit user permission to close and replace development, dev5 replaced the fixed development directory. Post-replacement GUI startup passed; the installer was rebuilt from that final directory and installation/uninstallation acceptance passed again. Stable remains unchanged.


### Development 0.4.0.dev4 — user guide and transient basemap panel

- Replaced the focus-dismissed basemap popup with an embedded transient panel. Explicit style selection, outside click, Close and Esc dismiss it; screenshot focus loss does not. A Windows mouse-only poll runs solely while the panel is visible, so a later click in another application also dismisses it without installing a global hook.
- Added responsive swatch cards, current-style/source information and compact scrolling rows for short map canvases. Retained both UI languages and themes.
- Replaced the short modal help page with a modeless native bilingual manual: 15 chapters, searchable full text, resizable contents pane, provider coverage/reference links, three tools and all 19 registered module groups. Bundled and standalone HTML are generated from the same source during each build. Scientific and output limitations are explicit; this does not claim finished advanced Toolbox parity.
- Verification and packaged candidate evidence are recorded in `docs/USER_GUIDE_AND_BASEMAP_PANEL.md`. Stable remains unpromoted.

1. Audit all repository station spatial datasets and coordinate tables without modifying originals. Compare geometry/attributes, CRS, shared IDs, and NOAA history when available.
2. Generate an identified shared station catalogue and embed its snapshot with the approved logo in Desktop.
3. Implement a clear station browser with country/search/multiple selection and a coordinate preview.
4. Export selected station feature classes to real FileGDB and GeoPackage, plus Excel and an export manifest.
5. Implement the first climate-download workflow, with only supported providers/elements, truthful provenance, progress and cancellation.
6. Build the one development EXE and verify it independently of ArcGIS and parent toolbox paths.
7. Review the development candidate with the user before promoting to stable.

## Later increments
- Broader climate registry and migrated scientific calculations with parity tests.
- Boundary imports, spatial filtering, raster interpolation and climate atlases.
- Installation/uninstallation and release packaging after the executable workflow is accepted.

## Acceptance evidence

### Delivered first slice — 17 October 2026
- Root and Desktop AGENTS.md guides created; master plan updated to 0.3.
- Audited station layers in all three repository FileGDBs and station shapefiles/CSV. Created the shared catalogue, version 2026.10.17.2, with 28,066 location records and 86 Egyptian stations. The two historical latitude-sign discrepancies remain explicitly flagged.
- Toolbox station selection now reads the shared catalogue. Its previous DBF input remains the fallback for old distributions without the shared file.
- Independent PySide6 UI implemented with the approved logo, Arabic/English, country/search/selection and coordinate preview.
- Real FileGDB/GeoPackage export and readback implemented, including Arabic text, stable IDs, numeric values and NULLs. Excel uses Data/Month/Source_Data/Daily and optional yearly files.
- NASA POWER and Open-Meteo ERA5 temperature/rainfall requests and raw-response caching implemented. Two-day live Cairo checks passed with two actual daily values for both elements and both providers. The ERA5-Land request returned missing rainfall, so the advertised first-slice provider uses tested ERA5 instead.
- Eight independent desktop tests passed, covering real GIS/Excel export, partial failures, missing values, leap years, per-year recalculation, UI selection preservation and the actual export-button/background-worker workflow.
- Legacy regression checks passed: station selection on Python 2.7 (17), runtime on Python 2.7 (19), station UI on Python 3 (3), and validation on Python 3 (10).
- Development EXE built and its own GIS/Excel self-test passed from a working directory outside the repository. It bundles its catalogue, Python/Qt/GDAL libraries and license notices. No ArcGIS paths or ArcPy import appear in packaged diagnostics.
- The build isolates its native DLL search path and requires a successful frozen GUI capture before replacing development. This prevents ambient Poppler ICU libraries from breaking Qt startup. The background worker preserves Qt's `QObject.event` method; export-button regression coverage protects queued worker startup.
- Native UI acceptance on this Windows machine passed: opened the development EXE, selected all 86 Egyptian stations, changed the output directory, clicked Export, observed completion, and checked Project.gdb, Project.gpkg and Stations.xlsx. Both spatial layers contain 86 features with successful coordinate/attribute readback. Test output is isolated under `.test-output/ui_workflow/`.
- Stable has not been promoted. Promotion requires the approved complete bundle hash and a fresh self-test.

### Still outstanding after the 0.2 expansion
- Clean Windows machine/VM acceptance and native ArcMap readback. Native ArcGIS Pro readback of all 20 NASA output feature classes at EPSG:32636 now passes.
- Exhaustive legacy parameter/field and raster-method parity; specialized isobars/wind-arrow/style/LYR workflows, project reopening/editor, and installer/uninstaller. Main interpolation, input/boundary import, reprojection and all 19 scientific module groups are now implemented; see the migration matrix.
- Independent geographical confirmation of the two flagged historical coordinate corrections.

This is a working first development delivery, not a claim that every master-plan feature is complete.

### Development 0.2 — expanded native workspace and hardening
- Replaced the schematic strip with a large native tile map: pan, wheel/button zoom, extent fit, point selection/picking, raster/line overlays, Esri labelled/unlabelled imagery, streets/topographic/gray basemaps and OSM. Esri imagery rendered successfully in live UI checks.
- Added optional official Google Map Tiles sessions and Microsoft Azure Maps connections with in-memory keys and viewport attribution. No live licensed-service test is claimed without credentials.
- Added persistent dark/light themes, a six-screen navigation structure, visible Add Data, F1 in-app guide, own point imports/coordinate entry, source CRS mapping, study-boundary filtering and regional grid generation.
- Vendored 38 pure scientific functions, with a reproducible extraction script and no parent-toolbox runtime import. Registered all 19 groups, provider dependencies, coverage, units, temporal scopes and yearly recomputation. Live Cairo checks exported all 19 NASA groups and 17 supported ERA5 groups; source gaps and insufficient trend history were correctly partial, not fabricated successes.
- Added actual selected-CRS FileGDB/GPKG geometries, metric/imperial summaries, IDW/nearest/TIN/spline/local exponential kriging, clipped GeoTIFFs, PDF pages and leave-one-out scores.
- All untrusted file parsing and substantial processing run as allowlisted JSON jobs in a child process. Added resource/input limits, defusedxml, bounded response streaming, cancellation timeout, per-job state/error/native-crash logs, and recovery after an abruptly killed worker.
- Add Data handles point/polygon/line/table/raster layers from FileGDB, GPKG, SHP, GeoJSON, SQLite, GeoTIFF, Excel/CSV. Missing CRS is explicit. Added Help with workflows, limitations and recovery steps.
- 17 automated tests pass. A 38-package advisory audit found zero known issues and skipped zero packages; native/application risks are not covered by that claim.
- Build gates include the frozen EXE's scientific/GIS/raster/PDF self-test, a GUI screenshot, and an actual GUI export through a second instance of the same EXE's processing mode. Development stays at its fixed path; stable remains unpromoted.
- Windows version resources identify Ahmad Ibrahim and MIRSAD Desktop. No available signing certificate exists; trusted publisher remains a separate release prerequisite.

### Local interface design proposal — 17 October 2026

- Added `docs/design/MIRSAD-Desktop-Concept.html`, a self-contained Arabic/English interface reference with embedded approved identity, 86 Egyptian catalogue records and the current 19-module registry snapshot. This is a design artifact, not another desktop application entry point or binary.
- Demonstrates station selection/search/sort, schematic map interaction, manual points, provider-specific availability, output planning, cancellable simulation, and explicit FileGDB partial failure. JSON plan save/load, a developer brief and a session log are real browser downloads; climate/GIS/Excel operations are explicitly simulations.
- `docs/design/README.md` records the implementation handoff, data provenance and limits. Original station data, scientific services, toolboxes and development/stable binaries were not changed by this design work.
- Verified the browser interactions for filtering/selection, provider availability, manual points, cancellation and partial output failure, plus JSON download/reload and Arabic/English. Responsive checks at 390/1440 CSS pixels showed no page overflow. Structural checks confirmed JavaScript syntax, unique HTML IDs, no external runtime assets and exact source parity for the embedded 86 records. Direct `file://` automation is blocked by browser policy; visual QA used local HTTP. See the design README and preview image for evidence.


### dev8 help and repository handoff — 19 October 2026

- Implemented 45-topic bilingual Qt/standalone/HTML/CHM help, with all 19 equation groups, 521 field mappings, native parameter references and explicit units/coverage examples. Concise map titles remain unchanged; methodology explains means of accumulations.
- Native Windows CHM Arabic and English display/search accepted; Qt search, language/topic preservation, bookmarks and PDF readback tested. Frozen help loads neither map nor ArcPy.
- Passed 58 Desktop tests, 16 isolated legacy suites (144 tests), 6 Python 2.7 suites (74 tests), native Pro parameter extraction, frozen export/workspace/help and installer install/uninstall/user-file-preservation gates.
- Development candidate 0.4.0.dev8 replaced only runtime/development after exact bundle-hash verification. Stable remains unpromoted. Added contributor instructions, issue/PR templates, isolated test runner, CI and explicit scratch cleanup evidence.
- Source/help implementation recorded in commit b8a97c4. Clean-checkout and remote handoff results are maintained in [DEV8_HELP_AND_REPOSITORY.md](docs/DEV8_HELP_AND_REPOSITORY.md).
- Native ArcMap processing, authenticated CDS/IMERG, advanced output/raster parity, complete DPI/accessibility matrix and visual acceptance of ArcGIS-native help summaries remain separate limits, not falsely closed by help tests.

- Remote handoff accepted: source commit e1f7c26 reached main, hosted deterministic CI and Pages deployment succeeded, and published CHM bytes match the local accepted guide. See the dev8 report for links and the documentation-only publication record.

### Field dictionary clarification — 19 October 2026

- Replaced generic equation-to-field explanations for all 521 fields / 19 modules with specific bilingual names, periods, calculation units and operations. Added field-name, identity, coverage and data-row dictionaries. Scientific functions, technical keys and concise map labels remain unchanged.
- Evidence and exact scope: [FIELD_REFERENCE_CLARIFICATION.md](docs/FIELD_REFERENCE_CLARIFICATION.md).
