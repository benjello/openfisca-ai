"""Tests for validate_parameters.py."""

from tests.tool_test_helpers import create_package, load_tool_module, write_file


validate_parameters = load_tool_module("validate_parameters.py", "validate_parameters_tool")


def test_validate_parameters_accepts_scale_units_and_metadata_reference(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/tax/brackets.yaml",
        """
        description: Tax brackets
        label: Tax brackets
        metadata:
          reference:
            - https://example.org/law.pdf#page=10
          threshold_unit: currency
          rate_unit: /1
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0.1
        """,
    )

    report = validate_parameters.ParameterValidator(package_path).validate_all()

    assert report["valid"] is True
    assert report["errors"] == []


def test_validate_parameters_reports_missing_scale_unit_metadata(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/tax/brackets.yaml",
        """
        description: Tax brackets
        label: Tax brackets
        reference:
          - https://example.org/law.pdf#page=10
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0.1
        """,
    )

    report = validate_parameters.ParameterValidator(package_path).validate_all()

    assert report["valid"] is False
    assert any(
        error["type"] == "missing_unit" and error["parameter_type"] == "scale"
        for error in report["errors"]
    )


def test_validate_parameters_checks_metadata_reference_pdf_page_numbers(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/benefits/age_limit.yaml",
        """
        description: Age limit
        label: Age limit
        unit: year
        metadata:
          reference:
            - https://example.org/law.pdf
        values:
          2024-01-01: 18
        """,
    )

    report = validate_parameters.ParameterValidator(package_path).validate_all()

    assert report["valid"] is True
    assert any(warning["type"] == "missing_page_number" for warning in report["warnings"])


def test_validate_parameters_reports_undefined_units_with_file_context(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/benefits/age_limit.yaml",
        """
        description: Age limit
        label: Age limit
        reference:
          - https://example.org/law.pdf#page=1
        unit: fortnight
        values:
          2024-01-01: 18
        """,
    )

    report = validate_parameters.ParameterValidator(package_path).validate_all()

    assert report["valid"] is False
    assert any(
        error["type"] == "undefined_unit" and "parameters/benefits/age_limit.yaml" in error["file"]
        for error in report["errors"]
    )
