# Day 19 — Test hardening, Docker, CI/CD, E2E, performance (tag v0.3.0)

Goal: Everything containerised, tested end-to-end, fast, and green in CI.

**Branch:** `day/19-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Backend tests

- [ ] **01** `test: fill unit test gaps in data package`
- [ ] **02** `test: add integration test synth to preprocess to infer`
- [ ] **03** `test(api): add full API workflow test`
- [ ] **04** `test: add hypothesis tests for transforms`
- [ ] **05** `test: consolidate shared fixtures`
- [ ] **06** `test: add golden-file tests for tiny cube`
- [ ] **07** `test: raise coverage to 85 percent`
- [ ] **08** `chore: make mypy strict clean`
- [ ] **09** `chore: make ruff clean`
- [ ] **10** `test: add slow marker and make test-fast`
- [ ] **11** `test(cli): add CLI tests`
- [ ] **12** `docs: write testing guide`

## B. Docker

- [ ] **13** `build(docker): add API Dockerfile for CUDA`
- [ ] **14** `build(docker): add API Dockerfile for CPU`
- [ ] **15** `build(docker): add web Dockerfile`
- [ ] **16** `build(docker): add nginx config for web`
- [ ] **17** `build(docker): add docker-compose.yml`
- [ ] **18** `build(docker): add GPU compose profile`
- [ ] **19** `build(docker): add healthchecks`
- [ ] **20** `build(docker): add env files`
- [ ] **21** `build(docker): add .dockerignore`
- [ ] **22** `build: add make docker-up target`

## C. CI/CD

- [ ] **23** `ci: add python version matrix`
- [ ] **24** `ci: add dependency caching`
- [ ] **25** `ci: add docker build job`
- [ ] **26** `ci: upload coverage report`
- [ ] **27** `ci: add release workflow`
- [ ] **28** `ci: add tag-based release`
- [ ] **29** `docs: add CI badges to README`
- [ ] **30** `ci: add dependabot config`

## D. Frontend QA

- [ ] **31** `test(web): add Playwright config`
- [ ] **32** `test(web): add e2e map load test`
- [ ] **33** `test(web): add e2e run prediction test`
- [ ] **34** `test(web): add e2e timeline test`
- [ ] **35** `test(web): add e2e zone select test`
- [ ] **36** `test(web): add visual regression snapshots`
- [ ] **37** `chore(web): run Lighthouse audit`
- [ ] **38** `fix(web): improve responsive layout`
- [ ] **39** `fix(web): resolve axe findings`
- [ ] **40** `perf(web): reduce bundle size`
- [ ] **41** `perf(web): add route and layer code splitting`
- [ ] **42** `fix(web): harden ErrorBoundary`
- [ ] **43** `perf(web): lazy-load heavy layers`
- [ ] **44** `test(web): raise coverage to 75 percent`

## E. Performance

- [ ] **45** `perf(api): profile endpoints`
- [ ] **46** `perf(data): optimise preprocessing hot loops`
- [ ] **47** `perf(data): vectorise window operations`
- [ ] **48** `perf(api): cache model across requests`
- [ ] **49** `perf(api): reduce startup time`
- [ ] **50** `test(perf): add Locust load test`
- [ ] **51** `docs: record load test results`
- [ ] **52** `perf: apply tuning from results`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/19-work` into `main` with `--no-ff`.
