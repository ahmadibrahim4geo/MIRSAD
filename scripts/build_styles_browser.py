# -*- coding: utf-8 -*-
"""Build docs/Styles_Browser.html from style definitions + .style inventory.

Usage: python3 scripts/build_styles_browser.py
"""
import os
import re
import io

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, "Documents")


def load_defs():
    txt = open(os.path.join(BASE, "utils", "generate_climate_styles.py"),
               encoding="utf-8", errors="ignore").read()
    styles = []
    for m in re.finditer(r"\{\s*\"category\":\s*\"([^\"]+)\"(.*?)\"id\":\s*\"([^\"]+)\"",
                         txt, re.S):
        cat, body, sid = m.group(1), m.group(2), m.group(3)
        nm = re.search(r'"name_en":\s*"([^"]+)"', body)
        na = re.search(r'"name_ar":\s*"([^"]+)"', body)
        src = re.search(r'"source":\s*"([^"]+)"', body)
        tiers = {}
        cm = re.search(r'"classes":\s*\{(.*?)\n\s*\},?\s*\n\s*"name_en"', body, re.S)
        if cm:
            for tm in re.finditer(r'"(\d+)":\s*\[(.*?)\]', cm.group(1), re.S):
                tiers[tm.group(1)] = re.findall(r'"(#[0-9A-Fa-f]{6})"', tm.group(2))
        styles.append(dict(id=sid, cat=cat,
                           en=nm.group(1) if nm else sid,
                           ar=na.group(1) if na else "",
                           src=src.group(1) if src else "", tiers=tiers))
    return styles


def inventory():
    out = []
    for root, _dirs, files in os.walk(os.path.join(BASE, "style")):
        for f in sorted(files):
            if f.endswith(".style"):
                p = os.path.join(root, f)
                out.append((os.path.relpath(p, BASE).replace(os.sep, "/"),
                            os.path.getsize(p)))
    return out


def swatches(hexes):
    return "".join(
        '<span class="sw" style="background:%s" title="%s" onclick="copyHex(\'%s\')"></span>' % (h, h, h)
        for h in hexes)


ELEM_AR = {"Temp": u"الحرارة", "Precip": u"الأمطار", "Wind": u"الرياح",
           "RH": u"الرطوبة", "Solar": u"الشمسي", "Model": u"النماذج",
           "Pres": u"الضغط", "SPres": u"السطحي", "UV": u"فوق البنفسجية",
           "Cloud": u"السحب", "Drought": u"الجفاف", "Aridity": u"القحولة"}


def elem_of(sid):
    return sid.split("_")[0]


ELEM_EN = {"Temp": "Temperature", "Precip": "Precipitation", "Wind": "Wind",
           "RH": "Humidity", "Solar": "Solar", "Model": "Models",
           "Pres": "Pressure", "SPres": "Surface", "UV": "UV Index",
           "Cloud": "Cloud", "Drought": "Drought", "Aridity": "Aridity"}

STR = {
    "ar": dict(lang='ar', dir='rtl', title=u'مستعرض الستايلات | Styles Browser',
               h1=u'مستعرض ستايلات الأطلس المناخي',
               sub=u'__NST__ تعريف لوني &bull; __NFILE__ ملف ستايل &bull; اضغط أي لون لنسخ كوده',
               ph=u'ابحث بالعربية أو الإنجليزية...', allel=u'كل العناصر', allcat=u'كل الفئات',
               tier=u'فئات', files=u'ملفات الستايل في الريبو', th_p=u'المسار', th_s=u'الحجم',
               other=('Styles_Browser_EN.html', 'English Edition'),
               copied=u'تم النسخ: ', elname=ELEM_AR, align='right'),
    "en": dict(lang='en', dir='ltr', title='Styles Browser',
               h1='Climate Atlas Styles Browser',
               sub='__NST__ style definitions &bull; __NFILE__ style files &bull; click any color to copy its code',
               ph='Search in English...', allel='All elements', allcat='All categories',
               tier='classes', files='Style files in the repo', th_p='Path', th_s='Size',
               other=('Styles_Browser.html', u'النسخة العربية'),
               copied='Copied: ', elname=ELEM_EN, align='left'),
}


