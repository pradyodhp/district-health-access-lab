# District Health Access & Demand Lab — Full Build Plan

A decision tool, not a dashboard. It answers three questions a health consultant would actually be paid to answer:

1. Where is the access gap? (which districts, how big)
2. What would it cost to close it? (which lever, how much)
3. Which assumption should we research more before deciding?

Target reader: a ZS / consulting interviewer opening the repo. Every artifact is built so that person concludes "this candidate thinks like an analyst AND ships like an engineer."

---

## The core model (one sentence)

For a chosen health service (e.g. diabetes screening, anemia treatment, institutional delivery) in a set of Indian districts:

**population -> eligible need -> aware -> screened -> treated**, with a gap and a cost-to-close at every stage, uncertainty on every input, and sliders for the levers (uptake, capacity, outreach spend).

---

## Phase 0 — Scope & problem framing (2-3 days)

**Deliverable: a one-page problem brief in the repo (`docs/problem-brief.md`).**

- Pick ONE service vertical. Recommended: **diabetes/hypertension screening in adults** (NFHS-5 has the indicators, the funnel logic is clean, and "NCD screening gap" is a real consulting topic). Backup: anemia in women 15-49.
- Pick 5-8 districts across 2-3 states with contrasting profiles (e.g. one urban, one tribal-rural, one mid-income) so comparisons are interesting.
- Define the funnel stages and the exact indicator for each. Every stage must map to a real NFHS/HMIS field or an explicitly-labeled assumption.
- Write the decision question in consulting language: "A state health mission has INR X crore. Which districts and which levers close the most screening gap per rupee?"

Placement-grade bar: the brief reads like the first slide of a client deck — decision, scope, data sources, explicit assumptions. No code yet.

## Phase 1 — Data foundation (1 week)

**Deliverable: a clean, versioned dataset + data dictionary + provenance table.**

Sources, in priority order:
1. **NFHS-5 (and NFHS-4 for trend) district CSVs** — SaiSiddhardhaKalla/NFHS repo as the starting parse, cross-checked against the official NFHS district factsheets (rchiips.org/nfhs).
2. **data.gov.in / HMIS** — facility counts, screening volumes where published.
3. **Census 2011 / projected population** — district denominators (state projections for 2026).
4. **WHO / World Bank APIs** — benchmark rates for context only, never as the primary number.

Build:
- `data/raw/` (untouched originals + download date + source URL), `data/processed/` (tidy parquet/CSV).
- `data/data_dictionary.md` — every column, unit, source, date, and whether it is OBSERVED or ASSUMED.
- A `provenance` table keyed per indicator: value, source, vintage, confidence grade (A/B/C).

Placement-grade bar: someone can trace any number on the UI to a source in under 30 seconds. This is the single biggest differentiator from student projects.

## Phase 2 — Funnel engine + uncertainty (1-2 weeks)

**Deliverable: a tested Python engine (FastAPI service) that computes the funnel with uncertainty bands.**

- Modular monolith (same pattern as Marketwatchdawg): `engine/` (pure functions, no web), `api/` (FastAPI), `scenarios/`.
- Every input parameter is a **distribution, not a point** (min/mode/max triangular or PERT — explainable in an interview without stats jargon). Observed values get narrow bands; assumptions get wide ones. This is the getguesstimate lesson: uncertainty on every input.
- Monte Carlo (numpy, 10k runs) -> p10/p50/p90 bands on every funnel stage and on the final access-gap number.
- Cost model: cost per additional screened person per lever (outreach camp, ASHA incentive, facility capacity). Costs are labeled ASSUMED with sources where findable.
- Pytest suite on the engine: monotonicity checks (gap shrinks when uptake rises), conservation checks (stage n+1 <= stage n), known-answer tests on one hand-computed district.

Placement-grade bar: in the interview he can say "every number is a distribution, here is the p50 and the band, and here is the test that proves the funnel math can't leak people."

## Phase 3 — Scenarios, levers & sensitivity (1-2 weeks)

**Deliverable: scenario API + sensitivity analysis + "what to research next" output.**

- Levers as scenario deltas: screening uptake +x%, facility capacity +y, outreach spend +z. Named presets ("Status quo", "Max outreach", "Capacity-first").
- **SALib** (Sobol or Morris) over the input distributions -> which assumptions actually move the answer. Render as a tornado chart (htaBIM-style) + a ranked "which assumption needs more research" list. Do NOT hand-roll the statistics — importing SALib is the industry-standard move and saying so in an interview is a plus.
- Scenario comparison endpoint: two scenarios side by side with delta-in-gap and delta-in-cost, including band overlap (honest about when two options are statistically indistinguishable).

