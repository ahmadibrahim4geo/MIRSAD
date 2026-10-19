# -*- coding: utf-8 -*-
"""Bounded, read-only single-band GeoTIFF range sampling for Python 2/3.

Only declared EPSG:4326, north-up, contiguous/tiled TIFF data are accepted.
Compression is limited to uncompressed, TIFF LZW and Deflate. Other encodings
fail explicitly. Native values are returned; product scale/units belong upstream.
"""
from __future__ import unicode_literals
import hashlib
import io
import json
import math
import os
import struct
import sys
import zlib
try:
    from urllib.request import Request,urlopen
except ImportError:
    from urllib2 import Request,urlopen


def lzw_decode(data,limit):
    values=bytearray(data);position=0;width=9;table=[bytes(bytearray([i])) for i in range(256)]+[None,None]
    previous=None;output=bytearray()
    while position+width<=len(values)*8:
        code=0
        for unused in range(width):
            code=(code<<1)|((values[position//8]>>(7-position%8))&1);position+=1
        if code==256:
            table=[bytes(bytearray([i])) for i in range(256)]+[None,None];width=9;previous=None;continue
        if code==257:break
        if code<len(table) and table[code] is not None:entry=table[code]
        elif code==len(table) and previous is not None:entry=previous+previous[:1]
        else:raise ValueError("Invalid TIFF LZW stream")
        output.extend(entry)
        if len(output)>limit:raise ValueError("Decompressed TIFF block exceeds limit")
        if previous is not None and len(table)<4096:
            table.append(previous+entry[:1])
            if len(table)==(1<<width)-1 and width<12:width+=1
        previous=entry
    return bytes(output)


class RangeGrid(object):
    def __init__(self,url,folder,cancelled,session=None):
        self.url,self.folder,self.cancelled,self.session=url,folder,cancelled,session
        self.raw_paths=[];self.blocks={};self.etag=None
        head=self.read(0,16)
        self.order="<" if head[:2]==b"II" else ">" if head[:2]==b"MM" else None
        if not self.order:raise ValueError("Not a TIFF")
        version=struct.unpack(self.order+"H",head[2:4])[0]
        if version==42:
            offset=struct.unpack(self.order+"I",head[4:8])[0];count_size,entry_size=2,12
            count=struct.unpack(self.order+"H",self.read(offset,2))[0]
        elif version==43 and struct.unpack(self.order+"H",head[4:6])[0]==8:
            offset=struct.unpack(self.order+"Q",head[8:16])[0];count_size,entry_size=8,20
            count=struct.unpack(self.order+"Q",self.read(offset,8))[0]
        else:raise ValueError("Unsupported TIFF header")
        if count>256:raise ValueError("TIFF directory exceeds metadata limit")
        entries=self.read(offset+count_size,count*entry_size);self.tags={}
        for i in range(count):
            entry=entries[i*entry_size:(i+1)*entry_size]
            if version==42:tag,kind,n,value=struct.unpack(self.order+"HHII",entry);inline=entry[8:12];capacity=4
            else:tag,kind,n,value=struct.unpack(self.order+"HHQQ",entry);inline=entry[12:20];capacity=8
            if tag not in (256,257,258,259,273,277,278,279,284,317,322,323,324,325,339,33550,33922,34735,42112,42113):continue
            sizes={1:("B",1),2:("c",1),3:("H",2),4:("I",4),12:("d",8),16:("Q",8)}
            if kind not in sizes:raise ValueError("Unsupported TIFF metadata type")
            fmt,size=sizes[kind];length=n*size
            if length>4*1024*1024:raise ValueError("TIFF metadata exceeds limit")
            raw=inline[:length] if length<=capacity else self.read(value,length)
            self.tags[tag]=raw if kind==2 else struct.unpack(self.order+str(n)+fmt,raw)
        t=self.tags
        self.width,self.height=int(t[256][0]),int(t[257][0])
        if not(0<self.width<=1000000 and 0<self.height<=1000000):raise ValueError("Invalid grid dimensions")
        if t.get(277,(1,))[0]!=1 or t.get(284,(1,))[0]!=1:raise ValueError("Only single-band contiguous TIFF is supported")
        self.bits=int(t[258][0]);self.sample_format=int(t.get(339,(1,))[0]);self.compression=int(t.get(259,(1,))[0])
        if self.bits not in (8,16,32,64) or self.compression not in (1,5,8,32946):raise ValueError("Unsupported TIFF pixel encoding")
        keys=t.get(34735,());geo={keys[i]:keys[i+3] for i in range(4,len(keys)-3,4) if keys[i+1]==0 and keys[i+2]==1}
        if geo.get(2048)!=4326 or 3072 in geo:raise ValueError("Grid must explicitly declare geographic EPSG:4326")
        if geo.get(1025,1)!=1:raise ValueError("Only PixelIsArea grids are supported")
        if 33550 not in t or 33922 not in t:raise ValueError("Missing north-up grid georeferencing")
        self.dx,self.dy=t[33550][:2];tie=t[33922]
        self.west=tie[3]-tie[0]*self.dx;self.north=tie[4]+tie[1]*self.dy
        if not all(not math.isnan(v) and not math.isinf(v) for v in (self.dx,self.dy,self.west,self.north)) or self.dx<=0 or self.dy<=0:raise ValueError("Invalid cell sizes")
        self.tile_width=int(t.get(322,(self.width,))[0]);self.tile_height=int(t.get(323,t.get(278,(self.height,)))[0])
        self.offsets=t.get(324,t.get(273));self.lengths=t.get(325,t.get(279))
        if self.tile_width<=0 or self.tile_height<=0:raise ValueError("Invalid grid block dimensions")
        expected=int(math.ceil(self.width/float(self.tile_width)))*int(math.ceil(self.height/float(self.tile_height)))
        if not self.offsets or not self.lengths or len(self.offsets)!=expected or len(self.lengths)!=expected:raise ValueError("Grid block directory mismatch")
        self.predictor=int(t.get(317,(1,))[0])
        if self.predictor not in (1,2) or (self.predictor==2 and self.sample_format==3):raise ValueError("Unsupported TIFF predictor")
        self.nodata=float(t[42113].rstrip(b"\x00")) if 42113 in t else None
        self.scale,self.offset,self.gdal_metadata=1.,0.,{}
        if 42112 in t:
            import xml.etree.ElementTree as ET
            xml=t[42112].rstrip(b"\x00").decode("utf-8")
            if "<!DOCTYPE" in xml:raise ValueError("Unexpected TIFF metadata document type")
            for item in ET.fromstring(xml).findall("Item"):
                if item.get("sample","0")!="0":continue
                self.gdal_metadata[item.get("name")]=item.text
                if item.get("role")=="scale":self.scale=float(item.text)
                if item.get("role")=="offset":self.offset=float(item.text)

    def read(self,offset,length):
        if self.cancelled():raise InterruptedErrorCompat("Cancelled")
        if offset<0 or length<0 or length>8*1024*1024:raise ValueError("Invalid TIFF range or range exceeds 8 MB")
        if length==0:return b""
        token=hashlib.sha256((self.url+"|%d|%d"%(offset,length)).encode("utf-8")).hexdigest()
        path=os.path.join(self.folder,token+".range.json") if self.folder else None
        import base64
        if path and os.path.isfile(path):
            with io.open(path,encoding="utf-8") as f:cached=json.load(f)
            if cached.get("url")!=self.url or cached.get("offset")!=offset or cached.get("length")!=length:raise ValueError("Cached range identity mismatch")
            data=base64.b64decode(cached["bytes"])
            if len(data)!=length or hashlib.sha256(data).hexdigest()!=cached["sha256"]:raise ValueError("Corrupt cached source range")
            etag=cached.get("etag")
        else:
            headers={"Range":"bytes=%d-%d"%(offset,offset+length-1),"User-Agent":"MIRSAD climate research","Accept-Encoding":"identity"}
            if self.session is None:
                response=urlopen(Request(self.url,headers=headers),timeout=45)
                status=response.getcode();info=response.info()
            else:
                response=self.session.get(self.url,headers=headers,timeout=(15,45),stream=True)
                status=response.status_code;info=response.headers
            try:
                if status!=206:raise ValueError("Source did not honor bounded HTTP Range (status %s)"%status)
                expected="bytes %d-%d/"%(offset,offset+length-1)
                if not info.get("Content-Range","").startswith(expected):raise ValueError("Unexpected HTTP Content-Range")
                data=response.read(length+1) if self.session is None else response.raw.read(length+1)
                etag=info.get("ETag")
            finally:response.close()
            if len(data)!=length:raise ValueError("Incomplete source range")
            if path:
                from .hybrid_pipeline import atomic_json
                atomic_json(path,dict(url=self.url,offset=offset,length=length,etag=etag,sha256=hashlib.sha256(data).hexdigest(),bytes=base64.b64encode(data).decode("ascii")))
        if self.etag and etag and self.etag!=etag:raise ValueError("Remote product changed during extraction; use a clean cache")
        if etag:self.etag=etag
        if path and path not in self.raw_paths:self.raw_paths.append(path)
        return data

    def block(self,index):
        import numpy as np
        if index in self.blocks:return self.blocks[index]
        columns=self.tile_width
        rows=min(self.tile_height,self.height-(index//int(math.ceil(self.width/float(columns))))*self.tile_height) if 324 not in self.tags else self.tile_height
        limit=columns*rows*self.bits//8
        if limit>16*1024*1024:raise ValueError("Decoded grid block exceeds 16 MB")
        data=self.read(self.offsets[index],self.lengths[index])
        if self.compression==5:data=lzw_decode(data,limit)
        elif self.compression in (8,32946):
            decoder=zlib.decompressobj();data=decoder.decompress(data,limit+1)
            if (hasattr(decoder,"eof") and not decoder.eof) or len(data)>limit or decoder.unconsumed_tail:raise ValueError("Invalid/oversized Deflate block")
        if len(data)!=limit:raise ValueError("Grid block has wrong decoded length")
        code={1:"u",2:"i",3:"f"}.get(self.sample_format)
        if code is None:raise ValueError("Unsupported TIFF sample type")
        array=np.frombuffer(data,dtype=self.order+code+str(self.bits//8)).reshape(rows,columns)
        if self.predictor==2:array=np.cumsum(array,axis=1,dtype=array.dtype)
        # Keep memory bounded even while sampling large point sets.
        if len(self.blocks)>=8:self.blocks.clear()
        self.blocks[index]=array
        return array

    def sample(self,longitude,latitude):
        column=int(math.floor((longitude-self.west)/self.dx));row=int(math.floor((self.north-latitude)/self.dy))
        if not(0<=column<self.width and 0<=row<self.height):return None
        nx=int(math.ceil(self.width/float(self.tile_width)))
        index=(row//self.tile_height)*nx+column//self.tile_width
        value=float(self.block(index)[row%self.tile_height,column%self.tile_width])
        if math.isnan(value) or math.isinf(value) or (self.nodata is not None and value==self.nodata):return None
        return value


class InterruptedErrorCompat(Exception):pass
