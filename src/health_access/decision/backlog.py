"""Machine-readable missing-evidence work, not a value-of-information estimator."""
def from_gates(readiness: dict) -> list[dict]:
    sources = {
        "SCREENING_COVERAGE": ["District programme distinct-person screening registers", "Published district screening reports"],
        "POPULATION_DENOMINATOR": ["Age/sex-compatible official population tables"],
        "COST": ["Programme accounts with price year and scope"],
        "INTERVENTION_EFFECT": ["Peer-reviewed intervention studies with transportability review"],
        "CAPACITY": ["Facility service registers and staffing rosters"],
        "MODEL_STABILITY": ["Independent methodological review and model validation report"],
    }
    return [{"id": "research-" + g["id"].lower(), "question": g["next_research_action"],
             "why_it_matters": g["reason"], "decision_gate": g["id"],
             "current_evidence": g["supporting_evidence"], "missing_evidence": g["missing_evidence"],
             "expected_impact": "Required for decision readiness; no numerical VOI claimed",
             "urgency": "HIGH", "owner": None, "status": "MISSING",
             "source_candidates": sources.get(g["id"], ["Compatible official metadata and source documentation"])}
            for g in readiness["gates"] if g["status"] != "PASS"]
