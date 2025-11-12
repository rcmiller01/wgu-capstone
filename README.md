# WGU D610 Capstone: Synthetic Health Data Processing Pipeline

**WGU Capstone Project** — Analysis of data processing pipeline performance for multi-source health data integration, focusing on validation accuracy and latency characteristics.

## 🎯 Project Scope

This project implements and evaluates a serverless FHIR data processing pipeline that integrates synthetic health data from multiple sources (Synthea, NHANES, VDH, NIH). The analysis examines:

- Pipeline validation pass rates across data sources
- Processing latency distribution and determinants  
- Impact of data quality flags on performance metrics
- Statistical comparison of processing outcomes

**Key Deliverable**: A reproducible data pipeline with validated outputs suitable for comparative performance analysis.

## 📊 Datasets & Licensing

All data used in this project is either **synthetic** or **publicly licensed**:

- **Synthea**: Synthetic FHIR R4 patient records (Apache 2.0 license)
- **NHANES**: CDC National Health and Nutrition Examination Survey (public domain)
- **VDH**: Virginia Department of Health public health statistics (public domain)
- **NIH**: Chest X-ray metadata from NIH Clinical Center (CC0 license)

**Security Note**: No credentials, API keys, or protected health information (PHI) are stored in this repository. All patient identifiers are hashed using HMAC-SHA256 for privacy-preserving linkage.

## 🚀 Quickstart (Grader Path)

This repository includes a **small processed sample** for grading purposes. The full data acquisition pipeline is documented but not required for evaluation.

### Prerequisites

- Python 3.11 (pinned for deterministic dependency resolution)
- 2 GB free disk space
- No network access required (uses committed processed data)

### Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies (pinned versions from requirements.txt)
python -m pip install -U pip
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### Validation (One-Command Smoke Test)

```bash
# Run all tests and generate minimal output (<2 minutes)
make smoke
```

This command:
1. Loads processed sample from `data/processed/cohort_fact_va.csv`
2. Runs validation tests (`pytest -q`)
3. Generates summary statistics

### Full Pipeline Execution

```bash
# Run complete pipeline (uses processed data, ~5 minutes)
make all
```

This executes:
1. **Data loading** from `data/processed/`
2. **Statistical analysis** (EDA, hypothesis tests)
3. **Visualization** generation (tables and figures)

**Expected Outputs**:
- `reports/figures/publication/*.png` — Publication-ready figures
- `reports/tables/` — Statistical tables (LaTeX/CSV format)
- `reports/analysis_summary.txt` — Text summary of findings

### SQL + DuckDB Data Lake Path (Optional)

For evaluators interested in the **SQL-centric data engineering** capabilities:

```bash
# Build local data lake with DuckDB (Bronze → Silver → Gold)
make lake

# Validate data quality
make lake-validate
```

This creates:
- **Bronze layer**: De-identified DICOM files (`data/bronze/images/`)
- **Silver layer**: Structured Parquet metadata (`data/silver/`)
- **Gold layer**: Analytics-ready joins (`data/gold/analytics/`)

**SQL transformations**:
- `sql/00_init.sql` — Create views over Parquet files
- `sql/20_gold_joins.sql` — Patient-imaging joins via DuckDB
- `sql/30_analytics_slices.sql` — Aggregations and summaries

**DuckDB advantages**:
- Embedded (no external database server)
- Direct queries on Parquet files
- SQL portable to Athena/BigQuery/Redshift

See [`docs/duckdb_overview.md`](docs/duckdb_overview.md) for architecture details.

## 📁 Repository Layout

