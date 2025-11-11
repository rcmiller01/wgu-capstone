"""
Statistical hypothesis testing module.

This module provides functions for executing paired t-tests, McNemar's tests,
effect size calculations, and sensitivity/subgroup analyses.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar
import warnings

warnings.filterwarnings('ignore')


def paired_t_test(
    df: pd.DataFrame,
    manual_baseline: float = 1200.0,
    alpha: float = 0.05
) -> Dict[str, float]:
    """
    Execute paired t-test for latency improvement.
    
    Args:
        df: DataFrame with latency_sec column
        manual_baseline: Manual baseline latency in seconds
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    print("\n" + "=" * 70)
    print("PAIRED T-TEST: LATENCY IMPROVEMENT")
    print("=" * 70)
    
    # Create paired data
    df = df.copy()
    df['manual_latency_est'] = manual_baseline
    df['latency_diff'] = df['manual_latency_est'] - df['latency_sec']
    
    # Two-tailed test
    t_stat, p_value_two_tail = stats.ttest_rel(
        df['manual_latency_est'], 
        df['latency_sec']
    )
    
    # One-tailed test (automated < manual, so diff > 0)
    if t_stat > 0:
        p_value_one_tail = p_value_two_tail / 2
    else:
        p_value_one_tail = 1 - (p_value_two_tail / 2)
    
    # Confidence interval
    ci = stats.t.interval(
        0.95, 
        len(df) - 1, 
        loc=df['latency_diff'].mean(), 
        scale=stats.sem(df['latency_diff'])
    )
    
    # Results
    print(f"Sample Size: {len(df):,}")
    print(f"Manual Baseline: {manual_baseline:.0f} seconds")
    print(f"Automated Mean: {df['latency_sec'].mean():.2f} seconds")
    print(f"Mean Difference: {df['latency_diff'].mean():.2f} seconds")
    print(f"\nt-statistic: {t_stat:.4f}")
    print(f"p-value (one-tailed): {p_value_one_tail:.6f}")
    print(f"95% CI: [{ci[0]:.2f}, {ci[1]:.2f}]")
    
    if p_value_one_tail < alpha:
        print(f"\n✓ REJECT H₀ (p < {alpha})")
        print("  Automated pipeline is significantly faster")
    else:
        print(f"\n❌ FAIL TO REJECT H₀ (p >= {alpha})")
        print("  Insufficient evidence of improvement")
    
    return {
        'sample_size': len(df),
        'manual_baseline_sec': manual_baseline,
        'automated_mean_sec': df['latency_sec'].mean(),
        'automated_median_sec': df['latency_sec'].median(),
        'mean_diff_sec': df['latency_diff'].mean(),
        't_statistic': t_stat,
        'p_value_two_tail': p_value_two_tail,
        'p_value_one_tail': p_value_one_tail,
        'ci_lower': ci[0],
        'ci_upper': ci[1],
        'significant': p_value_one_tail < alpha
    }


def mcnemar_test(
    df: pd.DataFrame,
    manual_validation_rate: float = 0.85,
    alpha: float = 0.05
) -> Dict[str, float]:
    """
    Execute McNemar's test for validation accuracy.
    
    Args:
        df: DataFrame with validation_pass_bool column
        manual_validation_rate: Baseline manual validation pass rate
        alpha: Significance level
        
    Returns:
        Dictionary with test results
    """
    print("\n" + "=" * 70)
    print("MCNEMAR'S TEST: VALIDATION ACCURACY")
    print("=" * 70)
    
    # Simulate manual validation (in real study, this would be measured)
    np.random.seed(12345)
    df = df.copy()
    df['manual_validation_est'] = np.random.rand(len(df)) < manual_validation_rate
    
    # Create contingency table
    contingency = pd.crosstab(
        df['manual_validation_est'], 
        df['validation_pass_bool'],
        rownames=['Manual'], 
        colnames=['Automated']
    )
    
    print("\nContingency Table:")
    print(contingency)
    
    # McNemar's test
    result = mcnemar(contingency, exact=False, correction=True)
    
    print(f"\nChi-square statistic: {result.statistic:.4f}")
    print(f"p-value: {result.pvalue:.6f}")
    
    manual_pass_rate = df['manual_validation_est'].mean() * 100
    auto_pass_rate = df['validation_pass_bool'].mean() * 100
    
    if result.pvalue < alpha:
        print(f"\n✓ REJECT H₀ (p < {alpha})")
        print("  Validation accuracy differs significantly")
    else:
        print(f"\n❌ FAIL TO REJECT H₀ (p >= {alpha})")
        print("  No significant difference")
    
    print(f"\nManual Pass Rate: {manual_pass_rate:.2f}%")
    print(f"Automated Pass Rate: {auto_pass_rate:.2f}%")
    print(f"Improvement: {auto_pass_rate - manual_pass_rate:+.2f} pp")
    
    return {
        'manual_pass_rate': manual_pass_rate / 100,
        'automated_pass_rate': auto_pass_rate / 100,
        'improvement_pp': auto_pass_rate - manual_pass_rate,
        'chi2_statistic': result.statistic,
        'p_value': result.pvalue,
        'significant': result.pvalue < alpha
    }


