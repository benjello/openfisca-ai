#!/usr/bin/env python3
"""Generate MCP configuration for an OpenFisca country package.

Detects the package structure and writes a `.mcp.json` file that any
MCP-aware agent (Claude Code, Cursor, Gemini, etc.) can use.

Usage:
  openfisca-ai setup-mcp <package-path> [--dry-run] [--force]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def detect_package_name(repo_path: Path) -> str | None:
    """Find the openfisca_* package directory name."""
    for child in repo_path.iterdir():
        if (
            child.is_dir()
            and child.name.startswith("openfisca_")
            and (child / "__init__.py").exists()
        ):
            return child.name
    return None


def generate_mcp_config(repo_path: Path) -> dict:
    """Generate .mcp.json content for the given repo."""
    package_name = detect_package_name(repo_path)
    if not package_name:
        raise ValueError(f"No openfisca_* package found in {repo_path}")

    repo_str = str(repo_path.resolve())

    return {
        "mcpServers": {
            "openfisca": {
                "command": "uv",
                "args": [
                    "run", "openfisca-ai", "mcp",
                    "--url", "http://localhost:5000",
                    "--serve",
                    "--serve-command", f"uv run openfisca serve --country-package {package_name}",
                    "--repo-path", repo_str,
                ],
            },
        },
    }


def setup_mcp(repo_path: Path, *, dry_run: bool = False, force: bool = False) -> dict:
    """Generate and write .mcp.json."""
    config = generate_mcp_config(repo_path)
    target = repo_path / ".mcp.json"

    if target.exists() and not force:
        return {
            "status": "skipped",
            "path": str(target),
            "reason": "file exists, use --force to overwrite",
            "config": config,
        }

    if dry_run:
        return {
            "status": "dry_run",
            "path": str(target),
            "config": config,
        }

    target.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "written",
        "path": str(target),
        "config": config,
    }


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: openfisca-ai setup-mcp <package-path> [--dry-run] [--force]")
        sys.exit(1)

    repo_path = Path(args[0])
    if not repo_path.exists():
        print(f"Path not found: {repo_path}")
        sys.exit(1)

    dry_run = "--dry-run" in args
    force = "--force" in args

    try:
        result = setup_mcp(repo_path, dry_run=dry_run, force=force)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    package_name = detect_package_name(repo_path)
    print(f"Package: {package_name}")
    print(f"Status: {result['status']}")
    print(f"Path: {result['path']}")

    if result["status"] == "skipped":
        print(f"Reason: {result['reason']}")

    print(f"\nMCP config:")
    print(json.dumps(result["config"], indent=2, ensure_ascii=False))

    print(f"\nTools disponibles via MCP :")
    print(f"  Métier (sans serveur OpenFisca) :")
    print(f"    - review_diff     : pré-digère un diff pour review LLM (~500 tok vs ~5k)")
    print(f"    - audit_package   : audit complet du package")
    print(f"  Calcul (nécessite openfisca serve) :")
    print(f"    - calculate       : calcul de variables")
    print(f"    - trace_calculation : trace complète avec dépendances")
    print(f"    - describe_variable, get_parameter, search_variables, ...")
    print(f"\nCompatible avec : Claude Code, Cursor, Gemini, Antigravity, etc.")


if __name__ == "__main__":
    main()
