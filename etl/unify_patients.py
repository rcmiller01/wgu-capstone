#!/usr/bin/env python3
"""
Unify patient data from multiple sources into Silver layer.

Creates a synthetic patient_core table for demonstration purposes.
In a real deployment, this would consolidate actual patient records from
Synthea, NHANES, VDH sources.

Usage:
    python -m etl.unify_patients --output data/silver/patient_core
"""

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

# Deterministic seed for reproducibility
SEED = 12345


def generate_synthetic_patients(n_patients: int = 1000, seed: int = SEED) -> pd.DataFrame:
    """
    Generate synthetic patient records for demonstration.

    In production, this would read and consolidate actual patient data
    from Synthea FHIR exports, NHANES survey data, and VDH records.

    Args:
        n_patients: Number of synthetic patients to generate
        seed: Random seed for reproducibility

    Returns:
        DataFrame with patient_core schema
    """
    np.random.seed(seed)

    # Generate customer IDs (1-indexed)
    customer_ids = np.arange(1, n_patients + 1)

    # Pseudonymize customer IDs (as would be done with real MRNs)
    def hash_customer_id(cid: int) -> str:
        return hashlib.sha256(f"capstone_2025:{cid}".encode()).hexdigest()[:16]

    # Generate demographic data
    ages = np.random.randint(18, 90, size=n_patients)
    genders = np.random.choice(["M", "F", "O"], size=n_patients, p=[0.48, 0.48, 0.04])

    # Generate vitals (realistic ranges)
    heights_cm = np.random.normal(170, 15, size=n_patients).clip(140, 210)
    weights_kg = np.random.normal(75, 20, size=n_patients).clip(40, 200)
    bmis = weights_kg / ((heights_cm / 100) ** 2)

    # Systolic/diastolic blood pressure
    sbp = np.random.normal(125, 15, size=n_patients).clip(90, 180)
    dbp = np.random.normal(80, 10, size=n_patients).clip(60, 110)

    # Create DataFrame
    df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_id_hash": [hash_customer_id(cid) for cid in customer_ids],
            "age": ages,
            "gender": genders,
            "height_cm": heights_cm.round(1),
            "weight_kg": weights_kg.round(1),
            "bmi": bmis.round(1),
            "systolic_bp": sbp.round(0).astype(int),
            "diastolic_bp": dbp.round(0).astype(int),
            "state": "VA",  # Virginia focus for capstone
            "source": "synthetic",
            "created_at": pd.Timestamp.now(),
        }
    )

    return df


def unify_patients(output_dir: Path, n_patients: int = 1000) -> None:
    """
    Create unified patient_core dataset.

    Args:
        output_dir: Output directory for patient_core parquet files
        n_patients: Number of patients to generate
    """
    print("Generating unified patient_core dataset...")
    print(f"  Target: {n_patients} patients")

    # Generate synthetic patient data
    # In production: load and merge Synthea/NHANES/VDH records
    df = generate_synthetic_patients(n_patients=n_patients, seed=SEED)

    print(f"  Generated {len(df)} patient records")
    print(f"  Age range: {df['age'].min()}-{df['age'].max()}")
    print(f"  Gender distribution: {df['gender'].value_counts().to_dict()}")

    # Write to Silver layer
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "patient_core.parquet"

    df.to_parquet(output_file, index=False, engine="pyarrow")

    print(f"\n✓ Patient core written to {output_file}")
    print(f"  Records: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="Unify patient data into Silver layer"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/silver/patient_core"),
        help="Output directory for patient_core parquet",
    )
    parser.add_argument(
        "--n-patients",
        type=int,
        default=1000,
        help="Number of synthetic patients to generate (default: 1000)",
    )

    args = parser.parse_args()

    unify_patients(output_dir=args.output, n_patients=args.n_patients)


if __name__ == "__main__":
    main()
