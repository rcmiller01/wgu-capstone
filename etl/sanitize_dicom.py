#!/usr/bin/env python3
"""
Sanitize DICOM files by removing/redacting PHI tags.

Implements DICOM de-identification per HIPAA Safe Harbor and DICOM
PS3.15 Annex E. Flags files with potential burned-in PHI for manual
review.

Usage:
    python etl/sanitize_dicom.py \
        --input data/raw/CT_Sample_Images/dicom_dir \
        --output data/bronze/images/
"""

import argparse
import hashlib
from pathlib import Path
from typing import Optional

import pandas as pd
import pydicom


# DICOM tags to remove (HIPAA identifiers per PS3.15 Annex E)
PHI_TAGS_TO_REMOVE = [
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
    "StudyID",
    "AccessionNumber",
    "DeviceSerialNumber",
    "PlateID",
]


def hash_identifier(value: str, salt: str = "capstone_2025") -> str:
    """
    Create a one-way hash of an identifier for pseudonymization.

    Args:
        value: Original identifier
        salt: Salt for HMAC (use consistent salt for deterministic mapping)

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:16]


def check_burned_in_annotation(ds: pydicom.Dataset) -> bool:
    """
    Check for burned-in annotation flag in DICOM.

    Per DICOM tag (0028,0301) BurnedInAnnotation:
    - "YES" = burned-in text present
    - "NO" = no burned-in text
    - Missing = assume potential burned-in text (flag as True)

    Args:
        ds: pydicom Dataset

    Returns:
        True if burned-in text detected or tag missing, False otherwise
    """
    if not hasattr(ds, "BurnedInAnnotation"):
        # Tag missing - assume potential burned-in text
        return True

    burned_in = str(ds.BurnedInAnnotation).upper()
    return burned_in == "YES" or burned_in == ""


def sanitize_dicom(
    dicom_path: Path, output_path: Path, pseudonymize: bool = False
) -> dict:
    """
    Sanitize a single DICOM file by removing/redacting PHI.

    Note: Does NOT transform pixel data. Only flags burned-in text.

    Args:
        dicom_path: Input DICOM file
        output_path: Output sanitized DICOM file
        pseudonymize: Whether to hash identifiers vs. remove completely

    Returns:
        Dictionary with sanitization summary
    """
    ds = pydicom.dcmread(str(dicom_path))

    summary = {
        "input_file": str(dicom_path),
        "output_file": str(output_path),
        "tags_removed": [],
        "tags_pseudonymized": [],
        "burned_in_text_flag": False,
    }

    # Check burned-in annotation BEFORE removing tags
    summary["burned_in_text_flag"] = check_burned_in_annotation(ds)

    # Remove PHI tags
    for tag_name in PHI_TAGS_TO_REMOVE:
        if hasattr(ds, tag_name):
            original_value = str(getattr(ds, tag_name))

            if pseudonymize and tag_name in [
                "PatientID",
                "StudyID",
                "AccessionNumber",
            ]:
                # Pseudonymize key identifiers (for linking)
                hashed_value = hash_identifier(original_value)
                setattr(ds, tag_name, hashed_value)
                summary["tags_pseudonymized"].append(
                    f"{tag_name}: {original_value} → {hashed_value}"
                )
            else:
                # Remove completely
                delattr(ds, tag_name)
                summary["tags_removed"].append(tag_name)

    # Remove private tags (vendor-specific, may contain PHI)
    ds.remove_private_tags()

    # Add de-identification note
    ds.PatientIdentityRemoved = "YES"
    ds.DeidentificationMethod = "HIPAA Safe Harbor + DICOM PS3.15 Annex E"

    # Write sanitized DICOM (do NOT transform pixel data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ds.save_as(str(output_path), write_like_original=False)

    return summary


def sanitize_batch(
    input_dir: Path,
    output_dir: Path,
    parquet_input: Optional[Path] = None
) -> None:
    """
    Sanitize a batch of DICOM files.

    Args:
        input_dir: Directory with original DICOM files
        output_dir: Directory for sanitized DICOM files
        parquet_input: Optional Bronze parquet with file paths
    """
    print(f"Sanitizing DICOM files from {input_dir}")

    # Find DICOM files
    if parquet_input and parquet_input.exists():
        # Use Bronze parquet as source
        df = pd.read_parquet(parquet_input)
        dicom_files = [
            Path(p) for p in df["file_path"] if Path(p).exists()
        ]
    else:
        # Scan directory
        dicom_files = list(input_dir.glob("**/*.dcm"))

    print(f"Found {len(dicom_files)} DICOM files")

    summaries = []
    burned_in_count = 0

    for dicom_path in dicom_files:
        # Preserve relative path structure
        rel_path = dicom_path.relative_to(input_dir)
        output_path = output_dir / rel_path

        try:
            summary = sanitize_dicom(
                dicom_path, output_path, pseudonymize=True
            )
            summaries.append(summary)

            if summary["burned_in_text_flag"]:
                burned_in_count += 1
                print(f"⚠ {dicom_path.name}: burned-in text detected")

        except Exception as e:
            print(f"✗ Error processing {dicom_path}: {e}")

    # Write sanitization report
    report_path = output_dir / "sanitization_report.json"
    import json

    with open(report_path, "w") as f:
        json.dump(summaries, f, indent=2)

    print(f"\n✓ Sanitized {len(summaries)} DICOM files")
    print(f"  Output: {output_dir}")
    print(f"  Files flagged for burned-in text: {burned_in_count}")
    print(f"  Report: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize DICOM files (remove PHI)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/CT Sample Images/dicom_dir"),
        help="Input directory with DICOM files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/bronze/images"),
        help="Output directory for sanitized DICOM files",
    )
    parser.add_argument(
        "--bronze-parquet",
        type=Path,
        help="Optional Bronze parquet with file paths",
    )

    args = parser.parse_args()

    sanitize_batch(
        input_dir=args.input,
        output_dir=args.output,
        parquet_input=args.bronze_parquet,
    )


if __name__ == "__main__":
    main()
