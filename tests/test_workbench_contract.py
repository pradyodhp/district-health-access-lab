"""Frontend-readable integrated contract, including a retrievable run and memo."""
import sys
from pathlib import Path
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.api import app


def test_workbench_roundtrip(tmp_path, monkeypatch):
    from health_access.decision import runs
    monkeypatch.setattr(runs, "ROOT", tmp_path, raising=False)
    from health_access import api
    monkeypatch.setattr(api, "ROOT", tmp_path)
    # The pilot evidence is bundled with the package, not with mutable run storage.
    def ledger(_):
        return []
    monkeypatch.setattr(api, "district_ledger", ledger)
    client = TestClient(app)
    case = client.get('/api/case').json()
    inputs = client.get('/api/scenario/status-quo').json()['inputs']
    request = {"case":case,"scenario_id":"status-quo","scenario_version":"1.0.0",
               "inputs":inputs,"seed":42,"simulation_count":100}
    response = client.post('/api/runs', json=request)
    assert response.status_code == 200, response.text
    run = response.json()
    assert client.get('/api/runs/' + run['run_id']).json()['snapshot_digest'] == run['snapshot_digest']
    memo = client.get('/api/runs/' + run['run_id'] + '/memo')
    assert memo.status_code == 200, memo.text
    assert memo.json()['run_id'] == run['run_id']
    assert memo.json()['decision'].startswith('DECISION ON HOLD')
    assert client.get('/api/evidence').status_code == 200
    assert client.get('/api/readiness').json()['status'] == 'HYPOTHETICAL_ONLY'
    assert client.get('/api/research/status-quo').json()['classification'] == 'HYPOTHETICAL'
    assert client.get('/api/robustness?draws=100').json()['classification'] == 'HYPOTHETICAL'
