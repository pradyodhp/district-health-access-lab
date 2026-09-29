# Interview kit

**Why this vertical?** Blood-glucose screening is an important NCD access question, and NFHS-5 publishes district-level adult glucose indicators. Those indicators are a need proxy only. I deliberately did not turn them into a screening gap.

**Where do the numbers come from?** Six pilot districts, four sex-specific indicators each, from a versioned community transcription of NFHS-5; every row carries source URL, survey vintage, retrieval date, source hash and an unverified marker. The 10,000-person scenario is invented to test mechanics, clearly labeled hypothetical.

**What assumptions dominate?** The app uses SALib Morris to screen the example model's input ranges. A high effect means that model outcome depends on an input; it does not validate the input or imply that a district should get funding.

**How would you validate?** Compare every selected indicator with the official district PDF; align district boundaries and age-specific population; distinguish unique persons screened from visits in HMIS; document private-sector omissions and sample error. Then test against a historical service period and interview implementers about costs and constraints.

**What is v2?** A sourced screening denominator, follow-up and cost ledger, district geospatial layer with documented boundary vintage, true scenario bands, and a PDF memo export. Add these only after the evidence gates, rather than painting an unsupported gap red on a map.

**Live demo script (2 minutes):** Overview shows why the decision is on hold. District evidence shows observed sex-specific percentages and provenance. Scenario lab shows an illustrative funnel, bands and Morris ranking. Memo states the information that would change the decision. The strongest choice is refusing to rank districts from an unrelated percentage.
