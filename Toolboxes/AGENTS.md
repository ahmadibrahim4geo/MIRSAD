# ArcGIS Toolbox development handoff

Read `../AGENTS.md` first. Updated 19 October 2026. This scope covers the three
ArcGIS toolboxes, their compatibility modules and metadata. Shared runtime
support is `../mirsad_core/`; maintenance commands are `../scripts/`.

## Current files and separation

| Entry point | Registered tools |
|---|---|
| `MIRSAD_Climate_Atlas_Generator_10_8.pyt` | Point atlas, English and Arabic only |
| `MIRSAD_Weather_Stations_Atlas_Generator.pyt` | Weather-station atlas, English and Arabic |
| `MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt` | Regional grid/raster atlas, English and Arabic |

`raster_atlas_generator.py` implements the regional tool. `POWER_*.py` and
`NOAA_WMO_*.py` remain compatibility loaders. Do not register the regional tool
again in the point toolbox; its own optional interpolation/raster outputs are
still legitimate point-tool features. Preserve filenames, aliases, field keys
and English/Arabic registrations unless explicitly migrating them.

## Development already completed

- Preserved Python 2.7/ArcMap and Python 3/ArcGIS Pro support in the same files.
  No separate copied Pro and ArcMap toolboxes are needed.
- Added shared source policies/download adapters, ordered Hybrid phases,
  independent NOAA GSOD/ERA5 sources, per-variable Auto resolution, monthly
  products and protected-source controls. Regional native grids support POWER,
  CHIRPS and CHELSA according to the implementation; do not infer support from
  the longer point/station source list.
- Added stable station/country selection and multi-selection against the shared
  catalogue, retained USAF/WBAN/location identity and explicit-ID GHCN policy.
- Preserved complete-period rainfall rules, optional individual-year Excel,
  field/season filters, missing-value provenance and module-specific failures.
- ArcGIS interpolation materializes the identical valid points in owned scratch
  FileGDBs before Spatial Analyst calls, addressing error 010819/path spaces.
  Restore environments/licenses; raster failures must not become false success.
- Added bilingual per-tool help summaries and CHM/HTML access through
  `mirsad_core.help_viewer`; formulas/fields are explained by the shared guide.
- Relocated all entry points and XML from the root into this folder in commit
  `e356ff7`. Bootstrap resolves repository data/style/catalogue/calendar paths
  from the source file, not the user's current directory. The point compatibility
  loader uses `mirsad_point_toolbox` so it cannot shadow `mirsad_core`.

## Contracts future changes must preserve

- Python 2.7 syntax in runtime support and toolboxes: no f-strings, pathlib,
  dataclasses or Python-3-only imports on the ArcMap path. Keep explicit UTF-8
  coding declarations where source contains Arabic.
- Keep `.pyt.xml` files beside their matching toolboxes. Do not incidentally
  stage ArcGIS-generated metadata edits; two container XML modifications and
  two untracked XML files were intentionally left local during reorganization.
- The old `utils` package and root-level `.pyt` paths are retired. Do not add
  duplicate root stubs; update callers and saved ArcGIS folder connections.
- Keep the whole checkout layout for ArcGIS tools: shared support, `scripts/`,
  catalogue, style, station hub and help are sibling directories. Desktop stays
  independent and must not import this folder at runtime.
- Calculation functions remain in the point `.pyt`; the independent Desktop
  vendors 38 reviewed pure functions. Do not infer that renaming the shared
  support package moved all scientific formulas into it.
- For a scientific change, review both methodology languages, expected values,
  dependencies, missingness, units, field schemas and host-specific guards.
  Do not merely overwrite `formula_review.json` to satisfy a stale-review check.

## Verification and evidence

The reorganization baseline is 17 isolated suites / 146 tests and 7 Python 2.7
suites / 68 tests. Cold imports with explicit ArcPy doubles passed for all three
toolboxes and both compatibility modules from outside the checkout.

Native Pro 3.6 loaded the relocated files and extracted 69/76/36 parameter
definitions, identical to the prior native snapshot. The snapshot is
`../Documents/Help/tool_parameters.json`. Refresh it with
`../scripts/export_help_parameters.py` under licensed Pro when definitions change;
the normal help build deliberately requires no ArcPy.

Run isolated checks with `../scripts/run_checks.py`; the root guide describes
interpreter/dependency setup. Run native scripts explicitly and report exactly
which processing/exports were exercised. Native ArcMap processing and complete
advanced Desktop parity remain open. A mocked ArcPy run or parameter extraction
is not proof of native processing success.

Read the [reorganization report](../MIRSAD%20Desktop/docs/reports/REPOSITORY_REORGANIZATION.md),
[source integration evidence](../MIRSAD%20Desktop/docs/reports/DEV7_SOURCE_ACCEPTANCE.md),
[output contract audit](../MIRSAD%20Desktop/docs/reports/OUTPUT_CONTRACT_AUDIT.md),
and [remaining work](../MIRSAD%20Desktop/docs/BACKLOG.md) before changing contracts.
