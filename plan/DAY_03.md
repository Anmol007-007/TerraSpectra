# Day 3 — Synthetic hyperspectral data generator; Deck.gl + Mapbox base map

Goal: Physically-inspired synthetic cubes with stress/disease dynamics and labels; base 3D map renders.

**Branch:** `day/03-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Spectral signature simulator

- [ ] **01** `feat(synth): add wavelength grid builder 224 bands 400-2500nm`
- [ ] **02** `feat(synth): add gaussian absorption feature helper`
- [ ] **03** `feat(synth): add healthy leaf baseline reflectance model`
- [ ] **04** `feat(synth): add chlorophyll absorption at 450 and 670nm`
- [ ] **05** `feat(synth): add carotenoid absorption feature`
- [ ] **06** `feat(synth): add red-edge sigmoid transition near 710nm`
- [ ] **07** `feat(synth): add NIR plateau model`
- [ ] **08** `feat(synth): add leaf water absorption at 970 1200 1450 1940nm`
- [ ] **09** `feat(synth): add SWIR dry-matter slope`
- [ ] **10** `feat(synth): add wavelength-dependent sensor noise model`
- [ ] **11** `feat(synth): add atmospheric absorption masks`
- [ ] **12** `test(synth): add healthy spectrum shape and range tests`

## B. Stress and disease model

- [ ] **13** `feat(synth): add disease severity parameter model`
- [ ] **14** `feat(synth): add chlorophyll reduction as function of severity`
- [ ] **15** `feat(synth): add red-edge blue shift with stress`
- [ ] **16** `feat(synth): add PRI change under stress`
- [ ] **17** `feat(synth): add leaf water decrease under stress`
- [ ] **18** `feat(synth): add SWIR reflectance increase under stress`
- [ ] **19** `feat(synth): add visible symptom threshold at severity 0.6`
- [ ] **20** `feat(synth): add logistic temporal progression over 21 days`
- [ ] **21** `feat(synth): add days-to-symptoms computation`
- [ ] **22** `test(synth): add monotonic severity response tests`

## C. Spatial field generator

- [ ] **23** `feat(synth): add farm polygon generator for 1000 acres`
- [ ] **24** `feat(synth): add crop parcel partitioning`
- [ ] **25** `feat(synth): add soil background spectrum and mixing`
- [ ] **26** `feat(synth): add gaussian random field helper`
- [ ] **27** `feat(synth): add outbreak seed sampler`
- [ ] **28** `feat(synth): add spatial diffusion of severity`
- [ ] **29** `feat(synth): add 5 acre hotspot injector`
- [ ] **30** `feat(synth): add synthetic DEM generator`
- [ ] **31** `feat(synth): add illumination shading from DEM`
- [ ] **32** `test(synth): add hotspot area approx 5 acres test`

## D. Cube assembly

- [ ] **33** `feat(synth): add cube composer returning float32 B H W`
- [ ] **34** `feat(synth): add noise injection to cube`
- [ ] **35** `feat(synth): add cloud and dead pixel simulation`
- [ ] **36** `feat(synth): add state and severity label masks`
- [ ] **37** `feat(synth): add forecast labels for horizons 7 14 21`
- [ ] **38** `feat(synth): add multi-date time series generation`
- [ ] **39** `feat(synth): add metadata sidecar JSON`
- [ ] **40** `test(synth): add cube shape dtype and label tests`

## E. Synth CLI

- [ ] **41** `feat(synth): add typer CLI generate command`
- [ ] **42** `feat(synth): add seed and size options`
- [ ] **43** `feat(synth): add progress bar`
- [ ] **44** `feat(synth): add output directory layout`
- [ ] **45** `build: add make synth target`
- [ ] **46** `test(synth): add CLI smoke test on tiny scene`

## F. Frontend map base

- [ ] **47** `build(web): add mapbox-gl and react-map-gl dependencies`
- [ ] **48** `build(web): add deck.gl dependencies`
- [ ] **49** `feat(web): add DeckGL overlay component`
- [ ] **50** `feat(web): add BaseMap component with token handling`
- [ ] **51** `feat(web): add satellite and streets style switch with maplibre fallback`
- [ ] **52** `test(web): add BaseMap render test with mocked map`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/03-work` into `main` with `--no-ff`.
