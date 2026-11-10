.PHONY: install lint format typecheck test test-fast synth preprocess train evaluate serve audit-memory web-dev web-test docker-up help

PYTHON := python
SRC := src/terraspectra
TESTS := tests

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all deps and pre-commit hooks
	$(PYTHON) -m pip install -e ".[dev,geo,ml]"
	pre-commit install

lint:  ## Run ruff linter
	ruff check $(SRC) $(TESTS) scripts

format:  ## Run ruff formatter
	ruff format $(SRC) $(TESTS) scripts

typecheck:  ## Run mypy strict type checker
	mypy $(SRC)

test:  ## Run all tests with coverage
	pytest $(TESTS) --cov=$(SRC) --cov-report=term-missing --cov-report=xml

test-fast:  ## Run only unit tests (fast)
	pytest $(TESTS) -m "unit" --no-cov

synth:  ## Generate synthetic data
	$(PYTHON) -m terraspectra.synth.cli generate

preprocess:  ## Run preprocessing pipeline
	$(PYTHON) -m terraspectra.data.preprocess.pipeline

train:  ## Train the model
	$(PYTHON) -m terraspectra.training.train

evaluate:  ## Evaluate the model
	$(PYTHON) -m terraspectra.training.evaluate

serve:  ## Start the FastAPI server
	uvicorn terraspectra.api.main:app --reload --host 0.0.0.0 --port 8000

audit-memory:  ## Run memory audit script
	$(PYTHON) scripts/audit_memory.py

web-dev:  ## Start the React dev server
	cd web && npm run dev

web-test:  ## Run frontend tests
	cd web && npm test

docker-up:  ## Start all services via docker-compose
	docker-compose up --build
