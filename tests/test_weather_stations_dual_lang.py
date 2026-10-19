# -*- coding: utf-8 -*-
"""Verification test suite for MIRSAD Ground Weather Stations Climate Atlas Generator:
1. English primary tool purity (English only, category=None, supplementary points present, legacy inputs hidden).
2. Arabic companion tool completeness (Arabic UI, category=None, correct mapping).
3. Arab stations spatial purity (zero anomalous points outside Arab geographic envelope).
"""
import os
import sys
import unittest
import types

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


class MockFilter(object):
    def __init__(self):
        self.type = ""
        self.list = []


class MockParameter(object):
    def __init__(self, displayName="", name="", datatype="", parameterType="", direction=""):
        self.displayName = displayName
        self.name = name
        self.datatype = datatype
        self.parameterType = parameterType
        self.direction = direction
        self.filter = MockFilter()
        self.value = None
        self.category = None
        self.description = ""
        self.enabled = True


class TestDualLanguageMirsadTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mock_arcpy = types.ModuleType("arcpy")
        mock_arcpy.Parameter = MockParameter
        mock_arcpy.da = types.SimpleNamespace()

        from importlib.machinery import SourceFileLoader
        pyt_path = os.path.join(BASE_DIR, "Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt")
        cls.mod = SourceFileLoader("mirsad_st_test", pyt_path).load_module("mirsad_st_test")
        cls.mod.arcpy = mock_arcpy
        cls.mod._core.arcpy = mock_arcpy

    def test_toolbox_tools_registration(self):
        tb = self.mod.Toolbox()
        self.assertEqual(len(tb.tools), 2)
        tool_names = [t.__name__ for t in tb.tools]
        self.assertIn("WeatherStationsAtlasGenerator", tool_names)
        self.assertIn("WeatherStationsAtlasGeneratorAR", tool_names)

    def test_english_tool_ui_and_parameters(self):
        tool = self.mod.WeatherStationsAtlasGenerator()
        params = tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)

        # 1. No collapsible category for station inputs
        self.assertIsNone(pdict["Station_Selection_Mode"].category)
        self.assertIsNone(pdict["Region_Filter"].category)
        self.assertIsNone(pdict["Select_Country"].category)
        self.assertIsNone(pdict["Study_Area_Polygon"].category)
        self.assertIsNone(pdict["Supplementary_Points"].category)
        self.assertIsNone(pdict["Include_Buffer_Stations"].category)

        # 2. Supplementary_Points present
        self.assertIn("Supplementary_Points", pdict)
        self.assertEqual(pdict["Supplementary_Points"].parameterType, "Optional")

        # 3. Legacy inputs completely hidden from GUI
        self.assertNotIn("Input_Point_Features", pdict)
        self.assertNotIn("Study_Area_Mask", pdict)

        # 4. English purity: no Arabic characters in top English parameter displayNames
        arabic_range = lambda s: any("\u0600" <= c <= "\u06FF" for c in s)
        for p in params[:15]:
            self.assertFalse(arabic_range(p.displayName), f"Found Arabic in English displayName: {p.displayName}")

    def test_arabic_tool_ui_and_parameters(self):
        tool = self.mod.WeatherStationsAtlasGeneratorAR()
        params = tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)

        # 1. Arabic tool label has (AR)
        self.assertIn("(AR)", tool.label)

        # 2. No category clips
        self.assertIsNone(pdict["Station_Selection_Mode"].category)
        self.assertIsNone(pdict["Supplementary_Points"].category)

        # 3. Arabic displayNames
        self.assertIn("نمط اختيار", pdict["Station_Selection_Mode"].displayName)
        self.assertIn("نقاط رفع إضافية", pdict["Supplementary_Points"].displayName)
        self.assertIn("مضلع حدود منطقة الدراسة", pdict["Study_Area_Polygon"].displayName)

    def test_arab_stations_spatial_purity(self):
        tool = self.mod.WeatherStationsAtlasGenerator()
        arab_stations = tool._resolve_stations("Select by Country (National Network)", "ARAB", None, False, "")
        self.assertGreaterEqual(len(arab_stations), 900)

        # Verify all stations are within Arab League geographic envelope
        for s in arab_stations:
            lat = s["Lat"]
            lon = s["Lon"]
            self.assertTrue(-15.0 <= lat <= 38.5, f"Station {s['Name']} (ID: {s['Station_ID']}) lat {lat} out of Arab bounds!")
            self.assertTrue(-18.0 <= lon <= 61.0, f"Station {s['Name']} (ID: {s['Station_ID']}) lon {lon} out of Arab bounds!")
            self.assertNotIn("BOGUS", s["Name"].upper(), f"Bogus station slipped in: {s['Name']}")


if __name__ == "__main__":
    unittest.main()
