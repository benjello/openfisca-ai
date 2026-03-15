# OpenFisca AI

Validation tools, configuration helpers, and agent scaffolding for working with [OpenFisca](https://openfisca.org) country packages.

Designed for agents like **Cursor**, **Claude Code**, **Gemini**, **Antigravity**, etc.

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/openfisca-ai
cd openfisca-ai
uv sync --dev
```

### 2. Configure Local Paths

**Option A - Interactive (recommended)**:
```bash
uv run python config/setup.py
```

**Option B - Manual**:
```bash
cp config/user.yaml.template config/user.yaml
# Edit config/user.yaml using:
#   countries.<id>.existing_code.path
#   countries.<id>.legislative_sources.root
```

Validate the config with:
```bash
uv run python config/test_config.py
```

See [Local Configuration Guide](docs/setup/local-configuration.md) for details.

### 3. Use Validation Tools

```bash
cd /path/to/your/openfisca-country
uv run openfisca-ai check-all .
uv run openfisca-ai suggest-units . --apply
```

### 4. Try the Alpha Runtime

The `run` command is still alpha, but it can now load a configured reference
country package, attach a compact pattern summary to its output, and build an
`implementation_brief` for downstream code generation.

```bash
uv run openfisca-ai run tasks/example_task.json
uv run openfisca-ai scaffold tasks/example_task.json
uv run openfisca-ai scaffold-apply tasks/example_task.json
```

`scaffold` is preview-first by default.
`scaffold-apply` writes artifacts either to `options.output_dir` or, when a
country config is present, directly to the configured reference package.

Example task:

```json
{
  "id": "encode_ceiling",
  "country": "tunisia",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Section 1 - The ceiling..."
  },
  "options": {
    "use_existing_code_as_reference": true,
    "include_reference_audit_summary": true
  }
}
```

If you already have a structured extraction, you can also pass
`inputs.extracted` to generate non-destructive scaffolding artifacts:

```json
{
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 - Credit rate is 10%.",
    "extracted": {
      "variables": [
        {
          "name": "income_tax_credit",
          "entity": "TaxUnit",
          "definition_period": "YEAR",
          "value_type": "float",
          "base_variable": "taxable_income",
          "parameter": "taxation.income_tax.credit_rate"
        }
      ],
      "parameters": [
        {
          "name": "taxation.income_tax.credit_rate",
          "label": "Income tax credit rate",
          "description": "Rate applied to taxable income.",
          "unit": "/1",
          "value": 0.1
        }
      ]
    }
  }
}
```

The result then includes:
- `implementation_brief`
- `artifacts` with target paths and generated contents for variables, parameters, and YAML tests
- `notes` when only commented test templates could be produced

To write these artifacts to disk, add an output directory in task options:

```json
{
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 - Credit rate is 10%.",
    "extracted": {
      "variables": [
        {
          "name": "income_tax_credit",
          "entity": "TaxUnit",
          "definition_period": "YEAR",
          "value_type": "float",
          "base_variable": "taxable_income",
          "parameter": "taxation.income_tax.credit_rate"
        }
      ]
    }
  },
  "options": {
    "output_dir": "../generated"
  }
}
```

`output_dir` is resolved relative to the task JSON file. Existing files are not
overwritten unless you also set `overwrite_artifacts: true`.

When writing artifacts, the pipeline also returns:
- `artifact_write_plan` with one entry per target file
- `diff_preview` inside each planned entry
- `written_artifacts` only when files were actually written

You can preview changes without writing anything:

```json
{
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 - Credit rate is 10%.",
    "extracted": {
      "variables": [
        {
          "name": "income_tax_credit",
          "entity": "TaxUnit",
          "definition_period": "YEAR",
          "value_type": "float",
          "base_variable": "taxable_income",
          "parameter": "taxation.income_tax.credit_rate"
        }
      ]
    }
  },
  "options": {
    "output_dir": "../generated",
    "plan_only": true
  }
}
```

Conflict handling can be controlled with `existing_artifact_strategy`:
- `create`: fail on existing files
- `skip`: leave existing files untouched
- `append`: append generated content to existing files
- `update`: replace existing files with generated content

If you want to apply the scaffold directly to the configured OpenFisca country
package instead of a separate output directory, use:

```json
{
  "country": "tunisia",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 - Surcharge rate is 2%.",
    "extracted": {
      "variables": [
        {
          "name": "income_tax_surcharge",
          "entity": "TaxUnit",
          "definition_period": "YEAR",
          "value_type": "float",
          "domain": "taxation",
          "base_variable": "taxable_income",
          "parameter": "taxation.income_tax.surcharge_rate"
        }
      ]
    }
  },
  "options": {
    "use_existing_code_as_reference": true,
    "apply_artifacts_to_reference_package": true
  }
}
```

This writes into the configured repository root of `existing_code.path` and
still refuses to overwrite existing files unless `overwrite_artifacts: true` is
explicitly set.

---

## What's Inside

### 📚 Documentation

**Universal Principles** (apply to all countries):
- [Universal Principles](docs/agents/01-universal/principles.md) - 14 core rules
- [Country Package Baseline](docs/agents/01-universal/country-package-baseline.md) - shared package structure, tooling, tests, and CI
- [Quality Checklist](docs/agents/01-universal/quality-checklist.md)
- [Development Workflow](docs/agents/01-universal/development-workflow.md)

**Framework** (country-agnostic guidelines):
- [Workflows](docs/agents/02-framework/workflows.md)
- [Country Configuration](docs/agents/02-framework/country-config.md)
- [Roles](docs/agents/02-framework/roles/)

**Country-Specific** (tested with openfisca-tunisia):
- [Tunisia Specifics](docs/agents/03-countries/tunisia/specifics.md)
- [Tunisia Validation Report](TUNISIA_VALIDATION_REPORT.md)

### 🛠️ Validation Tools

**Autonomous tools that work without AI agents** (fast, free, CI-ready):

- **[validate_units.py](tools/validate_units.py)** - Check all parameters have units
- **[suggest_units.py](tools/suggest_units.py)** - Auto-suggest missing units
- **[check_tooling.py](tools/check_tooling.py)** - Verify modern tooling (uv, ruff, yamllint)
- **[check_package_baseline.py](tools/check_package_baseline.py)** - Check shared OpenFisca package structure and baseline repo conventions
- **[validate_code.py](tools/validate_code.py)** - Check Python formulas for placeholders, hardcodes, and missing OpenFisca metadata
- **[validate_tests.py](tools/validate_tests.py)** - Check that computed variables are covered by YAML or Python tests
- **[extract_patterns.py](tools/extract_patterns.py)** - Extract reusable package patterns from real OpenFisca code
- **[audit_country_package.py](tools/audit_country_package.py)** - Run the full audit stack and render a consolidated report
- **`check-all`** - CLI alias for the full package audit, intended as the default repo-wide check

See [Tools README](tools/README.md) for usage.

### Status

- **Stable today**: configuration helpers and autonomous validation tools in `tools/`
- **Alpha / incomplete**: agent runtime in `src/openfisca_ai/` (`ExtractorAgent`, `CoderAgent`, `law_to_code`)
  - current useful behavior: load country config, resolve existing code, extract reusable patterns, build an implementation brief, and generate scaffolding artifacts from structured extracted input
  - not implemented yet: real code generation, test generation, multi-agent orchestration

---

## Architecture

```
3-Level Architecture:

