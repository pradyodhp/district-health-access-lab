import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fastapi.testclient import TestClient
from health_access.api import app

client = TestClient(app)


def test_v1_aliases_match_unversioned_routes():
    for path in ("health", "indicators", "readiness", "evidence", "research-backlog"):
        old = client.get(f"/api/{path}")
        new = client.get(f"/api/v1/{path}")
        assert new.status_code == old.status_code == 200
        assert new.json() == old.json()


def test_v1_alias_keeps_path_params_and_errors():
    assert client.get("/api/v1/runs/run-does-not-exist").status_code == client.get("/api/runs/run-does-not-exist").status_code
    assert client.get("/api/v1/nope").status_code == 404
