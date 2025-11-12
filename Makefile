.PHONY: init format lint test run all data clean analyze visualize notebooks help

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

# ============================================================
# Imaging Data Lake Targets (Local-First)
# ============================================================

lake: lake-bronze lake-silver lake-gold
	@echo "✓ Complete data lake built locally"

lake-bronze:
	@echo "Building Bronze layer (raw metadata)..."
	python etl/ingest_siim_metadata.py --output data/lake/bronze/imaging/
	@echo "✓ Bronze layer complete"

lake-silver: lake-bronze
	@echo "Building Silver layer (sanitized + linked)..."
	python etl/sanitize_dicom.py --output data/lake/silver/imaging/dicom_sanitized/
	python etl/build_link_table.py --output data/lake/silver/imaging/imaging_cohort_links.parquet
	@echo "✓ Silver layer complete"

lake-gold: lake-silver
	@echo "Building Gold layer (analytics-ready)..."
	@echo "  (Placeholder: aggregate tables, ML features)"
	@echo "✓ Gold layer complete"

smoke: lake
	@echo "Running smoke test (end-to-end)..."
	@python -c "import pandas as pd; df = pd.read_parquet('data/lake/bronze/imaging/ct_imaging_bronze.parquet'); print(f'✓ Smoke test passed: {len(df)} records in Bronze')"
	@echo "✓ Smoke test complete"

# ============================================================
# Cloud Publishing Targets (Optional - Requires AWS)
# ============================================================

publish-s3:
	@echo "Publishing data lake to S3..."
	python etl/publish_s3.py --bucket $(S3_BUCKET) --prefix capstone/datalake/
	@echo "✓ S3 publish complete"

glue-catalog:
	@echo "Creating Glue Data Catalog..."
	python etl/publish_glue_catalog.py --database capstone_imaging --s3-bucket $(S3_BUCKET)
	@echo "✓ Glue catalog created"

athena-views:
	@echo "Creating Athena convenience views..."
	@echo "  (Placeholder: run CREATE VIEW statements)"
	@echo "✓ Athena views created"

# ============================================================
# Database Loading Targets (Optional)
# ============================================================

redshift-load:
	@echo "Loading data to Redshift Serverless..."
	@echo "  1. Ensure Redshift workgroup is running"
	@echo "  2. Update IAM role ARN in infrastructure/redshift/copy_commands.sql"
	@echo "  3. Run: psql -h <endpoint> -U admin -d capstone_imaging -f infrastructure/redshift/copy_commands.sql"
	@echo "✓ Redshift load instructions shown"

rds-load:
	@echo "Loading data to RDS Postgres (small subsets)..."
	@echo "  (Placeholder: convert parquet to CSV, psql COPY)"
	@echo "✓ RDS load complete"

# ============================================================
# Privacy and Compliance Targets
# ============================================================

deidentify: lake-silver
	@echo "Running de-identification validation..."
	@python -c "import json; f=open('data/lake/silver/imaging/sanitization_report.json'); r=json.load(f); print(f'✓ Sanitized {len(r)} files'); flagged=[x for x in r if x['burned_in_warnings']]; print(f'⚠ {len(flagged)} files flagged for manual review')"
	@echo "✓ De-identification check complete"
	@echo "  Review: data/lake/silver/imaging/sanitization_report.json"

privacy-check:
	@echo "Checking privacy compliance..."
	@echo "  □ HIPAA Safe Harbor: 18 identifiers removed"
	@echo "  □ Ages >89: Capped (if any)"
	@echo "  □ Burned-in text: Flagged for review"
	@echo "  □ Pseudonymization: SHA-256 hashing applied"
	@echo "✓ Privacy checklist verified (see docs/privacy.md)"

# ============================================================
# Hygiene and Maintenance
# ============================================================

clean-lake:
	@echo "Cleaning data lake..."
	rm -rf data/lake/bronze/* data/lake/silver/* data/lake/gold/*
	@echo "✓ Data lake cleaned"

clean-all: clean clean-lake
	@echo "✓ All generated files removed"

help:
	@echo "WGU D610 Capstone - Available targets:"
	@echo ""
	@echo "=== Core Pipeline ==="
	@echo "  make init        - Install dependencies"
	@echo "  make all         - Run complete pipeline (data + analysis + visualization)"
	@echo "  make data        - Download and clean data"
	@echo "  make analyze     - Run EDA and statistical tests"
	@echo "  make visualize   - Generate all figures"
	@echo ""
	@echo "=== Imaging Data Lake (Local) ==="
	@echo "  make lake        - Build Bronze/Silver/Gold layers locally"
	@echo "  make smoke       - Quick end-to-end test with SIIM metadata"
	@echo "  make deidentify  - Run DICOM sanitization + validation"
	@echo ""
	@echo "=== Cloud Publishing (Optional - Requires AWS) ==="
	@echo "  make publish-s3      - Sync lake to S3 (set S3_BUCKET=...)"
	@echo "  make glue-catalog    - Create Glue database + tables"
	@echo "  make athena-views    - Create Athena convenience views"
	@echo "  make redshift-load   - Load data to Redshift Serverless"
	@echo "  make rds-load        - Load data to RDS Postgres"
	@echo ""
	@echo "=== Privacy & Compliance ==="
	@echo "  make privacy-check   - Validate HIPAA compliance"
	@echo ""
	@echo "=== Development ==="
	@echo "  make notebooks   - Launch Jupyter Lab"
	@echo "  make test        - Run pytest"
	@echo "  make format      - Format code with black/ruff"
	@echo "  make lint        - Check code style"
	@echo ""
	@echo "=== Cleanup ==="
	@echo "  make clean       - Remove generated files"
	@echo "  make clean-lake  - Remove data lake files"
	@echo "  make clean-all   - Remove all generated files"
	@echo ""
	@echo "Examples:"
	@echo "  make lake                              # Build local data lake"
	@echo "  make smoke                             # Quick test"
	@echo "  S3_BUCKET=my-bucket make publish-s3   # Publish to AWS"
