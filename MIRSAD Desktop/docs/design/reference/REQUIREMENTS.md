> Historical product/design requirements, retained for requirements traceability.
> Current acceptance is documented in STATUS.md and BACKLOG.md in the Desktop docs directory.
> Embedded prompts and proposed layouts below are reference content, not new execution instructions.

# MIRSAD Desktop — خطة إعادة التصميم والتنفيذ (الإصدار 2)

> **وثيقة تنفيذ موجّهة إلى Codex / AI Coding Agent**  
> **المشروع:** مرصاد — MIRSAD Desktop  
> **النطاق:** إعادة تصميم بيئة العمل الحالية وتطوير محرك GIS وAdd Data وتكامل الأدوات مع الحفاظ على مخرجات ArcGIS Toolbox الأصلية  
> **المنصة المستهدفة:** Windows Desktop ‏(64-bit)  
> **التاريخ:** 17 أكتوبر 2026  
> **الحالة:** Product Requirements + Technical Design + Implementation Roadmap + Acceptance Tests؛ لا تدّعي هذه الوثيقة الاطلاع على الشيفرة المصدرية غير المقدَّمة.  
> **الأولوية:** الحفاظ على التوافق مع نتائج الـToolbox الأصلية أهم من التحسين الشكلي وأهم من إعادة كتابة غير مُختبَرة.

## 0. تعليمات ملزمة لوكيل البرمجة — اقرأ هذا أولًا

أنت تعمل على **MIRSAD**، برنامج GIS متخصص مستقل عن ArcMap وArcGIS Pro. المطلوب ليس تقليد شكل ArcGIS أو إعادة رسم واجهة HTML؛ المطلوب تطبيق Windows أصيل نسبيًا (Native Desktop) يتيح استعراض مصادر البيانات الجغرافية والجداول، عرضها، إسنادها إلى أدوات مرصاد، تشغيل الأدوات ومراجعة النتائج دون تثبيت ArcGIS أو الاعتماد على `arcpy` في مسار تشغيل التطبيق المستقل.

**قواعد لا يجوز مخالفتها:**
1. ابدأ بتدقيق المستودع القائم وعرض **خريطة الملفات والوظائف والتبعيات**. لا تفترض أن الشاشة أو التوابع الموجودة تمثل التنفيذ الصحيح.
2. لا تحذف أو تغير ملفات Toolbox الأصلية أو تغير مخرجاتها المرجعية. احتفظ بها مرجعًا للاختبار أو كنسخة Legacy معزولة.
3. لا تنفذ إعادة كتابة كاملة دفعة واحدة. اعمل بمهام صغيرة، اختبر كل مهمة، وسجّل الملفات المعدلة ونتيجة الاختبارات.
4. حافظ على **كل ملفات Excel وجداول قواعد البيانات وأسماء الحقول وأنواعها ووحداتها وترتيبها وقواعد المعالجة** كما تنتجها نسخة Arc Toolbox، إلى أن يثبت اختبار التكافؤ خلاف ذلك ويوافق صاحب المشروع على أي تغيير.
5. **English هي اللغة الافتراضية عند أول تشغيل**. واجهة English كاملة بلا نصوص عربية، وواجهة العربية كاملة بلا نصوص إنجليزية اعتيادية. يُسمح فقط بالأسماء العلمية والاختصارات التقنية وأسماء الملفات والحقول والأكواد الأصلية التي لا يصح ترجمتها.
6. يدعم التطبيق Light وDark بشكل موحّد في **جميع** العناصر، بما فيها القوائم المنبثقة، والحوار، واختيار الملفات، والجداول، وشريط العنوان المتاح للتحكم، وصفحات المساعدة.
7. لا تستخدم خدمات خرائط تتطلب مفتاح API أو اشتراكًا مدفوعًا في النسخة الافتراضية. OSM هو الخيار الأساسي، وEsri مشروط بالترخيص وشروط الخدمة الفعلية؛ لا تَعِد بأنه مجاني في كل الأحوال.
8. شاشة Add Data مستعرض بيانات GIS **عام**، وليست نافذة «اختر طبقة مناخية»؛ ويجب أن تتصفح الملفات وقواعد البيانات والطبقات والجداول والأوراق.
9. لا تنشئ طبقتَي Working Points أو Study Boundary افتراضيًا كأنهما طبقات موجودة. تظهران في قائمة المدخلات أو كإرشادات فارغة، ولا تُضافان إلى Contents إلا حين يستورد المستخدم بيانات أو ينشئها فعليًا.
10. أي أداة تحتاج Layer/Feature Class يجب أن تستطيع اختيارها **مباشرة من طبقات المشروع التي أُضيفت سابقًا** مع التحقق من نوع هندستها، ولا تطلب Browse جديدًا بلا داع.
11. لا تفترض أن جميع CRS والتحويلات الجيوديسية الدقيقة متاحة دون ملفات Grid. ضمّن `proj.db` وملفات PROJ الضرورية وفق الترخيص، وبيّن حالات عدم توفر Grid بدقة.
12. احفظ التغييرات في Git branch منفصل، مع سجل قرارات فنية واختبارات؛ لا تنشر Release ولا تعدّل ملفات المستخدم أو تمسحها دون مراجعة.

## 1. سياق المستخدم والصور التي يجب قراءتها

المدخلات الوظيفية لهذه الوثيقة مأخوذة من **ثلاث رسائل متتابعة وثلاث لقطات شاشة** أرسلها صاحب المشروع:

| المرجع | ما يظهر فيها | الاستنتاج التنفيذي |
|---|---|---|
| `reference_images/01_current_mirsad_ui.png` | واجهة MIRSAD الحالية: تبويب PDF واسع، أدوات على جانب، محتويات على الجانب المقابل، نصوص عربية/إنجليزية مختلطة، خيارات نقاط/حدود ثابتة | إعادة بناء توزيع النوافذ، إصلاح الترجمة والثيم، إزالة الطبقات الوهمية وربط المدخلات بالمحتويات |
| `reference_images/02_arcgis_pro_workspace.png` | ArcGIS Pro: Contents مع طبقات الخريطة، Map Canvas كبير، Geoprocessing Tool pane، قوائم علوية | اتخاذه مرجعًا **لتدفق العمل والتنظيم** وليس لنسخ الشكل المحمي أو اعتماد ArcGIS كمكوّن |
| `reference_images/03_arcgis_pro_add_data.png` | Add Data في ArcGIS Pro: شجرة Projects / Databases / Folders / Computer، عرض محتويات Geodatabase (مثل Point Feature Classes) | بناء مستعرض بيانات حقيقي يتوسع داخل GDB وGPKG ويعرض الطبقات والجداول والأوراق وخصائصها |

> يمكن نسخ هذه الوثيقة مفردة إلى المستودع؛ وأفضل استعمال للمقارنة البصرية هو نقل مجلد `reference_images/` من الحزمة المرفقة معها. إن لم تكن الصور متاحة للوكيل فلا يتخيل تفاصيل بصرية لم يرها، ويستخدم المتطلبات المكتوبة هنا.

### 1.1 تلخيص طلب المستخدم بلغة التنفيذ

