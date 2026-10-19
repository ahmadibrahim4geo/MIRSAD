# دليل منهجية إضافة عنصر مناخي جديد للأطلس والتطبيق التدريجي على قواعد البيانات المكتملة
## Comprehensive Methodology Guide for Adding a New Climate Module and Incremental Database Updating

**المؤلف:** م. أحمد إبراهيم (Ahmad Ibrahim)  
**البريد الإلكتروني:** ahmadibrahim.geo@gmail.com  
**البيئة التشغيلية:** ArcGIS Desktop (ArcMap 10.8) / ArcGIS Pro (2.8+ / 3.x)  
**تاريخ التحديث:** أكتوبر 2026  

---

## 1. المقدمة والهدف العام (Purpose & Scope)

يوفر هذا الدليل **منهجية معيارية موحدة (Standard Operating Procedure - SOP)** لكيفية إضافة أي عنصر مناخي جديد إلى منظومة **NASA POWER & Open-Meteo Climate Atlas Generator**.

تم تصميم هذه المنهجية لتخدم مسارين أساسيين متكاملين:
1. **المسار الأول: تطوير الأداة البرمجية (Tool Codebase Integration):** كيفية تعديل كود الأداة ومكتبات التحميل والراسترات والقواميس ليتعرف النظام تلقائياً على الموديول الجديد في أي تشغيل مستقبلي عبر واجهة ArcMap / ArcGIS Pro.
2. **المسار الثاني: التطبيق التدريجي على قاعدة بيانات محملة مسبقاً (Incremental Database Backfill):** في حال قام المستخدم بالفعل بتحميل بيانات دراسة لمنطقة معينة (مثل مصر 1996–2025 لـ 646 نقطة) واكتملت مخرجاتها، ثم أراد إضافة عنصر جديد دون إعادة تشغيل المشروع بالكامل ودون المساس بالملفات وقواعد البيانات الأصلية (مبدأ التطعيم الآمن والإضافة التراكمية).

---

## 2. القواعد الذهبية والمبادئ الصارمة (Golden Rules)

> [!IMPORTANT]
> **القاعدة 1: العمل في بيئة مرحلية مستقلة (Strict Staging)**  
> لا تقم أبداً بالكتابة المباشرة على قواعد البيانات الأصلية أو استبدال الملفات القائمة قبل اكتمال التحقق. يتم حفظ المخرجات دائماً في مجلد مرحلي مؤقت يحمل اللاحقة `_STAGING` أو `_NEW` حتى يتم تدقيقها بالكامل، والاستبدال يتم يدوياً بعد التأكد.

> [!IMPORTANT]
> **القاعدة 2: التطابق الحرفي للهيكل والألياس في الجيوداتابيز (Schema & Alias Parity)**  
> - في الجيوداتابيز (GDB Feature Classes): أسماء الحقول إنجليزية كاملة، والألياس الإنجليزي مطابق تماماً لاسم الحقل (`field_alias == field_name`) بنسبة 100%. التعريب يخرج فقط من أدوات التصدير المعربة المنفصلة `_AR.gdb`.  
> - في ملفات الـ Shapefile: أسماء الأعمدة مختصرة وفريدة وبطول $\le 10$ أحرف، مع احتفاظ الـ Alias بالاسم الإنجليزي الكامل.

