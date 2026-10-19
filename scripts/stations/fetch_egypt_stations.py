# -*- coding: utf-8 -*-
"""
Egypt Climate Stations Fetcher — standalone script (ArcMap 10.x / Python 2.7)

Fetches all documented weather/climate stations inside Egypt from open official
sources (NOAA ISD history, Meteostat library when installed, WMO 62xxx block),
filters to the Egypt bounding box, dedupes, and writes:
  Egypt_Climate_Stations_Project/
    Egypt_Stations.gdb / Egypt_Weather_Stations (POINT, WGS 1984)
    Export_SHP / Egypt_Weather_Stations_WGS84.shp (+ sidecars)
    Stations_Summary.csv

Run with the ArcGIS Desktop python so arcpy is available, e.g.:
  C:\Python27\ArcGIS10.8\python.exe fetch_egypt_stations.py
Network is required for the download step only; the CSV is cached under
Egypt_Climate_Stations_Project/data/ for repeatable offline re-runs.
"""

import csv
import os
import shutil
import sys
import time

try:
    import arcpy
    _HAS_ARCPY = True
except Exception:
    arcpy = None
    _HAS_ARCPY = False

try:
    import requests
    _HAS_REQUESTS = True
except Exception:
    requests = None
    _HAS_REQUESTS = False

# ---------------------------------------------------------------- config ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(BASE_DIR, "Egypt_Climate_Stations_Project")
DATA_DIR = os.path.join(PROJECT, "data")
GDB_NAME = "Egypt_Stations.gdb"
FC_NAME = "Egypt_Weather_Stations"
SHP_DIR = os.path.join(PROJECT, "Export_SHP")
SHP_NAME = "Egypt_Weather_Stations_WGS84.shp"
CSV_PATH = os.path.join(PROJECT, "Stations_Summary.csv")

LAT_MIN, LAT_MAX = 21.9, 31.7
LON_MIN, LON_MAX = 24.7, 37.0

ISD_HISTORY_URLS = [
    "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv",
]

SCHEMA = ["Station_ID", "Station_Nm", "Station_Ar", "Latitude", "Longitude",
          "Elevation", "Source_DB", "Class_EN", "Class_AR",
          "Start_Year", "End_Year"]

