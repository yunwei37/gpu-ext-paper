#!/usr/bin/env python3
"""
Generate updated paper figures for GNN capability progression and FAISS phase-adaptive.
Outputs to docs/paper/img/results-raw/
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent  # gpu_ext root
IMG_DIR = Path(__file__).resolve().parent / "results-raw"

# ==================== Figure 1: GNN Capability Progression ====================

def plot_gnn_capability():
    """Bar chart showing L0 -> L1 -> L2 progression at 10M nodes."""
    result_dir = REPO / "workloads" / "pytorch" / "result"

    configs = [
        ("UVM Default", "v1_baseline_10m.json", "#e74c3c"),
        ("Advisory Hooks\n(always_max)", "v1_always_max_10m.json", "#f39c12"),
        ("+ Async Cross-Block\n(bpf_wq + migrate_range)", "v1_xb_dir_10m.json", "#2ecc71"),
    ]

    times = []
    labels = []
    colors = []
    for label, fname, color in configs:
        with open(result_dir / fname) as f:
            data = json.load(f)
        times.append(data["avg_epoch_time_s"])
        labels.append(label)
        colors.append(color)

    baseline = times[0]
    speedups = [baseline / t for t in times]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(configs))
    bars = ax.bar(x, times, width=0.55, color=colors, edgecolor='black', linewidth=0.8)

    # Speedup annotations
    for i, (bar, spd) in enumerate(zip(bars, speedups)):
        if i == 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                    "Baseline", ha='center', va='bottom', fontsize=16, fontweight='bold')
        else:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                    f"{spd:.2f}x", ha='center', va='bottom', fontsize=18, fontweight='bold')

    # L1->L2 gap annotation
    ax.annotate('', xy=(2, times[2]+6), xytext=(1, times[1]+6),
                arrowprops=dict(arrowstyle='<->', color='black', lw=2))
    ax.text(1.5, (times[1]+times[2])/2 + 8, '+27%', ha='center', va='bottom',
            fontsize=16, fontweight='bold', color='black')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=15)
    ax.set_ylabel("Epoch Time (seconds)", fontsize=20)
    ax.set_title("GNN Training (10M nodes, 1.34x oversub)", fontsize=20)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_ylim(0, max(times) * 1.25)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    out_dir = IMG_DIR / "pytorch"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "gnn_capability_progression.pdf", bbox_inches='tight')
    fig.savefig(out_dir / "gnn_capability_progression.png", dpi=150, bbox_inches='tight')
    print(f"Saved: {out_dir / 'gnn_capability_progression.pdf'}")
    plt.close(fig)


# ==================== Figure 2: FAISS Phase-Adaptive ====================

def plot_faiss_updated():
    """Updated FAISS figure using phase-adaptive (D3) results."""
    results_dir = REPO / "workloads" / "faiss" / "results"

    # Phase-adaptive experiment (exp_xb4): A=baseline, D3=phase_v2_stride+default_lru
    baseline_file = results_dir / "SIFT100M_IVF4096_Flat_uvm_20260304_160110.json"
    phase_file = results_dir / "SIFT100M_IVF4096_Flat_uvm_20260304_175524.json"
    # Keep SIFT50M from old data for the two-dataset comparison
    sift50m_base = results_dir / "SIFT50M_IVF4096_Flat_uvm_baseline.json"
    sift50m_ebpf = results_dir / "SIFT50M_IVF4096_Flat_uvm_prefetch_adaptive_tree.json"

    with open(baseline_file) as f:
        base100 = json.load(f)
    with open(phase_file) as f:
        phase100 = json.load(f)
    with open(sift50m_base) as f:
        base50 = json.load(f)
    with open(sift50m_ebpf) as f:
        ebpf50 = json.load(f)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # ---- Left: Build Index Progress ----
    datasets = [
        ("SIFT50M", base50, ebpf50, "tab:blue"),
        ("SIFT100M", base100, phase100, "tab:red"),
    ]

    for ds_name, base_d, ebpf_d, color in datasets:
        # Baseline
        prog = base_d["index_add"]["progress"]
        vecs = [p["vectors_added"] / 1e6 for p in prog]
        ts = [p["time"] for p in prog]
        ax1.plot(vecs, ts, marker='o', markersize=4, color=color,
                 linestyle='-', alpha=0.7, label=f"{ds_name} UVM Baseline")

        # gpubpf
        prog2 = ebpf_d["index_add"]["progress"]
        vecs2 = [p["vectors_added"] / 1e6 for p in prog2]
        ts2 = [p["time"] for p in prog2]
        ax1.plot(vecs2, ts2, marker='s', markersize=4, color=color,
                 linestyle='--', label=f"{ds_name} UVM gpubpf")

    ax1.set_xlabel("Vectors Added (millions)", fontsize=18)
    ax1.set_ylabel("Time (seconds)", fontsize=18)
    ax1.set_title("(a) Index Build Time", fontsize=20, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', labelsize=14)

    # ---- Right: Search Latency Normalized ----
    dataset_data = [
        ("SIFT50M", base50, ebpf50, "tab:blue", "o"),
        ("SIFT100M", base100, phase100, "tab:red", "s"),
    ]

    all_nprobes = [1, 4, 16]

    for ds_name, base_d, ebpf_d, color, marker in dataset_data:
        base_search = {s["nprobe"]: s for s in base_d["search"]}
        pref_search = {s["nprobe"]: s for s in ebpf_d["search"]}

        nprobes = []
        norm_lats = []
        for np_val in all_nprobes:
            if np_val in base_search and np_val in pref_search:
                bl = base_search[np_val]["search_time"] / base_search[np_val]["num_queries"] * 1000
                pl = pref_search[np_val]["search_time"] / pref_search[np_val]["num_queries"] * 1000
                nprobes.append(np_val)
                norm_lats.append(pl / bl)

        ax2.plot(nprobes, norm_lats, marker=marker, markersize=14, linewidth=3,
                 label=ds_name, color=color)

        for np_val, nl in zip(nprobes, norm_lats):
            change = (nl - 1.0) * 100
            ax2.annotate(f'{change:.1f}%',
                         xy=(np_val, nl),
                         xytext=(0, -20 if ds_name == "SIFT50M" else 15),
                         textcoords='offset points',
                         ha='center', va='top' if ds_name == "SIFT50M" else 'bottom',
                         fontsize=16, fontweight='bold', color=color)

    ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, linewidth=2)
    ax2.set_xticks(all_nprobes)
    ax2.set_xticklabels([str(n) for n in all_nprobes])
    ax2.set_xlabel("nprobe", fontsize=18)
    ax2.set_ylabel("Normalized Latency (Baseline = 1.0)", fontsize=18)
    ax2.set_title("(b) Search Latency", fontsize=20, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0.75, 1.15)
    ax2.tick_params(axis='both', labelsize=14)
    ax2.fill_between(all_nprobes, 0, 1.0, alpha=0.1, color='green', label='_nolegend_')
    ax2.text(all_nprobes[-1], 0.77, 'Lower is Better', ha='right', fontsize=14, color='green', alpha=0.8)

    # Combined legend
    legend_elements = [
        Line2D([0], [0], color='tab:orange', marker='o', markersize=8, linewidth=2, linestyle='-', label='UVM Baseline'),
        Line2D([0], [0], color='tab:red', marker='s', markersize=8, linewidth=2, linestyle='--', label='UVM gpubpf'),
        Line2D([0], [0], color='tab:blue', marker='o', markersize=10, linewidth=2, linestyle='-', label='SIFT50M'),
        Line2D([0], [0], color='tab:red', marker='s', markersize=10, linewidth=2, linestyle='-', label='SIFT100M'),
        Line2D([0], [0], color='gray', linestyle='--', linewidth=2, label='Baseline (1.0)'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=5, fontsize=12,
               bbox_to_anchor=(0.5, -0.02), frameon=True, fancybox=True)

    plt.subplots_adjust(bottom=0.18)

    out_dir = IMG_DIR / "faiss"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "faiss_benchmark_results_v2.pdf", bbox_inches='tight', facecolor='white')
    fig.savefig(out_dir / "faiss_benchmark_results_v2.png", dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {out_dir / 'faiss_benchmark_results_v2.pdf'}")

    # Print summary
    b100_build = base100["index_add"]["total_time"]
    p100_build = phase100["index_add"]["total_time"]
    print(f"\nSIFT100M build: {b100_build:.2f}s -> {p100_build:.2f}s ({(p100_build-b100_build)/b100_build*100:.1f}%)")
    b50_build = base50["index_add"]["total_time"]
    e50_build = ebpf50["index_add"]["total_time"]
    print(f"SIFT50M build: {b50_build:.2f}s -> {e50_build:.2f}s ({(e50_build-b50_build)/b50_build*100:.1f}%)")

    plt.close(fig)


if __name__ == "__main__":
    plot_gnn_capability()
    plot_faiss_updated()
    print("\nDone. Check docs/paper/img/results-raw/{pytorch,faiss}/")
