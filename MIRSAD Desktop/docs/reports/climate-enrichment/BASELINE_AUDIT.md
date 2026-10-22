# تدقيق بداية توسعة المتغيرات والمناسيب وطرق البخر والنتح

التاريخ: 19 أكتوبر 2026. مرجع المصدر: `09bb7fd043d6e8a9984e8f27f36c2815dbe4e0f2`.

**الحالة عند التقاط التدقيق، 19 أكتوبر: أُنجز تدقيق البداية وحماية العقود؛ لم تكن المتغيرات الجديدة أو PM أو DEM في الواجهة بعد.**
حالة التنفيذ اللاحقة في [قبول مصدر Desktop، 21 أكتوبر](DESKTOP_SOURCE_ACCEPTANCE.md).
هذه الوثيقة تسجل المرحلة A من خطة المستخدم، مع توضيحاته اللاحقة عن نماذج الارتفاعات
واشتقاق اليومي من الساعي. لا تمثل قبولًا كاملًا للخطة أو حزمة تنفيذ جديدة.

## الأدلة القابلة لإعادة التشغيل

- [أداة الالتقاط والمقارنة](../../../../scripts/audit_climate_enrichment.py): تقرأ المحركين
  دون ArcGIS أو شبكة؛ الالتقاط صريح ويرفض استبدال المرجع الموجود.
- [مرجع العقود](../../../../tests/fixtures/climate_enrichment_baseline.json): نتائج الحزم الـ19
  على مدخلات ثابتة، بأسماء وترتيب الحقول والقيم والمسارات وأوراق Excel وملخصات Daily.
- [اختبارات حماية المرجع](../../../../tests/test_climate_enrichment_baseline.py).
- [مصفوفة القدرات الحالية](CAPABILITY_MATRIX.json): 1,100 صف، لكل منها المتغير والمصدر والمنتج
  والدقة الزمنية والنطاق والفترة وطريقة الإخراج وحالة المحوّل البرمجي. الأسماء الجديدة
  الواردة في المصفوفة مفاتيح مرشحة، وليست متغيرات مفعلة.
- [فحوص الخدمة](SERVICE_PROBES.json) و[أداة تكرار الطلبات](../../../../scripts/probe_climate_enrichment.py).
- [قرارات التنفيذ](SCIENTIFIC_CONTRACTS.md) و[تتبّع مراحل القبول](IMPLEMENTATION_TRACKER.md).

بصمة JSON المعياري لمحتوى العقود:
`dece9806589307319b26328a1ac37c628758c8960f0c7ed5314df57d81f46704`.
المرجع يحمي السلوك الحالي؛ صحة المنهج العلمي تُثبت أيضًا بأمثلة مستقلة، لا بلقطات الانحدار وحدها.

## حماية بيانات المستخدم وحالة Git

توجد تعديلات وحذوفات سابقة في Sample Data وقواعد بيانات مصر، وحذف لخريطة المحطات،
وتعديلات وملفات XML مولدة بواسطة ArcGIS. ملف الخطة نفسه غير متعقب في بداية التدقيق.
لم تُرجع هذه الملفات، ولم تُعدّل بيانات المحطات، ولم تُضف ملفات المستخدم إلى staging.
لم يُنشأ commit أو نشر أو بناء أو تثبيت أو تعديل على stable.

## جرد الموجود والناقص

