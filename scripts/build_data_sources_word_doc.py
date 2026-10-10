# -*- coding: utf-8 -*-
"""Generate Climate Data Sources Comparison Guide Word Document (.docx)."""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(BASE_DIR, "Documents", "05_Climate_Data_Sources_Directory")
OUT_DOCX = os.path.join(TARGET_DIR, "Climate_Data_Sources_Comparison_Guide.docx")

doc = docx.Document()

# Page Margins (0.75 in)
for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

# Styling Helper
NAVY = RGBColor(15, 23, 42)      # #0F172A
BLUE = RGBColor(2, 132, 199)     # #0284C7
GRAY = RGBColor(71, 85, 105)     # #475569
DARK = RGBColor(30, 41, 59)      # #1E293B

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

# Title
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_after = Pt(4)
run_title = p_title.add_run("دليل ومقارنة مصادر ونماذج البيانات المناخية\nClimate Data Sources & Models Comparison Guide")
run_title.font.name = "Arial"
run_title.font.size = Pt(20)
run_title.font.bold = True
run_title.font.color.rgb = NAVY

# Subtitle
p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(14)
run_sub = p_sub.add_run("NASA POWER & NOAA/WMO Ground Weather Stations Climate Atlas Generator\nAuthor: Ahmad Ibrahim (أحمد إبراهيم) | Version 2.0 (October 2026)")
run_sub.font.name = "Calibri"
run_sub.font.size = Pt(11)
run_sub.font.color.rgb = BLUE

# Intro Paragraph
p_intro = doc.add_paragraph()
p_intro.paragraph_format.space_after = Pt(12)
run_intro = p_intro.add_run(
    "يقدم هذا المستند دليلاً علمياً وتطبيقياً مقارناً لمصادر ونماذج البيانات المناخية الخمسة المعتمدة في أداة توليد الأطلس المناخي (MIRSAD). "
    "يوضح الجدول الفترات الزمنية الفعلية (بداية التغطية ونهايتها)، والدقة المكانية، وطبيعة البيانات، والعناصر المقاسة والمنمذجة، "
    "ليتمكن الباحث من اتخاذ القرار السليم في اختيار المصدر الأنسب لمنطقة دراسته وهدفه العلمي."
)
run_intro.font.name = "Calibri"
run_intro.font.size = Pt(10.5)
run_intro.font.color.rgb = DARK

# Section 1 Heading
p_h1 = doc.add_paragraph()
p_h1.paragraph_format.space_before = Pt(12)
p_h1.paragraph_format.space_after = Pt(6)
r_h1 = p_h1.add_run("1. جدول المقارنة السريع والشامل / Master Summary Matrix")
r_h1.font.name = "Arial"
r_h1.font.size = Pt(13)
r_h1.font.bold = True
r_h1.font.color.rgb = BLUE

# Table 1: Summary Matrix
headers_1 = [
    "مصدر البيانات المناخية\nData Source",
    "سنة البداية\nStart Year",
    "سنة النهاية\nEnd Year",
    "الدقة المكانية\nSpatial Res.",
    "طبيعة البيانات\nData Nature",
    "اكتمال البيانات\nZero-Gap"
]

rows_1 = [
    [
        "Hybrid Climate Engine (Default)\nالنموذج الهجين (الافتراضي للأداة)",
        "1901\n(تاريخ المحطة)",
        "Present\nالوقت الحاضر",
        "Point Station\nإحداثيات المحطة",
        "Fused Multi-Source\nرصد حقيقي + إكمال آلي + أقمار",
        "100% Guaranteed\nمضمون بالكامل"
    ],
    [
        "NOAA ISD / GHCN Ground Archive\nأرشيف الرصد الأرضي المباشر",
        "1901\n(1850s)",
        "Present\n(Real-Time)",
        "Point Station\nأجهزة المحطة",
        "Physical Instruments\nرصد ميداني بحت من المستشعرات",
        "Subject to Gaps\nمعرض لفجوات الصيانة"
    ],
    [
        "NASA POWER Agroclimatology\nنموذج ناسا للمناخ الزراعي",
        "1981\n(1984 Solar)",
        "Present\n(2-4 days)",
        "0.5° × 0.625°\n(~50 × 60 km)",
        "Gridded Reanalysis\nإعادة تحليل شبكية MERRA-2",
        "100% Gridded\nشبكي مكتمل عالمياً"
    ],
    [
        "Open-Meteo ERA5 / ERA5-Land\nالنموذج الأوروبي عالي الدقة",
        "1940\n(1950 ERA5-L)",
        "Present\n(2-5 days)",
        "0.10° (~9 km)\nدقة فائقة",
        "Gridded ERA5-Land\nإعادة تحليل معدلة طبوغرافياً",
        "100% Gridded\nشبكي مكتمل عالمياً"
    ],
    [
        "Copernicus Climate Data Store (CDS)\nمخزن بيانات كوبرنيكوس الأوروبي",
        "1940\n(1950 ERA5-L)",
        "Present\n(2-5 days)",
        "0.10° (~9 km)\nدقة فائقة",
        "Gridded C3S Reanalysis\nإعادة تحليل أوروبية معتمدة",
        "100% Gridded\nشبكي مكتمل عالمياً"
    ]
]

