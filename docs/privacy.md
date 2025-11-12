# Privacy and De-identification

## Overview

This document describes privacy protections implemented for medical imaging data in the capstone project, aligned with HIPAA Safe Harbor standards and DICOM PS3.15 Annex E de-identification guidelines.

## De-identification Standards

### HIPAA Safe Harbor Compliance

The project implements 18 HIPAA Safe Harbor identifiers removal:

1. **Names**: Patient names removed from all DICOM tags
2. **Geographic subdivisions**: Addresses, zip codes (retain state only)
3. **Dates**: Dates shifted or aggregated (retain year for analysis)
4. **Telephone/fax numbers**: Removed
5. **Email addresses**: Removed
6. **Social Security numbers**: Not present in imaging data
7. **Medical record numbers**: Pseudonymized with one-way hash
8. **Health plan numbers**: Not applicable
9. **Account numbers**: Removed
10. **Certificate/license numbers**: Removed
11. **Vehicle identifiers**: Not applicable
12. **Device identifiers**: Device serial numbers removed
13. **Web URLs**: Not applicable
14. **IP addresses**: Not applicable
15. **Biometric identifiers**: Not applicable (images are clinical data, not biometric ID)
16. **Full-face photos**: Checked via `BurnedInAnnotation` flag
17. **Other unique identifiers**: Removed
18. **Ages >89**: Ages capped at 90+ (none in current dataset)

### DICOM PS3.15 Annex E

The `sanitize_dicom.py` script implements DICOM de-identification profile:

- **Remove**: Direct identifiers (names, IDs, dates)
- **Hash**: Indirect identifiers for linking (Patient ID, Study ID)
- **Retain**: Clinical metadata needed for analysis (age, sex, contrast)
- **Flag**: Potential burned-in text for manual review

## Pseudonymization

### One-Way Hashing

Patient and study identifiers are hashed using SHA-256 with salt:

```python
hash = SHA256(salt + original_id)[:16]
```

**Properties**:
- **One-way**: Cannot reverse hash to original ID
- **Deterministic**: Same ID always produces same hash (enables linking)
- **Collision-resistant**: Different IDs produce different hashes

**Use Cases**:
- Link imaging studies to cohort data
- Track same patient across multiple studies
- Maintain referential integrity without exposing PHI

### Salting Strategy

- **Salt**: `"capstone_2025"` (consistent across all scripts)
- **Stored**: In code (not secret for de-identified research data)
- **Production**: Use environment variable for per-deployment salt

## Burned-In PHI Detection

### Automated Checks

The `sanitize_dicom.py` script flags files for manual review:

1. **Explicit flag**: `BurnedInAnnotation=YES` in DICOM metadata
2. **Text patterns**: Image comments containing "PATIENT", "NAME", "MRN", "DOB", "SSN"
3. **Description fields**: Series/Study descriptions with identifiers

### Manual Review Process

Files flagged for burned-in PHI require:

1. **Visual inspection**: Open image and check for visible text overlays
2. **OCR screening**: Run optical character recognition to detect embedded text
3. **Exclusion**: Remove images with irremovable PHI from dataset
4. **Documentation**: Log excluded files in `sanitization_report.json`

## Data Governance

### Local Storage

- **Location**: `data/lake/bronze/`, `data/lake/silver/`, `data/lake/gold/`
- **Access**: File system permissions (user-only read/write)
- **Encryption**: BitLocker/FileVault recommended for laptop storage
- **Retention**: Delete after project completion per IRB protocol

### Cloud Storage (Optional)

If publishing to AWS S3:

- **Bucket encryption**: Enable S3-SSE (server-side encryption)
- **Access control**: Restrict to project IAM role only
- **Logging**: Enable CloudTrail for audit trail
- **Lifecycle**: Auto-delete after 90 days (configurable)

### IAM Policies

