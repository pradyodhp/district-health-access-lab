"""Paired-draw hypothetical robustness and explicit threshold uncertainty."""
from __future__ import annotations

import random
from dataclasses import dataclass
from math import isfinite, sqrt

from ..model import Scenario, funnel

FIELDS = ("eligible", "need_rate", "awareness_rate", "screening_rate",
          "followup_rate", "capacity", "spend_inr")


@dataclass(frozen=True)
class Thresholds:
    minimum_screened: float | None = None
    maximum_cost_per_person_inr: float | None = None
    minimum_probability: float = .7

    def __post_init__(self):
        values = (self.minimum_screened, self.maximum_cost_per_person_inr)
        if any(v is not None and (not isfinite(v) or v < 0) for v in values):
            raise ValueError("Invalid threshold")
        if not 0 <= self.minimum_probability <= 1:
            raise ValueError("Probability must be a rate")


def evaluate_thresholds(samples: list[dict], threshold: Thresholds,
                        *, classification: str = "HYPOTHETICAL") -> dict:
    if not samples:
        return {"status": "CANNOT_ASSESS", "reason": "No model draws"}
    if classification != "HYPOTHETICAL":
        return {"status": "CANNOT_ASSESS", "reason": "Real evidence gate not satisfied"}
    if threshold.minimum_screened is None and threshold.maximum_cost_per_person_inr is None:
        return {"status": "CANNOT_ASSESS", "reason": "No target threshold specified"}
    passed = 0
    for sample in samples:
        if threshold.minimum_screened is not None and sample["screened"] < threshold.minimum_screened:
            continue
        if threshold.maximum_cost_per_person_inr is not None:
            if sample["screened"] <= 0 or sample["spend_inr"] / sample["screened"] > threshold.maximum_cost_per_person_inr:
                continue
        passed += 1
    probability = passed / len(samples)
    # Borderline band explicitly prevents false binary certainty near the cutoff.
    status = ("MEETS_IN_HYPOTHETICAL_MODEL" if probability >= threshold.minimum_probability + .05 else
              "DOES_NOT_MEET_IN_HYPOTHETICAL_MODEL" if probability < threshold.minimum_probability - .05 else
              "BORDERLINE_IN_HYPOTHETICAL_MODEL")
    return {"status": status, "probability": probability, "draws": len(samples),
            "target_probability": threshold.minimum_probability,
            "warning": "Conditional on invented distributions, not real-world success probability"}


def compare_scenarios(scenarios: dict[str, Scenario], *, draws: int = 1000,
                      seed: int = 42, classification: str = "HYPOTHETICAL") -> dict:
    if classification != "HYPOTHETICAL":
        raise ValueError("Real robustness requires verified compatible input evidence")
    if not 100 <= draws <= 100_000 or not 2 <= len(scenarios) <= 8:
        raise ValueError("Invalid draw or scenario count")
    rng = random.Random(seed)
    wins = {name: 0.0 for name in scenarios}
    paired = {name: [] for name in scenarios}
    names = sorted(scenarios)
    def triangular_quantile(low, mode, high, q):
        if high == low:
            return low
        split = (mode - low) / (high - low)
        return (low + sqrt(q * (high - low) * (mode - low)) if q < split
                else high - sqrt((1 - q) * (high - low) * (high - mode)))

    for _ in range(draws):
        # Shared quantile per input models a common uncertainty source, avoiding
        # independent resampling that would make rankings less comparable.
        quantiles = [rng.random() for _ in FIELDS]
        results = {}
        for name in names:
            scenario = scenarios[name]
            samples = [triangular_quantile(getattr(scenario, field).low,
                                           getattr(scenario, field).mode,
                                           getattr(scenario, field).high, q)
                       for field, q in zip(FIELDS, quantiles)]
            outcome = funnel(*samples)
            paired[name].append(outcome)
            results[name] = outcome["screened"]
        maximum = max(results.values())
        ties = [n for n, value in results.items() if abs(value - maximum) < 1e-9]
        for name in ties:
            wins[name] += 1 / len(ties)
    thresholds = {}
    for name in names:
        values = sorted(s["screened"] for s in paired[name])
        thresholds[name] = {"p10": values[int(.1 * (draws - 1))],
                            "p50": values[int(.5 * (draws - 1))],
                            "p90": values[int(.9 * (draws - 1))]}
    # Preserve a compact response: detailed paired draws are kept in the function
    # only to compute shares, not shipped as an unbounded API payload.
    return {"classification": "HYPOTHETICAL", "seed": seed, "draws": draws,
            "bands": thresholds,
            "preference_share": {name: wins[name] / draws for name in names},
            "ties_split_evenly": True,
            "warning": "Conditional on synthetic assumptions; not empirical decision confidence",
            "reversal_note": "Vary the shared assumptions and compare preference share; no empirical reversal threshold claimed"}
