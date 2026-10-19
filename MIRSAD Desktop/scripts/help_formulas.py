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
    source=ROOT.parent/'MIRSAD_Climate_Atlas_Generator_10_8.pyt'
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


MONTHS=('January','February','March','April','May','June','July','August','September','October','November','December')
SEASONS={'Winter':(12,1,2),'Spring':(3,4,5),'Summer':(6,7,8),'Autumn':(9,10,11)}


def field_rule(module,field,arabic):
    """Map every emitted field to its actual operation; unknowns fail the build."""
    def text(ar,en):return ar if arabic else en
    if module=='Trends & Anomalies':
        if field.endswith('_Month_Pct'):return text('متوسط النسب الشهرية المحسوبة والمقربة؛ ليس نسبة المتوسط السنوي بالضرورة.','Mean of calculated/rounded monthly percentages; not necessarily the annual percentage.')
        if field in ('T_Anom_Month','R_Anom_Month','T_Month_Trend_Decade','R_Month_Trend_Decade'):return text('متوسط القيم الشهرية الصالحة من أعمدة الشذوذ/الاتجاه، بعد حسابها وتقريبها.','Mean valid monthly anomaly/trend outputs after those outputs have been calculated and rounded.')
        if 'Trend_Decade' in field:return text('ميل OLS ×10 لسلسلة السنة/الفصل/شهر التقويم المحدد؛ ≥8 سنوات صالحة.','OLS slope ×10 for the indicated annual/seasonal/calendar-month series; ≥8 valid years.')
        if 'Anom' in field:return text('متوسط الحديث ناقص خط الأساس للفترة المحددة'+('؛ النسبة ×100/abs(خط الأساس)، بشرط ≥5 مم.' if field.endswith('_Pct') else '.'),'Recent minus baseline mean for the indicated period'+('; percentage ×100/abs(baseline), requiring ≥5 mm.' if field.endswith('_Pct') else '.'))
    special={
        'DM_Aridity_Annual':('round(P_ann/(T_ann+10),2)','round(P_ann/(T_ann+10),2)'),
        'UNEP_Aridity_Annual':('round(P_ann/PET_ann,3)','round(P_ann/PET_ann,3)'),
        'Water_Deficit_Annual':('round(P_ann-PET_ann,1)','round(P_ann-PET_ann,1)'),
        'Dry_Months_Count':('عدد الشهور الصالحة التي P_m<2T_m، بشرط اكتمال 12 شهرًا.','Count months with P_m<2T_m, requiring all 12 valid months.'),
        'PET_Hargreaves_Annual':('مجموع PET_m للشهور الـ12؛ مم/سنة، تقريب منزلة.','Sum all 12 PET_m values; mm/year, rounded to one decimal.'),
        'T_Max_Summer_Month_Mean':('max(C_6(T2M),C_7(T2M),C_8(T2M))','max(C_6(T2M),C_7(T2M),C_8(T2M))'),
        'T_Min_Winter_Month_Mean':('min(C_12(T2M),C_1(T2M),C_2(T2M))','min(C_12(T2M),C_1(T2M),C_2(T2M))'),
        'T_Annual_Max_Mean':('متوسط الشهور المناخية لـT2M_MAX.','Mean climatological months of T2M_MAX.'),
        'T_Annual_Min_Mean':('متوسط الشهور المناخية لـT2M_MIN.','Mean climatological months of T2M_MIN.'),
        'W_Spd_Annual_Max_Month':('أعلى قيمة للسرعة الشهرية المناخية؛ الناتج سرعة وليس رقم الشهر.','Maximum climatological monthly speed; a speed value, not a month number.'),
        'W_Spd_Annual_Min_Month':('أدنى قيمة للسرعة الشهرية المناخية؛ الناتج سرعة وليس رقم الشهر.','Minimum climatological monthly speed; a speed value, not a month number.'),
        'Sol_Annual_Total':('متوسط مجاميع E[y,m]×أيام الشهر عبر السنوات ذات بيانات؛ انظر قيد التغطية.','Mean yearly sums of E[y,m]×calendar days for years with data; see coverage limitation.'),
        'HI_Winter_Mean':('متوسط Humidex الشهري في DJF؛ لا يستخدم Rothfusz هنا.','Mean monthly Humidex over DJF; this field does not use Rothfusz.'),
        'WBGT_Summer_Mean':('متوسط 0.7Tw+0.3T الشهري في JJA.','Mean monthly 0.7Tw+0.3T over JJA.')}
    if field in special:return special[field][0 if arabic else 1]
    if field.startswith('LST_minus_T_'):
        return text('فرق متوسطات TS وT2M للفترة المحددة، تقريب منزلتين؛ الشهر يستخدم قيمتي الشهر المقربتين.','Difference of TS and T2M means for the indicated period, rounded to two decimals; months use already rounded monthly values.')
    month=next((m for m in MONTHS if '_'+m+'_' in field),None)
    if month and field.endswith('_Range'):
        if field.startswith('ET_'):return text('max(PET[y,m])-min(PET[y,m])؛ ≥سنتين؛ PET لكل سنة بأيام التقويم الفعلية.','max(PET[y,m])-min(PET[y,m]); ≥2 years; per-year PET uses actual calendar days.')
        return text('max_y X[y,m]-min_y X[y,m] بعد تحويل وحدة المدخل؛ ≥سنتين لنفس الشهر.','max_y X[y,m]-min_y X[y,m] after input-unit transformation; ≥2 years for that month.')
    if field.startswith('W_Dir_'):return text('متوسط دائري للاتجاهات الشهرية الصالحة التابعة للفترة؛ أوزان متساوية.','Circular mean of valid monthly directions in the indicated period; equal weights.')
    if field.endswith('_Annual_Range'):
        return text('أعلى قيمة شهرية مناخية ناقص أدناها؛ HI يستخدم Rothfusz، وET يستخدم PET الشهري.','Maximum minus minimum climatological month; HI uses Rothfusz and ET uses monthly PET.')
    if field.startswith('ET_') and field.endswith('_Mean'):
        return text('قيمة PET للشهر، أو مجموع PET للشهور التابعة للفصل/السنة؛ تقريب منزلة واحدة.','Monthly PET or summed PET for the indicated season/year; rounded to one decimal.')
    if field.startswith('R_') and field.endswith('_Mean'):
        return text('متوسط مجموع المطر لنفس الشهر عبر السنوات.' if month else 'متوسط مجاميع المطر للسنوات/الفصول المكتملة فقط.','Mean rainfall total for that calendar month across years.' if month else 'Mean rainfall totals of complete years/seasons only.')
    if field.endswith('_Mean') and field.startswith(('T_','LST_','PSL_','PS_','W_Spd_','RH_','Td_','Sol_','UV_','Cld_','HI_','WC_')):
        return text('متوسط شهر التقويم عبر السنوات، أو متوسط الشهور المناخية التابعة للفترة؛ HI/WC بعد تطبيق معادلتهما الشهرية.','Calendar-month mean across years, or mean climatological months in the indicated period; HI/WC follow monthly index evaluation.')
    raise ValueError('Unmapped scientific output '+module+': '+field)


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
    parts.append('<table><tr><th>'+('العمود الفعلي' if arabic else 'Actual field')+'</th><th>'+('طريقة حسابه' if arabic else 'Calculation')+'</th></tr>')
    for field in calculation_fields(module):parts.append('<tr><td dir="ltr"><code>'+html.escape(field)+'</code></td><td>'+html.escape(field_rule(module,field,arabic))+'</td></tr>')
    parts.append('</table>'+heading('مرجع التنفيذ','Implementation reference'))
    parts.append('<p dir="ltr">MIRSAD_Climate_Atlas_Generator_10_8.pyt → '+html.escape(', '.join(item['functions']))+'<br>MIRSAD Desktop/src/mirsad_desktop/science.py</p>')
    parts.append('<p>'+('المعادلات من النواة المشتركة. تجهيز البيانات، حراس التغطية، ترشيح الحقول والوحدات النهائية قد تختلف بين الواجهتين؛ لا تعني مشاركة النواة تطابق جميع ملفات الإخراج.' if arabic else 'Equations come from the shared kernel. Input preparation, coverage guards, field filtering and final units can differ between hosts; a common kernel does not establish identical output files.')+'</p>')
    return ''.join(parts)
