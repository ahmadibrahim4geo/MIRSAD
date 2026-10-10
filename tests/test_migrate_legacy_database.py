# -*- coding: utf-8 -*-
"""Unit tests for migrate_legacy_database.py"""

import os
import sys
import unittest

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ_DIR not in sys.path:
    sys.path.insert(0, PROJ_DIR)

from migrate_legacy_database import (
    MODULES_INFO, SHP_FIELD_MAP, REV_SHP_MAP,
    heat_index_c, humidex_c, wbgt_shade_c, wind_chill_c,
    extraterrestrial_radiation_ra, LegacyAtlasMigrator
)

class TestLegacyMigration(unittest.TestCase):
    def test_modules_count(self):
        self.assertEqual(len(MODULES_INFO), 17)
        folders = [m["folder"] for m in MODULES_INFO]
        self.assertTrue(folders[0].startswith("01_"))
        self.assertTrue(folders[9].startswith("10_Heat_Index"))
        self.assertTrue(folders[16].startswith("17_Trends_And_Anomalies"))

    def test_temperature_fields_no_hi(self):
        t_mod = [m for m in MODULES_INFO if m["name"] == "Temperature"][0]
        t_flds = [f[0] for f in t_mod["fields"]]
        self.assertEqual(len(t_flds), 13)
        self.assertIn("T_Annual_Mean", t_flds)
        self.assertIn("Td_Annual_Mean", t_flds)
        self.assertNotIn("HI_Annual_Mean", t_flds)
        self.assertNotIn("WBGT_Summer_Mean", t_flds)

    def test_heat_index_standalone(self):
        hi_mod = [m for m in MODULES_INFO if m["name"] == "Heat Index"][0]
        hi_flds = [f[0] for f in hi_mod["fields"]]
        self.assertIn(len(hi_flds), (5, 7))
        self.assertIn("HI_Annual_Mean", hi_flds)
        self.assertIn("HI_Summer_Mean", hi_flds)
        self.assertIn("HI_Winter_Mean", hi_flds)
        self.assertIn("HI_Annual_Range", hi_flds)
        self.assertIn("WBGT_Summer_Mean", hi_flds)

    def test_bioclimatic_formulas(self):
        # Heat index when cool returns T
        self.assertEqual(heat_index_c(15.0, 50.0), 15.0)
        # Heat index when hot and humid increases
        hi_hot = heat_index_c(35.0, 70.0)
        self.assertGreater(hi_hot, 35.0)
        # Wind chill when cold and windy drops
        wc = wind_chill_c(2.0, 10.0)
        self.assertLess(wc, 2.0)
        # Radiation is positive
        ra = extraterrestrial_radiation_ra(30.0, 7)
        self.assertGreater(ra, 0.0)

    def test_csv_table_writer(self):
        import tempfile
        tmp_csv = os.path.join(tempfile.gettempdir(), "test_mig_table.csv")
        try:
            mig = LegacyAtlasMigrator(tempfile.gettempdir(), tempfile.gettempdir())
            records = [
                {
                    "oid": 1,
                    "lon": 31.2,
                    "lat": 30.0,
                    "fields": {
                        "T_Annual_Mean": 22.5,
                        "T_AnnMean": 22.5,
                    }
                }
            ]
            mig._write_csv_table(tmp_csv, records, ["T_Annual_Mean"], "2000", "2020")
            self.assertTrue(os.path.exists(tmp_csv))
            with open(tmp_csv, "r") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("T_Annual_Mean", lines[0])
            self.assertIn("22.5", lines[1])
        finally:
            if os.path.exists(tmp_csv):
                os.remove(tmp_csv)

if __name__ == "__main__":
    unittest.main()