See `infrastructure/iam_policies/s3_glue_athena.json` for least-privilege access:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject"
  ],
  "Resource": "arn:aws:s3:::capstone-bucket/datalake/*"
}
```

## Privacy Risk Assessment

### Current Dataset (CT Sample Images)

- **Source**: De-identified per HIPAA Safe Harbor
- **Ages**: 39-83 years (no ages >89)
- **Geographic scope**: No addresses or zip codes
- **Dates**: No specific dates (study dates removed during ingestion)
- **Risk level**: **Low** (already de-identified, no PHI in metadata)

### Residual Risks

1. **Burned-in text**: Some DICOM files may have visible patient info in image pixels
   - **Mitigation**: Automated flagging + manual review
   - **Residual risk**: Low (CT scans rarely have burned-in text)

2. **Re-identification**: Hashed IDs could theoretically be reversed if salt exposed
   - **Mitigation**: Use unique salt per deployment, rotate periodically
   - **Residual risk**: Very low (SHA-256 is cryptographically secure)

3. **Small cell sizes**: Age bins with <5 patients could enable re-identification
   - **Mitigation**: Aggregate to 5-year bins (50-54, 55-59, etc.)
   - **Residual risk**: Low (100 patients, well-distributed ages)

## Compliance Verification

### Validation Checks

The `make deidentify` target runs automated checks:

```bash
make deidentify
# Checks:
# - No PHI tags present in DICOM headers
# - All files flagged for burned-in text reviewed
# - Hashed IDs cannot be reversed (spot check)
# - Ages <90 (no capping needed)
# - No free-text fields with suspicious patterns
```

### Audit Trail

All de-identification actions logged:

- **File**: `data/lake/silver/imaging/sanitization_report.json`
- **Contents**:
  - Input/output file paths
  - Tags removed (list)
  - Tags pseudonymized (original → hash)
  - Burned-in warnings (if any)
  - Timestamp

## Ethics and IRB

### Research Use

This project is **educational/research only**:

- **Purpose**: Demonstrate serverless FHIR pipeline for capstone
- **Population**: De-identified CT imaging cases (no patient contact)
- **IRB status**: Exempt (no human subjects, de-identified data)

### Clinical Use Disclaimer

**This pipeline is NOT approved for clinical use.**

For production deployment:

1. **IRB approval**: Required for any patient data processing
2. **HIPAA Business Associate Agreement**: Needed with cloud provider
3. **Security assessment**: Penetration testing, vulnerability scan
4. **Validation**: Clinical validation study per FDA guidance
5. **Monitoring**: Ongoing privacy impact assessments

## References

- HIPAA Safe Harbor: 45 CFR §164.514(b)(2)
- DICOM PS3.15 Annex E: Security and System Management Profiles
- NIST SP 800-122: Guide to Protecting the Confidentiality of PII
- OCR Guidance on De-identification: [HHS.gov](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/)

## Contact

For privacy questions:

- **Project Lead**: Robert Miller
- **Email**: robert.miller@wgu.edu
- **Repository**: https://github.com/rcmiller01/wgu-capstone

---

## Simulated Patient-Image Linkage

**IMPORTANT**: The patient-image linkage in this project is **synthetic and simulated for demonstration purposes only**. It does NOT represent real patient-image associations.

### Linkage Method

The `build_link_table.py` script creates a Gold layer table (`customer_image_link.parquet`) that links imaging instances to patient records using a **deterministic hash-based mapping**:

```python
customer_id = hash_128(instance_uid + global_seed) % N + 1
```

Where:
- `instance_uid`: DICOM SOPInstanceUID (unique identifier for each image)
- `global_seed`: Fixed string "capstone_2025" for reproducibility
- `hash_128`: First 128 bits (16 bytes) of SHA-256 hash
- `N`: Total number of patients in Synthea cohort
- Result: customer_id in range [1, N]

### Limitations and Considerations

1. **No Real Linkage**: The CT Sample Images dataset and Synthea patient records are completely independent. The hash-based mapping creates a **mathematically deterministic but clinically meaningless** association.

2. **Demonstration Purpose**: This linkage enables:
   - Testing ETL pipeline end-to-end
   - Demonstrating data lake architecture (Bronze→Silver→Gold)
   - Showing how imaging and clinical data could be joined in analytics queries
   - Illustrating HIPAA-compliant pseudonymization techniques

3. **Production Requirements**: A real-world deployment would require:
   - **Proper MRN/Encounter Linkage**: Images linked via Medical Record Number (MRN) or encounter ID from hospital information systems
   - **IRB Approval**: Patient consent and institutional review for linkage
   - **Data Use Agreements**: Legal agreements between imaging source and clinical data source
   - **Validation**: Clinical review to ensure linkage accuracy

4. **Disclosure**: All analysis results must clearly state that patient-image associations are synthetic and not based on actual clinical records.

### Deterministic Mapping Benefits

The hash-based approach provides:
- **Reproducibility**: Same instance_uid always maps to same customer_id
- **Distribution**: Modulo operation distributes images across patient cohort
- **Pseudonymization**: Linkage doesn't expose PHI directly
- **Simplicity**: No complex matching logic or external databases required

This approach is acceptable for academic demonstration but should NOT be used for clinical decision-making or research conclusions about specific patient conditions.

---

**Last Updated**: January 2025  
**Status**: Compliant with HIPAA Safe Harbor for research use

