# Problem brief | pilot scope

## Client-style question

A state health mission has a fixed NCD screening budget, amount not yet specified. Which of six pilot districts should it investigate and prioritize for **adult blood-glucose screening**, and which outreach or capacity lever might close the largest *verified* screening gap per rupee? The answer is withheld until screening coverage, adult population, and costs can be supported. This is a hypothetical work sample, not a commission from a health mission.

## Scope

- Maharashtra: Mumbai, Pune, Gadchiroli.
- Odisha: Khordha, Koraput, Malkangiri.
- Six contrasting pilot districts across two states; do not treat them as statistically representative. Their urban/rural labels, facility access and relative income have not been validated.
- Adults aged 15+ are the survey universe of the selected NFHS-5 blood-sugar indicator. Any later programme targeting 30+ must obtain age-compatible data; do not silently apply the 15+ rate to that group.
- NFHS-5 district fact sheets are the starting source of observed *blood-glucose elevation or medicine* by sex. These percentages cannot be added or averaged without sex-specific denominators.
- NFHS-4 cells for these indicators in this third-party CSV are zero placeholders, not demonstrated historical observations. The extractor does not emit NFHS-4 rows rather than claiming a trend.

## Planned funnel, conditional on evidence

| Stage | Proposed measure | Status |
| --- | --- | --- |
| Population | District adults in the **same age range and geography** | Not sourced; must acquire census-derived compatible estimate, vintage and uncertainty. |
| Potential need | Sex-specific NFHS-5 elevated blood sugar or taking medicine | Observed proxy only; not diabetes prevalence, clinical diagnosis or full screening eligibility. |
| Aware | Proportion aware of condition among those needing care | Not in selected CSV; source or label as explicit scenario assumption. |
| Screened | Distinct adults screened in period / eligible adults | HMIS or survey source to validate, deduplicate, and align denominator; unknown now. |
| Referred / treated | Documented follow-up among those flagged | Not sourced; cannot be assumed from screening volume. |

The plausible operational pathway may not be a strict nested subset of NFHS blood-sugar elevation: screened people include those with normal results; treated people can precede this period's screen. Phase 2 must define cohorts and time windows before enforcing conservation. Avoid presenting a misleading single five-stage funnel until then.

## Decision criteria

Use incremental people reached and cost per incremental, eligible person screened *only after* denominator, baseline coverage, intervention effect and costs are identified. Show source dates and assumptions for every input, uncertainty intervals for scenario estimates, and a reversal condition. Never rank districts by raw blood-sugar percentage alone.
