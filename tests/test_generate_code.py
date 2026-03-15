"""Tests for structured scaffolding generation."""

from openfisca_ai.skills.generate_code import generate_scaffolding


def test_generate_scaffolding_creates_variable_parameter_and_test_artifacts():
    extracted = {
        "variables": [
            {
                "name": "income_tax_credit",
                "entity": "TaxUnit",
                "definition_period": "YEAR",
                "value_type": "float",
                "label": "Income tax credit",
                "domain": "taxation",
                "base_variable": "taxable_income",
                "parameter": "taxation.income_tax.credit_rate",
                "reference": "Tax code article 1",
            }
        ],
        "parameters": [
            {
                "name": "taxation.income_tax.credit_rate",
                "label": "Income tax credit rate",
                "description": "Rate applied to taxable income.",
                "unit": "/1",
                "value": 0.1,
                "effective_date": "2024-01-01",
                "reference": ["Tax code article 1"],
            }
        ],
        "tests": [
            {
                "name": "income tax credit basic case",
                "period": 2024,
                "input": {
                    "taxable_income": 1000,
                },
                "output": {
                    "income_tax_credit": 100,
                },
            }
        ],
    }
    implementation_brief = {
        "scaffolding": {
            "variable_root": "openfisca_demo/variables",
            "parameter_root": "openfisca_demo/parameters",
            "tests_root": "tests",
        }
    }

    result = generate_scaffolding(extracted, implementation_brief=implementation_brief)

    artifacts = result["artifacts"]
    assert [artifact["kind"] for artifact in artifacts] == ["variable", "parameter", "yaml_test"]
    assert artifacts[0]["path"] == "openfisca_demo/variables/taxation/income_tax_credit.py"
    assert 'class income_tax_credit(Variable):' in artifacts[0]["content"]
    assert 'taxable_income = tax_unit("taxable_income", period)' in artifacts[0]["content"]
    assert "return taxable_income * credit_rate" in artifacts[0]["content"]
    assert artifacts[1]["path"] == "openfisca_demo/parameters/taxation/income_tax/credit_rate.yaml"
    assert "unit: /1" in artifacts[1]["content"]
    assert artifacts[2]["path"] == "tests/taxation/income_tax_credit.yaml"
    assert "income tax credit basic case" in artifacts[2]["content"]
    assert result["notes"] == []


def test_generate_scaffolding_creates_test_templates_when_no_explicit_tests():
    extracted = {
        "variables": [
            {
                "name": "housing_allowance",
                "entity": "Household",
                "definition_period": "MONTH",
                "value_type": "float",
                "domain": "benefits",
            }
        ]
    }
    implementation_brief = {
        "scaffolding": {
            "variable_root": "openfisca_demo/variables",
            "parameter_root": "openfisca_demo/parameters",
            "tests_root": "tests",
        }
    }

    result = generate_scaffolding(extracted, implementation_brief=implementation_brief)

    assert result["artifacts"][0]["kind"] == "variable"
    assert result["artifacts"][1]["kind"] == "yaml_test_template"
    assert result["artifacts"][1]["path"] == "tests/benefits/housing_allowance.yaml"
    assert "TODO: replace this scaffold" in result["artifacts"][1]["content"]
    assert result["notes"] == [
        "No explicit tests were provided in `inputs.extracted.tests`; generated commented YAML test templates instead."
    ]
