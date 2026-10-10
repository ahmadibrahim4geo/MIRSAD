# -*- coding: utf-8 -*-
"""Trends monthly backfill — ArcGIS Pro (arcpy + Spatial Analyst).

Injects the 60 monthly trend/anomaly fields (T_Anom_<M>, R_Anom_<M>,
R_Anom_<M>_Pct, T_Trend_<M>, R_Trend_<M>) into the existing
Trends_And_Anomalies point layer from Monthly_Climatology/Trends_Monthly.csv
(join on Source_ID, alias = field name, existing values never overwritten),
then interpolates them with the SAME settings recorded in the atlas:

  Method .... Spline (Tension, weight=30, points=12)
  Cell ...... 250 m, snap to the existing T_Annual_Trend_Decade.tif grid
  Mask ...... GDB Egypt polygon (ExtractByMask AFTER interpolation)
  Output .... float32 GeoTIFF + statistics + pyramids, Month/ subfolder

Monthly rasters are grouped by unit for the unified stretch
(T_Anom | R_Anom | R_Anom_Pct | T_Trend | R_Trend), mirroring
monthly_group_key(): C, mm, %, C/dec and mm/dec never share one stretch.

Run with the ArcGIS Pro python:
  "...\\arcgispro-py3\\python.exe" build_trend_monthly_backfill.py [--limit N]
"""

import csv
import json
import os
import sys
import time

try:
    import arcpy
    from arcpy.sa import ExtractByMask, Spline
    arcpy.CheckOutExtension("Spatial")
except Exception as ex:
    raise SystemExit("arcpy/Spatial Analyst required: %s" % ex)

OUT_WS = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
GDB = os.path.join(OUT_WS, "Climate_Database_From_1996_To_2025.gdb")
FC = os.path.join(GDB, "Trends_And_Anomalies")
MASK = os.path.join(GDB, "Egypt")
SNAP_TIF = os.path.join(OUT_WS, "18_Trends_And_Anomalies", "T_Annual_Trend_Decade.tif")
MONTH_DIR = os.path.join(OUT_WS, "18_Trends_And_Anomalies", "Month")
CSV_PATH = os.path.join(OUT_WS, "00_Tables_And_Reports", "Monthly_Climatology",
                         "Trends_Monthly.csv")
LOG_PATH = os.path.join(OUT_WS, "00_Tables_And_Reports",
                         "trend_monthly_backfill.log")

CELL = 250.0
SPLINE_WEIGHT = 30.0
SPLINE_NPOINTS = 12
NODATA = "-3.4028235e+38"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
FIELDS = []
for _mn in MONTHS:
    FIELDS += ["T_Anom_%s" % _mn, "R_Anom_%s" % _mn,
               "R_Anom_%s_Pct" % _mn, "T_Trend_%s" % _mn,
               "R_Trend_%s" % _mn]

GROUPS = [
    ("T_Anom", [f for f in FIELDS if f.startswith("T_Anom")]),
    ("R_Anom", [f for f in FIELDS if f.startswith("R_Anom") and not f.endswith("_Pct")]),
    ("R_Anom_Pct", [f for f in FIELDS if f.startswith("R_Anom") and f.endswith("_Pct")]),
    ("T_Trend", [f for f in FIELDS if f.startswith("T_Trend")]),
    ("R_Trend", [f for f in FIELDS if f.startswith("R_Trend")]),
]


def log(t):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), t)
    print(line)
    sys.stdout.flush()
    with open(LOG_PATH, "a") as fh:
        fh.write(line + "\n")


