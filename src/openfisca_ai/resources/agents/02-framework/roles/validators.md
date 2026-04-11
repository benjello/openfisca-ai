# Role: validators

Validation guidance for reviewing OpenFisca implementations.

This document describes a **methodological role**, not a set of runtime validator agents already implemented in Python.

## Scope

Use this role to review:

- parameter metadata quality
- Python implementation quality
- test completeness
- consistency with documented legal sources

## Core Checks

### Python code

- no legal hardcoded values
- correct entity choice
- vectorized logic instead of Python loops
- no obvious placeholders or TODOs
- formatting and linting aligned with the target repository

### YAML parameters

- description, label, reference, and unit metadata present
- scale parameters use `threshold_unit` / `rate_unit` / `amount_unit` when appropriate
- references are precise and preferably include `#page=XX` for PDFs
- hierarchy matches country conventions

### Tests

- each meaningful formula has tests
- nominal and edge cases are covered
- manual calculations or legal reasoning are documented when useful
- target repository test suite passes

## Practical Workflow

1. Run the full static audit first:
   ```bash
   uv run openfisca-ai audit .
   ```

2. For each failing variable, spot-check with a live calculation if the MCP server is running:
   ```
   calculate(situation)        # verify a specific scenario
   trace_calculation(situation) # understand why a result is wrong
   ```

3. Compare implementation to country conventions and legal source

4. Produce a concise review report with concrete fixes

## MCP saves tokens here

Static tools detect structural errors (missing metadata, wrong entity, no tests).
`calculate` and `trace_calculation` detect semantic errors (wrong formula logic, wrong parameter path).
Use static tools first — they're fast and offline. Use MCP for the cases that pass static checks but feel wrong.

## Recommended Commands

```bash
# Full audit (static)
uv run openfisca-ai audit .

# Individual checks
uv run openfisca-ai validate-code .
uv run openfisca-ai validate-tests .
uv run openfisca-ai validate-units .
uv run openfisca-ai validate-parameters .
uv run openfisca-ai check-package-baseline .
uv run openfisca-ai check-tooling .

# Tests
uv run pytest
```

## Suggested Report Structure

```markdown
## Findings

1. Missing legal reference in `parameters/...`
2. Hardcoded threshold in `variables/...`
3. Missing edge-case test for threshold equality

## Recommended Fixes

1. Move threshold to YAML parameter
2. Add reference with exact article and page
3. Add a test covering the boundary case
```

## Notes

- External tools like OpenFisca Control Center can help validate production repositories.
- If a check cannot be automated, state the residual risk clearly instead of pretending it passed.
