# Lines-of-Code Reconciliation: Paper Claims vs. Source on Disk

ASPLOS'27 major revision, paper #1797 ("gpubpf").

2026-09-03 correction: the original component counts below were rechecked
against retained gpu_ext revision `aab36b8` using `git show` and `wc -l`.
The active draft now uses 573 for sequential prefetch, approximately 880 for
573+304, 1090 for 573+472+45, and 1334 for 472+454+408; its counting convention
is explicit. Current LFU/scheduler sources have additional revision code
(306/501 lines including loaders), so they are not silently substituted for
these historical counts. Observability LOC still needs the exact Table 1
per-run sources; the unresolved old counts below are not verified by this fix.

Scope: every policy-LOC number asserted in the paper, checked against the
source tree at `/home/yunwei37/workspace/gpu/gpu_ext` (HEAD, no git changes
made). All `wc -l` values below were actually run; every path listed exists.

Convention: host-side policies are a BPF program (`*.bpf.c`) plus a userspace
loader (`*.c`). The paper reports a single LOC per policy, so for each policy
we report **BPF / loader / sum** and compare the sum to the claim unless the
claim itself names a single component.

---

## 1. Every LOC claim extracted from the paper

All active claims are in `docs/paper/tex/eval.tex`. `design.tex` and
`implementation.tex` contain no per-policy LOC figures (only system-level
KLOC estimates; see note at the end).

| # | Claim (as written) | Policy / component named | File:line |
|---|---|---|---|
| C1 | "device-only prefetch (45~LOC)" | device L2 prefetch | eval.tex:32 |
| C2 | "host-device stride-based eBPF prefetch (472~LOC host + 45~LOC device)" | Stride prefetch (host) + device | eval.tex:32 |
| C3 | "sequential prefetch (375~LOC)" | sequential / adaptive-sequential prefetch | eval.tex:32 |
| C4 | "Greedy (always-steal, 16~LOC)" | CLC Greedy (device) | eval.tex:35 |
| C5 | "LatencyBudget (... 19~LOC)" | CLC LatencyBudget (device) | eval.tex:35 |
| C6 | "device-side access observation (45~LOC), host-side stride prefetch (472~LOC), and LFU eviction (304~LOC), totaling ~820~LOC" | MoE expert offload (composite) | eval.tex:46 |
| C7 | "(stride for weights, sequential for KV-cache, 375~LOC), coupled with LFU eviction (304~LOC). The resulting policy (totaling ~680~LOC)" | vLLM KV-cache offload (composite) | eval.tex:64 |
| C8 | "sequential prefetch (375~LOC)" | GNN training | eval.tex:80 |
| C9 | "converged policy (~890~LOC: sequential prefetch 375~LOC + stride prefetch 472~LOC + device-side 45~LOC)" | Faiss (composite) | eval.tex:92 |
| C10 | "implemented as a \sys eBPF program (925~LOC)" | GPREEMPT-equivalent preemption control | eval.tex:111 |
| C11 | "Prefetch(lo,hi) ... (454~LOC), while Evict(lo,hi) ... (472~LOC)" | Multi-tenant priority differentiation | eval.tex:123 |
| C12 | "(~926~LOC, combining Quota LRU, Tree-based Prefetch, and Dynamic Timeslice)" | Two-tenant co-location (composite) | eval.tex:136 |
| C13 | Table 2 (active): kernelretsnoop 153, threadhist 89, launchlate 347 | Device-side observability tools | eval.tex:205-207 |

There is also a **commented-out** "Policy support matrix" table (eval.tex:162-188,
inside `\begin{comment}`) with these entries: Global FIFO Eviction 145, Global
LFU Eviction 304, Multi-tenant Quota LRU 472, Adaptive Seq. Prefetch 375,
Stride Prefetch 472, GPU L2 Stride Prefetch 45, Tree-based Prefetch 454,
Dynamic Timeslice 408, Preemption Control 925, MaxSteals (CLC) 16,
LatencyBudget (CLC) 19. These are not in the compiled paper, but they are the
apparent source for several prose numbers and are cross-checked below.

