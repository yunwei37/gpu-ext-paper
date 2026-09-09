Draft reply message: 

Thank you for the detailed feedback. We organized the revision around the main issues raised by the reviewers and the shepherd.

Policy vs. mechanism and prior systems
Clarified in the Abstract, Introduction, Evaluation, and Conclusion which headline improvements come from policies implemented through gpubpf versus the gpubpf mechanism itself.
Added a policy-expressibility table and comparisons with seven policies from prior systems, including baseline/native/gpubpf results to quantify the overhead of the general mechanism.
Expanded the discussion of prior systems and explicitly identify policies and policy combinations enabled by gpubpf, including those produced through the agentic workflow.
Safety, verification, and implementation
Added a Transition Validation subsection describing resource-ownership checks.
Expanded the SIMT verifier description, including propagation through computations, branches, joins, and loops.
Added a safety-rule table (Table 1), rejected-policy examples, failure modes, and a description of the trusted computing base and verifier responsibilities.
Added discussions of stale statistics, per-tenant policies, storage/CXL extensions, application-policy interactions, raw observations, portability, and future accelerator interfaces.
Evaluation
Reorganized the evaluation around policy expressibility and benefits (RQ1) and mechanism cost (RQ2).
Added seven-policy prior-system comparisons (Table 2 and Fig. 15)
Expanded multi-tenant memory/bandwidth/scheduling experiments across five configs and three workloads (Fig. 12)
Added RTX 5090 and trampoline-scaling measurements (Fig. 16).
Clarified when results arise from application behavior, policy choices, or mechanism overhead.
Highlighted new policy implemented in gpubpf by AI Agents and summary them.
Fixed the noted typographic issues and typos
