# Country workflow: one country first, then more
# Country workflow: one country first, then more

This doc describes how to use openfisca-ai with **one country** (legislative sources + existing code), then add more countries without changing the framework.

## Idea

- You have **legislative sources** (laws, decrees, manuals) and **existing OpenFisca code** for a first country.
- The framework stays **country-agnostic**: each country is a config + optional task set.
- Agents and pipelines use **country config** to find sources and reference code; adding a new country = adding a new config (and optionally tasks).

## Directory layout (suggestion)

```
openfisca-ai/
├── config/
│   └── countries/
│       ├── _schema.yaml      # optional: schema for country configs
│       ├── tunisia.yaml     # first country
│       └── france.yaml      # later
├── tasks/
│   ├── example_task.json
│   └── countries/
│       ├── tunisia/
│       │   ├── encode_plafond_secu.json
│       │   └── validate_ir.yaml
│       └── france/
│           └── ...
└── ...
```

Your **legislative sources** and **existing code** can live outside the repo (paths in config) or be cloned/linked under a `sources/` or `repos/` tree; the config just points to them.

## Country config

Each country has a small config file (e.g. `config/countries/tunisia.yaml`) that defines:

- **Country id and label** (for logs and UI).
- **Paths to legislative sources** (directory of markdown/PDF/text, or list of files). Optional: rules for “authoritative” vs “supporting” docs.
- **Path to existing OpenFisca code** (repo or directory). Used as reference by the coder (and later by validators).
- Optional **conventions**: parameter hierarchy, naming (e.g. `snake_case`), entity levels (Person, Famille, Foyer, etc.), so agents stay consistent when you add more countries.

Example (YAML):

```yaml
# config/countries/tunisia.yaml
id: tunisia
label: Tunisia

# Where to find legislative / regulatory sources (your existing docs)
legislative_sources:
  root: /path/to/tunisia-law-docs   # or a list of paths
  # optional: file_pattern: "*.md"
  # optional: index_file: sources.md

# Existing OpenFisca code for this country (reference for coder and validators)
existing_code:
  path: /path/to/openfisca-tunisia
  # optional: main_package: openfisca_tunisia

# Optional: conventions for this country (extensible)
conventions:
  parameter_hierarchy: [gov, social_security, ...]
  entity_levels: [Person, Famille, Foyer]
  # naming: snake_case
```

For a **first country**, you only need one such file. For a **second country**, add another file (e.g. `france.yaml`) and point to that country’s sources and code; no change to the core framework.

## Task format with country

Tasks can reference a country so the pipeline knows which sources and code to use.

Example task that uses Tunisia config and your existing code as reference:

```json
{
  "id": "encode_plafond_secu",
  "country": "tunisia",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 – Le plafond de la Sécurité sociale est fixé à 3 666 € pour 2024.",
    "reference_code_path": null
  },
  "options": {
    "use_existing_code_as_reference": true
  }
}
```

- `country` is the key in `config/countries/<country>.yaml` (e.g. `tunisia`).
- The pipeline (or orchestrator) loads that config, resolves `legislative_sources.root` and `existing_code.path`, and passes them to the agents (e.g. extractor gets law from sources or from `law_text`, coder gets `reference_code_path` from config when `use_existing_code_as_reference` is true).

So: **one country** = one config + tasks under `tasks/countries/<country>/`; **more countries** = more configs and more task folders.

## Minimal workflow (one country)

1. **Add country config**
   Create `config/countries/<country>.yaml` with paths to your legislative sources and existing code.

2. **Document collector (optional)**
   If your sources are already in files, you can skip a “collector” and point `legislative_sources` at them. If you want an agent to fetch/normalise docs later, it can read this config to know where to write.

3. **Extractor**
   Input: law text (from task or from files under `legislative_sources`). Output: structured extracted data (provisions, parameters, variables). Same agent for every country; country-specific behaviour can come from conventions in config.

4. **Coder**
   Input: extracted data + optional reference code (from `existing_code.path` for the task’s country). Output: new or updated OpenFisca code. For the first country, “reference” is your existing code; for a new country, reference can be another country’s code or none.

5. **Later: validators, tests, CI**
   Same idea: validators and test-creators take `country` from the task and load that country’s config (and existing code) so they stay consistent and reusable across countries.

## Summary

- **One country:** one `config/countries/<id>.yaml` with `legislative_sources` and `existing_code.path`; tasks with `"country": "<id>"`; pipeline uses config to find sources and reference code.
- **More countries:** add another YAML and optional tasks; no change to agents or pipeline logic, only to config and task data.
- Your **legislative sources** and **existing code** are the inputs; the framework just needs their paths and a small convention block so it stays reusable.
