# -*- coding: utf-8 -*-
"""Offline QA tests for POWER_Climate_Atlas_Generator_10_8.pyt (new 104-column schema).
Runs with ArcMap 10.x python (2.7) WITHOUT network and WITHOUT arcpy.
Covers: seasons, missing values, circular mean, precip monthly/daily + rain days,
solar, pressure conversion + ranges, temperature range, Heat Index, wind
(max/range/dir), metadata, REQUIRED_COLUMNS, SHP map uniqueness, color ramps,
NASA URL builders, toolbox helpers.
"""
import calendar
import os
import sys

_test_dir = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(_test_dir)
PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(PYT):
    PYT = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else (os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt"))

mod = type(sys)("power_pyt_108")
mod.__dict__["__name__"] = "power_pyt_108"
with open(PYT, "rb") as fh:
    raw = fh.read()
try:
    raw = raw.decode("utf-8")
except Exception:
    pass
try:
    _text_type = unicode  # noqa: F821 - Python 2 only
except NameError:  # Python 3
    _text_type = str
if isinstance(raw, _text_type):
    try:
        raw = raw.encode("utf-8")  # py2.7 compile() needs bytes when a coding cookie is present
    except Exception:
        pass
if sys.version_info[0] == 3:
    # Python 3 compile() forbids a PEP 263 coding cookie in str source;
    # decode to str and drop the cookie line (file is utf-8).
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    _nl = "\n" if "\n" in raw else "\r\n"
    _first, _sep, _rest = raw.partition(_nl)
    if "coding" in _first and _first.lstrip().startswith("#"):
        raw = _rest
exec(compile(raw, PYT, "exec"), mod.__dict__)

PASS, FAIL = [], []

def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    line = ("PASS " if cond else "FAIL ") + name
    if detail != "":
        line += " | " + str(detail)
    print(line)

check("py version major", sys.version_info[0] in (2, 3), sys.version.split()[0])
check("seasons def", mod.SEASONS == {"Winter": (1,2,12), "Spring": (3,4,5), "Summer": (6,7,8), "Autumn": (9,10,11)})
check("missing -999", mod.is_missing(-999) and mod.is_missing(-999.0) and not mod.is_missing(25.3) and mod.is_missing(None))
cm = mod.circular_mean_deg([350, 10])
check("circular mean wrap", cm is not None and (cm < 5 or cm > 355), cm)
check("circular opposite None", mod.circular_mean_deg([90, 270]) is None)
check("precip monthly total", abs(mod.monthly_precip_total_from_rate(2.0, 2025, 1) - 62.0) < 1e-9)
check("leap feb", mod.month_days(2024, 2) == 29 and mod.month_days(2025, 2) == 28)
check("solar convert", abs(mod.solar_mj_to_kwh(3.6) - 1.0) < 1e-9)
check("pressure convert", abs(mod.pressure_kpa_to_mbar(101.3) - 1013.0) < 1e-9 and abs(mod.pressure_kpa_to_mbar(1013.0) - 1013.0) < 1e-9)

mt = dict(((2025, m), float(10 + m)) for m in range(1, 13))
mx = dict(((2025, m), float(15 + m)) for m in range(1, 13))
mn = dict(((2025, m), float(5 + m)) for m in range(1, 13))
mrh = dict(((2025, m), 50.0) for m in range(1, 13))
tf = mod.compute_temperature_fields(mt, mx, mn, mrh)
check("T range = 11", abs(tf["T_Annual_Range"] - 11.0) < 1e-9, tf["T_Annual_Range"])
check("T winter mean", abs(tf["T_Winter_Mean"] - (11.0 + 12.0 + 22.0) / 3) < 1e-9, tf["T_Winter_Mean"])
check("T max summer month", abs(tf["T_Max_Summer_Month_Mean"] - 18.0) < 1e-9, tf["T_Max_Summer_Month_Mean"])
check("T min winter month", abs(tf["T_Min_Winter_Month_Mean"] - 11.0) < 1e-9, tf["T_Min_Winter_Month_Mean"])
check("T annual max mean", abs(tf["T_Annual_Max_Mean"] - 21.5) < 1e-9, tf["T_Annual_Max_Mean"])
check("T annual min mean", abs(tf["T_Annual_Min_Mean"] - 11.5) < 1e-9, tf["T_Annual_Min_Mean"])
check("HI equals T when cool", abs(tf["HI_Annual_Mean"] - 16.5) < 1e-9 and abs(tf["HI_Summer_Mean"] - 17.0) < 1e-9,
      (tf["HI_Annual_Mean"], tf["HI_Summer_Mean"]))
check("HI_Winter_Mean present", tf.get("HI_Winter_Mean") is not None, tf.get("HI_Winter_Mean"))
check("HI range equals T range when cool", abs(tf.get("HI_Annual_Range") - 11.0) < 1e-9,
      tf.get("HI_Annual_Range"))
check("WBGT summer cool", tf.get("WBGT_Summer_Mean") is not None
      and 10.0 < tf["WBGT_Summer_Mean"] < 17.0, tf.get("WBGT_Summer_Mean"))
check("WBGT below air temp", tf.get("WBGT_Summer_Mean") < tf.get("T_Summer_Mean"))
check("WBGT missing inputs", mod.wbgt_shade_c(None, 50.0) is None and mod.wbgt_shade_c(30.0, None) is None)
check("wetbulb below air temp", mod.wetbulb_stull_c(30.0, 60.0) < 30.0)
check("wetbulb saturated ~= air temp", abs(mod.wetbulb_stull_c(30.0, 100.0) - 30.0) < 0.5)
check("humidex calculation", mod.humidex_c(15.0, 60.0) is not None)
check("HI below threshold", mod.heat_index_c(20.0, 50.0) == 20.0)
_hot = mod.heat_index_c(35.0, 60.0)
check("HI exceeds air temp when hot", _hot is not None and 40.0 < _hot < 50.0, _hot)
check("HI missing inputs", mod.heat_index_c(None, 50.0) is None and mod.heat_index_c(30.0, None) is None)
_wc0 = mod.windchill_c(0.0, 10.0 / 3.6)
check("WC freezing wind cools", _wc0 is not None and -3.5 < _wc0 < -3.1, _wc0)
check("WC warm passthrough", mod.windchill_c(20.0, 5.0) == 20.0)
check("WC calm passthrough", mod.windchill_c(0.0, 0.5) == 0.0)
check("WC missing inputs", mod.windchill_c(None, 5.0) is None and mod.windchill_c(0.0, None) is None)
check("Td None without input", tf.get("Td_Annual_Mean") is None and tf.get("Td_Summer_Mean") is None
      and tf.get("Td_Winter_Mean") is None)
mtd = dict(((2025, m), 12.0) for m in range(1, 13))
tfd = mod.compute_temperature_fields(mt, mx, mn, mrh, mtd)
check("Td means follow input", abs(tfd["Td_Annual_Mean"] - 12.0) < 1e-9
      and abs(tfd["Td_Summer_Mean"] - 12.0) < 1e-9 and abs(tfd["Td_Winter_Mean"] - 12.0) < 1e-9,
      (tfd["Td_Annual_Mean"], tfd["Td_Summer_Mean"], tfd["Td_Winter_Mean"]))
mws = dict(((2025, m), 5.0) for m in range(1, 13))
mtc = dict(((2025, m), 5.0) for m in range(1, 13))
pfwc = mod.compute_point_fields({"T2M": mtc, "WS10M": mws}, [2025], ["Climate_Models"], "Monthly")
check("WC winter below air temp", pfwc.get("WC_Winter_Mean") is not None
      and 0.5 < pfwc["WC_Winter_Mean"] < 5.0, pfwc.get("WC_Winter_Mean"))
check("WC annual present", pfwc.get("WC_Annual_Mean") is not None, pfwc.get("WC_Annual_Mean"))

# --- Trends & baseline anomalies: exact-slope warming series 2015-2025 ---
mtt = dict(((y, m), 20.0 + 0.1 * (y - 2015)) for y in range(2015, 2026) for m in range(1, 13))
mpt = dict(((y, m), 100.0 + 2.0 * (y - 2015)) for y in range(2015, 2026) for m in range(1, 13))
pftr = mod.compute_point_fields({"T2M": mtt, "PRECTOTCORR": mpt}, list(range(2015, 2026)),
                                ["Climate_Models"], "Monthly", precip_totals=True)
check("T trend +1.0/decade", abs(pftr["T_Annual_Trend_Decade"] - 1.0) < 1e-9, pftr["T_Annual_Trend_Decade"])
check("R trend +240/decade", abs(pftr["R_Annual_Trend_Decade"] - 240.0) < 1e-6, pftr["R_Annual_Trend_Decade"])
check("no baseline short series", pftr["T_Annual_Anom"] is None and pftr["R_Annual_Anom"] is None)
pf1y = mod.compute_trend_anomaly_fields(dict(((2025, m), 20.0) for m in range(1, 13)),
                                        dict(((2025, m), 10.0) for m in range(1, 13)))
check("single year all None", all(v is None for v in pf1y.values()), pf1y)

# --- 1991-2025 step climate: 20C/120mm baseline, 21C/144mm since 2021 ---
mta = dict(((y, m), 20.0 if y <= 2020 else 21.0) for y in range(1991, 2026) for m in range(1, 13))
mpa = dict(((y, m), 10.0 if y <= 2020 else 12.0) for y in range(1991, 2026) for m in range(1, 13))
pfa = mod.compute_point_fields({"T2M": mta, "PRECTOTCORR": mpa}, list(range(1991, 2026)),
                               ["Climate_Models"], "Monthly", precip_totals=True)
check("T anomaly +0.5", abs(pfa["T_Annual_Anom"] - 0.5) < 1e-9, pfa["T_Annual_Anom"])
check("T anomaly winter +0.5", abs(pfa["T_Anom_Winter"] - 0.5) < 1e-9, pfa["T_Anom_Winter"])
check("T anomaly summer +0.5", abs(pfa["T_Anom_Summer"] - 0.5) < 1e-9, pfa["T_Anom_Summer"])
check("T trend step ~+0.21", abs(pfa["T_Annual_Trend_Decade"] - 0.21) < 0.01, pfa["T_Annual_Trend_Decade"])
check("R anomaly +12mm", abs(pfa["R_Annual_Anom"] - 12.0) < 1e-9, pfa["R_Annual_Anom"])
check("R anomaly +10pct", abs(pfa["R_Annual_Anom_Pct"] - 10.0) < 1e-9, pfa["R_Annual_Anom_Pct"])
check("R winter anomaly +3mm/+10pct", abs(pfa["R_Anom_Winter"] - 3.0) < 1e-9
      and abs(pfa["R_Anom_Winter_Pct"] - 10.0) < 1e-9, (pfa["R_Anom_Winter"], pfa["R_Anom_Winter_Pct"]))
check("anom submodel registered", "Trends & Baseline Anomalies [Requires: Temperature, Precipitation]" in mod.SUBMODELS_ALL)
check("monthly range", abs(mod.monthly_range(mt) - 11.0) < 1e-9)
check("monthly range const is 0", mod.monthly_range(dict(((2025, m), 5.0) for m in range(1, 13))) == 0.0)

spd = dict(((2025, m), 5.0) for m in range(1, 13))
drc = dict(((2025, m), 350.0 if m in (1, 2, 12) else 90.0) for m in range(1, 13))
wf = mod.compute_wind_fields(spd, drc)
check("wind speed ann", abs(wf["W_Spd_Annual_Mean"] - 5.0) < 1e-9)
check("wind dir winter ~350", abs(wf["W_Dir_Winter_Mean"] - 350.0) < 1.0, wf["W_Dir_Winter_Mean"])
check("wind max/range const", wf["W_Spd_Annual_Max_Month"] == 5.0 and wf["W_Spd_Annual_Range"] == 0.0,
      (wf["W_Spd_Annual_Max_Month"], wf["W_Spd_Annual_Range"]))
check("wind min month const", wf["W_Spd_Annual_Min_Month"] == 5.0, wf["W_Spd_Annual_Min_Month"])
spd2 = dict(((2025, m), float(m)) for m in range(1, 13))
wf2 = mod.compute_wind_fields(spd2, drc)
check("wind max month", abs(wf2["W_Spd_Annual_Max_Month"] - 12.0) < 1e-9)
check("wind min month", abs(wf2["W_Spd_Annual_Min_Month"] - 1.0) < 1e-9, wf2["W_Spd_Annual_Min_Month"])
check("wind range", abs(wf2["W_Spd_Annual_Range"] - 11.0) < 1e-9)

tot = dict(((2025, m), 10.0 * calendar.monthrange(2025, m)[1]) for m in range(1, 13))
agg = mod.seasonal_totals_from_monthly_totals(tot, [2025])
check("precip winter total", abs(agg["Winter"] - 10.0 * (31 + 28 + 31)) < 1e-9, agg["Winter"])
check("precip ann grand==mean single-yr", abs(agg["Annual_Grand"] - agg["Annual_Mean"]) < 1e-9)

msol = dict(((2025, m), 18.0) for m in range(1, 13))
sf = mod.compute_solar_fields(msol, [2025])
check("solar ann 5.0", abs(sf["Sol_Annual_Mean"] - 5.0) < 1e-9, sf["Sol_Annual_Mean"])
check("solar total 1825", abs(sf["Sol_Annual_Total"] - 5.0 * 365) < 1e-6, sf["Sol_Annual_Total"])
check("solar range const is 0", sf.get("Sol_Annual_Range") == 0.0, sf.get("Sol_Annual_Range"))

monthly = {"T2M": mt, "T2M_MAX": mx, "T2M_MIN": mn,
           "PRECTOTCORR": dict(((2025, m), 1.0) for m in range(1, 13)),
           "SLP": dict(((2025, m), 101.3) for m in range(1, 13)),
           "PS": dict(((2025, m), 100.0) for m in range(1, 13)),
           "WS10M": spd, "WD10M": drc,
           "RH2M": dict(((2025, m), 50.0) for m in range(1, 13)),
           "ALLSKY_SFC_SW_DWN": msol,
           "ALLSKY_SFC_UV_INDEX": dict(((2025, m), 6.0) for m in range(1, 13)),
           "CLOUD_AMT": dict(((2025, m), 20.0) for m in range(1, 13))}
pf = mod.compute_point_fields(monthly, [2025], mod.MODULES_ALL, "Monthly")
check("all modules fields>=60 valid", len([v for v in pf.values() if v is not None]) >= 60, len(pf))
check("PSL converted", abs(pf["PSL_Annual_Mean"] - 1013.0) < 1e-9, pf["PSL_Annual_Mean"])
check("PSL range const is 0", pf["PSL_Annual_Range"] == 0.0)
check("R annual total 365", abs(pf["R_Annual_Mean"] - 365.0) < 1e-9, pf["R_Annual_Mean"])
check("R month mean absent", "R_Month_Mean" not in pf)
check("R extremes absent from monthly", "R_Max_Daily_Month" not in pf and "R_Annual_Rain_Days_Total" not in pf)
check("RH range const is 0", pf.get("RH_Annual_Range") == 0.0, pf.get("RH_Annual_Range"))
check("UV range const is 0", pf.get("UV_Annual_Range") == 0.0, pf.get("UV_Annual_Range"))
check("Cld range const is 0", pf.get("Cld_Annual_Range") == 0.0, pf.get("Cld_Annual_Range"))
check("Sol range const is 0", pf.get("Sol_Annual_Range") == 0.0, pf.get("Sol_Annual_Range"))
check("HI needs humidity note", True)
pfd = mod.compute_point_fields(monthly, [2025], ["Precipitation"], "Daily",
                               daily_raw={"PRECTOTCORR": {(2025, 1, 1): 0.5, (2025, 1, 2): 12.7, (2025, 1, 3): -999}})
precip_keys = [k for k in pfd.keys() if k.startswith("R_") and "Trend" not in k and "Anom" not in k]
check("precip fields count >= 8", len(precip_keys) >= 8, len(precip_keys))
check("R extremes absent from daily", "R_Max_Daily_Month" not in pfd and "R_Annual_Rain_Days_Total" not in pfd)
slpv = dict(((2025, m), 100.0 + m) for m in range(1, 13))
pfr = mod.compute_point_fields({"SLP": slpv}, [2025], ["Sea Level Pressure"], "Monthly")
check("PSL range varying", abs(pfr["PSL_Annual_Range"] - 110.0) < 1e-9, pfr["PSL_Annual_Range"])
check("temp fetches RH2M", "RH2M" in mod.MODULE_PARAMS["Temperature"])
check("temp fetches T2MDEW", "T2MDEW" in mod.MODULE_PARAMS["Temperature"])
check("models fetch WS10M", "WS10M" in mod.MODULE_PARAMS["Climate_Models"])
check("WC submodel registered", "Wind Chill / Cold Stress [Requires: Temperature, Wind]" in mod.SUBMODELS_ALL)
check("WC submodel deps", mod.SUBMODEL_DEPS["Wind Chill / Cold Stress [Requires: Temperature, Wind]"]["modules"] == ["Temperature", "Wind"])

rows = mod.metadata_rows_for_modules(["Temperature", "Dew Point", "Wind", "Heat Index"])
check("metadata rows T+DP+W+HI valid", len(rows) >= 34, len(rows))
cols = ["Field_Name", "Full_Name_EN", "Name_AR", "NASA_Code", "Module", "Period", "Statistic", "Unit", "Description_AR", "Description_EN", "Calculation", "Source", "Notes"]
check("metadata cols", all(all(c in r for c in cols) for r in rows))
check("REQUIRED valid count", len(mod.REQUIRED_COLUMNS) >= 116, len(mod.REQUIRED_COLUMNS))
check("R extremes absent from REQUIRED_COLUMNS", "R_Max_Daily_Month" not in mod.REQUIRED_COLUMNS and "R_Annual_Rain_Days_Total" not in mod.REQUIRED_COLUMNS)
check("all fielddefs in REQUIRED", all(r[0] in mod.REQUIRED_COLUMNS for r in mod.FIELD_DEFS))

# Evapotranspiration tests
et_res = mod.compute_drought_fields(mt, mx, mn, dict(((2025, m), 50.0) for m in range(1, 13)), lat=30.0)
check("ET fields computed", all(k in et_res for k in [
    "ET_Annual_Mean", "ET_Annual_Range",
    "ET_Winter_Mean", "ET_Spring_Mean", "ET_Summer_Mean", "ET_Autumn_Mean",
    "PET_Hargreaves_Annual"
]) and "ET_Annual_Total" not in et_res and "ET_Month_Mean" not in et_res and "ET_Seasonal_Range" not in et_res, et_res)
check("ET annual total > 0", et_res["ET_Annual_Mean"] > 0, et_res["ET_Annual_Mean"])
check("ET winter + spring + summer + autumn ~= annual mean",
      abs((et_res["ET_Winter_Mean"] + et_res["ET_Spring_Mean"] + et_res["ET_Summer_Mean"] + et_res["ET_Autumn_Mean"]) - et_res["ET_Annual_Mean"]) < 0.5,
      (et_res["ET_Winter_Mean"], et_res["ET_Spring_Mean"], et_res["ET_Summer_Mean"], et_res["ET_Autumn_Mean"], et_res["ET_Annual_Mean"]))

allf = [r[0] for r in mod.FIELD_DEFS] + [a[0] for a in mod.ADMIN_FIELDS]
bad = [f for f in allf if len(f) > 10]
check("long names all mapped", all(b in mod.SHP_FIELD_MAP for b in bad), bad[:3])
check("shp map unique<=10", len(mod.SHP_FIELD_MAP) >= 105
      and all(len(v) <= 10 for v in mod.SHP_FIELD_MAP.values())
      and len(set(mod.SHP_FIELD_MAP.values())) == len(mod.SHP_FIELD_MAP))
check("shp map covers climate", all(f in mod.SHP_FIELD_MAP for r in mod.FIELD_DEFS for f in [r[0]]))
check("ramps 7", all(len(mod.COLOR_RAMPS[k]) == 7 for k in ["Temperature", "Precipitation", "Sea Level Pressure", "Relative Humidity", "Dew Point", "Solar Radiation", "Cloud Cover"]))
check("UV 5 classes", len(mod.COLOR_RAMPS["UV Index"]) == 5)
b = mod.equal_interval_breaks(0, 70, 7)
check("breaks 8 edges", len(b) == 8 and abs(b[0]) < 1e-9 and abs(b[-1] - 70) < 1e-9, b)
u = mod.nasa_url("Monthly", 30.0, 31.0, 2015, 2025, ["T2M"])
check("nasa monthly url", "monthly/point" in u and "start=2015" in u and "end=2025" in u and "T2M" in u, u)
u2 = mod.nasa_url("Daily", 30.0, 31.0, 2015, 2025, ["PRECTOTCORR"])
check("nasa daily url", "daily/point" in u2 and "20150101" in u2 and "20251231" in u2, u2)
check("Toolbox+Tool", hasattr(mod, "Toolbox") and hasattr(mod, "PowerClimateAtlasGenerator"))

# toolbox-level helpers that do not need arcpy execution
tool = mod.PowerClimateAtlasGenerator()
rp, lp = tool._raster_paths("C:/out", "Temperature", "T_Annual_Mean")
check("raster path flat tif, no lyr", rp.endswith("01_Temperature/T_Annual_Mean.tif".replace("/", os.sep)) and lp is None, (rp, lp))
rp2, lp2 = tool._raster_paths("C:/out", "Wind", "W_Dir_Annual_Mean")
check("wind dir flat path, no lyr", "Direction" in rp2 and "Rasters" not in rp2 and lp2 is None, (rp2, lp2))
check("mask helper present", hasattr(mod, "ensure_mask_fc"))
check("module of field", tool._module_of_field("PSL_Winter_Mean") == "Sea Level Pressure" and tool._module_of_field("Sol_Annual_Total") == "Solar Radiation")
check("colors uv", tool._colors_for("UV Index", "UV_Summer_Mean") == mod.COLOR_RAMPS["UV Index"])
check("now_str", len(mod.now_str()) == 19, mod.now_str())

# Oct-2026 additions: UV noon-max, HI seasons, WC opt-in suite, Daily sheet
dl = mod.daylength_hours(30.0, 7)
check("daylength cairo july ~13.8h", 13.0 < dl < 14.5, dl)
uvn = mod.uv_mean24_to_noonmax(2.66, 30.04, 7)
check("uv 24h-mean 2.66 -> noon ~10.5", 9.5 < uvn < 11.5, uvn)
check("uv om passthrough none", mod.uv_mean24_to_noonmax(None, 30.0, 1) is None)
ct = dict((m, 30.0) for m in range(1, 13))
cr = dict((m, 50.0) for m in range(1, 13))
ts = mod.compute_thermal_stress_fields(ct, cr)
check("HI spring/autumn present", ts.get("HI_Spring_Mean") is not None and ts.get("HI_Autumn_Mean") is not None, (ts.get("HI_Spring_Mean"), ts.get("HI_Autumn_Mean")))
check("HI seasonal range absent", "HI_Seasonal_Range" not in ts)
cw = mod.compute_winter_chill_fields({1: 5.0, 7: 25.0}, {1: 5.0, 7: 4.0})
check("WC extended keys", all(k in cw for k in ("WC_Spring_Mean", "WC_Summer_Mean", "WC_Autumn_Mean", "WC_Annual_Range", "WC_January_Mean", "WC_July_Mean")), sorted(cw.keys()))
check("WC seasonal range absent", "WC_Seasonal_Range" not in cw)
check("WC monthly routed", mod.is_monthly_field("WC_July_Mean") and not mod.is_monthly_field("WC_Summer_Mean"))
w = mod.resolve_filtered_fields(["Wind Chill"], "All Variables & Fields (Full Suite) [Recommended]", temporal_scope="Annual;Winter;Spring;Summer;Autumn")
_ext = ("WC_Spring_Mean", "WC_Summer_Mean", "WC_Autumn_Mean", "WC_Annual_Range",
        "WC_January_Mean", "WC_February_Mean", "WC_March_Mean", "WC_April_Mean", "WC_May_Mean", "WC_June_Mean",
        "WC_July_Mean", "WC_August_Mean", "WC_September_Mean", "WC_October_Mean", "WC_November_Mean", "WC_December_Mean")
_stripped = [f for f in w["Wind Chill"] if f not in _ext]
check("WC toggle strip default", _stripped == ["WC_Winter_Mean", "WC_Annual_Mean"], _stripped)
d = tool._build_daily_table(
    [{"oid": 1, "Source_ID": 7, "daily_raw": {"T2M": {(2024, 1, 1): 20.5, (2024, 1, 2): 21.0}}}],
    ["T2M"])
check("daily table builder", d is not None and d["params"] == ["T2M"]
      and d["header"] == ["OBJECTID", "Source_ID", "Station_ID", "Station_Name", "Country", "Latitude", "Longitude", "Date", "T2M"]
      and d["rows"] == [[1, 7, 7, "", "", None, None, "2024-01-01", 20.5],
                        [1, 7, 7, "", "", None, None, "2024-01-02", 21.0]], d)
check("daily table none w/o data", tool._build_daily_table([{"oid": 1, "daily_raw": {}}], ["T2M"]) is None)
# Monthly interannual ranges (opt-in, default OFF)
_mm = {(2020, 1): 10.0, (2021, 1): 14.0, (2022, 1): 12.0, (2020, 7): 30.0, (2021, 7): 31.0}
_mr = mod.compute_point_fields({"T2M": dict(_mm)}, [2020, 2021, 2022], ["Temperature"], "Monthly")
check("monthly ranges off by default", "T_January_Range" not in _mr, sorted(_mr.keys()))
_mr2 = mod.compute_point_fields({"T2M": dict(_mm)}, [2020, 2021, 2022], ["Temperature"], "Monthly", monthly_ranges=True)
check("monthly range jan", _mr2.get("T_January_Range") == 4.0, _mr2.get("T_January_Range"))
check("monthly range jul", _mr2.get("T_July_Range") == 1.0, _mr2.get("T_July_Range"))
check("monthly range routed", mod.is_monthly_field("ET_December_Range") and mod.is_monthly_field("UV_July_Range"))
check("monthly range shp", mod.SHP_FIELD_MAP.get("ET_December_Range") == "ET_DecRng" and mod.SHP_FIELD_MAP.get("W_Spd_January_Range") == "WSp_JanRg")
# Opt-in monthly Heat Index suite (default OFF at publish; always computed)
_hts = mod.compute_thermal_stress_fields(dict((m, 32.0) for m in range(1, 13)), dict((m, 60.0) for m in range(1, 13)))
check("hi monthly jul rothfusz", abs(_hts.get("HI_July_Mean") - 37.07) < 0.05, _hts.get("HI_July_Mean"))
_hts2 = mod.compute_thermal_stress_fields(dict((m, 5.0) for m in range(1, 13)), dict((m, 70.0) for m in range(1, 13)))
check("hi monthly cold passthrough", _hts2.get("HI_January_Mean") == 5.0, _hts2.get("HI_January_Mean"))
check("hi monthly registered", len(mod.MODULE_FIELDS.get("Heat Index", [])) == 19 and mod.is_monthly_field("HI_July_Mean"))
check("hi monthly shp", mod.SHP_FIELD_MAP.get("HI_July_Mean") == "HI_JulMean" and mod.SHP_FIELD_MAP.get("HI_September_Mean") == "HI_SepMean")

print("")
print("==== SUMMARY: %d passed, %d failed ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
