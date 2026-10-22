# تحديث المصدر والتوثيق — 22 أكتوبر 2026

هذا تحديث تطوير للمصدر والموقع والشروحات، فوق نقطة البداية `09bb7fd`.
لا يعني اكتمال خطة التوسعة أو التكافؤ الكامل بين الأدوات. المثبت العام
[0.4.0.dev8](https://github.com/ahmadibrahim4geo/MIRSAD/releases/tag/desktop-v0.4.0-dev.8)
يخص 19 أكتوبر ولا يحتوي على الإضافات اللاحقة. مرشح Desktop المحلي المؤرخ
21 أكتوبر له أدلته المنفصلة ويَسبق تغييرات Toolbox والمساعدة التالية.

## ما أصبح في المصدر

| النطاق | التسليم والدليل |
|---|---|
| Desktop | 11 متغيرًا اختياريًا، تدقيق الاشتقاق اليومي من الساعات، إثراء DEM محلي/شبكي، HG وPM مستقلان، وXLSX تدريجي. [قبول المصدر](../MIRSAD%20Desktop/docs/reports/climate-enrichment/DESKTOP_SOURCE_ACCEPTANCE.md) |
| Point/Station Toolbox | المتغيرات الـ11، طرق HG/PM منفصلة، اختيار الراستر لكل طريقة، وتصدير سنوي مع المصدر والتغطية. 83/90 معاملًا؛ الإقليمي 36. [المتغيرات](../MIRSAD%20Desktop/docs/reports/climate-enrichment/TOOLBOX_ACCEPTANCE.md) و[PM](../MIRSAD%20Desktop/docs/reports/climate-enrichment/TOOLBOX_PM_ACCEPTANCE.md) |
| Excel الكبير | XLSX تدريجي وتقسيم الأوراق والملفات مع فهرس؛ قبول حد مليون صف في Python 3 و2.7 وقراءة Pro أصلية. [دليل Excel](../MIRSAD%20Desktop/docs/reports/climate-enrichment/LEGACY_EXCEL_ACCEPTANCE.md) |
| حماية النتائج | المرجع السابق للـ19 مجموعة والمعادلات القديمة محفوظ؛ الإضافات مغلقة افتراضيًا. المفقود يبقى مفقودًا والصفر الصحيح محفوظ. [baseline](../MIRSAD%20Desktop/docs/reports/climate-enrichment/BASELINE_AUDIT.md) |
| الشروحات والموقع | فهرس عربي/إنجليزي بروابط نسبية، حالة المصدر مقابل المثبت، دليل المصادر المولد، ومساعدة Qt/HTML/CHM. قاموس الحقول الإضافية موجود بالمصنفات؛ إكمال مرجع كل حقل في المساعدة ما زال مفتوحًا. |

الاشتقاق الساعي يحتاج ساعات UTC المكتملة بحسب عقد المتغير ويسجل عملية التجميع
والتغطية في المخرجات. لا تتحول المنتجات الشهرية أو المركبة إلى يومي مصطنع.
DEM إضافة اختيارية تحفظ المنسوب الأصلي وتعلن نوع السطح والمرجع الرأسي؛
Copernicus GLO-90 المتاح عبر Open-Meteo هو DSM ولا يوصف كأرض عارية.

## ما يبقى لإنهاء الخطة كاملة

1. DEM الاختياري في Toolbox، والإضافات الإقليمية/المنتجات التي تدعمها فعليًا.
2. قبول الراستر الإضافي وPM في تشغيل أصلي، وقبول ArcMap؛ تهيئة GP في
   ArcMap لم تكتمل في المحاولات المحدودة السابقة. نجاح Python 2.7 لا يعوضها.
3. القاموس التفصيلي الكامل للحقول الاختيارية في المساعدة، والتعريب الاختياري
   للأسماء المستعارة في Desktop، ومتطلبات حقول الموقع والتكافؤ المتقدم.
4. قياس pipeline ألف نقطة/30 سنة، الذاكرة والإلغاء والاستئناف، وDPI/الإتاحة.
5. قبول مرشح مجمع حديث قبل نشر مثبت جديد. قبول CDS/IMERG بحساب فعلي وبنود
   التكافؤ الأقدم تبقى في [قائمة المتبقي](../MIRSAD%20Desktop/docs/BACKLOG.md).

## التحقق والنشر

سجل الفحوص النهائية لهذا التحديث هو
[SOURCE_UPDATE_2026_10_22.json](SOURCE_UPDATE_2026_10_22.json)، ويحتفظ بنطاق
كل فحص وبصماته؛ نتائج Python 2.7 وPro السابقة تبقى مرتبطة بتقاريرها المؤرخة.
لا تجمع الأعداد المتداخلة باعتبارها اختبارات فريدة. حالات Pro الست تستخدم
استجابات مصدر اصطناعية ولا تثبت التنزيل الحي أو إنتاج الراستر الأصلي.

التحديث المأذون يشمل المصدر والتوثيق وموارد المساعدة المرجعية. بيانات المستخدم
المحلية وقواعد Sample Data وتغييرات XML المولدة ومجلدات التشغيل والبناء
والاختبار لا تدخل هذا التسليم. لم يُنشر مثبت جديد ولم تُرقّ نسخة stable.
تفاصيل المثبت المنشور وبصماته باقية في [سجل النشر](DEVELOPMENT_PUBLICATION.md).

English: this is a source/documentation update, with explicit pending work and
separate historical binary evidence. See the [English index](00_Documentation_Index.md),
[current status](../MIRSAD%20Desktop/docs/STATUS.md) and
[backlog](../MIRSAD%20Desktop/docs/BACKLOG.md). The public 19 October installer
does not include these source additions.
