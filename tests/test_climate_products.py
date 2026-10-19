# -*- coding: utf-8 -*-
"""Independent native-unit/coverage expectations, Python 2.7/3 compatible."""
from __future__ import unicode_literals
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT)
from utils import climate_products as p,hybrid_pipeline as h
from utils.protected_sources import daily_from_cds,CDS,cds_payload,cds_download,cds_csv


class ProductTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.mkdtemp(dir=os.path.join(ROOT,"MIRSAD Desktop",".test-output"))
        self.old=h._read
        self.station=dict(station_key="fixture",latitude=30.122,longitude=31.406)
    def tearDown(self):h._read=self.old;shutil.rmtree(self.folder)

    def test_cf_scale_offset_and_missing_applied_before_units(self):
        attrs=dict(scale_factor="0.01",add_offset="-99",_FillValue="-32768")
        self.assertAlmostEqual(p.unpack_cf(12070,attrs),21.7)
        self.assertIsNone(p.unpack_cf(-32768,attrs))
        self.assertAlmostEqual(p.unpack_cf(0,dict(scale_factor="0.1")),0.)

    def test_terra_native_monthly_rain_not_rate_and_no_daily_fabrication(self):
        def read(url,*unused):
            if url.endswith("dataset.xml"):
                return '<gridDataset><grid name="ppt"><attribute name="scale_factor" value="0.1"/><attribute name="add_offset" value="0"/><attribute name="units" value="mm"/><attribute name="_FillValue" value="-32768"/></grid></gridDataset>'
            return 'time,latitude[unit="degrees_north"],longitude[unit="degrees_east"],ppt[unit="mm"]\n2024-01-01T00:00:00Z,30,31,123\n2024-02-01T00:00:00Z,30,31,0\n'
        h._read=read
        records=p.run(p.TERRA,[self.station],dt.date(2024,1,1),dt.date(2024,2,29),["PRECTOTCORR"],self.folder,lambda e:None,lambda:False)
        rec=records[0]
        self.assertEqual(rec["series"],{})
        self.assertAlmostEqual(rec["native_monthly"]["PRECTOTCORR"]["2024-01"],12.3)
        self.assertEqual(rec["native_monthly"]["PRECTOTCORR"]["2024-02"],0.)
        h.prepare_monthly(records,dt.date(2024,1,1),dt.date(2024,2,29),"none",lambda *a:{})
        self.assertAlmostEqual(rec["monthly"]["PRECTOTCORR"][(2024,1)],12.3)
        self.assertEqual(rec["series"],{})

    def test_modis_quality_clear_sky_coverage_and_no_daily_rows(self):
        def read(url,*unused):
            if "/dates?" in url:return json.dumps(dict(dates=[dict(calendar_date="2024-01-01",modis_date="A2024001")]))
            rows=[dict(calendar_date="2024-01-01",band=band,data=[value]) for band,value in (("LST_Day_1km",15000),("QC_Day",0),("Clear_sky_days",3))]
            return json.dumps(dict(nrows=1,ncols=1,subset=rows))
        h._read=read
        rec=p.run(p.MODIS_DAY,[self.station],dt.date(2024,1,1),dt.date(2024,1,31),["TS"],self.folder,lambda e:None,lambda:False)[0]
        self.assertAlmostEqual(rec["native_monthly"]["TS"]["2024-01"],26.85)
        self.assertAlmostEqual(rec["native_monthly_coverage"]["TS"]["2024-01"],2/31.)
        self.assertEqual(rec["series"],{})
        self.assertTrue(rec["composites"][0]["accepted"])

    def test_ghcn_quality_flag_and_native_tenths(self):
        segments=["%5d%s%s%s"%(v,m,q,s) for v,m,q,s in ((123," "," ","0"),(0," "," ","0"),(999," ","X","0"))]
        text="USW00094728"+"202401PRCP"+"".join(segments+["-9999   "]*28)
        values,rejected=p.parse_ghcn(text,"USW00094728",dt.date(2024,1,1),dt.date(2024,1,31),["PRECTOTCORR"])
        self.assertEqual(values["PRECTOTCORR"],{"2024-01-01":12.3,"2024-01-02":0.})
        self.assertEqual(rejected,1)

    def test_cds_arco_hourly_units_are_aggregated_once(self):
        hourly={}
        constants={"2m_temperature":293.15,"2m_dewpoint_temperature":293.15,"skin_temperature":303.15,
            "surface_pressure":100000.,"total_precipitation":.001,"surface_solar_radiation_downwards":1e6,
            "10m_u_component_of_wind":3.,"10m_v_component_of_wind":4.}
        for variable,value in constants.items():hourly[variable]={"2024-01-01T%02d:00:00"%hour:value for hour in range(24)}
        required=["T2M","T2M_MAX","T2M_MIN","T2MDEW","TS","PS","RH2M","PRECTOTCORR","ALLSKY_SFC_SW_DWN","WS10M"]
        values=daily_from_cds(hourly,required)
        for p0,expected in (("T2M",20.),("TS",30.),("PS",100.),("RH2M",100.),("PRECTOTCORR",24.),("ALLSKY_SFC_SW_DWN",24.),("WS10M",5.)):
            self.assertAlmostEqual(values[p0]["2024-01-01"],expected)
        del hourly["total_precipitation"]["2024-01-01T04:00:00"]
        self.assertNotIn("PRECTOTCORR",daily_from_cds(hourly,required))
        self.assertEqual(cds_payload("2m_temperature",self.station)["inputs"]["area"],[30.122,31.406,30.122,31.406])

    def test_credential_errors_are_redacted_from_product_summaries(self):
        from utils import protected_sources
        old=protected_sources.protected_fetch
        def fail(*unused):raise ValueError("denied EXAMPLE_SECRET_123")
        protected_sources.protected_fetch=fail
        try:
            rec=p.run(CDS,[self.station],dt.date(2024,1,1),dt.date(2024,1,31),["T2M"],self.folder,lambda e:None,lambda:False,credentials=dict(token="EXAMPLE_SECRET_123"))[0]
            self.assertEqual(rec["status"],"FAILED")
            with open(rec["raw_path"],"rb") as f:self.assertNotIn(b"EXAMPLE_SECRET_123",f.read())
            self.assertIn("[redacted]",rec["warnings"][0])
        finally:protected_sources.protected_fetch=old

    def test_cds_protocol_and_secret_header_not_forwarded_to_asset(self):
        calls=[]
        class Response(object):
            status_code=200;headers={}
            def __init__(self,value=None,data=None):self.value=value;self.data=data
            def json(self):return self.value
            def iter_content(self,size):yield self.data
            def close(self):pass
        class Session(object):
            def post(self,url,**kwargs):
                calls.append((url,kwargs));return Response(dict(jobID='abc-123'))
            def get(self,url,**kwargs):
                calls.append((url,kwargs))
                if url.endswith('/results'):return Response(dict(asset=dict(value=dict(href='https://storage.example/result.csv'))))
                if url.startswith('https://storage'):return Response(data=b'valid_time,t2m\n2024-01-01 00:00:00,293.15\n')
                return Response(dict(status='successful'))
        text,metadata=cds_download('2m_temperature',self.station,'TEST_ONLY_TOKEN',lambda:False,Session())
        self.assertEqual(calls[0][1]['headers']['PRIVATE-TOKEN'],'TEST_ONLY_TOKEN')
        self.assertNotIn('headers',calls[-1][1])
        self.assertNotIn('TEST_ONLY_TOKEN',json.dumps(metadata))
        self.assertEqual(cds_csv(text,'2m_temperature',dt.date(2024,1,1),dt.date(2024,1,1)),{'2024-01-01T00:00:00':293.15})
        with self.assertRaises(ValueError):cds_download('2m_temperature',self.station,'',lambda:False,Session())
        with self.assertRaises(ValueError):cds_csv(text+text.splitlines()[1]+'\n','2m_temperature',dt.date(2024,1,1),dt.date(2024,1,1))


if __name__=="__main__":unittest.main()
