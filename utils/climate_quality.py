# -*- coding: utf-8 -*-
"""Data guards shared by the existing point and raster tools (Python 2/3)."""
import math

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")
SEASONS = {"Winter": (12, 1, 2), "Spring": (3, 4, 5),
           "Summer": (6, 7, 8), "Autumn": (9, 10, 11)}
IDENTITY_FIELDS = ("Source_ID", "Station_ID")


def number(value):
    try:
        value = float(value)
        return None if math.isnan(value) or math.isinf(value) or value <= -900 else value
    except (TypeError, ValueError, OverflowError):
        return None


def coordinates(geometry, wgs_sr):
    try:
        point = geometry.projectAs(wgs_sr).centroid
        return number(point.Y), number(point.X)
    except Exception:
        return None, None


class PointIndex(object):
    """Match WGS84 points to ~0.1 m; ambiguous points require a stable ID.

    OIDs are deliberately excluded: copying a feature class renumbers them.
    IDs only disambiguate coincident geometries; they never override a spatial
    mismatch or a failed projection.
    """
    def __init__(self, records):
        self.records = records
        self.by_xy = {}
        for idx, record in enumerate(records):
            key = self.key(record.get("lat"), record.get("lon"))
            if key is not None:
                self.by_xy.setdefault(key, []).append(idx)

    @staticmethod
    def key(lat, lon):
        lat, lon = number(lat), number(lon)
        return (round(lat, 6), round(lon, 6)) if lat is not None and lon is not None else None

    def match(self, lat, lon, fields=None):
        candidates = self.by_xy.get(self.key(lat, lon), [])
        if len(candidates) == 1:
            return candidates[0]
        if fields:
            for name in IDENTITY_FIELDS:
                value = fields.get(name)
                if value is None:
                    continue
                matches = [idx for idx in candidates
                           if self.records[idx].get("fields", {}).get(name) == value]
                if len(matches) == 1:
                    return matches[0]
        return None


def merge_point_layers(arcpy, base, layers, wgs_sr, reverse_names, short_names, warn):
    """Join attributes onto the first layer's geometry without an OID fallback."""
    identities = [f.name for f in arcpy.ListFields(base) if f.name in IDENTITY_FIELDS]
    records = []
    with arcpy.da.SearchCursor(base, ["SHAPE@"] + identities) as cursor:
        for row in cursor:
            lat, lon = coordinates(row[0], wgs_sr)
            records.append({"geom": row[0], "lat": lat, "lon": lon,
                            "fields": dict(zip(identities, row[1:]))})
    index = PointIndex(records)
    for layer in layers:
        oid = arcpy.Describe(layer).OIDFieldName
        names = [f.name for f in arcpy.ListFields(layer)
                 if f.type not in ("Geometry", "Raster", "Blob", "OID") and f.name != oid]
        unmatched = 0
        with arcpy.da.SearchCursor(layer, ["SHAPE@"] + names) as cursor:
            for row in cursor:
                values = dict((reverse_names.get(name, name), value)
                              for name, value in zip(names, row[1:]))
                lat, lon = coordinates(row[0], wgs_sr)
                idx = index.match(lat, lon, values)
                if idx is None:
                    unmatched += 1
                    continue
                target = records[idx]["fields"]
                for name, value in values.items():
                    if value is None:
                        continue
                    if isinstance(value, (int, float)) and number(value) is None:
                        continue
                    if target.get(name) is None:
                        target[name] = value
                    short = short_names.get(name)
                    if short and target.get(short) is None:
                        target[short] = value
        if unmatched:
            warn("Skipped %d unmatched or ambiguous point(s) in '%s'; OIDs are not spatial keys."
                 % (unmatched, layer))
    return records, index


def derive_from_fields(fields, heat_index, humidex, wbgt, windchill):
    """Fill existing indicators from actual inputs, keeping precalculated data.

    Annual temperature cannot supply monthly extrema for Hargreaves or the
    twelve rain/temperature pairs for Walter-Lieth. Trends need a time series,
    which a single climatological feature row does not contain.
    """
    result = dict(fields)

    def get(*names):
        for name in names:
            value = number(result.get(name))
            if value is not None:
                return value
        return None

    def put(name, value, places=2):
        if number(result.get(name)) is None and value is not None:
            result[name] = round(value, places)

    def complete(values):
        return all(v is not None for v in values)

    rain = [get("R_%s_Mean" % m) for m in MONTHS]
    temp = [get("T_%s_Mean" % m) for m in MONTHS]
    pets = [get("ET_%s_Mean" % m) for m in MONTHS]
    if complete(rain):
        put("R_Annual_Mean", sum(rain), 1)
    if complete(temp):
        put("T_Annual_Mean", sum(temp) / 12.0)
    if complete(pets):
        put("ET_Annual_Mean", sum(pets), 1)
        put("ET_Annual_Range", max(pets) - min(pets), 1)
    for season, months in SEASONS.items():
        values = [pets[m - 1] for m in months]
        if complete(values):
            put("ET_%s_Mean" % season, sum(values), 1)
    pet = get("ET_Annual_Mean", "PET_Hargreaves_Annual")
    put("ET_Annual_Mean", pet, 1)
    put("PET_Hargreaves_Annual", pet, 1)
    t = get("T_Annual_Mean", "T_AnnMean")
    p = get("R_Annual_Mean", "R_AnnMean", "R_Annual_Total", "R_AnnTot", "Precip_Annual_Sum")
    if p is not None and t is not None and t + 10.0 > 0.01:
        put("DM_Aridity_Annual", p / (t + 10.0))
    if p is not None and pet is not None:
        if pet > 0.01:
            put("UNEP_Aridity_Annual", p / pet, 3)
        put("Water_Deficit_Annual", p - pet, 1)
    if complete(rain) and complete(temp):
        put("Dry_Months_Count", sum(1 for p_m, t_m in zip(rain, temp) if p_m < 2.0 * t_m), 0)

    for period in ("Annual", "Winter", "Spring", "Summer", "Autumn") + MONTHS:
        t_p = get("T_%s_Mean" % period)
        rh_p = get("RH_%s_Mean" % period)
        w_p = get("W_Spd_%s_Mean" % period)
        if t_p is not None and rh_p is not None:
            formula = humidex if period == "Winter" else heat_index
            put("HI_%s_Mean" % period, formula(t_p, rh_p))
            if period == "Summer":
                put("WBGT_Summer_Mean", wbgt(t_p, rh_p))
        if t_p is not None and w_p is not None:
            put("WC_%s_Mean" % period, windchill(t_p, w_p))
    # Prefer the actual monthly index series for the annual average.
    for prefix in ("HI", "WC"):
        monthly = [get("%s_%s_Mean" % (prefix, m)) for m in MONTHS]
        if complete(monthly) and number(fields.get("%s_Annual_Mean" % prefix)) is None:
            result["%s_Annual_Mean" % prefix] = round(sum(monthly) / 12.0, 2)
        summer, winter = get("%s_Summer_Mean" % prefix), get("%s_Winter_Mean" % prefix)
        if summer is not None and winter is not None:
            put("%s_Annual_Range" % prefix, abs(summer - winter))
    return result
