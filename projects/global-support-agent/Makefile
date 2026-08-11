.PHONY: setup dev format lint test eval verify

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[dev]"

dev:
	$(PYTHON) -m uvicorn mova_support.api:app --reload --host 127.0.0.1 --port 8000

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest tests/unit tests/integration

eval:
	$(PYTHON) -m pytest tests/evals

verify: lint test eval