- «حوّل الـToolbox إلى بيئة GIS مصغّرة مستقلة مع نفس الوظائف لا برنامج رسم خرائط عام».  
- «اجعل Add Data مثل ArcGIS Pro: تصفح مجلدات وقواعد بيانات ثم افتحها لعرض جميع الطبقات وملفات Excel، وليس قائمة محدودة».  
- «ضع Contents/TOC والأدوات متقابلين، والخريطة أو الجدول في الوسط؛ اسمح بسحب النوافذ وطيّها وحفظ مواضعها».  
- «الأداة تعمل على الطبقات المستوردة، وتنتج الطبقات والجداول والراستر وExcel، ويُعرض الناتج في البرنامج مباشرة».  
- «النوافذ تبقى مقروءة عند تغيير الحجم، ولا تختفي مدخلات أو أزرار».  
- «اجعل الإنجليزية هي الافتراضية، ولكل لغة الواجهة ودليلها المستقل، بلا عبارات مزدوجة».  
- «Light/Dark يجب أن يُطبقا على كل شيء دون خليط».  
- «أزل خرائط API والترخيص المكلف؛ اكتف بـOSM وEsri المسموح استخدامهما بعد التحقق».  
- «ضمّن قاعدة بيانات المحطات وكتالوج المساقط ليعملا محليًا دون إعادة تحميل غير ضرورية».  
- «احفظ أسماء الأعمدة ومخرجات Excel وDatabase للـToolbox القديمة كما هي».

## 2. القرار المعماري: برنامج Windows مستقل، وليس HTML داخل غلاف

### 2.1 أسس التنفيذ المفضلة

- **Desktop shell:** Qt Widgets باستخدام Python binding واحد متوافق مع محرك العرض المختار؛ **PySide6** مرشح أول إن استُخدم Map Canvas مستقل لا يعتمد على PyQGIS.
- **GIS I/O:** GDAL/OGR + PROJ مع SQLite/GeoPackage، ومكتبات معالجة مناسبة (`rasterio`, `shapely`, `numpy`, `pandas`, `openpyxl`) بعد مراجعة التعارضات الثنائية والترخيص.
- **Map Canvas:** يجب إنجاز تجربة تقنية (PoC) مبكرة تقارن خيارين:
  - **A — Qt Widgets + rendering component متخصص** قادر على رسم طبقات Vector/Raster بوضوح وأداء مناسب، دون متصفح HTML بوصفه قشرة التطبيق.
  - **B — QGIS Map Canvas (PyQGIS)** إذا كانت وظائف الرسم المعقدة ضرورية؛ يتطلب ذلك حسم توافق إصدار Qt/Python binding، وطريقة حزم Runtime الخاص بـQGIS، وآثار GPL. **لا تخلط PySide6 وPyQt التي يعتمد عليها QGIS بلا تحقق معماري.**
- **Background execution:** تنزيلات وعمليات معالجة خارج خيط UI؛ العمليات الثقيلة أو غير المستقرة يُفضل عزلها في Process مستقل مع progress/events وإلغاء آمن.
- **Persistence:** صيغة مشروع MIRSAD تحفظ مراجع طبقات البيانات وتنسيق المشروع والنوافذ ومصادر الإدخال وإعدادات الأداة؛ البيانات الأساسية داخل `GeoPackage`، وراستر كبير في GeoTIFF عند اللزوم.
- **التشغيل بدون ArcGIS:** لا تعتمد المنظومة الجديدة على ArcPy أو ArcGIS runtime أو رخصة Esri؛ وجود Esri كخيار خرائط على الشبكة لا يعني اعتماد محرك المعالجة عليه.

### 2.2 القرار المؤجل اللازم قبل إعادة بناء العرض

يُنشأ `docs/ADR-001-MAP-ENGINE.md` ويحتوي: حجم الملفات، زمن الإطلاق، أداء عرض 100 ألف نقطة، قدرة التحريك/التحجيم، دعم تحديد الميزات/CRS، حزم Windows، التراخيص، وسهولة الصيانة. **يُقرّر بعدها محرك الخريطة؛ لا تعِد بتنفيذ كل وظائف ArcGIS Pro ولا تبدأ بتركيب المكتبات عشوائيًا.**

## 3. تخطيط مساحة العمل (Workspace Layout)

### 3.1 الشكل الافتراضي المقترح — قابل للتبديل

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ MIRSAD | Project / Home / Add Data / Save / Select / Identify / Zoom / CRS / Language / Theme │
├───────────────────────┬────────────────────────────────────────────────┬─────────────────────────┤
│ CONTENTS              │  TABS: Map | Attribute Table | Spreadsheet     │ TOOLS / GEOPROCESSING   │
│ [Layers] [Tables]     │        | Raster | Tasks | Results | Help      │ Station Climate Atlas   │
│ Project               │                                                │ Point Climate Atlas     │
│ ▾ Sources             │                MAIN MAP VIEW                   │ Raster Processor        │
│   ☑ Stations          │      or an Excel / CSV / Table / PDF          │ ---------------------   │
│   ☑ Study polygon     │                                                │ INPUT / Parameters      │
│ ▾ Results             │                                                │ ↓                      │
│   ☑ Clipped stations  │                                                │ OUTPUT / Workspace      │
│   ☐ Temperature.tif   │                                                │ ---------------------   │
│ Tables                │                                                │ [Run] [Cancel]          │
│   Station summary     │                                                │ [Progress + Log]        │
├───────────────────────┴────────────────────────────────────────────────┴─────────────────────────┤
│ Status: coordinates | scale | selected features | active CRS | jobs | source attribution       │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- **الأصل:** Contents يسارًا، Tools يمينًا، Canvas وسطًا، وفق صورة ArcGIS Pro. يُسمح بعكس الجانبين يدويًا أو في وضع RTL مع استعادة تخطيط المستخدم السابق.
- **النوافذ الجانبية:** `Dockable`, `Resizable`, `Closable`, `Auto-hide`, ويمكن إظهارها مجددًا عبر View > Panels؛ يجب ألا تختفي أبدًا دون طريقة واضحة لاستعادتها.
- **استمرار التخطيط:** Save/Restore pane geometry + splitter sizes بين الجلسات ولكل مستخدم؛ أمر **Reset Layout**.
- **العرض الأوسط:** افتراضيًا Map (وليس PDF). تتعدد تبويبات Map/Attribute Table/Excel/Raster/Results/Help، ويمكن إغلاقها أو فتحها من قائمة واضحة.
- **الأدوات:** ثلاث عائلات أساسية: **Station/Network Climate Atlas** و**Climate Atlas at My Points** و**Raster Tools**؛ الأسماء النهائية تُستمد من الكود القديم بعد الجرد.
- **التبويبات داخل Contents:** Layers / Tables / Outputs مع مجموعات Input, Generated, Temporary؛ زر يمين لإظهار الجدول/التقريب للطبقة/خصائص/إزالة من المشروع (دون حذف الأصل).
- **الصور والأزرار والشعار:** احفظ هوية MIRSAD والشعار المتاح، بدون تعديل غير مطلوب لمصدر الملكية أو العلامة.

### 3.2 حالات التشغيل والشاشات

| الحالة | الواجهة المتوقعة |
|---|---|
| أول تشغيل بلا مشروع | نافذة ترحيب لإنشاء/فتح مشروع؛ Contents فارغ، ولا توجد طبقات وهمية |
| فتح مشروع | استعادة الطبقات ومساراتها وتبويبات العرض وتخطيط النوافذ، وتنبيه للملفات المنقولة/غير المتاحة |
| ملف طبقة نشط | يظهر في Contents، ويصبح متاحًا لاختيار Tool Input المناسب |
| تشغيل أداة | تبقى الواجهة مستجيبة؛ Progress وLog مفصلان؛ زر Cancel ينفذ إلغاءً حقيقيًا |
| انتهاء معالجة | النتائج تظهر في Contents وResults، وتُعرض الملفات القابلة للعرض بتبويبات مناسبة |
| تغيير أبعاد النافذة | ألواح مرنة وتدفق Scroll، بلا أزرار مقطوعة أو نصوص غير مقروءة |

## 4. إعادة بناء Add Data — **أعلى أولوية وظيفية**

### 4.1 المطلوب كتجربة مستخدم

