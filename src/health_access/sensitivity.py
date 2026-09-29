"""Sensitivity on illustrative assumptions, not an empirical policy ranking."""
from dataclasses import replace

from .model import Assumption, Scenario, evaluate


def one_at_a_time(scenario: Scenario, outcome: str = "screened") -> list[dict]:
    """Show local low/high shifts; this is NOT a SALib global Sobol result."""
    names = ("eligible", "need_rate", "awareness_rate", "screening_rate",
             "followup_rate", "capacity", "spend_inr")
    center = evaluate(scenario)[outcome]
    findings = []
    for name in names:
        original = getattr(scenario, name)
        low_scenario = replace(scenario, **{name: replace(original, mode=original.low)})
        high_scenario = replace(scenario, **{name: replace(original, mode=original.high)})
        low = evaluate(low_scenario)[outcome]
        high = evaluate(high_scenario)[outcome]
        findings.append({"input": name, "low_outcome": low, "baseline": center,
                         "high_outcome": high, "swing": high - low,
                         "method": "one-at-a-time scenario range, not global sensitivity"})
    return sorted(findings, key=lambda row: row["swing"], reverse=True)


def salib_morris(scenario: Scenario, *, samples: int = 128, seed: int = 42) -> list[dict]:
    """Morris global screen using SALib; transparent bounds, deterministic seed."""
    from SALib.sample.morris import sample
    from SALib.analyze.morris import analyze
    import numpy as np

    names = ("eligible", "need_rate", "awareness_rate", "screening_rate",
             "followup_rate", "capacity")
    ranges = [getattr(scenario, name) for name in names]
    problem = {"num_vars": len(names), "names": list(names),
               "bounds": [[r.low, r.high] for r in ranges]}
    # Zero-width ranges make Morris undefined; omit those dimensions.
    varying = [(name, r) for name, r in zip(names, ranges) if r.high > r.low]
    if len(varying) < 2:
        return []
    problem = {"num_vars": len(varying), "names": [n for n, _ in varying],
               "bounds": [[r.low, r.high] for _, r in varying]}
    points = sample(problem, N=samples, seed=seed)
    outputs = []
    for point in points:
        updated = {n: replace(r, mode=float(v)) for (n, r), v in zip(varying, point)}
        outputs.append(evaluate(replace(scenario, **updated))["screened"])
    result = analyze(problem, points, np.asarray(outputs, dtype=float), print_to_console=False, seed=seed)
    return sorted([{"input": name, "mu_star": float(mu), "sigma": float(sigma),
                    "method": "SALib Morris; synthetic screening outcome"}
                   for name, mu, sigma in zip(problem["names"], result["mu_star"], result["sigma"])],
                  key=lambda x: x["mu_star"], reverse=True)
