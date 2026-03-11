"""Tests for the law_to_code pipeline."""

import pytest
from openfisca_ai.pipelines.law_to_code import run_law_to_code


def test_run_law_to_code_returns_dict():
    """Pipeline returns a dict with extracted and code keys."""
    result = run_law_to_code("Sample law text.")
    assert isinstance(result, dict)
    assert "extracted" in result
    assert "code" in result


def test_run_law_to_code_code_is_string():
    """Generated code is a string."""
    result = run_law_to_code("Article 1 – Some provision.")
    assert isinstance(result["code"], str)


def test_run_law_to_code_with_country_id():
    """Pipeline accepts country_id and use_existing_code_as_reference without crashing."""
    result = run_law_to_code(
        "Sample law.",
        country_id="tunisia",
        use_existing_code_as_reference=False,
    )
    assert "extracted" in result
    assert "code" in result
    assert result.get("country_id") == "tunisia"