t1 = doc.add_table(rows=len(rows_1) + 1, cols=6)
t1.alignment = WD_TABLE_ALIGNMENT.CENTER
t1.autofit = False

col_widths_1 = [Inches(2.2), Inches(0.9), Inches(0.9), Inches(1.1), Inches(1.4), Inches(1.0)]

# Format Header
for col_idx, text in enumerate(headers_1):
    cell = t1.cell(0, col_idx)
    cell.width = col_widths_1[col_idx]
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

# Format Data Rows
for row_idx, r_data in enumerate(rows_1):
    bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, text in enumerate(r_data):
        cell = t1.cell(row_idx + 1, col_idx)
        cell.width = col_widths_1[col_idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        if "Default" in text or "100% Guaranteed" in text or "0.10°" in text:
            r.font.bold = True
            r.font.color.rgb = BLUE
        else:
            r.font.color.rgb = DARK

# Section 2 Heading
p_h2 = doc.add_paragraph()
p_h2.paragraph_format.space_before = Pt(16)
p_h2.paragraph_format.space_after = Pt(6)
r_h2 = p_h2.add_run("2. مصفوفة توفر العناصر المناخية عبر المصادر / Climate Elements Matrix")
r_h2.font.name = "Arial"
r_h2.font.size = Pt(13)
r_h2.font.bold = True
r_h2.font.color.rgb = BLUE

headers_2 = [
    "العنصر المناخي / Parameter",
    "Hybrid Engine",
    "NOAA ISD",
    "NASA POWER",
    "Open-Meteo",
    "Copernicus CDS"
]

rows_2 = [
    ["درجات حرارة الهواء (T, Tmax, Tmin)", "نعم (رصد + إكمال)", "نعم (رصد أجهزة)", "نعم (MERRA-2)", "نعم (ERA5-L)", "نعم (ERA5-L)"],
    ["نقطة الندى والرطوبة النسبية (Td, RH)", "نعم (رصد + إكمال)", "نعم (رصد أجهزة)", "نعم (MERRA-2)", "نعم (ERA5-L)", "نعم (ERA5-L)"],
    ["ضغط مستوى سطح البحر (PSL) والآيزوبار", "نعم (رصد + إكمال)", "نعم (رصد أجهزة)", "نعم (Surface PS)", "نعم (ERA5-L)", "نعم (ERA5-L)"],
    ["سرعة واتجاه الرياح وعواصفها", "نعم (رصد + إكمال)", "نعم (رصد أجهزة)", "نعم (MERRA-2)", "نعم (ERA5-L)", "نعم (ERA5-L)"],
    ["الأمطار التراكمية ومعدلات الهطول", "نعم (رصد + إكمال)", "نعم (رصد أجهزة)", "نعم (MERRA-2)", "نعم (ERA5-L)", "نعم (ERA5-L)"],
    ["الغطاء السحابي بالأثمان والنسبة", "نعم (رصد + إكمال)", "نعم (رصد أجهزة)", "نعم (MERRA-2)", "نعم (ERA5-L)", "نعم (ERA5-L)"],
    ["الإشعاع الشمسي الكلي (GHI / DNI)", "نعم (دمج CERES)", "غير متوفر", "نعم (المعيار الذهبي)", "نعم (نمذجة)", "نعم (نمذجة)"],
    ["مؤشر الأشعة فوق البنفسجية (UV Index)", "نعم (دمج FLASHFlux)", "غير متوفر", "نعم (مستشعر فضائي)", "تقديري", "تقديري"],
    ["حرارة سطح الأرض الإشعاعية (LST)", "نعم (دمج فضائي)", "غير متوفر", "نعم (MERRA-2 Skin)", "نعم (ERA5 Skin)", "نعم (ERA5 Skin)"],
    ["حرارة ورطوبة التربة (4 أعماق)", "خياري", "غير متوفر", "غير متوفر", "نعم (0-255 سم)", "نعم (0-255 سم)"],
    ["المؤشرات الحيوية (HI, WC, ET, Aridity)", "نعم (حساب 100%)", "نعم (حساب رياضي)", "نعم (حساب رياضي)", "نعم (حساب رياضي)", "نعم (حساب رياضي)"],
    ["ضمان خلو الراستر من الخلايا الفارغة", "مضمون 100%", "معرض للفجوات", "مضمون 100%", "مضمون 100%", "مضمون 100%"]
]

t2 = doc.add_table(rows=len(rows_2) + 1, cols=6)
t2.alignment = WD_TABLE_ALIGNMENT.CENTER
t2.autofit = False

col_widths_2 = [Inches(2.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0), Inches(1.0)]

for col_idx, text in enumerate(headers_2):
    cell = t2.cell(0, col_idx)
    cell.width = col_widths_2[col_idx]
    set_cell_background(cell, "0284C7")
    set_cell_margins(cell, top=100, bottom=100, left=70, right=70)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

for row_idx, r_data in enumerate(rows_2):
    bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, text in enumerate(r_data):
        cell = t2.cell(row_idx + 1, col_idx)
        cell.width = col_widths_2[col_idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=70, bottom=70, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.0)
        if col_idx == 1:
            r.font.bold = True
            r.font.color.rgb = RGBColor(2, 132, 199)
        elif "غير متوفر" in text:
            r.font.color.rgb = RGBColor(220, 38, 38)
        else:
            r.font.color.rgb = DARK

# Section 3: Capabilities vs Limitations
p_h3 = doc.add_paragraph()
p_h3.paragraph_format.space_before = Pt(16)
p_h3.paragraph_format.space_after = Pt(6)
r_h3 = p_h3.add_run("3. مصفوفة ما يوفره وما يعجز عن توفيره كل مصدر / Capabilities vs Limitations")
r_h3.font.name = "Arial"
r_h3.font.size = Pt(13)
r_h3.font.bold = True
r_h3.font.color.rgb = BLUE

headers_3 = [
    "مصدر البيانات / Source",
    "ما يستطيع المصدر توفيره بدقة (Capabilities)",
    "ما لا يستطيع المصدر توفيره والقيود (Limitations)"
]

rows_3 = [
    [
        "Hybrid Climate Engine\n(الافتراضي للأداة)",
        "• تغطية 100% لجميع الموديلات الـ 19 دون أي قيم مفقودة.\n• رصد مادي حقيقي لأجهزة المحطة (حرارة، رطوبة، ضغط، رياح، أمطار).\n• دمج الإشعاع الشمسي والـ UV وحرارة السطح من الأقمار الصناعية (CERES).\n• حساب رياضي كامل لجميع النماذج البيومناخية الـ 8.\n• ضمان خلو أسطح الراستر النهائية من أي بكسلات فارغة.",
        "• لا يوفر قراءات بيرانوميتر أرضية (يعتمد على الأقمار الصناعية).\n• لا يوفر مقاطع رطوبة وحرارة التربة بالأعماق لجميع المحطات.\n• لا يصلح كبديل للتقارير الجنائية القضائية المشترطة للسجلات الخام دون استكمال.\n• لا يمكنه استكمال ثغرات المحطات المتوقفة قبل عام 1940."
    ],
    [
        "NOAA ISD / GHCN Archive\n(الرصد الأرضي المباشر)",
        "• حقيقة أرضية مادية 100% من أجهزة ومستشعرات المحطة دون أي نمذجة.\n• حرارة الهواء، ونقطة الندى، والرطوبة النسبية السيكرومترية.\n• ضغط سطح المحطة وضغط مستوى البحر (PSL) والآيزوبار.\n• سرعة واتجاه الرياح وعواصف الرياح القصوى (Wind Gusts).\n• كميات الأمطار اليومية والساعية وشفرات الطقس الحاضر.\n• حجية قانونية رسمية وموثوقية معتمدة للتقارير القضائية.",
        "• لا يوفر الإشعاع الشمسي (Solar Radiation) لمعظم المحطات.\n• لا يوفر مؤشر الأشعة فوق البنفسجية (UV Index).\n• لا يوفر حرارة سطح الأرض الإشعاعية (LST).\n• لا يوفر مقاطع رطوبة وحرارة التربة بالأعماق.\n• معرض لوجود قيم مفقودة وفترات انقطاع بسبب صيانة الحساسات.\n• لا يوفر تغطية شبكية في المناطق الخالية من أبراج المحطات."
    ],
    [
        "NASA POWER Agroclimatology\n(المناخ الزراعي والشمسي)",
        "• المعيار العالمي الذهبي للإشعاع الشمسي السطحي (أقمار CERES).\n• مؤشر الأشعة فوق البنفسجية اليومي (UV Index) الفضائي.\n• تغطية شبكية عالمية متصلة 100% بدون أي فجوات مكانية.\n• درجات حرارة الهواء على ارتفاع 2م وحرارة جلد الأرض (LST).\n• سرعة الرياح على ارتفاعات 2م و 10م و 50م واتجاه الرياح.\n• معدل الأمطار اليومي المصحح ونسبة الغطاء السحابي الكلي.",
        "• لا يوفر بيانات تاريخية قبل 1 يناير 1981 (1901-1980 غير متوفر).\n• لا يوفر هبات الرياح اللحظية القصوى (Wind Gusts).\n• لا يوفر ضغط مستوى سطح البحر (PSL) مباشرة (يوفر الضغط السطحي PS).\n• لا يوفر رطوبة أو حرارة التربة بالأعماق (0-255 سم).\n• دقة الخلية واسعة (~50 × 60 كم) لا تلتقط تضاريس الأودية الجبلية الضيقة.\n• يتأخر من 2 إلى 4 أيام عن التاريخ الحالي (ليس لحظياً)."
    ],
    [
        "Open-Meteo ERA5 / ERA5-Land\n(إعادة التحليل فائقة الدقة)",
        "• أعلى دقة مكانية عالمية في نماذج إعادة التحليل لليابسة: 0.10° (~9 كم).\n• سلسلة زمنية تاريخية مستمرة لأكثر من 85 عاماً (1940 إلى الآن).\n• مراعاة انحدار درجات الحرارة مع الارتفاع والتضاريس (DEM).\n• درجات حرارة الهواء، والحرارة المحسوسة، وهبات الرياح (Gusts).\n• ضغط مستوى سطح البحر المباشر عالي الدقة (PSL).\n• رطوبة وحرارة التربة عند 4 أعماق متتالية (0-255 سم).\n• البخر-نتح المرجعي القياسي ET0 بمعادلة فاو-56 بنمان مونتيث.",
        "• لا يوفر بيانات تاريخية قبل عام 1940 (1901-1939 غير متوفر).\n• لا يوفر مؤشر UV الفضائي المباشر (يقدم تقديرات إشعاعية عامة).\n• ليس رصداً مادياً حقيقياً لأجهزة المحطة (هو نموذج رياضي استيعابي).\n• يتأخر من 2 إلى 5 أيام عن التاريخ الحالي لإجراء المراجعات والتدقيق."
    ],
    [
        "Copernicus Climate Data Store\n(CDS / ERA5 / AgERA5)",
        "• المصدر المرجعي الرسمي المعتمد من المفوضية الأوروبية ومركز ECMWF الدولي.\n• دقة مكانية فائقة 0.10° (~9 كم) عبر شبكة ERA5-Land لليابسة.\n• سلسلة زمنية تاريخية متواصلة من عام 1940 وحتى الوقت الحاضر.\n• دعم مفتاح الوصول الرسمي (CDS API Key) مع دعم التدفق السريع دون مفتاح (Zero-Auth Fallback).\n• توافق تام مع استخراج شرائح الراستر بصيغة NetCDF وتحويلها لنقاط جغرافية.\n• رطوبة وحرارة التربة عند 4 أعماق متتالية (0-255 سم).",
        "• لا يوفر بيانات تاريخية قبل عام 1940 (1901-1939 غير متوفر).\n• الاستعلام المباشر عبر CDS API قد يتطلب الانتظار في طوابير معالجة (Queuing) إذا كانت خوادم CDS مزدحمة.\n• يتأخر من 2 إلى 5 أيام عن الوقت الفعلي لمطابقة الفحوصات الجوية.\n• ليس رصداً مادياً لمحطة أرضية حقيقية وإنما نموذج إعادة تحليل استيعابي."
    ]
]

t3 = doc.add_table(rows=len(rows_3) + 1, cols=3)
t3.alignment = WD_TABLE_ALIGNMENT.CENTER
t3.autofit = False

col_widths_3 = [Inches(1.8), Inches(2.8), Inches(2.8)]

for col_idx, text in enumerate(headers_3):
    cell = t3.cell(0, col_idx)
    cell.width = col_widths_3[col_idx]
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=100, bottom=100, left=90, right=90)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

