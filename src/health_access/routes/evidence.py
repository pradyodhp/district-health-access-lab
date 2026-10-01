"""Evidence resource endpoints."""
from fastapi import APIRouter
import csv
from fastapi import HTTPException
from ..decision.evidence import district_ledger, trace
from ..decision.hypotheses import HEALTH_HYPOTHESES
from ..decision.backlog import from_gates
from .context import ROOT
from .cases import readiness_view

router = APIRouter(tags=["evidence"])

@router.get("/indicators")
def indicators():
    with (ROOT / "data/processed/pilot_indicators.csv").open(newline="", encoding="utf-8") as stream:
        return {"rows": list(csv.DictReader(stream)),
                "warning": "Third-party NFHS parse; official district factsheet verification pending. Not screening coverage."}

@router.get("/evidence")
def evidence_room():
    records = district_ledger(ROOT / "data/processed/pilot_indicators.csv")
    return {"records": records, "classification": "OBSERVED_UNVERIFIED",
            "warning": "The ledger is NOT screening coverage; official PDF verification pending."}

@router.get("/evidence/{evidence_id:path}/lineage")
def evidence_lineage(evidence_id: str):
    records = district_ledger(ROOT / "data/processed/pilot_indicators.csv")
    try:
        lineage = trace(evidence_id, records)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"evidence_id": evidence_id, "lineage": lineage,
            "warning": "These observed-unverified indicator records do not validate screening coverage"}

@router.get("/research-backlog")
def evidence_research_backlog():
    return {"classification": "RESEARCH_QUESTIONS_NOT_FINDINGS", "items": from_gates(readiness_view())}

@router.get("/hypotheses")
def hypotheses_view():
    return {"hypotheses": HEALTH_HYPOTHESES, "status": "RESEARCH_QUESTIONS_NOT_FINDINGS"}
