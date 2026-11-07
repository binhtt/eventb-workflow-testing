PYTHON ?= python3

.PHONY: audit test smoke full analysis

audit:
	$(PYTHON) scripts/verify_artifact.py

test: audit
	$(PYTHON) -m unittest discover -v -s code -p checks.py

smoke:
	$(PYTHON) code/reproduce.py --mode smoke

full:
	$(PYTHON) code/reproduce.py --mode full

analysis:
	$(PYTHON) code/reproduce.py --mode analysis
