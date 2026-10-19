# MIRSAD development guide

## Start here — development handoff, 19 October 2026

This file is the shared handoff for future maintainers. Read it together with
[Toolboxes/AGENTS.md](Toolboxes/AGENTS.md) for ArcGIS work or
[MIRSAD Desktop/AGENTS.md](MIRSAD%20Desktop/AGENTS.md) for the independent app.
The development conversation is not required context: current state, history,
contracts, commands and outstanding acceptance are recorded in the repository.

- Current implementation: [Desktop status](MIRSAD%20Desktop/docs/STATUS.md).
- Outstanding requirements: [backlog](MIRSAD%20Desktop/docs/BACKLOG.md).
- Detailed dated history: [change log](MIRSAD%20Desktop/docs/CHANGELOG.md).
- Acceptance reports and hashes: [report index](MIRSAD%20Desktop/docs/README.md).
- Shared methodology: `Documents/Help/`, the bilingual adding-a-module guides,
  and `MIRSAD Desktop/docs/reports/METHODOLOGY_REVIEW.md`.

Current source before this handoff: `e356ff7`. Earlier local development took
place on 17–18 October; the first consolidated Desktop/source/help commit was
`b8a97c4` on 19 October. Do not infer separate commits for every earlier local
milestone, or treat dated historical limitations as the current capability list.

## What has been implemented

| Milestone | Delivered behavior and traceability |
|---|---|
| Legacy tools and Desktop foundation | Preserved ArcMap/Python 2.7 and Pro/Python 3; created one independent Windows x64 PySide6/Qt application, embedded identity/catalogue, real Excel/FileGDB/GeoPackage outputs and reproducible vendoring of 38 pure scientific functions. Desktop has no runtime dependency on ArcGIS or a parent toolbox. See the change log and architecture documents. |
| Catalogue audit | Shared deterministic `data/stations.sqlite` plus manifest and embedded Desktop copy, stable station keys, source-country identity and coordinate QA. Current catalogue has 28,066 location records. Earlier reports with 86 Egyptian entries are historical; current displayed subset is 85. Catalogue agreement is not field verification; flagged discrepancies remain explicit. |
| Native workspace and process isolation | Map/layers, Add Data, own points, study boundaries, CRS selection, read-only result previews and isolated JSON processing workers. Native failures, cancellation and partial export outcomes are reported without discarding successful files. |
| UI/tool separation | Three distinct point/station/regional-grid workflows, independent drafts, compact map/basemap controls, persistent native sizing, consistent Arabic/English and light/dark styling. Removed Google/Microsoft/API-key basemap connections. The header subtitle shows only the active language. |
| CRS browser | Embedded the ArcGIS Pro 3.6 hierarchy (7,519 entries) and separate official Esri catalogue (9,185 definitions), geographic/projected branches, UTM subdivisions, favorites and layer CRS. Catalogue presence is not proof of every datum transformation. |
| Shared sources and Hybrid | Independent NOAA GSOD/ERA5 and staged station Hybrid; finish NOAA across the selected network, then ERA5 missing cells, then declared NASA fallback, then optional monthly estimates. Any-point Hybrid skips NOAA observations. Existing valid higher-priority data and provenance remain unchanged. See `mirsad_core/` and the Hybrid architecture report. |
| Products and resolution | Implemented POWER/Open-Meteo, CHIRPS, TerraClimate, CHELSA, MODIS day/night, explicit-ID GHCN, and protected CDS/IMERG adapters. Auto chooses the finest suitable product per variable within the selected source and whole interval. Product/variable/region/period capabilities are authoritative in code. Native CHIRPS/CHELSA regional extraction is implemented; not every point product supports the regional tool. |
| Accounts and missing data | Need Sign In identifies protected sources. CDS uses a personal token; IMERG uses the user's Earthdata credentials. Desktop secrets stay in memory and use worker stdin. Monthly/composite products do not fabricate daily observations. Missing rainfall is never zero. Live authenticated CDS/IMERG acceptance remains pending. |
| Help and scientific dictionary | One bilingual source generates Qt/standalone/browser/CHM help: 45 topics, 19 module groups and 521 possible fields, formulas, inputs, units, coverage and worked examples. Each field has its own name, period, unit and operation. Annual range and same-month interannual range are distinct. Concise mean map titles are retained when averaging period accumulations; legacy PET Mean keys carry the documented climatological sums. |
| Contribution and organization | Added contributor/security/support guidance, CI, isolated legacy checks and clean-checkout acceptance. Moved entry points/XML to `Toolboxes/`, renamed `utils` to `mirsad_core`, separated maintenance scripts, categorized Desktop docs and consolidated obsolete execution plans without discarding remaining requirements. See `e356ff7` and the reorganization report. |

The implementation table is not a claim of complete Toolbox/Desktop parity.
Read the current backlog before asserting that an option, file schema, native
runtime or authenticated provider has been accepted.

## Latest accepted baseline

- 17 isolated legacy suites / 146 tests; 63 Desktop tests; 7 Python 2.7 suites /
  68 compatibility tests. These are separate scopes, not a sum of unique tests.
