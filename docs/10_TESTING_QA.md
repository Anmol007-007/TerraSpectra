# 10 — Testing & QA
- **Unit**: every public function. **Integration**: synth → ingest → preprocess → train(smoke) → infer. **API**: FastAPI TestClient, error paths, upload limits. **Property**: hypothesis for tiling coverage, transforms round-trip, area conversions.
- **Golden tests**: tiny synthetic cube (16×16×224) fixtures in `tests/fixtures`.
- **Overfit test**: model must overfit 32 samples to >95% acc in <200 steps.
- **Coverage gates**: backend 85%, frontend 75% (CI fails below).
- **Static**: `ruff check`, `ruff format --check`, `mypy --strict src`, `tsc --noEmit`, `eslint`.
- **E2E (Playwright)**: load map, run prediction (mock), select zone, timeline play, theme toggle.
- **Perf**: `scripts/audit_memory.py` (peak RSS/VRAM vs budget), `scripts/bench_*.py`, Locust API load test.
- **Security**: pip-audit, npm audit, upload validation, path traversal tests.
- **Definition of Done** per day: 52 commits · CI green · tests for new code · docs updated.
