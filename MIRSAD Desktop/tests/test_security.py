import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.validation import local_dataset
from mirsad_desktop.inputs import import_points,make_point
from mirsad_desktop.jobs import run_request,inspect_dataset

class InputSecurityTests(unittest.TestCase):
    def setUp(self):
        (ROOT/".test-output").mkdir(exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=ROOT/".test-output");self.folder=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_remote_virtual_files_scripts_and_duplicate_sites_are_rejected(self):
        for name in ("https://example.com/file.gpkg","/vsicurl/https://example.com/map.tif"):
            with self.assertRaises(ValueError):local_dataset(name)
        script=self.folder/"input.py";script.write_text("raise RuntimeError('not data')")
        with self.assertRaises(ValueError):local_dataset(script)
        csv=self.folder/"duplicate.csv";csv.write_text("id,x,y\n001,31,30\n001,31,30\n")
        with self.assertRaisesRegex(ValueError,"Duplicate"):import_points(csv,"x","y","id")
    def test_worker_rejects_unknown_operations_and_journals_error(self):
        request=self.folder/"request.json";request.write_text(json.dumps({"operation":"run_shell","command":"anything"}))
        self.assertEqual(run_request(request),2)
        self.assertEqual(json.loads((self.folder/"state.json").read_text())["status"],"failed")
        self.assertIn("Unsupported job",(self.folder/"error.txt").read_text())
    def test_add_data_reads_project_layers_and_geotiff_in_bounded_worker(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin
        from mirsad_desktop.exports import export_project
        points=[make_point("001","My point",31.2,30)]
        output,manifest=export_project(points,self.folder,"Dataset",{})
        info=inspect_dataset(output/"Project.gpkg",self.folder)
        self.assertEqual(info["kind"],"layers")
        point_info=inspect_dataset(output/"Project.gpkg",self.folder,"Stations")
        self.assertEqual(point_info["kind"],"point_mapping");self.assertEqual(point_info["features"],1)
        raster=self.folder/"input.tif"
        with rasterio.open(raster,"w",driver="GTiff",width=10,height=10,count=1,dtype="float32",crs="EPSG:32636",transform=from_origin(320000,3330000,100,100)) as target:
            target.write(np.arange(100,dtype="float32").reshape(10,10),1)
        preview=inspect_dataset(raster,self.folder)
        self.assertEqual(preview["kind"],"raster");self.assertTrue(Path(preview["preview"]).is_file())
        self.assertLess(preview["bounds"][0],preview["bounds"][2])

    def test_point_import_keeps_source_crs_metadata_without_changing_geometry(self):
        import hashlib
        from mirsad_desktop.exports import export_project
        from mirsad_desktop.jobs import execute
        point=make_point("0007","Projected source",31.2,30)
        output,_=export_project([point],self.folder,"Projected",{},crs="EPSG:32636")
        path=output/"Project.gpkg";before=hashlib.sha256(path.read_bytes()).hexdigest()
        # File CRS takes priority over an erroneous supplied fallback.
        result=execute(dict(operation="import_points",options=dict(path=str(path),layer="Stations",source_crs="EPSG:4326")),
                       self.folder,lambda update:None,lambda:False)
        self.assertEqual(result["crs"],"EPSG:32636")
        self.assertAlmostEqual(result["points"][0]["longitude"],31.2,places=7)
        self.assertAlmostEqual(result["points"][0]["latitude"],30,places=7)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
        csv=self.folder/"projected.csv";csv.write_text("id,x,y\n0007,500000,0\n",encoding="utf-8")
        result=execute(dict(operation="import_points",options=dict(path=str(csv),x_field="x",y_field="y",id_field="id",source_crs="EPSG:32636")),
                       self.folder,lambda update:None,lambda:False)
        self.assertEqual(result["crs"],"EPSG:32636")
        self.assertAlmostEqual(result["points"][0]["longitude"],33,places=7)
        self.assertEqual(result["points"][0]["usaf"],"0007")

if __name__=="__main__":unittest.main()
