# Climate Data Sources: Multi-Provider Directory & Comparison Guide
# دليل ومقارنة مصادر ونماذج البيانات المناخية

## 1. Executive Summary / ملخص تنفيذي
This directory houses the technical specifications, temporal coverage parameters, and variable matrices for the five authoritative climate data sources integrated into the **MIRSAD Climate Atlas Generator (Spatial Points & Gridded Rasters)**.

يحتوي هذا المجلد على التوصيفات الفنية، ونطاقات التغطية الزمنية، ومصفوفة المتغيرات للمصادر المناخية الخمسة المعتمدة في منظومة مِرصاد لتوليد الأطلس المناخي (للنقاط المكانية والبيانات الشبكية).

---

## 2. Quick Comparison Matrix / جدول المقارنة السريع والملخص

| Data Source / مصدر البيانات | Start Year / سنة البداية | End Year / سنة النهاية | Spatial Resolution / الدقة المكانية | Primary Nature / طبيعة البيانات | Zero-Gap Guarantee / ضمان اكتمال البيانات |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Hybrid Climate Engine (Default)**<br>النموذج الهجين (الافتراضي للأداة) | **1901** | **Present**<br>الوقت الحاضر | Station Physical Point<br>إحداثيات المحطة | Fused (Ground + Satellite + ERA5)<br>رصد أرضي مدمج مع الأقمار ونماذج ERA5 | **100% Guaranteed**<br>مضمون 100% بدون أي خلايا مفقودة |
| **NOAA ISD / GHCN Ground Archive**<br>أرشيف الرصد الأرضي المباشر | **1901**<br>*(1850s)* | **Present (Real-Time)**<br>الوقت الحاضر (فوري) | Station Physical Point<br>أجهزة ومستشعرات المحطة | 100% Physical Instruments<br>رصد ميداني بحت من أجهزة المحطة | ⚠️ Subject to sensor gaps<br>معرض لفجوات صيانة الحساسات |
| **NASA POWER Agroclimatology**<br>نموذج ناسا الزراعي والطاقة | **1981**<br>*(1984 Solar)* | **Present (2-4 days)**<br>الوقت الحاضر (تأخير 2-4 أيام) | $0.5^\circ \times 0.625^\circ$<br>(~50 × 60 km) | Gridded MERRA-2 + CERES<br>إعادة تحليل شبكية عالمية | **100% Gridded**<br>شبكي مكتمل عالمياً |
| **Copernicus Climate Data Store (CDS)**<br>مخزن بيانات كوبرنيكوس الأوروبي | **1940**<br>*(1950 ERA5-Land)* | **Present (2-5 days)**<br>الوقت الحاضر (تأخير 2-5 أيام) | **$0.10^\circ$ (~9–11 km)**<br>دقة مكانية فائقة | Gridded C3S Reanalysis<br>إعادة تحليل أوروبية رسمية معتمدة | **100% Gridded**<br>شبكي مكتمل عالمياً |
| **Open-Meteo ERA5 / ERA5-Land**<br>النموذج الأوروبي عالي الدقة | **1940**<br>*(1950 ERA5-Land)* | **Present (2-5 days)**<br>الوقت الحاضر (تأخير 2-5 أيام) | **$0.10^\circ$ (~9–11 km)**<br>دقة مكانية فائقة | Gridded ERA5-Land Terrestrial<br>إعادة تحليل شبكية معدلة طبوغرافياً | **100% Gridded**<br>شبكي مكتمل عالمياً |

---

## 3. Climatological Elements Breakdown / تفصيل العناصر المناخية

