# Contributing to {{project_name}}

Thank you for your interest in contributing!

## Prerequisites

```bash
git clone <repo-url>
cd {{project_slug}}
uv sync
```

## Automatic code checks with pre-commit

Automatic checks run before each commit via [pre-commit](https://pre-commit.com/).

### Installation

```bash
uv run pre-commit install
```

### Run checks manually

```bash
uv run pre-commit run --all-files
```

## Validation with openfisca-ai

This repository uses [openfisca-ai](https://github.com/benjello/openfisca-ai) as a validation toolkit:

```bash
uv run openfisca-ai validate-parameters .
uv run openfisca-ai validate-units .
uv run openfisca-ai validate-code .
uv run openfisca-ai audit .
```

## Tests

```bash
uv run pytest
```

## Code style

- Python 3.10+.
- Prefer type hints for public APIs.
- No hardcoded legal values — everything in YAML parameter files.

## Changelog format

The [CHANGELOG.md](CHANGELOG.md) documents each version. Possible sections:

- **Added**: new feature, new variable, new parameter.
- **Changed**: regulatory update, refactoring.
- **Fixed**: bug fix or crash fix.
- **Removed**: deprecated variable or parameter removal.

## Submitting a contribution

1. Check that no similar [issue](../../issues) or [PR](../../pulls) already exists.
2. Create a branch from the main branch.
3. Add tests for your changes.
4. Validate with the `openfisca-ai` commands above.
5. Update the `CHANGELOG.md`.
6. Submit your PR with a clear description.
