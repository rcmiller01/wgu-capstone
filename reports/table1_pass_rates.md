# Table 1: Validation Pass Rates by Source

**Comparison: v1 (Strict) vs v2 (Relaxed/Calibrated)**

| data_source   | n_v1_strict   |   passed_v1_strict | rate_pct_v1_strict   | n_v2_relaxed   |   passed_v2_relaxed | rate_pct_v2_relaxed   | improvement_pct   |
|:--------------|:--------------|-------------------:|:---------------------|:---------------|--------------------:|:----------------------|:------------------|
| nhanes        | 8             |                  8 | 100.0%               | 8              |                   8 | 100.0%                | 0.0%              |
| synthea       | 1,000         |                948 | 94.8%                | 1,000          |                 959 | 95.9%                 | 1.1%              |
| vdh           | 2             |                  2 | 100.0%               | 2              |                   2 | 100.0%                | 0.0%              |

*Note: Higher pass rates in v2 reflect calibrated validation rules that allow optional FHIR elements and handle legitimate missingness.*
