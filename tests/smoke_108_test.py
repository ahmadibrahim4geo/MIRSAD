# -*- coding: utf-8 -*-
"""GIS smoke test on ArcMap 10.x python (2.7): synthetic NASA monthly data through
the real arcpy pipeline: master build, SHP/CSV export, IDW+Kriging rasters, .lyr
via arcpy.mapping, dictionaries, wind vectors, isobars, QA. No network."""
import math
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt"))
OUT = os.path.join(BASE, "SmokeTest_108_Output")
PTS = os.path.join(BASE, "Egypt Climate Data", "Egpyt_Climate.gdb", "Point_Sample_Climate")
MASK = os.path.join(BASE, "Egypt Climate Data", "Egpyt_Climate.gdb", "Egypt")
LOG = os.path.join(BASE, "smoke108_progress.log")

mod = type(sys)("m108")
raw = open(PYT, "rb").read()
exec(compile(raw, PYT, "exec"), mod.__dict__)

try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)
arcpy.env.overwriteOutput = True

lfh = open(LOG, "w")

def log(*a):
    t = " ".join(str(x) for x in a)
    lfh.write(t + "\n")
    lfh.flush()

class Msg(object):
    def addMessage(self, t):
        log("[MSG] " + str(t))
    def addWarningMessage(self, t):
        log("[WARN] " + str(t))
    def addErrorMessage(self, t):
        log("[ERR] " + str(t))

messages = Msg()
tool = mod.PowerClimateAtlasGenerator()

if os.path.isdir(OUT):
    shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)

modules = ["Temperature", "Wind", "Precipitation", "Sea Level Pressure"]
gdb_path, paths = tool._build_layout(OUT, modules)
log("layout ok: " + gdb_path)

# spread subset: 9 evenly spaced points whatever the current GDB content is
sub = os.path.join(gdb_path, "smoke_in")
if arcpy.Exists(sub):
    arcpy.management.Delete(sub)
_all = [(r[0], r[1][0], r[1][1]) for r in
        arcpy.da.SearchCursor(PTS, ["OID", "SHAPE@XY"])]