def calculate_effect_size(df: pd.DataFrame, manual_baseline: float = 1200.0) -> Dict[str, float]:
    """
    Calculate Cohen's d effect size for paired samples.
    
    Args:
        df: DataFrame with latency_sec column
        manual_baseline: Manual baseline latency in seconds
        
    Returns:
        Dictionary with effect size metrics
    """
    print("\n" + "=" * 70)
    print("EFFECT SIZE ANALYSIS")
    print("=" * 70)
    
    df = df.copy()
    df['manual_latency_est'] = manual_baseline
    df['latency_diff'] = df['manual_latency_est'] - df['latency_sec']
    
    # Cohen's d for paired samples
    mean_diff = df['latency_diff'].mean()
    std_diff = df['latency_diff'].std()
    cohens_d = mean_diff / std_diff
    
    # Interpretation
    if abs(cohens_d) < 0.2:
        interpretation = "negligible"
    elif abs(cohens_d) < 0.5:
        interpretation = "small"
    elif abs(cohens_d) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"
    
    # Speedup factor
    speedup = manual_baseline / df['latency_sec'].mean()
    
    print(f"Cohen's d: {cohens_d:.4f}")
    print(f"Interpretation: {interpretation.upper()}")
    print(f"Speedup: {speedup:.1f}x faster")
    print(f"Time savings: {(1 - 1/speedup) * 100:.1f}%")
    
    return {
        'cohens_d': cohens_d,
        'interpretation': interpretation,
        'speedup_factor': speedup,
        'time_savings_pct': (1 - 1/speedup) * 100
    }


def sensitivity_analysis(
    df: pd.DataFrame,
    baseline_range_min: list = None,
    alpha: float = 0.05,
    output_dir: str = 'reports/figures/results'
) -> pd.DataFrame:
    """
    Test robustness across different baseline assumptions.
    
    Args:
        df: DataFrame with latency_sec column
        baseline_range_min: List of baseline values in minutes
        alpha: Significance level
        output_dir: Directory to save figures
        
    Returns:
        DataFrame with sensitivity analysis results
    """
    if baseline_range_min is None:
        baseline_range_min = [15, 20, 25, 30, 45]
    
    print("\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS")
    print("=" * 70)
    
    results = []
    
    for baseline_min in baseline_range_min:
        baseline_sec = baseline_min * 60
        df_temp = df.copy()
        df_temp['manual_latency_temp'] = baseline_sec
        df_temp['latency_diff_temp'] = df_temp['manual_latency_temp'] - df_temp['latency_sec']
        
        # Paired t-test
        t_stat, p_val = stats.ttest_rel(
            df_temp['manual_latency_temp'], 
            df_temp['latency_sec']
        )
        p_val_one_tail = p_val / 2 if t_stat > 0 else 1 - (p_val / 2)
        
        # Effect size
        cohens_d = df_temp['latency_diff_temp'].mean() / df_temp['latency_diff_temp'].std()
        
        results.append({
            'baseline_min': baseline_min,
            'baseline_sec': baseline_sec,
            't_statistic': t_stat,
            'p_value': p_val_one_tail,
            'cohens_d': cohens_d,
            'significant': p_val_one_tail < alpha,
            'large_effect': cohens_d >= 0.8
        })
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    # Robustness check
    all_sig = results_df['significant'].all()
    all_large = results_df['large_effect'].all()
    
    print(f"\nRobust across all baselines: {'✓ YES' if (all_sig and all_large) else '⚠ NO'}")
    
    # Visualization
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # P-values
    axes[0].plot(results_df['baseline_min'], results_df['p_value'], 
                 marker='o', linewidth=2, markersize=8)
    axes[0].axhline(alpha, color='red', linestyle='--', linewidth=2, label=f'α={alpha}')
    axes[0].set_xlabel('Baseline (minutes)')
    axes[0].set_ylabel('p-value (one-tailed)')
    axes[0].set_title('Significance Across Baselines')
    axes[0].legend()
    axes[0].set_yscale('log')
    axes[0].grid(True, alpha=0.3)
    
    # Effect sizes
    axes[1].plot(results_df['baseline_min'], results_df['cohens_d'], 
                 marker='o', linewidth=2, markersize=8, color='green')
    axes[1].axhline(0.8, color='red', linestyle='--', linewidth=2, label='Large (d=0.8)')
    axes[1].set_xlabel('Baseline (minutes)')
    axes[1].set_ylabel("Cohen's d")
    axes[1].set_title('Effect Size Across Baselines')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    filepath = output_path / 'sensitivity_analysis.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Saved: {filepath}")
    
    return results_df


