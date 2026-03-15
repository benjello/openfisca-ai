"""Tests for check_tooling.py."""

from tests.tool_test_helpers import create_package, load_tool_module, write_file


check_tooling = load_tool_module("check_tooling.py", "check_tooling_tool")


def test_check_tooling_passes_with_uv_ruff_and_tests(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "Makefile",
        """
        UV = uv run

        install:
        	$(UV) pip install -e .

        test:
        	$(UV) pytest

        check-style:
        	$(UV) ruff check .

        format-style:
        	$(UV) ruff format .
        """,
    )
    write_file(package_path / "pyproject.toml", "[tool.ruff]\nline-length = 100\n")
    write_file(package_path / ".yamllint", "extends: default\n")
    write_file(package_path / "tests/test_demo.py", "def test_demo():\n    assert True\n")

    checker = check_tooling.ToolingChecker(package_path)

    assert checker.check_all() is True
    assert checker.issues == []


def test_check_tooling_warns_but_does_not_fail_for_black_only_stack(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "Makefile",
        """
        test:
        	pytest
        """,
    )
    write_file(package_path / "pyproject.toml", "[tool.black]\nline-length = 88\n")
    write_file(package_path / "tests/test_demo.py", "def test_demo():\n    assert True\n")

    checker = check_tooling.ToolingChecker(package_path)

    assert checker.check_all() is True
    assert checker.issues == []
    assert any(warning["type"] == "legacy_formatter" for warning in checker.warnings)


def test_check_tooling_fails_when_tests_directory_is_missing(tmp_path):
    package_path = create_package(tmp_path)
    write_file(package_path / "pyproject.toml", "[tool.ruff]\nline-length = 100\n")

    checker = check_tooling.ToolingChecker(package_path)

    assert checker.check_all() is False
    assert any(issue["type"] == "no_tests" for issue in checker.issues)
