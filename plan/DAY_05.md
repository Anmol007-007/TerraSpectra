# Day 5 — Cleaning, normalisation, spectral indices, PCA; layer panel and 3D terrain (End of Week 1)

Goal: Preprocessing pipeline with streaming stats and IncrementalPCA on 200+ bands; polished layer controls.

**Branch:** `day/05-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Cleaning

- [ ] **01** `feat(preprocess): add bad band dropping with valid mask`
- [ ] **02** `feat(preprocess): add water-vapour band masking`
- [ ] **03** `feat(preprocess): add NaN and inf handling`
- [ ] **04** `feat(preprocess): add spectral spike removal`
- [ ] **05** `feat(preprocess): add Savitzky-Golay smoothing`
- [ ] **06** `feat(preprocess): add cloud and shadow masking`
- [ ] **07** `feat(preprocess): add nodata interpolation along spectrum`
- [ ] **08** `feat(preprocess): add reflectance clipping and scaling`
- [ ] **09** `feat(preprocess): add QA report dictionary`
- [ ] **10** `test(preprocess): add cleaning tests`

## B. Normalisation

- [ ] **11** `feat(preprocess): add streaming Welford per-band statistics`
- [ ] **12** `feat(preprocess): add stats save and load npz`
- [ ] **13** `feat(preprocess): add standardisation using stored stats`
- [ ] **14** `feat(preprocess): add min-max normalisation option`
- [ ] **15** `feat(preprocess): add continuum removal`
- [ ] **16** `feat(preprocess): add SNV normalisation`
- [ ] **17** `feat(preprocess): add BandStats dataclass`
- [ ] **18** `test(preprocess): add normalisation tests`

## C. Spectral indices

- [ ] **19** `feat(preprocess): add NDVI`
- [ ] **20** `feat(preprocess): add PRI`
- [ ] **21** `feat(preprocess): add NDWI`
- [ ] **22** `feat(preprocess): add red-edge position`
- [ ] **23** `feat(preprocess): add CIre`
- [ ] **24** `feat(preprocess): add MCARI`
- [ ] **25** `feat(preprocess): add index stack builder`
- [ ] **26** `test(preprocess): add index value tests on synthetic spectra`

## D. PCA

- [ ] **27** `feat(preprocess): add IncrementalPCA fit over windows`
- [ ] **28** `feat(preprocess): add n_components config`
- [ ] **29** `feat(preprocess): add explained variance report`
- [ ] **30** `feat(preprocess): add PCA save and load with joblib`
- [ ] **31** `feat(preprocess): add window transform to PCA space`
- [ ] **32** `feat(preprocess): add optional whitening`
- [ ] **33** `feat(preprocess): add scree plot figure`
- [ ] **34** `feat(preprocess): add reconstruction error metric`
- [ ] **35** `test(preprocess): add PCA tests`
- [ ] **36** `feat(cli): add fit-pca command`

## E. Preprocess pipeline

- [ ] **37** `feat(preprocess): add Preprocessor class composing steps`
- [ ] **38** `feat(preprocess): add pipeline config in data.yaml`
- [ ] **39** `feat(preprocess): add cached processed output as npy`
- [ ] **40** `feat(cli): add preprocess command`
- [ ] **41** `build: add make preprocess target`
- [ ] **42** `test(preprocess): add end-to-end preprocess integration test`

## F. Frontend layer controls

- [ ] **43** `feat(web): add LayerPanel component`
- [ ] **44** `feat(web): add toggle switch component`
- [ ] **45** `feat(web): add opacity slider component`
- [ ] **46** `feat(web): add 3D terrain toggle`
- [ ] **47** `feat(web): add pitch and bearing controls`
- [ ] **48** `feat(web): add reset view button`
- [ ] **49** `feat(web): add layer slice persistence in store`
- [ ] **50** `feat(web): add keyboard shortcuts for layers`
- [ ] **51** `test(web): add LayerPanel tests`
- [ ] **52** `docs(web): add week 1 UI screenshots notes`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/05-work` into `main` with `--no-ff`.
