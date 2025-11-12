# Capstone Submission Checklist

**Project**: Serverless FHIR Data Pipeline for Rural Healthcare  
**Student**: Robert Miller (000982134)  
**Date**: November 11, 2025  
**Status**: Pre-Submission Verification

---

## 📋 Task 2 (Proposal) Checklist

### Required Components

| Item | Requirement | File/Section | Complete |
|:-----|:------------|:-------------|:--------:|
| **A1** | Research question clearly stated | [proposal_reference.md](docs/proposal_reference.md) § Research Question | ✅ |
| **A2** | Research question is testable | Proposal § Hypotheses (H₀, H₁ with measurable variables) | ✅ |
| **B1** | Null hypothesis (H₀) stated | Proposal § Hypotheses | ✅ |
| **B2** | Alternative hypothesis (H₁) stated | Proposal § Hypotheses | ✅ |
| **B3** | Hypotheses align with research question | Both reference validation_pass_bool and latency_sec | ✅ |
| **C1** | Data sources identified | [data_sources.md](docs/data_sources.md) (Synthea, NHANES, VDH) | ✅ |
| **C2** | Data access described | URLs provided, download scripts included | ✅ |
| **C3** | Sample size justified | n=1,010 files sufficient for bootstrap CIs | ✅ |
| **D1** | Data extraction plan | [cleaning_plan.md](docs/cleaning_plan.md) § 10-Stage Workflow | ✅ |
| **D2** | Variables defined | [variables_table.md](docs/variables_table.md) (50+ variables) | ✅ |
| **D3** | Extraction tools specified | Python 3.11+, pandas, pyarrow, fhir.resources | ✅ |
| **E1** | Data preparation described | Cleaning Plan § Sentinel Values, Nullable Dtypes | ✅ |
| **E2** | Missing data handling | Cleaning Plan § Missing Data Policy (exclude vs. flag) | ✅ |
| **E3** | Outlier treatment | Cleaning Plan § Outlier Detection (1.5 × IQR) | ✅ |
| **F1** | Analytical method selected | Paired t-test (or Wilcoxon if non-normal) | ✅ |
| **F2** | Method matches hypotheses | Compares automated vs manual latency/accuracy | ✅ |
| **F3** | Statistical assumptions addressed | [metrics_spec.md](docs/metrics_spec.md) § Normality Checks | ✅ |
| **G1** | Tool selected (Python) | Proposal § Tool Justification | ✅ |
| **G2** | Tool capabilities justified | Python: pandas, scipy, Great Expectations, cloud integration | ✅ |
| **G3** | Tool appropriate for methods | Supports t-test, bootstrap, visualization | ✅ |
| **H** | IRB statement | Proposal § IRB Status (exempt - no human subjects) | ✅ |
| **I** | APA references | [references/apa.bib](references/apa.bib) (10+ sources) | ✅ |

**Task 2 Status**: ✅ All components present

---

## 📋 Task 3 (Results) Checklist

### Required Components

| Item | Requirement | File/Section | Complete |
|:-----|:------------|:-------------|:--------:|
| **A** | Methods summary | [phase8_results_writeup.md](reports/phase8_results_writeup.md) § 1 | ✅ |
| **A1** | Study design described | § 1.1 (quasi-experimental, 3 data sources) | ✅ |
| **A2** | Data sources recap | § 1.1 (Synthea, NHANES, VDH) | ✅ |
| **A3** | Variables defined | § 1.2 (validation_passed, latency_sec, file_size_kb) | ✅ |
| **A4** | Statistical methods | § 1.3 (bootstrap CIs, sensitivity analysis) | ✅ |
| **B** | Results presented | § 2 Performance Metrics | ✅ |
| **B1** | Descriptive statistics | § 2.1-2.2 (pass rates, latency P50/P95 by source) | ✅ |
| **B2** | Inferential statistics | § 2.1 (95.9% vs 95% target, 16.12s vs 30s target) | ✅ |
| **B3** | Hypotheses addressed | § 4.1 (H₁ confirmed - both metrics met targets) | ✅ |
| **C** | Tables and figures | § 6 Tables and Figures Summary | ✅ |
| **C1** | Appropriate visualizations | Table 1-5 (pass rates, latency, sensitivity), Figures 1-3 | ✅ |
| **C2** | Captions provided | § 6 (detailed captions for all tables/figures) | ✅ |
| **C3** | References in text | § 2.1-2.3 (references to "Table 1", "Figure 2", etc.) | ✅ |
| **D** | Interpretation | § 4 Interpretation and Discussion | ✅ |
| **D1** | Findings explained | § 4.1-4.3 (performance, calibration, format patterns) | ✅ |
| **D2** | Practical significance | § 4.4 (56-168x speedup vs manual) | ✅ |
| **D3** | Alignment with hypotheses | § 4.1 (all targets met, H₁ supported) | ✅ |
| **E** | Limitations | § 4.5 Limitations | ✅ |
| **E1** | Synthetic data | § 4.5.1 (Synthea is idealized, not real EHR) | ✅ |
| **E2** | Temporal aggregation | § 4.5.2 (file-level, not month-level) | ✅ |
| **E3** | Geographic scope | § 4.5.3 (Virginia-focused) | ✅ |
| **E4** | Cold start latency | § 4.5.4 (warm pipeline, production adds 1-5s) | ✅ |
| **E5** | Statistical power | § 4.5.5 (no true paired comparison) | ✅ |
| **F** | Recommendations | § 5 Conclusions, § 4 Recommendations for Implementation | ✅ |
| **F1** | Practical applications | § 5 (operational efficiency, data quality assurance) | ✅ |
| **F2** | Future research | § 4.5 (pilot on real data, temporal trends, multi-state) | ✅ |
| **F3** | Implementation guidance | § 4 Recommendations (calibrated validation, format SLAs) | ✅ |

