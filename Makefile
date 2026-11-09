.PHONY: install api test lint eval seed dev

install:
	python -m pip install -e ".[dev]"

seed:
	python data/generate_dataset.py

api:
	uvicorn apps.api.main:app --reload --port 8000

dev:
	uvicorn apps.api.main:app --port 8000

test:
	pytest tests/ mcp_servers/ -v

lint:
	ruff check .

eval:
	python evals/runners/ci_eval.py
