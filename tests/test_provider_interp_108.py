# -*- coding: utf-8 -*-
"""Tests for: (1) Climate Data Source / Open-Meteo mapping, (2) Interpolation
advanced parameters + dynamic enabling + SA execution. Runs on ArcMap 10.x
python (2.7); the OM pure-logic section needs no network and no arcpy."""
import csv
import io
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(PYT):
    PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt"))
TMP = os.path.join(BASE, "ProvTest_TMP")

if sys.version_info[0] == 2:
    mod = type(sys)("mprov")
    exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)
else:  # Python 3: SourceFileLoader handles the PEP 263 coding cookie
    import importlib.machinery as _ilm
    mod = _ilm.SourceFileLoader("mprov", PYT).load_module()

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = ("PASS " if cond else "FAIL ") + name
    if detail != "":
        line += " | " + str(detail)
    print(line)

# ---------------- 1. Open-Meteo variable mapping ----------------
d, h = mod.om_var_sets(mod.MODULES_ALL)
check("om daily has temp/precip/solar", all(v in d for v in
      ["temperature_2m_mean", "precipitation_sum", "shortwave_radiation_sum"]), d)
check("om hourly has pressure/humidity/cloud/wind/dewpoint",
      all(v in h for v in ["pressure_msl", "surface_pressure",
                           "relative_humidity_2m", "cloud_cover", "wind_speed_10m",
                           "dew_point_2m"]), h)
d2, h2 = mod.om_var_sets(["Temperature", "Heat Index"])
check("temp+HI needs hourly RH+Dew for HI/Td", "relative_humidity_2m" in h2 and "dew_point_2m" in h2 and len(d2) == 3, (d2, h2))
d_pure_t, h_pure_t = mod.om_var_sets(["Temperature"])
check("pure temp needs hourly Dew", h_pure_t == ["dew_point_2m"] and len(d_pure_t) == 3, (d_pure_t, h_pure_t))
check("dewpoint canon T2MDEW", mod.OM_CANON.get("dew_point_2m") == "T2MDEW")
d3, h3 = mod.om_var_sets(["Climate_Models"])
check("models hourly has wind for WC", "wind_speed_10m" in h3 and "dew_point_2m" in h3, h3)

u = mod.om_url(30.0, 31.0, 2015, 2025, ["temperature_2m_mean"], [])
check("om url base+dates", "archive-api.open-meteo.com/v1/archive" in u
      and "start_date=2015-01-01" in u and "end_date=2025-12-31" in u
      and "daily=temperature_2m_mean" in u and "hourly=" not in u, u)
u2 = mod.om_url(30.0, 31.0, 2025, 2025, ["temperature_2m_mean"], ["pressure_msl"])
check("om url hourly included", "hourly=pressure_msl" in u2, u2)

# ---------------- 2. daily/hourly aggregation ----------------
g = mod.om_group_daily(["2025-01-01", "2025-01-02", "2025-02-01"],
                       [10.0, None, 20.0], "mean")
check("om daily mean skips null", g == {(2025, 1): 10.0, (2025, 2): 20.0}, g)
g2 = mod.om_group_daily(["2025-01-01", "2025-01-02"], [2.0, 3.0], "sum")
check("om daily sum", g2 == {(2025, 1): 5.0}, g2)
g3 = mod.om_group_hourly(["2025-01-01T00:00", "2025-01-01T12:00", "2025-02-01T00:00"],
                         [1000.0, 1020.0, None])
check("om hourly mean", g3 == {(2025, 1): 1010.0}, g3)

resp = {"daily": {"time": ["2025-01-01", "2025-01-02"],
                  "temperature_2m_mean": [10.0, 14.0],
                  "precipitation_sum": [2.0, 3.0]},
        "hourly": {"time": ["2025-01-01T00:00", "2025-01-01T12:00"],
                   "pressure_msl": [1010.0, 1020.0]}}
