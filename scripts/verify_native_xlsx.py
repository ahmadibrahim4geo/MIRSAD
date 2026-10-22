# -*- coding: utf-8 -*-
"""Actual ArcMap/Pro feature-class -> legacy exporter -> XLSX -> native table.

Creates only a fresh QA geodatabase, with explicitly generated fixture values.
"""
from __future__ import print_function,unicode_literals
import argparse
import io
import json
import os
import sys
import time
import subprocess
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT)


def write_report(folder,report):
    payload=json.dumps(report,ensure_ascii=False,indent=2)
    if isinstance(payload,bytes):payload=payload.decode("utf-8")
    with io.open(os.path.join(folder,"acceptance.json"),"w",encoding="utf-8") as handle:handle.write(payload)


def arguments():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True)
    parser.add_argument("--timeout",type=int,default=180)
    parser.add_argument("--native-worker",action="store_true",help=argparse.SUPPRESS)
    return parser.parse_args()


def main():
    args=arguments();folder=os.path.abspath(args.output)
    if not folder.startswith(os.path.abspath(os.path.join(ROOT,"tests/.output"))+os.sep):raise ValueError("Native QA outputs must stay under tests/.output")
    if os.path.exists(folder):raise IOError("Preserve existing QA outputs; choose a fresh folder")
    os.makedirs(folder)
    print("STAGE: import ArcPy");sys.stdout.flush()
    import arcpy
    from mirsad_core.xlsx_stream import RowSpool
    source=os.path.join(ROOT,"Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")
    if sys.version_info[0]>=3:
        from importlib.machinery import SourceFileLoader
        from importlib.util import spec_from_loader,module_from_spec
        loader=SourceFileLoader("native_xlsx_core",source)
        spec=spec_from_loader(loader.name,loader);core=module_from_spec(spec);loader.exec_module(core)
    else:
        import imp
        core=imp.load_source("native_xlsx_core",source)
    print("STAGE: initialize native geoprocessor / create QA database");sys.stdout.flush()
    gdb=os.path.join(folder,"QA.gdb");arcpy.CreateFileGDB_management(folder,"QA.gdb")
    points=os.path.join(gdb,"Input_Points");sr=arcpy.SpatialReference(4326)
    arcpy.CreateFeatureclass_management(gdb,"Input_Points","POINT",spatial_reference=sr)
    for name,kind in (("Station_ID","TEXT"),("Station_Nm","TEXT"),("Point_Lat","DOUBLE"),("Point_Lon","DOUBLE"),("T_Annual_Mean","DOUBLE")):
        arcpy.AddField_management(points,name,kind)
    with arcpy.da.InsertCursor(points,["SHAPE@XY","Station_ID","Station_Nm","Point_Lat","Point_Lon","T_Annual_Mean"]) as cursor:
        cursor.insertRow([(31,30),"001234","النقطة التجريبية",30,31,20])
    with arcpy.da.SearchCursor(points,["Station_ID","Station_Nm","T_Annual_Mean","SHAPE@XY"]) as cursor:
        original=next(iter(cursor))
    daily=RowSpool()
    try:
        for i in range(60001):daily.append(["001234","2024-02-29",i,20.])
        messages=[];warnings=[]
        tool=core.PowerClimateAtlasGenerator()
        tool._export_excel(points,os.path.join(folder,"Temperature.xls"),messages.append,warnings.append,
            daily=dict(header=["Station_ID","Date","Sequence","T2M"],rows=daily),module_name="Temperature",
            admin_meta=dict(provider="NASA POWER API",y0=2024,y1=2024,data_start="2024-02-29",data_end="2024-02-29"))
        if warnings:raise AssertionError(warnings)
    finally:daily.close()
    workbook=os.path.join(folder,"Temperature.xlsx")
    if not os.path.isfile(workbook):raise AssertionError("Missing streaming XLSX")
    native=os.path.join(gdb,"Daily_Readback")
    print("STAGE: native ExcelToTable readback");sys.stdout.flush()
    arcpy.ExcelToTable_conversion(workbook,native,"Daily")
    if int(arcpy.GetCount_management(native).getOutput(0))!=60001:raise AssertionError("Native table changed row count")
    count=0
    with arcpy.da.SearchCursor(native,["Station_ID","Sequence","T2M"]) as cursor:
        for identifier,sequence,value in cursor:
            if identifier!="001234" or int(sequence)!=count or value!=20:raise AssertionError("Native XLSX row/identifier/value changed")
            count+=1
    with arcpy.da.SearchCursor(points,["Station_ID","Station_Nm","T_Annual_Mean","SHAPE@XY"]) as cursor:
        row=next(iter(cursor))
        if row!=original:raise AssertionError("Input feature was modified")
        if row[0]!="001234" or row[1]!="النقطة التجريبية" or row[2]!=20 or abs(row[3][0]-31)>1e-8 or abs(row[3][1]-30)>1e-8:
            raise AssertionError("QA fixture did not preserve attributes/coordinate tolerance")
    report=dict(passed=True,scope="Native feature export and ExcelToTable readback, not new climate calculations/Toolbox option parity",
        runtime=arcpy.GetInstallInfo(),product=arcpy.ProductInfo(),rows=count,output=folder,
        checks=["Actual feature class read by legacy exporter", "60001 rows in XLSX", "Native ExcelToTable preserves identifiers/order/values", "Source attributes/Arabic/geometry unchanged"])
    write_report(folder,report)
    print(json.dumps(dict(passed=True,rows=count,product=arcpy.ProductInfo(),output=folder)))


def bounded():
    args=arguments();folder=os.path.abspath(args.output)
    if not folder.startswith(os.path.abspath(os.path.join(ROOT,"tests/.output"))+os.sep):raise ValueError("QA output outside tests/.output")
    process=subprocess.Popen([sys.executable,os.path.abspath(__file__),"--native-worker"]+sys.argv[1:],
        creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    started=time.time()
    while process.poll() is None:
        if time.time()-started>args.timeout:
            process.kill();process.wait()
            report=dict(passed=False,scope="Native XLSX acceptance incomplete",error="Native process did not finish within the bounded timeout",timeout_seconds=args.timeout)
            if os.path.isdir(folder):write_report(folder,report)
            print(json.dumps(report));return 2
        time.sleep(.25)
    return process.returncode


if __name__=="__main__":
    if "--native-worker" in sys.argv:main()
    else:sys.exit(bounded())
