PYTHON ?= python3
PEBBLE ?= pebble
.PHONY: assets test build package independent
assets:
	$(PYTHON) test/generate.py
test:
	$(PYTHON) test/check.py
	$(PYTHON) tools/languages/check.py .
build:
	$(PEBBLE) build --sdk 4.33.1
	$(PYTHON) test/package.py
package:
	$(PYTHON) test/package.py --evidence build/evidence
independent:
	$(PYTHON) test/independent.py

languages:
	$(PYTHON) tools/languages/generate.py .
settings-test:
	node tools/languages/settings.cjs .
