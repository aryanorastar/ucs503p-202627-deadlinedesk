PYTHON ?= .venv/bin/python
DRAWIO ?= drawio
FIGURES := project-proposal/figures

.PHONY: setup run test check migrate seed docs docbuild diagrams

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) code/manage.py runserver

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) code/manage.py check
	$(PYTHON) code/manage.py makemigrations --check

migrate:
	$(PYTHON) code/manage.py migrate

seed:
	$(PYTHON) code/manage.py seed_demo

docs:
	$(PYTHON) -m mkdocs serve

docbuild:
	$(PYTHON) -m mkdocs build

# The .drawio files are the only diagram sources; this target only exports them.
# Needs draw.io Desktop's CLI (macOS: brew install --cask drawio).
diagrams:
	@for src in $(FIGURES)/*.drawio; do \
		$(DRAWIO) -x -f pdf --crop -a -b 12 -o "$${src%.drawio}.pdf" "$$src" && \
		$(DRAWIO) -x -f png -s 2 -b 24 -p 1 -o "$${src%.drawio}.png" "$$src" || exit 1; \
	done
