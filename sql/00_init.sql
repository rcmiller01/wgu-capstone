-- ==================================================================
-- 00_init.sql: Initialize DuckDB views over Parquet datasets
-- ==================================================================
-- This script creates external views that point to Parquet files
-- in the Bronze, Silver, and Gold layers. Views are computed on-demand
-- without copying data, enabling SQL analytics over the data lake.
--
-- Usage:
--   duckdb capstone.duckdb < sql/00_init.sql
-- ==================================================================

-- Bronze layer: Imaging instance metadata (extracted from DICOM)
CREATE OR REPLACE VIEW bronze_imaging_instance AS
SELECT
    instance_uid,
    series_uid,
    study_uid,
    modality,
    body_part_examined,
    manufacturer,
    rows,
    cols,
    photometric_interp,
    burned_in_text_flag,
    transfer_syntax_uid,
    file_sha256,
    relative_path,
    study_year,
    ingestion_timestamp,
    source_layer
FROM read_parquet('data/silver/imaging_instance/*.parquet');

-- Silver layer: Patient core demographics
CREATE OR REPLACE VIEW silver_patient_core AS
SELECT
    customer_id,
    customer_id_hash,
    age,
    gender,
    height_cm,
    weight_kg,
    bmi,
    systolic_bp,
    diastolic_bp,
    state,
    source,
    created_at
FROM read_parquet('data/silver/patient_core/*.parquet');

-- Gold layer: Synthetic patient-image linkage
CREATE OR REPLACE VIEW gold_imaging_link AS
SELECT
    customer_id,
    instance_uid,
    study_uid,
    modality,
    study_year,
    link_method,
    linkage_seed,
    created_at
FROM read_parquet('data/gold/imaging_link/*.parquet');

-- Verify views created successfully
SELECT 'bronze_imaging_instance' AS view_name, COUNT(*) AS row_count
FROM bronze_imaging_instance
UNION ALL
SELECT 'silver_patient_core', COUNT(*)
FROM silver_patient_core
UNION ALL
SELECT 'gold_imaging_link', COUNT(*)
FROM gold_imaging_link;
