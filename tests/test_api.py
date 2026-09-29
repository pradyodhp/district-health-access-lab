import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fastapi.testclient import TestClient
from health_access.api import app

client = TestClient(app)


def test_health_and_indicators_are_disclaimed():
    assert client.get("/api/health").json()["ok"]
    observed = client.get("/api/indicators").json()
    assert len(observed["rows"]) == 24
    assert "Not screening coverage" in observed["warning"]


def test_scenario_and_comparison_have_hypothetical_labels():
    result = client.get("/api/scenario/status-quo?draws=100")
    assert result.status_code == 200
    assert "HYPOTHETICAL" in result.json()["label"]
    assert result.json()["bands"]["screened"]["p10"] <= result.json()["bands"]["screened"]["p90"]
    comparison = client.get("/api/compare/status-quo/outreach").json()
    assert "HYPOTHETICAL" in comparison["label"]


def test_unknown_preset_fails():
    assert client.get("/api/scenario/made-up").status_code == 404
