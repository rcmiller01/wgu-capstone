# Metrics Specification

## Overview
This document defines all metrics computed in the `CohortFact_VA` table, including calculation methods, denominators, and data quality constraints.

**Target Grain**: Virginia (state_abbr='VA') × Month (period_id=YYYYMM)  
**Version**: 1.0.0  
**Last Updated**: 2025-11-11

---

## Metric Catalog

### 1. Synthea Metrics (from FHIR synthetic data)

#### 1.1 synthea_encounters
- **Definition**: Count of synthetic patient encounters in Virginia for the given month
- **Formula**: `COUNT(Encounter) WHERE state_abbr='VA' AND period_id=YYYYMM`
- **Data Type**: `Int64`
- **Denominator**: N/A (raw count)
- **Range**: `[0, ∞)`
- **Source**: Synthea FHIR Encounter resources
- **Derivation**:
  ```python
  encounters = df[
      (df['state_abbr'] == 'VA') & 
      (df['period_id'] == period_id)
  ].groupby(['state_abbr', 'period_id']).size()
  ```
- **Flags**: Set `low_precision_time=False` (Synthea has full datetime precision)

#### 1.2 synthea_dx_rate
- **Definition**: Diagnoses per 1,000 encounters
- **Formula**: `(COUNT(Condition) / COUNT(Encounter)) × 1000`
- **Data Type**: `Float64`
- **Denominator**: **Per 1,000 encounters** (NOT per patient)
- **Range**: `[0, ∞)` (can exceed 1000 if multiple diagnoses per encounter)
- **Source**: Synthea FHIR Condition and Encounter resources
- **Derivation**:
  ```python
  grouped = df.groupby(['state_abbr', 'period_id'])
  dx_count = grouped['condition_id'].count()
  encounter_count = grouped['encounter_id'].nunique()
  dx_rate = (dx_count / encounter_count) * 1000
  ```
- **QA Check**: If `encounter_count == 0`, set to `NULL` (avoid division by zero)

#### 1.3 synthea_lab_oob_rate
- **Definition**: Fraction of laboratory observations outside normal ranges
- **Formula**: `COUNT(Observation WHERE out_of_range=True) / COUNT(Observation WHERE category='laboratory')`
- **Data Type**: `Float64`
- **Denominator**: Total laboratory observations
- **Range**: `[0, 1]` (fraction/proportion)
- **Source**: Synthea FHIR Observation resources (category='laboratory')
- **Derivation**:
  ```python
  lab_obs = df[df['category'] == 'laboratory']
  grouped = lab_obs.groupby(['state_abbr', 'period_id'])
  oob_count = grouped['out_of_range'].sum()
  total_labs = grouped['observation_id'].count()
  oob_rate = oob_count / total_labs
  ```
- **Out-of-Range Logic**:
  - BMI (LOINC 39156-5): `value < 18.5 OR value > 30`
  - Systolic BP (LOINC 8480-6): `value < 90 OR value > 140`
  - Diastolic BP (LOINC 8462-4): `value < 60 OR value > 90`
  - Total Cholesterol (LOINC 2093-3): `value > 200 mg/dL`
  - HbA1c (LOINC 4548-4): `value > 6.5%`
- **QA Check**: If `total_labs == 0`, set to `NULL`

---

### 2. VDH Metrics (from Virginia Department of Health CSVs)

#### 2.1 vdh_case_rate_per_100k
- **Definition**: Disease case rate per 100,000 population
- **Formula**: `(SUM(case_count) / SUM(population)) × 100000`
- **Data Type**: `Float64`
- **Denominator**: **Per 100,000 population**
- **Range**: `[0, ∞)`
- **Source**: VDH case surveillance data
- **Derivation**:
  ```python
  def compute_rate_per_100k(count: int, population: int) -> float:
      if population == 0 or pd.isna(population):
          return np.nan
      return (count / population) * 100_000
  
  grouped = df.groupby(['state_abbr', 'period_id'])
  total_cases = grouped['case_count'].sum()
  total_pop = grouped['population'].sum()
  case_rate = compute_rate_per_100k(total_cases, total_pop)
  ```
