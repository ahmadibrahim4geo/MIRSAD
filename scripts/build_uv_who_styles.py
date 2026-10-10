# -*- coding: utf-8 -*-
"""Build UV WHO ArcMap .styles (ArcMap 10.8 + comtypes).

Outputs (style/00_Main_Element_Styles/):
  UV_WHO_16Class.style - stepped 16-color ramp + 16 fill + 16 outline colors + 16 symbols
  UV_WHO_5Class.style  - stepped 5-color WHO ramp + 5 fill colors + 5 symbols
                        (outlines inline in symbols; user orange #F79240 kept)

Rule: 5-class colors are the per-band MAXIMUM of the 16-class gradients.
Usage: C:\\Python27\\ArcGIS10.8\\python.exe build_uv_who_styles.py [16|5|all]
"""
import os
import shutil
import sys
import time
import gc

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "style", "00_Main_Element_Styles")
TEMPLATE_STYLE = os.path.join(BASE, "style", "Raw_Climate_Styles", "Meteorological.style")

LABELS16 = ["0-1 Low", "2 Low",
            "3 Moderate", "4 Moderate", "5 Moderate",
            "6 High", "7 High",
            "8 Very High", "9 Very High", "10 Very High",
            "11 Extreme", "12 Extreme", "13 Extreme",
            "14 Extreme", "15 Extreme", "16+ Extreme"]
FILLS16 = ["#90FF66", "#299500",
           "#FFFDE5", "#FFF470", "#F7E400",
           "#FBCDA7", "#F79240",
           "#FF7083", "#FF5269", "#D8001D",
           "#C7B3E6", "#B498DD", "#A07DD4", "#8D62CB", "#7947C2", "#6B499D"]
LABELS5 = ["1 Low (0-2)", "2 Moderate (3-5)", "3 High (6-7)",
           "4 Very High (8-10)", "5 Extreme (11+)"]
FILLS5 = ["#299500", "#F7E400", "#F79240", "#D8001D", "#6B499D"]

import arcpy  # noqa: F401
import comtypes.client

com_dir = r"C:\Program Files (x86)\ArcGIS\Desktop10.8\com"
m_disp = comtypes.client.GetModule(os.path.join(com_dir, "esriDisplay.olb"))


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def darker(h, t=0.35):
    r, g, b = hex_to_rgb(h)
    return (int(round(r * (1 - t))), int(round(g * (1 - t))), int(round(b * (1 - t))))


def make_rgb(r, g, b):
    c_obj = comtypes.client.CreateObject("esriDisplay.RgbColor")
    c = c_obj.QueryInterface(m_disp.IRgbColor)
    c.Red = r
    c.Green = g
    c.Blue = b
    return c_obj.QueryInterface(m_disp.IColor)


def new_item(name, category, obj):
    it = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
    it_s = it.QueryInterface(m_disp.IStyleGalleryItem)
    it_s.Name = name
    it_s.Category = category
    it_s.Item = obj
    return it_s


def build(target, ramp_name, fills, labels, tags, with_outline_colors):
    ldb = target[:-6] + ".ldb"
    for p in [ldb, target]:
        if os.path.isfile(p):
            try:
                os.remove(p)
            except Exception:
                pass
            time.sleep(0.05)
    shutil.copyfile(TEMPLATE_STYLE, target)
    conn = comtypes.client.CreateObject("ADODB.Connection")
    conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + target)
    for tbl in ["Color Ramps", "Colors", "Fill Symbols", "Line Symbols",
                "Marker Symbols", "Text Symbols"]:
        try:
            conn.Execute("DELETE FROM [" + tbl + "]")
        except Exception:
            pass
    conn.Close()
    del conn
    gc.collect()
    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sg_storage = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sg_storage.TargetFile = target
    sg_storage.AddFile(target)
    multi_obj = comtypes.client.CreateObject("esriDisplay.MultiPartColorRamp")
    multi = multi_obj.QueryInterface(m_disp.IMultiPartColorRamp)
    multi_cr = multi_obj.QueryInterface(m_disp.IColorRamp)
    multi_cr.Name = ramp_name
    for h in fills:
        r, g, b = hex_to_rgb(h)
        part_obj = comtypes.client.CreateObject("esriDisplay.AlgorithmicColorRamp")
        part = part_obj.QueryInterface(m_disp.IAlgorithmicColorRamp)
        part.FromColor = make_rgb(r, g, b)
        part.ToColor = make_rgb(r, g, b)
        part.Algorithm = 1
        multi.AddRamp(part_obj.QueryInterface(m_disp.IColorRamp))
    sg.AddItem(new_item(ramp_name, u"Default Ramps",
                        multi_obj.QueryInterface(m_disp.IColorRamp)))
    for tag, h, lab in zip(tags, fills, labels):
        r, g, b = hex_to_rgb(h)
        rgb = comtypes.client.CreateObject("esriDisplay.RgbColor")
        c = rgb.QueryInterface(m_disp.IRgbColor)
        c.Red = r
        c.Green = g
        c.Blue = b
        sg.AddItem(new_item(unicode(tag + " Fill " + lab), u"UV WHO Fill Colors",
                            rgb.QueryInterface(m_disp.IColor)))
        orr, ogg, obb = darker(h)
        if with_outline_colors:
            orgb = comtypes.client.CreateObject("esriDisplay.RgbColor")
            oc = orgb.QueryInterface(m_disp.IRgbColor)
            oc.Red = orr
            oc.Green = ogg
            oc.Blue = obb
            sg.AddItem(new_item(unicode(tag + " Outline " + lab), u"UV WHO Outline Colors",
                                orgb.QueryInterface(m_disp.IColor)))
        fill_obj = comtypes.client.CreateObject("esriDisplay.SimpleFillSymbol")
        fill = fill_obj.QueryInterface(m_disp.ISimpleFillSymbol)
        fill.Color = make_rgb(r, g, b)
        fill.Style = 0
        line_obj = comtypes.client.CreateObject("esriDisplay.SimpleLineSymbol")
        line = line_obj.QueryInterface(m_disp.ISimpleLineSymbol)
        line.Color = make_rgb(orr, ogg, obb)
        line.Width = 0.4
        line.Style = 0
        fill.Outline = line_obj.QueryInterface(m_disp.ILineSymbol)
        sg.AddItem(new_item(unicode(tag + " Symbol " + lab), u"UV WHO Fill Symbols", fill_obj))
    sg.SaveStyle(target, "Color Ramps", "")
    sg.SaveStyle(target, "Colors", "")
    sg.SaveStyle(target, "Fill Symbols", "")
    print("OK: " + target)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    if mode in ("16", "all"):
        build(os.path.join(OUT_DIR, "UV_WHO_16Class.style"), u"UV WHO 16-Class",
              FILLS16, LABELS16, ["Color %02d" % (i + 1) for i in range(16)], True)
    if mode in ("5", "all"):
        build(os.path.join(OUT_DIR, "UV_WHO_5Class.style"), u"UV WHO 5-Class",
              FILLS5, LABELS5, ["Color %d" % (i + 1) for i in range(5)], False)


if __name__ == "__main__":
    main()
