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
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

Requires Python 3.10+. The extraction itself has no third-party dependencies. A future pipeline will add the **official district fact-sheet cross-check**, a valid district population denominator and a real screening-coverage source before any district ranking, cost-per-person estimate, or funnel is presented as evidence. The raw CSV is an independently maintained parse of [NFHS-5/4 district fact sheets](https://github.com/SaiSiddhardhaKalla/NFHS), not an official release. See [source manifest](data/raw/SOURCES.md).

## Roadmap

1. Verify selected rows against official district PDFs, document any corrections, and source denominators and screening volumes from a comparable period.
2. Build a pure-Python funnel engine with separate observed and assumed inputs, bounds and conservation tests; expose it through FastAPI.
3. Add scenarios, uncertainty bands and sensitivity (SALib) after inputs are defensible.
4. Build the React decision interface, one-page memo and interview kit.

No individual health records, clinical advice, or operational funding recommendation are included.
