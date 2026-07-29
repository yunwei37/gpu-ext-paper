# ASPLOS'27 #1797 Revision Plan

## Meta Review

1. Implement all rebuttal commitments
2. **Q1 (SOTA baselines)** and **Q2 (safety)** are major sticking points
3. Distinguish mechanism vs policy (Rev F)

## Q1: SOTA Baselines

- Section 5: Add policy expressibility table (policy → user-space / driver-mod / gpubpf)
- Section 5.4: Expand GPREEMPT (925 LOC, zero driver changes, 96% P99 reduction)
- Section 6: Add TimeGraph/Gdev/GCAPS/LithOS comparison paragraph

## Q2: Safety

- Section 3.4: Transition validation pseudocode + failure mode taxonomy
- Section 3.5.1: SIMT verifier algorithm + 3 rejection examples
- Section 5.3: Safety stats (59 policies, 974 runs, 50 events caught, 0 panics)

## Mechanism vs Policy (Rev F)

- Interpret Fig.13: scheduling <1%, memory policies 55-92%
- Clarify: driver mods possible but lose safety + dynamism

## Per-Reviewer

- A: SASS prototype note, RTX 5090 in Table 1
- D: CXL/storage future work, per-tenant isolation
- E: Multi-tenant citations (MuxFlow/Orion/Tally)
- F: Portability (~100 LOC), ptrace vs LD_PRELOAD

## Artifact

- Release agent prompts + benchmark harnesses
