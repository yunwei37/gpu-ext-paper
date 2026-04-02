# OSDI '26 Submission #32 — Reviews and Assessment

**Status: Rejected**
**Scores: A=3 (Weak Accept), B=2 (Weak Reject), C=3 (Weak Accept), D=3 (Weak Accept)**

---

## Review #32A

**Overall merit: 3. Weak accept**
**Submission length: X. The submission length is good**

### Paper summary

gBPF implements eBPF for GPU resource management, providing a cross-layer policy runtime spanning host driver and device execution. The system hooks the GPU driver to expose a limited policy interface, augments the eBPF verifier to check for SIMT semantics to avoid deadlocks or divergence, and manages eBPF maps across the host and GPU memory hierarchies using eventual consistency. Evaluation shows that gBPF policies range from tens to hundreds of lines of code, can react to workload dynamics, and improve performance significantly across diverse workloads.

### Strengths

gBPF provides an interesting mechanism to extend dynamic, fine-grained GPU control using the familiar eBPF interface. The cross-layer architecture spanning host driver and GPU device is novel compared to prior host-only or device-only approaches.

The SIMT-aware verifier and the gBPF policy interface are interesting and well-designed. The distinction between warp-uniform and lane-varying values addresses a fundamental semantic mismatch between CPU eBPF and GPU execution models.

Reasonable performance results across microbenchmarks and realistic workloads.

### Weaknesses

Evaluation of expressiveness can be significantly strengthened. While Table 1 lists 14 policies, critical questions remain:

Coverage analysis: The paper should systematically survey recent GPU resource management papers and explicitly discuss which policies can or cannot be expressed in gBPF and why. This would provide concrete evidence of gBPF's expressiveness.
Policy composability: How do policies interact when composed? The multi-tenant benchmarks combine multiple primitives, but there is no discussion of composition semantics or potential conflicts.
Complexity distribution: Some policies require approximately 900 lines of low-level code (preemption control in Table 1). Is this complexity inherent to the policy or a limitation of the interface? A breakdown of where complexity arises would be helpful.
Missing use cases: Are there important GPU management tasks that gBPF cannot express? For instance, can it handle fine-grained VRAM defragmentation or cross-GPU coordination in multi-GPU systems?
The hierarchical gBPF maps use eventual consistency, but the implications are insufficiently analyzed.

Staleness quantification: What is the typical staleness window?
Policy sensitivity: Which policies are sensitive to stale data?
Failure modes: Under what conditions might staleness cause performance degradation or incorrect decisions?

### Comments for authors

Thank you for submitting to OSDI 2026. I enjoyed reading your paper and learning how gBPF extends eBPF to GPU resource management. The core idea of providing a cross-layer policy interface spanning host driver and GPU device execution is compelling, and the technical contributions, particularly the SIMT-aware verifier and hierarchical map design, are interesting and useful. The evaluation demonstrates good performance gains across diverse workloads. However, I have several concerns about the depth of expressiveness analysis and the implications of eventual consistency that should be addressed to strengthen the paper.

### Detailed comments

#### A1. Page #1 (Introduction)

> GPU profiling frameworks [22, 40, 54, 59] enable kernel-level observation but lack runtime programmability and driver integration, limiting adaptive resource management.

Perhaps eGPU [59] is worth spending another sentence: while it's primarily for observability, what prevented it from being used to program the policies?

**Assessment: ADDRESSED.** S3.4 explicitly states eGPU is "limited to read-only observability with high overhead." Eval (S6.4) adds: "We do not compare policy-level performance against eGPU or Neutrino because they are limited to read-only observability." The microbenchmark (Fig 12a) provides a quantitative overhead comparison (60-80% reduction vs eGPU-style injection).

---

#### A2. Page #2 (Introduction)

> gBPF-based policies improve throughput by up to 4.8x and reduce tail latency by up to 2x compared to static heuristics

Impressive performance gains. I'm curious about the effort of writing gBPF policies and getting them past the verifier.

**Assessment: PARTIALLY ADDRESSED.** RQ2 reports AI agent effort: 59 policies, 974 benchmark runs, 244 code edits, 5.5M tokens, $388. But human effort to write policies is not discussed. Table 1 shows LOC (16-925 lines) but doesn't contextualize difficulty. Verifier experience (13 accepted, 5 correctly rejected from 18 test programs) is mentioned in S6.4 but not from a developer-friction perspective.

---

#### A3. Page #3 (GPU Systems Architecture)

> Second, user-space runtimes lack global visibility and coordination across multi-tenant, multi-framework environments.

Is it typical to have many tenants and runtimes for GPU servers? In the case of training foundation models, for example, the setup is typically one training job across many dedicated GPU servers.

