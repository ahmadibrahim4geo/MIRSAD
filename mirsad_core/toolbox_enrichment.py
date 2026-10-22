# -*- coding: utf-8 -*-
"""Opt-in daily additions for Point/Station Toolbox, Python 2.7/3.

No ArcPy or Desktop imports. Legacy observations/calculations are never changed.
Supplementary inputs use their own declared source pipeline and audit files.
"""
from __future__ import unicode_literals
import calendar
import datetime as dt
from .daily_climate import VARIABLES, VERSION, derive_day, number, selected_dependencies

ORDER = ("RHmax", "RHmin", "ea", "es", "VPD_Source", "VPD_FAO56", "Trange",
         "Sunshine_Hours", "Ra", "U2", "Rn_FAO56")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
SEASONS = (("Winter", (12, 1, 2)), ("Spring", (3, 4, 5)),
           ("Summer", (6, 7, 8)), ("Autumn", (9, 10, 11)))
DESCRIPTIONS = {
    "RHmax": ("Maximum relative humidity", "الرطوبة النسبية العظمى", "max(hourly RH)"),
    "RHmin": ("Minimum relative humidity", "الرطوبة النسبية الصغرى", "min(hourly RH)"),
    "ea": ("Actual vapour pressure", "ضغط البخار الفعلي", "FAO56 eq14 dewpoint; otherwise eq17 RH extrema"),
    "es": ("Mean saturation vapour pressure", "متوسط ضغط البخار المشبع", "[e(Tmax)+e(Tmin)]/2; FAO56 eq11-12"),
    "VPD_Source": ("Source daily maximum vapour pressure deficit", "أقصى عجز يومي لضغط البخار من المصدر", "max(hourly source VPD); distinct from FAO56 daily deficit"),
    "VPD_FAO56": ("FAO56 daily vapour pressure deficit", "عجز ضغط البخار اليومي وفق FAO56", "es-ea"),
    "Trange": ("Daily temperature range", "المدى الحراري اليومي", "Tmax-Tmin"),
    "Sunshine_Hours": ("Daily sunshine duration", "مدة السطوع الشمسي اليومية", "source sunshine seconds / 3600"),
    "Ra": ("Daily extraterrestrial radiation", "الإشعاع اليومي خارج الغلاف الجوي", "FAO56 eq21-26; latitude and day of year"),
    "U2": ("Wind speed adjusted to 2 metres", "سرعة الرياح المعدلة إلى ارتفاع مترين", "FAO56 eq47; confirmed measurement height required"),
    "Rn_FAO56": ("FAO56 reference grass net radiation", "صافي الإشعاع لمرجع عشبي وفق FAO56", "FAO56 eq37-40; albedo 0.23; known elevation required"),
}
DAILY_HEADER = ["Point_OID", "Station_ID", "Station_Name", "Date", "Variable", "Unit", "Value"]
DICTIONARY_HEADER = ["Module", "Field_Name", "Default_Alias", "Variable", "Period", "Unit",
                     "Statistic", "Name_EN", "Name_AR", "Inputs", "Formula", "Missing_Rule", "Reference"]
METHOD_HEADER = ["Point_OID", "Variable", "Requested_Start", "Requested_End", "Valid_Days",
                 "Expected_Days", "Sources", "Elevation_m", "Formula_Version", "Note_EN", "Note_AR"]
HOURLY_HEADER = ["Point_OID", "Variable", "Input", "Date", "Source", "Input_Temporal",
                 "Output_Temporal", "Operation", "Timezone", "Valid_Samples", "Expected_Samples",
                 "Unit", "Scale", "Status", "Used_In_Optional_Input", "Note_EN", "Note_AR"]


def parameter_name(variable):
    return "Supplementary_" + variable


