# -*- coding: utf-8 -*-
"""
Update and enrich Fields_AR_EN_Units.xlsx with Equal Interval classification,
actual raster statistics (Egypt 1996-2025), and 5 distinct classes ordered
from largest to smallest (من الكبير للصغير).
"""
import os
import math
import xml.etree.ElementTree as ET
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
EXCEL_PATH = r"D:\My Software\NASA POWER Climate Atlas Generator\Fields_AR_EN_Units.xlsx"

# 1. Parse all 103 raster aux.xml files for exact empirical Min, Max, Mean
raster_stats = {}
for root, dirs, files in os.walk(BASE_DIR):
    for f in sorted(files):
        if f.lower().endswith('.tif.aux.xml') and not f.lower().endswith('_cls.tif.aux.xml'):
            xml_path = os.path.join(root, f)
            tif_name = f[:-8]
            fld_name = tif_name[:-4] if tif_name.lower().endswith('.tif') else tif_name
            tree = ET.parse(xml_path)
            root_elem = tree.getroot()
            s_min, s_max, s_mean = None, None, None
            for mdi in root_elem.findall('.//MDI'):
                k = mdi.attrib.get('key')
                if k == 'STATISTICS_MINIMUM': s_min = float(mdi.text)
                elif k == 'STATISTICS_MAXIMUM': s_max = float(mdi.text)
                elif k == 'STATISTICS_MEAN': s_mean = float(mdi.text)
            if s_min is None:
                hmin = root_elem.find('.//HistMin')
                if hmin is not None and hmin.text: s_min = float(hmin.text)
            if s_max is None:
                hmax = root_elem.find('.//HistMax')
                if hmax is not None and hmax.text: s_max = float(hmax.text)
            raster_stats[fld_name] = {
                'folder': os.path.basename(root),
                'tif': tif_name if tif_name.lower().endswith('.tif') else (tif_name + '.tif'),
                'min': s_min,
                'max': s_max,
                'mean': s_mean
            }

print(f"Loaded statistics for {len(raster_stats)} rasters.")

