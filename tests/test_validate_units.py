"""Tests for validate_units.py."""

from tests.tool_test_helpers import create_package, load_tool_module, write_file


validate_units = load_tool_module("validate_units.py", "validate_units_tool")


def test_validate_units_counts_scale_files_once(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/tax/brackets.yaml",
        """
        description: Tax brackets
        metadata:
          threshold_unit: currency
          rate_unit: /1
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0.1
        """,
    )
    write_file(
        package_path / "parameters/benefits/age_limit.yaml",
        """
        description: Age limit
        unit: year
        values:
          2024-01-01: 18
        """,
    )

    validator = validate_units.UnitsValidator(package_path)

    assert validator.validate() is True
    assert validator.parameter_files_count == 2
    assert len(validator.files_with_units) == 2
    assert validator.files_without_unit == []


def test_validate_units_rejects_scale_without_any_unit_metadata(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/tax/brackets.yaml",
        """
        description: Tax brackets
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0.1
        """,
    )

    validator = validate_units.UnitsValidator(package_path)

    assert validator.validate() is False
    assert "parameters/tax/brackets.yaml" in validator.files_without_unit


def test_validate_units_rejects_undefined_units(tmp_path):
    package_path = create_package(tmp_path)
    write_file(
        package_path / "parameters/benefits/age_limit.yaml",
        """
        description: Age limit
        unit: fortnight
        values:
          2024-01-01: 18
        """,
    )

    validator = validate_units.UnitsValidator(package_path)

    assert validator.validate() is False
    assert "fortnight" in validator.units_used