زر **Add Data** ظاهر دائمًا في الشريط العلوي، ويدعم `Ctrl+O` أو اختصار موثق آخر غير متعارض. عند الضغط تظهر **نافذة واحدة واضحة**:

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Add Data                                     [Search datasets, layers, files...]    │
├─────────────────────────────┬────────────────────────────────────────────────────────┤
│ FAVORITES                   │ Folder / Database: D:\GIS\Climate_Database_2025.gdb   │
│ RECENT                      │ Name                  Kind         Geometry   CRS      │
│ PROJECT                     │ Arab_Countries_Grid   FeatureClass Point      ...      │
│ ├─ Databases                │ Temperature           FeatureClass Point      ...      │
│ └─ Folders                  │ Statistics            Table        None       ...      │
│ THIS PC                     │                                                        │
│ ├─ C:                       │ [Dataset details / preview / 1st N rows]               │
│ ├─ D:                       │                                                        │
│ └─ Network locations        │                                                        │
├─────────────────────────────┴────────────────────────────────────────────────────────┤
│ File type: [All supported data ▼]   [Add Selected] [Open Folder] [Cancel]            │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**هذا مستعرض GIS، وليس نظام File Open عادي:**
1. شجرة Drives / This PC / Project / Folder Connections / Databases / Recent / Favorites.
2. شريط مسار قابل للتحرير، Breadcrumbs، Back/Forward/Up، Search، Refresh، عرض Details/Icons.
3. لا يتوقف التصفح عند ملف `.gpkg` أو مجلد `.gdb`؛ عند دخوله تُعرض **الطبقات والجداول الموجودة داخله**، مثل نموذج ArcGIS Pro بالصورة الثالثة.
4. عرض `Name`, `Type`, `Geometry`, `CRS`, `Feature Count` إن كان متاحًا بسرعة، `Size`, `Modified`، ومعاينة الصفوف والبيانات الوصفية.
5. دعم **اختيار متعدد** للطبقات والجداول ثم `Add Selected`، والنقر المزدوج، والسحب والإفلات من Explorer إلى المشروع عند إمكان ذلك.
6. إظهار الملفات المدعومة **دون تصفية مناخية مسبقة**. عند عدم معرفة النوع، تظهر رسالة سبب عدم الدعم لا إخفاء مبهم للملف.
7. فتح ملف Excel يعرض **أوراق العمل**؛ يمكن إضافتها كجداول، ومع اختيار حقول X/Y وإسناد CRS يمكن تحويلها إلى طبقة نقاط دون تعديل الملف الأصلي.
8. استيراد مجلد `.gdb` ومعاينة Feature Datasets/Feature Classes وجداولها؛ يتميز Drive GDB بأنه مجلد حاوية، لا تُعرض ملفاته الداخلية الخام كطبقات عادية.
9. بعد الإضافة تنتقل الـLayer Reference إلى **Project Data Catalog** وتظهر في Contents وتصبح متاحة فورًا للأدوات.
10. جميع رسائل الفشل واضحة: غير مدعوم، الملف تالف، صلاحية قراءة، لا توجد طبقات، CRS غير معرف، مسار شبكة غير متصل؛ سجلات تفصيلية دون تجميد UI.

### 4.2 مصفوفة الصيغ

| الصيغة | فتح / استعراض | إضافة للمشروع | عرض | ملاحظات |
|---|---|---|---|---|
| `.gpkg` | نعم: جميع Vector layers والجداول | اختيار طبقة واحدة أو أكثر | Map/Table | الصيغة الجغرافية الأساسية داخل المشروع |
| `.gdb` | نعم: استعراض Feature datasets/classes والجداول بحسب إمكانات GDAL | نعم للطبقات المدعومة | Map/Table | القراءة أولًا، والكتابة/الإنشاء مشروطان باختبار driver والإصدار |
| `.shp` | نعم | نعم | Map/Table | التعامل مع مجموعة الملفات المصاحبة والترميز وCRS |
| `.geojson`, `.json` الجغرافي | نعم بعد التحقق | نعم | Map/Table | لا تفترض أن كل JSON هو GeoJSON |
| `.csv`, `.tsv` | نعم | جدول أو XY points | Table/Map | اختبار UTF-8 وWindows encodings والفواصل العشرية |
| `.xls`, `.xlsx` | نعم: كل Workbook وشيتاته | نعم | Excel-like table | البيانات المعروضة لا تُعدل الملف الأصلي دون Save As أو موافقة |
| `.tif`, `.tiff`, GeoTIFF | نعم | نعم | Raster/Map | تأكد من CRS وNoData وقنوات العرض |
| `.vrt` | إذا دعم GDAL | نعم | Map/Raster | التحقق من مراجع الملفات |
| `.sqlite`, `.db` | إذا كان GIS/Spatialite قابلًا للتفسير | بحسب driver | Map/Table | تحذير عند قواعد بيانات غير جغرافية |
| `.kml`, `.kmz`, `.gpkg.zip`, `.gdb.zip` | بعد اختبار القدرة الفعلية | حسب دعم Driver | Map/Table | إضافات مرحلة لاحقة حسب الأولوية |
| `.pdf` | منفصل عن Add Data GIS أو ضمن ملفات المشروع | وثيقة/نتيجة فقط | PDF tab | ليس بديلًا لعرض الخريطة |

**لا تعد بدعم كل امتداد دون اختبار فعلي على Windows**؛ اعرض في قائمة الصيغ ما نجح اختباره فقط، وباقي الامتدادات ممكن تُفعّل تباعًا.

### 4.3 وظائف Data Catalog المركزية

- نموذج موحد لكائنات `DataSource`, `Dataset`, `Layer`, `Table`, `Raster`, `ProjectLayerReference`، مع `id`, `uri`, `subdataset/layer_name`, `crs`, `schema`, `geometry_type`, `is_available`.
- لا تخلط **إضافة إلى المشروع** مع **نسخ إلى قاعدة بيانات المشروع**؛ الأمر الأول Reference غير متلف، والثاني Import/Copy اختيار صريح.
- Catalog لا يعيد فتح ملف Excel كاملًا لكل اختيار في أداة؛ يستعمل Metadata Cache قابلًا للتحديث.
- تحديث تلقائي منسق للقوائم عند إضافة/حذف/إعادة تسمية طبقة في Contents، ومنع اختيار Inputs من نوع غير مناسب.
- إذا فقد البرنامج مصدر ملف، احتفظ بالمرجع مع علامة Missing Source ووظيفة Relink بدل إزالته صامتًا.

## 5. محتويات المشروع (Contents) وتكاملها مع Tools

### 5.1 قواعد Contents

- عرض الطبقات الفعلية **فقط** بعد إضافتها أو إنتاجها، مع مفتاح Visibility ورمز لنوع الهندسة ومفتاح Legend/Group.
- تجميع: `Inputs / Working Layers / Analysis Results / Rasters / Tables / Excel Outputs`؛ يختار المستخدم مجموعات أو تبويبات العرض.
- القائمة السياقية: Open Attribute Table، Zoom to Layer، Select Features، Show Layer Properties، CRS Details، Export، Remove from Map، Open File Location.
- السحب لتغيير ترتيب الطبقات والرسم على الخريطة، إظهار أسماء المصادر وحالتها.
- طبقات النقاط وحدود الدراسة ليست تهيئة مسبقة ولا بيانات مصطنعة. عند عدم إضافتها، يظهر Tool Input فارغ مع **Select existing layer** و**Browse/Add Data**.

### 5.2 مثال تسلسل العمل المطلوب

1. أنشئ مشروعًا فارغًا، فتظهر الخريطة بلا طبقات مشروع.
2. اضغط **Add Data**، افتح مجلدًا أو GPKG أو GDB، واختر طبقة نقاط محطات + Polygon للدراسة.
3. اضغط Add Selected؛ تظهر الطبقتان مباشرة في Contents وعلى Map.
4. افتح **Climate Atlas at My Points**؛ قائمة Point Input تعرض الطبقة النقطية تلقائيًا وتستبعد Polygon؛ Input Mask تعرض الـPolygon فقط.
5. حدد إعدادات المخرجات ونظام الإحداثيات، ثم Run.
6. يملأ البرنامج النتائج داخل Workspace، ويضيف الطبقات الجديدة إلى Contents، ويعرض Workbook Excel بتبويب مستقل داخل المنتصف.
7. يمكن فتح الـWorkbook الناتج وتصدير نسخة دون تغيير أسماء الـSheets والحقول الأصلية.

