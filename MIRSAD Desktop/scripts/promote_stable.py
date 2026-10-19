"""Promote the exact approved candidate to the one fixed stable path.

Run only after the user approves the development candidate. The explicit hash
binds approval to a reviewed build instead of silently promoting later changes.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from distribution import bundle_hash,remove_build_directory

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--approved-sha256",required=True)
args = parser.parse_args()
source,target = ROOT/"runtime/development",ROOT/"runtime/stable"
approved_hash = bundle_hash(source)
if approved_hash != args.approved_sha256:
    raise SystemExit("Candidate changed after approval; promotion refused.")
manifest = json.loads((source/"build_manifest.json").read_text(encoding="utf-8"))
if manifest["bundle_sha256"] != approved_hash or manifest["export_self_test"]["status"] != "complete":
    raise SystemExit("Candidate has no matching successful export test.")
if not manifest.get("gui_smoke_passed"):
    raise SystemExit("Candidate has no successful packaged GUI test.")
if not manifest.get("ui_worker_export_passed"):
    raise SystemExit("Candidate has no successful frozen UI/worker export test.")
if not manifest.get("workspace_acceptance_passed"):
    raise SystemExit("Candidate has no successful independent-tool / preview acceptance.")
subprocess.run([str(source/"MIRSAD.exe"),"--self-test",str(ROOT/".test-output/promotion_check.json")],check=True,timeout=120)
candidate,backup = ROOT/".build/promotion_candidate",ROOT/".build/stable_rollback"
remove_build_directory(candidate)
remove_build_directory(backup)
shutil.copytree(source,candidate)
if bundle_hash(candidate) != approved_hash:
    raise SystemExit("Distribution copy verification failed; stable was not changed.")
(candidate/"release.json").write_text(json.dumps({"approved_sha256":approved_hash,"version":manifest["version"]},indent=2))
(candidate/"README.md").write_text("# Approved MIRSAD release\n\nVersion: "+manifest["version"]+"\n\nApproved bundle: "+approved_hash+"\n")
if target.exists(): target.replace(backup)
try:
    candidate.replace(target)
except Exception:
    if backup.exists(): backup.replace(target)
    raise
remove_build_directory(backup)
print("Promoted approved build to",target/"MIRSAD.exe")
