# -*- coding: utf-8 -*-
"""Generate interactive tool-docs HTML (AR+EN) from the toolbox code itself.

Outputs:
  docs/Parameters_Guide.html / Parameters_Guide_EN.html   (all GP parameters)
  docs/Modules_Dependency_Map.html / _EN.html             (module dependency map)
Usage: python3 scripts/build_tool_docs.py
"""
import os
import re
import io

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "Documents")

AR_CAT = {"Variable & Field Selection": u"اختيار المتغيرات والحقول",
          "Measurement Units & Standards": u"وحدات القياس والمعايير",
          "Output Options": u"خيارات المخرجات",
          "Time Window": u"النافذة الزمنية"}

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
          "Trends & Anomalies": u"الاتجاهات والشذوذ"}


def parse_params(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r"def getParameterInfo\(self\):(.*?)\n        return \[",
                  txt, re.S)
    body = m.group(1)
    params = []
    starts = [m for m in re.finditer(r"(\w+)\s*=\s*arcpy\.Parameter\(", body)]
    for si, _pm in enumerate(starts):
        var = _pm.group(1)
        seg = body[_pm.end():starts[si + 1].start() if si + 1 < len(starts) else len(body)]
        lines = seg.split("\n")
        depth = 1
        kept = []
        for ln in lines:
            depth += ln.count("(") - ln.count(")")
            kept.append(ln)
            if depth <= 0:
                break
        args = "\n".join(kept)
        g = lambda k: (re.search(r'%s="(.*?)"' % k, args).group(1)
                             if re.search(r'%s="' % k, args) else "")
        try:
            disp, name, dt = g("displayName"), g("name"), g("datatype")
        except Exception:
            continue
        tail = body[_pm.end():_pm.end() + 4000]
        f = {}
        f["var"], f["disp"], f["name"], f["dt"] = var, disp, name, dt
        mv = re.search(r"%s\.multiValue\s*=\s*True" % re.escape(var), tail)
        f["multi"] = bool(mv)
        vl = re.search(r"%s\.filter\.list\s*=\s*\[(.*?)\]" % re.escape(var), tail, re.S)
        if vl:
            f["values"] = re.findall(r'"((?:[^"\\]|\\.)*)"', vl.group(1))[:14]
        else:
            f["values"] = []
        vv = re.search(r"%s\.value\s*=\s*(.+)" % re.escape(var), tail)
        f["default"] = (vv.group(1).strip()[:90] if vv else "")
        vc = re.search(r"%s\.category\s*=\s*\"(.*?)\"" % re.escape(var), tail)
        f["cat"] = vc.group(1) if vc else ""
        dm = re.search(r"%s\.description\s*=\s*\((.*?)\)" % re.escape(var), tail, re.S)
        if dm:
            desc = " ".join(re.findall(r'"((?:[^"\\]|\\.)*)"', dm.group(1)))
        else:
            dm2 = re.search(r"%s\.description\s*=\s*\"(.*?)\"" % re.escape(var), tail)
            desc = dm2.group(1) if dm2 else ""
        f["desc"] = desc.strip()[:900]
        params.append(f)
    # drop empties (regex misses)
    return [p for p in params if p["name"]]


