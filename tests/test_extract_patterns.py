"""Tests for extract_patterns.py."""

from tests.tool_test_helpers import create_country_repo, load_tool_module, write_file


extract_patterns = load_tool_module("extract_patterns.py", "extract_patterns_tool")


def test_extract_patterns_collects_structure_and_formula_usage(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/income.py",
        """
        from openfisca_core.periods import MONTH, YEAR
        from openfisca_core.variables import Variable
        from numpy import maximum as max_, minimum as min_, where


        class salary(Variable):
            value_type = float
            entity = Person
            definition_period = MONTH
            set_input = set_input_divide_by_period


        class taxable_income(Variable):
            value_type = float
            entity = TaxUnit
            definition_period = YEAR

            def formula(tax_unit, period, parameters):
                salaries = tax_unit.members("salary", period)
                total = tax_unit.sum(salaries)
                floor = parameters(period).taxation.floor
                return max_(total, floor)


        class income_tax(Variable):
            value_type = float
            entity = TaxUnit
            definition_period = YEAR

            def formula(tax_unit, period, parameters):
                taxable_income = tax_unit("taxable_income", period)
                brackets = parameters(period).taxation.income_tax.brackets
                base = brackets.calc(taxable_income)
                return where(taxable_income > 0, min_(base, taxable_income), 0)
        """,
    )
    write_file(
        repo_path / "openfisca_demo/parameters/taxation/floor.yaml",
        """
        description: Minimum floor
        unit: currency
        values:
          2024-01-01: 100
        """,
    )
    write_file(
        repo_path / "openfisca_demo/parameters/taxation/income_tax/brackets.yaml",
        """
        description: Income tax brackets
        metadata:
          threshold_unit: currency
          rate_unit: /1
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0
        """,
    )
    write_file(
        repo_path / "tests/taxation/income_tax.yaml",
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

    extractor = extract_patterns.PatternExtractor(repo_path)
    report = extractor.extract_all()

    assert report["country_package"] == "openfisca_demo"
    assert report["structure"]["has_entities_py"] is True

    variables = report["variables"]
    assert variables["variable_classes"] == 3
    assert variables["formula_variables"] == 2
    assert variables["entities"]["TaxUnit"] == 2
    assert variables["definition_periods"]["YEAR"] == 2
    assert variables["set_input_helpers"]["set_input_divide_by_period"] == 1
    assert variables["formula_patterns"]["uses_parameters"] == 2
    assert variables["formula_patterns"]["uses_members"] == 1
    assert variables["formula_patterns"]["uses_where"] == 1
    assert variables["formula_patterns"]["uses_brackets_calc"] == 1
    assert variables["aggregation_methods"]["sum"] == 1

    parameters = report["parameters"]
    assert parameters["yaml_files"] == 2
    assert parameters["scale_files"] == 1
    assert parameters["top_domains"]["taxation"] == 2
    assert parameters["unit_types"]["currency"] >= 2

    tests = report["tests"]
    assert tests["yaml_tests"] >= 2
    assert tests["python_tests"] == 1
    assert tests["top_domains"]["taxation"] == 1


def test_extract_patterns_accepts_package_directory_input(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/demo.py",
        """
        from openfisca_core.periods import MONTH
        from openfisca_core.variables import Variable


        class demo_variable(Variable):
            value_type = float
            entity = Person
            definition_period = MONTH

            def formula(person, period):
                return person("income", period)
        """,
    )

    extractor = extract_patterns.PatternExtractor(repo_path / "openfisca_demo")
    report = extractor.extract_all()

    assert report["country_package"] == "openfisca_demo"
    assert report["variables"]["formula_variables"] == 1
