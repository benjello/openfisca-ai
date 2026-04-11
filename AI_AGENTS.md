# OpenFisca AI Agent Guide

Instructions for coding assistants working with this repository and OpenFisca country packages.

## Purpose

This repository currently has two distinct layers:

- **Stable**: validation tools and configuration helpers
- **Alpha**: agent runtime and `law_to_code` pipeline scaffolding

Do not assume the runtime can already perform a full end-to-end implementation from legislation to production-ready OpenFisca code.

## Read Order

Guides are packaged under `src/openfisca_ai/resources/agents/` and accessible
via the `openfisca-ai guide` CLI from any project depending on openfisca-ai:

```bash
uv run openfisca-ai guide list                # list available guides
uv run openfisca-ai guide cat principles      # read a guide
uv run openfisca-ai guide show test-creator   # absolute path
```

Recommended reading:

1. `principles` — non-negotiable rules
2. `openfisca-basics` — variables, entities, parameters
3. `quality-checklist` — pre-commit checks
4. `country-config` — config loading
5. Role guide: `document-collector`, `parameter-architect`, `rules-engineer`,
   `test-creator`, `validators`
6. Country specifics: `03-countries/<country>/specifics`

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
- Autonomous validation tools (in `tools/`, exposed via the CLI)
- Methodology guides packaged in the wheel and accessible via `openfisca-ai guide`
- **MCP server** wrapping a running OpenFisca Web API (`openfisca-ai mcp`) — see dedicated section below
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

Typical mapping (read with `openfisca-ai guide cat <name>`):

- collecting sources -> `document-collector`
- designing parameter trees -> `parameter-architect`
- implementing formulas -> `rules-engineer`
- creating tests -> `test-creator`
- reviewing quality -> `validators`

## MCP Server — live access to a target OpenFisca system

When an OpenFisca country package is served via its Web API
(`openfisca serve`), openfisca-ai can expose it as MCP tools usable by agents:

```bash
# Start the OpenFisca API and the MCP server in one command
uv run openfisca-ai mcp --serve

# Or, if the API is already running elsewhere
uv run openfisca-ai mcp --url http://localhost:5000
```

Tools exposed (see `src/openfisca_ai/mcp/server.py` for the canonical list):

- `list_entities`, `list_variables`, `list_parameters` — explore the system
- `search_variables` — keyword search across names and descriptions
- `describe_variable` — entity, period, formula, legal references
- `get_parameter` — values and full historical dates
- `validate_situation` — structural validation before computing
- `calculate` — compute variables for a situation
- `trace_calculation` — compute + return the full dependency tree and
  intermediate values; pipe its output to `openfisca-ai generate-test-from-trace`
  to produce a YAML test in one step

**When to prefer MCP over static tools:**

- `audit` / `validate-*` first: structural errors, offline, free, fast
- MCP next: semantic errors (wrong formula, wrong parameter path), needs a
  live API; also the canonical way to ground test fixtures in real values
  rather than hand-computed estimates

The role guides (`rules-engineer`, `test-creator`, `validators`) document the
MCP workflow per role.

## Practical Expectation

If asked to implement legislation today, the reliable workflow is:

1. load config
2. read the relevant docs
3. use existing country code as reference
4. edit the target OpenFisca package directly
5. run validation tools and tests

Do not present this repo as if it already contains a complete autonomous multi-agent system.
