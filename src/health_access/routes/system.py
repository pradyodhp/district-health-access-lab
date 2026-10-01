"""System resource endpoints."""
from fastapi import APIRouter

router = APIRouter(tags=["system"])

@router.get("/health")
def health():
    return {"ok": True, "service": "district-health-access-lab", "api_version": "0.3.0", "engine_version": "1.0.0", "run_format": "2", "storage": "local JSON, not durable hosted persistence", "data_status": "NFHS parse unverified; no observed access-gap estimate"}
