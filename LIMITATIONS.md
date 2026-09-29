# Limitations and next evidence gates

- The bundled dataset is a third-party parse, not the official IIPS release. Each pilot value requires district PDF cross-check before being used as a decision input.
- NFHS-5 blood sugar elevated or on medication is **not** a diagnosis, unmet screening need, testing frequency or treatment gap. A respondent taking medicine may have a controlled measurement.
- NFHS-4 zeros in this file may mean unavailable data. No NFHS-4 trend is emitted.
- Survey district boundaries and 2011 Census codes may differ from current boundaries; administrative changes and denominator vintages must be reconciled.
- District survey estimates have sampling and non-sampling error; this source file does not supply confidence intervals or sample sizes.
- HMIS counts, if added, may count encounters rather than distinct people and may not include private-sector screening. Cross-source comparisons need matching age, sex, period and geography.
- Six selected districts are illustrative, not representative. No budget, facility capacity, cost or intervention effect is verified yet.
- This repository makes no clinical or funding recommendation in its current phase.
- The browser's "Print / save as PDF" action is a manual export, not a generated PDF service. No public demo URL or deployed service has been verified yet.
- The synthetic scenarios use made-up teaching parameters. Their percentile bands quantify uncertainty *under those assumptions*, not survey uncertainty or predictive accuracy for a real district.
- The scenario's follow-up stage is an illustrative nested cohort construction. Real care pathways have repeated screenings and treated patients from earlier periods; those cannot be reduced to this funnel without linked evidence.
