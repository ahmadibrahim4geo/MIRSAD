# -*- coding: utf-8 -*-
"""October 2026 HTML docs refresh (re-runnable, idempotent).

Complete EN/AR:
  - 21 new field cards each (UV_Seasonal_Range, HI x3, WC x17)
  - sequential renumbering + count updates (115 -> 136)
  - chrome language purity (EN: 'Arabic Edition' link; AR: value-tagged options)
  - copy-field-name buttons + toast + back-to-top
  - 'What is new (Oct 2026)' section + sidebar link

Usage: python3 scripts/update_html_docs_oct2026.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "Documents")

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]

CARD_TPL = """<div class="field-card" data-module="{mod}" data-period="{period}" data-type="{typ}" data-search="{search}">
                <div class="card-header" onclick="toggleCard(this)">
                    <div class="card-title-group">
                        <h3>
                            <span>{num:03d}. <code>{fld}</code></span>
                            <span class="sub-name">({en})</span>
                        </h3>
                        <div class="sub-name" style="margin-top:2px;">{ar} &bull; 10-char Shapefile: <code>{shp}</code> <button class="btn btn-secondary btn-copy" onclick="event.stopPropagation();copyField('{fld}')">Copy</button></div>
                    </div>
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span class="badge badge-blue">{mod}</span>
                        <span class="badge badge-teal">{period}</span>
                        <span class="badge badge-orange">{unit}</span>
                        <span style="font-size:1.1rem; color:var(--text-muted); margin-left:8px;">&#9662;</span>
                    </div>
                </div>
                <div class="card-body">
                    <table class="meta-table">
                        <tr><th>{t_fld}</th><td><code>{fld}</code></td></tr>
                        <tr><th>{t_shp}</th><td><code>{shp}</code></td></tr>
                        <tr><th>{t_en}</th><td>{en}</td></tr>
                        <tr><th>{t_mod}</th><td>{mod} (<code>{mod}</code>)</td></tr>
                        <tr><th>{t_per}</th><td>{period} &bull; {typ}</td></tr>
                        <tr><th>{t_unit}</th><td><strong>{unit}</strong></td></tr>
                        <tr><th>{t_src}</th><td>{src}</td></tr>
                        <tr><th>{t_calc}</th><td>{calc}</td></tr>
                        <tr><th>{t_ref}</th><td><code>{ref}</code></td></tr>
                    </table>

                    <h4 style="margin: 12px 0 6px 0; color:var(--primary); font-size:0.95rem;">{t_form}</h4>
                    <div class="formula-box">
                        $${form}$$
                    </div>

                    <h4 style="margin: 12px 0 6px 0; color:var(--primary); font-size:0.95rem;">{t_note}</h4>
                    <p style="font-size:0.9rem; margin-bottom:8px;">{note}</p>
                </div>
            </div>
