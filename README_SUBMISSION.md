# WGU Capstone Submission - START HERE

**Project**: A Paired t-Test Analysis of a Serverless FHIR Lakehouse for Streamlined and Consistent Rural Health Data Exchange  
**Student**: Robert Miller (000982134)  
**Submission Date**: November 11, 2025  
**Program**: Master of Science in Data Analytics (MSDA)

---

## 📂 Quick Navigation

This document is your **starting point** for navigating the complete capstone submission. All deliverables are organized below with direct links and descriptions.

### **🎯 Essential Documents (Start Here)**

1. **[Final Proposal Document](docs/proposal_reference.md)** - Research question, hypotheses, methods, and IRB status
2. **[Results Write-Up](reports/phase8_results_writeup.md)** - Complete results section with tables, figures, and interpretation
3. **[Phase 8 Completion Summary](reports/phase8_completion_summary.md)** - Executive summary of findings

### **📊 Core Deliverables by Phase**

| Phase | Document | Description |
|:------|:---------|:------------|
| **Phase 0** | [Proposal Reference](docs/proposal_reference.md) | Final proposal with research question and hypotheses |
| **Phase 1** | [Data Sources](docs/data_sources.md) | Synthea, NHANES, VDH data documentation |
| **Phase 1** | [Variables Table](docs/variables_table.md) | Complete data dictionary with 50+ variables |
| **Phase 2** | [Baseline Sources](docs/baseline_sources.md) | Manual entry benchmarks from literature |
| **Phase 3** | [Cleaning Plan](docs/cleaning_plan.md) | 10-stage cleaning workflow with v1 vs v2 comparison |
| **Phase 4** | [Metrics Specification](docs/metrics_spec.md) | P50/P95 latency, validation pass rate definitions |
| **Phase 4** | [Validation Policy](docs/methods_validation_policy.md) | v1 strict vs v2 relaxed validation rules |
| **Phase 5** | [pyproject.toml](pyproject.toml) | Python environment with locked versions |
| **Phase 6** | [Cohort Fact Table](data/processed/cohort_fact_va_v2_relaxed.csv) | Final aggregated metrics (4 rows × 7 columns) |
| **Phase 7** | [Phase 6 & 7 Summary](reports/phase6_phase7_summary.md) | Pipeline implementation and statistical analysis |
| **Phase 8** | [Results Write-Up](reports/phase8_results_writeup.md) | Complete results section (ready for DOCX) |

---

## 📁 Repository Structure

```
wgu-capstone/
├── README.md                          # Main project README
├── README_SUBMISSION.md               # ⭐ THIS FILE - Start here
├── pyproject.toml                     # Python project configuration
├── requirements.txt                   # Python dependencies
├── Makefile                           # Automation tasks
│
├── docs/                              # 📚 Documentation
│   ├── proposal_reference.md          # Final proposal
│   ├── data_sources.md                # Data source details
│   ├── variables_table.md             # Data dictionary
│   ├── metrics_spec.md                # Metrics definitions
│   ├── cleaning_plan.md               # Data cleaning workflow
│   ├── methods_validation_policy.md   # Validation rules policy
│   └── privacy_ethics.md              # IRB exemption justification
│
├── data/                              # 💾 Data Files
│   ├── processed/                     # Final outputs
│   │   ├── cohort_fact_va_v2_relaxed.csv       # Aggregated metrics
│   │   ├── processed_data.parquet              # Row-level data (1,010 records)
│   │   └── metadata.json                       # Provenance metadata
│   ├── raw/                           # Source data (not in repo - see DATA_DOWNLOAD_STATUS.md)
│   └── interim/                       # Intermediate processing outputs
│
├── reports/                           # 📈 Results and Analysis
│   ├── phase8_results_writeup.md      # ⭐ Main results document
│   ├── phase8_completion_summary.md   # Executive summary
│   ├── phase6_phase7_summary.md       # Pipeline and analysis summary
│   ├── table1_pass_rates.md/.csv      # Validation pass rates
│   ├── table2_latency_stats.md/.csv   # Processing latency statistics
│   ├── sensitivity_analysis_report.md # Robustness analysis
│   ├── figure1_pass_rate_comparison.png        # Pass rate bar chart
│   ├── figure2_latency_dotwhisker.png          # Latency error bars
│   └── figure3_coverage_trends.png             # 4-panel dashboard
│
├── src/                               # 🐍 Python Source Code
│   ├── pipeline/                      # Data processing scripts
│   │   ├── process_raw_data.py        # Main processing pipeline
│   │   ├── data_cleaning.py           # Cleaning functions
│   │   └── generate_cohort_summary.py # Aggregation logic
│   ├── analysis/                      # Statistical analysis scripts
│   │   ├── generate_phase7_outputs.py # Tables and figures generation
│   │   └── sensitivity_analysis.py    # Robustness testing
│   └── visualization/                 # Plotting utilities
│
├── resources/                         # 🔧 Configuration Files
│   ├── join_spec.json                 # Join keys and flag definitions
│   └── rules/                         # Validation rule packs (50+ rules)
│       ├── core.json                  # Cross-source core rules
│       ├── synthea.json               # FHIR-specific rules
│       ├── nhanes.json                # NHANES-specific rules
│       ├── vdh.json                   # VDH-specific rules
│       └── nih.json                   # NIH imaging rules (future)
│
├── tests/                             # ✅ Test Suite
│   ├── test_schema.py                 # 9 layout and schema tests
│   └── test_assumptions.py            # Data quality tests
│
├── references/                        # 📖 Bibliography
│   └── apa.bib                        # BibTeX references (APA 7th)
│
└── .github/workflows/                 # 🔄 CI/CD
    ├── tests.yml                      # Automated testing
    └── lint.yml                       # Code quality checks
```

