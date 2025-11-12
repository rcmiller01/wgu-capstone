# Metrics Specification - FINAL

**Document Status:** Final  
**Version:** 1.0  
**Date:** 2025-11-11  
**Project:** Serverless FHIR Data Pipeline Performance Study

---

## Overview

This document defines the dependent variables (metrics) used to evaluate serverless FHIR data pipeline performance. All metrics are derived from the cohort fact table (`cohort_fact_va.csv`) and measure operational efficiency, not clinical outcomes.

---

## Primary Metrics

### 1. Median End-to-End Latency (P50)

**Definition:** The 50th percentile of file processing time from S3 upload trigger to validation completion.

**Formula:**
```
P50_latency = QUANTILE(latency_sec, 0.50)
```

**Unit:** Seconds (s)  
**Denominator:** All successfully ingested files (validation_passed = TRUE or FALSE)  
**Target:** ≤ 30 seconds  
**Rationale:** Median represents typical case performance; less sensitive to outliers than mean

**Measurement:**
- **Numerator:** Sorted latency values at 50th percentile position
- **Denominator:** Total count of ingest runs (n=1,010)
- **Exclusions:** None (includes both passed and failed validations)

---

### 2. 95th Percentile Latency (P95)

**Definition:** The 95th percentile of file processing time; represents worst-case performance under normal conditions.

**Formula:**
```
P95_latency = QUANTILE(latency_sec, 0.95)
```

**Unit:** Seconds (s)  
**Denominator:** All successfully ingested files  
**Target:** ≤ 120 seconds (2 minutes)  
**Rationale:** Captures tail latency without being skewed by rare anomalies (P99, P99.9)

**Measurement:**
- **Numerator:** Sorted latency values at 95th percentile position
- **Denominator:** Total count of ingest runs (n=1,010)
- **Exclusions:** None

---

### 3. Validation Pass Rate

**Definition:** Proportion of ingested files that pass automated data quality validation checks.

**Formula:**
```
validation_pass_rate = COUNT(validation_passed = TRUE) / COUNT(all_files)
```

**Unit:** Proportion (0.00 to 1.00), reported as percentage  
**Denominator:** All files submitted for ingestion  
**Target:** ≥ 95.0%  
**Rationale:** Indicates data quality and validation rule appropriateness

**Measurement:**
- **Numerator:** Count of files with `validation_passed = TRUE` (n=969)
- **Denominator:** Total count of files processed (n=1,010)
- **Exclusions:** None (all ingest attempts counted)

**Validation Criteria (V2 Relaxed Policy):**
- Files fail only if:
  - Cannot derive temporal period (period_id) for any record
  - >5% of metric-critical rows unusable
  - Core schema broken (missing resourceType, id)
- Optional FHIR elements allowed; flagged with warnings (low_precision_time, ambiguous_geo)

---

## Secondary Metrics

### 4. Mean Latency by Data Source

**Definition:** Average processing time stratified by data source type (Synthea, NHANES, VDH).

**Formula:**
```
mean_latency_source = SUM(latency_sec) / COUNT(files) 
                      WHERE data_source = <source>
```

**Unit:** Seconds (s)  
**Denominator:** Files per data source  
**Purpose:** Identify performance differences across data formats (FHIR JSON vs XPT vs CSV)

**Measurement by Source:**
- **Synthea (FHIR):** numerator = sum of 1,000 latencies; denominator = 1,000
- **NHANES (XPT):** numerator = sum of 8 latencies; denominator = 8  
- **VDH (CSV):** numerator = sum of 2 latencies; denominator = 2

---

### 5. Mean File Size

**Definition:** Average file size in kilobytes, used to correlate with processing latency.

**Formula:**
```
mean_file_size_kb = SUM(file_size_kb) / COUNT(files)
```

**Unit:** Kilobytes (KB)  
**Denominator:** All processed files  
**Purpose:** Explanatory variable for latency; larger files expected to have longer processing times

**Measurement:**
- **Numerator:** Sum of file_size_kb for all records
- **Denominator:** Total count of files (n=1,010)
- **Exclusions:** None

---

## Denominators Summary Table

| Metric | Numerator | Denominator | Unit | Target |
|--------|-----------|-------------|------|--------|
| **P50 Latency** | Value at 50th percentile | All files (n=1,010) | seconds | ≤30s |
| **P95 Latency** | Value at 95th percentile | All files (n=1,010) | seconds | ≤120s |
| **Validation Pass Rate** | Files with validation_passed=TRUE (n=969) | All files (n=1,010) | proportion (%) | ≥95% |
| **Mean Latency (Source)** | Sum of latency_sec per source | Files per source | seconds | N/A |
| **Mean File Size** | Sum of file_size_kb | All files (n=1,010) | kilobytes | N/A |

---

## Statistical Analysis Plan

### Hypothesis 1: Processing Speed

**H₁:** Automated serverless pipeline reduces median processing time compared to manual entry.

- **Test:** Paired t-test (one-tailed)
- **Null Hypothesis (H₀):** μ_automated ≥ μ_manual (no improvement)
- **Alternative (H₁):** μ_automated < μ_manual (faster)
- **Alpha:** 0.05
- **Baseline:** Manual entry = 1200s (20 minutes) per record
- **Measured:** P50 automated = 16.12s

### Hypothesis 2: Validation Accuracy

**H₂:** Automated validation achieves higher accuracy than manual review.

- **Test:** McNemar's test (paired categorical)
- **Null Hypothesis (H₀):** p_automated = p_manual (no difference)
- **Alternative (H₁):** p_automated ≠ p_manual (different)
- **Alpha:** 0.05
- **Baseline:** Manual validation = 85% pass rate
- **Measured:** Automated validation = 95.9% pass rate

### Effect Size

- **Cohen's d:** (μ_manual - μ_automated) / σ_pooled
- **Purpose:** Quantify practical significance beyond statistical significance
- **Interpretation:** d > 0.8 = large effect

---

## Data Quality Flags

The following flags are carried forward from validation but do NOT cause file failure:

| Flag | Meaning | Impact on Metrics |
|------|---------|-------------------|
| `low_precision_time=1` | Only one temporal field present (e.g., period.start but not period.end) | Month derived from available field; warn in logs |
| `ambiguous_geo=1` | State derived from city/text, not explicit address.state | Excluded from VA geographic aggregates; counted in overall totals |
| `lab_oob_na=1` | Lab observation missing referenceRange | Excluded from lab_oob_rate numerator/denominator |

---

## Computation Examples

### Example 1: P50 Latency

```python
import pandas as pd

df = pd.read_parquet('data/processed/processed_data.parquet')
p50_latency = df['latency_sec'].quantile(0.50)
# Result: 16.12 seconds
```

### Example 2: Validation Pass Rate

```python
total_files = len(df)  # 1,010
passed_files = df['validation_passed'].sum()  # 969
pass_rate = passed_files / total_files  # 0.959 (95.9%)
```

### Example 3: Mean Latency by Source

```python
latency_by_source = df.groupby('data_source')['latency_sec'].mean()
# synthea: 20.46s
# nhanes: 5.63s
# vdh: 3.44s
```

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-11 | Final version. Fixed denominators, units, and validation policy references. |

---

**Document Status:** FINAL - Ready for submission
