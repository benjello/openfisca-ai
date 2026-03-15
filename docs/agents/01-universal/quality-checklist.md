# Quality Checklist

Short pre-commit and pre-PR checklist for OpenFisca work.

Based on [principles.md](principles.md).

## Code

- no legal values hardcoded in Python
- correct entity and definition period
- vectorized logic (`where`, `max_`, `min_`) instead of Python loops
- no placeholder code or TODOs left behind
- naming consistent with the target country package

## Parameters

- `description`, `label`, `reference`, and unit metadata present
- simple parameters use `unit`
- scale parameters use `threshold_unit`, `rate_unit`, `amount_unit` when needed
- references are precise; PDF links include `#page=XX` when possible
- YAML hierarchy matches the country conventions

## Tests

- each meaningful formula is covered by tests
- nominal and edge cases are present
- manual reasoning is documented when it helps explain expected values
- target repository test suite passes

## Tooling

- package baseline is present: `pyproject.toml`, `units.yaml`, `entities.py`, `parameters/`, `variables/`, `tests/`
- formatting and linting match the target repository
- validation tools pass:

```bash
uv run python /path/to/openfisca-ai/tools/check_package_baseline.py .
uv run python /path/to/openfisca-ai/tools/validate_code.py .
uv run python /path/to/openfisca-ai/tools/validate_tests.py .
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
```

## Git and Review

- commit message is specific
- no unrelated files are included
- legal sources used for the change are documented
- residual risks or assumptions are stated clearly

## Minimal Review Command Set

```bash
uv run pytest
uv run python /path/to/openfisca-ai/tools/check_package_baseline.py .
uv run python /path/to/openfisca-ai/tools/validate_code.py .
uv run python /path/to/openfisca-ai/tools/validate_tests.py .
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
```

## See Also

- [principles.md](principles.md)
- [country-package-baseline.md](country-package-baseline.md)
- [development-workflow.md](development-workflow.md)
- [../02-framework/roles/](../02-framework/roles/)
