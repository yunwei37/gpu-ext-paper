# Revision response draft for the shepherd (unsubmitted — 2026-09-07)

Status. Draft for author review, not submitted to the conference and not a
completion report. It answers the Aug 3/Aug 14 comments
([revision-comments.md](revision-comments.md)) against the original
[Q1–Q15 response](rebuttal.md). Not all comments are closed (see end). Live
status: the [completion checklist](../../revision-completion-checklist.md),
dated [revision plan](revision-plan.md),
[build review](revision-build-review.md). Current build: 17 pages,
conclusion on page 15.

## Q1 — scoped comparisons with published systems (Reviewers E, F)

Completed scoped comparisons cover MoE-Infinity, XSched, GPREEMPT, the
LMCache local-disk backend, Expert Buffering, FineMoE, Hummingbird and
POD-Attention, each labelled by scope. The seven policy ports implement
**selected published algorithms**, running native and gpubpf variants
through shared executors. LMCache supplies the disk-transport baseline;
our additional storage-admission policies are not reimplementations of an
LMCache paper algorithm. These comparisons do not establish original-system
reproduction or equivalence; each report identifies reused artifacts and
ported components.

- **XSched** (46 cells): baseline/original/BPF LC p99
  76.8780/26.9784/27.2502 s; BE 10.2377/10.1497/10.1616 kernels/s. The
  original artifact executes suspend/resume; BPF makes the bounded HPF
  decision; Level-1 only on sm_120
  ([report](../../../workloads/xsched/performance-full-575-20260903.md)).
- **GPREEMPT** (45-cell load study, 27-cell knee sweep): host-mapped
  compatibility port with original C decisions; under continuous background
  load, LC p99 native→C→BPF is
  1.795937/1.614817/1.610008 ms; not GDRCopy/hardware reproduction;
  conditional overload at 800 req/s retained
  ([load](../../../workloads/gpreempt/results-load-study-575-20260903.md),
  [knee](../../../workloads/gpreempt/results-lc-knee-575-20260903.md)).
- **MoE-Infinity** (15 cells): baseline/native/BPF
  11.8964/11.2233/11.1900 token/s; BPF/native 0.996540 [0.989239, 1.005508].
  Ported algorithm; the workload baseline has a prefill overload shortcut,
  so not a pure policy contrast
  ([report](../../../workloads/moe-infinity/results-paper-v3-protected-575.md)).
- **LMCache local disk**: the five-arm serving study (25 cells) is an
  all-submit mechanism-floor configuration, not an active policy-benefit
  result: BPF/native throughput median +0.2795%, min–max −3.42%…+5.17%
  ([five-arm](../../../workloads/lmcache-disk/results-575-lmcache-gds-five-arm-20260906.md)).
  Later variants retain adverse/mixed pairs: polling **read p99** worsens
  in all five BPF/native pairs, median +23.601% (not identical per block);
  every variant is preserved with its retained older numbers
  ([polling](../../../workloads/lmcache-disk/results-575-gds-mixed-live-feedback-20260907.md),
  [event](../../../workloads/lmcache-disk/results-575-gds-live-event-driven-20260907.md),
  [scheduled](../../../workloads/lmcache-disk/results-575-gds-mixed-scheduled-20260907.md)).
  The active policy comparison is the write-budget study below.
- **Expert Buffering** (15 cells): FIFO improvement native 2.55% [2.10, 3.09]
  / BPF 1.79% [0.79, 2.81]; BPF 0.74% [0.20, 1.40] slower than the identical
  native algorithm — a measured mechanism cost; not the original distributed
  system
  ([report](../../../workloads/expert-buffering-policy/section-vi/results-performance-575-20260903.md)).
- **FineMoE** (20 cells): the faster demand-only baseline (5.17 vs
  4.50/4.51 token/s) is integrated alongside the retained all-positive
  improvement ([report](../../../workloads/finemoe/results-performance.md)).
- **Hummingbird** (50 cells): periodic-arrival BE goodput, default baseline 179.23 →
  idle C/BPF 133.22/133.05 req/s, ≈19–20% below fixed GPreempt — not a
  reproduction of Hummingbird's headline benefit
  ([report](../../../workloads/hummingbird/results-575-20260903.md)).
- **POD-Attention** (250 operator cells plus phase campaign): BPF/CUDA
  latency −0.44%…+1.18% across ten shapes; phase study 1.78%/1.81% cost;
  non-generic fresh-process cold path explicit
  ([report](../../../workloads/pod-attention/results-575-20260903.md)).

## Q2 — safety and design depth (Reviewers B, F)

[design.tex](../tex-revision/tex/design.tex) adds transition-validation
pseudocode, the SIMT verifier description with rejected-policy examples, a
failure-mode taxonomy, and a TCB paragraph scoped to host OS, driver and
firmware, verifiers/toolchain, and gpubpf hooks;
[implementation.tex](../tex-revision/tex/implementation.tex) describes
Linux verifier + PREVAIL + uniformity/SIMT checks. Scoped evidence: the
CPU-only aggregate matrix passes six unsafe/control pairs yet marks the
host-verifier/driver-validator layers `NOT_RUN`; invalid-prefetch live
controls show exact native fallback and exact UVM/service restoration; the
scheduler-init matrix passes 16/16; the loader audit shows STRICT rejecting
invalid programs without consuming an ID. One-time admission cost
(141.266 ms `kernelretsnoop`, 11.767 ms `threadhist`) and the
shape-sensitive verifier-scaling boundary (exponent 1.3841, contradicting
the linear model) are reported; S0 finds no detected STRICT-vs-NO_VERIFY
difference with no preregistered equivalence margin, so no zero-overhead
claim. Table 1/array runs use the warning-mode runtime (map-pointer
warnings retained): performance evidence, not strict-admission evidence.

