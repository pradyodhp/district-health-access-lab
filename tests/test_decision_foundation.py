import sys
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.decision.evidence import compatible, district_ledger
from health_access.decision.readiness import assess
from health_access.decision.schema import Confidence, DecisionCase, Evidence, Intervention, Status

ROOT = Path(__file__).resolve().parents[1]


def demo_case(classification="REAL"):
    return DecisionCase(case_id="pilot", version="1", name="NCD screening", objective="maximize_additional_screened",
                        geography=("Maharashtra/Pune",), population="adults 30+", service="blood-glucose screening",
                        horizon_months=24, budget_inr=100000, target_outcome="additional adults screened",
                        interventions=(Intervention(id="outreach", name="Outreach", max_allocation_inr=100000),),
                        classification=classification, model_version="0.3.0")


def test_ledger_retains_unverified_status_and_dimensions():
    ledger = district_ledger(ROOT / "data/processed/pilot_indicators.csv")
    assert len(ledger) == 24
    assert {e.status for e in ledger} == {Status.OBSERVED_UNVERIFIED}
    assert all(e.source_url and e.retrieved_on and e.caveat for e in ledger)
    assert not compatible(ledger[:2], geography="Maharashtra/Pune", population="adults 30+", vintage="2019-21")


def test_missing_compatible_inputs_force_hold():
    report = assess(demo_case(), district_ledger(ROOT / "data/processed/pilot_indicators.csv"), as_of=date(2026, 9, 30))
    assert report["score"] == 0 and report["status"] == "HOLD"
    assert any("screening_coverage" in x for x in report["blockers"])
    assert assess(demo_case("HYPOTHETICAL"), [], as_of=date(2026, 9, 30))["status"] == "HYPOTHETICAL_ONLY"


def test_schema_rejects_false_observation_and_infeasible_minimum():
    with pytest.raises(ValidationError):
        Evidence(id="e", variable="screening_coverage", value=.5, unit="rate", status=Status.OBSERVED,
                 source="claim", vintage="2026", geography="Pune", population="adults 30+",
                 confidence=Confidence.HIGH, caveat="unknown", methodology="unknown", model_version="1")
    with pytest.raises(ValidationError):
        DecisionCase.model_validate({**demo_case().model_dump(), "budget_inr": 1, "interventions": [{"id": "outreach", "name": "Outreach", "min_allocation_inr": 2, "max_allocation_inr": 100000}]})


def test_case_evidence_readiness_api_contracts():
    from fastapi.testclient import TestClient
    from health_access.api import app
    client = TestClient(app)
    case = client.get("/api/case").json()
    assert case["classification"] == "HYPOTHETICAL"
    records = client.get("/api/evidence").json()
    assert len(records["records"]) == 24
    assert {r["status"] for r in records["records"]} == {"OBSERVED_UNVERIFIED"}
    readiness = client.get("/api/readiness").json()
    assert readiness["status"] == "HYPOTHETICAL_ONLY" and readiness["blockers"]
    assert client.post("/api/case/readiness", json={**case, "classification": "REAL"}).json()["status"] == "HOLD"
