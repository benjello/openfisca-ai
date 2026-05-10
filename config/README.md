# Config

- **`countries/`** — One YAML per country (committed). Structure, repo URLs, conventions.
- **`user.yaml.template`** — Canonical template for local path overrides. Copy to **`user.yaml`** and fill in; `user.yaml` is gitignored and overrides paths in `countries/*.yaml`.
- **`user.example.yaml`** — Minimal example of the same canonical schema.

The local user config can also describe agent targets under
`countries.<id>.agent`. This keeps country-specific launcher information close
to the OpenFisca country config without committing personal paths.

```yaml
agent_worktree_base: ${base_path}/.agent-worktrees

countries:
  france:
    existing_code:
      path: ${base_path}/openfisca-france
    agent:
      aliases: [openfisca-france]
      main_repo: openfisca-france
      repos:
        openfisca-france:
          path: ${base_path}/openfisca-france
          mode: rw
        openfisca-core:
          path: ${base_path}/openfisca-core
          mode: ro
        openfisca-survey-manager:
          path: ${base_path}/openfisca-survey-manager
          mode: worktree
```

Resolve these targets with:

```bash
uv run openfisca-ai target list
uv run openfisca-ai target resolve france
uv run openfisca-ai target doctor france
```

Add `--json` when a machine-readable JSON payload is required.
`target doctor` exits with an error if required local paths are missing.

See **`countries/README.md`** for setup (Tunisia first, then more countries).