AR_NAMES = {
    "ABU SIMBEL": u"أبو سمبل", "ABU SUWAYR": u"أبو صوير",
    "ABURDEES": u"أبورديس", "AD DANABIQ": u"الدنابيق",
    "ALEXANDRIA INTL": u"الإسكندرية الدولي", "ASWAN INTL": u"أسوان الدولي",
    "ASYUT INTL": u"أسيوط الدولي", "ASYUT-AGRIMET": u"أسيوط الزراعية",
    "BAHARIA": u"الواحات البحرية", "BAHTIM": u"بهتيم",
    "BALTIM": u"بلطيم", "BANHA": u"بنها",
    "BEAR EL ABD": u"بئر العبد", "BORG EL ARAB INTL": u"برج العرب الدولي",
    "CAIRO /ALMAZA": u"القاهرة / ألماظة", "CAIRO ALMAZA": u"القاهرة ألماظة",
    "CAIRO H.Q.": u"القاهرة (المقر الرئيسي)", "CAIRO INTL": u"القاهرة الدولي",
    "CAIRO WEST": u"القاهرة غرب", "DABAA": u"الضبعة",
    "DAHAB": u"دهب", "DAKHLA": u"الداخلة",
    "DAMANHOUR": u"دمنهور", "DAMIETTA": u"دمياط",
    "DARAW": u"دراو", "EDFOU": u"إدفو", "EDFU": u"إدفو",
    "EL ARISH INTL": u"العريش الدولي", "EL ARISH-AGRIMET": u"العريش الزراعية",
    "EL TOR": u"الطور", "EL-SUEZ": u"السويس",
    "ELHASANA": u"الحسنة", "EMBABA": u"إمبابة",
    "FAID": u"فايد", "FARAFRA": u"الفرافرة",
    "FAYOUM": u"الفيوم", "GHAZZA": u"غزة",
    "GIZA-AGRIMET": u"الجيزة الزراعية", "HELWAN": u"حلوان",
    "HURGHADA INTL": u"الغردقة الدولي", "HURGUADA": u"الغردقة",
    "ISMAILIA": u"الإسماعيلية", "ISMAILIA &": u"الإسماعيلية",
    "ISMALIA": u"الإسماعيلية", "JIYANKLIS NEW": u"جانيكليس الجديدة",
    "KHARGA": u"الخارجة", "KOSSEIR": u"القصير",
    "LUXOR INTL": u"الأقصر الدولي", "MADIYAH": u"مادية",
    "MALAWY-AGRIMET": u"ملوي الزراعية", "MARSA ALAM INTL": u"مرسى علم الدولي",
    "MERSA MATRUH": u"مرسى مطروح", "MINYA": u"المنيا",
    "NEKHEL": u"نخل", "PORT ALEXANDRIA": u"ميناء الإسكندرية",
    "PORT DAMIETTA": u"ميناء دمياط", "PORT SAID": u"بورسعيد",
    "PORT SAID/EL GAMIL": u"بورسعيد / الجميل", "PORT TAWFIK": u"بورتوفيق",
    "QENA": u"قنا", "RAFH-AGRIMET": u"رفح الزراعية",
    "RAS EL HIKMA / QISM MOURSY MATROUH": u"رأس الحكمة",
    "RAS SEDR": u"رأس سدر", "ROSETTA": u"رشيد",
    "SALLOUM": u"السلوم", "SALLUM PLATEAU": u"هضبة السلوم",
    "SANT KATREIN AIRPORT": u"مطار سانت كاترين", "SHALATIN": u"شلاتين",
    "SHARK EL OWEINAT INTL": u"شرق العوينات الدولي",
    "SHARM EL SHEIKH INT": u"شرم الشيخ الدولي",
    "SHEBIN EL KOM": u"شبين الكوم", "SIDI BARRANI": u"سيدي براني",
    "SIWA": u"سيوة", "SIWA OASIS ARPT": u"مطار واحة سيوة",
    "SOHAG / SUHAG INTL": u"سوهاج الدولي", "SOHAG AIRPORT": u"مطار سوهاج",
    "SOUTH OF VALLEY UNIVERSITY": u"جامعة جنوب الوادي",
    "ST CATHERINE INTL": u"سانت كاترين الدولي",
    "TABA AIRPORT (RAS ELNAKB)": u"مطار طابا (رأس النقب)",
    "TABA INTL": u"طابا الدولي", "TAHRIR": u"التحرير",
    "TANTA": u"طنطا", "WADI EL NATROON": u"وادي النطرون",
}


def norm_name(s):
    return " ".join(str(s or "").split())


def arabic_name(en_name):
    return AR_NAMES.get(norm_name(en_name), None)


def classify_station(en_name, icao):
    """(Class_EN, Class_AR). BOGUS records return None (excluded)."""
    n = norm_name(en_name).upper()
    if "BOGUS" in n:
        return None
    if "AGRIMET" in n or "AGRIC" in n:
        return ("Agricultural", u"زراعية")
    if "UNIVERSITY" in n:
        return ("Academic", u"بحثية")
    if str(icao or "").upper().startswith("HE"):
        return ("Airport", u"مطار")
    if any(k in n for k in ("INTL", "AIRPORT", "ARPT")):
        return ("Airport", u"مطار")
    if "PORT" in n or "HARBOR" in n:
        return ("Port", u"ميناء")
    return ("Synoptic", u"سينوبتيكية")


def log(msg):
    print("[stations] " + str(msg))


def makedirs_ok(path):
    if not os.path.isdir(path):
        os.makedirs(path)


# ------------------------------------------------------- download helpers ---
def http_get_text(url, timeout=90):
    if _HAS_REQUESTS:
        r = requests.get(url, timeout=timeout,
                         headers={"User-Agent": "Egypt-Stations-Fetcher/1.0"})
        if r.status_code != 200:
            raise RuntimeError("HTTP %s for %s" % (r.status_code, url))
        r.encoding = "utf-8"
        return r.text
    import urllib2
    req = urllib2.Request(url, headers={"User-Agent": "Egypt-Stations-Fetcher/1.0"})
    return urllib2.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def download_isd_history():
    """Returns local cached CSV path (downloads once, reuses cache)."""
    makedirs_ok(DATA_DIR)
    cached = [os.path.join(DATA_DIR, f) for f in sorted(os.listdir(DATA_DIR))
              if f.lower().startswith("isd-history") and f.lower().endswith(".csv")]
    if cached:
        log("using cached ISD history: %s" % os.path.basename(cached[-1]))
        return cached[-1]
    last_err = None
    for url in ISD_HISTORY_URLS:
        try:
            log("downloading %s ..." % url)
            text = http_get_text(url)
            if "USAF" not in text[:2000]:
                raise RuntimeError("unexpected content (no USAF header)")
            stamp = time.strftime("%Y%m%d")
            out = os.path.join(DATA_DIR, "isd-history_%s.csv" % stamp)
            with open(out, "wb") as fh:
                fh.write(text.encode("utf-8"))
            log("saved %s (%d bytes)" % (out, os.path.getsize(out)))
            return out
        except Exception as ex:
            last_err = ex
            log("WARN: %s failed: %s" % (url, ex))
    raise RuntimeError("ISD history download failed: %s" % last_err)


