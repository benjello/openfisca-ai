# OpenFisca AI - Agent Instructions Repository

AI coding assistant instructions for working with [OpenFisca](https://openfisca.org) country packages.

Designed for agents like **Cursor**, **Claude Code**, **Gemini**, **Antigravity**, etc.

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/openfisca-ai
cd openfisca-ai
```

### 2. Configure Local Paths

**Option A - Interactive (recommended)**:
```bash
python config/setup.py
```

**Option B - Manual**:
```bash
cp config/user.yaml.template config/user.yaml
# Edit config/user.yaml with your local paths
```

See [Local Configuration Guide](docs/setup/local-configuration.md) for details.

### 3. Use Validation Tools

```bash
cd /path/to/your/openfisca-country
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/suggest_units.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
```

---

## What's Inside

### 📚 Documentation

**Universal Principles** (apply to all countries):
- [Universal Principles](docs/agents/01-universal/principles.md) - 14 core rules
- [Quality Checklist](docs/agents/01-universal/quality-checklist.md)
- [Development Workflow](docs/agents/01-universal/development-workflow.md)

**Framework** (country-agnostic guidelines):
- [Parameter Management](docs/agents/02-framework/parameter-management.md)
- [Variable Coding](docs/agents/02-framework/variable-coding.md)
- [Testing Patterns](docs/agents/02-framework/testing-patterns.md)
- [Common Patterns](docs/agents/02-framework/common-patterns.md)
- [Country Configuration](docs/agents/02-framework/country-config.md)

**Country-Specific** (tested with openfisca-tunisia):
- [Tunisia Specifics](docs/agents/03-countries/tunisia/specifics.md)
- [Tunisia Validation Report](TUNISIA_VALIDATION_REPORT.md)

### 🛠️ Validation Tools

**Autonomous tools that work without AI agents** (fast, free, CI-ready):

- **[validate_units.py](tools/validate_units.py)** - Check all parameters have units
- **[suggest_units.py](tools/suggest_units.py)** - Auto-suggest missing units
- **[check_tooling.py](tools/check_tooling.py)** - Verify modern tooling (uv, ruff, yamllint)

See [Tools README](tools/README.md) for usage.

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
- ✅ Tunisia tested (439 parameters)

### Next (v0.2)
- [ ] validate_code.py - Check Python formulas
- [ ] validate_tests.py - Ensure test coverage
- [ ] extract_patterns.py - Learn from existing code
- [ ] Test with openfisca-france

### Future (v0.3)
- [ ] Agent integration (Cursor, Claude Code, etc.)
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
