"""Generated-table builders; source prose lives in Documents/Help."""
import html,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.registry import MODULES

def parameter_body(key,language):
    import hashlib
    source=ROOT.parent/'Documents/Help'
    snapshot=json.loads((source/'tool_parameters.json').read_text(encoding='utf-8'))
    for filename,digest in snapshot['source_sha256'].items():
        content=(ROOT.parent/filename).read_text(encoding='utf-8-sig').encode('utf-8') if snapshot.get('source_hash_policy')=='normalized-utf8-lf-v1' else (ROOT.parent/filename).read_bytes()
        if hashlib.sha256(content).hexdigest()!=digest:
            raise ValueError('Parameter help snapshot is stale: '+filename+'; refresh scripts/export_help_parameters.py with Pro')
    notes=json.loads((source/'parameter_notes_ar.json').read_text(encoding='utf-8'))
    tool=next(tool for tool in snapshot['tools'] if tool['id']==key);arabic=language=='ar'
    intro=('هذا مرجع معاملات أداة ArcGIS، وليس قائمة أوامر Desktop. القيم المعروضة لقطة التعريف الافتراضي من Pro 3.6؛ تغيرها الواجهة حسب المصدر والنمط والعناصر. خانة Required تخص التعريف، وقد تختلف الإلزامية الفعلية في Offline أو عند تعطيل خيار تابع. المصادر الشهرية تعطل Daily. حساب CDS/IMERG الفعلي وتوافق ArcMap الأصلي ما زالا ضمن حدود التحقق المعلنة.' if arabic else
        'This references the ArcGIS tool, not an identical Desktop command list. Values are a Pro 3.6 default-definition snapshot; controls change with provider, mode and modules. Required describes the declaration; runtime requirements can differ in Offline or disabled dependent controls. Monthly products disable Daily. Authenticated CDS/IMERG and native ArcMap verification limits remain explicit.')
    parts=['<p>'+intro+'</p><p>'+html.escape(tool['file'])+' · '+str(len(tool['parameters']))+(' معاملًا' if arabic else ' parameters')+'</p>']
    overrides={
        'OpenMeteo_Model':'Auto chooses the finest suitable product per variable and whole interval within the selected source; manual profiles fix a model. Actual product resolution is retained in provenance.',
        'Climate_Data_Source':'The selected provider controls actual requests and supported variables. See Sources for coverage, sign-in and standalone versus Hybrid policy.',
        'Temporal_Resolution':'Daily preserves actual daily observations where supported. Native monthly/composite products force Monthly and disable Daily export; this does not implement every daily extreme index.',
        'Earthdata_Username':'Legacy regional compatibility field; this does not enable regional Earthdata/IMERG. Implemented regional products are NASA POWER, CHIRPS and CHELSA.',
        'Earthdata_Password':'Legacy regional compatibility field; the implemented IMERG point/station adapter uses its own masked credentials controls.',
        'Output_Workspace':'Writable project output directory, with the dated climate database, element folders, tables and reports. Keep user projects outside the application installation.',
        'Generate_Monthly_Rasters':'Request monthly climatology surfaces when the current multi-year interval requirement is satisfied. This never synthesizes daily observations.'}
    for parameter in tool['parameters']:
        name=parameter['name']
        if name not in notes:raise ValueError('Missing Arabic parameter explanation: '+name)
        description=notes[name] if arabic else overrides.get(name,parameter['description'] or 'Optional export control; see the tool workflow and Output section.')
        label=parameter[language]
        parts+=['<h3>'+html.escape(label)+' <span dir="ltr">('+html.escape(name)+')</span></h3>', '<p>'+html.escape(description).replace('\n','<br>')+'</p>']
        fields=[('النوع' if arabic else 'Type',parameter['datatype']),('الإلزامية في التعريف' if arabic else 'Declared requirement',parameter['required']),
            ('الاتجاه' if arabic else 'Direction',parameter['direction']),('المجموعة' if arabic else 'Category',parameter['category']),
            ('الافتراضي في اللقطة' if arabic else 'Snapshot default',('مخفي / غير محفوظ' if arabic else 'Masked / not retained') if parameter['sensitive'] else parameter['default'])]
        parts.append('<table>'+''.join('<tr><th>'+label+'</th><td dir="auto">'+html.escape(str(value) if value is not None else '—')+'</td></tr>' for label,value in fields)+'</table>')
        if parameter['choices']:
            parts.append('<p><b>'+('الخيارات الأولية:' if arabic else 'Initial choices:')+'</b> '+html.escape(' | '.join(map(str,parameter['choices'])))+'</p>')
    return ''.join(parts)

