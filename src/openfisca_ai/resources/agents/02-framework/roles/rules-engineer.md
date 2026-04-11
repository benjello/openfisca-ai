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

For implementation work, **MCP-first** is more efficient than static-first:
exploring the existing system through MCP saves more agent context than
running static validation tools you don't yet have anything to validate. See
`openfisca-ai guide cat mcp` for the task-based strategy and the full tool
list.

1. **Explore what already exists** — before writing anything:

   If the MCP server is running:
   ```
   search_variables("keyword")          # find related variables
   describe_variable("variable_name")   # get entity, period, formula, references
   list_parameters                      # check existing parameter hierarchy
   get_parameter("path.to.param")       # verify current values
   ```

   `describe_variable` replaces reading the Python file + tracing imports.
   `search_variables` replaces grepping the codebase. `get_parameter`
   replaces walking the YAML hierarchy manually.

   If the MCP server is not running:
   ```bash
   uv run openfisca-ai extract-patterns .
   ```

2. **Identify** target variable, entity, period, legal conditions, parameter dependencies

3. **Implement** the formula with OpenFisca idioms

4. **Verify** every legal threshold, rate, and amount comes from YAML

5. **Keep** labels and references understandable

6. **Run static validation at the end** — see "Recommended Verification" below.

## Minimum Checklist

- correct entity and `definition_period`
- parameters loaded from the right path
- vectorized conditions with `where`, `max_`, `min_`, or equivalent
- no TODOs or placeholders left behind
- no unnecessary wrapper variables
- reference to the legal basis recorded

## Recommended Verification

```bash
uv run openfisca-ai validate-code .
uv run openfisca-ai validate-parameters .
uv run openfisca-ai validate-units .
uv run openfisca-ai check-package-baseline .
```

## Notes

- If the law is ambiguous, do not encode a guess as if it were certain.
- If the target repository already has a standard aggregation pattern, follow it.
- Tests are part of the implementation, not an optional follow-up.
