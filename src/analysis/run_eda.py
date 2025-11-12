"""
Exploratory Data Analysis (EDA) module.

This module provides functions for loading, validating, and exploring
the processed dataset through visualization and summary statistics.
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")


def load_and_validate_data(data_path: str = "data/processed/combined_data.parquet") -> pd.DataFrame:
    """
    Load processed data and perform validation checks.

    Args:
        data_path: Path to processed data file

    Returns:
        Validated DataFrame

    Raises:
        FileNotFoundError: If data file doesn't exist
        AssertionError: If validation checks fail
    """
    data_path_obj = Path(data_path)

    if not data_path_obj.exists():
        raise FileNotFoundError(
            f"Processed data not found at {data_path}. " "Please run Phase 3 data cleaning first."
        )

    df = pd.read_parquet(data_path_obj)

    # Validation checks
    print("=" * 70)
    print("DATA VALIDATION")
    print("=" * 70)

    # 1. Sample size
    min_sample = 800
    assert df.shape[0] >= min_sample, f"Insufficient sample size: {df.shape[0]} < {min_sample}"
    print(f"✓ Sample size: {df.shape[0]:,} (≥{min_sample} required)")

    # 2. Required columns
    required_cols = [
        "latency_sec",
        "validation_pass_bool",
        "data_source",
        "record_complexity",
        "file_size_kb",
    ]

    missing_cols = set(required_cols) - set(df.columns)
    assert len(missing_cols) == 0, f"Missing columns: {missing_cols}"
    print(f"✓ All {len(required_cols)} required columns present")

    # 3. No missing outcomes
    assert df["latency_sec"].notna().all(), "Missing values in latency_sec"
    assert df["validation_pass_bool"].notna().all(), "Missing values in validation_pass_bool"
    print("✓ No missing values in outcome variables")

    # 4. Value ranges
    assert (df["latency_sec"] > 0).all(), "Non-positive latency values"
    assert (df["latency_sec"] < 600).all(), "Implausible latency (>10 min)"
    assert (df["file_size_kb"] >= 0).all(), "Negative file sizes"
    print("✓ Value ranges valid")

    print("\n✓ All validation checks passed!")
    print(f"\nDataset shape: {df.shape}")
    print(f"Data sources: {df['data_source'].nunique()}")

    return df


def generate_univariate_plots(
    df: pd.DataFrame, output_dir: str = "reports/figures/eda"
) -> list[str]:
    """
    Generate univariate analysis plots.

    Args:
        df: DataFrame with processed data
        output_dir: Directory to save figures

    Returns:
        List of generated figure paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    sns.set_style("whitegrid")
    generated_files = []

    print("\n" + "=" * 70)
    print("GENERATING UNIVARIATE PLOTS")
    print("=" * 70)

    # 1. Latency distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(df["latency_sec"], bins=50, edgecolor="black", alpha=0.7, color="steelblue")
    axes[0].axvline(
        df["latency_sec"].median(),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f'Median: {df["latency_sec"].median():.1f}s',
    )
    axes[0].set_xlabel("Latency (seconds)")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title("Latency Distribution")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    sns.kdeplot(data=df, x="latency_sec", ax=axes[1], fill=True, color="steelblue")
    axes[1].axvline(30, color="green", linestyle=":", linewidth=2, label="P50 Target (30s)")
    axes[1].axvline(120, color="orange", linestyle=":", linewidth=2, label="P95 Target (120s)")
    axes[1].set_xlabel("Latency (seconds)")
    axes[1].set_title("Kernel Density Estimate")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_path / "latency_distribution.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    generated_files.append(str(filepath))
    print(f"✓ Saved: {filepath.name}")

    # 2. Data source distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    source_counts = df["data_source"].value_counts()
    source_counts.plot(kind="bar", ax=ax, color=sns.color_palette("colorblind"))
    ax.set_xlabel("Data Source")
    ax.set_ylabel("Number of Records")
    ax.set_title("Distribution by Data Source")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

    total = source_counts.sum()
    for i, v in enumerate(source_counts):
        ax.text(i, v + (total * 0.02), f"{v:,}\n({v/total*100:.1f}%)", ha="center", va="bottom")

    plt.tight_layout()
    filepath = output_path / "data_source_distribution.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    generated_files.append(str(filepath))
    print(f"✓ Saved: {filepath.name}")

    # 3. Validation pass rate
    fig, ax = plt.subplots(figsize=(8, 8))
    validation_counts = df["validation_pass_bool"].value_counts()
    colors = ["#2ecc71", "#e74c3c"]
    labels = ["Pass", "Fail"]

    ax.pie(
        validation_counts,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 14, "weight": "bold"},
    )
    ax.set_title(f"Validation Results (n={len(df):,})", fontsize=16, weight="bold")

    plt.tight_layout()
    filepath = output_path / "validation_pie_chart.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    generated_files.append(str(filepath))
    print(f"✓ Saved: {filepath.name}")

    print(f"\n✓ Generated {len(generated_files)} univariate plots")
    return generated_files


