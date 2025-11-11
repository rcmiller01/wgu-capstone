# Data Sources Documentation

**Project**: Serverless FHIR Data Pipeline for Rural Healthcare Interoperability  
**Purpose**: Document all data sources with volume, quality, and accessibility characteristics

---

## Overview

This study utilizes four complementary public and synthetic data sources that collectively represent the heterogeneous data landscape of rural healthcare networks. The sources provide structured electronic health records, public health survey data, state-level health metrics, and medical imaging—mirroring the variety of data types that rural health IT systems must integrate.

### Rationale for Selection

1. **Heterogeneity**: Captures structured (CSV), semi-structured (JSON/HL7), and unstructured (DICOM images) formats
2. **Realism**: Synthea generates clinically realistic patient timelines; NHANES provides real survey instruments; VDH supplies actual public health metrics
3. **Accessibility**: All sources are publicly available without IRB requirements
4. **HIPAA Compliance**: De-identified or synthetic, eliminating PHI concerns
5. **Rurality Context**: Virginia state data enables geographic stratification by rural health districts

---

## Source 1: Synthea Synthetic Health Records

**Provider**: MITRE Corporation  
**URL**: <https://synthea.mitre.org/downloads>  
**License**: Apache 2.0 (Open Source)

### Description

Synthea is an open-source synthetic patient generator that creates realistic but fictional patient records with complete longitudinal health histories. It models diseases, treatments, medications, encounters, and outcomes based on publicly available health statistics and clinical guidelines.

### Volume & Sparsity

- **Expected Volume**: ~5,000–10,000 patient records (configurable)
- **Record Depth**: Each patient includes 20–100+ encounters spanning multiple years
- **Generated Fields**: Demographics, conditions, medications, procedures, observations, immunizations, encounters
- **Sparsity Patterns**:
  - ~5–10% missingness in optional fields (allergies, careplan goals)
  - Social history fields (smoking, alcohol) ~15–20% sparse
  - Complete coverage for core demographics and encounter data
- **Temporal Coverage**: Generates data from birth to present across full patient lifespan

### Reliability

- **Organizational Backing**: MITRE Corporation (Federally Funded R&D Center)
- **Validation**: Disease progressions based on CDC statistics, clinical guidelines (e.g., ACC/AHA for cardiovascular)
- **Maintenance**: Active development; regular updates to disease modules
- **Known Limitations**:
  - Simplified disease models may not capture rare conditions
  - Population demographics default to Massachusetts unless customized
  - May underrepresent rural-specific health patterns (transport barriers, provider scarcity)

### Usability

- **Formats Available**: FHIR JSON, C-CDA XML, CSV (multiple tables)
- **Documentation**: Excellent—comprehensive wiki, module specifications, API docs
- **Access Method**: Command-line tool (Java) or downloadable pre-generated datasets
- **Technical Prerequisites**: Java 11+ for generation; none for pre-generated files
- **Learning Curve**: Low for CSV; moderate for FHIR/C-CDA customization

### Durability

- **Long-term Availability**: High—hosted on GitHub, backed by MITRE with DoD/federal funding
- **Versioning**: GitHub releases with semantic versioning (v3.x currently)
- **Archival Status**: Code repository ensures regenerability even if downloads become unavailable
- **Mirrors**: GitHub (primary), Maven Central (JAR artifacts)

### Access Information

- **Download**: <https://synthea.mitre.org/downloads> (pre-generated) or <https://github.com/synthetichealth/synthea> (source)
- **API**: None (batch generation only)
- **Authentication**: Not required
- **Cost**: Free

---

## Source 2: NHANES (National Health and Nutrition Examination Survey)

**Provider**: Centers for Disease Control and Prevention (CDC) / National Center for Health Statistics (NCHS)  
**URL**: <https://www.cdc.gov/nchs/nhanes>  
**License**: Public Domain (U.S. Government)

### Description

NHANES is a nationally representative survey combining interviews, physical examinations, and laboratory tests to assess the health and nutritional status of adults and children in the United States. Conducted biennially since 1999, it provides gold-standard public health metrics.

### Volume & Sparsity

- **Expected Volume**: ~2,000–5,000 records (subset of 2017–2020 cycles)
- **Survey Components**: Demographics, dietary, examination, laboratory, questionnaire
- **Generated Fields**: ~1,500+ variables across modules
- **Sparsity Patterns**:
  - Examination data: 5–15% missing due to participant refusal or contraindications
  - Laboratory results: 10–25% missing (insufficient sample, equipment failure)
  - Dietary recalls: ~20% missing for second-day recall
  - Income/sensitive questions: 15–30% missing or coded as "refused"
- **Temporal Coverage**: 2017–March 2020 (most recent complete cycle)

### Reliability

