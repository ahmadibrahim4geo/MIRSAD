# -*- coding: utf-8 -*-
"""
test_drought_dependencies_108.py
Verifies:
1. Drought module parameters and dependency resolution.
2. Extraterrestrial radiation (Ra) computation.
3. FAO-56 Hargreaves PET, UNEP Aridity Index, De Martonne Index,
   Water Deficit, and Dry Months count.
4. Auto-computation in compute_point_fields.
"""
import sys
import os
import math
import unittest

# Point to workspace root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import pure-python functions from PYT (2/3 compatible: imp was removed in 3.12,
# and spec_from_file_location() returns None for the .pyt extension)
try:
    import importlib.machinery as _ilm

    def _load_source(_name, _path):
        return _ilm.SourceFileLoader(_name, _path).load_module()
except ImportError:  # Python 2.7 fallback
    import imp as _imp
    _load_source = _imp.load_source
_pyt = os.path.join(ROOT, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(_pyt):
    _pyt = os.path.join(ROOT, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")
pyt_mod = _load_source("pyt_tool", _pyt)


class TestDroughtIndices(unittest.TestCase):

    def test_drought_module_registered(self):
        # Schema evolved: drought/aridity indices live under "Climate_Models"
        # as named submodels (no standalone "Drought & Aridity" module).
        for _sub in pyt_mod.SUBMODELS_ALL:
            self.assertIn(_sub, pyt_mod.MODULES_ALL,
                          "Submodel %s missing from MODULES_ALL" % _sub)
        self.assertIn("Climate_Models", pyt_mod.MODULE_PARAMS)
        self.assertIn("Climate_Models", pyt_mod.MODULE_FOLDER)
        self.assertIn("Climate_Models", pyt_mod.COLOR_RAMPS)

        # Verify auto-dependency requirements
        params = pyt_mod.MODULE_PARAMS["Climate_Models"]
        for p in ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN"]:
            self.assertIn(p, params, "Missing required parameter %s for drought" % p)

    def test_extraterrestrial_radiation_ra(self):
        # Cairo latitude ~30 degrees North
        ra_jan = pyt_mod.extraterrestrial_radiation_ra(30.0, 1)
        ra_jul = pyt_mod.extraterrestrial_radiation_ra(30.0, 7)
        self.assertGreater(ra_jul, ra_jan, "Summer Ra should be higher than Winter Ra in Northern hemisphere")
        self.assertTrue(7.0 <= ra_jan <= 10.0, "January Ra for Cairo should be ~8.6 mm/day, got %.2f" % ra_jan)
        self.assertTrue(15.0 <= ra_jul <= 18.0, "July Ra for Cairo should be ~16.5 mm/day, got %.2f" % ra_jul)

    def test_compute_drought_fields_hyper_arid(self):
        # Hyper-arid scenario (e.g. Aswan / Southern Egypt)
        # Lat ~24 N, very low precip (~1-2 mm/year), very high temperatures
        years = [2023]
        m_tmean = {1: 15.0, 2: 17.0, 3: 22.0, 4: 28.0, 5: 33.0, 6: 36.0,
                   7: 37.0, 8: 37.0, 9: 34.0, 10: 29.0, 11: 22.0, 12: 17.0}
        m_tmax = {k: v + 7.0 for k, v in m_tmean.items()}
        m_tmin = {k: v - 7.0 for k, v in m_tmean.items()}
        m_precip = {k: 0.1 for k in range(1, 13)} # total ~1.2 mm/year

        fields = pyt_mod.compute_drought_fields(m_tmean, m_tmax, m_tmin, m_precip, lat=24.0)

        self.assertIn("DM_Aridity_Annual", fields)
        self.assertIn("PET_Hargreaves_Annual", fields)
        self.assertIn("UNEP_Aridity_Annual", fields)
        self.assertIn("Water_Deficit_Annual", fields)
        self.assertIn("Dry_Months_Count", fields)

        # Check values
        pet = fields["PET_Hargreaves_Annual"]
        unep = fields["UNEP_Aridity_Annual"]
        dm = fields["DM_Aridity_Annual"]
        wd = fields["Water_Deficit_Annual"]
        dry_m = fields["Dry_Months_Count"]

        self.assertGreater(pet, 1000.0, "PET should be substantial (>1000 mm/year)")
        self.assertLess(unep, 0.05, "UNEP AI should be hyper-arid (<0.05)")
        self.assertLess(dm, 5.0, "De Martonne should indicate extreme aridity (<5)")
        self.assertLess(wd, -1000.0, "Water deficit should be severely negative (P - PET)")
        self.assertEqual(dry_m, 12.0, "All 12 months should be dry")

    def test_compute_point_fields_with_drought(self):
        years = [2023]
        monthly = {
            "T2M": dict(((2023, m), 20.0) for m in range(1, 13)),
            "T2M_MAX": dict(((2023, m), 25.0) for m in range(1, 13)),
            "T2M_MIN": dict(((2023, m), 15.0) for m in range(1, 13)),
            "PRECTOTCORR": dict(((2023, m), 10.0) for m in range(1, 13)), # 120 mm/year
        }
        res = pyt_mod.compute_point_fields(
            monthly, years, ["Drought & Aridity"], "Monthly",
            precip_totals=True, lat=30.0
        )
        self.assertIn("DM_Aridity_Annual", res)
        self.assertIn("PET_Hargreaves_Annual", res)
        self.assertIn("UNEP_Aridity_Annual", res)
        self.assertIn("Water_Deficit_Annual", res)
        self.assertIn("Dry_Months_Count", res)


if __name__ == "__main__":
    unittest.main()
