# الدليل العلمي والفني الشامل لمنظومة أطلس المناخ
## NASA POWER & Open-Meteo Climate Atlas Generator
### المرجع الأكاديمي والتقني التنفيذي الكامل لجميع المؤشرات والمعادلات ومصادر البيانات والطبقات (115 حقل مناخي وإداري)

**إعداد الباحث:** أحمد إبراهيم (Ahmad Ibrahim)  
**البريد الإلكتروني:** ahmadibrahim.geo@gmail.com  
**تاريخ التحديث:** أكتوبر 2026  

---

## 1. نظرة عامة ورؤية المشروع العلمية

تعتبر منظومة **NASA POWER & Open-Meteo Climate Atlas Generator** منصة برمجية وجيومعلوماتية متقدمة تعمل كأداة جغرافية تنفيذية (ArcGIS Python Toolbox - `.pyt`) ومكتبة برمجية مستقلة (`Toolboxes/raster_atlas_generator.py`) متوافقة بصورة كاملة مع بيئات **ArcGIS Desktop (ArcMap 10.8)** و **ArcGIS Pro (2.8+ / 3.x)**.

تهدف الأداة إلى سد الفجوة المكانية والزمنية الناتجة عن ندرة محطات الأرصاد الجوية السطحية في المناطق الجافة وشبه الجافة (خاصة الشرق الأوسط وشمال إفريقيا)، وذلك من خلال الدمج الآلي بين النماذج المناخية العالمية لإعادة التحليل (Atmospheric Reanalysis) والبيانات الرادارية والإشعاعية الفضائية الصادرة عن وكالة الفضاء الأمريكية (NASA) والمركز الأوروبي للتنبؤات الجوية متوسطة المدى (ECMWF)، وصولاً إلى إنشاء أسطح راستر مستمرة ومصفوفات جغرافية تحتوي على **103 مؤشر مناخي تخصصي** و **12 حقل بيانات إدارية وفنية** (بإجمالي **115 حقل** موزعة على **18 موديول مناخي مستقل**).

---

## 2. مصفوفة الموديلات المناخية الـ 18 والمجلدات الناتجة

| رمز الموديول | العنصر المناخي | مجلد الراستر الناتج | عدد الحقول | المتغيرات الأصلية المدخلة | التوصيف الفيزيائي |
|:---:|:---|:---|:---:|:---|:---|
| **00** | البيانات الإدارية والنظامية | `-` (سمات وصفية) | 12 | إحداثيات ومحددات وقت التشغيل | معرّف النقطة، الإحداثيات، التاريخ، طريقة الاستيفاء |
| **01** | درجات حرارة الهواء (Temperature) | `01_Temperature` | 10 | `T2M`, `T2M_MAX`, `T2M_MIN` | المتوسط السنوي والفصلي، المدى، والقصوى والدنيا |
| **02** | تساقط الأمطار (Precipitation) | `02_Precipitation` | 8 | `PRECTOTCORR` | المتوسط السنوي للتراكمات، المعدل الشهري، المجاميع الفصلية |
| **03** | الضغط عند مستوى البحر (Sea Level Pressure) | `03_Sea_Level_Pressure` | 6 | `PSL` | الضغط المخفض لمستوى سطح البحر هيدروستاتيكياً |
| **04** | الضغط الجوي السطحي (Surface Pressure) | `04_Surface_Pressure` | 6 | `PS` | الضغط الجوي الفعلي عند منسوب تضاريس المحطة |
| **05** | سرعة واتجاه الرياح (Wind) | `05_Wind` | 13 | `WS10M`, `U2M`, `V2M` | السرعة القياسية والمتوسط الاتجاهي الدائري لمتجهات الرياح |
| **06** | الرطوبة النسبية (Relative Humidity) | `06_Relative_Humidity` | 6 | `RH2M` | نسبة تشبع الهواء ببخار الماء عند 2 متر |
| **07** | درجة حرارة نقطة الندى (Dew Point) | `07_Dew_Point` | 6 | `T2MDEW` | المقياس المباشر لكتلة بخار الماء المطلقة في الهواء |
| **08** | الإشعاع الشمسي (Solar Radiation) | `08_Solar_Radiation` | 7 | `ALLSKY_SFC_SW_DWN` | المعدل اليومي (kWh/m²/day) والتراكمي السنوي الإجمالي |
| **09** | مؤشر الأشعة فوق البنفسجية (UV Index) | `09_UV_Index` | 6 | `ALLSKY_SFC_UV_INDEX` | مؤشر الخطر الصحي والإشعاعي عند الظهيرة الشمسية |
| **10** | الغطاء السحابي (Cloud Cover) | `10_Cloud_Cover` | 6 | `CLDTOT` | النسبة المئوية لمساحة قبة السماء المغطاة بالسحب |
| **11** | الإجهاد الحراري (Heat Index & WBGT) | `11_Heat_Index` | 5 | مشتق (`T2M`, `RH2M`) | معادلة روثفوس، درجة حرارة البصيلة الرطبة (Stull)، وWBGT |
| **12** | عامل برودة الرياح (Wind Chill) | `12_Wind_Chill` | 2 | مشتق (`T2M`, `WS10M`) | معادلة NWS المشتركة لفقدان الحرارة بالحمل |
| **13** | مؤشر دومارتون للجفاف (De Martonne) | `13_De_Martonne_Aridity` | 1 | مشتق (`R_Annual_Mean`, `T_Annual_Mean`) | $I_{DM} = P / (T + 10)$ لتصنيف الأقاليم المناخية |
| **14** | البخر-نتح المرجعي (Evapotranspiration) | `14_Evapotranspiration` | 9 | مشتق (`Ra`, `T`, `Tmax`, `Tmin`) | نموذج هارجريفز-ساماني (1985) والاحتياجات المائية |
| **15** | مؤشر الجفاف الدولي (UNEP Aridity) | `15_UNEP_Aridity` | 1 | مشتق (`R_Annual_Mean`, `PET_HarAnn`) | نسبة $P / PET$ المعتمدة لدى الأمم المتحدة لمكافحة التصحر |
| **16** | العجز المائي المناخي (Water Deficit) | `16_Water_Deficit` | 1 | مشتق (`R_Annual_Mean`, `PET_HarAnn`) | الميزان المائي الصافي $P - PET$ (سالب = عجز) |
| **17** | عدد الأشهر الجافة (Dry Months Count) | `17_Dry_Months` | 1 | مشتق (`P_m`, `T_m` لـ 12 شهر) | معيار باجنول-جوسن البيوكليماتي ($P < 2T$) |
| **18** | الاتجاهات المناخية والتغير (Trends) | `18_Trends_And_Anomalies` | 9 | مشتق من السلاسل الزمنية | انحدار OLS للعقد الزمني ومقارنة 2011-2020 بالأساس 1991-2020 |
| **المجموع** | **جميع الموديلات المناخية الـ 18** | **18 مجلد راستر** | **115** | **12 إداري + 103 مؤشر مناخي** | **التغطية الكاملة لجميع الأبعاد المناخية والبيئية** |

---

## 3. التوثيق العلمي الدقيق لمؤشرات الأمطار وحسم التسميات

### 3.1 المعضلة الفيزيائية والرياضية
تخرج بيانات الأمطار من نماذج ناسا بوحدة معدل يومي ($PRECTOTCORR$ بوحدة $\text{mm/day}$)، ولحساب الأمطار التراكمية لكل شهر يتم ضرب المعدل اليومي في عدد أيام الشهر الفعلي ($28, 29, 30, \text{ أو } 31$ يوماً).

وعند تجميع بيانات 30 سنة كاملة (فترة الأساس القياسية 1991–2020)، تخرج الأداة بمؤشرين أساسيين تم توحيد مسمياتهما عالمياً ورسمياً في الكود وقواعد البيانات:

