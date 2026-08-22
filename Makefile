.PHONY: api-install api-check api-test api-run web-install web-check web-test web-regression audit-prod audit-release

API_DIR := services/api
API_PYTHON := $(API_DIR)/.venv/bin/python

web-install:
	npm install

web-check:
	npm run check:web

web-test:
	npm run test:ui

web-regression:
	npm run verify:upgrade

audit-prod:
	npm run audit:prod:baseline

audit-release:
	npm run audit:prod:release

api-install:
	@python3 -c "import sys; sys.exit('Python 3.11+ is required; found ' + sys.version.split()[0]) if sys.version_info < (3, 11) else None"
	python3 -m venv $(API_DIR)/.venv
	$(API_PYTHON) -m pip install --upgrade pip
	$(API_PYTHON) -m pip install -e "$(API_DIR)[dev]"

api-check:
	$(API_PYTHON) -m ruff format --check $(API_DIR)
	$(API_PYTHON) -m ruff check $(API_DIR)
	$(API_PYTHON) -m mypy $(API_DIR)/src

api-test:
	$(API_PYTHON) -m pytest $(API_DIR)/tests

api-run:
	$(API_PYTHON) -m uvicorn app.main:app --app-dir $(API_DIR)/src --reload --port 8000
