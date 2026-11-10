# Day 17 — Tiling and stitching engine, GPU batching, correctness; timeline scaffold

Goal: Process massive rasters in tiles with seamless stitching; timeline slider foundation.

**Branch:** `day/17-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Tiling engine

- [ ] **01** `feat(inference): add TileSpec and tile grid generator`
- [ ] **02** `feat(inference): add overlap configuration`
- [ ] **03** `feat(inference): add edge tile reflection padding`
- [ ] **04** `feat(inference): add windowed tile reader`
- [ ] **05** `feat(inference): add tile index and ordering`
- [ ] **06** `feat(inference): add tile batch builder`
- [ ] **07** `feat(inference): add per-tile preprocessing`
- [ ] **08** `feat(inference): add tile inference function`
- [ ] **09** `feat(inference): add 2D Hann window weights`
- [ ] **10** `feat(inference): add stitcher accumulators`
- [ ] **11** `feat(inference): normalise by weight sum`
- [ ] **12** `feat(inference): write stitched GeoTIFF output`
- [ ] **13** `feat(inference): add memmap-backed stitcher for huge scenes`
- [ ] **14** `test(inference): add tile grid tests`

## B. GPU batching

- [ ] **15** `feat(inference): add dynamic batch size selection`
- [ ] **16** `feat(inference): add OOM backoff with retry`
- [ ] **17** `feat(inference): add pinned memory transfers`
- [ ] **18** `feat(inference): add CUDA stream overlap option`
- [ ] **19** `feat(inference): add tile DataLoader`
- [ ] **20** `feat(inference): add throughput metrics`
- [ ] **21** `feat(scripts): add tiling benchmark`
- [ ] **22** `test(inference): add batching tests`

## C. Tiling correctness

- [ ] **23** `test(inference): compare tiled vs full inference on small scene`
- [ ] **24** `test(inference): add seam artifact test`
- [ ] **25** `test(inference): add border handling test`
- [ ] **26** `test(inference): add non-square scene test`
- [ ] **27** `test(inference): add single-tile scene test`
- [ ] **28** `test(inference): add 2048x2048 synthetic scene test`
- [ ] **29** `test(inference): add hypothesis property tests for coverage`
- [ ] **30** `docs: document tiling algorithm and guarantees`

## D. API tiling endpoints

- [ ] **31** `feat(api): add POST /v1/predict/tile`
- [ ] **32** `feat(api): add tile processing status`
- [ ] **33** `feat(api): add progress counters`
- [ ] **34** `feat(api): add cancellation hook`
- [ ] **35** `test(api): add tiling endpoint tests`
- [ ] **36** `docs: update API spec for tiling`

## E. Frontend timeline scaffold

- [ ] **37** `feat(web): add Timeline types`
- [ ] **38** `feat(web): use scene timeline endpoint`
- [ ] **39** `feat(web): add TimelineSlider component`
- [ ] **40** `feat(web): add date ticks`
- [ ] **41** `feat(web): add play and pause button`
- [ ] **42** `feat(web): add speed control`
- [ ] **43** `feat(web): add selected date state`
- [ ] **44** `feat(web): make layers follow selected date`
- [ ] **45** `feat(web): prefetch adjacent dates`
- [ ] **46** `feat(web): add timeline skeleton`
- [ ] **47** `feat(web): add keyboard control for slider`
- [ ] **48** `test(web): add timeline tests`
- [ ] **49** `docs(web): document timeline`
- [ ] **50** `chore(web): add timeline mock data`
- [ ] **51** `style(web): add timeline accessibility roles`
- [ ] **52** `test(web): add timeline integration test`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/17-work` into `main` with `--no-ff`.
