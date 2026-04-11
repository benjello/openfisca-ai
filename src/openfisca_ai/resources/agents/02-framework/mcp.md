# MCP server — live access to a target OpenFisca system

The openfisca-ai MCP server wraps a running OpenFisca Web API
(`openfisca serve`) and exposes its system as a set of MCP tools an agent
can call directly. This guide is the **single source of truth** for the MCP
surface — other docs should reference this guide instead of duplicating tool
descriptions.

## Why this matters

Without MCP an agent has to read Python files, walk YAML hierarchies, and
mentally simulate formulas to understand a system. With MCP it asks targeted
questions and gets structured answers grounded in the real system. The token
savings come from **less context the agent has to ingest**, not from "fewer
tool calls".

## Starting the server

```bash
# Start the OpenFisca Web API and the MCP server in one command
uv run openfisca-ai mcp --serve

# Custom serve command (typical for a country package)
uv run openfisca-ai mcp --serve \
  --serve-command "uv run openfisca serve --country-package openfisca_paris_rh"

# If the API is already running elsewhere
uv run openfisca-ai mcp --url http://localhost:5000
```

In a Claude Code project, declare it once in `.mcp.json` and the assistant
picks it up automatically:

```json
{
  "mcpServers": {
    "openfisca": {
      "command": "uv",
      "args": [
        "run", "openfisca-ai", "mcp",
        "--serve",
        "--serve-command", "uv run openfisca serve --country-package openfisca_<country>"
      ]
    }
  }
}
```

### Startup cost

`openfisca serve` loads the entire country package into memory before the
API answers — typically **5–10 seconds** the first time, sometimes longer
for big packages. Once loaded, every MCP call is sub-second.

Practical implication: MCP pays off as soon as a session involves more than
3–4 calls. For a single one-shot check, the static tools (`audit`,
`validate-*`) are usually faster end-to-end because they have no startup
cost.

## Tools exposed

| Tool | Purpose | Typical inputs |
|---|---|---|
| `list_entities` | Discover entity types and roles | — |
| `list_variables` | List variables, optionally filtered by entity | `entity?` |
| `search_variables` | Keyword search across names and descriptions | `query`, `entity?` |
| `describe_variable` | Entity, period, formula, references for one variable | `variable_name` |
| `list_parameters` | List all parameters | — |
| `get_parameter` | Values and full historical dates of one parameter | `parameter_id` |
| `validate_situation` | Structural validation before computing | `situation` |
| `calculate` | Compute variables for a situation | `situation` |
| `trace_calculation` | Compute + return the full dependency tree and intermediate values | `situation` |

The canonical implementation lives in `src/openfisca_ai/mcp/server.py`. If a
tool's behavior here disagrees with that file, the file wins — please update
this guide.

## When to use MCP — by task, not by rigid order

The "static tools first, MCP second" rule is too coarse. Use this table
instead:

| Task | Recommended approach | Why |
|---|---|---|
| Audit / review existing code | **Static first** (`audit`, `validate-*`), MCP for the suspects | You don't know yet where issues are; static gives you a punch list cheaply |
| Implement a new variable | **MCP first** (`search_variables`, `describe_variable`, `get_parameter`), then static at the end | One MCP call replaces grepping and reading 5 Python files; static validates the result |
| Generate a YAML test | **MCP only** (`trace_calculation` → `generate-test-from-trace`) | Hand-computing expected values is the most token-expensive thing an agent can do |
| Debug a wrong calculation | **MCP only** (`trace_calculation`) | The trace tells you exactly which intermediate or parameter is wrong |
| CI / cold-start one-shot check | **Static only** | No running API, no startup cost, free, fast |
| Inspect parameter history | **MCP** (`get_parameter`) | Reading YAML files manually is slower and error-prone for date-based history |

## Test generation workflow

`trace_calculation` returns the full dependency tree with computed values.
`openfisca-ai generate-test-from-trace` converts that response into a
ready-to-use YAML test:

- inputs you provided → test inputs
- variables that were `null` → expected outputs grounded in the live calculation
- intermediate values → comments for traceability

You can either save the trace to a file and pass it as an argument:

```bash
uv run openfisca-ai generate-test-from-trace trace.json \
  --name test_my_variable \
  --reference "Article 12 du décret 2024-XXX" \
  --output tests/test_my_variable.yaml
```

…or pipe it directly from stdin (use `-` as the path):

```bash
# in an interactive shell
cat trace.json | uv run openfisca-ai generate-test-from-trace - \
  --name test_my_variable \
  --output tests/test_my_variable.yaml
```

The stdin form removes the need for an intermediate file when an agent
already has the trace JSON in hand.

## Connecting to Claude Code (and other MCP clients)

A `.mcp.json` at the project root is enough — Claude Code auto-discovers it.
Other MCP-aware clients use the same JSON format. The MCP server runs on
stdio, so no port allocation is needed for the server itself; only the
underlying `openfisca serve` API binds a TCP port (default `5000`).

## Notes

- The MCP server is a thin wrapper around the OpenFisca Web API — anything
  the API can answer is reachable through MCP, and vice-versa.
- `validate_situation` catches structural errors (unknown entity, unknown
  variable, missing person id) before calling the API, so it's cheaper than
  a failed `calculate`.
- `trace_calculation` is the most useful tool by far — get used to it
  before reaching for the others.
