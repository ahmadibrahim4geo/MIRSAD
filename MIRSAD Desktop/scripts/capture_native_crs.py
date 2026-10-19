"""Development-only read of the installed Pro taxonomy; never imported by Desktop."""
import json
from pathlib import Path
print("Loading ArcGIS Pro for CRS snapshot",flush=True)
import arcpy

root=Path(__file__).resolve().parents[1]
entries=[]
for kind in ("GCS","PCS"):
    names=arcpy.ListSpatialReferences("*",kind)
    for index,path in enumerate(names):
        sr=arcpy.SpatialReference(path)
        entries.append(dict(path=path,code=sr.factoryCode,name=sr.name,wkt=sr.exportToString().split(";")[0]))
        if index%1000==0:print(kind,index,len(names),flush=True)
data=dict(version=arcpy.GetInstallInfo()["Version"],entries=entries)
target=root/".test-output/native_crs.json"
target.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
print("Saved",len(entries),target,flush=True)
