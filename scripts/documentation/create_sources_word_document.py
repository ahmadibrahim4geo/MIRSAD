# -*- coding: utf-8 -*-
"""
Generate Comprehensive Scientific Sources, Cartographic Standards & References
Word Document (.docx) and Metadata Catalogs (.csv, .json, .md)
Mega Edition: 125 Styles across 11 Elements | 9 Class Tiers (3 to 11)
2,250 Color Ramps | 875 Colors | 875 Fill Symbols
"""

import os
import sys
import io
import json
import csv
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STYLE_DIR = os.path.join(BASE_DIR, "style")
SOURCES_DIR = os.path.join(STYLE_DIR, "Source_of_Style_and_Color")
DOCX_PATH = os.path.join(SOURCES_DIR, "Climate_Styles_Sources_and_References.docx")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts", "styles"))
import generate_climate_styles as gcs

def set_cell_shading(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_rtl(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

def add_hyperlink(paragraph, url, text, color="0563C1", underline=True, bold=False):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rPr.append(c)
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)
    if bold:
        b = OxmlElement('w:b')
        rPr.append(b)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def build_docx():
    print("Building Mega Climate Styles Sources & References Word Document (.docx)...")
    doc = docx.Document()

    # Margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    PRIMARY = RGBColor(27, 54, 93)     # Deep Navy
    SECONDARY = RGBColor(43, 91, 132)  # Slate Blue
    ACCENT = RGBColor(180, 40, 20)     # Warm Crimson
    TEXT_DARK = RGBColor(34, 34, 34)   # Charcoal
    MUTED_GRAY = RGBColor(100, 100, 100)

    # Document Header / Banner Box
    title_p = doc.add_paragraph()
    make_rtl(title_p)
    title_p.paragraph_format.space_before = Pt(8)
    title_p.paragraph_format.space_after = Pt(2)
    run_t = title_p.add_run("الموسوعة العلمية والمراجع الدولية المعتمدة للستايلات والتدرجات المناخية (Mega Edition)")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(20)
    run_t.font.bold = True
    run_t.font.color.rgb = PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sub_p.paragraph_format.space_after = Pt(6)
    run_sub = sub_p.add_run("Mega Edition: 125 Climate Styles across 11 Elements | 9 Class Tiers (3 to 11 Classes) | 2,250 Color Ramps")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = SECONDARY

    meta_p = doc.add_paragraph()
    make_rtl(meta_p)
    meta_p.paragraph_format.space_after = Pt(16)
    run_meta = meta_p.add_run(
        "المشروع: أطلس المناخ الشامل (NASA POWER & Open-Meteo Climate Atlas Generator)\n"
        "البيئات البرمجية: ArcGIS Desktop (ArcMap 10.0 - 10.8.2) | ArcGIS Pro | QGIS | GeoServer\n"
        "الهندسة الكارتوجرافية: 125 ستايلاً علمياً | 9 مستويات فئات (3، 4، 5، 6، 7، 8، 9، 10، 11 فئة) | 2,250 Color Ramps (فئات مجزأة وتدرجات ناعمة) | 875 لوناً فردياً | 875 رمز مضلع\n"
        "المسار المعتمد: style/Source_of_Style_and_Color/ | التوثيق الكارتوجرافي والفيزيائي الأكاديمي الشامل"
    )
    run_meta.font.name = "Arial"
    run_meta.font.size = Pt(9.5)
    run_meta.font.color.rgb = MUTED_GRAY

    # -----------------------------------------------------------------------
    # Section 1: Introduction & Physical Foundations
    # -----------------------------------------------------------------------
    h1 = doc.add_paragraph()
    make_rtl(h1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    r_h1 = h1.add_run("1. المقدمة والأسس الفيزيائية والكارتوجرافية لاختيار الألوان")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(14)
    r_h1.font.bold = True
    r_h1.font.color.rgb = PRIMARY

    p_intro = doc.add_paragraph()
    make_rtl(p_intro)
    p_intro.paragraph_format.line_spacing = 1.2
    p_intro.paragraph_format.space_after = Pt(8)
    r_intro = p_intro.add_run(
        "تعتبر الخريطة المناخية وسيلة اتصال بصري دقيقة لترجمة الظواهر الفيزيائية المعقدة للغلاف الجوي. "
        "وقد أثبتت الدراسات الكارتوجرافية الحديثة المنشورة في كبرى الدوريات العالمية (Nature Communications بواسطة Crameri et al., 2020) "
        "أن الاختيار العشوائي للألوان، وتحديداً تدرجات قوس قزح المشبعة (Rainbow / Jet)، يقود إلى أخطاء فادحة في تفسير البيانات المناخية وتضليل متخذي القرار. "
        "لذا تم بناء منظومة الستايلات في هذا المشروع بالاستناد الصارم إلى المعايير المعتمدة من الهيئات والمنظمات الدولية الكبرى: "
        "(IPCC, WMO, NOAA, WHO, UNEP, FAO, World Bank ESMAP, ColorBrewer, Esri Cartography, ECMWF, HadCRUT5, NASA Earthdata)."
    )
    r_intro.font.name = "Arial"
    r_intro.font.size = Pt(10.5)
    r_intro.font.color.rgb = TEXT_DARK

    bullets = [
        ("حظر تدرجات قوس قزح المشوهة (The End of the Rainbow Palette): ",
         "تدرجات Jet/Rainbow تخلق حدوداً وهمية (False Boundaries) عند الانتقال الحاد بين الأصفر والأزرق السماوي، بينما الحقيقة الفيزيائية للحرارة أو الضغط تتغير بنعومة. كما أنها تخفي التفاصيل الدقيقة في النطاق الأخضر المنعدم التباين."),
        ("التدرجات المحايدة إدراكياً (Perceptually Uniform Colormaps): ",
         "الاعتماد على الفضاء اللوني CIE L*a*b* والسطوع اللوني المنتظم خطياً (Linear Lightness Gradient ΔL*)، مما يضمن أن التغير في القيمة العددية يترجم مباشرة لتغير مكافئ ومريح في العين البشرية دون أي تشويش بصري."),
        ("التوافق مع فئات عمى الألوان (Colorblind-Safe Design): ",
         "يعاني ما يقارب 8% من الذكور من أشكال مختلفة من عمى الألوان (Deuteranopia, Protanopia). تضمن هذه الستايلات إمكانية التمييز البصري الكامل لجميع الفئات دون التباس."),
        ("جودة الطباعة بالأبيض والأسود (Greyscale Printable): ",
         "يمكن طباعة الخريطة بتدرج الرمادي التام دون أدنى فقدان للبيانات، حيث تتدرج القيم من الفاتح إلى الداكن بانتظام رياضي ثابت.")
    ]
    for b_title, b_desc in bullets:
        bp = doc.add_paragraph()
        make_rtl(bp)
        bp.paragraph_format.line_spacing = 1.15
        bp.paragraph_format.space_after = Pt(4)
        r_bt = bp.add_run("• " + b_title)
        r_bt.font.name = "Arial"
        r_bt.font.size = Pt(10)
        r_bt.font.bold = True
        r_bt.font.color.rgb = SECONDARY
        r_bd = bp.add_run(b_desc)
        r_bd.font.name = "Arial"
        r_bd.font.size = Pt(10)
        r_bd.font.color.rgb = TEXT_DARK

    # -----------------------------------------------------------------------
    # Section 2: 9 Class Tiers Architecture (3 to 11) & Symmetry Rules
    # -----------------------------------------------------------------------
    h2 = doc.add_paragraph()
    make_rtl(h2)
    h2.paragraph_format.space_before = Pt(16)
    h2.paragraph_format.space_after = Pt(6)
    r_h2 = h2.add_run("2. معمارية المستويات التسعة للفئات (3 إلى 11 فئة) والتناظر المناخي الصارم")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(14)
    r_h2.font.bold = True
    r_h2.font.color.rgb = PRIMARY

    p_tiers = doc.add_paragraph()
    make_rtl(p_tiers)
    p_tiers.paragraph_format.line_spacing = 1.2
    p_tiers.paragraph_format.space_after = Pt(8)
    r_ti = p_tiers.add_run(
        "لتغطية كافة الاحتمالات الكارتوجرافية والتحليلية الممكنة، تم توسيع كافة الستايلات الـ 125 لتشمل تسعة مستويات فئات كاملة: "
        "[3، 4، 5، 6، 7، 8، 9، 10، 11 فئة]، بنوعين مستقلين لكل فئة:\n"
        "1. الفئات المجزأة المستقلة [Stepped]: كل فئة تمثل كتلة لونية موحدة مسطحة (Solid Color Block) لتمثيل خرائط الراستر المصنفة (Classified Rasters) بوضوح تام.\n"
        "2. التدرج اللوني المستمر [Smooth]: تدرج ناعم يتبع الفضاء اللوني CIELab لتمثيل الأسطح المتصلة (Stretched Rasters)."
    )
    r_ti.font.name = "Arial"
    r_ti.font.size = Pt(10.5)
    r_ti.font.color.rgb = TEXT_DARK

    p_sym = doc.add_paragraph()
    make_rtl(p_sym)
    p_sym.paragraph_format.space_after = Pt(6)
    r_sy_t = p_sym.add_run("قواعد التناظر الرياضي الصارم للتدرجات ثنائية الاتجاه (Diverging Symmetry Rules):\n")
    r_sy_t.font.name = "Arial"
    r_sy_t.font.size = Pt(11)
    r_sy_t.font.bold = True
    r_sy_t.font.color.rgb = ACCENT

    sym_rules = [
        ("الفئات الفردية (3، 5، 7، 9، 11 فئة) - وجود فئة وسطى محايدة تماماً: ",
         "\n   • 11 فئة (النمط 5 - 1 - 5): 5 فئات سالبة + 1 محايدة (#FFFFFF أو #F7F7F7) + 5 فئات موجبة."
         "\n   • 9 فئات (النمط 4 - 1 - 4): 4 فئات سالبة + 1 محايدة + 4 فئات موجبة."
         "\n   • 7 فئات (النمط 3 - 1 - 3): 3 فئات سالبة + 1 محايدة + 3 فئات موجبة."
         "\n   • 5 فئات (النمط 2 - 1 - 2): فئتان سالبتان + 1 محايدة + فئتان موجبتان."
         "\n   • 3 فئات (النمط 1 - 1 - 1): فئة سالبة + 1 محايدة + فئة موجبة."),
        ("الفئات الزوجية والبينية (4، 6، 8، 10 فئات) - تماثل قطبي متوازن: ",
         "\n   • 10 فئات: 5 فئات سالبة تقابل 5 فئات موجبة بتدرج لوني تدريجي يلتقي في الوسط دون فئة نقطة الصفر."
         "\n   • 8 فئات: 4 فئات سالبة تقابل 4 فئات موجبة."
         "\n   • 6 فئات: 3 فئات سالبة تقابل 3 فئات موجبة."
         "\n   • 4 فئات: فئتان سالبتان تقابلان فئتين موجبتين.")
    ]
    for s_title, s_desc in sym_rules:
        sp = doc.add_paragraph()
        make_rtl(sp)
        sp.paragraph_format.space_after = Pt(4)
        r_stt = sp.add_run("✔ " + s_title)
        r_stt.font.name = "Arial"
        r_stt.font.size = Pt(10)
        r_stt.font.bold = True
        r_stt.font.color.rgb = SECONDARY
        r_sdd = sp.add_run(s_desc)
        r_sdd.font.name = "Arial"
        r_sdd.font.size = Pt(9.5)
        r_sdd.font.color.rgb = TEXT_DARK

    # -----------------------------------------------------------------------
    # Section 3: Native ArcObjects .style Architecture
    # -----------------------------------------------------------------------
    h3 = doc.add_paragraph()
    make_rtl(h3)
    h3.paragraph_format.space_before = Pt(16)
    h3.paragraph_format.space_after = Pt(6)
    r_h3 = h3.add_run("3. البنية البرمجية لقواعد بيانات الستايل (.style) ومكونات ArcObjects")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(14)
    r_h3.font.bold = True
    r_h3.font.color.rgb = PRIMARY

    p_arch = doc.add_paragraph()
    make_rtl(p_arch)
    p_arch.paragraph_format.line_spacing = 1.2
    p_arch.paragraph_format.space_after = Pt(8)
    r_arc = p_arch.add_run(
        "تعتمد ملفات .style الخاصة بـ ArcMap 10.x على معمارية قواعد بيانات Microsoft Jet 4.0 Access، "
        "حيث يتم تشفير الكائنات الكارتوجرافية عبر واجهات ArcObjects COM. وقد تم تزويد كل ملف .style بثلاثة جداول رئيسية:\n"
        "1. جدول [Color Ramps]: يحتوي على 2,250 تدرجاً لونياً ثنائي التكوين (MultiPartColorRamp)، يدمج فئات مجزأة وتدرجات ناعمة بأحجام مخصصة تضمن ظهور معاينة حية (Visual Preview) بنسبة 100% داخل ArcMap Style Manager.\n"
        "2. جدول [Colors]: يحتوي على 875 عينة لون فردية مسماة (RgbColor) تمثل ألوان الفئات ونقاط التعادل، ليتمكن المستخدم من اختيارها مباشرة من لوحة الألوان.\n"
        "3. جدول [Fill Symbols]: يحتوي على 875 رمز مضلع مغلق (SimpleFillSymbol) مع حدود خفيفة (0.4pt) لتمثيل النطاقات المناخية والمناطق المصنفة في الخرائط المتجهة (Vector Polygons)."
    )
    r_arc.font.name = "Arial"
    r_arc.font.size = Pt(10.5)
    r_arc.font.color.rgb = TEXT_DARK

    # -----------------------------------------------------------------------
    # Section 4: International Standards Table (15 Major Organizations)
    # -----------------------------------------------------------------------
    h4 = doc.add_paragraph()
    make_rtl(h4)
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(6)
    r_h4 = h4.add_run("4. جدول الفهرس الشامل لجميع المراجع الدولية المعتمدة (15 منظومة ومصدراً دولياً)")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(14)
    r_h4.font.bold = True
    r_h4.font.color.rgb = PRIMARY

    table_sources = [
        ("Esri: Better Colors for Better Mapping", "معهد إزري الأمريكي (Esri Inc.)", "تصميم الألوان الكارتوجرافية", "درجات الحرارة، الراستر العام", "https://www.esri.com/arcgis-blog/products/js-api-arcgis/mapping/better-colors-for-better-mapping"),
        ("CPT-City Climatological Archive", "جامعة شيفيلد / J.J. Green", "أرشيف التدرجات المناخية", "الحرارة، المطر، الضغط، التضاريس", "https://phillips.shef.ac.uk/pub/cpt-city/"),
        ("IPCC AR6 & Scientific Colour Maps", "الهيئة الدولية لتغير المناخ / د. فابيو كراميري", "المعايير البصرية المحايدة إدراكياً", "الحرارة، النماذج، الشذوذ المناخي", "https://www.fabiocrameri.ch/colourmaps/"),
        ("ColorBrewer 2.0 (Cynthia Brewer)", "جامعة بنسلفانيا / NSF", "الفئات الكارتوجرافية المتوازنة", "جميع العناصر (3 إلى 11 فئة)", "https://colorbrewer2.org/"),
        ("WMO Standards (WMO-No. 306 & No. 8)", "المنظمة العالمية للأرصاد الجوية (WMO)", "اللوائح الدولية للطقس والمناخ", "الرياح، الضغط، الغيوم، الصقيع", "https://library.wmo.int/records/item/35625-manual-on-codes"),
        ("NOAA NWS & NBM Operational Scales", "الهيئة الوطنية الأمريكية للمحيطات والغلاف الجوي", "المعايير التشغيلية للتنبؤات والرصد", "الحرارة، مؤشر الحرارة، المطر", "https://www.wpc.ncep.noaa.gov/"),
        ("Global Solar UV Index (ISBN 92 4 159007 6)", "منظمة الصحة العالمية (WHO) / WMO / UNEP", "المعيار الصحي الدولي الملزم", "مؤشر الأشعة فوق البنفسجية", "https://www.who.int/publications/i/item/9241590076"),
        ("UNEP Desertification Atlas & FAO-56", "برنامج الأمم المتحدة للبيئة / منظمة الفاو", "معايير القحولة والجفاف والهيدرولوجيا", "القحولة، الجفاف، العجز المائي", "https://wad.jrc.ec.europa.eu/"),
        ("Global Solar Atlas Standards", "البنك الدولي / ESMAP / Solargis", "كارتوجرافيا الطاقة الشمسية", "الإشعاع الشمسي والطاقة الكلية", "https://globalsolaratlas.info/"),
        ("Warming Stripes Climate Initiative", "بروفيسور إد هوكينز / جامعة ريدينج", "التواصل الكارتوجرافي للاحترار", "نماذج المناخ والشذوذ الحراري", "https://showyourstripes.info/"),
        ("ECMWF Copernicus Climate Change Service", "المركز الأوروبي للتنبؤات الجوية (ECMWF)", "إعادة التحليل المناخي العالمي ERA5", "النماذج المناخية ورطوبة التربة", "https://climate.copernicus.eu/"),
        ("NOAA Doppler Radar dBZ Scale", "المركز الوطني لرادارات الطقس (ROC / NWS)", "مقياس انعكاسية الرادار للهطول", "العواصف المطرية والهطول الراداري", "https://www.weather.gov/jetstream/reflectivity"),
        ("NASA Earth Science Data Systems (ESDS)", "وكالة الفضاء الأمريكية (NASA)", "بيانات الأقمار الاصطناعية (GPM, LST, MODIS)", "الحرارة السطحية، الأمطار، الهباء الجوي", "https://earthdata.nasa.gov/"),
        ("HadCRUT5 Historical Climate Analysis", "مركز هادلي للأرصاد البريطاني (Met Office)", "سجلات الاحترار العالمي التاريخية", "شذوذ درجات الحرارة منذ 1850", "https://www.metoffice.gov.uk/hadobs/hadcrut5/"),
        ("Köppen-Geiger Climate Classification", "جامعة فيينا ومعهد ماكس بلانك", "التصنيف المناخي العالمي المعياري", "الأقاليم الحرارية والمطرية", "http://koeppen-geiger.vu-wien.ac.at/")
    ]

    t1 = doc.add_table(rows=len(table_sources) + 1, cols=5)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)

    headers1 = ["المعيار / المصدر الرسمي", "الجهة الدولية المصدرة", "التصنيف الكارتوجرافي", "العناصر المناخية المطبقة", "الرابط الرسمي المباشر"]
    col_widths1 = [Inches(1.8), Inches(1.5), Inches(1.3), Inches(1.2), Inches(1.2)]

    hdr_cells = t1.rows[0].cells
    for i, title in enumerate(headers1):
        hdr_cells[i].width = col_widths1[i]
        set_cell_shading(hdr_cells[i], "1B365D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        make_rtl(p)
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, data in enumerate(table_sources):
        row_cells = t1.rows[row_idx + 1].cells
        bg_color = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        for i in range(5):
            row_cells[i].width = col_widths1[i]
            set_cell_shading(row_cells[i], bg_color)
            set_cell_margins(row_cells[i], top=80, bottom=80, left=100, right=100)
            row_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        p0 = row_cells[0].paragraphs[0]
        make_rtl(p0)
        r0 = p0.add_run(data[0])
        r0.font.name = "Arial"
        r0.font.size = Pt(9)
        r0.font.bold = True

        p1 = row_cells[1].paragraphs[0]
        make_rtl(p1)
        r1 = p1.add_run(data[1])
        r1.font.name = "Arial"
        r1.font.size = Pt(8.5)

        p2 = row_cells[2].paragraphs[0]
        make_rtl(p2)
        r2 = p2.add_run(data[2])
        r2.font.name = "Arial"
        r2.font.size = Pt(8.5)

        p3 = row_cells[3].paragraphs[0]
        make_rtl(p3)
        r3 = p3.add_run(data[3])
        r3.font.name = "Arial"
        r3.font.size = Pt(8.5)

        p4 = row_cells[4].paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_hyperlink(p4, data[4], "زيارة الرابط ↗", color="0563C1", underline=True, bold=True)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -----------------------------------------------------------------------
    # Section 5: Master Table of all 125 Palettes
    # -----------------------------------------------------------------------
    h5 = doc.add_paragraph()
    make_rtl(h5)
    h5.paragraph_format.space_before = Pt(16)
    h5.paragraph_format.space_after = Pt(6)
    r_h5 = h5.add_run("5. الفهرس الشامل لجميع الـ 125 ستايلاً كارتوجرافياً عبر عناصر المناخ الـ 11")
    r_h5.font.name = "Arial"
    r_h5.font.size = Pt(14)
    r_h5.font.bold = True
    r_h5.font.color.rgb = PRIMARY

    flat_styles = []
    all_elements = [{"folder": "01_Temperature", "name_en": "Temperature", "name_ar": "درجات الحرارة", "styles": gcs.TEMPERATURE_STYLES}] + gcs.OTHER_ELEMENTS
    for el in all_elements:
        el_ar = el.get("name_ar", el["folder"])
        for s in el["styles"]:
            flat_styles.append({
                "element_ar": el_ar,
                "id": s["id"],
                "name_en": s["name_en"],
                "name_ar": s["name_ar"],
                "category": s["category"],
                "source": s["source"]
            })

    t_styles = doc.add_table(rows=len(flat_styles) + 1, cols=5)
    t_styles.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_styles)

    headers_st = ["العنصر المناخي", "اسم الستايل (عربي / إنجليزي)", "المعرف البرمجي (ID)", "النوع الكارتوجرافي", "المصدر العلمي المعتمد"]
    col_w_st = [Inches(1.2), Inches(2.3), Inches(1.4), Inches(0.9), Inches(1.4)]

    hdr_s_cells = t_styles.rows[0].cells
    for i, title in enumerate(headers_st):
        hdr_s_cells[i].width = col_w_st[i]
        set_cell_shading(hdr_s_cells[i], "1B365D")
        set_cell_margins(hdr_s_cells[i], top=100, bottom=100, left=80, right=80)
        p = hdr_s_cells[i].paragraphs[0]
        make_rtl(p)
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, st in enumerate(flat_styles):
        row_cells = t_styles.rows[row_idx + 1].cells
        bg_color = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        for i in range(5):
            row_cells[i].width = col_w_st[i]
            set_cell_shading(row_cells[i], bg_color)
            set_cell_margins(row_cells[i], top=50, bottom=50, left=80, right=80)
            row_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        p0 = row_cells[0].paragraphs[0]
        make_rtl(p0)
        r0 = p0.add_run(st["element_ar"])
        r0.font.name = "Arial"
        r0.font.size = Pt(8)
        r0.font.bold = True

        p1 = row_cells[1].paragraphs[0]
        make_rtl(p1)
        r1a = p1.add_run(st["name_ar"] + "\n")
        r1a.font.name = "Arial"
        r1a.font.size = Pt(8.5)
        r1a.font.bold = True
        r1b = p1.add_run(st["name_en"])
        r1b.font.name = "Calibri"
        r1b.font.size = Pt(8)
        r1b.font.italic = True
        r1b.font.color.rgb = MUTED_GRAY

        p2 = row_cells[2].paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r2 = p2.add_run(st["id"])
        r2.font.name = "Consolas"
        r2.font.size = Pt(7)

        p3 = row_cells[3].paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = p3.add_run(st["category"])
        r3.font.name = "Arial"
        r3.font.size = Pt(8)

        p4 = row_cells[4].paragraphs[0]
        make_rtl(p4)
        r4 = p4.add_run(st["source"])
        r4.font.name = "Arial"
        r4.font.size = Pt(7.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -----------------------------------------------------------------------
    # Section 6: Practical GIS Guide for ArcMap Desktop 10.8
    # -----------------------------------------------------------------------
    h6 = doc.add_paragraph()
    make_rtl(h6)
    h6.paragraph_format.space_before = Pt(16)
    h6.paragraph_format.space_after = Pt(6)
    r_h6 = h6.add_run("6. خطوات استخدام وتطبيق الستايلات داخل برامج GIS (ArcMap 10.8 و QGIS)")
    r_h6.font.name = "Arial"
    r_h6.font.size = Pt(14)
    r_h6.font.bold = True
    r_h6.font.color.rgb = PRIMARY

    gis_steps = [
        ("إضافة ملف الستايل الشامل إلى ArcMap Style Manager: ",
         "من القائمة العلوية في برنامج ArcMap، توجه إلى Customize -> Style Manager -> اضغط زر Styles... -> اختر Add Style to List... -> استعرض وتوجه إلى مجلد All_ArcMap_Styles_Consolidated واختر الملف الرئيسي NASA_POWER_Climate_Atlas_Master.style أو ملف العنصر المناخي المستهدف."),
        ("تطبيق الـ Color Ramp على طبقات الراستر المصنفة (Classified Symbology): ",
         "انقر بزر الفأرة الأيمن على طبقة الراستر المناخية -> Properties -> تبويب Symbology -> اختر النمط Classified -> حدد عدد الفئات (Classes: من 3 إلى 11 فئة) -> افتح القائمة المنسدلة لـ Color Ramp -> ستجد الستايلات مصنفة بوضوح: اختر الستايل الملحق بكلمة [Stepped] للحصول على شرائح لونية مصمتة ومنفصلة تماماً، أو [Smooth] للتدرج الناعم."),
        ("تطبيق الرموز على الطبقات المتجهة (Vector Polygons): ",
         "عند تصنيف طبقات مضلعات الأقاليم المناخية أو نطاقات الجفاف، انقر على رمز المضلع -> ستجد رموز [Fill Symbols] المعيارية الجاهزة بألوان الفئات وحدود رمادية خفيفة (0.4pt) جاهزة للاختيار الفوري."),
        ("استخدام الألوان الفردية [Colors] في النصوص وتنسيق الإخراج: ",
         "جميع ألوان الفئات مسجلة كألوان معتمدة، يمكنك اختيارها عند تلوين عناصر الخريطة (نصوص الليجند، خطوط الكنتور، إطارات الخريطة)."),
        ("التطبيق الفوري لخرائط الراستر عبر ملفات .clr: ",
         "من نافذة ArcToolbox افتح Data Management Tools -> Raster -> Raster Properties -> Add Colormap. في خانة Input Raster اختر الراستر المصنف، وفي خانة Input Colormap File اختر ملف .clr المقابل."),
        ("التحميل في برنامج QGIS: ",
         "انقر بزر الفأرة الأيمن على الطبقة -> Properties -> Symbology -> اضغط زر Style بالأسفل -> Load Style واختر ملف .qml من مجلد QML.")
    ]

    for g_title, g_desc in gis_steps:
        gp = doc.add_paragraph()
        make_rtl(gp)
        gp.paragraph_format.space_after = Pt(4)
        r_gt = gp.add_run("✔ " + g_title)
        r_gt.font.name = "Arial"
        r_gt.font.size = Pt(10)
        r_gt.font.bold = True
        r_gt.font.color.rgb = SECONDARY
        r_gd = gp.add_run(g_desc)
        r_gd.font.name = "Arial"
        r_gd.font.size = Pt(10)
        r_gd.font.color.rgb = TEXT_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    foot_p = doc.add_paragraph()
    make_rtl(foot_p)
    r_foot = foot_p.add_run(
        "تم إعداد وتوليد هذه الموسوعة الكارتوجرافية الشاملة لتكون المرجع الأكاديمي والمهني المتكامل لتمثيل بيانات المناخ في جمهورية مصر العربية وكافة النطاقات الجغرافية العالمية بأعلى معايير الدقة والنزاهة العلمية."
    )
    r_foot.font.name = "Arial"
    r_foot.font.size = Pt(9)
    r_foot.font.italic = True
    r_foot.font.color.rgb = MUTED_GRAY

    # Save Word Document
    doc.save(DOCX_PATH)
    print(f"Word Document generated successfully: {DOCX_PATH}")

    # Copy to all target locations
    target_locations = [
        os.path.join(STYLE_DIR, "Climate_Styles_Sources_and_References.docx"),
        os.path.join(STYLE_DIR, "01_Temperature", "Source_of_Style_and_Color", "Climate_Styles_Sources_and_References.docx"),
        os.path.join(BASE_DIR, "All_ArcMap_Styles_Consolidated", "Climate_Styles_Sources_and_References.docx"),
        os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated", "Climate_Styles_Sources_and_References.docx")
    ]
    for loc in target_locations:
        loc_dir = os.path.dirname(loc)
        if not os.path.isdir(loc_dir):
            os.makedirs(loc_dir)
        shutil.copy2(DOCX_PATH, loc)
        print(f"Copied .docx to: {loc}")

def update_csv_and_json():
    print("Updating Sources_and_Links_Catalog (.csv & .json)...")
    csv_path = os.path.join(SOURCES_DIR, "Sources_and_Links_Catalog.csv")
    json_path = os.path.join(SOURCES_DIR, "Sources_and_Links_Catalog.json")

    sources = [
        {
            "Source_ID": "ESRI_MAPPING",
            "Title_AR": "مدونة إزري: ألوان أفضل لتخريط أفضل (Better Colors for Better Mapping)",
            "Title_EN": "Better Colors for Better Mapping (Esri ArcGIS Blog)",
            "Author": "Kristian Ekenes / Esri Cartography Team",
            "Organization": "Environmental Systems Research Institute (Esri Inc.)",
            "Category_AR": "تصميم الألوان والإرشادات الكارتوجرافية لنظم المعلومات الجغرافية",
            "URL": "https://www.esri.com/arcgis-blog/products/js-api-arcgis/mapping/better-colors-for-better-mapping",
            "Scope": "All Modules (خصوصاً درجات الحرارة والراستر)",
            "Applied_Styles": "Temp_Multi_SpectralMuted; Temp_Div_TealCoral"
        },
        {
            "Source_ID": "CPT_CITY",
            "Title_AR": "أرشيف CPT-City العالمي للتدرجات اللونية المناخية والكارتوجرافية",
            "Title_EN": "cpt-city: An Archive of Colour Gradients for Cartography & Climatology",
            "Author": "J.J. Green / University of Sheffield",
            "Organization": "University of Sheffield / Generic Mapping Tools (GMT)",
            "Category_AR": "أرشيف التدرجات اللونية لعلوم الأرض والأرصاد",
            "URL": "https://phillips.shef.ac.uk/pub/cpt-city/",
            "Scope": "Temperature, Precipitation, Pressure, Relief, Bathymetry",
            "Applied_Styles": "Temp_Div_PuOr; Precip_Div_BrBG; Pres_Seq_Density"
        },
        {
            "Source_ID": "IPCC_AR6_CRAMERI",
            "Title_AR": "معايير الهيئة الحكومية الدولية المعنية بتغير المناخ (IPCC AR6) والتدرجات العلمية المحايدة إدراكياً",
            "Title_EN": "IPCC AR6 Visual Guide & Scientific Colour Maps (Fabio Crameri)",
            "Author": "Dr. Fabio Crameri / IPCC Working Group I",
            "Organization": "Intergovernmental Panel on Climate Change (IPCC) / University of Oslo",
            "Category_AR": "المعايير البصرية العلمية للتقارير المناخية الدولية",
            "URL": "https://www.fabiocrameri.ch/colourmaps/",
            "Scope": "Temperature Anomalies, Climatological Means, Climate Models (01, 11)",
            "Applied_Styles": "Temp_Div_RdBu_IPCC; Temp_Multi_Thermal_Crameri; Temp_Multi_Roma_Crameri; Temp_Div_Nuuk_Cryo; Model_Div_TempAnomaly; Model_Div_PrecipChange"
        },
        {
            "Source_ID": "COLORBREWER",
            "Title_AR": "نظام كولور بروير للكارتوجرافيا وتمايز الفئات (ColorBrewer 2.0)",
            "Title_EN": "ColorBrewer 2.0: Color Advice for Cartography",
            "Author": "Dr. Cynthia Brewer / Mark Harrower",
            "Organization": "Pennsylvania State University / National Science Foundation (NSF)",
            "Category_AR": "المعيار الأكاديمي الكارتوجرافي العالمي للخرائط الموضوعية",
            "URL": "https://colorbrewer2.org/",
            "Scope": "All Modules (Sequential, Diverging, Qualitative 3 to 11 classes)",
            "Applied_Styles": "Temp_Seq_WarmRed; Temp_Seq_AmberOrange; Temp_Seq_CoolBlue; Temp_Div_RdYlBu_Brewer; Precip_Seq_Blues; Precip_Seq_YlGnBu; Precip_Seq_BuPu"
        },
        {
            "Source_ID": "WMO_STANDARDS",
            "Title_AR": "معايير المنظمة العالمية للأرصاد الجوية (WMO-No. 306 & WMO-No. 8)",
            "Title_EN": "World Meteorological Organization Synoptic & Climatological Standards",
            "Author": "WMO Commission for Instruments and Methods of Observation (CIMO)",
            "Organization": "World Meteorological Organization (WMO) - United Nations",
            "Category_AR": "المعايير الدولية للأرصاد الجوية والمناخ",
            "URL": "https://library.wmo.int/records/item/35625-manual-on-codes",
            "Scope": "Temperature, Wind, Pressure, Cloud Cover, Rainfall Intensity (01, 02, 03, 05, 09)",
            "Applied_Styles": "Temp_Multi_WMO_Standard; Temp_Seq_FrostThreshold; Precip_Seq_Intensity_WMO; Pres_Div_WMO_MSLP; Wind_Seq_Beaufort; Cloud_Seq_Okta"
        },
        {
            "Source_ID": "NOAA_NWS",
            "Title_AR": "المعايير التشغيلية للإدارة الوطنية الأمريكية للمحيطات والغلاف الجوي (NOAA & NWS)",
            "Title_EN": "NOAA National Weather Service Operational Scales & National Blend of Models (NBM)",
            "Author": "NOAA / National Weather Service / Weather Prediction Center (WPC)",
            "Organization": "National Oceanic and Atmospheric Administration (NOAA)",
            "Category_AR": "المعايير التشغيلية للتنبؤات والرصد المناخي",
            "URL": "https://www.wpc.ncep.noaa.gov/",
            "Scope": "Temperature, Heat Index, Wind Chill, Radar Reflectivity, Hurricanes (01, 02, 05)",
            "Applied_Styles": "Temp_Multi_NOAA_NWS; Temp_Multi_NOAA_CPC; Precip_Multi_DopplerRadar; Wind_Multi_DopplerVelocity; Wind_Multi_WindChill; Wind_Multi_Hurricanes"
        },
        {
            "Source_ID": "WHO_UV_INDEX",
            "Title_AR": "المعيار الدولي الموحد لمؤشر الأشعة فوق البنفسجية (WHO / WMO / UNEP)",
            "Title_EN": "Global Solar UV Index: A Practical Guide (ISBN 92 4 159007 6)",
            "Author": "World Health Organization / WMO / UNEP / ICNIRP",
            "Organization": "World Health Organization (WHO)",
            "Category_AR": "المعايير الدولية للصحة والسلامة الإشعاعية",
            "URL": "https://www.who.int/publications/i/item/9241590076",
            "Scope": "UV Index (08_UV_Index)",
            "Applied_Styles": "UV_Standard_WHO; UV_EPA_HealthRisk; UV_ErythemalDose; UV_SummerPeak"
        },
        {
            "Source_ID": "UNEP_FAO_ARIDITY",
            "Title_AR": "معايير القحولة والتصحر الدولية (أطلس التصحر العالمي UNEP / ودليل FAO-56)",
            "Title_EN": "UNEP World Atlas of Desertification & FAO-56 Irrigation Guidelines",
            "Author": "UNEP / UNESCO / FAO (Allen, Pereira, Raes, Smith)",
            "Organization": "UN Environment Programme / Food and Agriculture Organization (FAO)",
            "Category_AR": "معايير القحولة والجفاف والهيدرولوجيا الزراعية",
            "URL": "https://wad.jrc.ec.europa.eu/",
            "Scope": "Drought & Aridity, PET, Water Deficit, Crop VPD (06, 10)",
            "Applied_Styles": "Aridity_UNEP_World; Drought_SPEI_Index; Drought_PDSI_Palmer; Aridity_SoilMoistureDeficit; Drought_ETo_Hargreaves; RH_Seq_VPD_Agricultural"
        },
        {
            "Source_ID": "GLOBAL_SOLAR_ATLAS",
            "Title_AR": "معايير أطلس الطاقة الشمسية العالمي (World Bank / ESMAP / Solargis)",
            "Title_EN": "Global Solar Atlas Standards & Benchmarks",
            "Author": "Energy Sector Management Assistance Program (ESMAP) / Solargis",
            "Organization": "World Bank Group",
            "Category_AR": "كارتوجرافيا الإشعاع الشمسي والطاقة المتجددة",
            "URL": "https://globalsolaratlas.info/",
            "Scope": "Solar Radiation (07_Solar_Radiation)",
            "Applied_Styles": "Solar_Seq_YlOrRd; Solar_Seq_ESMAP_GHI; Solar_Seq_PVOUT; Solar_Seq_DNI_Thermal; Solar_Seq_SunshineDuration"
        },
        {
            "Source_ID": "ED_HAWKINS_STRIPES",
            "Title_AR": "مبادرة خطوط الاحترار العالمي (Ed Hawkins Warming Stripes)",
            "Title_EN": "Warming Stripes Climate Visualization Initiative",
            "Author": "Prof. Ed Hawkins / University of Reading",
            "Organization": "University of Reading / National Centre for Atmospheric Science (NCAS)",
            "Category_AR": "التواصل العلمي الكارتوجرافي للتغير المناخي",
            "URL": "https://showyourstripes.info/",
            "Scope": "Climate Models & Temperature Anomalies (11_Climate_Models)",
            "Applied_Styles": "Model_Div_WarmingStripes; Model_Div_TempAnomaly"
        },
        {
            "Source_ID": "ECMWF_ERA5",
            "Title_AR": "خدمة كوبرنيكوس لتغير المناخ (ECMWF C3S / ERA5 Reanalysis)",
            "Title_EN": "Copernicus Climate Change Service & ERA5 Global Reanalysis",
            "Author": "European Centre for Medium-Range Weather Forecasts (ECMWF)",
            "Organization": "European Union / ECMWF",
            "Category_AR": "إعادة التحليل المناخي ونمذجة الغلاف الجوي",
            "URL": "https://climate.copernicus.eu/",
            "Scope": "Temperature, Precipitation, Pressure, Humidity, Models (01, 02, 03, 06, 11)",
            "Applied_Styles": "Temp_Multi_ERA5_Thermal; Precip_Multi_ERA5_Total; Model_Multi_SSPSenarios"
        },
        {
            "Source_ID": "NASA_EARTHDATA",
            "Title_AR": "نظام بيانات علوم الأرض بوكالة ناسا (NASA Earth Science Data Systems)",
            "Title_EN": "NASA Earth Science Data Systems (GPM, MODIS, AIRS, LST)",
            "Author": "NASA Earthdata / Goddard Space Flight Center",
            "Organization": "National Aeronautics and Space Administration (NASA)",
            "Category_AR": "بيانات الاستشعار عن بعد والأقمار الاصطناعية المناخية",
            "URL": "https://earthdata.nasa.gov/",
            "Scope": "Precipitation, LST, Cloud Cover, Aerosols (01, 02, 09)",
            "Applied_Styles": "Temp_Multi_NASA_LST; Temp_Div_NASA_GISTEMP; Precip_Multi_NASA_GPM; Cloud_Seq_OpticalDepth; Cloud_Multi_AOD_Aerosol"
        },
        {
            "Source_ID": "HADCRUT5_CLIMATE",
            "Title_AR": "سجلات الاحترار العالمي لمركز هادلي البريطاني (HadCRUT5 Analysis)",
            "Title_EN": "HadCRUT5 Historical Global Surface Temperature Dataset",
            "Author": "UK Met Office Hadley Centre / Climatic Research Unit (CRU)",
            "Organization": "UK Met Office / University of East Anglia",
            "Category_AR": "سجلات درجات الحرارة التاريخية العالمية",
            "URL": "https://www.metoffice.gov.uk/hadobs/hadcrut5/",
            "Scope": "Historical Temperature Anomalies (01_Temperature)",
            "Applied_Styles": "Temp_Div_HadCRUT5"
        },
        {
            "Source_ID": "KOPPEN_GEIGER",
            "Title_AR": "نظام تصنيف الأقاليم المناخية لكوبن-جيجر (Köppen-Geiger World Atlas)",
            "Title_EN": "Köppen-Geiger World Climate Classification System",
            "Author": "Wladimir Köppen / Rudolf Geiger / University of Vienna",
            "Organization": "University of Vienna / Max Planck Institute",
            "Category_AR": "التصنيف المناخي الكارتوجرافي العالمي",
            "URL": "http://koeppen-geiger.vu-wien.ac.at/",
            "Scope": "Global Thermal Regimes & Climate Classification (01, 10)",
            "Applied_Styles": "Temp_Multi_KoppenThermal; Aridity_Multi_DesertBoundaries"
        }
    ]

    with io.open(csv_path, "w", encoding="utf-8-sig") as f:
        fieldnames = ["Source_ID", "Title_AR", "Title_EN", "Author", "Organization", "Category_AR", "URL", "Scope", "Applied_Styles"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in sources:
            writer.writerow(row)
    print(f"Updated CSV: {csv_path}")

    all_elements = [{"folder": "01_Temperature", "name_en": "Temperature", "name_ar": "درجات الحرارة", "styles": gcs.TEMPERATURE_STYLES}] + gcs.OTHER_ELEMENTS
    catalog_data = {
        "metadata": {
            "title_ar": "فهرس الموسوعة الكارتوجرافية الشاملة للستايلات والتدرجات المناخية",
            "title_en": "Comprehensive Catalog of Scientific Sources & Cartographic References for Mega Climate Atlas",
            "project": "NASA POWER & Open-Meteo Climate Atlas Generator",
            "total_standards": len(sources),
            "total_styles": 125,
            "total_elements": 11,
            "class_tiers": [3, 4, 5, 6, 7, 8, 9, 10, 11],
            "total_color_ramps": 2250,
            "total_colors": 875,
            "total_fill_symbols": 875
        },
        "standards": sources,
        "elements_and_styles": []
    }

    for el in all_elements:
        el_entry = {
            "folder": el["folder"],
            "name_en": el.get("name_en", el["folder"]),
            "name_ar": el.get("name_ar", el["folder"]),
            "styles_count": len(el["styles"]),
            "styles": []
        }
        for s in el["styles"]:
            el_entry["styles"].append({
                "id": s["id"],
                "name_en": s["name_en"],
                "name_ar": s["name_ar"],
                "category": s["category"],
                "source": s["source"],
                "classes": s["classes"]
            })
        catalog_data["elements_and_styles"].append(el_entry)

    with io.open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
    print(f"Updated JSON: {json_path}")

    for f_name, src_p in [("Sources_and_Links_Catalog.csv", csv_path), ("Sources_and_Links_Catalog.json", json_path)]:
        shutil.copy2(src_p, os.path.join(BASE_DIR, "All_ArcMap_Styles_Consolidated", f_name))
        shutil.copy2(src_p, os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated", f_name))

if __name__ == "__main__":
    build_docx()
    update_csv_and_json()
    print("\nMega Edition Sources Documentation & Word Document successfully created!")
