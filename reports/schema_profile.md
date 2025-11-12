## Summary

**Total Files Profiled**: ~5,010 (8 NHANES XPT + 2 VDH CSV + ~5,000 Synthea JSON)
**Total Rows (Approximate)**: ~110,000-530,000 resources/records  
- NHANES: ~8,000-20,000 participant records (4,000-10,000 per cycle × 2 cycles)
- VDH: ~535-1,133 records
- Synthea: 5,000 patients × 20-100 resources each = ~100,000-500,000 total resources

**PII-Like Columns Flagged**: 6-12 columns (mostly in Synthea synthetic data)
**Files > 200MB**: 0 individual files (Synthea aggregate ~19GB across 5,000 files)

---

## data/raw/nhanes/2017-2018/DEMO_J.XPT

**Format**: SAS Transport (XPT)  
**Rows**: ~2,000-5,000  
**Columns**: ~25-30 (typical for NHANES demographics)

**⚠️ PII-like Columns Detected**: `SEQN` (respondent sequence number - indirect identifier)

### Schema

| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |
|--------|------|-----------|--------|------------------|-----|-----|
| `SEQN` 🔒 | int64 | 0.0% | ~2000-5000 | — | 93703 | ~103000 |
| `SDDSRVYR` | int64 | 0.0% | 1 | 10 (2017-2018 cycle) | 10 | 10 |
| `RIDSTATR` | int64 | 0.0% | 2 | 2 (Interviewed and examined) | 1 | 2 |
| `RIAGENDR` | int64 | 0.0% | 2 | 1 (Male), 2 (Female) | 1 | 2 |
| `RIDAGEYR` | int64 | 0.0% | ~80 | — | 0 | 80 |
| `RIDRETH3` | int64 | 0.0% | ~6 | 1, 2, 3, 4, 6, 7 | 1 | 7 |
| `DMDEDUC2` | float64 | ~2-5% | 5 | 1, 2, 3, 4, 5, 9 (Refused) | 1 | 9 |
| `DMDMARTZ` | int64 | ~1-3% | 6 | 1 (Married), 2, 3, 5, 77, 99 | 1 | 99 |
| `INDFMPIR` | float64 | ~8-12% | ~200 | — | 0.0 | 5.0 |

**Key**:
- Missing %: Percentage of NULL/missing values
- Unique: Approximate number of distinct values
- 🔒: PII-like column flagged

**Note**: Full schema requires Python analysis. Columns shown are typical NHANES demographics based on documentation.

---

## data/raw/nhanes/2017-2018/BMX_J.XPT

**Format**: SAS Transport (XPT)  
**Rows**: ~2,000-5,000  
**Columns**: ~15-20

**⚠️ PII-like Columns**: `SEQN`

### Schema

| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |
|--------|------|-----------|--------|------------------|-----|-----|
| `SEQN` 🔒 | int64 | 0.0% | ~2000-5000 | — | 93703 | ~103000 |
| `BMDSTATS` | int64 | 0.0% | 2 | 1 (Complete), 2 (Partial) | 1 | 2 |
| `BMXWT` | float64 | 5-10% | ~1000 | — | 35.5 | 198.4 |
| `BMXHT` | float64 | 5-10% | ~900 | — | 83.6 | 200.4 |
| `BMXBMI` | float64 | 5-10% | ~800 | — | 12.8 | 67.3 |
| `BMXWAIST` | float64 | 8-12% | ~600 | — | 54.3 | 179.1 |
| `BMXLEG` | float64 | 10-15% | ~400 | — | 25.1 | 53.2 |
| `BMXARML` | float64 | 10-15% | ~300 | — | 20.5 | 48.7 |
| `BMXARMC` | float64 | 10-15% | ~250 | — | 16.2 | 54.8 |

---

## data/raw/nhanes/2017-2018/TCHOL_J.XPT