| النطاق | موجود فعليًا | ناقص أو يحتاج قبولًا |
|---|---|---|
| الأدوات | ثلاثة صناديق، لكل منها EN/AR؛ Desktop له مسارات محطات ونقاط وراستر مستقلة | لا يلزم Collector أو صندوق رابع |
| سجل العناصر | `MODULE_PARAMS`, `MODULE_FIELDS`, `FIELD_DEFS/FIELD_BY_NAME`, `MODULE_FOLDER` في صندوق النقاط؛ `registry.py` في Desktop | اختيارات المتغيرات الإضافية واعتمادياتها داخل العناصر الحالية |
| الحسابات | 38 دالة علمية منقولة وقت البناء إلى `science.py`، دون ArcGIS وقت التشغيل | دوال اليومية الجديدة وPM والتحقق المستقل منها |
| المصادر | NOAA GSOD وPOWER وOpen-Meteo، ومنتجات `climate_products.py` وفق قدراتها | ربط RHmax/RHmin وn وVPD المصدرية والمتغيرات المشتقة بالمحولات والمخرجات |
| الهجين | مراحل NOAA ثم ERA5 ثم POWER على مستوى الشبكة؛ استكمال شهري اختياري بعد التنزيل | إضافة المتغيرات إلى القدرات دون تغيير ترتيب المراحل أو القيم الأعلى أولوية |
| اليومية | الساعي الحالي يُجمّع على أيام UTC؛ المحرك المشترك يشترط 24 طابعًا زمنيًا صالحًا | تسجيل نوع التجميع وعدد الساعات والاكتمال في سجل القيم والمخرجات؛ تشديد فحص مواقع الساعات لا عددها فقط |
| الرطوبة | RHmean وDew Point قائمين؛ لا أسماء نهائية أو حقول مفعلة للامتدادات الجديدة | RHmax/RHmin وea/es ونسختا VPD وإحصاءاتها |
| الحرارة والإشعاع | Tmax/Tmin/Tmean وRs؛ Ra مستخدم داخليًا في HG | Trange اليومي المستقل، Ra اليومي المصدر، n، ونوعا Rn |
| الرياح والضغط | قياسات المصدر والتحويلات القائمة؛ PS بوحدة kPa داخل المحرك | U2 موثق الارتفاع؛ لا يجوز اعتبار اسم المفتاح WS10M إثباتًا لارتفاع قياس NOAA |
| ET | HG قائم ضمن Evapotranspiration، وحقول `ET_*` و`PET_Hargreaves_Annual` | PM يومي، اختيار طرق متعدد، وفصل ملفات وطبقات وراستر الطريقتين |
| المناسيب | منسوب الكتالوج/المدخل محفوظ كحقل موقع | لا توجد وحدة DEM مشتركة ولا `Z_Elev_m`/`Z_Source` اختياريان بعد |
| Excel | XLS في القديم؛ XLSX في Desktop؛ تقسيم أوراق موجود بالفعل في الاثنين | streaming كامل، تقسيم مصنفات مع فهرس، ومزامنة القواميس والطرق لكل العناصر |
| GIS | FileGDB/GPKG وقراءة رجعية حقيقية في Desktop | تكافؤ الخيارات المتقدمة والبيانات الوصفية مفتوح قبل هذه الدفعة |
| التعريب | Toolbox يحتفظ بالاسم/alias الإنجليزي وينشئ `_AR.gdb` اختياريًا | Desktop لا ينفذ مسار تعريب aliases مكافئًا؛ لا نفترض وجوده لمجرد توفر واجهة عربية |
| الراستر الإقليمي | POWER الشهري ومسارا CHIRPS/CHELSA الأصليان بحسب الكود | كل متغير إضافي يحتاج مسارًا إقليميًا مثبتًا؛ قائمة مصادر النقاط ليست قائمة مصادر الراستر |

## خريطة الكود والعقود

المسارات التالية محسوبة من جذر المستودع:

