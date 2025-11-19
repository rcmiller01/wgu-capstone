# SQL Equivalents: Cloud Data Warehouse Portability

## Overview

This document demonstrates how SQL queries written for DuckDB translate to cloud data warehouses (AWS Athena, Google BigQuery, Azure Synapse, Snowflake). The core logic remains the same—only minor syntax adjustments are needed.

## Patient-Imaging Join (Gold Layer)

### DuckDB (Local)

```sql
-- File: sql/20_gold_joins.sql
CREATE OR REPLACE TABLE gold_patient_imaging AS
SELECT
    p.customer_id,
    p.age,
    p.gender,
    p.bmi,
    l.instance_uid,
    i.modality,
    i.body_part_examined,
    i.study_year
FROM silver_patient_curated p
INNER JOIN gold_imaging_link l
    ON p.customer_id = l.customer_id
INNER JOIN bronze_imaging_curated i
    ON l.instance_uid = i.instance_uid;
```

### AWS Athena (Presto SQL)

```sql
-- Create external table from S3 Parquet
CREATE EXTERNAL TABLE IF NOT EXISTS silver_patient_core (
    customer_id INT,
    age INT,
    gender STRING,
    bmi DOUBLE
    -- ... other columns
)
STORED AS PARQUET
LOCATION 's3://my-bucket/healthdata/silver/patient_core/';

-- Same join logic works
CREATE TABLE gold_patient_imaging 
WITH (
    format='PARQUET',
    external_location='s3://my-bucket/healthdata/gold/analytics/'
) AS
SELECT
    p.customer_id,
    p.age,
    p.gender,
    p.bmi,
    l.instance_uid,
    i.modality,
    i.body_part_examined,
    i.study_year
FROM silver_patient_core p
INNER JOIN gold_imaging_link l
    ON p.customer_id = l.customer_id
INNER JOIN bronze_imaging_instance i
    ON l.instance_uid = i.instance_uid;
```

### Google BigQuery (Standard SQL)

```sql
-- Load Parquet from GCS (via bq load command or console)
-- Then query directly:

CREATE OR REPLACE TABLE `project.dataset.gold_patient_imaging` AS
SELECT
    p.customer_id,
    p.age,
    p.gender,
    p.bmi,
    l.instance_uid,
    i.modality,
    i.body_part_examined,
    i.study_year
FROM `project.dataset.silver_patient_core` p
INNER JOIN `project.dataset.gold_imaging_link` l
    ON p.customer_id = l.customer_id
INNER JOIN `project.dataset.bronze_imaging_instance` i
    ON l.instance_uid = i.instance_uid;
```

### Snowflake

```sql
-- Load Parquet from S3 stage
CREATE OR REPLACE TABLE gold_patient_imaging AS
SELECT
    p.customer_id,
    p.age,
    p.gender,
    p.bmi,
    l.instance_uid,
    i.modality,
    i.body_part_examined,
    i.study_year
FROM silver_patient_core p
INNER JOIN gold_imaging_link l
    ON p.customer_id = l.customer_id
INNER JOIN bronze_imaging_instance i
    ON l.instance_uid = i.instance_uid;
```

## Modality Aggregation (Analytics Slice)

### DuckDB

```sql
-- File: sql/30_analytics_slices.sql
COPY (
    SELECT
        modality,
        COUNT(*) AS n_instances,
        COUNT(DISTINCT customer_id) AS n_customers,
        ROUND(AVG(age), 1) AS avg_patient_age
    FROM gold_patient_imaging
    GROUP BY modality
    ORDER BY n_instances DESC
)
TO 'data/gold/analytics/modality_counts.parquet'
(FORMAT PARQUET);
```

### AWS Athena

```sql
-- Write results to S3
CREATE TABLE modality_counts
WITH (
    format='PARQUET',
    external_location='s3://my-bucket/healthdata/gold/analytics/'
) AS
SELECT
    modality,
    COUNT(*) AS n_instances,
    COUNT(DISTINCT customer_id) AS n_customers,
    ROUND(AVG(age), 1) AS avg_patient_age
FROM gold_patient_imaging
GROUP BY modality
ORDER BY n_instances DESC;
```

### BigQuery