> [!IMPORTANT]
> **القاعدة 3: استبعاد المؤشرات الفائضة وتوليد الراسترات ذات القيمة المكانية فقط (Streamlined Schema & Essential Rasters Policy)**  
> - **إلغاء المؤشرات الفائضة والمكررة:** تم إلغاء حقول `*_Month_Mean` نهائياً لتطابقها الرياضي التام مع `*_Annual_Mean` (المتوسط الحسابي للشهور الـ 12)، وكذلك إلغاء حقول المدى الفصلي `*_Seasonal_Range` للاكتفاء بالمدى السنوي `*_Annual_Range`. ويُستثنى من ذلك مؤشرا التطرف البيومناخي المستقلان (`T_Max_Summer_Month_Mean` و `T_Min_Winter_Month_Mean`) المحفوظان بعناية.
> - **سياسة راستر متسقة وواضحة:** يتم توليد الراسترات للمؤشرات الأساسية فقط (11 راستر رئيسياً للموديول المقارن: السنوي، 4 فصول، المدى السنوي، و5 فوارق سنوية وفصلية، بالإضافة للمتوسطات الشهرية الـ 12 حال تفعيل خيار الراسترات الشهرية).
> - **استثناء الفوارق الشهرية من الراستر:** تقتصر الفوارق الشهرية الاثنا عشر (مثل `LST_minus_T_January` حتى `December`) على الجداول في الجيوداتابيز وملفات الإكسل فقط، وتُستبعد تماماً من مصفوفة الراستر لمنع تضخيم المخرجات دون جدوى كارتوجرافية.

> [!IMPORTANT]
> **القاعدة 4: التوزيع القياسي للشيتات في ملفات الإكسل (Excel Sheets Distribution)**  
> - **شيت `Data`**: يحمل المؤشرات السنوية والفصلية والمدى والفوارق العامة (السنوي والفصول الأربعة)، بالإضافة لكافة الحقول الوصفية والإدارية.
> - **شيت `Month`**: يحمل أعمدة التعريف والإحداثيات (`OBJECTID`, `Source_ID`, `Point_Lat`, `Point_Lon`) بالإضافة إلى المتوسطات الشهرية الـ 12 (`<Param>_<Month>_Mean`)، والفوارق الشهرية الـ 12 (`<Param>_minus_<Ref>_<Month>`).

> [!IMPORTANT]
> **القاعدة 5: ثبات عدد باراميترات الأدوات في ArcGIS Toolbox**  
> يجب أن تظل الأداة الرئيسية محتفظة بدقة بـ **65 باراميتر**، وأداة الراستر بـ **33 باراميتر** دون أي إخلال بترتيب أو ترقيم الباراميترات في صندوق الأدوات `ArcToolbox`.

---

## 3. المسار الأول: خطوات تطوير الأداة البرمجية (Tool Codebase Integration)

يتطلب دمج عنصر مناخي جديد تحديث 4 ملفات برمجية أساسية داخل المستودع:

```
NASA POWER Climate Atlas Generator Codebase
├── Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt   (الأداة الرئيسية: سحب، حساب، تصدير)
├── Toolboxes/raster_atlas_generator.py                (أداة الراستر والاستيفاء)
├── generate_excel_dictionary.py             (مولد القواميس الشاملة)
└── generate_master_atlas_excel.py           (مولد دليل التصنيف الماستر)
```

### الخطوة 1.1: اختيار العنصر وتحديد مصادر البيانات والفيزياء المناخية
قبل البدء في الكود، حدد الآتي بدقة:
1. **الاسم الكامل للموديول:** مثل `Land Surface Temperature`.
2. **رقم المجلد:** الترقيم التسلسلي التالي (مثال: المجلد التاسع عشر `19_Land_Surface_Temperature`).
3. **الكود المختصر (Prefix):** رمز فريد للمؤشرات (مثل `LST`).
4. **مصدر البيانات في NASA POWER:** اسم الباراميتر في API (مثال: `TS` لدرجة حرارة سطح الأرض MERRA-2 بدقة 0.5°).
5. **مصدر البيانات في Open-Meteo:** اسم المتغير المكافئ في ERA5 (مثال: `skin_temperature`).
6. **وحدة القياس والمدى الفيزيائي:** الوحدة (مثال: `°C`) والنطاق الفيزيائي المعقول للاختبارات وQA (مثال: من -30 إلى 75 درجة مئوية).

---

### الخطوة 1.2: تعديل الأداة الرئيسية `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt`

