# MIRSAD Desktop — implementation and maintenance

Source update, 22 October: [STATUS](docs/STATUS.md), [BACKLOG](docs/BACKLOG.md)
and [the enrichment tracker](docs/reports/climate-enrichment/IMPLEMENTATION_TRACKER.md)
supersede historical capability/test counts below. Desktop source includes the
11 additions, optional DEM, independent HG/PM and streaming XLSX. The 21 October
frozen candidate predates the subsequent source/help changes; the publicly
downloadable dev8 installer is older still (19 October). Do not describe either
binary as packaging current source. See [publication scope](../Documents/SOURCE_UPDATE_2026_10_22.md).

Read the root AGENTS.md, `docs/STATUS.md` and `docs/BACKLOG.md` first. Original product requirements are retained under `docs/architecture/` and `docs/design/reference/`. This file describes the development contract; it does not authorize publishing an unapproved release.

## Development history and current handoff — 19 October 2026

The detailed record is [docs/CHANGELOG.md](docs/CHANGELOG.md), with evidence in
[docs/reports/](docs/reports/). The root handoff records the shared chronology;
these are the Desktop-specific implementation decisions future work must retain.

1. **Foundation, 17 October:** audited the legacy data/contracts and created an
   independent x64 app, approved branding, embedded catalogue and FileGDB/GPKG/
   Excel exports. Vendored 38 pure calculations rather than importing ArcGIS.
   Early 0.1/0.2 milestones are dated local deliveries consolidated into the
   first source commit `b8a97c4` on 19 October.
2. **Workspace and isolation:** native map/layer controls, Add Data, coordinate
   and file inputs, study boundaries, multi-station selection, projected outputs,
   interpolation/GeoTIFF/PDF and read-only result previews. Bounded JSON workers
   isolate native parsing/calculation/export crashes; cancellation and a later
   successful job were tested. The browser design concept is a reference only,
   not the application engine or an additional executable.
3. **UI rework/dev1–dev4, 18 October:** neutral dark/light themes, native resize
   behavior, compact map navigation and basemap icon/gallery, transient outside-
   click dismissal, translated controls and guide. Removed Google/Microsoft/API-
   key basemap connections. Three tools own independent input/climate/raster/
   output drafts; switching tools retains them. Raster controls are explicit.
4. **CRS/dev5:** embedded Pro/Esri hierarchy, geographic/projected categories,
   continental/UTM branches and hemispheres, favorites, layer CRS and search.
   Read `docs/reports/CRS_BROWSER_REWORK.md`; missing datum grids still matter.
5. **Sources/dev6–dev7:** independent sources, staged station Hybrid, any-point
   Hybrid and per-variable/whole-interval Auto resolution. Implemented product
   adapters and native regional extraction; monthly/composite coverage remains
   explicit. Need Sign In is per source, with user credentials in memory/stdin,
   never saved to jobs/projects/logs. Live CDS/IMERG acceptance is still open.
6. **Help/dev8, 19 October:** 45 bilingual topics in native Qt, standalone mode
   of the same EXE, offline HTML and two real CHMs. Tree/search/favorites,
   history, font/theme controls and PDF/printing use the same content. Help-only
   launch does not import the map or ArcPy. Build-time CHM compiler is pinned,
   signature-checked and locally extracted with local COM activation; do not
   install/replace system DLLs or commit its binaries.
7. **Scientific field dictionary:** 19 groups/521 possible fields have formulas,
   source variables, coverage, examples and specific bilingual names/periods/
   units/operations. `ET_Annual_Mean` is the documented climatological PET sum;
   annual and monthly interannual ranges differ. Keep concise mean map names
   and explain accumulation in methodology. See commit `fd8dae1` and the field
   clarification report. Scientific functions and field names were not changed
   by that documentation correction.
8. **Header and repository:** `5856e98` limits the subtitle to the active
   language; `e356ff7` moves ArcGIS files to `../Toolboxes/`, renames shared
   support to `../mirsad_core/`, groups maintenance scripts and reorganizes docs.
   Completed/redundant plans became status/backlog/change log. Product/design
   requirements remain marked reference material, not fresh execution prompts.

## Current acceptance and unresolved work

- Version **0.4.0.dev8**; all current binary paths below are development unless
  an explicitly approved stable release is present. Later help/layout changes
  retained this version, so identify candidates by exact hashes as well.
