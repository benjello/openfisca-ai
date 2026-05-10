"""Skill: generate OpenFisca scaffolding from structured law."""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

import yaml


DEFAULT_RETURN_BY_TYPE = {
    "bool": "False",
    "float": "0.0",
    "int": "0",
    "str": '""',
}


def _snake_case(value: str) -> str:
    """Normalize a human or technical identifier to snake_case."""
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value)
    return value.strip("_").lower() or "policy_rule"


def _entity_argument(entity_name: str) -> str:
    """Convert an OpenFisca entity class name to a formula argument name."""
    return _snake_case(entity_name)


def _normalize_value_type(raw: str | None) -> str:
    """Normalize a value type string to a Python/OpenFisca value_type symbol."""
    value_type = (raw or "float").strip().lower()
    return {
        "boolean": "bool",
        "number": "float",
        "string": "str",
    }.get(value_type, value_type)


def _default_return(value_type: str) -> str:
    """Return a safe placeholder expression for the given value type."""
    return DEFAULT_RETURN_BY_TYPE.get(value_type, "0.0")


def _parameter_access(parameter_path: str) -> str:
    """Render a dotted parameter path into OpenFisca Python access."""
    return "parameters(period)." + parameter_path.replace("/", ".")


def _reference_comment(reference: Any) -> str:
    """Render optional legal references as a concise comment block."""
    if not reference:
        return ""
    refs = reference if isinstance(reference, list) else [reference]
    lines = [f"# Reference: {item}" for item in refs if item]
    return "\n".join(lines)


def _variable_file_path(variable: dict[str, Any], scaffolding: dict[str, Any]) -> str:
    """Build a target path for a generated variable file."""
    root = PurePosixPath(scaffolding.get("variable_root", "openfisca_<country>/variables"))
    domain = variable.get("domain")
    filename = variable.get("filename") or _snake_case(variable.get("name", "policy_rule"))
    if domain:
        return str(root / _snake_case(domain) / f"{filename}.py")
    return str(root / f"{filename}.py")


def _test_file_path(variable: dict[str, Any], scaffolding: dict[str, Any]) -> str:
    """Build a target path for a generated YAML test file."""
    root = PurePosixPath(scaffolding.get("tests_root", "tests"))
    domain = variable.get("domain")
    filename = variable.get("filename") or _snake_case(variable.get("name", "policy_rule"))
    if domain:
        return str(root / _snake_case(domain) / f"{filename}.yaml")
    return str(root / f"{filename}.yaml")


def _render_formula(variable: dict[str, Any]) -> list[str]:
    """Render a minimal formula body from extracted variable hints."""
    value_type = _normalize_value_type(variable.get("value_type"))
    entity_name = variable.get("entity", "Person")
    entity_arg = _entity_argument(entity_name)
    formula_type = variable.get("formula_type")
    if not formula_type:
        if variable.get("base_variable") and variable.get("parameter"):
            formula_type = "multiply_parameter"
        elif variable.get("parameter"):
            formula_type = "parameter_only"
        elif variable.get("source_variable"):
            formula_type = "copy_input"

    if formula_type == "multiply_parameter":
        base_variable = variable["base_variable"]
        parameter = variable["parameter"]
        parameter_name = _snake_case(parameter.split(".")[-1])
        return [
            f'{base_variable} = {entity_arg}("{base_variable}", period)',
            f"{parameter_name} = {_parameter_access(parameter)}",
            f"return {base_variable} * {parameter_name}",
        ]

    if formula_type == "parameter_only":
        parameter = variable["parameter"]
        return [f"return {_parameter_access(parameter)}"]

    if formula_type == "copy_input":
        source_variable = variable["source_variable"]
        return [f'return {entity_arg}("{source_variable}", period)']

    return [
        "# TODO: encode the legislative rule from the extracted specification.",
        f"return {_default_return(value_type)}",
    ]


def _render_variable_code(variable: dict[str, Any]) -> str:
    """Render a minimal OpenFisca variable scaffold."""
    name = _snake_case(variable.get("name", "policy_rule"))
    entity_name = variable.get("entity", "Person")
    period = (variable.get("definition_period") or "YEAR").upper()
    value_type = _normalize_value_type(variable.get("value_type"))
    label = variable.get("label")
    formula_lines = _render_formula(variable)
    reference_comment = _reference_comment(variable.get("reference"))

    lines = [
        f"from openfisca_core.periods import {period}",
        "from openfisca_core.variables import Variable",
        "",
    ]
    if reference_comment:
        lines.extend([reference_comment, ""])

    lines.extend(
        [
            f"class {name}(Variable):",
            f"    value_type = {value_type}",
            f"    entity = {entity_name}",
            f"    definition_period = {period}",
        ]
    )
    if label:
        lines.append(f'    label = "{label}"')
    if variable.get("set_input"):
        lines.append(f"    set_input = {variable['set_input']}")

    lines.extend(["", f"    def formula({_entity_argument(entity_name)}, period, parameters):"])
    for line in formula_lines:
        lines.append(f"        {line}")

    return "\n".join(lines) + "\n"


