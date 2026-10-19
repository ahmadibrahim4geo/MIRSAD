# -*- coding: utf-8 -*-
"""
Expand every Color Ramp in each generated .style into individual Colors + Fill Symbols.

- Reads ACTUAL ramp contents from the .style (faithful, no guessing from sources).
- Does NOT touch Color Ramps at all (no add/delete/modify).
- Wipes Colors + Fill Symbols only, then rebuilds:
    Color Name: "<RampName> - Class 01/07 (#HEX)"
    Fill  Name: "<RampName> - Fill 01/07 (#HEX)"
  Zero-padded so items sort grouped per ramp.
- Category: preserves existing thematic categories per palette when possible,
  else falls back to the file's most common Color/Fill category.
- Handles MultiPart (stepped/smooth), single Algorithmic, and generic fallback.

Run with: C:\Python27\ArcGIS10.8\python.exe scripts\styles\expand_ramps_to_colors.py [--test <file>] [--all]
Default: --all (all generated styles, grouped by MD5, process once + sync copies).
"""
from __future__ import unicode_literals
import os
import sys
import shutil
import time
import gc
import hashlib
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STYLE_DIR = os.path.join(BASE_DIR, "style")
RAW_DIR = os.path.join(STYLE_DIR, "Raw_Climate_Styles")

# Official ESRI reference styles: NEVER touch (read-only distribution copies).
OFFICIAL_SKIP = set([
    "meteorological.style", "weather.style", "esri.style",
    "environmental.style", "conservation.style", "forestry.style",
    "military metoc.style", "soils euro.style", "water wastewater.style",
])

import arcpy  # noqa: F401  (ensures ArcGIS license binding)
import comtypes.client

com_dir = r"C:\Program Files (x86)\ArcGIS\Desktop10.8\com"
m_disp = comtypes.client.GetModule(os.path.join(com_dir, "esriDisplay.olb"))


def ole_to_rgb(v):
    v = int(v) & 0xFFFFFF
    return (v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF)


def rgb_to_hex(r, g, b):
    return "#%02X%02X%02X" % (r, g, b)


def make_rgb(r, g, b):
    c_obj = comtypes.client.CreateObject("esriDisplay.RgbColor")
    c = c_obj.QueryInterface(m_disp.IRgbColor)
    c.Red = r
    c.Green = g
    c.Blue = b
    return c_obj.QueryInterface(m_disp.IColor)


def create_fill_symbol(r, g, b):
    fill_obj = comtypes.client.CreateObject("esriDisplay.SimpleFillSymbol")
    fill = fill_obj.QueryInterface(m_disp.ISimpleFillSymbol)
    fill.Color = make_rgb(r, g, b)
    fill.Style = 0  # esriSFSSolid
    line_obj = comtypes.client.CreateObject("esriDisplay.SimpleLineSymbol")
    line = line_obj.QueryInterface(m_disp.ISimpleLineSymbol)
    line.Color = make_rgb(110, 110, 110)
    line.Width = 0.4
    line.Style = 0
    fill.Outline = line_obj.QueryInterface(m_disp.ILineSymbol)
    return fill_obj


def open_gallery(path):
    sg_obj = comtypes.client.CreateObject("esriFramework.StyleGallery")
    sg = sg_obj.QueryInterface(m_disp.IStyleGallery)
    sgs = sg_obj.QueryInterface(m_disp.IStyleGalleryStorage)
    sgs.AddFile(path)
    return sg_obj, sg, sgs


def enum_items(sg, cls, path):
    out = []
    enum = sg.Items(cls, path, "")
    enum.Reset()
    it = enum.Next()
    while it:
        out.append(it)
        it = enum.Next()
    return out


