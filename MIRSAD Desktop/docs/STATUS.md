# Current Desktop status

Updated: 19 October 2026. Development version: **0.4.0.dev8**.

مرصاد Desktop نسخة تطوير مستقلة عن ArcGIS، وليست إصدارًا نهائيًا معتمدًا.
الأدوات والمساعدة تعمل بالمسارات الموضحة أدناه. المتبقي في [BACKLOG](BACKLOG.md)،
والتسليمات السابقة في [CHANGELOG](CHANGELOG.md).

## Implemented

- One independent Windows x64 application, Arabic/English workspace, light/dark
  themes, map, layer/result previews, CRS browser and isolated processing workers.
- Point, station and regional grid/raster workflows with separate tool drafts,
  scientific dependencies, output settings and provenance. Toolbox parity is
  still an explicit acceptance task, not implied by shared code.
- Embedded audited station snapshot: 28,066 location records, stable keys and
  source identity. Catalogue agreement is not field verification.
- NASA POWER and Open-Meteo plus the implemented product adapters documented
  in [source/resolution reference](reports/CLIMATE_SOURCES_AND_RESOLUTION.md).
  Hybrid orders NOAA GSOD, ERA5 and NASA download stages before monthly filling.
  Finest-suitable resolution is selected per variable within the chosen source.
- Excel, real FileGDB/GeoPackage and configured raster/atlas outputs. Partial
  failures and missing data remain explicit; missing precipitation is not zero.
- 45-topic Arabic/English Qt, standalone, HTML and CHM help, including 19 climate
  modules, 521 field definitions, formulas, units, coverage and numerical examples.
- Header subtitle uses only the active interface language. Root toolboxes now
  live in `Toolboxes/`; shared support is `mirsad_core/`. Desktop stays independent
  of both at runtime.

## Run and build

- Development: `runtime/development/MIRSAD.exe`.
- Development installer: `runtime/installers/development/MIRSAD-Setup.exe`.
- Public development preview: [0.4.0.dev8](https://github.com/ahmadibrahim4geo/MIRSAD/releases/tag/desktop-v0.4.0-dev.8),
  published with the Windows x64 installer, Arabic/English CHMs and SHA-256 manifest.
  [Publication evidence](../../Documents/DEVELOPMENT_PUBLICATION.md) identifies the exact candidate.
- Stable: `runtime/stable/` reserved; no approved stable binary has been published.
- Build: `scripts/build_development.ps1`; compile help from the shared source,
  verify the candidate outside the checkout, then replace development only.
  Preserve the full executable directory, including `_internal`.

## Evidence and boundaries

Native ArcGIS Pro 3.6 re-read the relocated toolboxes with **69/76/36** default
parameters (points/stations/raster). Parameter definitions are unchanged after
relocation. Pure calculation signatures, constants and emitted fields remain
unchanged. This does not claim native processing execution in ArcMap or Pro.

The [reorganization report](reports/REPOSITORY_REORGANIZATION.md) records current
layout checks and build acceptance. Prior accepted processing/help evidence and
hashes remain in [dev7](reports/DEV7_SOURCE_ACCEPTANCE.md),
[dev8](reports/DEV8_HELP_AND_REPOSITORY.md) and the
[field clarification](reports/FIELD_REFERENCE_CLARIFICATION.md).

Do not infer acceptance of authenticated CDS/IMERG downloads, complete advanced
output/raster parity, full DPI/accessibility coverage or ArcGIS-native help
rendering from successful unit tests. See the backlog for exact remaining work.