افتح الملف وقم بإجراء الإضافات في المواقع المحددة أدناه:

#### 1. تسجيل اسم الموديول ومجلداته:
أضف اسم الموديول إلى القوائم والقواميس الثابتة:
```python
PRIMARY_MODULES_ALL = [
    "Temperature", "Precipitation", ..., "Land Surface Temperature"
]

MODULE_PARAMS = {
    ...
    "Land Surface Temperature": ["TS"],
}

MODULE_FOLDER = {
    ...
    "Land Surface Temperature": "19_Land_Surface_Temperature",
}

MODULE_SHORT = {
    ...
    "Land Surface Temperature": "LST",
}

DEFAULT_UNIT_BY_MODULE = {
    ...
    "Land Surface Temperature": "deg_c",
}

COLOR_RAMPS = {
    ...
    "Land Surface Temperature": "Temperature",  # أو سلم ألوان مخصص
}
```

#### 2. ربط Open-Meteo ERA5:
إذا كان المتغير متاحاً في Open-Meteo:
```python
OM_HOURLY_BY_MODULE = {
    ...
    "Land Surface Temperature": ["skin_temperature"],
}
OM_CANON = {
    ...
    "skin_temperature": "TS",
}
```

#### 3. تعريف مصفوفة الحقول المناخية (`_LST_DEFS`):
حدد قائمة الحقول الـ 35 بصيغة tuples:
`(Field_Name, Alias, Type, Width, Precision, Scale, Period, Statistic, Unit, Formula, Description)`:
```python
_LST_DEFS = [
    # 1. المؤشر السنوي
    ("LST_Annual_Mean", "Annual Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Annual", "Mean", "deg_c", "MEAN(TS_monthly)", "Mean annual land surface temperature"),
    # 2-5. الفصول الأربعة
    ("LST_Winter_Mean", "Winter Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Winter", "Mean", "deg_c", "MEAN(TS_Dec, Jan, Feb)", "Mean winter land surface temperature"),
    ("LST_Spring_Mean", "Spring Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Spring", "Mean", "deg_c", "MEAN(TS_Mar, Apr, May)", "Mean spring land surface temperature"),
    ("LST_Summer_Mean", "Summer Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Summer", "Mean", "deg_c", "MEAN(TS_Jun, Jul, Aug)", "Mean summer land surface temperature"),
    ("LST_Autumn_Mean", "Autumn Mean Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Autumn", "Mean", "deg_c", "MEAN(TS_Sep, Oct, Nov)", "Mean autumn land surface temperature"),
    # 6. المدى الحراري السنوي
    ("LST_Annual_Range", "Annual Range Land Surface Temperature", "DOUBLE", 8, 8, 2,
     "Annual", "Range", "deg_c", "MAX(TS_m) - MIN(TS_m)", "Annual range of monthly LST"),
    # 7-11. الفروق البيئية (السنوي والفصول الأربعة)
    ("LST_minus_T_Annual", "Annual Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Annual", "Mean", "deg_c", "LST_Annual_Mean - T_Annual_Mean", "Surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Winter", "Winter Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Winter", "Mean", "deg_c", "LST_Winter_Mean - T_Winter_Mean", "Winter surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Spring", "Spring Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Spring", "Mean", "deg_c", "LST_Spring_Mean - T_Spring_Mean", "Spring surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Summer", "Summer Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Summer", "Mean", "deg_c", "LST_Summer_Mean - T_Summer_Mean", "Summer surface skin temperature minus 2m air temperature"),
    ("LST_minus_T_Autumn", "Autumn Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2,
     "Autumn", "Mean", "deg_c", "LST_Autumn_Mean - T_Autumn_Mean", "Autumn surface skin temperature minus 2m air temperature"),
    # 12-23. الشهور الاثنا عشر
    ("LST_January_Mean", "January Mean Land Surface Temperature", "DOUBLE", 8, 8, 2, "January", "Mean", "deg_c", "MEAN(TS_Jan)", "January mean LST"),
    # ... حتى December ...
    # 24-35. الفوارق الشهرية الاثنا عشر (حقول جدولية في GDB والإكسل فقط)
    ("LST_minus_T_January", "January Surface Minus Air Temperature Difference", "DOUBLE", 8, 8, 2, "January", "Difference", "deg_c", "LST_Jan - T_Jan", "January surface minus air temperature"),
    # ... حتى December ...
]

FIELD_DEFS.extend(_LST_DEFS)
MODULE_FIELDS["Land Surface Temperature"] = [f[0] for f in _LST_DEFS]
```

