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

## Hypothetical allocation and robustness (increment C)

The bounded grid optimizer searches integer allocation steps subject to total budget, per-option limits, dependencies, intervention capacities and shared district caps. Its yield-per-rupee values are explicitly supplied as hypothetical assumptions; it rejects REAL classification. It does not optimize actual rupees or estimate intervention efficacy. The paired-draw robustness comparison applies the same uniform quantile to each scenario's corresponding input distribution (triangular inverse CDF), separates ties evenly and reports preference share and p10/p50/p90 under invented ranges. Threshold results have an explicit borderline band and return CANNOT_ASSESS for real evidence-gated decisions. Neither preference share nor threshold probability is real-world confidence. These methods are a training workbench while evidence gates remain open.

## Workbench and memo (increment D/E)

The existing four-view demo remains unchanged. Its added Decision workbench loads the case and evidence ledger, allows editing invented ranges, creates and retrieves an immutable local run, and exposes the research queue, bounded optimizer, paired robustness and threshold test. A structured JSON memo is generated from the stored run ID and case readiness, with evidence blockers and provenance attached. The memo remains on HOLD. The original front-end text memo and browser print remain legacy demonstrations, not a verified programmatic PDF export.

Limits: there is no evidence-backed cost/effect input, no real district allocation or empirical probability, no hosted durable run store, and no production deployment. The optimizer example contains conspicuously invented yields and capacities. To use this as a live consulting workflow, verify official factsheets, compatible screening numerators and denominators, intervention costs, effects and capacity, then review model stability independently. The new workbench is not a claim that those gates are complete.

## Run comparison

`GET /api/runs/{left_run_id}/compare/{right_run_id}` compares two stored runs from the same case. It lists changed input snapshots and the change in modeled median screened. The real-funding decision remains HOLD regardless of an illustrative improvement. Neither the model delta nor a changed version is evidence of causal impact. The workbench offers comparison after a second run; its prior-run state lasts only in that browser session.

## Evidence lineage drill-down

Each indicator ledger row has a source-trace action backed by `GET /api/evidence/{evidence_id}/lineage`. The endpoint walks explicit `derived_from` parent IDs and rejects missing parents or cycles; current 24 rows have no derived parents and remain `OBSERVED_UNVERIFIED`. The third-party transcription and its URL are traceable, but the ledger does not become a screening-coverage source through this action.
