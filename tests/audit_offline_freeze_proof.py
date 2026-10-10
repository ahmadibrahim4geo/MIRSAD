# -*- coding: utf-8 -*-
"""
Reproduction harness for the POWER Climate Atlas Generator offline-mode freeze.

It loads the REAL toolbox source with a mock arcpy, then calls the REAL
PowerClimateAtlasGenerator._merge_offline_layers with 17 precalculated point
layers laid out exactly the way DOWNLOAD mode writes them:

    <out_ws>/Climate_Database_From_2015_To_2024.gdb/<MODULE_SHORT[module]>

and reports every write the tool performs against those input datasets.
"""
import os
import sys

if sys.version_info[0] >= 3:
    import importlib.machinery
    import importlib.util
else:
    import imp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYT = os.path.join(ROOT, "MIRSAD_Climate_Atlas_Generator_10_8.pyt")

# ---------------------------------------------------------------- mock arcpy
OPS = []            # (op, target, detail)
LAYERS = {}         # path -> {"fields": [name...], "rows": [dict...]}
INPUT_PATHS = set()


class SpatialReference(object):
    def __init__(self, code=4326):
        self.factoryCode = code
        self.name = "WGS_1984" if code == 4326 else "Projected_%s" % code
        self.type = "Geographic" if code == 4326 else "Projected"


class Point(object):
    def __init__(self, x, y):
        self.X, self.Y = x, y
    @property
    def centroid(self):
        return self


class Geometry(object):
    def __init__(self, x, y):
        self._p = Point(x, y)
    def projectAs(self, sr):
        return self._p


class Field(object):
    def __init__(self, name, ftype="Double"):
        self.name, self.type = name, ftype
        self.aliasName = name


class Describe(object):
    def __init__(self, path):
        self.OIDFieldName = "OBJECTID"
        self.spatialReference = SpatialReference(4326)
        self.path = path


class _Cursor(object):
    def __init__(self, path, fields, update):
        self.path, self.fields, self.update = path, fields, update
        self._rows = []
        for r in LAYERS[path]["rows"]:
            row = []
            for f in fields:
                if f.upper() in ("SHAPE@", "SHAPE"):
                    row.append(Geometry(r["x"], r["y"]))
                elif f.upper() == "OBJECTID" or f.upper() == "OID":
                    row.append(r["oid"])
                else:
                    row.append(r["values"].get(f))
            self._rows.append(row)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter(self._rows)

    def updateRow(self, row):
        OPS.append(("updateRow", self.path, "fields=%d" % len(row)))
        rec = None
        for r in LAYERS[self.path]["rows"]:
            if r["oid"] == row[0]:
                rec = r
                break
        if rec is None:
            return
        for f, v in zip(self.fields, row):
            if f.upper() in ("SHAPE@", "SHAPE", "OBJECTID", "OID"):
                continue
            rec["values"][f] = v


class _DA(object):
    def SearchCursor(self, path, fields, *a, **k):
        OPS.append(("SearchCursor", path, ",".join(str(f) for f in fields)[:60]))
        return _Cursor(path, fields, False)
    def UpdateCursor(self, path, fields, *a, **k):
        OPS.append(("UpdateCursor", path, ",".join(str(f) for f in fields)[:60]))
        return _Cursor(path, fields, True)


class _Management(object):
    def CopyFeatures(self, src, dst, *a, **k):
        OPS.append(("CopyFeatures", dst, "from %s" % src))
        import copy as _c
        LAYERS[dst] = _c.deepcopy(LAYERS[src])
    def AddField(self, path, name, typ, *a, **k):
        OPS.append(("AddField", path, "%s %s" % (name, typ)))
        LAYERS[path]["fields"].append(name)
    def DeleteField(self, path, names, *a, **k):
        OPS.append(("DeleteField", path, ",".join(names)))
        for n in (names if isinstance(names, (list, tuple)) else [names]):
            if n in LAYERS[path]["fields"]:
                LAYERS[path]["fields"].remove(n)
            for r in LAYERS[path]["rows"]:
                r["values"].pop(n, None)
    def Delete(self, path, *a, **k):
        OPS.append(("Delete", path, ""))
    def Project(self, src, dst, sr, *a, **k):
        OPS.append(("Project", dst, "from %s" % src))
        import copy as _c
        LAYERS[dst] = _c.deepcopy(LAYERS[src])
    def CalculateStatistics(self, *a, **k):
        pass
    def DeleteFeatures(self, *a, **k):
        pass
    def CreateFileGDB(self, *a, **k):
        pass