"""

SHP = {"UV_Seasonal_Range": "UV_SeaRng",
       "HI_Spring_Mean": "HI_SprMean", "HI_Autumn_Mean": "HI_AutMean",
       "HI_Seasonal_Range": "HI_SeaRng",
       "WC_Spring_Mean": "WC_SprMean", "WC_Summer_Mean": "WC_SumMean",
       "WC_Autumn_Mean": "WC_AutMean", "WC_Annual_Range": "WC_AnRng",
       "WC_Seasonal_Range": "WC_SeaRng", "WC_January_Mean": "WC_JanMean",
       "WC_February_Mean": "WC_FebMean", "WC_March_Mean": "WC_MarMean",
       "WC_April_Mean": "WC_AprMean", "WC_May_Mean": "WC_MayMean",
       "WC_June_Mean": "WC_JunMean", "WC_July_Mean": "WC_JulMean",
       "WC_August_Mean": "WC_AugMean", "WC_September_Mean": "WC_SepMean",
       "WC_October_Mean": "WC_OctMean", "WC_November_Mean": "WC_NovMean",
       "WC_December_Mean": "WC_DecMean"}


def new_cards_en():
    uv = [dict(fld="UV_Seasonal_Range", en="Seasonal UV Index Range",
               ar="Seasonal amplitude of noon UV exposure",
               mod="09_UV_Index", period="Annual", typ="Range", unit="Index",
               src="NASA POWER ALLSKY_SFC_UV_INDEX converted to WHO noon-maximum",
               calc="Highest seasonal noon-max mean minus lowest seasonal noon-max mean",
               ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: uv_mean24_to_noonmax",
               form="UV_{Seasonal\\_Range} = \\max(DJF,MAM,JJA,SON) - \\min(DJF,MAM,JJA,SON)",
               note="Seasonal amplitude of noon UV exposure; fixed WHO scale applies.",
               search="uv seasonal range noon maximum who")]
    hi = [dict(fld="HI_Spring_Mean", en="Spring Mean Heat Index",
               ar="Spring heat build-up (Khamaseen season)",
               mod="11_Heat_Index", period="Spring", typ="Mean", unit="°C",
               src="Derived from T2M and RH2M (Rothfusz)",
               calc="Mean of monthly Rothfusz HI for months 3,4,5",
               ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_thermal_stress_fields",
               form="HI_{Spring} = (HI_{Mar}+HI_{Apr}+HI_{May})/3",
               note="Spring heat-stress build-up.",
               search="hi spring mean heat index rothfusz"),
          dict(fld="HI_Autumn_Mean", en="Autumn Mean Heat Index",
               ar="Late-summer residual heat",
               mod="11_Heat_Index", period="Autumn", typ="Mean", unit="°C",
               src="Derived from T2M and RH2M (Rothfusz)",
               calc="Mean of monthly Rothfusz HI for months 9,10,11",
               ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_thermal_stress_fields",
               form="HI_{Autumn} = (HI_{Sep}+HI_{Oct}+HI_{Nov})/3",
               note="Autumn heat (September peak).",
               search="hi autumn mean heat index rothfusz"),
          dict(fld="HI_Seasonal_Range", en="Seasonal Heat Index Range",
               ar="Intra-annual heat-stress amplitude",
               mod="11_Heat_Index", period="Annual", typ="Range", unit="°C",
               src="Derived from seasonal HI means",
               calc="Highest seasonal HI mean minus lowest seasonal HI mean",
               ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_thermal_stress_fields",
               form="HI_{Seasonal\\_Range} = \\max(seasons) - \\min(seasons)",
               note="Seasonal heat-stress amplitude.",
               search="hi seasonal range amplitude")]
    wc = []
    for f, p in [("WC_Spring_Mean", "Spring"), ("WC_Summer_Mean", "Summer"),
                 ("WC_Autumn_Mean", "Autumn")]:
        wc.append(dict(fld=f, en=p + " Mean Wind Chill",
                       ar="Opt-in cold-regions suite",
                       mod="12_Wind_Chill", period=p, typ="Mean", unit="°C",
                       src="Derived from T2M and WS10M (NWS 2001); opt-in",
                       calc="Mean of monthly WC; equals T when T>10C or calm",
                       ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_winter_chill_fields",
                       form="WC_{%s} = mean(monthly\\ WC)" % p,
                       note="Published only with the cold-regions opt-in toggle.",
                       search="wc wind chill %s opt-in" % p.lower()))
    wc += [dict(fld="WC_Annual_Range", en="Annual Wind Chill Range",
                ar="Annual cold-stress amplitude (opt-in)",
                mod="12_Wind_Chill", period="Annual", typ="Range", unit="°C",
                src="Derived from monthly WC (opt-in)",
                calc="Highest monthly WC minus lowest monthly WC",
                ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_winter_chill_fields",
                form="WC_{Annual\\_Range} = \\max(monthly) - \\min(monthly)",
                note="Opt-in only.", search="wc annual range opt-in"),
           dict(fld="WC_Seasonal_Range", en="Seasonal Wind Chill Range",
                ar="Seasonal cold-stress amplitude (opt-in)",
                mod="12_Wind_Chill", period="Annual", typ="Range", unit="°C",
                src="Derived from seasonal WC means (opt-in)",
                calc="Highest seasonal WC mean minus lowest seasonal WC mean",
                ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_winter_chill_fields",
                form="WC_{Seasonal\\_Range} = \\max(seasons) - \\min(seasons)",
                note="Opt-in only.", search="wc seasonal range opt-in")]
    for m in MONTHS_EN:
        f = "WC_%s_Mean" % m
        wc.append(dict(fld=f, en="%s Mean Wind Chill" % m,
                       ar="Monthly chill, opt-in only",
                       mod="12_Wind_Chill", period="Monthly", typ="Mean", unit="°C",
                       src="Derived from T2M and WS10M (NWS 2001); opt-in",
                       calc="Mean of valid %s WC values" % m,
                       ref="Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt: compute_winter_chill_fields",
                       form="WC_{%s} = monthly\\ WC" % m[:3],
                       note="Month/ raster when the monthly option is enabled.",
                       search="wc %s monthly wind chill opt-in" % m.lower()))
    return [("UV_Annual_Range", uv),
            ("HI_Summer_Mean", hi[:2]),
            ("HI_Annual_Range", hi[2:]),
            ("WC_Winter_Mean", wc[:3]),
            ("WC_Annual_Mean", wc[3:5]),
            ("WC_Seasonal_Range", wc[5:])]


AR_MONTH = {e: a for e, a in zip(
    MONTHS_EN,
    [u"يناير", u"فبراير", u"مارس", u"أبريل", u"مايو", u"يونيو",
     u"يوليو", u"أغسطس", u"سبتمبر", u"أكتوبر", u"نوفمبر", u"ديسمبر"])}
AR_SEASON = {"Spring": u"الربيع", "Summer": u"الصيف", "Autumn": u"الخريف",
             "Winter": u"الشتاء", "Annual": u"السنوي", "Monthly": u"الشهري"}


def new_cards_ar():
    en_groups = new_cards_en()
    out = []
    for anchor, cards in en_groups:
        ar_cards = []
        for c in cards:
            c2 = dict(c)
            fld = c["fld"]
            if fld == "UV_Seasonal_Range":
                c2.update(en=u"المدى الفصلي لمؤشر الأشعة فوق البنفسجية",
                          ar=u"السعة الفصلية لذروة UV الظهرية",
                          src=u"تحويل متوسط NASA اليومي إلى ذروة ظهرية WHO",
                          calc=u"أعلى متوسط فصلي ناقص أدناه",
                          note=u"السعة الفصلية للتعرض الظهري؛ بمقياس WHO الثابت.",
                          search=c["search"] + u" المدى الفصلي الأشعة فوق البنفسجية")
            elif fld in ("HI_Spring_Mean", "HI_Autumn_Mean", "HI_Seasonal_Range"):
                season = {"HI_Spring_Mean": u"الربيع", "HI_Autumn_Mean": u"الخريف"}.get(fld, u"الفصلي")
                c2.update(en={"HI_Spring_Mean": u"متوسط مؤشر الحرارة المحسوسة ربيعاً",
                              "HI_Autumn_Mean": u"متوسط مؤشر الحرارة المحسوسة خريفاً",
                              "HI_Seasonal_Range": u"المدى الفصلي لمؤشر الحرارة المحسوسة"}[fld],
                          ar=u"بطريقة روتفوش",
                          src=u"مشتق من الحرارة والرطوبة (روتفوش)",
                          note=u"ضمن مؤشرات الإجهاد الحراري الموسعة.")
            elif fld.startswith("WC_"):
                c2.update(ar=u"ضمن باقة المناطق الباردة الاختيارية",
                          src=u"مشتق من الحرارة والرياح (NWS 2001) — اختياري",
                          note=u"يُنشر فقط عند تفعيل خيار المناطق الباردة.")
                if "_Mean" in fld and fld not in ("WC_Annual_Range", "WC_Seasonal_Range"):
                    for m_en, m_ar in AR_MONTH.items():
                        if fld == "WC_%s_Mean" % m_en:
                            c2["en"] = u"متوسط مبرد الرياح لشهر %s" % m_ar
                    for s_en, s_ar in AR_SEASON.items():
                        if fld == "WC_%s_Mean" % s_en:
                            c2["en"] = u"متوسط مبرد الرياح %s" % (u"شتاءً" if s_en == "Winter" else
                                                                  u"سنوياً" if s_en == "Annual" else s_ar + u"اً")
            ar_cards.append(c2)
        out.append((anchor, ar_cards))
    return out


T_EN = dict(t_fld="Primary FGDB / Raster Name", t_shp="Shapefile 10-Character Name",
            t_en="English Display Name", t_mod="Module & Folder",
            t_per="Temporal Period & Type", t_unit="Measurement Unit",
            t_src="Data Source & Sensor", t_calc="Calculation",
            t_ref="Implementation Reference", t_form="Mathematical Formulation:",
            t_note="Scientific Interpretation:")
T_AR = dict(t_fld=u"اسم الحقل الفعلي (GDB / Raster)",
            t_shp=u"اسم الحقل المختصر في الشيب فايل",
            t_en=u"الاسم الإنجليزي الظاهر المعتمد",
            t_mod=u"الموديول ومجلد الراستر", t_per=u"الفترة الزمنية والنوع",
            t_unit=u"وحدة القياس", t_src=u"مصدر البيانات", t_calc=u"خطوات الحساب",
            t_ref=u"المرجع البرمجي", t_form=u"الصيغة الرياضية:", t_note=u"التفسير العلمي:")

COPY_JS = """
        function copyField(name) {
            function done() { showToast('Copied: ' + name); }
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(name).then(done, function() { fallback(); });
            } else { fallback(); }
            function fallback() {
                var ta = document.createElement('textarea');
                ta.value = name; document.body.appendChild(ta); ta.select();
                try { document.execCommand('copy'); } catch (e) {}
                document.body.removeChild(ta); done();
            }
        }
        function showToast(msg) {
            var t = document.getElementById('toast');
            if (!t) {
                t = document.createElement('div'); t.id = 'toast';
                t.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1B365D;color:#fff;padding:10px 18px;border-radius:6px;z-index:9999;font-size:0.9rem;';
                document.body.appendChild(t);
            }
            t.textContent = msg; t.style.display = 'block';
            setTimeout(function() { t.style.display = 'none'; }, 1600);
        }
