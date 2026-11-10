# TerraSpectra — Hyperspectral Crop Disease Forecasting

![CI](https://github.com/Anmol007-007/TerraSpectra/actions/workflows/python-tests.yml/badge.svg)
![Coverage](https://codecov.io/gh/Anmol007-007/TerraSpectra/branch/main/graph/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

TerraSpectra ingests hyperspectral satellite data cubes (200+ bands), runs a **3D-CNN + Vision Transformer hybrid** (PyTorch) that detects subtle chlorophyll and chemical changes, and **forecasts fungal blight ~3 weeks (21 days) before visible symptoms**. Results are served through a **FastAPI** inference API that tiles huge rasters on GPU and displayed in a **React + Deck.gl + Mapbox** 3D GIS dashboard with a red 5-acre risk zone on a 1,000-acre farm, analytics sidebar, and a historical timeline slider.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Anmol007-007/TerraSpectra.git
cd TerraSpectra

# 2. Create virtual environment (Python 3.11 required)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install all dependencies
make install

# 4. Generate synthetic data
make synth

# 5. Train the model
make train

# 6. Start the API server
make serve

# 7. In a separate terminal, start the web dashboard
make web-dev
```

---

## Modules

| # | Module | Stack | Location |
|---|--------|-------|----------|
| 1 | Geospatial Data Pipeline | Python, Rasterio, GDAL, h5py, scikit-learn (PCA) | `src/terraspectra/data/` |
| 2 | 3D-CNN & ViT Hybrid Model | PyTorch | `src/terraspectra/models/`, `training/` |
| 3 | Inference API with Tiling | FastAPI, uvicorn, pydantic v2 | `src/terraspectra/api/` |
| 4 | GIS Dashboard | React 18, TypeScript, Vite, Deck.gl 9, Mapbox GL | `web/` |

---

## Documentation

- [Project Specification](docs/01_PROJECT_SPEC.md)
- [Architecture](docs/02_ARCHITECTURE.md)
- [Repository Structure](docs/03_REPO_STRUCTURE.md)
- [Tech Stack & Setup](docs/04_TECH_STACK_SETUP.md)
- [Data Specification](docs/05_DATA_SPEC.md)
- [ML Specification](docs/06_ML_SPEC.md)
- [API Specification](docs/07_API_SPEC.md)
- [Frontend Specification](docs/08_FRONTEND_SPEC.md)
- [Git Commit Protocol](docs/09_GIT_COMMIT_PROTOCOL.md)
- [Testing & QA](docs/10_TESTING_QA.md)
- [Contributing](CONTRIBUTING.md)

---

## License

[MIT](LICENSE) (c) 2026 TerraSpectra Contributors