def _render_parameter_yaml(parameter: dict[str, Any]) -> str:
    """Render a minimal OpenFisca parameter YAML scaffold."""
    effective_date = parameter.get("effective_date", "2024-01-01")
    value = parameter.get("value", 0)
    payload: dict[str, Any] = {
        "description": parameter.get("description") or parameter.get("label") or "TODO: describe parameter.",
        "label": parameter.get("label") or parameter.get("name", "parameter"),
        "reference": parameter.get("reference") or ["TODO: add legal reference"],
    }

    unit = parameter.get("unit")
    if unit:
        payload["unit"] = unit

    payload["values"] = {
        effective_date: value,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def _parameter_file_path(parameter: dict[str, Any], scaffolding: dict[str, Any]) -> str:
    """Build a target path for a generated parameter YAML file."""
    root = PurePosixPath(scaffolding.get("parameter_root", "openfisca_<country>/parameters"))
    dotted_name = parameter.get("name", "policy.parameter")
    return str(root / PurePosixPath(*[part for part in dotted_name.replace("/", ".").split(".") if part])).rstrip("/") + ".yaml"


def _render_yaml_tests(tests: list[dict[str, Any]]) -> str:
    """Render explicit YAML tests from extracted specs."""
    return yaml.safe_dump(tests, sort_keys=False, allow_unicode=True)


def _render_test_template(variable: dict[str, Any]) -> str:
    """Render a commented YAML test scaffold when no explicit test is provided."""
    variable_name = _snake_case(variable.get("name", "policy_rule"))
    base_variable = variable.get("base_variable") or variable.get("source_variable") or "input_variable"
    period = variable.get("test_period") or "2024"
    return "\n".join(
        [
            "# TODO: replace this scaffold with a real OpenFisca YAML test.",
            f"# - name: {variable_name} basic case",
            f"#   period: {period}",
            "#   input:",
            f"#     {base_variable}: 0",
            "#   output:",
            f"#     {variable_name}: 0",
            "",
        ]
    )


def generate_scaffolding(
    extracted: dict[str, Any],
    implementation_brief: dict[str, Any] | None = None,
    **options,
) -> dict[str, Any]:
    """
    Generate non-destructive scaffolding artifacts from structured extracted law.

    Returns a dict with `artifacts`, `primary_code`, and `notes`.
    """
    implementation_brief = implementation_brief or {}
    scaffolding = implementation_brief.get("scaffolding") or {}
    extracted = extracted or {}

    variables = extracted.get("variables") or []
    parameters = extracted.get("parameters") or []
    explicit_tests = extracted.get("tests") or []

    artifacts: list[dict[str, str]] = []
    notes: list[str] = []

    for variable in variables:
        artifacts.append(
            {
                "kind": "variable",
                "path": _variable_file_path(variable, scaffolding),
                "content": _render_variable_code(variable),
            }
        )

    for parameter in parameters:
        artifacts.append(
            {
                "kind": "parameter",
                "path": _parameter_file_path(parameter, scaffolding),
                "content": _render_parameter_yaml(parameter),
            }
        )

    if explicit_tests:
        first_variable = variables[0] if variables else {}
        artifacts.append(
            {
                "kind": "yaml_test",
                "path": _test_file_path(first_variable, scaffolding),
                "content": _render_yaml_tests(explicit_tests),
            }
        )
    elif variables:
        for variable in variables:
            artifacts.append(
                {
                    "kind": "yaml_test_template",
                    "path": _test_file_path(variable, scaffolding),
                    "content": _render_test_template(variable),
                }
            )
        notes.append("No explicit tests were provided in `inputs.extracted.tests`; generated commented YAML test templates instead.")

    if not artifacts:
        notes.append("No structured variables or parameters were provided. Pass `inputs.extracted` to generate scaffolding artifacts.")

    primary_code = next((artifact["content"] for artifact in artifacts if artifact["kind"] == "variable"), "")
    return {
        "artifacts": artifacts,
        "notes": notes,
        "primary_code": primary_code,
    }


def generate_code(extracted: dict, **options) -> str:
    """
    Generate the primary variable source code from extracted law structure.

    This keeps the original string-based contract while the richer scaffolding
    API lives in `generate_scaffolding`.
    """
    return generate_scaffolding(extracted, **options)["primary_code"]
