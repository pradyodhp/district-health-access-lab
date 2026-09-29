import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.decision.hypotheses import HEALTH_HYPOTHESES
from health_access.decision.research import backlog
from health_access.scenarios import training_scenario


def test_hypothesis_links_and_backlog():
    assert {h.branch for h in HEALTH_HYPOTHESES} == {"Demand", "Access", "Capacity", "Retention"}
    assert all(h.question and h.metric and h.research_action for h in HEALTH_HYPOTHESES)
    rows = backlog(training_scenario(), [], effort={"awareness_rate": 1})
    assert rows[0]["score"] >= rows[-1]["score"]
    assert all(r["method"].endswith("not Bayesian VOI") for r in rows)
    assert all(r["evidence_status"] == "ASSUMED" for r in rows)
    with pytest.raises(ValueError):
        backlog(training_scenario(), [], effort={"awareness_rate": 0})
