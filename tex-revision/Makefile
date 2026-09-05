# Simple Makefile to build LaTeX paper with minted
# Usage: make (build), make clean, make distclean

TEX=main.tex
PDF=main.pdf
RESUB_TEX=
RESUB_PDF=
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

# Python figure scripts
PLOT_SCRIPTS = \
	img/results-raw/clc/plot_microbench_combined.py \
	img/results-raw/llama.cpp/visbasic.py \
	img/results-raw/vllm/generate_figures.py \
	img/results-raw/faiss/plot_results.py \
	img/results-raw/multi-tenant/plot_figures.py \
	img/results-raw/multi-tenant/plot_all_kernels_stacked.py \
	img/results-raw/multi-tenant/plot_colocated_results.py \
	img/pattern/vector_add/plot_thread_scheduling.py

.PHONY: all clean distclean figures

all: $(PDF)

figures:
	@echo "Regenerating all figures..."
	@for script in $(PLOT_SCRIPTS); do \
		echo "  Running $$script"; \
		python $$script || echo "  FAILED: $$script"; \
	done
	@echo "Done."

# Rule to convert SVG to PDF
img/%.pdf: img/%.svg
	convert $< $@

# Rule to convert HTML figures to PDF (via Chrome headless)
img/%.pdf: img/%.html
	$(CHROME) $(CHROME_FLAGS) --print-to-pdf=$@ $<




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
	@rm -f $(PDF)
