# Simple Makefile to build LaTeX paper with minted
# Usage: make (build), make clean, make distclean

TEX=main.tex
PDF=main.pdf
TEX_SRCS=$(wildcard tex/*.tex) $(TEX)
IMG_SRCS=$(wildcard img/*)
BIB=cite.bib

LATEX=pdflatex
LATEXFLAGS=-shell-escape -interaction=nonstopmode -halt-on-error
BIBTEX=bibtex

.PHONY: all clean distclean

all: $(PDF)

$(PDF): $(TEX_SRCS) $(IMG_SRCS) $(BIB)
	$(LATEX) $(LATEXFLAGS) $(TEX)
	$(BIBTEX) main || true
	$(LATEX) $(LATEXFLAGS) $(TEX)
	$(LATEX) $(LATEXFLAGS) $(TEX)

clean:
	@rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.out *.toc *.lof *.lot *.bcf *.run.xml
	@rm -rf _minted-*

distclean: clean
	@rm -f $(PDF)
