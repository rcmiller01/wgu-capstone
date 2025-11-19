# DuckDB Data Lake Overview

## Introduction

This project uses **DuckDB** as an embedded SQL engine to power a local, file-based data lake. DuckDB enables SQL analytics directly on Parquet files without requiring external database servers or cloud infrastructure.

## Why DuckDB?

### Key Advantages

1. **Embedded & Serverless**
   - No separate database process to manage
   - Single `.duckdb` file contains all metadata
   - Zero configuration for evaluators

2. **Native Parquet Support**
   - Direct queries on Parquet files via `read_parquet()`
   - No data import/export overhead
   - Preserves columnar storage benefits

3. **SQL Standard Compliance**
   - Full ANSI SQL support (joins, CTEs, window functions)
   - SQL is portable to Athena, BigQuery, Redshift, Snowflake
   - Familiar query patterns for data engineers

4. **Performance**
   - Vectorized execution engine
   - Efficient for analytical workloads (aggregations, joins)
   - Handles GB-scale data on laptop hardware

5. **Reproducibility**
   - All processing is deterministic (seed=12345)
   - No network dependencies
   - Git-friendly (database file excluded from version control)

## Architecture

### Data Lake Layout

```
data/
├── raw/                      # Original source files
│   ├── CT_Sample_Images/     # SIIM imaging dataset
│   ├── synthea/              # Synthetic EHR data
│   ├── nhanes/               # Public health surveys
│   └── vdh/                  # State health statistics
│
├── bronze/                   # De-identified, minimally processed
│   └── images/               # Sanitized DICOM files
│
├── silver/                   # Cleaned, structured Parquet
│   ├── imaging_instance/     # Instance-level imaging metadata
│   └── patient_core/         # Unified patient demographics
│
└── gold/                     # Analytics-ready joins
    ├── imaging_link/         # Synthetic patient-image linkage
    └── analytics/            # Final tables (patient_imaging, aggregates)
```

### SQL Pipeline

1. **00_init.sql**: Create views over Parquet files
   - `bronze_imaging_instance` → `data/silver/imaging_instance/*.parquet`
   - `silver_patient_core` → `data/silver/patient_core/*.parquet`
   - `gold_imaging_link` → `data/gold/imaging_link/*.parquet`

2. **10_silver_curate.sql**: Type casting and validation
   - Ensure consistent data types (VARCHAR, INTEGER, BOOLEAN)
   - Filter invalid records (e.g., age > 120, nulls in key columns)

3. **20_gold_joins.sql**: Create analytics tables
   - Join patients, imaging, and linkage via SQL
   - Export to `data/gold/analytics/patient_imaging.parquet`

4. **30_analytics_slices.sql**: Generate aggregations
   - Modality counts, demographics, study year distribution
   - Summary statistics as CSV/Parquet

## External Views Pattern

DuckDB's `read_parquet()` function creates **external views** that query Parquet files directly:

```sql
CREATE OR REPLACE VIEW bronze_imaging_instance AS
SELECT
    instance_uid,
    series_uid,
    modality,
    ...
FROM read_parquet('data/silver/imaging_instance/*.parquet');
```

**Benefits:**
- No data duplication (views reference original Parquet files)
- Wildcards (`*.parquet`) automatically include all files in directory
- Schema evolution: add new files without recreating views
- Lazy evaluation: only reads data when queried

## Workflow

### Building the Data Lake

```bash
# 1. De-identify DICOM files (Bronze layer)
make deidentify

# 2. Extract metadata + unify patients (Silver layer)
make lake-silver

# 3. Create linkage + run SQL transforms (Gold layer)
make lake-gold

# Combined: build entire lake
make lake
```

### Querying the Lake

```bash
# Open DuckDB CLI
duckdb health_data_lake.duckdb

# Query views
SELECT modality, COUNT(*) 
FROM bronze_imaging_instance 
GROUP BY modality;

# Join across layers
SELECT p.age, i.modality
FROM silver_patient_core p
JOIN gold_imaging_link l ON p.customer_id = l.customer_id
JOIN bronze_imaging_instance i ON l.instance_uid = i.instance_uid
LIMIT 10;
```

### Python Integration

The `etl/build_gold_views.py` module executes SQL scripts via DuckDB's Python API:

```python
import duckdb

conn = duckdb.connect('health_data_lake.duckdb')
conn.execute("CREATE VIEW ... FROM read_parquet(...)")
```

## Cloud Portability

SQL queries written for DuckDB are **portable** to cloud data warehouses:

- **AWS**: Athena (Presto), Redshift (PostgreSQL)
- **GCP**: BigQuery (Standard SQL)
- **Azure**: Synapse Analytics
- **Snowflake**: Native support

Example: The same `20_gold_joins.sql` works in Athena with minor syntax adjustments (e.g., `read_parquet` → external table).

## Performance Considerations

### When to Use DuckDB

✅ **Good for:**
- Analytical queries (aggregations, joins)
- Medium-scale data (GB to low TB on modern hardware)
- Reproducible research pipelines
- Local development and testing

❌ **Not ideal for:**
- Transactional workloads (OLTP)
- Concurrent multi-user writes
- Petabyte-scale data (use cloud warehouses)

### Optimization Tips

1. **Use Parquet**: Columnar format enables column pruning and predicate pushdown
2. **Partition data**: Organize Parquet by key columns (e.g., `year=2023/month=01/`)
3. **Filter early**: Apply `WHERE` clauses in views to reduce data scanned
4. **Index small dimension tables**: DuckDB auto-indexes small tables in memory

## Troubleshooting

### Database locked error
```
Error: database is locked
```
**Fix**: Close other DuckDB connections. Delete `.wal` file if needed:
```bash
rm health_data_lake.duckdb.wal
```

### View not found
```
Error: view 'bronze_imaging_instance' does not exist
```
**Fix**: Run initialization script:
```bash
duckdb health_data_lake.duckdb < sql/00_init.sql
```

### Parquet file not found
```
Error: No files found that match the pattern 'data/silver/*.parquet'
```
**Fix**: Build upstream layers first:
```bash
make lake-silver
```

## References

- **DuckDB Documentation**: https://duckdb.org/docs/
- **Parquet Format**: https://parquet.apache.org/
- **ANSI SQL Standard**: ISO/IEC 9075

---

**Last Updated**: 2025-11-12  
**Version**: 1.0.0
