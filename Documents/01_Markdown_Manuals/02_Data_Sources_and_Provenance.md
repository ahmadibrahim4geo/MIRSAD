# 02. Data Sources and Provenance
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. NASA POWER Data Architecture

The **NASA Prediction of Worldwide Energy Resources (POWER)** project is an initiative funded by the NASA Earth Science Applied Sciences Program. It synthesizes global satellite observations and atmospheric reanalysis models to provide meteorological and solar energy parameters tailored for renewable energy, building efficiency, and agroclimatology.

### 1.1 Underlying Models and Sensors

NASA POWER merges two primary NASA Earth observing systems:

1. **MERRA-2 (Modern-Era Retrospective analysis for Research and Applications, Version 2)**:
   - **Provider**: NASA Global Modeling and Assimilation Office (GMAO).
   - **Model Core**: Goddard Earth Observing System Atmospheric Model (GEOS-5.12.4) coupled with the 3D-Var Gridpoint Statistical Interpolation (GSI) analysis system.
   - **Native Spatial Resolution**: $0.5^\circ \text{ latitude} \times 0.625^\circ \text{ longitude}$ (approximately $50 \times 60\text{ km}$ at subtropical latitudes).
   - **Temporal Coverage**: 1980 to within a few weeks of real time.
   - **Atmospheric Assimilation**: Ingests millions of observations daily from microwave sounders (AMSU-A, ATMS), infrared sounders (AIRS, IASI, CrIS), radiosondes, aircraft, GPS radio occultation, and satellite scatterometers.
   - **Provided Variables**: Screen temperature ($T_{2M}$, $T_{max}$, $T_{min}$), precipitation flux ($PRECTOTCORR$), barometric pressure ($PS$), surface wind vectors ($U_{2M}$, $V_{2M}$, $WS_{10M}$), and relative humidity ($RH_{2M}$).

