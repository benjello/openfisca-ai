#!/usr/bin/env python3
"""CLI for openfisca-ai."""

import json
import sys
from pathlib import Path


def main():
    """Entry point for the openfisca-ai command."""
    args = sys.argv[1:]
    if not args or args[0] != "run":
        print("Usage: openfisca-ai run <task.json>", file=sys.stderr)
        sys.exit(1)

    task_path = Path(args[1])
    if not task_path.exists():
        print(f"Task file not found: {task_path}", file=sys.stderr)
        sys.exit(1)

    with open(task_path) as f:
        task = json.load(f)

    pipeline_name = task.get("pipeline", "law_to_code")
    country_id = task.get("country")
    inputs = task.get("inputs", {})
    options = task.get("options", {})

    if pipeline_name == "law_to_code":
        from openfisca_ai.pipelines.law_to_code import run_law_to_code
        law_text = inputs.get("law_text", "")
        use_ref = options.get("use_existing_code_as_reference", bool(country_id))
        result = run_law_to_code(
            law_text,
            country_id=country_id,
            use_existing_code_as_reference=use_ref,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown pipeline: {pipeline_name}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
