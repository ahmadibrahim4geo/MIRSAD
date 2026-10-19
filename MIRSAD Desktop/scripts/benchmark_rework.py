"""Measure the same IDW workload before/after index reuse with numerical parity."""
import importlib.util
import json
from pathlib import Path
import platform
import struct
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.analysis import Interpolator
baseline=ROOT/".test-output/rework-baseline/src/mirsad_desktop/analysis.py"
spec=importlib.util.spec_from_file_location("mirsad_desktop.benchmark_baseline",baseline)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
rng=np.random.default_rng(271828)
xy=rng.uniform(0,100000,(10000,2));values=xy[:,0]/1000+xy[:,1]/2000
query=rng.uniform(0,100000,(200000,2))
timings={}
outputs=[]
# Warm imports and allocation paths equally; report the median of three runs.
old.interpolate(xy,values,query[:32]);Interpolator(xy,values)(query[:32])
for name in ("before","after"):
    samples=[]
    for repeat in range(3):
        started=time.perf_counter();chunks=[]
        predict=Interpolator(xy,values) if name=="after" else None
        for offset in range(0,len(query),8192):
            q=query[offset:offset+8192]
            chunks.append(predict(q) if predict else old.interpolate(xy,values,q))
        samples.append(time.perf_counter()-started)
    timings[name]=float(np.median(samples));outputs.append(np.concatenate(chunks))
error=float(np.max(np.abs(outputs[0]-outputs[1])))
assert error<1e-10,error
report=dict(python=platform.python_version(),process_bits=struct.calcsize("P")*8,
            stations=len(xy),query_cells=len(query),neighbours=12,method="IDW power 2",seconds=timings,
            speedup=timings["before"]/timings["after"],max_abs_difference=error,
            scope="CPU interpolation only; does not claim ArcGIS/network/export speedup")
(ROOT/".test-output/rework-performance.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