| المسؤولية | موضع القراءة/الكتابة |
|---|---|
| سجل الحقول والتبعيات | `Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt`: `MODULE_PARAMS`, `MODULE_FIELDS`, `FIELD_DEFS`, `FIELD_BY_NAME`, `FIELD_ALIAS_AR`, `MODULE_FOLDER`, `SHP_FIELD_MAP` |
| معاملات التنفيذ | `PowerClimateAtlasGenerator.getParameterInfo/updateParameters/execute`؛ صندوق المحطات يرث منه ويحوّل معاملات المحطات عبر `_ParamProxy` |
| سياسة المصدر/Auto | `mirsad_core/climate_sources.py`: `pipeline_sources`, `reanalysis_plan`, `variable_resolution` |
| التنزيل الهجين | `mirsad_core/hybrid_pipeline.py`: `OM_DAILY`, `OM_HOURLY`, `NOAA_FIELDS`, `fetch_source`, `run` |
| تجميع المصدر | `hybrid_pipeline.monthly/prepare_monthly`؛ وفي المسار القديم `build_monthly_from_daily`؛ الفروق لا تُوحّد صامتًا |
| نتائج Desktop | `climate.prepare_outputs`, `registry.parameters/module_fields`, `services.run_climate_project` |
| Excel القديم | `write_excel_file`, `write_master_excel_workbook`, `export_excel_with_fallback`, `_export_excel`, `_export_yearly_excel` |
| Excel/GIS Desktop | `exports.station_properties/write_layer/element_sheets/workbook/export_project` |
| أسماء وaliases GIS | مواقع `AddField(... field_alias=name)` في صندوق النقاط؛ `_build_arabic_db` يترجم alias في النسخة الاختيارية فقط |
| راستر النقاط | مسار Toolbox القائم؛ Desktop `analysis.build_atlas`، بمرشحات الحقول والفترات |
| الراستر الإقليمي | `Toolboxes/raster_atlas_generator.py` وDesktop `regional.py`؛ المنتجات الأصلية في `climate_products.REGIONAL` |
| التضمين | `MIRSAD Desktop/scripts/vendor_science.py`؛ ينسخ المحولات المشتركة ويستخرج الدوال العلمية وقت التطوير |
| التوثيق | `Documents/Help/`، مولدات Desktop تحت `scripts/`، والموقع من `scripts/build_website.py` وقوالبه |

قراءة معاملات Pro السابقة تسجل 69/76/36؛ لم تُعدّل معاملات الأدوات هنا ولم يُعَد ادعاء قبول
native بناءً على هذه الأعداد. التقارير الحالية والـBacklog يحددان حدود التكافؤ القديمة.

## تتبّع استخدام الارتفاع الحالي

أُجري بحث في الأصناف الثلاثة والمحرك المشترك وجميع ملفات `src/mirsad_desktop` عن
`elev`, `Elev`, `altitude` ومواضع الحساب ذات الصلة. النتيجة تخص الكود الموجود، ولا تثبت
المرجع الرأسي أو صحة الارتفاعات في الطبيعة.

| الحقل | القراءة | الكتابة | موضع الحساب/الأثر |
|---|---|---|---|
| `Elev_m` في الكتالوج | `mirsad_core/station_catalogue.py` وقراءة محطات Toolbox | الطبقة المؤقتة في صندوق المحطات وmetadata | لا تمرره دوال HG الحالية كمدخل حساب |
| `Elev_m` أو `Elev_Meters` وأسماء بديلة | `_extract_points` بصندوق النقاط | `p_info['elevation']` ثم Excel/metadata، وإعادة إضافة خصائص المحطات لطبقات النتيجة | بعض المسارات القديمة تستعمل صفرًا افتراضيًا؛ لا يُقبل إثباتًا لمنسوب معلوم لنقطة إضافية في PM |
| `elevation` في Desktop | `inputs.make_point` أو كتالوج المحطات | `exports.station_properties` إلى `Elevation_m` | موجود وصفيًا؛ مستبعد من الاختيار التلقائي لحقول الراستر في `analysis.build_atlas` |
| `Elevation_m` في Grid Raster | كتابة بيانات نقطة/خلية المصدر | تقارير المصادر/Excel | لا يوجد إثراء DEM مشترك في هذا المسار |
| `Z_Elev_m`, `Z_Source` | غير موجودين | غير موجودين | إضافة اختيارية مستقبلية؛ لا إعادة تعريف للحقل الأصلي أو هندسة النقطة |