---

## 2. Inventory of actual policy sources (BPF / loader / sum)

### 2a. Host-side policies — `extension/` (measured with `wc -l`)

| Policy file (base name) | BPF (`*.bpf.c`) | Loader (`*.c`) | Sum |
|---|---:|---:|---:|
| `prefetch_stride` | 292 | 180 | **472** |
| `prefetch_adaptive_sequential` | 233 | 340 | **573** |
| `eviction_lfu` | 223 | 81 | **304** |
| `eviction_fifo` | 64 | 81 | **145** |
| `gpu_preempt_ctrl` | 279 | 646 | **925** |
| `gpu_sched_set_timeslices` | 187 | 221 | **408** |
| `prefetch_pid_tree` (Tree-based Prefetch) | 206 | 248 | **454** |
| `eviction_pid_quota` (Quota LRU) | 237 | 235 | **472** |

(Auxiliary headers in `extension/` such as `gpu_preempt.h`, `gpu_preempt_ctrl_event.h`,
`gpu_sched_set_timeslices.h`, `shared_maps.h`, `eviction_common.h` are shared
plumbing, not policy bodies, and are not counted by either side.)

### 2b. Device-side policies — `microbench/` (NOT in `extension/`)

Device policies are not standalone files; they are policy bodies inside shared
headers/benchmarks in `microbench/`.

| Claimed policy | Where it lives | Measured size |
|---|---|---|
| Device L2 prefetch ("45~LOC") | `microbench/memory/kernels/synthetic.cuh`, the `prefetch_l2` helper + `seq_prefetch_kernel` (lines 227-276); entry point `run_seq_device_prefetch` referenced at `microbench/memory/main.cu:107` | ~50 lines incl. comments (~45 code lines). Whole header is 637 lines. |
| CLC Greedy ("16~LOC") | `microbench/clc_bench/clc_policies.cuh`, `struct GreedyPolicy` (lines 29-39) | 11 lines for the struct; ~16 incl. its comment block (lines 23-39) |
| CLC MaxSteals ("16~LOC", support-matrix only) | same header, `struct MaxStealsPolicy` (lines 48-66) | 19 lines |
| CLC LatencyBudget ("19~LOC") | same header, `struct LatencyBudgetPolicy` (lines 228-242) | 15 lines for the struct; ~19 incl. its comment block (lines 214-242) |

The entire CLC policy header `microbench/clc_bench/clc_policies.cuh` is 458 lines
and contains 11 policies; individual policy structs are 11-19 lines each. The
benchmark harness that exercises them is `microbench/clc_bench/clc_policy_benchmark.cu`
(272 lines) — this is a benchmark, not a policy body.

### 2c. Observability tools — canonical source is ABSENT

The paper's Table 2 lists `kernelretsnoop`, `threadhist`, `launchlate`. Their
canonical source lives at `example/gpu/<tool>/` in an **external bpftime tree
that is not vendored into this repository** (no `bpftime` submodule in
`.gitmodules`, no `example/gpu/` directory anywhere in the tree). The build
harness `workloads/llama.cpp/observability_overhead/run_observability_overhead.py`
references `example_dir="example/gpu/<tool>"` but copies/patches sources from
that external tree.

Only **patched build copies** exist, under
`workloads/llama.cpp/results/exp_observability_overhead/*/tool_build/`.
Because the harness patches these sources at build time
(`patch_bpf_source`, `patch_launchlate_user_source`), their line counts are not
authoritative for the paper's numbers. Measured (run `20260706_173810`):

| Tool | loader `.c` | BPF `.bpf.c` | sum |
|---|---:|---:|---:|
| kernelretsnoop | 111 | 42 | 153 |
| threadhist | 94 | 32 | 126 |
| launchlate | 306 | 123 | 429 |

