# -*- coding: utf-8 -*-
"""Optional daily climate calculations, independent of ArcPy/Qt, Python 2.7/3.

Canonical inputs: Celsius, kPa, MJ/m2/day, m/s; dates are ISO calendar days.
No legacy calculation is replaced. Missing/invalid dependencies return NULL.
References: FAO-56 equations 7, 8, 11-14, 17, 21-26, 37-40, 47 and 6.
"""
from __future__ import unicode_literals
import datetime as dt
import math

VERSION = "fao56-daily-v1"
HOURLY_OPERATIONS = {"RH2M_MAX": "max", "RH2M_MIN": "min", "VPD_SOURCE": "max"}
EXTRA_HOURLY = {"RH2M_MAX": "relative_humidity_2m", "RH2M_MIN": "relative_humidity_2m",
                "VPD_SOURCE": "vapour_pressure_deficit", "WS10M_CONFIRMED": "wind_speed_10m"}
EXTRA_DAILY = {"SUNSHINE_DURATION": "sunshine_duration"}
POWER_ALIASES={"WS10M_CONFIRMED":"WS10M"}
PM_PRODUCT="Evapotranspiration_Penman_Monteith"
PM_DEPENDENCIES=("T2M_MAX","T2M_MIN","T2MDEW","RH2M_MAX","RH2M_MIN","ALLSKY_SFC_SW_DWN","PS","WS10M_CONFIRMED")
HOURLY_OPERATIONS["WS10M_CONFIRMED"] = "mean"

# Optional outputs remain inside their existing parent module. These are not
# added to legacy MODULE_FIELDS or default dependencies.
VARIABLES = {
    "RHmax": dict(module="Relative Humidity", prefix="RHmax", unit="percent", raw="RH2M_MAX", dependencies=("RH2M_MAX",)),
    "RHmin": dict(module="Relative Humidity", prefix="RHmin", unit="percent", raw="RH2M_MIN", dependencies=("RH2M_MIN",)),
    "ea": dict(module="Relative Humidity", prefix="ea", unit="kPa", dependencies=("T2M_MAX","T2M_MIN","T2MDEW","RH2M_MAX","RH2M_MIN")),
    "es": dict(module="Relative Humidity", prefix="es", unit="kPa", dependencies=("T2M_MAX","T2M_MIN")),
    "VPD_Source": dict(module="Relative Humidity", prefix="VPD_Source", unit="kPa; daily maximum", raw="VPD_SOURCE", dependencies=("VPD_SOURCE",)),
    "VPD_FAO56": dict(module="Relative Humidity", prefix="VPD_FAO56", unit="kPa", dependencies=("T2M_MAX","T2M_MIN","T2MDEW","RH2M_MAX","RH2M_MIN")),
    "Trange": dict(module="Temperature", prefix="Trange", unit="deg_C difference", dependencies=("T2M_MAX","T2M_MIN")),
    "Sunshine_Hours": dict(module="Solar Radiation", prefix="Sunshine", unit="hours/day", dependencies=("SUNSHINE_DURATION",)),
    "Ra": dict(module="Solar Radiation", prefix="Ra", unit="MJ/m2/day", dependencies=()),
    "U2": dict(module="Wind", prefix="U2", unit="m/s at 2m", dependencies=("WS10M_CONFIRMED",)),
    "Rn_FAO56": dict(module="Solar Radiation", prefix="Rn_FAO56", unit="MJ/m2/day", dependencies=("T2M_MAX","T2M_MIN","T2MDEW","RH2M_MAX","RH2M_MIN","ALLSKY_SFC_SW_DWN")),
}


def selected_dependencies(selected, modules):
    required = set()
    if len(set(selected)) != len(selected):
        raise ValueError("Duplicate supplementary variable")
    for name in selected:
        if name not in VARIABLES:
            raise ValueError("Unknown supplementary variable: " + str(name))
        if VARIABLES[name]["module"] not in modules:
            raise ValueError("Select the parent module for " + name + ": " + VARIABLES[name]["module"])
        required.update(VARIABLES[name]["dependencies"])
    return sorted(required)


def validate_et_methods(methods,modules):
    if methods is None:return ["HG"] if "Evapotranspiration" in modules else []
    if not isinstance(methods,(list,tuple)) or not methods or len(set(methods))!=len(methods) or any(m not in ("HG","PM") for m in methods):
        raise ValueError("Select HG, PM or both evapotranspiration methods")
    if "Evapotranspiration" not in modules:raise ValueError("Select Evapotranspiration before choosing its methods")
    return list(methods)


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = float(value)
        return result if not math.isnan(result) and not math.isinf(result) and result > -900 else None
    except (TypeError, ValueError, OverflowError):
        return None


