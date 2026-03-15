"""Helpers for tool tests."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_tool_module(filename: str, module_name: str):
    """Load a tool module from the tools/ directory."""
    module_path = REPO_ROOT / "tools" / filename
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_file(path: Path, content: str) -> None:
    """Write a text fixture file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def create_package(tmp_path: Path) -> Path:
    """Create a minimal fake OpenFisca package for tool tests."""
    package_path = tmp_path / "openfisca-demo"
    package_path.mkdir()
    write_file(
        package_path / "units.yaml",
        """
        - name: currency
        - name: /1
        - name: year
        - name: month
        """,
    )
    return package_path


def create_country_repo(tmp_path: Path, module_name: str = "openfisca_demo") -> Path:
    """Create a minimal fake OpenFisca country repository for baseline tests."""
    repo_path = tmp_path / module_name.replace("_", "-")
    package_dir = repo_path / module_name
    package_dir.mkdir(parents=True)

    write_file(package_dir / "__init__.py", "")
    write_file(
        package_dir / "units.yaml",
        """
        - name: currency
        - name: /1
        - name: year
        - name: month
        """,
    )
    write_file(package_dir / "entities.py", "entities = []\n")
    write_file(package_dir / "parameters/index.yaml", "description: Parameters\n")
    write_file(package_dir / "variables/__init__.py", "")
    write_file(repo_path / "tests/demo.yaml", "name: demo\n")

    return repo_path


def create_modern_country_repo(tmp_path: Path, module_name: str = "openfisca_demo") -> Path:
    """Create a coherent fake OpenFisca country repository with modern tooling."""
    repo_path = create_country_repo(tmp_path, module_name=module_name)
    project_name = module_name.replace("_", "-")

    write_file(
        repo_path / "pyproject.toml",
        f"""
        [project]
        name = "{project_name}"
        dependencies = ["openfisca-core[web-api]>=44,<45"]
        """,
    )
    write_file(repo_path / "uv.lock", "version = 1\n")
    write_file(repo_path / f"{module_name}/reforms/__init__.py", "")
    write_file(repo_path / f"{module_name}/situation_examples/example.json", "{}\n")
    write_file(
        repo_path / f"{module_name}/variables/income_tax.py",
        """
        from openfisca_core.periods import YEAR
        from openfisca_core.variables import Variable
        from numpy import where


        class income_tax(Variable):
            value_type = float
            entity = TaxUnit
            definition_period = YEAR

            def formula(tax_unit, period, parameters):
                taxable_income = tax_unit("taxable_income", period)
                rate = parameters(period).taxation.income_tax.rate
                return where(taxable_income > 0, taxable_income * rate, 0)
        """,
    )
    write_file(
        repo_path / f"{module_name}/parameters/taxation/income_tax/rate.yaml",
        """
        description: Income tax rate
        label: Income tax rate
        reference: Tax code, article 1
        unit: /1
        values:
          2024-01-01: 0.1
        """,
    )
    write_file(
        repo_path / "tests/income_tax.yaml",
        """
        - name: income tax
          output:
            income_tax: 10
        """,
    )
    write_file(
        repo_path / "tests/test_income_tax.py",
        """
        def test_income_tax_smoke():
            assert "income_tax"
        """,
    )
    write_file(
        repo_path / "Makefile",
        f"""
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
        	$(UV) openfisca test --country-package {module_name} tests
        """,
    )
    write_file(
        repo_path / ".github/workflows/ci.yml",
        f"""
        name: CI

        on: [push, pull_request]

        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - run: uv sync --extra dev
              - run: uv run openfisca test --country-package {module_name} tests
              - run: uv run yamllint {module_name}/parameters tests
        """,
    )

    return repo_path