```
wgu-capstone/
├── src/                      # Source code
│   ├── pipeline/            # Data acquisition & cleaning (636 LOC)
│   │   ├── data_acquisition.py
│   │   ├── data_cleaning.py
│   │   ├── synthea_processor.py
│   │   ├── nhanes_processor.py
│   │   └── build_cohort_fact.py
│   ├── analysis/            # Statistical analysis (541 LOC)
│   │   ├── run_eda.py
│   │   ├── run_statistical_tests.py
│   │   └── generate_phase7_outputs.py
│   └── visualization/       # Plotting utilities
├── etl/                     # Data lake ETL modules
│   ├── sanitize_dicom.py   # DICOM de-identification
│   ├── ingest_siim_metadata.py  # Imaging metadata extraction
│   ├── unify_patients.py   # Patient data unification
│   ├── build_link_table.py # Synthetic patient-image linkage
│   ├── build_gold_views.py # DuckDB SQL orchestration
│   └── validate_quality.py # Data quality checks
├── sql/                     # SQL transformation scripts
│   ├── 00_init.sql         # Create views over Parquet
│   ├── 10_silver_curate.sql  # Type casting & validation
│   ├── 20_gold_joins.sql   # Analytics table joins
│   └── 30_analytics_slices.sql  # Aggregations
├── tests/                   # Pytest test suite
│   ├── test_schema.py
│   ├── test_assumptions.py
│   └── test_cohort_fact_validation.py
├── data/                    # Data directories
│   ├── raw/                # Original source data (not committed)
│   ├── interim/            # Intermediate processing (not committed)
│   ├── processed/          # Final analysis-ready data (committed)
│   │   ├── cohort_fact_va.csv      # Main analysis dataset
│   │   └── metadata.json            # Dataset provenance
│   ├── bronze/             # De-identified DICOM (not committed)
│   ├── silver/             # Structured Parquet (not committed)
│   └── gold/               # Analytics tables (not committed)
├── reports/                 # Generated outputs
│   ├── figures/            # PNG visualizations
│   ├── tables/             # Statistical tables
│   └── schema_profile.md   # Data dictionary
├── docs/                    # Project documentation
│   ├── phase_index.md      # Phase-to-artifact mapping
│   ├── metrics_spec.md     # Variable definitions
│   ├── privacy_ethics.md   # Ethics & data governance
│   ├── duckdb_overview.md  # DuckDB architecture guide
│   ├── sql_equivalents.md  # Cloud SQL portability
│   └── PIPELINE_EXECUTION.md  # Technical pipeline guide
├── resources/               # Configuration files
│   ├── rules/*.json        # Validation rules
│   └── join_spec.json      # Data join specification
├── requirements.txt         # Pinned Python dependencies (single source of truth)
├── pyproject.toml          # Tool configuration (black, ruff, pytest)
├── Makefile                # Automation targets
└── .github/workflows/      # CI configuration (lint, tests)
```

## 🔬 Reproducibility

### Dependency Management

- **All dependencies pinned** in `requirements.txt` (e.g., `pandas==2.2.3`)
- Python version constrained to `>=3.11,<3.13` in `pyproject.toml`
- CI runs on Python 3.11 for deterministic grading

### Random Seed Management

Statistical analyses and simulations use fixed seeds for reproducibility:

- **Seed**: `42` (configured in `src/analysis/run_eda.py` and `src/analysis/run_statistical_tests.py`)
- NumPy: `numpy.random.default_rng(42)`
- Scikit-learn: `random_state=42` in all estimators

### Code Quality

- **Formatting**: `black` (line length 100)
- **Linting**: `ruff` (PEP 8, security checks, import sorting)
- **Type checking**: `mypy` (permissive mode, warns on redundant casts)
- **Pre-commit hooks**: Auto-strip notebook outputs, format code

## 🧪 Testing

```bash
# Run all tests with coverage report
make test

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"

# Run tests with verbose output
pytest -v
```

**Test Suite**:
- `test_schema.py`: Validates data structure and column presence
- `test_assumptions.py`: Checks statistical assumptions (normality, sample size)
- `test_cohort_fact_validation.py`: Verifies CohortFact_VA table integrity

Tests automatically **skip** when processed data is unavailable (e.g., fresh checkout).

## 📖 Documentation Map

See [`docs/phase_index.md`](docs/phase_index.md) for complete phase-to-artifact mapping.

**Key Documents**:
- **[Phase Index](docs/phase_index.md)**: Maps capstone phases to code/reports
- **[Metrics Specification](docs/metrics_spec.md)**: Variable definitions and derivations
- **[Privacy & Ethics](docs/privacy_ethics.md)**: Data governance and IRB considerations
- **[Pipeline Execution Guide](docs/PIPELINE_EXECUTION.md)**: Technical deep-dive on pipeline

