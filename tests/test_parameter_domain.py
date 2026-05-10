"""Tests for shared parameter and unit helpers."""

from openfisca_ai.domain.parameters import (
    get_declared_units,
    get_metadata,
    get_reference_entries,
    is_scale_parameter,
)
from openfisca_ai.domain.units import extract_unit_names, usual_unit_definitions


def test_parameter_helpers_read_root_metadata():
    content = {
        "description": "Rate",
        "unit": "/1",
        "reference": {"tax_code": ["Article 1", {"href": "https://example.test"}]},
    }

    assert get_metadata(content) == {}
    assert not is_scale_parameter(content)
    assert get_declared_units(content) == ["/1"]
    assert get_reference_entries(content) == ["Article 1", {"href": "https://example.test"}]


def test_parameter_helpers_read_scale_units_from_metadata():
    content = {
        "brackets": [],
        "metadata": {
            "threshold_unit": "currency",
            "rate_unit": "/1",
            "reference": "Law, article 2",
        },
    }

    assert get_metadata(content)["threshold_unit"] == "currency"
    assert is_scale_parameter(content)
    assert get_declared_units(content) == ["currency", "/1"]
    assert get_reference_entries(content) == ["Law, article 2"]


def test_extract_unit_names_ignores_invalid_entries():
    units = [
        {"name": "currency"},
        {"label": "missing name"},
        "not a mapping",
        {"name": "/1"},
    ]

    assert extract_unit_names(units) == {"currency", "/1"}


def test_usual_unit_definitions_can_be_filtered():
    units = usual_unit_definitions({"currency/kg", "kWh", "unknown"})

    assert [unit["name"] for unit in units] == ["kWh", "currency/kg"]
