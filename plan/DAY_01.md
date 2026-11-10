# Day 1 — Repo bootstrap, tooling, IDE context, CI skeleton

Goal: A clean, linted, CI-ready monorepo (Python backend + React web) with all IDE context docs in place.

**Branch:** `day/01-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. Repository bootstrap

- [ ] **01** `chore: initialize git repository on main branch`
- [ ] **02** `chore: add .gitignore for python node data and model artifacts`
- [ ] **03** `docs: add MIT LICENSE`
- [ ] **04** `docs: add README skeleton with project title and badges placeholder`
- [ ] **05** `chore: add .editorconfig with utf-8 lf and indent rules`
- [ ] **06** `chore: add .gitattributes with LFS rules for tif h5 pt onnx`
- [ ] **07** `chore: create top-level directory layout (src web configs docs plan scripts tests)`
- [ ] **08** `chore: add .gitkeep files to empty data directories`

## B. IDE context and docs

- [ ] **09** `docs: add AGENTS.md master IDE instructions`
- [ ] **10** `docs: add CLAUDE.md pointer for Claude Code`
- [ ] **11** `docs: add .cursorrules for Cursor`
- [ ] **12** `docs: add .github/copilot-instructions.md`
- [ ] **13** `docs: add docs/01_PROJECT_SPEC.md from Infotact document`
- [ ] **14** `docs: add docs/02_ARCHITECTURE.md with mermaid diagram`
- [ ] **15** `docs: add docs/05_DATA_SPEC.md`
- [ ] **16** `docs: add docs/06_ML_SPEC.md`

## C. Python tooling

- [ ] **17** `build: add pyproject.toml with project metadata and src layout`
- [ ] **18** `build: pin python 3.11 in .python-version`
- [ ] **19** `build: declare core runtime deps numpy scipy scikit-learn pyyaml`
- [ ] **20** `build: declare geospatial deps rasterio h5py pyproj shapely`
- [ ] **21** `build: declare deep learning dep torch`
- [ ] **22** `build: declare dev deps pytest pytest-cov hypothesis ruff mypy`
- [ ] **23** `build: generate requirements.txt for runtime deps`
- [ ] **24** `build: generate requirements-dev.txt for dev deps`
- [ ] **25** `chore: configure ruff lint and format rules in pyproject`
- [ ] **26** `chore: configure mypy strict settings in pyproject`
- [ ] **27** `test: configure pytest options markers and coverage in pyproject`
- [ ] **28** `chore: add Makefile with install lint format typecheck test targets`

## D. Backend package skeleton

- [ ] **29** `feat: create src/terraspectra package with version string`
- [ ] **30** `feat: add core subpackage`
- [ ] **31** `feat: add synth subpackage`
- [ ] **32** `feat: add geo subpackage`
- [ ] **33** `feat: add data subpackage with readers and preprocess modules`
- [ ] **34** `feat: add models subpackage`
- [ ] **35** `feat: add training and inference subpackages`
- [ ] **36** `feat: add api subpackage`

## E. Frontend skeleton

- [ ] **37** `feat(web): scaffold Vite React TypeScript app`
- [ ] **38** `chore(web): add package.json scripts dev build test lint`
- [ ] **39** `chore(web): enable strict TypeScript options in tsconfig`
- [ ] **40** `chore(web): add eslint config for react and typescript`
- [ ] **41** `chore(web): add prettier config`
- [ ] **42** `chore(web): add .env.example with VITE_MAPBOX_TOKEN and API base URL`
- [ ] **43** `chore(web): add vitest and testing-library config`
- [ ] **44** `test(web): add App smoke test`

## F. DevEx and CI

- [ ] **45** `chore: add pre-commit config with ruff and end-of-file fixer`
- [ ] **46** `chore: add pre-commit hooks for trailing whitespace and yaml check`
- [ ] **47** `ci: add GitHub Actions workflow for python lint and typecheck`
- [ ] **48** `ci: add GitHub Actions workflow for python tests with coverage`
- [ ] **49** `ci: add GitHub Actions workflow for web lint and test`
- [ ] **50** `docs: add CONTRIBUTING with commit convention and daily protocol`
- [ ] **51** `chore: add commit message template .gitmessage`
- [ ] **52** `chore: add scripts/check_commits.sh daily commit counter`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/01-work` into `main` with `--no-ff`.
