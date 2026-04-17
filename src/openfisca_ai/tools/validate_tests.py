#!/usr/bin/env python3
"""Validate OpenFisca test coverage at the package level."""

import ast
import re
import sys
from pathlib import Path


class TestValidator:
    """Validate that computed OpenFisca variables are covered by tests."""

    def __init__(self, package_path: Path):
        self.input_path = Path(package_path)
        self.repo_root = Path(package_path)
        self.country_package_dir: Path | None = None
        self.errors = []
        self.warnings = []
        self.info = []
        self.formula_variables: dict[str, str] = {}
        self.test_files: list[Path] = []

    def add_error(self, error_type: str, message: str, file_path: str):
        """Record a validation error."""
        self.errors.append(
            {
                "type": error_type,
                "severity": "ERROR",
                "message": message,
                "file": file_path,
            }
        )

    def add_warning(self, warning_type: str, message: str, file_path: str):
        """Record a validation warning."""
        self.warnings.append(
            {
                "type": warning_type,
                "severity": "WARNING",
                "message": message,
                "file": file_path,
            }
        )

    def is_country_package_dir(self, path: Path) -> bool:
        """Return True if the path looks like an OpenFisca country package module."""
        return (
            path.is_dir()
            and path.name.startswith("openfisca_")
            and (path / "__init__.py").exists()
        )

    def detect_layout(self):
        """Resolve whether the input path is a repo root or a package directory."""
        if self.is_country_package_dir(self.input_path):
            self.country_package_dir = self.input_path
            self.repo_root = self.input_path.parent
            self.info.append(
                f"✅ Input path looks like a country package directory: {self.country_package_dir.name}"
            )
            return

        self.repo_root = self.input_path
        candidates = [
            path
            for path in self.repo_root.iterdir()
            if self.is_country_package_dir(path)
        ]

        if not candidates:
            self.add_error(
                "missing_country_package",
                "Could not find a package directory named like openfisca_<country>",
                str(self.repo_root),
            )
            return

        if len(candidates) > 1:
            names = ", ".join(sorted(path.name for path in candidates))
            self.add_error(
                "ambiguous_country_package",
                f"Found multiple candidate package directories: {names}",
                str(self.repo_root),
            )
            return

        self.country_package_dir = candidates[0]
        self.info.append(f"✅ Country package detected: {self.country_package_dir.name}")

    def validate_all(self):
        """Run all validations."""
        print(f"🔍 Validating tests in {self.input_path}...\n")

        self.detect_layout()
        if self.country_package_dir is None:
            return self.get_report()

        self.collect_formula_variables()
        self.collect_test_files()
        self.check_coverage()

        return self.get_report()

    def collect_formula_variables(self):
        """Collect variable classes that define formula methods."""
        assert self.country_package_dir is not None
        variables_dir = self.country_package_dir / "variables"
        if not variables_dir.exists():
            self.add_error(
                "missing_variables_dir",
                "Missing variables/ directory in country package",
                str(self.country_package_dir / "variables"),
            )
            return

        for filepath in sorted(variables_dir.rglob("*.py")):
            if "__pycache__" in filepath.parts:
                continue
            self.collect_formula_variables_from_file(filepath)

        if self.formula_variables:
            self.info.append(
                f"✅ Formula variables found: {len(self.formula_variables)}"
            )
        else:
            self.add_warning(
                "no_formula_variables",
                "No Variable classes with formula methods found under variables/",
                str(variables_dir),
            )

    def collect_formula_variables_from_file(self, filepath: Path):
        """Collect formula variable classes from one Python file."""
        relative_path = str(filepath.relative_to(self.repo_root))
        try:
            tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
        except SyntaxError as exc:
            self.add_error(
                "syntax_error",
                f"Syntax error while scanning variable file: {exc.msg}",
                relative_path,
            )
            return

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not self.is_variable_class(node):
                continue
            if any(
                isinstance(statement, ast.FunctionDef) and statement.name.startswith("formula")
                for statement in node.body
            ):
                self.formula_variables[node.name] = relative_path

    def is_variable_class(self, node: ast.ClassDef) -> bool:
        """Return True when a class looks like an OpenFisca Variable."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Variable":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Variable":
                return True
        return False

    def collect_test_files(self):
        """Collect YAML and Python tests from the repository."""
        tests_dir = self.repo_root / "tests"
        if not tests_dir.exists():
            self.add_error(
                "missing_tests_dir",
                "Missing tests/ directory",
                str(tests_dir),
            )
            return

        yaml_tests = sorted(tests_dir.rglob("*.yaml"))
        py_tests = sorted(tests_dir.rglob("test_*.py"))
        self.test_files = yaml_tests + py_tests

        if yaml_tests:
            self.info.append(f"✅ YAML tests found: {len(yaml_tests)}")
        else:
            self.add_warning(
                "missing_yaml_tests",
                "No YAML tests found under tests/",
                str(tests_dir),
            )

        if py_tests:
            self.info.append(f"✅ Python tests found: {len(py_tests)}")
        else:
            self.add_warning(
                "missing_python_tests",
                "No Python tests found under tests/",
                str(tests_dir),
            )

        if not self.test_files:
            self.add_error(
                "empty_tests_dir",
                "tests/ exists but contains no YAML or Python test files",
                str(tests_dir),
            )

    def test_file_mentions_variable(self, filepath: Path, variable_name: str) -> bool:
        """Return True when a test file appears to exercise a variable."""
        if variable_name in filepath.stem:
            return True

        text = filepath.read_text(encoding="utf-8")
        pattern = re.compile(rf"\b{re.escape(variable_name)}\b")
        return bool(pattern.search(text))

    def check_coverage(self):
        """Check that each computed variable appears in at least one test file."""
        if not self.formula_variables or not self.test_files:
            return

        for variable_name, variable_file in sorted(self.formula_variables.items()):
            matching_tests = [
                test_file
                for test_file in self.test_files
                if self.test_file_mentions_variable(test_file, variable_name)
            ]

            if not matching_tests:
                self.add_error(
                    "untested_formula_variable",
                    f"Variable '{variable_name}' has a formula but no matching YAML or Python test was found",
                    variable_file,
                )

    def get_report(self):
        """Print report and return a structured result."""
        print("=" * 60)
        print("TEST VALIDATION REPORT")
        print("=" * 60)
        print()

        if self.info:
            print("📊 Status:\n")
            for item in self.info:
                print(f"   {item}")
            print()

        if not self.errors and not self.warnings:
            print("✅ ALL CHECKS PASSED!\n")
            return {"valid": True, "errors": [], "warnings": []}

        if self.errors:
            print(f"❌ {len(self.errors)} ERRORS:\n")
            for error in self.errors:
                print(f"  [{error['severity']}] {error['file']}")
                print(f"    {error['message']}")
                print()

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNINGS:\n")
            for warning in self.warnings:
                print(f"  [{warning['severity']}] {warning['file']}")
                print(f"    {warning['message']}")
                print()

        print("=" * 60)

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python validate_tests.py /path/to/openfisca-country-repo")
        print("\nExample:")
        print("  uv run python validate_tests.py /home/user/openfisca-tunisia")
        sys.exit(1)

    package_path = Path(sys.argv[1])
    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    validator = TestValidator(package_path)
    report = validator.validate_all()
    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
