"""
Visualization module for creating publication-ready figures.

This module provides functions for generating static and interactive
visualizations for results presentation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, List
import warnings

warnings.filterwarnings('ignore')


def create_executive_summary(
    df: pd.DataFrame,
    results: Dict,
    output_dir: str = 'reports/figures/publication'
) -> str:
    """
    Create 4-panel executive summary figure.
    
    Args:
        df: DataFrame with processed data
        results: Dictionary with statistical results
        output_dir: Directory to save figure
        
    Returns:
        Path to saved figure
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Configure for publication
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'serif'
    
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Panel A: Latency comparison
    ax1 = fig.add_subplot(gs[0, 0])
    manual_baseline = results.get('manual_baseline_sec', 1200)
    data_for_box = [
        [manual_baseline] * len(df),
        df['latency_sec'].values
    ]
    bp = ax1.boxplot(data_for_box, labels=['Manual\n(Baseline)', 'Automated\n(Measured)'],
                     patch_artist=True, widths=0.6)
    bp['boxes'][0].set_facecolor('lightcoral')
    bp['boxes'][1].set_facecolor('lightgreen')
    ax1.set_ylabel('Latency (seconds)', fontweight='bold')
    ax1.set_title('A. Processing Speed', fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    if 'speedup_factor' in results:
        speedup = results['speedup_factor']
        ax1.text(0.5, 0.95, f'{speedup:.1f}x Faster',
                transform=ax1.transAxes, ha='center', va='top',
                fontsize=14, fontweight='bold', color='green',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Panel B: Validation accuracy
    ax2 = fig.add_subplot(gs[0, 1])
    manual_val = results.get('manual_pass_rate', 0.85) * 100
    auto_val = results.get('automated_pass_rate', 0.95) * 100
    
    bars = ax2.bar(['Manual\n(Baseline)', 'Automated\n(Measured)'],
                   [manual_val, auto_val],
                   color=['lightcoral', 'lightgreen'],
                   edgecolor='black', linewidth=1.5)
    ax2.axhline(95, color='red', linestyle='--', linewidth=2,
               label='Target (95%)', alpha=0.7)
    ax2.set_ylabel('Validation Pass Rate (%)', fontweight='bold')
    ax2.set_title('B. Validation Accuracy', fontweight='bold', pad=10)
    ax2.set_ylim([0, 105])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.1f}%', ha='center', va='bottom',
                fontweight='bold', fontsize=11)
    
    # Panel C: Threshold achievement
    ax3 = fig.add_subplot(gs[1, 0])
    p50 = df['latency_sec'].quantile(0.5)
    p95 = df['latency_sec'].quantile(0.95)
    
    thresholds = pd.DataFrame({
        'Metric': ['P50\n(≤30s)', 'P95\n(≤120s)', 'Validation\n(≥95%)'],
        'Target': [30, 120, 95],
        'Actual': [p50, p95, auto_val]
    })
    
    y_pos = np.arange(len(thresholds))
    ax3.barh(y_pos, thresholds['Target'], color='lightgray',
            alpha=0.5, label='Target', edgecolor='black', linewidth=1)
    
    colors = []
    for i, (a, t) in enumerate(zip(thresholds['Actual'], thresholds['Target'])):
        if i == 2:  # Validation (higher is better)
            colors.append('green' if a >= t else 'orange')
        else:  # Latency (lower is better)
            colors.append('green' if a <= t else 'orange')
    
    ax3.barh(y_pos, thresholds['Actual'], color=colors,
            label='Actual', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(thresholds['Metric'])
    ax3.set_xlabel('Value', fontweight='bold')
    ax3.set_title('C. Success Thresholds', fontweight='bold', pad=10)
    ax3.legend(loc='lower right')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Panel D: Data distribution
    ax4 = fig.add_subplot(gs[1, 1])
    source_counts = df['data_source'].value_counts()
    colors_pie = sns.color_palette("colorblind", len(source_counts))
    ax4.pie(source_counts.values, labels=source_counts.index,
           autopct='%1.1f%%', startangle=90, colors=colors_pie,
           textprops={'fontsize': 9, 'weight': 'bold'})
    ax4.set_title(f'D. Data Sources (n={len(df):,})',
                 fontweight='bold', pad=10)
    
    fig.suptitle('Serverless FHIR Pipeline: Executive Summary',
                fontsize=16, fontweight='bold', y=0.98)
    
    # Save in multiple formats
    filepath_png = output_path / 'executive_summary.png'
    filepath_pdf = output_path / 'executive_summary.pdf'
    filepath_svg = output_path / 'executive_summary.svg'
    
    plt.savefig(filepath_png, dpi=300, bbox_inches='tight')
    plt.savefig(filepath_pdf, bbox_inches='tight')
    plt.savefig(filepath_svg, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved executive summary (PNG, PDF, SVG)")
    return str(filepath_png)


def create_interactive_dashboard(
    df: pd.DataFrame,
    output_dir: str = 'reports/figures/interactive'
) -> str:
    """
    Create interactive Plotly dashboard.
    
    Args:
        df: DataFrame with processed data
        output_dir: Directory to save HTML file
        
    Returns:
        Path to saved HTML file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Latency by Source', 'Latency vs File Size',
                       'Cumulative Distribution', 'Performance Timeline'),
        specs=[[{'type': 'box'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'scatter'}]]
    )
    
    # Panel 1: Box plot by source
    for source in df['data_source'].unique():
        source_data = df[df['data_source'] == source]['latency_sec']
        fig.add_trace(
            go.Box(y=source_data, name=source.title(), boxmean='sd'),
            row=1, col=1
        )
    
    # Panel 2: Scatter (latency vs file size)
    fig.add_trace(
        go.Scatter(
            x=df['file_size_kb'],
            y=df['latency_sec'],
            mode='markers',
            marker=dict(size=5, opacity=0.6,
                       color=df['data_source'].astype('category').cat.codes,
                       colorscale='Viridis', showscale=True),
            text=df['data_source'],
            hovertemplate='<b>%{text}</b><br>Size: %{x:.1f} KB<br>Latency: %{y:.2f}s<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Panel 3: CDF
    sorted_latency = np.sort(df['latency_sec'])
    cdf = np.arange(1, len(sorted_latency) + 1) / len(sorted_latency) * 100
    
    fig.add_trace(
        go.Scatter(x=sorted_latency, y=cdf, mode='lines',
                  line=dict(color='steelblue', width=2),
                  hovertemplate='Latency: %{x:.2f}s<br>Percentile: %{y:.1f}%<extra></extra>'),
        row=2, col=1
    )
    
    # Panel 4: Timeline
    df_sample = df.sample(min(1000, len(df)), random_state=12345).copy()
    df_sample = df_sample.sort_values('latency_sec').reset_index(drop=True)
    
    fig.add_trace(
        go.Scatter(
            x=df_sample.index,
            y=df_sample['latency_sec'],
            mode='markers',
            marker=dict(size=4, opacity=0.6,
                       color=df_sample['latency_sec'],
                       colorscale='RdYlGn_r'),
            hovertemplate='Record: %{x}<br>Latency: %{y:.2f}s<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_xaxes(title_text="Data Source", row=1, col=1)
    fig.update_xaxes(title_text="File Size (KB)", row=1, col=2)
    fig.update_xaxes(title_text="Latency (seconds)", row=2, col=1)
    fig.update_xaxes(title_text="Record Index", row=2, col=2)
    
    fig.update_yaxes(title_text="Latency (seconds)", row=1, col=1)
    fig.update_yaxes(title_text="Latency (seconds)", row=1, col=2)
    fig.update_yaxes(title_text="Cumulative %", row=2, col=1)
    fig.update_yaxes(title_text="Latency (seconds)", row=2, col=2)
    
    fig.update_layout(
        title_text="Interactive Performance Dashboard",
        title_font_size=18,
        showlegend=False,
        height=800
    )
    
    filepath = output_path / 'performance_dashboard.html'
    fig.write_html(filepath)
    
    print(f"✓ Saved interactive dashboard: {filepath}")
    return str(filepath)


def create_publication_figures(
    df: pd.DataFrame,
    results: Dict,
    output_dir: str = 'reports/figures/publication'
) -> List[str]:
    """
    Create all publication-ready figures.
    
    Args:
        df: DataFrame with processed data
        results: Dictionary with statistical results
        output_dir: Directory to save figures
        
    Returns:
        List of saved figure paths
    """
    print("\n" + "=" * 70)
    print("CREATING PUBLICATION FIGURES")
    print("=" * 70)
    
    saved_files = []
    
    # Executive summary
    filepath = create_executive_summary(df, results, output_dir)
    saved_files.append(filepath)
    
    # Interactive dashboard
    interactive_dir = str(Path(output_dir).parent / 'interactive')
    filepath = create_interactive_dashboard(df, interactive_dir)
    saved_files.append(filepath)
    
    print(f"\n✓ Created {len(saved_files)} publication figures")
    return saved_files


if __name__ == '__main__':
    # Example usage
    from .run_eda import load_and_validate_data
    from .run_statistical_tests import paired_t_test, calculate_effect_size
    
    df = load_and_validate_data()
    
    # Get results
    ttest_results = paired_t_test(df)
    effect_results = calculate_effect_size(df)
    results = {**ttest_results, **effect_results}
    
    # Create figures
    create_publication_figures(df, results)
    
    print("\n✓ Visualization complete!")
