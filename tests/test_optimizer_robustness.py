import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.decision.optimizer import Option, optimize
from health_access.decision.robustness import Thresholds, compare_scenarios, evaluate_thresholds
from health_access.scenarios import training_scenario, training_outreach


def options():
    return [Option("outreach", "A", 0, 100, 50, 1.0, 80),
            Option("capacity", "A", 0, 100, 50, 2.0, 100, depends_on=("outreach",))]


def test_budget_dependencies_and_shared_capacity():
    result = optimize(options(), budget_inr=150, district_capacity={"A": 110})
    assert result["classification"] == "HYPOTHETICAL"
    assert result["spend_inr"] <= 150
    assert result["illustrative_people_screened"] <= 110
    assert result["allocations_inr"]["outreach"] > 0 if result["allocations_inr"]["capacity"] else True
    assert result["unspent_inr"] == 150 - result["spend_inr"]


def test_real_optimizer_rejected_and_minimum_infeasible():
    with pytest.raises(ValueError, match="Real funding"):
        optimize(options(), budget_inr=200, district_capacity={"A": 100}, classification="REAL")
    assert optimize([Option("x", "A", 100, 100, 1, 1, 100)], budget_inr=99,
                    district_capacity={"A": 100})["status"] == "INFEASIBLE"
    with pytest.raises(ValueError):
        optimize([Option("x", "A", 0, 1_000_000, 1, 1, 100)], budget_inr=10,
                 district_capacity={"A": 100})


def test_paired_robustness_reproducible_and_ties():
    pair = {"a": training_scenario(), "b": training_scenario()}
    result = compare_scenarios(pair, draws=100, seed=7)
    assert result["preference_share"] == {"a": .5, "b": .5}
    assert result == compare_scenarios(pair, draws=100, seed=7)
    with pytest.raises(ValueError, match="Real robustness"):
        compare_scenarios(pair, classification="REAL")


def test_threshold_assesses_only_hypothetical_draws():
    samples = [{"screened": 10, "spend_inr": 100}, {"screened": 20, "spend_inr": 100}]
    result = evaluate_thresholds(samples, Thresholds(minimum_screened=15, minimum_probability=.5))
    assert result["probability"] == .5 and result["status"] == "BORDERLINE_IN_HYPOTHETICAL_MODEL"
    assert evaluate_thresholds(samples, Thresholds(minimum_screened=15), classification="REAL")["status"] == "CANNOT_ASSESS"


def test_optimizer_and_robustness_api_contracts():
    from fastapi.testclient import TestClient
    from health_access.api import app
    client = TestClient(app)
    payload = {"classification": "HYPOTHETICAL", "budget_inr": 150,
               "district_capacity": {"A": 110}, "options": [vars(o) for o in options()]}
    assert client.post("/api/optimize", json=payload).json()["status"] == "HYPOTHETICAL_OPTIMUM"
    payload["classification"] = "REAL"
    assert client.post("/api/optimize", json=payload).status_code == 422
    result = client.get("/api/robustness?draws=100&seed=3").json()
    assert sum(result["preference_share"].values()) == pytest.approx(1)
    assert "samples" not in result and result["classification"] == "HYPOTHETICAL"
    threshold = client.get("/api/threshold/status-quo?draws=100").json()
    assert "HYPOTHETICAL" in threshold["status"]


def test_conditional_preference_reversal_scan_is_reproducible():
    result = compare_scenarios({"a": training_scenario(), "b": training_scenario()}, draws=100, seed=9)
    for group in result["conditional_preference"].values():
        assert group == {"a": .5, "b": .5}
    assert "empirical cutoff" in result["reversal_note"]


def test_optimizer_rejects_fractional_allocation_grid():
    with pytest.raises(ValueError):
        Option('x', 'A', 0, 10.5, 1, .1, 20)
