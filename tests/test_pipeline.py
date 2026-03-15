"""Tests for the law_to_code pipeline."""

import pytest

from openfisca_ai.pipelines.law_to_code import run_law_to_code
from tests.tool_test_helpers import create_modern_country_repo, write_file


def test_run_law_to_code_returns_dict():
    """Pipeline returns a dict with extracted and code keys."""
    result = run_law_to_code("Sample law text.")
    assert isinstance(result, dict)
    assert "extracted" in result
    assert "code" in result
    assert "implementation_brief" in result
    assert "artifacts" in result


def test_run_law_to_code_code_is_string():
    """Generated code is a string."""
    result = run_law_to_code("Article 1 – Some provision.")
    assert isinstance(result["code"], str)
    assert result["implementation_brief"]["mode"] == "generic"
    assert result["implementation_brief"]["configured_conventions"]["naming"] == "snake_case"
    assert isinstance(result["artifacts"], list)


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


def test_run_law_to_code_includes_reference_package_analysis(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    repo_path = create_modern_country_repo(tmp_path / "fixtures")

    write_file(
        project_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        """,
    )
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    result = run_law_to_code(
        "Article 1 – Some provision.",
        country_id="demo",
        use_existing_code_as_reference=True,
    )

    assert result["reference_code_path"] == str(repo_path.resolve())
    assert result["reference_package_analysis"]["package_path"] == str(repo_path.resolve())
    assert result["reference_package_analysis"]["pattern_summary"]["country_package"] == "openfisca_demo"
    assert result["reference_package_analysis"]["pattern_summary"]["entities"] == {"TaxUnit": 1}
    assert result["implementation_brief"]["mode"] == "reference-guided"
    assert result["implementation_brief"]["observed_package_patterns"]["entities"] == ["TaxUnit"]
    assert result["implementation_brief"]["observed_package_patterns"]["formula_helpers"] == [
        "parameters(...)",
        "where",
    ]
    assert result["implementation_brief"]["scaffolding"]["variable_root"] == "openfisca_demo/variables"


def test_run_law_to_code_can_include_reference_audit_summary(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    create_modern_country_repo(tmp_path / "fixtures")

    write_file(
        project_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        """,
    )
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    result = run_law_to_code(
        "Article 1 – Some provision.",
        country_id="demo",
        use_existing_code_as_reference=True,
        include_reference_audit_summary=True,
    )

    assert result["reference_package_analysis"]["audit_summary"]["all_checks_passed"] is True
    assert result["reference_package_analysis"]["audit_summary"]["country_package"] == "openfisca_demo"
    assert result["implementation_brief"]["test_strategy"]["prefer_yaml_tests"] is True


def test_run_law_to_code_generates_scaffolding_from_extracted_input(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    create_modern_country_repo(tmp_path / "fixtures")

    write_file(
        project_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        conventions:
          entity_levels: [Person, TaxUnit]
          parameter_hierarchy: [taxation]
        """,
    )
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    result = run_law_to_code(
        "Article 1 – Some provision.",
        country_id="demo",
        use_existing_code_as_reference=True,
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_credit",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "domain": "taxation",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.credit_rate",
                }
            ],
            "parameters": [
                {
                    "name": "taxation.income_tax.credit_rate",
                    "label": "Income tax credit rate",
                    "description": "Rate applied to taxable income.",
                    "unit": "/1",
                    "value": 0.1,
                    "reference": ["Tax code article 1"],
                }
            ],
        },
    )

    assert result["code"].startswith("from openfisca_core.periods import YEAR")
    assert [artifact["kind"] for artifact in result["artifacts"]] == [
        "variable",
        "parameter",
        "yaml_test_template",
    ]
    assert result["artifacts"][0]["path"] == "openfisca_demo/variables/taxation/income_tax_credit.py"
    assert result["artifacts"][1]["path"] == "openfisca_demo/parameters/taxation/income_tax/credit_rate.yaml"
    assert result["artifacts"][2]["path"] == "tests/taxation/income_tax_credit.yaml"
    assert result["notes"] == [
        "No explicit tests were provided in `inputs.extracted.tests`; generated commented YAML test templates instead."
    ]


def test_run_law_to_code_can_write_artifacts_to_output_dir(tmp_path):
    output_dir = tmp_path / "generated"

    result = run_law_to_code(
        "Article 1 – Some provision.",
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_credit",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.credit_rate",
                }
            ],
            "parameters": [
                {
                    "name": "taxation.income_tax.credit_rate",
                    "label": "Income tax credit rate",
                    "description": "Rate applied to taxable income.",
                    "unit": "/1",
                    "value": 0.1,
                }
            ],
        },
        artifacts_output_dir=str(output_dir),
    )

    assert result["artifacts_output_dir"] == str(output_dir)
    assert result["artifact_write_plan"][0]["action"] == "create"
    assert len(result["written_artifacts"]) == 3
    assert (output_dir / "openfisca_<country>/variables/income_tax_credit.py").exists()
    assert (output_dir / "openfisca_<country>/parameters/taxation/income_tax/credit_rate.yaml").exists()
    assert (output_dir / "tests/income_tax_credit.yaml").exists()
    assert "class income_tax_credit(Variable):" in (
        output_dir / "openfisca_<country>/variables/income_tax_credit.py"
    ).read_text(encoding="utf-8")


def test_run_law_to_code_can_apply_artifacts_to_reference_package(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    repo_path = create_modern_country_repo(tmp_path / "fixtures")

    write_file(
        project_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        """,
    )
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    result = run_law_to_code(
        "Article 1 – Some provision.",
        country_id="demo",
        use_existing_code_as_reference=True,
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_surcharge",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "domain": "taxation",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.surcharge_rate",
                }
            ],
            "parameters": [
                {
                    "name": "taxation.income_tax.surcharge_rate",
                    "label": "Income tax surcharge rate",
                    "description": "Extra rate applied to taxable income.",
                    "unit": "/1",
                    "value": 0.02,
                }
            ],
        },
        apply_artifacts_to_reference_package=True,
    )

    assert result["reference_package_write_root"] == str(repo_path.resolve())
    assert len(result["written_artifacts"]) == 3
    assert (repo_path / "openfisca_demo/variables/taxation/income_tax_surcharge.py").exists()
    assert (repo_path / "openfisca_demo/parameters/taxation/income_tax/surcharge_rate.yaml").exists()
    assert (repo_path / "tests/taxation/income_tax_surcharge.yaml").exists()


