"""Hybrid monthly estimation and service integration acceptance."""
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
(ROOT/".test-output").mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop import climate,hybrid_pipeline as h
from mirsad_desktop.inputs import make_point
from mirsad_desktop.science import fill_interior_gaps
from mirsad_desktop.climate_sources import NOAA_ONLY,ERA5_ONLY,GRID_HYBRID,pipeline_sources


class MonthlyHybridTests(unittest.TestCase):
    def test_standalone_downloads_preserve_missing_variables_without_fallback(self):
        station=dict(make_point("A","Point",31,30),usaf="012345",wban="00001")
        for provider in (NOAA_ONLY,ERA5_ONLY,GRID_HYBRID):
            calls=[]
            def fetch(source,*unused):
                calls.append(source)
                return dict(series={"T2M":{"2024-01-01":20.}},raw="raw",warnings=[],urls=[source])
            with tempfile.TemporaryDirectory(dir=ROOT/".test-output") as folder,patch.object(h,"fetch_source",fetch):
                records,errors,urls=climate.download([station],dt.date(2024,1,1),dt.date(2024,1,1),provider,["Temperature","Precipitation"],folder,lambda e:None,lambda:False)
                self.assertEqual(calls,list(pipeline_sources(provider)))
                self.assertEqual(records[0]["series"].get("PRECTOTCORR",{}),{})
                layers,daily=climate.prepare_outputs(records,["Precipitation"],dt.date(2024,1,1),dt.date(2024,1,1),provider,"none")
                self.assertEqual(layers["Precipitation"][0]["properties"]["Status"],"NO_DATA")
                self.assertIsNone(layers["Precipitation"][0]["properties"]["R_January_Mean"])

    def test_monthly_climatology_only_after_sources_preserves_rain_and_daily_coverage(self):
        station=make_point("A","Point",31,30)
        series={p:{str(day):v for year,v in ((2023,10.),(2025,30.))
                   for day in (dt.date(year,1,1)+dt.timedelta(days=i) for i in range(31))}
                for p in ("T2M","T2M_MAX","T2M_MIN","PRECTOTCORR")}
        rec=dict(station=station,series=series,status="OK",error="")
        h.prepare_monthly([rec],dt.date(2023,1,1),dt.date(2025,1,31),"climatological",fill_interior_gaps)
        self.assertEqual(rec["monthly"]["T2M"][(2024,1)],20.)
        self.assertIsNone(rec["monthly"]["PRECTOTCORR"][(2024,1)])
        self.assertNotIn("2024-01-01",rec["series"]["T2M"])
        rec["series"]={p:{dt.date.fromisoformat(day):v for day,v in values.items()} for p,values in rec["series"].items()}
        layers,daily=climate.prepare_outputs([rec],["Temperature","Precipitation"],dt.date(2024,1,1),dt.date(2024,1,31),"Hybrid","climatological")
        self.assertEqual(layers["Temperature"][0]["properties"]["T_January_Mean"],20.)
        self.assertEqual(layers["Temperature"][0]["properties"]["Gap_Filled_Months"],3)
        self.assertEqual(layers["Temperature"][0]["properties"]["Coverage_Fraction"],0.)
        self.assertIsNone(layers["Precipitation"][0]["properties"]["R_January_Mean"])
        self.assertEqual(daily["Temperature"][1],[])

    def test_download_uses_network_barriers_and_reports_retained_raw_files(self):
        calls=[]
        stations=[dict(make_point(k,k,31,30),usaf="012345",wban="00001") for k in ("A","B")]
        def fetch(source,station,start,end,required,*unused):
            calls.append((source,station["station_key"]))
            return dict(series={"PRECTOTCORR":{"2024-01-01":0}} if source=="NASA POWER" else {},raw="raw",warnings=[],urls=[source])
        with tempfile.TemporaryDirectory(dir=ROOT/".test-output") as folder,patch.object(h,"fetch_source",fetch):
            records,errors,urls=climate.download(stations,dt.date(2024,1,1),dt.date(2024,1,1),"Hybrid",["Precipitation"],folder,lambda e:None,lambda:False)
            self.assertEqual([s for s,k in calls],[s for s in h.SOURCES for unused in stations])
            self.assertEqual(errors,[])
            self.assertEqual(records[0]["series"]["PRECTOTCORR"][dt.date(2024,1,1)],0.)
            self.assertEqual(len(records[0]["raw_paths"]),3)
            for path in records[0]["raw_paths"]:
                self.assertTrue(Path(path).exists())
            self.assertEqual(len(urls),3)


if __name__=="__main__":unittest.main()
