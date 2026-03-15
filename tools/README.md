# OpenFisca AI Tools - NO AGENTS NEEDED

Autonomous validation and checking tools that work **without AI agents**.

They can be called either directly from `tools/` or through the CLI wrapper:

```bash
uv run openfisca-ai audit /path/to/openfisca-country
uv run openfisca-ai check-all /path/to/openfisca-country
uv run openfisca-ai validate-code /path/to/openfisca-country
```

## Philosophy

These tools help you validate OpenFisca code **autonomously**:
- ✅ No LLM costs
- ✅ Instant results
- ✅ Actionable error messages
- ✅ CI/CD integration ready

They complement the shared package baseline documented in
[`docs/agents/01-universal/country-package-baseline.md`](../docs/agents/01-universal/country-package-baseline.md).

`check-all` is the preferred repo-wide entrypoint when you want one command to
run the full OpenFisca AI audit stack.

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
  - `unit` for simple parameters
  - `metadata.threshold_unit` / `metadata.rate_unit` / `metadata.amount_unit` for scale parameters
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
uv run python tools/validate_parameters.py /path/to/openfisca-country
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
  run: uv run python tools/validate_parameters.py openfisca_tunisia/
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
3. Add unit metadata to parameters missing it

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

### Scale parameters (`brackets`)

For bracket-based parameters, use metadata keys instead of a single `unit`:

```yaml
description: Income tax brackets
label: Income tax brackets
reference:
  - "Law n° XX, Article YY"
metadata:
  threshold_unit: currency
  rate_unit: /1
brackets:
  - threshold:
      2024-01-01: 0
    rate:
      2024-01-01: 0.1
```

### 2. `validate_units.py`

Focused validator for unit coverage only.

It accepts:
- `unit` for simple parameters
- `metadata.threshold_unit` / `rate_unit` / `amount_unit` for scale parameters

### 3. `suggest_units.py`

Heuristic unit suggester.

It can:
- suggest `unit` for simple parameters
- suggest missing scale units for `brackets`
- auto-apply only high-confidence suggestions with `--apply`

### 4. `check_tooling.py`

Tooling checker for OpenFisca repositories.

It prefers `uv` and `ruff`, but does not automatically fail every repo using a different valid stack.

It is intentionally limited to conventions. It does **not** yet validate the
full OpenFisca package baseline (`entities.py`, `units.yaml`, `parameters/`,
`tests/`, standard package layout).

### 5. `check_package_baseline.py`

Baseline checker for OpenFisca country repositories.

It verifies the shared package structure expected in most country packages:

- `pyproject.toml`
- `uv.lock` when using a modern `uv` workflow
- a top-level `openfisca_<country>` package
- `entities.py`, `units.yaml`, `parameters/`, `variables/`
- `tests/` and YAML tests
- common `Makefile` and CI entry points

Use it from the repository root:

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/check_package_baseline.py .
```

### 6. `validate_code.py`

Python code validator for OpenFisca country packages.

It currently checks for:

- TODO, FIXME, and placeholder markers in package code
- missing `entity` or `definition_period` on `Variable` classes
- explicit Python loops in `formula*` methods
- suspicious hardcoded numeric values in formulas
- Python `if` statements and comprehensions in formulas as warnings

Use it from the repository root:

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/validate_code.py .
```

### 7. `validate_tests.py`

Test coverage validator for OpenFisca country packages.

It currently checks for:

- presence of `tests/`
- presence of YAML and Python tests
- coverage of `Variable` classes that define `formula*` methods
- missing coverage when a computed variable is never mentioned in tests

Use it from the repository root:

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/validate_tests.py .
```

### 8. `extract_patterns.py`

Pattern extractor for OpenFisca country packages.

It summarizes:

- package structure
- variable entities and definition periods
- `set_input` helpers
- formula idioms such as `where`, `min_`, `max_`, `.calc(...)`, `members(...)`
- aggregation methods
- parameter domains, scale files, and common units
- test distribution

Use it from the repository root:

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/extract_patterns.py .
```

For machine-readable output:

```bash
uv run python /path/to/openfisca-ai/tools/extract_patterns.py . --json
```

### 9. `audit_country_package.py`

Unified audit runner for OpenFisca country packages.

It orchestrates:

- `check_package_baseline.py`
- `check_tooling.py`
- `validate_units.py`
- `validate_parameters.py`
- `validate_code.py`
- `validate_tests.py`
- `extract_patterns.py`

Use it from the repository root:

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/audit_country_package.py .
```

Alternative outputs:

```bash
uv run python /path/to/openfisca-ai/tools/audit_country_package.py . --json
uv run python /path/to/openfisca-ai/tools/audit_country_package.py . --markdown
uv run python /path/to/openfisca-ai/tools/audit_country_package.py . --markdown --output audit.md
```

---

## Future Tools (Planned)

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

## Current Limits

- `suggest_units.py` is heuristic: medium-confidence suggestions still need human review.
- `check_tooling.py` checks conventions, not correctness of the whole build system.
- Python code validation and test coverage validation are not implemented yet.

---

## See Also

- [Universal Principles](../docs/agents/01-universal/principles.md)
- [Country Package Baseline](../docs/agents/01-universal/country-package-baseline.md)
- [Quality Checklist](../docs/agents/01-universal/quality-checklist.md)
- [Tunisia Validation Report](../TUNISIA_VALIDATION_REPORT.md)