| Parameter / العنصر المناخي | Hybrid Engine | NOAA ISD Ground | NASA POWER API | Copernicus CDS | Open-Meteo ERA5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Air Temperature (T, Tmax, Tmin) / درجات الحرارة** | ✅ Observed + Gap-Fill | ✅ True Ground Sensor | ✅ MERRA-2 Grid | ✅ ERA5-Land (~9 km) | ✅ ERA5-Land Grid (~9 km) |
| **Dew Point & Relative Humidity / الرطوبة والندى** | ✅ Observed + Gap-Fill | ✅ True Ground Sensor | ✅ MERRA-2 Grid | ✅ ERA5-Land (~9 km) | ✅ ERA5-Land Grid (~9 km) |
| **Sea Level Pressure (PSL) / الضغط والآيزوبار** | ✅ Observed + Gap-Fill | ✅ True Ground Sensor | ✅ Surface Pressure | ✅ ERA5-Land (~9 km) | ✅ ERA5-Land Grid (~9 km) |
| **Wind Speed & Direction / سرعة واتجاه الرياح** | ✅ Observed + Gap-Fill | ✅ True Ground Sensor | ✅ MERRA-2 Grid | ✅ ERA5-Land (~9 km) | ✅ ERA5-Land Grid (~9 km) |
| **Precipitation / كميات ومعدلات الأمطار** | ✅ Observed + Gap-Fill | ✅ True Ground Sensor | ✅ Bias-Corrected | ✅ ERA5-Land (~9 km) | ✅ ERA5-Land Grid (~9 km) |
| **Cloud Cover / الغطاء السحابي** | ✅ Observed + Gap-Fill | ✅ True Ground Sensor | ✅ MERRA-2 Grid | ✅ ERA5-Land (~9 km) | ✅ ERA5-Land Grid (~9 km) |
| **Solar Radiation / الإشعاع الشمسي** | ✅ Satellite CERES Fusion | ❌ Sparse / BSRN Only | ✅ CERES Gold Standard | ✅ Radiative Model | ✅ Radiative Model |
| **UV Index / الأشعة فوق البنفسجية** | ✅ Satellite CERES Fusion | ❌ Not Measured | ✅ FLASHFlux Daily | ❌ Estimated | ❌ Estimated |
| **Land Surface Temp (LST) / حرارة سطح الأرض** | ✅ Satellite Skin Fusion | ❌ Not Measured | ✅ MERRA-2 TS Skin | ✅ ERA5 Skin Temp | ✅ ERA5 Skin Temp |
| **Soil Temp & Moisture / حرارة ورطوبة التربة** | ⚠️ Optional | ❌ Not Measured | ❌ Not Available | ✅ 4 Depths (0–255 cm) | ✅ 4 Depths (0–255 cm) |
| **Bioclimatic Submodels (HI, WC, ET, Aridity)** | ✅ Computed 100% | ✅ Computed from Data | ✅ Computed from Data | ✅ Computed 100% | ✅ Computed from Data |

---

## 4. Directory Subfolders / محتويات المجلدات الفرعية

1. **[01_Hybrid_Engine_NOAA_NASA_ERA5/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/01_Hybrid_Engine_NOAA_NASA_ERA5/)**
   - Documentation & profiles for the Default Hybrid Climatology Engine (1901–Present).
   - التوثيق الشامل للنموذج الهجين المعتمد افتراضياً (1901 إلى الآن).
2. **[02_NOAA_ISD_GHCN_Ground_Stations/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/02_NOAA_ISD_GHCN_Ground_Stations/)**
   - Direct physical station sensor records (1901–Present, Real-Time).
   - سجلات الرصد الميداني المباشر من أجهزة المحطة (1901 إلى الآن، فوري).
3. **[03_NASA_POWER_Agroclimatology/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/03_NASA_POWER_Agroclimatology/)**
   - Gridded agroclimatology and solar energy data (1981–Present).
   - بيانات ناسا الزراعية والإشعاع الشمسي (1981 إلى الآن).
4. **[04_Open_Meteo_ERA5_Reanalysis/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/04_Open_Meteo_ERA5_Reanalysis/)**
   - High-resolution European ERA5 & ERA5-Land reanalysis (1940–Present, ~9 km).
   - النموذج الأوروبي عالي الدقة المكانية ERA5-Land (1940 إلى الآن، ~9 كم).
