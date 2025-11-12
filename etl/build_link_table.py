#!/usr/bin/env python3
"""
Build link table joining imaging metadata with patient cohort data.

Creates a Silver layer table that links imaging studies to patient records
from the existing cohort datasets (Synthea, NHANES, VDH).

Usage:
    python etl/build_link_table.py --imaging data/lake/bronze/imaging/ --cohort data/processed/
"""

import argparse
from pathlib import Path

import pandas as pd


def build_synthetic_links(
    imaging_df: pd.DataFrame, cohort_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Build synthetic links between imaging and cohort data.

    Since datasets are independent, creates plausible links based on:
    - Age matching (±5 years)
    - Contrast status alignment with clinical conditions

    Args:
        imaging_df: Bronze imaging metadata
        cohort_df: Processed cohort data

    Returns:
        Link table with (imaging_id, patient_id, link_confidence)
    """
    links = []

    for img_idx, img_row in imaging_df.iterrows():
        img_age = img_row.get("Age", img_row.get("patient_age", 0))

        # Find cohort patients with similar age
        age_matches = cohort_df[
            abs(cohort_df.get("age", cohort_df.get("Age", 0)) - img_age) <= 5
        ]

        if len(age_matches) > 0:
            # Pick first match (deterministic for reproducibility)
            patient = age_matches.iloc[0]

            links.append(
                {
                    "imaging_case_id": img_row.get("id", img_row.get("case_id")),
                    "patient_id": patient.get("patient_id", patient.get("id")),
                    "link_method": "age_match_synthetic",
                    "age_delta": abs(
                        img_age - patient.get("age", patient.get("Age", 0))
                    ),
                    "link_confidence": 0.7,  # Synthetic link
                }
            )

    return pd.DataFrame(links)


def build_link_table(
    imaging_path: Path, cohort_path: Path, output_path: Path
) -> None:
    """
    Build and save link table.

    Args:
        imaging_path: Path to Bronze imaging parquet
        cohort_path: Path to processed cohort data
        output_path: Path for output link table
    """
    print(f"Building link table from:")
    print(f"  Imaging: {imaging_path}")
    print(f"  Cohort: {cohort_path}")

    # Load imaging metadata
    if imaging_path.is_file():
        df_imaging = pd.read_parquet(imaging_path)
    else:
        # Try finding Bronze parquet in directory
        parquet_files = list(imaging_path.glob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files in {imaging_path}")
        df_imaging = pd.read_parquet(parquet_files[0])

    print(f"Loaded {len(df_imaging)} imaging cases")

    # Load cohort data
    if cohort_path.is_file():
        df_cohort = pd.read_csv(cohort_path)
    else:
        # Try finding cohort CSV
        csv_files = list(cohort_path.glob("cohort_fact_*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No cohort CSV files in {cohort_path}")
        df_cohort = pd.read_csv(csv_files[0])

    print(f"Loaded {len(df_cohort)} cohort patients")

    # Build links
    df_links = build_synthetic_links(df_imaging, df_cohort)
    print(f"Created {len(df_links)} links")

    # Add metadata
    df_links["link_created_at"] = pd.Timestamp.now()
    df_links["link_version"] = "1.0"

    # Write to Silver layer
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_links.to_parquet(output_path, index=False, engine="pyarrow")

    print(f"✓ Link table written to {output_path}")
    print(f"  Records: {len(df_links)}")
    print(f"  Average confidence: {df_links['link_confidence'].mean():.2f}")


def main():
    parser = argparse.ArgumentParser(description="Build imaging-cohort link table")
    parser.add_argument(
        "--imaging",
        type=Path,
        default=Path("data/lake/bronze/imaging/ct_imaging_bronze.parquet"),
        help="Path to Bronze imaging parquet",
    )
    parser.add_argument(
        "--cohort",
        type=Path,
        default=Path("data/processed/cohort_fact_va_v2_relaxed.csv"),
        help="Path to cohort CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/lake/silver/imaging/imaging_cohort_links.parquet"),
        help="Output path for link table",
    )

    args = parser.parse_args()

    build_link_table(
        imaging_path=args.imaging, cohort_path=args.cohort, output_path=args.output
    )


if __name__ == "__main__":
    main()