**Task 3 Status**: ✅ All components present

---

## 📋 Deliverables Inventory

### Core Documents

- [x] **README_SUBMISSION.md** - Navigation hub for all deliverables
- [x] **proposal_reference.md** - Complete proposal with research question, hypotheses, methods, IRB
- [x] **phase8_results_writeup.md** - Complete results section (ready for DOCX conversion)
- [x] **phase8_completion_summary.md** - Executive summary of Phase 8 findings
- [ ] **proposal_task2.docx** - APA-formatted proposal for submission (needs conversion)
- [ ] **results_section.docx** - APA-formatted results for submission (needs conversion)

### Data Documentation

- [x] **data_sources.md** - Synthea, NHANES, VDH descriptions with URLs
- [x] **variables_table.md** - 50+ variables with types, ranges, descriptions
- [x] **data_dictionary_cohort_va.md** - Cohort fact table schema (7 columns)
- [x] **metrics_spec.md** - P50/P95 latency, validation pass rate definitions
- [x] **cleaning_plan.md** - 10-stage workflow with v1 vs v2 comparison
- [x] **methods_validation_policy.md** - v1 strict vs v2 relaxed validation rules

### Results and Analysis

- [x] **table1_pass_rates.md/.csv** - Validation pass rates (v1 vs v2) by source
- [x] **table2_latency_stats.md/.csv** - Processing latency (P50/P95) with 95% CI
- [x] **sensitivity_analysis_report.md** - Robustness testing (Tables 3-5)
- [x] **figure1_pass_rate_comparison.png** - Bar chart (v1 → v2)
- [x] **figure2_latency_dotwhisker.png** - Latency error bars (P50/P95)
- [x] **figure3_coverage_trends.png** - 4-panel dashboard
- [x] **phase6_phase7_summary.md** - Pipeline and analysis summary

### Code and Configuration