def parameters(arcpy, arabic=False):
    params = []
    for name in ORDER:
        spec = VARIABLES[name]
        english, arabic_name, formula = DESCRIPTIONS[name]
        p = arcpy.Parameter(displayName=(arabic_name if arabic else english) + " (" + name + ")",
                            name=parameter_name(name), datatype="GPBoolean",
                            parameterType="Optional", direction="Input")
        p.value = False
        p.category = ("إضافات: " if arabic else "Supplementary: ") + spec["module"]
        p.description = (
            ("إضافة اختيارية داخل العنصر المحدد؛ تتطلب المسار اليومي. " if arabic else
             "Optional output within its selected parent module; requires Daily processing. ") +
            "Unit: " + spec["unit"] + ". " + formula + ". " +
            ("الوحدات الإضافية ثابتة كما هي موضحة، مع حفظ الحقول والقيم الخام السابقة. " if arabic else
             "Supplementary units are canonical as stated; existing fields and raw values are preserved. ") +
            "Hourly_Processing records UTC sample counts; incomplete inputs remain NULL. " +
            "Rn requires a known metre elevation attribute; no sea-level default.")
        params.append(p)
    # Calculation is independent from optional interpolation.
    p = arcpy.Parameter(displayName="راسترات الإضافات الاختيارية" if arabic else "Interpolate supplementary fields",
                        name="Supplementary_Rasters", datatype="GPBoolean",
                        parameterType="Optional", direction="Input")
    p.value = False
    p.category = "إضافات: الراستر" if arabic else "Supplementary: Raster"
    p.description = "Optional supplementary mean/range surfaces; coverage counts are never interpolated."
    params.append(p)
    return params


def selection(pdict):
    return [name for name in ORDER if pdict.get(parameter_name(name)) is not None
            and bool(pdict[parameter_name(name)].value)]


def available(name, provider):
    """Match the implemented public point-source supplementary protocols."""
    from .climate_products import descriptor
    from .climate_sources import pipeline_sources
    if descriptor(provider):
        return False  # Product adapters retain their original daily/monthly outputs.
    sources = pipeline_sources(provider) or ()
    hourly = "Open-Meteo" in sources or "Open-Meteo" in (provider or "")
    if name in ("RHmax", "RHmin", "VPD_Source", "Sunshine_Hours"):
        return hourly
    if name == "U2":
        return hourly or "NASA POWER" in sources or "NASA" in (provider or "")
    return True  # Formulas still enforce actual dependencies and missingness.


def validate(selected, modules, temporal, offline, provider):
    if not selected:
        return
    selected_dependencies(selected, modules)
    from .climate_products import descriptor
    product = descriptor(provider)
    if offline or "Daily" not in (temporal or "") and "يومي" not in (temporal or ""):
        raise ValueError("Supplementary variables require the online Daily workflow; monthly values cannot become daily observations.")
    if product and product["temporal"] != "Daily":
        raise ValueError("This monthly/composite product cannot supply daily supplementary variables.")
    unsupported = [name for name in selected if not available(name, provider)]
    if unsupported:
        raise ValueError("Supplementary variables are not integrated with this selected source: " + ", ".join(unsupported))


