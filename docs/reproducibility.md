# Reproducibility

Run format 2 snapshots case/model/scenario versions, seven typed assumptions/rationales, seed/draws, evidence records/hash, readiness, engine version, Python version and Git version (APP_GIT_COMMIT, otherwise explicitly unknown). It stores point outputs, percentile bands, OAT, heuristic research, current-run versus training-baseline paired robustness and one-input reversal. Allocation is NOT_RUN unless separately executed; the app's separate optimizer is not silently added to the run.

Canonical JSON (sorted keys, no NaN) determines the input SHA256 and run ID. Output SHA256 covers point/bands/analyses. Loading validates input/evidence/output hashes; publication is atomic. `GET /api/runs/{id}/replay` reconstructs assumptions and verifies exact point/Monte Carlo bands. Analysis hashes are verified, but analysis replay is not yet independently recomputed by that endpoint. Engine changes must increment ENGINE_VERSION. Dependency-lock provenance is not yet complete for Python.

Memos consume frozen artifact evidence/readiness/analysis; a new ledger cannot silently change an old memo. Same inputs yield same run ID and the first saved timestamp. Format-1 artifacts fail closed with an explicit migration error. No migration silently upgrades them.

```bash
python3 scripts/demo.py --output /tmp/training-demo
```

The command emits a HYPOTHETICAL run, memo and replay result. Local JSON can be deleted on redeploy; hashes detect changes but are not signatures or a tamper-proof audit service.
