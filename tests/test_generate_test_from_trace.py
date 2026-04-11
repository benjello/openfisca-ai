"""Tests for the generate-test-from-trace CLI."""

import io
import json
import sys

from openfisca_ai import cli


SAMPLE_TRACE = {
    "situation": {
        "persons": {
            "alice": {
                "salaire_brut": {"2025-01": 3000},
                "salaire_net": {"2025-01": None},
            }
        }
    },
    "trace": {
        "salaire_net<2025-01>": {
            "value": 2400.0,
            "dependencies": [],
            "parameters": [],
        }
    },
}


def _run_cli(args):
    return cli.main(args)


def test_generate_test_from_trace_from_file(tmp_path, capsys):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(json.dumps(SAMPLE_TRACE), encoding="utf-8")

    exit_code = _run_cli(["generate-test-from-trace", str(trace_path), "--name", "test_alice"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "test_alice" in captured.out
    assert "salaire_net" in captured.out


def test_generate_test_from_trace_writes_output_file(tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(json.dumps(SAMPLE_TRACE), encoding="utf-8")

    out_path = tmp_path / "test_alice.yaml"
    exit_code = _run_cli(
        [
            "generate-test-from-trace",
            str(trace_path),
            "--name",
            "test_alice",
            "--output",
            str(out_path),
        ]
    )
    assert exit_code == 0
    assert out_path.is_file()
    body = out_path.read_text(encoding="utf-8")
    assert "test_alice" in body


def test_generate_test_from_trace_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(SAMPLE_TRACE)))

    exit_code = _run_cli(["generate-test-from-trace", "-", "--name", "test_alice"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "test_alice" in captured.out


def test_generate_test_from_trace_stdin_invalid_json(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json at all"))

    exit_code = _run_cli(["generate-test-from-trace", "-", "--name", "test_alice"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Invalid JSON" in captured.err


def test_generate_test_from_trace_missing_file(tmp_path, capsys):
    exit_code = _run_cli(
        ["generate-test-from-trace", str(tmp_path / "missing.json"), "--name", "test_alice"]
    )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "not found" in captured.err.lower()
