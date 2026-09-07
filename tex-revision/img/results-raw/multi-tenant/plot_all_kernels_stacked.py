#!/usr/bin/env python3
"""
Plot the audited historical single-round policy comparison (n=1 per config).

Visualization:
- Bottom segment: min(high_latency_s, low_latency_s) from the recorded durations
- Top segment: absolute difference of those recorded durations
- Total height: max(high_latency_s, low_latency_s), a completion-time proxy

The scheduler launcher records the low duration after waiting for high, so
these segments cannot recover true overlap or independent tenant finish times.
Scheduler engagement was not verified. This figure supplies no variance or
confidence intervals, statistical-significance or scheduler-ineffectiveness
claim. The memory-file no-policy row is the historical common reference; the
scheduler's separate no-policy row is not a matched repeated control here.
Twice the single-process duration is a sequential reference, not a lower bound.
See docs/eval/rq3-revision-audit.md for the source-selection and evidence limits.

Usage:
    python plot_all_kernels_stacked.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# The 16-inch source is intended for a roughly 7-inch, full-width paper figure:
# 18--20 pt source labels become approximately 7.9--8.8 pt before tight cropping.
# Final rendered bounding-box and print-size inspection remain necessary.
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 18,
    'axes.labelsize': 20,
    'axes.titlesize': 20,
    'legend.fontsize': 18,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'figure.dpi': 150,
})

# Selected configurations to plot (policy, high_param, low_param, label, is_sched)
SELECTED_CONFIGS = [
    ('no_policy', None, None, 'No Policy', False),
    ('sched_timeslice', 1000000, 200, 'Scheduler*', True),
    ('prefetch_pid_tree', 0, 20, 'Prefetch(0,20)', False),
    ('prefetch_pid_tree', 20, 80, 'Prefetch(20,80)', False),
    ('prefetch_eviction_pid', 20, 80, 'Evict(20,80)', False),
]

# Complete source files selected by docs/eval/rq3-revision-audit.md. Never choose
# a run by modification time or silently substitute a different/incomplete CSV.
HISTORICAL_SOURCES = [
    ('HotSpot', 'results_hotspot/policy_comparison_20251208_101609.csv',
     'results_hotspot/sched_comparison_20251208_113441.csv'),
    ('GEMM', 'results_gemm/policy_comparison_20251208_102321.csv',
     'results_gemm/sched_comparison_20251208_113846.csv'),
    ('K-Means', 'results_kmeans/policy_comparison_20251208_103714.csv',
     'results_kmeans/sched_comparison_20251208_114516.csv'),
]


def load_data(csv_path):
    """Load one fixed historical CSV, rejecting changed repetition semantics."""
    df = pd.read_csv(csv_path)
    if df.empty or not df['round'].eq(1).all():
        raise ValueError(f'Expected historical round=1 rows: {csv_path}')
    return df


def get_selected_rows(df, sched_df=None):
    """Filter dataframe to only selected configurations."""
    rows = []
    for policy, hp, lp, label, is_sched in SELECTED_CONFIGS:
        source_df = sched_df if is_sched else df
        if source_df is None:
            raise ValueError(f'Missing source for {label}')
        if policy == 'no_policy':
            row = source_df[source_df['policy'] == 'no_policy']
        else:
            row = source_df[(source_df['policy'] == policy) &
                     (source_df['high_param'] == hp) &
                     (source_df['low_param'] == lp)]
        if len(row) != 1:
            raise ValueError(f'Expected exactly one historical row for {label}')
        r = row.iloc[0].to_dict()
        if not all(np.isfinite(r[key]) and r[key] > 0
                   for key in ('high_latency_s', 'low_latency_s')):
            raise ValueError(f'Invalid recorded duration for {label}')
        r['label'] = label
        rows.append(r)
    return rows


def print_improvements(data, sched_data):
    """Print descriptive arithmetic, not repeated or engaged-policy evidence."""
    print("\n" + "=" * 80)
    print("HISTORICAL SINGLE-ROUND DIFFERENCES (vs memory-file No Policy)")
    print("=" * 80)
    print("n=1/configuration; no CI, significance or scheduler-ineffectiveness claim.")
    print("Scheduler* engagement unverified; scheduler control is a separate run.")

    for kernel_name, df in data.items():
        print(f"\n### {kernel_name} ###")
        sched_df = sched_data.get(kernel_name)
        rows = get_selected_rows(df, sched_df)

        baseline = None
        for r in rows:
            if r['label'] == 'No Policy':
                baseline = r
                break

        if baseline is None:
            print("  No baseline found")
            continue

        baseline_total = max(baseline['high_latency_s'], baseline['low_latency_s'])

        print(f"  {'Config':<20} {'Min(s)':<10} {'AbsDiff(s)':<10} {'Max(s)':<10} {'Reduction':<12}")
        print(f"  {'-'*62}")

        for r in rows:
            high = r['high_latency_s']
            low = r['low_latency_s']
            min_duration = min(high, low)
            duration_difference = abs(high - low)
            total = max(high, low)
            total_impr = (baseline_total - total) / baseline_total * 100

            print(f"  {r['label']:<20} {min_duration:<10.1f} {duration_difference:<10.1f} {total:<10.1f} {total_impr:>+10.1f}%")


def plot_kernel_subplot(ax, df, kernel_name, sched_df=None):
    """Plot a single kernel's data with stacked bars."""
    rows = get_selected_rows(df, sched_df)

    if not rows:
        ax.set_title(f"{kernel_name} (No Data)")
        return ax

    labels = [r['label'] for r in rows]

    # Arithmetic decomposition only: recorded durations do not prove overlap.
    min_durations = []
    duration_differences = []

    for r in rows:
        high = r['high_latency_s']
        low = r['low_latency_s']
        min_durations.append(min(high, low))
        duration_differences.append(abs(high - low))

    x = np.arange(len(labels))
    width = 0.6

    # Plot stacked bars
    ax.bar(x, min_durations, width,
           label='Min. recorded duration', color='#e74c3c', alpha=0.85)
    ax.bar(x, duration_differences, width, bottom=min_durations,
           label='Absolute duration difference', color='#3498db', alpha=0.85)

    # Add baseline lines
    single_1x = df[df['policy'] == 'single_1x']['high_latency_s'].values

    if len(single_1x) > 0:
        ax.axhline(y=single_1x[0], color='#2ecc71', linestyle='--', linewidth=2.5,
                   label='Single 1x')
        # A sequential reference, not a concurrent lower bound or optimum.
        sequential_reference = single_1x[0] * 2
        ax.axhline(y=sequential_reference, color='#9b59b6', linestyle='--', linewidth=2.5,
                   label='2×Single: sequential reference')

    ax.set_ylabel('Completion-time proxy (s)')
    ax.set_title(kernel_name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha='right')

    # Set y-axis limit with some padding
    max_val = max(b + s for b, s in zip(min_durations, duration_differences))
    ax.set_ylim(0, max_val * 1.15)

    return ax


