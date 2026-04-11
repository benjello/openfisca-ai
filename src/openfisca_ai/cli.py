#!/usr/bin/env python3
"""CLI for openfisca-ai."""

import json
import importlib.util
import sys
from pathlib import Path

from openfisca_ai.core.scaffold_report import (
    render_scaffold_report_markdown,
    render_scaffold_report_text,
)


GUIDE_SUBCOMMANDS = {"list", "show", "cat", "path"}


TOOL_COMMANDS = {
    "audit": "audit_country_package.py",
    "check-all": "audit_country_package.py",
    "check-package-baseline": "check_package_baseline.py",
    "check-tooling": "check_tooling.py",
    "extract-patterns": "extract_patterns.py",
    "suggest-units": "suggest_units.py",
    "validate-code": "validate_code.py",
    "validate-parameters": "validate_parameters.py",
    "validate-tests": "validate_tests.py",
    "validate-units": "validate_units.py",
}


def _repo_root() -> Path:
    """Return the repository root from the installed source tree."""
    return Path(__file__).resolve().parents[2]


def _load_tool_module(filename: str):
    """Load a tool module from the repository tools/ directory."""
    module_path = _repo_root() / "tools" / filename
    if not module_path.exists():
        raise FileNotFoundError(f"Tool module not found: {module_path}")

    module_name = f"openfisca_ai_cli_{module_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _print_usage(stream):
    """Print CLI usage."""
    print("Usage:", file=stream)
    print("  openfisca-ai run <task.json>", file=stream)
    print("  openfisca-ai scaffold <task.json>", file=stream)
    print("  openfisca-ai scaffold-apply <task.json>", file=stream)
    print("  openfisca-ai audit <package-path> [--json|--markdown] [--output FILE]", file=stream)
    print("  openfisca-ai check-all <package-path> [--json|--markdown] [--output FILE]", file=stream)
    print("  openfisca-ai extract-patterns <package-path> [--json]", file=stream)
    print("  openfisca-ai check-package-baseline <package-path>", file=stream)
    print("  openfisca-ai check-tooling <package-path>", file=stream)
    print("  openfisca-ai validate-code <package-path>", file=stream)
    print("  openfisca-ai validate-tests <package-path>", file=stream)
    print("  openfisca-ai validate-parameters <package-path>", file=stream)
    print("  openfisca-ai validate-units <package-path>", file=stream)
    print("  openfisca-ai suggest-units <package-path> [--apply]", file=stream)
    print("  openfisca-ai guide list", file=stream)
    print("  openfisca-ai guide show <name>", file=stream)
    print("  openfisca-ai guide cat <name>", file=stream)
    print("  openfisca-ai guide path", file=stream)


def _render_task_report(result: dict, report_format: str) -> str:
    """Render a human-readable scaffold report."""
    normalized = report_format.strip().lower()
    if normalized == "markdown":
        return render_scaffold_report_markdown(result)
    if normalized == "text":
        return render_scaffold_report_text(result)
    raise ValueError(f"Unsupported report_format: {report_format}")


