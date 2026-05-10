"""Tests for CI profile detection."""

from openfisca_ai.ci.detect import detect_ci_profile
from tests.tool_test_helpers import create_country_repo, write_file


def test_ci_detect_openfisca_package_uv(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(repo_path / "pyproject.toml", "[project]\nname = 'openfisca-demo'\ndependencies = ['openfisca-ai']\n")
    write_file(repo_path / "uv.lock", "version = 1\n")
    write_file(repo_path / ".github/workflows/ci.yml", "name: CI\n")

    report = detect_ci_profile(repo_path)

    assert report["repo_type"] == "openfisca-package"
    assert report["package_name"] == "openfisca_demo"
    assert report["environment_manager"] == "uv"
    assert report["has_github_actions"] is True
    assert report["has_yaml_tests"] is True
    assert report["recommended_profiles"] == [
        "openfisca-package",
        "openfisca-ai-tools",
        "ai-review",
    ]
    assert report["warnings"] == []


def test_ci_detect_openfisca_large(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(repo_path / "pyproject.toml", "[project]\nname = 'openfisca-demo'\n")
    for index in range(101):
        write_file(repo_path / f"tests/generated/test_{index}.yaml", "- name: demo\n  output: {}\n")

    report = detect_ci_profile(repo_path)

    assert report["repo_type"] == "openfisca-large"
    assert report["yaml_test_count"] == 102
    assert report["recommended_profiles"] == ["openfisca-large", "openfisca-ai-tools"]


def test_ci_detect_python_package(tmp_path):
    repo_path = tmp_path / "python-package"
    repo_path.mkdir()
    write_file(repo_path / "pyproject.toml", "[project]\nname = 'python-package'\n")
    write_file(repo_path / "tests/test_demo.py", "def test_demo():\n    assert True\n")

    report = detect_ci_profile(repo_path)

    assert report["repo_type"] == "python-package"
    assert report["package_name"] is None
    assert report["environment_manager"] == "pyproject"
    assert report["recommended_profiles"] == ["python-package"]


def test_ci_detect_openfisca_core(tmp_path):
    repo_path = tmp_path / "openfisca-core"
    write_file(repo_path / "openfisca_core/__init__.py", "")
    write_file(repo_path / "setup.py", "setup(name='OpenFisca-Core')\n")

    report = detect_ci_profile(repo_path)

    assert report["repo_type"] == "openfisca-core"
    assert report["environment_manager"] == "setuptools"
    assert report["recommended_profiles"] == ["openfisca-core"]
