# gpu_ext camera-ready working copy

This local version changes the system name and camera-ready presentation
and adds an artifact appendix with verification details. The paper's existing prose, captions,
and comments are preserved.

## Build

```sh
make camera-ready
```

The deliverable is `gpu_ext.pdf`; `main.pdf` is the same built document.
The default `make` target builds this paper only. The historical
`resubmission-changes.tex` remains available via `make revision-note`, but
is not part of the camera-ready deliverable.

## Presentation

- ACM `sigplan` layout, with anonymous/review mode removed and standard
  template geometry restored.
- System and title name: `gpu_ext`. Historical API, repository, raw-data,
  and experiment identifiers keep their original names.
- The ten authors, order, affiliations, and emails in `authors.tex` follow
  the supplied HotCRP record. Individual ACM metadata is retained; the
  visible author list occupies one line, followed by shared affiliations,
  with no email line. The custom renderer only affects the
  title's author block.
- CCS concepts, keywords, acknowledgments, and ACM reference format enabled.
- Eight active figure assets have updated system-name labels. The FAISS
  plot now lists its original nine input files explicitly so unrelated runs
  cannot replace curves through directory iteration order. Its nine plotted
  curves retain their original coordinates; all eight figures retain their
  numeric labels.
- Appendix A retains the artifact repository, brief inventory, and guide
  link. It adds abstract resource-request and transition-validation pseudocode
  with resource-specific synchronization, checks, fallback, and initiation,
  the SIMT verifier's worklist algorithm, and three paired rejection and
  acceptance examples. It does not add agent-workflow exposition.

The built PDF has 16 pages, including one artifact/verification appendix page. The final build
has no errors, overfull boxes, or unresolved references. All nine existing
body-section source files match the pre-edit backup apart from system-name
substitution, and all original main-file comment lines are retained.

## Publication fields still to supply

`camera-ready-metadata.tex` contains the conference name, date and location
from the [official ASPLOS 2027 site](https://www.asplos-conference.org/asplos2027/).
Replace its pending settings with the exact ACM rights-form block when
received. No license, DOI, ISBN, or artifact-evaluation badge has been
invented. The current file leaves DOI/ISBN empty and uses `setcopyright{none}`
until those publication-specific values are supplied.

## Artifact boundary

The original 25 primary and 259 nested agent transcripts remain unavailable
in the existing inventory. Derived Q1--Q6
reports and newly authored prompt templates do not replace the original
interactions. The code/harness/reanalysis links are usable independently;
this edit does not complete the promised original-trace release or certify
all workloads from a fresh GPU machine.
