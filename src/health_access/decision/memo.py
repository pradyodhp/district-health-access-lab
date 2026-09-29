"""Evidence-gated memo from a stored run, never a synthetic policy recommendation."""
from __future__ import annotations


def make_memo(run: dict, readiness: dict, evidence: list[dict]) -> dict:
    if run.get("classification") != "HYPOTHETICAL":
        raise ValueError("Only hypothetical run memos supported")
    snapshot = run["snapshot"]
    case = snapshot["case"]
    bands = run["bands"]["screened"]
    return {
        "title": f"Decision memo | {case['name']}",
        "decision": "DECISION ON HOLD - no real funding allocation justified",
        "classification": "HYPOTHETICAL",
        "case_id": case["case_id"], "case_version": case["version"],
        "run_id": run["run_id"], "scenario_id": snapshot["scenario_id"],
        "scenario_version": snapshot["scenario_version"],
        "model_version": case["model_version"],
        "objective": case["objective"], "population": case["population"],
        "geography": case["geography"], "horizon_months": case["horizon_months"],
        "illustrative_screened_band": bands,
        "sensitivity": "Inspect the scenario sensitivity screen; high model sensitivity is not causal evidence.",
        "evidence_summary": {"records": len(evidence),
                             "unverified": sum(e.get("status") == "OBSERVED_UNVERIFIED" for e in evidence),
                             "not_screening_coverage": True},
        "blockers": list(readiness["blockers"]) + [
            "Verified compatible adult population denominator missing",
            "Actual screening coverage numerator/denominator missing",
            "Validated intervention costs and effects missing",
            "Facility capacity and independent model-stability review missing",
        ],
        "next_research": ["Verify official district factsheets against transcription",
                          "Obtain compatible adult denominators and actual screening counts",
                          "Validate intervention costs, effects, capacity and period"],
        "alternatives": ["Do not allocate real funds from the synthetic scenario",
                         "Use the workbench only to compare hypothetical assumptions"],
        "limitations": ["NFHS glucose elevation is not screening coverage or causal effect",
                        "Synthetic output is not a district patient, expenditure or policy estimate"],
        "provenance": {"run_digest": run["snapshot_digest"],
                       "data_vintage": snapshot["data_vintage"],
                       "seed": snapshot["seed"], "draws": snapshot["simulation_count"]},
    }
