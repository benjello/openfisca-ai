# OpenFisca AI

A reusable toolkit for [OpenFisca](https://openfisca.org) country packages:
methodology guides, validation tools, configuration helpers, and (alpha) agent
scaffolding. Designed to be **added as a dependency** to any OpenFisca country
project so its tools, guides, and conventions travel with the package.

Friendly with **Claude Code**, **Cursor**, **Gemini**, **Antigravity**, etc.

---

## Use as a dependency in your OpenFisca package

This is the **recommended** way to consume openfisca-ai. You don't need to
clone it: add it as a dev dependency, then call its CLI from your country
project.

### 1. Add to your project

`pyproject.toml` of your OpenFisca country package:

```toml
[dependency-groups]
dev = [
    "openfisca-ai @ git+https://github.com/openfisca/openfisca-ai.git",
]
```

Then:

```bash
uv sync --group dev
```

### 2. Discover and read methodology guides

The methodology guides (universal principles, role guides, country-config, etc.)
are **packaged inside openfisca-ai** and accessible via the CLI from any project
that depends on it — no relative paths, no clone required.

```bash
# List all available guides
uv run openfisca-ai guide list

# Read a guide (short name or relative path)
uv run openfisca-ai guide cat principles
uv run openfisca-ai guide cat test-creator
uv run openfisca-ai guide cat 02-framework/roles/rules-engineer

# Show absolute file path of a guide (useful for editor integration)
uv run openfisca-ai guide show test-creator

# Print the root of the packaged resources directory
uv run openfisca-ai guide path
```

Available guide names:

- **Universal**: `principles`, `openfisca-basics`, `quality-checklist`,
  `country-package-baseline`, `development-workflow`
- **Framework**: `country-config`, `workflows`
- **Roles**: `document-collector`, `parameter-architect`, `rules-engineer`,
  `test-creator`, `validators`
- **Country specifics**: `03-countries/<country>/specifics`

### 3. Override or extend a guide for your project (overlay)

If your country project has specific conventions that should augment a generic
guide, drop a markdown file at the same relative path under
`docs/openfisca-ai/agents/` in your project. `openfisca-ai guide cat` will
return the generic guide followed by a `## Spécificités projet` section
containing your overlay.

Example — extend the test-creator guide for `openfisca-paris-rh`:

```
openfisca-paris-rh/
└── docs/
    └── openfisca-ai/
        └── agents/
            └── 02-framework/
                └── roles/
                    └── test-creator.md   # your overlay (project specific)
```

Then:

```bash
uv run openfisca-ai guide cat test-creator
# → generic content
# → ---
# → ## Spécificités projet
# → your overlay
```

### 4. Run the validation tools

The same CLI exposes the autonomous validation tools, runnable against any
OpenFisca country package:

```bash
cd /path/to/your/openfisca-country

uv run openfisca-ai check-all .              # full audit (preferred entrypoint)
uv run openfisca-ai validate-units .         # units coverage
uv run openfisca-ai validate-parameters .    # parameter metadata
uv run openfisca-ai validate-code .          # python formula sanity
uv run openfisca-ai validate-tests .         # test coverage
uv run openfisca-ai check-tooling .          # ruff / yamllint / uv config
uv run openfisca-ai check-package-baseline . # package baseline
uv run openfisca-ai suggest-units . --apply  # auto-fix missing units
uv run openfisca-ai extract-patterns .       # learn patterns from existing code
uv run openfisca-ai audit .                  # consolidated report
```

These tools are static, offline, and free — use them as the first line of
defense and in CI.

### 5. Use the MCP server for live, semantic checks

When your country package is served via its OpenFisca Web API
(`openfisca serve`), openfisca-ai exposes it as a set of MCP tools that an
agent can call directly. Install with the `mcp` extra:

```bash
uv add --group dev "openfisca-ai[mcp] @ git+https://github.com/openfisca/openfisca-ai.git"
```

Start the MCP server (and optionally the API as a subprocess):

```bash
uv run openfisca-ai mcp --serve              # start API + MCP server together
uv run openfisca-ai mcp --url http://localhost:5000  # use an already-running API
```

Tools exposed by the MCP server:

| Tool | Use it to |
|---|---|
| `list_entities` | Discover entity types and roles before constructing a situation |
| `list_variables` / `search_variables` | Find variables by name, description, or entity |
| `describe_variable` | Get entity, period, formula, references for one variable |
| `list_parameters` / `get_parameter` | Inspect parameter trees and historical values |
| `validate_situation` | Catch entity/variable/period errors before computing |
| `calculate` | Compute variables for a given situation |
| `trace_calculation` | Compute + return the full dependency tree and intermediate values |

**Workflow: generate a YAML test in one step**

```bash
# 1. Build a situation JSON with inputs filled and outputs set to null
# 2. Validate it (MCP):           validate_situation(situation)
# 3. Compute with full trace:     trace_calculation(situation)  → trace.json
# 4. Convert the trace into YAML:
uv run openfisca-ai generate-test-from-trace trace.json \
  --name test_my_variable \
  --reference "Article 12 du décret 2024-XXX" \
  --output tests/test_my_variable.yaml
```

This grounds the expected values in what the live system actually computes,
instead of being reconstructed by hand.

**Static tools vs. MCP — when to use each**

- Static tools (`audit`, `validate-*`): structural errors, missing metadata,
  wrong entity, no test. Free, offline, fast — use them first and in CI.
- MCP: semantic errors (formula wrong, parameter path wrong) and test fixture
  generation. Needs a live API, but is the canonical way to ground a test in
  reality.

Connect the MCP server to Claude Code (or any MCP-aware agent) by adding it
to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "openfisca": {
      "command": "uv",
      "args": ["run", "openfisca-ai", "mcp", "--serve"]
    }
  }
}
```

### 6. Tell Claude Code (or your assistant) where to look

In your project's `CLAUDE.md` (or equivalent), point the assistant at the
guide CLI rather than at relative file paths:

```markdown
## Toolkit méthodologique

