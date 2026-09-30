# Evidence methodology

The bundled source is a third-party NFHS CSV transcription, not an official district release. The compressed snapshot is versioned; `manifest.json` records the uncompressed SHA256 and vintage. Build checks bytes/metadata before writing the 24-row extract. Exact district/indicator labels, duplicate detection, missingness and percentage bounds fail closed. Source metadata remains provisional; official factsheet cross-check is still missing.

Evidence lifecycle: OBSERVED, OBSERVED_UNVERIFIED, DERIVED, ASSUMED, HYPOTHETICAL, INCOMPATIBLE, REJECTED. Current 24 records remain OBSERVED_UNVERIFIED. Derived records require parent IDs and a named transformation. Lineage rejects duplicate IDs, cycles and missing parents. Source URL, retrieval date, period, geography/level, population, age/sex, unit, source identifier/hash, confidence, caveat and method are available metadata. Numerator/denominator are explicitly typed when supplied; unavailable metadata is not invented.

Current NFHS period endpoints represent the documented 2019-21 survey window, not exact district fieldwork dates. They are coarse metadata and do not authenticate individual records. Retrieval date is not survey freshness. Geography codes in the CSV still require boundary verification. Blood-glucose/blood-pressure elevation or medicine percentages are proxies, not diagnosis or screening coverage. No sex-weighted average, NFHS-4 trend or causal effect is inferred.

Sources: [transcription repository](https://github.com/SaiSiddhardhaKalla/NFHS), [official factsheet index](https://rchiips.org/nfhs/districtfactsheet_NFHS-5.shtml). These are source routes, not claims of completed official verification.
