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

1. write at least one nominal test for each meaningful formula
2. add boundary cases:
   - exact threshold
   - just below / just above
   - zero or null cases where relevant
3. add scenario tests when multiple variables interact
4. document the expected result when it is not obvious
5. run the target repository test suite

## Minimum Checklist

- each implemented formula is exercised by tests
- threshold behavior is explicit
- scenario coverage exists when the formula depends on family or household structure
- expected values are justified when the math is not trivial
- tests pass in the target repository

## Notes

- Prefer a few precise tests over many vague ones.
- Use real legal reasoning, not unexplained magic numbers.
- If an official calculator exists, use it as an external comparison point when possible.
