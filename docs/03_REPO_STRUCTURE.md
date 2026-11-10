# 03 — Repository Structure (create files only here)
```
terraspectra/
├── AGENTS.md  CLAUDE.md  .cursorrules  .github/copilot-instructions.md
├── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md
├── pyproject.toml  requirements.txt  requirements-dev.txt  .python-version
├── Makefile  .pre-commit-config.yaml  .gitignore  .gitattributes  .editorconfig  .dockerignore
├── docker-compose.yml
├── configs/ default.yaml data.yaml model.yaml train.yaml api.yaml
├── data/ raw/ interim/ processed/ synthetic/ catalog/     (git-ignored, .gitkeep only)
├── models_store/                                          (checkpoints; git-ignored)
├── reports/ figures/ audits/ experiments.md
├── docs/ 01..10 *.md, KNOWN_ISSUES.md
├── plan/ DAY_01.md ... DAY_20.md
├── scripts/ check_commits.sh audit_memory.py bench_*.py
├── src/terraspectra/
│   ├── __init__.py  cli.py
│   ├── core/ settings.py logging.py seed.py timing.py device.py paths.py hashing.py constants.py schemas.py errors.py
│   ├── synth/ wavelengths.py leaf.py stress.py fields.py cube.py labels.py cli.py
│   ├── geo/ transforms.py gdal_utils.py area.py zones.py
│   ├── data/ readers/{base,geotiff,hdf5,factory}.py writers.py windows.py catalog.py
│   │         preprocess/{clean,normalize,indices,pca,pipeline}.py
│   │         patches.py dataset.py splits.py augment.py loaders.py
│   ├── models/ blocks3d.py cnn3d.py tokens.py attention.py vit.py hybrid.py heads.py temporal.py registry.py
│   ├── training/ trainer.py losses.py metrics.py callbacks.py train.py evaluate.py calibration.py explain.py profiling.py
│   ├── inference/ tiling.py stitch.py engine.py batching.py zones.py
│   └── api/ main.py deps.py schemas.py middleware.py security.py
│            services/{registry,jobs,cache}.py  routers/{health,scenes,predict,jobs,analytics}.py
├── tests/ unit/ integration/ api/ fixtures/ conftest.py
└── web/
    ├── package.json vite.config.ts tsconfig.json tailwind.config.ts .env.example
    ├── src/ main.tsx App.tsx
    │   ├── components/ map/ layout/ panels/ charts/ timeline/ common/
    │   ├── layers/ farmBoundary.ts parcels.ts heatmap.ts zones.ts uncertainty.ts
    │   ├── store/ (zustand slices)   hooks/   api/ (client, endpoints, zod schemas, mocks)
    │   └── utils/ geo.ts color.ts format.ts acres.ts   types/   styles/
    └── tests/ unit/ e2e/ fixtures/
```