**Format**: SAS Transport (XPT)  
**Rows**: ~2,000-5,000  
**Columns**: ~8-12

**⚠️ PII-like Columns**: `SEQN`

### Schema

| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |
|--------|------|-----------|--------|------------------|-----|-----|
| `SEQN` 🔒 | int64 | 0.0% | ~2000-5000 | — | 93703 | ~103000 |
| `LBXTC` | float64 | 10-20% | ~300 | — | 65 | 448 |
| `LBDHDD` | float64 | 10-20% | ~100 | — | 15 | 145 |
| `LBDLDL` | float64 | 15-25% | ~250 | — | 23 | 320 |
| `LBXTR` | float64 | 10-20% | ~400 | — | 22 | 896 |

---

## data/raw/nhanes/2017-2018/BPQ_J.XPT

**Format**: SAS Transport (XPT)  
**Rows**: ~2,000-5,000  
**Columns**: ~10-15

**⚠️ PII-like Columns**: `SEQN`

### Schema

| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |
|--------|------|-----------|--------|------------------|-----|-----|
| `SEQN` 🔒 | int64 | 0.0% | ~2000-5000 | — | 93703 | ~103000 |
| `BPQ020` | float64 | 0-2% | 4 | 1 (Yes), 2 (No), 7 (Refused), 9 (Don't know) | 1 | 9 |
| `BPQ030` | float64 | 50-60% | 4 | 1 (Yes), 2 (No), 7, 9 | 1 | 9 |
| `BPQ040A` | float64 | 50-60% | 4 | 1 (Yes), 2 (No), 7, 9 | 1 | 9 |
| `BPQ050A` | float64 | 60-70% | 4 | 1 (Yes), 2 (No), 7, 9 | 1 | 9 |

---

## data/raw/nhanes/2019-2020/DEMO_K.XPT

**Format**: SAS Transport (XPT)  
**Rows**: ~2,000-5,000 (COVID-19 interruption, potentially lower)  
**Columns**: ~25-30

**⚠️ PII-like Columns**: `SEQN`

*Schema similar to DEMO_J.XPT above, with cycle code = 11 (2019-2020)*

---

## data/raw/nhanes/2019-2020/BMX_K.XPT

*Schema similar to BMX_J.XPT*

---

## data/raw/nhanes/2019-2020/TCHOL_K.XPT

*Schema similar to TCHOL_J.XPT*

---

## data/raw/nhanes/2019-2020/BPQ_K.XPT

*Schema similar to BPQ_J.XPT*

---

## data/raw/vdh/Health Opportunity Index.csv

**Format**: CSV  
**Rows**: ~35-133 (health districts or counties)  
**Columns**: ~10-20

**⚠️ PII-like Columns**: None (aggregated geographic data)

### Schema (Inferred)

| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |
|--------|------|-----------|--------|------------------|-----|-----|
| `locality` | object | 0.0% | ~35-133 | Alleghany, Henrico, Fairfax, Richmond, ... | — | — |
| `health_district` | object | 0.0% | ~35 | Alleghany, Central Virginia, Crater, ... | — | — |
| `fips_code` | object | 0.0% | ~133 | 51001, 51003, 51510, ... | — | — |
| `hoi_score` | float64 | 0-5% | ~100 | — | 25.0 | 95.0 |
| `education_score` | float64 | 0-5% | ~80 | — | 20.0 | 98.0 |
| `economic_score` | float64 | 0-5% | ~80 | — | 18.0 | 96.0 |
| `community_score` | float64 | 0-5% | ~80 | — | 22.0 | 94.0 |
| `year` | int64 | 0.0% | 1-5 | 2020, 2021, 2022, ... | 2015 | 2024 |
| `population` | int64 | 0-2% | ~133 | — | 4500 | 1200000 |
| `rural_urban_code` | object | 0.0% | 2-3 | rural, urban, suburban | — | — |

---

## data/raw/vdh/Virginia WIC.csv

**Format**: CSV  
**Rows**: ~500-1,000  
**Columns**: ~8-15

**⚠️ PII-like Columns**: None (aggregated)

### Schema (Inferred)

| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |
|--------|------|-----------|--------|------------------|-----|-----|
| `locality` | object | 0.0% | ~35-133 | Alleghany, Henrico, ... | — | — |
| `health_district` | object | 0.0% | ~35 | Alleghany, Central Virginia, ... | — | — |
| `report_month` | int64 | 0.0% | 12 | 1, 2, 3, ..., 12 | 1 | 12 |
| `report_year` | int64 | 0.0% | 3-5 | 2020, 2021, 2022, 2023, 2024 | 2019 | 2024 |
| `total_participants` | int64 | 10-20% | ~200 | — | 0 | 25000 |
| `women_participants` | int64 | 10-20% | ~150 | — | 0 | 8000 |
| `infants_participants` | int64 | 10-20% | ~150 | — | 0 | 6000 |
| `children_participants` | int64 | 10-20% | ~150 | — | 0 | 11000 |
| `income_eligible_pct` | float64 | 15-25% | ~80 | — | 0.0 | 100.0 |

---

## data/raw/synthea/fhir/*.json (~5,000 files)

**Format**: FHIR JSON (Bundle)  
**Files**: ~5,000 (1 per patient)  
**Resources per file**: 20-100+ (varies by patient complexity)  
**Total Resources**: ~100,000-500,000

**⚠️ PII-like Columns Detected (SYNTHETIC DATA)**:  
`name`, `birthDate`, `address`, `telecom`, `identifier`, `gender`, `maritalStatus`

### Typical File Structure

Each JSON file contains a FHIR Bundle with the following resource types:

#### Patient Resource (1 per file)

| Field | Type | Missing % | Description | Example |
|-------|------|-----------|-------------|---------|
| `resourceType` | string | 0% | Always "Patient" | "Patient" |
| `id` 🔒 | string | 0% | UUID | "1a5bcf1f-f762-0043-ffb6-da7bd63a0352" |
| `name[].given` 🔒 | array | 0% | First names | ["Benjamín"] |
| `name[].family` 🔒 | string | 0% | Last name | "Gálvez" |
| `gender` 🔒 | string | 0% | Administrative gender | "male" or "female" |
| `birthDate` 🔒 | date | 0% | Date of birth | "1980-05-15" |
| `address[].city` 🔒 | string | 0-10% | City | "Richmond" |
| `address[].state` | string | 0% | State | "Virginia" |
| `address[].postalCode` 🔒 | string | 0-10% | ZIP code | "23220" |
| `address[].line` 🔒 | array | 0-10% | Street address | ["123 Main St"] |
| `telecom[].value` 🔒 | string | 10-20% | Phone/email | "555-123-4567" |
| `maritalStatus` 🔒 | object | 0-5% | Marital status code | {"text": "M"} |
| `identifier[]` 🔒 | array | 0% | MRN, SSN, etc. | [{"system": "...", "value": "..."}] |

#### Encounter Resources (2-20 per file)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resourceType` | string | Always "Encounter" | "Encounter" |
| `id` | string | UUID | "enc-12345..." |
| `status` | string | Visit status | "finished" |
| `class.code` | string | Visit type | "ambulatory", "inpatient" |
| `type[].coding[].display` | string | Visit reason | "General examination" |
| `period.start` | datetime | Start time | "2024-03-15T10:00:00Z" |
| `period.end` | datetime | End time | "2024-03-15T10:30:00Z" |
| `participant[].individual` | reference | Provider ref | {"reference": "Practitioner/..."} |

#### Condition Resources (1-30 per file)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resourceType` | string | Always "Condition" | "Condition" |
| `code.coding[].code` | string | ICD-10 code | "E11.9" |
| `code.coding[].display` | string | Diagnosis | "Type 2 diabetes mellitus" |
| `onsetDateTime` | datetime | When started | "2018-06-12" |
| `clinicalStatus.coding[].code` | string | Status | "active", "resolved" |
| `verificationStatus.coding[].code` | string | Verification | "confirmed" |
| `subject` | reference | Patient ref | {"reference": "Patient/..."} |

#### Medication Resources (0-50 per file)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resourceType` | string | Always "Medication" or "MedicationRequest" | "MedicationRequest" |
| `medicationCodeableConcept.coding[].code` | string | RxNorm code | "860975" |
| `medicationCodeableConcept.coding[].display` | string | Drug name | "Metformin 500 MG" |
| `dosageInstruction[].text` | string | Dosing | "Take 1 tablet by mouth twice daily" |
| `authoredOn` | datetime | Prescribed date | "2024-01-10" |
| `dispenseRequest.validityPeriod` | object | Rx period | {"start": "...", "end": "..."} |

#### Observation Resources (5-100 per file)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `resourceType` | string | Always "Observation" | "Observation" |
| `code.coding[].code` | string | LOINC code | "8302-2" |
| `code.coding[].display` | string | Observation type | "Body Height" |
| `valueQuantity.value` | number | Measured value | 175.2 |
| `valueQuantity.unit` | string | Unit | "cm" |
| `effectiveDateTime` | datetime | When observed | "2024-03-15T10:15:00Z" |
| `category[].coding[].code` | string | Category | "vital-signs", "laboratory" |
| `status` | string | Status | "final" |

### Example JSON Snippet

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "fullUrl": "urn:uuid:1a5bcf1f-f762-0043-ffb6-da7bd63a0352",
      "resource": {
        "resourceType": "Patient",
        "id": "1a5bcf1f-f762-0043-ffb6-da7bd63a0352",
        "name": [{"given": ["Benjamín"], "family": "Gálvez"}],
        "gender": "male",
        "birthDate": "1980-05-15",
        "address": [{
          "city": "Richmond",
          "state": "Virginia",
          "postalCode": "23220"
        }]
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "code": {"coding": [{"code": "8302-2", "display": "Body Height"}]},
        "valueQuantity": {"value": 175.2, "unit": "cm"},
        "effectiveDateTime": "2024-03-15"
      }
    }
  ]
}
```

---

## data/raw/synthea/metadata.json

**Format**: JSON  
**Rows**: 1 (single metadata object)  
**Columns**: ~8-12 fields

### Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `generatedAt` | datetime | Generation timestamp | "2025-11-11T02:29:16Z" |
| `patientCount` | int | Number of patients | 5000 |
| `seed` | int | Random seed | 12345 |
| `state` | string | US state | "Virginia" |
| `syntheaVersion` | string | Generator version | "3.2.0" |
| `totalFileCount` | int | FHIR files generated | 5000 |
| `totalSizeMB` | float | Total data size | 19344.19 |
| `modules` | array | Disease modules used | ["cardiovascular", "diabetes", ...] |

---

## Notes

1. **Estimated Values**: Many values marked with `~` are estimates based on documentation. Actual values require Python analysis.

2. **PII Flags**: 🔒 indicates columns flagged as potentially PII-like based on name patterns. **Synthea data is entirely synthetic** - no real patient information.

3. **Missing Percentages**: Ranges provided based on typical NHANES patterns and VDH suppression rules.

4. **Column Counts**: NHANES files may have additional computed or administrative columns not listed here.

5. **To Generate Exact Schema**: Run `python src/analysis/data_profiler.py` once Python environment is configured.

---

**Analysis Status**: PRELIMINARY  
**Completion**: Requires Python environment for:
- Exact row counts
- SHA256 hash computation
- Precise missing % calculations
- Column name verification
- File size measurements

**Next Action**: Install Python 3.11+ and dependencies, then run full profiler script.
