"""Reproducible run manifests for hypothetical case analyses.

Runs are immutable local JSON files. A hosted multi-instance service must use durable
shared storage before promising persistence across restarts or replicas.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ..model import Scenario, evaluate
from ..simulation import simulate
from .schema import DecisionCase

RUN_FORMAT_VERSION = "1"


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def make_run(case: DecisionCase, scenario: Scenario, *, scenario_id: str,
             scenario_version: str, draws: int, seed: int, created_at: datetime | None = None) -> dict:
    if not scenario_id or not scenario_version:
        raise ValueError("Scenario ID and version required")
    if not 100 <= draws <= 100_000 or not 0 <= seed <= 2**32 - 1:
        raise ValueError("Simulation count or seed out of bounds")
    # Never upgrade a real case to a policy recommendation by providing synthetic inputs.
    if case.classification != "HYPOTHETICAL":
        raise ValueError("Real case runs require verified domain evidence; use a hypothetical case")
    inputs = {name: vars(getattr(scenario, name)) for name in
              ("eligible", "need_rate", "awareness_rate", "screening_rate",
               "followup_rate", "capacity", "spend_inr")}
    snapshot = {"format_version": RUN_FORMAT_VERSION, "case": case.model_dump(mode="json"),
                "scenario_id": scenario_id, "scenario_version": scenario_version,
                "inputs": inputs, "seed": seed, "simulation_count": draws,
                "data_vintage": "NFHS-5 2019-21 (context only, not simulation input)"}
    digest = hashlib.sha256(canonical(snapshot).encode("utf-8")).hexdigest()
    return {"run_id": f"run-{digest[:24]}", "snapshot_digest": digest,
            "created_at": (created_at or datetime.now(timezone.utc)).isoformat(),
            "classification": "HYPOTHETICAL", "decision_status": "HOLD_FOR_REAL_FUNDING",
            "snapshot": snapshot, "point": evaluate(scenario),
            "bands": simulate(scenario, draws=draws, seed=seed),
            "disclaimer": "Synthetic training inputs; no district screening or cost estimate."}


class RunStore:
    def __init__(self, root: Path):
        self.root = root

    def save(self, run: dict) -> dict:
        self.root.mkdir(parents=True, exist_ok=True)
        run_id = run["run_id"]
        if not run_id.startswith("run-") or any(c not in "0123456789abcdef" for c in run_id[4:]) or len(run_id) != 28:
            raise ValueError("Invalid run ID")
        target = self.root / f"{run_id}.json"
        if target.exists():
            previous = self.get(run_id)
            if previous["snapshot_digest"] != run["snapshot_digest"] or previous["snapshot"] != run["snapshot"]:
                raise ValueError("Run ID collision")
            return previous
        # Exclusive create prevents overwrite; partial files are removed on failed write.
        try:
            with target.open("x", encoding="utf-8") as stream:
                json.dump(run, stream, indent=2, allow_nan=False)
                stream.write("\n")
        except FileExistsError:
            return self.get(run_id)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return run

    def get(self, run_id: str) -> dict:
        if not run_id.startswith("run-") or len(run_id) != 28 or any(c not in "0123456789abcdef" for c in run_id[4:]):
            raise ValueError("Invalid run ID")
        with (self.root / f"{run_id}.json").open(encoding="utf-8") as stream:
            return json.load(stream)
