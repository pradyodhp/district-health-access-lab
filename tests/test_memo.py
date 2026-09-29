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
    assert memo["evidence_summary"]["unverified"] == 1
    assert "not verified" in memo["blockers"]
    assert memo["illustrative_screened_band"] == run["bands"]["screened"]
