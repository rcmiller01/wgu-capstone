#!/usr/bin/env python3
"""
Publish Glue Data Catalog tables for Athena querying.

Creates AWS Glue database and tables pointing to S3 data lake.
No-op when running locally (requires AWS credentials).

Usage:
    python etl/publish_glue_catalog.py --database capstone_imaging --s3-bucket my-bucket
"""

import argparse
import json
import subprocess
from pathlib import Path


def create_glue_database(database_name: str) -> None:
    """Create Glue database if it doesn't exist."""
    cmd = [
        "aws",
        "glue",
        "create-database",
        "--database-input",
        json.dumps({"Name": database_name, "Description": "Capstone imaging database"}),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Created Glue database: {database_name}")
    except subprocess.CalledProcessError as e:
        if "AlreadyExistsException" in e.stderr:
            print(f"Database {database_name} already exists")
        else:
            print(f"✗ Error creating database: {e.stderr}")
            raise


def create_glue_table(
    database_name: str, table_name: str, s3_location: str, schema_path: Path
) -> None:
    """
    Create Glue table from SQL schema file.

    Args:
        database_name: Glue database name
        table_name: Table name
        s3_location: S3 path with parquet files
        schema_path: Path to SQL schema file
    """
    # Read schema (simplified - would need proper DDL parsing)
    with open(schema_path) as f:
        schema_sql = f.read()

    # Extract columns (basic parsing)
    columns = []
    for line in schema_sql.split("\n"):
        if "VARCHAR" in line or "INTEGER" in line or "BOOLEAN" in line:
            parts = line.strip().split()
            if len(parts) >= 2:
                col_name = parts[0].strip(",")
                col_type = "string" if "VARCHAR" in parts[1] else "int"
                columns.append({"Name": col_name, "Type": col_type})

    table_input = {
        "Name": table_name,
        "StorageDescriptor": {
            "Columns": columns,
            "Location": s3_location,
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
            },
        },
        "TableType": "EXTERNAL_TABLE",
    }

    cmd = [
        "aws",
        "glue",
        "create-table",
        "--database-name",
        database_name,
        "--table-input",
        json.dumps(table_input),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Created table: {database_name}.{table_name}")
    except subprocess.CalledProcessError as e:
        if "AlreadyExistsException" in e.stderr:
            print(f"Table {table_name} already exists")
        else:
            print(f"✗ Error creating table: {e.stderr}")


def publish_catalog(
    database_name: str, bucket: str, prefix: str, local_mode: bool = False
) -> None:
    """
    Publish Glue catalog for all tables.

    Args:
        database_name: Glue database name
        bucket: S3 bucket
        prefix: S3 prefix
        local_mode: If True, skip (no-op locally)
    """
    if local_mode:
        print("⚠ Local mode: Skipping Glue catalog creation")
        print("  (Requires AWS credentials and S3 data)")
        print("\nTo publish later:")
        print(f"  python etl/publish_glue_catalog.py --database {database_name} \\")
        print(f"    --s3-bucket {bucket} --s3-prefix {prefix}")
        return

    print(f"Publishing Glue catalog: {database_name}")

    # Create database
    create_glue_database(database_name)

    # Create tables
    tables = [
        ("imaging_study", f"s3://{bucket}/{prefix}bronze/imaging/", "schema/imaging_study.sql"),
        ("imaging_cohort_links", f"s3://{bucket}/{prefix}silver/imaging/", "schema/series.sql"),
    ]

    for table_name, s3_location, schema_file in tables:
        schema_path = Path("etl") / schema_file
        if schema_path.exists():
            create_glue_table(database_name, table_name, s3_location, schema_path)

    print(f"\n✓ Glue catalog published")
    print(f"\nQuery with Athena:")
    print(f"  SELECT * FROM {database_name}.imaging_study LIMIT 10;")


def main():
    parser = argparse.ArgumentParser(description="Publish Glue Data Catalog")
    parser.add_argument(
        "--database",
        type=str,
        default="capstone_imaging",
        help="Glue database name",
    )
    parser.add_argument(
        "--s3-bucket",
        type=str,
        help="S3 bucket (required for AWS mode)",
    )
    parser.add_argument(
        "--s3-prefix",
        type=str,
        default="capstone/datalake/",
        help="S3 prefix",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Local mode (no-op, skip Glue)",
    )

    args = parser.parse_args()

    if not args.local and not args.s3_bucket:
        parser.error("--s3-bucket required unless --local specified")

    publish_catalog(
        database_name=args.database,
        bucket=args.s3_bucket or "",
        prefix=args.s3_prefix,
        local_mode=args.local,
    )


if __name__ == "__main__":
    main()