---

## 🎯 Key Results (Executive Summary)

### Performance Metrics (All Targets Met ✓)

| Metric | Result | Target | Status |
|:-------|:------:|:------:|:------:|
| **Validation Pass Rate** | 95.9% | ≥95% | ✅ |
| **Median Latency (P50)** | 16.12s | ≤30s | ✅ |
| **Tail Latency (P95)** | 42.06s | ≤120s | ✅ |

### Key Findings

1. **Validation Calibration**: v2 relaxed policy improved pass rate by +1.1 percentage points (94.9% → 95.9%) while maintaining data quality standards

2. **Format-Specific Patterns**: 
   - FHIR JSON (Synthea): P50=16.16s, P95=42.06s (complex nested structure)
   - XPT Binary (NHANES): P50=5.94s, P95=6.59s (efficient binary format)
   - CSV Text (VDH): P50=3.45s, P95=4.09s (simple tabular data)

3. **Speedup vs Manual**: Automated pipeline is **56-168x faster** than manual entry (16s vs 900-2700s from literature)

4. **Robustness**: Sensitivity analysis confirmed findings stable across data quality scenarios (max deltas: +0.4 pp pass rate, +0.03s latency)

---

## 🔬 Reproducibility Guide

### Prerequisites

1. **Python Environment**: Python 3.11+ (tested with 3.13.5)
2. **Operating System**: Windows, macOS, or Linux
3. **Dependencies**: All specified in `requirements.txt`

### Quick Start (Reproduce All Results)

```powershell
# 1. Clone repository
git clone https://github.com/rcmiller01/wgu-capstone.git
cd wgu-capstone

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download data (optional - processed data already included)
python download_synthea.py
python download_vdh.py
# NHANES requires manual download (see data/raw/nhanes/README.md)

# 5. Run pipeline (or skip - outputs already in data/processed/)
python -m src.pipeline

# 6. Generate analysis outputs
python src/analysis/generate_phase7_outputs.py
python src/analysis/sensitivity_analysis.py

# 7. Run tests
pytest tests/ -v

# 8. View results
# Open reports/phase8_results_writeup.md in markdown viewer
# Or convert to DOCX: pandoc reports/phase8_results_writeup.md -o results.docx
```

### Using Make (Automation)

```powershell
make install     # Install dependencies
make test        # Run test suite
make lint        # Check code quality
make clean       # Clean temporary files
make all         # Run full pipeline
```

---

## 📊 Tables and Figures Reference

### Tables

