# Contributing to MIRSAD

[العربية](CONTRIBUTING_AR.md) · [User help](Help/index.html) · [Test matrix](Documents/TESTING.md)

MIRSAD contains three ArcGIS Python toolboxes and an independent Windows Desktop application. Contributions to documentation, accessibility, data-source adapters, numerical verification and GIS export readback are welcome. Desktop is a development candidate, not an approved stable release.

## Start from a clean checkout

Use Python 3.12 or 3.13, 64-bit, for Desktop. Keep ArcMap's Python 2.7 and ArcGIS Pro's licensed environment separate. From the repository root:

```powershell
py -3.12 -m venv 'MIRSAD Desktop/.venv'
& 'MIRSAD Desktop/.venv/Scripts/python.exe' -m pip install -r 'MIRSAD Desktop/requirements.txt'
& 'MIRSAD Desktop/.venv/Scripts/python.exe' -m pip install -r tests/requirements.txt
& 'MIRSAD Desktop/.venv/Scripts/python.exe' 'MIRSAD Desktop/scripts/vendor_science.py'
& 'MIRSAD Desktop/.venv/Scripts/python.exe' 'MIRSAD Desktop/scripts/prepare_assets.py'
& 'MIRSAD Desktop/.venv/Scripts/python.exe' 'MIRSAD Desktop/scripts/build_user_guide.py'
& 'MIRSAD Desktop/.venv/Scripts/python.exe' 'MIRSAD Desktop/launcher.py'
```

`requirements.lock` records the development build environment. The supported ranges in `requirements.txt` are the normal contributor installation entry point. Do not run pip against ArcGIS's managed environment to satisfy Desktop requirements.

The shared `data/stations.sqlite` snapshot and NOAA audit reference are versioned assets. Asset preparation verifies integrity and embeds a copy; Desktop never reads its parent toolbox directory at runtime. Do not regenerate the catalogue from a different source silently.

## Checks and a pull request

```powershell
& 'MIRSAD Desktop/.venv/Scripts/python.exe' scripts/run_checks.py
& 'MIRSAD Desktop/.venv/Scripts/python.exe' -m unittest discover -s 'MIRSAD Desktop/tests' -v
```

Legacy suites run in separate processes because their ArcPy doubles differ. Never use an all-files root discovery as a substitute: that folder also contains explicit licensed native scripts. Native Pro/ArcMap acceptance and live account downloads are distinct checks; ordinary CI does not establish them.

Use a focused branch and PR with the user-visible problem, final behavior, evidence and limits. Preserve Python 2.7 syntax in shared toolboxes and `utils/`. Put independent UI/runtime code only under `MIRSAD Desktop/`. Keep downloads, calculations, storage and UI separate. Follow [AGENTS.md](AGENTS.md) and the Desktop guide. Do not add generated test workspaces, virtual environments, credentials, application binaries, installers, or user project/data changes.

## Editing the bilingual help

Author topics in `Documents/Help/ar/` and `en/`, and register matching IDs in `topics.json`. Provider tables use the shared registry; parameter tables use the reviewed native snapshot. Equations use `formulas.json` plus the scientific field registry. Explain symbols, normalized inputs, exact output fields, units, coverage and a worked example. Map titles remain concise; aggregation details belong in methodology.

`build_user_guide.py` checks the reviewed calculation-function signatures. When a calculation changes, review the scientific consequences and expected-value tests before intentionally updating `formula_review.json`; do not bypass the check. Native parameter changes require `scripts/export_help_parameters.py` under licensed Pro. Normal help generation needs no ArcPy.

For Windows CHM compilation, prepare the build-time compiler once:

```powershell
& 'MIRSAD Desktop/.venv/Scripts/python.exe' 'MIRSAD Desktop/scripts/prepare_help_compiler.py' --download
& 'MIRSAD Desktop/.venv/Scripts/python.exe' 'MIRSAD Desktop/scripts/build_chm.py'
```

The downloader pins the Microsoft installer hash, validates its signature and extracts it locally. It does not install system DLLs or register global COM classes. Both CHMs must contain a full-text index. Verify Arabic text/search and English search in Windows, plus Desktop and browser help. Do not commit the compiler.

## Climate and data changes

Read the [English methodology](Documents/06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_EN.md), its Arabic companion and [current review](MIRSAD%20Desktop/docs/METHODOLOGY_REVIEW.md). Check historical claims against code.

Each source/element needs dependencies, actual units, temporal/spatial support, missing-value rules, provenance, independent expected values and failure tests. Missing precipitation is never zero. Retain station IDs as text, including leading zeros, and retain WBAN/location with USAF. Coordinate corrections require explicit evidence and a reproducible migration; never rewrite original geodatabases during an audit. A successful GeoPackage must not conceal a failed FileGDB export.

## Development package

Run `MIRSAD Desktop/scripts/build_development.ps1` only after preparing the CHM compiler. It validates assets/help, runs tests, builds and checks the actual EXE, then replaces only `runtime/development/`. Stable promotion and a public binary release require explicit approval of the tested candidate. See the test matrix for the acceptance boundaries; no release is published by CI.

Installer generation additionally requires a local Inno Setup compiler; `scripts/build_installer.py --compiler <ISCC.exe>` accepts its path. The compiler is a build tool, not a runtime dependency.