def provider_body(language):
    catalogue=json.loads((ROOT/"assets/climate_sources.json").read_text(encoding="utf-8"))
    introduction={
        "ar":"<p><b>الافتراضي Auto:</b> أدق منتج مناسب لكل متغير داخل المصدر المختار وللفترة كاملة. الحرارة والرطوبة والندى من ERA5-Land عند توفره، وبقية متغيرات Open-Meteo من ERA5. إذا بدأت الفترة قبل 1950 يستخدم ERA5 طوالها. «إعدادات متقدمة» تتيح اختيار نموذج يدوي ثابت؛ لا تُخترع درجات دقة للمصدر ذي الشبكة الثابتة. ملخص الواجهة يوضح الخطة، وSource_Resolution وملفات البيانات الخام تسجل المنتج المستخدم فعليًا. تصغير بكسل الإخراج لا يزيد دقة المصدر.</p><p><b>Need Sign In:</b> CDS يحتاج رمز API شخصيًا وقبول شروط المنتج، وIMERG يحتاج اسم مستخدم وكلمة مرور NASA Earthdata مع إجازة GES DISC. أدخل بياناتك في الخانات أسفل إعدادات المناخ؛ لا تدخل حساب المطور. تظل البيانات في الذاكرة وتُنقل إلى العامل عبر قناة stdin؛ لا تحفظ في المشروع أو ملفات المهمة أو السجلات. المساران منفذان واختبرت تحويلاتهما؛ لم يُثبت التنزيل بحساب فعلي بعد.</p><p><b>المحطات:</b> NOAA GSOD يحتاج USAF وWBAN والموقع. GHCN يحتاج GHCN_ID صريحًا في طبقة المحطات/النقاط الداعمة المستوردة؛ لا يُستبدل المعرف ولا أقرب محطة آليًا. المصادر الشبكية تعمل عند نقاط عادية وعند مواقع المحطات دون أن تصبح أرصاد محطة.</p>",
        "en":"<p><b>Auto is the default:</b> choose the finest suitable product per variable within the selected provider and for the whole requested interval. Supported temperature, RH and dewpoint use ERA5-Land; other supported Open-Meteo variables use ERA5. Intervals beginning before 1950 use ERA5 throughout. Advanced settings allow a fixed manual model. Fixed-grid providers do not acquire fictional resolution choices. The UI previews the plan; Source_Resolution and raw records report the actual product. Smaller output pixels do not add source detail.</p><p><b>Need Sign In:</b> CDS requires a personal API token and accepted dataset terms. IMERG requires NASA Earthdata username/password and GES DISC authorization. Enter your own credentials below the climate settings. Credentials stay in memory and pass to workers via stdin; they are absent from project, job and log files. Both adapters and conversion/protocol tests are implemented; live authenticated end-to-end access remains unverified.</p><p><b>Stations:</b> NOAA GSOD requires USAF/WBAN/location. GHCN requires explicit GHCN_ID in an imported supporting station/point layer. No automatic identifier or nearest-station substitution is made. Gridded sources work at arbitrary points and station locations without becoming station observations.</p>"
    }
    parts=[introduction[language]]
    for item in catalogue["sources"]:
        parts.append('<h3>'+html.escape(item['label'])+'</h3><p>'+html.escape(item['start']+' → '+item['end'])+'<br>'+html.escape(item['resolution']+' | '+item['temporal'])+'<br>'+html.escape(item['region']+' | '+', '.join(item['tools']))+'</p><p><b>Variables:</b> '+html.escape(', '.join(item['variables']))+'</p><p>'+html.escape(item['notes_'+language])+'</p><p><a href="'+html.escape(item['url'])+'">Official source</a></p>')
    return ''.join(parts)

