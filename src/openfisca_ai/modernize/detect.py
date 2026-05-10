"""Detect modernization state without modifying the repository."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openfisca_ai.ci.detect import detect_ci_profile


def _file_contains(path: Path, needles: tuple[str, ...]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    return any(needle in text for needle in needles)


def _detect_formatter(repo_path: Path) -> str:
    pyproject = repo_path / "pyproject.toml"
    setup_cfg = repo_path / "setup.cfg"
    makefile = repo_path / "Makefile"
    if _file_contains(pyproject, ("[tool.ruff]", "[tool.ruff.", "ruff")) or _file_contains(makefile, ("ruff check", "ruff format")):
        return "ruff"
    if _file_contains(pyproject, ("[tool.black]",)) or _file_contains(setup_cfg, ("[flake8]",)) or _file_contains(makefile, ("flake8", "black")):
        return "legacy"
    return "unknown"


def _detect_packaging(repo_path: Path) -> str:
    pyproject = repo_path / "pyproject.toml"
    setup_py = repo_path / "setup.py"
    setup_cfg = repo_path / "setup.cfg"
    if pyproject.exists() and _file_contains(pyproject, ("[project]",)):
        return "pyproject-project"
    if pyproject.exists():
        return "pyproject-tools-only"
    if setup_py.exists() or setup_cfg.exists():
        return "setuptools-legacy"
    return "unknown"


def detect_modernization_state(path: str | Path) -> dict[str, Any]:
    """Return modernization-relevant facts about a repository."""
    ci = detect_ci_profile(path)
    repo_path = Path(ci["repo_path"])
    pyproject = repo_path / "pyproject.toml"
    makefile = repo_path / "Makefile"
    github_workflows = repo_path / ".github" / "workflows"

    state: dict[str, Any] = {
        "schema_version": 1,
        "repo_path": ci["repo_path"],
        "repo_type": ci["repo_type"],
        "package_name": ci["package_name"],
        "ci": ci,
        "packaging": _detect_packaging(repo_path),
        "environment_manager": ci["environment_manager"],
        "formatter": _detect_formatter(repo_path),
        "has_pyproject": pyproject.exists(),
        "has_uv_lock": (repo_path / "uv.lock").exists(),
        "has_makefile": makefile.exists(),
        "has_yamllint": (repo_path / ".yamllint").exists(),
        "has_github_actions": github_workflows.is_dir(),
        "has_gitlab_ci": (repo_path / ".gitlab-ci.yml").exists(),
        "has_openfisca_ai_dependency": ci["has_openfisca_ai"],
    }
    return state
