# -*- coding: utf-8 -*-
"""
Build True Native ArcMap Climate Style Databases (.style)
Standard Edition: 125 Scientific Climate Styles across 11 Elements
Registered under Category: 'Default Ramps'
Dynamic MultiPartColorRamp with CIELab interpolation for seamless Classified & Stretched support.
"""
from __future__ import unicode_literals
import os
import sys
import shutil
import time
import gc

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STYLE_DIR = os.path.join(BASE_DIR, "style")
RAW_DIR = os.path.join(STYLE_DIR, "Raw_Climate_Styles")
TEMPLATE_STYLE = os.path.join(RAW_DIR, "Meteorological.style")

OUT_STYLE_DIR = os.path.join(STYLE_DIR, "ArcMap_Style_Files")
CONSOLIDATED_DIR = os.path.join(STYLE_DIR, "All_ArcMap_Styles_Consolidated")

for d in [OUT_STYLE_DIR, CONSOLIDATED_DIR]:
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

def make_rgb(r, g, b):
    c_obj = comtypes.client.CreateObject("esriDisplay.RgbColor")
    c = c_obj.QueryInterface(m_disp.IRgbColor)
    c.Red = r
    c.Green = g
    c.Blue = b
    return c_obj.QueryInterface(m_disp.IColor)

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def create_smooth_multipart_ramp(hex_list, name):
    """
    Creates a continuous smooth MultiPartColorRamp connecting adjacent
    color stops with CIELab interpolation.
    Category: 'Default Ramps'.
    When ArcMap renders with N classes, it dynamically samples this ramp.
    """
    multi_obj = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    multi = multi_obj.QueryInterface(m_disp.IMultiPartColorRamp)
    multi_cr = multi_obj.QueryInterface(m_disp.IColorRamp)
    multi_cr.Name = name
    n_segments = len(hex_list) - 1
    for i in range(n_segments):
        r1, g1, b1 = hex_to_rgb(hex_list[i])
        r2, g2, b2 = hex_to_rgb(hex_list[i+1])
        part_obj = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        part = part_obj.QueryInterface(m_disp.IAlgorithmicColorRamp)
        part.FromColor = make_rgb(r1, g1, b1)
        part.ToColor = make_rgb(r2, g2, b2)
        part.Algorithm = 1  # esriCIELabAlgorithm
        part_cr = part_obj.QueryInterface(m_disp.IColorRamp)
        multi.AddRamp(part_cr)
    return multi_obj

def create_stepped_multipart_ramp(hex_list, name):
    """
    Creates a stepped discrete MultiPartColorRamp where each slice
    is a uniform solid color (FromColor == ToColor).
    Category: 'Default Ramps'.
    """
    multi_obj = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    multi = multi_obj.QueryInterface(m_disp.IMultiPartColorRamp)
    multi_cr = multi_obj.QueryInterface(m_disp.IColorRamp)
    multi_cr.Name = name
    for h in hex_list:
        r, g, b = hex_to_rgb(h)
        part_obj = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        part = part_obj.QueryInterface(m_disp.IAlgorithmicColorRamp)
        part.FromColor = make_rgb(r, g, b)
        part.ToColor = make_rgb(r, g, b)
        part.Algorithm = 1
        part_cr = part_obj.QueryInterface(m_disp.IColorRamp)
        multi.AddRamp(part_cr)
    return multi_obj

def create_fill_symbol(hex_c):
    r, g, b = hex_to_rgb(hex_c)
    fill_obj = comtypes.client.CreateObject("esriDisplay.SimpleFillSymbol")
    fill = fill_obj.QueryInterface(m_disp.ISimpleFillSymbol)
    fill.Color = make_rgb(r, g, b)
    fill.Style = 0  # esriSFSSolid

    line_obj = comtypes.client.CreateObject("esriDisplay.SimpleLineSymbol")
    line = line_obj.QueryInterface(m_disp.ISimpleLineSymbol)
    line.Color = make_rgb(110, 110, 110)
    line.Width = 0.4
    line.Style = 0  # esriSLSSolid
    fill.Outline = line_obj.QueryInterface(m_disp.ILineSymbol)
    return fill_obj

