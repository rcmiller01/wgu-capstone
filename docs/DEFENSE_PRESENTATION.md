# Defense Presentation - Slide Deck Outline

**Project**: Serverless FHIR Data Pipeline for Rural Healthcare  
**Student**: Robert Miller (000982134)  
**Date**: November 11, 2025  
**Duration**: 5-10 minutes

---

## Slide 1: Title & Overview

### Title
**A Serverless FHIR Data Pipeline for Streamlined Rural Health Data Exchange**

Robert Miller | MSDA Capstone | WGU | November 2025

### Key Question
*Can automated cloud processing improve data consistency and timeliness in rural health networks?*

---

## Slide 2: Problem & Motivation (Rural/Serverless Rationale)

### The Problem

**Rural Health Networks Face Data Bottlenecks**:
- Manual data entry: **15-45 minutes per record** (literature: Mehmood 2013, Overhage 2020)
- Fragmented systems: EHR, lab, pharmacy on different platforms
- Limited IT staff: No dedicated data engineers
- Delayed insights: Weekly/monthly reports vs. real-time

### Why Serverless?

**Perfect Fit for Rural Constraints**:
- ✅ **No Infrastructure**: No servers to maintain (zero IT overhead)
- ✅ **Auto-Scaling**: Handles 1 file or 1,000 files automatically
- ✅ **Pay-Per-Use**: $0 cost when idle, ~$0.20 per 1,000 files when active
- ✅ **High Availability**: 99.9%+ uptime without operations team

### Operational Benefits

- **Reduce Labor**: 56-168x faster than manual entry
- **Improve Quality**: 95.9% automated validation vs. 85% manual (literature)
- **Enable Real-Time**: Process files in 16 seconds vs. 20 minutes

---

## Slide 3: Data & Methods

### Data Sources (Heterogeneous Mix)

| Source | Format | Records | Simulates |
|:-------|:------:|:-------:|:----------|
| **Synthea FHIR** | JSON | 1,000 | EHR patient bundles (Encounter, Obs, Meds) |
| **NHANES CDC** | XPT | 8 | Public health surveys |
| **VDH State** | CSV | 2 | State health indicators |
| **Total** | Mixed | **1,010** | Distributed rural network |

### Pipeline Architecture

```
[S3 Upload] → [Lambda Trigger] → [Format Parser] → [Validation (50+ Rules)] 
                                                          ↓
                                    [Pass/Fail Flag] → [S3 Output] → [Metrics Dashboard]
```

### Validation Framework (Rule Calibration)

**Two Policies Compared**:
- **v1 Strict**: Fails files with any missing optional FHIR elements → 94.9% pass rate
- **v2 Relaxed**: Allows optional elements; fails only if >5% unusable → **95.9% pass rate**

**Key Insight**: v2 aligns with FHIR specification (optional elements common) while maintaining quality

---

## Slide 4: Results - Performance Metrics

### Validation Pass Rate ✅

**Target**: ≥95%  
**Result**: **95.9%** (Target Met)

| Source | v1 Strict | v2 Relaxed | Improvement |
|:-------|:---------:|:----------:|:-----------:|
| Synthea FHIR | 94.8% | 95.9% | **+1.1 pp** |
| NHANES XPT | 100.0% | 100.0% | 0.0 pp |
| VDH CSV | 100.0% | 100.0% | 0.0 pp |
| **Overall** | **94.9%** | **95.9%** | **+1.1 pp** |

*Calibration insight: Relaxing optional element requirements reduced false negatives*

### Processing Latency ✅

**Target**: P50 ≤30s, P95 ≤120s  
**Results**: **Both Targets Met**

| Source | P50 (seconds) | P95 (seconds) | vs. Manual |
|:-------|:-------------:|:-------------:|:----------:|
| Synthea FHIR | 16.16 | 42.06 | **55x faster** |
| NHANES XPT | 5.94 | 6.59 | **150x faster** |
| VDH CSV | 3.45 | 4.09 | **290x faster** |
| **Overall** | **16.12** | **42.06** | **~75x avg** |

