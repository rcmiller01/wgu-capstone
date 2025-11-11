# Pipeline Execution Guide

## Prerequisites

1. **Python Environment**: Python 3.11+ with required packages installed
2. **Environment Variable**: Set `CAPSTONE_HMAC_SALT` for customer_id hashing
3. **Data Files**: Ensure all data sources are in `data/raw/` directories

## Setup

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Set Environment Variable

```powershell
$env:CAPSTONE_HMAC_SALT='your-secret-salt-value-here'
```

## Execution

### Run Full Pipeline

Execute all steps (1-3 from mitigation playbook):

```powershell
python src/pipeline/run_pipeline.py
```

This will:
1. Process Synthea FHIR bundles → `data/interim/synthea_va_month.parquet`
2. Process NHANES surveys → `data/interim/nhanes_va_month.parquet`
3. Process VDH CSVs → `data/interim/vdh_va_month.parquet`
4. Process NIH metadata → `data/interim/nih_va_month.parquet`
5. Build CohortFact_VA → `data/processed/cohort_fact_va.parquet`
6. Generate summary report → `reports/cohort_fact_summary.md`
7. Run validation tests → pytest output

### Run Individual Processors

**Synthea:**
```powershell
python src/pipeline/synthea_processor.py
```

**NHANES:**
```powershell
python src/pipeline/nhanes_processor.py
```

**VDH:**
```powershell
python src/pipeline/vdh_processor.py
```

**NIH:**
```powershell
python src/pipeline/nih_processor.py
```

**Build CohortFact_VA:**
```powershell
python src/pipeline/build_cohort_fact.py
```

**Generate Summary:**
```powershell
python src/analysis/generate_summary.py
```

### Run Tests

**Validation Tests:**
```powershell
pytest tests/test_cohort_fact_validation.py -v
```

**Customer ID Hash Tests:**
```powershell
pytest tests/test_customer_id_hash.py -v
```

**All Tests:**
```powershell
pytest tests/ -v
```

## Output Files

- **Interim Aggregates**: `data/interim/*_va_month.parquet` (one per source)
- **Final Table**: `data/processed/cohort_fact_va.parquet`
- **Summary Report**: `reports/cohort_fact_summary.md`

## Review Steps (After Execution)

1. **Check Summary Report**: Open `reports/cohort_fact_summary.md`
   - Row count: Should have ≥6 months
   - Month range: Should be contiguous
   - NA percentages: Expected per source limitations

2. **Validate Outputs**: Review pytest results
   - Uniqueness: No duplicate keys
   - Coverage: Contiguous period_ids
   - Bounds: Metrics within expected ranges
   - Consistency: Flags logically consistent

3. **Inspect Data**: Load parquet files for spot checks
   ```python
   import pandas as pd
   df = pd.read_parquet('data/processed/cohort_fact_va.parquet')
   print(df.head())
   ```

## Troubleshooting

### Error: "CAPSTONE_HMAC_SALT environment variable not set"
**Solution**: Set environment variable before running:
```powershell
$env:CAPSTONE_HMAC_SALT='your-secret-salt'
```

### Error: "FHIR directory not found"
**Solution**: Ensure Synthea data is in `data/raw/synthea/fhir/`

### Error: "NHANES directory not found"
**Solution**: Ensure NHANES cycles are in `data/raw/nhanes/2017-2018/` and `data/raw/nhanes/2019-2020/`

### Error: "pyreadstat not found"
**Solution**: Install missing package:
```powershell
pip install pyreadstat
```

### Error: Synthea processor taking too long
**Note**: Processing ~5000 JSON files takes time. First run may take 5-10 minutes.

## Next Steps (After Review)

If satisfied with summary report and validation tests:

1. Proceed to **Step 4** (Statistical Tests and Visualization)
2. Define statistical tests per requirements
3. Create visualization dashboards

## Notes

- **Synthea**: Processes ~5000 FHIR JSON files, filters to VA patients
- **NHANES**: Uses survey weights, post-stratifies to VA (simplified)
- **VDH**: Placeholder structure (actual VDH data would have temporal dimension)
- **NIH**: All NULL (no geographic data for VA)
- **Validation**: 5 acceptance tests from metrics_spec.md

## File Structure

```
data/
├── interim/              # Source aggregates (VA×month)
│   ├── synthea_va_month.parquet
│   ├── nhanes_va_month.parquet
│   ├── vdh_va_month.parquet
│   └── nih_va_month.parquet
└── processed/            # Final table
    └── cohort_fact_va.parquet

reports/
└── cohort_fact_summary.md  # Summary report for review

src/
├── pipeline/
│   ├── customer_id_hash.py       # HMAC-SHA256 hashing
│   ├── synthea_processor.py      # FHIR bundle parser
│   ├── nhanes_processor.py       # Survey processor
│   ├── vdh_processor.py          # VDH CSV processor
│   ├── nih_processor.py          # NIH metadata processor
│   ├── build_cohort_fact.py      # Multi-source join
│   └── run_pipeline.py           # Master runner
└── analysis/
    └── generate_summary.py       # Summary report generator

tests/
├── test_customer_id_hash.py      # Hash determinism tests
└── test_cohort_fact_validation.py  # Acceptance tests
```
