# Day 9 — Mid-Project: Extraction Audit (memory) + GIS Validation (geo alignment)

Goal: PROVE the pipeline handles massive 3D tensor memory needs; PROVE Deck.gl overlay aligns with real GPS coordinates.

**Branch:** `day/09-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Memory profiling tools

- [ ] **01** `feat(profiling): add memory profiler utility`
- [ ] **02** `feat(profiling): add CUDA memory stats helper`
- [ ] **03** `feat(profiling): add CPU RSS tracker`
- [ ] **04** `feat(profiling): add tensor size calculator`
- [ ] **05** `feat(profiling): add batch size estimator from memory budget`
- [ ] **06** `feat(profiling): add dataloader profiling`
- [ ] **07** `feat(profiling): add forward pass profiling`
- [ ] **08** `feat(profiling): add backward pass profiling`
- [ ] **09** `feat(profiling): add report writer markdown and json`
- [ ] **10** `feat(scripts): add audit_memory.py`
- [ ] **11** `test(profiling): add tensor size calculation tests`
- [ ] **12** `docs: add memory audit methodology`

## B. Memory optimisations

- [ ] **13** `perf(training): add bf16 autocast option`
- [ ] **14** `perf(training): add gradient accumulation`
- [ ] **15** `perf(training): add gradient checkpointing in CNN blocks`
- [ ] **16** `perf(training): add channels_last_3d memory format`
- [ ] **17** `perf(data): add patch size reduction config`
- [ ] **18** `perf(data): add float16 cache for processed cubes`
- [ ] **19** `perf(data): add pinned memory buffers`
- [ ] **20** `perf(data): tune num_workers automatically`
- [ ] **21** `perf(data): enable persistent workers`
- [ ] **22** `perf(data): add np.memmap backed arrays`
- [ ] **23** `feat(training): add OOM handler with batch halving retry`
- [ ] **24** `test(training): add OOM retry test with simulated error`

## C. Benchmarks

- [ ] **25** `feat(scripts): add large synthetic cube generator 2048x2048x224`
- [ ] **26** `feat(scripts): add throughput benchmark`
- [ ] **27** `feat(scripts): add dataloader benchmark`
- [ ] **28** `feat(scripts): write benchmark results CSV`
- [ ] **29** `feat(scripts): add benchmark plot`
- [ ] **30** `feat(profiling): add memory budget thresholds`
- [ ] **31** `test(profiling): add light CI benchmark test`
- [ ] **32** `docs: document benchmark results`

## D. GIS validation backend

- [ ] **33** `feat(geo): add pixel to lon/lat transform`
- [ ] **34** `feat(geo): add lon/lat to pixel transform`
- [ ] **35** `test(geo): add affine round-trip tests`
- [ ] **36** `feat(geo): add bounds to GeoJSON helper`
- [ ] **37** `feat(geo): add georeference check for prediction rasters`
- [ ] **38** `feat(geo): add pixel area helper`
- [ ] **39** `test(geo): add acre computation tests`
- [ ] **40** `feat(geo): add GCP fixtures JSON generator`

## E. GIS validation frontend

- [ ] **41** `feat(web): add pixelToLonLat util`
- [ ] **42** `feat(web): add backend fixture comparison test`
- [ ] **43** `test(web): add overlay alignment unit test`
- [ ] **44** `feat(web): add GCP markers debug layer`
- [ ] **45** `feat(web): add debug overlay toggle`
- [ ] **46** `feat(web): add crosshair component`
- [ ] **47** `feat(web): add coordinate readout`
- [ ] **48** `docs(web): note on mercator vs UTM distortion`
- [ ] **49** `test(web): add alignment tolerance tests`
- [ ] **50** `chore(web): add shared GCP fixtures`
- [ ] **51** `docs(web): add visual alignment checklist`
- [ ] **52** `fix(web): correct half-pixel offset in cell polygons`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/09-work` into `main` with `--no-ff`.
