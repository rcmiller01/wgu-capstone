-- ==================================================================
-- 20_gold_joins.sql: Create Gold analytics tables via SQL joins
-- ==================================================================
-- Join patient core, imaging instance, and linkage tables to create
-- analytics-ready datasets. Export to Parquet in Gold layer.
--
-- Usage:
--   duckdb capstone.duckdb < sql/20_gold_joins.sql
-- ==================================================================

-- Create joined patient-imaging table
CREATE OR REPLACE TABLE gold_patient_imaging AS
SELECT
    p.customer_id,
    p.customer_id_hash,
    p.age,
    p.gender,
    p.bmi,
    p.systolic_bp,
    p.diastolic_bp,
    p.state,
    l.instance_uid,
    l.study_uid,
    i.series_uid,
    i.modality,
    i.body_part_examined,
    i.manufacturer,
    i.rows,
    i.cols,
    i.photometric_interp,
    i.burned_in_text_flag,
    i.study_year,
    i.file_sha256,
    i.relative_path
FROM silver_patient_curated p
INNER JOIN gold_imaging_link l
    ON p.customer_id = l.customer_id
INNER JOIN bronze_imaging_curated i
    ON l.instance_uid = i.instance_uid;

-- Export to Parquet
COPY gold_patient_imaging
TO 'data/gold/analytics/patient_imaging.parquet'
(FORMAT PARQUET, COMPRESSION SNAPPY);

-- Verify export
SELECT
    'gold_patient_imaging' AS table_name,
    COUNT(*) AS row_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT instance_uid) AS unique_instances,
    COUNT(DISTINCT modality) AS unique_modalities
FROM gold_patient_imaging;
