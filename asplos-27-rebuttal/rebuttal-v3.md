# Author Response -- ASPLOS'27 Paper #1797 (gpubpf)

| Rev | Overall | Confidence/Notes | Key Concerns | Rebuttal Goal |
|-----|---------|-----------------|-------------|---------------|
| A | 4 Accept | 4; "impressive engineering feat" | Clarifications: adversarial heuristics, SASS, maps, accelerators, P40 | Primary champion: arm for PC discussion |
| B | 3 Neutral | 2; judged from first two pages | Async safety guarantees | Neutralize with two-layer model |
| C | 5 Strong ASPLOS | 3 High; two-sentence review | None | Score anchor; no action needed |
| D | 3 Weak accept | 2; thorough, constructive | Thrashing, CXL, per-tenant, trampoline scaling | Solidify weak accept |
| E | 2 Leaning reject | 3; lists five strengths | SOTA MoE baseline, MIG relevance, storage offload, agent setup | Move 2->3 via existing evidence |
| F | 2 Leaning reject | 3; "core idea very interesting" | SOTA baselines, attribution, safety depth, design sections, portability | Convert objections to fixable-in-revision |

We thank all reviewers for their detailed feedback.

## Q1. Are there state-of-the-art research systems that should be included as evaluation baselines? (E, F)

**E:** "there is related work like https://arxiv.org/pdf/2303.06182 that moves experts dynamically into HBM based on the gating function outcome, while overlapping the movement with collectives. I think the work needs to compare against SOTA research from the field."

**F:** "The evaluation compares only against state-of-practice baselines [...] even though the motivation and related work discuss several state-of-the-art research systems for GPU scheduling and memory management/offloading."

