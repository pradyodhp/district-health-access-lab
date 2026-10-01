"""Analysis resource endpoints."""
from fastapi import APIRouter
from fastapi import HTTPException, Query
from ..requests import OptimizationRequest
from ..decision.research import backlog
from ..decision.optimizer import Option, optimize
from ..decision.robustness import Thresholds, compare_scenarios, evaluate_thresholds
from ..decision.reversal import reversal_scan
from ..scenarios import PRESETS

router = APIRouter(tags=["analysis"])

@router.get("/research/{preset}")
def research_view(preset: str):
    if preset not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    return {"classification": "HYPOTHETICAL", "items": backlog(PRESETS[preset](), [], effort={}),
            "warning": "Heuristic research queue, not causal effects or formal value-of-information"}

@router.post("/optimize")
def optimize_view(payload: OptimizationRequest):
    try:
        options = [Option(**value.model_dump()) for value in payload.options]
        return optimize(options, budget_inr=payload.budget_inr,
                        district_capacity=payload.district_capacity,
                        classification=payload.classification)
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("/robustness")
def robustness_view(draws: int = Query(300, ge=100, le=10_000), seed: int = Query(42, ge=0, le=2**32-1)):
    return compare_scenarios({name: factory() for name, factory in PRESETS.items()},
                             draws=draws, seed=seed)

@router.get("/reversal/{left}/{right}")
def reversal_view(left: str, right: str, field: str = "awareness_rate",
                  steps: int = Query(20, ge=2, le=100)):
    if left not in PRESETS or right not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    try:
        return reversal_scan(PRESETS[left](), PRESETS[right](), field=field, steps=steps)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("/threshold/{preset}")
def threshold_view(preset: str, minimum_screened: float = Query(250, ge=0, allow_inf_nan=False),
                   minimum_probability: float = Query(.7, ge=0, le=1),
                   draws: int = Query(300, ge=100, le=10_000)):
    if preset not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    from ..decision.robustness import FIELDS
    import random
    from ..model import funnel
    rng = random.Random(42)
    scenario = PRESETS[preset]()
    samples = [funnel(*[rng.triangular(getattr(scenario, f).low, getattr(scenario, f).high,
                                      getattr(scenario, f).mode) for f in FIELDS]) for _ in range(draws)]
    try:
        return evaluate_thresholds(samples, Thresholds(minimum_screened=minimum_screened,
                                                       minimum_probability=minimum_probability))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
