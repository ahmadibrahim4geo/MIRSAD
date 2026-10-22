"""Optional variable outputs inside existing modules; no changes to legacy fields."""
import calendar
import datetime as dt
from collections import defaultdict

from .daily_climate import VARIABLES, VERSION, number, derive_day, selected_dependencies

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
SEASONS = dict(Winter=(12, 1, 2), Spring=(3, 4, 5), Summer=(6, 7, 8), Autumn=(9, 10, 11))
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
    "ET0_PM": ("FAO56 Penman-Monteith reference evapotranspiration", "البخر والنتح المرجعي بطريقة بنمان مونتيث", "FAO56 eq6; daily G=0; T=(Tmax+Tmin)/2"),
}


def field_unit(module,field,properties):
    """Map/GeoTIFF units follow the selected field, not its parent module."""
    from .daily_climate import PM_PRODUCT
    if module==PM_PRODUCT and field.startswith("ET_PM_"):
        if field.endswith("_Days"):return "days"
        unit="inches" if str(properties.get("Measurement_Unit","")).startswith("inches") else "mm"
        return unit+("/year" if "Annual_Mean" in field else "/season" if any(s+"_Mean" in field for s in SEASONS) else "/month")
    for spec in VARIABLES.values():
        if module==spec["module"] and field.startswith(spec["prefix"]+"_"):
            return "days" if field.endswith(("_Valid_Days","_Expected_Days")) else spec["unit"]
    return properties.get("Measurement_Unit","")


def field_definition(module, field, variable, unit, statistic, missing, method, sources=""):
    """One definition for each exported field, including its actual period."""
    prefix = "ET_PM" if variable == "ET0_PM" else VARIABLES[variable]["prefix"]
    suffix = field[len(prefix)+1:]
    period = suffix.rsplit("_", 1)[0] if suffix.endswith(("_Mean", "_Range")) else "Selected interval"
    english, arabic, formula = DESCRIPTIONS[variable]
    dependencies = "Tmax, Tmin, Rs, ea, wind with known height, pressure or known elevation; latitude/date" if variable == "ET0_PM" else ", ".join(VARIABLES[variable]["dependencies"])
    if variable in ("Ra", "Rn_FAO56"): dependencies += "; latitude/date" + ("; known elevation" if variable == "Rn_FAO56" else "")
    origin = "Source hourly aggregation" if variable in ("RHmax", "RHmin", "VPD_Source") else "Derived daily calculation"
    return [module, field, field, variable, unit, statistic, missing, method, period,
            english, arabic, dependencies, origin, sources, formula,
            "https://open-meteo.com/en/docs/historical-weather-api" if variable in ("RHmax", "RHmin", "VPD_Source", "Sunshine_Hours") else "https://www.fao.org/4/X0490E/x0490e00.htm"]


def hourly_audit(results, variables, start, end):
    """Export actual hourly processing counts, including incomplete days."""
    from .tabular import RowBuffer
    from .daily_climate import PM_PRODUCT, PM_DEPENDENCIES
    rows=RowBuffer()
    for result in results:
        for name in variables:
            module=PM_PRODUCT if name=="ET0_PM" else VARIABLES[name]["module"]
            dependencies=PM_DEPENDENCIES if name=="ET0_PM" else VARIABLES[name]["dependencies"]
            for parameter in dependencies:
                for date,info in sorted(result.get("processing_by_variable",{}).get(parameter,{}).items()):
                    if not str(start)<=date<=str(end):continue
                    rows.append([module,result["station"]["station_key"],name,parameter,date,
                        result.get("provenance",{}).get(parameter,{}).get(date,result.get("source_summary","")),
                        info.get("input_temporal"),info.get("output_temporal"),info.get("operation"),info.get("timezone"),
                        info.get("valid_samples"),info.get("expected_samples"),info.get("unit"),info.get("scale"),info.get("status"),
                        "Daily input from hourly samples; incomplete input rejected for optional formulas; legacy raw values retained. "+info.get("note",""),
                        "قيمة المدخل اليومية مشتقة من الساعات؛ تُستبعد المدخلات غير المكتملة من الحساب الإضافي مع حفظ القيم الخام القديمة"])
    return rows


