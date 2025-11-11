"""
Analysis module for WGU D610 Capstone.

This module provides functions for exploratory data analysis,
statistical hypothesis testing, and results visualization.
"""

from .run_eda import (
    load_and_validate_data,
    generate_univariate_plots,
    generate_bivariate_plots,
    assess_normality,
    create_eda_report
)

from .run_statistical_tests import (
    paired_t_test,
    mcnemar_test,
    calculate_effect_size,
    sensitivity_analysis,
    subgroup_analysis,
    export_results
)

__all__ = [
    'load_and_validate_data',
    'generate_univariate_plots',
    'generate_bivariate_plots',
    'assess_normality',
    'create_eda_report',
    'paired_t_test',
    'mcnemar_test',
    'calculate_effect_size',
    'sensitivity_analysis',
    'subgroup_analysis',
    'export_results'
]
