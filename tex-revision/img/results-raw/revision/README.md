# Matched scheduling figure

`scheduling-comparison-1x4-bars.pdf` is the current four-panel bar figure
(bars are within-workload medians). It is rendered by
`workloads/gpreempt/plot_scheduling_comparison_bars.py` from the published
per-point data of the earlier 2x2 figure.

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
