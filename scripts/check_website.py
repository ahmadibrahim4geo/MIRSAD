"""Verify relocated web links, real registry coverage and deterministic rendering."""
from collections import Counter
from html.parser import HTMLParser
import json
import re
from urllib.parse import unquote, urlsplit

from build_website import ROOT, SOURCE_PAGE, render, source_cards, MODULES, home_cards
from build_climate_source_catalogue import catalogue
from website_content import SOURCE_AR, VARIABLES


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.links=[];self.source_ids=[];self.modules=0;self.langs=Counter()
        self.feed(text)

    def handle_starttag(self,tag,attributes):
        attr=dict(attributes)
        if 'id' in attr:self.ids.append(attr['id'])
        for name in ('href','src'):
            if attr.get(name):self.links.append(attr[name])
        if 'data-language' in attr:
            assert attr['data-language']==attr.get('lang'),'Language spans must declare their language'
            self.langs[attr['data-language']]+=1
        if attr.get('data-filter-card')=='sources':self.source_ids.append(attr['id'])
        if attr.get('data-filter-card')=='modules':self.modules+=1


def main():
    assert not (ROOT/'climate-sources.html').exists(),'Source page belongs in Documents/07_Climate_Sources_Web_Guide/'
    data=catalogue()
    assert set(SOURCE_AR)=={source['id'] for source in data['sources']}
    for source in data['sources']:
        assert set(source['variables'])<=set(VARIABLES)
        assert set(SOURCE_AR[source['id']])=={'label','start','end','resolution','temporal','region'}
        for value in SOURCE_AR[source['id']].values():assert any('\u0600'<=char<='\u06ff' for char in value)
    for path in (ROOT/'data/climate_sources.json',ROOT/'MIRSAD Desktop/assets/climate_sources.json'):
        assert json.loads(path.read_text(encoding='utf-8'))==data,'Web update must preserve the reviewed runtime snapshot'
    cards,nav=source_cards(data)
    assert SOURCE_PAGE.read_text(encoding='utf-8')==render('climate-sources.html',{'SOURCE_CARDS':cards,'SOURCE_NAV':nav,'REVIEWED':data['reviewed']}),'Regenerate source page'
    # Compare generated home page without mutating checked-in files.
    assert (ROOT/'index.html').read_text(encoding='utf-8')==render('index.html',{'MODULE_CARDS':home_cards()}),'Regenerate home page'
    documents={path:Page(path.read_text(encoding='utf-8')) for path in (ROOT/'index.html',SOURCE_PAGE)}
    help_ids={s['id'] for s in json.loads((ROOT/'MIRSAD Desktop/assets/help_index.json').read_text(encoding='utf-8'))['sections']}
    checked=0
    for path,page in documents.items():
        assert len(page.ids)==len(set(page.ids)),path
        assert page.langs['ar']==page.langs['en'],(path,page.langs)
        for link in page.links:
            url=urlsplit(link)
            if url.scheme or url.netloc:continue
            target=(path.parent/unquote(url.path)).resolve() if url.path else path
            assert target.is_relative_to(ROOT) and target.is_file(),(path,link)
            checked+=1
            if url.fragment and target.suffix=='.html':
                if target==ROOT/'Help/index.html':assert url.fragment in help_ids,link
                else:
                    parsed=documents.get(target) or Page(target.read_text(encoding='utf-8'))
                    assert unquote(url.fragment) in parsed.ids,(path,link)
    assert documents[SOURCE_PAGE].source_ids==[s['id'] for s in data['sources']]
    assert documents[ROOT/'index.html'].modules==len(MODULES)==19
    css=(ROOT/'assets/site.css').read_text(encoding='utf-8')
    assert not re.search(r'\.pipeline\s+span\s*\{',css),'Only direct pipeline steps may be framed; translated labels must not get a second border'
    for resource in re.findall(r"url\(['\"]?([^)'\"]+)",css):
        assert (ROOT/'assets'/resource).is_file(),resource
    home=(ROOT/'index.html').read_text(encoding='utf-8')
    assert all(key in home for key in ('class="author-bio"','class="consultation"','#icon-github','#icon-mail','#icon-whatsapp'))
    for path in (ROOT/'Documents/04_Interactive_HTML_Guides').glob('*.html'):
        assert 'href="../../climate-sources.html"' not in path.read_text(encoding='utf-8-sig'),path
    print('Website passed:',checked,'local links/assets/anchors;',len(data['sources']),'fully localized source profiles; 19 registry modules; generated pages and runtime snapshots unchanged.')


if __name__=='__main__':main()
