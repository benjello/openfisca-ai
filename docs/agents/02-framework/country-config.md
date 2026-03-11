# Country Configuration

How to configure a country in OpenFisca AI so all agents can use it.

## Principle

The framework remains **country-agnostic**. Each country = **one YAML configuration file**.

Agents automatically load the config via `config_loader.py`:
```python
from openfisca_ai.config_loader import load_country_config, get_reference_code_path

config = load_country_config('countria')
reference_code = get_reference_code_path('countria')
```

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
countries:
  countria:
    legislative_sources:
      root: /home/user/docs/countria-laws
    existing_code:
      path: /home/user/repos/openfisca-countria
```

The `config_loader` automatically **merges** `user.yaml` with `countria.yaml`.

### Alternative: `~/.config/openfisca-ai/user.yaml`
If `config/user.yaml` doesn't exist, the loader looks in `~/.config/openfisca-ai/user.yaml`.

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

### In a pipeline
```python
# pipelines/law_to_code.py
def run_law_to_code(law_text, country_id='countria', ...):
    config = load_country_config(country_id)
    reference_code = get_reference_code_path(country_id)

    # Pass to agents
    coder = CoderAgent(...)
    result = coder.run(
        extracted=...,
        reference_code_path=reference_code,
        country_config=config
    )
```

### In an agent
```python
# agents/coder.py
class CoderAgent(Agent):
    def run(self, extracted, reference_code_path=None, country_config=None):
        if country_config:
            conventions = country_config.get('conventions', {})
            naming = conventions.get('naming', 'snake_case')
            # Adapt code generation according to conventions
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
countries:
  newland:
    legislative_sources:
      root: /home/me/newland-laws
    existing_code:
      path: /home/me/openfisca-newland
```

### 3. (Optional) Document specifics
If the country has **deviations** from the norm, create:
`docs/agents/03-countries/newland/specifics.md`

See [template](../03-countries/_template.md).

### 4. Create tasks
`tasks/countries/newland/encode_benefit.json`:
```json
{
  "id": "encode_benefit",
  "country": "newland",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Section 12 of the Social Benefits Act..."
  }
}
```

### 5. Test
```bash
openfisca-ai run tasks/countries/newland/encode_benefit.json
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
| Local paths | `config/user.yaml` or `~/.config/openfisca-ai/user.yaml` | Machine-specific paths (gitignored) |
| Specifics | `docs/agents/03-countries/<country>/specifics.md` | Deviations from norm (documentation) |
| Tasks | `tasks/countries/<country>/*.json` | Country-specific tasks |

---

**Next steps**:
- See [workflows.md](workflows.md) for pipelines using these configs
- See [../03-countries/_template.md](../03-countries/_template.md) for new country template