## 6. صناديق الأدوات الثلاث (Toolbox / Wizard Engine)

### 6.1 التصميم الهيكلي

- لوحة جانبية بعنوان واضح **Tools / Geoprocessing**، قابلة للتحريك والتثبيت والإخفاء والتكبير.
- شجرة أدوات أعلى اللوحة: `Station Climate Atlas`, `Climate Atlas at My Points`, `Raster Processing`، وبقية الأدوات الحالية إن وجدت تظهر بعد جرد الكود.
- عند اختيار أداة تظهر Tabs/Sections: **Inputs**, **Data Source / Period**, **Parameters**, **Outputs**, **Advanced**, مع Help جانبي.
- لكل Parameter تعريف Schema: معرف ثابت، اسم مترجم، نوع (`point_layer`, `polygon_layer`, `raster_layer`, `crs`, `number`, `folder`, `enum`)، مطلوب/اختياري، قيمة افتراضية، التحقق، Tooltip، ارتباطه بالكود.
- المدخلات تُختار من Data Catalog أو Add Data، ومعاينة CRS والحجم/الحقول قبل التشغيل.
- إعدادات Station Atlas تستعمل **الكتالوج المضمن لمحطات الرصد** تلقائيًا دون تكليف المستخدم كل مرة باستيراد ملف محطات.
- الأدوات تتعامل مباشرة مع المدخلات الحالية في المشروع، وتسمح بملفات خارجية عند الحاجة.
- Run حقيقي، Cancel حقيقي، Clear/Reset parameters، Save Parameters/Load Preset؛ إظهار مدة التنفيذ وسجل التشغيل.

### 6.2 الاحتفاظ بخواص الـToolbox الأصلية

عند مراجعة الكود، تُسرد جميع قيم `Station Selection Mode`, `Country/Region`, `Custom IDs`, `Neighboring Halo (30 km)`, `Boundary Mask`, `Survey Points`, `Download Only`, `Sequential/Batch`, `Temporal Range`, `Interpolation`, `Output CRS`, `Raster Settings`, `Units`, `Reclassification`, `Output Naming` وغيرها. **لا تحذف الإعدادات الموجودة لأن النسخة الجديدة تبدو أبسط**؛ أخفِ المتقدم تحت Advanced مع الحفاظ على سلوكه.

### 6.3 سلوك الحقول عند تصغير اللوحة

- حدود عرض معقولة و`QScrollArea`/Scrollable Form وشرح Tooltips ونص ملتف عند الحاجة.
- أزرار `Run`, `Cancel`, `View Logs` تظل مرئية في Footer مثبت أسفل اللوحة أو قابلة للوصول دون قصّ.
- اختبر نوافذ 1280×720 و1366×768 و1920×1080، وشاشات Windows DPI بنسبة 100%/125%/150%/200%، واللغتين، والثيمين.
- إذا ضاقت المساحة، ينتقل محتوى Advanced إلى أقسام قابلة للطي بدل اختفاء الحقول بصمت.

## 7. كتالوج محطات الأرصاد المضمن (Offline-first Station Catalog)

### 7.1 التمييز المطلوب

**قائمة المحطات وتعريفاتها وخصائصها** شيء، و**سلاسل القياسات المناخية التاريخية** شيء آخر. ينبغي وضع كتالوج المحطات المعتمد فعليًا من المشروع ضمن التثبيت أو تهيئة أول تشغيل محلية إذا كان ترخيص إعادة التوزيع يسمح؛ بينما قياسات الطقس تُنزّل عند الطلب حسب المصدر والفترة.

### 7.2 آلية عمل آمنة

- `assets/station_catalog/` نسخة قراءة فقط/Seed مع Version وSchema وLicense وChecksum وSource Date.
- أول تشغيل ينسخ البيانات التي تحتاج تحديثًا إلى `AppData/MIRSAD/` أو مجلد بيانات مناسب قابل للكتابة، ولا يكتب داخل `Program Files`.
- Database Services تحمل الكتالوج مرة واحدة وتخدم أدوات المحطات والنقاط والمناخ؛ cache وإعادة استخدام، وفلترة دولة/شبكة/معرّف.
- عند العمل Offline يمكن استعراض المحطات والحدود المحلية وإنشاء مشروعات وتجهيز المدخلات؛ **لا يُدَّعى تنزيل قياسات من السيرفر دون اتصال**.
- `Update Catalog` اختياري للتحقق من توفر نسخة أحدث عبر مصدر موثوق، ولا يعيد تنزيل الكتالوج كل مرة عند بدء أداة.
- حماية بيانات المستخدم والمخرجات من عملية Update أو Uninstall، والتأكد من جواز إعادة توزيع الكتالوج ضمن شروط المصدر.

## 8. أنظمة الإحداثيات والمساقط — مدمجة مع التطبيق

### 8.1 متطلبات CRS Browser

- تضمين PROJ runtime و`proj.db` ومعرّفات CRS المدعومة فعليًا من نسخة PROJ المصاحبة، مع إمكانية البحث **Offline**.
- شاشة `Choose Coordinate Reference System` تحتوي: `Search by Name or EPSG`, `Favorites`, `Recent`, `Geographic / Projected`, `Authority Code`, `Area of Use`, `Units`, `Datum`, `Axis Order`, `WKT/PROJ` عند الحاجة.
- الاختيار من: Project CRS، CRS الطبقة الأصلية، أو CRS من القائمة، مع تنبيه `Unknown CRS`.
- المستخدم يستطيع إضافة WKT مخصص مع Validation؛ وليس مجرد Dropdown بأرقام EPSG محدودة.
- يمكن اقتراح UTM Zone حسب منطقة الدراسة **بعد فحص خطوط الطول ومساحة النطاق**؛ لا تثبت زون واحدة لمصر أو العالم.
- عرض فرق واضح بين `Assign CRS` (إسناد مرجع دون تغيير الإحداثيات) و`Reproject` (تحويل الإحداثيات فعلًا)، مع تأكيد للتصرفات المؤثرة.
- عند عدم توفر Datum Transformation Grid اللازمة لدقة محددة، تحذير وإيضاح البديل ودقته وعدم الادعاء أن جميع التحويلات الدقيقة تعمل Offline بمجرد وجود `proj.db`.
- تخزين مرجع CRS في المشروع وفي GeoPackage/GeoTIFF وشكل المخرجات، والتحقق من Order X/Y ووحدات المسافة.

### 8.2 اختبارات مطلوبة

- يعمل بحث `EPSG:4326` و`EPSG:3857` دون اتصال.
- إضافة GPKG بطبقة مسقط مختلف يؤدي إلى On-the-fly Reprojection للعرض **من دون تغيير إحداثيات الملف الأصلي**.
- التحويل إلى CRS مخرجات اختاره المستخدم يغيّر الإحداثيات المحفوظة بطريقة صحيحة، ويحافظ على `NoData` وDatum قدر الإمكان، مع توثيق طريقة التحويل.
- النوافذ العربية تترجم تسميات الأزرار، لكن أكواد EPSG وأسماء الإسقاط الأصلية العلمية يجوز إبقاؤها لأسباب مرجعية.

## 9. الخرائط الأساسية: إزالة الاعتماد على خدمات مفاتيح API والرسوم

