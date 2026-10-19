# -*- coding: utf-8 -*-
"""
Generate Comprehensive Climatological Cartography Decision Guide & Seasonal Styles Brochure
Word Document (.docx) using python-docx.
"""
import os
import sys
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
CONSOLIDATED_1 = os.path.join(BASE_DIR, "All_ArcMap_Styles_Consolidated")
CONSOLIDATED_2 = os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated")
DOCX_FILENAME = "Seasonal_Climate_Styles_Decision_Guide.docx"
TARGET_DOCX = os.path.join(STYLE_DIR, DOCX_FILENAME)

def set_cell_shading(cell, color_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D0D7DE", sz="4", val="single"):
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

def add_callout(doc, title_text, body_text, border_color="1B365D", bg_color="F0F4F8"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(7.0)
    set_cell_shading(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    # Left thick border
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:right w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)

    p = cell.paragraphs[0]
    make_rtl(p)
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(title_text + "\n")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(11)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(27, 54, 93)

    r_body = p.add_run(body_text)
    r_body.font.name = "Arial"
    r_body.font.size = Pt(10)
    r_body.font.color.rgb = RGBColor(34, 34, 34)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(4)
    p_after.paragraph_format.space_after = Pt(4)

def build_decision_guide():
    print("Generating Climatological Decision Guide Word Document (.docx)...")
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    PRIMARY = RGBColor(27, 54, 93)     # Deep Navy
    SECONDARY = RGBColor(43, 91, 132)  # Slate Blue
    ACCENT = RGBColor(180, 40, 20)     # Warm Crimson
    TEXT_DARK = RGBColor(34, 34, 34)   # Charcoal
    FOREST_GREEN = RGBColor(30, 107, 56)

    # Document Header / Banner Box
    title_p = doc.add_paragraph()
    make_rtl(title_p)
    title_p.paragraph_format.space_before = Pt(8)
    title_p.paragraph_format.space_after = Pt(2)
    run_t = title_p.add_run("الدليل الكارتوجرافي الشامل لحسم القرارات واختيار التدرجات اللونية الفصصلية")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(20)
    run_t.font.bold = True
    run_t.font.color.rgb = PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sub_p.paragraph_format.space_after = Pt(6)
    run_sub = sub_p.add_run("Climatological Cartography Decision Guide & Seasonal Styles Brochure (Mega Edition)")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(11.5)
    run_sub.font.color.rgb = SECONDARY

    meta_p = doc.add_paragraph()
    make_rtl(meta_p)
    meta_p.paragraph_format.space_after = Pt(14)
    r_meta = meta_p.add_run("المشروع: أطلس المناخ الشامل (NASA POWER & Open-Meteo)  |  إعداد وتطوير: أحمد إبراهيم (@ahmadibrahim4geo)  |  الإصدار المعتمد 2026")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(120, 120, 120)

    # ---------------------------------------------------------------------------
    # Brochure Executive Summary Callout
    # ---------------------------------------------------------------------------
    add_callout(
        doc,
        "📌 بروشور تعريفي: حل معضلة الحيرة الكارتوجرافية بين الفصول (Seasonal Cartographic Dilemma)",
        "عند بناء أطلس المناخ وتصميم خرائط العناصر المناخية عبر فصول السنة المختلفة (صيف، شتاء، ربيع، خريف، وسنوي)، يقع الباحثون ومصممو الخرائط دائماً في حيرة كارتوجرافية كبرى:\n"
        "• هل نستخدم نفس التدرج اللوني لجميع الفصول؟\n"
        "• أم نخصص تدرجاً بارداً للشتاء وتدرجاً دافئاً للصيف وتدرجاً معتدلاً للربيع والخريف؟\n\n"
        "يقدم هذا الدليل المعتمد دولياً (استناداً لمعايير IPCC و WMO و Cynthia Brewer و Esri) حل هذا اللبس نهائياً عبر تأصيل القواعد العلمية الصارمة، وتقديم الجداول المرجعية التفصيلية لكل عنصر مناخي، وتدشين 41 قاعدة ستايل فرعية متخصصة ومستقلة بجوار الستايلات الأصلية لتوفير المرونة الكارتوجرافية المطلقة.",
        border_color="1B365D",
        bg_color="F4F7FA"
    )

    # ---------------------------------------------------------------------------
    # Section 1: The Golden Cartographic Rules
    # ---------------------------------------------------------------------------
    h1 = doc.add_paragraph()
    make_rtl(h1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    r_h1 = h1.add_run("1. التأصيل العلمي للقاعدة الذهبية الكارتوجرافية (حسم الحيرة)")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(14)
    r_h1.font.bold = True
    r_h1.font.color.rgb = PRIMARY

    p_intro = doc.add_paragraph()
    make_rtl(p_intro)
    p_intro.paragraph_format.line_spacing = 1.2
    p_intro.paragraph_format.space_after = Pt(8)
    r_intro = p_intro.add_run(
        "في الكارتوجرافيا المناخية الحديثة، ينقسم القرار التصميمي إلى مدرستين رئيستين وفقاً لطبيعة عرض الخريطة والهدف الإدراكي للقارئ:"
    )
    r_intro.font.name = "Arial"
    r_intro.font.size = Pt(10.5)
    r_intro.font.color.rgb = TEXT_DARK

    # School 1
    p_s1 = doc.add_paragraph()
    make_rtl(p_s1)
    p_s1.paragraph_format.space_after = Pt(4)
    r_s1_t = p_s1.add_run("✔ أولاً: المدرسة الموحدة للمقارنة البصرية المباشرة (Unified Comparative Approach)")
    r_s1_t.font.name = "Arial"
    r_s1_t.font.size = Pt(11.5)
    r_s1_t.font.bold = True
    r_s1_t.font.color.rgb = SECONDARY

    p_s1_b = doc.add_paragraph()
    make_rtl(p_s1_b)
    p_s1_b.paragraph_format.line_spacing = 1.2
    p_s1_b.paragraph_format.space_after = Pt(8)
    r_s1_b = p_s1_b.add_run(
        "• متى يكون هذا الخيار إلزامياً؟ عندما تُعرض خرائط الفصول الأربعة في لوحة أطلس واحدة مجمعة (لوحة رباعية 4 في 1) أو في صفحات متقابلة للمقارنة المكانية والزمنية الفورية.\n"
        "• العلة والأساس العلمي: إذا استخدمت درجات حمراء للصيف ودرجات زرقاء للشتاء، فإن نفس الدرجة اللونية ستعبر عن قيمتين مختلفتين تماماً، مما يُحدث خداعاً وتضليلاً بصرياً وإدراكياً فادحاً (Cognitive Distortion). فالقارئ يفترض لا شعورياً أن اللون المتطابق يعبر عن نفس القيمة الفيزيائية.\n"
        "• الإلزام الكارتوجرافي: توحيد التدرج اللوني ومقياس الفئات وتثبيت الفواصل (Fixed Breakpoints)، بحيث تظهر خريطة الشتاء مائلة تلقائياً للأزرق والأخضر، وخريطة الصيف مائلة للأحمر والأصفر على نفس السلم المعياري دون أدنى لبس."
    )
    r_s1_b.font.name = "Arial"
    r_s1_b.font.size = Pt(10)
    r_s1_b.font.color.rgb = TEXT_DARK

    # School 2
    p_s2 = doc.add_paragraph()
    make_rtl(p_s2)
    p_s2.paragraph_format.space_after = Pt(4)
    r_s2_t = p_s2.add_run("✔ ثانياً: مدرسة التباين النسبي والتخصيص الفصلي (Seasonal Dynamic Contrast Approach)")
    r_s2_t.font.name = "Arial"
    r_s2_t.font.size = Pt(11.5)
    r_s2_t.font.bold = True
    r_s2_t.font.color.rgb = ACCENT

    p_s2_b = doc.add_paragraph()
    make_rtl(p_s2_b)
    p_s2_b.paragraph_format.line_spacing = 1.2
    p_s2_b.paragraph_format.space_after = Pt(8)
    r_s2_b = p_s2_b.add_run(
        "• متى يكون هذا الخيار هو الأفضل كارتوجرافياً؟ عندما تكون الخريطة مستقلة بذاتها في صفحة كاملة خاصة بفصل محدد (مثل خريطة درجات حرارة الشتاء، أو تقرير عواصف الخريف المطرية).\n"
        "• المشكلة الفيزيائية المعالجة: في فصل الشتاء أو فصل الصيف، يكون المدى الحراري داخل الدولة أو منطقة الدراسة ضيقاً جداً (مثلاً درجات حرارة الشتاء تتراوح كلها بين 10°C و 18°C). لو طبقنا التدرج العام الموحد (الذي يمتد من 0°C إلى 45°C)، فستظهر خريطة الشتاء كلها بلون أزرق مصمت باهت، وتختفي الفروق المكانية الدقيقة بين السواحل والداخل أو المرتفعات والوديان!\n"
        "• الحل الكارتوجرافي: استخدام تدرج فصلي متخصص مصمم وموزع على المدى الفصلي الفعلي (مثل تدرج أزرق متدرج للشتاء يظهر الفروق بين الـ 10° والـ 18° عبر 7 فئات ناصعة، وتدرج أحمر/عنبري للصيف يظهر التباين بين الـ 30° والـ 45° بوضوح فائق)."
    )
    r_s2_b.font.name = "Arial"
    r_s2_b.font.size = Pt(10)
    r_s2_b.font.color.rgb = TEXT_DARK

    # Summary Table of the Golden Rule
    t_rule = doc.add_table(rows=3, cols=4)
    t_rule.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_rule)

    hdr_r = ["طبيعة الإخراج والعرض", "الاستراتيجية المعتمدة", "طريقة التدرج اللوني", "حالة الفواصل والفئات"]
    widths_r = [Inches(1.8), Inches(1.8), Inches(1.8), Inches(1.6)]
    for i, title in enumerate(hdr_r):
        cell = t_rule.rows[0].cells[i]
        cell.width = widths_r[i]
        set_cell_shading(cell, "1B365D")
        set_cell_margins(cell, 100, 100, 100, 100)
        p = cell.paragraphs[0]
        make_rtl(p)
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_r = [
        ("لوحة مجمعة (4 فصول في صفحة واحدة / مقارنة)", "المدرسة الموحدة (Unified Scale)", "نفس التدرج اللوني لجميع الفصول إجبارياً", "تثبيت الفواصل (Fixed Breaks) لجميع الخرائط"),
        ("خريطة مستقلة منفردة لفصل بذاته (تقرير/بحث)", "التمايز النسبي (Seasonal Contrast)", "تخصيص التدرج اللوني لطبيعة الفصل (بارد/دافئ)", "إعادة ضبط الفواصل على مدى بيانات الفصل")
    ]
    for row_idx, row in enumerate(data_r):
        bg = "F4F7FA" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(row):
            cell = t_rule.rows[row_idx + 1].cells[col_idx]
            cell.width = widths_r[col_idx]
            set_cell_shading(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            make_rtl(p)
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(9)
            if col_idx == 0:
                r.font.bold = True

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(8)

    # ---------------------------------------------------------------------------
    # Section 2: Detailed Decision Tables across all 11 Climate Elements
    # ---------------------------------------------------------------------------
    h2 = doc.add_paragraph()
    make_rtl(h2)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r_h2 = h2.add_run("2. الجداول المرجعية الشاملة لحسم الاختيارات في كافة العناصر المناخية")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(14)
    r_h2.font.bold = True
    r_h2.font.color.rgb = PRIMARY

    element_tables_data = [
        # 1. Temperature
        {
            "elem_title": "العنصر 01: درجات الحرارة والشذوذ والحرارة المحسوسة (Temperature)",
            "rows": [
                ("المتوسط السنوي العام", "Temp_Div_RdYlBu_Brewer", "كولور بروير القياسي المتوازن", "01_Temp_Annual_Mean.style", "كولور بروير / سينثيا بروير", "كحلي للبرودة وأحمر للحرارة بمركز أصفر دافئ محايد يمنع اختفاء الورق"),
                ("الصيف والحرارة العظمى (مستقل)", "Temp_Seq_WarmRed", "أحمر مرجاني متتابع دافئ", "01_Temp_Summer_Max.style", "ColorBrewer Reds / NOAA", "تدرج أحمر ناصع يبرز تباينات الطاقة الحرارية والمناطق الأشد حرارة"),
                ("الشتاء والحرارة الصغرى (مستقل)", "Temp_Seq_CoolBlue", "أزرق شتوي متدرج", "01_Temp_Winter_Min.style", "ColorBrewer Blues / WMO", "يتدرج من الثلجي الفاتح للكحلي العميق لإبراز تباينات البرودة بوضوح"),
                ("الربيع والخريف (انتقالي)", "Temp_Multi_SpectralMuted", "طيف إزري الناعم المريح", "01_Temp_Spring_Autumn.style", "Esri Better Colors Mapping", "ألوان طيفية معتدلة غير فاقعة تعبر عن اعتدال الفصول الانتقالية"),
                ("التدرج الموحد لجميع الفصول", "Temp_Multi_Thermal_Crameri", "التدرج العلمي المحايد إدراكياً", "01_Temp_Unified_All_Seasons.style", "Fabio Crameri / IPCC AR6", "تدرج باتلو المعتمد دولياً للمقارنة البصرية دون تشويه أو حدود زائفة"),
                ("الحرارة المحسوسة والإجهاد الحيوي", "Temp_Multi_SteadmanApparent", "الحرارة المحسوسة لستيدمان", "01_Temp_Heat_Index.style", "NOAA NWS / Steadman", "فئات بيومناخية معيارية من الأخضر (راحة) للأصفر فالبرتقالي فالقرمزي")
            ]
        },

        # 2. Precipitation
        {
            "elem_title": "العنصر 02: الأمطار والتساقط التراكمي ورادار الطقس (Precipitation)",
            "rows": [
                ("التراكم السنوي العام", "Precip_Seq_YlGnBu", "أصفر - أخضر - أزرق قياسي", "02_Precip_Annual_Total.style", "ColorBrewer YlGnBu / NOAA", "المعيار العالمي: أصفر للجفاف وأخضر للمتوسط وأزرق كحلي للأمطار الغزيرة"),
                ("أمطار الشتاء والسيول (مستقل)", "Precip_Seq_Blues", "أزرق مطري عميق للسيول", "02_Precip_Winter_Rain.style", "NOAA NWC Flash Flood", "يعزل الكتل المطرية الشتوية الغزيرة ومسارات المنخفضات الجوية"),
                ("أمطار الصيف والرياح الموسمية", "Precip_Seq_BuPu", "أزرق إلى أرجواني موسمي", "02_Precip_Summer_Monsoon.style", "WMO Monsoon Climatology", "مخصص للهطول الصيفي المداري وحزام التقارب الاستوائي ITCZ"),
                ("عواصف الربيع والخريف الرعدية", "Precip_Multi_DopplerRadar", "مقياس رادار الطقس الوطني", "02_Precip_Spring_Autumn_Storms.style", "NOAA ROC Doppler dBZ", "يوضح بؤر السحب الركامية والتقلبات المطرية الفجائية في الفصول الانتقالية"),
                ("شذوذ الأمطار ومؤشر الجفاف SPI", "Precip_Div_BrBG", "بني (جفاف) - أبيض - مخضر (وفرة)", "02_Precip_Drought_Anomaly_SPI.style", "WMO Commission Agrometeorology", "تدرج ثنائي الاتجاه بمركز محايد يوضح الانحراف السالب والموجب بدقة")
            ]
        },

        # 3. Sea Level Pressure
        {
            "elem_title": "العنصر 03: ضغط مستوى سطح البحر والأعاصير (Sea Level Pressure)",
            "rows": [
                ("المستوى السنوي والمعياري", "Pres_Div_WMO_MSLP", "المعيار الدولي لسطح البحر", "03_Pres_Annual_MSL_Standard.style", "WMO-No. 306 MSL Standard", "ثنائي الاتجاه حول 1013.25 مليبار (بنفسجي للمنخفض وأخضر للمرتفع)"),
                ("الشتاء (المرتفعات السيبيرية)", "Pres_Div_SiberianAnticyclone", "المرتفع السيبيري ومنخفضات المتوسط", "03_Pres_Winter_Siberian_High.style", "Synoptic Climatology Eurasia", "يبرز سيطرة المرتفعات القارية الباردة مقابل المنخفضات المتوسطية"),
                ("الصيف (المنخفضات الحرارية)", "Pres_Synoptic_Subtropical", "المرتفع شبه المداري والمنخفض الحراري", "03_Pres_Summer_Subtropical_Low.style", "Hadley Circulation Pressure", "يوضح تمدد المنخفضات الموسمية الحارة مقارنة بالمرتفع الآزوري")
            ]
        },

        # 4. Surface Pressure
        {
            "elem_title": "العنصر 04: الضغط الجوي السطحي والهبسومتري (Surface Pressure)",
            "rows": [
                ("الضغط السطحي التضاريسي", "SPres_Seq_Hypsometric", "الضغط السطحي الهبسومتري", "04_SPres_Hypsometric_Terrain.style", "ICAO Standard Atmosphere", "يعكس انخفاض الضغط الجوي الفعلي بدقة مع الارتفاع والتضاريس"),
                ("المنخفضات والهضاب الحادة", "SPres_Seq_ValleyBasin", "الضغط السطحي للمنخفضات العميقة", "04_SPres_Basin_Plateau_Extreme.style", "Dead Sea & Qattara Studies", "مخصص لإبراز الضغط في المنخفضات (كالقطارة) والهضاب الشاهقة")
            ]
        },

        # 5. Wind
        {
            "elem_title": "العنصر 05: سرعة وعواصف وطاقة الرياح (Wind Speed & Direction)",
            "rows": [
                ("السرعة السنوية والعامة", "Wind_Seq_Beaufort", "مقياس بوفورت الدولي للرياح", "05_Wind_Annual_Beaufort.style", "WMO-No. 306 Beaufort Scale", "أخضر للنسيم الهادئ $\\rightarrow$ أصفر $\\rightarrow$ برتقالي $\\rightarrow$ أحمر للرياح العاصفة"),
                ("رياح الشتاء والعواصف البحرية", "Wind_Seq_MarineGale", "الأنواء البحرية والرياح العاتية", "05_Wind_Winter_Gales_Chill.style", "National Data Buoy Center", "يبرز شدة الرياح الشتوية وتأثير تبريد الرياح (Wind Chill) البحري"),
                ("رياح الربيع وعواصف الخماسين", "Wind_Multi_KhamsinDust", "عواصف الخماسين الغبارية", "05_Wind_Spring_Khamsin_Dust.style", "MENA Dust Climatology", "تدرج رملي بني-كهرماني يعكس طابع العواصف الترابية وموجات الغبار"),
                ("نسيم الصيف الساحلي", "Wind_Seq_ThermalBreeze", "نسيم البر والبحر اليومي", "05_Wind_Summer_Thermal_Breeze.style", "Boundary Layer Meteorology", "تدرج ناعم يبرز الفروق الدقيقة في سرعات الرياح الساحلية صيفاً")
            ]
        },

        # 6. Relative Humidity
        {
            "elem_title": "العنصر 06: الرطوبة النسبية وبخار الماء (Relative Humidity)",
            "rows": [
                ("السنوي والمقارنات العامة", "RH_Seq_YlGnBu", "الرطوبة السطحية من الجفاف للتشبع", "06_Humidity_Annual_Mean.style", "ColorBrewer YlGnBu", "التدرج الكلاسيكي: أصفر للجفاف وأخضر للمعتدل وأزرق كحلي للتشبع"),
                ("رطوبة الصيف والإجهاد الخانق", "RH_Multi_WBGT_Stress", "مؤشر البصيلة الرطبة للإجهاد", "06_Humidity_Summer_Stress_WBGT.style", "ISO 7243 / OSHA Heat Stress", "يوضح خطورة تضافر الرطوبة العالية مع الحرارة على كفاءة التعرق البشري"),
                ("رطوبة الشتاء وأحزمة الضباب", "RH_Seq_FogSaturation", "تشبع الضباب والندى الساحلي", "06_Humidity_Winter_Fog_Saturation.style", "Aviation Surface Observations", "يركز على الفئات العليا (70% - 100%) لعزل أحزمة الضباب الصباحي"),
                ("تقلبات الربيع والخريف الجافة", "RH_Div_DewPointDepression", "فرق الحرارة ونقطة الندى", "06_Humidity_Transitional_Depression.style", "WMO Radiosonde Standards", "يوضح مدى اقتراب الهواء من التشبع أثناء الكتل الخماسينية والبحرية")
            ]
        },

        # 7. Solar Radiation
        {
            "elem_title": "العنصر 07: الإشعاع الشمسي والطاقة الكلية (Solar Radiation)",
            "rows": [
                ("السنوي والتراكمي العام", "Solar_Seq_YlOrRd", "الإشعاع الشمسي التراكمي", "07_Solar_Annual_GHI_ESMAP.style", "World Bank ESMAP / Solargis", "أصفر $\\rightarrow$ برتقالي $\\rightarrow$ أحمر قاني؛ المعيار المعتمد للطاقة الشمسية"),
                ("الصيف والذروة الإشعاعية", "Solar_Seq_DNI_Thermal", "الإشعاع المباشر المركز DNI", "07_Solar_Summer_DNI_Thermal.style", "NREL Solar Database NSRDB", "يبرز تمايز المناطق فائقة الإشعاع المباشر الملائمة لمحطات الطاقة الحرارية"),
                ("الشتاء وساعات السطوع المشتت", "Solar_Seq_SunshineDuration", "ساعات السطوع الشمسي الفعلي", "07_Solar_Winter_Diffuse_Sunshine.style", "WMO Sunshine Duration", "يبرز ساعات الإشراق اليومية وتشتت الضوء في الأيام الغائمة شتاءً"),
                ("الإشعاع الفعال زراعياً", "Solar_Seq_PAR_Agronomy", "الإشعاع الفعال في البناء الضوئي", "07_Solar_Spring_Autumn_Agronomy.style", "Agrometeorology Crop Scale", "يقيس طاقة الطيف الضوئي الفعالة لنمو المحاصيل في الفصول الزراعية")
            ]
        },

        # 8. UV Index
        {
            "elem_title": "العنصر 08: مؤشر الأشعة فوق البنفسجية الصحي (UV Index)",
            "rows": [
                ("المعيار الدولي الإلزامي (كل الفصول)", "UV_Standard_WHO", "معيار منظمة الصحة العالمية", "08_UV_Annual_WHO_Standard.style", "WHO / WMO / UNEP Standard", "قاعدة ملزمة: أخضر (منخفض) $\\rightarrow$ أصفر $\\rightarrow$ برتقالي $\\rightarrow$ أحمر $\\rightarrow$ بنفسجي"),
                ("ذروة الصيف والظهيرة الحارقة", "UV_SummerPeak", "ذروة الأشعة فوق البنفسجية الصيفية", "08_UV_Summer_Peak_Extreme.style", "Desert UV Monitoring", "يركز على فئات الخطر الشديد والمتطرف التي تتجاوز مؤشر 11 صيفاً"),
                ("الشتاء والتعرض الشمسي الآمن", "UV_Seq_VitaminDSynthesis", "النطاق الآمن لتكوين فيتامين د", "08_UV_Winter_Safe_Synthesis.style", "Photobiology & Endocrine Soc.", "يبرز الفئات المنخفضة والمعتدلة الآمنة للبناء الحيوي دون حروق")
            ]
        },

        # 9. Cloud Cover
        {
            "elem_title": "العنصر 09: الغطاء السحابي ونقاء السماء (Cloud Cover)",
            "rows": [
                ("السنوي ومقياس الأوكتا العالمي", "Cloud_Seq_Okta", "مقياس الأوكتا العالمي للسحب", "09_Cloud_Annual_Okta_Fraction.style", "WMO International Cloud Atlas", "من الأزرق السماوي الصافي (0 أوكتا) إلى الأبيض والرمادي الداكن (8 أوكتا)"),
                ("الشتاء والسحب الطبقية والضباب", "Cloud_Seq_LowCloudFog", "السحب المنخفضة وحزام الضباب", "09_Cloud_Winter_Low_Fog.style", "Aviation Fog & Ceiling Hazard", "يميز سحب الشتاء الطبقية المنخفضة وعوائق الرؤية الأفقية بدقة"),
                ("الصيف والربيع والسحب الركامية", "Cloud_Multi_ConvectiveTops", "القمم الركامية المخترقة والهباء", "09_Cloud_Summer_Convective_Aerosol.style", "NASA Convective Storm Research", "يوضح عواصف السحب الركامية وبؤر الهباء الجوي والغبار العالق")
            ]
        },

        # 10. Drought and Aridity
        {
            "elem_title": "العنصر 10: مؤشرات الجفاف والقحولة والبخر-نتح (Drought and Aridity)",
            "rows": [
                ("القحولة السنوية (دي مارتون/UNEP)", "Aridity_UNEP_World", "مؤشر القحولة العالمي لأطلس التصحر", "10_Aridity_Annual_UNEP_DeMartonne.style", "UNEP World Desertification", "من البني المحروق (شديد القحولة) إلى الأخضر الزمردي والأزرق (رطب)"),
                ("البخر-نتح والطلب التبخري الصيفي", "Drought_ETo_Hargreaves", "البخر-نتح المرجعي بهارجريفز", "10_Drought_Summer_PET_Hargreaves.style", "FAO-56 Irrigation Paper", "تدرج تصاعدي يعكس الارتفاع الحاد في فقد المياه صيفاً بالملم/يوم"),
                ("العجز المائي ومؤشر بالمر SPEI", "Drought_SPEI_Index", "مؤشر الجفاف والتبخر المعياري", "10_Drought_Water_Balance_SPEI.style", "Global SPEI Drought Monitor", "ثنائي الاتجاه: بني للعجز المائي الشديد وأزرق للفائض المائي والرطوبة"),
                ("زحف الرمال وتدهور الواحات", "Drought_Multi_DesertBoundaries", "زحف الكثبان وتدهور الأطراف", "10_Drought_Desert_Encroachment.style", "UNCCD Global Land Outlook", "يبرز هشاشة وتدهور أطراف الواحات والأراضي الزراعية الصحراوية")
            ]
        },

        # 11. Climate Models
        {
            "elem_title": "العنصر 11: نماذج التغير المناخي والسيناريوهات (Climate Models)",
            "rows": [
                ("شذوذ الاحترار وخطوط ريدينج", "Model_Div_WarmingStripes", "شرائط الاحترار العالمي لإد هوكينز", "11_Model_Temp_Warming_Stripes.style", "Prof. Ed Hawkins / Univ. Reading", "التدرج العالمي الشهير: خطوط زرقاء للسنوات الباردة وحمراء للسنوات الدافئة"),
                ("تغير الأمطار والظواهر القصوى", "Model_Div_PrecipChange", "نسبة التغير المتوقعة في الأمطار", "11_Model_Precip_Change_Extremes.style", "IPCC WG1 Interactive Atlas", "بني للمناطق المتوقع انخفاض أمطارها وأزرق للمناطق المتوقع زيادة هطولها"),
                ("مسارات التطور المشتركة SSPs", "Model_Multi_SSPSenarios", "سيناريوهات مسارات التطور SSP1-5", "11_Model_SSP_Scenarios_Multi.style", "IPCC AR6 Cross-Working Group", "الألوان المعيارية لسيناريوهات المستقبل من التنمية المستدامة للوقود الأحفوري")
            ]
        }
    ]

    for sec_data in element_tables_data:
        h_el = doc.add_paragraph()
        make_rtl(h_el)
        h_el.paragraph_format.space_before = Pt(12)
        h_el.paragraph_format.space_after = Pt(4)
        r_hel = h_el.add_run(sec_data["elem_title"])
        r_hel.font.name = "Arial"
        r_hel.font.size = Pt(12)
        r_hel.font.bold = True
        r_hel.font.color.rgb = SECONDARY

        t_el = doc.add_table(rows=len(sec_data["rows"]) + 1, cols=6)
        t_el.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t_el)

        headers_el = ["الحالة / المؤشر الفصلي", "كود الستايل (ID)", "اسم الستايل بالعربية", "ملف الستايل الفرعي (.style)", "المرجعية الدولية", "الخصائص الكارتوجرافية"]
        widths_el = [Inches(1.2), Inches(1.3), Inches(1.3), Inches(1.2), Inches(1.0), Inches(1.0)]

        for i, title in enumerate(headers_el):
            cell = t_el.rows[0].cells[i]
            cell.width = widths_el[i]
            set_cell_shading(cell, "1B365D")
            set_cell_margins(cell, 80, 80, 60, 60)
            p = cell.paragraphs[0]
            make_rtl(p)
            r = p.add_run(title)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

        for row_idx, r_data in enumerate(sec_data["rows"]):
            bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
            for col_idx, val in enumerate(r_data):
                cell = t_el.rows[row_idx + 1].cells[col_idx]
                cell.width = widths_el[col_idx]
                set_cell_shading(cell, bg)
                set_cell_margins(cell, 60, 60, 60, 60)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                make_rtl(p)
                r = p.add_run(val)
                r.font.name = "Arial"
                r.font.size = Pt(8)
                if col_idx in [0, 2]:
                    r.font.bold = True
                if col_idx == 1:
                    r.font.name = "Consolas"
                    r.font.size = Pt(7.5)
                    r.font.color.rgb = RGBColor(180, 40, 20)

        p_el_sp = doc.add_paragraph()
        p_el_sp.paragraph_format.space_before = Pt(4)

    # ---------------------------------------------------------------------------
    # Section 3: The 41 Sub-Styles Architecture Catalog
    # ---------------------------------------------------------------------------
    h3 = doc.add_paragraph()
    make_rtl(h3)
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    r_h3 = h3.add_run("3. كتالوج منظومة الستايلات الفرعية الجديدة المتخصصة (41 قاعدة .style جديدة)")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(14)
    r_h3.font.bold = True
    r_h3.font.color.rgb = PRIMARY

    p_sub_intro = doc.add_paragraph()
    make_rtl(p_sub_intro)
    p_sub_intro.paragraph_format.line_spacing = 1.2
    p_sub_intro.paragraph_format.space_after = Pt(8)
    r_si = p_sub_intro.add_run(
        "استجابة مباشرة لاحتياجات العمل الاحترافي وسهولة الوصول الفوري داخل ArcMap، قمنا بإنشاء وتدشين "
        "41 قاعدة بيانات ستايل فرعية جديدة مخصصة بالكامل (.style)، ووضعها مباشرة داخل المجلد الخاص بكل عنصر بجوار الستايل الأصلي الشامل، "
        "مع نسخها تلقائياً إلى مجلد الستايلات الموحد All_ArcMap_Styles_Consolidated. "
        "كل ملف من هذه الملفات يحتوي على التدرجات بفئاتها الـ 9 الكاملة (3 إلى 11 فئة) بنمطي Stepped و Smooth، "
        "مع الألوان المسماة ورموز المضلعات المغلقة."
    )
    r_si.font.name = "Arial"
    r_si.font.size = Pt(10.5)
    r_si.font.color.rgb = TEXT_DARK

    substyles_catalog = [
        ("01_Temperature", "01_Temp_Annual_Mean.style", "المتوسط السنوي لدرجات الحرارة", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("01_Temperature", "01_Temp_Summer_Max.style", "فصل الصيف والحرارات العظمى والموجات الحارة", "5 ستايلات", "90 Ramps | 35 Colors"),
        ("01_Temperature", "01_Temp_Winter_Min.style", "فصل الشتاء والحرارات الصغرى والصقيع", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("01_Temperature", "01_Temp_Spring_Autumn.style", "الفصول الانتقالية (الربيع والخريف)", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("01_Temperature", "01_Temp_Unified_All_Seasons.style", "التدرج الموحد لجميع الفصول (مقارنة بصرية)", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("01_Temperature", "01_Temp_Heat_Index.style", "مؤشر الحرارة المحسوسة والإجهاد الحراري", "2 ستايل", "36 Ramps | 14 Colors"),
        ("02_Precipitation", "02_Precip_Annual_Total.style", "التراكم السنوي العام للأمطار", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("02_Precipitation", "02_Precip_Winter_Rain.style", "أمطار الشتاء والسيول والثلوج", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("02_Precipitation", "02_Precip_Summer_Monsoon.style", "أمطار الصيف والرياح الموسمية المدارية", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("02_Precipitation", "02_Precip_Spring_Autumn_Storms.style", "عواصف الفصول الانتقالية ورادار الطقس", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("02_Precipitation", "02_Precip_Drought_Anomaly_SPI.style", "شذوذ الأمطار ومؤشرات الجفاف الهيدرولوجي", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("03_Sea_Level_Pressure", "03_Pres_Annual_MSL_Standard.style", "ضغط مستوى سطح البحر القياسي والميكروبار", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("03_Sea_Level_Pressure", "03_Pres_Winter_Siberian_High.style", "المرتفع السيبيري الشتوي ومنخفضات المتوسط", "2 ستايل", "36 Ramps | 14 Colors"),
        ("03_Sea_Level_Pressure", "03_Pres_Summer_Subtropical_Low.style", "المنخفضات الحرارية الصيفية وحزام الضغط", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("04_Surface_Pressure", "04_SPres_Hypsometric_Terrain.style", "الضغط السطحي الهبسومتري والتضاريسي", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("04_Surface_Pressure", "04_SPres_Basin_Plateau_Extreme.style", "الضغط السطحي للمنخفضات والهضاب الحادة", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("05_Wind", "05_Wind_Annual_Beaufort.style", "سرعة الرياح وفق مقياس بوفورت وكثافة الطاقة", "2 ستايل", "36 Ramps | 14 Colors"),
        ("05_Wind", "05_Wind_Winter_Gales_Chill.style", "الرياح الشتوية العاتية وتبريد الرياح البحري", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("05_Wind", "05_Wind_Spring_Khamsin_Dust.style", "عواصف الخماسين الربيعية والغبار الصحراوي", "2 ستايل", "36 Ramps | 14 Colors"),
        ("05_Wind", "05_Wind_Summer_Thermal_Breeze.style", "نسيم البر والبحر ودورة الرياح الصيفية", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("06_Relative_Humidity", "06_Humidity_Annual_Mean.style", "المتوسط السنوي للرطوبة وبخار الماء", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("06_Relative_Humidity", "06_Humidity_Summer_Stress_WBGT.style", "الإجهاد الرطب الصيفي وعجز ضغط البخار", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("06_Relative_Humidity", "06_Humidity_Winter_Fog_Saturation.style", "أحزمة الضباب الشتوي ونقطة الندى", "2 ستايل", "36 Ramps | 14 Colors"),
        ("06_Relative_Humidity", "06_Humidity_Transitional_Depression.style", "تقلبات الرطوبة وانخفاض نقطة الندى ربيعاً", "2 ستايل", "36 Ramps | 14 Colors"),
        ("07_Solar_Radiation", "07_Solar_Annual_GHI_ESMAP.style", "الإشعاع الشمسي الأفقي الكلي والكهروضوئي", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("07_Solar_Radiation", "07_Solar_Summer_DNI_Thermal.style", "ذروة الإشعاع المباشر المركز صيفاً DNI", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("07_Solar_Radiation", "07_Solar_Winter_Diffuse_Sunshine.style", "ساعات السطوع الشتوي والإشعاع المشتت", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("07_Solar_Radiation", "07_Solar_Spring_Autumn_Agronomy.style", "الإشعاع الشمسي الفعال في البناء الضوئي", "2 ستايل", "36 Ramps | 14 Colors"),
        ("08_UV_Index", "08_UV_Annual_WHO_Standard.style", "المعيار الصحي لمنظمة الصحة العالمية", "2 ستايل", "36 Ramps | 14 Colors"),
        ("08_UV_Index", "08_UV_Summer_Peak_Extreme.style", "ذروة الأشعة فوق البنفسجية الحارقة صيفاً", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("08_UV_Index", "08_UV_Winter_Safe_Synthesis.style", "النطاق الشمسي الآمن وتخليق فيتامين د", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("09_Cloud_Cover", "09_Cloud_Annual_Okta_Fraction.style", "مقياس الأوكتا العالمي ونسبة الغطاء السحابي", "2 ستايل", "36 Ramps | 14 Colors"),
        ("09_Cloud_Cover", "09_Cloud_Winter_Low_Fog.style", "سحب الشتاء المنخفضة والضباب والسمك البصري", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("09_Cloud_Cover", "09_Cloud_Summer_Convective_Aerosol.style", "السحب الركامية الصيفية والهباء الجوي", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("10_Drought_And_Aridity", "10_Aridity_Annual_UNEP_DeMartonne.style", "القحولة والجفاف لدي مارتون وUNEP", "2 ستايل", "36 Ramps | 14 Colors"),
        ("10_Drought_And_Aridity", "10_Drought_Summer_PET_Hargreaves.style", "البخر-نتح والطلب التبخري الصيفي السريع", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("10_Drought_And_Aridity", "10_Drought_Water_Balance_SPEI.style", "الموازنة المائية والعجز ورطوبة المحاصيل", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("10_Drought_And_Aridity", "10_Drought_Desert_Encroachment.style", "زحف الكثبان وتدهور أطراف الواحات", "2 ستايل", "36 Ramps | 14 Colors"),
        ("11_Climate_Models", "11_Model_Temp_Warming_Stripes.style", "شرائط الاحترار وشذوذ درجات الحرارة", "3 ستايلات", "54 Ramps | 21 Colors"),
        ("11_Climate_Models", "11_Model_Precip_Change_Extremes.style", "تغير الأمطار والظواهر المناخية القصوى", "4 ستايلات", "72 Ramps | 28 Colors"),
        ("11_Climate_Models", "11_Model_SSP_Scenarios_Multi.style", "سيناريوهات مسارات التطور وارتفاع البحر", "3 ستايلات", "54 Ramps | 21 Colors")
    ]

    t_sub = doc.add_table(rows=len(substyles_catalog) + 1, cols=5)
    t_sub.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sub)

    headers_sub = ["مجلد العنصر", "اسم ملف الستايل الفرعي", "التخصص والوظيفة الكارتوجرافية", "عدد الستايلات", "المحتوى الداخلي"]
    widths_sub = [Inches(1.4), Inches(1.8), Inches(1.8), Inches(0.8), Inches(1.2)]

    for i, title in enumerate(headers_sub):
        cell = t_sub.rows[0].cells[i]
        cell.width = widths_sub[i]
        set_cell_shading(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 60, 60)
        p = cell.paragraphs[0]
        make_rtl(p)
        r = p.add_run(title)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, r_data in enumerate(substyles_catalog):
        bg = "F7F9FB" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(r_data):
            cell = t_sub.rows[row_idx + 1].cells[col_idx]
            cell.width = widths_sub[col_idx]
            set_cell_shading(cell, bg)
            set_cell_margins(cell, 60, 60, 60, 60)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            make_rtl(p)
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            if col_idx == 1:
                r.font.name = "Consolas"
                r.font.size = Pt(7.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(27, 54, 93)
            elif col_idx == 2:
                r.font.bold = True

    # ---------------------------------------------------------------------------
    # Section 4: Implementation Steps in ArcMap Desktop 10.8
    # ---------------------------------------------------------------------------
    h4 = doc.add_paragraph()
    make_rtl(h4)
    h4.paragraph_format.space_before = Pt(16)
    h4.paragraph_format.space_after = Pt(6)
    r_h4 = h4.add_run("4. خطوات التطبيق العملي المباشر في برنامج ArcMap Desktop 10.8")
    r_h4.font.name = "Arial"
    r_h4.font.size = Pt(14)
    r_h4.font.bold = True
    r_h4.font.color.rgb = PRIMARY

    steps = [
        ("الخطوة 1: فتح Style Manager وإضافة الستايل المتخصص",
         "من القائمة العلوية لبرنامج ArcMap، اختر Customize -> ثم Style Manager -> اضغط على زر Styles -> اختر Add Style to List -> توجه لمجلد العنصر المطلوب (مثلاً style\\01_Temperature) واختر الستايل الفرعي المطلوب (مثل 01_Temp_Winter_Min.style أو 01_Temp_Summer_Max.style)."),
        ("الخطوة 2: تطبيق الستايل على طبقة الراستر المصنفة (Classified Rasters)",
         "انقر بزر الفأرة الأيمن على طبقة الراستر في جدول المحتويات (TOC) -> Properties -> تبويب Symbology -> اختر Classified -> حدد عدد الفئات في خانة Classes (من 3 إلى 11 فئة) -> في قائمة Color Ramp المنسدلة ستجد تدرجات الستايل الفرعي جاهزة، اختر التدرج المكتوب أمامه [Stepped] للحصول على كتل لونية مصمتة نقية."),
        ("الخطوة 3: تطبيق التدرج الانسيابي على الأسطح المتصلة (Stretched Rasters)",
         "من تبويب Symbology اختر Stretched -> في قائمة Color Ramp اختر التدرج المكتوب أمامه [Smooth] للحصول على تدرج ناعم يتبع الفضاء اللوني الفيزيائي CIELab."),
        ("الخطوة 4: تثبيت الفواصل لخرائط المقارنة المجمعة (Fixed Breakpoints)",
         "عند إعداد لوحة مجمعة للمقارنة بين الفصول، طبق التدرج الموحد (مثل 01_Temp_Unified_All_Seasons.style) ثم اضغط على زر Classify -> اختر Equal Interval أو فترات محددة يدوياً وثبّت نفس قيم الحدود (Break Values) في خرائط الفصول الأربعة لضمان دقة المقارنة البصرية وتفادي الخداع اللوني.")
    ]

    for st_title, st_desc in steps:
        p_st = doc.add_paragraph()
        make_rtl(p_st)
        p_st.paragraph_format.space_after = Pt(4)
        r_st_t = p_st.add_run(st_title + "\n")
        r_st_t.font.name = "Arial"
        r_st_t.font.size = Pt(10.5)
        r_st_t.font.bold = True
        r_st_t.font.color.rgb = SECONDARY

        r_st_d = p_st.add_run(st_desc)
        r_st_d.font.name = "Arial"
        r_st_d.font.size = Pt(9.5)
        r_st_d.font.color.rgb = TEXT_DARK

    # Save to multiple targets
    doc.save(TARGET_DOCX)
    print("Saved Primary DOCX: %s" % TARGET_DOCX)

    copy_targets = [
        os.path.join(BASE_DIR, DOCX_FILENAME),
        os.path.join(SOURCES_DIR, DOCX_FILENAME),
        os.path.join(CONSOLIDATED_1, DOCX_FILENAME),
        os.path.join(CONSOLIDATED_2, DOCX_FILENAME)
    ]
    for ct in copy_targets:
        shutil.copyfile(TARGET_DOCX, ct)
        print("Copied DOCX to: %s" % ct)

    print("ALL WORD DOCUMENTS GENERATED AND DISTRIBUTED SUCCESSFULLY!")

if __name__ == "__main__":
    build_decision_guide()