**Response:** Two SOTA comparisons already appear in the evaluation: the paper implements GPREEMPT's [ATC'25] priority-timeslice scheduling as a 925-LOC gpubpf program with zero driver-source changes, reducing LC P99 latency by 96% (Fig.12), and matches LMCache [arXiv'25], a SOTA KV-cache framework, with better tail latency (Fig.9). arXiv:2303.06182 is a framework-level MoE optimization (Meta AI) that migrates experts as atomic units via gating-function outputs, requiring runtime integration; it operates at a fundamentally different abstraction level than gpubpf's transparent, page-granularity approach, making a controlled head-to-head comparison infeasible without shared experimental assumptions. Driver-level systems (TimeGraph, Gdev, GCAPS, LithOS) require unsafe driver modifications and service interruptions; the comparable axis is whether their policies are expressible on gpubpf, which the GPREEMPT result demonstrates.

## Q2. What safety properties does gpubpf enforce, and how thoroughly are they evaluated? (B, F)

**B:** "it is difficult to gauge whether the claimed safety guarantees for a fully asynchronous mechanism like this are really possible."

**F:** "I would expect a more detailed analysis of the verifier's guarantees, examples of rejected unsafe policies, potential failure modes, the trusted computing base (TCB), and how the system handles buggy or pathological policies."

**F:** "The design and implementation sections are relatively thin."

**Response:** gpubpf enforces safety through two independent layers: (1) program safety via the unmodified Linux eBPF verifier (termination, memory safety, restricted kfuncs) plus SIMT-aware passes that reject lane-varying branches, unbounded loops, and non-uniform atomics (Section 3.5.1); and (2) transition validity via driver-owned state machines that validate each request against current state, degenerating stale or conflicting requests into no-ops rather than invalid states (Section 3.4). The TCB comprises the OS kernel, gpubpf driver module, GPU compiler backend, and GPU firmware (Section 3.5). Empirically, across 59 agent-generated policies and 974 runs, gpubpf caught 50 safety events, including 2 verifier-rejected policies (lane-varying branches and unbounded eviction-list loops), with zero panics or data corruption. The revision will expand Sections 3.4 and 4 with transition-validation pseudocode, the SIMT-verifier algorithm, verifier-rejection examples, and a failure-mode taxonomy.

## Q3. How much of the performance improvement comes from gpubpf itself versus the specific policies? (F)

**F:** "The paper does not clearly distinguish between the benefits of the general gpubpf mechanism and those of the specific hand-written policies evaluated."

**F:** "To what extent can the performance improvements observed in the evaluation be attributed to gpubpf? Which of the evaluated policies could already be implemented by existing frameworks [...]?"

**Response:** Fig.13 directly separates mechanism from policy: on memory-bound multi-tenant workloads, the GPREEMPT-style scheduling policy yields <1% improvement, while gpubpf's memory management policies yield 55-92%. These memory policies require OS-level page-fault hooks that are impossible in user space and unsafe as ad-hoc driver patches; existing frameworks could implement equivalent prefetch logic per-framework, but cannot coordinate memory and scheduling cross-domain or hot-swap policies at runtime without restarts. The revision will add a policy expressibility table mapping each evaluated policy to {user-space / driver-modification / gpubpf-only}.

## Q4. Is multi-tenant GPU sharing a real use case, and how would per-tenant isolation work? (E, D)

**E:** "SemiAnalysis, for example, questions its real-life value. For example, gpubpf compares itself to MIG GPU partitioning in 2.3, but SemiAnalysis reports that inferencing workloads do not really use it."

**D:** "what architectural enhancements are required to allow multiple users to safely execute their own distinct, custom eBPF resource policies simultaneously without cross-interference?"

**Response:** The SemiAnalysis article criticizes static hardware partitioning (MIG) at hyperscaler scale, which aligns with the paper's own critique in Section 2.3; gpubpf targets software co-location, not MIG. Production GPU underutilization is well-documented even for inference: MuxFlow (ByteDance, SCIS'24) reports 42% GPU memory utilization across 20,000+ inference GPUs, Orion (EuroSys'24) reports below 40% compute throughput, and Tally (ASPLOS'25) demonstrates inference+training co-location at a top venue. gpubpf's multi-tenant results (Fig.14: LC TPOT -40-45%, BE throughput +28%) build on this line of work. Per-tenant isolation (D-Q3) would require per-cgroup policy attachment and verifier-enforced map namespacing; the current single-policy design mirrors sched_ext, with per-tenant isolation as future work.

## Q5. How does gpubpf handle workload-internal heuristics that conflict with its policies? (A)

**A:** "How does gpubpf handles when existing optimization heuristic baked into the workload adversarially affects the gpubpf policies, especially given the constraints of not changing the workload."

**Response:** Section 5.3's KV-cache agent study directly illustrates this: the agent detected mutual thrashing between its prefetch policy and vLLM's internal allocator, then converged to a region-differentiated prefetch strategy that avoids the conflict. gpubpf's instant policy detachment bounds pathological cases, and the NVIDIA driver's existing thrashing detector (uvm_perf_thrashing.h) independently disables prefetches that cause excessive page migration.

## Q6. How does gpubpf work with workloads shipped as SASS binaries without PTX? (A)

**A:** "How does it work with workloads ship as SASS or binary? Is there a way to handle patching without relying on PTX?"

**Response:** Host-side policies (memory management, scheduling) operate entirely in the kernel driver and require no PTX. For device-side hooks on SASS-only binaries, gpubpf has a working prototype of SASS-level patching using NVBit's compiler infrastructure.

## Q7. Can the hierarchical BPF map structure support non-composable data? (A)

**A:** "Can you foresee any use cases that might require other forms of data to make better scheduling decisions, but the current map structure cannot quite accommodate?"

**Response:** gpubpf maps store data across three memory tiers (host DRAM, GPU global memory, GPU shared memory), supporting both associative aggregates and raw per-access data; the MoE and KV-cache case studies (Section 5.3) use device-side memory tracing that samples per-page access counts into GPU global memory. Non-composable global state that cannot be hierarchically merged can use host-pinned maps at PCIe latency cost (Fig.15b: 34ms per CPU map access); the eviction list, for example, is host-authoritative by design.

