# Architecture

## Data and decision chain

Versioned raw bytes -> checksum manifest -> strict extraction -> processed CSV -> typed evidence ledger -> explicit readiness gates. Hypothetical case -> field-validated assumptions -> pure funnel -> seeded simulation -> sensitivity/paired robustness -> frozen run artifact -> evidence-gated memo.

The Python modular monolith separates the model, extraction, uncertainty, evidence/readiness and decision analysis. `requests.py` owns API input contracts; `observability.py` owns request IDs, error handlers and local request logs. `api.py` only composes the application. Resource routers in `routes/` own evidence, cases, scenarios, runs, analysis and memos, mounted at `/api/v1` and at hidden-from-OpenAPI legacy `/api` routes. There is no path rewrite. `limits.py` owns process-wide compute admission. React separates five workbench section components, API transport, case/evidence/simulation/run/research hooks, and a small `useWorkbench` coordinator for cross-section invalidation. State is passed directly to each section without nested prop chains. No new global state library or distributed service was added.

No database, LLM, external numerical service, queue or microservice is required. RunStore atomically publishes complete local JSON using a temporary file and a no-overwrite hard link. This is single-host persistence, not hosted durability, access control or multiuser tenancy. API compatibility routes remain `/api/*`; `/health` is added. Versioned resource routers are implemented; a general domain-adapter interface remains future work.

The healthcare model does not consume district percentages. No generic non-health domain is falsely implemented. See [model methodology](model-methodology.md), [reproducibility](reproducibility.md) and the baseline [gap analysis](10-10-gap-analysis.md).
