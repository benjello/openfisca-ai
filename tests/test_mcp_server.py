"""Tests for MCP server wiring."""

import pytest


pytest.importorskip("mcp")


def test_mcp_run_configures_client_url(monkeypatch):
    from openfisca_ai.mcp import server

    async def fake_main():
        return None

    monkeypatch.setattr(server, "_main", fake_main)

    server.run(url="http://example.test:1234", serve=False, repo_path="/tmp/repo")

    assert server.client is not None
    assert server.client.base_url == "http://example.test:1234"


def test_cli_mcp_target_resolves_repo_and_serve_command(tmp_path, monkeypatch):
    from openfisca_ai import cli
    from openfisca_ai.mcp import server
    from tests.tool_test_helpers import write_file

    config_root = tmp_path / "config-root"
    repo_path = tmp_path / "workspace/openfisca-demo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(config_root))
    write_file(repo_path / "openfisca_demo/__init__.py", "")
    write_file(repo_path / ".git", "gitdir: .git/mock\n")
    write_file(
        config_root / "config/countries/demo.yaml",
        f"""
        id: demo
        label: Demo
        existing_code:
          path: {repo_path}
        """,
    )

    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(server, "run", fake_run)

    assert cli._run_mcp_command(["mcp", "--target", "demo"]) == 0
    assert captured == {
        "url": None,
        "serve": True,
        "serve_command": ["uv", "run", "openfisca", "serve", "--country-package", "openfisca_demo"],
        "repo_path": str(repo_path),
    }
