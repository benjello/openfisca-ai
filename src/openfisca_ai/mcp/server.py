"""OpenFisca MCP Server.

Provides MCP tools for interacting with OpenFisca tax-benefit systems.
Connect to any running OpenFisca Web API (openfisca serve).

Usage:
    openfisca-ai mcp [--url http://localhost:5000]
    OPENFISCA_API_URL=http://localhost:5000 openfisca-ai mcp
"""

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import OpenFiscaClient
from .errors import MCPError, ValidationError

server = Server("openfisca-mcp")
client = OpenFiscaClient()


def format_result(data: Any) -> list[TextContent]:
    if isinstance(data, dict):
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    return [TextContent(type="text", text=str(data))]


def format_error(error: MCPError) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(error.to_dict(), indent=2))]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_entities",
            description="List all entity types (person, household, etc.) and their roles. Use before constructing a situation.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="list_variables",
            description="List all variables, optionally filtered by entity. Entry point for discovery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity": {"type": "string", "description": "Filter by entity type"},
                },
                "required": [],
            },
        ),
        Tool(
            name="describe_variable",
            description=(
                "Get full details about a variable: valueType, definitionPeriod, entity, "
                "description, formulas, legislative references. "
                "IMPORTANT: definitionPeriod tells you the period format to use in situations "
                "(MONTH→'YYYY-MM', YEAR→'YYYY', DAY→'YYYY-MM-DD', ETERNITY→'ETERNITY')."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "variable_name": {"type": "string", "description": "Variable name"},
                },
                "required": ["variable_name"],
            },
        ),
        Tool(
            name="list_parameters",
            description="List all parameters (rates, thresholds, amounts). Use get_parameter for historical values.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_parameter",
            description="Get a parameter's values and full history across dates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "parameter_id": {"type": "string", "description": "Parameter ID (e.g. 'fonction_publique.valeur_point_indice')"},
                },
                "required": ["parameter_id"],
            },
        ),
        Tool(
            name="search_variables",
            description="Search variables by keyword in names and descriptions. Use when you don't know the exact name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term"},
                    "entity": {"type": "string", "description": "Filter by entity (optional)"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="calculate",
            description=(
                "Compute variable values for a situation. Set variable to null to request calculation.\n"
                "Structure: {\"persons\": {\"id\": {\"var\": {\"period\": value_or_null}}}, "
                "\"households\": {\"id\": {\"adults\": [\"id\"], \"var\": {\"period\": null}}}}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "situation": {"type": "object", "description": "Situation JSON"},
                },
                "required": ["situation"],
            },
        ),
        Tool(
            name="trace_calculation",
            description=(
                "Calculate with full dependency trace: which variables were computed, "
                "what each depended on, what parameter values were used. "
                "Use to explain WHY a result was reached, or to generate test fixtures."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "situation": {"type": "object", "description": "Situation JSON"},
                },
                "required": ["situation"],
            },
        ),
        Tool(
            name="validate_situation",
            description="Validate a situation structure without calculating. Catches entity/variable/period errors before running.",
            inputSchema={
                "type": "object",
                "properties": {
                    "situation": {"type": "object", "description": "Situation JSON to validate"},
                },
                "required": ["situation"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        match name:
            case "list_entities":
                return format_result(client.get_entities())
            case "list_variables":
                return await _list_variables(arguments.get("entity"))
            case "describe_variable":
                return format_result(client.get_variable(arguments["variable_name"]))
            case "list_parameters":
                return format_result(client.get_parameters())
            case "get_parameter":
                return format_result(client.get_parameter(arguments["parameter_id"]))
            case "search_variables":
                return await _search_variables(arguments["query"], arguments.get("entity"))
            case "calculate":
                return format_result(client.calculate(arguments["situation"]))
            case "trace_calculation":
                return format_result(client.trace(arguments["situation"]))
            case "validate_situation":
                return await _validate_situation(arguments["situation"])
            case _:
                raise ValidationError(f"Unknown tool: {name}")
    except MCPError as e:
        return format_error(e)
    except Exception as e:
        return format_error(MCPError("internal_error", str(e), 500))


async def _list_variables(entity: str | None) -> list[TextContent]:
    data = client.get_variables()
    if entity:
        filtered = {}
        for var_name, var_info in data.items():
            try:
                if client.get_variable(var_name).get("entity") == entity:
                    filtered[var_name] = var_info
            except Exception:
                continue
        data = filtered
    return format_result(data)


async def _search_variables(query: str, entity: str | None) -> list[TextContent]:
    all_vars = client.get_variables()
    query_lower = query.lower()
    matches = {}

    for var_name, var_info in all_vars.items():
        if query_lower in var_name.lower() or query_lower in var_info.get("description", "").lower():
            if entity:
                try:
                    if client.get_variable(var_name).get("entity") != entity:
                        continue
                except Exception:
                    continue
            matches[var_name] = var_info

    if not matches:
        return format_result({
            "message": f"No variables found matching '{query}'",
            "suggestions": ["Try a different term", "Use list_variables to see all"],
        })
    return format_result(matches)


async def _validate_situation(situation: dict[str, Any]) -> list[TextContent]:
    if not situation:
        raise ValidationError("Situation is required")

    errors = []
    entities = client.get_entities()
    all_vars = client.get_variables()

    valid_plurals = {e["plural"] for e in entities.values()} | set(entities.keys())
    for key in situation:
        if key not in valid_plurals:
            errors.append(f"Unknown entity type: '{key}'")

    persons = situation.get("persons", {})
    if not persons:
        errors.append("At least one person must be defined")

    for person_id, person_data in persons.items():
        for var_name in person_data:
            if var_name not in all_vars:
                errors.append(f"Unknown variable '{var_name}' for person '{person_id}'")

    for entity_key, entity_info in entities.items():
        if "roles" not in entity_info:
            continue
        entity_plural = entity_info["plural"]
        role_keys = set(entity_info["roles"].keys())
        for instance_id, instance_data in situation.get(entity_plural, {}).items():
            for key, value in instance_data.items():
                if key in role_keys:
                    for pid in (value if isinstance(value, list) else []):
                        if pid not in persons:
                            errors.append(f"Person '{pid}' in {entity_plural}/{instance_id}/{key} not defined")
                elif key not in all_vars:
                    errors.append(f"Unknown variable '{key}' for {entity_plural} '{instance_id}'")

    if errors:
        return format_result({"valid": False, "errors": errors})
    return format_result({"valid": True, "message": "Situation is valid"})


async def _main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def _start_openfisca_serve(command: list[str], url: str, timeout: int = 30) -> Any:
    """Start openfisca serve as a subprocess and wait until it responds."""
    import subprocess
    import sys
    import time

    proc = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=sys.stderr,
    )

    # Poll until the API responds or timeout
    import httpx
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            httpx.get(f"{url}/entities", timeout=2.0)
            return proc  # server is up
        except Exception:
            if proc.poll() is not None:
                raise RuntimeError(f"openfisca serve exited with code {proc.returncode}")
            time.sleep(0.5)

    proc.terminate()
    raise RuntimeError(f"openfisca serve did not respond within {timeout}s at {url}")


def run(url: str | None = None, serve: bool = False, serve_command: list[str] | None = None):
    """Entry point. url overrides OPENFISCA_API_URL env var.

    Args:
        url: OpenFisca API URL (default: http://localhost:5000).
        serve: If True, start `openfisca serve` as a subprocess before starting the MCP server.
               The subprocess is terminated automatically when the MCP server exits.
        serve_command: Custom serve command. Defaults to ["openfisca", "serve"].
    """
    import asyncio
    import atexit
    import os
    import subprocess

    if url:
        os.environ["OPENFISCA_API_URL"] = url

    api_url = os.environ.get("OPENFISCA_API_URL", "http://localhost:5000")

    _proc: subprocess.Popen | None = None

    if serve:
        cmd = serve_command or ["openfisca", "serve"]
        _proc = _start_openfisca_serve(cmd, api_url)

        def _cleanup():
            if _proc and _proc.poll() is None:
                _proc.terminate()
                try:
                    _proc.wait(timeout=5)
                except Exception:
                    _proc.kill()

        atexit.register(_cleanup)

    asyncio.run(_main())
