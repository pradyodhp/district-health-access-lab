"""Explainable evidence gates, never a numerical probability of policy readiness."""
from __future__ import annotations

from datetime import date

from .evidence import trace
from .schema import DecisionCase, Evidence, REQUIRED_DECISION_VARIABLES, Status

WEIGHTS = {variable: 20 for variable in REQUIRED_DECISION_VARIABLES}
GATE_VARIABLES = {
    "SCREENING_COVERAGE": "screening_coverage", "POPULATION_DENOMINATOR": "adult_population",
    "INTERVENTION_EFFECT": "intervention_effect", "COST": "intervention_cost",
    "CAPACITY": "facility_capacity", "MODEL_STABILITY": "model_stability",
}


def assess(case: DecisionCase, ledger: list[Evidence], *, as_of: date) -> dict:
    """A compatible download date cannot make an old survey period current.

    Explicit review evidence is required, including for derived parent chains.
    This is a metadata gate, not independent statistical/clinical certification.
    """
    required = set(REQUIRED_DECISION_VARIABLES) | {"model_stability"}
    candidates = [e for e in ledger if e.variable in required]
    dimensions = ("POPULATION", "GEOGRAPHY", "TIME_PERIOD", "NUMERATOR_DENOMINATOR")
    gates = []

    def trusted(e):
        try:
            chain = trace(e.id, ledger)
        except ValueError:
            return False
        return all(parent.status in {Status.OBSERVED, Status.DERIVED}
                   and parent.reviewed_by and parent.confidence.value in {"HIGH", "MEDIUM"}
                   and parent.retrieved_on and parent.retrieved_on <= as_of
                   for parent in chain)

    def compatible(e):
        return (e.geography in case.geography and e.geography_level == case.geography_level
                and e.population == case.population and case.period_start is not None
                and case.period_end is not None and e.period_start == case.period_start
                and e.period_end == case.period_end and e.period_end <= as_of)

    def gate(key, relevant, predicate, missing, action):
        valid = [e for e in relevant if trusted(e) and predicate(e)]
        # All relevant records must be checked; an explicitly invalid record is not
        # hidden by another matching record. Missing/unverified inputs produce HOLD.
        rejected = [e for e in relevant if e.status in {Status.REJECTED, Status.INCOMPATIBLE}]
        mismatched = [e for e in relevant if trusted(e) and not predicate(e)]
        if rejected or mismatched:
            status, reason = "FAIL", "Explicitly rejected or incompatible evidence is present"
        elif valid and len(valid) == len(relevant):
            status, reason = "PASS", "All supplied relevant records pass the stated metadata checks"
        else:
            status, reason = "HOLD", missing
        gates.append({"id": key, "status": status, "reason": reason,
                      "supporting_evidence": [e.id for e in valid],
                      "missing_evidence": [] if status == "PASS" else [missing],
                      "severity": "blocking", "next_research_action": action})

    gate(dimensions[0], candidates, lambda e: e.population == case.population,
         "Compatible population definition missing", "Validate age/sex/cohort definitions against the case")
    gate(dimensions[1], candidates, lambda e: e.geography in case.geography and e.geography_level == case.geography_level,
         "Compatible geography and geographic level missing", "Verify boundaries and named geography; create explicit crosswalk if needed")
    gate(dimensions[2], candidates,
         lambda e: bool(case.period_start and case.period_end and e.period_start == case.period_start
                        and e.period_end == case.period_end and e.period_end <= as_of),
         "Compatible survey/programme period missing; retrieval date is not survey vintage",
         "Source matching period evidence and document any period transformation")
    gate(dimensions[3], [e for e in candidates if e.variable == "screening_coverage"],
         lambda e: e.numerator is not None and e.denominator is not None and e.numerator <= e.denominator,
         "Distinct-person screening numerator and matching denominator missing",
         "Obtain compatible distinct-person counts; visits are not unique people")
    for key, variable in GATE_VARIABLES.items():
        records = [e for e in candidates if e.variable == variable]
        def predicate(e, variable=variable):
            if not compatible(e) or e.indicator_kind != "direct" or e.value is None:
                return False
            if variable == "screening_coverage":
                return (e.unit == "rate" and 0 <= e.value <= 1 and e.numerator is not None
                        and e.denominator is not None and abs(e.value - e.numerator/e.denominator) < 1e-6)
            units = {"adult_population": "people", "intervention_cost": "INR",
                     "intervention_effect": "rate", "facility_capacity": "people", "model_stability": "review"}
            return e.unit == units[variable] and e.value >= 0 and (variable != "intervention_effect" or e.value <= 1)
        gap = ("screening_coverage: NFHS elevation/medicine proxy is not distinct-person screening coverage" if variable == "screening_coverage"
               else f"Verified compatible {variable} evidence and review missing")
        gate(key, records, predicate, gap, f"Obtain and independently review direct {variable} evidence for every case geography")
        # Multi-district cases need each geography, not just one district's record.
        covered = {e.geography for e in records if trusted(e) and predicate(e)}
        if gates[-1]["status"] == "PASS" and covered != set(case.geography):
            gates[-1].update(status="HOLD", reason="Evidence does not cover every case geography",
                             missing_evidence=[f"{variable} for {g}" for g in case.geography if g not in covered])

    components = {v: WEIGHTS[v] if next(g for g in gates if GATE_VARIABLES.get(g["id"]) == v)["status"] == "PASS" else 0
                  for v in REQUIRED_DECISION_VARIABLES}
    blockers = [f"{g['id']}: {g['reason']}" for g in gates if g["status"] != "PASS"]
    if case.classification == "HYPOTHETICAL":
        blockers.insert(0, "Synthetic case cannot justify real funding")
    return {"score": sum(components.values()), "max_score": 100,
            "status": "HYPOTHETICAL_ONLY" if case.classification == "HYPOTHETICAL" else ("READY_FOR_REVIEW" if not blockers else "HOLD"),
            "components": components, "blockers": blockers, "gates": gates,
            "model_stability": "REVIEW_PRESENT" if gates[-1]["status"] == "PASS" else "UNASSESSED_FOR_REAL_DECISION",
            "rule": "Ten blocking metadata/review gates; completeness score is not decision confidence. READY_FOR_REVIEW is not a policy recommendation."}