# Special classification rules for specific domains
SPECIAL_RULES = {
    # Wind direction: 5 equal classes of 72 degrees each
    "W_Dir_Annual_Mean": (72.0, [0.0, 72.0, 144.0, 216.0, 288.0, 360.0]),
    "W_Dir_Winter_Mean": (72.0, [0.0, 72.0, 144.0, 216.0, 288.0, 360.0]),
    "W_Dir_Spring_Mean": (72.0, [0.0, 72.0, 144.0, 216.0, 288.0, 360.0]),
    "W_Dir_Summer_Mean": (72.0, [0.0, 72.0, 144.0, 216.0, 288.0, 360.0]),
    "W_Dir_Autumn_Mean": (72.0, [0.0, 72.0, 144.0, 216.0, 288.0, 360.0]),
    # Dry months: discrete 5 classes
    "Dry_Months_Count": (1.0, [8.0, 9.0, 10.0, 11.0, 12.0, 13.0]),
    # UNEP Aridity: 0 to 0.20 with step 0.04
    "UNEP_Aridity_Annual": (0.04, [0.0, 0.04, 0.08, 0.12, 0.16, 0.20]),
    # Water deficit: -2750 to -750 with step 400
    "Water_Deficit_Annual": (400.0, [-2750.0, -2350.0, -1950.0, -1550.0, -1150.0, -750.0]),
    # Decadal temperature trend: 0.10 to 0.60 with step 0.10
    "T_Annual_Trend_Decade": (0.10, [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]),
    # Temperature summer mean: 25 to 35 with step 2.0
    "T_Summer_Mean": (2.0, [25.0, 27.0, 29.0, 31.0, 33.0, 35.0]),
    # Temperature max summer month: 26 to 36 with step 2.0
    "T_Max_Summer_Month_Mean": (2.0, [26.0, 28.0, 30.0, 32.0, 34.0, 36.0]),
    # Annual temperature mean: 18 to 28 with step 2.0
    "T_Annual_Mean": (2.0, [18.0, 20.0, 22.0, 24.0, 26.0, 28.0]),
    # Winter temperature mean: 9 to 24 with step 3.0
    "T_Winter_Mean": (3.0, [9.0, 12.0, 15.0, 18.0, 21.0, 24.0]),
    # Spring temperature mean: 17.5 to 28.5 (or 17 to 29.5) -> step 2.2 or 2.5
    "T_Spring_Mean": (2.2, [17.0, 19.2, 21.4, 23.6, 25.8, 28.0]),
    # Autumn temperature mean: 19 to 30 -> step 2.2
    "T_Autumn_Mean": (2.0, [19.0, 21.0, 23.0, 25.0, 27.0, 29.5]),
    # Annual temperature range: 8 to 20.5 -> step 2.5
    "T_Annual_Range": (2.5, [8.0, 10.5, 13.0, 15.5, 18.0, 20.5]),
    # Annual precipitation mean: 0 to 250 with step 50
    "R_Annual_Mean": (50.0, [0.0, 50.0, 100.0, 150.0, 200.0, 250.0]),
    "R_Annual_Total": (50.0, [0.0, 50.0, 100.0, 150.0, 200.0, 250.0]),
    # Winter precipitation mean: 0 to 150 with step 30
    "R_Winter_Mean": (30.0, [0.0, 30.0, 60.0, 90.0, 120.0, 150.0]),
    "R_Winter_Total": (30.0, [0.0, 30.0, 60.0, 90.0, 120.0, 150.0]),
    # Spring precipitation mean: 0 to 45 with step 9 (or 0 to 50 step 10)
    "R_Spring_Mean": (10.0, [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]),
    "R_Spring_Total": (10.0, [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]),
    # Autumn precipitation mean: 0 to 50 with step 10
    "R_Autumn_Mean": (10.0, [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]),
    "R_Autumn_Total": (10.0, [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]),
    # Summer precipitation mean: 0 to 4 with step 0.8
    "R_Summer_Mean": (0.8, [0.0, 0.8, 1.6, 2.4, 3.2, 4.0]),
    "R_Summer_Total": (0.8, [0.0, 0.8, 1.6, 2.4, 3.2, 4.0]),
    # Annual solar total: 1800 to 2550 with step 150
    "Sol_Annual_Total": (150.0, [1800.0, 1950.0, 2100.0, 2250.0, 2400.0, 2550.0]),
    # Annual solar mean: 5.0 to 7.0 with step 0.4
    "Sol_Annual_Mean": (0.4, [5.0, 5.4, 5.8, 6.2, 6.6, 7.0]),
    # Relative humidity annual mean: 20 to 75 with step 11
    "RH_Annual_Mean": (11.0, [20.0, 31.0, 42.0, 53.0, 64.0, 75.0]),
    # Cloud cover annual mean: 0 to 50 with step 10
    "Cld_Annual_Mean": (10.0, [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]),
    # Evapotranspiration annual mean (annual total scale): 1000 to 2750 with step 350
    "ET_Annual_Mean": (350.0, [1000.0, 1350.0, 1700.0, 2050.0, 2400.0, 2750.0]),
    "PET_Hargreaves_Annual": (350.0, [1000.0, 1350.0, 1700.0, 2050.0, 2400.0, 2750.0]),
}

nice_numbers = [
    0.01, 0.02, 0.025, 0.04, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5,
    0.6, 0.75, 0.8, 1.0, 1.25, 1.5, 2.0, 2.2, 2.5, 3.0, 4.0, 5.0,
    6.0, 7.5, 8.0, 10.0, 11.0, 12.0, 12.5, 15.0, 20.0, 25.0, 30.0, 35.0,
    40.0, 45.0, 50.0, 60.0, 70.0, 72.0, 75.0, 80.0, 100.0, 125.0, 150.0,
    200.0, 250.0, 300.0, 350.0, 400.0, 500.0, 1000.0
]

def get_equal_classes(fld, vmin, vmax, n_classes=5):
    if fld in SPECIAL_RULES:
        return SPECIAL_RULES[fld]
    span = vmax - vmin
    if span <= 0: span = 1.0
    cand = []
    for ns in nice_numbers:
        if ns * n_classes >= span * 0.999:
            start = math.floor(vmin / ns) * ns
            if start + n_classes * ns >= vmax - 1e-4:
                excess = (start + n_classes * ns - vmax) + (vmin - start)
                cand.append((excess, ns, start))
    if cand:
        cand.sort(key=lambda x: (x[0], x[1]))
        _, step, start = cand[0]
    else:
        step = math.ceil(span / float(n_classes))
        start = math.floor(vmin / step) * step
    breaks = [round(start + i * step, 4) for i in range(n_classes + 1)]
    return step, breaks

