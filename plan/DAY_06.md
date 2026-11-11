# Day 6 — Patches, Dataset, splits, augmentation, DataLoader; heatmap types and rendering (Week 2 start)

Goal: Memory-efficient PyTorch dataset with leakage-free splits; heatmap data contract and layers from mock JSON.

**Branch:** `day/06-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: Complete all steps for the day, run `make lint` + related tests, delete unnecessary files, then commit everything at the end of the day all at once and push to main.


## A. Patch extraction

- [ ] **01** `feat(data): add PatchSpec dataclass`
- [ ] **02** `feat(data): add centre-pixel patch extractor`
- [ ] **03** `feat(data): add reflect padding at borders`
- [ ] **04** `feat(data): add stride sampler over valid pixels`
- [ ] **05** `feat(data): add valid-mask filtering`
- [ ] **06** `feat(data): add class-balanced sample index builder`
- [ ] **07** `feat(data): add patch index builder`
- [ ] **08** `feat(data): save patch index as parquet or npz`
- [ ] **09** `test(data): add patch shape tests`
- [ ] **10** `test(data): add border patch tests`

## B. Dataset

- [ ] **11** `feat(data): add HyperspectralPatchDataset`
- [ ] **12** `feat(data): add lazy windowed reads in dataset`
- [ ] **13** `feat(data): return tensor shape 1 D H W`
- [ ] **14** `feat(data): return state label`
- [ ] **15** `feat(data): return severity and days-to-symptoms targets`
- [ ] **16** `feat(data): return metadata dict`
- [ ] **17** `feat(data): add worker_init_fn for seeds`
- [ ] **18** `feat(data): add custom collate function`
- [ ] **19** `test(data): add dataset item tests`
- [ ] **20** `perf(data): add dataset throughput benchmark script`

## C. Splits

- [ ] **21** `feat(data): add spatial block splitter`
- [ ] **22** `feat(data): add buffer to avoid leakage`
- [ ] **23** `feat(data): add temporal splitter`
- [ ] **24** `feat(data): add stratified option`
- [ ] **25** `feat(data): persist splits.json manifest`
- [ ] **26** `feat(data): add seeded split reproducibility`
- [ ] **27** `test(data): assert no overlap between splits`
- [ ] **28** `docs: document split strategy`

## D. Augmentation

- [ ] **29** `feat(augment): add spectral jitter`
- [ ] **30** `feat(augment): add gaussian noise`
- [ ] **31** `feat(augment): add band dropout`
- [ ] **32** `feat(augment): add spatial flips and 90-degree rotations`
- [ ] **33** `feat(augment): add spectral mixup`
- [ ] **34** `feat(augment): add brightness scaling`
- [ ] **35** `feat(augment): add Compose wrapper`
- [ ] **36** `test(augment): add augmentation tests`

## E. DataLoader

- [ ] **37** `feat(data): add build_dataloader factory`
- [ ] **38** `feat(data): add pin_memory and prefetch options`
- [ ] **39** `feat(data): add persistent workers option`
- [ ] **40** `test(data): add DataLoader batch shape test`

## F. Frontend heatmap contract

- [ ] **41** `feat(web): add heatmap TypeScript types`
- [ ] **42** `feat(web): add mock result JSON for farm_001`
- [ ] **43** `feat(web): add zod schema for result payload`
- [ ] **44** `feat(web): add parseResult utility`
- [ ] **45** `feat(web): add grid to cell polygons util`
- [ ] **46** `feat(web): add heatmap GridCellLayer`
- [ ] **47** `feat(web): add risk color scale utility`
- [ ] **48** `feat(web): add risk to RGBA mapping`
- [ ] **49** `feat(web): add Legend component`
- [ ] **50** `feat(web): add heatmap opacity binding`
- [ ] **51** `test(web): add color scale tests`
- [ ] **52** `chore(web): add script to generate mock result JSON`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/06-work` into `main` with `--no-ff`.