assert len(_all) >= 9, "not enough points: %d" % len(_all)
_all.sort(key=lambda t: (round(t[2], 3), round(t[1], 3)))
_pick = [_all[i * len(_all) // 9][0] for i in range(9)]
arcpy.management.MakeFeatureLayer(
    PTS, "smoke_lyr", '"OID" IN (%s)' % ",".join(str(o) for o in _pick))
n_sel = int(arcpy.GetCount_management("smoke_lyr")[0])
log("selected: " + str(n_sel))
assert n_sel == 9, "selection failed: %s" % n_sel
arcpy.management.CopyFeatures("smoke_lyr", sub)
arcpy.management.Delete("smoke_lyr")

wgs = arcpy.SpatialReference(4326)
pts = tool._extract_points(sub, wgs, messages)
log("extracted: %d" % len(pts))
assert len(pts) == 9, len(pts)

def synth(p, i):
    base = 18.0 + i * 1.2 + (p["lat"] - 25.0) * 0.4
    monthly = {}
    tmean = {}
    for m in range(1, 13):
        tmean[(2025, m)] = base + 6.0 * math.sin(2 * math.pi * (m - 4) / 12.0)
    monthly["T2M"] = dict(tmean)
    monthly["T2M_MAX"] = dict(((2025, m), v + 6.0) for (y, m), v in tmean.items())
    monthly["T2M_MIN"] = dict(((2025, m), v - 6.0) for (y, m), v in tmean.items())
    monthly["PRECTOTCORR"] = dict(((2025, m), (8.0 if m in (1, 2, 12) else 0.2)) for m in range(1, 13))
    monthly["WS10M"] = dict(((2025, m), 4.0 + i * 0.2) for m in range(1, 13))
    monthly["WD10M"] = dict(((2025, m), 320.0) for m in range(1, 13))
    monthly["SLP"] = dict(((2025, m), 101.3 - i * 0.05) for m in range(1, 13))
    monthly["RH2M"] = dict(((2025, m), 55.0 - i) for m in range(1, 13))
    return monthly

results = []
for i, p in enumerate(pts):
    monthly = synth(p, i)
    fields = mod.compute_point_fields(monthly, [2025], modules, "Monthly")
    assert fields["T_Max_Summer_Month_Mean"] is not None, "synth broken"
    assert fields["HI_Annual_Mean"] is not None, "HI broken"
    assert fields["PSL_Annual_Mean"] is not None
    results.append(dict(p, parameter={}, fields=fields, status="OK", error=""))

out_sr = arcpy.Describe(sub).spatialReference  # native (World Mercator, metres)
elfcs = tool._build_element_layers(
    sub, gdb_path, out_sr, results, modules,
    {"y0": 2025, "y1": 2025, "temporal": "Monthly", "interp": "IDW",
     "base_cell": 50000.0, "wind_cell": 200000.0},
    messages.addMessage, messages.addWarningMessage)
log("element layers: %d" % len(elfcs))
assert set(elfcs) == set(modules), elfcs.keys()
for m, fc in elfcs.items():
    assert int(arcpy.GetCount_management(fc)[0]) == 9, (m, fc)
    short = mod.MODULE_SHORT.get(m, m)
    tool._export_shapefile(fc, os.path.join(paths["shp"], short + ".shp"),
                           messages.addMessage, messages.addWarningMessage)
    tool._export_csv(fc, os.path.join(paths["vec"], short + ".csv"),
                     messages.addMessage, messages.addWarningMessage)
    assert os.path.isfile(os.path.join(paths["shp"], short + ".shp")), short
    assert os.path.isfile(os.path.join(paths["vec"], short + ".csv")), short
tool._write_dictionaries(paths["vec"], modules, messages.addMessage)
assert os.path.isfile(os.path.join(paths["vec"], "Metadata_Dictionary.csv"))
assert os.path.isfile(os.path.join(paths["vec"], "Field_Dictionary_Arabic.csv"))

arcpy.CheckOutExtension("Spatial")
try:
    # Mirror execute(): one unit system. Project mask copy to out_sr (metres
    # here: Egypt mask GDB is geographic while points are Mercator metres).
    scratch = os.path.join(OUT, "_scratch")
    if not os.path.isdir(scratch):
        os.makedirs(scratch)
    maskp = os.path.join(scratch, "maskp.shp")
    try:
        if arcpy.Exists(maskp):
            arcpy.management.Delete(maskp)
    except Exception:
        pass
    arcpy.management.Project(MASK, maskp, out_sr)
    MASKP = maskp
    arcpy.env.outputCoordinateSystem = out_sr
    arcpy.env.cellSize = 50000.0
    arcpy.env.mask = maskp
    arcpy.env.extent = arcpy.Describe(maskp).extent
    log("mask projected: %s" % arcpy.Describe(maskp).spatialReference.name)
    reg = tool._interpolate_all(None, modules, paths, 50000.0, "IDW", MASKP,
                                messages.addMessage, messages.addWarningMessage,
                                source_by_module=elfcs)
    log("IDW rasters: %d" % len(reg))
    for item in reg:
        f, rp, lp = item[0], item[1], item[2]
        log("  %s tif=%s lyr=%s" % (f, os.path.isfile(rp), lp))
    assert len(reg) > 0, "no rasters"
    assert all(os.path.isfile(i[1]) for i in reg), "tif missing"
    assert all(i[2] is None for i in reg), "no .lyr should be produced"
    # Kriging + Spline paths on one field
    for meth in ("Ordinary Kriging", "Spline", "Natural Neighbor"):
        lyr = "pwr_smoke_pts"
        try:
            arcpy.management.Delete(lyr)
        except Exception:
            pass
        arcpy.management.MakeFeatureLayer(elfcs["Temperature"], lyr, "T_Annual_Mean IS NOT NULL")
        surf = tool._interp_surface(lyr, "T_Annual_Mean", 50000.0, meth)
        surf.save("in_memory/smoke_%s" % meth.split()[0])
        log("interp OK: %s" % meth)
        arcpy.management.Delete(lyr)
        arcpy.management.Delete("in_memory/smoke_%s" % meth.split()[0])
    # wind vectors + isobars (need Wind + PSL rasters in registry)
    wv = tool._build_wind_vectors(gdb_path, paths, reg, elfcs.get("Wind"), MASKP, out_sr, 200000.0,
                                  messages.addMessage, messages.addWarningMessage)
    log("wind fcs: %s" % wv)
    assert len(wv) == 5, wv
    tool._build_isobars(gdb_path, reg, messages.addMessage, messages.addWarningMessage)
    for n in ("Isobars_PSL_Winter_Mean", "Isobars_PSL_Spring_Mean",
              "Isobars_PSL_Summer_Mean", "Isobars_PSL_Autumn_Mean"):
        assert arcpy.Exists(os.path.join(gdb_path, n)), n
        log("isobar ok: %s" % n)
finally:
    arcpy.CheckInExtension("Spatial")

qa = tool._run_qa(elfcs, paths, modules, reg, results,
                  messages.addMessage, messages.addWarningMessage)
fails = [q for q in qa if not q[1]]
log("QA fails: %s" % fails)
assert not fails, fails
log("SMOKE108 OK")
lfh.close()
