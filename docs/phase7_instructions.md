# Phase 7 Instructions: EDA, Visualization, and Statistical Analysis

**Issue**: #8  
**Status**: In Progress  
**Goal**: Execute exploratory data analysis, create visualizations, run hypothesis tests, and document results

---

## Overview

Phase 7 is where the **actual data science** happens. This phase executes:

1. **Exploratory Data Analysis (EDA)**: Understanding data distributions, relationships, and quality
2. **Data Visualization**: Creating plots for exploration AND publication
3. **Statistical Testing**: Running paired t-test, McNemar's test, effect size calculations
4. **Assumption Validation**: Checking normality, independence, paired structure
5. **Sensitivity Analysis**: Testing robustness across baseline assumptions
6. **Results Documentation**: Generating tables, figures, and narrative findings

**Input**: `data/processed/combined_data.parquet` (from Phase 3 cleaning)  
**Output**: Statistical results, publication figures, EDA report

---

## Task 1: Load and Validate Processed Data

### Objective

Ensure cleaned data is analysis-ready before proceeding.

### Validation Checklist

```python
import pandas as pd
import numpy as np
from pathlib import Path

# Load data
df = pd.read_parquet('data/processed/combined_data.parquet')

# 1. Shape check
print(f"Dataset shape: {df.shape}")
assert df.shape[0] >= 800, "Insufficient sample size for 80% power"

# 2. Required columns
required_cols = [
    'latency_sec',           # Primary DV
    'validation_pass_bool',  # Secondary DV
    'data_source',           # Primary IV
    'record_complexity',     # IV
    'file_size_kb',          # Control variable
    'health_district',       # Stratifier (if VDH data present)
    'rural_urban',           # Stratifier
    'data_type'              # Stratifier
]

missing_cols = set(required_cols) - set(df.columns)
assert len(missing_cols) == 0, f"Missing columns: {missing_cols}"

# 3. No missing outcomes
assert df['latency_sec'].notna().all(), "Missing values in latency_sec"
assert df['validation_pass_bool'].notna().all(), "Missing values in validation_pass_bool"

# 4. Data types
assert pd.api.types.is_numeric_dtype(df['latency_sec'])
assert pd.api.types.is_bool_dtype(df['validation_pass_bool'])
assert pd.api.types.is_categorical_dtype(df['data_source']) or df['data_source'].dtype == 'object'

# 5. Value ranges
assert (df['latency_sec'] > 0).all(), "Non-positive latency values"
assert (df['latency_sec'] < 600).all(), "Implausible latency (>10 min for automated)"
assert (df['file_size_kb'] >= 0).all(), "Negative file sizes"

print("✓ Data validation passed!")
```

---

## Task 2: Exploratory Data Analysis (EDA)

### Objective

Understand data characteristics before formal testing.

### 2.1 Univariate Analysis

#### Continuous Variables

**Latency (latency_sec)**:

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Summary statistics
print(df['latency_sec'].describe())

# Histogram + KDE
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Raw distribution
axes[0].hist(df['latency_sec'], bins=50, edgecolor='black', alpha=0.7)
axes[0].axvline(df['latency_sec'].median(), color='red', linestyle='--', label='Median')
axes[0].axvline(df['latency_sec'].mean(), color='blue', linestyle='--', label='Mean')
axes[0].set_xlabel('Latency (seconds)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Distribution of Automated Pipeline Latency')
axes[0].legend()

# KDE with rug
sns.kdeplot(data=df, x='latency_sec', ax=axes[1], fill=True)
sns.rugplot(data=df, x='latency_sec', ax=axes[1], alpha=0.3)
axes[1].axvline(30, color='green', linestyle=':', label='P50 Threshold (30s)')
axes[1].axvline(120, color='orange', linestyle=':', label='P95 Threshold (120s)')
axes[1].set_xlabel('Latency (seconds)')
axes[1].set_title('Kernel Density Estimate')
axes[1].legend()

plt.tight_layout()
plt.savefig('reports/figures/eda/latency_distribution.png', dpi=300)
plt.show()