mth, draw = mod.om_parse_response(resp, ["temperature_2m_mean", "precipitation_sum"],
                                  ["pressure_msl"])
check("om parse temp monthly", mth["T2M"] == {(2025, 1): 12.0}, mth.get("T2M"))
check("om parse precip total", mth["PRECTOTCORR"] == {(2025, 1): 5.0},
      mth.get("PRECTOTCORR"))
check("om parse pressure hPa kept", mth["SLP"] == {(2025, 1): 1015.0}, mth.get("SLP"))
check("om daily_raw precip", draw["PRECTOTCORR"] == {(2025, 1, 1): 2.0, (2025, 1, 2): 3.0},
      draw.get("PRECTOTCORR"))

# ---------------- 3. precip totals mode (no x-days inflation) ----------------
mtot = {(2025, 1): 62.0, (2025, 2): 56.0, (2025, 12): 62.0}
pf = mod.compute_point_fields({"PRECTOTCORR": mtot}, [2025], ["Precipitation"],
                              "Monthly", precip_totals=True)
check("om winter mean direct", abs(pf["R_Winter_Mean"] - 180.0) < 1e-9, pf["R_Winter_Mean"])
pf2 = mod.compute_point_fields({"PRECTOTCORR": {(2025, 1): 2.0}}, [2025],
                               ["Precipitation"], "Monthly", precip_totals=False)
check("nasa rate still x-days", pf2["R_Winter_Mean"] is not None and abs(
    mod.monthly_precip_total_from_rate(2.0, 2025, 1) - 62.0) < 1e-9)

# ---------------- 4. provider-aware dictionaries (no arcpy needed) ----------------
try:
    import arcpy  # noqa - required below for params/SA sections
    _HAS_ARCPY = True
except ImportError:
    arcpy = None
    _HAS_ARCPY = False
tool = mod.PowerClimateAtlasGenerator()
if os.path.isdir(TMP):
    shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
def read_dict_csv(path):
    if sys.version_info[0] == 2:
        lines = open(path, "rb").read().decode("utf-8-sig").splitlines()
        rows = list(csv.reader([ln.encode("utf-8") for ln in lines]))
        rows = [[c.decode("utf-8") if isinstance(c, str) else c for c in r] for r in rows]
    else:
        with io.open(path, "r", encoding="utf-8-sig", newline="") as _fh:
            rows = list(csv.reader(_fh))
    return rows[0], [dict(zip(rows[0], r)) for r in rows[1:]]

tool._write_dictionaries(TMP, ["UV Index", "Wind", "Sea Level Pressure"],
                         lambda t: None,
                         "Open-Meteo Historical API (ERA5 Reanalysis)")
head, rows = read_dict_csv(os.path.join(TMP, "Metadata_Dictionary.csv"))
byf = dict((r["Field_Name"], r) for r in rows)
check("om dict source ERA5", all(r["Source"] == "Open-Meteo ERA5" for r in rows),
      set(r["Source"] for r in rows))
check("om UV note mean-of-max", "uv_index_max" in byf["UV_Summer_Mean"]["Notes"],
      byf["UV_Summer_Mean"]["Notes"][:80])
check("om wind speed note hourly", "hourly" in byf["W_Spd_Summer_Mean"]["Notes"],
      byf["W_Spd_Summer_Mean"]["Notes"][:80])
check("om PSL note hourly", "hourly" in byf["PSL_Summer_Mean"]["Notes"],
      byf["PSL_Summer_Mean"]["Notes"][:80])
tool._write_dictionaries(TMP, ["UV Index"], lambda t: None, "NASA POWER API")
head2, rows2 = read_dict_csv(os.path.join(TMP, "Metadata_Dictionary.csv"))
r2 = rows2[0]
check("nasa dict unchanged", r2["Source"] == "NASA POWER" and "uv_index_max" not in r2["Notes"],
      (r2["Source"], r2["Notes"][:60]))

