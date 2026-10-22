# -*- coding: utf-8 -*-
"""Dependency-free streaming XLSX for ArcMap/Python 2.7 and Pro/Python 3.

Literal cells, bounded row staging, indexed Daily sheet/file parts. No CSV path.
"""
from __future__ import unicode_literals
import itertools
import json
import math
import os
import re
import shutil
import tempfile
import threading
import uuid
import zipfile
from xml.sax.saxutils import escape, quoteattr

try:
    text_type=unicode
    numeric_types=(int,long,float)
except NameError:
    text_type=str
    numeric_types=(int,float)

NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"


class RowSpool(object):
    """Reiterable JSONL rows, spilling after 1 MiB, including on Python 2.7."""
    def __init__(self,memory_bytes=1024*1024):
        self.handle=tempfile.SpooledTemporaryFile(max_size=memory_bytes,mode="w+b")
        self.count=0;self.lock=threading.RLock()

    def append(self,row):
        data=(json.dumps(list(row),ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
        with self.lock:
            self.handle.seek(0,2);self.handle.write(data);self.count+=1

    def __len__(self):return self.count

    def __iter__(self):
        position=0
        while True:
            with self.lock:
                self.handle.seek(position);line=self.handle.readline();position=self.handle.tell()
            if not line:break
            yield json.loads(line.decode("utf-8"))

    def __getitem__(self,key):
        if isinstance(key,slice):
            start,stop,step=key.indices(len(self))
            if step<=0:raise ValueError("Positive row slice step required")
            return list(itertools.islice(self,start,stop,step))
        if key<0:key+=len(self)
        if key<0 or key>=len(self):raise IndexError(key)
        return next(itertools.islice(self,key,key+1))

    def close(self):self.handle.close()
    def __del__(self):
        handle=getattr(self,"handle",None)
        if handle is not None:handle.close()


class ExcelWriteError(RuntimeError):
    def __init__(self,message,files):
        RuntimeError.__init__(self,message);self.files=list(files)


def column(index):
    result=""
    while index:
        index,rem=divmod(index-1,26);result=chr(65+rem)+result
    return result


def xml_text(value):
    value=text_type(value)
    if re.search("[\x00-\x08\x0b\x0c\x0e-\x1f]",value):raise ValueError("Invalid XML control character in Excel text")
    if len(value)>32767:raise ValueError("Excel text exceeds 32767 characters")
    return escape(value)


class Book(object):
    def __init__(self,filename):
        self.filename=filename;self.folder=tempfile.mkdtemp(prefix=".mirsad-xlsx-",dir=os.path.dirname(filename));self.sheets=[]

    def sheet(self,name,headers,rtl=False,position=None):
        if not headers or len(headers)>16384:raise ValueError("Invalid Excel column count")
        if re.search(r"[\[\]:*?/\\]",name):raise ValueError("Invalid Excel sheet name")
        base=text_type(name)[:31];title=base;count=2
        used={s["name"].lower() for s in self.sheets}
        while title.lower() in used:
            suffix="_"+text_type(count);title=base[:31-len(suffix)]+suffix;count+=1
        item=dict(name=title,headers=list(headers),rtl=rtl,count=0,first=None,last=None,
                  file=os.path.join(self.folder,uuid.uuid4().hex+".body"))
        item["handle"]=open(item["file"],"wb")
        if position is None:self.sheets.append(item)
        else:self.sheets.insert(position,item)
        self.row(item,headers,header=True)
        return item

    def row(self,sheet,values,header=False):
        values=list(values)
        if len(values)>len(sheet["headers"]):raise ValueError("Row exceeds Excel header width")
        number=1 if header else sheet["count"]+2
        cells=[]
        for i,value in enumerate(values,1):
            ref=column(i)+text_type(number);style=' s="1"' if header else ""
            if value is None:continue
            if isinstance(value,bool):cells.append('<c r="'+ref+'" t="b"'+style+'><v>'+('1' if value else '0')+'</v></c>')
            elif isinstance(value,numeric_types) and not header:
                if isinstance(value,float) and (math.isnan(value) or math.isinf(value)):continue
                cells.append('<c r="'+ref+'"><v>'+text_type(value)+'</v></c>')
            else:cells.append('<c r="'+ref+'" t="inlineStr"'+style+'><is><t xml:space="preserve">'+xml_text(value)+'</t></is></c>')
        sheet["handle"].write(('<row r="'+text_type(number)+'">'+''.join(cells)+'</row>').encode("utf-8"))
        if not header:
            sheet["count"]+=1
            if "Date" in sheet["headers"]:
                i=sheet["headers"].index("Date")
                date=text_type(values[i]) if i<len(values) and values[i] is not None else None
                if date:
                    sheet["first"]=min(date,sheet["first"]) if sheet["first"] else date
                    sheet["last"]=max(date,sheet["last"]) if sheet["last"] else date

    def save(self):
        if os.path.exists(self.filename):raise IOError("Existing workbook preserved: "+self.filename)
        temporary=self.filename+"."+uuid.uuid4().hex+".writing"
        try:
            with zipfile.ZipFile(temporary,"w",zipfile.ZIP_DEFLATED,allowZip64=True) as archive:
                names=[];links=[];types=[]
                for i,sheet in enumerate(self.sheets,1):
                    sheet["handle"].close()
                    ref="A1:"+column(len(sheet["headers"]))+text_type(sheet["count"]+1)
                    xml=os.path.join(self.folder,text_type(i)+".xml")
                    with open(xml,"wb") as dst:
                        prefix='<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="'+NS+'"><dimension ref="'+ref+'"/><sheetViews><sheetView workbookViewId="0" rightToLeft="'+('1' if sheet["rtl"] else '0')+'"><pane ySplit="1" topLeftCell="A2" state="frozen"/></sheetView></sheetViews><sheetData>'
                        dst.write(prefix.encode("utf-8"))
                        with open(sheet["file"],"rb") as src:shutil.copyfileobj(src,dst,1024*1024)
                        dst.write(('</sheetData><autoFilter ref="'+ref+'"/></worksheet>').encode("utf-8"))
                    archive.write(xml,"xl/worksheets/sheet%d.xml"%i)
                    names.append('<sheet name='+quoteattr(sheet["name"])+' sheetId="%d" r:id="rId%d"/>'%(i,i))
                    links.append('<Relationship Id="rId%d" Type="%s/worksheet" Target="worksheets/sheet%d.xml"/>'%(i,REL,i))
                    types.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'%i)
                payloads={
                    'xl/workbook.xml':'<workbook xmlns="'+NS+'" xmlns:r="'+REL+'"><sheets>'+''.join(names)+'</sheets></workbook>',
                    'xl/_rels/workbook.xml.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(links)+'<Relationship Id="rIdStyles" Type="'+REL+'/styles" Target="styles.xml"/></Relationships>',
                    '_rels/.rels':'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="'+REL+'/officeDocument" Target="xl/workbook.xml"/></Relationships>',
                    '[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join(types)+'</Types>',
                    'xl/styles.xml':'<styleSheet xmlns="'+NS+'"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF08273D"/></patternFill></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'}
                for name,text in payloads.items():archive.writestr(name,text.encode("utf-8"))
            os.rename(temporary,self.filename)
        finally:
            if os.path.exists(temporary):os.remove(temporary)

    def close(self):
        for sheet in self.sheets:
            if not sheet["handle"].closed:sheet["handle"].close()
        shutil.rmtree(self.folder)


def write_workbook(path,sheets,sheet_capacity=1000000,part_daily_rows=4000000):
    """Tables are (name, headers, reiterable/single-pass rows, rtl)."""
    path=os.path.abspath(path)
    if not path.lower().endswith(".xlsx"):raise ValueError("Streaming Excel requires .xlsx")
    if not 1<=sheet_capacity<=1048575 or part_daily_rows<1:raise ValueError("Invalid row limits")
    if os.path.exists(path):raise IOError("Existing workbook preserved: "+path)
    parent=os.path.dirname(path)
    if not os.path.isdir(parent):os.makedirs(parent)
    tables=[]
    for name,headers,rows,rtl in sheets:
        if name!="Daily" and iter(rows) is rows:
            buffered=RowSpool()
            for row in rows:buffered.append(row)
            rows=buffered
        tables.append((name,list(headers),rows,rtl))
    if not tables or sum(name=="Daily" for name,_,_,_ in tables)>1:raise ValueError("One logical Daily table at most is required")
    books=[];files=[];index=[];split=False
    def prepare(filename):
        book=Book(filename);books.append(book);daily=None
        for name,headers,rows,rtl in tables:
            sheet=book.sheet(name,headers,rtl)
            if name=="Daily":daily=(sheet,rows);continue
            for row in rows:
                if sheet["count"]==sheet_capacity:sheet=book.sheet(name,headers,rtl)
                book.row(sheet,row)
        return book,daily
    def track(book,sheet):
        index.append(dict(Workbook=os.path.basename(book.filename),Sheet=sheet["name"],Records=sheet["count"],First_Date=sheet["first"],Last_Date=sheet["last"]))
    try:
        main,daily=prepare(path);current=main;part_rows=0;part=1;sheet_number=1
        if daily:
            sheet,rows=daily
            for row in rows:
                if part_rows==part_daily_rows:
                    track(current,sheet)
                    if current is not main:current.save();files.append(current.filename);current.close();books.remove(current)
                    split=True;part+=1;part_rows=0;sheet_number=1
                    current,daily=prepare(os.path.splitext(path)[0]+"_Part_%03d.xlsx"%part);sheet,_=daily
                elif sheet["count"]==sheet_capacity:
                    track(current,sheet);split=True;sheet_number+=1
                    sheet=current.sheet("Daily_"+text_type(sheet_number),sheet["headers"],sheet["rtl"],current.sheets.index(sheet)+1)
                current.row(sheet,row);part_rows+=1
            track(current,sheet)
            if current is not main:current.save();files.append(current.filename)
        if split:
            headers=["Workbook","Sheet","Records","First_Date","Last_Date"]
            sheet=main.sheet("Export_Index",headers)
            for entry in index:main.row(sheet,[entry[h] for h in headers])
        main.save();files.append(path)
        return dict(files=[path]+[f for f in files if f!=path],split=split,index=index)
    except Exception as error:
        raise ExcelWriteError(text_type(error),files)
    finally:
        for book in books:book.close()