- Latest organization baseline: **63 Desktop tests**, real frozen worker/GIS/
  raster/PDF/workspace/help gates and installer installation/readback/uninstall/
  user-file preservation passed. 18 packaged runtime modules matched source.
- A clean staged-source export passed asset/catalogue prep, scientific vendoring,
  help/contracts, documentation links and cold tool imports using the existing
  QA interpreter. This was not a new-environment full PyInstaller rebuild.
- Catalogue has 28,066 location records; preserve current country policy and
  station keys. Historical reports/design examples with 86 Egyptian stations
  do not override the current 85-entry display. No field verification is implied.
- Remaining: native ArcMap processing, exact advanced Toolbox/Desktop input/
  output/raster parity, authenticated CDS/IMERG, full DPI/accessibility matrix,
  ArcGIS-native help rendering and the documented legacy LST delta-unit defect.
  Keep these in `docs/BACKLOG.md`; do not describe the platform as fully accepted.

## Build, evidence and publication entry points

- `scripts/build_development.ps1 -PrepareOnly`: prepare/validate sources, assets
  and shared help, run tests, build and accept a candidate without replacing the
  current development app. Normal build replaces only after validation.
- `scripts/finalize_build.py --install-verified`: install the unchanged accepted
  candidate; it verifies the recorded bundle/EXE hashes before replacement.
- `scripts/build_installer.py` and `scripts/verify_installer.py`: build one
  development installer, exercise disposable QA installation and preserve user
  files. Never run a production install as an automated acceptance shortcut.
- `scripts/verify_packaged_source_equivalence.py`: read-only comparison of
  packaged Python against current source; do not execute extracted code.
- Shared help sources are in `../Documents/Help/`; generation uses
  `scripts/build_user_guide.py` and `scripts/build_chm.py`. Browser guides are in
  `docs/user/`; current reports are in `docs/reports/`. Do not recreate old plans
  or the retired flat report locations.
- The user explicitly authorized source/docs plus the current verified installer
  on GitHub on 19 October 2026. That candidate is a development prerelease, not
  a stable promotion. `../Documents/DEVELOPMENT_PUBLICATION.md` records the exact
  tag, source revision, installer checksum, acceptance and remaining limits.
  Runtime folders stay out of Git; publish binaries as release assets.

## Product requirements
- One Windows application with a professional, direct Arabic/English interface using the approved MIRSAD identity.
- No ArcGIS, ArcPy, toolbox path, ArcGIS Python, or ArcGIS DLL dependency at runtime.
- Bundle the station catalogue and identity assets in the executable distribution. Never fetch station data from a sibling toolbox at runtime.
- Export real Esri File Geodatabase feature classes and GeoPackage layers; daily nonspatial tables inside FileGDB are optional.
- Keep the legacy toolboxes and Desktop on an identified version of the same audited station catalogue.

## Exactly two fixed execution locations
- Development: `runtime/development/MIRSAD.exe`.
- Approved release: `runtime/stable/MIRSAD.exe`.
- Development builds replace the application at the development path. Do not create dated or numbered runnable copies.
- Build intermediates belong only in `.build/`; test files in `.test-output/`. These are disposable, not additional installed applications.
- A single promotion script copies the verified candidate to the fixed stable path only after explicit user approval. Compare candidate hashes and test reports before promotion.
- Stable must remain unchanged if development or promotion validation fails. Close the application before rebuilding its directory.
- Until a first release is approved, stable is reserved and clearly marked as not yet released; do not invent a stable binary.
- User projects and logs are outside the binary directories. Rebuilds and uninstall must preserve projects.

## Code organization
- `src/mirsad_desktop/`: application, services, UI, station catalogue, climate adapters, GIS/Excel exports.
- `assets/`: approved logo and embedded catalogue snapshot, with a source manifest.
- `scripts/`: reproducible audit, asset preparation, build, promotion, and release checks.
- `docs/`: architecture, methodology assessment, catalogue audit, compatibility and development notes.
- `tests/`: unit/integration tests and UI smoke checks. No separate experimental app entry points.
- `launcher.py`: the one application entry point, with explicit CLI diagnostic modes for automation.