def clean_style_database(target_path):
    ldb = target_path[:-6] + ".ldb" if target_path.endswith(".style") else target_path + ".ldb"
    if os.path.isfile(ldb):
        try: os.remove(ldb)
        except: pass
    if os.path.isfile(target_path):
        try: os.remove(target_path)
        except: pass
        time.sleep(0.05)
    shutil.copyfile(TEMPLATE_STYLE, target_path)

    conn = comtypes.client.CreateObject("ADODB.Connection")
    conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + target_path)
    for tbl in ["Color Ramps", "Colors", "Fill Symbols"]:
        rs = comtypes.client.CreateObject("ADODB.Recordset")
        rs.Open("SELECT * FROM [" + tbl + "]", conn, 1, 3)
        while not rs.EOF:
            rs.Delete()
            rs.MoveNext()
        rs.Close()
    conn.Close()
    del conn
    gc.collect()

def build_element_style(target_path, style_list, element_name):
    clean_style_database(target_path)

    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sg_storage = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sg_storage.TargetFile = target_path
    sg_storage.AddFile(target_path)

    ramp_count = 0
    color_count = 0
    fill_count = 0

    for s in style_list:
        s_id = s.get("id", "")
        s_name_en = s.get("name_en") or s_id
        classes_map = s.get("classes", {})

        # Highest available class tier for maximum continuous fidelity (usually 11 or 7)
        full_hex_list = classes_map.get("11") or classes_map.get(11) or \
                        classes_map.get("9") or classes_map.get(9) or \
                        classes_map.get("7") or classes_map.get(7) or \
                        classes_map.get("5") or classes_map.get(5)
        if not full_hex_list:
            continue

        # 1. Smooth Continuous Color Ramp (Registered under 'Default Ramps')
        smooth_name = u"Climate: %s - %s" % (element_name, s_name_en)
        r_smooth = create_smooth_multipart_ramp(full_hex_list, smooth_name)
        item_sm = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
        it_sm = item_sm.QueryInterface(m_disp.IStyleGalleryItem)
        it_sm.Name = smooth_name
        it_sm.Category = u"Default Ramps"
        it_sm.Item = r_smooth
        sg.AddItem(it_sm)
        ramp_count += 1

        # 2. Stepped Discrete Color Ramp (Registered under 'Default Ramps')
        stepped_name = u"Climate: %s - %s (Stepped)" % (element_name, s_name_en)
        r_stepped = create_stepped_multipart_ramp(full_hex_list, stepped_name)
        item_st = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
        it_st = item_st.QueryInterface(m_disp.IStyleGalleryItem)
        it_st.Name = stepped_name
        it_st.Category = u"Default Ramps"
        it_st.Item = r_stepped
        sg.AddItem(it_st)
        ramp_count += 1

        # 3. Add representative Colors & Fill Symbols (7 classes or 5 classes)
        sample_hexes = classes_map.get("7") or classes_map.get(7) or classes_map.get("5") or classes_map.get(5)
        if sample_hexes:
            tot = len(sample_hexes)
            for idx, hex_c in enumerate(sample_hexes):
                r, g, b = hex_to_rgb(hex_c)
                c_label = u"Climate: %s - %s [%d/%d]" % (element_name, s_name_en, idx + 1, tot)
                f_label = u"Climate: %s - %s Zone %d/%d Fill" % (element_name, s_name_en, idx + 1, tot)

                # Add Color
                rgb_obj = make_rgb(r, g, b)
                it_col = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                it_c_i = it_col.QueryInterface(m_disp.IStyleGalleryItem)
                it_c_i.Name = c_label
                it_c_i.Category = u"Default Ramps"
                it_c_i.Item = rgb_obj
                sg.AddItem(it_c_i)
                color_count += 1

                # Add Fill Symbol
                fill_obj = create_fill_symbol(hex_c)
                it_f = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                it_f_i = it_f.QueryInterface(m_disp.IStyleGalleryItem)
                it_f_i.Name = f_label
                it_f_i.Category = u"Default Ramps"
                it_f_i.Item = fill_obj
                sg.AddItem(it_f_i)
                fill_count += 1

    sg.SaveStyle(target_path, "Color Ramps", "")
    sg.SaveStyle(target_path, "Colors", "")
    sg.SaveStyle(target_path, "Fill Symbols", "")
    del sg, sg_storage, sg_obj
    gc.collect()
    time.sleep(0.05)
    print("SUCCESS: %s -> %d Color Ramps | %d Colors | %d Fill Symbols" % (
        os.path.basename(target_path), ramp_count, color_count, fill_count
    ))
    return ramp_count, color_count, fill_count

