# Role: parameter-architect

Design the YAML parameter structure for an OpenFisca implementation.

This is a **method guide**, not a runtime agent already implemented in Python.

## Goal

Turn extracted legal values into a coherent parameter tree that fits the target country package.

## Inputs

- extracted rules
- country conventions from config
- existing country code and parameters

## Expected Output

- parameter files placed in the right hierarchy
- complete metadata
- no duplicated or unnecessary parameters

## Practical Workflow

1. list every value that should live in YAML
2. group values by domain and program
3. reuse existing naming when the target package already has a pattern
   - if the MCP server is running, use `list_parameters` and `get_parameter`
     to inspect the existing tree and avoid duplicating an existing parameter
     under a new name; otherwise rely on `extract-patterns` and grep
4. choose between:
   - simple parameter with `unit`
   - scale parameter with `brackets` and unit metadata
5. add metadata:
   - `description`
   - `label`
   - `reference`
   - `unit` or scale unit metadata
6. include history when known

## Minimum Checklist

- all legal values are parameterized
- hierarchy matches country conventions
- simple parameters use `unit`
- scale parameters use `threshold_unit`, `rate_unit`, `amount_unit` when relevant
- references are precise and include `#page=XX` for PDFs when possible
- no duplicate parameter already exists under another name

## Notes

- Prefer clarity over clever abstraction.
- If a value is derived from another legal parameter, document that dependency explicitly.
- Do not leave legal constants in Python when they belong in YAML.
