# MIRSAD Desktop | مرصاد

تطبيق Windows مستقل بنواة Python وواجهة PySide6/Qt، بالعربية والإنجليزية.
النسخة الحالية **0.4.0.dev8 للتطوير**. لا يحتاج تشغيله ArcGIS أو Python خارجيًا
أو وجود مجلد Toolboxes بجانبه.

## التشغيل

- التطوير: `runtime/development/MIRSAD.exe`.
- مثبت التطوير: `runtime/installers/development/MIRSAD-Setup.exe`.
- الإصدار المعتمد: `runtime/stable/`؛ محجوز حتى اعتماد مرشح محدد.

احتفظ بمجلد التطبيق كاملًا، بما فيه `_internal`؛ لا تنقل EXE وحده.
مشروعات المستخدم خارج مجلد التثبيت، ولا تُمسح عند تحديث البرنامج أو إزالته.
لا يوجد إصدار Desktop نهائي منشور على GitHub Releases حتى الآن.

[تحميل مثبت التطوير 0.4.0.dev8](https://github.com/ahmadibrahim4geo/MIRSAD/releases/download/desktop-v0.4.0-dev.8/MIRSAD-Desktop-0.4.0.dev8-Windows-x64-Setup.exe)،
وملفات CHM وبصمات التحقق متاحة في [صفحة الإصدار](https://github.com/ahmadibrahim4geo/MIRSAD/releases/tag/desktop-v0.4.0-dev.8).
البصمات وحدود القبول موثقة في [سجل النشر](../Documents/DEVELOPMENT_PUBLICATION.md).
النشر التجريبي منفصل عن اعتماد stable.

## الدليل والحالة

- [فهرس التوثيق](docs/README.md).
- [الحالة الحالية](docs/STATUS.md) و[الشغل المتبقي](docs/BACKLOG.md).
- [الدليل العربي](docs/user/USER_GUIDE_AR.html) و[English guide](docs/user/USER_GUIDE_EN.html).
- [سجل التغييرات](docs/CHANGELOG.md) و[تقارير التحقق](docs/reports/).
- [المعمارية](docs/architecture/) و[دليل التطوير](AGENTS.md).

المساعدة متاحة أيضًا داخل التطبيق، وبالوضع المستقل `--user-guide`، وبملفي
CHM من المصدر المشترك. دليل العناصر يشرح المعادلات وأسماء الحقول والفترات والوحدات.
راجع الحالة والمتبقي قبل اعتبار كل المخرجات مطابقة لأدوات ArcGIS.

## تطوير وبناء مستقل

```powershell
& '.\scripts\build_development.ps1'
```

البيئة `.venv` خاصة بـDesktop؛ لا تستخدم ArcGIS Python للبناء. يجهز الأمر الأصول
والنواة العلمية والمساعدة، ويختبرها، ثم يبني ويفحص الحزمة خارج مجلد المستودع.
المرجع العلمي يأتي وقت البناء من `../Toolboxes/` والدعم المشترك من
`../mirsad_core/`، ثم يضمان محليًا؛ لا اعتماد على المجلدين عند تشغيل التطبيق.

المصدر في `src/`، والبناء والصيانة في `scripts/`، والاختبارات في `tests/`،
والأصول في `assets/`. الوسائط المؤقتة فقط في `.build/` و`.test-output/` ولا ترفع إلى Git.
التبعيات في `requirements.txt` و`requirements.lock`، وإشعارات تراخيصها ضمن التوزيع.

الترقية إلى stable ونشر إصدار وتثبيت نسخة إنتاج تحتاج موافقة صريحة على المرشح
المختبر. بيانات الناشر داخل EXE ليست توقيع Authenticode؛ لا يوجد ادعاء توقيع موثوق.
