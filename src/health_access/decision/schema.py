"""Versioned case and evidence records with explicit safety states."""
from __future__ import annotations

from datetime import date
from enum import Enum
from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Status(str, Enum):
    OBSERVED = "OBSERVED"
    OBSERVED_UNVERIFIED = "OBSERVED_UNVERIFIED"
    DERIVED = "DERIVED"
    ASSUMED = "ASSUMED"
    HYPOTHETICAL = "HYPOTHETICAL"
    INCOMPATIBLE = "INCOMPATIBLE"
    REJECTED = "REJECTED"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(min_length=1)
    variable: str = Field(min_length=1)
    value: float | None
    unit: str = Field(min_length=1)
    status: Status
    source: str = Field(min_length=1)
    source_url: str | None = None
    retrieved_on: date | None = None
    vintage: str = Field(min_length=1)
    geography: str = Field(min_length=1)
    population: str = Field(min_length=1)
    confidence: Confidence
    caveat: str = Field(min_length=1)
    methodology: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    derived_from: tuple[str, ...] = ()
    geography_level: str | None = None
    age_range: str | None = None
    sex: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    numerator: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    denominator: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    indicator_kind: Literal["direct", "proxy", "not_applicable"] = "proxy"
    transformation: str | None = None
    source_identifier: str | None = None
    source_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    reviewed_by: str | None = None


    @model_validator(mode="after")
    def valid_provenance(self):
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValueError("Evidence period is reversed")
        if self.numerator is not None and self.denominator is not None and self.numerator > self.denominator:
            raise ValueError("Numerator exceeds denominator")
        if self.status is Status.DERIVED and not self.transformation:
            raise ValueError("Derived records require an explicit transformation")
        if self.value is not None and not isfinite(self.value):
            raise ValueError("Evidence value must be finite")
        if self.status in {Status.OBSERVED, Status.OBSERVED_UNVERIFIED}:
            if self.value is None or not self.source_url or not self.retrieved_on:
                raise ValueError("Observed records need value, URL and retrieval date")
        if self.status is Status.DERIVED and not self.derived_from:
            raise ValueError("Derived values require parent IDs")
        if self.status in {Status.ASSUMED, Status.HYPOTHETICAL} and self.source_url:
            raise ValueError("Synthetic input cannot imply empirical source support")
        return self


class Constraint(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str = Field(min_length=1)
    rule: str = Field(min_length=1)


class Intervention(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    min_allocation_inr: float = Field(default=0, ge=0)
    max_allocation_inr: float = Field(ge=0)
    capacity_people: float | None = Field(default=None, ge=0)
    dependencies: tuple[str, ...] = ()

    @model_validator(mode="after")
    def valid_bounds(self):
        if self.max_allocation_inr < self.min_allocation_inr:
            raise ValueError("Maximum allocation below minimum")
        return self


class DecisionCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    case_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    name: str = Field(min_length=1)
    objective: Literal["maximize_additional_screened"]
    geography: tuple[str, ...] = Field(min_length=1)
    population: str = Field(min_length=1)
    service: str = Field(min_length=1)
    horizon_months: int = Field(gt=0)
    budget_inr: float = Field(ge=0)
    target_outcome: str = Field(min_length=1)
    interventions: tuple[Intervention, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    classification: Literal["REAL", "HYPOTHETICAL"]
    model_version: str = Field(min_length=1)
    geography_level: str = "district"
    period_start: date | None = None
    period_end: date | None = None

    @model_validator(mode="after")
    def valid_case(self):
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValueError("Case period is reversed")
        ids = [i.id for i in self.interventions]
        if len(ids) != len(set(ids)):
            raise ValueError("Intervention IDs must be unique")
        if any(d not in ids or d == i.id for i in self.interventions for d in i.dependencies):
            raise ValueError("Intervention dependency missing or self-referential")
        dependencies = {i.id: i.dependencies for i in self.interventions}
        def visit(key, active, visited):
            if key in active:
                raise ValueError("Cyclic intervention dependencies")
            if key in visited:
                return
            active.add(key)
            for dependency in dependencies[key]:
                visit(dependency, active, visited)
            active.remove(key)
            visited.add(key)
        visited = set()
        for key in ids:
            visit(key, set(), visited)
        if sum(i.min_allocation_inr for i in self.interventions) > self.budget_inr:
            raise ValueError("Minimum allocations exceed budget")
        return self


REQUIRED_DECISION_VARIABLES = (
    "adult_population", "screening_coverage", "intervention_cost",
    "intervention_effect", "facility_capacity",
)
