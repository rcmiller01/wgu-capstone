# Phase 0: Final Proposal Polish - Instructions

**Issue**: #1 - Phase 0: Final proposal polish  
**Priority**: P0 (Critical)  
**Labels**: phase:0-proposal, type:docs

---

## Objective

Polish the capstone proposal to meet WGU rubric requirements by ensuring:
1. Statistical terminology is consistent across name/topic/question/hypotheses
2. Voice is depersonalized (no "I/we/my" language)
3. Context clearly states the contribution to the field
4. All sections have proper in-text citations per APA guidelines

---

## Reference Documents

**Primary References:**
- `docs/proposal_reference.md` - Complete proposal content from submission template
- `docs/variables_table.md` - Comprehensive variable definitions with IV/DV roles
- `references/apa.bib` - Bibliography for citation management
- Original HTML template: `Capstone Proposal Model Template 2.htm`

---

## Tasks Checklist

### 1. Statistical Terminology Consistency ✓ (Mostly Complete)

**Current Status**: Strong foundation in place

**Verify:**
- [x] Research question mentions "streamline," "reduce friction," "raise consistency"
- [x] Hypotheses use proper notation (H₀, H₁)
- [x] Statistical test clearly identified (paired t-test, p < .05)
- [x] Variables table defines IV/DV roles (see `docs/variables_table.md`)
- [ ] **TODO**: Add explicit mention of primary DV (`latency_sec`) and secondary DV (`validation_pass_bool`) in hypothesis section

**Action Items:**
- Review hypothesis section to ensure DVs are explicitly named
- Confirm all statistical terms align with `docs/variables_table.md`

---

### 2. Depersonalize Voice ✅ (COMPLETE)

**Status**: Verified - No first-person pronouns found in proposal text

**Verification Complete**:
- Scanned entire proposal for "I", "we", "my", "our", "us"
- All instances found were HTML tags (`<i>` for italics) or language codes (`lang=EN-US`)
- Proposal already uses objective, academic voice throughout

**No action required** - Voice is already depersonalized per rubric requirements.

---

### 3. Context and Contribution Clarity

**Current Context Section**: Explains the problem well

**✅ COMPLETED**: Explicit statement of **contribution to the field** added

**Added to Context section:**
1. **Contextual Novelty**: Targets low-bandwidth, low-ops environments (vs. enterprise assumptions)
2. **Method Novelty**: Portable validation framework producing comparable metrics across vendors
3. **Practical Artifacts**: IaC + rule sets + runbooks for immediate reuse

**Success Criteria Defined:**
- Latency: P50 ≤ 30s, P95 ≤ 120s per file (100-10k rows)
- Reliability: ≥ 99% successful validations, ≥ 95% reproducible IaC runs
- Cost: ≤ $X per 1k records, 30-60% savings vs managed ETL
- Resilience: Offline-tolerant with at-least-once semantics

**Risks/Limits Acknowledged:**
- Cold-start variance and OCR latency (mitigated with warmers/batching)
- PHI handling out of scope (synthetic data with extension documentation)

**See**: `docs/proposal_reference.md` for complete enhanced context section

---

### 4. In-Text Citations Review

**Sections needing citation audit:**

#### ✓ Well-Cited Sections:
- Data section: (Evans, 2020; Santos & Costa, 2020)
- Data Gathering: (Swalin, 2018; Mehmood et al., 2013; Overhage et al., 2020; Jabour et al., 2018)
- Tools: (Evans, 2020; WGU, 2023)

#### ⚠️ Needs Citations:
- **Context section**: Claims about "fragmented systems" and "delayed data flow" need supporting evidence
- **Research Question**: Consider citing FHIR interoperability standards or rural health challenges
- **Project Outcomes**: "trust levels for health system decision makers" has citation but consider adding more
- **Data Analytics Tools**: Power BI claim needs citation

**Potential Missing Citations:**
- FHIR specification/standards (HL7.org)
- Rural healthcare challenges (HRSA, AHA reports)
- Serverless computing benefits in healthcare (AWS, Azure whitepapers)
- Data quality improvement frameworks

**Action Items:**
- Add 3-5 new citations to strengthen unsupported claims
- Ensure every factual claim has a citation
- Verify all in-text citations appear in References section

---

### 5. Variable Table Enhancement

**Current**: Basic Field/Type table in HTML template

**Required per Issue #1**: Add IV/DV role column

**Solution**: Reference comprehensive table in `docs/variables_table.md`

**Action Items:**
- Consider creating a simplified summary table for proposal submission showing:
  - Variable Name
  - Role (Primary DV, Secondary DV, IV, Control, Stratifier)
  - Type (categorical/numeric)
  - Scale (nominal/ordinal/continuous/count)

---

## Rubric Alignment

### A1: Research Question
- [x] Clearly stated
- [ ] **Enhance**: Cite FHIR/interoperability standards

### A2: Hypothesis
- [x] H₀ and H₁ properly stated
- [x] Statistical test identified (paired t-test)
- [ ] **Enhance**: Explicitly name DVs in hypothesis text

### A3: Context
- [x] Problem explained
- [ ] **Add**: Explicit contribution statement
- [ ] **Add**: Gap in literature citations

### B1: Data Sources
- [x] Four sources listed with URLs
- [x] De-identified and HIPAA compliant noted
- [ ] **Enhance**: Add citation for each source's credibility

### B2: Variable Table
- [x] Variables listed
- [ ] **Add**: IV/DV role column (reference variables_table.md)

### C1: Data Gathering
- [x] Treatment described
- [x] Missing data handling cited
- [ ] **Verify**: All technical claims have citations

### C2: Statistical Methods
- [x] Paired t-test identified
- [x] Alternative method (Wilcoxon) noted
- [x] Normality checks described
- [ ] **Verify**: All methods have textbook/source citations

### D1: Tools Justification
- [x] Python justified
- [ ] **Add**: Power BI citation
- [ ] **Consider**: Great Expectations citation

---

## Next Steps

1. **Review and annotate** the original HTML template with needed changes
2. **Create reference list** of additional citations needed
3. **Draft revised sections** addressing all TODO items above
4. **Cross-reference** with `docs/variables_table.md` for accuracy
5. **Final pass** for voice, terminology, and citation consistency

---

## Completion Criteria

- [ ] All first-person pronouns removed
- [ ] DVs explicitly named in hypothesis section
- [ ] Contribution to field stated in Context
- [ ] All factual claims have in-text citations
- [ ] Variable table includes IV/DV roles
- [ ] Statistical terminology consistent throughout
- [ ] Cross-referenced with variables_table.md
- [ ] Ready for mentor review

---

**Status**: Ready to begin Phase 0 polish  
**Est. Completion**: Align with project timeline (4/24/2025 final deadline)