- **الافتراضي:** OpenStreetMap، مع بطاقة Attribution دائمة، وcache واحترام Tile Usage Policy وعدم تنزيل مناطق كاملة مسبقًا من خوادم OSM العمومية.
- **Esri:** خيار ثانٍ **فقط إذا ثبت في وثيقة تراخيص المشروع أن الخدمة المحددة وممارسة الاستخدام المقررة مسموحتان ولا تتطلبان حسابًا أو مفتاح API/دفعًا من المستخدم في هذا السياق**. إذا كان الأمر غير مؤكد أو يتطلب هوية/مفتاحًا مدفوعًا: أخفِه أو عطّله مع توثيق السبب، ولا تتحايل على الوصول.
- إزالة أي خدمة تتطلب API Key أو Access Token مدفوعًا من قائمة Basemap الافتراضية، بدل إظهار زر لا يعمل.
- يجب تشغيل الواجهة والطبقات المحلية **حتى عند انقطاع الإنترنت**؛ الخريطة الأساسية الشبكية حينها ليست شرطًا لعرض الطبقات.
- دعم خلفية `None / Solid Color` لعرض GIS بلا شبكة، وعدم ربط نجاح المعالجة المناخية بخادم tiles.
- لا تخلط مصدر OSM المجاني المفتوح بترخيص خوادم tiles؛ ولا تعتبر Esri مفتوح المصدر أو مجانيًا دون تحقق.

**مصادر رسمية للتوثيق والتحقق:**
- OSM Tile Policy: <https://operations.osmfoundation.org/policies/tiles/>
- Esri service terms: <https://www.esri.com/en-us/legal/terms/web-site-service>
- Esri licensing: <https://location.arcgis.com/help/terms-of-use/>

## 10. اللغات والاتجاهات والمساعدة

### 10.1 Locales

- `en-US` الافتراضي لأول تشغيل؛ `ar-EG` اختياري ويُحفظ للمرة التالية.
- جميع نصوص UI من Translation Catalog: Menus, dialogs, tooltips, table headers, status bar, errors, validation, progress, About, Help, installers حيث أمكن.
- **ممنوع** النصوص المزدوجة مثل `المخرجات / Outputs` في أي واجهة إنتاجية. English only في الواجهة الإنجليزية، Arabic only في العربية إلا مصطلحات تقنية لا تُترجم وبيانات المصدر.
- RTL صحيح للواجهة العربية، LTR للإنجليزية؛ محاذاة أرقام EPSG ومسارات الملفات والرموز والإحداثيات باتجاه طبيعي مهما كانت لغة العرض.
- **لا تترجم أسماء الحقول أو ملفات التصدير أو Sheets أو أرقام المتغيرات العلمية**؛ ثبات هذه العناصر شرط لتطابق مخرجات الـToolbox القديمة.
- عند تغيير اللغة أثناء التشغيل، يُفضّل إعادة ترجمة النوافذ الحالية فورًا؛ إذا كان بعض عناصر Qt يتطلب إعادة فتح حوار، إبلاغ المستخدم بوضوح بدون فقدان العمل.

### 10.2 دليل مستقل بكل لغة

- `Help > User Guide` يُظهر دليلًا **باللغة المختارة فقط**، عربيًا أو إنجليزيًا.
- دليلان متكافئان `docs/help/en/` و`docs/help/ar/` بموضوعات: Starting Project، Add Data، CRS، Station Wizard، Point Wizard، Raster، Tables/Excel، Export، Troubleshooting، License/About.
- أمثلة وصور توضيحية خاصة بكل واجهة إذا تختلف مواضع العناصر، لا دليل مخلوط اللغتين.

## 11. مشكلة Light / Dark الحالية — إصلاح جذري

- لا يكفي تبديل CSS للنصف الظاهر من النافذة. يجب توحيد Theme Tokens/Palette لكل `QWidget` والـdialogs والـpopups والـmenus والـcombo boxes والـtooltips والـQTreeView/QTableView وPDF/Excel viewers.
- إعادة فحص hard-coded colors، ألوان النص والخلفية، حالات Hover/Selected/Disabled، Borders، Scrollbars، Tabs، Progress Bar، وNative file dialogs المستخدمة.
- اختبار فتح **Add Data** وفتح قائمة Context Menu داخل Contents في Light ثم Dark؛ كل عنصر يلتزم النمط المختار، بما فيه Popups غير الواضحة في الصورة الحالية.
- تجنب خلفية داكنة بنص داكن أو خلفية فاتحة بنص أبيض، وعدم حفظ اختيار الثيم في بعض Components دون أخرى.
- الثيم مستقل عن اللغة؛ جميع التركيبات الأربع مطلوب اختبارها: EN Light / EN Dark / AR Light / AR Dark.

## 12. الخرائط والجداول والنتائج

- Map toolbar: Pan, Zoom In/Out, Full Extent, Zoom to Layer, Identify, Select, Clear Selection, Measure (إن دُعم بدقة), Coordinate Display, Map CRS.
- Attribute table للطبقات باستعراض صفوف كبير عبر Pagination/Virtual Model دون تحميل كامل الملفات في RAM.
- ملف Excel الناتج يظهر في Tab Excel/Spreadsheet مع قائمة Sheets، صفوف/أعمدة وHeader ثابت، عمليات Preview/Export/Open External Application اختيارية.
- Raster preview ببيانات Min/Max/NoData/CRS ونطاق عرض ومفتاح Legend عند الحاجة.
- Results pane أو مجموعات داخل Contents تفصل Vector/Raster/Tables/Excel وExecution Logs، مع فتح الملف النهائي أو مجلده.
- PDF viewer تبويب اختياري لملف طلبه المستخدم أو تقرير ناتج، وليس **اللوحة الرئيسية الفارغة** عند بدء التطبيق.

## 13. الحفاظ الصارم على مخرجات Arc Toolbox الأصلية

### 13.1 Data Contract

لكل أداة أصلية أنشئ ملف `docs/legacy_output_contracts/<tool_id>.md` يتضمن:

| ما يجب توثيقه | طريقة التحقق |
|---|---|
| File names/folders | قارن المسارات النسبية ونمط التسمية |
| Excel workbook & sheet names | تطابق حرفي أسماء Sheets وترتيبها |
| Column names & order | تطابق تام بما فيها حالة الأحرف والمسافات |
| Data types/precision/nulls | تحقق من التاريخ والقيم والأرقام والفواصل |
| Worksheet styles/formulas إن وُجدت | تحقق من التنسيق والصيغ إذا كانت جزءًا من العقد |
| Database schema | أسماء Feature Classes/Tables/Fields، العلاقات والمعرّفات والفهارس المهمة |
| Geometry / CRS | نوع الهندسة والإسقاط ودقة الإحداثيات والحقول المكانية |
| Units and calculations | نفس القواعد/المعادلات/الفلاتر/الحدود الزمنية |
| Raster outputs | نفس Band Count وCRS وPixel Alignment وNoData والقيم ضمن tolerance مبرر |
| Logs/report metadata | مصدر البيانات وإعدادات التشغيل ومعلومات الجودة |

### 13.2 Golden Tests

1. خذ **عينات صغيرة مرجعية من تشغيل الـToolbox القديم** (أداة محطات، أداة نقاط، أداة Raster إن وجدت) من بيئة معروفة الصواب.
2. احتفظ بالمدخلات والمخرجات المرجعية وHashes وManifest؛ لا تعدّل المرجع.
3. نفّذ نفس الـInputs بالإصدار الجديد.
4. قارن مستوى **دلالة البيانات** وليس bytes فقط؛ ملفات `.xlsx` و`.gpkg` قد تختلف معلوماتها الداخلية أو metadata دون تغير النتائج.
5. أظهر تقريرًا واضحًا لأي انحراف: ورقة مفقودة، عمود جديد، اختلاف ترتيب، CRS، عدد Features، قيم مختلفة، Precision؛ وحدد أسباب الاختلاف.
6. يجب ألا تُقبل الهجرة إلى البرنامج الجديد لأي أداة قبل اجتياز Golden Tests أو اعتماد اختلاف موثّق من صاحب المشروع.
7. عند تغيير صيغة التخزين من `.gdb` إلى `.gpkg` يجب أن تبقى **البنية الدلالية والحقول والقيم والطبقات** مكافئة؛ التمثيل الثنائي ليس بالضرورة مطابقًا، ويجب توفير Export GDB إذا كان شرطًا لا يمكن الاستغناء عنه وكانت بيئة GDAL تدعمه.

