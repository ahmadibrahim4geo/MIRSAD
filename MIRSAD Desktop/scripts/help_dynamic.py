"""Generated-table builders; source prose lives in Documents/Help."""
import html,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.registry import MODULES


def supplementary_body(language):
    from mirsad_desktop.daily_climate import VARIABLES
    from mirsad_desktop.enrichment import DESCRIPTIONS
    arabic=language=="ar"
    parts=['<h3>'+('إضافات Desktop الاختيارية — 21 أكتوبر 2026' if arabic else 'Optional Desktop additions — 21 October 2026')+'</h3>']
    parts.append('<p>'+('توجد المتغيرات أسفل عناصرها الحالية؛ جميعها مغلقة افتراضيًا. قبول Toolbox والمرشح المجمع يسجل منفصلًا عن تكامل مصدر Desktop. تبقى الحسابات والحقول القديمة دون تغيير. اقرأ Field_Dictionary لكل اسم وفترة ووحدة وطريقة، وHourly_Processing للعملية وعدد العينات ومصدر اليوم المشتق. يلزم 24 ساعة UTC صحيحة وفريدة؛ اليوم الناقص يبقى NULL. توفر ملخص يومي لدى المزود لا يجعل البديل الساعي غير صالح؛ هذا المسار يستخدم الساعي الموثق.' if arabic else
        'Variables are nested under existing modules and off by default. Toolbox parity and packaged candidate acceptance are recorded separately from Desktop source integration. Legacy fields/calculations are preserved. Field_Dictionary describes each name, period, unit and method; Hourly_Processing records aggregation, sample counts and sources. A derived day requires 24 valid unique UTC hours; incomplete days remain NULL. Provider daily summaries can also exist; this implemented path uses documented hourly inputs.')+'</p>')
    parts.append('<table><tr>'+''.join('<th>'+label+'</th>' for label in (('المتغير','المعنى','الوحدة','الطريقة') if arabic else ('Variable','Meaning','Unit','Method')))+'</tr>')
    for name,spec in VARIABLES.items():
        description=DESCRIPTIONS[name]
        parts.append('<tr>'+''.join('<td>'+html.escape(value)+'</td>' for value in (name,description[1 if arabic else 0],spec['unit'],description[2]))+'</tr>')
    parts.append('</table><p>'+('الملخصات الجديدة تشترط شهورًا مكتملة. المتوسط السنوي/الموسمي يزن الأيام داخل كل سنة ثم يوسّط السنوات المكتملة؛ Winter يجمع ديسمبر ويناير وفبراير من السنة التقويمية نفسها. Annual_Range فرق أكبر وأصغر متوسط شهري مناخي؛ Month_Range فرق نفس الشهر بين سنوات. الوحدات الجديدة أعلاه ثابتة SI ولو اختيرت وحدات مختلفة للحقول القديمة.' if arabic else
        'New summaries require complete months. Annual/seasonal means weight days within each year, then average complete years; Winter uses December/January/February of the same calendar year. Annual_Range compares climatic monthly means; Month_Range compares the same month across years. The component units above remain canonical SI even when legacy summary units differ.')+'</p>')
    parts.append('<h3>Hargreaves / Penman–Monteith</h3><p>'+('تختار HG أو PM أو كليهما داخل البخر والنتح؛ HG هو الافتراضي. PM حساب FAO56 يومي مستقل: T=(Tmax+Tmin)/2، G=0 وalbedo=0.23. يحتاج ارتفاعًا معلومًا لصافي الإشعاع، ورياحًا بارتفاع قياس مؤكد؛ لا يُفترض سطح البحر أو ارتفاع جهاز NOAA من اسم WS10M. ضغط السطح مقدم على تقديره من الارتفاع. ea من الندى الصالح وإلا العظمى/الصغرى للرطوبة. لا يدخل PM في مؤشرات UNEP والعجز القديمة بدل HG. تجمع قيم PM اليومية للشهر/الموسم/السنة ثم يؤخذ المتوسط المناخي؛ يتبع PM وحدة الأمطار المختارة، واليومي يوضح mm/day أو inches/day. لكل طريقة طبقة ومصنف ومجلد راستر مستقل، واختيار الراستر منفصل عن الحساب. لا يحل VPD_Source اليومي الأقصى محل VPD_FAO56=es-ea.' if arabic else
        'Select HG, PM or both under Evapotranspiration; HG is the default. PM is an independent daily FAO56 calculation: T=(Tmax+Tmin)/2, G=0, albedo=0.23. It requires known elevation for net radiation and confirmed wind measurement height; no sea-level or NOAA WS10M height inference. Surface pressure takes priority over estimation from elevation. ea uses valid dewpoint, otherwise RH extrema. PM does not replace HG in legacy UNEP/water-deficit indices. Daily PM is summed for each complete month/season/year before climatic averaging. PM follows precipitation output units, with mm/day or inches/day in Daily. Methods have separate layers, workbooks and raster folders; raster selection is independent. Source maximum VPD never substitutes for VPD_FAO56=es-ea.')+'</p>')
    parts.append('<h3>'+('الارتفاع الاختياري وExcel الكبير' if arabic else 'Optional elevation and large Excel')+'</h3><p>'+('خيار المخرجات يضيف Z_Elev_m وZ_Source لكل طبقة نقاط ويحفظ المنسوب الأصلي والهندسة. يتاح GeoTIFF محلي بالمتر مع CRS معروف وتحديد DTM/DSM والمرجع الرأسي، أو Copernicus GLO-90 عبر Open-Meteo: DSM اسمي 90 مترًا وليس أرضًا عارية. استخدم DTM مناسبًا محليًا لاستبعاد أثر النباتات والعمران. Elevation_Source يوثق النموذج والمرجع والعينة وفشل القراءة؛ الصفر صالح والمفقود NULL. لا توحيد رأسي صامت ولا تنزيل ارتفاع خفي عند اختيار PM. أداة الشبكات لا تنشئ نقاطًا لأجل هذا الخيار.' if arabic else
        'The output option adds Z_Elev_m and Z_Source to point layers while preserving original elevation/geometry. Choose a local metre GeoTIFF with known CRS, DTM/DSM and vertical reference, or Copernicus GLO-90 through Open-Meteo: a nominal 90 m DSM. A suitable local DTM can exclude vegetation/buildings. Elevation_Source records product, datum, sampling and failures; zero is valid, missing is NULL. No silent vertical normalization or hidden DEM download for PM. The regional grid tool does not manufacture points for this option.')+'</p>')
    parts.append('<p>'+('يكتب Desktop ملفات XLSX فقط لهذا المسار: مليون صف بيانات لكل ورقة Daily وأربعة ملايين لكل ملف، ثم Daily_2 وملفات Part_002 وفهرس Export_Index. تتكرر البيانات الوصفية في الأجزاء وتحفظ الملفات الناجحة عند إخفاق لاحق. الصفوف اليومية تُخزن مؤقتًا على القرص؛ قبول مليون وصف لا يثبت بعد أداء تنزيل ألف نقطة لثلاثين سنة. Daily الكبير فوق 60 ألف صف في Toolbox النقطي/المحطات يستخدم XLSX قياسيًا على Python 2.7/3؛ ملفات XLS الصغيرة القديمة تحتفظ بعقدها. أداتا Point وStation تضيفان المتغيرات الـ11 في المسار اليومي للمصادر العامة المدعومة، عبر معاملات Supplementary_* مغلقة افتراضيًا. تحفظ المدخلات الإضافية منفصلة في Source Data/Supplementary_Inputs ولا تغير السلاسل القديمة. المصنف المتأثر يصبح XLSX ويضيف Supplementary_Daily عند الطلب وقاموسًا ومنهجية وتدقيق الساعات. استيفاء الإضافات خيار مستقل؛ أعداد أيام التغطية جدولية فقط. PM متاح أيضًا في Point وStation للمصادر العامة اليومية المدعومة، باختيار HG/PM مستقلين وراستر مستقل ومجلدَي Hargreaves وPenman_Monteith عند اختيار PM؛ HG وحده يحتفظ بمساره القديم. إثراء DEM في Toolbox والمسار الإقليمي والتعريب الاختياري في Desktop وArcMap الأصلي وDPI الشامل ما زالت أعمالًا متبقية. اختبار كل مرشح ومثبته موثق منفصلًا ولا يعني تثبيت نسخة المستخدم أو إصدارًا نهائيًا.' if arabic else
        'This Desktop path writes XLSX: one million data rows per Daily sheet and four million per file, then Daily_2, Part_002 files and Export_Index. Metadata repeats in parts; completed files survive later failures. Daily rows spool to disk. The million-row acceptance does not establish a 1000-point/30-year download benchmark. Legacy point/station Daily tables above 60,000 rows use standard-library XLSX on Python 2.7/3; small XLS retains its contract. Point/Station tools integrate the 11 variables for supported public daily point sources using default-off Supplementary_* parameters. Separate inputs under Source Data/Supplementary_Inputs preserve legacy series. Affected workbooks use XLSX, with optional Supplementary_Daily, field definitions, methodology and hourly audit. Supplementary interpolation is independently selected; coverage counts remain tabular. Daily PM is also integrated in Point/Station for supported public sources, with independent HG/PM calculation/raster selections and Hargreaves/Penman_Monteith folders when PM is selected; HG-only retains its legacy path. Toolbox DEM, regional additions, Desktop localized aliases, native ArcMap and full DPI remain outstanding. Each frozen candidate and installer has separate evidence; checks do not install the user app or establish a final release.')+'</p>')
    parts.append('<p><a href="https://www.fao.org/4/X0490E/x0490e00.htm">FAO-56</a> · <a href="https://open-meteo.com/en/docs/historical-weather-api">Open-Meteo</a> · <a href="https://open-meteo.com/en/docs/elevation-api">Elevation API</a></p>')
    return ''.join(parts)

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