#### 4. تعريف خريطة أسماء الـ Shapefile ($\le 10$ أحرف):
```python
_LST_SHP_MAP = {
    "LST_Annual_Mean": "LST_AnMean",
    "LST_Winter_Mean": "LST_WinMn",
    "LST_Spring_Mean": "LST_SprMn",
    "LST_Summer_Mean": "LST_SumMn",
    "LST_Autumn_Mean": "LST_AutMn",
    "LST_Annual_Range": "LST_AnRng",
    "LST_minus_T_Annual": "LST_mT_Ann",
    "LST_minus_T_Winter": "LST_mT_Win",
    "LST_minus_T_Spring": "LST_mT_Spr",
    "LST_minus_T_Summer": "LST_mT_Sum",
    "LST_minus_T_Autumn": "LST_mT_Aut",
    "LST_January_Mean": "LST_JanMn",
    # ... حتى December ...
    "LST_minus_T_January": "LST_mT_Jan",
    "LST_minus_T_February": "LST_mT_Feb",
    "LST_minus_T_March": "LST_mT_Mar",
    "LST_minus_T_April": "LST_mT_Apr",
    "LST_minus_T_May": "LST_mT_May",
    "LST_minus_T_June": "LST_mT_Jun",
    "LST_minus_T_July": "LST_mT_Jul",
    "LST_minus_T_August": "LST_mT_Aug",
    "LST_minus_T_September": "LST_mT_Sep",
    "LST_minus_T_October": "LST_mT_Oct",
    "LST_minus_T_November": "LST_mT_Nov",
    "LST_minus_T_December": "LST_mT_Dec",
}
SHP_FIELD_MAP.update(_LST_SHP_MAP)
```

#### 5. منطق الحساب في `compute_point_fields`:
أضف كود حساب مؤشرات العنصر داخل دالة الحساب:
```python
if "TS" in params_dict:
    # 1. المتوسطات الشهرية (عبر كل السنوات)
    # 2. المتوسط السنوي
    # 3. الفصول الأربعة (DJF, MAM, JJA, SON)
    # 4. المدى السنوي والفصلي
    # 5. الفروق السنوية والفصلية عن حرارة الهواء (LST - T)
    # 6. الفروق الشهرية الاثنا عشر (LST_m - T_m)
```

#### 6. فحوصات الجودة الفيزيائية (QA Checks):
في دالة `_run_qa`:
```python
if "LST_Annual_Mean" in row:
    val = row["LST_Annual_Mean"]
    if val is not None and not (-30.0 <= val <= 75.0):
        warnings.append("LST_Annual_Mean out of plausible range: {}".format(val))
```

---

### الخطوة 1.3: تعديل أداة الراستر `Toolboxes/raster_atlas_generator.py`