## 14. قواعد البيانات والتصدير

- **مشروع جديد:** اختيار مجلد Workspace؛ إعداد `project.gpkg` افتراضي، و`input/`, `output/`, `logs/`, `cache/`؛ يمكن فتح قاعدة بيانات خارجية دون نسخها.
- **Create GeoPackage:** اسم ومسار، CRS للطبقات الجديدة، Add Vector Layer، Add Table، Import Features، Export Selected، Validate Geometry.
- **Export Formats:** GeoPackage وShapefile وGeoJSON وExcel وCSV وGeoTIFF وفق نوع البيانات؛ FileGDB عند التحقق من دعم GDAL/OpenFileGDB وقيود الترخيص والإصدار.
- **FileGDB `.gdb` ليس ملفًا مفردًا:** يعامله المستعرض كحاوية Directory، ويتيح رؤية الطبقات والجداول بدلاً من عرض ملفات `.gdbtable` الخام للمستخدم.
- قبل كتابة نتيجة فوق ملف موجود يجب عرض `Overwrite / Create new / Cancel`، ولا يُسمح بمحو المخرجات لمجرد تشغيل Wizard ثانية.
- دعم ملفات عربية ومسارات طويلة وأقراص شبكة، مع فحص الصلاحيات وإشعار واضح عند الإخفاق.

## 15. عن مرصاد (About) وهوية التطبيق

تبويب **About** الحالي لا يجب أن يحتل مساحة مركزية كأنه أداة GIS. الأفضل نقله إلى `Help > About MIRSAD` أو حوار مستقل يحتوي:

- الشعار الرسمي واسم `MIRSAD Desktop` والإصدار الفعلي ورقم البناء/Commit.
- اسم المطور **وفق البيانات الرسمية الموثقة بالمستودع**، لا اختراع جهة أو بريد إلكتروني.
- وصف مختصر للبرنامج وروابط Documentation وGitHub وLicenses وPrivacy/Data Sources.
- مكونات مفتوحة المصدر وتراخيصها وAttribution لخدمات الخرائط عند استخدامها.
- `Copy Diagnostics`: نسخة نظام التشغيل، إصدار التطبيق، GDAL/PROJ ومكان Logs **دون كلمات مرور أو مفاتيح API**.

## 16. خطة التنفيذ حسب الأولوية والاعتماديات

### المرحلة 0 — تدقيق وحفظ نسخة مرجعية (P0: قبل أي تغيير)

**المهام:**
- جمع شجرة المشروع، تحديد نوع واجهة البرنامج الحالية: Web wrapper أم PySide6/PyQt أم غيرها.
- جرد ملفات `.pyt`, `.py`, إعدادات الأدوات، المحركات، Data Sources، DB، مكونات CSS/Qt، Windows packaging.
- تدقيق مدخلات/مخرجات Toolbox وأساليب حساب المحطات والاستيفاء، وتحديد source of truth.
- تجميع عينات تشغيل صحيحة من النسخة القديمة؛ إعداد Golden fixtures.
- عمل Git branch آمن وCI أساسي وملفات `docs/LEGACY_AUDIT.md`, `docs/MIGRATION_MATRIX.md`.

**شرط الانتقال:** قائمة الملفات والتبعيات وContract أولي لكل أداة وتقرير مواطن المخاطرة.

### المرحلة 1 — مشروع Qt أصيل وهيكل النوافذ (P0)

**المهام:**
- اختيار Map Engine بعد PoC وADR، وفصل App Services عن GUI.
- بناء Shell وDocks وContents/Tools/Canvas والـToolbar وشريط الحالة.
- حفظ تخطيط المستخدم وإعادة ضبطه، وجعل Map Tab هو الافتتاحي.
- تطبيق EN default، Translation Catalogs، ودليل عربي/إنجليزي أولي.
- توحيد Light/Dark عبر كل النوافذ والقوائم.

**شرط الانتقال:** نافذة قابلة للتغيير والطي والتحريك، واختبارات عرض للّغتين والثيمين وأحجام الشاشة من دون عناصر مختفية.

### المرحلة 2 — Add Data + Data Catalog + CRS (P0، قبل توصيل الأدوات)

**المهام:**
- إنشاء Browser بواجهته الكاملة من Drives إلى Folder/GPKG/GDB/Excel sheets.
- Input adapters واكتشاف sublayers والجداول/CRS والمعاينة وتعدد الاختيارات.
- Data Catalog للمشروع وربطه بـ Contents و Map، وإدارة الـMissing Sources.
- CRS Picker Offline مع `proj.db`, EPSG search, layer/project/output CRS.
- استيراد نقاط من Excel/CSV عبر XY fields مع اختيار CRS.

**شرط الانتقال:** **Add Data → Contents → Map/Table** يعمل فعليًا لكل صيغة P0 دون أي معالجة مناخية؛ ويستطيع المستخدم تصفح GPKG/GDB من الداخل.

### المرحلة 3 — ربط ثلاث الأدوات بالطبقات والكتالوج (P0/P1)

**المهام:**
- تكوين Parameter schemas للـStation وPoint وRaster tools مع فحص أنواع المدخلات.
- تحميل نسخة station metadata catalog محلية تلقائيًا إن سمحت المصادر والترخيص.
- تفعيل اختيار الطبقات من Contents/Project Catalog، وإدخال Boundary Mask/Point Layer.
- فصل عمليات التنزيل/التحويل عن UI وتشغيل العمال بProgress/Cancel/Logs.
- توصيل النواتج إلى GeoPackage وExcel وRaster مع Results pane.

**شرط الانتقال:** تجربة كاملة على مشروع صغير تبدأ بـ Add Data أو اختيار المحطات وتنتهي بملفات سليمة وتبويبات نتائج.

### المرحلة 4 — مطابقة مخرجات Arc Toolbox الأصلية (P0 قبل Release)

**المهام:**
- Golden tests لكل أداة؛ مطابقة Excel، أسماء Sheets والحقول، GeoPackage/GDB geometry، Raster.
- مقارنة الإعدادات المتقدمة ووحدات القياس ومعالجة Null/Timezones/CRS.
- تصحيح الفروق بلا إفساد المراجع، وتوليد تقارير توافق لكل أداة.

**شرط الانتقال:** قبول تقارير التوافق وتحقيق baseline المحدد لكل أداة.

### المرحلة 5 — الجودة والتثبيت والإصدار (P1)

**المهام:**
- Stress tests: طبقات كثيرة، ملفات Excel كبيرة، كثافة محطات، انقطاع اتصال، Cancel، DPI عالي.
- بناء Windows Setup/Uninstall وضم ملفات PROJ/Drivers وشعار MIRSAD.
- ضمان عدم حذف المشروعات/قواعد البيانات عند إلغاء التثبيت.
- بناء GitHub workflow للاختبارات والتجميع، وVersion/Changelog/Help ثنائي اللغة.

**شرط الانتقال:** تثبيت نظيف على جهاز Windows لا يحتوي ArcGIS أو Python، ونجاح import/open/run/export/uninstall مع بقاء بيانات المستخدم.

## 17. Backlog جاهز للتوزيع على مهام Codex

