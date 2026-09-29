import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from health_access.decision.cases import pilot_case
from health_access.decision.runs import make_run
from health_access.decision.comparison import compare_runs
from health_access.scenarios import training_scenario, training_outreach


def test_run_comparison_changes_and_hold():
    a = make_run(pilot_case(), training_scenario(), scenario_id='base', scenario_version='1', draws=100, seed=2)
    b = make_run(pilot_case(), training_outreach(), scenario_id='outreach', scenario_version='1', draws=100, seed=2)
    result = compare_runs(a, b)
    assert result['changed_inputs'] and result['left_run_id'] != result['right_run_id']
    assert result['screened_p50_delta'] == pytest.approx(b['bands']['screened']['p50']-a['bands']['screened']['p50'])
    assert result['decision_changed'] is False and result['decision_status'] == 'HOLD_FOR_REAL_FUNDING'
    assert compare_runs(a,a)['changed_inputs'] == []


def test_run_comparison_rejects_schema_mismatch():
    a = make_run(pilot_case(), training_scenario(), scenario_id='base', scenario_version='1', draws=100, seed=2)
    b = make_run(pilot_case(), training_scenario(), scenario_id='other', scenario_version='1', draws=100, seed=2)
    del b['snapshot']['inputs']['capacity']
    with pytest.raises(ValueError, match='schema'):
        compare_runs(a,b)
