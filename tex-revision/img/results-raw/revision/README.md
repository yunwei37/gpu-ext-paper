# Matched scheduling figure

`scheduling-comparison-lc-bars.pdf` is the earlier separate figure: a single-column
two-panel rendering of LC latency (XSched and GPreempt workloads), rendered
by `workloads/gpreempt/plot_scheduling_comparison_lc.py` from the published
per-point data below. The paper reports the LC latency metric for these policy ports.

`scheduling-comparison-1x4-bars.pdf` is an earlier full-width four-panel bar
rendering (including BE panels), rendered by
`workloads/gpreempt/plot_scheduling_comparison_bars.py` from the same data.

`scheduling-comparison-2x2.pdf` (29,336 bytes) is the earlier, data-generated
four-panel figure from gpu_ext, not a hand-entered plot. The original source,
all per-cell points and complete caption are published together under
`workloads/gpreempt/` in that repository:

- `plot_scheduling_comparison.py`
- `figures/scheduling-comparison-2x2.points.json`
- `figures/scheduling-comparison-2x2.caption.md`
- `results-load-study-575-20260903.md`

Source publication: gpu_ext commit `17c245b` retains those existing files and
the linked complete XSched and GPreempt raw audits. Regeneration uses the
script's documented arguments and the original raw-data paths. Do not type
new values into this PDF. The paper includes the 7.2-inch vector canvas at its
full text width; verify the final printed scale in a fresh paper build.

## Matched policy ports

`matched-port-panels.pdf` reports one metric per policy component.
Regenerate the earlier five-panel version with
`python plot_port_panels.py --panels port-panels.json --output-prefix /tmp/matched-ports`.
`port-panels.json` names each source report in gpu_ext and retains the plotted
values. FineMoE uses all-positive prefetch as its comparison baseline;
POD uses the Llama decode batch-128 case, not a ten-shape average.

2026-09-07 layout follow-up: grouped bars no longer overlap across the two
Hummingbird arrival patterns; baseline bars have a grayscale hatch. The
canvas is 7.0 inches wide to match the current paper's full text width and
retain 7 pt labels. Plotted values and the current baseline selection are
unchanged. The earlier figures remain in gpu_ext's `workloads/matched-ports/figures/`;
the current dated version is `matched-port-panels-baselines-20260907-print`.
Two `pdflatex` passes complete at 16 pages with no undefined references or
citations; this figure appears on page 12. This is a rendering fix, not new
performance evidence or a claim that every selected policy beats no policy.

## Device-side observability with GPU buffering

`obs-overhead-with-array.pdf` extends the revision observability comparison
with the completed five-pair GPU-local-buffer campaign. Original P40 values
are unchanged; the RTX 5090 gpubpf kernelretsnoop bar uses the five-pair
result (5.572554%). All earlier ten-pair measurements remain in the JSON and
the previous figure, including the superseded kernelretsnoop result. The five pairs use
their own uninstrumented baseline; they were measured separately from the
NVBit and original gpubpf campaign. Only prefill throughput is plotted; final
collection averages 10.379343 ms and is outside that timing window.

`obs-with-array-data.json` records every plotted pair and source paths.
`plot_obs_with_array.py` derives percentages from the original baseline/tool
throughputs and verifies them against the campaign summaries. To regenerate
from the enclosing gpu_ext checkout without overwriting existing outputs:

```sh
python tex-revision/img/results-raw/revision/plot_obs_with_array.py --output-prefix /tmp/obs-buffer --data-output /tmp/obs-buffer-data.json
```

The plot retains the earlier two-panel grouped-bar layout. Bars show means;
whiskers show the full RTX 5090 run ranges, including the launchlate range
below zero. Only gpubpf and NVBit appear in the legend; the selected
kernelretsnoop measurement uses GPU buffering without a separate series.
P40 retains the original reported values. The single-column vector canvas is
3.4 inches wide with 7--7.5 pt text. The previous `obs-overhead-bars.pdf` is kept.

## Combined seven-policy figure

`matched-policy-panels.pdf` combines the former Figures 16 and 17 in one
seven-panel row at the paper's 7-inch text width, with 7 pt labels. The
workload baseline, native policy, and BPF port share one legend.

`matched-policy-panels.json` retains the first figure's values except for
Expert Buffering's selected metric: completed whole-expert demand loads,
13,304 for FIFO and 11,595 for both policies (12.85% fewer, K=16). These
are workload transfers, counted identically in all five cohorts per arm.
The original throughput values remain in `port-panels.json`. MoE-Infinity
latency is displayed in seconds instead of milliseconds.

XSched and GPREEMPT medians are derived from the per-run samples in
`workloads/gpreempt/figures/scheduling-comparison-2x2.points.json`. The merged
figure keeps both previously plotted BE rates and adds the already measured
continuous-load group used by the GPREEMPT paragraph. Raw plotted samples
are copied into the panel data, and whiskers show their full ranges.

Regenerate from this directory with:

```sh
python plot_port_panels.py --output-prefix /tmp/matched-seven
```

No new experiment was run. The earlier figure PDFs and five-panel data remain
available; the paper references the combined figure.
