"""Read-only comparison of shipped Python code against the current source tree.

Ignore source filenames/line tables, and only the generated science module's
source-hash docstring. Do not execute code extracted from the executable.
"""
import hashlib
import argparse
import json
from pathlib import Path
import types
from PyInstaller.archive.readers import CArchiveReader

ROOT=Path(__file__).resolve().parents[1]


def signature(code,ignore_doc=False):
    values=[]
    for index,value in enumerate(code.co_consts):
        if ignore_doc and index==0 and isinstance(value,str):values.append('<generated source-hash documentation>')
        elif isinstance(value,types.CodeType):values.append(signature(value))
        elif isinstance(value,frozenset):values.append(sorted(map(repr,value)))
        else:values.append(repr(value))
    return dict(bytecode=code.co_code.hex(),constants=values,names=code.co_names,varnames=code.co_varnames,
        freevars=code.co_freevars,cellvars=code.co_cellvars,argcount=code.co_argcount,kwonly=code.co_kwonlyargcount,
        posonly=code.co_posonlyargcount,flags=code.co_flags,stack=code.co_stacksize,exceptions=code.co_exceptiontable.hex())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe',type=Path,default=ROOT/'runtime/development/MIRSAD.exe')
    parser.add_argument('--report',type=Path,default=ROOT/'.test-output/packaged_source_equivalence.json')
    args=parser.parse_args()
    exe=args.exe.resolve(strict=True)
    archive=CArchiveReader(str(exe));pyz=archive.open_embedded_archive('PYZ.pyz')
    checks=[]
    modules=('science','hybrid_pipeline','climate_sources','climate_products','protected_sources','remote_grid',
        'climate','services','exports','regional','ui','workspace','jobs','process_worker','ui_acceptance','registry','userguide','themes',
        'daily_climate','elevation','enrichment','excel_stream','tabular','tools','analysis')
    for name in modules:
        shipped=pyz.extract('mirsad_desktop.'+name)
        path=ROOT/'src/mirsad_desktop'/(name+'.py')
        current=compile(path.read_text(encoding='utf-8'),str(path),'exec',optimize=0)
        a=signature(shipped,ignore_doc=name=='science');b=signature(current,ignore_doc=name=='science')
        checks.append(dict(module=name,equivalent=a==b,source_documentation_matches=shipped.co_consts[0]==current.co_consts[0]))
    result=dict(passed=all(c['equivalent'] and c['source_documentation_matches'] for c in checks),checks=checks,exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
        scope='Static code comparison; no extracted code executed. Filenames/line tables and generated science source-hash docstring excluded. This does not verify native ArcGIS raster workspace changes.')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
