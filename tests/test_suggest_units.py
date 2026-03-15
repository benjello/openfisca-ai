"""Tests for suggest_units.py."""

import yaml

from tests.tool_test_helpers import create_package, load_tool_module, write_file


suggest_units = load_tool_module("suggest_units.py", "suggest_units_tool")


def test_suggest_units_apply_adds_simple_unit_without_breaking_yaml(tmp_path):
    package_path = create_package(tmp_path)
    parameter_path = package_path / "parameters/benefits/age_minimum.yaml"
    write_file(
        parameter_path,
        """
        description: Minimum age
        label: Minimum age
        reference:
          - https://example.org/law.pdf#page=4
        values:
          2024-01-01: 18
        """,
    )

    suggester = suggest_units.UnitSuggester(package_path)
    suggester.run(apply=True)

    content = yaml.safe_load(parameter_path.read_text(encoding="utf-8"))
    assert content["unit"] == "year"


def test_suggest_units_apply_adds_scale_units_in_metadata(tmp_path):
    package_path = create_package(tmp_path)
    parameter_path = package_path / "parameters/tax/income_scale.yaml"
    write_file(
        parameter_path,
        """
        description: Income tax scale
        label: Income tax scale
        reference:
          - https://example.org/law.pdf#page=9
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0.1
        """,
    )

    suggester = suggest_units.UnitSuggester(package_path)
    suggester.run(apply=True)

    content = yaml.safe_load(parameter_path.read_text(encoding="utf-8"))
    assert content["metadata"]["threshold_unit"] == "currency"
    assert content["metadata"]["rate_unit"] == "/1"
    assert "unit" not in content


def test_suggest_units_only_fills_missing_scale_unit_keys(tmp_path):
    package_path = create_package(tmp_path)
    parameter_path = package_path / "parameters/tax/income_scale.yaml"
    write_file(
        parameter_path,
        """
        description: Income tax scale
        label: Income tax scale
        reference:
          - https://example.org/law.pdf#page=9
        metadata:
          threshold_unit: currency
        brackets:
          - threshold:
              2024-01-01: 0
            rate:
              2024-01-01: 0.1
        """,
    )

    suggester = suggest_units.UnitSuggester(package_path)
    suggester.run(apply=True)

    content = yaml.safe_load(parameter_path.read_text(encoding="utf-8"))
    assert content["metadata"]["threshold_unit"] == "currency"
    assert content["metadata"]["rate_unit"] == "/1"