def test_run_law_to_code_refuses_to_overwrite_reference_package_artifacts(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    create_modern_country_repo(tmp_path / "fixtures")

    write_file(
        project_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        """,
    )
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    with pytest.raises(FileExistsError):
        run_law_to_code(
            "Article 1 – Some provision.",
            country_id="demo",
            use_existing_code_as_reference=True,
            extracted_data={
                "variables": [
                    {
                        "name": "income_tax",
                        "entity": "TaxUnit",
                        "definition_period": "YEAR",
                        "value_type": "float",
                        "base_variable": "taxable_income",
                        "parameter": "taxation.income_tax.rate",
                    }
                ]
            },
            apply_artifacts_to_reference_package=True,
        )


def test_run_law_to_code_can_skip_existing_output_artifacts(tmp_path):
    output_dir = tmp_path / "generated"
    existing_file = output_dir / "openfisca_<country>/variables/income_tax_credit.py"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_text("existing_line = 1\n", encoding="utf-8")

    result = run_law_to_code(
        "Article 1 – Some provision.",
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_credit",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.credit_rate",
                }
            ]
        },
        artifacts_output_dir=str(output_dir),
        existing_artifact_strategy="skip",
    )

    assert result["artifact_write_plan"][0]["action"] == "skip"
    assert len(result["written_artifacts"]) == 1
    assert result["written_artifacts"][0]["path"] == "tests/income_tax_credit.yaml"
    assert existing_file.read_text(encoding="utf-8") == "existing_line = 1\n"


def test_run_law_to_code_can_update_existing_output_artifacts(tmp_path):
    output_dir = tmp_path / "generated"
    existing_file = output_dir / "openfisca_<country>/variables/income_tax_credit.py"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_text("existing_line = 1\n", encoding="utf-8")

    result = run_law_to_code(
        "Article 1 – Some provision.",
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_credit",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.credit_rate",
                }
            ]
        },
        artifacts_output_dir=str(output_dir),
        existing_artifact_strategy="update",
    )

    assert result["artifact_write_plan"][0]["action"] == "update"
    assert result["written_artifacts"][0]["action"] == "update"
    assert existing_file.read_text(encoding="utf-8").startswith("from openfisca_core.periods import YEAR")


def test_run_law_to_code_plan_only_does_not_write_output_artifacts(tmp_path):
    output_dir = tmp_path / "generated"

    result = run_law_to_code(
        "Article 1 – Some provision.",
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_credit",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.credit_rate",
                }
            ]
        },
        artifacts_output_dir=str(output_dir),
        plan_only=True,
    )

    assert result["artifact_write_plan"][0]["action"] == "create"
    assert "written_artifacts" not in result
    assert not (output_dir / "openfisca_<country>/variables/income_tax_credit.py").exists()


def test_run_law_to_code_plan_only_does_not_write_reference_package(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    repo_path = create_modern_country_repo(tmp_path / "fixtures")

    write_file(
        project_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        """,
    )
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    result = run_law_to_code(
        "Article 1 – Some provision.",
        country_id="demo",
        use_existing_code_as_reference=True,
        extracted_data={
            "variables": [
                {
                    "name": "income_tax_surcharge",
                    "entity": "TaxUnit",
                    "definition_period": "YEAR",
                    "value_type": "float",
                    "domain": "taxation",
                    "base_variable": "taxable_income",
                    "parameter": "taxation.income_tax.surcharge_rate",
                }
            ]
        },
        apply_artifacts_to_reference_package=True,
        plan_only=True,
    )

    assert result["artifact_write_plan"][0]["action"] == "create"
    assert "written_artifacts" not in result
    assert not (repo_path / "openfisca_demo/variables/taxation/income_tax_surcharge.py").exists()
