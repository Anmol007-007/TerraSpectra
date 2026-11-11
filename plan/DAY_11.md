# Day 11 — Vision Transformer components; analytics panel scaffold (Week 3 start)

Goal: Spectral tokenisation, attention, encoder, SpectralViT; analytics sidebar scaffold with acreage utilities.

**Branch:** `day/11-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Tokenisation

- [ ] **01** `feat(models): add spectral group tokenizer`
- [ ] **02** `feat(models): add band grouping config`
- [ ] **03** `feat(models): add spatial-spectral patch embedding`
- [ ] **04** `feat(models): add linear projection to d_model`
- [ ] **05** `feat(models): add learnable CLS token`
- [ ] **06** `feat(models): add learned positional embedding`
- [ ] **07** `feat(models): add sinusoidal positional option`
- [ ] **08** `feat(models): add wavelength-aware positional encoding`
- [ ] **09** `feat(models): add token dropout`
- [ ] **10** `test(models): add tokenizer shape tests`

## B. Attention and encoder

- [ ] **11** `feat(models): add multi-head self-attention`
- [ ] **12** `feat(models): use scaled_dot_product_attention`
- [ ] **13** `feat(models): add attention dropout`
- [ ] **14** `feat(models): add MLP block`
- [ ] **15** `feat(models): add GELU and LayerNorm pre-norm`
- [ ] **16** `feat(models): add stochastic depth`
- [ ] **17** `feat(models): add TransformerEncoderBlock`
- [ ] **18** `feat(models): add encoder stack`
- [ ] **19** `feat(models): add option to return attention weights`
- [ ] **20** `test(models): add attention output shape tests`
- [ ] **21** `test(models): add attention weights sum-to-one test`
- [ ] **22** `test(models): add encoder gradient flow test`

## C. SpectralViT

- [ ] **23** `feat(models): add ViTConfig dataclass`
- [ ] **24** `feat(models): add SpectralViT class`
- [ ] **25** `feat(models): implement forward with CLS pooling`
- [ ] **26** `feat(models): add mean pooling option`
- [ ] **27** `feat(models): add trunc-normal init`
- [ ] **28** `feat(models): add parameter count helper`
- [ ] **29** `feat(models): register SpectralViT`
- [ ] **30** `test(models): add SpectralViT forward and backward test`

## D. Integration prep

- [ ] **31** `feat(models): add CNN-to-token feature adapter`
- [ ] **32** `feat(models): add reshape and group ops`
- [ ] **33** `feat(models): add dimension validation errors`
- [ ] **34** `test(models): add adapter tests`
- [ ] **35** `feat(configs): merge hybrid settings into model.yaml`
- [ ] **36** `docs: document token layout and shapes`

## E. Frontend analytics scaffold

- [ ] **37** `feat(web): add AnalyticsPanel container`
- [ ] **38** `feat(web): add collapsible right sidebar`
- [ ] **39** `feat(web): add tabs component`
- [ ] **40** `feat(web): add StatCard component`
- [ ] **41** `feat(web): add stat skeleton state`
- [ ] **42** `feat(web): add AnalyticsSummary types`
- [ ] **43** `feat(web): add mock analytics JSON`
- [ ] **44** `feat(web): add analytics selector hooks`
- [ ] **45** `feat(web): add cells to acres computation`
- [ ] **46** `test(web): add acreage computation tests`
- [ ] **47** `feat(web): add recharts wrapper component`
- [ ] **48** `feat(web): add chart theme tokens`
- [ ] **49** `feat(web): make charts responsive`
- [ ] **50** `feat(web): add empty state component`
- [ ] **51** `test(web): add AnalyticsPanel tests`
- [ ] **52** `docs(web): document analytics components`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/11-work` into `main` with `--no-ff`.