- Native Pro 3.6 re-read relocated definitions: 69 point, 76 station, 36 raster
  parameters, unchanged after reorganization. This is not native processing.
- Reviewed calculation functions/constants/521 field keys unchanged; shared
  adapters byte-identical across hosts. Clean staged-source export passed asset
  preparation, scientific vendoring, guide/contracts, 111 documentation links
  and fresh-interpreter imports from outside the checkout.
- Development EXE, clean-PATH worker/workspace/help gates and installer
  install/readback/uninstall/user-file-preservation passed. Exact current
  artifact hashes are in the reorganization report and publication manifest.
- Native ArcMap processing, complete advanced output/raster parity, authenticated
  CDS/IMERG, full DPI/accessibility and ArcGIS-native help rendering remain open.
  The legacy LST-minus-air Fahrenheit/Kelvin offset issue is documented, not
  silently repaired. Stable has not been promoted.

## Reproducible entry points

Use the independent Desktop `.venv` (Python 3.12 x64) for Desktop checks/builds,
and a compatible licensed ArcGIS Python for native checks. From repository root:

```powershell
& 'MIRSAD Desktop/.venv/Scripts/python.exe' scripts/run_checks.py
& 'MIRSAD Desktop/.venv/Scripts/python.exe' scripts/check_repository.py
& 'MIRSAD Desktop/.venv/Scripts/python.exe' -m unittest discover -s 'MIRSAD Desktop/tests' -v
```

Legacy Excel tests additionally require `tests/requirements.txt`; they are not
Desktop runtime dependencies. Native commands and exact coverage are in
`Documents/TESTING.md`. Source generation uses
`MIRSAD Desktop/scripts/vendor_science.py`, `prepare_assets.py` and
`build_user_guide.py`. The build command is documented in Desktop's handoff.

## Scope and project layout
- ArcGIS entry points and matching metadata live in `Toolboxes/`; shared Python 2.7/3 support is `mirsad_core/`. Maintenance generators live under `scripts/`.
- The existing Python toolboxes support ArcMap/Python 2.7 and ArcGIS Pro/Python 3. Preserve those runtimes.
- The independent application lives only in `MIRSAD Desktop/`. Read its `AGENTS.md` before changing it.
- Preserve user changes in Sample Data, geodatabases, and ArcGIS-generated XML. Never stage them incidentally.
- The approved identity is described in `assets/README.md`; reuse the existing logo and developer information.

## Development workflow
1. Inspect Git status, relevant code, actual data contracts, and applicable documentation.
2. State the intended behavior and any assumption that affects results. Record decisions and evidence, not private deliberation.
3. Implement the smallest complete usable workflow. Keep downloads, calculations, persistence, and UI separate.
4. Add meaningful checks for scientific correctness, compatibility, data preservation, and failures. Do not equate mocked ArcPy with native verification.
5. Review the diff, run relevant checks, update documentation, and report actual results and outstanding limits.
6. Do not change sources, coordinates, units, or missing-value rules silently. Keep raw observations and provenance.
7. Do not publish a release or promote development to stable without the user's explicit approval of that candidate.

## Shared station data
- Audit geographic coordinates against geometry, CRS, other repository copies, and an identified external reference when accessible.
- USAF alone is not a unique station key; retain WBAN and location. Preserve identifiers as text, including leading zeros.
- Range checks and agreement with a catalogue are not field verification. Separate confirmed errors, source discrepancies, duplicates, and unverified records.
- Preserve source country codes separately from MIRSAD display/region policy. Do not infer coordinate corrections from country labels.
- Generate the shared catalogue deterministically with a version/hash and an audit manifest. Embed a snapshot in Desktop; Desktop must never require a parent toolbox directory.
- Do not rewrite original geodatabases during an audit. Apply confirmed corrections through an explicit reproducible migration, with before/after evidence.

## Climate methods and exports
- Read the Arabic and English guides under `Documents/06_Methodology_Adding_New_Climate_Module/` together with the Desktop methodology review. Historical parameter counts and provider claims must be checked against code.
- Provider support must agree with the implemented adapters and per-tool capability registry. Distinguish an implemented protocol from live authenticated/native acceptance; do not revive old reports that describe currently implemented adapters as absent.
- Missing precipitation is not zero. Record aggregation coverage and scientific dependencies; add independent expected-value tests.
- Excel is the normal tabular output; report any CSV fallback. Preserve combined and optional individual-year exports.
- FileGDB and GeoPackage exports use the same calculated records and stable keys. A successful GeoPackage does not hide a failed FileGDB export.

## Git
- Stage only intentional source, tests, documentation, and validated reference assets.
- Keep virtual environments, temporary builds, user projects, credentials, and runtime output out of Git.
- Update the repository when the user requests it; attach any PR that is actually created.

## Publication authorization for this handoff

On 19 October 2026 the user explicitly requested source, documentation and the
current development installer on GitHub. Publish that verified candidate as a
clearly identified development prerelease; this does not authorize stable
promotion, a production installation or publishing future unreviewed binaries.
Keep EXE/installers as release assets rather than committing runtime/build
folders. Record source revision, SHA-256 values, checks and known limits. The
publication record is `Documents/DEVELOPMENT_PUBLICATION.md`.
