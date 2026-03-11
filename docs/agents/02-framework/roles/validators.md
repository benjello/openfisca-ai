# Agents: Validators

Set of agents to **validate quality, compliance, and consistency** of implementations.

## Overview

| Validator | Role | Scope |
|-----------|------|-------|
| **implementation-validator** | Overall quality, patterns, naming | One program |
| **program-reviewer** | Regulatory compliance | One program |
| **reference-validator** | Reference validity (URLs, pages) | All parameters/variables |
| **cross-program-validator** | Cross-program consistency | All country programs |
| **performance-optimizer** | Vectorization, performance | Python code |

---

## 1. implementation-validator

**Global** validation of an implementation (code + parameters + tests).

### Checks

#### Python Code
- [ ] **No hardcoded values** (except 0, 1)
- [ ] **Correct entities** (Person, Family, Household, TaxUnit)
- [ ] **Vectorized** (`where()`, `max_()`, `min_()` instead of loops)
- [ ] **adds vs add()** used correctly
- [ ] **No wrapper variables** (unnecessary)
- [ ] **No TODO/placeholders**
- [ ] **Formatted** (Black)

#### YAML Parameters
- [ ] **Complete metadata** (description, label, reference, unit)
- [ ] **Consistent hierarchy** (according to country convention)
- [ ] **Precise references** (with `#page=XX` for PDFs)
- [ ] **Reference format as list** if multiple sources
- [ ] **No duplicates** (check that similar parameter doesn't exist)

#### Tests
- [ ] **Each variable with formula → test**
- [ ] **Manual calculations** in comments with references
- [ ] **Edge cases** tested
- [ ] **Tests pass** (`pytest`)

### Output

**Structured report** with precise fixes:

```json
{
  "valid": false,
  "errors": [
    {
      "type": "hardcoded_value",
      "file": "variables/housing_allowance.py",
      "line": 15,
      "message": "Hardcoded value '1700' found. Must come from parameters.",
      "fix": {
        "old": "ceiling = 1700",
        "new": "ceiling = parameters(period).social_benefits.benefits.housing_allowance.income_ceiling"
      }
    },
    {
      "type": "missing_metadata",
      "file": "parameters/social_benefits/ceiling.yaml",
      "field": "reference",
      "message": "Missing 'reference' field.",
      "fix": "Add legal reference (law, article, URL with #page=XX)"
    }
  ],
  "warnings": [
    {
      "type": "wrapper_variable",
      "file": "variables/total_income.py",
      "message": "Variable 'total_income' appears to be an unnecessary wrapper (just calls 'income')."
    }
  ]
}
```

This report is used by **ci-fixer** to apply fixes automatically.

---

## 2. program-reviewer

**Regulatory** review: verify that implementation complies with legislation.

### Workflow

1. **Search official sources** (WebFetch, document-collector)
2. **Extract rules** (eligibility, calculation, ceilings, scales)
3. **Compare PR ↔ regulations**
4. **Check tests** (do they cover legal cases?)
5. **Write report**
6. **After user validation**: update GitHub issue/PR descriptions

### Structured Summary

```markdown
## Official Regulation: Housing Allowance (Countria)

### Eligibility (Social Benefits Act 2020, Sec. 12)
- Family income < 1700 CUR
- Family with dependent children
- Primary residence

### Amount Calculation (Sec. 14)
- Base amount: 220 CUR
- Supplement per child: 50 CUR
- Total ceiling: 450 CUR

### Comparison with PR #42
✅ Income eligibility: correct
✅ Base amount: correct
❌ Child supplement: missing (needs implementation)
⚠️ Total ceiling: not tested (add edge case test)

### Recommendations
1. Implement child_supplement (Sec. 14, p.16)
2. Add test with 5 children (ceiling 450)
3. Check formula: base + (supplement × nb_children), then min(total, 450)
```

### Important
**Does NOT modify code**: only flags gaps and discrepancies.

---

## 3. reference-validator

Validate that **references are valid** (accessible links, correct pages).

### Checks

#### URLs
- [ ] Links accessible (HTTP 200)
- [ ] PDFs downloadable
- [ ] Correct page numbers (`#page=XX` points to correct page)

#### Legal Citations
- [ ] Exact law number
- [ ] Article exists
- [ ] Correct date

#### Official Validation Tool

**OpenFisca Control Center**: https://control-center.tax-benefit.org/

- Automated validation of parameters for configured repositories
- Checks metadata completeness, reference validity
- Integration with GitHub repositories
- **Usage**: Configure your repository in Control Center for automatic validation

### Output

```json
{
  "broken_links": [
    {
      "file": "parameters/social_benefits/ceiling.yaml",
      "url": "https://example.gov/act-404.pdf",
      "error": "HTTP 404 Not Found"
    }
  ],
  "incorrect_pages": [
    {
      "file": "parameters/allowance.yaml",
      "url": "https://example.gov/act.pdf#page=99",
      "issue": "PDF only has 50 pages"
    }
  ],
  "missing_page_refs": [
    {
      "file": "parameters/rate.yaml",
      "url": "https://example.gov/doc.pdf",
      "fix": "Add #page=XX to URL"
    }
  ]
}
```

**Recommendation**: Use https://control-center.tax-benefit.org/ for continuous validation of production repositories.

---

## 4. cross-program-validator

Check **consistency between programs** in the same country.

### Checks

#### Naming
- [ ] Consistent conventions (snake_case everywhere or camelCase everywhere)
- [ ] Uniform terms (e.g., `income` vs `incomes`, `child` vs `children`)

#### Variable Reuse
- [ ] Common variables reused (e.g., `disposable_income`, `nb_children`)
- [ ] No duplicates (e.g., `net_salary` and `monthly_net_salary` for same thing)

#### Parameters
- [ ] Common parameters factored (e.g., `gov.minimum_wage` used by multiple programs)
- [ ] Consistent hierarchy

### Example

```markdown
## Consistency Countria: housing_allowance vs child_allowance

✅ Both use `nb_children` (same variable)
❌ housing_allowance uses `disposable_income`, child_allowance uses `monthly_income`
   → Standardize: choose one name
⚠️ Parameter `income_ceiling` exists twice:
   - social_benefits/benefits/housing_allowance/income_ceiling
   - social_benefits/benefits/child_allowance/income_ceiling
   → OK if different values, otherwise factor out
```

---

## 5. performance-optimizer

Identify **vectorization opportunities** and optimizations.

### Checks

#### Anti-patterns
- [ ] **Explicit Python loops** (replace with `where()`, `select()`)
- [ ] **Redundant calculations** (same variables calculated multiple times)
- [ ] **Unnecessary conversions** (e.g., float → int → float)

#### Best Practices
- [ ] `defined_for` to limit calculated periods
- [ ] `max_()`, `min_()` instead of `if/else`
- [ ] `where()` for conditions
- [ ] Efficient aggregations (`sum`, `any`, `all`)

### Example

#### ❌ Before (slow)
```python
def formula(person, period, parameters):
    result = []
    for p in person:
        if p.age > 18:
            result.append(p.salary * 1.1)
        else:
            result.append(p.salary)
    return result
```

#### ✅ After (fast, vectorized)
```python
def formula(person, period, parameters):
    age = person('age', period)
    salary = person('salary', period)
    bonus = where(age > 18, 1.1, 1.0)
    return salary * bonus
```

---

## Complete Validation Workflow

```
[Code + Params + Tests]
        ↓
[implementation-validator] → Quality report
        ↓
[program-reviewer] → Regulatory compliance report
        ↓
[reference-validator] → References report
        ↓
[cross-program-validator] → Consistency report
        ↓
[performance-optimizer] → Optimization suggestions
        ↓
[Consolidated report] → ci-fixer
```

## Global Checklist

- [ ] implementation-validator: no errors
- [ ] program-reviewer: complies with law
- [ ] reference-validator: all references valid
- [ ] cross-program-validator: consistent with other programs
- [ ] performance-optimizer: no anti-patterns
- [ ] Tests pass (`pytest`)
- [ ] CI green

## Resources

- [quality-checklist.md](../../01-universal/quality-checklist.md) for detailed checklist
- PolicyEngine validators: [policyengine-claude agents](../../../policyengine-claude-agents.md)

---

**Next steps**: Validation reports feed `ci-fixer` which applies fixes automatically.
