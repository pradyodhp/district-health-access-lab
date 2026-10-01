# 10/10 gap analysis

Audit started 2026-09-30 IST. Baseline: remote `main` commit `d3dbe05181cb4d9bba0afd2482b077c5b55592fb`. This is a pre-change audit, not a certification. No deployment was tested against a hosted service. The separate license choice is not part of this audit.

## Audit scope and executed checks

Inspected all 58 tracked paths: README, INTERVIEW, LIMITATIONS, six existing docs, raw manifest/data dictionary, raw compressed CSV, processed CSV, all Python modules/tests, scripts, React source/styles, package metadata, Vite configuration, CI and Render blueprint. No tracked TODO/FIXME/HACK markers were found; absence of markers does not mean absence of debt. Dependency directories and generated bundles are build outputs, not authored source.

| Check | Baseline result |
| --- | --- |
| Backend suite | 40 passed; Starlette/httpx deprecation warning. Existing environment Python 3.10, distinct from CI Python 3.11. |
| Frontend suite | 3 passed, all pure JavaScript utility tests. No component or E2E tests. |
| Production build | Passed; 541.75 kB JS chunk, 157.18 kB gzip. Vite warns above 500 kB. |
| Raw pipeline | Rebuilt 24 rows with no tracked CSV diff. |
| Raw snapshot | 73,632 CSV rows, 10,804,529 uncompressed bytes; SHA256 `750be317111bdd313d05d49ee48b6414b76def1018dc893dcea813334cefa0c8`, matching human manifest. |
| Processed data | 6 districts, 2 states, 4 indicators each; all OBSERVED_UNVERIFIED, values 7.3-25.8 percent. No empirical screening count. |
| Live local backend | Uvicorn started; all 21 declared application route patterns exercised using real HTTP, plus OpenAPI and built frontend `/`. Valid requests returned 200. |
| Invalid-input probes | Preset draws=1 returned 500 (uncaught ValueError); negative robustness seed returned 200; negative threshold returned 422; invalid run ID returned 404. |
| Dependency audit | npm reports esbuild moderate and Vite high development-server vulnerabilities; no claim that the static production bundle is directly exploitable from these advisories. Python dependency audit still needed. |

The HTTP run covered health, indicators, case, case readiness, evidence, lineage, readiness, run create/get/compare/memo, hypotheses, research, optimize, robustness, reversal, threshold, presets, preset/custom scenario and scenario comparison. It is a smoke test, not exhaustive endpoint security testing.

## Current architecture

A small modular monolith: FastAPI orchestration in `src/health_access/api.py`; a pure dataclass cohort model; extraction, scenarios, triangular simulation and OAT/Morris modules; decision modules for schemas, evidence, cases, readiness, research, optimization, robustness, reversal, runs, comparison and memo. React/Vite serves five top-level views including a workbench. Static assets are optionally mounted at `/`. The only persistence is local JSON files excluded from Git. No database, external model service, LLM output or microservice is needed for the demonstrated requirements.

## Current functionality

Strict pilot extraction; a 24-record source-linked evidence ledger; exact-dimension compatibility helper and cycle-aware lineage traversal; typed hypothetical case editing; immutable-content-addressed input snapshots; seeded training simulation; OAT and SALib Morris; heuristic research queue; bounded integer-grid allocation with dependencies/shared capacity; paired-quantile preference share; threshold and one-input reversal scans; stored-run comparison; server-produced structured HOLD memo. The legacy frontend text memo also remains.

## Existing strengths: what already clears the bar

- NFHS elevation/medicine indicators are not silently promoted to screening coverage, diagnosis or counts. Official verification remains pending.
- Synthetic parameters are separate from district data; real runs/allocations are rejected.
- Pure funnel conserves the cohort and caps screened people by capacity. Known-answer, monotonicity and reproducibility tests exist.
- OAT, Morris, paired robustness and heuristic research priority have honest interpretation caveats. Percentiles are not called empirical confidence intervals.
- Optimizer checks budget, grid size, option limits, dependencies and district caps; it refuses real funding classification.
- Source bytes are versioned, extraction is reproducible and CI detects changed processed output.
- Run IDs are deterministic; file lookup restricts IDs rather than accepting arbitrary paths.
- No district ranking, decorative gap map, fabricated impact, clinical advice or verified deployment claim was found in the current product.

