PYTHON ?= ../.venv/bin/python

.PHONY: run check test migrate seed

run:
	$(PYTHON) manage.py runserver

check:
	$(PYTHON) manage.py check

test:
	$(PYTHON) -m pytest

migrate:
	$(PYTHON) manage.py migrate

seed:
	$(PYTHON) manage.py seed_demo
