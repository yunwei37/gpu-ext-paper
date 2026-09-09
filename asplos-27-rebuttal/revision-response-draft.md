Draft reply message:

Thank you for the detailed feedback. We organized the revision around the main issues raised by the reviewers and the shepherd.

1. Policy vs. mechanism and prior systems

   - Clarified which gains come from policies and how gpubpf compares with native implementations of the same policies (Abstract, Sections 1 and 7). The headline application gains come from workload-specific policies, while gpubpf provides the safe, programmable mechanism for implementing them.
   - Added Policies from Prior Systems and a policy-expressibility table explaining seven prior policies, their original mechanisms, and how gpubpf implements them (Section 5.2.4, Table 2).

2. Safety, verification, and implementation

   - Added a Transition Validation subsection describing ownership and state checks, conflicting requests, and synchronization between validation and transition initiation (Section 3.5.1).
   - Expanded the SIMT verifier description and its uniformity analysis, including propagation through computations, branches, joins, and loops (Section 3.5.2).
   - Added a safety-rule table (Table 1) and rejected-policy examples, expanded the TCB description (Section 3.5), and clarified verifier responsibilities (Section 4.2).
   - Added discussions of storage/CXL (Section 3.2), independent tenant policies (Section 3.4), stale statistics, application-policy interactions, and raw records (Section 3.5.4), plus portability and future accelerators (Section 4).

3. Evaluation

   - Reorganized the evaluation around policy benefits (RQ1, Section 5.2) and mechanism cost (RQ2, Section 5.3).
   - To address whether the gains come from policies or the mechanism, and what performance cost gpubpf adds, we added comparisons for seven policies from prior systems (e.g., MoE-Infinity, Expert Buffering, and XSched; Section 5.2.4, Fig. 15). For each policy, we compare the workload baseline, its native implementation, and its gpubpf implementation. The results show that gpubpf preserves the evaluated policies’ benefits with near-native performance: the difference in main metrics between gpubpf and native implementations is below 2% for the configurations shown in Fig. 15.
   - Highlighted policies developed by AI Agents, and added a Summary of their insights and the benefits of coordinating memory and scheduling (Sections 5.2.2–5.2.3). These cases show how application access patterns and priorities guide joint decisions about data residency, transfer timing, and execution.
   - Expanded the memory/scheduling experiments across five configurations, three workloads, and oversubscription ratios (Section 5.2.3, Fig. 12), and added LMCache local-disk read-latency results (Section 5.2.2). Combined policies further reduce high-priority completion time over scheduling or memory alone.
   - Added RTX 5090 comparisons (Fig. 16) and trampoline-scaling measurements (Section 5.3). The evaluated tools incur lower overhead than NVBit; the scaling tests show low trampoline overhead, with map-update costs growing roughly linearly with active work.

We also fixed duplicate periods in paragraph headings and stray braces in the bibliography.
