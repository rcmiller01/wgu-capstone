# WGU D610 Capstone — Phase Index

This document maps each capstone phase to its corresponding artifacts, documentation, and code. Use this as a roadmap to navigate the project structure.

---

## Phase 0: Topic Selection & Preliminary Research

**Status**: ✅ Complete  
**Deliverables**: Topic approval, initial literature review

**Artifacts**:
- [`docs/phase0_instructions.md`](phase0_instructions.md) — Phase guidelines
- [`docs/baseline_sources.md`](baseline_sources.md) — Literature review sources
- [`references/apa.bib`](../references/apa.bib) — Bibliography (APA format)

**Summary**: Selected topic of health data pipeline performance analysis with multi-source integration. Identified gap in comparative performance metrics for serverless FHIR processing architectures.

---

## Phase 1: Proposal Development

**Status**: ✅ Complete  
**Deliverables**: Formal proposal document

**Artifacts**:
- [`docs/phase1_instructions.md`](phase1_instructions.md) — Phase guidelines
- [`docs/proposal_reference.md`](proposal_reference.md) — Proposal template reference
- Root: `Capstone Proposal Model Template 2.htm` — Final submitted proposal

**Summary**: Formalized research question, methodology, and data sources. Established evaluation criteria for pipeline performance (latency, validation accuracy).

---

## Phase 2: Data Collection & Ethics Review

**Status**: ✅ Complete  
**Deliverables**: Data acquisition plan, ethics review

**Artifacts**:
- [`docs/phase2_instructions.md`](phase2_instructions.md) — Phase guidelines
- [`docs/privacy_ethics.md`](privacy_ethics.md) — Ethics & privacy considerations
- [`docs/data_sources.md`](data_sources.md) — Data source documentation
- [`src/pipeline/data_acquisition.py`](../src/pipeline/data_acquisition.py) — Acquisition code

**Summary**: Identified four data sources (Synthea, NHANES, VDH, NIH). Established ethics framework for synthetic/public data use. No IRB required (no human subjects).

---

## Phase 3: Data Cleaning & Preparation

**Status**: ✅ Complete  
**Deliverables**: Cleaned datasets, data dictionary

**Artifacts**:
- [`docs/phase3_instructions.md`](phase3_instructions.md) — Phase guidelines
- [`docs/cleaning_plan.md`](cleaning_plan.md) — Cleaning methodology
- [`docs/variables_table.md`](variables_table.md) — Variable definitions
- [`src/pipeline/data_cleaning.py`](../src/pipeline/data_cleaning.py) — Cleaning code
- [`src/pipeline/synthea_processor.py`](../src/pipeline/synthea_processor.py) — FHIR parser
- [`src/pipeline/nhanes_processor.py`](../src/pipeline/nhanes_processor.py) — NHANES processor
- [`src/pipeline/build_cohort_fact.py`](../src/pipeline/build_cohort_fact.py) — Data integration
- [`data/processed/cohort_fact_va.csv`](../data/processed/cohort_fact_va.csv) — Final dataset
- [`reports/schema_profile.md`](../reports/schema_profile.md) — Data dictionary

**Summary**: Cleaned and standardized data from all sources. Created `CohortFact_VA` table at Virginia × month grain. Validated schema compliance.

---

## Phase 4-5: Exploratory Data Analysis (EDA)

**Status**: ✅ Complete (merged phases)  
**Deliverables**: EDA report, descriptive statistics

**Artifacts**:
- [`src/analysis/run_eda.py`](../src/analysis/run_eda.py) — EDA code
- [`src/analysis/data_profiler.py`](../src/analysis/data_profiler.py) — Profiling utilities
- [`notebooks/01_exploratory_data_analysis.ipynb`](../notebooks/01_exploratory_data_analysis.ipynb) — Interactive EDA
- [`reports/DATA_SUMMARY.md`](../reports/DATA_SUMMARY.md) — Summary report

**Summary**: Explored data distributions, missing patterns, and outliers. Documented variable transformations. Identified key covariates for analysis.

---

## Phase 6: Statistical Analysis Planning

**Status**: ✅ Complete  
**Deliverables**: Analysis plan, hypothesis specifications

**Artifacts**:
- [`docs/phase6_instructions.md`](phase6_instructions.md) — Phase guidelines
- [`docs/metrics_spec.md`](metrics_spec.md) — Metrics definitions
- [`src/analysis/run_statistical_tests.py`](../src/analysis/run_statistical_tests.py) — Test implementations
- [`notebooks/02_statistical_analysis.ipynb`](../notebooks/02_statistical_analysis.ipynb) — Interactive analysis

**Summary**: Defined primary outcome (validation pass rate) and secondary outcomes (latency, coverage). Specified statistical tests (chi-square, t-test, ANOVA).

---

## Phase 7: Analysis Execution & Results

**Status**: ✅ Complete  
**Deliverables**: Statistical results, publication-ready figures/tables

**Artifacts**:
- [`docs/phase7_instructions.md`](phase7_instructions.md) — Phase guidelines
- [`src/analysis/generate_phase7_outputs.py`](../src/analysis/generate_phase7_outputs.py) — Output generator
- [`reports/figures/publication/`](../reports/figures/) — Publication figures
  - `figure1_passrate.png` — Pass rate comparison
  - `figure2_latency.png` — Latency distribution
  - `figure3_coverage.png` — Data coverage heatmap
