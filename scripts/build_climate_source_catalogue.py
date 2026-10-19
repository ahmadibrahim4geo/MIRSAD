"""Generate the reviewed source directory, offline catalogue and bilingual web page.

Development-time operation only; Desktop embeds the resulting snapshot.
"""
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mirsad_core.climate_products import PRODUCTS,REGIONAL,GHCN
from mirsad_core.hybrid_pipeline import OM_DAILY,OM_HOURLY

UNITS={"T2M":"deg C","T2M_MAX":"deg C","T2M_MIN":"deg C","T2MDEW":"deg C","TS":"deg C",
       "PRECTOTCORR":"mm per day or native month total","RH2M":"percent","CLOUD_AMT":"percent",
       "PS":"kPa","SLP":"kPa","WS10M":"m/s","WD10M":"degree","ALLSKY_SFC_SW_DWN":"MJ/m2/day","ALLSKY_SFC_UV_INDEX":"source UV index"}
NOTES={
"chirps3":("أمطار شهرية نهائية؛ لم يُنفذ تنزيل CHIRPS اليومي. الصفر صحيح والمفقود NULL.","Final monthly rainfall only; daily CHIRPS ingestion is not implemented. Zero is valid; missing stays NULL."),
"terraclimate11":("الإصدار 1.1 مستقل عن 1.0. قراءة CF scale/offset من كل متغير. متوسط الحرارة مشتق من (العظمى+الصغرى)/2. المطر مجموع شهري.","v1.1 is separate from v1.0. CF scale/offset are read per variable. Mean temperature is (tmax+tmin)/2. Rainfall is a monthly total."),
"chelsa21":("تُقرأ الوحدات والتحويل من الملف نفسه؛ مدى التواريخ يختلف حسب المتغير. الإشعاع الشمسي مستبعد حتى حل تعارض بيانات وحدته. الملف غير المتاح يبقى NULL.","Units/scaling are validated from each file; dates vary by variable. Solar radiation is excluded pending conflicting unit metadata. Unavailable files stay NULL."),
"mod11a2_day":("حرارة سطح نهارية، وليست حرارة هواء. تجميع شهري موزون بأيام السماء الصافية المقبولة بالجودة. لا أيام رصد مصطنعة ولا فرق سطح/هواء دون حرارة هواء.","Daytime surface temperature, not air temperature. Monthly estimates weight quality-accepted clear-sky days. No synthetic daily observations or surface-air differences without air data."),
"mod11a2_night":("حرارة سطح ليلية منفصلة عن النهارية، بنفس فحص الجودة والسحب. نسبة التغطية تعكس الأيام الصافية المقبولة.","Nighttime surface temperature stays separate from daytime, with the same quality/cloud screening. Coverage reflects accepted clear-sky days."),
"ghcnd":("يلزم حقل GHCN_ID صريح من 11 حرفًا وإحداثيات مطابقة. لا تحويل تلقائي من USAF/WBAN ولا أقرب محطة. قيم QFLAG غير الفارغة تستبعد؛ TAVG غير الموجود لا يُخترع.","Requires an explicit 11-character GHCN_ID and matching coordinates. No USAF/WBAN conversion or nearest-station substitution. Nonblank QFLAG values are excluded; absent TAVG is not invented."),
"cds_era5_land_arco":("Need Sign In: رمز CDS الشخصي وقبول شروط المنتج. ARCO ساعي منزوع التراكم بالفعل؛ اليوم يتطلب 24 ساعة UTC. العظمى والصغرى من العينات الساعية، والرطوبة مشتقة من الحرارة والندى. الخدمة ترجع كامل الأرشيف لكل متغير ثم تُرشح الفترة محليًا بحد 64MB. المسار منفذ واختُبر بروتوكوله وتحويلاته؛ لم يُختبر بحساب حقيقي.","Need Sign In: personal CDS token and accepted dataset terms. ARCO is already hourly de-accumulated; a day requires 24 UTC hours. Max/min use hourly samples; RH is derived from temperature/dewpoint. The service returns the full archive per variable, filtered locally with a 64 MB limit. Protocol/conversion tests pass; authenticated end-to-end access remains unverified."),
"imerg07_final":("Need Sign In: حساب NASA Earthdata وإجازة GES DISC. أمطار Final اليومية بوحدة mm/day؛ لا ضرب ثانٍ في 24. المسار منفذ؛ التنزيل بحساب حقيقي لم يُختبر بعد.","Need Sign In: NASA Earthdata account with GES DISC authorization. Final daily precipitation is mm/day, with no second multiplication by 24. Adapter implemented; live authenticated download remains unverified."),
}


