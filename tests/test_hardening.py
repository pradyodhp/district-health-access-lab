from datetime import date
from dataclasses import replace
import hashlib
import gzip
import json
from pathlib import Path

import pytest
from health_access.scenarios import training_scenario
from health_access.decision.schema import Evidence, Status
from health_access.decision.cases import pilot_case
from health_access.decision.readiness import assess

ROOT = Path(__file__).resolve().parents[1]

def record(**changes):
    values = dict(id="screening", variable="screening_coverage", value=.5, unit="rate",
                  status="OBSERVED", source="test fixture", source_url="https://example.invalid/data",
                  retrieved_on=date(2026, 9, 30), vintage="2019-21", geography="Training",
                  population="adults", confidence="HIGH", caveat="Fixture, not evidence",
                  methodology="distinct-person fixture", model_version="1", reviewed_by="fixture review",
                  geography_level="district", period_start=date(2019, 1, 1), period_end=date(2021, 12, 31),
                  numerator=50, denominator=100, indicator_kind="direct")
    return Evidence(**(values | changes))

def test_scenario_units_are_field_specific():
    s=training_scenario()
    with pytest.raises(ValueError, match="eligible requires unit people"):
        replace(s, eligible=replace(s.eligible, unit="rate", low=.1, mode=.2, high=.3))
    with pytest.raises(ValueError, match="screening_rate requires unit rate"):
        replace(s, screening_rate=replace(s.screening_rate, unit="people"))

def test_evidence_states_periods_and_denominators():
    assert record(status=Status.REJECTED).status is Status.REJECTED
    with pytest.raises(ValueError): record(numerator=101)
    with pytest.raises(ValueError): record(period_start=date(2023,1,1))
    with pytest.raises(ValueError): record(status="DERIVED", derived_from=("parent",))

def test_ten_gates_do_not_refresh_old_period_from_download_date():
    c=pilot_case().model_copy(update=dict(classification="REAL",geography=("Training",),population="adults",
                              period_start=date(2026,1,1),period_end=date(2026,9,1)))
    report=assess(c,[record()],as_of=date(2026,9,30))
    gates={g['id']:g for g in report['gates']}
    assert len(gates)==10
    assert gates['TIME_PERIOD']['status']=='FAIL'
    assert gates['SCREENING_COVERAGE']['status']=='FAIL'
    assert report['status']=='HOLD'
    assert all({'reason','supporting_evidence','missing_evidence','severity','next_research_action'} <= g.keys() for g in gates.values())

def test_proxy_and_unverified_parent_cannot_pass():
    c=pilot_case().model_copy(update=dict(classification="REAL",geography=("Training",),population="adults",
                             period_start=date(2019,1,1),period_end=date(2021,12,31)))
    parent=record(id='parent',status='OBSERVED_UNVERIFIED')
    derived=record(status='DERIVED', derived_from=('parent',),transformation='fixture calculation')
    report=assess(c,[parent,derived],as_of=date(2026,9,30))
    assert next(g for g in report['gates'] if g['id']=='SCREENING_COVERAGE')['status']=='HOLD'
    assert assess(c,[record(indicator_kind='proxy')],as_of=date(2026,9,30))['status']=='HOLD'

def test_manifest_matches_raw_bytes():
    m=json.loads((ROOT/'data/raw/manifest.json').read_text())
    assert hashlib.sha256(gzip.open(ROOT/'data/raw'/m['file'],'rb').read()).hexdigest()==m['sha256_uncompressed']

from health_access.decision.runs import make_run, replay, RunStore
from health_access.decision.memo import make_memo
from health_access.decision.comparison import compare_runs
from fastapi.testclient import TestClient
from health_access.api import app

def test_artifact_hashes_replay_and_tampering(tmp_path):
    run=make_run(pilot_case(),training_scenario(),scenario_id='test',scenario_version='1',draws=100,seed=42,evidence=[record(status='OBSERVED_UNVERIFIED')])
    store=RunStore(tmp_path)
    store.save(run)
    assert replay(store.get(run['run_id']))['status']=='REPRODUCED'
    assert run['snapshot']['evidence_digest'] and run['output_digest']
    target=tmp_path/(run['run_id']+'.json')
    changed=json.loads(target.read_text());changed['point']['screened']=0;target.write_text(json.dumps(changed))
    with pytest.raises(ValueError,match='output integrity'):store.get(run['run_id'])
    assert not list(tmp_path.glob('.pending-*'))

def test_memo_uses_frozen_context_not_current_ledger():
    run=make_run(pilot_case(),training_scenario(),scenario_id='test',scenario_version='1',draws=100,seed=42,evidence=[record(status='OBSERVED_UNVERIFIED')])
    a=make_memo(run,{'blockers':['changed']},[])
    b=make_memo(run,{'blockers':['different']},[{'status':'OBSERVED'}])
    assert a==b
    assert a['evidence_summary']['unverified']==1
    assert isinstance(a['sensitivity'],list) and a['robustness']['classification']=='HYPOTHETICAL'
    assert a['allocation_analysis']['status']=='NOT_RUN'

def test_run_comparison_rejects_population_changes():
    run=make_run(pilot_case(),training_scenario(),scenario_id='test',scenario_version='1',draws=100,seed=42)
    other=make_run(pilot_case().model_copy(update={'population':'different'}),training_scenario(),scenario_id='test',scenario_version='1',draws=100,seed=42)
    with pytest.raises(ValueError,match='population'):compare_runs(run,other)

@pytest.mark.parametrize('path',['/api/scenario/status-quo?draws=1','/api/scenario/status-quo?draws=100001','/api/robustness?seed=-1','/api/threshold/status-quo?minimum_screened=-1'])
def test_expensive_invalid_inputs_return_422(path):
    assert TestClient(app).get(path).status_code==422

def test_request_ids_and_health_version():
    c=TestClient(app)
    response=c.get('/health')
    assert response.json()['run_format']=='2'
    assert response.headers['x-request-id']
    bad=c.get('/api/scenario/status-quo?draws=1')
    assert bad.json()['request_id']==bad.headers['x-request-id']

from health_access.decision.optimizer import Option, optimize

def test_optimizer_cycle_rejected():
    options=[Option('a','Training',0,100,50,.1,10,('b',)),Option('b','Training',0,100,50,.1,10,('a',))]
    with pytest.raises(ValueError,match='Cyclic'):optimize(options,budget_inr=100,district_capacity={'Training':100})

from health_access.decision.backlog import from_gates

def test_research_backlog_is_linked_and_has_work_state():
    report=assess(pilot_case(),[],as_of=date(2026,9,30))
    items=from_gates(report)
    assert len(items)==10
    assert all({'question','why_it_matters','decision_gate','current_evidence','missing_evidence','expected_impact','urgency','owner','status','source_candidates'} <= i.keys() for i in items)
