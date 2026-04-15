# ASPLOS 2027 -- Call for Papers

**30th ACM International Conference on Architectural Support for Programming Languages and Operating Systems**

**Crete, Greece -- April 11-15, 2027**

Official CFP page: https://www.asplos-conference.org/asplos2027/cfp/

## Important Dates

All dates are AoE (Anywhere on Earth). No separate abstract deadline.

**April Cycle:**
- Full paper submission: April 15, 2026
- Author response: July 6-9, 2026
- Notification: July 27, 2026

**September Cycle:**
- Full paper submission: September 9, 2026
- Author response: December 1-4, 2026
- Notification: December 21, 2026

## Formatting and Editing

We will use the same format template for submission and camera-ready versions. Submissions must be printable PDF files. When creating your submission, you must use the ACM's acmart Latex class available on the official ACM site, with sigplan, anonymous, review, and non-acm options. The review option enables line numbering which assists reviewers in making feedback concrete and specific. The non-acm option removes the ACM copyright information block. Your main LaTeX file should have the following structure:

```latex
% use the base acmart.cls
% use the sigplan proceeding template with the default 10 pt fonts
% nonacm option removes ACM related text in the submission. 
\documentclass[sigplan,anonymous,review,nonacm]{acmart}


\begin{document}
\title{...}


\begin{abstract}
...
\end{abstract}


\maketitle % should come after the abstract


% add the paper content here


% use the ACM bibliography style
\bibliographystyle{ACM-Reference-Format}
\bibliography{...}


\end{document}
```

Your final submission should visually look similar to this sample produced from the zip file above.

"Squeezing" Space is Forbidden. Refrain from tweaking the aforementioned template and from formatting your text in a manner that violates its settings. Notably, refrain from squeezing additional space, e.g., by using \vspace or packages that manipulate vertical space. The template already generates a very dense document, and you must not make it denser. Your submission will be visually and automatically inspected using tools developed for this purpose, and it will be rejected if you violate the formatting policy, even if your PDF passed the HotCRP format check (which is unable to verify much of the requirements).

### Page Layout and Limit

Full submissions must not exceed 11 pages of single-spaced two-column text. This page limit applies to all text, figures, tables, and footnotes. The only exceptions are the acknowledgment section (used only to acknowledge use of Generative AI as per ACM policy above), the bibliographic references section, and the appendices, which are not included in the page limit. Note that the submission must be self-contained within the page limit, allowing reviewers to evaluate the work without having to consider any external or supplementary material outside this limit. The reviewers greatly value conciseness, so if you can describe your work with fewer pages than the limit, please do. All pages should be numbered.

### Page Limit of Accepted Papers and Major Revisions

The authors of an accepted paper are allowed to use two additional pages in the camera-ready version beyond the aforementioned page limit. The same applies to major revisions, to accommodate added experiments and such. In addition to this +2 automatic page limit increase, authors of accepted papers may purchase 1-2 more pages, if they wish (payment will be processed when registering to the conference).

### Font Size, Tables, and Figures

The submission's text must use a 10pt font (not 9pt) or bigger. Labels, captions, and text within figures, graphs, and tables must use reasonable font sizes that, as printed, do not require extra magnification beyond "100%" to be legible. In particular, text inside figures/tables should generally use what appears to readers as a 9pt font or bigger after any intra-document scaling has been applied. Fonts appearing smaller than 8pt are not permitted. As noted, this and other requirements are not checked automatically by the HotCRP format checker, so it is the authors' responsibility to check it. Figures can and should use colors but should also be color-blind friendly. Spacing between figures/tables/captions/text should be determined by the latex template.

### References

Because references do not count against the page limit, the space they occupy should not be "optimized" away. Notably, the full, non-abbreviated first and last names of all co-authors of all citations must be specified (no "et al."). The reference citations within the submission (numbers in square brackets) should be hyperlinked to the corresponding items in the references section, to ease the job of reviewers. Also, reviewers will very much appreciate clickable links (preferably DOIs) associated with each entry in your references section.

### Specifications

The following table specifies some of the main typeset requirements. Use our mandatory latex template and follow the above instructions to make sure that these and other formatting requirements are met.

| Aspect | Requirement |
|--------|-------------|
| file format | PDF with numbered pages |
| page limit | 11 pages, not including references |
| paper size | US Letter 8.5in x 11in |
| top margin | 1in |
| bottom margin | 1in |
| left margin | 0.75in |
| right margin | 0.75in |
| column separation | 0.333in |
| body | 2-column, single-spaced |
| body font size | 10pt |
| abstract font | 10pt |
| section heading font | 12pt, bold |
| subsection heading font | 10pt, bold |
| space between section heading and text | ≥ 6pt |
| caption font | 9pt |
| fonts in figures and tables | ≥ 8pt, preferably ≥ 9pt |
| reference entries | 8pt; no page limit; list full names of all author (no "et al."); include link to document (preferably DOI); make references to citations clickable |
| appendices | do not count towards the page limit |

Submissions that violate any of these restrictions might be rejected without being reviewed.

## Anonymization (Double-Blind Review)

- Double-blind review process.
- Must make good faith attempt to anonymize: avoid identifying yourself or institution in submitted documents.
- Do not include "reference removed for blind review" text.
- Cite own studies as written by a third party.
- Only if not possible, upload and cite as anonymized supplemental material.
- Improperly anonymized submissions will likely be rejected without review.

## Submission Limits

- Maximum **4 submissions per author per cycle**.

## Review Process

### Rapid Review Round

- Double-blind rapid review considering only the **first two pages**.
- Assesses alignment with ASPLOS acceptance criteria and reviewer expertise.
- Authors should ensure **first two pages are self-contained**.
- A majority of submissions may not advance past rapid review.
- Brief feedback provided for papers not advanced.

### Full Review

- Uses Program Committee (PC) and Extended Review Committee (ERC).
- May ask for external reviews.

### Evaluation Criteria

- Relevance, novelty, technical merit, clarity.
- Must adhere to SIGPLAN Empirical Evaluation Guidelines.
- Strong submissions should: clearly motivate a significant problem, propose practical solutions, demonstrate advantages and disadvantages through sound experimental methods, state implementation status, articulate novel contributions, avoid overstatement.

## Author Response (Rebuttal)

- No hard word limit, but reviewers not expected to read beyond **800 words**.
- May describe new experiments/data if major revision is realistic possibility.

## Major Revision

- In addition to Accept/Reject, some submissions may receive "Major Revision".
- **6 weeks from notification** to revise and resubmit at camera-ready deadline.
- Clear, actionable reviewer feedback provided.
- Typically reviewed by same reviewers.

## Camera-Ready

- Accepted papers: **13 pages** (11 + 2 additional pages at no charge).
- May purchase 1-2 additional pages beyond that.

## Withdrawal and Resubmission Policy

- Withdrawn after reviews = considered "rejected" from that cycle.
- **Cannot resubmit to next two cycles**.

## Responsible Use of Generative AI

- Must fully disclose use of Generative AI per ACM authorship policy.
- GenAI tools may not be listed as authors.
- Use is permitted but must be disclosed in Acknowledgments section (before References).
- Example: "ChatGPT was utilized to generate sections of this Work, including text, tables, graphs, code, data, citations, etc."

## Artifact Evaluation

- Artifact evaluation continues in 2027 as ASPLOS tradition.

## Presentation Requirement

- One author must physically attend and present (exceptions for visa, care-giving, disability).