def fmt_val(v, step):
    if step >= 1 and abs(v - round(v)) < 1e-4:
        return str(int(round(v)))
    elif step >= 0.1 and abs(v * 10 - round(v * 10)) < 1e-4:
        return f"{v:.1f}"
    elif step >= 0.01:
        return f"{v:.2f}"
    else:
        return f"{v:.3f}"

# Load workbook
wb = openpyxl.load_workbook(EXCEL_PATH)
ws = wb['Climate_Fields']

# Colors and styling
NAVY_HEADER = "1F4E79"
HEADER_FONT = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)

THIN_BORDER = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

DATA_FONT = Font(name="Segoe UI", size=9)
DATA_FONT_BOLD = Font(name="Segoe UI", size=9, bold=True)
CODE_FONT = Font(name="Consolas", size=9)
CODE_FONT_BOLD = Font(name="Consolas", size=9, bold=True)

ROW_EVEN_FILL = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
ROW_WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

CLASS_HDR_FILLS = [
    PatternFill(start_color="FADBD8", end_color="FADBD8", fill_type="solid"), # Light Red
    PatternFill(start_color="FDEBD0", end_color="FDEBD0", fill_type="solid"), # Light Orange
    PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid"), # Light Yellow
    PatternFill(start_color="D5F5E3", end_color="D5F5E3", fill_type="solid"), # Light Green
    PatternFill(start_color="D4E6F1", end_color="D4E6F1", fill_type="solid"), # Light Blue
]

# Set New Headers for Climate_Fields
new_headers = [
    (8, "طريقة تصنيف الفئات المعتمدة\nClassification Method", 24),
    (9, "المدى الفعلي للراستر في مصر (1996-2025)\nActual Raster Range (Min - Max)", 28),
    (10, "الفئة الأولى (الأعلى / الأكبر)\nClass 1 (Highest)", 22),
    (11, "الفئة الثانية\nClass 2", 18),
    (12, "الفئة الثالثة\nClass 3", 18),
    (13, "الفئة الرابعة\nClass 4", 18),
    (14, "الفئة الخامسة (الأدنى / الأصغر)\nClass 5 (Lowest)", 22),
]

for col_idx, h_text, width in new_headers:
    cell = ws.cell(1, col_idx, h_text)
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = HEADER_ALIGN
    cell.border = THIN_BORDER
    col_letter = get_column_letter(col_idx)
    ws.column_dimensions[col_letter].width = width