These strengths satisfy specific checks, not entire future phases.

## Missing functionality and technical debt

| ID | Finding and location | Priority | Definition of done |
| --- | --- | --- | --- |
| E1 | Evidence schema lacks geography level, age/sex fields, period endpoints, numerator/denominator, transformation and rejection/incompatibility states (`decision/schema.py`). | P0 | Typed optional metadata, explicit rejected states, fail-closed compatibility and lineage tests. Legacy records remain unverified. |
| E2 | Readiness freshness uses retrieval age, not survey period. Derived records can count without checking verified parents; independent review is a permanent string blocker (`readiness.py`). | P0 | Ten explicit machine-readable gates with PASS/FAIL/HOLD/NOT_APPLICABLE, reasons, IDs, missing evidence, severity and research action. A current download cannot refresh old evidence. |
| E3 | Raw SHA is calculated but not enforced against a machine-readable manifest (`extract.py`, SOURCES). Codes/vintage drift not verified. | P0 | Versioned manifest, raw checksum enforcement, explicit metadata validation and reproducibility test. No silent source repair. |
| R1 | Run hash covers inputs but omits engine implementation/environment version, evidence snapshot, readiness, output hash and sensitivity/robustness/allocation snapshot (`runs.py`). | P0 | Manifest v2 snapshots context and computed analysis, hashes inputs/outputs, records versions/environment, verifies load, and exposes deterministic replay. Legacy behavior clearly identified. |
| R2 | Memo endpoint re-reads today's pilot evidence/readiness; same stored run could receive changed context. Memo analysis fields are narrative placeholders (`api.py`, memo). | P0 | Memo consumes frozen run context and actual run analyses. No fabricated recommendation; context changes cannot alter an old memo. |
| M1 | Scenario fields accept any allowed unit: eligible can be a rate; rate fields can be people. Case population/unit semantics are strings (`model.py`). | P0 | Field-specific unit validation and negative API tests; wrong units rejected before evaluation. |
| M2 | Funnel starts at eligible cohort, not population/eligibility/treatment. It is not a validated screening pathway. | P1 | Document current equations/limitations; adapter interface before extending stages. Add stages only with explicit semantics and conservation tests. |
| M3 | Run comparison allows same case ID with incompatible population/geography/period/model; percentile methods differ between simulation and robustness. | P1 | Explicit compatibility guard; shared percentile convention; paired comparisons distinguish sampling/config changes. |
| A1 | Only triangular independent input distributions; no convergence study or explicit uncertainty taxonomy. | P1 | Distribution metadata, sample/seed validation, convergence report at 1k/5k/10k/25k; no unwarranted CI language. |
| A2 | OAT has no normalized importance; research questions lack owner/status/gate/source candidates. | P1 | Structured missing-evidence backlog linked to gate IDs; preserve heuristic label and actual ranges. |
| A3 | Optimizer accepts cyclic dependencies; integer only; shared caps saturate outcome rather than forbid excessive attempted reach. | P1 | Document capacity semantics and discrete optimality; detect dependency cycles; fraction rules only when explicitly implemented/tested. |
| B1 | API orchestration is one module with inline request schemas; `Read-only demo API` docstring is stale. | P1 | Split request/analysis/service boundaries without breaking compatibility; correct description. |
| B2 | No error envelope/request ID/structured lifecycle logs/API version aliases. | P1 | Deterministic 4xx validation, request IDs, safe errors and JSON logs; compatibility routes retained. |
| F1 | Workbench uses many state variables and dense JSX; frontend fetch wrapper is local and only partly cancellable. | P1 | Focused components/shared client/hooks with tests; editing cannot display stale dependent results. |
| F2 | Research/robustness/reversal use presets even after custom edits. Case budget and optimizer budget are independent. | P0 UX truth | State that preset analysis is separate, or use current run inputs; clear stale results on edits. |
| F3 | Threshold target edit leaves old result visible; failed/empty API data can appear as zero via fallback formatting (`main.jsx`). | P1 | Invalidate target results; render unavailable/loading instead of invented zero; test errors/empty states. |
| F4 | Legacy memo is independent frontend prose, unlike run memo; Overview mixes OBSERVED wording and hardcoded counts. | P1 | Explain legacy draft or route to artifact-backed memo; exact OBSERVED_UNVERIFIED labels, derive counts from loaded data. |
| T1 | Three frontend tests never render UI; no primary-journey E2E, accessibility or error-state tests. | P1 | Component tests and automated journey from evidence through run/memo, API failure and stale-state tests. |
| T2 | Missing adversarial units, dates, lineage status, hash tampering, invalid draws, concurrency and infeasible/cyclic cases. | P0 | Regression tests for each discovered defect; coverage report, not just test count. |
| S1 | Preset simulation accepts up to 1m draws and invalid input may become 500; API lacks body/string limits, auth and rate limiting. | P0 | Consistent computation bounds; safe request limits; document demo threat model. Never claim public production multiuser security. |
| S2 | npm has two advisory-bearing packages; no lockfile committed, Python uses broad version ranges. | P1 | Tested upgrades, committed dependency locks, repeatable installation, Python/npm audit in CI. |
| S3 | Run writer uses exclusive open but readers can see partial files; content not validated on read; local disk can grow without retention. | P1 | Atomic immutable publication, schema/hash validation, documented storage/retention limitations. |
| O1 | No request/run logs, timing or memory benchmarks. | P1 | Lightweight structured events; reproducible benchmark script/report, no external monitoring platform. |
| D1 | Render blueprint has no health path/runtime pin/storage policy; deploy not executed; no `/health` version info. | P1 | Tested local deployment commands and health endpoint, runtime/env docs, fresh-clone acceptance. Hosted release remains separate authorization and validation. |
| C1 | CI tests/pipeline/build only; no lint/type/coverage/security/API smoke; npm install rather than npm ci. | P1 | CI runs locked installs, lint, tests, pipeline hash check, frontend/build, audit and HTTP smoke. |
| DOC1 | README roadmap says already-built features are future; architecture roadmap is historical baseline; dictionary allows UNAVAILABLE but extract emits only complete rows. | P1 | Mark history clearly and update current commands/claims. Create requested methodology/readiness/reproducibility/deployment/testing/limitations/backlog/interview documents. |
| DEMO1 | No one-command artifact-generating demo. | P1 | Deterministic training demo command outputs manifest/analysis/memo with HYPOTHETICAL labels. |

