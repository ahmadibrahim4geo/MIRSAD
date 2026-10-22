# -*- coding: utf-8 -*-
"""Independent FAO examples and missingness/provenance checks on Python 2.7/3."""
from __future__ import unicode_literals
import copy
import datetime as dt
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from mirsad_core import daily_climate as c, hybrid_pipeline as h


def hours():
    return ["2024-02-29T%02d:00" % hour for hour in range(24)]


class DailyScienceTests(unittest.TestCase):
    def test_fao56_example4_saturation_is_not_saturation_of_mean_temperature(self):
        self.assertAlmostEqual(c.saturation_mean(24.5, 15), 2.390, places=3)
        self.assertGreater(c.saturation_mean(24.5, 15), c.saturation_vp(19.75))

    def test_fao56_examples5_and6_actual_pressure_and_deficit(self):
        ea, method = c.actual_vp(25, 18, rhmax=82, rhmin=54)
        self.assertAlmostEqual(ea, 1.70, places=2)
        self.assertAlmostEqual(c.saturation_mean(25, 18) - ea, .91, places=2)
        self.assertEqual(method, "FAO56_eq17_RH_extrema")
        self.assertEqual(c.actual_vp(25, 18, dewpoint=0, rhmax=82, rhmin=54), (.6108, "FAO56_eq14_dewpoint"))

    def test_fao56_example8_daily_energy_and_example14_wind_height(self):
        self.assertAlmostEqual(c.radiation_ra(-20, "2001-09-03"), 32.2, places=1)
        self.assertAlmostEqual(c.wind_at_2m(3.2, 10), 2.4, places=1)
        self.assertIsNone(c.wind_at_2m(3.2, None))
        self.assertIsNone(c.wind_at_2m(-1, 10))
        self.assertEqual(c.wind_at_2m(0, 10), 0)

    def test_fao56_example18_daily_pm_full_components(self):
        # FAO-56 Chapter 4 Example 18: Uccle, 6 July, 50.8N, 100 m.
        raw = dict(T2M_MAX=21.5, T2M_MIN=12.3, RH2M_MAX=84, RH2M_MIN=63,
                   WS10M=10 / 3.6, ALLSKY_SFC_SW_DWN=22.07, SUNSHINE_DURATION=33300)
        original = copy.deepcopy(raw)
        values, metadata = c.derive_day(raw, 50.8, "2001-07-06", elevation=100, wind_height=10)
        self.assertAlmostEqual(values["Ra"], 41.09, places=2)
        self.assertAlmostEqual(values["Rn_FAO56"], 13.28, delta=.03)
        self.assertAlmostEqual(values["ET0_PM"], 3.88, delta=.03)
        self.assertAlmostEqual(values["Sunshine_Hours"], 9.25)
        self.assertEqual(metadata["T_method"], "(Tmax+Tmin)/2")
        self.assertEqual(metadata["ea_method"], "FAO56_eq17_RH_extrema")
        self.assertEqual(raw, original)

    def test_missing_inputs_never_become_default_sea_level_or_known_wind_height(self):
        raw = dict(T2M_MAX=25, T2M_MIN=15, T2MDEW=10, WS10M=3, PS=100,
                   ALLSKY_SFC_SW_DWN=15, SLP=101.3)
        values, metadata = c.derive_day(raw, 30, "2024-02-29")
        self.assertIsNone(values["U2"])
        self.assertIsNone(values["Rn_FAO56"])
        self.assertIsNone(values["ET0_PM"])
        self.assertIsNone(metadata["input_elevation"])
        self.assertEqual(metadata["pressure_kPa"], 100)
        self.assertIsNone(c.pressure_from_elevation(None))
        self.assertIsNone(c.actual_vp(25, 15, rhmax=101, rhmin=40)[0])
        self.assertIsNone(c.saturation_mean(10, 20))
        self.assertIsNone(c.saturation_vp(float("nan")))
        self.assertIsNone(c.penman_monteith(25, 15, 2, 1, 2, 10, 100))

    def test_polar_night_and_leap_day_do_not_reuse_a_monthly_representative_day(self):
        self.assertEqual(c.radiation_ra(90, "2024-12-21"), 0.)
        self.assertGreater(c.radiation_ra(90, "2024-06-21"), 0)
        self.assertNotEqual(c.radiation_ra(30, "2024-02-28"), c.radiation_ra(30, "2024-02-29"))
        self.assertIsNone(c.radiation_ra(91, "2024-02-29"))
        self.assertIsNone(c.radiation_ra(30, "2023-02-29"))


