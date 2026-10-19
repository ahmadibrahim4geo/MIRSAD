# -*- coding: utf-8 -*-
"""Independent source-order/data-integrity checks, runnable on Python 2.7/3."""
from __future__ import unicode_literals
import datetime as dt
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT)
from utils import hybrid_pipeline as h
from utils import climate_sources as policies


class HybridTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.mkdtemp(dir=os.path.join(ROOT,"MIRSAD Desktop",".test-output"))
        self.start=dt.date(2024,1,1)
        self.end=dt.date(2024,1,3)
        self.stations=[dict(station_key=k,usaf="012345",wban="0000"+str(i),latitude=0.,longitude=float(i),name=k)
                       for i,k in enumerate(("A","B"),1)]

    def tearDown(self):
        shutil.rmtree(self.folder)

    def run_pipeline(self,fetch,cancelled=lambda:False):
        return h.run(self.stations,self.start,self.end,["PRECTOTCORR"],self.folder,lambda e:None,cancelled,fetch=fetch)

    def test_barriers_missing_bounds_and_observation_priority(self):
        calls=[]
        def fetch(source,station,start,end,required,*unused):
            calls.append((source,station["station_key"],str(start),str(end)))
            data={"NOAA GSOD":{"2024-01-01":0},"Open-Meteo":{"2024-01-01":99,"2024-01-03":3},
                  "NASA POWER":{"2024-01-01":88,"2024-01-02":2,"2024-01-03":88}}[source]
            return dict(series={"PRECTOTCORR":data},raw="original",urls=[source],warnings=[],state="COMPLETE")
        result=self.run_pipeline(fetch)
        self.assertEqual([c[:2] for c in calls],[(s,k) for s in h.SOURCES for k in ("A","B")])
        self.assertEqual(calls[2][2:],("2024-01-02","2024-01-03"))
        self.assertEqual(calls[4][2:],("2024-01-02","2024-01-02"))
        self.assertEqual(result[0]["series"]["PRECTOTCORR"],{"2024-01-01":0.,"2024-01-02":2.,"2024-01-03":3.})
        self.assertEqual(result[0]["provenance"]["PRECTOTCORR"]["2024-01-01"],"NOAA GSOD")
        self.assertEqual(result[0]["missing_counts"],{"PRECTOTCORR":0})
        self.run_pipeline(lambda *args:self.fail("Successful request should be reused"))

    def test_cancellation_preserves_completed_request_and_resumes(self):
        state={"cancelled":False};calls=[]
        def fetch(source,station,*unused):
            calls.append((source,station["station_key"]))
            state["cancelled"]=True
            return dict(series={"PRECTOTCORR":{"2024-01-01":1}},raw="CSV",urls=[],warnings=[])
        with self.assertRaises(h.Cancelled):
            self.run_pipeline(fetch,lambda:state["cancelled"])
        self.assertEqual(len(calls),1)
        state["cancelled"]=False
        def resumed(source,station,*unused):
            calls.append((source,station["station_key"]))
            return dict(series={},raw=None,urls=[],warnings=[],state="NOT_AVAILABLE")
        self.run_pipeline(resumed)
        self.assertEqual(calls.count(("NOAA GSOD","A")),1)
        self.assertEqual(calls[1],("NOAA GSOD","B"))

    def test_failed_source_does_not_stop_network_or_become_cached_absence(self):
        calls=[]
        def fetch(source,station,*unused):
            calls.append(source)
            if source=="NOAA GSOD":
                raise IOError("temporary connection failure")
            return dict(series={},raw=None,urls=[],warnings=[],state="NOT_AVAILABLE")
        records=self.run_pipeline(fetch)
        self.assertEqual(records[0]["source_events"][0]["state"],"FAILED")
        self.assertEqual(records[0]["source_events"][1]["state"],"NOT_AVAILABLE")
        self.assertEqual(records[0]["status"],"FAILED")
        self.assertEqual(records[0]["missing_counts"]["PRECTOTCORR"],3)
        self.run_pipeline(fetch)
        self.assertEqual(calls.count("NOAA GSOD"),4)
        self.assertEqual(calls.count("Open-Meteo"),2)

    def test_noaa_zero_missing_flags_units_and_identifiers(self):
        text="STATION,DATE,LATITUDE,LONGITUDE,TEMP,PRCP,PRCP_ATTRIBUTES\n01234500001,2024-01-01,0,1,68,0,G\n01234500001,2024-01-02,0,1,9999.9,0,I\n"
        values,rejected=h.parse_noaa(text,self.stations[0],self.start,self.end,["T2M","PRECTOTCORR"])
        self.assertEqual(values["T2M"],{"2024-01-01":20})
        self.assertEqual(values["PRECTOTCORR"],{"2024-01-01":0})
        with self.assertRaises(ValueError):
            h.parse_noaa(text.replace("01234500001","01234500002"),self.stations[0],self.start,self.end,["T2M"])
        self.assertEqual(rejected,0)

    def test_monthly_spatial_estimates_do_not_modify_daily_or_use_estimated_donors(self):
        source={day:10. for day in h.days(dt.date(2024,1,1),dt.date(2024,1,31))}
        stations=[dict(station_key=k,latitude=0.,longitude=lon) for k,lon in (("A",0.),("B",1.),("C",2.))]
        records=[dict(station=s,series={"T2M":source if s["station_key"]=="B" else {}}) for s in stations]
        h.prepare_monthly(records,dt.date(2024,1,1),dt.date(2024,1,31),"spatial",lambda *a:{})
        self.assertEqual(records[0]["monthly"]["T2M"][(2024,1)],10.)
        self.assertEqual(records[0]["series"]["T2M"],{})
        self.assertEqual([d["station_key"] for d in records[2]["monthly_gap_provenance"]["T2M"]["2024-01"]["donors"]],["B"])

    def test_bundled_pipeline_is_identical_to_shared_source(self):
        bundled=os.path.join(ROOT,"MIRSAD Desktop","src","mirsad_desktop","hybrid_pipeline.py")
        with open(bundled,"rb") as f:
            desktop=f.read()
        with open(h.__file__.replace(".pyc",".py"),"rb") as f:
            toolbox=f.read()
        self.assertEqual(desktop,toolbox)

    def test_standalone_policies_never_fetch_another_source(self):
        for provider in (policies.NOAA_ONLY,policies.ERA5_ONLY,policies.GRID_HYBRID):
            calls=[]
            order=policies.pipeline_sources(provider)
            def fetch(source,station,*unused):
                calls.append(source)
                return dict(series={},raw="original",urls=[source],warnings=[],state="NOT_AVAILABLE")
            folder=os.path.join(self.folder,str(len(order))+order[0].replace(" ",""))
            result=h.run(self.stations,self.start,self.end,["PRECTOTCORR"],folder,lambda e:None,lambda:False,fetch=fetch,sources=order)
            self.assertEqual(calls,[source for source in order for station in self.stations])
            self.assertEqual(result[0]["source_policy"],list(order))
            self.assertEqual(result[0]["series"].get("PRECTOTCORR",{}),{})
            self.assertEqual(result[0]["missing_counts"]["PRECTOTCORR"],3)

    def test_noaa_arbitrary_point_makes_no_request_or_nearest_station_substitution(self):
        point=dict(station_key="user",latitude=30.,longitude=31.)
        def forbidden(*args):self.fail("Point without USAF/WBAN must not request NOAA")
        result=h.run([point],self.start,self.end,["T2M"],self.folder,lambda e:None,lambda:False,
                     fetch=forbidden,sources=("NOAA GSOD",))
        self.assertEqual(result[0]["missing_counts"],{"T2M":3})
        self.assertEqual(result[0]["series"].get("T2M",{}),{})

    def test_native_resolution_and_provider_scope(self):
        self.assertNotIn(policies.NOAA_ONLY,policies.point_providers())
        self.assertIn(policies.NOAA_ONLY,policies.point_providers(stations=True))
        self.assertIn("Auto",policies.resolution_options(policies.ERA5_ONLY)[0])
        self.assertEqual(policies.resolution_options(policies.NOAA_ONLY),(policies.NOAA_RESOLUTION,))
        self.assertEqual(policies.resolution_options("NASA POWER"),(policies.POWER_RESOLUTION,))
        self.assertEqual(policies.canonical_resolution("era5_seamless"),policies.ERA5_MODELS[2])
        with open(os.path.join(ROOT,"MIRSAD Desktop","src","mirsad_desktop","climate_sources.py"),"rb") as f:
            bundled=f.read()
        with open(os.path.join(ROOT,"utils","climate_sources.py"),"rb") as f:
            self.assertEqual(bundled,f.read())

    def test_auto_resolution_per_variable_and_whole_period(self):
        required=["T2M","RH2M","PRECTOTCORR","WS10M"]
        self.assertEqual(policies.reanalysis_plan(required,"auto",dt.date(2024,1,1)),
            [("era5_land",["T2M","RH2M"]),("era5",["PRECTOTCORR","WS10M"])])
        self.assertEqual(policies.reanalysis_plan(required,"auto",dt.date(1949,1,1)),[("era5",required)])
        self.assertEqual(policies.reanalysis_plan(required,"era5_land",dt.date(2024,1,1)),[("era5_land",required)])

    def test_auto_provenance_records_actual_model_and_resolution(self):
        def fetch(source,station,start,end,required,model,*unused):
            return dict(series={"T2M":{"2024-01-01":20},"PRECTOTCORR":{"2024-01-01":2}},
                raw={},urls=[],warnings=[],models_by_variable={"T2M":"era5_land","PRECTOTCORR":"era5"})
        result=h.run(self.stations[:1],self.start,self.start,["T2M","PRECTOTCORR"],self.folder,
                     lambda e:None,lambda:False,fetch=fetch,sources=("Open-Meteo",))[0]
        self.assertEqual(result["provenance"]["T2M"]["2024-01-01"],"Open-Meteo era5_land")
        self.assertEqual(result["resolution_by_variable"]["PRECTOTCORR"]["Open-Meteo era5"]["spatial"],"0.25 degree")


