# Country configs

One YAML file per country (in `config/countries/`). The pipeline merges them with **your local paths** from a user config file that is **not committed** (see below).

See `uv run openfisca-ai guide cat country-config` for the current configuration model.

## Your local paths (user config, gitignored)

So that each developer keeps their own paths without committing them:

1. Copy the example: `cp config/user.example.yaml config/user.yaml`
2. Edit `config/user.yaml` and set your paths under `countries.<country_id>`:
   - `existing_code.path`
   - `legislative_sources.root`
3. `config/user.yaml` is in `.gitignore` — it stays local.

Paths in `user.yaml` override those in `config/countries/<id>.yaml`. You can also use a global file: `~/.config/openfisca-ai/user.yaml` (canonical) or `~/.config/openfisca-ai/config.yaml` (legacy). The repo-level `config/user.yaml` takes precedence if it exists.

## Agent targets

When using local coding agents, keep target-specific repo wiring in the same
local user config:

```yaml
agent_worktree_base: ${base_path}/.agent-worktrees

countries:
  tunisia:
    existing_code:
      path: ${base_path}/openfisca-tunisia
    agent:
      aliases:
        - tunisie
        - openfisca-tunisia
      main_repo: openfisca-tunisia
      repos:
        openfisca-tunisia:
          path: ${base_path}/openfisca-tunisia
          mode: rw
        openfisca-core:
          path: ${base_path}/openfisca-core
          mode: ro
        openfisca-survey-manager:
          path: ${base_path}/openfisca-survey-manager
          mode: worktree
```

Repo modes are local workflow hints for launchers:

- `rw`: use the existing checkout as writable.
- `ro`: expose the repo as reference-only.
- `worktree`: create a target-specific Git worktree before editing.

Inspect the normalized target with:

```bash
uv run openfisca-ai target show tunisie
uv run openfisca-ai target resolve tunisie
uv run openfisca-ai target doctor tunisie
```

Add `--json` when a machine-readable JSON payload is required.
`target doctor` exits with an error if required local paths are missing.

## Tunisia (first country)

Existing code: **[openfisca/openfisca-tunisia](https://github.com/openfisca/openfisca-tunisia)** on GitHub.

1. Clone the repo: `git clone https://github.com/openfisca/openfisca-tunisia ../openfisca-tunisia` (or anywhere you like).
2. Create your user config and set paths (so they are not committed):
   ```bash
   cp config/user.example.yaml config/user.yaml
   # Edit config/user.yaml:
   # countries.tunisia.legislative_sources.root = /path/to/laws
   # countries.tunisia.existing_code.path = /path/to/openfisca-tunisia
   ```
3. Run: `uv run openfisca-ai run tasks/countries/tunisia/example_law_to_code.json`

## Adding another country

1. Copy `_example.yaml` to `<country_id>.yaml` (e.g. `france.yaml`).
2. Set `legislative_sources.root` and `existing_code.path` (and optional `existing_code.repo_url`).
3. Add tasks under `tasks/countries/<country_id>/` if needed.