def saturation_vp(temperature):
    t = number(temperature)
    if t is None or t <= -237.3:
        return None
    try:
        return number(.6108 * math.exp(17.27 * t / (t + 237.3)))
    except (OverflowError, ValueError):
        return None


def saturation_mean(tmax, tmin):
    hi, lo = number(tmax), number(tmin)
    if hi is None or lo is None or hi < lo:
        return None
    a, b = saturation_vp(hi), saturation_vp(lo)
    return (a + b) / 2. if a is not None and b is not None else None


def actual_vp(tmax=None, tmin=None, dewpoint=None, rhmax=None, rhmin=None):
    """Return (ea, method); no unlabelled RHmean/Tmin estimation fallback."""
    dew = saturation_vp(dewpoint)
    if dew is not None:
        return dew, "FAO56_eq14_dewpoint"
    hi, lo, rhi, rlo = [number(v) for v in (tmax, tmin, rhmax, rhmin)]
    if any(v is None for v in (hi, lo, rhi, rlo)) or hi < lo or not 0 <= rlo <= rhi <= 100:
        return None, "missing_valid_dewpoint_or_RH_extrema"
    a, b = saturation_vp(hi), saturation_vp(lo)
    if a is None or b is None:
        return None, "invalid_temperature"
    return (b * rhi / 100. + a * rlo / 100.) / 2., "FAO56_eq17_RH_extrema"


