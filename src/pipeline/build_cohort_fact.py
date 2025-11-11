"""
build_cohort_fact.py
--------------------
Build final CohortFact_VA table by joining all source aggregates.

Purpose:
- Join Synthea, NHANES, VDH, NIH aggregates on state_abbr='VA' × period_id=YYYYMM
- Produce final table with all 9 metrics + 3 validation flags
- Apply metadata (provenance, timestamps)

Output Schema (CohortFact_VA):
- state_abbr: 'VA' (primary key part 1)
- period_id: YYYYMM (primary key part 2)
- synthea_encounters: INT
- synthea_dx_rate: FLOAT [per 1k encounters]
- synthea_lab_oob_rate: FLOAT [0-1]
- vdh_case_rate_per_100k: FLOAT
- vdh_hosp_rate_per_100k: FLOAT
- nhanes_obesity_rate: FLOAT [0-1]
- nhanes_smoking_rate: FLOAT [0-1]
- nih_cxr_images: INT (nullable)
- nih_cxr_abnormal_rate: FLOAT [0-1] (nullable)
- low_precision_time: BOOLEAN
- ambiguous_geo: BOOLEAN
- nih_geo_limited: BOOLEAN
- provenance_timestamp: TIMESTAMP
- provenance_sources: STRING (comma-separated)

Usage:
    from src.pipeline.build_cohort_fact import build_cohort_fact
    
    df = build_cohort_fact(
        synthea_path='data/interim/synthea_va_month.parquet',
        nhanes_path='data/interim/nhanes_va_month.parquet',
        vdh_path='data/interim/vdh_va_month.parquet',
        nih_path='data/interim/nih_va_month.parquet'
    )
"""

import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np


