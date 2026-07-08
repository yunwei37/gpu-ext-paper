# Author Response

| Rev | Overall | Confidence / Notes | Key Concerns | Rebuttal Goal |
|---|---|---|---|---|
| A | 4 — Accept (OS-advance: 5) | Deeply engaged; "impressive engineering feat", "exciting future of systems research" | Five clarification questions: adversarial app heuristics; SASS-only binaries; map storage & non-composable data; future-accelerator implications; why P40 only | **Primary champion target**: convert from voter to defender — A is the only supporter with the depth to counter F in discussion |
| B | 3 — Neutral | Confidence 2; admits judging "from the first two pages" | Doubts safety guarantees are possible for a fully asynchronous mechanism | Neutralize with the two-layer safety model; commit to surfacing the invariant in §1 |
| C | 5 — Strong ASPLOS paper | High confidence, but the review is two sentences | None | Score champion; a thin review cannot carry a contested discussion alone — nothing to fix, C supplies the vote, A must supply the defense |
| D | 3 — Weak accept | Thorough, constructive | Proprietary-driver coupling; eventual-consistency staleness/thrashing; single system-wide policy; ptrace intrusiveness; PTX-only portability; Qs on CXL and trampoline scaling | Answer all four questions to solidify the weak accept |
| E | 2 — Leaning reject (OS-advance: 4) | Medium; lists five strengths | Missing SOTA MoE baseline (arXiv:2303.06182); MIG real-world relevance (SemiAnalysis); KV-cache offload to storage; wants agent prompts/details | Move 2→3 via existing evidence + gating-policy commitment + artifact release |
| F | 2 — Leaning reject (OS-advance: 4) | Most substantive negative; "core idea very interesting" | SOTA research baselines; mechanism-vs-policy attribution; safety-evaluation depth (verifier, rejected policies, failure modes, TCB); thin design sections; portability | Convert objections to "fixable in revision" |

## Q1. Why doesn't the evaluation compare against state-of-the-art research systems? (E, F)

**E:** "There is related work like arXiv:2303.06182 that moves experts dynamically into HBM based on the gating function outcome... I think the work needs to compare against SOTA research from the field."

**F-Q1:** "Are there state-of-the-art research systems for GPU memory management or scheduling that could be included as evaluation baselines? If not, why are they not applicable or directly comparable?"

**Response:** Two SOTA comparisons already exist in the paper: (1) GPREEMPT [14] (ATC'25), whose priority-timeslice policy we implemented as a 925-LOC gpubpf program with zero driver modification, achieving LC P99 latency reduction of 96% (Fig.12); and (2) LMCache [9], where gpubpf matches its throughput with better tail latency (Fig.9). Driver-level systems (TimeGraph, Gdev, GCAPS, LithOS) require unsafe driver modification and restarts; the relevant comparison axis is whether their policies are expressible via gpubpf, and the GPREEMPT result demonstrates they are. For arXiv:2303.06182 specifically, this is a framework-level solution that migrates experts as atomic units and requires runtime integration; its gating-based prediction is expressible as a gpubpf uprobe policy on the gating function. We can implement this gating-aware policy and compare directly in revision. (Note: gpubpf's current stride tracing and gating-based prediction are different, complementary mechanisms.)

## Q2. What safety guarantees does gpubpf provide for its fully asynchronous execution model? (F, B)

**F-Q3:** "What safety properties are enforced by the verifier? What kinds of unsafe or pathological policies are rejected, and how are invalid policies handled?"

**B:** "From the first two pages, it is difficult to gauge whether the claimed safety guarantees for a fully asynchronous mechanism like this are really possible."

