# Day 10 — MID-PROJECT REVIEW: audit report, hardening, refactor, release v0.1.0

Goal: Complete Extraction Audit + GIS Validation deliverables, fix issues, tag v0.1.0.

**Branch:** `day/10-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Review deliverables

- [ ] **01** `docs: add mid-project audit report skeleton`
- [ ] **02** `docs: add memory metrics table to audit`
- [ ] **03** `docs: add throughput table to audit`
- [ ] **04** `docs: add data pipeline coverage section`
- [ ] **05** `docs: list known issues in KNOWN_ISSUES.md`
- [ ] **06** `fix: resolve top audit issues`
- [ ] **07** `docs: add GIS validation results section`
- [ ] **08** `docs: add review checklist`
- [ ] **09** `docs: add demo script for mid review`
- [ ] **10** `docs: add CHANGELOG entry for week 1-2`

## B. Backend hardening

- [ ] **11** `chore: fill missing type hints for mypy strict`
- [ ] **12** `style: fix ruff lint warnings`
- [ ] **13** `docs: add missing docstrings to public APIs`
- [ ] **14** `refactor(core): add specific error classes usage`
- [ ] **15** `feat(data): add input validation to readers`
- [ ] **16** `chore: add logging coverage to pipeline steps`
- [ ] **17** `test(data): add empty raster edge case test`
- [ ] **18** `test(data): add nodata-only tile test`
- [ ] **19** `test(data): add single-band raster test`
- [ ] **20** `test(data): add big-endian dtype test`
- [ ] **21** `build: configure coverage settings`
- [ ] **22** `ci: add coverage gate 80 percent`

## C. Refactors

- [ ] **23** `refactor: extract shared constants module`
- [ ] **24** `refactor(data): deduplicate window iterators`
- [ ] **25** `refactor: rename ambiguous helpers`
- [ ] **26** `refactor(configs): clean up config keys`
- [ ] **27** `refactor: remove dead code`
- [ ] **28** `refactor(data): split oversized modules`
- [ ] **29** `refactor: update imports after moves`
- [ ] **30** `test: run full suite and fix regressions`

## D. Frontend hardening

- [ ] **31** `style(web): fix eslint warnings`
- [ ] **32** `chore(web): pass tsc strict check`
- [ ] **33** `test(web): add component tests for LayerPanel and Legend`
- [ ] **34** `fix(web): add aria labels to controls`
- [ ] **35** `feat(web): make sidebar responsive`
- [ ] **36** `feat(web): polish loading states`
- [ ] **37** `feat(web): add friendly error states`
- [ ] **38** `perf(web): memoize layers`
- [ ] **39** `perf(web): fix deck.gl updateTriggers`
- [ ] **40** `chore(web): add bundle analysis script`
- [ ] **41** `ci(web): add coverage threshold 70 percent`
- [ ] **42** `docs(web): update web README`

## E. Release v0.1.0

- [ ] **43** `chore: bump version to 0.1.0`
- [ ] **44** `docs: finalise CHANGELOG v0.1.0`
- [ ] **45** `docs: update README with progress and screenshots`
- [ ] **46** `docs: add architecture diagram updates`
- [ ] **47** `docs: mark week 1-2 plan complete`
- [ ] **48** `ci: run full CI and fix failures`
- [ ] **49** `docs: add demo checklist`
- [ ] **50** `docs: add retrospective notes`
- [ ] **51** `docs: outline week 3 goals`
- [ ] **52** `chore: tag v0.1.0`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/10-work` into `main` with `--no-ff`.
