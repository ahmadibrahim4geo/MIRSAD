# Test matrix and evidence

Reviewed 21 October 2026. Do not describe ArcPy doubles as native GIS verification.

| Layer | Command / environment | Meaning |
|---|---|---|
| Legacy deterministic suites | `python scripts/run_checks.py` after `pip install -r tests/requirements.txt` | Each suite in a separate process; no network/native ArcPy required. Logs and summary in `tests/.output/isolated/` |
| Climate enrichment baseline | `python scripts/audit_climate_enrichment.py` using the Desktop venv | Preserves pre-enrichment field values/order, missingness, Daily record hashes, sheets and legacy paths; reference capture refuses replacement. Not native acceptance or independent scientific validation. |
| Optional Desktop enrichment | `python -m unittest discover -s "MIRSAD Desktop/tests" -v` | Real new-variable/DEM/PM exports, missingness, method/raster selection, SI components and PM output units, hourly counts, source/UI isolation. Shared FAO expected values are in `tests/test_daily_climate.py`. |
| Optional Toolbox additions | `python scripts/run_checks.py --suite test_toolbox_enrichment.py` | 11 checks: EN/AR defaults/gating, strict coverage, canonical units, yearly XLSX, rejected hourly counts, zero/unknown elevation and identity/Arabic preservation; two Desktop comparisons require Python 3. |
| Native Toolbox additions | Licensed Pro Python: `python scripts/verify_toolbox_enrichment.py --kind points --output tests/.output/<fresh-name> --timeout 600` (repeat with `--kind stations`) | Actual Point/Station execution with synthetic offline source responses, 220 additional fields and native ExcelToTable. Does not establish live downloads, supplementary raster or ArcMap acceptance. [Evidence](../MIRSAD%20Desktop/docs/reports/climate-enrichment/TOOLBOX_ACCEPTANCE.md). |
| Large XLSX boundary | `python "MIRSAD Desktop/scripts/verify_excel_streaming.py"` | Writes/readbacks 1,000,001 data rows at the default million-row sheet limit. Not a full climate-download memory benchmark. |
| Legacy XLSX boundary | ArcMap Python: `python scripts/verify_legacy_excel_streaming.py --output <new-QA.xlsx>` | Actual million-row standard-library XLSX on Python 2.7; no openpyxl/ArcPy required. Does not establish ArcMap processing acceptance. |
| Native XLSX integration | Licensed ArcMap/Pro Python: `python scripts/verify_native_xlsx.py --output tests/.output/<new-QA-name> --timeout 180` | Native feature export and ExcelToTable; bounded subprocess records a timeout. Pro passed; ArcMap GP initialization remains open. |
| Enrichment live sample | `python "MIRSAD Desktop/scripts/verify_climate_enrichment_network.py" --live --output <new-QA-folder>` | Explicit 30N/31E February 2024 fixture, all extras, HG/PM and DEM through real Excel/GPKG/FileGDB; no protected account or frozen claim. |
| Enrichment Pro readback | Licensed Pro Python: `python "MIRSAD Desktop/scripts/verify_enrichment_native_readback.py" <QA-Project.gdb> --report <QA-report.json>` | Reads Desktop-authored new fields and checks default aliases; not native Toolbox execution. |
| Enrichment frozen worker | `python "MIRSAD Desktop/scripts/verify_enrichment_frozen.py" --exe <candidate-exe> --cache <recorded-fixture-cache> --output <new-QA-folder>` | Actual worker outside checkout with clean PATH and invalid proxy; verifies recorded public-source outputs without installing/replacing the app. |
| Candidate source identity | `python "MIRSAD Desktop/scripts/verify_packaged_source_equivalence.py" --exe <candidate-exe> --report <QA-report.json>` | Static comparison of 25 Python modules; no extracted code executed. |
| Legacy Python 2.7 | `python scripts/run_checks.py --python <ArcMap-python> --suite test_runtime_stability.py --suite test_tool_validation.py --suite test_climate_products.py --suite test_remote_grid.py --suite test_hybrid_pipeline.py --output tests/.output/python27` using a Python 3 runner | Explicit compatible test subset on Python 2.7; no claim of a native ArcPy import |
| Desktop | `python -m unittest discover -s "MIRSAD Desktop/tests" -v` with independent 64-bit Python 3.12/3.13 | Numerical, real Excel/GPKG/FileGDB readback, source fixtures, UI, jobs, failure boundaries; assets prepared first |
| Help contracts | `python scripts/check_repository.py` | Bilingual topics/CHM full-text stream, parameter snapshot, shared source equivalence, catalogue integrity |
| Native parameters | Licensed Pro Python: `python scripts/export_help_parameters.py` | Actual EN/AR `getParameterInfo`, not tool execution. 22 October final snapshot: 83 point, 90 station, 36 raster parameters; old parameters retain their positions |
| Native HG/PM | Licensed Pro Python: `python scripts/verify_toolbox_pm.py --output tests/.output/<fresh-name> --timeout 600` (repeat with `--kind stations`) | HG-only, PM-only and both; unchanged HG, FAO56 example18, monthly daily-sum equality and native ExcelToTable. Synthetic inputs; no raster/live-provider claim. [Evidence](../MIRSAD%20Desktop/docs/reports/climate-enrichment/TOOLBOX_PM_ACCEPTANCE.md). |
| Native processing | Explicit `tests/run_e2e_108.py`, `tests/verify_native_offline.py` and documented Desktop verification scripts | Require installed ArcGIS/licence and applicable extension. Inspect output paths/settings before running; not in generic CI |
| Live downloads | `MIRSAD Desktop/scripts/verify_*network.py` / source-specific verification scripts | Separate opt-in service checks; accounts/terms may be required. Never put credentials in command-line arguments or Git |
| Frozen EXE / installer | `scripts/build_development.ps1`, `scripts/build_installer.py`, `scripts/verify_installer.py` under Desktop | Actual executable from outside the repo, clean PATH; QA installer uses disposable location/AppId and preserves user files |

