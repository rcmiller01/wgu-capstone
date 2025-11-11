# Data Cleaning Plan

## Overview
This document specifies cleaning operations for all data sources to conform to the target schema defined in `resources/join_spec.json`. Each source requires dtype enforcement, column renaming, geographic/temporal derivations, PHI handling, and validation.

**Target Grain**: `state_month_va` (Virginia × YYYYMM period)  
**Common Keys**: `state_abbr`, `period_id`, `source_id`, `schema_variant`

---

## 1. Synthea (FHIR JSON)

### Dtype Locks
```python
# Patient Resource
{
    "id": "string",
    "name.family": "string",
    "name.given[0]": "string",
    "gender": "category",  # enum: male|female|other|unknown
    "birthDate": "datetime64[ns]",
    "address.state": "category",
    "address.city": "string",
    "address.postalCode": "string",
    "maritalStatus.text": "category"
}

# Encounter Resource
{
    "id": "string",
    "status": "category",  # enum: finished|in-progress|cancelled
    "class.code": "category",  # enum: AMB|EMER|IMP|ACUTE|VR
    "period.start": "datetime64[ns]",
    "period.end": "datetime64[ns]",
    "subject.reference": "string"
}

# Observation Resource
{
    "id": "string",
    "status": "category",  # enum: final|preliminary|amended
    "code.coding[0].code": "string",  # LOINC
    "valueQuantity.value": "float64",
    "valueQuantity.unit": "string",
    "effectiveDateTime": "datetime64[ns]"
}

# Condition Resource
{
    "id": "string",
    "code.coding[0].code": "string",  # SNOMED CT
    "code.coding[0].display": "string",
    "onsetDateTime": "datetime64[ns]",
    "clinicalStatus.coding[0].code": "category"
}
```

### Column Renames
```
Patient.id → patient_id
Patient.address[0].state → raw_state
Encounter.period.start → encounter_date
Observation.effectiveDateTime → observation_date
Condition.onsetDateTime → condition_onset_date
```

### Derivations
**state_abbr**:
```python
# Extract from Patient.address[0].state
# Force uppercase, validate against US state codes
# Filter: state_abbr == 'VA' OR remap all to 'VA' if needed
df['state_abbr'] = df['raw_state'].str.upper()
df = df[df['state_abbr'] == 'VA']
```

**period_id**:
```python
# From Encounter.period.start, Observation.effectiveDateTime, etc.
df['period_id'] = df['encounter_date'].dt.strftime('%Y%m')
# Set low_precision_time = False (full datetime available)
```

**customer_id** (HMAC hash):
```python
import hmac, hashlib, os
salt = os.getenv('CAPSTONE_HMAC_SALT')
df['customer_id'] = df['patient_id'].apply(
    lambda pid: hmac.new(salt.encode(), pid.encode(), hashlib.sha256).hexdigest()
)
```

### Drop Rules
**PHI-Sensitive** (even though synthetic):
- `name.family`, `name.given`
- `address.line` (keep state/city only)
- `telecom` (phone, email)
- Raw `patient_id` (replace with `customer_id`)

**Redundant**:
- `resourceType` (tracked in schema_variant)
- `fullUrl` (internal FHIR reference)

### Range Checks
```python
# Age validation (derived from birthDate)
age = (datetime.now() - df['birthDate']).dt.days / 365.25
assert age.between(0, 120).all(), "Invalid ages detected"

# Gender enum
assert df['gender'].isin(['male', 'female', 'other', 'unknown']).all()

# Observation values (example: BMI)
bmi_obs = df[df['loinc_code'] == '39156-5']
assert bmi_obs['value'].between(10, 80).all(), "BMI out of range"

# Blood pressure (example: systolic)
sbp_obs = df[df['loinc_code'] == '8480-6']
assert sbp_obs['value'].between(60, 250).all(), "SBP out of range"
```

### Enum Sets
```python
encounter_status = ['finished', 'in-progress', 'cancelled', 'entered-in-error']
encounter_class = ['AMB', 'EMER', 'IMP', 'ACUTE', 'NONAC', 'VR']
observation_status = ['final', 'preliminary', 'amended', 'cancelled', 'corrected']
condition_status = ['active', 'recurrence', 'relapse', 'inactive', 'remission', 'resolved']
```

### Null-Handling Policy
- **Required (fail if null)**: `patient_id`, `birthDate`, `gender`, `address.state`
- **Optional (allow null)**: `maritalStatus`, `address.postalCode`, `telecom`
- **Temporal nulls**: Set `low_precision_time = True` if only year available (rare in Synthea)
- **Value nulls**: For Observations, allow null `valueQuantity` if `valueCodeableConcept` present

