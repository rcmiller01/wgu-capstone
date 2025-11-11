#!/usr/bin/env python3
"""
Data Profiling Script - Non-Destructive Analysis
Walks data/raw and data/interim to profile all data files.
Generates:
  - reports/data_manifest.csv
  - reports/schema_profile.md
"""

import pandas as pd
import numpy as np
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys
import warnings
warnings.filterwarnings('ignore')

# Ensure we can handle large XPT files
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

# PII pattern detection
PII_PATTERNS = [
    'name', 'firstname', 'lastname', 'fullname', 'patient_name', 'provider_name',
    'email', 'mail', 'e_mail',
    'address', 'street', 'addr', 'home_address', 'mailing',
    'phone', 'telephone', 'cell', 'mobile', 'fax',
    'ssn', 'social_security', 'ss_number',
    'mrn', 'medical_record', 'patient_id', 'person_id',
    'dob', 'birth_date', 'birthdate', 'date_of_birth',
    'driver', 'license', 'passport',
    'account', 'credit_card', 'bank',
    'latitude', 'longitude', 'lat', 'lon', 'geo', 'coordinates',
    'ip_address', 'ip_addr', 'ipaddress'
]


def compute_file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"


def is_pii_column(col_name: str) -> bool:
    """Check if column name matches PII patterns."""
    col_lower = col_name.lower().replace('_', '').replace('-', '')
    return any(pattern.replace('_', '') in col_lower for pattern in PII_PATTERNS)


def infer_schema_csv(filepath: Path, sample_size: int = 100000) -> Tuple[pd.DataFrame, Dict, int, float]:
    """Profile CSV/TSV file."""
    try:
        # Detect separator
        sep = '\t' if filepath.suffix.lower() == '.tsv' else ','
        
        # Read sample to infer schema
        df_sample = pd.read_csv(filepath, sep=sep, nrows=sample_size, low_memory=False)
        
        # Try to get total row count efficiently
        try:
            total_rows = sum(1 for _ in open(filepath, 'r', encoding='utf-8', errors='ignore')) - 1
        except:
            total_rows = len(df_sample)
        
        sample_percent = min(100.0, (len(df_sample) / max(total_rows, 1)) * 100)
        
        # Profile each column
        schema = {}
        for col in df_sample.columns:
            col_data = df_sample[col]
            schema[col] = {
                'dtype': str(col_data.dtype),
                'missing_pct': (col_data.isna().sum() / len(col_data)) * 100,
                'n_unique': min(col_data.nunique(), 200),
                'top_5': [],
                'min': None,
                'max': None,
                'is_pii': is_pii_column(col)
            }
            
            # Categorical top 5
            if col_data.dtype == 'object' or col_data.nunique() < 20:
                try:
                    top_vals = col_data.value_counts().head(5).index.tolist()
                    schema[col]['top_5'] = [str(v)[:50] for v in top_vals]
                except:
                    pass
            
            # Numeric min/max
            if pd.api.types.is_numeric_dtype(col_data):
                try:
                    schema[col]['min'] = float(col_data.min())
                    schema[col]['max'] = float(col_data.max())
                except:
                    pass
        
        return df_sample, schema, total_rows, sample_percent
    
    except Exception as e:
        print(f"  ERROR reading CSV {filepath.name}: {e}")
        return None, {}, 0, 0.0