Les guides et outils viennent du package openfisca-ai (dep dev).

- Lister les guides : `uv run openfisca-ai guide list`
- Lire un guide :    `uv run openfisca-ai guide cat <name>`
- Lecture obligatoire avant toute tâche :
    - `principles`
    - `openfisca-basics`
    - `quality-checklist`
- Pour générer des tests YAML : `uv run openfisca-ai guide cat test-creator`
- Outils statiques d'abord : `uv run openfisca-ai audit .`
- Pour les checks sémantiques sur le système live, démarrer le MCP server :
  `uv run openfisca-ai mcp --serve` (voir `.mcp.json`)

## Spécificités projet

[décrire ici les conventions du projet — ou créer des overlays
sous docs/openfisca-ai/agents/]
```

---

## Develop on openfisca-ai itself

If instead of consuming openfisca-ai you want to **work on it** (add a guide,
add a tool, fix a bug):

```bash
git clone https://github.com/openfisca/openfisca-ai
cd openfisca-ai
uv sync --dev
```

Configure local country paths (so the runtime can find your reference repos):

```bash
cp config/user.example.yaml config/user.yaml
# Edit config/user.yaml:
# countries.<id>.existing_code.path
# countries.<id>.legislative_sources.root
```

Validate the config and run tests:

```bash
uv run python config/test_config.py
uv run pytest
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

### 📚 Methodology guides (packaged, accessible via `openfisca-ai guide`)

**Universal Principles** (apply to all countries):
- `principles` — 14 core rules
- `country-package-baseline` — shared package structure, tooling, tests, and CI
- `quality-checklist`
- `development-workflow`

**Framework** (country-agnostic guidelines):
- `workflows`
- `country-config`
- Role guides: `document-collector`, `parameter-architect`, `rules-engineer`,
  `test-creator`, `validators`

**Country-Specific** (tested with openfisca-tunisia):
- `03-countries/tunisia/specifics`
- [Tunisia Validation Report](TUNISIA_VALIDATION_REPORT.md)

Source files live under `src/openfisca_ai/resources/agents/` and ship inside
the wheel as package data.

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
   cp src/openfisca_ai/resources/agents/03-countries/tunisia/specifics.md \
      src/openfisca_ai/resources/agents/03-countries/yourcountry/specifics.md
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

- **Issues**: https://github.com/openfisca/openfisca-ai/issues
- **OpenFisca Slack**: https://openfisca.org/community
- **Methodology guides**: `uv run openfisca-ai guide list`

---

**Built with support from Claude Code (Opus 4.6)**
