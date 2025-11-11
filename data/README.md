# Data Directory

**Purpose**: Storage for all project data across acquisition, cleaning, and processing stages

---

## Directory Structure

```
data/
├── raw/                          # Original downloaded/generated data (READ-ONLY)
│   ├── synthea/                 # Synthetic patient records
│   │   ├── fhir/               # FHIR JSON files (1 per patient)
│   │   └── metadata.json       # Generation parameters
│   ├── nhanes/                  # CDC NHANES survey data
│   │   ├── 2017-2018/          # XPT files by cycle
│   │   ├── 2019-2020/
│   │   └── README.md
│   ├── vdh/                     # Virginia DoH state health data
│   │   └── *.csv               # County/district aggregates
│   └── nih_xray/                # NIH Chest X-Ray images
│       ├── images/             # PNG files
│       ├── sample/             # Stratified sample subset
│       └── Data_Entry_2017.csv # Metadata
│
├── interim/                      # Intermediate cleaning stages
│   ├── [source]_schema_validated/
│   ├── [source]_missing_handled/
│   ├── [source]_outliers_flagged/
│   └── [...]
│
├── processed/                    # Final analysis-ready datasets
│   ├── combined_data.parquet    # All sources merged
│   └── stratified_samples.parquet
│
├── acquisition_log.txt           # Download/generation audit trail
├── quality_report.md             # Data quality metrics
├── lineage_log.jsonl             # Transformation tracking
└── README.md                     # This file
```

---

## Data Sources

### 1. Synthea - Synthetic Health Records

- **Format**: FHIR JSON
- **Volume**: 5,000 patients (configurable)
- **Size**: ~500 MB - 2 GB
- **Acquisition**: Generated locally using Synthea CLI
- **Seed**: 12345 (reproducible)
- **State**: Virginia demographics

**Generate**:
```bash
python -m src.pipeline.data_acquisition --synthea --n-patients 5000
```

### 2. NHANES - National Health and Nutrition Examination Survey

- **Format**: SAS XPT → CSV
- **Volume**: ~2,000-5,000 participants per cycle
- **Size**: ~100-500 MB
- **Acquisition**: Downloaded from CDC FTP
- **Cycles**: 2017-2018, 2019-2020
- **Components**: Demographics, Body Measures, Cholesterol, Blood Pressure

**Download**:
```bash
python -m src.pipeline.data_acquisition --nhanes
```

### 3. Virginia Department of Health

- **Format**: CSV
- **Volume**: ~500-1,000 aggregated records
- **Size**: ~10-50 MB
- **Acquisition**: Manual download from data.virginia.gov
- **Datasets**: COVID cases, chronic disease indicators, HPSA data

**Setup**:
```bash
python -m src.pipeline.data_acquisition --vdh
# Then manually download files to data/raw/vdh/ (see README instructions)
```

### 4. NIH Chest X-Ray Dataset

- **Format**: PNG images + CSV metadata
- **Volume**: 1,000-5,000 images (sample from 112,120 total)
- **Size**: ~5-20 GB (full: 42 GB)
- **Acquisition**: Manual download from Kaggle or NIH Box
- **Sampling**: Stratified by pathology label for class balance

**Setup**:
```bash
python -m src.pipeline.data_acquisition --nih --n-images 2000
# Then download via Kaggle CLI or NIH Box (see README instructions)
```

---

## Data Acquisition

### All Sources

```bash
python -m src.pipeline.data_acquisition --all
```

This will:
1. Generate Synthea data (5,000 patients)
2. Download NHANES data (2017-2020 cycles)
3. Create VDH download instructions
4. Create NIH X-Ray download instructions

### Individual Sources

```bash
# Synthea only
python -m src.pipeline.data_acquisition --synthea --n-patients 5000 --seed 12345

# NHANES only
python -m src.pipeline.data_acquisition --nhanes --cycles 2017-2018,2019-2020

# VDH setup
python -m src.pipeline.data_acquisition --vdh

# NIH setup
python -m src.pipeline.data_acquisition --nih --n-images 2000
```

---

## Data Cleaning

### Pipeline Stages

