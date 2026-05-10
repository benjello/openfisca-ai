"""Detect CI-relevant repository characteristics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openfisca_ai.domain.package_layout import PackageLayout


LARGE_YAML_TEST_THRESHOLD = 100


def _has_file(path: Path, names: tuple[str, ...]) -> bool:
    return any((path / name).exists() for name in names)


def _count_yaml_tests(tests_dir: Path) -> int:
    if not tests_dir.exists():
        return 0
    return len(list(tests_dir.rglob("*.yaml"))) + len(list(tests_dir.rglob("*.yml")))


def _count_python_tests(tests_dir: Path) -> int:
    if not tests_dir.exists():
        return 0
    return len([
        path
        for path in tests_dir.rglob("test_*.py")
        if path.name not in {"__init__.py", "conftest.py"}
    ])


def _detect_environment_manager(repo_path: Path) -> str:
    if (repo_path / "uv.lock").exists():
        return "uv"
    if (repo_path / "pyproject.toml").exists():
        return "pyproject"
    if (repo_path / "setup.py").exists():
        return "setuptools"
    if _has_file(repo_path, ("requirements.txt", "requirements-dev.txt")):
        return "pip"
    return "unknown"


def _detect_repo_type(repo_path: Path, layout: PackageLayout, yaml_test_count: int) -> str:
    if repo_path.name == "openfisca-core" or (repo_path / "openfisca_core").is_dir():
        return "openfisca-core"
    if repo_path.name == "openfisca-survey-manager" or (repo_path / "openfisca_survey_manager").is_dir():
        return "python-package"
    if layout.package_dir and layout.package_name and layout.package_name.startswith("openfisca_"):
        if yaml_test_count >= LARGE_YAML_TEST_THRESHOLD:
            return "openfisca-large"
        return "openfisca-package"
    if (repo_path / "pyproject.toml").exists() or (repo_path / "setup.py").exists():
        return "python-package"
    return "unknown"


def _recommended_profiles(repo_type: str, has_openfisca_ai: bool) -> list[str]:
    profiles: list[str] = []
    if repo_type in {"openfisca-package", "openfisca-large"}:
        profiles.append(repo_type)
        profiles.append("openfisca-ai-tools")
    elif repo_type == "python-package":
        profiles.append("python-package")
    elif repo_type == "openfisca-core":
        profiles.append("openfisca-core")

    if has_openfisca_ai and repo_type in {"openfisca-package", "openfisca-large"}:
        profiles.append("ai-review")
    return profiles


def _warnings(report: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if report["repo_type"] == "unknown":
        warnings.append("Repository type could not be detected")
    if report["repo_type"] in {"openfisca-package", "openfisca-large"}:
        if not report["has_units"]:
            warnings.append("OpenFisca package has no units.yaml")
        if not report["has_parameters"]:
            warnings.append("OpenFisca package has no parameters directory")
        if not report["has_yaml_tests"] and not report["has_python_tests"]:
            warnings.append("No tests were detected")
    if report["environment_manager"] == "unknown":
        warnings.append("No Python environment manager was detected")
    return warnings


def detect_ci_profile(path: str | Path) -> dict[str, Any]:
    """Detect CI characteristics and recommended profiles for a repository."""
    repo_path = Path(path).resolve()
    layout = PackageLayout.from_path(repo_path)
    if layout.package_dir is not None:
        repo_path = layout.repo_root.resolve()

    tests_dir = repo_path / "tests"
    yaml_test_count = _count_yaml_tests(tests_dir)
    python_test_count = _count_python_tests(tests_dir)
    package_dir = layout.package_dir
    parameters_dir = layout.parameters_dir
    units_file = layout.units_file

    environment_manager = _detect_environment_manager(repo_path)
    has_openfisca_ai = False
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        has_openfisca_ai = "openfisca-ai" in pyproject.read_text(encoding="utf-8")

    repo_type = _detect_repo_type(repo_path, layout, yaml_test_count)
    report: dict[str, Any] = {
        "schema_version": 1,
        "repo_path": str(repo_path),
        "repo_type": repo_type,
        "package_name": layout.package_name,
        "package_dir": str(package_dir) if package_dir else None,
        "environment_manager": environment_manager,
        "has_makefile": (repo_path / "Makefile").exists(),
        "has_github_actions": (repo_path / ".github" / "workflows").is_dir(),
        "has_gitlab_ci": (repo_path / ".gitlab-ci.yml").exists(),
        "has_yaml_tests": yaml_test_count > 0,
        "has_python_tests": python_test_count > 0,
        "yaml_test_count": yaml_test_count,
        "python_test_count": python_test_count,
        "has_parameters": bool(parameters_dir and parameters_dir.is_dir()),
        "has_units": bool(units_file and units_file.exists()),
        "has_openfisca_ai": has_openfisca_ai,
        "recommended_profiles": [],
        "warnings": [],
    }
    report["recommended_profiles"] = _recommended_profiles(repo_type, has_openfisca_ai)
    report["warnings"] = _warnings(report)
    return report
