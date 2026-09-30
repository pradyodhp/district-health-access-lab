# Architecture

## Data and decision chain

Versioned raw bytes -> checksum manifest -> strict extraction -> processed CSV -> typed evidence ledger -> explicit readiness gates. Hypothetical case -> field-validated assumptions -> pure funnel -> seeded simulation -> sensitivity/paired robustness -> frozen run artifact -> evidence-gated memo.

The Python modular monolith separates the model, extraction, uncertainty, evidence/readiness and decision analysis. `requests.py` owns API input contracts; `observability.py` owns request IDs, error handlers and local request logs. `api.py` still owns routes and orchestration. React uses an API client and two extracted presentation components; the Workbench state/orchestration remains large. These are partial boundaries, not a completed router/hook refactor.

No database, LLM, external numerical service, queue or microservice is required. RunStore atomically publishes complete local JSON using a temporary file and a no-overwrite hard link. This is single-host persistence, not hosted durability, access control or multiuser tenancy. API compatibility routes remain `/api/*`; `/health` is added. API-versioned routers and a general domain-adapter interface are still future work.

The healthcare model does not consume district percentages. No generic non-health domain is falsely implemented. See [model methodology](model-methodology.md), [reproducibility](reproducibility.md) and the baseline [gap analysis](10-10-gap-analysis.md).
