#!/usr/bin/env python3
"""
Ingest SIIM/CT Sample Images metadata into Silver layer.

Extracts metadata from sanitized DICOM files in Bronze layer, creating
analytics-friendly parquet dataset with instance-level metadata.

Usage:
    python etl/ingest_siim_metadata.py \
        --input data/bronze/images \
        --output data/silver/imaging_instance
"""

import argparse
import hashlib
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import pydicom
from pydicom.errors import InvalidDicomError


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_dicom_metadata(dicom_path: Path, bronze_root: Path) -> Optional[Dict]:
    """
    Extract metadata from sanitized DICOM file.

    Args:
        dicom_path: Path to DICOM file
        bronze_root: Root of bronze layer for relative path calc

    Returns:
        Dictionary with required metadata fields
    """
    try:
        ds = pydicom.dcmread(str(dicom_path), stop_before_pixels=True)

        # Extract study year from StudyDate (YYYYMMDD)
        study_date = str(getattr(ds, "StudyDate", ""))
        study_year = int(study_date[:4]) if len(study_date) >= 4 else None

        # Check burned-in annotation flag
        burned_in = False
        if hasattr(ds, "BurnedInAnnotation"):
            burned_in_val = str(ds.BurnedInAnnotation).upper()
            burned_in = burned_in_val == "YES" or burned_in_val == ""
        else:
            # Missing tag = assume potential burned-in
            burned_in = True

        metadata = {
            "instance_uid": str(getattr(ds, "SOPInstanceUID", "")),
            "series_uid": str(getattr(ds, "SeriesInstanceUID", "")),
            "study_uid": str(getattr(ds, "StudyInstanceUID", "")),
            "modality": str(getattr(ds, "Modality", "")),
            "body_part_examined": str(getattr(ds, "BodyPartExamined", "")),
            "manufacturer": str(getattr(ds, "Manufacturer", "")),
            "rows": int(getattr(ds, "Rows", 0)),
            "cols": int(getattr(ds, "Columns", 0)),
            "photometric_interp": str(
                getattr(ds, "PhotometricInterpretation", "")
            ),
            "burned_in_text_flag": burned_in,
            "transfer_syntax_uid": str(
                getattr(ds.file_meta, "TransferSyntaxUID", "")
            ),
            "file_sha256": compute_file_hash(dicom_path),
            "relative_path": str(dicom_path.relative_to(bronze_root)),
            "study_year": study_year,
        }

        return metadata

    except InvalidDicomError:
        print(f"Warning: Invalid DICOM file: {dicom_path}")
        return None
    except Exception as e:
        print(f"Error reading {dicom_path}: {e}")
        return None


def ingest_imaging_metadata(bronze_dir: Path, output_dir: Path) -> None:
    """
    Ingest imaging metadata from Bronze to Silver layer.

    Args:
        bronze_dir: Path to Bronze layer (sanitized DICOM files)
        output_dir: Path to Silver layer output directory
    """
    print(f"Extracting metadata from Bronze layer: {bronze_dir}")

    # Find all DICOM files
    dicom_files = list(bronze_dir.rglob("*.dcm"))
    print(f"Found {len(dicom_files)} DICOM files")

    metadata_list = []
    for dicom_path in dicom_files:
        meta = extract_dicom_metadata(dicom_path, bronze_dir)
        if meta:
            metadata_list.append(meta)

    if not metadata_list:
        print("⚠ No valid metadata extracted")
        return

    df_silver = pd.DataFrame(metadata_list)

    # Add ingestion metadata
    df_silver["ingestion_timestamp"] = pd.Timestamp.now()
    df_silver["source_layer"] = "bronze"

    # Write to Silver layer as parquet
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "imaging_instance.parquet"
    df_silver.to_parquet(output_file, index=False, engine="pyarrow")

    print(f"\n✓ Silver layer written to {output_file}")
    print(f"  Records: {len(df_silver)}")
    print(f"  Columns: {len(df_silver.columns)}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
    print(f"  Burned-in text flags: {df_silver['burned_in_text_flag'].sum()}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract imaging metadata to Silver layer"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/bronze/images"),
        help="Input Bronze directory (sanitized DICOM)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/silver/imaging_instance"),
        help="Output Silver directory",
    )

    args = parser.parse_args()

    ingest_imaging_metadata(bronze_dir=args.input, output_dir=args.output)


if __name__ == "__main__":
    main()
