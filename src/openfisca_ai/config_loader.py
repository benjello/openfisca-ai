"""Load country configs for use by pipelines and agents."""

import os
from pathlib import Path
from typing import Any

# Default base path: project root (parent of src). Overridable for tests.
_CONFIG_BASE = Path(__file__).resolve().parent.parent.parent  # openfisca-ai/


def _project_root() -> Path:
    """Root directory for config (OPENFISCA_AI_ROOT, or repo root, or cwd)."""
    if os.environ.get("OPENFISCA_AI_ROOT"):
        return Path(os.environ["OPENFISCA_AI_ROOT"])
    for root in [_CONFIG_BASE, Path.cwd()]:
        if (root / "config" / "countries").exists():
            return root
    return _CONFIG_BASE


def get_countries_dir() -> Path:
    """Return the directory containing country YAML configs."""
    return _project_root() / "config" / "countries"


def _user_config_path() -> Path | None:
    """
    Path to the user's local config (paths only, gitignored).
    Prefer config/user.yaml in project, then ~/.config/openfisca-ai/user.yaml.
    """
    root = _project_root()
    local = root / "config" / "user.yaml"
    if local.exists():
        return local
    xdg = Path.home() / ".config" / "openfisca-ai" / "user.yaml"
    return xdg if xdg.exists() else None


def _load_user_config() -> dict[str, Any]:
    """Load user config (countries.* path overrides). Returns {} if missing or invalid."""
    path = _user_config_path()
    if not path:
        return {}
    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base. Override values take precedence."""
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_country_config(country_id: str) -> dict[str, Any] | None:
    """
    Load a country config by id (e.g. 'tunisia').
    Merges config/countries/<country_id>.yaml with the user's config/user.yaml
    (or ~/.config/openfisca-ai/user.yaml) so local paths stay private and out of git.
    Returns None if the country file does not exist.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for country config. Install with: pip install pyyaml")

    path = get_countries_dir() / f"{country_id}.yaml"
    if not path.exists():
        return None

    with open(path) as f:
        base = yaml.safe_load(f)

    if not isinstance(base, dict):
        return None

    user = _load_user_config()
    overrides = (user.get("countries") or {}).get(country_id)
    if isinstance(overrides, dict):
        base = _deep_merge(base, overrides)

    return base


def get_reference_code_path(country_id: str) -> Path | None:
    """
    Return the path to existing OpenFisca code for this country, if configured.
    """
    config = load_country_config(country_id)
    if not config:
        return None

    existing = config.get("existing_code") or {}
    raw = existing.get("path")
    if not raw:
        return None

    p = Path(raw)
    return p if p.is_absolute() else (_project_root() / raw)
