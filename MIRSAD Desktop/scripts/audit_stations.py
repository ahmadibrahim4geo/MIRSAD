"""Read-only inventory and reproducible station catalogue build.

Audit-time GDAL may be supplied by a GIS installation. The distributed application
uses its own pyogrio/GDAL wheels; this script is not an application dependency.
"""
import collections
import csv
import datetime as dt
import hashlib
import json
import math
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESKTOP = ROOT / "MIRSAD Desktop"
sys.path.insert(0, str(ROOT / "scripts"))
from country_continent_registry import get_country_info


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_points(path):
    from osgeo import gdal, osr
    gdal.UseExceptions()
    db = gdal.OpenEx(str(path), gdal.OF_VECTOR | gdal.OF_READONLY)
    layers = []
    for layer in db:
        definition = layer.GetLayerDefn()
        fields = {definition.GetFieldDefn(i).GetName().lower(): definition.GetFieldDefn(i).GetName()
                  for i in range(definition.GetFieldCount())}
        sid = next((fields[n] for n in ("station_id", "stationid") if n in fields), None)
        if not sid:
            layers.append({"layer": layer.GetName(), "count": layer.GetFeatureCount(), "kind": "not_station_layer"})
            continue
        source_sr = layer.GetSpatialRef()
        transform = None
        if source_sr:
            source_sr = source_sr.Clone()
            source_sr.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            wgs = osr.SpatialReference()
            wgs.ImportFromEPSG(4326)
            wgs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            transform = osr.CoordinateTransformation(source_sr, wgs)
        rows, issues = [], []
        def val(feature, *names, default=None):
            for name in names:
                if name.lower() in fields:
                    value = feature.GetField(fields[name.lower()])
                    if value is not None:
                        return value
            return default
        for feature in layer:
            geometry = feature.GetGeometryRef()
            issue = None
            if not geometry or not transform:
                issue = "missing_geometry_or_crs"
                x = y = None
            elif geometry.GetGeometryName() != "POINT":
                issue = "non_point_station_geometry"
                x = y = None
            else:
                point = geometry.Clone()
                point.Transform(transform)
                x, y = point.GetX(), point.GetY()
                if not (math.isfinite(x) and math.isfinite(y) and -180 <= x <= 180 and -90 <= y <= 90):
                    issue = "invalid_coordinate"
                elif x == 0 and y == 0:
                    issue = "zero_zero_coordinate"
            row = dict(usaf=str(val(feature, "Station_ID", default="")).strip(),
                       wban=str(val(feature, "WBAN", default="")).strip(),
                       name=str(val(feature, "Name", "Station_Nm", default="")),
                       country=str(val(feature, "Country", "Country_Cd", default="EG" if "Egypt" in path.name else "")),
                       latitude=y, longitude=x, elevation=val(feature, "Elev_m", "Elevation", "Elev_Meters"),
                       attribute_lat=val(feature, "Lat", "Latitude", "Point_Lat"),
                       attribute_lon=val(feature, "Lon", "Longitude", "Point_Lon"))
            if "-" in row["usaf"]:
                row["usaf"], compound_wban = row["usaf"].split("-", 1)
                row["wban"] = row["wban"] or compound_wban
            if not issue and row["attribute_lat"] is not None and row["attribute_lon"] is not None:
                if abs(float(row["attribute_lat"]) - y) > 1e-5 or abs(float(row["attribute_lon"]) - x) > 1e-5:
                    issue = "geometry_attribute_mismatch"
            row["issue"] = issue
            rows.append(row)
            if issue:
                issues.append({"usaf": row["usaf"], "name": row["name"], "issue": issue,
                               "geometry": [x, y], "attributes": [row["attribute_lon"], row["attribute_lat"]]})
        layers.append(dict(layer=layer.GetName(), count=len(rows), kind="station_layer",
                           crs=source_sr.ExportToWkt() if source_sr else None, issues=issues, rows=rows))
    db = None
    return layers


def km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    return 6371.0088 * 2 * math.asin(min(1, math.sqrt(math.sin((lat2-lat1)/2)**2 +
        math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2)))