def calculation_elevation(station):
    original=number(station.get("elevation"))
    if "supplement" in station.get("point_type", "").lower():original=None
    if original is not None:return original,"Original station/input attribute"
    dem=number(station.get("dem_elevation"))
    return (dem,station.get("dem_source")) if dem is not None else (None,None)


def calculation_inputs(result,date):
    """Reject temporally invalid inputs for new formulas, preserving raw/old fields."""
    inputs={p:values.get(date) for p,values in result["series"].items()}
    for p in inputs:
        quality=result.get("processing_by_variable",{}).get(p,{}).get(str(date),{})
        if quality.get("status","complete")!="complete":inputs[p]=None
    return inputs


def summarize(values, start, end, prefix, scopes=None, ranges=False,accumulation=False):
    """Full daily coverage per period; mean of daily values, never invented days.

    DJF uses the three months in the same calendar year, matching the existing
    atlas convention. Annual/seasonal means weight days within each year, then
    average complete year/season results across years. These are new fields.
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
    for period, months in [("Annual", tuple(range(1, 13))), *SEASONS.items()]:
        if scopes is not None and period not in scopes and not (period in SEASONS and "Seasonal" in scopes):
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
    valid = sum(number(values.get(start + dt.timedelta(days=i))) is not None for i in range((end - start).days + 1))
    fields[prefix + "_Valid_Days"] = valid
    fields[prefix + "_Expected_Days"] = (end - start).days + 1
    return fields


def apply(layers, daily, results, modules, selected, start, end, scopes=None, ranges=False,progress=None,cancelled=None):
    """Attach selected new fields and audit metadata; preserve source observations."""
    selected_dependencies(selected, modules)
    methods, dictionary = [], []
    needs_calculation=any("raw" not in VARIABLES[name] for name in selected)
    cancelled=cancelled or (lambda:False)
    for index, result in enumerate(results):
        if cancelled():raise InterruptedError("Cancelled")
        if progress:progress(dict(stage="calculation",completed=index,total=len(results),message="Supplementary variables %d/%d"%(index+1,len(results))))
        station = result["station"]
        z,z_source=calculation_elevation(station)
        raw = result["series"]
        computed = {name: {} for name in selected}
        audit={name:[] for name in selected}
        calculation_methods = defaultdict(set)
        for offset in range((end - start).days + 1):
            if offset%128==0 and cancelled():raise InterruptedError("Cancelled")
            date = start + dt.timedelta(days=offset)
            inputs = calculation_inputs(result,date)
            values, metadata = derive_day(inputs, station["latitude"], date, elevation=z) if needs_calculation else ({},{})
            for name in selected:
                spec = VARIABLES[name]
                value = inputs.get(spec["raw"]) if "raw" in spec else values.get(name)
                if number(value) is not None:
                    computed[name][date] = value
                used=list(spec["dependencies"])
                ea_inputs=["T2MDEW"] if metadata.get("ea_method")=="FAO56_eq14_dewpoint" else ["T2M_MAX","T2M_MIN","RH2M_MAX","RH2M_MIN"]
                if name=="ea":used=ea_inputs
                elif name=="VPD_FAO56":used=sorted(set(["T2M_MAX","T2M_MIN"]+ea_inputs))
                elif name=="Rn_FAO56":used=sorted(set(["T2M_MAX","T2M_MIN","ALLSKY_SFC_SW_DWN"]+ea_inputs))
                detail=dict(status="valid" if number(value) is not None else "missing_dependencies",
                    formula_version=VERSION, input_sources={p:result.get("provenance",{}).get(p,{}).get(str(date),result.get("source_summary","")) for p in used})
                if name in ("ea","VPD_FAO56","Rn_FAO56"):detail["ea_method"]=metadata["ea_method"]
                if name=="Rn_FAO56":
                    detail.update(input_elevation_m=z,input_elevation_source=z_source)
                if name=="U2":detail["wind_measurement_height_m"]=metadata.get("wind_measurement_height_m")
                if "raw" in spec:
                    detail["source_processing"]=result.get("processing_by_variable",{}).get(spec["raw"],{}).get(str(date),{})
                intervals=audit[name]
                if intervals and {k:v for k,v in intervals[-1].items() if k not in ("start","end")}==detail:
                    intervals[-1]["end"]=str(date)
                else:intervals.append(dict(detail,start=str(date),end=str(date)))
                if name in ("ea", "VPD_FAO56", "Rn_FAO56"):
                    calculation_methods[name].add(metadata["ea_method"])
        for name in selected:
            spec = VARIABLES[name]
            module, prefix = spec["module"], spec["prefix"]
            fields = summarize(computed[name], start, end, prefix, scopes, ranges)
            layers[module][index]["properties"].update(fields)
            for date, value in sorted(computed[name].items()):
                daily[module][1].append([station["station_key"], station["usaf"], station["name"],
                                       str(date), name, spec["unit"], value])
            source_variables = {p: result.get("provenance", {}).get(p, {}) for p in spec["dependencies"]}
            sources = sorted({src for values in source_variables.values() for src in values.values()})
            operations = sorted({details.get("operation", "") for p in spec["dependencies"]
                                 for details in result.get("processing_by_variable", {}).get(p, {}).values()})
            valid = fields[prefix + "_Valid_Days"]
            methods.append([station["station_key"], name, str(start), str(end),
                            "; ".join(sources) or ("Astronomical calculation" if name == "Ra" else result.get("source_summary", "")),
                            "; ".join(operations) or "daily derived calculation", "UTC", valid,
                            (end - start).days + 1, "; ".join(sorted(calculation_methods[name])),
                            z if name == "Rn_FAO56" else None, VERSION,
                            "Inspect Raw_Data source summaries for per-day sources and hourly sample counts; incomplete days stay NULL."])
            if index == 0:
                for field in fields:
                    unit = "days" if field.endswith(("_Valid_Days", "_Expected_Days")) else spec["unit"]
                    dictionary.append(field_definition(module, field, name, unit,
                                       "Count" if unit == "days" else "Range of monthly climatic means" if field.endswith("Annual_Range") else
                                       "Interannual range of same-month means" if field.endswith("Range") else "Mean of complete daily values",
                                       "NULL for incomplete dependencies/period; missing is never zero",
                                       "FAO56 daily / source hourly aggregation; supplementary fields use canonical units", "; ".join(sources)))
        result["supplementary_provenance"]=audit
    return dict(methods=methods, dictionary=dictionary,hourly_processing=hourly_audit(results,selected,start,end))


def build_pm(results,start,end,provider,scopes=None,ranges=False,progress=None,cancelled=None,units="Metric",unit_options=None):
    """One independent daily FAO56 product. HG fields and dependent indices are untouched."""
    from .exports import station_properties
    from .daily_climate import PM_PRODUCT,PM_DEPENDENCIES
    cancelled=cancelled or (lambda:False)
    from .tabular import RowBuffer
    precip_unit=(unit_options or {}).get("unit_precip") or ("Inches" if units=="Imperial" else "mm")
    if precip_unit not in ("mm","Millimeters","Millimetres","Millimeters (mm)","Inches","Inches (in)"):raise ValueError("Unsupported PM precipitation unit: "+str(precip_unit))
    factor,output_unit=(1/25.4,"inches") if precip_unit.startswith("Inches") else (1.,"mm")
    records,daily,methods,dictionary=[],RowBuffer(),[],[]
    for index,result in enumerate(results):
        if cancelled():raise InterruptedError("Cancelled")
        station=result["station"];z,z_source=calculation_elevation(station)
        values={};audit=[]
        for offset in range((end-start).days+1):
            if offset%128==0 and cancelled():raise InterruptedError("Cancelled")
            date=start+dt.timedelta(days=offset)
            inputs=calculation_inputs(result,date)
            components,meta=derive_day(inputs,station["latitude"],date,elevation=z)
            et=components["ET0_PM"]
            if number(et) is not None:
                values[date]=et*factor
                daily.append([station["station_key"],station["usaf"],station["name"],str(date),"ET0_PM",output_unit+"/day",et*factor])
            used=[p for p in PM_DEPENDENCIES if p not in ("T2MDEW","RH2M_MAX","RH2M_MIN")]
            used+=(['T2MDEW'] if meta["ea_method"]=="FAO56_eq14_dewpoint" else ["RH2M_MAX","RH2M_MIN"])
            if meta["pressure_method"]=="FAO56_eq7_known_elevation":used.remove("PS")
            detail=dict(formula_version=VERSION,status="valid" if et is not None else "missing_dependencies",
                        ea_method=meta["ea_method"],input_elevation_m=z,input_elevation_source=z_source,
                        pressure_method=meta["pressure_method"],wind_measurement_height_m=meta["wind_measurement_height_m"],
                        input_sources={p:result.get("provenance",{}).get(p,{}).get(str(date),result.get("source_summary",provider)) for p in used},
                        missing_components=[k for k in meta["missing_outputs"] if k in ("es","ea","Ra","U2","Rn_FAO56","ET0_PM")]+
                                           (["pressure"] if meta["pressure_kPa"] is None else []),G_MJ_m2_day=0.)
            if meta.get("quality_note"):detail["quality_note"]=meta["quality_note"]
            if audit and {k:v for k,v in audit[-1].items() if k not in ("start","end")}==detail:audit[-1]["end"]=str(date)
            else:audit.append(dict(detail,start=str(date),end=str(date)))
        fields=summarize(values,start,end,"ET_PM",scopes,ranges,accumulation=True)
        valid=fields["ET_PM_Valid_Days"];expected=fields["ET_PM_Expected_Days"]
        props=station_properties(station)
        props.update(Data_Start=str(start),Data_End=str(end),Source=result.get("source_summary",provider),
                     Measurement_Unit=output_unit+"; complete period accumulations (Daily: "+output_unit+"/day)",
                     Status="OK" if valid==expected else "PARTIAL" if valid else "NO_DATA",
                     Error_Msg="" if valid==expected else "%d/%d PM daily values; known elevation and complete dependencies required"%(valid,expected),
                     Valid_Days=valid,Expected_Days=expected,Coverage_Fraction=valid/expected)
        props.update(fields);records.append(dict(latitude=station["latitude"],longitude=station["longitude"],properties=props))
        result.setdefault("supplementary_provenance",{})["ET0_PM"]=audit
        methods.append([station["station_key"],"ET0_PM",str(start),str(end),result.get("source_summary",provider),
                        "Daily FAO56 calculation then sum", "UTC",valid,expected,
                        "; ".join(sorted({a["ea_method"] for a in audit})),z,VERSION,
                        "Reference grass; T=(Tmax+Tmin)/2; G=0; no source ET0 substitution. Per-day input sources in manifest supplementary_provenance."])
        if index==0:
            for field in fields:
                period_unit=output_unit+("/year" if "Annual_Mean" in field else "/season" if any(s+"_Mean" in field for s in SEASONS) else "/month")
                dictionary.append(field_definition(PM_PRODUCT,field,"ET0_PM","days" if field.endswith("Days") else period_unit,
                    "Count" if field.endswith("Days") else "Range of climatic monthly accumulations" if field.endswith("Annual_Range") else "Interannual range of same-month accumulations" if field.endswith("Range") else "Mean of complete period sums",
                    "NULL unless all days/dependencies of each period are present; no monthly estimates fed into PM",VERSION,result.get("source_summary",provider)))
    return records,(["Station_Key","Station_ID","Station_Name","Date","Variable","Unit","Value"],daily),dict(methods=methods,dictionary=dictionary,hourly_processing=hourly_audit(results,["ET0_PM"],start,end))
