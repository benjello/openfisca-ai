# OpenFisca AI Tools - NO AGENTS NEEDED

Autonomous validation and checking tools that work **without AI agents**.

## Philosophy

These tools help you validate OpenFisca code **autonomously**:
- ✅ No LLM costs
- ✅ Instant results
- ✅ Actionable error messages
- ✅ CI/CD integration ready

---

## Tools Available

### 1. `validate_parameters.py`

Check parameter files against universal principles (Principle 4).

**What it checks:**
- ✅ `units.yaml` exists at package root
- ✅ All parameters have required metadata:
  - `description` (clear sentence)
  - `label` (short name)
  - `reference` (legal citation)
  - `unit` (from units.yaml)
- ✅ All units used are defined in units.yaml
- ⚠️  PDF references include `#page=XX`

**Usage:**
```bash
# IMPORTANT: Run in package's venv with uv
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .

# Example for Tunisia
cd /home/user/openfisca-tunisia
uv run python ../openfisca-ai/tools/validate_parameters.py openfisca_tunisia
```

**Alternative (from anywhere)**:
```bash
# If you have the full path
python tools/validate_parameters.py /path/to/openfisca-country
```

**Output:**
```
🔍 Validating /path/to/openfisca-tunisia...

✅ Found units.yaml with 19 units defined
📋 Checking 439 parameter files...

❌ 727 ERRORS:
  [ERROR] parameters/retraite/rsa/age_legal.yaml
    Missing 'label' field (Short name for UI)
    (Principle 4: Well-documented parameters)
  ...

📊 Units: 12 used, 19 defined
✅ All units properly defined
```

**Exit codes:**
- `0` = All checks passed
- `1` = Errors found

**CI Integration:**
```yaml
# .github/workflows/validate.yml
- name: Validate parameters
  run: python tools/validate_parameters.py openfisca_tunisia/
```

---

## Real-World Results: openfisca-tunisia

Ran `validate_parameters.py` on openfisca-tunisia (439 parameter files):

**Findings:**
- ✅ **units.yaml exists** with 19 units defined
- ✅ **All units used are defined** (12 used, 19 defined)
- ❌ **727 errors found**:
  - Missing `label` field: ~250 files
  - Missing `reference` field: ~250 files
  - Missing `unit` field: ~227 files

**Conclusion:** Tunisia has good structure (units.yaml, descriptions) but needs:
1. Add `label` to all parameters
2. Add `reference` with legal citations
3. Add `unit` to parameters missing it

---

## How to Fix Issues

### Missing `label` field

**Before:**
```yaml
description: Pension minimale garanti de la CNRPS
values:
  1974-01-01: 0.66666
```

**After:**
```yaml
description: Pension minimale garanti de la CNRPS
label: Pension minimale CNRPS  # Short, clear name
values:
  1974-01-01: 0.66666
```

### Missing `reference` field

**Before:**
```yaml
description: Pension minimale garanti de la CNRPS
label: Pension minimale CNRPS
```

**After:**
```yaml
description: Pension minimale garanti de la CNRPS
label: Pension minimale CNRPS
reference:
  - "Loi n° XX, Article YY"
  - "http://www.example.tn/law.pdf#page=15"
```

### Missing `unit` field

**Before:**
```yaml
description: Age légal de départ à la retraite
label: Âge légal retraite RSA
values:
  1959-02-01: 60
```

**After:**
```yaml
description: Age légal de départ à la retraite
label: Âge légal retraite RSA
unit: year  # Must be defined in units.yaml
values:
  1959-02-01: 60
```

---

## Future Tools (Planned)

### 2. `validate_code.py` *(coming soon)*
Check Python code against principles:
- No hardcoded values
- Vectorization (no loops)
- Correct entities
- No TODOs

### 3. `validate_tests.py` *(coming soon)*
Check test files:
- All variables with formulas have tests
- Tests include manual calculations in comments
- Tests reference legal sources

### 4. `extract_patterns.py` *(coming soon)*
Extract reusable patterns from existing code:
- Income eligibility checks
- Progressive scales
- Family aggregations
- Indexed parameters

---

## Philosophy: Code as Documentation

Instead of asking agents to generate code, these tools:

1. **Validate** existing code against principles
2. **Extract** patterns from working implementations
3. **Guide** developers to fix issues autonomously
4. **Reduce** reliance on expensive AI agents

**Cost comparison:**
- Agent validation: ~$0.10-0.50 per run (API costs)
- `validate_parameters.py`: **FREE**, instant

**Speed comparison:**
- Agent validation: 30-60 seconds
- `validate_parameters.py`: **< 2 seconds** for 439 files

---

## Contributing

Add new validation tools following this pattern:

1. **Autonomous**: No AI/LLM required
2. **Fast**: < 5 seconds for typical repo
3. **Actionable**: Clear error messages with fixes
4. **Universal**: Work with any OpenFisca package

---

## See Also

- [Universal Principles](../docs/agents/01-universal/principles.md)
- [Quality Checklist](../docs/agents/01-universal/quality-checklist.md)
- [Tunisia Validation Report](../TUNISIA_VALIDATION_REPORT.md)
