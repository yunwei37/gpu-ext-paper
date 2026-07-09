# Author Response

| Rev | Overall | Confidence / Notes | Key Concerns | Rebuttal Goal |
|---|---|---|---|---|
| A | 4 — Accept (OS-advance: 5) | Deeply engaged; "impressive engineering feat", "exciting future of systems research" | Five clarification questions: adversarial app heuristics; SASS-only binaries; map storage & non-composable data; future-accelerator implications; why P40 only | **Primary champion target**: convert from voter to defender — A is the only supporter with the depth to counter F in discussion |
| B | 3 — Neutral | Confidence 2; admits judging "from the first two pages" | Doubts safety guarantees are possible for a fully asynchronous mechanism | Neutralize with the two-layer safety model; commit to surfacing the invariant in §1 |
| C | 5 — Strong ASPLOS paper | High confidence, but the review is two sentences | None | Score champion; a thin review cannot carry a contested discussion alone — nothing to fix, C supplies the vote, A must supply the defense |
| D | 3 — Weak accept | Thorough, constructive | Proprietary-driver coupling; eventual-consistency staleness/thrashing; single system-wide policy; ptrace intrusiveness; PTX-only portability; Qs on CXL and trampoline scaling | Answer all four questions to solidify the weak accept |
| E | 2 — Leaning reject (OS-advance: 4) | Medium; lists five strengths | Missing SOTA MoE baseline (arXiv:2303.06182); MIG real-world relevance (SemiAnalysis); KV-cache offload to storage; wants agent prompts/details | Move 2→3 via existing evidence + gating-policy commitment + artifact release |
| F | 2 — Leaning reject (OS-advance: 4) | Most substantive negative; "core idea very interesting" | SOTA research baselines; mechanism-vs-policy attribution; safety-evaluation depth (verifier, rejected policies, failure modes, TCB); thin design sections; portability | Convert objections to "fixable in revision" |

**Response:**

Thanks for reviewing our paper! 

## Q1. Why doesn't the evaluation compare against state-of-the-art research systems? (E, F)

We compare gpubpf to standard baselines (e.g., llama.cpp and vllm) as well as two SOTA systems: GPREEMPT [ATC25] (implemented as a gpubpf policy in Section 5.4) and LMCache [Arxiv25] (Section 5.2).  Many systems require unsafe driver modifications (GPREEMPT, TimeGraph, Gdev, GCAPS) and do not provide gpubpf's safety nor its dynamism; their policies could be implemented in gpubpf as in the experiment with GPREEMPT (Section 5.4). Concerning arXiv:2303.06182, the algorithms presented in the work could be expressed as gpubpf policies. 

## Q2. What safety guarantees does gpubpf provide? (F, B)

gpubpf builds safety using two layers.  In the first layer, gpubpf ensures program safety using verification.  It uses the unmodified Linux eBPF verifier to enforce termination, memory safety, and restricted kfuncs, and custom SIMT-aware passes to enforce warp-uniform branches, no global synchronization, nor non-uniform atomics (Section 3.5.1). In the second layer, gpubpf ensures safety through transition validity since callbacks never mutate state directly and the system validates each state change against the current state before applying them (Section 3.4).  gpubpf rejects policies that fail program safety and turns invalid transitions into no ops.  We describe the impact of gpubpf's safety for supporting agent-generated policies, where it prevents 50 safety violations from reaching deployment (Section 5.3).

## Q3. How portable is gpubpf beyond NVIDIA GPUs? (F, D)

gpubpf's design aligns with generic linux abstractions and is not coupled with the NVIDIA implementation. Porting gpubpf to non-NVIDIA kernel drivers should be straightforward, as the NVIDIA driver instrumentation only required ~100 LOC (Section 4).  gpubpf can target SPIR-V to support non-NVIDIA devices; we have a prototype implementation that shows this approach is viable. 


## Q4. How does gpubpf's model extend to storage-tier offloading, CXL memory, and future accelerator design? (A, D, E)

gpubpf's asynchronous state machine model could be extended to support storage-tier offloading, memory tiering, or future accelerator designs.  A storage tier adds new states and transitions where millisecond-scale transfers fit the async model, with gpubpf supplying placement policy complementary to Weka/VAST/CMX transport. CXL memory tiers map to new states atop HMM/migrate_vma, and the async model is a natural fit for CXL's higher latencies. For future accelerators, verified state-transitions could serve as the abstraction hardware exposes natively through architected attach points, firmware-validated transition tables, and privileged telemetry.

## Q5. How does gpubpf handle workload-internal optimization heuristics that conflict with gpubpf's policies? (A)