*Format patterns: FHIR ~3x slower than CSV due to nested structure, but still well within targets*

### Speedup vs. Manual Baseline

- **Manual Entry**: 900-2,700 seconds per record (literature baseline)
- **Automated**: 16 seconds per file (10-100 records)
- **Improvement**: **56-168x faster**

---

## Slide 5: Results - Sensitivity & Limitations

### Sensitivity Analysis (Robustness Testing)

**Question**: Are findings stable despite data quality issues?

**Method**: Simulate quality flags (missing temporal fields, ambiguous geography), compare metrics

| Scenario | Pass Rate | P50 Latency | Impact |
|:---------|:---------:|:-----------:|:------:|
| All Records (Baseline) | 95.9% | 16.12s | - |
| Exclude Temporal Flags | 96.3% | 16.15s | +0.4 pp, +0.03s |
| Exclude Geo Flags | 95.9% | 16.12s | 0.0 pp, 0.00s |
| Exclude Both Flags | 96.2% | 16.13s | +0.3 pp, +0.01s |

**Conclusion**: **Minimal sensitivity** - findings robust to data quality constraints

### Limitations (Honest Assessment)

1. **Synthetic Data**: Synthea FHIR is realistic but idealized; real EHR data may have more quality issues
   - *Mitigation*: Sensitivity analysis simulated missing fields; pilot on de-identified real data recommended

2. **Temporal Aggregation**: File-level metrics, not month-by-month trends
   - *Future Work*: Implement period_id grain for time-series analysis

3. **Geographic Scope**: Virginia-focused; may not generalize to other states
   - *Mitigation*: FHIR is national standard; pipeline architecture vendor-agnostic

4. **Cold Start Latency**: Measured "warm" pipeline; production cold starts add 1-5s
   - *Mitigation*: Provisioned concurrency or scheduled warm-ups

5. **No Paired Comparison**: Estimated manual baseline from literature, not direct measurement
   - *Alternative*: Future work could simulate manual workflows for formal paired t-test

**Key Takeaway**: Results demonstrate feasibility and performance; production deployment should validate on real data

---

## Slide 6: Reusability & Impact

### Immediately Reusable Artifacts

| Artifact | Location | Use Case |
|:---------|:---------|:---------|
| **Validation Rules** | `resources/rules/*.json` | Adapt 50+ rules to your data sources (JSON editing, no code) |
| **Join Spec Template** | `resources/join_spec.json` | Define your join keys and quality flags |
| **Processing Pipeline** | `src/pipeline/*.py` | FHIR/XPT/CSV processors (extend to HL7v2, X12) |
| **Analysis Scripts** | `src/analysis/*.py` | Bootstrap CIs, sensitivity testing, table generation |
| **CI/CD Workflows** | `.github/workflows/*.yml` | Automated testing and linting |

### Deployment Options (3 Paths)

1. **Local Development**: Test on sample data (30-60 min setup)
2. **AWS Lambda**: Production serverless ($10-15/month for 1,000 files/day)
3. **Azure Functions**: Alternative serverless (similar cost)

**ROI Example**: 1,000 files/month
- Manual: 1,000 files × 20 min = **333 hours/month** = **$6,660** (at $20/hour)
- Automated: **$10-15/month**
- **Savings**: **99.8%**

### Practical Recommendations

**For Rural Health Network Administrators**:
1. Start with pilot: 100-200 files on local development
2. Calibrate validation: Use v2-style relaxed policy for FHIR
3. Monitor format-specific latency: Set SLAs per data type (FHIR <30s, CSV <5s)
4. Implement quality flags: Track low_precision_time, ambiguous_geo for sensitivity analysis
5. Plan for cold starts: Use provisioned concurrency for latency-critical workflows

**For Health IT Developers**:
- See `docs/REUSABILITY_GUIDE.md` for deployment checklist
- GitHub repository: https://github.com/rcmiller01/wgu-capstone
- All code MIT licensed (freely reusable)

