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
plt.rcParams.update({'font.family': 'serif', 'font.size': 8, 'pdf.fonttype': 42,
                     'axes.labelsize': 8, 'xtick.labelsize': 7.2, 'ytick.labelsize': 7.2})
fig, axes = plt.subplots(1, 3, figsize=(7, 3.1))
colors = ['#e74c3c', '#3498db']
policies = ['baseline', 'memory_only', 'sched_only', 'combined']
for i, (ax, workload) in enumerate(zip(axes, DATA['workloads'])):
    labels = [r['label'] for r in workload['original']]
    for x, r in enumerate(workload['original']):
        first, last = sorted([r['high'], r['low']])
        ax.bar(x, first, .65, color=colors[0], edgecolor='white', linewidth=.3)
        ax.bar(x, last-first, .65, bottom=first, color=colors[1], hatch='///', linewidth=.3, edgecolor='white')
    for j, policy in enumerate(policies):
        rows = [r for r in workload['composition'] if r['policy'] == policy]
        high = np.array([r['high'] for r in rows])
        low = np.array([r['low'] for r in rows])
        first, last = np.median(np.minimum(high, low)), np.median(np.maximum(high, low))
        total = np.maximum(high, low)
        x = j + 6
        ax.bar(x, first, .65, color=colors[0], edgecolor='white', linewidth=.3)
        ax.bar(x, last-first, .65, bottom=first, color=colors[1], hatch='///', linewidth=.3, edgecolor='white')
        ax.errorbar(x, last, yerr=[[last-total.min()], [total.max()-last]], color='black', capsize=2, linewidth=1)
        ax.plot(x, np.median(high), 'D', color='black', markersize=3)
    for factor, color, style in [(1, '#2ecc71', '--'), (2, '#9b59b6', ':')]:
        ax.hlines(factor*workload['single'], -.5, 4.5, colors=color, linestyles=style, linewidth=1.2)
    ax.axvline(5, color='.65', linewidth=.6)
    ax.set_xticks([0, 1, 2, 3, 4, 6, 7, 8, 9], labels + ['No policy', 'Memory', 'Scheduler', 'Combined'], rotation=65, ha='right')
    ax.set_ylim(bottom=0)
    ax.set_xlim(-.6, 9.6)
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.set_axisbelow(True)
    ax.grid(axis='y', alpha=.2)
    ax.set_title(f'({chr(97+i)}) {workload["name"]}', fontsize=8, pad=17)
    ax.text(.25, 1.02, 'Original', transform=ax.transAxes, ha='center', fontsize=7.2)
    ax.text(.78, 1.02, 'Composition', transform=ax.transAxes, ha='center', fontsize=7.2)
    if i == 0:
        ax.set_ylabel('Completion time (s)')
handles = [Patch(facecolor=colors[0], label='Both running'),
           Patch(facecolor=colors[1], hatch='///', label='One running'),
           Line2D([], [], color='black', marker='D', linestyle='none', markersize=3, label='High-priority completion (new)'),
           Line2D([], [], color='#2ecc71', linestyle='--', label='Single 1×'),
           Line2D([], [], color='#9b59b6', linestyle=':', label='2×Single 1×')]
fig.legend(handles=handles, loc='upper center', ncol=3, fontsize=7.2, frameon=False, columnspacing=1.2)
fig.subplots_adjust(left=.07, right=.99, bottom=.34, top=.72, wspace=.29)
fig.savefig(ROOT / 'memory-composition.pdf')
fig.savefig('/tmp/gpubpf-memory-composition.png', dpi=180)
