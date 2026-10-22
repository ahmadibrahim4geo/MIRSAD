# MIRSAD documentation index

Updated: 22 October 2026. MIRSAD means **Meteorological Integrated Reanalysis Spatial Atlas Database**.

[العربية](00_Documentation_Index_AR.md) · [Website](../index.html) · [English help](../Help/MIRSAD_Help_EN.html) · [English CHM](../Help/MIRSAD_Help_EN.chm)

## Current implementation and downloads

The platform has 19 module groups and a reviewed dictionary of 521 possible legacy fields, plus optional enrichment fields described in each exported workbook. The shared catalogue contains 28,066 location records; catalogue agreement is not field verification. Output fields depend on the selected modules, periods and options.

Current source implements 11 optional daily variables, independent Hargreaves/Penman–Monteith calculations and streaming/split XLSX in Desktop and the point/station toolboxes. Desktop point workflows also support optional local/web DEM enrichment, preserving original elevations and declaring the model's surface type and datum. Complete-hour processing records the daily aggregation, UTC coverage and source in the output audit. Monthly/composite products do not become fabricated daily observations.

The publicly downloadable **0.4.0.dev8 installer is the 19 October build** and does not include these later source changes. Current help in this repository is newer than the release's CHM assets. A new binary candidate needs separate acceptance and publication; stable has not been promoted.

| Read first | Purpose |
|---|---|
| [22 October source update](SOURCE_UPDATE_2026_10_22.md) | Delivery scope, checks and outstanding work |
| [Current status](../MIRSAD%20Desktop/docs/STATUS.md) | Implemented workflows and binary distinction |
| [Backlog](../MIRSAD%20Desktop/docs/BACKLOG.md) | Unimplemented requirements and pending acceptance |
| [Enrichment tracker](../MIRSAD%20Desktop/docs/reports/climate-enrichment/IMPLEMENTATION_TRACKER.md) | Plan-to-evidence mapping |
| [Report index](../MIRSAD%20Desktop/docs/README.md) | Dated reports, hashes and test limits |
| [Publication record](DEVELOPMENT_PUBLICATION.md) | Exact public installer baseline and checksums |

## User guides and scientific references

- [English help centre](../Help/MIRSAD_Help_EN.html): current tool controls, methods, formulas, examples and units.
- [Source guide](07_Climate_Sources_Web_Guide/climate-sources.html?lang=en): implemented products, variables, periods, resolution, sign-in and tool capabilities.
- [English user guide](01_Markdown_Manuals/User_Guide_English.md).
- [Field/unit workbook](03_Excel_Dictionaries/Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx) and [cartographic classification workbook](03_Excel_Dictionaries/Climate_Atlas_Classification_Guide.xlsx): legacy reference assets; new optional output fields have their own Field_Dictionary sheets.
- [Adding a module](06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_EN.md), [Arabic companion](06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_AR.md) and [methodology review](../MIRSAD%20Desktop/docs/reports/METHODOLOGY_REVIEW.md).

The numbered manuals below retain historical explanations. Their older counts, provider claims and example layouts do not override current code, generated help or dated acceptance reports.

- [Overview](01_Markdown_Manuals/01_Executive_Overview.md).
- [Sources and provenance](01_Markdown_Manuals/02_Data_Sources_and_Provenance.md).
- [Processing pipeline](01_Markdown_Manuals/03_Processing_Pipeline.md).
- [Temporal aggregation](01_Markdown_Manuals/04_Temporal_Aggregation_and_Seasons.md).
- [Scientific formulas](01_Markdown_Manuals/05_Scientific_Formulas_All_Indicators.md).
- [Field reference](01_Markdown_Manuals/06_Field_by_Field_Reference.md).
- [Output schema](01_Markdown_Manuals/07_Output_Schema_and_File_Formats.md).
- [Missing data and QA](01_Markdown_Manuals/08_Missing_Data_QA_and_Gap_Filling.md).
- [Interpolation and raster](01_Markdown_Manuals/09_Spatial_Interpolation_and_Raster_Processing.md).
- [Assumptions and limits](01_Markdown_Manuals/10_Models_Assumptions_and_Limitations.md).
- [Worked examples](01_Markdown_Manuals/11_Examples_and_Hand_Calculations.md).
- [Online/offline workflows](01_Markdown_Manuals/12_User_Workflows_Online_Offline.md).
- [Validation reference](01_Markdown_Manuals/13_Validation_and_Testing.md).
- [Legacy field mapping](01_Markdown_Manuals/14_Field_Name_Legacy_Mapping.md).

## Development and acceptance

[Shared handoff](../AGENTS.md) · [Toolbox handoff](../Toolboxes/AGENTS.md) · [Desktop handoff](../MIRSAD%20Desktop/AGENTS.md) · [Testing](TESTING.md) · [Contributing](../CONTRIBUTING.md).

Toolbox DEM, regional enrichment, native raster/ArcMap acceptance, full optional-field help, the 1,000-point/30-year pipeline benchmark and complete DPI/accessibility remain open. Authenticated CDS/IMERG and other older parity requirements remain in the backlog. Pure Python compatibility tests and ArcPy doubles are not native ArcMap acceptance.
