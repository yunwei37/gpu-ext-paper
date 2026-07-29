# ASPLOS'27 #1797 Revision Plan

## Meta Review Requirements

1. Implement all rebuttal commitments
2. **Q1 (SOTA baselines)** and **Q2 (safety)** are major sticking points
3. Distinguish mechanism vs policy improvements (Rev F)

---

## Priority 1: Q1 + Q2

| Item | Section | Change |
|------|---------|--------|
| Policy expressibility table | 5 | New table: policy → {user-space, driver-mod, gpubpf} |
| GPREEMPT comparison | 5.4 | Expand: 925 LOC, zero driver changes, 96% P99 reduction |
| Driver-mod systems | 6 | Add paragraph: TimeGraph/Gdev/GCAPS/LithOS vs gpubpf |
| Transition validation | 3.4 | Add pseudocode algorithm |
| SIMT verifier | 3.5.1 | Add algorithm + 3 rejection examples |
| Failure modes | 3.4 | Add taxonomy (verifier reject / no-op / thrashing detect) |
| Safety statistics | 5.3 | 59 policies, 974 runs, 50 events caught, 0 panics |

---

## Priority 2: Mechanism vs Policy (Rev F)

- [ ] Interpret Fig.13: scheduling <1%, memory policies 55-92%
- [ ] Clarify: policies *could* use driver mods, but lose safety + dynamism

---

## Priority 3: Per-Reviewer

| Rev | Key Addition |
|-----|--------------|
| A | SASS prototype note, RTX 5090 in Table 1 |
| D | CXL/storage future work, per-tenant isolation |
| E | Multi-tenant citations (MuxFlow/Orion/Tally) |
| F | Portability (~100 LOC), ptrace vs LD_PRELOAD |

---

## Artifact

- [ ] Release agent prompts + benchmark harnesses