| ID | أولوية | مهمة | اختبار قبول مختصر |
|---|---|---|---|
| UI-01 | P0 | Native window/dockable panes | سحب/طي/إعادة إظهار Contents وTools وحفظ المواضع |
| UI-02 | P0 | Default Map tab and status bar | لا يُفتح PDF فارغ تلقائيًا |
| UI-03 | P0 | i18n كامل EN/AR | لا نصوص مزدوجة/مختلطة إلا Technical IDs |
| UI-04 | P0 | Light/Dark tokens and regression | كل popup/menu/dialog متناسق في أربع حالات |
| DATA-01 | P0 | Add Data tree & navigation | يفتح المجلدات وDrive/GPKG/GDB |
| DATA-02 | P0 | Read GPKG/GDB sublayers | تظهر جميع الطبقات والجداول داخل الحاوية |
| DATA-03 | P0 | Excel/CSV sheets + XY import | معاينة Sheets وإضافة جدول وتحويل إلى Points |
| DATA-04 | P0 | Project Data Catalog | الطبقة تظهر في Contents وقائمة Tool Input بدون Browse آخر |
| DATA-05 | P0 | No phantom layers | المشروع الفارغ لا يحتوي Layer وهمية |
| CRS-01 | P0 | Embedded PROJ catalog | بحث EPSG Offline، CRS display/reproject صحيح |
| MAP-01 | P0 | Native GIS map canvas | رسم طبقات متباينة CRS وتحديد/تكبير متاح |
| MAP-02 | P1 | Allowed basemaps | OSM مع Attribution وEsri مشروط بالترخيص |
| TOOL-01 | P0 | Three tool parameter adapters | Point يرفض Polygon والعكس؛ إظهار Required Errors |
| TOOL-02 | P0 | Bundled station catalog | تظهر محطة من Metadata Offline دون تنزيل متكرر |
| TOOL-03 | P0 | Workers and output registration | progress/cancel وظهور النتائج والملفات |
| LEG-01 | P0 | Golden data contracts | Excel columns/sheets/values وDB match baseline |
| LEG-02 | P0 | Raster parity | CRS/pixel/no-data/calculations حسب المعايير المرجعية |
| DOC-01 | P1 | About + bilingual Help | English help عند الإنجليزية، Arabic help عند العربية |
| DEP-01 | P1 | Windows Setup & Uninstall | عمل بلا ArcGIS وبدون فقد ملفات المشروع |

## 18. Acceptance Scenarios — سيناريوهات اختبار نهائية

### AC-01 — بداية نظيفة

**Given** تطبيق جديد بلا Project  
**When** أفتح MIRSAD للمرة الأولى  
**Then** اللغة إنجليزية وMap هو التبويب الأساسي وContents فارغ، وتوجد أدوات قابلة للفتح، ويمكن بدء مشروع دون طبقات مسبقة.

### AC-02 — تصفح GeoPackage متعدد الطبقات

**Given** ملف `.gpkg` يحوي `Stations` Points و`Study_Area` Polygon و`Statistics` non-spatial table  
**When** افتحه من Add Data  
**Then** تظهر العناصر الثلاثة بتصنيفها ونوعها وCRS، ويمكن إضافة اثنين أو الثلاثة إلى المشروع.

### AC-03 — استعراض File Geodatabase

**Given** `Climate_Database_2025.gdb` يحوي Feature Classes `Arab_Countries_Grid_Points`, `Temperature`  
**When** أفتح `.gdb` في Add Data  
**Then** أرى كليهما كطبقات قابلة للاختيار، لا كملفات داخلية مبهمة، وأستطيع إضافتها إلى Contents.

### AC-04 — اختيار مدخلات من Contents

**Given** Points + Polygon ضمن Contents  
**When** أفتح Point Climate Atlas  
**Then** قائمة Point Input تعرض النقاط فقط، وقائمة Mask تعرض الـPolygon فقط؛ كما توجد إمكانية Add Data من داخل حقل المدخل.

### AC-05 — Excel متكامل

**Given** ملف `.xlsx` به Sheets متعددة  
**When** افتحه وأضيف شيتًا للمشروع  
**Then** يظهر في Tables ويمكن عرضه في تبويب، ويمكن تحديد XY وإنشاء Point Layer مع اختيار CRS؛ لا تتبدل أسماء الأعمدة تلقائيًا.

### AC-06 — تكافؤ النواتج

**Given** بيانات مرجعية من Toolbox الأصلية وإعدادات متطابقة  
**When** أشغل نظيرها في MIRSAD الجديد  
**Then** يظهر تقرير نجاح أو فروق موثقة وتطابق Names, Sheets, Fields, Formulas/Formats عند لزومها، قيم محطات ورستر وCRS وفق Baseline.

### AC-07 — Offline CRS

**Given** لا يوجد اتصال إنترنت  
**When** أفتح Choose CRS وأبحث عن EPSG code  
**Then** يظهر CRS من قاعدة PROJ المضمنة ويمكن اختياره، بينما أي تحويل يتطلب Grid غير متاح يعلن ذلك صراحة.

### AC-08 — جميع أوضاع اللغة والثيم

**Given** العربية أو الإنجليزية وLight أو Dark  
**When** أفتح Add Data والقوائم والـWizards وHelp وAbout وجداول النتائج  
**Then** لا تظهر مساحة بثيم معاكس، ولا عبارات مزدوجة عربية/إنجليزية، وتكون عناصر التحكم واضحة ومقروءة.

### AC-09 — تصغير مساحة الأدوات

**Given** نافذة 1280×720 وDPI 150%  
**When** أضيق Tools ثم أوسعه أو أحركه أو أخفيه  
**Then** لا يفقد المستخدم أي Parameter أو زر Run؛ يوجد تمرير واستعادة عبر القائمة، ويتذكر التخطيط.

### AC-10 — مشروع مستقل مثبت على جهاز نظيف

**Given** Windows x64 بلا Python ولا ArcGIS  
**When** أنصب MIRSAD وأستورد GPKG وأشغل أداة محلية ثم Uninstall  
**Then** تعمل وظائف GIS الأساسية ويُحافظ على مجلدات مشروعات المستخدم وملفات النتائج.

### AC-11 — تحميل بدون تكرار

**Given** كتالوج المحطات مثبت ومفهرس ومحلي  
**When** أشغل Wizard محطات مرتين وأختار نفس الدولة  
**Then** يستخدم الكتالوج المحلي في المرتين، ولا يعاد تنزيله بلا سبب، وتنزيل القياسات التاريخية يحدث فقط عند الطلب.

### AC-12 — انقطاع الخريطة الأساسية

**Given** خادم Tile غير متاح  
**When** أفتح مشروعًا فيه طبقات محلية  
**Then** تظل الطبقات مرئية وتعمل الأدوات ولا يتجمد التطبيق، ويظهر تنبيه شبكي غير معطل للعمل.

## 19. مخرجات يجب أن يسلمها الوكيل في كل مرحلة

- `docs/LEGACY_AUDIT.md` و`docs/MIGRATION_MATRIX.md` بعد فحص فعلي للكود.
- `docs/ADR-001-MAP-ENGINE.md` يتضمن المفاضلة الفنية وقرارها.
- ملفات تنفيذ الواجهة والخدمات واختباراتها، دون العبث بالأصل.
- `docs/COMPATIBILITY_REPORT.md` بتفاصيل التكافؤ مع Golden tests؛ لا يكفي القول «يعمل».
- سجل واضح: Changed Files, Commands Run, Test Results, Remaining Limitations, Next Step.
- صور من واجهات الأربع حالات وعرض Add Data على GPKG وGDB وExcel؛ لقطات حقيقية من التطبيق لا نماذج وهمية.
- دليل استعمال لكل لغة، وقائمة تراخيص مكتبات/مصادر/خدمات الخرائط.
- Windows Installer قابل للاختبار عندما تصل مرحلة البناء وليس قبلها.

## 20. هيكل مجلدات مقترح داخل المستودع القائم

