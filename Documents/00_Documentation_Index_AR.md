# 00. الفهرس الشامل للتوثيق وخارطة الطريق المعمارية للمشروع
## منظومة مِرصاد (MIRSAD) للأطالس المناخية وقواعد البيانات الجغرافية
### Multi-source Integrated Reanalysis & Surface Atlas Database
#### الدليل المرجعي العلمي والرياضي والتقني الشامل

**اسم المنصة:** **مِرصاد (MIRSAD)**  
**المؤلف:** أحمد إبراهيم (Ahmad Ibrahim) — أخصائي نظم المعلومات الجغرافية والمناخ  
**البريد الإلكتروني:** ahmadibrahim.geo@gmail.com  
**آخر تحديث:** أكتوبر 2026 (الإصدار المؤسسي الموحد 2.0)  

---

## 1. الملخص التنفيذي وأهداف المنصة

تُعد **منظومة مِرصاد (MIRSAD - Multi-source Integrated Reanalysis & Surface Atlas Database)** منصة برمجية وجغرافية مؤتمتة رفيعة المستوى متوافقة كلياً مع بيئتي **ArcGIS Desktop (ArcMap 10.8)** و **ArcGIS Pro (2.8+ / 3.x)**. تهدف المنصة إلى استخلاص ومعالجة وتحليل السلاسل الزمنية المناخية، وتركيب المعدلات المناخية المعيارية لـ 30 عاماً (مثل خط الأساس المعتمد من المنظمة العالمية للأرصاد WMO للفترة 1991–2020 والفترة المعيارية 1996–2025)، وذلك عبر **18 موديولاً مناخياً وحيوياً متخصصاً** تضم **258 مؤشراً مناخياً علمياً** (114 مؤشراً سنوياً وفصلياً وبيومناخياً + 144 مؤشراً شهرياً مناخياً) إلى جانب **12 حقلاً للميتاداتا وتتبع المعالجة** (بإجمالي 270 حقلاً كلياً).

من خلال التكامل الذكي بين الرصد الفضائي للأقمار الصناعية (NASA CERES)، ونماذج إعادة التحليل الجوي العالمية (NASA MERRA-2, ECMWF ERA5, ERA5-Land بدقة ~9 كم)، وشبكات الرصد الأرضي المباشر لمحطات الأرصاد (28,095 محطة معتمدة من NOAA ISD و WMO)، والنموذج الهجين الذكي (Hybrid)، وإجراءات الاستيفاء الإحصائي الجغرافي الآلي، تتيح المنصة التوليد الفوري والمؤتمت لقواعد البيانات الجغرافية (File Geodatabase)، والطبقات النقطية (Shapefiles)، وأسطح الراستر المتصلة فائقة الدقة (GeoTIFF / ESRI GRID)، ومصنفات إكسيل المهيكلة، ومجلدات تتبع مصدر كل بيان (`Source Data`).

