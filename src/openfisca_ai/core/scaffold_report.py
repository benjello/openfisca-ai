"""Render human-readable scaffold reports."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _format_mapping_list(values: dict[str, Any]) -> str:
    """Render a simple mapping as a compact comma-separated list."""
    items = [key for key, value in values.items() if value]
    return ", ".join(items) if items else "none"


def render_scaffold_report_markdown(result: dict[str, Any]) -> str:
    """Render a markdown report for scaffold generation."""
    brief = result.get("implementation_brief") or {}
    patterns = brief.get("observed_package_patterns") or {}
    scaffolding = brief.get("scaffolding") or {}
    artifacts = result.get("artifacts") or []
    notes = result.get("notes") or []
    plan = result.get("artifact_write_plan") or []

    action_counts = Counter(entry.get("action", "unknown") for entry in plan)
    lines = [
        "# OpenFisca AI Scaffold Report",
        "",
        f"- Country: `{result.get('country_id') or 'n/a'}`",
        f"- Reference package: `{brief.get('country_package') or result.get('reference_code_path') or 'n/a'}`",
        f"- Mode: `{brief.get('mode', 'generic')}`",
        f"- Generated artifacts: `{len(artifacts)}`",
        "",
        "## Scaffolding Targets",
        "",
        f"- Variable root: `{scaffolding.get('variable_root', 'n/a')}`",
        f"- Parameter root: `{scaffolding.get('parameter_root', 'n/a')}`",
        f"- Tests root: `{scaffolding.get('tests_root', 'n/a')}`",
        "",
        "## Observed Patterns",
        "",
        f"- Entities: `{', '.join(patterns.get('entities') or []) or 'none'}`",
        f"- Definition periods: `{', '.join(patterns.get('definition_periods') or []) or 'none'}`",
        f"- Formula helpers: `{', '.join(patterns.get('formula_helpers') or []) or 'none'}`",
        f"- Variable domains: `{', '.join(patterns.get('variable_domains') or []) or 'none'}`",
        f"- Parameter domains: `{', '.join(patterns.get('parameter_domains') or []) or 'none'}`",
        f"- Unit types: `{', '.join(patterns.get('unit_types') or []) or 'none'}`",
        "",
        "## Artifacts",
        "",
    ]

    if artifacts:
        for artifact in artifacts:
            lines.append(f"- `{artifact['kind']}` -> `{artifact['path']}`")
    else:
        lines.append("- none")

    if notes:
        lines.extend(["", "## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")

    if plan:
        lines.extend(
            [
                "",
                "## Write Plan",
                "",
                f"- Actions: `{dict(action_counts)}`",
                "",
            ]
        )
        for entry in plan:
            lines.extend(
                [
                    f"### `{entry['path']}`",
                    "",
                    f"- Kind: `{entry['kind']}`",
                    f"- Exists: `{'yes' if entry.get('exists') else 'no'}`",
                    f"- Action: `{entry.get('action', 'unknown')}`",
                ]
            )
            if entry.get("diff_preview"):
                lines.extend(
                    [
                        "",
                        "```diff",
                        entry["diff_preview"],
                        "```",
                        "",
                    ]
                )
            else:
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_scaffold_report_text(result: dict[str, Any]) -> str:
    """Render a concise text report for scaffold generation."""
    brief = result.get("implementation_brief") or {}
    patterns = brief.get("observed_package_patterns") or {}
    plan = result.get("artifact_write_plan") or []
    notes = result.get("notes") or []
    artifacts = result.get("artifacts") or []
    action_counts = Counter(entry.get("action", "unknown") for entry in plan)

    lines = [
        "OPENFISCA AI SCAFFOLD REPORT",
        f"country: {result.get('country_id') or 'n/a'}",
        f"mode: {brief.get('mode', 'generic')}",
        f"artifacts: {len(artifacts)}",
        f"variable_root: {brief.get('scaffolding', {}).get('variable_root', 'n/a')}",
        f"parameter_root: {brief.get('scaffolding', {}).get('parameter_root', 'n/a')}",
        f"entities: {_format_mapping_list({item: 1 for item in patterns.get('entities') or []})}",
        f"formula_helpers: {_format_mapping_list({item: 1 for item in patterns.get('formula_helpers') or []})}",
    ]

    if plan:
        lines.append(f"write_actions: {dict(action_counts)}")
        for entry in plan:
            lines.append(
                f"- {entry['action']} {entry['kind']} {entry['path']} "
                f"(exists={'yes' if entry.get('exists') else 'no'})"
            )

    if notes:
        lines.append("notes:")
        for note in notes:
            lines.append(f"- {note}")

    return "\n".join(lines) + "\n"
