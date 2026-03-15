# Config

- **`countries/`** — One YAML per country (committed). Structure, repo URLs, conventions.
- **`user.yaml.template`** — Canonical template for local path overrides. Copy to **`user.yaml`** and fill in; `user.yaml` is gitignored and overrides paths in `countries/*.yaml`.
- **`user.example.yaml`** — Minimal example of the same canonical schema.

See **`countries/README.md`** for setup (Tunisia first, then more countries).
