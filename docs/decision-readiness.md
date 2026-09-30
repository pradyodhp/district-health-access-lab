# Decision readiness

`GET /api/readiness` and `POST /api/case/readiness` expose ten gates: POPULATION, GEOGRAPHY, TIME_PERIOD, NUMERATOR_DENOMINATOR, SCREENING_COVERAGE, POPULATION_DENOMINATOR, INTERVENTION_EFFECT, COST, CAPACITY, MODEL_STABILITY. Each returns state, reason, supporting IDs, missing evidence, blocking severity and next research action.

Current implementation uses PASS, FAIL and HOLD; NOT_APPLICABLE is reserved but not emitted because all ten gates are required for this healthcare funding question. Verified matching metadata/reviewer records are necessary, not independent certification. Derived records require trusted parent chains. Explicit rejected/incompatible records fail; missing/unverified evidence holds. Direct screening coverage needs distinct-person numerator/denominator and a consistent rate. Each required variable must cover every case geography. Exact period/population/geography-level checks prevent silent reuse across cohorts or vintages.

HYPOTHETICAL_ONLY never authorizes real funding. A REAL case with all metadata gates passing is READY_FOR_REVIEW, not a clinical/policy recommendation; actual real runs remain rejected. Current repository evidence cannot reach that state. Checklist points are not probabilities. The model-stability record is an explicit reviewed evidence requirement, not Monte Carlo convergence dressed up as validation.

Remaining limits: no evidence intake/authenticated reviewer workflow, time adequacy/transportability expert judgment, or operational sign-off. No user can obtain a genuine recommendation by changing a status string in a demo.
