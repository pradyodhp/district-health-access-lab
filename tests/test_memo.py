import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from health_access.decision.memo import make_memo
from health_access.decision.cases import pilot_case
from health_access.decision.runs import make_run
from health_access.scenarios import training_scenario


def test_memo_holds_and_traces_run():
    run = make_run(pilot_case(), training_scenario(), scenario_id="demo",
                   scenario_version="1", draws=100, seed=3)
    memo = make_memo(run, {"blockers": ["not verified"]}, [{"status": "OBSERVED_UNVERIFIED"}])
    assert memo["decision"].startswith("DECISION ON HOLD")
    assert memo["run_id"] == run["run_id"]
    assert memo["provenance"]["run_digest"] == run["snapshot_digest"]
    assert memo["evidence_summary"]["unverified"] == 0  # frozen empty snapshot, not caller context
    assert "not verified" not in memo["blockers"]  # no live caller context
    assert memo["illustrative_screened_band"] == run["bands"]["screened"]


def test_memo_has_client_sections_without_fabricated_recommendation():
    run = make_run(pilot_case(), training_scenario(), scenario_id="demo",
                   scenario_version="1", draws=100, seed=3)
    memo = make_memo(run, {"blockers":["unverified"]}, [])
    for key in ("executive_summary", "decision_question", "what_we_know",
                "what_we_do_not_know", "uncertainty", "scenario_comparison",
                "key_assumptions", "what_could_change", "methodology", "limitations"):
        assert memo[key]
    assert set(x["status"] for x in memo["key_assumptions"].values()) == {"HYPOTHETICAL"}
    assert "ON HOLD" in memo["decision"]
