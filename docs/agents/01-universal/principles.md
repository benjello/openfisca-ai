# Universal Principles - OpenFisca AI

These principles apply to **all agents**, **all countries**, **all tasks**.

**Validated by**: Analysis of openfisca-tunisia (439 parameters, 40 variables, history since 1959).

---

## The 14 Universal Principles

### Group 1: Source and Truth (3)

#### 1. Law is the source of truth

**Always** refer to official texts (laws, decrees, regulations, manuals).

❌ **Never** guess a rule or value
✅ **Always** search for the source before implementing

**Workflow**:
1. **Search** for texts (document-collector)
2. **Extract** structured rules (extractor)
3. **Implement** faithfully (rules-engineer)
4. **Verify** compliance (validators)

**Example**:
```python
# ✅ GOOD
reference = "Social Benefits Act 2020, Section 12"
```

---

#### 2. No hardcoded values

**No** legal values in Python code.
**All** values come from **parameters** (YAML files).

**Exceptions**: 0, 1, and period conversions (4 quarters, 12 months) if documented.

**❌ BAD**:
```python
def formula(family, period):
    return family('income', period) * 0.25  # Hardcoded value!
```

**✅ GOOD**:
```python
def formula(family, period, parameters):
    rate = parameters(period).social_benefits.housing_allowance.rate
    return family('income', period) * rate
```

**See**: [country-template/variables/housing_allowance.py](../country-template/variables/housing_allowance.py)

---

#### 3. Precise references

- **URLs** with `#page=XX` for PDFs
- **Exact citations** (law, article, date)
- **Verifiable sources**

**Example**:
```yaml
reference:
  - "Social Benefits Act 2020, Section 12"
  - "https://example.gov/social-benefits-act.pdf#page=15"  # ✅ With #page=XX
```

**See**: [country-template/parameters/social_benefits/](../country-template/parameters/social_benefits/)

---

### Group 2: Parameters (4)

#### 4. Well-documented parameters

**Required metadata**:
- `description`: One clear sentence
- `label`: Short name for UI
- `reference`: URL or legal citation
- `unit`: **MANDATORY** - `/1`, `EUR`, `TND`, `CUR`, etc.

**For scales/brackets (barèmes)**: Use specific unit fields in `metadata`:
- `threshold_unit`: Unit for bracket thresholds
- `rate_unit`: Unit for rates
- `amount_unit`: Unit for amounts (if applicable)

**IMPORTANT**: ALL packages MUST have a `units.yaml` file (at package root) defining all units used.

**Example simple parameter**:
```yaml
income_ceiling:
  description: Monthly income ceiling for housing allowance eligibility
  label: Income ceiling
  reference:
    - "Social Benefits Act 2020, Section 12"
    - "https://example.gov/social-benefits-act.pdf#page=15"
  unit: CUR
  values:
    2020-01-01: 1500
    2024-01-01: 1700
```

**Example scale/bracket parameter**:
```yaml
tax_scale:
  description: Progressive income tax scale
  label: Income tax scale
  reference:
    - "Tax Code 2020, Article 45"
  brackets:
    - threshold:
        2020-01-01: 0
      rate:
        2020-01-01: 0.0
    - threshold:
        2020-01-01: 10000
      rate:
        2020-01-01: 0.15
    - threshold:
        2020-01-01: 50000
      rate:
        2020-01-01: 0.30
  metadata:
    threshold_unit: CUR
    rate_unit: /1
```

**Example units.yaml** (required in all packages):
```yaml
# openfisca_<country>/units.yaml
# Define all units used in this country package

- name: /1
  label:
    one: percent
    other: percents
  ratio: true
  short_label: "%"

- name: CUR
  label:
    one: Countria currency unit
    other: Countria currency units
  short_label: Ꞓ

- name: month
  label: months

- name: year
  label:
    one: year
    other: years
  short_label:
    one: yr
    other: yrs
```

**See**: [country-template/parameters/social_benefits/housing_allowance/income_ceiling.yaml](../country-template/parameters/social_benefits/housing_allowance/income_ceiling.yaml)

---

#### 5. Complete history

- **Preserve** all past values
- **Enables** retrospective simulations
- **Format**: `date: value`

