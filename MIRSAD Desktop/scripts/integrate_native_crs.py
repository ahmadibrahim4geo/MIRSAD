"""Embed the installed Pro tree, keeping the separately versioned public catalogue."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/".test-output/native_crs.json"
data=json.loads(source.read_text(encoding="utf-8"))
official=json.loads(gzip.decompress((ROOT/"assets/crs_catalogue.json.gz").read_bytes()))
by_number={r["code"].split(":")[1]:r for r in official}
rows=[]
for entry in data["entries"]:
    reference=by_number.get(str(entry["code"]),{})
    code=reference.get("code",("EPSG:" if entry["code"]<100000 else "ESRI:")+str(entry["code"]))
    path=entry["path"].split("/")
    rows.append(dict(code=code,name=path[-1],esri_name=entry["name"],folder=path[:-1],wkt=entry["wkt"],deprecated=reference.get("deprecated",False)))
target=ROOT/"assets/crs_pro_tree.json.gz"
target.write_bytes(gzip.compress(json.dumps(rows,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode(),mtime=0))
manifest=dict(arcgis_pro_version=data["version"],entries=len(rows),
              counts={kind:sum(r["folder"][0]==kind for r in rows) for kind in ("Geographic Coordinate Systems","Projected Coordinate Systems")},
              sha256=hashlib.sha256(target.read_bytes()).hexdigest(),source_snapshot_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              purpose="Development-time native folder/name comparison; no runtime ArcGIS dependency")
(ROOT/"assets/crs_pro_tree_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps(manifest,indent=2))