def extract_ramp_colors(ramp_item):
    """Return ordered [(r,g,b), ...] decoded from the stored ramp object."""
    obj = ramp_item.Item
    # 1) MultiPart
    try:
        mp = obj.QueryInterface(m_disp.IMultiPartColorRamp)
        n = int(mp.NumberOfRamps)
        if n > 0:
            pairs = []
            ok = True
            for i in range(n):
                try:
                    part = mp.Ramp(i).QueryInterface(m_disp.IAlgorithmicColorRamp)
                    fc = part.FromColor.QueryInterface(m_disp.IColor)
                    tc = part.ToColor.QueryInterface(m_disp.IColor)
                    pairs.append((ole_to_rgb(fc.RGB), ole_to_rgb(tc.RGB)))
                except Exception:
                    ok = False
                    break
            if ok and pairs:
                if all(a == b for a, b in pairs):
                    return [a for a, b in pairs]  # stepped
                return [a for a, b in pairs] + [pairs[-1][1]]  # smooth
    except Exception:
        pass
    # 2) Single Algorithmic (From -> To)
    try:
        alg = obj.QueryInterface(m_disp.IAlgorithmicColorRamp)
        fc = alg.FromColor.QueryInterface(m_disp.IColor)
        tc = alg.ToColor.QueryInterface(m_disp.IColor)
        c1, c2 = ole_to_rgb(fc.RGB), ole_to_rgb(tc.RGB)
        if c1 == c2:
            return [c1]
        return [c1, c2]
    except Exception:
        pass
    # 3) Generic fallback: sample Size (or 7)
    try:
        cr = obj.QueryInterface(m_disp.IColorRamp)
        size = 0
        try:
            size = int(cr.Size)
        except Exception:
            size = 0
        if size is None or size <= 0:
            size = 7
        size = max(2, min(size, 25))
        cr.Size = size
        cr.CreateRamp()
        ec = cr.Colors
        ec.Reset()
        cols = []
        c = ec.Next()
        while c:
            try:
                ic = c.QueryInterface(m_disp.IColor)
                cols.append(ole_to_rgb(ic.RGB))
            except Exception:
                pass
            c = ec.Next()
        if cols:
            return cols
    except Exception:
        pass
    return []


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_targets():
    targets = []
    for root, dirs, files in os.walk(STYLE_DIR):
        if "Raw_Climate_Styles" in root:
            continue
        for f in files:
            if f.lower().endswith(".style") and f.lower() not in OFFICIAL_SKIP:
                targets.append(os.path.join(root, f))
    # root master too
    root_master = os.path.join(BASE_DIR, "NASA_POWER_Climate_Atlas_Master.style")
    if os.path.isfile(root_master):
        targets.append(root_master)
    # also top-level consolidated outside style/ if exists
    cons1 = os.path.join(BASE_DIR, "All_ArcMap_Styles_Consolidated")
    if os.path.isdir(cons1):
        for f in os.listdir(cons1):
            if f.lower().endswith(".style") and f.lower() not in OFFICIAL_SKIP:
                targets.append(os.path.join(cons1, f))
    # dedupe
    seen = set()
    uniq = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return sorted(uniq)


