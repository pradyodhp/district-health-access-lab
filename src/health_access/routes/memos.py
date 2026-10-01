"""Memos resource endpoints."""
from fastapi import APIRouter
from ..decision.memo import make_memo
from .runs import get_run

router = APIRouter(tags=["memos"])

@router.get("/runs/{run_id}/memo")
def run_memo(run_id: str):
    run = get_run(run_id)
    return make_memo(run, run["snapshot"]["readiness"], run["snapshot"]["evidence_snapshot"])
