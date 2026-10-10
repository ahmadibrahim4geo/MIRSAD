# -*- coding: utf-8 -*-
"""Trends seasonal backfill — ArcGIS Pro (arcpy + Spatial Analyst).

Injects the 16 seasonal trend/anomaly fields into the existing
Trends_And_Anomalies point layer from
Monthly_Climatology/Trends_Seasonal.csv (join on Source_ID,
alias = field name, existing values never overwritten), then interpolates
them with the SAME settings recorded in the atlas:

  Method .... Spline (Tension, weight=30, points=12)
  Cell ...... 250 m, snap to the existing T_Annual_Trend_Decade.tif grid
  Mask ...... GDB Egypt polygon (ExtractByMask AFTER interpolation)
  Output .... float32 GeoTIFF + statistics + pyramids, element folder
              (seasonal rasters sit next to the annual ones, NOT in Month/)

Run with the ArcGIS Pro python:
  "...\\arcgispro-py3\\python.exe" build_trend_seasonal_backfill.py
"""

import csv
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
OUT_DIR = os.path.join(OUT_WS, "18_Trends_And_Anomalies")
CSV_PATH = os.path.join(OUT_WS, "00_Tables_And_Reports", "Monthly_Climatology",
                        "Trends_Seasonal.csv")
LOG_PATH = os.path.join(OUT_WS, "00_Tables_And_Reports",
                         "trend_seasonal_backfill.log")

CELL = 250.0
SPLINE_WEIGHT = 30.0
SPLINE_NPOINTS = 12
NODATA = "-3.4028235e+38"

FIELDS = ["T_Anom_Spring", "T_Anom_Autumn",
          "R_Anom_Spring", "R_Anom_Spring_Pct",
          "R_Anom_Summer", "R_Anom_Summer_Pct",
          "R_Anom_Autumn", "R_Anom_Autumn_Pct",
          "T_Winter_Trend_Decade", "T_Spring_Trend_Decade", "T_Summer_Trend_Decade", "T_Autumn_Trend_Decade",
          "R_Winter_Trend_Decade", "R_Spring_Trend_Decade", "R_Summer_Trend_Decade", "R_Autumn_Trend_Decade"]


def log(t):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), t)
    print(line)
    sys.stdout.flush()
    with open(LOG_PATH, "a") as fh:
        fh.write(line + "\n")


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    t0 = time.time()
    arcpy.env.overwriteOutput = True
    arcpy.env.compression = "LZW"
    arcpy.env.tileSize = "128 128"
    arcpy.env.scratchWorkspace = r"C:\Users\ahmad\AppData\Local\Temp\opencode"
    arcpy.env.workspace = r"C:\Users\ahmad\AppData\Local\Temp\opencode"
    arcpy.env.snapRaster = SNAP_TIF
    arcpy.env.extent = arcpy.Describe(MASK).extent
    arcpy.env.outputCoordinateSystem = arcpy.Describe(SNAP_TIF).spatialReference

    # --- inject fields ---
    have = set(f.name for f in arcpy.ListFields(FC))
    for fld in FIELDS:
        if fld not in have:
            arcpy.management.AddField(FC, fld, "DOUBLE", field_alias=fld)
            log("added field %s" % fld)
    table = {}
    with open(CSV_PATH, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                table[int(float(row["Source_ID"]))] = row
            except Exception:
                pass
    n_fill = 0
    with arcpy.da.UpdateCursor(FC, ["Source_ID"] + FIELDS) as cur:
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

    # --- in_memory copies (SA rejects spaced paths / where-clause layers) ---
    for _o in ("in_memory/bk_sea_src", "in_memory/bk_sea_mask", "in_memory/bk_sea_sel"):
        try:
            arcpy.management.Delete(_o)
        except Exception:
            pass
    arcpy.management.CopyFeatures(FC, "in_memory/bk_sea_src")
    arcpy.management.CopyFeatures(MASK, "in_memory/bk_sea_mask")

    n = 0
    todo = FIELDS[:limit] if limit else FIELDS
    for fld in todo:
        out_tif = os.path.join(OUT_DIR, fld + ".tif")
        if os.path.exists(out_tif):
            log("[skip] %s exists" % fld)
            continue
        t1 = time.time()
        log("interpolating %s ..." % fld)
        try:
            arcpy.management.Delete("in_memory/bk_sea_sel")
        except Exception:
            pass
        arcpy.conversion.FeatureClassToFeatureClass(
            "in_memory/bk_sea_src", "in_memory", "bk_sea_sel",
            "%s IS NOT NULL" % arcpy.AddFieldDelimiters("in_memory/bk_sea_src", fld))
        try:
            surf = Spline("in_memory/bk_sea_sel", fld, CELL, "TENSION",
                          SPLINE_WEIGHT, SPLINE_NPOINTS)
        except Exception as ex:
            log("    %s SPLINE FAILED: %s" % (fld, ex))
            continue
        try:
            clipped = ExtractByMask(surf, "in_memory/bk_sea_mask")
        except Exception as ex:
            log("    %s CLIP FAILED: %s" % (fld, ex))
            continue
        try:
            arcpy.management.CopyRaster(clipped, out_tif, nodata_value=NODATA)
        except Exception as ex:
            log("    %s COPY FAILED: %s" % (fld, ex))
            continue
        # NOTE: CalculateStatistics hangs (>15 min) on these 26M-cell float32
        # rasters in this environment, so it is intentionally skipped.
        # ArcGIS Pro computes statistics on demand when a raster is opened,
        # and the stretch JSONs already carry the point-data min/max.
        try:
            arcpy.management.BuildPyramids(out_tif, "-1", "NONE", "BILINEAR", "DEFAULT", "75")
        except Exception as ex:
            log("    %s PYRAMID warning: %s" % (fld, ex))
        try:
            del surf, clipped
        except Exception:
            pass
        n += 1
        log("    [OK %d/16] %s (%.1fs)" % (n, fld + ".tif", time.time() - t1))
    log("Done: %d new rasters in %.1f min." % (n, (time.time() - t0) / 60.0))


if __name__ == "__main__":
    main()