```
+--------------------------------------------------------------------------------------------------+
|                                    منظومة مِرصاد (MIRSAD Platform)                                |
|                          Multi-source Integrated Reanalysis & Surface Atlas Database             |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   +-----------------------+      +-----------------------+      +----------------------------+   |
|   |   NASA POWER API      |      |   Open-Meteo Archive  |      |     حدود منطقة الدراسة     |   |
|   | MERRA-2 & CERES GHI   |      |  ECMWF ERA5 / ERA5-Land|     | بوليجون القص / نقاط المحطات|   |
|   +-----------+-----------+      +-----------+-----------+      +--------------+-------------+   |
|               |                              |                                 |                 |
|               +----------------------+-------+---------------------------------+                 |
|                                      |                                                           |
|                                      v                                                           |
|                        +---------------------------+                                             |
|                        | مرحلة جلب البيانات والفحص |                                             |
|                        | فلترة القيم الشاذة -999.0 |                                             |
|                        | شرط اكتمال السلسلة >= 75% |                                             |
|                        +-------------+-------------+                                             |
|                                      |                                                           |
|                                      v                                                           |
|                        +---------------------------+                                             |
|                        |  محرك التجميع الزمني العام |                                             |
|                        | يومي -> شهري -> فصلي/سنوي |                                             |
|                        | حساب متوسط الرياح المتجهي |                                             |
|                        +-------------+-------------+                                             |
|                                      |                                                           |
|                                      v                                                           |
|                        +---------------------------+                                             |
|                        | النمذجة البيومناخية الحيوية|                                             |
|                        | Hargreaves PET, UNEP,     |                                             |
|                        | Heat Index, WBGT, WindChill|                                            |
|                        | اتجاهات العقود والشذوذ    |                                             |
|                        +-------------+-------------+                                             |
|                                      |                                                           |
|              +-----------------------+-----------------------+                                   |
|              |                                               |                                   |
|              v                                               v                                   |
|   +--------------------------+                   +--------------------------+                    |
|   | قواعد البيانات Geodatabase|                   |  الاستيفاء المكاني للراستر |                   |
|   | 342 حقلاً (330 حقلاً مناخياً|                   | IDW / Spline / Kriging   |                   |
|   | 19 طبقة معالم معيارية    |                   | (سنوي، فصلي، وشهري Jan-Dec)|                   |
|   | مصنفات إكسيل ثنائية الورقة|                   +-------------+------------+                   |
|   +--------------------------+                                 |                                 |
|                                                                v                                 |
|                                                  +--------------------------+                    |
|                                                  | 19 مجلداً فرعياً للراستر  |                    |
|                                                  | 94 طبقة GeoTIFF رئيسية   |                    |
|                                                  | تصنيف وسمبولوجي معتمد    |                    |
|                                                  +--------------------------+                    |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. الهيكل التنظيمي للمجلدات وأدلة التوثيق

تم تنظيم الحزمة التوثيقية الكاملة بشكل معياري داخل 6 مجلدات منظمة ومفهرسة:

### نظرة عامة على تقسيم المجلدات:
- **`01_Markdown_Manuals/`**: الفصول التقنية المكتوبة بصيغة ماركداون (من 00 إلى 16)، والأدلة المرجعية الشاملة (عربي/إنجليزي)، وأدلة المستخدم.
- **`02_Word_Documents/`**: كتيبات ومستندات النشر الرسمية المنسقة بصيغة مايكروسوفت وورد (`.docx`).
- **`03_Excel_Dictionaries/`**: المعاجم الرقمية وقواميس الحقول والمصطلحات، ودليل فئات وتصنيفات السمبولوجي (`.xlsx`).
- **`04_Interactive_HTML_Guides/`**: المستكشفات التفاعلية للخرائط والمحطات، ومعارض الستايلات، وأدلة المعاملات (`.html`).
- **`05_Climate_Data_Sources_Directory/`**: مجلد مستقل لكل مصدر بيانات مناخية (Hybrid, NOAA ISD, NASA POWER, Copernicus CDS, Open-Meteo) باللغتين العربية والإنجليزية.
- **`06_Methodology_Adding_New_Climate_Module/`**: المنهجية المعيارية المعتمدة (SOP) لإضافة موديول مناخي جديد والتحديث التراكمي للبيانات باللغتين العربية والإنجليزية.

---

### جدول الفهرس الشامل للملفات التوثيقية:

| الفصل / الرمز | عنوان الملف التوثيقي | نطاق التركيز والمحتوى العلمي والتطبيقي |
|:---:|:---|:---|
| **00** | [00_Documentation_Index_AR.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/00_Documentation_Index_AR.md) | الفهرس العربي الشامل، البنية المعمارية للنظام، مصفوفة الموديلات، والمتطلبات البرمجية. |
| **00 (EN)** | [00_Documentation_Index.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/00_Documentation_Index.md) | Master sitemap, system architecture, module matrix, and environment specs (English). |
| **01** | [01_Executive_Overview.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/01_Executive_Overview.md) | النظرة العامة التنفيذية، الأهداف العلمية، وإمكانيات إعادة التحليل المناخي متعدد المصادر. |
| **02** | [02_Data_Sources_and_Provenance.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/02_Data_Sources_and_Provenance.md) | الخصائص الفيزيائية ومواصفات نماذج MERRA-2، و CERES، و ERA5، و ERA5-Land. |
| **03** | [03_Processing_Pipeline.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/03_Processing_Pipeline.md) | خط المعالجة الحسابي والجغرافي الشامل المكون من 13 مرحلة تنفيذية مؤتمتة. |
| **04** | [04_Temporal_Aggregation_and_Seasons.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/04_Temporal_Aggregation_and_Seasons.md) | الفصول السينوبتيكية المعيارية (DJF, MAM, JJA, SON)، والإحصاء الدائري، ومعادلات المطر. |
| **05** | [05_Scientific_Formulas_All_Indicators.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/05_Scientific_Formulas_All_Indicators.md) | الصياغات الرياضية والفيزيائية الكاملة لجميع المؤشرات عبر الموديلات الـ 19. |
| **06** | [06_Field_by_Field_Reference.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/06_Field_by_Field_Reference.md) | المعجم المرجعي الشامل لجميع الحقول حقلاً بحقل مع استشهادات أسطر الكود البرمجي. |
| **07** | [07_Output_Schema_and_File_Formats.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/07_Output_Schema_and_File_Formats.md) | هياكل Geodatabase، وتوافقية أسماء الشيب فايل (10 أحرف)، وتنسيقات GeoTIFF وإكسيل. |
| **08** | [08_Missing_Data_QA_and_Gap_Filling.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/08_Missing_Data_QA_and_Gap_Filling.md) | معالجة قيم الحراسة (-999.0)، وضوابط الجودة واكتمال السلسلة، وآليات سد الثغرات. |
| **09** | [09_Spatial_Interpolation_and_Raster_Processing.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/09_Spatial_Interpolation_and_Raster_Processing.md) | معايير الاستيفاء المكاني (IDW, Spline, Kriging)، والحواجز، والمحاذاة المكانية، والإسقاط. |
| **10** | [10_Models_Assumptions_and_Limitations.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/10_Models_Assumptions_and_Limitations.md) | الفرضيات والمحددات العلمية لنماذج إعادة التحليل، ومعادلة هارجريفز، وحدود مؤشر الحرارة. |
| **11** | [11_Examples_and_Hand_Calculations.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/11_Examples_and_Hand_Calculations.md) | أمثلة عددية محلولة يدوياً خطوة بخطوة للتحقق من صحة الخوارزميات الحسابية المطبقة. |
| **12** | [12_User_Workflows_Online_Offline.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/12_User_Workflows_Online_Offline.md) | دليل المستخدم التطبيقي لمسارات العمل المتصلة بالإنترنت، ونمط العمل غير المتصل (Offline). |
| **13** | [13_Validation_and_Testing.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/13_Validation_and_Testing.md) | حزم الاختبارات المؤتمتة، والمقارنة مع محطات الرصد الميداني الحقيقية، واختبارات الجودة. |
| **14** | [14_Field_Name_Legacy_Mapping.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/14_Field_Name_Legacy_Mapping.md) | جدول التوافق والمطابقة الشامل لأسماء الحقول القديمة مقابل الهيكل الموحد الحديث. |
| **15** | [15_Adding_New_Climate_Module_Guide_AR.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/15_Adding_New_Climate_Module_Guide_AR.md) | الدليل الإرشادي الموحد لإضافة موديول مناخي جديد خطوة بخطوة (باللغة العربية). |
| **16** | [16_Climate_Data_Sources_Temporal_Coverage.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/16_Climate_Data_Sources_Temporal_Coverage.md) | الدليل المرجعي لسلاسل التغطية الزمنية (من سنة كم إلى سنة كم) لجميع المصادر الخمسة المعتمدة. |
| **TXT** | [Climate_Data_Sources_Temporal_Coverage.txt](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/Climate_Data_Sources_Temporal_Coverage.txt) | الملف النصي الصريح لسنوات التغطية والمواصفات الفنية المعتمدة للمصادر المناخية. |
| **DIR (05)** | [05_Climate_Data_Sources_Directory/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/) | المجلد المتخصص لملفات وبطاقات التوصيف الفني للمصادر الخمسة (عربي وإنجليزي). |
| **DIR (06)** | [06_Methodology_Adding_New_Climate_Module/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/06_Methodology_Adding_New_Climate_Module/) | مجلد المنهجية المعيارية المعتمدة (SOP) لإضافة عنصر مناخي جديد والتحديث التراكمي للبيانات (عربي/إنجليزي). |
| **DOCX** | [Climate_Data_Sources_Comparison_Guide.docx](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/Climate_Data_Sources_Comparison_Guide.docx) | مستند وورد احترافي يحتوي على جداول المقارنة السريعة والشاملة وقواعد اتخاذ القرار. |
| **Audit** | [DOCUMENTATION_AUDIT_REPORT.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/DOCUMENTATION_AUDIT_REPORT.md) | تقرير التدقيق الفني الشامل الذي يثبت التطابق بنسبة 100% بين الكود البرمجي والتوثيق. |
| **AR** | [Complete_Scientific_Technical_Documentation_AR.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/Complete_Scientific_Technical_Documentation_AR.md) | الموسوعة التوثيقية العلمية والفنية العربية الموحدة الشاملة لكافة الأقسام. |
| **EN** | [Complete_Scientific_Technical_Documentation_EN.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/Complete_Scientific_Technical_Documentation_EN.md) | Unified English Master Documentation Manual. |
| **HTML** | [Complete_Scientific_Technical_Documentation.html](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/04_Interactive_HTML_Guides/Complete_Scientific_Technical_Documentation.html) | دليل الويب التفاعلي للتوثيق مع محرك بحث لحظي ديناميكي عبر الحقول الـ 136. |
| **HTML** | [Styles_Browser.html](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/04_Interactive_HTML_Guides/Styles_Browser.html) | معرض تفاعلي لـ 125 نمط كارتوجرافي مع خاصية نسخ الأكواد اللونية بنقرة واحدة. |
| **REF** | [HI_Felt_Temperature_Equations_AR_EN.md](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/01_Markdown_Manuals/HI_Felt_Temperature_Equations_AR_EN.md) | مرجع معادلات درجات الحرارة المحسوسة والإجهاد الحراري (Rothfusz, Humidex, WBGT). |
| **HTML** | [Parameters_Guide.html](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/04_Interactive_HTML_Guides/Parameters_Guide.html) | دليل تفاعلي يشرح جميع معاملات صندوق الأدوات المولدة آلياً من الكود المصدري. |
| **HTML** | [Modules_Dependency_Map.html](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/04_Interactive_HTML_Guides/Modules_Dependency_Map.html) | خريطة العلاقات والاعتماديات الشجرية التفاعلية بين الموديلات المناخية ومتطلباتها. |
| **HTML** | [Egypt_Weather_Stations_Map.html](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/04_Interactive_HTML_Guides/Egypt_Weather_Stations_Map.html) | المستكشف التفاعلي لمحطات الأرصاد الجوية في جمهورية مصر العربية (87 محطة معتمدة). |
| **HTML** | [Global_Weather_Stations_Map.html](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/04_Interactive_HTML_Guides/Global_Weather_Stations_Map.html) | المستكشف العالمي لمحطات الأرصاد الجوية (28,095 محطة) مع خاصية سحب وإفلات الشيب فايل. |
| **HUB** | [Weather_Stations_Hub/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Weather_Stations_Hub/) | مستودع بيانات محطات الأرصاد الجوية (قواعد بيانات، شيب فايل، مستكشفات الويب). |
| **TOOL** | [MIRSAD_Weather_Stations_Atlas_Generator.pyt](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/MIRSAD_Weather_Stations_Atlas_Generator.pyt) | أداة الأطلس المناخي المخصصة لمحطات الأرصاد الجوية الأرضية (نسخة الكربون الكاملة). |
| **DOCX** | [Complete_Scientific_Technical_Documentation.docx](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/02_Word_Documents/Complete_Scientific_Technical_Documentation.docx) | كتيب التوثيق الرسمي المعد للنشر والطباعة بصيغة مايكروسوفت وورد. |
| **XLSX** | [Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/03_Excel_Dictionaries/Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx) | المعجم المرجعي الرئيسي لجميع الحقول والمصطلحات والوحدات الفيزيائية (عربي/إنجليزي). |
| **XLSX** | [Climate_Atlas_Classification_Guide.xlsx](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/03_Excel_Dictionaries/Climate_Atlas_Classification_Guide.xlsx) | دليل فئات التصنيف الكارتوجرافي لكسور جنكس الطبيعية (3، 5، 7، 9 فئات). |

---

## 3. مصفوفة الموديلات المناخية الـ 19

يقوم محرك الأطلس المناخي بمعالجة وتركيب **19 موديولاً بيوفيزيائياً ومناخياً مستقلاً**، ويتم تصدير نواتج كل موديول إلى مجلد راستر فرعي مستقل ومنظم:

| الكود | اسم الموديول (عربي / إنجليزي) | مجلد مخرجات الراستر | إجمالي الحقول | السنوي/الفصلي/المعياري | الشهري Jan–Dec | العمليات الرياضية والفيزيائية الأساسية |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **00** | إدارة النظام والميتاداتا / Admin & Metadata | `-` (سمات وصفية نقطية فقط) | 12 | 12 | - | تتبع المعالجة، الإحداثيات الجغرافية والمعيارية |
| **01** | درجات الحرارة / Temperature | `01_Temperature` | 23 | 11 | 12 (متوسط الشهور) | المتوسطات الحسابية، المعدلات الفصلية، المتوسط الشهري |
| **02** | تساقط الأمطار / Precipitation | `02_Precipitation` | 20 | 8 | 12 (تراكمي الشهور) | المجاميع السنوية والفصلية، المتوسط اليومي، أيام المطر |
| **03** | الضغط عند مستوى البحر / Sea Level Pressure | `03_Sea_Level_Pressure` | 19 | 7 | 12 (متوسط الشهور) | المعدلات المعيارية، الضغط المعدل لرسم خطوط الآيزوبار |
| **04** | الضغط الجوي السطحي / Surface Pressure | `04_Surface_Pressure` | 19 | 7 | 12 (متوسط الشهور) | الضغط الجوي الحقيقي المقاس عند منسوب سطح الأرض |
| **05** | حركة الرياح / Wind | `05_Wind` | 39 | 15 | 24 (12 سرعة + 12 اتجاه) | السرعة العددية، والاتجاه المتجهي الدائري atan2(sin, cos) |
| **06** | الرطوبة النسبية / Relative Humidity | `06_Relative_Humidity` | 19 | 7 | 12 (متوسط الشهور) | المعدلات المعيارية السنوية والفصلية والشهرية |
| **07** | نقطة الندى / Dew Point | `07_Dew_Point` | 19 | 7 | 12 (متوسط الشهور) | درجة حرارة التشبع والرطوبة المطلقة |
| **08** | الإشعاع الشمسي / Solar Radiation | `08_Solar_Radiation` | 20 | 8 | 12 (متوسط الشهور) | الإشعاع الشمسي اليومي، التراكم السنوي، الطاقة الكهروضوئية |
| **09** | الأشعة فوق البنفسجية / UV Index | `09_UV_Index` | 20 | 8 | 12 (متوسط الشهور) | ذروة الظهيرة الشمسية، مقياس منظمة الصحة العالمية |
| **10** | الغطاء السحابي / Cloud Cover | `10_Cloud_Cover` | 19 | 7 | 12 (متوسط الشهور) | نسبة حجب السماء بالسحب (%) بالأثمان والنسبة |
| **11** | مؤشر الإجهاد الحراري / Heat Index | `11_Heat_Index` | 8 | 8 | - | معادلة روثفوس متعددة الحدود، والحرارة الرطبة لستول |
| **12** | عامل برودة الرياح / Wind Chill | `12_Wind_Chill` | 2 (+17 خياري) | 2 | - | معادلة التبريد بالحمل الحراري NWS للمناطق الباردة |
| **13** | مؤشر دومارتون للجفاف / De Martonne Aridity | `13_De_Martonne_Aridity` | 1 | 1 | - | تصنيف الجفاف البيومناخي وفق معادلة $I_{DM} = P / (T + 10)$ |
| **14** | البخر-نتح المرجعي / Evapotranspiration | `14_Evapotranspiration` | 22 | 10 | 12 (FAO-56 شهري) | نموذج هارجريفز-ساماني (1985)، واستهلاك مياه المحاصيل |
| **15** | مؤشر الجفاف الدولي / UNEP Aridity | `15_UNEP_Aridity` | 1 | 1 | - | تصنيف الأراضي الجافة وفق الأمم المتحدة $AI = P / \text{PET}$ |
| **16** | العجز المائي المناخي / Water Deficit | `16_Water_Deficit` | 1 | 1 | - | الميزان الهيدرولوجي الصافي $CWD = P - \text{PET}$ |
| **17** | عدد الأشهر الجافة / Dry Months | `17_Dry_Months` | 1 | 1 | - | المعيار البيومناخي لباغنولز وجوسين ($P < 2T$) |
| **18** | الاتجاهات والتغير / Trends & Anomalies | `18_Trends_And_Anomalies` | 9 | 9 | - | انحدار المربعات الصغرى للعقود (OLS Trend Slope) |
| **19** | حرارة سطح الأرض / Land Surface Temperature | `19_Land_Surface_Temperature` | 25 | 13 | 12 (متوسط الشهور) | حرارة الجلد الإشعاعية الفضائية (LST) وفوارق سطح الأرض |
| **المجموع** | **كافة الموديلات مجتمعة** | **19 مجلداً للراستر** | **295** | **139 (12 ميتاداتا + 127 سنوي/فصلي)** | **156 مؤشراً شهرياً** | **أطلس مناخي تطبيقي متكامل ومتعدد التخصصات** |

---

## 4. البيئة البرمجية ومتطلبات التشغيل

تم تصميم وبناء صندوق الأدوات ليعمل بكفاءة مطلقة عبر البيئات الحديثة والكلاسيكية دون الحاجة لتثبيت أي مكتبات خارجية مدفوعة خارج منظومة ESRI ArcGIS:

- **بيئة ArcGIS Desktop:** الإصدارات 10.8، 10.8.1، 10.8.2 (بيئة تشغيل بايثون 2.7.18 نواة 32 بت).
- **بيئة ArcGIS Pro:** الإصدارات من 2.8 حتى 3.3+ (بيئة تشغيل بايثون 3.7+ كوندا نواة 64 بت).
- **الامتداد الجغرافي الإلزامي:** امتداد التحليل المكاني `Spatial Analyst` (لتنفيذ استيفاء IDW, Spline, Kriging وقص الراستر).
- **مكتبات بايثون القياسية المستخدمة:** `arcpy`, `urllib2` / `requests`, `json`, `math`, `csv`, `calendar`, `os`, `sys`, `time`.
- **مكتبات بايثون الاختيارية:** `openpyxl` أو `xlwt` (لتصدير مصنفات إكسيل المنسقة مباشرة).
