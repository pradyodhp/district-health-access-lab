"""Source lineage and compatibility are explicit; no data promotion by implication."""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .schema import Confidence, Evidence, Status


def district_ledger(csv_path: Path, model_version: str = "0.2.0") -> list[Evidence]:
    with csv_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result = []
    for row in rows:
        result.append(Evidence(
            id=f"nfhs5:{row['state']}:{row['district']}:{row['indicator_id']}",
            variable=row["indicator_id"], value=float(row["value_pct"]), unit="percent",
            status=Status.OBSERVED_UNVERIFIED, source="NFHS community transcription",
            source_url=row["source_url"], retrieved_on=date.fromisoformat(row["retrieved_on"]),
            vintage=row["survey_vintage"], geography=f"{row['state']}/{row['district']}",
            population=f"{row['sex']} adults {row['age_group']}", confidence=Confidence.LOW,
            caveat=row["caveat"], methodology="Third-party transcription; PDF cross-check pending",
            model_version=model_version, geography_level="district", age_range=row["age_group"],
            sex=row["sex"], period_start=date(2019, 1, 1), period_end=date(2021, 12, 31),
            indicator_kind="proxy", source_identifier="nfhs-community-snapshot-2026-09-30",
            source_sha256=row["source_sha256"],
        ))
    return result


def compatible(records: list[Evidence], *, geography: str, population: str, vintage: str) -> bool:
    """Require exact dimensions; crosswalks must be separate DERIVED records."""
    return bool(records) and all(
        r.geography == geography and r.population == population and r.vintage == vintage
        for r in records
    )


def trace(evidence_id: str, ledger: list[Evidence]) -> list[Evidence]:
    by_id = {e.id: e for e in ledger}
    if len(by_id) != len(ledger):
        raise ValueError("Duplicate evidence IDs")
    result, visited, active = [], set(), set()

    def visit(key: str):
        if key in active:
            raise ValueError("Cycle in evidence lineage")
        if key in visited:
            return
        if key not in by_id:
            raise ValueError(f"Missing lineage parent {key}")
        active.add(key)
        for parent in by_id[key].derived_from:
            visit(parent)
        active.remove(key)
        visited.add(key)
        result.append(by_id[key])

    visit(evidence_id)
    return result
