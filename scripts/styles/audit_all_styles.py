# -*- coding: utf-8 -*-
import os
import sys
import comtypes.client

base_dir = r"D:\My Software\NASA POWER Climate Atlas Generator"

all_styles = []
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(".style") and "Raw_Climate_Styles" not in root and ".system_generated" not in root:
            all_styles.append(os.path.join(root, f))

report = []
for p in sorted(all_styles):
    rel = os.path.relpath(p, base_dir)
    size = os.path.getsize(p)
    try:
        conn = comtypes.client.CreateObject("ADODB.Connection")
        conn.Open("Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" + p)
        rs = comtypes.client.CreateObject("ADODB.Recordset")
        
        rs.Open("SELECT COUNT(*) FROM [Color Ramps]", conn)
        ramps = rs.Fields[0].Value
        rs.Close()
        
        rs.Open("SELECT COUNT(*) FROM [Colors]", conn)
        colors = rs.Fields[0].Value
        rs.Close()
        
        rs.Open("SELECT COUNT(*) FROM [Fill Symbols]", conn)
        fills = rs.Fields[0].Value
        rs.Close()
        
        # Check YlOrRd in Temperature or Master
        has_ylorrd = False
        if "Temperature" in rel or "Master" in rel:
            rs.Open("SELECT COUNT(*) FROM [Color Ramps] WHERE [Name] LIKE '%YlOrRd%'", conn)
            has_ylorrd = (rs.Fields[0].Value > 0)
            rs.Close()
            
        conn.Close()
        report.append((rel, size, ramps, colors, fills, has_ylorrd))
    except Exception as e:
        report.append((rel, size, -1, -1, -1, str(e)))

print("\n" + "=" * 115)
print("%-65s | %10s | %6s | %6s | %6s | %s" % (
    "File Path", "Size", "Ramps", "Colors", "Fills", "YlOrRd Included"
))
print("=" * 115)
for r in report:
    yl_str = "YES" if r[5] is True else ("-" if r[5] is False else str(r[5]))
    print("%-65s | %10d | %6d | %6d | %6d | %s" % (
        r[0], r[1], r[2], r[3], r[4], yl_str
    ))
print("=" * 115)