PAGE = """<!DOCTYPE html>
<html lang="__LANG__" dir="__DIR__">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
:root{--primary:#1B365D;--bg:#F1F5F9;--card:#fff;--border:#CBD5E1;--muted:#64748B}
*{box-sizing:border-box}body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:var(--bg);margin:0;color:#0F172A}
header{background:linear-gradient(135deg,#1B365D,#2A528A);color:#fff;padding:26px}
header a{color:#FBD38D;font-weight:bold}
.wrap{max-width:1200px;margin:0 auto;padding:20px}
.toolbar{display:flex;gap:10px;margin:16px 0;flex-wrap:wrap}
.toolbar input,.toolbar select{padding:10px 14px;border:2px solid var(--border);border-radius:8px;font-size:1rem}
.card{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:12px}
.card h3{margin:0 0 4px;color:var(--primary);font-size:1.02rem}
.meta{color:var(--muted);font-size:0.82rem;margin-bottom:8px}
.desc{font-size:0.9rem;white-space:pre-wrap}
.vals{font-size:0.82rem;color:#334155;margin-top:6px}
code{background:#F1F5F9;padding:1px 6px;border-radius:4px}
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#1B365D;color:#fff;padding:10px 18px;border-radius:6px;display:none;z-index:9999}
#backTop{display:none;position:fixed;bottom:24px;right:24px;z-index:9998;padding:10px 14px;border-radius:50%;border:none;background:var(--primary);color:#fff;cursor:pointer}
</style>
</head>
<body>
<header><div class="wrap">
<h1>__H1__</h1>
<p>__SUB__</p>
<p><a href="__OTHER_FILE__">__OTHER_LABEL__</a></p>
</div></header>
<div class="wrap">
<div class="toolbar">
<input id="q" placeholder="__PH__" onkeyup="applyFilter()" style="flex:1">
<select id="cat" onchange="applyFilter()"><option value="">__ALLCAT__</option>__CATS__</select>
</div>
<p id="count"></p>
<div id="cards">__CARDS__</div>
</div>
<div id="toast"></div>
<button id="backTop" onclick="window.scrollTo({top:0,behavior:'smooth'})">&#9650;</button>
<script>
function applyFilter(){
  var q=document.getElementById('q').value.toLowerCase();
  var ce=document.getElementById('cat'); var c=ce?ce.value:'';
  var n=0,total=0;
  document.querySelectorAll('#cards .card').forEach(function(el){
    total++;
    var ok=(el.getAttribute('data-search')||'').toLowerCase().includes(q);
    if(c) ok=ok&&el.getAttribute('data-cat')===c;
    el.style.display=ok?'block':'none';
    if(ok)n++;
  });
  document.getElementById('count').innerText=n+' / '+total;
}
document.addEventListener('DOMContentLoaded',applyFilter);
window.addEventListener('scroll',function(){var b=document.getElementById('backTop');if(b)b.style.display=(window.scrollY>600)?'block':'none';});
</script>
</body>
</html>"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_params(lang, other):
    import sys
    sys.path.insert(0, BASE)
    src = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")
    if not os.path.exists(src):
        src = os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")
    params = parse_params(src)
    cards = []
    for p in params:
        cat = p["cat"]
        if lang == "ar":
            catl = AR_CAT.get(cat, cat)
            search = "%s %s %s %s" % (p["disp"], p["name"], p["dt"], cat)
        else:
            catl = cat
            search = "%s %s %s %s" % (p["disp"], p["name"], p["dt"], cat)
        vals = ("<div class='vals'>Values: %s</div>" % ", ".join("<code>%s</code>" % esc(v) for v in p["values"])) if p["values"] else ""
        dflt = ("<div class='vals'>Default: <code>%s</code></div>" % esc(p["default"])) if p["default"] else ""
        multi = " <b>(multi-value)</b>" if p["multi"] else ""
        cards.append(
            """<div class="card" data-cat="%s" data-search="%s">
            <h3>%s%s</h3>
            <div class="meta"><code>%s</code> &bull; %s &bull; %s</div>
            <div class="desc">%s</div>%s%s</div>""" % (
                esc(cat), esc(search), esc(p["disp"]), multi, esc(p["name"]),
                esc(p["dt"]), esc(catl), esc(p["desc"]), vals, dflt))
    cats = sorted(set(p["cat"] for p in params))
    S = dict(LANG__=lang, DIR__=("rtl" if lang == "ar" else "ltr"),
             TITLE__=("دليل براميترات الأداة" if lang == "ar" else "Tool Parameters Guide"),
             H1__=("دليل براميترات أداة الأطلس المناخي" if lang == "ar" else "Climate Atlas Tool Parameters Guide"),
             SUB__=(u"%d براميتر — مولد تلقائياً من كود الأداة" % len(params) if lang == "ar"
                    else "%d parameters — auto-generated from the toolbox code" % len(params)),
             PH__=(u"ابحث باسم البراميتر..." if lang == "ar" else "Search parameters..."),
             ALLCAT__=(u"كل الفئات" if lang == "ar" else "All categories"))
    html = PAGE
    for k, v in S.items():
        html = html.replace("__" + k, v)
    html = html.replace("__OTHER_FILE__", other[0]).replace("__OTHER_LABEL__", other[1])
    html = html.replace("__CATS__", "".join('<option value="%s">%s</option>' % (c, (AR_CAT.get(c, c) if lang == "ar" else c)) for c in cats))
    html = html.replace("__CARDS__", "\n".join(cards))
    return html, len(params)


AR_MOD = {"Temperature": u"الحرارة", "Precipitation": u"الأمطار",
          "Sea Level Pressure": u"ضغط مستوى البحر",
          "Surface Pressure": u"الضغط السطحي", "Wind": u"الرياح",
          "Relative Humidity": u"الرطوبة النسبية", "Dew Point": u"نقطة الندى",
          "Solar Radiation": u"الإشعاع الشمسي", "UV Index": u"الأشعة فوق البنفسجية",
          "Cloud Cover": u"الغطاء السحابي", "Heat Index": u"الحرارة المحسوسة",
          "Wind Chill": u"مبرد الرياح",
          "De Martonne Aridity": u"القحولة (دي مارتون)",
          "Evapotranspiration": u"البخر-نتح",
          "Hargreaves PET": u"البخر-نتح (هارجريفز)",
          "UNEP Aridity": u"القحولة (الأمم المتحدة)",
          "Water Deficit": u"العجز المائي", "Dry Months": u"الأشهر الجافة",
          "Trends & Anomalies": u"الاتجاهات والشذوذ"}


def build_deps(lang, other):
    import sys
    sys.path.insert(0, BASE)
    pyt_file = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")
    if not os.path.exists(pyt_file):
        pyt_file = os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")
    txt = open(pyt_file,
               encoding="utf-8", errors="ignore").read()
    ns = {}
    m = re.search(r"MODULE_PARAMS = \{(.*?)\n\}", txt, re.S)
    mp = eval("{" + m.group(1) + "}")
    order = ["Temperature", "Precipitation", "Sea Level Pressure",
             "Surface Pressure", "Wind", "Relative Humidity", "Dew Point",
             "Solar Radiation", "UV Index", "Cloud Cover", "Heat Index",
             "Wind Chill", "De Martonne Aridity", "Evapotranspiration",
             "UNEP Aridity", "Water Deficit", "Dry Months", "Trends & Anomalies"]
    # dependents: module -> [modules needing it]
    prereq = {"Heat Index": ["Temperature", "Relative Humidity"],
              "Wind Chill": ["Temperature", "Wind"],
              "De Martonne Aridity": ["Temperature", "Precipitation"],
              "Evapotranspiration": ["Temperature"],
              "Hargreaves PET": ["Temperature"],
              "UNEP Aridity": ["Temperature", "Precipitation"],
              "Water Deficit": ["Temperature", "Precipitation"],
              "Dry Months": ["Temperature", "Precipitation"],
              "Trends & Anomalies": ["Temperature", "Precipitation"]}
    cards = []
    for mod in order:
        req = prereq.get(mod, [])
        deps = [d for d, rr in prereq.items() if mod in rr]
        if lang == "ar":
            title, reqt = AR_MOD.get(mod, mod), [AR_MOD.get(r, r) for r in req]
            dept = [AR_MOD.get(d, d) for d in deps]
            need_s = (u"يحتاج: " + "، ".join(reqt)) if reqt else u"لا يحتاج موديولات (بيانات أولية)"
            feed_s = (u"يغذي: " + "، ".join(dept)) if dept else u"نهائي (لا يغذي غيره)"
        else:
            title, reqt, dept = mod, req, deps
            need_s = ("Requires: " + ", ".join(reqt)) if reqt else "No prerequisites (raw data)"
            feed_s = ("Feeds: " + ", ".join(dept)) if dept else "Terminal (feeds nothing)"
        cards.append(
            """<div class="card" data-mod="%(mod)s" data-search="%(mod)s %(title)s" data-req="%(req)s" data-dep="%(dep)s" onclick="hi(this)">
            <h3>%(title)s</h3>
            <div class="meta"><code>%(params)s</code></div>
            <div class="desc">%(need)s<br>%(feed)s</div></div>""" % {
                "mod": mod, "title": title, "req": "|".join(req),
                "dep": "|".join(deps),
                "params": ", ".join(mp.get(mod, [])),
                "need": need_s, "feed": feed_s})
    S = dict(LANG__=lang, DIR__=("rtl" if lang == "ar" else "ltr"),
             TITLE__=(u"خريطة اعتمادية الموديولات" if lang == "ar" else "Module Dependency Map"),
             H1__=(u"خريطة اعتمادية موديولات الأطلس" if lang == "ar" else "Atlas Module Dependency Map"),
             SUB__=(u"%d موديول — اضغط أي بطاقة لإبراز علاقاتها" % len(order) if lang == "ar"
                    else "%d modules — click any card to highlight its relations" % len(order)),
             PH__=(u"ابحث باسم الموديول..." if lang == "ar" else "Search modules..."),
             ALLCAT__=(u"الكل" if lang == "ar" else "All"))
    html = PAGE
    for k, v in S.items():
        html = html.replace("__" + k, v)
    html = html.replace("__OTHER_FILE__", other[0]).replace("__OTHER_LABEL__", other[1])
    html = html.replace("__CATS__", "")
    html = html.replace("__CARDS__", "\n".join(cards))
    html = html.replace("__ELEMS__", "")
    html = html.replace('<select id="cat" onchange="applyFilter()"><option value="">%s</option></select>' % S["ALLCAT__"],
                        "")
    html += """