def catalogue():
    sources=[]
    for label,spec in PRODUCTS.items():
        item=dict(spec,label=label,tools=["stations"] if label==GHCN else ["points","stations"],
                  implementation="implemented; authenticated live verification pending" if spec['auth'] else "implemented; public sample verified",
                  normalized_units={v:UNITS.get(v,"source unit") for v in spec['variables']})
        if label in REGIONAL:item['tools'].append('regional')
        item['notes_ar'],item['notes_en']=NOTES[spec['id']];sources.append(item)
    sources[:0]=[
        dict(id="power",label="NASA POWER",variables=list(UNITS),resolution="0.5 x 0.625 degree meteorology; 1 x 1 degree radiation/cloud",temporal="Daily points; monthly regional",start="Meteorology 1981; radiation 1984; UV 2001",end="Latest published data, variable-dependent",region="Global",url="https://power.larc.nasa.gov/docs/",auth=None,tools=["points","stations","regional"],implementation="implemented",normalized_units=UNITS,notes_ar="شبكات ثابتة حسب المتغير؛ تصغير بكسل الإخراج لا يزيد دقة معلومات المصدر.",notes_en="Fixed variable-specific grids; smaller output pixels do not increase source information resolution."),
        dict(id="openmeteo",label="Open-Meteo ERA5 / ERA5-Land",variables=list(OM_DAILY)+list(OM_HOURLY),resolution="Auto: Land 0.1 degree or ERA5 0.25 degree per variable and full interval",temporal="Daily",start="ERA5 1940; Land 1950",end="Latest archive, typically delayed",region="Global; Land variables require valid land cells",url="https://open-meteo.com/en/docs/historical-weather-api",auth=None,tools=["points","stations"],implementation="implemented",normalized_units=UNITS,notes_ar="Auto يستخدم Land للحرارة والرطوبة والندى، وERA5 لبقية المتغيرات المدعومة. للفترة التي تبدأ قبل 1950 يستخدم ERA5 كاملًا. الوضع المستقل لا يستكمل NASA؛ المسار القديم والهجين لهما سياسة معلنة منفصلة.",notes_en="Auto uses Land for temperature, RH and dewpoint and ERA5 for other supported variables. An interval beginning before 1950 uses ERA5 throughout. Standalone never supplements NASA; legacy and Hybrid retain explicitly separate policies."),
        dict(id="gsod",label="NOAA GSOD",variables=["T2M","T2M_MAX","T2M_MIN","T2MDEW","PRECTOTCORR","PS","SLP","WS10M"],resolution="Station observations",temporal="Daily summaries",start="General archive 1929; station/element-specific",end="Station/year-specific",region="Exact catalogue station",url="https://www.ncei.noaa.gov/data/global-summary-of-the-day/",auth=None,tools=["stations"],implementation="implemented",normalized_units=UNITS,notes_ar="USAF وWBAN والموقع معًا؛ ليس ISD الساعي ولا GHCN. الهجين ينهي NOAA ثم ERA5 ثم NASA ثم Gap Fill الشهري.",notes_en="USAF, WBAN and location are required together. This is not hourly ISD or GHCN. Hybrid finishes NOAA, then ERA5, then NASA, then optional monthly Gap Fill."),
    ]
    return dict(version="2026-10-18-products-v1",reviewed="2026-10-18",sources=sources)


