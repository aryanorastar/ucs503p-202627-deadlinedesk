PYTHON ?= .venv/bin/python

.PHONY: setup run test check migrate seed docs docbuild

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
