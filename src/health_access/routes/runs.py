"""Runs resource endpoints."""
from fastapi import APIRouter
from fastapi import HTTPException
from ..requests import RunRequest
from ..decision.evidence import district_ledger
from ..decision.runs import RunStore, make_run, replay
from ..decision.comparison import compare_runs
from .context import ROOT

router = APIRouter(tags=["runs"])

@router.post("/runs")
def create_run(payload: RunRequest):
    try:
        run = make_run(payload.case, payload.inputs.domain(), scenario_id=payload.scenario_id,
                       scenario_version=payload.scenario_version,
                       draws=payload.simulation_count, seed=payload.seed,
                       evidence=district_ledger(ROOT / "data/processed/pilot_indicators.csv"))
        return RunStore(ROOT / "runs").save(run)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("/runs/{run_id}")
def get_run(run_id: str):
    try:
        return RunStore(ROOT / "runs").get(run_id)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        raise HTTPException(404, "Run not found") from exc

@router.get("/runs/{left_run_id}/compare/{right_run_id}")
def run_compare(left_run_id: str, right_run_id: str):
    try:
        return compare_runs(get_run(left_run_id), get_run(right_run_id))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

@router.get("/runs/{run_id}/replay")
def replay_run(run_id: str):
    try:
        run = get_run(run_id)
        if run["snapshot"]["simulation_count"] > 10_000:
            raise ValueError("Stored run exceeds API replay compute limit; use offline replay")
        return replay(run)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
