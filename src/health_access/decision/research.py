"""Heuristic research backlog, never presented as formal Bayesian VOI."""
from __future__ import annotations

from .schema import Confidence, Evidence, Status
from ..model import Scenario
from ..sensitivity import one_at_a_time


def backlog(scenario: Scenario, evidence: list[Evidence], *, effort: dict[str, int]) -> list[dict]:
    swings = {r["input"]: max(0, r["swing"]) for r in one_at_a_time(scenario)}
    max_swing = max(swings.values(), default=0)
    results = []
    for name, impact in swings.items():
        field = getattr(scenario, name)
        width = field.high - field.low
        relative_width = width / max(field.mode, 1e-9) if field.mode > 0 else width
        matching = [e for e in evidence if e.variable == name]
        confidence = matching[0].confidence if matching else Confidence.UNKNOWN
        status = matching[0].status if matching else Status.ASSUMED
        work = effort.get(name, 3)
        if not 1 <= work <= 5:
            raise ValueError("Effort is an ordinal 1-5 estimate")
        score = round(100 * (impact / max_swing if max_swing else 0)
                      * min(relative_width, 1) * (1 if confidence in {Confidence.LOW, Confidence.UNKNOWN} else .5)
                      / work, 2)
        results.append({"variable": name, "score": score, "impact_swing_people": impact,
                        "relative_range_width": relative_width, "effort_1_to_5": work,
                        "confidence": confidence.value, "evidence_status": status.value,
                        "method": "heuristic impact x range width x confidence factor / effort; not Bayesian VOI",
                        "research_action": "Find a compatible source and validate its cohort, period and geography"})
    return sorted(results, key=lambda r: (-r["score"], r["variable"]))
