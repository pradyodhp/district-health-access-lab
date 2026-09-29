"""Consulting hypothesis tree; untested branches are research questions, not claims."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Hypothesis:
    id: str
    branch: str
    question: str
    metric: str
    evidence_variable: str
    model_input: str | None
    research_action: str


HEALTH_HYPOTHESES = (
    Hypothesis("demand-awareness", "Demand", "Is low awareness limiting screening?",
               "aware eligible share", "awareness_rate", "awareness_rate", "Find population survey or field interviews"),
    Hypothesis("demand-willingness", "Demand", "Is willingness a barrier?",
               "opt-in share", "willingness", None, "Interview eligible adults"),
    Hypothesis("access-distance", "Access", "Does distance reduce access?",
               "travel time", "travel_time", None, "Measure district travel times"),
    Hypothesis("access-hours", "Access", "Are operating hours a barrier?",
               "available hours", "operating_hours", None, "Audit clinic opening hours"),
    Hypothesis("capacity-slots", "Capacity", "Are screening slots saturated?",
               "unique monthly slots", "facility_capacity", "capacity", "Audit site staffing and slots"),
    Hypothesis("capacity-equipment", "Capacity", "Is equipment limiting throughput?",
               "working devices", "equipment", None, "Audit functioning equipment"),
    Hypothesis("retention-followup", "Retention", "Do screened adults complete follow-up?",
               "linked follow-up share", "followup_rate", "followup_rate", "Link visits without double-counting"),
)
