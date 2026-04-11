# Role: test-creator

Create tests for OpenFisca variables and scenarios.

This is a **method guide**, not a runtime agent already implemented in Python.

## Goal

Write tests that prove the implementation matches the intended legal rule and catches edge cases.

## Inputs

- implemented variables
- YAML parameters
- legal source or extracted rule summary
- examples from the target country package

## Expected Output

- variable-level tests
- scenario or integration tests when useful
- boundary-case coverage
- documented reasoning for expected values

## Practical Workflow

Test creation is the **clearest case for going MCP-only**: hand-computing
expected values is the most token-expensive thing an agent can do, and any
manual reconstruction risks diverging from what the live system computes.
See `openfisca-ai guide cat mcp` for the canonical MCP workflow.

### With MCP server running (recommended path)

1. Build the situation with inputs set and outputs set to `null`.
2. Validate the input structure:
   ```
   validate_situation(situation)
   ```
3. Get computed values with full trace:
   ```
   trace_calculation(situation)
   ```
4. Generate the YAML test, either from a saved file:
   ```bash
   uv run openfisca-ai generate-test-from-trace trace.json \
     --name test_my_variable \
     --reference "Article 12 du décret 2024-XXX" \
     --output tests/test_my_variable.yaml
   ```
   …or by piping the trace JSON directly through stdin:
   ```bash
   echo "$trace_json" | uv run openfisca-ai generate-test-from-trace - \
     --name test_my_variable \
     --output tests/test_my_variable.yaml
   ```
5. Review the generated test, add boundary cases by hand.

### Fallback: without an MCP server

1. Write at least one nominal test for each meaningful formula.
2. Add boundary cases: exact threshold, just below / just above, zero/null
   where relevant.
3. Document the expected result with the legal reasoning (manual calculation).
4. Run the target repository test suite.

This fallback is fine for trivial formulas, but for anything non-trivial the
MCP path produces tests that are both faster to write **and** correct by
construction.

## Minimum Checklist

- each implemented formula is exercised by tests
- threshold behavior is explicit
- scenario coverage exists when the formula depends on family or household structure
- expected values are justified when the math is not trivial
- tests pass in the target repository

## Recommended Verification

```bash
uv run pytest
uv run openfisca-ai validate-tests .
```

## Notes

- Prefer a few precise tests over many vague ones.
- Use real legal reasoning, not unexplained magic numbers.
- If an official calculator exists, use it as an external comparison point when possible.
- The trace summary in generated tests documents intermediate values — keep it as a comment.
