# -*- coding: utf-8 -*-
"""
Tests for:
1. Execution Workflow Pipeline Mode (Batch Mode vs Sequential Mode)
2. Decoupled Temporal Scope Matrix (Annual, Winter, Spring, Summer, Autumn)
3. Both Climate Toolbox Tools:
   - POWER_Climate_Atlas_Generator_10_8.pyt
   - raster_atlas_generator.py
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


class MockArcPy(object):
    Parameter = MockParameter

    def AddFieldDelimiters(self, fc, fld):
        return fld

    def Exists(self, path):
        return True

    def ClearEnvironment(self, name):
        pass


mock_arcpy = MockArcPy()
sys.modules["arcpy"] = mock_arcpy

# Load pyt module dynamically
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


class TestTemporalScopeAndWorkflow(unittest.TestCase):

    def test_pyt_parse_temporal_scope(self):
        """Test parse_temporal_scope in POWER_Climate_Atlas_Generator_10_8."""
        all_5 = {"Annual", "Winter", "Spring", "Summer", "Autumn"}
        self.assertEqual(pyt_mod.parse_temporal_scope(None), all_5)
        self.assertEqual(pyt_mod.parse_temporal_scope(""), all_5)

        # Single scope
        self.assertEqual(pyt_mod.parse_temporal_scope("Annual"), {"Annual"})
        self.assertEqual(pyt_mod.parse_temporal_scope("Summer"), {"Summer"})

        # Multiple scopes separated by semicolon
        self.assertEqual(pyt_mod.parse_temporal_scope("Annual;Summer"), {"Annual", "Summer"})
        self.assertEqual(pyt_mod.parse_temporal_scope("Winter;Spring;Autumn"), {"Winter", "Spring", "Autumn"})

    def test_rag_parse_temporal_scope(self):
        """Test parse_temporal_scope in raster_atlas_generator."""
        all_5 = {"Annual", "Winter", "Spring", "Summer", "Autumn"}
        self.assertEqual(rag_mod.parse_temporal_scope(None), all_5)
        self.assertEqual(rag_mod.parse_temporal_scope(""), all_5)
        self.assertEqual(rag_mod.parse_temporal_scope("Annual"), {"Annual"})
        self.assertEqual(rag_mod.parse_temporal_scope("Annual;Winter;Spring"), {"Annual", "Winter", "Spring"})

    def test_get_field_temporal_scope_both_tools(self):
        """Test get_field_temporal_scope for primary indicators and submodels across both tools."""
        test_cases = [
            ("T_Annual_Mean", "Annual"),
            ("T_Winter_Mean", "Winter"),
            ("T_Spring_Mean", "Spring"),
            ("T_Summer_Mean", "Summer"),
            ("T_Autumn_Mean", "Autumn"),
            ("T_Annual_Range", "Annual"),
            ("R_Annual_Mean", "Annual"),
            ("R_Annual_Range", "Annual"),
            ("R_Winter_Mean", "Winter"),
            ("R_Spring_Mean", "Spring"),
            ("R_Summer_Mean", "Summer"),
            ("R_Autumn_Mean", "Autumn"),
            ("R_Winter_Total", "Winter"),
            ("R_Spring_Total", "Spring"),
            ("R_Summer_Total", "Summer"),
            ("R_Autumn_Total", "Autumn"),
            ("W_Spd_Annual_Mean", "Annual"),
            ("W_Spd_Winter_Mean", "Winter"),
            ("W_Spd_Spring_Mean", "Spring"),
            ("W_Spd_Summer_Mean", "Summer"),
            ("W_Spd_Autumn_Mean", "Autumn"),
            ("W_Dir_Annual_Mean", "Annual"),
            ("W_Dir_Winter_Mean", "Winter"),
            ("W_Dir_Spring_Mean", "Spring"),
            ("W_Dir_Summer_Mean", "Summer"),
            ("W_Dir_Autumn_Mean", "Autumn"),
            ("DM_Aridity_Annual", "Annual"),
            ("PET_Hargreaves_Annual", "Annual"),
            ("UNEP_Aridity_Annual", "Annual"),
            ("Water_Deficit_Annual", "Annual"),
            ("Dry_Months_Count", "Annual"),
            ("HI_Summer_Mean", "Summer"),
            ("HI_Winter_Mean", "Winter"),
            ("HI_Annual_Mean", "Annual"),
            ("WBGT_Summer_Mean", "Summer"),
        ]

        for fld, expected_scope in test_cases:
            self.assertEqual(pyt_mod.get_field_temporal_scope(fld), expected_scope,
                             "PYT scope mismatch for %s" % fld)
            self.assertEqual(rag_mod.get_field_temporal_scope(fld), expected_scope,
                             "RAG scope mismatch for %s" % fld)

    def test_resolve_filtered_fields_temporal_scope(self):
        """Test Cartesian product filtering by Temporal Scope in POWER_Climate_Atlas_Generator_10_8."""
        modules = ["Temperature", "Precipitation", "Wind"]

        # Case 1: Annual Only
        fields_annual = pyt_mod.resolve_filtered_fields(
            modules,
            "All Variables & Fields (Full Suite) [Recommended]",
            temporal_scope="Annual"
        )
        for m, flds in fields_annual.items():
            for f in flds:
                scope = pyt_mod.get_field_temporal_scope(f)
                self.assertEqual(scope, "Annual",
                                 "Field %s in module %s has scope %s, expected Annual" % (f, m, scope))

        self.assertIn("T_Annual_Mean", fields_annual["Temperature"])
        self.assertNotIn("T_Winter_Mean", fields_annual["Temperature"])
        self.assertNotIn("T_Summer_Mean", fields_annual["Temperature"])

        self.assertIn("R_Annual_Mean", fields_annual["Precipitation"])
        self.assertIn("R_Annual_Range", fields_annual["Precipitation"])
        self.assertNotIn("R_Month_Mean", fields_annual["Precipitation"])
        self.assertNotIn("R_Winter_Mean", fields_annual["Precipitation"])
        self.assertNotIn("R_Summer_Mean", fields_annual["Precipitation"])

        # Case 2: Summer Only
        fields_summer = pyt_mod.resolve_filtered_fields(
            modules,
            "All Variables & Fields (Full Suite) [Recommended]",
            temporal_scope="Summer"
        )
        for m, flds in fields_summer.items():
            for f in flds:
                scope = pyt_mod.get_field_temporal_scope(f)
                self.assertEqual(scope, "Summer",
                                 "Field %s in module %s has scope %s, expected Summer" % (f, m, scope))

        self.assertIn("T_Summer_Mean", fields_summer["Temperature"])
        self.assertNotIn("T_Annual_Mean", fields_summer["Temperature"])
        self.assertNotIn("T_Winter_Mean", fields_summer["Temperature"])

    def test_pyt_toolbox_parameters(self):
        """Verify parameters for Workflow Mode and Temporal Scope in 10_8 Tool."""
        tool = pyt_mod.PowerClimateAtlasGenerator()
        params = tool.getParameterInfo()
        pdict = {p.name: p for p in params}

        # Workflow mode parameter
        self.assertIn("Execution_Workflow_Mode", pdict)
        p_wf = pdict["Execution_Workflow_Mode"]
        self.assertEqual(p_wf.datatype, "GPString")
        self.assertIn("Batch Mode: Download All Then Process [Recommended]", p_wf.filter.list)
        self.assertIn("Sequential Mode: Element by Element", p_wf.filter.list)
        self.assertEqual(p_wf.value, "Batch Mode: Download All Then Process [Recommended]")

        # Temporal Scope parameter
        self.assertIn("Temporal_Scope", pdict)
        p_tscope = pdict["Temporal_Scope"]
        self.assertTrue(p_tscope.multiValue)
        self.assertEqual(p_tscope.filter.list, ["Annual", "Winter", "Spring", "Summer", "Autumn"])
        self.assertEqual(p_tscope.value, "Annual;Winter;Spring;Summer;Autumn")

        # Verify updateParameters disables workflow mode in offline mode
        pdict["Operation_Mode"].value = "Generate Maps from Existing Offline Multi-Layer Table"
        tool.updateParameters(params)
        self.assertFalse(p_wf.enabled)

        # Re-enable in online mode
        pdict["Operation_Mode"].value = "Download & Process from NASA POWER / Open-Meteo"
        tool.updateParameters(params)
        self.assertTrue(p_wf.enabled)

    def test_rag_toolbox_parameters(self):
        """Verify parameters for Workflow Mode and Temporal Scope in Raster Generator."""
        tool = rag_mod.RasterDataClimateAtlasGenerator()
        params = tool.getParameterInfo()
        pdict = {p.name: p for p in params}

        # Workflow mode parameter
        self.assertIn("Execution_Workflow_Mode", pdict)
        p_wf = pdict["Execution_Workflow_Mode"]
        self.assertEqual(p_wf.datatype, "GPString")
        self.assertIn("Batch Mode: Download All Then Process [Recommended]", p_wf.filter.list)
        self.assertIn("Sequential Mode: Element by Element", p_wf.filter.list)
        self.assertEqual(p_wf.value, "Batch Mode: Download All Then Process [Recommended]")

        # Temporal Scope parameter
        self.assertIn("Temporal_Scope", pdict)
        p_tscope = pdict["Temporal_Scope"]
        self.assertTrue(p_tscope.multiValue)
        self.assertEqual(p_tscope.filter.list, ["Annual", "Winter", "Spring", "Summer", "Autumn"])
        self.assertEqual(p_tscope.value, "Annual;Winter;Spring;Summer;Autumn")

        # Wind Factor Cell Size parameter
        self.assertIn("Wind_Factor_Cell_Size", pdict)
        p_wind_cell = pdict["Wind_Factor_Cell_Size"]
        self.assertEqual(p_wind_cell.value, 25000.0)

        # Wind Factor Cell Size disabled when Wind module not selected
        pdict["Climate_Modules"].value = "Temperature"
        tool.updateParameters(params)
        self.assertFalse(p_wind_cell.enabled)

        # Enabled when Wind module selected
        pdict["Climate_Modules"].value = "Temperature;Wind"
        tool.updateParameters(params)
        self.assertTrue(p_wind_cell.enabled)

        # Verify updateParameters disables workflow mode in offline mode
        pdict["Operation_Mode"].value = "Generate Atlas from Precalculated Point Layer(s) [Offline]"
        tool.updateParameters(params)
        self.assertFalse(p_wf.enabled)

        pdict["Operation_Mode"].value = "Download Gridded Data & Generate Atlas (Full Pipeline) [Default]"
        tool.updateParameters(params)
        self.assertTrue(p_wf.enabled)


if __name__ == "__main__":
    unittest.main()
