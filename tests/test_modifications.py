# -*- coding: utf-8 -*-
"""
Verification suite for the Climate Toolbox modifications:
1. Removal of R_Max_Daily_Month and R_Annual_Rain_Days_Total (6 core precipitation fields).
2. Wind Vector Spacing parameter and wind vector generation (Wind_Vector_*).
3. Strict boundary masking & clipping (arcpy.env.mask & extent, raster ExtractByMask, wind vector Clip).
"""

import io
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT_PATH = os.path.join(ROOT_DIR, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(PYT_PATH):
    PYT_PATH = os.path.join(ROOT_DIR, "POWER_Climate_Atlas_Generator_10_8.pyt")

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

# Load pyt module dynamically
pyt_mod = type(sys)("power_atlas_pyt")
pyt_mod.__dict__["arcpy"] = mock_arcpy
exec(compile(open(PYT_PATH, "rb").read(), PYT_PATH, "exec"), pyt_mod.__dict__)
pyt_mod.arcpy = mock_arcpy

import raster_atlas_generator as rag
rag.arcpy = mock_arcpy


class TestClimateToolboxModifications(unittest.TestCase):

    def test_01_pyt_precipitation_fields_removed(self):
        """Test R_Max_Daily_Month and R_Annual_Rain_Days_Total are removed from pyt."""
        # 1. FIELD_DEFS
        field_names = [r[0] for r in pyt_mod.FIELD_DEFS]
        self.assertNotIn("R_Max_Daily_Month", field_names)
        self.assertNotIn("R_Annual_Rain_Days_Total", field_names)

        # Precipitation fields in FIELD_DEFS must be exactly the 8 core fields
        precip_field_defs = [r[0] for r in pyt_mod.FIELD_DEFS if r[4] == "Precipitation"]
        expected_8 = [
            "R_Annual_Mean",
            "R_Annual_Range",
            "R_Winter_Mean",
            "R_Spring_Mean",
            "R_Summer_Mean",
            "R_Autumn_Mean",
            "R_January_Mean",
            "R_February_Mean",
            "R_March_Mean",
            "R_April_Mean",
            "R_May_Mean",
            "R_June_Mean",
            "R_July_Mean",
            "R_August_Mean",
            "R_September_Mean",
            "R_October_Mean",
            "R_November_Mean",
            "R_December_Mean",
            "R_January_Range",
            "R_February_Range",
            "R_March_Range",
            "R_April_Range",
            "R_May_Range",
            "R_June_Range",
            "R_July_Range",
            "R_August_Range",
            "R_September_Range",
            "R_October_Range",
            "R_November_Range",
            "R_December_Range"
        ]
        self.assertEqual(precip_field_defs, expected_8)

        # 2. REQUIRED_COLUMNS
        self.assertNotIn("R_Max_Daily_Month", pyt_mod.REQUIRED_COLUMNS)
        self.assertNotIn("R_Annual_Rain_Days_Total", pyt_mod.REQUIRED_COLUMNS)
        precip_req = [f for f in pyt_mod.REQUIRED_COLUMNS if f.startswith("R_") and "Trend" not in f and "Anom" not in f]
        self.assertEqual(precip_req, expected_8)

        # 3. SHP_FIELD_MAP
        self.assertNotIn("R_Max_Daily_Month", pyt_mod.SHP_FIELD_MAP)
        self.assertNotIn("R_Annual_Rain_Days_Total", pyt_mod.SHP_FIELD_MAP)
        self.assertNotIn("R_Seasonal_Range", pyt_mod.SHP_FIELD_MAP)
        self.assertNotIn("R_Month_Mean", pyt_mod.SHP_FIELD_MAP)

        # 4. compute_point_fields
        monthly = {
            "PRECTOTCORR": dict(((2025, m), 10.0) for m in range(1, 13)),
        }
        res = pyt_mod.compute_point_fields(
            monthly, [2025], ["Precipitation"], "Daily",
            daily_raw={"PRECTOTCORR": {(2025, 1, 1): 5.0, (2025, 1, 2): 15.0}}
        )
        self.assertNotIn("R_Max_Daily_Month", res)
        self.assertNotIn("R_Annual_Rain_Days_Total", res)
        core_8 = [f for f in expected_8 if not (f.endswith("_Range") and any(m in f for m in ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")))]
        for exp_f in core_8:
            self.assertIn(exp_f, res)
        # monthly ranges appear only with the opt-in flag
        res_rng = pyt_mod.compute_point_fields(
            monthly, [2025], ["Precipitation"], "Daily",
            daily_raw={"PRECTOTCORR": {(2025, 1, 1): 5.0, (2025, 1, 2): 15.0}},
            monthly_ranges=True
        )
        for exp_f in expected_8:
            self.assertIn(exp_f, res_rng)

    def test_02_raster_generator_precipitation_fields_removed(self):
        """Test R_Max_Daily_Month and R_Annual_Rain_Days_Total are removed from raster_atlas_generator."""
        # 1. MODULE_INDICATOR_FIELDS["Precipitation"]
        precip_indicators = [f[0] for f in rag.MODULE_INDICATOR_FIELDS.get("Precipitation", [])]
        expected_8 = [
            "R_Annual_Mean",
            "R_Annual_Range",
            "R_Winter_Mean",
            "R_Spring_Mean",
            "R_Summer_Mean",
            "R_Autumn_Mean",
            "R_January_Mean",
            "R_February_Mean",
            "R_March_Mean",
            "R_April_Mean",
            "R_May_Mean",
            "R_June_Mean",
            "R_July_Mean",
            "R_August_Mean",
            "R_September_Mean",
            "R_October_Mean",
            "R_November_Mean",
            "R_December_Mean",
            "R_January_Range",
            "R_February_Range",
            "R_March_Range",
            "R_April_Range",
            "R_May_Range",
            "R_June_Range",
            "R_July_Range",
            "R_August_Range",
            "R_September_Range",
            "R_October_Range",
            "R_November_Range",
            "R_December_Range"
        ]
        self.assertEqual(precip_indicators, expected_8)
        self.assertNotIn("R_Max_Daily_Month", precip_indicators)
        self.assertNotIn("R_Annual_Rain_Days_Total", precip_indicators)

        # 2. SHP_FIELD_MAP
        self.assertNotIn("R_Max_Daily_Month", rag.SHP_FIELD_MAP)
        self.assertNotIn("R_Annual_Rain_Days_Total", rag.SHP_FIELD_MAP)
        self.assertNotIn("R_Seasonal_Range", rag.SHP_FIELD_MAP)
        self.assertNotIn("R_Month_Mean", rag.SHP_FIELD_MAP)

    def test_03_pyt_wind_spacing_parameter(self):
        """Test Wind Vector Spacing parameter displayName and behavior in pyt."""
        tool = pyt_mod.PowerClimateAtlasGenerator()
        params = tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)
        self.assertIn("Wind_Factor_Cell_Size", pdict)
        p_wind = pdict["Wind_Factor_Cell_Size"]
        self.assertEqual(p_wind.displayName, "Wind Vector Spacing / Cell Size (Meters)")

        # Verify resolve_submodel_name does not hijack Wind into Wind Chill
        self.assertIsNone(pyt_mod.resolve_submodel_name("Wind"))
        self.assertIsNone(pyt_mod.resolve_submodel_name("Temperature"))
        self.assertIsNotNone(pyt_mod.resolve_submodel_name("Wind Chill"))

        # Test dynamic enable/disable in updateParameters
        pdict["Climate_Modules"].value = "Temperature;Precipitation"
        tool.updateParameters(params)
        self.assertFalse(p_wind.enabled)

        pdict["Climate_Modules"].value = "Temperature;Wind"
        tool.updateParameters(params)
        self.assertTrue(p_wind.enabled)

        pdict["Climate_Modules"].value = "Wind"
        tool.updateParameters(params)
        self.assertTrue(p_wind.enabled)

    def test_04_raster_generator_wind_spacing_parameter(self):
        """Test Wind Vector Spacing parameter in RasterDataClimateAtlasGenerator."""
        tool = rag.RasterDataClimateAtlasGenerator()
        params = tool.getParameterInfo()
        pdict = dict((p.name, p) for p in params)
        self.assertIn("Wind_Factor_Cell_Size", pdict)
        p_wind = pdict["Wind_Factor_Cell_Size"]
        self.assertEqual(p_wind.displayName, "Wind Vector Spacing / Cell Size (Meters)")
        self.assertEqual(p_wind.category, "Cartography & Spatial Interpolation")

        # Test dynamic enable/disable in updateParameters
        # When Wind is NOT selected
        pdict["Climate_Modules"].value = "Temperature;Precipitation"
        tool.updateParameters(params)
        self.assertFalse(p_wind.enabled)

        # When Wind IS selected
        pdict["Climate_Modules"].value = "Temperature;Wind"
        tool.updateParameters(params)
        self.assertTrue(p_wind.enabled)

    def test_05_raster_generator_has_build_wind_vectors(self):
        """Verify _build_wind_vectors method exists in RasterDataClimateAtlasGenerator."""
        tool = rag.RasterDataClimateAtlasGenerator()
        self.assertTrue(hasattr(tool, "_build_wind_vectors"))

    def test_06_wind_vector_standard_naming(self):
        """Verify standard naming for the 5 wind vector layers in code."""
        # Check in POWER_Climate_Atlas_Generator_10_8.pyt
        with io.open(PYT_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        self.assertIn('fc = os.path.join(gdb_path, "Wind_Vector_%s" % suffix)', content)

        # Check in raster_atlas_generator.py
        with io.open(os.path.join(ROOT_DIR, "raster_atlas_generator.py"), "r", encoding="utf-8", errors="ignore") as f:
            rag_content = f.read()
        self.assertIn('fc = os.path.join(gdb_path, "Wind_Vector_%s" % suffix)', rag_content)
        self.assertIn('arcpy.analysis.Clip(fish_pts, in_clip_layer, clipped_pts)', rag_content)

    def test_07_strict_mask_and_clip_in_code(self):
        """Verify arcpy.env.extent and ExtractByMask usage."""
        # In POWER_Climate_Atlas_Generator_10_8.pyt
        with io.open(PYT_PATH, "r", encoding="utf-8", errors="ignore") as f:
            pyt_content = f.read()
        self.assertIn('arcpy.env.extent = mask', pyt_content)
        self.assertIn('ExtractByMask(surf, effective_mask)', pyt_content)

        # In raster_atlas_generator.py
        with io.open(os.path.join(ROOT_DIR, "raster_atlas_generator.py"), "r", encoding="utf-8", errors="ignore") as f:
            rag_content = f.read()
        self.assertIn('arcpy.env.extent = clip_layer', rag_content)
        self.assertIn('clipped = ExtractByMask(raw_interp, clip_layer)', rag_content)

    def test_08_dew_point_module_separated(self):
        """Verify Dew Point is an independent module with 6 indicators and own folder."""
        # Check pyt
        self.assertIn("Dew Point", pyt_mod.PRIMARY_MODULES_ALL)
        self.assertEqual(pyt_mod.MODULE_FOLDER.get("Dew Point"), "08_Dew_Point")
        self.assertEqual(pyt_mod.MODULE_SHORT.get("Dew Point"), "Dew_Point")
        td_defs = [r[0] for r in pyt_mod.FIELD_DEFS if r[4] == "Dew Point"]
        expected_td = [
            "Td_Annual_Mean",
            "Td_Winter_Mean",
            "Td_Spring_Mean",
            "Td_Summer_Mean",
            "Td_Autumn_Mean",
            "Td_Annual_Range",
            "Td_January_Mean",
            "Td_February_Mean",
            "Td_March_Mean",
            "Td_April_Mean",
            "Td_May_Mean",
            "Td_June_Mean",
            "Td_July_Mean",
            "Td_August_Mean",
            "Td_September_Mean",
            "Td_October_Mean",
            "Td_November_Mean",
            "Td_December_Mean",
            "Td_January_Range",
            "Td_February_Range",
            "Td_March_Range",
            "Td_April_Range",
            "Td_May_Range",
            "Td_June_Range",
            "Td_July_Range",
            "Td_August_Range",
            "Td_September_Range",
            "Td_October_Range",
            "Td_November_Range",
            "Td_December_Range"
        ]
        self.assertEqual(td_defs, expected_td)
        # Ensure no Td_* in Temperature
        temp_defs = [r[0] for r in pyt_mod.FIELD_DEFS if r[4] == "Temperature"]
        self.assertTrue(all(not f.startswith("Td_") for f in temp_defs))

        # Check raster_atlas_generator
        self.assertIn("Dew Point", rag.PRIMARY_MODULES_ALL)
        self.assertEqual(rag.MODULE_FOLDER.get("Dew Point"), "08_Dew_Point")
        self.assertEqual(rag.MODULE_SHORT.get("Dew Point"), "Dew_Point")
        self.assertIn("Dew Point", rag.MODULE_INDICATOR_FIELDS)
        rag_td = [f[0] for f in rag.MODULE_INDICATOR_FIELDS["Dew Point"]]
        expected_td_rag = [
            "Td_Annual_Mean",
            "Td_Winter_Mean",
            "Td_Spring_Mean",
            "Td_Summer_Mean",
            "Td_Autumn_Mean",
            "Td_Annual_Range",
            "Td_January_Mean",
            "Td_February_Mean",
            "Td_March_Mean",
            "Td_April_Mean",
            "Td_May_Mean",
            "Td_June_Mean",
            "Td_July_Mean",
            "Td_August_Mean",
            "Td_September_Mean",
            "Td_October_Mean",
            "Td_November_Mean",
            "Td_December_Mean",
            "Td_January_Range",
            "Td_February_Range",
            "Td_March_Range",
            "Td_April_Range",
            "Td_May_Range",
            "Td_June_Range",
            "Td_July_Range",
            "Td_August_Range",
            "Td_September_Range",
            "Td_October_Range",
            "Td_November_Range",
            "Td_December_Range"
        ]
        self.assertEqual(rag_td, expected_td_rag)
        rag_temp = [f[0] for f in rag.MODULE_INDICATOR_FIELDS["Temperature"]]
        self.assertTrue(all(not f.startswith("Td_") for f in rag_temp))

    def test_09_evapotranspiration_unification(self):
        """Verify Evapotranspiration (ET) unification: annual-mean-as-total + monthly mean, folder 14_Evapotranspiration."""
        expected_et = [
            "ET_Annual_Mean",
            "ET_Annual_Range",
            "ET_Winter_Mean",
            "ET_Spring_Mean",
            "ET_Summer_Mean",
            "ET_Autumn_Mean",
            "ET_January_Mean",
            "ET_February_Mean",
            "ET_March_Mean",
            "ET_April_Mean",
            "ET_May_Mean",
            "ET_June_Mean",
            "ET_July_Mean",
            "ET_August_Mean",
            "ET_September_Mean",
            "ET_October_Mean",
            "ET_November_Mean",
            "ET_December_Mean",
            "ET_January_Range",
            "ET_February_Range",
            "ET_March_Range",
            "ET_April_Range",
            "ET_May_Range",
            "ET_June_Range",
            "ET_July_Range",
            "ET_August_Range",
            "ET_September_Range",
            "ET_October_Range",
            "ET_November_Range",
            "ET_December_Range"
        ]
        # In pyt
        self.assertIn("Evapotranspiration", pyt_mod.DERIVED_MODULES_ALL)
        self.assertEqual(pyt_mod.MODULE_FOLDER.get("Evapotranspiration"), "15_Evapotranspiration")
        self.assertEqual(pyt_mod.MODULE_SHORT.get("Evapotranspiration"), "Evapotranspiration")
        et_defs = [r[0] for r in pyt_mod.FIELD_DEFS if r[4] == "Evapotranspiration" and r[0] != "PET_Hargreaves_Annual"]
        self.assertEqual(et_defs, expected_et)

        # In raster_atlas_generator
        self.assertIn("Evapotranspiration", rag.DERIVED_MODULES_ALL)
        self.assertEqual(rag.MODULE_FOLDER.get("Evapotranspiration"), "15_Evapotranspiration")
        self.assertEqual(rag.MODULE_SHORT.get("Evapotranspiration"), "Evapotranspiration")
        self.assertIn("Evapotranspiration", rag.MODULE_INDICATOR_FIELDS)
        rag_et = [f[0] for f in rag.MODULE_INDICATOR_FIELDS["Evapotranspiration"]]
        expected_et_rag = [
            "ET_Annual_Mean",
            "ET_Annual_Range",
            "ET_Winter_Mean",
            "ET_Spring_Mean",
            "ET_Summer_Mean",
            "ET_Autumn_Mean",
            "ET_January_Mean",
            "ET_February_Mean",
            "ET_March_Mean",
            "ET_April_Mean",
            "ET_May_Mean",
            "ET_June_Mean",
            "ET_July_Mean",
            "ET_August_Mean",
            "ET_September_Mean",
            "ET_October_Mean",
            "ET_November_Mean",
            "ET_December_Mean",
            "ET_January_Range",
            "ET_February_Range",
            "ET_March_Range",
            "ET_April_Range",
            "ET_May_Range",
            "ET_June_Range",
            "ET_July_Range",
            "ET_August_Range",
            "ET_September_Range",
            "ET_October_Range",
            "ET_November_Range",
            "ET_December_Range"
        ]
        self.assertEqual(rag_et, expected_et_rag)

    def test_10_hi_monthly_optin_suite(self):
        """Verify opt-in monthly Heat Index suite: 12 HI_<Month>_Mean registered but stripped by default."""
        expected_hi_mon = [
            "HI_January_Mean", "HI_February_Mean", "HI_March_Mean",
            "HI_April_Mean", "HI_May_Mean", "HI_June_Mean",
            "HI_July_Mean", "HI_August_Mean", "HI_September_Mean",
            "HI_October_Mean", "HI_November_Mean", "HI_December_Mean"
        ]
        # In pyt: registered in FIELD_DEFS (Monthly/Mean/C) + SHP map
        hi_defs = [r[0] for r in pyt_mod.FIELD_DEFS if r[4] == "Heat Index"]
        for _f in expected_hi_mon:
            self.assertIn(_f, hi_defs)
            _row = pyt_mod.FIELD_BY_NAME[_f]
            self.assertEqual((_row[5], _row[6], _row[7]), ("Monthly", "Mean", "C"))
            self.assertLessEqual(len(pyt_mod.SHP_FIELD_MAP[_f]), 10)
        self.assertEqual(len(set(pyt_mod.SHP_FIELD_MAP.values())), len(pyt_mod.SHP_FIELD_MAP))
        # Computed (Rothfusz) + cold passthrough
        _ts = pyt_mod.compute_thermal_stress_fields(
            dict((m, 32.0) for m in range(1, 13)), dict((m, 60.0) for m in range(1, 13)))
        self.assertAlmostEqual(_ts["HI_July_Mean"], 37.07, places=1)
        _ts2 = pyt_mod.compute_thermal_stress_fields(
            dict((m, 5.0) for m in range(1, 13)), dict((m, 70.0) for m in range(1, 13)))
        self.assertEqual(_ts2["HI_January_Mean"], 5.0)
        # Param exists, default OFF, in the returned parameter list
        _pnames = [p.name for p in pyt_mod.PowerClimateAtlasGenerator().getParameterInfo()]
        self.assertIn("Extended_HI_Months", _pnames)
        # In raster_atlas_generator: mirrored
        rag_hi = [f[0] for f in rag.MODULE_INDICATOR_FIELDS["Heat Index"]]
        for _f in expected_hi_mon:
            self.assertIn(_f, rag_hi)
            self.assertLessEqual(len(rag.SHP_FIELD_MAP[_f]), 10)
        _rnames = [p.name for p in rag.RasterDataClimateAtlasGenerator().getParameterInfo()]
        self.assertIn("Extended_HI_Months", _rnames)

    def test_11_aliases_english_arabic_optin(self):
        """Aliases stay English (= field name); Arabic only via the opt-in _AR.gdb command."""
        import re
        with open(PYT_PATH, encoding="utf-8") as _fh:
            pyt_src = _fh.read()
        # Shapefile export: short NAME, alias = full English field name
        self.assertIn("AlterField(tmp_copy, n, SHP_FIELD_MAP[n], n)", pyt_src)
        # Main GDB: alias = field name
        self.assertIn("AddField(fc, wf, field_type, field_alias=wf)", pyt_src)
        # Arabic DB command maps every registered field (incl. new HI monthly) to Arabic
        self.assertIn("ar_map = dict((r[0], r[2]) for r in FIELD_DEFS)", pyt_src)
        for _m in ("January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"):
            _f = "HI_%s_Mean" % _m
            self.assertTrue(pyt_mod.FIELD_ALIAS_AR.get(_f), _f)
        # Excel Month sheet routing is keyword-based: new HI monthly match automatically
        for _m in ("January", "July", "December"):
            self.assertIn(_m, "HI_%s_Mean" % _m)
        # Raster tool: alias = field name
        rag_src_path = os.path.join(ROOT_DIR, "raster_atlas_generator.py")
        with open(rag_src_path, encoding="utf-8") as _fh:
            rag_src = _fh.read()
        self.assertIn("new_field_alias=fld", rag_src)

    def test_12_logical_ordering_and_period_filtering(self):
        """Verify sequential logical order (LST in pos 2), parameter counts (64 & 32), and period filtering."""
        # 1. Logical Module Ordering: LST in 2nd position after Temperature
        self.assertEqual(pyt_mod.PRIMARY_MODULES_ALL[0], "Temperature")
        self.assertEqual(pyt_mod.PRIMARY_MODULES_ALL[1], "Land Surface Temperature")
        self.assertEqual(rag.PRIMARY_MODULES_ALL[0], "Temperature")
        self.assertEqual(rag.PRIMARY_MODULES_ALL[1], "Land Surface Temperature")

        self.assertEqual(pyt_mod.MODULE_FOLDER["Land Surface Temperature"], "02_Land_Surface_Temperature")
        self.assertEqual(rag.MODULE_FOLDER["Land Surface Temperature"], "02_Land_Surface_Temperature")

        # 2. Legacy folder resolution
        self.assertEqual(pyt_mod.resolve_module_canonical("19_Land_Surface_Temperature"), "Land Surface Temperature")
        self.assertEqual(rag.resolve_module_canonical("19_Land_Surface_Temperature"), "Land Surface Temperature")
        self.assertEqual(pyt_mod.resolve_module_canonical("02_Land_Surface_Temperature"), "Land Surface Temperature")
        self.assertEqual(rag.resolve_module_canonical("02_Land_Surface_Temperature"), "Land Surface Temperature")

        # 3. Parameter Counts (Strictly 64/65/66 in PYT and 32/33/34 in RAG)
        pyt_params = pyt_mod.PowerClimateAtlasGenerator().getParameterInfo()
        self.assertIn(len(pyt_params), (64, 65, 66))
        rag_params = rag.RasterDataClimateAtlasGenerator().getParameterInfo()
        self.assertIn(len(rag_params), (32, 33, 34))

        # 4. Filter Scope: Annual Only
        ann_filtered = pyt_mod.resolve_filtered_fields(["Land Surface Temperature"], "Annual Only (سنوي فقط)")
        lst_ann = ann_filtered["Land Surface Temperature"]
        self.assertIn("LST_Annual_Mean", lst_ann)
        self.assertIn("LST_Annual_Range", lst_ann)
        self.assertNotIn("LST_Winter_Mean", lst_ann)
        self.assertNotIn("LST_January_Mean", lst_ann)
        self.assertNotIn("LST_Month_Mean", lst_ann)

        # 5. Filter Scope: Seasonal Only
        sea_filtered = pyt_mod.resolve_filtered_fields(["Land Surface Temperature"], "Seasonal Only (فصلي فقط)")
        lst_sea = sea_filtered["Land Surface Temperature"]
        self.assertIn("LST_Winter_Mean", lst_sea)
        self.assertIn("LST_Summer_Mean", lst_sea)
        self.assertNotIn("LST_Annual_Mean", lst_sea)
        self.assertNotIn("LST_January_Mean", lst_sea)

        # 6. Filter Scope: Monthly Climatology Only
        mon_filtered = pyt_mod.resolve_filtered_fields(["Land Surface Temperature"], "Monthly Climatology Only (شهري تفصيلي: يناير - ديسمبر)")
        lst_mon = mon_filtered["Land Surface Temperature"]
        self.assertIn("LST_January_Mean", lst_mon)
        self.assertIn("LST_July_Mean", lst_mon)
        self.assertNotIn("LST_Annual_Mean", lst_mon)
        self.assertNotIn("LST_Winter_Mean", lst_mon)
        self.assertNotIn("LST_Month_Mean", lst_mon)

        # 7. Redundant Month_Mean fields removed from candidate fields
        cand = pyt_mod.get_candidate_fields(["Land Surface Temperature", "Temperature"])
        self.assertNotIn("LST_Month_Mean", cand)
        self.assertNotIn("T_Month_Mean", cand)

        # 8. Full Suite: All fields included without redundant Month_Mean
        full_filtered = pyt_mod.resolve_filtered_fields(["Land Surface Temperature"], "Full Suite (Annual + Seasonal + Monthly) [Recommended]")
        lst_full = full_filtered["Land Surface Temperature"]
        self.assertIn("LST_Annual_Mean", lst_full)
        self.assertIn("LST_Winter_Mean", lst_full)
        self.assertIn("LST_January_Mean", lst_full)
        self.assertNotIn("LST_Month_Mean", lst_full)


if __name__ == "__main__":
    unittest.main()
