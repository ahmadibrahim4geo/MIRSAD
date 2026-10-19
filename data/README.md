# Shared station catalogue

`stations.sqlite` is the versioned, audited location catalogue shared by the legacy toolbox and MIRSAD Desktop. Country display policy is retained separately from the reference's `source_country`. Original reference coordinates are preserved alongside MIRSAD coordinates.

Metadata inside the database records the catalogue semantic hash, source DBF hash, reference hash and audit time. `reference/isd-history.csv` is the NOAA snapshot used for the audit, obtained from https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv.

Desktop embeds a build-time copy through `MIRSAD Desktop/scripts/prepare_assets.py`; it never opens this parent directory at runtime. The audit script is a development tool and uses an available GDAL/OGR Python installation. It does not modify original Esri geodatabases.

See `MIRSAD Desktop/docs/STATION_AUDIT.md` and `.json` for the evidence and limitations. Agreement with a catalogue is not ground verification.
