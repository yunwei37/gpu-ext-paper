#!/usr/bin/env python3
"""
Plot microbenchmark comparison: old vs new implementation
Parses markdown tables from micro_vec_add_result.md files
Left subplot: GPU absolute latency comparison (before/after optimization)
Right subplot: CPU map access latency (absolute time)
"""

import matplotlib.pyplot as plt
import numpy as np
import re
from pathlib import Path

def parse_markdown_table(filepath):
    """Parse benchmark results from markdown file."""
    results = {}
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the benchmark results table
    lines = content.split('\n')
    in_table = False
    for line in lines:
        if '| Test Name |' in line:
            in_table = True
            continue
        if in_table and line.startswith('|---'):
            continue
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                test_name = parts[0]
                workload = parts[1]
                avg_time_str = parts[2]

                # Parse average time (μs)
                try:
                    avg_time = float(avg_time_str)
                except:
                    avg_time = None

                if avg_time is not None:
                    results[(test_name, workload)] = {'time': avg_time}

    return results

def main():
    script_dir = Path(__file__).parent
    old_file = script_dir / 'old' / 'micro_vec_add_result.md'
    new_file = script_dir / 'micro_vec_add_result.md'

    old_results = parse_markdown_table(old_file)
    new_results = parse_markdown_table(new_file)

    # Get baseline time for reference
    baseline_time = None
    for key in new_results:
        if 'Baseline' in key[0] and key[1] == 'tiny':
            baseline_time = new_results[key]['time']
            break

    # Separate GPU and CPU tests
    gpu_labels = []
    gpu_old_time = []
    gpu_new_time = []

    cpu_labels = []
    cpu_time = []

    for key in sorted(old_results.keys()):
        test_name, workload = key
        # Skip baselines
        if 'Baseline' in test_name:
            continue
        # Only tiny and minimal
        if workload not in ('tiny', 'minimal'):
            continue
        # Check if exists in new results
        if key not in new_results:
            continue
        # Skip Hash tests
        if 'Hash' in test_name:
            continue

        # Create label: remove workload suffix for cleaner display
        label = test_name.replace(f' ({workload})', '')

        old_time = old_results[key]['time']
        new_time = new_results[key]['time']

        if old_time is None or new_time is None:
            continue

        if 'CPU' in test_name:
            # Simplify CPU labels
            label = label.replace('CPU ', '').replace(' map', '')
            cpu_labels.append(label)
            cpu_time.append(new_time)  # Keep in μs
        else:
            # Simplify GPU labels
            label = label.replace('GPU ', '').replace(' map', '')
            gpu_labels.append(label)
            gpu_old_time.append(old_time)
            gpu_new_time.append(new_time)

    # Create figure with two subplots
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 3.5),
                                             gridspec_kw={'width_ratios': [5, 1]})

    # Left subplot: GPU latency comparison
    x_gpu = np.arange(len(gpu_labels))
    width = 0.35

    ax_left.bar(x_gpu - width/2, gpu_old_time, width, label='Before Optimization',
                color='#7f7f7f', edgecolor='black', linewidth=0.5)
    ax_left.bar(x_gpu + width/2, gpu_new_time, width, label='After Optimization',
                color='#2ca02c', edgecolor='black', linewidth=0.5)

    # Add baseline reference line
    if baseline_time:
        ax_left.axhline(y=baseline_time, color='blue', linestyle='--', linewidth=1, alpha=0.7, label=f'Baseline ({baseline_time:.1f}μs)')

    ax_left.set_ylabel('Latency (μs)', fontsize=14)
    ax_left.set_xlabel('GPU-side Operation Type', fontsize=14)
    ax_left.set_xticks(x_gpu)
    ax_left.set_xticklabels(gpu_labels, fontsize=11, rotation=45, ha='right')
    ax_left.legend(fontsize=11, loc='upper right')
    ax_left.set_title('(a) GPU-side Operations', fontsize=14, fontweight='bold')

    # Add improvement percentage annotations
    for i, (old, new) in enumerate(zip(gpu_old_time, gpu_new_time)):
        if old > 0:
            reduction = ((old - new) / old) * 100
            if reduction > 0:
                ax_left.annotate(f'-{reduction:.0f}%',
                                xy=(x_gpu[i], max(old, new) + 0.3),
                                ha='center', va='bottom', fontsize=9, color='red', fontweight='bold')

    ax_left.set_axisbelow(True)
    ax_left.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax_left.set_ylim(0, max(gpu_old_time) * 1.2)

    # Right subplot: CPU map access latency
    x_cpu = np.arange(len(cpu_labels))
    # Convert to thousands for display (μs -> ms scale on axis)
    cpu_time_k = [t / 1000 for t in cpu_time]
    bars_cpu = ax_right.bar(x_cpu, cpu_time_k, 0.6, color='#d62728', edgecolor='black', linewidth=0.5)

    ax_right.set_ylabel('Latency (×10³ μs)', fontsize=14)
    ax_right.set_xlabel('CPU Map Op', fontsize=14)
    ax_right.set_xticks(x_cpu)
    ax_right.set_xticklabels(cpu_labels, fontsize=11, rotation=45, ha='right')
    ax_right.set_title('(b) CPU Map (PCIe)', fontsize=14, fontweight='bold')

    # Add value labels on CPU bars
    for i, bar in enumerate(bars_cpu):
        height = bar.get_height()
        ax_right.annotate(f'{cpu_time[i]:.0f}μs',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 2),
                         textcoords="offset points",
                         ha='center', va='bottom', fontsize=10)

    ax_right.set_axisbelow(True)
    ax_right.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax_right.set_ylim(0, max(cpu_time_k) * 1.15)

    plt.tight_layout()
    output_path = script_dir / 'microbench_comparison.pdf'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved to {output_path}")

if __name__ == '__main__':
    main()
