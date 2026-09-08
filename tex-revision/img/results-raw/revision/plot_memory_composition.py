"""Extend the original three workload panels using the recorded completion times."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'memory-composition-data.json').read_text())
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 8, 'pdf.fonttype': 42,
                     'axes.labelsize': 8, 'xtick.labelsize': 7, 'ytick.labelsize': 7.2})
fig, axes = plt.subplots(1, 3, figsize=(3.33, 1.55))
colors = ['#e74c3c', '#3498db']
policies = ['sched_only', 'combined']
for i, (ax, workload) in enumerate(zip(axes, DATA['workloads'])):
    labels = [r['label'].replace('Prefetch', 'P').replace('Evict', 'E') for r in workload['original']]
    for x, r in enumerate(workload['original']):
        first, last = sorted([r['high'], r['low']])
        ax.bar(x, first, .65, color=colors[0], alpha=.85)
        ax.bar(x, last-first, .65, bottom=first, color=colors[1], alpha=.85)
    for j, policy in enumerate(policies):
        rows = [r for r in workload['composition'] if r['policy'] == policy]
        high = np.array([r['high'] for r in rows])
        low = np.array([r['low'] for r in rows])
        first, last = np.median(np.minimum(high, low)), np.median(np.maximum(high, low))
        total = np.maximum(high, low)
        x = j + 5.6
        ax.bar(x, first, .65, color=colors[0], alpha=.85)
        ax.bar(x, last-first, .65, bottom=first, color=colors[1], alpha=.85)
        ax.errorbar(x, last, yerr=[[last-total.min()], [total.max()-last]], color='black', capsize=2, linewidth=1)
    for factor, color, style in [(1, '#2ecc71', '--'), (2, '#9b59b6', '--')]:
        ax.hlines(factor*workload['single'], -.5, 4.5, colors=color, linestyles=style, linewidth=1.2)
    ax.axvline(4.8, color='.65', linewidth=.6)
    ax.set_xticks([0, 1, 2, 3, 4, 5.6, 6.6], labels + ['Scheduler†', 'Combined†'], rotation=60, ha='right')
    ax.set_ylim(bottom=0)
    ax.set_xlim(-.6, 7.2)
    ax.yaxis.set_major_locator(MaxNLocator(3))
    ax.set_axisbelow(True)
    ax.grid(axis='y', alpha=.2)
    ax.set_title(workload['name'], fontsize=7.5, pad=4)
    if i == 0:
        ax.set_ylabel('Time (s)', labelpad=1)
handles = [Patch(facecolor=colors[0], alpha=.85, label='Both running'),
           Patch(facecolor=colors[1], alpha=.85, label='One running'),
           Line2D([], [], color='#2ecc71', linestyle='--', label='Single 1×'),
           Line2D([], [], color='#9b59b6', linestyle='--', label='2×Single 1×')]
fig.legend(handles=handles, loc='upper center', ncol=2, fontsize=7.2, frameon=False, columnspacing=.7, handlelength=1.2, handletextpad=.35, borderaxespad=0)
fig.subplots_adjust(left=.12, right=.99, bottom=.43, top=.70, wspace=.30)
fig.savefig(ROOT / 'memory-composition.pdf')
fig.savefig('/tmp/gpubpf-memory-composition.png', dpi=180)
