"""API request contracts, separate from the pure domain engine."""
from pydantic import BaseModel, Field, ConfigDict
from .limits import MAX_DRAWS, MAX_GRID
from pydantic import model_validator
from typing import Literal
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
    simulation_count: int = Field(default=500, ge=100, le=MAX_DRAWS)


class AllocationOption(StrictRequest):
    id: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    min_inr: int = Field(ge=0, le=10**12)
    max_inr: int = Field(ge=0, le=10**12)
    step_inr: int = Field(gt=0, le=10**12)
    assumed_people_per_inr: float = Field(ge=0)
    max_people: float = Field(ge=0)
    depends_on: list[str] = Field(default_factory=list, max_length=8)


class OptimizationRequest(StrictRequest):
    classification: Literal["HYPOTHETICAL"] = "HYPOTHETICAL"
    budget_inr: int = Field(ge=0, le=10**12)
    district_capacity: dict[str, float] = Field(min_length=1, max_length=50)
    options: list[AllocationOption] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def bounded_grid(self):
        count = 1
        for option in self.options:
            if option.max_inr < option.min_inr:
                raise ValueError("Invalid allocation limits")
            count *= (option.max_inr - option.min_inr) // option.step_inr + 1
            if count > MAX_GRID:
                raise ValueError("Allocation grid exceeds API compute limit")
        if any(value < 0 for value in self.district_capacity.values()):
            raise ValueError("Invalid district capacity")
        return self