**Assessment: NOT ADDRESSED.** The paper does not discuss when multi-tenancy is typical vs. atypical. The eval includes multi-tenant scenarios (S6.3) but doesn't justify their real-world prevalence or cite deployment surveys.

---

#### A4. Page #3 (Limitations of Existing Extensibility Mechanisms)

> Despite improved performance, these approaches embed static policies requiring kernel modifications, restricting dynamic adaptation and safe deployment of new policies.

Once such a framework is in place, how hard is it to make it extensible? That is, to provide an interface for the user space to download policies?

**Assessment: NOT ADDRESSED.** The paper doesn't discuss why existing kernel-level systems (TimeGraph, Gdev, GPREEMPT) couldn't simply add a policy-download interface. This is a key concern from Reviewer B as well.

---

#### A5. Page #5 (Memory Interface)

> such as 2MB physical UVM chunks or VA blocks, and finer-grained 4KB pages

How do callers select the right chunk sizes?

**Assessment: PARTIALLY ADDRESSED.** S5.2 states: "eviction hooks operate at 2MB block granularity, while prefetch hooks operate at page granularity, can prefetch as many pages as needed." These are fixed by the driver, not caller-selected. The paper could be clearer that granularity is determined by the hook type, not by the policy author.

---

#### A6. Page #5 (Memory Interface)

"and then trigger hostside prefetch handlers" -- Unclear how the GPU prefetch routine can trigger the host-side prefetch handler.

**Assessment: PARTIALLY ADDRESSED.** S4.1 mentions "device-side L2 prefetch triggers host callback for extended prefetch" and S5.3 says device-side hooks "issue policy hints to the host driver via cross-layer maps." But the exact mechanism (non-blocking page fault from L2 prefetch instruction triggers host fault handler where BPF runs) is not spelled out clearly in one place.

---

#### A7. Page #5 (Memory Interface)

> The runtime manages hierarchical logical eBPF map abstractions whose backing storage is automatically partitioned and replicated across host and device with consistency

It would be helpful to use one sentence or to briefly explain how you synchronize the maps across the hierarchies and across host and GPU memory.

**Assessment: ADDRESSED.** S4.3.3 explains: "our runtime periodically merges GPU-local map shards into canonical snapshots at synchronization points, such as GPU kernel completion boundaries." S5.3 adds: "A runtime daemon asynchronously flushes GPU-local shards to host-visible canonical map instances." The mechanism is now described.

---

#### A8. Page #5 (Memory Interface)

"gBPF injects trampolines at hook points" -- Are these hook points pre-determined? Or can these be inserted anywhere as long as they are at warp granularity?

**Assessment: PARTIALLY ADDRESSED.** S5.3 says hooks are at "memory instructions, GPU kernel function boundaries, and tracepoints" via dynamic CUDA API interception and PTX rewriting. These are structured locations, not arbitrary insertion points. But the paper doesn't explicitly state this constraint.

---

#### A9. Page #6 (SIMT-aware Verification)

> These constraints ensure safe policy integration that respects GPU hardware execution semantics

Does your verifier also check for memory safety? Also, how is termination handled? On the host side, the eBPF runtime has an instruction limit. Do you have something similar on the GPU side?

**Assessment: ADDRESSED.** S5.3: "We reuse Linux's eBPF verifier to enforce standard memory safety, bounded loops, and type correctness." And: "Each hook type carries resource budgets limiting instructions, helper invocations, and memory operations."

---

#### A10. Page #7 (Hierarchical Cross-layer Maps for State Coordination)

"Following eBPF's soft-state philosophy, gBPF maps provide relaxed, eventual consistency" -- Will stale values in the maps cause any consistency issues, like incorrect scheduling decisions or memory evictions?

**Assessment: PARTIALLY ADDRESSED.** S4.3.3 states: "Occasional staleness affects decision optimality but cannot violate correctness invariants such as memory integrity, which remain enforced by the GPU driver and hardware MMU." This is the right answer but lacks specificity -- no concrete examples of how staleness manifests or what the worst-case policy degradation looks like.

---

#### A11. Page #8 (Methodology and Setup)

"We evaluate gBPF on two machines" -- Why no H200 GPU evaluation?

**Assessment: NOT ADDRESSED.** The paper uses RTX 5090 and P40. No explanation for the absence of datacenter GPUs (H100/H200/A100).

---

#### A12. Page #8 (Microbenchmarks)

> We evaluate hostdevice prefetch coordination using a modified vector-add GPU kernel [41] with stride access pattern and 40GB working set (1.25x oversubscription)

This microbenchmark feels quite contrived. Have you tried to vary the % of oversubscription and the stride sizes?

**Assessment: PARTIALLY ADDRESSED.** The microbenchmark only shows 1.25x. However, the real workloads vary oversubscription: llama.cpp 1.84x, GNN 1.34-2.17x, FAISS 1.5x. But the microbenchmark itself is not parameterized, which is the reviewer's specific ask.

