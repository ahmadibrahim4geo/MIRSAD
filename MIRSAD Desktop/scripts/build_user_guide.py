"""Build offline Qt and browser help from reviewed bilingual topic files."""
import html,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'Documents/Help'
sys.path.insert(0,str(ROOT/'src'))
from mirsad_desktop import __version__
from mirsad_desktop.registry import MODULES
from help_dynamic import provider_body,module_table,parameter_body,supplementary_body
from help_formulas import check_review,formula_body

def build():
    check_review()
    manifest=json.loads((SOURCE/'topics.json').read_text(encoding='utf-8'));sections=[];ids=set()
    for item in manifest['topics']:
        key=item['id']
        if key in ids or not key.replace('-','').replace('_','').isalnum():raise ValueError('Invalid/duplicate help topic '+key)
        ids.add(key);section=dict(item)
        for language in ('ar','en'):
            text=(SOURCE/language/(key+'.html')).read_text(encoding='utf-8')
            text=text.replace('{{VERSION}}',__version__).replace('{{PROVIDERS}}',provider_body(language)).replace('{{MODULE_TABLE}}',module_table(language=='ar'))
            text=text.replace('{{SUPPLEMENTARY}}',supplementary_body(language))
            for tool in ('points','stations','raster'):
                marker='{{PARAMETERS:'+tool+'}}'
                if marker in text:text=text.replace(marker,parameter_body(tool,language))
            for module in MODULES:
                marker='{{FORMULA:'+module.name+'}}'
                if marker in text:text=text.replace(marker,formula_body(module.name,language))
            if '{{' in text:raise ValueError('Unresolved help template '+key)
            section[language+'_body']=text
        sections.append(section)
    index=dict(version=__version__,reviewed=json.loads((SOURCE/'tool_parameters.json').read_text(encoding='utf-8'))['reviewed'],modules=[m.name for m in MODULES],groups=manifest['groups'],sections=sections)
    (ROOT/'assets/help_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    template=(SOURCE/'viewer.html').read_text(encoding='utf-8')
    payload=json.dumps(index,ensure_ascii=False).replace('</','<\\/')
    output=ROOT.parent/'Help';output.mkdir(exist_ok=True)
    for language in ('ar','en'):
        title='مركز مساعدة مرصاد' if language=='ar' else 'MIRSAD Help Centre'
        body=''.join('<a name="'+s['id']+'"></a><h2>'+html.escape(s[language])+'</h2>'+s[language+'_body'] for s in sections)
        page='<!doctype html><html lang="'+language+'" dir="'+('rtl' if language=='ar' else 'ltr')+'"><head><meta charset="utf-8"></head><body><h1>'+title+'</h1>'+body+'</body></html>'
        (ROOT/('assets/help_'+language+'.html')).write_text(page,encoding='utf-8')
        browser=template.replace('@@LANG@@',language).replace('@@PAYLOAD@@',payload)
        (ROOT/('docs/user/USER_GUIDE_'+language.upper()+'.html')).write_text(browser,encoding='utf-8')
        (output/('MIRSAD_Help_'+language.upper()+'.html')).write_text(browser,encoding='utf-8')
    (output/'index.html').write_text(template.replace('@@LANG@@','en').replace('@@PAYLOAD@@',payload),encoding='utf-8')
    (ROOT/'assets/help.html').write_text('<!doctype html><meta charset="utf-8"><a href="help_ar.html">العربية</a> · <a href="help_en.html">English</a>',encoding='utf-8')
    print('Built bilingual help:',len(sections),'topics;',len(MODULES),'scientific groups')

if __name__=='__main__':build()