1. سجل الموديول في القوائم الرئيسية (`PRIMARY_MODULES_ALL`، `MODULE_FOLDER`، `MODULE_SHORT`، `POWER_PRIMARY_PARAM`، `COLOR_RAMPS`).
2. أضف أسماء حقول الـ Shapefile في `SHP_FIELD_MAP`.
3. **تسجيل الحقول المستهدفة بالراستر:** أضف في `MODULE_INDICATOR_FIELDS` الراسترات الأساسية الـ 11 فقط (واستثنِ الفوارق الشهرية منعاً لتوليد راسترات غير مطلوبة):
```python
MODULE_INDICATOR_FIELDS = {
    ...
    "Land Surface Temperature": [
        "LST_Annual_Mean",
        "LST_Winter_Mean",
        "LST_Spring_Mean",
        "LST_Summer_Mean",
        "LST_Autumn_Mean",
        "LST_Annual_Range",
        "LST_minus_T_Annual",
        "LST_minus_T_Winter",
        "LST_minus_T_Spring",
        "LST_minus_T_Summer",
        "LST_minus_T_Autumn",
    ],
}
```
4. أضف وسوم الراسترات الشهرية للمتوسطات:
```python
_MONTHLY_LABEL_BASE["Land Surface Temperature"] = ("LST", "Mean Land Surface Temperature")
```

---

### الخطوة 1.4: تحديث أدوات القاموس ودليل التصنيف

1. **ملف `generate_excel_dictionary.py`:**
   - أضف الحقول الـ 35 في `FIELDS_DATA`.
   - أضف الموديول في `MODULES_SUMMARY` (اسمه، كوده، عدد حقوله = 35).
   - حدّث العدادات الوصفية: إجمالي الحقول المناخية (330 مؤشراً) وحقول المعرفات (12 حقلاً إدارياً) ليصبح الإجمالي العام **342 حقلاً** عبر **19 موديولاً**.
   - شغّل السكربت لتحديث `docs/Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx`.

2. **ملف `generate_master_atlas_excel.py`:**
   - أضف الموديول إلى `MODULE_FOLDER_MAP` و `MODULES_METADATA`:
     ```python
     "19_Land_Surface_Temperature": {
         "ar_title": "درجة حرارة سطح الأرض",
         "en_title": "Land Surface Temperature",
         "unit": "°C",
         "scale_type": "standard",
     }
     ```

---

### الخطوة 1.5: الاختبار والتحقق الآلي للكود
قبل الانتقال لأي خطوة تالية، شغل حزم الاختبارات للتأكد من سلامة التطوير:
```powershell
python tests/test_power_atlas_108_offline.py
python tests/test_modifications.py
```
يجب أن تجتاز جميع الاختبارات بنسبة **100% نجاح (0 failures)**.

---

## 4. المسار الثاني: التطبيق التدريجي على قاعدة بيانات محملة مسبقاً (Incremental Execution)

> **سيناريو الواقع العملي:**  
> لديك مجلد مشروع كامل لدراسة مصر `Egypt Climate Data 1996-2025` يحتوي على:
> - جيوداتابيز `Climate_Database_From_1996_To_2025.gdb` (بها طبقة النقاط وجميع الطبقات من 01 إلى 18).
> - مجلدات الراسترات من `01_Temperature` إلى `18_Trends_And_Anomalies`.
> - مجلد `00_Tables_And_Reports` وملفات الإكسل الماستر.
> 
> **المطلوب:** إضافة الموديول الجديد `19_Land_Surface_Temperature` بنفس المعايير ودون التأثير على أي طبقة قائمة، وبحيث تتضمن الجيوداتابيز والإكسل جميع المؤشرات الـ 37 (بما فيها الفوارق الشهرية)، بينما تقتصر الراسترات على الـ 12 راستر الأساسية فقط.

---

### الخطوة 2.1: إعداد مجلد الـ Staging المؤقت
أنشئ مجلداً باسم الموديول مصحوباً بـ `_STAGING`:
```
C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature_STAGING\
```

---

### الخطوة 2.2: سحب البيانات الخام من NASA POWER وتخزين الكاش
استخرج إحداثيات النقاط (Lat, Lon) من طبقة النقاط (646 نقطة). قم بسحب باراميتر `TS` الشهري من 1996 إلى 2025 عبر API مع حفظ البيانات الخام في ملف كاش `JSON` محلي داخل `00_Tables_And_Reports\Egypt_TS_Raw_Monthly_1996_2025.json` لضمان عدم الحاجة لإعادة السحب:

