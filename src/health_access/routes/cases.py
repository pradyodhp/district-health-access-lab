"""Cases resource endpoints."""
from fastapi import APIRouter
from ..decision.cases import pilot_case
from ..decision.evidence import district_ledger
from ..decision.readiness import assess
from ..decision.schema import DecisionCase
from .context import ROOT

router = APIRouter(tags=["cases"])

@router.get("/case")
def case_view():
    return pilot_case()

@router.post("/case/readiness")
def case_readiness(payload: DecisionCase):
    from datetime import date
    return assess(payload, district_ledger(ROOT / "data/processed/pilot_indicators.csv"), as_of=date.today())

@router.get("/readiness")
def readiness_view():
    from datetime import date
    return assess(pilot_case(), district_ledger(ROOT / "data/processed/pilot_indicators.csv"), as_of=date.today())
