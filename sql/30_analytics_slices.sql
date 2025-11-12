-- ==================================================================
-- 30_analytics_slices.sql: Create analytics aggregations
-- ==================================================================
-- Generate summary tables and aggregations for validation and
-- reporting. Export to Parquet/CSV in Gold analytics directory.
--
-- Usage:
--   duckdb capstone.duckdb < sql/30_analytics_slices.sql
-- ==================================================================

-- Modality distribution
COPY (
    SELECT
        modality,
        COUNT(*) AS n_instances,
        COUNT(DISTINCT customer_id) AS n_customers,
        COUNT(DISTINCT study_uid) AS n_studies,
        ROUND(AVG(age), 1) AS avg_patient_age,
        ROUND(AVG(bmi), 1) AS avg_patient_bmi
    FROM gold_patient_imaging
    GROUP BY modality
    ORDER BY n_instances DESC
)
TO 'data/gold/analytics/modality_counts.parquet'
(FORMAT PARQUET);

-- Study year distribution
COPY (
    SELECT
        study_year,
        COUNT(*) AS n_instances,
        COUNT(DISTINCT customer_id) AS n_customers,
        COUNT(DISTINCT modality) AS n_modalities
    FROM gold_patient_imaging
    WHERE study_year IS NOT NULL
    GROUP BY study_year
    ORDER BY study_year
)
TO 'data/gold/analytics/study_year_distribution.parquet'
(FORMAT PARQUET);

-- Patient demographics summary
COPY (
    SELECT
        gender,
        COUNT(DISTINCT customer_id) AS n_customers,
        ROUND(AVG(age), 1) AS avg_age,
        ROUND(AVG(bmi), 1) AS avg_bmi,
        ROUND(AVG(systolic_bp), 1) AS avg_systolic_bp,
        ROUND(AVG(diastolic_bp), 1) AS avg_diastolic_bp
    FROM gold_patient_imaging
    GROUP BY gender
    ORDER BY n_customers DESC
)
TO 'data/gold/analytics/patient_demographics.parquet'
(FORMAT PARQUET);

-- Burned-in text flag summary
COPY (
    SELECT
        burned_in_text_flag,
        COUNT(*) AS n_instances,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
    FROM gold_patient_imaging
    GROUP BY burned_in_text_flag
    ORDER BY burned_in_text_flag
)
TO 'data/gold/analytics/burned_in_summary.parquet'
(FORMAT PARQUET);

-- Summary statistics (CSV for easy inspection)
COPY (
    SELECT
        'total_patients' AS metric,
        CAST(COUNT(DISTINCT customer_id) AS VARCHAR) AS value
    FROM gold_patient_imaging
    UNION ALL
    SELECT 'total_instances', CAST(COUNT(*) AS VARCHAR)
    FROM gold_patient_imaging
    UNION ALL
    SELECT 'total_studies', CAST(COUNT(DISTINCT study_uid) AS VARCHAR)
    FROM gold_patient_imaging
    UNION ALL
    SELECT 'avg_age', CAST(ROUND(AVG(age), 1) AS VARCHAR)
    FROM gold_patient_imaging
    UNION ALL
    SELECT 'avg_bmi', CAST(ROUND(AVG(bmi), 1) AS VARCHAR)
    FROM gold_patient_imaging
)
TO 'data/gold/analytics/summary_stats.csv'
(HEADER, DELIMITER ',');

-- Print completion message
SELECT 'Analytics slices created successfully' AS status;
