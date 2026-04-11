# OpenFisca Country Package Baseline

Practical baseline for a modern OpenFisca country package.

This page documents the parts that are common across most country packages:

- package structure
- development tooling
- test layout
- CI expectations
- OpenFisca-specific files such as `entities.py`, `units.yaml`, and `reforms/`

It is based on two local references:

- `../country-template` for the canonical OpenFisca package shape
- `../openfisca-tunisia` for current `uv`, `Makefile`, and CI practices

Use this page as the default target when creating a new country package or when
cleaning up an older one.

## What Is Baseline vs Country-Specific

Baseline means "shared by many OpenFisca country packages":

- Python package with a country module
- `entities.py`
- `variables/`
- `parameters/`
- `tests/`
- `units.yaml`
- `pyproject.toml`
- a small `Makefile`
- YAML tests runnable with `openfisca test`

Country-specific means:

- entity names and roles
- parameter hierarchy
- legal terminology
- language of labels and descriptions
- special scripts tied to local constraints

## Recommended Repository Layout

```text
openfisca-<country>/
├── pyproject.toml
├── Makefile
├── README.md
├── CHANGELOG.md
├── uv.lock
├── .github/
│   └── workflows/
├── tests/
├── openfisca_<country>/
│   ├── __init__.py
│   ├── entities.py
│   ├── units.yaml
│   ├── parameters/
│   │   └── index.yaml
│   ├── variables/
│   ├── reforms/
│   └── situation_examples/
```

Minimum required pieces for a useful package:

- `openfisca_<country>/entities.py`
- `openfisca_<country>/parameters/`
- `openfisca_<country>/variables/`
- `openfisca_<country>/units.yaml`
- `tests/`

Common but optional:

- `reforms/`
- `situation_examples/`
- `scripts/`
- `notebooks/`

## Python and Packaging

Prefer `pyproject.toml` and `uv`.

Typical package settings:

- one installable package: `openfisca_<country>`
- `openfisca-core[web-api]` as the main dependency
- a `dev` extra with `ruff`, `pytest`, `yamllint`, `twine`
- `tool.pytest.ini_options`
- `tool.ruff`

Avoid using a custom Git branch of `openfisca-core` as the default baseline.
That can be valid for experiments, but it should not define the universal
package standard.

## Core OpenFisca Files

### `entities.py`

Every country package needs an `entities.py` file defining the simulation
entities with `build_entity`.

Typical shared patterns:

- one person entity with `is_person=True`
- one or more group entities with roles
- an exported `entities = [...]` list

What is common:

- use `build_entity`
- define only the entities actually used by the legislation
- keep labels and roles explicit

What is not baseline:

- advanced explicit entity links
- experimental entity graph features

Those can exist in specific packages, but should not be assumed by default.

### `units.yaml`

`units.yaml` should live at package root:

```text
openfisca_<country>/units.yaml
```

Shared expectations:

- every unit used by parameters is declared there
- `/1`, `currency`, `month`, and `year` are common
- country-specific units such as `smig` are acceptable

### `parameters/`

Shared structure:

- parameter files are YAML
- folders are organized by legal domain
- `index.yaml` is used to expose folder structure
- simple parameters use `unit`
- scale parameters use `metadata.threshold_unit`, `metadata.rate_unit`,
  `metadata.amount_unit`

### `variables/`

Shared structure:

- variables are grouped by domain when the package grows
- formulas stay vectorized
- legal values come from parameters, not hardcoded Python constants

### `reforms/`

`reforms/` is common enough to be part of the baseline even if some smaller
packages may not need it immediately.

Use it for:

- policy variants
- temporary reforms
- scenario comparisons

Do not treat reforms as a special case invented later. Many OpenFisca packages
need them early.

### `situation_examples/`

These are useful for:

- demos
- smoke tests
- documentation
- agent prompts that need realistic sample inputs

They are not strictly required, but they are a strong default.

## Test Baseline

A modern package should usually have both:

- YAML tests run through `openfisca test`
- a few Python tests for package-level behavior when needed

YAML tests remain the baseline for legislative validation.

Recommended `tests/` content:

- formula tests by domain
- edge cases and threshold cases
- reform tests
- a minimal smoke test for package import or basic simulation setup

Recommended command:

```bash
uv run openfisca test --country-package openfisca_<country> tests
```

## Development Commands

Prefer a small `Makefile` over a large one.

Recommended common targets:

- `install`
- `build`
- `format-style`
- `check-style`
- `check-syntax-errors`
- `test`
- `check-all-yaml`

Typical commands behind them:

```bash
uv sync --extra dev
uv build
uv run ruff format .
uv run ruff check .
uv run yamllint openfisca_<country>/parameters tests
uv run openfisca test --country-package openfisca_<country> tests
```

The exact target names can vary, but using the same names across country
packages lowers friction for contributors and agents.

Recommended shared repository-level check from this toolkit:

```bash
uv run openfisca-ai check-all .
```

## CI Baseline

Reasonable default CI checks:

- install dependencies with `uv`
- lint Python
- lint YAML tests and parameters
- run YAML tests
- build the package
- optionally test the Web API

Useful advanced checks when the package is mature:

- Python version matrix
- minimal and maximal dependency matrix
- split YAML tests across jobs
- changelog/version guard
- release workflow
- Control Center parameter validation

These advanced jobs are worth documenting as "mature package" practices, not as
mandatory starting requirements.

## What To Reuse From Local References

From `../country-template`, reuse:

- overall package shape
- presence of `reforms/`
- presence of `situation_examples/`
- YAML test culture
- canonical OpenFisca file layout

From `../openfisca-tunisia`, reuse:

- `uv`-first workflow
- concise `Makefile`
- `ruff` setup
- GitHub Actions layout
- external YAML validation workflow
- realistic `units.yaml` conventions

Do not copy either repository blindly.

The goal is:

- `country-template` for package anatomy
- `openfisca-tunisia` for modern operations

## Baseline Review Checklist

Before calling a package "ready for agent work", check:

- `pyproject.toml` exists and is the source of truth
- `uv.lock` is committed
- `openfisca_<country>/entities.py` exists
- `openfisca_<country>/units.yaml` exists
- `openfisca_<country>/parameters/index.yaml` exists
- `openfisca_<country>/variables/` exists
- `tests/` exists and contains runnable YAML tests
- `Makefile` exposes standard commands
- CI runs at least lint + tests

## See Also

- [openfisca-basics.md](openfisca-basics.md)
- [principles.md](principles.md)
- [quality-checklist.md](quality-checklist.md)
