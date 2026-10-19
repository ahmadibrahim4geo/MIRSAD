"""Build the two static website pages from templates and implemented registries.

No runtime/scientific data is changed. Local assets also work with file:// URLs.
"""
import html
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT/'Documents/07_Climate_Sources_Web_Guide/climate-sources.html'
sys.path.insert(0, str(ROOT/'MIRSAD Desktop/src'))
from mirsad_desktop.registry import MODULES
from website_content import SOURCE_AR, VARIABLES, TOOLS, MODULE_DESCRIPTIONS


def bi(ar, en):
    return '<span data-language="ar" lang="ar" dir="rtl">'+html.escape(ar)+'</span><span data-language="en" lang="en" dir="ltr">'+html.escape(en)+'</span>'


def source_cards(data):
    cards=[];nav=[]
    units_ar={'deg C':'درجة مئوية','mm per day or native month total':'مم/يوم أو مجموع الشهر الأصلي، حسب المنتج','percent':'نسبة مئوية','kPa':'كيلوباسكال','m/s':'متر/ثانية','degree':'درجة زاوية','MJ/m2/day':'ميجاجول/م²/يوم','source UV index':'مؤشر الأشعة فوق البنفسجية من المصدر'}
    fields={'start':('بداية الأرشيف','Archive starts'),'end':('نهاية الأرشيف','Archive ends'),'resolution':('الدقة المكانية للمصدر','Source spatial resolution'),'temporal':('الفاصل الزمني المستخدم','Ingested time step'),'region':('النطاق الجغرافي','Geographic coverage')}
    for i,s in enumerate(data['sources'],1):
        localized=SOURCE_AR[s['id']]
        temporal='composite' if s['id'].startswith('mod11') else 'monthly' if s['temporal']=='Monthly' else 'daily monthly' if s['id']=='power' else 'daily'
        capabilities=' '.join(tool+':'+('monthly' if tool=='regional' else 'daily') for tool in s['tools']) if s['id']=='power' else ' '.join(tool+':'+temporal for tool in s['tools'])
        auth=bi('يتطلب تسجيل الدخول','Need Sign In') if s['auth'] else bi('دون تسجيل دخول','No sign-in')
        auth_class=' account' if s['auth'] else ''
        facts=''.join('<div><dt>'+bi(*labels)+'</dt><dd>'+bi(localized[key],s[key])+'</dd></div>' for key,labels in fields.items())
        facts+='<div><dt>'+bi('الأدوات المدعومة في مرصاد','Supported MIRSAD tools')+'</dt><dd>'+' · '.join(bi(*TOOLS[tool]) for tool in s['tools'])+'</dd></div>'
        variables=[]
        for variable in s['variables']:
            unit=s['normalized_units'][variable]
            unit_ar,unit_en=units_ar[unit],unit
            if variable=='PRECTOTCORR':
                if s['temporal']=='Monthly':unit_ar,unit_en='مليمتر للشهر (مجموع شهري)','mm per month (monthly total)'
                elif s['id']=='power':unit_ar,unit_en='النقاط والمحطات: مم/يوم؛ الشبكة الإقليمية: مجموع الشهر بالمليمتر','Points/stations: mm/day; regional grid: monthly total in mm'
                else:unit_ar,unit_en='مليمتر لليوم (إجمالي يومي)','mm per day (daily total)'
            variables.append('<li><code dir="ltr">'+variable+'</code><div>'+bi(*VARIABLES[variable])+'<small>'+bi(unit_ar,unit_en)+'</small></div></li>')
        note=s['notes_ar'].replace('Need Sign In:', 'يتطلب تسجيل الدخول:').replace('Gap Fill','استكمال الفجوات').replace('Auto يستخدم Land','الاختيار التلقائي يستخدم ERA5-Land')
        cards.append(f'<article class="card source-card" id="{s["id"]}" data-filter-card="sources" data-tools="{" ".join(s["tools"])}" data-temporal="{temporal}" data-capabilities="{capabilities}" data-auth="{"account" if s["auth"] else "public"}">\n'
            f'<div class="source-heading"><div><span class="number" dir="ltr">{i:02d} / 11</span><h2>'+bi(localized['label'],s['label'].replace(' (Need Sign In)',''))+'</h2></div><span class="pill'+auth_class+'">'+auth+'</span></div>\n'
            '<dl class="source-facts">'+facts+'</dl><p class="source-note">'+bi(note,s['notes_en'])+'</p>\n'
            '<details><summary>'+bi(f'العناصر المتاحة ورموزها ووحداتها ({len(variables)})',f'Available variables, codes and units ({len(variables)})')+'</summary><p class="muted">'+bi('وحدات المدخلات بعد تهيئة بيانات المصدر؛ قد تختلف وحدات أعمدة المخرجات وخياراتها.','Input units after source normalization; output column units and options may differ.')+'</p><ul class="variables">'+''.join(variables)+'</ul></details>\n'
            '<a class="source-link" href="'+html.escape(s['url'],quote=True)+'" rel="noopener noreferrer">'+bi('مرجع المصدر الرسمي ↗','Official source reference ↗')+'</a></article>')
        short=s['label'].split(' (')[0]
        nav_label=bi('MODIS MOD11A2 — نهارًا','MODIS MOD11A2 — Day') if s['id']=='mod11a2_day' else bi('MODIS MOD11A2 — ليلًا','MODIS MOD11A2 — Night') if s['id']=='mod11a2_night' else '<bdi dir="ltr">'+html.escape(short)+'</bdi>'
        nav.append(f'<li><a href="#{s["id"]}">{nav_label}</a></li>')
    return '\n'.join(cards),'\n'.join(nav)


def render(template, values):
    text=(ROOT/'scripts/templates'/template).read_text(encoding='utf-8')
    for key,value in values.items():text=text.replace('{{'+key+'}}',str(value))
    if '{{' in text:raise ValueError('Unresolved website template placeholder')
    return text


def build_sources_page(data):
    cards,nav=source_cards(data)
    SOURCE_PAGE.parent.mkdir(parents=True,exist_ok=True)
    SOURCE_PAGE.write_text(render('climate-sources.html',{'SOURCE_CARDS':cards,'SOURCE_NAV':nav,'REVIEWED':data['reviewed']}),encoding='utf-8')


def home_cards():
    cards=[]
    for index,module in enumerate(MODULES,1):
        category='derived' if module.group=='derived' else 'primary'
        cards.append(f'<article class="card module-card" data-filter-card="modules" data-category="{category}"><span class="number" dir="ltr">{index:02d}</span><h3>'+bi(module.arabic,module.name)+'</h3><p>'+bi(*MODULE_DESCRIPTIONS[module.name])+'</p><div class="pills">'+''.join('<code dir="ltr">'+p+'</code>' for p in module.params)+'</div></article>')
    return '\n'.join(cards)


def build_home():
    (ROOT/'index.html').write_text(render('index.html',{'MODULE_CARDS':home_cards()}),encoding='utf-8')


def main():
    from build_climate_source_catalogue import catalogue
    data=catalogue()
    assert set(SOURCE_AR)=={s['id'] for s in data['sources']}
    assert set(MODULE_DESCRIPTIONS)=={m.name for m in MODULES}
    build_sources_page(data);build_home()
    print('Built index.html and',SOURCE_PAGE.relative_to(ROOT),':',len(MODULES),'modules,',len(data['sources']),'source/product profiles.')


if __name__=='__main__':main()