| Table | File | Description |
|:------|:-----|:------------|
| **Table 1** | [table1_pass_rates.md](reports/table1_pass_rates.md) | Validation pass rates (v1 strict vs v2 relaxed) by source |
| **Table 2** | [table2_latency_stats.md](reports/table2_latency_stats.md) | Processing latency (P50/P95) with 95% CI by source |
| **Table 3** | [sensitivity_analysis_report.md](reports/sensitivity_analysis_report.md) | Sample sizes by exclusion scenario |
| **Table 4** | [sensitivity_analysis_report.md](reports/sensitivity_analysis_report.md) | Validation pass rates by scenario with deltas |
| **Table 5** | [sensitivity_analysis_report.md](reports/sensitivity_analysis_report.md) | Median latency by scenario with deltas |

### Figures

| Figure | File | Description |
|:-------|:-----|:------------|
| **Figure 1** | [figure1_pass_rate_comparison.png](reports/figure1_pass_rate_comparison.png) | Pass rate bar chart (v1 → v2) by source |
| **Figure 2** | [figure2_latency_dotwhisker.png](reports/figure2_latency_dotwhisker.png) | Latency dot-whisker plots (P50/P95) with 95% CI |
| **Figure 3** | [figure3_coverage_trends.png](reports/figure3_coverage_trends.png) | 4-panel coverage dashboard (counts, distributions, scatter, pass rates) |

---

## 🔍 Data Processing Pipeline

### Input Data Sources

1. **Synthea Synthetic FHIR Records**: 1,000 patient bundles (FHIR R4 JSON)
   - Source: https://synthea.mitre.org/downloads
   - Format: Nested JSON with Encounter, Observation, Medication, etc.
   - Size: ~2.4 MB average per file

2. **NHANES Public Health Data**: 8 XPT files (CDC survey data)
   - Source: https://www.cdc.gov/nchs/nhanes
   - Format: SAS XPT binary
   - Size: ~500 KB average per file

3. **Virginia Department of Health Data**: 2 CSV files (state health indicators)
   - Source: https://data.virginia.gov/browse?tags=health
   - Format: CSV text
   - Size: ~100 KB average per file

### Processing Stages

1. **Format Parsing**: FHIR JSON → DataFrame, XPT → DataFrame, CSV → DataFrame
2. **Schema Validation**: 50+ rules across 5 rule packs (core, synthea, nhanes, vdh, nih)
3. **Temporal Derivation**: Extract month identifier (YYYY-MM) from heterogeneous date fields
4. **Quality Flagging**: low_precision_time, ambiguous_geo, lab_oob_na flags
5. **Performance Logging**: Capture latency_sec, file_size_kb, validation_passed
6. **Aggregation**: Group by data_source → cohort_fact_va table (4 rows)

### Output Files

- **Row-Level**: `data/processed/processed_data.parquet` (1,010 records)
- **Aggregated**: `data/processed/cohort_fact_va_v2_relaxed.csv` (4 rows: nhanes, synthea, vdh, ALL)
- **Metadata**: `data/processed/metadata.json` (provenance: date, seed, record counts)

---

## 🛠️ Validation Framework

### Rule Pack Architecture

**Location**: `resources/rules/*.json`

| Rule Pack | Rules | Severity | Purpose |
|:----------|:-----:|:---------|:--------|
| **core.json** | 12 | error_if_metric_uncomputable | Cross-source data quality (required fields, data types) |
| **synthea.json** | 18 | v2_relaxed | FHIR-specific validation (optional elements allowed) |
| **nhanes.json** | 8 | strict | NHANES survey structure (complete temporal data) |
| **vdh.json** | 6 | strict | VDH CSV format (simple tabular checks) |
| **nih.json** | 6 | future | NIH imaging metadata (not yet implemented) |

### Validation Policies

- **v1 (Strict)**: Fails files with any missing optional FHIR elements → 94.9% pass rate
- **v2 (Relaxed/Calibrated)**: Allows optional elements; fails only if >5% metric-critical rows unusable → **95.9% pass rate**

**Rationale**: v2 aligns with HL7 FHIR R4 specification where many elements have 0..1 or 0..* cardinality

