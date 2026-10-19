# Hybrid — source barriers and monthly estimates

Implemented 18 October 2026, development 0.4.0.dev2. This change covers Hybrid
download/estimation order; it does not complete the separate advanced toolbox
parameter/export parity backlog.

## Requested and implemented order

1. Resolve station identity using USAF **and WBAN**, retaining location. Arbitrary
   points without both identifiers have no claimed NOAA station observations.
2. Finish NOAA GSOD requests for **all selected stations and years**.
3. Inventory missing station × variable × day cells. Finish selected Open-Meteo
   ERA5/ERA5-Land/ERA5-Seamless requests for all stations with supported gaps.
4. Inventory remaining gaps, then finish NASA POWER for all stations. UV/skin
   temperature dependencies unavailable through the ERA5 adapter go to POWER.
5. Aggregate to complete calendar months, then run the selected monthly Gap Fill
   once for the entire network. Calculate climate indices after this step.
6. Export the same calculated records to tables/GIS/raster processing.

These are source-wide barriers, including in element-by-element toolbox mode.
One unsuccessful station does not prevent the other stations or later sources
from being attempted. Completion of a source stage means every request has a
terminal result, not that every requested value exists.

`utils/hybrid_pipeline.py` is Python 2.7/3 compatible and contains the download,
parsing, merge, monthly aggregation and estimation orchestration. Desktop embeds
an identical copy through `scripts/vendor_science.py`; it has no parent toolbox
dependency. Both application workflow and single-point Hybrid convenience calls
use this engine. Other provider modes retain their existing adapters.

## Failure, resumption and provenance

- Request-sized checkpoints are committed atomically after a complete response.
  Each request covers at most a calendar year and the enclosing missing interval;
  a source can return extra days, but merging only fills empty cells.
- Successful and HTTP 404 responses are reusable. A connection/parse failure is
  recorded as `FAILED` and is retried on a later run; it is not cached as absence.
- Three bounded attempts, input-size bounds and cancellation checks are used.
  Downloads remain sequential, so a source stage never overlaps another stage.
- Higher-priority valid values, including actual zero rainfall, are preserved.
  Raw responses/flags, retrieval times, URLs, per-day sources, source events,
  remaining missing counts and monthly estimate audits are retained.
- Desktop projects copy request checkpoints plus summaries into `Raw_Data/`;
  the toolbox retains them in `Source Data/Hybrid/`. Desktop's isolated worker
  boundary is unchanged. Source ordering alone is not a guarantee against every
  native library failure or an arbitrarily large network exhausting memory.

## Scientific rules and explicit behavior changes

- NOAA ingestion is **GSOD daily summaries derived from ISD**, not direct ISD
  hourly ingestion or GHCN-Daily. A missing station/year file is distinguished
  from a failed request. USAF/WBAN are text fields in the temporary station layer.
- Coordinate discrepancies >0.05° are excluded and reported without moving the
  station. Quality flags and original observations remain in the raw response.
- NOAA incomplete rainfall flags are missing, including H/I zero without a
  complete precipitation report. Missing precipitation never becomes zero.
- Canonical units are °C, mm/day, kPa, m/s and MJ/m²/day. POWER RE solar energy is
  converted from kWh to MJ before the shared scientific kernel. Requests use UTC
  where selectable; Open-Meteo hourly means require all 24 hours. Wind direction
  uses a circular mean. NASA UV uses the existing documented noon-max estimate.
- A source monthly value needs all days of that calendar month. A partial
  requested month is not promoted to a full-month total or mean.
- Temporal climatological/linear methods retain the reviewed mean-variable
  rules: rainfall totals and wind bearings are excluded. Legacy climatological
  fallback to the station-wide mean and linear boundary fill are retained and
  labelled, rather than being advertised as observations.