## Policy versus mechanism (Reviewer F)

- Attribution: abstract/intro state headline throughput/tail numbers are
  policy gains and name measured mechanism costs (0.7% Expert Buffering,
  POD −0.44%…+1.18%, 3.219% UVM fault path, mixed storage effects)
  ([main.tex](../tex-revision/main.tex),
  [intro.tex](../tex-revision/tex/intro.tex); paper commits `2d0441d`,
  `46220f2` for the body/design grouping and
  [\S policy-mechanism](../tex-revision/tex/eval.tex) cost section).
- Versus original implementations: XSched's artifact and GPREEMPT's C
  decisions are compared directly, retaining the small same-policy deltas.
- Expressibility is tabulated from the confirmed 52-paper, seven-family
  ledger; no surveyed whole system is fully expressible
  ([ledger](../../experiment/policy/reference/RELATED_POLICY_EXPRESSIBILITY.md)).
- Fig. 13 is expanded to four panels from the fresh five-block, 20-cell
  measurement (paper commit `39ceb61`), retaining all three historical
  panels; the old sub-1% scheduling inference is qualified by a measured
  priority tradeoff: combined vs scheduling-only improves high priority
  −10.166% median and slows low priority +6.299% — a tradeoff, not an
  all-metrics win
  ([report](../../../workloads/fig13-fast/results-performance-575-20260907.md)).
- Agentic insights in the evaluation: device-side tracing led the agent to
  stride prefetch aligned with per-layer expert weight layout plus LFU
  eviction protecting frequently accessed shared layers, and to
  region-differentiated weight/KV prefetch (stride for weights, sequential
  for KV) under a PCIe-utilization budget, avoiding the mutual thrashing a
  uniform policy causes. The shared storage write budget is a budget-setting
  finding, not a novel paper algorithm nor uniquely enabled.

## Measurements, artifacts, and discussion (Reviewers A, D, E)

- Table 1 is complete for all three tools on the RTX 5090 (10 blocks, 70
  cells): gpubpf/NVBit overhead 90.7051/99.6210% (`kernelretsnoop`),
  2.9653/10.3501% (`threadhist`), 0.2208/8.7959% (`launchlate`); P40 values
  retained ([README](../../../workloads/llama.cpp/observability_overhead/revision-rq4/results-table1-warp-plt-575-06/README.md)).
  The independent five-pair, complete-record array lowers mean paired
  prefill overhead to 5.5726% (range 4.0175–6.7050%), with all 720,896
  records per tool run; final bulk lookup 10.379 ms, reported outside
  prefill timing; earlier ring variants and failed attempts remain retained
  ([README](../../../workloads/llama.cpp/observability_overhead/revision-rq4/results-onevalue-array-bootstrap-575-20260907/README.md)).
- **Write-budget study** (25 cells, 4,000 requests) — the active LMCache
  policy comparison: raising the shared-executor budget 10→200 ms lowers
  paired BPF read p99 by median 51.011% and raises write throughput 15.315%
  — throughput, not latency — in all five pairs; native also improves
  (53.999%/12.698%). BPF/native p99 stays mixed (−39.718%…+33.849%); no
  tight equivalence; real cuFile compatibility-mode disk, GPU-direct P2P
  not proven
  ([report](../../../workloads/lmcache-disk/results-575-gds-write-budget-20260907.md)).
- Stale state: all 21 cells plus phase-aligned analysis (15,747,386
  decisions) complete: a 1000 ms delay reduces paired throughput
  23.192%/22.684%, decision-weighted wrong-phase fractions 88.708%/88.854%;
  driver thrashing counters zero. Measured sensitivity — no observed
  driver-classified thrashing, no evaluated adaptive mitigation
  ([report](../../../workloads/stale-state-575/results-performance-gds-20260907.md)).
- SASS/PTX-free: EXIT-site injection executes compiler-generated BPF inside
  one existing cubin-only application (two EXIT sites, 100,352 per-thread
  outputs, expected output, exit zero)
  ([result](../../../workloads/sass-kretprobe/results/sass-exit-575-20260907-01/results.md));
  general helpers/maps, late attach, concurrent launches, performance
  parity unestablished; standalone AOT is a separate boundary
  ([note](../../experiment/revision-sass-aot-readiness-20260904.md)); NVBit
  supplies the trusted binary instrumentation.
- Discussion groups stale state, CXL, per-tenant, trampoline and
  portability points; the trampoline fixed-work study is inconclusive (no
  independence claimed); the warp-map scaling negative result stays
  repository evidence; the text distinguishes software co-location from the
  static partitioning the SemiAnalysis critique targets.
- Artifacts: agent prompts and benchmark harnesses are published; original
  historical transcripts remain missing, so we do not claim the originals
  are released; newly authored templates are labelled as such.
- Typography: double paragraph-heading periods and printed bibliography
  braces fixed; remaining bibliography metadata warnings are not a
  completed citation audit.

## Before submission

Remaining requirements: recovery of the original historical agent
transcripts (prompts/harnesses are out), and final
presentation/submission work including page-budget fitting. Disclosed
limits and future extensions — not new promises: GPU-direct P2P, general
SASS helpers/maps/late attach, per-tenant and CXL implementations, adaptive
freshness mitigation. This draft does not claim every reviewer or shepherd
comment is closed.
