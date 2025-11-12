-- Redshift Serverless COPY commands
-- Load data from S3 parquet into Redshift for analytics

-- Prerequisites:
-- 1. Create Redshift Serverless workgroup
-- 2. Attach IAM role with S3 read permissions
-- 3. Create database: CREATE DATABASE capstone_imaging;

-- ============================================================
-- Bronze Layer: imaging_study
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze_imaging_study (
    case_id INTEGER,
    study_instance_uid VARCHAR(128),
    patient_age INTEGER,
    patient_sex VARCHAR(1),
    study_date VARCHAR(8),
    modality VARCHAR(16),
    contrast BOOLEAN,
    contrast_tag VARCHAR(128),
    file_path VARCHAR(512),
    ingestion_timestamp TIMESTAMP,
    source_dataset VARCHAR(64)
);

COPY bronze_imaging_study
FROM 's3://capstone-imaging-bucket/datalake/bronze/imaging/'
IAM_ROLE 'arn:aws:iam::ACCOUNT_ID:role/RedshiftS3ReadRole'
FORMAT AS PARQUET;

-- ============================================================
-- Silver Layer: imaging_cohort_links
-- ============================================================

CREATE TABLE IF NOT EXISTS silver_imaging_cohort_links (
    imaging_case_id INTEGER,
    patient_id VARCHAR(64),
    link_method VARCHAR(64),
    age_delta INTEGER,
    link_confidence FLOAT,
    link_created_at TIMESTAMP,
    link_version VARCHAR(16)
);

COPY silver_imaging_cohort_links
FROM 's3://capstone-imaging-bucket/datalake/silver/imaging/'
IAM_ROLE 'arn:aws:iam::ACCOUNT_ID:role/RedshiftS3ReadRole'
FORMAT AS PARQUET;

-- ============================================================
-- Analytics Views
-- ============================================================

-- View: Imaging studies with patient age groups
CREATE OR REPLACE VIEW vw_imaging_age_groups AS
SELECT
    case_id,
    patient_age,
    CASE
        WHEN patient_age < 50 THEN '< 50'
        WHEN patient_age BETWEEN 50 AND 59 THEN '50-59'
        WHEN patient_age BETWEEN 60 AND 69 THEN '60-69'
        WHEN patient_age BETWEEN 70 AND 79 THEN '70-79'
        ELSE '80+'
    END AS age_group,
    contrast,
    modality,
    source_dataset
FROM bronze_imaging_study;

-- View: Contrast utilization by age group
CREATE OR REPLACE VIEW vw_contrast_by_age AS
SELECT
    age_group,
    COUNT(*) AS total_studies,
    SUM(CASE WHEN contrast THEN 1 ELSE 0 END) AS contrast_studies,
    ROUND(100.0 * SUM(CASE WHEN contrast THEN 1 ELSE 0 END) / COUNT(*), 1) AS contrast_pct
FROM vw_imaging_age_groups
GROUP BY age_group
ORDER BY age_group;

-- View: Linked imaging-cohort records
CREATE OR REPLACE VIEW vw_imaging_patient_linkage AS
SELECT
    i.case_id,
    i.patient_age AS imaging_age,
    i.contrast,
    l.patient_id,
    l.age_delta,
    l.link_confidence,
    l.link_method
FROM bronze_imaging_study i
INNER JOIN silver_imaging_cohort_links l
    ON i.case_id = l.imaging_case_id
WHERE l.link_confidence >= 0.5;

-- ============================================================
-- Quality Checks
-- ============================================================

-- Check row counts
SELECT 'bronze_imaging_study' AS table_name, COUNT(*) AS row_count
FROM bronze_imaging_study
UNION ALL
SELECT 'silver_imaging_cohort_links', COUNT(*)
FROM silver_imaging_cohort_links;

-- Check for duplicates
SELECT case_id, COUNT(*) AS dup_count
FROM bronze_imaging_study
GROUP BY case_id
HAVING COUNT(*) > 1;

-- Check age distribution
SELECT
    age_group,
    COUNT(*) AS studies
FROM vw_imaging_age_groups
GROUP BY age_group
ORDER BY age_group;

-- Check contrast distribution
SELECT
    contrast,
    COUNT(*) AS studies,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM bronze_imaging_study
GROUP BY contrast;

-- ============================================================
-- Cleanup (if needed)
-- ============================================================

-- DROP TABLE bronze_imaging_study;
-- DROP TABLE silver_imaging_cohort_links;
-- DROP VIEW vw_imaging_age_groups;
-- DROP VIEW vw_contrast_by_age;
-- DROP VIEW vw_imaging_patient_linkage;
