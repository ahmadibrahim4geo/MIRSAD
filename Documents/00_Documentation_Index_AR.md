# فهرس توثيق مِرصاد

محدث: 22 أكتوبر 2026. الاسم المعتمد: **Meteorological Integrated Reanalysis Spatial Atlas Database — قاعدة بيانات الأطلس المكاني لإعادة التحليل المتكامل للأرصاد الجوية**.

[English](00_Documentation_Index.md) · [الموقع](../index.html) · [المساعدة العربية](../Help/MIRSAD_Help_AR.html) · [CHM عربي](../Help/MIRSAD_Help_AR.chm)

## الحالة الحالية والتنزيل

تضم المنصة 19 مجموعة مناخية، وقاموسًا مراجعًا لـ521 حقلًا قديمًا ممكنًا، بالإضافة إلى حقول التوسعة الاختيارية المشروحة داخل كل مصنف صادر. يحتوي الكتالوج المشترك على 28,066 سجل موقع؛ تطابق الكتالوج لا يثبت صحة المحطة ميدانيًا. عدد حقول النتيجة يتغير بحسب العناصر والفترات والخيارات المختارة.

المصدر الحالي يضم 11 متغيرًا يوميًا اختياريًا، وحساب Hargreaves وPenman–Monteith مستقلين، وكتابة XLSX تدريجية وتقسيم الأوراق والملفات في Desktop وأداتي النقاط والمحطات. يدعم Desktop أيضًا إثراء مناسيب النقاط من DEM محلي أو شبكي، مع حفظ الأصل وبيان DTM أو DSM والمرجع الرأسي. عند اشتقاق اليومي من ساعات مكتملة تسجل المخرجات عملية التجميع وتغطية UTC والمصدر. المنتجات الشهرية والمركبة لا تتحول إلى مشاهدات يومية مصطنعة.

**المثبت العام 0.4.0.dev8 يخص بناء 19 أكتوبر** ولا يتضمن التعديلات اللاحقة. المساعدة الحالية في المستودع أحدث من ملفات CHM المرفقة بالإصدار المنشور. نشر مثبت جديد يحتاج قبول مرشحه على حدة؛ لم تُعتمد نسخة stable.

| ابدأ من هنا | المحتوى |
|---|---|
| [تحديث مصدر 22 أكتوبر](SOURCE_UPDATE_2026_10_22.md) | نطاق التسليم والفحوص والمتبقي |
| [الحالة الحالية](../MIRSAD%20Desktop/docs/STATUS.md) | الوظائف المنفذة والفرق عن المثبت |
| [المتبقي](../MIRSAD%20Desktop/docs/BACKLOG.md) | التنفيذ الناقص والقبول المطلوب |
| [تتبع خطة التوسعة](../MIRSAD%20Desktop/docs/reports/climate-enrichment/IMPLEMENTATION_TRACKER.md) | ربط كل دفعة بالدليل |
| [فهرس التقارير](../MIRSAD%20Desktop/docs/README.md) | التقارير المؤرخة والبصمات وحدود الفحوص |
| [سجل النشر](DEVELOPMENT_PUBLICATION.md) | مرجع المثبت العام وبصماته |

## الأدلة والمراجع العلمية

- [مركز المساعدة العربي](../Help/MIRSAD_Help_AR.html): الخيارات الحالية والمعادلات والوحدات والأمثلة.
- [دليل المصادر](07_Climate_Sources_Web_Guide/climate-sources.html): المنتجات المنفذة والعناصر والفترات والدقة والحسابات المطلوبة وقدرات كل أداة.
- [دليل المستخدم العربي](01_Markdown_Manuals/User_Guide_Arabic.md).
- [قاموس الحقول والوحدات](03_Excel_Dictionaries/Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx) و[دليل التصنيف الكارتوجرافي](03_Excel_Dictionaries/Climate_Atlas_Classification_Guide.xlsx): أصول مرجعية للحقول القديمة؛ لكل حقل اختياري جديد تعريفه في شيت Field_Dictionary بالمخرجات.
- [إضافة عنصر مناخي](06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_AR.md)، و[الدليل الإنجليزي](06_Methodology_Adding_New_Climate_Module/Adding_New_Climate_Module_Guide_EN.md)، و[مراجعة المنهجية](../MIRSAD%20Desktop/docs/reports/METHODOLOGY_REVIEW.md).

الأدلة المرقمة أدناه تحتفظ بالشروحات التاريخية. أعدادها القديمة ووصف المصادر وأمثلة المخرجات لا تحل محل الكود الحالي والمساعدة المولدة وتقارير القبول المؤرخة.

- [نظرة عامة](01_Markdown_Manuals/01_Executive_Overview.md).
- [المصادر وتتبعها](01_Markdown_Manuals/02_Data_Sources_and_Provenance.md).
- [مسار المعالجة](01_Markdown_Manuals/03_Processing_Pipeline.md).
- [التجميع الزمني والفصول](01_Markdown_Manuals/04_Temporal_Aggregation_and_Seasons.md).
- [المعادلات العلمية](01_Markdown_Manuals/05_Scientific_Formulas_All_Indicators.md).
- [مرجع الحقول](01_Markdown_Manuals/06_Field_by_Field_Reference.md).
- [المخرجات وصيغ الملفات](01_Markdown_Manuals/07_Output_Schema_and_File_Formats.md).
- [البيانات المفقودة والجودة](01_Markdown_Manuals/08_Missing_Data_QA_and_Gap_Filling.md).
- [الاستيفاء والراستر](01_Markdown_Manuals/09_Spatial_Interpolation_and_Raster_Processing.md).
- [الافتراضات والقيود](01_Markdown_Manuals/10_Models_Assumptions_and_Limitations.md).
- [أمثلة وحسابات يدوية](01_Markdown_Manuals/11_Examples_and_Hand_Calculations.md).
- [مسارات الإنترنت والأوفلاين](01_Markdown_Manuals/12_User_Workflows_Online_Offline.md).
- [مرجع التحقق](01_Markdown_Manuals/13_Validation_and_Testing.md).
- [ربط الحقول القديمة](01_Markdown_Manuals/14_Field_Name_Legacy_Mapping.md).

## التطوير وحدود التحقق

[التسليم المشترك](../AGENTS.md) · [تسليم Toolbox](../Toolboxes/AGENTS.md) · [تسليم Desktop](../MIRSAD%20Desktop/AGENTS.md) · [الاختبارات](TESTING.md) · [المساهمة](../CONTRIBUTING_AR.md).

ما زال DEM في Toolbox والإضافات الإقليمية والراستر الأصلي وArcMap وقاموس المساعدة الكامل للحقول الاختيارية واختبار ألف نقطة/30 سنة وDPI والإتاحة الشاملة مفتوحًا. قبول CDS/IMERG بحساب فعلي والتكافؤات الأقدم موثقة في المتبقي. اختبارات توافق Python ومحاكاة ArcPy لا تعادل قبول ArcMap الأصلي.