class AutomaticFailureTests(unittest.TestCase):
    def test_one_product_failure_preserves_other_variables_and_retries(self):
        import tempfile
        import shutil
        folder=tempfile.mkdtemp(dir=os.path.join(ROOT,"MIRSAD Desktop",".test-output"))
        old=h._read;calls=[];available=[False]
        def read(url,*unused):
            calls.append(url)
            if "models=era5_land" in url:
                if not available[0]:raise ValueError("temporary fixture outage")
                return '{"daily":{"time":["2024-01-01"],"temperature_2m_mean":[20]}}'
            return '{"daily":{"time":["2024-01-01"],"precipitation_sum":[2]}}'
        h._read=read
        try:
            station=dict(station_key="A",latitude=30.,longitude=31.)
            options=dict(stations=[station],start=dt.date(2024,1,1),end=dt.date(2024,1,1),required=["T2M","PRECTOTCORR"],cache_folder=folder,progress=lambda e:None,cancelled=lambda:False,sources=("Open-Meteo",))
            first=h.run(**options)[0]
            self.assertEqual(first["series"]["PRECTOTCORR"],{"2024-01-01":2.})
            self.assertNotIn("T2M",first.get("resolution_by_variable",{}))
            self.assertEqual(first["source_events"][0]["state"],"PARTIAL_FAILURE")
            available[0]=True
            second=h.run(**options)[0]
            self.assertEqual(second["series"]["T2M"],{"2024-01-01":20.})
            self.assertEqual(len(calls),4)
        finally:h._read=old;shutil.rmtree(folder)


if __name__=="__main__":unittest.main()