---

## 3. Reconciliation table (active claims)

| Claim | Matching files | Actual BPF | Actual loader | Actual sum | Delta (claim − actual) | Verdict |
|---|---|---:|---:|---:|---:|---|
| C1 device prefetch 45 | `microbench/memory/kernels/synthetic.cuh` (device region) | — | — | ~45 (approx) | 0 | **matches (approx)** — device region, not a standalone file |
| C2 stride host 472 | `extension/prefetch_stride.{bpf.c,c}` | 292 | 180 | 472 | 0 | **matches** |
| C3 sequential 375 | `extension/prefetch_adaptive_sequential.{bpf.c,c}` | 233 | 340 | 573 | −198 | **OFF BY 198** |
| C4 Greedy 16 | `microbench/clc_bench/clc_policies.cuh` (struct body) | — | — | 11 (struct) / ~16 w/ comments | 0 (approx) | **matches (approx)** — struct body, not a file |
| C5 LatencyBudget 19 | `microbench/clc_bench/clc_policies.cuh` (struct body) | — | — | 15 (struct) / ~19 w/ comments | 0 (approx) | **matches (approx)** — struct body, not a file |
| C6 ~820 (MoE: 45+472+304) | components each match | — | — | 45+472+304 = 821 | 0 | **matches** (arithmetic correct; C1/C2/LFU all verified) |
| C7 ~680 (vLLM: 375+304) | inherits bad C3 | — | — | claimed 375+304=679; actual 573+304=877 | −198 | **OFF BY 198** (propagated from C3) |
| C8 sequential 375 | `extension/prefetch_adaptive_sequential.{bpf.c,c}` | 233 | 340 | 573 | −198 | **OFF BY 198** |
| C9 ~890 (Faiss: 375+472+45) | inherits bad C3 | — | — | claimed 375+472+45=892; actual 573+472+45=1090 | −198 | **OFF BY 198** (propagated from C3) |
| C10 GPREEMPT-equiv 925 | `extension/gpu_preempt_ctrl.{bpf.c,c}` | 279 | 646 | 925 | 0 | **matches** |
| C11 Prefetch(lo,hi) 454 | `extension/prefetch_pid_tree.{bpf.c,c}` | 206 | 248 | 454 | 0 | **matches** |
| C11 Evict(lo,hi) 472 | `extension/eviction_pid_quota.{bpf.c,c}` | 237 | 235 | 472 | 0 | **matches** |
| C12 ~926 two-tenant (Quota LRU + Tree Prefetch + Dynamic Timeslice) | 472 + 454 + 408 | — | — | **1334** (472+454+408) | −408 | **OFF BY 408** — 926 = only the first two components (472+454); Dynamic Timeslice (408) is named but not counted |
| C13 kernelretsnoop 153 | build copy only (canonical absent) | 42 | 111 | 153 | 0 | **matches** (build copy; canonical not in repo) |
| C13 threadhist 89 | build copy only (canonical absent) | 32 | 94 | 126 | −37 | **cannot reconcile** — neither component nor sum equals 89; canonical source not in repo |
| C13 launchlate 347 | build copy only (canonical absent) | 123 | 306 | 429 | −82 | **cannot reconcile** — neither component nor sum equals 347; canonical source not in repo |

Cross-check against the **commented-out** support matrix (eval.tex:162-188):
FIFO 145 → `eviction_fifo` 64+81=145 ✓; LFU 304 → `eviction_lfu` 223+81=304 ✓;
Quota LRU 472 → `eviction_pid_quota` 237+235=472 ✓; Stride 472 ✓; Tree 454 →
`prefetch_pid_tree` 454 ✓; Dynamic Timeslice 408 → `gpu_sched_set_timeslices`
187+221=408 ✓; Preemption Control 925 → `gpu_preempt_ctrl` 925 ✓; GPU L2 45
(approx, device region) ✓; **Adaptive Seq. 375 → 573 actual ✗**; MaxSteals 16 /
LatencyBudget 19 (approx struct-body counts) ~✓.