- **Organizational Backing**: CDC/NCHS—authoritative U.S. health statistics agency
- **Validation**: Complex survey design with weights for national representativeness; rigorous QA/QC protocols
- **Maintenance**: Biennial releases; data files remain permanently available
- **Known Limitations**:
  - 2019–2020 cycle incomplete due to COVID-19 disruption
  - Oversamples certain demographics; requires survey weights for population inference
  - Not rural-specific (national sample with urban/rural stratification available)

### Usability

- **Formats Available**: SAS XPT (primary), SAS transport files convertible to CSV
- **Documentation**: Excellent—detailed codebooks, variable descriptions, analytic guidelines
- **Access Method**: Direct download (FTP) or CDC WONDER query system
- **Technical Prerequisites**: SAS, R (foreign/haven), or Python (pandas, xport) for XPT parsing
- **Learning Curve**: Moderate—complex survey design and weighting require statistical expertise

### Durability

- **Long-term Availability**: Very High—statutory mandate; archived by National Archives (NARA)
- **Versioning**: Cycle-based (e.g., 2017–2018, 2019–March 2020); files never modified post-release
- **Archival Status**: Permanent government records
- **Mirrors**: CDC FTP (primary), ICPSR (secondary archive)

### Access Information

- **Download**: <https://wwwn.cdc.gov/nchs/nhanes/> (by cycle/component)
- **API**: None (batch download only)
- **Authentication**: Not required
- **Cost**: Free

---

## Source 3: Virginia Department of Health Data Portal

**Provider**: Virginia Department of Health (VDH)  
**URL**: <https://data.virginia.gov/browse?tags=health>  
**License**: Open Data (varies by dataset; typically CC-BY or public domain)

### Description

VDH publishes county-level and health district-level statistics on health program utilization, social determinants of health, and environmental health indicators. This study utilizes two complementary datasets: **Virginia WIC Participation Data** (nutritional assistance program metrics) and **Health Opportunity Index** (composite measure of community health determinants). These datasets support stratified analysis by locality and health equity assessment.

### Volume & Sparsity

- **Expected Volume**: ~500–2,000 aggregated records (locality-level)
- **Geographic Granularity**: County (n=133) and/or Health District (n=35) levels
- **Datasets Used**:
  - **Virginia WIC Participation Data**: Participation counts by locality for Women, Infants, and Children nutritional program
  - **Health Opportunity Index (HOI)**: Composite scores incorporating education, economic, environmental, and social factors
- **Generated Fields**: Participation rates, demographic breakdowns, composite health determinant scores, locality identifiers
- **Sparsity Patterns**:
  - Small counts (<10) may be suppressed for privacy → ~5–10% censored cells
  - Rural localities may have zero participants for certain programs → ~10% structural zeros
  - HOI components: <5% missing (high completeness for composite indices)
- **Temporal Coverage**: Varies by dataset; WIC typically annual, HOI periodically updated

### Reliability

- **Organizational Backing**: Virginia Department of Health (state public health authority)
- **Validation**: 
  - WIC data: Federal program reporting requirements ensure data quality
  - HOI: Composite index methodology published and peer-reviewed (VCU Center on Society and Health)
- **Maintenance**: Active; datasets updated annually or as new data becomes available
- **Known Limitations**:
  - Aggregated data limits individual-level analysis
  - Suppression rules may reduce granularity in rural areas
  - HOI composite scores may mask variance in underlying components
  - WIC participation reflects program enrollment, not overall nutritional need

### Usability

- **Formats Available**: CSV (primary), JSON via Socrata API
- **Documentation**: Good—data dictionaries and methodology notes; variable for completeness
- **Access Method**: Web download or Socrata Open Data API (SODA)
- **Technical Prerequisites**: None for CSV; API key recommended for bulk/automated access
- **Learning Curve**: Low for CSV; moderate for API scripting

### Durability

- **Long-term Availability**: Moderate—state funding dependent; no statutory permanence guarantee
- **Versioning**: Datasets may be replaced rather than versioned; snapshots not always retained
- **Archival Status**: No formal archival; relies on Socrata (Tyler Technologies) hosting
- **Mirrors**: None identified

### Access Information

