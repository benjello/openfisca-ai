"""Resolve the filesystem layout of an OpenFisca country package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PackageLayout:
    """Filesystem paths for an OpenFisca country repository.

    A caller may pass either the repository root or the Python package directory
    named like `openfisca_<country>`. The resolver keeps track of errors instead
    of raising so validators can decide how to report them.
    """

    input_path: Path
    repo_root: Path
    package_dir: Path | None
    errors: tuple[str, ...] = ()

    @classmethod
    def from_path(cls, path: str | Path) -> "PackageLayout":
        """Resolve a package layout from a repository or package path."""
        input_path = Path(path)
        if cls.is_country_package_dir(input_path):
            return cls(
                input_path=input_path,
                repo_root=input_path.parent,
                package_dir=input_path,
            )

        if not input_path.exists():
            return cls(
                input_path=input_path,
                repo_root=input_path,
                package_dir=None,
                errors=(f"Path does not exist: {input_path}",),
            )

        if not input_path.is_dir():
            return cls(
                input_path=input_path,
                repo_root=input_path.parent,
                package_dir=None,
                errors=(f"Path is not a directory: {input_path}",),
            )

        candidates = [
            child
            for child in sorted(input_path.iterdir())
            if cls.is_country_package_dir(child)
        ]
        if len(candidates) == 1:
            return cls(
                input_path=input_path,
                repo_root=input_path,
                package_dir=candidates[0],
            )
        if not candidates:
            return cls(
                input_path=input_path,
                repo_root=input_path,
                package_dir=None,
                errors=(
                    "Could not find a package directory named like openfisca_<country>",
                ),
            )

        names = ", ".join(candidate.name for candidate in candidates)
        return cls(
            input_path=input_path,
            repo_root=input_path,
            package_dir=None,
            errors=(f"Found multiple candidate package directories: {names}",),
        )

    @staticmethod
    def is_country_package_dir(path: Path) -> bool:
        """Return True when a directory looks like an OpenFisca country package."""
        return (
            path.is_dir()
            and path.name.startswith("openfisca_")
            and (path / "__init__.py").exists()
        )

    @property
    def is_valid(self) -> bool:
        """Whether a single OpenFisca package directory was resolved."""
        return self.package_dir is not None and not self.errors

    @property
    def package_name(self) -> str | None:
        """Python package name, for example `openfisca_france`."""
        return self.package_dir.name if self.package_dir else None

    @property
    def variables_dir(self) -> Path | None:
        """Variables directory when a package is resolved."""
        return self.package_dir / "variables" if self.package_dir else None

    @property
    def parameters_dir(self) -> Path | None:
        """Parameters directory when a package is resolved."""
        return self.package_dir / "parameters" if self.package_dir else None

    @property
    def tests_dir(self) -> Path:
        """Repository-level tests directory."""
        return self.repo_root / "tests"

    @property
    def entities_file(self) -> Path | None:
        """Path to entities.py when a package is resolved."""
        return self.package_dir / "entities.py" if self.package_dir else None

    @property
    def units_file(self) -> Path | None:
        """Path to units.yaml when a package is resolved."""
        return self.package_dir / "units.yaml" if self.package_dir else None
