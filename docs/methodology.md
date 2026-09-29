# Methodology, current phase

The source is a community-maintained CSV transcribed from district NFHS fact sheets. `scripts/build_data.py` selects six exact state-district pairs and two sex-specific NFHS-5 blood-sugar indicators plus two blood-pressure indicators for context. The original indicator wording is retained. Data are percentages, not population counts. Blood pressure is included as context only; the pilot decision question concerns blood-glucose screening.

For each selected row the script records its value, denominator label (adult women or men, age 15+), observation status, survey vintage, source URL and retrieval date. Empty or zero NFHS-4 cells are not presented as trends because the source's NFHS-4 coverage for these indicators has not been established. Source-reported NFHS-5 zero remains a numeric observation, subject to official verification.

This phase makes **no** causal inference, screening-rate inference, sex-weighted district average, programme-cost estimate or district priority ranking. Phase 2 must first reconcile the proposed funnel's eligible, tested, positive, aware, referred and treated cohorts. Each conditional conversion must use a named denominator and compatible time window. Scenario assumptions should use defensible bounded distributions; sampled outputs must preserve physical constraints. Sensitivity analysis is meaningful only after the input definitions are defensible.

## Synthetic scenario contract (Phase 2 onward)

`eligible` is a hypothetical cohort, not a district population. `need_rate` is a fictional proxy share; `awareness_rate` is conditional on that group; `screening_rate` is conditional on awareness, not population-wide screening coverage. `followup_rate` applies to screened members of that cohort. Capacity caps the screened count. These definitions guarantee each successive count is no larger than its predecessor, but they are **not** measured care pathways. Training presets carry written `rationale` and min/mode/max values, sampled as triangular distributions (seed 42). The API reports 10th, 50th and 90th percentiles. Its one-at-a-time ranking and SALib Morris screen explore structural sensitivity; they do not establish statistical confidence intervals or prove intervention effects.

The text memo states that prioritization is deferred. Printing the memo view to PDF is an explicit browser action; there is not yet a server-side PDF export. A district choropleth has intentionally not been added: without valid district gap estimates, coloring the map would imply false precision. The 4-view interface includes an observed indicator ledger instead.

## Decision foundation (increment A)

The new `/api/case`, `/api/evidence`, `/api/readiness` and `/api/case/readiness` endpoints expose typed case definitions and full source-linked evidence records. The starter case is explicitly HYPOTHETICAL. An evidence record is typed as OBSERVED, OBSERVED_UNVERIFIED, DERIVED, ASSUMED or HYPOTHETICAL. Provenance fields include source, retrieval date, vintage, geography, population, confidence, caveat and model version. The current 24 NFHS rows remain OBSERVED_UNVERIFIED; none are relabeled as screening coverage. The rule-based readiness gate counts only matching verified/recent inputs and still returns HOLD pending independent methodological and stability review. Its 20-point-per-field number is a transparent completeness checklist, **not** a calibrated probability of a sound funding decision. Future increments will add editable cases, run manifests and analyses. Existing scenario endpoints are preserved.

## Reproducible hypothetical runs (increment B)

`POST /api/runs` takes a typed case, scenario ID/version, seven bounded distributions, random seed and draw count. It refuses cases classified REAL until an evidence-bound model is implemented. The canonical SHA256 of the complete input snapshot determines the run ID; repeated identical requests yield the same run and bands. `GET /api/runs/{id}` retrieves the saved artifact with model/case versions, survey-context vintage, seed, count and each assumption rationale. Current storage is local `runs/*.json`, excluded from git. On stateless or multi-replica deployment these files **are not durable**. Use shared storage before claiming hosted run retention. No third-party data is fed into the synthetic model.

## Hypotheses and research priority

`/api/hypotheses` maps demand, access, capacity and retention questions to possible metrics and research actions. These are questions, not findings. `/api/research/{preset}` reports a transparent **heuristic** rank on synthetic scenario inputs: one-at-a-time output swing, relative parameter range, evidence confidence and a stated 1-5 effort estimate. It is not formal Bayesian value of information and does not imply that model sensitivity is a causal effect. Its purpose is to identify which missing inputs may be worth validating next.
