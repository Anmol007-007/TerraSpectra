# Day 18 — Async jobs, caching, security, observability; historical spectral health timeline

Goal: Production-grade API behaviours; timeline shows crop spectral health progression with compare mode.

**Branch:** `day/18-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Job management

- [ ] **01** `feat(api): add JobStore interface`
- [ ] **02** `feat(api): add in-memory job store`
- [ ] **03** `feat(api): add sqlite job persistence`
- [ ] **04** `feat(api): add worker pool executor`
- [ ] **05** `feat(api): run predictions in background tasks`
- [ ] **06** `feat(api): add status transitions`
- [ ] **07** `feat(api): add progress updates`
- [ ] **08** `feat(api): add job timeouts`
- [ ] **09** `feat(api): add job cancellation`
- [ ] **10** `feat(api): add finished job cleanup`
- [ ] **11** `test(api): add job lifecycle tests`
- [ ] **12** `docs: document job lifecycle`

## B. Caching

- [ ] **13** `feat(api): add cache key hashing`
- [ ] **14** `feat(api): add disk result cache`
- [ ] **15** `feat(api): add cache TTL`
- [ ] **16** `feat(api): add cache invalidation`
- [ ] **17** `feat(api): add ETag support`
- [ ] **18** `feat(api): add gzip compression`
- [ ] **19** `feat(api): add range request support for rasters`
- [ ] **20** `test(api): add cache tests`

## C. Security and limits

- [ ] **21** `feat(api): add optional API key auth`
- [ ] **22** `feat(api): add rate limiting`
- [ ] **23** `feat(api): add upload size limit`
- [ ] **24** `feat(api): add file type validation`
- [ ] **25** `feat(api): add path traversal guard`
- [ ] **26** `feat(api): sanitise filenames`
- [ ] **27** `feat(api): tighten CORS config`
- [ ] **28** `test(api): add security tests`

## D. Observability

- [ ] **29** `feat(api): add Prometheus metrics endpoint`
- [ ] **30** `feat(api): add inference timing metrics`
- [ ] **31** `feat(api): add GPU stats gauge`
- [ ] **32** `feat(api): add structured error logging`
- [ ] **33** `chore(api): add log rotation config`
- [ ] **34** `test(api): add metrics tests`

## E. Frontend timeline progression

- [ ] **35** `feat(web): add SpectralHealth series type`
- [ ] **36** `feat(web): add spectral health endpoint hook`
- [ ] **37** `feat(web): add time-series line chart`
- [ ] **38** `feat(web): sync chart scrubber with map`
- [ ] **39** `feat(web): add compare mode toggle`
- [ ] **40** `feat(web): add side-by-side map view`
- [ ] **41** `feat(web): add before/after swipe control`
- [ ] **42** `feat(web): add trend arrows`
- [ ] **43** `feat(web): add progression statistics card`
- [ ] **44** `feat(web): add loop playback`
- [ ] **45** `feat(web): smooth animation transitions`
- [ ] **46** `feat(web): cache loaded frames`
- [ ] **47** `test(web): add progression tests`
- [ ] **48** `perf(web): optimise frame rendering`
- [ ] **49** `chore(web): add timeline a11y labels`
- [ ] **50** `docs(web): document compare mode`
- [ ] **51** `chore(web): update mocks for time series`
- [ ] **52** `style(web): polish timeline controls`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/18-work` into `main` with `--no-ff`.
