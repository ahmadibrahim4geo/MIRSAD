# -*- coding: utf-8 -*-
"""
Enrichment + Completeness rebuild for Climate Atlas .style databases.
- Adds 4 new Temperature palettes (mono-red, red-yellow, inferno, teal-green cold alternative).
- Completes orphan palettes into thematic subs (Temp 6 orphans, SPres 2, Wind 2).
- Rebuilds mains so each Main is a strict superset of its subs.
- Upgrades Colors/Fills to 11-class sequence (full ramp sequence integration).
- Syncs to element folders, STYLE/, ArcMap_Style_Files, All_Consolidated, 00_Main_Element_Styles.
Follows same approach as build_true_arcmap_style_databases.py (MultiPartColorRamp, Default Ramps, 0.4pt outline).
Run with: C:\Python27\ArcGIS10.8\python.exe scripts\styles\rebuild_enriched_climate_styles.py
"""
from __future__ import unicode_literals
import os, sys, shutil, time, gc, math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STYLE_DIR = os.path.join(BASE_DIR, "style")
RAW_DIR = os.path.join(STYLE_DIR, "Raw_Climate_Styles")
TEMPLATE_STYLE = os.path.join(RAW_DIR, "Meteorological.style")
OUT_STYLE_DIR = os.path.join(STYLE_DIR, "ArcMap_Style_Files")
CONSOLIDATED = os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated")
MAIN_ONLY_DIR = os.path.join(STYLE_DIR, "00_Main_Element_Styles")
for d in [OUT_STYLE_DIR, CONSOLIDATED, MAIN_ONLY_DIR]:
    if not os.path.isdir(d):
        os.makedirs(d)

sys.path.insert(0, os.path.join(BASE_DIR, "scripts", "styles"))
import generate_climate_styles as gcs

import arcpy
import comtypes.client

com_dir = r"C:\Program Files (x86)\ArcGIS\Desktop10.8\com"
m_sys = comtypes.client.GetModule(os.path.join(com_dir, "esriSystem.olb"))
m_disp = comtypes.client.GetModule(os.path.join(com_dir, "esriDisplay.olb"))
m_fw = comtypes.client.GetModule(os.path.join(com_dir, "esriFramework.olb"))

