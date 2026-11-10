# Day 2 — Core config, logging, schemas, constants; frontend foundations

Goal: Settings/logging/utility core with typed schemas and constants; Tailwind + layout shell for the dashboard.

**Branch:** `day/02-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Configuration system

- [ ] **01** `feat(core): add pydantic-settings Settings class with TS_ env prefix`
- [ ] **02** `feat(core): add data directory and models directory settings`
- [ ] **03** `feat(core): add device setting auto cpu cuda`
- [ ] **04** `feat(core): add YAML config loader with deep merge`
- [ ] **05** `feat(configs): add default.yaml`
- [ ] **06** `feat(configs): add data.yaml with bands gsd crs and patch size`
- [ ] **07** `feat(configs): add model.yaml with cnn and vit hyperparameters`
- [ ] **08** `test(core): add settings and yaml loader tests`

## B. Core utilities

- [ ] **09** `feat(core): add structured logging setup`
- [ ] **10** `feat(core): add rich console handler for dev logs`
- [ ] **11** `feat(core): add seed_everything utility for numpy torch random`
- [ ] **12** `feat(core): add Timer context manager and timing decorator`
- [ ] **13** `feat(core): add select_device utility with cuda fallback`
- [ ] **14** `feat(core): add path helpers for data raw interim processed`
- [ ] **15** `feat(core): add sha256 file and config hashing helpers`
- [ ] **16** `test(core): add tests for seed timer device hashing`

## C. Domain schemas

- [ ] **17** `feat(core): add GeoBounds pydantic model`
- [ ] **18** `feat(core): add BandInfo and WavelengthGrid models`
- [ ] **19** `feat(core): add SceneMetadata model`
- [ ] **20** `feat(core): add PixelState enum healthy stressed diseased`
- [ ] **21** `feat(core): add TileSpec model`
- [ ] **22** `feat(core): add JobStatus enum and Job model`
- [ ] **23** `feat(core): add RiskZone model with area acres and lead time`
- [ ] **24** `feat(core): add AnalyticsSummary and Anomaly models`
- [ ] **25** `feat(core): add custom error classes for data and inference`
- [ ] **26** `test(core): add schema validation tests`

## D. Constants and conversions

- [ ] **27** `feat(core): add spectral region constants VNIR and SWIR`
- [ ] **28** `feat(core): add index wavelength constants for NDVI PRI NDWI`
- [ ] **29** `feat(core): add water-vapour bad band ranges`
- [ ] **30** `feat(geo): add m2 to acres and acres to m2 converters`
- [ ] **31** `feat(geo): add pixels to acres using GSD`
- [ ] **32** `test(geo): add conversion tests for 5 acre and 1000 acre cases`

## E. Frontend configuration

- [ ] **33** `build(web): add tailwindcss and postcss config`
- [ ] **34** `build(web): add path aliases in vite and tsconfig`
- [ ] **35** `chore(web): create src folder structure components layers store hooks api utils types`
- [ ] **36** `feat(web): add global styles and CSS variables`
- [ ] **37** `feat(web): add design tokens for risk colors and theme`
- [ ] **38** `feat(web): add typed env accessor with defaults`
- [ ] **39** `feat(web): add geo and analytics TypeScript types`
- [ ] **40** `feat(web): add Header component`
- [ ] **41** `feat(web): add Sidebar component shell`
- [ ] **42** `feat(web): add AppLayout with header sidebar map and panel regions`

## F. Frontend base utilities

- [ ] **43** `feat(web): add MapContainer placeholder component`
- [ ] **44** `feat(web): add zustand store with ui slice`
- [ ] **45** `feat(web): add API client skeleton with fetch wrapper`
- [ ] **46** `feat(web): add app constants for GSD and acre conversion`
- [ ] **47** `feat(web): add acres utility functions`
- [ ] **48** `feat(web): add number and date format utilities`
- [ ] **49** `test(web): add tests for acres and format utils`
- [ ] **50** `test(web): add AppLayout render test`
- [ ] **51** `build(web): add react-query provider`
- [ ] **52** `docs(web): add web/README with run instructions`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/02-work` into `main` with `--no-ff`.
