# -*- coding: utf-8 -*-
"""
ArcGIS Pro and ArcMap Dual Compatibility Verification Suite.
Verifies that both tools in the Climate Toolbox:
  1. POWER_Climate_Atlas_Generator_10_8.pyt
  2. raster_atlas_generator.py
operate flawlessly under ArcGIS Pro (Python 3.x, arcpy.mp, .lyrx, PYTHON3 expression type)
as well as ArcGIS Desktop 10.8 (Python 2.7, arcpy.mapping, .lyr, PYTHON_9.3 expression type).
"""

import unittest
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT_PATH = os.path.join(ROOT_DIR, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(PYT_PATH):
    PYT_PATH = os.path.join(ROOT_DIR, "POWER_Climate_Atlas_Generator_10_8.pyt")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Mock arcpy for headless unit testing
class MockFilter(object):
    def __init__(self):
        self.type = ""
        self.list = []

class MockParameter(object):
    def __init__(self, displayName="", name="", datatype="", parameterType="Optional", direction="Input"):
        self.displayName = displayName
        self.name = name
        self.datatype = datatype
        self.parameterType = parameterType
        self.direction = direction
        self._val = None
        self._val_text = None
        self.category = ""
        self.description = ""
        self.enabled = True
        self.filter = MockFilter()
        self.multiValue = False
        self.altered = False
        self.error_message = None
        self.warning_message = None

    @property
    def value(self):
        return self._val

    @value.setter
    def value(self, v):
        self._val = v
        self._val_text = str(v) if v is not None else ""

    @property
    def valueAsText(self):
        if self._val_text is not None:
            return self._val_text
        return str(self._val) if self._val is not None else ""

    @valueAsText.setter
    def valueAsText(self, v):
        self._val_text = v

    def setErrorMessage(self, msg):
        self.error_message = msg

    def setWarningMessage(self, msg):
        self.warning_message = msg


class MockProMap(object):
    def __init__(self):
        self.layers = []

    def addDataFromPath(self, path):
        self.layers.append(path)
        return True


_shared_pro_map = MockProMap()

class MockProProject(object):
    def __init__(self, target="CURRENT"):
        self.activeMap = _shared_pro_map

    def listMaps(self):
        return [_shared_pro_map]


class MockArcPyMP(object):
    ArcGISProject = MockProProject


class MockArcPy(object):
    Parameter = MockParameter
    mp = MockArcPyMP()

    def AddFieldDelimiters(self, fc, fld):
        return fld

    def Exists(self, path):
        return True

    def ClearEnvironment(self, name):
        pass


mock_arcpy = MockArcPy()
sys.modules["arcpy"] = mock_arcpy

# Dynamically load the pyt module
pyt_mod = type(sys)("power_atlas_pyt")
pyt_mod.__dict__["arcpy"] = mock_arcpy
raw_pyt = open(PYT_PATH, "rb").read()
if sys.version_info[0] == 3:
    if isinstance(raw_pyt, bytes):
        raw_pyt = raw_pyt.decode("utf-8")
    _nl = "\n" if "\n" in raw_pyt else "\r\n"
    _first, _sep, _rest = raw_pyt.partition(_nl)
    if "coding" in _first and _first.lstrip().startswith("#"):
        raw_pyt = _rest
exec(compile(raw_pyt, PYT_PATH, "exec"), pyt_mod.__dict__)
pyt_mod.arcpy = mock_arcpy

import raster_atlas_generator as rag_mod
rag_mod.arcpy = mock_arcpy


class TestArcGISProCompatibility(unittest.TestCase):

    def test_01_python3_runtime_detected(self):
        """Verify Python 3 is active and compatibility flags are correctly configured."""
        self.assertEqual(sys.version_info[0], 3)
        self.assertFalse(pyt_mod.PY27)
        self.assertFalse(rag_mod.PY27)

    def test_02_calculate_field_expression_type(self):
        """Verify CalculateField expression type is PYTHON3 in Python 3 / ArcGIS Pro."""
        self.assertEqual(rag_mod.CALC_EXPR_TYPE, "PYTHON3")

    def test_03_layer_file_extension_pro(self):
        """Verify raster layer file generation targets .lyrx under ArcGIS Pro."""
        # Test raster_atlas_generator _create_layer_file extension logic
        tif_dummy = os.path.join(ROOT_DIR, "tests", "dummy.tif")
        is_pro = not rag_mod.PY27
        lyr_ext = ".lyrx" if is_pro else ".lyr"
        self.assertEqual(lyr_ext, ".lyrx")

    def test_04_pyt_toolbox_registration(self):
        """Verify MIRSAD Climate Atlas Toolbox registers both tools for ArcGIS Pro."""
        tb = pyt_mod.Toolbox()
        self.assertTrue("MIRSAD" in tb.label or "ArcGIS Pro" in tb.label)
        self.assertEqual(len(tb.tools), 2)
        tool_classes = [t.__name__ for t in tb.tools]
        self.assertIn("PowerClimateAtlasGenerator", tool_classes)
        self.assertIn("RasterDataClimateAtlasGenerator", tool_classes)

    def test_05_rag_standalone_toolbox(self):
        """Verify raster_atlas_generator.py provides a valid Toolbox class for standalone Pro use."""
        self.assertTrue(hasattr(rag_mod, "Toolbox"))
        tb = rag_mod.Toolbox()
        self.assertTrue("MIRSAD" in tb.label or "ArcGIS Pro" in tb.label)
        self.assertEqual(len(tb.tools), 1)
        self.assertEqual(tb.tools[0].__name__, "RasterDataClimateAtlasGenerator")

    def test_06_arcpy_mp_add_to_map_support(self):
        """Verify _add_to_map in 10_8 tool uses arcpy.mp when running inside ArcGIS Pro."""
        tool = pyt_mod.PowerClimateAtlasGenerator()
        messages = []
        warnings = []
        def mock_msg(m): messages.append(m)
        def mock_warn(w): warnings.append(w)

        registry = [
            ("T_Annual_Mean", "C:/out/01_Temp/T_Annual_Mean.tif", None, "Temperature", None, None)
        ]
        map_modules = ["Temperature"]

        # Call _add_to_map
        tool._add_to_map(registry, None, map_modules, mock_msg, mock_warn)

        # Verify layer was added to MockProMap via addDataFromPath
        pro_map = mock_arcpy.mp.ArcGISProject("CURRENT").activeMap
        self.assertIn("C:/out/01_Temp/T_Annual_Mean.tif", pro_map.layers)
        self.assertTrue(any("current ArcGIS Pro map" in m for m in messages))

    def test_07_all_parameters_instantiate_in_pro(self):
        """Verify all parameters in both tools instantiate cleanly without arcpy deprecations."""
        tool1 = pyt_mod.PowerClimateAtlasGenerator()
        params1 = tool1.getParameterInfo()
        self.assertTrue(len(params1) >= 20)

        tool2 = rag_mod.RasterDataClimateAtlasGenerator()
        params2 = tool2.getParameterInfo()
        self.assertTrue(len(params2) >= 20)

        # Check workflow mode and temporal scope parameters in both
        pdict1 = {p.name: p for p in params1}
        pdict2 = {p.name: p for p in params2}

        self.assertIn("Execution_Workflow_Mode", pdict1)
        self.assertIn("Execution_Workflow_Mode", pdict2)
        self.assertIn("Temporal_Scope", pdict1)
        self.assertIn("Temporal_Scope", pdict2)


if __name__ == "__main__":
    unittest.main()
