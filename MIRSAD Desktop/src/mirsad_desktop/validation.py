"""Bounded local input contracts. External documents never become commands."""
import math
import zipfile
from pathlib import Path

MAX_POINTS=20000
MAX_FIELDS=512
MAX_JSON_BYTES=256*1024*1024
TABLE_SUFFIXES={".xlsx",".csv",".tsv"}
VECTOR_SUFFIXES={".shp",".gpkg",".geojson",".json",".sqlite",".gdb"}
RASTER_SUFFIXES={".tif",".tiff"}

def local_dataset(path):
    text=str(path)
    if "://" in text or text.lower().startswith(("/vsi","\\vsi")):
        raise ValueError("Add Data accepts local datasets, not remote URLs or GDAL virtual file systems.")
    path=Path(path).resolve(strict=True)
    if path.suffix.lower() not in TABLE_SUFFIXES|VECTOR_SUFFIXES|RASTER_SUFFIXES:
        raise ValueError("Unsupported input. Use SHP, FileGDB, GeoPackage, GeoJSON, SQLite, GeoTIFF, Excel or CSV.")
    if path.suffix.lower()==".gdb":
        if not path.is_dir():raise ValueError("FileGDB must be a .gdb directory.")
    elif not path.is_file():raise ValueError("Expected a dataset file.")
    if path.suffix.lower() in TABLE_SUFFIXES|{".json",".geojson"} and path.stat().st_size>200*1024*1024:
        raise ValueError("Tabular/GeoJSON import is limited to 200 MB; subset the input first.")
    if path.suffix.lower()==".xlsx":
        with zipfile.ZipFile(path) as archive:
            members=archive.infolist()
            if len(members)>20000 or sum(item.file_size for item in members)>512*1024*1024:
                raise ValueError("Excel archive exceeds safe expansion limits. Split the workbook first.")
            if any(item.flag_bits&1 for item in members):raise ValueError("Encrypted workbook is not supported.")
    return path

def validate_points(points):
    if not points or len(points)>MAX_POINTS:raise ValueError("Choose 1 to %d points per job."%MAX_POINTS)
    seen=set()
    for point in points:
        lon,lat=float(point["longitude"]),float(point["latitude"])
        if not math.isfinite(lon) or not math.isfinite(lat) or not(-180<=lon<=180 and -90<=lat<=90):
            raise ValueError("Invalid WGS84 point coordinates.")
        key=point["station_key"]
        if not isinstance(key,str) or len(key)>1024 or key in seen:raise ValueError("Point identities must be unique, bounded text.")
        seen.add(key)
    return points

def bounded_json(path):
    import json
    path=Path(path)
    if path.stat().st_size>MAX_JSON_BYTES:raise ValueError("Job data exceeds the safe JSON size limit.")
    return json.loads(path.read_text(encoding="utf-8"))
