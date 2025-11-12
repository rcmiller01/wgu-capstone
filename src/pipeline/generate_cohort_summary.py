"""
Generate cohort fact table and validation report for Phase 3.

This script:
1. Loads processed data from Phase 3
2. Creates cohort_fact_va.csv with aggregated metrics
3. Generates validation_report.md with data quality checks
"""

from datetime import datetime
from pathlib import Path

import pandas as pd


def load_processed_data() -> pd.DataFrame:
    """Load processed data parquet file."""
    data_path = Path("data/processed/processed_data.parquet")

    if not data_path.exists():
        raise FileNotFoundError(
            f"Processed data not found at {data_path}. " "Run Phase 3 data cleaning first."
        )

    return pd.read_parquet(data_path)


def create_cohort_fact_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create cohort fact table with aggregated metrics by data source.

    Returns DataFrame with columns:
    - data_source
    - n_records
    - mean_latency_sec
    - p50_latency_sec
    - p95_latency_sec
    - validation_pass_rate
    - mean_file_size_kb
    """
    cohort = (
        df.groupby("data_source")
        .agg(
            n_records=("latency_sec", "count"),
            mean_latency_sec=("latency_sec", "mean"),
            p50_latency_sec=("latency_sec", lambda x: x.quantile(0.5)),
            p95_latency_sec=("latency_sec", lambda x: x.quantile(0.95)),
            validation_pass_rate=("validation_passed", "mean"),
            mean_file_size_kb=("file_size_kb", "mean"),
        )
        .reset_index()
    )

    # Add overall summary row
    overall = pd.DataFrame(
        [
            {
                "data_source": "ALL",
                "n_records": len(df),
                "mean_latency_sec": df["latency_sec"].mean(),
                "p50_latency_sec": df["latency_sec"].quantile(0.5),
                "p95_latency_sec": df["latency_sec"].quantile(0.95),
                "validation_pass_rate": df["validation_passed"].mean(),
                "mean_file_size_kb": df["file_size_kb"].mean(),
            }
        ]
    )

    cohort = pd.concat([cohort, overall], ignore_index=True)

    # Round to reasonable precision
    cohort["mean_latency_sec"] = cohort["mean_latency_sec"].round(2)
    cohort["p50_latency_sec"] = cohort["p50_latency_sec"].round(2)
    cohort["p95_latency_sec"] = cohort["p95_latency_sec"].round(2)
    cohort["validation_pass_rate"] = cohort["validation_pass_rate"].round(4)
    cohort["mean_file_size_kb"] = cohort["mean_file_size_kb"].round(2)

    return cohort


def generate_validation_report(df: pd.DataFrame, cohort: pd.DataFrame) -> str:
    """Generate markdown validation report."""

    report = []
    report.append("# Data Validation Report")
    report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n**Data Source**: `data/processed/processed_data.parquet`")
    report.append(f"\n**Total Records**: {len(df):,}")
    report.append("\n---\n")

    # 1. Schema Validation
    report.append("## 1. Schema Validation\n")
    required_columns = ["latency_sec", "file_size_kb", "data_source", "validation_passed"]

    report.append("**Required Columns:**\n")
    for col in required_columns:
        status = "✅" if col in df.columns else "❌"
        report.append(f"- {status} `{col}`")

    report.append(f"\n**Total Columns**: {len(df.columns)}")
    report.append(f"\n**Column List**: {', '.join(f'`{c}`' for c in df.columns)}\n")

    # 2. Data Quality Checks
    report.append("## 2. Data Quality Checks\n")

    # Missing values
    missing = df.isnull().sum()
    report.append("### Missing Values\n")
    if missing.sum() == 0:
        report.append("✅ **No missing values detected**\n")
    else:
        report.append("| Column | Missing Count | Missing % |\n")
        report.append("|--------|---------------|----------|\n")
        for col in missing[missing > 0].index:
            pct = (missing[col] / len(df)) * 100
            report.append(f"| `{col}` | {missing[col]:,} | {pct:.2f}% |\n")

    # Value ranges
    report.append("### Value Ranges\n")
    report.append("| Metric | Min | Max | Mean | Median |\n")
    report.append("|--------|-----|-----|------|--------|\n")

    for col in ["latency_sec", "file_size_kb"]:
        if col in df.columns:
            report.append(
                f"| `{col}` | {df[col].min():.2f} | {df[col].max():.2f} | "
                f"{df[col].mean():.2f} | {df[col].median():.2f} |\n"
            )

    # Data source distribution
    report.append("\n### Data Source Distribution\n")
    report.append("| Data Source | Count | Percentage |\n")
    report.append("|-------------|-------|------------|\n")

    source_dist = df["data_source"].value_counts()
    for source, count in source_dist.items():
        pct = (count / len(df)) * 100
        report.append(f"| {source} | {count:,} | {pct:.1f}% |\n")

    # 3. Statistical Assumptions
    report.append("\n## 3. Statistical Assumptions\n")

    # Sample size
    min_sample_size = 800
    sample_size_ok = len(df) >= min_sample_size
    status = "✅" if sample_size_ok else "❌"
    report.append(f"- {status} **Sample Size**: {len(df):,} (minimum: {min_sample_size:,})\n")

    # Latency range check
    latency_positive = (df["latency_sec"] > 0).all()
    status = "✅" if latency_positive else "❌"
    report.append(f"- {status} **Latency Positive**: All values > 0\n")

    latency_reasonable = (df["latency_sec"] < 600).all()
    status = "✅" if latency_reasonable else "⚠️"
    report.append(f"- {status} **Latency Reasonable**: All values < 600s (10 min)\n")

    # Validation boolean
    validation_types = df["validation_passed"].unique()
    validation_boolean = set(validation_types).issubset({True, False})
    status = "✅" if validation_boolean else "❌"
    report.append(f"- {status} **Validation Boolean**: Only True/False values\n")

    # 4. Cohort Summary
    report.append("\n## 4. Cohort Summary by Data Source\n")
    report.append(
        "| Data Source | N | Mean Latency (s) | P50 (s) | P95 (s) | Validation % | Avg File Size (KB) |\n"
    )
    report.append(
        "|-------------|---|------------------|---------|---------|--------------|--------------------|\n"
    )

    for _, row in cohort.iterrows():
        report.append(
            f"| {row['data_source']} | {row['n_records']:,} | "
            f"{row['mean_latency_sec']:.2f} | {row['p50_latency_sec']:.2f} | "
            f"{row['p95_latency_sec']:.2f} | {row['validation_pass_rate']*100:.1f}% | "
            f"{row['mean_file_size_kb']:.2f} |\n"
        )

    # 5. Threshold Achievement
    report.append("\n## 5. Performance Threshold Achievement\n")

    p50 = df["latency_sec"].quantile(0.5)
    p95 = df["latency_sec"].quantile(0.95)
    val_rate = df["validation_passed"].mean()

    p50_status = "✅" if p50 <= 30 else "❌"
    p95_status = "✅" if p95 <= 120 else "❌"
    val_status = "✅" if val_rate >= 0.95 else "⚠️"

    report.append(f"- {p50_status} **P50 Latency**: {p50:.2f}s (target: ≤30s)\n")
    report.append(f"- {p95_status} **P95 Latency**: {p95:.2f}s (target: ≤120s)\n")
    report.append(f"- {val_status} **Validation Rate**: {val_rate*100:.1f}% (target: ≥95%)\n")

    # 6. Data Readiness
    report.append("\n## 6. Data Readiness for Analysis\n")

    all_checks = [
        sample_size_ok,
        latency_positive,
        latency_reasonable,
        validation_boolean,
        missing.sum() == 0,
    ]

    if all(all_checks):
        report.append("✅ **All validation checks passed**\n")
        report.append("\nData is ready for Phase 6/7 analysis:\n")
        report.append("- Exploratory data analysis (EDA)\n")
        report.append("- Statistical hypothesis testing\n")
        report.append("- Visualization and reporting\n")
    else:
        report.append("⚠️ **Some validation checks failed**\n")
        report.append("\nReview failed checks above before proceeding to analysis.\n")

    report.append("\n---\n")
    report.append("\n*Report generated by `src/pipeline/generate_cohort_summary.py`*")

    return "\n".join(report)


def main():
    """Main execution function."""
    print("=" * 70)
    print("GENERATING COHORT SUMMARY AND VALIDATION REPORT")
    print("=" * 70)

    # Load data
    print("\n1. Loading processed data...")
    df = load_processed_data()
    print(f"   ✓ Loaded {len(df):,} records from data/processed/processed_data.parquet")

    # Create cohort fact table
    print("\n2. Creating cohort fact table...")
    cohort = create_cohort_fact_table(df)

    # Save cohort to CSV
    cohort_path = Path("data/processed/cohort_fact_va.csv")
    cohort.to_csv(cohort_path, index=False)
    print(f"   ✓ Saved cohort fact table to {cohort_path}")

    # Generate validation report
    print("\n3. Generating validation report...")
    report = generate_validation_report(df, cohort)

    # Save report
    report_path = Path("reports/validation_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"   ✓ Saved validation report to {report_path}")

    # Display summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nTotal Records: {len(df):,}")
    print(f"Data Sources: {df['data_source'].nunique()}")
    print(f"\nP50 Latency: {df['latency_sec'].quantile(0.5):.2f}s")
    print(f"P95 Latency: {df['latency_sec'].quantile(0.95):.2f}s")
    print(f"Validation Rate: {df['validation_passed'].mean()*100:.1f}%")
    print("\nFiles generated:")
    print(f"  - {cohort_path}")
    print(f"  - {report_path}")
    print("\n✓ Generation complete!")


if __name__ == "__main__":
    main()
