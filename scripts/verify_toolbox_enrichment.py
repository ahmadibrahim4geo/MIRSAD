# -*- coding: utf-8 -*-
"""Native Point/Station execution with synthetic, offline source responses.

This tests actual ArcPy processing/exports, not provider network availability.
All fixtures and outputs stay in a fresh tests/.output directory.
"""
from __future__ import print_function, unicode_literals
import argparse
import datetime as dt
import io
import json
import os
import sys
import subprocess
import traceback
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--kind", choices=("points", "stations"), default="points")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--native-worker", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def load(name, filename):
    if sys.version_info[0] < 3:
        import imp
        return imp.load_source(name, filename)
    from importlib.machinery import SourceFileLoader
    return SourceFileLoader(name, filename).load_module()


def report(folder, value):
    payload = json.dumps(value, ensure_ascii=False, indent=2)
    if isinstance(payload, bytes):payload = payload.decode("utf-8")
    with io.open(os.path.join(folder, "acceptance.json"), "w", encoding="utf-8") as handle:handle.write(payload)


def main():
    args = arguments();folder = os.path.abspath(args.output)
    if not folder.startswith(os.path.abspath(os.path.join(ROOT, "tests/.output"))+os.sep):raise ValueError("QA output outside tests/.output")
    if os.path.exists(folder):raise IOError("Preserve earlier evidence; choose a fresh output folder")
    os.makedirs(folder)
    global QA_CREATED
    QA_CREATED = True
    print("STAGE: native ArcPy import", flush=True) if sys.version_info[0] >= 3 else sys.stdout.write("STAGE: native ArcPy import\n")
    sys.stdout.flush()
    import arcpy
    from mirsad_core import hybrid_pipeline as pipeline, toolbox_enrichment as e
    print("STAGE: create native QA input");sys.stdout.flush()
    gdb = os.path.join(folder, "Inputs.gdb");arcpy.CreateFileGDB_management(folder, "Inputs.gdb")
    points = os.path.join(gdb, "Input_Points")
    arcpy.CreateFeatureclass_management(gdb, "Input_Points", "POINT", spatial_reference=arcpy.SpatialReference(4326))
    for name, kind in (("Station_ID", "TEXT"), ("WBAN", "TEXT"), ("Name", "TEXT"), ("Country", "TEXT"), ("Elev_m", "DOUBLE")):
        arcpy.AddField_management(points, name, kind)
    input_fields = ["SHAPE@XY", "Station_ID", "WBAN", "Name", "Country", "Elev_m"]
    with arcpy.da.InsertCursor(points, input_fields) as cursor:
        for i, z in enumerate((0., 100., None)):
            cursor.insertRow([(31+i*.01, 30+i*.01), "%06d" % (1234+i), "00001", "نقطة %d" % i, "EG", z])
    with arcpy.da.SearchCursor(points, input_fields) as cursor:original = list(cursor)
    constants = dict(T2M=20., T2M_MAX=25., T2M_MIN=15., T2MDEW=10., RH2M=61.5, RH2M_MAX=73., RH2M_MIN=50.,
        WS10M=3., WS10M_CONFIRMED=3., WD10M=0., ALLSKY_SFC_SW_DWN=22.07, SUNSHINE_DURATION=33300., VPD_SOURCE=1.2)
    requests = []
    def fetch(provider, station, start, end, required, model, session, cancelled):
        requests.append(dict(source=provider, station=station["station_key"], required=required))
        series = dict((p, dict((day, constants[p]) for day in pipeline.days(start, end))) for p in required if p in constants)
        processing = {}
        for p, op in (("RH2M_MAX", "max"), ("RH2M_MIN", "min"), ("VPD_SOURCE", "max"), ("WS10M_CONFIRMED", "mean")):
            if p in required:
                processing[p] = dict((day, dict(input_temporal="hourly", output_temporal="daily", operation=op,
                    timezone="UTC", valid_samples=24, expected_samples=24, status="complete", scale=1., unit="canonical")) for day in pipeline.days(start, end))
        return dict(series=series, processing_by_variable=processing, raw=dict(synthetic_fixture=True), warnings=[], urls=[], state="COMPLETE")
    pipeline.fetch_source = fetch
    # Fail immediately if any unmocked network path is reached.
    def no_network(*args, **kwargs):raise AssertionError("Unexpected network request in native fixture acceptance")
    core = load("native_enrichment_core", os.path.join(ROOT, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt"))
    if args.kind == "stations":
        station_module = load("native_enrichment_stations", os.path.join(ROOT, "Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt"))
        tool = station_module.WeatherStationsAtlasGenerator();core = station_module._core
    else:tool = core.PowerClimateAtlasGenerator()
    core.fetch_nasa_point = core.fetch_openmeteo_point = core.probe_server = no_network
    params = tool.getParameterInfo();pd = dict((p.name, p) for p in params)
    output = os.path.join(folder, "Atlas")
    values = dict(Output_Workspace=output, Climate_Data_Source="Open-Meteo ERA5 (Standalone - No NASA Supplement)",
        Climate_Modules="Temperature;Relative Humidity;Wind;Solar Radiation", Time_Mode="Custom Date Range",
        Start_Date=dt.datetime(2024, 2, 1), End_Date=dt.datetime(2024, 2, 29), Temporal_Resolution="Daily",
        Download_Only=True, Study_Area_Name="Native_Enrichment_QA", Save_Daily_Series=True,
        Gap_Fill_Method="No Fill (Keep Missing)", Add_To_Map=False, Export_Shapefiles=False,
        Export_Arabic_Database=False, Supplementary_Rasters=False)
    if args.kind == "stations":
        values.update(Station_Selection_Mode="Local Saved Station Layer (Shapefile / Geodatabase)", Local_Station_Features=points)
    else:values["Input_Point_Features"] = points
    for name in e.ORDER:values[e.parameter_name(name)] = True
    for name, value in values.items():
        if name in pd:pd[name].value = value
    lines, warnings = [], []
    class Messages(object):
        def addMessage(self, text):
            lines.append(text)
            with io.open(os.path.join(folder, "processing.log"), "a", encoding="utf-8") as handle:handle.write(core._excel_text(text)+"\n")
            if "Element layer '" in text or "BATCH DATA COMMITTED" in text:
                print(core._excel_text(text));sys.stdout.flush()
        def addWarningMessage(self, text):warnings.append(text)
        addWarning = addWarningMessage
        def addErrorMessage(self, text):raise RuntimeError(text)
    print("STAGE: execute real %s Toolbox with offline fixtures" % args.kind);sys.stdout.flush()
    tool.execute(params, Messages())
    with io.open(os.path.join(folder, "processing.log"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(core._excel_text(line) for line in lines+warnings))
    with arcpy.da.SearchCursor(points, input_fields) as cursor:
        if list(cursor) != original:raise AssertionError("Source attributes/geometry changed")
    generated = [os.path.join(output, name) for name in os.listdir(output) if name.startswith("Climate_Database_") and name.endswith(".gdb")]
    if len(generated) != 1:raise AssertionError("Missing or ambiguous native output GDB")
    field_count = 0
    for module in ("Temperature", "Relative Humidity", "Wind", "Solar Radiation"):
        fc = os.path.join(generated[0], core.MODULE_SHORT[module])
        if not arcpy.Exists(fc):raise AssertionError("Missing output layer: "+module)
        fields = e.fields_by_module(e.ORDER, dt.date(2024, 2, 1), dt.date(2024, 2, 29))[module]
        actual = dict((f.name, f) for f in arcpy.ListFields(fc))
        for field in fields:
            if field not in actual or actual[field].aliasName != field:raise AssertionError("Missing/changed default alias: "+field)
        field_count += len(fields)
        check_fields = ["Station_ID", "Source_ID"]+[name for name in fields if "February_Mean" in name or "Valid_Days" in name]
        with arcpy.da.SearchCursor(fc, check_fields) as cursor:
            for values in cursor:
                row = dict(zip(check_fields, values))
                if module == "Temperature" and abs(row["Trange_February_Mean"]-10.) > 1e-8:raise AssertionError("Temperature range mismatch")
                if module == "Relative Humidity" and row["RHmax_February_Mean"] != 73.:raise AssertionError("RH extrema mismatch")
                if module == "Solar Radiation":
                    if row["Sunshine_February_Mean"] != 9.25:raise AssertionError("Sunshine hours mismatch")
                    # Station's owned SHP has 0-based FIDs; GDB OIDs are 1-based.
                    # Verify the stable text identifier instead of assuming OIDs.
                    if row["Rn_FAO56_Valid_Days"] != (0 if row["Station_ID"] == "001236" else 29):raise AssertionError("Unknown elevation manufactured Rn")
        workbook = os.path.join(output, "00_Tables_And_Reports", core.MODULE_SHORT[module]+".xlsx")
        if not os.path.isfile(workbook):raise AssertionError("Missing supplementary XLSX")
        # Native Excel conversion proves the application can re-read its own new workbook.
        table = os.path.join(gdb, "Readback_"+core.MODULE_SHORT[module])
        arcpy.ExcelToTable_conversion(workbook, table, "Supplementary_Daily")
        if int(arcpy.GetCount_management(table).getOutput(0)) == 0:raise AssertionError("Empty native supplementary daily readback")
    with io.open(os.path.join(output, "Source Data", "Supplementary_Provenance.json"), encoding="utf-8") as handle:audit = json.load(handle)
    if len(audit["points"]) != 3:raise AssertionError("Point provenance lost")
    if not all("|00001|" in point["station_key"] for point in audit["points"]):raise AssertionError("WBAN leading zeros lost")
    if audit["points"][0]["elevation_m"] != 0. or audit["points"][2]["elevation_m"] is not None:raise AssertionError("Elevation missingness changed")
    report(folder, dict(passed=True, kind=args.kind, runtime=arcpy.GetInstallInfo(), source_network="Synthetic offline responses; no live provider acceptance",
        added_fields=field_count, points=3, parameters=len(params), requests=len(requests), warnings=warnings,
        checks=["Actual Toolbox execute with native ArcPy", "11 additions in parent layers", "English default aliases", "Native XLSX daily readback",
                "Known zero / unknown elevation distinguished", "Input geometry/attributes unchanged", "Per-day input provenance retained"],
        limits=["Supplementary rasters were disabled", "No authenticated providers", "Fixture period is February 2024"]))
    print(json.dumps(dict(passed=True, kind=args.kind, fields=field_count, output=folder)))


def bounded():
    args = arguments();folder = os.path.abspath(args.output)
    if not folder.startswith(os.path.abspath(os.path.join(ROOT, "tests/.output"))+os.sep):raise ValueError("QA output outside tests/.output")
    if os.path.exists(folder):raise IOError("Preserve earlier evidence; choose a fresh output folder")
    process = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--native-worker"]+sys.argv[1:])
    try:return process.wait(timeout=args.timeout)
    except TypeError:
        import time
        deadline = time.time()+args.timeout
        while process.poll() is None and time.time() < deadline:time.sleep(.2)
        if process.poll() is not None:return process.returncode
    except subprocess.TimeoutExpired:pass
    process.terminate();process.wait()
    if not os.path.isdir(folder):os.makedirs(folder)
    report(folder, dict(passed=False, timeout_seconds=args.timeout, kind=args.kind, reason="Native process did not complete within bounded acceptance"))
    return 1


if __name__ == "__main__":
    if arguments().native_worker:
        try:main()
        except Exception:
            folder = os.path.abspath(arguments().output)
            if globals().get("QA_CREATED"):report(folder, dict(passed=False, error=traceback.format_exc()))
            raise
    else:raise SystemExit(bounded())