# Sections 5-7 need real arcpy (parameters + Spatial Analyst); the pure-logic
# sections above already ran. Exit here with their summary when arcpy is absent.
if not _HAS_ARCPY:
    if os.path.isdir(TMP):
        shutil.rmtree(TMP, ignore_errors=True)
    print("")
    print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
    print("SKIP arcpy-only sections 5-7 (no ArcGIS in this interpreter)")
    if FAIL:
        print("FAILED:", FAIL)
    sys.exit(0 if not FAIL else 1)

# ---------------- 5. toolbox params + dynamic enabling ----------------
ps = tool.getParameterInfo()
check("param count >= 53", len(ps) >= 53, len(ps))
pdict = dict((p.name, p) for p in ps)
check("provider default NASA", pdict["Climate_Data_Source"].value == "NASA POWER API"
      and "Open-Meteo Historical API (ERA5 Reanalysis)" in pdict["Climate_Data_Source"].filter.list
      and "Copernicus Climate Data Store (CDS / ERA5 / AgERA5)" in pdict["Climate_Data_Source"].filter.list,
      (pdict["Climate_Data_Source"].value, pdict["Climate_Data_Source"].filter.list))
check("om model default era5-land", "ERA5-Land" in pdict["OpenMeteo_Model"].value
      and len(pdict["OpenMeteo_Model"].filter.list) == 3,
      (pdict["OpenMeteo_Model"].value, pdict["OpenMeteo_Model"].filter.list))

tool.updateParameters(ps)
check("om model disabled when NASA", not pdict["OpenMeteo_Model"].enabled)
pdict["Climate_Data_Source"].value = "Open-Meteo Historical API (ERA5 Reanalysis)"
tool.updateParameters(ps)
check("om model enabled when Open-Meteo", pdict["OpenMeteo_Model"].enabled)
pdict["Climate_Data_Source"].value = "Copernicus Climate Data Store (CDS / ERA5 / AgERA5)"
tool.updateParameters(ps)
check("cds key enabled when Copernicus", pdict["CDS_API_Key"].enabled and pdict["OpenMeteo_Model"].enabled)
pdict["Climate_Data_Source"].value = "NASA POWER API"
tool.updateParameters(ps)

check("idw defaults", pdict["IDW_Power"].value == 1.2 and pdict["IDW_Search_Type"].value == "Variable"
      and pdict["IDW_Num_Points"].value == 12, (pdict["IDW_Power"].value, pdict["IDW_Search_Type"].value, pdict["IDW_Num_Points"].value))
check("spline defaults", pdict["Spline_Type"].value == "Tension" and pdict["Spline_Weight"].value == 5.0
      and pdict["Spline_Num_Points"].value == 12, (pdict["Spline_Type"].value, pdict["Spline_Weight"].value, pdict["Spline_Num_Points"].value))
check("krig defaults", pdict["Krig_Model"].value == "Spherical" and pdict["Krig_Type"].value == "Ordinary"
      and pdict["Krig_Num_Points"].value == 12, (pdict["Krig_Model"].value, pdict["Krig_Type"].value, pdict["Krig_Num_Points"].value))

# IDW mode
pdict["Interpolation_Method"].value = "IDW"
tool.updateParameters(ps)
check("IDW enables idw group", all(pdict[n].enabled for n in ("IDW_Curve_Profile", "IDW_Search_Type", "IDW_Num_Points"))
      and not any(pdict[n].enabled for n in ("Krig_Model", "Krig_Type", "Krig_Num_Points", "Spline_Type", "Spline_Weight", "Spline_Num_Points")))

# IDW preset sync
pdict["IDW_Curve_Profile"].value = "Gentle / Smooth (Power 1.2)"
tool.updateParameters(ps)
check("IDW gentle profile syncs 1.2", pdict["IDW_Power"].value == 1.2 and not pdict["IDW_Power"].enabled)

