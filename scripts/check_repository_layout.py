"""Check active repository paths and Desktop documentation links, without GIS."""
import re
from pathlib import Path
from urllib.parse import unquote,urlsplit

ROOT=Path(__file__).resolve().parents[1]


def main():
    assert not (ROOT/'utils').exists(), 'Use mirsad_core, not the retired utils directory'
    assert not list(ROOT.glob('*.pyt')), 'Toolboxes belong in Toolboxes/'
    names=('MIRSAD_Climate_Atlas_Generator_10_8.pyt',
           'MIRSAD_Weather_Stations_Atlas_Generator.pyt',
           'MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt')
    for name in names:assert (ROOT/'Toolboxes'/name).is_file(),name
    assert (ROOT/'mirsad_core/__init__.py').is_file()
    pages=[ROOT/name for name in ('README.md','AGENTS.md','CONTRIBUTING.md','CONTRIBUTING_AR.md',
           'Toolboxes/README.md','Toolboxes/AGENTS.md','mirsad_core/README.md',
           'MIRSAD Desktop/README.md','MIRSAD Desktop/AGENTS.md','Documents/DEVELOPMENT_PUBLICATION.md',
           'Documents/SOURCE_UPDATE_2026_10_22.md',
           'Documents/00_Documentation_Index.md','Documents/00_Documentation_Index_AR.md',
           'Documents/05_Climate_Data_Sources_Directory/README.md','Documents/07_Climate_Sources_Web_Guide/README.md')]
    pages+=list((ROOT/'MIRSAD Desktop/docs').rglob('*.md'))
    checked=0;missing=[]
    for path in pages:
        for target in re.findall(r'\]\(([^\n)]+)\)',path.read_text(encoding='utf-8-sig')):
            target=target.strip('<>').split('#')[0]
            if not target or re.match(r'^[a-zA-Z]+:',target) or target.startswith('/'):continue
            checked+=1
            if not (path.parent/unquote(urlsplit(target).path)).exists():missing.append(str(path.relative_to(ROOT))+': '+target)
    if missing:raise AssertionError('Broken documentation links:\n'+'\n'.join(missing))
    print('Layout and',checked,'local documentation links passed.')


if __name__=='__main__':main()