**Response:** Safety rests on two independent layers. First, program safety: the unmodified Linux eBPF verifier enforces termination, memory safety, and restricted kfuncs, while SIMT-aware passes require warp-uniform branches, loop bounds, and map keys, and forbid barriers, global synchronization, and non-uniform atomics (Section 3.5.1). Second, transition validity: callbacks never mutate state directly but enqueue requests on driver-owned state machines, which validate each request against current state; stale or conflicting requests become no-ops, never invalid states (Section 3.4). Asynchrony affects optimality, not integrity, with FIFO fallback under pressure. Empirically, 59 agent-generated policies across 974 runs produced 50 safety events (24 logic bugs, 18 performance regressions, 2 verifier rejections, 2 GPU verifier-caught overflows, 4 other) with zero OS panics or data corruption (Section 5.3). The paper already contains all these elements (verifier rules in Section 3.5.1, TCB in Section 3.5, FIFO fallback in Section 3.4); for B's concern that the first two pages do not convey this, we will surface the two-layer invariant earlier in Section 1.

## Q3. Is multi-tenant GPU sharing a real use case? (E)

**E-W1:** "SemiAnalysis questions [MIG's] real-life value... inferencing workloads do not really use it."

**Response:** SemiAnalysis's observation applies to hyperscaler deployments (Meta, OpenAI, x.AI), but GPU underutilization remains widespread: production clusters report 42% GPU memory utilization across 20K+ GPUs (MuxFlow, SCIS'24), and inference+training co-location is an active research direction at ASPLOS'25 (Tally). gpubpf targets software co-location rather than hardware partitioning like MIG (Fig.14: LC TPOT drops 40-45% while BE improves 28%). We also note that multi-tenant is only one of four evaluation scenarios (RQ3); the paper's primary contributions (RQ1/RQ2) are entirely single-tenant.

## Q4. How would per-tenant policy isolation work? (D)

**D-Q3:** "What architectural enhancements are required to allow multiple users to safely execute their own distinct, custom eBPF resource policies simultaneously without cross-interference?"

**Response:** The path to per-tenant isolation involves per-cgroup policy attachment, verifier-enforced map namespacing, per-tenant hook budgets, and driver-arbitrated cross-tenant transitions. The current single-policy design mirrors sched_ext's architecture; per-tenant isolation is future work.

## Q5. How much of the performance improvement comes from gpubpf itself vs. the specific policies evaluated? (F)

**F-Q2:** "To what extent can the performance improvements observed in the evaluation be attributed to gpubpf? Which of the evaluated policies could already be implemented by existing frameworks, runtimes, driver modifications, or instrumentation systems, and what trade-offs does gpubpf improve?"

**Response:** Fig.13 already separates mechanism from policy: on memory-bound multi-tenant workloads, the GPREEMPT-style scheduling policy (expressible by existing frameworks) yields <1% improvement, while gpubpf memory policies (impossible in user space, unsafe as driver patches) yield 55-92%. Fig.7a isolates device-side hooks: device-only prefetch gives 1.34x, combined host+device gives 1.77x. cudaMemAdvise captures part of the decode gain but requires application changes and costs 40% prefill throughput (Fig.8).

## Q6. How portable is gpubpf beyond NVIDIA GPUs? (F, D)

**F-W5:** "The portability of the proposed mechanism is discussed only briefly."

**D-W5:** "Relies on NVIDIA's proprietary PTX instruction set, lacks immediate out-of-the-box portability to AMD or Intel."

**Response:** The host-side design aligns with generic Linux abstractions (HMM/migrate_vma, DRM scheduler), and the device-side can target vendor-neutral IR via the SPIR-V backend described in Section 4.

## Q7. How does the system handle VRAM thrashing when workload patterns change faster than the map sync interval? (D)

**D-Q1:** "How does the system handle or mitigate sudden bursts of VRAM thrashing when workload access patterns mutate faster than your periodic cross-layer map synchronization interval?"

**Response:** Staleness affects optimality, not correctness: the driver's state machines enforce valid transitions regardless of map freshness, and snapshots merge at GPU kernel completions. Policies can rate-limit via PCIe-utilization guards, as the KV-cache policy already does. Under rapid mutation, the system degenerates to default FIFO eviction, which is no worse than baseline UVM.


## Q8. How does gpubpf handle workload-internal optimization heuristics that conflict with its policies? (A)

**A-C1:** "How does gpubpf handle when existing optimization heuristics baked into the workload adversarially affects the gpubpf policies, especially given the constraints of not changing the workload."