---

#### A13. Page #10 (Case Studies)

"K-means iterations produce sequential scans that gBPF detects" -- How does gBPF detect sequential scan pattern? Is it programmed by developers, or is it automatic detection? If automatic detection, how accuracy is it?

**Assessment: PARTIALLY ADDRESSED.** The FAISS eval describes a "momentum-based phase detector" that is programmed in BPF by the agent, not automatic. The paper should clarify that pattern detection is policy-authored logic, not a built-in gBPF feature.

---

#### A14. Page #11 (RQ3: Programmability and Mechanism Overhead)

> Table 1 shows policy building blocks with lines of code and execution domain

Some policies need several hundreds lines of code to implement. Given that these are pretty low-level, they don't seem that easy to program?

**Assessment: PARTIALLY ADDRESSED.** The agent story (all 59 policies AI-generated) implicitly answers "agents write them," but the paper doesn't discuss human writability. No breakdown of where complexity arises in 925-LOC preemption control (boilerplate vs logic vs state management).

---

### Summary of 32A concerns

| # | Concern | Status |
|---|---------|--------|
| W1 | Coverage analysis / expressiveness survey | NOT ADDRESSED |
| W2 | Policy composability semantics | PARTIALLY |
| W3 | Complexity distribution (900 LOC breakdown) | NOT ADDRESSED |
| W4 | Missing use cases (defrag, multi-GPU) | NOT ADDRESSED |
| W5 | Staleness quantification | NOT ADDRESSED |
| W6 | Policy sensitivity to stale data | NOT ADDRESSED |
| W7 | Staleness failure modes | PARTIALLY |
| A1 | eGPU differentiation | ADDRESSED |
| A2 | Effort of writing policies | PARTIALLY |
| A3 | Multi-tenant prevalence | NOT ADDRESSED |
| A4 | Making existing frameworks extensible | NOT ADDRESSED |
| A5 | Chunk size selection | PARTIALLY |
| A6 | GPU-to-host prefetch trigger mechanism | PARTIALLY |
| A7 | Map synchronization explanation | ADDRESSED |
| A8 | Hook points pre-determined or arbitrary | PARTIALLY |
| A9 | Memory safety + termination on device | ADDRESSED |
| A10 | Stale maps causing issues | PARTIALLY |
| A11 | Why no H200 | NOT ADDRESSED |
| A12 | Vary oversubscription/stride in microbench | PARTIALLY |
| A13 | Sequential scan detection mechanism | PARTIALLY |
| A14 | Policies not easy to program | PARTIALLY |

---

## Review #32B

**Overall merit: 2. Weak reject**
**Submission length: X. The submission length is good**

### Paper summary

This paper presents gBPF, an eBPF-based runtime for GPU resource management that injects programmable hooks into kernel drivers and GPU device code to address memory placement, scheduling, and observability.

### Comments for authors

This paper presents gBPF, an eBPF-based runtime for GPU resource management that injects programmable hooks into kernel drivers and GPU device code to address memory placement, scheduling, and observability. The paper identifies practical challenges in GPU resource management including memory placement inefficiencies and scheduling imbalances and the evaluation covers realistic scenarios including MoE-based LLM inference, GNN training, and vector search.

However, the contribution remains primarily at the engineering integration level without fundamental advances in system capabilities.

#### B1. Limited systems contribution

Limited systems contribution: Prior systems (TimeGraph, Gdev, GPREEMPT) have demonstrated driver-level resource control without eBPF bytecode layers. Therefore, the central claim that GPU drivers should serve as extensible OS policy interfaces is not novel as this capability has existed through loadable kernel modules for decades. The purported advantages of eBPF do not translate effectively to the GPU driver context given the invasive modifications required to the NVIDIA driver stack. Unlike CPU eBPF programs that load into unmodified kernels, gBPF requires a custom-modified driver, negating the claimed benefit of runtime deployment without kernel changes.

**Assessment: PARTIALLY ADDRESSED.** The paper argues its contribution is the execution model (programmable effects on lifecycles) + SIMT-aware verification + cross-layer maps, not just "eBPF in GPU driver." The agent story (59 policies, zero panics, seconds-to-recover) demonstrates practical safety that LKMs don't provide. S5.1 says the driver change is ~100 LOC of instrumentation -- analogous to how sched_ext required kernel patches before being mainlined. But the paper does NOT make the sched_ext analogy explicitly, and does NOT directly argue why LKM-based extensibility is insufficient beyond "fragile" and "unsafe."

**Key gap:** The paper needs a sharper argument for why eBPF verification matters for GPU drivers specifically. The agent story is the best evidence (buggy policies recovered in seconds vs kernel panics with LKMs) but is buried in RQ2 rather than foregrounded.

