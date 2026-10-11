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
  template geometry restored. The repository bundles acmart v2.20
  (`acmart.cls`, `ACM-Reference-Format.bst`) so the build does not depend on
  the system TeX Live version.
- Title: the accepted title, "Safe and Programmable OS-Level GPU Resource
  Management with eBPF", without a system-name prefix. System name in the
  body: `gpu_ext`. Historical API, repository, raw-data, and experiment
  identifiers keep their original names.
- The ten authors, order, and emails in `authors.tex` follow the ACM
  rights-review record. Each author uses the standard acmart block
  (institution, city, country, email); grouped author strings are not
  allowed by ACM/Sheridan. These values must stay identical to the ACM
  rights-review form.
- CCS concepts, keywords, acknowledgments (NSF Award #2530909 and NEUTC;
  Williams' group: NSF award 2236966 and the eBPF Foundation; generative-AI
  disclosure), and ACM reference format enabled. The final page is balanced.
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

The built PDF has 17 pages: a 13-page body (including acknowledgments),
references, and one artifact/verification appendix page. The build has no
errors, overfull boxes, or unresolved references.

## Publication fields

`camera-ready-metadata.tex` uses Sheridan's ASPLOS 2027 V1 CR+CC-BY block:
Proceedings volume title, ISBN 979-8-4007-3012-2/2027/04, and DOI
10.1145/3845814.3850045 (Sheridan submission v1fp1797). Keep the license
(`setcctype`) identical to the choice on the ACM rights-review form, and
compare all values with the rights-review confirmation email.

## Artifact boundary

The original 25 primary and 259 nested agent transcripts remain unavailable
in the existing inventory. Derived Q1--Q6
reports and newly authored prompt templates do not replace the original
interactions. The code/harness/reanalysis links are usable independently;
this edit does not complete the promised original-trace release or certify
all workloads from a fresh GPU machine.