## 🎨 Generating Figures & Tables

```bash
# Generate all publication figures (saves to reports/figures/publication/)
make visualize

# Launch Jupyter Lab for interactive exploration
make notebooks
```

**Output Locations**:
- `reports/figures/publication/figure1_passrate.png` — Pass rate comparison
- `reports/figures/publication/figure2_latency.png` — Latency distribution
- `reports/figures/publication/figure3_coverage.png` — Data coverage heatmap
- `reports/tables/table1_descriptive.tex` — Descriptive statistics (LaTeX)
- `reports/tables/table2_tests.csv` — Hypothesis test results

**Runtime**: Figure generation completes in ~3 minutes on the processed sample.

## 🧹 Cleaning

```bash
# Remove all generated files (preserve raw data)
make clean
```

This clears:
- `data/interim/` and `data/processed/`
- `reports/figures/` and `reports/tables/`
- Python caches (`__pycache__`, `.pytest_cache`)
- Coverage reports (`.coverage`, `htmlcov/`)

## 📋 Makefile Targets

```bash
make init        # Install dependencies and pre-commit hooks
make all         # Run complete pipeline (data + analysis + viz)
make smoke       # Quick validation test (<2 minutes)
make data        # Data acquisition and cleaning (requires raw data)
make analyze     # Run EDA and statistical tests
make visualize   # Generate publication figures
make notebooks   # Launch Jupyter Lab
make test        # Run pytest suite
make lint        # Check code style (black, ruff)
make format      # Auto-format code
make clean       # Remove generated files
make help        # Show target descriptions
```

## 📦 Data Acquisition (Optional — Not Required for Grading)

The `data/raw/` directory is **empty by default**. Graders should use the committed processed sample in `data/processed/`.

For full reproducibility (optional), the acquisition pipeline is documented in:
- [`docs/PIPELINE_EXECUTION.md`](docs/PIPELINE_EXECUTION.md)
- [`src/pipeline/data_acquisition.py`](src/pipeline/data_acquisition.py)

**Note**: Acquiring Synthea data requires ~10-30 minutes and ~20 GB disk space. NHANES downloads require CDC FTP access. This is **not necessary** for grading.

## ⏱️ Expected Runtime

On a typical machine (4-core, 16 GB RAM):

| Task | Runtime |
|------|---------|
| `make smoke` | <2 minutes |
| `make test` | <2 minutes |
| `make analyze` | 3-5 minutes |
| `make visualize` | 2-3 minutes |
| `make all` | 5-10 minutes |
| Full data acquisition | 30-60 minutes (optional) |

## 📄 License & Academic Integrity

This project is released under the **MIT License** (see [`LICENSE`](LICENSE)).

All work is original and complies with WGU's academic integrity policy (see [`ACADEMIC_INTEGRITY.md`](ACADEMIC_INTEGRITY.md)).

## 📚 Citation

If referencing this work, please cite:

```bibtex
@software{wgu_capstone_2025,
  title = {WGU D610 Capstone: Synthetic Health Data Processing Pipeline},
  author = {Miller, Robert C.},
  year = {2025},
  url = {https://github.com/rcmiller01/wgu-capstone},
  version = {1.0.0}
}
```

## 🆘 Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'src'`  
**Fix**: Ensure virtual environment is activated and dependencies installed (`pip install -r requirements.txt`)

**Issue**: Tests skip with "Processed data not available"  
**Fix**: Expected behavior on fresh checkout. Run `make all` to generate data, or use committed `data/processed/cohort_fact_va.csv`

**Issue**: Figures don't match expected outputs  
**Fix**: Verify random seed is set to `42` in analysis scripts. Re-run `make clean && make all`

**Issue**: `make` commands fail on Windows  
**Fix**: Install `make` via Chocolatey (`choco install make`) or run Python commands directly:
```powershell
# Instead of 'make test'
pytest -q

# Instead of 'make all'
python -m src.pipeline
python -m src.analysis.run_eda
python -m src.analysis.run_statistical_tests
python -m src.visualization
```

---

**Contact**: For questions about this capstone project, please refer to the WGU course materials or contact your course instructor.
