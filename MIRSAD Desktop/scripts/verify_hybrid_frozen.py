"""Exercise actual frozen Hybrid worker outside the checkout's working directory."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.catalogue import Catalogue
catalogue=Catalogue()
stations=[s for s in catalogue.stations("EG") if s["usaf"] in ("623660","623180") and s["wban"]=="99999"][:2]
folder=ROOT/".test-output/hybrid-frozen"/str(time.time_ns())
folder.mkdir(parents=True)
request=dict(operation="climate",points=stations,folder=str(folder/"output"),name="Hybrid_Actual_EXE",metadata=catalogue.metadata(),
    options=dict(start="2024-01-01",end="2024-01-31",provider="Hybrid",om_model="era5",
                 modules=["Temperature","Precipitation","UV Index"],gap_method="climatological"))
path=folder/"request.json"
path.write_text(json.dumps(request,ensure_ascii=False),encoding="utf-8")
environment=dict(os.environ,PATH=os.environ["SystemRoot"]+";"+str(Path(os.environ["SystemRoot"])/"System32"))
subprocess.run([str(ROOT/"runtime/development/MIRSAD.exe"),"--run-job",str(path)],cwd=Path.home(),env=environment,check=True,timeout=180)
result=json.loads((folder/"result.json").read_text(encoding="utf-8"))
assert result["manifest"]["status"]=="complete",result["manifest"]["errors"]
output=Path(result["output"])
summary=[json.loads(p.read_text(encoding="utf-8")) for p in (output/"Raw_Data").glob("*-summary.json")]
assert len(summary)==2
assert any("NOAA GSOD" in row["source_summary"] for row in summary)
assert len(list((output/"Raw_Data").glob("*-monthly-estimates.json")))==2
report=dict(passed=True,output=str(output),worker_state=json.loads((folder/"state.json").read_text()),
    manifest_status=result["manifest"]["status"],sources=[s["source_summary"] for s in summary],
    bundle=json.loads((ROOT/"runtime/development/build_manifest.json").read_text())["bundle_sha256"])
(ROOT/".test-output/hybrid-frozen.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=True,indent=2))
