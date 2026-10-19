# -*- coding: utf-8 -*-
"""
NASA POWER & Open-Meteo Climate Atlas Generator
Comprehensive Climate Styles & Cartographic Color Palette Generator

Generates high-precision, cartographically balanced, perceptually uniform styles
for ArcGIS Desktop (10.x / 10.8), ArcGIS Pro, and QGIS.
Supported Formats: .style (ArcMap Style Database), .clr, .qml, .sld, .json, .csv.

Contains 125 Scientific Palettes across 11 Climate Elements.
Each palette supports 9 class tiers: 3, 4, 5, 6, 7, 8, 9, 10, 11 classes!
Total Color Ramps: 125 x 9 x 2 (Stepped + Smooth) = 2,250 Color Ramps!
"""
from __future__ import unicode_literals
import sys
import os
import io
import json

PY2 = sys.version_info[0] == 2
if PY2:
    text_type = unicode
else:
    text_type = str

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def open_utf8(path, mode="w"):
    if PY2:
        return io.open(path, mode, encoding="utf-8")
    else:
        return open(path, mode, encoding="utf-8")

def hex_to_rgb(hex_code):
    h = hex_code.strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def write_clr(path, hex_colors, start_val=1):
    with open_utf8(path, "w") as f:
        for idx, hex_c in enumerate(hex_colors):
            r, g, b = hex_to_rgb(hex_c)
            f.write(u"%d %d %d %d\n" % (start_val + idx, r, g, b))

TEMPERATURE_STYLES = [
  {
    "category": "Sequential", 
    "name_ar": "تدرج أحمر دافئ متتابع", 
    "source": "ColorBrewer Reds", 
    "classes": {
      "3": [
        "#FCBBA1", 
        "#ED4E38", 
        "#67000D"
      ], 
      "4": [
        "#FCBBA1", 
        "#FC7857", 
        "#CB2420", 
        "#67000D"
      ], 
      "5": [
        "#FCBBA1", 
        "#FC8868", 
        "#ED4E38", 
        "#B31719", 
        "#67000D"
      ], 
      "6": [
        "#FCBBA1", 
        "#FC9272", 
        "#FB6A4A", 
        "#DE2D26", 
        "#A50F15", 
        "#67000D"
      ], 
      "7": [
        "#FCBBA1", 
        "#FC997A", 
        "#FC7857", 
        "#ED4E38", 
        "#CB2420", 
        "#9A0C14", 
        "#67000D"
      ], 
      "8": [
        "#FCBBA1", 
        "#FD9E7F", 
        "#FC8261", 
        "#F76245", 
        "#E2382B", 
        "#BD1D1C", 
        "#930913", 
        "#67000D"
      ], 
      "9": [
        "#FCBBA1", 
        "#FDA283", 
        "#FC8868", 
        "#FB6F4F", 
        "#ED4E38", 
        "#D72A24", 
        "#B31719", 
        "#8D0812", 
        "#67000D"
      ], 
      "10": [
        "#FCBBA1", 
        "#FDA487", 
        "#FC8E6D", 
        "#FC7857", 
        "#F55E42", 
        "#E53D2E", 
        "#CB2420", 
        "#AB1317", 
        "#890712", 
        "#67000D"
      ], 
      "11": [
        "#FCBBA1", 
        "#FDA789", 
        "#FC9272", 
        "#FC7F5E", 
        "#FB6A4A", 
        "#ED4E38", 
        "#DE2D26", 
        "#C11F1D", 
        "#A50F15", 
        "#850612", 
        "#67000D"
      ]
    }, 
    "name_en": "Sequential Warm Red", 
    "id": "Temp_Seq_WarmRed"
  }, 
  {
    "category": "Sequential", 
    "name_ar": "تدرج برتقالي عنبري حراري", 
    "source": "ColorBrewer Oranges", 
    "classes": {
      "3": [
        "#FDD0A2", 
        "#F98D43", 
        "#7F2704"
      ], 
      "4": [
        "#FDD0A2", 
        "#FDB273", 
        "#E95E0D", 
        "#7F2704"
      ], 
      "5": [
        "#FDD0A2", 
        "#FDB87E", 
        "#F98D43", 
        "#DF5105", 
        "#7F2704"
      ], 
      "6": [
        "#FDD0A2", 
        "#FDBB84", 
        "#FDAE6B", 
        "#F16913", 
        "#D94801", 
        "#7F2704"
      ], 
      "7": [
        "#FDD0A2", 
        "#FDBF89", 
        "#FDB273", 
        "#F98D43", 
        "#E95E0D", 
        "#C94202", 
        "#7F2704"
      ], 
      "8": [
        "#FDD0A2", 
        "#FDC18D", 
        "#FDB579", 
        "#FCA560", 
        "#F37423", 
        "#E35708", 
        "#BE3E03", 
        "#7F2704"
      ], 
      "9": [
        "#FDD0A2", 
        "#FDC38F", 
        "#FDB87E", 
        "#FDB06E", 
        "#F98D43", 
        "#EE6511", 
        "#DF5105", 
        "#B63B03", 
        "#7F2704"
      ], 
      "10": [
        "#FDD0A2", 
        "#FDC491", 
        "#FDBA81", 
        "#FDB273", 
        "#FC9F59", 
        "#F5792B", 
        "#E95E0D", 
        "#DC4C03", 
        "#B03903", 
        "#7F2704"
      ], 
      "11": [
        "#FDD0A2", 
        "#FDC693", 
        "#FDBB84", 
        "#FDB578", 
        "#FDAE6B", 
        "#F98D43", 
        "#F16913", 
        "#E5590A", 
        "#D94801", 
        "#AB3704", 
        "#7F2704"
      ]
    }, 
    "name_en": "Thermal Amber Orange", 
    "id": "Temp_Seq_AmberOrange"
  }, 
  {
    "category": "Sequential", 
    "name_ar": "تدرج أزرق بارد للحرارة الصغرى", 
    "source": "ColorBrewer Blues", 
    "classes": {
      "3": [
        "#BDD7E7", 
        "#5198C9", 
        "#08306B"
      ], 
      "4": [
        "#BDD7E7", 
        "#7DB7DA", 
        "#2771B2", 
        "#08306B"
      ], 
      "5": [
        "#BDD7E7", 
        "#92C3DE", 
        "#5198C9", 
        "#175DA4", 
        "#08306B"
      ], 
      "6": [
        "#BDD7E7", 
        "#9ECAE1", 
        "#6BAED6", 
        "#3182BD", 
        "#08519C", 
        "#08306B"
      ], 
      "7": [
        "#BDD7E7", 
        "#A3CCE2", 
        "#7DB7DA", 
        "#5198C9", 
        "#2771B2", 
        "#084B94", 
        "#08306B"
      ], 
      "8": [
        "#BDD7E7", 
        "#A7CEE3", 
        "#89BEDC", 
        "#64A8D2", 
        "#3B88C1", 
        "#1F66AA", 
        "#09478E", 
        "#08306B"
      ], 
      "9": [
        "#BDD7E7", 
        "#AACFE3", 
        "#92C3DE", 
        "#72B1D7", 
        "#5198C9", 
        "#2D7CB9", 
        "#175DA4", 
        "#094489", 
        "#08306B"
      ], 
      "10": [
        "#BDD7E7", 
        "#ACD0E4", 
        "#99C7E0", 
        "#7DB7DA", 
        "#60A4D0", 
        "#408CC3", 
        "#2771B2", 
        "#1056A0", 
        "#094286", 
        "#08306B"
      ], 
      "11": [
        "#BDD7E7", 
        "#AED0E4", 
        "#9ECAE1", 
        "#86BCDC", 
        "#6BAED6", 
        "#5198C9", 
        "#3182BD", 
        "#2169AC", 
        "#08519C", 
        "#094083", 
        "#08306B"
      ]
    }, 
    "name_en": "Minimum Cold Temperature", 
    "id": "Temp_Seq_CoolBlue"
  }, 
  {
    "category": "Sequential", 
    "name_ar": "تدرج بنفسجي للصقيع الشديد والتجمد", 
    "source": "ColorBrewer Purples", 
    "classes": {
      "3": [
        "#DADAEB", 
        "#8A82BD", 
        "#3F007D"
      ], 
      "4": [
        "#DADAEB", 
        "#A8A6CF", 
        "#6B55A6", 
        "#3F007D"
      ], 
      "5": [
        "#DADAEB", 
        "#B4B4D7", 
        "#8A82BD", 
        "#5D3997", 
        "#3F007D"
      ], 
      "6": [
        "#DADAEB", 
        "#BCBDDC", 
        "#9E9AC8", 
        "#756BB1", 
        "#54278F", 
        "#3F007D"
      ], 
      "7": [
        "#DADAEB", 
        "#C1C2DF", 
        "#A8A6CF", 
        "#8A82BD", 
        "#6B55A6", 
        "#51228C", 
        "#3F007D"
      ], 
      "8": [
        "#DADAEB", 
        "#C5C5E0", 
        "#AFAED3", 
        "#9893C5", 
        "#7B72B4", 
        "#63459E", 
        "#4E1E8A", 
        "#3F007D"
      ], 
      "9": [
        "#DADAEB", 
        "#C7C8E2", 
        "#B4B4D7", 
        "#A29ECA", 
        "#8A82BD", 
        "#7163AD", 
        "#5D3997", 
        "#4C1B88", 
        "#3F007D"
      ], 
      "10": [
        "#DADAEB", 
        "#C9CAE3", 
        "#B9B9DA", 
        "#A8A6CF", 
        "#958FC3", 
        "#7E75B6", 
        "#6B55A6", 
        "#582F93", 
        "#4B1887", 
        "#3F007D"
      ], 
      "11": [
        "#DADAEB", 
        "#CBCBE4", 
        "#BCBDDC", 
        "#ADABD2", 
        "#9E9AC8", 
        "#8A82BD", 
        "#756BB1", 
        "#654AA0", 
        "#54278F", 
        "#4A1686", 
        "#3F007D"
      ]
    }, 
    "name_en": "Severe Frost & Cryosphere", 
    "id": "Temp_Seq_DeepPurple"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "تدرج الشذوذ الحراري المعتمد لتقرير المناخ السادس", 
    "source": "IPCC AR6 / Nature (Crameri)", 
    "classes": {
      "3": [
        "#4393C3", 
        "#FFFFBF", 
        "#B2182B"
      ], 
      "4": [
        "#053061", 
        "#92C5DE", 
        "#F4A582", 
        "#67001F"
      ], 
      "5": [
        "#053061", 
        "#92C5DE", 
        "#FFFFBF", 
        "#F4A582", 
        "#67001F"
      ], 
      "6": [
        "#053061", 
        "#347CB8", 
        "#92C5DE", 
        "#F4A582", 
        "#C4413C", 
        "#67001F"
      ], 
      "7": [
        "#053061", 
        "#347CB8", 
        "#92C5DE", 
        "#FFFFBF", 
        "#F4A582", 
        "#C4413C", 
        "#67001F"
      ], 
      "8": [
        "#053061", 
        "#2166AC", 
        "#4393C3", 
        "#92C5DE", 
        "#F4A582", 
        "#D6604D", 
        "#B2182B", 
        "#67001F"
      ], 
      "9": [
        "#053061", 
        "#2166AC", 
        "#4393C3", 
        "#92C5DE", 
        "#FFFFBF", 
        "#F4A582", 
        "#D6604D", 
        "#B2182B", 
        "#67001F"
      ], 
      "10": [
        "#053061", 
        "#1A5899", 
        "#347CB8", 
        "#5A9FCA", 
        "#92C5DE", 
        "#F4A582", 
        "#DE725A", 
        "#C4413C", 
        "#9F1128", 
        "#67001F"
      ], 
      "11": [
        "#053061", 
        "#1A5899", 
        "#347CB8", 
        "#5A9FCA", 
        "#92C5DE", 
        "#FFFFBF", 
        "#F4A582", 
        "#DE725A", 
        "#C4413C", 
        "#9F1128", 
        "#67001F"
      ]
    }, 
    "name_en": "IPCC AR6 Temperature Anomaly", 
    "id": "Temp_Div_RdBu_IPCC"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "تدرج كولور بروير الكلاسيكي المتباعد", 
    "source": "ColorBrewer 2.0 (Cynthia Brewer)", 
    "classes": {
      "3": [
        "#74ADD1", 
        "#FFFFBF", 
        "#D73027"
      ], 
      "4": [
        "#313695", 
        "#ABD9E9", 
        "#FDAE61", 
        "#A50026"
      ], 
      "5": [
        "#313695", 
        "#ABD9E9", 
        "#FFFFBF", 
        "#FDAE61", 
        "#A50026"
      ], 
      "6": [
        "#313695", 
        "#5E91C3", 
        "#ABD9E9", 
        "#FDAE61", 
        "#E65135", 
        "#A50026"
      ], 
      "7": [
        "#313695", 
        "#5E91C3", 
        "#ABD9E9", 
        "#FFFFBF", 
        "#FDAE61", 
        "#E65135", 
        "#A50026"
      ], 
      "8": [
        "#313695", 
        "#4575B4", 
        "#74ADD1", 
        "#ABD9E9", 
        "#FDAE61", 
        "#F46D43", 
        "#D73027", 
        "#A50026"
      ], 
      "9": [
        "#313695", 
        "#4575B4", 
        "#74ADD1", 
        "#ABD9E9", 
        "#FFFFBF", 
        "#FDAE61", 
        "#F46D43", 
        "#D73027", 
        "#A50026"
      ], 
      "10": [
        "#313695", 
        "#4265AC", 
        "#5E91C3", 
        "#82B8D7", 
        "#ABD9E9", 
        "#FDAE61", 
        "#F77E4A", 
        "#E65135", 
        "#CA2727", 
        "#A50026"
      ], 
      "11": [
        "#313695", 
        "#4265AC", 
        "#5E91C3", 
        "#82B8D7", 
        "#ABD9E9", 
        "#FFFFBF", 
        "#FDAE61", 
        "#F77E4A", 
        "#E65135", 
        "#CA2727", 
        "#A50026"
      ]
    }, 
    "name_en": "ColorBrewer RdYlBu Classic", 
    "id": "Temp_Div_RdYlBu_Brewer"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "طيف إزري الناعم المريح بصرياً", 
    "source": "Esri Better Colors for Better Mapping", 
    "classes": {
      "3": [
        "#64ABB0", 
        "#FFFFBF", 
        "#EA633E"
      ], 
      "4": [
        "#2B83BA", 
        "#ABDDA4", 
        "#FDAE61", 
        "#D7191C"
      ], 
      "5": [
        "#2B83BA", 
        "#ABDDA4", 
        "#FFFFBF", 
        "#FDAE61", 
        "#D7191C"
      ], 
      "6": [
        "#2B83BA", 
        "#64ABB0", 
        "#ABDDA4", 
        "#FDAE61", 
        "#EA633E", 
        "#D7191C"
      ], 
      "7": [
        "#2B83BA", 
        "#64ABB0", 
        "#ABDDA4", 
        "#FFFFBF", 
        "#FDAE61", 
        "#EA633E", 
        "#D7191C"
      ], 
      "8": [
        "#2B83BA", 
        "#569DB4", 
        "#7EBBAC", 
        "#ABDDA4", 
        "#FDAE61", 
        "#F17D49", 
        "#E45032", 
        "#D7191C"
      ], 
      "9": [
        "#2B83BA", 
        "#569DB4", 
        "#7EBBAC", 
        "#ABDDA4", 
        "#FFFFBF", 
        "#FDAE61", 
        "#F17D49", 
        "#E45032", 
        "#D7191C"
      ], 
      "10": [
        "#2B83BA", 
        "#4D97B5", 
        "#64ABB0", 
        "#8AC4AB", 
        "#ABDDA4", 
        "#FDAE61", 
        "#F48A4F", 
        "#EA633E", 
        "#E1452D", 
        "#D7191C"
      ], 
      "11": [
        "#2B83BA", 
        "#4D97B5", 
        "#64ABB0", 
        "#8AC4AB", 
        "#ABDDA4", 
        "#FFFFBF", 
        "#FDAE61", 
        "#F48A4F", 
        "#EA633E", 
        "#E1452D", 
        "#D7191C"
      ]
    }, 
    "name_en": "Esri Soft Spectral", 
    "id": "Temp_Multi_SpectralMuted"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "تدرج التركواز إلى المرجاني المريح للعين", 
    "source": "Esri Cartographic Design", 
    "classes": {
      "3": [
        "#48D1CC", 
        "#FFF2CE", 
        "#FF5722"
      ], 
      "4": [
        "#006666", 
        "#B2EBF2", 
        "#FFCCBC", 
        "#D84315"
      ], 
      "5": [
        "#006666", 
        "#B2EBF2", 
        "#FFF2CE", 
        "#FFCCBC", 
        "#D84315"
      ], 
      "6": [
        "#006666", 
        "#2BADAB", 
        "#B2EBF2", 
        "#FFCCBC", 
        "#FF7245", 
        "#D84315"
      ], 
      "7": [
        "#006666", 
        "#2BADAB", 
        "#B2EBF2", 
        "#FFF2CE", 
        "#FFCCBC", 
        "#FF7245", 
        "#D84315"
      ], 
      "8": [
        "#006666", 
        "#008B8B", 
        "#48D1CC", 
        "#B2EBF2", 
        "#FFCCBC", 
        "#FF8A65", 
        "#FF5722", 
        "#D84315"
      ], 
      "9": [
        "#006666", 
        "#008B8B", 
        "#48D1CC", 
        "#B2EBF2", 
        "#FFF2CE", 
        "#FFCCBC", 
        "#FF8A65", 
        "#FF5722", 
        "#D84315"
      ], 
      "10": [
        "#006666", 
        "#008282", 
        "#2BADAB", 
        "#69D8D5", 
        "#B2EBF2", 
        "#FFCCBC", 
        "#FF9B7A", 
        "#FF7245", 
        "#F5521F", 
        "#D84315"
      ], 
      "11": [
        "#006666", 
        "#008282", 
        "#2BADAB", 
        "#69D8D5", 
        "#B2EBF2", 
        "#FFF2CE", 
        "#FFCCBC", 
        "#FF9B7A", 
        "#FF7245", 
        "#F5521F", 
        "#D84315"
      ]
    }, 
    "name_en": "Teal to Coral Ergonomic", 
    "id": "Temp_Div_TealCoral"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "تدرج التباين الحراري البنفسجي-البرتقالي", 
    "source": "CPT-City Archive (J.J. Green)", 
    "classes": {
      "3": [
        "#8073AC", 
        "#FEE0B6", 
        "#B35806"
      ], 
      "4": [
        "#2D004B", 
        "#B2ABD2", 
        "#FDB863", 
        "#7F3B08"
      ], 
      "5": [
        "#2D004B", 
        "#B2ABD2", 
        "#FEE0B6", 
        "#FDB863", 
        "#7F3B08"
      ], 
      "6": [
        "#2D004B", 
        "#6B4E9A", 
        "#B2ABD2", 
        "#FDB863", 
        "#C96D0D", 
        "#7F3B08"
      ], 
      "7": [
        "#2D004B", 
        "#6B4E9A", 
        "#B2ABD2", 
        "#FEE0B6", 
        "#FDB863", 
        "#C96D0D", 
        "#7F3B08"
      ], 
      "8": [
        "#2D004B", 
        "#542788", 
        "#8073AC", 
        "#B2ABD2", 
        "#FDB863", 
        "#E08214", 
        "#B35806", 
        "#7F3B08"
      ], 
      "9": [
        "#2D004B", 
        "#542788", 
        "#8073AC", 
        "#B2ABD2", 
        "#FEE0B6", 
        "#FDB863", 
        "#E08214", 
        "#B35806", 
        "#7F3B08"
      ], 
      "10": [
        "#2D004B", 
        "#4A1D78", 
        "#6B4E9A", 
        "#8C81B5", 
        "#B2ABD2", 
        "#FDB863", 
        "#E88F2C", 
        "#C96D0D", 
        "#A65107", 
        "#7F3B08"
      ], 
      "11": [
        "#2D004B", 
        "#4A1D78", 
        "#6B4E9A", 
        "#8C81B5", 
        "#B2ABD2", 
        "#FEE0B6", 
        "#FDB863", 
        "#E88F2C", 
        "#C96D0D", 
        "#A65107", 
        "#7F3B08"
      ]
    }, 
    "name_en": "Extreme Temperature Variance", 
    "id": "Temp_Div_PuOr"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "مقياس باتلو العلمي المحايد إدراكياً", 
    "source": "Fabio Crameri Scientific Colour Maps", 
    "classes": {
      "3": [
        "#001030", 
        "#9ABA1B", 
        "#F6D94E"
      ], 
      "4": [
        "#001030", 
        "#369055", 
        "#F7B800", 
        "#F6D94E"
      ], 
      "5": [
        "#001030", 
        "#1F796A", 
        "#9ABA1B", 
        "#FE8900", 
        "#F6D94E"
      ], 
      "6": [
        "#001030", 
        "#136B72", 
        "#63A33E", 
        "#D2BF00", 
        "#FC6F0C", 
        "#F6D94E"
      ], 
      "7": [
        "#001030", 
        "#156075", 
        "#369055", 
        "#9ABA1B", 
        "#F7B800", 
        "#F86017", 
        "#F6D94E"
      ], 
      "8": [
        "#001030", 
        "#145877", 
        "#2C8361", 
        "#72AB31", 
        "#C2C200", 
        "#FB9E00", 
        "#F4551D", 
        "#F6D94E"
      ], 
      "9": [
        "#001030", 
        "#125279", 
        "#1F796A", 
        "#549C47", 
        "#9ABA1B", 
        "#E0BD00", 
        "#FE8900", 
        "#F24C20", 
        "#F6D94E"
      ], 
      "10": [
        "#001030", 
        "#0F4E7A", 
        "#0E7270", 
        "#369055", 
        "#7AB028", 
        "#B8C300", 
        "#F7B800", 
        "#FF7800", 
        "#F04422", 
        "#F6D94E"
      ], 
      "11": [
        "#001030", 
        "#0D4772", 
        "#136B72", 
        "#2F875E", 
        "#63A33E", 
        "#9ABA1B", 
        "#D2BF00", 
        "#FAA600", 
        "#FC6F0C", 
        "#F25826", 
        "#F6D94E"
      ]
    }, 
    "name_en": "Crameri Batlow Scientific", 
    "id": "Temp_Multi_Thermal_Crameri"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "مقياس روما العلمي المتباعد", 
    "source": "Fabio Crameri Scientific Colour Maps", 
    "classes": {
      "3": [
        "#4393C3", 
        "#FFFFBF", 
        "#F46D43"
      ], 
      "4": [
        "#7E1E7B", 
        "#92C5DE", 
        "#FEE090", 
        "#A50026"
      ], 
      "5": [
        "#7E1E7B", 
        "#92C5DE", 
        "#FFFFBF", 
        "#FEE090", 
        "#A50026"
      ], 
      "6": [
        "#7E1E7B", 
        "#555FA5", 
        "#92C5DE", 
        "#FEE090", 
        "#F98F52", 
        "#A50026"
      ], 
      "7": [
        "#7E1E7B", 
        "#555FA5", 
        "#92C5DE", 
        "#FFFFBF", 
        "#FEE090", 
        "#F98F52", 
        "#A50026"
      ], 
      "8": [
        "#7E1E7B", 
        "#542788", 
        "#4393C3", 
        "#92C5DE", 
        "#FEE090", 
        "#FDAE61", 
        "#F46D43", 
        "#A50026"
      ], 
      "9": [
        "#7E1E7B", 
        "#542788", 
        "#4393C3", 
        "#92C5DE", 
        "#FFFFBF", 
        "#FEE090", 
        "#FDAE61", 
        "#F46D43", 
        "#A50026"
      ], 
      "10": [
        "#7E1E7B", 
        "#602585", 
        "#555FA5", 
        "#5A9FCA", 
        "#92C5DE", 
        "#FEE090", 
        "#FEBB6D", 
        "#F98F52", 
        "#E0583C", 
        "#A50026"
      ], 
      "11": [
        "#7E1E7B", 
        "#602585", 
        "#555FA5", 
        "#5A9FCA", 
        "#92C5DE", 
        "#FFFFBF", 
        "#FEE090", 
        "#FEBB6D", 
        "#F98F52", 
        "#E0583C", 
        "#A50026"
      ]
    }, 
    "name_en": "Crameri Roma Diverging", 
    "id": "Temp_Multi_Roma_Crameri"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "مقياس درجات الحرارة السطحية للمنظمة العالمية للأرصاد", 
    "source": "WMO Technical Regulations WMO-No. 306", 
    "classes": {
      "3": [
        "#000080", 
        "#00FF00", 
        "#800000"
      ], 
      "4": [
        "#000080", 
        "#13E9FF", 
        "#FFE100", 
        "#800000"
      ], 
      "5": [
        "#000080", 
        "#00BFFF", 
        "#00FF00", 
        "#FFA500", 
        "#800000"
      ], 
      "6": [
        "#000080", 
        "#3D82FF", 
        "#3AFFD8", 
        "#E1FF00", 
        "#FF7A00", 
        "#800000"
      ], 
      "7": [
        "#000080", 
        "#3858FF", 
        "#13E9FF", 
        "#00FF00", 
        "#FFE100", 
        "#FF5800", 
        "#800000"
      ], 
      "8": [
        "#000080", 
        "#2734FF", 
        "#12D1FF", 
        "#46FFAA", 
        "#BBFF00", 
        "#FFBF00", 
        "#FF3800", 
        "#800000"
      ], 
      "9": [
        "#000080", 
        "#0000FF", 
        "#00BFFF", 
        "#00FFFF", 
        "#00FF00", 
        "#FFFF00", 
        "#FFA500", 
        "#FF0000", 
        "#800000"
      ], 
      "10": [
        "#000080", 
        "#0000F0", 
        "#349EFF", 
        "#13E9FF", 
        "#45FF90", 
        "#A3FF00", 
        "#FFE100", 
        "#FF8E00", 
        "#F00001", 
        "#800000"
      ], 
      "11": [
        "#000080", 
        "#0000E4", 
        "#3D82FF", 
        "#14D8FF", 
        "#3AFFD8", 
        "#00FF00", 
        "#E1FF00", 
        "#FFCA00", 
        "#FF7A00", 
        "#E40001", 
        "#800000"
      ]
    }, 
    "name_en": "WMO Synoptic Temperature", 
    "id": "Temp_Multi_WMO_Standard"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "المقياس المعتمد للتنبؤات الحرارية بهيئة الأرصاد الأمريكية", 
    "source": "NOAA National Weather Service (NWS)", 
    "classes": {
      "3": [
        "#2C1E5C", 
        "#98FB98", 
        "#8B0000"
      ], 
      "4": [
        "#2C1E5C", 
        "#76ABE8", 
        "#FFE100", 
        "#8B0000"
      ], 
      "5": [
        "#2C1E5C", 
        "#4169E1", 
        "#98FB98", 
        "#FFA500", 
        "#8B0000"
      ], 
      "6": [
        "#2C1E5C", 
        "#4757BE", 
        "#8ED7DB", 
        "#EEFE3D", 
        "#FF8400", 
        "#8B0000"
      ], 
      "7": [
        "#2C1E5C", 
        "#494BA7", 
        "#76ABE8", 
        "#98FB98", 
        "#FFE100", 
        "#FF6B00", 
        "#8B0000"
      ], 
      "8": [
        "#2C1E5C", 
        "#494397", 
        "#5C85E4", 
        "#94E1C9", 
        "#DAFE5D", 
        "#FFBF00", 
        "#FF5700", 
        "#8B0000"
      ], 
      "9": [
        "#2C1E5C", 
        "#483D8B", 
        "#4169E1", 
        "#87CEEB", 
        "#98FB98", 
        "#FFFF00", 
        "#FFA500", 
        "#FF4500", 
        "#8B0000"
      ], 
      "10": [
        "#2C1E5C", 
        "#453986", 
        "#455FCD", 
        "#76ABE8", 
        "#96E7BE", 
        "#CDFD6B", 
        "#FFE100", 
        "#FF9300", 
        "#F23E01", 
        "#8B0000"
      ], 
      "11": [
        "#2C1E5C", 
        "#423781", 
        "#4757BE", 
        "#6590E6", 
        "#8ED7DB", 
        "#98FB98", 
        "#EEFE3D", 
        "#FFCA00", 
        "#FF8400", 
        "#E73901", 
        "#8B0000"
      ]
    }, 
    "name_en": "NOAA NWS Heat Scale", 
    "id": "Temp_Multi_NOAA_NWS"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "تدرج حرارة سطح الأرض من أقمار ناسا", 
    "source": "NASA Earth Science Data Systems (LST)", 
    "classes": {
      "3": [
        "#0C0887", 
        "#CB4679", 
        "#F0F921"
      ], 
      "4": [
        "#0C0887", 
        "#9B199C", 
        "#EC7955", 
        "#F0F921"
      ], 
      "5": [
        "#0C0887", 
        "#7D03A8", 
        "#CB4679", 
        "#F89441", 
        "#F0F921"
      ], 
      "6": [
        "#0C0887", 
        "#6A02A5", 
        "#B02A90", 
        "#E06463", 
        "#FAA43A", 
        "#F0F921"
      ], 
      "7": [
        "#0C0887", 
        "#5D02A3", 
        "#9B199C", 
        "#CB4679", 
        "#EC7955", 
        "#FCAE35", 
        "#F0F921"
      ], 
      "8": [
        "#0C0887", 
        "#5303A2", 
        "#8A0DA3", 
        "#B8328A", 
        "#DA5C6A", 
        "#F3894A", 
        "#FCB631", 
        "#F0F921"
      ], 
      "9": [
        "#0C0887", 
        "#4B03A1", 
        "#7D03A8", 
        "#A82296", 
        "#CB4679", 
        "#E56B5D", 
        "#F89441", 
        "#FDBB2D", 
        "#F0F921"
      ], 
      "10": [
        "#0C0887", 
        "#46049E", 
        "#7302A6", 
        "#9B199C", 
        "#BC3786", 
        "#D7576D", 
        "#EC7955", 
        "#F99D3E", 
        "#FCC22C", 
        "#F0F921"
      ], 
      "11": [
        "#0C0887", 
        "#41049C", 
        "#6A02A5", 
        "#9011A1", 
        "#B02A90", 
        "#CB4679", 
        "#E06463", 
        "#F1844E", 
        "#FAA43A", 
        "#FBC82B", 
        "#F0F921"
      ]
    }, 
    "name_en": "NASA MODIS Land Surface Temp", 
    "id": "Temp_Multi_NASA_LST"
  }, 
  {
    "category": "Sequential", 
    "name_ar": "مقياس مخاطر الموجات الحارة الشديدة والإجهاد الحيوي", 
    "source": "WMO / WHO Health Heatwave Guidance", 
    "classes": {
      "3": [
        "#FFFFB2", 
        "#FC4E2A", 
        "#490000"
      ], 
      "4": [
        "#FFFFB2", 
        "#FE9A41", 
        "#D21220", 
        "#490000"
      ], 
      "5": [
        "#FFFFB2", 
        "#FEB24C", 
        "#FC4E2A", 
        "#B10026", 
        "#490000"
      ], 
      "6": [
        "#FFFFB2", 
        "#FFC25D", 
        "#FD8238", 
        "#E8281F", 
        "#93001C", 
        "#490000"
      ], 
      "7": [
        "#FFFFB2", 
        "#FFCC68", 
        "#FE9A41", 
        "#FC4E2A", 
        "#D21220", 
        "#7F0016", 
        "#490000"
      ], 
      "8": [
        "#FFFFB2", 
        "#FED370", 
        "#FEA847", 
        "#FD7534", 
        "#EE3522", 
        "#BF0724", 
        "#710011", 
        "#490000"
      ], 
      "9": [
        "#FFFFB2", 
        "#FED976", 
        "#FEB24C", 
        "#FD8D3C", 
        "#FC4E2A", 
        "#E31A1C", 
        "#B10026", 
        "#67000D", 
        "#490000"
      ], 
      "10": [
        "#FFFFB2", 
        "#FEDD7D", 
        "#FEBB55", 
        "#FE9A41", 
        "#FD6D32", 
        "#F13B24", 
        "#D21220", 
        "#A00020", 
        "#64000C", 
        "#490000"
      ], 
      "11": [
        "#FFFFB2", 
        "#FFE182", 
        "#FFC25D", 
        "#FEA445", 
        "#FD8238", 
        "#FC4E2A", 
        "#E8281F", 
        "#C50B23", 
        "#93001C", 
        "#61000B", 
        "#490000"
      ]
    }, 
    "name_en": "Extreme Heatwave Stress", 
    "id": "Temp_Multi_HeatwaveRisk"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "تدرج شذوذ الحرارة السطحية العالمي لمرصد غودارد", 
    "source": "NASA Goddard Institute for Space Studies (GISS)", 
    "classes": {
      "3": [
        "#73B3D8", 
        "#FFFFBF", 
        "#C51B17"
      ], 
      "4": [
        "#08306B", 
        "#C6DBEF", 
        "#FDD0A2", 
        "#67000D"
      ], 
      "5": [
        "#08306B", 
        "#C6DBEF", 
        "#FFFFBF", 
        "#FDD0A2", 
        "#67000D"
      ], 
      "6": [
        "#08306B", 
        "#5295C9", 
        "#C6DBEF", 
        "#FDD0A2", 
        "#DB4716", 
        "#67000D"
      ], 
      "7": [
        "#08306B", 
        "#5295C9", 
        "#C6DBEF", 
        "#FFFFBF", 
        "#FDD0A2", 
        "#DB4716", 
        "#67000D"
      ], 
      "8": [
        "#08306B", 
        "#2879B9", 
        "#73B3D8", 
        "#C6DBEF", 
        "#FDD0A2", 
        "#F16913", 
        "#C51B17", 
        "#67000D"
      ], 
      "9": [
        "#08306B", 
        "#2879B9", 
        "#73B3D8", 
        "#C6DBEF", 
        "#FFFFBF", 
        "#FDD0A2", 
        "#F16913", 
        "#C51B17", 
        "#67000D"
      ], 
      "10": [
        "#08306B", 
        "#2166A5", 
        "#5295C9", 
        "#89BDDE", 
        "#C6DBEF", 
        "#FDD0A2", 
        "#F7843C", 
        "#DB4716", 
        "#AC1315", 
        "#67000D"
      ], 
      "11": [
        "#08306B", 
        "#2166A5", 
        "#5295C9", 
        "#89BDDE", 
        "#C6DBEF", 
        "#FFFFBF", 
        "#FDD0A2", 
        "#F7843C", 
        "#DB4716", 
        "#AC1315", 
        "#67000D"
      ]
    }, 
    "name_en": "NASA GISTEMP Global Anomaly", 
    "id": "Temp_Div_NASA_GISTEMP"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "تدرج حرارة الهواء 2م لإعادة التحليل الأوروبي ERA5", 
    "source": "ECMWF Copernicus Climate Change Service (C3S)", 
    "classes": {
      "3": [
        "#00204D", 
        "#86B285", 
        "#E15759"
      ], 
      "4": [
        "#00204D", 
        "#358A88", 
        "#D5CE8A", 
        "#E15759"
      ], 
      "5": [
        "#00204D", 
        "#1E7084", 
        "#86B285", 
        "#F5D983", 
        "#E15759"
      ], 
      "6": [
        "#00204D", 
        "#105F7F", 
        "#559B86", 
        "#B7C487", 
        "#FECD6F", 
        "#E15759"
      ], 
      "7": [
        "#00204D", 
        "#0C547B", 
        "#358A88", 
        "#86B285", 
        "#D5CE8A", 
        "#FBB557", 
        "#E15759"
      ], 
      "8": [
        "#00204D", 
        "#074C77", 
        "#297B86", 
        "#61A286", 
        "#AAC086", 
        "#E7D486", 
        "#F7A544", 
        "#E15759"
      ], 
      "9": [
        "#00204D", 
        "#034775", 
        "#1E7084", 
        "#4A9487", 
        "#86B285", 
        "#C3C888", 
        "#F5D983", 
        "#F49837", 
        "#E15759"
      ], 
      "10": [
        "#00204D", 
        "#004273", 
        "#126782", 
        "#358A88", 
        "#67A685", 
        "#A3BE85", 
        "#D5CE8A", 
        "#FFDC80", 
        "#F28E2B", 
        "#E15759"
      ], 
      "11": [
        "#00204D", 
        "#003E6F", 
        "#105F7F", 
        "#2D7F86", 
        "#559B86", 
        "#86B285", 
        "#B7C487", 
        "#E2D287", 
        "#FECD6F", 
        "#F18932", 
        "#E15759"
      ]
    }, 
    "name_en": "ECMWF ERA5 2m Air Temp", 
    "id": "Temp_Multi_ERA5_Thermal"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "مقياس مركز التنبؤات المناخية الأمريكي CPC", 
    "source": "NOAA Climate Prediction Center", 
    "classes": {
      "3": [
        "#313695", 
        "#FFFFBF", 
        "#A50026"
      ], 
      "4": [
        "#313695", 
        "#BDE2EE", 
        "#FEBF70", 
        "#A50026"
      ], 
      "5": [
        "#313695", 
        "#90C3DD", 
        "#FFFFBF", 
        "#F98F52", 
        "#A50026"
      ], 
      "6": [
        "#313695", 
        "#74ADD1", 
        "#E0F3F8", 
        "#FEE090", 
        "#F46D43", 
        "#A50026"
      ], 
      "7": [
        "#313695", 
        "#659AC7", 
        "#BDE2EE", 
        "#FFFFBF", 
        "#FEBF70", 
        "#EB5B39", 
        "#A50026"
      ], 
      "8": [
        "#313695", 
        "#5A8DC0", 
        "#A3D3E6", 
        "#EAF6E8", 
        "#FFE99D", 
        "#FCA55D", 
        "#E44D33", 
        "#A50026"
      ], 
      "9": [
        "#313695", 
        "#5283BB", 
        "#90C3DD", 
        "#D3ECF4", 
        "#FFFFBF", 
        "#FED484", 
        "#F98F52", 
        "#DE422E", 
        "#A50026"
      ], 
      "10": [
        "#313695", 
        "#4B7BB7", 
        "#81B7D6", 
        "#BDE2EE", 
        "#EFF8DF", 
        "#FFEEA5", 
        "#FEBF70", 
        "#F77C49", 
        "#DA382A", 
        "#A50026"
      ], 
      "11": [
        "#313695", 
        "#4575B4", 
        "#74ADD1", 
        "#ABD9E9", 
        "#E0F3F8", 
        "#FFFFBF", 
        "#FEE090", 
        "#FDAE61", 
        "#F46D43", 
        "#D73027", 
        "#A50026"
      ]
    }, 
    "name_en": "NOAA CPC Climatological Scale", 
    "id": "Temp_Multi_NOAA_CPC"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "مقياس نوك العلمي للمناطق القطبية والجليد", 
    "source": "Fabio Crameri Scientific Colour Maps (Nuuk)", 
    "classes": {
      "3": [
        "#3A7EB0", 
        "#FFFFBF", 
        "#DF5842"
      ], 
      "4": [
        "#0D253A", 
        "#B5DBF2", 
        "#FAD3BD", 
        "#610012"
      ], 
      "5": [
        "#0D253A", 
        "#B5DBF2", 
        "#FFFFBF", 
        "#FAD3BD", 
        "#610012"
      ], 
      "6": [
        "#0D253A", 
        "#3A7EB0", 
        "#B5DBF2", 
        "#FAD3BD", 
        "#DF5842", 
        "#610012"
      ], 
      "7": [
        "#0D253A", 
        "#3A7EB0", 
        "#B5DBF2", 
        "#FFFFBF", 
        "#FAD3BD", 
        "#DF5842", 
        "#610012"
      ], 
      "8": [
        "#0D253A", 
        "#265E88", 
        "#639ECC", 
        "#B5DBF2", 
        "#FAD3BD", 
        "#EF8765", 
        "#BD332E", 
        "#610012"
      ], 
      "9": [
        "#0D253A", 
        "#265E88", 
        "#639ECC", 
        "#B5DBF2", 
        "#FFFFBF", 
        "#FAD3BD", 
        "#EF8765", 
        "#BD332E", 
        "#610012"
      ], 
      "10": [
        "#0D253A", 
        "#1C4E75", 
        "#3A7EB0", 
        "#76AFDA", 
        "#B5DBF2", 
        "#FAD3BD", 
        "#F59D77", 
        "#DF5842", 
        "#AC1C24", 
        "#610012"
      ], 
      "11": [
        "#0D253A", 
        "#1C4E75", 
        "#3A7EB0", 
        "#76AFDA", 
        "#B5DBF2", 
        "#FFFFBF", 
        "#FAD3BD", 
        "#F59D77", 
        "#DF5842", 
        "#AC1C24", 
        "#610012"
      ]
    }, 
    "name_en": "Crameri Nuuk Cryosphere", 
    "id": "Temp_Div_Nuuk_Cryo"
  }, 
  {
    "category": "Sequential", 
    "name_ar": "عتبات خطر الصقيع والتجمد الزراعي", 
    "source": "WMO Agricultural Meteorology Guidelines", 
    "classes": {
      "3": [
        "#E0F3F8", 
        "#347CB8", 
        "#021A3B"
      ], 
      "4": [
        "#E0F3F8", 
        "#61A3CC", 
        "#185392", 
        "#021A3B"
      ], 
      "5": [
        "#E0F3F8", 
        "#80B8D7", 
        "#347CB8", 
        "#0C3D73", 
        "#021A3B"
      ], 
      "6": [
        "#E0F3F8", 
        "#92C5DE", 
        "#4393C3", 
        "#2166AC", 
        "#053061", 
        "#021A3B"
      ], 
      "7": [
        "#E0F3F8", 
        "#A0CDE2", 
        "#61A3CC", 
        "#347CB8", 
        "#185392", 
        "#042C5A", 
        "#021A3B"
      ], 
      "8": [
        "#E0F3F8", 
        "#A9D2E5", 
        "#73AFD2", 
        "#3F8CC0", 
        "#276CAF", 
        "#114680", 
        "#042A56", 
        "#021A3B"
      ], 
      "9": [
        "#E0F3F8", 
        "#B0D6E8", 
        "#80B8D7", 
        "#4F99C6", 
        "#347CB8", 
        "#1E5FA2", 
        "#0C3D73", 
        "#042852", 
        "#021A3B"
      ], 
      "10": [
        "#E0F3F8", 
        "#B5D9EA", 
        "#8ABFDB", 
        "#61A3CC", 
        "#3D89BE", 
        "#2A70B1", 
        "#185392", 
        "#083669", 
        "#032650", 
        "#021A3B"
      ], 
      "11": [
        "#E0F3F8", 
        "#BADCEB", 
        "#92C5DE", 
        "#6EACD1", 
        "#4393C3", 
        "#347CB8", 
        "#2166AC", 
        "#134A86", 
        "#053061", 
        "#03254E", 
        "#021A3B"
      ]
    }, 
    "name_en": "WMO Frost & Freeze Hazard", 
    "id": "Temp_Seq_FrostThreshold"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "الأقاليم الحرارية المعيارية لتصنيف كوبن-جيجر", 
    "source": "Köppen-Geiger World Climate Classification", 
    "classes": {
      "3": [
        "#960000", 
        "#AEFF00", 
        "#800080"
      ], 
      "4": [
        "#960000", 
        "#FFA500", 
        "#00FFFF", 
        "#800080"
      ], 
      "5": [
        "#960000", 
        "#FF7993", 
        "#AEFF00", 
        "#2A9EFF", 
        "#800080"
      ], 
      "6": [
        "#960000", 
        "#FF5B93", 
        "#FFDC00", 
        "#43FF87", 
        "#196DFF", 
        "#800080"
      ], 
      "7": [
        "#960000", 
        "#FF4562", 
        "#FFA500", 
        "#AEFF00", 
        "#00FFFF", 
        "#2051FF", 
        "#800080"
      ], 
      "8": [
        "#960000", 
        "#FF323F", 
        "#FF8D66", 
        "#FFF200", 
        "#2DFF49", 
        "#33C7FF", 
        "#1C39FF", 
        "#800080"
      ], 
      "9": [
        "#960000", 
        "#FF1E22", 
        "#FF7993", 
        "#FFC700", 
        "#AEFF00", 
        "#45FFB5", 
        "#2A9EFF", 
        "#1223FF", 
        "#800080"
      ], 
      "10": [
        "#960000", 
        "#FF0000", 
        "#FF69B4", 
        "#FFA500", 
        "#FFFF00", 
        "#00FF00", 
        "#00FFFF", 
        "#007FFF", 
        "#0000FF", 
        "#800080"
      ], 
      "11": [
        "#960000", 
        "#F40000", 
        "#FF5B93", 
        "#FF9452", 
        "#FFDC00", 
        "#AEFF00", 
        "#43FF87", 
        "#2FD8FF", 
        "#196DFF", 
        "#3600F2", 
        "#800080"
      ]
    }, 
    "name_en": "Köppen-Geiger Thermal Regimes", 
    "id": "Temp_Multi_KoppenThermal"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "شذوذ الاحترار التاريخي لمركز هادلي البريطاني", 
    "source": "UK Met Office / Climatic Research Unit (CRU)", 
    "classes": {
      "3": [
        "#6BAED6", 
        "#FFFFBF", 
        "#DE2D26"
      ], 
      "4": [
        "#08519C", 
        "#BDD7E7", 
        "#FCAE91", 
        "#A50F15"
      ], 
      "5": [
        "#08519C", 
        "#BDD7E7", 
        "#FFFFBF", 
        "#FCAE91", 
        "#A50F15"
      ], 
      "6": [
        "#08519C", 
        "#5198C9", 
        "#BDD7E7", 
        "#FCAE91", 
        "#ED4E38", 
        "#A50F15"
      ], 
      "7": [
        "#08519C", 
        "#5198C9", 
        "#BDD7E7", 
        "#FFFFBF", 
        "#FCAE91", 
        "#ED4E38", 
        "#A50F15"
      ], 
      "8": [
        "#08519C", 
        "#3182BD", 
        "#6BAED6", 
        "#BDD7E7", 
        "#FCAE91", 
        "#FB6A4A", 
        "#DE2D26", 
        "#A50F15"
      ], 
      "9": [
        "#08519C", 
        "#3182BD", 
        "#6BAED6", 
        "#BDD7E7", 
        "#FFFFBF", 
        "#FCAE91", 
        "#FB6A4A", 
        "#DE2D26", 
        "#A50F15"
      ], 
      "10": [
        "#08519C", 
        "#2A75B5", 
        "#5198C9", 
        "#82B8DA", 
        "#BDD7E7", 
        "#FCAE91", 
        "#FD7C5B", 
        "#ED4E38", 
        "#CF2622", 
        "#A50F15"
      ], 
      "11": [
        "#08519C", 
        "#2A75B5", 
        "#5198C9", 
        "#82B8DA", 
        "#BDD7E7", 
        "#FFFFBF", 
        "#FCAE91", 
        "#FD7C5B", 
        "#ED4E38", 
        "#CF2622", 
        "#A50F15"
      ]
    }, 
    "name_en": "HadCRUT5 Historical Warming", 
    "id": "Temp_Div_HadCRUT5"
  }, 
  {
    "category": "Multi-Hue", 
    "name_ar": "درجة الحرارة المحسوسة الفعلية لستيدمان", 
    "source": "Steadman Biometeorological Formula", 
    "classes": {
      "3": [
        "#2B83BA", 
        "#FFD78F", 
        "#7F0000"
      ], 
      "4": [
        "#2B83BA", 
        "#E3F4B6", 
        "#F38649", 
        "#7F0000"
      ], 
      "5": [
        "#2B83BA", 
        "#C0E6AB", 
        "#FFD78F", 
        "#E24D2C", 
        "#7F0000"
      ], 
      "6": [
        "#2B83BA", 
        "#ABDDA4", 
        "#FFFFBF", 
        "#FDAE61", 
        "#D7191C", 
        "#7F0000"
      ], 
      "7": [
        "#2B83BA", 
        "#9CCDA9", 
        "#E3F4B6", 
        "#FFD78F", 
        "#F38649", 
        "#C81518", 
        "#7F0000"
      ], 
      "8": [
        "#2B83BA", 
        "#90C2AC", 
        "#D0ECAF", 
        "#FFF3B1", 
        "#FFBA6E", 
        "#EA6738", 
        "#BD1114", 
        "#7F0000"
      ], 
      "9": [
        "#2B83BA", 
        "#87BAAE", 
        "#C0E6AB", 
        "#F5FBBC", 
        "#FFD78F", 
        "#F99F58", 
        "#E24D2C", 
        "#B50F12", 
        "#7F0000"
      ], 
      "10": [
        "#2B83BA", 
        "#7FB4AF", 
        "#B5E1A7", 
        "#E3F4B6", 
        "#FFEDAA", 
        "#FFC076", 
        "#F38649", 
        "#DC3523", 
        "#AF0D10", 
        "#7F0000"
      ], 
      "11": [
        "#2B83BA", 
        "#79AFB1", 
        "#ABDDA4", 
        "#D5EEB1", 
        "#FFFFBF", 
        "#FFD78F", 
        "#FDAE61", 
        "#ED703D", 
        "#D7191C", 
        "#AA0B0F", 
        "#7F0000"
      ]
    }, 
    "name_en": "Steadman Apparent Temperature", 
    "id": "Temp_Multi_SteadmanApparent"
  }, 
  {
    "category": "Diverging", 
    "name_ar": "المدى الحراري السنوي للمناطق القارية", 
    "source": "Climatological Continental Range Index", 
    "classes": {
      "3": [
        "#78A3C8", 
        "#FFFFBF", 
        "#FC8D59"
      ], 
      "4": [
        "#1B385C", 
        "#B8D4E8", 
        "#FDD49E", 
        "#B30000"
      ], 
      "5": [
        "#1B385C", 
        "#B8D4E8", 
        "#FFFFBF", 
        "#FDD49E", 
        "#B30000"
      ], 
      "6": [
        "#1B385C", 
        "#5A85B0", 
        "#B8D4E8", 
        "#FDD49E", 
        "#FC8D59", 
        "#B30000"
      ], 
      "7": [
        "#1B385C", 
        "#5A85B0", 
        "#B8D4E8", 
        "#FFFFBF", 
        "#FDD49E", 
        "#FC8D59", 
        "#B30000"
      ], 
      "8": [
        "#1B385C", 
        "#3B6998", 
        "#78A3C8", 
        "#B8D4E8", 
        "#FDD49E", 
        "#FDAC75", 
        "#EC623F", 
        "#B30000"
      ], 
      "9": [
        "#1B385C", 
        "#3B6998", 
        "#78A3C8", 
        "#B8D4E8", 
        "#FFFFBF", 
        "#FDD49E", 
        "#FDAC75", 
        "#EC623F", 
        "#B30000"
      ], 
      "10": [
        "#1B385C", 
        "#335C89", 
        "#5A85B0", 
        "#88AFD0", 
        "#B8D4E8", 
        "#FDD49E", 
        "#FDBB84", 
        "#FC8D59", 
        "#E34A33", 
        "#B30000"
      ], 
      "11": [
        "#1B385C", 
        "#335C89", 
        "#5A85B0", 
        "#88AFD0", 
        "#B8D4E8", 
        "#FFFFBF", 
        "#FDD49E", 
        "#FDBB84", 
        "#FC8D59", 
        "#E34A33", 
        "#B30000"
      ]
    }, 
    "name_en": "Continental Annual Range", 
    "id": "Temp_Div_ContinentalThermal"
  }, 
  {
    "category": "Sequential", 
    "name_ar": "مؤشر الليالي الاستوائية وتراكم الحرارة الليلية", 
    "source": "WMO Expert Team on Climate Change Indices (ETCCDI)", 
    "classes": {
      "3": [
        "#FFF7BC", 
        "#F5851F", 
        "#662506"
      ], 
      "4": [
        "#FFF7BC", 
        "#FFB643", 
        "#D75807", 
        "#662506"
      ], 
      "5": [
        "#FFF7BC", 
        "#FFCC60", 
        "#F5851F", 
        "#BF4603", 
        "#662506"
      ], 
      "6": [
        "#FFF7BC", 
        "#FFD777", 
        "#FEA231", 
        "#E66910", 
        "#AD3D04", 
        "#662506"
      ], 
      "7": [
        "#FFF7BC", 
        "#FFDE86", 
        "#FFB643", 
        "#F5851F", 
        "#D75807", 
        "#A13804", 
        "#662506"
      ], 
      "8": [
        "#FFF7BC", 
        "#FEE391", 
        "#FEC44F", 
        "#FE9929", 
        "#EC7014", 
        "#CC4C02", 
        "#993404", 
        "#662506"
      ], 
      "9": [
        "#FFF7BC", 
        "#FEE596", 
        "#FFCC60", 
        "#FFA938", 
        "#F5851F", 
        "#E0630D", 
        "#BF4603", 
        "#923205", 
        "#662506"
      ], 
      "10": [
        "#FFF7BC", 
        "#FEE79B", 
        "#FFD26D", 
        "#FFB643", 
        "#FC9527", 
        "#EE7516", 
        "#D75807", 
        "#B54103", 
        "#8D3105", 
        "#662506"
      ], 
      "11": [
        "#FFF7BC", 
        "#FFE99E", 
        "#FFD777", 
        "#FEC04B", 
        "#FEA231", 
        "#F5851F", 
        "#E66910", 
        "#CF5003", 
        "#AD3D04", 
        "#892F05", 
        "#662506"
      ]
    }, 
    "name_en": "Tropical Nights Accumulation", 
    "id": "Temp_Seq_TropicalNights"
  }
]

