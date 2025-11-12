"""
test_cohort_fact_validation.py
-------------------------------
Acceptance tests for CohortFact_VA table.

Tests (from metrics_spec.md):
1. Uniqueness: PRIMARY KEY(state_abbr, period_id) has no duplicates
2. Coverage: All expected period_ids present in contiguous range
3. Bounds: All metrics within expected ranges
4. Consistency: Validation flags logically consistent
5. Flag Consistency: Flag combinations valid

Usage:
    pytest tests/test_cohort_fact_validation.py
"""

import pandas as pd
import pytest
from pathlib import Path


# Expected data ranges from metrics_spec.md
METRIC_BOUNDS = {
    'synthea_encounters': (0, None),  # Non-negative integer
    'synthea_dx_rate': (0, None),  # Non-negative per 1k
    'synthea_lab_oob_rate': (0, 1),  # Fraction 0-1
    'vdh_case_rate_per_100k': (0, None),  # Non-negative per 100k
    'vdh_hosp_rate_per_100k': (0, None),  # Non-negative per 100k
    'nhanes_obesity_rate': (0, 1),  # Fraction 0-1
    'nhanes_smoking_rate': (0, 1),  # Fraction 0-1
    'nih_cxr_images': (0, None),  # Non-negative integer (nullable)
    'nih_cxr_abnormal_rate': (0, 1),  # Fraction 0-1 (nullable)
}


@pytest.fixture
def cohort_fact_df():
    """Load CohortFact_VA table for testing."""
    path = Path('data/processed/cohort_fact_va.parquet')
    if not path.exists():
        pytest.skip(f"CohortFact_VA file not found: {path}")
    
    return pd.read_parquet(path)


class TestUniqueness:
    """Test 1: PRIMARY KEY(state_abbr, period_id) uniqueness."""
    
    def test_no_duplicate_keys(self, cohort_fact_df):
        """Assert no duplicate (state_abbr, period_id) combinations."""
        duplicates = cohort_fact_df.duplicated(subset=['state_abbr', 'period_id'])
        
        assert not duplicates.any(), \
            f"Found {duplicates.sum()} duplicate keys:\n{cohort_fact_df[duplicates]}"
    
    def test_state_abbr_is_VA(self, cohort_fact_df):
        """Assert all rows have state_abbr='VA'."""
        assert (cohort_fact_df['state_abbr'] == 'VA').all(), \
            "Some rows have state_abbr != 'VA'"


class TestCoverage:
    """Test 2: Contiguous period_id coverage."""
    
    def test_contiguous_period_range(self, cohort_fact_df):
        """Assert period_ids form contiguous range (no gaps)."""
        period_ids = sorted(cohort_fact_df['period_id'].unique())
        
        # Convert YYYYMM to datetime
        dates = pd.to_datetime(period_ids, format='%Y%m')
        
        # Check for gaps > 1 month
        gaps = dates[1:] - dates[:-1]
        max_gap = gaps.max()
        
        assert max_gap <= pd.Timedelta(days=31), \
            f"Gap of {max_gap} found in period_ids"
    
    def test_minimum_coverage(self, cohort_fact_df):
        """Assert at least 6 months of data (per mitigation playbook)."""
        assert len(cohort_fact_df) >= 6, \
            f"Expected >= 6 months, got {len(cohort_fact_df)}"


class TestBounds:
    """Test 3: Metric values within expected bounds."""
    
    @pytest.mark.parametrize("metric,bounds", METRIC_BOUNDS.items())
    def test_metric_bounds(self, cohort_fact_df, metric, bounds):
        """Assert metric values within expected range."""
        low, high = bounds
        
        # Get non-null values
        values = cohort_fact_df[metric].dropna()
        
        if values.empty:
            pytest.skip(f"No non-null values for {metric}")
        
        # Check lower bound
        if low is not None:
            min_val = values.min()
            assert min_val >= low, \
                f"{metric} minimum {min_val} < lower bound {low}"
        
        # Check upper bound
        if high is not None:
            max_val = values.max()
            assert max_val <= high, \
                f"{metric} maximum {max_val} > upper bound {high}"


class TestConsistency:
    """Test 4: Logical consistency of metrics and flags."""
    
    def test_flag_types(self, cohort_fact_df):
        """Assert validation flags are boolean."""
        for flag in ['low_precision_time', 'ambiguous_geo', 'nih_geo_limited']:
            assert cohort_fact_df[flag].dtype == bool, \
                f"{flag} should be boolean, got {cohort_fact_df[flag].dtype}"
    
    def test_nih_geo_limited_always_true(self, cohort_fact_df):
        """Assert nih_geo_limited is True for all rows (NIH has no VA geo)."""
        assert cohort_fact_df['nih_geo_limited'].all(), \
            "Some rows have nih_geo_limited=False (should always be True)"
    
    def test_nih_metrics_mostly_null(self, cohort_fact_df):
        """Assert NIH metrics are mostly NULL (due to geo limitation)."""
        nih_null_rate = cohort_fact_df['nih_cxr_images'].isna().mean()
        
        assert nih_null_rate >= 0.8, \
            f"NIH metrics should be >=80% NULL, got {nih_null_rate:.1%}"


class TestFlagConsistency:
    """Test 5: Validation flag combinations are valid."""
    
    def test_provenance_sources_not_empty(self, cohort_fact_df):
        """Assert provenance_sources is non-empty for all rows."""
        assert cohort_fact_df['provenance_sources'].str.len().min() > 0, \
            "Some rows have empty provenance_sources"
    
    def test_provenance_timestamp_present(self, cohort_fact_df):
        """Assert provenance_timestamp is present for all rows."""
        assert cohort_fact_df['provenance_timestamp'].notna().all(), \
            "Some rows missing provenance_timestamp"


if __name__ == '__main__':
    # Run tests standalone
    pytest.main([__file__, '-v'])
