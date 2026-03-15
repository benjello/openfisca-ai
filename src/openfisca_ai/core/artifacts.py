"""Helpers for planning and materializing generated artifacts to disk."""

from __future__ import annotations

from difflib import unified_diff
from pathlib import Path, PurePosixPath
from typing import Any


VALID_ARTIFACT_STRATEGIES = {"create", "skip", "append", "update"}


def _safe_relative_path(raw_path: str) -> Path:
    """Validate and normalize a generated relative artifact path."""
    posix_path = PurePosixPath(raw_path)
    if posix_path.is_absolute():
        raise ValueError(f"Artifact path must be relative: {raw_path}")
    if any(part in {"", ".", ".."} for part in posix_path.parts):
        raise ValueError(f"Artifact path contains unsafe segments: {raw_path}")
    return Path(*posix_path.parts)


def _normalize_strategy(strategy: str) -> str:
    """Validate a requested artifact conflict strategy."""
    normalized = (strategy or "create").strip().lower()
    if normalized not in VALID_ARTIFACT_STRATEGIES:
        supported = ", ".join(sorted(VALID_ARTIFACT_STRATEGIES))
        raise ValueError(f"Unsupported existing artifact strategy: {strategy}. Use one of: {supported}.")
    return normalized


def _join_appended_content(existing_content: str, new_content: str) -> str:
    """Append new content to an existing text file with a safe separator."""
    if not existing_content:
        return new_content
    if existing_content.endswith("\n"):
        separator = "" if new_content.startswith("\n") else "\n"
    else:
        separator = "\n\n" if new_content else "\n"
    return existing_content + separator + new_content


def _diff_preview(relative_path: str, before: str, after: str) -> str:
    """Build a unified diff preview for a text artifact."""
    diff_lines = unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=f"a/{relative_path}",
        tofile=f"b/{relative_path}",
        lineterm="",
    )
    return "\n".join(diff_lines)


def _build_artifact_plan(
    artifacts: list[dict[str, Any]],
    output_dir: str | Path,
    strategy: str,
    include_proposed_content: bool,
) -> list[dict[str, Any]]:
    """Build a write plan for generated artifacts."""
    root = Path(output_dir).resolve()
    strategy = _normalize_strategy(strategy)
    plan: list[dict[str, Any]] = []

    for artifact in artifacts:
        relative_path = _safe_relative_path(str(artifact["path"]))
        destination = root / relative_path
        exists = destination.exists()
        existing_content = destination.read_text(encoding="utf-8") if exists else ""
        new_content = str(artifact["content"])

        if not exists:
            action = "create"
            will_write = True
            proposed_content = new_content
            error = None
        elif strategy == "skip":
            action = "skip"
            will_write = False
            proposed_content = existing_content
            error = None
        elif strategy == "append":
            action = "append"
            will_write = True
            proposed_content = _join_appended_content(existing_content, new_content)
            error = None
        elif strategy == "update":
            action = "update"
            will_write = True
            proposed_content = new_content
            error = None
        else:
            action = "error"
            will_write = False
            proposed_content = existing_content
            error = f"Refusing to overwrite existing artifact: {destination}"

        plan_entry: dict[str, Any] = {
            "kind": str(artifact["kind"]),
            "path": str(relative_path),
            "written_path": str(destination),
            "exists": exists,
            "action": action,
            "will_write": will_write,
            "diff_preview": _diff_preview(str(relative_path), existing_content, proposed_content),
        }
        if error:
            plan_entry["error"] = error
        if include_proposed_content:
            plan_entry["proposed_content"] = proposed_content
        plan.append(plan_entry)

    return plan


def plan_artifact_writes(
    artifacts: list[dict[str, Any]],
    output_dir: str | Path,
    strategy: str = "create",
) -> list[dict[str, Any]]:
    """Plan artifact writes and return actions plus diff previews."""
    return _build_artifact_plan(
        artifacts,
        output_dir,
        strategy=strategy,
        include_proposed_content=False,
    )


def resolve_openfisca_repo_root(path: str | Path) -> Path:
    """Resolve a reference path to the containing OpenFisca repository root."""
    resolved = Path(path).resolve()
    if resolved.is_dir() and resolved.name.startswith("openfisca_") and (resolved / "__init__.py").exists():
        return resolved.parent
    return resolved


def materialize_artifacts(
    artifacts: list[dict[str, Any]],
    output_dir: str | Path,
    strategy: str = "create",
    overwrite: bool = False,
) -> list[dict[str, str]]:
    """Write generated artifacts to `output_dir` and return written file metadata."""
    normalized_strategy = "update" if overwrite else _normalize_strategy(strategy)
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)

    plan = _build_artifact_plan(
        artifacts,
        root,
        strategy=normalized_strategy,
        include_proposed_content=True,
    )
    written_artifacts: list[dict[str, str]] = []
    for entry in plan:
        if entry["action"] == "error":
            raise FileExistsError(str(entry["error"]))
        if not entry["will_write"]:
            continue

        destination = Path(entry["written_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(str(entry["proposed_content"]), encoding="utf-8")
        written_artifacts.append(
            {
                "kind": str(entry["kind"]),
                "path": str(entry["path"]),
                "written_path": str(destination),
                "action": str(entry["action"]),
            }
        )

    return written_artifacts
