# Phase 3 Instructions: Data Acquisition and Cleaning Pipeline

**Issue**: #4  
**Status**: In Progress  
**Goal**: Acquire all data sources, generate synthetic data, implement cleaning pipeline with quality validation

---

## Overview

Phase 3 transforms data sources from documentation to actual datasets ready for analysis:

1. **Data Acquisition**: Download public datasets + generate Synthea synthetic records
2. **Data Cleaning**: Handle missingness, outliers, format inconsistencies, validation failures
3. **Quality Metrics**: Track completeness, validity, consistency across raw → interim → processed
4. **Data Lineage**: Document transformations and quality checkpoints

This phase delivers the **actual data** needed for timing tests and statistical analysis.

---

## Task 1: Data Acquisition Strategy

### Objective

Document download procedures and generate synthetic data for all four sources.

### Data Sources Checklist

#### Source 1: Synthea Synthetic Health Records

**Method**: Generate using Synthea CLI

**Steps**:
1. Install Java 11+ (prerequisite for Synthea)
2. Download Synthea JAR from GitHub releases
3. Generate N=5,000 patient records with Virginia demographics
4. Export as FHIR JSON format
5. Store in `data/raw/synthea/`

**Command Template**:
```bash
java -jar synthea-with-dependencies.jar -p 5000 -s 12345 --exporter.fhir.export=true --exporter.baseDirectory=./output Virginia
```

**Configuration**:
- Population: 5,000 patients (balances realism with compute cost)
- Seed: 12345 (reproducibility)
- State: Virginia (aligns with VDH geographic context)
- Format: FHIR JSON (target format for pipeline)

**Expected Output**:
- ~5,000 patient JSON files in `data/raw/synthea/fhir/`
- File size: ~500 MB - 2 GB total
- Complexity distribution: Mix of simple (demographics) to complex (multi-year encounters)

---

#### Source 2: NHANES (National Health and Nutrition Examination Survey)

**Method**: Download via CDC FTP

**Target Cycles**: 2017-2018, 2019-March 2020 (most recent complete data)

**Components to Download**:
- Demographics (DEMO_J.XPT, DEMO_K.XPT)
- Examination (BMX_J.XPT, BMX_K.XPT - body measures)
- Laboratory (TCHOL_J.XPT, TCHOL_K.XPT - cholesterol)
- Questionnaire (BPQ_J.XPT, BPQ_K.XPT - blood pressure)

**Download URLs**:
- 2017-2018: `https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/[COMPONENT].XPT`
- 2019-2020: `https://wwwn.cdc.gov/Nchs/Nhanes/2019-2020/[COMPONENT].XPT`

**Storage**: `data/raw/nhanes/`

**Expected Output**:
- 8 XPT files (4 components × 2 cycles)
- ~100-500 MB total
- ~2,000-5,000 participant records per cycle

**Conversion**: XPT → CSV using Python `xport` or `pandas` library

---

#### Source 3: Virginia Department of Health Data Portal

**Method**: Download via Socrata API or web portal

**Target Datasets**:
1. **COVID-19 Cases by Health District**: County-level aggregates
2. **Chronic Disease Indicators**: Diabetes, hypertension prevalence by district
3. **Health Professional Shortage Areas**: Rural health access metrics

**Download URLs**:
- Portal: `https://data.virginia.gov/browse?tags=health`
- API: `https://data.virginia.gov/resource/[dataset-id].json`

**Storage**: `data/raw/vdh/`

**Expected Output**:
- 3-5 CSV files
- ~10-50 MB total
- County/district level aggregates (N=500-1,000 rows total)

**API Access**: Optional API token for bulk downloads (free registration)

---

#### Source 4: NIH Chest X-Ray Dataset

**Method**: Download subset from Kaggle or NIH Box

**Target Subset**: 1,000-5,000 images (random sample from 112,120 total)

**Download Options**:
- **Kaggle**: `kaggle datasets download -d nih-chest-xrays/data` (requires Kaggle account + API key)
- **NIH Box**: Manual download from `https://nihcc.app.box.com/v/ChestXray-NIHCC`

**Storage**: `data/raw/nih_xray/`

**Expected Output**:
- 1,000-5,000 PNG images
- `Data_Entry_2017.csv` (metadata file)
- ~5-20 GB total

**Sampling Strategy**: Stratified by pathology label to ensure class balance

---

### Data Acquisition Script

**File**: `src/pipeline/data_acquisition.py`

**Functions**:
1. `generate_synthea_data(n_patients, seed, output_dir)`: Run Synthea generator
2. `download_nhanes_data(cycles, components, output_dir)`: Fetch NHANES XPT files
3. `download_vdh_data(datasets, output_dir)`: Query Socrata API or download CSVs
4. `download_nih_xray_sample(n_images, output_dir)`: Sample and download images

