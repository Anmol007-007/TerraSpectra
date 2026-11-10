# Day 13 — Ablations, attention analysis, explainability; chemical anomalies panel

Goal: Evidence that ViT improves accuracy via cross-spectrum correlations; anomalies visualised.

**Branch:** `day/13-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Ablation study

- [ ] **01** `feat(experiments): add ablation config schema`
- [ ] **02** `feat(experiments): add cnn-only run config`
- [ ] **03** `feat(experiments): add vit-only run config`
- [ ] **04** `feat(experiments): add hybrid run config`
- [ ] **05** `feat(experiments): add PCA components sweep 16 32 64`
- [ ] **06** `feat(experiments): add patch size sweep 7 11 15`
- [ ] **07** `feat(experiments): add band group size sweep`
- [ ] **08** `feat(experiments): add ablation runner script`
- [ ] **09** `feat(experiments): add results aggregation`
- [ ] **10** `feat(experiments): add ablation plot`
- [ ] **11** `docs: generate ablation table markdown`
- [ ] **12** `docs: write ablation conclusions`

## B. Attention analysis

- [ ] **13** `feat(explain): add attention extraction hooks`
- [ ] **14** `feat(explain): add attention rollout`
- [ ] **15** `feat(explain): add per-band importance`
- [ ] **16** `feat(explain): add wavelength importance plot`
- [ ] **17** `feat(explain): save importance to JSON`
- [ ] **18** `feat(explain): add spectral attention heatmap`
- [ ] **19** `feat(explain): add top-k important bands list`
- [ ] **20** `test(explain): add attention rollout tests`
- [ ] **21** `feat(scripts): add analyse_attention.py`
- [ ] **22** `docs: document attention findings`

## C. Training improvements

- [ ] **23** `feat(training): add cosine restarts scheduler`
- [ ] **24** `feat(training): add stochastic weight averaging`
- [ ] **25** `feat(training): add mixup in training loop`
- [ ] **26** `feat(training): add label-noise robustness option`
- [ ] **27** `feat(training): add hard negative mining`
- [ ] **28** `feat(training): add multi-seed averaging script`
- [ ] **29** `feat(training): add checkpoint averaging`
- [ ] **30** `test(training): add SWA and averaging tests`

## D. Explainability

- [ ] **31** `feat(explain): add 3D Grad-CAM`
- [ ] **32** `feat(explain): add integrated gradients option`
- [ ] **33** `feat(explain): save saliency maps`
- [ ] **34** `test(explain): add Grad-CAM tests`

## E. Frontend anomalies

- [ ] **35** `feat(web): add ChemicalAnomaly type`
- [ ] **36** `feat(web): add anomalies mock data`
- [ ] **37** `feat(web): add AnomalyList component`
- [ ] **38** `feat(web): add AnomalyChart component`
- [ ] **39** `feat(web): add wavelength bar chart`
- [ ] **40** `feat(web): add severity badges`
- [ ] **41** `feat(web): add sort and filter for anomalies`
- [ ] **42** `feat(web): link anomaly click to map highlight`
- [ ] **43** `feat(web): highlight affected band range`
- [ ] **44** `feat(web): add band info tooltip`
- [ ] **45** `feat(web): add chlorophyll indicator`
- [ ] **46** `feat(web): add water stress indicator`
- [ ] **47** `feat(web): add PRI indicator`
- [ ] **48** `feat(web): add anomalies legend`
- [ ] **49** `test(web): add anomaly component tests`
- [ ] **50** `docs(web): document anomalies UI`
- [ ] **51** `test(web): add anomalies integration test`
- [ ] **52** `style(web): polish anomalies spacing`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/13-work` into `main` with `--no-ff`.
