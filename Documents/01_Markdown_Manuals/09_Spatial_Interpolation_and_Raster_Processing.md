# 09. Spatial Interpolation and Raster Processing
## NASA POWER & Open-Meteo Climate Atlas Generator

---

## 1. Geostatistical and Deterministic Interpolation Engines

The platform integrates three spatial interpolation algorithms via ArcGIS Spatial Analyst:

### 1.1 Inverse Distance Weighting (IDW)
- **Algorithm Type**: Deterministic local interpolator.
- **Mathematical Formulation**:
  $$\hat{Z}(s_0) = \frac{\sum_{i=1}^N \frac{1}{d_i^p} Z(s_i)}{\sum_{i=1}^N \frac{1}{d_i^p}}$$
  where $d_i = \|s_0 - s_i\|$ is Euclidean distance, and $p$ is the distance power parameter (default $p = 2.0$).
- **Characteristics**: Fast, completely robust, strictly preserves extreme values within sample bounds (no overshoot). Ideal for precipitation and wind speed in low-relief terrain.

### 1.2 Regularized and Tension Splines
- **Algorithm Type**: Minimum curvature surface fitting.
- **Mathematical Formulation**: Fits a mathematical membrane through sample points while minimizing total surface curvature.
- **Characteristics**: Produces exceptionally smooth, continuous gradients. Highly recommended for barometric pressure ($PSL$), ambient temperature ($T$), and solar insolation ($Sol$).

### 1.3 Ordinary Kriging
- **Algorithm Type**: Geostatistical Best Linear Unbiased Estimator (BLUE).
- **Semivariogram Modeling**: Fits experimental spatial semivariance:
  $$\gamma(h) = \frac{1}{2 N(h)} \sum_{i=1}^{N(h)} \left[Z(s_i) - Z(s_i + h)
\right]^2$$
  Supported models include **Spherical**, **Exponential**, and **Gaussian**.
- **Characteristics**: Models spatial autocorrelation and provides spatial prediction variance surfaces.

---

## 2. Safe Coordinate Transformation (`safe_project_fc`)

To eliminate spatial distortion when calculating cell sizes in metric units (e.g. 1000m resolution) from geographic degrees (WGS84 EPSG:4326):

```python
# Implemented in raster_atlas_generator.py (Line 833)
def safe_project_fc(in_fc, out_fc, target_sr):
    # Determines if reprojection is necessary
    desc = arcpy.Describe(in_fc)
    if desc.spatialReference.name == target_sr.name:
        arcpy.CopyFeatures_management(in_fc, out_fc)
    else:
        arcpy.Project_management(in_fc, out_fc, target_sr)
```

The system automatically selects appropriate regional Projected Coordinate Systems (e.g. UTM zones, Egypt Red Belt EPSG:22992, or Lambert Conformal Conic).

---

## 3. Raster Snapping, Alignment, and Cell Grid Consistency

To ensure that cell $(r, c)$ in `T_Annual_Mean.tif` corresponds to the exact same ground footprint as cell $(r, c)$ in `R_Annual_Mean.tif`:
- **Snap Raster Setting**: `arcpy.env.snapRaster = mask_boundary`
- **Extent Alignment**: `arcpy.env.extent = mask_boundary`
- **Cell Size Enforcement**: Uniform square cells (e.g. $0.05^\circ \times 0.05^\circ$ or $5000\text{m} \times 5000\text{m}$).
- **Masking & Clipping**: Automatically clips interpolated surfaces to the precise boundary polygon of the study area, setting background cells to standard NoData.

---

## 4. Monthly Climatology Surfaces: Unified Stretch and Storage

- **Same engine, same parameters**: the 12 `Month/` rasters reuse the user-selected interpolation method, cell size and clip mask (LZW, 128×128 tiles, statistics + pyramids).
- **Unified color stretch**: before interpolation the tool scans the 12 monthly fields and records one global min/max per element (Wind speed and direction separately). Classified displays built from these breaks are identical across all 12 months, so January vs. July differences are real, not an artifact of per-raster stretching.
- **Wind direction**: circular U/V interpolation (sin/cos + atan2 → 0–360°). Linear interpolation of degrees is mathematically wrong (mean of 350° and 10° is 0°, not 180°) and is never used.
- **Derived vectors from annual/seasonal surfaces**: `Wind_Vector_Annual` and seasonal vectors are sampled directly from the corresponding `W_Spd_*_Mean` and `W_Dir_*_Mean` rasters, while `Isobars_PSL` contours are generated from `PSL_Annual_Mean` and seasonal surfaces (with redundant `*_Month_Mean` surfaces retired).
