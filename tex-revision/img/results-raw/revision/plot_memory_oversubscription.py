"""Plot paired high-priority speedups from the adjacent observation CSV."""
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median
from types import SimpleNamespace
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

POLICIES = ['baseline', 'sched_only', 'prefetch_only', 'memory_only', 'combined']
LABELS = ['Default', 'Sched', 'Prefetch', 'Evict', 'Mem + Sched']
KERNELS = ['hotspot', 'gemm', 'kmeans_sparse']

def main():
    output = Path(__file__).resolve().parent
    args = SimpleNamespace(speedup_only=True)
    groups = defaultdict(list)
    with (output / 'memory-oversubscription-cells.csv').open() as f:
        for row in csv.DictReader(f):
            groups[(row['kernel'], float(row['requested_ratio']))].append(row)
    summaries = []
    for (kernel, ratio), rows in groups.items():
        assert len(rows) == 25
        baseline = {r['block']: float(r['high_s']) for r in rows if r['policy'] == 'baseline'}
        assert len(baseline) == 5
        for policy in POLICIES:
            selected = [r for r in rows if r['policy'] == policy]
            assert len(selected) == 5 and {r['block'] for r in selected} == set(baseline)
            values = [baseline[r['block']] / float(r['high_s']) for r in selected]
            summaries.append(dict(kernel=kernel, requested_ratio=ratio, policy=policy,
                actual_allocation_ratio=float(selected[0]['actual_allocation_ratio']),
                high_speedup_median=median(values), high_speedup_min=min(values),
                high_speedup_max=max(values)))
    plt.style.use('seaborn-v0_8-whitegrid')
    # Match the original all_kernels_stacked.pdf, including its bottom legend,
    # repeated axis labels, prominent titles, and thin gray frame/grid.
    plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 8, 'pdf.fonttype': 42,
                         'axes.labelsize': 8, 'axes.titlesize': 9,
                         'axes.linewidth': .4, 'axes.edgecolor': '.75',
                         'grid.linewidth': .4, 'grid.color': '.75',
                         'xtick.labelsize': 8, 'ytick.labelsize': 8})
    plots = ([('high_speedup', 'Speedup (×)')] if args.speedup_only else
             [('high_s', 'High-priority time (s)'), ('low_s', 'Low-priority time (s)'),
              ('both_finished_s', 'Both completed (s)')])
    for metric, ylabel in plots:
        fig, axes = plt.subplots(1, 3, figsize=(3.33, 1.30))
        for ax, kernel, title in zip(axes, KERNELS, ['HotSpot', 'GEMM', 'K-Means']):
            for policy, label, color, marker, style in zip(POLICIES, LABELS,
                    ['#777777', '#3498db', '#2ecc71', '#9b59b6', '#e74c3c'],
                    ['o', 's', '^', 'v', 'D'], ['-', '-', '--', '--', '-']):
                data = sorted([r for r in summaries if r['kernel'] == kernel and r['policy'] == policy], key=lambda r:r['requested_ratio'])
                x = [r['actual_allocation_ratio'] for r in data]
                y = [r[metric + '_median'] for r in data]
                err = [[r[metric + '_median'] - r[metric + '_min'] for r in data],
                       [r[metric + '_max'] - r[metric + '_median'] for r in data]]
                if data:
                    if metric == 'high_speedup' and policy == 'baseline':
                        style = '--'
                    ax.errorbar(x, y, yerr=err, color=color, marker=marker, linestyle=style,
                                linewidth=1.3 if policy == 'combined' else 1.0, markersize=4,
                                markerfacecolor=color, markeredgewidth=.4,
                                elinewidth=.5, capsize=1, alpha=.85, label=label)
            if metric == 'high_speedup':
                ax.axhline(1, color='#777777', linestyle='--', linewidth=1, alpha=.85)
            ax.set_xlim(.7, 1.6); ax.set_xticks([.8, 1.0, 1.2, 1.5], ['0.8', '1', '1.2', '1.5']); ax.set_ylim(bottom=0)
            ax.set_ylim(0, ax.get_ylim()[1] * 1.10)
            ax.yaxis.set_major_locator(MaxNLocator(3)); ax.set_axisbelow(True)
            ax.grid(axis='both', alpha=.8)
            ax.set_title(title, fontsize=9, pad=2)
            ax.set_ylabel(ylabel, labelpad=1)
        handles, labels = axes[0].get_legend_handles_labels()
        # Legend samples show line/marker styles without the error-bar glyphs.
        fig.legend([handle.lines[0] for handle in handles], labels,
                   loc='lower center', ncol=5, fontsize=8, frameon=False,
                   columnspacing=.35, handlelength=1.0, handletextpad=.2,
                   bbox_to_anchor=(.5, -.015), borderaxespad=0)
        fig.supxlabel('Oversubscription ratio', fontsize=8, y=.135)
        fig.subplots_adjust(left=.12, right=.98, bottom=.36, top=.86, wspace=.68)
        fig.savefig(output / 'memory-oversubscription-speedup.pdf')
        fig.savefig(output / 'memory-oversubscription-speedup.png', dpi=220)
        plt.close(fig)


if __name__ == '__main__':
    main()
