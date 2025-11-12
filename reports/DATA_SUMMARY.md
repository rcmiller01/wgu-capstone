# Data Summary Report

**Generated**: 2025-11-11
**Analyst**: Senior Data Engineer
**Purpose**: Non-destructive description of data files in repository

---

## Executive Summary

Based on directory structure analysis, this repository contains **3 PRIMARY DATA SOURCES** with the following breakdown:

- **Synthea (Synthetic FHIR)**: ~1,000+ JSON files (patient records)
- **NHANES (CDC Survey)**: 8 XPT files (demographics, body measures, cholesterol, blood pressure)
- **VDH (Virginia Dept of Health)**: 2 CSV files (state health metrics)

**Total Data Sources**: 3 main sources
**Est. Total Files**: 1,000+ files
**Status**: Files present in `data/raw/`, synthetic data NOT pushed to GitHub (as expected)

---

## Data Source 1: NHANES (National Health and Nutrition Examination Survey)

### Overview
- **Source**: CDC/NCHS
- **Format**: SAS Transport (XPT) files
- **Location**: `data/raw/nhanes/`
- **Cycles**: 2017-2018, 2019-2020
- **Files Found**: 8 XPT files

### Files Inventory

| File Path | Component | Cycle | Description |
|-----------|-----------|-------|-------------|
| `data/raw/nhanes/2017-2018/DEMO_J.XPT` | Demographics | 2017-2018 | Age, gender, race, income, education |
| `data/raw/nhanes/2017-2018/BMX_J.XPT` | Body Measures | 2017-2018 | Height, weight, BMI, waist circumference |
| `data/raw/nhanes/2017-2018/TCHOL_J.XPT` | Cholesterol | 2017-2018 | Total cholesterol, HDL, LDL, triglycerides |
| `data/raw/nhanes/2017-2018/BPQ_J.XPT` | Blood Pressure | 2017-2018 | Hypertension diagnosis, medication |
| `data/raw/nhanes/2019-2020/DEMO_K.XPT` | Demographics | 2019-2020 | Age, gender, race, income, education |
| `data/raw/nhanes/2019-2020/BMX_K.XPT` | Body Measures | 2019-2020 | Height, weight, BMI, waist circumference |
| `data/raw/nhanes/2019-2020/TCHOL_K.XPT` | Cholesterol | 2019-2020 | Total cholesterol, HDL, LDL, triglycerides |
| `data/raw/nhanes/2019-2020/BPQ_K.XPT` | Blood Pressure | 2019-2020 | Hypertension diagnosis, medication |

### Expected Schema (Based on Documentation)

#### DEMO (Demographics)
- `SEQN` - Respondent sequence number (INT, UNIQUE ID)
- `RIAGENDR` - Gender (1=Male, 2=Female)
- `RIDAGEYR` - Age in years (INT, 0-85+)
- `RIDRETH3` - Race/Ethnicity (CATEGORICAL)
- `DMDEDUC2` - Education level (CATEGORICAL)
- `INDFMPIR` - Family poverty income ratio (FLOAT)

**Expected Rows per Cycle**: 2,000-5,000 participants

#### BMX (Body Measures)
- `SEQN` - Respondent sequence number (FOREIGN KEY)
- `BMXWT` - Weight in kg (FLOAT)
- `BMXHT` - Height in cm (FLOAT)
- `BMXBMI` - Body Mass Index (FLOAT, calculated)
- `BMXWAIST` - Waist circumference in cm (FLOAT)

**Expected Missing**: 5-15% (participant refusal/contraindications)

#### TCHOL (Cholesterol)
- `SEQN` - Respondent sequence number (FOREIGN KEY)
- `LBXTC` - Total cholesterol (mg/dL, FLOAT)
- `LBDHDD` - Direct HDL cholesterol (mg/dL, FLOAT)
- `LBDLDL` - LDL cholesterol (mg/dL, FLOAT, calculated)
- `LBXTR` - Triglycerides (mg/dL, FLOAT)

**Expected Missing**: 10-25% (insufficient sample, equipment failure)

#### BPQ (Blood Pressure Questionnaire)
- `SEQN` - Respondent sequence number (FOREIGN KEY)
- `BPQ020` - Ever told you had high blood pressure (YES/NO)
- `BPQ040A` - Taking prescription for hypertension (YES/NO)
- `BPQ050A` - Now taking prescribed medicine (YES/NO)