def generate_bivariate_plots(
    df: pd.DataFrame, output_dir: str = "reports/figures/eda"
) -> list[str]:
    """
    Generate bivariate analysis plots.

    Args:
        df: DataFrame with processed data
        output_dir: Directory to save figures

    Returns:
        List of generated figure paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    print("\n" + "=" * 70)
    print("GENERATING BIVARIATE PLOTS")
    print("=" * 70)

    # 1. Latency by data source (boxplot)
    fig, ax = plt.subplots(figsize=(12, 6))
    df.boxplot(column="latency_sec", by="data_source", ax=ax, grid=False)
    ax.set_xlabel("Data Source", fontsize=12)
    ax.set_ylabel("Latency (seconds)", fontsize=12)
    ax.set_title("Latency Distribution by Data Source", fontsize=14, weight="bold")
    plt.suptitle("")
    ax.axhline(30, color="green", linestyle=":", linewidth=2, alpha=0.7, label="P50 Target")
    ax.axhline(120, color="orange", linestyle=":", linewidth=2, alpha=0.7, label="P95 Target")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_path / "latency_by_source_boxplot.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    generated_files.append(str(filepath))
    print(f"✓ Saved: {filepath.name}")

    # 2. Correlation heatmap
    numeric_cols = ["latency_sec", "file_size_kb", "validation_pass_bool"]
    corr_matrix = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8},
        ax=ax,
        vmin=-1,
        vmax=1,
    )
    ax.set_title("Correlation Matrix", fontsize=14, weight="bold")

    plt.tight_layout()
    filepath = output_path / "correlation_matrix.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    generated_files.append(str(filepath))
    print(f"✓ Saved: {filepath.name}")

    # 3. Scatter plot (file size vs latency)
    fig, ax = plt.subplots(figsize=(10, 6))

    source_categories = df["data_source"].astype("category")
    scatter = ax.scatter(
        df["file_size_kb"],
        df["latency_sec"],
        c=source_categories.cat.codes,
        alpha=0.6,
        s=30,
        cmap="tab10",
    )

    ax.set_xlabel("File Size (KB)", fontsize=12)
    ax.set_ylabel("Latency (seconds)", fontsize=12)
    ax.set_title("Latency vs File Size", fontsize=14, weight="bold")

    # Trend line
    if len(df) > 0:
        z = np.polyfit(df["file_size_kb"], df["latency_sec"], 1)
        p = np.poly1d(z)
        sorted_x = df["file_size_kb"].sort_values()
        ax.plot(
            sorted_x,
            p(sorted_x),
            "r--",
            alpha=0.8,
            linewidth=2,
            label=f"Trend: y={z[0]:.4f}x+{z[1]:.2f}",
        )
        ax.legend()

    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_path / "latency_vs_file_size_scatter.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    generated_files.append(str(filepath))
    print(f"✓ Saved: {filepath.name}")

    print(f"\n✓ Generated {len(generated_files)} bivariate plots")
    return generated_files


def assess_normality(
    df: pd.DataFrame, manual_baseline: float = 1200.0, output_dir: str = "reports/figures/eda"
) -> dict[str, float]:
    """
    Assess normality assumption for difference scores.

    Args:
        df: DataFrame with processed data
        manual_baseline: Manual baseline latency in seconds
        output_dir: Directory to save figures

    Returns:
        Dictionary with normality test results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print("NORMALITY ASSESSMENT")
    print("=" * 70)

    # Create difference scores
    df = df.copy()
    df["manual_latency_est"] = manual_baseline
    df["latency_diff"] = df["manual_latency_est"] - df["latency_sec"]

    # Shapiro-Wilk test (sample if n > 5000)
    sample_size = min(5000, len(df["latency_diff"]))
    sample_diff = df["latency_diff"].sample(sample_size, random_state=12345)

    stat, p_value = stats.shapiro(sample_diff)

    print("\nShapiro-Wilk Test:")
    print(f"  Sample Size: {sample_size:,}")
    print(f"  Test Statistic: {stat:.6f}")
    print(f"  P-value: {p_value:.6f}")

    if p_value < 0.05:
        print("  ❌ Reject null: Data is NOT normally distributed")
        print("  → Consider Wilcoxon signed-rank test")
    else:
        print("  ✓ Fail to reject: Data consistent with normal distribution")
        print("  → Paired t-test is appropriate")

    # Q-Q plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    stats.probplot(df["latency_diff"], dist="norm", plot=axes[0])
    axes[0].set_title("Q-Q Plot: Difference Scores", fontsize=12, weight="bold")
    axes[0].grid(True, alpha=0.3)

    # Histogram with normal overlay
    axes[1].hist(
        df["latency_diff"],
        bins=50,
        density=True,
        alpha=0.7,
        edgecolor="black",
        color="steelblue",
        label="Observed",
    )

    mu, sigma = df["latency_diff"].mean(), df["latency_diff"].std()
    x = np.linspace(df["latency_diff"].min(), df["latency_diff"].max(), 100)
    axes[1].plot(
        x, stats.norm.pdf(x, mu, sigma), "r-", lw=2, label=f"Normal(μ={mu:.1f}, σ={sigma:.1f})"
    )

    axes[1].set_xlabel("Latency Difference (seconds)", fontsize=12)
    axes[1].set_ylabel("Density", fontsize=12)
    axes[1].set_title(f"Normality Check (p={p_value:.4f})", fontsize=12, weight="bold")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_path / "qq_plots_normality.png"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\n✓ Saved: {filepath.name}")

    return {
        "shapiro_statistic": stat,
        "shapiro_pvalue": p_value,
        "is_normal": p_value >= 0.05,
        "mean_diff": mu,
        "std_diff": sigma,
    }


