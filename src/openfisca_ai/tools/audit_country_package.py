#!/usr/bin/env python3
"""
Run a unified audit over an OpenFisca country package.

Usage:
  uv run python audit_country_package.py /path/to/openfisca-country-repo
  uv run python audit_country_package.py /path/to/openfisca-country-repo --json
  uv run python audit_country_package.py /path/to/openfisca-country-repo --markdown
  uv run python audit_country_package.py /path/to/openfisca-country-repo --markdown --output report.md
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any


TOOL_FILES = {
    "baseline": "check_package_baseline.py",
    "tooling": "check_tooling.py",
    "units": "validate_units.py",
    "parameters": "validate_parameters.py",
    "code": "validate_code.py",
    "tests": "validate_tests.py",
    "patterns": "extract_patterns.py",
}


def load_tool_module(filename: str):
    """Load a sibling tool module from the tools/ directory."""
    module_path = Path(__file__).with_name(filename)
    module_name = f"openfisca_ai_tool_{module_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def count_by_type(items: list[dict[str, Any]]) -> dict[str, int]:
    """Count result items by their 'type' field."""
    return dict(Counter(item.get("type", "<unknown>") for item in items))


class CountryPackageAuditor:
    """Aggregate the validators and pattern extractor into one report."""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path)
        self.modules = {name: load_tool_module(filename) for name, filename in TOOL_FILES.items()}
        self._package_scope_path: Path | None = None
        self._repo_scope_path: Path = self.package_path

    def audit(self) -> dict[str, Any]:
        """Run all checks and return a normalized report."""
        self.resolve_paths()
        checks = {
            "baseline": self.run_baseline(),
            "tooling": self.run_tooling(),
            "units": self.run_units(),
            "parameters": self.run_parameters(),
            "code": self.run_code(),
            "tests": self.run_tests(),
            "patterns": self.run_patterns(),
        }
        return {
            "package_path": str(self.package_path.resolve()),
            "repo_scope_path": str(self._repo_scope_path.resolve()),
            "package_scope_path": str(self.package_scope_path.resolve()),
            "checks": checks,
            "summary": self.build_summary(checks),
        }

    def resolve_paths(self):
        """Resolve the repository root and country package directory paths."""
        if self._package_scope_path is not None:
            return

        if self.is_country_package_dir(self.package_path):
            self._package_scope_path = self.package_path
            self._repo_scope_path = self.package_path.parent
            return

        self._repo_scope_path = self.package_path
        candidates = [
            path
            for path in self.package_path.iterdir()
            if self.is_country_package_dir(path)
        ]
        if len(candidates) == 1:
            self._package_scope_path = candidates[0]
        else:
            self._package_scope_path = self.package_path

    @property
    def package_scope_path(self) -> Path:
        """Path to the country package module for package-scoped tools."""
        self.resolve_paths()
        assert self._package_scope_path is not None
        return self._package_scope_path

    def is_country_package_dir(self, path: Path) -> bool:
        """Return True when a path looks like an OpenFisca country package module."""
        return (
            path.is_dir()
            and path.name.startswith("openfisca_")
            and (path / "__init__.py").exists()
        )

    def run_baseline(self) -> dict[str, Any]:
        """Run package baseline checks."""
        module = self.modules["baseline"]
        checker = module.PackageBaselineChecker(self._repo_scope_path)
        output, valid = self.capture(checker.check_all)
        return {
            "valid": valid,
            "issues": checker.issues,
            "warnings": checker.warnings,
            "info": checker.info,
            "issue_types": count_by_type(checker.issues),
            "warning_types": count_by_type(checker.warnings),
            "output": output,
        }

    def run_tooling(self) -> dict[str, Any]:
        """Run tooling checks."""
        module = self.modules["tooling"]
        checker = module.ToolingChecker(self._repo_scope_path)
        output, valid = self.capture(checker.check_all)
        return {
            "valid": valid,
            "issues": checker.issues,
            "warnings": checker.warnings,
            "info": checker.info,
            "issue_types": count_by_type(checker.issues),
            "warning_types": count_by_type(checker.warnings),
            "output": output,
        }

    def run_units(self) -> dict[str, Any]:
        """Run unit coverage checks."""
        module = self.modules["units"]
        validator = module.UnitsValidator(self.package_scope_path)
        output, valid = self.capture(validator.validate)
        undefined_units = sorted(set(validator.units_used.keys()) - validator.units_defined)
        return {
            "valid": valid,
            "files_without_unit_count": len(validator.files_without_unit),
            "undefined_units": undefined_units,
            "parameter_files_count": validator.parameter_files_count,
            "units_defined_count": len(validator.units_defined),
            "units_used_count": len(validator.units_used),
            "output": output,
        }

    def run_parameters(self) -> dict[str, Any]:
        """Run parameter metadata checks."""
        module = self.modules["parameters"]
        validator = module.ParameterValidator(self.package_scope_path)
        output, report = self.capture(validator.validate_all)
        errors = report["errors"]
        warnings = report["warnings"]
        return {
            "valid": report["valid"],
            "errors": errors,
            "warnings": warnings,
            "error_types": count_by_type(errors),
            "warning_types": count_by_type(warnings),
            "output": output,
        }

    def run_code(self) -> dict[str, Any]:
        """Run Python code checks."""
        module = self.modules["code"]
        validator = module.CodeValidator(self._repo_scope_path)
        output, report = self.capture(validator.validate_all)
        errors = report["errors"]
        warnings = report["warnings"]
        return {
            "valid": report["valid"],
            "files_checked": validator.files_checked,
            "errors": errors,
            "warnings": warnings,
            "error_types": count_by_type(errors),
            "warning_types": count_by_type(warnings),
            "output": output,
        }

    def run_tests(self) -> dict[str, Any]:
        """Run test coverage checks."""
        module = self.modules["tests"]
        validator = module.TestValidator(self._repo_scope_path)
        output, report = self.capture(validator.validate_all)
        errors = report["errors"]
        warnings = report["warnings"]
        return {
            "valid": report["valid"],
            "formula_variable_count": len(validator.formula_variables),
            "errors": errors,
            "warnings": warnings,
            "error_types": count_by_type(errors),
            "warning_types": count_by_type(warnings),
            "output": output,
        }

    def run_patterns(self) -> dict[str, Any]:
        """Extract structural patterns from the package."""
        module = self.modules["patterns"]
        extractor = module.PatternExtractor(self._repo_scope_path)
        output, report = self.capture(extractor.extract_all)
        return {
            "valid": True,
            "report": report,
            "output": output,
        }

    def build_summary(self, checks: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Build a top-level audit summary."""
        failing_checks = [
            name
            for name, result in checks.items()
            if name != "patterns" and not result.get("valid", True)
        ]
        total_errors = 0
        total_warnings = 0

        for result in checks.values():
            total_errors += len(result.get("issues", []))
            total_errors += len(result.get("errors", []))
            total_warnings += len(result.get("warnings", []))

        pattern_report = checks["patterns"]["report"]
        return {
            "all_checks_passed": len(failing_checks) == 0,
            "failing_checks": failing_checks,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "country_package": pattern_report["country_package"],
            "formula_variables": pattern_report["variables"]["formula_variables"],
            "parameter_files": pattern_report["parameters"]["yaml_files"],
            "yaml_tests": pattern_report["tests"]["yaml_tests"],
            "python_tests": pattern_report["tests"]["python_tests"],
        }

    def capture(self, fn):
        """Capture stdout from a tool call and return its result."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = fn()
        return buffer.getvalue(), result


def render_text(report: dict[str, Any]) -> str:
    """Render a concise human-readable text report."""
    summary = report["summary"]
    lines = [
        "OPENFISCA AI AUDIT",
        f"Package: {summary['country_package']}",
        f"Path: {report['package_path']}",
        "",
        "Summary:",
        f"- all_checks_passed: {'yes' if summary['all_checks_passed'] else 'no'}",
        f"- failing_checks: {', '.join(summary['failing_checks']) or 'none'}",
        f"- total_errors: {summary['total_errors']}",
        f"- total_warnings: {summary['total_warnings']}",
        f"- formula_variables: {summary['formula_variables']}",
        f"- parameter_files: {summary['parameter_files']}",
        f"- yaml_tests: {summary['yaml_tests']}",
        f"- python_tests: {summary['python_tests']}",
        "",
        "Checks:",
    ]

    for check_name, result in report["checks"].items():
        if check_name == "patterns":
            continue
        issue_count = len(result.get("issues", [])) + len(result.get("errors", []))
        warning_count = len(result.get("warnings", []))
        lines.append(
            f"- {check_name}: {'pass' if result.get('valid', True) else 'fail'} "
            f"(errors={issue_count}, warnings={warning_count})"
        )

    lines.extend(
        [
            "",
            "Pattern Snapshot:",
            f"- entities: {report['checks']['patterns']['report']['variables']['entities']}",
            f"- definition_periods: {report['checks']['patterns']['report']['variables']['definition_periods']}",
            f"- variable_domains: {report['checks']['patterns']['report']['variables']['top_domains']}",
            f"- parameter_domains: {report['checks']['patterns']['report']['parameters']['top_domains']}",
        ]
    )
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    """Render a markdown audit report."""
    summary = report["summary"]
    lines = [
        "# OpenFisca AI Audit",
        "",
        f"- Package: `{summary['country_package']}`",
        f"- Path: `{report['package_path']}`",
        f"- All checks passed: `{'yes' if summary['all_checks_passed'] else 'no'}`",
        f"- Failing checks: `{', '.join(summary['failing_checks']) or 'none'}`",
        f"- Total errors: `{summary['total_errors']}`",
        f"- Total warnings: `{summary['total_warnings']}`",
        "",
        "## Checks",
        "",
    ]

    for check_name, result in report["checks"].items():
        if check_name == "patterns":
            continue
        issue_count = len(result.get("issues", [])) + len(result.get("errors", []))
        warning_count = len(result.get("warnings", []))
        lines.extend(
            [
                f"### `{check_name}`",
                "",
                f"- Status: `{'pass' if result.get('valid', True) else 'fail'}`",
                f"- Errors: `{issue_count}`",
                f"- Warnings: `{warning_count}`",
            ]
        )
        if result.get("error_types"):
            lines.append(f"- Error types: `{result['error_types']}`")
        if result.get("warning_types"):
            lines.append(f"- Warning types: `{result['warning_types']}`")
        lines.append("")

    pattern_report = report["checks"]["patterns"]["report"]
    lines.extend(
        [
            "## Pattern Snapshot",
            "",
            f"- Entities: `{pattern_report['variables']['entities']}`",
            f"- Definition periods: `{pattern_report['variables']['definition_periods']}`",
            f"- Set input helpers: `{pattern_report['variables']['set_input_helpers']}`",
            f"- Formula patterns: `{pattern_report['variables']['formula_patterns']}`",
            f"- Aggregations: `{pattern_report['variables']['aggregation_methods']}`",
            f"- Variable domains: `{pattern_report['variables']['top_domains']}`",
            f"- Parameter domains: `{pattern_report['parameters']['top_domains']}`",
            f"- Unit types: `{pattern_report['parameters']['unit_types']}`",
            f"- Test domains: `{pattern_report['tests']['top_domains']}`",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(args: list[str]) -> tuple[Path, str, Path | None]:
    """Parse CLI arguments."""
    if not args:
        raise ValueError(
            "Usage: uv run python audit_country_package.py /path/to/openfisca-country-repo [--json|--markdown] [--output path]"
        )

    package_path = Path(args[0])
    output_format = "text"
    output_path: Path | None = None

    index = 1
    while index < len(args):
        arg = args[index]
        if arg == "--json":
            output_format = "json"
        elif arg == "--markdown":
            output_format = "markdown"
        elif arg == "--output":
            index += 1
            if index >= len(args):
                raise ValueError("--output requires a file path")
            output_path = Path(args[index])
        else:
            raise ValueError(f"Unknown argument: {arg}")
        index += 1

    return package_path, output_format, output_path


def main():
    try:
        package_path, output_format, output_path = parse_args(sys.argv[1:])
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    auditor = CountryPackageAuditor(package_path)
    report = auditor.audit()

    if output_format == "json":
        rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
    elif output_format == "markdown":
        rendered = render_markdown(report)
    else:
        rendered = render_text(report)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")

    print(rendered)
    failing_checks = report["summary"]["failing_checks"]
    sys.exit(0 if not failing_checks else 1)


if __name__ == "__main__":
    main()