def radiation_ra(latitude, day):
    """Daily extraterrestrial energy MJ/m2/day (not legacy monthly water equivalent)."""
    lat = number(latitude)
    if lat is None or not -90 <= lat <= 90:
        return None
    if not isinstance(day, dt.date):
        try:
            day = dt.datetime.strptime(str(day), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None
    doy = day.timetuple().tm_yday
    phi = math.radians(lat)
    dr = 1 + .033 * math.cos(2 * math.pi * doy / 365.)
    delta = .409 * math.sin(2 * math.pi * doy / 365. - 1.39)
    angle = -math.tan(phi) * math.tan(delta)
    sunset = math.acos(max(-1., min(1., angle)))
    energy = 24 * 60 / math.pi * .0820 * dr * (
        sunset * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(sunset))
    return max(0., energy)  # analytic polar-night limit; not a missing-data replacement


def wind_at_2m(speed, height):
    speed, height = number(speed), number(height)
    if speed is None or height is None or speed < 0 or 67.8 * height - 5.42 <= 1:
        return None
    return speed * 4.87 / math.log(67.8 * height - 5.42)


def pressure_from_elevation(elevation):
    z = number(elevation)
    if z is None or 293 - .0065 * z <= 0:
        return None
    return 101.3 * ((293 - .0065 * z) / 293.) ** 5.26


def reference_net_radiation(rs, ra, tmax, tmin, ea, elevation):
    """FAO-56 grass-reference Rn, with known Z and no assumed sea-level altitude."""
    rs, ra, hi, lo, ea, z = [number(v) for v in (rs, ra, tmax, tmin, ea, elevation)]
    if any(v is None for v in (rs, ra, hi, lo, ea, z)):
        return None
    if rs < 0 or ra <= 0 or ea < 0 or hi < lo or lo <= -273.16:
        return None
    rso = (.75 + .00002 * z) * ra
    if rso <= 0:
        return None
    ratio = min(1., rs / rso)  # FAO-56 Eq39 explicitly bounds Rs/Rso above by 1.
    try:
        longwave = 4.903e-9 * ((hi + 273.16) ** 4 + (lo + 273.16) ** 4) / 2. * (
            .34 - .14 * math.sqrt(ea)) * (1.35 * ratio - .35)
        return number(.77 * rs - longwave)
    except OverflowError:
        return None


def penman_monteith(tmax, tmin, u2, es, ea, rn, pressure, soil_heat=0.):
    """FAO-56 daily reference ETo mm/day. Negative results are retained, not clipped."""
    hi, lo, wind, es, ea, rn, pressure, soil_heat = [number(v) for v in (
        tmax, tmin, u2, es, ea, rn, pressure, soil_heat)]
    if any(v is None for v in (hi, lo, wind, es, ea, rn, pressure, soil_heat)):
        return None
    t = hi / 2. + lo / 2.
    if hi < lo or t <= -237.3 or wind < 0 or pressure <= 0 or ea < 0 or es < ea:
        return None
    try:
        delta = 4098 * saturation_vp(t) / ((t + 237.3) ** 2)
        gamma = .000665 * pressure
        return number((.408 * delta * (rn - soil_heat) + gamma * 900. / (t + 273.) * wind * (es - ea)) / (
            delta + gamma * (1 + .34 * wind)))
    except (OverflowError, ZeroDivisionError):
        return None


def hourly_to_daily(timestamps, values, operation, unit="source unit", scale=1., bounds=None):
    """Strict UTC hourly slots -> (daily values, per-day processing/coverage).

    A duplicate, off-hour stamp, unequal array lengths or missing hour cannot
    produce a complete day's extreme. A failed day is described, never zero.
    Input values are not modified. Scale is applied after temporal aggregation.
    """
    if operation not in ("max", "min", "mean", "sum"):
        raise ValueError("Unsupported hourly aggregation: " + str(operation))
    if len(timestamps) != len(values):
        raise ValueError("Hourly timestamp/value array length mismatch")
    groups, invalid = {}, set()
    for stamp, value in zip(timestamps, values):
        stamp = str(stamp)
        try:
            parsed = dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M")
        except ValueError:
            raise ValueError("Hourly input requires explicit UTC YYYY-MM-DDTHH:MM timestamps")
        day, hour = str(parsed.date()), parsed.hour
        slots = groups.setdefault(day, {})
        if parsed.minute != 0 or hour in slots:
            invalid.add(day)
        v = number(value)
        if v is not None and bounds is not None and not bounds[0] <= v <= bounds[1]:
            v = None
        slots[hour] = v
    daily, processing = {}, {}
    for day, slots in groups.items():
        valid = [v for v in slots.values() if v is not None]
        complete = day not in invalid and len(valid) == 24 and set(slots) == set(range(24))
        processing[day] = dict(input_temporal="hourly", output_temporal="daily", operation=operation,
                               timezone="UTC", valid_samples=len(valid), expected_samples=24, unit=unit,
                               scale=scale, status="complete" if complete else "incomplete_or_duplicate_hour",
                               note="Daily value derived from complete hourly data" if complete else "Incomplete/invalid hourly input; no daily value")
        if complete:
            value = max(valid) if operation == "max" else min(valid) if operation == "min" else sum(valid)
            if operation == "mean":
                value /= 24.
            daily[day] = value * scale
    return daily, processing


def derive_day(raw, latitude, day, elevation=None, wind_height=None):
    """Calculate optional components without changing any input/source value.

    Caller must supply known elevation/measurement height, not infer either
    from a generic variable key or the enrichment checkbox. Results are a
    distinct component bundle; selecting columns/exporting them is separate.
    """
    hi, lo = number(raw.get("T2M_MAX")), number(raw.get("T2M_MIN"))
    es = saturation_mean(hi, lo)
    ea, ea_method = actual_vp(hi, lo, raw.get("T2MDEW"), raw.get("RH2M_MAX"), raw.get("RH2M_MIN"))
    ra = radiation_ra(latitude, day)
    confirmed_wind = number(raw.get("WS10M_CONFIRMED"))
    u2 = wind_at_2m(confirmed_wind if confirmed_wind is not None else raw.get("WS10M"),
                    10. if confirmed_wind is not None else wind_height)
    pressure = number(raw.get("PS"))
    pressure_method = "source_surface_pressure"
    if pressure is None or pressure <= 0:
        pressure, pressure_method = pressure_from_elevation(elevation), "FAO56_eq7_known_elevation"
    rn = reference_net_radiation(raw.get("ALLSKY_SFC_SW_DWN"), ra, hi, lo, ea, elevation)
    sunshine = number(raw.get("SUNSHINE_DURATION"))
    vpd = es - ea if es is not None and ea is not None and es >= ea else None
    values = dict(Trange=hi - lo if hi is not None and lo is not None and hi >= lo else None,
                  ea=ea, es=es, VPD_FAO56=vpd, Ra=ra, U2=u2, Rn_FAO56=rn,
                  Sunshine_Hours=sunshine / 3600. if sunshine is not None and 0 <= sunshine <= 86400 else None,
                  ET0_PM=penman_monteith(hi, lo, u2, es, ea, rn, pressure))
    metadata = dict(formula_version=VERSION, ea_method=ea_method, pressure_method=pressure_method,
                    input_elevation=elevation, wind_measurement_height_m=10. if confirmed_wind is not None else wind_height,
                    Rn_method="FAO56_reference_grass_albedo_0.23", G_MJ_m2_day=0.,
                    T_method="(Tmax+Tmin)/2", pressure_kPa=pressure,
                    missing_outputs=sorted(k for k, v in values.items() if v is None))
    if values["ET0_PM"] is not None and values["ET0_PM"] < 0:
        metadata["quality_note"] = "negative_reference_ET_retained_no_clipping"
    return values, metadata
