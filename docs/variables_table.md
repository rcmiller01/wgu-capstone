# Variable Definitions and Roles

This table defines all variables used in the serverless FHIR pipeline analysis, organized by their role in the study.

## Outcomes (Dependent Variables - DV)

| Variable | Role | Type | Scale | Notes |
|----------|------|------|-------|-------|
| `latency_sec` | Primary DV | numeric | continuous | End-to-end ingest + validate wall time per file/batch. Use P50/P95 for robustness. |
| `validation_pass_bool` | Secondary DV | boolean | binary | "Passed all validation checks." Consider a richer `validation_error_count` for effect sizes. |

## Explanatory Variables (Independent Variables / Covariates)

These are variables actively tested or modeled in the analysis.

| Variable | Role | Type | Scale | Notes |
|----------|------|------|-------|-------|
| `source_type` | IV | categorical | nominal | e.g., CSV, HL7, FHIR JSON, PDF(OCR), DICOM metadata. Likely to shift both latency and pass rate. |
| `schema_variant` | IV | categorical | nominal | Different column sets/layouts; include "strict vs permissive" mapping. |
| `record_count` | IV | numeric | count | Strong predictor of latency; log-transform if heavy-tailed. |
| `file_size_mb` | IV | numeric | continuous | Correlated with `record_count`; check for multicollinearity. |
| `compression` | IV | categorical | nominal | none/gzip/zip. Often reduces transfer time but increases CPU. |
| `transport_protocol` | IV | categorical | nominal | s3/http(s)/sftp. Captures IO path differences. |
| `batch_size` | IV | numeric | count | Rows per write/commit; can affect IO churn. |
| `concurrency_level` | IV | numeric | count | Workers/threads; interacts with storage + CPU. |
| `time_of_day` | IV or control | categorical | ordinal | Captures shared-infra contention; bucket into dayparts. |
| `network_rtt_ms` | Control | numeric | continuous | Measured at ingest; reduces omitted-variable bias for "slow network" days. |
| `cpu_utilization_pct` | Control | numeric | continuous | Node pressure; sample during run. |
| `storage_throughput_mb_s` | Control | numeric | continuous | From system metrics; IO bottlenecks. |

## Descriptive / Stratification Variables

These are not causal levers but used for grouping and context.

| Variable | Role | Type | Scale | Notes |
|----------|------|------|-------|-------|
| `health_district_id` | Stratifier | categorical | nominal | Good for fixed effects if infra differs by district. Don't treat as causal. |
| `encounter_date` | Descriptive | date | — | Only needed if your data selection depends on time; avoid storing exact dates if not needed. |
| `district_rate` | Context | numeric | continuous | If this is a public district-level metric, fine—but it's not needed for pipeline timing unless you hypothesize a relationship. |

## Variables to EXCLUDE (Privacy / Not Useful)

| Field | Why Exclude / Replace |
|-------|----------------------|
| `patient_id` | Direct identifier; not needed for timing/validation. If absolutely necessary for referential integrity, replace with a one-way `customer_id`/hash and keep mapping off-repo. |
| `image_path` | Can reveal storage layout or PHI context. If you need to reference a blob, store a non-reversible content hash or a synthetic ID, not a path. |
| `lab_result_value` | Clinical content isn't relevant to pipeline speed/validation unless you're validating value ranges; if used, aggregate to a count of out-of-range values rather than raw results. |

## Alignment to Hypotheses

### H₁ (Latency)
Median/95th-percentile `latency_sec` differs by `source_type` and scales with `record_count`/`file_size_mb`.

### H₂ (Quality)
`validation_pass_bool` (or error count) differs by `schema_variant` and `source_type`.

### H₃ (Infrastructure)
After controlling for `network_rtt_ms`, `cpu_utilization_pct`, and `storage_throughput_mb_s`, `concurrency_level` and `batch_size` have measurable effects on latency.

## Practical Guardrails

1. **Use patient-neutral, file-level rows**: One row = one ingest attempt (with a `run_id`)

2. **Predefine IV categories**:
   - **Designed** (you set them): `batch_size`, `concurrency_level`, `compression`, `transport_protocol`
   - **Observational** (you measure them): `network_rtt_ms`, `cpu_utilization_pct`, `storage_throughput_mb_s`
   - This distinction matters for ANOVA vs. regression analysis

3. **Prefer derived counts/flags over raw PHI-adjacent fields**: 
   - Example: "rows dropped for HIPAA-sensitive values" as a numeric rather than storing actual values
