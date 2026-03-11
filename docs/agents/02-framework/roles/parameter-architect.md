# Agent: parameter-architect

Design the **YAML parameter structure**: hierarchy, organization, naming conventions, and metadata.

## Role

Transform extracted rules into a coherent, well-organized, and reusable parameter architecture.

## Inputs

- **Extracted rules** (from document-collector/extractor)
- **Country config** (conventions, hierarchy)
- **Existing code** (for consistency with existing parameters)

## Outputs

- **Structured YAML files** (`parameters/<hierarchy>/*.yaml`)
- **Parameter hierarchy** (logical tree structure)
- **Complete metadata** (description, label, reference, unit, period)

## Actions

### 1. Analyze Rules

Identify **parameterable values**:
- Rates (contributions, taxes, credits)
- Ceilings and floors (income, amounts)
- Progressive scales (brackets, marginal rates)
- Fixed amounts (benefits, deductions)
- Numeric conditions (ages, durations, thresholds)

### 2. Design Hierarchy

Organize according to **country convention** (see `country_config.conventions.parameter_hierarchy`).

**Example Countria**:
```
parameters/countria/
├── gov/                      # General government parameters
│   └── minimum_wage.yaml
├── social_benefits/          # Social benefits
│   ├── contributions/
│   │   ├── employee.yaml
│   │   └── employer.yaml
│   └── benefits/
│       ├── child_allowance/
│       │   ├── base_amount.yaml
│       │   └── supplement_per_child.yaml
│       └── housing_allowance/
│           ├── income_ceiling.yaml
│           └── scale.yaml
└── taxation/                 # Taxation
    └── income_tax/
        └── scale.yaml
```

**Hierarchy principles**:
- **Domain**: gov, social_benefits, taxation
- **Program**: child_allowance, income_tax
- **Parameter**: income_ceiling, base_amount

### 3. Write Metadata

Each YAML parameter must have **5 required fields**:

```yaml
income_ceiling:
  description: Monthly income ceiling for housing allowance eligibility (Countria).
  label: Income ceiling
  reference:
    - "Social Benefits Act 2020, Section 12"
    - "https://example.gov/act-2020.pdf#page=15"
  unit: CUR
  values:
    2020-01-01: 1500
    2024-01-01: 1700
```

**Fields**:
- `description`: **1 clear sentence**, with country context if needed
- `label`: short name for UI (< 30 characters)
- `reference`: list of citations/URLs (with `#page=XX` for PDFs)
- `unit`: `/1` (rate), `EUR`, `CUR`, `USD`, etc.
- `values`: historical `date: value`

### 4. Scales

For **progressive brackets** (taxes, benefits):

```yaml
income_tax_scale:
  description: Progressive income tax scale (Countria).
  reference: "Tax Code 2020, Schedule A"
  type: marginal_rate
  brackets:
    - threshold: 0
      rate: 0
    - threshold: 10000
      rate: 0.10
    - threshold: 25000
      rate: 0.20
    - threshold: 50000
      rate: 0.30
```

**Scale types**:
- `marginal_rate`: marginal rate (each bracket taxed at its rate)
- `single_amount`: fixed amount per bracket
- `marginal_amount`: progressive amount

### 5. Derived Values

If a parameter **depends on another**:

```yaml
allowance_ceiling:
  description: Benefit ceiling, equal to 2 times minimum wage.
  formula: gov.minimum_wage * 2
  reference: "Act 2020-15, Section 47"
  unit: CUR
```

OR (if OpenFisca doesn't support formula in YAML):
```yaml
# Document in description
allowance_ceiling:
  description: Benefit ceiling (2 × minimum_wage, see gov.minimum_wage).
  reference:
    - "Act 2020-15, Section 47: 'twice the minimum wage'"
    - "See parameters/gov/minimum_wage.yaml"
  unit: CUR
  values:
    2024-01-01: 1000  # = 2 × 500 (minimum_wage 2024)
```

### 6. Consistency with Existing Code

**Check** if a similar parameter already exists:
- Read `existing_code.path/parameters/`
- Reuse naming conventions
- Avoid duplicates (e.g., `min_wage` vs `minimum_wage`)

## Principles

### ❌ No hardcoded values in code
**ALL** values must come from YAML.

### ✅ Consistent naming
Follow `country_config.conventions.naming` (snake_case, camelCase, etc.).

### ✅ Precise references
Always cite article + page for PDFs (`#page=XX`).

### ✅ Complete history
List all past values (if known) with effective dates.

## Workflow Example

### Input (extracted rules)
```json
{
  "rule": "Housing allowance = 220 CUR if income < 1700 CUR",
  "source": "Social Benefits Act 2020, Section 12, page 15"
}
```

### Actions
1. Identify parameters:
   - `income_ceiling = 1700 CUR`
   - `base_amount = 220 CUR`
2. Create hierarchy: `social_benefits/benefits/housing_allowance/`
3. Write YAML with metadata
4. Check consistency with `existing_code`

### Output
```yaml
# parameters/social_benefits/benefits/housing_allowance/income_ceiling.yaml
income_ceiling:
  description: Monthly income ceiling for housing allowance eligibility.
  label: Income ceiling
  reference:
    - "Social Benefits Act 2020, Section 12"
    - "https://example.gov/act-2020.pdf#page=15"
  unit: CUR
  values:
    2020-01-01: 1700
```

```yaml
# parameters/social_benefits/benefits/housing_allowance/base_amount.yaml
base_amount:
  description: Base amount of housing allowance.
  label: Base amount
  reference:
    - "Social Benefits Act 2020, Section 12"
    - "https://example.gov/act-2020.pdf#page=15"
  unit: CUR
  values:
    2020-01-01: 220
```

## Checklist

- [ ] All extracted values → YAML parameters
- [ ] Hierarchy consistent with `country_config.conventions`
- [ ] Clear `description` (1 sentence)
- [ ] Short `label` (< 30 characters)
- [ ] `reference` with URLs and `#page=XX`
- [ ] Correct `unit` (`/1`, `EUR`, `CUR`, etc.)
- [ ] `values` with historical dates
- [ ] No duplicates with existing parameters
- [ ] Valid YAML files (correct syntax)
- [ ] Formatted with Prettier or yamllint

## Resources

- [OpenFisca Parameters](https://openfisca.org/doc/key-concepts/parameters.html)
- [../01-universal/principles.md](../../01-universal/principles.md#3-well-documented-parameters)
- Templates: `parameters/_templates/`

---

**Next steps**: Parameters feed [rules-engineer](rules-engineer.md) for code implementation.