"""

TOP_CSS_JS = """
<button id="backTop" onclick="window.scrollTo({top:0,behavior:'smooth'})" style="display:none;position:fixed;bottom:24px;right:24px;z-index:9998;padding:10px 14px;border-radius:50%;border:none;background:var(--primary);color:#fff;cursor:pointer;font-size:1rem;">&#9650;</button>
<script>
window.addEventListener('scroll', function() {
    var b = document.getElementById('backTop');
    if (b) b.style.display = (window.scrollY > 600) ? 'block' : 'none';
});
</script>
"""

WHATSNEW_EN = """
        <section id="whatsnew">
            <h2>What Is New (October 2026)</h2>
            <ul>
                <li><strong>UV Index noon-maximum fix:</strong> NASA POWER 24-hour means are converted per month to WHO solar-noon estimates via astronomical daylength (shape factor 0.435, ~10&ndash;15% uncertainty); new <code>UV_Seasonal_Range</code>; fixed WHO classification in every class sheet.</li>
                <li><strong>Heat Index expansion:</strong> <code>HI_Spring_Mean</code>, <code>HI_Autumn_Mean</code>, <code>HI_Seasonal_Range</code> (Rothfusz).</li>
                <li><strong>Wind Chill cold-regions opt-in (default OFF):</strong> 3 seasonal means, annual/seasonal ranges and 12 monthly means with the <em>Extended_WC_Seasons</em> toggle; default runs stay Winter+Annual.</li>
                <li><strong>Optional Daily sheet:</strong> <em>Save Daily Time Series</em> adds a third workbook sheet for Daily temporal runs (CSV fallback past ~60000 rows).</li>
                <li><strong>Solar units corrected:</strong> kWh/m&sup2;/day everywhere (kWh/m&sup2;/year for the annual total).</li>
            </ul>
        </section>
