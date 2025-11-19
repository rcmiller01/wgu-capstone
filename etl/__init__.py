"""
ETL package for health data lake pipeline.

This package contains modules for building a local, SQL-centric data lake
using DuckDB and Parquet files.

Modules:
    sanitize_dicom: Remove PHI from DICOM files (Bronze layer)
    ingest_siim_metadata: Extract imaging metadata to Silver layer
    unify_patients: Consolidate patient data from multiple sources
    build_link_table: Create synthetic patient-image linkage
    build_gold_views: Execute SQL transformations via DuckDB
    validate_quality: Data quality checks on final outputs

Data Lake Layout:
    data/raw/ → Original source files (CT Sample Images, Synthea, etc.)
    data/bronze/ → De-identified, minimally processed copies
    data/silver/ → Cleaned, structured Parquet tables
    data/gold/ → Analytics-ready joined datasets

All processing is deterministic (seed=12345) and fully offline.
"""

__version__ = "1.0.0"