def infer_schema_json(filepath: Path, sample_size: int = 1000) -> Tuple[Any, Dict, int, float]:
    """Profile JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            total_rows = len(data)
            sample_data = data[:sample_size]
            sample_percent = min(100.0, (len(sample_data) / max(total_rows, 1)) * 100)
            
            # Convert to DataFrame for profiling
            df = pd.DataFrame(sample_data)
            schema = {}
            
            for col in df.columns:
                col_data = df[col]
                schema[col] = {
                    'dtype': str(col_data.dtype),
                    'missing_pct': (col_data.isna().sum() / len(col_data)) * 100,
                    'n_unique': min(col_data.nunique(), 200),
                    'top_5': [],
                    'min': None,
                    'max': None,
                    'is_pii': is_pii_column(col)
                }
        
        elif isinstance(data, dict):
            # Single record or nested structure
            total_rows = 1
            sample_percent = 100.0
            schema = {}
            
            def flatten_keys(d, parent_key=''):
                """Recursively get all keys from nested dict."""
                keys = []
                for k, v in d.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        keys.extend(flatten_keys(v, new_key))
                    else:
                        keys.append(new_key)
                return keys
            
            all_keys = flatten_keys(data)
            for key in all_keys[:100]:  # Limit to first 100 keys
                schema[key] = {
                    'dtype': 'object',
                    'missing_pct': 0.0,
                    'n_unique': 1,
                    'top_5': [],
                    'min': None,
                    'max': None,
                    'is_pii': is_pii_column(key)
                }
        else:
            total_rows = 1
            sample_percent = 100.0
            schema = {}
        
        return data, schema, total_rows, sample_percent
    
    except Exception as e:
        print(f"  ERROR reading JSON {filepath.name}: {e}")
        return None, {}, 0, 0.0


def infer_schema_xpt(filepath: Path, sample_size: int = 100000) -> Tuple[pd.DataFrame, Dict, int, float]:
    """Profile SAS XPT file."""
    try:
        # Read XPT file
        df_sample = pd.read_sas(filepath, format='xport', chunksize=None)
        
        if isinstance(df_sample, pd.DataFrame):
            total_rows = len(df_sample)
            sample_percent = 100.0
            
            if total_rows > sample_size:
                df_sample = df_sample.head(sample_size)
                sample_percent = (sample_size / total_rows) * 100
            
            # Profile each column
            schema = {}
            for col in df_sample.columns:
                col_data = df_sample[col]
                schema[col] = {
                    'dtype': str(col_data.dtype),
                    'missing_pct': (col_data.isna().sum() / len(col_data)) * 100,
                    'n_unique': min(col_data.nunique(), 200),
                    'top_5': [],
                    'min': None,
                    'max': None,
                    'is_pii': is_pii_column(col)
                }
                
                # Categorical top 5
                if col_data.dtype == 'object' or col_data.nunique() < 20:
                    try:
                        top_vals = col_data.value_counts().head(5).index.tolist()
                        schema[col]['top_5'] = [str(v)[:50] for v in top_vals]
                    except:
                        pass
                
                # Numeric min/max
                if pd.api.types.is_numeric_dtype(col_data):
                    try:
                        schema[col]['min'] = float(col_data.min())
                        schema[col]['max'] = float(col_data.max())
                    except:
                        pass
            
            return df_sample, schema, total_rows, sample_percent
        else:
            return None, {}, 0, 0.0
    
    except Exception as e:
        print(f"  ERROR reading XPT {filepath.name}: {e}")
        return None, {}, 0, 0.0


def infer_schema_parquet(filepath: Path, sample_size: int = 100000) -> Tuple[pd.DataFrame, Dict, int, float]:
    """Profile Parquet file."""
    try:
        # Read parquet metadata first
        import pyarrow.parquet as pq
        parquet_file = pq.ParquetFile(filepath)
        total_rows = parquet_file.metadata.num_rows
        
        # Read sample
        df_sample = pd.read_parquet(filepath)
        
        if total_rows > sample_size:
            df_sample = df_sample.head(sample_size)
            sample_percent = (sample_size / total_rows) * 100
        else:
            sample_percent = 100.0
        
        # Profile each column
        schema = {}
        for col in df_sample.columns:
            col_data = df_sample[col]
            schema[col] = {
                'dtype': str(col_data.dtype),
                'missing_pct': (col_data.isna().sum() / len(col_data)) * 100,
                'n_unique': min(col_data.nunique(), 200),
                'top_5': [],
                'min': None,
                'max': None,
                'is_pii': is_pii_column(col)
            }
            
            # Categorical top 5
            if col_data.dtype == 'object' or col_data.nunique() < 20:
                try:
                    top_vals = col_data.value_counts().head(5).index.tolist()
                    schema[col]['top_5'] = [str(v)[:50] for v in top_vals]
                except:
                    pass
            
            # Numeric min/max
            if pd.api.types.is_numeric_dtype(col_data):
                try:
                    schema[col]['min'] = float(col_data.min())
                    schema[col]['max'] = float(col_data.max())
                except:
                    pass
        
        return df_sample, schema, total_rows, sample_percent
    
    except Exception as e:
        print(f"  ERROR reading Parquet {filepath.name}: {e}")
        return None, {}, 0, 0.0


def guess_source_from_path(filepath: Path) -> str:
    """Guess data source from file path."""
    path_str = str(filepath).lower()
    if 'synthea' in path_str:
        return 'synthea'
    elif 'nhanes' in path_str:
        return 'nhanes'
    elif 'vdh' in path_str or 'virginia' in path_str:
        return 'vdh'
    elif 'nih' in path_str or 'xray' in path_str:
        return 'nih'
    else:
        return 'other'


def guess_license(source: str) -> str:
    """Guess license based on source."""
    licenses = {
        'synthea': 'Apache-2.0',
        'nhanes': 'Public Domain (US Govt)',
        'vdh': 'Open Data (varies)',
        'nih': 'CC0 / Public Domain',
        'other': 'unknown'
    }
    return licenses.get(source, 'unknown')


def is_synthetic(source: str, filepath: Path) -> bool:
    """Determine if data is synthetic."""
    if source == 'synthea':
        return True
    if 'synthetic' in str(filepath).lower() or 'mock' in str(filepath).lower():
        return True
    return False


def profile_all_data_files():
    """Main profiling function."""
    print("=" * 80)
    print("DATA PROFILER - Non-Destructive Analysis")
    print("=" * 80)
    
    workspace = Path.cwd()
    data_roots = [
        workspace / 'data' / 'raw',
        workspace / 'data' / 'interim'
    ]
    
    manifest_records = []
    schema_profiles = []
    
    total_files = 0
    total_rows_approx = 0
    large_files = []
    total_pii_columns = 0
    
    # File extensions to process
    extensions = ['.csv', '.tsv', '.json', '.parquet', '.xpt', '.xlsx']
    
    for root_dir in data_roots:
        if not root_dir.exists():
            print(f"\nSkipping {root_dir} (not found)")
            continue
        
        print(f"\n{'=' * 80}")
        print(f"Processing: {root_dir}")
        print(f"{'=' * 80}")
        
        # Find all data files
        data_files = []
        for ext in extensions:
            data_files.extend(root_dir.rglob(f'*{ext}'))
        
        data_files = sorted(data_files)
        
        if not data_files:
            print(f"  No data files found in {root_dir}")
            continue
        
        print(f"Found {len(data_files)} data files")
        
        for filepath in data_files:
            total_files += 1
            print(f"\n[{total_files}] {filepath.relative_to(workspace)}")
            
            # Get file size
            size_bytes = filepath.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            if size_mb > 200:
                large_files.append((str(filepath.relative_to(workspace)), size_mb))
            
            print(f"  Size: {size_mb:.2f} MB")
            
            # Compute hash
            print(f"  Computing SHA256...")
            file_hash = compute_file_hash(filepath)
            
            # Profile based on file type
            data = None
            schema = {}
            row_count = 0
            sample_percent = 0.0
            
            ext = filepath.suffix.lower()
            
            if ext in ['.csv', '.tsv']:
                data, schema, row_count, sample_percent = infer_schema_csv(filepath)
            elif ext == '.json':
                data, schema, row_count, sample_percent = infer_schema_json(filepath)
            elif ext == '.xpt':
                data, schema, row_count, sample_percent = infer_schema_xpt(filepath)
            elif ext == '.parquet':
                data, schema, row_count, sample_percent = infer_schema_parquet(filepath)
            else:
                print(f"  Skipping unsupported format: {ext}")
                continue
            
            print(f"  Rows: {row_count:,} (sampled {sample_percent:.1f}%)")
            print(f"  Columns: {len(schema)}")
            
            total_rows_approx += row_count
            
            # Count PII columns
            pii_cols = [col for col, info in schema.items() if info['is_pii']]
            total_pii_columns += len(pii_cols)
            
            if pii_cols:
                print(f"  PII-like columns: {len(pii_cols)}")
            
            # Guess metadata
            source_guess = guess_source_from_path(filepath)
            license_guess = guess_license(source_guess)
            is_synthetic_guess = is_synthetic(source_guess, filepath)
            
            # Add to manifest
            manifest_records.append({
                'file_path': str(filepath.relative_to(workspace)),
                'size_bytes': size_bytes,
                'sha256_full': file_hash,
                'row_count': row_count,
                'sample_percent': round(sample_percent, 2),
                'source_guess': source_guess,
                'license_guess': license_guess,
                'is_synthetic_guess': is_synthetic_guess
            })
            
            # Add to schema profile
            schema_profiles.append({
                'filepath': filepath.relative_to(workspace),
                'schema': schema,
                'row_count': row_count,
                'pii_columns': pii_cols
            })
    
    # Write manifest CSV
    print(f"\n{'=' * 80}")
    print("Writing reports...")
    print(f"{'=' * 80}")
    
    reports_dir = workspace / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    manifest_df = pd.DataFrame(manifest_records)
    manifest_path = reports_dir / 'data_manifest.csv'
    manifest_df.to_csv(manifest_path, index=False)
    print(f"✓ Manifest written: {manifest_path}")
    
    # Write schema profile markdown
    schema_path = reports_dir / 'schema_profile.md'
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write("# Data Schema Profile\n\n")
        f.write(f"**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Files**: {total_files}\n\n")
        f.write(f"**Total Rows (approx)**: {total_rows_approx:,}\n\n")
        f.write("---\n\n")
        
        for profile in schema_profiles:
            f.write(f"## {profile['filepath']}\n\n")
            f.write(f"**Rows**: {profile['row_count']:,}\n\n")
            f.write(f"**Columns**: {len(profile['schema'])}\n\n")
            
            if profile['pii_columns']:
                f.write(f"**⚠️ PII-like Columns Detected**: {', '.join(f'`{c}`' for c in profile['pii_columns'])}\n\n")
            
            # Schema table
            if profile['schema']:
                f.write("| Column | Type | Missing % | Unique | Top 5 Categories | Min | Max |\n")
                f.write("|--------|------|-----------|--------|------------------|-----|-----|\n")
                
                for col, info in profile['schema'].items():
                    pii_marker = "🔒" if info['is_pii'] else ""
                    col_name = f"{pii_marker} {col}" if pii_marker else col
                    
                    top_5_str = ', '.join(str(v) for v in info['top_5'][:5]) if info['top_5'] else '—'
                    if len(top_5_str) > 50:
                        top_5_str = top_5_str[:47] + '...'
                    
                    min_val = f"{info['min']:.2f}" if info['min'] is not None else '—'
                    max_val = f"{info['max']:.2f}" if info['max'] is not None else '—'
                    
                    f.write(f"| `{col_name}` | {info['dtype']} | {info['missing_pct']:.1f}% | "
                           f"{info['n_unique']} | {top_5_str} | {min_val} | {max_val} |\n")
                
                f.write("\n")
            
            f.write("---\n\n")
    
    print(f"✓ Schema profile written: {schema_path}")
    
    # Print summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total files processed: {total_files}")
    print(f"Total rows (approx): {total_rows_approx:,}")
    print(f"Total PII-like columns flagged: {total_pii_columns}")
    
    if large_files:
        print(f"\nFiles > 200 MB:")
        for fpath, size in large_files:
            print(f"  - {fpath}: {size:.2f} MB")
    else:
        print(f"\nNo files > 200 MB")
    
    print(f"\n{'=' * 80}")
    print("✓ Profiling complete!")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    profile_all_data_files()