<script>
function hi(el){
  document.querySelectorAll('#cards .card').forEach(function(c){c.style.opacity='0.35';c.style.border='';});
  el.style.opacity='1';el.style.border='2px solid #1B365D';
  function mark(list,color){
    (list||'').split('|').forEach(function(m){
      if(!m)return;
      document.querySelectorAll('#cards .card').forEach(function(c){
        var s=c.getAttribute('data-search')||'';
        if(c.getAttribute('data-mod')===m){c.style.opacity='1';c.style.border='2px solid '+color;}
      });
    });
  }
  mark(el.getAttribute('data-req'),'#059669');
  mark(el.getAttribute('data-dep'),'#D97706');
}
</script>"""
    # reuse PAGE toolbar pieces (strip unused category select already handled)
    html_dir = os.path.join(DOCS, "04_Interactive_HTML_Guides")
    os.makedirs(html_dir, exist_ok=True)
    fname = "Modules_Dependency_Map.html" if lang == "ar" else "Modules_Dependency_Map_EN.html"
    out = os.path.join(html_dir, fname)
    io.open(out, "w", encoding="utf-8").write(html)
    print("built %s modules=%d" % (out, len(order)))


if __name__ == "__main__":
    html_dir = os.path.join(DOCS, "04_Interactive_HTML_Guides")
    os.makedirs(html_dir, exist_ok=True)
    ar, n = build_params("ar", ("Parameters_Guide_EN.html", "English Edition"))
    io.open(os.path.join(html_dir, "Parameters_Guide.html"), "w", encoding="utf-8").write(ar)
    en, _n = build_params("en", ("Parameters_Guide.html", u"النسخة العربية"))
    io.open(os.path.join(html_dir, "Parameters_Guide_EN.html"), "w", encoding="utf-8").write(en)
    print("parameters guide built:", n)
    build_deps("ar", ("Modules_Dependency_Map_EN.html", "English Edition"))
    build_deps("en", ("Modules_Dependency_Map.html", u"النسخة العربية"))
