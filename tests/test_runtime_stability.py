# -*- coding: utf-8 -*-
"""Offline regressions for tool control flow; native GIS is tested separately.

Run this file in its own process: it deliberately installs a small ArcPy double.
Compatible with Python 2.7 and Python 3.
"""
import os
import sys
import types
import tempfile
import shutil
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


class Bag(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Parameter(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.value = None
        self.altered = False
        self.enabled = True
        self.filter = Bag(type="", list=[])
        self.category = None
        self.error = None

    @property
    def valueAsText(self):
        return self.value if isinstance(self.value, type(u"")) else (str(self.value) if self.value is not None else "")

    def setErrorMessage(self, message):
        self.error = message

    def setWarningMessage(self, message):
        pass

    def clearMessage(self):
        self.error = None


class Cursor(object):
    def __init__(self, rows=None):
        self.rows = rows or []

    def __enter__(self):
        return iter(self.rows)

    def __exit__(self, *args):
        return False


class ArcPy(types.ModuleType):
    Parameter = Parameter

    def __init__(self, pro=False, status="Available"):
        types.ModuleType.__init__(self, "arcpy")
        self.env = Bag(workspace="user_workspace", overwriteOutput=False,
                       mask="user_mask", extent="user_extent", snapRaster="user_snap",
                       cellSize=123, outputCoordinateSystem="user_sr",
                       parallelProcessingFactor="75%", compression="NONE",
                       tileSize="256 256", pyramid="PYRAMIDS",
                       rasterStatistics="NONE", scratchWorkspace="user_scratch")
        if pro:
            self.mp = Bag()
        self.status = status
        self.calls = []
        self.messages = []
        self.deleted = []
        self.sr = Bag(name="Test Metres", type="Projected", factoryCode=3857)
        self.extent = Bag(XMin=0, YMin=0, XMax=10000, YMax=10000)
        self.management = Bag(Delete=lambda path: self.deleted.append(path),
                              CopyFeatures=lambda *a: None,
                              Project=lambda *a: None,
                              MakeFeatureLayer=lambda *a: None,
                              GetCount=lambda *a: [4])
        self.conversion = Bag(PolygonToRaster=lambda *a: self.calls.append("mask_raster"))
        self.Select_analysis = lambda *args: self.calls.append(("select", args))
        self.da = Bag(SearchCursor=lambda path, fields: Cursor(
            [("1996", "2025")] if fields == ["Data_Start", "Data_End"] else []))

    def ClearEnvironment(self, name):
        setattr(self.env, name, None)

    def CheckExtension(self, name):
        return self.status

    def CheckOutExtension(self, name):
        self.calls.append("checkout")
        return "CheckedOut"

    def CheckInExtension(self, name):
        self.calls.append("checkin")

    def Exists(self, path):
        return bool(path)

    def Describe(self, path):
        return Bag(spatialReference=self.sr, extent=self.extent, OIDFieldName="OBJECTID", shapeType="Point")

    def SpatialReference(self, *args):
        return self.sr

    def ValidateTableName(self, name, *args):
        return name

    def ListFields(self, path):
        return [Bag(name="T_Annual_Mean", type="Double"),
                Bag(name="Data_Start", type="String"), Bag(name="Data_End", type="String")]

    def GetCount_management(self, path):
        return [4]

    def AddMessage(self, text):
        self.messages.append(text)

    AddWarning = AddMessage
    AddError = AddMessage

    def SetProgressor(self, *args):
        pass

    SetProgressorPosition = SetProgressor
    SetProgressorLabel = SetProgressor
    ResetProgressor = SetProgressor

    def AddFieldDelimiters(self, path, field):
        return field


sys.modules["arcpy"] = ArcPy()


def load(name, path):
    if sys.version_info[0] >= 3:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(name, path).load_module()
    import imp
    return imp.load_source(name, path)


core = load("stability_core", os.path.join(ROOT, "MIRSAD_Climate_Atlas_Generator_10_8.pyt"))
import raster_atlas_generator as raster
stations = load("stability_stations", os.path.join(ROOT, "MIRSAD_Weather_Stations_Atlas_Generator.pyt"))
from utils.arcgis_runtime import SpatialLicense, preserve_arcpy_environment, provider_error, filegdb_raster_workspace


class Messages(object):
    def __init__(self):
        self.lines = []

    def addMessage(self, line):
        self.lines.append(line)

    addWarningMessage = addMessage
    addWarning = addMessage
    addErrorMessage = addMessage


class RuntimeStability(unittest.TestCase):
    def setUp(self):
        # All test writes are confined to a fresh workspace directory.
        logdir = os.path.join(ROOT, "tests", "logs")
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        self.tmp = tempfile.mkdtemp(prefix="runtime_", dir=logdir)
        self.assertTrue(os.path.abspath(self.tmp).startswith(os.path.abspath(logdir) + os.sep))
        self.fake = ArcPy()
        core.arcpy = raster.arcpy = stations.arcpy = stations._core.arcpy = self.fake
        self.saved_env = dict(self.fake.env.__dict__)
        self.original_guide = sys.modules.get("generate_master_atlas_excel")
        guide = types.ModuleType("generate_master_atlas_excel")
        def build(**kwargs):
            with open(kwargs["target_excel"], "wb") as handle:
                handle.write(b"test guide")
        guide.build_master_classification_workbook = build
        sys.modules["generate_master_atlas_excel"] = guide

    def tearDown(self):
        if self.original_guide is None:
            sys.modules.pop("generate_master_atlas_excel", None)
        else:
            sys.modules["generate_master_atlas_excel"] = self.original_guide
        shutil.rmtree(self.tmp)

    def params(self, tool, **values):
        params = tool.getParameterInfo()
        pd = dict((p.name, p) for p in params)
        for name, value in values.items():
            pd[name].value = value
        return params

    def test_desktop_license_ownership(self):
        lease = SpatialLicense(self.fake)
        lease.acquire()
        lease.release()
        lease.release()
        self.assertEqual(self.fake.calls, ["checkout", "checkin"])
        self.fake.calls = []
        self.fake.status = "CheckedOut"
        lease = SpatialLicense(self.fake)
        lease.acquire()
        lease.release()
        self.assertEqual(self.fake.calls, [])

    def test_pro_does_not_explicitly_checkout_or_checkin(self):
        fake = ArcPy(pro=True)
        lease = SpatialLicense(fake)
        lease.acquire()
        lease.release()
        self.assertEqual(fake.calls, [])

    def test_unavailable_license_rejected(self):
        self.fake.status = "Unavailable"
        with self.assertRaises(RuntimeError):
            SpatialLicense(self.fake).acquire()
        self.assertEqual(self.fake.calls, [])

    def prepare_core(self):
        tool = core.PowerClimateAtlasGenerator()
        self.logs = []
        tool._export_excel = lambda *a, **k: None
        tool._write_dictionaries = lambda *a, **k: None
        tool._run_qa = lambda *a, **k: {}
        tool._extract_points = lambda *a, **k: []
        tool._interpolate_all = lambda *a, **k: []
        tool._write_log = lambda path, info: self.logs.append(info)
        tool._cleanup = lambda *a, **k: None
        return tool

    def core_params(self, tool, **overrides):
        values = dict(Operation_Mode="Interpolate & Map Existing Data (Offline Mode - No Internet)",
                      Precalculated_Point_Layers="01_Temperature", Climate_Modules="Temperature",
                      Climate_Data_Source="NASA POWER API",
                      Output_Workspace=self.tmp, Study_Area_Name="Regression", Study_Area_Mask=None,
                      Temporal_Scope="Annual", Field_Filter_Scope="Annual Only",
                      Add_To_Map=False, Export_Shapefiles=False)
        values.update(overrides)
        return self.params(tool, **values)

    def test_offline_execute_finishes_and_logs_timings(self):
        tool = self.prepare_core()
        messages = Messages()
        # Real offline direct-layer mapping and execute control flow are exercised.
        tool.execute(self.core_params(tool), messages)
        self.assertEqual(len(self.logs), 1)
        self.assertTrue(self.logs[0]["start_time"])
        self.assertEqual(self.logs[0]["module_timings"], {})
        self.assertTrue(any("[DONE]" in line or "[COMPLETED WITH WARNINGS]" in line for line in messages.lines))
        self.assertEqual(self.fake.calls, ["checkout", "checkin"])
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_offline_failure_releases_license_and_restores_environment(self):
        tool = self.prepare_core()
        def fail(*args, **kwargs):
            raise ValueError("simulated cursor error")
        tool._merge_offline_layers = fail
        with self.assertRaises(ValueError):
            tool.execute(self.core_params(tool), Messages())
        self.assertEqual(self.fake.calls, ["checkout", "checkin"])
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_qa_failure_does_not_report_unqualified_success(self):
        tool=self.prepare_core()
        def failed_qa(element_fcs,paths,modules,registry,results,msg,warn,**kwargs):
            warn("QA FAIL: raster processing failures failed=1")
            return [("raster processing failures",False,"failed=1")]
        tool._run_qa=failed_qa
        messages=Messages()
        tool.execute(self.core_params(tool),messages)
        self.assertTrue(any("[COMPLETED WITH WARNINGS]" in line for line in messages.lines))
        self.assertFalse(any("[DONE]" in line for line in messages.lines))

    def test_large_raster_rejected_before_mask_allocation(self):
        tool = self.prepare_core()
        self.fake.extent.XMax = self.fake.extent.YMax = 1000000
        with self.assertRaises(RuntimeError):
            tool.execute(self.core_params(tool, Study_Area_Mask="mask", Base_Cell_Size="1 Meters"), Messages())
        self.assertNotIn("mask_raster", self.fake.calls)
        self.assertNotIn("checkout", self.fake.calls)
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_download_only_never_allocates_a_raster_mask(self):
        tool = self.prepare_core()
        tool._extract_points = lambda *a: [{"oid": 1, "lat": 30.0, "lon": 31.0, "Source_ID": 1}]
        tool._build_single_element_layer = lambda *a, **k: "01_Temperature"
        self.fake.extent.XMax = self.fake.extent.YMax = 1000000
        probe, fetch = core.probe_server, core.fetch_nasa_point
        core.probe_server = lambda *a, **k: None
        core.fetch_nasa_point = lambda lat, lon, y0, y1, params, **k: dict(
            (p, dict(("2025%02d" % month, 20.0) for month in range(1, 13))) for p in params)
        try:
            tool.execute(self.core_params(tool,
                         Operation_Mode="Download & Generate Atlas (Full Pipeline) [Default]",
                         Download_Only=True, Input_Point_Features="raw_points",
                         Study_Area_Mask="mask", Base_Cell_Size="1 Meters"), Messages())
        finally:
            core.probe_server, core.fetch_nasa_point = probe, fetch
        self.assertNotIn("mask_raster", self.fake.calls)
        self.assertNotIn("checkout", self.fake.calls)
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_raster_execute_exports_sources_and_preserves_host_memory(self):
        raster._HAS_SA = True
        tool = raster.RasterDataClimateAtlasGenerator()
        tool._merge_offline_layers = lambda *a, **k: ({"Temperature": "01_Temperature"}, {"Temperature": [("T_Annual_Mean", "Temperature")]})
        tool._process_single_module_outputs = lambda *a, **k: None
        tool._write_dictionaries = lambda *a, **k: None
        tool._write_log = lambda *a, **k: None
        captured = []
        original = raster.export_source_data_folder
        raster.export_source_data_folder = lambda *a, **k: captured.append((a, k))
        try:
            params = self.params(tool, Operation_Mode="Interpolate & Map Existing Data (Offline Mode - No Internet)",
                                 Precalculated_Point_Layers="01_Temperature", Final_Clip_Layer="mask",
                                 Climate_Modules="Temperature", Output_Workspace=self.tmp)
            tool.execute(params, Messages())
        finally:
            raster.export_source_data_folder = original
        self.assertEqual(captured[0][0][2], ["Temperature"])
        self.assertEqual(captured[0][1]["y0"], 1996)
        self.assertEqual(captured[0][1]["y1"], 2025)
        self.assertNotIn("in_memory", self.fake.deleted)
        self.assertEqual(self.fake.calls, ["checkout", "checkin"])
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_raster_exception_releases_extension(self):
        tool = raster.RasterDataClimateAtlasGenerator()
        def fail(parameters, messages, lease):
            lease.acquire()
            self.fake.env.cellSize = 999
            raise ValueError("simulated interpolation error")
        tool._execute = fail
        with self.assertRaises(ValueError):
            tool.execute([], Messages())
        self.assertEqual(self.fake.calls, ["checkout", "checkin"])
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_station_daily_proxy_preserves_altered(self):
        p = stations._ParamProxy("Save_Daily_Series", False, altered=True)
        self.assertTrue(p.altered)
        self.assertFalse(p.value)
        self.assertTrue(repr(p).startswith("_ParamProxy"))
        self.assertEqual(stations._ParamProxy("Study_Area_Name", u"مصر").valueAsText, u"مصر")

    def test_daily_execute_accepts_legacy_proxy_and_respects_export_choice(self):
        probe, fetch = core.probe_server, core.fetch_nasa_point
        core.probe_server = lambda *a, **k: None
        core.fetch_nasa_point = lambda lat, lon, y0, y1, params, **k: dict(
            (p, {"20240101": 20.0, "20240102": 21.0}) for p in params)
        cases = [
            # Older station toolboxes forward values without ArcPy's altered flag.
            (Bag(name="Save_Daily_Series", value=False, valueAsText="false"), True),
            (stations._ParamProxy("Save_Daily_Series", False), True),
            (stations._ParamProxy("Save_Daily_Series", False, altered=True), False),
            (stations._ParamProxy("Save_Daily_Series", True, altered=True), True),
        ]
        try:
            for daily_param, expected_daily in cases:
                tool = self.prepare_core()
                tool._extract_points = lambda *a: [{"oid": 1, "lat": 30.0, "lon": 31.0, "Source_ID": 1}]
                tool._build_single_element_layer = lambda *a, **k: "01_Temperature"
                daily_calls = []
                tool._build_daily_table = lambda *a, **k: daily_calls.append(True)
                params = self.core_params(tool,
                    Operation_Mode="Download & Generate Atlas (Full Pipeline) [Default]",
                    Execution_Workflow_Mode="Sequential Mode: Element by Element",
                    Download_Only=True, Input_Point_Features="raw_points",
                    Single_Year=2024, Temporal_Resolution="Daily")
                params = [daily_param if p.name == "Save_Daily_Series" else p for p in params]
                tool.execute(params, Messages())
                self.assertEqual(bool(daily_calls), expected_daily)
                self.assertEqual(len(self.logs), 1)
                self.assertEqual(self.fake.env.__dict__, self.saved_env)
        finally:
            core.probe_server, core.fetch_nasa_point = probe, fetch

    def test_station_daily_and_arabic_workflow_reach_core_unchanged(self):
        tool = stations.WeatherStationsAtlasGeneratorAR()
        params = self.params(tool, Output_Workspace=self.tmp,
                             Climate_Data_Source=u"واجهة ناسا (NASA POWER API)",
                             Temporal_Resolution="Daily", Save_Daily_Series=False,
                             Execution_Workflow_Mode=u"نمط تتابعي: معالجة عنصر بعنصر")
        pd = dict((p.name, p) for p in params)
        pd["Save_Daily_Series"].altered = True
        tool._resolve_stations = lambda *a, **k: [{"Station_ID": "test", "Lat": 30.0, "Lon": 31.0}]
        tool._write_stations_shapefile = lambda *a, **k: None
        tool._enrich_station_metadata = lambda *a, **k: None
        original = stations._core.PowerClimateAtlasGenerator.execute
        captured = []
        stations._core.PowerClimateAtlasGenerator.execute = lambda self, p, m: captured.extend(p)
        try:
            tool.execute(params, Messages())
        finally:
            stations._core.PowerClimateAtlasGenerator.execute = original
        forwarded = dict((p.name, p) for p in captured)
        self.assertTrue(forwarded["Save_Daily_Series"].altered)
        self.assertFalse(forwarded["Save_Daily_Series"].value)
        self.assertEqual(forwarded["Execution_Workflow_Mode"].value, "Sequential Mode: Element by Element")
        self.assertTrue(forwarded["Climate_Data_Source"].value.startswith("NASA POWER"))
        self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_yearly_option_reaches_download_pipeline_without_extra_requests(self):
        probe, fetch = core.probe_server, core.fetch_nasa_point
        core.probe_server = lambda *a, **k: None
        requests = []
        def cached_fetch(lat, lon, y0, y1, params, **kwargs):
            requests.append((y0, y1))
            return dict((p, dict(("%04d%02d01" % (year, month), float(year - 2000))
                                 for year in range(y0, y1 + 1) for month in range(1, 13))) for p in params)
        core.fetch_nasa_point = cached_fetch
        try:
            for workflow in ("Sequential Mode: Element by Element", "Batch Mode: Download All Then Process [Recommended]"):
                for separate, end in ((True, 2024), (False, 2024), (True, 2023)):
                    requests[:] = []
                    tool = self.prepare_core()
                    tool._extract_points = lambda *a: [{"oid": 1, "lat": 30.0, "lon": 31.0}]
                    tool._build_single_element_layer = lambda *a, **k: "01_Temperature"
                    exported = []
                    tool._export_excel = lambda fc, path, *a, **k: exported.append((path, k))
                    params = self.core_params(tool,
                        Operation_Mode="Download & Generate Atlas (Full Pipeline) [Default]",
                        Execution_Workflow_Mode=workflow, Download_Only=True,
                        Input_Point_Features="raw_points", Temporal_Resolution="Daily",
                        Time_Mode="Year Range", Start_Year=2023, End_Year=end,
                        Export_Separate_Years=separate)
                    tool.execute(params, Messages())
                    self.assertEqual(requests, [(2023, end)])
                    self.assertEqual(len(exported), 3 if separate and end == 2024 else 1)
                    for path, options in exported[1:]:
                        self.assertIn(os.sep + "Years" + os.sep, path)
                        self.assertIsNotNone(options["daily"])
                        self.assertIn("table", options)
        finally:
            core.probe_server, core.fetch_nasa_point = probe, fetch

    def test_station_defaults_use_an_implemented_source(self):
        for cls in (stations.WeatherStationsAtlasGenerator, stations.WeatherStationsAtlasGeneratorAR):
            pd = dict((p.name, p) for p in cls().getParameterInfo())
            self.assertIsNone(provider_error(pd["Climate_Data_Source"].valueAsText))
            self.assertIn("Precalculated_Point_Layers", pd)

    def test_provider_validation_clears_when_switching_to_offline(self):
        tool = raster.RasterDataClimateAtlasGenerator()
        params = self.params(tool, Climate_Data_Source="Copernicus CDS", Climate_Modules="Temperature")
        pd = dict((p.name, p) for p in params)
        tool.updateMessages(params)
        self.assertIsNotNone(pd["Climate_Data_Source"].error)
        pd["Operation_Mode"].value = "Interpolate & Map Existing Data (Offline Mode - No Internet)"
        pd["Precalculated_Point_Layers"].value = "existing_climate"
        tool.updateMessages(params)
        self.assertIsNone(pd["Climate_Data_Source"].error)

    def test_station_offline_bypasses_station_selection_in_both_languages(self):
        for cls, mode in [(stations.WeatherStationsAtlasGenerator, "Interpolate & Map Existing Data (Offline Mode - No Internet)"),
                          (stations.WeatherStationsAtlasGeneratorAR, u"استيفاء ورسم الخرائط لبيانات موجودة مسبقاً (وضع أوفلاين)")]:
            tool = cls()
            params = self.params(tool, Operation_Mode=mode, Precalculated_Point_Layers="existing_climate_points")
            captured = []
            original = stations._core.PowerClimateAtlasGenerator.execute
            stations._core.PowerClimateAtlasGenerator.execute = lambda self, p, m: captured.extend(p)
            tool._resolve_stations = lambda *a, **k: self.fail("Offline must not select stations")
            try:
                tool.execute(params, Messages())
            finally:
                stations._core.PowerClimateAtlasGenerator.execute = original
            pd = dict((p.name, p) for p in captured)
            self.assertEqual(pd["Precalculated_Point_Layers"].value, "existing_climate_points")
            self.assertEqual(self.fake.env.__dict__, self.saved_env)

    def test_unimplemented_providers_blocked_before_network(self):
        for source in ("NOAA Direct Observations Archive", "Copernicus Climate Data Store (CDS / ERA5 / AgERA5)"):
            self.assertIsNotNone(provider_error(source))
        self.assertIsNone(provider_error("Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling"))
        self.assertIsNone(provider_error("NASA POWER API"))
        self.assertIsNone(provider_error(u"واجهة أوبن-ميتيو (Open-Meteo ERA5 Reanalysis)"))
        with self.assertRaises(RuntimeError):
            raster.RasterDataClimateAtlasGenerator()._download_single_tile(
                "Copernicus CDS", "T2M", 0, 0, 1, 1, 2020, 2021,
                os.path.join(self.tmp, "must_not_exist.nc"), "", "", lambda x: None, lambda x: None,
                cds_key="TEST_ONLY_NOT_A_REAL_KEY")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "must_not_exist.nc")))

    def test_nonfinite_values_do_not_reach_aggregation(self):
        for mod in (core, raster):
            self.assertTrue(mod.is_missing(float("inf")))
            self.assertTrue(mod.is_missing(float("-inf")))
            self.assertTrue(mod.is_missing(float("nan")))
        self.assertEqual(core.safe_mean([float("inf"), 20.0, 30.0]), 25.0)

    def test_failed_mask_never_publishes_unclipped_surface(self):
        import weakref
        live = []
        class Surface(object):
            def save(self, path):
                pass
        def interpolate(*args):
            self.assertTrue(args[0].endswith(os.path.join("spatial_work.gdb", "pwr_atlas_interp")))
            obj = Surface()
            live.append(weakref.ref(obj))
            return obj
        def fail_mask(*args):
            raise ValueError("simulated invalid mask")
        sa = types.ModuleType("arcpy.sa")
        sa.ExtractByMask = fail_mask
        original_sa = sys.modules.get("arcpy.sa")
        sys.modules["arcpy.sa"] = sa
        self.fake.da.SearchCursor = lambda *a: Cursor([(20.0,), (21.0,), (22.0,), (23.0,)])
        self.fake.management.CopyRaster = lambda *a, **k: self.fail("Unclipped surface published")
        tool = core.PowerClimateAtlasGenerator()
        tool._interp_surface = interpolate
        warnings = []
        try:
            for raster_mask in (None, "mask_raster"):
                result = tool._interpolate_all(
                    "01_Temperature", ["Temperature"],
                    {"vec": os.path.join(self.tmp, "reports")}, 500, "IDW", "mask",
                    lambda x: None, warnings.append,
                    wanted_fields_by_module={"Temperature": ["T_Annual_Mean"]},
                    raster_mask=raster_mask)
                self.assertEqual(result, [])
                self.assertIsNone(live[-1]())
        finally:
            if original_sa is None:
                sys.modules.pop("arcpy.sa", None)
            else:
                sys.modules["arcpy.sa"] = original_sa
        self.assertTrue(all("unmasked output was not published" in w for w in warnings))
        self.assertEqual(len([call for call in self.fake.calls if isinstance(call,tuple) and call[0]=="select" and call[1][2]=="T_Annual_Mean IS NOT NULL"]),2)

    def test_temporary_rasters_use_filegdb_and_restore_host_after_failure(self):
        old=globals().get("arcpy");globals()["arcpy"]=self.fake
        original=dict(workspace=getattr(self.fake.env,"workspace",None),scratchWorkspace=getattr(self.fake.env,"scratchWorkspace",None))
        @filegdb_raster_workspace
        def calculate(owner,out_tif,fail=False):
            self.assertTrue(self.fake.env.workspace.endswith("spatial_work.gdb"))
            self.assertEqual(self.fake.env.workspace,self.fake.env.scratchWorkspace)
            if fail:raise ValueError("expected processing failure")
            return "raster"
        try:
            target=os.path.join(self.tmp,"spaced output.tif")
            self.assertEqual(calculate(self,target),"raster")
            with self.assertRaises(ValueError):calculate(self,target,fail=True)
            self.assertEqual(dict((key,getattr(self.fake.env,key)) for key in original),original)
        finally:
            if old is None:globals().pop("arcpy",None)
            else:globals()["arcpy"]=old

    def test_raster_failure_cannot_pass_empty_registry_qa(self):
        checks=core.PowerClimateAtlasGenerator()._run_qa(
            {},{"vec":self.tmp},[],[],{},lambda text:None,lambda text:None,
            raster_failures=["Raster T_Annual_Mean failed: native error"])
        failed=[check for check in checks if check[0]=="raster processing failures"]
        self.assertEqual(failed,[("raster processing failures",False,"failed=1")])


if __name__ == "__main__":
    unittest.main()
