"""Tests for OpenFisca package layout resolution."""

from openfisca_ai.domain.package_layout import PackageLayout
from tests.tool_test_helpers import create_country_repo, write_file


def test_package_layout_resolves_repo_root(tmp_path):
    repo_path = create_country_repo(tmp_path, module_name="openfisca_demo")

    layout = PackageLayout.from_path(repo_path)

    assert layout.is_valid
    assert layout.repo_root == repo_path
    assert layout.package_dir == repo_path / "openfisca_demo"
    assert layout.package_name == "openfisca_demo"
    assert layout.variables_dir == repo_path / "openfisca_demo/variables"
    assert layout.parameters_dir == repo_path / "openfisca_demo/parameters"
    assert layout.tests_dir == repo_path / "tests"


def test_package_layout_resolves_package_dir(tmp_path):
    repo_path = create_country_repo(tmp_path, module_name="openfisca_demo")

    layout = PackageLayout.from_path(repo_path / "openfisca_demo")

    assert layout.is_valid
    assert layout.repo_root == repo_path
    assert layout.package_dir == repo_path / "openfisca_demo"


def test_package_layout_reports_missing_package(tmp_path):
    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()

    layout = PackageLayout.from_path(empty_repo)

    assert not layout.is_valid
    assert layout.package_dir is None
    assert layout.errors == (
        "Could not find a package directory named like openfisca_<country>",
    )


def test_package_layout_reports_ambiguous_package(tmp_path):
    repo_path = tmp_path / "repo"
    write_file(repo_path / "openfisca_one/__init__.py", "")
    write_file(repo_path / "openfisca_two/__init__.py", "")

    layout = PackageLayout.from_path(repo_path)

    assert not layout.is_valid
    assert layout.package_dir is None
    assert layout.errors == (
        "Found multiple candidate package directories: openfisca_one, openfisca_two",
    )
