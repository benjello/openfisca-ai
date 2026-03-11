#!/usr/bin/env python3
"""
Check Development Tooling - Verify modern tools are used

Checks:
1. Uses ruff (not Black/flake8)
2. Has proper Makefile with uv
3. Has test suite
4. Uses yamllint for parameters

Usage: python check_tooling.py /path/to/openfisca-country
"""

import sys
from pathlib import Path
import re


class ToolingChecker:
    """Check development tooling setup"""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path)
        self.issues = []
        self.warnings = []
        self.info = []

    def check_all(self):
        """Run all checks"""
        print(f"🔍 Checking tooling in {self.package_path}...\n")

        self.check_makefile()
        self.check_formatter()
        self.check_tests()
        self.check_yaml_validation()

        return self.report()

    def check_makefile(self):
        """Check Makefile uses uv"""
        makefile = self.package_path / "Makefile"

        if not makefile.exists():
            self.warnings.append({
                "type": "missing_makefile",
                "message": "No Makefile found - consider adding one for consistency",
                "fix": "Create Makefile with 'make install', 'make test', etc."
            })
            return

        content = makefile.read_text()

        # Check for uv
        if 'uv run' in content or 'UV = uv' in content:
            self.info.append("✅ Uses uv for environment management")
        else:
            self.issues.append({
                "type": "no_uv",
                "message": "Makefile doesn't use 'uv' - should use UV = uv run",
                "fix": "Add 'UV = uv run' at top of Makefile"
            })

        # Check for standard targets
        targets = ['install', 'test', 'check-style', 'format-style']
        missing = [t for t in targets if f'{t}:' not in content]

        if missing:
            self.warnings.append({
                "type": "missing_targets",
                "message": f"Makefile missing targets: {', '.join(missing)}",
                "fix": f"Add targets: {', '.join(missing)}"
            })

    def check_formatter(self):
        """Check if using ruff (modern) vs Black (legacy)"""
        makefile = self.package_path / "Makefile"
        pyproject = self.package_path / "pyproject.toml"

        uses_ruff = False
        uses_black = False
        uses_flake8 = False

        # Check Makefile
        if makefile.exists():
            content = makefile.read_text()
            if 'ruff format' in content or 'ruff check' in content:
                uses_ruff = True
            if 'black' in content.lower():
                uses_black = True
            if 'flake8' in content.lower():
                uses_flake8 = True

        # Check pyproject.toml
        if pyproject.exists():
            content = pyproject.read_text()
            if '[tool.ruff]' in content:
                uses_ruff = True
            if '[tool.black]' in content:
                uses_black = True

        if uses_ruff:
            self.info.append("✅ Uses ruff for formatting/linting (modern)")
        elif uses_black or uses_flake8:
            tools = []
            if uses_black:
                tools.append("Black")
            if uses_flake8:
                tools.append("flake8")

            self.issues.append({
                "type": "legacy_formatter",
                "message": f"Uses legacy tools: {', '.join(tools)}",
                "fix": "Migrate to ruff (all-in-one formatter + linter)",
                "priority": "HIGH"
            })
        else:
            self.warnings.append({
                "type": "no_formatter",
                "message": "No formatter/linter detected",
                "fix": "Add ruff to pyproject.toml and Makefile"
            })

    def check_tests(self):
        """Check test suite exists"""
        tests_dir = self.package_path / "tests"

        if not tests_dir.exists():
            self.issues.append({
                "type": "no_tests",
                "message": "No tests/ directory found",
                "fix": "Create tests/ directory with test files",
                "priority": "HIGH"
            })
            return

        # Count test files
        yaml_tests = list(tests_dir.rglob("*.yaml"))
        py_tests = list(tests_dir.rglob("test_*.py"))

        if not yaml_tests and not py_tests:
            self.warnings.append({
                "type": "empty_tests",
                "message": "tests/ directory exists but contains no test files",
                "fix": "Add YAML or Python test files"
            })
        else:
            self.info.append(f"✅ Has tests: {len(yaml_tests)} YAML, {len(py_tests)} Python")

    def check_yaml_validation(self):
        """Check if yamllint is configured"""
        yamllint_config = self.package_path / ".yamllint"
        makefile = self.package_path / "Makefile"

        has_yamllint = False

        if yamllint_config.exists():
            has_yamllint = True
            self.info.append("✅ Has .yamllint configuration")

        if makefile.exists():
            content = makefile.read_text()
            if 'yamllint' in content:
                has_yamllint = True

        if not has_yamllint:
            self.warnings.append({
                "type": "no_yamllint",
                "message": "No yamllint configuration found",
                "fix": "Add .yamllint config and 'make check-yaml' target"
            })

    def report(self):
        """Generate report"""
        print("=" * 70)
        print("TOOLING CHECK REPORT")
        print("=" * 70)
        print()

        # Info
        if self.info:
            print("📊 Status:\n")
            for item in self.info:
                print(f"   {item}")
            print()

        # Issues (critical)
        if self.issues:
            print(f"❌ {len(self.issues)} CRITICAL ISSUES:\n")
            for issue in self.issues:
                print(f"   [{issue.get('priority', 'MEDIUM')}] {issue['message']}")
                print(f"   💡 Fix: {issue['fix']}")
                print()

        # Warnings
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNINGS:\n")
            for warning in self.warnings:
                print(f"   {warning['message']}")
                print(f"   💡 Fix: {warning['fix']}")
                print()

        # Summary
        if not self.issues and not self.warnings:
            print("✅ ALL CHECKS PASSED!\n")
            print("Package uses modern development tooling:")
            print("  - uv for environment management")
            print("  - ruff for formatting/linting")
            print("  - yamllint for YAML validation")
            print("  - Complete test suite")
            print()
        else:
            print("📋 Recommendations:\n")
            print("   1. Use ruff (not Black/flake8) for modern Python tooling")
            print("   2. Use uv (not pip/venv) for fast environment management")
            print("   3. Add yamllint for parameter validation")
            print("   4. Ensure comprehensive test coverage")
            print()

        print("=" * 70)

        return len(self.issues) == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_tooling.py /path/to/openfisca-country")
        print("\nExample:")
        print("  python check_tooling.py /home/user/openfisca-tunisia")
        sys.exit(1)

    package_path = Path(sys.argv[1])

    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    checker = ToolingChecker(package_path)
    success = checker.check_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