**Example**:
```yaml
minimum_wage:
  values:
    2015-01-01: 800   # Complete history
    2018-01-01: 850
    2020-01-01: 900
    2024-01-01: 1000  # Current value
```

**See**: [country-template/parameters/labor_market/minimum_wage.yaml](../country-template/parameters/labor_market/minimum_wage.yaml)

---

#### 6. Indexed values

- **Indexation** on reference (minimum wage, inflation) → `unit: <reference>`
- **Automatic** evolution with reference
- **Alternative**: `formula` in YAML

**Example**:
```yaml
income_ceiling:
  description: Ceiling indexed on minimum wage (1.7 × minimum_wage)
  unit: minimum_wage  # ✅ Indexed value
  metadata:
    indexed_on: minimum_wage
    indexation_factor: 1.7
```

**Pattern**: If parameter derived from reference → `unit: <reference>` acceptable.

---

#### 7. Extensible metadata

- **Standard**: description, label, reference, unit
- **Custom**: Additional fields as needed
- **Examples**: `indexed_on`, `max_children`, `note`

**Example**:
```yaml
child_allowance:
  description: Monthly child allowance per child
  unit: CUR
  values:
    2024-01-01: 65
  metadata:
    max_children: 3  # ✅ Custom metadata
    note: "Maximum 3 children counted"
```

**See**: [country-template/parameters/social_benefits/family_benefits/child_allowance.yaml](../country-template/parameters/social_benefits/family_benefits/child_allowance.yaml)

---

### Group 3: Code (4)

#### 8. Correct entities

- **According to law**: Person, Family, Household, TaxUnit
- **Verify** which level receives/calculates the benefit
- **Don't guess**

**Example**:
```python
class housing_allowance(Variable):
    value_type = float
    entity = Family  # ✅ Law says "families receive"
    definition_period = MONTH
    label = "Housing allowance"
```

**See**: [country-template/variables/housing_allowance.py](../country-template/variables/housing_allowance.py)

---

#### 9. Vectorization

- **where()**, **max_()**, **min_()** instead of loops
- **NumPy** for performance
- **No** explicit `for` or `if`

**❌ BAD**:
```python
for person in persons:
    if person.age > 18:
        result[person] = calculate(person)
```

**✅ GOOD**:
```python
from numpy import where

eligible = age > 18
result = where(eligible, calculate(...), 0)
```

