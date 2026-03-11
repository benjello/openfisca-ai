# Quality Checklist - Pre-commit/PR

Mandatory checks before creating a commit or pull request.

Based on the [14 Universal Principles](principles.md).

---

## ✅ Code

### Variables and Formulas
- [ ] No hardcoded values (except 0, 1, period conversions)
- [ ] All values from parameters
- [ ] Variable at correct entity level (Person, Family, Household, TaxUnit)
- [ ] Correct `definition_period` (MONTH, YEAR, ETERNITY)
- [ ] Vectorized operations (`where()`, `max_()`, `min_()` instead of loops)
- [ ] No unnecessary wrapper variables

### Naming
- [ ] Variable names in `snake_case` (or country convention)
- [ ] Clear and descriptive labels
- [ ] Consistency with existing country code

### Quality
- [ ] No `# TODO` or placeholders
- [ ] No commented code (delete or document why)
- [ ] Docstrings for complex variables

---

## ✅ Parameters

### Mandatory Metadata
- [ ] `description`: One clear sentence
- [ ] `label`: Short name for UI
- [ ] `reference`: URL or legal citation
  - [ ] For PDFs: `#page=XX` added (e.g., `doc.pdf#page=42`)
- [ ] `unit`: `/1`, `EUR`, `TND`, `CUR`, etc.
- [ ] `values`: Dates + historical values

### Organization
- [ ] Logical hierarchy (e.g., `social_benefits/housing_allowance/`)
- [ ] No duplicates (check similar parameter doesn't exist)
- [ ] Valid YAML files (no syntax errors)

### Verified References
- [ ] Accessible URLs
- [ ] Correct page numbers for PDFs
- [ ] Exact legal citations (law number, article)

---

## ✅ Tests

### Coverage
- [ ] Each variable with formula → test file
- [ ] Unit tests (variable alone)
- [ ] Integration tests (complete scenarios)
- [ ] Edge cases tested:
  - [ ] Zero values
  - [ ] Values at thresholds (just below/above)
  - [ ] Various family sizes
  - [ ] Geographic cases (if applicable)

### Test Quality
- [ ] Manual calculations in comments (with legal reference)
- [ ] Expected values justified (e.g., "according to Art. 12, p.5: ...")
- [ ] Tests pass (`pytest` locally)

### Example Test Comment
```python
# Manual calculation (Benefits Act 2020, Art. 5, p.12):
# - Income: 1500 CUR
# - Ceiling for 2 children: 2000 CUR (Annex A)
# - Rate: 25% (Table B)
# - Amount: (2000 - 1500) × 0.25 = 125 CUR
assert amount == 125
```

---

## ✅ Regulatory Compliance

### Sources
- [ ] Implementation based on official texts (not guessed)
- [ ] Sources consulted and cited
- [ ] Simulable rules identified (vs non-simulable flagged)

### Validation
- [ ] Code verified against legal documentation
- [ ] Real use cases tested (if available)
- [ ] Comparison with official calculators (if exist)

---

## ✅ Performance

### Optimization
- [ ] No explicit Python loops
- [ ] Vectorized NumPy operations
- [ ] `defined_for` used to limit periods (if applicable)

### Anti-patterns Avoided
- [ ] No redundant calculations
- [ ] No multiple reads of same variable
- [ ] No unnecessary type conversions

---

## ✅ Documentation

### Code
- [ ] Docstrings for non-trivial variables/functions
- [ ] Comments for complex logic (with legal reference)
- [ ] No obvious comments (e.g., `# Calculate total` for `total = a + b`)

### Metadata
- [ ] Labels understandable for end users
- [ ] Technical descriptions clear for developers

---

## ✅ Formatting

### Python
- [ ] Formatted with **Black**
- [ ] Sorted imports (optional: `isort`)
- [ ] No `flake8` or `pylint` warnings (if used)

### YAML
- [ ] Formatted with **Prettier** or **yamllint**
- [ ] Consistent 2-space indentation
- [ ] No syntax errors

---

## ✅ Git

### Commits
- [ ] Clear and descriptive commit messages
- [ ] Format: `"Add <variable>: <short description>"`
  - Examples:
    - `"Add housing_allowance: monthly allowance for low-income families"`
    - `"Fix tax_rate: correct rate from 2024-01-01"`
- [ ] One commit per logical change (not mega-commits)

### Pull Request
- [ ] Clear title (< 70 characters)
- [ ] Description with:
  - [ ] Summary of changes (bullet points)
  - [ ] Legal references
  - [ ] Test plan
- [ ] No irrelevant files (`.env`, `__pycache__`, etc.)

---

## ✅ CI/CD

### Before Push
- [ ] Tests pass locally (`pytest`)
- [ ] Build succeeds (`python -m build` or equivalent)
- [ ] No linting errors

### After Push
- [ ] GitHub CI green
- [ ] No merge conflicts
- [ ] Peer review requested (if collaborative workflow)

---

## ✅ Country Specifics

### Configuration
- [ ] Country config loaded correctly (`country_id` in task)
- [ ] Country conventions respected (see `03-countries/<country>/specifics.md`)
- [ ] Deviations from norm documented (if any)

---

## 🚀 Quick Validation Commands

### Local Quick Check
```bash
# Tests
pytest

# Formatting
black src/
prettier --write config/

# Lint (optional)
flake8 src/
yamllint config/
```

### Complete Validation (before PR)
```bash
# All tests with coverage
pytest --cov=openfisca_ai --cov-report=term-missing

# Build
python -m build

# Verify country config
openfisca-ai run tasks/countries/<country>/test_task.json
```

---

## 📚 Resources

- **14 Principles**: [principles.md](principles.md)
- **OpenFisca Basics**: [openfisca-basics.md](openfisca-basics.md)
- **Examples**: [country-template](../country-template/)
- **Role-specific checklists**: [../02-framework/roles/](../02-framework/roles/)

---

**This checklist is universal**. For role-specific checks, see:
- [document-collector](../02-framework/roles/document-collector.md#checklist)
- [rules-engineer](../02-framework/roles/rules-engineer.md#checklist)
- [test-creator](../02-framework/roles/test-creator.md#checklist)
- [validators](../02-framework/roles/validators.md#checklist)
