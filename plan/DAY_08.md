# Day 8 — Training script, imbalance, evaluation, experiment tracking; tooltips, API mock layer

Goal: Reproducible training run + evaluation pipeline producing georeferenced predictions; interactive inspector UI.

**Branch:** `day/08-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Training script

- [ ] **01** `feat(training): add train.py CLI entrypoint`
- [ ] **02** `feat(training): add yaml config overrides via CLI`
- [ ] **03** `feat(training): add seeding at train start`
- [ ] **04** `feat(training): add logging of epoch metrics`
- [ ] **05** `feat(training): add tensorboard writer`
- [ ] **06** `feat(training): add CSV metrics logger`
- [ ] **07** `feat(training): add run directory creation`
- [ ] **08** `feat(training): snapshot config into run dir`
- [ ] **09** `feat(training): capture git hash in run metadata`
- [ ] **10** `build: add make train target`

## B. Imbalance and tuning

- [ ] **11** `feat(training): add automatic class weights from train split`
- [ ] **12** `feat(training): add WeightedRandomSampler option`
- [ ] **13** `feat(training): add focal gamma config`
- [ ] **14** `feat(training): add LR range finder`
- [ ] **15** `feat(training): add label smoothing`
- [ ] **16** `feat(training): add EMA of weights`
- [ ] **17** `test(training): add EMA and sampler tests`
- [ ] **18** `docs: document imbalance handling`

## C. Evaluation

- [ ] **19** `feat(training): add evaluate.py CLI`
- [ ] **20** `feat(training): add windowed full-scene prediction`
- [ ] **21** `feat(training): add stitched prediction raster`
- [ ] **22** `feat(training): write prediction GeoTIFF with georeference`
- [ ] **23** `feat(training): add confusion matrix plot`
- [ ] **24** `feat(training): add PR curve plot`
- [ ] **25** `feat(training): add per-class spectral signature plot`
- [ ] **26** `feat(training): save metrics JSON`
- [ ] **27** `feat(training): add reports directory writer`
- [ ] **28** `test(training): add evaluation smoke test`

## D. Experiment tracking

- [ ] **29** `docs: add experiments.md template`
- [ ] **30** `feat(training): add results table generator`
- [ ] **31** `feat(training): add checkpoint registry`
- [ ] **32** `feat(training): add best-model symlink`
- [ ] **33** `docs: add model card template`
- [ ] **34** `test(training): add registry tests`

## E. Frontend data layer and inspector

- [ ] **35** `feat(web): add fetch wrapper with timeout and retry`
- [ ] **36** `feat(web): add MSW mock adapter`
- [ ] **37** `feat(web): add react-query setup for API`
- [ ] **38** `feat(web): add useScene hook`
- [ ] **39** `feat(web): add usePrediction hook`
- [ ] **40** `feat(web): add loading states`
- [ ] **41** `feat(web): add ErrorBoundary component`
- [ ] **42** `feat(web): add Tooltip component`
- [ ] **43** `feat(web): add tooltip content for risk severity state`
- [ ] **44** `feat(web): add PixelInspector panel`
- [ ] **45** `feat(web): add spectral signature mini chart`
- [ ] **46** `feat(web): add selected pixel state`
- [ ] **47** `feat(web): add zoom to selection action`
- [ ] **48** `feat(web): add skeleton loaders`
- [ ] **49** `feat(web): add toast notifications`
- [ ] **50** `test(web): add Tooltip tests`
- [ ] **51** `test(web): add PixelInspector tests`
- [ ] **52** `docs(web): document data layer`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/08-work` into `main` with `--no-ff`.