1. **Schema Validation**: Verify structure, data types, required fields
2. **Missingness Handling**: Drop/impute based on variable role
3. **Outlier Detection**: Flag/treat extreme values (IQR, Z-score, domain rules)
4. **Format Standardization**: Dates (ISO 8601), strings (lowercase), booleans
5. **FHIR Validation**: Synthea-specific resource conformance checks

### Run Cleaning

```bash
# Clean all sources
python -m src.pipeline.data_cleaning --all

# Clean specific source
python -m src.pipeline.data_cleaning --source synthea
```

### Quality Metrics

After cleaning, review:
- `data/quality_report.md`: Completeness, validity, consistency metrics
- `data/lineage_log.jsonl`: Transformation audit trail
- `data/acquisition_log.txt`: Download/generation status

---

## Data Dictionary

See `docs/variables_table.md` for complete variable specifications:

**Primary Variables:**
- `latency_sec`: Processing time (DV, continuous)
- `validation_pass_bool`: Data quality validation (DV, binary)
- `data_source`: Source system (IV, categorical: synthea, nhanes, vdh, nih_xray)
- `record_complexity`: Complexity level (IV, ordinal: simple, moderate, complex)
- `file_size_kb`: File size in KB (control, continuous)

**Stratification:**
- `health_district`: Virginia health district (stratifier, categorical)
- `rural_urban`: Rural vs. urban classification (stratifier, binary)
- `data_type`: Structured, semi-structured, unstructured, imaging (stratifier, categorical)

---

## Reproducibility

### Seeds and Versions

- **Synthea Seed**: 12345 (fixed for reproducibility)
- **Python**: 3.11+
- **Synthea Version**: Latest release (see `data/raw/synthea/metadata.json`)
- **NHANES Cycles**: 2017-2018, 2019-2020 (no versioning, static datasets)

### Checksums

After acquisition, verify file integrity:

```bash
# Generate checksums
cd data/raw
find . -type f -exec sha256sum {} \; > checksums.txt

# Verify later
sha256sum -c checksums.txt
```

### Re-running Pipeline

Data acquisition is **idempotent**:
- Existing files are skipped (not re-downloaded)
- Synthea generation creates new output (use same seed for identical data)

To force re-download:
```bash
rm -rf data/raw/[source]
python -m src.pipeline.data_acquisition --[source]
```

---

## Storage Requirements

| Source | Raw Size | Interim Size | Processed Size | Total |
|--------|----------|--------------|----------------|-------|
| Synthea | 500 MB - 2 GB | +20% | +10% | ~2.5 GB |
| NHANES | 100-500 MB | +10% | +5% | ~600 MB |
| VDH | 10-50 MB | +5% | +5% | ~60 MB |
| NIH X-Ray | 5-20 GB | +2% | +1% | ~20 GB |
| **TOTAL** | **~6-23 GB** | **+15%** | **+8%** | **~23-28 GB** |

**Recommendations:**
- Minimum 30 GB free disk space
- SSD preferred for faster I/O during cleaning pipeline
- Use `.gitignore` to exclude `data/raw/` and `data/interim/` from version control

---

## Data Limitations

See `docs/baseline_sources.md` for detailed discussion of:

**Limitations** (external constraints):
1. Synthetic data realism (Synthea models may not capture all rural health patterns)
2. Inferred baseline (no live manual process to measure)
3. Geographic bias (Virginia-specific, may not generalize to other rural contexts)
4. Temporal gaps (NHANES 2019-2020 incomplete, NIH images stop at 2015)
5. NLP-derived labels (NIH X-Ray labels have ~10-15% error rate)

**Delimitations** (chosen scope):
1. Engineering focus (not clinical outcomes)
2. Four data types only (excludes claims, genomics, wearables)
3. Virginia context (not multi-state)
4. Synthetic/de-identified only (no real PHI)
5. Batch processing (not real-time streaming)

---

## Support

**Issues**: File issues at https://github.com/rcmiller01/wgu-capstone/issues

**Questions**:
- Data acquisition: See `data/raw/[source]/README.md`
- Data cleaning: See `docs/phase3_instructions.md`
- Variables: See `docs/variables_table.md`

---

**Last Updated**: 2025-11-10  
**Pipeline Version**: 1.0.0