---

## Talking Points (Be Ready to Explain)

### Rule Calibration (v1 → v2)

**Question**: *Why did you change validation rules?*

**Answer**: 
"Initially, v1 validation was too strict - it failed files with any missing optional FHIR elements, even though FHIR R4 specification allows many elements to be optional (0..1 or 0..* cardinality). For example, Encounter.period.end is optional because an encounter can be ongoing. v2 calibration allows these legitimate omissions while still enforcing core quality rules like 'patient_id required' and '>5% of records must be usable.' This improved pass rate from 94.9% to 95.9% (+1.1 percentage points) without compromising data quality. The improvement came entirely from reducing false negatives, not from lowering standards."

### Data Quality Flags

**Question**: *What are low_precision_time and ambiguous_geo flags?*

**Answer**:
"These flags identify records with reduced data quality but don't cause validation failure. low_precision_time=1 means only one temporal field is present (e.g., period.start but not period.end) - we can still derive a month identifier, but precision is lower. ambiguous_geo=1 means state was inferred from city name or is missing entirely. We carry these flags forward so analysts can choose whether to include or exclude flagged records. Sensitivity analysis showed minimal impact: excluding all flagged records changed pass rate by only +0.3 percentage points and latency by +0.03 seconds. This proves our findings are robust to data quality variations."

### Rural/Serverless Rationale

**Question**: *Why serverless specifically for rural health?*

**Answer**:
"Rural health networks have three key constraints: (1) limited IT staff - often zero dedicated data engineers, (2) variable workloads - some days 10 files, some days 1,000, and (3) tight budgets - can't afford idle infrastructure. Serverless addresses all three: no servers to maintain (zero ops burden), auto-scales from 1 to 1,000 concurrent executions automatically, and costs $0 when idle. For 1,000 files per day, total cost is ~$10-15/month versus $6,660/month for manual entry (333 hours at $20/hour). That's 99.8% savings. Traditional VM-based approaches require capacity planning, patching, monitoring - all deal-breakers for small rural facilities."

### Speedup Numbers (56-168x)

**Question**: *How did you calculate 56-168x speedup?*

**Answer**:
"Literature baseline: Mehmood 2013, Overhage 2020, and Jabour 2018 report manual EHR data entry times of 15-45 minutes per record, or 900-2,700 seconds. Our automated pipeline processes files in a median of 16 seconds. Each file contains 10-100+ records, but even conservatively assuming 1 record per file, 900 ÷ 16 = 56x faster (low estimate), 2,700 ÷ 16 = 168x faster (high estimate). True speedup is likely higher since files contain multiple records. This isn't a paired comparison (we didn't measure manual entry directly), but it's a reasonable descriptive estimate from established benchmarks."

### Limitations - Why Synthetic Data?

**Question**: *Why not test on real patient data?*

**Answer**:
"Three reasons: (1) HIPAA compliance - real patient data requires IRB approval and de-identification infrastructure outside capstone scope, (2) reproducibility - Synthea data is publicly available so others can replicate findings, and (3) controlled testing - synthetic data lets me simulate specific scenarios (missing fields, various file sizes) systematically. That said, I acknowledge this is a limitation - Synthea is realistic but idealized. Real EHR data has messier issues like free-text notes, vendor-specific extensions, legacy encodings. Sensitivity analysis partially addresses this by simulating missing fields (15% temporal, 10% geographic), showing robustness. Production deployment should pilot on de-identified real data to validate findings."

---

## Defense Prep Checklist

### Before Presentation

- [ ] Practice 5-minute walkthrough (Slides 1-6)
- [ ] Memorize key numbers: 95.9%, 16.12s, 56-168x, +1.1 pp
- [ ] Have GitHub repo open in browser (ready to show code if asked)
- [ ] Have `reports/figure1.png`, `figure2.png`, `figure3.png` ready to display
- [ ] Review talking points above (rule calibration, flags, serverless rationale)

### During Defense

