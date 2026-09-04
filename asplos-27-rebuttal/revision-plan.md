# ASPLOS'27 #1797 Revision Plan

## Current execution record — 2026-09-04

This file retains the historical proposal below, not a completion report.
The [review archive](README.md) preserves all seven reviews, the original
Q1–Q15 author response, and the submitted revision/shepherd comments; the
[live completion checklist](../../revision-completion-checklist.md) tracks
experiments, paper integration and artifact publication separately.
MoE-Infinity, XSched, the GPreempt contention and LC-knee studies, Expert
Buffering, FineMoE, Hummingbird and POD have completed their scoped
comparisons, including adverse results. The
[reviewer-facing ledger](../../experiment/policy/reference/RELATED_POLICY_EXPRESSIBILITY.md)
now covers 48 papers across seven policy families and links each measured
baseline -> native-policy -> BPF result without classifying any surveyed whole
system as fully expressible. Two
original strict-device counter positive/negative pairs pass, and two fresh
pairs also pass on the verifier-enabled Table 1 runtime. Actual
`kernelretsnoop`/`threadhist` A0 strict admission is now complete: an
independent analyzer accepts all five correctness cells and the complete pp32
preflight block, with every gpubpf cell bound to one target-PID admission and
its exact expected map. A1 admission-cost and S0 STRICT/NO_VERIFY steady-state
pairing remain open. The
[invalid-prefetch transition campaign](../../experiment/revision-safety/prefetch-invalid-575-02/result-review.md)
now completes all three live controls and exact old-UVM restoration. The
scheduler-init diagnostic and its 16-cell live transition matrix are complete;
all cells passed and the original driver/services were restored. LMCache disk is paused at the user's
request after a cross-arm correctness failure; its promised measurement is not
complete. Expert Buffering has completed its matched-policy study. The RTX 5090
device-side comparison now has a valid, independently analyzed two-tool subset:
all five correctness configurations and all 10 randomized pp=512 blocks passed,
with no rejected or retried cell. Exit-record overhead is 99.663% for gpubpf
and 99.621% for matched NVBit (gpubpf is 0.04185 percentage points slower),
while exit-count-histogram overhead is 4.007% and 10.301% (gpubpf is 6.29351
points lower). This is a mixed result, not a general gpubpf-over-NVBit win.
It completes only the non-cross-clock `kernelretsnoop` and `threadhist` rows;
the `launchlate` comparison remains invalid, and the verification-disabled
runtime does not establish verifier overhead. The frozen plan named llama.cpp
build 7101, while every accepted preflight and full-run arm consistently used
build 7102; this creates no cross-arm mismatch but is a disclosed deviation.
POD's separate phase campaign
is complete and measures about 1.8% same-path operator cost while exposing a
large, explicitly non-generic fresh-process cold path. A new cross-layer map
campaign also completes 15/15 cells, recovering 34,560 bounded raw tuples and
detecting all 2,560 deliberate overflow drops; it is expressibility evidence,
not a map-performance or strict-verifier result. The synthetic RTX 5090
trampoline-scaling study is complete: no-op cost remains in the
0.0012--0.0022 ms range at 4,096 blocks, while a counter callback grows from
0.0204 to 0.5417 ms as active warps grow from 2,048 to 32,768. This is a
controlled hook-cost result, not an application-level performance claim.
The [GPreempt load report](../../../workloads/gpreempt/results-load-study-575-20260903.md)
and [LC-knee report](../../../workloads/gpreempt/results-lc-knee-575-20260903.md)
retain the foreground/background tradeoff and conditional overload boundary.
Original agent transcripts have not been recovered.
The integrated draft was built and visually checked (16 pages, conclusion on
page 14); the working page budget and unmeasured commitments remain open.
Deployment and loader audits are also complete at their stated CPU-only
boundaries: both startup and running-process lifecycle paths completed 5/5
times, and strict verification rejected all three invalid-program trials
without consuming a program ID, whereas warning/default modes admitted them.

Several assertions in the old proposal were corrected by source/raw-data audit:
the old 96% launch-latency metric was not host-to-kernel-entry latency; historical
Fig. 13 did not prove scheduler engagement; invalid transitions have
operation-specific fallback rather than universal no-ops; the GPU prototype
uses PREVAIL plus SIMT analysis, distinct from Linux kernel verification; and
per-warp instrumentation does not make total cost independent of block count.
Those sentences below must not be reused as current paper claims. The old R0
statement that only two items bind the revision also does not supersede the
subsequently submitted author/shepherd commitments.

## Historical proposal

Draft for the HotCRP comment. Body text below R0 is copy-paste ready.
Supporting inventory and safety limits: `reproducibility-commitments.md`.

## R0. Author checklist (do not paste)

