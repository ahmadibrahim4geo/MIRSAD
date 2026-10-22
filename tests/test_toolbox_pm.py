# -*- coding: utf-8 -*-
"""Independent FAO example, daily accumulation and ET method isolation."""
from __future__ import unicode_literals
import copy
import datetime as dt
import os
import shutil
import sys
import tempfile
import types
import unittest
import test_runtime_stability as support
from mirsad_core import toolbox_pm as pm, toolbox_enrichment as e


def fixture(start, end):
    point = dict(oid=7, station_id="001234", station_name="مرجع Uccle", country="BE", lat=50.8, lon=4.35,
                 calculation_elevation=100.)
    # FAO56 chapter 4 example18, 6 July; values are canonical daily units.
    raw = dict(T2M_MAX=21.5, T2M_MIN=12.3, RH2M_MAX=84., RH2M_MIN=63.,
               WS10M_CONFIRMED=10./3.6, ALLSKY_SFC_SW_DWN=22.07)
    return point, dict(series=dict((p, dict((str(start+dt.timedelta(days=i)), value) for i in range((end-start).days+1)))
                                   for p, value in raw.items()), source_summary="Open-Meteo fixture", provenance={}, status="OK")


class ToolboxPM(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pm_", dir=os.path.join(support.ROOT, "tests", "logs"))
        self.fake = support.ArcPy();support.core.arcpy = self.fake

    def tearDown(self):shutil.rmtree(self.tmp)

    def test_fao_example18_and_no_legacy_input_mutation(self):
        day = dt.date(2001, 7, 6);point, source = fixture(day, day);before = copy.deepcopy((point, source))
        result = pm.calculate(point, source, day, day)
        self.assertAlmostEqual(result["daily"][day], 3.88, delta=.03)
        self.assertEqual(result["fields"]["ET_PM_Valid_Days"], 1)
        self.assertIsNone(result["fields"]["ET_PM_July_Mean"])
        self.assertEqual(result["provenance"][0]["pressure_method"], "FAO56_eq7_known_elevation")
        self.assertEqual(result["provenance"][0]["ea_method"], "FAO56_eq17_RH_extrema")
        self.assertEqual((point, source), before)

    def test_surface_pressure_first_and_missing_elevation_is_never_default_zero(self):
        day = dt.date(2001, 7, 6);point, source = fixture(day, day)
        source["series"]["PS"] = {str(day): 100.}
        result = pm.calculate(point, source, day, day)
        self.assertEqual(result["provenance"][0]["pressure_method"], "source_surface_pressure")
        point["calculation_elevation"] = None
        result = pm.calculate(point, source, day, day)
        self.assertFalse(result["daily"])
        self.assertEqual(result["status"], "NO_DATA")
        point["calculation_elevation"] = 0.
        self.assertTrue(pm.calculate(point, source, day, day)["daily"])

    def test_daily_sums_annual_year_average_and_missing_leap_day(self):
        start, end = dt.date(2023, 1, 1), dt.date(2024, 12, 31)
        values = dict((start+dt.timedelta(days=i), 2.) for i in range(731))
        fields = e.summarize(values, start, end, "ET_PM", ranges=True, accumulation=True)
        self.assertEqual(fields["ET_PM_Annual_Mean"], 731.)
        self.assertEqual(fields["ET_PM_February_Mean"], 57.)
        self.assertEqual(fields["ET_PM_February_Range"], 2.)
        values.pop(dt.date(2024, 2, 29))
        missing = e.summarize(values, start, end, "ET_PM", ranges=True, accumulation=True)
        self.assertEqual(missing["ET_PM_Annual_Mean"], 730.)
        self.assertIsNone(missing["ET_PM_February_Range"])
        self.assertEqual(missing["ET_PM_Valid_Days"], 730)

    def test_inches_and_daily_dictionary_are_independent_from_component_units(self):
        start, end = dt.date(2001, 7, 1), dt.date(2001, 7, 31)
        point, source = fixture(start, end)
        metric = pm.calculate(point, source, start, end)
        imperial = pm.calculate(point, source, start, end, precipitation_unit="Inches (in)")
        self.assertAlmostEqual(metric["fields"]["ET_PM_July_Mean"]/25.4, imperial["fields"]["ET_PM_July_Mean"])
        point["pm"] = imperial
        sheets = pm.sheets([point], start, end, ["ET_PM_July_Mean", "ET_PM_Annual_Range"], "Inches (in)")
        try:
            dictionary = dict((row[1], row) for row in sheets[0][2])
            self.assertEqual(dictionary["ET0_PM"][5], "inches/day")
            self.assertEqual(dictionary["ET_PM_Annual_Range"][5], "inches/month")
            self.assertEqual(dictionary["ET_PM_July_Mean"][5], "inches/month")
        finally:
            for sheet in sheets:
                if hasattr(sheet[2], "close"):sheet[2].close()

    def test_default_hg_parent_daily_and_raster_subset_contracts(self):
        p = support.Parameter(name=pm.METHODS_PARAMETER);r = support.Parameter(name=pm.RASTERS_PARAMETER)
        pd = {p.name:p, r.name:r};p.value="HG";r.value="HG"
        self.assertEqual(pm.selected(pd,["Evapotranspiration"],"Monthly",False,"NASA POWER"),(["HG"],["HG"]))
        p.value="PM";r.value=None
        self.assertEqual(pm.selected(pd,["Evapotranspiration"],"Daily",False,"NASA POWER"),(["PM"],[]))
        for modules, temporal, offline, provider in (([],"Daily",False,"NASA POWER"), (["Evapotranspiration"],"Monthly",False,"NASA POWER"),
                (["Evapotranspiration"],"Daily",True,"NASA POWER"), (["Evapotranspiration"],"Daily",False,"NOAA GSOD (Station Observations Only)")):
            with self.assertRaises(ValueError):pm.selected(pd,modules,temporal,offline,provider)
        p.value="HG";r.value="PM"
        with self.assertRaises(ValueError):pm.selected(pd,["Evapotranspiration"],"Daily",False,"NASA POWER")

    def test_invalid_hourly_input_rejected_without_mutating_source(self):
        day = dt.date(2001, 7, 6);point, source = fixture(day, day)
        source["processing_by_variable"] = {"WS10M_CONFIRMED": {str(day): dict(status="incomplete",valid_samples=23,expected_samples=24)}}
        before = copy.deepcopy(source)
        result = pm.calculate(point,source,day,day)
        self.assertFalse(result["daily"])
        self.assertEqual(source,before)
        self.assertIn("U2",result["provenance"][0]["missing_components"])

    def test_daily_table_arabic_and_distinct_raster_routes(self):
        day=dt.date(2001,7,6);point,source=fixture(day,day);point["pm"]=pm.calculate(point,source,day,day)
        package=pm.daily_table([point],day,day)
        try:
            row=list(package["rows"])[0]
            self.assertEqual(row[2:4],["001234","مرجع Uccle"])
            self.assertAlmostEqual(row[-1],3.88,delta=.03)
        finally:package["rows"].close()
        tool=support.core.PowerClimateAtlasGenerator();tool._et_methods=["HG","PM"]
        hg=tool._raster_paths(self.tmp,"Evapotranspiration","ET_Annual_Mean")[0]
        penman=tool._raster_paths(self.tmp,pm.PM_PRODUCT,"ET_PM_Annual_Mean")[0]
        self.assertIn("Hargreaves",hg);self.assertIn("Penman_Monteith",penman)
        self.assertNotEqual(hg,penman)
        tool._et_methods=["HG"]
        self.assertNotIn("Hargreaves",tool._raster_paths(self.tmp,"Evapotranspiration","ET_Annual_Mean")[0])

    def test_only_selected_method_reaches_interpolation_and_coverage_is_tabular(self):
        core=support.core;tool=core.PowerClimateAtlasGenerator();tool._et_raster_methods=["PM"]
        self.fake.da.SearchCursor=lambda path,fields:support.Cursor([tuple(2. for field in fields)]*4)
        self.fake.ListFields=lambda path:[support.Bag(name="ET_PM_Annual_Mean")]
        reached=[]
        def surface(layer,field,*args):
            reached.append(field);raise RuntimeError("intentional stop after verifying interpolation dispatch")
        tool._interp_surface=surface
        sa=types.ModuleType(str("arcpy.sa"));sa.ExtractByMask=lambda *args:None
        previous=sys.modules.get("arcpy.sa");sys.modules["arcpy.sa"]=sa
        try:
            tool._interpolate_all(None,["Evapotranspiration",pm.PM_PRODUCT],dict(vec=os.path.join(self.tmp,"Tables")),1000.,"IDW",None,
                lambda text:None,lambda text:None,scratch=os.path.join(self.tmp,"scratch"),
                source_by_module={"Evapotranspiration":"hg",pm.PM_PRODUCT:"pm"},
                wanted_fields_by_module={"Evapotranspiration":["ET_Annual_Mean"],pm.PM_PRODUCT:["ET_PM_Annual_Mean","ET_PM_Valid_Days"]})
        finally:
            if previous is None:sys.modules.pop("arcpy.sa",None)
            else:sys.modules["arcpy.sa"]=previous
        self.assertEqual(reached,["ET_PM_Annual_Mean"])

    @unittest.skipIf(sys.version_info[0]<3,"Actual openpyxl readback uses the independent Python 3 runtime")
    def test_yearly_pm_recomputes_sums_with_own_daily_and_dictionary(self):
        import openpyxl
        start,end=dt.date(2000,7,1),dt.date(2001,7,31);point,source=fixture(start,end)
        point.update(monthly={},daily_raw={},fields={},status="OK")
        point["pm"]=pm.calculate(point,source,start,end)
        original=copy.deepcopy(point)
        meta=dict(y0=2000,y1=2001,temporal="Daily",provider="Open-Meteo ERA5 (Standalone - No NASA Supplement)",
            gap_method="none",pm_start=str(start),pm_end=str(end),request_start=str(start),request_end=str(end),
            unit_precip="Millimeters (mm)")
        warnings=[]
        support.core.PowerClimateAtlasGenerator()._export_yearly_excel([point],[2000,2001],pm.PM_PRODUCT,self.tmp,meta,
            lambda text:None,warnings.append,save_daily=True,wanted_fields=["ET_PM_July_Mean","ET_PM_Valid_Days"])
        self.assertFalse(warnings,warnings)
        for year in (2000,2001):
            book=openpyxl.load_workbook(os.path.join(self.tmp,pm.PM_PRODUCT+"_%d.xlsx"%year),read_only=True)
            try:
                rows=list(book["Daily"].values);header=rows[0];data=rows[1:]
                self.assertTrue(all(str(row[header.index("Date")]).startswith(str(year)) for row in data))
                july=sum(row[-1] for row in data if str(row[header.index("Date")])[5:7]=="07")
                month=list(book["Month"].values)
                self.assertAlmostEqual(month[1][month[0].index("ET_PM_July_Mean")],july)
                self.assertIn("Field_Dictionary",book.sheetnames)
            finally:book.close()
        self.assertEqual(point,original)

    @unittest.skipIf(sys.version_info[0]<3,"Desktop parity uses Python 3")
    def test_desktop_accumulation_parity(self):
        sys.path.insert(0,os.path.join(support.ROOT,"MIRSAD Desktop","src"))
        from mirsad_desktop.enrichment import summarize
        start,end=dt.date(2023,1,1),dt.date(2024,12,31)
        values=dict((start+dt.timedelta(days=i),float(i%13)-2.) for i in range(731));values.pop(dt.date(2024,2,29))
        self.assertEqual(e.summarize(values,start,end,"ET_PM",ranges=True,accumulation=True),
                         summarize(values,start,end,"ET_PM",ranges=True,accumulation=True))


if __name__ == "__main__":unittest.main()
