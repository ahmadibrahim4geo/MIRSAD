# MIRSAD development guide

## Scope and project layout
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
- NASA POWER and Open-Meteo are implemented sources in the existing point tool. Do not advertise direct NOAA/Hybrid/CDS downloads without an implementation.
- Missing precipitation is not zero. Record aggregation coverage and scientific dependencies; add independent expected-value tests.
- Excel is the normal tabular output; report any CSV fallback. Preserve combined and optional individual-year exports.
- FileGDB and GeoPackage exports use the same calculated records and stable keys. A successful GeoPackage does not hide a failed FileGDB export.

## Git
- Stage only intentional source, tests, documentation, and validated reference assets.
- Keep virtual environments, temporary builds, user projects, credentials, and runtime output out of Git.
- Update the repository when the user requests it; attach any PR that is actually created.
