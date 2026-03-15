"""Helpers for analyzing a reference OpenFisca country package."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    """Return the repository root from the installed source tree."""
    return Path(__file__).resolve().parents[3]


def _load_tool_module(filename: str):
    """Load a tool module from the repository tools/ directory."""
    module_path = _repo_root() / "tools" / filename
    if not module_path.exists():
        raise FileNotFoundError(f"Tool module not found: {module_path}")

    module_name = f"openfisca_ai_runtime_{module_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def summarize_pattern_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return the most useful parts of a full pattern report."""
    return {
        "country_package": report["country_package"],
        "structure": report["structure"],
        "entities": report["variables"]["entities"],
        "definition_periods": report["variables"]["definition_periods"],
        "set_input_helpers": report["variables"]["set_input_helpers"],
        "formula_patterns": report["variables"]["formula_patterns"],
        "aggregation_methods": report["variables"]["aggregation_methods"],
        "variable_domains": report["variables"]["top_domains"],
        "parameter_domains": report["parameters"]["top_domains"],
        "unit_types": report["parameters"]["unit_types"],
        "yaml_tests": report["tests"]["yaml_tests"],
        "python_tests": report["tests"]["python_tests"],
    }


def _ordered_keys(counts: dict[str, Any]) -> list[str]:
    """Return the non-empty keys of a counter-like mapping in insertion order."""
    return [key for key, value in counts.items() if value]


def _formula_helpers(formula_patterns: dict[str, int]) -> list[str]:
    """Render active formula helper patterns into a concise list."""
    helper_names = {
        "uses_parameters": "parameters(...)",
        "uses_where": "where",
        "uses_min": "min_/minimum",
        "uses_max": "max_/maximum",
        "uses_round": "round",
        "uses_select": "select",
        "uses_brackets_calc": "brackets.calc",
        "uses_members": "entity.members(...)",
        "uses_has_role": "entity.has_role(...)",
    }
    return [
        name
        for key, name in helper_names.items()
        if formula_patterns.get(key, 0)
    ]


def build_implementation_brief(
    extracted: dict[str, Any] | None = None,
    country_config: dict[str, Any] | None = None,
    reference_package_analysis: dict[str, Any] | None = None,
    country_id: str | None = None,
) -> dict[str, Any]:
    """Build an actionable implementation brief for downstream code generation."""
    extracted = extracted or {}
    country_config = country_config or {}
    conventions = country_config.get("conventions") or {}
    pattern_summary = (reference_package_analysis or {}).get("pattern_summary") or {}

    country_package = pattern_summary.get("country_package")
    variable_root = (
        f"{country_package}/variables"
        if country_package
        else "openfisca_<country>/variables"
    )
    parameter_root = (
        f"{country_package}/parameters"
        if country_package
        else "openfisca_<country>/parameters"
    )

    yaml_tests = pattern_summary.get("yaml_tests", 0)
    python_tests = pattern_summary.get("python_tests", 0)
    formula_patterns = pattern_summary.get("formula_patterns") or {}

    observed_entities = _ordered_keys(pattern_summary.get("entities") or {})
    configured_entities = conventions.get("entity_levels") or []

    next_steps = [
        "Extract the policy intent into variables, parameters, and eligibility rules.",
        f"Create or update variable modules under `{variable_root}`.",
        f"Create or update parameter YAML files under `{parameter_root}` when the rule depends on legislation values.",
        "Add YAML tests in `tests/` for threshold and edge cases.",
    ]
    if python_tests:
        next_steps.append("Add Python tests only for behavior that is awkward to express in YAML.")
    if pattern_summary.get("set_input_helpers"):
        next_steps.append("Reuse existing set_input helpers before introducing new input normalization.")

    return {
        "mode": "reference-guided" if reference_package_analysis else "generic",
        "country_id": country_id,
        "country_package": country_package,
        "extracted_fields": sorted(extracted.keys()),
        "configured_conventions": {
            "naming": conventions.get("naming", "snake_case"),
            "parameter_hierarchy": conventions.get("parameter_hierarchy") or [],
            "entity_levels": configured_entities,
        },
        "observed_package_patterns": {
            "entities": observed_entities,
            "definition_periods": _ordered_keys(pattern_summary.get("definition_periods") or {}),
            "set_input_helpers": _ordered_keys(pattern_summary.get("set_input_helpers") or {}),
            "variable_domains": _ordered_keys(pattern_summary.get("variable_domains") or {}),
            "parameter_domains": _ordered_keys(pattern_summary.get("parameter_domains") or {}),
            "unit_types": _ordered_keys(pattern_summary.get("unit_types") or {}),
            "formula_helpers": _formula_helpers(formula_patterns),
            "aggregation_methods": _ordered_keys(pattern_summary.get("aggregation_methods") or {}),
        },
        "test_strategy": {
            "prefer_yaml_tests": yaml_tests >= python_tests,
            "yaml_tests": yaml_tests,
            "python_tests": python_tests,
        },
        "scaffolding": {
            "variable_root": variable_root,
            "parameter_root": parameter_root,
            "tests_root": "tests",
            "preferred_entities": configured_entities or observed_entities,
        },
        "next_steps": next_steps,
    }


def analyze_reference_package(
    package_path: str | Path,
    include_audit_summary: bool = False,
) -> dict[str, Any]:
    """Analyze a reference OpenFisca package using the stable tool layer."""
    package_path = Path(package_path)

    extract_patterns = _load_tool_module("extract_patterns.py")
    pattern_report = extract_patterns.PatternExtractor(package_path).extract_all()

    result = {
        "package_path": str(package_path),
        "pattern_summary": summarize_pattern_report(pattern_report),
    }

    if include_audit_summary:
        audit_country_package = _load_tool_module("audit_country_package.py")
        audit_report = audit_country_package.CountryPackageAuditor(package_path).audit()
        result["audit_summary"] = audit_report["summary"]

    return result
