# MIRSAD Desktop — implementation and maintenance

Read the root AGENTS.md, `docs/STATUS.md` and `docs/BACKLOG.md` first. Original product requirements are retained under `docs/architecture/` and `docs/design/reference/`. This file describes the development contract; it does not authorize publishing an unapproved release.

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
