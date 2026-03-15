# Local Configuration Guide

This repository is designed to be shared by multiple users. Each user needs to configure their own local paths to their OpenFisca country packages.

---

## Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
cd openfisca-ai
uv sync --dev
uv run python config/setup.py
```

This creates `config/user.yaml` with your local paths.

### Option 2: Manual Setup

```bash
cd openfisca-ai
uv sync --dev
cp config/user.yaml.template config/user.yaml
# Edit config/user.yaml with your paths
```

---

## Configuration Options

### Simple Single Country

If you only work with one country:

```yaml
# config/user.yaml
base_path: /home/yourname/projets
legislation_base_path: /home/yourname/legislation
active_country: tunisia
countries:
  tunisia:
    existing_code:
      path: ${base_path}/openfisca-tunisia
    legislative_sources:
      root: ${legislation_base_path}/tunisia
```

### Multiple Countries with Shared Base Path

If all your OpenFisca repos are in the same parent directory (recommended):

```yaml
# config/user.yaml
base_path: /home/yourname/projets
legislation_base_path: /home/yourname/legislation
active_country: tunisia
countries:
  tunisia:
    existing_code:
      path: ${base_path}/openfisca-tunisia
    legislative_sources:
      root: ${legislation_base_path}/tunisia
  france:
    existing_code:
      path: ${base_path}/openfisca-france
    legislative_sources:
      root: ${legislation_base_path}/france
  senegal:
    existing_code:
      path: ${base_path}/openfisca-senegal
    legislative_sources:
      root: ${legislation_base_path}/senegal
```

### Multiple Countries with Different Locations

If your repos are in different directories:

```yaml
# config/user.yaml
active_country: tunisia
countries:
  tunisia:
    existing_code:
      path: /home/yourname/work/openfisca-tunisia
    legislative_sources:
      root: /home/yourname/laws/tunisia
  france:
    existing_code:
      path: /mnt/shared/openfisca-france
    legislative_sources:
      root: /mnt/shared/laws/france
  local_test:
    existing_code:
      path: /tmp/openfisca-test-country
```

### Legacy Config Compatibility

Older configs using `countries.<id>.path` are still supported, but deprecated. The loader normalizes them internally to `existing_code.path`.

---

## Alternative: Global Configuration

Instead of `config/user.yaml`, you can use a global configuration file:

**Location**: `~/.config/openfisca-ai/user.yaml`

**Advantages**:
- Shared across all openfisca-ai clones
- Never risk committing by accident

**Setup**:

```bash
mkdir -p ~/.config/openfisca-ai
cp config/user.yaml.template ~/.config/openfisca-ai/user.yaml
# Edit ~/.config/openfisca-ai/user.yaml
```

Legacy fallback still supported: `~/.config/openfisca-ai/config.yaml`.

**Priority**:
1. `config/user.yaml` (local, highest priority)
2. `~/.config/openfisca-ai/user.yaml` (global)
3. `~/.config/openfisca-ai/config.yaml` (legacy global)
4. Environment variables referenced by `${...}` placeholders

---

## Alternative: Environment Variables

For CI/CD or temporary overrides used inside `config/user.yaml` or `config/countries/*.yaml`:

```bash
# Set specific country path
export OPENFISCA_TUNISIA_PATH=/home/user/projets/openfisca-tunisia
export OPENFISCA_TUNISIA_LAWS=/home/user/legislation/tunisia

# Example user.yaml entries:
# countries:
#   tunisia:
#     existing_code:
#       path: ${OPENFISCA_TUNISIA_PATH}
#     legislative_sources:
#       root: ${OPENFISCA_TUNISIA_LAWS}
```

---

## Verifying Configuration

After setup, verify your configuration:

```bash
# Check config file exists
ls -la config/user.yaml

# Validate and resolve configured paths
uv run python config/test_config.py
```

---

## Sharing the Repository

### When contributing

**NEVER commit your `config/user.yaml`**. It's in `.gitignore` but double-check:

```bash
git status
# Should NOT show config/user.yaml
```

### When cloning from GitHub

After cloning:

```bash
cd openfisca-ai
uv sync --dev
uv run python config/setup.py  # Interactive setup
# OR
cp config/user.yaml.template config/user.yaml
# Edit config/user.yaml
```

---

## Example Workflows

### Workflow 1: Validate Tunisia

```bash
# Your config/user.yaml
active_country: tunisia
base_path: /home/alice/repos
legislation_base_path: /home/alice/legislation
countries:
  tunisia:
    existing_code:
      path: ${base_path}/openfisca-tunisia
    legislative_sources:
      root: ${legislation_base_path}/tunisia

# Run validation
cd /home/alice/repos/openfisca-tunisia
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/suggest_units.py .
```

### Workflow 2: Test Multiple Countries

```bash
# Your config/user.yaml
base_path: /home/bob/openfisca-projects
legislation_base_path: /home/bob/legislation
active_country: senegal
countries:
  tunisia:
    existing_code:
      path: ${base_path}/openfisca-tunisia
  senegal:
    existing_code:
      path: ${base_path}/openfisca-senegal
  france:
    existing_code:
      path: ${base_path}/openfisca-france

# Validate all
for country in tunisia senegal france; do
  cd ${base_path}/openfisca-${country}
  echo "Validating ${country}..."
  uv run python /path/to/openfisca-ai/tools/validate_units.py .
done
```

---

## Troubleshooting

### "Path not found" error

Check your config:
```bash
cat config/user.yaml
# Verify paths are correct
```

### Config file not loading

Priority order:
1. `config/user.yaml` (check this first)
2. `~/.config/openfisca-ai/user.yaml`
3. `~/.config/openfisca-ai/config.yaml` (legacy)
4. Environment variables referenced by `${...}`

### Accidentally committed user.yaml

```bash
# Remove from git but keep locally
git rm --cached config/user.yaml
git commit -m "Remove accidentally committed user config"

# Verify .gitignore has:
cat .gitignore | grep user.yaml
```

---

## Summary

| Method | Location | Use Case |
|--------|----------|----------|
| **Interactive setup** | `uv run python config/setup.py` | First-time setup (recommended) |
| **Manual config** | `config/user.yaml` | Full control, local to repo |
| **Global config** | `~/.config/openfisca-ai/user.yaml` | Shared across all clones |
| **Legacy global config** | `~/.config/openfisca-ai/config.yaml` | Backward compatibility |
| **Environment vars** | `${OPENFISCA_*}` placeholders | CI/CD, temporary overrides |

**Best practice**: Use `config/user.yaml` with `base_path` and the canonical nested keys.

---

## See Also

- [Development Workflow](../agents/01-universal/development-workflow.md)
- [Validation Tools](../../tools/README.md)
- [Country Configuration](../agents/02-framework/country-config.md)
