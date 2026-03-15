# Country configs

One YAML file per country (in `config/countries/`). The pipeline merges them with **your local paths** from a user config file that is **not committed** (see below).

See [country-config.md](../../docs/agents/02-framework/country-config.md) for the current configuration model.

## Your local paths (user config, gitignored)

So that each developer keeps their own paths without committing them:

1. Copy the example: `cp config/user.example.yaml config/user.yaml`
2. Edit `config/user.yaml` and set your paths under `countries.<country_id>`:
   - `existing_code.path`
   - `legislative_sources.root`
3. `config/user.yaml` is in `.gitignore` — it stays local.

Paths in `user.yaml` override those in `config/countries/<id>.yaml`. You can also use a global file: `~/.config/openfisca-ai/user.yaml` (canonical) or `~/.config/openfisca-ai/config.yaml` (legacy). The repo-level `config/user.yaml` takes precedence if it exists.

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
