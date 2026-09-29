"""A bounded hypothetical one-input what-if, not a causal reversal claim."""
from __future__ import annotations
from dataclasses import replace

from ..model import Scenario, evaluate


def reversal_scan(left: Scenario, right: Scenario, *, field: str = "awareness_rate", steps: int = 20) -> dict:
    if field not in {"eligible", "need_rate", "awareness_rate", "screening_rate", "followup_rate", "capacity", "spend_inr"}:
        raise ValueError("Unknown assumption")
    if not 2 <= steps <= 100:
        raise ValueError("Steps out of bounds")
    # Vary a single shared quantile for the selected assumption; hold all other
    # inputs at their modes to keep this a transparent conditional what-if.
    outcomes = []
    for i in range(steps + 1):
        q = i / steps
        values = []
        for scenario in (left, right):
            old = getattr(scenario, field)
            value = old.low + q * (old.high - old.low)
            values.append(evaluate(replace(scenario, **{field: replace(old, mode=value)}))["screened"])
        delta = values[1] - values[0]
        outcomes.append({"assumption_quantile": q, "left_screened": values[0],
                         "right_screened": values[1], "difference": delta,
                         "preferred": "right" if delta > 1e-9 else "left" if delta < -1e-9 else "tie"})
    crossings = []
    for before, after in zip(outcomes, outcomes[1:]):
        if before["preferred"] != after["preferred"]:
            crossings.append({"between_quantiles": [before["assumption_quantile"], after["assumption_quantile"]],
                              "from": before["preferred"], "to": after["preferred"]})
    return {"classification": "HYPOTHETICAL", "field": field, "steps": steps,
            "sampled_preferences": outcomes, "preference_changes": crossings,
            "warning": "One-at-a-time assumed-input scan, not an observed or causal reversal threshold"}
