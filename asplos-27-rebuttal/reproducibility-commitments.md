# ASPLOS'27 #1797 — Reproducibility & SOTA Comparison Commitments

**Paper:** gpubpf / gpu_ext (ASPLOS'27 submission #1797)  
**Workspace root:** `/home/yunwei37/workspace/gpu/gpu_ext`  
**Inventory revision:** 2026-08-03 (full re-audit; supersedes earlier draft of same date)  
**Audience:** authors drafting HotCRP revision plan / author response.

**Execution update, 2026-09-04:** The RTX 5090 Table~1 rerun now has a valid
two-tool, ten-block comparison for matched exit records and exit-count
histograms. The outcome is mixed: NVBit is 0.04185 percentage points
lower-overhead for the full record stream, while gpubpf is 6.29351 points
lower-overhead for the final histogram. This completes only the two
non-cross-clock rows. `launchlate` remains invalid, and the performance runtime
had GPU verification disabled. The submitted P40-only result was an evaluation
gap, not evidence that NVBit lacked Blackwell support.

The separate
[S0 verifier-mode campaign](../../../workloads/llama.cpp/observability_overhead/revision-rq4/device-verifier-s0/results-s0-575-02-20260904.md)
passes 6/6 pp32 correctness cells and 60/60 pp512 timing cells, with an
independent replay of all 66 raw directories. In ten randomized complete blocks
per tool, STRICT versus NO_VERIFY has mean/median throughput effects of
-0.0746%/-0.0376% for `kernelretsnoop` (95% mean CI [-0.7845%, +0.6086%]) and
+0.0037%/-0.1374% for `threadhist` ([-0.4233%, +0.4390%]). Both intervals span
zero, so no directional difference is detected; because no equivalence margin
was preregistered, the result proves neither equivalence nor zero verifier
overhead. Relative to uninstrumented controls, STRICT throughput is 99.6631%
lower for the full exit-record stream and 4.0729% lower for the histogram, so
the callbacks themselves are not free. This separate result does not relabel
the earlier Table 1 runtime as verifier-enabled. The retained `s0-575-01`
parser-gate failure contributes no sample.

---

## 0. Commitment tiers (read this first)

| Tier | Meaning for HotCRP | Examples |
|------|---------------------|----------|
| **Safe** | Already true in tree/paper, or pure writing/artifact packaging | Foreground GPREEMPT-equiv Fig.12; LMCache baseline language; expressibility table; safety expansion; agent prompts/harnesses |
| **Stretch** | Optional only after code+numbers exist; **do not** put in HotCRP as hard commitment | Gating-function uprobe for MoE; packaging named “gpreempt-equiv” artifact dir; sync-interval / grid-scaling microstudies |
| **Forbidden** | Over-promises we cannot honestly deliver in revision | Full Huang H2H / 6–11×; re-run thustorage/GPreempt driver artifact as acceptance; LithOS TPC experiments; “LMCache as eBPF”; multi-vendor ports; CXL/GDS prototype |

---

## 1. Purpose / How to Use for the HotCRP Plan

For every SOTA / related-work system reviewers (especially **E** and **F**) may demand:

> **What can we safely promise in the revision plan?**

| If the claim is… | Then… |
|------------------|--------|
| An in-tree `extension/*.bpf.c` policy already used in eval | Promise **foregrounding**, clearer presentation, or modest re-measurement on our harness |
| Expressible as gpubpf policy (priority, timeslice, hot-expert residency, PID quota) but **not** the original artifact | Promise **expressibility + our evidence**, **not** head-to-head re-run of their driver/OS artifact |
| Framework baseline we already compare (LMCache, vLLM offload, llama.cpp ncmoe) | Keep as **baseline comparison**; do **not** claim “implemented LMCache as eBPF” |
| No usable public artifact / wrong abstraction / whole-GPU OS | **Discussion / related work only** |

**Related local files (do not treat as authoritative without re-check):**

| Path | Role |
|------|------|
| `docs/paper/asplos-27-rebuttal/revision-plan.md` | Scratch checklist (incomplete; **this file supersedes it for SOTA promises**) |
| `docs/paper/asplos-27-rebuttal/rebuttal.md`, `rebuttal-v3.md`, `fable.md` | Draft author responses; some wording over-promises (see §7) |
| `docs/paper/asplos-27-rebuttal/review.txt` | Full HotCRP reviews |
| `docs/paper/tex/eval.tex` | Paper evaluation claims (LOC, GPREEMPT-equiv, LMCache, multi-tenant) |
| `docs/experiment/POLICY_OVERVIEW.md` | Human overview (**stale**: claims ~10 eviction / 9 prefetch; tree has 8 eviction + 28 prefetch primary) |
| `docs/paper-material/ref-paper/` | **Preferred** PDF set (`gpreempt_atc25.pdf`, `gcaps.pdf`, `lmcache.pdf`, `lithos_sosp25.pdf`, `neutrino_osdi25.pdf`, `xsched_osdi25.pdf`, …) |
| `docs/paper/asplos-27-rebuttal/ref/` | **Do not trust filenames** — several downloads are wrong papers (see §4.2) |
| `docs/eval/multi-tenant-memory/`, `docs/eval/multi-tenant-scheduler/` | Harnesses + CSVs used for multi-tenant numbers |
| `docs/eval/agent/` | Agent study notes (q1–q6) for artifact packaging |

**LOC convention**

- **Disk LOC** = last line of file via editor inventory (≈ `wc -l`; includes comments/headers).
- **Paper LOC** from `eval.tex` often means **BPF + userspace loader** (or an older snapshot). When they diverge, both are shown.
- Paper **925 LOC** for GPREEMPT-style preemption: **`gpu_preempt_ctrl.bpf.c` (280) + `gpu_preempt_ctrl.c` (647) = 927 ≈ 925**.  
  Separate paper number **Dynamic Timeslice 408** ≈ `gpu_sched_set_timeslices.bpf.c` (188) + `.c` (222) = **410**.  
  Fig.12 uses **both** timeslice differentiation and preemption; do not collapse them into one 925-LOC program.

---

## 2. Meta-Review Mapping → Safe Deliverables

Sources: `review.txt`, `fable.md`, `rebuttal-v3.md`. Major sticking points: **Q1 SOTA** and **Q2 safety**; Rev **F** also wants **mechanism vs policy**.

| Review pressure | What they want | **Safe** revision deliverable | **Unsafe** over-promise |
|-----------------|----------------|-------------------------------|-------------------------|
| **E, F — Q1 SOTA** | Compare vs research systems | (1) Foreground **GPREEMPT-equivalent** priority timeslice + preempt policy already in tree + Fig.12 numbers; (2) Keep **LMCache** as framework baseline (Fig.9 / `fig:vllm-kv-offload`); (3) **Policy expressibility table** (§5); (4) MoE: document Expert Buffering ≈ page-level hot-expert residency via existing MoE policies | Full Huang et al. reproduction; “original + their + improved” for every paper; re-run GPREEMPT driver artifact; LithOS TPC/atomization experiments |
| **B, F — Q2 safety** | Depth on async safety | Expand §§3.4–4: transition validation, SIMT verifier, rejection examples, failure-mode taxonomy; reuse agent safety-event counts (50 events) from eval | Claim formal verification of full GPU stack / zero optimality loss under staleness |
| **F — mechanism vs policy** | Attribution | Clarify **Fig.13** (`fig:all-kernels-priority`): GPREEMPT-style **sched** &lt;1% on memory-bound vs memory policies 55–92% | Claim all gains come only from “mechanism” independent of policy |
| **A — Table 1 / P40** | RTX 5090 observability data | Add RTX 5090 numbers to Table 1 where microbench already exists (`fig:microbench` path) | Full re-benchmark of every observability tool on every GPU |
| **E — Q14 agents** | Reproducibility of agent study | Release **agent prompts + harnesses** (`docs/eval/agent/`, workload scripts) | Release private API keys / unprepared full conversation dumps |
| **D — portability / CXL / storage** | Discussion depth | Short design discussion only (state-machine extension) | Multi-vendor port experiments; working CXL/storage tier prototype |
| **E — MIG / multi-tenant relevance** | Real-world use | Cite software co-location literature (MuxFlow, Orion, Tally); clarify no MIG required | New hyperscaler production deployment study |

### Author-response HARD deliverables (Safe tier)

Implementable without new external systems:

1. Expand **§§3.4–4**: transition-validation pseudocode, SIMT-verifier algorithm, concrete verifier-rejection examples, failure-mode taxonomy (map to the 50 agent safety events: 24 logic, 18 performance, 2 verifier rejections, 2 GPU-side overflows, 4 other).
2. **Policy expressibility table** (draft §5; polish for paper).
3. **Table 1**: add RTX 5090 data (observability / device-side microbench path already in eval).
4. **Release** agent prompts + benchmark harnesses (artifact).
5. **Fig.13** mechanism-vs-policy interpretation paragraph.
6. Foreground existing SOTA evidence: GPREEMPT-equivalent (**925 ≈ preempt_ctrl BPF+loader**; timeslice separate) + LMCache as **framework baseline** (not eBPF reimplementation).

---

## 3. In-Tree Policy Inventory

**Root:** `extension/`  
**Build list:** `extension/Makefile` `BPF_APPS` / `SCX_APPS`  
**Overview (stale):** `docs/experiment/POLICY_OVERVIEW.md`

Policy programs on disk (`.bpf.c` under `extension/`, excluding pure tests unless noted).  
**LOC = physical lines in the file** (verified by reading file ends; ±1 possible for trailing newline).

### 3.1 Eviction policies (`eviction_*.bpf.c`)

| File | LOC | Role | Paper / eval use |
|------|-----|------|------------------|
| `extension/eviction_fifo.bpf.c` | 64 | FIFO baseline | Micro / agent exploration baseline |
| `extension/eviction_mru.bpf.c` | 74 | MRU (scan-friendly) | POLICY_OVERVIEW; FAISS-style scans |
| `extension/eviction_cycle_moe.bpf.c` | 124 | Protect T1 (attention/embed) under MoE | MoE expert offload story; pairs with MoE prefetch |
| `extension/eviction_freq_pid_decay.bpf.c` | 221 | Frequency + PID + decay | Multi-tenant runs under `docs/eval/multi-tenant-memory/` |
| `extension/eviction_lfu.bpf.c` | 224 | LFU | Paper Expert / KV cases (**304** ≈ 224 BPF + 82 loader) |
| `extension/eviction_pid_quota.bpf.c` | 238 | Per-PID memory quota | Multi-tenant “Quota LRU” (**472** ≈ 238 + 235 loader) |
| `extension/eviction_fifo_chance.bpf.c` | 240 | FIFO + second chance | Fairness / mixed tenants |
| `extension/eviction_lfu_xcoord.bpf.c` | 313 | LFU + xCoord shared maps | Cross-layer sched/memory coordination |

**Eviction subtotal:** 8 files, **~1498** LOC (`.bpf.c` only).

### 3.2 Prefetch policies (`prefetch_*.bpf.c`)

| File | LOC | Role | Paper / eval use |
|------|-----|------|------------------|
| `extension/prefetch_none.bpf.c` | 56 | Disable prefetch | Control |
| `extension/prefetch_always_max.bpf.c` | 63 | Max aggressive prefetch | Simple baseline; vLLM result configs |
| `extension/prefetch_adaptive_tree_iter.bpf.c` | 98 | Tree-aware iterative | Multi-tenant tree prefetch family |
| `extension/prefetch_max_passive_mru.bpf.c` | 132 | Passive + MRU | Exploration |
| `extension/prefetch_always_max_cycle_moe.bpf.c` | 136 | Always-max + cycle MoE | vLLM configs in `workloads/vllm/results/` |
| `extension/prefetch_max_mru_expert.bpf.c` | 142 | Expert + MRU | MoE exploration |
| `extension/prefetch_serving_adaptive.bpf.c` | 151 | Serving-adaptive | vLLM serving experiments (`exp_vllm_rerun`) |
| `extension/prefetch_pid_tree.bpf.c` | 207 | PID-aware tree | Multi-tenant “Tree-based Prefetch” (**454** ≈ 207 + 248 loader); `Prefetch(lo,hi)` evidence in multi-tenant CSVs |
| `extension/prefetch_always_max_xcoord.bpf.c` | 211 | Always-max + xCoord maps | Cross-layer |
| `extension/prefetch_trace.bpf.c` | 228 | Trace / observability-style | Pattern learning |
| `extension/prefetch_adaptive_sequential.bpf.c` | 234 | Adaptive sequential | Paper sequential **375** LOC — **does not match** current 234+340; see §9 |
| `extension/prefetch_template_belady.bpf.c` | 283 | Belady-style template | Research/exploration |
| `extension/prefetch_stride.bpf.c` | 293 | Stride prediction | Paper stride **472** ≈ 293 + 180 loader; MoE weights |
| `extension/prefetch_reuse_dist.bpf.c` | 358 | Reuse-distance guided | Exploration |
| `extension/prefetch_throttled_xb.bpf.c` | 366 | Throttled cross-block | PCIe-aware; vLLM `exp_xb2` / `exp_vllm_rerun` |
| `extension/prefetch_faiss_uprobe.bpf.c` | 393 | FAISS + uprobe | FAISS case study family |
| `extension/prefetch_cooperative.bpf.c` | 395 | Cooperative host/device | Host–device coordination |
| `extension/prefetch_proactive_layer.bpf.c` | 403 | Layer-proactive | LLM layer structure |
| `extension/prefetch_always_max_qos.bpf.c` | 408 | QoS + cycle-MoE + LC protection | Multi-tenant priority/QoS |
| `extension/prefetch_eviction_pid.bpf.c` | 410 | Combined PID prefetch + probabilistic eviction | **Memory priority** Prefetch(lo,hi)/Evict(lo,hi); heavy use in `docs/eval/multi-tenant-memory/` |
| `extension/prefetch_vllm_phase.bpf.c` | 412 | vLLM phase-aware | KV-cache / vLLM case (`exp_n6_vllm`) |
| `extension/prefetch_faiss_phase.bpf.c` | 419 | FAISS BUILD/SEARCH phase | FAISS case (~890 LOC combined claim) |
| `extension/prefetch_stride_multiblock.bpf.c` | 424 | Multi-block stride | Oversubscription / stride |
| `extension/prefetch_vllm_phase_transparent.bpf.c` | 424 | Transparent vLLM phase | No-app-mod vLLM (`exp_vllm_transparent`) |
| `extension/prefetch_cross_block_v2.bpf.c` | 463 | Cross-block prefetch v2 | Advanced prefetch |
| `extension/prefetch_llama_phase.bpf.c` | 465 | llama.cpp phase | Expert offload family |
| `extension/prefetch_gnn_proactive.bpf.c` | 621 | GNN proactive + uprobe | GNN training case |
| `extension/prefetch_moe_expert.bpf.c` | 769 | MoE expert proactive (bitmap fault replay) | **Huang Expert Buffering analogue at page level** (expressibility, not H2H) |

**Prefetch subtotal:** 28 files, **~8964** LOC (`.bpf.c` only).

Also under `extension/backup/`: `prefetch_direction.bpf.c` (not primary inventory).

### 3.3 Scheduling / preemption (`gpu_sched_*`, `gpu_preempt_*`, `sched_gpu_*`)

| File | LOC | Role | Paper / eval use |
|------|-----|------|------------------|
| `extension/gpu_sched_set_timeslices.bpf.c` | 188 | struct_ops timeslice by process name | Dynamic timeslice building block (**~408** with userspace) |
| `extension/gpu_sched_set_timeslices.c` | 222 | Userspace loader / map config | Paired with above |
| `extension/gpu_preempt_ctrl.bpf.c` | 280 | Tracepoint-based TSG preempt control; header: *“similar to GPreempt patch but uses tracepoints instead of modifying the kernel driver”* | **GPREEMPT-equivalent path (BPF half)** |
| `extension/gpu_preempt_ctrl.c` | 647 | Userspace: handles + `NVA06C_CTRL_CMD_PREEMPT` ioctl | Combined with BPF ≈ **927 ≈ paper 925** |
| `extension/gpu_sched_trace.bpf.c` | 291 | Sched observability | Host-side tracing |
| `extension/sched_gpu_minimal.bpf.c` | 134 | sched_ext minimal GPU-aware | SCX path (needs `SCX_INCLUDE_DIR`) |
| `extension/sched_gpu_serving.bpf.c` | 175 | Serving-oriented SCX | Multi-tenant serving |
| `extension/sched_gpu_xcoord_noad.bpf.c` | 188 | xCoord SCX w/o admission | Ablation |
| `extension/sched_gpu_xcoord.bpf.c` | 227 | xCoord SCX | Cross-layer |
| `extension/sched_gpu_baseline.bpf.c` | 228 | SCX baseline | Baseline |
| `extension/sched_gpu_coord.bpf.c` | 496 | Coordinated SCX | Advanced multi-tenant |

**Paper claim cross-check (GPREEMPT-style 925 LOC):**

```
gpu_preempt_ctrl.bpf.c  280
gpu_preempt_ctrl.c      647
---------------------------
Total                   927  ≈ eval.tex “925 LOC” (Preemption Control)
```

Separate:

```
gpu_sched_set_timeslices.bpf.c  188
gpu_sched_set_timeslices.c      222
---------------------------------
Total                           410  ≈ eval.tex “Dynamic Timeslice 408”
```

Fig.12 (`fig:scheduler-latency`) text: LC timeslice 1s / BE 200µs **plus** preemption policy equivalent to GPREEMPT.  
Eval harness: `docs/eval/multi-tenant-scheduler/` (modes include `timeslice_only`, `kfunc_only`, `timeslice_kfunc`).

**Do not** re-state this as “we re-ran the thustorage/GPreempt artifact.”  
State: **priority-based timeslice / preempt policy expressed as gpubpf programs without modifying driver source for the policy logic.**

**What GPREEMPT actually is (ATC'25, correct PDF: `docs/paper-material/ref-paper/gpreempt_atc25.pdf`):**  
Driver-level timeslice-based **yield** for context-switch preemption, plus **hint-based pre-preemption** overlapping data-preparation; public code at https://github.com/thustorage/GPreempt. Our stack is **policy-intent equivalent** (LC vs BE timeslice + force preempt via ioctl/tracepoints), **not** a port of their yield/pre-preemption driver patch or their 7-workload NVIDIA+AMD eval.

### 3.4 Observability / scaffolding (not “policies” but cited in paper)

| File | LOC | Notes |
|------|-----|--------|
| `extension/chunk_trace.bpf.c` | ≥144 | Chunk access tracing (ends after eviction_prepare kprobe) |
| `extension/struct_ops.bpf.c` | 51 | Template / skeleton |
| `extension/test_preempt_*.bpf.c`, `test_uprobe_*.bpf.c`, `uprobe_preempt_multi.bpf.c` | various | Demos / harnesses, not paper policies |

Device-side tools in eval Table 1 (`kernelretsnoop`, `threadhist`, `launchlate`) live primarily under the **bpftime / GPU tooling** tree, **not** as `extension/*.bpf.c` host policies — confirm artifact packaging before promising “all tools in `extension/`.”

Device-side **45 LOC** L2 prefetch / **16–19 LOC** CLC schedulers in `eval.tex` are **device eBPF**, not host `extension/prefetch_*.bpf.c`.

### 3.5 Inventory summary

| Class | # primary `.bpf.c` | Approx LOC |
|-------|--------------------|------------|
| Eviction | 8 | ~1.5k |
| Prefetch | 28 | ~9.0k |
| GPU sched struct_ops + preempt BPF | 3 (`set_timeslices`, `preempt_ctrl`, `sched_trace`) | ~0.76k BPF |
| sched_ext GPU apps | 6 | ~1.45k |
| **Policy-ish total (evict+prefetch+core sched BPF)** | **~45** | **~11k+** |

`POLICY_OVERVIEW.md` lists only a subset; **use this inventory + `Makefile` `BPF_APPS` as ground truth.**

### 3.6 Paper case study → best-effort `.bpf.c` mapping

Labels below are **best-effort**: paper describes agent-converged LOC bundles; filenames are the closest maintained programs. Exact binary that produced each figure is not always encoded in git history.

| Paper case / figure (eval.tex label) | Paper policy story | Best-effort files (code exists) | Used in paper numbers? |
|--------------------------------------|--------------------|----------------------------------|-------------------------|
| RQ1 vector-add stride (`fig:clc-policies`) | Host stride + device 45 LOC | `prefetch_stride.bpf.c` (+ device eBPF **not** in `extension/` host list) | **Yes** (paper) |
| RQ1 sequential mismatch | Sequential 375 LOC degrades 8% | `prefetch_adaptive_sequential.bpf.c` | **Yes** (paper) |
| Expert offload llama.cpp (`fig:llama-expert-offload`) | Stride + LFU + device 45 (~820 LOC) | `prefetch_stride.*`, `eviction_lfu.*`; related: `prefetch_llama_phase`, `eviction_cycle_moe`, `prefetch_moe_expert` | **Yes** (final numbers); MoE-named variants = exploration / expressibility |
| KV-cache vLLM (`fig:vllm-kv-offload`) | Adaptive seq + LFU (~680); match LMCache | `prefetch_adaptive_sequential.*`, `eviction_lfu.*`; harness results also exercise `prefetch_always_max_cycle_moe`, `prefetch_vllm_phase*`, `prefetch_serving_adaptive` | **Yes** baseline + UVM policies; LMCache is **framework**, not eBPF |
| GNN (`fig:gnn-epoch`) | Sequential + uprobe PyTorch | `prefetch_adaptive_sequential.*`, `prefetch_gnn_proactive.bpf.c` | **Yes** |
| FAISS (`fig:faiss-perf`) | Seq + stride + device (~890) | `prefetch_faiss_phase.*`, `prefetch_stride.*`, `prefetch_faiss_uprobe.*` | **Yes** |
| Multi-tenant compute (`fig:scheduler-latency` ≈ Fig.12) | GPREEMPT-style timeslice + preempt 925 | `gpu_sched_set_timeslices.*` + `gpu_preempt_ctrl.*` | **Yes** |
| Multi-tenant memory (`fig:all-kernels-priority` ≈ Fig.13) | Prefetch(lo,hi) 454 / Evict(lo,hi) 472 | `prefetch_pid_tree.*`, `prefetch_eviction_pid.*`, `eviction_pid_quota.*`; CSVs in `docs/eval/multi-tenant-memory/` | **Yes** |
| Two-tenant LC+BE (`fig:two-tenant` ≈ Fig.14) | ~926 LOC: Quota LRU + Tree Prefetch + Dynamic Timeslice | Same three families as above | **Yes** (composition LOC uncertain — see §9) |

**Status legend:** (a) **code exists**, (b) **used in paper numbers**, (c) **experimental/unused in paper figures**. Many prefetch variants are (a)+(c): present and often agent-explored, not all cited in final eval.tex paragraphs.

### 3.7 Harness / baseline paths (not eBPF policies)

| Path | Role | Exists? |
|------|------|---------|
| `workloads/vllm/docs/RTX5090_setup_lmcache.md` | LMCache setup on RTX 5090 (build from source for sm_120) | Yes |
| `workloads/vllm/vllm/examples/others/lmcache/` | Upstream-style LMCache examples (cpu offload, disagg, sharing) | Yes |
| `workloads/vllm/configs/serve_bench.py` | Serving bench configs | Yes |
| `workloads/vllm/results/` | Recorded UVM / offload / phase policy JSON logs + lmcache client/server logs | Yes |
| `workloads/vllm/results/logs/*lmcache*` | Evidence LMCache was run in harness | Yes |
| `docs/eval/multi-tenant-memory/` | Multi-tenant memory policy CSVs + plot scripts | Yes |
| `docs/eval/multi-tenant-scheduler/` | Scheduler / preempt microbench CSVs | Yes |
| `docs/eval/agent/` | Agent study notes for artifact | Yes |

---

## 4. External Systems Matrix

**Legend**

- **Public code?** Can we clone a usable artifact?
- **Expressible on gpubpf?** Can the *policy idea* map to hooks we have?
- **H2H feasible?** Controlled head-to-head on **same models, numbers, hardware** as their paper?
- **Commitment language:** preferred HotCRP wording.

| System | Public code? | Expressible on gpubpf? | H2H feasible? | Recommended commitment language |
|--------|--------------|------------------------|---------------|----------------------------------|
| **GPREEMPT** (ATC'25) | **Yes** — https://github.com/thustorage/GPreempt ; PDF: `docs/paper-material/ref-paper/gpreempt_atc25.pdf` | **Yes (policy intent)** — timeslice + preempt already in tree (`gpu_sched_set_timeslices.*`, `gpu_preempt_ctrl.*`). **Not** their yield + pre-preemption driver design | **Partial only** — our **equivalent policy** experiment (Fig.12, ~925 LOC preempt_ctrl) is done; full re-run of their **driver-patch artifact** is **not** required | “We implement GPREEMPT’s priority-timeslice / preemption **policy intent** as gpubpf programs (~925 LOC for the preemption controller BPF+loader; separate ~408 LOC timeslice program) **without driver source modification for the policy logic**, and evaluate the intended LC latency benefit on our multi-tenant microbenchmark (Fig.12).” |
| **GCAPS** (ECRTS'24) | **Claimed** public designs exist; PDF correct in both ref trees (`gcaps.pdf`). Exact GitHub readiness **uncertain** without live clone | **Partially** — priority preemption / isolation *ideas* map to timeslice + preempt + PID memory policies | **No** — do not promise RT taskset reproduction or their full real-time GPU stack | “GCAPS requires driver-level changes for real-time guarantees; **priority preemption is expressible** via gpubpf scheduling hooks. We do **not** claim a real-time taskset reproduction.” |
| **LMCache** | **Yes** (open source); already in eval harness | **N/A as “port to eBPF”** — framework KV-cache manager | **Already compared** as baseline (throughput / TTFT-style metrics) | “We compare against LMCache as a **SOTA framework-managed KV-cache baseline** (Fig.9 / `fig:vllm-kv-offload`). gpubpf is complementary (transparent UVM policies), **not** a reimplementation of LMCache.” |
| **Huang et al.** arXiv:2303.06182 (Expert Buffering et al.) | **No usable full artifact** for controlled repro of their LM/MT MoE stack | **Page-level analogue yes** — hot-expert residency / cycle protect + expert prefetch (`eviction_cycle_moe`, `prefetch_moe_expert`, related MoE prefetch). Dynamic gating & expert load-balance are **not** implemented as finished gpubpf policies | **No** — framework expert-atomic + gating vs page-level UVM; cannot honestly match **6.21–11.23×** (dynamic gating) or Expert Buffering memory claims | “Expert Buffering’s **hot-expert residency** idea is expressible as gpubpf eviction/prefetch at **page granularity**. We **do not** claim head-to-head reproduction of their models or speedups.” |
| **LithOS** (SOSP'25) | PDF: `docs/paper-material/ref-paper/lithos_sosp25.pdf` (GPU OS: TPC scheduler, kernel atomization, rightsizing, power) | **Only fragments** (coarse scheduling ideas) | **No** | “Related work / discussion: mechanism-level GPU OS; out of scope for policy-runtime comparison.” |
| **TimeGraph / Gdev** | Old research stacks | Priority/isolation *ideas* only | **No** (obsolete stacks) | “Related work only; historical driver-level GPU scheduling.” |
| **Neutrino** (OSDI'25) | **Yes** — https://github.com/open-neutrino/neutrino ; PDF: `docs/paper-material/ref-paper/neutrino_osdi25.pdf` | Overlaps **read-only** observability axis (not control policies) | Overhead comparison already framed vs NVBit | “Neutrino is **observability**; we do not claim policy control equivalence. Device-side overhead comparison remains vs NVBit-class tools.” |
| **XSched** (OSDI'25) | **Yes** — https://github.com/XpuOS/xsched (+ artifacts repo); PDF: `docs/paper-material/ref-paper/xsched_osdi25.pdf` | Preemptive XPU scheduling *ideas* partially map to timeslice/preempt; their multi-XPU XQueue stack is a different runtime | **No** mandatory H2H for this paper | “Related multi-tenant / preemptive scheduling motivation; expressibility of priority timeslice only if needed.” |
| **Tally** (ASPLOS'25) | PDF in `asplos-27-rebuttal/ref/tally-asplos25.pdf` (**content verified** Tally). Public artifact URL **uncertain** | Multi-tenant isolation / co-location **motivation**, not a UVM memory policy | Not required as H2H | Motivation citation for inference+training co-location (with MuxFlow, Orion). |
| **Orion / MuxFlow** | Various | Motivation for software co-location | Not required | Motivation citations only. |
| **CXL / storage tier** (Weka/VAST/CMX, etc.) | No integrated gpubpf stack | Design-level only (new states/transitions) | **No** | “Discussion: async state machine could add tiers; **no experimental claim** in revision.” |

### 4.1 What “expressible” means

A policy is **expressible on gpubpf** if it can be written as:

1. **Host driver eBPF** on UVM / GPU sched struct_ops / tracepoints / kfuncs we already expose, and/or  
2. **Device-side eBPF** for observation / limited control under SIMT verifier, and/or  
3. **Uprobe / app-phase** hooks without modifying application source (transparent),

**without** requiring permanent patches to the NVIDIA driver source tree for the *policy logic itself*.

Expressibility **does not** mean: same absolute performance, same hardware generation, or same end-to-end application stack as the original paper.

### 4.2 Misnamed / wrong PDFs under `asplos-27-rebuttal/ref/`

**Verified wrong filenames (do not cite as that system):**

| File under `asplos-27-rebuttal/ref/` | Actual content (page 1) |
|--------------------------------------|-------------------------|
| `gpreempt-atc25.pdf` | **FlashInfer** (attention engine) — **not** GPREEMPT |
| `neutrino-osdi25.pdf` | Algebraic geometry paper (primitive multiple schemes) — **not** Neutrino |
| `xsched-osdi25.pdf` | PDE uncertainty quantification math paper — **not** XSched |

**Verified correct in same folder (spot-check):** `gcaps.pdf`, `tally-asplos25.pdf`, `moe-offloading-2303.06182.pdf`.

**Always prefer:** `docs/paper-material/ref-paper/` for GPREEMPT, LithOS, Neutrino, XSched, LMCache, GCAPS.

### 4.3 Huang et al. (2303.06182) — techniques vs our MoE policies

From PDF abstract/body (Meta AI MoE inference paper):

| Their technique | What it does | Our mapping | Status |
|-----------------|--------------|-------------|--------|
| **Dynamic gating** | Change gating policy to cut waste factor; **6.21–11.23×** LM throughput claims | Would need framework gating change or uprobe on gating fn | **Not implemented** as finished policy; **Stretch only** |
| **Expert Buffering** | Keep hot/active experts in GPU, buffer rest in CPU; reduce static GPU mem up to **1.47×** | Page-level: `eviction_cycle_moe` protects T1 (attention/embed); `prefetch_moe_expert` replays prior-token fault bitmap as expert prefetch | **Code exists** (expressibility); **no H2H numbers** |
| **Expert load balancing** | A priori balance from historical activation | Not our UVM policy layer | **Out of scope** |

Honest statement: we map **Expert Buffering’s residency idea**, not their full system (expert-atomic migrate + gating integration + their LM/MT models on V100 cluster).

---

## 5. Policy Expressibility Table Draft

Columns: **Policy / User-space / Driver-mod / gpubpf / Evidence**.

| Policy (as evaluated or discussed) | User-space only? | Driver source mod? | gpubpf? | Evidence (paths / paper) |
|------------------------------------|------------------|--------------------|---------|---------------------------|
| Default UVM LRU/FIFO | Partial (`cudaMemAdvise` / prefetch async) | No (stock driver) | N/A baseline | eval baselines |
| App hints (`cudaMemAdvise`, `cudaMemPrefetchAsync`) | **Yes** | No | Optional complement | `fig:gnn-epoch`, `fig:llama-expert-offload`: hints need app changes; eBPF can add transparent gain |
| Framework offload (llama.cpp `ncmoe`, vLLM `--cpu-offload-gb`) | **Yes** (framework) | No | Complement via UVM policies | `fig:llama-expert-offload`, `fig:vllm-kv-offload` |
| LMCache KV management | **Yes** (framework) | No | **Compare only**, do not reimplement | `fig:vllm-kv-offload`; `workloads/vllm/.../lmcache/`; lmcache logs under `workloads/vllm/results/logs/` |
| Sequential / stride / adaptive prefetch | Partial (CUDA APIs) | Unsafe if patched into UVM | **Yes** — `prefetch_adaptive_sequential`, `prefetch_stride`, … | RQ1 / agent cases; LOC in §3 |
| LFU / PID-quota / cycle-MoE eviction | No clean user API | Unsafe ad-hoc patches | **Yes** — `eviction_lfu`, `eviction_pid_quota`, `eviction_cycle_moe` | RQ1–RQ3 |
| Multi-tenant memory priority Prefetch(lo,hi) / Evict(lo,hi) | No | Unsafe | **Yes** — `prefetch_eviction_pid`, `prefetch_pid_tree`, QoS variants | `fig:all-kernels-priority`; `docs/eval/multi-tenant-memory/` |
| GPREEMPT-style priority timeslice + preempt | Limited (CUDA MPS/MIG-like, not same) | **Original GPREEMPT: yes** | **Yes without driver-source policy patches** — `gpu_sched_set_timeslices` + `gpu_preempt_ctrl` | `fig:scheduler-latency`; ~925 LOC preempt_ctrl; comment in `gpu_preempt_ctrl.bpf.c` |
| GCAPS-style RT priority preempt | No | **Yes** (their design) | **Expressible subset** (priority preempt), not full RT | Expressibility only |
| Huang Expert Buffering (gating + expert-atomic migrate) | **Yes** (framework) | No | **Page-level analogue** — MoE prefetch/evict; **not** expert-atomic runtime | `prefetch_moe_expert`, `eviction_cycle_moe`; **no H2H numbers** |
| LithOS TPC / atomization GPU OS | N/A | Whole stack | **Not** as policy | Discussion only |
| XSched XQueue preemption | Their userspace/runtime stack | Platform-dependent | **Partial** priority scheduling ideas only | Discussion / motivation |
| Device-side L2 / observability policies | Limited (NVBit etc.) | No | **Yes** (SIMT eBPF) | Table 1, `fig:microbench`; vs NVBit |
| Agent-generated policies (59 explored) | N/A | Would be catastrophic if in-driver | **Yes** + detach | RQ2; release prompts (`docs/eval/agent/`) |

**Fill rule for the paper table:** mark cells as `{feasible / partial / unsafe / infeasible}` rather than checkmarks alone, and point each **gpubpf** row at a concrete `extension/*.bpf.c` when possible.

---

## 6. Safe HotCRP Revision-Plan Text (Copy-Paste Ready)

Use or trim the following block. It contains **no** unfinished draft language.

---

### Revision plan (SOTA, safety, attribution, artifacts)

**R1. SOTA research baselines (Reviewers E, F).**  
We will revise the evaluation narrative to foreground two existing comparisons: (1) a **GPREEMPT-equivalent** priority timeslice and preemption **policy** implemented as gpubpf programs under `extension/` (`gpu_sched_set_timeslices.*` for differentiated timeslices, and `gpu_preempt_ctrl.*` for preemption control totaling approximately **925 lines** BPF+userspace controller) **without modifying driver source for the policy logic**, reducing latency-critical P99 launch latency by 96% on our multi-tenant microbenchmark (Fig.12); (2) a comparison against **LMCache** as a state-of-the-art **framework** KV-cache baseline, where gpubpf UVM policies match throughput with improved tail latency (Fig.9). We will **not** re-run the upstream GPREEMPT driver-patch artifact as a mandatory experiment; the scientific claim is **policy expressibility and safe dynamic deployment**, not binary reproduction of their kernel tree.

**R2. Policy expressibility table (Reviewers E, F, Q1/Q15).**  
We will add a table mapping each evaluated policy class to feasibility under (a) user-space / framework APIs, (b) ad-hoc driver source modification, and (c) gpubpf, with pointers to in-tree programs under `extension/` (eviction, prefetch, and scheduling families). For driver-level systems such as TimeGraph, Gdev, GCAPS, LithOS, and XSched, the revision will treat the comparable axis as **whether core policy ideas are expressible**, not full system reimplementation.

**R3. MoE Expert Buffering (Reviewer E, arXiv:2303.06182).**  
Expert Buffering targets framework-level, expert-atomic migration guided by gating outputs and does not provide a usable full public artifact for controlled head-to-head reproduction on our stack. We will clarify that **hot-expert residency** is expressible at **page granularity** using existing MoE-oriented policies (e.g., `extension/eviction_cycle_moe.bpf.c`, `extension/prefetch_moe_expert.bpf.c` and related MoE prefetch variants), and we will **not** claim numerical reproduction of Huang et al.’s reported speedups (including dynamic-gating throughput claims).

**R4. Mechanism vs. policy (Reviewer F).**  
We will expand the discussion of Fig.13: on memory-bound multi-tenant workloads, the GPREEMPT-style **scheduling** policy yields &lt;1% improvement, while gpubpf **memory** priority policies improve completion time by 55–92%. This separates mechanism-supported policy layers from any single hardcoded heuristic.

**R5. Safety depth (Reviewers B, F).**  
We will expand Sections 3.4 and 4 with (i) transition-validation pseudocode, (ii) the SIMT-aware verifier algorithm, (iii) concrete verifier rejection examples, and (iv) a failure-mode taxonomy aligned with the agent study’s safety events (24 logic bugs, 18 performance regressions, 2 verifier rejections, 2 GPU-side overflows, 4 others), emphasizing that failed policies detach without OS panic.

**R6. Table 1 / RTX 5090 (Reviewer A).**  
We will add RTX 5090 measurements for device-side observability overheads in Table 1, consistent with microbenchmarks already reported on Server A.

**R7. Artifacts (Reviewer E).**  
We will release agent prompts and benchmark harnesses used in the policy-exploration study as a public artifact (including materials under `docs/eval/agent/` and the multi-tenant / workload harness scripts used for paper figures).

**R8. Scope explicitly out of revision experiments.**  
We will **not** promise: full multi-vendor ports; LithOS-scale GPU OS experiments; CXL/storage-tier prototypes; re-running every related system’s original artifact; or “original system + their policy + our improved policy” for every related paper.

---

## 7. Explicit DO NOT PROMISE List (Forbidden tier)

**Forbidden in HotCRP revision plan / camera-ready commitments:**

1. **Full Huang et al. (arXiv:2303.06182) reproduction** — matching their models, gating integration, or **6–11×** dynamic-gating claims.  
2. **LithOS** (or other whole-GPU OS) experimental port / TPC scheduling / kernel atomization study.  
3. **“Original system + their policy + our improved policy” for every related paper** (the old `revision-plan.md` wording). Limit that pattern to systems where we already have policies (GPREEMPT-class scheduling; page-level MoE residency).  
4. **Mandatory re-run of the full GPREEMPT driver artifact** (thustorage/GPreempt) as acceptance criteria. Expressibility + our Fig.12 experiment is enough.  
5. **GCAPS real-time taskset** or hard RT certification claims.  
6. **“We implemented LMCache as eBPF.”** LMCache remains a **baseline**, not a port.  
7. **Working CXL / NVMe / GDS tier** experiments in this revision. Discussion only.  
8. **Multi-vendor (AMD/Intel) performance campaigns** beyond SPIR-V/portability discussion already drafted.  
9. **Unqualified “no performance loss vs original GPREEMPT.”** We never ran their exact implementation head-to-head; only an equivalent policy.  
10. **Gating-aware Huang policy + “comparing directly”** if that language implies their speedups or their exact runtime integration (`fable.md` over-promise). Prefer: *page-level hot-expert residency already supported; optional stretch only* (§8).  
11. **Trust PDFs under `docs/paper/asplos-27-rebuttal/ref/` blindly** — several are wrong downloads; use `docs/paper-material/ref-paper/`.  
12. **Collapsing timeslice (408) and preemption (925) into one program** when citing LOC — they are separate artifacts; Fig.12 uses both.

**Dangerous leftover wording in old drafts (fix before reuse):**

| Draft | Risk |
|-------|------|
| `revision-plan.md`: “Original system, their policy in our system, our new improved policy” + “compability things?” | Open-ended; unfinished |
| `fable.md`: “commit to implementing this gating-aware policy and comparing directly” | Easy to read as full Huang H2H |
| Any “without performance loss” vs GPREEMPT binary | Implies H2H not performed |
| HotCRP text that attributes **all** 925 LOC to “timeslice + preempt combined” without naming `gpu_preempt_ctrl` | Slightly imprecise vs paper’s separate 408 / 925 table entries |

---

## 8. Optional Stretch Items (Only If Time)

Do **not** put these in the HotCRP plan as hard commitments. Promote only after code + numbers exist.

| Stretch | Why optional | Suggested bar to promote |
|---------|--------------|---------------------------|
| Gating-function **uprobe** that biases MoE prefetch (Huang-inspired) | Nice narrative for E; still not their stack | Working policy + one figure on **our** MoE model only; no claim of matching their × speedups |
| Side-by-side **qualitative** comparison table: framework Expert Buffering vs page-level cycle_moe/moe_expert | Low risk if no numeric claim of matching their paper | Text + LOC only |
| Package GPREEMPT-equivalent as a single named artifact directory with README | Improves reproducibility optics | Document 925 (preempt_ctrl) + 408 (timeslices) composition + run script from `docs/eval/multi-tenant-scheduler/` |
| Sync-interval sensitivity (Reviewer D) | Mentioned in drafts | One micro study |
| Grid-scaling trampoline data (Reviewer D) | Mentioned in drafts | One plot |
| Refresh `docs/experiment/POLICY_OVERVIEW.md` to match §3 inventory | Docs hygiene | Not paper-critical |

---

## 9. Uncertainties Found During Inventory

1. **Paper LOC vs disk LOC:** Solid matches when counting **BPF + userspace loader**:
   - LFU: 224 + 82 = **306 ≈ 304**
   - Stride: 293 + 180 = **473 ≈ 472**
   - Quota LRU: 238 + 235 = **473 ≈ 472**
   - Tree prefetch: 207 + 248 = **455 ≈ 454**
   - Dynamic timeslice: 188 + 222 = **410 ≈ 408**
   - Preemption control: 280 + 647 = **927 ≈ 925**
   - **Sequential 375:** current `prefetch_adaptive_sequential` is **234 + 340 = 574 ≠ 375**. Likely older version, different counting, or a different sequential implementation. Mark **uncertain**.
2. **Two-tenant ~926 LOC** (“Quota LRU + Tree Prefetch + Dynamic Timeslice”): naive sum 472+454+408 = **1334 ≠ 926**. Composition rule unclear (subset, shared loader, or older snapshot). Mark **uncertain**; do not invent a file sum that equals 926.
3. **`POLICY_OVERVIEW.md` is stale** (10 eviction / 9 prefetch). Do not use it as the sole inventory.
4. **Which exact policy binary produced each fig** is not fully encoded in filenames alone; `workloads/*/results/` JSON logs, `docs/eval/**` CSVs, and agent harnesses should be linked in the artifact release (R7).
5. **Device-side 45 LOC** policies in eval are **not** standalone `extension/prefetch_*.bpf.c` host files; they live in device-eBPF / bpftime paths. Confirm before claiming “all LOC under `extension/`.”
6. **sched_ext apps** (`sched_gpu_*`) need `SCX_INCLUDE_DIR` and may be disabled in default builds (`Makefile` `HAVE_SCX`). Do not promise SCX-based results without verifying the build flag on the eval machine. Multi-tenant **paper** numbers appear driven by NVIDIA timeslice/preempt paths, not SCX.
7. **Huang “gating-aware” stretch** is **not** checked in as a finished policy named for gating outputs; closest productionized MoE story is cycle/expert prefetch+evict.
8. **Rebuttal `ref/` PDFs** may be wrong; prefer `docs/paper-material/ref-paper/`. Known bad: `gpreempt-atc25.pdf`, `neutrino-osdi25.pdf`, `xsched-osdi25.pdf`.
9. **GCAPS / Tally public artifact URLs:** not re-cloned in this audit; treat code-availability claims as secondary to “expressibility only / motivation only.”
10. **Fig.12 / Fig.13 numbers** refer to **submitted PDF figure order**. LaTeX labels are `fig:scheduler-latency` and `fig:all-kernels-priority`. Keep PDF numbers when writing HotCRP text that already cites Fig.12/13.

---

## 10. Quick Reference: Safe vs Unsafe One-Liners

| Topic | Safe one-liner | Unsafe one-liner |
|-------|----------------|------------------|
| GPREEMPT | “Equivalent policy intent in ~925 LOC preempt controller (+ ~408 LOC timeslice), no driver-source policy mod; Fig.12.” | “We reproduced GPREEMPT’s artifact and matched all their results.” |
| LMCache | “Framework baseline; gpubpf matches throughput, better tails.” | “LMCache reimplemented as eBPF.” |
| Huang MoE | “Hot-expert residency expressible at page level via MoE policies.” | “We reproduce Expert Buffering and its 6–11× gains.” |
| GCAPS | “Priority preempt expressible; no RT taskset claim.” | “Full GCAPS comparison.” |
| LithOS / CXL | “Discussion / related work.” | “We will evaluate LithOS/CXL experimentally in revision.” |
| XSched / Tally | “Motivation / partial expressibility of priority scheduling.” | “We will re-run XSched/Tally artifacts head-to-head.” |
| Safety | “Expand verifier + transition validation + taxonomy.” | “Formally verified entire GPU driver.” |

---

## 11. Paper LOC reconciliation table (for authors)

| Paper name (eval.tex / commented table) | Paper LOC | Best-effort files | Disk sum | Match? |
|-----------------------------------------|-----------|-------------------|----------|--------|
| Global LFU Eviction | 304 | `eviction_lfu.bpf.c` + `.c` | 224+82=306 | **Yes** |
| Multi-tenant Quota LRU | 472 | `eviction_pid_quota.bpf.c` + `.c` | 238+235=473 | **Yes** |
| Adaptive Seq. Prefetch | 375 | `prefetch_adaptive_sequential.bpf.c` + `.c` | 234+340=574 | **No — uncertain** |
| Stride Prefetch | 472 | `prefetch_stride.bpf.c` + `.c` | 293+180=473 | **Yes** |
| Tree-based Prefetch | 454 | `prefetch_pid_tree.bpf.c` + `.c` | 207+248=455 | **Yes** |
| Prefetch(lo,hi) | 454 | likely tree / pid family | ~455 | **Plausible** |
| Evict(lo,hi) | 472 | likely quota or combined pid | ~473 | **Plausible** |
| Dynamic Timeslice | 408 | `gpu_sched_set_timeslices.*` | 188+222=410 | **Yes** |
| Preemption Control | 925 | `gpu_preempt_ctrl.*` | 280+647=927 | **Yes** |
| Two-tenant combined | ~926 | Quota + Tree + Timeslice | 1334 if summed | **Uncertain** |
| Device L2 / CLC | 45 / 16 / 19 | device eBPF (not host `extension/` inventory) | n/a here | Device path |

---

*End of document. Older scratch list at `docs/paper/asplos-27-rebuttal/revision-plan.md` should defer to this file for SOTA/reproducibility promises. Inventory revision 2026-08-03.*