def main():
    data=catalogue();content=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    for path in (ROOT/'data/climate_sources.json',ROOT/'MIRSAD Desktop/assets/climate_sources.json'):
        path.write_text(content,encoding='utf-8')
    ar=['# دليل مصادر مرصاد — الحالة المنفذة','', 'مراجعة 2026-10-18. نهاية الأرشيف متغيرة؛ لا تعني بداية المنتج وجود كل عنصر في كل موقع. بيانات المصدر ومؤشرات التغطية هي المرجع لكل تشغيل.','']
    en=['# MIRSAD climate sources — implemented state','','Reviewed 2026-10-18. Archive ends change; a product start does not guarantee every variable at every location. Inspect per-run provenance and coverage.','']
    bodies={"ar":[],"en":[]}
    for s in data['sources']:
        common=f"{s['start']} → {s['end']} | {s['resolution']} | {s['temporal']}"
        for language,lines in (('ar',ar),('en',en)):
            note=s['notes_'+language];lines.extend(['## '+s['label'],'',common,'',s['region']+' | '+', '.join(s['tools']),'', '**Variables:** '+', '.join(s['variables']),'',note,'',f"[Official reference]({s['url']})",''])
            bodies[language].append('<article><h2>'+html.escape(s['label'])+'</h2><p>'+html.escape(common)+'</p><p>'+html.escape(s['region']+' | '+', '.join(s['tools']))+'</p><p><b>Variables:</b> '+html.escape(', '.join(s['variables']))+'</p><p>'+html.escape(note)+'</p><a href="'+html.escape(s['url'])+'">Official reference</a></article>')
    for language,lines in (('AR',ar),('EN',en)):
        (ROOT/('Documents/05_Climate_Data_Sources_Directory/SOURCES_'+language+'.md')).write_text('\n'.join(lines),encoding='utf-8')
        guide=ROOT/('Documents/01_Markdown_Manuals/User_Guide_'+('Arabic' if language=='AR' else 'English')+'.md')
        if guide.exists():
            existing=guide.read_text(encoding='utf-8-sig');marker='<!-- CURRENT-SOURCE-CONTRACT -->'
            if marker in existing:existing=existing[:existing.index(marker)].rstrip()
            guide.write_text(existing+'\n\n'+marker+'\n\n'+'\n'.join(lines),encoding='utf-8')
        if language=='EN':
            (ROOT/'MIRSAD Desktop/docs/reports/CLIMATE_SOURCES_AND_RESOLUTION.md').write_text('\n'.join(lines)+'\n\nSee [delivery history](../CHANGELOG.md) and [remaining work](../BACKLOG.md).\n',encoding='utf-8')
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MIRSAD Climate Sources | مصادر مرصاد</title><style>body{font:16px/1.7 system-ui;margin:2rem auto;padding:0 1.2rem;max-width:1100px;background:#f8f8f8;color:#222}article{border:1px solid #ccc;border-radius:12px;padding:1.2rem;margin:1rem 0;background:white}a{color:#075b9f}h2{font-size:1.2rem}p{overflow-wrap:anywhere}@media(prefers-color-scheme:dark){body{background:#181818;color:#eee}article{background:#222;border-color:#444}a{color:#82c4ff}}</style></head><body><a href="index.html">MIRSAD</a><h1>Climate sources | مصادر المناخ</h1><p>2026-10-18 · Development / نسخة التطوير</p><section dir="rtl" lang="ar"><h1>العربية</h1>'+''.join(bodies['ar'])+'</section><section><h1>English</h1>'+''.join(bodies['en'])+'</section></body></html>'
    (ROOT/'climate-sources.html').write_text(page,encoding='utf-8')
    (ROOT/'Documents/05_Climate_Data_Sources_Directory/README.md').write_text('# Climate source directory | دليل المصادر\n\n[العربية](SOURCES_AR.md) · [English](SOURCES_EN.md) · [Website](../../climate-sources.html)\n\nGenerated from the implemented adapter registry by `scripts/build_climate_source_catalogue.py`. JSON snapshot: `data/climate_sources.json`; identical embedded Desktop snapshot.\n\nEarlier documents in this directory are historical references, not the implementation contract. The generated guides above supersede older completeness/provider claims. No source guarantees 100% coverage. Account products require the user’s own account; live authenticated verification is pending.\n',encoding='utf-8')
    directory=ROOT/'Documents/05_Climate_Data_Sources_Directory'
    groups={
        '02_NOAA_ISD_GHCN_Ground_Stations':['gsod','ghcnd'],
        '03_NASA_POWER_Agroclimatology':['power'],
        '04_Open_Meteo_ERA5_Reanalysis':['openmeteo'],
        '05_Copernicus_Climate_Data_Store_CDS':['cds_era5_land_arco'],
        '06_CHIRPS_v3':['chirps3'],'07_TerraClimate_v1_1':['terraclimate11'],
        '08_MODIS_LST':['mod11a2_day','mod11a2_night'],'09_CHELSA_v2_1':['chelsa21'],'10_NASA_IMERG_V07':['imerg07_final']}
    for folder,identifiers in groups.items():
        target=directory/folder;target.mkdir(exist_ok=True)
        for language in ('ar','en'):
            lines=['# MIRSAD climate source profile','', '2026-10-18 · Implemented development source contract','']
            for item in data['sources']:
                if item['id'] not in identifiers:continue
                lines.extend(['## '+item['label'],'',item['start']+' → '+item['end'],'',item['resolution']+' | '+item['temporal'],'',item['region']+' | '+', '.join(item['tools']),'',', '.join(item['variables']),'',item['notes_'+language],'',item['url'],''])
            lines.extend(['[All sources](../SOURCES_'+language.upper()+'.md)','','No source guarantees complete coverage. Missing values stay NULL.'])
            text='\n'.join(lines)
            (target/('README_AR.md' if language=='ar' else 'README.md')).write_text(text,encoding='utf-8')
            (target/('Data_Source_Profile_AR.txt' if language=='ar' else 'Data_Source_Profile.txt')).write_text(text,encoding='utf-8')
            if identifiers==['cds_era5_land_arco']:
                (target/('Copernicus_CDS_Specification_'+language.upper()+'.md')).write_text(text+'\n\nARCO daily conversions: complete 24-hour UTC days; Kelvin to Celsius; Pa to kPa; sum already de-accumulated hourly precipitation metres × 1000; sum hourly solar joules ÷ 1e6. Hourly-sample maxima/minima; RH from the documented Magnus formula. Unsupported sea-level pressure, cloud and UV remain NULL.\n',encoding='utf-8')
    hybrid=directory/'01_Hybrid_Engine_NOAA_NASA_ERA5'
    for language in ('AR','EN'):
        text=('# Hybrid source stages\n\nNOAA GSOD → Open-Meteo ERA5/Land → NASA POWER → optional monthly Gap Fill.\n\nFinish each source across the selected network before requesting missing cells from the next source. Any-point Hybrid skips NOAA. Valid higher-priority values remain unchanged. No source or filling method guarantees complete coverage. Raw observations, quality flags, per-value provenance and separate monthly estimates remain inspectable. Never fabricate daily observations from monthly filling.\n\n[Full source directory](../SOURCES_'+language+'.md)\n')
        if language=='AR':text+="\nينتهي تنزيل كل مصدر لجميع المواقع قبل الانتقال للمصدر التالي للقيم المفقودة فقط. هجين النقاط يبدأ من ERA5. الاستكمال الشهري اختياري بعد التنزيل ولا يصنع رصدًا يوميًا ولا يضمن اكتمالًا شاملًا.\n"
        (hybrid/('README_AR.md' if language=='AR' else 'README.md')).write_text(text,encoding='utf-8')
        (hybrid/('Data_Source_Profile_AR.txt' if language=='AR' else 'Data_Source_Profile.txt')).write_text(text,encoding='utf-8')
    print('Built source catalogue:',len(data['sources']),'sources, SHA256',hashlib.sha256(content.encode()).hexdigest())


if __name__=='__main__':main()
