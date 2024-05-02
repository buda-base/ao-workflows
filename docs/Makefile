# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

copy-files:
	@echo "Copying files to root directory"
	cp -a build/html/.  .


clean_build:
	@echo "Cleaning build directory"
	rm -rf *.html *.inv *.js _images _sources _static
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
html: Makefile
	@echo "Building documentation"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)  $(O)

%: Makefile
	@echo "% - pass through"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)  $(O)

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)  $(O)
	@echo "Cleaning build directory"
	# rm -rf *.html *.inv *.js _images _sources _static

build: html copy-files
	@echo "Done"
