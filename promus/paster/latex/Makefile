# Make file to compile a latex document. Modify the next variables
# according to your project needs.
#
#   texfile: Should be the name of the main latex file without
#            the .tex extension
#
#   TEX: The tex compiler (pdflatex, xelatex, ...)
#
#   rev: An integer to specify how versions to revert to so that
#        latexdiff can do the difference between the current document
#        and the older version. Value of 0 will compare your current 
#        edits to the latest version saved in the repository.
#    
#
file = doc
TEX = pdflatex
rev = 0

# Default behavior
all: pdf diff clean

# Reruns latex if needed.
$(file).pdf: $(wildcard *.tex)
	while ($(TEX) $(file) ; \
	grep -q "Rerun to get cross" $(file).log ) do true ; \
	done

pdf: $(file).pdf
	
diff:
	git show HEAD~${rev}:./$(file).tex > $(file)-old.tex
	latexdiff --flatten $(file)-old.tex $(file).tex > $(file)-diff.tex
	while ($(TEX) $(file)-diff ; \
	grep -q "Rerun to get cross" $(file)-diff.log ) do true ; \
	done
	@rm -f $(file)-diff.tex
	@rm -f $(file)-old.tex

clean:
	rm -f *.aux
	rm -f *.log
	rm -f *.out
