#!/usr/bin/env python3
"""
Extract reusable structural and coding patterns from an OpenFisca country package.

Usage: uv run python extract_patterns.py /path/to/openfisca-country-repo [--json]
"""

import ast
import json
import sys
from collections import Counter
from pathlib import Path

import yaml


class FormulaPatternVisitor(ast.NodeVisitor):
    """Collect notable OpenFisca idioms from a formula method."""

    def __init__(self):
        self.calls = Counter()
        self.attribute_calls = Counter()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls[node.func.id] += 1
        elif isinstance(node.func, ast.Attribute):
            self.attribute_calls[node.func.attr] += 1
        self.generic_visit(node)


class PatternExtractor:
    """Extract reusable patterns from a country package."""

    def __init__(self, package_path: Path):
        self.input_path = Path(package_path)
        self.repo_root = Path(package_path)
        self.country_package_dir: Path | None = None

    def is_country_package_dir(self, path: Path) -> bool:
        """Return True when a path looks like an OpenFisca country package module."""
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
            return

        candidates = [
            path for path in self.repo_root.iterdir() if self.is_country_package_dir(path)
        ]
        if len(candidates) == 1:
            self.country_package_dir = candidates[0]

    def extract_all(self) -> dict:
        """Extract a structured pattern summary."""
        self.detect_layout()
        if self.country_package_dir is None:
            raise ValueError(
                f"Could not find an OpenFisca country package under {self.input_path}"
            )

        package_dir = self.country_package_dir
        variables_dir = package_dir / "variables"
        parameters_dir = package_dir / "parameters"
        tests_dir = self.repo_root / "tests"

        report = {
            "repo_root": str(self.repo_root),
            "country_package": package_dir.name,
            "structure": {
                "has_entities_py": (package_dir / "entities.py").exists(),
                "has_units_yaml": (package_dir / "units.yaml").exists(),
                "has_parameters_dir": parameters_dir.exists(),
                "has_variables_dir": variables_dir.exists(),
                "has_reforms_dir": (package_dir / "reforms").exists(),
                "has_situation_examples_dir": (package_dir / "situation_examples").exists(),
                "has_tests_dir": tests_dir.exists(),
            },
            "variables": self.extract_variable_patterns(variables_dir),
            "parameters": self.extract_parameter_patterns(parameters_dir),
            "tests": self.extract_test_patterns(tests_dir),
        }
        return report

    def extract_variable_patterns(self, variables_dir: Path) -> dict:
        """Extract patterns from Python variables."""
        summary = {
            "python_files": 0,
            "variable_classes": 0,
            "formula_variables": 0,
            "entities": {},
            "definition_periods": {},
            "set_input_helpers": {},
            "top_domains": {},
            "formula_patterns": {
                "uses_parameters": 0,
                "uses_where": 0,
                "uses_min": 0,
                "uses_max": 0,
                "uses_round": 0,
                "uses_brackets_calc": 0,
                "uses_members": 0,
                "uses_has_role": 0,
                "uses_select": 0,
            },
            "aggregation_methods": {},
        }

        if not variables_dir.exists():
            return summary

        entity_counter = Counter()
        period_counter = Counter()
        set_input_counter = Counter()
        domain_counter = Counter()
        aggregation_counter = Counter()
        formula_pattern_counter = Counter()

        python_files = sorted(
            path for path in variables_dir.rglob("*.py") if "__pycache__" not in path.parts
        )
        summary["python_files"] = len(python_files)

        for filepath in python_files:
            relative = filepath.relative_to(variables_dir)
            parts = relative.parts
            domain = parts[0] if len(parts) > 1 else "<root>"
            domain_counter[domain] += 1

            tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or not self.is_variable_class(node):
                    continue

                summary["variable_classes"] += 1
                assignments = self.collect_class_assignments(node)

                entity_name = self.render_name(assignments.get("entity"))
                if entity_name:
                    entity_counter[entity_name] += 1

                period_name = self.render_name(assignments.get("definition_period"))
                if period_name:
                    period_counter[period_name] += 1

                set_input_name = self.render_name(assignments.get("set_input"))
                if set_input_name:
                    set_input_counter[set_input_name] += 1

                formula_methods = [
                    statement
                    for statement in node.body
                    if isinstance(statement, ast.FunctionDef)
                    and statement.name.startswith("formula")
                ]
                if formula_methods:
                    summary["formula_variables"] += 1

                for method in formula_methods:
                    visitor = FormulaPatternVisitor()
                    visitor.visit(method)

                    arg_names = {arg.arg for arg in method.args.args}
                    if "parameters" in arg_names or visitor.calls.get("parameters"):
                        formula_pattern_counter["uses_parameters"] += 1
                    if visitor.calls.get("where"):
                        formula_pattern_counter["uses_where"] += 1
                    if visitor.calls.get("min_") or visitor.calls.get("minimum"):
                        formula_pattern_counter["uses_min"] += 1
                    if visitor.calls.get("max_") or visitor.calls.get("maximum"):
                        formula_pattern_counter["uses_max"] += 1
                    if visitor.calls.get("round"):
                        formula_pattern_counter["uses_round"] += 1
                    if visitor.calls.get("select"):
                        formula_pattern_counter["uses_select"] += 1
                    if visitor.attribute_calls.get("calc"):
                        formula_pattern_counter["uses_brackets_calc"] += 1
                    if visitor.attribute_calls.get("members"):
                        formula_pattern_counter["uses_members"] += 1
                    if visitor.attribute_calls.get("has_role"):
                        formula_pattern_counter["uses_has_role"] += 1

                    for attr_name in ("sum", "any", "all", "min", "max"):
                        if visitor.attribute_calls.get(attr_name):
                            aggregation_counter[attr_name] += visitor.attribute_calls[attr_name]

        summary["entities"] = dict(entity_counter)
        summary["definition_periods"] = dict(period_counter)
        summary["set_input_helpers"] = dict(set_input_counter)
        summary["top_domains"] = dict(domain_counter.most_common(10))
        summary["formula_patterns"] = {
            key: formula_pattern_counter.get(key, 0)
            for key in summary["formula_patterns"]
        }
        summary["aggregation_methods"] = dict(aggregation_counter)
        return summary

    def extract_parameter_patterns(self, parameters_dir: Path) -> dict:
        """Extract structural patterns from YAML parameters."""
        summary = {
            "yaml_files": 0,
            "scale_files": 0,
            "top_domains": {},
            "unit_types": {},
        }
        if not parameters_dir.exists():
            return summary

        domain_counter = Counter()
        unit_counter = Counter()
        scale_files = 0

        yaml_files = sorted(
            path
            for path in parameters_dir.rglob("*.yaml")
            if path.name not in {"index.yaml", "units.yaml"}
        )
        summary["yaml_files"] = len(yaml_files)

        for filepath in yaml_files:
            relative = filepath.relative_to(parameters_dir)
            parts = relative.parts
            domain = parts[0] if parts else "<root>"
            domain_counter[domain] += 1

            content = yaml.safe_load(filepath.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                continue

            metadata = content.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}

            if "brackets" in content:
                scale_files += 1
                for key in ("threshold_unit", "rate_unit", "amount_unit"):
                    unit_name = metadata.get(key)
                    if unit_name:
                        unit_counter[unit_name] += 1
            else:
                unit_name = content.get("unit") or metadata.get("unit")
                if unit_name:
                    unit_counter[unit_name] += 1

        summary["scale_files"] = scale_files
        summary["top_domains"] = dict(domain_counter.most_common(10))
        summary["unit_types"] = dict(unit_counter.most_common(10))
        return summary

    def extract_test_patterns(self, tests_dir: Path) -> dict:
        """Extract high-level patterns from tests."""
        summary = {
            "yaml_tests": 0,
            "python_tests": 0,
            "top_domains": {},
        }
        if not tests_dir.exists():
            return summary

        yaml_tests = sorted(tests_dir.rglob("*.yaml"))
        py_tests = sorted(tests_dir.rglob("test_*.py"))
        summary["yaml_tests"] = len(yaml_tests)
        summary["python_tests"] = len(py_tests)

        domain_counter = Counter()
        for filepath in yaml_tests + py_tests:
            relative = filepath.relative_to(tests_dir)
            parts = relative.parts
            domain = parts[0] if len(parts) > 1 else "<root>"
            domain_counter[domain] += 1

        summary["top_domains"] = dict(domain_counter.most_common(10))
        return summary

    def is_variable_class(self, node: ast.ClassDef) -> bool:
        """Return True when a class looks like an OpenFisca Variable."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Variable":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Variable":
                return True
        return False

    def collect_class_assignments(self, node: ast.ClassDef) -> dict[str, ast.AST]:
        """Collect simple class-level assignments."""
        assignments = {}
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = statement.value
            elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                assignments[statement.target.id] = statement.value
        return assignments

    def render_name(self, node: ast.AST | None) -> str | None:
        """Render a simple Name/Attribute AST node to a string."""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self.render_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None


def print_human_report(report: dict):
    """Print a concise human-readable report."""
    print("=" * 70)
    print("OPENFISCA PATTERN REPORT")
    print("=" * 70)
    print()
    print(f"Package: {report['country_package']}")
    print()

    structure = report["structure"]
    print("Structure:")
    for key, value in structure.items():
        print(f"  - {key}: {'yes' if value else 'no'}")
    print()

    variables = report["variables"]
    print("Variables:")
    print(f"  - python_files: {variables['python_files']}")
    print(f"  - variable_classes: {variables['variable_classes']}")
    print(f"  - formula_variables: {variables['formula_variables']}")
    print(f"  - entities: {variables['entities']}")
    print(f"  - definition_periods: {variables['definition_periods']}")
    print(f"  - set_input_helpers: {variables['set_input_helpers']}")
    print(f"  - top_domains: {variables['top_domains']}")
    print(f"  - formula_patterns: {variables['formula_patterns']}")
    print(f"  - aggregation_methods: {variables['aggregation_methods']}")
    print()

    parameters = report["parameters"]
    print("Parameters:")
    print(f"  - yaml_files: {parameters['yaml_files']}")
    print(f"  - scale_files: {parameters['scale_files']}")
    print(f"  - top_domains: {parameters['top_domains']}")
    print(f"  - unit_types: {parameters['unit_types']}")
    print()

    tests = report["tests"]
    print("Tests:")
    print(f"  - yaml_tests: {tests['yaml_tests']}")
    print(f"  - python_tests: {tests['python_tests']}")
    print(f"  - top_domains: {tests['top_domains']}")
    print()
    print("=" * 70)


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: uv run python extract_patterns.py /path/to/openfisca-country-repo [--json]")
        sys.exit(1)

    package_path = Path(args[0])
    emit_json = "--json" in args[1:]

    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    extractor = PatternExtractor(package_path)
    report = extractor.extract_all()

    if emit_json:
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print_human_report(report)


if __name__ == "__main__":
    main()
