PYTHON ?= .venv/bin/python
DRAWIO ?= drawio
FIGURES := project-proposal/figures

.PHONY: setup run test check migrate seed docs docbuild diagrams demo

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
	$(PYTHON) scripts/export_diagrams.py

demo:
	$(PYTHON) scripts/run_demo.py
