# Cohort Data Dictionary - Virginia FHIR Pipeline

**Document Status:** Final  
**Version:** 1.0  
**Date:** 2025-11-11  
**Artifact:** `data/processed/cohort_fact_va.csv`

---

## Overview

This data dictionary documents the cohort fact table used for statistical analysis of serverless FHIR data pipeline performance. The table contains aggregated metrics by data source, derived from 1,010 individual file processing runs.

**Data Lineage:**
1. Raw data: NHANES XPT files, Synthea FHIR JSON, VDH CSV files
2. Processing: `src/pipeline/process_raw_data.py`
3. Aggregation: `src/pipeline/generate_cohort_summary.py`
4. Output: `data/processed/cohort_fact_va.csv`

---

## Schema Specification

### Row-Level Data (processed_data.parquet)

**File:** `data/processed/processed_data.parquet`  
**Rows:** 1,010  
**Columns:** 6

| Column Name | Data Type | Description | Valid Values | Nullable |
|-------------|-----------|-------------|--------------|----------|
| `data_source` | object (string) | Source system identifier | 'synthea', 'nhanes', 'vdh' | No |
| `file_name` | object (string) | Original filename processed | Any valid filename | No |
| `file_size_kb` | float64 | File size in kilobytes | >0.0 | No |
| `latency_sec` | float64 | End-to-end processing latency in seconds | >0.0, typically <600 | No |
| `validation_passed` | bool | Whether file passed validation checks | True, False | No |
| `processing_date` | object (ISO 8601 string) | Timestamp of processing run | ISO 8601 datetime | No |

**Primary Key:** None (flat event log)  
**Foreign Keys:** None

---

### Aggregated Cohort Table (cohort_fact_va.csv)

**File:** `data/processed/cohort_fact_va.csv`  
**Rows:** 4 (3 data sources + 1 aggregate row)  
**Columns:** 7

| Column Name | Data Type | Description | Formula | Unit |
|-------------|-----------|-------------|---------|------|
| `data_source` | string | Source system identifier ('nhanes', 'synthea', 'vdh', 'ALL') | Grouping variable | categorical |
| `n_records` | int64 | Count of files processed from this source | COUNT(*) per source | count |
| `mean_latency_sec` | float64 | Average processing latency | MEAN(latency_sec) | seconds |
| `p50_latency_sec` | float64 | Median processing latency (50th percentile) | QUANTILE(latency_sec, 0.50) | seconds |
| `p95_latency_sec` | float64 | 95th percentile latency | QUANTILE(latency_sec, 0.95) | seconds |
| `validation_pass_rate` | float64 | Proportion passing validation | SUM(validation_passed) / COUNT(*) | proportion (0.0-1.0) |
| `mean_file_size_kb` | float64 | Average file size | MEAN(file_size_kb) | kilobytes |

**Primary Key:** `data_source`  
**Foreign Keys:** None

**Special Rows:**
- `data_source = 'ALL'`: Aggregate across all sources (total population)

---

## Column Definitions (Detailed)

### 1. data_source

**Type:** Categorical string  
**Purpose:** Stratification variable for subgroup analysis

**Valid Values:**
- `'nhanes'`: National Health and Nutrition Examination Survey (XPT format)
- `'synthea'`: Synthetic patient records (FHIR R4 JSON)
- `'vdh'`: Virginia Department of Health public datasets (CSV)
- `'ALL'`: Aggregate across all sources

**Cardinality:** 4 unique values (3 sources + aggregate)

**Analysis Use:**
- Subgroup analysis by data format type
- Forest plots stratified by source
- Latency comparison across structured vs semi-structured data

---

### 2. n_records

**Type:** Integer (count)  
**Purpose:** Sample size per stratum

**Range:** 2 to 1,010
- NHANES: 8
- Synthea: 1,000
- VDH: 2
- ALL: 1,010

**Statistical Use:**
- Denominator for proportions (validation_pass_rate)
- Sample size for subgroup power calculations
- Weighting factor for meta-analysis

**Constraints:** >0; sum of sources equals 'ALL' row

---

### 3. mean_latency_sec

**Type:** Float (continuous)  
**Unit:** Seconds

**Purpose:** Average processing time per source

**Formula:**
```
mean_latency_sec = SUM(latency_sec) / n_records
```

**Range:** 3.44 to 20.46 seconds (observed)

