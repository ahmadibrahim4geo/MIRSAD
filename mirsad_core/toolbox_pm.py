# -*- coding: utf-8 -*-
"""Independent daily FAO56 PM product for the existing ET Toolbox module.

Python 2.7/3; no ArcPy imports. HG and indices depending on it stay unchanged.
"""
from __future__ import unicode_literals
import datetime as dt
from . import toolbox_enrichment as extra
from .daily_climate import PM_PRODUCT, PM_DEPENDENCIES, VERSION, derive_day, number

PREFIX = "ET_PM"
METHODS_PARAMETER = "Evapotranspiration_Methods"
RASTERS_PARAMETER = "Evapotranspiration_Raster_Methods"


def parameters(arcpy, arabic=False):
    output = []
    for name, label, description in (
        (METHODS_PARAMETER, "طرق حساب البخر والنتح" if arabic else "Evapotranspiration calculation methods",
         "HG is the preserved default. PM is an independent daily FAO56 product; known metre elevation and complete inputs required. PM never replaces HG in UNEP/water-deficit indices."),
        (RASTERS_PARAMETER, "طرق البخر والنتح المطلوب استيفاؤها" if arabic else "Evapotranspiration raster methods",
         "Independent raster selection. Only calculated methods may be interpolated; PM raster is off by default.")):
        p = arcpy.Parameter(displayName=label, name=name, datatype="GPString", parameterType="Optional", direction="Input")
        p.multiValue = True
        p.filter.type = "ValueList"
        p.filter.list = ["HG", "PM"]
        p.value = "HG"
        p.category = "طرق البخر والنتح" if arabic else "Evapotranspiration methods"
        p.description = (("HG هو الافتراضي المحفوظ. PM ناتج FAO56 يومي مستقل يحتاج منسوبًا معلومًا بالمتر ومدخلات مكتملة؛ لا يحل محل HG في مؤشرات UNEP والعجز المائي."
                          if name == METHODS_PARAMETER else "اختيار الراستر مستقل عن الحساب؛ تختار طريقة محسوبة فقط، وراستر PM مغلق افتراضيًا.") if arabic else description)
        output.append(p)
    return output


def values(parameter, default):
    if parameter is None:return list(default)
    raw = parameter.valueAsText or ""
    return [part.strip().strip("'\"") for part in raw.split(";") if part.strip().strip("'\"")]


def selected(pdict, modules, temporal, offline, provider):
    methods = values(pdict.get(METHODS_PARAMETER), ["HG"])
    rasters = values(pdict.get(RASTERS_PARAMETER), ["HG"])
    if not methods or len(set(methods)) != len(methods) or any(name not in ("HG", "PM") for name in methods):
        raise ValueError("Select HG, PM or both evapotranspiration calculation methods")
    if "Evapotranspiration" not in modules:
        if "PM" in methods:raise ValueError("Select Evapotranspiration before choosing PM")
        return [], []
    if "PM" in methods:
        from .climate_products import descriptor
        from .climate_sources import pipeline_sources
        if offline or ("Daily" not in (temporal or "") and "يومي" not in (temporal or "")):
            raise ValueError("PM requires the online Daily workflow; native monthly products cannot supply daily PM")
        if descriptor(provider) or pipeline_sources(provider) == ("NOAA GSOD",):
            raise ValueError("Daily PM is not integrated with this selected source; choose a supported public reanalysis/POWER policy")
    if len(set(rasters)) != len(rasters) or any(name not in methods for name in rasters):
        raise ValueError("Raster methods must be a subset of the calculated HG/PM methods")
    return methods, rasters


def output_units(precipitation_unit):
    value = (precipitation_unit or "Millimeters (mm)").lower()
    if value.startswith("inch"):return 1./25.4, "inches"
    if value.startswith(("mm", "millimet")):return 1., "mm"
    raise ValueError("Unsupported PM output precipitation unit: " + str(precipitation_unit))


def fields(start, end, scopes=None, ranges=False):
    return sorted(extra.summarize({}, start, end, PREFIX, scopes, ranges, accumulation=True))


def is_field(field):
    return bool(field and field.startswith(PREFIX + "_"))


