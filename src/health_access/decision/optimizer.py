"""Small, auditable grid optimizer for hypothetical allocations only.

Discrete enumeration is deliberate: it exposes feasibility and interactions rather than
hiding a solver behind unsupported empirical effects. It is not a funding recommendation.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isfinite


@dataclass(frozen=True)
class Option:
    id: str
    district: str
    min_inr: int
    max_inr: int
    step_inr: int
    assumed_people_per_inr: float
    max_people: float
    depends_on: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.id or not self.district or not all(isinstance(v, int) for v in (self.min_inr, self.max_inr, self.step_inr)) or self.min_inr < 0 or self.max_inr < self.min_inr:
            raise ValueError("Invalid option")
        if self.step_inr <= 0 or (self.max_inr - self.min_inr) % self.step_inr:
            raise ValueError("Allocation grid must exactly span limits")
        if not isfinite(self.assumed_people_per_inr) or self.assumed_people_per_inr < 0:
            raise ValueError("Invalid illustrative yield")
        if not isfinite(self.max_people) or self.max_people < 0:
            raise ValueError("Invalid illustrative capacity")


def optimize(options: list[Option], *, budget_inr: int,
             district_capacity: dict[str, float], classification: str = "HYPOTHETICAL") -> dict:
    if classification != "HYPOTHETICAL":
        raise ValueError("Real funding optimization requires verified evidence gates")
    if not isinstance(budget_inr, int) or budget_inr < 0 or not options or len(options) > 8:
        raise ValueError("Invalid budget or option count")
    if len({o.id for o in options}) != len(options):
        raise ValueError("Duplicate option ID")
    ids = {o.id for o in options}
    if any(d not in ids or d == o.id for o in options for d in o.depends_on):
        raise ValueError("Missing or self dependency")
    dependencies = {o.id: o.depends_on for o in options}
    def visit(key, active, visited):
        if key in active:
            raise ValueError("Cyclic option dependencies")
        if key in visited:
            return
        active.add(key)
        for dependency in dependencies[key]:
            visit(dependency, active, visited)
        active.remove(key)
        visited.add(key)
    visited = set()
    for key in ids:
        visit(key, set(), visited)
    if any(o.district not in district_capacity for o in options):
        raise ValueError("Each option requires a district capacity")
    if any(not isfinite(v) or v < 0 for v in district_capacity.values()):
        raise ValueError("Invalid district capacity")
    if sum(o.min_inr for o in options) > budget_inr:
        return {"status": "INFEASIBLE", "reason": "Minimum allocations exceed budget", "classification": classification}
    grids = [range(o.min_inr, o.max_inr + 1, o.step_inr) for o in options]
    count = 1
    for grid in grids:
        count *= len(grid)
    if count > 100_000:
        raise ValueError("Grid too large: reduce options or increase allocation steps")
    best = None
    for vector in product(*grids):
        spend = sum(vector)
        if spend > budget_inr:
            continue
        allocations = dict(zip((o.id for o in options), vector))
        if any(allocations[o.id] > 0 and any(allocations[d] == 0 for d in o.depends_on) for o in options):
            continue
        district_raw = {district: 0.0 for district in district_capacity}
        for option, amount in zip(options, vector):
            district_raw[option.district] += min(amount * option.assumed_people_per_inr, option.max_people)
        reached = {d: min(raw, district_capacity[d]) for d, raw in district_raw.items()}
        outcome = sum(reached.values())
        # Stable tie-break: maximize reach, minimize spend, then lexicographic vector.
        rank = (outcome, -spend, tuple(-v for v in vector))
        if best is None or rank > best[0]:
            best = (rank, allocations, reached, spend, outcome)
    if best is None:
        return {"status": "INFEASIBLE", "reason": "No feasible allocation with dependencies", "classification": classification}
    _, allocations, reached, spend, outcome = best
    return {"status": "HYPOTHETICAL_OPTIMUM", "classification": classification,
            "allocations_inr": allocations, "screened_by_district": reached,
            "illustrative_people_screened": outcome, "budget_inr": budget_inr,
            "spend_inr": spend, "unspent_inr": budget_inr - spend,
            "cost_per_person_inr": spend / outcome if outcome > 0 else None,
            "district_capacity_utilization": {d: (reached[d] / cap if cap else None)
                                               for d, cap in district_capacity.items()},
            "optimality_scope": "Optimal under the specified model and discrete grid constraints, not real-world optimality",
            "method": "bounded exhaustive grid, hypothetical yields; shared district capacity caps; not real funding advice"}
