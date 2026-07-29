# ASPLOS'27 #1797 Major Revision Plan

**Paper:** Safe and Programmable OS-Level GPU Resource Management with eBPF  
**Decision:** Accept subject to major revision  
**Shepherd:** TBD

---

## Meta Review Requirements

> 1. Please implement all of the changes you have indicated in your author response.
> 2. Please pay particular attention to Q1 and Q2 which are seen as major sticking points for acceptance.
> 3. Please pay attention to Reviewer F's concern with distinguishing between policy improvements and mechanism improvements.

---

## Reviewer Summary

| Rev | Score | Confidence | Status | Goal |
|-----|-------|------------|--------|------|
| A | 4 Accept | 4 | Champion | Satisfy clarifications |
| B | 3 Neutral | 2 | Skeptical on safety | Neutralize with Q2 |
| C | 5 Strong Accept | 3 | Anchor | No action needed |
| D | 3 Weak Accept | 2 | Constructive | Solidify |
| E | 2 Leaning Reject | 3 | Needs conversion | Address all concerns |
| F | 2 Leaning Reject | 3 | Needs conversion | Address all concerns |

---

## Priority 1: Major Sticking Points

### Q1: SOTA Baselines (Rev E, F)

**Problem:** Reviewers want comparison against research systems, not just state-of-practice.

**Rebuttal commitments:**
- Add policy expressibility table
- Clarify why certain comparisons are infeasible

**Changes:**

- [ ] **Section 5 (Evaluation):** Add Table X "Policy Expressibility" mapping each evaluated policy to implementation approach:

| Policy | User-space | Driver Mod | gpubpf | Notes |
|--------|------------|------------|--------|-------|
| MoE prefetch | No (no page-fault hooks) | Yes (unsafe) | Yes | Requires OS-level page-fault interposition |
| KV-cache offload | Partial (framework-specific) | Yes | Yes | Cross-framework coordination impossible in user-space |
| GPREEMPT scheduling | No | Yes (their impl) | Yes | 925 LOC, zero driver-source changes |
| Multi-tenant isolation | No | Yes | Yes | Requires cross-tenant visibility |

- [ ] **Section 5.4:** Expand GPREEMPT comparison paragraph
  - Highlight: implemented as 925-LOC gpubpf program
  - Zero driver-source changes vs original's driver modifications
  - 96% P99 latency reduction (Fig.12)

- [ ] **Section 6 (Related Work):** Add paragraph on driver-modification systems
  - TimeGraph, Gdev, GCAPS, LithOS require unsafe driver modifications
  - Their policies are expressible on gpubpf (demonstrated by GPREEMPT)
  - gpubpf provides safety + dynamism they lack

- [ ] **Section 5.2 or Related Work:** Clarify arXiv:2303.06182 (Meta AI MoE)
  - Framework-level optimization, migrates experts as atomic units
  - Requires runtime integration with specific framework
  - Different abstraction level than gpubpf's transparent page-granularity
  - Algorithms could be expressed as gpubpf policies

### Q2: Safety Guarantees (Rev B, F)

**Problem:** Safety claims need deeper technical evidence.

**Rebuttal commitments:**
- Expand Sections 3.4 and 4
- Add transition-validation pseudocode
- Add SIMT-verifier algorithm
- Add verifier-rejection examples
- Add failure-mode taxonomy

**Changes:**

- [ ] **Section 3.4 (Async Execution Model):** Add Algorithm 1 "Transition Validation"
  ```
  function VALIDATE_TRANSITION(page, requested_state):
    current = page.state
    if not VALID_EDGE(current, requested_state):
      return NO_OP  // Invalid transition becomes no-op
    if page.version != request.version:
      return NO_OP  // Stale request
    APPLY_TRANSITION(page, requested_state)
  ```

- [ ] **Section 3.5.1 (SIMT Verifier):** Add Algorithm 2 "SIMT Safety Verification"
  - Step 1: Run unmodified Linux eBPF verifier (termination, memory safety, restricted kfuncs)
  - Step 2: SIMT-aware passes:
    - Reject lane-varying branches (control flow must be warp-uniform)
    - Reject unbounded loops
    - Reject non-uniform atomics
  - Step 3: Verify map access patterns

- [ ] **Section 3.5.1:** Add concrete rejection examples
  - Example 1: Lane-varying branch `if (threadIdx.x % 2) { ... }` → REJECTED
  - Example 2: Unbounded eviction-list loop → REJECTED
  - Example 3: Non-uniform atomic on shared variable → REJECTED

- [ ] **Section 3.5 or 4:** Add "Trusted Computing Base" paragraph
  - TCB components: OS kernel, gpubpf driver module (~100 LOC hooks), GPU compiler backend, GPU firmware
  - What each component is trusted for

- [ ] **Section 3.4:** Add "Failure Mode Taxonomy" 
  - Program safety violation → Verifier rejection (pre-deployment)
  - Invalid transition → No-op (runtime)
  - Stale state → No-op (runtime)
  - Thrashing detection → Driver disables prefetches (runtime)

- [ ] **Section 5.3 (Agent Studies):** Add empirical safety statistics
  - 59 agent-generated policies
  - 974 total runs
  - 50 safety events caught
  - 2 verifier-rejected policies (lane-varying branches, unbounded loops)
  - 0 kernel panics
  - 0 data corruption

---

## Priority 2: Mechanism vs Policy Attribution (Rev F)

**Problem:** Unclear what benefits come from gpubpf mechanism vs specific policies.

**Changes:**

