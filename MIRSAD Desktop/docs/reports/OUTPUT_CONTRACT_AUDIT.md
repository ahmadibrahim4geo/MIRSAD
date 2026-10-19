# Output contract audit

Static audit of current declarations and a complete two-year fixture with monthly ranges enabled; no complete runtime parity is claimed.

| Module | Legacy fields | Desktop fields | Missing declared fields |
|---|---:|---:|---|
| Temperature | 34 | 34 | None |
| Land Surface Temperature | 35 | 35 | None |
| Precipitation | 30 | 30 | None |
| Sea Level Pressure | 30 | 30 | None |
| Surface Pressure | 30 | 30 | None |
| Wind | 49 | 49 | None |
| Relative Humidity | 30 | 30 | None |
| Dew Point | 30 | 30 | None |
| Solar Radiation | 31 | 31 | None |
| UV Index | 30 | 30 | None |
| Cloud Cover | 30 | 30 | None |
| Heat Index | 19 | 19 | None |
| Wind Chill | 18 | 18 | None |
| De Martonne Aridity | 1 | 1 | None |
| Evapotranspiration | 31 | 31 | None |
| UNEP Aridity | 1 | 1 | None |
| Water Deficit | 1 | 1 | None |
| Dry Months | 1 | 1 | None |
| Trends & Anomalies | 90 | 90 | None |

Legacy metadata absent from the current Desktop property contract: Cell_Size, Interp_Meth, Source_ID, Temporal, Wind_Cell

Remaining validation/change scopes: Exact metadata names/types/order; Input attribute retention and station identifier mappings; Daily wide versus long table layout; Legacy short filenames/folders and .xls versus Desktop .xlsx; Advanced submodel/field filters and raster parameter mapping; Native ArcMap runtime and approved interpolation tolerances

Scientific calculations and shared source code do not establish identical file schemas. See OUTPUT_CONTRACT_AUDIT.json for every declared field.
