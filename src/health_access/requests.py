"""API request contracts, separate from the pure domain engine."""
from pydantic import BaseModel, Field, ConfigDict
from .model import Assumption, Scenario
from .decision.schema import DecisionCase

class StrictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_max_length=2000)

class Range(StrictRequest):
    low: float = Field(ge=0)
    mode: float = Field(ge=0)
    high: float = Field(ge=0)
    unit: str
    rationale: str = Field(min_length=1)

    def domain(self):
        return Assumption(**self.model_dump())


class ScenarioInput(StrictRequest):
    eligible: Range
    need_rate: Range
    awareness_rate: Range
    screening_rate: Range
    followup_rate: Range
    capacity: Range
    spend_inr: Range

    def domain(self):
        return Scenario(**{key: getattr(self, key).domain() for key in type(self).model_fields})


class RunRequest(StrictRequest):
    case: DecisionCase
    scenario_id: str = Field(min_length=1)
    scenario_version: str = Field(min_length=1)
    inputs: ScenarioInput
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    simulation_count: int = Field(default=500, ge=100, le=100_000)


class OptimizationRequest(StrictRequest):
    classification: str = "HYPOTHETICAL"
    budget_inr: int = Field(ge=0)
    district_capacity: dict[str, float]
    options: list[dict]

