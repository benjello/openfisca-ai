#!/usr/bin/env python3
"""Check OpenFisca country package baseline structure."""

import sys
from pathlib import Path


class PackageBaselineChecker:
    """Check the baseline structure expected in most OpenFisca country packages."""

    def __init__(self, package_path: Path):
        self.input_path = Path(package_path)
        self.repo_root = Path(package_path)
        self.country_package_dir: Path | None = None
        self.issues = []
        self.warnings = []
        self.info = []

    def check_all(self):
        """Run all baseline checks."""
        print(f"🔍 Checking OpenFisca package baseline in {self.input_path}...\n")

        self.detect_layout()
        self.check_pyproject()
        self.discover_country_package()
        self.check_country_package_files()
        self.check_tests()
        self.check_makefile()
        self.check_ci()

        return self.report()

    def detect_layout(self):
        """Resolve whether the input path is a repo root or the package directory itself."""
        if (self.input_path / "pyproject.toml").exists():
            self.repo_root = self.input_path
            return

        if self.is_country_package_dir(self.input_path):
            self.country_package_dir = self.input_path
            self.repo_root = self.input_path.parent
            self.info.append(
                f"✅ Input path looks like a country package directory: {self.country_package_dir.name}"
            )

    def is_country_package_dir(self, path: Path) -> bool:
        """Return True if the path looks like an OpenFisca country package module."""
        return (
            path.is_dir()
            and path.name.startswith("openfisca_")
            and (path / "__init__.py").exists()
        )

    def add_issue(self, issue_type: str, message: str, fix: str):
        """Record a critical baseline issue."""
        self.issues.append(
            {
                "type": issue_type,
                "message": message,
                "fix": fix,
            }
        )

    def add_warning(self, warning_type: str, message: str, fix: str):
        """Record a non-critical baseline warning."""
        self.warnings.append(
            {
                "type": warning_type,
                "message": message,
                "fix": fix,
            }
        )

    def check_pyproject(self):
        """Check pyproject.toml and basic packaging metadata."""
        pyproject = self.repo_root / "pyproject.toml"
        if not pyproject.exists():
            self.add_issue(
                "missing_pyproject",
                "Missing pyproject.toml",
                "Add a pyproject.toml as the source of truth for packaging and tooling",
            )
            return

        content = pyproject.read_text(encoding="utf-8")
        self.info.append("✅ pyproject.toml found")

        if "openfisca-core" in content:
            self.info.append("✅ pyproject.toml declares openfisca-core")
        else:
            self.add_warning(
                "missing_openfisca_core_dependency",
                "pyproject.toml does not mention openfisca-core",
                "Declare openfisca-core[web-api] in project dependencies if this is a country package",
            )

        uv_lock = self.repo_root / "uv.lock"
        if uv_lock.exists():
            self.info.append("✅ uv.lock found")
        else:
            self.add_warning(
                "missing_uv_lock",
                "uv.lock is missing",
                "Run 'uv sync' and commit uv.lock for a modern uv-based workflow",
            )

    def discover_country_package(self):
        """Find the installable OpenFisca country package directory."""
        if self.country_package_dir is not None:
            self.info.append(f"✅ Country package detected: {self.country_package_dir.name}")
            return

        candidates = [
            path
            for path in self.repo_root.iterdir()
            if self.is_country_package_dir(path)
        ]

        if not candidates:
            self.add_issue(
                "missing_country_package",
                "Could not find an installable package directory named like openfisca_<country>",
                "Create a top-level package such as openfisca_tunisia with __init__.py",
            )
            return

        if len(candidates) > 1:
            names = ", ".join(sorted(path.name for path in candidates))
            self.add_issue(
                "ambiguous_country_package",
                f"Found multiple candidate package directories: {names}",
                "Keep a single top-level OpenFisca country package or point the tool at the package directory itself",
            )
            return

        self.country_package_dir = candidates[0]
        self.info.append(f"✅ Country package detected: {self.country_package_dir.name}")

    def check_country_package_files(self):
        """Check the standard files and directories inside the country package."""
        if self.country_package_dir is None:
            return

        package_dir = self.country_package_dir

        required_files = {
            "__init__.py": "Package marker file",
            "entities.py": "Entity definitions for the simulation",
            "units.yaml": "Unit definitions used by parameters",
        }
        for filename, purpose in required_files.items():
            path = package_dir / filename
            if not path.exists():
                self.add_issue(
                    f"missing_{filename.replace('.', '_')}",
                    f"Missing {package_dir.name}/{filename} ({purpose})",
                    f"Add {filename} to the country package",
                )

        required_dirs = {
            "parameters": "Parameter YAML files",
            "variables": "Variable formulas",
        }
        for dirname, purpose in required_dirs.items():
            path = package_dir / dirname
            if not path.exists():
                self.add_issue(
                    f"missing_{dirname}_dir",
                    f"Missing {package_dir.name}/{dirname}/ ({purpose})",
                    f"Create {dirname}/ in the country package",
                )

        parameters_dir = package_dir / "parameters"
        if parameters_dir.exists():
            index_yaml = parameters_dir / "index.yaml"
            if index_yaml.exists():
                self.info.append("✅ parameters/index.yaml found")
            else:
                self.add_warning(
                    "missing_parameters_index",
                    f"Missing {package_dir.name}/parameters/index.yaml",
                    "Add parameters/index.yaml to expose the parameter hierarchy cleanly",
                )

        for optional_dir, description in (
            ("reforms", "policy variants and temporary reforms"),
            ("situation_examples", "sample inputs for demos and smoke tests"),
        ):
            path = package_dir / optional_dir
            if path.exists():
                self.info.append(f"✅ {optional_dir}/ found")
            else:
                self.add_warning(
                    f"missing_{optional_dir}_dir",
                    f"Missing {package_dir.name}/{optional_dir}/",
                    f"Add {optional_dir}/ when the package starts needing {description}",
                )

    def check_tests(self):
        """Check the test directory and baseline OpenFisca YAML tests."""
        tests_dir = self.repo_root / "tests"
        if not tests_dir.exists():
            self.add_issue(
                "missing_tests_dir",
                "Missing tests/ directory",
                "Add a tests/ directory with YAML tests runnable by 'openfisca test'",
            )
            return

        yaml_tests = list(tests_dir.rglob("*.yaml"))
        py_tests = list(tests_dir.rglob("test_*.py"))

        if not yaml_tests and not py_tests:
            self.add_warning(
                "empty_tests",
                "tests/ exists but contains no YAML or Python tests",
                "Add at least YAML legislative tests, and Python tests when package-level behavior needs them",
            )
            return

        if yaml_tests:
            self.info.append(f"✅ YAML tests found: {len(yaml_tests)}")
        else:
            self.add_warning(
                "missing_yaml_tests",
                "No YAML tests found under tests/",
                "Add YAML tests as the baseline legislative validation layer",
            )

        if py_tests:
            self.info.append(f"✅ Python tests found: {len(py_tests)}")

    def check_makefile(self):
        """Check common Makefile entry points used across country packages."""
        makefile = self.repo_root / "Makefile"
        if not makefile.exists():
            self.add_warning(
                "missing_makefile",
                "No Makefile found",
                "Add a small Makefile with common targets such as install, build, check-style, and test",
            )
            return

        content = makefile.read_text(encoding="utf-8")
        self.info.append("✅ Makefile found")

        if "uv " in content or "uv\n" in content:
            self.info.append("✅ Makefile uses uv")
        else:
            self.add_warning(
                "no_uv_in_makefile",
                "Makefile does not mention uv",
                "Prefer uv-based commands for dependency sync, lint, and tests",
            )

        targets = [
            "install",
            "build",
            "check-syntax-errors",
            "check-style",
            "test",
        ]
        missing_targets = [target for target in targets if f"{target}:" not in content]
        if missing_targets:
            self.add_warning(
                "missing_make_targets",
                f"Makefile is missing common targets: {', '.join(missing_targets)}",
                "Add the shared targets used across OpenFisca country packages",
            )

        if "openfisca test" not in content:
            self.add_warning(
                "missing_openfisca_test_command",
                "Makefile does not expose an 'openfisca test' command",
                "Prefer running YAML tests through 'openfisca test --country-package ... tests'",
            )

    def check_ci(self):
        """Check for baseline CI workflows."""
        workflows_dir = self.repo_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.add_warning(
                "missing_ci_workflows",
                "No .github/workflows directory found",
                "Add CI workflows for linting, tests, and package build",
            )
            return

        workflow_files = sorted(workflows_dir.glob("*.yml")) + sorted(workflows_dir.glob("*.yaml"))
        if not workflow_files:
            self.add_warning(
                "empty_ci_workflows",
                ".github/workflows exists but contains no workflow files",
                "Add at least one workflow running lint and tests",
            )
            return

        self.info.append(f"✅ CI workflows found: {len(workflow_files)}")
        content = "\n".join(
            workflow.read_text(encoding="utf-8") for workflow in workflow_files
        )

        if "uv " in content or "uv\n" in content:
            self.info.append("✅ CI mentions uv")
        else:
            self.add_warning(
                "no_uv_in_ci",
                "CI workflows do not mention uv",
                "Prefer uv in CI to match local package workflows",
            )

        if "openfisca test" in content or "pytest" in content:
            self.info.append("✅ CI includes test execution")
        else:
            self.add_warning(
                "no_test_job_in_ci",
                "CI workflows do not appear to run tests",
                "Add a test job running YAML tests and any needed Python tests",
            )

        if "yamllint" in content or "validate_yaml" in content:
            self.info.append("✅ CI includes YAML validation")
        else:
            self.add_warning(
                "no_yaml_validation_in_ci",
                "CI workflows do not appear to validate YAML files",
                "Add yamllint or a dedicated YAML validation workflow",
            )

    def report(self):
        """Print a report and return True when no critical issue remains."""
        print("=" * 70)
        print("PACKAGE BASELINE REPORT")
        print("=" * 70)
        print()

        if self.info:
            print("📊 Status:\n")
            for item in self.info:
                print(f"   {item}")
            print()

        if self.issues:
            print(f"❌ {len(self.issues)} CRITICAL ISSUES:\n")
            for issue in self.issues:
                print(f"   {issue['message']}")
                print(f"   💡 Fix: {issue['fix']}")
                print()

        if self.warnings:
            print(f"⚠️  {len(self.warnings)} WARNINGS:\n")
            for warning in self.warnings:
                print(f"   {warning['message']}")
                print(f"   💡 Fix: {warning['fix']}")
                print()

        if not self.issues and not self.warnings:
            print("✅ ALL CHECKS PASSED!\n")
            print("Repository matches the shared OpenFisca country package baseline.")
            print()
        elif not self.issues:
            print("📋 Baseline is usable, but some modern conventions are missing.\n")
        else:
            print("📋 Baseline is incomplete. Fix the critical structure first.\n")

        print("=" * 70)

        return len(self.issues) == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python check_package_baseline.py /path/to/openfisca-country-repo")
        print("\nExample:")
        print("  uv run python check_package_baseline.py /home/user/openfisca-tunisia")
        sys.exit(1)

    package_path = Path(sys.argv[1])
    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    checker = PackageBaselineChecker(package_path)
    success = checker.check_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
