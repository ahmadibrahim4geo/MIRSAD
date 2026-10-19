"""Embed exactly the shared, audited catalogue snapshot and approved identity."""
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
ROOT = DESKTOP.parent


def main():
    source = ROOT/"data/stations.sqlite"
    with sqlite3.connect(source) as db:
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Invalid station catalogue")
        metadata = {key:json.loads(value) for key,value in db.execute("SELECT key,value FROM metadata")}
        if db.execute("SELECT COUNT(*) FROM stations").fetchone()[0] != metadata["count"]:
            raise RuntimeError("Station count differs from the manifest")
    db.close()
    target = DESKTOP/"assets"
    target.mkdir(exist_ok=True)
    shutil.copy2(source,target/"stations.sqlite")
    for name in ("mirsad-wordmark.png","mirsad-favicon.svg","mirsad-icon-dark.svg"):
        shutil.copy2(ROOT/"assets"/name,target/name)
    metadata["embedded_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    (target/"catalogue_manifest.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    # Convert the approved vector icon to the Windows executable icon; no redesign.
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage,QPainter
    from PySide6.QtSvg import QSvgRenderer
    image = QImage(256,256,QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    QSvgRenderer(str(target/"mirsad-favicon.svg")).render(painter)
    painter.end()
    if not image.save(str(target/"mirsad.ico"),"ICO"):
        raise RuntimeError("Windows icon conversion failed")
    from importlib.metadata import distributions
    notices = []
    for distribution in distributions():
        name = distribution.metadata["Name"]
        notices.append({"name":name,"version":distribution.version,
                        "license":distribution.metadata.get("License-Expression") or distribution.metadata.get("License")})
        for item in distribution.files or []:
            relative = str(item).replace("\\","/")
            if "/licenses/" in relative.lower() or relative.rsplit("/",1)[-1].lower().startswith(("license","copying")):
                source_file = Path(distribution.locate_file(item))
                if source_file.is_file():
                    # Distribution metadata may use parent-relative paths for
                    # native wheel libraries. Keep copied notices inside assets.
                    safe_parts=[part for part in Path(relative).parts if part not in (".","..")]
                    license_target = target/"licenses"/name/Path(*safe_parts)
                    if not license_target.resolve().is_relative_to((target/"licenses").resolve()):
                        raise RuntimeError("Invalid license notice path")
                    license_target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(source_file,license_target)
    (target/"third_party.json").write_text(json.dumps(notices,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Prepared embedded catalogue:",metadata["catalogue_version"],metadata["count"])


if __name__ == "__main__": main()
