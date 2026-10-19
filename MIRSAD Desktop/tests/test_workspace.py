import datetime as dt
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.inputs import import_points,make_point,grid_points,filter_boundary
from mirsad_desktop.exports import export_project
from mirsad_desktop.registry import MODULES
from mirsad_desktop.climate import prepare_outputs

class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        (ROOT/".test-output").mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/".test-output");self.folder=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()

    def test_user_csv_projected_coordinates_and_dual_export_readback(self):
        from pyproj import Transformer
        x,y=Transformer.from_crs(4326,32636,always_xy=True).transform(31.2357,30.0444)
        path=self.folder/"points.csv";path.write_text("ID,Name,E,N,T_Annual_Mean\n001,محطتي,%s,%s,25\n"%(x,y),encoding="utf-8")
        points=import_points(path,"E","N","ID","Name","EPSG:32636")
        self.assertEqual(points[0]["usaf"],"001");self.assertEqual(points[0]["name"],"محطتي")
        self.assertAlmostEqual(points[0]["longitude"],31.2357,places=6)
        self.assertEqual(points[0]["attributes"]["T_Annual_Mean"],"25")
        output,manifest=export_project(points,self.folder,"Projected",{},crs="EPSG:32636")
        self.assertEqual(manifest["status"],"complete",manifest["errors"])
        for name in ("Project.gdb","Project.gpkg"):
            self.assertEqual(manifest["outputs"][name][0]["crs"],"EPSG:32636")
        with self.assertRaises(ValueError):make_point("x","x",1e9,1e9)

    def test_all_nineteen_scientific_groups_have_real_outputs_and_units(self):
        point=make_point("P1","Test",31,30)
        start,end=dt.date(2024,1,1),dt.date(2024,12,31)
        constants={"T2M":25,"T2M_MAX":30,"T2M_MIN":20,"TS":28,"PRECTOTCORR":1,"SLP":101.3,"PS":100,
                   "WS10M":5,"WD10M":350,"RH2M":60,"T2MDEW":15,"ALLSKY_SFC_SW_DWN":18,"ALLSKY_SFC_UV_INDEX":2,"CLOUD_AMT":40}
        series={key:{start+dt.timedelta(days=i):value for i in range(366)} for key,value in constants.items()}
        result=[dict(station=point,series=series,status="OK",error="")]
        layers,daily=prepare_outputs(result,[m.name for m in MODULES],start,end,"NASA POWER")
        self.assertEqual(len(layers),19)
        self.assertAlmostEqual(layers["Surface Pressure"][0]["properties"]["PS_Annual_Mean"],1000)
        self.assertAlmostEqual(layers["Solar Radiation"][0]["properties"]["Sol_Annual_Mean"],5)
        self.assertEqual(layers["Precipitation"][0]["properties"]["R_Annual_Mean"],366)
        self.assertEqual(layers["Land Surface Temperature"][0]["properties"]["LST_minus_T_Annual"],3)
        self.assertIsNotNone(layers["UNEP Aridity"][0]["properties"]["UNEP_Aridity_Annual"])
        self.assertIsNone(layers["Trends & Anomalies"][0]["properties"]["T_Annual_Trend_Decade"])
        for module,records in layers.items():self.assertEqual(records[0]["properties"]["Coverage_Fraction"],1,module)

    def test_trend_and_baseline_need_sufficient_years_and_imperial_deltas(self):
        from mirsad_desktop.science import compute_point_fields
        monthly={"T2M":{(y,m):25+.2*(y-1991) for y in range(1991,2025) for m in range(1,13)},
                 "PRECTOTCORR":{(y,m):10 for y in range(1991,2025) for m in range(1,13)}}
        values=compute_point_fields(monthly,list(range(1991,2025)),["Trends & Anomalies"],"Daily",precip_totals=True,gap_method="none")
        self.assertAlmostEqual(values["T_Annual_Trend_Decade"],2,places=5)
        self.assertAlmostEqual(values["T_Annual_Anom"],2.8,places=5)
        point=make_point("P","P",31,30);start,end=dt.date(2024,1,1),dt.date(2024,12,31)
        series={p:{start+dt.timedelta(days=i):v for i in range(366)} for p,v in {"TS":28,"T2M":25}.items()}
        layers,_=prepare_outputs([dict(station=point,series=series,status="OK",error="")],["Land Surface Temperature"],start,end,"NASA POWER",units="Imperial")
        self.assertAlmostEqual(layers["Land Surface Temperature"][0]["properties"]["LST_minus_T_Annual"],5.4)

    def test_all_interpolation_methods_and_real_clipped_geotiff_pdf(self):
        import numpy as np
        import rasterio
        from shapely import box
        from mirsad_desktop.analysis import interpolate,METHODS,run_existing_project
        xy=np.array([[0,0],[1000,0],[0,1000],[1000,1000],[500,500]],float)
        values=np.array([10,10,10,10,10],float)
        for method in METHODS:
            estimate=interpolate(xy,values,[[400,450]],method)[0]
            self.assertAlmostEqual(estimate,10,places=6,msg=method)
        points=[make_point(str(i),str(i),31+x/100000,30+y/100000,attributes={"T_Annual_Mean":float(i+20)}) for i,(x,y) in enumerate(xy)]
        boundary=box(30.998,29.998,31.012,30.012)
        output,manifest=run_existing_project(points,self.folder,"Atlas",{},["T_Annual_Mean"],cell_size=200,crs="EPSG:32636",boundary=boundary)
        self.assertEqual(manifest["status"],"complete",manifest["errors"])
        tif=next((output/"Atlas").glob("*.tif"))
        with rasterio.open(tif) as dataset:
            self.assertEqual(dataset.crs.to_epsg(),32636);self.assertEqual(dataset.nodata,-9999)
            self.assertGreater(np.count_nonzero(dataset.read(1)!=-9999),0)
        pdf=output/"Atlas/MIRSAD_Climate_Atlas.pdf";self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
        self.assertTrue(filter_boundary(points,boundary))
        self.assertTrue(grid_points(boundary,500,"EPSG:32636"))

if __name__=="__main__":unittest.main()
