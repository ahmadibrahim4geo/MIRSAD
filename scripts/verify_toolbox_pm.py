"""Native Pro HG-only / PM-only / both acceptance with FAO56 offline fixtures."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback
import verify_toolbox_enrichment as native

ROOT = Path(native.ROOT)


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--kind', choices=('points', 'stations'), default='points')
    parser.add_argument('--native-worker', action='store_true', help=argparse.SUPPRESS)
    return parser.parse_args()


def main():
    args = arguments();folder = args.output.resolve()
    if not folder.is_relative_to(ROOT/'tests/.output') or folder.exists():raise ValueError('Choose a fresh tests/.output directory')
    folder.mkdir();print('STAGE: native ArcPy import', flush=True)
    import arcpy
    from mirsad_core import hybrid_pipeline as pipeline, toolbox_pm as pm
    core = native.load('native_pm_core', str(ROOT/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt'))
    station_module = None
    if args.kind == 'stations':
        station_module = native.load('native_pm_stations', str(ROOT/'Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt'))
        core = station_module._core
    gdb = folder/'Input.gdb';arcpy.management.CreateFileGDB(str(folder), gdb.name)
    points = str(gdb/'Fixture')
    arcpy.management.CreateFeatureclass(str(gdb), 'Fixture', 'POINT', spatial_reference=arcpy.SpatialReference(4326))
    for name, kind in [('Station_ID', 'TEXT'), ('WBAN', 'TEXT'), ('Name', 'TEXT'), ('Elev_m', 'DOUBLE')]:arcpy.management.AddField(points, name, kind)
    input_fields = ['Station_ID', 'WBAN', 'Name', 'Elev_m', 'SHAPE@XY']
    with arcpy.da.InsertCursor(points, input_fields) as cursor:
        cursor.insertRow(['001234', '00001', 'مرجع FAO56', 100., (4.35, 50.8)])
        cursor.insertRow(['001235', '00001', 'منسوب مفقود', None, (4.36, 50.81)])
    with arcpy.da.SearchCursor(points, input_fields) as cursor:original = list(cursor)
    constants = dict(T2M=16.9, T2M_MAX=21.5, T2M_MIN=12.3, RH2M_MAX=84., RH2M_MIN=63.,
                     ALLSKY_SFC_SW_DWN=22.07, WS10M_CONFIRMED=10./3.6)
    def fetch(source, station, start, end, required, model, session, cancelled):
        return dict(series={p:{day:constants[p] for day in pipeline.days(start, end)} for p in required if p in constants},
                    raw=dict(synthetic_fixture=True), warnings=[], urls=[], state='COMPLETE')
    pipeline.fetch_source = fetch
    def no_network(*args, **kwargs):raise AssertionError('Unexpected network call in offline native PM acceptance')
    core.probe_server = core.fetch_nasa_point = core.fetch_openmeteo_point = no_network
    reports, hg_reference = {}, None
    for methods in ('HG', 'PM', 'HG;PM'):
        key = methods.replace(';', '_');out = folder/key
        print('STAGE: native ET methods '+methods, flush=True)
        tool = station_module.WeatherStationsAtlasGenerator() if station_module else core.PowerClimateAtlasGenerator()
        params = tool.getParameterInfo();pd = {p.name:p for p in params}
        values = dict(Input_Point_Features=points, Output_Workspace=str(out), Climate_Modules='Evapotranspiration',
            Climate_Data_Source='Open-Meteo ERA5 (Standalone - No NASA Supplement)', Temporal_Resolution='Daily',
            Time_Mode='Custom Date Range', Start_Date=dt.datetime(2001, 7, 1), End_Date=dt.datetime(2001, 7, 31),
            Download_Only=True, Save_Daily_Series=True, Gap_Fill_Method='No Fill (Keep Missing)', Add_To_Map=False,
            Evapotranspiration_Methods=methods, Evapotranspiration_Raster_Methods=None)
        if station_module:values.update(Station_Selection_Mode='Local Saved Station Layer (Shapefile / Geodatabase)', Local_Station_Features=points)
        for name, value in values.items():
            if name in pd:pd[name].value = value
        lines, warnings = [], []
        class Messages:
            def addMessage(self, text):lines.append(text)
            def addWarningMessage(self, text):warnings.append(text)
            addWarning = addWarningMessage
            def addErrorMessage(self, text):raise RuntimeError(text)
        tool.execute(params, Messages())
        (out/'native.log').write_text('\n'.join(lines+warnings), encoding='utf-8')
        if any('QA FAIL:' in text or 'failed:' in text.lower() for text in warnings):raise AssertionError(warnings)
        databases = list(out.glob('Climate_Database_*.gdb'))
        if len(databases) != 1:raise AssertionError('Missing output database')
        database = databases[0]
        hg = str(database/'Evapotranspiration');penman = str(database/pm.PM_PRODUCT)
        if arcpy.Exists(hg) != ('HG' in methods) or arcpy.Exists(penman) != ('PM' in methods):raise AssertionError('ET method output leak')
        if 'HG' in methods:
            hfields = [f for f in core.MODULE_FIELDS['Evapotranspiration'] if f in {item.name for item in arcpy.ListFields(hg)}]
            with arcpy.da.SearchCursor(hg, ['Station_ID']+hfields) as cursor:hvalues = sorted(list(cursor))
            if hg_reference is None:hg_reference = hvalues
            elif hvalues != hg_reference:raise AssertionError('Selecting PM changed HG values')
            workbook = out/('15_Evapotranspiration/Hargreaves/Evapotranspiration.xlsx' if 'PM' in methods else '00_Tables_And_Reports/Evapotranspiration.xls')
            if not workbook.is_file():raise AssertionError('HG workbook path changed')
        if 'PM' in methods:
            names = pm.fields(dt.date(2001, 7, 1), dt.date(2001, 7, 31))
            actual = {f.name:f.aliasName for f in arcpy.ListFields(penman)}
            if not all(actual.get(name) == name for name in names):raise AssertionError('PM aliases/schema mismatch')
            with arcpy.da.SearchCursor(penman, ['Station_ID', 'ET_PM_Valid_Days', 'ET_PM_July_Mean', 'Status']) as cursor:
                rows = {row[0]:row[1:] for row in cursor}
            if rows['001234'][0] != 31 or rows['001235'][0] != 0 or rows['001235'][1] is not None:raise AssertionError('PM missingness/coverage mismatch')
            workbook = out/'15_Evapotranspiration/Penman_Monteith'/(pm.PM_PRODUCT+'.xlsx')
            if not workbook.is_file():raise AssertionError('Missing PM workbook')
            table = str(gdb/('Readback_'+key));arcpy.conversion.ExcelToTable(str(workbook), table, 'Daily')
            with arcpy.da.SearchCursor(table, ['Station_ID', 'Date', 'ET0_PM']) as cursor:daily = list(cursor)
            if len(daily) != 31:raise AssertionError('PM Daily must exclude the unknown-elevation point')
            sample = next(row for row in daily if str(row[1]).startswith('2001-07-06'))
            if abs(sample[2]-3.88) > .03:raise AssertionError('FAO56 example18 daily PM mismatch')
            if abs(sum(row[2] for row in daily)-rows['001234'][1]) > 1e-8:raise AssertionError('PM monthly value is not the sum of daily PM')
        reports[key] = dict(passed=True, methods=methods, warnings=warnings, hg_unchanged=True,
            pm_fao_example18=('PM' in methods), native_excel_readback=('PM' in methods), parameters=len(params))
    with arcpy.da.SearchCursor(points, input_fields) as cursor:
        if list(cursor) != original:raise AssertionError('Input attributes/geometry changed')
    report = dict(passed=True, kind=args.kind, runtime=arcpy.GetInstallInfo(), cases=reports,
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
            ['Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt','Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt','mirsad_core/toolbox_pm.py','mirsad_core/toolbox_enrichment.py']},
        limits=['Synthetic offline provider responses', args.kind+' native execution',
                'Raster disabled; independent raster routing covered separately', 'No ArcMap claim'])
    (folder/'acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Native PM acceptance passed: HG / PM / both; FAO56 and unchanged HG', flush=True)


if __name__ == '__main__':
    args = arguments()
    if args.native_worker:
        try:main()
        except Exception:
            print(traceback.format_exc(), flush=True);raise
    else:
        if args.output.resolve().exists():raise ValueError('Preserve earlier QA evidence; choose a fresh folder')
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--native-worker']+sys.argv[1:])
        try:raise SystemExit(process.wait(timeout=args.timeout))
        except subprocess.TimeoutExpired:
            process.terminate();process.wait();raise SystemExit('Native PM acceptance timed out; outputs retained')
