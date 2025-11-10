.PHONY: init format lint test run

init:
	python -m pip install -U pip
	pip install -r requirements.txt
	pre-commit install

format:
	black src tests
	ruff check --fix src tests || true

lint:
	black --check src tests
	ruff check src tests
	@nbstripout --is-installed >/dev/null 2>&1 || echo "Tip: run 'pre-commit install' to auto-strip notebooks."

test:
	pytest -q

run:
	python -m src.pipeline