- Explicit **spatial** mode now estimates missing monthly cells using inverse
  geodesic-distance weights from up to three original donor stations (power 1,
  identical locations <1 m use the nearest value). It can estimate monthly
  precipitation when selected; it does not estimate wind bearings. Donor keys
  and distances are recorded. There is no imposed donor-distance threshold or
  claim that distant donors are climatologically representative; inspect the
  audit before scientific use. No donor estimates are recursively reused.
- Hybrid no longer applies the old unconditional post-calculation spatial
  filling to final indices for every non-None gap mode. Derived results are
  computed from the finalized monthly inputs, preserving scientific dependencies.
- Daily source coverage remains raw coverage after monthly estimation. Estimates
  never create daily measurements. Desktop adds `Gap_Fill_Method` and
  `Gap_Filled_Months` to its records and retains per-cell monthly audit JSON.
- Yearly exports reuse the same finalized monthly series and estimate flags.

## Evidence

- Six shared tests run on both Python 2.7 and Python 3: global source order,
  missing interval bounds, priority/zero preservation, checkpoints/resumption,
  failure versus absence, NOAA identity/flags/units and original spatial donors.
- Desktop suite: 35 passing tests, including monthly mean estimation, unchanged
  rainfall/daily coverage and routing to the common engine. GIS readback includes
  the new text field after correcting its writer type.
- Legacy suites: 19 runtime + 10 validation checks pass on Python 2.7 and 3.
- `.test-output/hybrid-live/report.json`: live two-station January 2024 downloads
  and Desktop Excel/FileGDB/GeoPackage exports. Cairo had NOAA observations;
  Alexandria had a genuine NOAA 404 and was completed from later sources.
- `.test-output/hybrid-native.json`: actual ArcGIS Pro 3.6 tool execution for
  Cairo January 2024, Temperature/Precipitation/UV, daily persistence, GDB and
  Excel output. USAF/WBAN survive the native temporary shapefile/cursor roundtrip.
  This does not certify every station, period, module or native ArcMap execution.
- `.test-output/hybrid-frozen.json`: actual 0.4.0.dev2 EXE climate worker, launched
  with its working directory outside the checkout, downloaded the two-station
  Hybrid case and exported Excel/FileGDB/GeoPackage plus raw/estimation audits.
  The worker finished and the export manifest was complete. The normal frozen
  self-test, GUI export and workspace/preview acceptance gates also passed.
- The candidate installer passed payload readback, installed workspace, uninstall
  and user-file preservation checks using the separate QA AppId. Production
  installation and stable were unchanged. Final development bundle SHA256:
  `154ff74789a900701a79eb586f5de36f527349b5faa7ff9617d22761f79a954f`.
  Installer SHA256:
  `74838a96a4707f883ccd4757131af68290404d9146fd109d6a24a4f13c8d2ecf`.

References: [NOAA GSOD format](https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt),
[Open-Meteo archive](https://open-meteo.com/en/docs/historical-weather-api),
[NASA POWER](https://power.larc.nasa.gov/docs/services/api/).

## Additional provider candidates, not implemented by this change

- [Copernicus CDS API](https://cds.climate.copernicus.eu/en/how-to-api): direct
  catalogue access, account/token and dataset licence acceptance. ERA5 accessed
  through CDS and ERA5 served by Open-Meteo are access routes to the same model
  family, not independent ground observations.
- [ClimateSERV API](https://climateserv2.servirglobal.net/develop-api): CHIRPS
  precipitation and IMERG gridded products; useful additional precipitation
  products rather than an all-variable station substitute.
- [Meteostat JSON API](https://dev.meteostat.net/api.html): station/point weather,
  RapidAPI key required. [Open bulk data](https://dev.meteostat.net/data.html)
  is also available; datasets can include model-filled values, so source flags
  must be retained and model estimates distinguished from observations.
- [NOAA CDO](https://www.ncei.noaa.gov/cdo-web/webservices/v2): additional NOAA
  archives including GHCN-Daily; the API requires a token and its station IDs
  require an explicit mapping, not an assumed USAF-only match.