1. **المتوسط السنوي لتساقط الأمطار (`R_Annual_Mean`)**:
   - **الوحدة**: ملم/سنة (mm/year).
   - **المعادلة الرياضية**:
     $$R_{Annual\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \left(\sum_{m=1}^{12} P_{y, m}\right) = \sum_{m=1}^{12} \overline{P}_m$$
   - **التفسير الفيزيائي**: يمثل **متوسط مجموع الأمطار المتساقطة خلال السنة الواحدة** على مدار الـ 30 عاماً. في شمال مصر (الساحل الشمالي والإسكندرية) تبلغ هذه القيمة حوالي **200 إلى 224 ملم/سنة**، وفي القاهرة حوالي **25 ملم/سنة**، وفي أسوان أقل من **2 ملم/سنة**.
   - **التطور التاريخي**: كان يسمى في الإصدارات القديمة للأداة باسم `R_Annual_Total`، وتم استبداله رسمياً بـ `R_Annual_Mean` ليعبر بدقة عن أنه **متوسط المجاميع السنوية** عبر فترة الأساس المناخية.

2. **المتوسط الشهري لتساقط الأمطار (`R_Month_Mean`) [حقل ملغى / Retired]:**
   *(تم استبعاده في الهيكلية المبسطة المعتمدة لتطابقه الرياضي التام مع المتوسط السنوي)*
   - **الوحدة**: ملم/شهر (mm/month).
   - **المعادلة الرياضية**:
     $$R_{Month\_Mean} = \frac{R_{Annual\_Mean}}{12} = \frac{1}{12} \sum_{m=1}^{12} \overline{P}_m$$
   - **التفسير الفيزيائي**: يمثل **المعدل الشهري لماء المطر** الناتج عن قسمة المتوسط السنوي الكلي على 12 شهراً. في محطة يبلغ متوسطها السنوي 224 ملم، يكون المتوسط الشهري الناتج هو $224 / 12 = \mathbf{18.67\text{ mm/month}}$.
   - **التطور التاريخي**: كان يسمى سابقاً باسم `R_Annual_Mean`، وتم تعديل تسميته إلى `R_Month_Mean` ليعبر بدقة عن كونه معدلاً شهرياً وليس مجموعاً سنوياً.

3. **متوسطات هطول الأمطار الفصلية (Seasonal Mean Precipitation)**:
   - **الوحدة**: مم/فصل (mm/season).
   - **المعادلة الرياضية الحسابية**:
     $$R_{Winter\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \left(P_{y, 12} + P_{y, 1} + P_{y, 2}\right)$$
     $$R_{Spring\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \left(P_{y, 3} + P_{y, 4} + P_{y, 5}\right)$$
     $$R_{Summer\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \left(P_{y, 6} + P_{y, 7} + P_{y, 8}\right)$$
     $$R_{Autumn\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \left(P_{y, 9} + P_{y, 10} + P_{y, 11}\right)$$
   - **المعنى الفيزيائي والحسابي**: تمثل هذه الحقول **متوسط مجموع هطول الأمطار خلال الفصل** عبر جميع السنوات الكاملة لفترة الدراسة. استخدام كلمة `Mean` بدلاً من `Total` يعكس بدقة أن القيمة هي متوسط سنوي للأمطار الفصلية وليست مجموع أمطار الـ 30 عاماً مجتمعة.
   - **المسميات المعتمدة رسمياً**:
     * `R_Winter_Mean` (متوسط هطول الأمطار خلال فصل الشتاء)
     * `R_Spring_Mean` (متوسط هطول الأمطار خلال فصل الربيع)
     * `R_Summer_Mean` (متوسط هطول الأمطار خلال فصل الصيف)
     * `R_Autumn_Mean` (متوسط هطول الأمطار خلال فصل الخريف)

---

## 4. الفصول المناخية الأربعة والعمليات الرياضية الدائرية للرياح

### 4.1 الفصول المناخية المعتمدة عالمياً (WMO)
- **فصل الشتاء (DJF)**: يشمل ديسمبر، يناير، وفبراير (أشهر 12، 1، 2).
- **فصل الربيع (MAM)**: يشمل مارس، أبريل، ومايو (أشهر 3، 4، 5).
- **فصل الصيف (JJA)**: يشمل يونيو، يوليو، وأغسطس (أشهر 6، 7، 8).
- **فصل الخريف (SON)**: يشمل سبتمبر، أكتوبر، ونوفمبر (أشهر 9، 10، 11).

### 4.2 الحساب المتجهي لاتجاه الرياح السائد (Circular Vector Mean)
لحساب الاتجاه السائد للرياح دون الوقوع في خطأ المتوسط الحسابي البسيط (حيث أن متوسط 350° و10° هو 180° جنوباً وهو خطأ كارثي بينما الصحيح هو 360° شمالاً)، يتم تطبيق التحليل الدائري لمركبات المتجهات:
$$u = -\sin\left(\frac{\pi \cdot \theta}{180}\right), \quad v = -\cos\left(\frac{\pi \cdot \theta}{180}\right)$$
$$\overline{\theta} = \text{atan2}(-\overline{u}, -\overline{v}) \pmod{360^\circ}$$

---

## 5. المعجم الشامل والمفصل لجميع الحقول الـ 115 (19 عمود لكل حقل)

### 001. `OBJECTID` (المعرف الرقمي التسلسلي الفريد للظاهرة في قاعدة البيانات الجغرافية (Geodatabase OID). / OBJECTID)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `OBJECTID` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `OBJECTID` |
| **2** | **الاسم بالإنجليزية** | OBJECTID |
| **3** | **الاسم بالعربية** | المعرف الرقمي التسلسلي الفريد للظاهرة في قاعدة البيانات الجغرافية (Geodatabase OID). |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `-` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: OBJECTID='Sample_OBJECTID_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 002. `Source_ID` (المعرف الفريد لمحطة الرصد أو النقطة المناخية المصدرية المدخلة في المعالجة. / Source_ID)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Source_ID` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Source_ID` |
| **2** | **الاسم بالإنجليزية** | Source_ID |
| **3** | **الاسم بالعربية** | المعرف الفريد لمحطة الرصد أو النقطة المناخية المصدرية المدخلة في المعالجة. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `-` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Source_ID='Sample_Source_ID_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 003. `Point_Lat` (دائرة العرض الجغرافية للنقطة بالنظام الإحداثي العالمي WGS 1984 بالدرجات العشرية. / Point_Lat)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Point_Lat` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Point_Lat` |
| **2** | **الاسم بالإنجليزية** | Point_Lat |
| **3** | **الاسم بالعربية** | دائرة العرض الجغرافية للنقطة بالنظام الإحداثي العالمي WGS 1984 بالدرجات العشرية. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `درجة (°)` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Point_Lat='Sample_Point_Lat_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 004. `Point_Lon` (خط الطول الجغرافي للنقطة بالنظام الإحداثي العالمي WGS 1984 بالدرجات العشرية. / Point_Lon)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Point_Lon` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Point_Lon` |
| **2** | **الاسم بالإنجليزية** | Point_Lon |
| **3** | **الاسم بالعربية** | خط الطول الجغرافي للنقطة بالنظام الإحداثي العالمي WGS 1984 بالدرجات العشرية. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `درجة (°)` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Point_Lon='Sample_Point_Lon_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 005. `Data_Start` (سنة أو تاريخ بداية السلسلة الزمنية المناخية المسحوبة من وكالة ناسا POWER. / Data_Start)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Data_Start` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Data_Start` |
| **2** | **الاسم بالإنجليزية** | Data_Start |
| **3** | **الاسم بالعربية** | سنة أو تاريخ بداية السلسلة الزمنية المناخية المسحوبة من وكالة ناسا POWER. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `سنة / تاريخ` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Data_Start='Sample_Data_Start_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 006. `Data_End` (سنة أو تاريخ نهاية السلسلة الزمنية المناخية المسحوبة من وكالة ناسا POWER. / Data_End)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Data_End` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Data_End` |
| **2** | **الاسم بالإنجليزية** | Data_End |
| **3** | **الاسم بالعربية** | سنة أو تاريخ نهاية السلسلة الزمنية المناخية المسحوبة من وكالة ناسا POWER. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `سنة / تاريخ` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Data_End='Sample_Data_End_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 007. `Temporal` (الدقة الزمنية للبيانات المدخلة في المعالجة (Daily يومي / Monthly شهري / Precalc محسوب مسبقاً). / Temporal)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Temporal` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Temporal` |
| **2** | **الاسم بالإنجليزية** | Temporal |
| **3** | **الاسم بالعربية** | الدقة الزمنية للبيانات المدخلة في المعالجة (Daily يومي / Monthly شهري / Precalc محسوب مسبقاً). |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `نص` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Temporal='Sample_Temporal_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 008. `Interp_Meth` (خوارزمية الاستيفاء المكاني المستخدمة في توليد أسطح الراستر (IDW / Kriging / Spline). / Interp_Meth)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Interp_Meth` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Intrp_Meth` |
| **2** | **الاسم بالإنجليزية** | Interp_Meth |
| **3** | **الاسم بالعربية** | خوارزمية الاستيفاء المكاني المستخدمة في توليد أسطح الراستر (IDW / Kriging / Spline). |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `نص` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Intrp_Meth='Sample_Intrp_Meth_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 009. `Cell_Size` (حجم ودقة خلية الراستر الناتجة عن الاستيفاء المكاني بوحدات الإسقاط المعتمد. / Cell_Size)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cell_Size` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cell_Size` |
| **2** | **الاسم بالإنجليزية** | Cell_Size |
| **3** | **الاسم بالعربية** | حجم ودقة خلية الراستر الناتجة عن الاستيفاء المكاني بوحدات الإسقاط المعتمد. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `متر / درجات` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Cell_Size='Sample_Cell_Size_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 010. `Wind_Cell` (المسافة التباعدية بين خلايا شبكة متجهات وأسهم اتجاه وسرعة الرياح. / Wind_Cell)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Wind_Cell` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Wind_Cell` |
| **2** | **الاسم بالإنجليزية** | Wind_Cell |
| **3** | **الاسم بالعربية** | المسافة التباعدية بين خلايا شبكة متجهات وأسهم اتجاه وسرعة الرياح. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `متر / درجات` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Wind_Cell='Sample_Wind_Cell_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 011. `Status` (حالة إتمام المعالجة الحسابية المناخية للنقطة بنجاح (OK أو FAILED). / Status)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Status` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Status` |
| **2** | **الاسم بالإنجليزية** | Status |
| **3** | **الاسم بالعربية** | حالة إتمام المعالجة الحسابية المناخية للنقطة بنجاح (OK أو FAILED). |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `نص` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Status='Sample_Status_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 012. `Error_Msg` (نص رسالة الخطأ أو التشخيص التحذيري في حال تعثر معالجة بيانات النقطة. / Error_Msg)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Error_Msg` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Error_Msg` |
| **2** | **الاسم بالإنجليزية** | Error_Msg |
| **3** | **الاسم بالعربية** | نص رسالة الخطأ أو التشخيص التحذيري في حال تعثر معالجة بيانات النقطة. |
| **4** | **الطبقة والموديول** | `00_Admin` (Admin / بيانات إدارية) |
| **5** | **مجلد الراستر الناتج** | `-` |
| **6** | **نوع المؤشر** | System / Metadata |
| **7** | **الفترة الزمنية** | Static / Runtime |
| **8** | **الوحدة الفيزيائية** | `نص` |
| **9** | **مصدر البيانات** | ArcGIS Geoprocessing Runtime & User Interface |
| **10** | **المتغير الأصلي** | `System Parameter` |
| **11** | **نوع البيانات الداخلة** | Integer, Float, String, Date |
| **12** | **التحويل الأولي** | Direct assignment from user tool parameters and point grid geometry |
| **13** | **المعادلة الرياضية** | $$N/A (Spatial & Execution Metadata)$$ |
| **14** | **خطوات الحساب** | 1. Captured at tool execution start. 2. Propagated to point attribute table. 3. Logged in audit trail. |
| **15** | **معالجة القيم الناقصة** | Required system fields; never null or -999.0. |
| **16** | **مثال رقمي يدوي** | Example value: Error_Msg='Sample_Error_Msg_Value' |
| **17** | **التفسير العلمي** | Provides spatial traceability, projection metadata, date ranges, and processing status for reproducibility. |
| **18** | **التحذيرات ومحددات الاستخدام** | Do not delete or alter admin fields; required for raster interpolation and database indexing. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: execute() lines 4070-4200` |

---

### 013. `T_Annual_Mean` (المتوسط السنوي لدرجة الحرارة / Annual Mean Air Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Air Temperature |
| **3** | **الاسم بالعربية** | المتوسط السنوي لدرجة الحرارة |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$T_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{T}_m$$ |
| **14** | **خطوات الحساب** | 1. Calculate 30-year climatological mean for each month (Jan-Dec). 2. Sum the 12 monthly means. 3. Divide by 12. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** | Monthly means [12.0, 13.5, 17.0, 21.5, 26.0, 29.5, 31.0, 31.0, 28.0, 24.0, 18.5, 14.0] -> Sum = 246.0 -> Mean = 20.5 °C. |
| **17** | **التفسير العلمي** | Baseline thermal state of the atmosphere, fundamental for ecological classification, energy demand, and comfort. |
| **18** | **التحذيرات ومحددات الاستخدام** | Represents screen-level air temperature (2m above ground), not surface skin temperature (LST). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 014. `T_Winter_Mean` (متوسط درجة الحرارة في الشتاء / Winter Mean Air Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Air Temperature |
| **3** | **الاسم بالعربية** | متوسط درجة الحرارة في الشتاء |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$T_{Winter\_Mean} = \frac{\overline{T}_{Dec} + \overline{T}_{Jan} + \overline{T}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological means for December, January, and February. 2. Calculate their arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** | Dec=14.0 °C, Jan=12.0 °C, Feb=13.5 °C -> Mean = (14.0 + 12.0 + 13.5)/3 = 13.17 °C. |
| **17** | **التفسير العلمي** | Indicates cold-season thermal severity, crucial for crop vernalization, heating degree days, and frost risk. |
| **18** | **التحذيرات ومحددات الاستخدام** | Uses climatological winter (DJF); spans calendar year boundaries in time series. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 015. `T_Spring_Mean` (متوسط درجة الحرارة في الربيع / Spring Mean Air Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_SprMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Air Temperature |
| **3** | **الاسم بالعربية** | متوسط درجة الحرارة في الربيع |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$T_{Spring\_Mean} = \frac{\overline{T}_{Mar} + \overline{T}_{Apr} + \overline{T}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological means for March, April, and May. 2. Calculate their arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** | Mar=17.0 °C, Apr=21.5 °C, May=26.0 °C -> Mean = (17.0 + 21.5 + 26.0)/3 = 21.50 °C. |
| **17** | **التفسير العلمي** | Represents spring transitional warming, governing the onset of the agricultural growing season. |
| **18** | **التحذيرات ومحددات الاستخدام** | Subject to rapid synoptic shifts (e.g. desert Khamaseen heat waves). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 016. `T_Summer_Mean` (متوسط درجة الحرارة في الصيف / Summer Mean Air Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_SumMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Air Temperature |
| **3** | **الاسم بالعربية** | متوسط درجة الحرارة في الصيف |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$T_{Summer\_Mean} = \frac{\overline{T}_{Jun} + \overline{T}_{Jul} + \overline{T}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological means for June, July, and August. 2. Calculate their arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** | Jun=29.5 °C, Jul=31.0 °C, Aug=31.0 °C -> Mean = (29.5 + 31.0 + 31.0)/3 = 30.50 °C. |
| **17** | **التفسير العلمي** | Peak summer thermal loading, driving cooling degree days, peak agricultural water demand, and heat stress. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reanalysis may underestimate localized urban heat island (UHI) peaks. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 017. `T_Autumn_Mean` (متوسط درجة الحرارة في الخريف / Autumn Mean Air Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AutMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Air Temperature |
| **3** | **الاسم بالعربية** | متوسط درجة الحرارة في الخريف |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$T_{Autumn\_Mean} = \frac{\overline{T}_{Sep} + \overline{T}_{Oct} + \overline{T}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological means for September, October, and November. 2. Calculate their arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** | Sep=28.0 °C, Oct=24.0 °C, Nov=18.5 °C -> Mean = (28.0 + 24.0 + 18.5)/3 = 23.50 °C. |
| **17** | **التفسير العلمي** | Autumn transitional cooling, marking crop harvesting and the start of winter cropping seasons. |
| **18** | **التحذيرات ومحددات الاستخدام** | Transition speed varies significantly between maritime and continental desert regimes. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 018. `T_Annual_Range` (المدى الحراري السنوي العام / Annual Temperature Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AnnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Temperature Range |
| **3** | **الاسم بالعربية** | المدى الحراري السنوي العام |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$$$ |
| **14** | **خطوات الحساب** |  |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** |  |
| **17** | **التفسير العلمي** |  |
| **18** | **التحذيرات ومحددات الاستخدام** |  |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 019. `T_Max_Summer_Month_Mean` (أقصى متوسط شهري لدرجة الحرارة في الصيف / Maximum Summer Monthly Mean Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Max_Summer_Month_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_MaxSumMo` |
| **2** | **الاسم بالإنجليزية** | Maximum Summer Monthly Mean Temperature |
| **3** | **الاسم بالعربية** | أقصى متوسط شهري لدرجة الحرارة في الصيف |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Max |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$$$ |
| **14** | **خطوات الحساب** |  |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** |  |
| **17** | **التفسير العلمي** |  |
| **18** | **التحذيرات ومحددات الاستخدام** |  |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 020. `T_Min_Winter_Month_Mean` (أدنى متوسط شهري لدرجة الحرارة في الشتاء / Minimum Winter Monthly Mean Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Min_Winter_Month_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_MinWinMo` |
| **2** | **الاسم بالإنجليزية** | Minimum Winter Monthly Mean Temperature |
| **3** | **الاسم بالعربية** | أدنى متوسط شهري لدرجة الحرارة في الشتاء |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Min |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$T_{Winter\_Mean} = \frac{\overline{T}_{Dec} + \overline{T}_{Jan} + \overline{T}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological means for December, January, and February. 2. Calculate their arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** | Dec=14.0 °C, Jan=12.0 °C, Feb=13.5 °C -> Mean = (14.0 + 12.0 + 13.5)/3 = 13.17 °C. |
| **17** | **التفسير العلمي** | Indicates cold-season thermal severity, crucial for crop vernalization, heating degree days, and frost risk. |
| **18** | **التحذيرات ومحددات الاستخدام** | Uses climatological winter (DJF); spans calendar year boundaries in time series. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 021. `T_Annual_Max_Mean` (المتوسط السنوي لدرجات الحرارة العظمى / Annual Mean Maximum Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Annual_Max_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_MaxMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Maximum Temperature |
| **3** | **الاسم بالعربية** | المتوسط السنوي لدرجات الحرارة العظمى |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M_MAX` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$$$ |
| **14** | **خطوات الحساب** |  |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** |  |
| **17** | **التفسير العلمي** |  |
| **18** | **التحذيرات ومحددات الاستخدام** |  |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 022. `T_Annual_Min_Mean` (المتوسط السنوي لدرجات الحرارة الصغرى / Annual Mean Minimum Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Annual_Min_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_MinMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Minimum Temperature |
| **3** | **الاسم بالعربية** | المتوسط السنوي لدرجات الحرارة الصغرى |
| **4** | **الطبقة والموديول** | `01_Temperature` (01_Temperature (درجة الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `01_Temperature` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2M, T2M_MAX, T2M_MIN) / Open-Meteo ERA5 (temperature_2m) |
| **10** | **المتغير الأصلي** | `T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Mean Air Temperature at 2m (°C) |
| **12** | **التحويل الأولي** | None required; natively ingested in degrees Celsius (°C). |
| **13** | **المعادلة الرياضية** | $$$$ |
| **14** | **خطوات الحساب** |  |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v) (excluding -999.0, -99.0, NaN). Requires >=75% valid monthly observations. |
| **16** | **مثال رقمي يدوي** |  |
| **17** | **التفسير العلمي** |  |
| **18** | **التحذيرات ومحددات الاستخدام** |  |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 1850-1920` |

---

### 023. `HI_Annual_Mean` (المتوسط السنوي لمؤشر الحرارة المحسوسة / Annual Mean Heat Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `HI_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `HI_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Heat Index |
| **3** | **الاسم بالعربية** | المتوسط السنوي لمؤشر الحرارة المحسوسة |
| **4** | **الطبقة والموديول** | `11_Heat_Index` (11_Heat_Index (مؤشر الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `11_Heat_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and RH2M |
| **10** | **المتغير الأصلي** | `T2M+RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Relative Humidity (%) |
| **12** | **التحويل الأولي** | Temperature converted to Fahrenheit internally for Rothfusz polynomial, output converted back to Celsius. |
| **13** | **المعادلة الرياضية** | $$HI = -42.379 + 2.049T_f + 10.143RH - 0.224T_f RH - \dots \text{ (Rothfusz 9-parameter)}$$ |
| **14** | **خطوات الحساب** | 1. Convert monthly T to °F. 2. If Tf >= 80°F (26.7°C), compute 9-term Rothfusz equation. If Tf < 80°F, use Steadman linear formula. 3. Convert HI back to °C. 4. Average 12 monthly values. |
| **15** | **معالجة القيم الناقصة** | Requires both valid T2M and RH2M. Computed via heat_index_c and wbgt_shade_c. |
| **16** | **مثال رقمي يدوي** | Monthly HI values calculated -> Annual Mean = 22.4 °C. |
| **17** | **التفسير العلمي** | Mean apparent temperature experienced by the human body considering evaporative cooling inhibition by ambient moisture. |
| **18** | **التحذيرات ومحددات الاستخدام** | Applies strictly to human biometeorological comfort in shade with light breeze. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: heat_index_c (line 797), wetbulb_stull_c (line 840), wbgt_shade_c (line 858); Toolboxes/raster_atlas_generator.py: lines 962-1015` |

---

### 024. `HI_Summer_Mean` (متوسط مؤشر الحرارة المحسوسة في فصل الصيف / Summer Mean Heat Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `HI_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `HI_SumMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Heat Index |
| **3** | **الاسم بالعربية** | متوسط مؤشر الحرارة المحسوسة في فصل الصيف |
| **4** | **الطبقة والموديول** | `11_Heat_Index` (11_Heat_Index (مؤشر الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `11_Heat_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and RH2M |
| **10** | **المتغير الأصلي** | `T2M+RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Relative Humidity (%) |
| **12** | **التحويل الأولي** | Temperature converted to Fahrenheit internally for Rothfusz polynomial, output converted back to Celsius. |
| **13** | **المعادلة الرياضية** | $$HI_{Summer\_Mean} = \frac{HI_{Jun} + HI_{Jul} + HI_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Compute monthly Heat Index for Jun, Jul, Aug. 2. Average the three values. |
| **15** | **معالجة القيم الناقصة** | Requires both valid T2M and RH2M. Computed via heat_index_c and wbgt_shade_c. |
| **16** | **مثال رقمي يدوي** | Jun=32.5, Jul=36.8, Aug=37.2 °C -> Summer Mean = 35.50 °C. |
| **17** | **التفسير العلمي** | Summer thermal discomfort level. NOAA Warning thresholds: Caution (27-32°C), Extreme Caution (32-41°C), Danger (41-54°C). |
| **18** | **التحذيرات ومحددات الاستخدام** | Coastal zones experience massive HI amplification due to high humidity. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: heat_index_c (line 797), wetbulb_stull_c (line 840), wbgt_shade_c (line 858); Toolboxes/raster_atlas_generator.py: lines 962-1015` |

---

### 025. `HI_Winter_Mean` (متوسط مؤشر الحرارة المحسوسة في فصل الشتاء / Winter Mean Heat Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `HI_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `HI_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Heat Index |
| **3** | **الاسم بالعربية** | متوسط مؤشر الحرارة المحسوسة في فصل الشتاء |
| **4** | **الطبقة والموديول** | `11_Heat_Index` (11_Heat_Index (مؤشر الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `11_Heat_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and RH2M |
| **10** | **المتغير الأصلي** | `T2M+RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Relative Humidity (%) |
| **12** | **التحويل الأولي** | Temperature converted to Fahrenheit internally for Rothfusz polynomial, output converted back to Celsius. |
| **13** | **المعادلة الرياضية** | $$HI_{Winter\_Mean} = \frac{HI_{Dec} + HI_{Jan} + HI_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Compute monthly Heat Index for Dec, Jan, Feb. 2. Average the three values. |
| **15** | **معالجة القيم الناقصة** | Requires both valid T2M and RH2M. Computed via heat_index_c and wbgt_shade_c. |
| **16** | **مثال رقمي يدوي** | Dec=14.0, Jan=12.0, Feb=13.5 °C -> Winter Mean = 13.17 °C. |
| **17** | **التفسير العلمي** | Winter apparent temperature; under cool conditions (T < 20°C), HI defaults to dry-bulb temperature. |
| **18** | **التحذيرات ومحددات الاستخدام** | Heat index formula is dormant at low temperatures. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: heat_index_c (line 797), wetbulb_stull_c (line 840), wbgt_shade_c (line 858); Toolboxes/raster_atlas_generator.py: lines 962-1015` |

---

### 026. `HI_Annual_Range` (المدى السنوي لمؤشر الحرارة المحسوسة (الإجهاد الحراري) / Annual Heat Index Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `HI_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `HI_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Heat Index Range |
| **3** | **الاسم بالعربية** | المدى السنوي لمؤشر الحرارة المحسوسة (الإجهاد الحراري) |
| **4** | **الطبقة والموديول** | `11_Heat_Index` (11_Heat_Index (مؤشر الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `11_Heat_Index` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and RH2M |
| **10** | **المتغير الأصلي** | `T2M+RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Relative Humidity (%) |
| **12** | **التحويل الأولي** | Temperature converted to Fahrenheit internally for Rothfusz polynomial, output converted back to Celsius. |
| **13** | **المعادلة الرياضية** | $$HI_{Annual\_Range} = \max(HI_1, \dots, HI_{12}) - \min(HI_1, \dots, HI_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find peak monthly HI. 2. Find lowest monthly HI. 3. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Requires both valid T2M and RH2M. Computed via heat_index_c and wbgt_shade_c. |
| **16** | **مثال رقمي يدوي** | Max (Aug) = 37.2 °C, Min (Jan) = 12.0 °C -> Range = 25.2 °C. |
| **17** | **التفسير العلمي** | Annual biometeorological apparent temperature swing. |
| **18** | **التحذيرات ومحددات الاستخدام** | Exceeds dry-bulb temperature range in humid climates due to non-linear humidity weighting. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: heat_index_c (line 797), wetbulb_stull_c (line 840), wbgt_shade_c (line 858); Toolboxes/raster_atlas_generator.py: lines 962-1015` |

---

### 027. `WBGT_Summer_Mean` (متوسط الإجهاد الحراري صيفاً (WBGT) / Summer Mean Wet-Bulb Globe Temperature (Shade))

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `WBGT_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WBGT_SuMn` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Wet-Bulb Globe Temperature (Shade) |
| **3** | **الاسم بالعربية** | متوسط الإجهاد الحراري صيفاً (WBGT) |
| **4** | **الطبقة والموديول** | `11_Heat_Index` (11_Heat_Index (مؤشر الحرارة)) |
| **5** | **مجلد الراستر الناتج** | `11_Heat_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and RH2M |
| **10** | **المتغير الأصلي** | `T2M+RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Relative Humidity (%) |
| **12** | **التحويل الأولي** | Temperature converted to Fahrenheit internally for Rothfusz polynomial, output converted back to Celsius. |
| **13** | **المعادلة الرياضية** | $$\text{WBGT}_{shade} = 0.7 T_w + 0.3 T_a$$ |
| **14** | **خطوات الحساب** | 1. Calculate natural wet-bulb temperature Tw using Stull (2011) formula from Summer T and RH. 2. Weight Tw by 0.7 and ambient T by 0.3 according to ISO 7243 shade standard. |
| **15** | **معالجة القيم الناقصة** | Requires both valid T2M and RH2M. Computed via heat_index_c and wbgt_shade_c. |
| **16** | **مثال رقمي يدوي** | T=32.0 °C, RH=60% -> Tw (Stull) = 25.4 °C -> WBGT = 0.7(25.4) + 0.3(32.0) = 17.78 + 9.60 = 27.38 °C. |
| **17** | **التفسير العلمي** | Gold standard occupational and athletic thermal heat strain metric (ISO 7243 / ACGIH). Thresholds: 28°C (heavy labor limit), 32°C (extreme risk). |
| **18** | **التحذيرات ومحددات الاستخدام** | Calculated for outdoor shade / indoor conditions without direct solar radiation load (no black globe term). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: heat_index_c (line 797), wetbulb_stull_c (line 840), wbgt_shade_c (line 858); Toolboxes/raster_atlas_generator.py: lines 962-1015` |

---

### 028. `Td_Annual_Mean` (المتوسط السنوي لدرجة حرارة نقطة الندى / Annual Mean Dew Point Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Td_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Td_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Dew Point Temperature |
| **3** | **الاسم بالعربية** | المتوسط السنوي لدرجة حرارة نقطة الندى |
| **4** | **الطبقة والموديول** | `07_Dew_Point` (07_Dew_Point (نقطة الندى)) |
| **5** | **مجلد الراستر الناتج** | `07_Dew_Point` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2MDEW) / Open-Meteo ERA5 (dew_point_2m) |
| **10** | **المتغير الأصلي** | `T2MDEW` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Dew Point Temperature (°C) |
| **12** | **التحويل الأولي** | None; ingested directly in °C. |
| **13** | **المعادلة الرياضية** | $$Td_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{Td}_m$$ |
| **14** | **خطوات الحساب** | 1. Calculate 30-year climatological mean dew point for each month. 2. Compute arithmetic mean across 12 months. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Td <= T2M at all times. |
| **16** | **مثال رقمي يدوي** | Monthly dew points [7.2, 7.5, 9.8, 12.0, 15.1, 18.5, 21.2, 21.8, 19.5, 16.0, 12.2, 8.8] -> Mean = 14.13 °C. |
| **17** | **التفسير العلمي** | Direct measure of absolute atmospheric water vapor mass (specific humidity proxy). Unlike RH, dew point is temperature-independent. |
| **18** | **التحذيرات ومحددات الاستخدام** | Values exceeding 20°C cause severe oppressive sultry discomfort in humans. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2165-2200` |

---

### 029. `Td_Winter_Mean` (متوسط نقطة الندى في الشتاء / Winter Mean Dew Point Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Td_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Td_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Dew Point Temperature |
| **3** | **الاسم بالعربية** | متوسط نقطة الندى في الشتاء |
| **4** | **الطبقة والموديول** | `07_Dew_Point` (07_Dew_Point (نقطة الندى)) |
| **5** | **مجلد الراستر الناتج** | `07_Dew_Point` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2MDEW) / Open-Meteo ERA5 (dew_point_2m) |
| **10** | **المتغير الأصلي** | `T2MDEW` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Dew Point Temperature (°C) |
| **12** | **التحويل الأولي** | None; ingested directly in °C. |
| **13** | **المعادلة الرياضية** | $$Td_{Winter\_Mean} = \frac{\overline{Td}_{Dec} + \overline{Td}_{Jan} + \overline{Td}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological dew points for Dec, Jan, Feb. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Td <= T2M at all times. |
| **16** | **مثال رقمي يدوي** | Dec=8.8, Jan=7.2, Feb=7.5 °C -> Winter Mean = 7.83 °C. |
| **17** | **التفسير العلمي** | Winter absolute moisture content. Low dew points indicate dry air masses. |
| **18** | **التحذيرات ومحددات الاستخدام** | Dew points below 0°C indicate frost risk when air temperature drops. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2165-2200` |

---

### 030. `Td_Spring_Mean` (متوسط نقطة الندى في الربيع / Spring Mean Dew Point Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Td_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Td_SprMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Dew Point Temperature |
| **3** | **الاسم بالعربية** | متوسط نقطة الندى في الربيع |
| **4** | **الطبقة والموديول** | `07_Dew_Point` (07_Dew_Point (نقطة الندى)) |
| **5** | **مجلد الراستر الناتج** | `07_Dew_Point` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2MDEW) / Open-Meteo ERA5 (dew_point_2m) |
| **10** | **المتغير الأصلي** | `T2MDEW` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Dew Point Temperature (°C) |
| **12** | **التحويل الأولي** | None; ingested directly in °C. |
| **13** | **المعادلة الرياضية** | $$Td_{Spring\_Mean} = \frac{\overline{Td}_{Mar} + \overline{Td}_{Apr} + \overline{Td}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological dew points for Mar, Apr, May. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Td <= T2M at all times. |
| **16** | **مثال رقمي يدوي** | Mar=9.8, Apr=12.0, May=15.1 °C -> Spring Mean = 12.30 °C. |
| **17** | **التفسير العلمي** | Spring moisture build-up as regional surface heating increases evaporation. |
| **18** | **التحذيرات ومحددات الاستخدام** | Subject to sudden shifts during dry continental Khamaseen incursions. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2165-2200` |

---

### 031. `Td_Summer_Mean` (متوسط نقطة الندى في الصيف / Summer Mean Dew Point Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Td_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Td_SumMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Dew Point Temperature |
| **3** | **الاسم بالعربية** | متوسط نقطة الندى في الصيف |
| **4** | **الطبقة والموديول** | `07_Dew_Point` (07_Dew_Point (نقطة الندى)) |
| **5** | **مجلد الراستر الناتج** | `07_Dew_Point` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2MDEW) / Open-Meteo ERA5 (dew_point_2m) |
| **10** | **المتغير الأصلي** | `T2MDEW` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Dew Point Temperature (°C) |
| **12** | **التحويل الأولي** | None; ingested directly in °C. |
| **13** | **المعادلة الرياضية** | $$Td_{Summer\_Mean} = \frac{\overline{Td}_{Jun} + \overline{Td}_{Jul} + \overline{Td}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological dew points for Jun, Jul, Aug. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Td <= T2M at all times. |
| **16** | **مثال رقمي يدوي** | Jun=18.5, Jul=21.2, Aug=21.8 °C -> Summer Mean = 20.50 °C. |
| **17** | **التفسير العلمي** | Summer peak absolute atmospheric humidity, driving coastal sultry conditions. |
| **18** | **التحذيرات ومحددات الاستخدام** | Dew points >21°C severely impair human evaporative thermoregulation. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2165-2200` |

---

### 032. `Td_Autumn_Mean` (متوسط نقطة الندى في الخريف / Autumn Mean Dew Point Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Td_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Td_AutMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Dew Point Temperature |
| **3** | **الاسم بالعربية** | متوسط نقطة الندى في الخريف |
| **4** | **الطبقة والموديول** | `07_Dew_Point` (07_Dew_Point (نقطة الندى)) |
| **5** | **مجلد الراستر الناتج** | `07_Dew_Point` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2MDEW) / Open-Meteo ERA5 (dew_point_2m) |
| **10** | **المتغير الأصلي** | `T2MDEW` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Dew Point Temperature (°C) |
| **12** | **التحويل الأولي** | None; ingested directly in °C. |
| **13** | **المعادلة الرياضية** | $$Td_{Autumn\_Mean} = \frac{\overline{Td}_{Sep} + \overline{Td}_{Oct} + \overline{Td}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological dew points for Sep, Oct, Nov. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Td <= T2M at all times. |
| **16** | **مثال رقمي يدوي** | Sep=19.5, Oct=16.0, Nov=12.2 °C -> Autumn Mean = 15.90 °C. |
| **17** | **التفسير العلمي** | Autumn atmospheric moisture decline. |
| **18** | **التحذيرات ومحددات الاستخدام** | High nighttime radiation cooling relative to high dew points triggers dense radiation fog. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2165-2200` |

---

### 033. `Td_Annual_Range` (المدى السنوي لدرجة حرارة نقطة الندى / Annual Dew Point Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Td_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Td_AnnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Dew Point Range |
| **3** | **الاسم بالعربية** | المدى السنوي لدرجة حرارة نقطة الندى |
| **4** | **الطبقة والموديول** | `07_Dew_Point` (07_Dew_Point (نقطة الندى)) |
| **5** | **مجلد الراستر الناتج** | `07_Dew_Point` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (T2MDEW) / Open-Meteo ERA5 (dew_point_2m) |
| **10** | **المتغير الأصلي** | `T2MDEW` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Dew Point Temperature (°C) |
| **12** | **التحويل الأولي** | None; ingested directly in °C. |
| **13** | **المعادلة الرياضية** | $$Td_{Annual\_Range} = \max(\overline{Td}_1, \dots, \overline{Td}_{12}) - \min(\overline{Td}_1, \dots, \overline{Td}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find maximum monthly mean dew point. 2. Find minimum monthly mean dew point. 3. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Td <= T2M at all times. |
| **16** | **مثال رقمي يدوي** | Max month (Aug) = 21.8 °C, Min month (Jan) = 7.2 °C -> Range = 14.6 °C. |
| **17** | **التفسير العلمي** | Annual absolute atmospheric moisture swing. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reflects seasonal changes in water vapor content. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2165-2200` |

---

### 034. `R_Annual_Mean` (المتوسط السنوي لتساقط الأمطار / Annual Mean Precipitation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Precipitation |
| **3** | **الاسم بالعربية** | المتوسط السنوي لتساقط الأمطار |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `ملم (mm)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Annual\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} \sum_{m=1}^{12} P_{y,m} = \sum_{m=1}^{12} \overline{P}_m$$ |
| **14** | **خطوات الحساب** | 1. Calculate monthly total precipitation for every month in the 30-year period (P_rate * days). 2. Sum monthly totals for each year to get annual total P_year. 3. Average the annual totals over the 30 years (equivalent to sum of 12 climatological monthly totals). |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Climatological monthly totals: Jan=45, Feb=35, Mar=25, Apr=15, May=5, Jun=0, Jul=0, Aug=0, Sep=2, Oct=12, Nov=35, Dec=50 mm -> Annual Sum = 224.0 mm/year. |
| **17** | **التفسير العلمي** | Mean annual accumulated precipitation volume over the 30-year climatological normal. Critical benchmark for hydrological water balance, reservoir design, and agricultural rainfed viability. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Named 'R_Annual_Mean' because it is the 30-year MEAN of annual accumulations (~224 mm/year in northern Egypt). In legacy versions of the tool it was labeled 'R_Annual_Total'. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

> [!NOTE]
> **Retired Field (حقل ملغى):** تم استبعاده من الهيكلية المعتمدة لتكراره الرياضي مع `R_Annual_Mean`. محفوظ للأرشفة التاريخية.

### 035. `R_Month_Mean` (المتوسط الشهري لتساقط الأمطار / Mean Monthly Precipitation) [RETIRED]

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Month_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_MonMean` |
| **2** | **الاسم بالإنجليزية** | Mean Monthly Precipitation |
| **3** | **الاسم بالعربية** | المتوسط الشهري لتساقط الأمطار |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `ملم (mm)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Month\_Mean} = \frac{R_{Annual\_Mean}}{12} = \frac{1}{12} \sum_{m=1}^{12} \overline{P}_m$$ |
| **14** | **خطوات الحساب** | 1. Compute R_Annual_Mean (30-year mean annual accumulated precipitation). 2. Divide by 12 months. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | R_Annual_Mean = 224.0 mm -> R_Month_Mean = 224.0 / 12 = 18.67 mm/month. |
| **17** | **التفسير العلمي** | Mean monthly rainfall rate averaged across the 12 months of the year. Provides a standardized monthly baseline rate. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: In strongly seasonal Mediterranean and arid climates where summer has 0 mm, this value does not represent actual rain falling in dry months; it is an annual average divided by 12. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

### 036. `R_Annual_Range` (المدى السنوي للأمطار / Annual Precipitation Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Precipitation Range |
| **3** | **الاسم بالعربية** | المدى السنوي للأمطار |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `ملم (mm)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Annual\_Range} = \max(\overline{P}_1, \dots, \overline{P}_{12}) - \min(\overline{P}_1, \dots, \overline{P}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find wettest climatological month total. 2. Find driest climatological month total. 3. Compute difference. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Wettest month (Dec) = 50.0 mm, Driest month (Jul) = 0.0 mm -> Range = 50.0 - 0.0 = 50.0 mm. |
| **17** | **التفسير العلمي** | Measures monthly rainfall seasonality and intra-annual precipitation contrast. |
| **18** | **التحذيرات ومحددات الاستخدام** | In arid zones where the driest month is 0 mm, the range equals the wettest month total. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

> [!NOTE]
> **Retired Field (حقل ملغى):** تم استبعاده من الهيكلية المعتمدة للاكتفاء بـ `R_Annual_Range`. محفوظ للأرشفة التاريخية.

### 037. `R_Seasonal_Range` (المدى الفصلي للأمطار / Seasonal Precipitation Range) [RETIRED]

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Seasonal_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_SeaRng` |
| **2** | **الاسم بالإنجليزية** | Seasonal Precipitation Range |
| **3** | **الاسم بالعربية** | المدى الفصلي للأمطار |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `ملم (mm)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Season\_Range} = \max(R_{Win}, R_{Spr}, R_{Sum}, R_{Aut}) - \min(R_{Win}, R_{Spr}, R_{Sum}, R_{Aut})$$ |
| **14** | **خطوات الحساب** | 1. Compute seasonal precipitation totals for DJF, MAM, JJA, SON. 2. Compute Max_Season - Min_Season. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Win=130 mm, Spr=45 mm, Sum=0 mm, Aut=49 mm -> Season Range = 130 - 0 = 130.0 mm. |
| **17** | **التفسير العلمي** | Quantifies seasonal regime contrast (e.g. Mediterranean winter concentration vs summer drought). |
| **18** | **التحذيرات ومحددات الاستخدام** | Calculated on 3-month seasonal sums, not individual months. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

### 038. `R_Winter_Mean` (متوسط هطول الأمطار خلال فصل الشتاء / Winter Mean Precipitation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Precipitation |
| **3** | **الاسم بالعربية** | متوسط هطول الأمطار خلال فصل الشتاء |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `مم/فصل (mm/season)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Winter\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} (P_{y,Dec} + P_{y,Jan} + P_{y,Feb})$$ |
| **14** | **خطوات الحساب** | 1. For each complete year y, calculate winter seasonal total: P_Dec + P_Jan + P_Feb. 2. Average the seasonal totals across all complete study years. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Dec=50.0, Jan=45.0, Feb=35.0 mm -> Winter Seasonal Total = 130.0 mm. Multi-year Mean = 130.0 mm/season. |
| **17** | **التفسير العلمي** | Mean precipitation depth falling during meteorological winter (DJF), primary recharge season in Mediterranean climates. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Named 'R_Winter_Mean' because it is the multi-year AVERAGE of winter seasonal accumulations. Unit is mm/season (مم/فصل). In legacy versions it was labeled 'R_Winter_Total'. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

### 039. `R_Spring_Mean` (متوسط هطول الأمطار خلال فصل الربيع / Spring Mean Precipitation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_SprMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Precipitation |
| **3** | **الاسم بالعربية** | متوسط هطول الأمطار خلال فصل الربيع |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `مم/فصل (mm/season)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Spring\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} (P_{y,Mar} + P_{y,Apr} + P_{y,May})$$ |
| **14** | **خطوات الحساب** | 1. For each complete year y, calculate spring seasonal total: P_Mar + P_Apr + P_May. 2. Average the seasonal totals across all complete study years. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Mar=25.0, Apr=15.0, May=5.0 mm -> Spring Seasonal Total = 45.0 mm. Multi-year Mean = 45.0 mm/season. |
| **17** | **التفسير العلمي** | Mean precipitation depth falling during meteorological spring (MAM). |
| **18** | **التحذيرات ومحددات الاستخدام** | Convective spring storm events may exhibit high spatial heterogeneity. Unit is mm/season (مم/فصل). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

### 040. `R_Summer_Mean` (متوسط هطول الأمطار خلال فصل الصيف / Summer Mean Precipitation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_SumMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Precipitation |
| **3** | **الاسم بالعربية** | متوسط هطول الأمطار خلال فصل الصيف |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `مم/فصل (mm/season)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Summer\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} (P_{y,Jun} + P_{y,Jul} + P_{y,Aug})$$ |
| **14** | **خطوات الحساب** | 1. For each complete year y, calculate summer seasonal total: P_Jun + P_Jul + P_Aug. 2. Average the seasonal totals across all complete study years. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Jun=0.0, Jul=0.0, Aug=0.0 mm -> Summer Seasonal Total = 0.0 mm. Multi-year Mean = 0.0 mm/season. |
| **17** | **التفسير العلمي** | Mean precipitation depth falling during meteorological summer (JJA), often near 0 in arid/Mediterranean domains. |
| **18** | **التحذيرات ومحددات الاستخدام** | In arid Mediterranean regions, summer mean is typically 0.0 mm/season. Unit is mm/season (مم/فصل). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

### 041. `R_Autumn_Mean` (متوسط هطول الأمطار خلال فصل الخريف / Autumn Mean Precipitation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AutMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Precipitation |
| **3** | **الاسم بالعربية** | متوسط هطول الأمطار خلال فصل الخريف |
| **4** | **الطبقة والموديول** | `02_Precipitation` (02_Precipitation (الأمطار)) |
| **5** | **مجلد الراستر الناتج** | `02_Precipitation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `مم/فصل (mm/season)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PRECTOTCORR) / Open-Meteo ERA5 (precipitation_sum) |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Daily precipitation flux (mm/day) or monthly sums (mm) |
| **12** | **التحويل الأولي** | NASA POWER rate (mm/day) multiplied by calendar days in month (monthly_precip_total_from_rate). Open-Meteo provides monthly sums. |
| **13** | **المعادلة الرياضية** | $$R_{Autumn\_Mean} = \frac{1}{N_{years}} \sum_{y=1}^{N_{years}} (P_{y,Sep} + P_{y,Oct} + P_{y,Nov})$$ |
| **14** | **خطوات الحساب** | 1. For each complete year y, calculate autumn seasonal total: P_Sep + P_Oct + P_Nov. 2. Average the seasonal totals across all complete study years. |
| **15** | **معالجة القيم الناقصة** | Requires >=75% valid data points per period (safe_sum with min_frac=0.75). Sentinels -999.0 excluded. |
| **16** | **مثال رقمي يدوي** | Sep=2.0, Oct=12.0, Nov=35.0 mm -> Autumn Seasonal Total = 49.0 mm. Multi-year Mean = 49.0 mm/season. |
| **17** | **التفسير العلمي** | Mean precipitation depth falling during meteorological autumn (SON), early season recharge. |
| **18** | **التحذيرات ومحددات الاستخدام** | Autumn convective storms can trigger flash flooding in arid wadis. Unit is mm/season (مم/فصل). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: monthly_precip_total_from_rate (line 749), seasonal_totals_from_monthly_totals (line 721), safe_sum (line 642); Toolboxes/raster_atlas_generator.py: lines 1925-1980` |

---

### 042. `PSL_Annual_Mean` (المتوسط السنوي لضغط مستوى سطح البحر / Annual Mean Sea Level Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PSL_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PSL_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Sea Level Pressure |
| **3** | **الاسم بالعربية** | المتوسط السنوي لضغط مستوى سطح البحر |
| **4** | **الطبقة والموديول** | `03_Sea_Level_Pressure` (03_Sea_Level_Pressure (ضغط مستوى البحر)) |
| **5** | **مجلد الراستر الناتج** | `03_Sea_Level_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PSL) / Open-Meteo ERA5 (pressure_msl) |
| **10** | **المتغير الأصلي** | `SLP` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PSL_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{PSL}_m$$ |
| **14** | **خطوات الحساب** | 1. Convert raw pressure from kPa to hPa. 2. Compute 30-year climatological mean for each month. 3. Average 12 monthly means. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Monthly hPa: [1018, 1017, 1015, 1013, 1011, 1009, 1008, 1008, 1011, 1014, 1016, 1018] -> Annual Mean = 1013.17 hPa. |
| **17** | **التفسير العلمي** | Mean barometric atmospheric pressure at Mean Sea Level (MSL). Reflects synoptic pressure systems and atmospheric circulation cells. |
| **18** | **التحذيرات ومحددات الاستخدام** | PS is strongly dependent on station elevation; PSL removes elevation effects using the hypsometric reduction. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 043. `PSL_Winter_Mean` (متوسط ضغط مستوى سطح البحر في الشتاء / Winter Mean Sea Level Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PSL_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PSL_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Sea Level Pressure |
| **3** | **الاسم بالعربية** | متوسط ضغط مستوى سطح البحر في الشتاء |
| **4** | **الطبقة والموديول** | `03_Sea_Level_Pressure` (03_Sea_Level_Pressure (ضغط مستوى البحر)) |
| **5** | **مجلد الراستر الناتج** | `03_Sea_Level_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PSL) / Open-Meteo ERA5 (pressure_msl) |
| **10** | **المتغير الأصلي** | `SLP` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PSL_{Winter\_Mean} = \frac{\overline{PSL}_{Dec} + \overline{PSL}_{Jan} + \overline{PSL}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Dec, Jan, Feb. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Dec=1018.0, Jan=1018.5, Feb=1017.0 hPa -> Winter Mean = 1017.83 hPa. |
| **17** | **التفسير العلمي** | Winter synoptic pressure regime, indicating Azores/Siberian high-pressure dominance or Mediterranean cyclonic activity. |
| **18** | **التحذيرات ومحددات الاستخدام** | Averaged across meteorological winter months (DJF). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 044. `PSL_Spring_Mean` (متوسط ضغط مستوى سطح البحر في الربيع / Spring Mean Sea Level Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PSL_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PSL_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Sea Level Pressure |
| **3** | **الاسم بالعربية** | متوسط ضغط مستوى سطح البحر في الربيع |
| **4** | **الطبقة والموديول** | `03_Sea_Level_Pressure` (03_Sea_Level_Pressure (ضغط مستوى البحر)) |
| **5** | **مجلد الراستر الناتج** | `03_Sea_Level_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PSL) / Open-Meteo ERA5 (pressure_msl) |
| **10** | **المتغير الأصلي** | `SLP` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PSL_{Spring\_Mean} = \frac{\overline{PSL}_{Mar} + \overline{PSL}_{Apr} + \overline{PSL}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Mar, Apr, May. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Mar=1015.0, Apr=1013.0, May=1011.0 hPa -> Spring Mean = 1013.00 hPa. |
| **17** | **التفسير العلمي** | Spring synoptic pressure regime, characterized by transitioning thermal depressions. |
| **18** | **التحذيرات ومحددات الاستخدام** | Captures rapid pressure drops associated with spring desert depressions. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 045. `PSL_Summer_Mean` (متوسط ضغط مستوى سطح البحر في الصيف / Summer Mean Sea Level Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PSL_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PSL_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Sea Level Pressure |
| **3** | **الاسم بالعربية** | متوسط ضغط مستوى سطح البحر في الصيف |
| **4** | **الطبقة والموديول** | `03_Sea_Level_Pressure` (03_Sea_Level_Pressure (ضغط مستوى البحر)) |
| **5** | **مجلد الراستر الناتج** | `03_Sea_Level_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PSL) / Open-Meteo ERA5 (pressure_msl) |
| **10** | **المتغير الأصلي** | `SLP` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PSL_{Summer\_Mean} = \frac{\overline{PSL}_{Jun} + \overline{PSL}_{Jul} + \overline{PSL}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Jun, Jul, Aug. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Jun=1009.0, Jul=1008.0, Aug=1008.0 hPa -> Summer Mean = 1008.33 hPa. |
| **17** | **التفسير العلمي** | Summer synoptic pressure regime, reflecting the extension of the Indian Monsoon Thermal Low across North Africa and the Middle East. |
| **18** | **التحذيرات ومحددات الاستخدام** | Typically the lowest sea level pressure period in the subtropical desert belt. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 046. `PSL_Autumn_Mean` (متوسط ضغط مستوى سطح البحر في الخريف / Autumn Mean Sea Level Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PSL_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PSL_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Sea Level Pressure |
| **3** | **الاسم بالعربية** | متوسط ضغط مستوى سطح البحر في الخريف |
| **4** | **الطبقة والموديول** | `03_Sea_Level_Pressure` (03_Sea_Level_Pressure (ضغط مستوى البحر)) |
| **5** | **مجلد الراستر الناتج** | `03_Sea_Level_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PSL) / Open-Meteo ERA5 (pressure_msl) |
| **10** | **المتغير الأصلي** | `SLP` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PSL_{Autumn\_Mean} = \frac{\overline{PSL}_{Sep} + \overline{PSL}_{Oct} + \overline{PSL}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Sep, Oct, Nov. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Sep=1011.0, Oct=1014.0, Nov=1016.0 hPa -> Autumn Mean = 1013.67 hPa. |
| **17** | **التفسير العلمي** | Autumn pressure recovery, with the retreat of the summer monsoon trough and building continental ridges. |
| **18** | **التحذيرات ومحددات الاستخدام** | May feature Red Sea Trough extensions producing unstable weather. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 047. `PSL_Annual_Range` (المدى السنوي لضغط مستوى سطح البحر / Annual Sea Level Pressure Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PSL_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PSL_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Sea Level Pressure Range |
| **3** | **الاسم بالعربية** | المدى السنوي لضغط مستوى سطح البحر |
| **4** | **الطبقة والموديول** | `03_Sea_Level_Pressure` (03_Sea_Level_Pressure (ضغط مستوى البحر)) |
| **5** | **مجلد الراستر الناتج** | `03_Sea_Level_Pressure` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PSL) / Open-Meteo ERA5 (pressure_msl) |
| **10** | **المتغير الأصلي** | `SLP` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PSL_{Annual\_Range} = \max(\overline{PSL}_1, \dots, \overline{PSL}_{12}) - \min(\overline{PSL}_1, \dots, \overline{PSL}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find maximum monthly mean pressure. 2. Find minimum monthly mean pressure. 3. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Max month (Jan) = 1018.5 hPa, Min month (Jul) = 1008.0 hPa -> Range = 10.5 hPa. |
| **17** | **التفسير العلمي** | Annual barometric pressure swing, reflecting the seasonal shift between winter anticyclonic ridges and summer thermal troughs. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reflects seasonal climatological amplitude, not daily synoptic variance. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 048. `PS_Annual_Mean` (المتوسط السنوي للضغط الجوي عند السطح الفعلي / Annual Mean Surface Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PS_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PS_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Surface Pressure |
| **3** | **الاسم بالعربية** | المتوسط السنوي للضغط الجوي عند السطح الفعلي |
| **4** | **الطبقة والموديول** | `04_Surface_Pressure` (04_Surface_Pressure (الضغط السطحي)) |
| **5** | **مجلد الراستر الناتج** | `04_Surface_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PS) / Open-Meteo ERA5 (surface_pressure) |
| **10** | **المتغير الأصلي** | `PS` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PS_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{PS}_m$$ |
| **14** | **خطوات الحساب** | 1. Convert raw pressure from kPa to hPa. 2. Compute 30-year climatological mean for each month. 3. Average 12 monthly means. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Monthly hPa: [1018, 1017, 1015, 1013, 1011, 1009, 1008, 1008, 1011, 1014, 1016, 1018] -> Annual Mean = 1013.17 hPa. |
| **17** | **التفسير العلمي** | Mean barometric atmospheric pressure at ground surface elevation. Reflects synoptic pressure systems and atmospheric circulation cells. |
| **18** | **التحذيرات ومحددات الاستخدام** | PS is strongly dependent on station elevation; PSL removes elevation effects using the hypsometric reduction. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 049. `PS_Winter_Mean` (متوسط الضغط السطحي في الشتاء / Winter Mean Surface Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PS_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PS_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Surface Pressure |
| **3** | **الاسم بالعربية** | متوسط الضغط السطحي في الشتاء |
| **4** | **الطبقة والموديول** | `04_Surface_Pressure` (04_Surface_Pressure (الضغط السطحي)) |
| **5** | **مجلد الراستر الناتج** | `04_Surface_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PS) / Open-Meteo ERA5 (surface_pressure) |
| **10** | **المتغير الأصلي** | `PS` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PS_{Winter\_Mean} = \frac{\overline{PS}_{Dec} + \overline{PS}_{Jan} + \overline{PS}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Dec, Jan, Feb. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Dec=1018.0, Jan=1018.5, Feb=1017.0 hPa -> Winter Mean = 1017.83 hPa. |
| **17** | **التفسير العلمي** | Winter synoptic pressure regime, indicating Azores/Siberian high-pressure dominance or Mediterranean cyclonic activity. |
| **18** | **التحذيرات ومحددات الاستخدام** | Averaged across meteorological winter months (DJF). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 050. `PS_Spring_Mean` (متوسط الضغط السطحي في الربيع / Spring Mean Surface Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PS_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PS_SprMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Surface Pressure |
| **3** | **الاسم بالعربية** | متوسط الضغط السطحي في الربيع |
| **4** | **الطبقة والموديول** | `04_Surface_Pressure` (04_Surface_Pressure (الضغط السطحي)) |
| **5** | **مجلد الراستر الناتج** | `04_Surface_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PS) / Open-Meteo ERA5 (surface_pressure) |
| **10** | **المتغير الأصلي** | `PS` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PS_{Spring\_Mean} = \frac{\overline{PS}_{Mar} + \overline{PS}_{Apr} + \overline{PS}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Mar, Apr, May. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Mar=1015.0, Apr=1013.0, May=1011.0 hPa -> Spring Mean = 1013.00 hPa. |
| **17** | **التفسير العلمي** | Spring synoptic pressure regime, characterized by transitioning thermal depressions. |
| **18** | **التحذيرات ومحددات الاستخدام** | Captures rapid pressure drops associated with spring desert depressions. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 051. `PS_Summer_Mean` (متوسط الضغط السطحي في الصيف / Summer Mean Surface Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PS_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PS_SumMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Surface Pressure |
| **3** | **الاسم بالعربية** | متوسط الضغط السطحي في الصيف |
| **4** | **الطبقة والموديول** | `04_Surface_Pressure` (04_Surface_Pressure (الضغط السطحي)) |
| **5** | **مجلد الراستر الناتج** | `04_Surface_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PS) / Open-Meteo ERA5 (surface_pressure) |
| **10** | **المتغير الأصلي** | `PS` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PS_{Summer\_Mean} = \frac{\overline{PS}_{Jun} + \overline{PS}_{Jul} + \overline{PS}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Jun, Jul, Aug. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Jun=1009.0, Jul=1008.0, Aug=1008.0 hPa -> Summer Mean = 1008.33 hPa. |
| **17** | **التفسير العلمي** | Summer synoptic pressure regime, reflecting the extension of the Indian Monsoon Thermal Low across North Africa and the Middle East. |
| **18** | **التحذيرات ومحددات الاستخدام** | Typically the lowest sea level pressure period in the subtropical desert belt. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 052. `PS_Autumn_Mean` (متوسط الضغط السطحي في الخريف / Autumn Mean Surface Pressure)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PS_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PS_AutMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Surface Pressure |
| **3** | **الاسم بالعربية** | متوسط الضغط السطحي في الخريف |
| **4** | **الطبقة والموديول** | `04_Surface_Pressure` (04_Surface_Pressure (الضغط السطحي)) |
| **5** | **مجلد الراستر الناتج** | `04_Surface_Pressure` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PS) / Open-Meteo ERA5 (surface_pressure) |
| **10** | **المتغير الأصلي** | `PS` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PS_{Autumn\_Mean} = \frac{\overline{PS}_{Sep} + \overline{PS}_{Oct} + \overline{PS}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological pressure for Sep, Oct, Nov. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Sep=1011.0, Oct=1014.0, Nov=1016.0 hPa -> Autumn Mean = 1013.67 hPa. |
| **17** | **التفسير العلمي** | Autumn pressure recovery, with the retreat of the summer monsoon trough and building continental ridges. |
| **18** | **التحذيرات ومحددات الاستخدام** | May feature Red Sea Trough extensions producing unstable weather. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 053. `PS_Annual_Range` (المدى السنوي للضغط السطحي الفعلي / Annual Surface Pressure Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PS_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PS_AnnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Surface Pressure Range |
| **3** | **الاسم بالعربية** | المدى السنوي للضغط السطحي الفعلي |
| **4** | **الطبقة والموديول** | `04_Surface_Pressure` (04_Surface_Pressure (الضغط السطحي)) |
| **5** | **مجلد الراستر الناتج** | `04_Surface_Pressure` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `hPa / mbar` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (PS) / Open-Meteo ERA5 (surface_pressure) |
| **10** | **المتغير الأصلي** | `PS` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Barometric Pressure (hPa / mbar) |
| **12** | **التحويل الأولي** | NASA POWER kPa converted to hPa (mbar) by multiplying by 10.0 (pressure_kpa_to_mbar). Open-Meteo provides hPa directly. |
| **13** | **المعادلة الرياضية** | $$PS_{Annual\_Range} = \max(\overline{PS}_1, \dots, \overline{PS}_{12}) - \min(\overline{PS}_1, \dots, \overline{PS}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find maximum monthly mean pressure. 2. Find minimum monthly mean pressure. 3. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Incomplete months (<75%) skipped. Monthly means averaged. |
| **16** | **مثال رقمي يدوي** | Max month (Jan) = 1018.5 hPa, Min month (Jul) = 1008.0 hPa -> Range = 10.5 hPa. |
| **17** | **التفسير العلمي** | Annual barometric pressure swing, reflecting the seasonal shift between winter anticyclonic ridges and summer thermal troughs. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reflects seasonal climatological amplitude, not daily synoptic variance. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: pressure_kpa_to_mbar (line 761), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 1985-2060` |

---

### 054. `W_Spd_Annual_Mean` (المتوسط السنوي لسرعة الرياح / Annual Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Wind Speed |
| **3** | **الاسم بالعربية** | المتوسط السنوي لسرعة الرياح |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{WS}_m$$ |
| **14** | **خطوات الحساب** | 1. Calculate 30-year climatological mean wind speed for each month. 2. Compute arithmetic mean across 12 months. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Monthly speeds [4.2, 4.5, 4.8, 4.6, 4.3, 4.1, 3.9, 3.8, 3.9, 4.0, 4.1, 4.2] -> Mean = 4.20 m/s. |
| **17** | **التفسير العلمي** | Climatological baseline kinetic energy of near-surface airflow, critical for wind energy feasibility, evaporation, and aeolian erosion. |
| **18** | **التحذيرات ومحددات الاستخدام** | Standard height is 10 meters above ground level (WS10M). Roughness effects can reduce speed near ground. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 055. `W_Spd_Winter_Mean` (متوسط سرعة الرياح في الشتاء / Winter Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Wind Speed |
| **3** | **الاسم بالعربية** | متوسط سرعة الرياح في الشتاء |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Winter\_Mean} = \frac{\overline{WS}_{Dec} + \overline{WS}_{Jan} + \overline{WS}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological speeds for Dec, Jan, Feb. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Dec=4.2, Jan=4.2, Feb=4.5 m/s -> Winter Mean = 4.30 m/s. |
| **17** | **التفسير العلمي** | Winter wind regime driven by Mediterranean frontal systems and pressure gradients. |
| **18** | **التحذيرات ومحددات الاستخدام** | Averaged across DJF. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 056. `W_Spd_Spring_Mean` (متوسط سرعة الرياح ربيعاً / Spring Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Wind Speed |
| **3** | **الاسم بالعربية** | متوسط سرعة الرياح ربيعاً |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Spring\_Mean} = \frac{\overline{WS}_{Mar} + \overline{WS}_{Apr} + \overline{WS}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological speeds for Mar, Apr, May. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Mar=4.8, Apr=4.6, May=4.3 m/s -> Spring Mean = 4.57 m/s. |
| **17** | **التفسير العلمي** | Spring wind peak, often the windiest season in North Africa due to intense desert cyclogenesis (Khamaseen storms). |
| **18** | **التحذيرات ومحددات الاستخدام** | Associated with high dust and sandstorm activity. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 057. `W_Spd_Summer_Mean` (متوسط سرعة الرياح صيفاً / Summer Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Wind Speed |
| **3** | **الاسم بالعربية** | متوسط سرعة الرياح صيفاً |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Summer\_Mean} = \frac{\overline{WS}_{Jun} + \overline{WS}_{Jul} + \overline{WS}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological speeds for Jun, Jul, Aug. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Jun=4.1, Jul=3.9, Aug=3.8 m/s -> Summer Mean = 3.93 m/s. |
| **17** | **التفسير العلمي** | Summer wind regime, dominated by steady Etesian northerly winds over the eastern Mediterranean. |
| **18** | **التحذيرات ومحددات الاستخدام** | Provides beneficial natural ventilation in coastal zones. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 058. `W_Spd_Autumn_Mean` (متوسط سرعة الرياح خريفاً / Autumn Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Wind Speed |
| **3** | **الاسم بالعربية** | متوسط سرعة الرياح خريفاً |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Autumn\_Mean} = \frac{\overline{WS}_{Sep} + \overline{WS}_{Oct} + \overline{WS}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological speeds for Sep, Oct, Nov. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Sep=3.9, Oct=4.0, Nov=4.1 m/s -> Autumn Mean = 4.00 m/s. |
| **17** | **التفسير العلمي** | Autumn transitional wind conditions. |
| **18** | **التحذيرات ومحددات الاستخدام** | Relatively calm season before winter cyclonic reactivation. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 059. `W_Spd_Annual_Max_Month` (أقصى متوسط سرعة رياح شهري مسجل خلال العام / Maximum Monthly Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Annual_Max_Month` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_MaxMo` |
| **2** | **الاسم بالإنجليزية** | Maximum Monthly Mean Wind Speed |
| **3** | **الاسم بالعربية** | أقصى متوسط سرعة رياح شهري مسجل خلال العام |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Max |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Max\_Month} = \max(\overline{WS}_1, \dots, \overline{WS}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Compare 12 monthly climatological mean wind speeds. 2. Return maximum. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Monthly values -> Maximum month is March with 4.8 m/s. |
| **17** | **التفسير العلمي** | Identifies the month with the highest sustained climatological wind energy potential. |
| **18** | **التحذيرات ومحددات الاستخدام** | Represents monthly mean, not instantaneous maximum gust speed. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 060. `W_Spd_Annual_Min_Month` (أدنى متوسط سرعة رياح شهري مسجل خلال العام / Minimum Monthly Mean Wind Speed)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Annual_Min_Month` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_MinMo` |
| **2** | **الاسم بالإنجليزية** | Minimum Monthly Mean Wind Speed |
| **3** | **الاسم بالعربية** | أدنى متوسط سرعة رياح شهري مسجل خلال العام |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Min |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Min\_Month} = \min(\overline{WS}_1, \dots, \overline{WS}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Compare 12 monthly climatological mean wind speeds. 2. Return minimum. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Monthly values -> Minimum month is August with 3.8 m/s. |
| **17** | **التفسير العلمي** | Identifies the month of greatest atmospheric stagnation and lowest wind generation. |
| **18** | **التحذيرات ومحددات الاستخدام** | Low wind speeds correlate with poor air pollution dispersion. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 061. `W_Spd_Annual_Range` (المدى السنوي لسرعة الرياح الشهرية / Annual Wind Speed Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Spd_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WSp_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Wind Speed Range |
| **3** | **الاسم بالعربية** | المدى السنوي لسرعة الرياح الشهرية |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `م/ث (m/s)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$WSp_{Annual\_Range} = \max(\overline{WS}_1, \dots, \overline{WS}_{12}) - \min(\overline{WS}_1, \dots, \overline{WS}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Compute WSp_Max_Month - WSp_Min_Month. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Circular statistics applied to angles using 4-quadrant arctan. |
| **16** | **مثال رقمي يدوي** | Max (4.8) - Min (3.8) = 1.0 m/s. |
| **17** | **التفسير العلمي** | Intra-annual wind speed seasonality and variability. |
| **18** | **التحذيرات ومحددات الاستخدام** | Low range indicates steady, year-round wind resource. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 062. `W_Dir_Annual_Mean` (المتوسط السنوي لاتجاه الرياح السائد / Annual Prevailing Wind Direction)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Dir_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WDr_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Prevailing Wind Direction |
| **3** | **الاسم بالعربية** | المتوسط السنوي لاتجاه الرياح السائد |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Circular Mean Vector Direction |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `Degrees (°)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WD10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$\overline{\theta} = \text{atan2}\left(\frac{1}{N}\sum_{i=1}^N \sin(\theta_i), \frac{1}{N}\sum_{i=1}^N \cos(\theta_i)\right) \pmod{360^\circ}$$ |
| **14** | **خطوات الحساب** | 1. Decompose each wind direction angle into unit vector components: u = -sin(theta), v = -cos(theta). 2. Compute mean U and mean V. 3. Reconstruct circular direction using atan2(-mean_u, -mean_v) mapped to [0, 360) degrees. |
| **15** | **معالجة القيم الناقصة** | Standard arithmetic averaging of angles is strictly avoided (e.g. mean of 350° and 10° is 0°/360°, not 180°). Handled via circular_mean_deg. |
| **16** | **مثال رقمي يدوي** | Angles: [350°, 360°, 10°] -> circular mean = 360.0° (Due North). |
| **17** | **التفسير العلمي** | Prevailing annual wind trajectory, governing sand dune migration, industrial plume dispersion, and runway alignments. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Direction indicates the direction FROM which the wind blows (meteorological convention: 0°=North, 90°=East, 180°=South, 270°=West). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 063. `W_Dir_Winter_Mean` (متوسط اتجاه الرياح في الشتاء / Winter Prevailing Wind Direction)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Dir_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WDr_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Prevailing Wind Direction |
| **3** | **الاسم بالعربية** | متوسط اتجاه الرياح في الشتاء |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Circular Mean Vector Direction |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `Degrees (°)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WD10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$\overline{\theta} = \text{atan2}\left(\frac{1}{N}\sum_{i=1}^N \sin(\theta_i), \frac{1}{N}\sum_{i=1}^N \cos(\theta_i)\right) \pmod{360^\circ}$$ |
| **14** | **خطوات الحساب** | 1. Decompose each wind direction angle into unit vector components: u = -sin(theta), v = -cos(theta). 2. Compute mean U and mean V. 3. Reconstruct circular direction using atan2(-mean_u, -mean_v) mapped to [0, 360) degrees. |
| **15** | **معالجة القيم الناقصة** | Standard arithmetic averaging of angles is strictly avoided (e.g. mean of 350° and 10° is 0°/360°, not 180°). Handled via circular_mean_deg. |
| **16** | **مثال رقمي يدوي** | Winter angles [315°, 330°, 340°] -> circular mean = 328.3° (North-Northwest). |
| **17** | **التفسير العلمي** | Prevailing winter wind direction, typically northwest to west in the Levant and Egypt. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Direction indicates the direction FROM which the wind blows (meteorological convention: 0°=North, 90°=East, 180°=South, 270°=West). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 064. `W_Dir_Spring_Mean` (متوسط اتجاه الرياح في الربيع / Spring Prevailing Wind Direction)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Dir_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WDr_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Prevailing Wind Direction |
| **3** | **الاسم بالعربية** | متوسط اتجاه الرياح في الربيع |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Circular Mean Vector Direction |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `Degrees (°)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WD10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$\overline{\theta} = \text{atan2}\left(\frac{1}{N}\sum_{i=1}^N \sin(\theta_i), \frac{1}{N}\sum_{i=1}^N \cos(\theta_i)\right) \pmod{360^\circ}$$ |
| **14** | **خطوات الحساب** | 1. Decompose each wind direction angle into unit vector components: u = -sin(theta), v = -cos(theta). 2. Compute mean U and mean V. 3. Reconstruct circular direction using atan2(-mean_u, -mean_v) mapped to [0, 360) degrees. |
| **15** | **معالجة القيم الناقصة** | Standard arithmetic averaging of angles is strictly avoided (e.g. mean of 350° and 10° is 0°/360°, not 180°). Handled via circular_mean_deg. |
| **16** | **مثال رقمي يدوي** | Spring angles [220°, 240°, 260°] -> circular mean = 240.0° (Southwest). |
| **17** | **التفسير العلمي** | Spring prevailing wind direction, reflecting southerly/southwesterly desert winds. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Direction indicates the direction FROM which the wind blows (meteorological convention: 0°=North, 90°=East, 180°=South, 270°=West). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 065. `W_Dir_Summer_Mean` (متوسط اتجاه الرياح في الصيف / Summer Prevailing Wind Direction)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Dir_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WDr_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Prevailing Wind Direction |
| **3** | **الاسم بالعربية** | متوسط اتجاه الرياح في الصيف |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Circular Mean Vector Direction |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `Degrees (°)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WD10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$\overline{\theta} = \text{atan2}\left(\frac{1}{N}\sum_{i=1}^N \sin(\theta_i), \frac{1}{N}\sum_{i=1}^N \cos(\theta_i)\right) \pmod{360^\circ}$$ |
| **14** | **خطوات الحساب** | 1. Decompose each wind direction angle into unit vector components: u = -sin(theta), v = -cos(theta). 2. Compute mean U and mean V. 3. Reconstruct circular direction using atan2(-mean_u, -mean_v) mapped to [0, 360) degrees. |
| **15** | **معالجة القيم الناقصة** | Standard arithmetic averaging of angles is strictly avoided (e.g. mean of 350° and 10° is 0°/360°, not 180°). Handled via circular_mean_deg. |
| **16** | **مثال رقمي يدوي** | Summer angles [350°, 355°, 5°] -> circular mean = 356.7° (Northerly). |
| **17** | **التفسير العلمي** | Summer prevailing direction, reflecting constant northerly maritime trade/Etesian winds. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Direction indicates the direction FROM which the wind blows (meteorological convention: 0°=North, 90°=East, 180°=South, 270°=West). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 066. `W_Dir_Autumn_Mean` (متوسط اتجاه الرياح في الخريف / Autumn Prevailing Wind Direction)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `W_Dir_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WDr_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Prevailing Wind Direction |
| **3** | **الاسم بالعربية** | متوسط اتجاه الرياح في الخريف |
| **4** | **الطبقة والموديول** | `05_Wind` (05_Wind (الرياح)) |
| **5** | **مجلد الراستر الناتج** | `05_Wind` |
| **6** | **نوع المؤشر** | Circular Mean Vector Direction |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `Degrees (°)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (WS10M, U2M, V2M) / Open-Meteo ERA5 (wind_speed_10m, wind_direction_10m) |
| **10** | **المتغير الأصلي** | `WD10M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Wind Speed (m/s) and Wind Vector Directions (degrees) |
| **12** | **التحويل الأولي** | Vector components U (eastward) and V (northward) synthesized into circular angles when computing direction. |
| **13** | **المعادلة الرياضية** | $$\overline{\theta} = \text{atan2}\left(\frac{1}{N}\sum_{i=1}^N \sin(\theta_i), \frac{1}{N}\sum_{i=1}^N \cos(\theta_i)\right) \pmod{360^\circ}$$ |
| **14** | **خطوات الحساب** | 1. Decompose each wind direction angle into unit vector components: u = -sin(theta), v = -cos(theta). 2. Compute mean U and mean V. 3. Reconstruct circular direction using atan2(-mean_u, -mean_v) mapped to [0, 360) degrees. |
| **15** | **معالجة القيم الناقصة** | Standard arithmetic averaging of angles is strictly avoided (e.g. mean of 350° and 10° is 0°/360°, not 180°). Handled via circular_mean_deg. |
| **16** | **مثال رقمي يدوي** | Autumn angles [0°, 15°, 30°] -> circular mean = 15.0° (North-Northeast). |
| **17** | **التفسير العلمي** | Autumn prevailing wind direction, shifting from north to northeast. |
| **18** | **التحذيرات ومحددات الاستخدام** | CRITICAL: Direction indicates the direction FROM which the wind blows (meteorological convention: 0°=North, 90°=East, 180°=South, 270°=West). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: circular_mean_deg (line 663), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2065-2120` |

---

### 067. `RH_Annual_Mean` (المتوسط السنوي للرطوبة النسبية / Annual Mean Relative Humidity)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `RH_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `RH_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Relative Humidity |
| **3** | **الاسم بالعربية** | المتوسط السنوي للرطوبة النسبية |
| **4** | **الطبقة والموديول** | `06_Relative_Humidity` (06_Relative_Humidity (الرطوبة النسبية)) |
| **5** | **مجلد الراستر الناتج** | `06_Relative_Humidity` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (RH2M) / Open-Meteo ERA5 (relative_humidity_2m) |
| **10** | **المتغير الأصلي** | `RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Screen-Level Relative Humidity (%) |
| **12** | **التحويل الأولي** | None; ingested directly as percentage (0-100%). |
| **13** | **المعادلة الرياضية** | $$RH_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{RH}_m$$ |
| **14** | **خطوات الحساب** | 1. Compute 30-year climatological mean RH for each of the 12 months. 2. Calculate arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v). Values clipped to physical boundary [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Monthly RH: [68, 65, 60, 52, 48, 50, 55, 58, 60, 62, 65, 69]% -> Annual Mean = 60.17%. |
| **17** | **التفسير العلمي** | Mean atmospheric moisture saturation ratio. Strongly modulates human comfort, crop transpiration, and corrosion rates. |
| **18** | **التحذيرات ومحددات الاستخدام** | Relative humidity is strongly inversely correlated with air temperature over diurnal cycles. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2125-2160` |

---

### 068. `RH_Winter_Mean` (متوسط الرطوبة النسبية شتاءً / Winter Mean Relative Humidity)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `RH_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `RH_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Relative Humidity |
| **3** | **الاسم بالعربية** | متوسط الرطوبة النسبية شتاءً |
| **4** | **الطبقة والموديول** | `06_Relative_Humidity` (06_Relative_Humidity (الرطوبة النسبية)) |
| **5** | **مجلد الراستر الناتج** | `06_Relative_Humidity` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (RH2M) / Open-Meteo ERA5 (relative_humidity_2m) |
| **10** | **المتغير الأصلي** | `RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Screen-Level Relative Humidity (%) |
| **12** | **التحويل الأولي** | None; ingested directly as percentage (0-100%). |
| **13** | **المعادلة الرياضية** | $$RH_{Winter\_Mean} = \frac{\overline{RH}_{Dec} + \overline{RH}_{Jan} + \overline{RH}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological RH for Dec, Jan, Feb. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v). Values clipped to physical boundary [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Dec=69%, Jan=68%, Feb=65% -> Winter Mean = 67.33%. |
| **17** | **التفسير العلمي** | Winter moisture saturation, typically the highest RH season due to lower ambient temperatures. |
| **18** | **التحذيرات ومحددات الاستخدام** | High winter humidity increases fog occurrence and damp cold sensation. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2125-2160` |

---

### 069. `RH_Spring_Mean` (متوسط الرطوبة النسبية ربيعاً / Spring Mean Relative Humidity)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `RH_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `RH_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Relative Humidity |
| **3** | **الاسم بالعربية** | متوسط الرطوبة النسبية ربيعاً |
| **4** | **الطبقة والموديول** | `06_Relative_Humidity` (06_Relative_Humidity (الرطوبة النسبية)) |
| **5** | **مجلد الراستر الناتج** | `06_Relative_Humidity` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (RH2M) / Open-Meteo ERA5 (relative_humidity_2m) |
| **10** | **المتغير الأصلي** | `RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Screen-Level Relative Humidity (%) |
| **12** | **التحويل الأولي** | None; ingested directly as percentage (0-100%). |
| **13** | **المعادلة الرياضية** | $$RH_{Spring\_Mean} = \frac{\overline{RH}_{Mar} + \overline{RH}_{Apr} + \overline{RH}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological RH for Mar, Apr, May. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v). Values clipped to physical boundary [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Mar=60%, Apr=52%, May=48% -> Spring Mean = 53.33%. |
| **17** | **التفسير العلمي** | Spring moisture transition, showing sharp drops during continental desert wind advection. |
| **18** | **التحذيرات ومحددات الاستخدام** | Sudden drops below 20% can cause crop desiccation. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2125-2160` |

---

### 070. `RH_Summer_Mean` (متوسط الرطوبة النسبية صيفاً / Summer Mean Relative Humidity)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `RH_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `RH_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Relative Humidity |
| **3** | **الاسم بالعربية** | متوسط الرطوبة النسبية صيفاً |
| **4** | **الطبقة والموديول** | `06_Relative_Humidity` (06_Relative_Humidity (الرطوبة النسبية)) |
| **5** | **مجلد الراستر الناتج** | `06_Relative_Humidity` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (RH2M) / Open-Meteo ERA5 (relative_humidity_2m) |
| **10** | **المتغير الأصلي** | `RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Screen-Level Relative Humidity (%) |
| **12** | **التحويل الأولي** | None; ingested directly as percentage (0-100%). |
| **13** | **المعادلة الرياضية** | $$RH_{Summer\_Mean} = \frac{\overline{RH}_{Jun} + \overline{RH}_{Jul} + \overline{RH}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological RH for Jun, Jul, Aug. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v). Values clipped to physical boundary [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Jun=50%, Jul=55%, Aug=58% -> Summer Mean = 54.33%. |
| **17** | **التفسير العلمي** | Summer moisture regime; coastal areas experience intense sultry humidity while inland deserts remain arid. |
| **18** | **التحذيرات ومحددات الاستخدام** | High summer RH exacerbates heat stress by suppressing sweat evaporation. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2125-2160` |

---

### 071. `RH_Autumn_Mean` (متوسط الرطوبة النسبية خريفاً / Autumn Mean Relative Humidity)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `RH_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `RH_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Relative Humidity |
| **3** | **الاسم بالعربية** | متوسط الرطوبة النسبية خريفاً |
| **4** | **الطبقة والموديول** | `06_Relative_Humidity` (06_Relative_Humidity (الرطوبة النسبية)) |
| **5** | **مجلد الراستر الناتج** | `06_Relative_Humidity` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (RH2M) / Open-Meteo ERA5 (relative_humidity_2m) |
| **10** | **المتغير الأصلي** | `RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Screen-Level Relative Humidity (%) |
| **12** | **التحويل الأولي** | None; ingested directly as percentage (0-100%). |
| **13** | **المعادلة الرياضية** | $$RH_{Autumn\_Mean} = \frac{\overline{RH}_{Sep} + \overline{RH}_{Oct} + \overline{RH}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological RH for Sep, Oct, Nov. 2. Average the 3 values. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v). Values clipped to physical boundary [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Sep=60%, Oct=62%, Nov=65% -> Autumn Mean = 62.33%. |
| **17** | **التفسير العلمي** | Autumn humidity recovery as temperatures cool and Mediterranean evaporation remains active. |
| **18** | **التحذيرات ومحددات الاستخدام** | Contributes to morning dew and condensation formation. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2125-2160` |

---

### 072. `RH_Annual_Range` (المدى السنوي للرطوبة النسبية / Annual Relative Humidity Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `RH_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `RH_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Relative Humidity Range |
| **3** | **الاسم بالعربية** | المدى السنوي للرطوبة النسبية |
| **4** | **الطبقة والموديول** | `06_Relative_Humidity` (06_Relative_Humidity (الرطوبة النسبية)) |
| **5** | **مجلد الراستر الناتج** | `06_Relative_Humidity` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (RH2M) / Open-Meteo ERA5 (relative_humidity_2m) |
| **10** | **المتغير الأصلي** | `RH2M` |
| **11** | **نوع البيانات الداخلة** | Monthly / Daily Screen-Level Relative Humidity (%) |
| **12** | **التحويل الأولي** | None; ingested directly as percentage (0-100%). |
| **13** | **المعادلة الرياضية** | $$RH_{Annual\_Range} = \max(\overline{RH}_1, \dots, \overline{RH}_{12}) - \min(\overline{RH}_1, \dots, \overline{RH}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find maximum monthly RH. 2. Find minimum monthly RH. 3. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Filtered with is_missing(v). Values clipped to physical boundary [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Max month (Dec) = 69%, Min month (May) = 48% -> Range = 21.0%. |
| **17** | **التفسير العلمي** | Intra-annual seasonal swing in atmospheric moisture saturation. |
| **18** | **التحذيرات ومحددات الاستخدام** | Calculated on monthly averages, not daily extremes. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2125-2160` |

---

### 073. `Sol_Annual_Mean` (المتوسط اليومي السنوي للإشعاع الشمسي / Annual Mean Daily Solar Radiation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Daily Solar Radiation |
| **3** | **الاسم بالعربية** | المتوسط اليومي السنوي للإشعاع الشمسي |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/day` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{Sol}_m$$ |
| **14** | **خطوات الحساب** | 1. Convert raw daily solar flux to kWh/m²/day (/ 3.6). 2. Compute 30-year climatological monthly means. 3. Average 12 monthly means. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Monthly means [3.2, 4.3, 5.8, 6.9, 7.6, 8.2, 8.1, 7.5, 6.4, 5.0, 3.8, 3.0] kWh/m²/day -> Mean = 5.82 kWh/m²/day. |
| **17** | **التفسير العلمي** | Mean daily all-sky solar insolation received on a horizontal surface. Primary metric for photovoltaic (PV) and solar thermal energy sizing. |
| **18** | **التحذيرات ومحددات الاستخدام** | Represents global horizontal irradiance (GHI) under all-sky conditions (including cloud attenuation). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 074. `Sol_Annual_Total` (إجمالي الإشعاع الشمسي السنوي التراكمي / Annual Total Solar Radiation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Annual_Total` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_AnTot` |
| **2** | **الاسم بالإنجليزية** | Annual Total Solar Radiation |
| **3** | **الاسم بالعربية** | إجمالي الإشعاع الشمسي السنوي التراكمي |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Accumulated Annual Sum |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/year` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Annual\_Total} = \sum_{m=1}^{12} \left(\overline{Sol}_m \times N_{days, m}\right) \approx Sol_{Annual\_Mean} \times 365.25$$ |
| **14** | **خطوات الحساب** | 1. Multiply each monthly mean daily insolation by the number of days in that month. 2. Sum all 12 monthly accumulated totals. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Sum of (Monthly mean * days) across 12 months = 2,128.5 kWh/m²/year. |
| **17** | **التفسير العلمي** | Total annual solar energy yield per square meter, the benchmark parameter for utility-scale solar farm yield modeling. |
| **18** | **التحذيرات ومحددات الاستخدام** | Expressed in kWh/m²/year. Multiply by 3.6 to convert to MJ/m²/year. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 075. `Sol_Winter_Mean` (متوسط الإشعاع الشمسي شتاءً / Winter Mean Daily Solar Radiation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Daily Solar Radiation |
| **3** | **الاسم بالعربية** | متوسط الإشعاع الشمسي شتاءً |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/day` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Winter\_Mean} = \frac{\overline{Sol}_{Dec} + \overline{Sol}_{Jan} + \overline{Sol}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological daily insolation for Dec, Jan, Feb. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Dec=3.0, Jan=3.2, Feb=4.3 kWh/m²/day -> Winter Mean = 3.50 kWh/m²/day. |
| **17** | **التفسير العلمي** | Winter baseline solar resource, determining off-grid solar battery storage requirements during lowest sun elevation. |
| **18** | **التحذيرات ومحددات الاستخدام** | Lowest insolation season due to low solar zenith angle and winter cloudiness. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 076. `Sol_Spring_Mean` (متوسط الإشعاع الشمسي ربيعاً / Spring Mean Daily Solar Radiation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Daily Solar Radiation |
| **3** | **الاسم بالعربية** | متوسط الإشعاع الشمسي ربيعاً |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/day` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Spring\_Mean} = \frac{\overline{Sol}_{Mar} + \overline{Sol}_{Apr} + \overline{Sol}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological daily insolation for Mar, Apr, May. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Mar=5.8, Apr=6.9, May=7.6 kWh/m²/day -> Spring Mean = 6.77 kWh/m²/day. |
| **17** | **التفسير العلمي** | Spring insolation surge, driving rapid photosynthetic activity and surface warming. |
| **18** | **التحذيرات ومحددات الاستخدام** | Atmospheric aerosol and dust storms (Khamaseen) can cause temporary sharp dips. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 077. `Sol_Summer_Mean` (متوسط الإشعاع الشمسي صيفاً / Summer Mean Daily Solar Radiation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Daily Solar Radiation |
| **3** | **الاسم بالعربية** | متوسط الإشعاع الشمسي صيفاً |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/day` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Summer\_Mean} = \frac{\overline{Sol}_{Jun} + \overline{Sol}_{Jul} + \overline{Sol}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological daily insolation for Jun, Jul, Aug. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Jun=8.2, Jul=8.1, Aug=7.5 kWh/m²/day -> Summer Mean = 7.93 kWh/m²/day. |
| **17** | **التفسير العلمي** | Peak summer solar resource under high sun elevation and minimal cloudiness. |
| **18** | **التحذيرات ومحددات الاستخدام** | High ambient temperatures cause photovoltaic panel efficiency degradation (temperature coefficient loss). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 078. `Sol_Autumn_Mean` (متوسط الإشعاع الشمسي خريفاً / Autumn Mean Daily Solar Radiation)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Daily Solar Radiation |
| **3** | **الاسم بالعربية** | متوسط الإشعاع الشمسي خريفاً |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/day` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Autumn\_Mean} = \frac{\overline{Sol}_{Sep} + \overline{Sol}_{Oct} + \overline{Sol}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological daily insolation for Sep, Oct, Nov. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Sep=6.4, Oct=5.0, Nov=3.8 kWh/m²/day -> Autumn Mean = 5.07 kWh/m²/day. |
| **17** | **التفسير العلمي** | Autumn declining insolation trajectory. |
| **18** | **التحذيرات ومحددات الاستخدام** | Steadily decreasing day length reduces daily energy totals. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 079. `Sol_Annual_Range` (المدى السنوي للإشعاع الشمسي / Annual Solar Radiation Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Sol_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Sol_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Solar Radiation Range |
| **3** | **الاسم بالعربية** | المدى السنوي للإشعاع الشمسي |
| **4** | **الطبقة والموديول** | `08_Solar_Radiation` (08_Solar_Radiation (الإشعاع الشمسي)) |
| **5** | **مجلد الراستر الناتج** | `08_Solar_Radiation` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `kWh/m²/day` |
| **9** | **مصدر البيانات** | NASA POWER CERES/FLASHFlux (ALLSKY_SFC_SW_DWN) / Open-Meteo (shortwave_radiation_sum) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_SW_DWN` |
| **11** | **نوع البيانات الداخلة** | Daily Downward Solar Shortwave Insolation |
| **12** | **التحويل الأولي** | NASA POWER native MJ/m²/day converted to kWh/m²/day by dividing by 3.6 (solar_mj_to_kwh). 1 kWh = 3.6 MJ. |
| **13** | **المعادلة الرياضية** | $$Sol_{Annual\_Range} = \max(\overline{Sol}_1, \dots, \overline{Sol}_{12}) - \min(\overline{Sol}_1, \dots, \overline{Sol}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find highest monthly mean daily insolation. 2. Find lowest monthly mean daily insolation. 3. Compute difference. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Physical validation: Sol >= 0. Aggregated with safe_sum. |
| **16** | **مثال رقمي يدوي** | Max (Jun) = 8.2, Min (Dec) = 3.0 -> Range = 5.20 kWh/m²/day. |
| **17** | **التفسير العلمي** | Seasonal solar insolation amplitude, a function of latitude and seasonal cloud cover variations. |
| **18** | **التحذيرات ومحددات الاستخدام** | Higher latitudes exhibit dramatically higher solar seasonality. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: solar_mj_to_kwh (line 755), climat_monthly_means (line 700); Toolboxes/raster_atlas_generator.py: lines 2205-2245` |

---

### 080. `UV_Annual_Mean` (المتوسط السنوي لمؤشر الأشعة فوق البنفسجية / Annual Mean UV Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UV_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UV_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean UV Index |
| **3** | **الاسم بالعربية** | المتوسط السنوي لمؤشر الأشعة فوق البنفسجية |
| **4** | **الطبقة والموديول** | `09_UV_Index` (09_UV_Index (الأشعة فوق البنفسجية)) |
| **5** | **مجلد الراستر الناتج** | `09_UV_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `Index (0-16+)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (ALLSKY_SFC_UV_INDEX) / Open-Meteo (uv_index_max) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_UV_INDEX` |
| **11** | **نوع البيانات الداخلة** | Daily Noon Maximum Ultraviolet Index |
| **12** | **التحويل الأولي** | None; standard WHO/WMO dimensionless index. |
| **13** | **المعادلة الرياضية** | $$UV_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{UV}_m$$ |
| **14** | **خطوات الحساب** | 1. Compute 30-year climatological noon UV index for each month. 2. Average 12 monthly values. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Values >= 0 validated. Climatologically averaged. |
| **16** | **مثال رقمي يدوي** | Monthly UV [3.1, 4.5, 6.8, 8.9, 10.5, 11.8, 11.7, 10.6, 8.7, 6.2, 4.1, 2.8] -> Mean = 7.48. |
| **17** | **التفسير العلمي** | Mean annual solar erythemal UV radiation intensity, measuring sunburn risk and skin damage potential. |
| **18** | **التحذيرات ومحددات الاستخدام** | WHO UV categories: Low (<2), Moderate (3-5), High (6-7), Very High (8-10), Extreme (11+). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2250-2285` |

---

### 081. `UV_Winter_Mean` (متوسط مؤشر UV شتاءً / Winter Mean UV Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UV_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UV_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean UV Index |
| **3** | **الاسم بالعربية** | متوسط مؤشر UV شتاءً |
| **4** | **الطبقة والموديول** | `09_UV_Index` (09_UV_Index (الأشعة فوق البنفسجية)) |
| **5** | **مجلد الراستر الناتج** | `09_UV_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `Index (0-16+)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (ALLSKY_SFC_UV_INDEX) / Open-Meteo (uv_index_max) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_UV_INDEX` |
| **11** | **نوع البيانات الداخلة** | Daily Noon Maximum Ultraviolet Index |
| **12** | **التحويل الأولي** | None; standard WHO/WMO dimensionless index. |
| **13** | **المعادلة الرياضية** | $$UV_{Winter\_Mean} = \frac{\overline{UV}_{Dec} + \overline{UV}_{Jan} + \overline{UV}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological UV for Dec, Jan, Feb. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Values >= 0 validated. Climatologically averaged. |
| **16** | **مثال رقمي يدوي** | Dec=2.8, Jan=3.1, Feb=4.5 -> Winter Mean = 3.47 (Moderate). |
| **17** | **التفسير العلمي** | Winter UV exposure level; typically the only season in the subtropics where UV drops below the High category. |
| **18** | **التحذيرات ومحددات الاستخدام** | Even in winter, subtropical midday UV can reach Moderate risk. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2250-2285` |

---

### 082. `UV_Spring_Mean` (متوسط مؤشر UV ربيعاً / Spring Mean UV Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UV_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UV_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean UV Index |
| **3** | **الاسم بالعربية** | متوسط مؤشر UV ربيعاً |
| **4** | **الطبقة والموديول** | `09_UV_Index` (09_UV_Index (الأشعة فوق البنفسجية)) |
| **5** | **مجلد الراستر الناتج** | `09_UV_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `Index (0-16+)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (ALLSKY_SFC_UV_INDEX) / Open-Meteo (uv_index_max) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_UV_INDEX` |
| **11** | **نوع البيانات الداخلة** | Daily Noon Maximum Ultraviolet Index |
| **12** | **التحويل الأولي** | None; standard WHO/WMO dimensionless index. |
| **13** | **المعادلة الرياضية** | $$UV_{Spring\_Mean} = \frac{\overline{UV}_{Mar} + \overline{UV}_{Apr} + \overline{UV}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological UV for Mar, Apr, May. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Values >= 0 validated. Climatologically averaged. |
| **16** | **مثال رقمي يدوي** | Mar=6.8, Apr=8.9, May=10.5 -> Spring Mean = 8.73 (Very High). |
| **17** | **التفسير العلمي** | Rapid spring surge into dangerous UV categories as solar zenith angle steepens. |
| **18** | **التحذيرات ومحددات الاستخدام** | Sun protection required; rapid burn times. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2250-2285` |

---

### 083. `UV_Summer_Mean` (متوسط مؤشر UV صيفاً / Summer Mean UV Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UV_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UV_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean UV Index |
| **3** | **الاسم بالعربية** | متوسط مؤشر UV صيفاً |
| **4** | **الطبقة والموديول** | `09_UV_Index` (09_UV_Index (الأشعة فوق البنفسجية)) |
| **5** | **مجلد الراستر الناتج** | `09_UV_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `Index (0-16+)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (ALLSKY_SFC_UV_INDEX) / Open-Meteo (uv_index_max) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_UV_INDEX` |
| **11** | **نوع البيانات الداخلة** | Daily Noon Maximum Ultraviolet Index |
| **12** | **التحويل الأولي** | None; standard WHO/WMO dimensionless index. |
| **13** | **المعادلة الرياضية** | $$UV_{Summer\_Mean} = \frac{\overline{UV}_{Jun} + \overline{UV}_{Jul} + \overline{UV}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological UV for Jun, Jul, Aug. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Values >= 0 validated. Climatologically averaged. |
| **16** | **مثال رقمي يدوي** | Jun=11.8, Jul=11.7, Aug=10.6 -> Summer Mean = 11.37 (Extreme). |
| **17** | **التفسير العلمي** | Sustained extreme UV radiation hazard, with peak daily noon indices routinely exceeding 11-12. |
| **18** | **التحذيرات ومحددات الاستخدام** | Extreme sunburn hazard; skin damage occurs in under 10-15 minutes of unprotected midday exposure. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2250-2285` |

---

### 084. `UV_Autumn_Mean` (متوسط مؤشر UV خريفاً / Autumn Mean UV Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UV_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UV_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean UV Index |
| **3** | **الاسم بالعربية** | متوسط مؤشر UV خريفاً |
| **4** | **الطبقة والموديول** | `09_UV_Index` (09_UV_Index (الأشعة فوق البنفسجية)) |
| **5** | **مجلد الراستر الناتج** | `09_UV_Index` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `Index (0-16+)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (ALLSKY_SFC_UV_INDEX) / Open-Meteo (uv_index_max) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_UV_INDEX` |
| **11** | **نوع البيانات الداخلة** | Daily Noon Maximum Ultraviolet Index |
| **12** | **التحويل الأولي** | None; standard WHO/WMO dimensionless index. |
| **13** | **المعادلة الرياضية** | $$UV_{Autumn\_Mean} = \frac{\overline{UV}_{Sep} + \overline{UV}_{Oct} + \overline{UV}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological UV for Sep, Oct, Nov. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Values >= 0 validated. Climatologically averaged. |
| **16** | **مثال رقمي يدوي** | Sep=8.7, Oct=6.2, Nov=4.1 -> Autumn Mean = 6.33 (High). |
| **17** | **التفسير العلمي** | Autumn UV decline as sun moves toward the southern hemisphere. |
| **18** | **التحذيرات ومحددات الاستخدام** | High category persists into October. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2250-2285` |

---

### 085. `UV_Annual_Range` (المدى السنوي لمؤشر الأشعة فوق البنفسجية / Annual UV Index Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UV_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UV_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual UV Index Range |
| **3** | **الاسم بالعربية** | المدى السنوي لمؤشر الأشعة فوق البنفسجية |
| **4** | **الطبقة والموديول** | `09_UV_Index` (09_UV_Index (الأشعة فوق البنفسجية)) |
| **5** | **مجلد الراستر الناتج** | `09_UV_Index` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `Index (0-16+)` |
| **9** | **مصدر البيانات** | NASA POWER MERRA-2 (ALLSKY_SFC_UV_INDEX) / Open-Meteo (uv_index_max) |
| **10** | **المتغير الأصلي** | `ALLSKY_SFC_UV_INDEX` |
| **11** | **نوع البيانات الداخلة** | Daily Noon Maximum Ultraviolet Index |
| **12** | **التحويل الأولي** | None; standard WHO/WMO dimensionless index. |
| **13** | **المعادلة الرياضية** | $$UV_{Annual\_Range} = \max(\overline{UV}_1, \dots, \overline{UV}_{12}) - \min(\overline{UV}_1, \dots, \overline{UV}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find maximum monthly UV index. 2. Find minimum monthly UV index. 3. Compute difference. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Values >= 0 validated. Climatologically averaged. |
| **16** | **مثال رقمي يدوي** | Max (Jun) = 11.8, Min (Dec) = 2.8 -> Range = 9.0. |
| **17** | **التفسير العلمي** | Annual UV amplitude, driven primarily by seasonal change in solar elevation angle. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reflects seasonal variation in solar noon UV intensity. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2250-2285` |

---

### 086. `Cld_Annual_Mean` (المتوسط السنوي للغطاء السحابي / Annual Mean Cloud Cover)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cld_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cld_AnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Cloud Cover |
| **3** | **الاسم بالعربية** | المتوسط السنوي للغطاء السحابي |
| **4** | **الطبقة والموديول** | `10_Cloud_Cover` (10_Cloud_Cover (الغطاء السحابي)) |
| **5** | **مجلد الراستر الناتج** | `10_Cloud_Cover` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER CERES/MERRA-2 (CLDTOT) / Open-Meteo (cloud_cover) |
| **10** | **المتغير الأصلي** | `CLOUD_AMT` |
| **11** | **نوع البيانات الداخلة** | Daily / Monthly Total Cloud Area Fraction (%) |
| **12** | **التحويل الأولي** | Ingested as percentage (0-100%). If decimal fraction (0-1), multiplied by 100. |
| **13** | **المعادلة الرياضية** | $$Cld_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} \overline{Cld}_m$$ |
| **14** | **خطوات الحساب** | 1. Compute 30-year climatological cloud cover percentage for each month. 2. Average 12 monthly values. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Bounded to [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Monthly cloud % [35, 30, 25, 18, 12, 5, 2, 3, 8, 15, 22, 32]% -> Annual Mean = 17.25%. |
| **17** | **التفسير العلمي** | Mean fraction of the sky obscured by clouds. Inversely proportional to sunshine duration. |
| **18** | **التحذيرات ومحددات الاستخدام** | Values in subtropical deserts are among the lowest globally (<20%), indicating exceptionally clear skies. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2290-2325` |

---

### 087. `Cld_Winter_Mean` (متوسط الغطاء السحابي شتاءً / Winter Mean Cloud Cover)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cld_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cld_WnMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Cloud Cover |
| **3** | **الاسم بالعربية** | متوسط الغطاء السحابي شتاءً |
| **4** | **الطبقة والموديول** | `10_Cloud_Cover` (10_Cloud_Cover (الغطاء السحابي)) |
| **5** | **مجلد الراستر الناتج** | `10_Cloud_Cover` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER CERES/MERRA-2 (CLDTOT) / Open-Meteo (cloud_cover) |
| **10** | **المتغير الأصلي** | `CLOUD_AMT` |
| **11** | **نوع البيانات الداخلة** | Daily / Monthly Total Cloud Area Fraction (%) |
| **12** | **التحويل الأولي** | Ingested as percentage (0-100%). If decimal fraction (0-1), multiplied by 100. |
| **13** | **المعادلة الرياضية** | $$Cld_{Winter\_Mean} = \frac{\overline{Cld}_{Dec} + \overline{Cld}_{Jan} + \overline{Cld}_{Feb}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological cloud cover for Dec, Jan, Feb. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Bounded to [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Dec=32%, Jan=35%, Feb=30% -> Winter Mean = 32.33%. |
| **17** | **التفسير العلمي** | Winter cloudiness maximum, associated with mid-latitude Mediterranean frontal cyclones. |
| **18** | **التحذيرات ومحددات الاستخدام** | Highest cloud cover season in Mediterranean climates. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2290-2325` |

---

### 088. `Cld_Spring_Mean` (متوسط الغطاء السحابي ربيعاً / Spring Mean Cloud Cover)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cld_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cld_SpMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Cloud Cover |
| **3** | **الاسم بالعربية** | متوسط الغطاء السحابي ربيعاً |
| **4** | **الطبقة والموديول** | `10_Cloud_Cover` (10_Cloud_Cover (الغطاء السحابي)) |
| **5** | **مجلد الراستر الناتج** | `10_Cloud_Cover` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER CERES/MERRA-2 (CLDTOT) / Open-Meteo (cloud_cover) |
| **10** | **المتغير الأصلي** | `CLOUD_AMT` |
| **11** | **نوع البيانات الداخلة** | Daily / Monthly Total Cloud Area Fraction (%) |
| **12** | **التحويل الأولي** | Ingested as percentage (0-100%). If decimal fraction (0-1), multiplied by 100. |
| **13** | **المعادلة الرياضية** | $$Cld_{Spring\_Mean} = \frac{\overline{Cld}_{Mar} + \overline{Cld}_{Apr} + \overline{Cld}_{May}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological cloud cover for Mar, Apr, May. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Bounded to [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Mar=25%, Apr=18%, May=12% -> Spring Mean = 18.33%. |
| **17** | **التفسير العلمي** | Spring cloud decline, featuring scattered cirrus and dust hazes. |
| **18** | **التحذيرات ومحددات الاستخدام** | Dust plumes can sometimes be classified as aerosol rather than cloud. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2290-2325` |

---

### 089. `Cld_Summer_Mean` (متوسط الغطاء السحابي صيفاً / Summer Mean Cloud Cover)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cld_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cld_SuMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Cloud Cover |
| **3** | **الاسم بالعربية** | متوسط الغطاء السحابي صيفاً |
| **4** | **الطبقة والموديول** | `10_Cloud_Cover` (10_Cloud_Cover (الغطاء السحابي)) |
| **5** | **مجلد الراستر الناتج** | `10_Cloud_Cover` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER CERES/MERRA-2 (CLDTOT) / Open-Meteo (cloud_cover) |
| **10** | **المتغير الأصلي** | `CLOUD_AMT` |
| **11** | **نوع البيانات الداخلة** | Daily / Monthly Total Cloud Area Fraction (%) |
| **12** | **التحويل الأولي** | Ingested as percentage (0-100%). If decimal fraction (0-1), multiplied by 100. |
| **13** | **المعادلة الرياضية** | $$Cld_{Summer\_Mean} = \frac{\overline{Cld}_{Jun} + \overline{Cld}_{Jul} + \overline{Cld}_{Aug}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological cloud cover for Jun, Jul, Aug. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Bounded to [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Jun=5%, Jul=2%, Aug=3% -> Summer Mean = 3.33%. |
| **17** | **التفسير العلمي** | Summer extreme sky clarity due to intense large-scale Hadley cell atmospheric subsidence. |
| **18** | **التحذيرات ومحددات الاستخدام** | Nearly cloudless conditions prevail across the Saharan-Arabian desert belt. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2290-2325` |

---

### 090. `Cld_Autumn_Mean` (متوسط الغطاء السحابي خريفاً / Autumn Mean Cloud Cover)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cld_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cld_AuMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Cloud Cover |
| **3** | **الاسم بالعربية** | متوسط الغطاء السحابي خريفاً |
| **4** | **الطبقة والموديول** | `10_Cloud_Cover` (10_Cloud_Cover (الغطاء السحابي)) |
| **5** | **مجلد الراستر الناتج** | `10_Cloud_Cover` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER CERES/MERRA-2 (CLDTOT) / Open-Meteo (cloud_cover) |
| **10** | **المتغير الأصلي** | `CLOUD_AMT` |
| **11** | **نوع البيانات الداخلة** | Daily / Monthly Total Cloud Area Fraction (%) |
| **12** | **التحويل الأولي** | Ingested as percentage (0-100%). If decimal fraction (0-1), multiplied by 100. |
| **13** | **المعادلة الرياضية** | $$Cld_{Autumn\_Mean} = \frac{\overline{Cld}_{Sep} + \overline{Cld}_{Oct} + \overline{Cld}_{Nov}}{3}$$ |
| **14** | **خطوات الحساب** | 1. Extract climatological cloud cover for Sep, Oct, Nov. 2. Compute average. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Bounded to [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Sep=8%, Oct=15%, Nov=22% -> Autumn Mean = 15.00%. |
| **17** | **التفسير العلمي** | Autumn gradual increase in cloudiness with the return of Mediterranean trough systems. |
| **18** | **التحذيرات ومحددات الاستخدام** | Early autumn remains mostly clear. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2290-2325` |

---

### 091. `Cld_Annual_Range` (المدى السنوي للغطاء السحابي / Annual Cloud Cover Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Cld_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Cld_AnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Cloud Cover Range |
| **3** | **الاسم بالعربية** | المدى السنوي للغطاء السحابي |
| **4** | **الطبقة والموديول** | `10_Cloud_Cover` (10_Cloud_Cover (الغطاء السحابي)) |
| **5** | **مجلد الراستر الناتج** | `10_Cloud_Cover` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | NASA POWER CERES/MERRA-2 (CLDTOT) / Open-Meteo (cloud_cover) |
| **10** | **المتغير الأصلي** | `CLOUD_AMT` |
| **11** | **نوع البيانات الداخلة** | Daily / Monthly Total Cloud Area Fraction (%) |
| **12** | **التحويل الأولي** | Ingested as percentage (0-100%). If decimal fraction (0-1), multiplied by 100. |
| **13** | **المعادلة الرياضية** | $$Cld_{Annual\_Range} = \max(\overline{Cld}_1, \dots, \overline{Cld}_{12}) - \min(\overline{Cld}_1, \dots, \overline{Cld}_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find maximum monthly cloud cover. 2. Find minimum monthly cloud cover. 3. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Sentinels -999.0 removed. Bounded to [0, 100]%. |
| **16** | **مثال رقمي يدوي** | Max (Jan) = 35%, Min (Jul) = 2% -> Range = 33.0%. |
| **17** | **التفسير العلمي** | Annual cloud cover seasonality, showing the contrast between winter frontal activity and summer subsidence. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reflects monthly mean variations. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: climat_monthly_means (line 700), seasonal_means_from_monthly (line 709); Toolboxes/raster_atlas_generator.py: lines 2290-2325` |

---

### 092. `WC_Winter_Mean` (متوسط الإحساس بالبرودة شتاءً (تبريد الرياح) / Winter Mean Wind Chill Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `WC_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WC_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Wind Chill Temperature |
| **3** | **الاسم بالعربية** | متوسط الإحساس بالبرودة شتاءً (تبريد الرياح) |
| **4** | **الطبقة والموديول** | `12_Wind_Chill` (12_Wind_Chill (مبرد الرياح)) |
| **5** | **مجلد الراستر الناتج** | `12_Wind_Chill` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and Wind Speed (WS10M/WS2M) |
| **10** | **المتغير الأصلي** | `T2M+WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Wind Speed (m/s converted to km/h) |
| **12** | **التحويل الأولي** | Wind speed in m/s converted to km/h by multiplying by 3.6 (V_kmh = WS * 3.6). |
| **13** | **المعادلة الرياضية** | $$WC = 13.12 + 0.6215 T - 11.37 V^{0.16} + 0.3965 T V^{0.16}$$ |
| **14** | **خطوات الحساب** | 1. Convert wind speed to km/h. 2. Apply Joint US NWS / Environment Canada (2001) formula if T <= 10°C and V > 4.8 km/h. 3. Average across Dec, Jan, Feb. |
| **15** | **معالجة القيم الناقصة** | Wind chill formula active when T <= 10°C and V > 4.8 km/h; otherwise defaults to ambient air temperature T. |
| **16** | **مثال رقمي يدوي** | T=8.0 °C, WS=5.0 m/s (18 km/h) -> V^0.16 = 1.587 -> WC = 13.12 + 0.6215(8) - 11.37(1.587) + 0.3965(8)(1.587) = 5.08 °C. |
| **17** | **التفسير العلمي** | Apparent cold temperature experienced on exposed skin due to convective heat dissipation accelerated by wind. |
| **18** | **التحذيرات ومحددات الاستخدام** | Does not cause inanimate objects (e.g. car radiators) to cool below actual air temperature. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: windchill_c (line 872); Toolboxes/raster_atlas_generator.py: lines 2360-2390` |

---

### 093. `WC_Annual_Mean` (المتوسط السنوي للإحساس بالبرودة (تبريد الرياح) / Annual Mean Wind Chill Temperature)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `WC_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WC_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Wind Chill Temperature |
| **3** | **الاسم بالعربية** | المتوسط السنوي للإحساس بالبرودة (تبريد الرياح) |
| **4** | **الطبقة والموديول** | `12_Wind_Chill` (12_Wind_Chill (مبرد الرياح)) |
| **5** | **مجلد الراستر الناتج** | `12_Wind_Chill` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Derived biometeorological synthesis from T2M and Wind Speed (WS10M/WS2M) |
| **10** | **المتغير الأصلي** | `T2M+WS10M` |
| **11** | **نوع البيانات الداخلة** | Monthly Climatological Air Temperature (°C) and Wind Speed (m/s converted to km/h) |
| **12** | **التحويل الأولي** | Wind speed in m/s converted to km/h by multiplying by 3.6 (V_kmh = WS * 3.6). |
| **13** | **المعادلة الرياضية** | $$WC_{Annual\_Mean} = \frac{1}{12} \sum_{m=1}^{12} WC_m$$ |
| **14** | **خطوات الحساب** | 1. Calculate monthly wind chill for all 12 months. 2. Compute arithmetic mean. |
| **15** | **معالجة القيم الناقصة** | Wind chill formula active when T <= 10°C and V > 4.8 km/h; otherwise defaults to ambient air temperature T. |
| **16** | **مثال رقمي يدوي** | Average of 12 monthly wind chill values = 18.9 °C. |
| **17** | **التفسير العلمي** | Annual average apparent convective thermal sensation. |
| **18** | **التحذيرات ومحددات الاستخدام** | In warm months (T > 10°C), wind chill equals ambient temperature T. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: windchill_c (line 872); Toolboxes/raster_atlas_generator.py: lines 2360-2390` |

---

### 094. `DM_Aridity_Annual` (مؤشر دي مارتون للجفاف والقحولة / De Martonne Aridity Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `DM_Aridity_Annual` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `DM_AridAnn` |
| **2** | **الاسم بالإنجليزية** | De Martonne Aridity Index |
| **3** | **الاسم بالعربية** | مؤشر دي مارتون للجفاف والقحولة |
| **4** | **الطبقة والموديول** | `13_De_Martonne_Aridity` (13_De_Martonne_Aridity (دليل دي مارتون)) |
| **5** | **مجلد الراستر الناتج** | `13_De_Martonne_Aridity` |
| **6** | **نوع المؤشر** | Index |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `Index (mm/°C)` |
| **9** | **مصدر البيانات** | Derived agroclimatic index from R_Annual_Mean and T_Annual_Mean |
| **10** | **المتغير الأصلي** | `PRECTOTCORR+T2M` |
| **11** | **نوع البيانات الداخلة** | Annual Accumulated Precipitation (mm) and Annual Mean Air Temperature (°C) |
| **12** | **التحويل الأولي** | Computed from R_Annual_Mean (mm/year) and T_Annual_Mean (°C). |
| **13** | **المعادلة الرياضية** | $$I_{DM} = \frac{P_{Annual}}{T_{Annual} + 10}$$ |
| **14** | **خطوات الحساب** | 1. Retrieve R_Annual_Mean (P in mm). 2. Retrieve T_Annual_Mean (T in °C). 3. Add 10 to T. 4. Divide P by (T + 10). |
| **15** | **معالجة القيم الناقصة** | Requires valid precipitation and temperature. If T <= -10°C, guarded against division by zero. |
| **16** | **مثال رقمي يدوي** | P = 224.0 mm, T = 20.5 °C -> I_DM = 224.0 / (20.5 + 10) = 224.0 / 30.5 = 7.34. |
| **17** | **التفسير العلمي** | De Martonne (1926) aridity index classifying climatic drought regimes. Classification: Hyper-arid (<5), Arid (5-10), Semi-arid (10-20), Mediterranean/Sub-humid (20-30), Humid (30-55), Extremely Humid (>55). |
| **18** | **التحذيرات ومحددات الاستخدام** | Empirical formulation; in extremely hot deserts where T > 30°C, the +10 denominator provides a dampening offset. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 2395-2420` |

---

### 095. `ET_Annual_Mean` (المتوسط السنوي للبخر والنتح / Annual Mean Evapotranspiration)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Annual_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_AnnMean` |
| **2** | **الاسم بالإنجليزية** | Annual Mean Evapotranspiration |
| **3** | **الاسم بالعربية** | المتوسط السنوي للبخر والنتح (مجموع السنة النمطية) |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean (of per-year annual sums) |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm/year` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | متوسط المجاميع السنوية (يقابل `R_Annual_Mean` للمطر) |
| **14** | **خطوات الحساب** | 1. Sum 12 climatological monthly reference evapotranspiration totals. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Sum of 12 monthly ET totals = 1,930.0 mm/year. |
| **17** | **التفسير العلمي** | Mean annual accumulated atmospheric evaporative demand (one typical year). |
| **18** | **التحذيرات ومحددات الاستخدام** | أعيدت تسميته أكتوبر 2026 من `ET_Annual_Total` (نفس القيم) لمطابقة منطق المطر. مطابق لـ `PET_Hargreaves_Annual`. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

> **ملغى:** `ET_Annual_Total` أعيدت تسميته إلى `ET_Annual_Mean` (نفس قيم mm/year). المعنى الشهري القديم يعيش فقط في `ET_Month_Mean` (mm/month).

---

> [!NOTE]
> **Retired Field (حقل ملغى):** تم استبعاده من الهيكلية المعتمدة لتكراره الرياضي مع `ET_Annual_Mean`. محفوظ للأرشفة التاريخية.

### 096. `ET_Month_Mean` (المتوسط الشهري للبخر والنتح / Mean Monthly Evapotranspiration) [RETIRED]

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Month_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_MonMean` |
| **2** | **الاسم بالإنجليزية** | Mean Monthly Evapotranspiration |
| **3** | **الاسم بالعربية** | المتوسط الشهري للبخر والنتح |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm/month` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Month\_Mean} = \frac{ET_{Annual\_Mean}}{12}$$ |
| **14** | **خطوات الحساب** | 1. Divide ET_Annual_Mean by 12 months. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | 1,930.0 mm / 12 = 160.83 mm/month. |
| **17** | **التفسير العلمي** | Mean monthly rate of reference crop evapotranspiration. |
| **18** | **التحذيرات ومحددات الاستخدام** | Monthly rate averaged over the whole year. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 097. `ET_Annual_Range` (المدى السنوي للبخر والنتح / Annual Reference Evapotranspiration Range)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Annual_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_AnnRng` |
| **2** | **الاسم بالإنجليزية** | Annual Reference Evapotranspiration Range |
| **3** | **الاسم بالعربية** | المدى السنوي للبخر والنتح |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Annual\_Range} = \max(ET_1, \dots, ET_{12}) - \min(ET_1, \dots, ET_{12})$$ |
| **14** | **خطوات الحساب** | 1. Find peak monthly ET total. 2. Find minimum monthly ET total. 3. Compute difference. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Max month (Jul) = 260 mm, Min month (Dec) = 58 mm -> Range = 202.0 mm. |
| **17** | **التفسير العلمي** | Measures the seasonal amplitude in crop water demand. |
| **18** | **التحذيرات ومحددات الاستخدام** | Reflects the swing between winter low-demand and summer peak-demand months. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

> [!NOTE]
> **Retired Field (حقل ملغى):** تم استبعاده من الهيكلية المعتمدة للاكتفاء بـ `ET_Annual_Range`. محفوظ للأرشفة التاريخية.

### 098. `ET_Seasonal_Range` (المدى الفصلي للبخر والنتح / Seasonal Reference Evapotranspiration Range) [RETIRED]

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Seasonal_Range` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_SeaRng` |
| **2** | **الاسم بالإنجليزية** | Seasonal Reference Evapotranspiration Range |
| **3** | **الاسم بالعربية** | المدى الفصلي للبخر والنتح |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Range |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Season\_Range} = \max(ET_{Win}, ET_{Spr}, ET_{Sum}, ET_{Aut}) - \min(ET_{Win}, ET_{Spr}, ET_{Sum}, ET_{Aut})$$ |
| **14** | **خطوات الحساب** | 1. Compute seasonal totals for DJF, MAM, JJA, SON. 2. Compute Max - Min. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Summer (755 mm) - Winter (205 mm) = 550.0 mm. |
| **17** | **التفسير العلمي** | Seasonal swing in evaporative demand across 3-month blocks. |
| **18** | **التحذيرات ومحددات الاستخدام** | Calculated on 3-month seasonal sums. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 099. `ET_Winter_Mean` (متوسط بخر ونتح الشتاء / Winter Mean Evapotranspiration)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Winter_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_WinMean` |
| **2** | **الاسم بالإنجليزية** | Winter Mean Evapotranspiration |
| **3** | **الاسم بالعربية** | متوسط بخر ونتح الشتاء |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Winter\_Total} = ET_{Dec} + ET_{Jan} + ET_{Feb}$$ |
| **14** | **خطوات الحساب** | 1. Sum monthly ET totals for December, January, February. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Dec=58, Jan=62, Feb=85 mm -> Winter Total = 205.0 mm. |
| **17** | **التفسير العلمي** | Total atmospheric evaporative demand during meteorological winter (DJF), the period of lowest crop water consumption. |
| **18** | **التحذيرات ومحددات الاستخدام** | Winter crops require minimum irrigation water. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 100. `ET_Spring_Mean` (متوسط بخر ونتح الربيع / Spring Mean Evapotranspiration)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Spring_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_SprMean` |
| **2** | **الاسم بالإنجليزية** | Spring Mean Evapotranspiration |
| **3** | **الاسم بالعربية** | متوسط بخر ونتح الربيع |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Spring |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Spring\_Total} = ET_{Mar} + ET_{Apr} + ET_{May}$$ |
| **14** | **خطوات الحساب** | 1. Sum monthly ET totals for March, April, May. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Mar=135, Apr=180, May=225 mm -> Spring Total = 540.0 mm. |
| **17** | **التفسير العلمي** | Spring evaporative demand build-up as ambient temperatures and solar radiation escalate. |
| **18** | **التحذيرات ومحددات الاستخدام** | Sharp increase in crop irrigation requirements. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 101. `ET_Summer_Mean` (متوسط بخر ونتح الصيف / Summer Mean Evapotranspiration)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Summer_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_SumMean` |
| **2** | **الاسم بالإنجليزية** | Summer Mean Evapotranspiration |
| **3** | **الاسم بالعربية** | متوسط بخر ونتح الصيف |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Summer\_Total} = ET_{Jun} + ET_{Jul} + ET_{Aug}$$ |
| **14** | **خطوات الحساب** | 1. Sum monthly ET totals for June, July, August. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Jun=255, Jul=260, Aug=240 mm -> Summer Total = 755.0 mm. |
| **17** | **التفسير العلمي** | Peak summer crop water demand, representing over 40% of the entire annual irrigation duty. |
| **18** | **التحذيرات ومحددات الاستخدام** | Canal irrigation systems and pumps operate at maximum design capacity. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 102. `ET_Autumn_Mean` (متوسط بخر ونتح الخريف / Autumn Mean Evapotranspiration)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `ET_Autumn_Mean` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `ET_AutMean` |
| **2** | **الاسم بالإنجليزية** | Autumn Mean Evapotranspiration |
| **3** | **الاسم بالعربية** | متوسط بخر ونتح الخريف |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Autumn |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$ET_{Autumn\_Total} = ET_{Sep} + ET_{Oct} + ET_{Nov}$$ |
| **14** | **خطوات الحساب** | 1. Sum monthly ET totals for September, October, November. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Sep=195, Oct=145, Nov=90 mm -> Autumn Total = 430.0 mm. |
| **17** | **التفسير العلمي** | Autumn evaporative demand decline. |
| **18** | **التحذيرات ومحددات الاستخدام** | Irrigation intervals can be steadily extended. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 103. `PET_Hargreaves_Annual` (التبخر-نتح الكامن السنوي بهارجريفز / Annual Hargreaves Potential Evapotranspiration)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `PET_Hargreaves_Annual` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `PET_HarAnn` |
| **2** | **الاسم بالإنجليزية** | Annual Hargreaves Potential Evapotranspiration |
| **3** | **الاسم بالعربية** | التبخر-نتح الكامن السنوي بهارجريفز |
| **4** | **الطبقة والموديول** | `14_Evapotranspiration` (14_Evapotranspiration (البخر والنتح)) |
| **5** | **مجلد الراستر الناتج** | `14_Evapotranspiration` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm/year` |
| **9** | **مصدر البيانات** | Hargreaves-Samani (1985) Reference Crop Evapotranspiration (PET) model |
| **10** | **المتغير الأصلي** | `T2M+T2M_MAX+T2M_MIN` |
| **11** | **نوع البيانات الداخلة** | Extraterrestrial Solar Ra, Monthly Mean T2M, T_Max, T_Min |
| **12** | **التحويل الأولي** | Daily extraterrestrial radiation Ra computed analytically from latitude and day of year (extraterrestrial_radiation_ra), converted to equivalent water depth (mm/day) by multiplying by 0.408. |
| **13** | **المعادلة الرياضية** | $$PET_{m} = 0.0023 \times 0.408 R_a \times (T_m + 17.8) \times \sqrt{T_{max, m} - T_{min, m}} \times N_{days, m}; \quad PET_{Annual} = \sum_{m=1}^{12} PET_m$$ |
| **14** | **خطوات الحساب** | 1. For each month m (1-12), compute daily Ra at point latitude. 2. Evaluate Hargreaves-Samani daily PET. 3. Multiply by number of days in month to get monthly PET_m. 4. Sum all 12 monthly totals. |
| **15** | **معالجة القيم الناقصة** | Requires T, Tmax, Tmin, and valid latitude. Sentinels excluded. Bounded to PET >= 0. |
| **16** | **مثال رقمي يدوي** | Monthly PET values [62, 85, 135, 180, 225, 255, 260, 240, 195, 145, 90, 58] mm -> Annual PET = 1,930.0 mm/year. |
| **17** | **التفسير العلمي** | Theoretical maximum atmospheric evaporative demand for an extensive, well-watered reference grass crop. Primary baseline for agricultural crop irrigation water duty sizing. |
| **18** | **التحذيرات ومحددات الاستخدام** | Empirical temperature-difference proxy for solar radiation; can overestimate in windy arid conditions and underestimate in cloudy humid tropics. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: extraterrestrial_radiation_ra (line 1350), compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 939-960, 2425-2480` |

---

### 104. `UNEP_Aridity_Annual` (مؤشر القحولة العالمي (برنامج الأمم المتحدة للبيئة) / UNEP Aridity Index)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `UNEP_Aridity_Annual` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `UNEP_Arid` |
| **2** | **الاسم بالإنجليزية** | UNEP Aridity Index |
| **3** | **الاسم بالعربية** | مؤشر القحولة العالمي (برنامج الأمم المتحدة للبيئة) |
| **4** | **الطبقة والموديول** | `15_UNEP_Aridity` (15_UNEP_Aridity (مؤشر UNEP)) |
| **5** | **مجلد الراستر الناتج** | `15_UNEP_Aridity` |
| **6** | **نوع المؤشر** | Index |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `Ratio (dimensionless)` |
| **9** | **مصدر البيانات** | Derived agroclimatic index from R_Annual_Mean and PET_Hargreaves_Annual |
| **10** | **المتغير الأصلي** | `PRECTOTCORR+PET` |
| **11** | **نوع البيانات الداخلة** | Annual Accumulated Precipitation (mm) and Annual Hargreaves PET (mm) |
| **12** | **التحويل الأولي** | Computed from R_Annual_Mean (mm) and PET_Hargreaves_Annual (mm). |
| **13** | **المعادلة الرياضية** | $$AI_{UNEP} = \frac{P_{Annual}}{PET_{Annual}}$$ |
| **14** | **خطوات الحساب** | 1. Retrieve 30-year R_Annual_Mean. 2. Retrieve PET_Hargreaves_Annual. 3. Divide P by PET. |
| **15** | **معالجة القيم الناقصة** | If PET <= 0 or missing, flagged as NoData. Guarded against division by zero. |
| **16** | **مثال رقمي يدوي** | P = 224.0 mm, PET = 1,930.0 mm -> AI_UNEP = 224.0 / 1930.0 = 0.116. |
| **17** | **التفسير العلمي** | Official United Nations Environment Programme (UNEP, 1992) and UNCCD Aridity Index. Standard bioclimatic classes: Hyper-arid (<0.05), Arid (0.05 - 0.20), Semi-arid (0.20 - 0.50), Dry sub-humid (0.50 - 0.65), Humid (>0.65). |
| **18** | **التحذيرات ومحددات الاستخدام** | Value of 0.116 classifies the location strictly as 'Arid' (0.05 - 0.20). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 2485-2510` |

---

### 105. `Water_Deficit_Annual` (العجز/الفائض المائي المناخي السنوي / Annual Climatic Water Deficit/Surplus)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Water_Deficit_Annual` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `WatDefAnn` |
| **2** | **الاسم بالإنجليزية** | Annual Climatic Water Deficit/Surplus |
| **3** | **الاسم بالعربية** | العجز/الفائض المائي المناخي السنوي |
| **4** | **الطبقة والموديول** | `16_Water_Deficit` (16_Water_Deficit (العجز المائي)) |
| **5** | **مجلد الراستر الناتج** | `16_Water_Deficit` |
| **6** | **نوع المؤشر** | Mean |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm/year` |
| **9** | **مصدر البيانات** | Derived climatic water balance from R_Annual_Mean and PET_Hargreaves_Annual |
| **10** | **المتغير الأصلي** | `PRECTOTCORR-PET` |
| **11** | **نوع البيانات الداخلة** | Annual Accumulated Precipitation (mm) and Annual Hargreaves PET (mm) |
| **12** | **التحويل الأولي** | Computed from R_Annual_Mean (mm) and PET_Hargreaves_Annual (mm). |
| **13** | **المعادلة الرياضية** | $$CWD_{Annual} = P_{Annual} - PET_{Annual}$$ |
| **14** | **خطوات الحساب** | 1. Retrieve R_Annual_Mean (P in mm). 2. Retrieve PET_Hargreaves_Annual (PET in mm). 3. Subtract PET from P. |
| **15** | **معالجة القيم الناقصة** | Requires valid precipitation and PET. Expressed as signed difference. |
| **16** | **مثال رقمي يدوي** | P = 224.0 mm, PET = 1,930.0 mm -> CWD = 224.0 - 1,930.0 = -1,706.0 mm/year. |
| **17** | **التفسير العلمي** | Net climatic water balance deficit or surplus. Negative values represent an absolute net atmospheric water deficit that must be supplemented by irrigation or groundwater to sustain vegetation. |
| **18** | **التحذيرات ومحددات الاستخدام** | In arid zones, deficit is large and negative (-1,706 mm indicates severe net hydrological deficit). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 2515-2540` |

---

### 106. `Dry_Months_Count` (عدد الأشهر الجافة بيولوجياً (والتر-ليث) / Biological Dry Months Count (Walter-Lieth))

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `Dry_Months_Count` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `Dry_Months` |
| **2** | **الاسم بالإنجليزية** | Biological Dry Months Count (Walter-Lieth) |
| **3** | **الاسم بالعربية** | عدد الأشهر الجافة بيولوجياً (والتر-ليث) |
| **4** | **الطبقة والموديول** | `17_Dry_Months` (17_Dry_Months (الأشهر الجافة)) |
| **5** | **مجلد الراستر الناتج** | `17_Dry_Months` |
| **6** | **نوع المؤشر** | Count |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `Months (0-12)` |
| **9** | **مصدر البيانات** | Bagnouls & Gaussen bioclimatic criterion evaluated across all 12 monthly climatological pairs |
| **10** | **المتغير الأصلي** | `PRECTOTCORR+T2M` |
| **11** | **نوع البيانات الداخلة** | 12 Climatological Monthly Precipitation Totals (mm) and Mean Temperatures (°C) |
| **12** | **التحويل الأولي** | Evaluated on the 12 monthly pairs (P_m, T_m) where P is in mm and T is in °C. |
| **13** | **المعادلة الرياضية** | $$N_{Dry\_Months} = \sum_{m=1}^{12} \mathbb{I}\left(P_m < 2 \times T_m\right)$$ |
| **14** | **خطوات الحساب** | 1. For each month m from 1 to 12: Check if P_m (mm) < 2 * T_m (°C). 2. If condition holds, score month as dry (1), else wet (0). 3. Sum the 12 scores (0 to 12). |
| **15** | **معالجة القيم الناقصة** | Requires complete 12-month climatology for both P and T. If any month missing, flagged as NoData. |
| **16** | **مثال رقمي يدوي** | Months with P < 2T: Jan(45>24 -> 0), Feb(35>27 -> 0), Mar(25<34 -> 1), Apr(15<43 -> 1), May(5<52 -> 1), Jun(0<59 -> 1), Jul(0<62 -> 1), Aug(0<62 -> 1), Sep(2<56 -> 1), Oct(12<48 -> 1), Nov(35<37 -> 1), Dec(50>28 -> 0) -> Dry Months = 9. |
| **17** | **التفسير العلمي** | Bagnouls-Gaussen (1953) xerothermic index criterion. Months where rainfall is less than twice the temperature (P < 2T) experience severe biological moisture stress where vegetation cannot meet transpirational demand. |
| **18** | **التحذيرات ومحددات الاستخدام** | Integer count ranging between 0 (perhumid) and 12 (hyper-arid desert). |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_drought_fields (line 1373); Toolboxes/raster_atlas_generator.py: lines 2545-2570` |

---

### 107. `T_Annual_Trend_Decade` (اتجاه الحرارة في العقد (الميل المناخي) / Temperature Trend per Decade)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Annual_Trend_Decade` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AnnTrDec` |
| **2** | **الاسم بالإنجليزية** | Temperature Trend per Decade |
| **3** | **الاسم بالعربية** | اتجاه الحرارة في العقد (الميل المناخي) |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Trend |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C/decade` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\beta = \frac{\sum_{i=1}^N (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^N (x_i - \bar{x})^2}; \quad \text{Trend} = \beta \times 10$$ |
| **14** | **خطوات الحساب** | 1. Extract annual mean temperatures y_i for years x_i (N >= 10). 2. Fit OLS linear regression line. 3. Multiply annual slope beta by 10 to express change per decade. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Annual slope = +0.028 °C/year -> Decadal Trend = +0.28 °C/decade. |
| **17** | **التفسير العلمي** | Long-term rate of regional climate warming per decade over the observation record. Benchmark for IPCC climate change detection and attribution. |
| **18** | **التحذيرات ومحددات الاستخدام** | Requires at least 10 complete years; vulnerable to endpoint selection bias in short time series. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 108. `R_Annual_Trend_Decade` (اتجاه الأمطار في العقد (الميل المناخي) / Precipitation Trend per Decade)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Annual_Trend_Decade` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnnTrDec` |
| **2** | **الاسم بالإنجليزية** | Precipitation Trend per Decade |
| **3** | **الاسم بالعربية** | اتجاه الأمطار في العقد (الميل المناخي) |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Trend |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm/decade` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\beta = \frac{\sum_{i=1}^N (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^N (x_i - \bar{x})^2}; \quad \text{Trend} = \beta \times 10$$ |
| **14** | **خطوات الحساب** | 1. Extract annual precipitation totals y_i for years x_i (N >= 10). 2. Fit OLS linear regression line. 3. Multiply annual slope by 10. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Annual slope = -0.52 mm/year -> Decadal Trend = -5.2 mm/decade. |
| **17** | **التفسير العلمي** | Long-term rate of annual precipitation change per decade. Indicates regional wetting or drying trends. |
| **18** | **التحذيرات ومحددات الاستخدام** | High interannual rainfall variability in arid zones can yield statistically insignificant slopes. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 109. `T_Annual_Anom` (شذوذ الحرارة السنوي عن معيار 1991-2020 / Annual Temperature Anomaly vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Annual_Anom` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AnnAnom` |
| **2** | **الاسم بالإنجليزية** | Annual Temperature Anomaly vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ الحرارة السنوي عن معيار 1991-2020 |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta T_{Annual} = \overline{T}_{Recent (2011-2020)} - \overline{T}_{Baseline (1991-2020)}$$ |
| **14** | **خطوات الحساب** | 1. Compute mean annual temperature for the recent decade (2011-2020). 2. Compute mean for standard WMO baseline (1991-2020). 3. Subtract baseline from recent. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent (2011-2020) = 21.1 °C, Baseline (1991-2020) = 20.5 °C -> Anomaly = 21.1 - 20.5 = +0.60 °C. |
| **17** | **التفسير العلمي** | Shift in recent annual thermal state relative to the standard climatological normal. |
| **18** | **التحذيرات ومحددات الاستخدام** | Positive values indicate recent warming above the normal. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 110. `T_Anom_Winter` (شذوذ حرارة الشتاء عن معيار 1991-2020 / Winter Temperature Anomaly vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Anom_Winter` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AnomWin` |
| **2** | **الاسم بالإنجليزية** | Winter Temperature Anomaly vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ حرارة الشتاء عن معيار 1991-2020 |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta T_{Winter} = \overline{T}_{Win, Recent} - \overline{T}_{Win, Baseline}$$ |
| **14** | **خطوات الحساب** | 1. Compute winter (DJF) mean for recent decade. 2. Compute winter mean for baseline. 3. Subtract baseline from recent. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent Winter = 13.6 °C, Baseline Winter = 13.1 °C -> Anomaly = +0.50 °C. |
| **17** | **التفسير العلمي** | Winter seasonal thermal shift. |
| **18** | **التحذيرات ومحددات الاستخدام** | Winter warming reduces chill hours for fruit trees. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 111. `T_Anom_Summer` (شذوذ حرارة الصيف عن معيار 1991-2020 / Summer Temperature Anomaly vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `T_Anom_Summer` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `T_AnomSum` |
| **2** | **الاسم بالإنجليزية** | Summer Temperature Anomaly vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ حرارة الصيف عن معيار 1991-2020 |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Summer |
| **8** | **الوحدة الفيزيائية** | `°C` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `T2M` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta T_{Summer} = \overline{T}_{Sum, Recent} - \overline{T}_{Sum, Baseline}$$ |
| **14** | **خطوات الحساب** | 1. Compute summer (JJA) mean for recent decade. 2. Compute summer mean for baseline. 3. Subtract baseline from recent. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent Summer = 31.4 °C, Baseline Summer = 30.5 °C -> Anomaly = +0.90 °C. |
| **17** | **التفسير العلمي** | Summer seasonal thermal shift, showing amplified summer warming rates. |
| **18** | **التحذيرات ومحددات الاستخدام** | Intensifies peak electricity demand for air conditioning. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 112. `R_Annual_Anom` (شذوذ الأمطار السنوي عن معيار 1991-2020 / Annual Precipitation Anomaly vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Annual_Anom` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnnAnom` |
| **2** | **الاسم بالإنجليزية** | Annual Precipitation Anomaly vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ الأمطار السنوي عن معيار 1991-2020 |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta R_{Annual} = \overline{P}_{Recent (2011-2020)} - \overline{P}_{Baseline (1991-2020)}$$ |
| **14** | **خطوات الحساب** | 1. Compute mean annual precipitation for recent decade. 2. Compute for 1991-2020 normal. 3. Compute Recent - Baseline. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent = 210.0 mm, Baseline = 224.0 mm -> Absolute Anomaly = 210.0 - 224.0 = -14.0 mm. |
| **17** | **التفسير العلمي** | Absolute volume change in annual precipitation over the recent decade. |
| **18** | **التحذيرات ومحددات الاستخدام** | Negative values denote rainfall deficit relative to normal. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 113. `R_Annual_Anom_Pct` (شذوذ الأمطار السنوي بالنسبة المئوية / Annual Precipitation Anomaly Percent vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Annual_Anom_Pct` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnnAnPct` |
| **2** | **الاسم بالإنجليزية** | Annual Precipitation Anomaly Percent vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ الأمطار السنوي بالنسبة المئوية |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Annual |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta R_{Annual, \%} = \frac{\overline{P}_{Recent} - \overline{P}_{Baseline}}{\overline{P}_{Baseline}} \times 100$$ |
| **14** | **خطوات الحساب** | 1. Check if baseline >= 5 mm. 2. Compute (Recent - Baseline) / Baseline * 100. 3. If baseline < 5 mm, return None to prevent explosive percentages. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent = 210.0 mm, Baseline = 224.0 mm -> Relative Anomaly = (-14.0 / 224.0) * 100 = -6.25%. |
| **17** | **التفسير العلمي** | Percentage anomaly in annual rainfall relative to climatological normal. |
| **18** | **التحذيرات ومحددات الاستخدام** | Guarded with None when baseline < 5 mm in hyper-arid zones to prevent division by near-zero. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 114. `R_Anom_Winter` (شذوذ أمطار الشتاء عن معيار 1991-2020 / Winter Precipitation Anomaly vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Anom_Winter` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnomWin` |
| **2** | **الاسم بالإنجليزية** | Winter Precipitation Anomaly vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ أمطار الشتاء عن معيار 1991-2020 |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `mm` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta R_{Winter} = \overline{P}_{Win, Recent} - \overline{P}_{Win, Baseline}$$ |
| **14** | **خطوات الحساب** | 1. Compute winter (DJF) total for recent decade. 2. Compute winter total for baseline. 3. Compute Recent - Baseline. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent Winter = 120.0 mm, Baseline Winter = 130.0 mm -> Winter Anomaly = -10.0 mm. |
| **17** | **التفسير العلمي** | Absolute change in winter recharge precipitation. |
| **18** | **التحذيرات ومحددات الاستخدام** | Directly impacts winter crop yields and dam inflows. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---

### 115. `R_Anom_Winter_Pct` (شذوذ أمطار الشتاء بالنسبة المئوية / Winter Precipitation Anomaly Percent vs 1991-2020)

| بند المواصفة | البعد العلمي والفني | القيمة التنفيذية المعتمدة بالكود |
|:---:|:---|:---|
| **1** | **اسم الحقل الفعلي** | **قاعدة البيانات/الراستر**: `R_Anom_Winter_Pct` &nbsp;\|&nbsp; **شيب فايل (10 حروف)**: `R_AnomWPct` |
| **2** | **الاسم بالإنجليزية** | Winter Precipitation Anomaly Percent vs 1991-2020 |
| **3** | **الاسم بالعربية** | شذوذ أمطار الشتاء بالنسبة المئوية |
| **4** | **الطبقة والموديول** | `18_Trends_And_Anomalies` (18_Trends_And_Anomalies (الاتجاهات والشذوذ)) |
| **5** | **مجلد الراستر الناتج** | `18_Trends_And_Anomalies` |
| **6** | **نوع المؤشر** | Anomaly |
| **7** | **الفترة الزمنية** | Winter |
| **8** | **الوحدة الفيزيائية** | `%` |
| **9** | **مصدر البيانات** | Ordinary Least Squares (OLS) decadal linear trend regression and WMO 1991-2020 baseline comparison |
| **10** | **المتغير الأصلي** | `PRECTOTCORR` |
| **11** | **نوع البيانات الداخلة** | Annual and Seasonal multi-year time series (minimum 10 years for trend) |
| **12** | **التحويل الأولي** |  |
| **13** | **المعادلة الرياضية** | $$\Delta R_{Winter, \%} = \frac{\overline{P}_{Win, Recent} - \overline{P}_{Win, Baseline}}{\overline{P}_{Win, Baseline}} \times 100$$ |
| **14** | **خطوات الحساب** | 1. Check if baseline winter total >= 5 mm. 2. Compute (Recent - Baseline) / Baseline * 100. |
| **15** | **معالجة القيم الناقصة** | Requires minimum 10 valid annual values for OLS trend (_lin_trend_per_decade). Relative precipitation anomalies guarded when baseline < 5 mm. |
| **16** | **مثال رقمي يدوي** | Recent = 120.0 mm, Baseline = 130.0 mm -> Relative Anomaly = (-10.0 / 130.0) * 100 = -7.69%. |
| **17** | **التفسير العلمي** | Percentage departure in winter rainfall from the 30-year normal. |
| **18** | **التحذيرات ومحددات الاستخدام** | Guarded with None when baseline winter total < 5 mm. |
| **19** | **مرجع التنفيذ بالكود** | `Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: _lin_trend_per_decade (line 1185), _recent_minus_baseline (line 1201); Toolboxes/raster_atlas_generator.py: lines 2575-2630` |

---