class HourlyProvenanceTests(unittest.TestCase):
    def test_extremes_means_and_time_integration_have_distinct_operations(self):
        values, details = c.hourly_to_daily(hours(), list(range(24)), "max", "percent", bounds=(0, 100))
        self.assertEqual(values, {"2024-02-29": 23})
        self.assertEqual(details["2024-02-29"]["valid_samples"], 24)
        self.assertEqual(details["2024-02-29"]["timezone"], "UTC")
        self.assertEqual(c.hourly_to_daily(hours(), list(range(24)), "min")[0]["2024-02-29"], 0)
        self.assertEqual(c.hourly_to_daily(hours(), [100] * 24, "sum", "MJ/m2/day", scale=.0036)[0]["2024-02-29"], 8.64)
        self.assertEqual(c.hourly_to_daily(hours(), list(range(24)), "mean")[0]["2024-02-29"], 11.5)

    def test_missing_duplicate_off_hour_invalid_and_short_arrays_cannot_be_complete(self):
        for timestamps, values in ((hours()[:-1], [50] * 23),
                                   (hours() + [hours()[0]], [50] * 25),
                                   ([hours()[0].replace(":00", ":30")] + hours()[1:], [50] * 24),
                                   (hours(), [50] * 23 + [None]),
                                   (hours(), [50] * 23 + [101])):
            daily, processing = c.hourly_to_daily(timestamps, values, "max", bounds=(0, 100))
            self.assertEqual(daily, {})
            self.assertEqual(processing["2024-02-29"]["status"], "incomplete_or_duplicate_hour")
        with self.assertRaises(ValueError):
            c.hourly_to_daily(hours(), [50] * 23, "max")

    def test_shared_pipeline_preserves_raw_data_and_emits_hourly_processing(self):
        original = dict(hourly=dict(time=hours(), relative_humidity_2m=list(range(24)),
                                   vapour_pressure_deficit=[.1] * 24))
        old = h._read
        calls = []
        def read(url, *args):
            calls.append(url)
            return json.dumps(original)
        h._read = read
        try:
            response = h.fetch_source("Open-Meteo", dict(latitude=30, longitude=31),
                dt.date(2024, 2, 29), dt.date(2024, 2, 29),
                ["RH2M_MAX", "RH2M_MIN", "VPD_SOURCE"], "era5", None, lambda: False)
        finally:
            h._read = old
        self.assertEqual(response["raw"], original)
        self.assertEqual(response["series"]["RH2M_MAX"], {"2024-02-29": 23})
        self.assertEqual(response["series"]["RH2M_MIN"], {"2024-02-29": 0})
        self.assertEqual(response["processing_by_variable"]["VPD_SOURCE"]["2024-02-29"]["operation"], "max")
        self.assertEqual(calls[0].count("relative_humidity_2m"), 1)

    def test_malformed_extra_hourly_array_preserves_valid_daily_temperature(self):
        payload=dict(daily=dict(time=["2024-02-29"],temperature_2m_mean=[20]),
                     hourly=dict(time=hours(),relative_humidity_2m=[50]*23))
        old=h._read
        h._read=lambda *args:json.dumps(payload)
        try:
            response=h.fetch_source("Open-Meteo",dict(latitude=30,longitude=31),
                dt.date(2024,2,29),dt.date(2024,2,29),["T2M","RH2M_MAX"],"era5",None,lambda:False)
        finally:h._read=old
        self.assertEqual(response["series"]["T2M"],{"2024-02-29":20})
        self.assertEqual(response["series"]["RH2M_MAX"],{})
        self.assertEqual(response["state"],"PARTIAL_FAILURE")
        self.assertTrue(any("array length mismatch" in warning for warning in response["warnings"]))

    def test_optional_dewpoint_quality_does_not_rewrite_legacy_hourly_values(self):
        payload=dict(hourly=dict(time=hours(),dew_point_2m=[5]*25,relative_humidity_2m=[50]*24,surface_pressure=[1000]*24))
        old=h._read;h._read=lambda *args:json.dumps(payload)
        try:
            response=h.fetch_source("Open-Meteo",dict(latitude=30,longitude=31),dt.date(2024,2,29),dt.date(2024,2,29),
                ["T2MDEW","PS","RH2M_MAX"],"era5",None,lambda:False)
        finally:h._read=old
        self.assertEqual(response["series"]["T2MDEW"],{"2024-02-29":5})
        self.assertEqual(response["series"]["PS"],{"2024-02-29":100})
        self.assertEqual(response["processing_by_variable"]["T2MDEW"]["2024-02-29"]["status"],"invalid_hourly_input")
        self.assertEqual(response["processing_by_variable"]["PS"]["2024-02-29"]["status"],"complete")
        self.assertEqual(response["raw"],payload)

    def test_unsupported_power_keys_are_skipped_and_processing_follows_winning_source(self):
        calls = []
        def fetch(source, station, start, end, required, *args):
            calls.append((source, list(required)))
            return dict(series={p: {"2024-02-29": 40} for p in required}, raw={}, urls=[], warnings=[],
                        processing_by_variable={"RH2M_MAX": {"2024-02-29": dict(operation="max", valid_samples=24)}})
        result = h.run([dict(station_key="user", latitude=30, longitude=31)],
                       dt.date(2024, 2, 29), dt.date(2024, 2, 29), ["RH2M_MAX", "T2M"], None,
                       lambda event: None, lambda: False, fetch=fetch)[0]
        self.assertEqual([source for source, required in calls], ["Open-Meteo"])
        self.assertEqual(result["processing_by_variable"]["RH2M_MAX"]["2024-02-29"]["source"], "Open-Meteo auto")
        calls[:] = []
        missing = h.run([dict(station_key="user", latitude=30, longitude=31)],
                        dt.date(2024, 2, 29), dt.date(2024, 2, 29), ["RH2M_MAX"], None,
                        lambda event: None, lambda: False, fetch=fetch, sources=("NASA POWER",))[0]
        self.assertEqual(calls, [])
        self.assertEqual(missing["missing_counts"], {"RH2M_MAX": 1})

    def test_vendored_science_is_identical_and_imports_without_arcgis(self):
        path = os.path.join(ROOT, "MIRSAD Desktop", "src", "mirsad_desktop", "daily_climate.py")
        with open(path, "rb") as handle:
            bundled = handle.read()
        with open(os.path.join(ROOT, "mirsad_core", "daily_climate.py"), "rb") as handle:
            self.assertEqual(bundled, handle.read())


if __name__ == "__main__":
    unittest.main()