```text
MIRSAD_Repository/
├─ legacy_toolbox/                 # النسخة الأصلية كما هي أو مراجع إلى مكانها الحالي
├─ MIRSAD_Desktop/
│  ├─ app/
│  │  ├─ shell/                     # MainWindow, Docks, Layout persistence
│  │  ├─ ui/                        # Add Data, Tool panes, dialogs, tables, Help, About
│  │  ├─ i18n/                      # en, ar translations
│  │  ├─ themes/                    # light, dark unified tokens
│  │  ├─ catalog/                   # Project Data Catalog + browse model
│  │  ├─ io/                        # OGR/GDAL/Excel/CSV adapters
│  │  ├─ map/                       # CRS-aware Map canvas and layers
│  │  ├─ crs/                       # PROJ integration and picker
│  │  ├─ stations/                  # Station catalog and metadata
│  │  ├─ tools/                     # station, point, raster tools
│  │  ├─ engine/                    # Tasks, workers, pipeline, output parity
│  │  └─ storage/                   # Project manifest and GeoPackage
│  ├─ assets/
│  │  ├─ branding/                  # شعار مرصاد الأصلي
│  │  └─ station_catalog/           # Seed data licensed for redistribution
│  ├─ resources/                    # packaged PROJ data & Qt resources
│  ├─ tests/
│  │  ├─ fixtures/                  # test-only synthetic data / references
│  │  ├─ integration/
│  │  └─ golden/                     # baseline comparisons
│  ├─ installer/
│  └─ pyproject.toml
├─ docs/
│  ├─ MIRSAD_DESKTOP_REDESIGN_EXECUTION_PLAN_V2.md
│  ├─ reference_images/
│  ├─ legacy_output_contracts/
│  ├─ help/en/
│  ├─ help/ar/
│  ├─ LEGACY_AUDIT.md               # after inspection
│  ├─ ADR-001-MAP-ENGINE.md         # after PoC
│  └─ COMPATIBILITY_REPORT.md       # after tests
└─ .github/workflows/
```

> **لا تعِد ترتيب المستودع القائم آليًا** كي يطابق هذه الشجرة؛ عدّلها وفق نتيجة التدقيق. الأولوية الحفاظ على تاريخ Git والمسارات التي يعتمد عليها الـToolbox الأصلية.

## 21. مخاطر وقرارات تحتاج فحصًا لا تخمينًا

1. **هل الواجهة الحالية HTML؟** لا نجزم اعتمادًا على الصورة؛ افحص ملفات `web`, `QtWebEngine`, `pywebview`, `Electron`, `PySide`, `PyQt` وقرار التغليف. إذا كانت Web wrapper، اكتب Migration Plan إلى Qt Widgets أو قرارًا مبررًا، ولا تنفذ إعادة تصميم مكلفة بلا دليل.
2. **PyQGIS والترخيص:** قد يقدم رسمًا جاهزًا قويًا لكنه يزيد حجم المثبت ومتطلبات الحزم وله آثار GPL وتوافق Python/Qt؛ احسم عبر PoC وقرار مكتوب.
3. **Qt licensing:** Qt for Python متاح بشروط LGPL/GPL أو رخصة تجارية؛ راجع الالتزامات عند التوزيع.
4. **Esri basemap:** شروط الخدمة والاستخدام تختلف حسب الخدمة والحساب وحجم الاستهلاك؛ لا تضمّن خدمة مخالفة لأن URL متاح.
5. **محطات الطقس:** راجع مصدر Metadata وشروط إعادة توزيع القائمة، وفرق بينها وبين أرشيف القياسات الكبير.
6. **GDB writing:** قدرة `OpenFileGDB` مرتبطة بإصدار GDAL ودعم خصائص الطبقات؛ انقل إلى GPKG افتراضيًا ولا تَعِد بتطابق ESRI-specific behavior دون اختبار.
7. **ملفات Grid الدقيقة:** كثير من CRS المعروفة موجودة في `proj.db`، بينما ملفات transformation grids قد تكون مستقلة؛ عالج ذلك صراحة.
8. **الهجرة الحسابية:** قد يكون بداخل ArcPy عمليات Interpolation/Projection/Field Calculation تختلف في السلوك عن GDAL/SciPy؛ Golden Tests شرط أساسي.
9. **Performance:** لا تحمّل جميع سجلات Excel أو ملايين Features في Widgets مباشرة؛ التصفح عبر models/virtualization وتدرج رسم الخرائط.

## 22. البرومبت النهائي الجاهز للصق في Codex

> **انسخ النص التالي كما هو إلى Codex بعد وضع هذه الوثيقة والصور في المستودع:**

```text
You are the lead desktop GIS engineer for MIRSAD Desktop.
Read docs/MIRSAD_DESKTOP_REDESIGN_EXECUTION_PLAN_V2.md in full, along with
its docs/reference_images/ screenshots, and examine the existing repository.
Treat the legacy ArcGIS Toolbox's outputs and data schemas as compatibility
contracts. Do not delete, rewrite, or move legacy assets before auditing them.

First deliver Phase 0: inventory the repository, identify current GUI technology,
GIS and file drivers, tool input/output contracts, station data sources, packaging,
branding, i18n, themes, and existing tests. Document findings, evidence paths,
and the migration matrix. Then implement the smallest verifiable Phase 1/2 slice:
a native dockable main window, robust GIS Add Data browser that opens folder,
GeoPackage layers, FileGDB feature classes and Excel sheets, and a shared project
Data Catalog wired into Contents and tool inputs. English must be default,
Arabic must be separately localized, and Light/Dark must be consistent.

Do not claim completed features without running tests or a working demonstration.
Use an ADR/PoC to select the map engine, assess Qt/PyQGIS licensing, respect OSM
usage rules and verify any Esri basemap terms. Bundle PROJ CRS catalog for offline
search and clearly distinguish CRS definitions from unavailable datum grids.

Implement incrementally on a branch with tests and compatibility reports. Preserve
Excel workbook/sheet names, exact columns, ordering, calculations, DB schemas,
CRS and raster semantics from golden legacy results. Ask for missing golden
samples only if required after inspecting all available local resources.

At each stage report: audit results, modified files, tests executed, actual
limitations, and next smallest implementation step. No fake layers, no false
success messages, no hidden UI controls at small window sizes.
```

## 23. المراجع التقنية الرسمية (للتنفيذ والمراجعة)

- Qt for Python / PySide6: <https://doc.qt.io/qtforpython-6/>
- Qt for Python licensing: <https://doc.qt.io/qtforpython-6.10/commercial/index.html>
- QGIS Map Canvas embedding: <https://github.com/qgis/QGIS-Documentation/blob/master/docs/pyqgis_developer_cookbook/canvas.rst>
- QGIS GPL: <https://qgis.org/license/>
- GDAL GeoPackage: <https://gdal.org/en/stable/drivers/vector/gpkg.html>
- GDAL OpenFileGDB: <https://gdal.org/en/stable/drivers/vector/openfilegdb.html>
- PROJ resources / proj.db: <https://proj.org/en/stable/resource_files.html>
- OpenStreetMap Tile Usage Policy: <https://operations.osmfoundation.org/policies/tiles/>
- Esri site and services terms: <https://www.esri.com/en-us/legal/terms/web-site-service>

---

**خلاصة القرار التنفيذي:** يبدأ التطوير بتدقيق الكود الحالي ووضع Baseline لمخرجاته، ثم بيئة Qt Desktop ذات Contents/Tools قابلة للطي مع Map Canvas فعلي، ثم **Add Data** الموحّد وتصفح GPKG/GDB/Excel، ثم كتالوج CRS ومحطات Offline، ثم توصيل الأدوات الثلاث واختبار التطابق مع الـToolbox القديمة، وأخيرًا التغليف والتوزيع. **لا يُعد أي انتقال ناجحًا إذا غيّر مخرجات Excel/Database أو أفقد المستخدم الوصول إلى طبقات مشروعه أو وضع الألوان/اللغة الصحيح.**
