"""Reviewed equation prose plus field names from the pure calculation registry.

No ArcPy import. Documentation generation never changes scientific functions.
"""
import ast,hashlib,html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'Documents/Help'
sys.path.insert(0,str(ROOT/'src'))
from mirsad_desktop.registry import MODULES,module_fields
from mirsad_desktop.science import compute_point_fields


def calculation_fields(module):
    values=dict(T2M=20.,T2M_MAX=25.,T2M_MIN=15.,PRECTOTCORR=50.,TS=28.,RH2M=60.,T2MDEW=12.,
        PS=100.,SLP=101.3,WS10M=3.,WD10M=350.,ALLSKY_SFC_SW_DWN=18.,ALLSKY_SFC_UV_INDEX=1.,CLOUD_AMT=40.)
    monthly={p:{(year,month):value for year in (2023,2024) for month in range(1,13)} for p,value in values.items()}
    fields=compute_point_fields(monthly,[2023,2024],[module],'Daily',precip_totals=True,gap_method='none',lat=30.,monthly_ranges=True)
    return sorted(module_fields(module,fields))


def evidence():
    spec=json.loads((SOURCE/'formulas.json').read_text(encoding='utf-8'))
    if {e['module'] for e in spec['entries']}!={m.name for m in MODULES}:raise ValueError('Equation manual must cover all module groups')
    source=ROOT.parent/'Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt'
    tree=ast.parse(source.read_text(encoding='utf-8-sig'));functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    names=sorted({name for e in spec['entries'] for name in e['functions']}|{'climat_monthly_means','monthly_interannual_ranges','convert_fields_to_user_units','safe_mean','safe_sum','is_missing','daylength_hours','uv_mean24_to_noonmax','circular_mean_deg'})
    signatures={name:hashlib.sha256(ast.dump(functions[name],include_attributes=False).encode('utf-8')).hexdigest() for name in names}
    constants={}
    wanted={'SEASONS','MISSING_SENTINELS','MONTH_NAMES_EN','BASELINE_YEARS','BASELINE_MIN_YEARS','RECENT_WINDOW','RECENT_MIN_YEARS','TREND_MIN_YEARS'}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in wanted:constants[target.id]=ast.dump(node.value,include_attributes=False)
    return dict(reviewed=spec['reviewed'],functions=signatures,constants=constants,modules={m.name:calculation_fields(m.name) for m in MODULES})


def check_review():
    actual=evidence();expected=json.loads((SOURCE/'formula_review.json').read_text(encoding='utf-8'))
    if actual!=expected:raise ValueError('Scientific help review is stale: review function/field changes before updating formula_review.json')


from help_field_reference import field_reference


def field_rule(module,field,arabic):
    """Compatibility accessor for the specific calculation description."""
    return field_reference(module,field,arabic)['calculation']


