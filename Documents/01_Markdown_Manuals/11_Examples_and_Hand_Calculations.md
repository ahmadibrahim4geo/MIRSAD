# 11. Worked Numerical Examples and Hand Calculations
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Example 1: 30-Year Precipitation Aggregation (Cairo Grid Cell)

### 1.1 Objective
Verify the calculation of `R_Annual_Mean`, `R_Annual_Range`, and Seasonal Totals from monthly climatological values (noting the retirement of legacy `R_Month_Mean` and `R_Seasonal_Range`).

### 1.2 Input Climatological Monthly Totals (mm)
Assume a 30-year climatological normal (1991–2020) for a grid cell in the Cairo metropolitan region:
- January ($\overline{P}_1$): $5.2\text{ mm}$
- February ($\overline{P}_2$): $4.8\text{ mm}$
- March ($\overline{P}_3$): $3.5\text{ mm}$
- April ($\overline{P}_4$): $1.2\text{ mm}$
- May ($\overline{P}_5$): $0.5\text{ mm}$
- June ($\overline{P}_6$): $0.0\text{ mm}$
- July ($\overline{P}_7$): $0.0\text{ mm}$
- August ($\overline{P}_8$): $0.0\text{ mm}$
- September ($\overline{P}_9$): $0.1\text{ mm}$
- October ($\overline{P}_{10}$): $1.4\text{ mm}$
- November ($\overline{P}_{11}$): $3.8\text{ mm}$
- December ($\overline{P}_{12}$): $5.9\text{ mm}$

### 1.3 Step-by-Step Calculation
1. **Annual Mean Accumulated Precipitation (`R_Annual_Mean`)**:
   $$R_{Annual\_Mean} = \sum_{m=1}^{12} \overline{P}_m = 5.2 + 4.8 + 3.5 + 1.2 + 0.5 + 0.0 + 0.0 + 0.0 + 0.1 + 1.4 + 3.8 + 5.9 = \mathbf{26.40\text{ mm/year}}$$
2. **Legacy Monthly Mean Precipitation (`R_Month_Mean`, Retired)**:
   $$R_{Month\_Mean} = \frac{R_{Annual\_Mean}}{12} = \frac{26.40}{12} = \mathbf{2.20\text{ mm/month}}$$
   *(Retired in the streamlined schema in favor of `R_Annual_Mean`)*.
3. **Seasonal Means**:
   - **Winter (`R_WinMean`)**: $\overline{P}_{12} + \overline{P}_1 + \overline{P}_2 = 5.9 + 5.2 + 4.8 = \mathbf{15.90\text{ mm/season}}$
   - **Spring (`R_SprMean`)**: $\overline{P}_3 + \overline{P}_4 + \overline{P}_5 = 3.5 + 1.2 + 0.5 = \mathbf{5.20\text{ mm/season}}$
   - **Summer (`R_SumMean`)**: $\overline{P}_6 + \overline{P}_7 + \overline{P}_8 = 0.0 + 0.0 + 0.0 = \mathbf{0.00\text{ mm/season}}$
   - **Autumn (`R_AutMean`)**: $\overline{P}_9 + \overline{P}_{10} + \overline{P}_{11} = 0.1 + 1.4 + 3.8 = \mathbf{5.30\text{ mm/season}}$
4. **Ranges**:
   - **Annual Monthly Range (`R_AnnRng`)**: $\max(\overline{P}_m) - \min(\overline{P}_m) = 5.9 - 0.0 = \mathbf{5.90\text{ mm/month}}$
   - **Seasonal Range (`R_SeaRng`)**: $\max(R_{season}) - \min(R_{season}) = 15.90 - 0.00 = \mathbf{15.90\text{ mm/season}}$

---

## 2. Example 2: Circular Mean Wind Direction (Sinai Grid Cell)

### 2.1 Objective
Verify that averaging wind angles crossing the North meridian ($0^\circ / 360^\circ$) produces the correct prevailing direction rather than an erroneous arithmetic average.

### 2.2 Input Monthly Prevailing Angles (Degrees)
Consider 4 winter months with north-northwesterly and north-northeasterly winds:
- Month 1: $340^\circ$ (NNW)
- Month 2: $355^\circ$ (NNW)
- Month 3: $5^\circ$ (NNE)
- Month 4: $20^\circ$ (NNE)

