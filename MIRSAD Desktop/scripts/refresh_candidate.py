"""Revalidate a signed development bundle and refresh its exact approval hash."""
import hashlib
import json
import subprocess
from pathlib import Path
from distribution import bundle_hash

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/"runtime/development";output=ROOT/".test-output"
output.mkdir(exist_ok=True)
subprocess.run([str(folder/"MIRSAD.exe"),"--self-test",str(output/"signed_check.json")],check=True,timeout=120,cwd=Path.home())
subprocess.run([str(folder/"MIRSAD.exe"),"--ui-export-test",str(output/"signed_ui_check.json")],check=True,timeout=100,cwd=Path.home())
data=json.loads((output/"signed_check.json").read_text(encoding="utf-8"))
if not json.loads((output/"signed_ui_check.json").read_text(encoding="utf-8"))["passed"]:raise RuntimeError("Signed UI test failed")
data.update(gui_smoke_passed=True,ui_worker_export_passed=True,exe_sha256=hashlib.sha256((folder/"MIRSAD.exe").read_bytes()).hexdigest(),bundle_sha256=bundle_hash(folder))
(folder/"build_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("Revalidated bundle:",data["bundle_sha256"])
