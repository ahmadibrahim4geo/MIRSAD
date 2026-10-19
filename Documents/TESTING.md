# Test matrix and evidence

Reviewed 19 October 2026. Do not describe ArcPy doubles as native GIS verification.

| Layer | Command / environment | Meaning |
|---|---|---|
| Legacy deterministic suites | `python scripts/run_checks.py` after `pip install -r tests/requirements.txt` | Each suite in a separate process; no network/native ArcPy required. Logs and summary in `tests/.output/isolated/` |
| Legacy Python 2.7 | `python scripts/run_checks.py --python <ArcMap-python> --suite test_runtime_stability.py --suite test_tool_validation.py --suite test_climate_products.py --suite test_remote_grid.py --suite test_hybrid_pipeline.py --output tests/.output/python27` using a Python 3 runner | Explicit compatible test subset on Python 2.7; no claim of a native ArcPy import |
| Desktop | `python -m unittest discover -s "MIRSAD Desktop/tests" -v` with independent 64-bit Python 3.12/3.13 | Numerical, real Excel/GPKG/FileGDB readback, source fixtures, UI, jobs, failure boundaries; assets prepared first |
| Help contracts | `python scripts/check_repository.py` | Bilingual topics/CHM full-text stream, parameter snapshot, shared source equivalence, catalogue integrity |
| Native parameters | Licensed Pro Python: `python scripts/export_help_parameters.py` | Actual EN/AR `getParameterInfo`, not tool execution. Latest snapshot: 69 point, 76 station, 36 raster parameters |
| Native processing | Explicit `tests/run_e2e_108.py`, `tests/verify_native_offline.py` and documented Desktop verification scripts | Require installed ArcGIS/licence and applicable extension. Inspect output paths/settings before running; not in generic CI |
| Live downloads | `MIRSAD Desktop/scripts/verify_*network.py` / source-specific verification scripts | Separate opt-in service checks; accounts/terms may be required. Never put credentials in command-line arguments or Git |
| Frozen EXE / installer | `scripts/build_development.ps1`, `scripts/build_installer.py`, `scripts/verify_installer.py` under Desktop | Actual executable from outside the repo, clean PATH; QA installer uses disposable location/AppId and preserves user files |

Do not run broad root `unittest discover`: that directory retains native, script-style acceptance programs as well as unit suites. Old scripts are retained for their coverage and host-specific purpose; confirmed generated scratch was removed, not test source. Four native scripts also have their obsolete parameter counts aligned with the native 69-parameter point contract; this does not claim those processing scripts ran. Five native scratch programs now write under `tests/.output/` instead of the repository root.

The dev8 cleanup repaired UTF-8 BOM handling in two test loaders, updated EN/AR toolbox registration and native parameter expectations, aligned provider/provenance/grid assertions with implemented source policies, and updated the audited Egypt display count to 85. It also fixed the actual specific-country picker regression after an invalid aggregate is cleared. Rainfall, NULL, units, identity and numerical assertions remain enforced. XLS readback dependencies are explicit; their absence must fail setup, not silently turn into a passing readback.

## Scientific and naming policy

“Mean precipitation” is a concise map title. The methodology explains that annual/seasonal climatic means average complete annual/seasonal accumulations. A title does not need to repeat all aggregation steps. Existing field names, map names and calculations are preserved by help edits.

Each equation page includes normalized input codes, units, its formula, actual field names, coverage rules and a worked example. `formula_review.json` detects stale calculation functions/constants; a maintainer must review scientific changes before updating it. Known host differences, including legacy non-Celsius `LST_minus_T_*` conversion, are disclosed rather than silently changed in a documentation update.

## Current native/account boundaries

See [dev7 native evidence](../MIRSAD%20Desktop/docs/DEV7_SOURCE_ACCEPTANCE.md) and the dev8 help/repository report. Dev7 native Pro source/raster processing evidence remains useful; changing documentation does not rerun or expand it. Native ArcMap end-to-end acceptance and live authenticated CDS/IMERG acceptance remain unconfirmed. Full advanced raster/output parity is a separate open milestone. Stable is not promoted by these checks.
