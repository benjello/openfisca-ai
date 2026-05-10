"""Group audit findings into actionable modernization work items."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from openfisca_ai.tools.audit_country_package import CountryPackageAuditor


def _sample_files(items: list[dict[str, Any]], limit: int = 8) -> list[str]:
    seen: list[str] = []
    for item in items:
        file_path = item.get("file")
        if file_path and file_path not in seen:
            seen.append(file_path)
        if len(seen) >= limit:
            break
    return seen


def _group(group_id: str, title: str, priority: str, risk: str, action: str, items: list[dict[str, Any]], rationale: str, agent_prompt: str) -> dict[str, Any]:
    return {
        "id": group_id,
        "title": title,
        "priority": priority,
        "risk": risk,
        "action": action,
        "count": len(items),
        "sample_files": _sample_files(items),
        "rationale": rationale,
        "agent_prompt": agent_prompt,
    }


def build_error_resolution_plan(path: str | Path) -> dict[str, Any]:
    """Build a grouped, proposal-only plan from audit findings."""
    repo_path = Path(path)
    report = CountryPackageAuditor(repo_path).audit()
    parameters = report["checks"]["parameters"]
    code = report["checks"]["code"]
    tests = report["checks"]["tests"]

    parameter_errors = parameters.get("errors", [])
    parameter_warnings = parameters.get("warnings", [])
    code_errors = code.get("errors", [])
    test_errors = tests.get("errors", [])

    missing_labels = [item for item in parameter_errors if item.get("type") == "missing_label"]
    missing_references = [item for item in parameter_errors if item.get("type") == "missing_reference"]
    translated_labels = [item for item in parameter_warnings if item.get("type") in {"missing_label_ar", "missing_label_en"}]
    pdf_pages = [item for item in parameter_warnings if item.get("type") == "missing_page_number"]
    hardcodes = [item for item in code_errors if item.get("type") in {"hardcoded_numeric_value", "todo_comment"}]

    groups = []
    if missing_labels:
        groups.append(_group(
            "parameter-labels",
            "Add missing parameter labels",
            "high",
            "low",
            "agent-assisted",
            missing_labels,
            "Labels can often be drafted from descriptions, then reviewed quickly by a human.",
            "For each sampled file, propose a concise French label based on description and path. Do not change references or values.",
        ))
    if missing_references:
        groups.append(_group(
            "missing-references",
            "Add missing legal references",
            "high",
            "high",
            "human-source-required",
            missing_references,
            "References should not be invented. They need source lookup or domain validation.",
            "Group files by policy domain and identify likely source families. Ask for source confirmation before editing YAML.",
        ))
    if test_errors:
        groups.append(_group(
            "missing-tests",
            "Add missing tests for formula variables",
            "medium",
            "medium",
            "agent-assisted",
            test_errors,
            "Missing tests are actionable but require choosing representative input situations.",
            "Group untested variables by file/domain. Propose one minimal YAML test per high-value variable before editing.",
        ))
    if hardcodes:
        groups.append(_group(
            "code-hardcodes-and-todos",
            "Review hardcoded values and TODO markers",
            "medium",
            "high",
            "policy-review-required",
            hardcodes,
            "Hardcoded values and TODOs can be real policy debt or validator false positives.",
            "Classify each finding as true policy value, enum/status code, harmless constant, or TODO needing issue. Do not refactor without approval.",
        ))
    if translated_labels:
        groups.append(_group(
            "translated-labels",
            "Add translated parameter labels",
            "low",
            "medium",
            "agent-assisted-review",
            translated_labels,
            "Translations are useful but should not block modernization unless multilingual metadata is a current goal.",
            "Draft label_en and label_ar from existing French labels/descriptions, then request human validation.",
        ))
    if pdf_pages:
        groups.append(_group(
            "pdf-page-numbers",
            "Add page anchors to PDF references",
            "low",
            "medium",
            "defer-by-default",
            pdf_pages,
            "Page anchors improve traceability but are tedious and should not be prioritized before labels, references, and tests.",
            "Only work on this group when source PDFs are available and the user explicitly asks for page-level cleanup.",
        ))

    return {
        "schema_version": 1,
        "repo_path": str(repo_path.resolve()),
        "summary": report["summary"],
        "groups": groups,
        "counts_by_group": {group["id"]: group["count"] for group in groups},
        "counts_by_priority": dict(Counter(group["priority"] for group in groups)),
        "notes": [
            "This plan is proposal-only and does not modify files.",
            "pdf-page-numbers is intentionally low priority by default.",
        ],
    }