┌─────────────────────────────────────────┐
│ Level 1: Universal Principles          │  ← Apply to ALL countries
│ - 14 core rules (snake_case, units...)  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Level 2: Framework                      │  ← Country-agnostic patterns
│ - Parameter patterns                     │
│ - Variable formulas                      │
│ - Testing strategies                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Level 3: Country-Specific               │  ← Tunisia, France, etc.
│ - Conventions (entities, hierarchy)     │
│ - Multilingual requirements             │
└─────────────────────────────────────────┘
```

---

## Philosophy

### 1. Universal First

Start with **universal principles** that work for ALL OpenFisca countries:
- Snake_case naming
- units.yaml requirement
- Ruff for formatting
- uv for environment management

Then apply the shared package baseline:
- `pyproject.toml` + `uv.lock`
- `entities.py`, `parameters/`, `variables/`, `tests/`, `units.yaml`
- YAML tests with `openfisca test`
- a small `Makefile` and CI checks

### 2. Learn from Reality

Extract patterns from **working code** (openfisca-tunisia, openfisca-france) rather than theoretical specs.

### 3. Autonomous Tools

**Minimize AI agent costs** with fast, free validation tools:
- `validate_units.py`: < 2 seconds for 439 files
- Agent validation: ~$0.50 + 30-60 seconds

### 4. Progressive Complexity

- **Level 1**: Universal rules → quick validation
- **Level 2**: Patterns → code generation
- **Level 3**: Country specifics → localization

---

## Example: Tunisia Validation

Real results from `openfisca-tunisia` (439 parameter files):

```bash
cd /home/user/openfisca-tunisia
uv run python /path/to/openfisca-ai/tools/validate_units.py .