HG الحالي يعتمد الحرارة وخط العرض والتوقيت، ولا يقرأ منسوب المحطة مباشرة في الدوال التي
جرى تتبّعها. أي استخدام جديد لـZ في PM/الضغط/Rso سيحمل مصدر مدخل صريحًا منفصلًا عن
خيار إثراء طبقات النتائج.

## تفاصيل Excel التي تؤثر على ترتيب التنفيذ

- `export_excel_with_fallback` يقسم الجداول إلى أوراق 60,000 صف بيانات، ثم يكتب XLS عبر
  xlwt. عند تعذر الكتابة له fallback قديم إلى CSV؛ يبقى عقدًا قديمًا موثقًا خارج ميزة التقسيم الجديدة.
- Desktop يقسم الجداول إلى أوراق 1,000,000 صف بيانات في XLSX، لكنه يستعمل
  `Workbook(write_only=False)`؛ كما يجمع Daily في قوائم داخل `prepare_outputs`.
- تحسين الكاتب وحده لا يحل ذاكرة ملايين السجلات؛ يجب معالجة إنشاء الصفوف والتصدير على دفعات.
- Data وMonth وSource_Data موجودة بحسب العنصر؛ Daily عند اختيار حفظها. بيانات يومية
  طويلة في Desktop تختلف عن بعض الجداول العريضة القديمة. لا ندعي التكافؤ الكامل الموجود أصلًا.
- سقف الورقة شامل العناوين: XLSX = 1,048,576؛ XLS = 65,536. حدود التقسيم العملية يجب
  أن تكون أقل أو مساوية للحد التقني، مع فهرس أجزاء وعدم إسقاط/تكرار سجلات.

## فحوص المصدر الفعلية

العينة: `30N, 31E`، من 28 فبراير إلى 1 مارس 2024، UTC. هذه حالة اختبار صريحة؛
لا تغيّر البلد أو الموقع الافتراضي للتطبيق.

| المنتج/الطلب | النتيجة |
|---|---|
| ERA5-Land: `relative_humidity_2m_max` يومي وساعي RH | HTTP 200؛ 96،91،42%؛ مطابق لأقصى 24 ساعة في الأيام الثلاثة |
| ERA5-Land: `relative_humidity_2m_min` يومي وساعي RH | HTTP 200؛ 26،14،15%؛ مطابق لأدنى 24 ساعة في الأيام الثلاثة |
| ERA5: `sunshine_duration` | HTTP 200؛ 39646.6،39923.7،40199.44 ثانية؛ تحتاج تحويلًا إلى ساعات |
| ERA5: `vapour_pressure_deficit_max` يومي وساعي VPD | HTTP 200؛ 1.82،2.91،3.21 kPa؛ مطابق لأقصى القيم الساعية |

فشل الاتصال الأول داخل الشبكة المقيدة بسبب DNS؛ نجح تكرار نفس الفحوص في مسار الشبكة
المسموح. لا تُعد هذه العينة قبولًا عالميًا لكل موقع وفترة ومنتج، ولا يعني نجاح الخدمة
أن محول MIRSAD الحالي قد أُضيف له المتغير بالفعل.

