# -*- coding: utf-8 -*-
"""Independent synthetic TIFF pixels, bounded requests and native cell centres."""
from __future__ import unicode_literals
from legacy_test_support import temporary_workspace
import datetime as dt
import io
import os
import shutil
import struct
import sys
import tempfile
import unittest
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT)
from mirsad_core import remote_grid as r,climate_products as p


def tiff(compression=1):
    # Two 2x2 strips, int16 values, upper-left=(10,20), native 1-degree cells.
    tags={256:(4,[2]),257:(4,[4]),258:(3,[16]),259:(3,[compression]),
        273:(4,[0,0]),277:(3,[1]),278:(4,[2]),279:(4,[8,8]),339:(3,[2]),
        33550:(12,[1.,1.,0.]),33922:(12,[0.,0.,0.,10.,20.,0.]),
        34735:(3,[1,1,0,2,1025,0,1,1,2048,0,1,4326]),42113:(2,b'-9999\x00')}
    start=8+2+len(tags)*12+4;extra=bytearray();entries=[]
    # Assign strip offsets after the directory and all indirect metadata.
    size=sum(len(v) if k==2 else len(v)*{3:2,4:4,12:8}[k] for k,v in tags.values() if (len(v) if k==2 else len(v)*{3:2,4:4,12:8}[k])>4)
    tags[273]=(4,[start+size,start+size+8])
    for tag,(kind,values) in sorted(tags.items()):
        raw=values if kind==2 else struct.pack('<'+str(len(values))+{3:'H',4:'I',12:'d'}[kind],*values)
        value=raw.ljust(4,b'\x00') if len(raw)<=4 else struct.pack('<I',start+len(extra))
        entries.append(struct.pack('<HHI',tag,kind,len(values))+value)
        if len(raw)>4:extra.extend(raw)
    return b'II'+struct.pack('<HIH',42,8,len(tags))+b''.join(entries)+struct.pack('<I',0)+bytes(extra)+struct.pack('<8h',1,2,0,-9999,5,6,7,8)


class Session(object):
    def __init__(self,data,status=206):self.data=data;self.status=status;self.calls=0
    def get(self,url,headers,**unused):
        a,b=map(int,headers['Range'][6:].split('-'));self.calls+=1
        class Response(object):
            status_code=self.status
            raw=io.BytesIO(self.data[a:b+1])
            headers={'Content-Range':'bytes %d-%d/%d'%(a,b,len(self.data)),'ETag':'fixture-v1'}
            def close(self):self.raw.close()
        return Response()


class RangeTests(unittest.TestCase):
    def setUp(self):self.folder=temporary_workspace()
    def tearDown(self):shutil.rmtree(self.folder)
    def test_strip_pixels_zero_nodata_edges_and_reusable_cache(self):
        session=Session(tiff());grid=r.RangeGrid('https://fixture/grid',self.folder,lambda:False,session)
        self.assertEqual(grid.sample(10.5,19.5),1.)
        self.assertEqual(grid.sample(10.5,18.5),0.)
        self.assertIsNone(grid.sample(11.5,18.5))
        self.assertEqual(grid.sample(11.5,16.5),8.)
        self.assertIsNone(grid.sample(12.,19.))
        calls=session.calls
        other=r.RangeGrid('https://fixture/grid',self.folder,lambda:False,session)
        self.assertEqual(other.sample(11.5,16.5),8.);self.assertEqual(session.calls,calls)
    def test_whole_file_response_and_unsupported_compression_rejected(self):
        with self.assertRaises(ValueError):r.RangeGrid('https://fixture/grid',None,lambda:False,Session(tiff(),200))
        with self.assertRaises(ValueError):r.RangeGrid('https://fixture/grid',None,lambda:False,Session(tiff(7)))
    def test_cancellation_and_range_bounds(self):
        with self.assertRaises(r.InterruptedErrorCompat):r.RangeGrid('https://fixture/grid',None,lambda:True,Session(tiff()))
        grid=r.RangeGrid('https://fixture/grid',None,lambda:False,Session(tiff()))
        with self.assertRaises(ValueError):grid.read(-1,1)
        with self.assertRaises(ValueError):grid.read(0,9*1024*1024)
    def test_regional_uses_original_centres_and_polygon_and_limit(self):
        old=p.RangeGrid
        class Grid(object):
            west=10.;north=20.;dx=1.;dy=1.;width=2;height=4
            def __init__(self,*unused):pass
        p.RangeGrid=Grid
        try:
            cells=p.native_grid_cells(p.CHIRPS,(10,16,12,20),dt.date(2024,1,1),dt.date(2024,1,31),['PRECTOTCORR'],self.folder,lambda:False,contains=lambda x,y:x<11)
            self.assertEqual([(c['longitude'],c['latitude']) for c in cells],[(10.5,19.5),(10.5,18.5),(10.5,17.5),(10.5,16.5)])
            with self.assertRaises(ValueError):p.native_grid_cells(p.CHIRPS,(10,16,12,20),dt.date(2024,1,1),dt.date(2024,1,31),['PRECTOTCORR'],self.folder,lambda:False,limit=2)
        finally:p.RangeGrid=old


if __name__=='__main__':unittest.main()