def definition(field, precipitation_unit="Millimeters (mm)"):
    factor, unit = output_units(precipitation_unit)
    suffix = field[len(PREFIX)+1:]
    count = suffix in ("Valid_Days", "Expected_Days")
    period = "Selected interval" if count else suffix.rsplit("_", 1)[0]
    unit = "days" if count else unit + ("/year" if suffix == "Annual_Mean" else "/season" if period in dict(extra.SEASONS) else "/month")
    statistic = ("Count" if count else "Range of climatic monthly accumulations" if suffix == "Annual_Range" else
                 "Interannual range of same-month accumulations" if suffix.endswith("Range") else "Mean of complete period sums")
    return [PM_PRODUCT, field, field, "ET0_PM", period, unit, statistic,
            "FAO56 Penman-Monteith reference evapotranspiration", "البخر والنتح المرجعي بطريقة بنمان مونتيث",
            ", ".join(PM_DEPENDENCIES) + "; latitude/date; known elevation in metres",
            "FAO56 eq6; T=(Tmax+Tmin)/2; G=0; albedo=0.23; sum daily PM then average complete periods",
            "NULL for incomplete dependencies/period; negative ET retained with quality note; no monthly gap estimates",
            "https://www.fao.org/4/x0490e/x0490e00.htm"]


def short_field(field):
    if not is_field(field):return None
    suffix = field[len(PREFIX)+1:]
    if suffix in ("Valid_Days", "Expected_Days"):return "PMValid" if suffix == "Valid_Days" else "PMExpect"
    period, operation = suffix.rsplit("_", 1)
    periods = ("Annual", "Winter", "Spring", "Summer", "Autumn") + extra.MONTHS
    return "PM%02d%s" % (periods.index(period), "Mn" if operation == "Mean" else "Rng")


def calculate(point, source, start, end, scopes=None, ranges=False, precipitation_unit="Millimeters (mm)", cancelled=None):
    factor, unit = output_units(precipitation_unit)
    cancelled = cancelled or (lambda: False)
    values, intervals = {}, []
    z = number(point.get("calculation_elevation"))
    for offset in range((end-start).days+1):
        if offset % 128 == 0 and cancelled():
            from .hybrid_pipeline import Cancelled
            raise Cancelled("Cancelled")
        date = start + dt.timedelta(days=offset);text = str(date)
        inputs = dict((p, cells.get(text)) for p, cells in source.get("series", {}).items())
        for p in inputs:
            if source.get("processing_by_variable", {}).get(p, {}).get(text, {}).get("status", "complete") != "complete":inputs[p] = None
        components, metadata = derive_day(inputs, point["lat"], date, elevation=z)
        et = number(components["ET0_PM"])
        if et is not None:values[date] = et*factor
        used = [p for p in PM_DEPENDENCIES if p not in ("T2MDEW", "RH2M_MAX", "RH2M_MIN")]
        used += ["T2MDEW"] if metadata["ea_method"] == "FAO56_eq14_dewpoint" else ["RH2M_MAX", "RH2M_MIN"]
        if metadata["pressure_method"] != "source_surface_pressure":used.remove("PS")
        detail = dict(status="valid" if et is not None else "missing_dependencies", formula_version=VERSION,
            ea_method=metadata["ea_method"], pressure_method=metadata["pressure_method"], elevation_m=z,
            elevation_source="Original input metre attribute" if z is not None else None,
            wind_measurement_height_m=metadata.get("wind_measurement_height_m"),
            input_sources=dict((p, source.get("provenance", {}).get(p, {}).get(text, source.get("source_summary", ""))) for p in used),
            missing_components=[name for name in metadata["missing_outputs"] if name in ("es", "ea", "Ra", "U2", "Rn_FAO56", "ET0_PM")] +
                               (["pressure"] if metadata["pressure_kPa"] is None else []),
            daily_output_unit=unit+"/day", G_MJ_m2_day=0.)
        if metadata.get("quality_note"):detail["quality_note"] = metadata["quality_note"]
        previous = dict((key, value) for key, value in intervals[-1].items() if key not in ("start", "end")) if intervals else None
        if previous == detail:intervals[-1]["end"] = text
        else:intervals.append(dict(detail, start=text, end=text))
    summary = extra.summarize(values, start, end, PREFIX, scopes, ranges, accumulation=True)
    count, expected = summary[PREFIX+"_Valid_Days"], summary[PREFIX+"_Expected_Days"]
    return dict(fields=summary, daily=values, provenance=intervals, source=source, unit=unit,
        status="OK" if count == expected else "PARTIAL" if count else "NO_DATA",
        error="" if count == expected else "%d/%d valid daily PM values; known elevation and complete dependencies required" % (count, expected))


