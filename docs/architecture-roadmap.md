# Historical architecture assessment and incremental roadmap

This records the pre-workbench assessment. For current architecture and remaining gaps, see [architecture](architecture.md) and [10/10 gap analysis](10-10-gap-analysis.md).

Assessment date: 2026-09-30. Baseline: `d8ee400` on `main`; 17 tests pass, Vite builds.

## What exists

A modular Python/FastAPI backend (`src/health_access/`) holds a strict NFHS CSV extractor, a pure hypothetical cohort funnel, seeded triangular Monte Carlo, preset scenarios, one-at-a-time and SALib Morris screens. The React/Vite app is a four-view evidence-first work sample. The source snapshot, row-level CSV provenance, limitations, README, tests and GitHub CI are present. The original endpoints remain a useful compatibility surface.

The source's four blood-glucose/blood-pressure percentages per pilot district are an unverified third-party transcription of NFHS-5. They are neither screening coverage nor diagnosed prevalence. NFHS-4 zeros are not valid trends. There is no compatible adult population denominator, verified screening coverage, intervention effect, cost or follow-up series. The current synthetic teaching model cannot responsibly rank districts or allocate actual funding.

## Design gaps

- Hardcoded training presets lack a typed case, separate evidence records, scenario ancestry and an auditable run manifest.
- The domain funnel is coupled to a particular outcome; a shared model interface and domain adapter are needed, but adding speculative domain implementations would obscure the decision workflow.
- Readiness is a prominent visual HOLD label, not an explainable evidence-and-stability rule. The UI's source ledger is not a first-class evidence room.
- No guarded optimization, paired-draw robustness, threshold or research-priority analysis exists. A point estimate alone cannot support a decision.
- The memo is composed in React, not from a versioned run artifact. The UI has preset selection but no case/assumption editing. A manual browser print is the only PDF export.
- CI covers Python and Vite but not frontend behavior; the run cannot yet be retrieved by ID. No deployed demo is verified.

## Boundaries that must stay explicit

1. `evidence` parses and validates observed inputs and source metadata. A source identifier is never permission to treat an unverified value as verified.
2. `cases` defines typed, versioned decision objectives, units and constraints. Synthetic demonstration is an explicit case classification.
3. `model` remains pure; healthcare supplies a domain adapter. No district value is injected into the synthetic funnel by implication.
4. `analysis` computes Monte Carlo, sensitivity, research priority, optimization and paired-draw robustness. All decision outputs carry evidence status and provenance.
5. `api` orchestrates and stores run manifests with immutable snapshots. The UI and memo consume the same artifact. No LLM writes numerical outcomes.

Flat files are enough for this portfolio scope. Do not introduce a database or microservices unless user needs, scale or concurrency demonstrate a reason. Runs can begin as immutable local JSON files with collision-safe names; production multi-instance persistence needs later architecture review. CLI/export workflows must not promise durable hosted storage without it.

## Sequence and release gates

| Phase | Increment | Gate |
| --- | --- | --- |
| A | Typed case/evidence schemas, compatibility checks, lineage and readiness report; map all NFHS rows without upgrading trust. | Every missing dimension yields explicit HOLD; schema and API tests; old API still works. |
| B | Case-driven model inputs and versioned run snapshots, deterministic seeds and scenario ancestry. | Same run ID reproduces same bands; input change changes digest; conservation/property tests. |
| C | Research backlog, linked uncertainty/sensitivity, paired-draw robustness, decision thresholds and a guarded hypothetical allocation optimizer. | Constraints hold; tie handling and reversal tests; real policy result blocked by missing evidence. |
| D | React workbench (case, evidence, model, scenarios, sensitivity, optimize, robustness, memo), editable hypothetical inputs and run retrieval. | Browser interactions and visual review; no example output called a district estimate. |
| E | Structured client memo, lineage drill-down, CI/frontend tests and fresh-clone acceptance test. | Memo says DECISION ON HOLD while blocked. A generated PDF is only claimed after implemented and verified. |

Do not ship a district map with colored screening gaps, empirical cost/person, client recommendation or live deployment until the official factsheets, compatible denominators, screening counts, cost/effect evidence and operational hosting have been sourced and checked. Synthetic optimization is useful for demonstrating mechanics, not allocating real rupees.
