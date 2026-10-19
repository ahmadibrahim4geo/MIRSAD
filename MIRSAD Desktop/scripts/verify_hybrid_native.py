"""Native Pro: preserve USAF/WBAN through temporary station GIS input and run Hybrid."""
import datetime as dt
import importlib.machinery
import json
from pathlib import Path
import sys
import time
import arcpy
import argparse

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
sys.path.insert(0,str(REPO))
from utils.station_catalogue import load_shared_catalogue
from utils.climate_sources import NOAA_ONLY,ERA5_ONLY,ERA5_MODELS
from utils.climate_products import CHIRPS,TERRA,CHELSA
parser=argparse.ArgumentParser()
parser.add_argument("--provider",choices=("hybrid","noaa","era5","chirps","terra","chelsa"),default="hybrid")
args=parser.parse_args()
stations_module=importlib.machinery.SourceFileLoader("hybrid_native_stations",str(REPO/"MIRSAD_Weather_Stations_Atlas_Generator.pyt")).load_module()
target=ROOT/".test-output/hybrid-live"/("Native_"+str(time.time_ns()))
target.mkdir(parents=True)
all_stations=load_shared_catalogue(str(REPO/"data/stations.sqlite"))["EG"]
stations=[s for s in all_stations if s["Station_ID"]=="623660" and s["WBAN"]=="99999"][:1]
assert stations
tool=stations_module.WeatherStationsAtlasGenerator()
for cls in (stations_module.WeatherStationsAtlasGenerator,stations_module.WeatherStationsAtlasGeneratorAR):
    pd={p.name:p for p in cls().getParameterInfo()}
    choices=" ".join(pd["Climate_Data_Source"].filter.list)
    assert "NOAA GSOD" in choices and "Standalone" in choices,choices
    assert str(pd["OpenMeteo_Model"].value)==ERA5_MODELS[0],str(pd["OpenMeteo_Model"].value)
path=str(target/"stations.shp")
tool._write_stations_shapefile(stations,path)
points=tool._extract_points(path,arcpy.SpatialReference(4326),None)
assert points[0]["wban"]=="99999",points
assert points[0]["station_id"]=="623660",points
parameters=stations_module._core.PowerClimateAtlasGenerator.getParameterInfo(tool)
values=dict(Input_Point_Features=path,Output_Workspace=str(target/"Atlas"),Study_Area_Name="Hybrid acceptance",
    Climate_Data_Source="Hybrid: NOAA Station Observations + NASA / ERA5 Gap-Filling",
    Climate_Modules="Temperature;Precipitation;UV Index",Time_Mode="Custom Date Range",
    Start_Date=dt.datetime(2024,1,1),End_Date=dt.datetime(2024,1,31),Temporal_Resolution="Daily",
    Gap_Fill_Method="Climatological Month Mean (Recommended)",Download_Only=True,
    Save_Daily_Series=True,Export_Shapefiles=False,Add_To_Map=False)
values["Climate_Data_Source"]={"noaa":NOAA_ONLY,"era5":ERA5_ONLY,"hybrid":values["Climate_Data_Source"],"chirps":CHIRPS,"terra":TERRA,"chelsa":CHELSA}[args.provider]
if args.provider=="era5":values["OpenMeteo_Model"]=ERA5_MODELS[0]
if args.provider=="chelsa":values.update(Start_Date=dt.datetime(2021,1,1),End_Date=dt.datetime(2021,1,31))
if args.provider in ("chirps","terra","chelsa"):values["Climate_Modules"]="Precipitation"
for parameter in parameters:
    if parameter.name in values:
        parameter.value=values[parameter.name]
messages=[]
class Messages:
    def addMessage(self,value): messages.append(str(value));print(value,flush=True)
    def addWarningMessage(self,value): messages.append("WARNING "+str(value));print(value,flush=True)
    def addWarning(self,value): self.addWarningMessage(value)
    def addErrorMessage(self,value): messages.append("ERROR "+str(value));print(value,flush=True)
stations_module._core.PowerClimateAtlasGenerator.execute(tool,parameters,Messages())
summaries=list(target.rglob("*-summary.json"))
assert summaries
summary=json.loads(summaries[0].read_text(encoding="utf-8"))
expected={"noaa":["NOAA GSOD"],"era5":["Open-Meteo"],"hybrid":["NOAA GSOD","Open-Meteo","NASA POWER"],"chirps":[CHIRPS],"terra":[TERRA],"chelsa":[CHELSA]}[args.provider]
assert summary["source_policy"]==expected,summary
assert all(event["source"] in expected for event in summary.get("source_events",[])),summary
assert expected[0] in summary["source_summary"],summary
books=list(target.rglob("*.xlsx"))+list(target.rglob("*.xls"))
assert books
readback=[]
for gdb in target.rglob("*.gdb"):
    for directory,dirs,features in arcpy.da.Walk(str(gdb),datatype="FeatureClass"):
        for feature in features:
            path=str(Path(directory)/feature)
            fields=[f.name for f in arcpy.ListFields(path)]
            if "R_January_Mean" in fields:
                values0=[row[0] for row in arcpy.da.SearchCursor(path,["R_January_Mean"])]
                assert values0 and values0[0] is not None,(path,values0)
                if args.provider in ("chirps","terra","chelsa"):
                    assert abs(values0[0]-{"chirps":0.,"terra":2.5,"chelsa":1.}[args.provider])<.011,(path,values0)
                readback.append(dict(path=path,field="R_January_Mean",values=values0))
assert readback,"No calculated rainfall field read back from native FileGDB"
report=dict(passed=True,arcgis_pro=arcpy.GetInstallInfo()["Version"],points=points,
            output=str(target),workbooks=[str(p) for p in books],source_summary=summary["source_summary"],readback=readback,messages=messages)
(ROOT/(".test-output/"+args.provider+"-native.json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("NATIVE HYBRID PASSED",flush=True)
