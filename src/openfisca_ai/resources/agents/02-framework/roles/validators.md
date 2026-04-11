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

1. read the relevant legal source or specification
2. inspect code, parameters, and tests together
3. compare implementation to country conventions
4. run validation tools and the repository test suite
5. produce a concise review report with concrete fixes

## Recommended Commands

In this repository:

```bash
uv run pytest
```

In the target OpenFisca country package:

```bash
uv run python /path/to/openfisca-ai/tools/check_package_baseline.py .
uv run python /path/to/openfisca-ai/tools/validate_code.py .
uv run python /path/to/openfisca-ai/tools/validate_tests.py .
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
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