# Percentiles
print("\nLatency Percentiles:")
print(df['latency_sec'].quantile([0.25, 0.5, 0.75, 0.95]))
```

**File Size (file_size_kb)**:

```python
# File size distribution (often right-skewed)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Linear scale
axes[0].hist(df['file_size_kb'], bins=50, edgecolor='black', alpha=0.7)
axes[0].set_xlabel('File Size (KB)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('File Size Distribution (Linear Scale)')

# Log scale (if skewed)
axes[1].hist(np.log10(df['file_size_kb'] + 1), bins=50, edgecolor='black', alpha=0.7)
axes[1].set_xlabel('Log10(File Size + 1)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('File Size Distribution (Log Scale)')

plt.tight_layout()
plt.savefig('reports/figures/eda/file_size_distribution.png', dpi=300)
plt.show()
```

#### Categorical Variables

**Data Source**:

```python
# Value counts
source_counts = df['data_source'].value_counts()
print(source_counts)

# Bar chart
fig, ax = plt.subplots(figsize=(10, 6))
source_counts.plot(kind='bar', ax=ax, color=sns.color_palette("colorblind"))
ax.set_xlabel('Data Source')
ax.set_ylabel('Number of Records')
ax.set_title('Distribution of Records by Data Source')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

# Add percentage labels
total = source_counts.sum()
for i, v in enumerate(source_counts):
    ax.text(i, v + 10, f'{v}\n({v/total*100:.1f}%)', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('reports/figures/eda/data_source_distribution.png', dpi=300)
plt.show()
```

**Validation Pass Rate**:

```python
# Overall pass rate
pass_rate = df['validation_pass_bool'].mean() * 100
print(f"Overall Validation Pass Rate: {pass_rate:.2f}%")

# Pie chart
fig, ax = plt.subplots(figsize=(8, 8))
validation_counts = df['validation_pass_bool'].value_counts()
colors = ['#2ecc71', '#e74c3c']  # Green for pass, red for fail
ax.pie(validation_counts, labels=['Pass', 'Fail'], autopct='%1.1f%%', 
       startangle=90, colors=colors, textprops={'fontsize': 14})
ax.set_title(f'Validation Results (n={len(df)})', fontsize=16)
plt.savefig('reports/figures/eda/validation_pie_chart.png', dpi=300)
plt.show()
```

---

### 2.2 Bivariate Analysis

#### Latency by Data Source

```python
# Boxplot comparison
fig, ax = plt.subplots(figsize=(12, 6))
df.boxplot(column='latency_sec', by='data_source', ax=ax)
ax.set_xlabel('Data Source')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Latency Distribution by Data Source')
plt.suptitle('')  # Remove auto-title
ax.axhline(30, color='green', linestyle=':', label='P50 Threshold')
ax.axhline(120, color='orange', linestyle=':', label='P95 Threshold')
ax.legend()
plt.tight_layout()
plt.savefig('reports/figures/eda/latency_by_source_boxplot.png', dpi=300)
plt.show()

# Violin plot (shows distribution shape)
fig, ax = plt.subplots(figsize=(12, 6))
sns.violinplot(data=df, x='data_source', y='latency_sec', ax=ax, palette="colorblind")
ax.set_xlabel('Data Source')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Latency Distribution by Data Source (Violin Plot)')
ax.axhline(30, color='green', linestyle=':', alpha=0.7)
ax.axhline(120, color='orange', linestyle=':', alpha=0.7)
plt.tight_layout()
plt.savefig('reports/figures/eda/latency_by_source_violin.png', dpi=300)
plt.show()
```

#### Validation Pass Rate by Complexity

```python
# Grouped bar chart
pass_rate_by_complexity = df.groupby('record_complexity')['validation_pass_bool'].agg(['sum', 'count'])
pass_rate_by_complexity['pass_rate'] = pass_rate_by_complexity['sum'] / pass_rate_by_complexity['count'] * 100

fig, ax = plt.subplots(figsize=(10, 6))
pass_rate_by_complexity['pass_rate'].plot(kind='bar', ax=ax, color=sns.color_palette("colorblind"))
ax.set_xlabel('Record Complexity')
ax.set_ylabel('Validation Pass Rate (%)')
ax.set_title('Validation Pass Rate by Record Complexity')
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.axhline(95, color='red', linestyle='--', label='Target (95%)')
ax.legend()

# Add value labels
for i, (idx, row) in enumerate(pass_rate_by_complexity.iterrows()):
    ax.text(i, row['pass_rate'] + 1, f"{row['pass_rate']:.1f}%\n(n={row['count']})", 
            ha='center', va='bottom')

plt.tight_layout()
plt.savefig('reports/figures/eda/validation_by_complexity.png', dpi=300)
plt.show()
```

#### Correlation Analysis

```python
# Select numeric columns only
numeric_cols = ['latency_sec', 'file_size_kb', 'validation_pass_bool']
# Add any other numeric variables (e.g., if you have numeric encoding for categories)

# Correlation matrix
corr_matrix = df[numeric_cols].corr()
print(corr_matrix)

# Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title('Correlation Matrix of Continuous Variables')
plt.tight_layout()
plt.savefig('reports/figures/eda/correlation_matrix.png', dpi=300)
plt.show()
```

#### Scatter Plots

```python
# File size vs latency
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(df['file_size_kb'], df['latency_sec'], 
                    c=df['data_source'].astype('category').cat.codes, 
                    alpha=0.6, s=30, cmap='tab10')
ax.set_xlabel('File Size (KB)')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Latency vs File Size (colored by Data Source)')

# Add colorbar legend
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Data Source')

# Trend line
z = np.polyfit(df['file_size_kb'], df['latency_sec'], 1)
p = np.poly1d(z)
ax.plot(df['file_size_kb'].sort_values(), p(df['file_size_kb'].sort_values()), 
        "r--", alpha=0.8, label=f'Trend: y={z[0]:.4f}x+{z[1]:.2f}')
ax.legend()

plt.tight_layout()
plt.savefig('reports/figures/eda/latency_vs_file_size_scatter.png', dpi=300)
plt.show()
```

---

### 2.3 Stratified Analysis

#### Rural vs Urban Comparison

```python
# Split violin plot
fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=df, x='rural_urban', y='latency_sec', split=True, 
               hue='data_source', ax=ax, palette="colorblind")
ax.set_xlabel('Geographic Classification')
ax.set_ylabel('Latency (seconds)')
ax.set_title('Latency Distribution: Rural vs Urban by Data Source')
plt.tight_layout()
plt.savefig('reports/figures/eda/rural_urban_comparison.png', dpi=300)
plt.show()
```

#### Health District Small Multiples

```python
# Small multiples (facet grid)
g = sns.FacetGrid(df, col='health_district', col_wrap=4, height=3, aspect=1.2)
g.map(plt.hist, 'latency_sec', bins=20, edgecolor='black')
g.set_axis_labels('Latency (seconds)', 'Frequency')
g.set_titles(col_template="{col_name}")
g.fig.suptitle('Latency Distribution by Health District', y=1.02, fontsize=16)
plt.tight_layout()
plt.savefig('reports/figures/eda/latency_by_health_district.png', dpi=300)
plt.show()
```

---

### 2.4 Missing Data Analysis

```python
import missingno as msno

# Missing data matrix
fig = msno.matrix(df, figsize=(12, 6), fontsize=10)
plt.title('Missing Data Pattern')
plt.tight_layout()
plt.savefig('reports/figures/eda/missing_data_matrix.png', dpi=300)
plt.show()

# Missing data heatmap
fig = msno.heatmap(df, figsize=(10, 8))
plt.title('Missing Data Correlation Heatmap')
plt.tight_layout()
plt.savefig('reports/figures/eda/missing_data_heatmap.png', dpi=300)
plt.show()

# Summary table
missing_summary = pd.DataFrame({
    'column': df.columns,
    'missing_count': df.isna().sum(),
    'missing_pct': df.isna().mean() * 100
}).sort_values('missing_pct', ascending=False)

print("\nMissing Data Summary:")
print(missing_summary[missing_summary['missing_pct'] > 0])
```

---

## Task 3: Normality Assessment

### Objective

Test assumption of normality for paired t-test.

### 3.1 Q-Q Plots

```python
from scipy import stats

# Create baseline comparison
manual_baseline = 1200  # 20 minutes in seconds
df['manual_latency_est'] = manual_baseline
df['latency_diff'] = df['manual_latency_est'] - df['latency_sec']

# Q-Q plot for difference scores
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Overall
stats.probplot(df['latency_diff'], dist="norm", plot=axes[0])
axes[0].set_title('Q-Q Plot: Latency Difference Scores (Overall)')
axes[0].set_xlabel('Theoretical Quantiles')
axes[0].set_ylabel('Sample Quantiles')

# By data source (example: Synthea)
synthea_diff = df[df['data_source'] == 'synthea']['latency_diff']
stats.probplot(synthea_diff, dist="norm", plot=axes[1])
axes[1].set_title('Q-Q Plot: Latency Difference Scores (Synthea Only)')
axes[1].set_xlabel('Theoretical Quantiles')
axes[1].set_ylabel('Sample Quantiles')

plt.tight_layout()
plt.savefig('reports/figures/eda/qq_plots_normality.png', dpi=300)
plt.show()
```

### 3.2 Shapiro-Wilk Test

```python
# Shapiro-Wilk test (sample if n > 5000)
sample_size = min(5000, len(df['latency_diff']))
sample_diff = df['latency_diff'].sample(sample_size, random_state=12345)

stat, p_value = stats.shapiro(sample_diff)

print(f"\nShapiro-Wilk Test for Normality:")
print(f"  Test Statistic: {stat:.6f}")
print(f"  P-value: {p_value:.6f}")

if p_value < 0.05:
    print("  ❌ Reject null hypothesis: Data is NOT normally distributed")
    print("  → Consider Wilcoxon signed-rank test as alternative")
else:
    print("  ✓ Fail to reject null: Data is consistent with normal distribution")
    print("  → Paired t-test is appropriate")

# Histogram with normal overlay
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['latency_diff'], bins=50, density=True, alpha=0.7, edgecolor='black', label='Observed')

# Fit normal distribution
mu, sigma = df['latency_diff'].mean(), df['latency_diff'].std()
x = np.linspace(df['latency_diff'].min(), df['latency_diff'].max(), 100)
ax.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', lw=2, label=f'Normal(μ={mu:.1f}, σ={sigma:.1f})')

ax.set_xlabel('Latency Difference (manual - automated, seconds)')
ax.set_ylabel('Density')
ax.set_title(f'Distribution of Difference Scores\nShapiro-Wilk p={p_value:.4f}')
ax.legend()

plt.tight_layout()
plt.savefig('reports/figures/eda/normality_histogram_overlay.png', dpi=300)
plt.show()
```

---

## Task 4: Statistical Hypothesis Testing

### Objective

Execute formal statistical tests to answer research questions.

### 4.1 Paired t-test: Latency Improvement

**Hypotheses**:
- H₀: μ_diff = 0 (no difference between manual and automated latency)
- H₁: μ_diff > 0 (automated is faster than manual)

```python
# One-sided paired t-test (automated < manual, so diff > 0)
t_stat, p_value_two_tail = stats.ttest_rel(df['manual_latency_est'], df['latency_sec'])
p_value_one_tail = p_value_two_tail / 2  # One-sided test

print("\n" + "="*60)
print("PAIRED T-TEST: LATENCY IMPROVEMENT")
print("="*60)
print(f"Sample Size: {len(df)}")
print(f"Manual Baseline (estimated): {manual_baseline} sec ({manual_baseline/60:.1f} min)")
print(f"Automated Mean: {df['latency_sec'].mean():.2f} sec")
print(f"Automated Median: {df['latency_sec'].median():.2f} sec")
print(f"Mean Difference: {df['latency_diff'].mean():.2f} sec")
print(f"\nt-statistic: {t_stat:.4f}")
print(f"p-value (one-tailed): {p_value_one_tail:.6f}")

# Decision
alpha = 0.05
if p_value_one_tail < alpha:
    print(f"\n✓ REJECT H₀ (p < {alpha})")
    print("  Conclusion: Automated pipeline is significantly faster than manual baseline")
else:
    print(f"\n❌ FAIL TO REJECT H₀ (p >= {alpha})")
    print("  Conclusion: Insufficient evidence of improvement")

# Confidence interval for mean difference
ci = stats.t.interval(0.95, len(df)-1, 
                      loc=df['latency_diff'].mean(), 
                      scale=stats.sem(df['latency_diff']))
print(f"\n95% CI for Mean Difference: [{ci[0]:.2f}, {ci[1]:.2f}] seconds")
```

### 4.2 Effect Size: Cohen's d

```python
# Cohen's d for paired samples
mean_diff = df['latency_diff'].mean()
std_diff = df['latency_diff'].std()
cohens_d = mean_diff / std_diff

print(f"\nEffect Size (Cohen's d): {cohens_d:.4f}")

# Interpretation
if cohens_d < 0.2:
    interpretation = "negligible"
elif cohens_d < 0.5:
    interpretation = "small"
elif cohens_d < 0.8:
    interpretation = "medium"
else:
    interpretation = "large"

print(f"Interpretation: {interpretation.upper()} effect")
print("\nBenchmarks (Cohen, 1988):")
print("  Small: d = 0.2")
print("  Medium: d = 0.5")
print("  Large: d = 0.8")

if cohens_d >= 0.8:
    print("\n✓ Effect size meets success threshold (d ≥ 0.8)")
else:
    print(f"\n⚠ Effect size below target (d = {cohens_d:.2f} < 0.8)")
```

### 4.3 Visualization: Before-After Plot

```python
# Paired before-after plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Box plot comparison
data_for_plot = pd.DataFrame({
    'Manual (Baseline)': df['manual_latency_est'],
    'Automated (Measured)': df['latency_sec']
})

axes[0].boxplot([data_for_plot['Manual (Baseline)'], data_for_plot['Automated (Measured)']], 
                labels=['Manual\n(Baseline)', 'Automated\n(Measured)'])
axes[0].set_ylabel('Latency (seconds)')
axes[0].set_title('Before-After Comparison')
axes[0].text(0.5, 0.95, f'p={p_value_one_tail:.6f}\nCohen\'s d={cohens_d:.2f}', 
             transform=axes[0].transAxes, ha='center', va='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Panel B: Difference distribution
axes[1].hist(df['latency_diff'], bins=50, edgecolor='black', alpha=0.7)
axes[1].axvline(0, color='red', linestyle='--', label='No Difference')
axes[1].axvline(df['latency_diff'].mean(), color='blue', linestyle='-', linewidth=2, 
                label=f'Mean Diff = {df["latency_diff"].mean():.1f}s')
axes[1].set_xlabel('Latency Difference (manual - automated, seconds)')
axes[1].set_ylabel('Frequency')
axes[1].set_title('Distribution of Improvement')
axes[1].legend()

plt.tight_layout()
plt.savefig('reports/figures/results/paired_ttest_visualization.png', dpi=300)
plt.show()
```

---

### 4.4 McNemar's Test: Validation Accuracy

**Hypotheses**:
- H₀: Proportion discordant pairs (manual pass/automated fail) = (manual fail/automated pass)
- H₁: Proportions differ (automated has better accuracy)

```python
from statsmodels.stats.contingency_tables import mcnemar

# Create contingency table
# Assume baseline validation pass rate = 85%
np.random.seed(12345)
df['manual_validation_est'] = np.random.rand(len(df)) < 0.85  # 85% pass rate

# Contingency table
contingency = pd.crosstab(df['manual_validation_est'], df['validation_pass_bool'],
                         rownames=['Manual (Baseline)'], colnames=['Automated (Measured)'])
print("\nContingency Table:")
print(contingency)

# McNemar's test
result = mcnemar(contingency, exact=False, correction=True)

print("\n" + "="*60)
print("MCNEMAR'S TEST: VALIDATION ACCURACY IMPROVEMENT")
print("="*60)
print(f"Chi-square statistic: {result.statistic:.4f}")
print(f"p-value: {result.pvalue:.6f}")

if result.pvalue < 0.05:
    print(f"\n✓ REJECT H₀ (p < 0.05)")
    print("  Conclusion: Automated validation accuracy differs significantly from manual baseline")
else:
    print(f"\n❌ FAIL TO REJECT H₀ (p >= 0.05)")
    print("  Conclusion: No significant difference in validation accuracy")

# Pass rates
manual_pass_rate = df['manual_validation_est'].mean() * 100
automated_pass_rate = df['validation_pass_bool'].mean() * 100

print(f"\nManual Pass Rate (estimated): {manual_pass_rate:.2f}%")
print(f"Automated Pass Rate (measured): {automated_pass_rate:.2f}%")
print(f"Improvement: {automated_pass_rate - manual_pass_rate:+.2f} percentage points")
```

### 4.5 Visualization: Confusion Matrix

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Confusion matrix
cm = confusion_matrix(df['manual_validation_est'], df['validation_pass_bool'])

fig, ax = plt.subplots(figsize=(8, 6))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, 
                              display_labels=['Fail', 'Pass'])
disp.plot(cmap='Blues', ax=ax, values_format='d')
ax.set_title(f'Validation Accuracy: Manual vs Automated\nMcNemar p={result.pvalue:.6f}')
ax.set_xlabel('Automated (Measured)')
ax.set_ylabel('Manual (Baseline Estimate)')

plt.tight_layout()
plt.savefig('reports/figures/results/mcnemar_confusion_matrix.png', dpi=300)
plt.show()
```

---

## Task 5: Sensitivity Analysis

### Objective

Test robustness of results across baseline assumptions.

### Baseline Range Testing

```python
# Test across baseline range (15, 20, 25, 30, 45 minutes)
baseline_range = [15, 20, 25, 30, 45]  # minutes
results = []

for baseline_min in baseline_range:
    baseline_sec = baseline_min * 60
    df['manual_latency_temp'] = baseline_sec
    df['latency_diff_temp'] = df['manual_latency_temp'] - df['latency_sec']
    
    # Paired t-test
    t_stat, p_val = stats.ttest_rel(df['manual_latency_temp'], df['latency_sec'])
    p_val_one_tail = p_val / 2
    
    # Effect size
    cohens_d_temp = df['latency_diff_temp'].mean() / df['latency_diff_temp'].std()
    
    results.append({
        'baseline_min': baseline_min,
        'baseline_sec': baseline_sec,
        't_statistic': t_stat,
        'p_value': p_val_one_tail,
        'cohens_d': cohens_d_temp,
        'significant': p_val_one_tail < 0.05
    })

results_df = pd.DataFrame(results)
print("\nSensitivity Analysis Results:")
print(results_df)

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# P-values across baseline
axes[0].plot(results_df['baseline_min'], results_df['p_value'], marker='o', linewidth=2)
axes[0].axhline(0.05, color='red', linestyle='--', label='α = 0.05')
axes[0].set_xlabel('Baseline Manual Time (minutes)')
axes[0].set_ylabel('p-value (one-tailed)')
axes[0].set_title('Statistical Significance Across Baseline Assumptions')
axes[0].legend()
axes[0].set_yscale('log')
axes[0].grid(True, alpha=0.3)

# Effect sizes across baseline
axes[1].plot(results_df['baseline_min'], results_df['cohens_d'], marker='o', linewidth=2, color='green')
axes[1].axhline(0.8, color='red', linestyle='--', label='Large Effect (d=0.8)')
axes[1].axhline(0.5, color='orange', linestyle=':', label='Medium Effect (d=0.5)')
axes[1].set_xlabel('Baseline Manual Time (minutes)')
axes[1].set_ylabel('Cohen\'s d')
axes[1].set_title('Effect Size Across Baseline Assumptions')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('reports/figures/results/sensitivity_analysis.png', dpi=300)
plt.show()

# Robustness assessment
all_significant = results_df['significant'].all()
all_large_effect = (results_df['cohens_d'] >= 0.8).all()

print(f"\nRobustness Assessment:")
print(f"  Significant across all baselines: {'✓ YES' if all_significant else '❌ NO'}")
print(f"  Large effect across all baselines: {'✓ YES' if all_large_effect else '❌ NO'}")
```

---

## Task 6: Subgroup Analysis

### Objective

Test if improvements hold across different data types and complexities.

### By Data Source

```python
# Forest plot data
subgroup_results = []

for source in df['data_source'].unique():
    subset = df[df['data_source'] == source]
    
    # Skip if too few samples
    if len(subset) < 30:
        continue
    
    # Paired t-test
    t_stat, p_val = stats.ttest_rel(subset['manual_latency_est'], subset['latency_sec'])
    p_val_one_tail = p_val / 2
    
    # Effect size
    mean_diff = subset['latency_diff'].mean()
    std_diff = subset['latency_diff'].std()
    cohens_d = mean_diff / std_diff
    
    # CI for Cohen's d (approximation)
    n = len(subset)
    se_d = np.sqrt((n-1)/(n-3)) * np.sqrt((1/n) + (cohens_d**2)/(2*n))
    ci_lower = cohens_d - 1.96 * se_d
    ci_upper = cohens_d + 1.96 * se_d
    
    subgroup_results.append({
        'subgroup': source,
        'n': n,
        'cohens_d': cohens_d,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'p_value': p_val_one_tail
    })

subgroup_df = pd.DataFrame(subgroup_results)
print("\nSubgroup Analysis by Data Source:")
print(subgroup_df)

# Forest plot
fig, ax = plt.subplots(figsize=(10, 6))

y_pos = np.arange(len(subgroup_df))
ax.errorbar(subgroup_df['cohens_d'], y_pos, 
            xerr=[subgroup_df['cohens_d'] - subgroup_df['ci_lower'],
                  subgroup_df['ci_upper'] - subgroup_df['cohens_d']],
            fmt='o', markersize=8, capsize=5, linewidth=2)

ax.set_yticks(y_pos)
ax.set_yticklabels([f"{row['subgroup']} (n={row['n']})" for _, row in subgroup_df.iterrows()])
ax.set_xlabel('Cohen\'s d (95% CI)')
ax.set_title('Effect Size by Data Source (Forest Plot)')
ax.axvline(0, color='gray', linestyle='--', linewidth=1)
ax.axvline(0.8, color='red', linestyle=':', linewidth=1, label='Large Effect Threshold')
ax.legend()
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('reports/figures/results/forest_plot_by_source.png', dpi=300)
plt.show()
```

---

## Task 7: Results Export and Documentation

### Objective

Save results for reporting and sharing.

### Export Statistical Results

```python
# Compile all results
final_results = {
    'sample_size': len(df),
    'manual_baseline_sec': manual_baseline,
    'automated_mean_sec': df['latency_sec'].mean(),
    'automated_median_sec': df['latency_sec'].median(),
    'automated_p50_sec': df['latency_sec'].quantile(0.5),
    'automated_p95_sec': df['latency_sec'].quantile(0.95),
    'mean_improvement_sec': df['latency_diff'].mean(),
    'paired_ttest_statistic': t_stat,
    'paired_ttest_pvalue_one_tail': p_value_one_tail,
    'cohens_d': cohens_d,
    'meets_p50_threshold': df['latency_sec'].quantile(0.5) <= 30,
    'meets_p95_threshold': df['latency_sec'].quantile(0.95) <= 120,
    'manual_validation_rate': manual_pass_rate / 100,
    'automated_validation_rate': automated_pass_rate / 100,
    'validation_improvement_pp': automated_pass_rate - manual_pass_rate,
    'mcnemar_chi2': result.statistic,
    'mcnemar_pvalue': result.pvalue,
    'meets_validation_threshold': automated_pass_rate >= 95
}

# Save to CSV
results_table = pd.DataFrame([final_results])
results_table.to_csv('reports/statistical_results.csv', index=False)
print("\n✓ Results saved to: reports/statistical_results.csv")

# Pretty print summary
print("\n" + "="*60)
print("FINAL RESULTS SUMMARY")
print("="*60)
for key, value in final_results.items():
    print(f"{key}: {value}")
```

---

## Completion Criteria

Phase 7 is complete when:

- ✅ EDA completed with 15-20 visualizations saved to `reports/figures/eda/`
- ✅ Normality assessed (Q-Q plots, Shapiro-Wilk test)
- ✅ Paired t-test executed with p-value and effect size
- ✅ McNemar's test executed for validation accuracy
- ✅ Sensitivity analysis across baseline range (15-45 min)
- ✅ Subgroup analysis by data source and complexity
- ✅ Statistical results exported to `reports/statistical_results.csv`
- ✅ Publication-ready figures saved (300 DPI PNG)
- ✅ Assumptions validated or violations documented

---

## Rubric Alignment

**WGU D610 Capstone Rubric Requirements:**

| Criterion | Phase 7 Coverage |
|-----------|------------------|
| **F1: Visualizations** | 25+ plots (EDA + results) |
| **F2: Statistical Tests** | Paired t-test, McNemar's, normality tests |
| **F3: Effect Sizes** | Cohen's d with interpretation |
| **F4: Assumption Checking** | Q-Q plots, Shapiro-Wilk, sensitivity analysis |
| **G1: Results Interpretation** | Documented in results summary |

---

**Next Steps After Phase 7:**
- Phase 8: Results interpretation and discussion
- Phase 9: Report writing and compilation
- Phase 10: Defense preparation

---

**Status**: Ready to execute analysis  
**Prerequisites**: `data/processed/combined_data.parquet` must exist (from Phase 3 cleaning)
