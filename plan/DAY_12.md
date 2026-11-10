# Day 12 — Hybrid 3D-CNN + ViT assembly, multi-task heads, hybrid training; acreage-at-risk charts

Goal: HybridCNNViT trains end-to-end; acreage-at-risk visualisations with thresholds.

**Branch:** `day/12-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Hybrid model

- [ ] **01** `feat(models): add HybridConfig dataclass`
- [ ] **02** `feat(models): add HybridCNNViT class`
- [ ] **03** `feat(models): wire 3D-CNN stem into model`
- [ ] **04** `feat(models): wire feature adapter`
- [ ] **05** `feat(models): wire SpectralViT encoder`
- [ ] **06** `feat(models): add fusion of CNN pooled and CLS features`
- [ ] **07** `feat(models): add output dict with logits severity forecast`
- [ ] **08** `feat(models): add auxiliary outputs for debugging`
- [ ] **09** `feat(models): add freeze CNN option`
- [ ] **10** `feat(models): add load pretrained CNN weights`
- [ ] **11** `feat(models): add parameter count report`
- [ ] **12** `feat(models): register hybrid model`
- [ ] **13** `test(models): add hybrid forward shape test`
- [ ] **14** `test(models): add hybrid backward test`

## B. Training changes

- [ ] **15** `feat(configs): add hybrid train config`
- [ ] **16** `feat(training): add two-stage training schedule`
- [ ] **17** `feat(training): add layer-wise LR decay`
- [ ] **18** `feat(training): extend warmup for transformer`
- [ ] **19** `feat(training): ensure mixed precision for hybrid`
- [ ] **20** `feat(training): log attention statistics`
- [ ] **21** `fix(training): keep checkpoint compatibility across models`
- [ ] **22** `feat(training): add train_hybrid make target`
- [ ] **23** `test(training): add hybrid smoke training test`
- [ ] **24** `docs: document hybrid training procedure`

## C. Multi-task heads

- [ ] **25** `feat(models): add state classification head`
- [ ] **26** `feat(models): add severity regression head`
- [ ] **27** `feat(models): add forecast days-to-symptoms head`
- [ ] **28** `feat(training): add multi-task loss`
- [ ] **29** `feat(training): add configurable loss weights`
- [ ] **30** `feat(training): add uncertainty-weighted loss option`
- [ ] **31** `feat(training): add regression metrics MAE RMSE`
- [ ] **32** `test(training): add multi-task loss tests`

## D. Performance

- [ ] **33** `perf(models): add torch.compile option`
- [ ] **34** `perf(models): benchmark hybrid throughput`
- [ ] **35** `perf(models): profile hybrid memory`
- [ ] **36** `docs: add hybrid performance report`

## E. Frontend acreage charts

- [ ] **37** `feat(web): add AcreageAtRisk chart`
- [ ] **38** `feat(web): add donut chart variant`
- [ ] **39** `feat(web): add bar chart variant`
- [ ] **40** `feat(web): add risk threshold slider`
- [ ] **41** `feat(web): add threshold state in store`
- [ ] **42** `feat(web): compute acres from cells and threshold`
- [ ] **43** `feat(web): add acre value formatting`
- [ ] **44** `feat(web): add chart tooltips`
- [ ] **45** `feat(web): add chart legend`
- [ ] **46** `feat(web): add chart animations`
- [ ] **47** `feat(web): add CSV export of acreage`
- [ ] **48** `test(web): add AcreageAtRisk tests`
- [ ] **49** `feat(web): add chart accessibility labels`
- [ ] **50** `chore(web): update mock analytics data`
- [ ] **51** `docs(web): document charts`
- [ ] **52** `test(web): add analytics integration test`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/12-work` into `main` with `--no-ff`.
