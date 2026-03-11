# Development Workflow - Universal Practices

Best practices for working with OpenFisca country packages.

---

## 1. Use `uv` for Environment Management

**ALL OpenFisca packages use `uv`** for fast, reliable dependency management.

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### Setup

```bash
cd /path/to/openfisca-country

# Install package in development mode
make install
# OR
uv sync --extra dev
```

---

## 2. Run Scripts in Package Environment

**IMPORTANT**: Always run validation scripts **inside the package's venv** using `uv run`.

### ❌ Wrong (global environment)
```bash
# DON'T DO THIS
python tools/validate_units.py /path/to/openfisca-country
```

### ✅ Correct (package environment)
```bash
cd /path/to/openfisca-country

# Use uv run to execute in venv
uv run python /path/to/openfisca-ai/tools/validate_units.py .
```

---

## 3. Makefile Targets

All OpenFisca packages follow a **standard Makefile** pattern:

```makefile
# Use uv for all commands
UV = uv run

# Standard targets
install:    # Install package in dev mode
test:       # Run all tests
check-style:  # Check code style (ruff)
format-style: # Format code (ruff)
check-yaml:   # Validate YAML files
```

### Common Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format-style

# Check code quality
make check-style

# Validate YAML parameters
make check-all-yaml
```

---

## 4. Code Quality Tools

### Ruff (Linter + Formatter)

**Modern all-in-one** tool for Python code quality.

```bash
# Format code
uv run ruff format .

# Check/fix linting issues
uv run ruff check --fix .
```

### Yamllint (YAML Validation)

```bash
# Check all parameters
uv run yamllint openfisca_tunisia/parameters

# Check tests
uv run yamllint tests
```

---

## 5. Running Validation Tools

### From openfisca-ai tools/

```bash
cd /path/to/openfisca-country

# Validate units (in package venv)
uv run python /path/to/openfisca-ai/tools/validate_units.py .

# Suggest missing units
uv run python /path/to/openfisca-ai/tools/suggest_units.py .

# Apply suggestions
uv run python /path/to/openfisca-ai/tools/suggest_units.py . --apply
```

### Add to Makefile (recommended)

```makefile
# Add to country package Makefile
check-units:
	$(UV) python /path/to/openfisca-ai/tools/validate_units.py .

suggest-units:
	$(UV) python /path/to/openfisca-ai/tools/suggest_units.py .
```

Then use:
```bash
make check-units
make suggest-units
```

---

## 6. Testing Workflow

```bash
cd /path/to/openfisca-country

# 1. Install
make install

# 2. Make changes to parameters/variables

# 3. Format code
make format-style

# 4. Validate
make check-style
make check-all-yaml
uv run python /path/to/openfisca-ai/tools/validate_units.py .

# 5. Run tests
make test

# 6. Commit (if all passes)
git add .
git commit -m "Your message

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 7. CI/CD Integration

Add validation to GitHub Actions:

```yaml
# .github/workflows/validate.yml
name: Validate

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install package
        run: make install

      - name: Check style
        run: make check-style

      - name: Validate YAML
        run: make check-all-yaml

      - name: Validate units
        run: uv run python ../openfisca-ai/tools/validate_units.py .

      - name: Run tests
        run: make test
```

---

## 8. Why `uv`?

**Speed**: 10-100x faster than pip

```
pip install:   45s
uv sync:       2s
```

**Reliability**: Deterministic dependency resolution

**Compatibility**: Drop-in replacement for pip/venv

---

## 9. Environment Variables

```bash
# Optional: speed up uv with caching
export UV_CACHE_DIR=~/.cache/uv

# Use specific Python version
export UV_PYTHON=python3.11
```

---

## 10. Troubleshooting

### "Package not found"
```bash
# Re-sync environment
uv sync --extra dev
```

### "Import error"
```bash
# Ensure you're using uv run
uv run python script.py  # ✅
python script.py         # ❌
```

### "Wrong Python version"
```bash
# Check Python version
uv run python --version

# Force specific version
UV_PYTHON=python3.11 uv sync
```

---

## Summary

| Task | Command |
|------|---------|
| Setup | `make install` or `uv sync --extra dev` |
| Format | `make format-style` |
| Validate | `make check-style && make check-all-yaml` |
| Test | `make test` |
| Validate units | `uv run python tools/validate_units.py .` |

**Golden rule**: Always use `uv run` or `make` targets, never bare `python` commands!

---

**See also**:
- [Universal Principles](principles.md)
- [Quality Checklist](quality-checklist.md)
- [Tools README](../../tools/README.md)
