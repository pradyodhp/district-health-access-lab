"""Scenarios resource endpoints."""
from fastapi import APIRouter
from fastapi import HTTPException, Query
from ..requests import ScenarioInput
from ..model import compare, evaluate
from ..scenarios import PRESETS
from ..sensitivity import one_at_a_time, salib_morris
from ..simulation import simulate

router = APIRouter(tags=["scenarios"])

@router.get("/presets")
def presets():
    return {"presets": list(PRESETS), "type": "SYNTHETIC, not district data"}

@router.get("/scenario/{name}")
def scenario(name: str, draws: int = Query(500, ge=100, le=10_000)):
    if name not in PRESETS:
        raise HTTPException(404, "Unknown scenario")
    sc = PRESETS[name]()
    return {
        "label": "HYPOTHETICAL EXAMPLE - NOT A DISTRICT ESTIMATE",
        "name": name, "inputs": sc, "point": evaluate(sc),
        "bands": simulate(sc, draws=draws), "sensitivity": one_at_a_time(sc),
        "morris": salib_morris(sc, samples=32),
    }

@router.post("/scenario")
def custom_scenario(payload: ScenarioInput):
    try:
        sc = payload.domain()
        return {"label": "USER-SUPPLIED HYPOTHETICAL SCENARIO", "point": evaluate(sc),
                "bands": simulate(sc, draws=500), "sensitivity": one_at_a_time(sc)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("/compare/{left}/{right}")
def compare_presets(left: str, right: str):
    if left not in PRESETS or right not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    return {"label": "HYPOTHETICAL SCENARIO COMPARISON - NOT A POLICY ESTIMATE",
            "left": left, "right": right,
            "comparison": compare(evaluate(PRESETS[left]()), evaluate(PRESETS[right]()))}
