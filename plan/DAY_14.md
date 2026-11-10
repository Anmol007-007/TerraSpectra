# Day 14 — 21-day forecast: temporal labels/model, risk-zone detection; zone UI

Goal: Predict blight three weeks ahead; extract the 5-acre red zone as GeoJSON; highlight on map.

**Branch:** `day/14-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Temporal labels and data

- [ ] **01** `feat(data): add multi-horizon label generator`
- [ ] **02** `feat(data): add horizons 7 14 21 days`
- [ ] **03** `feat(data): add temporal dataset returning K acquisitions`
- [ ] **04** `feat(data): add sequence stacking of cubes`
- [ ] **05** `feat(data): add temporal pooling option`
- [ ] **06** `feat(data): add delta features between dates`
- [ ] **07** `feat(data): add time encoding`
- [ ] **08** `feat(data): add temporal split by dates`
- [ ] **09** `test(data): add temporal dataset tests`
- [ ] **10** `docs: document temporal labels`

## B. Temporal model

- [ ] **11** `feat(models): add temporal encoder module`
- [ ] **12** `feat(models): add GRU temporal option`
- [ ] **13** `feat(models): add transformer temporal option`
- [ ] **14** `feat(models): fuse spatial spectral and temporal features`
- [ ] **15** `feat(models): add forecast days output`
- [ ] **16** `feat(models): add per-horizon heads`
- [ ] **17** `feat(training): add ordinal forecast loss`
- [ ] **18** `feat(training): add survival-style loss option`
- [ ] **19** `feat(training): add lead-time metric`
- [ ] **20** `test(models): add temporal model tests`
- [ ] **21** `feat(training): add train_temporal script`
- [ ] **22** `test(training): add temporal smoke training test`

## C. Zone detection

- [ ] **23** `feat(inference): add risk threshold map`
- [ ] **24** `feat(inference): add connected components labelling`
- [ ] **25** `feat(inference): add minimum area filter`
- [ ] **26** `feat(inference): polygonize zones with rasterio.features`
- [ ] **27** `feat(inference): add polygon simplification`
- [ ] **28** `feat(inference): add zone statistics`
- [ ] **29** `feat(inference): compute zone area in acres`
- [ ] **30** `feat(inference): rank zones by risk`
- [ ] **31** `test(inference): add 5-acre hotspot detection test`
- [ ] **32** `feat(inference): add GeoJSON export of zones`
- [ ] **33** `test(inference): add zone geometry tests`
- [ ] **34** `feat(cli): add extract-zones command`

## D. Frontend zones

- [ ] **35** `feat(web): add RiskZone types`
- [ ] **36** `feat(web): add zones mock GeoJSON`
- [ ] **37** `feat(web): add zones PolygonLayer`
- [ ] **38** `feat(web): add red highlight styling`
- [ ] **39** `feat(web): add pulsing outline animation`
- [ ] **40** `feat(web): add zone labels`
- [ ] **41** `feat(web): add ZoneList panel`
- [ ] **42** `feat(web): add zone click selection`
- [ ] **43** `feat(web): add fit-to-zone action`
- [ ] **44** `feat(web): add ZoneDetails card`
- [ ] **45** `feat(web): show area in acres`
- [ ] **46** `feat(web): add lead time badge`
- [ ] **47** `feat(web): add recommended action text`
- [ ] **48** `feat(web): add min-risk filter for zones`
- [ ] **49** `test(web): add zone layer tests`
- [ ] **50** `docs(web): document zones UI`
- [ ] **51** `test(web): add zone selection integration test`
- [ ] **52** `style(web): polish zone visuals`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/14-work` into `main` with `--no-ff`.
