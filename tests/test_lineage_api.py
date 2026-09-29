from pathlib import Path
import sys
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from health_access.api import app


def test_evidence_lineage_drilldown():
    client = TestClient(app)
    row = client.get('/api/evidence').json()['records'][0]
    result = client.get('/api/evidence/' + row['id'] + '/lineage')
    assert result.status_code == 200
    assert result.json()['lineage'][0]['id'] == row['id']
    assert result.json()['lineage'][0]['status'] == 'OBSERVED_UNVERIFIED'
    assert client.get('/api/evidence/nonexistent/lineage').status_code == 404