- [ ] R1 names MoE-Infinity and XSched from `sota-baseline-feasibility.md`, neither of which has been built on this host yet. The short version commits to at least one runnable baseline per axis and names these two as the ones being brought up, so a single failed build is survivable, but both failing is not. Smoke-test them early; `sota-feas-moe.md` lists DeepSpeed ZeRO-Inference and PowerInfer as fallbacks for the MoE axis, and `sota-feas-sched.md` lists Orion for the scheduling axis.
- [x] R6: NVBit added SM_120 support in v1.7.4, released 2025-02-11, so the old "NVBit lacks Blackwell support" line cannot be reused. The submitted P40-only comparison reflected a gap in the original evaluation, not a lack of Blackwell support in NVBit. The valid 5090 two-tool result above closes those two rows; `launchlate` remains invalid.
- [ ] R1: XSched's public implementation gives Level-1 inter-kernel preemption on sm_120 (`arch.cpp` falls through to `CudaQueueLv1`; Level-2 and Level-3 return `nullptr`). Label the numbers accordingly, or a reviewer who knows the artifact will read them as paper-level preemption.
- [ ] Fix the LOC errors found in `loc-reconciliation.md` before the revised paper goes out. The 925 (`gpu_preempt_ctrl`) and 408 (`gpu_sched_set_timeslices`) figures check out and are separate entries, but the sequential prefetch claim of 375 should be 573, which shifts the two composite totals at `eval.tex:64` and `eval.tex:92`, and the two-tenant total of 926 at `eval.tex:136` omits the 408 timeslice component it names, so it should be 1334.
- [ ] Confirm the agent safety-event breakdown in R5 matches the numbers in `eval.tex`.
- [ ] The submitted author response was `rebuttal.md`, not `rebuttal-v3.md` or `fable.md`. The meta-review binds us to what that file says, which is only two hard commitments: RTX 5090 experiments in the Table 1 device-side comparison (Q8) and a public release of prompts and benchmark harnesses (Q14). Everything else in this plan is a voluntary addition, so it can be scoped, but the two above cannot. Note in particular that `fable.md`'s promise to implement a gating-aware MoE policy and compare directly was never submitted and does not bind us.

---

We thank the reviewers and the committee. Below is our plan for each requested revision.

