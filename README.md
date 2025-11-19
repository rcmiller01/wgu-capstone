# Offline SQL Data Lake for Multi-Modal Health Data Integration

This repository implements a fully offline, standards-based data ingestion pipeline for healthcare records using FHIR, CSV, SAS, and DICOM formats. Designed for small networks and rural health providers, it offers a privacy-preserving alternative to cloud-native data lakes—delivering speed, interoperability, and analytical readiness without requiring internet access.

## Core Features

- **Multi-format ingestion**: Supports FHIR JSON, SAS XPT, CSV, and DICOM imaging metadata
- **Three-tier pipeline**: Bronze (raw ingestion), Silver (validation & cleaning), and Gold (curated integration)
- **Validation**: Configurable via Great Expectations with both strict and relaxed schema profiles
- **Privacy-preserving design**: HMAC-SHA256 pseudonymization with optional key rotation support
- **Serverless architecture**: Built entirely with Python, DuckDB, and filesystem-based workflows

## Performance Highlights

- **Median processing time**: ~16 seconds per file
- **Validation success rate**: >95% using relaxed profile
- **Latency improvement over manual workflows**: >50×
- Compatible with NHANES, Synthea, VDH, and DICOM datasets

## Architecture

### Data Pipeline (Medallion Architecture)

```
data/raw/          → Bronze (raw files, untouched)
data/interim/      → Silver (validated, cleaned)
data/processed/    → Gold (curated, analysis-ready)
```

### Key Components

- **Ingestion**: Format-specific processors for FHIR, XPT, CSV, DICOM
- **Validation**: Rule-based validation with Great Expectations
- **Pseudonymization**: HMAC-SHA256 with configurable salt
- **Analytics**: DuckDB SQL engine for local querying

## Quick Start

### Prerequisites

- Python 3.11+
- 2 GB free disk space
- No network access required (fully offline)

### Installation

```bash
# Clone repository
git clone https://github.com/rcmiller01/health-data-lake.git
cd health-data-lake

# Set up environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Set environment variable for pseudonymization
export PIPELINE_HMAC_SALT='your-secret-salt-value'  # On Windows: set or $env:

# Run full pipeline
python run_pipeline.py --source_dir data/raw --output_dir data/processed

# Or use individual processors
python -m src.pipeline.synthea_processor
python -m src.pipeline.nhanes_processor
```

### Run with Make

```bash
# Initialize environment
make init

# Run full pipeline
make all

# Run tests
make test

# Quick validation
make smoke
```

## Outputs

- **Structured data**: `.parquet` files in `data/processed/`
- **Validation logs**: `reports/validation_*.md`
- **Cohort summaries**: `reports/cohort_fact_va.csv`
- **Quality flags**: Optional flags for time/geolocation issues

## Project Structure

```
health-data-lake/
├── src/
│   ├── pipeline/          # Data ingestion processors
│   ├── analysis/          # Statistical analysis
│   └── visualization/     # Reporting utilities
├── tests/                 # Test suite
├── data/
│   ├── raw/              # Bronze layer
│   ├── interim/          # Silver layer
│   └── processed/        # Gold layer
├── reports/              # Generated outputs
│   └── figures/          # Visualizations
├── docs/                 # Documentation
│   ├── DUCKDB_IMPLEMENTATION.md
│   ├── PIPELINE_EXECUTION.md
│   └── privacy.md
├── resources/
│   └── rules/            # Validation rules
├── requirements.txt      # Python dependencies
└── Makefile             # Automation targets
```

## Documentation

- **[Pipeline Execution Guide](docs/PIPELINE_EXECUTION.md)**: Technical deep-dive
- **[DuckDB Implementation](docs/DUCKDB_IMPLEMENTATION.md)**: SQL analytics setup
- **[Privacy & Security](docs/privacy.md)**: HIPAA compliance and de-identification
- **[Data Sources](docs/data_sources.md)**: Supported formats and schemas
- **[Cleaning Plan](docs/cleaning_plan.md)**: Data transformation workflow

## Data Sources Supported

| Source | Format | Description |
|--------|--------|-------------|
| **Synthea** | FHIR JSON | Synthetic patient records (FHIR R4) |
| **NHANES** | SAS XPT | CDC National Health Survey data |
| **VDH** | CSV | Virginia Department of Health statistics |
| **DICOM** | Metadata CSV | Medical imaging metadata (NIH Chest X-ray) |

## Performance Metrics

Results from processing test datasets:

| Metric | Value |
|--------|-------|
| Median Latency (P50) | 16.12 seconds |
| P95 Latency | 42.06 seconds |
| Validation Pass Rate | 95.9% |
| Speedup vs Manual | 56-168× |

See `reports/figures/` for detailed performance charts.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_schema.py
```

## Contributing

This is a research/demonstration project. For questions or suggestions, please open an issue.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **MITRE Synthea**: Synthetic patient generator
- **CDC NHANES**: Public health survey data
- **HL7 FHIR**: Healthcare interoperability standards
- **DuckDB**: Embedded SQL analytics engine

## Citation

If you reference this work, please cite:

```bibtex
@software{health_data_lake_2025,
  title = {Offline SQL Data Lake for Multi-Modal Health Data Integration},
  author = {Miller, Robert C.},
  year = {2025},
  url = {https://github.com/rcmiller01/wgu-capstone},
  version = {1.0.0}
}
```

## Contact

For questions about this project:
- **Repository**: [github.com/rcmiller01/wgu-capstone](https://github.com/rcmiller01/wgu-capstone)
- **Issues**: Use GitHub issue tracker
- **Email**: Available in commit history