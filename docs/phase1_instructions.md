# Phase 1: Data Source & Variables Table - Instructions

**Issue**: #2 - Phase 1: Data source and variables table  
**Priority**: P0 (Critical)  
**Labels**: phase:1-data, type:research, type:docs

---

## Objective

Document and validate all data sources with comprehensive metadata including:
1. Primary dataset links and access information
2. Variables table with IV/DV roles (✅ Already complete - see Phase 0)
3. Volume and sparsity characteristics
4. Reliability and credibility assessment
5. Usability and durability evaluation
6. Limitations vs. Delimitations (clearly distinguished)

---

## Reference Documents

**Completed in Phase 0:**
- `docs/variables_table.md` - Complete variable specifications with IV/DV roles ✅
- `docs/variables_table_summary.md` - Submission-ready table ✅
- `docs/proposal_reference.md` - Data sources section (needs expansion)

**To Create:**
- `docs/data_sources.md` - Comprehensive data source documentation

---

## Tasks Checklist

### 1. Primary Dataset Links ✅ (Already in proposal_reference.md)

**Current Status**: Four sources documented with URLs

**Sources:**
1. ✅ Synthea Synthetic Health Records - https://synthea.mitre.org/downloads
2. ✅ NHANES Public Health Data (CDC) - https://www.cdc.gov/nchs/nhanes
3. ✅ Virginia Department of Health Data Portal - https://data.virginia.gov/browse?tags=health
4. ✅ Radiology Imaging Dataset (RSNA/NIH Chest X-Ray) - https://www.kaggle.com/datasets/nih-chest-xrays/data

---

### 2. Variables Table (Name, Role IV/DV, Type) ✅ COMPLETE

**Status**: Completed in Phase 0

**Deliverables:**
- `docs/variables_table.md` - Full technical specification
- `docs/variables_table_summary.md` - Submission-ready format

**No additional work required** - reference existing tables

---

### 3. Volume & Sparsity Documentation

**Requirements:**
- Total record counts per source
- Missing data patterns and percentages
- Field-level completeness metrics
- Distribution characteristics (skewness, outliers)

**Action Items:**
- [ ] Document expected volume from each source
- [ ] Identify fields with known sparsity issues
- [ ] Quantify missingness percentages (if known from documentation)
- [ ] Note any temporal or geographic sparsity patterns

---

### 4. Reliability Assessment

**Requirements:**
- Data source credibility (organizational backing)
- Update frequency and maintenance status
- Known quality issues or caveats
- Validation methods used by source providers

**Action Items:**
- [ ] Document organizational provenance (CDC, MITRE, VDH, NIH)
- [ ] Verify active maintenance status
- [ ] Note any known quality limitations from source documentation
- [ ] Include de-identification/HIPAA compliance status

---

### 5. Usability Evaluation

**Requirements:**
- Format accessibility (CSV, JSON, DICOM, etc.)
- Documentation quality
- Licensing and terms of use
- Technical barriers to acquisition

**Action Items:**
- [ ] Document file formats available
- [ ] Assess documentation completeness
- [ ] Verify open access or licensing requirements
- [ ] Note any technical prerequisites (APIs, credentials, etc.)

---

### 6. Durability Assessment

**Requirements:**
- Long-term availability expectations
- Archival status and permanence
- Versioning and change tracking
- Backup/mirror availability

**Action Items:**
- [ ] Assess institutional commitment to long-term hosting
- [ ] Check for DOI or permanent identifiers
- [ ] Note version control mechanisms
- [ ] Identify mirror sites or backup sources

---

### 7. Limitations vs. Delimitations (Critical Distinction)

**Limitations** = Constraints BEYOND your control
- Synthetic data may not capture all real-world edge cases
- Baseline performance must be inferred (no live manual process to measure)
- Public datasets may have geographic or demographic biases
- Temporal coverage may be incomplete

**Delimitations** = Boundaries YOU chose
- Focus on data engineering performance, not clinical outcomes
- Scope limited to four specific data types (structured, semi-structured, unstructured, images)
- Virginia-focused for geographic context
- Synthetic/de-identified data only (no real PHI)

**Action Items:**
- [ ] Clearly separate limitations (external constraints) from delimitations (study scope choices)
- [ ] Justify each delimitation as a reasonable boundary
- [ ] Acknowledge how limitations affect interpretation
- [ ] Document mitigation strategies for key limitations

---

## Deliverable Structure

### Comprehensive Data Source Document

Create `docs/data_sources.md` with sections:

1. **Overview**
   - Summary of four data sources
   - Rationale for selection

2. **Source 1: Synthea Synthetic Health Records**
   - Description
   - Volume & sparsity
   - Reliability
   - Usability
   - Durability
   - Access information

3. **Source 2: NHANES (CDC)**
   - [Same structure]

4. **Source 3: Virginia Dept of Health**
   - [Same structure]

5. **Source 4: NIH Chest X-Ray Dataset**
   - [Same structure]

6. **Aggregate Characteristics**
   - Combined volume
   - Overall sparsity patterns
   - Quality summary

7. **Limitations**
   - External constraints beyond researcher control
   - Impact on study validity
   - Mitigation strategies

8. **Delimitations**
   - Researcher-chosen scope boundaries
   - Justification for each boundary
   - What's explicitly excluded and why

---

## Rubric Alignment

### B1: Data Sources
- [x] Four sources listed with URLs
- [x] De-identified and HIPAA compliant noted
- [ ] **Expand**: Volume, reliability, usability, durability details
- [ ] **Add**: Sparsity patterns and quality assessment

### B2: Variables Table
- [x] Variables listed (Phase 0)
- [x] IV/DV roles defined (Phase 0)
- [x] Types and scales specified (Phase 0)

### B3: Limitations & Delimitations
- [x] Basic limitations noted (baseline inference)
- [x] Basic delimitations noted (engineering vs clinical focus)
- [ ] **Expand**: Comprehensive coverage of both with clear distinction

---

## Completion Criteria

- [ ] All four data sources fully documented
- [ ] Volume and sparsity quantified for each source
- [ ] Reliability assessed with organizational backing
- [ ] Usability evaluated (format, docs, licensing)
- [ ] Durability assessed (long-term availability)
- [ ] Limitations clearly distinguished from delimitations
- [ ] Variables table cross-referenced (already complete)
- [ ] All sources have permanent links
- [ ] Quality issues acknowledged with mitigation plans

---

**Status**: Ready to begin Phase 1 data source documentation  
**Next**: Create comprehensive `docs/data_sources.md`
