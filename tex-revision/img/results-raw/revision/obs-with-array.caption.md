# obs-overhead-with-array — caption and reproduction

## Caption (self-contained)

Device-side observability overhead is prefill throughput loss expressed as
a percentage of the uninstrumented baseline throughput in that campaign:
each measurement uses its own campaign baseline (the RTX 5090
panel shows two independent campaigns), and no baselines are pooled across
campaigns. Panels are horizontal dot/range plots on a symlog axis
(linear between -1 and +1, logarithmic beyond), so negative paired values
are shown as measured rather than clamped. (a) P40, Llama 1B
sequence-mixed llama.cpp prefill: published submitted-paper values
(historical), gpubpf 8% versus NVBit 85% (kernelretsnoop), 3% versus 87%
(threadhist), and 14% versus 93% (launchlate); these are single published
points and no per-pair variance was recorded for them, so none is shown.
(b) RTX 5090, TinyLlama-1.1B Q4_K_M llama.cpp pp512 prefill. Original
three-tool campaign, ten paired blocks per arm (n = 10): dots are the ten
paired measurements, the horizontal bar spans min to max, and the tick
marks the arm mean. gpubpf is 90.71% (90.54-91.07), 2.97% (2.33-3.89), and
0.22% (-0.64 to +1.23; four of the ten pairs are negative and are shown
left of zero) for kernelretsnoop, threadhist, and launchlate; NVBit is
99.62% (99.62-99.63), 10.35% (8.45-13.62), and 8.80% (6.89-11.36).
Diamonds mark the completed GPU-local-array kernelretsnoop optimization, an
independent campaign of five paired blocks (n = 5) with its own
five-block baseline: mean 5.57%, range 4.02-6.70 (the five diamonds are
the five paired values; the bar is their range). It was not paired against
the older NVBit or gpubpf-ring runs, which were not re-run in that
campaign. The final bulk host lookup of the finite 23.2 MB
(23,199,768-byte) GPU-local array averages 10.379 ms (10.16-10.96) after
target completion and lies outside the prefill timing window; the array is
a finite buffer sized for this pp512 workload, not an unbounded or
concurrent-kernel streaming collector.

## Reproduction

The final canvas is 3.4 by 2.5 inches with unchanged 7.5 pt labels. This
compact rendering removes vertical whitespace from the earlier 3.2-inch-high
version without changing plotted measurements, axis scaling or font size.

Run from the gpu_ext root. The script refuses to overwrite existing
outputs, so write to a fresh directory instead of deleting anything:

    d=$(mktemp -d obs-with-array.XXXXXX)
    python3 docs/paper/tex-revision/img/results-raw/revision/plot_obs_with_array.py \
        --data-output "$d/obs-with-array-data.json" \
        --output-prefix "$d/obs-overhead-with-array"

The script reads:

- workloads/llama.cpp/observability_overhead/p40-submitted-table1.json
  (transcribed published P40 values, labelled historical in the output)
- workloads/llama.cpp/observability_overhead/revision-rq4/
  results-table1-warp-plt-575-06/cells.json and summary.json
  (ten rotated blocks, 70 cells)
- workloads/llama.cpp/observability_overhead/revision-rq4/
  results-onevalue-array-bootstrap-575-20260907/cells.json and summary.json
  (five paired blocks, storage gpu-array-onevalue)

Paired overhead per block is derived as 100*(baseline - tool)/baseline and
cross-checked against the recorded per-cell overhead_pct and the campaign
summaries; the script raises if any value disagrees. It writes
obs-with-array-data.json (all per-pair values, means, ranges, baselines,
and provenance), obs-overhead-with-array.pdf, and obs-overhead-with-array.png
to the directory named by --data-output / --output-prefix (a copy of each
output is tracked next to the script). The
final-lookup statistics are transcribed from the new campaign's README
per-block table and are recorded under rtx5090_gpu_array.final_lookup_ms.
The older obs-overhead-bars.pdf and all recorded campaign data are not
modified.
