# 05. Scientific Formulas and Mathematical Specifications
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Mathematical Notation and Conventions

- $m \in \{1, 2, \dots, 12\}$: Calendar months from January (1) to December (12).
- $y \in \{1, 2, \dots, N\}$: Observation years in the climatological baseline (e.g. 1991 to 2020, $N = 30$).
- $\overline{X}_m$: 30-year climatological normal for month $m$.
- $N_{days, m}$: Number of calendar days in month $m$.
- $\mathbb{I}(\cdot)$: Indicator function equal to 1 if the condition is true, 0 otherwise.

---

## 2. Module 01: Air Temperature Formulations

1. **Annual Mean Temperature ($T_{Annual\_Mean}$, °C)**:
   $$T_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{T}_m$$

2. **Seasonal Mean Temperatures ($T_{Winter\_Mean}, T_{Spring\_Mean}, T_{Summer\_Mean}, T_{Autumn\_Mean}$, °C)**:
   $$T_{Winter\_Mean} = \frac{\overline{T}_{12} + \overline{T}_1 + \overline{T}_2}{3}, \quad T_{Spring\_Mean} = \frac{\overline{T}_3 + \overline{T}_4 + \overline{T}_5}{3}$$
   $$T_{Summer\_Mean} = \frac{\overline{T}_6 + \overline{T}_7 + \overline{T}_8}{3}, \quad T_{Autumn\_Mean} = \frac{\overline{T}_9 + \overline{T}_{10} + \overline{T}_{11}}{3}$$

3. **Annual Temperature Range ($T_{Annual\_Range}$, °C)**:
   $$T_{Annual\_Range} = \max_{m=1}^{12}(\overline{T}_m) - \min_{m=1}^{12}(\overline{T}_m)$$

4. **Extreme Monthly Means ($T_{Max\_Summer\_Month\_Mean}, T_{Min\_Winter\_Month\_Mean}$, °C)**:
   $$T_{Max\_Summer\_Month\_Mean} = \max(\overline{T}_6, \overline{T}_7, \overline{T}_8), \quad T_{Min\_Winter\_Month\_Mean} = \min(\overline{T}_{12}, \overline{T}_1, \overline{T}_2)$$