2. **CERES (Clouds and the Earth's Radiant Energy System) & FLASHFlux**:
   - **Sensors**: Scanning radiometers aboard NASA Terra, Aqua, and Suomi-NPP satellites measuring broadband reflected solar and emitted thermal radiances.
   - **FLASHFlux (Fast Longwave and SHortwave Fluxes)**: Rapid-release radiative transfer algorithm providing surface shortwave solar insolation on a $1.0^\circ \times 1.0^\circ$ global grid.
   - **Provided Variables**: All-sky surface downward shortwave irradiance ($ALLSKY\_SFC\_SW\_DWN$) and noon UV index ($ALLSKY\_SFC\_UV\_INDEX$).

### 1.2 NASA POWER API Technical Implementation

- **API Endpoint**: `https://power.larc.nasa.gov/api/temporal/`
- **Sub-Endpoints**:
  - `hourly/point`: High-resolution hourly time series.
  - `daily/point`: Daily aggregations for temperature, rainfall, radiation, and wind.
  - `monthly/point`: Monthly climatological means and totals.
  - `climatology/point`: Pre-computed multi-year monthly baseline normals.
- **Payload Format**: Standard GeoJSON / JSON containing `header`, `parameters`, and ordered dictionary values keyed by temporal timestamps (`YYYYMMDD` or `YYYYMM`).
- **Data Reduction for Sea Level Pressure ($PSL$)**:
  Because MERRA-2 natively supplies surface barometric pressure ($PS$) at model terrain height, the generator calculates Mean Sea Level Pressure ($PSL$) using the barometric hypsometric equation:
  $$PSL = PS \times \exp\left(
rac{g_0 \cdot Z}{R_d \cdot T_v}
ight)$$
  where $g_0 = 9.80665\text{ m/s}^2$, $Z$ is ground surface elevation (m), $R_d = 287.05\text{ J/(kg}\cdot\text{K)}$ is the gas constant for dry air, and $T_v$ is mean virtual temperature of the fictitious air column (K).

---

## 2. Open-Meteo Historical Weather API Architecture

The **Open-Meteo Historical Weather API** provides seamless access to the European Centre for Medium-Range Weather Forecasts (ECMWF) global reanalysis archives without requiring local GRIB file processing.

### 2.1 Underlying Models and Sensors

1. **ECMWF ERA5 Reanalysis**:
   - **Provider**: Copernicus Climate Change Service (C3S) / ECMWF.
   - **Model Core**: Integrated Forecasting System (IFS) Cy41r2 with 4D-Var data assimilation.
   - **Native Spatial Resolution**: $0.25^\circ \times 0.25^\circ$ (approximately $28 \times 28\text{ km}$ at the equator).
   - **Vertical Discretization**: 137 atmospheric levels from the surface up to 0.01 hPa.
   - **Temporal Range**: 1940 to present.

2. **ECMWF ERA5-Land Reanalysis**:
   - **Model Core**: Standalone land-surface component driven by downscaled ERA5 atmospheric forcing, running the HTESSEL (Hydrology Tiled ECMWF Scheme for Surface Exchanges over Land) model.
   - **Native Spatial Resolution**: Enhanced to $0.1^\circ \times 0.1^\circ$ (approximately $9 \times 9\text{ km}$).
   - **Significance**: Substantially superior representation of complex terrain, mountainous temperature lapse rates, and localized soil water balances.

### 2.2 Open-Meteo API Technical Implementation

- **API Endpoint**: `https://archive-api.open-meteo.com/v1/archive`
- **Ingestion Parameters**:
  - `temperature_2m`, `temperature_2m_max`, `temperature_2m_min`
  - `precipitation_sum` (accumulated liquid water equivalent in mm)
  - `pressure_msl` (natively reduced mean sea level pressure in hPa)
  - `surface_pressure` (hPa)
  - `wind_speed_10m` (m/s) & `wind_direction_10m` (degrees)
  - `relative_humidity_2m` (%)
  - `dew_point_2m` (°C)
  - `shortwave_radiation_sum` (MJ/m²/day converted to kWh/m²/day)
  - `uv_index_max` (dimensionless)
  - `cloud_cover` (%)

---

## 3. Parameter Mapping and Cross-Provider Harmonization

The platform maintains absolute mathematical equivalence across both data providers through the following mapping matrix:

| Indicator Domain | Tool Field Name | NASA POWER Parameter | Open-Meteo Parameter | Physical Units | Harmonization Conversion in Code |
|:---|:---|:---|:---|:---:|:---|
| **Air Temperature** | `T_Annual_Mean` | `T2M` | `temperature_2m` | °C | None (Identical) |
| **Max Temperature** | `T_Annual_Max_Mean` | `T2M_MAX` | `temperature_2m_max` | °C | None (Identical) |
| **Min Temperature** | `T_Annual_Min_Mean` | `T2M_MIN` | `temperature_2m_min` | °C | None (Identical) |
| **Precipitation** | `R_Annual_Mean` | `PRECTOTCORR` | `precipitation_sum` | mm/year | Rate (mm/day) $\times$ Days in Month $
\rightarrow$ Annual Sum |
| **Sea Level Pressure** | `PSL_Annual_Mean` | `PS` (reduced) | `pressure_msl` | hPa (mbar) | NASA kPa $\times 10.0 
\rightarrow$ hPa |
| **Surface Pressure** | `PS_Annual_Mean` | `PS` | `surface_pressure` | hPa (mbar) | NASA kPa $\times 10.0 
\rightarrow$ hPa |
| **Wind Speed** | `W_Spd_Annual_Mean` | `WS10M` (or `WS2M`) | `wind_speed_10m` | m/s | None (Identical) |
| **Wind Direction** | `W_Dir_Annual_Mean` | `U2M`, `V2M` | `wind_direction_10m` | Degrees (°) | Vector atan2 circular mean |
| **Relative Humidity** | `RH_Annual_Mean` | `RH2M` | `relative_humidity_2m` | % | None (Identical) |
| **Dew Point** | `Td_Annual_Mean` | `T2MDEW` | `dew_point_2m` | °C | None (Identical) |
| **Solar Radiation** | `Sol_Annual_Mean` | `ALLSKY_SFC_SW_DWN` | `shortwave_radiation_sum` | kWh/m²/day | NASA MJ/m² $/ 3.6 
\rightarrow$ kWh/m² |
| **Solar Radiation** | `Sol_Annual_Total` | `ALLSKY_SFC_SW_DWN` | `shortwave_radiation_sum` | kWh/m²/year | Daily mean $\times 365.25$ (or sum of monthly totals) |
| **UV Index** | `UV_Annual_Mean` | `ALLSKY_SFC_UV_INDEX`| `uv_index_max` | Index (0-16+) | None (Identical) |
| **Cloud Cover** | `Cld_Annual_Mean` | `CLDTOT` | `cloud_cover` | % | Fraction ($0-1$) $\times 100 
\rightarrow$ % |
