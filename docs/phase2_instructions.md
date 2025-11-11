# Phase 2 Instructions: Baseline and Testing Context

**Issue**: #3  
**Status**: In Progress  
**Goal**: Establish credible baseline for manual data entry performance and define comprehensive testing methodology

---

## Overview

Phase 2 establishes the foundation for the paired t-test comparison by:

1. **Documenting the baseline** (manual data entry performance) with peer-reviewed sources
2. **Acknowledging limitations** of inferred baseline (no live manual process to measure)
3. **Defining the test plan** for measuring automated pipeline performance
4. **Setting success thresholds** aligned with success criteria from proposal

This phase transitions from "what we're studying" (Phase 0-1) to "how we'll measure it" (Phase 2).

---

## Task 1: Locate Peer-Reviewed Baseline Sources

### Objective

Find 3-5 credible sources (peer-reviewed studies, operational reports, time-motion analyses) that document manual health data entry time and accuracy.

### Requirements

**Time Estimates:**
- Manual data entry time per record (target: 15-45 minute range)
- Include variance by record complexity (simple demographics vs. full encounter)
- Preference for rural/safety-net settings if available

**Accuracy/Error Rates:**
- Validation pass rates or error rates for manual transcription
- Common error types (transposition, omission, format errors)
- Target: 80-90% accuracy range to establish conservative baseline

**Source Credibility:**
- Peer-reviewed journals (preferred)
- Government reports (CMS, ONC, state health departments)
- Healthcare operational research (HIMSS, AMIA conferences)
- Time-motion studies from HIT implementation literature

### Search Strategy

**Databases:**
- PubMed/MEDLINE
- IEEE Xplore (health informatics)
- Google Scholar
- CMS.gov / HealthIT.gov publications

**Keywords:**
- "manual data entry" + "health records"
- "EHR data entry time" OR "transcription time"
- "data quality" + "manual entry" + "error rate"
- "health information exchange" + "workflow"
- "interoperability" + "rural health"

### Deliverable

Document findings in `docs/baseline_sources.md`:
- Citation (APA format)
- Key findings (time/accuracy metrics)
- Context (setting, sample size, data type)
- Relevance to study (why this baseline applies)

---

## Task 2: Create Baseline Statement + Limitation

### Objective

Write a concise, defensible baseline statement that establishes the "control condition" for the paired t-test.

### Requirements

**Baseline Statement Components:**

1. **Point Estimate**: "Manual data entry averages X minutes per record with Y% validation accuracy"
2. **Range/Variance**: "Range: A-B minutes depending on record complexity"
3. **Source Attribution**: "Based on [Citation 1], [Citation 2], [Citation 3]"
4. **Context Match**: Explain why these estimates reasonably apply to rural FHIR integration context

**Limitation Acknowledgment:**

Must explicitly state:
- This is an **inferred baseline** (not measured from actual manual process in this study)
- Conservative estimates chosen to avoid inflating improvement claims
- Sensitivity analysis will test across baseline range
- Real-world validation recommended for production deployment

### Deliverable

Section in `docs/baseline_sources.md` titled "Baseline Statement and Limitations"

---

## Task 3: Draft Timing Test Plan

### Objective

Document how automated pipeline latency will be measured to enable paired comparison.

### Requirements

**Test Design:**

1. **Sample Selection**:
   - N = 500-1,000 records per data type (Synthea, NHANES, VDH, NIH images)
   - Stratified by complexity (simple vs. complex records)
   - Random sampling to ensure representativeness

2. **Measurement Approach**:
   - Start time: Record dropped in S3 bucket (event timestamp)
   - End time: Validated record available in FHIR store (query timestamp)
   - Capture: `latency_sec = end_time - start_time`
   - Precision: Millisecond resolution (CloudWatch Logs, Lambda execution duration)

3. **Validation Criteria**:
   - Schema validation (Great Expectations checks)
   - FHIR resource conformance (HAPI FHIR validator)
   - Data completeness (required fields present)
   - Capture: `validation_pass_bool = True/False`