**Usage**:
```bash
python -m src.pipeline.data_acquisition --all
# or individually:
python -m src.pipeline.data_acquisition --synthea --n-patients 5000
python -m src.pipeline.data_acquisition --nhanes --cycles 2017-2018,2019-2020
```

**Logging**: Track download status, file sizes, record counts to `data/acquisition_log.txt`

---

## Task 2: Data Cleaning Strategy

### Objective

Transform raw data into validated, analysis-ready datasets with documented quality metrics.

### Cleaning Pipeline Stages

#### Stage 1: Schema Validation

**Purpose**: Ensure data matches expected structure before processing

**Checks**:
- Required columns present
- Data types correct (numeric, string, date, boolean)
- Primary keys unique (patient_id, record_id, image_id)
- Foreign key integrity (e.g., encounter_id references valid patient_id)

**Tool**: Great Expectations
- Define expectations suite for each data source
- Auto-generate data docs showing validation results
- Fail-fast on critical schema violations

**Output**: `data/interim/[source]_schema_validated/`

---

#### Stage 2: Missingness Handling

**Purpose**: Address missing values with explicit policy

**Policies by Variable Type**:

1. **Primary Keys** (patient_id, record_id): **DROP** (cannot analyze without ID)
2. **Dependent Variables** (latency_sec, validation_pass_bool): **DROP** (outcome required for analysis)
3. **Independent Variables**:
   - **data_source**: DROP (stratification variable - must be known)
   - **record_complexity**: IMPUTE as "unknown" category
   - **file_size_kb**: IMPUTE with median (unlikely missing, but fallback)
4. **Clinical/Survey Data**:
   - **Numerical** (BMI, cholesterol): IMPUTE with median (or mark as "missing" flag)
   - **Categorical** (diagnosis codes): IMPUTE with "Not Recorded" category
   - **Dates**: DROP record if critical (e.g., encounter_date), else impute or flag

**Documentation**: Log missingness rates before/after imputation in `data/quality_report.md`

**Code Example**:
```python
def handle_missingness(df, policy):
    # Track before
    missing_before = df.isnull().sum()
    
    # Apply policy
    if policy == 'drop':
        df = df.dropna(subset=critical_cols)
    elif policy == 'median':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif policy == 'category':
        df[cat_cols] = df[cat_cols].fillna('Unknown')
    
    # Track after
    missing_after = df.isnull().sum()
    
    # Log
    log_missingness(missing_before, missing_after)
    return df
```

---

#### Stage 3: Outlier Detection and Treatment

**Purpose**: Identify extreme values that may indicate errors or anomalies

**Methods**:

1. **Z-Score Method**: Flag values >3 SD from mean
2. **IQR Method**: Flag values outside [Q1 - 1.5×IQR, Q3 + 1.5×IQR]
3. **Domain Rules**: Flag clinically impossible values (e.g., age=300, BMI=5)

**Treatment Options**:
- **Cap/Winsorize**: Replace outliers with 1st/99th percentile
- **Flag and Keep**: Add `is_outlier` boolean column, retain value
- **Drop**: Remove record if multiple extreme values suggest data corruption

**Application**:
- **Latency (latency_sec)**: Flag >3 SD (likely Lambda timeout or system error), investigate separately
- **File Size (file_size_kb)**: Cap at 99th percentile (prevents mega-file skew)
- **Clinical Values**: Use domain rules (e.g., systolic BP 50-250 mmHg)

**Output**: `data/interim/[source]_outliers_flagged/`

---

#### Stage 4: Format Standardization

**Purpose**: Ensure consistent formats across heterogeneous sources

**Transformations**:

1. **Date Formats**: ISO 8601 (YYYY-MM-DD) for all sources
2. **Numeric Precision**: Round to 2 decimals (latency to 0.01 sec)
3. **String Casing**: Lowercase for categorical variables (avoids "Male" ≠ "male")
4. **Boolean Encoding**: True/False (not 1/0, Y/N, yes/no)
5. **Missing Indicators**: Standardize to `None` (not "NA", "NULL", "", NaN variations)

**Code Example**:
```python
def standardize_formats(df):
    # Dates
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Numeric
    df['latency_sec'] = df['latency_sec'].round(2)
    
    # Categorical
    df['data_source'] = df['data_source'].str.lower()
    
    # Boolean
    df['validation_pass_bool'] = df['validation_pass_bool'].astype(bool)
    
    return df
```

---

#### Stage 5: FHIR Validation (Synthea Specific)

**Purpose**: Ensure generated Synthea FHIR resources conform to specification

**Validator**: HAPI FHIR Validator CLI

**Checks**:
- Resource type valid (Patient, Encounter, Observation, etc.)
- Required elements present (e.g., Patient.identifier)
- Reference integrity (Encounter.subject → Patient.id)
- Terminology bindings (CodeableConcept uses valid code systems)
- Cardinality rules (e.g., Patient.name 1..*)

