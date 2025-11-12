"""
Tests for validating statistical assumptions and data integrity.

These tests serve as smoke tests to ensure:
1. Data exists and is accessible
2. Required columns are present
3. No missing outcome variables
4. Data values are in expected ranges
5. Sample size meets requirements
6. Normality assumptions (when applicable)
"""

from pathlib import Path

import pandas as pd
import pytest
from scipy import stats


@pytest.fixture
def processed_data():
    """Load processed data for testing."""
    data_path = Path("data/processed/processed_data.parquet")

    if not data_path.exists():
        pytest.skip("Processed data not available - run data pipeline first")

    return pd.read_parquet(data_path)


def test_data_exists():
    """Test that processed data file exists."""
    data_path = Path("data/processed/processed_data.parquet")
    assert data_path.exists(), "Processed data file not found"


def test_required_columns(processed_data):
    """Test that all required columns are present."""
    required_columns = ["latency_sec", "file_size_kb", "data_source", "validation_passed"]

    for col in required_columns:
        assert col in processed_data.columns, f"Missing required column: {col}"


def test_no_missing_outcomes(processed_data):
    """Test that outcome variables have no missing values."""
    outcome_vars = ["latency_sec", "validation_passed"]

    for var in outcome_vars:
        missing_count = processed_data[var].isna().sum()
        assert missing_count == 0, f"{var} has {missing_count} missing values"


def test_latency_range(processed_data):
    """Test that latency values are within reasonable range."""
    latency = processed_data["latency_sec"]

    # Latency should be positive
    assert (latency > 0).all(), "Found non-positive latency values"

    # Latency should be less than 10 minutes (600 seconds)
    assert (latency < 600).all(), "Found unusually high latency values (>600s)"


def test_validation_boolean(processed_data):
    """Test that validation_passed is boolean."""
    validation = processed_data["validation_passed"]

    # Should only contain True/False
    unique_values = set(validation.unique())
    assert unique_values.issubset(
        {True, False}
    ), f"validation_passed contains non-boolean values: {unique_values}"


def test_sample_size(processed_data):
    """Test that sample size meets minimum requirement."""
    n = len(processed_data)
    min_sample_size = 800

    assert n >= min_sample_size, f"Sample size ({n}) below minimum requirement ({min_sample_size})"


def test_data_sources_present(processed_data):
    """Test that expected data sources are present."""
    expected_sources = ["nhanes", "synthea"]
    actual_sources = set(processed_data["data_source"].unique())

    for source in expected_sources:
        assert source in actual_sources, f"Expected data source '{source}' not found"


def test_normality_assumption(processed_data):
    """
    Test normality assumption for latency (informative, not enforced).

    Note: Paired t-test is robust to moderate departures from normality
    with large sample sizes (n > 30). This test is informative only.
    """
    latency = processed_data["latency_sec"]

    # Sample if too large (Shapiro-Wilk max n=5000)
    if len(latency) > 5000:
        latency_sample = latency.sample(5000, random_state=12345)
    else:
        latency_sample = latency

    # Shapiro-Wilk test
    statistic, p_value = stats.shapiro(latency_sample)

    # Record result (not enforced due to robustness)
    is_normal = p_value > 0.05

    print("\nNormality test (Shapiro-Wilk):")
    print(f"  Statistic: {statistic:.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(
        f"  Result: {'Normal' if is_normal else 'Non-normal'} "
        f"(informative only - t-test robust with n={len(latency)})"
    )


def test_latency_variance(processed_data):
    """Test that latency has reasonable variance (not constant)."""
    latency = processed_data["latency_sec"]

    # Coefficient of variation should be meaningful
    cv = latency.std() / latency.mean()

    assert cv > 0.01, f"Latency variance too low (CV={cv:.4f}) - data may be constant"


def test_file_size_range(processed_data):
    """Test that file sizes are within reasonable range."""
    file_size = processed_data["file_size_kb"]

    # File sizes should be positive
    assert (file_size > 0).all(), "Found non-positive file sizes"

    # File sizes should be less than 10 MB (10240 KB)
    assert (file_size < 10240).all(), "Found unusually large files (>10 MB)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
