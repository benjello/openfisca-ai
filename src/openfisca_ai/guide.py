"""Discovery and resolution of methodology guides packaged with openfisca-ai.

Guides are markdown files distributed under ``openfisca_ai/resources/agents/``.
They can be listed, located, and read from the installed package — so consumer
projects do not need to clone openfisca-ai to access them.

A consumer project may overlay a generic guide by placing a file with the same
relative path under ``docs/openfisca-ai/agents/`` in its working directory.
When an overlay exists, :func:`read_guide` returns the generic content followed
by a ``## Spécificités projet`` section containing the overlay.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

RESOURCES_PACKAGE = "openfisca_ai"
RESOURCES_SUBPATH = ("resources", "agents")
OVERLAY_SUBPATH = Path("docs") / "openfisca-ai" / "agents"
OVERLAY_SEPARATOR = "\n\n---\n\n## Spécificités projet\n\n"


@dataclass(frozen=True)
class Guide:
    """A methodology guide shipped with openfisca-ai."""

    name: str
    """Short name (file stem), e.g. ``test-creator``."""

    relative_path: str
    """Path relative to the resources/agents/ root, e.g. ``02-framework/roles/test-creator.md``."""


def _resources_root() -> Traversable:
    root = files(RESOURCES_PACKAGE)
    for part in RESOURCES_SUBPATH:
        root = root / part
    return root


def _iter_markdown(root: Traversable, prefix: str = "") -> list[tuple[str, Traversable]]:
    """Recursively yield (relative_path, traversable) for every .md file under root."""
    found: list[tuple[str, Traversable]] = []
    for entry in root.iterdir():
        rel = f"{prefix}{entry.name}"
        if entry.is_dir():
            found.extend(_iter_markdown(entry, prefix=f"{rel}/"))
        elif entry.name.endswith(".md"):
            found.append((rel, entry))
    return found


def list_guides() -> list[Guide]:
    """Return all guides packaged with openfisca-ai, sorted by relative path."""
    root = _resources_root()
    items = _iter_markdown(root)
    guides = [
        Guide(name=Path(rel).stem, relative_path=rel)
        for rel, _ in items
    ]
    return sorted(guides, key=lambda g: g.relative_path)


def _normalize_query(name: str) -> str:
    """Strip a trailing .md so callers can use either form."""
    return name[:-3] if name.endswith(".md") else name


def resolve_guide(name: str) -> Guide:
    """Resolve a guide by short name or relative path.

    Accepts:
        - short name: ``test-creator``
        - relative path: ``02-framework/roles/test-creator``
        - relative path with extension: ``02-framework/roles/test-creator.md``

    Raises ``LookupError`` if no guide matches, or if a short name is ambiguous.
    """
    query = _normalize_query(name)
    guides = list_guides()

    # Exact relative path match (with implicit .md).
    for guide in guides:
        if guide.relative_path == f"{query}.md" or guide.relative_path == query:
            return guide

    # Short name match (file stem).
    matches = [g for g in guides if g.name == query]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        paths = ", ".join(g.relative_path for g in matches)
        raise LookupError(
            f"Guide name '{name}' is ambiguous. Use one of the following paths: {paths}"
        )

    raise LookupError(f"Unknown guide: {name!r}. Run `openfisca-ai guide list` to see available guides.")


def guide_resource_path(guide: Guide) -> Path:
    """Return the absolute on-disk path of the packaged guide.

    Falls back to ``Path(str(...))`` resolution which works for regular file
    installs (the common case for editable / wheel installs of openfisca-ai).
    """
    root = _resources_root()
    traversable = root
    for part in guide.relative_path.split("/"):
        traversable = traversable / part
    return Path(str(traversable))


def overlay_path(guide: Guide, project_root: Path | None = None) -> Path:
    """Return the path where a project may place an overlay for ``guide``."""
    base = (project_root or Path.cwd()) / OVERLAY_SUBPATH
    return base / guide.relative_path


def read_guide(name: str, project_root: Path | None = None) -> str:
    """Read a guide, applying a project overlay when present.

    The packaged content always comes first; if an overlay exists at
    ``<project_root>/docs/openfisca-ai/agents/<relative_path>``, its content is
    appended after a ``## Spécificités projet`` separator.
    """
    guide = resolve_guide(name)
    base_path = guide_resource_path(guide)
    base_text = base_path.read_text(encoding="utf-8")

    overlay = overlay_path(guide, project_root=project_root)
    if overlay.is_file():
        overlay_text = overlay.read_text(encoding="utf-8")
        return base_text.rstrip() + OVERLAY_SEPARATOR + overlay_text.lstrip()

    return base_text


def resources_root_path() -> Path:
    """Absolute path to the packaged resources/agents/ directory."""
    return Path(str(_resources_root()))
