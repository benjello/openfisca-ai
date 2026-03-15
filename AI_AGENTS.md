# OpenFisca AI Agent Guide

Instructions for coding assistants working with this repository and OpenFisca country packages.

## Purpose

This repository currently has two distinct layers:

- **Stable**: validation tools and configuration helpers
- **Alpha**: agent runtime and `law_to_code` pipeline scaffolding

Do not assume the runtime can already perform a full end-to-end implementation from legislation to production-ready OpenFisca code.

## Read Order

1. [`docs/agents/01-universal/principles.md`](docs/agents/01-universal/principles.md)
2. [`docs/agents/01-universal/openfisca-basics.md`](docs/agents/01-universal/openfisca-basics.md)
3. [`docs/agents/01-universal/quality-checklist.md`](docs/agents/01-universal/quality-checklist.md)
4. [`docs/agents/02-framework/country-config.md`](docs/agents/02-framework/country-config.md)
5. Relevant file in [`docs/agents/02-framework/roles/`](docs/agents/02-framework/roles/)
6. Country-specific doc in [`docs/agents/03-countries/`](docs/agents/03-countries/) when applicable

## Non-Negotiable Rules

- Law is the source of truth.
- No legal values hardcoded in Python.
- Parameters need metadata and units.
- Variables need tests.
- Use OpenFisca-style vectorized logic.
- Respect country conventions from config.

## Current Repository Reality

### What works today

- Config loading from [`config/countries/`](config/countries/) plus local overrides in `config/user.yaml`
- Validation tools in [`tools/`](tools/)
- Minimal CLI entrypoint: `uv run openfisca-ai run <task.json>`

### What is not complete

- `ExtractorAgent` and `CoderAgent` are still placeholders
- `law_to_code` does not generate production-ready OpenFisca artifacts
- No orchestrated slash-commands like `/encode-policy`, `/review-pr`, `/fix-pr`

## Configuration

Load country config with:

```python
from openfisca_ai.config_loader import load_country_config, get_reference_code_path

config = load_country_config("tunisia")
reference_code_path = get_reference_code_path("tunisia")
```

Use local config overrides in `config/user.yaml` with the canonical schema:

```yaml
countries:
  tunisia:
    existing_code:
      path: /path/to/openfisca-tunisia
    legislative_sources:
      root: /path/to/tunisia-laws
```

## Recommended Commands

```bash
uv sync --dev
uv run python config/test_config.py
uv run pytest
uv run openfisca-ai run tasks/example_task.json
```

For OpenFisca country packages:

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
```

## How To Work As An Agent

Treat the role documents as **guidance**, not as proof that a runtime agent for that role exists in code.

Typical mapping:

- collecting sources -> [`document-collector.md`](docs/agents/02-framework/roles/document-collector.md)
- designing parameter trees -> [`parameter-architect.md`](docs/agents/02-framework/roles/parameter-architect.md)
- implementing formulas -> [`rules-engineer.md`](docs/agents/02-framework/roles/rules-engineer.md)
- creating tests -> [`test-creator.md`](docs/agents/02-framework/roles/test-creator.md)
- reviewing quality -> [`validators.md`](docs/agents/02-framework/roles/validators.md)

## Practical Expectation

If asked to implement legislation today, the reliable workflow is:

1. load config
2. read the relevant docs
3. use existing country code as reference
4. edit the target OpenFisca package directly
5. run validation tools and tests

Do not present this repo as if it already contains a complete autonomous multi-agent system.
