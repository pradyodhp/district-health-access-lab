"""One-command hypothetical artifact, memo and replay demonstration."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from health_access.scenarios import training_scenario
from health_access.decision.cases import pilot_case
from health_access.decision.evidence import district_ledger
from health_access.decision.runs import make_run, RunStore, replay
from health_access.decision.memo import make_memo

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'runs/demo');args=parser.parse_args()
    run=make_run(pilot_case(),training_scenario(),scenario_id='training-demo',scenario_version='1',draws=1000,seed=42,
                 evidence=district_ledger(ROOT/'data/processed/pilot_indicators.csv'))
    RunStore(args.output).save(run)
    memo=make_memo(run,run['snapshot']['readiness'],run['snapshot']['evidence_snapshot'])
    (args.output/'memo.json').write_text(json.dumps(memo,indent=2)+'\n')
    print(json.dumps({'classification':'HYPOTHETICAL / TRAINING DATA','run_id':run['run_id'],
                      'replay':replay(run)['status'],'decision':memo['decision'],'output':str(args.output)},indent=2))
