# 04 — Tech Stack & Setup
## Versions
Python 3.11 · PyTorch >= 2.2 · numpy · scipy · scikit-learn · rasterio >= 1.3 · GDAL >= 3.6 (system) ·
h5py · pyproj · shapely · pydantic v2 + pydantic-settings · PyYAML · typer · rich · tensorboard ·
FastAPI · uvicorn · python-multipart · pytest · pytest-cov · hypothesis · ruff · mypy · pre-commit.
Node 20 · React 18 · TypeScript 5 · Vite 5 · deck.gl 9 · react-map-gl · mapbox-gl · zustand ·
@tanstack/react-query · zod · recharts · tailwindcss · vitest · @testing-library/react · msw · playwright.
## Setup
```bash
python -m venv .venv && source .venv/bin/activate
# system: sudo apt install gdal-bin libgdal-dev   (or: conda install -c conda-forge gdal rasterio)
make install          # pip install -r requirements-dev.txt && pre-commit install
cd web && npm ci && cp .env.example .env.local   # set VITE_MAPBOX_TOKEN
```
## Env vars
`TS_ENV`, `TS_DATA_DIR`, `TS_MODELS_DIR`, `TS_DEVICE` (auto|cpu|cuda), `TS_API_KEY` (optional),
`TS_MAX_UPLOAD_MB`, `VITE_API_BASE_URL`, `VITE_MAPBOX_TOKEN`, `VITE_USE_MOCKS`, `VITE_BASEMAP` (mapbox|maplibre).
## Make targets
`install lint format typecheck test test-fast synth preprocess train evaluate serve audit-memory web-dev web-test docker-up`
## Free fallback
No Mapbox token? Set `VITE_BASEMAP=maplibre` so the app still runs with an open style.
