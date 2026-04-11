#!/usr/bin/env python3
"""
Validate OpenFisca Python code against common coding principles.

Usage: uv run python validate_code.py /path/to/openfisca-country-repo
"""

import ast
import re
import sys
from pathlib import Path


ALLOWED_NUMERIC_CONSTANTS = {0, 1, 4, 12}
TODO_PATTERN = re.compile(r"\b(?:TODO|FIXME|XXX)\b", re.IGNORECASE)


class FormulaVisitor(ast.NodeVisitor):
    """Collect suspicious patterns inside an OpenFisca formula."""

    def __init__(self):
        self.loop_nodes = []
        self.comprehension_nodes = []
        self.if_nodes = []
        self.pass_nodes = []
        self.ellipsis_nodes = []
        self.numeric_constants = []

    def visit_For(self, node):
        self.loop_nodes.append(node)
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.loop_nodes.append(node)
        self.generic_visit(node)

    def visit_While(self, node):
        self.loop_nodes.append(node)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.comprehension_nodes.append(node)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.comprehension_nodes.append(node)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.comprehension_nodes.append(node)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.comprehension_nodes.append(node)
        self.generic_visit(node)

    def visit_If(self, node):
        self.if_nodes.append(node)
        self.generic_visit(node)

    def visit_Pass(self, node):
        self.pass_nodes.append(node)
        self.generic_visit(node)

    def visit_Constant(self, node):
        if node.value is Ellipsis:
            self.ellipsis_nodes.append(node)
        elif isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if node.value not in ALLOWED_NUMERIC_CONSTANTS:
                self.numeric_constants.append(node)
        self.generic_visit(node)


class CodeValidator:
    """Validate Python code in an OpenFisca country package."""

    def __init__(self, package_path: Path):
        self.input_path = Path(package_path)
        self.repo_root = Path(package_path)
        self.country_package_dir: Path | None = None
        self.errors = []
        self.warnings = []
        self.info = []
        self.files_checked = 0

    def add_error(self, error_type: str, message: str, file_path: str):
        """Record a code validation error."""
        self.errors.append(
            {
                "type": error_type,
                "severity": "ERROR",
                "message": message,
                "file": file_path,
            }
        )

    def add_warning(self, warning_type: str, message: str, file_path: str):
        """Record a code validation warning."""
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
        print(f"🔍 Validating Python code in {self.input_path}...\n")

        self.detect_layout()
        if self.country_package_dir is None:
            return self.get_report()

        python_files = self.collect_python_files()
        self.files_checked = len(python_files)
        print(f"📋 Checking {self.files_checked} Python files...\n")

        for filepath in python_files:
            self.validate_file(filepath)

        return self.get_report()

    def collect_python_files(self) -> list[Path]:
        """Collect Python files from the country package."""
        assert self.country_package_dir is not None
        return sorted(
            path
            for path in self.country_package_dir.rglob("*.py")
            if "__pycache__" not in path.parts
        )

    def validate_file(self, filepath: Path):
        """Validate one Python file."""
        relative_path = str(filepath.relative_to(self.repo_root))
        text = filepath.read_text(encoding="utf-8")

        if TODO_PATTERN.search(text):
            self.add_error(
                "todo_comment",
                "Found TODO/FIXME/XXX marker in Python code",
                relative_path,
            )

        try:
            tree = ast.parse(text, filename=str(filepath))
        except SyntaxError as exc:
            self.add_error(
                "syntax_error",
                f"Syntax error: {exc.msg}",
                relative_path,
            )
            return

        for node in tree.body:
            if isinstance(node, ast.ClassDef) and self.is_variable_class(node):
                self.validate_variable_class(node, relative_path)

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

    def validate_variable_class(self, node: ast.ClassDef, relative_path: str):
        """Validate one OpenFisca variable class."""
        assignments = self.collect_class_assignments(node)

        if "entity" not in assignments:
            self.add_error(
                "missing_entity",
                f"Variable class '{node.name}' is missing 'entity'",
                relative_path,
            )

        if "definition_period" not in assignments:
            self.add_error(
                "missing_definition_period",
                f"Variable class '{node.name}' is missing 'definition_period'",
                relative_path,
            )

        formula_methods = [
            statement
            for statement in node.body
            if isinstance(statement, ast.FunctionDef) and statement.name.startswith("formula")
        ]

        for method in formula_methods:
            self.validate_formula_method(node.name, method, relative_path)

    def validate_formula_method(
        self,
        class_name: str,
        method: ast.FunctionDef,
        relative_path: str,
    ):
        """Validate one formula method."""
        visitor = FormulaVisitor()
        visitor.visit(method)

        if visitor.pass_nodes:
            self.add_error(
                "placeholder_pass",
                f"{class_name}.{method.name} contains 'pass'",
                relative_path,
            )

        if visitor.ellipsis_nodes:
            self.add_error(
                "placeholder_ellipsis",
                f"{class_name}.{method.name} contains '...'",
                relative_path,
            )

        if visitor.loop_nodes:
            self.add_error(
                "python_loop_in_formula",
                f"{class_name}.{method.name} uses explicit Python loops",
                relative_path,
            )

        if visitor.comprehension_nodes:
            self.add_warning(
                "comprehension_in_formula",
                f"{class_name}.{method.name} uses a Python comprehension; verify vectorized OpenFisca idioms are not available",
                relative_path,
            )

        if visitor.if_nodes:
            self.add_warning(
                "if_statement_in_formula",
                f"{class_name}.{method.name} uses Python 'if'; verify vectorized logic or formula versioning would be clearer",
                relative_path,
            )

        for constant in visitor.numeric_constants:
            self.add_error(
                "hardcoded_numeric_value",
                (
                    f"{class_name}.{method.name} uses hardcoded numeric value "
                    f"{constant.value!r} at line {constant.lineno}"
                ),
                relative_path,
            )

    def get_report(self):
        """Print report and return a structured result."""
        print("=" * 60)
        print("CODE VALIDATION REPORT")
        print("=" * 60)
        print()

        if self.info:
            print("📊 Status:\n")
            for item in self.info:
                print(f"   {item}")
            print()

        print(f"📋 Python files checked: {self.files_checked}\n")

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
        print("Usage: uv run python validate_code.py /path/to/openfisca-country-repo")
        print("\nExample:")
        print("  uv run python validate_code.py /home/user/openfisca-tunisia")
        sys.exit(1)

    package_path = Path(sys.argv[1])
    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    validator = CodeValidator(package_path)
    report = validator.validate_all()
    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