**Command**:
```bash
java -jar hapi-fhir-validator-cli.jar -v r4 -f data/raw/synthea/fhir/*.json
```

**Output**: Validation report with error/warning counts

**Treatment**: Move invalid resources to `data/interim/synthea_invalid/` for investigation

---

### Data Cleaning Script

**File**: `src/pipeline/data_cleaning.py` (expand existing stub)

**Functions**:
1. `validate_schema(df, source, expectations_suite)`: Schema checks with Great Expectations
2. `handle_missingness(df, policy_dict)`: Apply missingness policies
3. `detect_outliers(df, method, columns)`: Flag or treat outliers
4. `standardize_formats(df)`: Normalize dates, strings, booleans
5. `validate_fhir_resources(fhir_dir)`: Run HAPI validator on FHIR JSON

**Pipeline Orchestration**:
```python
def clean_data_source(source_name):
    # Load raw
    df_raw = load_raw_data(source_name)
    
    # Stage 1: Schema
    df = validate_schema(df_raw, source_name)
    
    # Stage 2: Missingness
    df = handle_missingness(df, MISSINGNESS_POLICY)
    
    # Stage 3: Outliers
    df = detect_outliers(df, method='iqr', columns=NUMERIC_COLS)
    
    # Stage 4: Formats
    df = standardize_formats(df)
    
    # Save interim
    save_interim(df, source_name)
    
    # Quality report
    generate_quality_report(df, source_name)
    
    return df
```

**Usage**:
```bash
python -m src.pipeline.data_cleaning --source synthea
python -m src.pipeline.data_cleaning --all
```

---

## Task 3: Quality Metrics and Data Lineage

### Objective

Track data quality across pipeline stages with transparency and auditability.

### Quality Metrics to Track

**Completeness**:
- `missing_rate = (missing_cells / total_cells) × 100`
- Track before/after imputation
- Threshold: <20% missing for critical variables

**Validity**:
- `schema_compliance = (valid_records / total_records) × 100`
- FHIR validation pass rate
- Threshold: ≥95% valid

**Consistency**:
- Format standardization success rate
- Date parsing errors
- Threshold: 100% parseable

**Uniqueness**:
- Duplicate primary key rate
- Threshold: 0% duplicates

**Accuracy** (proxy measures):
- Outlier rate (% flagged as extreme)
- Domain rule violation rate (e.g., negative age)
- Threshold: <5% outliers

### Quality Report Format

**File**: `data/quality_report.md`

**Template**:
```markdown
# Data Quality Report

**Generated**: 2025-11-10 14:32:15
**Pipeline Version**: 1.0.0

## Summary

| Source | Records (Raw) | Records (Clean) | Dropped (%) | Missing Rate (%) | Outliers (%) | Validation Pass (%) |
|--------|---------------|-----------------|-------------|------------------|--------------|---------------------|
| Synthea | 5,000 | 4,847 | 3.1% | 8.2% | 2.4% | 97.3% |
| NHANES | 9,254 | 8,891 | 3.9% | 12.5% | 1.8% | 100% |
| VDH | 873 | 873 | 0% | 5.1% | 0% | 100% |
| NIH X-Ray | 2,500 | 2,495 | 0.2% | 0.3% | 0% | 99.8% |
| **TOTAL** | **17,627** | **17,106** | **3.0%** | **7.9%** | **1.6%** | **98.8%** |

## Detailed Findings

### Synthea
- **Schema Issues**: 12 records missing Patient.identifier (dropped)
- **Missingness**: Observation.value[x] missing in 8.2% (median imputed)
- **Outliers**: 121 records with Encounter.period >365 days (flagged, kept)
- **FHIR Validation**: 141 warnings (non-critical terminology bindings)

### NHANES
[...]
```

### Data Lineage Tracking

**Purpose**: Document all transformations from raw → interim → processed

**Approach**: Data lineage log file

**File**: `data/lineage_log.jsonl` (JSON Lines format for append-only logging)

**Log Entry Schema**:
```json
{
  "timestamp": "2025-11-10T14:32:15Z",
  "source": "synthea",
  "stage": "outlier_detection",
  "input_path": "data/interim/synthea_missing_handled/",
  "output_path": "data/interim/synthea_outliers_flagged/",
  "records_in": 4859,
  "records_out": 4847,
  "records_dropped": 12,
  "drop_reason": "Multiple outliers (>3 variables >3 SD)",
  "transformation": "IQR outlier flagging + drop if >3 outliers",
  "parameters": {"method": "iqr", "threshold": 1.5}
}
```

