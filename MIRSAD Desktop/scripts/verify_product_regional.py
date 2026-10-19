# -*- coding: utf-8 -*-
"""Small native CHIRPS AOI acceptance, usable on Python 2.7 and Python 3."""
from __future__ import print_function
import argparse
import datetime as dt
import io
import json
import os
import sys
import time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=os.path.dirname(ROOT)
sys.path.insert(0,REPO)
parser=argparse.ArgumentParser();parser.add_argument('--arcgis',action='store_true');parser.add_argument('--annual',action='store_true');args=parser.parse_args()
out=os.path.join(ROOT,'.test-output','regional-products','run-'+str(int(time.time()*1000)))
os.makedirs(out)
from utils.climate_products import CHIRPS
if not args.arcgis:
    sys.path.insert(0,os.path.join(ROOT,'src'))
    from shapely.geometry import box,mapping
    from mirsad_desktop.regional import run_regional_project
    output,report=run_regional_project(out,'NativeCells',{},mapping(box(-70.05,-4.05,-69.95,-3.95)),None,
        '2024-01-01','2024-01-31',['Precipitation'],provider=CHIRPS,gap_method='none',progress=lambda e:print(e,flush=True))
    assert report['processing']['native_grid_cells']==4,report
    assert not any(e.get('stage') in ('filegdb','geopackage') for e in report['errors']),report
    import pyogrio
    meta,_,geometry,arrays=pyogrio.raw.read(output/'Project.gpkg',layer='Precipitation',columns=['R_January_Mean'])
    assert len(geometry)==4
    assert all(100<float(v)<600 for v in arrays[0]),arrays
    result=dict(passed=True,output=str(output),native_cells=4,precipitation=list(map(float,arrays[0])))
else:
    print('Importing native ArcGIS runtime');sys.stdout.flush()
    import arcpy
    toolbox_path=os.path.join(REPO,'MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt')
    if sys.version_info[0]>=3:
        import importlib.machinery
        import importlib.util
        loader=importlib.machinery.SourceFileLoader('regional_product_native_acceptance',toolbox_path)
        spec=importlib.util.spec_from_loader(loader.name,loader)
        module=importlib.util.module_from_spec(spec);loader.exec_module(module)
    else:
        import imp
        module=imp.load_source('regional_product_native_acceptance',toolbox_path)
    aoi=os.path.join(out,'aoi.shp');sr=arcpy.SpatialReference(4326)
    arcpy.CreateFeatureclass_management(out,'aoi.shp','POLYGON',spatial_reference=sr)
    geometry=arcpy.Polygon(arcpy.Array([arcpy.Point(x,y) for x,y in [(-70.05,-4.05),(-69.95,-4.05),(-69.95,-3.95),(-70.05,-3.95),(-70.05,-4.05)]]),sr)
    with arcpy.da.InsertCursor(aoi,['SHAPE@']) as cursor:cursor.insertRow([geometry])
    tool=module.RasterDataClimateAtlasGenerator();parameters=tool.getParameterInfo()
    values=dict(Download_Extent_Layer=aoi,Final_Clip_Layer=aoi,Output_Workspace=os.path.join(out,'Atlas'),Climate_Data_Source=CHIRPS,
        Climate_Modules='Precipitation',Time_Mode='Custom Date Range',Start_Date=dt.datetime(2024,1,1),End_Date=dt.datetime(2024,1,31),
        Output_Spatial_Reference=arcpy.SpatialReference(32719),Output_Cell_Size=5000)
    if args.annual:values['End_Date']=dt.datetime(2024,12,31)
    for parameter in parameters:
        if parameter.name in values:parameter.value=values[parameter.name]
    class Messages(object):
        def addMessage(self,text):print(text)
        def addWarningMessage(self,text):print(text)
        def addWarning(self,text):print(text)
        def addErrorMessage(self,text):print(text)
    tool.execute(parameters,Messages())
    readback=[]
    for path,dirs,files in os.walk(out):
        for directory in dirs:
            if not directory.endswith('.gdb'):continue
            for folder,subfolders,layers in arcpy.da.Walk(os.path.join(path,directory),datatype='FeatureClass'):
                for layer in layers:
                    feature=os.path.join(folder,layer);fields=[f.name for f in arcpy.ListFields(feature)]
                    if 'R_January_Mean' in fields:
                        values0=[row[0] for row in arcpy.da.SearchCursor(feature,['R_January_Mean'])]
                        assert len(values0)==4 and all(v is not None and 100<v<600 for v in values0),values0
                        readback.append(values0)
    assert readback,'No native precipitation feature class read back'
    if args.annual:
        rasters=[os.path.join(path,name) for path,dirs,files in os.walk(out) for name in files if name.lower().endswith('.tif')]
        assert rasters,'No annual source raster generated'
        assert any(float(arcpy.GetRasterProperties_management(path,'MAXIMUM')[0])>0 for path in rasters),rasters
    result=dict(passed=True,output=out,native_cells=4,precipitation=readback,runtime=arcpy.GetInstallInfo())
with io.open(os.path.join(out,'acceptance.json'),'w',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False,indent=2))
print('REGIONAL PRODUCT PASSED',result)
