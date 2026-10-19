# Security and reliability — development 0.2

Reviewed 17 October 2026. This records implemented controls and evidence, not a guarantee of zero vulnerabilities.

## Boundaries implemented
- The UI launches its own EXE in an allowlisted `--run-job` mode. File inspection/import, GIS writes, downloads and interpolation execute in a child process; no pickle, eval, arbitrary command or shell protocol exists.
- Worker exit/crash is detected, journaled and reported; a recovery test kills a started worker and successfully runs the next export in the same UI. Cooperative cancellation has a 75-second termination fallback for that owned child.
- Local format whitelist: SHP, FileGDB directory, GPKG, GeoJSON, SQLite, GeoTIFF, XLSX, CSV/TSV. URLs and GDAL virtual paths are rejected. No uploaded document becomes executable instructions.
- Point batches are bounded to 20,000 records and 512 fields; coordinates and unique identities are checked. Geometry display and boundary complexity are bounded. Missing CRS requires assignment. Original files are not modified.
- Tabular/GeoJSON inputs are limited to 200 MB; Excel expansion to 512 MB and 20,000 ZIP members. `defusedxml` protects openpyxl XML parsing. No ZIP extraction is used.
- Climate JSON responses are streamed with a 64 MB cap and timeouts, using normal HTTPS certificate verification. Known providers have fixed endpoints.
- Raster processing defaults to at most 1,000,000 cells; local kriging to 250,000. Input and output coordinates are checked; GIS and raster outputs are reopened for verification.
- External text is plain text in errors, table previews and map tooltips. Excel source strings remain strings rather than formulas. Catalogue SQL uses parameter binding.
- User project names do not escape the chosen output folder; existing projects are refused. Requests use argument arrays with no shell. Job files, caches, binaries and logs are excluded from Git.
- Licensed basemap credentials are retained in memory, excluded from disk HTTP cache, processing requests and logs. Attribution is retrieved from the provider. Licensed services are not live-tested without credentials.
- Visible log blocks and stderr capture are bounded; job diagnostics are local and never uploaded automatically.

## Evidence
- 17 meaningful automated tests currently pass, including malicious/unsupported input rejection, duplicate IDs, projection readback, job allowlisting, abrupt worker termination and subsequent recovery.
- `pip-audit` 2.10.1 checked 38 installed Python distributions: zero advisory findings and zero skipped packages. Full JSON is generated under `.test-output/dependency_audit.json`; review the exact lock file when repeating.
- Bandit 1.9.4 scanned application sources and the launcher with no scan errors: zero medium/high findings and 11 low findings. Ten are legacy numeric-conversion/missing-value fallbacks in the generated scientific kernel (B110/B112), retained with scientific tests; they are not authentication/error-control bypasses. One is `os.startfile` (B606), used only to open the verified generated project directory on the user's action, with no shell arguments. The full report is `.test-output/code_audit.json`; these findings were reviewed, not silently suppressed.
- Live NASA/ERA5 downloads pass after response streaming limits. Esri basemap tiles render in the native UI. ArcGIS Pro reads all 20 NASA output feature classes at EPSG:32636.

## Practical limits
- The package audit does not cover every native Qt/GDAL/PROJ component, OS vulnerability, or unknown application defect. Native parsers still process untrusted data inside a child process. The process boundary reduces crash impact; it is not an OS sandbox or hard Windows memory quota.
- Clean Windows VM, prolonged workloads, native ArcMap readback and exhaustive advanced-tool parity remain additional acceptance work. ArcGIS Pro readback was completed; this is distinct from ArcMap.
- The current-user certificate store has no available code-signing certificate. Version metadata identifies Ahmad Ibrahim/MIRSAD but does not authenticate the publisher. Do not disable SmartScreen or fabricate trust.

## Maintainer checks
Run the automated tests and packaged self-test/UI worker test before replacing development. Rerun the package advisory audit after dependencies change, inspect worker journals for failures, update this record, and preserve stable until candidate approval. Never store certificate private keys or API keys in the repository.
