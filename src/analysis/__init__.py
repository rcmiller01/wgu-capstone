"""
Analysis module for health data lake.

This module provides functions for exploratory data analysis,
statistical hypothesis testing, and results visualization.
"""

from .run_eda import (
    assess_normality,
    create_eda_report,
    generate_bivariate_plots,
    generate_univariate_plots,
    load_and_validate_data,
)
from .run_statistical_tests import (
    calculate_effect_size,
    export_results,
    mcnemar_test,
    paired_t_test,
    sensitivity_analysis,
    subgroup_analysis,
)

__all__ = [
    "load_and_validate_data",
    "generate_univariate_plots",
    "generate_bivariate_plots",
    "assess_normality",
    "create_eda_report",
    "paired_t_test",
    "mcnemar_test",
    "calculate_effect_size",
    "sensitivity_analysis",
    "subgroup_analysis",
    "export_results",
]
