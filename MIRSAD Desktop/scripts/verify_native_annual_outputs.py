"""Independently read the native ArcGIS annual CHIRPS fixture with GDAL.

Read-only to project outputs. QA report belongs beside the acceptance fixture.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pyogrio
import rasterio

parser=argparse.ArgumentParser()
parser.add_argument('acceptance',type=Path)
args=parser.parse_args()
acceptance=json.loads(args.acceptance.read_text(encoding='utf-8'))
assert acceptance['passed']
project=Path(acceptance['output'])/'Atlas'
database=next(project.glob('Climate_Database_*.gdb'))
months=['January','February','March','April','May','June','July','August','September','October','November','December']
fields=['R_Annual_Mean']+['R_'+month+'_Mean' for month in months]+['Point_Lat','Point_Lon']
metadata,_,geometry,arrays=pyogrio.raw.read(database,layer='Precipitation',columns=fields)
by_name=dict(zip(metadata['fields'],arrays))
arrays=[by_name[field] for field in fields]
assert len(geometry)==4
assert all(np.isfinite(values).all() for values in arrays)
sources={}
for path in (project/'Source Data/Products').glob('*-product-summary.json'):
    source=json.loads(path.read_text(encoding='utf-8'))
    station=source['station']
    values=source['native_monthly']['PRECTOTCORR']
    assert len(values)==12
    sources[(round(station['latitude'],6),round(station['longitude'],6))]=values
for index,(latitude,longitude) in enumerate(zip(arrays[-2],arrays[-1])):
    raw=sources[(round(float(latitude),6),round(float(longitude),6))]
    # Annual fields retain native precision; monthly display fields are rounded
    # to 2 decimals by the existing export contract. Compare each independently.
    np.testing.assert_allclose(arrays[0][index],sum(raw.values()),rtol=0,atol=1e-6)
    np.testing.assert_allclose([array[index] for array in arrays[1:13]],
        [round(raw['2024-%02d'%month],2) for month in range(1,13)],rtol=0,atol=1e-9)
rasters=[]
expected={'R_Annual_Mean','R_Annual_Range','R_Winter_Mean','R_Spring_Mean','R_Summer_Mean','R_Autumn_Mean'}
paths=sorted((project/'03_Precipitation').glob('*.tif'))
assert {path.stem for path in paths}==expected
for path in paths:
    with rasterio.open(path) as raster:
        values=raster.read(1,masked=True).compressed()
        assert raster.crs.to_epsg()==32719
        assert raster.res==(5000.,5000.)
        assert values.size and np.isfinite(values).all() and values.min()>=0
        if path.stem!='R_Annual_Range':assert values.max()>0
        rasters.append(dict(name=path.name,crs=raster.crs.to_string(),resolution=list(raster.res),
            cells=int(values.size),minimum=float(values.min()),maximum=float(values.max()),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
report=dict(passed=True,reader='Independent GDAL/rasterio and pyogrio',native_acceptance=str(args.acceptance),
    annual_precipitation_mm=list(map(float,arrays[0])),annual_equals_sum_of_twelve_raw_native_months=True,
    monthly_export_rounding_decimals=2,rasters=rasters)
target=args.acceptance.parent/'annual_raster_readback.json'
target.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(target)
print(json.dumps(report,indent=2))
