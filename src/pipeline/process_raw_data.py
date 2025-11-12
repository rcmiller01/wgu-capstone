"""
Process raw NHANES and Synthea data into analysis-ready format.

This creates a synthetic performance measurement dataset combining:
- Synthea FHIR files (measure file processing latency)
- NHANES XPT files (measure file processing latency)
- VDH CSV files (measure file processing latency)

Generates simulated latency and validation metrics for pipeline performance study.
"""

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def process_synthea_data() -> pd.DataFrame:
    """Process Synthea FHIR files into performance records."""
    print("   Processing Synthea FHIR data...")

    synthea_dir = Path("data/raw/synthea/fhir")

    if not synthea_dir.exists():
        print("   ⚠️  Synthea directory not found, skipping...")
        return pd.DataFrame()

    fhir_files = list(synthea_dir.glob("*.json"))

    if not fhir_files:
        print("   ⚠️  No FHIR files found, skipping...")
        return pd.DataFrame()

    # Sample subset for processing (use first 1000 files)
    sample_size = min(1000, len(fhir_files))
    sampled_files = np.random.choice(fhir_files, sample_size, replace=False)

    records = []
    for fpath in sampled_files:
        file_size_kb = fpath.stat().st_size / 1024

        # Simulate latency based on file size (realistic serverless function timing)
        # Base: 5-15 seconds + size factor
        base_latency = np.random.uniform(5, 15)
        size_factor = (file_size_kb / 100) * np.random.uniform(0.1, 0.5)
        latency_sec = base_latency + size_factor

        # Add some noise
        latency_sec += np.random.normal(0, 2)
        latency_sec = max(1, latency_sec)  # Ensure positive

        # Validation: 96% pass rate (relaxed rules for optional FHIR elements)
        validation_passed = np.random.random() < 0.96

        records.append(
            {
                "data_source": "synthea",
                "file_name": fpath.name,
                "file_size_kb": round(file_size_kb, 2),
                "latency_sec": round(latency_sec, 2),
                "validation_passed": validation_passed,
            }
        )

    df = pd.DataFrame(records)
    print(f"   ✓ Processed {len(df):,} Synthea records")
    return df


def process_nhanes_data() -> pd.DataFrame:
    """Process NHANES XPT files into performance records."""
    print("   Processing NHANES data...")

    nhanes_dirs = [Path("data/raw/nhanes/2017-2018"), Path("data/raw/nhanes/2019-2020")]

    records = []
    for nhanes_dir in nhanes_dirs:
        if not nhanes_dir.exists():
            continue

        xpt_files = list(nhanes_dir.glob("*.XPT"))

        for fpath in xpt_files:
            file_size_kb = fpath.stat().st_size / 1024

            # Simulate latency (XPT files are smaller, faster processing)
            base_latency = np.random.uniform(3, 8)
            size_factor = (file_size_kb / 100) * np.random.uniform(0.05, 0.2)
            latency_sec = base_latency + size_factor

            # Add noise
            latency_sec += np.random.normal(0, 1)
            latency_sec = max(1, latency_sec)

            # Validation: 98% pass rate (structured survey data)
            validation_passed = np.random.random() < 0.98

            records.append(
                {
                    "data_source": "nhanes",
                    "file_name": fpath.name,
                    "file_size_kb": round(file_size_kb, 2),
                    "latency_sec": round(latency_sec, 2),
                    "validation_passed": validation_passed,
                }
            )

    df = pd.DataFrame(records)
    print(f"   ✓ Processed {len(df):,} NHANES records")
    return df


def process_vdh_data() -> pd.DataFrame:
    """Process VDH CSV files into performance records."""
    print("   Processing VDH data...")

    vdh_dir = Path("data/raw/vdh")
    csv_files = list(vdh_dir.glob("*.csv"))

    if not csv_files:
        print("   ⚠️  No VDH CSV files found, skipping...")
        return pd.DataFrame()

    records = []
    for fpath in csv_files:
        file_size_kb = fpath.stat().st_size / 1024

        # Simulate latency (small CSVs, very fast)
        base_latency = np.random.uniform(2, 5)
        size_factor = (file_size_kb / 100) * np.random.uniform(0.02, 0.1)
        latency_sec = base_latency + size_factor

        # Add noise
        latency_sec += np.random.normal(0, 0.5)
        latency_sec = max(1, latency_sec)

        # Validation: 99% pass rate (well-structured CSVs)
        validation_passed = np.random.random() < 0.99

        records.append(
            {
                "data_source": "vdh",
                "file_name": fpath.name,
                "file_size_kb": round(file_size_kb, 2),
                "latency_sec": round(latency_sec, 2),
                "validation_passed": validation_passed,
            }
        )

    df = pd.DataFrame(records)
    print(f"   ✓ Processed {len(df):,} VDH records")
    return df


def main():
    """Main processing pipeline."""
    print("=" * 70)
    print("PROCESSING RAW DATA TO ANALYSIS FORMAT")
    print("=" * 70)

    # Set random seed for reproducibility
    np.random.seed(12345)

    # Process each data source
    print("\n1. Processing data sources...")
    df_synthea = process_synthea_data()
    df_nhanes = process_nhanes_data()
    df_vdh = process_vdh_data()

    # Combine all sources
    print("\n2. Combining data sources...")
    df = pd.concat([df_synthea, df_nhanes, df_vdh], ignore_index=True)

    if len(df) == 0:
        print("   ❌ No data to process!")
        return

    print(f"   ✓ Combined {len(df):,} total records")

    # Add metadata
    df["processing_date"] = datetime.now().isoformat()

    # Save to parquet
    print("\n3. Saving processed data...")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "processed_data.parquet"
    df.to_parquet(output_path, index=False)
    print(f"   ✓ Saved to {output_path}")

    # Save metadata
    metadata = {
        "generated_date": datetime.now().isoformat(),
        "total_records": len(df),
        "data_sources": {"synthea": len(df_synthea), "nhanes": len(df_nhanes), "vdh": len(df_vdh)},
        "columns": list(df.columns),
        "seed": 12345,
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✓ Saved metadata to {metadata_path}")

    # Display summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nTotal Records: {len(df):,}")
    print("\nBy Data Source:")
    print(df["data_source"].value_counts().to_string())
    print("\nLatency Statistics:")
    print(f"  Mean: {df['latency_sec'].mean():.2f}s")
    print(f"  Median (P50): {df['latency_sec'].median():.2f}s")
    print(f"  P95: {df['latency_sec'].quantile(0.95):.2f}s")
    print(f"\nValidation Pass Rate: {df['validation_passed'].mean()*100:.1f}%")
    print("\n✓ Processing complete!")


if __name__ == "__main__":
    main()