```sql
-- Results stored in BigQuery table
CREATE OR REPLACE TABLE `project.dataset.modality_counts` AS
SELECT
    modality,
    COUNT(*) AS n_instances,
    COUNT(DISTINCT customer_id) AS n_customers,
    ROUND(AVG(age), 1) AS avg_patient_age
FROM `project.dataset.gold_patient_imaging`
GROUP BY modality
ORDER BY n_instances DESC;

-- Export to GCS if needed
EXPORT DATA OPTIONS(
    uri='gs://my-bucket/healthdata/gold/analytics/modality_counts-*.parquet',
    format='PARQUET'
) AS
SELECT * FROM `project.dataset.modality_counts`;
```

### Snowflake

```sql
-- Same syntax as DuckDB
CREATE OR REPLACE TABLE modality_counts AS
SELECT
    modality,
    COUNT(*) AS n_instances,
    COUNT(DISTINCT customer_id) AS n_customers,
    ROUND(AVG(age), 1) AS avg_patient_age
FROM gold_patient_imaging
GROUP BY modality
ORDER BY n_instances DESC;

-- Unload to S3
COPY INTO @my_stage/modality_counts.parquet
FROM modality_counts
FILE_FORMAT = (TYPE = PARQUET);
```

## Read Parquet Files Pattern

### DuckDB

```sql
-- Direct query on Parquet files (no external table needed)
SELECT * FROM read_parquet('data/silver/patient_core/*.parquet');
```

### AWS Athena

```sql
-- Create external table pointing to S3
CREATE EXTERNAL TABLE silver_patient_core (
    customer_id INT,
    age INT
    -- ... columns
)
STORED AS PARQUET
LOCATION 's3://my-bucket/healthdata/silver/patient_core/';

-- Then query
SELECT * FROM silver_patient_core;
```

### BigQuery

```sql
-- Load Parquet via bq command:
-- bq load --source_format=PARQUET \
--   dataset.silver_patient_core \
--   gs://my-bucket/healthdata/silver/patient_core/*.parquet

-- Query after load
SELECT * FROM `project.dataset.silver_patient_core`;
```

### Snowflake

```sql
-- Create external stage
CREATE STAGE my_stage
URL='s3://my-bucket/healthdata/'
CREDENTIALS=(AWS_KEY_ID='...' AWS_SECRET_KEY='...');

-- Query directly from stage
SELECT * FROM @my_stage/silver/patient_core/;

-- Or load into table
COPY INTO silver_patient_core
FROM @my_stage/silver/patient_core/
FILE_FORMAT = (TYPE = PARQUET);
```

## Syntax Differences Summary

| Feature | DuckDB | Athena | BigQuery | Snowflake |
|---------|--------|--------|----------|-----------|
| **Read Parquet** | `read_parquet('path/*.parquet')` | External table + S3 location | Load via `bq load` | External stage |
| **Table Names** | Unquoted | Unquoted | \`project.dataset.table\` | Unquoted |
| **Export** | `COPY ... TO 'file'` | `CREATE TABLE ... WITH location=` | `EXPORT DATA` | `COPY INTO @stage` |
| **String Type** | `VARCHAR` | `STRING` | `STRING` | `VARCHAR` |
| **Double Type** | `DOUBLE` | `DOUBLE` | `FLOAT64` | `DOUBLE` |
| **Array Type** | `ARRAY<T>` | `ARRAY<T>` | `ARRAY<T>` | `ARRAY` |

## Key Takeaways

1. **Core SQL is portable**: `SELECT`, `JOIN`, `GROUP BY`, `WINDOW` functions work across all platforms

2. **External data access differs**: Each platform has its own mechanism for reading Parquet from object storage

3. **Export syntax varies**: DuckDB uses `COPY`, Athena uses `CREATE TABLE`, BigQuery uses `EXPORT DATA`

4. **Type names mostly compatible**: Minor differences (e.g., `STRING` vs `VARCHAR`, `FLOAT64` vs `DOUBLE`)

5. **Cost implications**:
   - **DuckDB**: Free (local computation)
   - **Athena**: $5/TB scanned
   - **BigQuery**: $5/TB scanned or $0.04/slot-hour
   - **Snowflake**: Credit-based (varies by warehouse size)

## Migration Path

To migrate from local DuckDB to cloud:

1. **Upload Parquet files** to S3/GCS/Azure Blob
2. **Create external tables** (Athena) or load data (BigQuery/Snowflake)
3. **Run SQL scripts** from `sql/` directory with minimal syntax changes
4. **Verify results** match local DuckDB outputs

The deterministic seed (12345) ensures reproducible results across platforms.

---

**Last Updated**: 2025-11-12  
**Version**: 1.0.0
