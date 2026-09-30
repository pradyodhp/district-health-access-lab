"""Sensitivity on illustrative assumptions, not an empirical policy ranking."""
from dataclasses import replace

from .model import Scenario, evaluate


def one_at_a_time(scenario: Scenario, outcome: str = "screened") -> list[dict]:
    """Low/high sweep per assumption; heuristic screen only, not a fitted importance ranking."""
    base = evaluate(scenario)
    base_value = base[outcome]
    rows = []
    for assumption in scenario.assumptions:
        results = {}
        for label in ("low", "high"):
            varied = replace(
                scenario,
                assumptions=[
                    replace(a, mode=getattr(a, label)) if a.name == assumption.name else a
                    for a in scenario.assumptions
                ],
            )
            results[label] = evaluate(varied)[outcome]
        swing = abs(results["high"] - results["low"])
        rows.append(
            {
                "assumption": assumption.name,
                "unit": assumption.unit,
                "rationale": assumption.rationale,
                "low": results["low"],
                "base": base_value,
                "high": results["high"],
                "swing": swing,
                "interpretation": (
                    "One-at-a-time swing on a synthetic teaching model; "
                    "does not rank real-world importance or validate any input."
                ),
            }
        )
    return sorted(rows, key=lambda row: row["swing"], reverse=True)


def morris_screen(scenario: Scenario, outcome: str = "screened", trajectories: int = 20):
    """SALib Morris on training ranges; illustrates screening mechanics, not empirical drivers."""
    from SALib.analyze import morris
    from SALib.sample import morris as sample_morris

    names = [a.name for a in scenario.assumptions]
    bounds = [[a.low, a.high] for a in scenario.assumptions]
    problem = {"num_vars": len(names), "names": names, "bounds": bounds}
    samples = sample_morris.sample(problem, trajectories, num_levels=4, seed=scenario.seed)

    def run(row):
        varied = replace(
            scenario,
            assumptions=[
                replace(a, mode=float(value)) for a, value in zip(scenario.assumptions, row)
            ],
        )
        return evaluate(varied)[outcome]

    results = [run(row) for row in samples]
    analysis = morris.analyze(problem, samples, results, seed=scenario.seed)
    return [
        {
            "assumption": name,
            "mu_star": float(mu),
            "sigma": float(sigma),
            "interpretation": (
                "Morris elementary-effects screen over assumed ranges; "
                "not evidence of real-world importance."
            ),
        }
        for name, mu, sigma in zip(names, analysis["mu_star"], analysis["sigma"])
    ]
