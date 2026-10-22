"""Record current-source Toolbox evidence, separately from earlier frozen builds."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'MIRSAD Desktop/docs/reports/climate-enrichment/TOOLBOX_ACCEPTANCE.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--points', type=Path, default=ROOT/'tests/.output/native-point-enrichment-final/acceptance.json')
    parser.add_argument('--stations', type=Path, default=ROOT/'tests/.output/native-station-enrichment-verified/acceptance.json')
    args = parser.parse_args()
    inputs = dict(points=args.points, stations=args.stations,
                  current_qa=ROOT/'tests/.output/toolbox-enrichment-qa/acceptance.json',
                  isolated=ROOT/'tests/.output/toolbox-enrichment-final/summary.json',
                  python27=ROOT/'tests/.output/python27-toolbox-enrichment-final/summary.json')
    evidence = {key: json.loads(path.read_text(encoding='utf-8')) for key, path in inputs.items()}
    assert all(value['passed'] for value in evidence.values()), 'A required acceptance gate failed'
    assert evidence['current_qa']['source_sha256'] == hashlib.sha256((ROOT/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt').read_bytes()).hexdigest()
    for key, count in (('points', 81), ('stations', 88)):
        assert evidence[key]['kind'] == key and evidence[key]['parameters'] == count
        assert evidence[key]['added_fields'] == 220 and evidence[key]['points'] == 3
    sources = ['Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt',
               'Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt',
               'mirsad_core/toolbox_enrichment.py', 'mirsad_core/daily_climate.py',
               'tests/test_toolbox_enrichment.py', 'scripts/verify_toolbox_enrichment.py',
               'scripts/verify_toolbox_enrichment_qa.py',
               'Documents/Help/tool_parameters.json', 'Documents/Help/parameter_notes_ar.json']
    result = dict(recorded=datetime.datetime.now(datetime.timezone.utc).isoformat(), passed=True,
        scope='11 optional daily variables in Point/Station source; native Pro with synthetic offline source responses',
        evidence=evidence,
        evidence_sha256={str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs.values()},
        source_sha256={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources},
        python27_skips=['Desktop summary parity and openpyxl readback require Python 3; 9 other new checks ran on Python 2.7'],
        limits=['No live Toolbox provider acceptance', 'Supplementary raster native acceptance pending',
                'Toolbox PM and optional DEM remain pending', 'Native ArcMap remains pending',
                'Existing frozen candidate/installer evidence belongs to the earlier Desktop source snapshot'])
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Recorded Toolbox acceptance:', sum(item['tests'] for item in evidence['isolated']['results']),
          'isolated tests; native Pro Point and Station passed')


if __name__ == '__main__':main()
