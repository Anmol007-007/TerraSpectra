# Day 16 — FastAPI core, schemas, model service, endpoints; real API integration in UI (Week 4 start)

Goal: Running REST API serving models and scenes; frontend switched from mocks to live API.

**Branch:** `day/16-work` · **Target:** exactly 52 commits (one per step) · Read `AGENTS.md` first.

Rule: finish a step, run `make lint` + related tests, then `git commit -m "<message>"`. Do not combine steps.


## A. App core

- [ ] **01** `feat(api): add FastAPI app factory`
- [ ] **02** `feat(api): add settings dependency`
- [ ] **03** `feat(api): add lifespan startup and shutdown`
- [ ] **04** `feat(api): configure CORS`
- [ ] **05** `feat(api): add request-id middleware`
- [ ] **06** `feat(api): add request logging middleware`
- [ ] **07** `feat(api): add global exception handlers`
- [ ] **08** `feat(api): add health endpoint`
- [ ] **09** `feat(api): add version endpoint`
- [ ] **10** `feat(api): add OpenAPI metadata and tags`
- [ ] **11** `feat(api): add uvicorn run script and make serve`
- [ ] **12** `test(api): add health and version tests`

## B. Schemas

- [ ] **13** `feat(api): add PredictRequest schema`
- [ ] **14** `feat(api): add PredictResponse and Result schemas`
- [ ] **15** `feat(api): add GeoJSON pydantic models`
- [ ] **16** `feat(api): add JobStatus response schema`
- [ ] **17** `feat(api): add error response schema`
- [ ] **18** `feat(api): add pagination schema`
- [ ] **19** `feat(api): add request validators`
- [ ] **20** `test(api): add schema validation tests`

## C. Model service

- [ ] **21** `feat(api): add ModelRegistry service`
- [ ] **22** `feat(api): load checkpoint at startup`
- [ ] **23** `feat(api): add device placement`
- [ ] **24** `feat(api): add warmup inference`
- [ ] **25** `feat(api): add thread-safe access lock`
- [ ] **26** `feat(api): add singleton accessor dependency`
- [ ] **27** `feat(api): add inference function wrapper`
- [ ] **28** `feat(api): add fp16 inference option`
- [ ] **29** `feat(api): add batch predict function`
- [ ] **30** `test(api): add model service tests`

## D. Endpoints

- [ ] **31** `feat(api): add GET /v1/models`
- [ ] **32** `feat(api): add GET /v1/scenes`
- [ ] **33** `feat(api): add GET /v1/scenes/{id}`
- [ ] **34** `feat(api): add POST /v1/predict`
- [ ] **35** `feat(api): add GET /v1/jobs/{id}`
- [ ] **36** `feat(api): add GET /v1/jobs/{id}/result`
- [ ] **37** `feat(api): add GET /v1/jobs/{id}/zones`
- [ ] **38** `feat(api): add GET /v1/scenes/{id}/analytics`
- [ ] **39** `feat(api): add POST /v1/scenes/upload`
- [ ] **40** `test(api): add endpoint tests`

## E. Frontend API integration

- [ ] **41** `feat(web): add real API client endpoints`
- [ ] **42** `feat(web): add VITE_API_BASE_URL handling`
- [ ] **43** `feat(web): make mocks opt-in via VITE_USE_MOCKS`
- [ ] **44** `test(web): add MSW handlers matching API spec`
- [ ] **45** `feat(web): add typed endpoint functions`
- [ ] **46** `feat(web): add SceneSelector component`
- [ ] **47** `feat(web): add ModelSelector component`
- [ ] **48** `feat(web): add Run Prediction button`
- [ ] **49** `feat(web): add job polling hook`
- [ ] **50** `feat(web): add progress UI`
- [ ] **51** `feat(web): add API error handling UX`
- [ ] **52** `test(web): add API integration tests`

---
End of day: run `scripts/check_commits.sh` (expects >= 52). Merge `day/16-work` into `main` with `--no-ff`.
