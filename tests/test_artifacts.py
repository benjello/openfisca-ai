"""Tests for artifact planning and materialization."""

from openfisca_ai.core.artifacts import materialize_artifacts, plan_artifact_writes


def test_plan_artifact_writes_reports_create_and_diff_preview(tmp_path):
    artifacts = [
        {
            "kind": "variable",
            "path": "openfisca_demo/variables/example.py",
            "content": "print('hello')\n",
        }
    ]

    plan = plan_artifact_writes(artifacts, tmp_path, strategy="create")

    assert len(plan) == 1
    assert plan[0]["action"] == "create"
    assert plan[0]["will_write"] is True
    assert "--- a/openfisca_demo/variables/example.py" in plan[0]["diff_preview"]
    assert "+++ b/openfisca_demo/variables/example.py" in plan[0]["diff_preview"]


def test_materialize_artifacts_supports_skip_update_and_append_strategies(tmp_path):
    artifacts = [
        {
            "kind": "variable",
            "path": "openfisca_demo/variables/example.py",
            "content": "new_line = 2\n",
        }
    ]
    target = tmp_path / "openfisca_demo/variables/example.py"
    target.parent.mkdir(parents=True)
    target.write_text("existing_line = 1\n", encoding="utf-8")

    skip_plan = plan_artifact_writes(artifacts, tmp_path, strategy="skip")
    assert skip_plan[0]["action"] == "skip"
    assert materialize_artifacts(artifacts, tmp_path, strategy="skip") == []
    assert target.read_text(encoding="utf-8") == "existing_line = 1\n"

    append_plan = plan_artifact_writes(artifacts, tmp_path, strategy="append")
    assert append_plan[0]["action"] == "append"
    append_result = materialize_artifacts(artifacts, tmp_path, strategy="append")
    assert append_result[0]["action"] == "append"
    assert target.read_text(encoding="utf-8") == "existing_line = 1\n\nnew_line = 2\n"

    update_plan = plan_artifact_writes(artifacts, tmp_path, strategy="update")
    assert update_plan[0]["action"] == "update"
    update_result = materialize_artifacts(artifacts, tmp_path, strategy="update")
    assert update_result[0]["action"] == "update"
    assert target.read_text(encoding="utf-8") == "new_line = 2\n"
