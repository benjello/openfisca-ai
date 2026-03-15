"""Tests for audit_country_package.py."""

from tests.tool_test_helpers import (
    create_country_repo,
    create_modern_country_repo,
    load_tool_module,
    write_file,
)


audit_country_package = load_tool_module(
    "audit_country_package.py",
    "audit_country_package_tool",
)

def test_audit_country_package_aggregates_all_checks(tmp_path):
    repo_path = create_modern_country_repo(tmp_path)
    auditor = audit_country_package.CountryPackageAuditor(repo_path)

    report = auditor.audit()

    assert report["summary"]["all_checks_passed"] is True
    assert report["summary"]["failing_checks"] == []
    assert report["checks"]["baseline"]["valid"] is True
    assert report["checks"]["tooling"]["valid"] is True
    assert report["checks"]["units"]["valid"] is True
    assert report["checks"]["parameters"]["valid"] is True
    assert report["checks"]["code"]["valid"] is True
    assert report["checks"]["tests"]["valid"] is True
    assert report["checks"]["patterns"]["report"]["country_package"] == "openfisca_demo"


def test_audit_country_package_reports_failing_checks(tmp_path):
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
    write_file(
        repo_path / "pyproject.toml",
        """
        [project]
        name = "OpenFisca-Demo"
        dependencies = ["openfisca-core[web-api]>=44,<45"]
        """,
    )

    auditor = audit_country_package.CountryPackageAuditor(repo_path)
    report = auditor.audit()

    assert report["summary"]["all_checks_passed"] is False
    assert "code" in report["summary"]["failing_checks"]
    assert "tests" in report["summary"]["failing_checks"]


def test_audit_country_package_markdown_renderer_contains_key_sections(tmp_path):
    repo_path = create_modern_country_repo(tmp_path)
    auditor = audit_country_package.CountryPackageAuditor(repo_path)
    report = auditor.audit()

    rendered = audit_country_package.render_markdown(report)

    assert "# OpenFisca AI Audit" in rendered
    assert "## Checks" in rendered
    assert "### `baseline`" in rendered
    assert "## Pattern Snapshot" in rendered