# ------------------------------------------------------------- NOAA parse ---
def parse_float(s, missing=(-999.9, -999.0, -999.0)):
    try:
        f = float(str(s).strip().lstrip("+"))
    except Exception:
        return None
    for m in (-999.9, -999.0, -99.0):
        if abs(f - m) < 1e-9:
            return None
    return f


def parse_year(s):
    try:
        y = int(str(s).strip()[:4])
        return y if 1700 < y < 2100 else None
    except Exception:
        return None


def load_noaa_egypt(csv_path):
    """Parse ISD history, keep CTRY==EG inside the Egypt bbox."""
    stations = []
    with open(csv_path, "rb") as fh:
        # py2 csv needs byte strings: read bytes, decode values afterwards
        reader = csv.DictReader(fh)
        cols = dict((c.strip().upper(), c) for c in (reader.fieldnames or []))
        need = ["USAF", "WBAN", "STATION NAME", "CTRY", "LAT", "LON"]
        if not all(k in cols for k in need):
            raise RuntimeError("unexpected ISD columns: %s" % reader.fieldnames)

        def _d(v):
            if isinstance(v, str):
                return v.decode("utf-8", "replace")
            return v if v is not None else ""

        get = lambda r, k, d="": _d(r.get(cols[k], d))
        for r in reader:
            try:
                if str(get(r, "CTRY")).strip().upper() != "EG":
                    continue
                lat = parse_float(get(r, "LAT"))
                lon = parse_float(get(r, "LON"))
                if lat is None or lon is None:
                    continue  # no precise coordinates -> exclude per spec
                if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                    continue  # outside Egypt -> exclude per spec
                usaf = str(get(r, "USAF")).strip()
                wban = str(get(r, "WBAN")).strip()
                elev = parse_float(get(r, "ELEV(M)" if "ELEV(M)" in cols else "ELEV"))
                nm = str(get(r, "STATION NAME")).strip()
                ic = str(get(r, "ICAO")).strip() if "ICAO" in cols else ""
                cls = classify_station(nm, ic)
                if cls is None:
                    continue  # bogus/test record, excluded
                ar = arabic_name(nm)
                stations.append({
                    "Station_ID": "%s-%s" % (usaf, wban),
                    "Station_Nm": nm,
                    "Station_Ar": ar if ar is not None else nm,
                    "Latitude": lat, "Longitude": lon, "Elevation": elev,
                    "Source_DB": "NOAA",
                    "Class_EN": cls[0], "Class_AR": cls[1],
                    "Start_Year": parse_year(get(r, "BEGIN")),
                    "End_Year": parse_year(get(r, "END")),
                    "_usaf": usaf, "_wban": wban, "_icao": ic,
                })
            except Exception:
                continue
    # dedupe by USAF-WBAN, keep the record with the longest valid period
    best = {}
    for s in stations:
        k = s["Station_ID"]
        span = lambda x: ((x["End_Year"] or 0) - (x["Start_Year"] or 0)) if x["Start_Year"] else -1
        if k not in best or span(s) > span(best[k]):
            best[k] = s
    out = sorted(best.values(), key=lambda s: s["Station_Nm"])
    log("NOAA EG stations in bbox: %d (raw rows kept: %d)" % (len(out), len(stations)))
    return out


