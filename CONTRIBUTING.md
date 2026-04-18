# Contributing to openfisca-ai

Thank you for your interest in contributing to the OpenFisca AI toolkit!

## Development setup

```bash
git clone https://github.com/benjello/openfisca-ai.git
cd openfisca-ai
uv sync
```

## Running tests

```bash
uv run pytest
```

## Project structure

```
src/openfisca_ai/
  agents/       # AI agent definitions
  core/         # Orchestrator, LLM engine, artifacts
  mcp/          # MCP server & client
  pipelines/    # Law-to-code pipeline
  resources/    # Guides, country templates, reusable templates
  skills/       # Extract law, generate code
  tools/        # CLI validation tools (validate-parameters, validate-units, etc.)
```

## Code style

- Python 3.10+.
- Prefer type hints for public APIs.
- Keep modules focused; add new agents/skills under `src/openfisca_ai/`.
- No hardcoded values — configuration lives in YAML or JSON files.

## Adding a new validation tool

1. Create the tool under `src/openfisca_ai/tools/`.
2. Register it as a CLI subcommand in `cli.py`.
3. Add tests in `tests/`.
4. Document the tool in the README.

## Adding reusable templates

Country-package templates (CONTRIBUTING, issue/PR templates) live in
`src/openfisca_ai/resources/templates/`. Each template is provided in French
(`.fr.md`) and English (`.en.md`) with `{{project_name}}` and `{{project_slug}}`
placeholders. See the [templates README](src/openfisca_ai/resources/templates/README.md).

## Changelog format

The [CHANGELOG.md](CHANGELOG.md) follows the Keep a Changelog convention:

- **Added**: new features, new tools.
- **Changed**: updates to existing functionality.
- **Fixed**: bug fixes.
- **Removed**: deprecated feature removal.

## Submitting a contribution

1. Check that no similar [issue](../../issues) or [PR](../../pulls) exists.
2. Branch from `main`, make your changes, add tests if applicable.
3. Ensure tests pass and the CLI still runs: `uv run openfisca-ai --help`.
4. Update the `CHANGELOG.md`.
5. Submit a PR with a clear description of the change.