def build(lang="ar"):
    S = STR[lang]
    styles = load_defs()
    inv = inventory()
    cards = []
    for s in styles:
        el = elem_of(s["id"])
        tiers = "".join(
            "<div class='tier'><b>%s %s:</b> %s</div>" % (k, S["tier"], swatches(v))
            for k, v in sorted(s["tiers"].items(), key=lambda x: int(x[0])))
        meta_el = S["elname"].get(el, el)
        # bilingual search index in BOTH editions (UI chrome stays monolingual)
        search = "%s %s %s %s %s" % (s["id"], s["en"], meta_el,
                                     ELEM_AR.get(el, ""), ELEM_EN.get(el, ""))
        cards.append(
            """<div class="card" data-cat="%(cat)s" data-el="%(el)s" data-search="%(search)s">
            <h3>%(en)s</h3>
            <div class="meta">%(id)s &bull; %(meta_el)s &bull; %(cat)s &bull; %(src)s</div>
            %(tiers)s</div>""" % dict(s, tiers=tiers, el=el, search=search, meta_el=meta_el))
    files = "".join(
        "<tr><td><code>%s</code></td><td>%.1f MB</td></tr>" % (p, sz / 1048576.0)
        for p, sz in inv)
    html = """<!DOCTYPE html>
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
.card h3{margin:0 0 4px;color:var(--primary);font-size:1.05rem}
.meta{color:var(--muted);font-size:0.82rem;margin-bottom:8px}
.tier{margin:6px 0;font-size:0.85rem}
.sw{display:inline-block;width:34px;height:22px;border-radius:4px;margin:2px;border:1px solid #94A3B8;cursor:pointer;vertical-align:middle}
table{width:100%;border-collapse:collapse;background:#fff;font-size:0.85rem}
th,td{border:1px solid var(--border);padding:6px 10px;text-align:__ALIGN__}
th{background:#F8FAFC}
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
<select id="el" onchange="applyFilter()"><option value="">__ALLEL__</option>__ELEMS__</select>
<select id="cat" onchange="applyFilter()"><option value="">__ALLCAT__</option>__CATS__</select>
</div>
<div id="cards">
__CARDS__
</div>
<h2>__FILES__</h2>
<table><thead><tr><th>__TH_P__</th><th>__TH_S__</th></tr></thead><tbody>__FILES_ROWS__</tbody></table>
</div>
<div id="toast"></div>
<button id="backTop" onclick="window.scrollTo({top:0,behavior:'smooth'})">&#9650;</button>
<script>
function applyFilter(){
  var q=document.getElementById('q').value.toLowerCase();
  var c=document.getElementById('cat').value;
  var e=document.getElementById('el').value;
  var n=0, total=0;
  document.querySelectorAll('#cards .card').forEach(function(el){
    total++;
    var ok=(el.getAttribute('data-search')||'').toLowerCase().includes(q);
    if(c) ok = ok && el.getAttribute('data-cat')===c;
    if(e) ok = ok && el.getAttribute('data-el')===e;
    el.style.display = ok?'block':'none';
    if(ok) n++;
  });
  document.getElementById('count').innerText = n + ' / ' + total;
}
document.addEventListener('DOMContentLoaded', applyFilter);
function copyHex(h){
  function done(){var t=document.getElementById('toast');t.textContent='__COPIED__'+h;t.style.display='block';setTimeout(function(){t.style.display='none'},1400);}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(h).then(done,done);}else{done();}
}
window.addEventListener('scroll',function(){var b=document.getElementById('backTop');if(b)b.style.display=(window.scrollY>600)?'block':'none';});
</script>
</body>
</html>"""
    cats = sorted(set(s["cat"] for s in styles))
    elems = sorted(set(elem_of(s["id"]) for s in styles))
    for k in ["LANG__", "DIR__", "TITLE__", "H1__", "SUB__", "PH__", "ALLEL__",
              "ALLCAT__", "FILES__", "TH_P__", "TH_S__", "COPIED__", "ALIGN__"]:
        html = html.replace("__" + k, S[k.lower().rstrip("_")] if k.lower().rstrip("_") in S else "")
    html = html.replace("__OTHER_FILE__", S["other"][0]).replace("__OTHER_LABEL__", S["other"][1])
    html = html.replace("__NST__", str(len(styles))).replace("__NFILE__", str(len(inv)))
    html = html.replace("__CATS__", "".join('<option value="%s">%s</option>' % (c, c) for c in cats))
    html = html.replace("__ELEMS__", "".join(
        '<option value="%s">%s</option>' % (e, S["elname"].get(e, e)) for e in elems))
    html = html.replace('<div id="cards">', '<p id="count"></p><div id="cards">')
    html = html.replace("__CARDS__", "\n".join(cards)).replace("__FILES_ROWS__", files)
    out = os.path.join(DOCS, "Styles_Browser.html" if lang == "ar" else "Styles_Browser_EN.html")
    io.open(out, "w", encoding="utf-8").write(html)
    print("built %s styles=%d files=%d" % (out, len(styles), len(inv)))


if __name__ == "__main__":
    build("ar")
    build("en")
