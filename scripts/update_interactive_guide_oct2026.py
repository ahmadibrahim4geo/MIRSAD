# -*- coding: utf-8 -*-
"""October 2026 Interactive_Guide overhaul v2 (re-runnable, idempotent).

- 18 module cards (was 10), database regenerated from FIELD_DEFS (287 rows)
- Live calculators: aridity (existing) + Heat Index + UV noon + Wind Chill
- Pure-Arabic UI (Latin kept only for codes/symbols/units)
- switchTab fixed (explicit element), developer credits card
Usage: python3 scripts/update_interactive_guide_oct2026.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE, "Documents", "Interactive_Guide.html")
if not os.path.exists(PATH):
    PATH = os.path.join(BASE, "Documents", "04_Interactive_HTML_Guides", "Interactive_Guide.html")

AR_MOD = {"Temperature": u"الحرارة", "Precipitation": u"الأمطار",
          "Sea Level Pressure": u"ضغط مستوى البحر", "Surface Pressure": u"الضغط السطحي",
          "Wind": u"الرياح", "Relative Humidity": u"الرطوبة النسبية",
          "Dew Point": u"نقطة الندى", "Solar Radiation": u"الإشعاع الشمسي",
          "UV Index": u"الأشعة فوق البنفسجية", "Cloud Cover": u"الغطاء السحابي",
          "Heat Index": u"الحرارة المحسوسة", "Wind Chill": u"مبرد الرياح",
          "De Martonne Aridity": u"القحولة (دي مارتون)",
          "Evapotranspiration": u"البخر-نتح", "Hargreaves PET": u"البخر-نتح (هارجريفز)",
          "UNEP Aridity": u"القحولة (الأمم المتحدة)",
          "Water Deficit": u"العجز المائي", "Dry Months": u"الأشهر الجافة",
          "Trends & Anomalies": u"الاتجاهات والشذوذ",
          "Trends and Anomalies": u"الاتجاهات والشذوذ",
          "Climate_Models": u"النماذج المناخية",
          "Drought & Aridity": u"الجفاف والقحولة"}

MOD_CARD = [
    ("Temperature", u"🌡️ الحرارة", u"المتوسطات الشهرية والفصلية والسنوية، المدى الحراري، العظمى والصغرى."),
    ("Precipitation", u"🌧️ الأمطار", u"المجاميع السنوية والفصلية والمديات والمعدلات الشهرية."),
    ("Sea Level Pressure", u"🧭 ضغط مستوى البحر", u"المتوسطات السنوية والفصلية مع إمكانية خطوط الأيزوبار."),
    ("Surface Pressure", u"🧭 الضغط السطحي", u"الضغط الفعلي عند منسوب المحطة."),
    ("Wind", u"💨 الرياح", u"السرعة والاتجاه بالمتوسط الدائري الاتجاهي."),
    ("Relative Humidity", u"💧 الرطوبة النسبية", u"المتوسطات الشهرية والفصلية والسنوية."),
    ("Dew Point", u"🌫️ نقطة الندى", u"درجة التكثف الشهرية والفصلية والسنوية."),
    ("Solar Radiation", u"☀️ الإشعاع الشمسي", u"المعدل اليومي والإجمالي السنوي (كيلوواط ساعة/م²)."),
    ("UV Index", u"🕶️ الأشعة فوق البنفسجية", u"ذروة الظهيرة بمقياس منظمة الصحة العالمية الثابت."),
    ("Cloud Cover", u"☁️ الغطاء السحابي", u"نسب التغطية الشهرية والفصلية والسنوية."),
    ("Heat Index", u"🌡️ الحرارة المحسوسة", u"روتفوش صيفاً وربيعاً وخريفاً وهيوميدكس شتاءً + المدى الفصلي."),
    ("Wind Chill", u"❄️ مبرد الرياح", u"شتاءً وسنوياً افتراضياً، وباقة كاملة للمناطق الباردة اختيارياً."),
    ("De Martonne Aridity", u"🌵 القحولة (دي مارتون)", u"دليل الجفاف السنوي."),
    ("Evapotranspiration", u"🌱 البخر-نتح", u"هارجريفز-ساماني الشهري والفصلي والسنوي."),
    ("UNEP Aridity", u"🌍 القحولة (الأمم المتحدة)", u"مؤشر الجفاف العالمي (الأمطار ÷ البخر-نتح)."),
    ("Water Deficit", u"💧 العجز المائي", u"الموازنة المناخية (الأمطار − البخر-نتح)."),
    ("Dry Months", u"📅 الأشهر الجافة", u"عدد الأشهر الجافة بيولوجياً."),
    ("Trends & Anomalies", u"📈 الاتجاهات والشذوذ", u"اتجاهات العقود وشذوذ خط الأساس."),
]

CALC_CARDS = """
                <div class="card">
                    <h3>🌡️ حاسبة الحرارة المحسوسة (روتفوش)</h3>
                    <div class="input-group"><label>الحرارة (°م)</label><input type="number" id="inp_hit" value="38" oninput="recalcHI()"></div>
                    <div class="input-group"><label>الرطوبة (%)</label><input type="number" id="inp_hirh" value="45" oninput="recalcHI()"></div>
                    <p>المؤشر: <strong id="res_hi">-</strong> °م <span id="tag_hi" class="badge badge-orange"></span></p>
                </div>
                <div class="card">
                    <h3>🕶️ مقدر ذروة الأشعة فوق البنفسجية</h3>
                    <div class="input-group"><label>المتوسط اليومي (من ناسا)</label><input type="number" step="0.01" id="inp_uvm" value="2.66" oninput="recalcUV()"></div>
                    <div class="input-group"><label>خط العرض</label><input type="number" id="inp_uvlat" value="30" oninput="recalcUV()"></div>
                    <div class="input-group"><label>الشهر (1-12)</label><input type="number" id="inp_uvmo" value="7" oninput="recalcUV()"></div>
                    <p>ذروة الظهر التقديرية: <strong id="res_uv">-</strong> <span id="tag_uv" class="badge badge-orange"></span></p>
                </div>
                <div class="card">
                    <h3>❄️ حاسبة مبرد الرياح</h3>
                    <div class="input-group"><label>الحرارة (°م)</label><input type="number" id="inp_wct" value="5" oninput="recalcWC()"></div>
                    <div class="input-group"><label>سرعة الرياح (م/ث)</label><input type="number" id="inp_wcv" value="5" oninput="recalcWC()"></div>
                    <p>الإحساس الفعلي: <strong id="res_wc">-</strong> °م <span id="tag_wc" class="badge badge-orange"></span></p>
                </div>
