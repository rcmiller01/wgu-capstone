#!/usr/bin/env python3
"""
Publish local data lake to S3 for cloud analytics.

Syncs Bronze/Silver/Gold layers to S3 bucket with appropriate partitioning
and metadata for AWS Glue/Athena integration.

Usage:
    python etl/publish_s3.py --bucket my-capstone-bucket --prefix datalake/
"""

import argparse
import subprocess
from pathlib import Path


def sync_to_s3(local_path: Path, s3_uri: str, dry_run: bool = False) -> None:
    """
    Sync local directory to S3 using AWS CLI.

    Args:
        local_path: Local directory to sync
        s3_uri: S3 destination (s3://bucket/prefix/)
        dry_run: If True, show what would be synced without uploading
    """
    if not local_path.exists():
        print(f"⚠ Local path does not exist: {local_path}")
        return

    cmd = [
        "aws",
        "s3",
        "sync",
        str(local_path),
        s3_uri,
        "--exclude",
        "*.pyc",
        "--exclude",
        "__pycache__/*",
    ]

    if dry_run:
        cmd.append("--dryrun")

    print(f"Syncing {local_path} → {s3_uri}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error syncing to S3: {e}")
        print(f"  stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        print("✗ AWS CLI not found. Install with: pip install awscli")
        raise


def publish_lake(
    local_root: Path, bucket: str, prefix: str = "", dry_run: bool = False
) -> None:
    """
    Publish entire data lake to S3.

    Args:
        local_root: Local data lake root (e.g., data/lake/)
        bucket: S3 bucket name
        prefix: S3 key prefix (e.g., datalake/)
        dry_run: If True, preview sync without uploading
    """
    layers = ["bronze", "silver", "gold"]

    for layer in layers:
        local_layer = local_root / layer
        s3_uri = f"s3://{bucket}/{prefix}{layer}/"

        if local_layer.exists():
            print(f"\n{'='*60}")
            print(f"Publishing {layer.upper()} layer")
            print(f"{'='*60}")
            sync_to_s3(local_layer, s3_uri, dry_run=dry_run)
        else:
            print(f"⚠ Skipping {layer} layer (not found at {local_layer})")

    print(f"\n✓ Data lake published to s3://{bucket}/{prefix}")
    print(f"\nNext steps:")
    print(f"  1. Run Glue crawler: make glue-catalog")
    print(f"  2. Create Athena views: make athena-views")
    print(f"  3. Query data: aws athena start-query-execution ...")


def main():
    parser = argparse.ArgumentParser(description="Publish data lake to S3")
    parser.add_argument(
        "--local-root",
        type=Path,
        default=Path("data/lake"),
        help="Local data lake root directory",
    )
    parser.add_argument(
        "--bucket", type=str, required=True, help="S3 bucket name (required)"
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="capstone/datalake/",
        help="S3 key prefix (default: capstone/datalake/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview sync without uploading",
    )

    args = parser.parse_args()

    publish_lake(
        local_root=args.local_root,
        bucket=args.bucket,
        prefix=args.prefix,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