---

## 📖 Documentation Index

### Proposal and Methods

- **[Proposal Reference](docs/proposal_reference.md)**: Research question, hypotheses, success criteria, IRB exemption
- **[Metrics Specification](docs/metrics_spec.md)**: P50/P95 latency, validation pass rate definitions with formulas and targets
- **[Validation Policy](docs/methods_validation_policy.md)**: v1 vs v2 comparison, error handling, flag definitions
- **[Cleaning Plan](docs/cleaning_plan.md)**: 10-stage workflow, sentinel values, nullable dtypes

### Data Documentation

- **[Data Sources](docs/data_sources.md)**: Synthea, NHANES, VDH descriptions with URLs
- **[Variables Table](docs/variables_table.md)**: Complete data dictionary (50+ variables with types, ranges, descriptions)
- **[Data Dictionary - Cohort VA](docs/data_dictionary_cohort_va.md)**: Cohort fact table schema (7 columns)
- **[Join Specification](resources/join_spec.json)**: Join keys, synthetic flags, aggregation logic

### Results and Analysis

- **[Phase 8 Results Write-Up](reports/phase8_results_writeup.md)**: Complete results section with tables, figures, interpretation, limitations
- **[Phase 8 Completion Summary](reports/phase8_completion_summary.md)**: Executive summary with key findings
- **[Phase 6 & 7 Summary](reports/phase6_phase7_summary.md)**: Pipeline implementation and statistical analysis
- **[Sensitivity Analysis Report](reports/sensitivity_analysis_report.md)**: Robustness testing across 4 scenarios

### Validation Reports

- **[Validation Report v2 Relaxed](reports/validation_report_v2_relaxed.md)**: Final 95.9% pass rate
- **[Validation Report v1 Strict](reports/validation_report_v1_strict.md)**: Baseline 94.9% pass rate

---

## 🧪 Testing and Quality Assurance

### Test Suite

**Run Tests**: `pytest tests/ -v --cov=src`

| Test File | Tests | Purpose |
|:----------|:-----:|:--------|
| **test_schema.py** | 9 | Validate project layout, join spec, rule packs, Python version lock, nullable dtypes |
| **test_assumptions.py** | 5 | Data quality checks (missing values, outliers, dtypes) |

### Code Quality

**Linting**: `black src tests && ruff check src tests && mypy src`

- **black**: Auto-formatting (line length 100)
- **ruff**: Fast linting (replace flake8, isort, pyupgrade)
- **mypy**: Static type checking (Python 3.11+)

### CI/CD Pipelines

- **[tests.yml](.github/workflows/tests.yml)**: Python 3.11/3.12 matrix, pytest with coverage, codecov upload
- **[lint.yml](.github/workflows/lint.yml)**: black --check, ruff check, mypy, pre-commit

**Status**: All tests passing ✅, lint checks green ✅

---

## 📦 Submission Package Contents

### What's Included in `capstone_submission_v1.zip`

```
capstone_submission_v1/
├── README_SUBMISSION.md               # ⭐ Open this first
├── ACADEMIC_INTEGRITY.md              # Honor code statement
├── LICENSE                            # MIT License
│
├── proposal_task2.docx                # Final proposal (APA formatted)
├── results_section.docx               # Results write-up (APA formatted)
│
├── docs/                              # All documentation
├── reports/                           # All tables, figures, analysis
├── data/processed/                    # Final datasets (row-level + aggregated)
├── src/                               # All Python source code
├── resources/                         # Configuration and validation rules
├── tests/                             # Test suite
├── references/                        # BibTeX bibliography
│
├── pyproject.toml                     # Python project config
├── requirements.txt                   # Dependencies
├── Makefile                           # Automation tasks
└── .github/workflows/                 # CI/CD pipelines
```

**Total Size**: ~50 MB (including processed data, figures, documentation)