**See**: [country-template/variables/housing_allowance.py](../country-template/variables/housing_allowance.py#L32)

---

#### 10. Period conversions acceptable

- **4** (quarters), **12** (months) acceptable
- **Document** in comment
- **Not** a legal value (mathematical conversion)

**Example**:
```python
# ✅ ACCEPTABLE
return 4 * quarterly_amount  # 4 quarters in a year
return 12 * monthly_amount   # 12 months in a year
```

**Principle**: Mathematical period conversions (0, 1, 4, 12) acceptable if documented.

---

#### 11. No TODOs in production

- **New code**: Zero TODOs
- **Legacy code**: Clean progressively
- **Principle**: Complete code or don't commit

**❌ BAD**:
```python
def formula(...):
    # TODO: add eligibility check
    return amount
```

**✅ GOOD**:
```python
def formula(...):
    eligible = income < ceiling  # Complete
    return where(eligible, amount, 0)
```

---

### Group 4: Quality (3)

#### 12. Systematic tests

- **Every variable** with formula → test
- **Nominal cases** + **edge cases**
- **Manual calculations** in comments

**Example**:
```python
def test_housing_allowance_eligible():
    """
    Test nominal case: eligible family.

    Manual calculation (Social Benefits Act 2020, Section 12, page 15):
    - Family income: 1200 CUR (< ceiling 1700)
    - Base amount: 220 CUR (2024 value)
    → Housing allowance = 220 CUR
    """
    simulation.set_input('disposable_income', '2024-01', 1200)
    assert simulation.calculate('housing_allowance', '2024-01') == 220
```

**See**: [country-template/tests/test_housing_allowance.py](../country-template/tests/test_housing_allowance.py)

---

#### 13. Pattern reuse

- **Study** existing country code
- **Reuse** consistent patterns
- **Avoid** duplication

**Examples**:
- Pattern: Eligibility based on income
- Pattern: Progressive tax brackets
- Pattern: Family aggregation (Person → Family)

**See**: Country-specific patterns in [03-countries/](../03-countries/)

---

#### 14. Formatting and Naming

- **Python**: Black or **Ruff** (modern all-in-one formatter/linter)
  - Black: `black src/`
  - Ruff: `ruff format src/` + `ruff check src/` (recommended for new projects)
- **YAML**: Prettier or yamllint
- **Naming**: **snake_case** (universal OpenFisca convention)
  - Variables: `housing_allowance`, `disposable_income`
  - Parameters: `income_ceiling`, `base_amount`
  - Files: `housing_allowance.py`, `test_housing_allowance.py`
- **Consistency** across all countries

**Examples**:
```python
# ✅ GOOD - snake_case
class housing_allowance(Variable):
    ...

class disposable_income(Variable):
    ...
```

```python
# ❌ BAD - camelCase or other
class HousingAllowance(Variable):  # Wrong
    ...

class disposableIncome(Variable):  # Wrong
    ...
```

```bash
# Format code (choose one)
black src/                    # Traditional
ruff format src/              # Modern (recommended)

# Lint (ruff only)
ruff check src/ --fix         # Auto-fix issues

# Format YAML
prettier --write config/
```

**Note**: `snake_case` is a **universal** OpenFisca convention, not a country-specific choice. Migration to Ruff is recommended for new projects.

---

## Summary Table

| Group | Principles | Validated |
|-------|-----------|-----------|
| **Source and truth** | 1-3 | ✅ By Tunisia |
| **Parameters** | 4-7 | ✅ + 3 new discovered |
| **Code** | 8-11 | ✅ With nuances |
| **Quality** | 12-14 | ✅ (partial application) |

---

## What is NOT universal

**Country-specific configuration** (see `config/countries/<country>.yaml`):

- Parameter hierarchy (gov, social_benefits, taxation, etc.)
- Entity names (Person vs Individu, Family vs Famille)
- Currency units (CUR, EUR, TND, USD)
- Terminology (minimum_wage vs smig vs smic)
- Separate regimes (pension systems: CNRPS, RSA, RSNA)
- Calculation periods (quarterly vs monthly)

**What IS universal** (cannot be changed):
- **Naming convention**: `snake_case` (always)
- **File structure**: parameters/, variables/, tests/
- **Metadata fields**: description, label, reference, unit (mandatory)
- **Units file**: `<package>/units.yaml` (required in all packages)

---

## Pre-commit Checklist

Before every commit, verify:

- [ ] **Principle 1**: Based on official text (not guessed)
- [ ] **Principle 2**: No hardcode (except 0, 1, 4, 12)
- [ ] **Principle 3**: References with #page=XX
- [ ] **Principle 4**: Parameters with description, label, reference, **unit** (+ units.yaml exists)
- [ ] **Principle 5**: Value history present
- [ ] **Principle 8**: Correct entity
- [ ] **Principle 9**: Vectorized code
- [ ] **Principle 11**: No TODOs
- [ ] **Principle 12**: Tests written and passing
- [ ] **Principle 14**: Code formatted

---

## Resources

### Documentation
- **Validation**: [UNIVERSAL_PRINCIPLES_VALIDATION.md](../UNIVERSAL_PRINCIPLES_VALIDATION.md)
- **Learning**: [LEARNING_LOG.md](../../LEARNING_LOG.md)
- **Final version**: [PRINCIPLES_UNIVERSELS_FINAUX.md](../PRINCIPLES_UNIVERSELS_FINAUX.md)
- **Country examples**: [country-template/](../country-template/)
- **Country specifics**: [03-countries/](../03-countries/)

### External Tools
- **OpenFisca Control Center**: https://control-center.tax-benefit.org/
  - Automated parameter validation for configured repositories
  - Reference checking and metadata validation
  - Essential for production repositories

---

**Version**: 2.0 (2026-03-11)
**Language**: English (universal documentation)
**Validated by**: openfisca-tunisia
**Status**: ✅ Finalized and applicable
