# Day 15 — Evaluation, calibration, robustness, export; analytics polish (End of Week 3, tag v0.2.0)

Goal: Quantified performance incl. lead time; calibrated uncertainty; polished analytics UX.

**Branch:** `day/15-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Evaluation

- [ ] **01** `feat(eval): add lead-time analysis`
- [ ] **02** `feat(eval): add per-horizon metrics`
- [ ] **03** `feat(eval): add ROC-AUC`
- [ ] **04** `feat(eval): add PR-AUC`
- [ ] **05** `feat(eval): add spatial block metrics`
- [ ] **06** `feat(eval): add zone-level precision and recall`
- [ ] **07** `feat(eval): add false alarm rate`
- [ ] **08** `feat(eval): add cost-benefit pesticide simulation`
- [ ] **09** `feat(eval): add report generator`
- [ ] **10** `feat(eval): add evaluation plots`
- [ ] **11** `feat(eval): save evaluation JSON`
- [ ] **12** `test(eval): add evaluation tests`

## B. Calibration

- [ ] **13** `feat(calibration): add temperature scaling`
- [ ] **14** `feat(calibration): add reliability diagram`
- [ ] **15** `feat(calibration): add ECE metric`
- [ ] **16** `feat(calibration): add MC-dropout inference`
- [ ] **17** `feat(calibration): add uncertainty map output`
- [ ] **18** `feat(calibration): add confidence thresholds`
- [ ] **19** `test(calibration): add calibration tests`
- [ ] **20** `docs: document calibration`

## C. Robustness

- [ ] **21** `feat(eval): add noise robustness test`
- [ ] **22** `feat(eval): add band-drop robustness test`
- [ ] **23** `feat(eval): add cloud robustness test`
- [ ] **24** `feat(eval): add distribution shift test`
- [ ] **25** `feat(eval): add seed variance study`
- [ ] **26** `feat(eval): add robustness stats`
- [ ] **27** `docs: add robustness report`
- [ ] **28** `test(eval): add robustness test harness`

## D. Model export

- [ ] **29** `feat(export): save state_dict with config`
- [ ] **30** `feat(export): attempt TorchScript export`
- [ ] **31** `feat(export): attempt ONNX export`
- [ ] **32** `docs: finalise model card`
- [ ] **33** `feat(export): add model version file`
- [ ] **34** `test(export): add export load tests`

## E. Frontend polish

- [ ] **35** `feat(web): add analytics summary header`
- [ ] **36** `feat(web): add total acres KPI`
- [ ] **37** `feat(web): add at-risk acres KPI`
- [ ] **38** `feat(web): add trend delta indicator`
- [ ] **39** `feat(web): add uncertainty overlay toggle`
- [ ] **40** `feat(web): show confidence in details`
- [ ] **41** `feat(web): add export map as PNG`
- [ ] **42** `feat(web): add export analytics CSV`
- [ ] **43** `style(web): add print stylesheet`
- [ ] **44** `feat(web): add dark mode`
- [ ] **45** `feat(web): add theme toggle`
- [ ] **46** `feat(web): persist sidebar state`
- [ ] **47** `feat(web): add keyboard navigation`
- [ ] **48** `style(web): polish tooltips`
- [ ] **49** `test(web): add KPI tests`
- [ ] **50** `chore(web): run axe accessibility audit`
- [ ] **51** `perf(web): reduce rerenders in analytics`
- [ ] **52** `chore: tag v0.2.0 and update changelog`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/15-work` into `main` with `--no-ff`.
