"""Read-only demo API. All output from synthetic presets carries a scenario label."""
from pathlib import Path
import csv

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .model import Assumption, Scenario, compare, evaluate
from .decision.cases import pilot_case
from .decision.evidence import district_ledger
from .decision.readiness import assess
from .decision.schema import DecisionCase
from .decision.runs import RunStore, make_run
from .decision.hypotheses import HEALTH_HYPOTHESES
from .decision.research import backlog
from .decision.optimizer import Option, optimize
from .decision.robustness import Thresholds, compare_scenarios, evaluate_thresholds
from .decision.memo import make_memo
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
        return Scenario(**{key: getattr(self, key).domain() for key in type(self).model_fields})


@app.get("/api/health")
def health():
    return {"ok": True, "data_status": "NFHS parse unverified; no observed access-gap estimate"}


@app.get("/api/indicators")
def indicators():
    with (ROOT / "data/processed/pilot_indicators.csv").open(newline="", encoding="utf-8") as stream:
        return {"rows": list(csv.DictReader(stream)),
                "warning": "Third-party NFHS parse; official district factsheet verification pending. Not screening coverage."}


@app.get("/api/case")
def case_view():
    return pilot_case()


@app.post("/api/case/readiness")
def case_readiness(payload: DecisionCase):
    from datetime import date
    return assess(payload, district_ledger(ROOT / "data/processed/pilot_indicators.csv"), as_of=date.today())


@app.get("/api/evidence")
def evidence_room():
    records = district_ledger(ROOT / "data/processed/pilot_indicators.csv")
    return {"records": records, "classification": "OBSERVED_UNVERIFIED",
            "warning": "The ledger is NOT screening coverage; official PDF verification pending."}


@app.get("/api/readiness")
def readiness_view():
    from datetime import date
    return assess(pilot_case(), district_ledger(ROOT / "data/processed/pilot_indicators.csv"), as_of=date.today())


class RunRequest(BaseModel):
    case: DecisionCase
    scenario_id: str = Field(min_length=1)
    scenario_version: str = Field(min_length=1)
    inputs: ScenarioInput
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    simulation_count: int = Field(default=500, ge=100, le=100_000)


@app.post("/api/runs")
def create_run(payload: RunRequest):
    try:
        run = make_run(payload.case, payload.inputs.domain(), scenario_id=payload.scenario_id,
                       scenario_version=payload.scenario_version,
                       draws=payload.simulation_count, seed=payload.seed)
        return RunStore(ROOT / "runs").save(run)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    try:
        return RunStore(ROOT / "runs").get(run_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(404, "Run not found") from exc


@app.get("/api/runs/{run_id}/memo")
def run_memo(run_id: str):
    run = get_run(run_id)
    from datetime import date
    records = district_ledger(ROOT / "data/processed/pilot_indicators.csv")
    readiness = assess(pilot_case(), records, as_of=date.today())
    return make_memo(run, readiness, [record.model_dump(mode="json") for record in records])


@app.get("/api/hypotheses")
def hypotheses_view():
    return {"hypotheses": HEALTH_HYPOTHESES, "status": "RESEARCH_QUESTIONS_NOT_FINDINGS"}


@app.get("/api/research/{preset}")
def research_view(preset: str):
    if preset not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    return {"classification": "HYPOTHETICAL", "items": backlog(PRESETS[preset](), [], effort={}),
            "warning": "Heuristic research queue, not causal effects or formal value-of-information"}


class OptimizationRequest(BaseModel):
    classification: str = "HYPOTHETICAL"
    budget_inr: int = Field(ge=0)
    district_capacity: dict[str, float]
    options: list[dict]


@app.post("/api/optimize")
def optimize_view(payload: OptimizationRequest):
    try:
        options = [Option(**value) for value in payload.options]
        return optimize(options, budget_inr=payload.budget_inr,
                        district_capacity=payload.district_capacity,
                        classification=payload.classification)
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/api/robustness")
def robustness_view(draws: int = Query(300, ge=100, le=10_000), seed: int = 42):
    return compare_scenarios({name: factory() for name, factory in PRESETS.items()},
                             draws=draws, seed=seed)


@app.get("/api/threshold/{preset}")
def threshold_view(preset: str, minimum_screened: float = 250,
                   minimum_probability: float = Query(.7, ge=0, le=1),
                   draws: int = Query(300, ge=100, le=10_000)):
    if preset not in PRESETS:
        raise HTTPException(404, "Unknown preset")
    from .decision.robustness import FIELDS
    import random
    from .model import funnel
    rng = random.Random(42)
    scenario = PRESETS[preset]()
    samples = [funnel(*[rng.triangular(getattr(scenario, f).low, getattr(scenario, f).high,
                                      getattr(scenario, f).mode) for f in FIELDS]) for _ in range(draws)]
    try:
        return evaluate_thresholds(samples, Thresholds(minimum_screened=minimum_screened,
                                                       minimum_probability=minimum_probability))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


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