# Output:
✅ units.yaml found with 19 units defined
📋 Checking 439 parameter files...

📊 Summary:
   Total parameters: 439
   With unit field: 428 (97%)
   Missing unit: 11 (3%)

✅ All used units are defined in units.yaml
📈 Most used units:
   /1: 156 files
   currency: 142 files
   year: 89 files
```

See [Tunisia Validation Report](TUNISIA_VALIDATION_REPORT.md) for full results.

---

## Contributing

### Adding a New Country

1. Create config file:
   ```bash
   cp config/countries/tunisia.yaml config/countries/yourcountry.yaml
   # Edit with your country specifics
   ```

2. Create specifics doc:
   ```bash
   cp docs/agents/03-countries/tunisia/specifics.md \
      docs/agents/03-countries/yourcountry/specifics.md
   # Document country-specific conventions
   ```

3. Test validation:
   ```bash
   cd /path/to/openfisca-yourcountry
   uv run python /path/to/openfisca-ai/tools/validate_units.py .
   uv run python /path/to/openfisca-ai/tools/check_tooling.py .
   ```

### Adding New Validation Tools

Follow the pattern in [Tools README](tools/README.md):
- **Autonomous**: No AI/LLM required
- **Fast**: < 5 seconds
- **Actionable**: Clear error messages
- **Universal**: Work with any OpenFisca package

---

## Roadmap

### Current (v0.1)
- ✅ 14 universal principles validated
- ✅ Units validation (validate_units.py, suggest_units.py)
- ✅ Tooling validation (check_tooling.py)
- ✅ Package baseline validation (check_package_baseline.py)
- ✅ Python code validation (validate_code.py)
- ✅ Test coverage validation (validate_tests.py)
- ✅ Pattern extraction from existing code (extract_patterns.py)
- ✅ Unified package audit (audit_country_package.py)
- ✅ Tunisia tested (439 parameters)

### Next (v0.2)
- [ ] Test with openfisca-france

### Future (v0.3)
- [ ] Agent integration beyond reference-package analysis
- [ ] Auto-fix suggestions (beyond just reporting)
- [ ] Multilingual support for metadata

---

## Inspiration

This project is inspired by [PolicyEngine](https://policyengine.org), a fork of OpenFisca with [21 specialized agents](https://github.com/PolicyEngine/policyengine) for US legislation.

Our approach differs by:
- **Universal first**: Work with ANY OpenFisca country
- **3-level architecture**: Universal → Framework → Country
- **Cost optimization**: Autonomous tools instead of agents
- **Progressive learning**: Extract patterns from real code

---

## Resources

- **OpenFisca**: https://openfisca.org
- **Control Center**: https://control-center.tax-benefit.org (official validator)
- **Country Template**: https://github.com/openfisca/country-template
- **Tunisia Package**: https://github.com/openfisca/openfisca-tunisia

---

## License

MIT (same as OpenFisca)

---

## Support

- **Issues**: https://github.com/YOUR_USERNAME/openfisca-ai/issues
- **OpenFisca Slack**: https://openfisca.org/community
- **Documentation**: [docs/](docs/)

---

**Built with support from Claude Code (Opus 4.6)**
