# Install dependencies
install:
	uv pip install -e .
	uv pip install -e ".[dev]"

# Run app
run:
	uvicorn app.main:app --reload

# Run tests
test:
	pytest

# Lint check
lint:
	ruff check .

# Format code
format:
	ruff check . --fix
	ruff format .
	black .

# Pre-commit
precommit:
	pre-commit run --all-files