- **Suppression Handling**:
  - If `case_count < 5`, set to `NA` (not zero)
  - Set `suppressed=True` flag
- **Flags**: `low_precision_time=True` if month unavailable (yearly data)

#### 2.2 vdh_hosp_rate_per_100k
- **Definition**: Hospitalization rate per 100,000 population
- **Formula**: `(SUM(hospitalization_count) / SUM(population)) × 100000`
- **Data Type**: `Float64`
- **Denominator**: **Per 100,000 population**
- **Range**: `[0, ∞)`
- **Source**: VDH hospitalization data
- **Derivation**: Same as `vdh_case_rate_per_100k` with `hospitalization_count`
- **Suppression Handling**: Same as case rate
- **QA Check**: `rate ≈ 100000 * count / pop` within 0.1 tolerance

---

### 3. NHANES Metrics (from National Health and Nutrition Examination Survey XPT files)

#### 3.1 nhanes_obesity_rate
- **Definition**: Obesity prevalence (BMI ≥ 30) projected to Virginia population via post-stratification
- **Formula**: `SUM(prevalence_stratum × VA_population_share_stratum)`
- **Data Type**: `Float64`
- **Denominator**: N/A (prevalence proportion, not rate)
- **Range**: `[0, 1]` (fraction/proportion)
- **Source**: NHANES BMX files (BMXBMI), DEMO files (survey weights)
- **Derivation** (Post-stratification):
  ```python
  # Step 1: Compute national prevalence by stratum
  strata = ['age_band', 'sex']  # minimum strata
  national_prev = {}
  for stratum in strata_combinations:
      subset = nhanes_df[matches_stratum(stratum)]
      weighted_obese = (subset['is_obese'] * subset['WTMEC2YR']).sum()
      weighted_total = subset['WTMEC2YR'].sum()
      national_prev[stratum] = weighted_obese / weighted_total
  
  # Step 2: Pull VA demographic margins (from ACS/VDH)
  va_margins = get_va_population_shares(strata)
  
  # Step 3: Post-stratify
  va_obesity_rate = sum(
      national_prev[s] * va_margins[s] 
      for s in strata_combinations
  )
  ```
- **Obesity Definition**: `BMI ≥ 30 kg/m²`
- **Survey Weights**: Use `WTMEC2YR` (exam weight)
- **Strata Used**: Minimum `age_band × sex`; add `race/ethnicity` if sample size allows
- **Temporal Assignment**: Assign same value to all months in covered years (2017-2020)
- **Flags**: `low_precision_time=True` (cycle-level, not monthly)
- **QA Checks**:
  - `sum(va_margins) == 1.0` (population shares sum to 100%)
  - Non-degenerate standard errors
  - Document strata used in metadata

#### 3.2 nhanes_smoking_rate
- **Definition**: Smoking prevalence projected to Virginia population via post-stratification
- **Formula**: Same post-stratification as obesity
- **Data Type**: `Float64`
- **Denominator**: N/A (prevalence proportion)
- **Range**: `[0, 1]`
- **Source**: NHANES SMQ files (smoking questionnaire), DEMO files
- **Derivation**: Same as `nhanes_obesity_rate` with smoking indicator
- **Smoking Definition**: Current smoker (SMQ020=1 "Do you now smoke cigarettes?")
- **Survey Weights**: Use `WTINT2YR` (interview weight, not exam)
- **Flags**: `low_precision_time=True`

---

### 4. NIH Metrics (from chest X-ray image metadata)

#### 4.1 nih_cxr_images
- **Definition**: Count of chest X-ray images with Virginia state information
- **Formula**: `COUNT(image_id) WHERE state_abbr='VA' AND period_id=YYYYMM`
- **Data Type**: `Int64` (nullable)
- **Denominator**: N/A (raw count)
- **Range**: `[0, ∞)` or `NULL`
- **Source**: NIH ChestX-ray14 metadata
- **Derivation**:
  ```python
  # Geo availability check
  geo_missing_pct = df['state'].isna().mean()
  if geo_missing_pct >= 0.8:
      # Omit from VA join
      nih_cxr_images = None
      nih_geo_limited = True
  else:
      # Aggregate where state available
      nih_cxr_images = df[
          (df['state_abbr'] == 'VA') & 
          (df['period_id'] == period_id)
      ].groupby(['state_abbr', 'period_id']).size()
  ```
