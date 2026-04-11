#!/usr/bin/env python3
"""Generate an OpenFisca YAML test from a trace_calculation MCP response.

Usage:
    # From a JSON file containing the trace output:
    openfisca-ai generate-test-from-trace trace.json [--output test_output.yaml] [--name my_test]

    # Or import and use programmatically:
    from tools.generate_test_from_trace import generate_yaml_test
    yaml_str = generate_yaml_test(trace_response, name="test_salaire_base")

Why:
    trace_calculation returns the full dependency tree with computed values.
    This tool converts that into a ready-to-use YAML test, with:
    - inputs: the situation values you provided (non-null)
    - outputs: the values computed by the system (previously null)
    - intermediate values documented as comments for traceability

Token savings:
    Without this tool, writing tests requires manually computing expected values
    and constructing the YAML by hand. This tool does it in one step from a live trace.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _extract_period(variable_data: dict) -> str | None:
    """Extract the first period key from a variable's period dict."""
    for period_key in variable_data:
        return period_key
    return None


VarKey = tuple[str, str, str, str]  # (entity_group, instance_id, var_name, period)


def _extract_inputs_outputs(
    situation: dict[str, Any],
    trace: dict[str, Any],
) -> tuple[dict[VarKey, Any], dict[VarKey, Any]]:
    """Split situation variables into inputs (provided) and outputs (computed/null).

    Returns:
        inputs: variables with non-null values (what you provided)
        outputs: variables that were null (what the system computed)
    """
    inputs: dict[VarKey, Any] = {}
    outputs: dict[VarKey, Any] = {}

    # Walk through all entity groups in the situation
    for entity_group, instances in situation.items():
        if not isinstance(instances, dict):
            continue
        for instance_id, instance_data in instances.items():
            if not isinstance(instance_data, dict):
                continue
            for var_name, period_data in instance_data.items():
                if not isinstance(period_data, dict):
                    continue  # skip role lists like "adults": [...]
                period = _extract_period(period_data)
                if period is None:
                    continue
                value = period_data[period]

                key = (entity_group, instance_id, var_name, period)
                if value is None:
                    # This was requested — find computed value in trace
                    computed = _find_computed_value(trace, var_name, instance_id, period)
                    outputs[key] = computed
                else:
                    inputs[key] = value

    return inputs, outputs


def _find_computed_value(
    trace: dict[str, Any],
    var_name: str,
    instance_id: str,
    period: str,
) -> Any:
    """Find the computed value for a variable in the trace output."""
    # Trace structure varies by OpenFisca version, handle common shapes
    trace_data = trace.get("trace", trace)

    # Try key like "variable_name<period>" or "variable_name-period"
    for key_pattern in [
        f"{var_name}<{period}>",
        f"{var_name}-{period}",
        var_name,
    ]:
        if key_pattern in trace_data:
            entry = trace_data[key_pattern]
            value = entry.get("output_value") or entry.get("value") or entry.get("output")
            if isinstance(value, list) and len(value) == 1:
                return value[0]
            return value

    # Fallback: look in the calculate result if present
    result = trace.get("result") or trace.get("calculate")
    if result and isinstance(result, dict):
        for entity_group, instances in result.items():
            if isinstance(instances, dict) and instance_id in instances:
                var_data = instances[instance_id].get(var_name, {})
                if isinstance(var_data, dict) and period in var_data:
                    return var_data[period]

    return "???"  # Could not find — user must fill in


