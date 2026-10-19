# ArcGIS toolboxes

Developer handoff and completed work: [AGENTS.md](AGENTS.md).

Open these Python toolboxes from the Catalog pane in ArcMap or ArcGIS Pro:

| File | Purpose |
|---|---|
| `MIRSAD_Climate_Atlas_Generator_10_8.pyt` | Point climate atlas, English and Arabic tools |
| `MIRSAD_Weather_Stations_Atlas_Generator.pyt` | Weather-station climate atlas, English and Arabic tools |
| `MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt` | Regional grid/raster climate atlas, English and Arabic tools |

The same files support ArcMap/Python 2.7 and ArcGIS Pro/Python 3. They do not
require separate duplicated distributions. Raster tools appear only in their
dedicated toolbox.

Keep the repository layout intact: these entry points use sibling
[`mirsad_core`](../mirsad_core/README.md), `scripts/`, `data/`, `style/`,
`Weather_Stations_Hub/` and `Help/` in the repository root. Copying only this
folder is not a complete toolbox installation. Loading is independent of the
current working directory; add the checkout as a folder connection in ArcGIS.

`raster_atlas_generator.py` implements the raster tool. The `POWER_*.py` and
`NOAA_WMO_*.py` modules are compatibility entry points. XML files must stay
beside their matching `.pyt` files so ArcGIS can find tool help and metadata.

Former root-level toolbox paths moved here on 19 October 2026. Update saved
Catalog connections and automation paths. No duplicate root-level tools remain.
Existing project data and geodatabases were not migrated.

- [English offline guide](../Help/MIRSAD_Help_EN.html)
- [الدليل العربي](../Help/MIRSAD_Help_AR.html)
- [English CHM](../Help/MIRSAD_Help_EN.chm) / [Arabic CHM](../Help/MIRSAD_Help_AR.chm)
- [Testing and native-verification limits](../Documents/TESTING.md)
