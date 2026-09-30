import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.api import app
from health_access.decision.cases import pilot_case
from health_access.decision.runs import RunStore, make_run
from health_access.scenarios import training_scenario


def test_identical_snapshot_reproduces_bands_and_id(tmp_path):
    when = datetime(2026, 9, 30, tzinfo=timezone.utc)
    a = make_run(pilot_case(), training_scenario(), scenario_id="base", scenario_version="1",
                 draws=200, seed=7, created_at=when)
    b = make_run(pilot_case(), training_scenario(), scenario_id="base", scenario_version="1",
                 draws=200, seed=7, created_at=when)
    assert a == b
    assert a["snapshot"]["inputs"]["need_rate"]["rationale"]
    assert a["classification"] == "HYPOTHETICAL"
    assert a["decision_status"] == "HOLD_FOR_REAL_FUNDING"
    assert make_run(pilot_case(), training_scenario(), scenario_id="base", scenario_version="1",
                    draws=200, seed=8, created_at=when)["run_id"] != a["run_id"]
    store = RunStore(tmp_path)
    assert store.save(a) == a
    assert store.save(b) == a
    assert store.get(a["run_id"])["bands"] == a["bands"]
    with pytest.raises(ValueError):
        store.get("../../etc/passwd")


def test_real_case_is_blocked():
    case = pilot_case().model_dump()
    case["classification"] = "REAL"
    from health_access.decision.schema import DecisionCase
    with pytest.raises(ValueError, match="verified"):
        make_run(DecisionCase.model_validate(case), training_scenario(), scenario_id="a", scenario_version="1", draws=100, seed=0)


def test_run_api_roundtrip_and_rejects_real(monkeypatch, tmp_path):
    import health_access.api as api
    monkeypatch.setattr(api, "RunStore", lambda root: RunStore(tmp_path))
    client = TestClient(app)
    case = pilot_case().model_dump(mode="json")
    inputs = {k: vars(v) for k, v in vars(training_scenario()).items()}
    payload = {"case": case, "scenario_id": "baseline", "scenario_version": "1", "inputs": inputs,
               "seed": 5, "simulation_count": 100}
    result = client.post("/api/runs", json=payload)
    assert result.status_code == 200, result.text
    assert client.get("/api/runs/" + result.json()["run_id"]).json() == result.json()
    assert client.get("/api/runs/not-a-run").status_code == 404
    payload["case"]["classification"] = "REAL"
    assert client.post("/api/runs", json=payload).status_code == 422