def summarize(values, start, end, prefix, scopes=None, ranges=False, accumulation=False):
    """Same conservative daily-period contract as Desktop; no gap estimates.

    DJF contains months 12/1/2 of the same calendar year, the atlas convention.
    Complete periods contribute one yearly mean; missing periods remain NULL.
    """
    monthly = {}
    for year in range(start.year, end.year + 1):
        for month in range(1, 13):
            dates = [dt.date(year, month, d) for d in range(1, calendar.monthrange(year, month)[1] + 1)]
            if start <= dates[0] and dates[-1] <= end and all(number(values.get(d)) is not None for d in dates):
                monthly[(year, month)] = [float(values[d]) for d in dates]
    fields = {}
    for index, month in enumerate(MONTHS, 1):
        means = [sum(v) if accumulation else sum(v) / len(v) for (y, m), v in monthly.items() if m == index]
        fields[prefix + "_" + month + "_Mean"] = sum(means) / len(means) if means else None
        if ranges:
            fields[prefix + "_" + month + "_Range"] = max(means) - min(means) if len(means) >= 2 else None
    for period, months in (("Annual", tuple(range(1, 13))),) + SEASONS:
        if scopes is not None and period not in scopes and not (period != "Annual" and "Seasonal" in scopes):
            continue
        per_year = []
        for year in range(start.year, end.year + 1):
            if all((year, month) in monthly for month in months):
                data = [v for month in months for v in monthly[(year, month)]]
                per_year.append(sum(data) if accumulation else sum(data) / len(data))
        fields[prefix + "_" + period + "_Mean"] = sum(per_year) / len(per_year) if per_year else None
    if scopes is None or "Annual" in scopes:
        climatology = [fields[prefix + "_" + month + "_Mean"] for month in MONTHS]
        fields[prefix + "_Annual_Range"] = max(climatology) - min(climatology) if all(v is not None for v in climatology) else None
    fields[prefix + "_Valid_Days"] = sum(number(values.get(start + dt.timedelta(days=i))) is not None
                                         for i in range((end - start).days + 1))
    fields[prefix + "_Expected_Days"] = (end - start).days + 1
    return fields


def variable_for_field(field):
    # Longest first: es/ea etc cannot consume another variable's prefix.
    return next((name for name in ORDER if field.startswith(VARIABLES[name]["prefix"] + "_")), None)


def fields_by_module(selected, start, end, scopes=None, ranges=False):
    grouped = {}
    for name in selected:
        spec = VARIABLES[name]
        fields = list(summarize({}, start, end, spec["prefix"], scopes, ranges))
        # Stable schema independent of Python dictionary iteration order.
        grouped.setdefault(spec["module"], []).extend(sorted(fields))
    return grouped


def field_definition(name, field):
    spec = VARIABLES[name]
    suffix = field[len(spec["prefix"]) + 1:]
    is_count = suffix in ("Valid_Days", "Expected_Days")
    statistic = ("Count" if is_count else "Range of climatic monthly means" if suffix == "Annual_Range" else
                 "Interannual range of same-month means" if suffix.endswith("Range") else "Mean of complete daily periods")
    period = "Selected interval" if is_count else suffix.rsplit("_", 1)[0]
    en, ar, formula = DESCRIPTIONS[name]
    return [spec["module"], field, field, name, period, "days" if is_count else spec["unit"],
            statistic, en, ar, ", ".join(spec["dependencies"]) +
            ("; latitude/date" if name in ("Ra", "Rn_FAO56") else "") +
            ("; known elevation in metres" if name == "Rn_FAO56" else ""), formula,
            "NULL for incomplete period/dependencies; valid zero retained; missing is never zero",
            "https://open-meteo.com/en/docs/historical-weather-api" if "raw" in spec else
            "https://www.fao.org/4/x0490e/x0490e00.htm"]


def download(points, selected, start, end, provider, model, folder, progress, cancelled, session=None, fetch=None, credentials=None, required=None):
    """A separate input contract avoids replacing any legacy raw observations."""
    from . import hybrid_pipeline as pipeline
    from .climate_sources import pipeline_sources
    from .climate_products import descriptor, run
    stations, identities = {}, []
    for point in points:
        usaf, wban = point.get("station_id", ""), point.get("wban", "")
        key = "%s|%s|%.8f|%.8f" % (usaf, wban, point["lat"], point["lon"])
        identities.append(key)
        stations[key] = dict(station_key=key, usaf=usaf, wban=wban, ghcn_id=point.get("ghcn_id"),
                             latitude=point["lat"], longitude=point["lon"], name=point.get("station_name", ""))
    required = selected_dependencies(selected, list(set(VARIABLES[name]["module"] for name in selected))) if required is None else list(required)
    # Astronomical-only calculations need neither an account nor a network call.
    if not required:
        return [dict(station=stations[key], series={}, provenance={}, source_summary="Astronomical calculation") for key in identities]
    ordered = [stations[key] for key in sorted(stations)]
    if descriptor(provider):
        result = run(provider, ordered, start, end, required, folder, progress, cancelled,
                     session=session, credentials=credentials)
    else:
        sources = pipeline_sources(provider)
        if not sources:
            sources = ("Open-Meteo", "NASA POWER") if "Open-Meteo" in provider else ("NASA POWER",)
        result = pipeline.run(ordered, start, end, required, folder, progress, cancelled,
                              model=model, session=session, sources=sources, fetch=fetch)
    by_key = dict((record["station"]["station_key"], record) for record in result)
    return [by_key[key] for key in identities]