We encountered a similar issue of thrashing caused by interference between an application (VLLM) and gpubpf policies in the KV-cache agent case study (Section 5.3).  Gpubpf currently employs two mechanisms to alleviate the impact of such a problem.  First, the agent using gpubpf can adapt the gpubpf policy that it employs to address an application's heuristics that conflict with its goals, i.e., the gpubpf policy does not need to be static.  Second, gpubpf builds on the NVIDIA driver, which already provides [online support for detecting and minimizing the impact of certain thrashing issues](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/main/kernel-open/nvidia-uvm/uvm_perf_thrashing.h).  As an example, the NVIDIA driver will disable gpubpf prefetches if they lead to considerable memory thrashing.  


## Q6. How does gpubpf work with workloads shipped as SASS binaries without PTX? (A)

gpubpf host-side policies (memory management, scheduling) do not need PTX as they operate only in the kernel driver.  gpubpf device-side hooks use PTX, but, we have a working prototype of SASS-level patching that uses NVBit's compiler infrastructure.


## Q7. Can the hierarchical BPF map structure support non-composable data for scheduling decisions? (A)

gpubpf maps store data across memory tiers (e.g., host DRAM, GPU global memory, GPU thread-block shared memory) to allow device-side and host-side extensions to share data (Section 3.5.3).  gpubpf device-side extensions usually place data that must be shared with host-side extensions (e.g., profiling data) into GPU global memory, and data that is only accessed by gpu extensions (e.g., intermediate values) into GPU thread-block shared memory.  This design can support both aggregate/composite data and raw data, and we have experimented on both.  For example, the Expert Offloading and KV-Cache Offloading case studies (Section 5.3) both use device-side memory tracing extensions that sample the device's memory accesses and place them into GPU global memory.  We have experimented with other use cases that exploit both GPU thread-block shared memory and GPU global memory, although, we did not include them in the current draft of the paper. 

## Q8. Why was device-side overhead only measured on P40? (A)

Figure 15 (a) shows gpubpf overheads on common device-side operations measured on RTX 5090. In future drafts, we will add experiments on the RTX 5090 when comparing gpubpf to existing device-side observability tools in Table 1.

## Q9. How would per-tenant policy isolation work? (D)

Supporting per-tenant policy isolation in gpubpf would require changes to many components, although the system's high-level asynchronous resource state machine model would remain unchanged.  In particular, per-tenant policy isolation requires per-cgroup policy attachment, gpubpf verifier-enforced map namespacing, per-tenant hook budgets to minimize overhead interference across tenants, and a number of permission issues.  

## Q10. How does the system handle VRAM thrashing when workload patterns change faster than the map sync interval? (D)

This is an interesting challenge, albeit one that we have not observed in practice.  gpubpf allows policies to issue map synchronization operations.  So, a gpubpf policy could alleviate the impact of such thrashing by issuing more frequent synchronization operations when thrashing increases. 

## Q11. Does trampoline overhead scale with kernel size? (D)

gpubpf imposes trampoline overhead on a per warp basis (warp leader executes, shuffle-broadcasts result); it is a constant overhead with respect to block count. 

## Q12. How intrusive is the ptrace-based instrumentation? (D)

In addition to ptrace, the prototype supports LD_PRELOAD, which may be more palatable for security compliance.  The tradeoff is that LD_PRELOAD reduces dynamism as gpubpf cannot modify GPU-device policies while the host application executes when using LD_PRELOAD.

## Q13. Is multi-tenant GPU sharing a real use case? (E)

gpubpf supports custom policies for both multi-tenant (Section 5.4) and single-tenant scenarios (Section 5.3, 5.4).  Academic (e.g., Tally [ASPLOS25], LithOS [OSDI25]) and industrial (e.g., MuxFlow [Arxiv23]) systems use multi-tenant GPU sharing to improve GPU utilization; gpubpf's experiments on multi-tenancy build on this line of work.

## Q14. What was the agent setup for the policy exploration case studies? (E)

We will release prompts and benchmark harnesses as a publicly available artifact.

## Q15. How much of the performance improvement comes from gpubpf itself vs. the specific policies evaluated? (F)

gpubpf provides a safe and dynamic method for writing custom resource management policies; our evaluation shows that the policies that it supports improve performance relative to standard baselines and SOTA approaches (see Q1).  Similar improvements are possible by implementing the evaluated policies (Section 5) in existing frameworks, through driver modifications, or with instrumentation systems, at the cost of lost safety and dynamism.  Additionally, the evaluation shows that gpubpf has lower overhead compared to existing device-side extension tools (Section 5.5).


