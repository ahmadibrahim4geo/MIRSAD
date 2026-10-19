# -*- coding: utf-8 -*-
"""Regressions for missing data and climatological output; Python 2/3."""
import unittest
import test_runtime_stability as support
import os
from mirsad_core.climate_quality import PointIndex, derive_from_fields, merge_point_layers

core, raster = support.core, support.raster


class Geometry(object):
    def __init__(self, x, y):
        self.centroid = support.Bag(X=x, Y=y)

    def projectAs(self, sr):
        return self


class TableCursor(object):
    def __init__(self, rows, fields):
        self.rows, self.fields = rows, fields

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def __iter__(self):
        for self.current in self.rows:
            yield [self.current.get(f) for f in self.fields]

    def updateRow(self, row):
        self.current.update(zip(self.fields, row))


class TableGIS(support.ArcPy):
    """Copies deliberately reverse rows and renumber OIDs, like real exports can."""
    def __init__(self, tables):
        support.ArcPy.__init__(self)
        self.tables = tables
        self.da = support.Bag(SearchCursor=self.cursor, UpdateCursor=self.cursor)
        self.management.CopyFeatures = self.copy
        self.management.AddField = self.add_field
        self.management.DeleteField = self.delete_fields
        self.CopyFeatures_management = self.copy
        self.AddField_management = self.add_field

    def cursor(self, path, fields):
        return TableCursor(self.tables[path], fields)

    def Exists(self, path):
        return path in self.tables

    def ListFields(self, path):
        names = set(name for row in self.tables[path] for name in row)
        return [support.Bag(name=n, type=("Geometry" if n == "SHAPE@" else
                "OID" if n == "OBJECTID" else "Double")) for n in sorted(names)]

    def copy(self, source, target):
        self.tables[target] = [dict(row, OBJECTID=i + 1)
                               for i, row in enumerate(reversed(self.tables[source]))]

    def add_field(self, path, name, *args, **kwargs):
        for row in self.tables[path]:
            row.setdefault(name, None)

    def delete_fields(self, path, names):
        for row in self.tables[path]:
            for name in names:
                row.pop(name, None)


