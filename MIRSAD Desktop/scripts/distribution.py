"""Hash complete distributions and constrain removal to build intermediates."""
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bundle_hash(folder):
    digest = hashlib.sha256()
    for path in sorted(Path(folder).rglob("*")):
        if path.is_file() and path.name not in ("build_manifest.json","release.json","README.md"):
            relative = path.relative_to(folder).as_posix()
            digest.update(relative.encode("utf-8"))
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def remove_build_directory(folder):
    path = Path(folder).resolve()
    build = (ROOT/".build").resolve()
    if build not in path.parents:
        raise RuntimeError("Refused deletion outside the build workspace: "+str(path))
    if path.exists(): shutil.rmtree(path)