4. **Paired Structure**:
   - Same record processed through:
     - **Manual path**: Baseline estimate (20 min avg, 85% accuracy)
     - **Automated path**: Measured pipeline performance
   - Enables paired t-test on difference scores

**Environmental Controls:**

- AWS Lambda memory allocation (consistent across runs)
- Cold start mitigation (pre-warm functions)
- Network variability logging (VPC flow logs)
- Time of day stratification (workload variation)

### Deliverable

Section in `docs/baseline_sources.md` titled "Timing Test Methodology"

---

## Task 4: Define Success Thresholds

### Objective

Quantify the acceptance criteria that distinguish "successful improvement" from "marginal gain."

### Requirements

**Aligned with Proposal Success Criteria:**

1. **Latency Reduction** (Primary DV: `latency_sec`):
   - P50 (median) ≤ 30 seconds
   - P95 (95th percentile) ≤ 120 seconds
   - **Rationale**: Even P95 case is 10x faster than 20-minute manual baseline

2. **Validation Accuracy** (Secondary DV: `validation_pass_bool`):
   - ≥ 95% validation pass rate
   - **Rationale**: Improvement over 85% manual baseline with margin for quality assurance

3. **Reliability**:
   - ≥ 99% successful processing (excluding invalid source data)
   - **Rationale**: Production-grade resilience for safety-critical health data

4. **Cost Efficiency**:
   - 30-60% reduction in operational cost vs. manual FTE
   - **Rationale**: Aligns with serverless pay-per-use economics

5. **Statistical Significance**:
   - Paired t-test p-value < .05 (α = 0.05)
   - Cohen's d ≥ 0.8 (large effect size)
   - **Rationale**: Ensures improvement is both statistically significant and practically meaningful

**Threshold Justification:**

Each threshold should reference:
- Industry benchmarks (if available)
- Baseline performance (why threshold represents improvement)
- Practical impact (what this means for rural clinics)

### Deliverable

Section in `docs/baseline_sources.md` titled "Success Thresholds and Acceptance Criteria"

---

## Task 5: Cross-Reference and Integrate

### Objective

Ensure Phase 2 documentation aligns with proposal and variables table.

### Checklist

- [ ] Baseline estimates cite 3-5 credible sources
- [ ] Limitation explicitly acknowledged (inferred, not measured)
- [ ] Test plan defines paired structure for paired t-test
- [ ] Success thresholds align with proposal success criteria
- [ ] Latency/validation DVs match `variables_table.md` definitions
- [ ] Statistical method (paired t-test, α=.05) consistent with proposal
- [ ] All citations in APA format (ready for references/apa.bib)

---

## Completion Criteria

Phase 2 is complete when:

- ✅ `docs/baseline_sources.md` created with:
  - 3-5 peer-reviewed/operational sources cited
  - Baseline statement (time + accuracy with range)
  - Limitation acknowledgment (inferred baseline)
  - Timing test methodology (paired design, measurement approach)
  - Success thresholds (quantified for all 5 criteria)

- ✅ All content aligns with proposal and variables table
- ✅ Citations ready for bibliography integration
- ✅ Issue #3 can be closed with confidence

---

## Rubric Alignment

**WGU D610 Capstone Rubric Requirements:**

| Criterion | Phase 2 Coverage |
|-----------|------------------|
| **B1: Data Collection** | Timing test methodology defines how latency/validation data will be collected |
| **B2: Statistical Analysis Plan** | Paired t-test design with baseline comparison documented |
| **C1: Credibility of Sources** | Peer-reviewed baseline sources establish credibility |
| **C2: Limitations** | Inferred baseline limitation explicitly acknowledged |
| **D1: Success Criteria** | Quantified thresholds for latency, accuracy, reliability, cost |

---

**Next Steps After Phase 2:**
- Phase 3: Data cleaning plan (how to handle missing data, outliers, failed validations)
- Phase 4: Methods documentation (statistical procedures in detail)
- Phase 5: Tooling setup (AWS infrastructure, Python environment)

---

**Status**: Ready to begin baseline research  
**Priority**: Locate credible sources for manual data entry time/accuracy baselines