**R1. Comparison against state-of-the-art research systems (Reviewers E, F).**
We will strengthen the evaluation along two axes. First, we will foreground two research-system comparisons that already exist in the submission but are currently underplayed: a GPREEMPT [ATC'25] equivalent priority-timeslice and preemption policy implemented entirely as gpubpf programs, with no driver source modification for the policy logic, reducing latency-critical P99 launch latency by 96% (Fig. 12); and a comparison against LMCache, a state-of-the-art framework-managed KV-cache system, where gpubpf matches throughput with better tail latency (Fig. 9), which we will extend to LMCache's local-disk backend so that the storage-tier offload case Reviewer E raised is answered with measurements rather than only discussion. Second, we will add head-to-head comparisons against research artifacts that run on our hardware, a single RTX 5090 (sm_120, 32 GB) plus a Tesla P40, with no A100/H100, no multi-GPU, and no MIG: **MoE-Infinity** (activation-aware expert offloading, public artifact with an explicit Blackwell build path) on the MoE offloading workload, and **XSched** (OSDI'25, transparent preemptive scheduling that requires no driver patch) on the multi-tenant scheduling workload, reported at the level of preemption its public implementation provides on our GPU. Where a system's artifact cannot run on this hardware, the revision will say so explicitly with the reason rather than omitting the system: GPREEMPT's artifact is a kernel module built against driver 550 and does not load on our 575 driver, which is why we compare against its policy rather than its binary; Tally's artifact evaluation requires an A100; Mooncake requires multi-node RDMA; G10 is simulator-only; and Expert Buffering (arXiv:2303.06182), DeepUM, and LithOS have no public artifact.

**R2. Policy expressibility table (Reviewers E, F).**
We will add a table mapping each evaluated policy class to its feasibility under (a) user-space and framework APIs, (b) ad-hoc driver source modification, and (c) gpubpf, with each gpubpf cell pointing at the concrete in-tree program. For driver-level systems such as TimeGraph, Gdev, GCAPS, LithOS, and XSched, the comparable axis is whether the core policy idea is expressible on gpubpf, which the GPREEMPT-equivalent result demonstrates concretely. Cells will be marked feasible, partial, unsafe, or infeasible rather than with checkmarks, so the trade-off each approach pays is visible.

**R3. MoE expert management (Reviewer E, arXiv:2303.06182).**
Expert Buffering operates at framework level, migrating experts as atomic units under gating-function guidance. We will add a subsection contrasting that design with gpubpf's transparent page-granularity residency management, implemented by the existing MoE eviction and prefetch policies, and quantify where page granularity wins (partial-expert reuse, compute-transfer overlap) and where expert-atomic migration wins. We will state precisely which comparisons we ran and which we could not, rather than claiming numerical reproduction of results obtained on a different model and cluster.

**R4. Separating mechanism from policy (Reviewer F).**
We will expand the analysis of Fig. 13, which already isolates the two: on memory-bound multi-tenant workloads the GPREEMPT-style scheduling policy yields under 1% improvement while gpubpf's memory-management policies yield 55 to 92%. The revision will state, per evaluated policy, which results depend on OS-level page-fault hooks that are unavailable in user space, which depend on cross-domain coordination of memory and scheduling, and which could be obtained by an existing framework at the cost of per-framework integration, safety, or the ability to hot-swap policies.

**R5. Safety guarantees, design depth, and TCB (Reviewers B, F).**
We will expand Sections 3.4 and 4 with transition-validation pseudocode, the SIMT-aware verifier algorithm, concrete examples of rejected policies (lane-varying branches, unbounded eviction-list loops), a failure-mode taxonomy aligned with the agent study's safety events, and an explicit TCB statement covering the OS kernel, the gpubpf driver module, the GPU compiler backend, and GPU firmware. The two-layer argument will be made explicit: program safety from the unmodified Linux eBPF verifier plus SIMT passes, and transition validity from driver-owned state machines that degenerate stale or conflicting requests into no-ops. The design and implementation sections will be extended using part of the two additional pages.

**R6. Device-side overhead on current hardware (Reviewer A).**
We will add RTX 5090 measurements to Table 1, including the NVBit comparison, and state in the text why the submitted version used the P40. Fig. 15(a) already reports gpubpf device-side overhead on the RTX 5090; the revision will make the two devices consistent so the comparison does not depend on the reader inferring the reason.

**R7. Artifacts (Reviewer E).**
We will release the agent prompts, interaction logs, and benchmark harnesses used in the policy-exploration study, so the agent-driven results are inspectable and repeatable.

**R8. Portability and deployment intrusiveness (Reviewers D, F).**
We will expand the portability discussion: host-side hooks require approximately 100 LOC over the open GPL kernel modules and align with existing Linux HMM/migrate_vma and DRM scheduler abstractions; the device-side JIT targets PTX today with a SPIR-V backend path, and we will report our SASS-level patching prototype for binaries shipped without PTX (Reviewer A). We will also clarify that the ptrace attach is a one-time 273 ms operation used only for device-side hook injection, and that LD_PRELOAD is supported as a non-intrusive alternative for production deployment (Reviewer D).

**R9. Additional discussion items.**
We will address, in the text: mitigation of thrashing when access patterns change faster than the map synchronization interval, including the driver's retained eviction authority and the policy-side PCIe-utilization guard (Reviewer D); extension of the asynchronous state machine to CXL tiers, positioned as complementary to transport solutions, with the storage tier covered experimentally in R1 (Reviewers D, E); what per-tenant policy isolation would require, namely per-cgroup policy attachment and verifier-enforced map namespacing (Reviewer D); why trampoline overhead is independent of block count, since the hook is per-warp with shuffle broadcast (Reviewer D); which forms of state the hierarchical map structure cannot merge and how host-authoritative maps handle them (Reviewer A); implications for future accelerator design, where verified state transitions become an architected attach point (Reviewer A); and the distinction between static hardware partitioning, which the cited SemiAnalysis critique targets, and the software co-location setting gpubpf addresses (Reviewer E).

**Out of scope for this revision.**
To keep the plan achievable by September 8, we will not attempt: multi-vendor performance campaigns on AMD or Intel GPUs; a CXL or GPUDirect Storage tier implemented inside gpubpf itself, separate from the LMCache disk-backend comparison in R1; LithOS-scale whole-GPU-OS experiments; or re-running the original artifact of every related system. Portability and tiering will be argued at the design level with the mechanisms above.

---
---

# Short version (alternative to the above, about one fifth the length)

Pick one of the two, do not send both. Same commitments, no supporting detail.

---

We thank the reviewers and the committee! We will implement these changes:

**Q1, state-of-the-art baselines (Reviewers E, F).** We will add at least three runnable state-of-the-art research baselines, such as MoE-Infinity, XSched, and an extension of the existing LMCache comparison to its local-disk backend. When an artifact cannot run on our hardware but its policy fits our hooks, we will implement the policy instead, as we already do for GPREEMPT's priority timeslicing (Fig. 12) and will do for Expert Buffering's hot-expert residency. Where neither route is open we will name the system and say why.

**Q2, safety and design depth (Reviewers B, F).** We will add transition-validation pseudocode, the SIMT verifier algorithm, examples of rejected policies, a failure-mode taxonomy, and an explicit account of the trusted computing base to the design and implementation sections.

**Policy versus mechanism (Reviewer F).** We will add a policy expressibility table separating what is feasible in user space, what requires driver modification, and what gpubpf supports, and we will expand Fig. 13, which already separates the two. For each policy class we will state which of the two the result depends on.

**Measurements, artifacts, and discussion.** We will add RTX 5090 numbers to Table 1 (Reviewer A) and release the agent prompts and benchmark harnesses (Reviewer E). The text will also address thrashing under stale state, CXL tiers, per-tenant policies, trampoline scaling, and portability (Reviewers A, D), and will distinguish our software co-location setting from the static partitioning the SemiAnalysis critique targets(Reviewer E).