```python
# نموذج طلب الـ API
url = (
    "https://power.larc.nasa.gov/api/temporal/monthly/point"
    "?parameters=TS&community=AG&longitude={:.4f}&latitude={:.4f}&start=1996&end=2025&format=JSON"
).format(lon, lat)
```

---

### الخطوة 2.3: حساب المؤشرات المناخية وتوليد مخرجات الـ Staging
احسب لكافة النقاط الـ 646 القيم التالية:
1. **المتوسطات الشهرية الـ 12:** متوسط كل شهر عبر السنوات الـ 30 (`LST_January_Mean` .. `LST_December_Mean`).
2. **المتوسط السنوي:** متوسط الـ 12 شهراً (`LST_Annual_Mean`).
3. **الفصول الأربعة:**
   - الشتاء (Winter): متوسط شهور (ديسمبر، يناير، فبراير).
   - الربيع (Spring): متوسط شهور (مارس، أبريل، مايو).
   - الصيف (Summer): متوسط شهور (يونيو، يوليو، أغسطس).
   - الخريف (Autumn): متوسط شهور (سبتمبر، أكتوبر، نوفمبر).
4. **المدى:**
   - السنوي (`LST_Annual_Range`) = أدفأ شهر - أبرد شهر. (تم الاستغناء عن المدى الفصلي تماشياً مع الهيكلية المبسطة المعتمدة).
5. **الفروق السنوية والفصلية:**
   - `LST_minus_T_Annual` = LST_Annual_Mean - T_Annual_Mean (من طبقة Temperature).
   - `LST_minus_T_Winter` = LST_Winter_Mean - T_Winter_Mean.
   - `LST_minus_T_Spring` = LST_Spring_Mean - T_Spring_Mean.
   - `LST_minus_T_Summer` = LST_Summer_Mean - T_Summer_Mean.
   - `LST_minus_T_Autumn` = LST_Autumn_Mean - T_Autumn_Mean.
6. **الفوارق الشهرية الاثنا عشر (حقول جدولية فقط):**
   - `LST_minus_T_January` حتى `LST_minus_T_December` بطرح متوسط حرارة الهواء للشهر نفسه من حرارة السطح.

قم بتصدير الملفات الآتية داخل مجلد الـ Staging:
- **ملف CSV:** `19_Land_Surface_Temperature.csv` (ترميز `utf-8` بدون BOM، يحتوي على المؤشرات السنوية والفصلية).
- **ملف إكسل ثنائي الشيتات:** `19_Land_Surface_Temperature.xls`:
  - **شيت `Data`** (23 عموداً): 12 حقلاً إدارياً + السنوي (1) والفصول الأربعة (4) والمدى السنوي (1) والفوارق السنوية والفصلية الخمسة (5).
  - **شيت `Month`** (28 عموداً): 4 أعمدة إدارية + 12 متوسط شهري + 12 فارق شهري.
- **نسخ متزامنة:** انسخ ملف `.xls` إلى `00_Tables_And_Reports\Land_Surface_Temperature.xls` وملف المناخ الشهري إلى `00_Tables_And_Reports\Monthly_Climatology\Land_Surface_Temperature.csv`.
- **ملف GeoJSON:** `19_Land_Surface_Temperature_Grid_Points.geojson`.
- **ملف Shapefile:** `19_Land_Surface_Temperature_Grid_Points.shp` مع أسماء أعمدة $\le 10$ أحرف لكافة المؤشرات الـ 35.

---

### الخطوة 2.4: إنشاء وتعبئة الطبقة في الجيوداتابيز (ArcPy GDB Feature Class)
استخدم سكربت Python (بواسطة `C:\Python27\ArcGIS10.8\python.exe`) لتنفيذ الآتي داخل الجيوداتابيز:

