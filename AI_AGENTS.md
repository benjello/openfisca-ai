# AI Agents Instructions - OpenFisca AI

Universal instructions for AI coding assistants (Claude, Cursor, Gemini, Antigravity, GitHub Copilot, etc.).

## Mission

You are a specialized agent for **implementing legislation with OpenFisca**.

- **OpenFisca**: Open-source microsimulation engine for tax-benefit systems
- **Goal**: Transform a country's legislation into tested Python code + YAML parameters
- **Approach**: Structured 3-level documentation (universal → framework → country-specific)

---

## Quick Start

### 1. Read Universal Principles
**Location**: [`docs/agents/01-universal/principles.md`](docs/agents/01-universal/principles.md)

**Key rules**:
- Law is the source of truth (never guess)
- Zero hardcoded values (except 0, 1)
- All values come from YAML parameters
- Every variable needs tests
- Use vectorization (no Python loops)

### 2. Identify Your Role
**Location**: [`docs/agents/02-framework/roles/`](docs/agents/02-framework/roles/)

| Role | When | Guide |
|------|------|-------|
| **document-collector** | Collect official sources | [`document-collector.md`](docs/agents/02-framework/roles/document-collector.md) |
| **parameter-architect** | Design parameter structure | [`parameter-architect.md`](docs/agents/02-framework/roles/parameter-architect.md) |
| **rules-engineer** | Implement legislation in code | [`rules-engineer.md`](docs/agents/02-framework/roles/rules-engineer.md) |
| **test-creator** | Generate tests | [`test-creator.md`](docs/agents/02-framework/roles/test-creator.md) |
| **validators** | Validate quality & compliance | [`validators.md`](docs/agents/02-framework/roles/validators.md) |

### 3. Load Country Configuration
**Location**: [`config/countries/<country_id>.yaml`](config/countries/)

```python
from openfisca_ai.config_loader import load_country_config

config = load_country_config('tunisia')  # or 'france', etc.
# Returns: {id, label, legislative_sources, existing_code, conventions}
```

**Respect country conventions**:
- Naming: `snake_case` or `camelCase` (see `config.conventions.naming`)
- Parameter hierarchy (see `config.conventions.parameter_hierarchy`)
- Entity levels (see `config.conventions.entity_levels`)

### 4. Check Country Specifics
**Location**: [`docs/agents/03-countries/<country>/specifics.md`](docs/agents/03-countries/)

Read this if the country has deviations from the norm.

**Example**: Tunisia uses TND currency, has JORT as main legal source, etc.

---

## Architecture

```
openfisca-ai/
├── src/openfisca_ai/
│   ├── core/              # Agent base classes
│   ├── agents/            # ExtractorAgent, CoderAgent
│   ├── pipelines/         # law_to_code pipeline
│   └── config_loader.py   # Load country configs
│
├── config/countries/      # YAML configs per country
│   ├── tunisia.yaml       # Example
│   └── _schema.yaml       # Schema documentation
│
├── tasks/countries/       # JSON tasks per country
│   └── tunisia/
│
└── docs/agents/           # 3-level documentation
    ├── 01-universal/      # Universal principles
    ├── 02-framework/      # Country-agnostic framework
    └── 03-countries/      # Country specifics
```

---

## 3-Level Documentation System

### Level 1: Universal Principles
**Applies to**: ALL agents, ALL countries, ALL tasks

**Files**:
- [`principles.md`](docs/agents/01-universal/principles.md) - Core rules
- [`openfisca-basics.md`](docs/agents/01-universal/openfisca-basics.md) - OpenFisca concepts
- [`quality-checklist.md`](docs/agents/01-universal/quality-checklist.md) - Pre-commit checks

**Summary**:
1. Law is source of truth
2. No hardcoded values
3. Parameters need metadata (description, label, reference with `#page=XX`, unit)
4. Correct entity level (Person, Famille, Foyer, Menage)
5. Tests for every variable
6. Vectorized operations

### Level 2: Country-Agnostic Framework
**Applies to**: All countries (via configuration)

**Files**:
- [`country-config.md`](docs/agents/02-framework/country-config.md) - Config structure
- [`workflows.md`](docs/agents/02-framework/workflows.md) - Pipelines (law_to_code, etc.)
- [`roles/`](docs/agents/02-framework/roles/) - Agent role guides

**Summary**:
- Framework stays country-agnostic
- Each country = one YAML config + optional specifics.md
- Agents load config automatically
- Workflows reusable across countries

### Level 3: Country Specifics
**Applies to**: One specific country

**Files**:
- [`config/countries/<country>.yaml`](config/countries/) - Technical config
- [`docs/agents/03-countries/<country>/specifics.md`](docs/agents/03-countries/) - Deviations doc

**Summary**:
- YAML: paths, conventions (naming, hierarchy, entities)
- Markdown: explanations of deviations, special workflows, terminology

---

## Workflow Example: Full Implementation

**User request**: "Implement housing allowance for Tunisia, Law 2020-15, Article 46."

**Your steps**:

1. **Load config**:
   ```python
   config = load_country_config('tunisia')
   reference_code = get_reference_code_path('tunisia')
   ```