Do not run broad root `unittest discover`: that directory retains native, script-style acceptance programs as well as unit suites. Old scripts are retained for their coverage and host-specific purpose; confirmed generated scratch was removed, not test source. Four native scripts also have their obsolete parameter counts aligned with the native 69-parameter point contract; this does not claim those processing scripts ran. Five native scratch programs now write under `tests/.output/` instead of the repository root.

The dev8 cleanup repaired UTF-8 BOM handling in two test loaders, updated EN/AR toolbox registration and native parameter expectations, aligned provider/provenance/grid assertions with implemented source policies, and updated the audited Egypt display count to 85. It also fixed the actual specific-country picker regression after an invalid aggregate is cleared. Rainfall, NULL, units, identity and numerical assertions remain enforced. XLS readback dependencies are explicit; their absence must fail setup, not silently turn into a passing readback.

## Scientific and naming policy

“Mean precipitation” is a concise map title. The methodology explains that annual/seasonal climatic means average complete annual/seasonal accumulations. A title does not need to repeat all aggregation steps. Existing field names, map names and calculations are preserved by help edits.

Each equation page includes normalized input codes, units, its formula, actual field names, coverage rules and a worked example. `formula_review.json` detects stale calculation functions/constants; a maintainer must review scientific changes before updating it. Known host differences, including legacy non-Celsius `LST_minus_T_*` conversion, are disclosed rather than silently changed in a documentation update.

## Current native/account boundaries

See [dev7 native evidence](../MIRSAD%20Desktop/docs/reports/DEV7_SOURCE_ACCEPTANCE.md) and the dev8 help/repository report. Dev7 native Pro source/raster processing evidence remains useful; changing documentation does not rerun or expand it. Native ArcMap end-to-end acceptance and live authenticated CDS/IMERG acceptance remain unconfirmed. Full advanced raster/output parity is a separate open milestone. Stable is not promoted by these checks.


Clean-checkout acceptance at commit `625ced7` passed in a new independent venv installed from public PyPI with system site-packages disabled. All 16 legacy suites plus core export readback, both help suites, source/help contracts and standalone Arabic help passed. Legacy test scratch is owned by `tests/.output/`; Desktop tests create their `.test-output/` directory themselves. See the dev8 report for precise scope; a second full binary compilation was not performed in the clone.

Hosted [deterministic CI for source commit e1f7c26](https://github.com/ahmadibrahim4geo/MIRSAD/actions/runs/39193075315) completed successfully after publication. The final Markdown-only handoff record reuses this accepted source result.