1. إنشاء Feature Class باسم `Land_Surface_Temperature`:
```python
import arcpy

gdb = r"C:\...\Climate_Database_From_1996_To_2025.gdb"
fc_name = "Land_Surface_Temperature"
target_fc = gdb + "\\" + fc_name

# إنشاء الطبقة بنظام إحداثيات Web Mercator (3857)
arcpy.CreateFeatureclass_management(
    gdb, fc_name, "POINT", spatial_reference=arcpy.SpatialReference(3857)
)
```

2. إضافة الحقول الإدارية الـ 12 (`OBJECTID`, `Point_ID`, `Point_Lat`, `Point_Lon`, `Elev_m`, `Data_Start`, `Data_End`, `Temporal`, `Interp_Meth`, `Cell_Size`, `Wind_Cell`, `Status`).
3. إضافة حقول المؤشرات الـ 35 كنوع `DOUBLE` مع **الالتزام الصارم بشرط الألياس**:
```python
for field_name in LST_INDICATOR_FIELDS:
    # الألياس مطابق للاسم الإنجليزي 100%
    arcpy.AddField_management(
        target_fc, field_name, "DOUBLE", field_alias=field_name
    )
```
4. فتح `arcpy.da.InsertCursor` وتعبئة القيم المحسوبة بالكامل لكل نقطة من ملف JSON.
5. التحقق البرمجي:
```python
count = int(arcpy.GetCount_management(target_fc)[0])
assert count == 646, "Row count mismatch!"
for f in arcpy.ListFields(target_fc):
    if f.type not in ("OID", "Geometry"):
        assert f.name == f.aliasName, "Alias mismatch for field: " + f.name
```

---

### الخطوة 2.5: توليد الراسترات السطحية (Surface Rasters via Spline)
أنشئ مجلد الراسترات الفعلي:
`C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature\`

استخدم بيئة ArcPy Spatial Analyst لتوليد الراسترات الأساسية الـ 11 بدقة متناهية:
```python
import os
import arcpy
from arcpy.sa import Spline, ExtractByMask

arcpy.CheckOutExtension("Spatial")

ref_raster = r"C:\...\Egypt Climate Data 1996-2025\01_Temperature\T_Annual_Mean.tif"
mask_poly = r"C:\...\Egypt Climate Data 1996-2025\Climate_Database_From_1996_To_2025.gdb\Egypt"

arcpy.env.snapRaster = ref_raster
arcpy.env.cellSize = 250.0  # 250m
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)
arcpy.env.compression = "LZW"

out_dir = r"C:\...\Egypt Climate Data 1996-2025\19_Land_Surface_Temperature"

rasters_to_build = [
    "LST_Annual_Mean",
    "LST_Winter_Mean",
    "LST_Spring_Mean",
    "LST_Summer_Mean",
    "LST_Autumn_Mean",
    "LST_Annual_Range",
    "LST_minus_T_Annual",
    "LST_minus_T_Winter",
    "LST_minus_T_Spring",
    "LST_minus_T_Summer",
    "LST_minus_T_Autumn",
]

for field in rasters_to_build:
    out_tif = os.path.join(out_dir, field + ".tif")
    surf = Spline(target_fc, field, cell_size=250.0, spline_type="TENSION", weight=30.0, n_points=12)
    clipped = ExtractByMask(surf, mask_poly)
    clipped.save(out_tif)
    arcpy.CalculateStatistics_management(out_tif)
    arcpy.BuildPyramids_management(out_tif)