# Fill rows in Climate_Fields
for r in range(2, ws.max_row + 1):
    short_f = ws.cell(r, 2).value
    full_f = ws.cell(r, 3).value
    mod = str(ws.cell(r, 4).value or "")
    unit = str(ws.cell(r, 6).value or "").strip()
    
    is_even = (r % 2 == 0)
    bg_fill = ROW_EVEN_FILL if is_even else ROW_WHITE_FILL

    # Apply existing cells formatting cleanup
    for c in range(1, 8):
        cell = ws.cell(r, c)
        cell.border = THIN_BORDER
        if c in (1, 6):
            cell.alignment = Alignment(horizontal="center", vertical="center")
        elif c in (2, 3):
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.font = CODE_FONT_BOLD if c == 2 else CODE_FONT
        elif c in (4, 5, 7):
            cell.alignment = Alignment(horizontal="right", vertical="center")
        if not cell.fill or cell.fill.fill_type is None or cell.fill.start_color.rgb in ("00FFFFFF", "FFFFFFFF", None):
            cell.fill = bg_fill

    if "Admin" in mod or full_f not in raster_stats:
        # Admin row
        for c in range(8, 15):
            cell = ws.cell(r, c, "-")
            cell.font = DATA_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.fill = bg_fill
            cell.border = THIN_BORDER
        continue

    # Climate raster row
    st = raster_stats[full_f]
    vmin, vmax, vmean = st['min'], st['max'], st['mean']
    step, breaks = get_equal_classes(full_f, vmin, vmax, 5)

    # Classification method
    c8 = ws.cell(r, 8, "Equal Interval (فترات متساوية)")
    c8.font = DATA_FONT
    c8.alignment = Alignment(horizontal="center", vertical="center")
    c8.fill = bg_fill
    c8.border = THIN_BORDER

    # Actual range
    actual_range_str = f"{vmin:.2f} إلى {vmax:.2f} ({unit})" if unit and unit != "-" else f"{vmin:.2f} إلى {vmax:.2f}"
    c9 = ws.cell(r, 9, actual_range_str)
    c9.font = CODE_FONT
    c9.alignment = Alignment(horizontal="center", vertical="center")
    c9.fill = bg_fill
    c9.border = THIN_BORDER

    # 5 Classes ordered from largest to smallest (من الكبير للصغير)
    # Class 1: breaks[4] to breaks[5]
    # Class 2: breaks[3] to breaks[4]
    # Class 3: breaks[2] to breaks[3]
    # Class 4: breaks[1] to breaks[2]
    # Class 5: breaks[0] to breaks[1]
    if full_f == "Dry_Months_Count":
        class_strs = [
            "12 شهر (جفاف دائم)",
            "11 شهر",
            "10 أشهر",
            "9 أشهر",
            "8 أشهر (الساحل الشمالي)"
        ]
    elif full_f.startswith("W_Dir"):
        class_strs = [
            "288° - 360° (شمالي غربي إلى شمالي)",
            "216° - 288° (غربي إلى شمالي غربي)",
            "144° - 216° (جنوبي إلى جنوبي غربي)",
            "72° - 144° (شرقي إلى جنوبي شرقي)",
            "0° - 72° (شمالي إلى شمالي شرقي)"
        ]
    elif full_f == "Water_Deficit_Annual":
        class_strs = [
            f"{fmt_val(breaks[4], step)} إلى {fmt_val(breaks[5], step)} (الأقل عجزاً)",
            f"{fmt_val(breaks[3], step)} إلى {fmt_val(breaks[4], step)}",
            f"{fmt_val(breaks[2], step)} إلى {fmt_val(breaks[3], step)}",
            f"{fmt_val(breaks[1], step)} إلى {fmt_val(breaks[2], step)}",
            f"{fmt_val(breaks[0], step)} إلى {fmt_val(breaks[1], step)} (الأشد عجزاً)"
        ]
    else:
        class_strs = [
            f"{fmt_val(breaks[4], step)} - {fmt_val(breaks[5], step)}",
            f"{fmt_val(breaks[3], step)} - {fmt_val(breaks[4], step)}",
            f"{fmt_val(breaks[2], step)} - {fmt_val(breaks[3], step)}",
            f"{fmt_val(breaks[1], step)} - {fmt_val(breaks[2], step)}",
            f"{fmt_val(breaks[0], step)} - {fmt_val(breaks[1], step)}"
        ]

    for ci, cstr in enumerate(class_strs):
        col_no = 10 + ci
        cell = ws.cell(r, col_no, cstr)
        cell.font = DATA_FONT_BOLD if ci in (0, 4) else DATA_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.fill = bg_fill
        cell.border = THIN_BORDER

# Sheet 2: Dedicated Atlas Maps Guide (103 Maps without Admin rows)
GUIDE_SHEET_NAME = "Atlas_103_Maps_Classification"
if GUIDE_SHEET_NAME in wb.sheetnames:
    del wb[GUIDE_SHEET_NAME]
ws_guide = wb.create_sheet(title=GUIDE_SHEET_NAME)

guide_headers = [
    (1, "رقم\nNo.", 6),
    (2, "الموديول المناخي\nClimate Module", 25),
    (3, "اسم ملف الراستر (GeoTIFF)\nRaster File Name", 30),
    (4, "اسم الحقل الكامل (EN)\nFull Field Name", 28),
    (5, "اسم الخريطة المقترح للأطلس (بالعربي)\nSuggested Atlas Map Title (AR)", 40),
    (6, "الوحدة\nUnit", 14),
    (7, "طريقة التصنيف\nClassification", 18),
    (8, "طول الفئة (الخطوة)\nStep Interval", 15),
    (9, "أدنى قيمة فعلية\nMin", 14),
    (10, "أقصى قيمة فعلية\nMax", 14),
    (11, "متوسط مصر\nMean", 14),
    (12, "الفئة الأولى (الأعلى)\nClass 1 (Highest)", 22),
    (13, "الفئة الثانية\nClass 2", 18),
    (14, "الفئة الثالثة\nClass 3", 18),
    (15, "الفئة الرابعة\nClass 4", 18),
    (16, "الفئة الخامسة (الأدنى)\nClass 5 (Lowest)", 22),
]

for col_idx, h_text, width in guide_headers:
    cell = ws_guide.cell(1, col_idx, h_text)
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = HEADER_ALIGN
    cell.border = THIN_BORDER
    col_letter = get_column_letter(col_idx)
    ws_guide.column_dimensions[col_letter].width = width

