# Country Configuration

How to configure a country in OpenFisca AI so all agents can use it.

## Principle

The framework remains **country-agnostic**. Each country = **one YAML configuration file**.

The Python runtime can load the config via `config_loader.py`:
```python
from openfisca_ai.config_loader import load_country_config, get_reference_code_path

config = load_country_config('countria')
reference_code = get_reference_code_path('countria')
```

If `reference_code` exists, the alpha runtime can also analyze that package with:

```python
from openfisca_ai.core.reference_package import analyze_reference_package

analysis = analyze_reference_package(reference_code, include_audit_summary=True)
```

If your extraction phase already produced structured variables and parameters,
the current runtime can turn them into scaffolding artifacts without writing to
disk.

If you want those artifacts materialized, pass `options.output_dir` in the task
JSON. The CLI resolves it relative to the task file location.

If you want to apply them directly inside the configured country package, pass
`options.apply_artifacts_to_reference_package: true`. The runtime resolves the
repository root from `existing_code.path` and writes there.

If you want a dry run first, pass `options.plan_only: true`. The runtime then
returns an `artifact_write_plan` with diff previews but does not write files.

If generated paths already exist, choose a conflict strategy with
`options.existing_artifact_strategy`:

- `create`
- `skip`
- `append`
- `update`

## Config File Structure

`config/countries/<country>.yaml`:

```yaml
id: countria
label: Countria

# Legislative sources (laws, decrees, manuals)
legislative_sources:
  root: /path/to/countria-law-docs
  # Optional:
  # file_pattern: "*.md"
  # index_file: sources.md

# Existing OpenFisca code (for reference)
existing_code:
  path: /path/to/openfisca-countria
  # Optional:
  # main_package: openfisca_countria

# Conventions (extensible as needed)
conventions:
  parameter_hierarchy:
    - gov
    - social_benefits
    - taxation
  entity_levels:
    - Person
    - Family
    - Household
    - TaxUnit
  naming: snake_case
  # Other conventions as needed
```

## Required Fields

### `id` (string)
Unique country identifier (lowercase, no spaces).
Used in tasks: `"country": "countria"`.

### `label` (string)
Displayed country name (for logs and UI).

## Optional Fields

### `legislative_sources` (dict)
Paths to legislative sources.

**Fields**:
- `root`: root directory of documents
- `file_pattern`: file pattern (e.g., `"*.md"`, `"*.pdf"`)
- `index_file`: index file listing sources

**Usage**: `document-collector` reads these paths to search/organize sources.

### `existing_code` (dict)
Path to existing OpenFisca code for the country.

**Fields**:
- `path`: package directory (e.g., `/path/to/openfisca-countria`)
- `main_package`: Python package name (e.g., `openfisca_countria`)

**Usage**: `rules-engineer` and `validators` use this code as **reference** for patterns and conventions.

### `conventions` (dict)
Country-specific conventions (extensible).

**Standard fields**:
- `parameter_hierarchy`: list of hierarchy levels (e.g., `[gov, social_benefits, taxation]`)
- `entity_levels`: list of entities (e.g., `[Person, Family, Household]`)

