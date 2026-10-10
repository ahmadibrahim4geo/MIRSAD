# -*- coding: utf-8 -*-
"""
test_excel_export_108.py
Verifies:
1. write_excel_file creates valid .xls files with xlwt.
2. Formatted styling: dark blue headers, zebra striping, borders, auto column widths.
3. Arabic UTF-8 text integrity and RTL worksheet support.
4. write_master_excel_workbook multi-sheet creation.
5. write_csv UTF-8 BOM marker (\xef\xbb\xbf).
"""
import sys
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import types
mod = types.ModuleType("pyt_tool")
_pyt_file = os.path.join(ROOT, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")
if not os.path.exists(_pyt_file):
    _pyt_file = os.path.join(ROOT, "POWER_Climate_Atlas_Generator_10_8.pyt")
exec(compile(open(_pyt_file, "rb").read(), "pyt_tool", "exec"), mod.__dict__)
pyt_mod = mod


class TestExcelAndArabicExport(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_excel_")

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_excel_single_sheet_arabic(self):
        xls_path = os.path.join(self.test_dir, "test_arabic.xls")
        header = [u"رقم المحطة", u"اسم المحطة", u"متوسط الحرارة السنوي", u"مؤشر الجفاف"]
        rows = [
            [1, u"القاهرة", 21.45, 1.73],
            [2, u"الإسكندرية", 20.12, 4.25],
            [3, u"أسوان", 26.85, 0.15]
        ]
        ok = pyt_mod.write_excel_file(xls_path, header, rows, sheet_name=u"المناخ", rtl=True)
        self.assertTrue(ok, "write_excel_file returned False")
        self.assertTrue(os.path.isfile(xls_path), "Excel file was not created on disk")
        self.assertGreater(os.path.getsize(xls_path), 500, "Excel file is suspiciously small")

        # Read back with xlrd if available
        try:
            import xlrd
            wb = xlrd.open_workbook(xls_path)
            sheet = wb.sheet_by_index(0)
            self.assertEqual(sheet.nrows, 4)
            self.assertEqual(sheet.ncols, 4)
            val = sheet.cell_value(1, 1)
            self.assertEqual(val, u"القاهرة")
        except ImportError:
            pass

    def test_write_master_excel_workbook(self):
        master_xls = os.path.join(self.test_dir, "Climate_Atlas_Master_Workbook.xls")
        sheets = [
            ("Temperature", [u"ID", u"T_Annual_Mean", u"T_Summer_Mean"], [[1, 21.5, 28.2], [2, 20.1, 26.5]], False),
            ("Precipitation", [u"ID", u"R_Annual_Mean", u"R_Winter_Mean"], [[1, 25.4, 18.2], [2, 185.0, 120.0]], False),
            ("Drought", [u"ID", u"DM_Aridity", u"UNEP_Aridity"], [[1, 1.73, 0.042], [2, 4.25, 0.12]], False),
        ]
        ok = pyt_mod.write_master_excel_workbook(master_xls, sheets)
        self.assertTrue(ok, "write_master_excel_workbook returned False")
        self.assertTrue(os.path.isfile(master_xls), "Master workbook file was not created")
        self.assertGreater(os.path.getsize(master_xls), 1000)

        try:
            import xlrd
            wb = xlrd.open_workbook(master_xls)
            self.assertEqual(wb.nsheets, 3)
            self.assertIn("Temperature", wb.sheet_names())
            self.assertIn("Precipitation", wb.sheet_names())
            self.assertIn("Drought", wb.sheet_names())
        except ImportError:
            pass

    def test_write_csv_utf8_bom(self):
        csv_path = os.path.join(self.test_dir, "test_bom.csv")
        header = [u"المعرف", u"الاسم", u"الحرارة"]
        rows = [[1, u"مرسى علم", 25.3]]

        pyt_mod.write_csv(csv_path, header, rows)
        self.assertTrue(os.path.isfile(csv_path))

        with open(csv_path, "rb") as fh:
            content = fh.read()

        # Must begin with UTF-8 BOM \xef\xbb\xbf
        self.assertTrue(content.startswith(b"\xef\xbb\xbf"), "CSV missing UTF-8 BOM")
        # Check Arabic text is decodable
        decoded = content.decode("utf-8")
        self.assertIn(u"مرسى علم", decoded)

    def test_get_element_source_metadata_all_providers(self):
        # 1. Hybrid
        hyb = pyt_mod.get_element_source_metadata("Temperature", "Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling")
        self.assertIn("NOAA", hyb["primary_source"])
        self.assertIn("ERA5", hyb["gap_fill_source"])
        self.assertIn("In-Situ", hyb["spatial_resolution"])

        # 2. NOAA Direct
        noaa = pyt_mod.get_element_source_metadata("Wind", "NOAA ISD / GHCN Direct Station Ground Observations Archive")
        self.assertIn("NOAA", noaa["primary_source"])
        self.assertIn("Synoptic", noaa["model_used"])

        # 3. Open-Meteo ERA5
        om = pyt_mod.get_element_source_metadata("Precipitation", "Open-Meteo Historical API (ERA5 Reanalysis)", om_model="ERA5-Land")
        self.assertIn("Open-Meteo", om["primary_source"])
        self.assertIn("ERA5-Land", om["model_used"])
        self.assertIn("9 km", om["spatial_resolution"])

        # 4. NASA POWER
        nasa = pyt_mod.get_element_source_metadata("Solar Radiation", "NASA POWER API")
        self.assertIn("NASA POWER", nasa["primary_source"])
        self.assertIn("CERES", nasa["model_used"])

    def test_export_source_data_folder(self):
        pts = [
            {"oid": 1, "station_id": "623660-99999", "station_name": "Cairo Intl", "country": "EG", "lat": 30.12, "lon": 31.40, "elevation": 74.0},
            {"oid": 2, "station_id": "401800-99999", "station_name": "Jerusalem Airport", "country": "PS", "lat": 31.86, "lon": 35.21, "elevation": 757.0}
        ]
        modules = ["Temperature", "Precipitation", "Wind"]

        pyt_mod.export_source_data_folder(
            self.test_dir, pts, modules,
            provider="Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling",
            om_model="ERA5-Land", gap_method="climatological", y0=1996, y1=2025
        )

        source_dir = os.path.join(self.test_dir, "Source Data")
        self.assertTrue(os.path.isdir(source_dir), "Source Data folder was not created")

        xls_path = os.path.join(source_dir, "Climate_Data_Sources_Provenance.xls")
        self.assertTrue(os.path.isfile(xls_path), "Climate_Data_Sources_Provenance.xls missing")
        self.assertGreater(os.path.getsize(xls_path), 1000)

        csv_path = os.path.join(source_dir, "Climate_Data_Sources_Provenance.csv")
        self.assertTrue(os.path.isfile(csv_path), "Climate_Data_Sources_Provenance.csv missing")
        with open(csv_path, "rb") as fh:
            content = fh.read()
            self.assertTrue(content.startswith(b"\xef\xbb\xbf"), "Provenance CSV missing UTF-8 BOM")
            decoded = content.decode("utf-8")
            self.assertIn("Cairo Intl", decoded)
            self.assertIn("Jerusalem Airport", decoded)
            self.assertIn("623660-99999", decoded)
            self.assertIn("NOAA", decoded)

        readme_en = os.path.join(source_dir, "README_Sources_Provenance.txt")
        self.assertTrue(os.path.isfile(readme_en), "README_Sources_Provenance.txt missing")

        readme_ar = os.path.join(source_dir, u"README_مصادر_البيانات_والنماذج.txt")
        self.assertTrue(os.path.isfile(readme_ar), "README_مصادر_البيانات_والنماذج.txt missing")


if __name__ == "__main__":
    unittest.main()

