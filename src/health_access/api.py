"""Read-only demo API. All output from synthetic presets carries a scenario label."""
from pathlib import Path
import csv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .model import Assumption, Scenario, compare, evaluate
from .scenarios import PRESETS
from .sensitivity import one_at_a_time, salib_morris
from .simulation import simulate

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="District Health Access Lab", version="0.2.0",
              description="Observed indicator table + separate hypothetical simulation. Not policy advice.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])


class Range(BaseModel):
    low: float = Field(ge=0)
    mode: float = Field(ge=0)
    high: float = Field(ge=0)
    unit: str
    rationale: str = Field(min_length=1)

    def domain(self):
        return Assumption(**self.model_dump())


class ScenarioInput(BaseModel):
    eligible: Range
    need_rate: Range
    awareness_rate: Range
    screening_rate: Range
    followup_rate: Range
    capacity: Range
    spend_inr: Range

    def domain(self):
        return Scenario(**{key: getattr(self, key).domain() for key in self.model_fields})


@app.get("/api/health")
def health():
    return {"ok": True, "data_status": "NFHS parse unverified; no observed access-gap estimate"}


@app.get("/api/indicators")
def indicators():
    with (ROOT / "data/processed/pilot_indicators.csv").open(newline="", encoding="utf-8") as stream:
        return {"rows": list(csv.DictReader(stream)),
                "warning": "Third-party NFHS parse; official district factsheet verification pending. Not screening coverage."}


@app.get("/api/presets")
def presets():
    return {"presets": list(PRESETS), "type": "SYNTHETIC, not district data"}


@app.get("/api/scenario/{name}")
def scenario(name: str, draws: int = 500):
    if name not in PRESETS:
        raise HTTPException(404, "Unknown scenario")
    sc = PRESETS[name]()
    return {
        "label": "HYPOTHETICAL EXAMPLE - NOT A DISTRICT ESTIMATE",
        "name": name, "inputs": sc, "point": evaluate(sc),
        "bands": simulate(sc, draws=draws), "sensitivity": one_at_a_time(sc),
        "morris": salib_morris(sc, samples=32),
    }


@app.post("/api/scenario")
def custom_scenario(payload: ScenarioInput):
    try:
        sc = payload.domain()
        return {"label": "USER-SUPPLIED HYPOTHETICAL SCENARIO", "point": evaluate(sc),
                "bands": simulate(sc, draws=500), "sensitivity": one_at_a_time(sc)}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/compare/{left}/{right}")
def compare_presets(left: str, right: str):
    if left not in PRESETS or right not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    return {"label": "HYPOTHETICAL SCENARIO COMPARISON - NOT A POLICY ESTIMATE",
            "left": left, "right": right,
            "comparison": compare(evaluate(PRESETS[left]()), evaluate(PRESETS[right]()))}


if (ROOT / "web/dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "web/dist", html=True), name="web")