## UI
- Tools are the product's primary navigation. Each tool owns its points, selection, source/period, modules, project name and processing draft; switching tools must preserve and isolate those drafts.
- Keep the map, layer/result tree, viewer tabs, input/climate/raster/output positions and progress controls fixed. Shared controls may render the active tool's draft; they must not become global mutable scientific settings.
- Start worldwide with no assumed country. Egypt is a case study and may be used explicitly in test fixtures, never as the default project, map extent, provider region or missing-country fallback. Preserve user deletions of case-study data/HTML.
- Use neutral charcoal dark tokens with MIRSAD accents and the approved identity; the local design folder is a reference, not a scientific implementation.
- Keep Add Data and Help visible. Enable raster outputs explicitly for a climate tool. The separate point-field raster wizard must not be presented as full parity with the legacy regional raster-download tool.
- Results are read-only previews. Parse spreadsheets/GIS/PDF in isolated jobs, bound pages, preserve original bytes and distinguish display layers from active tool inputs. Removing a view must never delete a dataset.
- Keep primary actions obvious. Show the selected station count, source, period, output path, progress, cancellation, and final result.
- Do not freeze the GUI during network or export work. Workers must return structured errors.
- Use real functionality; do not show an enabled button for an unimplemented workflow.
- Keep station selection stable across sorting/filtering; distinguish no selection from all filtered stations.
- Geography checks, station catalogue metadata, and source/provenance must be inspectable.

## Changes and verification
1. Read the current implementation and test evidence; identify affected UI and data contracts.
2. Define user-visible acceptance criteria and failure behavior before editing.
3. Implement and validate core services independently of Qt.
4. Test coordinate parity, stable IDs, CRS, field types, NULLs, Arabic strings, and export readback.
5. Test the packaged executable from a directory outside the repository and check that ArcGIS is absent from loaded module paths.
6. Visually inspect a UI screenshot and exercise the main workflow. Offscreen smoke checks alone are not proof of actual desktop usability.
7. Update `docs/STATUS.md`, `docs/BACKLOG.md` and `docs/CHANGELOG.md` with completed work and actual limitations. Put acceptance evidence in `docs/reports/`. A working first slice is not the whole climate atlas.
8. Rebuild only development. Report the fixed EXE path and evidence; wait for approval before promotion.
9. Build one candidate installer at `runtime/installers/development/MIRSAD-Setup.exe`. Installer smoke tests use disposable `.build/` space and a separate QA AppId. Never install a production copy or alter stable as part of a test. The normal per-user installer destination is one fixed `%LOCALAPPDATA%/Programs/MIRSAD`; the approved package remains in the stable distribution channel.

## Scientific and release controls
- Use deterministic fixtures and authoritative source references. Do not claim global station accuracy from geographic range checks.
- Preserve raw station/source fields and display normalization separately. Quarantine uncertain errors rather than moving stations automatically.
- Never treat GIS OIDs as permanent identity. Use station keys and a catalogue hash.
- Keep English field names/aliases by default; localized labels belong in the UI unless a localized export is explicitly selected.
- Every new climate module needs a registry entry, variables/dependencies, units, coverage, provenance, independent calculations, and export tests.
- Record dependency versions and third-party license notices with the distributed build.

## Input and crash boundaries
- Route file inspection, GIS parsing, downloads, exports and raster processing through the same EXE's allowlisted JSON worker mode. A native library failure must not terminate the UI.
- Never deserialize executable objects, use pickle/eval, run a shell from a job, or turn document contents into instructions.
- Add Data must accept local supported datasets, require a real source CRS when absent, and bound row counts, fields, geometry complexity, JSON/network sizes, raster cells and Excel expansion.
- Preserve input files. Refuse duplicate identities and existing project paths instead of silently removing/overwriting records.
- Keep API keys in memory and out of requests saved for processing, logs, manifests, repository and EXE resources. Use normal TLS validation.
- Retain job state/error/native-crash logs locally. Do not upload telemetry automatically. Bound the visible log and allow cancellation of a nonresponsive child.
- Test abrupt worker termination and a subsequent successful job, not just caught Python exceptions.
- Rerun a dependency advisory audit after dependency changes. State its package scope and date; do not claim that a clean package scan proves absence of native-library or application vulnerabilities.
- Windows CompanyName metadata is not Authenticode. Never create a fake trusted-publisher claim or disable OS protection to suppress warnings.