5. **[05_Copernicus_Climate_Data_Store_CDS/](file:///D:/My%20Software/NASA%20POWER%20Climate%20Atlas%20Generator/Documents/05_Climate_Data_Sources_Directory/05_Copernicus_Climate_Data_Store_CDS/)**
   - Official European C3S Copernicus Climate Data Store specifications (1940–Present, ~9 km).
   - المواصفات الفنية المعتمدة لمخزن بيانات كوبرنيكوس الأوروبي (1940 إلى الآن، ~9 كم).

---

## 5. Capabilities vs Limitations Matrix / مصفوفة ما يوفره وما يعجز عن توفيره كل مصدر

| Data Source / مصدر البيانات | ما يستطيع المصدر توفيره بدقة (Capabilities) | ما لا يستطيع المصدر توفيره (Limitations) |
| :--- | :--- | :--- |
| **Hybrid Climate Engine**<br>*(Default / الافتراضي)* | • تغطية 100% لكافة الموديلات الـ 19 دون أي قيم مفقودة.<br>• رصد مادي حقيقي لأجهزة المحطة (حرارة، رطوبة، ضغط، رياح، أمطار).<br>• دمج الإشعاع الشمسي والـ UV من الأقمار الصناعية (CERES).<br>• حساب كامل لجميع النماذج البيومناخية الـ 8.<br>• ضمان خلو أسطح الراستر النهائية من أي بكسلات فارغة. | • لا يوفر قراءات بيرانوميتر أرضية (يعتمد على الأقمار الصناعية).<br>• لا يوفر مقاطع رطوبة وحرارة التربة بالأعماق المتعددة لجميع المحطات.<br>• لا يصلح كبديل للتقارير الجنائية القضائية التي تشترط السجلات الخام دون استكمال.<br>• لا يمكنه استكمال ثغرات المحطات المتوقفة قبل عام 1940. |
| **NOAA ISD / GHCN Archive**<br>*(Ground Truth / رصد أرضي)* | • حقيقة أرضية مادية 100% من أجهزة المحطة مباشرة دون أي نمذجة.<br>• حرارة الهواء، ونقطة الندى، والرطوبة النسبية.<br>• ضغط سطح المحطة وضغط مستوى البحر (PSL) والآيزوبار.<br>• سرعة واتجاه الرياح وهبات الرياح القصوى (Wind Gusts).<br>• كميات الأمطار اليومية والساعية وحالات الطقس الحاضر.<br>• حجية قانونية رسمية وموثوقية معتمدة للتقارير القضائية. | • **لا يوفر الإشعاع الشمسي (Solar Radiation)** لمعظم المحطات.<br>• **لا يوفر مؤشر الأشعة فوق البنفسجية (UV Index)**.<br>• **لا يوفر حرارة سطح الأرض الإشعاعية (LST)**.<br>• **لا يوفر مقاطع رطوبة وحرارة التربة بالأعماق**.<br>• معرض لوجود قيم مفقودة وفترات انقطاع بسبب صيانة الحساسات.<br>• لا يوفر تغطية شبكية في المناطق الخالية من أبراج المحطات. |
| **NASA POWER Agroclimatology**<br>*(Agro & Solar / زراعي وشمسي)* | • المعيار العالمي الذهبي للإشعاع الشمسي السطحي (CERES).<br>• مؤشر الأشعة فوق البنفسجية اليومي (UV Index) الفضائي.<br>• تغطية شبكية عالمية متصلة 100% بدون أي فجوات مكانية.<br>• درجات حرارة الهواء على ارتفاع 2م وحرارة جلد الأرض (LST).<br>• سرعة الرياح على ارتفاعات 2م و 10م و 50م واتجاه الرياح.<br>• معدل الأمطار المصحح ونسبة الغطاء السحابي الكلي. | • **لا يوفر بيانات تاريخية قبل 1 يناير 1981** (1901-1980 غير متوفر).<br>• **لا يوفر هبات الرياح اللحظية القصوى (Wind Gusts)**.<br>• **لا يوفر ضغط مستوى سطح البحر (PSL) مباشرة** (يوفر الضغط السطحي PS فقط).<br>• **لا يوفر رطوبة أو حرارة التربة بالأعماق** (0-255 سم).<br>• دقة الخلية واسعة (~50 × 60 كم) لا تلتقط تضاريس الأودية الجبلية الضيقة.<br>• يتأخر من 2 إلى 4 أيام عن التاريخ الحالي (ليس لحظياً). |
| **Copernicus Climate Data Store (CDS)**<br>*(Official European C3S / كوبرنيكوس)* | • المرجع العالمي المعتمد دولياً لدى WMO و IPCC لإعادة التحليل المناخي.<br>• دقة مكانية فائقة لليابسة: **0.10° (~9 كم)** مع تصحيح الانحدار الطبوغرافي.<br>• سلسلة تاريخية متصلة تفوق 85 عاماً (1940 إلى الوقت الحاضر).<br>• استيعاب بيانات 4D-Var متقدم جداً يدمج مليارات الأرصاد السطحية والجوية والفضائية.<br>• رطوبة وحرارة التربة عند 4 أعماق متتالية (0-255 سم).<br>• دعم اختياري للمفتاح الشخصي واستخراج سلس بدون كلمة مرور. | • **لا يوفر بيانات تاريخية قبل عام 1940** (1901-1939 غير مشمول).<br>• **ليس رصداً مادياً نقياً لحساس المحطة** (هو نموذج استيعابي ناتج عن محاكاة فيزيائية).<br>• **لا يشمل سيناريوهات التغير المناخي المستقبلية** (مستبعدة مؤقتاً تماشياً مع النطاق).<br>• يتأخر من يومين إلى 5 أيام عن التاريخ الحالي لإجراء المراجعات والتدقيق. |
| **Open-Meteo ERA5 / ERA5-Land**<br>*(High-Res Reanalysis / فائق الدقة)* | • أعلى دقة مكانية عالمية في نماذج إعادة التحليل لليابسة: **0.10° (~9 كم)**.<br>• سلسلة زمنية تاريخية مستمرة لأكثر من 85 عاماً (1940 إلى الآن).<br>• مراعاة انحدار درجات الحرارة مع الارتفاع والتضاريس (DEM).<br>• درجات حرارة الهواء، والحرارة المحسوسة، وهبات الرياح (Gusts).<br>• ضغط مستوى سطح البحر المباشر عالي الدقة (PSL).<br>• **رطوبة وحرارة التربة عند 4 أعماق متتالية (0-255 سم)**.<br>• البخر-نتح المرجعي القياسي ET0 بمعادلة فاو-56 بنمان مونتيث. | • **لا يوفر بيانات تاريخية قبل عام 1940** (1901-1939 غير متوفر).<br>• **لا يوفر مؤشر UV الفضائي المباشر** (يقدم تقديرات إشعاعية عامة).<br>• **ليس رصداً مادياً حقيقياً لأجهزة المحطة** (هو نموذج رياضي استيعابي).<br>• يتأخر من 2 إلى 5 أيام عن التاريخ الحالي لإجراء المراجعات والتدقيق. |

---

## 6. Decision Rules / قواعد اختيار المصدر للباحث
- **لأطلس المحطات الرسمي وإنتاج خرائط خالية 100% من الخلايا الفارغة:** اختر **Hybrid Engine** (الافتراضي).
- **للتدقيق الأكاديمي والرصد الميداني البحت من موازين الحرارة والبارومترات:** اختر **NOAA ISD Ground**.
- **لدراسات الطاقة الشمسية والزراعة بعد عام 1981:** اختر **NASA POWER API**.
- **للمناطق الجبلية والتضاريس الوعرة، أو دراسات التربة، أو الفترات من 1940 إلى 1980:** اختر **Open-Meteo ERA5**.