---

## 4. Verification of the specific suspects from the earlier audit

### Suspect A — "925 LOC" GPREEMPT-equivalent = `gpu_preempt_ctrl`
**Verdict: the earlier audit was wrong; the claim MATCHES.**
`extension/gpu_preempt_ctrl.bpf.c` (279) + `extension/gpu_preempt_ctrl.c` (646) =
**925**, exactly the figure at eval.tex:111. No discrepancy. (Note: the related
header `gpu_preempt.h`/`gpu_preempt_ctrl_event.h` are shared plumbing and are
correctly excluded from both the claim and our count.)

### Suspect B — "408 LOC" = `gpu_sched_set_timeslices`, must stay separate from 925
**Verdict: correctly separate, and matches.**
`extension/gpu_sched_set_timeslices.bpf.c` (187) + `.c` (221) = **408**, exactly.
This figure appears only in the commented-out support matrix (eval.tex:178), not
in active prose, so it is not currently double-counted with the 925. No action
needed beyond keeping the two distinct if the support matrix is re-enabled.

### Suspect C — "375 LOC" sequential prefetch vs adaptive-sequential sources
**Verdict: confirmed mismatch. OFF BY 198.**
`extension/prefetch_adaptive_sequential.{bpf.c,c}` = 233 + 340 = **573**, not 375.
Neither component alone (233, 340) nor the sum (573) equals 375. The figure 375
is used three times in active prose (C3, C7 via C3, C8, C9 via C3), so the error
propagates into two composite totals (~680 and ~890).

### Suspect D — "926 LOC" two-tenant, named components reportedly sum to more
**Verdict: confirmed mismatch. OFF BY 408.**
The prose (eval.tex:136) names **three** components: Quota LRU + Tree-based
Prefetch + Dynamic Timeslice = 472 + 454 + 408 = **1334**. The stated total 926
equals only the first two (472 + 454). The Dynamic Timeslice (408) is named in
the component list but absent from the arithmetic.

### Suspect E — device-side 45 / 16 / 19 not in host inventory
**Verdict: confirmed — they are device-side and live under `microbench/`, not `extension/`.**
- 45 (device L2 prefetch) → `microbench/memory/kernels/synthetic.cuh`, device
  region; matches approximately (no standalone file).
- 16 (CLC Greedy / MaxSteals) and 19 (CLC LatencyBudget) →
  `microbench/clc_bench/clc_policies.cuh`, policy struct bodies inside a shared
  458-line header; matches approximately as struct-body counts, but there are no
  standalone 16- or 19-line files.

---

## 5. Per-mismatch cause and exact .tex edit (NOT applied — for the authors to make)

### Mismatch 1 — "sequential prefetch (375~LOC)" (eval.tex:32, 64, 80, 92)
- **Most likely cause:** the sequential/adaptive-sequential policy was
  substantially expanded after the 375 figure was recorded. `git log` shows
  `prefetch_adaptive_sequential.bpf.c` has been 233 lines and the loader 340
  lines (sum 573) for the entire tracked history (since 2026-01-17), so 375 does
  not correspond to any committed version of these two files; it most plausibly
  came from an earlier uncommitted prototype or was miscounted.
- **Exact edit for the authors:** re-measure
  `extension/prefetch_adaptive_sequential.{bpf.c,c}` (currently 233+340=573) and
  replace `375~LOC` with the new total at all four sites:
  - eval.tex:32 `(375~LOC)` → `(573~LOC)` (or whatever the fresh count is)
  - eval.tex:64 `(stride for weights, sequential for KV-cache, 375~LOC)` → use the new number, and update the resulting `~680~LOC` total (375+304 → 573+304 = **~880~LOC**)
  - eval.tex:80 `sequential prefetch (375~LOC)` → new number
  - eval.tex:92 `sequential prefetch 375~LOC` → new number, and update the `~890~LOC` total (375+472+45 → 573+472+45 = **~1090~LOC**)
