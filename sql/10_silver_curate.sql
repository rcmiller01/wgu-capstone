-- ==================================================================
-- 10_silver_curate.sql: Curate and normalize Silver layer
-- ==================================================================
-- Apply type casting, data validation, and normalization to Silver
-- layer views. Ensures consistent types and handles edge cases.
--
-- Usage:
--   duckdb capstone.duckdb < sql/10_silver_curate.sql
-- ==================================================================

-- Curated imaging metadata with type safety
CREATE OR REPLACE VIEW bronze_imaging_curated AS
SELECT
    CAST(instance_uid AS VARCHAR) AS instance_uid,
    CAST(series_uid AS VARCHAR) AS series_uid,
    CAST(study_uid AS VARCHAR) AS study_uid,
    UPPER(CAST(modality AS VARCHAR)) AS modality,
    CAST(body_part_examined AS VARCHAR) AS body_part_examined,
    CAST(manufacturer AS VARCHAR) AS manufacturer,
    CAST(rows AS INTEGER) AS rows,
    CAST(cols AS INTEGER) AS cols,
    CAST(photometric_interp AS VARCHAR) AS photometric_interp,
    CAST(burned_in_text_flag AS BOOLEAN) AS burned_in_text_flag,
    CAST(transfer_syntax_uid AS VARCHAR) AS transfer_syntax_uid,
    CAST(file_sha256 AS VARCHAR) AS file_sha256,
    CAST(relative_path AS VARCHAR) AS relative_path,
    CAST(study_year AS INTEGER) AS study_year,
    CAST(ingestion_timestamp AS TIMESTAMP) AS ingestion_timestamp
FROM bronze_imaging_instance
WHERE instance_uid IS NOT NULL
  AND study_uid IS NOT NULL;

-- Curated patient core with validated ranges
CREATE OR REPLACE VIEW silver_patient_curated AS
SELECT
    CAST(customer_id AS INTEGER) AS customer_id,
    CAST(customer_id_hash AS VARCHAR) AS customer_id_hash,
    CAST(age AS INTEGER) AS age,
    UPPER(CAST(gender AS VARCHAR)) AS gender,
    CAST(height_cm AS DOUBLE) AS height_cm,
    CAST(weight_kg AS DOUBLE) AS weight_kg,
    CAST(bmi AS DOUBLE) AS bmi,
    CAST(systolic_bp AS INTEGER) AS systolic_bp,
    CAST(diastolic_bp AS INTEGER) AS diastolic_bp,
    UPPER(CAST(state AS VARCHAR)) AS state,
    CAST(source AS VARCHAR) AS source,
    CAST(created_at AS TIMESTAMP) AS created_at
FROM silver_patient_core
WHERE customer_id IS NOT NULL
  AND age BETWEEN 0 AND 120
  AND gender IN ('M', 'F', 'O');

-- Verify curated views
SELECT 'bronze_imaging_curated' AS view_name, COUNT(*) AS row_count
FROM bronze_imaging_curated
UNION ALL
SELECT 'silver_patient_curated', COUNT(*)
FROM silver_patient_curated;
