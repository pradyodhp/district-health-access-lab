import sys
from pathlib import Path
from fastapi.testclient import TestClient
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from health_access.api import app
from health_access.decision.reversal import reversal_scan
from health_access.scenarios import training_scenario, training_outreach


def test_reversal_scan_is_conditional_and_bounded():
    a=training_scenario()
    same=reversal_scan(a,a)
    assert len(same['sampled_preferences']) == 21
    assert not same['preference_changes']
    assert all(x['preferred']=='tie' for x in same['sampled_preferences'])
    assert reversal_scan(a,training_outreach()) == reversal_scan(a,training_outreach())
    with pytest.raises(ValueError):
        reversal_scan(a,a,steps=1000)


def test_reversal_api_rejects_invalid_inputs():
    c=TestClient(app)
    assert c.get('/api/reversal/status-quo/outreach').json()['classification']=='HYPOTHETICAL'
    assert c.get('/api/reversal/bad/outreach').status_code==404
    assert c.get('/api/reversal/status-quo/outreach?field=bogus').status_code==422
