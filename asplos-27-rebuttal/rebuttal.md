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

**How to address:** Point out that two SOTA comparisons already exist in the paper but were not foregrounded clearly enough:

1. GPREEMPT [14] (ATC'25) — we implemented its priority-timeslice policy as a 925-LOC gpubpf program with zero driver modification, achieving LC P99 latency reduction of 96% (Fig.12).
2. LMCache [9] — gpubpf matches its throughput with better tail latency (Fig.9).

For driver-level systems (TimeGraph, Gdev, GCAPS, LithOS): these require unsafe driver modification and restarts. The relevant comparison axis is whether their policies are expressible via gpubpf — the GPREEMPT result demonstrates this.

For E's specific citation (arXiv:2303.06182, MoE expert offloading via gating): explain that it is a framework-level solution that migrates experts as atomic units and requires runtime integration. Its gating-based prediction is expressible as a gpubpf uprobe policy on the gating function. We commit to implementing this gating-aware policy and comparing directly in revision.

Note: gpubpf's current approach (device-side stride tracing) and gating-based prediction are different mechanisms — stride tracing uses memory access patterns, gating uses the MoE router output. They are complementary, not equivalent."

## Q2. What safety guarantees does gpubpf provide for its fully asynchronous execution model? (F, B)

**F-Q3:** "What safety properties are enforced by the verifier? What kinds of unsafe or pathological policies are rejected, and how are invalid policies handled?"

**How to address:** Explain the two-layer safety model:

Layer 1 — Program safety: the unmodified Linux eBPF verifier (termination, memory safety, restricted kfuncs) plus SIMT-aware passes. Branches, loop bounds, and map keys must be warp-uniform; barriers, global synchronization, and non-uniform atomics are forbidden; per-hook resources are bounded (Section 3.5.1).

Layer 2 — Transition validity: callbacks never mutate state directly. They enqueue transition requests on driver-owned state machines. The driver validates each request against current state; stale or conflicting requests become no-ops or reordering — never invalid states (Section 3.4). Asynchrony affects optimality, not integrity. FIFO fallback under pressure or misconfiguration.

Empirical evidence: 59 agent-generated policies, 974 runs, 50 safety events (24 logic bugs, 18 performance regressions, 2 verifier rejections, 2 GPU verifier-caught overflows, 4 other), zero OS panics or data corruption.

The paper already contains: verifier rules (Section 3.5.1), TCB (Section 3.5), transition validity / FIFO fallback (Section 3.4), and empirical safety data (Section 5.3). The rebuttal should consolidate these existing answers rather than promising new content. For B specifically: note that the safety argument exists but is scattered — we will surface the two-layer invariant earlier in Section 1.

## Q3. Is multi-tenant GPU sharing a real use case? (E)

**E-W1:** "SemiAnalysis questions [MIG's] real-life value... inferencing workloads do not really use it."

**How to address:** SemiAnalysis's quote ("all online inferencing workloads require one GPU at a minimum") targets hyperscaler deployments (Meta, OpenAI, x.AI). But GPU underutilization is a widespread real problem: production clusters report 42% GPU memory utilization (MuxFlow, ByteDance, 20K+ GPUs, SCIS'24), and inference+training co-location is an active ASPLOS'25 topic (Tally). Software co-location (not hardware partitioning like MIG) is how operators address this — which is exactly what gpubpf targets (Fig.14: LC TPOT drops 40-45% while BE improves 28%). More importantly, multi-tenant is only one of four evaluation scenarios (RQ3); the paper's primary contributions (RQ1/RQ2) are entirely single-tenant.

## Q4. How would per-tenant policy isolation work? (D)

**D-Q3:** "What architectural enhancements are required to allow multiple users to safely execute their own distinct, custom eBPF resource policies simultaneously without cross-interference?"

**How to address:** Describe the path: per-cgroup policy attachment, verifier-enforced map namespacing, per-tenant hook budgets, driver-arbitrated cross-tenant transitions. The current single-policy design mirrors sched_ext's architecture; per-tenant isolation is future work.

## Q5. How much of the performance improvement comes from gpubpf itself vs. the specific policies evaluated? (F)

**F-Q2:** "To what extent can the performance improvements observed in the evaluation be attributed to gpubpf? Which of the evaluated policies could already be implemented by existing frameworks, runtimes, driver modifications, or instrumentation systems, and what trade-offs does gpubpf improve?"

**How to address:** Fig.13 already separates mechanism from policy: on memory-bound multi-tenant workloads, the GPREEMPT-style scheduling policy (expressible by existing frameworks) yields <1% improvement, while gpubpf memory policies (impossible in user space, unsafe as driver patches) yield 55-92% improvement. Fig.7a isolates device-side hooks: device-only prefetch gives 1.34x, combined host+device gives 1.77x. cudaMemAdvise captures part of the decode gain but needs application changes and costs 40% prefill throughput (Fig.8).

No additional commitment needed — the evidence is already in the paper. Summarize it concisely in the rebuttal.

## Q5. How portable is gpubpf beyond NVIDIA GPUs? (F, D)

**F-W5:** "The portability of the proposed mechanism is discussed only briefly."

**D-W5:** "Relies on NVIDIA's proprietary PTX instruction set, lacks immediate out-of-the-box portability to AMD or Intel."

**How to address:** Host-side design aligns with generic Linux abstractions (HMM/migrate_vma, DRM scheduler). Device-side can target vendor-neutral IR via SPIR-V backend (Section 4). Keep this brief — portability is minor for all reviewers.