- [`reports/tables/`](../reports/tables/) — Statistical tables
- [`reports/phase6_phase7_summary.md`](../reports/phase6_phase7_summary.md) — Combined summary

**Summary**: Executed planned analyses. Found significant differences in pass rates between sources (χ²=45.2, p<0.001). Latency showed right-skewed distribution (median=2.3s).

---

## Phase 8: Results Interpretation & Write-Up

**Status**: ✅ Complete  
**Deliverables**: Results interpretation, discussion of findings

**Artifacts**:
- [`reports/phase8_results_writeup.md`](../reports/phase8_results_writeup.md) — Formal write-up
- [`reports/phase8_completion_summary.md`](../reports/phase8_completion_summary.md) — Phase summary
- [`notebooks/03_visualization_dashboard.ipynb`](../notebooks/03_visualization_dashboard.ipynb) — Interactive dashboard

**Summary**: Interpreted statistical results in context of research questions. Discussed implications for pipeline design. Identified limitations (synthetic data, temporal resolution).

---

## Phase 9-10: Final Deliverables & Presentation

**Status**: ✅ Complete (merged phases)  
**Deliverables**: Final report, presentation slides, repository submission

**Artifacts**:
- [`reports/phase9_phase10_summary.md`](../reports/phase9_phase10_summary.md) — Final summary
- Root: [`README.md`](../README.md) — Repository documentation
- [`docs/PIPELINE_EXECUTION.md`](PIPELINE_EXECUTION.md) — Technical documentation
- All code in [`src/`](../src/) — Reproducible pipeline

**Summary**: Finalized all deliverables. Repository configured for grading with deterministic outputs. Documentation complete for reproducibility.

---

## Supporting Documentation

### Technical Documentation
- [`docs/PIPELINE_EXECUTION.md`](PIPELINE_EXECUTION.md) — Detailed pipeline guide
- [`docs/IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) — Code architecture
- [`resources/join_spec.json`](../resources/join_spec.json) — Data join specification
- [`resources/rules/*.json`](../resources/rules/) — Validation rules

### Configuration Files
- [`pyproject.toml`](../pyproject.toml) — Tool configuration (black, ruff, pytest)
- [`requirements.txt`](../requirements.txt) — Python dependencies (pinned)
- [`.pre-commit-config.yaml`](../.pre-commit-config.yaml) — Pre-commit hooks
- [`Makefile`](../Makefile) — Automation targets

### Quality Assurance
- [`tests/test_schema.py`](../tests/test_schema.py) — Schema validation tests
- [`tests/test_assumptions.py`](../tests/test_assumptions.py) — Statistical assumption tests
- [`tests/test_cohort_fact_validation.py`](../tests/test_cohort_fact_validation.py) — Data integrity tests
- [`.github/workflows/`](../.github/workflows/) — CI/CD configuration

---

## Quick Navigation

| Need to... | Look here |
|------------|-----------|
| **Understand project scope** | [`README.md`](../README.md) |
| **Run the pipeline** | [`docs/PIPELINE_EXECUTION.md`](PIPELINE_EXECUTION.md) |
| **See data definitions** | [`docs/metrics_spec.md`](metrics_spec.md) |
| **View statistical results** | [`reports/phase6_phase7_summary.md`](../reports/phase6_phase7_summary.md) |
| **Check data quality** | [`reports/schema_profile.md`](../reports/schema_profile.md) |
| **Review code architecture** | [`docs/IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) |
| **Understand ethics considerations** | [`docs/privacy_ethics.md`](privacy_ethics.md) |
| **Reproduce analysis** | `make all` (see [`Makefile`](../Makefile)) |

---

## Artifact Checklist for Grading

- [ ] **Phase 0-1**: Proposal document (`.htm` file in root)
- [ ] **Phase 2**: Ethics review ([`docs/privacy_ethics.md`](privacy_ethics.md))
- [ ] **Phase 3**: Cleaned data ([`data/processed/cohort_fact_va.csv`](../data/processed/cohort_fact_va.csv))
- [ ] **Phase 3**: Data dictionary ([`reports/schema_profile.md`](../reports/schema_profile.md))
- [ ] **Phase 4-5**: EDA report ([`reports/DATA_SUMMARY.md`](../reports/DATA_SUMMARY.md))
- [ ] **Phase 6**: Analysis plan ([`docs/metrics_spec.md`](metrics_spec.md))
- [ ] **Phase 7**: Statistical results ([`reports/phase6_phase7_summary.md`](../reports/phase6_phase7_summary.md))
- [ ] **Phase 7**: Figures ([`reports/figures/publication/*.png`](../reports/figures/))
- [ ] **Phase 8**: Results write-up ([`reports/phase8_results_writeup.md`](../reports/phase8_results_writeup.md))
- [ ] **Phase 9-10**: Final repository ([`README.md`](../README.md))
- [ ] **Code**: Reproducible pipeline ([`src/`](../src/))
- [ ] **Tests**: Passing test suite (`make test`)

---

**Last Updated**: 2025-11-12  
**Repository**: [rcmiller01/wgu-capstone](https://github.com/rcmiller01/wgu-capstone)
