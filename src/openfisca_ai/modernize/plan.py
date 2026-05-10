"""Build non-destructive modernization plans."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openfisca_ai.modernize.detect import detect_modernization_state


def _step(
    step_id: str,
    title: str,
    status: str,
    risk: str,
    reason: str,
    suggested_commands: list[str] | None = None,
    agent_prompt: str | None = None,
) -> dict[str, Any]:
    step = {
        "id": step_id,
        "title": title,
        "status": status,
        "risk": risk,
        "reason": reason,
        "suggested_commands": suggested_commands or [],
    }
    if agent_prompt:
        step["agent_prompt"] = agent_prompt
    return step


def build_modernization_plan(path: str | Path) -> dict[str, Any]:
    """Build a proposal-only modernization plan for a repository."""
    state = detect_modernization_state(path)
    steps: list[dict[str, Any]] = []

    if state["repo_type"] in {"openfisca-package", "openfisca-large"}:
        steps.append(_step(
            "first-pass-validation",
            "Run an OpenFisca first-pass diagnosis",
            "recommended",
            "low",
            "Before changing packaging or CI, inspect current parameter metadata, units, Python formulas, tests, and package audit results.",
            [
                "uv run openfisca-ai validate-parameters .",
                "uv run openfisca-ai validate-units .",
                "uv run openfisca-ai validate-code .",
                "uv run openfisca-ai validate-tests .",
                "uv run openfisca-ai audit . --markdown --output audit-report.md",
                f"uv run openfisca test --country-package {state['package_name']} tests" if state.get("package_name") else "uv run openfisca test --country-package <package_name> tests",
            ],
        ))
        steps.append(_step(
            "resolve-detected-errors",
            "Resolve detected OpenFisca errors before tooling migration",
            "conditional",
            "medium",
            "If the first-pass diagnosis reports errors, resolve or triage them before changing packaging, CI, or formatting. An agent can help classify findings, propose focused fixes, and rerun checks.",
            [
                "uv run openfisca-ai audit . --markdown --output audit-report.md",
                "uv run openfisca-ai audit . --json --output audit-report.json",
            ],
            agent_prompt=(
                "Read audit-report.md and audit-report.json. Classify findings into: "
                "(1) quick metadata fixes, (2) code hardcodes/TODOs needing policy review, "
                "(3) missing tests, (4) false positives. Propose a minimal sequence of fixes, "
                "apply only the approved fix group, then rerun the relevant openfisca-ai checks."
            ),
        ))
    elif state["repo_type"] == "python-package":
        steps.append(_step(
            "first-pass-validation",
            "Run a Python package first-pass diagnosis",
            "recommended",
            "low",
            "Before changing packaging or CI, run the existing test suite and inspect current tooling.",
            [
                "uv run pytest",
                "uv run openfisca-ai check-tooling .",
            ],
        ))

    if state["packaging"] == "pyproject-project":
        steps.append(_step(
            "packaging",
            "Keep canonical pyproject packaging",
            "ok",
            "low",
            "The repository already has a PEP 621 [project] section in pyproject.toml.",
        ))
    elif state["packaging"] in {"setuptools-legacy", "pyproject-tools-only"}:
        steps.append(_step(
            "packaging",
            "Propose canonical pyproject packaging",
            "propose",
            "medium",
            "Package metadata is not fully declared in a PEP 621 [project] section.",
            ["openfisca-ai modernize plan .", "uv build"],
        ))
    else:
        steps.append(_step(
            "packaging",
            "Inspect packaging manually",
            "manual_review",
            "medium",
            "No canonical Python packaging file was detected.",
        ))

    if state["environment_manager"] == "uv":
        steps.append(_step(
            "environment",
            "Keep uv environment management",
            "ok",
            "low",
            "uv.lock is present.",
        ))
    else:
        steps.append(_step(
            "environment",
            "Propose uv environment management",
            "propose",
            "medium",
            "uv.lock is not present; migration should preserve existing install/test commands first.",
            ["uv sync", "uv lock"],
        ))

    if state["formatter"] == "ruff":
        steps.append(_step(
            "formatter",
            "Keep ruff formatter/linter",
            "ok",
            "low",
            "ruff is already detected in pyproject.toml or Makefile.",
        ))
    else:
        steps.append(_step(
            "formatter",
            "Propose ruff linting",
            "propose",
            "low",
            "Ruff was not detected as the main formatter/linter.",
            ["uv run ruff check .", "uv run ruff format --check ."],
        ))

    if state["repo_type"] in {"openfisca-package", "openfisca-large"} and not state["has_yamllint"]:
        steps.append(_step(
            "yaml-lint",
            "Propose yamllint for parameters and tests",
            "propose",
            "low",
            "OpenFisca packages rely heavily on YAML parameters and tests.",
            ["uv run yamllint <package>/parameters tests"],
        ))

    if state["has_makefile"]:
        steps.append(_step(
            "makefile",
            "Review existing Makefile targets",
            "review",
            "low",
            "A Makefile exists; modernize should preserve project-specific commands.",
        ))
    else:
        steps.append(_step(
            "makefile",
            "Propose a small Makefile",
            "propose",
            "low",
            "No Makefile was detected for common install, lint, and test commands.",
        ))

    if not state["has_openfisca_ai_dependency"] and state["repo_type"] in {"openfisca-package", "openfisca-large"}:
        steps.append(_step(
            "openfisca-ai-tools",
            "Propose openfisca-ai as a dev dependency",
            "propose",
            "low",
            "Adding openfisca-ai enables audit, target, MCP, and validation helpers in CI.",
            ["uv add --group dev openfisca-ai"],
        ))

    if state["has_github_actions"] or state["has_gitlab_ci"]:
        steps.append(_step(
            "ci",
            "Plan CI normalization without overwriting existing workflows",
            "review",
            "medium",
            "Existing CI files were detected; future ci plan/apply should propose diffs, not replace blindly.",
            ["openfisca-ai ci detect ."],
        ))
    else:
        steps.append(_step(
            "ci",
            "Propose CI workflows",
            "propose",
            "medium",
            "No GitHub Actions or GitLab CI configuration was detected.",
            ["openfisca-ai ci detect ."],
        ))

    return {
        "schema_version": 1,
        "repo_path": state["repo_path"],
        "repo_type": state["repo_type"],
        "state": state,
        "steps": steps,
        "notes": [
            "This plan is proposal-only and does not modify files.",
            "Apply steps one by one after human or agent review.",
        ],
    }