- [x] **src/pipeline/** - Data processing scripts (process_raw_data.py, data_cleaning.py, etc.)
- [x] **src/analysis/** - Statistical analysis (generate_phase7_outputs.py, sensitivity_analysis.py)
- [x] **resources/rules/*.json** - 50+ validation rules across 5 rule packs
- [x] **resources/join_spec.json** - Join keys, flags, aggregation logic
- [x] **tests/** - Test suite (test_schema.py, test_assumptions.py)
- [x] **pyproject.toml** - Python project config (version lock, dependencies)
- [x] **requirements.txt** - Pinned dependencies
- [x] **.github/workflows/** - CI/CD pipelines (tests.yml, lint.yml)

### Defense Materials

- [x] **DEFENSE_PRESENTATION.md** - 6-slide deck outline with talking points
- [x] **REUSABILITY_GUIDE.md** - One-page how-to-reuse guide for rural networks
- [x] **ACADEMIC_INTEGRITY.md** - Honor code statement

### Data Files

- [x] **data/processed/cohort_fact_va_v2_relaxed.csv** - Final aggregated metrics (4 rows)
- [x] **data/processed/processed_data.parquet** - Row-level data (1,010 records)
- [x] **data/processed/metadata.json** - Provenance metadata

**Total Files**: 40+ deliverables

---

## 📋 Quality Checks

### Documentation Quality

| Check | Status | Notes |
|:------|:------:|:------|
| All markdown files render correctly | ✅ | Viewed in VS Code markdown preview |
| Links work (relative paths) | 🔄 | **TO DO**: Verify all internal links |
| Tables formatted consistently | ✅ | All use markdown table syntax |
| Figures render correctly | ✅ | All PNG files viewable |
| Code blocks have syntax highlighting | ✅ | Language specified (python, json, powershell) |
| Grammar and spelling checked | 🔄 | **TO DO**: Run spell check on all .md files |
| APA references formatted | ✅ | BibTeX entries in references/apa.bib |

### Code Quality

| Check | Status | Command | Result |
|:------|:------:|:--------|:-------|
| All tests passing | ✅ | `pytest tests/ -v` | 9/9 passed |
| Black formatting | ✅ | `black --check src tests` | All files formatted |
| Ruff linting | ✅ | `ruff check src tests` | Clean (known exceptions documented) |
| Mypy type checking | ✅ | `mypy src` | No type errors |
| Coverage > 80% | ✅ | `pytest --cov=src` | 85% coverage |

### Reproducibility

| Check | Status | Notes |
|:------|:------:|:------|
| Virtual environment recreatable | ✅ | `python -m venv .venv && pip install -r requirements.txt` |
| All scripts executable | ✅ | `python -m src.pipeline`, `python src/analysis/*.py` |
| Data provenance documented | ✅ | metadata.json with seed=12345, generation date |
| Random seed consistent | ✅ | All scripts use seed=12345 |
| CI/CD passing | ✅ | GitHub Actions green on main branch |

---

## 📋 Submission Package Preparation

### Files to Include in ZIP

```
capstone_submission_v1/
├── README_SUBMISSION.md               ⭐ Open first
├── ACADEMIC_INTEGRITY.md
├── LICENSE
│
├── proposal_task2.docx                📄 For grading
├── results_section.docx               📄 For grading
│
├── docs/
│   ├── proposal_reference.md
│   ├── data_sources.md
│   ├── variables_table.md
│   ├── metrics_spec.md
│   ├── cleaning_plan.md
│   ├── methods_validation_policy.md
│   ├── DEFENSE_PRESENTATION.md
│   └── REUSABILITY_GUIDE.md
│
├── reports/
│   ├── phase8_results_writeup.md
│   ├── phase8_completion_summary.md
│   ├── table1_pass_rates.md/.csv
│   ├── table2_latency_stats.md/.csv
│   ├── sensitivity_analysis_report.md
│   ├── figure1_pass_rate_comparison.png
│   ├── figure2_latency_dotwhisker.png
│   └── figure3_coverage_trends.png
│
├── data/processed/
│   ├── cohort_fact_va_v2_relaxed.csv
│   ├── processed_data.parquet
│   └── metadata.json
│
├── src/                               Full source code
├── resources/                         Rules and join spec
├── tests/                             Test suite
├── references/                        BibTeX bibliography
│
├── pyproject.toml
├── requirements.txt
└── Makefile
```

### Files to EXCLUDE (too large, reproducible)

- `.venv/` - Python environment (recreate with `pip install -r requirements.txt`)
- `data/raw/` - Source data (download with scripts or use processed data)
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/` - Temporary files
- `.git/` - Git history (too large, available on GitHub)
- `*.pyc`, `*.pyo` - Compiled Python files

### ZIP Command

```powershell
# Create submission package
Compress-Archive -Path `
  README_SUBMISSION.md, `
  ACADEMIC_INTEGRITY.md, `
  LICENSE, `
  docs, `
  reports, `
  data/processed, `
  src, `
  resources, `
  tests, `
  references, `
  pyproject.toml, `
  requirements.txt, `
  Makefile `
  -DestinationPath capstone_submission_v1.zip
```

---

## 📋 Pre-Submission Actions

### Must Complete Before Submission

- [ ] **Convert to DOCX**: Use pandoc to create `proposal_task2.docx` and `results_section.docx`
  ```powershell
  pandoc docs/proposal_reference.md -o proposal_task2.docx --reference-doc=apa_template.docx
  pandoc reports/phase8_results_writeup.md -o results_section.docx --reference-doc=apa_template.docx
  ```

- [ ] **Insert Figures in DOCX**: Manually insert figure1.png, figure2.png, figure3.png at referenced locations

- [ ] **Apply APA Formatting**: Times New Roman 12pt, double spacing, running head, page numbers

- [ ] **Add Citations**: Convert in-text references to APA 7th edition with references/apa.bib

- [ ] **Spell Check**: Run grammar check on all DOCX files

- [ ] **Link Verification**: Click every link in README_SUBMISSION.md to ensure they work

- [ ] **Dry Run**: Extract ZIP, follow README_SUBMISSION.md steps, verify reproducibility

- [ ] **Create ZIP**: Run Compress-Archive command above

### Optional Enhancements

- [ ] Add screenshots of pipeline execution (CloudWatch logs, S3 buckets) for proposal
- [ ] Create 1-page visual summary (infographic) of key findings
- [ ] Record 2-minute demo video showing pipeline execution
- [ ] Create PowerPoint version of DEFENSE_PRESENTATION.md

---

## 📋 Rubric Self-Assessment

### Task 2 (Proposal)

| Criterion | Self-Rating | Confidence | Notes |
|:----------|:-----------:|:----------:|:------|
| Research Question | Competent | High | Clear, testable, aligns with MSDA program |
| Hypotheses | Competent | High | H₀ and H₁ with measurable variables |
| Data Sources | Competent | High | 3 sources, URLs, download scripts |
| Data Extraction | Competent | High | 10-stage workflow documented |
| Data Preparation | Competent | High | Missing data, outliers, sentinels |
| Analytical Method | Competent | High | Paired t-test with normality checks |
| Tool Justification | Competent | High | Python capabilities aligned to methods |
| IRB Statement | Competent | High | Exempt - no human subjects |
| APA References | Competent | Medium | 10+ sources, need formatting check |

**Predicted Grade**: Competent (all criteria met)

### Task 3 (Results)

| Criterion | Self-Rating | Confidence | Notes |
|:----------|:-----------:|:----------:|:------|
| Methods Summary | Competent | High | Complete recap in § 1 |
| Results | Competent | High | All metrics reported with CIs |
| Tables/Figures | Competent | High | 5 tables, 3 figures with captions |
| Interpretation | Competent | High | Performance, calibration, patterns |
| Limitations | Competent | High | 5 limitations honestly discussed |
| Recommendations | Competent | High | Practical + future research |

**Predicted Grade**: Competent (all criteria met)

---

## 📋 Defense Preparation

### Key Numbers to Memorize

- **95.9%** - Validation pass rate (target ≥95%)
- **16.12s** - Median latency P50 (target ≤30s)
- **42.06s** - Tail latency P95 (target ≤120s)
- **+1.1 pp** - v1→v2 improvement (94.9% → 95.9%)
- **56-168x** - Speedup vs manual entry
- **1,010** - Total files processed (1,000 Synthea, 8 NHANES, 2 VDH)
- **50+** - Validation rules across 5 rule packs
- **$10-15/month** - Cost for 1,000 files/day (vs $6,660 manual)

### 3-Minute Elevator Pitch

"Rural health networks struggle with slow manual data entry, taking 15-45 minutes per record. I built an automated serverless FHIR pipeline that processes health data in 16 seconds with 95.9% validation accuracy. The system uses AWS Lambda with 50+ validation rules across Synthea FHIR, NHANES, and VDH data sources. Key findings: validation pass rate 95.9% (exceeding 95% target), median latency 16 seconds (well below 30-second target), and 56-168x speedup versus manual entry. Sensitivity analysis confirmed robustness across data quality scenarios. The solution costs $10-15 per month for 1,000 files versus $6,660 for manual labor - a 99.8% cost reduction. All code, validation rules, and deployment guides are open-source and immediately reusable by other rural health networks."

### Anticipated Questions (Prepared Responses)

✅ Rule calibration (v1 → v2): See DEFENSE_PRESENTATION.md  
✅ Data quality flags: See DEFENSE_PRESENTATION.md  
✅ Serverless rationale: See DEFENSE_PRESENTATION.md  
✅ Speedup calculation: See DEFENSE_PRESENTATION.md  
✅ Limitations (synthetic data): See DEFENSE_PRESENTATION.md  

---

## 📋 Final Checklist (Day of Submission)

### Morning Of

- [ ] Final spell check on all DOCX files
- [ ] Verify ZIP file size < 100 MB (should be ~50 MB)
- [ ] Extract ZIP to temp folder, test README_SUBMISSION.md navigation
- [ ] Run `pytest tests/` one final time (all passing)
- [ ] Check GitHub repo status (all commits pushed)
- [ ] Print 1 copy of proposal_task2.docx for reference

### Submission

- [ ] Upload `capstone_submission_v1.zip` to WGU submission portal
- [ ] Submit `proposal_task2.docx` (if separate upload required)
- [ ] Submit `results_section.docx` (if separate upload required)
- [ ] Verify submission confirmation email received
- [ ] Note submission timestamp for records

### Post-Submission

- [ ] Create GitHub release tag `v1.0-submission`
- [ ] Archive local submission folder to external drive (backup)
- [ ] Schedule defense preparation time (review DEFENSE_PRESENTATION.md)
- [ ] Prepare any additional materials requested by evaluator

---

**Checklist Version**: 1.0  
**Last Updated**: November 11, 2025  
**Status**: Ready for Final Review

**Next Steps**: Complete "Must Complete Before Submission" section, then create ZIP package.
