"""Transparent rule-based decision gate; no cosmetic score can override blockers."""
from __future__ import annotations

from datetime import date

from .schema import DecisionCase, Evidence, REQUIRED_DECISION_VARIABLES, Status


# Each field is either checked and valid (20 points) or blocked (0); model stability
# cannot be inferred from a converged synthetic simulation.
WEIGHTS = {variable: 20 for variable in REQUIRED_DECISION_VARIABLES}


def assess(case: DecisionCase, ledger: list[Evidence], *, as_of: date) -> dict:
    if case.classification == "HYPOTHETICAL":
        return {
            "score": 0, "max_score": 100, "status": "HYPOTHETICAL_ONLY",
            "blockers": ["Synthetic case cannot justify real funding"],
            "components": {key: 0 for key in WEIGHTS},
            "model_stability": "UNASSESSED_FOR_REAL_DECISION",
            "rule": "Each required verified, compatible and current variable earns 20; any blocker forces HOLD",
        }
    components, blockers = {}, []
    for variable, weight in WEIGHTS.items():
        matches = [e for e in ledger if e.variable == variable]
        valid = [e for e in matches if e.status in {Status.OBSERVED, Status.DERIVED}
                 and e.geography in case.geography and e.population == case.population
                 and e.retrieved_on is not None and e.retrieved_on <= as_of
                 and (as_of - e.retrieved_on).days <= 730
                 and e.confidence.value in {"HIGH", "MEDIUM"}]
        # The above is necessary, not sufficient: screening numerator/denominator,
        # intervention effects and costs need methodological review as well.
        components[variable] = weight if valid else 0
        if not valid:
            blockers.append(f"{variable}: verified compatible recent evidence missing")
    blockers.append("Independent methodological validation and model-stability review pending")
    return {"score": sum(components.values()), "max_score": 100,
            "status": "HOLD", "components": components, "blockers": blockers,
            "model_stability": "UNASSESSED_FOR_REAL_DECISION",
            "rule": "Each required verified, compatible and current variable earns 20; any blocker forces HOLD"}