## Q6. How does the system handle VRAM thrashing when workload patterns change faster than the map sync interval? (D)

**D-Q1:** "How does the system handle or mitigate sudden bursts of VRAM thrashing when workload access patterns mutate faster than your periodic cross-layer map synchronization interval?"

**How to address:** Explain that staleness affects optimality, not correctness — the driver's state machines enforce valid transitions regardless of map freshness. Snapshots merge at GPU kernel completions. Policies can rate-limit via PCIe-utilization guards (as the KV-cache policy already does). Under rapid mutation, the system degenerates to default FIFO eviction, which is no worse than baseline UVM.

No additional commitment needed — the mechanism explanation (staleness affects optimality not correctness, FIFO fallback) suffices for D who is already a weak accept.

## Q7. How does gpubpf handle workload-internal optimization heuristics that conflict with its policies? (A)

**A-C1:** "How does gpubpf handle when existing optimization heuristics baked into the workload adversarially affects the gpubpf policies, especially given the constraints of not changing the workload."

**How to address:** Cite the KV-cache agent case study as a concrete example: the agent detected thrashing between gpubpf's prefetch policy and vLLM's own allocator, and converged to a region-differentiated prefetch that works with (not against) the application's behavior. Also note that instant policy detachment bounds pathological interactions — if a policy degrades performance, it can be removed without restart.

## Q8. How does gpubpf work with workloads shipped as SASS binaries without PTX? (A)

**A-C2:** "How does it work with workloads shipped as SASS or binary? Is there a way to handle patching without relying on PTX?"

**How to address:** Distinguish two cases: host-side policies (memory management, scheduling) need no PTX at all — they operate entirely in the kernel driver. Device-side hooks primarily use PTX (present in fatbinaries for JIT compatibility in common ML frameworks). For SASS-only binaries, we have a working prototype of SASS-level patching leveraging NVBit's compiler infrastructure.

**Verify before submitting:** (1) PTX-in-fatbin claim holds for actual target applications (llama.cpp, vLLM/PyTorch, Faiss). (2) SASS patching prototype is in a presentable state — confirm what workloads it covers and any limitations, so the claim is precise.

## Q9. Can the hierarchical BPF map structure support non-composable data for scheduling decisions? (A)

**A-C3:** "Can you clarify a bit more how the BPF maps are stored?... Can you foresee any use cases that might require other forms of data to make better scheduling decisions, but the current map structure cannot quite accommodate?"

**How to address:** Explain that shards hold associative aggregates (counters, min/max); the eviction list is host-authoritative. Acknowledge honestly that non-composable global state (e.g., a sorted priority queue across all warps) cannot use the hierarchical shard model and must pin maps host-side at PCIe latency cost (Fig.15b shows CPU map access is 6000x slower than GPU-side). This is a real limitation for policies requiring globally-ordered data structures.

## Q10. Why was device-side overhead only measured on P40? (A)

**A-C5:** "Any reason why device-side overhead is only measured on P40?"

**How to address:** At submission time, device-side instrumentation was validated on P40. We have since extended support to RTX 5090 and will add device-side overhead numbers on RTX 5090 in revision.

## Q11. What was the agent setup for the policy exploration case studies? (E)

**E:** "More details are needed about the agent setup (prompts used for Claude, etc.) to make it more informative."

**How to address:** Commit to releasing prompts, benchmark harness, all 59 generated policies, and 974-run logs as a publicly available artifact.

## Q12. How intrusive is the ptrace-based instrumentation, and does trampoline overhead scale with kernel size? (D)

**D-W1:** "Host-side implementation remains tightly coupled with explicit hooks in the proprietary GPU driver module."

**D-W4:** "Reliance on dynamic binary instrumentation via ptrace... could spark stability and security compliance rejections in enterprise production."

**D-Q4:** "Does the runtime overhead of application-level trampoline hooks scale efficiently when executing massive, complex accelerator kernels characterized by extreme block counts and heavy thread utilization?"

**How to address:** For driver coupling: hooks are ~100 LOC over the open GPL kernel modules, aligned with HMM/migrate_vma and DRM abstractions — not proprietary internals. For ptrace: it is a one-time attach (273ms startup), used only for device-side hooks; LD_PRELOAD is supported as an alternative — no ptrace needed in production. Host-side driver-hook policies touch no application code at all. For trampoline scaling: overhead is per-warp (warp leader executes, shuffle-broadcasts result), O(1) w.r.t. block count; Table 1 shows 3-14% on llama.cpp prefill.

## Q13. How does gpubpf's model extend to storage-tier offloading, CXL memory, and future accelerator design? (E, D, A)

**E-Q1:** "KVCache offload is increasingly to storage these days... How would eBPF handle such use case?"

**D-Q2:** "Can the proposed asynchronous resource state machine model scale seamlessly into hybrid server environments that incorporate emerging disaggregated memory architectures like tiered CXL memory pools?"

**A-C4:** "It's worth adding some discussion of how this affects the design of future accelerators: how much to implement in hardware, what kind of abstraction to expose."

**How to address:** All three are natural extensions of the state machine model. Storage tier: add new states and transitions; ms-scale transfers fit the async model; gpubpf supplies placement policy, complementary to Weka/VAST/CMX transport. CXL: new memory tiers map to new states atop HMM/migrate_vma; the async model fits CXL's higher latencies. Future accelerators: verified state-transitions could serve as the abstraction hardware exposes natively — architected attach points, firmware-validated transition tables, privileged telemetry. Each is one sentence in the rebuttal; this is the lowest-priority section and the first to cut if over word limit.