def _run_task_command(args: list[str], command: str = "run") -> int:
    """Run the existing pipeline task command."""
    if len(args) < 2:
        print("Usage: openfisca-ai run|scaffold|scaffold-apply <task.json>", file=sys.stderr)
        return 1

    task_path = Path(args[1])
    if not task_path.exists():
        print(f"Task file not found: {task_path}", file=sys.stderr)
        return 1

    with open(task_path, encoding="utf-8") as f:
        task = json.load(f)

    pipeline_name = task.get("pipeline", "law_to_code")
    country_id = task.get("country")
    inputs = task.get("inputs", {})
    options = task.get("options", {})

    if pipeline_name == "law_to_code":
        from openfisca_ai.pipelines.law_to_code import run_law_to_code
        law_text = inputs.get("law_text", "")
        extracted_data = inputs.get("extracted")
        use_ref = options.get("use_existing_code_as_reference", bool(country_id))
        include_reference_audit_summary = options.get("include_reference_audit_summary", False)
        output_dir = options.get("output_dir")
        if output_dir:
            output_dir = str((task_path.parent / output_dir).resolve())
        apply_artifacts_to_reference_package = options.get(
            "apply_artifacts_to_reference_package",
            False,
        )
        overwrite_artifacts = options.get("overwrite_artifacts", False)
        default_plan_only = command == "scaffold"
        plan_only = options.get("plan_only", default_plan_only)
        if command == "scaffold-apply":
            plan_only = options.get("plan_only", False)
            if not output_dir and not apply_artifacts_to_reference_package and country_id:
                apply_artifacts_to_reference_package = True
        report_path = options.get("report_path")
        if report_path:
            report_path = str((task_path.parent / report_path).resolve())
        report_format = options.get("report_format", "markdown")
        existing_artifact_strategy = options.get("existing_artifact_strategy")
        if existing_artifact_strategy is None:
            existing_artifact_strategy = "update" if overwrite_artifacts else "create"
        if command == "scaffold-apply" and not (output_dir or apply_artifacts_to_reference_package):
            print(
                "scaffold-apply requires either options.output_dir or a configured "
                "country reference package.",
                file=sys.stderr,
            )
            return 1
        try:
            result = run_law_to_code(
                law_text,
                country_id=country_id,
                use_existing_code_as_reference=use_ref,
                include_reference_audit_summary=include_reference_audit_summary,
                extracted_data=extracted_data,
                artifacts_output_dir=output_dir,
                apply_artifacts_to_reference_package=apply_artifacts_to_reference_package,
                existing_artifact_strategy=existing_artifact_strategy,
                overwrite_artifacts=overwrite_artifacts,
                plan_only=plan_only,
            )
            if report_path:
                rendered_report = _render_task_report(result, report_format)
                report_file = Path(report_path)
                report_file.parent.mkdir(parents=True, exist_ok=True)
                report_file.write_text(rendered_report, encoding="utf-8")
                result["report_path"] = str(report_file)
                result["report_format"] = report_format
        except Exception as exc:
            print(f"Pipeline failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print(f"Unknown pipeline: {pipeline_name}", file=sys.stderr)
    return 1


def _run_tool_command(command: str, args: list[str]) -> int:
    """Delegate a CLI subcommand to a tool module main() function."""
    filename = TOOL_COMMANDS[command]
    try:
        module = _load_tool_module(filename)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    old_argv = sys.argv
    sys.argv = [filename, *args[1:]]
    try:
        module.main()
        return 0
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        return 1
    finally:
        sys.argv = old_argv


def _run_guide_command(args: list[str]) -> int:
    """Discover, locate and read methodology guides packaged with openfisca-ai."""
    from openfisca_ai.guide import (
        list_guides,
        read_guide,
        resolve_guide,
        guide_resource_path,
        overlay_path,
        resources_root_path,
    )

    if len(args) < 2 or args[1] not in GUIDE_SUBCOMMANDS:
        print(
            "Usage: openfisca-ai guide {list|show|cat|path} [name]",
            file=sys.stderr,
        )
        return 1

    sub = args[1]

    if sub == "list":
        guides = list_guides()
        if not guides:
            print("No guides found.", file=sys.stderr)
            return 1
        width = max(len(g.name) for g in guides)
        for guide in guides:
            print(f"{guide.name.ljust(width)}  {guide.relative_path}")
        return 0

    if sub == "path":
        print(resources_root_path())
        return 0

    if len(args) < 3:
        print(f"Usage: openfisca-ai guide {sub} <name>", file=sys.stderr)
        return 1

    name = args[2]
    try:
        guide = resolve_guide(name)
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if sub == "show":
        base = guide_resource_path(guide)
        print(base)
        overlay = overlay_path(guide)
        if overlay.is_file():
            print(f"overlay: {overlay}")
        return 0

    if sub == "cat":
        try:
            print(read_guide(name))
        except LookupError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        return 0

    return 1


def main(argv: list[str] | None = None) -> int:
    """Entry point for the openfisca-ai command."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        _print_usage(sys.stderr)
        return 1

    command = args[0]
    if command in {"run", "scaffold", "scaffold-apply"}:
        return _run_task_command(args, command=command)

    if command == "guide":
        return _run_guide_command(args)

    if command in TOOL_COMMANDS:  # noqa: RET505
        return _run_tool_command(command, args)

    _print_usage(sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
