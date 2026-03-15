# Workflows and Pipelines

This file describes the **current** executable workflow and the **target** workflow the repository is designed around.

## Current Executable Workflow

The executable entrypoints currently exposed by the package are:

- `run` and `scaffold` for the alpha `law_to_code` pipeline
- `scaffold-apply` for explicit scaffold writes
- `audit` / `check-all` and validation subcommands for country-package analysis

### What it does today

- loads country config when requested
- instantiates `ExtractorAgent` and `CoderAgent`
- resolves `existing_code.path` when `use_existing_code_as_reference` is enabled
- extracts a compact reference-package pattern summary from the configured country package
- builds an `implementation_brief` from country conventions and observed package patterns
- generates non-destructive scaffolding artifacts when `inputs.extracted` contains structured variables or parameters
- optionally adds an audit summary from the stable validator stack
- returns a dict with `extracted`, `code`, `implementation_brief`, `artifacts`, and optional reference-package metadata

### What it does not do yet

- produce production-ready OpenFisca artifacts
- orchestrate multiple specialized agents
- validate references automatically
- generate tests automatically

See [`src/openfisca_ai/pipelines/law_to_code.py`](../../../src/openfisca_ai/pipelines/law_to_code.py).

### CLI usage

```bash
uv run openfisca-ai run tasks/example_task.json
uv run openfisca-ai scaffold tasks/example_task.json
uv run openfisca-ai scaffold-apply tasks/example_task.json
uv run openfisca-ai check-all /path/to/openfisca-country
```

Behavior summary:

- `run`: generic pipeline entrypoint
- `scaffold`: preview-first scaffold mode
- `scaffold-apply`: explicit write mode, using `options.output_dir` or the configured reference package when a country is set

Task shape:

```json
{
  "id": "encode_ceiling",
  "country": "countria",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Section 1 – The ceiling..."
  },
  "options": {
    "use_existing_code_as_reference": true,
    "include_reference_audit_summary": true
  }
}
```

When a valid `existing_code.path` is configured, the pipeline output can include:

- `implementation_brief`
- `artifacts`
- `reference_code_path`
- `reference_package_analysis.pattern_summary`
- `reference_package_analysis.audit_summary` if `include_reference_audit_summary` is enabled

If `options.output_dir` is set, the pipeline also writes the generated
artifacts to disk and returns:

- `artifacts_output_dir`
- `artifact_write_plan`
- `written_artifacts`

If `options.apply_artifacts_to_reference_package` is set, the pipeline writes
the artifacts to the configured OpenFisca repository behind
`existing_code.path` and returns:

- `reference_package_write_root`
- `artifact_write_plan`
- `written_artifacts`

To get useful scaffolding today, prefer tasks that provide `inputs.extracted`,
for example:

```json
{
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 - Credit rate is 10%.",
    "extracted": {
      "variables": [
        {
          "name": "income_tax_credit",
          "entity": "TaxUnit",
          "definition_period": "YEAR",
          "value_type": "float",
          "base_variable": "taxable_income",
          "parameter": "taxation.income_tax.credit_rate"
        }
      ],
      "parameters": [
        {
          "name": "taxation.income_tax.credit_rate",
          "label": "Income tax credit rate",
          "description": "Rate applied to taxable income.",
          "unit": "/1",
          "value": 0.1
        }
      ]
    }
  },
  "options": {
    "output_dir": "../generated"
  }
}
```

`output_dir` is resolved relative to the task JSON file path. Existing files
are preserved unless `overwrite_artifacts` is explicitly enabled.

If `plan_only` is enabled, the pipeline still returns `artifact_write_plan`
with `diff_preview` entries, but it does not write anything to disk.

Conflict handling is controlled with `existing_artifact_strategy`:

- `create`: fail on existing files
- `skip`: leave existing files unchanged
- `append`: append generated content to existing files
- `update`: replace existing files

To apply artifacts directly in the configured reference package:

```json
{
  "country": "countria",
  "pipeline": "law_to_code",
  "inputs": {
    "law_text": "Article 1 - Surcharge rate is 2%.",
    "extracted": {
      "variables": [
        {
          "name": "income_tax_surcharge",
          "entity": "TaxUnit",
          "definition_period": "YEAR",
          "value_type": "float",
          "domain": "taxation",
          "base_variable": "taxable_income",
          "parameter": "taxation.income_tax.surcharge_rate"
        }
      ]
    }
  },
  "options": {
    "use_existing_code_as_reference": true,
    "apply_artifacts_to_reference_package": true
  }
}
```

This mode is intentionally conservative: it errors on existing files unless
`overwrite_artifacts` is explicitly enabled.

## Reliable Manual Workflow

For actual implementation work today, use this repository as a methodology + validation toolkit:

1. configure the target country with [`country-config.md`](country-config.md)
2. read the relevant role guide in [`roles/`](roles/)
3. inspect the target OpenFisca country package
4. implement parameters, variables, and tests in that package
5. run validation tools from [`tools/`](../../../tools/)
6. run the country package test suite

The quickest entrypoint is now:

```bash
uv run openfisca-ai check-all /path/to/openfisca-country
```

## Conceptual Target Workflow

The long-term design is still:

```text
Legal text
  -> extraction
  -> parameter design
  -> code generation
  -> test generation
  -> validation
```

Use the role guides as design references for these phases:

- [`roles/document-collector.md`](roles/document-collector.md)
- [`roles/parameter-architect.md`](roles/parameter-architect.md)
- [`roles/rules-engineer.md`](roles/rules-engineer.md)
- [`roles/test-creator.md`](roles/test-creator.md)
- [`roles/validators.md`](roles/validators.md)

These are methodological roles, not runtime agents already implemented in Python.

## Notes

- Commands like `/encode-policy`, `/review-pr`, or `/fix-pr` are **not implemented** in this repository.
- If you add a new runtime pipeline, document it here only after it is actually wired into the CLI.

**See also**:
- [roles/](roles/)
- [country-config.md](country-config.md)
