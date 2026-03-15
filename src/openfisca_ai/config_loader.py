"""Load country configs for use by pipelines and agents."""

import os
import re
from pathlib import Path
from typing import Any

# Default base path: project root (parent of src). Overridable for tests.
_CONFIG_BASE = Path(__file__).resolve().parent.parent.parent  # openfisca-ai/
_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


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


def get_user_config_path() -> Path | None:
    """
    Path to the user's local config (paths only, gitignored).
    Prefer config/user.yaml in project, then XDG config files.

    Supports both ~/.config/openfisca-ai/user.yaml (canonical) and
    ~/.config/openfisca-ai/config.yaml (legacy).
    """
    root = _project_root()
    local = root / "config" / "user.yaml"
    if local.exists():
        return local

    xdg_dir = Path.home() / ".config" / "openfisca-ai"
    for name in ("user.yaml", "config.yaml"):
        path = xdg_dir / name
        if path.exists():
            return path

    return None


def _user_config_path() -> Path | None:
    """Backward-compatible private alias."""
    return get_user_config_path()


def _expand_vars(value: str, context: dict[str, str]) -> str:
    """Expand ${var} placeholders from context first, then environment."""

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in context and context[key] not in (None, ""):
            return context[key]

        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value

        return match.group(0)

    expanded = value
    for _ in range(10):
        updated = _VAR_PATTERN.sub(replace, expanded)
        if updated == expanded:
            break
        expanded = updated
    return expanded


def _expand_placeholders(value: Any, context: dict[str, str]) -> Any:
    """Recursively expand ${...} placeholders in config values."""
    if isinstance(value, str):
        return _expand_vars(value, context)
    if isinstance(value, list):
        return [_expand_placeholders(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _expand_placeholders(item, context) for key, item in value.items()}
    return value


def _normalize_user_config(data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize user config to the canonical schema.

    Canonical shape:
      countries.<id>.existing_code.path
      countries.<id>.legislative_sources.root

    Legacy shapes still supported:
      countries.<id>.path
      legislative_sources.<id> = /path/to/laws
    """
    if not isinstance(data, dict):
        return {}

    normalized = dict(data)
    raw_countries = normalized.get("countries")
    legacy_sources = normalized.get("legislative_sources")

    if not isinstance(raw_countries, dict):
        normalized["countries"] = {}
        return normalized

    countries: dict[str, Any] = {}
    for country_id, raw_settings in raw_countries.items():
        if isinstance(raw_settings, str):
            settings: dict[str, Any] = {"path": raw_settings}
        elif isinstance(raw_settings, dict):
            settings = dict(raw_settings)
        else:
            continue

        legacy_path = settings.pop("path", None)
        existing_code = settings.get("existing_code")
        if legacy_path and not (isinstance(existing_code, dict) and existing_code.get("path")):
            settings = _deep_merge(settings, {"existing_code": {"path": legacy_path}})

        if isinstance(legacy_sources, dict):
            legacy_source_root = legacy_sources.get(country_id)
            source_settings = settings.get("legislative_sources")
            if legacy_source_root and not (isinstance(source_settings, dict) and source_settings.get("root")):
                settings = _deep_merge(settings, {"legislative_sources": {"root": legacy_source_root}})

        countries[country_id] = settings

    normalized["countries"] = countries
    return normalized


def _resolve_project_path(raw: str | None) -> str | None:
    """Resolve a path-like config value relative to the project root."""
    if not raw or not isinstance(raw, str):
        return raw
    if "${" in raw:
        return raw

    path = Path(raw).expanduser()
    if path.is_absolute():
        return str(path)

    return str((_project_root() / path).resolve())


def _resolve_country_paths(config: dict[str, Any]) -> dict[str, Any]:
    """Resolve known path fields to absolute paths."""
    for section, key in (
        ("legislative_sources", "root"),
        ("existing_code", "path"),
    ):
        section_value = config.get(section)
        if isinstance(section_value, dict):
            resolved = _resolve_project_path(section_value.get(key))
            if resolved is not None:
                section_value[key] = resolved

    return config


def _load_user_config() -> dict[str, Any]:
    """Load user config (countries.* path overrides). Returns {} if missing or invalid."""
    path = _user_config_path()
    if not path:
        return {}
    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return {}
        return _normalize_user_config(data)
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

    context = {
        key: str(value)
        for key, value in user.items()
        if isinstance(value, (str, int, float, Path))
    }
    base = _expand_placeholders(base, context)
    return _resolve_country_paths(base)


def get_reference_code_path(country_id: str) -> Path | None:
    """
    Return the path to existing OpenFisca code for this country, if configured.
    """
    config = load_country_config(country_id)
    if not config:
        return None

    existing = config.get("existing_code") or {}
    raw = existing.get("path")
    if not raw or "${" in raw:
        return None

    p = Path(raw)
    return p if p.is_absolute() else (_project_root() / raw)


def get_legislative_sources_root(country_id: str) -> Path | None:
    """Return the path to legislative sources for this country, if configured."""
    config = load_country_config(country_id)
    if not config:
        return None

    sources = config.get("legislative_sources") or {}
    raw = sources.get("root")
    if not raw or "${" in raw:
        return None

    p = Path(raw)
    return p if p.is_absolute() else (_project_root() / raw)