**Excluded** (too large, reproducible from source):
- `.venv/` (Python virtual environment - recreate with `python -m venv .venv`)
- `data/raw/` (source data - download with scripts or use processed data)
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/` (temporary build files)

---

## 🎓 Rubric Alignment Checklist

### Task 2 Requirements

| Requirement | File/Section | Status |
|:------------|:-------------|:------:|
| **A. Research Question** | [proposal_reference.md](docs/proposal_reference.md) § Research Question | ✅ |
| **B. Hypotheses** | [proposal_reference.md](docs/proposal_reference.md) § Hypotheses | ✅ |
| **C. Data Collection** | [data_sources.md](docs/data_sources.md) | ✅ |
| **D. Data Extraction** | [cleaning_plan.md](docs/cleaning_plan.md) § 10-Stage Workflow | ✅ |
| **E. Data Preparation** | [cleaning_plan.md](docs/cleaning_plan.md) § Sentinel Values, Nullable Dtypes | ✅ |
| **F. Data Analysis** | [metrics_spec.md](docs/metrics_spec.md) § Statistical Analysis Plan | ✅ |
| **G. Tool Justification** | [proposal_reference.md](docs/proposal_reference.md) § Tool Justification | ✅ |
| **H. IRB Status** | [proposal_reference.md](docs/proposal_reference.md) § IRB Status | ✅ |
| **I. APA References** | [references/apa.bib](references/apa.bib) | ✅ |

### Task 3 Requirements (Results)

| Requirement | File/Section | Status |
|:------------|:-------------|:------:|
| **A. Methods Summary** | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 1 | ✅ |
| **B. Results** | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 2-3 | ✅ |
| **C. Tables/Figures** | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 6 | ✅ |
| **D. Interpretation** | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 4 | ✅ |
| **E. Limitations** | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 4.5 | ✅ |
| **F. Recommendations** | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 5 | ✅ |

---

## 🚀 How to Reuse This Project

### For Other Rural Health Networks

This project provides immediately reusable artifacts:

1. **Validation Rule Packs** (`resources/rules/*.json`): 50+ rules adaptable to your data sources
2. **Join Specification** (`resources/join_spec.json`): Template for defining join keys and quality flags
3. **Processing Pipeline** (`src/pipeline/`): FHIR/XPT/CSV processors with extensible architecture
4. **Analysis Scripts** (`src/analysis/`): Bootstrap CIs, sensitivity analysis, table/figure generation
5. **CI/CD Pipelines** (`.github/workflows/`): Automated testing and linting

### Deployment Steps

See **[REUSABILITY_GUIDE.md](docs/REUSABILITY_GUIDE.md)** for detailed instructions on:
- Adapting validation rules to your data sources
- Configuring join keys for your use case
- Setting up AWS Lambda/Azure Functions deployment
- Estimating costs and performance

---

## 📞 Support and Contact

**Student**: Robert Miller  
**Student ID**: 000982134  
**Email**: robert.miller@wgu.edu  
**Program**: MSDA - Master of Science in Data Analytics  
**Institution**: Western Governors University

**Repository**: https://github.com/rcmiller01/wgu-capstone  
**Issues**: https://github.com/rcmiller01/wgu-capstone/issues

---

## 📄 License and Academic Integrity

This project is released under the **MIT License** (see [LICENSE](LICENSE)).

**Academic Integrity Statement**: This work represents my original research and analysis. All external sources are properly cited in APA 7th edition format. See [ACADEMIC_INTEGRITY.md](ACADEMIC_INTEGRITY.md) for full statement.

---

## 🎯 Next Steps for Reviewers

1. **Start with Proposal**: Read [proposal_reference.md](docs/proposal_reference.md) to understand research question and methods
2. **Review Results**: Read [phase8_results_writeup.md](reports/phase8_results_writeup.md) for complete findings
3. **Explore Data**: Check [cohort_fact_va_v2_relaxed.csv](data/processed/cohort_fact_va_v2_relaxed.csv) for final metrics
4. **Examine Tables/Figures**: View reports/table*.md and reports/figure*.png for visualizations
5. **Verify Reproducibility**: Run `pytest tests/` to confirm all tests pass
6. **Check Code Quality**: Run `make lint` to verify clean code standards

**Estimated Review Time**: 2-3 hours for thorough examination of all deliverables

---

**Document Version**: 1.0  
**Last Updated**: November 11, 2025  
**Status**: ✅ Ready for Submission
