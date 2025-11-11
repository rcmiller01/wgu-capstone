# Capstone Proposal Reference

**Student**: Robert Miller (000982134)  
**Project Name**: A Paired t-Test Analysis of a Serverless FHIR Lakehouse for Streamlined and Consistent Rural Health Data Exchange  
**Topic**: Serverless FHIR Data Pipeline for Rural Healthcare Interoperability  
**End Date**: 4/24/2025

---

## Research Question

How can implementing a cloud-based, serverless FHIR-compliant data pipeline streamline health-data exchange, reduce operational friction, and raise data consistency across a distributed rural healthcare network while maintaining compliance and scalability?

---

## Hypotheses

**H₀** (Null): Implementation of the serverless FHIR pipeline will produce no statistically significant change in data consistency or timeliness compared with the current manual process.

**H₁** (Alternative): Implementation of the serverless FHIR pipeline will produce a statistically significant improvement in data consistency and timeliness as measured by a paired t-test (p < .05).

---

## Context

This study examines whether a serverless, FHIR-compliant data pipeline can make rural health-network data sharing more consistent, timely, and frictionless. Many small hospitals and clinics operate with fragmented systems and delayed data flow. By automating ingestion and validation within a lightweight serverless design, the project aims to demonstrate measurable improvement in how reliably information moves across the network. The focus is on the efficiency and quality of data movement rather than patient outcomes, aligning with the MSDA program's emphasis on applied analytics and measurable operational results.

### Contribution to the Field

**Contextual Novelty**: Most serverless health data demonstrations assume stable networks and enterprise operations. This research targets low-bandwidth, low-operations environments and proves viability through measurement rather than marketing materials. While existing literature examines FHIR adoption in large health systems, this study addresses the unique challenges of distributed, heterogeneous data sources common in rural networks with limited IT resources.

**Method Novelty**: The study introduces a portable validation framework (rule packs + harness) that travels across sources and vendors, producing comparable metrics. This approach enables objective comparison of data quality regardless of source system heterogeneity.

**Practical Artifacts**: The research delivers immediately reusable Infrastructure-as-Code (IaC), validation rule sets, and operational runbooks that can be deployed by other rural health networks without extensive customization.

### Success Criteria

**Latency Target**: P50 ≤ 30 seconds, P95 ≤ 120 seconds per file (100–10,000 rows), measured source-to-validated.

**Reliability**: ≥ 99% successful validations after auto-retry on transient errors; ≥ 95% reproducible runs from IaC.

**Cost Ceiling**: ≤ $X per 1,000 records end-to-end at typical clinic volumes; demonstrate 30–60% savings versus a minimal managed ETL stack.

**Resilience**: Offline-tolerant staging (e.g., durable queue + idempotent processors) with at-least-once semantics.

### Acknowledged Risks and Limitations

**Technical Constraints**: Cold-start variance and OCR latency may inflate tail latencies. Mitigation strategies include warmers/batching, with separate reporting of cold and hot distributions.

**Scope Boundaries**: PHI handling is out of scope; the study uses de-identified and synthetic data with documentation on how to extend the framework safely for production environments.

---

## Data Sources

**Primary Data Sources:**
- **Synthea Synthetic Health Records**: https://synthea.mitre.org/downloads
- **NHANES Public Health Data (CDC)**: https://www.cdc.gov/nchs/nhanes
- **Virginia Department of Health Data Portal**: https://data.virginia.gov/browse?tags=health
- **Radiology Imaging Dataset (RSNA Chest X-Ray)**: https://www.kaggle.com/datasets/nih-chest-xrays/data

**Dataset Characteristics:**
- ~7,000 structured records
- ~1,000 radiology images
- Mix of structured (EHR tables), semi-structured (HL7/JSON), and unstructured (images) data
- Fully de-identified and HIPAA compliant

**Limitations**: Baseline ingestion performance must be inferred rather than measured directly. Estimates drawn from time-motion studies reporting 15-45 minutes per record for manual entry (Mehmood et al., 2013; Overhage et al., 2020; Jabour et al., 2018; UCSF Healthforce, 2024).

**Delimitations**: Study focuses on data engineering performance and accuracy, not clinical impact or outcomes.

---

## Data Treatment

Each dataset will be downloaded in CSV, JSON, or image format and loaded into a serverless cloud data lake. 

**Missing Data Handling:**
- Records missing key identifiers (patient_id, encounter_date) will be removed or imputed
- Mean for numeric fields, mode for categorical
- Prevents distortion in statistical tests (Swalin, 2018)

**Outlier Treatment:**
- Values beyond 1.5 × IQR will be winsorized or flagged for review

**Derived Variables:**
- `latency_sec`: captures processing time
- `validation_pass_bool`: captures data quality

**Validation:**
- Great Expectations (2024) for automated validation and schema enforcement
- Audit trails of successful and failed ingestions

**Paired Sample Design:**
- Process identical inputs through two paths:
  - Modeled manual path (20-minute, 85% baseline performance)
  - Automated serverless FHIR pipeline
- Provides direct before-and-after comparison for paired t-test

---

## Statistical Methods

**Primary Method**: Paired-samples t-test (α = .05)

**Normality Checks:**
- Q-Q Plot
- Shapiro-Wilk test (Evans, 2020)

**Alternative if non-normal**: Wilcoxon Signed-Rank test (non-parametric)

**Effect Size**: Cohen's d to quantify magnitude of improvement

**Tools:**
- Python (Pandas, SciPy, Great Expectations) for analysis and validation
- Power BI for visualization of data flow and quality patterns

---

## Tool Justification

Python provides scalable and reproducible analytics and integrates well with AWS and Azure serverless environments (Evans, 2020). According to *Data Science Using Python and R* (WGU, 2023), Python's libraries allow efficient statistical testing within modern data architectures. Its combination of flexibility and industry adoption makes it a practical choice for a study focused on data integration and workflow improvement.

---

## Expected Outcomes

The project will determine whether a serverless FHIR pipeline can make health data exchange more consistent, timely, and scalable for rural networks. 

**Support for H₁ requires**: Paired t-test p-value < .05

**Practical Impact**: A confirmed improvement would demonstrate that the proposed architecture:
- Reduces bottlenecks in data movement
- Raises overall record accuracy
- Increases trust levels for health system decision makers (Santos & Costa, 2020)

---

## IRB Status

✓ This project does not involve human subjects research and is exempt from WGU IRB review.

---

## Key References

*(See references/apa.bib for complete bibliography)*

- Evans, R. J. (2020). Business analytics. Western Governors University.
- Great Expectations. (2024). The leading tool for data quality validation.
- Jabour, A. M., et al. (2018). Toward timely data for cancer research. Journal of Registry Management, 45(1), 12-18.
- Mehmood, A., et al. (2013). Development and pilot implementation of a data collection system. BMC Public Health, 13, 709.
- Overhage, J. M., et al. (2020). Physician time spent using the electronic health record. JAMA Network Open, 3(6), e206700.
- Santos, M., & Costa, C. (2020). Big data: Concepts, warehousing, and analytics. WGU.
- Swalin, A. (2018). How to Handle Missing Data. Towards Data Science.
- Synthea Project. (2024). Open synthetic patient generator. MITRE Corporation.
- UCSF Healthforce Center. (2024). Cancer Registrar Workload and Staffing Study.