def build_cohort_fact(
    synthea_path: str = 'data/interim/synthea_va_month.parquet',
    nhanes_path: str = 'data/interim/nhanes_va_month.parquet',
    vdh_path: str = 'data/interim/vdh_va_month.parquet',
    nih_path: str = 'data/interim/nih_va_month.parquet',
    output_path: str = 'data/processed/cohort_fact_va.parquet'
) -> pd.DataFrame:
    """
    Build final CohortFact_VA table from source aggregates.
    
    Args:
        synthea_path: Path to Synthea VA×month aggregates
        nhanes_path: Path to NHANES VA×month aggregates
        vdh_path: Path to VDH VA×month aggregates
        nih_path: Path to NIH VA×month aggregates
        output_path: Path to save final table
        
    Returns:
        DataFrame with CohortFact_VA schema
    """
    print("Building CohortFact_VA table...")
    
    # Load source aggregates
    print(f"Loading Synthea data from {synthea_path}...")
    synthea_df = pd.read_parquet(synthea_path) if Path(synthea_path).exists() else None
    
    print(f"Loading NHANES data from {nhanes_path}...")
    nhanes_df = pd.read_parquet(nhanes_path) if Path(nhanes_path).exists() else None
    
    print(f"Loading VDH data from {vdh_path}...")
    vdh_df = pd.read_parquet(vdh_path) if Path(vdh_path).exists() else None
    
    print(f"Loading NIH data from {nih_path}...")
    nih_df = pd.read_parquet(nih_path) if Path(nih_path).exists() else None
    
    # Determine all period_ids (union across sources)
    all_period_ids = set()
    for df in [synthea_df, nhanes_df, vdh_df, nih_df]:
        if df is not None:
            all_period_ids.update(df['period_id'].unique())
    
    if not all_period_ids:
        raise ValueError("No data found in any source files")
    
    print(f"Found {len(all_period_ids)} unique period_ids across sources")
    
    # Create base DataFrame with all period_ids
    base_df = pd.DataFrame({
        'state_abbr': 'VA',
        'period_id': sorted(list(all_period_ids))
    })
    
    # Join Synthea metrics
    if synthea_df is not None:
        synthea_cols = ['state_abbr', 'period_id', 'synthea_encounters', 
                        'synthea_dx_rate', 'synthea_lab_oob_rate']
        base_df = base_df.merge(
            synthea_df[synthea_cols], 
            on=['state_abbr', 'period_id'], 
            how='left'
        )
    else:
        base_df['synthea_encounters'] = None
        base_df['synthea_dx_rate'] = None
        base_df['synthea_lab_oob_rate'] = None
    
    # Join NHANES metrics
    if nhanes_df is not None:
        nhanes_cols = ['state_abbr', 'period_id', 'nhanes_obesity_rate', 'nhanes_smoking_rate']
        base_df = base_df.merge(
            nhanes_df[nhanes_cols], 
            on=['state_abbr', 'period_id'], 
            how='left'
        )
    else:
        base_df['nhanes_obesity_rate'] = None
        base_df['nhanes_smoking_rate'] = None
    
    # Join VDH metrics
    if vdh_df is not None:
        vdh_cols = ['state_abbr', 'period_id', 'vdh_case_rate_per_100k', 'vdh_hosp_rate_per_100k']
        base_df = base_df.merge(
            vdh_df[vdh_cols], 
            on=['state_abbr', 'period_id'], 
            how='left'
        )
    else:
        base_df['vdh_case_rate_per_100k'] = None
        base_df['vdh_hosp_rate_per_100k'] = None
    
    # Join NIH metrics
    if nih_df is not None:
        nih_cols = ['state_abbr', 'period_id', 'nih_cxr_images', 'nih_cxr_abnormal_rate']
        base_df = base_df.merge(
            nih_df[nih_cols], 
            on=['state_abbr', 'period_id'], 
            how='left'
        )
    else:
        base_df['nih_cxr_images'] = None
        base_df['nih_cxr_abnormal_rate'] = None
    
    # Add validation flags
    # low_precision_time: True if VDH present (monthly precision)
    base_df['low_precision_time'] = False
    if vdh_df is not None:
        vdh_periods = set(vdh_df['period_id'])
        base_df['low_precision_time'] = base_df['period_id'].isin(vdh_periods)
    
    # ambiguous_geo: True if NHANES present (no VA-specific geo)
    base_df['ambiguous_geo'] = False
    if nhanes_df is not None:
        nhanes_periods = set(nhanes_df['period_id'])
        base_df['ambiguous_geo'] = base_df['period_id'].isin(nhanes_periods)
    
    # nih_geo_limited: Always True for all periods
    base_df['nih_geo_limited'] = True
    
    # Add provenance metadata
    base_df['provenance_timestamp'] = datetime.utcnow().isoformat()
    
    # Provenance sources
    sources = []
    if synthea_df is not None:
        sources.append('Synthea')
    if nhanes_df is not None:
        sources.append('NHANES')
    if vdh_df is not None:
        sources.append('VDH')
    if nih_df is not None:
        sources.append('NIH')
    base_df['provenance_sources'] = ','.join(sources)
    
    # Reorder columns
    final_cols = [
        'state_abbr', 'period_id',
        'synthea_encounters', 'synthea_dx_rate', 'synthea_lab_oob_rate',
        'vdh_case_rate_per_100k', 'vdh_hosp_rate_per_100k',
        'nhanes_obesity_rate', 'nhanes_smoking_rate',
        'nih_cxr_images', 'nih_cxr_abnormal_rate',
        'low_precision_time', 'ambiguous_geo', 'nih_geo_limited',
        'provenance_timestamp', 'provenance_sources'
    ]
    
    result_df = base_df[final_cols]
    
    # Save to processed/
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_parquet(output_path, index=False)
    print(f"\nSaved CohortFact_VA to {output_path}")
    
    print(f"\nCohortFact_VA Summary:")
    print(f"  Total rows: {len(result_df)}")
    print(f"  Period range: {result_df['period_id'].min()} to {result_df['period_id'].max()}")
    print(f"  Columns: {len(result_df.columns)}")
    
    return result_df


if __name__ == '__main__':
    # Demo execution
    df = build_cohort_fact()
    
    print("\nSample records:")
    print(df.head(10).to_string(index=False))
    
    print("\nColumn NA percentages:")
    na_pct = (df.isna().sum() / len(df) * 100).sort_values(ascending=False)
    print(na_pct.to_string())