"""

WHATSNEW_AR = """
        <section id="whatsnew">
            <h2>ما الجديد (أكتوبر 2026)</h2>
            <ul>
                <li><strong>إصلاح ذروة UV الظهرية:</strong> تحويل متوسطات NASA اليومية (24 ساعة) إلى تقدير ذروة الظهر WHO بطول النهار الفلكي (معامل 0.435)؛ حقل <code>UV_Seasonal_Range</code> جديد؛ ومقياس WHO ثابت في كل الشيتات.</li>
                <li><strong>توسعة الحرارة المحسوسة:</strong> <code>HI_Spring_Mean</code> و<code>HI_Autumn_Mean</code> و<code>HI_Seasonal_Range</code> (روتفوش).</li>
                <li><strong>باقة المناطق الباردة الاختيارية (مطفية افتراضياً):</strong> فصول مبرد الرياح ومدييه وشهرياته بتوجل <em>Extended_WC_Seasons</em>؛ والوضع الافتراضي شتاء+سنوي فقط.</li>
                <li><strong>شيت يومي اختياري:</strong> خيار حفظ السلاسل اليومية يضيف شيت <em>Daily</em> ثالثاً (أو CSV عند تجاوز السعة).</li>
                <li><strong>تصحيح وحدات الشمسي:</strong> kWh/m&sup2;/day دائماً (وkWh/m&sup2;/year للإجمالي السنوي).</li>
            </ul>
        </section>
