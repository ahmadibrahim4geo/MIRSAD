# dev8 — bilingual help and repository readiness

Reviewed 19 October 2026. Development candidate **0.4.0.dev8**; stable remains unpromoted. This change does not close the separate advanced Toolbox/Desktop output and raster-option parity milestone.

## Implemented behavior

- One bilingual content source in `Documents/Help/`, consumed by native Qt help, the standalone help mode of the same EXE, offline browser HTML, and real Windows CHM. No extra application or runtime dependency on the parent toolbox is introduced.
- 45 topics per language: all three tools, source/coverage/sign-in policies, actual parameter references, workflows, failures, outputs and contributing; 21 equation/symbol/unit topics cover all 19 climate groups and 521 possible calculation fields.
- Each equation page explains source-variable codes, symbols, units, actual formulas, application order, exact output names, missing/coverage conditions, a numerical example and implementation references. Calculation-function/constant signatures and native parameter fingerprints fail help generation when stale.
- Concise map names such as “Mean precipitation” remain valid. Methodology states whether the mean averages annual/seasonal accumulations. No map/field renaming or silent scientific change was made to accommodate prose.
- Native Qt contents/search/favorites, history, language-preserving topics, font/theme controls and real print/PDF. Standalone help does not import map or ArcPy modules. Browser help has matching navigation/search/bookmarks and no external runtime scripts or server dependency.
- Windows CHM contents/index/full-text search/favorites are real, not a renamed HTML file. The compiler installer is pinned and its Microsoft Authenticode signature validated, then extracted locally; no system DLL replacement/global COM registration. Local CLSID **and ProgID** activation is required to produce the full-text stream. Compiler files stay outside Git/distribution.
- `utils/help_viewer.py` opens local CHM (HTML fallback) from ArcMap Python 2.7 or Pro Python 3 without Qt. Six per-tool XML summaries were intentionally updated, preserving other metadata. Native ArcGIS rendering of those summaries/links has not been visually accepted in this batch; parameter metadata was read from native Pro 3.6.
- Fixed the actual specific-country station picker regression: clearing an invalid aggregate country also disables/clears its picker. National aggregate scopes retain optional subset selection. This is UI validation, not a station-data migration.

## Actual acceptance evidence

| Check | Result |
|---|---|
| Independent Desktop suite | **58 tests passed**, 140.931 s, including numerical expected values, Excel/GPKG/FileGDB readback, process failures, tool drafts and help |
| Isolated legacy suites | **16 suites / 144 tests passed**; no shared ArcPy-double state |
| Python 2.7 compatibility | **6 suites / 74 tests passed**, including station selection, source barriers and product/grid protocols; not native ArcPy verification |
| Native parameter snapshot | Pro 3.6 read EN/AR parameter definitions: **69 point, 76 station, 36 raster**. No processing execution implied |
| Compiled Arabic CHM | Equations/Arabic visually read in Windows; full-text **الأمطار → 3 topics**, including rainfall equations |
| Compiled English CHM | Equations visually read in Windows; full-text **Rothfusz → 18 topics**, including Heat Index |
| Browser manual | Arabic normalized search, rainfall equation selection, language retains topic, bookmark survives reload; localhost used only for QA |
| Frozen EXE | GIS/science/raster/PDF self-test, GUI, worker exports and full workspace gates passed outside repo with clean PATH |
| Frozen help mode | Both languages passed; 45 topics, map_imported=false, arcpy_imported=false, real PDFs and screenshots inspected |
| Frozen source comparison | All 18 reviewed runtime modules, including userguide/themes, match source and source documentation |
| Installer QA | Payload readback, installed workspace, uninstall and user-file preservation passed with separate QA AppId; production installation unchanged |
| Added test dependencies | OSV query on 19 October: xlwt 1.3.0 and xlrd 2.0.2, zero reported advisories. Scope is these two test packages only; Desktop runtime dependencies unchanged |

