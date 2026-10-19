# -*- coding: utf-8 -*-
"""
Generate Master Visual Styles Catalog in Microsoft Excel (.xlsx)
NASA POWER & Open-Meteo Climate Atlas Generator

Features:
- Single comprehensive Excel workbook with 12 sheets:
  1. Index & Overview (الفهرس الشامل والإحصائيات)
  2 to 12. Individual sheets for each of the 11 climate elements
- In each element sheet:
  * Table of Color Ramps for tiers 3 to 11 classes (Stepped & Smooth)
  * CRITICAL: Each color is rendered in its OWN individual cell with its ACTUAL background fill color (HEX color)!
  * Font color automatically adapts to relative luminance for optimal readability.
  * Table of Individual Named Colors and Fill Symbols with swatches.
"""

import os
import sys
import io
import json
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STYLE_DIR = os.path.join(BASE_DIR, "style")
EXCEL_OUT_STYLE = os.path.join(STYLE_DIR, "NASA_POWER_Climate_Atlas_Master_Styles.xlsx")
EXCEL_OUT_CONSOLIDATED = os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated", "NASA_POWER_Climate_Atlas_Master_Styles.xlsx")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts", "styles"))
import generate_climate_styles as gcs

# Helper styling functions
def get_contrast_font(hex_code, bold=True, size=9):
    h = hex_code.strip().lstrip('#')
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    # Relative luminance
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    font_color = "000000" if lum >= 135 else "FFFFFF"
    return Font(name="Consolas", size=size, bold=bold, color=font_color)

def get_fill(hex_code):
    h = hex_code.strip().lstrip('#').upper()
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    return PatternFill(start_color=h, end_color=h, fill_type="solid")

thin_border_side = Side(border_style="thin", color="D3D3D3")
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
thick_bottom = Border(bottom=Side(border_style="medium", color="1B365D"))

hdr_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
hdr_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

subhdr_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
subhdr_fill = PatternFill(start_color="2B5B84", end_color="2B5B84", fill_type="solid")

