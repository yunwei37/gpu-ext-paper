# Expert Buffering result integration

2026-09-03: the active paper now reports the complete five-block matched
FIFO/native/host-uBPF Section VI policy port. The paragraph gives the three
median throughputs, paired throughput intervals, identical native/BPF policy
outcomes, 12.85% logical-copy reduction and the measured 0.74% BPF/native
cost. It explicitly excludes original distributed-system/model/throughput
reproduction and PCIe-traffic claims. The introduction's inventory now names
Expert Buffering; the stale Expert Buffering TODO is removed while the paused
LMCache correctness gap remains explicit.

The Huang et al. citation was transcribed from the retained complete arXiv
v2 PDF's title/authors/version metadata and added to `cite.bib` as
`huang2023towards` (`arXiv:2303.06182`, cs.DC, 2023).

The first fresh-build attempt used an absolute BibTeX output path; TeX's
`openout_any=p` rejected that path, so the resulting unresolved-citation PDF
was discarded as validation evidence. A clean retry ran BibTeX from its new
temporary output directory, followed by two final `pdflatex` passes. The final
log has no undefined citation/reference warning, includes the new bibliography
entry, and produces a letter-size **16-page PDF with Conclusion on page 14**.
Thus the local result integration builds successfully and does not add a page,
but the previously recorded page-budget gap remains unresolved.

The paragraph rewrite followed the local systems-paper rule: lead with the
matched setup, state policy and mechanism effects separately, then close with
the reproduction boundary. No figure, package, label or result outside the
newly completed campaign was changed.
