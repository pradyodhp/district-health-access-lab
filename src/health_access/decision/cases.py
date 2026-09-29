"""Healthcare pilot adapter: domain-neutral case schema, explicit synthetic status."""
from .schema import Constraint, DecisionCase, Intervention


def pilot_case() -> DecisionCase:
    return DecisionCase(
        case_id="ncd-screening-pilot", version="1.0.0", name="District NCD screening pilot",
        objective="maximize_additional_screened",
        geography=("Maharashtra/Mumbai", "Maharashtra/Pune", "Maharashtra/Gadchiroli",
                   "Odisha/Khordha", "Odisha/Koraput", "Odisha/Malkangiri"),
        population="hypothetical adults 15+ cohort", service="blood-glucose screening",
        horizon_months=24, budget_inr=0, target_outcome="additional adults screened",
        interventions=(),
        constraints=(Constraint(name="evidence-gate", rule="Do not infer screening coverage from NFHS glucose indicator"),),
        classification="HYPOTHETICAL", model_version="0.3.0",
    )
