# 10. Models, Physical Assumptions, and Scientific Limitations
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Atmospheric Reanalysis Inherent Uncertainties

While global reanalyses (MERRA-2 and ERA5) provide continuous spatial coverage, users must recognize fundamental physical constraints:

1. **Topographic Smoothing**:
   - Reanalysis grid models represent the Earth's surface as a smoothed elevation terrain.
   - Deep valleys, steep mountain peaks (e.g. Sinai Mountain massif, Red Sea Hills, Atlas Mountains), and sharp escarpments are generalized.
   - Consequently, localized temperature inversions, valley cold-air pooling, and extreme rain-shadow effects may be smoothed out.

2. **Convective Precipitation in Arid Regions**:
   - In desert regions (e.g. the Sahara and Arabian Peninsula), rainfall occurs primarily via highly localized, episodic convective storm cells.
   - Reanalysis models often capture the synoptic moisture surge but may distribute rainfall across the entire $0.25^\circ - 0.5^\circ$ grid cell, slightly underestimating peak local rainfall intensity while overestimating rainfall spatial extent.

3. **Coastal Boundary Grids**:
   - Grid cells straddling coastlines blend land and marine surface fluxes, potentially buffering temperature extremes along immediate coastlines.

---

## 2. Hargreaves-Samani Evapotranspiration Assumptions

The Hargreaves-Samani (1985) reference crop evapotranspiration model ($PET$) is used because it requires only temperature and extraterrestrial radiation ($R_a$), making it ideal for data-sparse regions where wind and vapor pressure records are incomplete:

$$PET = 0.0023 \times 0.408 R_a \times (T + 17.8) \times \sqrt{T_{max} - T_{min}}$$

### Underlying Assumptions:
1. **Diurnal Temperature Range ($T_{max} - T_{min}$) as Radiation Proxy**: Assumes that daily temperature amplitude is primarily governed by solar insolation and cloudiness.
2. **Standard Humidity Equilibrium**: Assumes relative humidity and wind speed follow standard inland continental equilibria.
3. **Known Limitation**: In windy, hyper-arid regions with intense advection (e.g. desert hot winds), Hargreaves can underestimate $PET$ compared to full FAO-56 Penman-Monteith. In humid coastal environments, it can slightly overestimate $PET$.

---

## 3. Biometeorological Envelopes of Validity

### 3.1 Rothfusz Heat Index Validity Envelope
- **Empirical Basis**: Regression fit to Steadman's human thermoregulation models.
- **Validity Range**: Strictly formulated for ambient temperatures $T \ge 26.7^\circ\text{C}$ ($80^\circ\text{F}$) and relative humidity $RH \ge 40\%$.
- **Tool Handling**: When $T < 20^\circ\text{C}$, the tool smoothly transitions to ambient dry-bulb temperature, as physiological heat dissipation impairment is inactive at cool temperatures.

### 3.2 Wind Chill Validity Envelope
- **Empirical Basis**: Joint US National Weather Service / Environment Canada (2001) model.
- **Validity Range**: Formulated for temperatures $T \le 10^\circ\text{C}$ and wind speeds $V > 4.8\text{ km/h}$.
- **Tool Handling**: When $T > 10^\circ\text{C}$ or wind is calm ($V \le 4.8\text{ km/h}$), the formula defaults to ambient temperature $T$, preventing artificial cooling values in warm seasons.
