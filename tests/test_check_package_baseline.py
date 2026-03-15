"""Tests for check_package_baseline.py."""

from tests.tool_test_helpers import create_country_repo, load_tool_module, write_file


check_package_baseline = load_tool_module(
    "check_package_baseline.py",
    "check_package_baseline_tool",
)


def test_check_package_baseline_passes_for_modern_country_repo(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "pyproject.toml",
        """
        [project]
        name = "OpenFisca-Demo"
        dependencies = ["openfisca-core[web-api]>=44,<45"]
        """,
    )
    write_file(repo_path / "uv.lock", "version = 1\n")
    write_file(repo_path / "openfisca_demo/reforms/__init__.py", "")
    write_file(repo_path / "openfisca_demo/situation_examples/example.json", "{}\n")
    write_file(
        repo_path / "Makefile",
        """
        UV = uv run

        install:
        	uv sync --extra dev

        build:
        	uv build

        check-syntax-errors:
        	$(UV) python -m compileall -q .

        check-style:
        	$(UV) ruff check .

        test:
        	$(UV) openfisca test --country-package openfisca_demo tests
        """,
    )
    write_file(
        repo_path / ".github/workflows/ci.yml",
        """
        name: CI

        on: [push, pull_request]

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - run: uv sync --extra dev
              - run: uv run openfisca test --country-package openfisca_demo tests
              - run: uv run yamllint openfisca_demo/parameters tests
        """,
    )

    checker = check_package_baseline.PackageBaselineChecker(repo_path)

    assert checker.check_all() is True
    assert checker.issues == []
    assert checker.warnings == []


def test_check_package_baseline_fails_when_core_structure_is_missing(tmp_path):
    repo_path = tmp_path / "openfisca-broken"
    repo_path.mkdir()

    checker = check_package_baseline.PackageBaselineChecker(repo_path)

    assert checker.check_all() is False
    assert any(issue["type"] == "missing_pyproject" for issue in checker.issues)
    assert any(issue["type"] == "missing_country_package" for issue in checker.issues)
    assert any(issue["type"] == "missing_tests_dir" for issue in checker.issues)


def test_check_package_baseline_warns_for_older_but_usable_setup(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "pyproject.toml",
        """
        [project]
        name = "OpenFisca-Demo"
        dependencies = ["openfisca-core[web-api]>=44,<45"]
        """,
    )
    write_file(repo_path / "tests/test_smoke.py", "def test_smoke():\n    assert True\n")
    (repo_path / "tests" / "demo.yaml").unlink()

    checker = check_package_baseline.PackageBaselineChecker(repo_path)

    assert checker.check_all() is True
    assert checker.issues == []
    warning_types = {warning["type"] for warning in checker.warnings}
    assert "missing_uv_lock" in warning_types
    assert "missing_makefile" in warning_types
    assert "missing_ci_workflows" in warning_types
    assert "missing_yaml_tests" in warning_types
