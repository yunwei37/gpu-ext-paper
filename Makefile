# Simple Makefile to build LaTeX paper with minted
# Usage: make (build), make clean, make distclean

TEX=main.tex
PDF=main.pdf
RESUB_TEX=resubmission-changes.tex
RESUB_PDF=resubmission-changes.pdf
TEX_SRCS=$(wildcard tex/*.tex) $(TEX)
IMG_SRCS=$(wildcard img/*)
BIB=cite.bib

# SVG processing
SVGS=$(wildcard img/*.svg)
SVG_PDFS=$(SVGS:.svg=.pdf)

# HTML figure processing (Chrome headless)
CHROME=google-chrome-stable
CHROME_FLAGS=--headless --disable-gpu --no-sandbox --print-to-pdf-no-header
HTML_FIGS=$(wildcard img/*.html)
HTML_PDFS=$(HTML_FIGS:.html=.pdf)

LATEX=pdflatex
LATEXFLAGS=-shell-escape -interaction=nonstopmode -halt-on-error
BIBTEX=bibtex

.PHONY: all clean distclean

all: $(PDF) $(RESUB_PDF)

# Rule to convert SVG to PDF
img/%.pdf: img/%.svg
	convert $< $@

# Rule to convert HTML figures to PDF (via Chrome headless)
img/%.pdf: img/%.html
	$(CHROME) $(CHROME_FLAGS) --print-to-pdf=$@ $<

$(RESUB_PDF): $(RESUB_TEX)
	$(LATEX) $(LATEXFLAGS) $(RESUB_TEX)

$(PDF): $(TEX_SRCS) $(IMG_SRCS) $(BIB) $(SVG_PDFS) $(HTML_PDFS)
	$(LATEX) $(LATEXFLAGS) $(TEX)
	$(BIBTEX) main || true
	$(LATEX) $(LATEXFLAGS) $(TEX)
	$(LATEX) $(LATEXFLAGS) $(TEX)

clean:
	@rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.toc *.lof *.lot *.bcf *.run.xml
	@rm -rf _minted-*
	@rm -f $(SVG_PDFS)
	@rm -f $(HTML_PDFS)

distclean: clean
	@rm -f $(PDF) $(RESUB_PDF)
