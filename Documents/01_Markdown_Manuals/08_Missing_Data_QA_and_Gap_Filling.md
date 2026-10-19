# 08. Missing Data Quality Assurance and Gap-Filling Strategies
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Sentinel Value Identification and Ingestion Scrubbing

Satellite and numerical weather reanalysis APIs convey missing, corrupt, or uncalculated grid observations through specific numerical sentinels. The platform detects and sanitizes these sentinels during ingestion via `is_missing(v)` (line 612):

```python
# Implemented in Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt (Line 612)
MISSING_SENTINELS = {-999.0, -99.0, -9999.0, -99999.0}

def is_missing(v):
    if v is None:
        return True
    try:
        fv = float(v)
        if math.isnan(fv) or math.isinf(fv):
            return True
        return fv in MISSING_SENTINELS
    except (ValueError, TypeError):
        return True
```

---

## 2. The 75% Completeness Rule (`min_frac = 0.75`)

In strict accordance with World Meteorological Organization (WMO) guidelines for calculating climatological standard normals (WMO-No. 1203):
- A monthly mean requires at least **75% of daily observations** to be valid ($\ge 23$ days in a 31-day month).
- An annual total or seasonal mean requires at least **75% of component periods** to be valid.
- A 30-year climatological normal requires at least **75% of years** ($\ge 23$ out of 30 years) to be present.

This rule is enforced computationally via `safe_sum` (line 642):

```python
# Implemented in Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt (Line 642)
def safe_sum(values, expected, min_frac=0.75):
    valid = [v for v in values if not is_missing(v)]
    if len(valid) < expected * min_frac:
        return None
    return sum(valid) * (float(expected) / float(len(valid)))
```

Notice that `safe_sum` not only validates completeness against `min_frac`, but also performs **proportional scaling** (`* expected / len(valid)`) to prevent underestimating accumulated precipitation when 1–5 non-consecutive days are missing.

---

## 3. Physical Boundary Enforcement

All ingested and calculated variables pass through strict biophysical boundary validation:

| Variable | Physical Boundary Envelope | Corrective Action if Violated |
|:---|:---:|:---|
| **Relative Humidity ($RH$)** | $0.0\% \le RH \le 100.0\%$ | Clipped to boundary $[0, 100]\%$. |
| **Dew Point ($Td$)** | $Td \le T_{ambient}$ | Clamped to $T_{ambient}$ if $Td > T$ due to numerical rounding. |
| **Solar Radiation ($Sol$)** | $Sol \ge 0.0\text{ kWh/m}^2$ | Clamped to $0.0$. |
| **Surface Pressure ($PS$)** | $300\text{ hPa} \le PS \le 1100\text{ hPa}$ | Values $<300$ or $>1100$ rejected as corrupt sentinels. |
| **Wind Speed ($WS$)** | $0.0\text{ m/s} \le WS \le 120.0\text{ m/s}$ | Clamped to $0.0$ if negative. |
| **Dry Months Count** | $0 \le N \le 12$ | Integer constrained to $[0, 12]$. |
| **Precipitation Relative Anomaly** | Baseline $\ge 5.0\text{ mm}$ | Guarded with `None` if baseline $< 5\text{ mm}$ to prevent division by near-zero. |

---

## 4. Spatial Gap-Filling and Interpolator Fallback

When a sampling point fails API retrieval due to network timeout or geographical boundary masking (e.g. marine boundary cells in coastal projects):
1. **Local Point Cache Search**: Searches local SQLite / JSON cache for previous successful pulls.
2. **Nearest-Neighbor Spatial Imputation**: If $<5\%$ of total points fail, spatial interpolation (Kriging / IDW) naturally infers values from surrounding valid neighbors without introducing bias.
3. **NoData Propagation**: If an entire geographic sector is missing, the corresponding raster cells are assigned formal NoData sentinels to avoid presenting fabricated data.
