# Variable Table Summary - For Proposal Submission

This table provides a concise overview of key variables used in the serverless FHIR pipeline analysis.

## Primary Variables

| Variable Name | Role | Type | Scale | Description |
|---------------|------|------|-------|-------------|
| `latency_sec` | **Primary DV** | Numeric | Continuous | End-to-end ingest + validate wall time per file/batch (source-to-validated) |
| `validation_pass_bool` | **Secondary DV** | Boolean | Binary | Pass/fail status: "Passed all validation checks" |
| `source_type` | IV | Categorical | Nominal | Data source format (CSV, HL7, FHIR JSON, PDF/OCR, DICOM metadata) |
| `schema_variant` | IV | Categorical | Nominal | Column sets/layouts ("strict" vs "permissive" mapping) |
| `record_count` | IV | Numeric | Count | Number of records per file/batch; predictor of latency |
| `file_size_mb` | IV | Numeric | Continuous | File size in megabytes; correlated with record_count |
| `compression` | IV | Categorical | Nominal | Compression type (none/gzip/zip) |
| `transport_protocol` | IV | Categorical | Nominal | Transport method (s3/https/sftp) |
| `batch_size` | IV | Numeric | Count | Rows per write/commit operation |
| `concurrency_level` | IV | Numeric | Count | Number of workers/threads in parallel |
| `health_district_id` | Stratifier | Categorical | Nominal | Virginia health district identifier (for fixed effects) |

## Control Variables (Infrastructure/Environment)

| Variable Name | Role | Type | Scale | Description |
|---------------|------|------|-------|-------------|
| `network_rtt_ms` | Control | Numeric | Continuous | Network round-trip time measured at ingest |
| `cpu_utilization_pct` | Control | Numeric | Continuous | Node CPU pressure during processing |
| `storage_throughput_mb_s` | Control | Numeric | Continuous | Storage I/O throughput from system metrics |
| `time_of_day` | Control | Categorical | Ordinal | Time bucket (daypart) to capture infrastructure contention |

## Excluded Variables (Privacy/Not Applicable)

| Variable Name | Reason for Exclusion |
|---------------|---------------------|
| `patient_id` | Direct PHI identifier; not needed for pipeline performance measurement |
| `image_path` | May reveal storage layout or PHI context; use content hash instead |
| `lab_result_value` | Clinical data not relevant to pipeline speed/validation metrics |
| `encounter_date` | Temporal identifier; only needed if time-dependent analysis required |

---

## Variable Role Definitions

- **Primary DV**: Main outcome variable being measured (latency)
- **Secondary DV**: Additional outcome variable (data quality/validation)
- **IV**: Independent variable - factors manipulated or observed to test effects
- **Control**: Variable measured to reduce confounding (not a causal lever)
- **Stratifier**: Grouping variable for fixed effects or subgroup analysis

---

## Alignment to Research Hypotheses

### H₁: Latency Improvement
- **Outcome**: `latency_sec` (P50/P95 distributions)
- **Predictors**: `source_type`, `record_count`, `file_size_mb`, `compression`, `transport_protocol`
- **Controls**: `network_rtt_ms`, `cpu_utilization_pct`, `storage_throughput_mb_s`

### H₂: Validation Quality
- **Outcome**: `validation_pass_bool` (success rate)
- **Predictors**: `schema_variant`, `source_type`, `compression`

### H₃: Infrastructure Efficiency
- **Outcome**: `latency_sec` (adjusted)
- **Designed IVs**: `batch_size`, `concurrency_level`
- **Controls**: `network_rtt_ms`, `cpu_utilization_pct`, `storage_throughput_mb_s`

---

**Note**: For complete variable specifications including measurement details and practical guardrails, see [`docs/variables_table.md`](variables_table.md).
