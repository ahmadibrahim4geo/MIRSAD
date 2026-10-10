# Technical Specification: Copernicus Climate Data Store (CDS / ERA5 / AgERA5)

## 1. Overview and Institutional Mandate
The **Copernicus Climate Data Store (CDS)** is the flagship data dissemination portal of the **Copernicus Climate Change Service (C3S)**, implemented by the **European Centre for Medium-Range Weather Forecasts (ECMWF)** on behalf of the European Commission.

In **MIRSAD (منظومة مِرصاد)**, Copernicus CDS represents the 5th official climatological data source, powering both the **Spatial Climate Atlas Generator (Points)** and the **Gridded & Raster Climate Atlas Generator (Rasters)**.

---

## 2. Model Architecture & Data Products
### A. ECMWF ERA5 Global Atmospheric Reanalysis
- **Core Model Cycle:** IFS Cy41r2 (Integrated Forecasting System).
- **Data Assimilation:** Advanced 4D-Var (Four-Dimensional Variational Data Assimilation) assimilating conventional surface stations, radiosondes, aircraft observations, and modern satellite radiances.
- **Native Spatial Resolution:** TL637 (~31 km / 0.25° grid).
- **Vertical Coverage:** 137 model levels from surface up to 0.01 hPa (~80 km altitude).
- **Temporal Horizon:** January 1, 1940 to present.

### B. ECMWF ERA5-Land Terrestrial Surface Reanalysis
- **Land Surface Scheme:** H-TESSEL (Tiled ECMWF Scheme for Surface Exchanges over Land with improved hydrology).
- **Spatial Resolution:** 0.10° (~9 km on the equator, ~11 km in mid-latitudes).
- **Topographic Downscaling:** Elevation-adjusted thermodynamic downscaling using high-resolution digital elevation models (DEM) with local lapse-rate temperature adjustments.
- **Temporal Horizon:** January 1, 1950 to present.

### C. AgERA5 Agricultural Indicators
- **Focus:** Daily surface meteorological variables tailored for agricultural modeling, crop phenology, and agroclimatological risk assessments.
- **Spatial Resolution:** 0.10° regular latitude-longitude grid.
- **Temporal Horizon:** January 1, 1979 to present.

---

## 3. Parameter Mapping in MIRSAD
| MIRSAD Climatological Element | CDS / ERA5 Parameter | Units & Representation |
| :--- | :--- | :--- |
| **Temperature** | `2m_temperature`, `maximum_2m_temperature`, `minimum_2m_temperature` | °C (converted from K) |
| **Precipitation** | `total_precipitation` | mm / day or mm / month (converted from m) |
| **Wind** | `10m_u_component_of_wind`, `10m_v_component_of_wind`, `10m_wind_speed` | m/s, wind direction degrees |
| **Relative Humidity & Dew Point** | `2m_dewpoint_temperature`, calculated with Magnus-Tetens from $T$ and $T_d$ | % and °C |
| **Sea Level Pressure** | `mean_sea_level_pressure` | hPa (converted from Pa) |
| **Surface Pressure** | `surface_pressure` | hPa (converted from Pa) |
| **Solar Radiation** | `surface_solar_radiation_downwards` (SSRD) | kWh/m²/day or MJ/m²/day (converted from J/m²) |
| **Cloud Cover** | `total_cloud_cover` | Octas (0-8) or Percentage (0-100%) |
| **Soil Temperature** | `soil_temperature_level_1` to `4` | °C (0-7, 7-28, 28-100, 100-255 cm) |
| **Soil Moisture** | `volumetric_soil_water_layer_1` to `4` | m³/m³ |
| **Evapotranspiration** | `potential_evapotranspiration` / FAO-56 Penman-Monteith | mm / day |

---

## 4. Integration in MIRSAD Tools
### 1. Spatial Climate Atlas Generator (`MIRSAD_Climate_Atlas_Generator_10_8.pyt`)
- Parameter: `Climate_Data_Source = "Copernicus Climate Data Store (CDS / ERA5 / AgERA5)"`
- Reanalysis Model parameter: `OpenMeteo_Model` active (ERA5-Land ~9 km, ERA5-Seamless, ERA5 Standard).
- Optional Token: `CDS_API_Key` for personal access token.
- Seamless fallback: zero-login gateway ensures 100% successful downloads without authentication failures.
- Dedicated output in `Source Data/`: complete provenance documentation in Excel and CSV.

### 2. Gridded & Raster Climate Atlas Generator (`raster_atlas_generator.py`)
- Parameter: `Climate_Data_Source = "Copernicus Climate Data Store (CDS / ERA5 / AgERA5)"`
- Optional Token: `CDS_API_Key` supported.
- Tiled Regional NetCDF Extraction: extracts gridded tiles, generates 32-bit Float GeoTIFF rasters, applies Jenks natural breaks classification, and builds multi-sheet Excel workbooks.

---

## 5. Scientific Citation
When publishing work derived from Copernicus CDS in MIRSAD, cite:
> Hersbach, H., Bell, B., Berrisford, P., et al. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049. https://doi.org/10.1002/qj.3803
> Muñoz-Sabater, J., Dutra, E., Agustí-Panareda, A., et al. (2021). ERA5-Land: A state-of-the-art global reanalysis dataset for land applications. *Earth System Science Data*, 13(9), 4349–4383. https://doi.org/10.5194/essd-13-4349-2021
