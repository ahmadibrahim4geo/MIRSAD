"""Fast deterministic contracts for a clean source checkout. No ArcGIS/network."""
import ast,hashlib,json,sqlite3,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DESKTOP=ROOT/'MIRSAD Desktop'
sys.path.insert(0,str(DESKTOP/'scripts'));sys.path.insert(0,str(DESKTOP/'src'))

def main():
    from check_repository_layout import main as check_layout
    check_layout()
    from check_website import main as check_website
    check_website()
    from help_formulas import check_review
    from help_dynamic import parameter_body
    from audit_climate_enrichment import check as check_climate_baseline
    check_climate_baseline()
    from mirsad_desktop import __version__
    check_review()
    index=json.loads((DESKTOP/'assets/help_index.json').read_text(encoding='utf-8'))
    assert index['version']==__version__
    ids={item['id'] for item in index['sections']}
    assert len(ids)==len(index['sections'])
    for language in ('ar','en'):
        chm=ROOT/('Help/MIRSAD_Help_'+language.upper()+'.chm')
        data=chm.read_bytes()
        assert data[:4]==b'ITSF' and b'/$FIftiMain' in data
        assert data==(DESKTOP/'assets'/chm.name).read_bytes()
        assert all(('/'+key+'.html').encode() in data for key in ids)
        assert '<script' in (ROOT/('Help/MIRSAD_Help_'+language.upper()+'.html')).read_text(encoding='utf-8')
        for tool in ('points','stations','raster'):assert parameter_body(tool,language)
    for name in ('hybrid_pipeline.py','climate_sources.py','climate_products.py','remote_grid.py','protected_sources.py','daily_climate.py'):
        assert (ROOT/'mirsad_core'/name).read_bytes()==(DESKTOP/'src/mirsad_desktop'/name).read_bytes(),name
    source=ast.parse((ROOT/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt').read_text(encoding='utf-8-sig'))
    functions={n.name:ast.dump(ast.parse(ast.unparse(n)).body[0],include_attributes=False) for n in source.body if isinstance(n,ast.FunctionDef)}
    vendored=ast.parse((DESKTOP/'src/mirsad_desktop/science.py').read_text(encoding='utf-8'))
    for node in vendored.body:
        if isinstance(node,ast.FunctionDef):assert functions[node.name]==ast.dump(node,include_attributes=False),node.name
    catalogue=ROOT/'data/stations.sqlite'
    with sqlite3.connect(catalogue) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert db.execute('SELECT COUNT(*) FROM stations').fetchone()[0]==28066
    assert hashlib.sha256(catalogue.read_bytes()).digest()==hashlib.sha256((DESKTOP/'assets/stations.sqlite').read_bytes()).digest()
    for file in ('CONTRIBUTING.md','CONTRIBUTING_AR.md','SECURITY.md','SUPPORT.md','CODE_OF_CONDUCT.md','Documents/TESTING.md'):
        assert (ROOT/file).is_file(),file
    for path in (ROOT/'Toolboxes').glob('*.pyt.xml'):ET.parse(path)
    print('Repository contracts passed:',__version__,len(ids),'bilingual topics; CHM index, source parity and catalogue verified.')
if __name__=='__main__':main()