Scratch evidence: `.test-output/dev8-build.log`, `packaged_help_ar/en.json/.png/.pdf`, `packaged_source_equivalence.json`, `installer_acceptance.json`; root `tests/.output/isolated/summary.json` and `python27/summary.json`. Screenshots are QA output, not required runtime assets.

## Cleanup and contribution setup

Removed 12 explicit generated scratch paths. Three small generated/abandoned files were retained locally for audit before removal from the root. No test source, Sample Data, user geodatabase or prior user deletion was removed/restored. Five native scratch scripts now write under `tests/.output/`. See `Documents/REPOSITORY_CLEANUP_2026_10_19.json` for paths, byte counts and hashes.

Repaired two UTF-8 BOM test loaders; updated obsolete toolbox registration/parameter/provider expectations and the audited Egypt display count. Added explicit XLS readback dependencies instead of skipping real readback. Current source checks run each legacy suite in a new process. Native scripts remain explicit licensed checks, not silently skipped unit successes.

Added Arabic/English contribution guidance, support/security/conduct policies, bug/idea/documentation/PR templates, a Windows deterministic CI workflow and a test matrix. Shared catalogue/reference files are intentionally versioned; environments, compiler tools, runtime EXE/installer payloads, caches and test output remain ignored. Source hash policy normalizes UTF-8/BOM/newlines to survive Git checkouts while retaining original native-audit byte hashes.

Public PyPI dependency resolution passed for the contributor requirements. Clean checkout and remote publication are recorded below when completed; a local passing suite is not a claim that GitHub Actions has run.

## Candidate hashes

| Artifact | SHA256 |
|---|---|
| Development EXE | `cb257b90888db12c8fd9a4932ea3035a3a8cf209e6072e8d64733424073e0cff` |
| Complete development bundle | `e8bc77433d02df98bdb0ed8a3c7cc60a7c29e55a77b8f03a909b3adb99d6a490` |
| Development installer | `6b9315a090147ee592d0cae42358fd10067c9d8323583b09b0762451b7dbf11a` |
| EN CHM | `fe180de29b9790c1153e7bf07f2f4d6b5b806768d55191671eb9a74f193edd34` |
| AR CHM | `a7ef55dc4a325d629eff8ca7ff0e3b36a2d6a4e973cbce85143f716724356f5c` |

## Remaining boundaries

- Native ArcMap end-to-end processing and live authenticated CDS/IMERG downloads remain unconfirmed; dev7 native Pro processing evidence is retained, not expanded by help tests.
- Full advanced raster/export parameter and file-schema parity remains separate. Pure shared calculations do not prove identical full workflows.
- The guide discloses the existing legacy non-Celsius LST-minus-air conversion difference; scientific fixes require a separate reviewed change.
- CHM content is bilingual; Windows viewer chrome follows installed Windows resources. Full 100/125/150/200% DPI and screen-reader acceptance was not completed here.
- Stable contains its reservation README only. No public binary Release, production installation or stable promotion was performed.

## Source handoff

Clean clone at commit `625ced7` passed all 10 handoff steps. It used a new venv with `include-system-site-packages=false`, dependencies installed from public PyPI, and clean PATH/PYTHONPATH. Source catalogue/science/assets/help generation, all 16 legacy suites, independent core export readback, the help-centre/equation tests, repository contracts and standalone Arabic help passed. The packaged EXE/installer gates above ran in the primary build workspace; a second full PyInstaller build inside the clone was deliberately not repeated.

The clean-checkout audit found and repaired two hidden scratch assumptions: five Desktop test modules now create their owned output directory, and three legacy suites use `tests/.output/` through a Python 2/3 helper instead of requiring Desktop scratch. The latter three suites also passed again on Python 2.7 (23 tests). No scientific assertion was relaxed.

Source implementation: `b8a97c4`. Contribution/readiness setup: `d66f181`. Fresh-checkout fixture fixes: `530a5c0`, `625ced7`. Native/user files excluded from these commits remain untouched in the working tree. Remote publication is verified separately in the final handoff; no GitHub Actions result is implied by this local evidence.