map_counter = 1
for r in range(14, ws.max_row + 1):
    full_f = ws.cell(r, 3).value
    mod = ws.cell(r, 4).value
    unit = str(ws.cell(r, 6).value or "").strip()
    title = ws.cell(r, 7).value
    st = raster_stats.get(full_f)
    if not st:
        continue

    vmin, vmax, vmean = st['min'], st['max'], st['mean']
    step, breaks = get_equal_classes(full_f, vmin, vmax, 5)

    gr = map_counter + 1
    is_even = (map_counter % 2 == 0)
    bg_fill = ROW_EVEN_FILL if is_even else ROW_WHITE_FILL

    if full_f == "Dry_Months_Count":
        class_strs = [
            "12 شهر (جفاف دائم)",
            "11 شهر",
            "10 أشهر",
            "9 أشهر",
            "8 أشهر (الساحل)"
        ]
    elif full_f.startswith("W_Dir"):
        class_strs = [
            "288° - 360° (شمالي غربي)",
            "216° - 288° (غربي)",
            "144° - 216° (جنوبي)",
            "72° - 144° (شرقي)",
            "0° - 72° (شمالي شرقي)"
        ]
    elif full_f == "Water_Deficit_Annual":
        class_strs = [
            f"{fmt_val(breaks[4], step)} إلى {fmt_val(breaks[5], step)} (الأقل عجزاً)",
            f"{fmt_val(breaks[3], step)} إلى {fmt_val(breaks[4], step)}",
            f"{fmt_val(breaks[2], step)} إلى {fmt_val(breaks[3], step)}",
            f"{fmt_val(breaks[1], step)} إلى {fmt_val(breaks[2], step)}",
            f"{fmt_val(breaks[0], step)} إلى {fmt_val(breaks[1], step)} (الأشد عجزاً)"
        ]
    else:
        class_strs = [
            f"{fmt_val(breaks[4], step)} - {fmt_val(breaks[5], step)}",
            f"{fmt_val(breaks[3], step)} - {fmt_val(breaks[4], step)}",
            f"{fmt_val(breaks[2], step)} - {fmt_val(breaks[3], step)}",
            f"{fmt_val(breaks[1], step)} - {fmt_val(breaks[2], step)}",
            f"{fmt_val(breaks[0], step)} - {fmt_val(breaks[1], step)}"
        ]

    row_data = [
        (1, map_counter, Alignment(horizontal="center", vertical="center"), DATA_FONT_BOLD),
        (2, mod, Alignment(horizontal="right", vertical="center"), DATA_FONT),
        (3, st['tif'], Alignment(horizontal="left", vertical="center"), CODE_FONT_BOLD),
        (4, full_f, Alignment(horizontal="left", vertical="center"), CODE_FONT),
        (5, title, Alignment(horizontal="right", vertical="center"), DATA_FONT_BOLD),
        (6, unit, Alignment(horizontal="center", vertical="center"), DATA_FONT),
        (7, "Equal Interval", Alignment(horizontal="center", vertical="center"), DATA_FONT),
        (8, fmt_val(step, step), Alignment(horizontal="center", vertical="center"), CODE_FONT_BOLD),
        (9, f"{vmin:.2f}", Alignment(horizontal="center", vertical="center"), CODE_FONT),
        (10, f"{vmax:.2f}", Alignment(horizontal="center", vertical="center"), CODE_FONT),
        (11, f"{vmean:.2f}", Alignment(horizontal="center", vertical="center"), CODE_FONT),
        (12, class_strs[0], Alignment(horizontal="center", vertical="center"), DATA_FONT_BOLD),
        (13, class_strs[1], Alignment(horizontal="center", vertical="center"), DATA_FONT),
        (14, class_strs[2], Alignment(horizontal="center", vertical="center"), DATA_FONT),
        (15, class_strs[3], Alignment(horizontal="center", vertical="center"), DATA_FONT),
        (16, class_strs[4], Alignment(horizontal="center", vertical="center"), DATA_FONT_BOLD),
    ]

    for cidx, val, align, font in row_data:
        cell = ws_guide.cell(gr, cidx, val)
        cell.alignment = align
        cell.font = font
        cell.fill = bg_fill
        cell.border = THIN_BORDER

    map_counter += 1

# Ensure gridlines are visible
ws.views.sheetView[0].showGridLines = True
ws_guide.views.sheetView[0].showGridLines = True

wb.save(EXCEL_PATH)
print(f"Successfully saved updated Excel workbook: {EXCEL_PATH}")
print(f"Added {map_counter - 1} maps to dedicated {GUIDE_SHEET_NAME} sheet.")
