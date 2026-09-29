"""Diff two stored hypothetical run manifests without claiming empirical improvement."""
from __future__ import annotations


def compare_runs(left: dict, right: dict) -> dict:
    if left.get("classification") != "HYPOTHETICAL" or right.get("classification") != "HYPOTHETICAL":
        raise ValueError("Only hypothetical runs may be compared")
    a, b = left["snapshot"], right["snapshot"]
    if a["case"]["case_id"] != b["case"]["case_id"]:
        raise ValueError("Runs from different cases are not directly comparable")
    changes = []
    if set(a["inputs"]) != set(b["inputs"]):
        raise ValueError("Input schema mismatch")
    for variable, old in a["inputs"].items():
        new = b["inputs"].get(variable)
        if new is None:
            raise ValueError("Input schema mismatch")
        if old != new:
            changes.append({"variable": variable, "before": old, "after": new})
    for key in ("case", "scenario_id", "scenario_version", "simulation_count", "seed"):
        if a[key] != b[key]:
            changes.append({"variable": key, "before": a[key], "after": b[key]})
    left_band, right_band = left["bands"]["screened"], right["bands"]["screened"]
    return {"classification": "HYPOTHETICAL", "left_run_id": left["run_id"],
            "right_run_id": right["run_id"], "changed_inputs": changes,
            "screened_p50_delta": right_band["p50"] - left_band["p50"],
            "left_screened_band": left_band, "right_screened_band": right_band,
            "decision_changed": False, "decision_status": "HOLD_FOR_REAL_FUNDING",
            "warning": "Illustrative synthetic run comparison, not causal effect or policy improvement"}