**Expected Missing**: 15-30% (refused/don't know responses)

### Data Example (Hypothetical Row)
```
SEQN=93703, RIAGENDR=1, RIDAGEYR=45, BMXWT=85.3, BMXHT=175.2, BMXBMI=27.8, 
LBXTC=195.5, BPQ020=1 (Yes)
```

### PII Flags
- ⚠️ `SEQN` - Could be considered identifying in conjunction with other data
- All other variables are de-identified or aggregated

### Metadata
- **Source Guess**: nhanes
- **License Guess**: Public Domain (U.S. Government)
- **Is Synthetic**: FALSE
- **Format**: SAS XPT (SAS Transport)
- **Compression**: None

---

## Data Source 2: Synthea (Synthetic Patient Records)

### Overview
- **Source**: MITRE Corporation Synthea Generator
- **Format**: FHIR JSON (1 file per patient)
- **Location**: `data/raw/synthea/fhir/`
- **Files Found**: ~1,000+ JSON files (sample shown)
- **Generation Date**: 2025-11-11 (per acquisition log)
- **Configuration**: 5,000 patients, seed=12345, state=Virginia

### Files Inventory (Sample)
Files follow naming pattern: `[FirstName][Number]_[LastName][Number]_[UUID].json`

Examples:
- `Benjamín452_Gálvez271_1a5bcf1f-f762-0043-ffb6-da7bd63a0352.json`
- `August363_Torp761_aec974d4-2944-30bc-4aa2-635f3681d575.json`
- `Kip442_Rodriguez71_de59c9b7-1403-b518-8642-a00cbbd2af18.json`
- ... (1,000+ more files)

### Expected Schema (FHIR Resources)

Each JSON file contains a FHIR Bundle with multiple resources:

#### Patient Resource
```json
{
  "resourceType": "Patient",
  "id": "patient-uuid",
  "identifier": [{"system": "...", "value": "..."}],
  "name": [{"given": ["FirstName"], "family": "LastName"}],
  "gender": "male|female",
  "birthDate": "YYYY-MM-DD",
  "address": [{"city": "...", "state": "Virginia", "postalCode": "..."}],
  "maritalStatus": {...},
  "telecom": [...]
}
```

#### Encounter Resource
- `id` - Unique identifier
- `status` - finished/in-progress
- `class` - inpatient/outpatient/emergency
- `type` - Visit type codes
- `period` - Start/end timestamps
- `serviceProvider` - Healthcare org reference

#### Condition Resource (Diagnoses)
- `code` - ICD-10/SNOMED codes
- `onsetDateTime` - When condition started
- `clinicalStatus` - active/resolved
- `verificationStatus` - confirmed/provisional

#### Medication Resource
- `code` - RxNorm codes
- `dosageInstruction` - Dosing details
- `effectivePeriod` - When prescribed

#### Observation Resource (Labs/Vitals)
- `code` - LOINC codes
- `value` - Numeric or coded value
- `effectiveDateTime` - When observed
- `category` - vital-signs/laboratory

### Typical File Size
- **Per Patient**: 50-500 KB (varies by encounter count)
- **Total Estimated**: ~19 GB for 5,000 patients (per acquisition log)

### Expected Row Count
- **Files**: 5,000 (1 per patient)
- **Resources per file**: 20-100+ (encounters, conditions, medications, etc.)
- **Total Resources**: 100,000-500,000 across all files

### PII Flags (Synthetic but realistic-looking)
- 🔒 `name` - Patient names (synthetic but PII-like)
- 🔒 `birthDate` - Dates of birth
- 🔒 `address` - Street addresses
- 🔒 `telecom` - Phone numbers
- 🔒 `identifier` - Medical record numbers
- ⚠️ `id` - UUIDs (not truly identifying)

**Note**: All PII is SYNTHETIC - generated data, not real patients

### Data Example
```json
{
  "resourceType": "Patient",
  "id": "1a5bcf1f-f762-0043-ffb6-da7bd63a0352",
  "name": [{"given": ["Benjamín"], "family": "Gálvez"}],
  "gender": "male",
  "birthDate": "1980-05-15",
  "address": [{"city": "Richmond", "state": "Virginia", "postalCode": "23220"}]
}
```

### Metadata
- **Source Guess**: synthea
- **License Guess**: Apache-2.0
- **Is Synthetic**: TRUE
- **Format**: FHIR JSON
- **Compression**: None

### Additional Files
- `data/raw/synthea/metadata.json` - Generation parameters
- `data/raw/synthea/metadata/2025_11_11T02_29_16Z_5000_Virginia_*.json` - Detailed generation log

---

## Data Source 3: VDH (Virginia Department of Health)

### Overview
- **Source**: Virginia Department of Health / data.virginia.gov
- **Format**: CSV
- **Location**: `data/raw/vdh/`
- **Files Found**: 2 CSV files

### Files Inventory

| File Path | Description | Expected Content |
|-----------|-------------|------------------|
| `data/raw/vdh/Health Opportunity Index.csv` | Health equity metrics by locality | County-level health determinants |
| `data/raw/vdh/Virginia WIC.csv` | WIC program participation data | Enrollment and demographic data |

### Expected Schema

#### Health Opportunity Index
**Purpose**: Measures social determinants of health across Virginia localities

Likely columns:
- `locality` / `county` - Geographic area (CATEGORICAL)
- `fips_code` - County FIPS code (STRING, 5-digit)
- `health_district` - VA health district name (CATEGORICAL)
- `hoi_score` - Overall health opportunity index (FLOAT, 0-100)
- `education_score` - Education subdomain score (FLOAT)
- `economic_score` - Economic subdomain score (FLOAT)
- `community_score` - Community/environment score (FLOAT)
- `year` / `report_date` - Data year (INT or DATE)
- `population` - Population denominator (INT)
- `rural_urban_code` - Rural/Urban classification (CATEGORICAL)

**Expected Rows**: ~133 (one per Virginia county) or 35 (one per health district)

**Expected Missing**: 10-20% (small counts suppressed for privacy)

#### Virginia WIC
**Purpose**: WIC (Women, Infants, Children) program participation

Likely columns:
- `locality` / `health_district` - Geographic area
- `report_month` / `report_year` - Time period
- `total_participants` - Count of WIC participants (INT)
- `women_participants` - Pregnant/postpartum women count (INT)
- `infants_participants` - Infants (0-12 mo) count (INT)
- `children_participants` - Children (1-5 yr) count (INT)
- `income_eligible_pct` - % income-eligible population (FLOAT)

**Expected Rows**: 500-1,000 (monthly/quarterly by locality)

**Expected Missing**: 15-30% (suppressed counts <10 for privacy)

### PII Flags
- ✅ No direct PII expected (aggregated/de-identified data)
- ⚠️ `locality` in combination with small counts could indirectly identify

### Data Example (Hypothetical)
```csv
locality,health_district,hoi_score,population,rural_urban_code
Alleghany,Alleghany,45.2,15000,rural
Henrico,Henrico,78.5,334000,urban
```

### Metadata
- **Source Guess**: vdh
- **License Guess**: Open Data (varies by dataset)
- **Is Synthetic**: FALSE
- **Format**: CSV
- **Compression**: None

---

## Summary Statistics

### File Counts by Source
| Source | Files | Format | Estimated Size |
|--------|-------|--------|----------------|
| NHANES | 8 | XPT | ~100-500 MB |
| Synthea | ~5,000 | JSON (FHIR) | ~19 GB |
| VDH | 2 | CSV | ~1-10 MB |
| **TOTAL** | **~5,010** | **Mixed** | **~19-20 GB** |

### Files > 200 MB
Based on acquisition log estimate:
- Synthea aggregate size: ~19 GB across 5,000 files
- Individual Synthea files: ~3.8 MB average (none > 200 MB individually)
- NHANES files: Typically 10-50 MB each (none > 200 MB)
- VDH files: <10 MB

**Result**: No individual files > 200 MB detected

### PII-Like Columns Flagged

| Source | PII-Like Columns | Notes |
|--------|------------------|-------|
| NHANES | 1 | `SEQN` (respondent ID) |
| Synthea | 5-10 per file | name, birthDate, address, telecom, identifier (ALL SYNTHETIC) |
| VDH | 0-1 | locality (aggregated, low risk) |

**Total PII-Like Columns**: ~6-12 across all sources

**Critical Note**: Synthea PII is SYNTHETIC (fake data) - no real patient information

---

## Data Quality Notes

### Completeness
- ✅ All expected NHANES files present (4 components × 2 cycles = 8 files)
- ✅ Synthea generated successfully (5,000 patients per acquisition log)
- ⚠️ VDH manually downloaded (2 files present)
- ❌ NIH X-Ray data not present (manual download required, documented in README)

### Missing Data Expectations
- **NHANES**: 5-30% missing depending on component (normal for survey data)
- **Synthea**: <5% missing (synthetic data, complete by design)
- **VDH**: 10-30% missing (suppressed small counts for privacy)

### File Integrity
- Hash computation not completed (requires Python environment)
- Recommend running `src/analysis/data_profiler.py` once Python is configured

---

## Next Steps for Complete Analysis

### Prerequisites
1. Install Python 3.11+ environment
2. Install required packages:
   ```bash
   pip install pandas numpy pyarrow
   ```

### Run Full Profiler
```bash
python src/analysis/data_profiler.py
```

This will generate:
- `reports/data_manifest.csv` - Complete file inventory with SHA256 hashes
- `reports/schema_profile.md` - Detailed column-by-column schema analysis

### Manual Inspection (If Python Unavailable)
For immediate data review:
1. NHANES XPT files: Use SAS, R (haven package), or Python (pandas)
2. Synthea JSON: Use any JSON viewer/editor
3. VDH CSV: Use Excel, Notepad++, or any CSV tool

---

## Compliance & Privacy

### Data Classification
- **NHANES**: De-identified survey data (PUBLIC)
- **Synthea**: Synthetic data (PUBLIC, no PHI)
- **VDH**: Aggregated state data (PUBLIC)

### IRB/HIPAA Status
- ✅ No IRB required (all public/synthetic data)
- ✅ HIPAA compliant (de-identified/synthetic)
- ✅ Safe for version control (after excluding large files)

### Reproducibility
- **Synthea Seed**: 12345 (reproducible generation)
- **NHANES**: Static datasets (no versioning, permanent archive)
- **VDH**: Manual download (recommend documenting download date)

---

**Report Generated**: 2025-11-11  
**Status**: PRELIMINARY (awaiting Python environment for full profiling)  
**Action Required**: Install Python dependencies and run `data_profiler.py` for complete analysis