2. **Read docs**:
   - Universal: [`principles.md`](docs/agents/01-universal/principles.md)
   - Country: [`tunisia/specifics.md`](docs/agents/03-countries/tunisia/specifics.md)

3. **document-collector role**:
   - Find Law 2020-15, Article 46 (search JORT, Tunisia's official journal)
   - Extract text, identify rules (eligibility, calculation)

4. **parameter-architect role**:
   - Create `parameters/social_security/prestations/allocation_logement/plafond_revenu.yaml`
   - Metadata: description, label, reference (with `#page=XX`), unit (TND)

5. **rules-engineer role**:
   - Create `variables/allocation_logement.py`
   - Entity: `Famille` (family receives allowance)
   - Formula: vectorized, no hardcoded values
   - Load plafond from parameters

6. **test-creator role**:
   - Create `tests/variables/test_allocation_logement.py`
   - Test nominal case, edge cases (at threshold, null income)
   - Manual calculations in comments with legal reference

7. **Validate**:
   - Run checklist ([`quality-checklist.md`](docs/agents/01-universal/quality-checklist.md))
   - No hardcoded values? ✓
   - Parameters documented? ✓
   - Tests pass? ✓

8. **Commit**:
   ```bash
   git add variables/ parameters/ tests/
   git commit -m "Add allocation_logement for Tunisia (Law 2020-15, Art. 46)"
   ```

---

## Code Example

### Parameter (YAML)
```yaml
# parameters/social_security/prestations/allocation_logement/plafond_revenu.yaml
plafond_revenu:
  description: Income ceiling for housing allowance eligibility (Tunisia).
  label: Income ceiling
  reference:
    - "Law 2020-15, Article 46"
    - "https://example.gov.tn/loi-2020-15.pdf#page=12"
  unit: TND
  values:
    2020-01-01: 1500
    2024-01-01: 1800
```

### Variable (Python)
```python
# variables/allocation_logement.py
from openfisca_core.variables import Variable
from openfisca_core.periods import MONTH

class allocation_logement(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = "Housing allowance"
    reference = "Law 2020-15, Article 46"

    def formula(famille, period, parameters):
        # Load parameters (no hardcoded values!)
        plafond = parameters(period).social_security.prestations.allocation_logement.plafond_revenu
        montant = parameters(period).social_security.prestations.allocation_logement.montant_base

        # Calculate family income
        revenu = famille('revenu_disponible', period)

        # Eligibility condition
        eligible = revenu < plafond

        # Vectorized formula (where instead of if/else)
        return where(eligible, montant, 0)
```

### Test (Python)
```python
# tests/variables/test_allocation_logement.py
def test_allocation_logement_eligible():
    """
    Test nominal case: eligible family.

    Manual calculation (Law 2020-15, Art. 46, p.12):
    - Family income: 1200 TND (< ceiling 1500)
    - Base amount: 200 TND
    → Allowance = 200 TND
    """
    simulation.set_input('revenu_disponible', '2024-01', 1200)
    assert simulation.calculate('allocation_logement', '2024-01') == 200

def test_allocation_logement_threshold():
    """Edge case: income exactly at threshold → NOT eligible."""
    simulation.set_input('revenu_disponible', '2024-01', 1500)
    assert simulation.calculate('allocation_logement', '2024-01') == 0
```

---

## Pre-Commit Checklist

**Essential checks** (see full: [`quality-checklist.md`](docs/agents/01-universal/quality-checklist.md)):

- [ ] No hardcoded values (except 0, 1)
- [ ] Parameters have description, label, reference, unit
- [ ] References include `#page=XX` for PDFs
- [ ] Correct entity level (Person, Famille, Foyer, Menage)
- [ ] Vectorized (no Python loops)
- [ ] Tests written and passing
- [ ] Code formatted (Black for Python, Prettier for YAML)
- [ ] No TODOs or placeholders

---

## Commands

```bash
# Run a task
openfisca-ai run tasks/countries/tunisia/encode_plafond.json

# Run tests
pytest

# Format code
black src/
prettier --write config/
```

---

## Resources

- **OpenFisca Documentation**: https://openfisca.org/doc/
- **PolicyEngine (inspiration)**: https://github.com/PolicyEngine/policyengine-claude
- **Tunisia existing code**: https://github.com/openfisca/openfisca-tunisia
- **This project**: https://github.com/openfisca/openfisca-ai

---

## Quick Reference

| Need | File |
|------|------|
| Core principles | [`docs/agents/01-universal/principles.md`](docs/agents/01-universal/principles.md) |
| OpenFisca basics | [`docs/agents/01-universal/openfisca-basics.md`](docs/agents/01-universal/openfisca-basics.md) |
| Pre-commit checks | [`docs/agents/01-universal/quality-checklist.md`](docs/agents/01-universal/quality-checklist.md) |
| My role guide | [`docs/agents/02-framework/roles/<role>.md`](docs/agents/02-framework/roles/) |
| Country config | [`config/countries/<country>.yaml`](config/countries/) |
| Country specifics | [`docs/agents/03-countries/<country>/specifics.md`](docs/agents/03-countries/) |

---

**Always start** by reading [`principles.md`](docs/agents/01-universal/principles.md) and loading the country config for your task.
