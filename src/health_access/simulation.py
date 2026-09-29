"""Reproducible uncertainty propagation of clearly labeled assumptions."""
import random

from .model import Scenario, funnel


def simulate(scenario: Scenario, *, draws: int = 10_000, seed: int = 42):
    if not 100 <= draws <= 1_000_000:
        raise ValueError("Draws must be between 100 and 1,000,000")
    rng = random.Random(seed)
    fields = ("eligible", "need_rate", "awareness_rate", "screening_rate",
              "followup_rate", "capacity", "spend_inr")
    samples = {key: [] for key in funnel(100, .5, .5, .5, .5, 100, 0)}
    for _ in range(draws):
        values = [rng.triangular(getattr(scenario, field).low,
                                 getattr(scenario, field).high,
                                 getattr(scenario, field).mode)
                  for field in fields]
        result = funnel(*values)
        for key, value in result.items():
            samples[key].append(value)
    def percentile(sorted_values, fraction):
        pos = fraction * (len(sorted_values) - 1)
        left = int(pos)
        return sorted_values[left] * (1 - pos + left) + sorted_values[min(left + 1, len(sorted_values) - 1)] * (pos - left)
    return {key: {f"p{p}": percentile(sorted(values), p / 100) for p in (10, 50, 90)}
            for key, values in samples.items()}