**Note**: Naming convention is **always `snake_case`** (universal OpenFisca standard, see [Principle 14](../01-universal/principles.md#14-formatting-and-naming)).

**Custom fields**: Add as needed (e.g., `tax_terminology`, `validation_workflow`).

## Local Paths (not in git)

To keep local paths **out of git**, use `config/user.yaml`:

### Create `config/user.yaml` (gitignored)
```yaml
base_path: /home/user/repos
legislation_base_path: /home/user/laws

countries:
  countria:
    existing_code:
      path: ${base_path}/openfisca-countria
    legislative_sources:
      root: ${legislation_base_path}/countria
```

The `config_loader` automatically **merges** `user.yaml` with `countria.yaml`, expands `${...}` placeholders from top-level values and environment variables, then resolves relative paths from the project root.

### Alternative: global config file
If `config/user.yaml` doesn't exist, the loader looks in:
1. `~/.config/openfisca-ai/user.yaml` (canonical)
2. `~/.config/openfisca-ai/config.yaml` (legacy compatibility)

## Usage in Code

### Load config
```python
from openfisca_ai.config_loader import load_country_config

config = load_country_config('countria')
# Returns dict with id, label, legislative_sources, existing_code, conventions
```

### Get existing code path
```python
from openfisca_ai.config_loader import get_reference_code_path

path = get_reference_code_path('countria')
# Returns Path or None
```

### Get legislative sources root
```python
from openfisca_ai.config_loader import get_legislative_sources_root

path = get_legislative_sources_root('countria')
# Returns Path or None
```

### In a pipeline
```python
# pipelines/law_to_code.py
from openfisca_ai.core.reference_package import (
    analyze_reference_package,
    build_implementation_brief,
)


def run_law_to_code(law_text, country_id='countria', ...):
    config = load_country_config(country_id)
    reference_code = get_reference_code_path(country_id)
    reference_analysis = analyze_reference_package(reference_code)

    # Pass to agents
    coder = CoderAgent(...)
    result = coder.run(
        extracted=...,
        reference_code_path=reference_code,
        country_config=config,
        reference_package_analysis=reference_analysis,
        implementation_brief=build_implementation_brief(
            extracted=...,
            country_config=config,
            reference_package_analysis=reference_analysis,
            country_id=country_id,
        ),
    )
    # result['artifacts'] now contains target paths + file contents
    # the pipeline can also write them when an output directory is provided
    # or directly into the configured reference package when requested
    # artifact_write_plan provides diff previews before any write
```

### In an agent
```python
# agents/coder.py
class CoderAgent(Agent):
    def run(self, extracted, reference_code_path=None, country_config=None, reference_package_analysis=None, implementation_brief=None):
        if country_config:
            conventions = country_config.get('conventions', {})
            naming = conventions.get('naming', 'snake_case')
            # Adapt code generation according to conventions
        if reference_package_analysis:
            pattern_summary = reference_package_analysis['pattern_summary']
            # Use package patterns as generation context
        if implementation_brief:
            scaffolding = implementation_brief['scaffolding']
            # Use variable_root / parameter_root / tests_root for output targeting
        ...
```

## Adding a New Country

### 1. Create config file
`config/countries/newland.yaml`:
```yaml
id: newland
label: Newland
legislative_sources:
  root: /data/newland-legislation
existing_code:
  path: /repos/openfisca-newland
  main_package: openfisca_newland
conventions:
  parameter_hierarchy: [gov, social_benefits, taxation]
  entity_levels: [Person, Family, Household, TaxUnit]
  naming: snake_case
```

### 2. (Optional) Add local paths
`config/user.yaml`:
```yaml
base_path: /home/me/repos
legislation_base_path: /home/me/laws

countries:
  newland:
    existing_code:
      path: ${base_path}/openfisca-newland
    legislative_sources:
      root: ${legislation_base_path}/newland
```

### 3. (Optional) Document specifics
If the country has **deviations** from the norm, create:
`src/openfisca_ai/resources/agents/03-countries/newland/specifics.md`

See [template](../03-countries/_template.md).

### 4. Create tasks
`tasks/countries/newland/encode_benefit.json`:
```json
{
  "id": "encode_benefit",
  "country": "newland",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Section 12 of the Social Benefits Act...",
    "extracted": {
      "variables": [
        {
          "name": "housing_allowance",
          "entity": "Household",
          "definition_period": "MONTH",
          "value_type": "float",
          "parameter": "social_benefits.housing_allowance.base_amount"
        }
      ],
      "parameters": [
        {
          "name": "social_benefits.housing_allowance.base_amount",
          "label": "Housing allowance base amount",
          "description": "Base amount used for the housing allowance.",
          "unit": "currency",
          "value": 100
        }
      ]
    }
  },
  "options": {
    "use_existing_code_as_reference": true,
    "include_reference_audit_summary": true,
    "apply_artifacts_to_reference_package": true,
    "plan_only": true,
    "existing_artifact_strategy": "skip"
  }
}
```

This application mode refuses to overwrite existing files unless
`overwrite_artifacts` is explicitly set to `true`.

### 5. Test
```bash
uv run openfisca-ai run tasks/countries/newland/encode_benefit.json
```

## Schema Validation

To validate config files, see `config/countries/_schema.yaml`.

Automatic validation (optional):
```bash
yamllint config/countries/countria.yaml
# Or with JSON Schema if _schema.yaml is in JSON Schema format
```

## Summary

| Element | File | Usage |
|---------|------|-------|
| Public config | `config/countries/<country>.yaml` | Structure, conventions (versioned in git) |
| Local paths | `config/user.yaml` | Machine-specific paths (gitignored) |
| Global fallback | `~/.config/openfisca-ai/user.yaml` or `~/.config/openfisca-ai/config.yaml` | Shared machine-level config |
| Specifics | `src/openfisca_ai/resources/agents/03-countries/<country>/specifics.md` | Deviations from norm (documentation) |
| Tasks | `tasks/countries/<country>/*.json` | Country-specific tasks |

---

**Next steps**:
- See [workflows.md](workflows.md) for pipelines using these configs
- See [../03-countries/_template.md](../03-countries/_template.md) for new country template
