PYTHON ?= python

.PHONY: install install-dev format lint test run pre-commit-install pre-commit-run clean

# Install basic dependencies
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

# Install with dev dependencies
install-dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

# Format code
format:
	$(PYTHON) -m black app tests
	$(PYTHON) -m ruff format app tests

# Lint check
lint:
	$(PYTHON) -m ruff check app tests
	$(PYTHON) -m black --check app tests

fix:
	$(PYTHON) -m ruff check app tests --fix
	
# Run tests
test:
	$(PYTHON) -m pytest tests

# Run FastAPI app
run:
	$(PYTHON) -m uvicorn app.main:app --reload

# Pre-commit setup
pre-commit-install:
	$(PYTHON) -m pre_commit install

pre-commit-run:
	$(PYTHON) -m pre_commit run --all-files

# Clean cache files (cross-platform safe)
clean:
	$(PYTHON) -c "import shutil, os; [shutil.rmtree(d, ignore_errors=True) for d in ['.pytest_cache', '.ruff_cache']];"