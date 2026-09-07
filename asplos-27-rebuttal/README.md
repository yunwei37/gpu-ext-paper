# ASPLOS 2027 #1797 review record

The review and correspondence record was reconciled with the author's
HotCRP text supplied on 2026-09-03. It is not an independent live HotCRP fetch.

| Record | Contents |
| --- | --- |
| [Reviews A–G](review.txt) | All seven reviews, including A/D/E post-response comments, E's updated score and the G meta-review. The previous E score is retained in the update note and Git history. |
| [Submitted author response](rebuttal.md) | Original Q1–Q15 response, attributed in the supplied page to Andi Quinn, Jul 8. Its leading strategy table is historical author preparation, not review text or current scores. |
| [Revision comments](revision-comments.md) | Full Aug 3 author commitments and Aug 14 shepherd follow-up, including policy/mechanism attribution and typographic requests. |
| [Revision plan](revision-plan.md) | Historical implementation proposal, with corrections noted at its top; not proof of completion. |
| [Revision response draft](revision-response-draft-20260907.md) | Evidence-linked 2026-09-07 author-review draft; not submitted to the conference. Distinguishes scoped results, open deliverables and future extensions. |
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

The historical 2026-09-03 LMCache pause was superseded by the user's later
instruction to resume. Local-disk, native/BPF storage-policy and the matched
write-budget campaigns are now complete at their reported scope; see the
current revision plan and response draft above. Earlier failures remain
retained, but do not label these completed measurements deferred.
