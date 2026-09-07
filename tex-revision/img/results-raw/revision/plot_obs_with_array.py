#!/usr/bin/env python3
"""Render the updated device-side observability overhead figure.

Two side-by-side grouped-bar panels preserve the earlier figure's layout.
P40 uses the submitted values. RTX 5090 uses the original ten paired blocks
per tool plus five independent GPU-buffer pairs for kernelretsnoop. Bars
show means, and RTX 5090 whiskers show the complete observed range.
The symlog axis includes zero and the negative launchlate range.
All measurements are prefill throughput loss relative to the baseline
from the same campaign.

Paired overhead per block is derived as 100*(baseline - tool)/baseline
from the recorded cells and cross-checked against the recorded per-cell
overhead_pct and the campaign summaries. No GPU execution and no paper
edits; the old obs-overhead-bars.pdf is left untouched.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TOOLS = ("kernelretsnoop", "threadhist", "launchlate")
TOOL_TICKS = ("kernelretsnoop", "threadhist", "launchlate")
SYSTEMS = ("gpubpf", "nvbit")
ARM_COLORS = {"gpubpf": "#0072B2", "nvbit": "#D97706"}
GRAY = "#404040"
STYLE = {"font.family": "DejaVu Sans", "font.size": 8.0,
         "axes.labelsize": 8.0, "xtick.labelsize": 8.0, "ytick.labelsize": 8.0,
         "legend.fontsize": 8.0, "axes.spines.top": False,
         "axes.spines.right": False, "pdf.fonttype": 42, "ps.fonttype": 42}
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
DEFAULT_P40 = REPO / "workloads/llama.cpp/observability_overhead" / "p40-submitted-table1.json"
OLD_DIR = (REPO / "workloads/llama.cpp/observability_overhead/revision-rq4"
           / "results-table1-warp-plt-575-06")
NEW_DIR = (REPO / "workloads/llama.cpp/observability_overhead/revision-rq4"
           / "results-onevalue-array-bootstrap-575-20260907")

# Transcribed provenance from the new-campaign README (its per-block lookup
# table and allocation size); not derivable from cells.json.
ARRAY_LOOKUP = {"mean_ms": 10.379343, "min_ms": 10.157582, "max_ms": 10.959894,
                "allocated_bytes": 23199768,
                "note": "one whole-value host lookup of the finite GPU-local "
                        "array after target completion; outside the prefill "
                        "timing window; buffer sized for the pp512 workload"}


def _finite(value) -> bool:
    return type(value) in (int, float) and not isinstance(value, bool) and math.isfinite(value)


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-9)


def load_p40(path: Path) -> dict:
    data = json.loads(path.read_text())
    if data.get("gpu") != "P40" or sorted(data.get("tools", {})) != sorted(TOOLS):
        raise ValueError("P40 file must be the transcribed P40 Table 1 values")
    values = {}
    for tool in TOOLS:
        for system in SYSTEMS:
            value = data["tools"][tool][system]
            if not _finite(value) or not 0 < value < 100:
                raise ValueError(f"P40 {tool}/{system} value out of range: {value}")
            values[f"{system}_{tool}"] = float(value)
    return values


def derive_campaign(cells_path: Path, summary_path: Path, expected_arms: list[str],
                    n_blocks: int, require_storage: str | None = None) -> dict:
    cells = json.loads(cells_path.read_text())
    baseline, per_pair = {}, {}
    for cell in cells:
        arm, block, throughput = cell["arm"], cell["block"], cell["throughput_tok_s"]
        if arm == "baseline":
            if not _finite(throughput):
                raise ValueError(f"baseline block {block} lacks numeric throughput")
            baseline[block] = float(throughput)
    for cell in cells:
        arm, block, throughput = cell["arm"], cell["block"], cell["throughput_tok_s"]
        if arm == "baseline":
            continue
        base = baseline.get(block)
        if base is None or not _finite(throughput):
            raise ValueError(f"{arm} block {block} has no complete baseline pair")
        if require_storage and cell.get("storage") != require_storage:
            raise ValueError(f"{arm} block {block} storage is {cell.get('storage')!r}")
        derived = 100.0 * (base - throughput) / base
        recorded_pct = cell.get("overhead_pct")
        if not _finite(recorded_pct) or not _close(derived, float(recorded_pct)):
            raise ValueError(f"{arm} block {block} recorded overhead does not match "
                             f"the derived paired value: {recorded_pct} vs {derived}")
        per_pair.setdefault(arm, {})[block] = derived
    if sorted(baseline) != list(range(1, n_blocks + 1)):
        raise ValueError(f"expected {n_blocks} baseline blocks, got {sorted(baseline)}")
    for arm in expected_arms:
        blocks = per_pair.get(arm, {})
        if sorted(blocks) != list(range(1, n_blocks + 1)):
            raise ValueError(f"{arm} does not cover blocks 1..{n_blocks}: {sorted(blocks)}")
    summary = json.loads(summary_path.read_text())
    arms = {entry["arm"]: entry for entry in summary["arms"]}
    if arms.get("baseline", {}).get("cells") != n_blocks or \
            not _close(arms["baseline"]["throughput_tok_s_mean"], sum(baseline.values()) / n_blocks):
        raise ValueError("summary baseline mean disagrees with the recorded cells")
    for arm in expected_arms:
        entry = arms.get(arm)
        if entry is None or entry.get("cells") != n_blocks:
            raise ValueError(f"summary lacks {n_blocks} cells for {arm}")
        mean = sum(per_pair[arm].values()) / n_blocks
        if not _close(entry["mean_overhead_pct"], mean):
            raise ValueError(f"{arm} summary mean disagrees with the derived mean")
    return {
        "baseline_mean_tok_s": sum(baseline.values()) / n_blocks,
        "per_pair_overhead_pct": {arm: {str(b): per_pair[arm][b]
                                        for b in sorted(per_pair[arm])}
                                  for arm in expected_arms},
        "mean_overhead_pct": {arm: sum(per_pair[arm].values()) / n_blocks
                              for arm in expected_arms},
        "min_overhead_pct": {arm: min(per_pair[arm].values()) for arm in expected_arms},
        "max_overhead_pct": {arm: max(per_pair[arm].values()) for arm in expected_arms},
    }


def build_data(p40: dict, old: dict, new: dict) -> dict:
    return {
        "schema": "obs_overhead_with_array_v1",
        "metric": "prefill throughput loss, percent of the same-campaign "
                  "baseline throughput (lower is better)",
        "plot_note": "grouped mean bars with full-range whiskers; symlog axis "
                     "linear between -1 and +1 retains the negative launchlate range",
        "campaigns": {
            "p40_submitted": {
                "gpu": "P40",
                "workload": "Llama 1B, sequence-mixed llama.cpp prefill",
                "status": "historical",
                "n_pairs": None,
                "raw_variance": "none recorded with the published values; no "
                                "per-pair values are available and none are implied",
                "source": [
                    "docs/paper/tex/eval.tex (tab:obs-overhead)",
                    "workloads/llama.cpp/observability_overhead/p40-submitted-table1.json",
                ],
                "published_point_pct": p40,
            },
            "rtx5090_table1": {
                "gpu": "RTX 5090",
                "driver": "575.57.08",
                "workload": "TinyLlama-1.1B Q4_K_M, llama.cpp pp512 prefill",
                "status": "published",
                "n_pairs_per_arm": 10,
                "baseline_mean_tok_s": old["baseline_mean_tok_s"],
                "source": [
                    "workloads/llama.cpp/observability_overhead/revision-rq4/"
                    "results-table1-warp-plt-575-06/cells.json",
                    "workloads/llama.cpp/observability_overhead/revision-rq4/"
                    "results-table1-warp-plt-575-06/summary.json",
                    "workloads/llama.cpp/observability_overhead/revision-rq4/"
                    "results-table1-warp-plt-575-06/README.md",
                ],
                **old,
            },
            "rtx5090_gpu_array": {
                "gpu": "RTX 5090",
                "driver": "575.57.08",
                "workload": "TinyLlama-1.1B Q4_K_M, llama.cpp pp512 prefill",
                "status": "new",
                "tool": "kernelretsnoop",
                "storage": "gpu-array-onevalue",
                "n_pairs": 5,
                "independent_campaign": True,
                "baseline_note": "own five-block baseline; the five pairs are not "
                                 "interleaved with, or paired against, the table1 "
                                 "NVBit or gpubpf-ring arms",
                "baseline_mean_tok_s": new["baseline_mean_tok_s"],
                "source": [
                    "workloads/llama.cpp/observability_overhead/revision-rq4/"
                    "results-onevalue-array-bootstrap-575-20260907/cells.json",
                    "workloads/llama.cpp/observability_overhead/revision-rq4/"
                    "results-onevalue-array-bootstrap-575-20260907/summary.json",
                    "workloads/llama.cpp/observability_overhead/revision-rq4/"
                    "results-onevalue-array-bootstrap-575-20260907/README.md",
                ],
                "final_lookup_ms": ARRAY_LOOKUP,
                **new,
            },
        },
    }


def _draw(data: dict, paths: list[Path]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    p40 = data["campaigns"]["p40_submitted"]["published_point_pct"]
    old = data["campaigns"]["rtx5090_table1"]
    new = data["campaigns"]["rtx5090_gpu_array"]
    style = dict(STYLE, **{"font.size": 7.5, "axes.labelsize": 7.5,
                          "xtick.labelsize": 7, "ytick.labelsize": 7,
                          "legend.fontsize": 7.5})
    with plt.rc_context(style):
        figure, axes = plt.subplots(1, 2, figsize=(3.4, 2.0), sharey=True)
        for column, axis in enumerate(axes):
            for index, tool in enumerate(TOOLS):
                for system, offset in zip(SYSTEMS, (-.22, .22)):
                    arm = f"{system}_{tool}"
                    mean = p40[arm] if column == 0 else old["mean_overhead_pct"][arm]
                    # Leave room for the additional buffered gpubpf result.
                    center = index + offset
                    width = .36
                    if column == 1 and index == 0:
                        center = index + (-.29 if system == "gpubpf" else 0)
                        width = .25
                    axis.bar(center, mean, width=width, color=ARM_COLORS[system],
                             edgecolor="#333333", linewidth=.3,
                             hatch="//" if system == "nvbit" else None)
                    if column == 1:
                        low = old["min_overhead_pct"][arm]
                        high = old["max_overhead_pct"][arm]
                        axis.errorbar(center, mean, yerr=[[mean-low], [high-mean]],
                                      fmt="none", color=GRAY, capsize=1.5, linewidth=1)
            axis.set_yscale("symlog", linthresh=1)
            axis.set_ylim(-1, 200)
            axis.set_yticks([-1, 0, 1, 10, 100], ["−1", "0", "1", "10", "100"])
            axis.set_xticks(range(3), ["kernel-\nret-snoop", "thread-\nhist", "launch-\nlate"])
            axis.set_title(("(a) P40", "(b) RTX 5090")[column], fontsize=7.5, pad=4)
            axis.grid(axis="y", alpha=.25, linewidth=.6)
            axis.axhline(0, color="#555555", linewidth=.6)
        arm = "gpubpf_kernelretsnoop"
        mean = new["mean_overhead_pct"][arm]
        low, high = new["min_overhead_pct"][arm], new["max_overhead_pct"][arm]
        axes[1].bar(.29, mean, width=.25, facecolor="white",
                    edgecolor=ARM_COLORS["gpubpf"], hatch="xxxx", linewidth=.7)
        axes[1].errorbar(.29, mean, yerr=[[mean-low], [high-mean]],
                         fmt="none", color=GRAY, capsize=1.5, linewidth=1)
        axes[0].set_ylabel("Prefill throughput loss (%)")
        handles = [Patch(facecolor=ARM_COLORS["gpubpf"], label="gpubpf"),
                   Patch(facecolor=ARM_COLORS["nvbit"], hatch="//", label="NVBit"),
                   Patch(facecolor="white", edgecolor=ARM_COLORS["gpubpf"],
                         hatch="xxxx", label="GPU buffer")]
        figure.legend(handles=handles, loc="upper center", ncol=3, frameon=False,
                      bbox_to_anchor=(.5, 1.0), handlelength=1.1,
                      handletextpad=.4, columnspacing=.9)
        figure.subplots_adjust(left=.17, right=.99, bottom=.23, top=.76, wspace=.20)
        try:
            for path in paths:
                figure.savefig(path, dpi=300)
        finally:
            plt.close(figure)


def render(p40_path: Path, old_cells: Path, old_summary: Path, new_cells: Path,
           new_summary: Path, data_path: Path, prefix: Path) -> list[Path]:
    p40 = load_p40(p40_path)
    old = derive_campaign(old_cells, old_summary,
                          [f"{system}_{tool}" for system in SYSTEMS for tool in TOOLS],
                          10)
    new = derive_campaign(new_cells, new_summary, ["gpubpf_kernelretsnoop"], 5,
                          require_storage="gpu-array-onevalue")
    data = build_data(p40, old, new)
    outputs = [prefix.with_suffix(suffix) for suffix in (".pdf", ".png")]
    if any(path.exists() for path in outputs) or data_path.exists():
        raise FileExistsError("output exists; remove the previous figure first")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, indent=2) + "\n")
    _draw(data, outputs)
    return [data_path, *outputs]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p40", type=Path, default=DEFAULT_P40)
    parser.add_argument("--old-cells", type=Path, default=OLD_DIR / "cells.json")
    parser.add_argument("--old-summary", type=Path, default=OLD_DIR / "summary.json")
    parser.add_argument("--new-cells", type=Path, default=NEW_DIR / "cells.json")
    parser.add_argument("--new-summary", type=Path, default=NEW_DIR / "summary.json")
    parser.add_argument("--data-output", type=Path,
                        default=HERE / "obs-with-array-data.json")
    parser.add_argument("--output-prefix", type=Path,
                        default=HERE / "obs-overhead-with-array")
    args = parser.parse_args()
    results = render(args.p40, args.old_cells, args.old_summary,
                     args.new_cells, args.new_summary,
                     args.data_output, args.output_prefix)
    print("\n".join(str(path) for path in results))