def _build_yaml_test(
    name: str,
    situation: dict[str, Any],
    inputs: dict,
    outputs: dict,
    trace: dict[str, Any],
    law_reference: str | None = None,
) -> str:
    """Build a YAML test string in OpenFisca format."""
    lines = []
    lines.append(f"- name: {name}")

    if law_reference:
        lines.append(f"  # Source: {law_reference}")

    # --- period ---
    # Detect the main period from outputs
    periods = {k[3] for k in outputs}
    main_period = next(iter(periods)) if periods else "2024-01"
    lines.append(f"  period: {main_period}")

    # --- input ---
    lines.append("  input:")

    # Group inputs by entity_group → instance_id
    by_entity: dict[str, dict[str, dict]] = {}
    for (entity_group, instance_id, var_name, period), value in inputs.items():
        by_entity.setdefault(entity_group, {}).setdefault(instance_id, {})[var_name] = (value, period)

    for entity_group, instances in (situation.items()):
        if not isinstance(instances, dict):
            continue
        # Only emit entity groups that have inputs
        entity_inputs = by_entity.get(entity_group, {})
        has_roles = any(
            isinstance(v, list)
            for inst in instances.values()
            if isinstance(inst, dict)
            for v in inst.values()
        )
        if not entity_inputs and not has_roles:
            continue

        lines.append(f"    {entity_group}:")
        for instance_id, instance_data in instances.items():
            if not isinstance(instance_data, dict):
                continue
            lines.append(f"      {instance_id}:")
            # Roles first
            for k, v in instance_data.items():
                if isinstance(v, list):
                    lines.append(f"        {k}: {json.dumps(v)}")
            # Input variables
            instance_vars = entity_inputs.get(instance_id, {})
            for var_name, (value, period) in instance_vars.items():
                lines.append(f"        {var_name}: {value}")

    # --- output ---
    lines.append("  output:")

    by_entity_out: dict[str, dict[str, dict]] = {}
    for (entity_group, instance_id, var_name, period), value in outputs.items():
        by_entity_out.setdefault(entity_group, {}).setdefault(instance_id, {})[var_name] = value

    for entity_group, instances in by_entity_out.items():
        lines.append(f"    {entity_group}:")
        for instance_id, vars_out in instances.items():
            lines.append(f"      {instance_id}:")
            for var_name, value in vars_out.items():
                lines.append(f"        {var_name}: {value}")

    # --- trace summary as comment ---
    trace_data = trace.get("trace", {})
    if trace_data:
        lines.append("")
        lines.append("  # --- Trace (intermediate values for documentation) ---")
        for trace_key, entry in list(trace_data.items())[:20]:  # cap at 20 lines
            val = entry.get("output_value") or entry.get("value", "?")
            if isinstance(val, list) and len(val) == 1:
                val = val[0]
            lines.append(f"  # {trace_key}: {val}")

    return "\n".join(lines) + "\n"


def generate_yaml_test(
    trace_response: dict[str, Any],
    name: str = "test_generated",
    law_reference: str | None = None,
) -> str:
    """Generate a YAML test string from a trace_calculation response.

    Args:
        trace_response: Full response from trace_calculation MCP tool.
        name: Test name (snake_case).
        law_reference: Optional legal reference to add as comment.

    Returns:
        YAML string ready to paste into a test file.
    """
    situation = trace_response.get("situation", {})
    if not situation:
        # Try to reconstruct from trace keys
        situation = trace_response.get("request", {}).get("situation", {})

    inputs, outputs = _extract_inputs_outputs(situation, trace_response)
    return _build_yaml_test(name, situation, inputs, outputs, trace_response, law_reference)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an OpenFisca YAML test from a trace_calculation response."
    )
    parser.add_argument("trace_file", help="JSON file containing the trace_calculation response")
    parser.add_argument("--output", "-o", help="Output YAML file (default: stdout)")
    parser.add_argument("--name", "-n", default="test_generated", help="Test name")
    parser.add_argument("--reference", "-r", help="Legal reference to document in the test")
    args = parser.parse_args()

    trace_path = Path(args.trace_file)
    if not trace_path.exists():
        print(f"File not found: {trace_path}", file=sys.stderr)
        sys.exit(1)

    with open(trace_path, encoding="utf-8") as f:
        trace_response = json.load(f)

    yaml_str = generate_yaml_test(
        trace_response,
        name=args.name,
        law_reference=args.reference,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(yaml_str, encoding="utf-8")
        print(f"Test written to {output_path}")
    else:
        print(yaml_str)


if __name__ == "__main__":
    main()