def calculate(point, source, selected, start, end, scopes=None, ranges=False, cancelled=None):
    """Return fields, daily values and per-day input provenance, without mutation."""
    cancelled = cancelled or (lambda: False)
    elevation = number(point.get("calculation_elevation"))
    computed = dict((name, {}) for name in selected)
    audit = dict((name, []) for name in selected)
    for offset in range((end - start).days + 1):
        if offset % 128 == 0 and cancelled():
            from .hybrid_pipeline import Cancelled
            raise Cancelled("Cancelled")
        date = start + dt.timedelta(days=offset)
        text = str(date)
        inputs = dict((p, values.get(text)) for p, values in source.get("series", {}).items())
        for p in inputs:
            if source.get("processing_by_variable", {}).get(p, {}).get(text, {}).get("status", "complete") != "complete":
                inputs[p] = None
        derived, metadata = derive_day(inputs, point["lat"], date, elevation=elevation)
        for name in selected:
            spec = VARIABLES[name]
            value = inputs.get(spec["raw"]) if "raw" in spec else derived.get(name)
            if number(value) is not None:
                computed[name][date] = value
            used = list(spec["dependencies"])
            if name in ("ea", "VPD_FAO56", "Rn_FAO56"):
                ea_inputs = ["T2MDEW"] if metadata["ea_method"] == "FAO56_eq14_dewpoint" else ["T2M_MAX", "T2M_MIN", "RH2M_MAX", "RH2M_MIN"]
                used = ea_inputs + ([] if name == "ea" else ["T2M_MAX", "T2M_MIN"]) + (["ALLSKY_SFC_SW_DWN"] if name == "Rn_FAO56" else [])
            detail = dict(status="valid" if number(value) is not None else "missing_dependencies", formula_version=VERSION,
                          input_sources=dict((p, source.get("provenance", {}).get(p, {}).get(text, source.get("source_summary", ""))) for p in sorted(set(used))))
            if name in ("ea", "VPD_FAO56", "Rn_FAO56"):
                detail["ea_method"] = metadata["ea_method"]
            if name == "Rn_FAO56":
                detail.update(elevation_m=elevation, elevation_source="Original input metre attribute" if elevation is not None else None)
            if name == "U2":
                detail["wind_measurement_height_m"] = metadata.get("wind_measurement_height_m")
            intervals = audit[name]
            previous = dict((k, v) for k, v in intervals[-1].items() if k not in ("start", "end")) if intervals else None
            if previous == detail:
                intervals[-1]["end"] = text
            else:
                intervals.append(dict(detail, start=text, end=text))
    fields = {}
    for name in selected:
        fields.update(summarize(computed[name], start, end, VARIABLES[name]["prefix"], scopes, ranges))
    return dict(fields=fields, daily=computed, provenance=audit, source=source)


