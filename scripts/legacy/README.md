# Legacy one-off scripts (superseded — do not use for new runs)

These scripts were manual, one-time helpers used during atlas construction
(seasonal-range backfill, Arabic-alias patching, dictionary sync). Their
behavior is now implemented **inside the tools themselves**:

- `Generate Monthly Climatology Rasters (Jan–Dec)` option (default OFF,
  requires ≥ 2 years) in both `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt`
  (online) and `Toolboxes/raster_atlas_generator.py` (offline)
- `Month/` subfolder routing + unified monthly color stretch
- `Wind_Vector_Month` from `W_*_Month_Mean` rasters; PSL/PS month isobars
- Main-GDB alias = field name (Arabic aliases only in `<base>_AR.gdb`)

Current supported helpers (kept at `scripts/` top level):

- `build_monthly_tables.py` — pure-Python monthly climatology tables + CSVs
  from the raw monthly JSON archive (no ArcGIS needed)
- `build_monthly_backfill_arcmap.py` — ArcMap script injecting the monthly
  fields into the GDB and interpolating the `Month/` rasters