المراجع: [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api)،
[FAO-56 بيانات الأرصاد](https://www.fao.org/4/X0490E/x0490e07.htm)،
[FAO-56 المعادلة المرجعية](https://www.fao.org/4/X0490E/x0490e06.htm)،
[Copernicus DEM](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM).

## نتائج الاختبارات

| الفحص | النتيجة الفعلية في هذه الدفعة | الحدود |
|---|---|---|
| Legacy قبل التعديل | 17 مجموعة / 146 اختبارًا ناجحة | اختبارات معزولة؛ ليست تشغيل ArcGIS أصليًا |
| Desktop قبل التعديل | 63 اختبارًا ناجحة، 144.067 ثانية | تشمل GIS/Excel حقيقيين وUI/jobs، وليست قبول binary جديد |
| Python 2.7 | 7 مجموعات / 76 اختبارًا ناجحة | المجموعات المسماة أدناه؛ لا import/processing أصلي لـArcMap |
| حماية المرجع الجديدة | 3 اختبارات ناجحة | قيم/ترتيب/فقد/مسارات وسلوك رفض إعادة الالتقاط |
| Legacy بعد إضافة الحماية | 18 مجموعة / 149 اختبارًا ناجحة | تشمل الاختبارات الثلاثة الجديدة؛ ليست 149 اختبارًا إضافيًا |
| مقارنة المحركين | ناجحة للحزم الـ19 مع شهور كاملة وناقصة | التساوي لا يعني تكافؤ جميع exports/native rasters |
| عقود المستودع والموقع بعد التوثيق | ناجحة؛ 167 رابط توثيق محلي و63 رابط/أصل/anchor للموقع | scientific/source/catalogue/help parity ناجحة؛ لا إعادة بناء binary |
| خدمة Open-Meteo | أربعة طلبات ناجحة | عينة واحدة لمدة 3 أيام |

فشل اختبار XLS في أول محاولة لأن `.venv` لا تضم xlwt. أُعيدت المجموعات بعد إضافة
`MIRSAD Desktop/.build/reorganization/test-deps` الموجودة مسبقًا إلى PYTHONPATH للعملية
فقط؛ نجحت المجموعات الـ17. لم تُثبّت مكتبات أو تُغيّر تبعيات التطبيق.
ظهرت تحذيرات deprecation من Shapely في اختبارات Desktop، دون فشل.

المجموعات السبعة على Python 2.7: `test_runtime_stability`, `test_tool_validation`,
`test_climate_products`, `test_remote_grid`, `test_hybrid_pipeline`,
`test_station_multi_selection`, `test_repository_layout`.
الأعداد تخص نطاقات متداخلة، ولا تُجمع باعتبارها اختبارات علمية فريدة.

## أوامر التكرار

من جذر المستودع، باستخدام PowerShell:

```powershell
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'MIRSAD Desktop/.build/reorganization/test-deps').Path
& 'MIRSAD Desktop/.venv/Scripts/python.exe' scripts/run_checks.py --output tests/.output/comprehensive-baseline-ready
& 'MIRSAD Desktop/.venv/Scripts/python.exe' -m unittest discover -s 'MIRSAD Desktop/tests' -v
& 'MIRSAD Desktop/.venv/Scripts/python.exe' scripts/audit_climate_enrichment.py
& 'MIRSAD Desktop/.venv/Scripts/python.exe' scripts/check_repository.py
```

إذا لم تكن مكتبات الاختبار المحلية موجودة في checkout جديد، تُجهز متطلبات
`tests/requirements.txt` في بيئة QA قبل تشغيل Legacy؛ لا تعتمد نسخة Desktop الموزعة عليها.
`--capture` أمر تأسيس مرة واحدة وليس أمر إصلاح للاختبارات. لا يُحدّث المرجع لإخفاء تغيير
في الحساب أو اسم الحقل أو مسار النتيجة.

## ما يلي التدقيق

تحديث متابعة 21 أكتوبر: دُمجت الإضافات في مصدر Desktop وأعيد تشغيل المرجع الأصلي
بنجاح. التفاصيل في [قبول مصدر Desktop](DESKTOP_SOURCE_ACCEPTANCE.md)؛ وصف ما بعد
التدقيق أدناه هو ترتيب العمل عند التقاط هذه الوثيقة، وليس قائمة الحالة الحالية.

يبدأ التنفيذ بسجل اختيارات المتغيرات وتتبّع المعالجة اليومية، وتجهيز مسار Excel الكبير،
ثم دمج الرطوبة والمشتقات والمناسيب وPM على دفعات كاملة. كل دفعة تعيد اختبار السلوك القديم
والخيارات الجديدة مقفولة، وتضيف أمثلة علمية مستقلة وفحوص المخرجات. لا تكفي لقطة البداية
لإثبات أن خيارات Off الجديدة تحافظ على السلوك قبل أن تُضاف هذه الخيارات وتُختبر فعليًا.
