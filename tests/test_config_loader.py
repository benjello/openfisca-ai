"""Tests for configuration loading and compatibility."""

from pathlib import Path
from textwrap import dedent

from openfisca_ai.config_loader import (
    get_legislative_sources_root,
    get_reference_code_path,
    get_user_config_path,
    load_country_config,
)


def write_file(path: Path, content: str) -> None:
    """Write a test fixture file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def test_load_country_config_merges_canonical_user_overrides(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/tunisia.yaml",
        """
        id: tunisia
        label: Tunisia
        legislative_sources:
          root: null
        existing_code:
          path: null
        """,
    )
    write_file(
        repo_root / "config/user.yaml",
        """
        base_path: /srv/openfisca
        legislation_base_path: /srv/legislation
        countries:
          tunisia:
            existing_code:
              path: ${base_path}/openfisca-tunisia
            legislative_sources:
              root: ${legislation_base_path}/tunisia
        """,
    )

    config = load_country_config("tunisia")

    assert config is not None
    assert config["existing_code"]["path"] == "/srv/openfisca/openfisca-tunisia"
    assert config["legislative_sources"]["root"] == "/srv/legislation/tunisia"
    assert get_reference_code_path("tunisia") == Path("/srv/openfisca/openfisca-tunisia")
    assert get_legislative_sources_root("tunisia") == Path("/srv/legislation/tunisia")


def test_load_country_config_supports_legacy_user_format(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))

    write_file(
        repo_root / "config/countries/tunisia.yaml",
        """
        id: tunisia
        label: Tunisia
        legislative_sources:
          root: null
        existing_code:
          path: null
        """,
    )
    write_file(
        repo_root / "config/user.yaml",
        """
        base_path: /legacy/repos
        countries:
          tunisia:
            path: ${base_path}/openfisca-tunisia
        legislative_sources:
          tunisia: /legacy/laws/tunisia
        """,
    )

    config = load_country_config("tunisia")

    assert config is not None
    assert config["existing_code"]["path"] == "/legacy/repos/openfisca-tunisia"
    assert config["legislative_sources"]["root"] == "/legacy/laws/tunisia"


def test_global_legacy_config_yaml_is_supported(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    home_root = tmp_path / "home"
    monkeypatch.setenv("OPENFISCA_AI_ROOT", str(repo_root))
    monkeypatch.setenv("HOME", str(home_root))

    write_file(
        repo_root / "config/countries/tunisia.yaml",
        """
        id: tunisia
        label: Tunisia
        existing_code:
          path: null
        """,
    )
    global_config = home_root / ".config/openfisca-ai/config.yaml"
    write_file(
        global_config,
        """
        countries:
          tunisia:
            existing_code:
              path: /global/openfisca-tunisia
        """,
    )

    assert get_user_config_path() == global_config
    assert get_reference_code_path("tunisia") == Path("/global/openfisca-tunisia")
