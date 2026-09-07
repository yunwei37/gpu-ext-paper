#!/usr/bin/env python3
"""Render the updated device-side observability overhead figure.

Two vertically stacked horizontal dot/range panels, one per GPU:
  (a) P40, published submitted-paper values (historical; no per-pair
      variance is recorded for these values, so single points are drawn).
  (b) RTX 5090: all ten paired blocks per arm of the original three-tool
      campaign (points + min-max whisker + mean tick), plus the completed
      GPU-local-array kernelretsnoop result: five paired points (diamonds)
      with min-max and mean from its own independent five-pair campaign.

The x axis is symlog with a linear region between -1 and +1, so the
negative gpubpf launchlate pairs remain visible; nothing is clamped,
dropped, or replaced by a positive floor. All measures are prefill
throughput loss in percent relative to the same-campaign baseline.

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
STYLE = {"font.family": "DejaVu Sans", "font.size": 7.5,
         "axes.labelsize": 7.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
         "legend.fontsize": 7.5, "axes.spines.top": False,
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
        "plot_note": "symlog axis, linear between -1 and +1; the negative "
                     "gpubpf launchlate pairs are shown, not clamped",
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
    from matplotlib.lines import Line2D

    p40 = data["campaigns"]["p40_submitted"]["published_point_pct"]
    old = data["campaigns"]["rtx5090_table1"]
    new = data["campaigns"]["rtx5090_gpu_array"]
    old_pairs = old["per_pair_overhead_pct"]
    new_pairs = new["per_pair_overhead_pct"]["gpubpf_kernelretsnoop"]
    rows = {tool: index for index, tool in enumerate(reversed(TOOLS))}

    with plt.rc_context(STYLE):
        figure, axes = plt.subplots(2, 1, figsize=(3.4, 2.5), sharex=True)
        for axis in axes:
            axis.set_xscale("symlog", linthresh=1.0)
            axis.set_xlim(-2, 150)
            axis.set_ylim(-0.6, 2.6)
            axis.set_yticks([0, 1, 2], TOOL_TICKS[::-1])
            axis.grid(axis="x", alpha=.25, linewidth=.6, which="major")
        for axis in axes:
            axis.set_xticks([-1, 0, 1, 10, 100])
            axis.set_xticklabels(["-1", "0", "1", "10", "100"])
        axes[1].set_xlabel("Prefill throughput loss (%)")
        axes[0].set_title("(a) P40, Llama 1B prefill", fontsize=7.5, pad=3)
        axes[1].set_title("(b) RTX 5090, TinyLlama-1.1B prefill", fontsize=7.5, pad=3)

        for tool in TOOLS:
            y = rows[tool]
            for system, offset in zip(SYSTEMS, (0.18, -0.18)):
                arm = f"{system}_{tool}"
                axis = axes[0]
                axis.scatter([p40[arm]], [y + offset], marker="o", s=9,
                             color=ARM_COLORS[system], zorder=3)
        top = axes[0]
        for tool in TOOLS:
            y = rows[tool]
            for system, offset in zip(SYSTEMS, (0.18, -0.18)):
                arm = f"{system}_{tool}"
                values = [old_pairs[arm][str(block)] for block in range(1, 11)]
                axis = axes[1]
                axis.hlines(y + offset, min(values), max(values),
                            color=ARM_COLORS[system], linewidth=.8, zorder=2)
                for end in (min(values), max(values)):
                    axis.vlines(end, y + offset - .05, y + offset + .05,
                                color=ARM_COLORS[system], linewidth=.8, zorder=2)
                for index, value in enumerate(values):
                    jiggled = y + offset + (0.06 if index % 2 == 0 else -0.06)
                    axis.scatter([value], [jiggled], marker="o", s=8,
                                 color=ARM_COLORS[system], zorder=3)
                axis.vlines(old["mean_overhead_pct"][arm], y + offset - .09,
                            y + offset + .09, color=GRAY, linewidth=1.0, zorder=4)
        y = rows["kernelretsnoop"]
        axis = axes[1]
        values = [new_pairs[str(block)] for block in range(1, 6)]
        axis.hlines(y, min(values), max(values), color=GRAY, linewidth=.8, zorder=2)
        for end in (min(values), max(values)):
            axis.vlines(end, y - .05, y + .05, color=GRAY, linewidth=.8, zorder=2)
        for index, value in enumerate(values):
            jiggled = y + (0.05 if index % 2 == 0 else -0.05)
            axis.scatter([value], [jiggled], marker="D", s=11,
                         facecolor=ARM_COLORS["gpubpf"], edgecolor="#002A43",
                         linewidth=.3, zorder=4)
        axis.vlines(new["mean_overhead_pct"]["gpubpf_kernelretsnoop"], y - .09,
                    y + .09, color=GRAY, linewidth=1.0, zorder=4)
        handles = [
            Line2D([0], [0], marker="o", color=ARM_COLORS["gpubpf"], linestyle="",
                   markersize=4, label="gpubpf"),
            Line2D([0], [0], marker="o", color=ARM_COLORS["nvbit"], linestyle="",
                   markersize=4, label="NVBit"),
            Line2D([0], [0], marker="D", color=ARM_COLORS["gpubpf"], linestyle="",
                   markersize=4, label="gpubpf + array"),
            Line2D([0], [0], marker="|", color=GRAY, linestyle="",
                   markersize=6, label="mean"),
        ]
        figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, 1.02),
                      ncol=4, frameon=False, handlelength=1.1, handletextpad=.4,
                      columnspacing=1.0)
        figure.tight_layout(rect=(0, 0, .98, .93), h_pad=0.8, w_pad=1.0)
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