---

## 2. VDH (CSV)

### Dtype Locks
```python
# Health Opportunity Index
{
    "locality": "string",
    "fips_code": "string",  # keep as string (leading zeros)
    "health_opportunity_index": "float64",
    "education_score": "float64",
    "social_economic_score": "float64",
    "physical_environment_score": "float64",
    "community_safety_score": "float64",
    "population": "int64",
    "median_household_income": "int64",
    "poverty_rate": "float64",
    "year": "int64"
}

# Virginia WIC
{
    "locality": "string",
    "fips_code": "string",
    "report_year": "int64",
    "report_month": "int64",  # nullable
    "total_participants": "int64",
    "women_participants": "int64",
    "infants_participants": "int64",
    "children_participants": "int64"
}
```

### Column Renames
```
locality → locality_name
fips_code → locality_fips
health_opportunity_index → hoi_score
report_year → year
report_month → month
```

### Derivations
**state_abbr**:
```python
# All VDH data is Virginia localities
df['state_abbr'] = 'VA'
```

**period_id**:
```python
# For HOI: year only → YYYY01 + low_precision_time flag
df['period_id'] = df['year'].astype(str) + '01'
df['low_precision_time'] = True

# For WIC: year + month if available
df['period_id'] = df['year'].astype(str) + df['month'].astype(str).str.zfill(2)
df['low_precision_time'] = df['month'].isna()
df.loc[df['month'].isna(), 'period_id'] = df['year'].astype(str) + '01'
```

### Drop Rules
**Redundant**:
- Internal row IDs if present
- Duplicate locality identifiers (keep `fips_code` as primary)

**PHI**: None (aggregated geographic data)

### Range Checks
```python
# HOI scores (0-100 scale)
assert df['hoi_score'].between(0, 100).all()
assert df['education_score'].between(0, 100).all()

# Population (VA locality range)
assert df['population'].between(1000, 2_000_000).all()

# Poverty rate (0-100%)
assert df['poverty_rate'].between(0, 100).all()

# WIC participants (non-negative)
assert (df['total_participants'] >= 0).all()
assert (df['women_participants'] >= 0).all()

# Month validation
assert df['month'].isna() | df['month'].between(1, 12)

# Year validation
assert df['year'].between(2015, 2025).all()
```

### Enum Sets
```python
# FIPS codes must start with '51' (Virginia)
assert df['fips_code'].str.startswith('51').all()

# 133 Virginia localities (95 counties + 38 cities)
valid_localities = 133  # validate against reference list
```

### Null-Handling Policy
- **Required (fail if null)**: `locality_name`, `fips_code`, `year`
- **Optional (allow null)**: `month` (annual data), individual metric columns (suppressed for small counts)
- **Temporal nulls**: Set `low_precision_time = True` when `month` is null
- **Suppressed counts**: WIC participants may be null/0 for small localities (privacy protection)

---

## 3. NHANES (XPT)

### Dtype Locks
```python
# DEMO files
{
    "SEQN": "int64",  # keep but drop before output
    "SDDSRVYR": "int64",  # cycle: 10=2017-18, 11=2019-20
    "RIDSTATR": "category",  # 1=interview, 2=interview+exam
    "RIAGENDR": "category",  # 1=male, 2=female
    "RIDAGEYR": "int64",
    "RIDRETH3": "category",  # race/ethnicity
    "DMDEDUC2": "category",  # education
    "INDFMPIR": "float64",  # income-to-poverty ratio
    "WTINT2YR": "float64",  # interview weight
    "WTMEC2YR": "float64",  # exam weight
    "SDMVPSU": "int64",  # PSU for variance
    "SDMVSTRA": "int64"  # stratum for variance
}

# BMX files
{
    "SEQN": "int64",
    "BMXWT": "float64",  # weight (kg)
    "BMXHT": "float64",  # height (cm)
    "BMXBMI": "float64",  # BMI
    "BMXWAIST": "float64"  # waist circumference
}

# TCHOL files
{
    "SEQN": "int64",
    "LBXTC": "float64",  # total cholesterol (mg/dL)
    "LBDTCSI": "float64"  # total cholesterol (mmol/L)
}

# BPQ files
{
    "SEQN": "int64",
    "BPQ020": "category",  # told high BP (1=yes, 2=no, 7=refused, 9=don't know)
    "BPQ080": "category",  # told high cholesterol
    "BPQ090D": "category"  # prescribed cholesterol meds
}
```

