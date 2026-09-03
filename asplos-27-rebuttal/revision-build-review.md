# Revision draft build review — 2026-09-03

This is a checked draft checkpoint, **not a submission-ready or fully completed
revision**. It preserves the pre-existing paper revision `d1ab623`.

## Latest integrated build — 12:05 UTC

The fresh `/tmp/gpubpf-paper-integrated-cC8g5i` build uses this tree's source
and a newly generated BibTeX bibliography: **16 pages, 4,466,712 bytes**,
conclusion and references beginning on page 14. There are no undefined
references/citations or overfull horizontal boxes. Two vertical overflows
(1.858 and 9.954 pt) and 80 bibliography metadata warnings remain. This is
not a full citation audit or a completed page-budget reduction.

Hummingbird's full negative result, POD's actual device-selector comparison
and process-wide cost, and both strict-counter positive/negative pairs are
now integrated. The source retains numerical-characterization limitations,
the verification-disabled performance runtime, and the separate native
driver-transition gaps. The POD citation was checked against the local
author PDF's first-page metadata, including its DOI and 16-page length.

Rendered and inspected pages 5, 10, 11 and 12: the SIMT listing is now whole
on page 5; the four-panel scheduling figure, qualified historical memory
figure and seven-row capability table remain readable. The new comparisons
fit within the columns. Condensation removed duplicated setup/exploration
prose and two non-result illustrations, retaining their assets and every
reported adverse result; type size and margins were not reduced.

The working original-body-plus-two-page target remains unmet. LMCache's
repaired disk preflight has passed and its correctness/formal sequence is
ongoing outside this paper build. Table 1, the actual Expert Buffering policy,
remaining native safety tests, refreshed engaged memory/scheduling matrix
and original-transcript recovery are not closed by this checkpoint.

## Earlier checkpoint, retained for history

## Fresh build and visual checks

- Built with system pdfLaTeX, BibTeX, and repeated pdfLaTeX in the new directory
  `/tmp/gpubpf-paper-review-BpRzNp`. BibTeX ran from that directory with
  `BIBINPUTS` and `BSTINPUTS` pointing at the paper tree. The final log reads
  that directory's newly generated `main.bbl`, not the stale repository copy.
- Build succeeds: **18 pages, 4,522,544 bytes**, no undefined references or
  citations and no overfull horizontal boxes. Existing bibliography metadata
  warnings and two small vertical overflows (1.36/1.844 pt) remain; this is not
  a full citation audit.
- Regenerated historical Fig. 13 from the six explicitly selected CSVs using
  `img/results-raw/multi-tenant/plot_all_kernels_stacked.py`. Inputs and values
  are unchanged. The system Python has the plotting libraries; the MoE virtual
  environment does not. A pandas optional-bottleneck-version warning did not
  stop the successful plot generation.
- Rendered and visually inspected pages 12 and 13: the new four-panel XSched/
  GPreempt plot, corrected historical Fig. 13 and capability table are readable
  at full text width. The caption distinguishes metrics, medians, individual
  cells, missing historical engagement and the absence of equivalence claims.
- A 38.15 pt scheduling-helper overflow was fixed with explicit word-break
  opportunities and a shorter sentence. Recompiled and inspected page 7;
  helper names now remain inside the column without shrinking type or margins.
- Active paragraph headings and bibliography brace repairs are included in
  the fresh output. Historical raw observations and the superseded Fig. 12
  assets remain retained; the unsupported 96% launch-latency claim is removed
  from the active evaluation.

Rebuild from a new output directory, preserving current source:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=NEW_DIR main.tex
# In NEW_DIR, with BIBINPUTS and BSTINPUTS set to the paper directory:
bibtex main
# Back in the paper directory, repeat twice:
pdflatex -interaction=batchmode -halt-on-error -output-directory=NEW_DIR main.tex
```

## Remaining publication work

The old PDF concludes on page 11 and begins references on page 12. This draft
concludes on page 16 and begins references later on that page. The working
original-body-plus-two-page target is therefore **not met**; removing only
reference pages would not solve it. Keep the new scheduling figure readable
and retain the safety boundaries and negative results while condensing
duplicated exposition, detailed exploration histories and secondary figures.
The short SIMT listing currently crosses pages 5–6 and should be kept together
in the final layout. Rebuild and re-inspect after those changes.

The matched subsection currently contains MoE-Infinity, XSched, GPreempt,
FineMoE and the separate 610 UVM mechanism-cost result. The newly completed
Hummingbird report still needs integration. POD's full comparison, strict
device enforcement, LMCache disk and RTX 5090 instrumentation results are
still pending. Missing original agent transcripts are not replaced by newly
authored reproduction prompts. See the parent repository's
`docs/revision-completion-checklist.md` for the live execution ledger.
