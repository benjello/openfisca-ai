"""Resolve local agent targets from OpenFisca AI country configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openfisca_ai.config_loader import (
    _expand_placeholders,
    _load_user_config,
    get_countries_dir,
    load_country_config,
)

VALID_REPO_MODES = {"rw", "ro", "worktree"}


class AgentTargetError(RuntimeError):
    """Raised when an agent target cannot be resolved."""


def _country_ids() -> list[str]:
    ids = set()
    countries_dir = get_countries_dir()
    if countries_dir.exists():
        ids.update(
            path.stem
            for path in countries_dir.glob("*.yaml")
            if not path.name.startswith("_")
        )

    user = _load_user_config()
    countries = user.get("countries")
    if isinstance(countries, dict):
        ids.update(str(country_id) for country_id in countries)

    return sorted(ids)


def _user_context() -> dict[str, str]:
    user = _load_user_config()
    return {
        key: str(value)
        for key, value in user.items()
        if isinstance(value, (str, int, float, Path))
    }


def _as_absolute_path(raw: str | None, base: Path | None = None) -> str | None:
    if not raw:
        return None
    path = Path(raw).expanduser()
    if path.is_absolute():
        return str(path)
    if base is not None:
        return str((base / path).resolve())
    return str(path.resolve())


def _repo_name_from_path(path: str | None, fallback: str) -> str:
    if path:
        return Path(path).name
    return fallback


def _normalize_repo_entry(
    name: str,
    raw: Any,
    base_path: Path | None,
) -> dict[str, Any]:
    if isinstance(raw, str):
        if raw in VALID_REPO_MODES:
            mode = raw
            path = name
        else:
            path, _, mode_value = raw.partition(":")
            mode = mode_value or "rw"
    elif isinstance(raw, dict):
        path = raw.get("path") or name
        mode = raw.get("mode", "rw")
    else:
        raise AgentTargetError(f"Invalid repository config for {name!r}")

    if mode not in VALID_REPO_MODES:
        raise AgentTargetError(
            f"Invalid mode {mode!r} for repository {name!r}; "
            f"expected one of: {', '.join(sorted(VALID_REPO_MODES))}"
        )

    return {
        "name": name,
        "path": _as_absolute_path(str(path), base_path),
        "mode": mode,
    }


def _normalize_repos(
    raw_repos: Any,
    main_repo_name: str,
    main_repo_path: str | None,
    base_path: Path | None,
) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []

    if raw_repos is None:
        raw_repos = {
            main_repo_name: {
                "path": main_repo_path,
                "mode": "rw",
            }
        }

    if isinstance(raw_repos, dict):
        for name, raw in raw_repos.items():
            repos.append(_normalize_repo_entry(str(name), raw, base_path))
    elif isinstance(raw_repos, list):
        for item in raw_repos:
            if isinstance(item, str):
                name, _, mode = item.partition(":")
                repos.append(
                    _normalize_repo_entry(
                        name,
                        {"path": name, "mode": mode or "rw"},
                        base_path,
                    )
                )
            elif isinstance(item, dict):
                name = item.get("name")
                if not name:
                    raise AgentTargetError("Repository list entries must define a name")
                repos.append(_normalize_repo_entry(str(name), item, base_path))
            else:
                raise AgentTargetError("Repository entries must be strings or mappings")
    else:
        raise AgentTargetError("agent.repos must be a mapping or a list")

    if not any(repo["name"] == main_repo_name for repo in repos):
        repos.insert(
            0,
            {
                "name": main_repo_name,
                "path": _as_absolute_path(main_repo_path, base_path),
                "mode": "rw",
            },
        )

    for repo in repos:
        repo["is_main"] = repo["name"] == main_repo_name

    return repos


def _country_config_from_user_only(country_id: str) -> dict[str, Any] | None:
    user = _load_user_config()
    countries = user.get("countries")
    if not isinstance(countries, dict):
        return None
    raw = countries.get(country_id)
    if not isinstance(raw, dict):
        return None
    context = _user_context()
    config = _expand_placeholders(dict(raw), context)
    config.setdefault("id", country_id)
    config.setdefault("label", country_id)
    return config


def build_agent_target(country_id: str) -> dict[str, Any] | None:
    """Build the normalized agent target for a country id."""
    config = load_country_config(country_id) or _country_config_from_user_only(country_id)
    if not config:
        return None

    user = _load_user_config()
    agent = config.get("agent") or {}
    if not isinstance(agent, dict):
        raise AgentTargetError(f"countries.{country_id}.agent must be a mapping")

    context = _user_context()
    existing_code = config.get("existing_code") or {}
    main_repo_path = existing_code.get("path") if isinstance(existing_code, dict) else None
    main_repo_name = agent.get("main_repo") or _repo_name_from_path(main_repo_path, country_id)

    raw_base = agent.get("base") or user.get("base_path")
    raw_base = _expand_placeholders(raw_base, context)
    base_path = Path(str(raw_base)).expanduser() if raw_base else None

    repos = _normalize_repos(
        agent.get("repos"),
        str(main_repo_name),
        main_repo_path,
        base_path,
    )
    main_repo = next(repo for repo in repos if repo["is_main"])

    raw_aliases = agent.get("aliases") or []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    aliases = sorted(
        {
            str(country_id),
            str(main_repo_name),
            *[str(alias) for alias in raw_aliases],
        }
    )

    raw_worktree_base = agent.get("worktree_base") or user.get("agent_worktree_base")
    raw_worktree_base = _expand_placeholders(raw_worktree_base, context)
    if raw_worktree_base:
        worktree_base = _as_absolute_path(str(raw_worktree_base), base_path)
    elif base_path:
        worktree_base = str((base_path / ".agent-worktrees").resolve())
    elif main_repo.get("path"):
        worktree_base = str((Path(main_repo["path"]).parent / ".agent-worktrees").resolve())
    else:
        worktree_base = None

    return {
        "id": str(country_id),
        "label": config.get("label", country_id),
        "aliases": aliases,
        "country": str(country_id),
        "main_repo": main_repo,
        "repos": repos,
        "worktree_base": worktree_base,
    }


def list_agent_targets() -> list[dict[str, Any]]:
    """List all configured agent targets."""
    targets = []
    for country_id in _country_ids():
        target = build_agent_target(country_id)
        if target:
            targets.append(target)
    return sorted(targets, key=lambda target: target["id"])


def resolve_agent_target(name: str) -> dict[str, Any]:
    """Resolve a country id, alias, or main repository name to an agent target."""
    matches = [
        target
        for target in list_agent_targets()
        if name == target["id"] or name in target["aliases"]
    ]

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        ids = ", ".join(target["id"] for target in matches)
        raise AgentTargetError(f"Ambiguous agent target {name!r}: {ids}")

    raise AgentTargetError(f"Unknown agent target: {name!r}")