### Column Renames
```
SEQN → respondent_id (drop later)
SDDSRVYR → cycle_code
RIDAGEYR → age_years
RIAGENDR → gender_code
BMXWT → weight_kg
BMXHT → height_cm
BMXBMI → bmi
LBXTC → total_cholesterol_mg_dl
BPQ020 → has_high_bp
WTMEC2YR → survey_weight
```

### Derivations
**state_abbr**:
```python
# NHANES has NO state-level geography
# Use survey weights to project national estimates to VA
df['state_abbr'] = 'VA'  # proxy designation
df['is_weighted_proxy'] = True
```

**period_id**:
```python
# Derive from cycle code (no exact dates)
cycle_map = {10: '201701', 11: '201901'}  # map to first month of cycle
df['period_id'] = df['cycle_code'].map(cycle_map)
df['low_precision_time'] = True  # only year-level precision
```

### Drop Rules
**PHI-Sensitive**:
- `SEQN` (respondent ID - drop after merging datasets)

**Refused/Don't Know codes** (recode or filter):
- Values 7, 77, 777 (Refused)
- Values 9, 99, 999 (Don't Know)
- Option 1: Convert to NaN
- Option 2: Create separate flag column

**Redundant**:
- `LBDTCSI` (keep mg/dL version only)
- Comment codes (BMIWT, BMIHT, etc. - keep data columns only)

### Range Checks
```python
# Age (0-80, top-coded at 80)
assert df['age_years'].between(0, 80).all()

# BMI (physiologically plausible)
assert df['bmi'].between(10, 80).all() | df['bmi'].isna()

# Weight (kg)
assert df['weight_kg'].between(20, 250).all() | df['weight_kg'].isna()

# Height (cm)
assert df['height_cm'].between(50, 230).all() | df['height_cm'].isna()

# Total cholesterol (mg/dL)
assert df['total_cholesterol_mg_dl'].between(50, 600).all() | df['total_cholesterol_mg_dl'].isna()

# Survey weights (must be positive)
assert (df['survey_weight'] > 0).all() | df['survey_weight'].isna()
```

### Enum Sets
```python
# Cycle codes
valid_cycles = [10, 11]  # 2017-2018, 2019-2020

# Gender codes
valid_gender = [1, 2]  # 1=male, 2=female

# Interview/exam status
valid_status = [1, 2]  # 1=interview only, 2=both

# Race/ethnicity (RIDRETH3)
valid_race = [1, 2, 3, 4, 6, 7]

# Yes/No/Refused/Don't Know
valid_ynrdk = [1, 2, 7, 9]
```

### Null-Handling Policy
- **Required (fail if null)**: `SEQN`, `cycle_code`, `age_years`, `gender_code`, `survey_weight`
- **Optional (allow null)**: BMI, cholesterol, blood pressure (exam data ~10-20% missing)
- **Skip patterns**: Many questionnaire items have high missingness (50-70%) due to age/eligibility filters
- **Refused/Don't Know**: Convert codes 7/77/777 and 9/99/999 to NaN, track in separate flag column
- **Temporal nulls**: Always set `low_precision_time = True` (no exact dates available)

---

## 4. NIH (Image Metadata)

### Dtype Locks
```python
{
    "image_id": "string",
    "patient_id": "string",  # if available
    "acquisition_date": "datetime64[ns]",  # if available
    "finding_labels": "string",  # pipe-separated list
    "patient_age": "int64",
    "patient_gender": "category",
    "view_position": "category",  # PA|AP|LATERAL
    "image_width": "int64",
    "image_height": "int64",
    "state": "category"  # RARELY available
}
```

### Column Renames
```
Patient ID → patient_id
Finding Labels → finding_labels
Patient Age → patient_age
Patient Gender → patient_gender
View Position → view_position
```

### Derivations
**state_abbr**:
```python
# NIH chest X-ray data LACKS geography
# Most records will not have state information
df['state_abbr'] = df['state'].fillna('UNKNOWN')
df['ambiguous_geo'] = df['state'].isna()
df['nih_geo_limited'] = True  # flag for all NIH rows
```

**period_id**:
```python
# From acquisition_date if available
df['period_id'] = df['acquisition_date'].dt.strftime('%Y%m')
df.loc[df['acquisition_date'].isna(), 'period_id'] = 'UNKNOWN'
df['low_precision_time'] = df['acquisition_date'].isna()
```

### Drop Rules
**PHI-Sensitive**:
- `patient_id` (if real patient data; likely de-identified already)

**Redundant**:
- Raw image paths (keep metadata only)
- Duplicate metadata fields

### Range Checks
```python
# Age (newborn to elderly)
assert df['patient_age'].between(0, 110).all() | df['patient_age'].isna()

# Image dimensions (reasonable X-ray sizes)
assert df['image_width'].between(500, 5000).all()
assert df['image_height'].between(500, 5000).all()
```

### Enum Sets
```python
# Gender
valid_gender = ['M', 'F', 'O', 'U']  # male, female, other, unknown

# View position
valid_views = ['PA', 'AP', 'LATERAL', 'LL', 'RL']

# Finding labels (common findings)
common_findings = [
    'No Finding', 'Atelectasis', 'Cardiomegaly', 'Effusion', 
    'Infiltration', 'Mass', 'Nodule', 'Pneumonia', 'Pneumothorax'
]
```

### Null-Handling Policy
- **Required (fail if null)**: `image_id`, `finding_labels`
- **Optional (allow null)**: `acquisition_date`, `patient_age`, `state` (EXPECTED to be null)
- **Temporal nulls**: Set `low_precision_time = True` when `acquisition_date` is null
- **Geographic nulls**: Set `ambiguous_geo = True` and `nih_geo_limited = True` when `state` is null
- **Expected missingness**: 80-100% of records will lack `state` and many will lack `acquisition_date`

---

## Cross-Source Validation

### Unified Schema Checks
After cleaning, all sources must conform to:
```python
required_columns = [
    'state_abbr',           # category
    'period_id',            # string (YYYYMM)
    'source_id',            # category (CSV|FHIR|IMG_META)
    'schema_variant',       # category
    'low_precision_time',   # boolean
    'ambiguous_geo',        # boolean
    'nih_geo_limited'       # boolean (NIH only)
]
```

### Data Quality Flags Summary
```python
# Flag assignment rules:
# - low_precision_time: True if only year available (NHANES always, VDH sometimes, NIH often)
# - ambiguous_geo: True if state could not be confidently resolved (NIH mostly)
# - nih_geo_limited: True for all NIH records (geography not in dataset)
```

### Merge Key Validation
```python
# Before aggregation to state_month grain:
# 1. Verify state_abbr is valid US state code or 'VA'
# 2. Verify period_id matches regex: ^\d{6}$ (YYYYMM)
# 3. Verify source_id in allowed set
# 4. Remove duplicates on natural key combinations
```

---

## Implementation Checklist

### Phase 1: Extract
- [ ] Load Synthea FHIR JSON bundles (5,000 files)
- [ ] Load VDH CSVs (2 files)
- [ ] Load NHANES XPT files (8 files)
- [ ] Load NIH metadata (if available)

### Phase 2: Clean (per source)
- [ ] Apply dtype locks
- [ ] Rename columns to conformed names
- [ ] Derive state_abbr and period_id
- [ ] Drop PHI/redundant columns
- [ ] Enforce range checks and enums
- [ ] Handle nulls per policy

### Phase 3: Validate
- [ ] Run rules from `resources/rules/core.json`
- [ ] Run source-specific rules (synthea.json, vdh.json, nhanes.json, nih.json)
- [ ] Generate validation report
- [ ] Flag records failing critical checks

### Phase 4: Transform
- [ ] Set validation flags (low_precision_time, ambiguous_geo, nih_geo_limited)
- [ ] Apply HMAC hash for Synthea customer_id
- [ ] Filter to state_abbr='VA' where appropriate
- [ ] Merge datasets on SEQN (NHANES) or patient_id (Synthea)

### Phase 5: Load
- [ ] Aggregate to state_month_va grain
- [ ] Compute cohort fact columns
- [ ] Build dimension tables (GeoDim, DateDim, SourceDim)
- [ ] Write to processed data directory

---

## Notes

- **Survey Weights**: NHANES requires survey weights (WTINT2YR, WTMEC2YR) for valid population estimates. Consult CDC guidelines before aggregation.
- **FHIR Parsing**: Synthea FHIR bundles require recursive JSON navigation; use `entry[].resource` array.
- **SAS Transport**: NHANES XPT files require `pyreadstat` library for reading.
- **Privacy**: Even though Synthea is synthetic, maintain PHI handling practices for consistency.
- **Performance**: Synthea processing (5,000 files × ~3.8MB) may require parallel processing or chunking.

---

**Last Updated**: 2025-11-11  
**See Also**: `resources/join_spec.json`, `resources/rules/*.json`