# --------------------------------------------------------------- Meteostat ---
def load_meteostat_egypt():
    """Optional enrichment via the meteostat package (needs pandas)."""
    try:
        from meteostat import Stations
    except Exception as ex:
        log("Meteostat skipped (package not installed: %s)" % ex)
        return []
    try:
        df = Stations().bounds((LAT_MIN, LON_MIN), (LAT_MAX, LON_MAX)).fetch()
    except Exception as ex:
        log("Meteostat query failed: %s" % ex)
        return []
    out = []
    for _idx, row in df.iterrows():
        try:
            g = lambda c, d=None: (row[c] if c in row.index and row[c] == row[c] else d)
            lat, lon = g("latitude"), g("longitude")
            if lat is None or lon is None:
                continue
            lat, lon = float(lat), float(lon)
            if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                continue
            wmo = g("wmo")
            try:
                wmo = str(int(float(wmo))) if wmo is not None else ""
            except Exception:
                wmo = str(wmo or "")
            elev = g("elevation")
            try:
                elev = float(elev)
            except Exception:
                elev = None
            _nm = str(g("name") or "").strip()
            _ic = str(g("icao") or "").strip()
            _cls = classify_station(_nm, _ic) or ("Other", u"أخرى")
            _ar = arabic_name(_nm)
            out.append({
                "Station_ID": wmo or ("MS-%s" % (g("icao") or g("id") or "?")),
                "Station_Nm": _nm,
                "Station_Ar": _ar if _ar is not None else _nm,
                "Latitude": lat, "Longitude": lon, "Elevation": elev,
                "Source_DB": "Meteostat",
                "Class_EN": _cls[0], "Class_AR": _cls[1],
                "Start_Year": None, "End_Year": None,
                "_wmo": wmo, "_icao": _ic,
            })
        except Exception:
            continue
    log("Meteostat stations in bbox: %d" % len(out))
    return out


def merge_sources(noaa, met):
    """Merge Meteostat into NOAA by ICAO or proximity+name; flag WMO 62xxx."""
    merged = list(noaa)
    by_icao = dict((s["_icao"], s) for s in merged if s["_icao"])
    added = enriched = 0
    for m in met:
        target = by_icao.get(m["_icao"]) if m["_icao"] else None
        if target is None:
            best, best_d = None, 0.03
            for s in merged:
                d = abs(s["Latitude"] - m["Latitude"]) + abs(s["Longitude"] - m["Longitude"])
                if d < best_d and (not m["Station_Nm"] or m["Station_Nm"][:4].upper() in s["Station_Nm"].upper() or s["Station_Nm"][:4].upper() in m["Station_Nm"].upper()):
                    best, best_d = s, d
            target = best
        if target is None:
            merged.append(m)
            added += 1
        else:
            if m["_wmo"] and m["_wmo"].startswith("62"):
                target["Station_ID"] = m["_wmo"]
                target["Source_DB"] = "WMO/Meteostat"
            elif "Meteostat" not in target["Source_DB"]:
                target["Source_DB"] = target["Source_DB"] + "+Meteostat"
            if target["Elevation"] is None and m["Elevation"] is not None:
                target["Elevation"] = m["Elevation"]
            enriched += 1
    # Egypt's block in both USAF and WMO numbering is 62xxx
    wmo62 = 0
    for s in merged:
        is62 = str(s.get("_usaf", "")).startswith("62") or str(s["Station_ID"]).startswith("62")
        if is62:
            wmo62 += 1
            if s["Source_DB"] == "NOAA":
                s["Source_DB"] = "WMO/NOAA"
    merged.sort(key=lambda s: s["Station_Nm"])
    log("merged: %d total (%d enriched, %d new from Meteostat, %d in WMO 62xxx block)"
        % (len(merged), enriched, added, wmo62))
    return merged


# ------------------------------------------------------------------ outputs ---
def enc(cell):
    if cell is None:
        return ""
    if sys.version_info[0] == 2 and isinstance(cell, unicode):
        return cell.encode("utf-8")
    return cell


def write_csv(path, header, rows):
    fh = open(path, "wb")
    fh.write("\xef\xbb\xbf")  # UTF-8 BOM for Excel/Arabic
    w = csv.writer(fh)
    w.writerow([enc(h) for h in header])
    for r in rows:
        w.writerow([enc(c) for c in r])
    fh.close()


