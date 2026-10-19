# mirsad_core

Shared Python 2.7/3 support for the ArcGIS toolboxes. This package replaces the
former `utils` package; imports now use `from mirsad_core...`.

| Modules | Responsibility |
|---|---|
| `climate_sources`, `climate_products` | Provider capabilities, model/resolution selection and products |
| `hybrid_pipeline`, `protected_sources`, `remote_grid` | Ordered downloads, provenance and protected/grid protocols |
| `climate_quality`, `station_catalogue` | Input quality, stable station keys and catalogue reads |
| `arcgis_runtime` | ArcGIS environment, licenses, errors and export boundaries |
| `calendar_dialog`, `help_viewer` | Calendar and offline-help support |

This name does not mean every scientific formula lives here. The legacy pure
calculation functions remain in
[`Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt`](../Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt).
Desktop vendors the reviewed pure functions and selected adapters into its own
source and package; it never imports this sibling package at runtime.

Maintenance generators are in `scripts/styles/`, `scripts/documentation/`,
`scripts/stations/` and `scripts/data/`. They are explicit developer commands,
not imports needed to run the climate tools. Moving files has not authorized
running maintenance commands against existing user datasets.