**Interpretation:**
- Lower values indicate faster processing
- Expected to correlate with file_size_kb
- Varies by data format complexity (CSV < XPT < FHIR JSON)

---

### 4. p50_latency_sec

**Type:** Float (continuous)  
**Unit:** Seconds

**Purpose:** Median processing time (primary dependent variable)

**Formula:**
```
p50_latency_sec = QUANTILE(latency_sec, 0.50)
```

**Range:** 3.44 to 16.16 seconds (observed)

**Target:** ≤30 seconds

**Statistical Properties:**
- Robust to outliers (vs mean)
- Represents typical case performance
- Used in paired t-test for H₁

---

### 5. p95_latency_sec

**Type:** Float (continuous)  
**Unit:** Seconds

**Purpose:** Tail latency metric (worst-case under normal conditions)

**Formula:**
```
p95_latency_sec = QUANTILE(latency_sec, 0.95)
```

**Range:** 4.09 to 42.06 seconds (observed)

**Target:** ≤120 seconds (2 minutes)

**Interpretation:**
- 95% of files process faster than this threshold
- Excludes rare outliers (P99, P99.9)
- Service-level agreement (SLA) boundary

---

### 6. validation_pass_rate

**Type:** Float (proportion)  
**Unit:** Dimensionless (0.0 to 1.0), reported as percentage

**Purpose:** Data quality metric (secondary dependent variable)

**Formula:**
```
validation_pass_rate = SUM(validation_passed == TRUE) / n_records
```

**Range:** 0.959 to 1.000 (observed)
- NHANES: 1.000 (100%)
- Synthea: 0.959 (95.9%)
- VDH: 1.000 (100%)
- ALL: 0.959 (95.9%)

**Target:** ≥0.95 (95%)

**Validation Criteria (V2 Relaxed):**
- Files fail only if core schema broken or >5% metric rows unusable
- Optional FHIR elements allowed with warnings
- See `docs/methods_validation_policy.md` for full policy

---

### 7. mean_file_size_kb

**Type:** Float (continuous)  
**Unit:** Kilobytes (KB)

**Purpose:** Explanatory variable for latency regression

**Formula:**
```
mean_file_size_kb = SUM(file_size_kb) / n_records
```

**Range:** 20.42 to 3,569.44 KB (observed)
- NHANES: 20.42 KB (small XPT tables)
- VDH: 249.82 KB (aggregated CSV)
- Synthea: 3,569.44 KB (large FHIR bundles)

**Expected Relationship:**
- Positive correlation with latency (larger files → longer processing)
- Non-linear (overhead cost + size-dependent cost)

---

## Data Quality Constraints

### Mandatory Fields
All 7 columns must be present; no NULL values allowed in cohort table.

### Range Checks
- `n_records` > 0
- `mean_latency_sec` > 0
- `p50_latency_sec` > 0
- `p95_latency_sec` ≥ p50_latency_sec (percentile ordering)
- `validation_pass_rate` ∈ [0.0, 1.0]
- `mean_file_size_kb` > 0

### Referential Integrity
- `data_source = 'ALL'` row: `n_records` = sum of source-specific rows

### Precision
- Latency metrics: rounded to 2 decimal places
- Validation rate: rounded to 4 decimal places (0.9594 → 95.94%)
- File size: rounded to 2 decimal places

---

## Example Rows

```csv
data_source,n_records,mean_latency_sec,p50_latency_sec,p95_latency_sec,validation_pass_rate,mean_file_size_kb
nhanes,8,5.63,5.94,6.59,1.0,20.42
synthea,1000,20.46,16.16,42.06,0.959,3569.44
vdh,2,3.44,3.44,4.09,1.0,249.82
ALL,1010,20.31,16.12,41.56,0.959,3534.76
```

---

## Usage Notes

### Statistical Analysis
- Use `p50_latency_sec` and `p95_latency_sec` for hypothesis testing
- Use `validation_pass_rate` for McNemar's test
- Use `data_source` for subgroup/stratified analysis

### Reproducibility
- Data generated with random seed 12345
- Processing date: 2025-11-11
- Pipeline version: See `data/processed/metadata.json`

### Limitations
- Synthea data is synthetic (realistic structure, not real patients)
- Small sample sizes for NHANES (n=8) and VDH (n=2)
- Validation rules simulate production FHIR validation logic

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-11 | Final freeze. 6 columns in row-level data, 7 columns in cohort aggregate. |

---

**Document Status:** FINAL - Schema frozen for analysis
