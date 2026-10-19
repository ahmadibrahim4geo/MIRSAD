"""Human-readable output dictionary. Documentation only; no calculations here.

Each row states one quantity, one period and one operation. Keep the legacy
technical keys separate from translated names and from the calculation units.
"""

MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December')
MONTHS_AR = ('يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو',
             'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر')
SEASONS = {'Winter': (12, 1, 2), 'Spring': (3, 4, 5),
           'Summer': (6, 7, 8), 'Autumn': (9, 10, 11)}
SEASONS_AR = dict(Winter='الشتاء', Spring='الربيع', Summer='الصيف', Autumn='الخريف')

# prefix: Arabic quantity, English quantity, normalized source, calculation unit
QUANTITIES = {
    'T': ('درجة حرارة الهواء', 'air temperature', 'T2M', '°C'),
    'LST': ('درجة حرارة سطح الأرض', 'land surface temperature', 'TS', '°C'),
    'R': ('هطول الأمطار', 'precipitation', 'PRECTOTCORR', 'mm'),
    'PSL': ('الضغط عند مستوى سطح البحر', 'sea-level pressure', 'SLP', 'hPa'),
    'PS': ('الضغط السطحي', 'surface pressure', 'PS', 'hPa'),
    'W_Spd': ('سرعة الرياح', 'wind speed', 'WS10M', 'm/s'),
    'W_Dir': ('اتجاه الرياح', 'wind direction', 'WD10M', '°'),
    'RH': ('الرطوبة النسبية', 'relative humidity', 'RH2M', '%'),
    'Td': ('درجة حرارة نقطة الندى', 'dew-point temperature', 'T2MDEW', '°C'),
    'Sol': ('الإشعاع الشمسي', 'solar radiation', 'ALLSKY_SFC_SW_DWN', 'kWh/m²/day'),
    'UV': ('مؤشر الأشعة فوق البنفسجية', 'UV index', 'ALLSKY_SFC_UV_INDEX', 'index'),
    'Cld': ('الغطاء السحابي', 'cloud cover', 'CLOUD_AMT', '%'),
    'HI': ('مؤشر الحرارة', 'Heat Index', 'HI', '°C'),
    'WC': ('برودة الرياح', 'Wind Chill', 'WC', '°C'),
    'ET': ('البخر والنتح المحتمل', 'potential evapotranspiration', 'PET', 'mm'),
}


