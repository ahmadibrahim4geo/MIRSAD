# -*- coding: utf-8 -*-
"""Unit and regression tests for NOAA / WMO Weather Stations Atlas Generator & Hub."""
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

from country_continent_registry import COUNTRY_REGISTRY, get_country_info


class TestWeatherStationsRegistry(unittest.TestCase):
    def test_registry_coverage(self):
        self.assertGreater(len(COUNTRY_REGISTRY), 280)
        
        # Test Arab League countries
        arab_samples = ["EG", "SA", "AE", "AG", "DZ", "MO", "TS", "SU", "IZ", "KU", "QA", "MU", "LE", "BA", "YM", "MR", "SO", "DJ", "CN", "GZ", "WE"]
        for code in arab_samples:
            en, ar, cont, is_arab = get_country_info(code)
            self.assertTrue(is_arab, f"Expected {code} ({en}) to be recognized as Arab country")
            self.assertNotEqual(ar, "", f"Expected {code} to have Arabic name")

    def test_continent_assignment(self):
        # Samples across continents
        self.assertEqual(get_country_info("US")[2], "North America")
        self.assertEqual(get_country_info("CA")[2], "North America")
        self.assertEqual(get_country_info("FR")[2], "Europe")
        self.assertEqual(get_country_info("GM")[2], "Europe")
        self.assertEqual(get_country_info("JA")[2], "Asia")
        self.assertEqual(get_country_info("IN")[2], "Asia")
        self.assertEqual(get_country_info("CH")[2], "Asia")
        self.assertEqual(get_country_info("BR")[2], "South America")
        self.assertEqual(get_country_info("AR")[2], "South America")
        self.assertEqual(get_country_info("AS")[2], "Oceania")
        self.assertEqual(get_country_info("NZ")[2], "Oceania")
        self.assertEqual(get_country_info("SF")[2], "Africa")
        self.assertEqual(get_country_info("NI")[2], "Africa")
        self.assertEqual(get_country_info("AY")[2], "Antarctica")

    def test_pyt_compilation_and_parameters(self):
        pyt_path = os.path.join(BASE_DIR, "MIRSAD_Weather_Stations_Atlas_Generator.pyt")
        if not os.path.exists(pyt_path):
            pyt_path = os.path.join(BASE_DIR, "NOAA_WMO_Weather_Stations_Atlas_Generator.pyt")
        self.assertTrue(os.path.exists(pyt_path))

        with open(pyt_path, "r", encoding="utf-8") as f:
            code = f.read()

        class MockParam(object):
            def __init__(self, displayName='', name='', datatype='', parameterType='', direction='', multiValue=False):
                self.displayName = displayName
                self.name = name
                self.datatype = datatype
                self.parameterType = parameterType
                self.direction = direction
                self.multiValue = multiValue
                self._val = None
                self.enabled = True
                self.category = ''
                self.description = ''
                self.altered = False
                class Filter(object):
                    def __init__(self):
                        self.type = ''
                        self.list = []
                self.filter = Filter()

            @property
            def value(self):
                return self._val

            @value.setter
            def value(self, val):
                self._val = val

            @property
            def valueAsText(self):
                if self._val is None:
                    return ''
                if isinstance(self._val, list):
                    return ';'.join(str(x) for x in self._val)
                return str(self._val)

            @valueAsText.setter
            def valueAsText(self, val):
                self._val = val

            @property
            def values(self):
                if isinstance(self._val, list):
                    return self._val
                if self._val:
                    return str(self._val).split(';')
                return []

            @values.setter
            def values(self, vals):
                self._val = vals

        class MockArcpy(object):
            Parameter = MockParam
            @staticmethod
            def ListFields(layer): return []
            @staticmethod
            def AddMessage(m): pass
            @staticmethod
            def AddWarning(m): pass
            @staticmethod
            def AddError(m): pass

        sys.modules['arcpy'] = MockArcpy

        globs = {"__file__": pyt_path, "arcpy": MockArcpy}
        exec(code, globs)

        tool = globs["WeatherStationsAtlasGenerator"]()
        params = tool.getParameterInfo()
        self.assertGreaterEqual(len(params), 65)

        pdict = dict((p.name, p) for p in params)

        # Check Top Station Selection Parameters
        self.assertIn("Station_Selection_Mode", pdict)
        self.assertIn("Region_Filter", pdict)
        self.assertIn("Select_Country", pdict)
        self.assertIn("Study_Area_Polygon", pdict)
        self.assertIn("Include_Buffer_Stations", pdict)
        self.assertIn("Custom_Station_IDs", pdict)
        self.assertIn("Local_Station_Features", pdict)

        # Check Expanded Climate Data Source Parameter
        self.assertIn("Climate_Data_Source", pdict)
        src_list = pdict["Climate_Data_Source"].filter.list
        self.assertTrue(any("NASA POWER" in s for s in src_list))
        self.assertTrue(any("Open-Meteo" in s for s in src_list))
        self.assertTrue(any("NOAA ISD" in s for s in src_list))
        self.assertTrue(any("Hybrid" in s for s in src_list))

        # Check Core Carbon-Copy Parameters Exist
        self.assertIn("Climate_Modules", pdict)
        self.assertIn("Temporal_Scope", pdict)
        self.assertIn("Measurement_Units_System", pdict)
        self.assertIn("Interpolation_Method", pdict)
        self.assertIn("Base_Cell_Size", pdict)
        self.assertIn("Create_Isobars", pdict)
        self.assertIn("Enable_Raster_Reclass", pdict)
        self.assertIn("Focal_Smoothing", pdict)

        # Test cascading update to Arab Countries
        pdict["Station_Selection_Mode"].valueAsText = "Select by Country (National Network)"
        pdict["Region_Filter"].valueAsText = "Arab League Countries (22 Nations)"
        tool.updateParameters(params)
        self.assertIn("Egypt (EG)", pdict["Select_Country"].filter.list)
        self.assertIn("[All Arab League Countries (ARAB)]", pdict["Select_Country"].filter.list)

        # Test cascading update to Europe
        pdict["Region_Filter"].valueAsText = "Europe"
        tool.updateParameters(params)
        self.assertIn("France (FR)", pdict["Select_Country"].filter.list)
        self.assertIn("[All European Countries (EUROPE)]", pdict["Select_Country"].filter.list)

        # Test station resolution
        arab_stations = tool._resolve_stations("Select by Country (National Network)", "ARAB", None, False, "")
        self.assertGreaterEqual(len(arab_stations), 900)

        egypt_stations = tool._resolve_stations("Select by Country (National Network)", "EG", None, False, "")
        self.assertEqual(len(egypt_stations), 87)

        world_stations = tool._resolve_stations("Select by Country (National Network)", "WORLD", None, False, "")
        self.assertEqual(len(world_stations), 28095)


if __name__ == "__main__":
    unittest.main()