### 2.3 Step-by-Step Calculation
1. **Decompose Angles into Unit Cartesian Components**:
   - $\theta_1 = 340^\circ$: $\sin(340^\circ) = -0.3420$, $\cos(340^\circ) = 0.9397$
   - $\theta_2 = 355^\circ$: $\sin(355^\circ) = -0.0872$, $\cos(355^\circ) = 0.9962$
   - $\theta_3 = 5^\circ$: $\sin(5^\circ) = +0.0872$, $\cos(5^\circ) = 0.9962$
   - $\theta_4 = 20^\circ$: $\sin(20^\circ) = +0.3420$, $\cos(20^\circ) = 0.9397$
2. **Sum Components**:
   - $S_{\sin} = -0.3420 - 0.0872 + 0.0872 + 0.3420 = \mathbf{0.0000}$
   - $S_{\cos} = 0.9397 + 0.9962 + 0.9962 + 0.9397 = \mathbf{3.8718}$
3. **Compute 4-Quadrant Arctangent**:
   $$\overline{\theta} = \text{atan2}(S_{\sin}, S_{\cos}) = \text{atan2}(0.0000, 3.8718) = 0.0\text{ rad} = \mathbf{0.0^\circ \text{ (Due North)}}$$
   *(Note: Naive arithmetic averaging would yield $(340 + 355 + 5 + 20) / 4 = 720 / 4 = 180.0^\circ$ (Due South), a catastrophic 180° inversion).*

---

## 3. Example 3: Biometeorological Heat Index and Shade WBGT

### 3.1 Objective
Calculate the Rothfusz Heat Index and ISO 7243 shade WBGT for a peak summer afternoon.

### 3.2 Inputs
- Ambient 2m Air Temperature: $T = 36.0^\circ\text{C}$
- Relative Humidity: $RH = 55.0\%$

### 3.3 Heat Index Calculation
1. Convert $T$ to Fahrenheit: $T_f = 36.0 \times 1.8 + 32 = 96.8^\circ\text{F}$.
2. Because $T_f \ge 80^\circ\text{F}$, evaluate Rothfusz polynomial:
   $$HI_f = -42.379 + 2.04901523(96.8) + 10.14333127(55) - 0.22475541(96.8)(55) - 6.83783 \times 10^{-3}(96.8)^2 - 5.481717 \times 10^{-2}(55)^2 + 1.22874 \times 10^{-3}(96.8)^2(55) + 8.5282 \times 10^{-4}(96.8)(55)^2 - 1.99 \times 10^{-6}(96.8)^2(55)^2$$
   $$HI_f \approx 124.6^\circ\text{F}$$
3. Convert back to Celsius:
   $$HI_c = \frac{124.6 - 32}{1.8} = \mathbf{51.4^\circ\text{C}}$$
   *(NOAA Category: "Danger" - Heat cramps or heat stroke highly likely with continued exposure).*

### 3.4 Shade WBGT Calculation
1. Natural Wet-Bulb Temperature ($T_w$) via Stull (2011) formula at $T=36^\circ\text{C}, RH=55\%$:
   $$T_w \approx 28.2^\circ\text{C}$$
2. ISO 7243 Shade WBGT:
   $$WBGT_{shade} = 0.7 \times T_w + 0.3 \times T_a = 0.7(28.2) + 0.3(36.0) = 19.74 + 10.80 = \mathbf{30.54^\circ\text{C}}$$
   *(Work/Rest Recommendation: 25% work / 75% rest per hour under heavy physical labor).*

---

## 4. Example 4: Agroclimatic Water Balance (Hargreaves, UNEP, Deficit)

### 4.1 Inputs (Aswan Station Normal)
- Annual Mean Precipitation: $R_{Annual\_Mean} = 1.5\text{ mm/year}$
- Annual Hargreaves PET: $PET_{Hargreaves\_Annual} = 2,450.0\text{ mm/year}$
- Annual Mean Air Temperature: $T_{Annual\_Mean} = 26.5^\circ\text{C}$

### 4.2 Step-by-Step Calculation
1. **De Martonne Aridity Index (`DM_AridAnn`)**:
   $$I_{DM} = \frac{P}{T + 10} = \frac{1.5}{26.5 + 10} = \frac{1.5}{36.5} = \mathbf{0.041}$$
   *(Class: Hyper-arid, $I_{DM} < 5$).*
2. **UNEP Aridity Index (`UNEP_Arid`)**:
   $$AI_{UNEP} = \frac{P}{PET} = \frac{1.5}{2450.0} = \mathbf{0.00061}$$
   *(Class: Hyper-arid, $AI < 0.05$).*
3. **Climatic Water Deficit (`WatDefAnn`)**:
   $$CWD = P - PET = 1.5 - 2450.0 = \mathbf{-2,448.5\text{ mm/year}}$$
   *(Severe net annual atmospheric moisture deficit).*
