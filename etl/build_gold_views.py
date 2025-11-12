#!/usr/bin/env python3
"""
Execute SQL transformations to build Gold layer using DuckDB.

This module orchestrates the execution of SQL scripts that:
1. Create views over Parquet datasets (Bronze/Silver)
2. Perform joins and transformations
3. Export Gold analytics tables

Usage:
    python -m etl.build_gold_views --db capstone.duckdb
"""

import argparse
import sys
from pathlib import Path

import duckdb


def execute_sql_file(conn: duckdb.DuckDBPyConnection, sql_file: Path) -> None:
    """
    Execute a SQL file through DuckDB connection.

    Args:
        conn: DuckDB connection
        sql_file: Path to SQL file to execute

    Raises:
        RuntimeError: If SQL execution fails
    """
    print(f"Executing {sql_file.name}...")

    with open(sql_file, "r") as f:
        sql_content = f.read()

    try:
        # Split on semicolons and execute statements separately
        # (DuckDB can handle multiple statements, but split for better error reporting)
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        for i, stmt in enumerate(statements, 1):
            try:
                conn.execute(stmt)
            except Exception as e:
                print(f"  ✗ Error in statement {i}:")
                print(f"    {stmt[:100]}...")
                raise RuntimeError(f"SQL error in {sql_file.name} statement {i}: {e}") from e

        print(f"  ✓ {sql_file.name} complete ({len(statements)} statements)")

    except Exception as e:
        print(f"✗ Failed to execute {sql_file.name}")
        raise


def build_gold_views(db_path: Path, sql_dir: Path) -> None:
    """
    Build Gold layer by executing SQL transformation pipeline.

    Args:
        db_path: Path to DuckDB database file
        sql_dir: Directory containing SQL scripts

    Raises:
        SystemExit: If any SQL execution fails
    """
    print("Building Gold layer with DuckDB...")
    print(f"  Database: {db_path}")
    print(f"  SQL scripts: {sql_dir}")

    # Ensure SQL directory exists
    if not sql_dir.exists():
        print(f"✗ SQL directory not found: {sql_dir}")
        sys.exit(1)

    # Connect to DuckDB (creates file if not exists)
    print("\nConnecting to DuckDB...")
    conn = duckdb.connect(str(db_path))

    # SQL files to execute (in order)
    sql_files = [
        "00_init.sql",
        "10_silver_curate.sql",
        "20_gold_joins.sql",
        "30_analytics_slices.sql",
    ]

    print("\nExecuting SQL pipeline...\n")

    try:
        for sql_file_name in sql_files:
            sql_file = sql_dir / sql_file_name

            if not sql_file.exists():
                print(f"⚠ Skipping {sql_file_name} (not found)")
                continue

            execute_sql_file(conn, sql_file)

        print("\n✓ Gold layer build complete")

    except Exception as e:
        print(f"\n✗ Gold layer build failed: {e}")
        sys.exit(1)

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Build Gold layer using DuckDB SQL transformations"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("capstone.duckdb"),
        help="DuckDB database file (default: capstone.duckdb)",
    )
    parser.add_argument(
        "--sql-dir",
        type=Path,
        default=Path("sql"),
        help="Directory containing SQL scripts (default: sql/)",
    )

    args = parser.parse_args()

    build_gold_views(db_path=args.db, sql_dir=args.sql_dir)


if __name__ == "__main__":
    main()
