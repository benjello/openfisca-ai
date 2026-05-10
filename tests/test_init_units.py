"""Tests for init_units.py."""

import yaml

from tests.tool_test_helpers import create_country_repo, load_tool_module, write_file


init_units = load_tool_module("init_units.py", "init_units_tool")


def test_init_units_find_package_accepts_repo_and_package_path(tmp_path):
    repo_path = create_country_repo(tmp_path)
    package_path = repo_path / "openfisca_demo"

    assert init_units._find_package_dir(repo_path) == package_path
    assert init_units._find_package_dir(package_path) == package_path


def test_init_units_scan_reads_root_and_scale_units(tmp_path):
    repo_path = create_country_repo(tmp_path)
    package_path = repo_path / "openfisca_demo"
    write_file(
        package_path / "parameters/tax/rate.yaml",
        """
        description: Tax rate
        unit: /1
        values:
          2024-01-01: 0.1
        """,
    )
    write_file(
        package_path / "parameters/tax/income_scale.yaml",
        """
        description: Income tax scale
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

    scanned = init_units.scan_parameters(package_path / "parameters")

    by_file = {entry["path"].name: entry for entry in scanned}
    assert by_file["rate.yaml"]["existing_unit"] == "/1"
    assert by_file["income_scale.yaml"]["existing_unit"] == "currency,/1"
    assert by_file["income_scale.yaml"]["has_brackets"] is True


def test_init_units_apply_writes_unit_to_simple_parameter(tmp_path):
    repo_path = create_country_repo(tmp_path)
    package_path = repo_path / "openfisca_demo"
    parameter_path = package_path / "parameters/benefits/age_minimum.yaml"
    write_file(
        parameter_path,
        """
        description: Minimum age
        values:
          2024-01-01: 18
        """,
    )

    scanned = init_units.scan_parameters(package_path / "parameters")
    changes = init_units.apply_units(scanned, dry_run=False)

    content = yaml.safe_load(parameter_path.read_text(encoding="utf-8"))
    assert changes
    assert content["unit"] == "year"
