#!/usr/bin/env python3
"""
Ingest SIIM/CT Sample Images metadata into Bronze layer.

Extracts metadata from DICOM files and overview.csv, creating a Bronze
parquet dataset with raw metadata for downstream processing.

Usage:
    python etl/ingest_siim_metadata.py --output data/lake/bronze/imaging/
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import pydicom
from pydicom.errors import InvalidDicomError


def extract_dicom_metadata(dicom_path: Path) -> Optional[Dict]:
    """
    Extract metadata from a single DICOM file.

    Args:
        dicom_path: Path to DICOM file

    Returns:
        Dictionary of metadata fields, or None if invalid DICOM
    """
    try:
        ds = pydicom.dcmread(str(dicom_path), stop_before_pixels=True)

        metadata = {
            # Identifiers
            "file_path": str(dicom_path),
            "study_instance_uid": str(getattr(ds, "StudyInstanceUID", "")),
            "series_instance_uid": str(getattr(ds, "SeriesInstanceUID", "")),
            "sop_instance_uid": str(getattr(ds, "SOPInstanceUID", "")),
            # Patient demographics
            "patient_age": str(getattr(ds, "PatientAge", "")),
            "patient_sex": str(getattr(ds, "PatientSex", "")),
            # Study metadata
            "study_date": str(getattr(ds, "StudyDate", "")),
            "study_time": str(getattr(ds, "StudyTime", "")),
            "study_description": str(getattr(ds, "StudyDescription", "")),
            # Series metadata
            "modality": str(getattr(ds, "Modality", "")),
            "series_description": str(getattr(ds, "SeriesDescription", "")),
            "series_number": int(getattr(ds, "SeriesNumber", 0)),
            # Image metadata
            "rows": int(getattr(ds, "Rows", 0)),
            "columns": int(getattr(ds, "Columns", 0)),
            "slice_thickness": float(getattr(ds, "SliceThickness", 0.0))
            if hasattr(ds, "SliceThickness")
            else None,
            # Contrast information
            "contrast_bolus_agent": str(getattr(ds, "ContrastBolusAgent", "")),
            "contrast_bolus_route": str(getattr(ds, "ContrastBolusRoute", "")),
            # Technical parameters
            "kvp": float(getattr(ds, "KVP", 0.0)) if hasattr(ds, "KVP") else None,
            "exposure_time": float(getattr(ds, "ExposureTime", 0.0))
            if hasattr(ds, "ExposureTime")
            else None,
        }

        return metadata

    except InvalidDicomError:
        print(f"Warning: Invalid DICOM file: {dicom_path}")
        return None
    except Exception as e:
        print(f"Error reading {dicom_path}: {e}")
        return None


def ingest_ct_sample_images(
    ct_dir: Path, output_dir: Path, include_dicom: bool = True
) -> None:
    """
    Ingest CT Sample Images dataset into Bronze layer.

    Args:
        ct_dir: Path to CT Sample Images directory
        output_dir: Path to Bronze output directory
        include_dicom: Whether to extract metadata from DICOM files
    """
    print(f"Ingesting CT Sample Images from {ct_dir}")

    # Load overview.csv as base metadata
    overview_csv = ct_dir / "overview.csv"
    if not overview_csv.exists():
        raise FileNotFoundError(f"overview.csv not found at {overview_csv}")

    df_overview = pd.read_csv(overview_csv, index_col=0)
    print(f"Loaded {len(df_overview)} cases from overview.csv")

    # Extract DICOM metadata if requested
    if include_dicom:
        print("Extracting metadata from DICOM files...")
        dicom_dir = ct_dir / "dicom_dir"

        metadata_list = []
        for idx, row in df_overview.iterrows():
            dicom_path = dicom_dir / row["dicom_name"]

            if dicom_path.exists():
                dicom_meta = extract_dicom_metadata(dicom_path)
                if dicom_meta:
                    # Merge with overview.csv metadata
                    merged = {**row.to_dict(), **dicom_meta}
                    merged["case_id"] = row["id"]
                    metadata_list.append(merged)
            else:
                print(f"Warning: DICOM file not found: {dicom_path}")

        df_bronze = pd.DataFrame(metadata_list)
        print(f"Extracted metadata from {len(df_bronze)} DICOM files")
    else:
        # Use only overview.csv
        df_bronze = df_overview.copy()
        df_bronze["case_id"] = df_bronze["id"]

    # Add ingestion metadata
    df_bronze["ingestion_timestamp"] = pd.Timestamp.now()
    df_bronze["source_dataset"] = "ct_sample_images"
    df_bronze["data_version"] = "1.0"

    # Write to Bronze layer as parquet
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ct_imaging_bronze.parquet"
    df_bronze.to_parquet(output_file, index=False, engine="pyarrow")

    print(f"✓ Bronze layer written to {output_file}")
    print(f"  Records: {len(df_bronze)}")
    print(f"  Columns: {len(df_bronze.columns)}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(description="Ingest SIIM/CT metadata to Bronze")
    parser.add_argument(
        "--ct-dir",
        type=Path,
        default=Path("data/raw/CT Sample Images"),
        help="Path to CT Sample Images directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/lake/bronze/imaging"),
        help="Output directory for Bronze layer",
    )
    parser.add_argument(
        "--no-dicom",
        action="store_true",
        help="Skip DICOM metadata extraction (use only overview.csv)",
    )

    args = parser.parse_args()

    ingest_ct_sample_images(
        ct_dir=args.ct_dir, output_dir=args.output, include_dicom=not args.no_dicom
    )


if __name__ == "__main__":
    main()