5. **Annual Means of Daily Maximum & Minimum ($T_{Annual\_Max\_Mean}, T_{Annual\_Min\_Mean}$, °C)**:
   $$T_{Annual\_Max\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{T}_{max, m}, \quad T_{Annual\_Min\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{T}_{min, m}$$

---

## 3. Module 02: Precipitation Formulations

1. **Annual Mean Precipitation ($R_{Annual\_Mean}$, mm/year)**:
   $$R_{Annual\_Mean} = \sum_{m=1}^{12} \overline{P}_m = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \sum_{m=1}^{12} P_{y, m}$$

2. **Monthly Mean Precipitation ($R_{Month\_Mean}$, mm/month)**:
   $$R_{Month\_Mean} = \frac{R_{Annual\_Mean}}{12}$$

3. **Annual & Seasonal Precipitation Ranges ($R_{Annual\_Range}, R_{Season\_Range}$, mm)**:
   $$R_{Annual\_Range} = \max_{m=1}^{12}(\overline{P}_m) - \min_{m=1}^{12}(\overline{P}_m)$$
   $$R_{Season\_Range} = \max(R_{Win}, R_{Spr}, R_{Sum}, R_{Aut}) - \min(R_{Win}, R_{Spr}, R_{Sum}, R_{Aut})$$

4. **Seasonal Precipitation Totals ($R_{WinTot}, R_{SprTot}, R_{SumTot}, R_{AutTot}$, mm)**:
   $$R_{Win} = \overline{P}_{12} + \overline{P}_1 + \overline{P}_2, \quad R_{Spr} = \overline{P}_3 + \overline{P}_4 + \overline{P}_5$$
   $$R_{Sum} = \overline{P}_6 + \overline{P}_7 + \overline{P}_8, \quad R_{Aut} = \overline{P}_9 + \overline{P}_{10} + \overline{P}_{11}$$

---

## 4. Modules 03 & 04: Barometric Pressure Formulations

1. **Sea Level Pressure ($PSL_{Annual\_Mean}$, hPa) & Surface Pressure ($PS_{Annual\_Mean}$, hPa)**:
   $$PSL_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{PSL}_m, \quad PS_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{PS}_m$$
2. **Seasonal Pressure Means**: Formulated identically to temperature over DJF, MAM, JJA, SON.
3. **Pressure Ranges ($PSL_{Annual\_Range}, PS_{Annual\_Range}$, hPa)**: Difference between highest and lowest monthly normal.

---

## 5. Module 05: Wind Speed and Direction Formulations

1. **Scalar Wind Speed Means ($WSp_{Annual\_Mean}, WSp_{Seasonal}$, m/s)**: Arithmetic mean over 12 months or 3 seasonal months.
2. **Wind Speed Range ($WSp_{Annual\_Range}$, m/s)**: $\max_m(\overline{WS}_m) - \min_m(\overline{WS}_m)$.
3. **Prevailing Wind Direction ($WDr_{Annual\_Mean}, WDr_{Seasonal}$, Degrees)**:
   $$\overline{\theta} = \text{atan2}\left(\frac{1}{N}\sum \sin \theta_i, \frac{1}{N}\sum \cos \theta_i
\right) \pmod{360^\circ}$$

---

## 6. Modules 06 & 07: Moisture Formulations (RH and Dew Point)

1. **Relative Humidity Means ($RH_{Annual\_Mean}, RH_{Seasonal}$, %)**:
   $$RH_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{RH}_m$$
2. **Dew Point Temperature Means ($Td_{Annual\_Mean}, Td_{Seasonal}$, °C)**:
   $$Td_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{Td}_m$$
   *Physical Boundary Enforcement*: $Td \le T$ across all observation pairs.

---

## 7. Module 08: Solar Radiation Formulations

1. **Annual Mean Daily Insolation ($Sol_{Annual\_Mean}$, kWh/m²/day)**:
   $$Sol_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{Sol}_m$$
2. **Annual Total Solar Energy Yield ($Sol_{Annual\_Total}$, kWh/m²/year)**:
   $$Sol_{Annual\_Total} = \sum_{m=1}^{12} \left(\overline{Sol}_m \times N_{days, m}
\right) \approx Sol_{Annual\_Mean} \times 365.25$$

---

## 8. Modules 09 & 10: UV Index and Cloud Cover Formulations

1. **UV Index Statistics ($UV_{Annual\_Mean}, UV_{Seasonal}$, Index 0-16+)**: Arithmetic mean of monthly solar noon maximum indices.
   NASA POWER `ALLSKY_SFC_UV_INDEX` daily/monthly values are 24-hour means including night zeros, NOT noon maxima (verified Cairo: noon 10.5 → daily 2.66). Each monthly 24h-mean is therefore converted to a WHO noon-maximum estimate before any aggregation:
   $$UV_{noon}(y,m) = \overline{UV}_{24h}(y,m) \times \frac{24}{daylength(lat,m) \times 0.435}$$
   with astronomical mid-month daylength and empirical clear-sky shape factor $k \approx 0.435$ (Cairo Jul/Jan within ~6%, uncertainty ~10–15%). Open-Meteo `uv_index_max` (already a daily maximum) is averaged directly without conversion. Monthly/seasonal/annual means, `UV_Annual_Range` and `UV_Annual_Range (with UV_Seasonal_Range retired)` are all computed on noon-max values. UV classification is the fixed WHO scale (identical in every class sheet), never Equal Interval.
2. **Cloud Cover Statistics ($Cld_{Annual\_Mean}, Cld_{Seasonal}$, %)**: Arithmetic mean of monthly total cloud area fractions.

---

## 9. Module 11: Biometeorological Heat Stress Formulations

1. **Rothfusz Heat Index ($HI$, °C)**:
   Computed by converting $T$ to Fahrenheit ($T_f = T \times 1.8 + 32$):
   $$\text{If } T_f \ge 80^\circ\text{F}: \quad HI_f = -42.379 + 2.04901523 T_f + 10.14333127 RH - 0.22475541 T_f RH - 6.83783 \times 10^{-3} T_f^2 - 5.481717 \times 10^{-2} RH^2 + 1.22874 \times 10^{-3} T_f^2 RH + 8.5282 \times 10^{-4} T_f RH^2 - 1.99 \times 10^{-6} T_f^2 RH^2$$
   $$\text{If } T_f < 80^\circ\text{F}: \quad HI_f = 0.5 \times (T_f + 61.0 + [(T_f - 68.0) \times 1.2] + (RH \times 0.094))$$
   Output converted back to Celsius: $HI = (HI_f - 32) / 1.8$.

2. **Wet-Bulb Temperature ($T_w$, °C - Stull, 2011)**:
   $$T_w = T \cdot \text{atan}\left(0.151977 \sqrt{RH + 8.313659}
\right) + \text{atan}(T + RH) - \text{atan}(RH - 1.676331) + 0.00391838 \cdot RH^{3/2} \cdot \text{atan}(0.023101 RH) - 4.686035$$

3. **Summer Mean Shade WBGT ($WBGT_{Summer\_Mean}$, °C - ISO 7243)**:
   $$WBGT_{shade} = 0.7 T_w + 0.3 T_a$$

---

## 10. Module 12: Wind Chill Temperature Formulations

Joint US National Weather Service / Environment Canada (2001) formula:
$$\text{If } T \le 10^\circ\text{C} \text{ and } V > 4.8\text{ km/h}: \quad WC = 13.12 + 0.6215 T - 11.37 V^{0.16} + 0.3965 T V^{0.16}$$
where $V = WS \times 3.6$ (wind speed in km/h). If $T > 10^\circ\text{C}$ or $V \le 4.8\text{ km/h}$, $WC = T$.

---

## 11. Module 13: De Martonne Aridity Index Formulation

$$I_{DM} = \frac{R_{Annual\_Mean}}{T_{Annual\_Mean} + 10}$$
- **Classification Scale**:
  - $I_{DM} < 5$: Hyper-arid
  - $5 \le I_{DM} < 10$: Arid
  - $10 \le I_{DM} < 20$: Semi-arid
  - $20 \le I_{DM} < 30$: Mediterranean / Sub-humid
  - $30 \le I_{DM} < 55$: Humid
  - $I_{DM} \ge 55$: Extremely Humid

---

## 12. Module 14: Evapotranspiration (Hargreaves-Samani PET) Formulations

1. **Extraterrestrial Radiation ($R_a$, MJ/m²/day - FAO-56)**:
   $$R_a = \frac{24 \times 60}{\pi} G_{sc} d_r \left[\omega_s \sin(\varphi)\sin(\delta) + \cos(\varphi)\cos(\delta)\sin(\omega_s)
ight]$$
   where $G_{sc} = 0.0820\text{ MJ/(m}^2\cdot\text{min)}$, $d_r = 1 + 0.033\cos(2\pi J / 365)$, $\delta = 0.409\sin(2\pi J / 365 - 1.39)$, and $\omega_s = \arccos(-\tan(\varphi)\tan(\delta))$.

2. **Daily Potential Evapotranspiration ($PET_{daily}$, mm/day)**:
   $$PET_{daily} = 0.0023 \times 0.408 R_a \times (T + 17.8) \times \sqrt{T_{max} - T_{min}}$$

3. **Annual Hargreaves PET ($PET_{Hargreaves\_Annual}$, mm/year)**:
   $$PET_{Annual} = \sum_{m=1}^{12} \left(PET_{daily, m} \times N_{days, m}
\right)$$

---

## 13. Modules 15, 16 & 17: Aridity, Water Deficit, and Dry Months

1. **UNEP Aridity Index ($AI_{UNEP}$, Dimensionless)**:
   $$AI_{UNEP} = \frac{R_{Annual\_Mean}}{PET_{Hargreaves\_Annual}}$$
   - Hyper-arid: $AI < 0.05$
   - Arid: $0.05 \le AI < 0.20$
   - Semi-arid: $0.20 \le AI < 0.50$
   - Dry sub-humid: $0.50 \le AI < 0.65$
   - Humid: $AI \ge 0.65$

2. **Climatic Water Deficit / Surplus ($CWD_{Annual}$, mm/year)**:
   $$CWD_{Annual} = R_{Annual\_Mean} - PET_{Hargreaves\_Annual}$$
   *(Negative values denote water deficit; positive values denote water surplus).*

3. **Bagnouls-Gaussen Dry Months Count ($N_{Dry\_Months}$, Months 0-12)**:
   $$N_{Dry\_Months} = \sum_{m=1}^{12} \mathbb{I}\left(\overline{P}_m < 2 \times \overline{T}_m
\right)$$

---

## 14. Module 18: Decadal Trends and Baseline Anomalies

1. **Ordinary Least Squares (OLS) Decadal Trend ($\beta_{decade}$)**:
   $$\beta = \frac{\sum_{i=1}^N (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^N (x_i - \bar{x})^2}, \quad \text{Trend}_{Decade} = \beta \times 10$$
   *(Evaluated for Temperature in °C/decade and Precipitation in mm/decade for $N \ge 10$ years).*

2. **Temperature Anomaly ($\Delta T$, °C)**:
   $$\Delta T = \overline{T}_{\text{Recent (2011-2020)}} - \overline{T}_{\text{Baseline (1991-2020)}}$$

3. **Precipitation Absolute & Relative Anomalies ($\Delta R$, mm and %)**:
   $$\Delta R = \overline{P}_{\text{Recent}} - \overline{P}_{\text{Baseline}}$$
   $$\Delta R_{\%} = \begin{cases} \frac{\overline{P}_{\text{Recent}} - \overline{P}_{\text{Baseline}}}{\overline{P}_{\text{Baseline}}} \times 100, & \text{if } \overline{P}_{\text{Baseline}} \ge 5\text{ mm} \ \text{None (Guarded)}, & \text{if } \overline{P}_{\text{Baseline}} < 5\text{ mm} \end{cases}$$
