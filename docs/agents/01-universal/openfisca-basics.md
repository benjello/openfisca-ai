# OpenFisca Basics

Quick guide to OpenFisca concepts for AI agents.

## Key Concepts

### 1. Variables

A **variable** represents data (income, age) or a calculation result (benefit amount, tax).

```python
from openfisca_core.variables import Variable
from openfisca_core.periods import MONTH

class housing_allowance(Variable):
    value_type = float
    entity = Family
    definition_period = MONTH
    label = "Housing allowance"
    reference = "Social Benefits Act 2020, Section 12"

    def formula(family, period, parameters):
        income = family('disposable_income', period)
        ceiling = parameters(period).social_benefits.housing_allowance.income_ceiling
        base_amount = parameters(period).social_benefits.housing_allowance.base_amount

        from numpy import where
        eligible = income < ceiling
        return where(eligible, base_amount, 0)
```

**Variable types**:
- `float`: amounts, rates
- `int`: counters, ages
- `bool`: eligibility, conditions
- `Enum`: statuses (married/single, employed/unemployed)
- `date`: birth dates, events

**See**: [country-template/variables/](../country-template/variables/)

### 2. Entities

**Entities** are the levels at which rules apply.

```python
# Common levels (hierarchical order)
Person      # Individual
Family      # Family (family relationships)
Household   # Household (shared residence)
TaxUnit     # Tax unit (tax filing)
```

**Hierarchy**: A person belongs to a family, which belongs to a household, etc.

### 3. Parameters

**Parameters** store legal values (rates, ceilings, brackets) in YAML files.

```yaml
# parameters/social_benefits/housing_allowance/base_amount.yaml
description: Base monthly housing allowance amount
label: Base amount
reference: "Social Benefits Act 2020, Section 12"
unit: CUR
values:
  2020-01-01: 200
  2024-01-01: 220
```

**Access in code**:
```python
base_amount = parameters(period).social_benefits.housing_allowance.base_amount
```

**See**: [country-template/parameters/](../country-template/parameters/)

### 4. Periods

**Periods** define when a variable is calculated.

```python
definition_period = MONTH   # Monthly
definition_period = YEAR    # Annual
definition_period = ETERNITY  # Permanent (e.g., birth date)
```

**Automatic conversion**:
```python
# Variable defined as MONTH
annual_salary = person('salary', period.this_year)  # Sums 12 months
january_salary = person('salary', '2024-01')
```

### 5. Formulas

The **formula** calculates the variable's value.

```python
def formula(family, period, parameters):
    # family() : access other family variables
    # period : calculation period
    # parameters(period) : access legal parameters

    income = family('disposable_income', period)
    ceiling = parameters(period).social_benefits.housing_allowance.income_ceiling

    from numpy import minimum as min_
    return min_(income, ceiling)
```

### 6. Entity Aggregations

**From Person to Family**:
```python
class family_income(Variable):
    value_type = float
    entity = Family
    definition_period = MONTH

    def formula(family, period):
        # Sum income of all members
        return family.sum(family.members('salary', period))
```

**From Family to Person**:
```python
class allowance_per_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH

    def formula(person, period):
        # Family allowance, projected to each member
        family_allowance = person.family('housing_allowance', period)
        return family_allowance / person.family.nb_persons()
```

**Aggregation functions**:
- `family.sum()`: sum
- `family.all()`: all true (AND)
- `family.any()`: at least one true (OR)
- `family.max()`, `family.min()`

**See**: [country-template/variables/family_benefits.py](../country-template/variables/family_benefits.py)

### 7. Vectorized Operations

OpenFisca uses NumPy for performance.

```python
from numpy import where, maximum as max_, minimum as min_

# Conditions
eligible = (income < ceiling) * (nb_children > 0)
amount = where(eligible, calculate_amount, 0)

# Min/Max
capped_income = min_(income, ceiling)
minimum_amount = max_(calculated_amount, floor_amount)

# Multiple selection
from openfisca_core.indexed_enums import select
result = select(
    [case_1, case_2, case_3],
    [amount_1, amount_2, amount_3],
    default=0
)
```

### 8. Tax Brackets

For progressive calculations (taxes, benefits by bracket).

```yaml
# parameters/taxation/income_tax/tax_brackets.yaml
type: marginal_rate
brackets:
  - threshold: 0
    rate: 0
  - threshold: 10000
    rate: 0.10
  - threshold: 25000
    rate: 0.20
```

```python
def formula(tax_unit, period, parameters):
    taxable_income = tax_unit('taxable_income', period)
    brackets = parameters(period).taxation.income_tax.tax_brackets
    return brackets.calc(taxable_income)
```

**Bracket types**:
- `marginal_rate`: marginal rate (progressive tax)
- `single_amount`: fixed amount per bracket
- `marginal_amount`: progressive amount

**See**: [country-template/variables/income_tax.py](../country-template/variables/income_tax.py)

### 9. Conditional Definition

Limit a variable to certain periods:

```python
class covid_relief(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    defined_for = "2020-03 <= period <= 2020-12"  # Only Mar-Dec 2020
```

### 10. Metadata

```python
class unemployment_benefit(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Unemployment benefit"
    reference = "Labor Code, Article L5422-1"
    set_input = set_input_divide_by_period  # Divide annual input to monthly
```

### 11. Country Package Baseline

OpenFisca code usually lives in a country package with a stable layout:

```text
openfisca_<country>/
├── entities.py
├── units.yaml
├── parameters/
├── variables/
├── reforms/
└── situation_examples/

tests/
pyproject.toml
Makefile
```

This repository layout is common enough that agents should assume it by
default, then adapt only when the target package clearly differs.

See [country-package-baseline.md](country-package-baseline.md) for the
recommended baseline shared by `country-template`-style packages and modern
packages such as `openfisca-tunisia`.

## Naming Conventions

### Variables (Python)
```python
housing_allowance       # snake_case
number_of_children
taxable_income
```

### Parameters (YAML)
```yaml
# Hierarchy by domain
social_benefits/
  housing_allowance/
    income_ceiling.yaml
    base_amount.yaml
  family_benefits/
    child_allowance.yaml
taxation/
  income_tax/
    tax_brackets.yaml
```

## Resources

- [OpenFisca Documentation](https://openfisca.org/doc/)
- [OpenFisca Core](https://github.com/openfisca/openfisca-core)
- Examples: [country-template](../country-template/)
- Country repos: [openfisca-france](https://github.com/openfisca/openfisca-france), [openfisca-tunisia](https://github.com/openfisca/openfisca-tunisia)
- Shared package structure: [country-package-baseline.md](country-package-baseline.md)

---

**Next steps**:
- Read [principles.md](principles.md) for universal rules
- Consult [../02-framework/roles/](../02-framework/roles/) for agent guides