def build_master_excel():
    print("Generating Master Excel Styles Catalog with True Visual Swatches...")
    wb = openpyxl.Workbook()

    # -------------------------------------------------------------------------
    # Sheet 1: Index & Overview
    # -------------------------------------------------------------------------
    ws_idx = wb.active
    ws_idx.title = "Index & Summary"
    ws_idx.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_idx.merge_cells("A1:J2")
    t_cell = ws_idx["A1"]
    t_cell.value = "NASA POWER & Open-Meteo Climate Atlas Generator\nالموسوعة الكارتوجرافية الشاملة للستايلات والتدرجات اللونية (Mega Edition)"
    t_cell.font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
    t_cell.fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    t_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Subtitle
    ws_idx.merge_cells("A3:J3")
    sub_cell = ws_idx["A3"]
    sub_cell.value = "فهرس شامل يضم 125 ستايلاً علمياً | 9 مستويات فئات (3 إلى 11 فئة) | 2,250 Color Ramps | 875 لون فردي ورمز مضلع"
    sub_cell.font = Font(name="Calibri", size=10, italic=True, color="333333")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")

    # KPI Table
    ws_idx["A5"] = "الإحصائية الكارتوجرافية"
    ws_idx["B5"] = "القيمة الإجمالية"
    ws_idx["C5"] = "الملاحظات والمواصفات المعيارية"
    for col_l in ["A", "B", "C"]:
        ws_idx[f"{col_l}5"].font = hdr_font
        ws_idx[f"{col_l}5"].fill = hdr_fill
        ws_idx[f"{col_l}5"].alignment = hdr_align

    kpi_rows = [
        ("إجمالي العناصر المناخية (Climate Elements)", "11 عنصراً", "الحرارة، الأمطار، الضغط الجوي، الرياح، الرطوبة، الإشعاع، الأشعة، الغيوم، الجفاف، النماذج"),
        ("إجمالي الستايلات الكارتوجرافية (Scientific Styles)", "125 ستايلاً", "معتمدة ومطابقة لمعايير IPCC, WMO, NOAA, WHO, UNEP, ColorBrewer"),
        ("مستويات الفئات المتاحة لكل ستايل (Class Tiers)", "9 مستويات كاملة", "3، 4، 5، 6، 7، 8، 9، 10، 11 فئة (فردية وزوجية وبينية)"),
        ("أنواع التدرج اللوني (Ramp Types)", "نوعان مستقلان", "[Stepped] فئات مجزأة مصمتة للراستر المصنف + [Smooth] تدرج ناعم للراستر المتصل"),
        ("إجمالي الـ Color Ramps المدمجة", "2,250 Color Ramp", "100% Valid بنسبة معاينة مرئية حية داخل ArcMap Style Gallery"),
        ("إجمالي الألوان الفردية المسجلة ([Colors])", "875 لوناً فردياً", "عينات لونية مسماة متاحة للاختيار المباشر في لوحة ألوان ArcMap"),
        ("إجمالي رموز المضلعات المسجلة ([Fill Symbols])", "875 رمز مضلع", "رموز مساحات مصمتة مع حدود خفيفة 0.4pt لتمثيل الخرائط المتجهة"),
        ("قواعد التناظر ثنائي الاتجاه (Diverging Symmetry)", "تناظر قطبي صارم", "11 فئة (5-1-5) | 9 فئات (4-1-4) | 7 فئات (3-1-3) | 5 فئات (2-1-2) مع فئة محايدة")
    ]

    for r_idx, (k, v, desc) in enumerate(kpi_rows, start=6):
        bg = "F7F9FB" if r_idx % 2 == 1 else "FFFFFF"
        ws_idx[f"A{r_idx}"] = k
        ws_idx[f"B{r_idx}"] = v
        ws_idx[f"C{r_idx}"] = desc
        ws_idx[f"A{r_idx}"].font = Font(name="Arial", size=9.5, bold=True)
        ws_idx[f"B{r_idx}"].font = Font(name="Arial", size=9.5, bold=True, color="1B365D")
        ws_idx[f"C{r_idx}"].font = Font(name="Arial", size=9)
        for col_l in ["A", "B", "C"]:
            ws_idx[f"{col_l}{r_idx}"].fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")
            ws_idx[f"{col_l}{r_idx}"].border = thin_border
            ws_idx[f"{col_l}{r_idx}"].alignment = Alignment(vertical="center")

    # Table of Elements Summary
    ws_idx["A16"] = "فهرس صفحات العناصر المناخية والروابط المباشرة"
    ws_idx.merge_cells("A16:F16")
    ws_idx["A16"].font = hdr_font
    ws_idx["A16"].fill = subhdr_fill
    ws_idx["A16"].alignment = Alignment(horizontal="center", vertical="center")

    headers_elem = ["رقم المجلد", "اسم العنصر المناخي (عربي)", "Element Name (English)", "عدد الستايلات", "عدد Color Ramps", "اسم الصفحة في الإكسيل"]
    for c_idx, h_text in enumerate(headers_elem, start=1):
        c_cell = ws_idx.cell(row=17, column=c_idx)
        c_cell.value = h_text
        c_cell.font = hdr_font
        c_cell.fill = hdr_fill
        c_cell.alignment = hdr_align

    all_elements = [{"folder": "01_Temperature", "name_en": "Temperature", "name_ar": "درجات الحرارة", "styles": gcs.TEMPERATURE_STYLES}] + gcs.OTHER_ELEMENTS
    for e_idx, el in enumerate(all_elements, start=18):
        bg = "F7F9FB" if e_idx % 2 == 1 else "FFFFFF"
        fld = el["folder"]
        n_st = len(el["styles"])
        n_rm = n_st * 18
        sh_name = fld
        row_vals = [fld[:2], el.get("name_ar", fld), el.get("name_en", fld), n_st, n_rm, sh_name]
        for c_idx, val in enumerate(row_vals, start=1):
            cell = ws_idx.cell(row=e_idx, column=c_idx)
            cell.value = val
            cell.font = Font(name="Arial", size=9.5, bold=(c_idx in [1, 2, 4]))
            cell.fill = PatternFill(start_color=bg, end_color=bg, fill_type="solid")
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center" if c_idx in [1, 4, 5] else "left", vertical="center")

    ws_idx.column_dimensions["A"].width = 30
    ws_idx.column_dimensions["B"].width = 25
    ws_idx.column_dimensions["C"].width = 65
    ws_idx.column_dimensions["D"].width = 16
    ws_idx.column_dimensions["E"].width = 18
    ws_idx.column_dimensions["F"].width = 25

    # -------------------------------------------------------------------------
    # Sheets 2 to 12: Individual Element Sheets
    # -------------------------------------------------------------------------
    for el in all_elements:
        fld = el["folder"]
        el_ar = el.get("name_ar", fld)
        el_en = el.get("name_en", fld)
        st_list = el["styles"]

        ws = wb.create_sheet(title=fld[:31])
        ws.views.sheetView[0].showGridLines = True

        # Sheet Header Banner
        ws.merge_cells("A1:R2")
        h_cell = ws["A1"]
        h_cell.value = f"{el_ar} - {el_en}\nNASA POWER Climate Atlas - {len(st_list)} Scientific Styles | 9 Class Tiers (3 to 11 Classes)"
        h_cell.font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
        h_cell.fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
        h_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Section 1 Header
        ws.cell(row=4, column=1, value="جدول التدرجات اللونية المرئية (Visual Color Ramps & Exact Swatches)")
        ws.merge_cells("A4:R4")
        ws["A4"].font = hdr_font
        ws["A4"].fill = subhdr_fill
        ws["A4"].alignment = Alignment(horizontal="left", vertical="center")

        ramp_headers = [
            "ID الستايل", "اسم الستايل (إنجليزي)", "اسم الستايل (عربي)", "النوع الكارتوجرافي",
            "المصدر العلمي", "عدد الفئات", "نمط التدرج",
            "اللون 1", "اللون 2", "اللون 3", "اللون 4", "اللون 5", "اللون 6", "اللون 7", "اللون 8", "اللون 9", "اللون 10", "اللون 11"
        ]

        for c_idx, h_text in enumerate(ramp_headers, start=1):
            cell = ws.cell(row=5, column=c_idx, value=h_text)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = hdr_align
            cell.border = thin_border

        cur_row = 6
        for s in st_list:
            s_id = s["id"]
            s_en = s["name_en"]
            s_ar = s["name_ar"]
            s_cat = s["category"]
            s_src = s["source"]
            classes_map = s.get("classes", {})
            sorted_tiers = sorted([int(k) for k in classes_map.keys()])

            for nclass in sorted_tiers:
                hex_list = classes_map.get(nclass) or classes_map.get(str(nclass))
                if not hex_list:
                    continue

                for r_type in ["Stepped", "Smooth"]:
                    meta_vals = [
                        s_id, s_en, s_ar, s_cat, s_src,
                        f"{nclass} فئات", f"[{r_type}]"
                    ]
                    for c_idx, val in enumerate(meta_vals, start=1):
                        cell = ws.cell(row=cur_row, column=c_idx, value=val)
                        cell.font = Font(name="Arial", size=8.5, bold=(c_idx in [1, 6, 7]))
                        bg_c = "F9FBFD" if cur_row % 2 == 1 else "FFFFFF"
                        cell.fill = PatternFill(start_color=bg_c, end_color=bg_c, fill_type="solid")
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="center" if c_idx in [4, 6, 7] else "left", vertical="center")

                    # Color Swatch Cells (Columns 8 to 18)
                    for col_step in range(11):
                        cell_swatch = ws.cell(row=cur_row, column=8 + col_step)
                        if col_step < len(hex_list):
                            h_col = hex_list[col_step]
                            cell_swatch.value = h_col
                            cell_swatch.fill = get_fill(h_col)
                            cell_swatch.font = get_contrast_font(h_col, bold=True, size=8)
                            cell_swatch.alignment = Alignment(horizontal="center", vertical="center")
                        else:
                            # Empty padding for tiers < 11
                            cell_swatch.value = ""
                            cell_swatch.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
                        cell_swatch.border = thin_border

                    cur_row += 1

        # Section 2: Individual Named Colors and Fill Symbols Table
        cur_row += 2
        ws.cell(row=cur_row, column=1, value="جدول الألوان الفردية المعتمدة ورموز المضلعات المسجلة ([Colors] & [Fill Symbols])")
        ws.merge_cells(f"A{cur_row}:G{cur_row}")
        ws[f"A{cur_row}"].font = hdr_font
        ws[f"A{cur_row}"].fill = subhdr_fill
        ws[f"A{cur_row}"].alignment = Alignment(horizontal="left", vertical="center")
        cur_row += 1

        color_headers = ["عينة اللون (Visual Swatch)", "اسم اللون المسجل في ArcMap", "كود اللون (HEX)", "القيم الرقمية (RGB)", "الدور الكارتوجرافي", "رمز المضلع المقابل ([Fill Symbol])", "الستايل التابع له"]
        for c_idx, h_text in enumerate(color_headers, start=1):
            cell = ws.cell(row=cur_row, column=c_idx, value=h_text)
            cell.font = hdr_font
            cell.fill = hdr_fill
            cell.alignment = hdr_align
            cell.border = thin_border
        cur_row += 1

        for s in st_list:
            s_name = s["name_en"]
            s_cat = s["category"]
            is_div = (s_cat.lower() == "diverging")
            sample_hexes = s["classes"].get("7") or s["classes"].get(7) or s["classes"].get("5") or s["classes"].get(5)
            if not sample_hexes:
                continue

            tot_sample = len(sample_hexes)
            mid_idx = tot_sample // 2

            for idx, hex_c in enumerate(sample_hexes):
                h_clean = hex_c.lstrip('#')
                r = int(h_clean[0:2], 16)
                g = int(h_clean[2:4], 16)
                b = int(h_clean[4:6], 16)

                if is_div and idx == mid_idx and (tot_sample % 2 == 1):
                    c_name = f"{s_name} - Neutral Center ({hex_c})"
                    f_name = f"{s_name} - Neutral Center Fill ({hex_c})"
                    c_role = "نقطة التعادل المحايدة (Neutral Center Zero/Mean)"
                else:
                    c_name = f"{s_name} - Class {idx + 1}/{tot_sample} ({hex_c})"
                    f_name = f"{s_name} - Zone {idx + 1}/{tot_sample} Fill ({hex_c})"
                    c_role = f"فئة تصنيف رقم {idx + 1} من {tot_sample}"

                # Visual Swatch Cell
                c1 = ws.cell(row=cur_row, column=1, value=hex_c)
                c1.fill = get_fill(hex_c)
                c1.font = get_contrast_font(hex_c, bold=True, size=8.5)
                c1.alignment = Alignment(horizontal="center", vertical="center")
                c1.border = thin_border

                row_color_vals = [c_name, hex_c, f"RGB({r}, {g}, {b})", c_role, f_name, s_name]
                for col_k, c_val in enumerate(row_color_vals, start=2):
                    cell = ws.cell(row=cur_row, column=col_k, value=c_val)
                    cell.font = Font(name="Arial", size=8.5, bold=(col_k in [2, 3]))
                    bg_c = "F9FBFD" if cur_row % 2 == 1 else "FFFFFF"
                    cell.fill = PatternFill(start_color=bg_c, end_color=bg_c, fill_type="solid")
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center" if col_k in [3, 4] else "left", vertical="center")

                cur_row += 1

        # Adjust column widths for clean readability
        ws.column_dimensions["A"].width = 24
        ws.column_dimensions["B"].width = 30
        ws.column_dimensions["C"].width = 32
        ws.column_dimensions["D"].width = 16
        ws.column_dimensions["E"].width = 32
        ws.column_dimensions["F"].width = 12
        ws.column_dimensions["G"].width = 12
        for col_i in range(8, 19):
            ws.column_dimensions[get_column_letter(col_i)].width = 11

    # Save to designated locations
    wb.save(EXCEL_OUT_STYLE)
    print(f"Master Excel Workbook saved: {EXCEL_OUT_STYLE}")

    if os.path.isdir(os.path.dirname(EXCEL_OUT_CONSOLIDATED)):
        wb.save(EXCEL_OUT_CONSOLIDATED)
        print(f"Copied Master Excel to: {EXCEL_OUT_CONSOLIDATED}")

if __name__ == "__main__":
    build_master_excel()
