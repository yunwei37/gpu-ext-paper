# ASPLOS 2027 #1797 review record

The review and correspondence record was reconciled with the author's
HotCRP text supplied on 2026-09-03. It is not an independent live HotCRP fetch.

| Record | Contents |
| --- | --- |
| [Reviews A–G](review.txt) | All seven reviews, including A/D/E post-response comments, E's updated score and the G meta-review. The previous E score is retained in the update note and Git history. |
| [Submitted author response](rebuttal.md) | Original Q1–Q15 response, attributed in the supplied page to Andi Quinn, Jul 8. Its leading strategy table is historical author preparation, not review text or current scores. |
| [Revision comments](revision-comments.md) | Full Aug 3 author commitments and Aug 14 shepherd follow-up, including policy/mechanism attribution and typographic requests. |
| [Revision plan](revision-plan.md) | Historical implementation proposal, with corrections noted at its top; not proof of completion. |
| [Current completion checklist](../../revision-completion-checklist.md) | Separates executed experiments, paper integration, artifact release and remaining obligations. |

The meta-review requires all promised changes, with Q1/Q2 and
policy/mechanism attribution emphasized; it does not restrict the revision to
those three topics. Original Q3–Q15 also cover portability, storage/CXL,
application interference, SASS, maps, 5090 overhead, tenant isolation,
stale-state thrashing, trampoline scaling, attachment, co-location and prompts.
Statements quoted from a reviewer or the old response are not automatically
validated implementation claims. In particular, later source audits corrected
the universal-no-op, strict-verifier, block-count-independent-overhead and
historical scheduling-latency assertions.

User direction on 2026-09-03: pause LMCache experiments and prioritize the
other systems. This does not erase the original storage-tier commitment:
retain the failure evidence, keep the storage discussion, and explain the
deferred measurement in the revision response rather than marking it complete.
