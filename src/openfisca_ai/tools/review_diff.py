#!/usr/bin/env python3
"""Pre-digest a git diff for LLM review.

Parses a diff, identifies touched variables/parameters/tests, runs targeted
validations, and produces a compact structured report that any LLM agent can
consume with minimal tokens.

Usage:
  openfisca-ai review-diff <package-path> [--diff-file FILE] [--json] [--markdown]

If --diff-file is not given, reads from stdin.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_diff(diff_text: str) -> dict:
    """Extract structured information from a unified diff."""
    files_changed = []
    current_file = None
    additions = 0
    deletions = 0

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current_file:
                files_changed.append(current_file)
            match = re.search(r"b/(.+)$", line)
            fname = match.group(1) if match else "unknown"
            current_file = {
                "path": fname,
                "additions": 0,
                "deletions": 0,
                "is_parameter": "/parameters/" in fname and fname.endswith((".yaml", ".yml")),
                "is_variable": fname.endswith(".py") and "/variables/" in fname,
                "is_test": "/tests/" in fname,
                "is_ci": ".github/" in fname or ".gitlab" in fname,
                "is_doc": fname.endswith(".md") or fname == "CHANGELOG.md",
            }
            additions = 0
            deletions = 0
        elif line.startswith("+") and not line.startswith("+++"):
            if current_file:
                current_file["additions"] += 1
        elif line.startswith("-") and not line.startswith("---"):
            if current_file:
                current_file["deletions"] += 1

    if current_file:
        files_changed.append(current_file)

    return {
        "files": files_changed,
        "total_files": len(files_changed),
        "total_additions": sum(f["additions"] for f in files_changed),
        "total_deletions": sum(f["deletions"] for f in files_changed),
    }


def classify_changes(parsed: dict) -> dict:
    """Classify changes by domain."""
    files = parsed["files"]

    parameters = [f for f in files if f["is_parameter"]]
    variables = [f for f in files if f["is_variable"]]
    tests = [f for f in files if f["is_test"]]
    ci = [f for f in files if f["is_ci"]]
    docs = [f for f in files if f["is_doc"]]
    other = [f for f in files if not any([
        f["is_parameter"], f["is_variable"], f["is_test"], f["is_ci"], f["is_doc"],
    ])]

    is_trivial = (
        len(parameters) == 0
        and len(variables) == 0
        and parsed["total_additions"] + parsed["total_deletions"] < 20
    )

    change_type = "mineur"
    if parameters and variables:
        change_type = "évolution réglementaire"
    elif parameters:
        change_type = "mise à jour paramètres"
    elif variables:
        change_type = "modification formules"
    elif tests:
        change_type = "ajout/modification tests"
    elif ci or docs:
        change_type = "infrastructure/documentation"

    missing_tests = len(variables) > 0 and len(tests) == 0

    return {
        "change_type": change_type,
        "is_trivial": is_trivial,
        "missing_tests": missing_tests,
        "parameters_touched": [f["path"] for f in parameters],
        "variables_touched": [f["path"] for f in variables],
        "tests_touched": [f["path"] for f in tests],
        "ci_touched": [f["path"] for f in ci],
        "docs_touched": [f["path"] for f in docs],
        "other_touched": [f["path"] for f in other],
    }


def run_targeted_validation(package_path: Path, classification: dict) -> dict:
    """Run validation only on areas affected by the diff."""
    results = {}

    if classification["parameters_touched"]:
        try:
            from openfisca_ai.tools.validate_parameters import ParameterValidator
            pkg = _find_package_dir(package_path)
            validator = ParameterValidator(pkg)
            report = validator.validate_all()
            results["parameters"] = {
                "valid": report["valid"],
                "error_count": len(report["errors"]),
                "warning_count": len(report["warnings"]),
                "errors": report["errors"][:5],
            }
        except Exception as e:
            results["parameters"] = {"valid": False, "error": str(e)}

    if classification["variables_touched"]:
        try:
            from openfisca_ai.tools.validate_code import CodeValidator
            validator = CodeValidator(package_path)
            report = validator.validate_all()
            results["code"] = {
                "valid": report["valid"],
                "error_count": len(report["errors"]),
                "warning_count": len(report["warnings"]),
                "errors": report["errors"][:5],
            }
        except Exception as e:
            results["code"] = {"valid": False, "error": str(e)}

    return results


def _find_package_dir(repo_path: Path) -> Path:
    """Find the openfisca_* package directory."""
    for child in repo_path.iterdir():
        if (
            child.is_dir()
            and child.name.startswith("openfisca_")
            and (child / "__init__.py").exists()
        ):
            return child
    return repo_path


def build_report(diff_text: str, package_path: Path) -> dict:
    """Build a complete review-diff report."""
    parsed = parse_diff(diff_text)
    classification = classify_changes(parsed)
    validation = run_targeted_validation(package_path, classification)

    return {
        "summary": {
            "change_type": classification["change_type"],
            "is_trivial": classification["is_trivial"],
            "missing_tests": classification["missing_tests"],
            "files_changed": parsed["total_files"],
            "lines_added": parsed["total_additions"],
            "lines_deleted": parsed["total_deletions"],
        },
        "classification": classification,
        "validation": validation,
    }


def render_markdown(report: dict) -> str:
    """Render report as compact markdown."""
    s = report["summary"]
    c = report["classification"]
    lines = [
        f"## Review du diff",
        f"",
        f"- **Type** : {s['change_type']}",
        f"- **Fichiers** : {s['files_changed']} ({s['lines_added']}+ / {s['lines_deleted']}-)",
        f"- **Trivial** : {'oui' if s['is_trivial'] else 'non'}",
        f"- **Tests manquants** : {'oui — des variables sont modifiées sans tests' if s['missing_tests'] else 'non'}",
    ]

    if c["parameters_touched"]:
        lines.append(f"\n### Paramètres touchés")
        for p in c["parameters_touched"]:
            lines.append(f"- `{p}`")

    if c["variables_touched"]:
        lines.append(f"\n### Variables touchées")
        for v in c["variables_touched"]:
            lines.append(f"- `{v}`")

    v = report.get("validation", {})
    if v:
        lines.append(f"\n### Validation ciblée")
        for check_name, result in v.items():
            status = "OK" if result.get("valid") else "ERREURS"
            lines.append(f"- **{check_name}** : {status}")
            if result.get("errors"):
                for err in result["errors"][:3]:
                    msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                    lines.append(f"  - {msg}")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: openfisca-ai review-diff <package-path> [--diff-file FILE] [--json] [--markdown]")
        sys.exit(1)

    package_path = Path(args[0])
    diff_file = None
    output_format = "markdown"

    i = 1
    while i < len(args):
        if args[i] == "--diff-file" and i + 1 < len(args):
            diff_file = args[i + 1]
            i += 2
        elif args[i] == "--json":
            output_format = "json"
            i += 1
        elif args[i] == "--markdown":
            output_format = "markdown"
            i += 1
        else:
            i += 1

    if diff_file:
        diff_text = Path(diff_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        diff_text = sys.stdin.read()
    else:
        print("Error: provide --diff-file or pipe diff via stdin", file=sys.stderr)
        sys.exit(1)

    report = build_report(diff_text, package_path)

    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(report))


if __name__ == "__main__":
    main()