"""


def render(card, T, num):
    c = dict(card)
    c.update(T)
    c["num"] = num
    c["shp"] = SHP[card["fld"]]
    return CARD_TPL.format(**c)


def insert_after(txt, anchor_field, html):
    """Insert html right after the card containing anchor_field's code span."""
    pat = re.compile(r"<code>" + re.escape(anchor_field) + r"</code>")
    m = None
    for mm in pat.finditer(txt):
        m = mm
        break
    if not m:
        raise RuntimeError("anchor not found: " + anchor_field)
    nxt = txt.find('<div class="field-card"', m.end())
    pos = nxt if nxt > 0 else len(txt)
    return txt[:pos] + html + txt[pos:]


def renumber(txt):
    n = [0]

    def _rep(m):
        n[0] += 1
        return "<span>%03d. <code>" % n[0]

    return re.sub(r"<span>\d+\. <code>", _rep, txt), n[0]


def patch(path, lang):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        txt = fh.read()
    T = T_EN if lang == "en" else T_AR
    groups = [(a, [dict(c) for c in cards]) for a, cards in
              (new_cards_en() if lang == "en" else new_cards_ar())]
    # insert in reverse document order is unnecessary; anchors are unique
    if "<code>UV_Seasonal_Range</code>" not in txt:
        for anchor, cards in groups:
            html = "".join(render(c, T, 0) for c in cards)
            txt = insert_after(txt, anchor, html)
    # renumber all cards in document order
    txt, total = renumber(txt)
    # counts
    txt = txt.replace("All 115 Indicators", "All %d Indicators" % total)
    txt = txt.replace("115 \u0645\u0624\u0634\u0631", "%d \u0645\u0624\u0634\u0631" % total)
    txt = re.sub(r"Showing <strong id=\"visibleCount\">115</strong> of 115",
                 "Showing <strong id=\"visibleCount\">%d</strong> of %d" % (total, total), txt)
    txt = re.sub(r'id="visibleCount">115<', 'id="visibleCount">%d<' % total, txt)
    # filter-stats fallback text
    txt = txt.replace(" of 115 Indicators", " of %d Indicators" % total)
    # chrome language purity
    if lang == "en":
        txt = txt.replace("&larr; \u0627\u0644\u0646\u0633\u062e\u0629 \u0627\u0644\u0639\u0631\u0628\u064a\u0629 (Arabic)",
                          "&larr; Arabic Edition")
    else:
        # value-tagged period/type options keep filtering on English values
        for en, ar in [("Annual", u"سنوي"), ("Winter", u"شتاء"), ("Spring", u"ربيع"),
                       ("Summer", u"صيف"), ("Autumn", u"خريف"), ("Monthly", u"شهري"),
                       ("Daily", u"يومي"), ("Static / Runtime", u"ثابت / تشغيلي")]:
            txt = txt.replace("<option>%s</option>" % en,
                              '<option value="%s">%s</option>' % (en, ar))
        for en, ar in [("Mean", u"متوسط"), ("Total", u"مجموع"), ("Range", u"مدى"),
                       ("Extreme / MinMax", u"أقصى"), ("Model / Derived", u"مشتق"),
                       ("Trend / Anomaly", u"اتجاه"), ("System / Metadata", u"نظام")]:
            txt = txt.replace("<option>%s</option>" % en,
                              '<option value="%s">%s</option>' % (en, ar))
        txt = txt.replace("&rarr; English Edition", "&rarr; " + u"النسخة الإنجليزية")
    # interactivity: copy JS + back-to-top (idempotent markers)
    if "function copyField(" not in txt:
        txt = txt.replace("</body>", "<script>" + COPY_JS + "</script>\n</body>")
    if 'id="backTop"' not in txt:
        txt = txt.replace("</body>", TOP_CSS_JS + "\n</body>")
    # what's-new section + sidebar link (idempotent)
    if 'id="whatsnew"' not in txt:
        wn = WHATSNEW_EN if lang == "en" else WHATSNEW_AR
        txt = txt.replace('<section id="catalog">', wn + '\n        <section id="catalog">')
        link = ('<a href="#whatsnew">5. What Is New (Oct 2026)</a>' if lang == "en"
                else '<a href="#whatsnew">5. ' + u'ما الجديد (أكتوبر 2026)' + '</a>')
        txt = txt.replace('<a href="#catalog">', link + "\n            " + '<a href="#catalog">')
        # catalog sidebar link was 5 -> now 6 (targeted at the anchor)
        if lang == "en":
            txt = txt.replace('<a href="#catalog">5. All ', '<a href="#catalog">6. All ')
        else:
            txt = re.sub(r'(<a href="#catalog">)5\. ', r'\g<1>6. ', txt, count=1)
    txt = re.sub(r'>115 Total Fields<', '>%d Total Fields<' % total, txt)
    # AR/other badge: 115 + words inside a badge span
    txt = re.sub(r'(badge badge-blue">)115( [^<]*</span>)', r'\g<1>%d\g<2>' % total, txt)
    if ".btn-copy" not in txt:
        txt = txt.replace("</style>", ".btn-copy{padding:2px 8px;font-size:0.75rem;margin-left:8px;}\n    </style>")
    # copy button on EVERY card sub-name line that lacks one
    def _addbtn(m):
        div = m.group(0)
        if "copyField(" in div:
            return div
        fld = re.search(r"10-char Shapefile: <code>([^<]+)</code>", div)
        name = fld.group(1) if fld else None
        if not name:
            code = re.search(r"<code>([^<]+)</code>", div)
            name = code.group(1) if code else None
        if not name:
            return div
        return div.replace("</div>",
                           ' <button class="btn btn-secondary btn-copy" onclick="event.stopPropagation();copyField(\'%s\')">%s</button></div>'
                           % (name, "Copy" if lang == "en" else u"نسخ"), 1)
    txt = re.sub(r'<div class="sub-name" style="margin-top:2px;">.*?</div>', _addbtn, txt, flags=re.S)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("patched %s cards=%d" % (os.path.basename(path), total))


if __name__ == "__main__":
    patch(os.path.join(DOCS, "Complete_Scientific_Technical_Documentation.html"), "en")
    patch(os.path.join(DOCS, "Complete_Scientific_Technical_Documentation_AR.html"), "ar")