## Q8. Why was device-side overhead only measured on P40? (A)

**A:** "Any reason why device side overhead is only measured on P40?"

**Response:** Table 1 uses the P40 for comparison against NVBit because NVBit lacked sm_120 (Blackwell) support until v1.7.4 (February 2025); the comparison shows gpubpf's 3-14% overhead versus NVBit's 85-93%. Fig.15(a) already measures gpubpf's device-side operation overhead on the RTX 5090, showing 65-81% reduction versus naive per-thread execution.

## Q9. How does gpubpf handle VRAM thrashing when workload patterns change faster than the map sync interval? (D)

**D:** "How does the system handle or mitigate sudden bursts of VRAM thrashing when workload access patterns mutate faster than your periodic cross-layer map synchronization interval?"

**Response:** Staleness affects scheduling optimality but cannot violate memory integrity: callbacks enqueue transition requests on driver-owned state machines, which validate each request against current state, and the driver retains eviction authority with FIFO fallback under resource pressure (Section 3.4). Device-local snapshots merge at GPU kernel completions, and policies can trigger explicit synchronization and rate-limit prefetches via PCIe-utilization guards, as the KV-cache policy does; this mitigates but does not eliminate optimality loss under rapid transitions.

## Q10. Does trampoline overhead scale with kernel size? (D)

**D:** "Does the runtime overhead of application-level trampoline hooks scale efficiently when executing massive, complex accelerator kernels characterized by extreme block counts and heavy thread utilization?"

**Response:** Trampoline overhead is per-warp (the warp leader executes the hook and shuffle-broadcasts the result), making it independent of block count; Table 1 shows 3-14% overhead on llama.cpp prefill across three device-side tools of varying complexity (153-347 LOC).

## Q11. How portable is gpubpf, and how intrusive is the implementation? (D, F)

**D:** "the system's host-side implementation remains tightly coupled with explicit hooks in the proprietary GPU driver module"

**D:** "the reliance on dynamic binary instrumentation via ptrace to inject monitoring code directly into running user applications introduces intrusive workarounds"

**F:** "The portability of the proposed mechanism is discussed only briefly"

**Response:** The ptrace attach is a one-time operation (273ms) used only for device-side hook injection; LD_PRELOAD is supported as a non-intrusive alternative for production deployments. Host-side driver hooks require approximately 100 LOC over the open GPL kernel modules, aligned with existing Linux HMM/migrate_vma and DRM scheduler abstractions, making porting to other GPU drivers that expose these interfaces straightforward. Device-side JIT currently targets PTX with a SPIR-V backend path noted in Section 4; porting the SIMT verifier and warp-level execution to non-NVIDIA architectures with different warp widths requires per-architecture engineering work.

## Q12. How would gpubpf extend to CXL memory, storage-tier offloading, and future accelerator design? (A, D, E)

**A:** "It's worth adding some discussion of how this affects the design of future accelerators"

**D:** "Can the proposed asynchronous resource state machine model scale seamlessly into hybrid server environments that incorporate emerging disaggregated memory architectures like tiered CXL memory pools?"

**E:** "How would ebpf handle such use case?" [KV-cache offload to storage]

**Response:** CXL disaggregated memory adds tier states and transitions atop HMM/migrate_vma; the asynchronous model is a natural fit for CXL's higher latencies. A storage tier similarly extends the state machine with millisecond-scale transfers, where gpubpf supplies cross-tier placement policy complementary to transport solutions such as Weka, VAST, and CMX. For future accelerator design, verified state-transitions could serve as the abstraction hardware exposes natively through architected attach points and firmware-validated transition tables. Agent prompts and interaction logs will be released as publicly available artifacts.
