# Country Template - "Countria"

Generic examples for OpenFisca AI documentation and new country implementations.

## Purpose

This template provides **generic, reusable examples** for:
1. **Universal documentation** (01-universal, 02-framework)
2. **Starting a new country** implementation
3. **Testing and demonstrations**

**Important**: This is NOT a real country. Examples are simplified for educational purposes.

---

## Structure

```
country-template/
├── README.md              # This file
├── parameters/            # Generic YAML parameters
│   ├── labor_market/
│   │   └── minimum_wage.yaml
│   ├── social_benefits/
│   │   ├── housing_allowance/
│   │   │   ├── income_ceiling.yaml
│   │   │   └── base_amount.yaml
│   │   └── family_benefits/
│   │       └── child_allowance.yaml
│   └── taxation/
│       └── income_tax/
│           └── tax_brackets.yaml
├── variables/             # Generic Python variables
│   ├── housing_allowance.py
│   ├── family_benefits.py
│   └── income_tax.py
└── tests/                 # Generic tests
    ├── test_housing_allowance.py
    └── test_family_benefits.py
```

---

## Generic Concepts

### Country: "Countria"
- **Currency**: CUR (Countria Currency Unit)
- **Minimum wage**: Called "minimum_wage" (generic)
- **Entities**: Person, Family, Household, TaxUnit
- **Language**: English (for universal examples)

### Generic Programs
1. **Housing Allowance**: Low-income families, income-based
2. **Family Benefits**: Per-child allowance
3. **Income Tax**: Progressive tax brackets

---

## Repository Naming Convention

### OpenFisca Country Repositories

**Standard naming** : `github.com/openfisca/openfisca-<country>`

Examples:

- France: [`github.com/openfisca/openfisca-france`](https://github.com/openfisca/openfisca-france)
- Tunisia: [`github.com/openfisca/openfisca-tunisia`](https://github.com/openfisca/openfisca-tunisia)
- UK: [`github.com/openfisca/openfisca-uk`](https://github.com/openfisca/openfisca-uk)
- USA (PolicyEngine): [`github.com/PolicyEngine/openfisca-us`](https://github.com/PolicyEngine/openfisca-us)

### This Template Repository

**Exception** : `github.com/openfisca/country-template`

This template is NOT a real country implementation, so it doesn't follow the `openfisca-<country>` pattern.

---

## Usage

### For Documentation
Reference these examples in universal documentation:

```markdown
See [country-template/parameters/social_benefits/housing_allowance](../country-template/parameters/social_benefits/)
```

### For New Country

#### 1. Create Repository

Follow OpenFisca convention:

```bash
# Create repo: openfisca-<country>
git clone github.com/openfisca/country-template openfisca-<yourcountry>
cd openfisca-<yourcountry>
```

#### 2. Customize

1. Replace "Countria" with your country name
2. Replace CUR with your currency (EUR, USD, TND, etc.)
3. Replace generic values with real legislation
4. Update entity names if different (Person, Famille, etc.)
5. Update all references to point to real legislation

---

## Principles Demonstrated

All examples follow the **14 Universal Principles**:
1. ✅ Law as source of truth (references provided)
2. ✅ No hardcoded values (except 0, 1, period conversions)
3. ✅ Well-documented parameters
4. ✅ Correct entities
5. ✅ Complete history
6. ✅ Indexed values (when applicable)
7. ✅ Extensible metadata
8. ✅ Vectorization
9. ✅ No TODOs
10. ✅ Tests for all variables
11. ✅ Pattern reuse
12. ✅ Precise references
13. ✅ Period conversions documented
14. ✅ Formatted code

---

## Contributing

When adding examples:
- Keep them **generic and simple**
- Follow **all 14 principles**
- Add **comments** explaining concepts
- Use **clear variable names**
- Provide **complete metadata**

---

_Template created 2026-03-11 for OpenFisca AI universal documentation_