def main():
    reference = ROOT / "data/reference/isd-history.csv"
    noaa, noaa_countries, by_usaf = {}, {}, collections.defaultdict(list)
    if reference.exists():
        with reference.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                try:
                    xy = float(row["LAT"]), float(row["LON"])
                    if not (-90 <= xy[0] <= 90 and -180 <= xy[1] <= 180):
                        continue
                    noaa[(row["USAF"], row["WBAN"])] = xy
                    noaa_countries[(row["USAF"], row["WBAN"])] = row.get("CTRY", "")
                    by_usaf[row["USAF"]].append(xy)
                except (ValueError, KeyError):
                    pass
    paths = list((ROOT / "Weather_Stations_Hub").rglob("*.shp"))
    paths += list((ROOT / "Sample Data").rglob("*.shp"))
    paths += [p for p in ROOT.rglob("*.gdb") if p.is_dir() and "MIRSAD Desktop" not in p.parts]
    inventory, all_rows = [], {}
    for path in sorted(set(paths)):
        try:
            layers = read_points(path)
            for layer in layers:
                label = str(path.relative_to(ROOT)) + "/" + layer["layer"]
                all_rows[label] = layer.pop("rows", [])
                inventory.append(dict(path=label, **layer))
        except Exception as exc:
            inventory.append(dict(path=str(path.relative_to(ROOT)), error=str(exc)))
    summary = ROOT / "Sample Data/Egypt_Climate_Stations/Stations_Summary.csv"
    if summary.exists():
        with summary.open(encoding="utf-8-sig", newline="") as handle:
            all_rows[str(summary.relative_to(ROOT))] = [dict(usaf=row["Station_ID"].split("-")[0],
                name=row["Station_Nm"], latitude=float(row["Latitude"]), longitude=float(row["Longitude"]))
                for row in csv.DictReader(handle)]
    global_key = next(key for key in all_rows if key.endswith("Global_Weather_Stations.shp/Global_Weather_Stations"))
    canonical, discrepancies, seen = [], [], set()
    for source in all_rows[global_key]:
        row = dict(source)
        if row["issue"]:
            raise RuntimeError("Canonical geometry requires review before catalogue regeneration: " + str(row))
        key = "%s|%s|%.6f|%.6f" % (row["usaf"], row["wban"], row["latitude"], row["longitude"])
        if key in seen:
            continue
        seen.add(key)
        refs = [noaa[(row["usaf"], row["wban"])]] if (row["usaf"], row["wban"]) in noaa else by_usaf[row["usaf"]]
        distance = min((km((row["latitude"], row["longitude"]), xy) for xy in refs), default=None)
        qa = "reference_match" if distance is not None and distance <= 1.0 else "reference_unmatched"
        if distance is not None and distance > 1:
            qa = "review_required"
            discrepancies.append(dict(station_key=key, name=row["name"], distance_km=round(distance, 3),
                                      latitude=row["latitude"], longitude=row["longitude"]))
        if row["issue"]:
            qa = "quarantined"
        en, ar, continent, is_arab = get_country_info(row["country"], row["latitude"], row["longitude"])
        canonical.append(dict(station_key=key, usaf=row["usaf"], wban=row["wban"], name=row["name"],
                              country=row["country"], country_name=en, country_ar=ar, continent=continent,
                              source_country=noaa_countries.get((row["usaf"],row["wban"]), ""),
                              reference_latitude=noaa.get((row["usaf"],row["wban"]),(None,None))[0],
                              reference_longitude=noaa.get((row["usaf"],row["wban"]),(None,None))[1],
                              is_arab=int(is_arab), latitude=row["latitude"], longitude=row["longitude"],
                              elevation=row["elevation"], qa_status=qa))
    comparison = []
    canonical_by_usaf = collections.defaultdict(list)
    for row in canonical:
        canonical_by_usaf[row["usaf"]].append(row)
    for label, rows in all_rows.items():
        same, missing, different = 0, 0, []
        for row in rows:
            refs = canonical_by_usaf[row["usaf"]]
            if not refs or row["latitude"] is None:
                missing += 1
                continue
            distance = min(km((row["latitude"], row["longitude"]), (p["latitude"], p["longitude"])) for p in refs)
            if distance <= 0.1:
                same += 1
            else:
                different.append(dict(usaf=row["usaf"], name=row["name"], distance_km=round(distance, 3)))
        if rows:
            comparison.append(dict(path=label, same_location=same, unmatched=missing, different=different))
    semantic_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    metadata = dict(catalogue_version="2026.10.17.2", catalogue_hash=semantic_hash, count=len(canonical),
                    source="NOAA ISD station locations; MIRSAD display policy retained",
                    source_dbf_sha256=digest(ROOT / "Weather_Stations_Hub/Shapefiles/Global_Weather_Stations.dbf"),
                    reference_url="https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv",
                    reference_sha256=digest(reference) if reference.exists() else None,
                    audited_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                    qa_counts=dict(collections.Counter(r["qa_status"] for r in canonical)),
                    accuracy_limit="Catalogue agreement is not ground verification; discrepancies are not silently relocated.")
    final_output = ROOT / "data/stations.sqlite"
    output = ROOT / "data/stations.new.sqlite"
    if output.exists():
        output.unlink()
    columns = list(canonical[0])
    types = {"latitude": "REAL", "longitude": "REAL", "reference_latitude": "REAL", "reference_longitude": "REAL",
             "elevation": "REAL", "is_arab": "INTEGER"}
    with sqlite3.connect(output) as db:
        db.execute("CREATE TABLE stations (%s, PRIMARY KEY(station_key))" %
                   ",".join('"%s" %s' % (key, types.get(key, "TEXT")) for key in columns))
        db.executemany("INSERT INTO stations VALUES (%s)" % ",".join("?" for _ in columns),
                       [[r[key] for key in columns] for r in canonical])
        db.execute("CREATE INDEX station_country ON stations(country)")
        db.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)")
        db.executemany("INSERT INTO metadata VALUES (?,?)", [(k, json.dumps(v, ensure_ascii=False)) for k,v in metadata.items()])
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Catalogue integrity failed")
    db.close()
    output.replace(final_output)
    report = dict(metadata=metadata, inventory=inventory, comparisons=comparison, noaa_discrepancies=discrepancies,
                  tables_note="Stations_Summary.csv checked by compound NOAA identifiers and coordinates.")
    (DESKTOP / "docs/STATION_AUDIT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dict(catalogue=str(final_output), **metadata), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