"""

CALC_JS = """
    // Heat Index (Rothfusz, NWS)
    function recalcHI() {
        var t = parseFloat(document.getElementById('inp_hit').value) || 0;
        var rh = Math.min(100, Math.max(0, parseFloat(document.getElementById('inp_hirh').value) || 0));
        var tf = t * 9 / 5 + 32, hi;
        if (tf < 80) { hi = t; }
        else {
            hi = -42.379 + 2.04901523 * tf + 10.14333127 * rh - 0.22475541 * tf * rh
                - 0.00683783 * tf * tf - 0.05481717 * rh * rh + 0.00122874 * tf * tf * rh
                + 0.00085282 * tf * rh * rh - 0.00000199 * tf * tf * rh * rh;
            hi = (hi - 32) * 5 / 9;
        }
        document.getElementById('res_hi').innerText = hi.toFixed(1);
        var tag = 'مريح';
        if (hi >= 54) tag = 'خطر شديد';
        else if (hi >= 41) tag = 'خطر';
        else if (hi >= 32) tag = 'حذر شديد';
        else if (hi >= 27) tag = 'حذر';
        document.getElementById('tag_hi').innerText = tag;
    }
    // UV noon-max estimator (daylength-based, k=0.435)
    function recalcUV() {
        var m24 = parseFloat(document.getElementById('inp_uvm').value) || 0;
        var lat = parseFloat(document.getElementById('inp_uvlat').value) || 30;
        var mo = Math.min(12, Math.max(1, parseInt(document.getElementById('inp_uvmo').value) || 7));
        var doy = [15, 45, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349][mo - 1];
        var decl = -23.44 * Math.cos(2 * Math.PI * (doy + 10) / 365) * Math.PI / 180;
        var la = lat * Math.PI / 180;
        var c = -Math.tan(la) * Math.tan(decl);
        var dl = (c <= -1) ? 24 : (c >= 1 ? 0 : 2 * Math.acos(c) * 180 / Math.PI / 15);
        var noon = (dl < 0.5 || m24 <= 0) ? 0 : m24 * 24 / (dl * 0.435);
        document.getElementById('res_uv').innerText = noon.toFixed(1);
        var tag = 'منخفض';
        if (noon >= 11) tag = 'متطرف';
        else if (noon >= 8) tag = 'عال جدا';
        else if (noon >= 6) tag = 'عال';
        else if (noon >= 3) tag = 'معتدل';
        document.getElementById('tag_uv').innerText = tag;
    }
    // Wind Chill (NWS 2001)
    function recalcWC() {
        var t = parseFloat(document.getElementById('inp_wct').value) || 0;
        var v = Math.max(0, parseFloat(document.getElementById('inp_wcv').value) || 0) * 3.6;
        var wc = t;
        if (t <= 10 && v >= 4.8) {
            var p = Math.pow(v, 0.16);
            wc = 13.12 + 0.6215 * t - 11.37 * p + 0.3965 * t * p;
        }
        document.getElementById('res_wc').innerText = wc.toFixed(1);
        var tag = (t <= 10 && v >= 4.8) ? 'تبريد فعلي بالرياح' : 'يساوي حرارة الهواء';
        document.getElementById('tag_wc').innerText = tag;
    }
