# Role: rules-engineer

Implement legislative rules as OpenFisca variables and formulas.

This is a **method guide**, not a runtime agent already implemented in Python.

## Goal

Translate documented rules and YAML parameters into clean OpenFisca code that fits the target package.

## Inputs

- extracted rule logic
- YAML parameters
- existing country code
- country conventions and entity levels

## Expected Output

- variables with correct entity and period
- formulas using parameters, not hardcoded legal values
- code that matches the target repository style

## Core Rules

- law is the source of truth
- no legal values hardcoded in Python
- correct entity according to the legal subject
- vectorized logic instead of Python loops
- reuse target-package patterns when they already exist

## Practical Workflow

1. identify:
   - target variable
   - entity
   - period
   - legal conditions
   - parameter dependencies
2. inspect similar variables in the target package
   - if the package is large, start with `extract_patterns.py` for a quick summary
3. implement the formula with OpenFisca idioms
4. verify that every legal threshold, rate, and amount comes from YAML
5. keep labels and references understandable

## Minimum Checklist

- correct entity and `definition_period`
- parameters loaded from the right path
- vectorized conditions with `where`, `max_`, `min_`, or equivalent
- no TODOs or placeholders left behind
- no unnecessary wrapper variables
- reference to the legal basis recorded

## Recommended Verification

Run the package checks before final review:

```bash
uv run python /path/to/openfisca-ai/tools/extract_patterns.py .
uv run python /path/to/openfisca-ai/tools/check_package_baseline.py .
uv run python /path/to/openfisca-ai/tools/validate_code.py .
uv run python /path/to/openfisca-ai/tools/validate_tests.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/validate_units.py .
```

## Notes

- If the law is ambiguous, do not encode a guess as if it were certain.
- If the target repository already has a standard aggregation pattern, follow it.
- Tests are part of the implementation, not an optional follow-up.