def inject_fields():
    have = set(f.name for f in arcpy.ListFields(FC))
    missing = [f for f in FIELDS if f not in have]
    for fld in missing:
        arcpy.management.AddField(FC, fld, "DOUBLE", field_alias=fld)
    if missing:
        log("added %d fields (alias=field name)." % len(missing))
    table = {}
    with open(CSV_PATH, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                table[int(float(row["Source_ID"]))] = row
            except Exception:
                pass
    cur_fields = ["Source_ID"] + FIELDS
    n_fill = 0
    with arcpy.da.UpdateCursor(FC, cur_fields) as cur:
        for row in cur:
            try:
                sid = int(row[0])
            except Exception:
                continue
            rec = table.get(sid)
            if not rec:
                continue
            dirty = False
            for i, fld in enumerate(FIELDS, 1):
                if row[i] is None:
                    v = rec.get(fld)
                    if v not in (None, ""):
                        try:
                            row[i] = float(v)
                            dirty = True
                        except Exception:
                            pass
            if dirty:
                cur.updateRow(row)
                n_fill += 1
    log("filled NULLs in %d rows (existing values untouched)." % n_fill)


def save_raster(src_raster, out_tif):
    log("      clip...")
    clipped = ExtractByMask(src_raster, "in_memory/bk_trend_mask")
    if os.path.exists(out_tif):
        arcpy.management.Delete(out_tif)
    log("      copy...")
    arcpy.management.CopyRaster(clipped, out_tif, nodata_value=NODATA)
    log("      stats...")
    arcpy.management.CalculateStatistics(out_tif)
    log("      pyramids...")
    try:
        arcpy.management.BuildPyramids(out_tif, "-1", "BILINEAR", "DEFAULT", "75")
    except Exception as ex:
        log("    pyramid warning: %s" % ex)
    log("      saved.")


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    t0 = time.time()
    if not os.path.isdir(MONTH_DIR):
        os.makedirs(MONTH_DIR)
    arcpy.env.overwriteOutput = True
    arcpy.env.compression = "LZW"
    arcpy.env.tileSize = "128 128"
    arcpy.env.scratchWorkspace = r"C:\Users\ahmad\AppData\Local\Temp\opencode"
    arcpy.env.workspace = r"C:\Users\ahmad\AppData\Local\Temp\opencode"
    arcpy.env.snapRaster = SNAP_TIF
    arcpy.env.extent = arcpy.Describe(MASK).extent
    arcpy.env.outputCoordinateSystem = arcpy.Describe(SNAP_TIF).spatialReference

    inject_fields()

    # in_memory copy: SA tools reject input paths containing spaces.
    try:
        arcpy.management.Delete("in_memory/bk_trend_src")
    except Exception:
        pass
    arcpy.management.CopyFeatures(FC, "in_memory/bk_trend_src")
    src_fc = "in_memory/bk_trend_src"
    try:
        arcpy.management.Delete("in_memory/bk_trend_mask")
    except Exception:
        pass
    arcpy.management.CopyFeatures(MASK, "in_memory/bk_trend_mask")

    have = set(f.name for f in arcpy.ListFields(FC))
    todo = [f for f in FIELDS if f in have]
    if limit:
        todo = todo[:limit]
    # per-group unified stretch from point data
    for gname, gflds in GROUPS:
        gmin, gmax = None, None
        try:
            with arcpy.da.SearchCursor(FC, gflds) as cur:
                for row in cur:
                    for v in row:
                        if v is None:
                            continue
                        fv = float(v)
                        if gmin is None or fv < gmin:
                            gmin = fv
                        if gmax is None or fv > gmax:
                            gmax = fv
        except Exception as ex:
            log("[%s] stretch scan failed: %s" % (gname, ex))
        with open(os.path.join(MONTH_DIR, "Trends_%s_monthly_stretch.json" % gname), "w") as fh:
            json.dump({"group": gname, "min": gmin, "max": gmax,
                       "method": "Spline(Tension,w=%s,n=%s)" % (SPLINE_WEIGHT, SPLINE_NPOINTS),
                       "cell": CELL}, fh, indent=2)
        log("[%s] stretch %.4g..%.4g" % (gname, gmin, gmax))
    n = 0
    for fld in todo:
        out_tif = os.path.join(MONTH_DIR, fld + ".tif")
        if os.path.exists(out_tif):
            continue
        lyr = "bk_trend_interp"
        sel = "in_memory/bk_trend_sel"
        for _o in (lyr, sel):
            try:
                arcpy.management.Delete(_o)
            except Exception:
                pass
        # NOTE: SA Spline rejects a where-clause feature LAYER (spurious
        # ERROR 010819), so export the valid rows to a plain in_memory FC.
        arcpy.conversion.FeatureClassToFeatureClass(
            src_fc, "in_memory", "bk_trend_sel",
            "%s IS NOT NULL" % arcpy.AddFieldDelimiters(src_fc, fld))
        t1 = time.time()
        try:
            surf = Spline(sel, fld, CELL, "TENSION", SPLINE_WEIGHT, SPLINE_NPOINTS)
        except Exception as ex:
            log("    %s FAILED: %s" % (fld, ex))
            try:
                log("    SA messages: %s" % arcpy.GetMessages(2))
            except Exception:
                pass
            continue
        save_raster(surf, out_tif)
        try:
            del surf
        except Exception:
            pass
        for _o in (lyr, sel):
            try:
                arcpy.management.Delete(_o)
            except Exception:
                pass
        n += 1
        log("    [OK %d/%d] %s (%.1fs)" % (n, len(todo), fld + ".tif", time.time() - t1))
    log("Done: %d rasters in %.1f min." % (n, (time.time() - t0) / 60.0))


if __name__ == "__main__":
    main()
