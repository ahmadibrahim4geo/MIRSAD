# -*- coding: utf-8 -*-
"""Audit blocking errors across every toolbox entry point, without native GIS."""
from __future__ import unicode_literals
import os
import shutil
import tempfile
import unittest

import test_runtime_stability as support

core, stations, raster = support.core, support.stations, support.raster


class ToolValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="validation_", dir=os.path.join(support.ROOT, "tests", "logs"))
        self.fake = support.ArcPy()
        core.arcpy = stations.arcpy = stations._core.arcpy = raster.arcpy = self.fake
        self.classes = (core.PowerClimateAtlasGenerator, stations.WeatherStationsAtlasGenerator,
                        stations.WeatherStationsAtlasGeneratorAR, raster.RasterDataClimateAtlasGenerator)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def setup_tool(self, cls):
        tool = cls()
        params = tool.getParameterInfo()
        pd = dict((p.name, p) for p in params)
        for name in ("Output_Workspace", "Output_Folder"):
            if name in pd:
                pd[name].value = self.tmp
        for name in ("Input_Point_Features", "Download_Extent_Layer"):
            if name in pd:
                pd[name].value = "valid_input"
        pd["Climate_Modules"].value = "Temperature"
        return tool, params, pd

    def errors(self, pd):
        return dict((name, p.error) for name, p in pd.items() if p.error)

    def test_all_visible_provider_choices_have_a_download_implementation(self):
        for cls in self.classes:
            tool, params, pd = self.setup_tool(cls)
            is_raster = cls == raster.RasterDataClimateAtlasGenerator
            for source in pd["Climate_Data_Source"].filter.list:
                self.assertIsNone(support.provider_error(source, raster=is_raster), (cls.__name__, source))
                pd["Climate_Data_Source"].value = source
                tool.updateParameters(params)
                tool.updateMessages(params)
                self.assertFalse(self.errors(pd), (cls.__name__, source, self.errors(pd)))

    def test_old_hybrid_settings_stay_explicit_errors_and_can_be_corrected(self):
        for cls in self.classes:
            tool, params, pd = self.setup_tool(cls)
            valid = pd["Climate_Data_Source"].value
            for old in ("Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling",
                        "NOAA ISD / GHCN Direct Station Ground Observations Archive", "Copernicus CDS"):
                pd["Climate_Data_Source"].value = old
                tool.updateParameters(params)
                tool.updateMessages(params)
                self.assertIsNotNone(pd["Climate_Data_Source"].error, cls.__name__)
                self.assertEqual(pd["Climate_Data_Source"].value, old)
            pd["Climate_Data_Source"].value = valid
            tool.updateParameters(params)
            tool.updateMessages(params)
            self.assertIsNone(pd["Climate_Data_Source"].error, cls.__name__)

    def test_model_choices_and_missing_prerequisites_do_not_create_blocking_errors(self):
        for cls in self.classes:
            tool, params, pd = self.setup_tool(cls)
            for model in pd["Climate_Modules"].filter.list:
                pd["Climate_Modules"].value = model
                tool.updateParameters(params)
                tool.updateMessages(params)
                self.assertFalse(self.errors(pd), (cls.__name__, model, self.errors(pd)))

    def test_repaired_raster_inputs_and_dates_clear_old_errors(self):
        tool, params, pd = self.setup_tool(raster.RasterDataClimateAtlasGenerator)
        pd["Download_Extent_Layer"].value = None
        pd["Time_Mode"].value = "Year Range"
        pd["Start_Year"].value, pd["End_Year"].value = 2025, 2024
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertIsNotNone(pd["Download_Extent_Layer"].error)
        self.assertIsNotNone(pd["End_Year"].error)
        pd["Download_Extent_Layer"].value = "valid_extent"
        pd["End_Year"].value = 2025
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertFalse(self.errors(pd), self.errors(pd))

    def test_offline_ignores_disabled_download_dates_and_provider_in_every_tool(self):
        for cls in self.classes:
            tool, params, pd = self.setup_tool(cls)
            pd["Climate_Data_Source"].value = "Hybrid"
            pd["Time_Mode"].value = "Year Range"
            pd["Start_Year"].value, pd["End_Year"].value = 2025, 2024
            tool.updateMessages(params)
            self.assertIsNotNone(pd["Climate_Data_Source"].error)
            pd["Operation_Mode"].value = "Interpolate & Map Existing Data (Offline Mode - No Internet)"
            pd["Precalculated_Point_Layers"].value = "existing_climate"
            tool.updateParameters(params)
            tool.updateMessages(params)
            self.assertFalse(self.errors(pd), (cls.__name__, self.errors(pd)))

    def test_disabled_pressure_settings_cannot_block_point_or_station_downloads(self):
        for cls in self.classes[:-1]:
            tool, params, pd = self.setup_tool(cls)
            pd["Pressure_Interval_Scheme"].value = "Custom Interval"
            pd["Custom_Pressure_Step"].value = 0
            for download_only, isobars in ((False, False), (True, True)):
                pd["Download_Only"].value = download_only
                pd["Create_Isobars"].value = isobars
                tool.updateParameters(params)
                tool.updateMessages(params)
                self.assertFalse(self.errors(pd), (cls.__name__, self.errors(pd)))

    def test_zero_raster_cell_size_is_reported_and_clears_after_repair(self):
        tool, params, pd = self.setup_tool(raster.RasterDataClimateAtlasGenerator)
        pd["Output_Cell_Size"].value = 0
        tool.updateMessages(params)
        self.assertIsNotNone(pd["Output_Cell_Size"].error)
        pd["Output_Cell_Size"].value = 500
        tool.updateMessages(params)
        self.assertIsNone(pd["Output_Cell_Size"].error)

    def test_openmeteo_models_are_enabled_in_both_station_languages(self):
        for cls in self.classes[1:3]:
            tool, params, pd = self.setup_tool(cls)
            tool.updateParameters(params)
            self.assertTrue(pd["OpenMeteo_Model"].enabled, cls.__name__)

    def test_active_pressure_settings_still_report_invalid_values(self):
        for cls in self.classes[:-1]:
            tool, params, pd = self.setup_tool(cls)
            pd["Climate_Modules"].value = "Sea Level Pressure"
            pd["Create_Isobars"].value = True
            pd["Pressure_Interval_Scheme"].value = "Custom Interval"
            pd["Custom_Pressure_Step"].value = 0
            tool.updateParameters(params)
            tool.updateMessages(params)
            self.assertIsNotNone(pd["Custom_Pressure_Step"].error, cls.__name__)
            pd["Custom_Pressure_Step"].value = 4
            tool.updateParameters(params)
            tool.updateMessages(params)
            self.assertIsNone(pd["Custom_Pressure_Step"].error, cls.__name__)

    def test_raster_offline_input_errors_clear_when_returning_online(self):
        tool, params, pd = self.setup_tool(raster.RasterDataClimateAtlasGenerator)
        pd["Operation_Mode"].value = "Interpolate & Map Existing Data (Offline Mode - No Internet)"
        pd["Precalculated_Point_Layers"].value = None
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertIsNotNone(pd["Precalculated_Point_Layers"].error)
        for name in ("Climate_Data_Source", "Time_Mode", "Single_Year", "Start_Year", "End_Year", "Start_Date", "End_Date"):
            self.assertFalse(pd[name].enabled, name)
        pd["Operation_Mode"].value = "Download Gridded Data & Generate Atlas (Full Pipeline) [Default]"
        tool.updateParameters(params)
        tool.updateMessages(params)
        self.assertFalse(self.errors(pd), self.errors(pd))


if __name__ == "__main__":
    unittest.main()
