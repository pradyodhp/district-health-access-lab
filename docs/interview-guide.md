# Interview guide

## 30 seconds

This is an evidence-first decision workbench for health screening. It keeps source-backed indicators separate from invented scenario inputs, simulates explicit assumptions, tests sensitivity and robustness, and refuses a funding recommendation when screening/denominator/cost/effect evidence is missing. Every training run has hashes and a replayable snapshot.

## Two minutes

Ordinary dashboards make numbers look comparable before checking population, period and definitions. Here a checksum-validated source pipeline builds an unverified NFHS ledger. Ten readiness gates explain what is missing. A separate fictional cohort demonstrates the mechanics: seeded Monte Carlo, OAT/Morris, paired scenario preference, discrete allocation and a HOLD memo. Trace a source, change an assumption, save a run, inspect hashes and replay. None of those operations converts a glucose percentage into screening coverage.

## Five-minute technical walkthrough

1. Open evidence and read OBSERVED_UNVERIFIED, source period and proxy caveat.
2. Inspect the ten readiness gates and linked research backlog.
3. In Model & runs create a training run. Explain field-specific units and conservation.
4. Show input/output digests, seed/draw count and replay; edit an assumption to invalidate stale output.
5. Show OAT and paired training robustness; explain hypothetical dependence and no causal claim.
6. Run the separate integer-grid optimizer; state fictional yields and optimality scope.
7. Generate the artifact-backed memo. It says DECISION ON HOLD.

## Decisions, tradeoffs and factual answers

Why no AI? Numerical outputs come from explicit deterministic algorithms; a language model is unnecessary here. Why no microservices/database? Current scale and state do not justify them; local JSON's durability limit is explicit. Why no district ranking? Compatible screening evidence and denominators are absent. Why triangular? Transparent training ranges, not fitted data; other distributions are future work. Does convergence validate the model? No, it only stabilizes Monte Carlo summaries under assumptions. Are gates a certification? No, metadata/review gates precede expert decision review. Is it deployed? Not by this upgrade. What remains? Empirical evidence, expert validation, auth/durable storage, generic adapters, fuller UI/E2E/accessibility and Python dependency locking.

Do not say 30 phases are DONE. Read [engineering report](final-engineering-report.md) for the exact DONE/PARTIAL/BLOCKED scorecard.
