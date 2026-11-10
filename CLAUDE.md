# AGENTS.md — TerraSpectra (read this first, every session)

You are the AI pair-programmer for **TerraSpectra: Hyperspectral Crop Disease Forecasting**
(Infotact Solutions Project Document, Adv. Data Science & ML Engineering Vol. II, Project 1).

## 1. One-paragraph mission
Ingest hyperspectral satellite data cubes (200+ bands), run a **3D-CNN + Vision Transformer hybrid**
(PyTorch) that detects subtle chlorophyll/chemical changes, and **forecast fungal blight ~3 weeks
(21 days) before visible symptoms**. Serve it through a **FastAPI** inference API that tiles huge
rasters on GPU, and show results in a **React + Deck.gl + Mapbox** 3D GIS dashboard with a red
5-acre risk zone on a 1,000-acre farm, analytics sidebar, and a historical timeline slider.

## 2. The four Key Modules (all mandatory)
| # | Module | Stack | Lives in |
|---|--------|-------|----------|
| 1 | Geospatial Data Pipeline | Python, Rasterio, GDAL, h5py, scikit-learn (PCA) | `src/terraspectra/data/` |
| 2 | 3D-CNN & ViT Hybrid Model | PyTorch | `src/terraspectra/models/`, `training/` |
| 3 | Inference API with tiling | FastAPI, uvicorn, pydantic v2 | `src/terraspectra/api/` |
| 4 | GIS Dashboard | React 18, TypeScript, Vite, Deck.gl 9, Mapbox GL | `web/` |

## 3. How to work (strict protocol)
1. Open `plan/DAY_XX.md` for the current day. Each has **exactly 52 numbered commit steps**.
2. Do the steps **in order**. One step = one small, real, atomic change = **one git commit**.
3. After each step: run `make lint` (fast) and the relevant tests, then commit using the
   message given in the step (Conventional Commits). Never batch several steps into one commit.
4. Never create empty commits or whitespace-only padding commits. If a step is already
   satisfied, improve it meaningfully (docstring, test, type hint) and commit that instead.
5. At end of day run `scripts/check_commits.sh` — it must print `>= 52`.
6. Mid-Project Review = Day 10. Final Review = Day 20 (see `plan/DAY_10.md`, `plan/DAY_20.md`).

## 4. Read these docs before coding the related area
- `docs/01_PROJECT_SPEC.md` — requirements, use case, success criteria (from the PDF)
- `docs/02_ARCHITECTURE.md` — components, data flow, diagrams
- `docs/03_REPO_STRUCTURE.md` — exact file tree; put files only where listed
- `docs/04_TECH_STACK_SETUP.md` — versions, install, env vars, commands
- `docs/05_DATA_SPEC.md` — cube shapes, bands, CRS, synthetic data, labels
- `docs/06_ML_SPEC.md` — model, tensor shapes, losses, metrics, training
- `docs/07_API_SPEC.md` — endpoints, JSON schemas, tiling algorithm
- `docs/08_FRONTEND_SPEC.md` — components, layers, state, UX
- `docs/09_GIT_COMMIT_PROTOCOL.md` — commit rules, branches, tags
- `docs/10_TESTING_QA.md` — test strategy, coverage gates, definition of done

## 5. Coding standards (non-negotiable)
- Python 3.11, full type hints, `mypy --strict` on `src/`, `ruff` for lint+format, docstrings (Google style).
- No hard-coded paths/magic numbers: use `configs/*.yaml` + `terraspectra.core.settings`.
- Never load a whole cube into RAM when a windowed read works (Rasterio `Window`, HDF5 chunks).
- Seeds via `seed_everything`; every experiment logs config + git hash.
- Frontend: TypeScript `strict`, no `any`, functional components + hooks, Zustand for state,
  zod for validating API payloads, Vitest + Testing Library, Playwright for e2e.
- All geo math goes through the tested helpers (`geo/transforms.py`, `web/src/utils/geo.ts`).
- Units: reflectance 0–1 float32, wavelengths in nm, area in acres (1 acre = 4046.8564 m²).
- Public functions need a test. Bug fix = failing test first.

## 6. Domain facts to keep in mind
- Hyperion-like sensor: 30 m GSD → 1 pixel = 900 m² ≈ 0.2224 acre. 5 acres ≈ 22–23 pixels.
  1,000 acres ≈ 4,497 pixels ≈ 67×67 px.
- Bands: 224 synthetic bands, 400–2500 nm; drop water-vapour bands (~1350–1460, 1790–1960, >2400 nm).
- Pre-visual stress signals: red-edge shift (680–750 nm), PRI (531/570), chlorophyll decline,
  leaf water content (970/1200/1450/1940 nm), SWIR dry-matter changes.
- Classes: 0 healthy, 1 pre-symptomatic stress, 2 visibly diseased. Forecast horizon: 21 days.
- Real data (NASA Hyperion / ESA) is optional; **synthetic data generator is the default** and must work offline.

## 7. Definition of Done (per day)
52 commits, CI green, tests added for new code, docs updated for new public behavior,
no TODO left without an issue note in `docs/KNOWN_ISSUES.md`.

## 8. Do NOT
- Commit large rasters/checkpoints (use Git LFS or `data/` + `.gitignore`).
- Commit secrets (Mapbox token goes in `web/.env.local`).
- Change the public API contract in `docs/07_API_SPEC.md` without updating the doc and tests.
- Skip the memory-safety requirement for the Mid-Project "Extraction Audit".

<!-- Verified and synchronized for Claude Code -->