OTHER_ELEMENTS = [
  {
    "name_ar": "الأمطار والتساقط", 
    "styles": [
      {
        "category": "Sequential", 
        "name_ar": "تدرج الهطول المطري التراكمي القياسي", 
        "source": "ColorBrewer Blues", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#4292C6", 
            "#08306B"
          ], 
          "4": [
            "#BDD7E7", 
            "#6BAED6", 
            "#2171B5", 
            "#08306B"
          ], 
          "5": [
            "#BDD7E7", 
            "#86BCDC", 
            "#4292C6", 
            "#1761A8", 
            "#08306B"
          ], 
          "6": [
            "#BDD7E7", 
            "#94C4DF", 
            "#5CA3D0", 
            "#307EBC", 
            "#0F57A1", 
            "#08306B"
          ], 
          "7": [
            "#BDD7E7", 
            "#9ECAE1", 
            "#6BAED6", 
            "#4292C6", 
            "#2171B5", 
            "#08519C", 
            "#08306B"
          ], 
          "8": [
            "#BDD7E7", 
            "#A3CCE2", 
            "#7BB6D9", 
            "#559ECD", 
            "#3684BF", 
            "#1C68AE", 
            "#084C95", 
            "#08306B"
          ], 
          "9": [
            "#BDD7E7", 
            "#A6CDE3", 
            "#86BCDC", 
            "#62A7D2", 
            "#4292C6", 
            "#2B79B9", 
            "#1761A8", 
            "#09498F", 
            "#08306B"
          ], 
          "10": [
            "#BDD7E7", 
            "#A9CEE3", 
            "#8EC1DD", 
            "#6BAED6", 
            "#519BCB", 
            "#3987C0", 
            "#2171B5", 
            "#135BA4", 
            "#09468B", 
            "#08306B"
          ], 
          "11": [
            "#BDD7E7", 
            "#ABCFE3", 
            "#94C4DF", 
            "#76B4D8", 
            "#5CA3D0", 
            "#4292C6", 
            "#307EBC", 
            "#1D6AB0", 
            "#0F57A1", 
            "#094388", 
            "#08306B"
          ]
        }, 
        "name_en": "Cumulative Rainfall Blues", 
        "id": "Precip_Seq_Blues"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "تدرج الهطول المناخي السنوي والفصلي", 
        "source": "NOAA ROC / ColorBrewer YlGnBu", 
        "classes": {
          "3": [
            "#FFFFCC", 
            "#41B6C4", 
            "#081D58"
          ], 
          "4": [
            "#FFFFCC", 
            "#99D6B9", 
            "#2280B8", 
            "#081D58"
          ], 
          "5": [
            "#FFFFCC", 
            "#C7E9B4", 
            "#41B6C4", 
            "#225EA8", 
            "#081D58"
          ], 
          "6": [
            "#FFFFCC", 
            "#D6EFB3", 
            "#75C8BD", 
            "#2798C1", 
            "#264DA0", 
            "#081D58"
          ], 
          "7": [
            "#FFFFCC", 
            "#E1F3B2", 
            "#99D6B9", 
            "#41B6C4", 
            "#2280B8", 
            "#26429B", 
            "#081D58"
          ], 
          "8": [
            "#FFFFCC", 
            "#E8F6B1", 
            "#B4E1B6", 
            "#69C3BF", 
            "#30A1C2", 
            "#236CAF", 
            "#263A97", 
            "#081D58"
          ], 
          "9": [
            "#FFFFCC", 
            "#EDF8B1", 
            "#C7E9B4", 
            "#7FCDBB", 
            "#41B6C4", 
            "#1D91C0", 
            "#225EA8", 
            "#253494", 
            "#081D58"
          ], 
          "10": [
            "#FFFFCC", 
            "#EFF9B4", 
            "#D0ECB3", 
            "#99D6B9", 
            "#61C0C0", 
            "#34A5C2", 
            "#2280B8", 
            "#2455A4", 
            "#22318D", 
            "#081D58"
          ], 
          "11": [
            "#FFFFCC", 
            "#F1F9B6", 
            "#D6EFB3", 
            "#ACDEB7", 
            "#75C8BD", 
            "#41B6C4", 
            "#2798C1", 
            "#2372B2", 
            "#264DA0", 
            "#1F2F88", 
            "#081D58"
          ]
        }, 
        "name_en": "Climatological Precipitation", 
        "id": "Precip_Seq_YlGnBu"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "تدرج أمطار الرياح الموسمية والهطول الغزير", 
        "source": "ColorBrewer BuPu", 
        "classes": {
          "3": [
            "#BFD3E6", 
            "#8C6BB1", 
            "#4D004B"
          ], 
          "4": [
            "#BFD3E6", 
            "#8C96C6", 
            "#88419D", 
            "#4D004B"
          ], 
          "5": [
            "#BFD3E6", 
            "#95A9D0", 
            "#8C6BB1", 
            "#852C8C", 
            "#4D004B"
          ], 
          "6": [
            "#BFD3E6", 
            "#9AB4D6", 
            "#8D85BE", 
            "#8A53A5", 
            "#831D82", 
            "#4D004B"
          ], 
          "7": [
            "#BFD3E6", 
            "#9EBCDA", 
            "#8C96C6", 
            "#8C6BB1", 
            "#88419D", 
            "#810F7C", 
            "#4D004B"
          ], 
          "8": [
            "#BFD3E6", 
            "#A3BFDC", 
            "#91A1CC", 
            "#8D7EBA", 
            "#8B5AA8", 
            "#863693", 
            "#790C75", 
            "#4D004B"
          ], 
          "9": [
            "#BFD3E6", 
            "#A6C2DD", 
            "#95A9D0", 
            "#8D8BC1", 
            "#8C6BB1", 
            "#894CA2", 
            "#852C8C", 
            "#740A6F", 
            "#4D004B"
          ], 
          "10": [
            "#BFD3E6", 
            "#A9C4DE", 
            "#98AFD3", 
            "#8C96C6", 
            "#8D7AB8", 
            "#8B5EAA", 
            "#88419D", 
            "#842487", 
            "#6F086B", 
            "#4D004B"
          ], 
          "11": [
            "#BFD3E6", 
            "#ABC5DF", 
            "#9AB4D6", 
            "#909ECA", 
            "#8D85BE", 
            "#8C6BB1", 
            "#8A53A5", 
            "#873996", 
            "#831D82", 
            "#6C0768", 
            "#4D004B"
          ]
        }, 
        "name_en": "Monsoon & Heavy Downpours", 
        "id": "Precip_Seq_BuPu"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "شذوذ وفائض وعجز الأمطار عن المعدل الطبيعي", 
        "source": "ColorBrewer BrBG", 
        "classes": {
          "3": [
            "#BF812D", 
            "#F6E8C3", 
            "#01665E"
          ], 
          "4": [
            "#543005", 
            "#DFC27D", 
            "#80CDC1", 
            "#003C30"
          ], 
          "5": [
            "#543005", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#003C30"
          ], 
          "6": [
            "#543005", 
            "#A5691C", 
            "#DFC27D", 
            "#80CDC1", 
            "#1F7E76", 
            "#003C30"
          ], 
          "7": [
            "#543005", 
            "#A5691C", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#1F7E76", 
            "#003C30"
          ], 
          "8": [
            "#543005", 
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#80CDC1", 
            "#35978F", 
            "#01665E", 
            "#003C30"
          ], 
          "9": [
            "#543005", 
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#35978F", 
            "#01665E", 
            "#003C30"
          ], 
          "10": [
            "#543005", 
            "#7E4809", 
            "#A5691C", 
            "#C89142", 
            "#DFC27D", 
            "#80CDC1", 
            "#4AA49B", 
            "#1F7E76", 
            "#015B52", 
            "#003C30"
          ], 
          "11": [
            "#543005", 
            "#7E4809", 
            "#A5691C", 
            "#C89142", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#4AA49B", 
            "#1F7E76", 
            "#015B52", 
            "#003C30"
          ]
        }, 
        "name_en": "Precipitation Departure Anomaly", 
        "id": "Precip_Div_BrBG"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر الهطول القياسي (SPI) للجفاف والرطوبة", 
        "source": "WMO Commission for Agricultural Meteorology (SPI)", 
        "classes": {
          "3": [
            "#FFAA00", 
            "#F6E8C3", 
            "#0070FF"
          ], 
          "4": [
            "#730000", 
            "#FFFF00", 
            "#A6F28F", 
            "#002673"
          ], 
          "5": [
            "#730000", 
            "#FFFF00", 
            "#F6E8C3", 
            "#A6F28F", 
            "#002673"
          ], 
          "6": [
            "#730000", 
            "#F56E00", 
            "#FFFF00", 
            "#A6F28F", 
            "#5F8D92", 
            "#002673"
          ], 
          "7": [
            "#730000", 
            "#F56E00", 
            "#FFFF00", 
            "#F6E8C3", 
            "#A6F28F", 
            "#5F8D92", 
            "#002673"
          ], 
          "8": [
            "#730000", 
            "#E60000", 
            "#FFAA00", 
            "#FFFF00", 
            "#A6F28F", 
            "#38A800", 
            "#0070FF", 
            "#002673"
          ], 
          "9": [
            "#730000", 
            "#E60000", 
            "#FFAA00", 
            "#FFFF00", 
            "#F6E8C3", 
            "#A6F28F", 
            "#38A800", 
            "#0070FF", 
            "#002673"
          ], 
          "10": [
            "#730000", 
            "#C80002", 
            "#F56E00", 
            "#FFC000", 
            "#FFFF00", 
            "#A6F28F", 
            "#58BA33", 
            "#5F8D92", 
            "#015CDA", 
            "#002673"
          ], 
          "11": [
            "#730000", 
            "#C80002", 
            "#F56E00", 
            "#FFC000", 
            "#FFFF00", 
            "#F6E8C3", 
            "#A6F28F", 
            "#58BA33", 
            "#5F8D92", 
            "#015CDA", 
            "#002673"
          ]
        }, 
        "name_en": "Standardized Precipitation Index", 
        "id": "Precip_Div_SPI"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس انعكاسية رادار الطقس الوطني للسيول", 
        "source": "NOAA NWS Radar Operations Center (ROC)", 
        "classes": {
          "3": [
            "#04E9E7", 
            "#E5BC00", 
            "#4A0072"
          ], 
          "4": [
            "#04E9E7", 
            "#00A000", 
            "#EF0000", 
            "#4A0072"
          ], 
          "5": [
            "#04E9E7", 
            "#01E101", 
            "#E5BC00", 
            "#C80000", 
            "#4A0072"
          ], 
          "6": [
            "#04E9E7", 
            "#65D263", 
            "#A9CE00", 
            "#FF6F00", 
            "#CE0038", 
            "#4A0072"
          ], 
          "7": [
            "#04E9E7", 
            "#726CBD", 
            "#00A000", 
            "#E5BC00", 
            "#EF0000", 
            "#EE00A7", 
            "#4A0072"
          ], 
          "8": [
            "#04E9E7", 
            "#0300F4", 
            "#01C501", 
            "#FDF802", 
            "#FD9500", 
            "#D40000", 
            "#F800FD", 
            "#4A0072"
          ], 
          "9": [
            "#04E9E7", 
            "#283FF4", 
            "#01E101", 
            "#5CA900", 
            "#E5BC00", 
            "#FE4500", 
            "#C80000", 
            "#E031EF", 
            "#4A0072"
          ], 
          "10": [
            "#04E9E7", 
            "#2F5AF5", 
            "#02F702", 
            "#00A000", 
            "#F8EB01", 
            "#F89E00", 
            "#EF0000", 
            "#BF0000", 
            "#CE3FE4", 
            "#4A0072"
          ], 
          "11": [
            "#04E9E7", 
            "#306EF5", 
            "#65D263", 
            "#01BA01", 
            "#A9CE00", 
            "#E5BC00", 
            "#FF6F00", 
            "#DC0000", 
            "#CE0038", 
            "#BF47DC", 
            "#4A0072"
          ]
        }, 
        "name_en": "Doppler Radar Reflectivity dBZ", 
        "id": "Precip_Multi_DopplerRadar"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس مخاطر السيول الجارفة والفيضانات المفاجئة", 
        "source": "NOAA National Water Center (NWC)", 
        "classes": {
          "3": [
            "#B2E2E2", 
            "#90A330", 
            "#7F0000"
          ], 
          "4": [
            "#B2E2E2", 
            "#20904E", 
            "#F4A59B", 
            "#7F0000"
          ], 
          "5": [
            "#B2E2E2", 
            "#3DAA70", 
            "#90A330", 
            "#EC7498", 
            "#7F0000"
          ], 
          "6": [
            "#B2E2E2", 
            "#52B588", 
            "#0B7736", 
            "#FDC959", 
            "#EC525E", 
            "#7F0000"
          ], 
          "7": [
            "#B2E2E2", 
            "#5EBD98", 
            "#20904E", 
            "#90A330", 
            "#F4A59B", 
            "#E83739", 
            "#7F0000"
          ], 
          "8": [
            "#B2E2E2", 
            "#66C2A4", 
            "#2CA25F", 
            "#006D2C", 
            "#FFD92F", 
            "#E78AC3", 
            "#E41A1C", 
            "#7F0000"
          ], 
          "9": [
            "#B2E2E2", 
            "#70C6AC", 
            "#3DAA70", 
            "#14803F", 
            "#90A330", 
            "#FBBC74", 
            "#EC7498", 
            "#D71619", 
            "#7F0000"
          ], 
          "10": [
            "#B2E2E2", 
            "#78C9B2", 
            "#49B07D", 
            "#20904E", 
            "#34792D", 
            "#E6CD30", 
            "#F4A59B", 
            "#ED6278", 
            "#CD1416", 
            "#7F0000"
          ], 
          "11": [
            "#B2E2E2", 
            "#7ECCB6", 
            "#52B588", 
            "#289D5A", 
            "#0B7736", 
            "#90A330", 
            "#FDC959", 
            "#EB92B7", 
            "#EC525E", 
            "#C51114", 
            "#7F0000"
          ]
        }, 
        "name_en": "Flash Flood Guidance Risk", 
        "id": "Precip_Multi_FlashFlood"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "تدرج تراكم الثلوج والكتل الجليدية", 
        "source": "National Snow and Ice Data Center (NSIDC)", 
        "classes": {
          "3": [
            "#C6E8F8", 
            "#43A2CA", 
            "#1F1A3A"
          ], 
          "4": [
            "#C6E8F8", 
            "#7BCCC4", 
            "#0868AC", 
            "#1F1A3A"
          ], 
          "5": [
            "#C6E8F8", 
            "#9CD8C0", 
            "#43A2CA", 
            "#0A5496", 
            "#1F1A3A"
          ], 
          "6": [
            "#C6E8F8", 
            "#AFDFBE", 
            "#68BBC7", 
            "#287FB8", 
            "#094889", 
            "#1F1A3A"
          ], 
          "7": [
            "#C6E8F8", 
            "#BAE4BC", 
            "#7BCCC4", 
            "#43A2CA", 
            "#0868AC", 
            "#084081", 
            "#1F1A3A"
          ], 
          "8": [
            "#C6E8F8", 
            "#BCE5C5", 
            "#8FD3C2", 
            "#5FB4C8", 
            "#3189BD", 
            "#095CA0", 
            "#133A76", 
            "#1F1A3A"
          ], 
          "9": [
            "#C6E8F8", 
            "#BEE5CB", 
            "#9CD8C0", 
            "#6FC1C6", 
            "#43A2CA", 
            "#1F76B4", 
            "#0A5496", 
            "#17366E", 
            "#1F1A3A"
          ], 
          "10": [
            "#C6E8F8", 
            "#BFE5D0", 
            "#A7DCBF", 
            "#7BCCC4", 
            "#59B0C8", 
            "#358EC0", 
            "#0868AC", 
            "#094D8F", 
            "#1A3368", 
            "#1F1A3A"
          ], 
          "11": [
            "#C6E8F8", 
            "#C0E6D4", 
            "#AFDFBE", 
            "#89D1C2", 
            "#68BBC7", 
            "#43A2CA", 
            "#287FB8", 
            "#0960A3", 
            "#094889", 
            "#1B3063", 
            "#1F1A3A"
          ]
        }, 
        "name_en": "Cryospheric Snow & Glacial", 
        "id": "Precip_Multi_SnowIce"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "تدرج قياس الهطول العالمي عبر أقمار ناسا GPM", 
        "source": "NASA Global Precipitation Measurement (GPM)", 
        "classes": {
          "3": [
            "#A8E6F5", 
            "#03045E", 
            "#3A0CA3"
          ], 
          "4": [
            "#A8E6F5", 
            "#0077B6", 
            "#F72585", 
            "#3A0CA3"
          ], 
          "5": [
            "#A8E6F5", 
            "#0795C7", 
            "#03045E", 
            "#BC109E", 
            "#3A0CA3"
          ], 
          "6": [
            "#A8E6F5", 
            "#05A7D1", 
            "#164992", 
            "#A00E76", 
            "#9308AD", 
            "#3A0CA3"
          ], 
          "7": [
            "#A8E6F5", 
            "#00B4D8", 
            "#0077B6", 
            "#03045E", 
            "#F72585", 
            "#7209B7", 
            "#3A0CA3"
          ], 
          "8": [
            "#A8E6F5", 
            "#38BBDC", 
            "#0688C0", 
            "#153683", 
            "#7B076F", 
            "#D61894", 
            "#6B09B4", 
            "#3A0CA3"
          ], 
          "9": [
            "#A8E6F5", 
            "#4DC0DF", 
            "#0795C7", 
            "#145A9F", 
            "#03045E", 
            "#C0177C", 
            "#BC109E", 
            "#650AB2", 
            "#3A0CA3"
          ], 
          "10": [
            "#A8E6F5", 
            "#5AC4E2", 
            "#079FCD", 
            "#0077B6", 
            "#132C7A", 
            "#67046C", 
            "#F72585", 
            "#A60BA7", 
            "#610AB0", 
            "#3A0CA3"
          ], 
          "11": [
            "#A8E6F5", 
            "#63C8E4", 
            "#05A7D1", 
            "#0483BD", 
            "#164992", 
            "#03045E", 
            "#A00E76", 
            "#E01C8F", 
            "#9308AD", 
            "#5D0AAF", 
            "#3A0CA3"
          ]
        }, 
        "name_en": "NASA GPM IMERG Precipitation", 
        "id": "Precip_Multi_NASA_GPM"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "تدرج مراقبة الأمطار عالي الدقة CHIRPS", 
        "source": "Climate Hazards Center / UCSB", 
        "classes": {
          "3": [
            "#A2D9CE", 
            "#16A085", 
            "#0B4C3F"
          ], 
          "4": [
            "#A2D9CE", 
            "#45B39D", 
            "#117864", 
            "#0B4C3F"
          ], 
          "5": [
            "#A2D9CE", 
            "#5DBDA9", 
            "#16A085", 
            "#106D5A", 
            "#0B4C3F"
          ], 
          "6": [
            "#A2D9CE", 
            "#6BC2B1", 
            "#36AB93", 
            "#138871", 
            "#0F6655", 
            "#0B4C3F"
          ], 
          "7": [
            "#A2D9CE", 
            "#73C6B6", 
            "#45B39D", 
            "#16A085", 
            "#117864", 
            "#0E6251", 
            "#0B4C3F"
          ], 
          "8": [
            "#A2D9CE", 
            "#7AC9B9", 
            "#53B8A4", 
            "#2EA88F", 
            "#148F77", 
            "#10725F", 
            "#0E5F4E", 
            "#0B4C3F"
          ], 
          "9": [
            "#A2D9CE", 
            "#7FCBBC", 
            "#5DBDA9", 
            "#3CAE97", 
            "#16A085", 
            "#12826C", 
            "#106D5A", 
            "#0D5C4C", 
            "#0B4C3F"
          ], 
          "10": [
            "#A2D9CE", 
            "#83CCBE", 
            "#65C0AE", 
            "#45B39D", 
            "#2AA68D", 
            "#14927A", 
            "#117864", 
            "#0F6957", 
            "#0D5B4B", 
            "#0B4C3F"
          ], 
          "11": [
            "#A2D9CE", 
            "#86CEC0", 
            "#6BC2B1", 
            "#4FB7A2", 
            "#36AB93", 
            "#16A085", 
            "#138871", 
            "#107460", 
            "#0F6655", 
            "#0D594A", 
            "#0B4C3F"
          ]
        }, 
        "name_en": "CHIRPS High-Resolution Rainfall", 
        "id": "Precip_Seq_CHIRPS_Rain"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "تدرج إجمالي الهطول المطري لنموذج ERA5 العالمي", 
        "source": "ECMWF Copernicus Climate Change Service", 
        "classes": {
          "3": [
            "#B5D9F0", 
            "#2166AC", 
            "#49006A"
          ], 
          "4": [
            "#B5D9F0", 
            "#4393C3", 
            "#053061", 
            "#49006A"
          ], 
          "5": [
            "#B5D9F0", 
            "#6EACD1", 
            "#2166AC", 
            "#231C56", 
            "#49006A"
          ], 
          "6": [
            "#B5D9F0", 
            "#84BBD9", 
            "#3781BA", 
            "#10457E", 
            "#2A0D4F", 
            "#49006A"
          ], 
          "7": [
            "#B5D9F0", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061", 
            "#2D004B", 
            "#49006A"
          ], 
          "8": [
            "#B5D9F0", 
            "#97C8E1", 
            "#5DA1CB", 
            "#3279B6", 
            "#154E8B", 
            "#1B255B", 
            "#31004F", 
            "#49006A"
          ], 
          "9": [
            "#B5D9F0", 
            "#9BCAE2", 
            "#6EACD1", 
            "#3C88BD", 
            "#2166AC", 
            "#0C3D73", 
            "#231C56", 
            "#340053", 
            "#49006A"
          ], 
          "10": [
            "#B5D9F0", 
            "#9ECCE4", 
            "#7AB4D5", 
            "#4393C3", 
            "#2E75B4", 
            "#185392", 
            "#053061", 
            "#271552", 
            "#360055", 
            "#49006A"
          ], 
          "11": [
            "#B5D9F0", 
            "#A0CDE5", 
            "#84BBD9", 
            "#569DC8", 
            "#3781BA", 
            "#2166AC", 
            "#10457E", 
            "#17295D", 
            "#2A0D4F", 
            "#380057", 
            "#49006A"
          ]
        }, 
        "name_en": "ECMWF ERA5 Total Precipitation", 
        "id": "Precip_Multi_ERA5_Total"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "مقياس شدة الأمطار الساعية للمنظمة العالمية للأرصاد", 
        "source": "WMO-No. 8 Guide to Meteorological Instruments", 
        "classes": {
          "3": [
            "#E0F7FA", 
            "#17B9CD", 
            "#006064"
          ], 
          "4": [
            "#E0F7FA", 
            "#4ECEDF", 
            "#009EB0", 
            "#006064"
          ], 
          "5": [
            "#E0F7FA", 
            "#6FD8E6", 
            "#17B9CD", 
            "#008D9B", 
            "#006064"
          ], 
          "6": [
            "#E0F7FA", 
            "#80DEEA", 
            "#26C6DA", 
            "#00ACC1", 
            "#00838F", 
            "#006064"
          ], 
          "7": [
            "#E0F7FA", 
            "#92E2ED", 
            "#4ECEDF", 
            "#17B9CD", 
            "#009EB0", 
            "#007D88", 
            "#006064"
          ], 
          "8": [
            "#E0F7FA", 
            "#9FE5EF", 
            "#62D4E3", 
            "#22C2D6", 
            "#08B0C5", 
            "#0094A4", 
            "#007982", 
            "#006064"
          ], 
          "9": [
            "#E0F7FA", 
            "#A7E8F0", 
            "#6FD8E6", 
            "#38C9DC", 
            "#17B9CD", 
            "#00A7BB", 
            "#008D9B", 
            "#00767F", 
            "#006064"
          ], 
          "10": [
            "#E0F7FA", 
            "#AEE9F1", 
            "#79DBE8", 
            "#4ECEDF", 
            "#20C0D4", 
            "#0CB2C7", 
            "#009EB0", 
            "#008794", 
            "#00737C", 
            "#006064"
          ], 
          "11": [
            "#E0F7FA", 
            "#B3EBF2", 
            "#80DEEA", 
            "#5CD2E2", 
            "#26C6DA", 
            "#17B9CD", 
            "#00ACC1", 
            "#0097A8", 
            "#00838F", 
            "#007179", 
            "#006064"
          ]
        }, 
        "name_en": "WMO Hourly Rainfall Intensity", 
        "id": "Precip_Seq_Intensity_WMO"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر الجفاف والفيضان متعدد المقاييس الزمنية SPEI", 
        "source": "Vicente-Serrano et al. (SPEI Global)", 
        "classes": {
          "3": [
            "#BF812D", 
            "#F6E8C3", 
            "#35978F"
          ], 
          "4": [
            "#8C510A", 
            "#DFC27D", 
            "#80CDC1", 
            "#01665E"
          ], 
          "5": [
            "#8C510A", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#01665E"
          ], 
          "6": [
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#80CDC1", 
            "#35978F", 
            "#01665E"
          ], 
          "7": [
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#35978F", 
            "#01665E"
          ], 
          "8": [
            "#8C510A", 
            "#AE7122", 
            "#CB9648", 
            "#DFC27D", 
            "#80CDC1", 
            "#50A99F", 
            "#27867E", 
            "#01665E"
          ], 
          "9": [
            "#8C510A", 
            "#AE7122", 
            "#CB9648", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#50A99F", 
            "#27867E", 
            "#01665E"
          ], 
          "10": [
            "#8C510A", 
            "#A5691C", 
            "#BF812D", 
            "#D0A155", 
            "#DFC27D", 
            "#80CDC1", 
            "#5CB2A8", 
            "#35978F", 
            "#1F7E76", 
            "#01665E"
          ], 
          "11": [
            "#8C510A", 
            "#A5691C", 
            "#BF812D", 
            "#D0A155", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#5CB2A8", 
            "#35978F", 
            "#1F7E76", 
            "#01665E"
          ]
        }, 
        "name_en": "Multi-scalar SPEI Drought/Wet", 
        "id": "Precip_Div_SPEI_Multi"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "المكافئ المائي للغطاء الثلجي والهيدرولوجيا", 
        "source": "USDA NRCS SNOTEL / NASA SnowEx", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#58A0CE", 
            "#084594"
          ], 
          "4": [
            "#BDD7E7", 
            "#7DB7DA", 
            "#3987C0", 
            "#084594"
          ], 
          "5": [
            "#BDD7E7", 
            "#92C3DE", 
            "#58A0CE", 
            "#2B79B9", 
            "#084594"
          ], 
          "6": [
            "#BDD7E7", 
            "#9ECAE1", 
            "#6BAED6", 
            "#4292C6", 
            "#2171B5", 
            "#084594"
          ], 
          "7": [
            "#BDD7E7", 
            "#A3CCE2", 
            "#7DB7DA", 
            "#58A0CE", 
            "#3987C0", 
            "#1E69AF", 
            "#084594"
          ], 
          "8": [
            "#BDD7E7", 
            "#A7CEE3", 
            "#89BEDC", 
            "#66AAD4", 
            "#4996C8", 
            "#317FBC", 
            "#1C64AB", 
            "#084594"
          ], 
          "9": [
            "#BDD7E7", 
            "#AACFE3", 
            "#92C3DE", 
            "#72B1D7", 
            "#58A0CE", 
            "#3F8EC4", 
            "#2B79B9", 
            "#1A60A9", 
            "#084594"
          ], 
          "10": [
            "#BDD7E7", 
            "#ACD0E4", 
            "#99C7E0", 
            "#7DB7DA", 
            "#63A8D2", 
            "#4C98CA", 
            "#3987C0", 
            "#2675B7", 
            "#195DA6", 
            "#084594"
          ], 
          "11": [
            "#BDD7E7", 
            "#AED0E4", 
            "#9ECAE1", 
            "#86BCDC", 
            "#6BAED6", 
            "#58A0CE", 
            "#4292C6", 
            "#3381BE", 
            "#2171B5", 
            "#185BA4", 
            "#084594"
          ]
        }, 
        "name_en": "Snow Water Equivalent SWE", 
        "id": "Precip_Seq_SWE_Snowpack"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس السحب الحملية الركامية والسيول الوميضية", 
        "source": "NOAA Storm Prediction Center (SPC)", 
        "classes": {
          "3": [
            "#C7EAE5", 
            "#FF9C00", 
            "#4A004A"
          ], 
          "4": [
            "#C7EAE5", 
            "#738751", 
            "#DD3200", 
            "#4A004A"
          ], 
          "5": [
            "#C7EAE5", 
            "#1F7971", 
            "#FF9C00", 
            "#B70002", 
            "#4A004A"
          ], 
          "6": [
            "#C7EAE5", 
            "#3C948C", 
            "#D6B730", 
            "#F55800", 
            "#9A0002", 
            "#4A004A"
          ], 
          "7": [
            "#C7EAE5", 
            "#4EA69E", 
            "#738751", 
            "#FF9C00", 
            "#DD3200", 
            "#870001", 
            "#4A004A"
          ], 
          "8": [
            "#C7EAE5", 
            "#5AB4AC", 
            "#01665E", 
            "#FFCC00", 
            "#FF6600", 
            "#CC0000", 
            "#7A0000", 
            "#4A004A"
          ], 
          "9": [
            "#C7EAE5", 
            "#69BBB3", 
            "#1F7971", 
            "#B1A540", 
            "#FF9C00", 
            "#EC4B00", 
            "#B70002", 
            "#75000E", 
            "#4A004A"
          ], 
          "10": [
            "#C7EAE5", 
            "#74C0B8", 
            "#308880", 
            "#738751", 
            "#FFC200", 
            "#FF7300", 
            "#DD3200", 
            "#A70002", 
            "#710016", 
            "#4A004A"
          ], 
          "11": [
            "#C7EAE5", 
            "#7DC4BD", 
            "#3C948C", 
            "#38705B", 
            "#D6B730", 
            "#FF9C00", 
            "#F55800", 
            "#D11700", 
            "#9A0002", 
            "#6E001C", 
            "#4A004A"
          ]
        }, 
        "name_en": "Severe Convective Cloudburst", 
        "id": "Precip_Multi_ConvectiveStorm"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "شذوذ الرياح الموسمية المدارية وفترات الانقطاع", 
        "source": "Indian Meteorological Department / WMO Monsoon", 
        "classes": {
          "3": [
            "#DFC27D", 
            "#F6E8C3", 
            "#018571"
          ], 
          "4": [
            "#A6611A", 
            "#DFC27D", 
            "#80CDC1", 
            "#018571"
          ], 
          "5": [
            "#A6611A", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#018571"
          ], 
          "6": [
            "#A6611A", 
            "#C4914C", 
            "#DFC27D", 
            "#80CDC1", 
            "#4EA898", 
            "#018571"
          ], 
          "7": [
            "#A6611A", 
            "#C4914C", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#4EA898", 
            "#018571"
          ], 
          "8": [
            "#A6611A", 
            "#BA813B", 
            "#CDA15C", 
            "#DFC27D", 
            "#80CDC1", 
            "#5FB5A5", 
            "#3C9D8B", 
            "#018571"
          ], 
          "9": [
            "#A6611A", 
            "#BA813B", 
            "#CDA15C", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#5FB5A5", 
            "#3C9D8B", 
            "#018571"
          ], 
          "10": [
            "#A6611A", 
            "#B57933", 
            "#C4914C", 
            "#D2A964", 
            "#DFC27D", 
            "#80CDC1", 
            "#67BBAC", 
            "#4EA898", 
            "#319784", 
            "#018571"
          ], 
          "11": [
            "#A6611A", 
            "#B57933", 
            "#C4914C", 
            "#D2A964", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#67BBAC", 
            "#4EA898", 
            "#319784", 
            "#018571"
          ]
        }, 
        "name_en": "Tropical Monsoon Anomaly", 
        "id": "Precip_Div_MonsoonAnomaly"
      }
    ], 
    "folder": "02_Precipitation", 
    "name_en": "Precipitation"
  }, 
  {
    "name_ar": "الضغط عند مستوى سطح البحر", 
    "styles": [
      {
        "category": "Diverging", 
        "name_ar": "مقياس الضغط الجوي المتباعد عند 1013.25 مليبار", 
        "source": "WMO Synoptic Standards (1013.25 hPa)", 
        "classes": {
          "3": [
            "#D6604D", 
            "#FFFFBF", 
            "#2166AC"
          ], 
          "4": [
            "#67001F", 
            "#F4A582", 
            "#92C5DE", 
            "#053061"
          ], 
          "5": [
            "#67001F", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#053061"
          ], 
          "6": [
            "#67001F", 
            "#C4413C", 
            "#F4A582", 
            "#92C5DE", 
            "#347CB8", 
            "#053061"
          ], 
          "7": [
            "#67001F", 
            "#C4413C", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#347CB8", 
            "#053061"
          ], 
          "8": [
            "#67001F", 
            "#B2182B", 
            "#D6604D", 
            "#F4A582", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061"
          ], 
          "9": [
            "#67001F", 
            "#B2182B", 
            "#D6604D", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061"
          ], 
          "10": [
            "#67001F", 
            "#9F1128", 
            "#C4413C", 
            "#DE725A", 
            "#F4A582", 
            "#92C5DE", 
            "#5A9FCA", 
            "#347CB8", 
            "#1A5899", 
            "#053061"
          ], 
          "11": [
            "#67001F", 
            "#9F1128", 
            "#C4413C", 
            "#DE725A", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#5A9FCA", 
            "#347CB8", 
            "#1A5899", 
            "#053061"
          ]
        }, 
        "name_en": "WMO MSLP Diverging", 
        "id": "Pres_Div_WMO_MSLP"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "تدرج المنخفضات والمرتفعات الجوية السينوبتيكية", 
        "source": "NOAA Ocean Prediction Center (OPC)", 
        "classes": {
          "3": [
            "#F46D43", 
            "#FFFFBF", 
            "#4575B4"
          ], 
          "4": [
            "#A50026", 
            "#FDAE61", 
            "#ABD9E9", 
            "#313695"
          ], 
          "5": [
            "#A50026", 
            "#FDAE61", 
            "#FFFFBF", 
            "#ABD9E9", 
            "#313695"
          ], 
          "6": [
            "#A50026", 
            "#E65135", 
            "#FDAE61", 
            "#ABD9E9", 
            "#5E91C3", 
            "#313695"
          ], 
          "7": [
            "#A50026", 
            "#E65135", 
            "#FDAE61", 
            "#FFFFBF", 
            "#ABD9E9", 
            "#5E91C3", 
            "#313695"
          ], 
          "8": [
            "#A50026", 
            "#D73027", 
            "#F46D43", 
            "#FDAE61", 
            "#ABD9E9", 
            "#74ADD1", 
            "#4575B4", 
            "#313695"
          ], 
          "9": [
            "#A50026", 
            "#D73027", 
            "#F46D43", 
            "#FDAE61", 
            "#FFFFBF", 
            "#ABD9E9", 
            "#74ADD1", 
            "#4575B4", 
            "#313695"
          ], 
          "10": [
            "#A50026", 
            "#CA2727", 
            "#E65135", 
            "#F77E4A", 
            "#FDAE61", 
            "#ABD9E9", 
            "#82B8D7", 
            "#5E91C3", 
            "#4265AC", 
            "#313695"
          ], 
          "11": [
            "#A50026", 
            "#CA2727", 
            "#E65135", 
            "#F77E4A", 
            "#FDAE61", 
            "#FFFFBF", 
            "#ABD9E9", 
            "#82B8D7", 
            "#5E91C3", 
            "#4265AC", 
            "#313695"
          ]
        }, 
        "name_en": "Synoptic Highs & Lows", 
        "id": "Pres_Synoptic_HighLow"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "تدرج المنخفضات المدارية العميقة ومراكز الأعاصير", 
        "source": "National Hurricane Center (NHC)", 
        "classes": {
          "3": [
            "#49006A", 
            "#EA509C", 
            "#F49AC2"
          ], 
          "4": [
            "#49006A", 
            "#BD1886", 
            "#F98EAE", 
            "#F49AC2"
          ], 
          "5": [
            "#49006A", 
            "#A1017C", 
            "#EA509C", 
            "#FBA9B8", 
            "#F49AC2"
          ], 
          "6": [
            "#49006A", 
            "#8F017A", 
            "#D32C92", 
            "#F874A5", 
            "#FBB6BC", 
            "#F49AC2"
          ], 
          "7": [
            "#49006A", 
            "#830178", 
            "#BD1886", 
            "#EA509C", 
            "#F98EAE", 
            "#FCBFBE", 
            "#F49AC2"
          ], 
          "8": [
            "#49006A", 
            "#7A0177", 
            "#AE017E", 
            "#DD3497", 
            "#F768A1", 
            "#FA9FB5", 
            "#FCC5C0", 
            "#F49AC2"
          ], 
          "9": [
            "#49006A", 
            "#740175", 
            "#A1017C", 
            "#CB258E", 
            "#EA509C", 
            "#F97EA8", 
            "#FBA9B8", 
            "#FBC0C0", 
            "#F49AC2"
          ], 
          "10": [
            "#49006A", 
            "#6F0074", 
            "#97007B", 
            "#BD1886", 
            "#E03B98", 
            "#F463A0", 
            "#F98EAE", 
            "#FBB0BA", 
            "#FABCC1", 
            "#F49AC2"
          ], 
          "11": [
            "#49006A", 
            "#6C0073", 
            "#8F017A", 
            "#B30980", 
            "#D32C92", 
            "#EA509C", 
            "#F874A5", 
            "#FA9AB3", 
            "#FBB6BC", 
            "#FAB8C1", 
            "#F49AC2"
          ]
        }, 
        "name_en": "Tropical Cyclones & Depressions", 
        "id": "Pres_Multi_Cyclones"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "تدرج كثافة الهواء والباروكلينيكية الجوية", 
        "source": "CPT-City Isobaric Archive", 
        "classes": {
          "3": [
            "#FEE8C8", 
            "#F67A50", 
            "#7F0000"
          ], 
          "4": [
            "#FEE8C8", 
            "#FDAC75", 
            "#DF442D", 
            "#7F0000"
          ], 
          "5": [
            "#FEE8C8", 
            "#FDC18A", 
            "#F67A50", 
            "#CE2718", 
            "#7F0000"
          ], 
          "6": [
            "#FEE8C8", 
            "#FDCA94", 
            "#FD9661", 
            "#EA5C40", 
            "#C1190C", 
            "#7F0000"
          ], 
          "7": [
            "#FEE8C8", 
            "#FDD09A", 
            "#FDAC75", 
            "#F67A50", 
            "#DF442D", 
            "#B90C05", 
            "#7F0000"
          ], 
          "8": [
            "#FEE8C8", 
            "#FDD49E", 
            "#FDBB84", 
            "#FC8D59", 
            "#EF6548", 
            "#D7301F", 
            "#B30000", 
            "#7F0000"
          ], 
          "9": [
            "#FEE8C8", 
            "#FDD6A3", 
            "#FDC18A", 
            "#FD9F69", 
            "#F67A50", 
            "#E65339", 
            "#CE2718", 
            "#AC0000", 
            "#7F0000"
          ], 
          "10": [
            "#FEE8C8", 
            "#FDD8A7", 
            "#FDC68F", 
            "#FDAC75", 
            "#FB8957", 
            "#F16A4A", 
            "#DF442D", 
            "#C72012", 
            "#A70001", 
            "#7F0000"
          ], 
          "11": [
            "#FEE8C8", 
            "#FEDAAB", 
            "#FDCA94", 
            "#FDB780", 
            "#FD9661", 
            "#F67A50", 
            "#EA5C40", 
            "#DA3623", 
            "#C1190C", 
            "#A30001", 
            "#7F0000"
          ]
        }, 
        "name_en": "Isobaric Air Density", 
        "id": "Pres_Seq_Density"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "المنخفضات الجوية الشديدة والأعاصير الحلزونية", 
        "source": "WMO Severe Weather Information Centre", 
        "classes": {
          "3": [
            "#998EC3", 
            "#FFFFBF", 
            "#F1A340"
          ], 
          "4": [
            "#542788", 
            "#D8DAEB", 
            "#FEE0B6", 
            "#B35806"
          ], 
          "5": [
            "#542788", 
            "#D8DAEB", 
            "#FFFFBF", 
            "#FEE0B6", 
            "#B35806"
          ], 
          "6": [
            "#542788", 
            "#998EC3", 
            "#D8DAEB", 
            "#FEE0B6", 
            "#F1A340", 
            "#B35806"
          ], 
          "7": [
            "#542788", 
            "#998EC3", 
            "#D8DAEB", 
            "#FFFFBF", 
            "#FEE0B6", 
            "#F1A340", 
            "#B35806"
          ], 
          "8": [
            "#542788", 
            "#836CAF", 
            "#AEA7D0", 
            "#D8DAEB", 
            "#FEE0B6", 
            "#F8B769", 
            "#DC8A2E", 
            "#B35806"
          ], 
          "9": [
            "#542788", 
            "#836CAF", 
            "#AEA7D0", 
            "#D8DAEB", 
            "#FFFFBF", 
            "#FEE0B6", 
            "#F8B769", 
            "#DC8A2E", 
            "#B35806"
          ], 
          "10": [
            "#542788", 
            "#785BA5", 
            "#998EC3", 
            "#B9B3D7", 
            "#D8DAEB", 
            "#FEE0B6", 
            "#FAC17C", 
            "#F1A340", 
            "#D27D25", 
            "#B35806"
          ], 
          "11": [
            "#542788", 
            "#785BA5", 
            "#998EC3", 
            "#B9B3D7", 
            "#D8DAEB", 
            "#FFFFBF", 
            "#FEE0B6", 
            "#FAC17C", 
            "#F1A340", 
            "#D27D25", 
            "#B35806"
          ]
        }, 
        "name_en": "Severe Cyclone Deep Core", 
        "id": "Pres_Div_SevereCyclone"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "المرتفعات شبه المدارية وحزام الضغط المرتفع الآزوري", 
        "source": "Hadley Circulation Pressure Climatology", 
        "classes": {
          "3": [
            "#B3CDE3", 
            "#8B77B6", 
            "#810F7C"
          ], 
          "4": [
            "#B3CDE3", 
            "#8C96C6", 
            "#8856A7", 
            "#810F7C"
          ], 
          "5": [
            "#B3CDE3", 
            "#96A3CD", 
            "#8B77B6", 
            "#87489C", 
            "#810F7C"
          ], 
          "6": [
            "#B3CDE3", 
            "#9CACD2", 
            "#8C89C0", 
            "#8A63AD", 
            "#863F96", 
            "#810F7C"
          ], 
          "7": [
            "#B3CDE3", 
            "#A0B1D4", 
            "#8C96C6", 
            "#8B77B6", 
            "#8856A7", 
            "#863991", 
            "#810F7C"
          ], 
          "8": [
            "#B3CDE3", 
            "#A2B5D7", 
            "#929ECA", 
            "#8C84BD", 
            "#8A69B0", 
            "#884EA1", 
            "#85348E", 
            "#810F7C"
          ], 
          "9": [
            "#B3CDE3", 
            "#A4B8D8", 
            "#96A3CD", 
            "#8C8EC2", 
            "#8B77B6", 
            "#895EAB", 
            "#87489C", 
            "#85318C", 
            "#810F7C"
          ], 
          "10": [
            "#B3CDE3", 
            "#A6BAD9", 
            "#99A8D0", 
            "#8C96C6", 
            "#8C81BC", 
            "#8B6CB1", 
            "#8856A7", 
            "#874398", 
            "#842E8A", 
            "#810F7C"
          ], 
          "11": [
            "#B3CDE3", 
            "#A7BCDA", 
            "#9CACD2", 
            "#909BC9", 
            "#8C89C0", 
            "#8B77B6", 
            "#8A63AD", 
            "#8850A3", 
            "#863F96", 
            "#842C89", 
            "#810F7C"
          ]
        }, 
        "name_en": "Subtropical High Belts", 
        "id": "Pres_Synoptic_Subtropical"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "المرتفع السيبيري الشتوي مقابل منخفضات المتوسط", 
        "source": "Synoptic Climatology of Eurasia & North Africa", 
        "classes": {
          "3": [
            "#4575B4", 
            "#FFFFBF", 
            "#F46D43"
          ], 
          "4": [
            "#313695", 
            "#74ADD1", 
            "#FDAE61", 
            "#A50026"
          ], 
          "5": [
            "#313695", 
            "#74ADD1", 
            "#FFFFBF", 
            "#FDAE61", 
            "#A50026"
          ], 
          "6": [
            "#313695", 
            "#4575B4", 
            "#74ADD1", 
            "#FDAE61", 
            "#F46D43", 
            "#A50026"
          ], 
          "7": [
            "#313695", 
            "#4575B4", 
            "#74ADD1", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F46D43", 
            "#A50026"
          ], 
          "8": [
            "#313695", 
            "#4060AA", 
            "#5687BE", 
            "#74ADD1", 
            "#FDAE61", 
            "#F8844D", 
            "#D95039", 
            "#A50026"
          ], 
          "9": [
            "#313695", 
            "#4060AA", 
            "#5687BE", 
            "#74ADD1", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F8844D", 
            "#D95039", 
            "#A50026"
          ], 
          "10": [
            "#313695", 
            "#3D55A5", 
            "#4575B4", 
            "#5E91C3", 
            "#74ADD1", 
            "#FDAE61", 
            "#F98F52", 
            "#F46D43", 
            "#CC4234", 
            "#A50026"
          ], 
          "11": [
            "#313695", 
            "#3D55A5", 
            "#4575B4", 
            "#5E91C3", 
            "#74ADD1", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F98F52", 
            "#F46D43", 
            "#CC4234", 
            "#A50026"
          ]
        }, 
        "name_en": "Siberian High vs Mediterranean", 
        "id": "Pres_Div_SiberianAnticyclone"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "تدرج خطوط تساوي الضغط عالي الدقة (2 مليبار)", 
        "source": "NOAA High-Resolution Rapid Refresh (HRRR)", 
        "classes": {
          "3": [
            "#2B83BA", 
            "#FFFFBF", 
            "#D53E4F"
          ], 
          "4": [
            "#2B83BA", 
            "#D3ED9C", 
            "#FECF7D", 
            "#D53E4F"
          ], 
          "5": [
            "#2B83BA", 
            "#ABDDA4", 
            "#FFFFBF", 
            "#FDAE61", 
            "#D53E4F"
          ], 
          "6": [
            "#2B83BA", 
            "#91C9A9", 
            "#EBF7A0", 
            "#FFE695", 
            "#FA9555", 
            "#D53E4F"
          ], 
          "7": [
            "#2B83BA", 
            "#7EBBAC", 
            "#D3ED9C", 
            "#FFFFBF", 
            "#FECF7D", 
            "#F8844D", 
            "#D53E4F"
          ], 
          "8": [
            "#2B83BA", 
            "#70B2AF", 
            "#BDE4A1", 
            "#F1F9A9", 
            "#FFEDA1", 
            "#FEBC6D", 
            "#F67747", 
            "#D53E4F"
          ], 
          "9": [
            "#2B83BA", 
            "#64ABB0", 
            "#ABDDA4", 
            "#E6F598", 
            "#FFFFBF", 
            "#FEE08B", 
            "#FDAE61", 
            "#F46D43", 
            "#D53E4F"
          ], 
          "10": [
            "#2B83BA", 
            "#5FA6B1", 
            "#9DD2A7", 
            "#D3ED9C", 
            "#F4FBAE", 
            "#FFF1A8", 
            "#FECF7D", 
            "#FCA05A", 
            "#F16845", 
            "#D53E4F"
          ], 
          "11": [
            "#2B83BA", 
            "#5CA3B2", 
            "#91C9A9", 
            "#C3E79F", 
            "#EBF7A0", 
            "#FFFFBF", 
            "#FFE695", 
            "#FEC272", 
            "#FA9555", 
            "#EE6446", 
            "#D53E4F"
          ]
        }, 
        "name_en": "High-Resolution Microbar Isobars", 
        "id": "Pres_Multi_MicrobarIsobars"
      }
    ], 
    "folder": "03_Sea_Level_Pressure", 
    "name_en": "Sea Level Pressure"
  }, 
  {
    "name_ar": "الضغط الجوي السطحي", 
    "styles": [
      {
        "category": "Sequential", 
        "name_ar": "تدرج الضغط السطحي الهبسومتري المرتبط بالتضاريس", 
        "source": "ICAO Standard Atmosphere Model", 
        "classes": {
          "3": [
            "#003C30", 
            "#E0E9D4", 
            "#543005"
          ], 
          "4": [
            "#003C30", 
            "#80CDC1", 
            "#DFC27D", 
            "#543005"
          ], 
          "5": [
            "#003C30", 
            "#4AA49B", 
            "#E0E9D4", 
            "#C89142", 
            "#543005"
          ], 
          "6": [
            "#003C30", 
            "#2C8D85", 
            "#ABDED6", 
            "#EDD9A7", 
            "#B57726", 
            "#543005"
          ], 
          "7": [
            "#003C30", 
            "#1F7E76", 
            "#80CDC1", 
            "#E0E9D4", 
            "#DFC27D", 
            "#A5691C", 
            "#543005"
          ], 
          "8": [
            "#003C30", 
            "#14746C", 
            "#62B6AB", 
            "#BDE6E0", 
            "#F3E2B9", 
            "#D2A65B", 
            "#9A5E15", 
            "#543005"
          ], 
          "9": [
            "#003C30", 
            "#0A6C64", 
            "#4AA49B", 
            "#9CD8CE", 
            "#E0E9D4", 
            "#E8D097", 
            "#C89142", 
            "#92570F", 
            "#543005"
          ], 
          "10": [
            "#003C30", 
            "#01665E", 
            "#35978F", 
            "#80CDC1", 
            "#C7EAE5", 
            "#F6E8C3", 
            "#DFC27D", 
            "#BF812D", 
            "#8C510A", 
            "#543005"
          ], 
          "11": [
            "#003C30", 
            "#016259", 
            "#2C8D85", 
            "#6BBDB2", 
            "#ABDED6", 
            "#E0E9D4", 
            "#EDD9A7", 
            "#D6AE65", 
            "#B57726", 
            "#864E0A", 
            "#543005"
          ]
        }, 
        "name_en": "Hypsometric Topographic Pressure", 
        "id": "SPres_Seq_Hypsometric"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "تدرج الضغط الطبوغرافي المعقد للمرتفعات والوديان", 
        "source": "USGS / NASA SRTM Digital Elevation", 
        "classes": {
          "3": [
            "#2D004B", 
            "#EDDDD1", 
            "#7F3B08"
          ], 
          "4": [
            "#2D004B", 
            "#B2ABD2", 
            "#FDB863", 
            "#7F3B08"
          ], 
          "5": [
            "#2D004B", 
            "#8C81B5", 
            "#EDDDD1", 
            "#E88F2C", 
            "#7F3B08"
          ], 
          "6": [
            "#2D004B", 
            "#7864A5", 
            "#C9C7E1", 
            "#FFD095", 
            "#D77911", 
            "#7F3B08"
          ], 
          "7": [
            "#2D004B", 
            "#6B4E9A", 
            "#B2ABD2", 
            "#EDDDD1", 
            "#FDB863", 
            "#C96D0D", 
            "#7F3B08"
          ], 
          "8": [
            "#2D004B", 
            "#613E92", 
            "#9C93C2", 
            "#D3D3E7", 
            "#FFDAAA", 
            "#F1A145", 
            "#C0640A", 
            "#7F3B08"
          ], 
          "9": [
            "#2D004B", 
            "#5A318D", 
            "#8C81B5", 
            "#C0BCDB", 
            "#EDDDD1", 
            "#FFC782", 
            "#E88F2C", 
            "#B95D07", 
            "#7F3B08"
          ], 
          "10": [
            "#2D004B", 
            "#542788", 
            "#8073AC", 
            "#B2ABD2", 
            "#D8DAEB", 
            "#FEE0B6", 
            "#FDB863", 
            "#E08214", 
            "#B35806", 
            "#7F3B08"
          ], 
          "11": [
            "#2D004B", 
            "#502382", 
            "#7864A5", 
            "#A39AC7", 
            "#C9C7E1", 
            "#EDDDD1", 
            "#FFD095", 
            "#F5A84E", 
            "#D77911", 
            "#AE5506", 
            "#7F3B08"
          ]
        }, 
        "name_en": "Orographic Relief Column", 
        "id": "SPres_Multi_Terrain"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "شذوذ الضغط الجوي السطحي عن المعدل التضاريسي", 
        "source": "ECMWF Surface Pressure Diagnostics", 
        "classes": {
          "3": [
            "#67A9CF", 
            "#FFFFBF", 
            "#EF6548"
          ], 
          "4": [
            "#2166AC", 
            "#BDC9E1", 
            "#FDBB84", 
            "#B30000"
          ], 
          "5": [
            "#2166AC", 
            "#BDC9E1", 
            "#FFFFBF", 
            "#FDBB84", 
            "#B30000"
          ], 
          "6": [
            "#2166AC", 
            "#67A9CF", 
            "#BDC9E1", 
            "#FDBB84", 
            "#EF6548", 
            "#B30000"
          ], 
          "7": [
            "#2166AC", 
            "#67A9CF", 
            "#BDC9E1", 
            "#FFFFBF", 
            "#FDBB84", 
            "#EF6548", 
            "#B30000"
          ], 
          "8": [
            "#2166AC", 
            "#5392C3", 
            "#86B4D5", 
            "#BDC9E1", 
            "#FDBB84", 
            "#F5835B", 
            "#DB4C31", 
            "#B30000"
          ], 
          "9": [
            "#2166AC", 
            "#5392C3", 
            "#86B4D5", 
            "#BDC9E1", 
            "#FFFFBF", 
            "#FDBB84", 
            "#F5835B", 
            "#DB4C31", 
            "#B30000"
          ], 
          "10": [
            "#2166AC", 
            "#4987BE", 
            "#67A9CF", 
            "#95B9D8", 
            "#BDC9E1", 
            "#FDBB84", 
            "#F89265", 
            "#EF6548", 
            "#D13E25", 
            "#B30000"
          ], 
          "11": [
            "#2166AC", 
            "#4987BE", 
            "#67A9CF", 
            "#95B9D8", 
            "#BDC9E1", 
            "#FFFFBF", 
            "#FDBB84", 
            "#F89265", 
            "#EF6548", 
            "#D13E25", 
            "#B30000"
          ]
        }, 
        "name_en": "Surface Pressure Anomaly", 
        "id": "SPres_Div_Anomaly"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "مقياس الارتفاع البارومتري للطيران والملاحة الجوية", 
        "source": "Federal Aviation Administration (FAA)", 
        "classes": {
          "3": [
            "#C7E9C0", 
            "#41AB5D", 
            "#00441B"
          ], 
          "4": [
            "#C7E9C0", 
            "#74C476", 
            "#238B45", 
            "#00441B"
          ], 
          "5": [
            "#C7E9C0", 
            "#8BCF88", 
            "#41AB5D", 
            "#147C38", 
            "#00441B"
          ], 
          "6": [
            "#C7E9C0", 
            "#98D594", 
            "#61BA6C", 
            "#30984E", 
            "#087331", 
            "#00441B"
          ], 
          "7": [
            "#C7E9C0", 
            "#A1D99B", 
            "#74C476", 
            "#41AB5D", 
            "#238B45", 
            "#006D2C", 
            "#00441B"
          ], 
          "8": [
            "#C7E9C0", 
            "#A7DBA0", 
            "#81CA80", 
            "#58B668", 
            "#359D53", 
            "#1B823E", 
            "#00672A", 
            "#00441B"
          ], 
          "9": [
            "#C7E9C0", 
            "#ABDDA4", 
            "#8BCF88", 
            "#68BE70", 
            "#41AB5D", 
            "#2B934B", 
            "#147C38", 
            "#006228", 
            "#00441B"
          ], 
          "10": [
            "#C7E9C0", 
            "#AEDEA7", 
            "#92D28F", 
            "#74C476", 
            "#53B365", 
            "#37A055", 
            "#238B45", 
            "#0E7734", 
            "#005F26", 
            "#00441B"
          ], 
          "11": [
            "#C7E9C0", 
            "#B0DFAA", 
            "#98D594", 
            "#7DC87D", 
            "#61BA6C", 
            "#41AB5D", 
            "#30984E", 
            "#1D8540", 
            "#087331", 
            "#005C25", 
            "#00441B"
          ]
        }, 
        "name_en": "Barometric Altimeter QNH", 
        "id": "SPres_Seq_Altimeter"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "الضغط السطحي للهضاب العالية (هضبة التبت وإثيوبيا)", 
        "source": "High-Altitude Meteorology Research", 
        "classes": {
          "3": [
            "#313695", 
            "#E0F3F8", 
            "#F46D43"
          ], 
          "4": [
            "#313695", 
            "#99CAE1", 
            "#FFF5AF", 
            "#F46D43"
          ], 
          "5": [
            "#313695", 
            "#74ADD1", 
            "#E0F3F8", 
            "#FEE090", 
            "#F46D43"
          ], 
          "6": [
            "#313695", 
            "#6296C5", 
            "#B6DEEC", 
            "#FAFDCB", 
            "#FFCC7D", 
            "#F46D43"
          ], 
          "7": [
            "#313695", 
            "#5687BE", 
            "#99CAE1", 
            "#E0F3F8", 
            "#FFF5AF", 
            "#FEBF70", 
            "#F46D43"
          ], 
          "8": [
            "#313695", 
            "#4C7DB8", 
            "#84B9D8", 
            "#C2E4EF", 
            "#F3FAD8", 
            "#FFE99D", 
            "#FEB568", 
            "#F46D43"
          ], 
          "9": [
            "#313695", 
            "#4575B4", 
            "#74ADD1", 
            "#ABD9E9", 
            "#E0F3F8", 
            "#FFFFBF", 
            "#FEE090", 
            "#FDAE61", 
            "#F46D43"
          ], 
          "10": [
            "#313695", 
            "#446EB1", 
            "#6AA0CB", 
            "#99CAE1", 
            "#C9E7F1", 
            "#EFF8DF", 
            "#FFF5AF", 
            "#FED585", 
            "#FCA75E", 
            "#F46D43"
          ], 
          "11": [
            "#313695", 
            "#4268AE", 
            "#6296C5", 
            "#8BBEDB", 
            "#B6DEEC", 
            "#E0F3F8", 
            "#FAFDCB", 
            "#FFECA3", 
            "#FFCC7D", 
            "#FCA25B", 
            "#F46D43"
          ]
        }, 
        "name_en": "Tibetan & Ethiopian Plateau", 
        "id": "SPres_Multi_PlateauHigh"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الضغط السطحي للمنخفضات العميقة (القطارة والبحر الميت)", 
        "source": "Dead Sea & Qattara Basin Barometric Studies", 
        "classes": {
          "3": [
            "#FFFFD4", 
            "#FE9929", 
            "#993404"
          ], 
          "4": [
            "#FFFFD4", 
            "#FFC46E", 
            "#E67317", 
            "#993404"
          ], 
          "5": [
            "#FFFFD4", 
            "#FED98E", 
            "#FE9929", 
            "#D95F0E", 
            "#993404"
          ], 
          "6": [
            "#FFFFD4", 
            "#FFE19C", 
            "#FFB354", 
            "#EF821E", 
            "#CC560C", 
            "#993404"
          ], 
          "7": [
            "#FFFFD4", 
            "#FFE6A5", 
            "#FFC46E", 
            "#FE9929", 
            "#E67317", 
            "#C3500A", 
            "#993404"
          ], 
          "8": [
            "#FFFFD4", 
            "#FFE9AC", 
            "#FFD080", 
            "#FFAC49", 
            "#F48921", 
            "#DE6812", 
            "#BD4C09", 
            "#993404"
          ], 
          "9": [
            "#FFFFD4", 
            "#FFECB1", 
            "#FED98E", 
            "#FFB95E", 
            "#FE9929", 
            "#EC7C1C", 
            "#D95F0E", 
            "#B94908", 
            "#993404"
          ], 
          "10": [
            "#FFFFD4", 
            "#FFEEB5", 
            "#FFDD96", 
            "#FFC46E", 
            "#FFA742", 
            "#F68C23", 
            "#E67317", 
            "#D25A0D", 
            "#B54708", 
            "#993404"
          ], 
          "11": [
            "#FFFFD4", 
            "#FFF0B8", 
            "#FFE19C", 
            "#FFCC7B", 
            "#FFB354", 
            "#FE9929", 
            "#EF821E", 
            "#E16B14", 
            "#CC560C", 
            "#B24507", 
            "#993404"
          ]
        }, 
        "name_en": "Deep Depression & Rift Valley", 
        "id": "SPres_Seq_ValleyBasin"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "انحراف تدرج الضغط الشاقولي عن الغلاف المعياري", 
        "source": "WMO Upper-Air Sounding Standards", 
        "classes": {
          "3": [
            "#2166AC", 
            "#FFFFBF", 
            "#D6604D"
          ], 
          "4": [
            "#053061", 
            "#4393C3", 
            "#F4A582", 
            "#67001F"
          ], 
          "5": [
            "#053061", 
            "#4393C3", 
            "#FFFFBF", 
            "#F4A582", 
            "#67001F"
          ], 
          "6": [
            "#053061", 
            "#2166AC", 
            "#4393C3", 
            "#F4A582", 
            "#D6604D", 
            "#67001F"
          ], 
          "7": [
            "#053061", 
            "#2166AC", 
            "#4393C3", 
            "#FFFFBF", 
            "#F4A582", 
            "#D6604D", 
            "#67001F"
          ], 
          "8": [
            "#053061", 
            "#185392", 
            "#2E75B4", 
            "#4393C3", 
            "#F4A582", 
            "#E1785E", 
            "#B0433D", 
            "#67001F"
          ], 
          "9": [
            "#053061", 
            "#185392", 
            "#2E75B4", 
            "#4393C3", 
            "#FFFFBF", 
            "#F4A582", 
            "#E1785E", 
            "#B0433D", 
            "#67001F"
          ], 
          "10": [
            "#053061", 
            "#134A86", 
            "#2166AC", 
            "#347CB8", 
            "#4393C3", 
            "#F4A582", 
            "#E68367", 
            "#D6604D", 
            "#9D3435", 
            "#67001F"
          ], 
          "11": [
            "#053061", 
            "#134A86", 
            "#2166AC", 
            "#347CB8", 
            "#4393C3", 
            "#FFFFBF", 
            "#F4A582", 
            "#E68367", 
            "#D6604D", 
            "#9D3435", 
            "#67001F"
          ]
        }, 
        "name_en": "Atmospheric Lapse Rate Departure", 
        "id": "SPres_Div_LapseRate"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "الضغط السطحي للتضاريس الدقيقة والمنحدرات", 
        "source": "Complex Terrain Mesoscale Meteorology", 
        "classes": {
          "3": [
            "#00441B", 
            "#FFFFCC", 
            "#800026"
          ], 
          "4": [
            "#00441B", 
            "#ACDDA7", 
            "#FFC062", 
            "#800026"
          ], 
          "5": [
            "#00441B", 
            "#74C476", 
            "#FFFFCC", 
            "#FD8D3C", 
            "#800026"
          ], 
          "6": [
            "#00441B", 
            "#56AD62", 
            "#D2EDC2", 
            "#FFE087", 
            "#F4692E", 
            "#800026"
          ], 
          "7": [
            "#00441B", 
            "#419E55", 
            "#ACDDA7", 
            "#FFFFCC", 
            "#FFC062", 
            "#ED4D26", 
            "#800026"
          ], 
          "8": [
            "#00441B", 
            "#31934C", 
            "#8DCF8B", 
            "#DFF2C5", 
            "#FFE99B", 
            "#FFA34C", 
            "#E73520", 
            "#800026"
          ], 
          "9": [
            "#00441B", 
            "#238B45", 
            "#74C476", 
            "#C7E9C0", 
            "#FFFFCC", 
            "#FED976", 
            "#FD8D3C", 
            "#E31A1C", 
            "#800026"
          ], 
          "10": [
            "#00441B", 
            "#1F8340", 
            "#64B76B", 
            "#ACDDA7", 
            "#E6F5C7", 
            "#FFEEA6", 
            "#FFC062", 
            "#F87934", 
            "#D8171E", 
            "#800026"
          ], 
          "11": [
            "#00441B", 
            "#1C7C3C", 
            "#56AD62", 
            "#96D393", 
            "#D2EDC2", 
            "#FFFFCC", 
            "#FFE087", 
            "#FFAC53", 
            "#F4692E", 
            "#CF141F", 
            "#800026"
          ]
        }, 
        "name_en": "Micro-relief Surface Pressure", 
        "id": "SPres_Multi_MicroRelief"
      }
    ], 
    "folder": "04_Surface_Pressure", 
    "name_en": "Surface Pressure"
  }, 
  {
    "name_ar": "سرعة واتجاه الرياح", 
    "styles": [
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس بوفورت الدولي لسرعة وطاقة الرياح", 
        "source": "WMO-No. 306 Beaufort Scale", 
        "classes": {
          "3": [
            "#BEE3F8", 
            "#FDAE61", 
            "#49006A"
          ], 
          "4": [
            "#BEE3F8", 
            "#BBDC93", 
            "#EB5736", 
            "#49006A"
          ], 
          "5": [
            "#BEE3F8", 
            "#1A9641", 
            "#FDAE61", 
            "#D7191C", 
            "#49006A"
          ], 
          "6": [
            "#BEE3F8", 
            "#5DB151", 
            "#FFEFAC", 
            "#F67B49", 
            "#B60844", 
            "#49006A"
          ], 
          "7": [
            "#BEE3F8", 
            "#7EC35C", 
            "#BBDC93", 
            "#FDAE61", 
            "#EB5736", 
            "#9E015B", 
            "#49006A"
          ], 
          "8": [
            "#BEE3F8", 
            "#95CF64", 
            "#6BB463", 
            "#FFDC96", 
            "#F98A50", 
            "#E03927", 
            "#8A006B", 
            "#49006A"
          ], 
          "9": [
            "#BEE3F8", 
            "#A6D96A", 
            "#1A9641", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F46D43", 
            "#D7191C", 
            "#7A0177", 
            "#49006A"
          ], 
          "10": [
            "#BEE3F8", 
            "#AADA7B", 
            "#44A54A", 
            "#BBDC93", 
            "#FFD28A", 
            "#FA9253", 
            "#EB5736", 
            "#C51034", 
            "#750176", 
            "#49006A"
          ], 
          "11": [
            "#BEE3F8", 
            "#AEDB88", 
            "#5DB151", 
            "#83C072", 
            "#FFEFAC", 
            "#FDAE61", 
            "#F67B49", 
            "#E3432B", 
            "#B60844", 
            "#700074", 
            "#49006A"
          ]
        }, 
        "name_en": "WMO Beaufort Wind Scale", 
        "id": "Wind_Seq_Beaufort"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "سرعة الرياح القطرية لرادار الدوبلر (اقتراب/ابتعاد)", 
        "source": "NOAA ROC Doppler Radial Velocity", 
        "classes": {
          "3": [
            "#008000", 
            "#C5C5C5", 
            "#CC0000"
          ], 
          "4": [
            "#00FF00", 
            "#004000", 
            "#660000", 
            "#FF0000"
          ], 
          "5": [
            "#00FF00", 
            "#004000", 
            "#C5C5C5", 
            "#660000", 
            "#FF0000"
          ], 
          "6": [
            "#00FF00", 
            "#009F00", 
            "#004000", 
            "#660000", 
            "#B20001", 
            "#FF0000"
          ], 
          "7": [
            "#00FF00", 
            "#009F00", 
            "#004000", 
            "#C5C5C5", 
            "#660000", 
            "#B20001", 
            "#FF0000"
          ], 
          "8": [
            "#00FF00", 
            "#00BF00", 
            "#008000", 
            "#004000", 
            "#660000", 
            "#990000", 
            "#CC0000", 
            "#FF0000"
          ], 
          "9": [
            "#00FF00", 
            "#00BF00", 
            "#008000", 
            "#004000", 
            "#C5C5C5", 
            "#660000", 
            "#990000", 
            "#CC0000", 
            "#FF0000"
          ], 
          "10": [
            "#00FF00", 
            "#00CF00", 
            "#009F00", 
            "#006F01", 
            "#004000", 
            "#660000", 
            "#8C0001", 
            "#B20001", 
            "#D90000", 
            "#FF0000"
          ], 
          "11": [
            "#00FF00", 
            "#00CF00", 
            "#009F00", 
            "#006F01", 
            "#004000", 
            "#C5C5C5", 
            "#660000", 
            "#8C0001", 
            "#B20001", 
            "#D90000", 
            "#FF0000"
          ]
        }, 
        "name_en": "Doppler Radial Velocity", 
        "id": "Wind_Multi_DopplerVelocity"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس سافير-سيمبسون لشدة الأعاصير المدارية", 
        "source": "NOAA National Hurricane Center (NHC)", 
        "classes": {
          "3": [
            "#41B6C4", 
            "#FD8D3C", 
            "#4D004B"
          ], 
          "4": [
            "#41B6C4", 
            "#FED976", 
            "#E31A1C", 
            "#4D004B"
          ], 
          "5": [
            "#41B6C4", 
            "#A3818B", 
            "#FD8D3C", 
            "#B00B23", 
            "#4D004B"
          ], 
          "6": [
            "#41B6C4", 
            "#655192", 
            "#FFBB5F", 
            "#EE5528", 
            "#930325", 
            "#4D004B"
          ], 
          "7": [
            "#41B6C4", 
            "#253494", 
            "#FED976", 
            "#FD8D3C", 
            "#E31A1C", 
            "#800026", 
            "#4D004B"
          ], 
          "8": [
            "#41B6C4", 
            "#2F469B", 
            "#CBA584", 
            "#FFAE55", 
            "#F3662D", 
            "#C61221", 
            "#7A002C", 
            "#4D004B"
          ], 
          "9": [
            "#41B6C4", 
            "#3554A0", 
            "#A3818B", 
            "#FFC767", 
            "#FD8D3C", 
            "#EA4323", 
            "#B00B23", 
            "#750030", 
            "#4D004B"
          ], 
          "10": [
            "#41B6C4", 
            "#395EA4", 
            "#82658F", 
            "#FED976", 
            "#FFA74F", 
            "#F56F31", 
            "#E31A1C", 
            "#A00624", 
            "#710033", 
            "#4D004B"
          ], 
          "11": [
            "#41B6C4", 
            "#3B67A8", 
            "#655192", 
            "#DAB581", 
            "#FFBB5F", 
            "#FD8D3C", 
            "#EE5528", 
            "#CF141F", 
            "#930325", 
            "#6D0035", 
            "#4D004B"
          ]
        }, 
        "name_en": "Saffir-Simpson Hurricane Scale", 
        "id": "Wind_Multi_Hurricanes"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مخاطر الاضطرابات الجوية لطيران الخطوط الجوية", 
        "source": "ICAO / FAA Aviation Turbulence Scale", 
        "classes": {
          "3": [
            "#2B83BA", 
            "#FDAE61", 
            "#4A0000"
          ], 
          "4": [
            "#2B83BA", 
            "#FFFFBF", 
            "#D7191C", 
            "#4A0000"
          ], 
          "5": [
            "#2B83BA", 
            "#D5EEB1", 
            "#FDAE61", 
            "#B80C14", 
            "#4A0000"
          ], 
          "6": [
            "#2B83BA", 
            "#BCE4A9", 
            "#FFDF99", 
            "#E96336", 
            "#A50410", 
            "#4A0000"
          ], 
          "7": [
            "#2B83BA", 
            "#ABDDA4", 
            "#FFFFBF", 
            "#FDAE61", 
            "#D7191C", 
            "#99000D", 
            "#4A0000"
          ], 
          "8": [
            "#2B83BA", 
            "#9ECFA8", 
            "#E7F5B7", 
            "#FFD189", 
            "#EF7A42", 
            "#C51218", 
            "#8D000C", 
            "#4A0000"
          ], 
          "9": [
            "#2B83BA", 
            "#93C5AB", 
            "#D5EEB1", 
            "#FFEBA7", 
            "#FDAE61", 
            "#E24D2C", 
            "#B80C14", 
            "#84000B", 
            "#4A0000"
          ], 
          "10": [
            "#2B83BA", 
            "#8BBEAD", 
            "#C7E8AD", 
            "#FFFFBF", 
            "#FFC980", 
            "#F38649", 
            "#D7191C", 
            "#AD0812", 
            "#7D000B", 
            "#4A0000"
          ], 
          "11": [
            "#2B83BA", 
            "#84B8AE", 
            "#BCE4A9", 
            "#EEF8BA", 
            "#FFDF99", 
            "#FDAE61", 
            "#E96336", 
            "#CA1419", 
            "#A50410", 
            "#78000A", 
            "#4A0000"
          ]
        }, 
        "name_en": "Clear Air Turbulence Risk", 
        "id": "Wind_Multi_AviationTurbulence"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "مقياس الأنواء البحرية والرياح العاتية في عرض البحر", 
        "source": "National Data Buoy Center (NDBC)", 
        "classes": {
          "3": [
            "#B2E2E2", 
            "#4CB281", 
            "#006D2C"
          ], 
          "4": [
            "#B2E2E2", 
            "#66C2A4", 
            "#2CA25F", 
            "#006D2C"
          ], 
          "5": [
            "#B2E2E2", 
            "#7ACAB3", 
            "#4CB281", 
            "#239452", 
            "#006D2C"
          ], 
          "6": [
            "#B2E2E2", 
            "#86CFBC", 
            "#5CBC96", 
            "#3AA86D", 
            "#1D8C4A", 
            "#006D2C"
          ], 
          "7": [
            "#B2E2E2", 
            "#8DD2C3", 
            "#66C2A4", 
            "#4CB281", 
            "#2CA25F", 
            "#198745", 
            "#006D2C"
          ], 
          "8": [
            "#B2E2E2", 
            "#93D4C7", 
            "#72C7AD", 
            "#58B990", 
            "#40AB73", 
            "#279A58", 
            "#168341", 
            "#006D2C"
          ], 
          "9": [
            "#B2E2E2", 
            "#97D6CA", 
            "#7ACAB3", 
            "#60BE9B", 
            "#4CB281", 
            "#35A668", 
            "#239452", 
            "#14803F", 
            "#006D2C"
          ], 
          "10": [
            "#B2E2E2", 
            "#9AD7CD", 
            "#81CDB8", 
            "#66C2A4", 
            "#55B78D", 
            "#43AD76", 
            "#2CA25F", 
            "#20904E", 
            "#127E3D", 
            "#006D2C"
          ], 
          "11": [
            "#B2E2E2", 
            "#9CD9CF", 
            "#86CFBC", 
            "#6EC5AA", 
            "#5CBC96", 
            "#4CB281", 
            "#3AA86D", 
            "#289D5A", 
            "#1D8C4A", 
            "#107D3B", 
            "#006D2C"
          ]
        }, 
        "name_en": "Marine Offshore Gale Scale", 
        "id": "Wind_Seq_MarineGale"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس فوجيتا المطور للأعاصير القمعية التدميرية", 
        "source": "NOAA Storm Prediction Center (EF-Scale)", 
        "classes": {
          "3": [
            "#C7E9C0", 
            "#FD8D3C", 
            "#490000"
          ], 
          "4": [
            "#C7E9C0", 
            "#FEB24C", 
            "#FC4E2A", 
            "#490000"
          ], 
          "5": [
            "#C7E9C0", 
            "#C2BD62", 
            "#FD8D3C", 
            "#D62F29", 
            "#490000"
          ], 
          "6": [
            "#C7E9C0", 
            "#97C26E", 
            "#FEA445", 
            "#FD6A31", 
            "#C01827", 
            "#490000"
          ], 
          "7": [
            "#C7E9C0", 
            "#74C476", 
            "#FEB24C", 
            "#FD8D3C", 
            "#FC4E2A", 
            "#B10026", 
            "#490000"
          ], 
          "8": [
            "#C7E9C0", 
            "#81C980", 
            "#DDB959", 
            "#FE9D43", 
            "#FD7534", 
            "#E63D29", 
            "#A10021", 
            "#490000"
          ], 
          "9": [
            "#C7E9C0", 
            "#8ACD88", 
            "#C2BD62", 
            "#FEA948", 
            "#FD8D3C", 
            "#FD602E", 
            "#D62F29", 
            "#95001E", 
            "#490000"
          ], 
          "10": [
            "#C7E9C0", 
            "#91D08E", 
            "#ABC069", 
            "#FEB24C", 
            "#FE9A41", 
            "#FD7A36", 
            "#FC4E2A", 
            "#CA2328", 
            "#8C001B", 
            "#490000"
          ], 
          "11": [
            "#C7E9C0", 
            "#96D393", 
            "#97C26E", 
            "#E7B755", 
            "#FEA445", 
            "#FD8D3C", 
            "#FD6A31", 
            "#ED422A", 
            "#C01827", 
            "#850019", 
            "#490000"
          ]
        }, 
        "name_en": "Enhanced Fujita Tornado Scale", 
        "id": "Wind_Multi_EF_Tornado"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مؤشر التبريد بالرياح ومخاطر التجمد البشري", 
        "source": "NOAA National Weather Service (Wind Chill)", 
        "classes": {
          "3": [
            "#A5D8F7", 
            "#2C71B1", 
            "#67001F"
          ], 
          "4": [
            "#A5D8F7", 
            "#65A4CF", 
            "#2C3D92", 
            "#67001F"
          ], 
          "5": [
            "#A5D8F7", 
            "#8ABCDA", 
            "#2C71B1", 
            "#3B1F85", 
            "#67001F"
          ], 
          "6": [
            "#A5D8F7", 
            "#9ECAE1", 
            "#4292C6", 
            "#08519C", 
            "#3F007D", 
            "#67001F"
          ], 
          "7": [
            "#A5D8F7", 
            "#9FCCE5", 
            "#65A4CF", 
            "#2C71B1", 
            "#2C3D92", 
            "#4D006C", 
            "#67001F"
          ], 
          "8": [
            "#A5D8F7", 
            "#A0CEE7", 
            "#7BB2D5", 
            "#3C88C0", 
            "#175AA2", 
            "#362D8A", 
            "#540061", 
            "#67001F"
          ], 
          "9": [
            "#A5D8F7", 
            "#A1CFE9", 
            "#8ABCDA", 
            "#5099C9", 
            "#2C71B1", 
            "#1C4A98", 
            "#3B1F85", 
            "#580058", 
            "#67001F"
          ], 
          "10": [
            "#A5D8F7", 
            "#A1D0EB", 
            "#95C4DE", 
            "#65A4CF", 
            "#3983BD", 
            "#1C5FA5", 
            "#2C3D92", 
            "#3D1180", 
            "#5B0052", 
            "#67001F"
          ], 
          "11": [
            "#A5D8F7", 
            "#A2D1EC", 
            "#9ECAE1", 
            "#74AED4", 
            "#4292C6", 
            "#2C71B1", 
            "#08519C", 
            "#33328C", 
            "#3F007D", 
            "#5D004D", 
            "#67001F"
          ]
        }, 
        "name_en": "NOAA NWS Wind Chill Index", 
        "id": "Wind_Multi_WindChill"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "كثافة طاقة الرياح لتوليد الكهرباء على ارتفاع 100م", 
        "source": "Global Wind Atlas / DTU Wind Energy", 
        "classes": {
          "3": [
            "#CCEBC5", 
            "#4EB3D3", 
            "#084081"
          ], 
          "4": [
            "#CCEBC5", 
            "#7BCCC4", 
            "#2B8CBE", 
            "#084081"
          ], 
          "5": [
            "#CCEBC5", 
            "#93D4BD", 
            "#4EB3D3", 
            "#1E7AB5", 
            "#084081"
          ], 
          "6": [
            "#CCEBC5", 
            "#A0DAB8", 
            "#6CC2CA", 
            "#3B9BC6", 
            "#136FB0", 
            "#084081"
          ], 
          "7": [
            "#CCEBC5", 
            "#A8DDB5", 
            "#7BCCC4", 
            "#4EB3D3", 
            "#2B8CBE", 
            "#0868AC", 
            "#084081"
          ], 
          "8": [
            "#CCEBC5", 
            "#ADDFB7", 
            "#89D1C0", 
            "#64BECD", 
            "#40A2CA", 
            "#2482B9", 
            "#0962A6", 
            "#084081"
          ], 
          "9": [
            "#CCEBC5", 
            "#B1E1B9", 
            "#93D4BD", 
            "#72C6C8", 
            "#4EB3D3", 
            "#3596C3", 
            "#1E7AB5", 
            "#095EA1", 
            "#084081"
          ], 
          "10": [
            "#CCEBC5", 
            "#B4E2BA", 
            "#9AD7BA", 
            "#7BCCC4", 
            "#60BBCE", 
            "#44A6CC", 
            "#2B8CBE", 
            "#1974B2", 
            "#095A9D", 
            "#084081"
          ], 
          "11": [
            "#CCEBC5", 
            "#B7E3BB", 
            "#A0DAB8", 
            "#85CFC1", 
            "#6CC2CA", 
            "#4EB3D3", 
            "#3B9BC6", 
            "#2685BA", 
            "#136FB0", 
            "#0A589B", 
            "#084081"
          ]
        }, 
        "name_en": "Wind Power Density at 100m", 
        "id": "Wind_Seq_PowerDensity"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "سرعات التيار النفاث في طبقات الجو العليا (250 hPa)", 
        "source": "Aviation High-Altitude Jet Stream Climatology", 
        "classes": {
          "3": [
            "#313695", 
            "#FFD78F", 
            "#4A0000"
          ], 
          "4": [
            "#313695", 
            "#ABD9E9", 
            "#F46D43", 
            "#4A0000"
          ], 
          "5": [
            "#313695", 
            "#82B8D7", 
            "#FFD78F", 
            "#DE422E", 
            "#4A0000"
          ], 
          "6": [
            "#313695", 
            "#6BA1CB", 
            "#E0F0D0", 
            "#FA9555", 
            "#CD2927", 
            "#4A0000"
          ], 
          "7": [
            "#313695", 
            "#5E91C3", 
            "#ABD9E9", 
            "#FFD78F", 
            "#F46D43", 
            "#BE1D27", 
            "#4A0000"
          ], 
          "8": [
            "#313695", 
            "#5385BC", 
            "#94C6DF", 
            "#F4F9C5", 
            "#FCA55D", 
            "#E85537", 
            "#B31227", 
            "#4A0000"
          ], 
          "9": [
            "#313695", 
            "#4B7CB8", 
            "#82B8D7", 
            "#CEE7DA", 
            "#FFD78F", 
            "#F8874E", 
            "#DE422E", 
            "#AB0826", 
            "#4A0000"
          ], 
          "10": [
            "#313695", 
            "#4575B4", 
            "#74ADD1", 
            "#ABD9E9", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F46D43", 
            "#D73027", 
            "#A50026", 
            "#4A0000"
          ], 
          "11": [
            "#313695", 
            "#446FB1", 
            "#6BA1CB", 
            "#9BCCE2", 
            "#E0F0D0", 
            "#FFD78F", 
            "#FA9555", 
            "#EC5D3A", 
            "#CD2927", 
            "#9B0023", 
            "#4A0000"
          ]
        }, 
        "name_en": "Jet Stream Core Isotachs", 
        "id": "Wind_Multi_JetStream"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس دوغلاس لحالة البحر وارتفاع الأمواج", 
        "source": "WMO Marine Meteorology Guide (Douglas Scale)", 
        "classes": {
          "3": [
            "#E0F3F8", 
            "#2166AC", 
            "#67001F"
          ], 
          "4": [
            "#E0F3F8", 
            "#4393C3", 
            "#053061", 
            "#67001F"
          ], 
          "5": [
            "#E0F3F8", 
            "#6EACD1", 
            "#2166AC", 
            "#231C56", 
            "#67001F"
          ], 
          "6": [
            "#E0F3F8", 
            "#84BBD9", 
            "#3781BA", 
            "#10457E", 
            "#2A0D4F", 
            "#67001F"
          ], 
          "7": [
            "#E0F3F8", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061", 
            "#2D004B", 
            "#67001F"
          ], 
          "8": [
            "#E0F3F8", 
            "#9ECBE2", 
            "#5DA1CB", 
            "#3279B6", 
            "#154E8B", 
            "#1B255B", 
            "#390045", 
            "#67001F"
          ], 
          "9": [
            "#E0F3F8", 
            "#A6D0E4", 
            "#6EACD1", 
            "#3C88BD", 
            "#2166AC", 
            "#0C3D73", 
            "#231C56", 
            "#400040", 
            "#67001F"
          ], 
          "10": [
            "#E0F3F8", 
            "#ADD4E7", 
            "#7AB4D5", 
            "#4393C3", 
            "#2E75B4", 
            "#185392", 
            "#053061", 
            "#271552", 
            "#45003C", 
            "#67001F"
          ], 
          "11": [
            "#E0F3F8", 
            "#B2D7E8", 
            "#84BBD9", 
            "#569DC8", 
            "#3781BA", 
            "#2166AC", 
            "#10457E", 
            "#17295D", 
            "#2A0D4F", 
            "#49003A", 
            "#67001F"
          ]
        }, 
        "name_en": "Douglas Sea State & Waves", 
        "id": "Wind_Multi_SeaState"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "نسيم البر والبحر ودورة الرياح اليومية الساحلية", 
        "source": "Coastal Boundary Layer Meteorology", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#6BAED6", 
            "#08519C"
          ], 
          "4": [
            "#BDD7E7", 
            "#8EC1DD", 
            "#4790C5", 
            "#08519C"
          ], 
          "5": [
            "#BDD7E7", 
            "#9ECAE1", 
            "#6BAED6", 
            "#3182BD", 
            "#08519C"
          ], 
          "6": [
            "#BDD7E7", 
            "#A4CDE2", 
            "#81B9DA", 
            "#569CCC", 
            "#2B78B6", 
            "#08519C"
          ], 
          "7": [
            "#BDD7E7", 
            "#A9CEE3", 
            "#8EC1DD", 
            "#6BAED6", 
            "#4790C5", 
            "#2771B2", 
            "#08519C"
          ], 
          "8": [
            "#BDD7E7", 
            "#ACD0E4", 
            "#97C6DF", 
            "#7BB6D9", 
            "#5CA1CF", 
            "#3B88C1", 
            "#246DAF", 
            "#08519C"
          ], 
          "9": [
            "#BDD7E7", 
            "#AED0E4", 
            "#9ECAE1", 
            "#86BCDC", 
            "#6BAED6", 
            "#5198C9", 
            "#3182BD", 
            "#2169AC", 
            "#08519C"
          ], 
          "10": [
            "#BDD7E7", 
            "#AFD1E4", 
            "#A2CBE2", 
            "#8EC1DD", 
            "#77B4D8", 
            "#60A4D0", 
            "#4790C5", 
            "#2E7CB9", 
            "#1F66AB", 
            "#08519C"
          ], 
          "11": [
            "#BDD7E7", 
            "#B1D2E5", 
            "#A4CDE2", 
            "#94C4DF", 
            "#81B9DA", 
            "#6BAED6", 
            "#569CCC", 
            "#3F8BC2", 
            "#2B78B6", 
            "#1E64A9", 
            "#08519C"
          ]
        }, 
        "name_en": "Diurnal Coastal Breeze", 
        "id": "Wind_Seq_ThermalBreeze"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "رياح الخماسين والعواصف الغبارية الصحراوية", 
        "source": "Middle East & North Africa Dust Climatology", 
        "classes": {
          "3": [
            "#FFF7BC", 
            "#EC7C1C", 
            "#3D1703"
          ], 
          "4": [
            "#FFF7BC", 
            "#FFB643", 
            "#AE4207", 
            "#3D1703"
          ], 
          "5": [
            "#FFF7BC", 
            "#FFCC60", 
            "#EC7C1C", 
            "#8C3005", 
            "#3D1703"
          ], 
          "6": [
            "#FFF7BC", 
            "#FFD777", 
            "#FEA231", 
            "#CC560C", 
            "#7A2B06", 
            "#3D1703"
          ], 
          "7": [
            "#FFF7BC", 
            "#FFDE86", 
            "#FFB643", 
            "#EC7C1C", 
            "#AE4207", 
            "#6E2706", 
            "#3D1703"
          ], 
          "8": [
            "#FFF7BC", 
            "#FEE391", 
            "#FEC44F", 
            "#FE9929", 
            "#D95F0E", 
            "#993404", 
            "#662506", 
            "#3D1703"
          ], 
          "9": [
            "#FFF7BC", 
            "#FEE596", 
            "#FFCC60", 
            "#FFA938", 
            "#EC7C1C", 
            "#C14F0A", 
            "#8C3005", 
            "#612306", 
            "#3D1703"
          ], 
          "10": [
            "#FFF7BC", 
            "#FEE79B", 
            "#FFD26D", 
            "#FFB643", 
            "#FA9326", 
            "#DD6611", 
            "#AE4207", 
            "#822D06", 
            "#5D2206", 
            "#3D1703"
          ], 
          "11": [
            "#FFF7BC", 
            "#FFE99E", 
            "#FFD777", 
            "#FEC04B", 
            "#FEA231", 
            "#EC7C1C", 
            "#CC560C", 
            "#9F3805", 
            "#7A2B06", 
            "#592106", 
            "#3D1703"
          ]
        }, 
        "name_en": "Khamsin Sandstorm Gales", 
        "id": "Wind_Multi_KhamsinDust"
      }
    ], 
    "folder": "05_Wind", 
    "name_en": "Wind"
  }, 
  {
    "name_ar": "الرطوبة النسبية وبخار الماء", 
    "styles": [
      {
        "category": "Sequential", 
        "name_ar": "تدرج الرطوبة النسبية السطحية من الجفاف للتشبع", 
        "source": "ColorBrewer YlGnBu Climatology", 
        "classes": {
          "3": [
            "#FFFFD9", 
            "#41B6C4", 
            "#081D58"
          ], 
          "4": [
            "#FFFFD9", 
            "#99D6B9", 
            "#2280B8", 
            "#081D58"
          ], 
          "5": [
            "#FFFFD9", 
            "#C7E9B4", 
            "#41B6C4", 
            "#225EA8", 
            "#081D58"
          ], 
          "6": [
            "#FFFFD9", 
            "#D6EFB3", 
            "#75C8BD", 
            "#2798C1", 
            "#264DA0", 
            "#081D58"
          ], 
          "7": [
            "#FFFFD9", 
            "#E1F3B2", 
            "#99D6B9", 
            "#41B6C4", 
            "#2280B8", 
            "#26429B", 
            "#081D58"
          ], 
          "8": [
            "#FFFFD9", 
            "#E8F6B1", 
            "#B4E1B6", 
            "#69C3BF", 
            "#30A1C2", 
            "#236CAF", 
            "#263A97", 
            "#081D58"
          ], 
          "9": [
            "#FFFFD9", 
            "#EDF8B1", 
            "#C7E9B4", 
            "#7FCDBB", 
            "#41B6C4", 
            "#1D91C0", 
            "#225EA8", 
            "#253494", 
            "#081D58"
          ], 
          "10": [
            "#FFFFD9", 
            "#EFF9B5", 
            "#D0ECB3", 
            "#99D6B9", 
            "#61C0C0", 
            "#34A5C2", 
            "#2280B8", 
            "#2455A4", 
            "#22318D", 
            "#081D58"
          ], 
          "11": [
            "#FFFFD9", 
            "#F1F9B9", 
            "#D6EFB3", 
            "#ACDEB7", 
            "#75C8BD", 
            "#41B6C4", 
            "#2798C1", 
            "#2372B2", 
            "#264DA0", 
            "#1F2F88", 
            "#081D58"
          ]
        }, 
        "name_en": "Surface Relative Humidity", 
        "id": "RH_Seq_YlGnBu"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "قناة بخار الماء بالأشعة تحت الحمراء للأقمار الاصطناعية", 
        "source": "EUMETSAT / GOES Water Vapor Channel", 
        "classes": {
          "3": [
            "#000000", 
            "#787878", 
            "#5B0082"
          ], 
          "4": [
            "#000000", 
            "#505050", 
            "#A0A0A0", 
            "#5B0082"
          ], 
          "5": [
            "#000000", 
            "#3B3B3B", 
            "#787878", 
            "#B4B4B4", 
            "#5B0082"
          ], 
          "6": [
            "#000000", 
            "#303030", 
            "#606060", 
            "#909090", 
            "#C0C0C0", 
            "#5B0082"
          ], 
          "7": [
            "#000000", 
            "#282828", 
            "#505050", 
            "#787878", 
            "#A0A0A0", 
            "#C8C8C8", 
            "#5B0082"
          ], 
          "8": [
            "#000000", 
            "#232323", 
            "#444444", 
            "#676767", 
            "#898989", 
            "#ABABAB", 
            "#BAADBE", 
            "#5B0082"
          ], 
          "9": [
            "#000000", 
            "#202020", 
            "#3B3B3B", 
            "#5A5A5A", 
            "#787878", 
            "#969696", 
            "#B4B4B4", 
            "#AF9AB7", 
            "#5B0082"
          ], 
          "10": [
            "#000000", 
            "#1D1D1D", 
            "#353535", 
            "#505050", 
            "#6A6A6A", 
            "#858585", 
            "#A0A0A0", 
            "#BABABA", 
            "#A78BB1", 
            "#5B0082"
          ], 
          "11": [
            "#000000", 
            "#1B1B1B", 
            "#303030", 
            "#484848", 
            "#606060", 
            "#787878", 
            "#909090", 
            "#A8A8A8", 
            "#C0C0C0", 
            "#A07FAD", 
            "#5B0082"
          ]
        }, 
        "name_en": "Satellite Water Vapor IR", 
        "id": "RH_Multi_SatWaterVapor"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "فرق درجة الحرارة ونقطة الندى (تحديد تشبع الهواء)", 
        "source": "WMO Radiosonde & Synoptic Observations", 
        "classes": {
          "3": [
            "#5AAE61", 
            "#F6E8C3", 
            "#B35806"
          ], 
          "4": [
            "#00441B", 
            "#A6DBA0", 
            "#FDB863", 
            "#7F3B08"
          ], 
          "5": [
            "#00441B", 
            "#A6DBA0", 
            "#F6E8C3", 
            "#FDB863", 
            "#7F3B08"
          ], 
          "6": [
            "#00441B", 
            "#3D934C", 
            "#A6DBA0", 
            "#FDB863", 
            "#C96D0D", 
            "#7F3B08"
          ], 
          "7": [
            "#00441B", 
            "#3D934C", 
            "#A6DBA0", 
            "#F6E8C3", 
            "#FDB863", 
            "#C96D0D", 
            "#7F3B08"
          ], 
          "8": [
            "#00441B", 
            "#1B7837", 
            "#5AAE61", 
            "#A6DBA0", 
            "#FDB863", 
            "#E08214", 
            "#B35806", 
            "#7F3B08"
          ], 
          "9": [
            "#00441B", 
            "#1B7837", 
            "#5AAE61", 
            "#A6DBA0", 
            "#F6E8C3", 
            "#FDB863", 
            "#E08214", 
            "#B35806", 
            "#7F3B08"
          ], 
          "10": [
            "#00441B", 
            "#146B30", 
            "#3D934C", 
            "#6EB970", 
            "#A6DBA0", 
            "#FDB863", 
            "#E88F2C", 
            "#C96D0D", 
            "#A65107", 
            "#7F3B08"
          ], 
          "11": [
            "#00441B", 
            "#146B30", 
            "#3D934C", 
            "#6EB970", 
            "#A6DBA0", 
            "#F6E8C3", 
            "#FDB863", 
            "#E88F2C", 
            "#C96D0D", 
            "#A65107", 
            "#7F3B08"
          ]
        }, 
        "name_en": "Dew Point Depression", 
        "id": "RH_Div_DewPointDepression"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "تدرج تشبع الضباب والندى الكثيف الساحلي", 
        "source": "Aviation Surface Weather Observation (Fog/Mist)", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#4292C6", 
            "#08306B"
          ], 
          "4": [
            "#BDD7E7", 
            "#6BAED6", 
            "#2171B5", 
            "#08306B"
          ], 
          "5": [
            "#BDD7E7", 
            "#86BCDC", 
            "#4292C6", 
            "#1761A8", 
            "#08306B"
          ], 
          "6": [
            "#BDD7E7", 
            "#94C4DF", 
            "#5CA3D0", 
            "#307EBC", 
            "#0F57A1", 
            "#08306B"
          ], 
          "7": [
            "#BDD7E7", 
            "#9ECAE1", 
            "#6BAED6", 
            "#4292C6", 
            "#2171B5", 
            "#08519C", 
            "#08306B"
          ], 
          "8": [
            "#BDD7E7", 
            "#A3CCE2", 
            "#7BB6D9", 
            "#559ECD", 
            "#3684BF", 
            "#1C68AE", 
            "#084C95", 
            "#08306B"
          ], 
          "9": [
            "#BDD7E7", 
            "#A6CDE3", 
            "#86BCDC", 
            "#62A7D2", 
            "#4292C6", 
            "#2B79B9", 
            "#1761A8", 
            "#09498F", 
            "#08306B"
          ], 
          "10": [
            "#BDD7E7", 
            "#A9CEE3", 
            "#8EC1DD", 
            "#6BAED6", 
            "#519BCB", 
            "#3987C0", 
            "#2171B5", 
            "#135BA4", 
            "#09468B", 
            "#08306B"
          ], 
          "11": [
            "#BDD7E7", 
            "#ABCFE3", 
            "#94C4DF", 
            "#76B4D8", 
            "#5CA3D0", 
            "#4292C6", 
            "#307EBC", 
            "#1D6AB0", 
            "#0F57A1", 
            "#094388", 
            "#08306B"
          ]
        }, 
        "name_en": "Fog & Condensation Saturation", 
        "id": "RH_Seq_FogSaturation"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "مؤشر عجز ضغط البخار لإجهاد المحاصيل الزراعية", 
        "source": "FAO-56 Irrigation / Agriculture & Forest Fire", 
        "classes": {
          "3": [
            "#C7E9C0", 
            "#FEB24C", 
            "#B10026"
          ], 
          "4": [
            "#C7E9C0", 
            "#74C476", 
            "#FD8D3C", 
            "#B10026"
          ], 
          "5": [
            "#C7E9C0", 
            "#8BCF88", 
            "#FEB24C", 
            "#FD7033", 
            "#B10026"
          ], 
          "6": [
            "#C7E9C0", 
            "#98D594", 
            "#B4BF66", 
            "#FE9C42", 
            "#FD5D2D", 
            "#B10026"
          ], 
          "7": [
            "#C7E9C0", 
            "#A1D99B", 
            "#74C476", 
            "#FEB24C", 
            "#FD8D3C", 
            "#FC4E2A", 
            "#B10026"
          ], 
          "8": [
            "#C7E9C0", 
            "#A7DBA0", 
            "#81CA80", 
            "#CBBC5F", 
            "#FEA245", 
            "#FD7D37", 
            "#F1462A", 
            "#B10026"
          ], 
          "9": [
            "#C7E9C0", 
            "#ABDDA4", 
            "#8BCF88", 
            "#9FC16C", 
            "#FEB24C", 
            "#FD9740", 
            "#FD7033", 
            "#E93F2A", 
            "#B10026"
          ], 
          "10": [
            "#C7E9C0", 
            "#AEDEA7", 
            "#92D28F", 
            "#74C476", 
            "#D7BA5B", 
            "#FEA647", 
            "#FD8D3C", 
            "#FD6630", 
            "#E33A29", 
            "#B10026"
          ], 
          "11": [
            "#C7E9C0", 
            "#B0DFAA", 
            "#98D594", 
            "#7DC87D", 
            "#B4BF66", 
            "#FEB24C", 
            "#FE9C42", 
            "#FD8238", 
            "#FD5D2D", 
            "#DE3629", 
            "#B10026"
          ]
        }, 
        "name_en": "Vapor Pressure Deficit VPD", 
        "id": "RH_Seq_VPD_Agricultural"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس درجة حرارة نقطة الندى المطلقة (°C)", 
        "source": "NOAA National Weather Service (Dew Point)", 
        "classes": {
          "3": [
            "#800080", 
            "#3FDFC2", 
            "#FF0000"
          ], 
          "4": [
            "#800080", 
            "#3858FF", 
            "#CEFF45", 
            "#FF0000"
          ], 
          "5": [
            "#800080", 
            "#3300DE", 
            "#3FDFC2", 
            "#FFE000", 
            "#FF0000"
          ], 
          "6": [
            "#800080", 
            "#4600B2", 
            "#32A1FF", 
            "#71FF70", 
            "#FFB500", 
            "#FF0000"
          ], 
          "7": [
            "#800080", 
            "#4A0096", 
            "#3858FF", 
            "#3FDFC2", 
            "#CEFF45", 
            "#FF9600", 
            "#FF0000"
          ], 
          "8": [
            "#800080", 
            "#4B0082", 
            "#0000FF", 
            "#00BFFF", 
            "#00FF7F", 
            "#FFFF00", 
            "#FF7F00", 
            "#FF0000"
          ], 
          "9": [
            "#800080", 
            "#530082", 
            "#3300DE", 
            "#3C86FF", 
            "#3FDFC2", 
            "#9AFF61", 
            "#FFE000", 
            "#FF7600", 
            "#FF0000"
          ], 
          "10": [
            "#800080", 
            "#580082", 
            "#4000C6", 
            "#3858FF", 
            "#27C6F2", 
            "#26F88F", 
            "#CEFF45", 
            "#FFC800", 
            "#FF6E00", 
            "#FF0000"
          ], 
          "11": [
            "#800080", 
            "#5C0081", 
            "#4600B2", 
            "#2129FF", 
            "#32A1FF", 
            "#3FDFC2", 
            "#71FF70", 
            "#F1FF23", 
            "#FFB500", 
            "#FF6800", 
            "#FF0000"
          ]
        }, 
        "name_en": "Absolute Dew Point Scale", 
        "id": "RH_Multi_DewPointTemp"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الرطوبة النوعية ونسبة محتوى بخار الماء (جم/كجم)", 
        "source": "Atmospheric Boundary Layer Thermodynamics", 
        "classes": {
          "3": [
            "#D0D1E6", 
            "#3690C0", 
            "#023858"
          ], 
          "4": [
            "#D0D1E6", 
            "#74A9CF", 
            "#0570B0", 
            "#023858"
          ], 
          "5": [
            "#D0D1E6", 
            "#8EB3D5", 
            "#3690C0", 
            "#05659E", 
            "#023858"
          ], 
          "6": [
            "#D0D1E6", 
            "#9DB9D9", 
            "#5E9FC9", 
            "#207DB6", 
            "#045E94", 
            "#023858"
          ], 
          "7": [
            "#D0D1E6", 
            "#A6BDDB", 
            "#74A9CF", 
            "#3690C0", 
            "#0570B0", 
            "#045A8D", 
            "#023858"
          ], 
          "8": [
            "#D0D1E6", 
            "#ACC0DD", 
            "#83AFD2", 
            "#549BC6", 
            "#2782B9", 
            "#056AA6", 
            "#045585", 
            "#023858"
          ], 
          "9": [
            "#D0D1E6", 
            "#B1C2DE", 
            "#8EB3D5", 
            "#67A3CB", 
            "#3690C0", 
            "#1978B4", 
            "#05659E", 
            "#03517F", 
            "#023858"
          ], 
          "10": [
            "#D0D1E6", 
            "#B4C4DF", 
            "#96B6D7", 
            "#74A9CF", 
            "#4E98C5", 
            "#2B85BB", 
            "#0570B0", 
            "#046199", 
            "#034E7B", 
            "#023858"
          ], 
          "11": [
            "#D0D1E6", 
            "#B7C5DF", 
            "#9DB9D9", 
            "#7FADD1", 
            "#5E9FC9", 
            "#3690C0", 
            "#207DB6", 
            "#056CA9", 
            "#045E94", 
            "#034C77", 
            "#023858"
          ]
        }, 
        "name_en": "Specific Humidity g/kg", 
        "id": "RH_Seq_SpecificHumidity"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مؤشر البصيلة الرطبة المعياري للإجهاد الحراري", 
        "source": "ISO 7243 / OSHA Heat Stress Standards", 
        "classes": {
          "3": [
            "#006D2C", 
            "#FFD300", 
            "#7F0000"
          ], 
          "4": [
            "#006D2C", 
            "#C2E03D", 
            "#FF8200", 
            "#7F0000"
          ], 
          "5": [
            "#006D2C", 
            "#71B956", 
            "#FFD300", 
            "#FF4B00", 
            "#7F0000"
          ], 
          "6": [
            "#006D2C", 
            "#2CA25F", 
            "#FFFF00", 
            "#FFA500", 
            "#FF0000", 
            "#7F0000"
          ], 
          "7": [
            "#006D2C", 
            "#269956", 
            "#C2E03D", 
            "#FFD300", 
            "#FF8200", 
            "#E90001", 
            "#7F0000"
          ], 
          "8": [
            "#006D2C", 
            "#229250", 
            "#95CA4D", 
            "#FFF200", 
            "#FFB200", 
            "#FF6500", 
            "#D90002", 
            "#7F0000"
          ], 
          "9": [
            "#006D2C", 
            "#1E8E4B", 
            "#71B956", 
            "#E8F325", 
            "#FFD300", 
            "#FF9800", 
            "#FF4B00", 
            "#CD0002", 
            "#7F0000"
          ], 
          "10": [
            "#006D2C", 
            "#1B8A48", 
            "#50AC5B", 
            "#C2E03D", 
            "#FFEB00", 
            "#FFBA00", 
            "#FF8200", 
            "#FF3000", 
            "#C40003", 
            "#7F0000"
          ], 
          "11": [
            "#006D2C", 
            "#198745", 
            "#2CA25F", 
            "#A3D049", 
            "#FFFF00", 
            "#FFD300", 
            "#FFA500", 
            "#FF6E00", 
            "#FF0000", 
            "#BD0003", 
            "#7F0000"
          ]
        }, 
        "name_en": "Wet Bulb Globe Temp WBGT", 
        "id": "RH_Multi_WBGT_Stress"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "الماء القابل للتساقط وخرائط الأنهار الجوية", 
        "source": "NASA AIRS / NOAA Atmospheric Rivers", 
        "classes": {
          "3": [
            "#B3E5FC", 
            "#347CB8", 
            "#49006A"
          ], 
          "4": [
            "#B3E5FC", 
            "#61A3CC", 
            "#185392", 
            "#49006A"
          ], 
          "5": [
            "#B3E5FC", 
            "#80B8D7", 
            "#347CB8", 
            "#0C3D73", 
            "#49006A"
          ], 
          "6": [
            "#B3E5FC", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061", 
            "#49006A"
          ], 
          "7": [
            "#B3E5FC", 
            "#97CAE3", 
            "#61A3CC", 
            "#347CB8", 
            "#185392", 
            "#1B2C63", 
            "#49006A"
          ], 
          "8": [
            "#B3E5FC", 
            "#9BCEE7", 
            "#73AFD2", 
            "#3F8CC0", 
            "#276CAF", 
            "#114680", 
            "#252864", 
            "#49006A"
          ], 
          "9": [
            "#B3E5FC", 
            "#9ED1E9", 
            "#80B8D7", 
            "#4F99C6", 
            "#347CB8", 
            "#1E5FA2", 
            "#0C3D73", 
            "#2B2664", 
            "#49006A"
          ], 
          "10": [
            "#B3E5FC", 
            "#A1D3EB", 
            "#8ABFDB", 
            "#61A3CC", 
            "#3D89BE", 
            "#2A70B1", 
            "#185392", 
            "#083669", 
            "#2F2365", 
            "#49006A"
          ], 
          "11": [
            "#B3E5FC", 
            "#A2D5ED", 
            "#92C5DE", 
            "#6EACD1", 
            "#4393C3", 
            "#347CB8", 
            "#2166AC", 
            "#134A86", 
            "#053061", 
            "#322165", 
            "#49006A"
          ]
        }, 
        "name_en": "Precipitable Water PWAT", 
        "id": "RH_Multi_PWAT_AtmRiver"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "تقارب وتباعد تدفق الرطوبة الجوية", 
        "source": "Dynamic Meteorology Moisture Convergence", 
        "classes": {
          "3": [
            "#DFC27D", 
            "#F6E8C3", 
            "#01665E"
          ], 
          "4": [
            "#8C510A", 
            "#DFC27D", 
            "#80CDC1", 
            "#01665E"
          ], 
          "5": [
            "#8C510A", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#01665E"
          ], 
          "6": [
            "#8C510A", 
            "#B78845", 
            "#DFC27D", 
            "#80CDC1", 
            "#49988E", 
            "#01665E"
          ], 
          "7": [
            "#8C510A", 
            "#B78845", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#49988E", 
            "#01665E"
          ], 
          "8": [
            "#8C510A", 
            "#A97532", 
            "#C49B57", 
            "#DFC27D", 
            "#80CDC1", 
            "#5BA99F", 
            "#36877E", 
            "#01665E"
          ], 
          "9": [
            "#8C510A", 
            "#A97532", 
            "#C49B57", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#5BA99F", 
            "#36877E", 
            "#01665E"
          ], 
          "10": [
            "#8C510A", 
            "#A26C29", 
            "#B78845", 
            "#CBA560", 
            "#DFC27D", 
            "#80CDC1", 
            "#65B2A7", 
            "#49988E", 
            "#2C7F76", 
            "#01665E"
          ], 
          "11": [
            "#8C510A", 
            "#A26C29", 
            "#B78845", 
            "#CBA560", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#65B2A7", 
            "#49988E", 
            "#2C7F76", 
            "#01665E"
          ]
        }, 
        "name_en": "Moisture Flux Convergence", 
        "id": "RH_Div_MoistureFlux"
      }
    ], 
    "folder": "06_Relative_Humidity", 
    "name_en": "Relative Humidity"
  }, 
  {
    "name_ar": "الإشعاع الشمسي والطاقة الكلية", 
    "styles": [
      {
        "category": "Sequential", 
        "name_ar": "تدرج الإشعاع الشمسي الكلي التراكمي", 
        "source": "ColorBrewer YlOrRd", 
        "classes": {
          "3": [
            "#FFFFCC", 
            "#FD8D3C", 
            "#800026"
          ], 
          "4": [
            "#FFFFCC", 
            "#FFBF5A", 
            "#F44025", 
            "#800026"
          ], 
          "5": [
            "#FFFFCC", 
            "#FED976", 
            "#FD8D3C", 
            "#E31A1C", 
            "#800026"
          ], 
          "6": [
            "#FFFFCC", 
            "#FFE187", 
            "#FEAB49", 
            "#FD5D2D", 
            "#D41121", 
            "#800026"
          ], 
          "7": [
            "#FFFFCC", 
            "#FFE692", 
            "#FFBF5A", 
            "#FD8D3C", 
            "#F44025", 
            "#CA0923", 
            "#800026"
          ], 
          "8": [
            "#FFFFCC", 
            "#FFEA9A", 
            "#FFCE6A", 
            "#FEA245", 
            "#FD6C31", 
            "#EA2D20", 
            "#C20425", 
            "#800026"
          ], 
          "9": [
            "#FFFFCC", 
            "#FFEDA0", 
            "#FED976", 
            "#FEB24C", 
            "#FD8D3C", 
            "#FC4E2A", 
            "#E31A1C", 
            "#BD0026", 
            "#800026"
          ], 
          "10": [
            "#FFFFCC", 
            "#FFEFA5", 
            "#FEDD7F", 
            "#FFBF5A", 
            "#FE9E43", 
            "#FD7434", 
            "#F44025", 
            "#DA151F", 
            "#B60026", 
            "#800026"
          ], 
          "11": [
            "#FFFFCC", 
            "#FFF1A9", 
            "#FFE187", 
            "#FFC965", 
            "#FEAB49", 
            "#FD8D3C", 
            "#FD5D2D", 
            "#ED3321", 
            "#D41121", 
            "#B10026", 
            "#800026"
          ]
        }, 
        "name_en": "Global Solar Radiation", 
        "id": "Solar_Seq_YlOrRd"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الإشعاع الشمسي الأفقي الكلي للبنك الدولي", 
        "source": "World Bank ESMAP / Solargis Global Solar Atlas", 
        "classes": {
          "3": [
            "#FFFFB2", 
            "#F7692D", 
            "#7A0000"
          ], 
          "4": [
            "#FFFFB2", 
            "#FEA346", 
            "#DF2C23", 
            "#7A0000"
          ], 
          "5": [
            "#FFFFB2", 
            "#FFBD54", 
            "#F7692D", 
            "#CA1625", 
            "#7A0000"
          ], 
          "6": [
            "#FFFFB2", 
            "#FECC5C", 
            "#FD8D3C", 
            "#F03B20", 
            "#BD0026", 
            "#7A0000"
          ], 
          "7": [
            "#FFFFB2", 
            "#FFD46B", 
            "#FEA346", 
            "#F7692D", 
            "#DF2C23", 
            "#B10020", 
            "#7A0000"
          ], 
          "8": [
            "#FFFFB2", 
            "#FFDA75", 
            "#FFB24E", 
            "#FC8338", 
            "#F24A24", 
            "#D32124", 
            "#A9001C", 
            "#7A0000"
          ], 
          "9": [
            "#FFFFB2", 
            "#FFDF7D", 
            "#FFBD54", 
            "#FE9540", 
            "#F7692D", 
            "#EA3621", 
            "#CA1625", 
            "#A30019", 
            "#7A0000"
          ], 
          "10": [
            "#FFFFB2", 
            "#FFE383", 
            "#FEC558", 
            "#FEA346", 
            "#FB7D35", 
            "#F35126", 
            "#DF2C23", 
            "#C30B26", 
            "#9F0017", 
            "#7A0000"
          ], 
          "11": [
            "#FFFFB2", 
            "#FFE587", 
            "#FECC5C", 
            "#FFAD4C", 
            "#FD8D3C", 
            "#F7692D", 
            "#F03B20", 
            "#D62424", 
            "#BD0026", 
            "#9B0015", 
            "#7A0000"
          ]
        }, 
        "name_en": "Global Horizontal Irradiance GHI", 
        "id": "Solar_Seq_ESMAP_GHI"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "القدرة الإنتاجية لتوليد الكهرباء الكهروضوئية", 
        "source": "Global Solar Atlas Photovoltaic Electricity", 
        "classes": {
          "3": [
            "#FFF7BC", 
            "#FE9929", 
            "#8C2D04"
          ], 
          "4": [
            "#FFF7BC", 
            "#FEC44F", 
            "#EC7014", 
            "#8C2D04"
          ], 
          "5": [
            "#FFF7BC", 
            "#FFD371", 
            "#FE9929", 
            "#DC5E0B", 
            "#8C2D04"
          ], 
          "6": [
            "#FFF7BC", 
            "#FFDD84", 
            "#FFB340", 
            "#F3811D", 
            "#D25305", 
            "#8C2D04"
          ], 
          "7": [
            "#FFF7BC", 
            "#FEE391", 
            "#FEC44F", 
            "#FE9929", 
            "#EC7014", 
            "#CC4C02", 
            "#8C2D04"
          ], 
          "8": [
            "#FFF7BC", 
            "#FEE697", 
            "#FFCD63", 
            "#FFAC3A", 
            "#F68820", 
            "#E3660F", 
            "#C34703", 
            "#8C2D04"
          ], 
          "9": [
            "#FFF7BC", 
            "#FFE89C", 
            "#FFD371", 
            "#FEB946", 
            "#FE9929", 
            "#F17A19", 
            "#DC5E0B", 
            "#BC4403", 
            "#8C2D04"
          ], 
          "10": [
            "#FFF7BC", 
            "#FFEA9F", 
            "#FFD97C", 
            "#FEC44F", 
            "#FFA836", 
            "#F88C22", 
            "#EC7014", 
            "#D75807", 
            "#B64103", 
            "#8C2D04"
          ], 
          "11": [
            "#FFF7BC", 
            "#FFEBA2", 
            "#FFDD84", 
            "#FFCA5D", 
            "#FFB340", 
            "#FE9929", 
            "#F3811D", 
            "#E66910", 
            "#D25305", 
            "#B23F03", 
            "#8C2D04"
          ]
        }, 
        "name_en": "Photovoltaic Potential PVOUT", 
        "id": "Solar_Seq_PVOUT"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الإشعاع المباشر لمحطات الطاقة الشمسية المركزة", 
        "source": "NREL National Solar Radiation Database (NSRDB)", 
        "classes": {
          "3": [
            "#FFFFE5", 
            "#FE9929", 
            "#662506"
          ], 
          "4": [
            "#FFFFE5", 
            "#FFCE66", 
            "#E1640E", 
            "#662506"
          ], 
          "5": [
            "#FFFFE5", 
            "#FEE391", 
            "#FE9929", 
            "#CC4C02", 
            "#662506"
          ], 
          "6": [
            "#FFFFE5", 
            "#FFEBA2", 
            "#FEBC48", 
            "#F07818", 
            "#B74203", 
            "#662506"
          ], 
          "7": [
            "#FFFFE5", 
            "#FFF0AE", 
            "#FFCE66", 
            "#FE9929", 
            "#E1640E", 
            "#AA3C04", 
            "#662506"
          ], 
          "8": [
            "#FFFFE5", 
            "#FFF4B6", 
            "#FFDA7F", 
            "#FFB23F", 
            "#F4821D", 
            "#D55606", 
            "#A03704", 
            "#662506"
          ], 
          "9": [
            "#FFFFE5", 
            "#FFF7BC", 
            "#FEE391", 
            "#FEC44F", 
            "#FE9929", 
            "#EC7014", 
            "#CC4C02", 
            "#993404", 
            "#662506"
          ], 
          "10": [
            "#FFFFE5", 
            "#FFF8C1", 
            "#FEE79B", 
            "#FFCE66", 
            "#FFAC3A", 
            "#F68720", 
            "#E1640E", 
            "#C04703", 
            "#933205", 
            "#662506"
          ], 
          "11": [
            "#FFFFE5", 
            "#FFF9C4", 
            "#FFEBA2", 
            "#FFD777", 
            "#FEBC48", 
            "#FE9929", 
            "#F07818", 
            "#D95B09", 
            "#B74203", 
            "#8F3105", 
            "#662506"
          ]
        }, 
        "name_en": "Direct Normal Irradiance DNI", 
        "id": "Solar_Seq_DNI_Thermal"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "ساعات سطوع الشمس اليومية الفعلية (0-14 ساعة)", 
        "source": "WMO Sunshine Duration Climatological Standard", 
        "classes": {
          "3": [
            "#FFFFD4", 
            "#FE9929", 
            "#8C2D04"
          ], 
          "4": [
            "#FFFFD4", 
            "#FEC44F", 
            "#EC7014", 
            "#8C2D04"
          ], 
          "5": [
            "#FFFFD4", 
            "#FFD371", 
            "#FE9929", 
            "#DC5E0B", 
            "#8C2D04"
          ], 
          "6": [
            "#FFFFD4", 
            "#FFDD84", 
            "#FFB340", 
            "#F3811D", 
            "#D25305", 
            "#8C2D04"
          ], 
          "7": [
            "#FFFFD4", 
            "#FEE391", 
            "#FEC44F", 
            "#FE9929", 
            "#EC7014", 
            "#CC4C02", 
            "#8C2D04"
          ], 
          "8": [
            "#FFFFD4", 
            "#FFE79B", 
            "#FFCD63", 
            "#FFAC3A", 
            "#F68820", 
            "#E3660F", 
            "#C34703", 
            "#8C2D04"
          ], 
          "9": [
            "#FFFFD4", 
            "#FFEAA2", 
            "#FFD371", 
            "#FEB946", 
            "#FE9929", 
            "#F17A19", 
            "#DC5E0B", 
            "#BC4403", 
            "#8C2D04"
          ], 
          "10": [
            "#FFFFD4", 
            "#FFECA7", 
            "#FFD97C", 
            "#FEC44F", 
            "#FFA836", 
            "#F88C22", 
            "#EC7014", 
            "#D75807", 
            "#B64103", 
            "#8C2D04"
          ], 
          "11": [
            "#FFFFD4", 
            "#FFEEAC", 
            "#FFDD84", 
            "#FFCA5D", 
            "#FFB340", 
            "#FE9929", 
            "#F3811D", 
            "#E66910", 
            "#D25305", 
            "#B23F03", 
            "#8C2D04"
          ]
        }, 
        "name_en": "Daily Sunshine Hours", 
        "id": "Solar_Seq_SunshineDuration"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الإشعاع الشمسي المشتت في الغلاف الجوي", 
        "source": "Solar Energy Engineering Diffuse Radiation", 
        "classes": {
          "3": [
            "#CCEBC5", 
            "#7BCCC4", 
            "#2B8CBE"
          ], 
          "4": [
            "#CCEBC5", 
            "#9AD7BA", 
            "#60BBCE", 
            "#2B8CBE"
          ], 
          "5": [
            "#CCEBC5", 
            "#A8DDB5", 
            "#7BCCC4", 
            "#4EB3D3", 
            "#2B8CBE"
          ], 
          "6": [
            "#CCEBC5", 
            "#AFE0B8", 
            "#8ED3BE", 
            "#6CC2CA", 
            "#48ABCF", 
            "#2B8CBE"
          ], 
          "7": [
            "#CCEBC5", 
            "#B4E2BA", 
            "#9AD7BA", 
            "#7BCCC4", 
            "#60BBCE", 
            "#44A6CC", 
            "#2B8CBE"
          ], 
          "8": [
            "#CCEBC5", 
            "#B8E3BC", 
            "#A2DBB7", 
            "#89D1C0", 
            "#70C5C8", 
            "#56B7D1", 
            "#40A2CA", 
            "#2B8CBE"
          ], 
          "9": [
            "#CCEBC5", 
            "#BAE4BD", 
            "#A8DDB5", 
            "#93D4BD", 
            "#7BCCC4", 
            "#67BFCC", 
            "#4EB3D3", 
            "#3E9FC8", 
            "#2B8CBE"
          ], 
          "10": [
            "#CCEBC5", 
            "#BCE5BE", 
            "#ACDFB7", 
            "#9AD7BA", 
            "#86D0C1", 
            "#73C6C7", 
            "#60BBCE", 
            "#4BAFD1", 
            "#3C9DC7", 
            "#2B8CBE"
          ], 
          "11": [
            "#CCEBC5", 
            "#BEE5BF", 
            "#AFE0B8", 
            "#A0DAB8", 
            "#8ED3BE", 
            "#7BCCC4", 
            "#6CC2CA", 
            "#59B8D0", 
            "#48ABCF", 
            "#3B9BC6", 
            "#2B8CBE"
          ]
        }, 
        "name_en": "Diffuse Horizontal Irradiance", 
        "id": "Solar_Seq_DHI_Diffuse"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الإشعاع الشمسي للألواح الكهروضوئية المائلة", 
        "source": "PVGIS European Commission Photovoltaic Platform", 
        "classes": {
          "3": [
            "#FFFFE5", 
            "#FEC44F", 
            "#A50F15"
          ], 
          "4": [
            "#FFFFE5", 
            "#FEE391", 
            "#FB6A4A", 
            "#A50F15"
          ], 
          "5": [
            "#FFFFE5", 
            "#FFEDA7", 
            "#FEC44F", 
            "#ED4E38", 
            "#A50F15"
          ], 
          "6": [
            "#FFFFE5", 
            "#FFF3B3", 
            "#FFD777", 
            "#FE914C", 
            "#E43C2D", 
            "#A50F15"
          ], 
          "7": [
            "#FFFFE5", 
            "#FFF7BC", 
            "#FEE391", 
            "#FEC44F", 
            "#FB6A4A", 
            "#DE2D26", 
            "#A50F15"
          ], 
          "8": [
            "#FFFFE5", 
            "#FFF8C2", 
            "#FFE99D", 
            "#FFD16C", 
            "#FEA04D", 
            "#F35B3F", 
            "#D62923", 
            "#A50F15"
          ], 
          "9": [
            "#FFFFE5", 
            "#FFF9C6", 
            "#FFEDA7", 
            "#FFDB81", 
            "#FEC44F", 
            "#FD834C", 
            "#ED4E38", 
            "#CF2622", 
            "#A50F15"
          ], 
          "10": [
            "#FFFFE5", 
            "#FFFACA", 
            "#FFF0AE", 
            "#FEE391", 
            "#FFCE66", 
            "#FEA84E", 
            "#FB6A4A", 
            "#E84432", 
            "#CB2420", 
            "#A50F15"
          ], 
          "11": [
            "#FFFFE5", 
            "#FFFACC", 
            "#FFF3B3", 
            "#FEE79A", 
            "#FFD777", 
            "#FEC44F", 
            "#FE914C", 
            "#F55F43", 
            "#E43C2D", 
            "#C7221F", 
            "#A50F15"
          ]
        }, 
        "name_en": "Global Tilted Irradiance GTI", 
        "id": "Solar_Seq_GTI_Tilted"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الإشعاع الشمسي الفعال في البناء الضوئي الزراعي", 
        "source": "Agrometeorology Crop Photosynthesis Scale", 
        "classes": {
          "3": [
            "#C7E9C0", 
            "#74C476", 
            "#006D2C"
          ], 
          "4": [
            "#C7E9C0", 
            "#92D28F", 
            "#4AAE5F", 
            "#006D2C"
          ], 
          "5": [
            "#C7E9C0", 
            "#A1D99B", 
            "#74C476", 
            "#31A354", 
            "#006D2C"
          ], 
          "6": [
            "#C7E9C0", 
            "#A9DCA2", 
            "#86CC85", 
            "#5CB768", 
            "#29984C", 
            "#006D2C"
          ], 
          "7": [
            "#C7E9C0", 
            "#AEDEA7", 
            "#92D28F", 
            "#74C476", 
            "#4AAE5F", 
            "#239146", 
            "#006D2C"
          ], 
          "8": [
            "#C7E9C0", 
            "#B1E0AB", 
            "#9BD696", 
            "#81CA80", 
            "#63BB6C", 
            "#3DA859", 
            "#1F8B42", 
            "#006D2C"
          ], 
          "9": [
            "#C7E9C0", 
            "#B4E1AD", 
            "#A1D99B", 
            "#8BCF88", 
            "#74C476", 
            "#55B365", 
            "#31A354", 
            "#1C8840", 
            "#006D2C"
          ], 
          "10": [
            "#C7E9C0", 
            "#B6E2AF", 
            "#A5DB9F", 
            "#92D28F", 
            "#7EC97E", 
            "#67BD6E", 
            "#4AAE5F", 
            "#2D9D4F", 
            "#19853D", 
            "#006D2C"
          ], 
          "11": [
            "#C7E9C0", 
            "#B8E3B1", 
            "#A9DCA2", 
            "#98D594", 
            "#86CC85", 
            "#74C476", 
            "#5CB768", 
            "#41AA5B", 
            "#29984C", 
            "#17823C", 
            "#006D2C"
          ]
        }, 
        "name_en": "Photosynthetically Active PAR", 
        "id": "Solar_Seq_PAR_Agronomy"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "معامل صفاء السماء ونفاذية الغلاف الجوي للإشعاع", 
        "source": "Solar Radiation Clearness Index Modeling", 
        "classes": {
          "3": [
            "#B3CDE3", 
            "#8B77B6", 
            "#810F7C"
          ], 
          "4": [
            "#B3CDE3", 
            "#8C96C6", 
            "#8856A7", 
            "#810F7C"
          ], 
          "5": [
            "#B3CDE3", 
            "#96A3CD", 
            "#8B77B6", 
            "#87489C", 
            "#810F7C"
          ], 
          "6": [
            "#B3CDE3", 
            "#9CACD2", 
            "#8C89C0", 
            "#8A63AD", 
            "#863F96", 
            "#810F7C"
          ], 
          "7": [
            "#B3CDE3", 
            "#A0B1D4", 
            "#8C96C6", 
            "#8B77B6", 
            "#8856A7", 
            "#863991", 
            "#810F7C"
          ], 
          "8": [
            "#B3CDE3", 
            "#A2B5D7", 
            "#929ECA", 
            "#8C84BD", 
            "#8A69B0", 
            "#884EA1", 
            "#85348E", 
            "#810F7C"
          ], 
          "9": [
            "#B3CDE3", 
            "#A4B8D8", 
            "#96A3CD", 
            "#8C8EC2", 
            "#8B77B6", 
            "#895EAB", 
            "#87489C", 
            "#85318C", 
            "#810F7C"
          ], 
          "10": [
            "#B3CDE3", 
            "#A6BAD9", 
            "#99A8D0", 
            "#8C96C6", 
            "#8C81BC", 
            "#8B6CB1", 
            "#8856A7", 
            "#874398", 
            "#842E8A", 
            "#810F7C"
          ], 
          "11": [
            "#B3CDE3", 
            "#A7BCDA", 
            "#9CACD2", 
            "#909BC9", 
            "#8C89C0", 
            "#8B77B6", 
            "#8A63AD", 
            "#8850A3", 
            "#863F96", 
            "#842C89", 
            "#810F7C"
          ]
        }, 
        "name_en": "Atmosphere Clearness Index Kt", 
        "id": "Solar_Seq_ClearnessIndex"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "معامل انعكاس سطح الأرض للإشعاع الشمسي (الألبيدو)", 
        "source": "NASA MODIS / VIIRS Surface Albedo", 
        "classes": {
          "3": [
            "#000000", 
            "#999999", 
            "#A5D5F2"
          ], 
          "4": [
            "#000000", 
            "#666666", 
            "#CCCCCC", 
            "#A5D5F2"
          ], 
          "5": [
            "#000000", 
            "#4C4C4C", 
            "#999999", 
            "#D0C7BE", 
            "#A5D5F2"
          ], 
          "6": [
            "#000000", 
            "#3D3D3D", 
            "#7A7A7A", 
            "#B7B7B7", 
            "#D3C4B6", 
            "#A5D5F2"
          ], 
          "7": [
            "#000000", 
            "#333333", 
            "#666666", 
            "#999999", 
            "#CCCCCC", 
            "#D4C2B0", 
            "#A5D5F2"
          ], 
          "8": [
            "#000000", 
            "#2C2C2C", 
            "#575757", 
            "#838383", 
            "#AFAFAF", 
            "#CFC9C4", 
            "#CFC5B9", 
            "#A5D5F2"
          ], 
          "9": [
            "#000000", 
            "#282828", 
            "#4C4C4C", 
            "#727272", 
            "#999999", 
            "#BFBFBF", 
            "#D0C7BE", 
            "#CBC7C0", 
            "#A5D5F2"
          ], 
          "10": [
            "#000000", 
            "#242424", 
            "#434343", 
            "#666666", 
            "#888888", 
            "#AAAAAA", 
            "#CCCCCC", 
            "#D2C5B9", 
            "#C8C8C6", 
            "#A5D5F2"
          ], 
          "11": [
            "#000000", 
            "#212121", 
            "#3D3D3D", 
            "#5B5B5B", 
            "#7A7A7A", 
            "#999999", 
            "#B7B7B7", 
            "#CECAC6", 
            "#D3C4B6", 
            "#C5CACA", 
            "#A5D5F2"
          ]
        }, 
        "name_en": "Surface Shortwave Albedo", 
        "id": "Solar_Multi_SolarAlbedo"
      }
    ], 
    "folder": "07_Solar_Radiation", 
    "name_en": "Solar Radiation"
  }, 
  {
    "name_ar": "مؤشر الأشعة فوق البنفسجية", 
    "styles": [
      {
        "category": "Multi-Hue", 
        "name_ar": "المعيار الدولي الإلزامي لمنظمة الصحة العالمية", 
        "source": "WHO / WMO / UNEP (ISBN 92 4 159007 6)", 
        "classes": {
          "3": [
            "#289500", 
            "#E83A0A", 
            "#452494"
          ], 
          "4": [
            "#289500", 
            "#FBBA00", 
            "#B80010", 
            "#452494"
          ], 
          "5": [
            "#289500", 
            "#D0D900", 
            "#E83A0A", 
            "#A51C3E", 
            "#452494"
          ], 
          "6": [
            "#289500", 
            "#96C900", 
            "#FA7A00", 
            "#CE0010", 
            "#98337C", 
            "#452494"
          ], 
          "7": [
            "#289500", 
            "#6CBD00", 
            "#FBBA00", 
            "#E83A0A", 
            "#B80010", 
            "#8440A8", 
            "#452494"
          ], 
          "8": [
            "#289500", 
            "#48B500", 
            "#F7E400", 
            "#F85900", 
            "#D80010", 
            "#A80010", 
            "#6B49C8", 
            "#452494"
          ], 
          "9": [
            "#289500", 
            "#44B100", 
            "#D0D900", 
            "#FC9300", 
            "#E83A0A", 
            "#C60010", 
            "#A51C3E", 
            "#6644C1", 
            "#452494"
          ], 
          "10": [
            "#289500", 
            "#41AE00", 
            "#B0D000", 
            "#FBBA00", 
            "#F45303", 
            "#DC160F", 
            "#B80010", 
            "#A02960", 
            "#6241BC", 
            "#452494"
          ], 
          "11": [
            "#289500", 
            "#3FAB00", 
            "#96C900", 
            "#F9D700", 
            "#FA7A00", 
            "#E83A0A", 
            "#CE0010", 
            "#AD0010", 
            "#98337C", 
            "#603EB8", 
            "#452494"
          ]
        }, 
        "name_en": "WHO Global Solar UV Index", 
        "id": "UV_Standard_WHO"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس الحماية الصحية من أضرار الأشعة الحارقة", 
        "source": "US Environmental Protection Agency (EPA)", 
        "classes": {
          "3": [
            "#38A800", 
            "#FFAA00", 
            "#4C005C"
          ], 
          "4": [
            "#38A800", 
            "#FFFF00", 
            "#FF0000", 
            "#4C005C"
          ], 
          "5": [
            "#38A800", 
            "#BEE400", 
            "#FFAA00", 
            "#CD0060", 
            "#4C005C"
          ], 
          "6": [
            "#38A800", 
            "#95D400", 
            "#FFDD00", 
            "#FF6400", 
            "#A7008B", 
            "#4C005C"
          ], 
          "7": [
            "#38A800", 
            "#79C900", 
            "#FFFF00", 
            "#FFAA00", 
            "#FF0000", 
            "#8400A8", 
            "#4C005C"
          ], 
          "8": [
            "#38A800", 
            "#71C400", 
            "#DAF000", 
            "#FFCF00", 
            "#FF7A00", 
            "#E40040", 
            "#7C009D", 
            "#4C005C"
          ], 
          "9": [
            "#38A800", 
            "#6AC100", 
            "#BEE400", 
            "#FFEA00", 
            "#FFAA00", 
            "#FF4D00", 
            "#CD0060", 
            "#760094", 
            "#4C005C"
          ], 
          "10": [
            "#38A800", 
            "#65BE00", 
            "#A8DB00", 
            "#FFFF00", 
            "#FFC700", 
            "#FF8600", 
            "#FF0000", 
            "#B90078", 
            "#71008E", 
            "#4C005C"
          ], 
          "11": [
            "#38A800", 
            "#61BC00", 
            "#95D400", 
            "#E5F400", 
            "#FFDD00", 
            "#FFAA00", 
            "#FF6400", 
            "#EC0032", 
            "#A7008B", 
            "#6D0089", 
            "#4C005C"
          ]
        }, 
        "name_en": "EPA Erythemal Damage Spectrum", 
        "id": "UV_EPA_HealthRisk"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الجرعة اليومية للأشعة فوق البنفسجية المؤثرة حيوياً", 
        "source": "CIE S 007/E-1998 Erythemal Action Spectrum", 
        "classes": {
          "3": [
            "#FFFFCC", 
            "#FD7033", 
            "#800026"
          ], 
          "4": [
            "#FFFFCC", 
            "#FEA647", 
            "#EB3021", 
            "#800026"
          ], 
          "5": [
            "#FFFFCC", 
            "#FEBC57", 
            "#FD7033", 
            "#D9141F", 
            "#800026"
          ], 
          "6": [
            "#FFFFCC", 
            "#FFC965", 
            "#FD953F", 
            "#F74627", 
            "#CC0B23", 
            "#800026"
          ], 
          "7": [
            "#FFFFCC", 
            "#FED36F", 
            "#FEA647", 
            "#FD7033", 
            "#EB3021", 
            "#C30425", 
            "#800026"
          ], 
          "8": [
            "#FFFFCC", 
            "#FED976", 
            "#FEB24C", 
            "#FD8D3C", 
            "#FC4E2A", 
            "#E31A1C", 
            "#BD0026", 
            "#800026"
          ], 
          "9": [
            "#FFFFCC", 
            "#FFDE81", 
            "#FEBC57", 
            "#FE9B42", 
            "#FD7033", 
            "#F33E25", 
            "#D9141F", 
            "#B50026", 
            "#800026"
          ], 
          "10": [
            "#FFFFCC", 
            "#FFE189", 
            "#FFC35F", 
            "#FEA647", 
            "#FD873A", 
            "#FC562C", 
            "#EB3021", 
            "#D21021", 
            "#AF0026", 
            "#800026"
          ], 
          "11": [
            "#FFFFCC", 
            "#FFE490", 
            "#FFC965", 
            "#FEAE4A", 
            "#FD953F", 
            "#FD7033", 
            "#F74627", 
            "#E6221D", 
            "#CC0B23", 
            "#AA0026", 
            "#800026"
          ]
        }, 
        "name_en": "Daily Erythemal UV Dose", 
        "id": "UV_ErythemalDose"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "ذروة الأشعة فوق البنفسجية الشديدة في ظهيرة الصيف", 
        "source": "Tropical & Desert UV Radiation Monitoring", 
        "classes": {
          "3": [
            "#229954", 
            "#EA7545", 
            "#512E5F"
          ], 
          "4": [
            "#229954", 
            "#EFAB4A", 
            "#D04863", 
            "#512E5F"
          ], 
          "5": [
            "#229954", 
            "#F2C244", 
            "#EA7545", 
            "#AB4591", 
            "#512E5F"
          ], 
          "6": [
            "#229954", 
            "#F4D03F", 
            "#EB984E", 
            "#E74C3C", 
            "#8E44AD", 
            "#512E5F"
          ], 
          "7": [
            "#229954", 
            "#D7C844", 
            "#EFAB4A", 
            "#EA7545", 
            "#D04863", 
            "#83409F", 
            "#512E5F"
          ], 
          "8": [
            "#229954", 
            "#C2C147", 
            "#F1B847", 
            "#EB8E4B", 
            "#E8593E", 
            "#BC467E", 
            "#7C3E96", 
            "#512E5F"
          ], 
          "9": [
            "#229954", 
            "#B2BD4A", 
            "#F2C244", 
            "#EC9F4D", 
            "#EA7545", 
            "#DF4A4B", 
            "#AB4591", 
            "#773C8F", 
            "#512E5F"
          ], 
          "10": [
            "#229954", 
            "#A6B94B", 
            "#F3CA41", 
            "#EFAB4A", 
            "#EB894A", 
            "#E96040", 
            "#D04863", 
            "#9C44A1", 
            "#723A89", 
            "#512E5F"
          ], 
          "11": [
            "#229954", 
            "#9BB64C", 
            "#F4D03F", 
            "#F0B448", 
            "#EB984E", 
            "#EA7545", 
            "#E74C3C", 
            "#C24676", 
            "#8E44AD", 
            "#6F3985", 
            "#512E5F"
          ]
        }, 
        "name_en": "Tropical Summer Noon Peak UV", 
        "id": "UV_SummerPeak"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس فيتزباتريك لتحمل الجلد وسرعة حروق الشمس", 
        "source": "Harvard Medical School / Fitzpatrick Phototypes", 
        "classes": {
          "3": [
            "#FAD8C3", 
            "#BA774B", 
            "#452514"
          ], 
          "4": [
            "#FAD8C3", 
            "#D5976F", 
            "#8F5532", 
            "#452514"
          ], 
          "5": [
            "#FAD8C3", 
            "#E3A882", 
            "#BA774B", 
            "#7A4526", 
            "#452514"
          ], 
          "6": [
            "#FAD8C3", 
            "#E8B18F", 
            "#CB8A61", 
            "#A0623C", 
            "#6F3E22", 
            "#452514"
          ], 
          "7": [
            "#FAD8C3", 
            "#EBB897", 
            "#D5976F", 
            "#BA774B", 
            "#8F5532", 
            "#683A20", 
            "#452514"
          ], 
          "8": [
            "#FAD8C3", 
            "#EDBC9D", 
            "#DDA17A", 
            "#C6855A", 
            "#A76840", 
            "#834C2B", 
            "#63371E", 
            "#452514"
          ], 
          "9": [
            "#FAD8C3", 
            "#EFC0A2", 
            "#E3A882", 
            "#CF8F66", 
            "#BA774B", 
            "#995D38", 
            "#7A4526", 
            "#5F351D", 
            "#452514"
          ], 
          "10": [
            "#FAD8C3", 
            "#F0C2A6", 
            "#E6AD89", 
            "#D5976F", 
            "#C38257", 
            "#AB6C42", 
            "#8F5532", 
            "#744124", 
            "#5C331C", 
            "#452514"
          ], 
          "11": [
            "#FAD8C3", 
            "#F1C5A9", 
            "#E8B18F", 
            "#DB9E77", 
            "#CB8A61", 
            "#BA774B", 
            "#A0623C", 
            "#864F2D", 
            "#6F3E22", 
            "#5A311B", 
            "#452514"
          ]
        }, 
        "name_en": "Fitzpatrick Skin Phototypes", 
        "id": "UV_Multi_Fitzpatrick"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "مؤشر الأشعة فوق البنفسجية في المرتفعات والجبال", 
        "source": "Alpine Solar Radiation Amplification Studies", 
        "classes": {
          "3": [
            "#289500", 
            "#D80010", 
            "#1F0445"
          ], 
          "4": [
            "#289500", 
            "#F85900", 
            "#6B49C8", 
            "#1F0445"
          ], 
          "5": [
            "#289500", 
            "#FCA400", 
            "#D80010", 
            "#5330A1", 
            "#1F0445"
          ], 
          "6": [
            "#289500", 
            "#FACB00", 
            "#EB4108", 
            "#AD367F", 
            "#44228A", 
            "#1F0445"
          ], 
          "7": [
            "#289500", 
            "#F7E400", 
            "#F85900", 
            "#D80010", 
            "#6B49C8", 
            "#3B187B", 
            "#1F0445"
          ], 
          "8": [
            "#289500", 
            "#DCD900", 
            "#FB8600", 
            "#E6350B", 
            "#BD2D61", 
            "#5D3BB1", 
            "#371573", 
            "#1F0445"
          ], 
          "9": [
            "#289500", 
            "#C8D100", 
            "#FCA400", 
            "#F04A06", 
            "#D80010", 
            "#9B3D9A", 
            "#5330A1", 
            "#34136D", 
            "#1F0445"
          ], 
          "10": [
            "#289500", 
            "#B9CA00", 
            "#FBBA00", 
            "#F85900", 
            "#E32D0D", 
            "#C42751", 
            "#6B49C8", 
            "#4B2894", 
            "#311168", 
            "#1F0445"
          ], 
          "11": [
            "#289500", 
            "#ACC500", 
            "#FACB00", 
            "#FA7A00", 
            "#EB4108", 
            "#D80010", 
            "#AD367F", 
            "#613FB8", 
            "#44228A", 
            "#2F0F65", 
            "#1F0445"
          ]
        }, 
        "name_en": "High-Altitude Alpine UV", 
        "id": "UV_Multi_HighAltitude"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "النطاق الشمسي الحيوي الآمن لتكوين فيتامين د", 
        "source": "Photobiology & Endocrine Society Guidelines", 
        "classes": {
          "3": [
            "#B2E2E2", 
            "#4CB281", 
            "#006D2C"
          ], 
          "4": [
            "#B2E2E2", 
            "#66C2A4", 
            "#2CA25F", 
            "#006D2C"
          ], 
          "5": [
            "#B2E2E2", 
            "#7ACAB3", 
            "#4CB281", 
            "#239452", 
            "#006D2C"
          ], 
          "6": [
            "#B2E2E2", 
            "#86CFBC", 
            "#5CBC96", 
            "#3AA86D", 
            "#1D8C4A", 
            "#006D2C"
          ], 
          "7": [
            "#B2E2E2", 
            "#8DD2C3", 
            "#66C2A4", 
            "#4CB281", 
            "#2CA25F", 
            "#198745", 
            "#006D2C"
          ], 
          "8": [
            "#B2E2E2", 
            "#93D4C7", 
            "#72C7AD", 
            "#58B990", 
            "#40AB73", 
            "#279A58", 
            "#168341", 
            "#006D2C"
          ], 
          "9": [
            "#B2E2E2", 
            "#97D6CA", 
            "#7ACAB3", 
            "#60BE9B", 
            "#4CB281", 
            "#35A668", 
            "#239452", 
            "#14803F", 
            "#006D2C"
          ], 
          "10": [
            "#B2E2E2", 
            "#9AD7CD", 
            "#81CDB8", 
            "#66C2A4", 
            "#55B78D", 
            "#43AD76", 
            "#2CA25F", 
            "#20904E", 
            "#127E3D", 
            "#006D2C"
          ], 
          "11": [
            "#B2E2E2", 
            "#9CD9CF", 
            "#86CFBC", 
            "#6EC5AA", 
            "#5CBC96", 
            "#4CB281", 
            "#3AA86D", 
            "#289D5A", 
            "#1D8C4A", 
            "#107D3B", 
            "#006D2C"
          ]
        }, 
        "name_en": "Vitamin D Optimal Synthesis", 
        "id": "UV_Seq_VitaminDSynthesis"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "شذوذ الأشعة الناتج عن ترقق طبقة الأوزون", 
        "source": "WMO/UNEP Scientific Assessment of Ozone Depletion", 
        "classes": {
          "3": [
            "#74ADD1", 
            "#FFFFBF", 
            "#F46D43"
          ], 
          "4": [
            "#4575B4", 
            "#ABD9E9", 
            "#FDAE61", 
            "#D73027"
          ], 
          "5": [
            "#4575B4", 
            "#ABD9E9", 
            "#FFFFBF", 
            "#FDAE61", 
            "#D73027"
          ], 
          "6": [
            "#4575B4", 
            "#74ADD1", 
            "#ABD9E9", 
            "#FDAE61", 
            "#F46D43", 
            "#D73027"
          ], 
          "7": [
            "#4575B4", 
            "#74ADD1", 
            "#ABD9E9", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F46D43", 
            "#D73027"
          ], 
          "8": [
            "#4575B4", 
            "#659AC7", 
            "#87BBD9", 
            "#ABD9E9", 
            "#FDAE61", 
            "#F8844D", 
            "#EB5B39", 
            "#D73027"
          ], 
          "9": [
            "#4575B4", 
            "#659AC7", 
            "#87BBD9", 
            "#ABD9E9", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F8844D", 
            "#EB5B39", 
            "#D73027"
          ], 
          "10": [
            "#4575B4", 
            "#5E91C3", 
            "#74ADD1", 
            "#90C3DD", 
            "#ABD9E9", 
            "#FDAE61", 
            "#F98F52", 
            "#F46D43", 
            "#E65135", 
            "#D73027"
          ], 
          "11": [
            "#4575B4", 
            "#5E91C3", 
            "#74ADD1", 
            "#90C3DD", 
            "#ABD9E9", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F98F52", 
            "#F46D43", 
            "#E65135", 
            "#D73027"
          ]
        }, 
        "name_en": "Stratospheric Ozone UV Anomaly", 
        "id": "UV_Div_OzoneDepletion"
      }
    ], 
    "folder": "08_UV_Index", 
    "name_en": "UV Index"
  }, 
  {
    "name_ar": "الغطاء السحابي ونقاء السماء", 
    "styles": [
      {
        "category": "Multi-Hue", 
        "name_ar": "مقياس الأوكتا العالمي للسحب (من 0 إلى 8 أوكتا)", 
        "source": "WMO International Cloud Atlas (Okta Scale)", 
        "classes": {
          "3": [
            "#A8D4F5", 
            "#2980B9", 
            "#17202A"
          ], 
          "4": [
            "#A8D4F5", 
            "#5499C7", 
            "#2471A3", 
            "#17202A"
          ], 
          "5": [
            "#A8D4F5", 
            "#6AA6CE", 
            "#2980B9", 
            "#20608A", 
            "#17202A"
          ], 
          "6": [
            "#A8D4F5", 
            "#77AED2", 
            "#458FC1", 
            "#2677AC", 
            "#1D567C", 
            "#17202A"
          ], 
          "7": [
            "#A8D4F5", 
            "#7FB3D5", 
            "#5499C7", 
            "#2980B9", 
            "#2471A3", 
            "#1B4F72", 
            "#17202A"
          ], 
          "8": [
            "#A8D4F5", 
            "#85B8DA", 
            "#61A0CB", 
            "#3E8BBF", 
            "#277AB0", 
            "#216795", 
            "#1C4867", 
            "#17202A"
          ], 
          "9": [
            "#A8D4F5", 
            "#89BBDD", 
            "#6AA6CE", 
            "#4B93C4", 
            "#2980B9", 
            "#2575A8", 
            "#20608A", 
            "#1C435F", 
            "#17202A"
          ], 
          "10": [
            "#A8D4F5", 
            "#8DBEE0", 
            "#71AAD0", 
            "#5499C7", 
            "#3A88BE", 
            "#277BB2", 
            "#2471A3", 
            "#1E5A82", 
            "#1D3F59", 
            "#17202A"
          ], 
          "11": [
            "#A8D4F5", 
            "#8FC0E2", 
            "#77AED2", 
            "#5D9ECA", 
            "#458FC1", 
            "#2980B9", 
            "#2677AC", 
            "#226A99", 
            "#1D567C", 
            "#1C3B54", 
            "#17202A"
          ]
        }, 
        "name_en": "WMO Okta Cloud Scale", 
        "id": "Cloud_Seq_Okta"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "نسبة الغطاء السحابي الكلي المئوية (0% - 100%)", 
        "source": "MODIS / EUMETSAT Cloud Fraction", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#4292C6", 
            "#08306B"
          ], 
          "4": [
            "#BDD7E7", 
            "#6BAED6", 
            "#2171B5", 
            "#08306B"
          ], 
          "5": [
            "#BDD7E7", 
            "#86BCDC", 
            "#4292C6", 
            "#1761A8", 
            "#08306B"
          ], 
          "6": [
            "#BDD7E7", 
            "#94C4DF", 
            "#5CA3D0", 
            "#307EBC", 
            "#0F57A1", 
            "#08306B"
          ], 
          "7": [
            "#BDD7E7", 
            "#9ECAE1", 
            "#6BAED6", 
            "#4292C6", 
            "#2171B5", 
            "#08519C", 
            "#08306B"
          ], 
          "8": [
            "#BDD7E7", 
            "#A3CCE2", 
            "#7BB6D9", 
            "#559ECD", 
            "#3684BF", 
            "#1C68AE", 
            "#084C95", 
            "#08306B"
          ], 
          "9": [
            "#BDD7E7", 
            "#A6CDE3", 
            "#86BCDC", 
            "#62A7D2", 
            "#4292C6", 
            "#2B79B9", 
            "#1761A8", 
            "#09498F", 
            "#08306B"
          ], 
          "10": [
            "#BDD7E7", 
            "#A9CEE3", 
            "#8EC1DD", 
            "#6BAED6", 
            "#519BCB", 
            "#3987C0", 
            "#2171B5", 
            "#135BA4", 
            "#09468B", 
            "#08306B"
          ], 
          "11": [
            "#BDD7E7", 
            "#ABCFE3", 
            "#94C4DF", 
            "#76B4D8", 
            "#5CA3D0", 
            "#4292C6", 
            "#307EBC", 
            "#1D6AB0", 
            "#0F57A1", 
            "#094388", 
            "#08306B"
          ]
        }, 
        "name_en": "Total Cloud Fraction %", 
        "id": "Cloud_Seq_Fraction"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "درجات حرارة قمم السحب بالأشعة تحت الحمراء", 
        "source": "NOAA GOES-R Advanced Baseline Imager (ABI)", 
        "classes": {
          "3": [
            "#B0D0E8", 
            "#0000FF", 
            "#FF0000"
          ], 
          "4": [
            "#B0D0E8", 
            "#444444", 
            "#00FF00", 
            "#FF0000"
          ], 
          "5": [
            "#B0D0E8", 
            "#656565", 
            "#0000FF", 
            "#AEFF00", 
            "#FF0000"
          ], 
          "6": [
            "#B0D0E8", 
            "#7A7A7A", 
            "#50378B", 
            "#7CA993", 
            "#E1FF00", 
            "#FF0000"
          ], 
          "7": [
            "#B0D0E8", 
            "#888888", 
            "#444444", 
            "#0000FF", 
            "#00FF00", 
            "#FFFF00", 
            "#FF0000"
          ], 
          "8": [
            "#B0D0E8", 
            "#8E9295", 
            "#575757", 
            "#4D2FAB", 
            "#7C84B3", 
            "#82FF00", 
            "#FFE500", 
            "#FF0000"
          ], 
          "9": [
            "#B0D0E8", 
            "#92999F", 
            "#656565", 
            "#4E3D70", 
            "#0000FF", 
            "#6FC972", 
            "#AEFF00", 
            "#FFD100", 
            "#FF0000"
          ], 
          "10": [
            "#B0D0E8", 
            "#969FA7", 
            "#707070", 
            "#444444", 
            "#4929BD", 
            "#766EC5", 
            "#00FF00", 
            "#CBFF00", 
            "#FFC200", 
            "#FF0000"
          ], 
          "11": [
            "#B0D0E8", 
            "#99A4AD", 
            "#7A7A7A", 
            "#515151", 
            "#50378B", 
            "#0000FF", 
            "#7CA993", 
            "#6DFF00", 
            "#E1FF00", 
            "#FFB500", 
            "#FF0000"
          ]
        }, 
        "name_en": "Satellite IR Cloud Top Temp", 
        "id": "Cloud_Multi_IR_CloudTop"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "السمك البصري للغيوم وكثافة حجب الضوء", 
        "source": "NASA MODIS Cloud Optical Properties", 
        "classes": {
          "3": [
            "#CCEBC5", 
            "#4EB3D3", 
            "#084081"
          ], 
          "4": [
            "#CCEBC5", 
            "#7BCCC4", 
            "#2B8CBE", 
            "#084081"
          ], 
          "5": [
            "#CCEBC5", 
            "#93D4BD", 
            "#4EB3D3", 
            "#1E7AB5", 
            "#084081"
          ], 
          "6": [
            "#CCEBC5", 
            "#A0DAB8", 
            "#6CC2CA", 
            "#3B9BC6", 
            "#136FB0", 
            "#084081"
          ], 
          "7": [
            "#CCEBC5", 
            "#A8DDB5", 
            "#7BCCC4", 
            "#4EB3D3", 
            "#2B8CBE", 
            "#0868AC", 
            "#084081"
          ], 
          "8": [
            "#CCEBC5", 
            "#ADDFB7", 
            "#89D1C0", 
            "#64BECD", 
            "#40A2CA", 
            "#2482B9", 
            "#0962A6", 
            "#084081"
          ], 
          "9": [
            "#CCEBC5", 
            "#B1E1B9", 
            "#93D4BD", 
            "#72C6C8", 
            "#4EB3D3", 
            "#3596C3", 
            "#1E7AB5", 
            "#095EA1", 
            "#084081"
          ], 
          "10": [
            "#CCEBC5", 
            "#B4E2BA", 
            "#9AD7BA", 
            "#7BCCC4", 
            "#60BBCE", 
            "#44A6CC", 
            "#2B8CBE", 
            "#1974B2", 
            "#095A9D", 
            "#084081"
          ], 
          "11": [
            "#CCEBC5", 
            "#B7E3BB", 
            "#A0DAB8", 
            "#85CFC1", 
            "#6CC2CA", 
            "#4EB3D3", 
            "#3B9BC6", 
            "#2685BA", 
            "#136FB0", 
            "#0A589B", 
            "#084081"
          ]
        }, 
        "name_en": "Cloud Optical Thickness Tau", 
        "id": "Cloud_Seq_OpticalDepth"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "السحب المنخفضة وحزام الضباب ومخاطر الرؤية", 
        "source": "Aviation Weather Center Ceiling & Fog Hazard", 
        "classes": {
          "3": [
            "#C5CBD0", 
            "#8E99A2", 
            "#566573"
          ], 
          "4": [
            "#C5CBD0", 
            "#A1AAB1", 
            "#849094", 
            "#566573"
          ], 
          "5": [
            "#C5CBD0", 
            "#ABB2B9", 
            "#8E99A2", 
            "#7F8C8D", 
            "#566573"
          ], 
          "6": [
            "#C5CBD0", 
            "#B0B7BE", 
            "#9AA3AB", 
            "#88949A", 
            "#778488", 
            "#566573"
          ], 
          "7": [
            "#C5CBD0", 
            "#B4BAC1", 
            "#A1AAB1", 
            "#8E99A2", 
            "#849094", 
            "#717F84", 
            "#566573"
          ], 
          "8": [
            "#C5CBD0", 
            "#B6BDC3", 
            "#A7AEB6", 
            "#96A0A9", 
            "#8A959C", 
            "#818E90", 
            "#6D7B82", 
            "#566573"
          ], 
          "9": [
            "#C5CBD0", 
            "#B8BEC4", 
            "#ABB2B9", 
            "#9CA5AD", 
            "#8E99A2", 
            "#869297", 
            "#7F8C8D", 
            "#6A7880", 
            "#566573"
          ], 
          "10": [
            "#C5CBD0", 
            "#B9C0C6", 
            "#AEB5BC", 
            "#A1AAB1", 
            "#949EA7", 
            "#8B969D", 
            "#849094", 
            "#7A888A", 
            "#68767E", 
            "#566573"
          ], 
          "11": [
            "#C5CBD0", 
            "#BBC1C7", 
            "#B0B7BE", 
            "#A5ADB4", 
            "#9AA3AB", 
            "#8E99A2", 
            "#88949A", 
            "#828F91", 
            "#778488", 
            "#66747D", 
            "#566573"
          ]
        }, 
        "name_en": "Low Stratus & Fog Ceiling", 
        "id": "Cloud_Seq_LowCloudFog"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "القمم الركامية المخترقة وعواصف البرد الشديدة", 
        "source": "NASA Convective Storm Research", 
        "classes": {
          "3": [
            "#000080", 
            "#FFFF00", 
            "#4A004A"
          ], 
          "4": [
            "#000080", 
            "#4FE97C", 
            "#FF6500", 
            "#4A004A"
          ], 
          "5": [
            "#000080", 
            "#00BFFF", 
            "#FFFF00", 
            "#FF0000", 
            "#4A004A"
          ], 
          "6": [
            "#000080", 
            "#3D82FF", 
            "#6DFF00", 
            "#FF9B00", 
            "#D10042", 
            "#4A004A"
          ], 
          "7": [
            "#000080", 
            "#3858FF", 
            "#4FE97C", 
            "#FFFF00", 
            "#FF6500", 
            "#B1005E", 
            "#4A004A"
          ], 
          "8": [
            "#000080", 
            "#2734FF", 
            "#4ED1C9", 
            "#A0FF00", 
            "#FFB800", 
            "#FF4000", 
            "#960071", 
            "#4A004A"
          ], 
          "9": [
            "#000080", 
            "#0000FF", 
            "#00BFFF", 
            "#00FF00", 
            "#FFFF00", 
            "#FF7F00", 
            "#FF0000", 
            "#800080", 
            "#4A004A"
          ], 
          "10": [
            "#000080", 
            "#0000F0", 
            "#349EFF", 
            "#4FE97C", 
            "#B8FF00", 
            "#FFC800", 
            "#FF6500", 
            "#E6002D", 
            "#7A007A", 
            "#4A004A"
          ], 
          "11": [
            "#000080", 
            "#0000E4", 
            "#3D82FF", 
            "#54D8B3", 
            "#6DFF00", 
            "#FFFF00", 
            "#FF9B00", 
            "#FF4D00", 
            "#D10042", 
            "#750075", 
            "#4A004A"
          ]
        }, 
        "name_en": "Overshooting Tops & Hailstorms", 
        "id": "Cloud_Multi_ConvectiveTops"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "عمق الهباء الجوي البصري والعواصف الترابية الصحراوية", 
        "source": "NASA AERONET / MODIS Aerosol Optical Depth", 
        "classes": {
          "3": [
            "#313695", 
            "#FFD78F", 
            "#8C510A"
          ], 
          "4": [
            "#313695", 
            "#CAE5DC", 
            "#F8844D", 
            "#8C510A"
          ], 
          "5": [
            "#313695", 
            "#93BFDC", 
            "#FFD78F", 
            "#ED5F3C", 
            "#8C510A"
          ], 
          "6": [
            "#313695", 
            "#719CC9", 
            "#F0F7C8", 
            "#FCA25B", 
            "#E34B32", 
            "#8C510A"
          ], 
          "7": [
            "#313695", 
            "#5885BD", 
            "#CAE5DC", 
            "#FFD78F", 
            "#F8844D", 
            "#DC3C2B", 
            "#8C510A"
          ], 
          "8": [
            "#313695", 
            "#4575B4", 
            "#ABD9E9", 
            "#FFFFBF", 
            "#FDAE61", 
            "#F46D43", 
            "#D73027", 
            "#8C510A"
          ], 
          "9": [
            "#313695", 
            "#436DB0", 
            "#93BFDC", 
            "#E2F0CF", 
            "#FFD78F", 
            "#FA9755", 
            "#ED5F3C", 
            "#CE3824", 
            "#8C510A"
          ], 
          "10": [
            "#313695", 
            "#4267AD", 
            "#80ABD1", 
            "#CAE5DC", 
            "#FFF6B4", 
            "#FEB76B", 
            "#F8844D", 
            "#E75436", 
            "#C63C21", 
            "#8C510A"
          ], 
          "11": [
            "#313695", 
            "#4162AB", 
            "#719CC9", 
            "#B5DDE5", 
            "#F0F7C8", 
            "#FFD78F", 
            "#FCA25B", 
            "#F57446", 
            "#E34B32", 
            "#C0401F", 
            "#8C510A"
          ]
        }, 
        "name_en": "Aerosol Optical Depth 550nm", 
        "id": "Cloud_Multi_AOD_Aerosol"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "سحب السمحاق العالية ومسار الجليد السحابي", 
        "source": "Cirrus Cloud Radiation & Cryosphere Climatology", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#4C8FC6", 
            "#08306B"
          ], 
          "4": [
            "#BDD7E7", 
            "#6BAED6", 
            "#2171B5", 
            "#08306B"
          ], 
          "5": [
            "#BDD7E7", 
            "#82B8DA", 
            "#4C8FC6", 
            "#1C60A2", 
            "#08306B"
          ], 
          "6": [
            "#BDD7E7", 
            "#8EBEDD", 
            "#5FA1CF", 
            "#357DBC", 
            "#185697", 
            "#08306B"
          ], 
          "7": [
            "#BDD7E7", 
            "#96C2DF", 
            "#6BAED6", 
            "#4C8FC6", 
            "#2171B5", 
            "#164F8F", 
            "#08306B"
          ], 
          "8": [
            "#BDD7E7", 
            "#9CC5E0", 
            "#78B4D8", 
            "#5A9CCD", 
            "#3C82BE", 
            "#1E67AA", 
            "#144B8A", 
            "#08306B"
          ], 
          "9": [
            "#BDD7E7", 
            "#A0C7E1", 
            "#82B8DA", 
            "#64A6D2", 
            "#4C8FC6", 
            "#2E78B9", 
            "#1C60A2", 
            "#134786", 
            "#08306B"
          ], 
          "10": [
            "#BDD7E7", 
            "#A4C9E1", 
            "#89BBDC", 
            "#6BAED6", 
            "#5799CB", 
            "#4085C0", 
            "#2171B5", 
            "#1A5A9C", 
            "#124583", 
            "#08306B"
          ], 
          "11": [
            "#BDD7E7", 
            "#A6CBE2", 
            "#8EBEDD", 
            "#74B2D8", 
            "#5FA1CF", 
            "#4C8FC6", 
            "#357DBC", 
            "#1F6AAD", 
            "#185697", 
            "#114380", 
            "#08306B"
          ]
        }, 
        "name_en": "High Cirrus Ice Water Path", 
        "id": "Cloud_Seq_CirrusIce"
      }
    ], 
    "folder": "09_Cloud_Cover", 
    "name_en": "Cloud Cover"
  }, 
  {
    "name_ar": "مؤشرات الجفاف والقحولة", 
    "styles": [
      {
        "category": "Multi-Hue", 
        "name_ar": "مؤشر القحولة العالمي المعتمد لأطلس التصحر", 
        "source": "UNEP World Atlas of Desertification (AI = P/PET)", 
        "classes": {
          "3": [
            "#D73027", 
            "#ECF7A5", 
            "#006837"
          ], 
          "4": [
            "#D73027", 
            "#FEE08B", 
            "#A6D96A", 
            "#006837"
          ], 
          "5": [
            "#D73027", 
            "#FEBB6B", 
            "#ECF7A5", 
            "#77C465", 
            "#006837"
          ], 
          "6": [
            "#D73027", 
            "#FCA25B", 
            "#FFF3AA", 
            "#C5E67E", 
            "#5AB65F", 
            "#006837"
          ], 
          "7": [
            "#D73027", 
            "#F98F52", 
            "#FEE08B", 
            "#ECF7A5", 
            "#A6D96A", 
            "#46AA59", 
            "#006837"
          ], 
          "8": [
            "#D73027", 
            "#F7814B", 
            "#FECB79", 
            "#FFFBB8", 
            "#D2EC86", 
            "#8CCD67", 
            "#36A255", 
            "#006837"
          ], 
          "9": [
            "#D73027", 
            "#F57647", 
            "#FEBB6B", 
            "#FFEC9E", 
            "#ECF7A5", 
            "#B9E176", 
            "#77C465", 
            "#289D52", 
            "#006837"
          ], 
          "10": [
            "#D73027", 
            "#F46D43", 
            "#FDAE61", 
            "#FEE08B", 
            "#FFFFBF", 
            "#D9EF8B", 
            "#A6D96A", 
            "#66BD63", 
            "#1A9850", 
            "#006837"
          ], 
          "11": [
            "#D73027", 
            "#F16840", 
            "#FCA25B", 
            "#FED17E", 
            "#FFF3AA", 
            "#ECF7A5", 
            "#C5E67E", 
            "#94D168", 
            "#5AB65F", 
            "#18934D", 
            "#006837"
          ]
        }, 
        "name_en": "UNEP World Aridity Index", 
        "id": "Aridity_UNEP_World"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر الجفاف والتبخر المعياري المتعدد", 
        "source": "Global SPEI Drought Monitor (Vicente-Serrano)", 
        "classes": {
          "3": [
            "#D6604D", 
            "#FFFFBF", 
            "#2166AC"
          ], 
          "4": [
            "#67001F", 
            "#F4A582", 
            "#92C5DE", 
            "#053061"
          ], 
          "5": [
            "#67001F", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#053061"
          ], 
          "6": [
            "#67001F", 
            "#C4413C", 
            "#F4A582", 
            "#92C5DE", 
            "#347CB8", 
            "#053061"
          ], 
          "7": [
            "#67001F", 
            "#C4413C", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#347CB8", 
            "#053061"
          ], 
          "8": [
            "#67001F", 
            "#B2182B", 
            "#D6604D", 
            "#F4A582", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061"
          ], 
          "9": [
            "#67001F", 
            "#B2182B", 
            "#D6604D", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#4393C3", 
            "#2166AC", 
            "#053061"
          ], 
          "10": [
            "#67001F", 
            "#9F1128", 
            "#C4413C", 
            "#DE725A", 
            "#F4A582", 
            "#92C5DE", 
            "#5A9FCA", 
            "#347CB8", 
            "#1A5899", 
            "#053061"
          ], 
          "11": [
            "#67001F", 
            "#9F1128", 
            "#C4413C", 
            "#DE725A", 
            "#F4A582", 
            "#FFFFBF", 
            "#92C5DE", 
            "#5A9FCA", 
            "#347CB8", 
            "#1A5899", 
            "#053061"
          ]
        }, 
        "name_en": "SPEI Drought Severity", 
        "id": "Drought_SPEI_Index"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر بالمر الهيدرولوجي والزراعي لشدة الجفاف", 
        "source": "NOAA National Centers for Environmental Information", 
        "classes": {
          "3": [
            "#E66101", 
            "#FFFFBF", 
            "#542788"
          ], 
          "4": [
            "#730000", 
            "#FDB863", 
            "#B2ABD2", 
            "#2D004B"
          ], 
          "5": [
            "#730000", 
            "#FDB863", 
            "#FFFFBF", 
            "#B2ABD2", 
            "#2D004B"
          ], 
          "6": [
            "#730000", 
            "#D64310", 
            "#FDB863", 
            "#B2ABD2", 
            "#6B4E9A", 
            "#2D004B"
          ], 
          "7": [
            "#730000", 
            "#D64310", 
            "#FDB863", 
            "#FFFFBF", 
            "#B2ABD2", 
            "#6B4E9A", 
            "#2D004B"
          ], 
          "8": [
            "#730000", 
            "#C51B17", 
            "#E66101", 
            "#FDB863", 
            "#B2ABD2", 
            "#8073AC", 
            "#542788", 
            "#2D004B"
          ], 
          "9": [
            "#730000", 
            "#C51B17", 
            "#E66101", 
            "#FDB863", 
            "#FFFFBF", 
            "#B2ABD2", 
            "#8073AC", 
            "#542788", 
            "#2D004B"
          ], 
          "10": [
            "#730000", 
            "#B01412", 
            "#D64310", 
            "#ED7822", 
            "#FDB863", 
            "#B2ABD2", 
            "#8C81B5", 
            "#6B4E9A", 
            "#4A1D78", 
            "#2D004B"
          ], 
          "11": [
            "#730000", 
            "#B01412", 
            "#D64310", 
            "#ED7822", 
            "#FDB863", 
            "#FFFFBF", 
            "#B2ABD2", 
            "#8C81B5", 
            "#6B4E9A", 
            "#4A1D78", 
            "#2D004B"
          ]
        }, 
        "name_en": "Palmer Drought Severity PDSI", 
        "id": "Drought_PDSI_Palmer"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "مؤشر استنزاف وعجز رطوبة التربة الجذرية", 
        "source": "European Drought Observatory (EDO / Copernicus)", 
        "classes": {
          "3": [
            "#543005", 
            "#E0E9D4", 
            "#003C30"
          ], 
          "4": [
            "#543005", 
            "#DFC27D", 
            "#80CDC1", 
            "#003C30"
          ], 
          "5": [
            "#543005", 
            "#C89142", 
            "#E0E9D4", 
            "#4AA49B", 
            "#003C30"
          ], 
          "6": [
            "#543005", 
            "#B57726", 
            "#EDD9A7", 
            "#ABDED6", 
            "#2C8D85", 
            "#003C30"
          ], 
          "7": [
            "#543005", 
            "#A5691C", 
            "#DFC27D", 
            "#E0E9D4", 
            "#80CDC1", 
            "#1F7E76", 
            "#003C30"
          ], 
          "8": [
            "#543005", 
            "#9A5E15", 
            "#D2A65B", 
            "#F3E2B9", 
            "#BDE6E0", 
            "#62B6AB", 
            "#14746C", 
            "#003C30"
          ], 
          "9": [
            "#543005", 
            "#92570F", 
            "#C89142", 
            "#E8D097", 
            "#E0E9D4", 
            "#9CD8CE", 
            "#4AA49B", 
            "#0A6C64", 
            "#003C30"
          ], 
          "10": [
            "#543005", 
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#F6E8C3", 
            "#C7EAE5", 
            "#80CDC1", 
            "#35978F", 
            "#01665E", 
            "#003C30"
          ], 
          "11": [
            "#543005", 
            "#864E0A", 
            "#B57726", 
            "#D6AE65", 
            "#EDD9A7", 
            "#E0E9D4", 
            "#ABDED6", 
            "#6BBDB2", 
            "#2C8D85", 
            "#016259", 
            "#003C30"
          ]
        }, 
        "name_en": "Soil Moisture Depletion", 
        "id": "Aridity_SoilMoistureDeficit"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "معدل البخر-نتح المرجعي بهارجريفز (ملم/يوم)", 
        "source": "FAO-56 Irrigation and Drainage Guidelines", 
        "classes": {
          "3": [
            "#FFFFB2", 
            "#F7692D", 
            "#7A0000"
          ], 
          "4": [
            "#FFFFB2", 
            "#FEA346", 
            "#DF2C23", 
            "#7A0000"
          ], 
          "5": [
            "#FFFFB2", 
            "#FFBD54", 
            "#F7692D", 
            "#CA1625", 
            "#7A0000"
          ], 
          "6": [
            "#FFFFB2", 
            "#FECC5C", 
            "#FD8D3C", 
            "#F03B20", 
            "#BD0026", 
            "#7A0000"
          ], 
          "7": [
            "#FFFFB2", 
            "#FFD46B", 
            "#FEA346", 
            "#F7692D", 
            "#DF2C23", 
            "#B10020", 
            "#7A0000"
          ], 
          "8": [
            "#FFFFB2", 
            "#FFDA75", 
            "#FFB24E", 
            "#FC8338", 
            "#F24A24", 
            "#D32124", 
            "#A9001C", 
            "#7A0000"
          ], 
          "9": [
            "#FFFFB2", 
            "#FFDF7D", 
            "#FFBD54", 
            "#FE9540", 
            "#F7692D", 
            "#EA3621", 
            "#CA1625", 
            "#A30019", 
            "#7A0000"
          ], 
          "10": [
            "#FFFFB2", 
            "#FFE383", 
            "#FEC558", 
            "#FEA346", 
            "#FB7D35", 
            "#F35126", 
            "#DF2C23", 
            "#C30B26", 
            "#9F0017", 
            "#7A0000"
          ], 
          "11": [
            "#FFFFB2", 
            "#FFE587", 
            "#FECC5C", 
            "#FFAD4C", 
            "#FD8D3C", 
            "#F7692D", 
            "#F03B20", 
            "#D62424", 
            "#BD0026", 
            "#9B0015", 
            "#7A0000"
          ]
        }, 
        "name_en": "Reference Evapotranspiration", 
        "id": "Drought_ETo_Hargreaves"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر الطلب التبخري لرصد الجفاف الوميضي السريع", 
        "source": "NOAA Physical Sciences Laboratory (EDDI)", 
        "classes": {
          "3": [
            "#35978F", 
            "#F6E8C3", 
            "#8C510A"
          ], 
          "4": [
            "#01665E", 
            "#80CDC1", 
            "#DFC27D", 
            "#543005"
          ], 
          "5": [
            "#01665E", 
            "#80CDC1", 
            "#F6E8C3", 
            "#DFC27D", 
            "#543005"
          ], 
          "6": [
            "#01665E", 
            "#35978F", 
            "#80CDC1", 
            "#DFC27D", 
            "#A5691C", 
            "#543005"
          ], 
          "7": [
            "#01665E", 
            "#35978F", 
            "#80CDC1", 
            "#F6E8C3", 
            "#DFC27D", 
            "#A5691C", 
            "#543005"
          ], 
          "8": [
            "#01665E", 
            "#27867E", 
            "#50A99F", 
            "#80CDC1", 
            "#DFC27D", 
            "#BF812D", 
            "#8C510A", 
            "#543005"
          ], 
          "9": [
            "#01665E", 
            "#27867E", 
            "#50A99F", 
            "#80CDC1", 
            "#F6E8C3", 
            "#DFC27D", 
            "#BF812D", 
            "#8C510A", 
            "#543005"
          ], 
          "10": [
            "#01665E", 
            "#1F7E76", 
            "#35978F", 
            "#5CB2A8", 
            "#80CDC1", 
            "#DFC27D", 
            "#C89142", 
            "#A5691C", 
            "#7E4809", 
            "#543005"
          ], 
          "11": [
            "#01665E", 
            "#1F7E76", 
            "#35978F", 
            "#5CB2A8", 
            "#80CDC1", 
            "#F6E8C3", 
            "#DFC27D", 
            "#C89142", 
            "#A5691C", 
            "#7E4809", 
            "#543005"
          ]
        }, 
        "name_en": "Evaporative Demand Drought EDDI", 
        "id": "Drought_EDDI_Evaporative"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر رطوبة المحاصيل الزراعية الأسبوعي", 
        "source": "USDA / NOAA Joint Agricultural Weather Facility", 
        "classes": {
          "3": [
            "#BF812D", 
            "#F6E8C3", 
            "#80CDC1"
          ], 
          "4": [
            "#8C510A", 
            "#DFC27D", 
            "#C7EAE5", 
            "#01665E"
          ], 
          "5": [
            "#8C510A", 
            "#DFC27D", 
            "#F6E8C3", 
            "#C7EAE5", 
            "#01665E"
          ], 
          "6": [
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#C7EAE5", 
            "#80CDC1", 
            "#01665E"
          ], 
          "7": [
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#F6E8C3", 
            "#C7EAE5", 
            "#80CDC1", 
            "#01665E"
          ], 
          "8": [
            "#8C510A", 
            "#AE7122", 
            "#CB9648", 
            "#DFC27D", 
            "#C7EAE5", 
            "#99D7CD", 
            "#5BA99F", 
            "#01665E"
          ], 
          "9": [
            "#8C510A", 
            "#AE7122", 
            "#CB9648", 
            "#DFC27D", 
            "#F6E8C3", 
            "#C7EAE5", 
            "#99D7CD", 
            "#5BA99F", 
            "#01665E"
          ], 
          "10": [
            "#8C510A", 
            "#A5691C", 
            "#BF812D", 
            "#D0A155", 
            "#DFC27D", 
            "#C7EAE5", 
            "#A4DCD3", 
            "#80CDC1", 
            "#49988E", 
            "#01665E"
          ], 
          "11": [
            "#8C510A", 
            "#A5691C", 
            "#BF812D", 
            "#D0A155", 
            "#DFC27D", 
            "#F6E8C3", 
            "#C7EAE5", 
            "#A4DCD3", 
            "#80CDC1", 
            "#49988E", 
            "#01665E"
          ]
        }, 
        "name_en": "Crop Moisture Index CMI", 
        "id": "Drought_CMI_CropMoisture"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "عجز البخر-نتح الفعلي عن المرجعي للمحاصيل", 
        "source": "USGS FEWS NET Water Balance Evapotranspiration", 
        "classes": {
          "3": [
            "#FFFFD4", 
            "#EC7C1C", 
            "#542788"
          ], 
          "4": [
            "#FFFFD4", 
            "#FFAF4E", 
            "#C3500A", 
            "#542788"
          ], 
          "5": [
            "#FFFFD4", 
            "#FFC976", 
            "#EC7C1C", 
            "#A93F06", 
            "#542788"
          ], 
          "6": [
            "#FFFFD4", 
            "#FED98E", 
            "#FE9929", 
            "#D95F0E", 
            "#993404", 
            "#542788"
          ], 
          "7": [
            "#FFFFD4", 
            "#FFDF9A", 
            "#FFAF4E", 
            "#EC7C1C", 
            "#C3500A", 
            "#933022", 
            "#542788"
          ], 
          "8": [
            "#FFFFD4", 
            "#FFE4A2", 
            "#FFBE65", 
            "#F99125", 
            "#DE6812", 
            "#B44607", 
            "#8D2E32", 
            "#542788"
          ], 
          "9": [
            "#FFFFD4", 
            "#FFE7A8", 
            "#FFC976", 
            "#FFA138", 
            "#EC7C1C", 
            "#D15A0C", 
            "#A93F06", 
            "#892C3D", 
            "#542788"
          ], 
          "10": [
            "#FFFFD4", 
            "#FFEAAD", 
            "#FFD283", 
            "#FFAF4E", 
            "#F68C23", 
            "#E16C14", 
            "#C3500A", 
            "#A03905", 
            "#852B45", 
            "#542788"
          ], 
          "11": [
            "#FFFFD4", 
            "#FFECB1", 
            "#FED98E", 
            "#FFB95E", 
            "#FE9929", 
            "#EC7C1C", 
            "#D95F0E", 
            "#B94908", 
            "#993404", 
            "#822B4C", 
            "#542788"
          ]
        }, 
        "name_en": "Actual ET Deficit Index", 
        "id": "Drought_ETa_ActualDeficit"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "مؤشر اختلاف المياه المعياري للغطاء النباتي والتربة", 
        "source": "Gao (1996) Remote Sensing Water Index", 
        "classes": {
          "3": [
            "#DFC27D", 
            "#F6E8C3", 
            "#01665E"
          ], 
          "4": [
            "#8C510A", 
            "#DFC27D", 
            "#80CDC1", 
            "#003C30"
          ], 
          "5": [
            "#8C510A", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#003C30"
          ], 
          "6": [
            "#8C510A", 
            "#B78845", 
            "#DFC27D", 
            "#80CDC1", 
            "#01665E", 
            "#003C30"
          ], 
          "7": [
            "#8C510A", 
            "#B78845", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#01665E", 
            "#003C30"
          ], 
          "8": [
            "#8C510A", 
            "#A97532", 
            "#C49B57", 
            "#DFC27D", 
            "#80CDC1", 
            "#36877E", 
            "#01584E", 
            "#003C30"
          ], 
          "9": [
            "#8C510A", 
            "#A97532", 
            "#C49B57", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#36877E", 
            "#01584E", 
            "#003C30"
          ], 
          "10": [
            "#8C510A", 
            "#A26C29", 
            "#B78845", 
            "#CBA560", 
            "#DFC27D", 
            "#80CDC1", 
            "#49988E", 
            "#01665E", 
            "#015146", 
            "#003C30"
          ], 
          "11": [
            "#8C510A", 
            "#A26C29", 
            "#B78845", 
            "#CBA560", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#49988E", 
            "#01665E", 
            "#015146", 
            "#003C30"
          ]
        }, 
        "name_en": "Normalized Difference Water NDWI", 
        "id": "Drought_NDWI_WaterIndex"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "زحف الكثبان الرملية وتدهور أطراف الواحات", 
        "source": "UNCCD Global Land Outlook / Sahara Encroachment", 
        "classes": {
          "3": [
            "#8C510A", 
            "#E0D0B0", 
            "#0868AC"
          ], 
          "4": [
            "#8C510A", 
            "#DFC27D", 
            "#A8DDB5", 
            "#0868AC"
          ], 
          "5": [
            "#8C510A", 
            "#D0A155", 
            "#E0D0B0", 
            "#7EBFC0", 
            "#0868AC"
          ], 
          "6": [
            "#8C510A", 
            "#C68E3E", 
            "#E0C891", 
            "#C0D8B3", 
            "#5FADC6", 
            "#0868AC"
          ], 
          "7": [
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#E0D0B0", 
            "#A8DDB5", 
            "#43A2CA", 
            "#0868AC"
          ], 
          "8": [
            "#8C510A", 
            "#B87A28", 
            "#D7AF66", 
            "#E0CA9A", 
            "#CAD6B2", 
            "#91CCBC", 
            "#3D99C6", 
            "#0868AC"
          ], 
          "9": [
            "#8C510A", 
            "#B27525", 
            "#D0A155", 
            "#E0C58A", 
            "#E0D0B0", 
            "#B7DAB4", 
            "#7EBFC0", 
            "#3993C3", 
            "#0868AC"
          ], 
          "10": [
            "#8C510A", 
            "#AE7122", 
            "#CB9648", 
            "#DFC27D", 
            "#E0CB9F", 
            "#CFD5B2", 
            "#A8DDB5", 
            "#6EB5C4", 
            "#358EC0", 
            "#0868AC"
          ], 
          "11": [
            "#8C510A", 
            "#AA6D20", 
            "#C68E3E", 
            "#D9B56D", 
            "#E0C891", 
            "#E0D0B0", 
            "#C0D8B3", 
            "#98D1BA", 
            "#5FADC6", 
            "#328ABE", 
            "#0868AC"
          ]
        }, 
        "name_en": "Desert Biome Encroachment", 
        "id": "Drought_Multi_DesertBoundaries"
      }
    ], 
    "folder": "10_Drought_And_Aridity", 
    "name_en": "Drought and Aridity"
  }, 
  {
    "name_ar": "نماذج التغير المناخي والسيناريوهات", 
    "styles": [
      {
        "category": "Diverging", 
        "name_ar": "خطوط الاحترار العالمي لجامعة ريدينج (1850-2025)", 
        "source": "Prof. Ed Hawkins / University of Reading (Warming Stripes)", 
        "classes": {
          "3": [
            "#6BAED6", 
            "#FFFFBF", 
            "#CB181D"
          ], 
          "4": [
            "#08306B", 
            "#BDD7E7", 
            "#FCAE91", 
            "#67000D"
          ], 
          "5": [
            "#08306B", 
            "#BDD7E7", 
            "#FFFFBF", 
            "#FCAE91", 
            "#67000D"
          ], 
          "6": [
            "#08306B", 
            "#4C8FC6", 
            "#BDD7E7", 
            "#FCAE91", 
            "#E34733", 
            "#67000D"
          ], 
          "7": [
            "#08306B", 
            "#4C8FC6", 
            "#BDD7E7", 
            "#FFFFBF", 
            "#FCAE91", 
            "#E34733", 
            "#67000D"
          ], 
          "8": [
            "#08306B", 
            "#2171B5", 
            "#6BAED6", 
            "#BDD7E7", 
            "#FCAE91", 
            "#FB6A4A", 
            "#CB181D", 
            "#67000D"
          ], 
          "9": [
            "#08306B", 
            "#2171B5", 
            "#6BAED6", 
            "#BDD7E7", 
            "#FFFFBF", 
            "#FCAE91", 
            "#FB6A4A", 
            "#CB181D", 
            "#67000D"
          ], 
          "10": [
            "#08306B", 
            "#1C60A2", 
            "#4C8FC6", 
            "#82B8DA", 
            "#BDD7E7", 
            "#FCAE91", 
            "#FD7C5B", 
            "#E34733", 
            "#B11119", 
            "#67000D"
          ], 
          "11": [
            "#08306B", 
            "#1C60A2", 
            "#4C8FC6", 
            "#82B8DA", 
            "#BDD7E7", 
            "#FFFFBF", 
            "#FCAE91", 
            "#FD7C5B", 
            "#E34733", 
            "#B11119", 
            "#67000D"
          ]
        }, 
        "name_en": "Ed Hawkins Warming Stripes", 
        "id": "Model_Div_WarmingStripes"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "شذوذ درجات الحرارة المتوقعة لنماذج CMIP6 المناخية", 
        "source": "World Climate Research Programme (WCRP / CMIP6)", 
        "classes": {
          "3": [
            "#4393C3", 
            "#FFFFBF", 
            "#F46D43"
          ], 
          "4": [
            "#053061", 
            "#92C5DE", 
            "#FEE090", 
            "#A50026"
          ], 
          "5": [
            "#053061", 
            "#92C5DE", 
            "#FFFFBF", 
            "#FEE090", 
            "#A50026"
          ], 
          "6": [
            "#053061", 
            "#347CB8", 
            "#92C5DE", 
            "#FEE090", 
            "#F46D43", 
            "#A50026"
          ], 
          "7": [
            "#053061", 
            "#347CB8", 
            "#92C5DE", 
            "#FFFFBF", 
            "#FEE090", 
            "#F46D43", 
            "#A50026"
          ], 
          "8": [
            "#053061", 
            "#2166AC", 
            "#4393C3", 
            "#92C5DE", 
            "#FEE090", 
            "#FB9957", 
            "#E14730", 
            "#A50026"
          ], 
          "9": [
            "#053061", 
            "#2166AC", 
            "#4393C3", 
            "#92C5DE", 
            "#FFFFBF", 
            "#FEE090", 
            "#FB9957", 
            "#E14730", 
            "#A50026"
          ], 
          "10": [
            "#053061", 
            "#1A5899", 
            "#347CB8", 
            "#5A9FCA", 
            "#92C5DE", 
            "#FEE090", 
            "#FDAE61", 
            "#F46D43", 
            "#D73027", 
            "#A50026"
          ], 
          "11": [
            "#053061", 
            "#1A5899", 
            "#347CB8", 
            "#5A9FCA", 
            "#92C5DE", 
            "#FFFFBF", 
            "#FEE090", 
            "#FDAE61", 
            "#F46D43", 
            "#D73027", 
            "#A50026"
          ]
        }, 
        "name_en": "CMIP6 Temperature Anomaly", 
        "id": "Model_Div_TempAnomaly"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "نسبة التغير المتوقعة في الأمطار المستقبلية (%)", 
        "source": "IPCC Working Group I Interactive Atlas", 
        "classes": {
          "3": [
            "#BF812D", 
            "#F6E8C3", 
            "#01665E"
          ], 
          "4": [
            "#543005", 
            "#DFC27D", 
            "#80CDC1", 
            "#003C30"
          ], 
          "5": [
            "#543005", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#003C30"
          ], 
          "6": [
            "#543005", 
            "#A5691C", 
            "#DFC27D", 
            "#80CDC1", 
            "#1F7E76", 
            "#003C30"
          ], 
          "7": [
            "#543005", 
            "#A5691C", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#1F7E76", 
            "#003C30"
          ], 
          "8": [
            "#543005", 
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#80CDC1", 
            "#35978F", 
            "#01665E", 
            "#003C30"
          ], 
          "9": [
            "#543005", 
            "#8C510A", 
            "#BF812D", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#35978F", 
            "#01665E", 
            "#003C30"
          ], 
          "10": [
            "#543005", 
            "#7E4809", 
            "#A5691C", 
            "#C89142", 
            "#DFC27D", 
            "#80CDC1", 
            "#4AA49B", 
            "#1F7E76", 
            "#015B52", 
            "#003C30"
          ], 
          "11": [
            "#543005", 
            "#7E4809", 
            "#A5691C", 
            "#C89142", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#4AA49B", 
            "#1F7E76", 
            "#015B52", 
            "#003C30"
          ]
        }, 
        "name_en": "CMIP6 Precipitation % Change", 
        "id": "Model_Div_PrecipChange"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "سيناريوهات مسارات التطور المشتركة (SSP1 إلى SSP5)", 
        "source": "IPCC AR6 Cross-Working Group Scenario Palette", 
        "classes": {
          "3": [
            "#005A32", 
            "#FED976", 
            "#7F0000"
          ], 
          "4": [
            "#005A32", 
            "#74C476", 
            "#FD8D3C", 
            "#7F0000"
          ], 
          "5": [
            "#005A32", 
            "#4FA75D", 
            "#FED976", 
            "#F15F2B", 
            "#7F0000"
          ], 
          "6": [
            "#005A32", 
            "#36964E", 
            "#B0CD76", 
            "#FFAC53", 
            "#E93D22", 
            "#7F0000"
          ], 
          "7": [
            "#005A32", 
            "#238B45", 
            "#74C476", 
            "#FED976", 
            "#FD8D3C", 
            "#E31A1C", 
            "#7F0000"
          ], 
          "8": [
            "#005A32", 
            "#1F8442", 
            "#5FB368", 
            "#C7D176", 
            "#FFB95D", 
            "#F77432", 
            "#D41618", 
            "#7F0000"
          ], 
          "9": [
            "#005A32", 
            "#1B7E40", 
            "#4FA75D", 
            "#9BCA76", 
            "#FED976", 
            "#FFA14A", 
            "#F15F2B", 
            "#C91315", 
            "#7F0000"
          ], 
          "10": [
            "#005A32", 
            "#187A3F", 
            "#419E55", 
            "#74C476", 
            "#D4D376", 
            "#FFC062", 
            "#FD8D3C", 
            "#ED4D26", 
            "#C01013", 
            "#7F0000"
          ], 
          "11": [
            "#005A32", 
            "#16773D", 
            "#36964E", 
            "#65B86C", 
            "#B0CD76", 
            "#FED976", 
            "#FFAC53", 
            "#F97B35", 
            "#E93D22", 
            "#BA0F11", 
            "#7F0000"
          ]
        }, 
        "name_en": "IPCC Shared Socioeconomic SSPs", 
        "id": "Model_Multi_SSPSenarios"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "مؤشر تكرار وشدة الظواهر المناخية المتطرفة", 
        "source": "WMO Commission for Climatology / ETCCDI", 
        "classes": {
          "3": [
            "#FFFFCC", 
            "#FD7033", 
            "#490000"
          ], 
          "4": [
            "#FFFFCC", 
            "#FEA647", 
            "#D22528", 
            "#490000"
          ], 
          "5": [
            "#FFFFCC", 
            "#FEBC57", 
            "#FD7033", 
            "#A70020", 
            "#490000"
          ], 
          "6": [
            "#FFFFCC", 
            "#FFC965", 
            "#FD953F", 
            "#EF432A", 
            "#880017", 
            "#490000"
          ], 
          "7": [
            "#FFFFCC", 
            "#FED36F", 
            "#FEA647", 
            "#FD7033", 
            "#D22528", 
            "#750012", 
            "#490000"
          ], 
          "8": [
            "#FFFFCC", 
            "#FED976", 
            "#FEB24C", 
            "#FD8D3C", 
            "#FC4E2A", 
            "#BD0026", 
            "#67000D", 
            "#490000"
          ], 
          "9": [
            "#FFFFCC", 
            "#FFDE81", 
            "#FEBC57", 
            "#FE9B42", 
            "#FD7033", 
            "#E43829", 
            "#A70020", 
            "#63000C", 
            "#490000"
          ], 
          "10": [
            "#FFFFCC", 
            "#FFE189", 
            "#FFC35F", 
            "#FEA647", 
            "#FD873A", 
            "#FC562C", 
            "#D22528", 
            "#96001B", 
            "#60000B", 
            "#490000"
          ], 
          "11": [
            "#FFFFCC", 
            "#FFE490", 
            "#FFC965", 
            "#FEAE4A", 
            "#FD953F", 
            "#FD7033", 
            "#EF432A", 
            "#C30F27", 
            "#880017", 
            "#5E000A", 
            "#490000"
          ]
        }, 
        "name_en": "Climate Extremes ETCCDI", 
        "id": "Model_Multi_ExtremesIndex"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "الزيادة المتوقعة في عدد الليالي الاستوائية الحارة", 
        "source": "CMIP6 Future Extreme Temperature Projections", 
        "classes": {
          "3": [
            "#FFF7BC", 
            "#F5851F", 
            "#662506"
          ], 
          "4": [
            "#FFF7BC", 
            "#FFB643", 
            "#D75807", 
            "#662506"
          ], 
          "5": [
            "#FFF7BC", 
            "#FFCC60", 
            "#F5851F", 
            "#BF4603", 
            "#662506"
          ], 
          "6": [
            "#FFF7BC", 
            "#FFD777", 
            "#FEA231", 
            "#E66910", 
            "#AD3D04", 
            "#662506"
          ], 
          "7": [
            "#FFF7BC", 
            "#FFDE86", 
            "#FFB643", 
            "#F5851F", 
            "#D75807", 
            "#A13804", 
            "#662506"
          ], 
          "8": [
            "#FFF7BC", 
            "#FEE391", 
            "#FEC44F", 
            "#FE9929", 
            "#EC7014", 
            "#CC4C02", 
            "#993404", 
            "#662506"
          ], 
          "9": [
            "#FFF7BC", 
            "#FEE596", 
            "#FFCC60", 
            "#FFA938", 
            "#F5851F", 
            "#E0630D", 
            "#BF4603", 
            "#923205", 
            "#662506"
          ], 
          "10": [
            "#FFF7BC", 
            "#FEE79B", 
            "#FFD26D", 
            "#FFB643", 
            "#FC9527", 
            "#EE7516", 
            "#D75807", 
            "#B54103", 
            "#8D3105", 
            "#662506"
          ], 
          "11": [
            "#FFF7BC", 
            "#FFE99E", 
            "#FFD777", 
            "#FEC04B", 
            "#FEA231", 
            "#F5851F", 
            "#E66910", 
            "#CF5003", 
            "#AD3D04", 
            "#892F05", 
            "#662506"
          ]
        }, 
        "name_en": "Projected Tropical Nights TR20", 
        "id": "Model_Seq_TropicalNightsTR20"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "أيام الجفاف المتتالية واتساع الفترات الجافة", 
        "source": "IPCC AR6 Drought Projections Index", 
        "classes": {
          "3": [
            "#FFFFD4", 
            "#EC7C1C", 
            "#542788"
          ], 
          "4": [
            "#FFFFD4", 
            "#FFAF4E", 
            "#C3500A", 
            "#542788"
          ], 
          "5": [
            "#FFFFD4", 
            "#FFC976", 
            "#EC7C1C", 
            "#A93F06", 
            "#542788"
          ], 
          "6": [
            "#FFFFD4", 
            "#FED98E", 
            "#FE9929", 
            "#D95F0E", 
            "#993404", 
            "#542788"
          ], 
          "7": [
            "#FFFFD4", 
            "#FFDF9A", 
            "#FFAF4E", 
            "#EC7C1C", 
            "#C3500A", 
            "#933022", 
            "#542788"
          ], 
          "8": [
            "#FFFFD4", 
            "#FFE4A2", 
            "#FFBE65", 
            "#F99125", 
            "#DE6812", 
            "#B44607", 
            "#8D2E32", 
            "#542788"
          ], 
          "9": [
            "#FFFFD4", 
            "#FFE7A8", 
            "#FFC976", 
            "#FFA138", 
            "#EC7C1C", 
            "#D15A0C", 
            "#A93F06", 
            "#892C3D", 
            "#542788"
          ], 
          "10": [
            "#FFFFD4", 
            "#FFEAAD", 
            "#FFD283", 
            "#FFAF4E", 
            "#F68C23", 
            "#E16C14", 
            "#C3500A", 
            "#A03905", 
            "#852B45", 
            "#542788"
          ], 
          "11": [
            "#FFFFD4", 
            "#FFECB1", 
            "#FED98E", 
            "#FFB95E", 
            "#FE9929", 
            "#EC7C1C", 
            "#D95F0E", 
            "#B94908", 
            "#993404", 
            "#822B4C", 
            "#542788"
          ]
        }, 
        "name_en": "Consecutive Dry Days CDD", 
        "id": "Model_Seq_ConsecutiveDryDays"
      }, 
      {
        "category": "Diverging", 
        "name_ar": "شذوذ الأيام شديدة المطر والأمطار الغزيرة القصوى", 
        "source": "WMO ETCCDI Extreme Precipitation Indices", 
        "classes": {
          "3": [
            "#DFC27D", 
            "#F6E8C3", 
            "#018571"
          ], 
          "4": [
            "#A6611A", 
            "#DFC27D", 
            "#80CDC1", 
            "#003C30"
          ], 
          "5": [
            "#A6611A", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#003C30"
          ], 
          "6": [
            "#A6611A", 
            "#C4914C", 
            "#DFC27D", 
            "#80CDC1", 
            "#018571", 
            "#003C30"
          ], 
          "7": [
            "#A6611A", 
            "#C4914C", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#018571", 
            "#003C30"
          ], 
          "8": [
            "#A6611A", 
            "#BA813B", 
            "#CDA15C", 
            "#DFC27D", 
            "#80CDC1", 
            "#3C9D8B", 
            "#016C5A", 
            "#003C30"
          ], 
          "9": [
            "#A6611A", 
            "#BA813B", 
            "#CDA15C", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#3C9D8B", 
            "#016C5A", 
            "#003C30"
          ], 
          "10": [
            "#A6611A", 
            "#B57933", 
            "#C4914C", 
            "#D2A964", 
            "#DFC27D", 
            "#80CDC1", 
            "#4EA898", 
            "#018571", 
            "#005F4F", 
            "#003C30"
          ], 
          "11": [
            "#A6611A", 
            "#B57933", 
            "#C4914C", 
            "#D2A964", 
            "#DFC27D", 
            "#F6E8C3", 
            "#80CDC1", 
            "#4EA898", 
            "#018571", 
            "#005F4F", 
            "#003C30"
          ]
        }, 
        "name_en": "Very Wet Days R95p Index", 
        "id": "Model_Div_ExtremePrecipR95p"
      }, 
      {
        "category": "Sequential", 
        "name_ar": "تحول أيام درجات التدفئة والتبريد لاستهلاك الطاقة", 
        "source": "Energy Climatology Heating & Cooling Degree Days", 
        "classes": {
          "3": [
            "#BDD7E7", 
            "#2169AC", 
            "#BD0026"
          ], 
          "4": [
            "#BDD7E7", 
            "#4790C5", 
            "#885379", 
            "#BD0026"
          ], 
          "5": [
            "#BDD7E7", 
            "#5EA3D0", 
            "#2169AC", 
            "#D4524B", 
            "#BD0026"
          ], 
          "6": [
            "#BDD7E7", 
            "#6BAED6", 
            "#3182BD", 
            "#08519C", 
            "#FC4E2A", 
            "#BD0026"
          ], 
          "7": [
            "#BDD7E7", 
            "#7AB5D9", 
            "#4790C5", 
            "#2169AC", 
            "#885379", 
            "#F1452A", 
            "#BD0026"
          ], 
          "8": [
            "#BDD7E7", 
            "#85BADB", 
            "#559BCB", 
            "#2D7BB8", 
            "#1258A1", 
            "#B5535F", 
            "#EA3E29", 
            "#BD0026"
          ], 
          "9": [
            "#BDD7E7", 
            "#8CBDDC", 
            "#5EA3D0", 
            "#3A87C0", 
            "#2169AC", 
            "#53528F", 
            "#D4524B", 
            "#E43829", 
            "#BD0026"
          ], 
          "10": [
            "#BDD7E7", 
            "#92C0DE", 
            "#65A9D3", 
            "#4790C5", 
            "#2B77B6", 
            "#165CA3", 
            "#885379", 
            "#EA503A", 
            "#E03429", 
            "#BD0026"
          ], 
          "11": [
            "#BDD7E7", 
            "#96C2DF", 
            "#6BAED6", 
            "#5198C9", 
            "#3182BD", 
            "#2169AC", 
            "#08519C", 
            "#A95367", 
            "#FC4E2A", 
            "#DC3029", 
            "#BD0026"
          ]
        }, 
        "name_en": "Degree Days Heating/Cooling Shift", 
        "id": "Model_Seq_DegreeDays"
      }, 
      {
        "category": "Multi-Hue", 
        "name_ar": "سيناريوهات غمر وارتفاع منسوب البحر الساحلي حتى 2100", 
        "source": "IPCC Special Report on Ocean and Cryosphere (SROCC)", 
        "classes": {
          "3": [
            "#08519C", 
            "#FEE5D9", 
            "#A50F15"
          ], 
          "4": [
            "#08519C", 
            "#A4C9E1", 
            "#FD9879", 
            "#A50F15"
          ], 
          "5": [
            "#08519C", 
            "#6BAED6", 
            "#FEE5D9", 
            "#FB6A4A", 
            "#A50F15"
          ], 
          "6": [
            "#08519C", 
            "#569CCC", 
            "#CBDAE4", 
            "#FDB99F", 
            "#F0543B", 
            "#A50F15"
          ], 
          "7": [
            "#08519C", 
            "#4790C5", 
            "#A4C9E1", 
            "#FEE5D9", 
            "#FD9879", 
            "#E84432", 
            "#A50F15"
          ], 
          "8": [
            "#08519C", 
            "#3B88C1", 
            "#85BADB", 
            "#DADDE1", 
            "#FEC6AF", 
            "#FD7F5E", 
            "#E2382B", 
            "#A50F15"
          ], 
          "9": [
            "#08519C", 
            "#3182BD", 
            "#6BAED6", 
            "#BDD7E7", 
            "#FEE5D9", 
            "#FCAE91", 
            "#FB6A4A", 
            "#DE2D26", 
            "#A50F15"
          ], 
          "10": [
            "#08519C", 
            "#2E7CB9", 
            "#60A4D0", 
            "#A4C9E1", 
            "#E2DFDF", 
            "#FFCDB9", 
            "#FD9879", 
            "#F55E42", 
            "#D82A24", 
            "#A50F15"
          ], 
          "11": [
            "#08519C", 
            "#2B78B6", 
            "#569CCC", 
            "#8EBEDD", 
            "#CBDAE4", 
            "#FEE5D9", 
            "#FDB99F", 
            "#FD8766", 
            "#F0543B", 
            "#D22723", 
            "#A50F15"
          ]
        }, 
        "name_en": "Coastal Sea Level Rise Scenarios", 
        "id": "Model_Multi_SeaLevelRise"
      }
    ], 
    "folder": "11_Climate_Models", 
    "name_en": "Climate Models"
  }
]

CLIMATE_ELEMENTS_STYLES = [{'folder': '01_Temperature', 'name_en': 'Temperature', 'name_ar': 'درجات الحرارة', 'styles': TEMPERATURE_STYLES}] + OTHER_ELEMENTS
print("Mega Climate Styles Configured: 125 Palettes with 9 Class Tiers (3 to 11) across 11 Elements.")