def subgroup_analysis(
    df: pd.DataFrame,
    manual_baseline: float = 1200.0,
    alpha: float = 0.05,
    output_dir: str = 'reports/figures/results'
) -> pd.DataFrame:
    """
    Test improvements across data source subgroups.
    
    Args:
        df: DataFrame with latency_sec and data_source columns
        manual_baseline: Manual baseline latency in seconds
        alpha: Significance level
        output_dir: Directory to save figures
        
    Returns:
        DataFrame with subgroup analysis results
    """
    print("\n" + "=" * 70)
    print("SUBGROUP ANALYSIS BY DATA SOURCE")
    print("=" * 70)
    
    df = df.copy()
    df['manual_latency_est'] = manual_baseline
    df['latency_diff'] = df['manual_latency_est'] - df['latency_sec']
    
    results = []
    
    for source in df['data_source'].unique():
        subset = df[df['data_source'] == source]
        
        if len(subset) < 30:
            continue
        
        # Paired t-test
        t_stat, p_val = stats.ttest_rel(
            subset['manual_latency_est'], 
            subset['latency_sec']
        )
        p_val_one_tail = p_val / 2 if t_stat > 0 else 1 - (p_val / 2)
        
        # Effect size
        cohens_d = subset['latency_diff'].mean() / subset['latency_diff'].std()
        
        # CI for Cohen's d
        n = len(subset)
        se_d = np.sqrt((n-1)/(n-3)) * np.sqrt((1/n) + (cohens_d**2)/(2*n))
        ci_lower = cohens_d - 1.96 * se_d
        ci_upper = cohens_d + 1.96 * se_d
        
        results.append({
            'subgroup': source,
            'n': n,
            'mean_latency': subset['latency_sec'].mean(),
            'cohens_d': cohens_d,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'p_value': p_val_one_tail,
            'significant': p_val_one_tail < alpha
        })
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    # Forest plot
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(results_df) * 0.8)))
    
    y_pos = np.arange(len(results_df))
    ax.errorbar(
        results_df['cohens_d'], y_pos,
        xerr=[results_df['cohens_d'] - results_df['ci_lower'],
              results_df['ci_upper'] - results_df['cohens_d']],
        fmt='o', markersize=10, capsize=5, linewidth=2
    )
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['subgroup'].title()} (n={row['n']:,})" 
                        for _, row in results_df.iterrows()])
    ax.set_xlabel("Cohen's d (95% CI)")
    ax.set_title('Effect Size by Data Source (Forest Plot)')
    ax.axvline(0, color='gray', linestyle='--', linewidth=1)
    ax.axvline(0.8, color='red', linestyle=':', linewidth=2, label='Large Effect')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    filepath = output_path / 'forest_plot_by_source.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Saved: {filepath}")
    
    return results_df


def export_results(
    results_dict: Dict,
    output_path: str = 'reports/statistical_results.csv'
) -> None:
    """
    Export statistical results to CSV.
    
    Args:
        results_dict: Dictionary with all statistical results
        output_path: Path to save results CSV
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    results_df = pd.DataFrame([results_dict])
    results_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Results exported to: {output_file}")
    print("\nResults Summary:")
    for key, value in results_dict.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")


if __name__ == '__main__':
    # Example usage
    from .run_eda import load_and_validate_data
    
    df = load_and_validate_data()
    
    # Hypothesis tests
    ttest_results = paired_t_test(df)
    mcnemar_results = mcnemar_test(df)
    effect_results = calculate_effect_size(df)
    
    # Robustness checks
    sensitivity_results = sensitivity_analysis(df)
    subgroup_results = subgroup_analysis(df)
    
    # Export
    all_results = {**ttest_results, **mcnemar_results, **effect_results}
    export_results(all_results)
    
    print("\n✓ Statistical analysis complete!")
