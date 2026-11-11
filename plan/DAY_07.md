# Day 7 — 3D-CNN blocks, model v1, losses, metrics, Trainer; pixel grid overlay

Goal: Working 3D-CNN classifier with full training loop; interactive pixel grid on the map.

**Branch:** `day/07-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. 3D building blocks

- [ ] **01** `feat(models): add Conv3DBlock conv bn gelu`
- [ ] **02** `feat(models): add ResidualBlock3D`
- [ ] **03** `feat(models): add SE spectral attention block`
- [ ] **04** `feat(models): add Dropout3d wrapper`
- [ ] **05** `feat(models): add stem block`
- [ ] **06** `feat(models): add spectral pooling layer`
- [ ] **07** `feat(models): add global pooling head`
- [ ] **08** `feat(models): add weight initialisation helper`
- [ ] **09** `test(models): add block output shape tests`
- [ ] **10** `test(models): add gradient flow tests`

## B. CNN3D v1

- [ ] **11** `feat(models): add CNN3DConfig dataclass`
- [ ] **12** `feat(models): add CNN3DClassifier class`
- [ ] **13** `feat(models): implement forward pass`
- [ ] **14** `feat(models): add classification head`
- [ ] **15** `feat(models): add parameter count utility`
- [ ] **16** `feat(models): add model summary utility`
- [ ] **17** `feat(models): add model registry`
- [ ] **18** `test(models): add forward and backward smoke tests`

## C. Losses and metrics

- [ ] **19** `feat(training): add cross entropy with class weights`
- [ ] **20** `feat(training): add focal loss`
- [ ] **21** `feat(training): add dice loss`
- [ ] **22** `feat(training): add class weight computation`
- [ ] **23** `feat(training): add confusion matrix metric`
- [ ] **24** `feat(training): add precision recall F1`
- [ ] **25** `feat(training): add macro-F1 and per-class F1`
- [ ] **26** `feat(training): add mIoU`
- [ ] **27** `feat(training): add MetricCollection`
- [ ] **28** `test(training): add loss and metric tests`

## D. Trainer

- [ ] **29** `feat(training): add Trainer class skeleton`
- [ ] **30** `feat(training): add train epoch loop`
- [ ] **31** `feat(training): add validation loop`
- [ ] **32** `feat(training): add AdamW optimizer factory`
- [ ] **33** `feat(training): add cosine scheduler with warmup`
- [ ] **34** `feat(training): add AMP support`
- [ ] **35** `feat(training): add gradient clipping`
- [ ] **36** `feat(training): add checkpoint saving`
- [ ] **37** `feat(training): add resume from checkpoint`
- [ ] **38** `feat(training): add early stopping callback`
- [ ] **39** `feat(training): add callback interface`
- [ ] **40** `test(training): add overfit-tiny-batch test`

## E. Frontend pixel grid

- [ ] **41** `feat(web): add PixelGridLayer`
- [ ] **42** `feat(web): add geo to cell index conversion`
- [ ] **43** `feat(web): set cell size from 30m GSD`
- [ ] **44** `feat(web): colour cells by probability`
- [ ] **45** `feat(web): add optional elevation extrusion`
- [ ] **46** `feat(web): enable picking on cells`
- [ ] **47** `feat(web): add hover state in store`
- [ ] **48** `feat(web): add highlight for selected cell`
- [ ] **49** `feat(web): bind legend to layer range`
- [ ] **50** `feat(web): wire mock data to grid layer`
- [ ] **51** `test(web): add grid layer unit tests`
- [ ] **52** `feat(web): add demo page for grid layer`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/07-work` into `main` with `--no-ff`.
