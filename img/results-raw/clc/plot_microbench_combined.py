#!/usr/bin/env python3
"""
Plot combined microbenchmark results: (a) Memory prefetch policies, (b) Block scheduling policies.
Both normalized to baseline = 1.0.
"""

import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 26,
    'axes.labelsize': 30,
    'axes.titlesize': 30,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'legend.fontsize': 22,
    'figure.dpi': 150,
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# ============================================================
# (a) Memory Prefetch Microbenchmark
# Normalized speedup (higher = better), baseline = 1.0
# ============================================================
mem_policies = ['Default\nUVM', 'Device\nPrefetch', 'Host+Device\nStride eBPF', 'Sequential\nPrefetch']
mem_speedups = [1.0, 1.34, 1.77, 0.92]
mem_colors = ['#7f7f7f', '#2ca02c', '#1f77b4', '#d62728']

x_m = np.arange(len(mem_policies))
bars_m = ax1.bar(x_m, mem_speedups, 0.6, color=mem_colors, edgecolor='black', linewidth=0.5)

# Baseline reference line
ax1.axhline(y=1.0, color='gray', linestyle='--', linewidth=2, alpha=0.7)

# Annotations
for i, (bar, val) in enumerate(zip(bars_m, mem_speedups)):
    if i > 0:
        change = (val - 1.0) * 100
        sign = '+' if change >= 0 else ''
        color = '#2ca02c' if change > 0 else '#d62728'
        ax1.annotate(f'{sign}{change:.0f}%',
                    xy=(bar.get_x() + bar.get_width()/2, val),
                    xytext=(0, 5),
                    textcoords='offset points',
                    ha='center', va='bottom', fontsize=22, color=color, fontweight='bold')

ax1.set_ylabel('Normalized Speedup')
ax1.set_title('(a) Memory Prefetch')
ax1.set_xticks(x_m)
ax1.set_xticklabels(mem_policies)
ax1.set_ylim(0, max(mem_speedups) * 1.2)
ax1.set_axisbelow(True)

# ============================================================
# (b) Block Scheduling Microbenchmark
# Normalized latency (lower = better), baseline = 1.0
# ============================================================
policies = ['FixedWork', 'Greedy', 'LatencyBudget']

# Raw data
runtimes_a = [0.1019, 0.0910, 0.0909]  # Imbalanced GEMM
runtimes_b = [14.8, 17.8, 14.7]        # ClusteredHeavy

# Normalize to FixedWork baseline
norm_a = [r / runtimes_a[0] for r in runtimes_a]
norm_b = [r / runtimes_b[0] for r in runtimes_b]

x_s = np.arange(len(policies))
width = 0.3

bars_imb = ax2.bar(x_s - width/2, norm_a, width,
                   label='Imbalanced GEMM', color='#2ca02c', edgecolor='black', linewidth=0.5)
bars_clh = ax2.bar(x_s + width/2, norm_b, width,
                   label='Clustered Heavy', color='#1f77b4', edgecolor='black', linewidth=0.5)

# Baseline reference line
ax2.axhline(y=1.0, color='gray', linestyle='--', linewidth=2, alpha=0.7)

# Annotations for non-baseline policies
for bars, norms in [(bars_imb, norm_a), (bars_clh, norm_b)]:
    for i, (bar, val) in enumerate(zip(bars, norms)):
        if i == 0:  # skip FixedWork baseline
            continue
        change = (val - 1.0) * 100
        sign = '+' if change >= 0 else ''
        color = '#d62728' if change > 0 else '#2ca02c'
        ax2.annotate(f'{sign}{change:.0f}%',
                    xy=(bar.get_x() + bar.get_width()/2, val),
                    xytext=(0, 5),
                    textcoords='offset points',
                    ha='center', va='bottom', fontsize=18, color=color, fontweight='bold')

ax2.set_ylabel('Normalized Latency')
ax2.set_title('(b) Block Scheduling')
ax2.set_xticks(x_s)
ax2.set_xticklabels(policies)
ax2.set_ylim(0, max(norm_b) * 1.2)
ax2.legend(loc='upper left')
ax2.set_axisbelow(True)

plt.tight_layout()

output_file = 'microbench_combined.pdf'
plt.savefig(output_file, bbox_inches='tight', dpi=300)
plt.savefig('microbench_combined.png', bbox_inches='tight', dpi=300)
print(f"Saved: {output_file}")
plt.show()
