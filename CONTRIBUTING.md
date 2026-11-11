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

1. Checkout/work on `day/XX-short-name` or `main`.
2. Implement and test all items from `plan/DAY_XX.md`.
3. Keep code modular, run `make lint` and tests.
4. Clean up any temporary scratch files or unnecessary artifacts.
5. At the end of the day, commit all completed work at once and push to `main`.

## Code Standards

- **Python**: 3.11, full type hints, mypy --strict, ruff, Google docstrings
- **TypeScript**: strict mode, no `any`, functional components + hooks
- **Tests**: every public function; bug fix = failing test first
- **No secrets**: `.env.local` is gitignored; Mapbox token stays local

