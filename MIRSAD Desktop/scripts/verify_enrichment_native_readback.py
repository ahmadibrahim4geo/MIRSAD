"""Licensed Pro readback of Desktop-authored FileGDB; not Toolbox processing acceptance."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gdb",type=Path)
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args()
    import arcpy
    arcpy.env.workspace=str(args.gdb.resolve(strict=True))
    fields=[]
    prefixes=("RHmax_","RHmin_","ea_","es_","VPD_","Trange_","Sunshine_","Ra_","U2_","Rn_FAO56_","ET_PM_")
    for name in arcpy.ListFeatureClasses():
        path=str(args.gdb/name)
        for field in arcpy.ListFields(path):
            if field.name in ("Z_Elev_m","Z_Source") or field.name.startswith(prefixes):
                if field.aliasName!=field.name:raise AssertionError("Alias mismatch: "+name+" / "+field.name)
                fields.append(dict(layer=name,name=field.name,alias=field.aliasName,type=field.type))
    if not fields:raise AssertionError("No supplementary fields found")
    report=dict(passed=True,scope="Native ArcGIS Pro reads Desktop FileGDB and verifies default aliases; not native Toolbox processing",fields=fields)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Pro readback passed:",len(fields),"new fields; aliases match names")


if __name__=="__main__":main()
