# District Health Access Lab

**Decision question:** Given a fixed, yet-to-be-specified NCD screening budget, which of six pilot districts should a health mission investigate first, and which intervention could close the most *verified* screening gap per rupee?

A portfolio work sample in health-access analysis, built as a decision tool rather than a dashboard. **This is a data foundation, not a working screening-gap estimate.** The available NFHS-5 measure is elevated blood glucose or use of glucose-control medicine in adults 15+, *not* diabetes diagnosis, unmet need, screening coverage, or a count of people. The lab will not infer those outcomes from this indicator alone.

## Pilot districts

Maharashtra: Mumbai, Pune, Gadchiroli. Odisha: Khordha, Koraput, Malkangiri. These give a useful range of urban and less urban settings across two states, but urbanicity itself is **not** a quantified input here. See [problem brief](docs/problem-brief.md).

## Current deliverables

- Immutable compressed snapshot of the third-party NFHS district CSV and a reproducible extraction into four sex-specific indicators for six pilot districts.
- Row-level provenance with source URL, survey vintage, extraction date, value status and quality caveat.
- Strict validation and tests: no silent conversion of absent NFHS-4 values to zero, no duplicate keys, percentage bounds, complete pilot coverage.
- [Data dictionary](data/data_dictionary.md), [methodology](docs/methodology.md), [limitations](LIMITATIONS.md) and [full blueprint](docs/blueprint.md).

## Run locally

```bash
python3 scripts/build_data.py
python3 -m pip install -r requirements.txt -r requirements-dev.txt
python3 -m pytest -q
```

Requires Python 3.10+. The extraction itself has no third-party dependencies. A future pipeline will add the **official district fact-sheet cross-check**, a valid district population denominator and a real screening-coverage source before any district ranking, cost-per-person estimate, or funnel is presented as evidence. The raw CSV is an independently maintained parse of [NFHS-5/4 district fact sheets](https://github.com/SaiSiddhardhaKalla/NFHS), not an official release. See [source manifest](data/raw/SOURCES.md).

## Current decision workbench and next evidence

The synthetic engine, FastAPI, React workbench, sensitivity, paired robustness, discrete allocation, run manifests and artifact-backed memo are implemented. They remain a training work sample. The remaining empirical task is official factsheet verification, compatible screening counts/denominators and cost/effect/capacity evidence, followed by independent methodological review.

No individual health records, clinical advice, or operational funding recommendation are included.

## Run the interactive work sample

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt httpx
python3 scripts/build_data.py
uvicorn health_access.api:app --app-dir src --reload
# In another terminal:
cd web && npm install && npm run dev
```

Open the local Vite URL displayed by npm. Build `web` with `npm run build` to let FastAPI serve the bundled interface at `/`. Scenario labels say **HYPOTHETICAL** throughout. The district evidence ledger uses parsed NFHS percentages; it does not combine them with fabricated screening counts. The scenario lab uses a deliberately fictional cohort, Monte Carlo bands and SALib Morris screening. The decision memo can be downloaded as text or printed to PDF using the browser. Read [methodology](docs/methodology.md), [limitations](LIMITATIONS.md) and the [interview kit](INTERVIEW.md) before presenting this as a work sample.

**Not yet shipped as a policy tool:** official district PDF verification, screening coverage, compatible population denominators, cost model evidence, valid district ranking, map, one-click server-generated PDF and live deployment. Those are evidence/hosting gates, not quietly completed features.

### Decision workbench (local)

The additional **Decision workbench** tab runs an evidence-gated training flow: case/evidence review, editable hypothetical assumptions, versioned local runs, heuristic research queue, training allocation and paired robustness, and a structured memo from the run. The memo remains **DECISION ON HOLD** for real funding. Backend endpoints are documented in the FastAPI OpenAPI page at `/docs`; no deployment or durable hosted run storage is claimed. Run the existing API and Vite dev server as described above. The original four tabs and API routes remain.

### Verification

`python3 -m pytest -q` covers source extraction, domain validation, conservation, reproducibility, optimizer constraints and API contracts. `cd web && npm test && npm run build` checks the UI safety projections and builds the application; CI runs both. The default six-district case remains hypothetical because observed inputs are an unverified transcription and the required screening, denominator, cost, effect and capacity evidence is missing. Model preference percentages are conditional on training distributions, not real-world confidence.

See the [five-minute acceptance checklist](docs/acceptance-checklist.md) for the synthetic case walkthrough, expected evidence HOLD and test gates.

## Audit and interview documentation

- [10/10 baseline gap analysis](docs/10-10-gap-analysis.md)
- [Architecture](docs/architecture.md) and [model equations](docs/model-methodology.md)
- [Evidence methodology](docs/evidence-methodology.md), [readiness gates](docs/decision-readiness.md), [research backlog](docs/research-backlog.md)
- [Run integrity/replay](docs/reproducibility.md), [testing](docs/testing.md), [deployment configuration](docs/deployment.md)
- [Limitations](docs/limitations.md), [performance](docs/performance.md), [interview guide](docs/interview-guide.md)

One-command training artifacts: `python3 scripts/demo.py --output /tmp/training-demo`. All demo results are HYPOTHETICAL. `/health` reports service/engine/run format and local-storage limits. The v2 run stores frozen evidence, readiness and analyses with input/output hashes; its memo does not re-read today's ledger. Format-1 local runs require explicit migration. No deployment was made by this upgrade.