class _Env(object):
    def __getattr__(self, k):
        return None
    def __setattr__(self, k, v):
        object.__setattr__(self, k, v)


class MockArcPy(object):
    def __init__(self):
        self.da = _DA()
        self.management = _Management()
        self.env = _Env()
        self.sa = None
    def SpatialReference(self, code=4326):
        return SpatialReference(code)
    def ListFields(self, path):
        if path not in LAYERS:
            raise RuntimeError("ListFields: unknown %s" % path)
        out = [Field("OBJECTID", "OID"), Field("Shape", "Geometry")]
        for n in LAYERS[path]["fields"]:
            if n.upper() in ("OBJECTID", "SHAPE"):
                continue
            out.append(Field(n, "String" if n in ("Data_Start", "Data_End", "Temporal",
                                                  "Interp_Meth", "Status", "Error_Msg") else "Double"))
        return out
    def Exists(self, path):
        return path in LAYERS
    def Describe(self, path):
        if path not in LAYERS:
            raise RuntimeError("Describe: unknown %s" % path)
        return Describe(path)
    def ClearEnvironment(self, *a):
        pass
    def AddMessage(self, m):
        pass
    def AddWarning(self, m):
        pass


# ------------------------------------------------------- build the fake GDB
mock = MockArcPy()

if sys.version_info[0] >= 3:
    loader = importlib.machinery.SourceFileLoader("pytmod", PYT)
    spec = importlib.util.spec_from_file_location("pytmod", PYT, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pytmod"] = mod
    spec.loader.exec_module(mod)
else:
    mod = imp.load_source("pytmod", PYT)
    sys.modules["pytmod"] = mod

mod.arcpy = mock
mod._HAS_ARCPY = True

OUT_WS = os.path.join(ROOT, "_proof_out")
# Exactly what DOWNLOAD mode produces for Year Range 2015-2024 ...
GDB = os.path.join(OUT_WS, "Climate_Database_From_2015_To_2024.gdb")
# ... and what OFFLINE mode recomputes from the inputs' Data_Start/Data_End
#     (pyt lines 3958 vs 3985): the same name, therefore the same GDB.
OFFLINE_GDB = os.path.join(OUT_WS, "Climate_Database_%s.gdb" % "From_2015_To_2024")

MODULES = [m for m in mod.ALL_CANONICAL_MODULES]
ADMIN = [a[0] for a in mod.ADMIN_FIELDS]

PTS = [(31.20, 30.05), (31.35, 30.05), (31.50, 30.20), (31.65, 30.20), (31.80, 30.35)]

for m in MODULES:
    short = mod.MODULE_SHORT.get(m, m)
    path = os.path.join(GDB, short)
    flds = list(ADMIN) + list(mod.MODULE_FIELDS.get(m, [])) + ["Feat_ID", "Feat_Name", "OBJECTID_1"]
    rows = []
    for i, (lon, lat) in enumerate(PTS):
        vals = dict((f, float(i + 1)) for f in mod.MODULE_FIELDS.get(m, []))
        for _c in ("Feat_ID", "Feat_Name", "OBJECTID_1"):
            vals[_c] = "legacy-%d" % i
        vals["Data_Start"] = "2015"
        vals["Data_End"] = "2024"
        vals["Source_ID"] = i + 1
        vals["Status"] = "OK"
        rows.append({"oid": i + 1, "x": lon, "y": lat, "values": vals})
    LAYERS[path] = {"fields": flds, "rows": rows}
    INPUT_PATHS.add(path)

in_text = ";".join(os.path.join(GDB, mod.MODULE_SHORT.get(m, m)) for m in MODULES)

print("=" * 78)
print("DOWNLOAD-MODE OUTPUT GDB  : %s" % os.path.basename(GDB))
print("OFFLINE-MODE OUTPUT GDB   : %s" % os.path.basename(OFFLINE_GDB))
print("SAME PATH?                : %s" % (GDB == OFFLINE_GDB))
print("INPUT LAYERS SUPPLIED     : %d" % len(INPUT_PATHS))
print("=" * 78)

# Snapshot the input field schema so we can show what the tool destroys.
before = dict((p, list(LAYERS[p]["fields"])) for p in INPUT_PATHS)

tool = mod.PowerClimateAtlasGenerator()
wanted = dict((m, list(mod.MODULE_FIELDS.get(m, []))) for m in MODULES)

print("\n--- invoking real _merge_offline_layers() ---\n")
element_fcs = tool._merge_offline_layers(
    in_text, OFFLINE_GDB, SpatialReference(3857), MODULES, [],
    wanted, (lambda s: None), (lambda s: None),
    admin_meta={"data_start": "2015", "data_end": "2024", "temporal": "Monthly",
                "base_cell": 5000.0, "wind_cell": 25000.0})

WRITE_OPS = ("AddField", "DeleteField", "updateRow", "CopyFeatures")

# ------------------------------------------------------------- the verdict
print("\n" + "=" * 78)
print("WRITES PERFORMED AGAINST THE USER'S OWN INPUT LAYERS")
print("=" * 78)
hits = {}
for op, target, detail in OPS:
    if op in WRITE_OPS and target in INPUT_PATHS:
        hits.setdefault(target, []).append((op, detail))

if not hits:
    print("  (none - inputs were left untouched)")
for target in sorted(hits):
    name = os.path.basename(target)
    ops = hits[target]
    kinds = sorted(set(o for o, _ in ops))
    print("  WRITTEN: %-22s <- %s" % (name, ", ".join("%s x%d" % (k, sum(1 for o, _ in ops if o == k))
                                                     for k in kinds)))

print("\n" + "=" * 78)
print("SCHEMA DAMAGE: fields removed from the user's input feature classes")
print("=" * 78)
damaged = 0
for p in sorted(INPUT_PATHS):
    lost = [f for f in before[p] if f not in LAYERS[p]["fields"]]
    if lost:
        damaged += 1
        print("  %-22s lost %d field(s): %s" % (os.path.basename(p), len(lost), ", ".join(lost[:6])))
if not damaged:
    print("  (no columns lost)")

print("\n" + "=" * 78)
print("DATA DAMAGE: climate values overwritten with NULL in the user's inputs")
print("=" * 78)
nulled = 0
for p in sorted(INPUT_PATHS):
    short = os.path.basename(p)
    for r in LAYERS[p]["rows"]:
        for f, v in r["values"].items():
            if f in mod.MODULE_FIELDS.get(
                    [k for k, v2 in mod.MODULE_SHORT.items() if v2 == short][0] if
                    any(v2 == short for v2 in mod.MODULE_SHORT.values()) else "", []):
                if v is None:
                    nulled += 1
                    break
print("  rows blanked to NULL: %d" % nulled)

print("\n" + "=" * 78)
print("MODULES THAT MISSED THE SAFE 'direct_layer_map' FAST PATH")
print("=" * 78)
missed = []
for m in MODULES:
    short = mod.MODULE_SHORT.get(m, m)
    if mod.resolve_module_canonical(short) is None:
        missed.append((m, short))
for m, s in missed:
    print("  %-22s (basename %r does not resolve) -> rebuilt IN PLACE" % (m, s))
print("  total: %d of %d modules" % (len(missed), len(MODULES)))
