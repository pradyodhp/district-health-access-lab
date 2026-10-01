from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from health_access.api import app
from health_access.limits import ComputeBudget, expensive
from health_access.requests import RunRequest, OptimizationRequest
from health_access.decision.cases import pilot_case
from health_access.scenarios import training_scenario
from pydantic import ValidationError
import pytest


def test_window_and_concurrency_are_bounded_and_recover():
    now = [0]
    budget = ComputeBudget(per_minute=2, concurrent=1, clock=lambda: now[0])
    assert budget.enter()
    assert not budget.enter()
    budget.leave()
    assert budget.enter()
    budget.leave()
    assert not budget.enter()
    now[0] = 60
    assert budget.enter()
    budget.leave()


def test_atomic_admission():
    budget = ComputeBudget(concurrent=2)
    with ThreadPoolExecutor(max_workers=16) as pool:
        assert sum(pool.map(lambda _: budget.enter(), range(16))) == 2
    assert budget.active == 2
    budget.leave()
    budget.leave()


def test_both_route_mounts_share_budget(monkeypatch):
    budget = ComputeBudget(per_minute=1)
    monkeypatch.setattr(app.state, 'compute_budget', budget)
    client = TestClient(app)
    assert client.get('/api/scenario/status-quo?draws=100').status_code == 200
    denied = client.get('/api/v1/scenario/status-quo?draws=100')
    assert denied.status_code == 429
    assert denied.headers['retry-after'] == '60'
    assert denied.json()['request_id'] == denied.headers['x-request-id']
    assert client.get('/api/v1/evidence').status_code == 200
    assert budget.active == 0


def test_exception_releases_slot(monkeypatch):
    budget = ComputeBudget()
    monkeypatch.setattr(app.state, 'compute_budget', budget)
    assert TestClient(app).get('/api/scenario/missing').status_code == 404
    assert budget.active == 0


def test_simulation_and_grid_bounds():
    with pytest.raises(ValidationError):
        RunRequest(case=pilot_case(), scenario_id='x', scenario_version='1',
                   inputs={k: vars(v) for k,v in vars(training_scenario()).items()}, simulation_count=10001)
    option = dict(id='x',district='x',min_inr=0,max_inr=20000,step_inr=1,
                  assumed_people_per_inr=1,max_people=10)
    with pytest.raises(ValidationError):
        OptimizationRequest(budget_inr=10,district_capacity={'x':10},options=[option])
    for prefix in ('/api/', '/api/v1/'):
        assert TestClient(app).get(prefix+'scenario/status-quo?draws=10001').status_code == 422
        assert expensive('GET',prefix+'runs/x/replay')
        assert not expensive('GET',prefix+'runs/x/memo')


def test_openapi_contains_real_v1_resources_only():
    paths = app.openapi()['paths']
    for path in ('evidence','case','runs','scenario','robustness','runs/{run_id}/memo'):
        assert '/api/v1/'+path in paths
        assert '/api/'+path not in paths


def test_v1_missing_resource_error_has_same_shape():
    response = TestClient(app).get('/api/v1/nope')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Not Found'
    assert response.json()['request_id'] == response.headers['x-request-id']