DETAILS={
"Temperature":("متوسط الحرارة ومتوسط العظمى والصغرى والمدى الحراري.","Mean temperature, mean daily maxima/minima and temperature range."),
"Land Surface Temperature":("حرارة سطح الأرض/الجلد والفرق عن حرارة الهواء؛ ليست حرارة هواء إضافية.","Skin/surface temperature and its difference from air temperature."),
"Precipitation":("مجاميع مطر للشهور المكتملة وملخصاتها؛ المفقود ليس صفرًا.","Complete-month rainfall totals and summaries; missing is not zero."),
"Sea Level Pressure":("ضغط مختزل إلى سطح البحر.","Pressure reduced to sea level."),
"Surface Pressure":("ضغط عند السطح؛ يختلف عن الضغط البحري.","Surface pressure, distinct from sea-level pressure."),
"Wind":("سرعة الرياح عند 10 م واتجاه بمتوسط دائري.","10 m wind speed and circular-mean direction."),
"Relative Humidity":("الرطوبة النسبية كنسبة مئوية.","Relative humidity as percent."),
"Dew Point":("درجة حرارة نقطة الندى.","Dew-point temperature."),
"Solar Radiation":("طاقة إشعاع يومية متوسطة وملخصات تراكمية.","Mean daily solar energy and accumulated summaries."),
"UV Index":("مؤشر UV مع تقريب الظهر الموروث لبيانات NASA.","UV index using the inherited NASA noon approximation."),
"Cloud Cover":("متوسط نسبة الغطاء السحابي.","Mean cloud-cover fraction in percent."),
"Heat Index":("تقديرات الإجهاد الحراري من الحرارة والرطوبة؛ نواتج WBGT تقريبية وليست قياس جهاز.","Heat/humidity stress estimates; WBGT outputs are approximations, not instrument observations."),
"Wind Chill":("تقدير برودة الرياح من الحرارة وسرعتها؛ يتبع مجال تطبيق الصيغة.","Wind-chill estimate from air temperature and speed within the formula's domain."),
"De Martonne Aridity":("مؤشر دي مارتون السنوي P/(T+10)، باعتماد مطر وحرارة صالحين.","Annual De Martonne P/(T+10), requiring valid precipitation and temperature."),
"Evapotranspiration":("PET بطريقة Hargreaves اعتمادًا على الحرارة والعظمى والصغرى ودائرة العرض.","Hargreaves PET using mean/max/min temperature and latitude."),
"UNEP Aridity":("نسبة P/PET؛ يتطلب مطرًا وPET صالحين.","P/PET ratio, requiring valid precipitation and PET."),
"Water Deficit":("العجز المائي وفق حسابات المطر وPET في المحرك.","Water deficit from the kernel's precipitation/PET calculations."),
"Dry Months":("عدد الأشهر الجافة بحسب مقارنة المطر والحرارة P&lt;2T.","Dry-month count using the precipitation/temperature P&lt;2T criterion."),
"Trends & Anomalies":("اتجاهات الحرارة والمطر وشذوذ خط الأساس عند كفاية التاريخ.","Temperature/rainfall trends and baseline anomalies when history is sufficient."),
}

def module_table(arabic):
    rows=['<table><tr><th>'+('العنصر' if arabic else 'Module')+'</th><th>'+('ما ينتجه' if arabic else 'Meaning')+'</th><th>'+('الاعتماديات والوحدة المعتادة' if arabic else 'Dependencies / usual unit')+'</th></tr>']
    for module in MODULES:
        title=(module.arabic+'<br>'+html.escape(module.name)) if arabic else html.escape(module.name)
        rows.append('<tr><td>'+title+'</td><td>'+DETAILS[module.name][0 if arabic else 1]+'</td><td dir="ltr">'+', '.join(module.params)+'<br>'+html.escape(module.unit)+'</td></tr>')
    return ''.join(rows)+'</table>'
