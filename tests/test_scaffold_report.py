"""Tests for human-readable scaffold reports."""

from openfisca_ai.core.scaffold_report import (
    render_scaffold_report_markdown,
    render_scaffold_report_text,
)


def build_sample_result():
    return {
        "country_id": "demo",
        "implementation_brief": {
            "mode": "reference-guided",
            "country_package": "openfisca_demo",
            "scaffolding": {
                "variable_root": "openfisca_demo/variables",
                "parameter_root": "openfisca_demo/parameters",
                "tests_root": "tests",
            },
            "observed_package_patterns": {
                "entities": ["TaxUnit"],
                "definition_periods": ["YEAR"],
                "formula_helpers": ["parameters(...)", "where"],
                "variable_domains": ["taxation"],
                "parameter_domains": ["taxation"],
                "unit_types": ["/1"],
            },
        },
        "artifacts": [
            {
                "kind": "variable",
                "path": "openfisca_demo/variables/taxation/income_tax_credit.py",
            }
        ],
        "notes": ["No explicit tests were provided."],
        "artifact_write_plan": [
            {
                "kind": "variable",
                "path": "openfisca_demo/variables/taxation/income_tax_credit.py",
                "exists": False,
                "action": "create",
                "diff_preview": "--- a/example\n+++ b/example",
            }
        ],
    }


def test_render_scaffold_report_markdown_contains_key_sections():
    rendered = render_scaffold_report_markdown(build_sample_result())

    assert "# OpenFisca AI Scaffold Report" in rendered
    assert "## Scaffolding Targets" in rendered
    assert "## Observed Patterns" in rendered
    assert "## Write Plan" in rendered
    assert "```diff" in rendered


def test_render_scaffold_report_text_contains_summary_lines():
    rendered = render_scaffold_report_text(build_sample_result())

    assert "OPENFISCA AI SCAFFOLD REPORT" in rendered
    assert "country: demo" in rendered
    assert "write_actions:" in rendered
    assert "- create variable openfisca_demo/variables/taxation/income_tax_credit.py" in rendered
