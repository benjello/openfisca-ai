# Resume Memo

Updated: 2026-03-15
Branch: `main`

## Context

This note was reconstructed from the current repository state so future
sessions can resume from a concrete checkpoint.

## Current State

- Large local WIP is present and not committed yet.
- `git status` at reconstruction time showed:
  - `39` modified files
  - `25` untracked files
  - `7` deleted files
- Test suite passes:
  - `uv run pytest -q`
  - Result: `66 passed`

## Main Work In Progress

The active work appears to be a broad tooling and runtime update around:

- CLI support for:
  - `run`
  - `scaffold`
  - `scaffold-apply`
  - validation and audit subcommands
- pipeline support for:
  - `implementation_brief`
  - artifact planning
  - artifact write/apply flows
- documentation refresh for the new runtime and validation workflow
- expanded test coverage for CLI, pipeline, config loading, and tooling

## Key Files

- `src/openfisca_ai/cli.py`
- `src/openfisca_ai/pipelines/law_to_code.py`
- `src/openfisca_ai/config_loader.py`
- `src/openfisca_ai/skills/generate_code.py`
- `src/openfisca_ai/core/__init__.py`
- `README.md`
- `tests/test_pipeline.py`
- `tests/test_cli.py`
- `tools/check_package_baseline.py`
- `tools/extract_patterns.py`
- `tools/validate_code.py`
- `tools/validate_tests.py`

## Reconstructed Checkpoint

- The implementation is currently coherent and passing.
- The repo does not contain an explicit earlier conversation checkpoint.
- The most likely stopping point was after implementing the new
  scaffold/artifact workflow and its tests, before staging and splitting the
  work into commits.

## Next Recommended Step

1. Review the unstaged diff and separate it into logical commits.
2. Decide whether deleted docs/files should remain deleted.
3. Commit the runtime/tooling changes separately from broad documentation edits.

## Important Reminder

If we want exact conversation-level resumption next time, update this file at
the end of each working session with:

- what was just finished
- what remains blocked or undecided
- the single next command or edit to do