def sheets(results, module, selected, start, end, save_daily=False, wanted=None):
    """Disk-spooled audit and optional daily sheets; no CSV approximation."""
    from .xlsx_stream import RowSpool
    names = [name for name in selected if VARIABLES[name]["module"] == module]
    if not names:
        return []
    dictionary, methods, hourly, daily = [], [], RowSpool(), RowSpool()
    for field in sorted(set(field for rec in results for field in rec.get("supplementary", {}).get("fields", {}))):
        name = variable_for_field(field)
        if name in names and (wanted is None or field in wanted):
            dictionary.append(field_definition(name, field))
    for rec in results:
        package = rec.get("supplementary", {})
        source = package.get("source", {})
        for name in names:
            values = package.get("daily", {}).get(name, {})
            valid = sum(start <= date <= end for date in values)
            methods.append([rec.get("oid"), name, str(start), str(end), valid, (end-start).days+1,
                            source.get("source_summary", ""), rec.get("calculation_elevation") if name == "Rn_FAO56" else None,
                            VERSION, "Supplementary inputs have a separate source audit; no monthly estimates used. Canonical units in Field_Dictionary.",
                            "مدخلات الإضافات موثقة منفصلة؛ لا تستخدم التقديرات الشهرية. الوحدات موضحة في قاموس الحقول."])
            if save_daily:
                for date, value in sorted(values.items()):
                    if start <= date <= end:
                        daily.append([rec.get("oid"), rec.get("station_id", ""), rec.get("station_name", ""), str(date), name, VARIABLES[name]["unit"], value])
            for p in VARIABLES[name]["dependencies"]:
                actual = source.get("processing_by_variable", {}).get(p, {})
                details = dict((date, dict(info, audit_source=source.get("provenance", {}).get(p, {}).get(date, source.get("source_summary", "")),
                                           audit_used=info.get("status") == "complete")) for date, info in actual.items())
                # A rejected source day has no merged value, but still needs
                # its 23/24 (etc.) evidence in the exported hourly audit.
                rejected = []
                for attempt in source.get("processing_attempts", []):
                    for date, info in attempt.get("variables", {}).get(p, {}).items():
                        if date not in actual:
                            rejected.append((date, dict(info, audit_source=attempt.get("source", ""), audit_used=False)))
                for date, info in sorted(list(details.items()) + rejected, key=lambda item: (item[0], item[1].get("audit_source", ""))):
                    if not str(start) <= date <= str(end):
                        continue
                    hourly.append([rec.get("oid"), name, p, date, info.get("audit_source"),
                        info.get("input_temporal"), info.get("output_temporal"), info.get("operation"), info.get("timezone"),
                        info.get("valid_samples"), info.get("expected_samples"), info.get("unit"), info.get("scale"), info.get("status"), info.get("audit_used"),
                        "Daily input derived from hourly samples; incomplete input rejected. " + info.get("note", ""),
                        "اشتق هذا المسار المدخل اليومي من الساعات المتاحة؛ تستبعد الأيام غير المكتملة وتبقى العملية والتغطية معلنتين."])
    output = [("Field_Dictionary", DICTIONARY_HEADER, dictionary, False),
              ("Methodology", METHOD_HEADER, methods, False), ("Hourly_Processing", HOURLY_HEADER, hourly, False)]
    if save_daily:
        output.append(("Supplementary_Daily", DAILY_HEADER, daily, False))
    else:
        daily.close()
    return output


def short_field(field):
    """Deterministic unique <=10-char SHP names, independent of selected subset."""
    name = variable_for_field(field)
    if name is None:
        return None
    prefix = "X%02d" % ORDER.index(name)
    suffix = field[len(VARIABLES[name]["prefix"]) + 1:]
    periods = ("Annual", "Winter", "Spring", "Summer", "Autumn") + MONTHS
    if suffix in ("Valid_Days", "Expected_Days"):
        return prefix + ("Valid" if suffix == "Valid_Days" else "Expect")
    period, operation = suffix.rsplit("_", 1)
    return prefix + "%02d" % periods.index(period) + ("Mn" if operation == "Mean" else "Rng")
