"""Tests for modernization detection and planning."""

from openfisca_ai.modernize import build_modernization_plan, detect_modernization_state
from tests.tool_test_helpers import create_country_repo, write_file


def test_modernize_detect_openfisca_package_state(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(repo_path / "pyproject.toml", "[project]\nname = 'openfisca-demo'\n")
    write_file(repo_path / "uv.lock", "version = 1\n")

    state = detect_modernization_state(repo_path)

    assert state["repo_type"] == "openfisca-package"
    assert state["packaging"] == "pyproject-project"
    assert state["environment_manager"] == "uv"


def test_modernize_plan_proposes_missing_tools(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(repo_path / "setup.py", "setup(name='openfisca-demo')\n")

    plan = build_modernization_plan(repo_path)
    step_ids = [step["id"] for step in plan["steps"]]
    proposed = {step["id"] for step in plan["steps"] if step["status"] == "propose"}

    assert step_ids[0] == "first-pass-validation"
    assert step_ids[1] == "resolve-detected-errors"
    assert "validate-parameters" in "\n".join(plan["steps"][0]["suggested_commands"])
    assert "uv run openfisca test --country-package openfisca_demo tests" in plan["steps"][0]["suggested_commands"]
    assert plan["steps"][1]["status"] == "conditional"
    assert "agent_prompt" in plan["steps"][1]
    assert "packaging" in step_ids
    assert "environment" in proposed
    assert "formatter" in proposed
    assert "openfisca-ai-tools" in proposed
    assert plan["notes"] == [
        "This plan is proposal-only and does not modify files.",
        "Apply steps one by one after human or agent review.",
    ]


def test_modernize_plan_keeps_existing_canonical_choices(tmp_path):
    repo_path = create_country_repo(tmp_path)
    write_file(
        repo_path / "pyproject.toml",
        """
        [project]
        name = "openfisca-demo"

        [tool.ruff]
        line-length = 100
        """,
    )
    write_file(repo_path / "uv.lock", "version = 1\n")

    plan = build_modernization_plan(repo_path)
    statuses = {step["id"]: step["status"] for step in plan["steps"]}

    assert statuses["first-pass-validation"] == "recommended"
    assert statuses["resolve-detected-errors"] == "conditional"
    assert statuses["packaging"] == "ok"
    assert statuses["environment"] == "ok"
    assert statuses["formatter"] == "ok"