class DataQuality(unittest.TestCase):
    def test_missing_rain_is_null_but_observed_zero_stays_zero(self):
        result = core.compute_point_fields(
            {"PRECTOTCORR": {(2025, 1): 0.0}}, [2025], ["Precipitation"],
            "Monthly", precip_totals=True, gap_method="none")
        self.assertEqual(result["R_January_Mean"], 0.0)
        self.assertIsNone(result["R_February_Mean"])
        self.assertIsNone(result["R_Annual_Mean"])

    def test_rain_sums_require_complete_periods(self):
        monthly = dict(((2025, m), 10.0) for m in range(1, 13))
        del monthly[(2025, 7)]
        result = core.seasonal_totals_from_monthly_totals(monthly, [2025])
        self.assertIsNone(result["Annual_Mean"])
        self.assertIsNone(result["Annual_Grand"])
        self.assertIsNone(result["Summer"])
        self.assertEqual(result["Winter"], 30.0)

    def test_complete_years_are_not_diluted_by_partial_years(self):
        monthly = dict(((2024, m), 10.0) for m in range(1, 13))
        monthly[(2025, 1)] = 1000.0
        result = core.seasonal_totals_from_monthly_totals(monthly, [2024, 2025])
        self.assertEqual(result["Annual_Mean"], 120.0)
        self.assertEqual(result["Annual_Grand"], 120.0)
        self.assertEqual(result["Winter"], 30.0)

    def test_daily_rain_totals_require_all_days(self):
        raw = dict(("202501%02d" % day, 1.0) for day in range(1, 31))
        grouped = core.build_monthly_from_daily({"PRECTOTCORR": raw}, [], ["PRECTOTCORR"], [2025])
        self.assertIsNone(grouped["PRECTOTCORR"][(2025, 1)])
        dates = ["2025-01-%02d" % day for day in range(1, 31)]
        self.assertIsNone(core.om_group_daily(dates, [1.0] * 30, "sum")[(2025, 1)])
        self.assertEqual(core.om_group_daily(dates + ["2025-01-31"], [1.0] * 31, "sum")[(2025, 1)], 31.0)
        self.assertIsNone(core.om_group_daily(dates + ["2025-01-30"], [1.0] * 31, "sum")[(2025, 1)])
        february = ["2024-02-%02d" % day for day in range(1, 30)]
        self.assertEqual(core.om_group_daily(february, [0.0] * 29, "sum")[(2024, 2)], 0.0)

    def test_drought_never_fabricates_missing_temperature_or_rain(self):
        result = core.compute_drought_fields({(2025, 1): 20.0}, {}, {}, {}, lat=30.0)
        for field in ("ET_Annual_Mean", "ET_February_Mean", "DM_Aridity_Annual",
                      "UNEP_Aridity_Annual", "Water_Deficit_Annual", "Dry_Months_Count"):
            self.assertIsNone(result.get(field), field)

    def test_et_is_independent_of_rain_but_requires_extremes(self):
        mean = dict((m, 20.0) for m in range(1, 13))
        high = dict((m, 25.0) for m in range(1, 13))
        low = dict((m, 15.0) for m in range(1, 13))
        result = core.compute_drought_fields(mean, high, low, {}, lat=30.0)
        self.assertGreater(result["ET_Annual_Mean"], 0)
        self.assertIsNone(result["UNEP_Aridity_Annual"])
        self.assertIsNone(result["Dry_Months_Count"])
        high.pop(7)
        result = core.compute_drought_fields(mean, high, low, {}, lat=30.0)
        self.assertIsNone(result["ET_July_Mean"])
        self.assertIsNone(result["ET_Summer_Mean"])
        self.assertIsNone(result["ET_Annual_Mean"])
        self.assertGreater(result["ET_Winter_Mean"], 0)

    def test_zero_rain_is_valid_and_zero_pet_has_no_aridity_ratio(self):
        mean = dict((m, 20.0) for m in range(1, 13))
        rain = dict((m, 0.0) for m in range(1, 13))
        result = core.compute_drought_fields(mean, mean, mean, rain, lat=30.0)
        self.assertEqual(result["ET_Annual_Mean"], 0.0)
        self.assertEqual(result["DM_Aridity_Annual"], 0.0)
        self.assertEqual(result["Dry_Months_Count"], 12)
        self.assertIsNone(result["UNEP_Aridity_Annual"])

    def test_raster_monthly_option_exists(self):
        pd = dict((p.name, p) for p in raster.RasterDataClimateAtlasGenerator().getParameterInfo())
        self.assertIn("Generate_Monthly_Rasters", pd)
        self.assertFalse(pd["Generate_Monthly_Rasters"].value)

    def test_raster_monthly_filter_keeps_mean_and_range_switches_independent(self):
        original, original_mkdir = raster.arcpy, raster.makedirs_ok
        gis = TableGIS({"points": [{"OBJECTID": 1, "SHAPE@": Geometry(31, 30),
                                   "T_Annual_Mean": None, "T_January_Mean": None,
                                   "T_January_Range": None}]})
        gis.GetCount_management = lambda p: support.Bag(getOutput=lambda i: "1")
        raster.arcpy, raster.makedirs_ok = gis, lambda path: None
        try:
            tool = raster.RasterDataClimateAtlasGenerator()
            raw = [(f, f) for f in ("T_Annual_Mean", "T_January_Mean", "T_January_Range")]
            for means, ranges, expected in (
                    (False, False, ["T_Annual_Mean"]),
                    (True, False, ["T_Annual_Mean", "T_January_Mean"]),
                    (False, True, ["T_Annual_Mean", "T_January_Range"]),
                    (True, True, [f[0] for f in raw])):
                exported = []
                tool._export_vectors = lambda p, m, d, fields, e, msg: exported.extend(f[0] for f in fields)
                tool._process_single_module_outputs(
                    0, "Temperature", 1, "points", raw, set(["Annual"]),
                    "out", "vec", False, None, "IDW", 1000, gis.sr,
                    "gdb", 1000, [], lambda m: None, lambda m: None,
                    monthly_enabled=means, monthly_ranges_on=ranges)
                self.assertEqual(exported, expected)
        finally:
            raster.arcpy, raster.makedirs_ok = original, original_mkdir

    def derive(self, fields):
        return derive_from_fields(fields, core.heat_index_c, core.humidex_c,
                                  core.wbgt_shade_c, core.windchill_c)

    def test_offline_annual_means_do_not_invent_monthly_pet_or_dry_count(self):
        result = self.derive({"T_Annual_Mean": 20.0, "R_Annual_Mean": 120.0})
        self.assertEqual(result["DM_Aridity_Annual"], 4.0)
        for name in ("ET_Annual_Mean", "ET_January_Mean", "UNEP_Aridity_Annual",
                     "Dry_Months_Count", "T_Annual_Trend_Decade", "T_Anom_Annual"):
            self.assertIsNone(result.get(name), name)

    def test_offline_actual_monthly_pet_and_dry_pairs_are_used(self):
        fields = {}
        for m in core.MONTH_NAMES_EN:
            fields.update({"T_%s_Mean" % m: 20.0, "R_%s_Mean" % m: 10.0,
                           "ET_%s_Mean" % m: 20.0})
        result = self.derive(fields)
        self.assertEqual(result["ET_Annual_Mean"], 240.0)
        self.assertEqual(result["ET_Winter_Mean"], 60.0)
        self.assertEqual(result["UNEP_Aridity_Annual"], 0.5)
        self.assertEqual(result["Dry_Months_Count"], 12)
        fields["Dry_Months_Count"] = 7
        fields["ET_Annual_Mean"] = 500.0
        self.assertEqual(self.derive(fields)["Dry_Months_Count"], 7)
        self.assertEqual(self.derive(fields)["ET_Annual_Mean"], 500.0)
        fields.pop("ET_July_Mean")
        fields.pop("ET_Annual_Mean")
        self.assertIsNone(self.derive(fields).get("ET_Annual_Mean"))

    def test_annual_thermal_inputs_do_not_supply_a_season(self):
        result = self.derive({"T_Annual_Mean": 30.0, "RH_Annual_Mean": 60.0})
        self.assertIsNotNone(result.get("HI_Annual_Mean"))
        self.assertIsNone(result.get("HI_Summer_Mean"))
        self.assertIsNone(result.get("HI_Winter_Mean"))

    def test_coincident_points_require_a_unique_identity(self):
        records = [{"lat": 30.0, "lon": 31.0, "fields": {"Station_ID": "a"}},
                   {"lat": 30.0, "lon": 31.0, "fields": {"Station_ID": "b"}}]
        index = PointIndex(records)
        self.assertIsNone(index.match(30.0, 31.0))
        self.assertEqual(index.match(30.0, 31.0, {"Station_ID": "b"}), 1)
        self.assertIsNone(index.match(31.0, 32.0, {"Station_ID": "b"}))

    def tables(self):
        return {
            "base": [{"OBJECTID": 10, "SHAPE@": Geometry(31.0, 30.0), "T_Annual_Mean": 20.0},
                     {"OBJECTID": 20, "SHAPE@": Geometry(32.0, 30.0), "T_Annual_Mean": 10.0}],
            "rain": [{"OBJECTID": 10, "SHAPE@": Geometry(32.0, 30.0), "R_Annual_Mean": 400.0},
                     {"OBJECTID": 20, "SHAPE@": Geometry(31.0, 30.0), "R_Annual_Mean": 300.0}],
            "wrong": [{"OBJECTID": 10, "SHAPE@": Geometry(31.0004, 30.0), "RH_Annual_Mean": 99.0}]}

    def test_merge_rejects_same_oid_at_another_or_nearby_location(self):
        gis, warnings = TableGIS(self.tables()), []
        records, index = merge_point_layers(gis, "base", ["base", "rain", "wrong"],
                                            gis.sr, {}, {}, warnings.append)
        self.assertEqual(records[0]["fields"]["R_Annual_Mean"], 300.0)
        self.assertEqual(records[1]["fields"]["R_Annual_Mean"], 400.0)
        self.assertNotIn("RH_Annual_Mean", records[0]["fields"])
        self.assertEqual(len(warnings), 1)

    def test_both_offline_engines_survive_renumbered_output_oids(self):
        for module in (core, raster):
            original_arcpy, original_project = module.arcpy, module.safe_project_fc
            gis = TableGIS(self.tables())
            module.arcpy = gis
            module.safe_project_fc = lambda base, *args: base
            try:
                if module is core:
                    paths = core.PowerClimateAtlasGenerator()._merge_offline_layers(
                        "base;rain;wrong", "gdb", gis.sr, ["De Martonne Aridity"],
                        ["De Martonne Aridity"], {"De Martonne Aridity": ["DM_Aridity_Annual"]},
                        lambda m: None, lambda m: None)
                else:
                    paths, _ = raster.RasterDataClimateAtlasGenerator()._merge_offline_layers(
                        ["base", "rain", "wrong"], "gdb", gis.sr, ["De Martonne Aridity"],
                        ["De Martonne Aridity"], lambda m: None, lambda m: None)
                actual = dict((row["SHAPE@"].centroid.X, row["DM_Aridity_Annual"])
                              for row in gis.tables[paths["De Martonne Aridity"]])
                self.assertEqual(actual, {31.0: 10.0, 32.0: 20.0})
            finally:
                module.arcpy, module.safe_project_fc = original_arcpy, original_project

    def test_raster_online_derived_values_use_actual_data_and_no_fixed_trends(self):
        original = raster.arcpy
        gis = TableGIS(self.tables())
        raster.arcpy = gis
        try:
            for model, field in (("De Martonne Aridity", "DM_Aridity_Annual"),
                                 ("Trends & Anomalies", "T_Annual_Trend_Decade"),
                                 ("Evapotranspiration", "ET_Annual_Mean")):
                path, _ = raster.RasterDataClimateAtlasGenerator()._process_single_derived_to_master_points(
                    "NASA POWER", model, [], 2024, 2025, "gdb", "scratch", "", "",
                    {"Temperature": "base", "Precipitation": "rain"}, {}, lambda m: None, lambda m: None)
                actual = dict((row["SHAPE@"].centroid.X, row[field]) for row in gis.tables[path])
                self.assertEqual(actual, {31.0: 10.0, 32.0: 20.0} if model == "De Martonne Aridity"
                                 else {31.0: None, 32.0: None})
        finally:
            raster.arcpy = original


if __name__ == "__main__":
    unittest.main()