def main():
    base_dir = Path(__file__).parent
    # Data lives in the eval directory, not in the paper repo
    data_dir = base_dir.parents[3] / 'eval' / 'multi-tenant-memory'

    # Exact audited files are required; missing inputs fail rather than picking
    # a newer or partial run. CSV contents remain unchanged.
    data = {}
    sched_data = {}
    for kernel_name, memory_file, scheduler_file in HISTORICAL_SOURCES:
        csv_path = data_dir / memory_file
        data[kernel_name] = load_data(csv_path)
        print(f"Loaded {kernel_name}: {csv_path}")
        csv_path = data_dir / scheduler_file
        sched_data[kernel_name] = load_data(csv_path)
        print(f"Loaded Scheduler - {kernel_name}: {csv_path}")

    # Print improvement ratios
    print_improvements(data, sched_data)

    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    # Plot each kernel
    for idx, (kernel_name, df) in enumerate(data.items()):
        sched_df = sched_data.get(kernel_name)
        plot_kernel_subplot(axes[idx], df, kernel_name, sched_df)

    # Add shared legend at bottom
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.02),
               columnspacing=1.0)
    fig.text(0.5, -0.13,
             'Historical single-round (n=1/config); no CI or significance claim.\n'
             '* Scheduler engagement unverified; no ineffectiveness conclusion.\n'
             'Common no-policy reference comes from the separate memory run.',
             ha='center', va='top', fontsize=18)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.35)

    # Save
    output_path = base_dir / 'all_kernels_stacked'
    plt.savefig(f'{output_path}.pdf', bbox_inches='tight')
    plt.savefig(f'{output_path}.png', bbox_inches='tight')
    plt.close()
    print(f"\nSaved: {output_path}.pdf/png")


if __name__ == "__main__":
    main()