def formula_body(module,language):
    spec=json.loads((SOURCE/'formulas.json').read_text(encoding='utf-8'))
    item=next(e for e in spec['entries'] if e['module']==module);arabic=language=='ar'
    meta=next(m for m in MODULES if m.name==module)
    def heading(ar,en):return '<h3>'+(ar if arabic else en)+'</h3>'
    parts=['<p><a href="#calculation-flow">'+('الرموز وتدفق الحساب' if arabic else 'Symbols and calculation flow')+'</a> · <a href="#calculation-units">'+('الوحدات' if arabic else 'Units')+'</a></p>']
    parts.append(heading('متغيرات المصدر والتبعيات','Source variables and dependencies'))
    parts.append('<p dir="ltr">'+html.escape(', '.join(meta.params))+'</p>')
    parts.append('<p>'+('المتغيرات المدرجة رموز داخلية معيارية؛ يشرح رابط الرموز معناها ووحداتها. قد يختلف اسم الحقل في استجابة المصدر أو صفوف Daily.' if arabic else 'These are normalized internal variable codes; the symbols link explains their meaning and units. Provider response or Daily column layouts can use different names.')+'</p>')
    if module in ('Evapotranspiration','UNEP Aridity','Water Deficit','UV Index'):
        parts.append('<p>'+('يستخدم هذا الحساب أيضًا خط العرض Latitude.' if arabic else 'This calculation also uses Latitude.')+'</p>')
    parts.append(heading('المعادلات كما ينفذها المحرك','Equations implemented by the kernel'))
    parts.extend('<p dir="ltr"><code>'+html.escape(equation)+'</code></p>' for equation in item['equations'])
    for title_ar,title_en,key in [('كيف يطبقها مرصاد','How MIRSAD applies it','steps'),('شروط الصلاحية والفقد','Validity and missing-data rules','limits'),('مثال محسوب','Worked example','example')]:
        parts.extend([heading(title_ar,title_en),'<p>'+html.escape(item[key+'_'+language])+'</p>'])
    parts.append(heading('ربط المعادلة بأسماء الأعمدة','Equation-to-output-column mapping'))
    parts.append('<p>'+('هذه مجموعة أعمدة الحساب الممكنة، مع تفعيل المدى الشهري. قد يخفي مرشح الحقول/الفصول وخيارات HI/WC بعضها؛ إدراج عمود هنا لا يعني تفعيله في كل تشغيل. الجداول الناتجة تحفظ القيم المحسوبة؛ لا يعيد مرصاد حساب المؤشر من Excel المقرب.' if arabic else 'This is the possible calculation field set with monthly ranges enabled. Field/season filters and HI/WC options can hide fields; listing a field does not enable it in every run. Outputs store calculated values; MIRSAD does not recalculate indices from rounded Excel cells.')+'</p>')
    parts.append('<p>'+('كل صف أدناه يشرح عمودًا في جدول النتائج، وليس محطة أو سنة منفصلة. اسم العمود التقني يبقى كما هو في Excel وGIS؛ الاسم الواضح والفترة يشرحان معناه. الوحدات هنا وحدات الحساب الأساسية؛ خيارات التصدير قد تحولها كما في صفحة الوحدات. NULL قيمة مفقودة وليست صفرًا.' if arabic else 'Each row below describes an output column, not a separate station or year. Technical keys remain unchanged in Excel/GIS; the readable name and period explain their meaning. Units below are calculation units; export options may convert them as explained on the units page. NULL is missing, not zero.')+'</p>')
    parts.append('<table width="100%" class="field-reference"><tr><th>'+('العمود ومعناه والفترة' if arabic else 'Field, meaning and period')+'</th><th>'+('وحدة الحساب' if arabic else 'Calculation unit')+'</th><th>'+('ما الذي يحسبه هذا العمود تحديدًا؟' if arabic else 'What exactly does this column calculate?')+'</th></tr>')
    for field in calculation_fields(module):
        info=field_reference(module,field,arabic)
        parts.append('<tr><td><p dir="ltr"><code>'+html.escape(field)+'</code></p><p><b>'+html.escape(info['title'])+'</b><br>'+html.escape(info['period'])+'</p></td><td>'+html.escape(info['unit'])+'</td><td>'+html.escape(info['calculation'])+'</td></tr>')
    parts.append('</table>'+heading('مرجع التنفيذ','Implementation reference'))
    parts.append('<p dir="ltr">Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt → '+html.escape(', '.join(item['functions']))+'<br>MIRSAD Desktop/src/mirsad_desktop/science.py</p>')
    parts.append('<p>'+('المعادلات من النواة المشتركة. تجهيز البيانات، حراس التغطية، ترشيح الحقول والوحدات النهائية قد تختلف بين الواجهتين؛ لا تعني مشاركة النواة تطابق جميع ملفات الإخراج.' if arabic else 'Equations come from the shared kernel. Input preparation, coverage guards, field filtering and final units can differ between hosts; a common kernel does not establish identical output files.')+'</p>')
    return ''.join(parts)
