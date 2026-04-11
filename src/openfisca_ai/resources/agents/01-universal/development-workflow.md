# Development Workflow

Practical workflow for using this repository with an OpenFisca country package.

## 1. Prepare the environment

In this repository:

```bash
uv sync --dev
uv run python config/test_config.py
```

In the target OpenFisca country package:

```bash
cd /path/to/openfisca-country
uv sync --extra dev
```

## 2. Implement in the target package

Use this repository for:

- conventions and checklists
- country configuration
- validation tools

Do the actual OpenFisca code and parameter edits in the target country package.

## 3. Run validation tools

From the target country package:

```bash
uv run python /path/to/openfisca-ai/tools/audit_country_package.py .
uv run python /path/to/openfisca-ai/tools/extract_patterns.py .
uv run python /path/to/openfisca-ai/tools/check_package_baseline.py .
uv run python /path/to/openfisca-ai/tools/validate_code.py .
uv run python /path/to/openfisca-ai/tools/validate_tests.py .
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/suggest_units.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
```

If the suggestions are obviously safe:

```bash
uv run python /path/to/openfisca-ai/tools/suggest_units.py . --apply
```

## 4. Run repository checks

Typical OpenFisca repository loop:

```bash
make format-style
make check-style
make test
```

If the repository does not expose Make targets, run the equivalent `uv run ...` commands directly.

## 5. Review before commit

- re-read the legal source
- verify parameter metadata
- check edge-case tests
- document any assumption or limitation

Then use the checklist in [quality-checklist.md](quality-checklist.md).

## Notes

- Prefer `uv run` over bare `python`.
- Prefer repository-native tooling over inventing a new local workflow.
- This repository does not yet provide a full autonomous implementation pipeline.
