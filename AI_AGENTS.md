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

Role guides are **method patterns**, not exclusive identities. A single task
("implement variable X") usually runs several patterns in sequence:

1. `document-collector` — find legal sources
2. `parameter-architect` — lay out parameter YAML
3. `rules-engineer` — write the formula
4. `test-creator` — produce YAML tests
5. `validators` — audit the result

You don't have to "pick a role". Apply the patterns in the order that fits
the task. Skipping steps is fine when they are already done.

Read with `uv run openfisca-ai guide cat <name>`.

## MCP Server

The MCP server exposes a running OpenFisca system as a set of tools
(exploration, calculation, trace).

**Single source of truth**: `uv run openfisca-ai guide cat mcp`. That guide
lists the tools, the startup cost, and the **task-based** strategy for
choosing between static tools and MCP — the oversimplified "static first"
rule only fits audit work; for implementation or test generation, MCP wins.

Quickstart:

```bash
uv run openfisca-ai mcp --serve \
  --serve-command "uv run openfisca serve --country-package openfisca_<country>"
```

In a project with a `.mcp.json`, Claude Code auto-discovers the server.

## Practical Expectation

If asked to implement legislation today, the reliable workflow is:

1. load config
2. read the relevant docs
3. use existing country code as reference
4. edit the target OpenFisca package directly
5. run validation tools and tests

Do not present this repo as if it already contains a complete autonomous multi-agent system.
