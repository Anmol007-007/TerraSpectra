# Contributing to TerraSpectra

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): imperative summary
```

**Types:** `feat` `fix` `docs` `test` `refactor` `perf` `build` `ci` `chore` `style`

**Scopes (optional):** `web` `api` `data` `models` `training` `inference` `synth` `geo` `core` `ci`

### Examples
```
feat(data): add windowed GeoTIFF reader with Rasterio
fix(models): correct SE attention channel dimension mismatch
docs: update API_SPEC with /v1/jobs endpoints
test(geo): add property test for m2_to_acres round-trip
ci: pin ubuntu-22.04 in GitHub Actions workflows
```

## Daily Protocol

1. `git checkout -b day/XX-short-name` from `main`
2. Execute each step from `plan/DAY_XX.md` in order
3. After each step: `make lint` → commit → next step
4. At end of day: `bash scripts/check_commits.sh` (must print >= 52)
5. `git checkout main && git merge --no-ff day/XX-short-name`
6. `git push origin main`

## Code Standards

- **Python**: 3.11, full type hints, mypy --strict, ruff, Google docstrings
- **TypeScript**: strict mode, no `any`, functional components + hooks
- **Tests**: every public function; bug fix = failing test first
- **No secrets**: `.env.local` is gitignored; Mapbox token stays local