- [ ] **Section 5.2 or 5.3:** Add explicit interpretation of Fig.13
  - GPREEMPT-style scheduling alone: <1% improvement on memory-bound workloads
  - gpubpf memory policies: 55-92% improvement
  - Conclusion: memory management policies (requiring OS-level hooks) drive most gains

- [ ] **Section 5:** Add paragraph after policy expressibility table
  - Policies in table *could* be implemented via driver modifications
  - Trade-off: lose safety (kernel panics possible) and dynamism (restarts required)
  - gpubpf's contribution: enables these policies safely and dynamically

- [ ] **Abstract or Intro:** Ensure framing separates mechanism from policy
  - Mechanism contribution: safe, dynamic, full-stack policy interface
  - Policy contribution: demonstrate interface enables high-performance policies

---

## Priority 3: Reviewer-Specific Concerns

### Rev A (Champion - maintain support)

- [ ] **Section 5.3:** Expand KV-cache agent paragraph on adversarial heuristics
  - Agent detected mutual thrashing between gpubpf prefetch and vLLM allocator
  - Converged to region-differentiated strategy
  - gpubpf's instant detachment bounds pathological cases

- [ ] **Section 4 or 6:** Add note on SASS-level patching
  - Host-side policies don't need PTX (kernel driver only)
  - Device-side: working prototype using NVBit compiler infrastructure

- [ ] **Section 3.5.3:** Clarify map structure supports non-composable data
  - Three tiers: host DRAM, GPU global memory, GPU shared memory
  - Non-composable global state can use host-pinned maps (34ms PCIe latency cost)
  - Example: eviction list is host-authoritative by design

- [ ] **Table 1 / Section 5.5:** Add RTX 5090 data for device-side overhead comparison
  - Currently P40-only because NVBit lacked sm_120 support until Feb 2025
  - Fig.15(a) already shows RTX 5090 data

### Rev D (Solidify weak accept)

- [ ] **Section 6 (Discussion):** Add future directions paragraph
  - CXL memory: adds tier states atop HMM/migrate_vma, async model fits higher latencies
  - Storage tier: millisecond-scale transfers, gpubpf supplies placement policy
  - Future accelerators: verified state-transitions as architected abstraction

- [ ] **Section 6:** Add per-tenant isolation as explicit future work
  - Would require per-cgroup policy attachment
  - Verifier-enforced map namespacing
  - Current single-policy model mirrors sched_ext
  
- [ ] **Section 5.5 or 3.5.2:** Clarify trampoline overhead
  - Per-warp execution (warp leader executes, shuffle-broadcasts)
  - Independent of block count

### Rev E (Convert 2 → 3)

- [ ] **Section 2.3 or 5.4:** Strengthen multi-tenant motivation
  - Cite: MuxFlow (ByteDance SCIS'24) - 42% GPU memory utilization across 20k+ inference GPUs
  - Cite: Orion (EuroSys'24) - below 40% compute throughput
  - Cite: Tally (ASPLOS'25) - inference+training co-location
  - gpubpf results: LC TPOT -40-45%, BE throughput +28%

- [ ] **Section 6:** Add storage-tier extension discussion
  - State machine extends with millisecond-scale storage transitions
  - gpubpf supplies placement policy, complements Weka/VAST/CMX transport

- [ ] **Artifact:** Prepare release package
  - Agent prompts (Claude)
  - Benchmark harnesses
  - Interaction logs

### Rev F (Convert 2 → 3)

- [ ] **Section 3.4, 3.5:** Expand design detail (already covered in Q2)

- [ ] **Section 4:** Expand portability discussion
  - ~100 LOC driver hooks over open GPL kernel modules
  - Aligned with Linux HMM/migrate_vma and DRM scheduler abstractions
  - SPIR-V backend path for non-NVIDIA (prototype exists)

- [ ] **Section 4:** Add ptrace vs LD_PRELOAD discussion
  - ptrace: one-time 273ms attach, fully dynamic
  - LD_PRELOAD: non-intrusive, but can't modify policies at runtime
  - Both supported, choice depends on deployment requirements

---

## Artifact Checklist

- [ ] Agent prompts for Claude
- [ ] Benchmark harness scripts
- [ ] Interaction logs from agent studies
- [ ] README with reproduction instructions

---

## Section Change Summary

| Section | Changes |
|---------|---------|
| 2.3 | Strengthen multi-tenant motivation with citations |
| 3.4 | Algorithm 1 (transition validation), failure-mode taxonomy |
| 3.5.1 | Algorithm 2 (SIMT verifier), rejection examples |
| 3.5.3 | Clarify map structure for non-composable data |
| 4 | TCB, portability (~100 LOC), SASS prototype, ptrace vs LD_PRELOAD |
| 5 | Policy expressibility table, mechanism vs policy attribution |
| 5.3 | Safety statistics, adversarial heuristics handling |
| 5.4 | Expand GPREEMPT comparison |
| 5.5 | RTX 5090 data, trampoline overhead clarification |
| 6 | Related work expansion, CXL/storage/accelerator discussion, per-tenant future work |

---

## Timeline (Suggested)

| Week | Focus |
|------|-------|
| 1 | Q1 (expressibility table, SOTA discussion) + Q2 (algorithms, examples) |
| 2 | Mechanism vs policy attribution + Rev F design expansion |
| 3 | Rev A/D/E specific concerns + artifact preparation |
| 4 | Full read-through, polish, shepherd feedback |

---

## Shepherd Communication

First email to shepherd should:
1. Confirm understanding of major revision requirements
2. Share this plan for feedback
3. Ask about timeline expectations
4. Ask if any concerns need prioritization beyond meta review
