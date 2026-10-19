# -*- coding: utf-8 -*-
"""Read the bundled station DBF without opening an ArcGIS workspace (Py2/3)."""
from __future__ import unicode_literals
import collections
import math
import os
import struct
import sqlite3

_CACHE = {}


def load_shared_catalogue(path):
    """Versioned, audited location snapshot shared with the independent desktop."""
    stat = os.stat(path)
    signature = (os.path.abspath(path), stat.st_size, stat.st_mtime)
    if signature in _CACHE:
        return _CACHE[signature]
    countries = {}
    database = sqlite3.connect(path)
    try:
        # Python 2.7's sqlite3.Row rejects unicode column-name indexes.
        database.row_factory = lambda cursor, row: dict((column[0], value)
                                                       for column, value in zip(cursor.description, row))
        for row in database.execute("SELECT * FROM stations ORDER BY country,name,station_key"):
            station = {"Station_ID": row["usaf"], "WBAN": row["wban"], "Name": row["name"],
                       "Country": row["country"], "Country_Nm": row["country_name"],
                       "Continent": row["continent"], "Is_Arab": bool(row["is_arab"]),
                       "Lat": row["latitude"], "Lon": row["longitude"], "Elev_m": row["elevation"] or 0.0,
                       "Station_Key": row["station_key"], "Coordinate_QA": row["qa_status"]}
            countries.setdefault(row["country"], []).append(station)
    finally:
        database.close()
    _CACHE.clear()
    _CACHE[signature] = countries
    return countries


def _text(raw):
    return raw.rstrip(b" \x00").decode("utf-8", "replace").strip()


def _number(raw):
    try:
        value = float(raw)
        return None if math.isnan(value) or math.isinf(value) else value
    except (TypeError, ValueError):
        return None


def load_catalogue(dbf_path):
    """Cache by file identity; only keep the current directory snapshot."""
    stat = os.stat(dbf_path)
    signature = (os.path.abspath(dbf_path), stat.st_size, stat.st_mtime)
    if signature in _CACHE:
        return _CACHE[signature]
    countries = {}
    with open(dbf_path, "rb") as handle:
        header = handle.read(32)
        if len(header) != 32:
            raise ValueError("Invalid station directory DBF header.")
        count, header_size, record_size = struct.unpack("<IHH", header[4:12])
        if header_size < 33 or record_size < 2:
            raise ValueError("Invalid station directory DBF dimensions.")
        offsets, offset = {}, 1
        for _ in range((header_size - 33) // 32):
            descriptor = handle.read(32)
            if len(descriptor) != 32:
                raise ValueError("Truncated station directory DBF fields.")
            name = _text(descriptor[:11].split(b"\x00")[0])
            width = struct.unpack("B", descriptor[16:17])[0]
            offsets[name] = (offset, offset + width)
            offset += width
        required = ("Station_ID", "Name", "Country", "Lat", "Lon")
        if not all(name in offsets for name in required) or offset > record_size:
            raise ValueError("Station directory is missing required fields.")
        handle.seek(header_size)
        for _ in range(count):
            raw = handle.read(record_size)
            if len(raw) != record_size:
                raise ValueError("Truncated station directory DBF record.")
            if raw[:1] == b"*":
                continue

            def field(name):
                bounds = offsets.get(name)
                return raw[bounds[0]:bounds[1]] if bounds else b""

            station_id, country = _text(field("Station_ID")), _text(field("Country")).upper()
            lat, lon = _number(field("Lat")), _number(field("Lon"))
            if not station_id or not country or lat is None or lon is None:
                continue
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue
            station = {"Station_ID": station_id, "WBAN": _text(field("WBAN")),
                       "Name": _text(field("Name")) or station_id, "Country": country,
                       "Country_Nm": _text(field("Country_Nm")),
                       "Continent": _text(field("Continent")),
                       "Is_Arab": bool(_number(field("Is_Arab"))),
                       "Lat": lat, "Lon": lon, "Elev_m": _number(field("Elev_m")) or 0.0}
            countries.setdefault(country, []).append(station)
    _CACHE.clear()
    _CACHE[signature] = countries
    return countries


def station_choices(stations):
    """Keep duplicate USAF codes distinct using WBAN and, when needed, location."""
    def base_label(station):
        name = " ".join(station["Name"].replace(";", ",").replace("'", "").split())
        return "%s [%s/%s, %s]" % (name, station["Station_ID"],
                                     station.get("WBAN") or "-", station["Country"])
    counts = collections.Counter(base_label(station) for station in stations)
    choices = {}
    for station in stations:
        label = base_label(station)
        if counts[label] > 1:
            label += " (%.6f, %.6f)" % (station["Lat"], station["Lon"])
        # Identical station/code/location rows describe the same selection.
        choices.setdefault(label, station)
    return choices