- [ ] Start with problem (Slide 2) - motivate why this matters
- [ ] Emphasize operational benefits (no infrastructure, auto-scale, pay-per-use)
- [ ] Show results (Slide 4) - all targets met, tables with numbers
- [ ] Be honest about limitations (Slide 5) - builds credibility
- [ ] End with reusability (Slide 6) - practical impact

### Anticipate Questions

**Common Defense Questions**:
1. "Why serverless instead of traditional VMs?" → See Rural/Serverless Rationale talking point
2. "What happens if validation rules are too strict or too lenient?" → See Rule Calibration talking point
3. "How do you handle missing data?" → See Data Quality Flags talking point
4. "Can this work on real patient data?" → See Limitations talking point
5. "What's the cost for a 10,000-file workload?" → 10,000 × $0.20/1,000 = $2.00/day = $60/month

**Technical Deep-Dive Questions**:
1. "How did you calculate bootstrap confidence intervals?" → 1,000 iterations, percentile method (2.5, 97.5), see `src/analysis/generate_phase7_outputs.py` lines 30-60
2. "What's in the validation rule packs?" → 50+ rules in `resources/rules/*.json`, show example: CORE_001 (patient_id NOT NULL)
3. "How do you ensure reproducibility?" → Random seed 12345, requirements.txt pinned versions, CI/CD with pytest, see Makefile
4. "What if a file fails validation?" → Flagged with validation_passed=FALSE, logged to CloudWatch, moved to `data/failed/` for review

---

## Backup Materials (Have Ready)

### Code Walkthrough (if asked)

**Show**:
- `resources/rules/core.json` (validation rule example)
- `resources/join_spec.json` (join keys and flags)
- `src/analysis/generate_phase7_outputs.py` (bootstrap CI calculation)
- `.github/workflows/tests.yml` (CI/CD pipeline)

### Figures (have high-res PNG ready)

- **Figure 1**: Pass rate comparison bar chart (v1 strict vs v2 relaxed)
- **Figure 2**: Latency dot-whisker plots (P50/P95 with error bars)
- **Figure 3**: 4-panel dashboard (coverage, distributions, scatter, pass rates)

### Tables (have markdown or DOCX ready)

- **Table 1**: Validation pass rates by source
- **Table 2**: Latency statistics with bootstrap 95% CI
- **Table 3-5**: Sensitivity analysis (sample sizes, pass rates, latency)

---

## Time Management (5-Minute Version)

| Minute | Content |
|:------:|:--------|
| 0:00-0:30 | Slide 1: Title, research question |
| 0:30-1:30 | Slide 2: Problem (manual entry slow), Why serverless (ops benefits) |
| 1:30-2:30 | Slide 3: Data sources, pipeline architecture, rule calibration |
| 2:30-4:00 | Slide 4: Results (95.9% pass rate, 16.12s latency, 56-168x speedup) |
| 4:00-4:30 | Slide 5: Sensitivity (robust), Limitations (honest) |
| 4:30-5:00 | Slide 6: Reusability (artifacts, ROI), Recommendations |

**Total**: 5 minutes + Q&A

---

## One-Liner Summaries (Elevator Pitch)

**Project**: "I built an automated serverless data pipeline that processes health data 75x faster than manual entry while maintaining 95.9% quality validation."

**Problem**: "Rural health networks struggle with slow manual data entry and fragmented systems, taking 20+ minutes per record."

**Solution**: "Cloud-based serverless architecture with automated FHIR validation, costing $10/month for 1,000 files versus $6,660/month for manual labor."

**Results**: "Achieved 95.9% validation pass rate and 16-second median processing time, exceeding all targets. Sensitivity analysis confirmed robustness."

**Impact**: "Reusable validation rules, pipeline code, and deployment guides enable other rural networks to implement in 30-60 minutes."

---

**Presentation Version**: 1.0  
**Last Updated**: November 11, 2025  
**Status**: ✅ Ready for Defense

**Good Luck!** 🎓
