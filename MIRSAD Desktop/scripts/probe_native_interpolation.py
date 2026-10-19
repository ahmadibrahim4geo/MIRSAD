"""Read-only input probing of Spatial Analyst's space-containing path failure."""
from pathlib import Path
import tempfile
import shutil
import json
import arcpy
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.test-output/regional-products/run-1792330989374/Atlas/Climate_Database_From_20240101_To_20241231.gdb/Precipitation'
target=ROOT/'.test-output/native-interpolation-probe';target.mkdir(exist_ok=True)
short=Path(tempfile.mkdtemp(prefix='mirsad_sa_probe_'))
cases=[]
try:
    arcpy.env.parallelProcessingFactor='0'
    arcpy.env.overwriteOutput=True
    arcpy.env.outputCoordinateSystem=arcpy.SpatialReference(32719)
    arcpy.ClearEnvironment('mask');arcpy.ClearEnvironment('extent')
    database=target/'working.gdb'
    if not arcpy.Exists(str(database)):arcpy.CreateFileGDB_management(str(target),database.name)
    mask=str(source.parent/'aoi_Boundary')
    arcpy.management.MakeFeatureLayer(str(source),'probe_points','R_Annual_Mean IS NOT NULL')
    for name,points,extent in (('feature_no_extent',str(source),None),('layer_no_extent','probe_points',None),('feature_path_extent',str(source),mask),('layer_path_extent','probe_points',mask),('layer_numeric_extent','probe_points',arcpy.Describe(mask).extent)):
        try:
            arcpy.env.workspace=str(database);arcpy.env.scratchWorkspace=str(database)
            if extent is None:arcpy.ClearEnvironment('extent')
            else:arcpy.env.extent=extent
            raster=arcpy.sa.Idw(points,'R_Annual_Mean',5000,2.,arcpy.sa.RadiusVariable(12))
            raster.save(str(target/(name+'.tif')))
            cases.append(dict(case=name,passed=True))
        except Exception as exc:cases.append(dict(case=name,passed=False,error=str(exc)))
        print(json.dumps(cases[-1]),flush=True)
finally:
    arcpy.Delete_management('probe_points')
    arcpy.ClearEnvironment('workspace');arcpy.ClearEnvironment('scratchWorkspace')
    shutil.rmtree(short,ignore_errors=True)
(target/'report.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
