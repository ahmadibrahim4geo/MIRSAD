"""Guard the approved pre-enrichment behavior across later optional features."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ClimateEnrichmentBaselineTests(unittest.TestCase):
    @unittest.skipIf(sys.version_info[0] < 3, "Cross-host auditor uses the independent Python 3 Desktop runtime")
    def test_existing_fields_values_daily_records_and_output_contracts(self):
        process = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "audit_climate_enrichment.py")],
                                   cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = process.communicate()
        self.assertEqual(process.returncode, 0, (out + error).decode("utf-8", "replace"))

    @unittest.skipIf(sys.version_info[0] < 3, "Capture guard runs in the Python 3 audit utility")
    def test_accepted_reference_cannot_be_silently_recaptured(self):
        path = os.path.join(ROOT, "tests", "fixtures", "climate_enrichment_baseline.json")
        with open(path, "rb") as handle:
            original = handle.read()
        process = subprocess.Popen([sys.executable, os.path.join(ROOT, "scripts", "audit_climate_enrichment.py"), "--capture"],
                                   cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, error = process.communicate()
        self.assertNotEqual(process.returncode, 0)
        self.assertIn(b"Refusing to replace", error)
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), original)

    def test_reference_preserves_leap_day_missingness_and_original_field_contract(self):
        path = os.path.join(ROOT, "tests", "fixtures", "climate_enrichment_baseline.json")
        with open(path, "rb") as handle:
            reference = json.loads(handle.read().decode("utf-8"))["contracts"]
        self.assertEqual(len(reference["module_fields"]), 19)
        complete = reference["desktop_outputs"]["complete"]["Precipitation"]["values"]
        missing = reference["desktop_outputs"]["missing_days"]["Precipitation"]["values"]
        self.assertEqual(complete["Valid_Days"], 731)
        self.assertEqual(missing["Valid_Days"], 730)
        self.assertLess(missing["Coverage_Fraction"], 1)
        self.assertIsNone(missing["R_Period_Total"])
        self.assertEqual(reference["module_folders"]["Evapotranspiration"], "15_Evapotranspiration")
        self.assertIn("ET_Annual_Mean", reference["module_fields"]["Evapotranspiration"])
        self.assertNotIn("Z_Elev_m", complete)
        self.assertNotIn("Z_Source", complete)


if __name__ == "__main__":
    unittest.main()
