# Phase 6 Instructions: Reproducible Implementation Setup

**Issue**: #7  
**Status**: In Progress  
**Goal**: Create complete reproducible analysis environment with notebooks, scripts, Makefile, and configuration

---

## Overview

Phase 6 transforms our project from "documentation and data" to a **fully executable analysis pipeline**:

1. **Jupyter Notebooks**: Interactive EDA and statistical analysis
2. **Analysis Scripts**: Programmatic pipeline execution
3. **Makefile**: One-command reproducibility (`make all`)
4. **Environment Management**: Locked dependencies for reproducibility
5. **Visualization Framework**: Publication-ready plots and dashboards
6. **CI/Smoke Tests**: Automated validation

This phase delivers a **working analysis pipeline** that anyone can run.

---

## Task 1: Jupyter Notebook Setup

### Objective

Create analysis notebooks for interactive exploration and statistical testing.

### Notebooks to Create

#### 1. `notebooks/01_exploratory_data_analysis.ipynb`

**Purpose**: Data profiling, visualization, assumption checking

**Sections**:
1. **Setup & Data Loading**
   - Import libraries (pandas, numpy, matplotlib, seaborn)
   - Load `data/processed/combined_data.parquet`
   - Display data shape, types, memory usage

2. **Univariate Analysis**
   - Distribution plots for continuous variables (latency_sec, file_size_kb)
   - Bar charts for categorical variables (data_source, record_complexity, rural_urban)
   - Summary statistics (mean, median, std, min, max, quartiles)
   - Missing data heatmap

3. **Bivariate Analysis**
   - Latency by data source (boxplot, violin plot)
   - Validation pass rate by complexity (grouped bar chart)
   - Correlation matrix heatmap
   - Scatter plots: file_size_kb vs latency_sec

4. **Stratification Analysis**
   - Health district comparison (small multiples)
   - Rural vs urban performance (side-by-side distributions)
   - Data type comparison (structured vs semi-structured vs unstructured vs imaging)

5. **Normality Assessment**
   - Q-Q plots for latency_sec (overall and by data_source)
   - Histograms with normal overlay
   - Shapiro-Wilk test results table
   - Log transformation exploration if needed

6. **Outlier Detection**
   - Boxplots with outlier annotation
   - Z-score distribution
   - IQR-based flagging visualization
   - Decision: keep, transform, or investigate

**Visualizations** (~15-20 plots):
- Histograms, KDE plots, boxplots, violin plots
- Bar charts, heatmaps, scatter plots
- Q-Q plots, small multiples
- Color palette: seaborn colorblind palette for accessibility

---

#### 2. `notebooks/02_statistical_analysis.ipynb`

**Purpose**: Hypothesis testing, effect size calculation, sensitivity analysis

**Sections**:
1. **Setup & Baseline Comparison**
   - Load processed data
   - Create baseline comparison dataset (manual estimates vs automated measurements)
   - Paired structure validation

2. **Paired t-test: Latency**
   - Normality check (Shapiro-Wilk on difference scores)
   - Paired t-test execution: `scipy.stats.ttest_rel()`
   - Cohen's d calculation
   - Confidence intervals
   - Visualization: before-after plot, difference distribution

3. **McNemar's Test: Validation Accuracy**
   - Contingency table (manual pass/fail vs automated pass/fail)
   - McNemar's test: `statsmodels.stats.contingency_tables.mcnemar()`
   - Effect size (odds ratio)
   - Visualization: stacked bar chart, confusion matrix

4. **Sensitivity Analysis**
   - Test across baseline range (15, 20, 25, 30, 45 min)
   - Plot p-values and effect sizes vs baseline assumption
   - Robustness assessment

5. **Subgroup Analysis**
   - Paired t-test by data_source (4 separate tests)
   - Paired t-test by record_complexity (3 levels)
   - Forest plot of effect sizes across subgroups

6. **Assumption Violations & Alternatives**
   - If normality violated: Wilcoxon signed-rank test
   - If paired structure violated: Independent t-test (sanity check)
   - Comparison of parametric vs non-parametric results

7. **Results Summary**
   - Summary table: test statistic, p-value, effect size, CI
   - Interpretation narrative
   - Export results to `reports/statistical_results.csv`

