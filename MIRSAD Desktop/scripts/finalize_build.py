"""Normalize the one development path and exercise its actual executable."""
import hashlib
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from distribution import bundle_hash,remove_build_directory

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
mode=parser.add_mutually_exclusive_group()
mode.add_argument("--verify-only",action="store_true",help="Verify build scratch without replacing the open development application")
mode.add_argument("--install-verified",action="store_true",help="Install the unchanged candidate already accepted by --verify-only")
args=parser.parse_args()
development = ROOT/"runtime/development"
generated = ROOT/".build/dist/MIRSAD"
report = ROOT/".test-output/packaged_self_test.json"
report.parent.mkdir(exist_ok=True)
def install_candidate():
    for target in (generated,development):
        if not target.resolve().is_relative_to(ROOT.resolve()):raise RuntimeError('Invalid development target')
    backup=ROOT/'.build/development_rollback'
    remove_build_directory(backup)
    development.parent.mkdir(parents=True,exist_ok=True)
    if development.exists():development.replace(backup)
    try:generated.replace(development)
    except Exception:
        if backup.exists():backup.replace(development)
        raise
    remove_build_directory(backup)
    print('Installed verified development candidate:',development/'MIRSAD.exe')

if args.install_verified:
    accepted=json.loads((generated/'build_manifest.json').read_text(encoding='utf-8'))
    gates=('gui_smoke_passed','ui_worker_export_passed','workspace_acceptance_passed','help_acceptance_passed')
    if not all(accepted.get(gate) is True for gate in gates):raise RuntimeError('Candidate acceptance is incomplete')
    if accepted.get('bundle_sha256')!=bundle_hash(generated) or accepted.get('exe_sha256')!=hashlib.sha256((generated/'MIRSAD.exe').read_bytes()).hexdigest():
        raise RuntimeError('Candidate changed after acceptance; verify it again before replacement')
    install_candidate();raise SystemExit(0)

clean_env = dict(os.environ)
clean_env["MIRSAD_TEST_SETTINGS"]=str(ROOT/".test-output/packaged_qa_settings.ini")
clean_env["PATH"] = ";".join([str(Path(os.environ.get("SystemRoot","C:\\Windows")) / "System32"), os.environ.get("SystemRoot","C:\\Windows")])

subprocess.run([str(generated/"MIRSAD.exe"),"--self-test",str(report)],cwd=Path.home(),check=True,timeout=120,env=clean_env)
data = json.loads(report.read_text(encoding="utf-8"))
if data["arcpy_imported"] or any("arcgis" in path.lower() for path in data["python_paths"]):
    raise RuntimeError("ArcGIS dependency leaked into packaged application")

# GIS diagnostics do not import Qt. Exercise the actual frozen GUI as a separate
# release gate so a native DLL conflict cannot replace a working development app.
screenshot = report.parent/"ui_packaged.png"
for path in (screenshot, screenshot.with_suffix(".startup.log"), screenshot.with_suffix(".error.txt")):
    path.unlink(missing_ok=True)
subprocess.run([str(generated/"MIRSAD.exe"),"--ui-smoke",str(screenshot)],cwd=Path.home(),check=True,timeout=45,env=clean_env)
if not screenshot.is_file() or screenshot.stat().st_size < 1000:
    raise RuntimeError("Packaged GUI did not produce a screenshot")
data["gui_smoke_passed"] = True
ui_report=report.parent/"packaged_ui_export.json"
subprocess.run([str(generated/"MIRSAD.exe"),"--ui-export-test",str(ui_report)],cwd=Path.home(),check=True,timeout=100,env=clean_env)
ui_result=json.loads(ui_report.read_text(encoding="utf-8"))
if not ui_result["passed"]:raise RuntimeError("Frozen UI processing worker failed")
data["ui_worker_export_passed"]=True
workspace_report=report.parent/"packaged_workspace.json"
subprocess.run([str(generated/"MIRSAD.exe"),"--ui-workspace-test",str(workspace_report)],cwd=Path.home(),check=True,timeout=150,env=clean_env)
workspace_result=json.loads(workspace_report.read_text(encoding="utf-8"))
if not workspace_result["passed"]:raise RuntimeError("Frozen tool workspace / preview acceptance failed")
data["workspace_acceptance_passed"]=True

# Exercise the help mode in the frozen EXE without loading map/GIS modules.
for language,topic in (('ar','formula-pet'),('en','formula-heat-index')):
    help_report=report.parent/('packaged_help_'+language+'.json')
    subprocess.run([str(generated/'MIRSAD.exe'),'--help-test',str(help_report),'--language',language,'--help-topic',topic],
        cwd=Path.home(),check=True,timeout=45,env=clean_env)
    help_result=json.loads(help_report.read_text(encoding='utf-8'))
    if not help_result['passed'] or help_result['topics']<45 or help_result['map_imported'] or help_result['arcpy_imported']:
        raise RuntimeError('Frozen bilingual help acceptance failed: '+language)
data['help_acceptance_passed']=True
data["exe_sha256"] = hashlib.sha256((generated/"MIRSAD.exe").read_bytes()).hexdigest()
data["bundle_sha256"] = bundle_hash(generated)
(generated/"build_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
if args.verify_only:
    print("Packaged candidate verified; development application was not replaced.")
    raise SystemExit(0)
install_candidate()
