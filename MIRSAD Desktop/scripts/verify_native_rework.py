"""Read/validate actual .pyt parameter objects and the new GDB in native Pro."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
print("Starting native Toolbox validation",flush=True)
import arcpy

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
def load(name,path):
    loader=importlib.machinery.SourceFileLoader(name,str(path))
    spec=importlib.util.spec_from_loader(name,loader);module=importlib.util.module_from_spec(spec);loader.exec_module(module)
    return module

checks=[]
for filename,classes in (("Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt",("PowerClimateAtlasGenerator","SpatialClimateAtlasGeneratorAR")),
                         ("Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt",("WeatherStationsAtlasGenerator","WeatherStationsAtlasGeneratorAR")),
                         ("Toolboxes/MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt",("RasterDataClimateAtlasGenerator","RasterDataClimateAtlasGeneratorAR"))):
    module=load("native_"+filename.replace(".","_"),REPO/filename)
    for cls in classes:
        try:
            tool=getattr(module,cls)();parameters=tool.getParameterInfo()
            tool.updateParameters(parameters);tool.updateMessages(parameters)
            provider=next((p for p in parameters if p.name=="Climate_Data_Source"),None)
            checks.append(dict(tool=cls,parameters=len(parameters),provider_choices=list(provider.filter.list) if provider else [],passed=True))
        except Exception as exc:checks.append(dict(tool=cls,passed=False,error=str(exc)))
        print(checks[-1],flush=True)
gdb=ROOT/".test-output/rework-live/Regional_Live/Project.gdb"
arcpy.env.workspace=str(gdb)
layers=[]
for name in arcpy.ListFeatureClasses():
    description=arcpy.Describe(name)
    layers.append(dict(name=name,rows=int(arcpy.management.GetCount(name)[0]),wkid=description.spatialReference.factoryCode,
                       fields=[f.name for f in arcpy.ListFields(name)]))
report=dict(arcgis_pro=arcpy.GetInstallInfo()["Version"],tool_checks=checks,gdb_readback=layers,
            passed=all(c["passed"] for c in checks) and len(layers)>=2,
            scope="Native parameter construction/update and FileGDB readback; not a complete end-to-end run of every toolbox/provider")
(ROOT/".test-output/rework-native.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Native validation:",report["passed"],flush=True)
raise SystemExit(0 if report["passed"] else 1)
