"""Recheck current Toolbox QA against existing native outputs; no recalculation."""
import argparse
import datetime as dt
import hashlib
import json
import runpy
from pathlib import Path
import verify_toolbox_enrichment as native

ROOT = Path(native.ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--points', type=Path, default=ROOT/'tests/.output/native-point-enrichment-final')
    parser.add_argument('--stations', type=Path, default=ROOT/'tests/.output/native-station-enrichment-verified')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--refresh-parameters', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT/'tests/.output') or output.exists():raise ValueError('Choose a fresh tests/.output QA folder')
    print('STAGE: native ArcPy import', flush=True)
    import arcpy
    core = native.load('native_current_qa_core', str(ROOT/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt'))
    output.mkdir()
    reports = {}
    for kind, base in (('points', args.points.resolve()), ('stations', args.stations.resolve())):
        if not base.is_relative_to(ROOT/'tests/.output'):raise ValueError('Native QA input outside tests/.output')
        previous = json.loads((base/'acceptance.json').read_text(encoding='utf-8'))
        if not previous['passed']:raise ValueError('Native execution/readback must pass before QA-only follow-up')
        atlas = base/'Atlas'
        databases = list(atlas.glob('Climate_Database_*.gdb'))
        if len(databases) != 1:raise ValueError('Ambiguous output database')
        modules = ['Temperature', 'Wind', 'Relative Humidity', 'Solar Radiation']
        layers = {name: str(databases[0]/core.MODULE_SHORT[name]) for name in modules}
        wanted = {name: [f.name for f in arcpy.ListFields(layers[name])
                        if f.name in core.MODULE_FIELDS[name] or core.enrichment.variable_for_field(f.name)] for name in modules}
        messages, warnings = [], []
        checks = core.PowerClimateAtlasGenerator()._run_qa(layers, dict(vec=str(atlas/'00_Tables_And_Reports')),
            modules, [], [], messages.append, warnings.append, wanted_fields_by_module=wanted)
        if not all(ok for name, ok, detail in checks):raise AssertionError(warnings)
        reports[kind] = dict(checks=checks, output_database=str(databases[0]), original_warnings=previous['warnings'],
            passed=True, scope='Read-only current QA on the existing native fixture output; no new processing or raster acceptance')
    if args.refresh_parameters:runpy.run_path(str(ROOT/'scripts/export_help_parameters.py'), run_name='__main__')
    result = dict(passed=True, reports=reports, recorded=dt.datetime.now(dt.timezone.utc).isoformat(),
        source_sha256=hashlib.sha256((ROOT/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt').read_bytes()).hexdigest(),
        note='Original native runs flagged old static SHP-name QA; current QA recognizes the actual supplementary mapping. Original evidence is retained.')
    (output/'acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Current native-output QA passed for Point and Station', flush=True)


if __name__ == '__main__':main()
