"""Scenario-only cohort funnel. None of its parameters are estimated from NFHS."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Assumption:
    low: float
    mode: float
    high: float
    unit: str
    rationale: str

    def __post_init__(self):
        if not (isfinite(self.low) and isfinite(self.mode) and isfinite(self.high)):
            raise ValueError("Inputs must be finite")
        if not 0 <= self.low <= self.mode <= self.high:
            raise ValueError("Invalid assumption range")
        if self.unit == "rate" and self.high > 1:
            raise ValueError("A rate cannot exceed one")
        if self.unit not in {"rate", "people", "INR"}:
            raise ValueError("Unknown unit")
        if not self.rationale:
            raise ValueError("Assumption rationale required")


@dataclass(frozen=True)
class Scenario:
    eligible: Assumption
    need_rate: Assumption
    awareness_rate: Assumption
    screening_rate: Assumption
    followup_rate: Assumption
    capacity: Assumption
    spend_inr: Assumption

    def __post_init__(self):
        expected = {"eligible": "people", "capacity": "people", "spend_inr": "INR",
                    "need_rate": "rate", "awareness_rate": "rate",
                    "screening_rate": "rate", "followup_rate": "rate"}
        for field, unit in expected.items():
            if getattr(self, field).unit != unit:
                raise ValueError(f"{field} requires unit {unit}")


def funnel(eligible: float, need_rate: float, awareness_rate: float,
           screening_rate: float, followup_rate: float, capacity: float,
           spend_inr: float) -> dict[str, float]:
    """Synthetic *eligible cohort* transitions, not historical patient counts.

    Here `screening_rate` is the conditional probability that an aware person
    in the eligible-need cohort gets screened. It is NOT population coverage.
    """
    values = (eligible, need_rate, awareness_rate, screening_rate,
              followup_rate, capacity, spend_inr)
    if any(not isfinite(v) or v < 0 for v in values):
        raise ValueError("Inputs must be finite and nonnegative")
    if any(r > 1 for r in (need_rate, awareness_rate, screening_rate, followup_rate)):
        raise ValueError("Rates cannot exceed one")
    need = eligible * need_rate
    aware = need * awareness_rate
    screened = min(aware * screening_rate, capacity)
    followed_up = screened * followup_rate
    return {
        "eligible": eligible, "need_proxy": need, "aware": aware,
        "screened": screened, "followed_up": followed_up,
        "unscreened_need_proxy": need - screened,
        "spend_inr": spend_inr,
    }


def evaluate(scenario: Scenario) -> dict[str, float]:
    a = scenario
    return funnel(a.eligible.mode, a.need_rate.mode, a.awareness_rate.mode,
                  a.screening_rate.mode, a.followup_rate.mode,
                  a.capacity.mode, a.spend_inr.mode)


def compare(base: dict[str, float], proposal: dict[str, float]) -> dict[str, float | None]:
    extra = proposal["screened"] - base["screened"]
    cost = proposal["spend_inr"] - base["spend_inr"]
    return {
        "incremental_screened": extra,
        "incremental_spend_inr": cost,
        "inr_per_extra_screened": cost / extra if extra > 0 and cost >= 0 else None,
    }
