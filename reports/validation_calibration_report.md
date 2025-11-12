# Validation Calibration Report

## Pre- vs Post-Calibration Failure Analysis

### Overall Pass Rates

| Validation Policy | Total Records | Passed | Failed | Pass Rate |
|------------------|---------------|--------|--------|-----------|
| **V1 - Strict** | 1,010 | 958 | 52 | 94.9% |
| **V2 - Relaxed** | 1,010 | 969 | 41 | 95.9% |
| **Improvement** | - | +11 | -11 | +1.0% |

### Top Failing Rule Types (Pre- vs Post-Calibration)

| Rule Type | V1 Strict Failures | V2 Relaxed Failures | Reduction | Rationale for Relaxation |
|-----------|-------------------|---------------------|-----------|--------------------------|
| **Optional FHIR elements missing** | ~26 (50%) | ~16 (39%) | -38% | Allow null for non-required fields (e.g., Encounter.period.end, Observation.component) |
| **Incomplete temporal data** | ~13 (25%) | ~8 (20%) | -38% | Accept single date field; flag with `low_precision_time=1` |
| **Ambiguous geography** | ~8 (15%) | ~5 (12%) | -38% | Derive state from city/text; flag with `ambiguous_geo=1` |
| **Missing reference ranges** | ~5 (10%) | ~12 (29%) | +140% | Mark lab rows "not applicable" vs file failure (reduces strict errors but increases specific metric exclusions) |

**Note:** V2 shifts validation philosophy from "fail entire file" to "flag row-level warnings + proceed." Files only fail if >5% of metric-critical rows are unusable or core identifiers (resourceType, id, period_id) are missing.

### Failure Taxonomy by Data Source

#### V1 - Strict Validation (94.9% pass rate)

| Source | Total | Passed | Failed | Failure % |
|--------|-------|--------|--------|-----------|
| NHANES | 8 | 8 | 0 | 0.0% |
| Synthea | 1,000 | 948 | 52 | 5.2% |
| VDH | 2 | 2 | 0 | 0.0% |
| **ALL** | **1,010** | **958** | **52** | **5.1%** |

#### V2 - Relaxed Validation (95.9% pass rate)

| Source | Total | Passed | Failed | Failure % |
|--------|-------|--------|--------|-----------|
| NHANES | 8 | 8 | 0 | 0.0% |
| Synthea | 1,000 | 959 | 41 | 4.1% |
| VDH | 2 | 2 | 0 | 0.0% |
| **ALL** | **1,010** | **969** | **41** | **4.1%** |

### Key Findings

**Structured Data (NHANES, VDH):**
- 100% pass rate in both V1 and V2
- Well-formed CSV/XPT files with complete required fields
- No optional element variability

**Semi-Structured Data (Synthea FHIR):**
- V1: 94.8% pass rate (52 failures)
- V2: 95.9% pass rate (41 failures)
- Improvement: +1.1 percentage points
- All failures confined to Synthea due to FHIR's flexible schema

**Failure Causes (Synthea FHIR):**
- **Not schema breakage** - all files are valid FHIR R4
- **Optional element variability** - different patient records have different sets of optional fields
- **Real-world realism** - production FHIR exchanges exhibit similar patterns

### Validation Policy Changes (V1 → V2)

#### 1. Encounter Date Presence
- **V1 Strict:** Require both `Encounter.period.start` AND `period.end` → error
- **V2 Relaxed:** Require at least one temporal field → error; flag single-date records with `low_precision_time=1` → warn

#### 2. Patient Geography
- **V1 Strict:** Require `Patient.address.state` → error
- **V2 Relaxed:** Derive from state/city/text; flag with `ambiguous_geo=1` if derivation fails → warn

#### 3. Observation Values
- **V1 Strict:** Require `Observation.value[x]` → error
- **V2 Relaxed:** Allow either value[x] OR component[]; only error if neither exists

#### 4. Reference Ranges
- **V1 Strict:** Missing `referenceRange` → error
- **V2 Relaxed:** Mark lab row "not applicable" → exclude from lab_oob_rate calculation (warn, not error)

#### 5. File-Level Pass/Fail Policy
**V2 files fail only if:**
- Cannot derive any month (period_id) for the file
- >5% of metric-critical rows are unusable
- Core schema broken (missing resourceType/id)

**Everything else:** Warn + flag + proceed

---

**Report Generated:** 2025-11-11  
**Analysis Tool:** `analyze_failures.py`  
**Data Source:** `data/processed/processed_data_v*.parquet`
