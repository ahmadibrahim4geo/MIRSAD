"""Static field/parameter audit; does not import native ArcGIS or claim runtime parity."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
sys.path[:0]=[str(ROOT/'src'),str(REPO)]
from mirsad_desktop.registry import MODULES,module_fields
from mirsad_desktop.science import compute_point_fields
from mirsad_desktop.exports import station_properties
from mirsad_desktop.inputs import make_point


def main():
    loader=importlib.machinery.SourceFileLoader('mirsad_contract_reference',str(REPO/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt'))
    spec=importlib.util.spec_from_loader(loader.name,loader);core=importlib.util.module_from_spec(spec);loader.exec_module(core)
    sample=station_properties(make_point('A','Contract fixture',31.,30.))
    monthly={p:{(y,m):v+(y-2023) for y in (2023,2024) for m in range(1,13)} for p,v in dict(T2M=20.,T2M_MAX=25.,T2M_MIN=15.,PRECTOTCORR=30.,TS=28.,RH2M=60.,T2MDEW=12.,PS=100.,SLP=101.3,WS10M=3.,WD10M=350.,ALLSKY_SFC_SW_DWN=15.,ALLSKY_SFC_UV_INDEX=5.,CLOUD_AMT=40.).items()}
    rows=[]
    for module in MODULES:
        computed=compute_point_fields(monthly,[2023,2024],[module.name],'Daily',precip_totals=True,gap_method='none',lat=30.,monthly_ranges=True)
        actual=list(module_fields(module.name,computed))
        reference=list(core.MODULE_FIELDS.get(module.name,[]))
        rows.append(dict(module=module.name,legacy_fields=reference,desktop_fields=actual,
            missing_in_desktop=sorted(set(reference)-set(actual)),extra_in_desktop=sorted(set(actual)-set(reference))))
    admin=[v[0] for v in core.ADMIN_FIELDS]
    report=dict(scope='Static declared fields on a complete two-year deterministic fixture with monthly ranges enabled; no native ArcGIS import required and no full output parity claim',
        modules=rows,legacy_admin_fields=admin,desktop_station_fields=list(sample),
        legacy_metadata_not_in_desktop=sorted(set(admin)-set(sample)-{'Data_Start','Data_End','Measurement_Unit','Status','Error_Msg'}),
        remaining=['Exact metadata names/types/order','Input attribute retention and station identifier mappings','Daily wide versus long table layout','Legacy short filenames/folders and .xls versus Desktop .xlsx','Advanced submodel/field filters and raster parameter mapping','Native ArcMap runtime and approved interpolation tolerances'])
    target=ROOT/'docs/reports/OUTPUT_CONTRACT_AUDIT.json';target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Output contract audit','','Static audit of current declarations and a complete two-year fixture with monthly ranges enabled; no complete runtime parity is claimed.','','| Module | Legacy fields | Desktop fields | Missing declared fields |','|---|---:|---:|---|']
    for r in rows:lines.append('| '+r['module']+' | '+str(len(r['legacy_fields']))+' | '+str(len(r['desktop_fields']))+' | '+(', '.join(r['missing_in_desktop']) or 'None')+' |')
    lines.extend(['','Legacy metadata absent from the current Desktop property contract: '+', '.join(report['legacy_metadata_not_in_desktop']),
        '','Remaining validation/change scopes: '+ '; '.join(report['remaining']),
        '','Scientific calculations and shared source code do not establish identical file schemas. See OUTPUT_CONTRACT_AUDIT.json for every declared field.'])
    (ROOT/'docs/reports/OUTPUT_CONTRACT_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))


if __name__=='__main__':main()
