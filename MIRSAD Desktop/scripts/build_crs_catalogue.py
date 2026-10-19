"""Development-only snapshot of official Esri definitions; no ArcGIS runtime import."""
import gzip
import hashlib
import json
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]


def main():
    session=requests.Session()
    commit=session.get("https://api.github.com/repos/Esri/projection-engine-db-doc/commits/main",timeout=30)
    commit.raise_for_status();revision=commit.json()["sha"]
    rows=[];sources=[]
    for file,kind in (("geogcs","Geographic Coordinate Systems"),("projcs","Projected Coordinate Systems")):
        url=f"https://raw.githubusercontent.com/Esri/projection-engine-db-doc/{revision}/json/pe_list_{file}.json"
        response=session.get(url,timeout=60);response.raise_for_status()
        if len(response.content)>30*1024*1024:raise ValueError("Unexpected CRS catalogue size")
        sources.append(dict(url=url,sha256=hashlib.sha256(response.content).hexdigest()))
        for item in next(iter(response.json().values())):
            code=str(item["authority"])+":"+str(item["wkid"])
            area="; ".join(e["areaname"] for e in item.get("extent",[]))
            rows.append(dict(code=code,name=item.get("description") or item["name"],esri_name=item["name"],
                             folder=[kind,area or "World"],wkt=item["wkt2"],deprecated=item.get("deprecated")=="yes"))
    rows.sort(key=lambda r:(r["folder"],r["name"],r["code"]))
    data=json.dumps(rows,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode()
    target=ROOT/"assets/crs_catalogue.json.gz"
    target.write_bytes(gzip.compress(data,mtime=0))
    manifest=dict(source="Esri Projection Engine Database",revision=revision,sources=sources,
                  entries=len(rows),counts={kind:sum(r["folder"][0]==kind for r in rows) for kind in
                     ("Geographic Coordinate Systems","Projected Coordinate Systems")},
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                  taxonomy="Esri type and official area of use; native Pro folder snapshot overrides when present",
                  license="Apache-2.0; see crs_catalogue_LICENSE.txt")
    (ROOT/"assets/crs_catalogue_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    license_response=session.get(f"https://raw.githubusercontent.com/Esri/projection-engine-db-doc/{revision}/license.txt",timeout=30)
    license_response.raise_for_status()
    (ROOT/"assets/crs_catalogue_LICENSE.txt").write_bytes(license_response.content)
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":main()
