"""Tests for validate_code.py."""

from tests.tool_test_helpers import create_country_repo, load_tool_module, write_file


validate_code = load_tool_module("validate_code.py", "validate_code_tool")


def test_validate_code_passes_for_clean_openfisca_variable(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/benefits.py",
        """
        from openfisca_core.periods import MONTH
        from openfisca_core.variables import Variable
        from numpy import where


        class housing_allowance(Variable):
            value_type = float
            entity = Family
            definition_period = MONTH

            def formula(family, period, parameters):
                base_amount = parameters(period).benefits.housing_allowance.amount
                eligible = family("is_eligible", period)
                return where(eligible, base_amount, 0)
        """,
    )

    validator = validate_code.CodeValidator(repo_path)
    report = validator.validate_all()

    assert report["valid"] is True
    assert report["errors"] == []
    assert report["warnings"] == []


def test_validate_code_reports_missing_metadata_placeholders_and_hardcodes(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/bad_variable.py",
        """
        from openfisca_core.variables import Variable


        class bad_allowance(Variable):
            value_type = float

            def formula(person, period):
                # TODO: replace with parameter
                total = 0
                for amount in [1, 2]:
                    total += amount
                if person("age", period) > 18:
                    return ...
                return total + 3
        """,
    )

    validator = validate_code.CodeValidator(repo_path)
    report = validator.validate_all()

    assert report["valid"] is False
    error_types = {error["type"] for error in report["errors"]}
    assert "missing_entity" in error_types
    assert "missing_definition_period" in error_types
    assert "todo_comment" in error_types
    assert "python_loop_in_formula" in error_types
    assert "placeholder_ellipsis" in error_types
    assert "hardcoded_numeric_value" in error_types

    warning_types = {warning["type"] for warning in report["warnings"]}
    assert "if_statement_in_formula" in warning_types


def test_validate_code_warns_for_if_statement_without_failing(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/warn_only.py",
        """
        from openfisca_core.periods import MONTH
        from openfisca_core.variables import Variable


        class taxable_income(Variable):
            value_type = float
            entity = Person
            definition_period = MONTH

            def formula(person, period):
                income = person("income", period)
                eligible = person("eligible", period)
                if eligible is None:
                    return 0
                return income
        """,
    )

    validator = validate_code.CodeValidator(repo_path)
    report = validator.validate_all()

    assert report["valid"] is True
    assert report["errors"] == []
    assert any(warning["type"] == "if_statement_in_formula" for warning in report["warnings"])
