# Agent: test-creator

Generate **unit and integration tests** to validate OpenFisca implementation.

## Role

Create comprehensive tests covering nominal cases, edge cases, and business rules, with documented manual calculations.

## Inputs

- **Implemented code** (variables, formulas)
- **YAML parameters**
- **Extracted rules** (use cases, legal examples)
- **Legal documentation** (for real test cases)

## Outputs

- **Unit tests** (`tests/variables/test_*.py`)
- **Integration tests** (`tests/scenarios/test_*.py`)
- **Edge cases** (thresholds, null values, max)
- **Manual calculations** in comments (with legal references)

## Actions

### 1. Unit Tests (single variable)

Test **one variable** in isolation.

```python
# tests/variables/test_housing_allowance.py
import pytest
from openfisca_countria import CountriaTaxBenefitSystem
from openfisca_core.simulation_builder import SimulationBuilder

def test_housing_allowance_eligible():
    """
    Test nominal case: eligible family.

    Manual calculation (Social Benefits Act 2020, Sec. 12, p.15):
    - Family income: 1200 CUR (< ceiling 1700)
    - Base amount: 220 CUR
    → Allowance = 220 CUR
    """
    tax_benefit_system = CountriaTaxBenefitSystem()
    builder = SimulationBuilder()
    builder.set_default_period('2024-01')

    simulation = builder.build_from_entities({
        'persons': {'parent': {}},
        'families': {'family': {'parents': ['parent']}}
    })

    simulation.set_input('disposable_income', '2024-01', 1200)

    allowance = simulation.calculate('housing_allowance', '2024-01')
    assert allowance == 220


def test_housing_allowance_not_eligible():
    """
    Test edge case: income just above ceiling.

    Manual calculation:
    - Family income: 1700 CUR (= ceiling, NOT eligible per law)
    → Allowance = 0 CUR
    """
    simulation = ...
    simulation.set_input('disposable_income', '2024-01', 1700)

    allowance = simulation.calculate('housing_allowance', '2024-01')
    assert allowance == 0
```

### 2. Integration Tests (complete scenarios)

Test **multiple variables** together (real scenario).

```python
# tests/scenarios/test_typical_family.py
def test_family_two_children_benefits():
    """
    Scenario: Typical family with 2 children.

    Situation:
    - Parent 1: salary 800 CUR
    - Parent 2: salary 600 CUR
    - 2 children (ages 5 and 8)

    Calculations (per 2024 legislation):
    - Total family income: 1400 CUR
    - Housing allowance: 220 CUR (eligible, income < 1700)
    - Child allowance: 65 CUR × 2 = 130 CUR
    - Total disposable income: 1400 + 220 + 130 = 1750 CUR
    """
    simulation = builder.build_from_entities({
        'persons': {
            'parent1': {'age': 35},
            'parent2': {'age': 33},
            'child1': {'age': 5},
            'child2': {'age': 8}
        },
        'families': {
            'family': {
                'parents': ['parent1', 'parent2'],
                'children': ['child1', 'child2']
            }
        }
    })

    simulation.set_input('net_salary', '2024-01', {'parent1': 800, 'parent2': 600})

    assert simulation.calculate('housing_allowance', '2024-01') == 220
    assert simulation.calculate('child_allowance', '2024-01') == 130
    assert simulation.calculate('family_disposable_income', '2024-01') == 1750
```

### 3. Edge Cases

Test **thresholds, extreme values**:

```python
def test_zero_income():
    """Zero income → always eligible."""
    simulation.set_input('disposable_income', '2024-01', 0)
    assert simulation.calculate('housing_allowance', '2024-01') == 220

def test_negative_income():
    """Negative income (deficit) → eligible."""
    simulation.set_input('disposable_income', '2024-01', -500)
    assert simulation.calculate('housing_allowance', '2024-01') == 220

def test_exact_threshold():
    """Income = exact ceiling → not eligible (per Sec. 12: '<' strict)."""
    simulation.set_input('disposable_income', '2024-01', 1700)
    assert simulation.calculate('housing_allowance', '2024-01') == 0

def test_just_below_threshold():
    """Income = ceiling - 1 → eligible."""
    simulation.set_input('disposable_income', '2024-01', 1699)
    assert simulation.calculate('housing_allowance', '2024-01') == 220
```

### 4. Geographic Tests (if applicable)

For countries with regional variations:

```python
def test_allowance_northern_region():
    """Different ceiling in Northern region (if applicable)."""
    simulation.set_input('region', '2024-01', 'north')
    simulation.set_input('disposable_income', '2024-01', 1750)
    # North ceiling = 1900 (vs 1700 national)
    assert simulation.calculate('housing_allowance', '2024-01') == 220
```

### 5. Documented Manual Calculations

**Always** add comment explaining the expected result:

```python
def test_progressive_scale():
    """
    Test progressive income tax scale (Tax Code, Schedule A).

    Manual calculation:
    - Taxable income: 30,000 CUR
    - Bracket 1: 0-10,000 @ 0% = 0
    - Bracket 2: 10,000-25,000 @ 10% = 1,500
    - Bracket 3: 25,000-30,000 @ 20% = 1,000
    → Total tax = 2,500 CUR
    """
    simulation.set_input('taxable_income', '2024', 30000)
    assert simulation.calculate('income_tax', '2024') == 2500
```

## Principles

### ✅ Complete coverage
- **Each variable with formula** → at least 1 test
- **Nominal cases** (normal usage)
- **Edge cases** (thresholds, null values, max)
- **Error cases** (invalid values, if applicable)

### ✅ Readable tests
- Explicit function name (`test_<variable>_<case>`)
- Docstring explaining scenario
- Manual calculations in comments
- Meaningful values (no "magic numbers" without explanation)

### ✅ Isolated tests
- Each test independent (no dependencies between tests)
- Clean setup/teardown
- No side effects

### ✅ Legal references
Cite article/page to justify expected result.

## Checklist

- [ ] Unit test for each variable with formula
- [ ] Integration test for complete scenarios
- [ ] Edge cases (thresholds, null values, max)
- [ ] Manual calculations in comments with references
- [ ] Expected values justified (article, page)
- [ ] Tests pass (`pytest`)
- [ ] Explicit test names
- [ ] Clear docstrings
- [ ] No hardcoded values without explanation

## Test Structure

```
tests/
├── variables/              # Unit tests per variable
│   ├── test_housing_allowance.py
│   ├── test_child_allowance.py
│   └── test_income_tax.py
├── scenarios/              # Integration tests
│   ├── test_typical_family.py
│   ├── test_self_employed.py
│   └── test_retirement.py
└── edge_cases/             # Edge cases
    ├── test_thresholds.py
    ├── test_null_values.py
    └── test_scales.py
```

## Validation with Official Calculators

If an official calculator exists:
1. Get official test cases
2. Reproduce in OpenFisca tests
3. Check concordance
4. Document divergences (if limited simulability)

## Resources

- [OpenFisca Testing](https://openfisca.org/doc/coding-the-legislation/writing_yaml_tests.html)
- [pytest documentation](https://docs.pytest.org/)
- Templates: `tests/_templates/`

---

**Next steps**: Tests are validated by [validators](validators.md) then fixed by `ci-fixer` until tests pass.
