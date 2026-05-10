"""Tests for local agent target resolution."""

import json
from pathlib import Path
from textwrap import dedent

import yaml

from openfisca_ai import cli
from openfisca_ai.agent_targets import list_agent_targets, resolve_agent_target


def write_file(path: Path, content: str) -> None:
    """Write a test fixture file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def test_resolve_agent_target_from_country_user_config(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/tunisia.yaml",
        """
        id: tunisia
        label: Tunisia
        existing_code:
          path: null
        """,
    )
    write_file(
        repo_root / "config/user.yaml",
        """
        base_path: /srv/openfisca
        agent_worktree_base: ${base_path}/.agent-worktrees
        countries:
          tunisia:
            existing_code:
              path: ${base_path}/openfisca-tunisia
            agent:
              aliases:
                - tunisie
                - openfisca-tunisia
              main_repo: openfisca-tunisia
              repos:
                openfisca-tunisia:
                  path: ${base_path}/openfisca-tunisia
                  mode: rw
                openfisca-core:
                  path: ${base_path}/openfisca-core
                  mode: ro
                openfisca-survey-manager:
                  path: ${base_path}/openfisca-survey-manager
                  mode: worktree
        """,
    )

    target = resolve_agent_target("tunisie")

    assert target["id"] == "tunisia"
    assert target["main_repo"]["path"] == "/srv/openfisca/openfisca-tunisia"
    assert target["worktree_base"] == "/srv/openfisca/.agent-worktrees"
    assert target["aliases"] == ["openfisca-tunisia", "tunisia", "tunisie"]
    assert [repo["mode"] for repo in target["repos"]] == ["rw", "ro", "worktree"]


def test_agent_target_defaults_to_existing_code_repo(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: ../fixtures/openfisca-demo
        """,
    )

    target = resolve_agent_target("openfisca-demo")

    assert target["id"] == "demo"
    assert target["main_repo"]["name"] == "openfisca-demo"
    assert target["main_repo"]["mode"] == "rw"
    assert target["repos"] == [target["main_repo"]]


def test_list_agent_targets_includes_user_only_country(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(repo_root / "config/countries/.keep", "")
    write_file(
        repo_root / "config/user.yaml",
        """
        base_path: /srv/openfisca
        countries:
          france:
            label: France
            existing_code:
              path: ${base_path}/openfisca-france
            agent:
              aliases:
                - openfisca-france
        """,
    )

    targets = list_agent_targets()

    assert [target["id"] for target in targets] == ["france"]
    assert resolve_agent_target("openfisca-france")["id"] == "france"


def test_cli_target_resolve_outputs_json(tmp_path, monkeypatch, capsys):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/tunisia.yaml",
        """
        id: tunisia
        label: Tunisia
        existing_code:
          path: null
        """,
    )
    write_file(
        repo_root / "config/user.yaml",
        """
        base_path: /srv/openfisca
        countries:
          tunisia:
            existing_code:
              path: ${base_path}/openfisca-tunisia
            agent:
              aliases:
                - tunisie
        """,
    )

    exit_code = cli.main(["target", "resolve", "tunisie", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["id"] == "tunisia"
    assert payload["main_repo"]["name"] == "openfisca-tunisia"


def test_cli_target_resolve_outputs_yaml_by_default(tmp_path, monkeypatch, capsys):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/tunisia.yaml",
        """
        id: tunisia
        label: Tunisia
        existing_code:
          path: null
        """,
    )
    write_file(
        repo_root / "config/user.yaml",
        """
        base_path: /srv/openfisca
        countries:
          tunisia:
            existing_code:
              path: ${base_path}/openfisca-tunisia
            agent:
              aliases:
                - tunisie
        """,
    )

    exit_code = cli.main(["target", "resolve", "tunisie"])

    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert "&id" not in captured.out
    assert "*id" not in captured.out
    assert payload["id"] == "tunisia"
    assert payload["main_repo"]["path"] == "/srv/openfisca/openfisca-tunisia"


def test_cli_target_list_outputs_yaml_when_requested(tmp_path, monkeypatch, capsys):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/demo.yaml",
        """
        id: demo
        label: Demo
        existing_code:
          path: /srv/openfisca/openfisca-demo
        """,
    )

    exit_code = cli.main(["target", "list", "--yaml"])

    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert payload[0]["id"] == "demo"
