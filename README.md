<p align="center">
  <a href="https://ahmadibrahim4geo.github.io/MIRSAD/">
    <img src="assets/mirsad-logo-full.png" alt="مِرصاد — قاعدة بيانات الأطلس المكاني لإعادة التحليل المتكامل للأرصاد الجوية | Meteorological Integrated Reanalysis Spatial Atlas Database" width="100%">
  </a>
</p>

<h1 align="center">مِرصاد | MIRSAD</h1>

<p align="center">
  أدوات ArcGIS وتطبيق Desktop مستقل لتحليل المناخ، واختيار محطات الرصد، وإنتاج الأطالس وقواعد البيانات الجغرافية.<br>
  ArcGIS tools and an independent Desktop application for climate analysis, station selection, spatial atlases and geodatabases.
</p>

<p align="center">
  <a href="https://github.com/ahmadibrahim4geo/MIRSAD/actions/workflows/checks.yml"><img src="https://github.com/ahmadibrahim4geo/MIRSAD/actions/workflows/checks.yml/badge.svg" alt="Deterministic source checks"></a>
  <a href="https://github.com/ahmadibrahim4geo/MIRSAD"><img src="https://img.shields.io/badge/ArcGIS-ArcMap%20%7C%20Pro-0079c1" alt="ArcGIS ArcMap and Pro"></a>
  <a href="#requirements"><img src="https://img.shields.io/badge/Python-2.7%20%7C%203-3776ab" alt="Python 2.7 and 3"></a>
  <a href="#modules"><img src="https://img.shields.io/badge/Climate%20Modules-19-047857" alt="19 climate modules"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue" alt="MIT License"></a>
</p>

<p align="center">
  <a href="https://ahmadibrahim4geo.github.io/MIRSAD/">الموقع | Website</a> ·
  <a href="https://github.com/ahmadibrahim4geo/MIRSAD/archive/refs/heads/main.zip">تحميل الحزمة | Download ZIP</a> ·
  <a href="Documents/00_Documentation_Index_AR.md">التوثيق العربي</a> ·
  <a href="Documents/00_Documentation_Index.md">English Docs</a>
</p>

---

## ابدأ من هنا | Start here

