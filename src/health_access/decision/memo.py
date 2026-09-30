"""Evidence-gated memo from a stored run, never a synthetic policy recommendation."""
from __future__ import annotations


def make_memo(run: dict, readiness: dict, evidence: list[dict]) -> dict:
    if run.get("classification") != "HYPOTHETICAL":
        raise ValueError("Only hypothetical run memos supported")
    snapshot = run["snapshot"]
    # v2 context is authoritative. Caller-provided current evidence cannot alter it.
    readiness = snapshot.get("readiness", readiness)
    evidence = snapshot.get("evidence_snapshot", evidence)
    case = snapshot["case"]
    bands = run["bands"]["screened"]
    blockers = list(readiness["blockers"]) + [
        "Verified compatible adult population denominator missing",
        "Actual screening coverage numerator/denominator missing",
        "Validated intervention costs and effects missing",
        "Facility capacity and independent model-stability review missing",
    ]
    return {
        "title": f"Decision memo | {case['name']}",
        "executive_summary": "DECISION ON HOLD. The model is a training example; available evidence does not support a district funding choice.",
        "decision": "DECISION ON HOLD - no real funding allocation justified",
        "decision_question": "Where could an NCD screening budget close the most verified screening gap per rupee?",
        "classification": "HYPOTHETICAL",
        "case_id": case["case_id"], "case_version": case["version"],
        "run_id": run["run_id"], "scenario_id": snapshot["scenario_id"],
        "scenario_version": snapshot["scenario_version"],
        "model_version": case["model_version"],
        "objective": case["objective"], "population": case["population"],
        "geography": case["geography"], "horizon_months": case["horizon_months"],
        "what_we_know": ["The pilot ledger contains third-party NFHS-5 indicator transcription; official fact-sheet check is pending",
                         "The recorded percentages concern elevated measures or medicine use, not screening coverage"],
        "what_we_do_not_know": blockers,
        "illustrative_screened_band": bands,
        "uncertainty": "p10/p50/p90 are conditional on invented training distributions; not empirical confidence.",
        "scenario_comparison": "Compare stored hypothetical run IDs before inferring a model change; no policy comparison is supported.",
        "key_assumptions": {key: {"low": value["low"], "mode": value["mode"], "high": value["high"],
                                    "unit": value["unit"], "status": "HYPOTHETICAL"}
                            for key, value in snapshot["inputs"].items()},
        "sensitivity": run.get("analyses", {}).get("sensitivity", []),
        "robustness": run.get("analyses", {}).get("robustness", {}),
        "allocation_analysis": run.get("analyses", {}).get("allocation", {"status": "NOT_RUN"}),
        "readiness": readiness,
        "research_questions": run.get("analyses", {}).get("research", []),
        "what_could_change": ["Verified compatible screening counts and adult denominators could change whether a gap can be assessed",
                              "Validated cost and effect studies could change allocation feasibility",
                              "Assumed awareness and capacity ranges can change rankings inside the training model only"],
        "evidence_summary": {"records": len(evidence),
                             "unverified": sum(e.get("status") == "OBSERVED_UNVERIFIED" for e in evidence),
                             "not_screening_coverage": True},
        "blockers": blockers,
        "next_research": ["Verify official district factsheets against transcription",
                          "Obtain compatible adult denominators and actual screening counts",
                          "Validate intervention costs, effects, capacity and period"],
        "alternatives": ["Do not allocate real funds from the synthetic scenario",
                         "Use the workbench only to compare hypothetical assumptions"],
        "methodology": "Versioned hypothetical case, triangular distributions, seeded Monte Carlo; real decision blocked by evidence gate.",
        "limitations": ["NFHS glucose elevation is not screening coverage or causal effect",
                        "Synthetic output is not a district patient, expenditure or policy estimate"],
        "provenance": {"run_digest": run["snapshot_digest"], "output_digest": run.get("output_digest"),
                       "data_vintage": snapshot["data_vintage"],
                       "seed": snapshot["seed"], "draws": snapshot["simulation_count"]},
    }
