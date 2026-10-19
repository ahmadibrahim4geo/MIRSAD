# -*- coding: utf-8 -*-
"""
test_modes_and_inputs_108.py
Verifies:
1. Parameter layout, ordering and 46-parameter count.
2. Operation_Mode toggling in updateParameters.
3. Offline vs. Download mode parameter enablement/disablement.
4. updateMessages validation requirements per mode.
"""
import sys
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:  # Python 3 (imp was removed in 3.12; .pyt needs SourceFileLoader)
    import importlib.machinery as _ilm

    def _load_source(_name, _path):
        return _ilm.SourceFileLoader(_name, _path).load_module()
except ImportError:  # Python 2.7 fallback
    import imp as _imp
    _load_source = _imp.load_source
_pyt = os.path.join(ROOT, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(_pyt):
    _pyt = os.path.join(ROOT, "POWER_Climate_Atlas_Generator_10_8.pyt")
pyt_mod = _load_source("pyt_tool", _pyt)

try:
    import arcpy  # noqa - getParameterInfo() builds real arcpy.Parameter objects
    _HAS_ARCPY = True
except ImportError:
    _HAS_ARCPY = False


class DummyParameter(object):
    def __init__(self, name, value=None, enabled=True):
        self.name = name
        self.value = value
        self.valueAsText = str(value) if value is not None else ""
        self.enabled = enabled
        self.altered = False
        self.filter = type("Filter", (), {"list": [], "type": "ValueList"})()
        self._message = None

    def clearMessage(self):
        self._message = None

    def setErrorMessage(self, msg):
        self._message = msg

    def hasError(self):
        return self._message is not None


@unittest.skipUnless(_HAS_ARCPY, "needs ArcGIS arcpy for getParameterInfo()")
class TestModesAndInputs(unittest.TestCase):

    def setUp(self):
        self.tool = pyt_mod.PowerClimateAtlasGenerator()

    def test_parameter_count_and_indices(self):
        params = self.tool.getParameterInfo()
        self.assertEqual(len(params), 69, "Expected 69 parameters, got %d" % len(params))

        # Index 0: Operation_Mode
        self.assertEqual(params[0].name, "Operation_Mode")
        self.assertEqual(params[0].value, "Download & Generate Atlas (Full Pipeline) [Default]")
        self.assertIn("Interpolate & Map Existing Data (Offline Mode - No Internet)", params[0].filter.list)

        # Index 1: Download_Only (run scope switch, next to Operation_Mode)
        self.assertEqual(params[1].name, "Download_Only")
        self.assertEqual(params[1].parameterType, "Optional")

        # Index 2: Input_Point_Features
        self.assertEqual(params[2].name, "Input_Point_Features")
        self.assertEqual(params[2].parameterType, "Optional")

        # Index 3: Precalculated_Point_Layers
        self.assertEqual(params[3].name, "Precalculated_Point_Layers")
        self.assertEqual(params[3].parameterType, "Optional")

    def test_update_parameters_download_mode(self):
        params = self.tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)
        pdict["Operation_Mode"].value = "Download & Generate Atlas (Full Pipeline) [Default]"

        self.tool.updateParameters(params)

        self.assertTrue(pdict["Input_Point_Features"].enabled, "Input_Point_Features should be enabled in Download mode")
        self.assertFalse(pdict["Precalculated_Point_Layers"].enabled, "Precalculated_Point_Layer should be disabled in Download mode")
        self.assertTrue(pdict["Climate_Data_Source"].enabled, "Climate_Data_Source should be enabled in Download mode")
        self.assertTrue(pdict["Time_Mode"].enabled, "Time_Mode should be enabled in Download mode")
        self.assertTrue(pdict["Download_Only"].enabled, "Download_Only should be enabled in Download mode")

    def test_update_parameters_offline_mode(self):
        params = self.tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)
        pdict["Operation_Mode"].value = "Interpolate & Map Existing Data (Offline Mode - No Internet)"

        self.tool.updateParameters(params)

        self.assertFalse(pdict["Input_Point_Features"].enabled, "Input_Point_Features should be disabled in Offline mode")
        self.assertTrue(pdict["Precalculated_Point_Layers"].enabled, "Precalculated_Point_Layer should be enabled in Offline mode")
        self.assertFalse(pdict["Climate_Data_Source"].enabled, "Climate_Data_Source should be disabled in Offline mode")
        self.assertFalse(pdict["Time_Mode"].enabled, "Time_Mode should be disabled in Offline mode")
        self.assertFalse(pdict["Download_Only"].enabled, "Download_Only should be disabled in Offline mode")
        self.assertFalse(pdict["Single_Year"].enabled, "Single_Year should be disabled in Offline mode")
        self.assertFalse(pdict["Start_Year"].enabled, "Start_Year should be disabled in Offline mode")
        self.assertFalse(pdict["End_Year"].enabled, "End_Year should be disabled in Offline mode")

    def test_update_messages_validation(self):
        params = self.tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)

        # 1. Download mode without input points should trigger error
        pdict["Operation_Mode"].value = "Download & Generate Atlas (Full Pipeline) [Default]"
        pdict["Input_Point_Features"].value = None
        self.tool.updateMessages(params)
        self.assertTrue(pdict["Input_Point_Features"].hasError(), "Expected error for missing Input_Point_Features in Download mode")

        # 2. Offline mode without precalculated layer should trigger error
        pdict["Operation_Mode"].value = "Interpolate & Map Existing Data (Offline Mode - No Internet)"
        pdict["Precalculated_Point_Layers"].value = None
        self.tool.updateMessages(params)
        self.assertTrue(pdict["Precalculated_Point_Layers"].hasError(), "Expected error for missing Precalculated_Point_Layer in Offline mode")


if __name__ == "__main__":
    unittest.main()