# ---------- color utils (CIELab interpolation, same as build_mega) ----------
def srgb_to_xyz(r, g, b):
    def inv(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    rl, gl, bl = inv(r), inv(g), inv(b)
    return (rl*0.4124564+gl*0.3575761+bl*0.1804375,
            rl*0.2126729+gl*0.7151522+bl*0.0721750,
            rl*0.0193339+gl*0.1191920+bl*0.9503041)
def xyz_to_lab(x, y, z):
    xn, yn, zn = 0.95047, 1.0, 1.08883
    def f(t):
        return t**(1.0/3.0) if t > 0.008856 else 7.787*t + 16.0/116.0
    fx, fy, fz = f(x/xn), f(y/yn), f(z/zn)
    return (116.0*fy-16.0, 500.0*(fx-fy), 200.0*(fy-fz))
def lab_to_xyz(L, a, b):
    xn, yn, zn = 0.95047, 1.0, 1.08883
    fy = (L+16.0)/116.0; fx = a/500.0+fy; fz = fy-b/200.0
    def invf(t):
        return t**3 if t**3 > 0.008856 else (t-16.0/116.0)/7.787
    return (invf(fx)*xn, invf(fy)*yn, invf(fz)*zn)
def xyz_to_srgb(x, y, z):
    rl = x*3.2404542+y*-1.5371385+z*-0.4985314
    gl = x*-0.9692660+y*1.8760108+z*0.0415560
    bl = x*0.0556434+y*-0.2040259+z*1.0572252
    def gam(v):
        v = max(0.0, min(1.0, v))
        return 12.92*v if v <= 0.0031308 else 1.055*(v**(1.0/2.4))-0.055
    return (int(round(gam(rl)*255)), int(round(gam(gl)*255)), int(round(gam(bl)*255)))
def hex_to_lab(h):
    h = h.strip().lstrip('#')
    if len(h) == 3: h = "".join([c*2 for c in h])
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return xyz_to_lab(*srgb_to_xyz(r,g,b))
def lab_to_hex(L,a,b):
    r,g,bl = xyz_to_srgb(*lab_to_xyz(L,a,b))
    return '#%02X%02X%02X' % (r,g,bl)
def interp_lab(c1,c2,t):
    return (c1[0]+(c2[0]-c1[0])*t, c1[1]+(c2[1]-c1[1])*t, c1[2]+(c2[2]-c1[2])*t)
def interpolate_piecewise(anchors_hex, n):
    lab = [hex_to_lab(h) for h in anchors_hex]
    if n == 1: return [anchors_hex[len(anchors_hex)//2]]
    m = len(lab); res = []
    for i in range(n):
        t = float(i)/float(n-1); st = t*(m-1)
        idx = min(int(math.floor(st)), m-2); lt = st-idx
        L,a,b = interp_lab(lab[idx], lab[idx+1], lt)
        res.append(lab_to_hex(L,a,b))
    return res
def generate_classes(cat, anchors):
    classes = {}
    is_div = (cat.lower() == "diverging")
    for n in [3,4,5,6,7,8,9,10,11]:
        if is_div:
            neg, neu, pos = anchors
            if n % 2 == 1:
                k = (n-1)//2
                left = interpolate_piecewise(neg, k) if k>0 else []
                right = interpolate_piecewise(pos, k) if k>0 else []
                classes[n] = left + [neu] + right
            else:
                k = n//2
                classes[n] = interpolate_piecewise(neg,k) + interpolate_piecewise(pos,k)
        else:
            classes[n] = interpolate_piecewise(anchors, n)
    # JSON keys must be strings for generate_climate_styles compat
    return dict([(unicode(k), v) for k,v in classes.items()])
def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3: h = "".join([c*2 for c in h])
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

# ---------- 4 new enrichment palettes ----------
NEW_TEMP = [
    {"id": "Temp_Seq_MonoRed_Pure", "name_en": "Pure Monochromatic Red Scale",
     "name_ar": "تدرج أحمر أحادي نقي من الوردي الفاتح إلى العنابي الداكن",
     "category": "Sequential", "source": "ColorBrewer 2.0 Reds 9-class (Cynthia Brewer)",
     "anchors": ["#FFF5F0","#FEE5D9","#FCAE91","#FB6A4A","#EF3B2C","#CB181D","#A50F15","#67000D"]},
    {"id": "Temp_Seq_RedYellow_Dual", "name_en": "Red-Yellow Dual Heat Scale",
     "name_ar": "تدرج ثنائي أحمر-أصفر للحرارة الشديدة",
     "category": "Sequential", "source": "ColorBrewer 2.0 YlOrRd (temperature-calibrated)",
     "anchors": ["#FFFFCC","#FFEDA0","#FED976","#FEB24C","#FD8D3C","#FC4E2A","#E31A1C","#BD0026","#800026"]},
    {"id": "Temp_Multi_Inferno_Perceptual", "name_en": "Inferno Perceptual Heat",
     "name_ar": "تدرج إنفرنو الإدراكي الموحد (بديل علمي بجانب الأزرق)",
     "category": "Multi-Hue", "source": "Crameri Scientific / Matplotlib inferno (perceptually uniform)",
     "anchors": ["#000004","#3B0F4F","#7E246A","#B5367A","#DD513A","#F3771A","#FCA50A","#F6D746","#FCFFA4"]},
    {"id": "Temp_Seq_TealGreen_Cold", "name_en": "Teal-Green Cold Alternative",
     "name_ar": "تدرج بارد بديل بجانب الأزرق (تركواز-أخضر للبرودة)",
     "category": "Sequential", "source": "ColorBrewer BuGn/Teal cold alternative (Brewer)",
     "anchors": ["#E5F5F9","#CCECE6","#99D8C9","#66C2A4","#41AE76","#238B45","#006D2C","#00441B"]},
]
for s in NEW_TEMP:
    s["classes"] = generate_classes(s["category"], s["anchors"])
    del s["anchors"]

# ---------- ArcObjects builders ----------
def make_rgb(r,g,b):
    c_obj = comtypes.client.CreateObject("esriDisplay.RgbColor")
    c = c_obj.QueryInterface(m_disp.IRgbColor)
    c.Red=r; c.Green=g; c.Blue=b
    return c_obj.QueryInterface(m_disp.IColor)
def create_stepped(hex_list, name):
    mo = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    m = mo.QueryInterface(m_disp.IMultiPartColorRamp)
    mo.QueryInterface(m_disp.IColorRamp).Name = name
    for h in hex_list:
        r,g,b = hex_to_rgb(h)
        po = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        p = po.QueryInterface(m_disp.IAlgorithmicColorRamp)
        p.FromColor = make_rgb(r,g,b); p.ToColor = make_rgb(r,g,b); p.Algorithm = 1
        m.AddRamp(po.QueryInterface(m_disp.IColorRamp))
    return mo
def create_smooth(hex_list, name):
    mo = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    m = mo.QueryInterface(m_disp.IMultiPartColorRamp)
    mo.QueryInterface(m_disp.IColorRamp).Name = name
    for i in range(len(hex_list)-1):
        r1,g1,b1 = hex_to_rgb(hex_list[i]); r2,g2,b2 = hex_to_rgb(hex_list[i+1])
        po = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        p = po.QueryInterface(m_disp.IAlgorithmicColorRamp)
        p.FromColor = make_rgb(r1,g1,b1); p.ToColor = make_rgb(r2,g2,b2); p.Algorithm = 1
        m.AddRamp(po.QueryInterface(m_disp.IColorRamp))
    return mo
def create_fill(hex_c):
    r,g,b = hex_to_rgb(hex_c)
    fo = comtypes.client.CreateObject("esriDisplay.SimpleFillSymbol")
    f = fo.QueryInterface(m_disp.ISimpleFillSymbol)
    f.Color = make_rgb(r,g,b); f.Style = 0
    lo = comtypes.client.CreateObject("esriDisplay.SimpleLineSymbol")
    l = lo.QueryInterface(m_disp.ISimpleLineSymbol)
    l.Color = make_rgb(110,110,110); l.Width = 0.4; l.Style = 0
    f.Outline = lo.QueryInterface(m_disp.ILineSymbol)
    return fo

def get_theme(s_id, elem_label):
    if s_id in ["Temp_Seq_WarmRed","Temp_Seq_AmberOrange","Temp_Multi_HeatwaveRisk","Temp_Seq_TropicalNights","Temp_Multi_NASA_LST","Temp_Seq_MonoRed_Pure","Temp_Seq_RedYellow_Dual"]:
        return ("Summer Max Temperature Ramps","Summer Heat Colors","Summer Heat Zones")
    elif s_id in ["Temp_Seq_CoolBlue","Temp_Seq_FrostThreshold","Temp_Div_Nuuk_Cryo","Temp_Seq_DeepPurple","Temp_Seq_TealGreen_Cold"]:
        return ("Winter Min Temperature Ramps","Winter Cold Colors","Winter Cold Zones")
    elif s_id in ["Temp_Div_RdYlBu_Brewer","Temp_Div_RdBu_IPCC","Temp_Multi_WMO_Standard","Temp_Div_HadCRUT5","Temp_Multi_KoppenThermal","Temp_Div_NASA_GISTEMP"]:
        return ("Annual Mean Temperature Ramps","Annual Mean Colors","Annual Mean Zones")
    elif s_id in ["Temp_Multi_SpectralMuted","Temp_Div_TealCoral","Temp_Div_PuOr","Temp_Div_ContinentalThermal","Temp_Multi_Roma_Crameri"]:
        return ("Transitional Seasons Ramps","Transitional Colors","Transitional Zones")
    elif s_id in ["Temp_Multi_Thermal_Crameri","Temp_Multi_Roma_Crameri","Temp_Multi_NOAA_NWS","Temp_Multi_ERA5_Thermal","Temp_Multi_NOAA_CPC","Temp_Div_NASA_GISTEMP","Temp_Multi_Inferno_Perceptual","Temp_Multi_KoppenThermal","Temp_Div_HadCRUT5","Temp_Div_RdYlBu_Brewer"]:
        return ("Unified Climatology Ramps","Unified Climatological Colors","Unified Climatological Zones")
    elif s_id in ["Temp_Multi_SteadmanApparent"]:
        return ("Heat Index Ramps","Perceived Temperature Colors","Heat Stress Zones")
    # fallback to original mapping from build script
    import build_true_arcmap_style_databases as _orig
    try:
        return _orig.get_theme_for_style(s_id, elem_label)
    except Exception:
        return (elem_label+" Ramps", elem_label+" Colors", elem_label+" Zones")

def sample11(classes_map):
    for k in [u"11", u"9", u"7", u"5", "11", 11, "9", 9, "7", 7, "5", 5]:
        if k in classes_map and classes_map[k]:
            return classes_map[k]
    return None

def build_main(target_path, style_list, element_label):
    ldb = target_path[:-6]+".ldb" if target_path.endswith(".style") else target_path+".ldb"
    if os.path.isfile(ldb):
        try: os.remove(ldb)
        except: pass
    if os.path.isfile(target_path):
        try: os.remove(target_path)
        except: pass
        time.sleep(0.05)
    shutil.copyfile(TEMPLATE_STYLE, target_path)
    conn = comtypes.client.CreateObject("ADODB.Connection")
    conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source="+target_path)
    for tbl in ["Color Ramps","Colors","Fill Symbols"]:
        rs = comtypes.client.CreateObject("ADODB.Recordset")
        rs.Open("SELECT * FROM ["+tbl+"]", conn, 1, 3)
        while not rs.EOF:
            rs.Delete(); rs.MoveNext()
        rs.Close()
    conn.Close(); del conn, rs; gc.collect()
    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sgs = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sgs.TargetFile = target_path; sgs.AddFile(target_path)
    rc=cc=fc=0
    safe = unicode(element_label or "Climate")
    for s in style_list:
        s_id = s.get("id",""); s_en = s.get("name_en") or s_id
        s_cat = s.get("category") or safe
        is_div = (s_cat.lower()=="diverging")
        cmap = s.get("classes",{})
        tiers = sorted([int(k) for k in cmap.keys()])
        ramp_cat, color_cat, fill_cat = get_theme(s_id, safe)
        theme_tag = ramp_cat.replace(" Temperature Ramps","").replace(" Precipitation Ramps","").replace(" Ramps","").strip()
        if "Master" in safe:
            prefix = s_id.split("_")[0]
            etag = {"Temp":"01 Temp","Precip":"02 Precip","Pres":"03 MSLP","SPres":"04 SPres","Wind":"05 Wind","RH":"06 RH","Solar":"07 Solar","UV":"08 UV","Cloud":"09 Cloud","Aridity":"10 Drought","Drought":"10 Drought","Model":"11 Model"}.get(prefix, safe)
            ramp_prefix = u"%s [%s]" % (etag, theme_tag)
            color_cat = etag+" - "+color_cat; fill_cat = etag+" - "+fill_cat
        else:
            ramp_prefix = u"[%s]" % theme_tag
        for nc in tiers:
            hl = cmap.get(nc) or cmap.get(unicode(nc)) or cmap.get(unicode(str(nc))) or cmap.get(str(nc))
            if not hl: continue
            sn = u"%s %s - Stepped (%d Classes)" % (ramp_prefix, s_en, nc)
            it = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
            it.Name=sn; it.Category=u"Default Ramps"; it.Item=create_stepped(hl,sn); sg.AddItem(it); rc+=1
            mn = u"%s %s - Smooth (%d Classes)" % (ramp_prefix, s_en, nc)
            it2 = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
            it2.Name=mn; it2.Category=u"Default Ramps"; it2.Item=create_smooth(hl,mn); sg.AddItem(it2); rc+=1
        sh = sample11(cmap)
        if sh:
            tot=len(sh); mid=tot//2
            for idx,hx in enumerate(sh):
                r,g,b = hex_to_rgb(hx)
                if is_div and idx==mid and (tot%2==1):
                    cl=u"%s - Neutral Center (%s)"%(s_en,hx); fl=u"%s - Neutral Center Fill (%s)"%(s_en,hx)
                else:
                    cl=u"%s - Class %d/%d (%s)"%(s_en,idx+1,tot,hx); fl=u"%s - Zone %d/%d Fill (%s)"%(s_en,idx+1,tot,hx)
                ic = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
                ic.Name=cl; ic.Category=color_cat; ic.Item=make_rgb(r,g,b); sg.AddItem(ic); cc+=1
                iff = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
                iff.Name=fl; iff.Category=fill_cat; iff.Item=create_fill(hx); sg.AddItem(iff); fc+=1
    sg.SaveStyle(target_path,"Color Ramps",""); sg.SaveStyle(target_path,"Colors",""); sg.SaveStyle(target_path,"Fill Symbols","")
    del sg,sgs,sg_obj; gc.collect(); time.sleep(0.05)
    print("SUCCESS MAIN: %s -> %d Ramps | %d Colors | %d Fills" % (os.path.basename(target_path),rc,cc,fc))
    return rc,cc,fc

def build_sub(target_path, style_list, label, ramp_cat, color_cat, fill_cat):
    ldb = target_path[:-6]+".ldb" if target_path.endswith(".style") else target_path+".ldb"
    if os.path.isfile(ldb):
        try: os.remove(ldb)
        except: pass
    if os.path.isfile(target_path):
        try: os.remove(target_path)
        except: pass
        time.sleep(0.05)
    shutil.copyfile(TEMPLATE_STYLE, target_path)
    conn = comtypes.client.CreateObject("ADODB.Connection")
    conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source="+target_path)
    for tbl in ["Color Ramps","Colors","Fill Symbols"]:
        rs = comtypes.client.CreateObject("ADODB.Recordset")
        rs.Open("SELECT * FROM ["+tbl+"]", conn, 1, 3)
        while not rs.EOF:
            rs.Delete(); rs.MoveNext()
        rs.Close()
    conn.Close(); del conn, rs; gc.collect()
    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sgs = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sgs.TargetFile = target_path; sgs.AddFile(target_path)
    rc=cc=fc=0
    theme_tag = unicode(label.split(" and ")[0].strip() if " and " in unicode(label) else unicode(label).strip())
    for s in style_list:
        s_en = s.get("name_en") or s.get("id","")
        s_cat = s.get("category") or label
        is_div = (s_cat.lower()=="diverging")
        cmap = s.get("classes",{})
        tiers = sorted([int(k) for k in cmap.keys()])
        for nc in tiers:
            hl = cmap.get(nc) or cmap.get(unicode(nc)) or cmap.get(str(nc))
            if not hl: continue
            sn=u"[%s] %s - Stepped (%d Classes)"%(theme_tag,s_en,nc)
            it = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
            it.Name=sn; it.Category=u"Default Ramps"; it.Item=create_stepped(hl,sn); sg.AddItem(it); rc+=1
            mn=u"[%s] %s - Smooth (%d Classes)"%(theme_tag,s_en,nc)
            it2 = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
            it2.Name=mn; it2.Category=u"Default Ramps"; it2.Item=create_smooth(hl,mn); sg.AddItem(it2); rc+=1
        sh = sample11(cmap)
        if sh:
            tot=len(sh); mid=tot//2
            for idx,hx in enumerate(sh):
                r,g,b = hex_to_rgb(hx)
                if is_div and idx==mid and (tot%2==1):
                    cl=u"%s - Neutral Center (%s)"%(s_en,hx); fl=u"%s - Neutral Center Fill (%s)"%(s_en,hx)
                else:
                    cl=u"%s - Class %d/%d (%s)"%(s_en,idx+1,tot,hx); fl=u"%s - Zone %d/%d Fill (%s)"%(s_en,idx+1,tot,hx)
                ic = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
                ic.Name=cl; ic.Category=unicode(color_cat); ic.Item=make_rgb(r,g,b); sg.AddItem(ic); cc+=1
                iff = comtypes.client.CreateObject("esriFramework.StyleGalleryItem").QueryInterface(m_disp.IStyleGalleryItem)
                iff.Name=fl; iff.Category=unicode(fill_cat); iff.Item=create_fill(hx); sg.AddItem(iff); fc+=1
    sg.SaveStyle(target_path,"Color Ramps",""); sg.SaveStyle(target_path,"Colors",""); sg.SaveStyle(target_path,"Fill Symbols","")
    del sg,sgs,sg_obj; gc.collect(); time.sleep(0.05)
    print("SUCCESS SUB: %s -> %d Ramps | %d Colors | %d Fills" % (os.path.basename(target_path),rc,cc,fc))
    return rc,cc,fc

def sync_copy(src, dsts):
    for d in dsts:
        dd = os.path.dirname(d)
        if not os.path.isdir(dd): os.makedirs(dd)
        shutil.copyfile(src, d)

if __name__ == "__main__":
    print("=== Enrichment + completeness rebuild ===")
    all_els = [{"folder":"01_Temperature","name_en":"Temperature","styles":list(gcs.TEMPERATURE_STYLES)}] + [dict(folder=e["folder"],name_en=e["name_en"],styles=list(e["styles"])) for e in gcs.OTHER_ELEMENTS]
    by_id = {}
    for el in all_els:
        for s in el["styles"]:
            by_id[s["id"]] = s
    for s in NEW_TEMP:
        by_id[s["id"]] = s
    # extend temperature element
    for el in all_els:
        if el["folder"]=="01_Temperature":
            el["styles"] = el["styles"] + NEW_TEMP
            print("Temperature palettes: %d -> %d" % (len(gcs.TEMPERATURE_STYLES), len(el["styles"])))
    elmap = dict([(e["folder"], e) for e in all_els])

    def pick(ids):
        out=[]
        for i in ids:
            if i in by_id: out.append(by_id[i])
            else: print("WARNING missing "+i)
        return out

    # --- updated sub specs (complete orphans + enrichment) ---
    subs = [
        ("01_Temperature","01_Temp_Annual_Mean.style","Annual Temperature Mean","Annual Temperature Ramps","Annual Temperature Colors","Annual Temperature Zones",
         ["Temp_Div_RdYlBu_Brewer","Temp_Multi_Thermal_Crameri","Temp_Multi_SpectralMuted","Temp_Div_RdBu_IPCC","Temp_Div_NASA_GISTEMP","Temp_Div_HadCRUT5"]),
        ("01_Temperature","01_Temp_Summer_Max.style","Summer and Extreme Maximum Temperature","Summer Max Temperature Ramps","Summer Max Colors","Summer Heat Zones",
         ["Temp_Seq_WarmRed","Temp_Seq_AmberOrange","Temp_Multi_HeatwaveRisk","Temp_Seq_TropicalNights","Temp_Multi_NASA_LST","Temp_Seq_MonoRed_Pure","Temp_Seq_RedYellow_Dual"]),
        ("01_Temperature","01_Temp_Winter_Min.style","Winter and Minimum Temperature / Frost","Winter Min Temperature Ramps","Winter Cold & Frost Colors","Winter Cold Zones",
         ["Temp_Seq_CoolBlue","Temp_Seq_FrostThreshold","Temp_Div_Nuuk_Cryo","Temp_Seq_DeepPurple","Temp_Seq_TealGreen_Cold"]),
        ("01_Temperature","01_Temp_Spring_Autumn.style","Transitional Seasons Spring and Autumn","Transitional Temperature Ramps","Spring & Autumn Colors","Transitional Temperature Zones",
         ["Temp_Multi_SpectralMuted","Temp_Div_TealCoral","Temp_Div_PuOr","Temp_Multi_WMO_Standard","Temp_Multi_Roma_Crameri","Temp_Div_ContinentalThermal"]),
        ("01_Temperature","01_Temp_Unified_All_Seasons.style","Unified Multi-Panel Seasons Comparison","Unified Multi-Panel Ramps","Unified Climatological Colors","Unified Climatological Zones",
         ["Temp_Multi_Thermal_Crameri","Temp_Div_RdYlBu_Brewer","Temp_Multi_NOAA_NWS","Temp_Multi_ERA5_Thermal","Temp_Multi_NOAA_CPC","Temp_Multi_KoppenThermal","Temp_Multi_Inferno_Perceptual"]),
        ("01_Temperature","01_Temp_Heat_Index.style","Perceived Temperature and Heat Index","Heat Index Ramps","Perceived Temperature Colors","Heat Stress Zones",
         ["Temp_Multi_SteadmanApparent","Temp_Multi_HeatwaveRisk"]),
        ("01_Temperature","01_Temp_RedScale_Enriched.style","Enriched Red Scales and Perceptual Alternatives","Enriched Red & Perceptual Ramps","Enriched Heat Colors","Enriched Heat Zones",
         ["Temp_Seq_MonoRed_Pure","Temp_Seq_RedYellow_Dual","Temp_Multi_Inferno_Perceptual","Temp_Seq_TealGreen_Cold"]),
        ("04_Surface_Pressure","04_SPres_Hypsometric_Terrain.style","Hypsometric Surface Pressure and Complex Terrain","Hypsometric Surface Pressure Ramps","Hypsometric Pressure Colors","Hypsometric Pressure Zones",
         ["SPres_Seq_Hypsometric","SPres_Multi_Terrain","SPres_Multi_MicroRelief","SPres_Seq_Altimeter"]),
        ("04_Surface_Pressure","04_SPres_Basin_Plateau_Extreme.style","Plateau and Deep Basin Surface Pressure","Basin & Plateau Pressure Ramps","Plateau & Basin Colors","Plateau & Basin Zones",
         ["SPres_Seq_ValleyBasin","SPres_Multi_PlateauHigh","SPres_Div_Anomaly","SPres_Div_LapseRate"]),
        ("05_Wind","05_Wind_Summer_Thermal_Breeze.style","Summer Coastal Sea Breeze and Jet Stream","Coastal Thermal Breeze Ramps","Coastal Breeze Colors","Coastal Breeze Zones",
         ["Wind_Seq_ThermalBreeze","Wind_Multi_DopplerVelocity","Wind_Multi_JetStream","Wind_Multi_Hurricanes","Wind_Multi_AviationTurbulence"]),
    ]
    # build subs
    for folder,fname,label,rc_cat,cc_cat,fc_cat,ids in subs:
        sel = pick(ids)
        local = os.path.join(STYLE_DIR, folder, fname)
        build_sub(local, sel, label, rc_cat, cc_cat, fc_cat)
        sync_copy(local, [os.path.join(OUT_STYLE_DIR,fname), os.path.join(CONSOLIDATED,fname)])

    # --- rebuild mains (01,04,05 + master) ---
    mains = [
        ("01_Temperature","01_Temperature.style","Temperature"),
        ("04_Surface_Pressure","04_Surface_Pressure.style","Surface Pressure"),
        ("05_Wind","05_Wind.style","Wind"),
    ]
    for folder,fname,label in mains:
        sel = elmap[folder]["styles"]
        local = os.path.join(STYLE_DIR, folder, fname)
        build_main(local, sel, label)
        style_sub = os.path.join(STYLE_DIR, folder, "STYLE", fname)
        sync_copy(local, [style_sub, os.path.join(OUT_STYLE_DIR,fname), os.path.join(CONSOLIDATED,fname)])

    # master (all + new)
    master_styles = []
    for e in all_els:
        master_styles.extend(e["styles"])
    print("Master palettes total: %d" % len(master_styles))
    master_local = os.path.join(OUT_STYLE_DIR, "NASA_POWER_Climate_Atlas_Master.style")
    build_main(master_local, master_styles, "Climate Atlas Master")
    sync_copy(master_local, [os.path.join(CONSOLIDATED,"NASA_POWER_Climate_Atlas_Master.style"),
                             os.path.join(BASE_DIR,"NASA_POWER_Climate_Atlas_Master.style")])
    # refresh 00_Main_Element_Styles with rebuilt mains + master
    for folder,fname,label in mains:
        shutil.copyfile(os.path.join(STYLE_DIR,folder,fname), os.path.join(MAIN_ONLY_DIR,fname))
    shutil.copyfile(master_local, os.path.join(MAIN_ONLY_DIR,"12_NASA_POWER_Climate_Atlas_Master.style"))
    print("=== DONE ===")
