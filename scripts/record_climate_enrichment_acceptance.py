"""Record existing acceptance evidence; never runs tests or promotes binaries."""
import hashlib
import argparse
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DESKTOP=ROOT/"MIRSAD Desktop"
REPORT=DESKTOP/"docs/reports/climate-enrichment/SOURCE_ACCEPTANCE.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-frozen",action="store_true")
    parser.add_argument("--include-installer",action="store_true")
    args=parser.parse_args()
    if args.include_installer and not args.include_frozen:parser.error("Installer evidence requires the frozen candidate")
    inputs={
        "legacy":ROOT/"tests/.output/legacy-streaming-final/summary.json",
        "python27":ROOT/"tests/.output/python27-legacy-streaming/summary.json",
        "live":DESKTOP/".test-output/climate-enrichment-quality-live/acceptance.json",
        "excel_boundary":DESKTOP/".test-output/excel-streaming/Boundary.acceptance.json",
        "pro_readback":DESKTOP/".test-output/climate-enrichment-quality-live/native-readback.json",
    }
    evidence={key:json.loads(path.read_text(encoding="utf-8")) for key,path in inputs.items()}
    if not all(report.get("passed") for report in evidence.values()):raise ValueError("Acceptance evidence contains a failure")
    log=DESKTOP/".test-output/climate-enrichment-final-tests.log"
    text=log.read_text(encoding="utf-8-sig",errors="replace")
    match=re.search(r"Ran (\d+) tests in ([\d.]+)s\s+OK\s*$",text)
    if not match:raise ValueError("Desktop suite has not completed successfully")
    summaries={}
    for key in ("legacy","python27"):
        runs=evidence[key]["results"]
        summaries[key]=dict(suites=len(runs),tests=sum(r["tests"] for r in runs),passed=True,results=runs)
    summaries["desktop"]=dict(tests=int(match[1]),seconds=float(match[2]),passed=True)
    inputs["desktop_log"]=log
    frozen=None
    if args.include_frozen:
        paths={"worker":DESKTOP/".test-output/frozen-enrichment-quality/acceptance.json",
               "source_equivalence":DESKTOP/".test-output/climate-enrichment-source-equivalence.json",
               "build":DESKTOP/".build/dist/MIRSAD/build_manifest.json"}
        frozen={key:json.loads(path.read_text(encoding="utf-8")) for key,path in paths.items()}
        exe_hash=digest(DESKTOP/".build/dist/MIRSAD/MIRSAD.exe")
        if not all(r.get("exe_sha256")==exe_hash for r in frozen.values()):raise ValueError("Frozen evidence does not identify the same candidate")
        if not frozen["worker"].get("passed") or not frozen["source_equivalence"].get("passed"):raise ValueError("Frozen checks failed")
        if not all(frozen["build"].get(key) for key in ("gui_smoke_passed","ui_worker_export_passed","workspace_acceptance_passed","help_acceptance_passed")):
            raise ValueError("Frozen general gates are incomplete")
        inputs.update(paths)
        if args.include_installer:
            installed=DESKTOP/".test-output/installer_acceptance.json"
            installer_manifest=DESKTOP/"runtime/installers/development/installer_manifest.json"
            acceptance=json.loads(installed.read_text(encoding="utf-8"))
            package=json.loads(installer_manifest.read_text(encoding="utf-8"))
            if not acceptance.get("passed") or acceptance.get("production_installation_changed") is not False:
                raise ValueError("Isolated installer acceptance failed")
            if acceptance["installer_sha256"]!=package["installer_sha256"] or package["bundle_sha256"]!=frozen["build"]["bundle_sha256"]:
                raise ValueError("Installer evidence identifies another payload")
            if digest(installer_manifest.parent/"MIRSAD-Setup.exe")!=package["installer_sha256"]:raise ValueError("Installer changed")
            frozen["installer"]=dict(manifest=package,acceptance=acceptance)
            inputs.update(installer_acceptance=installed,installer_manifest=installer_manifest)
    runtime=list((ROOT/"mirsad_core").glob("*.py"))+list((DESKTOP/"src/mirsad_desktop").glob("*.py"))+list((ROOT/"Toolboxes").glob("*.pyt"))
    report=dict(date="2026-10-21",base_revision="09bb7fd043d6e8a9984e8f27f36c2815dbe4e0f2",
        scope="Desktop source enrichment"+(" and verified frozen build scratch" if frozen else "")+"; no Toolbox processing, runtime replacement or publication acceptance",
        tests=summaries,live=evidence["live"],excel_boundary=evidence["excel_boundary"],
        pro_readback=dict(passed=True,new_fields=len(evidence["pro_readback"]["fields"]),scope=evidence["pro_readback"]["scope"]),
        evidence_files={str(path.relative_to(ROOT)).replace("\\","/"):digest(path) for path in inputs.values()},
        runtime_source_sha256={str(path.relative_to(ROOT)).replace("\\","/"):digest(path) for path in sorted(runtime)},
        baseline_fixture_sha256=digest(ROOT/"tests/fixtures/climate_enrichment_baseline.json"),
        help_manifest=json.loads((ROOT/"Help/chm_manifest.json").read_text(encoding="utf-8")),
        remaining=["Toolbox UI/execution/exports and native ArcMap acceptance", "Supported regional enrichment",
                   "Optional localized Desktop aliases and full generated field help", "Large climate pipeline memory/time acceptance",
                   "Complete DPI/accessibility and fresh-checkout build acceptance"])
    if frozen:report["frozen_candidate"]=frozen
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Recorded source acceptance:",summaries["desktop"]["tests"],"Desktop tests;",summaries["legacy"]["tests"],"isolated legacy tests")


if __name__=="__main__":main()