- **Flags**: `nih_geo_limited=True` (always), `ambiguous_geo=True` if state missing

#### 4.2 nih_cxr_abnormal_rate
- **Definition**: Fraction of chest X-rays with abnormal findings
- **Formula**: `COUNT(finding_labels != 'No Finding') / COUNT(image_id)`
- **Data Type**: `Float64` (nullable)
- **Denominator**: Total images
- **Range**: `[0, 1]` or `NULL`
- **Source**: NIH ChestX-ray14 metadata (finding_labels)
- **Derivation**:
  ```python
  if nih_geo_limited or geo_missing_pct >= 0.8:
      nih_cxr_abnormal_rate = None
  else:
      subset = df[(df['state_abbr'] == 'VA') & (df['period_id'] == period_id)]
      abnormal_count = (subset['finding_labels'] != 'No Finding').sum()
      total_images = len(subset)
      nih_cxr_abnormal_rate = abnormal_count / total_images if total_images > 0 else None
  ```
- **Flags**: `nih_geo_limited=True`

---

## Validation Flags

### low_precision_time (UInt8: 0 or 1)
- **Set to 1 when**:
  - NHANES: Always (only cycle-level temporal data)
  - VDH: When month is unavailable (yearly data)
  - Synthea: Rare (if only year available; typically has full datetime)
  - NIH: When acquisition_date is missing
- **Set to 0 when**: Full month/day precision available

### ambiguous_geo (UInt8: 0 or 1)
- **Set to 1 when**:
  - State could not be confidently resolved
  - NIH: State field is NULL (expected for 80-100% of records)
  - Synthea: Patient address has only city, no state, and city not in VA city list
- **Set to 0 when**: State explicitly available and validated

### nih_geo_limited (UInt8: 0 or 1)
- **Set to 1 when**: Source is NIH (always)
- **Set to 0 when**: Source is Synthea, VDH, or NHANES

---

## Denominator Reference Table

| Metric | Denominator | Unit | Example Interpretation |
|--------|-------------|------|------------------------|
| `synthea_encounters` | N/A (count) | encounters | 1,234 encounters in VA in Jan 2020 |
| `synthea_dx_rate` | **Per 1,000 encounters** | diagnoses | 1,500 means 1.5 diagnoses per encounter |
| `synthea_lab_oob_rate` | Total labs | proportion | 0.15 means 15% of labs out of range |
| `vdh_case_rate_per_100k` | **Per 100,000 population** | cases | 50 means 50 cases per 100k people |
| `vdh_hosp_rate_per_100k` | **Per 100,000 population** | hospitalizations | 10 means 10 hospitalizations per 100k |
| `nhanes_obesity_rate` | N/A (prevalence) | proportion | 0.35 means 35% obesity prevalence |
| `nhanes_smoking_rate` | N/A (prevalence) | proportion | 0.18 means 18% smoking prevalence |
| `nih_cxr_images` | N/A (count) | images | 50 images or NULL |
| `nih_cxr_abnormal_rate` | Total images | proportion | 0.40 means 40% abnormal or NULL |

---

## Acceptance Tests

### Test 1: Uniqueness
```python
assert cohort_fact[['state_abbr', 'period_id']].duplicated().sum() == 0
assert cohort_fact['state_abbr'].notna().all()
assert cohort_fact['period_id'].notna().all()
```

### Test 2: Coverage
```python
# All VDH months must exist
vdh_months = get_vdh_month_range()
assert set(vdh_months).issubset(set(cohort_fact['period_id']))
```

### Test 3: Bounds
```python
# Rates must be non-negative
assert (cohort_fact['vdh_case_rate_per_100k'] >= 0).all(skipna=True)
assert (cohort_fact['vdh_hosp_rate_per_100k'] >= 0).all(skipna=True)

# Proportions must be in [0, 1]
assert cohort_fact['synthea_lab_oob_rate'].between(0, 1).all(skipna=True)
assert cohort_fact['nhanes_obesity_rate'].between(0, 1).all(skipna=True)
assert cohort_fact['nhanes_smoking_rate'].between(0, 1).all(skipna=True)
assert cohort_fact['nih_cxr_abnormal_rate'].between(0, 1).all(skipna=True)

# No infinities
assert not np.isinf(cohort_fact.select_dtypes(include=[np.number])).any().any()
```

