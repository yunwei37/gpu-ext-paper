Draft reply message:

Thank you for the detailed feedback. We organized the revision around the main issues raised by the reviewers and the shepherd.

1. Policy vs. mechanism and prior systems

   - Clarified in the Abstract, Introduction, Evaluation, and Conclusion that the headline improvements come from policies implemented through gpubpf, and separately summarized comparisons with native implementations.
   - Added a policy-expressibility table explaining seven prior policies, their underlying mechanisms, and how gpubpf implements their decisions (Table 2).
   - Highlighted workload-specific policies and policy combinations enabled by gpubpf, including choices made through the agentic workflow.

2. Safety, verification, and implementation

   - Added a Transition Validation subsection covering resource ownership, current-state checks, conflicting requests, and synchronization between validation and execution.
   - Expanded the SIMT verifier description, including propagation through computations and control flow, joins, and loops.
   - Added a safety-rule table (Table 1), rejected-policy examples, responses to invalid requests, and an explicit description of the trusted computing base.
   - Integrated author-response clarifications on stale statistics, per-tenant policies, storage/CXL extensions, application-policy interactions, raw observations, portability, and future accelerator interfaces.

3. Evaluation

   - Reorganized the evaluation around policy expressibility and benefits (RQ1) and mechanism cost (RQ2).
   - Added baseline/native/gpubpf comparisons for seven prior policies to distinguish policy benefits from implementation overhead (Fig. 15).
   - Expanded the joint memory/scheduling experiments across five configurations, three workloads, and varying oversubscription ratios (Fig. 12).
   - Added RTX 5090 observability comparisons (Fig. 16) and trampoline-scaling measurements.
   - Added a Summary explaining how application access patterns and task priorities guide coordinated memory and scheduling decisions, and how agent-developed policies specialize these decisions to workloads.
   - Addressed the duplicate paragraph-heading punctuation and bibliography brace-rendering issues.