def build_master_style(target_path):
    clean_style_database(target_path)

    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sg_storage = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sg_storage.TargetFile = target_path
    sg_storage.AddFile(target_path)

    ramp_count = 0
    color_count = 0
    fill_count = 0

    for elem in gcs.CLIMATE_ELEMENTS_STYLES:
        elem_name = elem.get("name_en", "Climate")
        styles = elem.get("styles", [])

        for s in styles:
            s_name_en = s.get("name_en") or s.get("id", "")
            classes_map = s.get("classes", {})
            full_hex_list = classes_map.get("11") or classes_map.get(11) or \
                            classes_map.get("9") or classes_map.get(9) or \
                            classes_map.get("7") or classes_map.get(7) or \
                            classes_map.get("5") or classes_map.get(5)
            if not full_hex_list:
                continue

            # 1. Smooth Continuous Color Ramp
            smooth_name = u"Climate: %s - %s" % (elem_name, s_name_en)
            r_smooth = create_smooth_multipart_ramp(full_hex_list, smooth_name)
            item_sm = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            it_sm = item_sm.QueryInterface(m_disp.IStyleGalleryItem)
            it_sm.Name = smooth_name
            it_sm.Category = u"Default Ramps"
            it_sm.Item = r_smooth
            sg.AddItem(it_sm)
            ramp_count += 1

            # 2. Stepped Discrete Color Ramp
            stepped_name = u"Climate: %s - %s (Stepped)" % (elem_name, s_name_en)
            r_stepped = create_stepped_multipart_ramp(full_hex_list, stepped_name)
            item_st = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            it_st = item_st.QueryInterface(m_disp.IStyleGalleryItem)
            it_st.Name = stepped_name
            it_st.Category = u"Default Ramps"
            it_st.Item = r_stepped
            sg.AddItem(it_st)
            ramp_count += 1

            # Colors & Fills
            sample_hexes = classes_map.get("7") or classes_map.get(7) or classes_map.get("5") or classes_map.get(5)
            if sample_hexes:
                tot = len(sample_hexes)
                for idx, hex_c in enumerate(sample_hexes):
                    r, g, b = hex_to_rgb(hex_c)
                    c_label = u"Climate: %s - %s [%d/%d]" % (elem_name, s_name_en, idx + 1, tot)
                    f_label = u"Climate: %s - %s Zone %d/%d Fill" % (elem_name, s_name_en, idx + 1, tot)

                    rgb_obj = make_rgb(r, g, b)
                    it_col = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                    it_c_i = it_col.QueryInterface(m_disp.IStyleGalleryItem)
                    it_c_i.Name = c_label
                    it_c_i.Category = u"Default Ramps"
                    it_c_i.Item = rgb_obj
                    sg.AddItem(it_c_i)
                    color_count += 1

                    fill_obj = create_fill_symbol(hex_c)
                    it_f = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
                    it_f_i = it_f.QueryInterface(m_disp.IStyleGalleryItem)
                    it_f_i.Name = f_label
                    it_f_i.Category = u"Default Ramps"
                    it_f_i.Item = fill_obj
                    sg.AddItem(it_f_i)
                    fill_count += 1

    sg.SaveStyle(target_path, "Color Ramps", "")
    sg.SaveStyle(target_path, "Colors", "")
    sg.SaveStyle(target_path, "Fill Symbols", "")
    del sg, sg_storage, sg_obj
    gc.collect()
    time.sleep(0.05)
    print("SUCCESS MASTER: %s -> %d Color Ramps | %d Colors | %d Fill Symbols" % (
        os.path.basename(target_path), ramp_count, color_count, fill_count
    ))

if __name__ == "__main__":
    print("=================================================================")
    print("GENERATING TRUE NATIVE ARCMAP .STYLE DATABASES (CATEGORY: Default Ramps)")
    print("=================================================================")

    for elem in gcs.CLIMATE_ELEMENTS_STYLES:
        folder = elem.get("folder", "")
        name_en = elem.get("name_en", "")
        styles = elem.get("styles", [])
        fname = folder + ".style"

        p_out = os.path.join(OUT_STYLE_DIR, fname)
        p_cons = os.path.join(CONSOLIDATED_DIR, fname)
        elem_dir = os.path.join(STYLE_DIR, folder)
        p_elem = os.path.join(elem_dir, fname) if os.path.isdir(elem_dir) else None

        build_element_style(p_out, styles, name_en)
        shutil.copyfile(p_out, p_cons)
        if p_elem:
            shutil.copyfile(p_out, p_elem)

    # Master Style
    master_name = "NASA_POWER_Climate_Atlas_Master.style"
    p_master_out = os.path.join(OUT_STYLE_DIR, master_name)
    p_master_cons = os.path.join(CONSOLIDATED_DIR, master_name)

    build_master_style(p_master_out)
    shutil.copyfile(p_master_out, p_master_cons)

    print("\nALL NATIVE ARCMAP STYLES GENERATED SUCCESSFULLY!")
