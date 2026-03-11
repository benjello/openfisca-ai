# Local Configuration Guide

This repository is designed to be shared by multiple users. Each user needs to configure their own local paths to their OpenFisca country packages.

---

## Quick Start

### Option 1: Interactive Setup (Recommended)

```bash
cd openfisca-ai
python config/setup.py
```

This creates `config/user.yaml` with your local paths.

### Option 2: Manual Setup

```bash
cd openfisca-ai
cp config/user.yaml.template config/user.yaml
# Edit config/user.yaml with your paths
```

---

## Configuration Options

### Simple Single Country

If you only work with one country:

```yaml
# config/user.yaml
active_country: tunisia
countries:
  tunisia:
    path: /home/yourname/projets/openfisca-tunisia
```

### Multiple Countries with Shared Base Path

If all your OpenFisca repos are in the same parent directory (recommended):

```yaml
# config/user.yaml
base_path: /home/yourname/projets
active_country: tunisia
countries:
  tunisia:
    path: ${base_path}/openfisca-tunisia
  france:
    path: ${base_path}/openfisca-france
  senegal:
    path: ${base_path}/openfisca-senegal
```

### Multiple Countries with Different Locations

If your repos are in different directories:

```yaml
# config/user.yaml
active_country: tunisia
countries:
  tunisia:
    path: /home/yourname/work/openfisca-tunisia
  france:
    path: /mnt/shared/openfisca-france
  local_test:
    path: /tmp/openfisca-test-country
```

---

## Alternative: Global Configuration

Instead of `config/user.yaml`, you can use a global configuration file:

**Location**: `~/.config/openfisca-ai/config.yaml`

**Advantages**:
- Shared across all openfisca-ai clones
- Never risk committing by accident

**Setup**:

```bash
mkdir -p ~/.config/openfisca-ai
cp config/user.yaml.template ~/.config/openfisca-ai/config.yaml
# Edit ~/.config/openfisca-ai/config.yaml
```

**Priority**:
1. `config/user.yaml` (local, highest priority)
2. `~/.config/openfisca-ai/config.yaml` (global)
3. Environment variables (see below)

---

## Alternative: Environment Variables

For CI/CD or temporary overrides:

```bash
# Set base path
export OPENFISCA_AI_BASE_PATH=/home/user/projets

# Set specific country path
export OPENFISCA_TUNISIA_PATH=/home/user/projets/openfisca-tunisia

# Run tools
cd $OPENFISCA_TUNISIA_PATH
uv run python /path/to/openfisca-ai/tools/validate_units.py .
```

---

## Verifying Configuration

After setup, verify your configuration:

```bash
# Check config file exists
ls -la config/user.yaml

# Try running a validation tool
cd /path/to/your/openfisca-tunisia
uv run python /path/to/openfisca-ai/tools/validate_units.py .
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
python config/setup.py  # Interactive setup
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
countries:
  tunisia:
    path: ${base_path}/openfisca-tunisia

# Run validation
cd /home/alice/repos/openfisca-tunisia
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/suggest_units.py .
```

### Workflow 2: Test Multiple Countries

```bash
# Your config/user.yaml
base_path: /home/bob/openfisca-projects
active_country: senegal
countries:
  tunisia:
    path: ${base_path}/openfisca-tunisia
  senegal:
    path: ${base_path}/openfisca-senegal
  france:
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
2. `~/.config/openfisca-ai/config.yaml`
3. Environment variables

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
| **Interactive setup** | `python config/setup.py` | First-time setup (recommended) |
| **Manual config** | `config/user.yaml` | Full control, local to repo |
| **Global config** | `~/.config/openfisca-ai/config.yaml` | Shared across all clones |
| **Environment vars** | `export OPENFISCA_*_PATH=...` | CI/CD, temporary overrides |

**Best practice**: Use `config/user.yaml` with `base_path` for simplicity.

---

## See Also

- [Development Workflow](../agents/01-universal/development-workflow.md)
- [Validation Tools](../../tools/README.md)
- [Country Configuration](../agents/02-framework/country-config.md)