---

#### B2. Unjustified cross-layer complexity

Unjustified cross-layer complexity. The cross-layer design introduces unnecessary architectural complexity. The SIMT-aware verifier and warp-level execution models exist solely to work around the fundamental mismatch between eBPF's scalar semantics and GPU SIMT parallelism. Rather than providing a clean abstraction, these mechanisms constrain developers to specific coding patterns while adding verification and compilation overhead.

**Assessment: PARTIALLY ADDRESSED.** The paper frames SIMT-aware verification as a contribution, not a workaround. S4.2 argues it "ensures safe policy integration that respects GPU hardware execution semantics." The warp-level optimization (S4.2.2) reduces overhead by 60-80% vs naive injection (Fig 12a). But the paper doesn't directly counter the "unnecessary complexity" framing -- it doesn't argue why a simpler alternative wouldn't work.

---

#### B3. Evaluation methodology flaws

The evaluation methodology has significant flaws. The reported 4.8x speedup for MoE inference (Section 6.2.2) compares against naive framework-level CPU offloading (llama.cpp's ncmoe parameter) and unoptimized UVM, rather than optimized kernel-level memory management systems such as GPREEMPT (ATC'25) or LithOS (SOSP'23). While the paper mentions that GPREEMPT-style scheduler policies are ineffective on memory-bound workloads, it provides no head-to-head performance data against these systems under identical experimental conditions. Without comparison against these stronger baselines, it remains unclear whether the performance gains stem from the eBPF-based approach or simply from implementing reasonable memory management policies that could equally be realized through conventional kernel modifications.

**Assessment: PARTIALLY ADDRESSED.** The paper now includes:
- 1.76x over application-tuned `cudaMemAdvise` (a stronger baseline than ncmoe)
- vLLM comparison against LMCache (state-of-the-art KV-cache offloading framework)
- S6.3.1 shows GPREEMPT-style scheduler policies are <1% effective on memory-bound workloads
- Multi-tenant microbench explicitly compares scheduler-only (GPREEMPT-style) vs memory policies

**Key gap:** No head-to-head comparison against GPREEMPT or LithOS running on the same hardware with the same workloads. The paper argues these systems solve different problems (scheduling vs memory) but doesn't demonstrate this with identical experimental setups. The 4.8x headline number is still against framework offloading, not against the strongest kernel-level baseline.

---

### Summary of 32B concerns

| # | Concern | Status | Risk |
|---|---------|--------|------|
| B1 | Engineering-only, no fundamental advance; LKMs already do this | PARTIALLY | **HIGH** -- core rejection reason |
| B2 | Cross-layer complexity unjustified, SIMT verifier is a workaround | PARTIALLY | MEDIUM |
| B3 | 4.8x against naive baselines, no GPREEMPT/LithOS head-to-head | PARTIALLY | **HIGH** -- core rejection reason |

**This is the most dangerous review.** The reviewer's position is that the contribution is engineering integration, and the eval doesn't prove the approach is better than conventional kernel modifications. Addressing B1 and B3 is critical for resubmission.

---

## Review #32C

**Overall merit: 3. Weak accept**
**Submission length: Z. The submission is too short to understand**

### Paper summary

In this paper the authors present an eBPF-based scheduling/memory management policy and observability framework for GPU workloads. The user can hook at various points of the aforementioned subsystems in the host OS kernel and in the code executed on the device, and inject eBPF programs implementing policy or observation code. The evaluation demonstrates various case studies in GPU single/multi-tenant environments, improving performance/fairness, and reducing overheads vs. baselines and competitors.

Strengths:

Timely context, important problem tackled
The proposed designed seems to achieve its objectives, and the numbers in evaluation look good
Weaknesses:

Motivation could be stronger
Paper can be hard to read for non-experts

### Comments for authors

Thank you for submitting this paper to the conference. It is clear that it tackles an important problem, that of writing easily-programmable and robust memory management/scheduling policies or observation tools for GPU workloads. GPU computations being what they are today, the context is also obviously very timely. The numbers in evaluation look good, and it seems that gBPF achieves its objectives.

#### C1. Motivation proof

There is an extensive amount of discussion about the motivation for the work, but very little proof to back up the claims made. Figure 1 and 2 are not discussed at all (we don't even know what workload the numbers in Figure 2 correspond to), so I don't really know what to make of them. In the discussion there is very little references to the issues mentioned, and most of the citations relate to existing GPU computation runtimes/libraries, policy enforcement or observation tools.

**Assessment: PARTIALLY ADDRESSED.** Figure 1 caption now identifies workloads: "faiss Build... faiss Query... llama.cpp MoE Prefill... Decode... PyTorch DNN." Figure 2 caption says "GPU thread scheduling imbalance observed via eBPF tracing" with SM load distribution. But body text integration is still weak -- the figures are not deeply discussed in the motivation section text. The citation "73%" from [park2025helm, kehne2019etc, ganguly2019interplay] provides quantitative backing for policy sensitivity.

---

#### C2. Challenges and design connection

Beyond the aforementioned issue, as a non-expert I found the paper quite difficult to read. Some key aspects of the work that in my opinion require clarification are:

Challenges and how they are addressed by the design: without further clarification I don't understand C2. The design should also probably refer back to C1-C3 to explain how they are addressed concretely.

**Assessment: ADDRESSED.** S4 now opens with: "As identified in S3.4, achieving these goals requires addressing three GPU-specific challenges... (1) cross-device latency... (2) memory-scheduling coupling... (3) fragmented visibility..." Each design subsection connects back to these challenges. S4.1 explicitly explains how the lifecycle model addresses cross-device latency (asynchronous effects) and memory-scheduling coupling (unified interface).

---

#### C3. Host and device policy hooks detail

Host and device policy hooks: this is a central part of the approach, we need more than a few words to clarify what each hook corresponds to and how it can be used to implement policy/observability tools. Also, please define the events mentioned at the beginning of 4.3.1.

**Assessment: PARTIALLY ADDRESSED.** S4.1 defines three program types (GPU_MEM, GPU_SCHED, GPU_DEV) with their events (activate, access, evict_prepare, prefetch for memory; task_init, task_destroy for scheduling). The MoE code example (Listing 1) shows concrete hook usage. S5.2-5.3 provides implementation detail. But a consolidated table of all hooks with their context fields and return semantics is missing.

---

#### C4. Security

Security: I understand that the eBPF code injected can be faulty but is not fully malicious? Any concrete examples (ideally with a reference) of the eBPF code being "buggy or misconfigured"? What is exactly the additional attack surface opened by gBPF on top of traditional eBPF?

**Assessment: ADDRESSED.** S4.2 states the threat model: "we trust system administrators loading policies, but consider policy code potentially buggy or misconfigured." RQ2 provides concrete numbers: "50 safety-relevant events (24 logic bugs, 18 performance regressions, 2 verifier rejections, 2 GPU memory faults, and 4 other events) with zero kernel panics or data corruption." The paper does not discuss additional attack surface beyond traditional eBPF, which is a minor gap.

---

#### C5. Policies in Table 1 underdeveloped; any dynamic?

The paper should also develop on the policies (Table 1) developed with the framework, nothing much is said about these at the moment. Also, the paper insist that existing work are limited to static policies, are any of the policy presented in Table 1 dynamic? What about evaluation vs. a static policy?

**Assessment: PARTIALLY ADDRESSED.** The FAISS case study describes a dynamic phase-adaptive policy. The eval compares against static defaults (LRU, FIFO). But Table 1 itself has minimal descriptions -- just tags and LOC. No column indicating static vs dynamic. The eval doesn't have a controlled experiment of "same policy logic, static vs dynamic."

---

#### C6. Competitor justification

The choice of competitors in 6.1 should be justified.

**Assessment: NOT ADDRESSED.** S6.1 lists baselines (default UVM, hints, framework offloading) but doesn't justify why these are the right comparisons or why others (GPREEMPT, LithOS, etc.) are excluded.

---

#### C7. "Naively extending eBPF" meaning

The paper should develop on what "naively extending eBPF" means concretely. Do the authors mean simply using traditional eBPF only in the OS kernel?

**Assessment: ADDRESSED.** S3.4 explains three specific mismatches: cross-device latency (synchronous callbacks too slow), memory-scheduling coupling (independent subsystems don't work), fragmented visibility (CPU eBPF can't see GPU-internal state). This makes "naive" = using CPU eBPF patterns without these adaptations.

---

#### C8. "1.34x speedup" vs what?

6.2.1 "1.34x speedup" vs. what?

**Assessment: ADDRESSED.** Microbench text states: "With device-only prefetch and default host prefetch at thread entry, we achieve 1.34x speedup" -- baseline is default (no eBPF) UVM behavior.

---

#### C9. Undefined acronyms

There are many acronyms used without being defined

**Assessment: PROBABLY NOT FULLY ADDRESSED.** S2.2 partially defines kfunc ("approved kernel functions (helper or kfuncs)"). SM (Streaming Multiprocessor) is used without definition. TSG (Time-Slice Group) is introduced in S5.2 but may not be defined at first use. UVM is defined in S2.1. SIMT is defined in S2.1.

---

#### C10. "kernel" ambiguity

The word "kernel" may lead to confusion in the context targeted by the paper, possibly differentiate "OS kernel" from "GPU kernel"

**Assessment: PROBABLY NOT FULLY ADDRESSED.** The paper uses "GPU kernels" and "kernel driver" but some sentences remain ambiguous (e.g., "kernel-level approaches provide control but embed policy logic into privileged drivers" -- does "kernel-level" mean OS kernel or GPU kernel?). Not systematically audited.

---

#### C11. Small font on figures

The font size on several figures is too small

**Assessment: UNKNOWN.** Cannot verify from LaTeX source alone. Figures are included as PDF images.

---

#### C12. What is a kfunc?

What is a kfunc?

**Assessment: PARTIALLY ADDRESSED.** S2.2: "approved kernel functions (helper or kfuncs)." A kfunc is a kernel function callable from eBPF programs, but the paper doesn't explicitly define the term or distinguish kfuncs from helpers.

---

#### C13. Figure 7 "eBPF" should be gBPF?

Figure 7 "eBPF" gBPF? Same remark for the text in the paper commenting this graph.

**Assessment: UNKNOWN.** Cannot verify figure content from LaTeX source.

---

#### C14. AMD/Intel portability -- code reuse

The implementation looks like a nice amount of engineering work. The paper claims that the approach is generic and could be applied to AMD GPUs too, how much of the LoC developed for Nvidia can be reused for AMD? What about Intel GPUs?

**Assessment: PARTIALLY ADDRESSED.** S7 (Portability) discusses: SPIR-V for device-side portability, HMM/migrate_vma for host memory (AMD ROCm already uses this), DRM scheduler for scheduling abstraction. But says "End-to-end portability requires vendor-specific runtime support and hardware tuning, which remain future work." No quantification of reusable LOC.

---

### Summary of 32C concerns

| # | Concern | Status |
|---|---------|--------|
| C1 | Fig 1&2 undiscussed, motivation lacks proof | PARTIALLY |
| C2 | C1-C3 challenges not connected to design | ADDRESSED |
| C3 | Hooks need more detail | PARTIALLY |
| C4 | Security: concrete buggy examples? Attack surface? | ADDRESSED |
| C5 | Table 1 underdeveloped; static vs dynamic? | PARTIALLY |
| C6 | Competitor choice justification | NOT ADDRESSED |
| C7 | "Naively extending eBPF" meaning | ADDRESSED |
| C8 | "1.34x speedup" baseline | ADDRESSED |
| C9 | Undefined acronyms | PROBABLY NOT FIXED |
| C10 | "kernel" ambiguity | PROBABLY NOT FIXED |
| C11 | Small font on figures | UNKNOWN |
| C12 | What is a kfunc? | PARTIALLY |
| C13 | Figure label eBPF vs gBPF | UNKNOWN |
| C14 | AMD/Intel code reuse quantification | PARTIALLY |

---

## Review #32D

**Overall merit: 3. Weak accept**
**Submission length: X. The submission length is good**

### Paper summary

gBPF uses BPF-style hooks to provide control over the execution of GPU kernels, focusing particularly on control over thread-block scheduling and on the placement and movement of pages between host memory and device memory. The implementation allows transparent use via PTX re-writing, coupled with verification that the injected code will not cause divergence or other potential issues. The system is evaluated on a range of workloads including LLM inference, GCN training, and synthetic examples

### Comments for authors

Strengths:

The paper provides good extensions beyond prior work on using BPF to instrument GPU code -- particularly eGPU which targeted more limited observability workloads, and had a simpler implementation with higher costs from synchronization

This could be described in much more depth, but I found the range of policies interesting. Each of the larger examples in the evaluation was using a different policy, helping provide some illustration that gBPF is reasonably general-purpose, and that a single better default is insufficient. If accepted, I hope that more space can be devoted to concrete examples -- the current text often includes "eBPF applies..." when really this is a choice from the policy

#### D1. Overhead depth

Weaknesses:

More depth is needed in the analysis of overheads. Fig 12 shows some isolated costs, but I was hoping to see a simple measurement of the increase in resource use -- registers, flops, shared memory -- when instrumenting an already-optimized workload (say, a cutlass GEMM).
That will show how much of a benefit is required in order to pay for the costs.

**Assessment: NOT ADDRESSED.** The paper shows percentage throughput degradation (Table 3: 3-14% for device-side tools) and hook-enabled overhead (<0.2%). But no register count, FLOP overhead, or shared memory consumption increase is reported for real workloads. The microbenchmark (Fig 12) uses a toy vector-add, not an optimized kernel.

---

#### D2. Persistent thread-block dispatch generality

How general is the introduction of the persistent thread-block dispatch layer? Does this limit each SM to running a single block, or can the system handle dispatch to blocks that might have different resource needs?

**Assessment: NOT ADDRESSED.** S5.3 mentions "persistent GPU workers as long-lived kernels that poll and claim logical work units" and "cluster launch control APIs" on Blackwell, but doesn't discuss SM occupancy constraints or whether blocks with heterogeneous resource requirements can coexist.

---

#### D3. Concrete policy examples; be specific about scope

It would be great to provide some concrete examples of the kinds of policy that can be implemented. I found early sections of the paper quite ambiguous and lacking in precision -- I'd suggest making things more concrete by being specific that scheduling is in terms of thread-block dispatch, and that memory control is on page movement via UVM.

**Assessment: PARTIALLY ADDRESSED.** S4.1.2 provides a concrete MoE code example with three cooperating BPF programs. S4.1 specifies "2MB UVM chunks or VA blocks, and finer-grained 4KB pages." But the intro and design sections still use abstract language ("resource lifecycles," "transitions") before grounding in specifics. The scope (UVM page movement, TSG scheduling, thread-block dispatch) could be stated upfront.

---

#### D4. Oversubscription-only focus

The choice to focus on over-subscribed workloads could be made clearer up front. The paper has a good set of examples workloads, but these are generally either running multiple jobs on a single GPU (without clear justification for why to run them together), or running a large job on a memory-constrained GPU. It would be great to highlight were there are cases that improved policies can optimize a job that is already performing well, rather than mitigating thrashing

**Assessment: NOT ADDRESSED.** All single-tenant experiments are oversubscribed (1.25-2.17x). The multi-tenant experiments create artificial contention. No experiment shows gBPF improving a workload that fits in GPU memory and runs at near-optimal performance. The paper doesn't justify why oversubscription is the right focus or acknowledge this limitation.

---

#### D5. Memory isolation in multi-tenant

I was unclear if the multi-tenant workloads include memory isolation; perhaps I missed this, but it should be stated explicitly given the range of options seen for sharing Nvidia GPUs

**Assessment: PARTIALLY ADDRESSED.** S4.1 states: "a single administrator-defined policy governs all tenants, as with sched_ext; per-tenant policy isolation is future work." Multi-tenant experiments use UVM's default address space sharing. But the paper doesn't discuss MIG or other isolation mechanisms and their interaction with gBPF.

---

#### D6. "Prefetching with adaptive aggressiveness" policy detail

The example of "prefetching with adaptive aggressiveness based on PCIe utilization and memory region" is one illustration of a case where I'd like to understand the policy definition better

**Assessment: PARTIALLY ADDRESSED.** vLLM eval section describes: "adaptive aggressiveness based on PCIe utilization and memory region (stride-based for weights, sequential for KV-cache), with LFU eviction." But no pseudocode or quantitative thresholds for "adaptive aggressiveness" are provided.

---

#### D7. Figure font sizes

Labels on graph axes etc need to be much larger (the paper should be readable on a regular size screen without zooming)

**Assessment: UNKNOWN.** Cannot verify from LaTeX source.

---

#### D8. "Trampolines at execution phase boundaries" -- how identified?

p7 refers to adding "trampolines" at "execution phase boundaries", I was curious how these are identified

**Assessment: PARTIALLY ADDRESSED.** S5.3: "dynamically intercepting CUDA runtime APIs to extract GPU kernel PTX, rewrite it with binary trampolines, and load instrumented kernels back without recompilation or application restart." Hook points are at "memory instructions, GPU kernel function boundaries, and tracepoints." The "execution phase boundaries" are operationally GPU kernel launch/completion events detected via CUDA API interception, but this isn't stated explicitly.

---

#### D9. "Under moderate imbalance" -- should be optimized?

p8 the description of the single-tenant GEMM benchmark refers to "under moderate imbalance" -- I would expect this to be an optimized regular workload

**Assessment: PARTIALLY ADDRESSED.** The benchmark deliberately creates imbalance to demonstrate scheduling policy value. The paper says "FixedWork (static block assignment, no scheduler)" is the baseline. This is a synthetic scenario, and the paper doesn't test on optimized GEMM (e.g., CUTLASS) where imbalance is minimal. Related to D1 and D4.

---

#### D10. "Warps of 32" is NVIDIA-specific

p4 "GPU kernels execute in warps of 32 threads" -- this is specific to Nvidia

**Assessment: NOT ADDRESSED.** S3.4 still states this as a general GPU fact. Should qualify as NVIDIA-specific (AMD wavefronts are 32 or 64 threads).

---

#### D11. Fig 1 context

Fig 1 -- the context that eBPF is being used to optimize page movement in UVM would help appreciate the significance here (as opposed, say, to thinking about placement of data in different HBM stacks)

**Assessment: PARTIALLY ADDRESSED.** Fig 1 caption says "Memory access (page fault) patterns" which implies UVM context, but doesn't explicitly state this is about host-device page migration under UVM oversubscription.

---

#### D12. Fig 2 -- imbalance doesn't prove balance helps

Fig 2 -- this shows imbalance in some metrics, but does not in itself show that achieving balance would improve performance. For instance, perhaps SM0 is running a kernel with less use of registers and shared memory than the other SMs

**Assessment: ADDRESSED.** The CLC microbenchmark (S6.2.1, Fig 8) demonstrates that policies addressing imbalance reduce latency by ~11%. This provides the missing evidence that balance matters.

---

#### D13. "Deadlock risks" -- actual deadlock?

p4, "deadlock risks from thousands of concurrent memory operations", clearly this can be very slow, but does the implementation actually deadlock?

**Assessment: PARTIALLY ADDRESSED.** S3.4 mentions "deadlock risks" in the context of naive SIMT eBPF execution (warp divergence from scalar logic). The paper doesn't clarify whether this is a theoretical risk prevented by the verifier or an observed failure mode. The SIMT-aware verifier (S4.2) is designed to prevent this, but no concrete deadlock example is given.

---

#### D14. "GPU kernel" vs "OS kernel" consistency

Suggest being meticulous in always writing "GPU kernel" and "OS kernel" to avoid some ambiguity. e.g. p5 whether "kernel restarts" are needing to reboot a system after a policy update, or a GPU kernel

**Assessment: PROBABLY NOT FULLY ADDRESSED.** The paper uses "kernel driver" and "GPU kernels" in many places, but likely has remaining instances of bare "kernel" that are ambiguous. Not systematically audited.

---

### Summary of 32D concerns

| # | Concern | Status |
|---|---------|--------|
| D1 | Register/FLOP/shared memory overhead on real workloads | NOT ADDRESSED |
| D2 | Persistent thread-block dispatch generality | NOT ADDRESSED |
| D3 | Concrete policy examples; scope specificity | PARTIALLY |
| D4 | Oversubscription-only focus; can policies help well-performing jobs? | NOT ADDRESSED |
| D5 | Memory isolation in multi-tenant | PARTIALLY |
| D6 | "Adaptive aggressiveness" policy detail | PARTIALLY |
| D7 | Figure font sizes | UNKNOWN |
| D8 | Trampoline boundary identification | PARTIALLY |
| D9 | Moderate imbalance benchmark vs optimized workload | PARTIALLY |
| D10 | "Warps of 32" is NVIDIA-specific | NOT ADDRESSED |
| D11 | Fig 1 UVM context | PARTIALLY |
| D12 | Fig 2 doesn't prove balance helps | ADDRESSED |
| D13 | Deadlock: theoretical or actual? | PARTIALLY |
| D14 | "GPU kernel" vs "OS kernel" consistency | PROBABLY NOT FIXED |

---

## Cross-Review Summary

### Most critical unaddressed concerns (resubmission blockers)

1. **Baseline strength (B3):** The 4.8x headline compares against framework offloading. No head-to-head against GPREEMPT/LithOS. The 1.76x over application-tuned hints is stronger but underemphasized.

2. **Systems contribution framing (B1):** "Engineering integration" vs "fundamental advance." The lifecycle model and agent story are good counter-arguments but need to be foregrounded, not buried in RQ2.

3. **Expressiveness survey (A-W1):** No systematic mapping of which recent GPU management policies can/cannot be expressed. This would directly counter B1 and strengthen A.

4. **Staleness analysis (A-W5/W6/W7):** No quantification of map consistency window, no analysis of which policies are sensitive, no failure mode discussion.

5. **Overhead depth (D1):** No register/FLOP/shared memory measurement on real workloads. Reviewers want to know the cost of instrumentation on an already-optimized kernel.

6. **Oversubscription-only focus (D4):** All experiments involve memory pressure. No demonstration of value for workloads that fit in GPU memory.

### Concerns addressed well

- eGPU differentiation (A1): Clear comparison in text and quantitative overhead comparison
- Map synchronization mechanism (A7): Described in S4.3.3 and S5.3
- Memory safety + termination on device (A9): Verifier reuse + resource budgets
- Security with concrete examples (C4): 50 safety events, zero panics
- Challenge-design connection (C2): S4 explicitly references S3.4 challenges
- "Naively extending eBPF" meaning (C7): Three mismatches clearly articulated
- Balance helps performance (D12): CLC microbenchmark provides evidence

### Presentation issues (easy fixes)

- Undefined acronyms: SM, TSG, kfunc (C9, C12)
- "kernel" ambiguity throughout (C10, D14)
- "Warps of 32" should be qualified as NVIDIA-specific (D10)
- Figure font sizes (C11, D7)
- Figure labels: eBPF vs gBPF (C13)
- Competitor choice justification (C6)
- Fig 1 needs explicit UVM context (D11)
