"""Tests for validate_tests.py."""

from tests.tool_test_helpers import create_country_repo, load_tool_module, write_file


validate_tests = load_tool_module("validate_tests.py", "validate_tests_tool")


def test_validate_tests_passes_when_formula_variables_are_covered(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/benefits.py",
        """
        from openfisca_core.periods import MONTH
        from openfisca_core.variables import Variable


        class housing_allowance(Variable):
            value_type = float
            entity = Family
            definition_period = MONTH

            def formula(family, period, parameters):
                return family("income", period)
        """,
    )
    write_file(
        repo_path / "tests/housing_allowance.yaml",
        """
        - name: housing allowance
          output:
            housing_allowance: 100
        """,
    )
    write_file(
        repo_path / "tests/test_housing_allowance.py",
        """
        def test_housing_allowance_smoke():
            assert "housing_allowance"
        """,
    )

    validator = validate_tests.TestValidator(repo_path)
    report = validator.validate_all()

    assert report["valid"] is True
    assert report["errors"] == []


def test_validate_tests_fails_when_formula_variable_has_no_matching_test(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/benefits.py",
        """
        from openfisca_core.periods import MONTH
        from openfisca_core.variables import Variable


        class child_allowance(Variable):
            value_type = float
            entity = Family
            definition_period = MONTH

            def formula(family, period, parameters):
                return family("income", period)
        """,
    )
    write_file(
        repo_path / "tests/other_variable.yaml",
        """
        - name: other output
          output:
            housing_allowance: 100
        """,
    )

    validator = validate_tests.TestValidator(repo_path)
    report = validator.validate_all()

    assert report["valid"] is False
    assert any(error["type"] == "untested_formula_variable" for error in report["errors"])


def test_validate_tests_warns_when_yaml_or_python_layer_is_missing(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/income.py",
        """
        from openfisca_core.periods import MONTH
        from openfisca_core.variables import Variable


        class taxable_income(Variable):
            value_type = float
            entity = Person
            definition_period = MONTH

            def formula(person, period):
                return person("income", period)
        """,
    )
    (repo_path / "tests" / "demo.yaml").unlink()
    write_file(
        repo_path / "tests/test_taxable_income.py",
        """
        def test_taxable_income():
            assert "taxable_income"
        """,
    )

    validator = validate_tests.TestValidator(repo_path)
    report = validator.validate_all()

    assert report["valid"] is True
    assert report["errors"] == []
    assert any(warning["type"] == "missing_yaml_tests" for warning in report["warnings"])