for row_idx, r_data in enumerate(rows_3):
    bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, text in enumerate(r_data):
        cell = t3.cell(row_idx + 1, col_idx)
        cell.width = col_widths_3[col_idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=80, bottom=80, left=90, right=90)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        if col_idx == 0:
            r.font.bold = True
            r.font.color.rgb = BLUE
        else:
            r.font.color.rgb = DARK

# Section 4: Decision Rules
p_h4 = doc.add_paragraph()
p_h4.paragraph_format.space_before = Pt(16)
p_h4.paragraph_format.space_after = Pt(6)
r_h4 = p_h4.add_run("4. قواعد وشجرة اتخاذ القرار للباحث الجغرافي / Decision Guide")
r_h4.font.name = "Arial"
r_h4.font.size = Pt(13)
r_h4.font.bold = True
r_h4.font.color.rgb = BLUE

rules = [
    ("لإنتاج أطلس مناخي متكامل وخالٍ من الخلايا المفقودة (الخيار الافتراضي):",
     "اختر [Hybrid Engine] حيث يضمن لك الاستناد إلى الرصد الميداني الحقيقي للمحطة مع استكمال أي فجوات وصيانة تلقائياً."),
    ("للتدقيق الأكاديمي والرصد الميداني البحت من موازين الحرارة والبارومترات:",
     "اختر [NOAA ISD Ground] للاعتماد الحصري على المستشعرات المادية في المحطة دون أي نمذجة رياضية."),
    ("لدراسات الطاقة الشمسية والحرارية واستهلاك المياه الزراعي بعد عام 1981:",
     "اختر [NASA POWER API] للاستفادة من المعيار الذهبي لأقمار CERES ودقة الطاقة الشمسية المتصلة."),
    ("للمناطق الجبلية والتضاريس الوعرة، أو دراسات حرارة ورطوبة التربة، أو الفترات من 1940 إلى 1980:",
     "اختر [Open-Meteo ERA5] للاستفادة من أعلى دقة مكانية متاحة عالمياً (~9 كم) المعدلة طبوغرافياً."),
    ("للأبحاث الأوروبية المعتمدة رسمياً والوصول المباشر لبيانات ECMWF و ERA5-Land:",
     "اختر [Copernicus Climate Data Store (CDS)] للاستفادة من المرجعية الأوروبية الرسمية لبرنامج كوبرنيكوس مع إمكانية إدخال CDS API Key الخاص بك أو العمل المباشر دون تسجيل.")
]

for title, desc in rules:
    p_rule = doc.add_paragraph()
    p_rule.paragraph_format.space_after = Pt(4)
    r_t = p_rule.add_run(f"• {title} ")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(10)
    r_t.font.bold = True
    r_t.font.color.rgb = NAVY
    r_d = p_rule.add_run(desc)
    r_d.font.name = "Calibri"
    r_d.font.size = Pt(10)
    r_d.font.color.rgb = DARK

doc.save(OUT_DOCX)
print("Successfully generated Word Document at:", OUT_DOCX)