def field_reference(module, field, arabic):
    """Return localized title, explicit period, internal unit and exact operation.

    Unknown structures fail generation instead of falling back to vague prose.
    Available field keys are independently checked against the reviewed kernel.
    """
    def t(ar, en):
        return ar if arabic else en

    month = next((m for m in MONTHS if m in field.split('_')), None)
    season = next((s for s in SEASONS if s in field.split('_')), None)
    period_key = month or season or ('Month' if 'Month' in field.split('_') and module == 'Trends & Anomalies' else 'Annual')
    if month:
        period = t('شهر ' + MONTHS_AR[MONTHS.index(month)] + ' عبر سنوات الدراسة', month + ' across study years')
        short = t(MONTHS_AR[MONTHS.index(month)], month)
        months = (MONTHS.index(month) + 1,)
    elif season:
        months = SEASONS[season]
        names = t('، '.join(MONTHS_AR[m-1] for m in months), ', '.join(MONTHS[m-1] for m in months))
        short = t(SEASONS_AR[season], season)
        period = short + ' (' + names + ')'
    elif period_key == 'Month':
        months = tuple(range(1, 13))
        short = t('ملخص الشهور', 'monthly summary')
        period = t('ملخص أعمدة يناير إلى ديسمبر الصالحة', 'Summary of valid January–December output columns')
    else:
        months = tuple(range(1, 13))
        short = t('السنة', 'year')
        period = t('السنة: يناير إلى ديسمبر', 'Year: January–December')

    known_annual = {'DM_Aridity_Annual', 'UNEP_Aridity_Annual', 'Water_Deficit_Annual',
                   'Dry_Months_Count', 'PET_Hargreaves_Annual', 'T_Annual_Max_Mean',
                   'T_Annual_Min_Mean', 'Sol_Annual_Total', 'W_Spd_Annual_Max_Month',
                   'W_Spd_Annual_Min_Month', 'LST_minus_T_Annual'}
    if not (month or season or field in known_annual or '_Annual_' in field or
            (module == 'Trends & Anomalies' and period_key == 'Month')):
        raise ValueError('Unknown output period: ' + module + ': ' + field)

    def row(title, unit, calculation):
        return dict(title=title, period=period, unit=unit, calculation=calculation)

    if module == 'Trends & Anomalies':
        rain = field.startswith('R_')
        quantity = t('هطول الأمطار', 'precipitation') if rain else t('درجة حرارة الهواء', 'air temperature')
        unit = 'mm' if rain else '°C'
        trend = 'Trend_Decade' in field
        pct = field.endswith('_Pct')
        name = t('اتجاه ', 'Trend in ') if trend else t('شذوذ ', 'Anomaly of ')
        title = name + quantity + ' — ' + short
        if pct:
            title = t('النسبة المئوية لشذوذ هطول الأمطار — ', 'Percentage precipitation anomaly — ') + short
        if trend:
            unit += t('/عقد (10 سنوات)', '/decade (10 years)')
        if pct:
            unit = '%'
        if period_key == 'Month':
            title = t('متوسط الاتجاهات الشهرية لـ', 'Mean monthly trends in ') + quantity if trend else (
                t('متوسط نسب شذوذ الأمطار الشهرية', 'Mean monthly precipitation anomaly percentages') if pct else
                t('متوسط الشذوذات الشهرية لـ', 'Mean monthly anomalies of ') + quantity)
            if trend:
                keys = ', '.join(('R_' if rain else 'T_') + m + '_Trend_Decade' for m in MONTHS)
            else:
                keys = ', '.join(('R_Anom_' if rain else 'T_Anom_') + m + ('_Pct' if pct else '') for m in MONTHS)
            rule = t('المتوسط الحسابي للأعمدة الشهرية الصالحة التالية بعد حسابها وتقريبها: ',
                     'Arithmetic mean of the following valid monthly columns after their calculation and rounding: ') + keys + '.'
            rule += t(' هذا ملخص للحقول الشهرية، وليس حقل الشذوذ أو الاتجاه السنوي.',
                      ' This summarizes monthly fields; it is not the annual anomaly or annual trend field.')
            return row(title, unit, rule)
        if month:
            series = t('مجاميع المطر لشهر ' + short + ' في كل سنة', 'each year’s ' + month + ' rainfall total') if rain else t(
                'متوسطات حرارة شهر ' + short + ' في كل سنة', 'each year’s ' + month + ' mean air temperature')
        elif season:
            series = t('مجموع مطر أشهر ' + period + ' لكل سنة مكتملة الفصل', 'each year’s rainfall sum for ' + period + ', requiring all three months') if rain else t(
                'متوسط حرارة أشهر ' + period + ' لكل سنة مكتملة الفصل', 'each year’s mean air temperature for ' + period + ', requiring all three months')
        else:
            series = t('مجموع المطر لكل سنة مكتملة الشهور الـ12', 'each complete year’s 12-month rainfall total') if rain else t(
                'متوسط حرارة الشهور الـ12 لكل سنة مكتملة', 'each complete year’s mean of 12 monthly air temperatures')
        if trend:
            rule = t('تكوين سلسلة من ' + series + '، ثم حساب ميل الانحدار الخطي بالمربعات الصغرى مقابل السنوات الفعلية وضربه ×10. يلزم 8 سنوات صالحة على الأقل؛ الموجب زيادة والسالب انخفاض.',
                     'Build a series of ' + series + '; fit an ordinary least-squares slope against actual years and multiply by 10. Requires at least 8 valid years; positive means increasing, negative decreasing.')
        else:
            rule = t('تكوين سلسلة من ' + series + '. الشذوذ = متوسط أحدث 10 سنوات صالحة كحد أقصى (5 على الأقل) ناقص متوسط سنوات 1991–2020 الصالحة (20 على الأقل).',
                     'Build a series of ' + series + '. Anomaly = mean of up to the latest 10 valid years (at least 5) minus mean of valid 1991–2020 years (at least 20).')
            if pct:
                rule += t(' الناتج هنا = 100 × الشذوذ ÷ القيمة المطلقة لمتوسط خط الأساس؛ يلزم خط أساس مطلق لا يقل عن 5 مم.',
                          ' This field = 100 × anomaly / absolute baseline mean; the absolute baseline must be at least 5 mm.')
            else:
                rule += t(' الموجب أعلى من خط الأساس والسالب أقل منه.', ' Positive is above baseline; negative is below it.')
        return row(title, unit, rule)

    special = {
        'DM_Aridity_Annual': (
            t('مؤشر دي مارتون للجفاف السنوي', 'Annual De Martonne aridity index'), t('مؤشر (P بالـmm، T بالـ°C)', 'index (P in mm, T in °C)'),
            t('مجموع متوسطات المطر الشهرية الـ12 ÷ (متوسط حرارة الشهور الـ12 +10)، وتقريب منزلتين. يلزم اكتمال المطر والحرارة وأن يكون المقام أكبر من 0.01.',
              'Sum of 12 climatological monthly rainfall totals / (mean of 12 monthly temperatures + 10), rounded to two decimals. Requires all rainfall/temperature months and denominator >0.01.')),
        'UNEP_Aridity_Annual': (
            t('مؤشر UNEP للجفاف السنوي', 'Annual UNEP aridity index'), t('نسبة بلا وحدة', 'dimensionless ratio'),
            t('مجموع متوسطات المطر الشهرية الـ12 ÷ مجموع PET للشهور الـ12؛ تقريب 3 منازل. يلزم اكتمال المجموعين وPET أكبر من 0.01 مم؛ ليست نسبة مئوية.',
              'Sum of 12 climatological monthly rainfall totals / sum of 12 monthly PET values; three decimals. Requires both complete sums and PET >0.01 mm; not a percentage.')),
        'Water_Deficit_Annual': (
            t('الميزان المائي السنوي (مطر ناقص بخر ونتح محتمل)', 'Annual water balance (precipitation minus PET)'), 'mm/year',
            t('مجموع متوسطات المطر الشهرية الـ12 ناقص مجموع PET للشهور الـ12؛ تقريب منزلة. السالب عجز والموجب فائض، وليس مقدار العجز موجبًا في كل الحالات. يلزم اكتمال المجموعين.',
              'Sum of 12 climatological monthly rainfall totals minus sum of 12 monthly PET values; one decimal. Negative is deficit, positive surplus; it is not an always-positive deficit magnitude. Requires both complete sums.')),
        'Dry_Months_Count': (
            t('عدد الأشهر الجافة في السنة', 'Number of dry months per year'), t('شهر (0–12)', 'months (0–12)'),
            t('عد الشهور التي يكون متوسط مجموع المطر فيها بالـmm أقل من ضعفي متوسط الحرارة بالـ°C. تساوي القيمتين لا يعد جفافًا. يلزم اكتمال 12 شهرًا من المطر والحرارة.',
              'Count months whose climatological rainfall total in mm is strictly below twice their mean temperature in °C. Equality is not dry. Requires all 12 rainfall and temperature months.')),
        'PET_Hargreaves_Annual': (
            t('البخر والنتح المحتمل السنوي بطريقة هارجريفز', 'Annual Hargreaves potential evapotranspiration'), 'mm/year',
            t('مجموع قيم PET المحسوبة من مناخيات الشهور الـ12، ثم تقريب منزلة؛ نفس القيمة المحسوبة في ET_Annual_Mean باسم تقني آخر. ليس قياسًا للبخر الفعلي.',
              'Sum of PET calculated from all 12 climatological months, rounded to one decimal; the same calculated value as ET_Annual_Mean under another technical key. Not measured actual evapotranspiration.')),
        'T_Max_Summer_Month_Mean': (
            t('أعلى متوسط حرارة لشهر صيفي', 'Warmest summer-month mean air temperature'), '°C',
            t('أكبر متوسط مناخي لحرارة الهواء T2M بين يونيو ويوليو وأغسطس. قيمة حرارة وليست اسم الشهر، ولا تستخدم T2M_MAX.',
              'Maximum climatological T2M mean among June, July and August. A temperature value, not a month name; does not use T2M_MAX.')),
        'T_Min_Winter_Month_Mean': (
            t('أقل متوسط حرارة لشهر شتوي', 'Coldest winter-month mean air temperature'), '°C',
            t('أصغر متوسط مناخي لحرارة الهواء T2M بين ديسمبر ويناير وفبراير. قيمة حرارة وليست اسم الشهر، ولا تستخدم T2M_MIN.',
              'Minimum climatological T2M mean among December, January and February. A temperature value, not a month name; does not use T2M_MIN.')),
        'T_Annual_Max_Mean': (
            t('المتوسط السنوي لدرجات الحرارة العظمى', 'Annual mean maximum air temperature'), '°C',
            t('متوسط مناخيات الشهور لقيم العظمى T2M_MAX؛ ليس أعلى متوسط شهري ولا أعلى رصد مفرد.',
              'Mean of monthly climatologies of maximum temperature T2M_MAX; not the highest monthly mean or the highest individual observation.')),
        'T_Annual_Min_Mean': (
            t('المتوسط السنوي لدرجات الحرارة الصغرى', 'Annual mean minimum air temperature'), '°C',
            t('متوسط مناخيات الشهور لقيم الصغرى T2M_MIN؛ ليس أقل متوسط شهري ولا أقل رصد مفرد.',
              'Mean of monthly climatologies of minimum temperature T2M_MIN; not the lowest monthly mean or the lowest individual observation.')),
        'Sol_Annual_Total': (
            t('متوسط إجمالي الطاقة الشمسية السنوية', 'Mean annual total solar energy'), 'kWh/m²/year',
            t('لكل سنة: جمع متوسط الطاقة اليومية لكل شهر × أيام ذلك الشهر الفعلية، ثم أخذ متوسط المجاميع السنوية المتاحة. النواة قد تجمع سنة جزئية؛ راجع حراس التغطية. يختلف عن Sol_Annual_Mean ذي الوحدة اليومية.',
              'For each year, sum each month’s mean daily energy × its actual calendar days; then average available yearly totals. The kernel can include partial years; inspect coverage guards. Unlike Sol_Annual_Mean, this is not daily energy.')),
        'HI_Winter_Mean': (
            t('متوسط مؤشر الرطوبة الحرارية Humidex في الشتاء', 'Winter mean Humidex'), '°C',
            t('حساب Humidex من حرارة ورطوبة كل شهر مناخي في ديسمبر ويناير وفبراير، ثم متوسط القيم الصالحة. رغم البادئة HI، هذا الحقل يستخدم Humidex وليس مؤشر Rothfusz.',
              'Calculate Humidex from each climatological month’s temperature and humidity in December, January and February, then average valid results. Despite its HI prefix, this field uses Humidex rather than Rothfusz Heat Index.')),
        'WBGT_Summer_Mean': (
            t('متوسط تقدير WBGT في الظل صيفًا', 'Summer mean shade WBGT estimate'), '°C',
            t('متوسط التقدير الشهري (0.7 × حرارة البصيلة الرطبة بطريقة Stull + 0.3 × حرارة الهواء) في يونيو ويوليو وأغسطس. تقدير مناخي في الظل، وليس قياس سلامة مهنية معتمدًا.',
              'Mean monthly estimate (0.7 × Stull wet-bulb temperature + 0.3 × air temperature) for June, July and August. A climatological shade estimate, not a certified occupational safety measurement.')),
    }
    if field in special:
        return row(*special[field])

    if field.startswith('LST_minus_T_'):
        title = t('فرق حرارة سطح الأرض عن حرارة الهواء — ', 'Land-minus-air temperature difference — ') + short
        rule = t('متوسط حرارة سطح الأرض TS للفترة ' + period + ' ناقص متوسط حرارة الهواء T2M للفترة نفسها؛ الموجب يعني أن سطح الأرض أدفأ. تقريب منزلتين.',
                 'Mean land surface temperature TS for ' + period + ' minus mean air temperature T2M for the same period; positive means land is warmer. Rounded to two decimals.')
        if month:
            rule += t(' يستخدم متوسطي الشهر المقربين مسبقًا.', ' Uses the two already rounded monthly means.')
        return row(title, t('فرق °C', '°C difference'), rule)

    prefix = next((p for p in sorted(QUANTITIES, key=len, reverse=True) if field.startswith(p+'_')), None)
    if prefix is None:
        raise ValueError('Unknown output quantity: ' + module + ': ' + field)
    ar_name, en_name, source, unit = QUANTITIES[prefix]
    quantity = t(ar_name, en_name)
    ar_of = 'لل' + ar_name[2:] if ar_name.startswith('ال') else 'ل' + ar_name
    if field in ('W_Spd_Annual_Max_Month', 'W_Spd_Annual_Min_Month'):
        maximum = 'Max' in field
        return row(t(('أعلى' if maximum else 'أقل') + ' متوسط شهري لسرعة الرياح',
                     ('Highest' if maximum else 'Lowest') + ' climatological monthly wind speed'), unit,
                   t(('أكبر' if maximum else 'أصغر') + ' قيمة بين متوسطات سرعة الرياح للشهور الـ12 عبر سنوات الدراسة. الناتج سرعة وليس رقم الشهر.',
                     ('Maximum' if maximum else 'Minimum') + ' of the 12 climatological monthly wind speeds. The result is a speed, not a month number.'))
    if field.endswith('_Range'):
        title = t(('مدى ' + short + ' بين السنوات' if month else 'المدى السنوي') + ' ' + ar_of,
                  (month + ' interannual range' if month else 'Annual range') + ' of ' + quantity)
        if prefix in ('RH', 'Cld'):
            unit = t('نقطة مئوية', 'percentage points')
        if prefix == 'ET':
            unit = 'mm/month'
        if month:
            rule = t('أكبر قيمة شهرية ' + ar_of + ' في ' + short + ' ناقص أصغر قيمة لنفس الشهر عبر سنوات الدراسة. يلزم سنتان صالحتان على الأقل؛ لا تقارن شهورًا مختلفة.',
                     'Maximum monthly ' + quantity + ' in ' + month + ' minus minimum for that same month across study years. Requires at least two valid years; does not compare different calendar months.')
            if prefix == 'ET':
                rule += t(' يحسب PET لكل سنة بأيام الشهر الفعلية، ثم يحسب المدى ويقرب منزلتين.',
                          ' PET is calculated for each year using actual calendar days, then its range is rounded to two decimals.')
        else:
            rule = t('أعلى قيمة شهرية مناخية ' + ar_of + ' ناقص أدناها بين يناير وديسمبر. يقارن شهور السنة المناخية؛ لا يمثل الفرق بين المجاميع السنوية عبر السنوات.',
                     'Highest minus lowest climatological monthly ' + quantity + ' among January–December. Compares calendar-month climatologies, not yearly totals across years.')
            if prefix == 'ET':
                rule += t(' يلزم اكتمال قيم PET للشهور الـ12؛ تقريب منزلة.', ' Requires all 12 monthly PET values; one decimal.')
            else:
                rule += t(' يلزم شهران مناخيان صالحان على الأقل.', ' Requires at least two valid climatological months.')
        if prefix in ('HI', 'WC'):
            rule += t(' تستخدم قيم المؤشر بعد تطبيق معادلته على مناخيات المدخلات الشهرية.',
                      ' Uses index values after applying its equation to monthly input climatologies.')
        return row(title, unit, rule)
    if not field.endswith('_Mean'):
        raise ValueError('Unknown output statistic: ' + module + ': ' + field)
    title = t(('متوسط ' + short if month or season else 'المتوسط السنوي') + ' ' + ar_of,
              (short + ' mean' if month or season else 'Annual mean') + ' ' + quantity)
    if prefix == 'ET':
        unit = 'mm/month' if month else ('mm/season' if season else 'mm/year')
        if month:
            days = (31,28.25,31,30,31,30,31,31,30,31,30,31)[months[0]-1]
            rule = t('قيمة PET لشهر ' + short + ' محسوبة بمعادلة هارجريفز من متوسطات حرارة هذا الشهر عبر سنوات الدراسة، وليست متوسط PET اليومي. تضرب المعادلة في ' + str(days) + ' يومًا لهذا الشهر المناخي. تقريب منزلة.',
                     month + ' PET calculated with Hargreaves from that month’s climatological temperatures, not mean daily PET. The equation multiplies by ' + str(days) + ' days for this climatological month. One decimal.')
        else:
            keys = ', '.join('ET_'+MONTHS[m-1]+'_Mean' for m in months) if season else t('من ET_January_Mean إلى ET_December_Mean', 'ET_January_Mean through ET_December_Mean')
            rule = t('جمع PET للشهور التابعة للفترة ' + period + ' قبل تقريبها، ثم تقريب الناتج لمنزلة. يلزم اكتمال ' + ('الأشهر الثلاثة' if season else '12 شهرًا') + '. أعمدة الشهور المقابلة: ',
                     'Sum unrounded monthly PET for ' + period + ', then round to one decimal. Requires all ' + str(len(months)) + ' months. Corresponding monthly columns: ') + keys + '.'
            rule += t(' الاسم التقني Mean محفوظ؛ العملية هنا مجموع PET المحسوب من الشهور المناخية وليست القسمة على عدد الشهور.',
                      ' The legacy Mean key is retained; this operation sums PET from climatological months rather than dividing by the number of months.')
        return row(title, unit, rule)
    if prefix == 'R':
        unit = 'mm/month' if month else ('mm/season' if season else 'mm/year')
        if month:
            rule = t('متوسط مجاميع المطر لشهر ' + short + ' عبر السنوات ذات القيمة الشهرية الصالحة: مجموع تلك القيم ÷ عددها. ليس متوسط كمية المطر اليومية.',
                     'Average valid ' + month + ' rainfall totals across study years: sum those monthly totals / their count. Not mean daily rainfall.')
        else:
            rule = t('لكل سنة تجمع أمطار أشهر ' + period + ' عند اكتمالها، ثم يؤخذ المتوسط الحسابي لهذه المجاميع عبر السنوات الصالحة. يلزم ' + str(len(months)) + ' شهرًا لكل مجموع؛ لا يقسم مجموع الفترة على عدد شهورها.',
                     'For each year, sum rainfall for ' + period + ' only when complete, then average these totals across valid years. Each total requires all ' + str(len(months)) + ' months; the period total is not divided by its month count.')
        return row(title, unit, rule)
    if prefix == 'W_Dir':
        return row(title, unit, t('متوسط دائري متساوي الأوزان لاتجاهات الرياح الشهرية الصالحة في ' + period + ' عبر سنوات الدراسة؛ ليس متوسطًا حسابيًا للدرجات ولا ترجيحًا بسرعة الرياح. عند تعادل اتجاهات متعاكسة تكون النتيجة NULL. 0° شمال، 90° شرق، 180° جنوب، 270° غرب.',
                                  'Equal-weight circular mean of valid monthly wind directions for ' + period + ' across study years; not an arithmetic degree average or speed-weighted direction. Balanced opposing directions give NULL. 0° north, 90° east, 180° south, 270° west.'))
    if prefix in ('HI', 'WC'):
        method = 'Rothfusz' if prefix == 'HI' else 'Wind Chill'
        if month:
            rule = t('تطبيق معادلة ' + method + ' على متوسطات مدخلات شهر ' + short + ' عبر السنوات، ثم تقريب منزلتين. لا يحسب متوسط مؤشر كل يوم.',
                     'Apply ' + method + ' to ' + month + ' input climatologies, then round to two decimals. Does not average daily index values.')
        else:
            rule = t('حساب ' + method + ' لكل شهر مناخي في ' + period + '، ثم المتوسط الحسابي للقيم الصالحة. لا يمثل أعلى مؤشر يومي مسجل.',
                     'Calculate ' + method + ' for each climatological month in ' + period + ', then average valid index values. Not the highest observed daily index.')
        return row(title, unit, rule)
    if month:
        rule = t('متوسط القيم الشهرية الصالحة لـ' + quantity + ' في ' + short + ' عبر سنوات الدراسة: مجموع القيم ÷ عددها. المدخل المعياري: ',
                 'Average valid monthly ' + quantity + ' values for ' + month + ' across study years: sum / count. Normalized input: ') + source + '.'
    else:
        names = t('، '.join(MONTHS_AR[m-1] for m in months), ', '.join(MONTHS[m-1] for m in months))
        rule = t('المتوسط الحسابي لمتوسطات ' + quantity + ' الشهرية المناخية لشهور ' + names + ' الصالحة، دون ترجيح بعدد أيام الشهر. المدخل المعياري: ',
                 'Arithmetic mean of valid climatological monthly ' + quantity + ' for ' + names + ', without weighting by month length. Normalized input: ') + source + '.'
    if prefix == 'Sol':
        rule += t(' تحول الطاقة اليومية من MJ/m²/day بالقسمة على 3.6؛ القيمة متوسط يومي وليست مجموع طاقة الفترة.',
                  ' Convert daily energy from MJ/m²/day by dividing by 3.6; the result is mean daily energy, not the period’s energy total.')
    if prefix == 'UV':
        rule += t(' بعد تحويل NASA إلى تقدير وقت الظهيرة، أو استخدام مؤشر المصدر الجاهز في المسار المصرح به؛ راجع حدود تحويل UV.',
                  ' After NASA-to-estimated-noon conversion, or using a ready index in the declared provider path; see UV conversion limits.')
    return row(title, unit, rule)
