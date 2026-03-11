# Contributing to openfisca-ai

Thank you for your interest in contributing.

## Development setup

```bash
git clone <repo-url>
cd openfisca-ai
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Code style

- Use Python 3.10+.
- Prefer type hints for public APIs.
- Keep modules focused; add new agents/skills under `src/openfisca_ai/` as needed.

## Pull requests

1. Open an issue or pick an existing one.
2. Branch from `main`, make your changes, add tests if applicable.
3. Ensure tests pass and the CLI still runs.
4. Submit a PR with a clear description of the change.