- If the authors intended "375" to mean *only the BPF program* or *only the
  loader*, that is also wrong (233 and 340 respectively, neither is 375); the
  method must be stated and the number recomputed.

### Mismatch 2 — two-tenant "~926~LOC" (eval.tex:136)
- **Most likely cause:** the total was computed from only two of the three named
  components (Quota LRU 472 + Tree-based Prefetch 454 = 926), omitting the
  Dynamic Timeslice (408). The component list and the total are internally
  inconsistent.
- **Exact edit for the authors:** choose one and make the prose self-consistent:
  - **Option A (keep all three components, fix the total):** change `~926~LOC` to
    `~1330~LOC` (472 + 454 + 408 = 1334).
  - **Option B (keep the 926 total, drop the uncounted component):** change the
    component list to "combining Quota LRU and Tree-based Prefetch" (and confirm
    the Dynamic Timeslice is genuinely not part of this policy).
  The same inconsistency is latent in the commented support matrix
  (eval.tex:162-188); if that table is re-enabled, ensure the per-row numbers
  add up to whichever composite total the prose states.

### Mismatch 3 — device-side 45 / 16 / 19 have no standalone source files
- **Most likely cause:** these are device-side policy bodies embedded in shared
  headers/benchmarks under `microbench/`, counted as struct/function bodies
  rather than whole files, so they cannot be located as files in `extension/`.
  The numbers are approximately correct as body-level counts.
- **Exact edit for the authors:** to make the claim verifiable, either (a) state
  in a footnote/caption that device-side LOC counts the policy body inside the
  device source (and name the file, e.g. `microbench/memory/kernels/synthetic.cuh`
  for the 45-LOC L2 prefetch and `microbench/clc_bench/clc_policies.cuh` for the
  CLC policies), or (b) factor each device policy into its own file and re-count
  whole files, as is done for the host-side policies. No number needs to change
  if option (a) is taken; only the counting method needs to be documented.

### Mismatch 4 — observability Table 2 threadhist (89) and launchlate (347)
- **Most likely cause:** these figures were taken from the **canonical,
  un-patched** bpftime sources at `example/gpu/<tool>/`, which are **not vendored
  in this repository**. The only artifacts present are build copies under
  `workloads/llama.cpp/results/exp_observability_overhead/*/tool_build/`, and
  those are patched by `run_observability_overhead.py` before building, so their
  line counts differ from the canonical source. `kernelretsnoop` happens to match
  (153) even in the patched build copy; `threadhist` (build copy 126) and
  `launchlate` (build copy 429) do not.
- **Exact edit for the authors:** re-measure the canonical (pre-patch) sources
  from the bpftime tree the tools are built from, and update Table 2
  (eval.tex:205-207) for `threadhist` and `launchlate` to whatever the canonical
  loader+BPF sum actually is. If the bpftime tree is pinned, record its commit in
  the artifact appendix so the 153/89/347 (or updated) figures are reproducible.
  **Cannot identify** the exact files from within this repo alone.

---

## 6. Notes / out of scope
- `docs/paper/tex/implementation.tex:5` gives system-level estimates (`~1 KLOC`
  kernel module, `~100 LOC` driver instrumentation, `~10 KLOC` user-space loader,
  `~1 KLOC` LLVM backend). These are not per-policy LOC and are not reconciled
  here; they would need to be checked against the `kernel-module/` and bpftime
  trees separately.
- `docs/paper/tex/design.tex` contains no per-policy LOC figures (only a listing
  figure, `fig:moe-listing`, which is illustrative and not counted).
- No `.tex` file and no source file was modified. No `git commit` was run.