"""

DEV_CARD = """
                <div class="card" style="border:2px solid var(--primary-light);">
                    <h3>المطور</h3>
                    <p><strong>أحمد إبراهيم (Ahmad Ibrahim)</strong> — باحث ومطور أطلس المناخ (NASA POWER & Open-Meteo).</p>
                    <p>GitHub: <strong>@ahmadibrahim4geo</strong> &bull; البريد: <strong>ahmadibrahim.geo@gmail.com</strong></p>
                </div>
"""


def div_end(txt, open_idx):
    depth = 0
    for m in re.finditer(r"</?div\b[^>]*>", txt[open_idx:]):
        if m.group(0).startswith("</"):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            return open_idx + m.end()
    raise RuntimeError("unbalanced divs")


def tab_inner(txt, tab_id):
    o = txt.find('id="%s"' % tab_id)
    if o < 0:
        raise RuntimeError("tab missing: " + tab_id)
    d = txt.rfind("<div", 0, o)
    end = div_end(txt, d)
    return txt.find(">", o) + 1, end - len("</div>"), d, end


def build_fields_js():
    import re as _re
    pyt_file = os.path.join(BASE, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
    if not os.path.exists(pyt_file):
        pyt_file = os.path.join(BASE, "POWER_Climate_Atlas_Generator_10_8.pyt")
    txt = open(pyt_file,
               encoding="utf-8", errors="ignore").read()
    m = _re.search(r"FIELD_DEFS = \[(.*?)\n\]", txt, re.S)
    rows = []
    for mm in _re.finditer(
            r'\(\s*"([^"]+)",\s*"([^"]+)",\s*u?"([^"]*)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"',
            m.group(1)):
        fname, _en, ar, _raw, mod, per, _stat, unit = mm.groups()
        rows.append((fname, ar, mod, per, unit))
    js = "    const fieldsData = [\n"
    for fname, ar, mod, per, unit in rows:
        ar = ar.replace("\\", "\\\\").replace('"', '\\"')
        js += '        { f: "%s", ar: "%s", mod: "%s", per: "%s", u: "%s", desc: "" },\n' % (
            fname, ar, AR_MOD.get(mod, mod), per, unit)
    js += "    ];"
    return js, len(rows)


def patch():
    with open(PATH, encoding="utf-8", errors="ignore") as fh:
        txt = fh.read()

    js, n = build_fields_js()
    # 1. counts
    txt = txt.replace(u"العناصر المناخية الـ 10", u"العناصر المناخية الـ 18")
    txt = txt.replace(u"المؤشرات الـ 82", u"المؤشرات الـ %d" % n)
    txt = txt.replace(u"قاعدة المؤشرات الـ 82 الكاملة", u"قاعدة المؤشرات الـ %d الكاملة" % n)

    # 2. elements tab grid -> 18 cards
    s, e, _d, _end = tab_inner(txt, "tab-elements")
    seg = txt[s:e]
    g = seg.find('<div class="grid-2">')
    if g < 0:
        raise RuntimeError("grid-2 missing in elements tab")
    grids = seg.find(">", g) + 1
    cards = []
    for _mod, title, desc in MOD_CARD:
        cards.append('                <div class="card">\n                    <h3>%s</h3>\n                    <p>%s</p>\n                </div>' % (title, desc))
    seg2 = seg[:grids] + "\n" + "\n".join(cards) + "\n                "
    txt = txt[:s] + seg2 + txt[e:]

    # 3. database array
    txt = re.sub(r"const fieldsData = \[.*?\];", lambda m: js, txt, flags=re.S, count=1)

    # 4. calculator cards + JS (idempotent)
    if "inp_hit" not in txt:
        s, e, _d, _end = tab_inner(txt, "tab-calculator")
        txt = txt[:e] + CALC_CARDS + txt[e:]
    if "function recalcHI(" not in txt:
        txt = txt.replace("</script>", CALC_JS + "\n</script>", 1)

    # 5. pure-Arabic result tags
    for en_tag in ["Hyper-arid", "Arid", "Semi-arid", "Sub-humid", "Humid", "Dry sub-humid"]:
        txt = txt.replace("(%s)" % en_tag, "")

    # 6. switchTab robustness (idempotent)
    for t in ["modes", "wmo", "calculator", "elements", "database"]:
        txt = txt.replace("switchTab('%s')" % t, "switchTab(this,'%s')" % t)
    if "function switchTab(ev," not in txt:
        txt = txt.replace(
            "function switchTab(tabId) {",
            "function switchTab(ev, tabId) {\n"
            "        var el = (ev && ev.classList) ? ev : ((ev && ev.currentTarget) ? ev.currentTarget : null);")
        txt = txt.replace("event.target.classList.add('active');",
                          "if (el) el.classList.add('active');")

    # 7. developer card at end of modes tab (idempotent)
    if "ahmadibrahim.geo@gmail.com" not in txt:
        s, e, _d, _end = tab_inner(txt, "tab-modes")
        txt = txt[:e] + DEV_CARD + txt[e:]

    with open(PATH, "w", encoding="utf-8") as fh:
        fh.write(txt)
    print("interactive guide patched, fields:", n)


if __name__ == "__main__":
    patch()