**Response:** The KV-cache agent case study (Section 5.3) demonstrates exactly this scenario: the agent detected thrashing between gpubpf's prefetch policy and vLLM's own allocator, and converged to a region-differentiated prefetch that works with the application's behavior rather than against it. More generally, instant policy detachment bounds pathological interactions — if a policy degrades performance, it can be removed without restart.

## Q9. How does gpubpf work with workloads shipped as SASS binaries without PTX? (A)

**A-C2:** "How does it work with workloads shipped as SASS or binary? Is there a way to handle patching without relying on PTX?"

**Response:** Host-side policies (memory management, scheduling) need no PTX at all and operate entirely in the kernel driver. Device-side hooks primarily use PTX, which is present in fatbinaries for JIT compatibility in common ML frameworks. For SASS-only binaries, we have a working prototype of SASS-level patching leveraging NVBit's compiler infrastructure.


## Q10. Can the hierarchical BPF map structure support non-composable data for scheduling decisions? (A)

**A-C3:** "Can you clarify a bit more how the BPF maps are stored?... Can you foresee any use cases that might require other forms of data to make better scheduling decisions, but the current map structure cannot quite accommodate?"

**Response:** Shards hold associative aggregates (counters, min/max), and the eviction list is host-authoritative. Non-composable global state such as a sorted priority queue across all warps cannot use the hierarchical shard model and must pin maps host-side at PCIe latency cost (Fig.15b: CPU map access is 6000x slower than GPU-side). This is a real limitation for policies requiring globally-ordered data structures.

## Q11. Why was device-side overhead only measured on P40? (A)

**A-C5:** "Any reason why device-side overhead is only measured on P40?"

**Response:** At evaluation time, while our device-side instrumentation supports 5090 and our cuda version, NVbit did not yet support RTX 5090, so our device-side instrumentation was validated and compared on P40. We will add RTX 5090 device-side overhead numbers in revision.

## Q12. What was the agent setup for the policy exploration case studies? (E)

**E:** "More details are needed about the agent setup (prompts used for Claude, etc.) to make it more informative."

**Response:** We will release prompts, benchmark harness, all 59 generated policies, and 974-run logs as a publicly available artifact.

## Q13. How intrusive is the ptrace-based instrumentation, and does trampoline overhead scale with kernel size? (D)

**D-W1:** "Host-side implementation remains tightly coupled with explicit hooks in the proprietary GPU driver module."

**D-W4:** "Reliance on dynamic binary instrumentation via ptrace... could spark stability and security compliance rejections in enterprise production."

**D-Q4:** "Does the runtime overhead of application-level trampoline hooks scale efficiently when executing massive, complex accelerator kernels characterized by extreme block counts and heavy thread utilization?"

**Response:** ptrace is a one-time attach (273ms startup) used only for device-side hooks; LD_PRELOAD is supported as an alternative, so no ptrace is needed in production. Host-side driver-hook policies touch no application code at all. Trampoline overhead is per-warp (warp leader executes, shuffle-broadcasts result), O(1) with respect to block count; Table 1 shows 3-14% on llama.cpp prefill.

## Q14. How does gpubpf's model extend to storage-tier offloading, CXL memory, and future accelerator design? (E, D, A)

**E-Q1:** "KVCache offload is increasingly to storage these days... How would eBPF handle such use case?"

**D-Q2:** "Can the proposed asynchronous resource state machine model scale seamlessly into hybrid server environments that incorporate emerging disaggregated memory architectures like tiered CXL memory pools?"

**A-C4:** "It's worth adding some discussion of how this affects the design of future accelerators: how much to implement in hardware, what kind of abstraction to expose."

**Response:** All three are natural extensions of the state machine model. A storage tier adds new states and transitions where millisecond-scale transfers fit the async model, with gpubpf supplying placement policy complementary to Weka/VAST/CMX transport. CXL memory tiers map to new states atop HMM/migrate_vma, and the async model is a natural fit for CXL's higher latencies. For future accelerators, verified state-transitions could serve as the abstraction hardware exposes natively through architected attach points, firmware-validated transition tables, and privileged telemetry.