## Data/evidence gaps

Official factsheet row checks, compatible distinct-person screening counts, matching adult denominators, intervention effects, programme costs and operational capacity remain unavailable in this repository. Survey 2019-21 is not current evidence simply because the file was retrieved in 2026. No code upgrade can supply missing empirical evidence. Do not merge male/female percentages, infer NFHS-4 trends from placeholder zeros, or infer causality from cross-sectional indicators. Real-world policy readiness is BLOCKED until evidence and independent methodological/stability review exist.

## Modeling gaps

Current model: need = eligible × need_rate; aware = need × awareness_rate; screened = min(aware × screening_rate, capacity); followed_up = screened × followup_rate. Spend is an input, not a cost function. There is no treatment linkage stage or causal intervention estimator. Independent triangular distributions are training choices, not fitted posteriors; paired comparisons share quantiles as a modeled dependence assumption. Optimization maximizes hypothetical reach under a discrete grid, not real cost-effectiveness. These limitations need formal equations and examples, not a new algorithm presented as evidence.

## Testing, UX and accessibility gaps

Backend tests give a useful foundation but do not cover all rejection paths or artifact corruption. Frontend tests cover only utility functions. Explicit focus styling, chart text alternatives, select labels, loading states, responsive evidence tables and keyboard/screen-reader tests need work. There is no measured contrast audit. A build is not visual acceptance. Actual browser journey and screenshots must follow UI changes.

