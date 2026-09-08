# Memory and scheduling composition plot

`plot_memory_composition.py` reads `memory-composition-data.json` and writes
`memory-composition.pdf`. Run it with Python, matplotlib, and NumPy.

The JSON retains all five observations per configuration from each of the three
2026-09-08 combined-comparison CSVs. Its source paths are relative to the main
repository's `docs/` directory. The original five comparison entries and the
single-process baseline are copied from the original 2025-12-08 CSVs. They are
not pooled with the new observations. The original PDF remains unchanged.

New completion times use the shared release timestamp and independently observed
process exits, with policies attached before CUDA initialization. They include
initialization, two benchmark warmups, one measured iteration, and termination.
The original runner starts its timer before process creation and observes exits
with sequential waits. The plot retains the original five configurations and adds only scheduling-only
and combined policies from the new experiment. These last two bars form the
matched comparison. Fresh no-policy and memory-only observations remain in the
JSON but are not plotted. Historical and new bars are not paired.

For each new configuration, the lower segment ends at the median first-completion
time. The complete bar ends at the median last-completion time. The upper segment
is the difference of those endpoints, not an independently averaged duration.
Whiskers span the five observed last-completion times. In all new scheduling-only and combined runs, the high-priority process
finishes first, so the lower segment ends at median high-priority completion.
The original Single 1× and 2×Single 1× lines extend only across the original group.

The text reports the median of five within-run relative reductions in
high-priority completion time for combined versus scheduling-only policies:
10.376621% (HotSpot), 2.313002% (GEMM), and 1.357259% (K-Means).