```

> [!WARNING]
> **قاعدة الاستبعاد الحاسم للراستر:**  
> - **لا يتم توليد أي راستر لمؤشرات `*_Month_Mean` الملغاة نهائياً**.
> - **يُمنع منعاً باتاً توليد راسترات للفوارق الشهرية الاثنا عشر**؛ حيث تظل حقولاً جدولية داخل الجيوداتابيز والإكسل فقط ولا تخرج كراسترات.

---

### الخطوة 2.6: توليد دليل التصنيف وتحديث القواميس الماستر
بعد توليد الراسترات الـ 11 وحساب إحصائياتها، شغّل أداة دليل التصنيف الماستر:
```powershell
python generate_master_atlas_excel.py --base_dir "C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025" --study_area "Egypt"
```
**النتيجة:**
- يقرأ السكربت إحصائيات ملفات الـ TIFF الـ 11 ويولّد شيت `19_Land_Surface_Temperature` في ملف `Climate_Atlas_Classification_Guide.xlsx`.
- يحتوي الشيت على 4 جداول منفصلة لفئات التصنيف (3 فئات، 5 فئات، 7 فئات، 9 فئات).

ثم قم بنسخ وتحديث قاموس الحقول:
- نسخ `docs\Climate_Atlas_Fields_Dictionary_AR_EN_Units.xlsx` (342 حقلاً) إلى مجلد المشروع و`00_Tables_And_Reports\`.

---

## 5. قائمة الفحص والتدقيق النهائي (QA/QC Checklist)

قبل اعتبار العملية مكتملة وناجحة، تحقق من استيفاء الجدول التالي:

| # | عنصر الفحص | المعيار المقبول | أداة التحقق |
|:---:|:---|:---|:---|
| **1** | عدد باراميترات الأداة الرئيسية | 65 باراميتر بالضبط | كود `.pyt` في ArcMap |
| **2** | عدد باراميترات أداة الراستر | 33 باراميتر بالضبط | كود `Toolboxes/raster_atlas_generator.py` |
| **3** | عدد سجلات الـ Feature Class | 646 نقطة (مطابق لطبقة العينة) | `arcpy.GetCount_management` |
| **4** | إجمالي حقول الـ Feature Class | 47 حقلاً (12 إداري + 35 مؤشر) | `arcpy.ListFields` |
| **5** | تطابق أسماء الحقول مع الألياس | `name == aliasName` بنسبة 100% | `arcpy.ListFields` |
| **6** | أطوال أسماء حقول Shapefile | $\le 10$ أحرف دون تكرار | فحص ملف `.dbf` |
| **7** | عدد راسترات الموديول 19 | 11 ملف `.tif` أساسي فقط | فحص المجلد `19_...` |
| **8** | استبعاد الراسترات غير المطلوبة | عدم وجود راسترات ملغاة وعدم وجود راسترات الفوارق الشهرية | فحص المجلد |
| **9** | محاذاة وخصائص الراسترات | Snap = T_Annual_Mean, Cell = 250m, Mask = Egypt | ArcMap Raster Properties |
| **10** | هيكل شيتات ملف الإكسل | شيت `Data` (23 عموداً) وشيت `Month` (28 عموداً) | `xlrd` / Excel |
| **11** | شيت دليل التصنيف الجديد | وجود شيت `19_Land_Surface_Temperature` (فئات 3، 5، 7، 9) | `openpyxl` / Excel |
| **12** | عدد الحقول في القاموس الشامل | 342 حقلاً و 19 موديولاً (330 مناخي + 12 إداري) | `Climate_Atlas_Fields_Dictionary` |
| **13** | سلامة الاختبارات البرمجية | جميع الاختبارات ناجحة بنسبة 100% | `test_power_atlas_108_offline.py` |

---

## 6. الخلاصة

باتباع هذه الخطوات المنهجية بدقة:
1. تصبح منظومة الأطلس قابلة للتوسع اللانهائي لدعم أي عنصر مناخي إضافي مستقبلاً (مثل: رطوبة التربة Soil Moisture، النتح التبخري الفعلي Actual Evapotranspiration، مؤشرات الجفاف SPEI، وغيرها).
2. يمكن تطعيم وتحديث أي قاعدة بيانات سابقة للمشروع دون الحاجة لإعادة سحب أو معالجة العناصر الأخرى، مع الحفاظ الكامل على سلامة البيانات والاتساق الهندسي والإحصائي الشامل.
