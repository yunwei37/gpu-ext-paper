# ASPLOS'27 #1797 Revision Plan

Draft for the HotCRP comment. Body text below R0 is copy-paste ready.
Supporting inventory and safety limits: `reproducibility-commitments.md`.

## R0. Author checklist (do not paste)

- [ ] R1 names MoE-Infinity and XSched from `sota-baseline-feasibility.md`. Neither has been built on this host yet. Smoke-test both before sending, or soften to "we are evaluating" if a build fails today.
- [ ] R6: NVBit added SM_120 support in v1.7.4, released 2025-02-11, so the old "NVBit lacks Blackwell support" line cannot be reused. The only defensible reason the submitted table used the P40 is that those runs predate that release. A 5090 re-run is feasible; `sota-feas-sched.md` recommends v1.7.5 for a driver-575 header match.
- [ ] R1: XSched's public implementation gives Level-1 inter-kernel preemption on sm_120 (`arch.cpp` falls through to `CudaQueueLv1`; Level-2 and Level-3 return `nullptr`). Label the numbers accordingly, or a reviewer who knows the artifact will read them as paper-level preemption.
- [ ] Fix the LOC errors found in `loc-reconciliation.md` before the revised paper goes out. The 925 (`gpu_preempt_ctrl`) and 408 (`gpu_sched_set_timeslices`) figures check out and are separate entries, but the sequential prefetch claim of 375 should be 573, which shifts the two composite totals at `eval.tex:64` and `eval.tex:92`, and the two-tenant total of 926 at `eval.tex:136` omits the 408 timeslice component it names, so it should be 1334.
- [ ] Confirm the agent safety-event breakdown in R5 matches the numbers in `eval.tex`.

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

We thank the reviewers, and we plan the following revisions.

**Baselines (Reviewers E, F).** We will compare against the research systems that can actually run on our hardware, a single RTX 5090 with no A100 and no MIG available: MoE-Infinity on the MoE offloading workload, XSched on multi-tenant scheduling, and LMCache's local-disk backend for the storage-tier case Reviewer E raised. When a system's artifact cannot run on our machine but its policy fits our hooks, we will implement the policy instead. GPREEMPT's priority timeslicing already runs this way, as a gpubpf program with no driver source change (Fig. 12), and Expert Buffering's hot-expert residency becomes a page-granularity eviction and prefetch policy on our MoE workload. For the remaining systems we will state plainly why a head-to-head is not possible: GPREEMPT's own artifact is a kernel module built against driver 550, Tally's evaluation requires an A100, G10 exists only in simulation, and DeepUM and LithOS were never released.

**Expressibility and attribution (Reviewers E, F).** We will add a table showing which policies are feasible in user space, which require driver modification, and which gpubpf supports, and we will expand Fig. 13, where memory policies improve completion time by 55 to 92% while the scheduling policy contributes under 1%.

**Safety and design depth (Reviewers B, F).** Sections 3.4 and 4 will gain transition-validation pseudocode, the SIMT verifier algorithm, examples of rejected policies, a failure-mode taxonomy, and an explicit account of the trusted computing base.

**Measurements, artifacts, and discussion.** We will add RTX 5090 numbers to Table 1 (Reviewer A) and release the agent prompts and benchmark harnesses (Reviewer E). The text will also address thrashing under stale state, CXL tiers, per-tenant policies, trampoline overhead at high block counts, and portability of the driver hooks (Reviewers A, D).

We will not attempt multi-vendor ports, a storage tier inside gpubpf, or re-running the original artifact of every related system.
