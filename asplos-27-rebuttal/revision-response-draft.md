Draft reply message:

Thank you for the detailed feedback. We organized the revision around the main issues raised by the reviewers and the shepherd.

1. Policy vs. mechanism and prior systems

   - Clarified that policies drive the headline gains and compared gpubpf with native implementations of the same policies (Abstract, Sections 1 and 7).
   - Added Section 5.2.4 to explain which prior policies gpubpf supports (Table 2) and compare workload baselines, native policies, and gpubpf implementations (Fig. 15), separating policy benefits from gpubpf overhead (Q1, Q15; Reviewers E, F).

2. Safety, verification, and implementation

   - Added Transition Validation (Section 3.5.1), covering ownership, current-state checks, conflicting requests, and synchronization between validation and execution (Q2; Reviewers B, F).
   - Expanded SIMT-aware Verification (Section 3.5.2), explaining uniformity propagation through computations and control flow, including joins and loops.
   - Grouped the TCB, rejected-policy examples, and safety rules (Table 1) in Section 3.5, with verifier responsibilities in Section 4.2.
   - Explained how the model extends to storage/CXL (Section 3.2), what independent tenant policies require (Section 3.4), and how policies handle stale statistics, application heuristics, and raw records (Section 3.5.4). Discussed portability and interfaces for future accelerators in Section 4 (Q3–Q5, Q7, Q9, Q10).

3. Evaluation

   - Organized policy benefits under RQ1 (Section 5.2) and mechanism cost under RQ2 (Section 5.3).
   - Added an LMCache local-disk comparison in Section 5.2.2 (Q1, Q4; Reviewer E).
   - Expanded the joint memory/scheduling comparison in Section 5.2.3 across five configurations, three workloads, and oversubscription ratios (Fig. 12), fulfilling the promised expansion of the original Fig. 13.
   - Added RTX 5090 observability comparisons (Fig. 16) and trampoline-scaling measurements in Section 5.3 (Q8, Q11; Reviewers A, D).
   - Added a Summary at the end of Section 5.2.3, drawing insights from the agent-developed policies in Section 5.2.2 and the memory/scheduling combinations in Section 5.2.3, as requested by the shepherd.
   - Fixed duplicate periods in paragraph headings and stray braces in the bibliography.
