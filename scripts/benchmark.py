"""Reproducible local uncertainty runtime/convergence report, not model validation."""
import json
import sys
import time
import tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from health_access.scenarios import training_scenario
from health_access.simulation import simulate

if __name__=='__main__':
    rows=[]; previous=None
    for count in (1000,5000,10000,25000,100000):
        tracemalloc.start();start=time.perf_counter();bands=simulate(training_scenario(),draws=count,seed=42)
        elapsed=time.perf_counter()-start;_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        median=bands['screened']['p50']
        rows.append({'draws':count,'seconds':round(elapsed,4),'peak_traced_bytes':peak,
                     'screened_p50':median,'median_change_from_previous':None if previous is None else median-previous})
        previous=median
    print(json.dumps({'classification':'HYPOTHETICAL','seed':42,'method':'Independent triangular parameter propagation',
                      'scope':'Local Python runtime and traced allocations, not API load or browser memory',
                      'warning':'Stabilized Monte Carlo summaries do not establish empirical or model validity','rows':rows},indent=2))
