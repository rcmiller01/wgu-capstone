# Results Section Paragraphs

**Document Purpose:** Paste-ready text for submission document  
**Date:** 2025-11-11  
**Project:** WGU D610 Capstone - Serverless FHIR Pipeline Performance Study

---

## Performance Paragraph (Primary Results)

Across 1,010 ingest runs (Synthea n=1,000; NHANES n=8; VDH n=2), median end-to-end latency was 16.12 seconds (P95 41.56s), well within the target thresholds of ≤30s (P50) and ≤120s (P95). The calibrated validation suite achieved a 95.9% pass rate under the relaxed policy (v2), compared to 94.9% under strict validation (v1). All 41 remaining failures originated from Synthea FHIR files and were attributable to optional-field variability (missing temporal precision, geographic ambiguity) that did not affect metric computability. NHANES and VDH sources maintained 100% pass rates in both validation versions.

---

## Limitations Paragraph

This study's data integration has three key limitations. First, NHANES 2017-2020 provides Virginia-weighted demographic priors but lacks individual-level temporal precision (survey months aggregated to 2-year cycles); these records are flagged low_precision_time=1 and contribute to overall counts but are excluded from month-stratified analyses. Second, NIH Chest X-ray images could not be joined to Virginia cohorts due to missing state-level geography in DICOM metadata (ambiguous_geo=1); these data remain available for future image processing pipelines but do not contribute to the current geographic stratification. Third, Synthea generates realistic FHIR data for pipeline performance testing but is synthetic; validation rates and latency distributions reflect pipeline realism, not epidemiologic validity.

---

## Usage Instructions

**Copy-Paste Workflow:**

1. **Performance Results:** Copy the "Performance Paragraph" section directly into your submission document's Results section
2. **Limitations:** Copy the "Limitations Paragraph" into your Discussion or Limitations section
3. **No Editing Needed:** Text is submission-ready with proper statistics, n values, and citations to data sources

**Key Statistics Referenced:**
- Total files: n=1,010 (Synthea=1,000; NHANES=8; VDH=2)
- P50 latency: 16.12s (target: ≤30s)
- P95 latency: 41.56s (target: ≤120s)
- Validation v1 (strict): 94.9% pass rate (52 failures)
- Validation v2 (relaxed): 95.9% pass rate (41 failures)
- NHANES/VDH: 100% pass rate in both versions

**Cross-References:**
- Full metrics: `docs/metrics_spec.md`
- Validation comparison: `reports/validation_calibration_report.md`
- Data dictionary: `docs/data_dictionary_cohort_va.md`
- Validation policy: `docs/methods_validation_policy.md`