def build_gdb(stations):
    if not _HAS_ARCPY:
        raise RuntimeError("arcpy is required (run with the ArcGIS python).")
    makedirs_ok(PROJECT)
    gdb = os.path.join(PROJECT, GDB_NAME)
    if not arcpy.Exists(gdb):
        arcpy.management.CreateFileGDB(PROJECT, GDB_NAME)
        log("created GDB: %s" % gdb)
    fc = os.path.join(gdb, FC_NAME)
    if arcpy.Exists(fc):
        arcpy.management.Delete(fc)
    wgs = arcpy.SpatialReference(4326)
    arcpy.management.CreateFeatureclass(gdb, FC_NAME, "POINT", spatial_reference=wgs)
    arcpy.management.AddField(fc, "Station_ID", "TEXT", field_length=20)
    arcpy.management.AddField(fc, "Station_Nm", "TEXT", field_length=100)
    arcpy.management.AddField(fc, "Station_Ar", "TEXT", field_length=100)
    arcpy.management.AddField(fc, "Latitude", "DOUBLE")
    arcpy.management.AddField(fc, "Longitude", "DOUBLE")
    arcpy.management.AddField(fc, "Elevation", "DOUBLE")
    arcpy.management.AddField(fc, "Source_DB", "TEXT", field_length=30)
    arcpy.management.AddField(fc, "Class_EN", "TEXT", field_length=30)
    arcpy.management.AddField(fc, "Class_AR", "TEXT", field_length=30)
    arcpy.management.AddField(fc, "Start_Year", "LONG")
    arcpy.management.AddField(fc, "End_Year", "LONG")
    fields = ["SHAPE@XY"] + SCHEMA
    with arcpy.da.InsertCursor(fc, fields) as cur:
        for s in stations:
            cur.insertRow([(s["Longitude"], s["Latitude"])] + [s[c] for c in SCHEMA])
    n = int(arcpy.GetCount_management(fc)[0])
    log("Feature Class %s: %d stations (WGS 1984)" % (FC_NAME, n))
    return fc


def export_shapefile(fc):
    makedirs_ok(SHP_DIR)
    arcpy.conversion.FeatureClassToShapefile([fc], SHP_DIR)
    got = os.path.join(SHP_DIR, FC_NAME + ".shp")
    want = os.path.join(SHP_DIR, SHP_NAME)
    if os.path.abspath(got) != os.path.abspath(want) and os.path.isfile(got):
        sg, sw = os.path.splitext(got)[0], os.path.splitext(want)[0]
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            src, dst = sg + ext, sw + ext
            if os.path.isfile(src):
                if os.path.isfile(dst):
                    os.remove(dst)
                os.rename(src, dst)
    log("Shapefile: %s" % want)
    # enforce UTF-8 codepage so Arabic attributes render correctly
    try:
        with open(os.path.splitext(want)[0] + ".cpg", "wb") as fh:
            fh.write("UTF-8")
        log("Shapefile codepage: UTF-8")
    except Exception as ex:
        log("WARN: cpg write failed: %s" % ex)
    return want


def main():
    t0 = __import__("time").time()
    log("Egypt bbox: lat %.1f-%.1f lon %.1f-%.1f" % (LAT_MIN, LAT_MAX, LON_MIN, LON_MAX))
    cached_csv = download_isd_history()
    noaa = load_noaa_egypt(cached_csv)
    met = load_meteostat_egypt()
    stations = merge_sources(noaa, met)
    if not stations:
        raise RuntimeError("no stations found - nothing to write")
    fc = build_gdb(stations)
    shp = export_shapefile(fc)
    rows = [[s[c] for c in SCHEMA] for s in stations]
    write_csv(CSV_PATH, SCHEMA, rows)
    log("CSV: %s (%d rows)" % (CSV_PATH, len(rows)))
    by_src = {}
    by_cls = {}
    unmapped = []
    for s in stations:
        by_src[s["Source_DB"]] = by_src.get(s["Source_DB"], 0) + 1
        by_cls[s["Class_EN"]] = by_cls.get(s["Class_EN"], 0) + 1
        if s["Station_Ar"] == s["Station_Nm"]:
            unmapped.append(s["Station_Nm"])
    log("by source: %s" % by_src)
    log("by class: %s" % by_cls)
    log("names without Arabic mapping: %d %s" % (len(unmapped), unmapped[:10]))
    lats = [s["Latitude"] for s in stations]
    lons = [s["Longitude"] for s in stations]
    log("extent: lat %.3f-%.3f lon %.3f-%.3f" % (min(lats), max(lats), min(lons), max(lons)))
    log("sample: %s" % stations[0])
    log("DONE in %.1fs -> %s" % (time.time() - t0, PROJECT))
    return {"fc": fc, "shp": shp, "csv": CSV_PATH, "n": len(stations)}


if __name__ == "__main__":
    main()
