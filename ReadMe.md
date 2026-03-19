## Setup

```bash
uv pip install -e .
uv pip install -e ".[dev]"

pre-commit install 


detect-secrets scan > .secrets.baseline