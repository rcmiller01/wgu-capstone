-- DuckDB Pragmas for Deterministic Execution
-- ============================================
-- This file configures DuckDB settings for reproducible, deterministic query execution.
-- Execute these pragmas BEFORE running any SQL transformations to ensure consistency.
--
-- Usage:
--   duckdb capstone.duckdb < sql/duckdb_pragmas.sql
--
-- Or in Python:
--   import duckdb
--   conn = duckdb.connect('capstone.duckdb')
--   conn.execute(open('sql/duckdb_pragmas.sql').read())
--
-- Reference: https://duckdb.org/docs/configuration/pragmas.html

-- Force single-threaded execution for deterministic results
-- This ensures queries produce identical outputs across machines and runs
-- (Trade-off: Slower execution, but guaranteed reproducibility)
PRAGMA threads=1;

-- Disable progress bar output (useful for automated pipelines)
PRAGMA enable_progress_bar=false;

-- Set memory limit to 4GB (prevents runaway queries, suitable for GB-scale data)
PRAGMA memory_limit='4GB';

-- Enable optimizer for efficient query plans
-- (DuckDB's optimizer is deterministic, so this doesn't affect reproducibility)
PRAGMA enable_optimizer=true;

-- Set hash function for deterministic hash joins
-- Note: DuckDB uses a deterministic hash by default, but we make it explicit
PRAGMA force_parallelism=false;

-- Verification query: Display current settings
SELECT 
    'Threads: ' || current_setting('threads') as setting_1,
    'Memory Limit: ' || current_setting('memory_limit') as setting_2,
    'Progress Bar: ' || current_setting('enable_progress_bar') as setting_3,
    'Optimizer: ' || current_setting('enable_optimizer') as setting_4;

-- Expected output:
-- ┌─────────────┬─────────────────────┬───────────────────────┬──────────────────────┐
-- │  setting_1  │     setting_2       │       setting_3       │      setting_4       │
-- ├─────────────┼─────────────────────┼───────────────────────┼──────────────────────┤
-- │ Threads: 1  │ Memory Limit: 4GB   │ Progress Bar: false   │ Optimizer: true      │
-- └─────────────┴─────────────────────┴───────────────────────┴──────────────────────┘

SELECT 'DuckDB pragmas configured for deterministic execution' as status;