[نظرة عامة](#overview) · [التثبيت](#requirements) · [اختيار المحطات](#stations) · [الحزم](#modules) · [المصادر](#sources) · [النتائج](#outputs) · [التوثيق والتحقق](#documentation) · [English](#english)

<a id="overview"></a>

## ما هي مِرصاد؟

**MIRSAD** اختصار **Meteorological Integrated Reanalysis Spatial Atlas Database**، ومعناه **قاعدة بيانات الأطلس المكاني لإعادة التحليل المتكامل للأرصاد الجوية**.

تساعد المنظومة على تنزيل السلاسل الزمنية عند نقاط أو مواقع محطات مختارة، وحساب المؤشرات السنوية والفصلية والشهرية، ثم تصدير طبقات النقاط والجداول وقواعد البيانات وأسـطح الراستر. تدعم العمل بمصادر الإنترنت المنفذة، أو الاستيفاء الأوفلاين من طبقات محسوبة مسبقًا.

| المكوّن | الوظيفة | نقطة الدخول |
| --- | --- | --- |
| أداة المحطات | اختيار دولة ومحطة واحدة أو عدة محطات بالأسماء والأكواد؛ واجهتان عربية وإنجليزية | `MIRSAD_Weather_Stations_Atlas_Generator.pyt` |
| صندوق أطلس النقاط | السلاسل الزمنية، حساب المؤشرات، التصدير والاستيفاء | `MIRSAD_Climate_Atlas_Generator_10_8.pyt` |
| أداة الراستر | شبكات NASA POWER وCHIRPS وCHELSA أو نقاط محسوبة مسبقًا، ثم الاستيفاء والقص | `MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt` — صندوق مستقل |
| دليل المحطات | مواقع وأكواد المحطات وطبقاتها ومستكشفات HTML | `Weather_Stations_Hub/` |

## MIRSAD Desktop — نسخة التطوير المستقلة

خطة دورة التطوير التالية، وتنظيم صناديق النقاط والمحطات والراستر، واختيار الدقة تلقائيًا لكل عنصر، وإضافة المصادر ومزامنة الأدلة والموقع مسجلة في [خطة التطوير المشتركة وسجل القرارات](Documents/DEVELOPMENT_ROADMAP.md). البنود المخططة ليست إعلانًا عن وظائف منفذة.

بدأ تطوير تطبيق Windows مستقل داخل [MIRSAD Desktop](MIRSAD%20Desktop/README.md)، بكتالوج محطات مضمن وواجهة عربية/إنجليزية، وتصدير FileGDB وGeoPackage وExcel. يوجد مكان ثابت للتطوير ومكان ثابت للنسخة المعتمدة بعد الموافقة؛ لا يوجد إصدار Desktop منشور على GitHub Releases حتى الآن. راجع [خطة التنفيذ وحالة الوظائف](MIRSAD%20Desktop/IMPLEMENTATION_PLAN.md) و[دليل التطوير](AGENTS.md).

تحديث dev8: مركز مساعدة محلي عربي/إنجليزي، 45 موضوعًا، ومعادلات العناصر الـ19 مرتبطة بـ521 حقلًا محسوبًا ممكنًا. يوجد فهرس وبحث ومفضلة وتنقل وطباعة داخل Desktop، وملفا Windows CHM ونسخة HTML من المحتوى نفسه. تبقى عناوين الخرائط موجزة مثل «متوسط هطول الأمطار»، ويشرح الدليل متوسط التراكميات والوحدات وشروط التغطية.

[الدليل العربي](Help/MIRSAD_Help_AR.html) · [English help](Help/MIRSAD_Help_EN.html) · [CHM عربي](Help/MIRSAD_Help_AR.chm) · [English CHM](Help/MIRSAD_Help_EN.chm) · [المساهمة بالعربية](CONTRIBUTING_AR.md) · [Contributing](CONTRIBUTING.md) · [الفحوص وحدودها](Documents/TESTING.md)

نرحب بالمساهمات والأفكار عبر قوالب Issues وPull Requests. لتنزيل الدليل وتشغيل HTML محليًا استخدم حزمة ZIP الكاملة؛ معاينة GitHub للملف لا تشغل الصفحة التفاعلية. مصدر Desktop متاح هنا، بينما EXE والمثبت وبيئة البناء خارج Git؛ لا تعني إتاحة المصدر اعتماد نسخة مستقرة أو نشر إصدار ثنائي.

<a id="requirements"></a>

## التثبيت والتشغيل

- **ArcMap / ArcGIS Desktop 10.x:** بيئة Python 2.7 المرفقة بالبرنامج.
- **ArcGIS Pro:** بيئة Python 3 المرفقة بالبرنامج.
- **Spatial Analyst:** مطلوب للعمليات المكانية التي تستخدمه، ومنها إنتاج أسطح الراستر.
- الاتصال بالإنترنت مطلوب للتنزيل؛ وضع الأوفلاين يعتمد على مدخلات محلية محسوبة مسبقًا.

1. حمّل [المستودع كاملًا كملف ZIP](https://github.com/ahmadibrahim4geo/MIRSAD/archive/refs/heads/main.zip)، أو استنسخه:

   ```bash
   git clone https://github.com/ahmadibrahim4geo/MIRSAD.git
   ```

2. احتفظ بهيكل المجلدات؛ ملفات `.pyt` تعتمد على المحرك وملفات `utils/`، وأداة المحطات تعتمد على `Weather_Stations_Hub/`. تنزيل ملف `.pyt` منفرد لا يكفي.
3. أضف صندوق الأدوات المطلوب عبر **Catalog / ArcToolbox → Add Toolbox**.
4. افتح الأداة، وحدد المدخلات والمصدر والفترة والحزم ومجلد الإخراج، ثم شغّلها.

بعد تحديث الأداة، أعد فتحها. إذا كنت تستخدم ModelBuilder أو استدعاءً برمجيًا بمعاملات مرتبة حسب المواقع، حدّث تعريف أداة المحطات للمعامل الجديد `Selected_Stations`.

<a id="stations"></a>

## اختيار محطة واحدة أو عدة محطات

1. افتح أداة المحطات بالعربية أو الإنجليزية.
2. اختر **«اختيار محطات محددة من الدولة (اختيار متعدد)»** / **Select Specific Stations by Country (Multiple Selection)**.
3. اختر الإقليم ثم الدولة.
4. اختر محطة واحدة أو أكثر من **«اختر المحطات من الدولة (اختيار متعدد)»**، ثم شغّل الأداة.

تظهر أسماء المحطات وأكواد **USAF/WBAN** والدولة لتمييز الأكواد المتكررة. الاختيار الفارغ يمنع التشغيل؛ تغيير الدولة يستبعد الاختيارات الخارجة عن قائمتها. تبقى أوضاع شبكة الدولة كاملة، والأكواد اليدوية، والطبقة المحلية متاحة. يمكن إضافة نقاط رفع داعمة إذا اختار المستخدم طبقتها صراحة.

في وضع **«اختيار بالدولة (الشبكة الوطنية المعتمدة)»** تتاح قائمة المحطات أيضًا بعد اختيار الإقليم والدولة. اختيار محطات منها يعالج هذا الاختيار فقط؛ تركها فارغة يعالج شبكة الدولة كاملة. يظل شرط اختيار محطة واحدة على الأقل خاصًا بوضع **«اختيار محطات محددة»**. النطاقات الإقليمية الشاملة تبقى متاحة في وضع الشبكة.

الدليل المرفق يحتوي على **28,066 سجل محطة عالميًا، منها 85 في مصر**. اختيار محطة يحدد موقع الاستعلام؛ **نوع البيانات يحدده المصدر**، ولا يعني تلقائيًا تنزيل أرصاد NOAA المباشرة.

[دليل اختيار المحطات وتفاصيل التحقق](Documents/STATION_MULTI_SELECTION_2026_10_16_AR.md)

## الشهريات والأوفلاين وجودة البيانات

- **أوفلاين:** استخدم طبقات نقاط بها مؤشرات محسوبة مسبقًا دون إعادة تنزيل السلاسل الزمنية.
- **راستر الشهريات في أداة الراستر:** فعّل `Generate_Monthly_Rasters` مع حقول الشهور الموجودة وفترة سنتين فأكثر. المتوسطات الشهرية ونطاقاتها لهما مفتاحان مستقلان. الدعم الشهري الأونلاين لهذه الأداة غير مكتمل.
- **الأمطار:** الصفر المرصود يظل صفرًا؛ الشهر المفقود يظل خاليًا. المجاميع اليومية والشهرية والفصلية والسنوية تتطلب اكتمال مدخلات الفترة.
- **المؤشرات المشتقة:** نقص المدخلات اللازمة ينتج `NULL` بدل افتراض قيم للحرارة أو المطر أو الاتجاهات.
- **الدمج المكاني:** المطابقة تعتمد على مواقع النقاط، مع تمييز النقاط المتطابقة عند توفر معرفاتها؛ لا يُستخدم OID لربط مواقع مختلفة.

[إصلاحات جودة البيانات وحدود الدعم](Documents/DATA_QUALITY_FIXES_2026_10_16_AR.md)

<a id="modules"></a>

## الحزم المناخية | Climate modules

تضم المنظومة **19 حزمة**. يوضح الجدول أسماءها البرمجية وطبقاتها ومجلداتها الحالية. **521 حقل مؤشر مسجلًا**، ومع **13 حقلًا إداريًا** يصبح الكتالوج **534 عمودًا**. الحقول المسجلة تشمل الخيارات الإضافية؛ المخرجات الفعلية تعتمد على الإعدادات وتوفر البيانات.

| # | الحزمة / Module | Feature Class | مجلد الراستر / Folder | الحقول المسجلة |
| :---: | --- | --- | --- | :---: |
| 01 | Temperature | `Temperature` | `01_Temperature` | 34 |
| 02 | Land Surface Temperature | `Land_Surface_Temperature` | `02_Land_Surface_Temperature` | 35 |
| 03 | Precipitation | `Precipitation` | `03_Precipitation` | 30 |
| 04 | Sea Level Pressure | `Sea_Level_Pressure` | `04_Sea_Level_Pressure` | 30 |
| 05 | Surface Pressure | `Surface_Pressure` | `05_Surface_Pressure` | 30 |
| 06 | Wind | `Wind` | `06_Wind` | 49 |
| 07 | Relative Humidity | `Relative_Humidity` | `07_Relative_Humidity` | 30 |
| 08 | Dew Point | `Dew_Point` | `08_Dew_Point` | 30 |
| 09 | Solar Radiation | `Solar_Radiation` | `09_Solar_Radiation` | 31 |
| 10 | UV Index | `UV_Index` | `10_UV_Index` | 30 |
| 11 | Cloud Cover | `Cloud_Cover` | `11_Cloud_Cover` | 30 |
| 12 | Heat Index | `Heat_Index` | `12_Heat_Index` | 19 |
| 13 | Wind Chill | `Wind_Chill` | `13_Wind_Chill` | 18 |
| 14 | De Martonne Aridity | `De_Martonne_Aridity` | `14_De_Martonne_Aridity` | 1 |
| 15 | Evapotranspiration | `Evapotranspiration` | `15_Evapotranspiration` | 31 |
| 16 | UNEP Aridity | `UNEP_Aridity` | `16_UNEP_Aridity` | 1 |
| 17 | Water Deficit | `Water_Deficit` | `17_Water_Deficit` | 1 |
| 18 | Dry Months | `Dry_Months` | `18_Dry_Months` | 1 |
| 19 | Trends & Anomalies | `Trends_And_Anomalies` | `19_Trends_And_Anomalies` | 90 |

يستخدم حساب البخر والنتح صيغة **Hargreaves-Samani** الموجودة في المحرك، بمتوسط الحرارة وعظماها وصغراها والإشعاع الفلكي. يحتاج كل مؤشر إلى مدخلاته الفعلية. تتوفر المعادلات والوحدات والأمثلة في [الدليل العلمي](Documents/01_Markdown_Manuals/05_Scientific_Formulas_All_Indicators.md) و[مرجع الحقول](Documents/01_Markdown_Manuals/Fields_Reference_Table.md).

<a id="sources"></a>

## مصادر البيانات وحالة دعمها

| المصدر | الدعم المنفذ في نسخة التطوير |
|---|---|
| NASA POWER | النقاط والمحطات والشبكة الإقليمية؛ شبكة المصدر حسب المتغير |
| Open-Meteo ERA5/Land | Auto لأدق منتج مناسب لكل متغير وفترة؛ اختيار يدوي متقدم |
| NOAA GSOD / GHCN-Daily | رصد محطات فقط، بمعرف المصدر والموقع؛ لا استبدال بأقرب محطة |
| Hybrid | NOAA ثم ERA5 ثم NASA؛ وهجين نقاط ERA5 ثم NASA؛ Gap Fill الشهري بعد انتهاء المراحل |
| CHIRPS v3 / CHELSA v2.1 | نقاط ومواقع المحطات، وخلايا الشبكة الإقليمية الأصلية |
| TerraClimate v1.1 | مناخ شهري عند النقاط ومواقع المحطات |
| MODIS MOD11A2 | حرارة سطح نهارية أو ليلية منفصلة، مع جودة وتغطية السماء الصافية |
| CDS ERA5-Land / NASA IMERG V07 Final | Need Sign In؛ رمز CDS أو حساب Earthdata الخاص بالمستخدم. المساران منفذان، والتحقق بحساب فعلي ما زال مطلوبًا |

[دليل المصادر العربي](Documents/05_Climate_Data_Sources_Directory/SOURCES_AR.md) · [English source guide](Documents/05_Climate_Data_Sources_Directory/SOURCES_EN.md) · [Bilingual website catalogue](climate-sources.html)

كل مصدر يوفر اعتماديات محددة؛ غياب البيانات يبقى NULL ولا يفرض تحويل المصدر. المنتجات الشهرية/المركبة لا تصنع سجلات يومية. لا يوجد ضمان اكتمال 100%. المقارنة الكاملة بين أعمدة ومخرجات Toolbox وDesktop ما زالت بوابة قبول مستقلة.

<a id="outputs"></a>

## المخرجات وتنظيم المشروع

حسب الأداة والحزم والإعدادات المختارة، تنتج المنظومة:

- طبقات نقاط داخل File Geodatabase، وتصدير Shapefile عند تفعيله.
- أسطح **GeoTIFF** مستوفاة ومقصوصة على منطقة الدراسة، باستخدام طرق مثل IDW وKriging وSpline.
- جداول **Excel** ومؤشرات سنوية وفصلية وشهرية؛ وسلاسل يومية عند تفعيل حفظها. تنقسم السلاسل الكبيرة على شيتات `Daily` و`Daily_2` وغيرها دون حذف صفوف؛ يُستخدم CSV فقط عند فشل تصدير Excel مع رسالة توضح السبب.
- متجهات الرياح وخطوط تساوي الضغط عند تفعيل خياراتها، وقواميس وتقارير تشغيل.

لتصدير السنوات منفردة، فعّل **«تصدير ملف Excel مستقل لكل سنة (بالإضافة إلى الملف المجمع)»** / **Export Separate Excel Workbook per Year** عند تنزيل فترة متعددة السنوات. تحت مجلد كل عنصر ينشأ مجلد `Years` يحتوي ملفات `<Element>_<Year>.xls`. يعاد حساب الملخصات لكل سنة ببياناتها ووحداتها وإعدادات سد الفجوات نفسها، دون إعادة التنزيل. تحتوي الملفات على `Data` و`Source_Data` و`Month` حسب الحقول المختارة، و`Daily` عند تفعيل حفظ اليومي. يظل الملف المجمّع موجودًا؛ الخيار لا ينشئ راستر أو قاعدة بيانات مستقلة لكل سنة، ولا يعمل على مؤشرات أوفلاين مجمعة لا تحتوي السلسلة الأصلية.

```text
MIRSAD/
├── MIRSAD_Climate_Atlas_Generator_10_8.pyt
├── MIRSAD_Weather_Stations_Atlas_Generator.pyt
├── raster_atlas_generator.py
├── utils/                  # ملفات التشغيل المساعدة
├── Weather_Stations_Hub/   # دليل المحطات وطبقاتها ومستكشفاتها
├── assets/                 # الشعار المعتمد وملفات الموقع
├── Documents/              # الأدلة العلمية والتقنية
├── style/                  # الستايلات وأدلة الألوان
├── tests/                  # اختبارات الحسابات والتوافق والتشغيل
└── index.html              # الصفحة التعريفية
```

[دليل الستايلات والألوان](style/00_Main_Element_Styles/README.md) · [ملفات الشعار المعتمد](assets/README.md)

<a id="documentation"></a>

## التوثيق والتحقق

| المرجع | الرابط |
| --- | --- |
| التوثيق العربي | [فهرس الأدلة](Documents/00_Documentation_Index_AR.md) |
| English documentation | [Documentation index](Documents/00_Documentation_Index.md) |
| استخدام الأدوات | [العربية](Documents/01_Markdown_Manuals/User_Guide_Arabic.md) · [English](Documents/01_Markdown_Manuals/User_Guide_English.md) |
| اختيار المحطات المتعدد | [دليل الميزة](Documents/STATION_MULTI_SELECTION_2026_10_16_AR.md) |
| جودة البيانات | [تغييرات 16 أكتوبر 2026](Documents/DATA_QUALITY_FIXES_2026_10_16_AR.md) |
| التشغيل والتوافق | [الإصلاحات وحدود التحقق الأصلي](Documents/RUNTIME_FIXES_2026_10_16_AR.md) |
| التطوير والمساهمة | [العربية](Documents/06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_AR.md) · [English](Documents/06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_EN.md) |

نجحت اختبارات Python 2.7 و3، ومنها **17 حالة لاختيار المحطات المتعدد** و**8 حالات للتصدير السنوي وExcel**. يشمل التحقق حفظ ملفات Excel وقراءتها فعليًا، والتقسيم عند تجاوز 60 ألف صف، والتواريخ الكبيسة، ووحدات القياس ومجاميع الأمطار السنوية. بعض اختبارات تدفق GIS تستخدم محاكاة ArcPy؛ نجاحها لا يعادل اختبار التشغيل الأصلي. عائق تثبيت ArcGIS المحلي وحدود التحقق موثقان في تقرير التشغيل أعلاه.

أمثلة اختبارات مستقلة عن الشبكة، تُشغّل كل مجموعة في عملية منفصلة:

```bash
python -B tests/test_station_multi_selection.py
python -B tests/test_data_quality.py
python -B tests/test_runtime_stability.py
python -B tests/test_yearly_excel_export.py
python -B tests/test_tool_validation.py
```

بعد توفر تثبيت ArcGIS سليم، يُشغّل الفحص الأصلي صراحةً من بيئته:

```bash
python -B tests/verify_native_offline.py
```

<a id="english"></a>

## English quick guide

**MIRSAD — Meteorological Integrated Reanalysis Spatial Atlas Database** is an ArcGIS toolkit for climate time series, station-location analysis, thematic atlases and geodatabases. The approved bilingual logo appears first in this README; its Arabic full name is **قاعدة بيانات الأطلس المكاني لإعادة التحليل المتكامل للأرصاد الجوية**.

1. Download the **complete repository** and keep its folder structure, including `utils/`, the core engine and `Weather_Stations_Hub/`.
2. Add either Python toolbox through **Catalog / ArcToolbox → Add Toolbox**. Use the Python environment supplied with ArcMap or ArcGIS Pro and Spatial Analyst for the operations that require it.
3. For a station subset, select **Select Specific Stations by Country (Multiple Selection)**, choose a region and country, then one or more named stations. Empty or stale selections never broaden into a whole-country run. Existing country-network, manual-ID and local-layer modes remain available.
4. Select the provider, period, climate modules and output workspace, then run. NASA POWER and Open-Meteo are implemented for point/station-location queries; the online raster pipeline uses NASA POWER Regional. Direct NOAA, Hybrid and CDS downloads are not implemented.
5. For monthly rasters in the raster tool, use **Offline** mode, existing monthly fields and a span of at least two years. Monthly means and monthly ranges have independent switches.

In **Select by Country (National Network)** mode, the station checklist is also available after choosing a region and an individual country. Select a subset or leave it empty for the full national network. The dedicated specific-stations mode still requires a nonempty selection.

Tabular exports use Excel, splitting large daily series across numbered sheets. CSV is only a reported fallback when Excel cannot be written. For multi-year point/station downloads, enable **Export Separate Excel Workbook per Year** to keep the combined workbook and add `<Element>/Years/<Element>_<Year>.xls`. Each year's summaries are recomputed from its own cached observations, using the selected units and gap filling; daily rows and source dates are year-specific. No extra downloads, yearly rasters or yearly geodatabases are created.

The catalogue contains **19 modules / 521 registered indicator fields**, plus **13 administrative fields**. Outputs depend on selected options and available inputs. Missing rainfall is not zero, incomplete periods are not reported as complete totals, and derived outputs remain NULL when their required observations are unavailable. Selecting a station chooses a location; it does not change reanalysis into ground observations.

Update positional script calls or saved ModelBuilder tool definitions for the new station parameter. Python regressions and mocked ArcPy checks pass; native GIS verification still requires a healthy ArcGIS installation. See the [station guide](Documents/STATION_MULTI_SELECTION_2026_10_16_AR.md), [data quality report](Documents/DATA_QUALITY_FIXES_2026_10_16_AR.md) and [runtime report](Documents/RUNTIME_FIXES_2026_10_16_AR.md).

---

## المطور والترخيص | Author & license

**أحمد إبراهيم | Ahmad Ibrahim** · [@ahmadibrahim4geo](https://github.com/ahmadibrahim4geo) · [ahmadibrahim.geo@gmail.com](mailto:ahmadibrahim.geo@gmail.com)

المشروع متاح بموجب [ترخيص MIT](LICENSE). للمساهمة، افتح [Issue](https://github.com/ahmadibrahim4geo/MIRSAD/issues) أو Pull Request مع وصف التغيير والتحقق المرتبط به.