### Test 4: Consistency
```python
# VDH rate calculation consistency
tolerance = 0.1
for _, row in cohort_fact.iterrows():
    if pd.notna(row['vdh_case_count']) and pd.notna(row['vdh_population']):
        expected_rate = (row['vdh_case_count'] / row['vdh_population']) * 100_000
        actual_rate = row['vdh_case_rate_per_100k']
        assert abs(actual_rate - expected_rate) < tolerance
```

### Test 5: Flag Consistency
```python
# NHANES always has low_precision_time
nhanes_rows = cohort_fact[cohort_fact['source_id'].str.contains('nhanes', case=False)]
assert (nhanes_rows['low_precision_time'] == 1).all()

# NIH always has nih_geo_limited
nih_rows = cohort_fact[cohort_fact['source_id'] == 'IMG_META']
assert (nih_rows['nih_geo_limited'] == 1).all()
```

---

## Provenance Metadata

For each metric in the final `CohortFact_VA` table:

```python
provenance = {
    'synthea_encounters': {
        'from_source': 'Synthea FHIR',
        'method': 'count',
        'denominator': 'N/A',
        'aggregation': 'sum over VA localities × month'
    },
    'synthea_dx_rate': {
        'from_source': 'Synthea FHIR',
        'method': 'ratio',
        'denominator': 'per 1,000 encounters',
        'aggregation': '(total diagnoses / total encounters) × 1000'
    },
    'vdh_case_rate_per_100k': {
        'from_source': 'VDH surveillance CSV',
        'method': 'standardized_rate',
        'denominator': 'per 100,000 population',
        'aggregation': '(sum cases / sum population) × 100000'
    },
    'nhanes_obesity_rate': {
        'from_source': 'NHANES XPT (BMX, DEMO)',
        'method': 'post_stratification',
        'denominator': 'prevalence proportion',
        'aggregation': 'sum(national_prevalence_stratum × VA_pop_share_stratum)',
        'strata': 'age_band × sex',
        'survey_weight': 'WTMEC2YR'
    }
}
```

---

## Quality Assurance Checklist

### Pre-Aggregation
- [ ] Remove Refused/Don't Know codes (NHANES: 7/77/777, 9/99/999)
- [ ] Normalize customer_id inputs (trim, uppercase) before HMAC hashing
- [ ] Filter Synthea to VA before heavy joins
- [ ] Set suppressed=True for VDH cells with n<5

### During Aggregation
- [ ] Use correct survey weights (NHANES: WTMEC2YR for exams, WTINT2YR for interviews)
- [ ] Apply consistent denominator per metric (see table above)
- [ ] Handle division by zero (set to NULL, not 0 or inf)
- [ ] Preserve flags through all transformations

### Post-Aggregation
- [ ] Run all 5 acceptance tests
- [ ] Verify no gaps in VDH month coverage
- [ ] Document actual strata used for NHANES post-stratification
- [ ] Compute and store standard errors for NHANES prevalence estimates
- [ ] Generate summary statistics (row count, month range, NA percentages)

---

## Implementation Notes

1. **Compute rates in single functions** to avoid drift:
   ```python
   def rate_per_100k(count, population):
       return (count / population) * 100_000 if population > 0 else np.nan
   ```

2. **Store intermediate counts/denominators** for QA:
   - Keep `vdh_case_count`, `vdh_population` alongside `vdh_case_rate_per_100k`
   - Keep `synthea_encounter_count`, `synthea_dx_count` alongside `synthea_dx_rate`

3. **Document all assumptions**:
   - VA city list for Synthea geographic mapping
   - LOINC codes and thresholds for lab out-of-range logic
   - Age bands and race/ethnicity categories for NHANES strata

---

**Version History**:
- v1.0.0 (2025-11-11): Initial specification

**See Also**:
- `resources/join_spec.json`
- `docs/cleaning_plan.md`
- `resources/rules/*.json`
