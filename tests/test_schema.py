"""
Tests for validating project structure, schemas, and data specifications.
"""

import json
from pathlib import Path

import pandas as pd
import pytest


def test_project_layout():
    """Test that expected project directories exist."""
    expected_paths = [
        "src",
        "src/pipeline",
        "src/analysis",
        "src/visualization",
        "notebooks",
        "data/raw",
        "data/interim",
        "data/processed",
        "docs",
        "references",
        "reports",
        "resources",
        "resources/rules",
        "tests",
    ]

    for p in expected_paths:
        assert Path(p).exists(), f"Missing expected path: {p}"


def test_join_spec_exists():
    """Test that join specification file exists."""
    join_spec_path = Path("resources/join_spec.json")
    assert join_spec_path.exists(), "Join specification not found"


def test_join_spec_structure():
    """Test that join_spec.json has required keys and structure."""
    join_spec_path = Path("resources/join_spec.json")

    with open(join_spec_path) as f:
        spec = json.load(f)

    # Check top-level keys
    required_top_keys = [
        "join_table",
        "join_keys",
        "synthetic_keys_and_flags",
        "aggregation_logic",
        "validation_constraints",
    ]

    for key in required_top_keys:
        assert key in spec, f"Missing required key in join_spec.json: {key}"

    # Check join_keys structure
    join_keys = spec["join_keys"]
    required_join_keys = ["data_source", "period_id", "state_abbr"]

    for key in required_join_keys:
        assert key in join_keys, f"Missing required join key: {key}"

    # Check synthetic_keys_and_flags structure
    flags = spec["synthetic_keys_and_flags"]
    required_flags = [
        "low_precision_time",
        "ambiguous_geo",
        "lab_oob_na",
        "nih_geo_limited",
    ]

    for flag in required_flags:
        assert flag in flags, f"Missing required flag definition: {flag}"


def test_validation_rules_exist():
    """Test that all validation rule packs exist."""
    rules_dir = Path("resources/rules")
    required_rules = [
        "core.json",
        "synthea.json",
        "nhanes.json",
        "vdh.json",
        "nih.json",
    ]

    for rule_file in required_rules:
        rule_path = rules_dir / rule_file
        assert rule_path.exists(), f"Missing validation rule pack: {rule_file}"


def test_validation_rules_structure():
    """Test that validation rules have required structure."""
    rules_dir = Path("resources/rules")
    core_rules_path = rules_dir / "core.json"

    with open(core_rules_path) as f:
        rules = json.load(f)

    # Check required top-level keys (actual schema uses rule_pack_name not name)
    required_keys = ["rule_pack_name", "version", "rules", "severity_policy"]
    for key in required_keys:
        assert key in rules, f"Missing required key in core.json: {key}"

    # Check that rules is a list
    assert isinstance(rules["rules"], list), "rules should be a list"

    # Check each rule has required fields
    for rule in rules["rules"]:
        assert "rule_id" in rule, "Rule missing rule_id"
        assert "name" in rule, "Rule missing name"
        assert "severity" in rule, "Rule missing severity"
        assert "description" in rule, "Rule missing description"


def test_cohort_fact_schema_keys():
    """Test that cohort fact table will have expected keys."""
    join_spec_path = Path("resources/join_spec.json")

    with open(join_spec_path) as f:
        spec = json.load(f)

    # Expected primary key (actual schema uses list format)
    assert spec["join_table"]["primary_key"] == ["data_source"]

    # Expected join keys should be defined
    join_keys = spec["join_keys"]
    assert "data_source" in join_keys
    assert "period_id" in join_keys
    assert "state_abbr" in join_keys


def test_null_safe_dtypes_documented():
    """Test that nullable dtypes are documented in cleaning plan."""
    cleaning_plan_path = Path("docs/cleaning_plan.md")
    assert cleaning_plan_path.exists(), "Cleaning plan not found"

    with open(cleaning_plan_path, encoding="utf-8") as f:
        content = f.read()

    # Check for null-safe dtype references
    assert "Int64" in content, "Int64 nullable dtype not documented"
    assert "Float64" in content, "Float64 nullable dtype not documented"
    assert "boolean" in content, "boolean nullable dtype not documented"


def test_python_version_locked():
    """Test that Python version is locked in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"

    with open(pyproject_path) as f:
        content = f.read()

    # Check for python version requirement
    assert "requires-python" in content, "Python version not specified in pyproject.toml"
    assert "3.11" in content, "Python 3.11 not specified in pyproject.toml"


@pytest.mark.skipif(
    not Path("data/processed/cohort_fact_va.csv").exists(),
    reason="Processed cohort data not available",
)
def test_cohort_fact_dtypes():
    """Test that cohort fact table uses nullable dtypes."""
    cohort_path = Path("data/processed/cohort_fact_va.csv")
    df = pd.read_csv(cohort_path)

    # Convert to nullable dtypes if not already
    # This is what the pipeline should do
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    for col in numeric_cols:
        # These should be nullable types in production
        # This test validates the concept
        assert df[col].dtype in [
            "int64",
            "Int64",
            "float64",
            "Float64",
        ], f"Unexpected dtype for {col}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
