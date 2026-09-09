#!/usr/bin/env python3
"""Render matched policy ports with a shared baseline/native/BPF legend.

Each panel is one scoped policy comparison: bars for its stated baseline,
the native policy implementation, and the gpubpf port of the same policy, from
matched-policy-panels.json (published values with per-panel sources).
Seven panels share one row. XSched and GPREEMPT medians are derived from
the retained per-run samples; whiskers show their full range. Expert Buffering uses whole-expert loads. The original
five-panel data file remains supported. No GPU execution and no paper edits.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

COLORS = {"baseline": "#666666", "original": "#D97706", "port": "#0072B2"}
LEGEND = (("baseline", "Baseline"), ("original", "Native policy"), ("port", "gpubpf"))
STYLE = {"font.family": "DejaVu Sans", "font.size": 7,
         "axes.labelsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
         "legend.fontsize": 7, "axes.spines.top": False,
         "axes.spines.right": False, "pdf.fonttype": 42, "ps.fonttype": 42}
HERE = Path(__file__).resolve().parent


def load_panels(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text())
    if data.get("schema") not in ("matched_port_panels_v1", "matched_port_panels_v2"):
        raise ValueError("panel file is not the matched-port panel data")
    panels = data["panels"]
    if len(panels) not in (5, 7) or len({p["id"] for p in panels}) != len(panels):
        raise ValueError("expected five or seven distinct panels")
    for panel in panels:
        for group in panel["groups"]:
            for key, value in group.items():
                if key == "label":
                    continue
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    raise ValueError(f"bad value in panel {panel['id']}: {group}")
    for panel in panels:
        for group, samples in zip(panel["groups"], panel.get("samples", [])):
            for arm, values in samples.items():
                if not math.isclose(group[arm], statistics.median(values), abs_tol=1e-9):
                    raise ValueError(f"median disagrees with samples: {panel['id']}/{arm}")
    return panels


def _draw(panels: list[dict], paths: list[Path]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MaxNLocator

    with plt.rc_context(STYLE):
        figure, axes = plt.subplots(1, len(panels), figsize=(7.0, 1.8))
        for panel, axis in zip(panels, axes):
            if panel["id"] == "gpreempt":
                # Keep the two request-rate groups in the compact figure;
                # continuous-load measurements remain in the data and prose.
                visible = [i for i, group in enumerate(panel["groups"])
                           if group["label"] != "cont."]
                panel = dict(panel, groups=[panel["groups"][i] for i in visible],
                             samples=[panel["samples"][i] for i in visible])
            n_arms = max(sum(1 for key, _ in LEGEND if key in group)
                         for group in panel["groups"])
            span = .7
            step = span / (n_arms - 1) if n_arms > 1 else 0.0
            width = span / n_arms * .95
            for group_index, group in enumerate(panel["groups"]):
                arms = [key for key, _ in LEGEND if key in group]
                for slot, arm in enumerate(arms):
                    center = group_index + (slot - (len(arms) - 1) / 2) * step
                    style = {"hatch": "///", "edgecolor": "#404040",
                             "linewidth": .3} if arm == "baseline" else {}
                    axis.bar(center, group[arm], color=COLORS[arm],
                             width=width, **style)
                    if "samples" in panel:
                        values = panel["samples"][group_index][arm]
                        axis.errorbar(center, group[arm],
                                      yerr=[[group[arm]-min(values)], [max(values)-group[arm]]],
                                      color="#222222", capsize=2, linewidth=1, fmt="none")
            top = max(g[k] for g in panel["groups"] for k in g if k != "label")
            if "samples" in panel:
                top = max(v for sample in panel["samples"] for values in sample.values() for v in values)
            axis.set_ylim(0, top * 1.22)
            axis.set_xticks(range(len(panel["groups"])),
                            [g["label"] for g in panel["groups"]])
            if panel["id"] == "hummingbird":
                axis.set_xticklabels([{"periodic": "Per.", "BurstGPT": "Burst"}.get(
                    g["label"], g["label"]) for g in panel["groups"]])
            if panel["id"] == "gpreempt":
                axis.tick_params(axis="x", labelrotation=55)
                for label in axis.get_xticklabels():
                    label.set_horizontalalignment("right")
            if "xlabel" in panel:
                axis.set_xlabel(panel["xlabel"])
            axis.set_ylabel(panel["metric"])
            axis.set_title(panel["title"], fontsize=7, pad=3)
            axis.yaxis.set_major_locator(MaxNLocator(nbins=4))
            axis.ticklabel_format(axis="y", style="plain", useOffset=False)
            axis.grid(axis="y", alpha=.25, linewidth=.6)
        handles = [Line2D([0], [0], color=COLORS[key], marker="s", markersize=5,
                          linewidth=0, label=label) for key, label in LEGEND]
        figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, 1.02),
                      ncol=3, frameon=False, handlelength=1.1,
                      handletextpad=.4, columnspacing=1.0)
        if len(panels) == 7:
            figure.subplots_adjust(left=.06, right=.995, bottom=.31, top=.69, wspace=.95)
        else:
            figure.tight_layout(rect=(0, 0, 1, .94), h_pad=1.0, w_pad=1.5)
        try:
            for path in paths:
                figure.savefig(path, dpi=300)
        finally:
            plt.close(figure)


def render(panels_path: Path, prefix: Path) -> list[Path]:
    panels = load_panels(panels_path)
    paths = [prefix.with_suffix(suffix) for suffix in (".pdf", ".png")]
    if any(path.exists() for path in paths):
        raise FileExistsError("output exists; choose a new explicit figure prefix")
    prefix.parent.mkdir(parents=True, exist_ok=True)
    _draw(panels, paths)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panels", type=Path, default=HERE / "matched-policy-panels.json")
    parser.add_argument("--output-prefix", type=Path,
                        default=HERE / "matched-policy-panels")
    args = parser.parse_args()
    outputs = render(args.panels, args.output_prefix)
    print("\n".join(str(path) for path in outputs))
