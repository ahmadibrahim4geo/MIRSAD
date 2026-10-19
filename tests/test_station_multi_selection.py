# -*- coding: utf-8 -*-
"""Country -> multiple named stations, without native ArcGIS; Python 2/3."""
from __future__ import unicode_literals
import os
import shutil
import struct
import tempfile
import unittest

import test_runtime_stability as support
from mirsad_core.station_catalogue import load_catalogue, station_choices

stations = support.stations


def station(code, name, country, lat, lon, wban="99999"):
    return {"Station_ID": code, "WBAN": wban, "Name": name, "Country": country,
            "Country_Nm": country, "Lat": lat, "Lon": lon, "Elev_m": 0.0,
            "Continent": "Africa" if country == "EG" else "Asia", "Is_Arab": True}


class StationMultipleSelection(unittest.TestCase):
    def setUp(self):
        self.saved_arcpy = stations.arcpy, stations._core.arcpy
        self.gis = support.ArcPy()
        stations.arcpy = stations._core.arcpy = self.gis
        logdir = os.path.join(support.ROOT, "tests", "logs")
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        self.tmp = tempfile.mkdtemp(prefix="station_picker_", dir=logdir)
        self.catalogue = {
            "EG": [station("623660", "Cairo", "EG", 30, 31, "11111"),
                   station("623660", "Cairo", "EG", 30.1, 31.1, "22222"),
                   station("624140", "Aswan", "EG", 24, 32)],
            "SA": [station("404380", "Riyadh", "SA", 24, 46)],
            "FR": [station("071560", "Paris", "FR", 49, 2)]}

    def tearDown(self):
        stations.arcpy, stations._core.arcpy = self.saved_arcpy
        shutil.rmtree(self.tmp)

    def setup_tool(self, arabic=False):
        cls = stations.WeatherStationsAtlasGeneratorAR if arabic else stations.WeatherStationsAtlasGenerator
        tool = cls()
        tool._station_catalogue = lambda: self.catalogue
        params = tool.getParameterInfo()
        pd = dict((p.name, p) for p in params)
        pd["Station_Selection_Mode"].value = ("اختيار محطات محددة من الدولة (اختيار متعدد)"
                                                if arabic else stations.SPECIFIC_STATIONS_MODE)
        pd["Select_Country"].value = "مصر (EG)" if arabic else "Egypt (EG)"
        return tool, params, pd

    def test_ui_in_both_languages_shows_country_stations_and_codes(self):
        for arabic in (False, True):
            tool, params, pd = self.setup_tool(arabic)
            tool.updateParameters(params)
            pick = pd["Selected_Stations"]
            self.assertTrue(pick.multiValue)
            self.assertTrue(pick.enabled)
            self.assertEqual(len(pick.filter.list), 3)
            self.assertTrue(all(", EG]" in label for label in pick.filter.list))
            self.assertTrue(any("623660/11111" in label for label in pick.filter.list))
            self.assertTrue(any("623660/22222" in label for label in pick.filter.list))
            self.assertEqual(pd["Select_Country"].valueAsText[-4:], "(EG)")
            self.assertEqual("اختيار" in pick.displayName, arabic)

    def test_country_change_clears_stale_selection_in_both_languages(self):
        for arabic in (False, True):
            tool, params, pd = self.setup_tool(arabic)
            tool.updateParameters(params)
            pd["Selected_Stations"].values = pd["Selected_Stations"].filter.list[:2]
            pd["Select_Country"].value = "Saudi Arabia (SA)"
            tool.updateParameters(params)
            self.assertEqual(pd["Selected_Stations"].values, [])
            self.assertEqual(len(pd["Selected_Stations"].filter.list), 1)
            self.assertIn(", SA]", pd["Selected_Stations"].filter.list[0])
            tool.updateMessages(params)
            self.assertIsNotNone(pd["Selected_Stations"].error)

    def test_repeated_validation_preserves_current_selection(self):
        tool, params, pd = self.setup_tool(True)
        tool.updateParameters(params)
        values = pd["Selected_Stations"].filter.list[:2]
        pd["Selected_Stations"].values = values
        for _ in range(3):
            tool.updateParameters(params)
            self.assertEqual(pd["Selected_Stations"].values, values)
            self.assertEqual(len(pd["Selected_Stations"].filter.list), 3)

    def test_other_regions_and_world_allow_individual_countries(self):
        for arabic, region in ((False, "Europe"), (True, "أوروبا"),
                               (False, "All Countries Worldwide (Global Open Dataset)"),
                               (True, "جميع دول العالم (قاعدة البيانات المفتوحة)")):
            tool, params, pd = self.setup_tool(arabic)
            pd["Region_Filter"].value = region
            pd["Select_Country"].value = "France (FR)"
            tool.updateParameters(params)
            self.assertEqual(pd["Select_Country"].valueAsText[-4:], "(FR)")
            self.assertEqual(len(pd["Selected_Stations"].filter.list), 1)
            self.assertIn(", FR]", pd["Selected_Stations"].filter.list[0])

    def test_no_country_requires_a_choice_and_reselection_clears_error(self):
        tool, params, pd = self.setup_tool()
        pd["Select_Country"].value = "[All Arab League Countries (ARAB)]"
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertIsNotNone(pd["Select_Country"].error)
        self.assertFalse(pd["Selected_Stations"].enabled)
        pd["Select_Country"].value = "Egypt (EG)"
        tool.updateParameters(params)
        pd["Selected_Stations"].values = pd["Selected_Stations"].filter.list[:1]
        tool.updateMessages(params)
        self.assertIsNone(pd["Select_Country"].error)
        self.assertIsNone(pd["Selected_Stations"].error)

    def test_explicit_subset_keeps_duplicate_usaf_codes_distinct(self):
        tool, params, pd = self.setup_tool()
        options = station_choices(self.catalogue["EG"])
        labels = [label for label in sorted(options) if "11111" in label]
        result = tool._resolve_stations(stations.SPECIFIC_STATIONS_MODE, "EG", None,
                                        False, "", selected_stations=labels + labels)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["WBAN"], "11111")

    def test_explicit_saudi_country_code_is_not_the_arab_aggregate(self):
        tool, _, _ = self.setup_tool()
        self.assertEqual(tool._parse_target_country("Saudi Arabia (SA)", "Arab"), "SA")
        self.assertEqual(tool._parse_target_country("[All Arab League Countries (ARAB)]", "Arab"), "ARAB")

    def test_same_codes_and_names_are_distinguished_by_location(self):
        a = station("623660", "Cairo", "EG", 30.0, 31.0)
        b = station("623660", "Cairo", "EG", 30.1, 31.1)
        choices = station_choices([a, b, dict(a)])
        self.assertEqual(len(choices), 2)
        self.assertTrue(any("30.100000" in label for label in choices))

    def test_empty_invalid_and_wrong_country_selections_never_fall_back(self):
        tool, _, _ = self.setup_tool()
        tool._load_all_stations = lambda *a: self.fail("Must not load the whole network")
        eg = list(station_choices(self.catalogue["EG"]))[0]
        for country, selected in (("EG", []), ("EG", ["unknown"]),
                                   ("EG", [eg, "unknown"]), ("SA", [eg])):
            with self.assertRaises(RuntimeError):
                tool._resolve_stations(stations.SPECIFIC_STATIONS_MODE, country, None,
                                       False, "", selected_stations=selected)

    def test_picker_inactive_for_spatial_mode_and_offline(self):
        tool, params, pd = self.setup_tool()
        tool._station_catalogue = lambda: self.fail("Inactive picker must not read the catalogue")
        pd["Station_Selection_Mode"].value = "Spatial Intersect by Study Area Boundary (Polygon Clip)"
        tool.updateParameters(params)
        self.assertFalse(pd["Selected_Stations"].enabled)
        pd["Station_Selection_Mode"].value = stations.SPECIFIC_STATIONS_MODE
        pd["Operation_Mode"].value = "Interpolate & Map Existing Data (Offline Mode - No Internet)"
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertFalse(pd["Selected_Stations"].enabled)
        self.assertIsNone(pd["Selected_Stations"].error)

    def test_national_mode_allows_optional_station_subset_after_region_and_country(self):
        for arabic, region, country in ((False, "Europe", "France (FR)"),
                                        (True, "أوروبا", "فرنسا (FR)"),
                                        (False, "Arab League Countries (22 Nations)", "Egypt (EG)"),
                                        (True, "دول الوطن العربي (22 دولة)", "مصر (EG)")):
            tool, params, pd = self.setup_tool(arabic)
            pd["Station_Selection_Mode"].value = ("اختيار بالدولة (الشبكة الوطنية المعتمدة)" if arabic
                                                    else "Select by Country (National Network)")
            pd["Region_Filter"].value = region
            pd["Select_Country"].value = country
            tool.updateParameters(params)
            self.assertTrue(pd["Selected_Stations"].enabled)
            self.assertTrue(pd["Selected_Stations"].filter.list)
            tool.updateMessages(params)
            self.assertIsNone(pd["Selected_Stations"].error)
            chosen = pd["Selected_Stations"].filter.list[:1]
            result = tool._resolve_stations("Select by Country (National Network)",
                "FR" if "(FR)" in country else "EG", None, False, "", selected_stations=chosen)
            self.assertEqual(len(result), 1)
            pd["Selected_Stations"].values = chosen
            tool.updateParameters(params)
            self.assertEqual(pd["Selected_Stations"].values, chosen)

    def test_national_mode_keeps_aggregate_scopes_and_full_network_default(self):
        tool, params, pd = self.setup_tool()
        pd["Station_Selection_Mode"].value = "Select by Country (National Network)"
        pd["Select_Country"].value = "[All Arab League Countries (ARAB)]"
        tool.updateParameters(params)
        self.assertEqual(pd["Select_Country"].valueAsText, "[All Arab League Countries (ARAB)]")
        # National aggregate scopes now also allow an explicit subset. Empty
        # selection still means the full network, as the execution check below verifies.
        self.assertTrue(pd["Selected_Stations"].enabled)
        self.assertTrue(pd["Selected_Stations"].filter.list)
        tool.updateMessages(params)
        self.assertIsNone(pd["Selected_Stations"].error)
        tool._load_all_stations = lambda *a: self.catalogue["EG"] + self.catalogue["SA"]
        result = tool._resolve_stations("Select by Country (National Network)", "EG", None, False, "")
        self.assertEqual(len(result), 3)

    def test_execution_passes_only_selected_stations_to_core_in_both_languages(self):
        original = stations._core.PowerClimateAtlasGenerator.execute
        try:
            for arabic, national in ((False, False), (True, False), (False, True), (True, True)):
                tool, params, pd = self.setup_tool(arabic)
                if national:
                    pd["Station_Selection_Mode"].value = ("اختيار بالدولة (الشبكة الوطنية المعتمدة)" if arabic
                                                            else "Select by Country (National Network)")
                tool.updateParameters(params)
                chosen = pd["Selected_Stations"].filter.list[:2]
                pd["Selected_Stations"].values = chosen
                pd["Output_Workspace"].value = self.tmp
                written, forwarded = [], []
                tool._write_stations_shapefile = lambda rows, path: written.extend(rows)
                tool._enrich_station_metadata = lambda *a: None
                stations._core.PowerClimateAtlasGenerator.execute = lambda self, p, m: forwarded.extend(p)
                tool.execute(params, support.Messages())
                self.assertEqual(len(written), 2)
                self.assertEqual(set(station_choices(written)), set(chosen))
                self.assertTrue(any(p.name == "Input_Point_Features" for p in forwarded))
                self.assertEqual(self.gis.env.workspace, "user_workspace")
        finally:
            stations._core.PowerClimateAtlasGenerator.execute = original

    def test_missing_catalogue_produces_validation_error(self):
        tool, params, pd = self.setup_tool()
        def unavailable():
            raise IOError("missing station DBF")
        tool._station_catalogue = unavailable
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertIn("missing station DBF", pd["Selected_Stations"].error)
        with self.assertRaises(IOError):
            tool._resolve_stations(stations.SPECIFIC_STATIONS_MODE, "EG", None,
                                   False, "", selected_stations=["anything"])

    def test_empty_execution_never_reaches_the_engine(self):
        tool, params, pd = self.setup_tool()
        tool.updateParameters(params)
        pd["Output_Workspace"].value = self.tmp
        tool._write_stations_shapefile = lambda *args: self.fail("Must not write a whole network")
        with self.assertRaises(RuntimeError):
            tool.execute(params, support.Messages())

    def test_real_directory_egypt_and_duplicate_code_labels_are_unambiguous(self):
        tool = stations.WeatherStationsAtlasGenerator()
        first = tool._station_catalogue()
        self.assertIs(first, tool._station_catalogue())
        # Audited Ghazza country correction removes one former EG display row;
        # raw source country remains separately preserved in the shared catalogue.
        self.assertEqual(len(first["EG"]), 85)
        self.assertEqual(len(station_choices(first["EG"])), 85)
        us = station_choices(first["US"])
        same_usaf = [(label, s) for label, s in us.items() if s["Station_ID"] == "999999"]
        self.assertGreater(len(same_usaf), 1)
        self.assertEqual(len(set(label for label, _ in same_usaf)), len(same_usaf))

    def test_dbf_reader_ignores_deleted_rows_and_invalidates_cache(self):
        path = os.path.join(self.tmp, "stations.dbf")
        fields = [("Station_ID", 10), ("Name", 24), ("Country", 2),
                  ("Lat", 12), ("Lon", 12)]
        header_size, record_size = 33 + 32 * len(fields), 1 + sum(width for _, width in fields)

        def write(name):
            header = bytearray(32)
            header[0] = 3
            header[4:12] = struct.pack("<IHH", 2, header_size, record_size)
            with open(path, "wb") as handle:
                handle.write(header)
                for field_name, width in fields:
                    descriptor = bytearray(32)
                    encoded = field_name.encode("ascii")
                    descriptor[:len(encoded)] = encoded
                    descriptor[11] = ord("C")
                    descriptor[16] = width
                    handle.write(descriptor)
                handle.write(b"\r")
                row = b"".join(value.encode("utf-8").ljust(width)
                               for value, (_, width) in zip(("623660", name, "EG", "30", "31"), fields))
                handle.write(b" " + row)
                handle.write(b"*" + row)
                handle.write(b"\x1a")
        write("محطة")
        first = load_catalogue(path)
        self.assertEqual(len(first["EG"]), 1)
        self.assertEqual(first["EG"][0]["Name"], "محطة")
        self.assertIs(first, load_catalogue(path))
        stamp = os.stat(path).st_mtime
        write("Updated")
        os.utime(path, (stamp + 2, stamp + 2))
        second = load_catalogue(path)
        self.assertIsNot(first, second)
        self.assertEqual(second["EG"][0]["Name"], "Updated")
        with open(path, "wb") as handle:
            handle.write(b"truncated")
        with self.assertRaises(ValueError):
            load_catalogue(path)


if __name__ == "__main__":
    unittest.main()
