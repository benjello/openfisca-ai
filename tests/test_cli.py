"""Tests for the openfisca-ai CLI."""

import json

from openfisca_ai import cli
from tests.tool_test_helpers import create_country_repo, create_modern_country_repo, write_file


def test_cli_without_args_prints_usage(capsys):
    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Usage:" in captured.err


def test_cli_run_task_outputs_json(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {"law_text": "Article 1"},
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert "extracted" in payload
    assert "code" in payload
    assert "artifacts" in payload


def test_cli_scaffold_task_outputs_json(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["scaffold", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["artifacts"][0]["kind"] == "variable"
    assert "written_artifacts" not in payload


def test_cli_audit_command_runs_successfully(tmp_path, capsys):
    repo_path = create_modern_country_repo(tmp_path)

    exit_code = cli.main(["audit", str(repo_path), "--markdown"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# OpenFisca AI Audit" in captured.out


def test_cli_check_all_command_runs_successfully(tmp_path, capsys):
    repo_path = create_modern_country_repo(tmp_path)

    exit_code = cli.main(["check-all", str(repo_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "OPENFISCA AI AUDIT" in captured.out


def test_cli_validate_code_propagates_failure(tmp_path, capsys):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "openfisca_demo/variables/bad.py",
        """
        from openfisca_core.variables import Variable


        class bad_variable(Variable):
            value_type = float

            def formula(person, period):
                return 2
        """,
    )

    exit_code = cli.main(["validate-code", str(repo_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "CODE VALIDATION REPORT" in captured.out


def test_cli_run_task_includes_reference_package_analysis(tmp_path, capsys, monkeypatch):
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
    task_path = project_root / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "country": "demo",
                "pipeline": "law_to_code",
                "inputs": {"law_text": "Article 1"},
                "options": {
                    "use_existing_code_as_reference": True,
                    "include_reference_audit_summary": True,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["reference_code_path"] == str(repo_path.resolve())
    assert payload["reference_package_analysis"]["pattern_summary"]["country_package"] == "openfisca_demo"
    assert payload["reference_package_analysis"]["audit_summary"]["all_checks_passed"] is True
    assert payload["implementation_brief"]["mode"] == "reference-guided"


def test_cli_run_task_generates_scaffolding_from_extracted_input(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["artifacts"][0]["kind"] == "variable"
    assert payload["artifacts"][0]["path"] == "openfisca_<country>/variables/income_tax_credit.py"
    assert payload["artifacts"][1]["kind"] == "parameter"
    assert payload["artifacts"][2]["kind"] == "yaml_test_template"


def test_cli_run_task_can_write_artifacts_to_output_dir(tmp_path, capsys):
    task_dir = tmp_path / "tasks"
    task_dir.mkdir()
    task_path = task_dir / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "output_dir": "../generated",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    generated_dir = (task_dir / "../generated").resolve()
    assert exit_code == 0
    assert payload["artifacts_output_dir"] == str(generated_dir)
    assert payload["artifact_write_plan"][0]["action"] == "create"
    assert len(payload["written_artifacts"]) == 2
    assert (generated_dir / "openfisca_<country>/variables/income_tax_credit.py").exists()
    assert (generated_dir / "tests/income_tax_credit.yaml").exists()


def test_cli_scaffold_with_output_dir_keeps_plan_only_default(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "output_dir": "generated",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["scaffold", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["artifact_write_plan"][0]["action"] == "create"
    assert "written_artifacts" not in payload
    assert not ((tmp_path / "generated") / "openfisca_<country>/variables/income_tax_credit.py").exists()


def test_cli_scaffold_apply_writes_output_dir(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "output_dir": "generated",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["scaffold-apply", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert len(payload["written_artifacts"]) == 2
    assert ((tmp_path / "generated") / "openfisca_<country>/variables/income_tax_credit.py").exists()


def test_cli_scaffold_apply_defaults_to_reference_package_when_country_is_configured(
    tmp_path,
    capsys,
    monkeypatch,
):
    project_root = tmp_path / "project"
    task_dir = project_root / "tasks"
    task_dir.mkdir(parents=True)
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
    task_path = task_dir / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "country": "demo",
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
                        "variables": [
                            {
                                "name": "income_tax_bonus",
                                "entity": "TaxUnit",
                                "definition_period": "YEAR",
                                "value_type": "float",
                                "domain": "taxation",
                                "base_variable": "taxable_income",
                                "parameter": "taxation.income_tax.bonus_rate",
                            }
                        ]
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    exit_code = cli.main(["scaffold-apply", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["reference_package_write_root"] == str(repo_path.resolve())
    assert (repo_path / "openfisca_demo/variables/taxation/income_tax_bonus.py").exists()


def test_cli_scaffold_apply_requires_explicit_destination(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
                        "variables": [
                            {
                                "name": "income_tax_credit",
                                "entity": "TaxUnit",
                                "definition_period": "YEAR",
                                "value_type": "float",
                            }
                        ]
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["scaffold-apply", str(task_path)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "scaffold-apply requires either options.output_dir or a configured country reference package." in captured.err


def test_cli_scaffold_can_write_markdown_report(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "output_dir": "generated",
                    "plan_only": True,
                    "report_path": "reports/scaffold.md",
                    "report_format": "markdown",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["scaffold", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    report_path = tmp_path / "reports/scaffold.md"
    assert exit_code == 0
    assert payload["report_path"] == str(report_path.resolve())
    assert payload["report_format"] == "markdown"
    assert report_path.exists()
    assert "# OpenFisca AI Scaffold Report" in report_path.read_text(encoding="utf-8")


def test_cli_run_task_can_append_to_existing_output_artifact(tmp_path, capsys):
    generated_dir = tmp_path / "generated"
    existing_file = generated_dir / "openfisca_<country>/variables/income_tax_credit.py"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_text("existing_line = 1\n", encoding="utf-8")
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "output_dir": "generated",
                    "existing_artifact_strategy": "append",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["artifact_write_plan"][0]["action"] == "append"
    assert payload["written_artifacts"][0]["action"] == "append"
    assert "existing_line = 1" in existing_file.read_text(encoding="utf-8")
    assert "class income_tax_credit(Variable):" in existing_file.read_text(encoding="utf-8")


def test_cli_run_task_plan_only_returns_plan_without_writing(tmp_path, capsys):
    task_path = tmp_path / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "output_dir": "generated",
                    "plan_only": True,
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    generated_dir = (tmp_path / "generated").resolve()
    assert exit_code == 0
    assert payload["artifact_write_plan"][0]["action"] == "create"
    assert "written_artifacts" not in payload
    assert not (generated_dir / "openfisca_<country>/variables/income_tax_credit.py").exists()


def test_cli_run_task_can_apply_artifacts_to_reference_package(tmp_path, capsys, monkeypatch):
    project_root = tmp_path / "project"
    task_dir = project_root / "tasks"
    task_dir.mkdir(parents=True)
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
    task_path = task_dir / "task.json"
    task_path.write_text(
        json.dumps(
            {
                "country": "demo",
                "pipeline": "law_to_code",
                "inputs": {
                    "law_text": "Article 1",
                    "extracted": {
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
                },
                "options": {
                    "use_existing_code_as_reference": True,
                    "apply_artifacts_to_reference_package": True,
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(project_root))

    exit_code = cli.main(["run", str(task_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["reference_package_write_root"] == str(repo_path.resolve())
    assert (repo_path / "openfisca_demo/variables/taxation/income_tax_surcharge.py").exists()
    assert (repo_path / "tests/taxation/income_tax_surcharge.yaml").exists()
