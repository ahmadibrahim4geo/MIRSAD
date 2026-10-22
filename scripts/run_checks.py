"""Run deterministic legacy suites in isolated processes (no ArcPy mock leakage).

Python 3 runner; --python may select legacy Python 2.7 for compatible suites.
Native ArcGIS scripts are intentionally explicit, licensed host checks.
"""
import argparse,concurrent.futures,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SUITES=('test_arcgis_pro_compatibility.py','test_climate_products.py','test_climate_enrichment_baseline.py','test_daily_climate.py','test_data_quality.py',
 'test_drought_dependencies_108.py','test_excel_export_108.py','test_hybrid_pipeline.py',
 'test_migrate_legacy_database.py','test_modifications.py','test_remote_grid.py','test_repository_layout.py',
 'test_runtime_stability.py','test_station_multi_selection.py','test_tool_validation.py',
 'test_weather_stations_atlas.py','test_weather_stations_dual_lang.py',
 'test_workflow_and_temporal_scope.py','test_yearly_excel_export.py','test_xlsx_stream.py','test_toolbox_enrichment.py','test_toolbox_pm.py')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--python',default=sys.executable)
    parser.add_argument('--jobs',type=int,default=3);parser.add_argument('--suite',action='append',choices=SUITES)
    parser.add_argument('--output',type=Path,default=ROOT/'tests/.output/isolated')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    def run(name):
        start=time.monotonic();command=[args.python,'-m','unittest','discover','-s','tests','-p',name,'-v']
        try:
            process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=90,env=dict(os.environ,PYTHONIOENCODING='utf-8'))
            output=process.stdout+process.stderr;code=process.returncode
        except subprocess.TimeoutExpired as error:output=(error.stdout or b'')+(error.stderr or b'');code='timeout'
        (args.output/(name+'.log')).write_bytes(output)
        match=re.search(rb'Ran (\d+) tests?',output)
        result=dict(suite=name,exit=code,tests=int(match[1]) if match else None,seconds=round(time.monotonic()-start,2))
        print(json.dumps(result),flush=True);return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(args.jobs,4))) as executor:
        results=list(executor.map(run,args.suite or SUITES))
    report=dict(python=args.python,isolated=True,passed=all(r['exit']==0 for r in results),results=results)
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