Placement-grade bar: the tool can say "the answer barely changes unless the awareness-rate assumption is wrong — go research THAT" — that sentence is a ZS answer.

## Phase 4 — Front end (2 weeks)

**Deliverable: the React app — the thing an interviewer actually looks at.**

Stack: React + Vite + Tailwind + Recharts (or ECharts), served by FastAPI as a static build like Marketwatchdawg (dev on Vite hot-reload).

Four views, no more:
1. **Funnel view** — one district, the five-stage funnel as a horizontal waterfall with p10-p90 bands per stage; the gap in red, covered population in neutral ink.
2. **Map view** — district choropleth of gap size (GeoJSON district boundaries, public domain); click a district to load its funnel.
3. **Scenario view** — sliders for the levers; bands update live; compare two scenarios side by side; tornado chart + sensitivity ranking.
4. **Memo view** — the auto-generated one-page decision memo (see Phase 5).

Design: his Porsche-mono taste — white/ink minimal, red only for the gap/problem, blue only for healthy/improved, big numbers, zero text walls.

Placement-grade bar: 60 seconds on the funnel view and the interviewer understands the whole project.

## Phase 5 — Decision memo + honesty layer (3-4 days)

**Deliverable: auto-generated one-page decision memo (markdown -> PDF) + limitations section.**

- Memo template: decision, recommendation, the 3 numbers that matter, the band on each, what would change the recommendation, cost estimate. Regenerated from the current scenario — the user clicks "export memo" and gets a PDF.
- `LIMITATIONS.md` + an in-app limitations panel: what the model cannot see (supply-side quality, private-sector share, NFHS sampling error at district level, cross-sectional not longitudinal). Written plainly.
- `docs/methodology.md` — the funnel math, the uncertainty approach, why SALib, why triangular distributions. Written so a non-technical interviewer gets it in 5 minutes.

Placement-grade bar: the limitations section is what separates "student demo" from "consultant work sample". Admitting limits reads senior.

## Phase 6 — Ship & placement packaging (1 week)

**Deliverable: public repo + live demo + interview kit.**

- README with: the decision question up top, a 3-screenshot tour, architecture diagram, data sources, how to run in 2 commands.
- Deploy: FastAPI serving the built front end on Render/Railway free tier (single service, like Marketwatchdawg). Fallback: Vercel front + Render API.
- CI: GitHub Actions running pytest + a data-validation check on every push.
- 2-3 min walkthrough video or GIF in the README.
- `INTERVIEW.md`: the 5 questions he'll get ("why this vertical", "where do the numbers come from", "what are the biggest assumptions", "how would you validate", "what's v2") with his answers, so the project survives the interview, not just the skim.

---

## Stack summary

| Layer | Choice | Why |
|---|---|---|
| Engine | Python, pandas, numpy | his comfort zone, Monte Carlo is trivial |
| Sensitivity | SALib | industry standard, no hand-rolled stats |
| API | FastAPI + Pydantic | typed params = distributions enforced by schema |
| Storage | flat files (parquet/CSV) + DuckDB optional | no DB ops burden for a portfolio piece |
| Front end | React + Vite + Tailwind + Recharts | same pattern he already knows |
| Charts | funnel waterfall, choropleth, tornado, band plots | 4 chart types, done well |
| Deploy | single FastAPI service on Render/Railway | one URL in the README |

## Timeline

6-8 weeks at student pace (evenings/weekends), or ~3 weeks at full-time pace. Phases 0-2 produce an impressive repo even if nothing else ships — the data foundation + engine alone beats most portfolio projects. Front end is Phase 4 deliberately: the thinking is the product, the UI is the packaging.

## Reference repos (steal ideas, fork nothing)

- getguesstimate/guesstimate-app — uncertainty-on-every-input UX
- Heorlytics/htaBIM — funnel + tornado chart shapes, pharma decision-model skeleton
- nhs-bnssg-analytics/PathSimR — healthcare pathway modeling rigor
- SaiSiddhardhaKalla/NFHS — dataset starting point
- SALib/SALib — sensitivity analysis

## Hard rules for the build

- Every number traceable: OBSERVED vs ASSUMED labeled everywhere, never mixed silently.
- Uncertainty shown, never hidden. Bands on everything.
- It answers a decision. Any feature that doesn't move the decision gets cut.
- Limitations stated before the interviewer asks.
- No fabricated data anywhere; gaps get wide bands and a label, not invented precision.