pdict["IDW_Curve_Profile"].value = "Custom Power"
tool.updateParameters(ps)
check("IDW custom profile enables power", pdict["IDW_Power"].enabled)

# Kriging mode
pdict["Interpolation_Method"].value = "Ordinary Kriging"
tool.updateParameters(ps)
check("Kriging enables krig group", all(pdict[n].enabled for n in ("Krig_Model", "Krig_Type", "Krig_Num_Points"))
      and not any(pdict[n].enabled for n in ("IDW_Curve_Profile", "IDW_Power", "IDW_Search_Type", "IDW_Num_Points", "Spline_Type", "Spline_Weight", "Spline_Num_Points")))

# Spline mode
pdict["Interpolation_Method"].value = "Spline"
tool.updateParameters(ps)
check("Spline enables spline group", all(pdict[n].enabled for n in ("Spline_Type", "Spline_Weight", "Spline_Num_Points"))
      and not any(pdict[n].enabled for n in ("IDW_Curve_Profile", "IDW_Power", "IDW_Search_Type", "IDW_Num_Points", "Krig_Model", "Krig_Type", "Krig_Num_Points")))

# Dynamic Map_Add_Modules sync
pdict["Climate_Modules"].values = ["Temperature"]
pdict["Add_To_Map"].value = True
tool.updateParameters(ps)
check("Map_Add_Modules syncs single module", pdict["Map_Add_Modules"].values == ["Temperature"]
      and pdict["Map_Add_Modules"].filter.list == ["Temperature"],
      (pdict["Map_Add_Modules"].values, pdict["Map_Add_Modules"].filter.list))

pdict["Climate_Modules"].values = mod.MODULES_ALL
tool.updateParameters(ps)
check("Map_Add_Modules syncs all modules", set(pdict["Map_Add_Modules"].values) == set(mod.MODULES_ALL)
      and set(pdict["Map_Add_Modules"].filter.list) == set(mod.MODULES_ALL))

# Purge cache at bottom in Maintenance & Cache
check("Purge_Cache at end", ps[-1].name == "Purge_Cache" and ps[-1].category == "Maintenance & Cache")
check("Download_Only phrasing", "Download & Save Point Data Only" in pdict["Download_Only"].displayName)

# ---------------- 6. real SA execution of every branch ----------------
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
sp = arcpy.SpatialReference(4326)
try:
    arcpy.management.Delete("in_memory/px")
except Exception:
    pass
arcpy.management.CreateFeatureclass("in_memory", "px", "POINT", spatial_reference=sp)
arcpy.management.AddField("in_memory/px", "ZV", "DOUBLE")
with arcpy.da.InsertCursor("in_memory/px", ["SHAPE@XY", "ZV"]) as cur:
    for i, (x, y) in enumerate([(30.0, 30.0), (31.0, 30.0), (32.0, 30.0),
                                (30.0, 31.0), (31.0, 31.0), (32.0, 31.0)]):
        cur.insertRow([(x, y), 20.0 + i])
arcpy.management.MakeFeatureLayer("in_memory/px", "pwr_px_lyr")
cases = [
    ("idw-default", "IDW", None, None),
    ("idw-custom", "IDW", {"power": 1.2, "search": "Variable", "npoints": 6, "maxdist": None}, None),
    ("idw-fixed", "IDW", {"power": 2.0, "search": "Fixed", "npoints": 4, "maxdist": 3.0}, None),
    ("krig-ord-sph", "Ordinary Kriging", None, {"model": "Spherical", "ktype": "Ordinary", "npoints": 5}),
    ("krig-univ-gau", "Ordinary Kriging", None, {"model": "Gaussian", "ktype": "Universal", "npoints": 5}),
    ("spline-tension", "Spline", {"spline_type": "Tension", "spline_weight": 5.0, "spline_npoints": 12}, None),
    ("spline-regularized", "Spline", {"spline_type": "Regularized", "spline_weight": 0.1, "spline_npoints": 10}, None),
    ("natneigh", "Natural Neighbor", None, None),
]
for label, meth, io, ko in cases:
    try:
        surf = tool._interp_surface("pwr_px_lyr", "ZV", 0.5, meth, io, ko)
        surf.save("in_memory/px_" + label.replace("-", "_"))
        check("SA " + label, True)
    except Exception as ex:
        check("SA " + label, False, str(ex)[:150])

