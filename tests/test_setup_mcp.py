"""Tests for setup_mcp.py."""

from tests.tool_test_helpers import create_country_repo, load_tool_module, write_file


setup_mcp = load_tool_module("setup_mcp.py", "setup_mcp_tool")


def test_setup_mcp_generates_config_from_repo_root(tmp_path):
    repo_path = create_country_repo(tmp_path)

    config = setup_mcp.generate_mcp_config(repo_path)

    server = config["mcpServers"]["openfisca"]
    args = server["args"]

    assert "uv run openfisca serve --country-package openfisca_demo" in args
    assert str(repo_path.resolve()) in args


def test_setup_mcp_accepts_package_directory_and_writes_at_repo_root(tmp_path):
    repo_path = create_country_repo(tmp_path)
    package_path = repo_path / "openfisca_demo"

    result = setup_mcp.setup_mcp(package_path, dry_run=True)

    assert result["status"] == "dry_run"
    assert result["path"] == str(repo_path / ".mcp.json")
    assert any(
        "openfisca serve --country-package openfisca_demo" in arg
        for arg in result["config"]["mcpServers"]["openfisca"]["args"]
    )


def test_setup_mcp_generates_config_from_target(tmp_path, monkeypatch):
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

    result = setup_mcp.setup_mcp(tmp_path, dry_run=True, target_name="demo")

    assert result["path"] == str(repo_path / ".mcp.json")
    assert result["config"]["mcpServers"]["openfisca"]["args"] == [
        "run",
        "openfisca-ai",
        "mcp",
        "--target",
        "demo",
        "--url",
        "http://localhost:5000",
    ]
