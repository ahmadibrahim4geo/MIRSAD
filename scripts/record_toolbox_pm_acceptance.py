"""Record HG/PM source evidence after native Point/Station fixture acceptance."""
import datetime
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def previous_english_description(raw, expected):
    """Prove the exact earlier bytes differ only in the localized tooltip.

    Current native Station and EN/AR metadata cover that later UI assignment.
    Any other byte change fails; no scientific review/hash is overwritten.
    """
    text = raw.decode('utf-8')
    function = next(node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef) and node.name == 'parameters')
    assignment = next(node for node in ast.walk(function) if isinstance(node, ast.Assign) and
                      any(isinstance(target, ast.Attribute) and target.attr == 'description' for target in node.targets))
    lines = text.splitlines(keepends=True)
    newline = '\r\n' if lines[assignment.lineno-1].endswith('\r\n') else '\n'
    lines[assignment.lineno-1:assignment.end_lineno] = ['        p.description = description'+newline]
    return hashlib.sha256(''.join(lines).encode('utf-8')).hexdigest() == expected


def main():
    paths = dict(points=ROOT/'tests/.output/native-toolbox-pm-pro/acceptance.json',
                 stations=ROOT/'tests/.output/native-toolbox-pm-stations-pro/acceptance.json',
                 isolated=ROOT/'tests/.output/toolbox-pm-final/summary.json',
                 python27=ROOT/'tests/.output/python27-toolbox-pm-final/summary.json')
    evidence = {key:json.loads(path.read_text(encoding='utf-8')) for key,path in paths.items()}
    assert all(report['passed'] for report in evidence.values()), 'A required gate failed'
    metadata_only_differences = []
    for kind, count in [('points',83),('stations',90)]:
        assert set(evidence[kind]['cases']) == {'HG','PM','HG_PM'}
        assert all(case['passed'] and case['parameters'] == count for case in evidence[kind]['cases'].values())
        for name, value in evidence[kind]['source_sha256'].items():
            raw = (ROOT/name).read_bytes();current = hashlib.sha256(raw).hexdigest()
            if current != value:
                assert kind == 'points' and name == 'mirsad_core/toolbox_pm.py' and previous_english_description(raw,value), 'Native source evidence stale: '+name
                metadata_only_differences.append(dict(source=name, native_sha256=value, current_sha256=current,
                    difference='Only the p.description localization assignment; reconstructed earlier file matches native hash byte-for-byte. Current Station run and EN/AR parameter snapshot cover localization.'))
    names = ['Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt','Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt',
             'mirsad_core/toolbox_pm.py','mirsad_core/toolbox_enrichment.py','mirsad_core/daily_climate.py',
             'tests/test_toolbox_pm.py','tests/test_toolbox_enrichment.py','scripts/verify_toolbox_pm.py',
             'Documents/Help/tool_parameters.json','Documents/Help/parameter_notes_ar.json']
    result = dict(passed=True, recorded=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='HG / daily FAO56 PM / both in Point and Station, native Pro with offline synthetic source responses',
        evidence=evidence,
        metadata_only_source_differences=metadata_only_differences,
        evidence_sha256={str(path.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths.values()},
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
        limits=['No live Toolbox network acceptance','Native PM raster acceptance pending; dispatch tested in isolation',
                'No native ArcMap acceptance','Optional DEM in Toolbox remains pending',
                '21 October frozen candidate/installer do not package these later source/help changes'])
    target = ROOT/'MIRSAD Desktop/docs/reports/climate-enrichment/TOOLBOX_PM_ACCEPTANCE.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Recorded Toolbox PM acceptance:',sum(item['tests'] for item in evidence['isolated']['results']),'isolated tests; six native method cases passed')


if __name__ == '__main__':main()
