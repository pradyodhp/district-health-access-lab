# Five-minute workbench acceptance (local only)

Start the FastAPI service and Vite or build `web` for FastAPI to serve. The sequence below uses the synthetic pilot case. Do not use it to claim an actual district screening gap or funding recommendation.

1. Open **Decision workbench > Case & evidence**. Confirm the case is HYPOTHETICAL, real decision HOLD, readiness 0/100, and the 24 NFHS ledger records are OBSERVED_UNVERIFIED. Trace one source and see its vintage, cohort, geography and caveat. Edit a case name or version before a run if demonstrating case creation.
2. In **Model & runs**, run `status-quo`. Record the run ID, seed, snapshot digest, and p10/p50/p90 screened. Change awareness mode within its low/high range. The old run must disappear from the current result view. Run again, compare with the prior run, and retrieve the stored run by ID. A different assumption must change the digest; the comparison must list that input and retain HOLD for real funding.
3. In **Sensitivity & research**, open the heuristic queue and its explicitly untested hypothesis questions. It is not Bayesian value of information or a causal ranking.
4. In **Allocation & robustness**, set an illustrative budget, run the bounded optimizer, inspect constraints and unspent budget, compare paired-draw scenario preferences, view the conditional-awareness split and the bounded what-if reversal, then test a target threshold. All results are HYPOTHETICAL and not empirical success probabilities.
5. In **Memo**, generate the structured memo from the stored run. It must say DECISION ON HOLD, list the missing denominator, screening coverage, validated costs/effects, capacity and model-stability review, and carry the exact run provenance. Download JSON if needed; browser print from the legacy tab is not a programmatic PDF export.

Automated gates: `python3 -m pytest -q`, `cd web && npm test && npm run build`, and the same commands from a fresh clone. CI also rebuilds the extraction and checks its CSV for unintended changes. No live deployment is part of this acceptance.

## Approved gap closure (2026-10-01)

- Frontend: five section views, resource hooks and shared API transport, with
  cross-section invalidation in `useWorkbench`. No nested prop chains.
- Backend: six resource routers mounted under `/api/v1`, plus legacy mounts.
  Typed inputs and deterministic 404/422/429 error envelopes.
- Compute: 10,000 draws, 20,000 grid combinations, 120 expensive starts/minute
  and 2 active computations per process. Admission concurrency is tested.
- Accessibility: Tab/Enter-only primary journey, focus pixels, accessible names,
  pressed-state navigation, skip link, chart text table and reduced motion.
  All five workbench sections have axe scans and responsive screenshots at
  390/768/1366. A real NVDA/VoiceOver spoken-output pass remains NOT DONE.
- Deployment: free-only blueprint checked, no paid resource added, no deployment
  started. Free-tier cold starts and ephemeral run storage are documented.

Still outside completion: hosted deployment/fresh hosted deploy verification,
real assistive-technology audio review, sustained HTTP load testing, static
Python typing, authentication and deployment-grade rate/storage protection.
No real-data validation, empirical intervention effect or cost evidence was
created by this engineering increment. The evidence gate remains HOLD.
