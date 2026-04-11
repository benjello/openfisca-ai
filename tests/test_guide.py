"""Tests for the guide discovery module."""

from pathlib import Path

import pytest

from openfisca_ai import cli, guide


def test_list_guides_includes_known_roles():
    names = {g.name for g in guide.list_guides()}
    assert {"principles", "test-creator", "rules-engineer", "validators"} <= names


def test_resolve_guide_by_short_name():
    g = guide.resolve_guide("test-creator")
    assert g.relative_path == "02-framework/roles/test-creator.md"


def test_resolve_guide_by_relative_path():
    g = guide.resolve_guide("02-framework/roles/test-creator")
    assert g.name == "test-creator"


def test_resolve_guide_by_relative_path_with_extension():
    g = guide.resolve_guide("02-framework/roles/test-creator.md")
    assert g.name == "test-creator"


def test_resolve_guide_unknown_raises():
    with pytest.raises(LookupError):
        guide.resolve_guide("nonexistent-guide")


def test_resolve_guide_ambiguous_short_name_raises(monkeypatch):
    fake = [
        guide.Guide(name="dup", relative_path="dir1/dup.md"),
        guide.Guide(name="dup", relative_path="dir2/dup.md"),
    ]
    monkeypatch.setattr(guide, "list_guides", lambda: fake)
    with pytest.raises(LookupError, match="ambiguous"):
        guide.resolve_guide("dup")


def test_read_guide_returns_packaged_content():
    text = guide.read_guide("test-creator")
    assert "test-creator" in text.lower() or "test" in text.lower()


def test_read_guide_applies_overlay(tmp_path):
    overlay_dir = tmp_path / "docs" / "openfisca-ai" / "agents" / "02-framework" / "roles"
    overlay_dir.mkdir(parents=True)
    overlay_file = overlay_dir / "test-creator.md"
    overlay_file.write_text("Project specific note about Individu entity.\n", encoding="utf-8")

    merged = guide.read_guide("test-creator", project_root=tmp_path)
    assert "Spécificités projet" in merged
    assert "Project specific note about Individu entity." in merged


def test_read_guide_no_overlay_when_absent(tmp_path):
    text = guide.read_guide("test-creator", project_root=tmp_path)
    assert "Spécificités projet" not in text


def test_guide_resource_path_exists():
    g = guide.resolve_guide("test-creator")
    path = guide.guide_resource_path(g)
    assert path.is_file()


def test_resources_root_path_exists():
    root = guide.resources_root_path()
    assert root.is_dir()
    assert (root / "02-framework" / "roles" / "test-creator.md").is_file()


# CLI tests


def test_cli_guide_list(capsys):
    exit_code = cli.main(["guide", "list"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "test-creator" in captured.out
    assert "02-framework/roles/test-creator.md" in captured.out


def test_cli_guide_show(capsys):
    exit_code = cli.main(["guide", "show", "test-creator"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "test-creator.md" in captured.out


def test_cli_guide_cat(capsys):
    exit_code = cli.main(["guide", "cat", "test-creator"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(captured.out) > 100


def test_cli_guide_path(capsys):
    exit_code = cli.main(["guide", "path"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert Path(captured.out.strip()).is_dir()


def test_cli_guide_unknown_name(capsys):
    exit_code = cli.main(["guide", "show", "nonexistent"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Unknown guide" in captured.err


def test_cli_guide_no_subcommand(capsys):
    exit_code = cli.main(["guide"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Usage:" in captured.err
