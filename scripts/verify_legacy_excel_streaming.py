# -*- coding: utf-8 -*-
"""Actual default XLSX row boundary on Python 2.7/3, without external packages."""
from __future__ import print_function
import argparse
import json
import os
import sys
import time
import zipfile
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT)
from mirsad_core.xlsx_stream import write_workbook,NS


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows",type=int,default=1000001)
    parser.add_argument("--output",default=os.path.join(ROOT,"tests/.output/legacy-excel/Boundary.xlsx"))
    args=parser.parse_args()
    if not 1<=args.rows<=5000000:parser.error("Choose 1..5,000,000 explicit fixture rows")
    started=time.time()
    def rows():
        for index in range(args.rows):yield ["2024-02-29",index]
    result=write_workbook(args.output,[("Source_Data",["Source"],[["Generated sequential fixture"]],False),
        ("Daily",["Date","ID"],rows(),False)])
    count=0;sheets=0
    for path in result["files"]:
        with zipfile.ZipFile(path) as archive:
            definitions=ET.fromstring(archive.read("xl/workbook.xml")).find("{%s}sheets"%NS)
            for i,item in enumerate(definitions,1):
                if not item.get("name").startswith("Daily"):continue
                sheets+=1
                with archive.open("xl/worksheets/sheet%d.xml"%i) as stream:
                    data=None
                    for event,element in ET.iterparse(stream,events=("start","end")):
                        if event=="start" and element.tag=="{%s}sheetData"%NS:data=element
                        if event=="end" and element.tag=="{%s}row"%NS:
                            if element.get("r")!="1":
                                identifier=int(element[1].find("{%s}v"%NS).text)
                                if identifier!=count:raise AssertionError("Missing/duplicate/reordered row: %s"%count)
                                count+=1
                            if data is not None:data.remove(element)
    if count!=args.rows:raise AssertionError("Changed output row count")
    report=dict(passed=True,rows=count,sheets=sheets,files=result["files"],seconds=round(time.time()-started,3),
                python=sys.version,scope="Real standard-library XLSX boundary; not native ArcMap processing or a climate-download memory benchmark")
    with open(os.path.splitext(args.output)[0]+".acceptance.json","w") as handle:json.dump(report,handle,indent=2)
    print(json.dumps(report))


if __name__=="__main__":main()
