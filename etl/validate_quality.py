#!/usr/bin/env python3
"""
Data quality validation for Gold layer outputs.

Runs checks on final Parquet datasets to ensure:
- Files exist and are readable
- Required columns present
- No unexpected nulls in key columns
- Reasonable row counts

Usage:
    python -m etl.validate_quality
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import pandas as pd


def check_file_exists(file_path: Path) -> Tuple[bool, str]:
    """Check if file exists and is readable."""
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    try:
        df = pd.read_parquet(file_path)
        return True, f"✓ File readable ({len(df)} rows, {len(df.columns)} cols)"
    except Exception as e:
        return False, f"Error reading file: {e}"


def check_non_empty(df: pd.DataFrame, name: str) -> Tuple[bool, str]:
    """Check dataset is non-empty."""
    if len(df) == 0:
        return False, f"{name} is empty (0 rows)"
    return True, f"✓ {name} has {len(df)} rows"


def check_columns_exist(
    df: pd.DataFrame, name: str, required_cols: List[str]
) -> Tuple[bool, str]:
    """Check required columns are present."""
    missing = set(required_cols) - set(df.columns)
    if missing:
        return False, f"{name} missing columns: {missing}"
    return True, f"✓ {name} has all required columns"


def check_no_nulls(
    df: pd.DataFrame, name: str, key_cols: List[str]
) -> Tuple[bool, str]:
    """Check key columns have no nulls."""
    for col in key_cols:
        if col not in df.columns:
            continue

        null_count = df[col].isna().sum()
        if null_count > 0:
            return False, f"{name}.{col} has {null_count} nulls"

    return True, f"✓ {name} key columns have no nulls"


def validate_patient_imaging(file_path: Path) -> List[Tuple[bool, str]]:
    """Validate patient_imaging gold table."""
    results = []

    # Check file exists
    success, msg = check_file_exists(file_path)
    results.append((success, msg))
    if not success:
        return results

    # Load data
    df = pd.read_parquet(file_path)

    # Check non-empty
    results.append(check_non_empty(df, "patient_imaging"))

    # Check required columns
    required_cols = ["customer_id", "instance_uid"]
    results.append(check_columns_exist(df, "patient_imaging", required_cols))

    # Check key columns for nulls
    results.append(check_no_nulls(df, "patient_imaging", required_cols))

    # Check reasonable row count (should have some joined records)
    if len(df) < 10:
        results.append(
            (False, f"patient_imaging has only {len(df)} rows (expected >10)")
        )
    else:
        results.append((True, f"✓ patient_imaging has reasonable row count"))

    return results


def validate_analytics_slices(analytics_dir: Path) -> List[Tuple[bool, str]]:
    """Validate analytics slice outputs."""
    results = []

    # Check directory exists
    if not analytics_dir.exists():
        results.append((False, f"Analytics directory not found: {analytics_dir}"))
        return results

    results.append((True, f"✓ Analytics directory exists"))

    # Check for expected outputs
    expected_files = [
        "patient_imaging.parquet",
        "modality_counts.parquet",
    ]

    for file_name in expected_files:
        file_path = analytics_dir / file_name
        if file_path.exists():
            try:
                df = pd.read_parquet(file_path)
                results.append((True, f"✓ {file_name} ({len(df)} rows)"))
            except Exception as e:
                results.append((False, f"Error reading {file_name}: {e}"))
        else:
            results.append((False, f"Missing analytics file: {file_name}"))

    return results


def validate_quality(gold_dir: Path = Path("data/gold")) -> bool:
    """
    Run all quality checks on Gold layer.

    Args:
        gold_dir: Path to Gold layer directory

    Returns:
        True if all checks pass, False otherwise
    """
    print("Running quality validation on Gold layer...")
    print(f"  Location: {gold_dir}\n")

    all_results = []

    # Validate patient_imaging table
    print("Checking patient_imaging table...")
    patient_imaging_path = gold_dir / "analytics" / "patient_imaging.parquet"
    all_results.extend(validate_patient_imaging(patient_imaging_path))

    # Validate analytics slices
    print("\nChecking analytics slices...")
    analytics_dir = gold_dir / "analytics"
    all_results.extend(validate_analytics_slices(analytics_dir))

    # Print summary
    print("\n" + "=" * 60)
    failures = [r for r in all_results if not r[0]]

    if failures:
        print(f"✗ Quality validation FAILED ({len(failures)} issues)\n")
        for success, msg in all_results:
            symbol = "✓" if success else "✗"
            print(f"  {symbol} {msg}")
        return False
    else:
        print(f"✓ Quality validation PASSED ({len(all_results)} checks)\n")
        for success, msg in all_results:
            print(f"  {msg}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Validate Gold layer data quality"
    )
    parser.add_argument(
        "--gold-dir",
        type=Path,
        default=Path("data/gold"),
        help="Gold layer directory (default: data/gold)",
    )

    args = parser.parse_args()

    success = validate_quality(gold_dir=args.gold_dir)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