- **Download**: <https://data.virginia.gov/browse?tags=health> (browse and filter)
- **API**: Socrata SODA API (<https://dev.socrata.com>)
- **Authentication**: API token (free registration) for rate limit increases
- **Cost**: Free

---

## Source 4: NIH Chest X-Ray Dataset (ChestX-ray14 / CheXpert derivatives)

**Provider**: National Institutes of Health (NIH) via Kaggle / Stanford ML Group  
**URL**: <https://www.kaggle.com/datasets/nih-chest-xrays/data>  
**License**: CC0 (Public Domain) for NIH; varies for derivatives

### Description

A large-scale dataset of chest X-ray images with weak supervision labels for 14 common thoracic pathologies. Originally released by NIH Clinical Center; widely used for computer vision and radiology AI research. Represents the "unstructured data" component of the pipeline.

### Volume & Sparsity

- **Expected Volume**: ~1,000–5,000 images (subset of 112,120 total)
- **Image Characteristics**: DICOM format, ~1024×1024 pixels, 8-bit grayscale
- **Metadata Fields**: Patient ID (anonymized), image view (PA/AP/lateral), pathology labels, bounding boxes (if present)
- **Sparsity Patterns**:
  - ~60% of images labeled "No Finding" (majority class imbalance)
  - ~40% have ≥1 pathology label (some multi-label)
  - Bounding boxes available for only ~1,000 images (~1% of dataset)
  - Metadata missingness: <1% (high completeness)
- **Temporal Coverage**: Images from 1992–2015

### Reliability

- **Organizational Backing**: NIH Clinical Center (world's largest research hospital)
- **Validation**: Labels extracted via NLP from radiology reports (weak supervision); subset validated by radiologists
- **Maintenance**: Static dataset (no updates); published 2017
- **Known Limitations**:
  - NLP-derived labels have ~10–15% false positive/negative rate (Rajpurkar et al., 2017)
  - Class imbalance favors "No Finding"
  - Patient demographics not included (only anonymized IDs)
  - Not representative of rural imaging (tertiary research hospital source)

### Usability

- **Formats Available**: PNG (converted from DICOM), CSV metadata
- **Documentation**: Good—original paper (Wang et al., 2017), Kaggle data dictionary
- **Access Method**: Kaggle download (requires free account) or NIH Box (direct)
- **Technical Prerequisites**: Large storage (~42GB); DICOM tools (pydicom, dcmtk) if using original format
- **Learning Curve**: Low for metadata; moderate for DICOM processing

### Durability

- **Long-term Availability**: High—NIH commitment + Kaggle permanence for popular datasets
- **Versioning**: Static v1.0; no planned updates
- **Archival Status**: NIH Box serves as permanent archive
- **Mirrors**: Kaggle (primary), NIH Box (<https://nihcc.app.box.com/v/ChestXray-NIHCC>)

### Access Information

- **Download**: <https://www.kaggle.com/datasets/nih-chest-xrays/data> or <https://nihcc.app.box.com/v/ChestXray-NIHCC>
- **API**: None (batch download only)
- **Authentication**: Free Kaggle or Box account
- **Cost**: Free

---

## Aggregate Characteristics

### Combined Volume

| Source | Records | Images | Total Data Size |
|--------|---------|--------|-----------------|
| Synthea | ~5,000–10,000 patients | 0 | ~500MB–2GB (JSON) |
| NHANES | ~2,000–5,000 | 0 | ~100–500MB (XPT/CSV) |
| Virginia DoH | ~500–1,000 aggregates | 0 | ~10–50MB (CSV) |
| NIH Chest X-Ray | ~1,000–5,000 | ~1,000–5,000 | ~5–20GB (PNG) |
| **TOTAL** | **~8,500–21,000** | **~1,000–5,000** | **~6–23GB** |

### Overall Sparsity Patterns

- **Structured Data (Synthea, NHANES, VDH)**: 5–30% missingness depending on field sensitivity
- **Image Metadata**: <5% missingness (high completeness)
- **Primary Keys**: 100% coverage (patient_id, encounter_id, image_id)
- **Clinical Values**: 10–25% typical for lab results, vital signs

### Quality Summary

| Dimension | Assessment | Notes |
|-----------|------------|-------|
| **Completeness** | Good | Core fields well-populated; optional/sensitive fields sparse |
| **Accuracy** | High | Synthea validated against clinical guidelines; NHANES gold-standard; VDH statutory reporting |
| **Consistency** | Moderate | Format heterogeneity (CSV/JSON/XPT/DICOM) requires normalization |
| **Timeliness** | Good | NHANES/VDH updated regularly; Synthea/NIH static but regenerable |
| **Provenance** | Excellent | All sources from authoritative organizations with clear lineage |

---

## Limitations

**Limitations** are external constraints beyond the researcher's control that may affect study validity.

### 1. Synthetic Data Realism

**Constraint**: Synthea generates data based on statistical models, not actual patient trajectories.

**Impact**: May not capture rare edge cases, comorbidity interactions, or rural-specific social determinants (e.g., transport barriers, provider scarcity).

**Mitigation**: Validate pipeline performance on both Synthea and real public health data (NHANES, VDH) to demonstrate generalizability.

### 2. Baseline Performance Inference

**Constraint**: No live manual data entry process is available to measure actual baseline ingestion time and error rates.

**Impact**: Baseline estimates (20 minutes/record, 85% accuracy) are derived from time-motion studies in other contexts, introducing uncertainty.

**Mitigation**: Use conservative estimates from peer-reviewed literature; perform sensitivity analysis across baseline range (15–45 minutes); document assumptions transparently.

### 3. Geographic and Demographic Biases

**Constraint**: NHANES is nationally representative but not rural-specific; NIH imaging data comes from a tertiary research hospital; Synthea defaults to Massachusetts demographics.

**Impact**: Results may not fully generalize to Appalachian, Deep South, or Southwestern rural contexts with distinct health profiles.

**Mitigation**: Use Virginia state data for rural stratification; acknowledge geographic limitations in discussion; recommend future validation in target regions.

### 4. Temporal Coverage Gaps

**Constraint**: NHANES 2019–2020 incomplete (COVID disruption); some VDH historical data not digitized; NIH images stop at 2015.

**Impact**: Cannot assess temporal trends or recent changes in data patterns.

**Mitigation**: Focus on pipeline performance (which is time-invariant) rather than epidemiological trends; use most recent complete datasets.

### 5. NLP-Derived Image Labels

**Constraint**: NIH chest X-ray labels extracted via NLP from reports have ~10–15% error rate.

**Impact**: Validation pass rates for imaging data may include label noise unrelated to pipeline quality.

**Mitigation**: Treat image validation as OCR/metadata extraction test (not clinical accuracy); report validation performance separately by data type.

---

## Delimitations

**Delimitations** are researcher-chosen scope boundaries that define what the study will and will not address.

### 1. Focus on Data Engineering, Not Clinical Outcomes

**Boundary**: Study measures pipeline latency and data quality validation, not patient health outcomes, diagnostic accuracy, or care quality.

**Justification**: Aligns with MSDA program's emphasis on applied analytics and operational improvement. Clinical outcome research requires IRB approval, longitudinal cohorts, and clinical domain expertise beyond the scope of a data analytics capstone.

**Exclusion**: Clinical decision support, treatment effectiveness, patient safety metrics.

### 2. Scope Limited to Four Data Types

**Boundary**: Structured (CSV/tables), semi-structured (JSON/HL7), unstructured (text/OCR), and images (DICOM/PNG). Excludes streaming/real-time data, genomics, wearables, and claims data.

**Justification**: These four types represent the majority of rural health IT data exchange scenarios (EHR, lab interfaces, faxes/PDFs, radiology). Including additional types would dilute focus without proportional insight gain.

**Exclusion**: HL7 v2 message streams, FHIR subscriptions, genomic VCF files, wearable time-series, insurance claims (837/835 EDI).

### 3. Virginia Geographic Context

**Boundary**: State-level health data sourced from Virginia Department of Health; health district stratification specific to Virginia's 35 districts.

**Justification**: Provides realistic geographic stratification for rural vs. urban comparisons. Virginia's mix of Appalachian, coastal, and suburban regions offers useful diversity. Constraining to one state simplifies data governance and licensing.

**Exclusion**: Multi-state analyses, tribal health systems, territories (Puerto Rico, U.S. Virgin Islands).

### 4. Synthetic and De-identified Data Only

**Boundary**: No protected health information (PHI) or real patient data; all sources are synthetic (Synthea), fully de-identified (NHANES, VDH aggregates), or anonymized (NIH imaging).

**Justification**: Eliminates IRB requirements, enables open-source publication of methods and code, and reduces regulatory barriers. Demonstrates that the pipeline can handle realistic data structures without needing actual PHI.

**Exclusion**: Live EHR data, identifiable patient records, clinical trial datasets.

### 5. Batch Processing Focus

**Boundary**: Study evaluates batch ingestion (files dropped in S3/queue) rather than real-time streaming or transactional OLTP.

**Justification**: Rural clinics typically exchange data via batch transfers (overnight feeds, periodic reconciliations) rather than live streams. Batch design is more resilient to intermittent connectivity.

**Exclusion**: WebSocket streams, HL7 MLLP real-time feeds, CDC real-time syndromic surveillance.

---

## Summary

The four selected data sources collectively provide:

- ✅ **Volume**: 8,500–21,000 records + 1,000–5,000 images (~6–23GB)
- ✅ **Heterogeneity**: Structured, semi-structured, unstructured, and imaging data
- ✅ **Credibility**: All from authoritative organizations (MITRE, CDC, VDH, NIH)
- ✅ **Accessibility**: Publicly available, well-documented, no cost
- ✅ **HIPAA Compliance**: De-identified or synthetic
- ✅ **Durability**: High to very high long-term availability

**Limitations** (external) are acknowledged with mitigation strategies. **Delimitations** (chosen) are justified as reasonable scope boundaries for a data analytics capstone focused on operational pipeline performance in rural healthcare settings.

---

**Cross-References:**
- Variable specifications: `docs/variables_table.md`
- Submission-ready table: `docs/variables_table_summary.md`
- Proposal context: `docs/proposal_reference.md`