def process_one_style(path):
    # --- open and read ramps + existing cats ---
    sg_obj, sg, sgs = open_gallery(path)
    ramps = enum_items(sg, "Color Ramps", path)
    colors_before = enum_items(sg, "Colors", path)
    fills_before = enum_items(sg, "Fill Symbols", path)

    ramp_data = []  # (ramp_name, [(r,g,b)])
    for r in ramps:
        rgb_list = extract_ramp_colors(r)
        if not rgb_list:
            print("  WARNING: could not decode ramp: %s (skipped)" % r.Name)
            continue
        ramp_data.append((r.Name, r.Category, rgb_list))
    ramp_data.sort(key=lambda x: x[0])

    # --- category mapping from existing items ---
    pal_to_ccat = {}
    pal_to_fcat = {}
    ccat_counter = Counter()
    fcat_counter = Counter()
    for c in colors_before:
        ccat_counter[c.Category] += 1
        base = c.Name.split(" - ")[0].strip() if " - " in c.Name else ""
        if base and base not in pal_to_ccat:
            pal_to_ccat[base] = c.Category
    for fl in fills_before:
        fcat_counter[fl.Category] += 1
        base = fl.Name.split(" - ")[0].strip() if " - " in fl.Name else ""
        if base and base not in pal_to_fcat:
            pal_to_fcat[base] = fl.Category
    default_ccat = ccat_counter.most_common(1)[0][0] if ccat_counter else "Default"
    default_fcat = fcat_counter.most_common(1)[0][0] if fcat_counter else "Default"

    # longest-match palette lookup
    pal_keys = sorted(set(list(pal_to_ccat.keys()) + list(pal_to_fcat.keys())), key=len, reverse=True)

    def cats_for_ramp(ramp_name):
        cc = default_ccat
        fc = default_fcat
        for pal in pal_keys:
            if pal and pal in ramp_name:
                if pal in pal_to_ccat:
                    cc = pal_to_ccat[pal]
                if pal in pal_to_fcat:
                    fc = pal_to_fcat[pal]
                break
        return cc, fc

    n_ramps = len(ramps)
    n_decoded = len(ramp_data)
    exp_colors = sum(len(x[2]) for x in ramp_data)

    # release gallery before ADODB wipe
    del sg, sgs, sg_obj, ramps, colors_before, fills_before
    gc.collect()

    # --- wipe Colors + Fill Symbols only (ramps untouched) ---
    conn = comtypes.client.CreateObject("ADODB.Connection")
    conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + path)
    for tbl in ["Colors", "Fill Symbols"]:
        rs = comtypes.client.CreateObject("ADODB.Recordset")
        rs.Open("SELECT * FROM [" + tbl + "]", conn, 1, 3)
        while not rs.EOF:
            rs.Delete()
            rs.MoveNext()
        rs.Close()
    conn.Close()
    del conn, rs
    gc.collect()

    # --- re-add expanded colors/fills ---
    sg_obj2, sg2, sgs2 = open_gallery(path)
    try:
        sgs2.TargetFile = path
    except Exception:
        pass
    cc = 0
    fc = 0
    for ramp_name, ramp_cat, rgb_list in ramp_data:
        N = len(rgb_list)
        ccat, fcat = cats_for_ramp(ramp_name)
        for idx, (r, g, b) in enumerate(rgb_list):
            hx = rgb_to_hex(r, g, b)
            c_name = u"%s - Class %02d/%02d (%s)" % (ramp_name, idx + 1, N, hx)
            f_name = u"%s - Fill %02d/%02d (%s)" % (ramp_name, idx + 1, N, hx)
            it_c = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            ic = it_c.QueryInterface(m_disp.IStyleGalleryItem)
            ic.Name = c_name
            ic.Category = ccat
            ic.Item = make_rgb(r, g, b)
            sg2.AddItem(ic)
            cc += 1
            it_f = comtypes.client.CreateObject("esriFramework.StyleGalleryItem")
            iff = it_f.QueryInterface(m_disp.IStyleGalleryItem)
            iff.Name = f_name
            iff.Category = fcat
            iff.Item = create_fill_symbol(r, g, b)
            sg2.AddItem(iff)
            fc += 1
        del ccat, fcat
    sg2.SaveStyle(path, "Colors", "")
    sg2.SaveStyle(path, "Fill Symbols", "")
    del sg2, sgs2, sg_obj2
    gc.collect()
    time.sleep(0.05)
    print("SUCCESS: %s | Ramps kept=%d (decoded %d) -> Colors=%d Fills=%d" % (
        os.path.basename(path), n_ramps, n_decoded, cc, fc))
    return n_ramps, cc, fc


def main():
    args = sys.argv[1:]
    if "--test" in args:
        i = args.index("--test")
        t = args[i + 1]
        process_one_style(t)
        return
    targets = collect_targets()
    print("Found %d .style files (excluding Raw)." % len(targets))
    # group by content hash: process once, copy to siblings
    groups = defaultdict(list)
    for t in targets:
        try:
            groups[md5_of(t)].append(t)
        except Exception as e:
            print("HASH FAIL %s: %s" % (t, e))
    print("Unique contents: %d groups." % len(groups))
    for h, paths in sorted(groups.items(), key=lambda kv: kv[1][0]):
        rep = sorted(paths)[0]
        print("\n== GROUP (%d files) rep=%s ==" % (len(paths), os.path.relpath(rep, BASE_DIR)))
        process_one_style(rep)
        for other in sorted(paths)[1:]:
            try:
                ldb = other[:-6] + ".ldb" if other.endswith(".style") else other + ".ldb"
                if os.path.isfile(ldb):
                    os.remove(ldb)
            except Exception:
                pass
            shutil.copyfile(rep, other)
            print("  synced -> %s" % os.path.relpath(other, BASE_DIR))
            gc.collect()


if __name__ == "__main__":
    main()