**Visualizations** (~10-12 plots):
- Q-Q plots, before-after plots, difference distributions
- Contingency tables, confusion matrices
- Sensitivity analysis curves
- Forest plots for subgroup effects

---

#### 3. `notebooks/03_visualization_dashboard.ipynb`

**Purpose**: Publication-ready figures and interactive dashboards

**Sections**:
1. **Figure 1: Data Acquisition Summary**
   - 4-panel plot showing volume by source
   - Timeline of data coverage
   - Missingness summary heatmap
   - Geographic coverage map (Virginia health districts)

2. **Figure 2: Performance Comparison**
   - Main result plot: Manual vs Automated latency (boxplot + violin)
   - Validation accuracy comparison (grouped bar chart)
   - Cost per record comparison (bar chart with error bars)
   - Reliability metrics (gauge charts)

3. **Figure 3: Statistical Results**
   - Paired t-test results visualization
   - Effect size magnitude (Cohen's d benchmarks)
   - Confidence interval plot
   - P-value annotation

4. **Figure 4: Subgroup Analysis**
   - Latency by data source (4-panel boxplot)
   - Complexity stratification (violin plots)
   - Rural vs urban comparison (split violin)
   - Small multiples by health district

5. **Interactive Dashboard** (Optional - Plotly/Dash)
   - Dropdown filters: data_source, complexity, health_district
   - Dynamic latency distribution
   - Real-time success threshold checking
   - Export to HTML for presentation

**Export Formats**:
- High-res PNG (300 DPI) for paper
- SVG for vector graphics
- PDF for slides
- HTML for interactive viewing

---

### Notebook Best Practices

**Code Organization**:
```python
# Standard imports at top
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import plotly.express as px

# Set visual defaults
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12

# Reproducibility
np.random.seed(12345)
```

**Documentation**:
- Markdown cells explaining each analysis step
- Inline comments for complex code
- Interpretation after each statistical test
- References to proposal/hypothesis alignment

**Reproducibility**:
- No hardcoded paths (use `Path(__file__).parent` or config)
- Random seeds set
- Package versions documented
- Data checksums validated

---

## Task 2: Analysis Scripts (Programmatic Execution)

### Objective

Create Python scripts for non-interactive, reproducible analysis execution.

### Scripts to Create

#### 1. `src/analysis/run_eda.py`

**Purpose**: Generate all EDA plots programmatically

**Functions**:
```python
def plot_univariate_distributions(df, output_dir):
    """Generate histograms and KDE plots for all continuous variables."""
    
def plot_bivariate_relationships(df, output_dir):
    """Create scatter plots and correlation heatmap."""
    
def plot_stratified_analysis(df, output_dir):
    """Boxplots/violin plots by categorical variables."""
    
def check_normality(df, output_dir):
    """Q-Q plots and Shapiro-Wilk test results."""
    
def generate_eda_report(df):
    """Compile all EDA into markdown report."""
```

**Usage**:
```bash
python -m src.analysis.run_eda --data data/processed/combined_data.parquet --output reports/figures/
```

---

#### 2. `src/analysis/run_statistical_tests.py`

**Purpose**: Execute hypothesis tests and save results

**Functions**:
```python
def paired_ttest_latency(df):
    """Paired t-test for latency_sec."""
    
def mcnemar_test_validation(df):
    """McNemar's test for validation_pass_bool."""
    
def calculate_effect_sizes(df):
    """Cohen's d, odds ratios."""
    
def sensitivity_analysis(df, baseline_range):
    """Test across baseline assumptions."""
    
def subgroup_analysis(df, groupby_col):
    """Stratified tests by data_source, complexity."""
    
def export_results(results, output_path):
    """Save to CSV and JSON."""
```

**Usage**:
```bash
python -m src.analysis.run_statistical_tests --data data/processed/combined_data.parquet --output reports/statistical_results.csv
```

---

#### 3. `src/visualization/plot_results.py`

**Purpose**: Generate publication-ready figures

**Functions**:
```python
def plot_main_results(df, output_dir):
    """Figure 2: Performance comparison plots."""
    
def plot_statistical_results(results, output_dir):
    """Figure 3: T-test results with effect sizes."""
    
def plot_subgroup_forest(results, output_dir):
    """Figure 4: Forest plot of subgroup effects."""
    
def create_dashboard(df, output_path):
    """Interactive Plotly dashboard."""
```

**Usage**:
```bash
python -m src.visualization.plot_results --data data/processed/combined_data.parquet --results reports/statistical_results.csv --output reports/figures/
```

---

## Task 3: Makefile for Reproducible Workflows

### Objective

One-command execution of entire pipeline.

### Makefile Targets

```makefile
.PHONY: all data clean analyze visualize test help

# Default target
all: data clean analyze visualize

# Data acquisition
data:
	@echo "Downloading and generating data..."
	python -m src.pipeline.data_acquisition --all

# Data cleaning
clean:
	@echo "Cleaning and processing data..."
	python -m src.pipeline.data_cleaning --all
	@echo "Generating quality report..."
	python -m src.pipeline.data_cleaning --report

# Statistical analysis
analyze:
	@echo "Running EDA..."
	python -m src.analysis.run_eda --data data/processed/combined_data.parquet --output reports/figures/eda/
	@echo "Running statistical tests..."
	python -m src.analysis.run_statistical_tests --data data/processed/combined_data.parquet --output reports/statistical_results.csv

# Visualization
visualize:
	@echo "Generating publication figures..."
	python -m src.visualization.plot_results --data data/processed/combined_data.parquet --results reports/statistical_results.csv --output reports/figures/

# Run Jupyter notebooks (non-interactive)
notebooks:
	@echo "Executing notebooks..."
	jupyter nbconvert --execute --to html notebooks/01_exploratory_data_analysis.ipynb --output-dir reports/
	jupyter nbconvert --execute --to html notebooks/02_statistical_analysis.ipynb --output-dir reports/
	jupyter nbconvert --execute --to html notebooks/03_visualization_dashboard.ipynb --output-dir reports/

# Run tests
test:
	@echo "Running schema validation tests..."
	pytest tests/test_schema.py -v
	@echo "Running statistical assumption tests..."
	pytest tests/test_assumptions.py -v

# Clean generated files
clean-all:
	rm -rf data/interim/* data/processed/* reports/figures/* reports/*.html

# Help
help:
	@echo "Available targets:"
	@echo "  make data       - Download/generate all data sources"
	@echo "  make clean      - Clean and process raw data"
	@echo "  make analyze    - Run EDA and statistical tests"
	@echo "  make visualize  - Generate publication figures"
	@echo "  make notebooks  - Execute Jupyter notebooks"
	@echo "  make test       - Run validation tests"
	@echo "  make all        - Run full pipeline (data → clean → analyze → visualize)"
	@echo "  make clean-all  - Remove all generated files"
```

**Usage**:
```bash
make all              # Full pipeline
make data             # Just data acquisition
make analyze          # Just analysis (assumes data exists)
make test             # Validation checks
```

---

## Task 4: Environment Management

### Objective

Lock all dependencies for reproducibility.

### Update `requirements.txt`

Add analysis and visualization packages:

```txt
# Existing packages
pandas>=2.1.0
numpy>=1.24.0

# Data acquisition
xport>=3.3.0          # NHANES XPT parsing

# Data validation
great-expectations>=0.18.0

# Statistical analysis
scipy>=1.11.0
statsmodels>=0.14.0
scikit-learn>=1.3.0

# Visualization
matplotlib>=3.8.0
seaborn>=0.13.0
plotly>=5.18.0
kaleido>=0.2.1        # Static image export for Plotly

# Jupyter
jupyter>=1.0.0
jupyterlab>=4.0.0
ipykernel>=6.25.0
nbconvert>=7.9.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Code quality
black>=23.9.0
flake8>=6.1.0
mypy>=1.5.0

# Utilities
python-dotenv>=1.0.0  # Environment variable management
tqdm>=4.66.0          # Progress bars
```

### Update `pyproject.toml`

Add tool configurations:

```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "--verbose --cov=src --cov-report=html"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "notebooks/*"]
```

---

## Task 5: CI Smoke Tests

### Objective

Automated validation that pipeline runs without errors.

### Create `tests/test_assumptions.py`

```python
"""Test statistical assumptions before analysis."""
import pandas as pd
import pytest
from pathlib import Path
from scipy import stats

DATA_PATH = Path("data/processed/combined_data.parquet")

@pytest.fixture
def df():
    """Load processed data."""
    return pd.read_parquet(DATA_PATH)

def test_data_exists(df):
    """Check that processed data file exists and loads."""
    assert len(df) > 0
    assert df is not None

def test_required_columns(df):
    """Check that all analysis variables are present."""
    required = [
        'latency_sec', 
        'validation_pass_bool', 
        'data_source', 
        'record_complexity',
        'file_size_kb'
    ]
    for col in required:
        assert col in df.columns, f"Missing required column: {col}"

def test_no_missing_outcomes(df):
    """Check that DVs have no missing values."""
    assert df['latency_sec'].notna().all()
    assert df['validation_pass_bool'].notna().all()

def test_latency_range(df):
    """Check that latency values are reasonable."""
    assert (df['latency_sec'] > 0).all()
    assert (df['latency_sec'] < 600).all()  # <10 min (sanity check)

def test_validation_boolean(df):
    """Check that validation is truly boolean."""
    assert df['validation_pass_bool'].dtype == bool

def test_sample_size(df):
    """Check that we have sufficient sample size for power."""
    assert len(df) >= 800, "Sample size below power analysis target"

def test_normality_assumption(df):
    """Test normality of latency difference scores (log note if violated)."""
    # Create difference scores (manual baseline - automated)
    manual_baseline = 1200  # 20 minutes in seconds
    diff = manual_baseline - df['latency_sec']
    
    # Shapiro-Wilk test
    stat, p = stats.shapiro(diff.sample(min(5000, len(diff))))
    
    if p < 0.05:
        pytest.skip(f"Normality violated (p={p:.4f}), use non-parametric test")
    else:
        assert True  # Pass if normal
```

### GitHub Actions CI (Optional)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run schema tests
      run: pytest tests/test_schema.py -v
    
    - name: Check code formatting
      run: black --check src/
```

---

## Task 6: Directory Organization

### Final Structure

```
wgu-capstone/
├── data/
│   ├── raw/                  # Never modify
│   ├── interim/              # Cleaning stages
│   ├── processed/            # Analysis-ready
│   └── README.md
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_statistical_analysis.ipynb
│   └── 03_visualization_dashboard.ipynb
├── src/
│   ├── pipeline/
│   │   ├── data_acquisition.py
│   │   └── data_cleaning.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── run_eda.py
│   │   └── run_statistical_tests.py
│   └── visualization/
│       ├── __init__.py
│       └── plot_results.py
├── tests/
│   ├── test_schema.py
│   └── test_assumptions.py
├── reports/
│   ├── figures/
│   │   ├── eda/
│   │   └── results/
│   └── statistical_results.csv
├── Makefile
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Completion Criteria

Phase 6 is complete when:

- ✅ 3 Jupyter notebooks created with full analysis workflows
- ✅ Analysis scripts (`run_eda.py`, `run_statistical_tests.py`) functional
- ✅ Visualization script (`plot_results.py`) generates publication figures
- ✅ Makefile with `data`, `clean`, `analyze`, `visualize`, `test` targets
- ✅ `requirements.txt` updated with all analysis packages
- ✅ `tests/test_assumptions.py` with normality, sample size, data quality checks
- ✅ Can run `make all` from clean repository and generate full results
- ✅ Notebooks execute without errors (`make notebooks`)

---

## Rubric Alignment

**WGU D610 Capstone Rubric Requirements:**

| Criterion | Phase 6 Coverage |
|-----------|------------------|
| **E1: Reproducibility** | Makefile + requirements.txt ensure anyone can replicate |
| **E2: Code Quality** | Black formatting, type hints, docstrings |
| **E3: Documentation** | Jupyter notebooks with markdown explanations |
| **F1: Visualizations** | 15-20 EDA plots + 10-12 results plots |
| **F2: Statistical Tests** | Paired t-test, McNemar's test implemented |

---

**Next Steps After Phase 6:**
- Phase 7: Execute EDA and analysis (run the notebooks/scripts created here)
- Phase 8: Results interpretation and writing
- Phase 9: Report compilation
- Phase 10: Defense preparation

---

**Status**: Ready to implement notebooks and scripts  
**Priority**: Create EDA notebook template first (foundation for all analysis)
