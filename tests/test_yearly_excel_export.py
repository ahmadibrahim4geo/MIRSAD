# -*- coding: utf-8 -*-
"""Year-specific climate summaries and lossless Excel-first export (Python 2/3)."""
from __future__ import unicode_literals
import copy
import os
import shutil
import tempfile
import unittest

import test_runtime_stability as support

core = support.core


class YearlyExcelExport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="yearly_excel_", dir=os.path.join(support.ROOT, "tests", "logs"))
        self.tool = core.PowerClimateAtlasGenerator()
        self.messages, self.warnings, self.workbooks = [], [], []
        self.writer = core.write_master_excel_workbook
        core.write_master_excel_workbook = lambda path, sheets: self.workbooks.append((path, sheets)) or True
        self.meta = dict(y0=2023, y1=2024, temporal="Daily", provider="NASA POWER API",
                         gap_method="none", unit_temp="Celsius", request_start="2023-06-01",
                         request_end="2024-11-30")
        self.results = [dict(oid=7, lat=30.0, lon=31.0, station_id="001234", station_name="القاهرة",
            country="EG", monthly={
                "T2M": dict(((year, month), value) for year, value in ((2023, 10.0), (2024, 30.0))
                            for month in range(1, 13)),
                "PRECTOTCORR": dict(((year, month), value) for year, value in ((2023, 1.0), (2024, 2.0))
                                     for month in range(1, 13))},
            daily_raw={"T2M": {(2023, 12, 31): 11.0, (2024, 2, 29): 31.0},
                       "PRECTOTCORR": {(2023, 12, 31): 1.0, (2024, 2, 29): 2.0}},
            fields={"T_Annual_Mean": 999.0}, status="OK")]

    def tearDown(self):
        core.write_master_excel_workbook = self.writer
        shutil.rmtree(self.tmp)

    def export(self, module="Temperature", **kwargs):
        self.tool._export_yearly_excel(self.results, [2023, 2024], module, self.tmp, self.meta,
            self.messages.append, self.warnings.append, **kwargs)

    def sheet(self, workbook, name):
        return dict((item[0], item) for item in workbook[1])[name]

    def test_yearly_workbooks_recompute_data_month_daily_and_source_without_mutation(self):
        before = copy.deepcopy(self.results)
        self.export(save_daily=True)
        self.assertEqual(len(self.workbooks), 2)
        for workbook, year, mean, date in zip(self.workbooks, (2023, 2024), (10.0, 30.0),
                                             ("2023-12-31", "2024-02-29")):
            path, sheets = workbook
            self.assertTrue(path.endswith("_%d.xls" % year))
            self.assertEqual(set(s[0] for s in sheets), set(("Data", "Month", "Daily", "Source_Data")))
            data = self.sheet(workbook, "Data")
            row = dict(zip(data[1], data[2][0]))
            self.assertEqual(row["T_Annual_Mean"], mean)
            self.assertEqual(row["Station_ID"], "001234")
            self.assertEqual(row["Data_Start"], "2023-06-01" if year == 2023 else "2024-01-01")
            self.assertEqual(row["Data_End"], "2023-12-31" if year == 2023 else "2024-11-30")
            month = self.sheet(workbook, "Month")
            self.assertEqual(month[2][0][month[1].index("T_January_Mean")], mean)
            daily = self.sheet(workbook, "Daily")
            self.assertEqual(len(daily[2]), 1)
            self.assertEqual(daily[2][0][daily[1].index("Date")], date)
            source = self.sheet(workbook, "Source_Data")
            coverage = source[2][0][source[1].index("Requested_Data_Start")]
            self.assertIn(str(year), coverage)
            self.assertNotIn(str(2024 if year == 2023 else 2023), coverage)
        self.assertEqual(self.results, before)
        self.assertFalse(self.warnings)
        self.assertFalse(any(name.endswith(".csv") for name in os.listdir(self.tmp)))

    def test_yearly_precipitation_uses_year_totals_not_range_average(self):
        self.export(module="Precipitation", wanted_fields=["R_Annual_Mean"])
        for workbook, expected in zip(self.workbooks, (12.0, 24.0)):
            data = self.sheet(workbook, "Data")
            self.assertEqual(data[2][0][data[1].index("R_Annual_Mean")], expected)
            self.assertNotIn("Daily", [sheet[0] for sheet in workbook[1]])
            self.assertNotIn("R_Winter_Mean", data[1])

    def test_monthly_source_and_units_are_applied_separately_per_year(self):
        self.meta.update(temporal="Monthly", provider="Open-Meteo Historical API (ERA5 Reanalysis)",
                         unit_temp="Fahrenheit", om_model="ERA5-Land")
        self.export(save_daily=True)
        for workbook, expected in zip(self.workbooks, (50.0, 86.0)):
            data = self.sheet(workbook, "Data")
            self.assertEqual(data[2][0][data[1].index("T_Annual_Mean")], expected)
            self.assertNotIn("Daily", [sheet[0] for sheet in workbook[1]])

    def test_nasa_monthly_rain_rates_and_era5_totals_keep_their_year_semantics(self):
        self.meta["temporal"] = "Monthly"
        for provider, expected in (("NASA POWER API", (365.0, 732.0)),
                                   ("Open-Meteo Historical API (ERA5 Reanalysis)", (12.0, 24.0))):
            self.workbooks[:] = []
            self.meta["provider"] = provider
            self.export(module="Precipitation", wanted_fields=["R_Annual_Mean"])
            for workbook, total in zip(self.workbooks, expected):
                data = self.sheet(workbook, "Data")
                self.assertEqual(data[2][0][data[1].index("R_Annual_Mean")], total)

    def test_empty_year_does_not_inherit_range_values_or_other_years(self):
        self.results[0]["monthly"] = {"T2M": {(2023, 1): 10.0}}
        self.results[0]["daily_raw"] = {}
        self.export()
        data = self.sheet(self.workbooks[1], "Data")
        row = dict(zip(data[1], data[2][0]))
        self.assertIsNone(row["T_Annual_Mean"])
        self.assertEqual(row["Status"], "NO_DATA")

    def test_large_daily_series_stay_in_excel_without_csv(self):
        rows = [[index] for index in range(120001)]
        core.export_excel_with_fallback(os.path.join(self.tmp, "Temperature.xls"),
            [("Daily", ["Index"], rows, False)], self.messages.append, self.warnings.append)
        sheets = self.workbooks[0][1]
        self.assertEqual([s[0] for s in sheets], ["Daily", "Daily_2", "Daily_3"])
        self.assertEqual([len(s[2]) for s in sheets], [60000, 60000, 1])
        self.assertEqual([row for sheet in sheets for row in sheet[2]], rows)
        self.assertFalse(os.listdir(self.tmp))
        self.assertFalse(self.warnings)

    def test_excel_writer_failure_creates_complete_csv_and_reports_fallback(self):
        for failure in ("false", "exception"):
            def fail(*args):
                if failure == "exception":
                    raise IOError("workbook unavailable")
                return False
            core.write_master_excel_workbook = fail
            path = os.path.join(self.tmp, failure + ".xls")
            ok = core.export_excel_with_fallback(path,
                [("Daily", ["Date", "Value"], [["2024-02-29", 0.0]], False)],
                self.messages.append, self.warnings.append)
            self.assertFalse(ok)
            with open(os.path.splitext(path)[0] + "_daily.csv", "rb") as handle:
                content = handle.read().decode("utf-8-sig")
            self.assertIn("2024-02-29,0.0", content)
        self.assertEqual(len(self.warnings), 2)
        self.assertFalse(any(line.startswith("Excel:") for line in self.messages))

    def test_real_excel_roundtrip_keeps_all_rows_and_arabic_station_names(self):
        try:
            import xlrd
            import xlwt
        except ImportError:
            self.skipTest("Native Excel writer/reader not installed in this interpreter")
        core.write_master_excel_workbook = self.writer
        self.export(save_daily=True)
        self.tool._write_dictionaries(self.tmp, ["Temperature"], self.messages.append)
        core.export_source_data_folder(self.tmp, self.results, ["Temperature"], "NASA POWER API",
                                        msg=self.messages.append, warn=self.warnings.append)
        for year, expected in ((2023, 10.0), (2024, 30.0)):
            path = os.path.join(self.tmp, "%s_%d.xls" % (core.MODULE_SHORT["Temperature"], year))
            book = xlrd.open_workbook(path)
            data = book.sheet_by_name("Data")
            header = data.row_values(0)
            self.assertEqual(data.cell_value(1, header.index("T_Annual_Mean")), expected)
            self.assertEqual(data.cell_value(1, header.index("Station_Nm")), "القاهرة")
        path = os.path.join(self.tmp, "large.xls")
        core.export_excel_with_fallback(path, [("Daily", ["Index"], [[i] for i in range(60001)], False)],
                                        self.messages.append, self.warnings.append)
        book = xlrd.open_workbook(path)
        self.assertEqual(book.sheet_names(), ["Daily", "Daily_2"])
        self.assertEqual(book.sheet_by_name("Daily").nrows, 60001)
        self.assertEqual(book.sheet_by_name("Daily_2").cell_value(1, 0), 60000)
        self.assertFalse(self.warnings)
        self.assertFalse(any(name.endswith(".csv") for folder, dirs, files in os.walk(self.tmp) for name in files))


if __name__ == "__main__":
    unittest.main()