**Visualization**: Generate lineage DAG (Directed Acyclic Graph) showing:
- Raw sources → Interim stages → Processed dataset
- Record counts at each node
- Drop/impute/transform operations as edges

**Tool**: Use `graphviz` or `mermaid` to render lineage diagram

---

## Task 4: Directory Structure and Documentation

### Data Directory Layout

```
data/
├── raw/                          # Original downloaded/generated data (READ-ONLY)
│   ├── synthea/
│   │   ├── fhir/                # FHIR JSON files (1 per patient)
│   │   └── metadata.json        # Generation parameters (seed, n_patients)
│   ├── nhanes/
│   │   ├── 2017-2018/           # XPT files by cycle
│   │   ├── 2019-2020/
│   │   └── README.md            # Component descriptions
│   ├── vdh/
│   │   ├── covid_cases.csv
│   │   ├── chronic_disease.csv
│   │   └── hpsa_data.csv
│   └── nih_xray/
│       ├── images/              # PNG files
│       └── Data_Entry_2017.csv  # Metadata
│
├── interim/                      # Intermediate cleaning stages
│   ├── synthea_schema_validated/
│   ├── synthea_missing_handled/
│   ├── synthea_outliers_flagged/
│   ├── nhanes_converted_csv/    # XPT → CSV
│   ├── nhanes_missing_handled/
│   └── [...]                    # Each source × cleaning stage
│
├── processed/                    # Final analysis-ready datasets
│   ├── combined_data.parquet    # All sources merged with IVs/DVs
│   ├── train_test_split.parquet # If needed for ML validation
│   └── stratified_samples.parquet # Stratified by data_source, complexity
│
├── acquisition_log.txt           # Download/generation timestamps and status
├── quality_report.md             # Quality metrics summary
├── lineage_log.jsonl             # Transformation audit trail
└── README.md                     # Data dictionary and usage guide
```

### Data README Template

**File**: `data/README.md`

**Sections**:
1. **Overview**: What data is here and purpose
2. **Data Sources**: Links to original sources and acquisition dates
3. **Directory Structure**: Explanation of raw/interim/processed
4. **Usage**:
   - How to regenerate data (`make data` or `python -m src.pipeline.data_acquisition`)
   - How to clean data (`python -m src.pipeline.data_cleaning`)
5. **Quality Metrics**: Link to quality_report.md
6. **Data Dictionary**: Variable names, types, descriptions (link to `variables_table.md`)
7. **Reproducibility**: Seeds, versions, checksums

---

## Completion Criteria

Phase 3 is complete when:

- ✅ All 4 data sources acquired:
  - Synthea: 5,000 patients generated with seed 12345
  - NHANES: 2017-2020 cycles downloaded and converted to CSV
  - VDH: 3+ datasets downloaded (county/district aggregates)
  - NIH: 1,000-5,000 images sampled with metadata

- ✅ Data cleaning pipeline implemented in `src/pipeline/data_cleaning.py`:
  - Schema validation (Great Expectations)
  - Missingness handling (policy-based)
  - Outlier detection (IQR/Z-score)
  - Format standardization
  - FHIR validation (Synthea)

- ✅ Quality metrics tracked:
  - `data/quality_report.md` generated with completeness, validity, consistency metrics
  - All sources meet thresholds (≥95% valid, <20% missing critical vars, <5% outliers)

- ✅ Data lineage documented:
  - `data/lineage_log.jsonl` logs all transformations
  - README explains raw → interim → processed flow

- ✅ Final datasets ready in `data/processed/`:
  - Combined dataset with all sources, stratification variables, DVs/IVs
  - N ≥ 800-1,000 records for statistical power

- ✅ Code is runnable:
  - `python -m src.pipeline.data_acquisition --all` succeeds
  - `python -m src.pipeline.data_cleaning --all` succeeds
  - Scripts are idempotent (can re-run safely)

---

## Rubric Alignment

**WGU D610 Capstone Rubric Requirements:**

| Criterion | Phase 3 Coverage |
|-----------|------------------|
| **B1: Data Collection** | Data acquisition scripts document how all 4 sources are obtained |
| **B2: Data Preparation** | Cleaning pipeline handles missingness, outliers, format standardization |
| **C1: Data Quality** | Quality report with completeness, validity, consistency metrics |
| **C2: Reproducibility** | Seeds, versions, lineage logging ensure reproducibility |
| **D2: Limitations** | Quality report identifies data limitations (missingness, outliers, validity issues) |

---

**Next Steps After Phase 3:**
- Phase 4: Detailed statistical methods (normality checks, paired t-test procedure)
- Phase 5: Tooling justification (Python vs. R vs. SAS)
- Phase 6: Full repo scaffold (Makefile, environment files, CI checks)

---

**Status**: Ready to begin data acquisition and cleaning  
**Priority**: Generate Synthea data first (longest running task ~30 min for 5k patients)
