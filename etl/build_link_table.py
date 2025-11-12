#!/usr/bin/env python3
"""
Build synthetic patient-image link table.

Creates Gold layer table linking imaging instances to synthetic patient
records using deterministic hash-based mapping. This linkage is for
demonstration purposes ONLY and does not reflect real patient-image
associations.

Usage:
    python etl/build_link_table.py \
        --imaging data/silver/imaging_instance \
        --cohort data/processed/synthea_cohort_va.parquet \
        --output data/gold/imaging_link
"""

import argparse
import hashlib
from pathlib import Path

import pandas as pd

# Global seed for deterministic hashing
LINKAGE_SEED = "capstone_2025"


def hash_to_customer_id(instance_uid: str, num_patients: int) -> int:
    """
    Map instance UID to customer ID using deterministic hash.

    Algorithm: customer_id = hash_128(instance_uid + seed) % N + 1

    Args:
        instance_uid: DICOM SOPInstanceUID
        num_patients: Total number of patients in cohort (N)

    Returns:
        customer_id (1-indexed)
    """
    # Concatenate instance UID with global seed
    hash_input = f"{instance_uid}{LINKAGE_SEED}"

    # Compute SHA-256 hash and take first 128 bits (16 bytes)
    hash_bytes = hashlib.sha256(hash_input.encode()).digest()[:16]

    # Convert to integer
    hash_int = int.from_bytes(hash_bytes, byteorder="big")

    # Map to customer_id range: 1 to N
    customer_id = (hash_int % num_patients) + 1

    return customer_id


def build_synthetic_links(
    imaging_df: pd.DataFrame, num_patients: int
) -> pd.DataFrame:
    """
    Build synthetic patient-image links using deterministic hashing.

    Args:
        imaging_df: Silver imaging metadata (with instance_uid)
        num_patients: Total patients in cohort (for modulo mapping)

    Returns:
        Link table with (customer_id, instance_uid, study_uid,
                         modality, study_year)
    """
    links = []

    for _, row in imaging_df.iterrows():
        instance_uid = row["instance_uid"]
        customer_id = hash_to_customer_id(instance_uid, num_patients)

        links.append(
            {
                "customer_id": customer_id,
                "instance_uid": instance_uid,
                "study_uid": row["study_uid"],
                "modality": row["modality"],
                "study_year": row.get("study_year"),
            }
        )

    return pd.DataFrame(links)


def build_link_table(
    imaging_path: Path, cohort_path: Path, output_path: Path
) -> None:
    """
    Build and save synthetic link table.

    Args:
        imaging_path: Path to Silver imaging_instance parquet
        cohort_path: Path to processed cohort data (for count)
        output_path: Path for Gold layer output
    """
    print("Building synthetic patient-image link table")

    # Load imaging metadata
    if imaging_path.is_dir():
        # Read all parquet files in directory
        parquet_files = list(imaging_path.glob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(
                f"No parquet files found in {imaging_path}"
            )
        df_imaging = pd.concat(
            [pd.read_parquet(f) for f in parquet_files], ignore_index=True
        )
    else:
        df_imaging = pd.read_parquet(imaging_path)

    print(f"  Imaging instances: {len(df_imaging)}")

    # Get patient count from cohort
    if cohort_path.is_dir():
        cohort_files = list(cohort_path.glob("*.parquet"))
        if not cohort_files:
            raise FileNotFoundError(
                f"No parquet files found in {cohort_path}"
            )
        df_cohort = pd.concat(
            [pd.read_parquet(f) for f in cohort_files], ignore_index=True
        )
    else:
        df_cohort = pd.read_parquet(cohort_path)

    num_patients = len(df_cohort["customer_id"].unique())
    print(f"  Cohort patients: {num_patients}")

    # Build synthetic links
    df_links = build_synthetic_links(df_imaging, num_patients)

    # Add metadata
    df_links["link_method"] = "deterministic_hash"
    df_links["linkage_seed"] = LINKAGE_SEED
    df_links["created_at"] = pd.Timestamp.now()

    # Write to Gold layer
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "customer_image_link.parquet"
    df_links.to_parquet(output_file, index=False, engine="pyarrow")

    print(f"\n✓ Link table written to {output_file}")
    print(f"  Records: {len(df_links)}")
    print(f"  Unique customers: {df_links['customer_id'].nunique()}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="Build synthetic patient-image link table"
    )
    parser.add_argument(
        "--imaging",
        type=Path,
        default=Path("data/silver/imaging_instance"),
        help="Path to Silver imaging metadata",
    )
    parser.add_argument(
        "--cohort",
        type=Path,
        default=Path("data/processed/synthea_cohort_va.parquet"),
        help="Path to cohort data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/gold/imaging_link"),
        help="Output directory for Gold layer",
    )

    args = parser.parse_args()

    build_link_table(
        imaging_path=args.imaging,
        cohort_path=args.cohort,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
