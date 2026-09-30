# Testing and quality gates

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check src scripts tests
python3 scripts/build_data.py
python3 -m pytest -q --cov=health_access --cov-report=term-missing
pip-audit -r requirements.txt
(cd web && npm ci && npm test && npm run build && npm audit --audit-level=moderate)
python3 scripts/demo.py --output /tmp/training-demo
```

Use Python 3.10+; CI runs 3.11, Node 22. Ruff deliberately enforces F rules (undefined/unused code), not a claim of complete formatting or type coverage. Backend tests cover extraction, units, model conservation/monotonicity, reproducibility, readiness incompatibility, artifacts/hash tampering, memo context, optimization/dependencies and API rejection. Coverage is a diagnostic, not proof of correctness.

Frontend runs 3 pure utility tests and Vitest/Testing Library components/journey tests: readiness/HOLD reasons, loading, hash/storage metadata, model run/edit invalidation and API failure. Component mocks are not a real browser E2E test; a separate Playwright suite in e2e/ drives the real app in Chromium (evidence to run to replay to memo, plus an API-failure case) and runs an axe-core WCAG 2 A/AA scan of each workbench section, all in CI. Local real HTTP smoke exercises compatibility routes, new health/backlog/replay and invalid-input bounds. Visual browser acceptance should inspect desktop/mobile after UI changes. Automated a11y covers only axe-detectable rules (contrast, names, roles); manual screen-reader and keyboard review is not done. Concurrency/load and static Python typing remain work.

CI checks pipeline/checksum drift, backend tests/coverage/lint/audit, npm locked install/tests/build/audit, actual API smoke and deterministic training demo. A pending CI run is not success until read back.
