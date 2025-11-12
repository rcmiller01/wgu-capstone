.PHONY: init format lint test smoke run all data clean analyze visualize notebooks help

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

smoke:
	@echo "Running smoke test (quick validation)..."
	@echo "1. Checking data availability..."
	@test -f data/processed/cohort_fact_va.csv && echo "   ✓ Processed data found" || echo "   ⚠ Processed data missing"
	@echo "2. Running tests..."
	@pytest -q --tb=short
	@echo "3. Generating summary statistics..."
	@python -c "import pandas as pd; df = pd.read_csv('data/processed/cohort_fact_va.csv'); print(f'   ✓ Loaded {len(df)} rows, {len(df.columns)} columns')"
	@echo "✓ Smoke test complete"

run:
	python -m src.pipeline

# Analysis workflow targets
all: data analyze visualize
	@echo "✓ Complete pipeline executed successfully"

data:
	@echo "Running data acquisition..."
	python -m src.pipeline --acquire
	@echo "Running data cleaning..."
	python -m src.pipeline --clean
	@echo "✓ Data pipeline complete"

analyze:
	@echo "Running exploratory data analysis..."
	python -m src.analysis.run_eda
	@echo "Running statistical tests..."
	python -m src.analysis.run_statistical_tests
	@echo "✓ Analysis complete"

visualize:
	@echo "Generating publication figures..."
	python -m src.visualization
	@echo "✓ Visualizations complete"

notebooks:
	@echo "Starting Jupyter Lab..."
	jupyter lab

clean:
	@echo "Cleaning generated files..."
	rm -rf data/interim/* data/processed/*
	rm -rf reports/figures/eda/* reports/figures/publication/* reports/figures/interactive/*
	rm -rf __pycache__ src/__pycache__ src/pipeline/__pycache__ src/analysis/__pycache__
	rm -rf .pytest_cache htmlcov .coverage
	rm -f reports/*.txt reports/*.csv
	@echo "✓ Clean complete"

help:
	@echo "WGU D610 Capstone - Available targets:"
	@echo ""
	@echo "  make init        - Install dependencies"
	@echo "  make smoke       - Quick validation test (<2 minutes)"
	@echo "  make all         - Run complete pipeline (data + analysis + visualization)"
	@echo "  make data        - Download and clean data"
	@echo "  make analyze     - Run EDA and statistical tests"
	@echo "  make visualize   - Generate all figures"
	@echo "  make notebooks   - Launch Jupyter Lab"
	@echo "  make test        - Run pytest"
	@echo "  make clean       - Remove generated files"
	@echo "  make format      - Format code with black/ruff"
	@echo "  make lint        - Check code style"
	@echo "  make help        - Show this help message"
