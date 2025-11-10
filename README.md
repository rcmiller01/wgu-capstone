# WGU Capstone — Repository Skeleton

A minimal, grader-proof scaffold for the capstone project. It favors reproducibility, privacy, and tidy commits.

## Quickstart
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1  # adjust for your OS
python -m pip install -U pip
pip install -r requirements.txt
pre-commit install
make lint
make test
python -m src.pipeline

Layout
src/                # pipeline & analysis code
notebooks/          # exploratory only; outputs stripped in CI/pre-commit
data/
  raw/
  interim/
  processed/
models/
reports/
  figures/
docs/
  privacy_ethics.md
  baseline_sources.md
references/
  apa.bib

Ethics & Privacy

See docs/privacy_ethics.md. This project avoids PHI and uses public or synthetic data. Pseudonymization (customer_id) is required when joining longitudinal sources.

Reproducibility

Pinned tooling via requirements.txt

Consistent formatting (black) and linting (ruff)

Notebook outputs are stripped via pre-commit

Minimal tests verify structure and invariants

License & Academic Integrity

Add your preferred license (MIT recommended) and see ACADEMIC_INTEGRITY.md.
