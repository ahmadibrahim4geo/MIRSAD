# -*- coding: utf-8 -*-
"""Validate the SEQUENTIAL _query_all: order preserved, duplicate coords fetched
once (cache), failures kept without aborting. Uses stubbed fetch (no network)."""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt") if os.path.exists(os.path.join(BASE, "Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt")) else os.path.join(BASE, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")

mod = type(sys)("qseq")
exec(compile(open(PYT, "rb").read(), PYT, "exec"), mod.__dict__)

calls = []

def fake_fetch(lat, lon, y0, y1, params, temporal="Monthly", timeout=60, retries=3, session=None, **kwargs):
    calls.append((round(lat, 4), round(lon, 4)))
    if abs(lat - 99.0) < 1e-9:
        raise RuntimeError("simulated network failure")
    return {"T2M": {"202501": 20.0 + lat}}

mod.fetch_nasa_point = fake_fetch

try:
    import arcpy
except ImportError:
    print("SKIP: arcpy not available in this environment.")
    sys.exit(0)

class Msg(object):
    def __init__(self):
        self.msgs = []
        self.warns = []
    def addMessage(self, t):
        self.msgs.append(str(t))
    def addWarningMessage(self, t):
        self.warns.append(str(t))
    def addErrorMessage(self, t):
        self.msgs.append("ERR " + str(t))

messages = Msg()
tool = mod.PowerClimateAtlasGenerator()
pts = [
    {"oid": 1, "lat": 30.0, "lon": 31.0},
    {"oid": 2, "lat": 31.0, "lon": 32.0},
    {"oid": 3, "lat": 30.0, "lon": 31.0},  # duplicate of oid 1 -> cache
    {"oid": 4, "lat": 99.0, "lon": 99.0},  # fails
    {"oid": 5, "lat": 32.0, "lon": 33.0},
]
results, ok, fail = tool._query_all(pts, 2025, 2025, ["T2M"], "Monthly",
                                    messages, messages.addMessage, messages.addWarningMessage)
order = [r["oid"] for r in results]
print("order: " + str(order))
assert order == [1, 2, 3, 4, 5], order
print("fetch calls: " + str(calls))
assert len(calls) == 4, calls  # duplicate served from cache
assert ok == 4, ok
assert len(fail) == 1 and fail[0][0] == 4, fail
assert results[2]["parameter"] == results[0]["parameter"], "cache mismatch"
assert results[3]["status"] == "FAILED"
print("SEQ QUERY TEST OK")

# ---------------- probe_server: fail fast, clear cause ----------------
def fake_om(lat, lon, y0, y1, modules, timeout=60, retries=3,
            daily_vars=None, hourly_vars=None, **kwargs):
    return {}, {}, []

mod.fetch_openmeteo_point = fake_om
mod.probe_server("NASA POWER API", 30.0, 31.0, 2025, 400)
print("probe NASA ok")
mod.probe_server("Open-Meteo Historical API (ERA5 Reanalysis)", 30.0, 31.0, 2025, 400)
print("probe OM ok")


def fake_down(lat, lon, y0, y1, params, temporal="Monthly", timeout=60, retries=3,
              session=None, **kwargs):
    raise RuntimeError("simulated outage")


def fake_om_down(lat, lon, y0, y1, modules, timeout=60, retries=3,
                 daily_vars=None, hourly_vars=None, **kwargs):
    raise RuntimeError("simulated outage")

mod.fetch_nasa_point = fake_down
try:
    mod.probe_server("NASA POWER API", 30.0, 31.0, 2025, 400)
    raise AssertionError("probe should have raised")
except RuntimeError as ex:
    assert "NASA POWER API" in str(ex) and "simulated outage" in str(ex), str(ex)[:200]
    print("probe NASA fail-fast ok")
mod.fetch_openmeteo_point = fake_om_down
try:
    mod.probe_server("Open-Meteo X", 30.0, 31.0, 2025, 400)
    raise AssertionError("probe should have raised")
except RuntimeError as ex:
    print("probe OM fail-fast ok")
print("PROBE TEST OK")
