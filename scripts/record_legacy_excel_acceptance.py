"""Record legacy XLSX evidence separately from the earlier Desktop candidate."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    paths=dict(tests=ROOT/"tests/.output/legacy-streaming-final/summary.json",
        python27=ROOT/"tests/.output/python27-legacy-streaming/summary.json",
        boundary=ROOT/"tests/.output/legacy-excel/Boundary.acceptance.json",
        native_pro=ROOT/"tests/.output/native-xlsx-pro-verified/acceptance.json",
        native_arcmap=ROOT/"tests/.output/native-xlsx-arcmap-bounded/acceptance.json")
    evidence={key:json.loads(path.read_text(encoding="utf-8")) for key,path in paths.items() if path.is_file()}
    for key in ("tests","python27","boundary","native_pro"):
        if not evidence.get(key,{}).get("passed"):raise ValueError("Missing/failed evidence: "+key)
    for key in ("tests","python27"):
        evidence[key]["suites"]=len(evidence[key]["results"])
        evidence[key]["tests"]=sum(r["tests"] for r in evidence[key]["results"])
    evidence.setdefault("native_arcmap",dict(passed=False,status="not completed; no native acceptance claim"))
    files=[ROOT/name for name in ("mirsad_core/xlsx_stream.py","Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt",
        "tests/test_xlsx_stream.py","tests/test_yearly_excel_export.py","scripts/verify_legacy_excel_streaming.py","scripts/verify_native_xlsx.py")]
    report=dict(date="2026-10-21",scope="Point/station large-Daily XLSX, not climate option/regional parity",
        evidence=evidence,source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        evidence_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values() if p.is_file()},
        limits=["Native ArcMap geoprocessor initialization", "Full climate-download memory/time benchmark",
                "Legacy partial-export propagation at project level", "New Toolbox variables/PM/DEM and regional parity"])
    target=ROOT/"MIRSAD Desktop/docs/reports/climate-enrichment/LEGACY_EXCEL_ACCEPTANCE.json"
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Recorded legacy XLSX:",evidence["tests"]["tests"],"isolated tests;",evidence["python27"]["tests"],"Python 2.7 tests")


if __name__=="__main__":main()