# ---------------- 7. isobar scheme gating + fixed steps PSL/PS ----------------
msgs, warns = [], []
pdict["Create_Isobars"].value = False
pdict["Climate_Modules"].values = ["Sea Level Pressure", "Surface Pressure"]
tool.updateParameters(ps)
check("isobars off disables", pdict["Pressure_Interval_Scheme"].enabled is False and pdict["Custom_Pressure_Step"].enabled is False)
pdict["Create_Isobars"].value = True
tool.updateParameters(ps)
check("isobars on enables scheme", pdict["Pressure_Interval_Scheme"].enabled is True)
pdict["Pressure_Interval_Scheme"].value = "Global Standard (4 mbar)"
tool.updateParameters(ps)
check("global locks 4 disabled", pdict["Custom_Pressure_Step"].value == 4.0 and pdict["Custom_Pressure_Step"].enabled is False,
      (pdict["Custom_Pressure_Step"].value, pdict["Custom_Pressure_Step"].enabled))
pdict["Pressure_Interval_Scheme"].value = "Local Detailed (2 mbar)"
tool.updateParameters(ps)
check("local locks 2 disabled", pdict["Custom_Pressure_Step"].value == 2.0 and pdict["Custom_Pressure_Step"].enabled is False)
pdict["Pressure_Interval_Scheme"].value = "Custom Interval"
tool.updateParameters(ps)
check("custom opens step", pdict["Custom_Pressure_Step"].enabled is True)
pdict["Climate_Modules"].values = ["Temperature"]
tool.updateParameters(ps)
check("no pressure hides scheme", pdict["Pressure_Interval_Scheme"].enabled is False and pdict["Custom_Pressure_Step"].enabled is False)
gdbi = os.path.join(TMP, "iso.gdb")
arcpy.management.CreateFileGDB(TMP, "iso.gdb")
_rp1 = os.path.join(TMP, "pslwin.tif")
_rp2 = os.path.join(TMP, "pswin.tif")
tool._interp_surface("pwr_px_lyr", "ZV", 0.5, "IDW").save(_rp1)
tool._interp_surface("pwr_px_lyr", "ZV", 0.5, "IDW").save(_rp2)
_reg = [("PSL_Winter_Mean", _rp1, "", "Sea Level Pressure", [], 7),
        ("PS_Winter_Mean", _rp2, "", "Surface Pressure", [], 7)]
tool._build_isobars(gdbi, _reg, msgs.append, warns.append, 0.5)
c1 = int(arcpy.GetCount_management(os.path.join(gdbi, "Isobars_PSL_Winter_Mean"))[0])
c2 = int(arcpy.GetCount_management(os.path.join(gdbi, "Isobars_PS_Winter_Mean"))[0])
check("isobars PSL+PS built", c1 > 0 and c2 > 0, (c1, c2))
for fc in ["Isobars_PSL_Winter_Mean", "Isobars_PS_Winter_Mean"]:
    arcpy.management.Delete(os.path.join(gdbi, fc))
tool._build_isobars(gdbi, _reg, msgs.append, warns.append, 50.0)
d1 = int(arcpy.GetCount_management(os.path.join(gdbi, "Isobars_PSL_Winter_Mean"))[0])
check("finer step more lines", d1 <= c1, (d1, c1))
arcpy.CheckInExtension("Spatial")

if os.path.isdir(TMP):
    shutil.rmtree(TMP, ignore_errors=True)

print("")
print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