def create_eda_report(df: pd.DataFrame, output_path: str = "reports/eda_summary.txt") -> None:
    """
    Create text summary report of EDA findings.

    Args:
        df: DataFrame with processed data
        output_path: Path to save report
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("EXPLORATORY DATA ANALYSIS SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Dataset: {len(df):,} records\n")
        f.write(f"Data Sources: {df['data_source'].nunique()}\n")
        f.write(f"Columns: {len(df.columns)}\n\n")

        f.write("LATENCY STATISTICS:\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Mean:     {df['latency_sec'].mean():.2f} seconds\n")
        f.write(f"  Median:   {df['latency_sec'].median():.2f} seconds\n")
        f.write(f"  Std Dev:  {df['latency_sec'].std():.2f} seconds\n")
        f.write(f"  P50:      {df['latency_sec'].quantile(0.5):.2f} seconds\n")
        f.write(f"  P95:      {df['latency_sec'].quantile(0.95):.2f} seconds\n")
        f.write(f"  P99:      {df['latency_sec'].quantile(0.99):.2f} seconds\n\n")

        f.write("VALIDATION STATISTICS:\n")
        f.write("-" * 70 + "\n")
        pass_rate = df["validation_pass_bool"].mean() * 100
        f.write(f"  Pass Rate: {pass_rate:.2f}%\n")
        f.write(f"  Passed:    {df['validation_pass_bool'].sum():,}\n")
        f.write(f"  Failed:    {(~df['validation_pass_bool']).sum():,}\n\n")

        f.write("DATA SOURCE BREAKDOWN:\n")
        f.write("-" * 70 + "\n")
        source_counts = df["data_source"].value_counts()
        for source, count in source_counts.items():
            pct = count / len(df) * 100
            f.write(f"  {source}: {count:,} ({pct:.1f}%)\n")

        f.write("\n" + "=" * 70 + "\n")

    print(f"\n✓ EDA report saved to: {output_file}")


if __name__ == "__main__":
    # Example usage
    df = load_and_validate_data()
    generate_univariate_plots(df)
    generate_bivariate_plots(df)
    normality_results = assess_normality(df)
    create_eda_report(df)

    print("\n✓ EDA complete!")
