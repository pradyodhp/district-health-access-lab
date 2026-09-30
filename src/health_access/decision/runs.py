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
from .schema import DecisionCase, Evidence
from .readiness import assess
from ..sensitivity import one_at_a_time
from .research import backlog
from .backlog import from_gates
from .robustness import compare_scenarios
from .reversal import reversal_scan
from ..scenarios import PRESETS
from ..model import Assumption
import os
import platform
import tempfile
import logging

RUN_FORMAT_VERSION = "2"
ENGINE_VERSION = "1.0.0"


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def make_run(case: DecisionCase, scenario: Scenario, *, scenario_id: str,
             scenario_version: str, draws: int, seed: int, created_at: datetime | None = None,
             evidence: list[Evidence] | None = None, as_of=None,
             git_commit: str | None = None) -> dict:
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
    from datetime import date
    evidence = evidence or []
    readiness = assess(case, evidence, as_of=as_of or date.today())
    evidence_json = [e.model_dump(mode="json") for e in evidence]
    snapshot = {"engine_version": ENGINE_VERSION, "evidence_snapshot": evidence_json,
                "evidence_digest": hashlib.sha256(canonical(evidence_json).encode()).hexdigest(),
                "readiness": readiness, "distribution": "independent triangular low/mode/high",
                "environment": {"python": platform.python_version()},
                "git_commit": git_commit or os.environ.get("APP_GIT_COMMIT", "unknown"),
                "format_version": RUN_FORMAT_VERSION, "case": case.model_dump(mode="json"),
                "scenario_id": scenario_id, "scenario_version": scenario_version,
                "inputs": inputs, "seed": seed, "simulation_count": draws,
                "data_vintage": "NFHS-5 2019-21 (context only, not simulation input)"}
    digest = hashlib.sha256(canonical(snapshot).encode("utf-8")).hexdigest()
    logger = logging.getLogger("health_access")
    logger.info(canonical({"event": "run_started", "case_id": case.case_id,
                           "case_version": case.version, "model_version": case.model_version,
                           "engine_version": ENGINE_VERSION, "seed": seed, "draws": draws}))
    point = evaluate(scenario)
    bands = simulate(scenario, draws=draws, seed=seed)
    analyses = {"sensitivity": one_at_a_time(scenario),
                "research": backlog(scenario, evidence, effort={}), "evidence_research": from_gates(readiness),
                "robustness": compare_scenarios({"current-run": scenario, "training-baseline": PRESETS["status-quo"]()},
                                                draws=min(draws, 10000), seed=seed),
                "reversal": reversal_scan(scenario, PRESETS["status-quo"](), field="awareness_rate"),
                "allocation": {"status": "NOT_RUN", "reason": "No optimizer configuration was supplied with this run"}}
    outputs = {"point": point, "bands": bands, "analyses": analyses}
    logger.info(canonical({"event": "run_completed", "run_id": "run-" + digest[:24],
                           "seed": seed, "draws": draws, "engine_version": ENGINE_VERSION}))
    return {"output_digest": hashlib.sha256(canonical(outputs).encode()).hexdigest(),
            "run_id": f"run-{digest[:24]}", "snapshot_digest": digest,
            "created_at": (created_at or datetime.now(timezone.utc)).isoformat(),
            "classification": "HYPOTHETICAL", "decision_status": "HOLD_FOR_REAL_FUNDING",
            "snapshot": snapshot, "point": point, "bands": bands, "analyses": analyses,
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
        validate_run(run)
        # Write complete bytes to a private temporary file, then atomically publish
        # with a no-overwrite hard link. Readers never observe a partial JSON file.
        fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(run, stream, indent=2, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                return self.get(run_id)
        finally:
            Path(temporary).unlink(missing_ok=True)
        return run

    def get(self, run_id: str) -> dict:
        if not run_id.startswith("run-") or len(run_id) != 28 or any(c not in "0123456789abcdef" for c in run_id[4:]):
            raise ValueError("Invalid run ID")
        with (self.root / f"{run_id}.json").open(encoding="utf-8") as stream:
            run = json.load(stream)
        validate_run(run)
        return run


def validate_run(run: dict) -> None:
    snapshot = run["snapshot"]
    digest = hashlib.sha256(canonical(snapshot).encode()).hexdigest()
    if run["snapshot_digest"] != digest or run["run_id"] != "run-" + digest[:24]:
        raise ValueError("Run input integrity check failed")
    if snapshot.get("format_version") != RUN_FORMAT_VERSION:
        raise ValueError("Legacy run format requires explicit migration; not verified as v2")
    evidence = snapshot["evidence_snapshot"]
    if snapshot["evidence_digest"] != hashlib.sha256(canonical(evidence).encode()).hexdigest():
        raise ValueError("Evidence integrity check failed")
    outputs = {key: run[key] for key in ("point", "bands", "analyses")}
    if run["output_digest"] != hashlib.sha256(canonical(outputs).encode()).hexdigest():
        raise ValueError("Run output integrity check failed")


def replay(run: dict) -> dict:
    validate_run(run)
    if run["snapshot"]["engine_version"] != ENGINE_VERSION:
        raise ValueError("Engine version mismatch")
    snapshot = run["snapshot"]
    scenario = Scenario(**{key: Assumption(**value) for key, value in snapshot["inputs"].items()})
    result = {"point": evaluate(scenario),
              "bands": simulate(scenario, draws=snapshot["simulation_count"], seed=snapshot["seed"])}
    if result["point"] != run["point"] or result["bands"] != run["bands"]:
        raise ValueError("Replay mismatch; environment or implementation differs")
    return {"status": "REPRODUCED", "run_id": run["run_id"], "outputs": result,
            "scope": "Point and Monte Carlo bands; stored analysis hashes separately verified"}
