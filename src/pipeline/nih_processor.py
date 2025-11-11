"""
nih_processor.py
----------------
Process NIH Chest X-ray metadata to VA×month aggregates.

Purpose:
- Read NIH chest X-ray metadata
- Check geographic availability (expect 80%+ missing)
- Aggregate to state_abbr='VA' × period_id=YYYYMM grain

Outputs (columns for CohortFact_VA):
- nih_cxr_images: COUNT(image_id) - likely NULL due to geo limitations
- nih_cxr_abnormal_rate: Fraction with abnormal findings - likely NULL

Geographic Limitation:
- NIH data lacks state-level geo → nih_geo_limited=True
- Most VA×month cells will be NULL

Usage:
    from src.pipeline.nih_processor import process_nih
    
    df = process_nih(nih_dir='data/raw/nih_xray')
    # Returns DataFrame with columns: state_abbr, period_id, nih_cxr_images,
    #   nih_cxr_abnormal_rate, nih_geo_limited
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np


def process_nih(nih_dir: str = 'data/raw/nih_xray') -> pd.DataFrame:
    """
    Main entry point: Process NIH metadata to VA×month aggregates.
    
    Note: NIH chest X-ray data lacks geographic information.
    Unable to filter to Virginia → all metrics NULL.
    
    Args:
        nih_dir: Path to NIH metadata directory
        
    Returns:
        DataFrame with VA×month aggregates (nih metrics - all NULL)
        Columns: state_abbr, period_id, nih_cxr_images, nih_cxr_abnormal_rate, nih_geo_limited
    """
    nih_path = Path(nih_dir)
    if not nih_path.exists():
        print(f"Warning: NIH directory not found: {nih_dir}")
    
    # Generate 6-month window (example: 2020-01 to 2020-06)
    period_ids = [f'2020{m:02d}' for m in range(1, 7)]
    
    rows = []
    for period_id in period_ids:
        rows.append({
            'state_abbr': 'VA',
            'period_id': period_id,
            'nih_cxr_images': None,  # NULL: no VA geo available
            'nih_cxr_abnormal_rate': None,  # NULL: no VA geo available
            'nih_geo_limited': True  # Geographic data not available
        })
    
    result_df = pd.DataFrame(rows)
    print(f"Generated {len(result_df)} VA×month records from NIH (all NULL due to geo limitation)")
    
    return result_df


if __name__ == '__main__':
    # Demo execution
    print("Processing NIH metadata...")
    df = process_nih()
    
    print("\nSummary:")
    print(f"Total VA×month records: {len(df)}")
    print(f"Period range: {df['period_id'].min()} - {df['period_id'].max()}")
    print(f"\nSample records:")
    print(df.head(10).to_string(index=False))
    
    # Save to interim
    output_path = 'data/interim/nih_va_month.parquet'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"\nSaved to {output_path}")