## Production-readiness, security and observability gaps

This is a local portfolio workbench, not a production health service. No sensitive patient data is present. Public unauthenticated compute/run creation needs deployment-specific protection, resource controls and a storage policy. Local run files are not durable on Render free/stateless replicas. Dependency advisories found by npm: https://github.com/advisories/GHSA-67mh-4wv8-2f99, https://github.com/advisories/GHSA-4w7w-66w2-5vf9, https://github.com/advisories/GHSA-v6wh-96g9-6wx3, https://github.com/advisories/GHSA-fx2h-pf6j-xcff. Advisory applicability differs by dev server/platform; audit findings are not proof of compromise. Structured request/run timing logs and repeatable load measurements are absent.

## Documentation gaps

The requested professional doc suite is not yet present. Existing methodology is useful but mixes historical increments and current behavior; architecture roadmap was written before later modules. README's short test command omits runtime requirements needed by tests. Documentation must distinguish prototype mechanics, empirical blockers and hosted deployment state. No license should be selected as part of this engineering upgrade.

## Exact implementation plan and phase mapping

After this audit, follow the requested priority order, not superficial feature count:

1. **Evidence correctness (phases 2-4, 28):** E1/E3, typed metadata/lifecycle, manifest verification, no status promotion. Gate: schema/drift/lineage rejection tests and identical 24-row extract.
2. **Readiness (10-11):** E2/A2, explicit ten-gate results and linked research actions. Gate: stale/incompatible/proxy inputs cannot pass; real decision remains HOLD.
3. **Artifacts/memo/versioning (12-14):** R1/R2/S3, frozen evidence/readiness/analysis, integrity/replay. Gate: identical inputs reproduce outputs; tampered artifacts rejected; old memo independent of current ledger.
4. **Model/uncertainty/analysis (5-9):** M1-M3/A1/A3, strict units/constraints, documented mathematics, convergence/sensitivity/robustness and optimizer semantics. Gate: conservation, monotonicity, zero/finite/rate/cycle/compatibility tests.
5. **Backend/security/observability (1,19-22,29):** B1/B2/S1/S2/O1. Gate: all compatibility endpoints smoke-tested; bounded invalid input yields 4xx; deterministic logs/errors; dependency checks.
6. **Frontend/tests/accessibility (15-18):** F1-F4/T1, component/service boundaries, truth labels, stale-state handling and keyboard journey. Gate: component/E2E tests, build and inspected desktop/mobile pixels.
7. **Deployment/CI/docs/demo/interview (23-27):** D1/C1/DOC1/DEMO1. Gate: fresh-clone command verification, complete doc links, demo replay. Hosted deployment is not assumed authorized by a request to make configuration reproducible.
8. **Final acceptance (30):** report DONE/PARTIAL/BLOCKED separately for architecture, evidence system, modeling, uncertainty, sensitivity, robustness, optimization, frontend, testing, security, deployment and documentation. Any unmet gate remains explicit; empirical evidence cannot be marked DONE by synthetic tests.

Every row's definition of done above is an acceptance condition. Implementation status belongs in the final engineering report, not retroactively in this baseline audit. Do not claim every possible weakness was proven absent: this is a bounded source/test audit, not an independent clinical, statistical or penetration-test review.


## 2026-10-01 follow-up: approved engineering gaps

The gap descriptions above are the Phase 0 baseline, not current defects. The
follow-up implements resource routers (no rewrite alias), typed bounded compute
requests and process-wide admission; five workbench views and case/evidence/
simulation/decision-run/research hooks; keyboard journey, focus/accessible-name/
reduced-motion and responsive checks. See acceptance-checklist.md for the exact
implemented scope and remaining limits. Real assistive-technology audio review
and hosted deployment are not claimed. Free-only deployment is prepared, not
started. All healthcare evidence/model limits remain unchanged.
