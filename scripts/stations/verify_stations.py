# -*- coding: utf-8 -*-
"""Verify station deliverables: GDB FC, SHP, CSV."""
import csv
import os

BASE = r"C:\Users\ahmad\Desktop\NASA POWER Climate Atlas Generator"
P = os.path.join(BASE, "Egypt_Climate_Stations_Project")
FC = os.path.join(P, "Egypt_Stations.gdb", "Egypt_Weather_Stations")
SHP = os.path.join(P, "Export_SHP", "Egypt_Weather_Stations_WGS84.shp")
CSV = os.path.join(P, "Stations_Summary.csv")

import arcpy

ok = True
def check(name, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name + (" | " + str(detail) if detail else ""))
    if not cond:
        ok = False

check("GDB FC exists", arcpy.Exists(FC))
d = arcpy.Describe(FC)
check("FC is Point WGS84", d.shapeType == "Point" and d.spatialReference.factoryCode == 4326,
      d.spatialReference.name)
n = int(arcpy.GetCount_management(FC)[0])
check("FC count == 86 (bogus excluded)", n == 86, n)
fields = [f.name for f in arcpy.ListFields(FC)]
for req in ["Station_ID", "Station_Nm", "Station_Ar", "Latitude", "Longitude", "Elevation",
            "Source_DB", "Class_EN", "Class_AR", "Start_Year", "End_Year"]:
    check("field " + req, req in fields)
check("SHP exists", os.path.isfile(SHP), os.path.getsize(SHP) if os.path.isfile(SHP) else 0)
ns = int(arcpy.GetCount_management(SHP)[0])
check("SHP count == 86", ns == 86, ns)
cpg = os.path.splitext(SHP)[0] + ".cpg"
check("SHP cpg UTF-8", os.path.isfile(cpg) and open(cpg, "rb").read().strip() == "UTF-8")
check("CSV exists", os.path.isfile(CSV))
rows = list(csv.reader(open(CSV, "rb")))
check("CSV 86 data rows + header", len(rows) == 87, len(rows))
names = [r[0] for r in arcpy.da.SearchCursor(FC, ["Station_Nm"])]
for key in ["CAIRO", "ALEXANDRIA", "ASWAN", "LUXOR"]:
    check("known station " + key, any(key in (nm or "") for nm in names))
ar = [r[0] for r in arcpy.da.SearchCursor(FC, ["Station_Ar"]) if r[0]]
check("Station_Ar filled all", len(ar) == n, len(ar))
check("Arabic sample Cairo", any(u"القاهرة" in (a or "") for a in ar))
ce = set(r[0] for r in arcpy.da.SearchCursor(FC, ["Class_EN"]) if r[0])
check("classes valid set", ce <= set(["Airport", "Agricultural", "Port", "Academic", "Synoptic", "Other"]), ce)
ca = set(r[0] for r in arcpy.da.SearchCursor(FC, ["Class_AR"]) if r[0])
check("arabic classes valid", ca <= set([u"مطار", u"زراعية", u"ميناء", u"بحثية", u"سينوبتيكية", u"أخرى"]), len(ca))
check("no BOGUS station", not any("BOGUS" in (nm or "") for nm in names))
lats = [r[0] for r in arcpy.da.SearchCursor(FC, ["Latitude"])]
lons = [r[0] for r in arcpy.da.SearchCursor(FC, ["Longitude"])]
check("bbox in spec", min(lats) >= 21.9 and max(lats) <= 31.7 and min(lons) >= 24.7 and max(lons) <= 37.0,
      (min(lats), max(lats), min(lons), max(lons)))
print("STATIONS_VERIFY " + ("OK" if ok else "FAILED"))
import sys
sys.exit(0 if ok else 1)