def daily_table(results, start, end):
    from .xlsx_stream import RowSpool
    rows = RowSpool()
    for rec in results:
        for date, value in sorted(rec.get("pm", {}).get("daily", {}).items()):
            if start <= date <= end:
                rows.append([rec.get("oid"), rec.get("oid"), rec.get("station_id", ""), rec.get("station_name", ""),
                             rec.get("country", ""), rec.get("lat"), rec.get("lon"), str(date), value])
    return dict(params=["ET0_PM"], header=["OBJECTID", "Source_ID", "Station_ID", "Station_Name", "Country", "Latitude", "Longitude", "Date", "ET0_PM"], rows=rows)


def sheets(results, start, end, wanted, precipitation_unit):
    from .xlsx_stream import RowSpool
    dictionary = [definition(field, precipitation_unit) for field in wanted if is_field(field)]
    # The daily column has its own explicit unit, separate from period sums.
    factor, unit = output_units(precipitation_unit)
    dictionary.append([PM_PRODUCT, "ET0_PM", "ET0_PM", "ET0_PM", "Daily", unit+"/day", "Daily FAO56 calculation",
        "Daily FAO56 PM reference evapotranspiration", "البخر والنتح المرجعي اليومي بطريقة بنمان مونتيث",
        ", ".join(PM_DEPENDENCIES), "FAO56 eq6; daily G=0; no monthly gap estimates", "NULL when any required component is missing",
        "https://www.fao.org/4/x0490e/x0490e00.htm"])
    methodology, hourly = [], RowSpool()
    for rec in results:
        package = rec.get("pm", {});source = package.get("source", {})
        count = sum(start <= date <= end for date in package.get("daily", {}))
        methodology.append([rec.get("oid"), "ET0_PM", str(start), str(end), count, (end-start).days+1,
            source.get("source_summary", ""), rec.get("calculation_elevation"), VERSION,
            "Independent PM; daily G=0; T=(Tmax+Tmin)/2. Surface pressure before elevation estimate. Daily values sum into complete periods. Per-day input sources in PM_Provenance.json.",
            "PM مستقل؛ يحفظ HG والمؤشرات المعتمدة عليه. تتراكم القيم اليومية للفترات المكتملة مع توثيق المدخلات الفعلية لكل يوم."])
        for p in PM_DEPENDENCIES:
            actual = source.get("processing_by_variable", {}).get(p, {})
            details = [(date, dict(info, audit_source=source.get("provenance", {}).get(p, {}).get(date, source.get("source_summary", "")),
                                   audit_used=info.get("status") == "complete")) for date, info in actual.items()]
            for attempt in source.get("processing_attempts", []):
                details.extend((date, dict(info, audit_source=attempt.get("source", ""), audit_used=False))
                    for date, info in attempt.get("variables", {}).get(p, {}).items() if date not in actual)
            for date, info in sorted(details, key=lambda item: (item[0], item[1].get("audit_source", ""))):
                if str(start) <= date <= str(end):
                    hourly.append([rec.get("oid"), "ET0_PM", p, date, info.get("audit_source"), info.get("input_temporal"),
                        info.get("output_temporal"), info.get("operation"), info.get("timezone"), info.get("valid_samples"), info.get("expected_samples"),
                        info.get("unit"), info.get("scale"), info.get("status"), info.get("audit_used"),
                        "Daily input derived from hourly samples; incomplete input rejected; raw legacy values preserved.",
                        "مدخل يومي مشتق من الساعات؛ ترفض المدخلات غير المكتملة مع حفظ القيم الخام القديمة."])
    return [("Field_Dictionary", extra.DICTIONARY_HEADER, dictionary, False),
            ("Methodology", extra.METHOD_HEADER, methodology, False), ("Hourly_Processing", extra.HOURLY_HEADER, hourly, False)]
